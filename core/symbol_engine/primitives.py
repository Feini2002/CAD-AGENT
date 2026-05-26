"""Render SYMBOL_SPEC parts into safe preview CAD_PLAN glyph primitives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.symbol_engine.symbol_spec import validate_symbol_spec


PREVIEW_LAYER = "CODEX_PREVIEW"

SUPPORTED_PART_KINDS = (
    "outline",
    "inner_offset",
    "thick_band",
    "split_line",
    "leg_marker",
    "arc_marker",
    "orientation_marker",
)


@dataclass(frozen=True)
class FootprintContext:
    x0: float
    y0: float
    width_mm: float
    depth_mm: float
    z: float = 0.0

    @classmethod
    def from_symbol_spec(cls, spec: dict[str, Any], base_point: list[float | int]) -> FootprintContext:
        footprint = spec["footprint"]
        z = float(base_point[2]) if len(base_point) > 2 else 0.0
        return cls(
            x0=float(base_point[0]),
            y0=float(base_point[1]),
            width_mm=float(footprint["width_mm"]),
            depth_mm=float(footprint["depth_mm"]),
            z=z,
        )


def _params(part: dict[str, Any]) -> dict[str, Any]:
    raw = part.get("params")
    return raw if isinstance(raw, dict) else {}


def _point(ctx: FootprintContext, x: float, y: float) -> list[float]:
    return [ctx.x0 + x, ctx.y0 + y, ctx.z]


def _glyph_item(part: dict[str, Any], *, primitive: str, **geometry: object) -> dict[str, Any]:
    item: dict[str, Any] = {
        "part_id": str(part["part_id"]),
        "kind": str(part["kind"]),
        "primitive": primitive,
    }
    item.update(geometry)
    return item


def render_outline(part: dict[str, Any], ctx: FootprintContext) -> list[dict[str, Any]]:
    return [
        _glyph_item(
            part,
            primitive="rectangle",
            corner1=_point(ctx, 0.0, 0.0),
            corner2=_point(ctx, ctx.width_mm, ctx.depth_mm),
        )
    ]


def render_inner_offset(part: dict[str, Any], ctx: FootprintContext) -> list[dict[str, Any]]:
    inset = float(_params(part).get("inset_mm", 40.0))
    inset = min(inset, ctx.width_mm / 4, ctx.depth_mm / 4)
    return [
        _glyph_item(
            part,
            primitive="rectangle",
            corner1=_point(ctx, inset, inset),
            corner2=_point(ctx, ctx.width_mm - inset, ctx.depth_mm - inset),
        )
    ]


def render_thick_band(part: dict[str, Any], ctx: FootprintContext) -> list[dict[str, Any]]:
    band = float(_params(part).get("band_width_mm", 40.0))
    band = min(band, ctx.depth_mm / 2)
    return [
        _glyph_item(
            part,
            primitive="rectangle",
            corner1=_point(ctx, 0.0, ctx.depth_mm - band),
            corner2=_point(ctx, ctx.width_mm, ctx.depth_mm),
        )
    ]


def render_split_line(part: dict[str, Any], ctx: FootprintContext) -> list[dict[str, Any]]:
    axis = str(_params(part).get("axis", "x"))
    if axis == "y":
        x = ctx.width_mm / 2
        return [
            _glyph_item(
                part,
                primitive="line",
                start_point=_point(ctx, x, 0.0),
                end_point=_point(ctx, x, ctx.depth_mm),
            )
        ]
    y = ctx.depth_mm / 2
    return [
        _glyph_item(
            part,
            primitive="line",
            start_point=_point(ctx, 0.0, y),
            end_point=_point(ctx, ctx.width_mm, y),
        )
    ]


def render_leg_marker(part: dict[str, Any], ctx: FootprintContext) -> list[dict[str, Any]]:
    size = float(_params(part).get("marker_size_mm", 60.0))
    size = min(size, ctx.width_mm / 3, ctx.depth_mm / 3)
    inset = size / 2
    cx = ctx.width_mm - inset
    cy = ctx.depth_mm - inset
    return [
        _glyph_item(
            part,
            primitive="circle",
            center=_point(ctx, cx, cy),
            radius=size / 2,
        )
    ]


def render_arc_marker(part: dict[str, Any], ctx: FootprintContext) -> list[dict[str, Any]]:
    radius = float(_params(part).get("marker_size_mm", min(ctx.width_mm, ctx.depth_mm) / 4))
    center_x = ctx.width_mm / 2
    center_y = 0.0
    start_angle = 0.0
    end_angle = 90.0
    return [
        _glyph_item(
            part,
            primitive="arc",
            center=_point(ctx, center_x, center_y),
            radius=radius,
            start_angle=start_angle,
            end_angle=end_angle,
        )
    ]


def render_seat_split(part: dict[str, Any], ctx: FootprintContext) -> list[dict[str, Any]]:
    ratio = float(_params(part).get("span_ratio", 0.35))
    y = ctx.depth_mm * ratio
    return [
        _glyph_item(
            part,
            primitive="line",
            start_point=_point(ctx, 0.0, y),
            end_point=_point(ctx, ctx.width_mm, y),
        )
    ]


def render_drawer_line(part: dict[str, Any], ctx: FootprintContext) -> list[dict[str, Any]]:
    spacing = float(_params(part).get("line_spacing_mm", 200.0))
    spacing = max(spacing, 40.0)
    items: list[dict[str, Any]] = []
    y = spacing
    while y < ctx.depth_mm - spacing * 0.25:
        items.append(
            _glyph_item(
                part,
                primitive="line",
                start_point=_point(ctx, 0.0, y),
                end_point=_point(ctx, ctx.width_mm, y),
            )
        )
        y += spacing
    return items or [
        _glyph_item(
            part,
            primitive="line",
            start_point=_point(ctx, 0.0, ctx.depth_mm / 2),
            end_point=_point(ctx, ctx.width_mm, ctx.depth_mm / 2),
        )
    ]


def render_door_swing(part: dict[str, Any], ctx: FootprintContext) -> list[dict[str, Any]]:
    radius = float(_params(part).get("marker_size_mm", min(ctx.width_mm, ctx.depth_mm) / 3))
    return [
        _glyph_item(
            part,
            primitive="arc",
            center=_point(ctx, 0.0, 0.0),
            radius=radius,
            start_angle=0.0,
            end_angle=90.0,
        )
    ]


def render_orientation_marker(part: dict[str, Any], ctx: FootprintContext) -> list[dict[str, Any]]:
    span_ratio = float(_params(part).get("span_ratio", 0.35))
    axis = str(_params(part).get("axis", "y"))
    span = (ctx.depth_mm if axis == "y" else ctx.width_mm) * span_ratio
    if axis == "y":
        x = ctx.width_mm / 2
        return [
            _glyph_item(
                part,
                primitive="line",
                start_point=_point(ctx, x, ctx.depth_mm * 0.15),
                end_point=_point(ctx, x, ctx.depth_mm * 0.15 + span),
            )
        ]
    y = ctx.depth_mm / 2
    return [
        _glyph_item(
            part,
            primitive="line",
            start_point=_point(ctx, ctx.width_mm * 0.15, y),
            end_point=_point(ctx, ctx.width_mm * 0.15 + span, y),
        )
    ]


_PART_RENDERERS = {
    "outline": render_outline,
    "inner_offset": render_inner_offset,
    "thick_band": render_thick_band,
    "split_line": render_split_line,
    "leg_marker": render_leg_marker,
    "arc_marker": render_arc_marker,
    "seat_split": render_seat_split,
    "drawer_line": render_drawer_line,
    "door_swing": render_door_swing,
    "orientation_marker": render_orientation_marker,
}


def render_symbol_part(part: dict[str, Any], ctx: FootprintContext) -> list[dict[str, Any]]:
    kind = str(part.get("kind", ""))
    renderer = _PART_RENDERERS.get(kind)
    if renderer is None:
        raise ValueError(f"Unsupported symbol part kind for primitive rendering: {kind}")
    return renderer(part, ctx)


def symbol_spec_to_glyph_primitives(
    spec: dict[str, Any],
    *,
    base_point: list[float | int] | None = None,
) -> list[dict[str, Any]]:
    errors = validate_symbol_spec(spec)
    if errors:
        raise ValueError("Invalid SYMBOL_SPEC: " + "; ".join(errors))

    placement = base_point or [0.0, 0.0, 0.0]
    ctx = FootprintContext.from_symbol_spec(spec, placement)
    items: list[dict[str, Any]] = []
    for part in spec.get("parts", []):
        if isinstance(part, dict):
            items.extend(render_symbol_part(part, ctx))
    if not items:
        raise ValueError("SYMBOL_SPEC produced no glyph primitives.")
    return items


def symbol_spec_to_cad_plan(
    spec: dict[str, Any],
    *,
    base_point: list[float | int] | None = None,
    domain: str = "generic",
    layer: str = PREVIEW_LAYER,
    include_label: bool = False,
    include_dimensions: bool = False,
) -> dict[str, Any]:
    """Build a draw_symbol_glyph CAD_PLAN from a SYMBOL_SPEC."""

    if include_label or include_dimensions:
        raise ValueError("Symbol glyph CAD_PLAN must not enable labels or dimensions by default.")

    placement = list(base_point or [0.0, 0.0, 0.0])
    if len(placement) == 2:
        placement.append(0.0)

    return {
        "version": "0.1",
        "domain": domain,
        "intent": "draw_symbol_glyph",
        "object": {
            "type": "symbol_glyph",
            "name": f"{spec.get('object_type', 'object')} {spec.get('archetype', 'symbol')}",
            "symbol_id": spec["symbol_id"],
            "archetype": spec.get("archetype"),
            "glyph_primitives": symbol_spec_to_glyph_primitives(spec, base_point=placement),
        },
        "placement": {"mode": "absolute", "base_point": placement},
        "drawing": {
            "layer": layer,
            "include_label": include_label,
            "include_dimensions": include_dimensions,
        },
        "confidence": 1.0,
        "needs_confirmation": False,
    }
