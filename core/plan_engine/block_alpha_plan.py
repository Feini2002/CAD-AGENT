"""Validation and dry-run helpers for insert_block_alpha CAD_PLAN intents."""

from __future__ import annotations

from typing import Any

from core.block_engine.block_placement import create_block_insertion_intent
from core.verification.evidence_contract import NON_CAD_GEOMETRY_ACCURACY, SCREENSHOT_NOT_APPLICABLE


PREVIEW_LAYER = "CODEX_PREVIEW"
BLOCK_REFERENCE_TYPE = "block_reference"


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _point3(point: Any) -> list[float | int]:
    if not isinstance(point, list) or len(point) not in (2, 3):
        return [0, 0, 0]
    if len(point) == 2:
        return [point[0], point[1], 0]
    return [point[0], point[1], point[2]]


def validate_insert_block_alpha(plan: dict[str, Any]) -> list[str]:
    """Validate a preview-only block insertion CAD_PLAN."""

    errors: list[str] = []
    obj = plan.get("object", {})
    placement = plan.get("placement", {})
    drawing = plan.get("drawing", {})

    _require(isinstance(obj, dict), "object must be an object.", errors)
    _require(isinstance(placement, dict), "placement must be an object.", errors)
    _require(isinstance(drawing, dict), "drawing must be an object.", errors)
    if errors:
        return errors

    _require(obj.get("type") == BLOCK_REFERENCE_TYPE, "object.type must be 'block_reference'.", errors)
    _require(bool(str(obj.get("block_id", "")).strip()), "object.block_id is required.", errors)
    _require(bool(str(obj.get("name", "")).strip()), "object.name is required.", errors)

    cad_identity = obj.get("cad_identity")
    _require(isinstance(cad_identity, dict), "object.cad_identity is required.", errors)
    if isinstance(cad_identity, dict):
        _require(bool(str(cad_identity.get("block_name", "")).strip()), "object.cad_identity.block_name is required.", errors)

    _require(placement.get("mode") == "absolute", "insert_block_alpha only supports placement.mode=absolute.", errors)
    base_point = placement.get("base_point")
    _require(isinstance(base_point, list), "placement.base_point is required for absolute placement.", errors)
    if isinstance(base_point, list):
        _require(len(base_point) in (2, 3), "placement.base_point must contain 2 or 3 numbers.", errors)
        _require(all(isinstance(value, (int, float)) for value in base_point), "placement.base_point values must be numbers.", errors)

    rotation = placement.get("rotation", 0)
    _require(isinstance(rotation, (int, float)), "placement.rotation must be a number.", errors)

    scale = placement.get("scale", [1, 1, 1])
    _require(isinstance(scale, list), "placement.scale must be an array of three numbers.", errors)
    if isinstance(scale, list):
        _require(len(scale) == 3, "placement.scale must contain exactly three values.", errors)
        _require(all(isinstance(value, (int, float)) for value in scale), "placement.scale values must be numbers.", errors)
        _require(all(value > 0 for value in scale), "placement.scale values must be greater than 0.", errors)

    layer = drawing.get("layer")
    _require(bool(layer), "drawing.layer is required.", errors)
    _require(layer == PREVIEW_LAYER, f"insert_block_alpha only allows drawing.layer={PREVIEW_LAYER}.", errors)

    attributes = obj.get("attributes")
    if attributes is not None:
        _require(isinstance(attributes, dict), "object.attributes must be an object when provided.", errors)

    return errors


