#!/usr/bin/env python
"""Run RCAD-25 block-first real-CAD smoke evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT

from core.verification.symbol_block_first_cad_smoke import run_symbol_block_first_cad_smoke


def main() -> int:
    parser = argparse.ArgumentParser(description="Run RCAD-25 SYMBOL-09 block-first CAD smoke.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--no-cad", action="store_true", help="Emit deferred evidence without connecting to CAD.")
    args = parser.parse_args()

    try:
        report = run_symbol_block_first_cad_smoke(
            root=args.root,
            output_dir=args.output_dir,
            plan_path=args.plan,
            no_cad=args.no_cad,
        )
    except RuntimeError as exc:
        blocker = {
            "version": "0.1",
            "package_id": "RCAD-25-SYMBOL-BLOCK-FIRST",
            "status": "external_blocker",
            "message": str(exc),
            "evidence_state": "deferred_cad_readback_required",
            "geometry_accuracy": "not_verified_without_cad_readback",
            "screenshot_role": "not_applicable",
        }
        print(json.dumps(blocker, ensure_ascii=False, indent=2))
        return 2

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report.get("status") == "geometry_verified":
        return 0
    if report.get("status") == "deferred":
        return 0 if args.no_cad else 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
