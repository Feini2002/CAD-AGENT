from __future__ import annotations

import json
import subprocess
import sys
import unittest

from tests.helpers import PROJECT_ROOT, artifact_path
from core.maintenance.repo_audit import run_repo_audit


class RepoAuditTests(unittest.TestCase):
    def test_flags_large_python_file_and_raw_sys_path_insert(self) -> None:
        root = artifact_path("repo_audit", "large_file_case")
        package = root / "core"
        package.mkdir(parents=True, exist_ok=True)
        target = package / "large.py"
        target.write_text(
            "import sys\n"
            "sys.path.insert(0, 'bad')\n"
            + "\n".join(f"x{i} = {i}" for i in range(8)),
            encoding="utf-8",
        )

        report = run_repo_audit(root, max_python_lines=5)

        codes = {finding["code"] for finding in report["findings"]}
        self.assertIn("large_python_file", codes)
        self.assertIn("raw_sys_path_insert", codes)
        self.assertEqual(report["summary"]["finding_count"], 2)

    def test_ignores_pycache_when_it_is_not_tracked(self) -> None:
        root = artifact_path("repo_audit", "pycache_case")
        cache = root / "core" / "__pycache__"
        cache.mkdir(parents=True, exist_ok=True)
        (cache / "x.pyc").write_bytes(b"cache")

        report = run_repo_audit(root)

        self.assertEqual(report["summary"]["finding_count"], 0)

    def test_does_not_flag_sys_path_text_inside_string_literals(self) -> None:
        root = artifact_path("repo_audit", "fixture_string_case")
        root.mkdir(parents=True, exist_ok=True)
        target = root / "test_fixture.py"
        target.write_text(
            "fixture = \"sys.path.insert(0, 'bad')\"\n",
            encoding="utf-8",
        )

        report = run_repo_audit(root)

        codes = {finding["code"] for finding in report["findings"]}
        self.assertNotIn("raw_sys_path_insert", codes)

    def test_flags_other_python_path_mutation_shapes(self) -> None:
        root = artifact_path("repo_audit", "path_mutation_shapes")
        package = root / "core"
        package.mkdir(parents=True, exist_ok=True)
        (package / "alias.py").write_text(
            "import sys as system\nsystem.path.append('bad')\n",
            encoding="utf-8",
        )
        (package / "from_import.py").write_text(
            "from sys import path as sys_path\nsys_path.extend(['bad'])\n",
            encoding="utf-8",
        )
        (package / "__init__.py").write_text(
            "__path__.append('bad')\n",
            encoding="utf-8",
        )

        report = run_repo_audit(root)

        flagged_paths = {finding["path"].replace("\\", "/") for finding in report["findings"]}
        self.assertIn("core/alias.py", flagged_paths)
        self.assertIn("core/from_import.py", flagged_paths)
        self.assertIn("core/__init__.py", flagged_paths)

    def test_cli_emits_json_report(self) -> None:
        root = artifact_path("repo_audit", "cli_case")
        root.mkdir(parents=True, exist_ok=True)
        target = root / "script.py"
        target.write_text("import sys\nsys.path.insert(0, 'bad')\n", encoding="utf-8")

        completed = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "run_repo_audit.py"),
                "--root",
                str(root),
                "--max-python-lines",
                "1",
            ],
            cwd=PROJECT_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "findings")
        self.assertEqual(report["summary"]["finding_count"], 2)

    def test_cli_can_fail_on_findings_when_used_as_gate(self) -> None:
        root = artifact_path("repo_audit", "cli_gate_case")
        root.mkdir(parents=True, exist_ok=True)
        target = root / "script.py"
        target.write_text("import sys\nsys.path.insert(0, 'bad')\n", encoding="utf-8")

        completed = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "run_repo_audit.py"),
                "--root",
                str(root),
                "--fail-on-findings",
            ],
            cwd=PROJECT_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )

        self.assertEqual(completed.returncode, 1)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "findings")

    def test_ignores_common_local_dependency_directories(self) -> None:
        root = artifact_path("repo_audit", "ignored_dependency_dirs")
        package = root / ".venv" / "Lib" / "site-packages"
        package.mkdir(parents=True, exist_ok=True)
        target = package / "large.py"
        target.write_text("import sys\nsys.path.insert(0, 'bad')\n", encoding="utf-8")

        report = run_repo_audit(root, max_python_lines=1)

        self.assertEqual(report["summary"]["finding_count"], 0)


if __name__ == "__main__":
    unittest.main()
