#!/usr/bin/env python3
"""Run RCAD-06 controlled hatch CAD smoke."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.verification.hatch_cad_smoke import run_hatch_cad_smoke  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run controlled hatch CAD smoke.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--no-cad", action="store_true")
    args = parser.parse_args()

    report = run_hatch_cad_smoke(output_dir=args.output_dir, no_cad=args.no_cad)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "geometry_verified" or args.no_cad else 1


if __name__ == "__main__":
    sys.exit(main())
