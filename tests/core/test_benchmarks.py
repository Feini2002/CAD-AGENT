from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
