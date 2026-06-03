from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT

from core.maintenance.dev_volume_audit import DevVolumeThresholds, build_dev_volume_report


def _compact_report(report: dict, *, top_groups: int) -> dict:
    top_groups = max(1, top_groups)
    return {
        "status": report["status"],
        "root": report["root"],
        "summary": report["summary"],
        "findings": report["findings"],
        "top_changed_groups": report.get("top_changed_groups", [])[:top_groups],
        "top_tracked_groups": report.get("top_tracked_groups", [])[:top_groups],
        "top_untracked_groups": report.get("top_untracked_groups", [])[:top_groups],
        "largest_tracked_deltas": report.get("largest_tracked_deltas", [])[:top_groups],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize current local development volume.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--max-changed-files", type=int, default=DevVolumeThresholds.max_changed_files)
    parser.add_argument("--max-insertions", type=int, default=DevVolumeThresholds.max_insertions)
    parser.add_argument("--max-untracked-files", type=int, default=DevVolumeThresholds.max_untracked_files)
    parser.add_argument(
        "--max-single-file-insertions",
        type=int,
        default=DevVolumeThresholds.max_single_file_insertions,
    )
    parser.add_argument("--fail-on-findings", action="store_true")
    parser.add_argument("--fail-on-severity", choices=["low", "medium", "high"])
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--top-groups", type=int, default=10)
    args = parser.parse_args()

    thresholds = DevVolumeThresholds(
        max_changed_files=args.max_changed_files,
        max_insertions=args.max_insertions,
        max_untracked_files=args.max_untracked_files,
        max_single_file_insertions=args.max_single_file_insertions,
    )
    report = build_dev_volume_report(
        args.root,
        thresholds=thresholds,
        fail_on_severity=args.fail_on_severity or "medium",
    )
    output = _compact_report(report, top_groups=args.top_groups) if args.summary_only else report
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if args.fail_on_findings and report["status"] == "findings":
        return 1
    if args.fail_on_severity and report["summary"]["blocking_finding_count"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
