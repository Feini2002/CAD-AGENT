"""Structured office layout failure classification for non-CAD benchmarks."""

from __future__ import annotations

from typing import Any

from core.geometry_backends.rect2d import rect_intersects


def _object_bbox(item: dict[str, Any]) -> dict[str, list[float]]:
    base = item["base_point"]
    size = item["size"]
    return {
        "min": [float(base[0]), float(base[1])],
        "max": [float(base[0]) + float(size["width"]), float(base[1]) + float(size["depth"])],
    }


def _find_object(composition: dict[str, Any], instance_id: str) -> dict[str, Any] | None:
    for item in composition.get("objects", []):
        if isinstance(item, dict) and item.get("instance_id") == instance_id:
            return item
    return None


def _entry_clearance_zone(ref: dict[str, Any]) -> dict[str, list[float]]:
    depth = float(ref.get("clear_depth_mm", 1200))
    width = float(ref.get("clear_width_mm", 1200))
    return {"min": [0.0, 0.0], "max": [width, depth]}


def _chair_pullback_zone(obj: dict[str, Any], ref: dict[str, Any]) -> dict[str, list[float]]:
    bbox = _object_bbox(obj)
    behind = float(ref.get("behind_depth_mm", 800))
    return {
        "min": [bbox["min"][0], bbox["min"][1] - behind],
        "max": [bbox["max"][0], bbox["min"][1]],
    }


def _cabinet_front_clearance_zone(obj: dict[str, Any], ref: dict[str, Any]) -> dict[str, list[float]]:
    bbox = _object_bbox(obj)
    front = float(ref.get("front_depth_mm", 800))
    return {
        "min": [bbox["min"][0], bbox["min"][1] - front],
        "max": [bbox["max"][0], bbox["min"][1]],
    }


def evaluate_composition_layout_failure(composition: dict[str, Any]) -> dict[str, Any] | None:
    """Return blocked payload when clearance semantics cannot be satisfied."""

    clearance_refs = composition.get("clearance_refs", [])
    if not isinstance(clearance_refs, list):
        return None
    objects = composition.get("objects", [])
    if not isinstance(objects, list):
        return None

    object_bboxes = [_object_bbox(item) for item in objects if isinstance(item, dict)]
    blocked_reasons: list[str] = []

    entry_refs = [ref for ref in clearance_refs if isinstance(ref, dict) and ref.get("role") == "entry_clearance"]
    for ref in entry_refs:
        zone = _entry_clearance_zone(ref)
        for index, bbox in enumerate(object_bboxes):
            if rect_intersects(bbox, zone):
                instance_id = objects[index].get("instance_id", f"object-{index}")
                blocked_reasons.append(
                    f"entry_clearance_conflict: {instance_id} overlaps entry clearance zone."
                )

    pullback_zones: list[dict[str, list[float]]] = []
    cabinet_front_zones: list[dict[str, list[float]]] = []
    for ref in clearance_refs:
        if not isinstance(ref, dict):
            continue
        bound_to = ref.get("bound_to")
        if not isinstance(bound_to, str):
            continue
        bound_object = _find_object(composition, bound_to)
        if bound_object is None:
            continue
        role = ref.get("role")
        if role == "chair_pullback_clearance":
            pullback_zones.append(_chair_pullback_zone(bound_object, ref))
        elif role == "cabinet_front_clearance":
            cabinet_front_zones.append(_cabinet_front_clearance_zone(bound_object, ref))

    for pullback in pullback_zones:
        for cabinet_front in cabinet_front_zones:
            if rect_intersects(pullback, cabinet_front):
                blocked_reasons.append(
                    "clearance_conflict: chair_pullback_clearance overlaps cabinet_front_clearance."
                )

    if not blocked_reasons:
        return None

    if any("entry_clearance_conflict" in reason for reason in blocked_reasons):
        failure_category = "entry_clearance_conflict"
    else:
        failure_category = "clearance_conflict"
    return {
        "status": "blocked",
        "failure_category": failure_category,
        "blocked_reasons": blocked_reasons,
    }


def classify_placement_failures(placements: list[dict[str, Any]]) -> tuple[str, list[str]]:
    """Map placement failures to a benchmark failure category."""

    reasons: list[str] = []
    for placement in placements:
        if placement.get("status") == "placed":
            continue
        reasons.extend(str(item) for item in placement.get("failure_reasons", []) if item)
    if any("insufficient" in reason for reason in reasons):
        return "insufficient_space", reasons
    if any("path_surface" in reason for reason in reasons):
        return "circulation_conflict", reasons
    if any("fixed_obstacle" in reason for reason in reasons):
        return "obstacle_conflict", reasons
    if reasons:
        return "layout_blocked", reasons
    return "", []


def evaluate_blank_shell_layout_expectation(
    workflow: dict[str, Any],
    *,
    placements: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Honor workflow layout_expectation by blocking partial-success layouts."""

    expectation = workflow.get("layout_expectation")
    if not isinstance(expectation, dict):
        return None
    mode = str(expectation.get("mode", ""))
    if mode != "require_all_placed":
        return None

    blocked_placements = [placement for placement in placements if placement.get("status") != "placed"]
    if not blocked_placements:
        return None

    failure_category, blocked_reasons = classify_placement_failures(placements)
    if not failure_category:
        failure_category = str(expectation.get("failure_category", "insufficient_space"))
    return {
        "status": "blocked",
        "failure_category": failure_category,
        "blocked_reasons": blocked_reasons or ["one or more required placements were blocked."],
    }
