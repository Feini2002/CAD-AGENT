from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.verification.evidence_vocabulary import EVIDENCE_NEGATIVE_GUARD_VERIFIED
from core.verification.negative_plan_registry import (
    NEGATIVE_REAL_CAD_CAPABILITY_ID,
    RCAD_20_CANONICAL_REPORT,
    VPROOF_51_BOUNDARY_DOC,
    assert_vproof_51_negative_cad_contract,
    apply_negative_real_cad_guard_writeback,
    build_negative_real_cad_registry_row,
    merge_negative_plan_registry_rows,
    run_vproof_51_negative_cad_sync,
    validate_negative_real_cad_report,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


def _sample_real_cad_report() -> dict:
    return {
        "version": "0.1",
        "suite_id": "negative_cad_runner",
        "status": "pass",
        "mode": "real_cad",
        "evidence_state": EVIDENCE_NEGATIVE_GUARD_VERIFIED,
        "created_handles": [],
        "safety": {
            "layer": "CODEX_PREVIEW",
            "saved_dwg": False,
            "deleted_entities": False,
            "modified_formal_layers": False,
        },
        "session_guard": {
            "comparison": {
                "preview_layer_entity_delta": 0,
                "modelspace_entity_delta": 0,
            }
        },
    }


class Vproof51NegativeCadTests(unittest.TestCase):
    def test_validate_real_cad_report_contract(self) -> None:
        self.assertEqual(validate_negative_real_cad_report(_sample_real_cad_report()), [])
        bad = _sample_real_cad_report()
        bad["created_handles"] = ["ABC"]
        self.assertTrue(validate_negative_real_cad_report(bad))

    def test_boundary_doc_exists(self) -> None:
        text = (PROJECT_ROOT / VPROOF_51_BOUNDARY_DOC).read_text(encoding="utf-8")
        for phrase in (
            "V-PROOF-51",
            "negative.cad_plan.real_cad_guard",
            "negative_guard_verified",
            "created_handles=[]",
            "不得声称",
            "geometry_verified",
            "RCAD-20",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_sync_with_fixture_report(self) -> None:
        output_dir = artifact_path("vproof_51", "sync_fixture")
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / "negative_cad_runner_report.json"
        report_path.write_text(json.dumps(_sample_real_cad_report(), indent=2), encoding="utf-8")

        summary = run_vproof_51_negative_cad_sync(
            project_root=PROJECT_ROOT,
            output_dir=output_dir,
            report_path=report_path,
            dry_run=True,
        )
        self.assertEqual(summary["writeback_status"], "applied")
        self.assertEqual(summary["report_mode"], "real_cad")

    def test_apply_rejects_fake_mode_report(self) -> None:
        registry = {
            "version": "0.1",
            "registry_id": "test",
            "capabilities": [build_negative_real_cad_registry_row()],
        }
        merge_negative_plan_registry_rows(registry, [])
        fake = _sample_real_cad_report()
        fake["mode"] = "fake_cad"
        result = apply_negative_real_cad_guard_writeback(
            registry,
            report_rel="output/test.json",
            report=fake,
            project_root=PROJECT_ROOT,
            dry_run=True,
        )
        self.assertEqual(result.status, "rejected")

    def test_live_registry_contract_when_row_present(self) -> None:
        registry = json.loads(
            (PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json").read_text(encoding="utf-8")
        )
        if not any(
            item.get("capability_id") == NEGATIVE_REAL_CAD_CAPABILITY_ID
            for item in registry.get("capabilities", [])
        ):
            self.skipTest("real_cad_guard row not merged yet")
        if not (PROJECT_ROOT / RCAD_20_CANONICAL_REPORT).is_file():
            self.skipTest("RCAD-20 real CAD report is not present in this workspace")
        assert_vproof_51_negative_cad_contract(project_root=PROJECT_ROOT)


if __name__ == "__main__":
    unittest.main()
