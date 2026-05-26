"""Non-CAD geometry checks derived from CAD_PLAN and layout metadata."""

from __future__ import annotations

from typing import Any

from core.layout_engine.basic_layout import bbox_inside, bboxes_overlap
from core.plan_engine.validate_plan import validate_plan

BLOCK_REFERENCE_READBACK_FIELDS = (
    "handle",
    "type",
    "block_name",
    "insertion_point",
    "rotation",
    "scale",
    "layer",
    "bbox",
)

BLOCK_INSERTION_TOLERANCE_MM = 1.0
BLOCK_ROTATION_TOLERANCE_DEG = 0.5
BLOCK_BBOX_TOLERANCE_MM = 2.0


def expected_bbox_from_plan(plan: dict[str, Any]) -> dict[str, list[float | int]]:
    obj = plan["object"]
    base = plan["placement"].get("base_point", [0, 0, 0])
    return {
        "min": [base[0], base[1]],
        "max": [base[0] + obj["width"], base[1] + obj["depth"]],
    }


def missing_block_reference_fields(entity: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for field in BLOCK_REFERENCE_READBACK_FIELDS:
        if field not in entity:
            missing.append(field)
            continue
        value = entity.get(field)
        if value is None or value == "" or value == []:
            missing.append(field)
    return missing


def classify_block_readback_failure(check_name: str) -> str:
    mapping = {
        "readback_fields": "readback_missing",
        "block_name": "block_name_mismatch",
        "insertion_point": "anchor_mismatch",
        "rotation": "rotation_mismatch",
        "scale": "geometry_mismatch",
        "layer": "layer_mismatch",
        "bbox": "geometry_mismatch",
    }
    return mapping.get(check_name, "geometry_mismatch")


def expected_block_reference_from_plan(plan: dict[str, Any]) -> dict[str, Any]:
    from core.block_engine.block_placement import create_block_insertion_intent
    from core.plan_engine.block_alpha_plan import _block_dict_from_plan

    placement = plan["placement"]
    base = placement.get("base_point", [0, 0, 0])
    if len(base) == 2:
        base = [base[0], base[1], 0]
    block = _block_dict_from_plan(plan)
    cad_identity = plan["object"].get("cad_identity", {})
    intent = create_block_insertion_intent(
        block,
        base_point=base,
        rotation=placement.get("rotation", 0),
        layer=plan["drawing"]["layer"],
    )
    return {
        "block_name": str(cad_identity.get("block_name", "")),
        "insertion_point": [float(value) for value in base[:3]],
        "rotation": float(placement.get("rotation", 0)),
        "scale": [float(value) for value in placement.get("scale", [1, 1, 1])],
        "layer": plan["drawing"]["layer"],
        "bbox": intent["bbox"],
    }


def _near(actual: float, expected: float, tolerance: float) -> bool:
    return abs(actual - expected) <= tolerance


def _near_xy(actual: list[float], expected: list[float], tolerance: float) -> bool:
    if len(actual) < 2 or len(expected) < 2:
        return False
    return _near(float(actual[0]), float(expected[0]), tolerance) and _near(float(actual[1]), float(expected[1]), tolerance)


def _check_block_field(
    *,
    name: str,
    status: str,
    message: str,
    failure_category: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"name": name, "status": status, "message": message}
    if failure_category:
        payload["failure_category"] = failure_category
    return payload


def check_block_reference_readback(
    plan: dict[str, Any],
    entity: dict[str, Any],
    *,
    insertion_tolerance_mm: float = BLOCK_INSERTION_TOLERANCE_MM,
    rotation_tolerance_deg: float = BLOCK_ROTATION_TOLERANCE_DEG,
    bbox_tolerance_mm: float = BLOCK_BBOX_TOLERANCE_MM,
) -> list[dict[str, Any]]:
    """Compare a normalized block_reference entity against insert_block_alpha expectations."""

    expected = expected_block_reference_from_plan(plan)
    checks: list[dict[str, Any]] = []

    missing = missing_block_reference_fields(entity)
    if missing:
        checks.append(
            _check_block_field(
                name="readback_fields",
                status="fail",
                message=f"missing fields: {missing}",
                failure_category="readback_missing",
            )
        )
        return checks

    if entity.get("type") != "block_reference":
        checks.append(
            _check_block_field(
                name="entity_type",
                status="fail",
                message=f"expected block_reference, got {entity.get('type')!r}",
                failure_category="readback_missing",
            )
        )

    block_name = str(entity.get("block_name", ""))
    block_ok = block_name == expected["block_name"]
    checks.append(
        _check_block_field(
            name="block_name",
            status="pass" if block_ok else "fail",
            message=f"actual={block_name!r}, expected={expected['block_name']!r}",
            failure_category=None if block_ok else "block_name_mismatch",
        )
    )

    insertion = entity.get("insertion_point", [])
    insertion_ok = _near_xy(insertion, expected["insertion_point"], insertion_tolerance_mm)
    checks.append(
        _check_block_field(
            name="insertion_point",
            status="pass" if insertion_ok else "fail",
            message=f"actual={insertion}, expected={expected['insertion_point']}",
            failure_category=None if insertion_ok else "anchor_mismatch",
        )
    )

    rotation = float(entity.get("rotation", 0))
    expected_rotation = float(expected["rotation"])
    rotation_ok = _near(rotation, expected_rotation, rotation_tolerance_deg)
    checks.append(
        _check_block_field(
            name="rotation",
            status="pass" if rotation_ok else "fail",
            message=f"actual={rotation}, expected={expected_rotation}",
            failure_category=None if rotation_ok else "rotation_mismatch",
        )
    )

    scale = entity.get("scale", [])
    expected_scale = expected["scale"]
    scale_ok = (
        isinstance(scale, list)
        and len(scale) == 3
        and all(_near(float(scale[index]), float(expected_scale[index]), 1e-6) for index in range(3))
    )
    checks.append(
        _check_block_field(
            name="scale",
            status="pass" if scale_ok else "fail",
            message=f"actual={scale}, expected={expected_scale}",
            failure_category=None if scale_ok else "geometry_mismatch",
        )
    )

    layer_ok = entity.get("layer") == expected["layer"]
    checks.append(
        _check_block_field(
            name="layer",
            status="pass" if layer_ok else "fail",
            message=f"actual={entity.get('layer')!r}, expected={expected['layer']!r}",
            failure_category=None if layer_ok else "layer_mismatch",
        )
    )

    actual_bbox = entity.get("bbox")
    expected_bbox = expected.get("bbox")
    if isinstance(actual_bbox, dict) and isinstance(expected_bbox, dict):
        bbox_ok = _near_xy(actual_bbox.get("min", []), expected_bbox.get("min", []), bbox_tolerance_mm) and _near_xy(
            actual_bbox.get("max", []),
            expected_bbox.get("max", []),
            bbox_tolerance_mm,
        )
        checks.append(
            _check_block_field(
                name="bbox",
                status="pass" if bbox_ok else "fail",
                message=f"actual={actual_bbox}, expected={expected_bbox}",
                failure_category=None if bbox_ok else "geometry_mismatch",
            )
        )
    else:
        checks.append(
            _check_block_field(
                name="bbox",
                status="fail",
                message="bbox evidence missing on readback entity or plan expectation",
                failure_category="readback_missing",
            )
        )

    return checks


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

    if plan.get("intent") == "insert_block_alpha":
        return [
            {
                "name": "block_reference_readback_required",
                "status": "not_run",
                "message": "Use check_block_reference_readback() with a normalized CAD entity.",
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
