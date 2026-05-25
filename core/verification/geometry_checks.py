"""Non-CAD geometry checks derived from CAD_PLAN and layout metadata."""

from __future__ import annotations

from typing import Any

from core.layout_engine.basic_layout import bbox_inside, bboxes_overlap
from core.plan_engine.validate_plan import validate_plan


def expected_bbox_from_plan(plan: dict[str, Any]) -> dict[str, list[float | int]]:
    obj = plan["object"]
    base = plan["placement"].get("base_point", [0, 0, 0])
    return {
        "min": [base[0], base[1]],
        "max": [base[0] + obj["width"], base[1] + obj["depth"]],
    }


def check_plan_geometry(
    plan: dict[str, Any],
    *,
    boundary: dict[str, list[float | int]] | None = None,
    other_bboxes: list[dict[str, list[float | int]]] | None = None,
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    validation_errors = validate_plan(plan)
    if validation_errors:
        return [
            {
                "name": "cad_plan_geometry_input",
                "status": "fail",
                "message": "; ".join(validation_errors),
            }
        ]

    bbox = expected_bbox_from_plan(plan)
    checks.append({"name": "expected_bbox", "status": "pass", "message": str(bbox), "bbox": bbox})
    if boundary is not None:
        checks.append(
            {
                "name": "inside_boundary",
                "status": "pass" if bbox_inside(bbox, boundary) else "fail",
                "message": f"bbox {bbox} within boundary {boundary}",
            }
        )
    for index, other in enumerate(other_bboxes or []):
        checks.append(
            {
                "name": f"overlap_{index}",
                "status": "fail" if bboxes_overlap(bbox, other) else "pass",
                "message": f"bbox {bbox} compared with {other}",
            }
        )
    return checks
