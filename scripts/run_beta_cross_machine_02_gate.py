#!/usr/bin/env python3
"""BETA-CROSS-MACHINE-02: P0 migration re-verify gate (no-CAD + optional real CAD)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.verification.cross_machine_reverify import run_beta_cross_machine_02_gate  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run BETA-CROSS-MACHINE-02 migration re-verify gate.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "output" / "validation_runs" / "beta-cross-machine-02-20260528",
    )
    parser.add_argument("--no-cad", action="store_true", help="Skip real CAD user_gate steps.")
    parser.add_argument("--skip-unittest", action="store_true", help="Skip unittest inside core platform gate.")
    args = parser.parse_args()

    report = run_beta_cross_machine_02_gate(
        project_root=PROJECT_ROOT,
        output_dir=args.output_dir.resolve(),
        include_real_cad=not args.no_cad,
        skip_unittest=args.skip_unittest,
    )
    print(json.dumps({"status": report.get("status"), "output_dir": str(args.output_dir)}, ensure_ascii=False, indent=2))
    status = str(report.get("status", "blocked"))
    user_gate = str(report.get("user_gate", {}).get("status", "pending"))
    if status == "pass":
        return 0 if user_gate == "acknowledged" else 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
