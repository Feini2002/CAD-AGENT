from __future__ import annotations

import unittest

from core.benchmarks.runner import run_benchmark_suite
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class CommercialFitoutMicroSceneBenchmarkTests(unittest.TestCase):
    def test_micro_scene_benchmark_passes_without_silent_failures(self) -> None:
        result = run_benchmark_suite(
            PROJECT_ROOT / "examples" / "benchmarks" / "commercial_fitout_micro_scene_benchmark.json",
            output_root=artifact_path("benchmarks", "commercial_fitout_micro_scene"),
        )

        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["summary"], {"total": 8, "passed": 8, "failed": 0})
        blocked = [case for case in result["cases"] if case["actual"]["pipeline_status"] == "blocked"]
        passed = [case for case in result["cases"] if case["actual"]["pipeline_status"] == "ok"]
        self.assertEqual(len(blocked), 4)
        self.assertEqual(len(passed), 4)
        for case in blocked:
            self.assertEqual(case["actual"]["evidence_state"], "blocked_expected_non_cad")
            self.assertEqual(case["actual"]["cad_plan_count"], 0)
            self.assertIn(case["actual"]["failure_category"], case["expected"]["failure_category"])
        for case in passed:
            self.assertEqual(case["actual"]["evidence_state"], "benchmark_pass_non_cad")
            self.assertGreaterEqual(case["actual"]["cad_plan_count"], 1)


if __name__ == "__main__":
    unittest.main()
