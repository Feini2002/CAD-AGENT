"""Development volume audit helpers for large local work batches."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DevVolumeThresholds:
    max_changed_files: int = 90
    max_insertions: int = 5000
    max_untracked_files: int = 50
    max_single_file_insertions: int = 1200


def _normalize_path(path: str) -> str:
    path = path.strip().strip('"')
    return path.replace("\\", "/")


def classify_path(path: str) -> str:
    normalized = _normalize_path(path)
    if normalized.startswith("tests/"):
        return "tests"
    if normalized.startswith("core/"):
        return "core_code"
    if normalized.startswith("scripts/"):
        return "scripts"
    if normalized.startswith("docs/handoffs/"):
        return "handoff_docs"
    if normalized.startswith("docs/"):
        return "docs"
    if normalized.startswith("examples/capability_proof/") or "capability_showcase" in normalized:
        return "capability_registry_showcase"
    if normalized.startswith("output/"):
        return "evidence_output"
    if normalized.endswith(".md"):
        return "status_docs"
    return "other"


def parse_porcelain_status(text: str) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    for line in text.splitlines():
        if not line:
            continue
        if line.startswith("?? "):
            status = "??"
            path = line[3:]
        else:
            status = line[:2].strip() or line[:2]
            path = line[3:] if len(line) > 3 else ""
        path = _normalize_path(path)
        if not path:
            continue
        changes.append({"status": status, "path": path, "area": classify_path(path)})
    return changes


def parse_numstat(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        additions_text, deletions_text, path_text = parts[0], parts[1], parts[2]
        additions = 0 if additions_text == "-" else int(additions_text)
        deletions = 0 if deletions_text == "-" else int(deletions_text)
        path = _normalize_path(path_text)
        rows.append(
            {
                "path": path,
                "area": classify_path(path),
                "additions": additions,
                "deletions": deletions,
            }
        )
    return rows


def _run_git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-c", "core.quotePath=false", *args],
        cwd=root,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=True,
    )
    return completed.stdout


def build_dev_volume_report(
    root: Path,
    *,
    thresholds: DevVolumeThresholds | None = None,
    status_text: str | None = None,
    numstat_text: str | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    thresholds = thresholds or DevVolumeThresholds()
    if status_text is None:
        status_text = _run_git(root, "status", "--short")
    if numstat_text is None:
        numstat_text = _run_git(root, "diff", "--numstat")

    status_rows = parse_porcelain_status(status_text)
    numstat_rows = parse_numstat(numstat_text)

    area_counts: dict[str, int] = {}
    for row in status_rows:
        area_counts[row["area"]] = area_counts.get(row["area"], 0) + 1

    area_line_delta: dict[str, dict[str, int]] = {}
    for row in numstat_rows:
        area = row["area"]
        bucket = area_line_delta.setdefault(area, {"additions": 0, "deletions": 0})
        bucket["additions"] += row["additions"]
        bucket["deletions"] += row["deletions"]

    untracked_count = sum(1 for row in status_rows if row["status"] == "??")
    changed_file_count = len(status_rows)
    tracked_file_count = changed_file_count - untracked_count
    total_insertions = sum(row["additions"] for row in numstat_rows)
    total_deletions = sum(row["deletions"] for row in numstat_rows)
    largest_files = sorted(
        numstat_rows,
        key=lambda row: (row["additions"] + row["deletions"], row["path"]),
        reverse=True,
    )[:10]

    findings: list[dict[str, Any]] = []
    if changed_file_count > thresholds.max_changed_files:
        findings.append(
            {
                "code": "large_changed_file_count",
                "severity": "medium",
                "message": f"{changed_file_count} changed files exceeds {thresholds.max_changed_files}.",
            }
        )
    if untracked_count > thresholds.max_untracked_files:
        findings.append(
            {
                "code": "large_untracked_file_count",
                "severity": "medium",
                "message": f"{untracked_count} untracked files exceeds {thresholds.max_untracked_files}.",
            }
        )
    if total_insertions > thresholds.max_insertions:
        findings.append(
            {
                "code": "large_insertion_count",
                "severity": "low",
                "message": f"{total_insertions} inserted lines exceeds {thresholds.max_insertions}.",
            }
        )
    oversized_files = [
        row for row in numstat_rows if row["additions"] > thresholds.max_single_file_insertions
    ]
    for row in oversized_files:
        findings.append(
            {
                "code": "large_single_file_delta",
                "severity": "low",
                "path": row["path"],
                "message": f"{row['additions']} inserted lines exceeds {thresholds.max_single_file_insertions}.",
            }
        )

    return {
        "status": "pass" if not findings else "findings",
        "root": str(root),
        "summary": {
            "changed_file_count": changed_file_count,
            "tracked_changed_file_count": tracked_file_count,
            "untracked_file_count": untracked_count,
            "insertions": total_insertions,
            "deletions": total_deletions,
            "finding_count": len(findings),
        },
        "by_area_file_count": dict(sorted(area_counts.items())),
        "by_area_line_delta": dict(sorted(area_line_delta.items())),
        "largest_tracked_deltas": largest_files,
        "thresholds": {
            "max_changed_files": thresholds.max_changed_files,
            "max_insertions": thresholds.max_insertions,
            "max_untracked_files": thresholds.max_untracked_files,
            "max_single_file_insertions": thresholds.max_single_file_insertions,
        },
        "findings": findings,
    }
