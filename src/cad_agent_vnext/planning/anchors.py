from __future__ import annotations

from cad_agent_vnext.domain.common import BBox2D, Point2D


ANCHOR_NAMES = {
    "front_left",
    "front_center",
    "front_right",
    "center_left",
    "center",
    "center_right",
    "rear_left",
    "rear_center",
    "rear_right",
}


def anchor_point(bbox: BBox2D, anchor: str, *, margin: float = 0) -> Point2D:
    if anchor not in ANCHOR_NAMES:
        raise ValueError(f"unsupported_anchor:{anchor}")
    min_x, min_y, max_x, max_y = bbox
    x_positions = {
        "left": min_x + margin,
        "center": (min_x + max_x) / 2,
        "right": max_x - margin,
    }
    y_positions = {
        "front": min_y + margin,
        "center": (min_y + max_y) / 2,
        "rear": max_y - margin,
    }
    if anchor == "center":
        return (x_positions["center"], y_positions["center"])
    vertical, horizontal = anchor.split("_", 1)
    return (x_positions[horizontal], y_positions[vertical])

