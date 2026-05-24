#!/usr/bin/env python
"""Execute a CAD_PLAN in a safe preview-first way."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Protocol

try:
    from core.plan_engine.validate_plan import load_json, validate_plan
except ImportError:  # pragma: no cover - compatibility for direct execution.
    from scripts.validate_plan import load_json, validate_plan


PREVIEW_LAYER = "CODEX_PREVIEW"


class CadPreviewDriver(Protocol):
    def draw_rectangle(self, **kwargs: object) -> None:
        ...

    def draw_text(self, **kwargs: object) -> None:
        ...

    def add_dimension(self, **kwargs: object) -> None:
        ...


def point3(values: list[Any]) -> list[float | int]:
    if len(values) == 2:
        return [values[0], values[1], 0]
    return [values[0], values[1], values[2]]


def execute_plan_file(
    plan_path: Path,
    *,
    driver: CadPreviewDriver,
    preview_only: bool = True,
) -> dict[str, object]:
    plan = load_json(plan_path)
    errors = validate_plan(plan)
    if errors:
        raise ValueError("Invalid CAD_PLAN: " + "; ".join(errors))

    if plan["intent"] != "draw_object":
        raise ValueError("execute_plan.py currently supports intent=draw_object only.")

    obj = plan["object"]
    placement = plan["placement"]
    drawing = plan["drawing"]

    if placement.get("mode") != "absolute":
        raise ValueError("execute_plan.py currently supports absolute placement only.")

    layer = drawing["layer"]
    if preview_only and layer != PREVIEW_LAYER:
        raise ValueError(f"Preview execution only allows layer={PREVIEW_LAYER}.")

    width = obj.get("width")
    depth = obj.get("depth")
    if not isinstance(width, (int, float)) or not isinstance(depth, (int, float)):
        raise ValueError("object.width and object.depth are required for preview drawing.")

    base = point3(placement["base_point"])
    x0, y0, z0 = base
    corner2 = [x0 + width, y0 + depth, z0]
    color = "yellow"

    driver.draw_rectangle(
        corner1=base,
        corner2=corner2,
        layer=layer,
        color=color,
    )

    if drawing.get("include_label", False):
        label_height = max(80, min(width, depth) * 0.2)
        driver.draw_text(
            text=obj["name"],
            position=[x0 + width / 2, y0 + depth / 2, z0],
            height=label_height,
            layer=layer,
            color=color,
        )

    if drawing.get("include_dimensions", False):
        dimension_offset = max(120, min(width, depth) * 0.3)
        driver.add_dimension(
            start_point=base,
            end_point=[x0 + width, y0, z0],
            text_position=[x0 + width / 2, y0 - dimension_offset, z0],
            layer=layer,
            color=color,
        )
        driver.add_dimension(
            start_point=base,
            end_point=[x0, y0 + depth, z0],
            text_position=[x0 - dimension_offset, y0 + depth / 2, z0],
            layer=layer,
            color=color,
        )

    return {
        "status": "executed",
        "plan": str(plan_path),
        "intent": plan["intent"],
        "object_type": obj["type"],
        "object_name": obj["name"],
        "object_size": [width, depth],
        "base_point": base,
        "layer": layer,
        "preview_only": preview_only,
        "entities": {
            "rectangle": 1,
            "text": 1 if drawing.get("include_label", False) else 0,
            "dimensions": 2 if drawing.get("include_dimensions", False) else 0,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute a CAD_PLAN JSON file.")
    parser.add_argument("plan", type=Path, help="Path to CAD_PLAN JSON.")
    parser.add_argument(
        "--allow-formal-layer",
        action="store_true",
        help="Allow drawing to a non-preview layer. Use only with explicit user approval.",
    )
    args = parser.parse_args()

    try:
        from core.cad_io.autocad_com import AutoCADComDriver
    except ImportError:  # pragma: no cover - compatibility with legacy layout.
        from drivers.autocad_com import AutoCADComDriver

    result = execute_plan_file(
        args.plan,
        driver=AutoCADComDriver(),
        preview_only=not args.allow_formal_layer,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
