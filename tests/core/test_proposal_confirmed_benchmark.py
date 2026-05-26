from __future__ import annotations

import json
import shutil
import unittest

from core.proposal_engine.confirmed_benchmark import (
    default_proposal_confirmed_benchmark_path,
    run_proposal_confirmed_benchmark,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class ProposalConfirmedBenchmarkTests(unittest.TestCase):
    def test_beta_proposal_05_confirmed_benchmark_passes(self) -> None:
        output_root = artifact_path("benchmarks", "beta_proposal_05")
        result = run_proposal_confirmed_benchmark(project_root=PROJECT_ROOT, output_root=output_root)

        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["summary"], {"total": 2, "passed": 2, "failed": 0})
        self.assertEqual(result["evidence_summary"]["benchmark_pass_non_cad_count"], 2)
        self.assertEqual(result["evidence_summary"]["readback_geometry_verified_count"], 0)
        self.assertTrue(result["evidence_summary"]["non_cad_only"])
        for case in result["cases"]:
            self.assertEqual(case["status"], "pass", case)
            self.assertEqual(case["actual"]["evidence_state"], "benchmark_pass_non_cad")
            self.assertEqual(case["actual"]["geometry_accuracy"], "not_verified_without_cad_readback")
            self.assertEqual(case["actual"]["screenshot_role"], "visual_aid_only")
            self.assertTrue(case["actual"]["validation_all_valid"])
            self.assertGreaterEqual(case["actual"]["unselected_candidate_count"], 1)

        summary_path = output_root / "benchmark_summary.json"
        self.assertTrue(summary_path.is_file())
        saved = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertIn("evidence_summary", saved)

    def test_confirmed_benchmark_suite_file_exists(self) -> None:
        path = default_proposal_confirmed_benchmark_path(PROJECT_ROOT)
        self.assertTrue(path.is_file())
        suite = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(suite["suite_id"], "proposal-confirmed-benchmark")
        for case in suite["cases"]:
            expected = case["expected"]
            self.assertIn("evidence_state", expected)
            self.assertIn("geometry_accuracy", expected)
            self.assertIn("screenshot_role", expected)

    def test_confirmed_benchmark_rejects_output_root_outside_project_output(self) -> None:
        output_root = PROJECT_ROOT / "tests" / "outside_confirmed_benchmark"
        try:
            with self.assertRaisesRegex(ValueError, "output_root"):
                run_proposal_confirmed_benchmark(project_root=PROJECT_ROOT, output_root=output_root)
        finally:
            if output_root.exists():
                shutil.rmtree(output_root, ignore_errors=True)

    def test_confirmed_benchmark_rejects_unsafe_case_id(self) -> None:
        suite_path = artifact_path("benchmarks", "unsafe_confirmed_suite.json")
        suite_path.write_text(
            json.dumps(
                {
                    "suite_id": "unsafe-confirmed-benchmark",
                    "cases": [
                        {
                            "case_id": "../escape",
                            "workflow": "examples/workflows/blank_shell_layout_loop.json",
                            "selected_candidate_id": "candidate-main",
                            "expected": {
                                "finalize_status": "ok",
                                "validation_all_valid": True,
                                "requires_unselected_evidence": True,
                                "evidence_state": "benchmark_pass_non_cad",
                                "geometry_accuracy": "not_verified_without_cad_readback",
                                "screenshot_role": "visual_aid_only",
                            },
                        }
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "case_id"):
            run_proposal_confirmed_benchmark(
                project_root=PROJECT_ROOT,
                output_root=artifact_path("benchmarks", "unsafe_confirmed_out"),
                suite_path=suite_path,
            )


if __name__ == "__main__":
    unittest.main()
