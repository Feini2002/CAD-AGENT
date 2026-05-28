#!/usr/bin/env python
"""V-PROOF-71: build LCAD-11 trend dashboard and sync registry smoke rows."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT

from core.verification.trend_dashboard import run_vproof_71_trend_dashboard_sync


def main() -> int:
    parser = argparse.ArgumentParser(description="V-PROOF-71 trend dashboard sync.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "output" / "validation_runs" / "vproof-71-trend-dashboard",
    )
    parser.add_argument("--sources", type=Path, help="Override trend_dashboard_sources.json")
    parser.add_argument("--no-refresh-coverage", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        summary = run_vproof_71_trend_dashboard_sync(
            project_root=args.root.resolve(),
            output_dir=args.output_dir.resolve(),
            sources_path=args.sources,
            dry_run=args.dry_run,
            refresh_coverage=not args.no_refresh_coverage,
        )
    except (AssertionError, FileNotFoundError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary.get("dashboard_status") != "pass":
        return 2
    if summary.get("writeback_rejected_count", 0) > 0:
        return 1
    if summary.get("writeback_applied_count", 0) < 1:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
