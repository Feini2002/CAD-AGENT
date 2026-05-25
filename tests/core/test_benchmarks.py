from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from core.benchmarks.runner import run_benchmark_suite
from tests.helpers import artifact_path


class BenchmarkRunnerTests(unittest.TestCase):
    def test_non_cad_core_benchmark_runs_pipeline_case(self) -> None:
        result = run_benchmark_suite(
            PROJECT_ROOT / "examples/benchmarks/non_cad_core_benchmark.json",
            output_root=artifact_path("benchmarks", "non_cad_core"),
        )

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["summary"], {"total": 1, "passed": 1, "failed": 0})
        case = result["cases"][0]
        self.assertEqual(case["case_id"], "minimal-cabinet-non-cad")
        self.assertEqual(case["actual"]["pipeline_status"], "ok")
        self.assertEqual(case["actual"]["dry_run_status"], "valid")
        self.assertEqual(case["actual"]["verification_status"], "unverified")

    def test_blank_shell_core_benchmark_runs_four_cases(self) -> None:
        result = run_benchmark_suite(
            PROJECT_ROOT / "examples/benchmarks/blank_shell_core_benchmark.json",
            output_root=artifact_path("benchmarks", "blank_shell_core"),
        )

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["summary"], {"total": 4, "passed": 4, "failed": 0})
        self.assertEqual(
            {case["case_id"] for case in result["cases"]},
            {"retail_blank_shell", "office_small_suite", "residential_living_room", "restaurant_small_front"},
        )
        for case in result["cases"]:
            self.assertGreaterEqual(case["actual"]["candidate_count"], 2)
            self.assertGreaterEqual(case["actual"]["zone_count"], 2)
            self.assertGreaterEqual(case["actual"]["placement_count"], 5)

    def test_blank_shell_benchmark_cases_use_distinct_workflows(self) -> None:
        suite = json.loads(
            (PROJECT_ROOT / "examples/benchmarks/blank_shell_core_benchmark.json").read_text(encoding="utf-8")
        )

        workflows = [case["workflow"] for case in suite["cases"]]
        self.assertEqual(len(workflows), 4)
        self.assertEqual(len(set(workflows)), 4)


if __name__ == "__main__":
    unittest.main()
