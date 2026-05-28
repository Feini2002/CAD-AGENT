#!/usr/bin/env python
"""V-PROOF-72: run L1 capability lab and sync registry smoke rows."""

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

from core.verification.capability_lab import run_vproof_72_nightly_lab_sync


def main() -> int:
    parser = argparse.ArgumentParser(description="V-PROOF-72 nightly lab sync.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "output" / "validation_runs" / "vproof-72-nightly-lab",
    )
    parser.add_argument("--tier", default="L1", choices=["L0", "L1"])
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--lab-dry-run", action="store_true", help="Plan lab steps only.")
    parser.add_argument("--dry-run", action="store_true", help="Registry writeback dry-run.")
    args = parser.parse_args()

    try:
        summary = run_vproof_72_nightly_lab_sync(
            project_root=args.root.resolve(),
            output_dir=args.output_dir.resolve(),
            tier=args.tier,
            manifest_path=args.manifest,
            dry_run=args.dry_run,
            lab_dry_run=args.lab_dry_run,
        )
    except (AssertionError, FileNotFoundError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary.get("lab_status") != "pass":
        return 2
    if summary.get("writeback_rejected_count", 0) > 0:
        return 1
    if summary.get("writeback_applied_count", 0) < 1:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
