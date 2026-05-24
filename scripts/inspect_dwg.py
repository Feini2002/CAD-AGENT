#!/usr/bin/env python
"""Inspect a DWG after execution.

Future responsibilities:
- count new entities
- summarize layers
- report bounding boxes
- verify key dimensions against CAD_PLAN
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a DWG or active CAD document.")
    parser.add_argument("--dwg", type=Path, help="Optional DWG path.")
    args = parser.parse_args()

    print("inspect_dwg.py scaffold")
    print(f"- dwg: {args.dwg if args.dwg else 'active CAD document'}")
    print("- status: inspection is not implemented yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

