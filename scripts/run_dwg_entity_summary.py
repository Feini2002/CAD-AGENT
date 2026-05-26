#!/usr/bin/env python3
"""Emit read-only DWG entity summary (BETA-DRAWING-READ-01)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.drawing_analysis.dwg_read_only import (  # noqa: E402
    read_active_cad_entity_summary,
    read_entity_summary_from_fixture,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only ModelSpace entity summary.")
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path("examples/drawing_read/sample_modelspace_entities.json"),
        help="Use normalized entity fixture instead of live AutoCAD.",
    )
    parser.add_argument("--layer", default=None, help="Optional layer filter.")
    parser.add_argument("--output", type=Path, default=Path("output/test_artifacts/drawing_read/beta_drawing_read_01/summary.json"))
    parser.add_argument("--use-cad", action="store_true", help="Read from active AutoCAD instead of fixture.")
    args = parser.parse_args()

    try:
        if args.use_cad:
            summary = read_active_cad_entity_summary(layer=args.layer)
        else:
            summary = read_entity_summary_from_fixture(args.fixture.resolve())
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
