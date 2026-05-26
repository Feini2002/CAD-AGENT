"""Execute draw_symbol_glyph CAD_PLAN primitives on a preview CAD driver."""

from __future__ import annotations

from typing import Any


DEFAULT_GLYPH_COLOR = "cyan"


def expected_readback_type_counts(glyph_primitives: list[dict[str, Any]]) -> dict[str, int]:
    """Map planned glyph primitives to CAD entity type counts after execution."""

    line_count = 0
    circle_count = 0
    polyline_count = 0
    arc_count = 0
    for item in glyph_primitives:
        if not isinstance(item, dict):
            continue
        primitive = str(item.get("primitive", ""))
        if primitive == "rectangle":
            line_count += 4
        elif primitive == "line":
            line_count += 1
        elif primitive == "circle":
            circle_count += 1
        elif primitive == "polyline":
            polyline_count += 1
        elif primitive == "arc":
            arc_count += 1
    counts: dict[str, int] = {}
    if line_count:
        counts["line"] = line_count
    if circle_count:
        counts["circle"] = circle_count
    if polyline_count:
        counts["polyline"] = polyline_count
    if arc_count:
        counts["arc"] = arc_count
    return dict(sorted(counts.items()))


def _collect_handles(result: object) -> list[str]:
    if result is None:
        return []
    if isinstance(result, str):
        return [result]
    if isinstance(result, dict):
        if isinstance(result.get("handles"), list):
            return [str(handle) for handle in result["handles"]]
        if result.get("handle"):
            return [str(result["handle"])]
    if isinstance(result, list):
        return [str(item) for item in result]
    return []


def execute_glyph_primitive(
    driver: Any,
    item: dict[str, Any],
    *,
    layer: str,
    color: str = DEFAULT_GLYPH_COLOR,
) -> list[str]:
    """Draw one glyph primitive and return created handles."""

    primitive = str(item.get("primitive", ""))
    if primitive == "rectangle":
        return _collect_handles(
            driver.draw_rectangle(
                corner1=item["corner1"],
                corner2=item["corner2"],
                layer=layer,
                color=color,
            )
        )
    if primitive == "line":
        return _collect_handles(
            driver.draw_line(
                start_point=item["start_point"],
                end_point=item["end_point"],
                layer=layer,
                color=color,
            )
        )
    if primitive == "polyline":
        return _collect_handles(
            driver.draw_polyline(
                points=item["points"],
                closed=bool(item.get("closed", False)),
                layer=layer,
                color=color,
            )
        )
    if primitive == "circle":
        return _collect_handles(
            driver.draw_circle(
                center=item["center"],
                radius=item["radius"],
                layer=layer,
                color=color,
            )
        )
    if primitive == "arc":
        return _collect_handles(
            driver.draw_arc(
                center=item["center"],
                radius=item["radius"],
                start_angle=item["start_angle"],
                end_angle=item["end_angle"],
                layer=layer,
                color=color,
            )
        )
    raise ValueError(f"Unsupported glyph primitive: {primitive}")
