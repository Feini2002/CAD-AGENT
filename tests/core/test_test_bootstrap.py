from __future__ import annotations

import ast
import unittest
from pathlib import Path

from tests.bootstrap import PROJECT_ROOT


def _has_sys_path_insert_call(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr != "insert":
            continue
        value = func.value
        if isinstance(value, ast.Attribute) and value.attr == "path" and isinstance(value.value, ast.Name) and value.value.id == "sys":
            return True
    return False


class TestBootstrapContractTests(unittest.TestCase):
    def test_project_root_points_to_repository_root(self) -> None:
        self.assertTrue((PROJECT_ROOT / "CORE_RESTRUCTURE_PLAN.md").exists())

    def test_core_tests_do_not_insert_sys_path_directly(self) -> None:
        offenders: list[str] = []
        for path in (PROJECT_ROOT / "tests" / "core").glob("test_*.py"):
            if path.name == "test_test_bootstrap.py":
                continue
            if _has_sys_path_insert_call(path):
                offenders.append(path.relative_to(PROJECT_ROOT).as_posix())
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
