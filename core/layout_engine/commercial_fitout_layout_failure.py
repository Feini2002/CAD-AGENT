"""Commercial fitout micro-scene failure classification for non-CAD benchmarks."""

from __future__ import annotations

from typing import Any

from core.geometry_backends.rect2d import rect_intersects
from core.layout_engine.office_layout_failure import evaluate_composition_layout_failure


def _object_bbox(item: dict[str, Any]) -> dict[str, list[float]]:
    base = item["base_point"]
    size = item["size"]
    return {
        "min": [float(base[0]), float(base[1])],
        "max": [float(base[0]) + float(size["width"]), float(base[1]) + float(size["depth"])],
    }


def is_fitout_composition(composition: dict[str, Any]) -> bool:
    composition_id = str(composition.get("composition_id", ""))
    return composition.get("domain") == "commercial_fitout" or composition_id.startswith("fitout_")


def evaluate_main_aisle_conflict(composition: dict[str, Any]) -> dict[str, Any] | None:
    constraints = composition.get("layout_constraints")
    if not isinstance(constraints, dict):
        return None
    aisle = constraints.get("main_aisle")
    if not isinstance(aisle, dict):
        return None
    zone = {"min": [float(aisle["min"][0]), float(aisle["min"][1])], "max": [float(aisle["max"][0]), float(aisle["max"][1])]}
    blocked_reasons: list[str] = []
    for item in composition.get("objects", []):
        if not isinstance(item, dict):
            continue
        if rect_intersects(_object_bbox(item), zone):
            instance_id = str(item.get("instance_id", "object"))
            blocked_reasons.append(f"circulation_conflict: {instance_id} blocks main_aisle zone.")
    if not blocked_reasons:
        return None
    return {
        "status": "blocked",
        "failure_category": "circulation_conflict",
        "blocked_reasons": blocked_reasons,
    }


def evaluate_meeting_seating_conflict(composition: dict[str, Any]) -> dict[str, Any] | None:
    if str(composition.get("composition_id", "")) != "fitout_meeting_seating_conflict":
        return None
    objects = [item for item in composition.get("objects", []) if isinstance(item, dict)]
    table = next((item for item in objects if item.get("type") == "table"), None)
    chairs = [item for item in objects if item.get("type") == "chair"]
    if table is None or not chairs:
        return None
    table_bbox = _object_bbox(table)
    blocked_reasons: list[str] = []
    for chair in chairs:
        if rect_intersects(_object_bbox(chair), table_bbox):
            blocked_reasons.append(
                f"insufficient_space: {chair.get('instance_id')} overlaps meeting_table seating zone."
            )
    if not blocked_reasons:
        return None
    return {
        "status": "blocked",
        "failure_category": "insufficient_space",
        "blocked_reasons": blocked_reasons,
    }


def evaluate_fitout_composition_layout_failure(composition: dict[str, Any]) -> dict[str, Any] | None:
    """Return blocked payload for fitout micro-scenes; delegates office clearance rules when needed."""

    if not is_fitout_composition(composition):
        return evaluate_composition_layout_failure(composition)

    for evaluator in (evaluate_main_aisle_conflict, evaluate_meeting_seating_conflict):
        result = evaluator(composition)
        if result is not None:
            return result
    return evaluate_composition_layout_failure(composition)
