"""Create CAD-independent block insertion intents."""

from __future__ import annotations

import math
from typing import Any


def create_block_insertion_intent(
    block: dict[str, Any],
    *,
    base_point: list[float | int],
    rotation: float | int = 0,
    layer: str = "CODEX_PREVIEW",
) -> dict[str, Any]:
    if rotation and not block.get("rotation_allowed", False):
        raise ValueError(f"Block {block.get('block_id')} does not allow rotation.")
    anchors = block.get("anchor_points", {})
    insertion = anchors.get("insert") if isinstance(anchors, dict) else None
    if insertion is None:
        insertion = block.get("insertion_point", [0, 0, 0])
    footprint = block.get("footprint_2d", block.get("size", {}))
    width = footprint["width"]
    depth = footprint["depth"]
    normalized_rotation = int(rotation) % 360 if float(rotation).is_integer() else rotation
    warnings: list[str] = []
    if normalized_rotation in {90, 270}:
        warnings.append("right_angle_rotation_bbox")
    elif normalized_rotation not in {0, 180}:
        warnings.append("non_right_angle_rotation_bbox_is_approximate")

    bbox = _rotated_block_bbox(
        width=float(width),
        depth=float(depth),
        insertion=[float(insertion[0]), float(insertion[1])],
        base_point=[float(base_point[0]), float(base_point[1])],
        rotation_degrees=float(rotation),
    )
    cad_identity = block.get("cad_identity", {})
    return {
        "operation": "insert_block_preview_intent",
        "executes_cad": False,
        "block_id": block["block_id"],
        "name": block["name"],
        "cad_identity": cad_identity,
        "base_point": base_point,
        "rotation": rotation,
        "layer": layer,
        "layer_role": block.get("layer_bindings", {}).get("insert_layer_role", "preview"),
        "bbox": bbox,
        "validation_status": block.get("validation", {}).get("status", "symbol_fallback"),
        "geometry_accuracy": "not_verified_without_cad_readback",
        "warnings": warnings,
    }


def _rotated_block_bbox(
    *,
    width: float,
    depth: float,
    insertion: list[float],
    base_point: list[float],
    rotation_degrees: float,
) -> dict[str, list[float]]:
    theta = math.radians(rotation_degrees)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    xs: list[float] = []
    ys: list[float] = []
    for x, y in ((0.0, 0.0), (width, 0.0), (width, depth), (0.0, depth)):
        local_x = x - insertion[0]
        local_y = y - insertion[1]
        xs.append(base_point[0] + local_x * cos_t - local_y * sin_t)
        ys.append(base_point[1] + local_x * sin_t + local_y * cos_t)
    return {
        "min": [min(xs), min(ys)],
        "max": [max(xs), max(ys)],
    }
