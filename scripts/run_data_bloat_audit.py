#!/usr/bin/env python3
"""Run the read-only data-bloat audit before training."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.maintenance.data_bloat_audit import (  # noqa: E402
    DEFAULT_LINE_WARNING_COUNT,
    DEFAULT_OUTPUT_PATH,
    DEFAULT_SIZE_WARNING_BYTES,
    run_data_bloat_audit,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit data bloat and fact-source blockers before training.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--capability-map", type=Path, default=Path("capability-map-data.js"))
    parser.add_argument("--training-source-manifest", type=Path, default=Path("docs") / "training" / "training-sources.json")
    parser.add_argument(
        "--coverage",
        type=Path,
        default=Path("output") / "validation_runs" / "capability-lab" / "cad_capability_coverage.json",
    )
    parser.add_argument("--size-warning-bytes", type=int, default=DEFAULT_SIZE_WARNING_BYTES)
    parser.add_argument("--line-warning-count", type=int, default=DEFAULT_LINE_WARNING_COUNT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--summary-only", action="store_true", help="Print JSON only; do not write a report file.")
    parser.add_argument("--write", action="store_true", help="Write the audit report JSON. This never deletes or archives files.")
    args = parser.parse_args()

    report = run_data_bloat_audit(
        project_root=args.project_root,
        capability_map_path=args.capability_map,
        training_source_manifest_path=args.training_source_manifest,
        coverage_path=args.coverage,
        size_warning_bytes=args.size_warning_bytes,
        line_warning_count=args.line_warning_count,
        output_path=None if args.summary_only else args.output,
        write=args.write and not args.summary_only,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report.get("status") == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
