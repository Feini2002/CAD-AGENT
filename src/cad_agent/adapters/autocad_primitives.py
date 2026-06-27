from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from cad_agent.domain.primitives import Primitive


PREVIEW_LAYER = "CODEX_PREVIEW"

AUTOCAD_PRIMITIVE_MAP: dict[str, tuple[str, str]] = {
    "line": ("draw_line", "LINE"),
    "rectangle": ("draw_polyline", "LWPOLYLINE"),
    "polyline": ("draw_polyline", "LWPOLYLINE"),
    "circle": ("draw_circle", "CIRCLE"),
    "arc": ("draw_arc", "ARC"),
    "text": ("draw_text", "TEXT"),
    "ellipse": ("draw_polyline", "LWPOLYLINE"),
}


@dataclass(frozen=True)
class AutoCadPrimitiveCall:
    primitive_id: str
    semantic_object_id: str
    method: str
    kwargs: dict[str, Any]
    expected_entity_type: str


def primitive_to_autocad_call(primitive: Primitive) -> AutoCadPrimitiveCall:
    if primitive.layer != PREVIEW_LAYER:
        raise ValueError(f"AutoCAD backend only writes {PREVIEW_LAYER}.")

    if primitive.primitive_type == "line":
        method, expected = AUTOCAD_PRIMITIVE_MAP["line"]
        kwargs = {
            "start_point": _point3(_required(primitive.geometry, "start", fallback_key="start_point")),
            "end_point": _point3(_required(primitive.geometry, "end", fallback_key="end_point")),
        }
    elif primitive.primitive_type == "rectangle":
        method, expected = AUTOCAD_PRIMITIVE_MAP["rectangle"]
        kwargs = {"points": _rectangle_points(primitive.geometry), "closed": True}
    elif primitive.primitive_type == "polyline":
        method, expected = AUTOCAD_PRIMITIVE_MAP["polyline"]
        kwargs = {
            "points": [_point3(point) for point in _required(primitive.geometry, "points")],
            "closed": bool(primitive.geometry.get("closed", False)),
        }
    elif primitive.primitive_type == "circle":
        method, expected = AUTOCAD_PRIMITIVE_MAP["circle"]
        kwargs = {
            "center": _point3(_required(primitive.geometry, "center")),
            "radius": _positive_float(_required(primitive.geometry, "radius"), key="radius"),
        }
    elif primitive.primitive_type == "arc":
        method, expected = AUTOCAD_PRIMITIVE_MAP["arc"]
        kwargs = {
            "center": _point3(_required(primitive.geometry, "center")),
            "radius": _positive_float(_required(primitive.geometry, "radius"), key="radius"),
            "start_angle": _float(_required(primitive.geometry, "start_angle"), key="start_angle"),
            "end_angle": _float(_required(primitive.geometry, "end_angle"), key="end_angle"),
        }
    elif primitive.primitive_type == "text":
        method, expected = AUTOCAD_PRIMITIVE_MAP["text"]
        kwargs = {
            "text": str(_required(primitive.geometry, "text")),
            "position": _point3(_required(primitive.geometry, "position")),
            "height": _positive_float(primitive.geometry.get("height", primitive.geometry.get("text_height", 12.0)), key="height"),
        }
    elif primitive.primitive_type == "ellipse":
        method, expected = AUTOCAD_PRIMITIVE_MAP["ellipse"]
        kwargs = {
            "points": _ellipse_points(primitive.geometry),
            "closed": True,
        }
    else:
        raise ValueError(f"Unsupported primitive type: {primitive.primitive_type}")

    kwargs["layer"] = PREVIEW_LAYER
    kwargs["layer_role"] = "preview"
    return AutoCadPrimitiveCall(
        primitive_id=primitive.primitive_id,
        semantic_object_id=primitive.semantic_object_id,
        method=method,
        kwargs=kwargs,
        expected_entity_type=expected,
    )


def _required(geometry: dict[str, Any], key: str, *, fallback_key: str | None = None) -> Any:
    if key in geometry:
        return geometry[key]
    if fallback_key and fallback_key in geometry:
        return geometry[fallback_key]
    raise ValueError(f"Missing primitive geometry key: {key}")


def _point3(value: Any) -> list[float]:
    if not isinstance(value, (list, tuple)) or len(value) < 2:
        raise ValueError("Expected a 2D or 3D point.")
    z = value[2] if len(value) > 2 else 0.0
    return [_float(value[0], key="x"), _float(value[1], key="y"), _float(z, key="z")]


def _float(value: Any, *, key: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Primitive geometry key {key!r} must be numeric.") from exc
    if not math.isfinite(result):
        raise ValueError(f"Primitive geometry key {key!r} must be finite.")
    return result


def _positive_float(value: Any, *, key: str) -> float:
    result = _float(value, key=key)
    if result <= 0:
        raise ValueError(f"Primitive geometry key {key!r} must be positive.")
    return result


def _rectangle_points(geometry: dict[str, Any]) -> list[list[float]]:
    if "points" in geometry:
        points = [_point3(point) for point in geometry["points"]]
        if len(points) != 4:
            raise ValueError("Rectangle points geometry must contain exactly 4 points.")
        return points

    if "corner1" in geometry and "corner2" in geometry:
        x1, y1, z1 = _point3(geometry["corner1"])
        x2, y2, _z2 = _point3(geometry["corner2"])
        return [[x1, y1, z1], [x2, y1, z1], [x2, y2, z1], [x1, y2, z1]]

    origin = _point3(_required(geometry, "origin"))
    width = _positive_float(_required(geometry, "width"), key="width")
    depth = _positive_float(_required(geometry, "depth"), key="depth")
    x, y, z = origin
    return [[x, y, z], [x + width, y, z], [x + width, y + depth, z], [x, y + depth, z]]


def _ellipse_points(geometry: dict[str, Any]) -> list[list[float]]:
    center = _point3(_required(geometry, "center"))
    radius_x = _positive_float(
        geometry.get("radius_x", geometry.get("rx", geometry.get("major_radius"))),
        key="radius_x",
    )
    radius_y = _positive_float(
        geometry.get("radius_y", geometry.get("ry", geometry.get("minor_radius"))),
        key="radius_y",
    )
    segments = int(geometry.get("segments", 24))
    if segments < 8:
        raise ValueError("Ellipse polyline approximation needs at least 8 segments.")
    cx, cy, cz = center
    return [
        [cx + math.cos((math.tau * index) / segments) * radius_x, cy + math.sin((math.tau * index) / segments) * radius_y, cz]
        for index in range(segments)
    ]
