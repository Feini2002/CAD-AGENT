from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
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


class ScriptBootstrapTests(unittest.TestCase):
    def test_scripts_do_not_insert_sys_path_directly(self) -> None:
        offenders: list[str] = []
        for path in (PROJECT_ROOT / "scripts").glob("*.py"):
            if path.name == "_bootstrap.py":
                continue
            if _has_sys_path_insert_call(path):
                offenders.append(path.relative_to(PROJECT_ROOT).as_posix())
        self.assertEqual(offenders, [])

    def test_direct_script_entrypoints_still_run(self) -> None:
        command = [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "validate_plan.py"),
            str(PROJECT_ROOT / "examples" / "plans" / "draw_test_cabinet.json"),
        ]
        completed = subprocess.run(command, cwd=PROJECT_ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("VALID CAD_PLAN", completed.stdout)

    def test_json_cli_stdout_survives_non_ascii_workspace_path(self) -> None:
        env = os.environ.copy()
        env.pop("PYTHONIOENCODING", None)
        env["PYTHONUTF8"] = "0"
        command = [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_repo_audit.py"),
            "--root",
            str(PROJECT_ROOT),
            "--max-python-lines",
            "500",
        ]
        completed = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertNotIn("UnicodeEncodeError", completed.stderr)
        json.loads(completed.stdout)

    def test_package_import_of_script_wrapper_still_works(self) -> None:
        command = [
            sys.executable,
            "-c",
            "from scripts.execute_plan import execute_plan_file; print(callable(execute_plan_file))",
        ]
        completed = subprocess.run(command, cwd=PROJECT_ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("True", completed.stdout)


if __name__ == "__main__":
    unittest.main()
