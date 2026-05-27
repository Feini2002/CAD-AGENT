#!/usr/bin/env python3
"""Run intent_lab CAD suite (V-PROOF-14 / V-PROOF-15)."""

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
from core.verification.intent_lab_cad import run_intent_lab_cad_suite


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and optionally execute intent_lab CAD_PLAN fixtures.")
    parser.add_argument("--no-cad", action="store_true")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    driver_factory = None
    if not args.no_cad:
        from core.cad_io.autocad_com import AutoCADComDriver

        def driver_factory() -> AutoCADComDriver:
            return AutoCADComDriver(connect_existing_only=True)

    output_dir = resolve_under_project_output(PROJECT_ROOT, args.output_dir, label="output_dir")
    report = run_intent_lab_cad_suite(
        root=PROJECT_ROOT,
        output_dir=output_dir,
        no_cad=args.no_cad,
        driver_factory=driver_factory,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report.get("status") in {"pass", "geometry_verified", "deferred"}:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
