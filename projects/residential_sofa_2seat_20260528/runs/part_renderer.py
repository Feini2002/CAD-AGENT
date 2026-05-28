"""Case-local visual-parts renderer for sofa visual training rounds.

This is intentionally kept under the case until the visual contract passes user
review. Core promotion happens in a later package.
"""

from __future__ import annotations

import math
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

ROUNDED_RECT_FAMILY = {
    "rounded_rect",
    "pill_horizontal",
    "rounded_rect_tall",
    "rounded_rect_wide",
}

CURVED_SHAPE_FAMILY = {
    "curved_arm",
    "seat_bow_cushion",
    "back_soft_panel",
    "base_curved_rail",
}

CONNECTION_SPECS = (
    ("arm_left", "seat_left", "x"),
    ("seat_right", "arm_right", "x"),
    ("base_rail", "arm_left", "y"),
    ("base_rail", "arm_right", "y"),
    ("base_rail", "seat_left", "y"),
    ("base_rail", "seat_right", "y"),
)

HARD_BACK_ROLES = {"hard_back", "rear_back", "rear_back_rail", "structural_back"}
DEFAULT_LAYER_ORDER_BACK_TO_FRONT = ("hard_back", "back_cushion", "seat_cushion")


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


def _line_key(x1: float, y1: float, x2: float, y2: float) -> tuple[float, float, float, float]:
    p1 = (round(x1, 3), round(y1, 3))
    p2 = (round(x2, 3), round(y2, 3))
    a, b = sorted([p1, p2])
    return (a[0], a[1], b[0], b[1])


def _line(
    driver: Any,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    line_registry: set[tuple[float, float, float, float]] | None = None,
    line_stats: dict[str, int] | None = None,
) -> list[str]:
    if line_registry is not None:
        key = _line_key(x1, y1, x2, y2)
        if key in line_registry:
            if line_stats is not None:
                line_stats["deduped_line_count"] = line_stats.get("deduped_line_count", 0) + 1
            return []
        line_registry.add(key)
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


def _rounded_rect(
    driver: Any,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    r: float,
    *,
    line_registry: set[tuple[float, float, float, float]] | None = None,
    line_stats: dict[str, int] | None = None,
) -> list[str]:
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
    handles += _line(driver, x0 + r, y0, x1 - r, y0, line_registry=line_registry, line_stats=line_stats)
    handles += _arc(driver, x1 - r, y0 + r, r, 270, 360)
    handles += _line(driver, x1, y0 + r, x1, y1 - r, line_registry=line_registry, line_stats=line_stats)
    handles += _arc(driver, x1 - r, y1 - r, r, 0, 90)
    handles += _line(driver, x1 - r, y1, x0 + r, y1, line_registry=line_registry, line_stats=line_stats)
    handles += _arc(driver, x0 + r, y1 - r, r, 90, 180)
    handles += _line(driver, x0, y1 - r, x0, y0 + r, line_registry=line_registry, line_stats=line_stats)
    handles += _arc(driver, x0 + r, y0 + r, r, 180, 270)
    return handles


def _bow_arc(driver: Any, xl: float, xr: float, y: float, bow: float) -> list[str]:
    chord = xr - xl
    if chord <= 0:
        return []
    sag = max(4.0, min(float(bow), chord * 0.08))
    radius = (chord * chord) / (8.0 * sag) + sag / 2.0
    cx = (xl + xr) / 2.0
    cy = y - radius + sag
    start = math.degrees(math.atan2(y - cy, xl - cx))
    end = math.degrees(math.atan2(y - cy, xr - cx))
    if (end - start) % 360.0 > 180.0:
        start, end = end, start
    return _arc(driver, cx, cy, radius, start, end)


def _bowed_rect(
    driver: Any,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    r: float,
    *,
    bow: float,
    line_registry: set[tuple[float, float, float, float]] | None = None,
    line_stats: dict[str, int] | None = None,
) -> list[str]:
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
    handles += _line(driver, x0 + r, y1, x1 - r, y1, line_registry=line_registry, line_stats=line_stats)
    handles += _arc(driver, x1 - r, y1 - r, r, 0, 90)
    handles += _line(driver, x1, y1 - r, x1, y0 + r, line_registry=line_registry, line_stats=line_stats)
    handles += _arc(driver, x1 - r, y0 + r, r, 270, 360)
    handles += _bow_arc(driver, x0 + r, x1 - r, y0, bow)
    handles += _arc(driver, x0 + r, y0 + r, r, 180, 270)
    handles += _line(driver, x0, y0 + r, x0, y1 - r, line_registry=line_registry, line_stats=line_stats)
    handles += _arc(driver, x0 + r, y1 - r, r, 90, 180)
    return handles


