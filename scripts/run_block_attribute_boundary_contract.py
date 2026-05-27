#!/usr/bin/env python3
"""Run RBLOCK-06 block attribute probe boundary contract (no CAD)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT
except ImportError:
    from scripts._bootstrap import PROJECT_ROOT

ROOT = PROJECT_ROOT

from core.block_engine.block_attribute_boundary import (
    assert_block_attribute_boundary_contract,
    block_attribute_boundary_status_summary,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="RBLOCK-06 block attribute boundary contract")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "output" / "validation_runs" / "rblock-06-block-attribute-no-cad",
        help="Optional directory for summary JSON",
    )
    args = parser.parse_args()

    assert_block_attribute_boundary_contract(project_root=ROOT)
    summary = block_attribute_boundary_status_summary(project_root=ROOT)
    summary["status"] = "pass"

    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)
        out_path = args.output / "block_attribute_boundary_summary.json"
        out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(out_path)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
