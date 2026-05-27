#!/usr/bin/env python3
"""Run RBLOCK-07 block matrix registry sync (no CAD)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT
except ImportError:
    from scripts._bootstrap import PROJECT_ROOT

ROOT = PROJECT_ROOT

from core.block_engine.block_matrix_registry import (
    assert_block_matrix_registry_contract,
    run_block_matrix_registry_no_cad_sync,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="RBLOCK-07 block matrix registry sync")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "output" / "validation_runs" / "rblock-07-block-matrix-registry-no-cad",
    )
    parser.add_argument("--apply", action="store_true", help="Write registry JSON (default dry-run binding only)")
    args = parser.parse_args()

    assert_block_matrix_registry_contract(project_root=ROOT)
    summary = run_block_matrix_registry_no_cad_sync(
        project_root=ROOT,
        output_dir=args.output,
        dry_run=not args.apply,
    )
    summary_path = args.output / "block_matrix_registry_sync_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(summary_path)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
