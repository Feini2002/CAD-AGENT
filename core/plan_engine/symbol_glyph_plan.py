"""Validation and dry-run helpers for draw_symbol_glyph CAD_PLAN intent."""

from __future__ import annotations

from typing import Any


ALLOWED_GLYPH_PRIMITIVES = {"rectangle", "line", "polyline", "circle", "arc"}
FORBIDDEN_GLYPH_PRIMITIVES = {"text", "dimension"}


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _is_point(value: object) -> bool:
    return isinstance(value, list) and len(value) in (2, 3) and all(isinstance(v, (int, float)) for v in value)


def validate_glyph_primitive(item: dict[str, Any], *, index: int) -> list[str]:
    errors: list[str] = []
    prefix = f"object.glyph_primitives[{index}]"
    _require(bool(item.get("part_id")), f"{prefix}.part_id is required.", errors)
    _require(bool(item.get("kind")), f"{prefix}.kind is required.", errors)
    primitive = item.get("primitive")
    _require(isinstance(primitive, str), f"{prefix}.primitive is required.", errors)
    if isinstance(primitive, str):
        _require(primitive in ALLOWED_GLYPH_PRIMITIVES, f"{prefix}.primitive is not supported.", errors)
        _require(primitive not in FORBIDDEN_GLYPH_PRIMITIVES, f"{prefix}.primitive must not be text or dimension.", errors)

    if primitive == "rectangle":
        _require(_is_point(item.get("corner1")), f"{prefix}.corner1 is required for rectangle.", errors)
        _require(_is_point(item.get("corner2")), f"{prefix}.corner2 is required for rectangle.", errors)
    elif primitive == "line":
        _require(_is_point(item.get("start_point")), f"{prefix}.start_point is required for line.", errors)
        _require(_is_point(item.get("end_point")), f"{prefix}.end_point is required for line.", errors)
    elif primitive == "polyline":
        points = item.get("points")
        _require(isinstance(points, list) and len(points) >= 2, f"{prefix}.points must contain at least 2 points.", errors)
        if isinstance(points, list):
            for point_index, point in enumerate(points):
                _require(_is_point(point), f"{prefix}.points[{point_index}] must be numeric.", errors)
    elif primitive == "circle":
        _require(_is_point(item.get("center")), f"{prefix}.center is required for circle.", errors)
        radius = item.get("radius")
        _require(isinstance(radius, (int, float)) and radius > 0, f"{prefix}.radius must be > 0.", errors)
    elif primitive == "arc":
        _require(_is_point(item.get("center")), f"{prefix}.center is required for arc.", errors)
        radius = item.get("radius")
        _require(isinstance(radius, (int, float)) and radius > 0, f"{prefix}.radius must be > 0.", errors)
        for angle_key in ("start_angle", "end_angle"):
            angle = item.get(angle_key)
            _require(isinstance(angle, (int, float)), f"{prefix}.{angle_key} must be numeric.", errors)

    return errors


def _bbox_from_primitive(item: dict[str, Any]) -> list[float] | None:
    primitive = item.get("primitive")
    if primitive == "rectangle":
        c1 = item.get("corner1")
        c2 = item.get("corner2")
        if _is_point(c1) and _is_point(c2):
            xs = [float(c1[0]), float(c2[0])]
            ys = [float(c1[1]), float(c2[1])]
            return [min(xs), min(ys), max(xs), max(ys)]
    if primitive == "line":
        start = item.get("start_point")
        end = item.get("end_point")
        if _is_point(start) and _is_point(end):
            xs = [float(start[0]), float(end[0])]
            ys = [float(start[1]), float(end[1])]
            return [min(xs), min(ys), max(xs), max(ys)]
    if primitive == "circle" or primitive == "arc":
        center = item.get("center")
        radius = item.get("radius")
        if _is_point(center) and isinstance(radius, (int, float)):
            r = float(radius)
            return [float(center[0]) - r, float(center[1]) - r, float(center[0]) + r, float(center[1]) + r]
    if primitive == "polyline":
        points = item.get("points")
        if isinstance(points, list) and points and all(_is_point(point) for point in points):
            xs = [float(point[0]) for point in points]
            ys = [float(point[1]) for point in points]
            return [min(xs), min(ys), max(xs), max(ys)]
    return None


def validate_draw_symbol_glyph(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    obj = plan.get("object", {})
    drawing = plan.get("drawing", {})
    _require(isinstance(obj, dict), "object must be an object.", errors)
    if not isinstance(obj, dict):
        return errors

    _require(obj.get("type") == "symbol_glyph", "object.type must be 'symbol_glyph'.", errors)
    _require(bool(obj.get("symbol_id")), "object.symbol_id is required.", errors)
    glyphs = obj.get("glyph_primitives")
    _require(isinstance(glyphs, list) and len(glyphs) > 0, "object.glyph_primitives must be a non-empty array.", errors)
    if isinstance(glyphs, list):
        for index, item in enumerate(glyphs):
            if isinstance(item, dict):
                errors.extend(validate_glyph_primitive(item, index=index))
            else:
                errors.append(f"object.glyph_primitives[{index}] must be an object.")

    if drawing.get("include_label"):
        errors.append("drawing.include_label must be false for draw_symbol_glyph.")
    if drawing.get("include_dimensions"):
        errors.append("drawing.include_dimensions must be false for draw_symbol_glyph.")

    return errors


def create_draw_symbol_glyph_dry_run_report(plan: dict[str, Any]) -> dict[str, Any]:
    obj = plan["object"]
    drawing = plan["drawing"]
    glyphs = obj.get("glyph_primitives", [])
    entities: list[dict[str, Any]] = []

    for item in glyphs:
        if not isinstance(item, dict):
            continue
        entity = {
            "type": str(item.get("primitive", "unknown")),
            "layer": drawing["layer"],
            "part_id": item.get("part_id"),
            "kind": item.get("kind"),
        }
        entities.append(entity)

    boxes = [_bbox_from_primitive(item) for item in glyphs if isinstance(item, dict)]
    boxes = [box for box in boxes if box]
    if boxes:
        bbox = [
            min(box[0] for box in boxes),
            min(box[1] for box in boxes),
            max(box[2] for box in boxes),
            max(box[3] for box in boxes),
        ]
    else:
        bbox = [0.0, 0.0, 0.0, 0.0]

    base = plan["placement"]["base_point"]
    if len(base) == 2:
        base = [base[0], base[1], 0]

    human_summary = "\n".join(
        [
            "CAD_PLAN DRY RUN",
            f"- intent: {plan['intent']}",
            f"- symbol_id: {obj.get('symbol_id')}",
            f"- archetype: {obj.get('archetype')}",
            f"- glyph_primitives: {len(entities)}",
            f"- placement: {plan['placement'].get('mode')} at {base}",
            f"- layer: {drawing.get('layer')}",
        ]
    )
    return {
        "version": "0.1",
        "status": "valid",
        "validation_errors": [],
        "intent": plan["intent"],
        "layer": drawing["layer"],
        "bbox": bbox,
        "entities": entities,
        "human_summary": human_summary,
        "evidence_state": "deferred_cad_readback_required",
    }
