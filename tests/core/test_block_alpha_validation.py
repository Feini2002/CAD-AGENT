from __future__ import annotations

import json
import unittest

from tests.bootstrap import PROJECT_ROOT

from core.verification.block_alpha_validation import (
    build_block_alpha_no_cad_report,
    build_block_alpha_readback_report,
    validate_block_alpha_report_evidence,
)
from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    NON_CAD_GEOMETRY_ACCURACY,
)


class BlockAlphaValidationTests(unittest.TestCase):
    def test_no_cad_report_is_deferred_and_not_geometry_verified(self) -> None:
        plan_path = PROJECT_ROOT / "examples/plans/insert_block_alpha_test.json"
        report = build_block_alpha_no_cad_report(plan_path=plan_path)
        self.assertEqual(report["status"], "deferred")
        self.assertEqual(report["evidence_state"], EVIDENCE_DEFERRED_CAD_READBACK)
        self.assertEqual(report["geometry_accuracy"], NON_CAD_GEOMETRY_ACCURACY)
        self.assertEqual(validate_block_alpha_report_evidence(report, no_cad=True), "")

    def test_no_cad_gate_rejects_geometry_verified_claim(self) -> None:
        plan_path = PROJECT_ROOT / "examples/plans/insert_block_alpha_test.json"
        report = build_block_alpha_no_cad_report(plan_path=plan_path)
        report["status"] = "geometry_verified"
        self.assertIn("must not claim geometry_verified", validate_block_alpha_report_evidence(report, no_cad=True))

    def test_no_cad_gate_requires_deferred_status(self) -> None:
        plan_path = PROJECT_ROOT / "examples/plans/insert_block_alpha_test.json"
        report = build_block_alpha_no_cad_report(plan_path=plan_path)
        report["status"] = "failed"
        self.assertIn("requires status='deferred'", validate_block_alpha_report_evidence(report, no_cad=True))

    def test_readback_report_passes_for_matching_block_reference(self) -> None:
        plan_path = PROJECT_ROOT / "examples/plans/insert_block_alpha_test.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        from core.verification.geometry_checks import expected_block_reference_from_plan

        expected = expected_block_reference_from_plan(plan)
        entity = {"handle": "BR1", "type": "block_reference", **expected}
        report = build_block_alpha_readback_report(
            plan_path=plan_path,
            entities=[entity],
            created_handles=["BR1"],
        )
        self.assertEqual(report["status"], "geometry_verified")
        self.assertEqual(report["evidence_state"], EVIDENCE_READBACK_GEOMETRY_VERIFIED)
        self.assertEqual(report["geometry_accuracy"], GEOMETRY_VERIFIED_BY_READBACK)
        self.assertEqual(validate_block_alpha_report_evidence(report, no_cad=False), "")

    def test_readback_report_requires_created_handles_scope(self) -> None:
        plan_path = PROJECT_ROOT / "examples/plans/insert_block_alpha_test.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        from core.verification.geometry_checks import expected_block_reference_from_plan

        expected = expected_block_reference_from_plan(plan)
        entity = {"handle": "OLD1", "type": "block_reference", **expected}
        report = build_block_alpha_readback_report(
            plan_path=plan_path,
            entities=[entity],
            created_handles=[],
        )
        self.assertEqual(report["status"], "failed")
        self.assertIn("created_handles_scope", [check["name"] for check in report["checks"]])

    def test_cad_gate_rejects_geometry_verified_without_block_reference_identity(self) -> None:
        report = {
            "status": "geometry_verified",
            "evidence_state": EVIDENCE_READBACK_GEOMETRY_VERIFIED,
            "geometry_accuracy": GEOMETRY_VERIFIED_BY_READBACK,
            "checks": [{"name": "block_name", "status": "pass"}],
            "created_handles": [],
            "entity": {"handle": "L1", "type": "line"},
        }
        failure = validate_block_alpha_report_evidence(report, no_cad=False)
        self.assertIn("created_handles", failure)

    def test_cad_gate_rejects_geometry_verified_without_scope_check(self) -> None:
        plan_path = PROJECT_ROOT / "examples/plans/insert_block_alpha_test.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        from core.verification.geometry_checks import expected_block_reference_from_plan

        expected = expected_block_reference_from_plan(plan)
        report = {
            "status": "geometry_verified",
            "evidence_state": EVIDENCE_READBACK_GEOMETRY_VERIFIED,
            "geometry_accuracy": GEOMETRY_VERIFIED_BY_READBACK,
            "checks": [{"name": "block_name", "status": "pass"}],
            "created_handles": ["BR1"],
            "entity": {"handle": "BR1", "type": "block_reference", **expected},
        }
        failure = validate_block_alpha_report_evidence(report, no_cad=False)
        self.assertIn("created_handles_scope", failure)

    def test_cad_gate_rejects_geometry_verified_without_geometry_fields(self) -> None:
        report = {
            "status": "geometry_verified",
            "evidence_state": EVIDENCE_READBACK_GEOMETRY_VERIFIED,
            "geometry_accuracy": GEOMETRY_VERIFIED_BY_READBACK,
            "checks": [
                {"name": "created_handles_scope", "status": "pass"},
                {"name": "block_name", "status": "pass"},
            ],
            "created_handles": ["BR1"],
            "entity": {"handle": "BR1", "type": "block_reference"},
        }
        failure = validate_block_alpha_report_evidence(report, no_cad=False)
        self.assertIn("entity.block_name", failure)


if __name__ == "__main__":
    unittest.main()
