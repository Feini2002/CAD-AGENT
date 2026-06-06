"""Development volume audit helpers for large local work batches."""

from __future__ import annotations

import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3}


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
    if normalized.startswith("agents/"):
        return "agents"
    if normalized.startswith("openspec/"):
        return "openspec"
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


def _severity_counts(findings: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(finding.get("severity", "medium") for finding in findings)
    return {severity: counts.get(severity, 0) for severity in SEVERITY_RANK}


def _blocking_finding_count(
    findings: list[dict[str, Any]],
    *,
    fail_on_severity: str = "medium",
) -> int:
    threshold = SEVERITY_RANK[fail_on_severity]
    return sum(
        1
        for finding in findings
        if SEVERITY_RANK.get(finding.get("severity", "medium"), SEVERITY_RANK["medium"])
        >= threshold
    )


def _path_group(path: str) -> str:
    parts = _normalize_path(path).split("/")
    if len(parts) >= 2 and parts[0] == "openspec" and parts[1] == "changes":
        return "openspec/changes"
    if len(parts) >= 2:
        return "/".join(parts[:2])
    return parts[0]


def _top_group_summaries(
    groups: set[str],
    *,
    changed_counts: Counter[str],
    tracked_counts: Counter[str],
    untracked_counts: Counter[str],
    line_delta: dict[str, dict[str, int]],
    sort_count_key: str,
    limit: int = 10,
) -> list[dict[str, int | str]]:
    rows: list[dict[str, int | str]] = []
    for group in groups:
        delta = line_delta.get(group, {"additions": 0, "deletions": 0})
        rows.append(
            {
                "group": group,
                "changed_files": changed_counts.get(group, 0),
                "tracked_files": tracked_counts.get(group, 0),
                "untracked_files": untracked_counts.get(group, 0),
                "additions": delta["additions"],
                "deletions": delta["deletions"],
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            -int(row[sort_count_key]),
            -(int(row["additions"]) + int(row["deletions"])),
            str(row["group"]),
        ),
    )[:limit]


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
    fail_on_severity: str = "medium",
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

    tracked_status_rows = [row for row in status_rows if row["status"] != "??"]
    tracked_area_counts = Counter(row["area"] for row in tracked_status_rows)
    changed_group_counts = Counter(_path_group(row["path"]) for row in status_rows)
    tracked_group_counts = Counter(_path_group(row["path"]) for row in tracked_status_rows)

    area_line_delta: dict[str, dict[str, int]] = {}
    group_line_delta: dict[str, dict[str, int]] = {}
    for row in numstat_rows:
        area = row["area"]
        bucket = area_line_delta.setdefault(area, {"additions": 0, "deletions": 0})
        bucket["additions"] += row["additions"]
        bucket["deletions"] += row["deletions"]
        group = _path_group(row["path"])
        group_bucket = group_line_delta.setdefault(group, {"additions": 0, "deletions": 0})
        group_bucket["additions"] += row["additions"]
        group_bucket["deletions"] += row["deletions"]

    untracked_rows = [row for row in status_rows if row["status"] == "??"]
    untracked_count = len(untracked_rows)
    changed_file_count = len(status_rows)
    tracked_file_count = changed_file_count - untracked_count
    artifact_only = bool(status_rows) and all(row["area"] == "evidence_output" for row in status_rows)
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
                "severity": "low" if artifact_only else "medium",
                "artifactOnly": artifact_only,
                "message": f"{changed_file_count} changed files exceeds {thresholds.max_changed_files}.",
            }
        )
    if untracked_count > thresholds.max_untracked_files:
        findings.append(
            {
                "code": "large_untracked_file_count",
                "severity": "low" if artifact_only else "medium",
                "artifactOnly": artifact_only,
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

    untracked_area_counts = Counter(row["area"] for row in untracked_rows)
    untracked_group_counts = Counter(_path_group(row["path"]) for row in untracked_rows)
    severity_counts = _severity_counts(findings)
    all_groups = set(changed_group_counts) | set(group_line_delta)

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
            "severity_counts": severity_counts,
            "blocking_severity": fail_on_severity,
            "blocking_finding_count": _blocking_finding_count(
                findings,
                fail_on_severity=fail_on_severity,
            ),
        },
        "by_area_file_count": dict(sorted(area_counts.items())),
        "by_area_line_delta": dict(sorted(area_line_delta.items())),
        "tracked_by_area": dict(sorted(tracked_area_counts.items())),
        "changed_groups": dict(sorted(changed_group_counts.items())),
        "tracked_groups": dict(sorted(tracked_group_counts.items())),
        "untracked_by_area": dict(sorted(untracked_area_counts.items())),
        "untracked_groups": dict(sorted(untracked_group_counts.items())),
        "by_group_line_delta": dict(sorted(group_line_delta.items())),
        "top_changed_groups": _top_group_summaries(
            all_groups,
            changed_counts=changed_group_counts,
            tracked_counts=tracked_group_counts,
            untracked_counts=untracked_group_counts,
            line_delta=group_line_delta,
            sort_count_key="changed_files",
        ),
        "top_tracked_groups": _top_group_summaries(
            set(tracked_group_counts) | set(group_line_delta),
            changed_counts=changed_group_counts,
            tracked_counts=tracked_group_counts,
            untracked_counts=untracked_group_counts,
            line_delta=group_line_delta,
            sort_count_key="tracked_files",
        ),
        "top_untracked_groups": _top_group_summaries(
            set(untracked_group_counts),
            changed_counts=changed_group_counts,
            tracked_counts=tracked_group_counts,
            untracked_counts=untracked_group_counts,
            line_delta=group_line_delta,
            sort_count_key="untracked_files",
        ),
        "largest_tracked_deltas": largest_files,
        "thresholds": {
            "max_changed_files": thresholds.max_changed_files,
            "max_insertions": thresholds.max_insertions,
            "max_untracked_files": thresholds.max_untracked_files,
            "max_single_file_insertions": thresholds.max_single_file_insertions,
        },
        "findings": findings,
    }
