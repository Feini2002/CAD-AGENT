"""Convert OBJECT_SPEC dictionaries into safe preview CAD_PLAN dictionaries."""

from __future__ import annotations

from typing import Any


def object_to_plan(
    spec: dict[str, Any],
    *,
    base_point: list[float | int] | None = None,
    domain: str = "generic",
    layer: str = "CODEX_PREVIEW",
    include_dimensions: bool = True,
    include_label: bool = True,
) -> dict[str, Any]:
    size = spec["size"]
    return {
        "version": "0.1",
        "domain": domain,
        "intent": "draw_object",
        "object": {
            "type": spec["type"],
            "name": spec["name"],
            "width": size["width"],
            "depth": size["depth"],
            "height": size["height"],
            "object_spec_id": spec["object_id"],
        },
        "placement": {
            "mode": "absolute",
            "base_point": base_point or [0, 0, 0],
        },
        "drawing": {
            "layer": layer,
            "include_label": include_label,
            "include_dimensions": include_dimensions,
        },
        "confidence": 0.9,
        "needs_confirmation": False,
    }
