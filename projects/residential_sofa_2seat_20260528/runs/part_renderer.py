"""Case-local visual-parts renderer for sofa round12.

This is intentionally kept under the case until the visual contract passes user
review. Core promotion happens in a later package.
"""

from __future__ import annotations

from typing import Any

from core.cad_io.autocad_com import PREVIEW_LAYER


REQUIRED_PART_IDS = {
    "arm_left",
    "arm_right",
    "seat_left",
    "seat_right",
    "back_left",
    "back_right",
    "base_rail",
}


def _collect(result: object) -> list[str]:
    if isinstance(result, dict) and result.get("handle"):
        return [str(result["handle"])]
    if isinstance(result, dict) and isinstance(result.get("handles"), list):
        return [str(handle) for handle in result["handles"]]
    if isinstance(result, str):
        return [result]
    if isinstance(result, list):
        return [str(item) for item in result]
    return []


def _line(driver: Any, x1: float, y1: float, x2: float, y2: float) -> list[str]:
    return _collect(
        driver.draw_line(
            start_point=[x1, y1, 0],
            end_point=[x2, y2, 0],
            layer=PREVIEW_LAYER,
            color="cyan",
        )
    )


def _arc(driver: Any, cx: float, cy: float, r: float, start: float, end: float) -> list[str]:
    return _collect(
        driver.draw_arc(
            center=[cx, cy, 0],
            radius=r,
            start_angle=start,
            end_angle=end,
            layer=PREVIEW_LAYER,
            color="cyan",
        )
    )


def _rounded_rect(driver: Any, x0: float, y0: float, x1: float, y1: float, r: float) -> list[str]:
    min_straight_mm = 8.0
    r = max(
        1.0,
        min(
            r,
            max(1.0, (abs(x1 - x0) - min_straight_mm) / 2.0),
            max(1.0, (abs(y1 - y0) - min_straight_mm) / 2.0),
        ),
    )
    handles: list[str] = []
    handles += _line(driver, x0 + r, y0, x1 - r, y0)
    handles += _arc(driver, x1 - r, y0 + r, r, 270, 360)
    handles += _line(driver, x1, y0 + r, x1, y1 - r)
    handles += _arc(driver, x1 - r, y1 - r, r, 0, 90)
    handles += _line(driver, x1 - r, y1, x0 + r, y1)
    handles += _arc(driver, x0 + r, y1 - r, r, 90, 180)
    handles += _line(driver, x0, y1 - r, x0, y0 + r)
    handles += _arc(driver, x0 + r, y0 + r, r, 180, 270)
    return handles


def _part_bounds(part_id: str, *, x0: float, y0: float, width: float, height: float) -> tuple[float, float, float, float]:
    arm_w = 120.0
    gap = 8.0
    protrude = 30.0
    seat_bottom = y0 + 48.0
    seat_top = y0 + height * 0.23
    back_bottom = y0 + height * 0.29
    back_top = y0 + height - 18.0
    seat_w = (width - 2 * arm_w) / 2.0
    x1 = x0 + width

    if part_id == "arm_left":
        return (x0, y0 + protrude, x0 + arm_w, y0 + height - 30.0)
    if part_id == "arm_right":
        return (x1 - arm_w, y0 + protrude, x1, y0 + height - 30.0)
    if part_id == "seat_left":
        sx0 = x0 + arm_w + gap
        return (sx0, seat_bottom, sx0 + seat_w - 2 * gap, seat_top)
    if part_id == "seat_right":
        sx0 = x0 + arm_w + seat_w + gap
        return (sx0, seat_bottom, sx0 + seat_w - 2 * gap, seat_top)
    if part_id == "back_left":
        bx0 = x0 + arm_w + gap
        return (bx0, back_bottom, bx0 + seat_w - 2 * gap, back_top)
    if part_id == "back_right":
        bx0 = x0 + arm_w + seat_w + gap
        return (bx0, back_bottom, bx0 + seat_w - 2 * gap, back_top)
    if part_id == "base_rail":
        return (x0 + 12.0, y0 - 22.0, x1 - 12.0, y0 + 38.0)
    raise ValueError(f"unsupported visual part: {part_id}")


def render_visual_parts(
    driver: Any,
    visual_parts: dict[str, Any],
    *,
    origin: list[float],
    width: float,
    height: float,
) -> dict[str, Any]:
    """Render declared sofa visual parts and return part-to-handle coverage."""

    parts = visual_parts.get("parts")
    if not isinstance(parts, list):
        raise ValueError("visual_parts.parts must be a list")

    declared = {str(part.get("id")) for part in parts if isinstance(part, dict)}
    missing = sorted(REQUIRED_PART_IDS - declared)
    if missing:
        raise ValueError(f"missing required visual parts: {', '.join(missing)}")

    x0 = float(origin[0])
    y0 = float(origin[1])
    radius = float(visual_parts.get("sizing", {}).get("fillet_mm_approx", 30))
    part_handles: dict[str, list[str]] = {}

    for part in parts:
        part_id = str(part["id"])
        if part.get("closed") is not True:
            raise ValueError(f"visual part must be closed: {part_id}")
        shape = str(part.get("shape", ""))
        bx0, by0, bx1, by1 = _part_bounds(part_id, x0=x0, y0=y0, width=width, height=height)
        if shape not in {"rounded_rect", "pill_horizontal", "rounded_rect_tall", "rounded_rect_wide"}:
            raise ValueError(f"unsupported visual part shape: {shape}")
        part_handles[part_id] = _rounded_rect(driver, bx0, by0, bx1, by1, radius)

    return {
        "status": "rendered",
        "case_id": visual_parts.get("case_id"),
        "round": visual_parts.get("round"),
        "created_count": sum(len(handles) for handles in part_handles.values()),
        "part_handles": part_handles,
    }
