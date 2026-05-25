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


if __name__ == "__main__":
    unittest.main()
