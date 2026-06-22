from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Iterable


SCHEMA_VERSION = "cad-agent-vnext-import-boundaries/v1"
VNEXT_ROOT = Path("src/cad_agent_vnext")

DOMAIN_FORBIDDEN_IMPORTS = (
    "openai",
    "agents",
    "openai_codex",
    "win32com",
    "core",
    "cad_agent",
    "agents.pipeline",
)
GLOBAL_FORBIDDEN_PARTS = (
    "training",
    "workbench",
    "coverage",
)
LEGACY_IMPORT_PREFIXES = (
    "core",
    "cad_agent",
    "agents.pipeline",
)
CAD_WRITE_CALLS = {
    "apply_preview_patch",
    "update_preview_objects",
    "delete_preview_objects",
    "rollback_transaction",
    "execute_preview",
    "save",
    "save_as",
}
BUSINESS_ROUTE_TOKENS = (
    "KEYWORD",
    "KEYWORDS",
    "EXACT_ROUTE",
    "PHRASE_ROUTE",
)


def normalize_path(path: Path) -> str:
    return path.as_posix()


def is_same_or_child(module_name: str, prefix: str) -> bool:
    return module_name == prefix or module_name.startswith(f"{prefix}.")


def finding(code: str, path: Path, message: str, *, detail: str | None = None) -> dict[str, str]:
    payload = {
        "code": code,
        "severity": "blocked",
        "path": normalize_path(path),
        "message": message,
    }
    if detail:
        payload["detail"] = detail
    return payload


def iter_imports(tree: ast.AST) -> Iterable[str]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                yield node.module


def iter_call_names(tree: ast.AST) -> Iterable[str]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                yield func.id
            elif isinstance(func, ast.Attribute):
                yield func.attr


def iter_assigned_names(tree: ast.AST) -> Iterable[str]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    yield target.id
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            yield node.target.id


def is_legacy_adapter(path: Path) -> bool:
    return normalize_path(path).endswith("src/cad_agent_vnext/adapters/legacy_autocad_backend.py")


def check_file(root: Path, path: Path) -> list[dict[str, str]]:
    relative = path.relative_to(root)
    normalized = normalize_path(relative)
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return [finding("python_syntax_error", relative, "Python file could not be parsed.", detail=str(exc))]

    imports = list(iter_imports(tree))
    findings: list[dict[str, str]] = []

    if normalized.startswith("src/cad_agent_vnext/domain/"):
        for module_name in imports:
            if any(is_same_or_child(module_name, prefix) for prefix in DOMAIN_FORBIDDEN_IMPORTS):
                findings.append(
                    finding(
                        "domain_forbidden_import",
                        relative,
                        "domain/** must stay pure and cannot import model runtimes, AutoCAD, or legacy modules.",
                        detail=module_name,
                    )
                )

    if normalized.startswith("src/cad_agent_vnext/planning/"):
        for module_name in imports:
            if module_name.startswith("cad_agent_vnext.adapters") or "autocad" in module_name.lower():
                findings.append(
                    finding(
                        "planning_forbidden_adapter_import",
                        relative,
                        "planning/** must not import AutoCAD adapters.",
                        detail=module_name,
                    )
                )

    if normalized.startswith("src/cad_agent_vnext/verification/"):
        for call_name in iter_call_names(tree):
            if call_name in CAD_WRITE_CALLS:
                findings.append(
                    finding(
                        "verification_forbidden_cad_write_call",
                        relative,
                        "verification/** must not call CAD write operations.",
                        detail=call_name,
                    )
                )

    if normalized.startswith("src/cad_agent_vnext/tools/"):
        for assigned_name in iter_assigned_names(tree):
            upper_name = assigned_name.upper()
            if any(token in upper_name for token in BUSINESS_ROUTE_TOKENS):
                findings.append(
                    finding(
                        "tools_business_keyword_route",
                        relative,
                        "tools/** must not define business keyword route tables.",
                        detail=assigned_name,
                    )
                )

    for module_name in imports:
        if any(is_same_or_child(module_name, prefix) for prefix in LEGACY_IMPORT_PREFIXES):
            if not is_legacy_adapter(relative):
                findings.append(
                    finding(
                        "vnext_forbidden_legacy_import",
                        relative,
                        "vNext code must not import legacy modules except legacy_autocad_backend.py.",
                        detail=module_name,
                    )
                )

        if any(part in module_name.split(".") for part in GLOBAL_FORBIDDEN_PARTS):
            findings.append(
                finding(
                    "vnext_forbidden_control_plane_import",
                    relative,
                    "vNext code must not import training/workbench/status/coverage control-plane modules.",
                    detail=module_name,
                )
            )

    return findings


def check_import_boundaries(root: str | Path = ".") -> list[dict[str, str]]:
    root_path = Path(root).resolve()
    source_root = root_path / VNEXT_ROOT
    if not source_root.exists():
        return []

    findings: list[dict[str, str]] = []
    for path in sorted(source_root.rglob("*.py")):
        findings.extend(check_file(root_path, path))
    return findings


def build_report(root: str | Path = ".") -> dict[str, object]:
    root_path = Path(root).resolve()
    findings = check_import_boundaries(root_path)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "blocked" if findings else "pass",
        "root": str(root_path),
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check vNext import boundaries.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    args = parser.parse_args(argv)

    report = build_report(args.root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["status"] == "blocked" else 0


if __name__ == "__main__":
    sys.exit(main())