def _base_curved_rail(
    driver: Any,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    r: float,
    *,
    line_registry: set[tuple[float, float, float, float]] | None = None,
    line_stats: dict[str, int] | None = None,
) -> list[str]:
    return _bowed_rect(
        driver,
        x0,
        y0,
        x1,
        y1,
        min(r, 10.0),
        bow=8.0,
        line_registry=line_registry,
        line_stats=line_stats,
    )


def _shape_bounds(
    part: str | dict[str, Any],
    *,
    x0: float,
    y0: float,
    width: float,
    height: float,
) -> tuple[float, float, float, float]:
    if isinstance(part, dict):
        ratios = part.get("bounds_ratio")
        if isinstance(ratios, list) and len(ratios) == 4:
            rx0, ry0, rx1, ry1 = (float(value) for value in ratios)
            return (
                x0 + width * rx0,
                y0 + height * ry0,
                x0 + width * rx1,
                y0 + height * ry1,
            )
        part_id = str(part.get("id", ""))
    else:
        part_id = str(part)

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


def _part_bounds(part_id: str, *, x0: float, y0: float, width: float, height: float) -> tuple[float, float, float, float]:
    return _shape_bounds(part_id, x0=x0, y0=y0, width=width, height=height)


def _shape_family(shape: str) -> str:
    if shape in ROUNDED_RECT_FAMILY:
        return "rounded_rect"
    if shape in CURVED_SHAPE_FAMILY:
        return shape
    return shape or "unknown"


def _interval_overlap(a0: float, a1: float, b0: float, b1: float) -> float:
    return max(0.0, min(a1, b1) - max(a0, b0))


def _connection_defects(
    bounds: dict[str, tuple[float, float, float, float]],
    *,
    specs: tuple[tuple[str, str, str], ...] = CONNECTION_SPECS,
    tol: float = 1.0,
) -> tuple[int, int]:
    gap_count = 0
    overlap_count = 0
    for left_id, right_id, axis in specs:
        if left_id not in bounds or right_id not in bounds:
            continue
        ax0, ay0, ax1, ay1 = bounds[left_id]
        bx0, by0, bx1, by1 = bounds[right_id]
        if axis == "x":
            if _interval_overlap(ay0, ay1, by0, by1) <= tol:
                continue
            gap = max(bx0 - ax1, ax0 - bx1, 0.0)
            overlap = _interval_overlap(ax0, ax1, bx0, bx1)
        else:
            if _interval_overlap(ax0, ax1, bx0, bx1) <= tol:
                continue
            gap = max(by0 - ay1, ay0 - by1, 0.0)
            overlap = _interval_overlap(ay0, ay1, by0, by1)
        if gap > tol:
            gap_count += 1
        if overlap > tol:
            overlap_count += 1
    return gap_count, overlap_count


def _connection_specs(visual_parts: dict[str, Any]) -> tuple[tuple[str, str, str], ...]:
    layout = visual_parts.get("layout", {})
    raw_pairs = layout.get("connection_pairs") if isinstance(layout, dict) else None
    if not isinstance(raw_pairs, list):
        return CONNECTION_SPECS

    pairs: list[tuple[str, str, str]] = []
    for item in raw_pairs:
        if isinstance(item, list) and len(item) == 3:
            left_id, right_id, axis = item
        elif isinstance(item, dict):
            left_id, right_id, axis = item.get("a"), item.get("b"), item.get("axis")
        else:
            continue
        axis_str = str(axis)
        if axis_str not in {"x", "y"}:
            continue
        pairs.append((str(left_id), str(right_id), axis_str))
    return tuple(pairs) if pairs else CONNECTION_SPECS


def _semantic_role(part_id: str, role: str) -> str:
    if role in HARD_BACK_ROLES:
        return "hard_back"
    # Earlier rounds called the rear structural rail "front_rail"; keep reading
    # it as the hard back so the audit can catch the direction mistake.
    if part_id == "base_rail" and role in {"front_rail", "base_rail", ""}:
        return "hard_back"
    return role


