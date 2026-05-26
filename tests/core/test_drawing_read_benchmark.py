from __future__ import annotations

import json
import shutil
import unittest

from core.drawing_analysis.drawing_read_benchmark import (
    default_drawing_read_benchmark_path,
    run_drawing_read_benchmark,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class DrawingReadBenchmarkTests(unittest.TestCase):
    def test_beta_drawing_read_05_benchmark_passes(self) -> None:
        output_root = artifact_path("benchmarks", "beta_drawing_read_05")
        result = run_drawing_read_benchmark(project_root=PROJECT_ROOT, output_root=output_root)

        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["summary"], {"total": 3, "passed": 3, "failed": 0})
        self.assertEqual(result["expected_evidence_summary_errors"], [])
        evidence = result["evidence_summary"]
        self.assertEqual(evidence["benchmark_pass_non_cad_count"], 2)
        self.assertEqual(evidence["blocked_expected_non_cad_count"], 1)

        by_id = {case["case_id"]: case for case in result["cases"]}
        blocked = by_id["walls_only_missing_opening_blocked"]
        self.assertEqual(blocked["actual"]["pipeline_status"], "blocked")
        blockers = blocked["actual"]["structured_blockers"]
        self.assertTrue(any(item["code"] == "missing_entry_opening" for item in blockers))

        full = by_id["geometry_feature_full_chain_pass"]
        self.assertEqual(full["actual"]["shell_id"], "shell-drawing-read-sample-geometry")
        self.assertEqual(full["actual"]["shell_export_status"], "ok")

        summary_path = output_root / "benchmark_summary.json"
        self.assertTrue(summary_path.is_file())

    def test_drawing_read_benchmark_suite_file_exists(self) -> None:
        path = default_drawing_read_benchmark_path(PROJECT_ROOT)
        self.assertTrue(path.is_file())
        suite = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(suite["suite_id"], "drawing-read-benchmark")

    def test_drawing_read_case_id_must_be_safe_path_segment(self) -> None:
        suite_path = artifact_path("benchmarks", "drawing_read_unsafe_case", "suite.json")
        suite = {
            "suite_id": "drawing-read-unsafe-case",
            "cases": [
                {
                    "case_id": "../escape",
                    "fixture": "examples/drawing_read/sample_geometry_feature_fixture.json",
                    "expected": {},
                }
            ],
        }
        suite_path.write_text(json.dumps(suite), encoding="utf-8")

        with self.assertRaises(ValueError):
            run_drawing_read_benchmark(
                project_root=PROJECT_ROOT,
                output_root=artifact_path("benchmarks", "drawing_read_unsafe_case", "out"),
                suite_path=suite_path,
            )

    def test_drawing_read_output_root_must_stay_under_project_output(self) -> None:
        output_root = PROJECT_ROOT / "tests" / "outside_drawing_read_output"
        try:
            with self.assertRaises(ValueError):
                run_drawing_read_benchmark(
                    project_root=PROJECT_ROOT,
                    output_root=output_root,
                )
        finally:
            if output_root.exists():
                shutil.rmtree(output_root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
