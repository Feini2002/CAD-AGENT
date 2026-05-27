"""Validation and dry-run helpers for insert_block_alpha CAD_PLAN intents."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.block_engine.block_placement import create_block_insertion_intent
from core.verification.evidence_contract import (
    EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)


PREVIEW_LAYER = "CODEX_PREVIEW"
BLOCK_REFERENCE_TYPE = "block_reference"
CONTROLLED_BLOCK_ID = "controlled-test-block-001"
CONTROLLED_BLOCK_NAME = "CODEX_TEST_BLOCK_001"
SECOND_CONTROLLED_BLOCK_ID = "controlled-test-block-002"
SECOND_CONTROLLED_BLOCK_NAME = "CODEX_TEST_BLOCK_002"
CONTROLLED_BLOCK_ALLOWLIST = {
    CONTROLLED_BLOCK_ID: CONTROLLED_BLOCK_NAME,
    SECOND_CONTROLLED_BLOCK_ID: SECOND_CONTROLLED_BLOCK_NAME,
}


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
    block_id = str(obj.get("block_id", "")).strip()
    _require(bool(block_id), "object.block_id is required.", errors)
    if block_id:
        _require(
            block_id in CONTROLLED_BLOCK_ALLOWLIST,
            "insert_block_alpha only allows controlled test block ids: "
            + ", ".join(sorted(CONTROLLED_BLOCK_ALLOWLIST)),
            errors,
        )
    _require(bool(str(obj.get("name", "")).strip()), "object.name is required.", errors)

    cad_identity = obj.get("cad_identity")
    _require(isinstance(cad_identity, dict), "object.cad_identity is required.", errors)
    if isinstance(cad_identity, dict):
        block_name = str(cad_identity.get("block_name", "")).strip()
        _require(bool(block_name), "object.cad_identity.block_name is required.", errors)
        if block_name and block_id in CONTROLLED_BLOCK_ALLOWLIST:
            expected_name = CONTROLLED_BLOCK_ALLOWLIST[block_id]
            _require(
                block_name == expected_name,
                f"insert_block_alpha block_id={block_id} requires object.cad_identity.block_name={expected_name}.",
                errors,
            )

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
        if len(scale) == 3 and all(isinstance(value, (int, float)) for value in scale):
            _require(
                scale[0] == scale[1] == scale[2],
                "insert_block_alpha alpha only supports uniform scale.",
                errors,
            )

    layer = drawing.get("layer")
    _require(bool(layer), "drawing.layer is required.", errors)
    _require(layer == PREVIEW_LAYER, f"insert_block_alpha only allows drawing.layer={PREVIEW_LAYER}.", errors)

    attributes = obj.get("attributes")
    attribute_probe = bool(obj.get("attribute_readback_probe"))
    if attributes is not None:
        _require(isinstance(attributes, dict), "object.attributes must be an object when provided.", errors)
        if attribute_probe and isinstance(attributes, dict):
            _require(bool(attributes), "attribute_readback_probe requires non-empty object.attributes.", errors)
            for tag, value in attributes.items():
                if not str(tag).strip():
                    errors.append("object.attributes keys must be non-empty tag names.")
                if not isinstance(value, (str, int, float)):
                    errors.append(f"object.attributes[{tag!r}] must be a scalar value.")
        elif attributes and not attribute_probe:
            errors.append(
                "object.attributes is only allowed when object.attribute_readback_probe is true (BETA-CAD-BLOCK-02 probe plans)."
            )

    if attribute_probe and attributes is None:
        errors.append("object.attribute_readback_probe requires object.attributes.")

    return errors


def _block_dict_from_plan(plan: dict[str, Any]) -> dict[str, Any]:
    obj = plan["object"]
    placement = plan["placement"]
    cad_identity = obj.get("cad_identity", {})
    block_id = str(obj["block_id"])
    block_name = str(cad_identity.get("block_name", block_id))

    scale = placement.get("scale", [1, 1, 1])
    scale_factor = float(scale[0])
    try:
        from core.block_engine.block_library import load_block_library, normalize_block

        for block in load_block_library().get("blocks", []):
            if isinstance(block, dict) and block.get("block_id") == block_id:
                normalized = deepcopy(normalize_block(block))
                if scale_factor != 1.0:
                    for size_key in ("size", "footprint_2d"):
                        size = normalized.get(size_key)
                        if isinstance(size, dict):
                            for axis in ("width", "depth", "height"):
                                if isinstance(size.get(axis), (int, float)):
                                    size[axis] = float(size[axis]) * scale_factor
                    anchor_points = normalized.get("anchor_points")
                    if isinstance(anchor_points, dict):
                        for key, point in list(anchor_points.items()):
                            if isinstance(point, list):
                                anchor_points[key] = [
                                    float(value) * scale_factor if isinstance(value, (int, float)) else value
                                    for value in point
                                ]
                    insertion_point = normalized.get("insertion_point")
                    if isinstance(insertion_point, list):
                        normalized["insertion_point"] = [
                            float(value) * scale_factor if isinstance(value, (int, float)) else value
                            for value in insertion_point
                        ]
                return normalized
    except (OSError, ValueError):
        pass

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

    if plan.get("drawing_standard_profile_id"):
        from core.drawing_standard.drawing_standard_profile import apply_drawing_standard_to_plan

        plan = apply_drawing_standard_to_plan(
            dict(plan),
            object_role=str(plan.get("object_role", "block_insert")),
        )

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
        "evidence_state": EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
        "human_summary": human_summary,
    }
