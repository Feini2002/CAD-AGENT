from __future__ import annotations

import shutil
import unittest

from scripts.run_composition_cad_check import run_composition_cad_check
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class CompositionCadCheckSafetyTests(unittest.TestCase):
    def test_rejects_benchmark_output_root_outside_project_output_before_cad_connect(self) -> None:
        outside_root = PROJECT_ROOT / "tests" / "outside_composition_benchmark"
        output_dir = artifact_path("composition_cad_check", "outside_benchmark_rejected")
        try:
            with self.assertRaisesRegex(ValueError, "benchmark_output_root"):
                run_composition_cad_check(
                    benchmark_output_root=outside_root,
                    output_dir=output_dir,
                )
        finally:
            if outside_root.exists():
                shutil.rmtree(outside_root, ignore_errors=True)

    def test_rejects_output_dir_outside_project_output_before_cad_connect(self) -> None:
        benchmark_output_root = artifact_path("benchmarks", "composition_contract")
        outside_output = PROJECT_ROOT / "tests" / "outside_composition_cad"
        try:
            with self.assertRaisesRegex(ValueError, "output_dir"):
                run_composition_cad_check(
                    benchmark_output_root=benchmark_output_root,
                    output_dir=outside_output,
                )
        finally:
            if outside_output.exists():
                shutil.rmtree(outside_output, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
