from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable


SCHEMA_VERSION = "cad-agent-cleanroom-check/v1"

REQUIRED_PATHS = [
    "README.md",
    "AGENTS.md",
    "LICENSE",
    "pyproject.toml",
    "src/cad_agent",
    "src/cad_agent/resources/object_catalog.json",
    "tests",
    "evals/compiler",
    "evals/gate0",
    "tools",
    ".agents/skills/cad-scene-authoring/SKILL.md",
    "docs/ARCHITECTURE.md",
    "docs/SAFETY.md",
    "docs/STATUS.md",
    "docs/ROADMAP.md",
    "docs/DEVELOPMENT.md",
]

FORBIDDEN_PATHS = [
    "core",
    "agents",
    "projects",
    "libraries",
    "output",
    "scripts",
    "config/vnext",
    "docs/vnext",
    "docs/migration",
    "CAD_AGENT_vNext_Doc_Pack",
    "cad_floor_plan_reference_pack",
    "standard_cad_library_raw",
    "workers",
    "native_plugins",
    "capability-map.html",
    "capability-map-data.js",
    "CORE_CONTEXT_BRIEF.md",
    "CORE_RESTRUCTURE_PLAN.md",
    "CORE_STATUS.md",
]

FORBIDDEN_TEXT_TOKENS = [
    "cad_agent_vnext",
    "cad-agent-vnext",
    "scripts/vnext",
    "schemas/vnext",
    "config/vnext",
    "output/vnext",
    "docs/vnext",
    "CORE_CONTEXT_BRIEF",
    "CORE_RESTRUCTURE_PLAN",
]

SOURCE_FORBIDDEN_SNIPPETS = [
    "from core",
    "import core",
    "agents.pipeline",
]

TEXT_SUFFIXES = {".py", ".md", ".toml", ".json", ".jsonl", ".yml", ".yaml", ".gitignore"}


def build_report(root: str | Path = ".") -> dict[str, object]:
    root_path = Path(root).resolve()
    findings: list[dict[str, str]] = []

    for relative in REQUIRED_PATHS:
        if not (root_path / relative).exists():
            findings.append(_finding("required_path_missing", relative, "Required cleanroom path is missing."))

    for relative in FORBIDDEN_PATHS:
        if (root_path / relative).exists():
            findings.append(_finding("forbidden_path_present", relative, "Old repository path must not be present in main tree."))

    for path in _iter_text_files(root_path):
        relative = path.relative_to(root_path).as_posix()
        if relative == "tools/check_cleanroom.py" or relative.startswith("tests/"):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for token in FORBIDDEN_TEXT_TOKENS:
            if token in text:
                findings.append(_finding("forbidden_text_token", relative, f"Forbidden old path/token found: {token}"))
        if relative.startswith("src/cad_agent/"):
            for snippet in SOURCE_FORBIDDEN_SNIPPETS:
                if snippet in text:
                    findings.append(_finding("forbidden_source_import", relative, f"Forbidden old-system snippet found: {snippet}"))

    findings.extend(_check_gate0_cases(root_path / "evals" / "gate0" / "cases.jsonl"))

    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "pass" if not findings else "blocked",
        "root": str(root_path),
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check cleanroom repository shape.")
    parser.add_argument("--root", default=".")
    args = parser.parse_args(argv)

    report = build_report(args.root)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


def _iter_text_files(root: Path) -> Iterable[Path]:
    skip_dirs = {".git", ".codegraph", ".pytest_cache", ".venv", ".cad_agent_runs", ".cad_agent_schemas"}
    for path in root.rglob("*"):
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.is_file() and (path.suffix in TEXT_SUFFIXES or path.name in {"README.md", "AGENTS.md", ".gitignore"}):
            yield path


def _check_gate0_cases(path: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if not path.exists():
        return findings
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            findings.append(_finding("gate0_case_invalid_json", f"{path.as_posix()}:{line_number}", str(exc)))
            continue
        text = json.dumps(payload, ensure_ascii=False)
        for token in ("sceneSpecFixture", "deskWidth", "mouseSide", "monitorCount"):
            if token in text:
                findings.append(
                    _finding("gate0_case_contains_fixture", f"{path.as_posix()}:{line_number}", f"Gate 0 public case contains fixture token: {token}")
                )
    return findings


def _finding(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "severity": "blocked", "path": path, "message": message}


if __name__ == "__main__":
    sys.exit(main())
