"""Fast current-view nearby drawing for preview-only CAD quick trials."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from core.placement.designer_view_nearby import (
    PREVIEW_LAYER,
    audit_nearby_readback,
    collect_cad_view_context,
    resolve_nearby_placement,
)
from core.verification.inspect_dwg import snapshot_entities_by_handles


DEFAULT_OBJECT_SIZES: dict[str, tuple[float, float]] = {
    "rect": (900.0, 500.0),
    "rectangle": (900.0, 500.0),
    "test_rect": (900.0, 500.0),
    "sofa": (1800.0, 750.0),
    "couch": (1800.0, 750.0),
    "沙发": (1800.0, 750.0),
}
VISUAL_DEICTIC_TOKENS = (
    "截图",
    "图片",
    "图里",
    "图上",
    "这里",
    "这儿",
    "看到",
    "当前视口",
    "当前画面",
    "屏幕",
    "箭头",
    "圈",
    "框",
    "screenshot",
    "image",
    "here",
    "marked",
)
VISUAL_POSITION_TOKENS = (
    "旁边",
    "附近",
    "边上",
    "旁侧",
    "靠近",
    "右边",
    "左边",
    "上方",
    "下方",
    "nearby",
    "beside",
    "adjacent",
    "near",
    "right",
    "left",
    "above",
    "below",
)


def run_quick_nearby_draw(
    driver: Any,
    *,
    phrase: str,
    object_type: str,
    object_name: str | None = None,
    width: float | int | None = None,
    depth: float | int | None = None,
    recent_created_handles: list[str] | None = None,
    visual_context: dict[str, Any] | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Resolve a nearby phrase from the current viewport and draw a small preview object."""

    started = time.perf_counter()
    resolved_width, resolved_depth = _resolve_size(object_type, width=width, depth=depth)
    input_scope = _input_scope(phrase, visual_context=visual_context)
    timings: dict[str, float] = {}

    context_started = time.perf_counter()
    context = collect_cad_view_context(driver, recent_created_handles=recent_created_handles)
    timings["context_seconds"] = _elapsed(context_started)

    placement_started = time.perf_counter()
    resolution = resolve_nearby_placement(
        context,
        phrase=phrase,
        target_size={"width": resolved_width, "depth": resolved_depth},
    )
    resolution = _decorate_resolution_for_input_scope(resolution, input_scope)
    timings["placement_seconds"] = _elapsed(placement_started)

    if resolution.get("status") != "resolved":
        report = {
            "status": resolution.get("status", "blocked"),
            "mode": "quick_trial",
            "task": "quick_nearby_draw",
            "input_scope": input_scope,
            "object": _object_payload(object_type, object_name, resolved_width, resolved_depth),
            "placement_resolution": resolution,
            "created_handle_count": 0,
            "created_handles": [],
            "created_bbox": None,
            "timings": _finish_timings(timings, started),
            "safety": _safety(),
            "evidence_boundary": _evidence_boundary(),
        }
        _write_optional_report(output_dir, report)
        return report

    draw_started = time.perf_counter()
    base = resolution["base_point"]
    created_handles = _draw_preview_object(
        driver,
        object_type=object_type,
        base_point=base,
        width=resolved_width,
        depth=resolved_depth,
    )
    timings["draw_seconds"] = _elapsed(draw_started)

    readback_started = time.perf_counter()
    readback = snapshot_entities_by_handles(driver, created_handles, layer=PREVIEW_LAYER)
    nearby_audit = audit_nearby_readback(resolution, readback_entities=readback)
    timings["readback_seconds"] = _elapsed(readback_started)
    created_bbox = nearby_audit.get("readback_bbox")

    report = {
        "status": "pass" if created_handles and nearby_audit.get("geometry_verified") else "needs_review",
        "mode": "quick_trial",
        "task": "quick_nearby_draw",
        "input_scope": input_scope,
        "object": _object_payload(object_type, object_name, resolved_width, resolved_depth),
        "placement_resolution": resolution,
        "created_handle_count": len(created_handles),
        "created_handles": created_handles,
        "created_bbox": created_bbox,
        "readback_entities": readback,
        "nearby_audit": nearby_audit,
        "timings": _finish_timings(timings, started),
        "safety": _safety(),
        "evidence_boundary": _evidence_boundary(),
    }
    _write_optional_report(output_dir, report)
    return report


def _resolve_size(object_type: str, *, width: float | int | None, depth: float | int | None) -> tuple[float, float]:
    default = DEFAULT_OBJECT_SIZES.get(str(object_type).strip().lower(), DEFAULT_OBJECT_SIZES["rect"])
    resolved_width = float(width) if width is not None else default[0]
    resolved_depth = float(depth) if depth is not None else default[1]
    if resolved_width <= 0 or resolved_depth <= 0:
        raise ValueError("width and depth must be positive numbers.")
    return resolved_width, resolved_depth


def _input_scope(phrase: str, *, visual_context: dict[str, Any] | None) -> dict[str, Any]:
    context = dict(visual_context or {})
    text = str(phrase or "")
    visual_request = bool(context) or _contains_any(text, VISUAL_DEICTIC_TOKENS) or _contains_any(text, VISUAL_POSITION_TOKENS)
    source = str(context.get("source") or ("current_cad_view" if visual_request else "unspecified"))
    scope = {
        "scope_type": "visual_limited" if visual_request else "current_view_limited",
        "visual_request": visual_request,
        "visual_source": source,
        "target_hint": context.get("target_hint"),
        "cad_mapping": context.get("cad_mapping", "current_viewport_focus_anchor"),
        "anchor_policy": "current_viewport_selected_recent_visible_cluster",
        "screenshot_role": "visual_targeting_hint_only" if source in {"user_screenshot", "screenshot", "image"} else "not_provided",
        "checked": ["current_viewport_bbox", "focus_anchor", "created_handles_readback"],
        "not_checked": [
            "eye_tracking",
            "screenshot_pixel_to_cad_transform",
            "formal_user_visual_acceptance",
        ],
    }
    return {key: value for key, value in scope.items() if value is not None}


