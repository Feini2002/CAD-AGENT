"""Small deterministic layout primitives for early Core verification."""

from __future__ import annotations

from typing import Any

from core.geometry_backends.rect2d import rect_contains, rect_intersects


def bbox_from_base(base_point: list[float | int], width: float | int, depth: float | int) -> dict[str, list[float | int]]:
    return {
        "min": [base_point[0], base_point[1]],
        "max": [base_point[0] + width, base_point[1] + depth],
    }


def bbox_inside(inner: dict[str, list[float | int]], outer: dict[str, list[float | int]]) -> bool:
    return rect_contains(outer, inner)


def bboxes_overlap(first: dict[str, list[float | int]], second: dict[str, list[float | int]]) -> bool:
    return rect_intersects(first, second)


def create_single_object_layout(
    *,
    project_model: dict[str, Any],
    object_spec: dict[str, Any],
    base_point: list[float | int] | None = None,
) -> dict[str, Any]:
    space = project_model["spaces"][0]
    boundary = space["boundary"]
    size = object_spec["size"]
    base = base_point or boundary["min"] + [0]
    bbox = bbox_from_base(base, size["width"], size["depth"])
    inside = bbox_inside(bbox, boundary)

    return {
        "version": "0.1",
        "layout_id": f"layout-{project_model['project_id']}",
        "project_id": project_model["project_id"],
        "candidates": [
            {
                "candidate_id": "candidate-001",
                "score": 0.85 if inside else 0.2,
                "placements": [
                    {
                        "object_id": object_spec["object_id"],
                        "base_point": base,
                        "rotation": 0,
                        "bbox": bbox,
                    }
                ],
                "checks": [
                    {
                        "name": "inside_boundary",
                        "status": "pass" if inside else "fail",
                    }
                ],
            }
        ],
        "uncertainties": [] if inside else ["Object placement exceeds the selected space boundary."],
    }


def create_layout_candidates(
    *,
    project_model: dict[str, Any],
    object_specs: list[dict[str, Any]],
    preferences: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from core.layout_engine.clearance import check_clearance
    from core.layout_engine.circulation import check_main_aisle_width
    from core.layout_engine.collision import check_collisions
    from core.layout_engine.scoring import score_checks

    preferences = preferences or {}
    boundary = project_model["spaces"][0]["boundary"]
    cursor_x = boundary["min"][0]
    base_y = boundary["min"][1]
    spacing = preferences.get("object_spacing_mm", 300)
    placements: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []

    for spec in object_specs:
        size = spec["size"]
        base = [cursor_x, base_y, 0]
        bbox = bbox_from_base(base, size["width"], size["depth"])
        inside = bbox_inside(bbox, boundary)
        checks.append(
            {
                "name": "inside_boundary",
                "status": "pass" if inside else "fail",
                "objects": [spec["object_id"]],
                "message": f"{spec['object_id']} bbox {bbox}",
            }
        )
        placements.append(
            {
                "object_id": spec["object_id"],
                "base_point": base,
                "rotation": 0,
                "bbox": bbox,
            }
        )
        cursor_x += size["width"] + spacing

    checks.extend(check_collisions(placements))
    checks.extend(check_clearance(placements, minimum_clearance=preferences.get("minimum_clearance_mm", 100)))
    if "main_aisle_width_mm" in preferences:
        checks.extend(
            check_main_aisle_width(
                placements=placements,
                boundary=boundary,
                minimum_width=preferences["main_aisle_width_mm"],
            )
        )
    score = score_checks(checks)
    return {
        "version": "0.1",
        "layout_id": f"layout-{project_model['project_id']}",
        "project_id": project_model["project_id"],
        "candidates": [
            {
                "candidate_id": "candidate-001",
                "score": score,
                "placements": placements,
                "checks": checks,
            }
        ],
        "uncertainties": [] if score >= 0.7 else ["One or more layout checks failed."],
    }
