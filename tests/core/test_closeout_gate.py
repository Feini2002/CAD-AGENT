from __future__ import annotations

import json
from pathlib import Path
import unittest

from tests.helpers import temporary_artifact_dir


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _prepare_run_package(root: Path, *, delete: bool = False, asset: bool = False) -> Path:
    from core.orchestrator.run_package_state import create_run_package

    state = create_run_package(
        "closeout demo",
        user_request={"text": "visible CAD closeout"},
        root_dir=root,
    )
    run_dir = Path(state["runDir"])
    _write_json(
        run_dir / "dispatch_plan.json",
        {
            "schemaVersion": "run-package-dispatch-plan/v1",
            "runId": state["runId"],
            "status": "ready",
            "taskType": "focused_cad_visible_delivery",
            "requiresVisualCloseout": True,
            "hasDeleteOperation": delete,
            "hasAssetOperation": asset,
        },
    )
    return run_dir


def _write_passing_core_evidence(run_dir: Path) -> None:
    _write_json(run_dir / "cad_reports" / "validation_report.json", {"status": "pass"})
    _write_json(run_dir / "cad_reports" / "dry_run_report.json", {"status": "pass"})
    _write_json(
        run_dir / "cad_reports" / "readback_summary.json",
        {
            "status": "ok",
            "created_handles_readback": "ok",
            "targetLayer": "CODEX_PREVIEW",
            "savedCurrentDwg": False,
        },
    )
    _write_json(
        run_dir / "agent_outputs" / "visual_acceptance_output.json",
        {
            "status": "pass",
            "visualAcceptanceDecision": "pass",
            "blockingReasons": [],
            "visualProblems": [],
            "evidenceBoundary": {"checked": ["non screenshot evidence checked"]},
        },
    )
    _write_json(run_dir / "cad_reports" / "neighbor_protection.json", {"status": "pass"})


class CloseoutGateTests(unittest.TestCase):
    def test_passing_visible_closeout_writes_decision_and_marks_ready(self) -> None:
        from core.orchestrator.closeout_gate import run_closeout_gate
        from core.orchestrator.run_package_state import load_run_state

        with temporary_artifact_dir("closeout_gate_pass") as root:
            run_dir = _prepare_run_package(root)
            _write_passing_core_evidence(run_dir)

            decision = run_closeout_gate(run_dir)

            self.assertTrue(decision["can_deliver"])
            self.assertEqual(decision["status"], "ready_for_delivery")
            self.assertEqual(decision["closeoutState"], "ready_for_user_review")
            self.assertEqual(decision["stateMachineVersion"], "closeout-state-machine/v1")
            self.assertEqual(decision["missingEvidence"], [])
            self.assertTrue((run_dir / "closeout_decision.json").is_file())
            self.assertIn("visual_acceptance_review=pass", decision["evidence_boundary"]["checked"])
            self.assertNotIn("user accepted", "; ".join(decision["final_response_allowed_claims"]).casefold())

            state = load_run_state(run_dir)
            self.assertEqual(state["status"], "ready_for_delivery")
            self.assertEqual(state["stages"]["ready_for_delivery"]["outputFiles"], ["closeout_decision.json"])

    def test_missing_visual_acceptance_blocks_delivery(self) -> None:
        from core.orchestrator.closeout_gate import run_closeout_gate
        from core.orchestrator.run_package_state import load_run_state

        with temporary_artifact_dir("closeout_gate_missing_visual") as root:
            run_dir = _prepare_run_package(root)
            _write_passing_core_evidence(run_dir)
            (run_dir / "agent_outputs" / "visual_acceptance_output.json").unlink()

            decision = run_closeout_gate(run_dir)

            self.assertFalse(decision["can_deliver"])
            self.assertEqual(decision["status"], "not_verified")
            self.assertEqual(decision["closeoutState"], "visual_evidence_missing")
            self.assertIn("visual_acceptance_review missing", decision["blocking_reasons"])
            self.assertNotIn("visual_acceptance_review missing or not pass", decision["blocking_reasons"])
            self.assertEqual(load_run_state(run_dir)["status"], "blocked")

    def test_screenshot_does_not_replace_created_handle_readback(self) -> None:
        from core.orchestrator.closeout_gate import run_closeout_gate

        with temporary_artifact_dir("closeout_gate_screenshot_boundary") as root:
            run_dir = _prepare_run_package(root)
            _write_passing_core_evidence(run_dir)
            (run_dir / "cad_reports" / "readback_summary.json").unlink()
            (run_dir / "screenshots" / "preview.png").write_bytes(b"fake png bytes")

            decision = run_closeout_gate(run_dir)

            self.assertFalse(decision["can_deliver"])
            self.assertIn("created_handles_readback missing", decision["blocking_reasons"])
            self.assertEqual(decision["evidence_boundary"]["screenshots"]["role"], "visual_aid_only")
            self.assertEqual(decision["evidence_boundary"]["screenshots"]["count"], 1)

    def test_state_machine_missing_labels_do_not_look_like_passing_blocking_reasons(self) -> None:
        from core.orchestrator.closeout_gate import run_closeout_gate

        with temporary_artifact_dir("closeout_gate_missing_label_boundary") as root:
            run_dir = _prepare_run_package(root)
            _write_passing_core_evidence(run_dir)
            _write_json(
                run_dir / "cad_reports" / "readback_summary.json",
                {
                    "status": "not_verified",
                    "readbackStatus": "not_verified",
                    "targetLayer": "CODEX_PREVIEW",
                    "savedCurrentDwg": False,
                    "driverMode": "fake_driver_preflight",
                    "cadGeometryVerified": False,
                },
            )

            decision = run_closeout_gate(run_dir)

            self.assertFalse(decision["can_deliver"])
            self.assertIn("created_handles_readback not ok", decision["blocking_reasons"])
            self.assertIn("real CAD geometry not verified", decision["blocking_reasons"])
            self.assertIn("created_handles_readback=ok", decision["missingEvidence"])
            self.assertIn("real CAD geometry verified", decision["missingEvidence"])
            self.assertNotIn("created_handles_readback=ok", decision["blocking_reasons"])
            self.assertNotIn("real CAD geometry verified", decision["blocking_reasons"])

    def test_delete_and_asset_requests_require_their_hard_gate_reports(self) -> None:
        from core.orchestrator.closeout_gate import run_closeout_gate

        with temporary_artifact_dir("closeout_gate_required_gates") as root:
            run_dir = _prepare_run_package(root, delete=True, asset=True)
            _write_passing_core_evidence(run_dir)

            decision = run_closeout_gate(run_dir)

            self.assertFalse(decision["can_deliver"])
            self.assertIn("delete_scope_gate missing", decision["blocking_reasons"])
            self.assertIn("asset_source_boundary missing", decision["blocking_reasons"])

            _write_json(run_dir / "cad_reports" / "delete_scope_gate.json", {"status": "pass"})
            _write_json(run_dir / "cad_reports" / "asset_source_boundary.json", {"status": "pass"})
            decision = run_closeout_gate(run_dir)

            self.assertTrue(decision["can_deliver"])
            self.assertIn("delete_scope_gate=pass", decision["evidence_boundary"]["checked"])
            self.assertIn("asset_source_boundary=pass", decision["evidence_boundary"]["checked"])


if __name__ == "__main__":
    unittest.main()
