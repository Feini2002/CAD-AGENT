#!/usr/bin/env python
"""V-PROOF-51: bind RCAD-20 real CAD negative guard evidence into registry."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT

from core.verification.negative_plan_registry import run_vproof_51_negative_cad_sync


def main() -> int:
    parser = argparse.ArgumentParser(description="V-PROOF-51 negative real CAD registry sync.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "output" / "validation_runs" / "vproof-51-negative-cad",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Existing negative_cad_runner_report.json (defaults to RCAD-20 canonical path).",
    )
    parser.add_argument("--real-cad", action="store_true", help="Run negative runner in real AutoCAD session.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        summary = run_vproof_51_negative_cad_sync(
            project_root=args.root.resolve(),
            output_dir=args.output_dir.resolve(),
            report_path=args.report,
            run_real_cad=args.real_cad,
            dry_run=args.dry_run,
        )
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary.get("writeback_status") != "applied":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
