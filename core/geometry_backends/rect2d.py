"""No-dependency 2D rectangle geometry helpers."""

from __future__ import annotations

from math import hypot
from typing import Any


Number = float | int
Point = list[Number]
Rect = dict[str, Point]


def _point(value: Any, *, label: str) -> list[float]:
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"{label} must be a 2D point.")
    if not all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in value):
        raise ValueError(f"{label} must contain numeric coordinates.")
    return [float(value[0]), float(value[1])]


def normalize_rect(rect: dict[str, Any], *, label: str = "rect") -> dict[str, list[float]]:
    """Return a float bbox and reject inverted rectangles."""

    if not isinstance(rect, dict):
        raise ValueError(f"{label} must be an object.")
    min_point = _point(rect.get("min"), label=f"{label}.min")
    max_point = _point(rect.get("max"), label=f"{label}.max")
    if min_point[0] >= max_point[0] or min_point[1] >= max_point[1]:
        raise ValueError(f"{label}.min must be lower than {label}.max.")
    return {"min": min_point, "max": max_point}


def rect_area(rect: Rect) -> float:
    normalized = normalize_rect(rect)
    return (normalized["max"][0] - normalized["min"][0]) * (normalized["max"][1] - normalized["min"][1])


def rect_center(rect: Rect) -> list[float]:
    normalized = normalize_rect(rect)
    return [
        (normalized["min"][0] + normalized["max"][0]) / 2,
        (normalized["min"][1] + normalized["max"][1]) / 2,
    ]


def rect_intersects(first: Rect, second: Rect) -> bool:
    left = normalize_rect(first, label="first")
    right = normalize_rect(second, label="second")
    return not (
        left["max"][0] <= right["min"][0]
        or right["max"][0] <= left["min"][0]
        or left["max"][1] <= right["min"][1]
        or right["max"][1] <= left["min"][1]
    )


def rect_contains(outer: Rect, inner: Rect) -> bool:
    normalized_outer = normalize_rect(outer, label="outer")
    normalized_inner = normalize_rect(inner, label="inner")
    return (
        normalized_inner["min"][0] >= normalized_outer["min"][0]
        and normalized_inner["min"][1] >= normalized_outer["min"][1]
        and normalized_inner["max"][0] <= normalized_outer["max"][0]
        and normalized_inner["max"][1] <= normalized_outer["max"][1]
    )


def rect_gap(first: Rect, second: Rect) -> float:
    """Return the shortest distance between two rectangles, or 0 when overlapping."""

    left = normalize_rect(first, label="first")
    right = normalize_rect(second, label="second")
    x_gap = max(0.0, right["min"][0] - left["max"][0], left["min"][0] - right["max"][0])
    y_gap = max(0.0, right["min"][1] - left["max"][1], left["min"][1] - right["max"][1])
    if x_gap == 0:
        return float(y_gap)
    if y_gap == 0:
        return float(x_gap)
    return float(hypot(x_gap, y_gap))


def expand_rect(rect: Rect, amount: Number) -> dict[str, list[float]]:
    if not isinstance(amount, (int, float)) or isinstance(amount, bool):
        raise ValueError("amount must be numeric.")
    normalized = normalize_rect(rect)
    distance = float(amount)
    expanded = {
        "min": [normalized["min"][0] - distance, normalized["min"][1] - distance],
        "max": [normalized["max"][0] + distance, normalized["max"][1] + distance],
    }
    return normalize_rect(expanded, label="expanded")


def _zone_bbox(zone: dict[str, Any], *, index: int) -> dict[str, list[float]]:
    if not isinstance(zone, dict):
        raise ValueError(f"zones[{index}] must be an object.")
    return normalize_rect(zone.get("bbox"), label=f"zones[{index}].bbox")


def _split_rect_by_zone(rect: dict[str, list[float]], zone: dict[str, list[float]]) -> list[dict[str, list[float]]]:
    if not rect_intersects(rect, zone):
        return [rect]

    candidates = [
        {"min": [rect["min"][0], rect["min"][1]], "max": [zone["min"][0], rect["max"][1]]},
        {"min": [zone["max"][0], rect["min"][1]], "max": [rect["max"][0], rect["max"][1]]},
        {
            "min": [max(rect["min"][0], zone["min"][0]), rect["min"][1]],
            "max": [min(rect["max"][0], zone["max"][0]), zone["min"][1]],
        },
        {
            "min": [max(rect["min"][0], zone["min"][0]), zone["max"][1]],
            "max": [min(rect["max"][0], zone["max"][0]), rect["max"][1]],
        },
    ]
    fragments: list[dict[str, list[float]]] = []
    for candidate in candidates:
        if candidate["min"][0] < candidate["max"][0] and candidate["min"][1] < candidate["max"][1]:
            fragments.append(candidate)
    return fragments


