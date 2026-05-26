from __future__ import annotations

import json
import unittest

from tests.bootstrap import PROJECT_ROOT

from core.verification.evidence_contract import (
    EVIDENCE_BENCHMARK_PASS_NON_CAD,
    EVIDENCE_BLOCKED_EXPECTED_NON_CAD,
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
    EVIDENCE_INVALID_CONFIGURATION,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    EVIDENCE_STATE_VALUES,
    classify_benchmark_pipeline_evidence,
    is_geometry_verified_evidence_state,
    validate_evidence_state,
    validate_failure_expected_contract,
    validate_evidence_summary,
)


class EvidenceClassifierTests(unittest.TestCase):
    def test_benchmark_pipeline_classifier_covers_known_paths(self) -> None:
        self.assertEqual(
            classify_benchmark_pipeline_evidence(
                pipeline_status="ok",
                dry_run_status="valid",
                verification_status="unverified",
            )["evidence_state"],
            EVIDENCE_BENCHMARK_PASS_NON_CAD,
        )
        self.assertEqual(
            classify_benchmark_pipeline_evidence(
                pipeline_status="blocked",
                dry_run_status="unknown",
                verification_status="unknown",
            )["evidence_state"],
            EVIDENCE_BLOCKED_EXPECTED_NON_CAD,
        )
        self.assertEqual(
            classify_benchmark_pipeline_evidence(
                pipeline_status="invalid",
                dry_run_status="unknown",
                verification_status="unknown",
            )["evidence_state"],
            EVIDENCE_INVALID_CONFIGURATION,
        )
        self.assertEqual(
            classify_benchmark_pipeline_evidence(
                pipeline_status="ok",
                dry_run_status="valid",
                verification_status="geometry_verified",
            )["evidence_state"],
            EVIDENCE_READBACK_GEOMETRY_VERIFIED,
        )
        self.assertEqual(
            classify_benchmark_pipeline_evidence(
                pipeline_status="ok",
                dry_run_status="valid",
                verification_status="failed",
            )["evidence_state"],
            EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
        )
        self.assertEqual(
            classify_benchmark_pipeline_evidence(
                pipeline_status="fail",
                dry_run_status="invalid",
                verification_status="failed",
            )["evidence_state"],
            EVIDENCE_DEFERRED_CAD_READBACK,
        )

    def test_unknown_evidence_state_is_rejected(self) -> None:
        self.assertIn("unknown evidence_state", validate_evidence_state("made_up_state"))

    def test_geometry_verified_states_are_classified(self) -> None:
        self.assertTrue(is_geometry_verified_evidence_state(EVIDENCE_READBACK_GEOMETRY_VERIFIED))
        self.assertFalse(is_geometry_verified_evidence_state(EVIDENCE_BENCHMARK_PASS_NON_CAD))

    def test_failure_expected_contract_requires_structured_reason(self) -> None:
        errors = validate_failure_expected_contract(
            {
                "pipeline_status": "blocked",
                "evidence_state": EVIDENCE_BLOCKED_EXPECTED_NON_CAD,
            },
            label="case",
        )
        self.assertTrue(errors)

    def test_failure_expected_contract_accepts_invalid_configuration(self) -> None:
        errors = validate_failure_expected_contract(
            {
                "pipeline_status": "invalid",
                "evidence_state": EVIDENCE_INVALID_CONFIGURATION,
                "contains_blocked_reason": "shell_model",
            },
            label="case",
        )
        self.assertEqual(errors, [])

    def test_validate_evidence_summary_rejects_inconsistent_non_cad_only(self) -> None:
        error = validate_evidence_summary(
            {
                "case_count": 1,
                "evidence_state_counts": {"readback_geometry_verified": 1},
                "geometry_accuracy_counts": {},
                "benchmark_pass_non_cad_count": 0,
                "blocked_expected_non_cad_count": 0,
                "invalid_configuration_count": 0,
                "readback_geometry_verified_count": 1,
                "cad_capability_verified_count": 0,
                "deferred_cad_readback_count": 0,
                "dry_run_valid_plan_only_count": 0,
                "non_cad_only": True,
            }
        )
        self.assertIn("non_cad_only=true", error)

    def test_benchmark_json_expected_evidence_triplets_are_complete(self) -> None:
        suite_paths = sorted((PROJECT_ROOT / "examples/benchmarks").glob("*.json"))
        for suite_path in suite_paths:
            suite = json.loads(suite_path.read_text(encoding="utf-8"))
            self.assertIsInstance(
                suite.get("expected_evidence_summary"),
                dict,
                f"{suite_path.name} missing expected_evidence_summary",
            )
            for case in suite.get("cases", []):
                expected = case.get("expected", {})
                self.assertIsInstance(expected, dict, f"{suite_path.name}:{case.get('case_id')} expected must be object")
                for field in ("evidence_state", "geometry_accuracy", "screenshot_role"):
                    self.assertIn(field, expected, f"{suite_path.name}:{case.get('case_id')} missing {field}")
                evidence_state = expected["evidence_state"]
                self.assertIn(
                    evidence_state,
                    EVIDENCE_STATE_VALUES,
                    f"{suite_path.name}:{case.get('case_id')} has unknown evidence_state",
                )


if __name__ == "__main__":
    unittest.main()
