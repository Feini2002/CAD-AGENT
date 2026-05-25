"""No-dependency validation helpers for orthogonal polygons."""

from __future__ import annotations

from typing import Any


def _point(value: Any, *, label: str) -> list[float]:
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"{label} must be a 2D point.")
    if not all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in value):
        raise ValueError(f"{label} must contain numeric coordinates.")
    return [float(value[0]), float(value[1])]


def _bbox(points: list[list[float]]) -> dict[str, list[float]]:
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return {"min": [min(xs), min(ys)], "max": [max(xs), max(ys)]}


def _area(points: list[list[float]]) -> float:
    total = 0.0
    for start, end in zip(points, points[1:]):
        total += start[0] * end[1] - end[0] * start[1]
    return abs(total) / 2


def _is_between(value: float, start: float, end: float) -> bool:
    low, high = sorted([start, end])
    return low <= value <= high


def _segment_intersects(
    first: tuple[list[float], list[float]],
    second: tuple[list[float], list[float]],
) -> bool:
    a, b = first
    c, d = second
    first_horizontal = a[1] == b[1]
    second_horizontal = c[1] == d[1]

    if first_horizontal and not second_horizontal:
        return _is_between(c[0], a[0], b[0]) and _is_between(a[1], c[1], d[1])
    if not first_horizontal and second_horizontal:
        return _is_between(a[0], c[0], d[0]) and _is_between(c[1], a[1], b[1])
    if first_horizontal and second_horizontal and a[1] == c[1]:
        return max(min(a[0], b[0]), min(c[0], d[0])) <= min(max(a[0], b[0]), max(c[0], d[0]))
    if not first_horizontal and not second_horizontal and a[0] == c[0]:
        return max(min(a[1], b[1]), min(c[1], d[1])) <= min(max(a[1], b[1]), max(c[1], d[1]))
    return False


def _has_self_intersection(points: list[list[float]]) -> bool:
    segments = list(zip(points, points[1:]))
    last_index = len(segments) - 1
    for left_index, left_segment in enumerate(segments):
        for right_index, right_segment in enumerate(segments[left_index + 1 :], start=left_index + 1):
            if abs(left_index - right_index) <= 1:
                continue
            if left_index == 0 and right_index == last_index:
                continue
            if _segment_intersects(left_segment, right_segment):
                return True
    return False


def validate_orthogonal_polygon(points: list[Any]) -> dict[str, Any]:
    """Validate a closed orthogonal polygon and return structured geometry data."""

    errors: list[str] = []
    try:
        normalized = [_point(point, label="points[]") for point in points]
    except ValueError as error:
        return {"status": "fail", "errors": [str(error)], "area": None, "bbox": None}

    if len(normalized) < 4:
        errors.append("Orthogonal polygon must contain at least 4 points.")
    if normalized and normalized[0] != normalized[-1]:
        errors.append("Orthogonal polygon must be closed.")

    for index, (start, end) in enumerate(zip(normalized, normalized[1:])):
        if start == end:
            errors.append(f"Segment {index} has zero length.")
        if start[0] != end[0] and start[1] != end[1]:
            errors.append(f"Segment {index} must be horizontal or vertical.")

    if not errors and _has_self_intersection(normalized):
        errors.append("Orthogonal polygon contains self-intersection.")

    valid = not errors
    return {
        "status": "pass" if valid else "fail",
        "errors": errors,
        "area": _area(normalized) if valid else None,
        "bbox": _bbox(normalized) if normalized else None,
    }
