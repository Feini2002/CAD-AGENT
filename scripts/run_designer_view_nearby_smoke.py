#!/usr/bin/env python
"""Smoke test designer-view nearby placement in CODEX_PREVIEW."""

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

from core.placement.designer_view_nearby import PREVIEW_LAYER, run_nearby_preview_trial
from core.verification.fake_cad_driver import FakeCadDriver


def _output_dir(root: Path) -> Path:
    return root / "output" / "validation_runs" / "designer-view-nearby-placement"


def _fake_driver() -> tuple[Any, list[str]]:
    driver = FakeCadDriver()
    driver.current_viewport_bbox = {"min": [0, 0], "max": [6000, 3600]}
    anchor = driver.draw_rectangle(
        corner1=[600, 900, 0],
        corner2=[2600, 1700, 0],
        layer=PREVIEW_LAYER,
    )
    return driver, [str(handle) for handle in anchor.get("handles", [])]


def _real_driver() -> tuple[Any, list[str]]:
    from core.cad_io.autocad_com import AutoCADComDriver

    driver = AutoCADComDriver(connect_existing_only=True)
    viewport = driver.get_current_viewport_bbox()
    width = float(viewport["max"][0]) - float(viewport["min"][0])
    height = float(viewport["max"][1]) - float(viewport["min"][1])
    anchor_width = max(800.0, min(width * 0.22, 1800.0))
    anchor_depth = max(400.0, min(height * 0.18, 900.0))
    x0 = float(viewport["min"][0]) + width * 0.12
    y0 = float(viewport["min"][1]) + height * 0.35
    anchor = driver.draw_rectangle(
        corner1=[x0, y0, 0],
        corner2=[x0 + anchor_width, y0 + anchor_depth, 0],
        layer=PREVIEW_LAYER,
    )
    return driver, [str(handle) for handle in anchor.get("handles", [])]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run designer-view nearby placement smoke.")
    parser.add_argument("--no-cad", action="store_true", help="Use FakeCadDriver instead of active AutoCAD.")
    parser.add_argument("--phrase", default="在旁边画个测试矩形", help="Nearby phrase to resolve.")
    parser.add_argument("--width", type=float, default=900.0, help="Test object width in mm.")
    parser.add_argument("--depth", type=float, default=500.0, help="Test object depth in mm.")
    parser.add_argument("--output-dir", type=Path, default=_output_dir(PROJECT_ROOT))
    args = parser.parse_args()

    try:
        driver, anchor_handles = _fake_driver() if args.no_cad else _real_driver()
        report = run_nearby_preview_trial(
            driver,
            phrase=args.phrase,
            object_type="designer_view_nearby_smoke",
            object_name="旁边烟测",
            width=args.width,
            depth=args.depth,
            output_dir=args.output_dir,
            recent_created_handles=anchor_handles,
        )
    except Exception as exc:
        report = {
            "status": "blocked",
            "task": "designer_view_nearby_smoke",
            "blocked_reason": str(exc),
            "no_cad": args.no_cad,
            "safety": {
                "preview_layer_only": True,
                "saved_dwg": False,
                "deleted_entities": False,
                "modified_formal_layers": False,
            },
        }
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "nearby_preview_trial_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
