"""Create first-pass reusable parametric CAD object specs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.object_engine.object_to_plan import object_to_plan


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OBJECTS_PATH = PROJECT_ROOT / "libraries" / "objects" / "object_defaults.json"


def load_object_defaults(path: Path = DEFAULT_OBJECTS_PATH) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    objects = data.get("objects") if isinstance(data, dict) else None
    if not isinstance(objects, dict):
        raise ValueError("object_defaults.json must contain an objects map.")
    return objects


DEFAULT_OBJECTS = load_object_defaults()


def create_object_spec(
    object_type: str,
    *,
    name: str | None = None,
    width: float | int | None = None,
    depth: float | int | None = None,
    height: float | int | None = None,
    style_profile_id: str | None = None,
) -> dict[str, Any]:
    if object_type not in DEFAULT_OBJECTS:
        raise ValueError(f"Unsupported object type: {object_type}")

    defaults = DEFAULT_OBJECTS[object_type]
    resolved_width = width if width is not None else defaults["width"]
    resolved_depth = depth if depth is not None else defaults["depth"]
    resolved_height = height if height is not None else defaults["height"]
    for key, value in [("width", resolved_width), ("depth", resolved_depth), ("height", resolved_height)]:
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"{key} must be a positive number.")

    components = [dict(component) for component in defaults.get("components", [])]
    if not components:
        components = [{"component_id": f"{object_type}-body", "role": "body", "count": 1}]

    spec: dict[str, Any] = {
        "version": "0.1",
        "object_id": f"object-{object_type}-{int(resolved_width)}x{int(resolved_depth)}",
        "type": object_type,
        "name": name or str(defaults["name"]),
        "style_profile_id": style_profile_id or "style-modern",
        "size": {
            "width": resolved_width,
            "depth": resolved_depth,
            "height": resolved_height,
        },
        "components": components,
        "placement_requirements": ["base point is lower-left plan corner"],
        "drawing_intent": "plan_preview",
    }
    if defaults.get("placement_role"):
        spec["placement_role"] = defaults["placement_role"]
    clearance_refs = defaults.get("clearance_refs")
    if isinstance(clearance_refs, list) and clearance_refs:
        spec["clearance_refs"] = [dict(ref) if isinstance(ref, dict) else ref for ref in clearance_refs]
    assertion_hints = defaults.get("assertion_hints")
    if isinstance(assertion_hints, list) and assertion_hints:
        spec["assertion_hints"] = list(assertion_hints)
    return spec


def apply_style_to_object_spec(spec: dict[str, Any], style_profile: dict[str, Any]) -> dict[str, Any]:
    styled = {
        **spec,
        "style_profile_id": style_profile.get("style_id", spec.get("style_profile_id", "style-modern")),
        "components": [dict(component) for component in spec.get("components", [])],
    }
    tokens = style_profile.get("tokens", {}) if isinstance(style_profile.get("tokens"), dict) else {}
    detail_level = tokens.get("detail_level")
    object_type = spec.get("type")
    if object_type == "cabinet":
        if detail_level == "high":
            styled["components"].append({"component_id": "cabinet-ornamental-rails", "role": "ornament", "count": 2})
        elif detail_level == "low":
            styled["components"] = [
                component for component in styled["components"] if component.get("role") != "front_panel"
            ]
            styled["components"].append(
                {"component_id": "cabinet-minimal-front", "role": "simplified_panel", "count": 1}
            )
        elif detail_level == "medium":
            styled["components"].append({"component_id": "cabinet-flat-front-lines", "role": "panel_line", "count": 2})
    if tokens.get("label_policy") == "object_and_size":
        styled["placement_requirements"] = list(spec.get("placement_requirements", [])) + [
            "label should include object name and primary size"
        ]
    elif tokens.get("label_policy") == "none":
        styled["placement_requirements"] = list(spec.get("placement_requirements", [])) + [
            "omit preview label unless explicitly requested"
        ]
    return styled


def object_spec_to_cad_plan(
    spec: dict[str, Any],
    *,
    base_point: list[float | int] | None = None,
    domain: str = "generic",
    layer: str = "CODEX_PREVIEW",
    include_dimensions: bool = True,
    include_label: bool = True,
) -> dict[str, Any]:
    return object_to_plan(
        spec,
        base_point=base_point,
        domain=domain,
        layer=layer,
        include_dimensions=include_dimensions,
        include_label=include_label,
    )
