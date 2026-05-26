from __future__ import annotations

import json
import unittest

from core.benchmarks.runner import run_benchmark_suite
from core.project_samples.benchmark import default_project_sample_benchmark_path, run_project_sample_benchmark
from core.project_samples.protocol import scan_projects_root
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class ProjectSampleBenchmarkTests(unittest.TestCase):
    def test_beta_project_sample_04_protocol_scan_includes_both_samples(self) -> None:
        report = scan_projects_root(PROJECT_ROOT / "projects")
        sample_ids = {item["sample_id"] for item in report["samples"]}
        self.assertEqual(report["status"], "pass")
        self.assertIn("sample_blank_shell", sample_ids)
        self.assertIn("sample_blank_shell_too_small", sample_ids)

    def test_beta_project_sample_04_benchmark_pass_and_blocked(self) -> None:
        output_root = artifact_path("benchmarks", "beta_project_sample_04")
        result = run_project_sample_benchmark(project_root=PROJECT_ROOT, output_root=output_root)

        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["summary"], {"total": 2, "passed": 2, "failed": 0})

        summary = result["evidence_summary"]
        self.assertEqual(summary["case_count"], 2)
        self.assertEqual(summary["benchmark_pass_non_cad_count"], 1)
        self.assertEqual(summary["blocked_expected_non_cad_count"], 1)
        self.assertEqual(summary.get("readback_geometry_verified_count", 0), 0)
        self.assertTrue(summary.get("non_cad_only", True))

        by_id = {case["case_id"]: case for case in result["cases"]}
        passed = by_id["sample_blank_shell_pass"]
        self.assertEqual(passed["actual"]["pipeline_status"], "ok")
        self.assertEqual(passed["actual"]["evidence_state"], "benchmark_pass_non_cad")
        self.assertGreaterEqual(passed["actual"]["cad_plan_count"], 5)
        self.assertEqual(passed["actual"]["shell_id"], "shell-sample-blank-shell")

        blocked = by_id["sample_blank_shell_too_small_blocked"]
        self.assertEqual(blocked["actual"]["pipeline_status"], "blocked")
        self.assertEqual(blocked["actual"]["evidence_state"], "blocked_expected_non_cad")
        self.assertEqual(blocked["actual"]["cad_plan_count"], 0)
        self.assertEqual(blocked["actual"]["shell_id"], "shell-sample-blank-shell-too-small")

        summary_path = output_root / "benchmark_summary.json"
        self.assertTrue(summary_path.is_file())
        saved = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "pass")

    def test_project_sample_benchmark_suite_path_exists(self) -> None:
        path = default_project_sample_benchmark_path(PROJECT_ROOT)
        self.assertTrue(path.is_file())
        suite = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(suite["suite_id"], "project-sample-benchmark")
        self.assertEqual(len(suite["cases"]), 2)

    def test_project_sample_workflows_use_projects_for_sample_inputs(self) -> None:
        project_roles = {"design_brief", "drawing_model", "shell_model"}
        for rel in (
            "examples/workflows/sample_blank_shell_project_loop.json",
            "examples/workflows/sample_blank_shell_too_small_loop.json",
        ):
            workflow = json.loads((PROJECT_ROOT / rel).read_text(encoding="utf-8"))
            for role, value in workflow["inputs"].items():
                if role not in project_roles:
                    continue
                self.assertTrue(
                    str(value).startswith("projects/"),
                    f"{rel} {role} should use projects/, got {value}",
                )


if __name__ == "__main__":
    unittest.main()
