#!/usr/bin/env python3
"""Run demand-side benchmark cases with real CAD (V-PROOF-22)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.path_safety import resolve_under_project_output
from core.verification.demand_case_cad_smoke import run_demand_case_cad_smoke


def main() -> int:
    parser = argparse.ArgumentParser(description="Demand-side benchmark CAD smoke on CODEX_PREVIEW.")
    parser.add_argument("--no-cad", action="store_true")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--skip-benchmark", action="store_true")
    args = parser.parse_args()

    output_dir = resolve_under_project_output(PROJECT_ROOT, args.output_dir, label="output_dir")
    driver = None
    if not args.no_cad:
        from core.cad_io.autocad_com import AutoCADComDriver

        driver = AutoCADComDriver(connect_existing_only=True)

    report = run_demand_case_cad_smoke(
        root=PROJECT_ROOT,
        output_dir=output_dir,
        no_cad=args.no_cad,
        driver=driver,
        skip_benchmark=args.skip_benchmark,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("geometry_verified") else 1


if __name__ == "__main__":
    raise SystemExit(main())
