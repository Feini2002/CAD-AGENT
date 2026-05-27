#!/usr/bin/env python3
"""Run SYMBOL-09 block-first tier smoke manifest (non-CAD)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.symbol_engine.block_first_tier import (  # noqa: E402
    default_manifest_path,
    run_block_first_tier_smoke,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run block-first tier smoke (SYMBOL-09).")
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("output/validation_runs/symbol-09-block-first-no-cad"),
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    manifest_path = args.manifest or default_manifest_path(root)
    result = run_block_first_tier_smoke(manifest_path, output_root=args.output_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
