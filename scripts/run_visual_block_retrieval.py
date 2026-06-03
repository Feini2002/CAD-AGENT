#!/usr/bin/env python3
"""Run visual-first retrieval for block references in the active AutoCAD DWG."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.cad_io.autocad_com import AutoCADComDriver  # noqa: E402
from core.visual_retrieval import retrieve_visual_blocks_from_driver  # noqa: E402


DEFAULT_OUTPUT = PROJECT_ROOT / "output" / "validation_runs" / "visual-cad-asset-retrieval" / "retrieval_report.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Find a CAD block using visual-first semantic retrieval.")
    parser.add_argument("--query", required=True, help="User request, for example: 根据截图找到三人沙发对应图块")
    parser.add_argument("--visual-hint", default="", help="Optional normalized visual hint, e.g. sofa three-seat plan view")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--inspect-top",
        type=int,
        default=0,
        help="Optionally inspect detailed block definitions for the top N candidates after visual-first ranking.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        driver = AutoCADComDriver(connect_existing_only=True)
        report = retrieve_visual_blocks_from_driver(
            driver,
            query=args.query,
            visual_hint=args.visual_hint or None,
            top_k=args.top_k,
            inspect_top=args.inspect_top,
        ).to_dict()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report.get("status") == "pass" else 1
    except Exception as exc:
        payload = {
            "status": "blocked",
            "failure_category": "visual_block_retrieval_failed",
            "message": str(exc),
            "output": str(args.output),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
