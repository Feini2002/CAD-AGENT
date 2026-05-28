"""Closed visual-part primitive definitions.

The helpers return neutral primitive dictionaries. CAD execution remains in
``core.execution`` or case scripts so these helpers can be tested without COM.
"""

from __future__ import annotations

from typing import Any


def _line(part_id: str, start: list[float], end: list[float]) -> dict[str, Any]:
    return {
        "part_id": part_id,
        "primitive": "line",
        "start_point": start,
        "end_point": end,
        "closed_component": True,
    }


def _arc(part_id: str, center: list[float], radius: float, start: float, end: float) -> dict[str, Any]:
    return {
        "part_id": part_id,
        "primitive": "arc",
        "center": center,
        "radius": radius,
        "start_angle": start,
        "end_angle": end,
        "closed_component": True,
    }


def rounded_rect_closed(
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    *,
    radius: float,
    part_id: str,
) -> list[dict[str, Any]]:
    """Return four lines and four arcs for a closed rounded rectangle."""

    if x1 <= x0 or y1 <= y0:
        raise ValueError("rounded_rect_closed requires x1 > x0 and y1 > y0")
    r = max(1.0, min(float(radius), (x1 - x0) / 2.2, (y1 - y0) / 2.2))
    return [
        _line(part_id, [x0 + r, y0, 0], [x1 - r, y0, 0]),
        _arc(part_id, [x1 - r, y0 + r, 0], r, 270, 360),
        _line(part_id, [x1, y0 + r, 0], [x1, y1 - r, 0]),
        _arc(part_id, [x1 - r, y1 - r, 0], r, 0, 90),
        _line(part_id, [x1 - r, y1, 0], [x0 + r, y1, 0]),
        _arc(part_id, [x0 + r, y1 - r, 0], r, 90, 180),
        _line(part_id, [x0, y1 - r, 0], [x0, y0 + r, 0]),
        _arc(part_id, [x0 + r, y0 + r, 0], r, 180, 270),
    ]


def pill_horizontal_closed(
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    *,
    part_id: str,
) -> list[dict[str, Any]]:
    """Return a closed horizontal pill shape."""

    width = x1 - x0
    height = y1 - y0
    if width <= height:
        raise ValueError("pill_horizontal requires width > height")
    return rounded_rect_closed(x0, y0, x1, y1, radius=height / 2.0, part_id=part_id)