def _contains_any(text: str, tokens: tuple[str, ...]) -> bool:
    lowered = text.lower()
    for token in tokens:
        haystack = lowered if token.isascii() else text
        needle = token.lower() if token.isascii() else token
        if needle in haystack:
            return True
    return False


def _decorate_resolution_for_input_scope(
    resolution: dict[str, Any],
    input_scope: dict[str, Any],
) -> dict[str, Any]:
    decorated = dict(resolution)
    decorated["input_scope"] = {
        "scope_type": input_scope["scope_type"],
        "visual_source": input_scope["visual_source"],
        "anchor_policy": input_scope["anchor_policy"],
    }
    if input_scope.get("visual_request"):
        checked = list(decorated.get("checked", []))
        if "visual_focus_anchor" not in checked:
            checked.append("visual_focus_anchor")
        decorated["checked"] = checked

        assumptions = list(decorated.get("assumptions", []))
        visual_assumption = (
            "Visual wording or screenshot limits the target to the current CAD view; CAD coordinates still require "
            "viewport, focus-anchor and created-handle readback evidence."
        )
        if visual_assumption not in assumptions:
            assumptions.append(visual_assumption)
        decorated["assumptions"] = assumptions
    return decorated


def _draw_preview_object(
    driver: Any,
    *,
    object_type: str,
    base_point: list[float | int],
    width: float,
    depth: float,
) -> list[str]:
    normalized = str(object_type).strip().lower()
    if normalized in {"sofa", "couch", "沙发"}:
        return _draw_sofa_symbol(driver, base_point=base_point, width=width, depth=depth)
    return _draw_rect_symbol(driver, base_point=base_point, width=width, depth=depth)


def _draw_rect_symbol(driver: Any, *, base_point: list[float | int], width: float, depth: float) -> list[str]:
    x0, y0 = float(base_point[0]), float(base_point[1])
    result = driver.draw_rectangle(
        corner1=[x0, y0, 0],
        corner2=[x0 + width, y0 + depth, 0],
        layer=PREVIEW_LAYER,
        color="yellow",
    )
    return [str(handle) for handle in result.get("handles", []) if handle]


def _draw_sofa_symbol(driver: Any, *, base_point: list[float | int], width: float, depth: float) -> list[str]:
    x0, y0 = float(base_point[0]), float(base_point[1])
    x1, y1 = x0 + width, y0 + depth
    arm = min(170.0, width * 0.12)
    back = min(150.0, depth * 0.22)
    inner_x0 = x0 + arm
    inner_x1 = x1 - arm
    seat_y0 = y0 + depth * 0.18
    seat_y1 = y1 - back - depth * 0.06
    cushion_w = (inner_x1 - inner_x0) / 3.0

    handles: list[str] = []
    handles.extend(_draw_rect_symbol(driver, base_point=[x0, y0, 0], width=width, depth=depth))
    _append_line(driver, handles, x0, y1 - back, x1, y1 - back)
    _append_line(driver, handles, inner_x0, y0, inner_x0, y1 - back)
    _append_line(driver, handles, inner_x1, y0, inner_x1, y1 - back)
    for index in (1, 2):
        x = inner_x0 + cushion_w * index
        _append_line(driver, handles, x, seat_y0, x, seat_y1)
        _append_line(driver, handles, x, y1 - back, x, y1)
    _append_polyline(
        driver,
        handles,
        [
            [inner_x0, y0, 0],
            [(x0 + x1) / 2.0, y0 - min(45.0, depth * 0.06), 0],
            [inner_x1, y0, 0],
        ],
    )
    return handles


def _append_line(driver: Any, handles: list[str], x1: float, y1: float, x2: float, y2: float) -> None:
    result = driver.draw_line(
        start_point=[x1, y1, 0],
        end_point=[x2, y2, 0],
        layer=PREVIEW_LAYER,
        color="cyan",
    )
    handle = result.get("handle")
    if handle:
        handles.append(str(handle))


def _append_polyline(driver: Any, handles: list[str], points: list[list[float]]) -> None:
    result = driver.draw_polyline(points=points, closed=False, layer=PREVIEW_LAYER, color="cyan")
    handle = result.get("handle")
    if handle:
        handles.append(str(handle))


def _object_payload(object_type: str, object_name: str | None, width: float, depth: float) -> dict[str, Any]:
    return {
        "type": object_type,
        "name": object_name or object_type,
        "width": width,
        "depth": depth,
        "layer": PREVIEW_LAYER,
    }


def _elapsed(started: float) -> float:
    return round(time.perf_counter() - started, 6)


def _finish_timings(timings: dict[str, float], started: float) -> dict[str, float]:
    result = dict(timings)
    result["end_to_end_seconds"] = _elapsed(started)
    return result


def _write_optional_report(output_dir: Path | None, report: dict[str, Any]) -> None:
    if output_dir is None:
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "quick_nearby_draw_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _safety() -> dict[str, bool]:
    return {
        "preview_layer_only": True,
        "saved_dwg": False,
        "deleted_entities": False,
        "modified_formal_layers": False,
    }


def _evidence_boundary() -> dict[str, str]:
    return {
        "checked": "current viewport placement, focus anchor, preview-layer created handles and bbox readback",
        "not_checked": "formal CAD deliverable accuracy, object-family mastery, user visual acceptance, table C improvement",
    }