def _sofa_layer_order_pass(
    role_bounds: dict[str, list[tuple[float, float, float, float]]],
    visual_parts: dict[str, Any],
) -> int:
    semantics = visual_parts.get("visual_semantics", {})
    if not isinstance(semantics, dict):
        semantics = {}
    order = semantics.get("layer_order_back_to_front", list(DEFAULT_LAYER_ORDER_BACK_TO_FRONT))
    if not isinstance(order, list) or len(order) < 3:
        order = list(DEFAULT_LAYER_ORDER_BACK_TO_FRONT)
    front_direction = str(semantics.get("plan_view_front_direction", "+Y"))

    centers: list[float] = []
    for role in order:
        grouped = role_bounds.get(str(role), [])
        if not grouped:
            return 0
        centers.append(sum((b[1] + b[3]) / 2.0 for b in grouped) / len(grouped))
    if front_direction == "-Y":
        return int(all(centers[i] > centers[i + 1] for i in range(len(centers) - 1)))
    return int(all(centers[i] < centers[i + 1] for i in range(len(centers) - 1)))


def summarize_visual_parts_for_audit(
    visual_parts: dict[str, Any],
    *,
    origin: list[float],
    width: float,
    height: float,
) -> dict[str, int]:
    parts = visual_parts.get("parts")
    if not isinstance(parts, list):
        return {}

    x0 = float(origin[0])
    y0 = float(origin[1])
    shape_families: list[str] = []
    bounds: dict[str, tuple[float, float, float, float]] = {}
    role_bounds: dict[str, list[tuple[float, float, float, float]]] = {}
    closed_part_count = seat_count = back_count = hard_back_count = rounded_count = 0

    for part in parts:
        if not isinstance(part, dict):
            continue
        part_id = str(part.get("id", ""))
        role = _semantic_role(part_id, str(part.get("role", "")))
        shape = str(part.get("shape", ""))
        family = _shape_family(shape)
        shape_families.append(family)
        if family == "rounded_rect":
            rounded_count += 1
        if part.get("closed") is True:
            closed_part_count += 1
        if role == "seat_cushion":
            seat_count += 1
        if role == "back_cushion":
            back_count += 1
        if role == "hard_back":
            hard_back_count += 1
        if part_id in REQUIRED_PART_IDS:
            part_bounds = _shape_bounds(part, x0=x0, y0=y0, width=width, height=height)
            bounds[part_id] = part_bounds
            role_bounds.setdefault(role, []).append(part_bounds)

    gap_count, overlap_count = _connection_defects(bounds, specs=_connection_specs(visual_parts))
    return {
        "required_part_count": len(REQUIRED_PART_IDS),
        "closed_part_count": closed_part_count,
        "seat_cushion_count": seat_count,
        "back_cushion_count": back_count,
        "hard_back_count": hard_back_count,
        "sofa_layer_order_pass": _sofa_layer_order_pass(role_bounds, visual_parts),
        "full_width_split_count": 0,
        "rounded_rect_family_count": rounded_count,
        "distinct_shape_family_count": len(set(shape_families)),
        "part_gap_count": gap_count,
        "part_overlap_count": overlap_count,
    }


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
    line_registry: set[tuple[float, float, float, float]] = set()
    line_stats = {"deduped_line_count": 0}
    audit_summary = summarize_visual_parts_for_audit(
        visual_parts,
        origin=origin,
        width=width,
        height=height,
    )

    for part in parts:
        part_id = str(part["id"])
        if part.get("closed") is not True:
            raise ValueError(f"visual part must be closed: {part_id}")
        shape = str(part.get("shape", ""))
        bx0, by0, bx1, by1 = _shape_bounds(part, x0=x0, y0=y0, width=width, height=height)
        if shape not in ROUNDED_RECT_FAMILY | CURVED_SHAPE_FAMILY:
            raise ValueError(f"unsupported visual part shape: {shape}")
        if shape == "base_curved_rail":
            part_handles[part_id] = _base_curved_rail(
                driver,
                bx0,
                by0,
                bx1,
                by1,
                radius,
                line_registry=line_registry,
                line_stats=line_stats,
            )
        elif shape in {"seat_bow_cushion", "back_soft_panel"}:
            bow = float(part.get("bow_mm", 24.0 if shape == "seat_bow_cushion" else 10.0))
            part_handles[part_id] = _bowed_rect(
                driver,
                bx0,
                by0,
                bx1,
                by1,
                radius,
                bow=bow,
                line_registry=line_registry,
                line_stats=line_stats,
            )
        else:
            part_handles[part_id] = _rounded_rect(
                driver,
                bx0,
                by0,
                bx1,
                by1,
                radius,
                line_registry=line_registry,
                line_stats=line_stats,
            )

    return {
        "status": "rendered",
        "case_id": visual_parts.get("case_id"),
        "round": visual_parts.get("round"),
        "created_count": sum(len(handles) for handles in part_handles.values()),
        "deduped_line_count": line_stats["deduped_line_count"],
        "part_handles": part_handles,
        "audit_summary": audit_summary,
    }
