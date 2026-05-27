#!/usr/bin/env python
"""Execute interior delivery composition CAD_PLAN artifacts in AutoCAD."""

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

from core.path_safety import resolve_under_project_output
from core.verification.composition_cad_check import DEFAULT_CASE_ORDER, build_case_offsets, run_composition_cad_check


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute composition benchmark CAD plans in AutoCAD.")
    parser.add_argument(
        "--benchmark-output-root",
        type=Path,
        default=PROJECT_ROOT / "output" / "test_artifacts" / "benchmarks" / "interior_delivery_manual",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "output" / "validation_runs" / "interior-composition-cad",
    )
    parser.add_argument(
        "--start-x",
        type=float,
        default=12000,
        help="World X coordinate for the first composition case. Use a new value to avoid old preview entities.",
    )
    parser.add_argument(
        "--spacing-x",
        type=float,
        default=4200,
        help="Horizontal spacing between composition cases.",
    )
    parser.add_argument(
        "--start-y",
        type=float,
        default=0,
        help="World Y coordinate for all composition cases. Use a high value to avoid existing DWG geometry.",
    )
    parser.add_argument(
        "--case",
        dest="case_ids",
        action="append",
        default=None,
        help="Composition benchmark case id to run. Repeat for multiple cases. Default: interior delivery trio.",
    )
    args = parser.parse_args()

    selected_case_ids = args.case_ids or list(DEFAULT_CASE_ORDER)
    report = run_composition_cad_check(
        benchmark_output_root=resolve_under_project_output(
            PROJECT_ROOT, args.benchmark_output_root, label="benchmark_output_root"
        ),
        output_dir=resolve_under_project_output(PROJECT_ROOT, args.output_dir, label="output_dir"),
        case_ids=selected_case_ids,
        case_offsets=build_case_offsets(
            selected_case_ids,
            start_x=args.start_x,
            start_y=args.start_y,
            spacing_x=args.spacing_x,
        ),
        project_root=PROJECT_ROOT,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "geometry_verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
