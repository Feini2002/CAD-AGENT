from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable


SCHEMA_VERSION = "cad-agent-vnext-legacy-expansion-check/v1"
DEFAULT_STATE_PATH = Path("docs/vnext/MIGRATION_STATE.json")

ALLOWED_EXACT = {
    ".gitignore",
    "AGENTS.md",
    "README.md",
    "package.json",
    "pyproject.toml",
}

ALLOWED_PREFIXES = (
    ".agents/skills/cad-scene-authoring/",
    "config/vnext/",
    "docs/vnext/",
    "evals/gate0/",
    "output/vnext/",
    "schemas/vnext/generated/",
    "scripts/vnext/",
    "src/cad_agent_vnext/",
    "tests/vnext/",
)


def normalize_path(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def is_vnext_allowlisted(path: str) -> bool:
    normalized = normalize_path(path)
    return normalized in ALLOWED_EXACT or normalized.startswith(ALLOWED_PREFIXES)


def _finding(code: str, path: str, baseline_ref: str, message: str) -> dict[str, str]:
    return {
        "code": code,
        "severity": "blocked",
        "path": normalize_path(path),
        "baselineRef": baseline_ref,
        "message": message,
    }


def find_legacy_expansions(
    added_paths: Iterable[str],
    *,
    baseline_ref: str,
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []

    for raw_path in sorted({normalize_path(path) for path in added_paths if path}):
        if is_vnext_allowlisted(raw_path):
            continue

        path = normalize_path(raw_path)
        lower_path = path.lower()
        name = Path(path).name
        upper_name = name.upper()

        if path.startswith("agents/pipeline/") and path.endswith("/agent.json"):
            findings.append(
                _finding(
                    "legacy_pipeline_agent_added",
                    path,
                    baseline_ref,
                    "Gate 0 before VN-14 forbids adding legacy pipeline agent definitions.",
                )
            )
            continue

        if lower_path.startswith("docs/training/") and "curriculum" in lower_path:
            findings.append(
                _finding(
                    "training_curriculum_item_added",
                    path,
                    baseline_ref,
                    "Gate 0 before VN-14 forbids adding legacy training curriculum items.",
                )
            )
            continue

        if path.startswith("scripts/run_") and path.endswith(".py"):
            findings.append(
                _finding(
                    "legacy_run_script_added",
                    path,
                    baseline_ref,
                    "Gate 0 before VN-14 forbids adding legacy-style scripts/run_*.py entrypoints.",
                )
            )
            continue

        if "/" not in path and path.endswith(".md") and (
            "ARCHITECTURE" in upper_name or "PLAN" in upper_name
        ):
            findings.append(
                _finding(
                    "root_architecture_doc_added",
                    path,
                    baseline_ref,
                    "Gate 0 before VN-14 forbids adding new root architecture or planning Markdown files.",
                )
            )
            continue

        if any(token in lower_path for token in ("table_a", "table_b", "table_c", "表a", "表b", "表c")):
            findings.append(
                _finding(
                    "legacy_table_field_candidate_added",
                    path,
                    baseline_ref,
                    "Gate 0 before VN-14 forbids expanding legacy table A/B/C surfaces outside vNext.",
                )
            )

    return findings


def load_baseline_ref(root: Path) -> str:
    state_path = root / DEFAULT_STATE_PATH
    if not state_path.exists():
        return "HEAD"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    return str(state.get("baselineCommit") or "HEAD")


def run_git(root: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"git {' '.join(args)} failed")
    return completed.stdout


def expand_untracked_path(root: Path, path: str) -> list[str]:
    candidate = root / path
    if candidate.is_dir():
        return [
            normalize_path(str(child.relative_to(root)))
            for child in candidate.rglob("*")
            if child.is_file()
        ]
    return [normalize_path(path)]


def collect_added_paths(root: Path, baseline_ref: str) -> list[str]:
    added: set[str] = set()

    diff_output = run_git(root, ["diff", "--name-status", "--diff-filter=A", baseline_ref, "--"])
    for line in diff_output.splitlines():
        parts = line.split("\t", 1)
        if len(parts) == 2:
            added.add(normalize_path(parts[1]))

    status_output = run_git(root, ["status", "--porcelain=v1", "--untracked-files=all"])
    for line in status_output.splitlines():
        status = line[:2]
        path = normalize_path(line[3:])
        if status == "??":
            added.update(expand_untracked_path(root, path))
        elif "A" in status:
            added.add(path)

    return sorted(added)


def build_report(root: Path, baseline_ref: str) -> dict[str, object]:
    added_paths = collect_added_paths(root, baseline_ref)
    findings = find_legacy_expansions(added_paths, baseline_ref=baseline_ref)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "blocked" if findings else "pass",
        "baselineRef": baseline_ref,
        "checkedAddedPathCount": len(added_paths),
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check that legacy expansion remains frozen during vNext Gate 0 work.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--baseline-ref", help="Baseline commit or tag. Defaults to docs/vnext/MIGRATION_STATE.json.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    baseline_ref = args.baseline_ref or load_baseline_ref(root)
    report = build_report(root, baseline_ref)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["status"] == "blocked" else 0


if __name__ == "__main__":
    sys.exit(main())
