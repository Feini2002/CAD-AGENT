#!/usr/bin/env python3
"""Close stale active evidence refs in the system asset library."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.assets.asset_evidence_closure import close_missing_asset_evidence_refs  # noqa: E402


DEFAULT_CLOSURE_REPORT = (
    PROJECT_ROOT
    / "output"
    / "validation_runs"
    / "system-assets"
    / "evidence-closure"
    / "drawing_standards_basic_evidence_closure.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive missing historical evidence refs and point active refs to current evidence.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--json-path", action="append", default=[])
    parser.add_argument("--closure-report", type=Path, default=DEFAULT_CLOSURE_REPORT)
    parser.add_argument("--report-ref", required=True)
    parser.add_argument("--visual-ref", default="")
    parser.add_argument("--extra-active-ref", action="append", default=[])
    parser.add_argument("--reason", default="historical evidence refs superseded by current asset-library evidence closure")
    args = parser.parse_args()

    default_json_paths = [
        args.project_root / "libraries/system_library/drawing_standards/basic/assets.json",
        args.project_root / "libraries/system_library/registry.json",
    ]
    json_paths = [Path(path) for path in args.json_path] if args.json_path else default_json_paths
    report = close_missing_asset_evidence_refs(
        project_root=args.project_root,
        json_paths=json_paths,
        closure_report_path=args.closure_report,
        report_ref=args.report_ref,
        visual_ref=args.visual_ref or None,
        extra_active_refs=args.extra_active_ref,
        reason=args.reason,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
