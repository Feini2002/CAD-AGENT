#!/usr/bin/env python
"""Run primitive capability matrix via cad_capability_probe."""

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
from core.verification.primitive_matrix import run_primitive_matrix


def main() -> int:
    parser = argparse.ArgumentParser(description="Run primitive matrix for LCAD regression.")
    parser.add_argument("--no-cad", action="store_true", help="Use fake driver only.")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    output_dir = resolve_under_project_output(root, args.output_dir, label="output_dir")
    report = run_primitive_matrix(
        output_dir=output_dir,
        no_cad=args.no_cad,
        driver_factory=None if args.no_cad else _default_driver_factory,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "pass" else 1


def _default_driver_factory() -> object:
    from core.cad_io.autocad_com import AutoCADComDriver

    return AutoCADComDriver(connect_existing_only=True)


if __name__ == "__main__":
    raise SystemExit(main())
