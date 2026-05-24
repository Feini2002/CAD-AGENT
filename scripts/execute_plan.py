#!/usr/bin/env python
"""Execute a CAD_PLAN.

The first real implementation should only support safe preview drawing for
simple rectangular objects. It should call the CAD driver layer instead of
putting AutoCAD COM details directly in this file.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute a CAD_PLAN JSON file.")
    parser.add_argument("plan", type=Path, help="Path to CAD_PLAN JSON.")
    parser.add_argument("--preview-only", action="store_true", default=True, help="Draw to preview layer only.")
    args = parser.parse_args()

    print("execute_plan.py scaffold")
    print(f"- plan: {args.plan}")
    print("- status: CAD execution is intentionally not implemented yet.")
    print("- next: validate plan, dry-run, then wire AutoCAD driver for CODEX_PREVIEW drawing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

