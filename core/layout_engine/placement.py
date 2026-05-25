"""Place generic objects inside function zones using conservative bbox checks."""

from __future__ import annotations

from typing import Any

from core.block_engine.block_selector import select_block_candidate
from core.geometry_backends.rect2d import expand_rect, rect_contains, rect_intersects
from core.object_engine.parametric_objects import create_object_spec


def _zone_geometry(zone: dict[str, Any]) -> dict[str, list[float | int]]:
    geometry = zone.get("geometry", zone.get("boundary"))
    if not isinstance(geometry, dict):
        raise ValueError("zone geometry is required.")
    return geometry


def _size_from_source(source_result: dict[str, Any], object_type: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if source_result.get("status") == "selected" and source_result.get("selected_block"):
        block = source_result["selected_block"]
        size = block["size"]
        return (
            {"width": size["width"], "depth": size["depth"]},
            {"type": "block", "block_id": block["block_id"], "block": block},
        )
    spec = source_result.get("fallback_object_spec") or create_object_spec(object_type)
    size = spec["size"]
    return (
        {"width": size["width"], "depth": size["depth"]},
        {"type": "object_spec_fallback", "object_spec": spec},
    )


def _failure_reasons(
    *,
    bbox: dict[str, list[float | int]],
    zone_geometry: dict[str, list[float | int]],
    path_surfaces: list[dict[str, Any]],
    fixed_obstacles: list[dict[str, Any]],
    existing_bboxes: list[dict[str, list[float | int]]],
) -> list[str]:
    reasons: list[str] = []
    if not rect_contains(zone_geometry, bbox):
        reasons.append("bbox exceeds zone geometry.")
    if any(rect_intersects(bbox, surface) for surface in path_surfaces):
        reasons.append("bbox overlaps path_surface.")
    for obstacle in fixed_obstacles:
        obstacle_id = obstacle.get("obstacle_id", obstacle.get("id", "unknown"))
        if isinstance(obstacle.get("bbox"), dict) and rect_intersects(bbox, obstacle["bbox"]):
            reasons.append(f"bbox overlaps fixed_obstacle:{obstacle_id}.")
    if any(rect_intersects(bbox, existing) for existing in existing_bboxes):
        reasons.append("bbox overlaps another placement.")
    return reasons


def create_zone_placements(
    zones: list[dict[str, Any]],
    *,
    object_types: list[str],
    block_library: dict[str, Any] | None = None,
    preferences: dict[str, Any] | None = None,
    path_surfaces: list[dict[str, Any]] | None = None,
    fixed_obstacles: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Create conservative object placements driven by zone geometry and object size."""

    preferences = preferences or {}
    path_surfaces = path_surfaces or []
    fixed_obstacles = fixed_obstacles or []
    clearance = float(preferences.get("clearance_mm", 100))
    spacing = float(preferences.get("placement_spacing_mm", 300))
    placements: list[dict[str, Any]] = []
    placed_bboxes: list[dict[str, list[float | int]]] = []

    for zone in zones:
        geometry = _zone_geometry(zone)
        cursor_x = float(geometry["min"][0])
        base_y = float(geometry["min"][1])
        for object_type in object_types:
            remaining_width = float(geometry["max"][0]) - cursor_x
            remaining_depth = float(geometry["max"][1]) - base_y
            preflight_reasons: list[str] = []
            if remaining_width <= 0 or remaining_depth <= 0:
                preflight_reasons.append("insufficient remaining zone space for placement.")
                source_result = {"status": "fallback", "fallback_object_spec": create_object_spec(object_type)}
            elif block_library is not None:
                source_result = select_block_candidate(
                    block_library,
                    category=object_type,
                    domain=preferences.get("domain"),
                    tags=preferences.get("tags", []),
                    max_width=remaining_width,
                    max_depth=remaining_depth,
                )
            else:
                source_result = {"status": "fallback", "fallback_object_spec": create_object_spec(object_type)}
            size, source = _size_from_source(source_result, object_type)
            bbox = {
                "min": [cursor_x, base_y],
                "max": [cursor_x + float(size["width"]), base_y + float(size["depth"])],
            }
            reasons = _failure_reasons(
                bbox=bbox,
                zone_geometry=geometry,
                path_surfaces=path_surfaces,
                fixed_obstacles=fixed_obstacles,
                existing_bboxes=placed_bboxes,
            )
            reasons = preflight_reasons + reasons
            status = "blocked" if reasons else "placed"
            placement = {
                "object_id": f"placement-{zone['zone_id']}-{object_type}",
                "object_type": object_type,
                "zone_id": zone["zone_id"],
                "status": status,
                "base_point": [cursor_x, base_y, 0],
                "rotation": 0,
                "bbox": bbox,
                "clearance_bbox": expand_rect(bbox, clearance),
                "source": source,
                "failure_reasons": reasons,
            }
            placements.append(placement)
            if status == "placed":
                placed_bboxes.append(bbox)
                cursor_x = bbox["max"][0] + spacing
    return placements
