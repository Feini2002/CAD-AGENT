from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import artifact_path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class BenchmarkCliTests(unittest.TestCase):
    def test_run_benchmark_suite_script_outputs_json_summary(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts/run_benchmark_suite.py"),
                "examples/benchmarks/non_cad_core_benchmark.json",
                "--output-root",
                str(artifact_path("benchmarks", "cli")),
            ],
            cwd=PROJECT_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["summary"]["passed"], 1)

    def test_run_blank_shell_pipeline_script_outputs_json_summary(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts/run_blank_shell_pipeline.py"),
                "examples/workflows/blank_shell_layout_loop.json",
                "--output-dir",
                str(artifact_path("blank_shell_pipeline", "cli")),
            ],
            cwd=PROJECT_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "ok")
        self.assertGreaterEqual(result["metrics"]["cad_plans"], 1)

    def test_scene_beta_wrappers_accept_output_root_alias(self) -> None:
        scripts = [
            ("run_office_scene_beta_benchmark.py", "office_scene_beta_cli"),
            ("run_residential_scene_beta_benchmark.py", "residential_scene_beta_cli"),
            ("run_restaurant_scene_beta_benchmark.py", "restaurant_scene_beta_cli"),
        ]

        for script_name, output_name in scripts:
            with self.subTest(script=script_name):
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(PROJECT_ROOT / "scripts" / script_name),
                        "--output-root",
                        str(artifact_path("benchmarks", output_name)),
                    ],
                    cwd=PROJECT_ROOT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    capture_output=True,
                    check=False,
                )

                self.assertEqual(completed.returncode, 0, completed.stderr)
                result = json.loads(completed.stdout)
                self.assertEqual(result["status"], "pass")


if __name__ == "__main__":
    unittest.main()
