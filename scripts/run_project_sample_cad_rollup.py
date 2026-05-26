#!/usr/bin/env python3
"""Run LCAD-08 project sample CAD rollup across registered samples."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.project_samples.project_sample_cad_rollup import (  # noqa: E402
    connect_autocad_driver,
    run_project_sample_cad_rollup,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/validation_runs/project-sample-cad-rollup"),
    )
    parser.add_argument("--no-cad", action="store_true")
    parser.add_argument(
        "--require-cad-verified",
        action="store_true",
        help="Return non-zero unless rollup status is geometry_verified.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    driver = None
    if not args.no_cad:
        try:
            driver = connect_autocad_driver()
        except Exception as exc:
            print(f"AutoCAD unavailable ({exc}); use --no-cad for deferred.", file=sys.stderr)
            return 2

    report = run_project_sample_cad_rollup(
        args.output_dir.resolve(),
        project_root=root,
        driver=driver,
        no_cad=args.no_cad,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if report.get("status") == "geometry_verified":
        return 0
    if args.require_cad_verified:
        return 1
    if report.get("status") in {"deferred", "invalid"}:
        return 0 if report.get("status") == "deferred" else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
