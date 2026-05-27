#!/usr/bin/env python3
"""Run per-row commercial_fitout catalog CAD smoke (V-PROOF-21 extension)."""

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
from core.verification.fitout_catalog_cad_smoke import run_fitout_catalog_cad_smoke


def main() -> int:
    parser = argparse.ArgumentParser(description="CAD smoke for each commercial_fitout catalog registry row.")
    parser.add_argument("--no-cad", action="store_true")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--catalog-object-id", action="append", dest="catalog_object_ids", default=None)
    parser.add_argument("--start-x", type=float, default=90000)
    parser.add_argument("--start-y", type=float, default=52000)
    args = parser.parse_args()

    output_dir = resolve_under_project_output(PROJECT_ROOT, args.output_dir, label="output_dir")
    driver = None
    if not args.no_cad:
        from core.cad_io.autocad_com import AutoCADComDriver

        driver = AutoCADComDriver(connect_existing_only=True)

    report = run_fitout_catalog_cad_smoke(
        root=PROJECT_ROOT,
        output_dir=output_dir,
        no_cad=args.no_cad,
        driver=driver,
        base_offset=[args.start_x, args.start_y, 0],
        catalog_object_ids=args.catalog_object_ids,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") in {"pass", "geometry_verified"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
