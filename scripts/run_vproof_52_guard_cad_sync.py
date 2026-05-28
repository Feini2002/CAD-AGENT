#!/usr/bin/env python
"""V-PROOF-52: bind RCAD-21 guard full CAD strict chain into registry."""

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

from core.verification.guard_cad_registry import run_vproof_52_guard_cad_sync


def main() -> int:
    parser = argparse.ArgumentParser(description="V-PROOF-52 guard CAD registry sync.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "output" / "validation_runs" / "vproof-52-guard-cad",
    )
    parser.add_argument("--report", type=Path, help="Existing guard_full_cad_report.json")
    parser.add_argument("--real-cad", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        summary = run_vproof_52_guard_cad_sync(
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
    if summary.get("writeback_rejected_count", 0) > 0:
        return 1
    if summary.get("writeback_applied_count", 0) < 1:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
