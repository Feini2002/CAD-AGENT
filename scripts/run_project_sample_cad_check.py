#!/usr/bin/env python3
"""Execute project sample CAD_PLAN items in AutoCAD (BETA-PROJECT-SAMPLE-05)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.project_samples.cad_check import (  # noqa: E402
    DEFAULT_CAD_OFFSET,
    DEFAULT_SAMPLE_ID,
    connect_autocad_driver,
    run_project_sample_cad_check_with_workflow,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run optional CODEX_PREVIEW CAD check for project sample blank-shell workflow."
    )
    parser.add_argument("--sample-id", default=DEFAULT_SAMPLE_ID)
    parser.add_argument(
        "--workflow-output-dir",
        type=Path,
        default=Path("output/test_artifacts/project_samples/beta_project_sample_05/workflow"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/validation_runs/beta-project-sample-05-cad"),
    )
    parser.add_argument(
        "--no-cad",
        action="store_true",
        help="Emit deferred_cad_readback_required without connecting to AutoCAD.",
    )
    parser.add_argument(
        "--require-cad-verified",
        action="store_true",
        help="Return non-zero unless the saved report is geometry_verified.",
    )
    parser.add_argument("--start-x", type=float, default=DEFAULT_CAD_OFFSET[0])
    parser.add_argument("--start-y", type=float, default=DEFAULT_CAD_OFFSET[1])
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    offset = [args.start_x, args.start_y, 0]
    driver = None
    if not args.no_cad:
        try:
            driver = connect_autocad_driver()
        except Exception as exc:
            print(f"AutoCAD unavailable ({exc}); use --no-cad for deferred evidence.", file=sys.stderr)
            return 2

    report = run_project_sample_cad_check_with_workflow(
        project_root=root,
        workflow_output_dir=args.workflow_output_dir.resolve(),
        cad_output_dir=args.output_dir.resolve(),
        sample_id=args.sample_id,
        driver=driver,
        no_cad=args.no_cad,
        offset=offset,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if report.get("status") == "geometry_verified":
        return 0
    if args.require_cad_verified:
        print("CAD geometry verification required but report is not geometry_verified.", file=sys.stderr)
        return 1
    if report.get("status") == "deferred":
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
