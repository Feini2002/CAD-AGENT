#!/usr/bin/env python
"""Run CAD_PLAN fixture validate / dry-run / optional CODEX_PREVIEW execution."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.path_safety import resolve_under_project_output
from core.verification.cad_plan_fixture_suite import run_cad_plan_fixture_suite


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CAD_PLAN fixture suite for LCAD regression.")
    parser.add_argument("--no-cad", action="store_true", help="Only validate and dry-run fixtures.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=None)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    output_dir = resolve_under_project_output(root, args.output_dir, label="output_dir")
    report = run_cad_plan_fixture_suite(
        root=root,
        manifest_path=args.manifest,
        output_dir=output_dir,
        no_cad=args.no_cad,
        driver_factory=None if args.no_cad else _default_driver_factory,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] in {"pass", "geometry_verified"} else 1


def _default_driver_factory() -> object:
    from core.cad_io.autocad_com import AutoCADComDriver

    return AutoCADComDriver(connect_existing_only=True)


if __name__ == "__main__":
    raise SystemExit(main())
