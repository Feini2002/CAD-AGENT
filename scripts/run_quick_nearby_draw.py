#!/usr/bin/env python
"""Run a fast current-view nearby draw quick trial."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.quick_tasks.nearby_draw import run_quick_nearby_draw
from core.verification.fake_cad_driver import FakeCadDriver


def _fake_driver() -> Any:
    driver = FakeCadDriver()
    driver.current_viewport_bbox = {"min": [0, 0], "max": [5000, 3000]}
    anchor = driver.draw_rectangle(
        corner1=[500, 800, 0],
        corner2=[1500, 1400, 0],
        layer="CODEX_PREVIEW",
    )
    driver.selected_handles = [str(handle) for handle in anchor.get("handles", [])]
    return driver


def _real_driver() -> Any:
    from core.cad_io.autocad_com import AutoCADComDriver

    return AutoCADComDriver(connect_existing_only=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fast CODEX_PREVIEW nearby draw from the current CAD viewport.")
    parser.add_argument("--phrase", default="在旁边画个沙发", help="Nearby phrase to resolve from the current CAD view.")
    parser.add_argument("--object-type", default="sofa", help="Object type, e.g. sofa, rect.")
    parser.add_argument("--object-name", help="Optional object name for the report.")
    parser.add_argument("--width", type=float, help="Override object width in mm.")
    parser.add_argument("--depth", type=float, help="Override object depth in mm.")
    parser.add_argument("--recent-handle", action="append", default=[], help="Recent created handle to prefer as focus.")
    parser.add_argument("--visual-source", help="Optional visual source, e.g. user_screenshot or current_cad_view.")
    parser.add_argument("--visual-target-hint", help="Optional visual target hint such as marked_region or current_focus.")
    parser.add_argument("--output-dir", type=Path, help="Optional report directory.")
    parser.add_argument("--no-cad", action="store_true", help="Use a fake driver smoke fixture instead of AutoCAD.")
    args = parser.parse_args()

    try:
        driver = _fake_driver() if args.no_cad else _real_driver()
        report = run_quick_nearby_draw(
            driver,
            phrase=args.phrase,
            object_type=args.object_type,
            object_name=args.object_name,
            width=args.width,
            depth=args.depth,
            recent_created_handles=[str(handle) for handle in args.recent_handle],
            visual_context=_visual_context_from_args(args),
            output_dir=args.output_dir,
        )
    except Exception as exc:
        report = {
            "status": "blocked",
            "mode": "quick_trial",
            "task": "quick_nearby_draw",
            "blocked_reason": str(exc),
            "safety": {
                "preview_layer_only": True,
                "saved_dwg": False,
                "deleted_entities": False,
                "modified_formal_layers": False,
            },
        }
        if args.output_dir is not None:
            args.output_dir.mkdir(parents=True, exist_ok=True)
            (args.output_dir / "quick_nearby_draw_report.json").write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "pass" else 1


def _visual_context_from_args(args: argparse.Namespace) -> dict[str, str] | None:
    if not args.visual_source and not args.visual_target_hint:
        return None
    context: dict[str, str] = {}
    if args.visual_source:
        context["source"] = args.visual_source
    if args.visual_target_hint:
        context["target_hint"] = args.visual_target_hint
    return context


if __name__ == "__main__":
    raise SystemExit(main())