def subtract_no_place_zones(boundary: dict[str, Any], zones: list[dict[str, Any]]) -> dict[str, Any]:
    """Subtract bbox no-place zones from a bbox shell using conservative fragments."""

    if not isinstance(boundary, dict) or boundary.get("type", "bbox") != "bbox":
        return {
            "status": "unsupported",
            "rects": [],
            "blocked_reasons": ["subtract_no_place_zones currently supports bbox shell boundaries only."],
        }

    try:
        fragments = [normalize_rect(boundary, label="boundary")]
        normalized_zones = [_zone_bbox(zone, index=index) for index, zone in enumerate(zones)]
    except ValueError as error:
        return {"status": "invalid", "rects": [], "blocked_reasons": [str(error)]}

    blocked_reasons: list[str] = []
    changed = False
    for zone in normalized_zones:
        next_fragments: list[dict[str, list[float]]] = []
        for fragment in fragments:
            split = _split_rect_by_zone(fragment, zone)
            if split != [fragment]:
                changed = True
            next_fragments.extend(split)
        fragments = [fragment for fragment in next_fragments if rect_area(fragment) > 0]
        if not fragments:
            blocked_reasons.append("No placeable rectangle remains after subtracting no-place zones.")
            break

    if blocked_reasons:
        status = "blocked"
    elif not changed:
        status = "pass"
    else:
        status = "partial"
    return {"status": status, "rects": fragments, "blocked_reasons": blocked_reasons}


def path_to_rect_strips(polyline: list[Any], *, width: Number) -> list[dict[str, list[float]]]:
    """Convert an orthogonal path polyline into rectangular strips."""

    if not isinstance(width, (int, float)) or isinstance(width, bool) or width <= 0:
        raise ValueError("width must be > 0.")
    if not isinstance(polyline, list) or len(polyline) < 2:
        raise ValueError("polyline must contain at least two points.")

    points = [_point(point, label="polyline[]") for point in polyline]
    half_width = float(width) / 2
    strips: list[dict[str, list[float]]] = []
    for start, end in zip(points, points[1:]):
        if start == end:
            continue
        if start[1] == end[1]:
            min_x, max_x = sorted([start[0], end[0]])
            strips.append({"min": [min_x, start[1] - half_width], "max": [max_x, start[1] + half_width]})
        elif start[0] == end[0]:
            min_y, max_y = sorted([start[1], end[1]])
            strips.append({"min": [start[0] - half_width, min_y], "max": [start[0] + half_width, max_y]})
        else:
            raise ValueError("path_to_rect_strips supports orthogonal path segments only.")
    if not strips:
        raise ValueError("polyline must contain at least one non-zero segment.")
    return [normalize_rect(strip, label="strip") for strip in strips]


def _distance_to_rect(point: list[float], rect: dict[str, list[float]]) -> float:
    dx = max(rect["min"][0] - point[0], 0, point[0] - rect["max"][0])
    dy = max(rect["min"][1] - point[1], 0, point[1] - rect["max"][1])
    return float(hypot(dx, dy))


def distance_to_opening_or_obstacle(
    point: Any,
    *,
    openings: list[dict[str, Any]] | None = None,
    obstacles: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return conservative nearest distances from a point to openings and obstacles."""

    normalized_point = _point(point, label="point")
    nearest_opening: dict[str, Any] | None = None
    nearest_obstacle: dict[str, Any] | None = None

    for index, opening in enumerate(openings or []):
        center = _point(opening.get("center"), label=f"openings[{index}].center")
        distance = float(hypot(center[0] - normalized_point[0], center[1] - normalized_point[1]))
        if nearest_opening is None or distance < nearest_opening["distance"]:
            nearest_opening = {"id": opening.get("opening_id", opening.get("id", f"opening-{index}")), "distance": distance}

    for index, obstacle in enumerate(obstacles or []):
        bbox = normalize_rect(obstacle.get("bbox"), label=f"obstacles[{index}].bbox")
        distance = _distance_to_rect(normalized_point, bbox)
        if nearest_obstacle is None or distance < nearest_obstacle["distance"]:
            nearest_obstacle = {"id": obstacle.get("obstacle_id", obstacle.get("id", f"obstacle-{index}")), "distance": distance}

    distances = [
        candidate["distance"]
        for candidate in [nearest_opening, nearest_obstacle]
        if candidate is not None
    ]
    return {
        "point": normalized_point,
        "nearest_opening": nearest_opening,
        "nearest_obstacle": nearest_obstacle,
        "min_distance": min(distances) if distances else None,
    }
