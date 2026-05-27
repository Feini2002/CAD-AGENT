from __future__ import annotations

import unittest
from pathlib import Path

from tests.bootstrap import PROJECT_ROOT

from core.path_safety import (
    resolve_under_project_output,
    resolve_under_project_root,
    validate_safe_path_segment,
)


class PathSafetyTests(unittest.TestCase):
    def test_rejects_output_outside_project_output_tree(self) -> None:
        with self.assertRaisesRegex(ValueError, "must stay under project output"):
            resolve_under_project_output(PROJECT_ROOT, Path("examples/plans/draw_test_cabinet.json"), label="output_dir")

    def test_rejects_plan_outside_project_root(self) -> None:
        with self.assertRaisesRegex(ValueError, "must stay under project root"):
            resolve_under_project_root(PROJECT_ROOT, Path("C:/outside/plan.json"), label="plan_path")

    def test_accepts_relative_output_under_output(self) -> None:
        resolved = resolve_under_project_output(
            PROJECT_ROOT,
            Path("output/validation_runs/path-safety-test"),
            label="output_dir",
        )
        self.assertTrue(str(resolved).replace("\\", "/").endswith("output/validation_runs/path-safety-test"))

    def test_validate_safe_path_segment_rejects_traversal(self) -> None:
        with self.assertRaisesRegex(ValueError, "safe path segment"):
            validate_safe_path_segment("../evil", label="case_id")


if __name__ == "__main__":
    unittest.main()
