#!/usr/bin/env python3
"""Emit geometry feature candidates (BETA-DRAWING-READ-02)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.drawing_analysis.geometry_candidates import read_geometry_candidates_from_fixture  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract wall/door/column/no-place candidates from fixture.")
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path("examples/drawing_read/sample_geometry_feature_fixture.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/test_artifacts/drawing_read/beta_drawing_read_02/candidates.json"),
    )
    args = parser.parse_args()

    try:
        candidates = read_geometry_candidates_from_fixture(args.fixture.resolve())
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(candidates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(candidates, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
