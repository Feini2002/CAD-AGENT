from __future__ import annotations

import json
import unittest
from copy import deepcopy

from tests.helpers import temporary_artifact_dir


def _phase9_plan(*, layer: str = "CODEX_PREVIEW") -> dict[str, object]:
    return {
        "version": "0.1",
        "domain": "generic",
        "intent": "draw_object",
        "object": {
            "type": "table",
            "name": "Phase 9 single preview table",
            "width": 900,
            "depth": 450,
        },
        "placement": {
            "mode": "absolute",
            "base_point": [72000, 42000, 0],
        },
        "drawing": {
            "layer": layer,
            "include_label": False,
            "include_dimensions": False,
        },
        "confidence": 0.91,
        "needs_confirmation": False,
    }


class Phase9SinglePreviewTests(unittest.TestCase):
    def test_scope_record_locks_single_preview_to_codex_preview_and_no_save(self) -> None:
        from core.contracts.phase9_preview import build_phase9_preview_scope_record

        scope = build_phase9_preview_scope_record(cad_plan=_phase9_plan())

        self.assertEqual(scope["phase"], "Phase 9")
        self.assertEqual(scope["targetLayer"], "CODEX_PREVIEW")
        self.assertEqual(scope["maxPreviewTaskCount"], 1)
        self.assertEqual(scope["savePolicy"]["savedCurrentDwg"], False)
        self.assertIn("formal_layer_write", scope["forbiddenEffects"])
        self.assertIn("registry_mutation", scope["forbiddenEffects"])
        self.assertIn("table_c_mutation", scope["forbiddenEffects"])
        self.assertEqual(scope["cadPlanIntent"], "draw_object")

    def test_preflight_blocks_formal_layer_before_preview_write(self) -> None:
        from core.contracts.phase9_preview import run_phase9_single_preview

        with temporary_artifact_dir("phase9_formal_layer_blocked") as root:
            result = run_phase9_single_preview(
                cad_plan=_phase9_plan(layer="A-WALL"),
                output_dir=root,
                driver_factory=lambda: self.fail("driver must not be constructed when preflight blocks"),
            )

        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.verification_status, "not_verified")
        self.assertFalse(result.cad_geometry_verified)
        self.assertTrue(any("CODEX_PREVIEW" in reason for reason in result.blocking_reasons))
        self.assertFalse(result.evidence.satisfies("real_cad_readback"))
        self.assertTrue(result.evidence.satisfies("no_save_guard"))
        self.assertEqual(result.report["autoCADReadinessProbe"]["status"], "not_run")
        self.assertFalse(result.report["autoCADReadinessProbe"]["previewAttempted"])

    def test_autocad_readiness_probe_records_external_blocker_without_preview_write(self) -> None:
        from core.contracts.phase9_preview import run_phase9_single_preview

        def unavailable_driver() -> object:
            raise RuntimeError("No active AutoCAD.Application instance is available")

        with temporary_artifact_dir("phase9_autocad_probe_blocked") as root:
            result = run_phase9_single_preview(
                cad_plan=_phase9_plan(),
                output_dir=root,
                driver_factory=unavailable_driver,
                driver_backend="autocad_com_existing",
            )
            probe = json.loads((root / "phase9_autocad_readiness_probe.json").read_text(encoding="utf-8"))

        self.assertEqual(result.status, "external_blocker")
        self.assertFalse(result.cad_geometry_verified)
        self.assertEqual(result.created_handle_count, 0)
        self.assertEqual(result.readback_entity_count, 0)
        self.assertEqual(probe["status"], "external_blocker")
        self.assertFalse(probe["applicationAvailable"])
        self.assertFalse(probe["activeDocumentAvailable"])
        self.assertFalse(probe["activeDocumentAccessible"])
        self.assertFalse(probe["previewAttempted"])
        self.assertIn("No active AutoCAD.Application", probe["blocker"])

    def test_fake_driver_preview_remains_not_verified_even_with_created_handles(self) -> None:
        from core.contracts.phase9_preview import run_phase9_single_preview
        from core.verification.fake_cad_driver import FakeCadDriver

        with temporary_artifact_dir("phase9_fake_driver_not_verified") as root:
            result = run_phase9_single_preview(
                cad_plan=_phase9_plan(),
                output_dir=root,
                driver_factory=FakeCadDriver,
                driver_backend="fake_driver_preflight",
            )

        self.assertEqual(result.status, "not_verified")
        self.assertEqual(result.created_handle_count, 4)
        self.assertEqual(result.readback_entity_count, 4)
        self.assertFalse(result.cad_geometry_verified)
        self.assertFalse(result.evidence.satisfies("real_cad_readback"))
        self.assertTrue(result.evidence.satisfies("no_save_guard"))
        self.assertIn("real_cad_readback", result.missing_evidence)

    def test_created_handles_readback_and_no_save_can_verify_real_backend(self) -> None:
        from core.contracts.phase9_preview import run_phase9_single_preview
        from core.verification.fake_cad_driver import FakeCadDriver

        with temporary_artifact_dir("phase9_real_backend_contract") as root:
            result = run_phase9_single_preview(
                cad_plan=_phase9_plan(),
                output_dir=root,
                driver_factory=FakeCadDriver,
                driver_backend="autocad_com_existing",
            )

            report = json.loads((root / "phase9_preview_report.json").read_text(encoding="utf-8"))

        self.assertEqual(result.status, "geometry_verified")
        self.assertEqual(result.verification_status, "verified")
        self.assertEqual(result.created_handle_count, 4)
        self.assertEqual(result.readback_entity_count, 4)
        self.assertTrue(result.cad_geometry_verified)
        self.assertTrue(result.evidence.satisfies("real_cad_readback"))
        self.assertTrue(result.evidence.satisfies("no_save_guard"))
        self.assertEqual(result.completion.checked_evidence, ["real_cad_readback", "no_save_guard"])
        self.assertFalse(result.execution_summary["savedCurrentDwg"])
        self.assertEqual(report["autoCADReadinessProbe"]["status"], "ready")
        self.assertTrue(report["autoCADReadinessProbe"]["applicationAvailable"])
        self.assertTrue(report["autoCADReadinessProbe"]["activeDocumentAvailable"])
        self.assertTrue(report["autoCADReadinessProbe"]["activeDocumentAccessible"])
        self.assertTrue(report["autoCADReadinessProbe"]["previewAttempted"])
        self.assertEqual(report["autoCADReadinessProbe"]["activeDocument"]["name"], "sample-active.dwg")
        self.assertEqual(report["targetLayer"], "CODEX_PREVIEW")
        self.assertEqual(report["savedCurrentDwg"], False)
        self.assertEqual(report["readbackEntityCount"], 4)
        self.assertEqual(report["evidenceBoundary"]["notChecked"], ["user_visual_acceptance", "phase10_rehearsal"])

    def test_saved_current_dwg_true_blocks_even_if_readback_exists(self) -> None:
        from core.contracts.phase9_preview import build_phase9_evidence_package, build_phase9_preview_task

        task = build_phase9_preview_task(cad_plan=_phase9_plan())
        execution_summary = {
            "status": "executed",
            "layer": "CODEX_PREVIEW",
            "created_handles": ["H1"],
            "savedCurrentDwg": True,
            "safety": {
                "layer": "CODEX_PREVIEW",
                "saved_dwg": True,
                "deleted_entities": False,
                "modified_formal_layers": False,
            },
        }
        evidence = build_phase9_evidence_package(
            task_id=task.task_id,
            driver_backend="autocad_com_existing",
            execution_summary=execution_summary,
            readback_entities=[{"handle": "H1", "type": "line", "layer": "CODEX_PREVIEW"}],
            blocking_reasons=[],
        )

        self.assertFalse(evidence.satisfies("no_save_guard"))
        self.assertFalse(evidence.satisfies("real_cad_readback"))

    def test_preview_registered_dry_run_screenshot_and_model_text_do_not_satisfy_readback(self) -> None:
        from core.contracts.phase9_preview import build_phase9_evidence_package

        evidence = build_phase9_evidence_package(
            task_id="task-phase9-negative",
            driver_backend="autocad_com_existing",
            execution_summary={
                "status": "preview_registered_non_cad",
                "layer": "CODEX_PREVIEW",
                "created_handles": [],
                "savedCurrentDwg": False,
                "screenshot": "visual-aid.png",
                "dryRunStatus": "valid",
            },
            readback_entities=[],
            blocking_reasons=[],
            model_text="Preview registered and screenshot looks right.",
        )

        self.assertTrue(evidence.satisfies("no_save_guard"))
        self.assertFalse(evidence.satisfies("real_cad_readback"))
        self.assertEqual(evidence.real_cad_readback_items(), [])

    def test_missing_created_handle_readback_blocks_real_backend(self) -> None:
        from core.contracts.phase9_preview import run_phase9_single_preview
        from core.verification.fake_cad_driver import FakeCadDriver

        with temporary_artifact_dir("phase9_missing_readback") as root:
            result = run_phase9_single_preview(
                cad_plan=_phase9_plan(),
                output_dir=root,
                driver_factory=lambda: FakeCadDriver(missing_readback_handle="H101"),
                driver_backend="autocad_com_existing",
            )

        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.created_handle_count, 4)
        self.assertEqual(result.readback_entity_count, 3)
        self.assertFalse(result.cad_geometry_verified)
        self.assertFalse(result.evidence.satisfies("real_cad_readback"))
        self.assertTrue(any("created handles readback" in reason for reason in result.blocking_reasons))


if __name__ == "__main__":
    unittest.main()
