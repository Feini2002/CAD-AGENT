"""Create CAD-independent block insertion intents."""

from __future__ import annotations

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
    insertion = block.get("insertion_point", [0, 0, 0])
    width = block["size"]["width"]
    depth = block["size"]["depth"]
    normalized_rotation = int(rotation) % 360 if float(rotation).is_integer() else rotation
    warnings: list[str] = []
    if normalized_rotation in {90, 270}:
        bbox_width, bbox_depth = depth, width
        anchor_x, anchor_y = insertion[1], insertion[0]
        warnings.append("right_angle_rotation_bbox")
    elif normalized_rotation in {0, 180}:
        bbox_width, bbox_depth = width, depth
        anchor_x, anchor_y = insertion[0], insertion[1]
    else:
        bbox_width, bbox_depth = width, depth
        anchor_x, anchor_y = insertion[0], insertion[1]
        warnings.append("non_right_angle_rotation_bbox_is_approximate")

    min_x = base_point[0] - anchor_x
    min_y = base_point[1] - anchor_y
    return {
        "operation": "insert_block_preview_intent",
        "executes_cad": False,
        "block_id": block["block_id"],
        "name": block["name"],
        "base_point": base_point,
        "rotation": rotation,
        "layer": layer,
        "bbox": {
            "min": [min_x, min_y],
            "max": [min_x + bbox_width, min_y + bbox_depth],
        },
        "warnings": warnings,
    }
