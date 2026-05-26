from __future__ import annotations

import json
import unittest

from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path

from core.benchmarks.runner import run_benchmark_case, run_benchmark_suite


class BenchmarkValidationTests(unittest.TestCase):
    def test_benchmark_suite_rejects_non_object_cases(self) -> None:
        suite_path = artifact_path("benchmarks", "invalid_suite", "suite.json")
        suite_path.parent.mkdir(parents=True, exist_ok=True)
        suite_path.write_text(
            json.dumps({"version": "0.1", "suite_id": "invalid", "cases": ["not-a-case"]}),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "cases\\[0\\] must be an object"):
            run_benchmark_suite(
                suite_path,
                output_root=artifact_path("benchmarks", "invalid_suite", "out"),
            )

    def test_benchmark_suite_rejects_empty_case_list(self) -> None:
        suite_path = artifact_path("benchmarks", "empty_suite", "suite.json")
        suite_path.parent.mkdir(parents=True, exist_ok=True)
        suite_path.write_text(
            json.dumps({"version": "0.1", "suite_id": "empty", "cases": []}),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "cases must not be empty"):
            run_benchmark_suite(
                suite_path,
                output_root=artifact_path("benchmarks", "empty_suite", "out"),
            )

    def test_benchmark_case_requires_expected_assertions(self) -> None:
        with self.assertRaisesRegex(ValueError, "expected must be a non-empty object"):
            run_benchmark_case(
                {
                    "case_id": "missing-expected",
                    "pipeline": "object_spec",
                    "object_type": "desk",
                },
                root=PROJECT_ROOT,
                output_root=artifact_path("benchmarks", "missing_expected"),
            )

    def test_benchmark_case_rejects_failure_expected_without_structured_reason(self) -> None:
        with self.assertRaisesRegex(ValueError, "failure_category or contains_blocked_reason"):
            run_benchmark_case(
                {
                    "case_id": "bad-failure-contract",
                    "pipeline": "composition_spec",
                    "composition_id": "door_clearance_conflict",
                    "expected": {
                        "pipeline_status": "blocked",
                        "evidence_state": "blocked_expected_non_cad",
                        "geometry_accuracy": "not_verified_without_cad_readback",
                        "screenshot_role": "visual_aid_only",
                    },
                },
                root=PROJECT_ROOT,
                output_root=artifact_path("benchmarks", "bad_failure_contract"),
            )

    def test_benchmark_case_rejects_unknown_expected_evidence_state(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown evidence_state"):
            run_benchmark_case(
                {
                    "case_id": "bad-evidence",
                    "pipeline": "object_spec",
                    "object_type": "desk",
                    "expected": {
                        "evidence_state": "not_a_real_evidence_state",
                        "pipeline_status": "ok",
                    },
                },
                root=PROJECT_ROOT,
                output_root=artifact_path("benchmarks", "bad_evidence"),
            )

    def test_benchmark_case_requires_expected_evidence_triplet(self) -> None:
        with self.assertRaisesRegex(ValueError, "expected.evidence_state is required"):
            run_benchmark_case(
                {
                    "case_id": "missing-evidence-triplet",
                    "workflow": "examples/workflows/full_non_cad_core_loop.json",
                    "expected": {
                        "pipeline_status": "ok",
                        "dry_run_status": "valid",
                        "verification_status": "unverified",
                    },
                },
                root=PROJECT_ROOT,
                output_root=artifact_path("benchmarks", "missing_evidence_triplet"),
            )


if __name__ == "__main__":
    unittest.main()
