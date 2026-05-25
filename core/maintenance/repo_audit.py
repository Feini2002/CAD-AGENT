"""Repository audit helpers for low-risk hardening work."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


IGNORED_DIR_NAMES = {
    "__pycache__",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "node_modules",
    "output",
    "venv",
}


def _iter_python_files(root: Path) -> list[Path]:
    root = root.resolve()
    files: list[Path] = []
    for path in root.rglob("*.py"):
        relative_parts = path.relative_to(root).parts
        if any(part in IGNORED_DIR_NAMES for part in relative_parts):
            continue
        files.append(path)
    return sorted(files)


def _finding(
    code: str,
    path: Path,
    message: str,
    *,
    severity: str = "medium",
) -> dict[str, str]:
    return {
        "code": code,
        "severity": severity,
        "path": str(path),
        "message": message,
    }


def _has_python_path_mutation_call(text: str) -> bool:
    tree = ast.parse(text)
    sys_names = {"sys"}
    sys_path_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "sys":
                    sys_names.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module == "sys":
            for alias in node.names:
                if alias.name == "path":
                    sys_path_names.add(alias.asname or alias.name)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr not in {"insert", "append", "extend"}:
            continue
        value = func.value
        if isinstance(value, ast.Name) and value.id in sys_path_names:
            return True
        if isinstance(value, ast.Name) and value.id == "__path__":
            return True
        if isinstance(value, ast.Attribute) and value.attr == "path":
            owner = value.value
            if isinstance(owner, ast.Name) and owner.id in sys_names:
                return True
    return False


def run_repo_audit(root: Path, *, max_python_lines: int = 500) -> dict[str, Any]:
    """Return structured findings for maintainability risks that are cheap to verify."""

    root = root.resolve()
    findings: list[dict[str, str]] = []
    for path in _iter_python_files(root):
        rel_path = path.relative_to(root)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(
                _finding(
                    "non_utf8_python_file",
                    rel_path,
                    "Python file is not UTF-8 decodable.",
                )
            )
            continue

        line_count = len(text.splitlines())
        if line_count > max_python_lines:
            findings.append(
                _finding(
                    "large_python_file",
                    rel_path,
                    f"Python file has {line_count} lines, above limit {max_python_lines}.",
                    severity="low",
                )
            )
        try:
            has_raw_sys_path_insert = _has_python_path_mutation_call(text)
        except SyntaxError:
            findings.append(
                _finding(
                    "python_syntax_error",
                    rel_path,
                    "Python file cannot be parsed by ast.",
                )
            )
            has_raw_sys_path_insert = False

        if has_raw_sys_path_insert and rel_path.as_posix() not in {
            "scripts/_bootstrap.py",
            "tests/bootstrap.py",
            "tests/core/__init__.py",
        }:
            findings.append(
                _finding(
                    "raw_sys_path_insert",
                    rel_path,
                    "Use shared bootstrap instead of local Python path mutation.",
                )
            )

    return {
        "status": "pass" if not findings else "findings",
        "root": str(root),
        "summary": {"finding_count": len(findings)},
        "findings": findings,
    }
