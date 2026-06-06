from __future__ import annotations

import unittest

from core.verification.cad_validation_debt_closure import build_cad_validation_debt_closure_report


class CadValidationDebtClosureTests(unittest.TestCase):
    def test_closure_report_classifies_eight_validation_debts(self) -> None:
        coverage = {
            "status": "pass",
            "summary": {
                "total_count": 333,
                "showcase_count": 303,
                "smoke_count": 25,
                "deferred_count": 5,
                "cad_proof_count": 303,
                "cad_proof_coverage_percent": 90.99,
                "cad_strength_headline_percent": 90.99,
            },
            "evidence_path_audit": {"report_path_missing": 303},
        }
        evidence_audit = {
            "status": "fail",
            "summary": {"audited_count": 303, "passed_count": 0, "failed_count": 303},
        }
        cad_validation = {
            "status": "pass",
            "geometry_gate": {"status": "pass", "failed_required_step_ids": []},
            "infrastructure_gate": {"status": "fail", "failed_required_step_ids": ["unit_tests"]},
            "evidence_summary": {
                "readback_geometry_verified_count": 2,
                "cad_capability_verified_count": 1,
                "screenshot_role_counts": {"visual_aid_only": 2, "not_applicable": 1},
            },
            "block_alpha": {"geometry_verified": True},
        }
        data_bloat = {
            "status": "blocked",
            "blocked": [{"code": "coverage_report_path_missing", "missingCount": 303}],
        }
        drawing_read = {
            "status": "pass",
            "evidence_summary": {"non_cad_only": True, "readback_geometry_verified_count": 0},
        }

        report = build_cad_validation_debt_closure_report(
            coverage_report=coverage,
            evidence_audit_report=evidence_audit,
            cad_validation_report=cad_validation,
            data_bloat_report=data_bloat,
            drawing_read_report=drawing_read,
            repair_gate_status="pass",
            repair_gate_command="python -m unittest tests.core.test_delete_neighbor_gates",
        )

        self.assertEqual(report["status"], "partial")
        self.assertEqual(report["summary"]["debt_count"], 8)
        self.assertEqual(report["summary"]["resolved_or_bounded_count"], 5)
        self.assertEqual(report["summary"]["blocked_count"], 3)
        by_id = {item["id"]: item for item in report["items"]}
        self.assertEqual(by_id["table_c_gap"]["status"], "blocked_batch_debt")
        self.assertEqual(by_id["table_c_gap"]["metrics"]["remaining_to_full_count"], 30)
        self.assertEqual(by_id["evidence_report_path_missing"]["status"], "blocked_batch_debt")
        self.assertEqual(by_id["rcad_scope_boundary"]["status"], "bounded_by_real_cad")
        self.assertEqual(by_id["screenshot_boundary"]["status"], "bounded_by_readback")
        self.assertEqual(by_id["local_repair_scope"]["status"], "guard_verified")


if __name__ == "__main__":
    unittest.main()
