#!/usr/bin/env python3
"""Run RBLOCK-04 block insert matrix manifest (no-CAD)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.block_engine.block_matrix_manifest import (  # noqa: E402
    default_manifest_path,
    run_block_insert_matrix_manifest,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run block insert matrix manifest (RBLOCK-04).")
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("output/validation_runs/rblock-04-block-matrix-no-cad"),
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    manifest_path = args.manifest or default_manifest_path(root)
    result = run_block_insert_matrix_manifest(manifest_path, output_root=args.output_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
