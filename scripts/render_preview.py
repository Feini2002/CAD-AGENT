#!/usr/bin/env python
"""Render or capture a preview after CAD execution.

Future responsibilities:
- capture CAD window or exported preview
- save image into output/previews
- optionally compare with expected screenshots
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a CAD preview.")
    parser.add_argument("--output", type=Path, default=Path("output/previews/preview.png"))
    args = parser.parse_args()

    print("render_preview.py scaffold")
    print(f"- output: {args.output}")
    print("- status: rendering is not implemented yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

