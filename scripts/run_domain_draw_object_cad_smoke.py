#!/usr/bin/env python3
"""Run per-domain draw_object CAD smoke (coverage wave)."""

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
from core.verification.domain_draw_object_cad_smoke import run_domain_draw_object_cad_smoke


def main() -> int:
    parser = argparse.ArgumentParser(description="Domain draw_object CAD smoke on CODEX_PREVIEW.")
    parser.add_argument("--no-cad", action="store_true")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--start-x", type=float, default=88000)
    parser.add_argument("--start-y", type=float, default=52000)
    args = parser.parse_args()

    output_dir = resolve_under_project_output(PROJECT_ROOT, args.output_dir, label="output_dir")
    driver = None
    if not args.no_cad:
        from core.cad_io.autocad_com import AutoCADComDriver

        driver = AutoCADComDriver(connect_existing_only=True)

    report = run_domain_draw_object_cad_smoke(
        root=PROJECT_ROOT,
        output_dir=output_dir,
        no_cad=args.no_cad,
        driver=driver,
        base_offset=[args.start_x, args.start_y, 0],
    )
    report_path = output_dir / "domain_draw_object_cad_smoke_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**report, "report_path": str(report_path)}, ensure_ascii=False, indent=2))
    return 0 if report.get("geometry_verified") else 1


if __name__ == "__main__":
    raise SystemExit(main())