def _block_dict_from_plan(plan: dict[str, Any]) -> dict[str, Any]:
    obj = plan["object"]
    placement = plan["placement"]
    cad_identity = obj.get("cad_identity", {})
    block_id = str(obj["block_id"])
    block_name = str(cad_identity.get("block_name", block_id))

    try:
        from core.block_engine.block_library import load_block_library, normalize_block

        for block in load_block_library().get("blocks", []):
            if isinstance(block, dict) and block.get("block_id") == block_id:
                return normalize_block(block)
    except (OSError, ValueError):
        pass

    scale = placement.get("scale", [1, 1, 1])
    width = 900 * float(scale[0])
    depth = 450 * float(scale[1])
    return {
        "block_id": block_id,
        "name": obj.get("name", block_name),
        "cad_identity": {
            "block_name": block_name,
            "definition_name": block_name,
            "expected_entity_type": "block_reference",
        },
        "size": {"width": width, "depth": depth},
        "footprint_2d": {"width": width, "depth": depth},
        "anchor_points": {"insert": _point3(placement.get("base_point", [0, 0, 0]))},
        "insertion_point": _point3(placement.get("base_point", [0, 0, 0])),
        "rotation_allowed": True,
        "layer_bindings": {"insert_layer_role": "preview"},
        "validation": {"status": "metadata_only"},
    }


def create_insert_block_alpha_dry_run_report(plan: dict[str, Any]) -> dict[str, Any]:
    """Build a machine-readable dry-run report for insert_block_alpha."""

    from core.plan_engine.validate_plan import validate_plan

    errors = validate_plan(plan)
    if errors:
        return {
            "version": "0.1",
            "status": "invalid",
            "validation_errors": errors,
            "entities": [],
            "human_summary": "INVALID CAD_PLAN",
        }

    obj = plan["object"]
    placement = plan["placement"]
    drawing = plan["drawing"]
    base_point = _point3(placement["base_point"])
    rotation = placement.get("rotation", 0)
    scale = placement.get("scale", [1, 1, 1])
    block = _block_dict_from_plan(plan)
    intent = create_block_insertion_intent(
        block,
        base_point=base_point,
        rotation=rotation,
        layer=drawing["layer"],
    )

    cad_identity = obj.get("cad_identity", {})
    checks = [
        {
            "name": "preview_layer_only",
            "status": "pass" if drawing["layer"] == PREVIEW_LAYER else "fail",
            "message": f"layer={drawing['layer']}",
        },
        {
            "name": "block_identity",
            "status": "pass" if cad_identity.get("block_name") else "fail",
            "message": str(cad_identity.get("block_name", "")),
        },
        {
            "name": "anchor_point",
            "status": "pass",
            "message": str(base_point),
        },
        {
            "name": "rotation",
            "status": "pass",
            "message": str(rotation),
        },
        {
            "name": "scale",
            "status": "pass",
            "message": str(scale),
        },
        {
            "name": "bbox_preview",
            "status": "pass",
            "message": str(intent["bbox"]),
        },
    ]
    layer_role = intent.get("layer_role", block.get("layer_bindings", {}).get("insert_layer_role", "preview"))

    human_summary = "\n".join(
        [
            "CAD_PLAN DRY RUN",
            f"- intent: {plan['intent']}",
            f"- block_id: {obj.get('block_id')}",
            f"- block_name: {cad_identity.get('block_name')}",
            f"- placement: absolute at {base_point}, rotation={rotation}, scale={scale}",
            f"- layer: {drawing.get('layer')}",
            f"- layer_role: {layer_role}",
            f"- bbox: {intent['bbox']}",
            f"- geometry_accuracy: {NON_CAD_GEOMETRY_ACCURACY}",
        ]
    )
    return {
        "version": "0.1",
        "status": "valid",
        "validation_errors": [],
        "intent": plan["intent"],
        "layer": drawing["layer"],
        "layer_role": layer_role,
        "bbox": intent["bbox"],
        "entities": [
            {
                "type": "block_reference",
                "layer": drawing["layer"],
                "block_id": obj.get("block_id"),
                "block_name": cad_identity.get("block_name"),
                "base_point": base_point,
                "rotation": rotation,
                "scale": scale,
                "bbox": intent["bbox"],
            }
        ],
        "checks": checks,
        "evidence_state": "dry_run_valid_plan_only",
        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
        "human_summary": human_summary,
    }
