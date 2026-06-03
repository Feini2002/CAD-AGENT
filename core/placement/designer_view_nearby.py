"""Resolve "nearby" placement from the designer's current CAD view."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from core.execution.execute_plan import execute_plan_file
from core.geometry_backends.rect2d import normalize_rect, rect_contains, rect_gap, rect_intersects
from core.verification.inspect_dwg import snapshot_entities_by_handles


PREVIEW_LAYER = "CODEX_PREVIEW"
DEFAULT_SPACING_MM = 300.0
MIN_SPACING_MM = 100.0
CLUSTER_SCORE_DOMINANCE_RATIO = 1.25
DIRECTION_KEYWORDS = {
    "right": ("右", "右边", "右侧", "右手", "right", "east"),
    "left": ("左", "左边", "左侧", "left", "west"),
    "top": ("上方", "上面", "上侧", "顶部", "往上", "above", "top", "north"),
    "bottom": ("下方", "下面", "下侧", "底部", "往下", "below", "bottom", "south"),
}
NEARBY_KEYWORDS = ("旁边", "附近", "边上", "旁侧", "靠近", "挨着", "nearby", "beside", "adjacent", "near")


def collect_cad_view_context(
    driver: Any,
    *,
    recent_created_handles: list[str] | None = None,
    preview_layer: str = PREVIEW_LAYER,
    max_entities: int = 200,
) -> dict[str, Any]:
    """Collect the CAD facts needed to interpret "nearby" from the current view."""

    viewport_bbox = _driver_viewport_bbox(driver)
    selected_handles = _driver_selected_handles(driver)
    requested_recent = [str(handle) for handle in recent_created_handles or []]
    all_entities = _snapshot_modelspace(driver)
    recent_entities = _snapshot_handles(driver, requested_recent)
    visible_entities = _visible_entity_summaries(all_entities + recent_entities, viewport_bbox)
    visible_recent = [
        str(entity["handle"])
        for entity in _visible_entity_summaries(recent_entities, viewport_bbox)
        if entity.get("handle")
    ]
    preview_entities = [
        entity for entity in visible_entities if str(entity.get("layer", "")) == preview_layer
    ]

    return {
        "unit": "mm",
        "preview_layer": preview_layer,
        "viewport_bbox": viewport_bbox,
        "selected_handles": [handle for handle in selected_handles if _entity_by_handle(visible_entities, handle)],
        "recent_created_handles": list(dict.fromkeys(visible_recent)),
        "visible_entities_summary": _dedupe_entities(visible_entities)[:max_entities],
        "preview_entities_summary": _dedupe_entities(preview_entities)[:max_entities],
        "capture_policy": {"screenshot_required": False},
    }


def resolve_nearby_placement(
    view_context: dict[str, Any],
    *,
    phrase: str,
    target_size: dict[str, float | int],
    spacing_mm: float = DEFAULT_SPACING_MM,
) -> dict[str, Any]:
    """Resolve a vague nearby phrase into a deterministic base point."""

    phrase_analysis = _phrase_analysis(phrase)
    viewport_raw = view_context.get("viewport_bbox")
    if not isinstance(viewport_raw, dict):
        return {
            "status": "blocked",
            "phrase": phrase,
            "phrase_analysis": phrase_analysis,
            "blocked_reasons": ["viewport_bbox is required for designer-view nearby placement."],
            "checked": [],
            "not_checked": ["nearby placement cannot be proven without the original viewport."],
            "assumptions": [],
        }

    try:
        viewport = normalize_rect(viewport_raw, label="viewport_bbox")
        width = _positive_float(target_size.get("width"), "target_size.width")
        depth = _positive_float(target_size.get("depth"), "target_size.depth")
    except ValueError as error:
        return {
            "status": "blocked",
            "phrase": phrase,
            "phrase_analysis": phrase_analysis,
            "blocked_reasons": [str(error)],
            "checked": [],
            "not_checked": ["nearby placement cannot be resolved with invalid geometry inputs."],
            "assumptions": [],
        }

    entities = _visible_entity_summaries(
        view_context.get("visible_entities_summary", []),
        viewport,
    )
    anchor = _select_anchor(view_context, entities, viewport)
    if anchor is None:
        return {
            "status": "blocked",
            "phrase": phrase,
            "phrase_analysis": phrase_analysis,
            "viewport_bbox_before_draw": viewport,
            "blocked_reasons": ["No visible focus anchor is available in the current viewport."],
            "checked": ["viewport_bbox"],
            "not_checked": ["focus_anchor", "candidate_slots", "created_handles"],
            "assumptions": [],
        }
    if anchor.get("requires_confirmation"):
        return {
            "status": "needs_confirmation",
            "phrase": phrase,
            "phrase_analysis": phrase_analysis,
            "viewport_bbox_before_draw": viewport,
            "anchor_source": anchor["source"],
            "anchor_candidates": anchor.get("candidates", []),
            "blocked_reasons": ["Visible focus is ambiguous; select an object or provide a clearer direction before drawing nearby."],
            "checked": ["viewport_bbox", "visible_focus_candidates"],
            "not_checked": ["focus_anchor", "candidate_slots", "created_handles_readback"],
            "assumptions": ["Designer-view nearby placement needs one current visual focus anchor."],
        }

    directions = _direction_order(phrase)
    obstacles = [
        entity for entity in entities if str(entity.get("handle")) not in set(anchor["handles"])
    ]
    candidate_slots = [
        _candidate_slot(
            direction=direction,
            anchor_bbox=anchor["bbox"],
            viewport=viewport,
            target_width=width,
            target_depth=depth,
            obstacles=obstacles,
            phrase=phrase,
            spacing_mm=spacing_mm,
        )
        for direction in directions
    ]
    viable = [slot for slot in candidate_slots if slot["status"] == "pass"]
    if not viable:
        return {
            "status": "needs_confirmation",
            "phrase": phrase,
            "phrase_analysis": phrase_analysis,
            "viewport_bbox_before_draw": viewport,
            "anchor_source": anchor["source"],
            "anchor_handles": anchor["handles"],
            "anchor_bbox": anchor["bbox"],
            "candidate_slots": candidate_slots,
            "blocked_reasons": ["No nearby slot fits inside the original current viewport without collision."],
            "checked": ["viewport_bbox", "focus_anchor", "candidate_slots"],
            "not_checked": ["created_handles_readback"],
            "assumptions": ["User may need to specify a direction, shrink the object, or allow a new visible area."],
        }

    selected = sorted(viable, key=lambda slot: (-float(slot["score"]), _direction_rank(slot["direction"], phrase)))[0]
    return {
        "status": "resolved",
        "phrase": phrase,
        "phrase_analysis": phrase_analysis,
        "viewport_bbox_before_draw": viewport,
        "anchor_source": anchor["source"],
        "anchor_confidence": anchor.get("confidence", 0.7),
        "anchor_handles": anchor["handles"],
        "anchor_bbox": anchor["bbox"],
        "candidate_slots": candidate_slots,
        "selected_slot": selected,
        "base_point": selected["base_point"],
        "target_bbox_expected": selected["bbox"],
        "checks": {
            "target_in_original_viewport": selected["checks"]["target_in_original_viewport"],
            "near_anchor": selected["checks"]["near_anchor"],
            "collision_free": selected["checks"]["collision_free"],
        },
        "max_nearby_distance": _max_nearby_distance(anchor["bbox"], width, depth),
        "checked": ["viewport_bbox", "focus_anchor", "candidate_slots", "target_bbox_expected"],
        "not_checked": ["created_handles_readback", "user_visual_acceptance", "object_family_mastery"],
        "assumptions": [
            "Nearby means an adjacent candidate slot in the original current viewport.",
            "Screenshot is not required for this geometry proof.",
        ],
    }


def audit_nearby_readback(
    resolution: dict[str, Any],
    *,
    readback_entities: list[dict[str, Any]],
) -> dict[str, Any]:
    """Verify created entities against the pre-draw viewport and anchor."""

    if resolution.get("status") != "resolved":
        return {
            "status": "fail",
            "geometry_verified": False,
            "failure_category": "placement_not_resolved",
            "checks": {
                "created_bbox_readback": False,
                "created_bbox_in_original_viewport": False,
                "created_bbox_near_anchor": False,
            },
            "readback_bbox": None,
        }

    created_bbox = _combined_entity_bbox(readback_entities)
    if created_bbox is None:
        return {
            "status": "fail",
            "geometry_verified": False,
            "failure_category": "created_bbox_readback_missing",
            "checks": {
                "created_bbox_readback": False,
                "created_bbox_in_original_viewport": False,
                "created_bbox_near_anchor": False,
            },
            "readback_bbox": None,
        }

    viewport = normalize_rect(resolution["viewport_bbox_before_draw"], label="viewport_bbox_before_draw")
    anchor_bbox = normalize_rect(resolution["anchor_bbox"], label="anchor_bbox")
    max_distance = float(resolution.get("max_nearby_distance") or _max_nearby_distance(anchor_bbox, 1, 1))
    in_viewport = rect_contains(viewport, created_bbox) or rect_intersects(viewport, created_bbox)
    near_anchor = rect_gap(anchor_bbox, created_bbox) <= max_distance
    geometry_verified = bool(in_viewport and near_anchor)
    return {
        "status": "pass" if geometry_verified else "fail",
        "geometry_verified": geometry_verified,
        "readback_bbox": created_bbox,
        "checks": {
            "created_bbox_readback": True,
            "created_bbox_in_original_viewport": in_viewport,
            "created_bbox_near_anchor": near_anchor,
        },
        "checked": ["created_handles_bbox", "original_viewport", "anchor_distance"],
        "not_checked": ["visual_style_match", "construction_drawing_accuracy", "table_c_improvement"],
    }


def run_nearby_preview_trial(
    driver: Any,
    *,
    phrase: str,
    object_type: str,
    object_name: str,
    width: float | int,
    depth: float | int,
    output_dir: Path | None = None,
    recent_created_handles: list[str] | None = None,
) -> dict[str, Any]:
    """Preview-only quick trial for drawing a simple object in the current-view nearby slot."""

    resolved_output_dir = output_dir or Path("output") / "nearby_preview_trial"
    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    context = collect_cad_view_context(driver, recent_created_handles=recent_created_handles)
    resolution = resolve_nearby_placement(
        context,
        phrase=phrase,
        target_size={"width": width, "depth": depth},
    )
    _write_json(resolved_output_dir / "cad_view_context.json", context)
    _write_json(resolved_output_dir / "placement_resolution_report.json", resolution)
    if resolution.get("status") != "resolved":
        report = {
            "status": resolution.get("status", "blocked"),
            "task": "designer_view_nearby_preview_trial",
            "resolution": resolution,
            "safety": _preview_safety(),
            "evidence_boundary": _evidence_boundary(),
        }
        _write_json(resolved_output_dir / "nearby_preview_trial_report.json", report)
        return report

    plan = _plan_from_resolution(
        resolution,
        object_type=object_type,
        object_name=object_name,
        width=width,
        depth=depth,
    )
    plan_path = resolved_output_dir / "nearby_cad_plan.json"
    _write_json(plan_path, plan)
    execution = execute_plan_file(plan_path, driver=driver, preview_only=True)
    handles = [str(handle) for handle in execution.get("created_handles", []) if handle]
    readback = snapshot_entities_by_handles(driver, handles, layer=PREVIEW_LAYER)
    nearby_audit = audit_nearby_readback(resolution, readback_entities=readback)
    status = "pass" if execution.get("status") == "executed" and nearby_audit["geometry_verified"] else "needs_review"
    report = {
        "status": status,
        "task": "designer_view_nearby_preview_trial",
        "resolution": resolution,
        "cad_plan": str(plan_path),
        "execution": execution,
        "readback_entities": readback,
        "nearby_audit": nearby_audit,
        "safety": _preview_safety(),
        "evidence_boundary": _evidence_boundary(),
    }
    _write_json(resolved_output_dir / "nearby_preview_trial_report.json", report)
    return report


def _driver_viewport_bbox(driver: Any) -> dict[str, Any] | None:
    value = getattr(driver, "current_viewport_bbox", None)
    if callable(value):
        value = value()
    if isinstance(value, dict):
        return value
    for name in ("get_current_viewport_bbox", "get_viewport_bbox"):
        method = getattr(driver, name, None)
        if callable(method):
            try:
                result = method()
            except Exception:
                continue
            if isinstance(result, dict):
                return result
    return None


def _driver_selected_handles(driver: Any) -> list[str]:
    value = getattr(driver, "selected_handles", None)
    if callable(value):
        value = value()
    if isinstance(value, list):
        return [str(item) for item in value]
    method = getattr(driver, "get_selected_handles", None)
    if callable(method):
        try:
            result = method()
        except Exception:
            return []
        if isinstance(result, list):
            return [str(item) for item in result]
    return []


def _snapshot_modelspace(driver: Any) -> list[dict[str, Any]]:
    method = getattr(driver, "snapshot_modelspace", None)
    if not callable(method):
        return []
    try:
        entities = method()
    except TypeError:
        entities = method(layer=None)
    except Exception:
        return []
    return [entity for entity in entities if isinstance(entity, dict)]


def _snapshot_handles(driver: Any, handles: list[str]) -> list[dict[str, Any]]:
    if not handles:
        return []
    method = getattr(driver, "snapshot_handles", None)
    if callable(method):
        try:
            entities = method(handles=handles)
        except Exception:
            return []
        return [entity for entity in entities if isinstance(entity, dict)]
    return []


def _visible_entity_summaries(
    entities: Any,
    viewport: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    normalized_viewport = None
    if isinstance(viewport, dict):
        try:
            normalized_viewport = normalize_rect(viewport, label="viewport")
        except ValueError:
            normalized_viewport = None
    if not isinstance(entities, list):
        return result
    for entity in entities:
        if not isinstance(entity, dict):
            continue
        bbox = _entity_bbox(entity)
        if bbox is None:
            continue
        if normalized_viewport is not None and not rect_intersects(normalized_viewport, bbox):
            continue
        summary = {
            "handle": str(entity.get("handle", "")),
            "type": str(entity.get("type", entity.get("object_name", "unknown"))),
            "layer": str(entity.get("layer", "")),
            "bbox": bbox,
        }
        if entity.get("block_name"):
            summary["block_name"] = str(entity["block_name"])
        result.append(summary)
    return result


def _dedupe_entities(entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entity in entities:
        key = str(entity.get("handle") or json.dumps(entity.get("bbox"), sort_keys=True))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(entity)
    return deduped


def _entity_by_handle(entities: list[dict[str, Any]], handle: str) -> dict[str, Any] | None:
    for entity in entities:
        if str(entity.get("handle")) == str(handle):
            return entity
    return None


def _select_anchor(
    view_context: dict[str, Any],
    visible_entities: list[dict[str, Any]],
    viewport: dict[str, list[float]],
) -> dict[str, Any] | None:
    for source, key in (
        ("explicit_target_handles", "target_handles"),
        ("selected_handles", "selected_handles"),
        ("recent_created_handles", "recent_created_handles"),
    ):
        handles = [str(handle) for handle in view_context.get(key, []) if handle]
        entities = [
            entity
            for handle in handles
            if (entity := _entity_by_handle(visible_entities, handle)) is not None
            and rect_intersects(viewport, entity["bbox"])
        ]
        bbox = _combined_entity_bbox(entities)
        if bbox is not None:
            confidence = {"explicit_target_handles": 1.0, "selected_handles": 0.95, "recent_created_handles": 0.85}[source]
            return {
                "source": source,
                "handles": [str(entity.get("handle")) for entity in entities],
                "bbox": bbox,
                "confidence": confidence,
            }

    non_preview = [
        entity
        for entity in visible_entities
        if str(entity.get("layer")) != str(view_context.get("preview_layer", PREVIEW_LAYER))
    ]
    focus_cluster = _select_visual_cluster(non_preview, viewport)
    if focus_cluster is not None:
        return focus_cluster

    preview = [
        entity
        for entity in visible_entities
        if str(entity.get("layer")) == str(view_context.get("preview_layer", PREVIEW_LAYER))
    ]
    preview_cluster = _select_visual_cluster(preview, viewport, source="preview_content_cluster", confidence=0.45)
    if preview_cluster is not None:
        return preview_cluster
    return None


def _select_visual_cluster(
    entities: list[dict[str, Any]],
    viewport: dict[str, list[float]],
    *,
    source: str = "visible_focus_cluster",
    confidence: float = 0.6,
) -> dict[str, Any] | None:
    clusters = _entity_clusters(entities, viewport)
    if not clusters:
        return None
    if len(clusters) == 1:
        cluster = clusters[0]
        return {
            "source": source,
            "handles": cluster["handles"],
            "bbox": cluster["bbox"],
            "confidence": confidence,
        }

    ranked = sorted(clusters, key=lambda cluster: float(cluster["score"]), reverse=True)
    if float(ranked[0]["score"]) < float(ranked[1]["score"]) * CLUSTER_SCORE_DOMINANCE_RATIO:
        return {
            "source": "ambiguous_visible_focus",
            "requires_confirmation": True,
            "candidates": [
                {
                    "handles": cluster["handles"],
                    "bbox": cluster["bbox"],
                    "score": round(float(cluster["score"]), 3),
                }
                for cluster in ranked[:4]
            ],
        }
    cluster = ranked[0]
    return {
        "source": source,
        "handles": cluster["handles"],
        "bbox": cluster["bbox"],
        "confidence": max(0.5, confidence - 0.1),
    }


def _entity_clusters(entities: list[dict[str, Any]], viewport: dict[str, list[float]]) -> list[dict[str, Any]]:
    threshold = _cluster_gap_threshold(viewport)
    clusters: list[dict[str, Any]] = []
    for entity in entities:
        bbox = _entity_bbox(entity)
        if bbox is None:
            continue
        handle = str(entity.get("handle", ""))
        for cluster in clusters:
            if rect_gap(cluster["bbox"], bbox) <= threshold:
                cluster["entities"].append(entity)
                if handle:
                    cluster["handles"].append(handle)
                cluster["bbox"] = _union_bbox(cluster["bbox"], bbox)
                cluster["score"] = _visual_cluster_score(cluster["bbox"], viewport, len(cluster["entities"]))
                break
        else:
            clusters.append(
                {
                    "entities": [entity],
                    "handles": [handle] if handle else [],
                    "bbox": bbox,
                    "score": _visual_cluster_score(bbox, viewport, 1),
                }
            )
    return clusters


def _cluster_gap_threshold(viewport: dict[str, list[float]]) -> float:
    width = float(viewport["max"][0]) - float(viewport["min"][0])
    height = float(viewport["max"][1]) - float(viewport["min"][1])
    return max(250.0, min(width, height) * 0.18)


def _visual_cluster_score(bbox: dict[str, list[float]], viewport: dict[str, list[float]], entity_count: int) -> float:
    width = float(bbox["max"][0]) - float(bbox["min"][0])
    height = float(bbox["max"][1]) - float(bbox["min"][1])
    area = max(1.0, width * height)
    viewport_center = _rect_center(viewport)
    cluster_center = _rect_center(bbox)
    viewport_width = float(viewport["max"][0]) - float(viewport["min"][0])
    viewport_height = float(viewport["max"][1]) - float(viewport["min"][1])
    diagonal = max(1.0, math.hypot(viewport_width, viewport_height))
    center_distance = math.hypot(cluster_center[0] - viewport_center[0], cluster_center[1] - viewport_center[1])
    center_factor = max(0.0, 1.0 - center_distance / diagonal)
    return area * (1.0 + center_factor) + entity_count * 1000.0


def _candidate_slot(
    *,
    direction: str,
    anchor_bbox: dict[str, list[float]],
    viewport: dict[str, list[float]],
    target_width: float,
    target_depth: float,
    obstacles: list[dict[str, Any]],
    phrase: str,
    spacing_mm: float,
) -> dict[str, Any]:
    base = _base_for_direction(direction, anchor_bbox, target_width, target_depth, spacing_mm)
    bbox = {"min": [base[0], base[1]], "max": [base[0] + target_width, base[1] + target_depth]}
    max_nearby = _max_nearby_distance(anchor_bbox, target_width, target_depth)
    failure_reasons: list[str] = []
    target_in_viewport = rect_contains(viewport, bbox)
    if not target_in_viewport:
        failure_reasons.append("target bbox is outside the original current viewport.")
    collision_free = True
    collisions: list[str] = []
    for obstacle in obstacles:
        obstacle_bbox = obstacle.get("bbox")
        if isinstance(obstacle_bbox, dict) and rect_intersects(bbox, obstacle_bbox):
            collision_free = False
            collisions.append(str(obstacle.get("handle", "unknown")))
    if not collision_free:
        failure_reasons.append("target bbox collides with visible geometry: " + ", ".join(collisions))
    distance = rect_gap(anchor_bbox, bbox)
    near_anchor = distance <= max_nearby
    if not near_anchor:
        failure_reasons.append("target bbox is too far from the focus anchor.")
    readable_spacing = distance >= MIN_SPACING_MM or distance == 0
    if not readable_spacing:
        failure_reasons.append("target bbox is too close to the focus anchor.")
    preferred = _direction_matches_phrase(direction, phrase)
    score = 0.0
    if target_in_viewport:
        score += 100.0
    if collision_free:
        score += 100.0
    if near_anchor:
        score += max(0.0, 80.0 - distance / 10.0)
    if readable_spacing:
        score += 20.0
    if preferred:
        score += 35.0
    score -= _direction_rank(direction, phrase) * 0.1
    return {
        "direction": direction,
        "status": "blocked" if failure_reasons else "pass",
        "base_point": [base[0], base[1], 0],
        "bbox": bbox,
        "distance_to_anchor": distance,
        "score": round(score, 3),
        "failure_reasons": failure_reasons,
        "checks": {
            "target_in_original_viewport": target_in_viewport,
            "near_anchor": near_anchor,
            "collision_free": collision_free,
            "readable_spacing": readable_spacing,
            "matches_direction_phrase": preferred,
        },
    }


def _base_for_direction(
    direction: str,
    anchor: dict[str, list[float]],
    width: float,
    depth: float,
    spacing: float,
) -> list[float]:
    x0, y0 = anchor["min"]
    x1, y1 = anchor["max"]
    return {
        "right": [x1 + spacing, y0],
        "left": [x0 - spacing - width, y0],
        "top": [x0, y1 + spacing],
        "bottom": [x0, y0 - spacing - depth],
        "right_top": [x1 + spacing, y1 + spacing],
        "right_bottom": [x1 + spacing, y0 - spacing - depth],
        "left_top": [x0 - spacing - width, y1 + spacing],
        "left_bottom": [x0 - spacing - width, y0 - spacing - depth],
    }[direction]


def _direction_order(phrase: str) -> list[str]:
    normalized = phrase.lower()
    all_directions = ["right", "top", "bottom", "left", "right_top", "right_bottom", "left_top", "left_bottom"]
    bias = _phrase_analysis(phrase).get("direction_bias")
    if bias == "right":
        return ["right", "right_top", "right_bottom", "top", "bottom", "left", "left_top", "left_bottom"]
    if bias == "left":
        return ["left", "left_top", "left_bottom", "top", "bottom", "right", "right_top", "right_bottom"]
    if bias == "top":
        return ["top", "right_top", "left_top", "right", "left", "bottom", "right_bottom", "left_bottom"]
    if bias == "bottom":
        return ["bottom", "right_bottom", "left_bottom", "right", "left", "top", "right_top", "left_top"]
    if bias == "right_top":
        return ["right_top", "right", "top", "right_bottom", "left_top", "bottom", "left", "left_bottom"]
    if bias == "right_bottom":
        return ["right_bottom", "right", "bottom", "right_top", "left_bottom", "top", "left", "left_top"]
    if bias == "left_top":
        return ["left_top", "left", "top", "left_bottom", "right_top", "bottom", "right", "right_bottom"]
    if bias == "left_bottom":
        return ["left_bottom", "left", "bottom", "left_top", "right_bottom", "top", "right", "right_top"]
    if "右" in phrase or "right" in normalized:
        return ["right", "right_top", "right_bottom", "top", "bottom", "left", "left_top", "left_bottom"]
    if "左" in phrase or "left" in normalized:
        return ["left", "left_top", "left_bottom", "top", "bottom", "right", "right_top", "right_bottom"]
    if "上" in phrase or "top" in normalized or "above" in normalized:
        return ["top", "right_top", "left_top", "right", "left", "bottom", "right_bottom", "left_bottom"]
    if "下" in phrase or "bottom" in normalized or "below" in normalized:
        return ["bottom", "right_bottom", "left_bottom", "right", "left", "top", "right_top", "left_top"]
    return all_directions


def _direction_rank(direction: str, phrase: str) -> int:
    return _direction_order(phrase).index(direction)


def _direction_matches_phrase(direction: str, phrase: str) -> bool:
    bias = _phrase_analysis(phrase).get("direction_bias")
    if bias is None:
        pass
    elif "_" in str(bias):
        return direction == bias
    elif bias == "right":
        return direction.startswith("right")
    elif bias == "left":
        return direction.startswith("left")
    elif bias == "top":
        return "top" in direction
    elif bias == "bottom":
        return "bottom" in direction
    if "右" in phrase or "right" in phrase.lower():
        return direction.startswith("right")
    if "左" in phrase or "left" in phrase.lower():
        return direction.startswith("left")
    if "上" in phrase or "top" in phrase.lower() or "above" in phrase.lower():
        return "top" in direction
    if "下" in phrase or "bottom" in phrase.lower() or "below" in phrase.lower():
        return "bottom" in direction
    return True


def _phrase_analysis(phrase: str) -> dict[str, Any]:
    text = str(phrase or "")
    lowered = text.lower()
    matched_directions: set[str] = set()
    matched_tokens: list[str] = []
    for direction, keywords in DIRECTION_KEYWORDS.items():
        for keyword in keywords:
            haystack = lowered if keyword.isascii() else text
            needle = keyword.lower() if keyword.isascii() else keyword
            if needle in haystack:
                matched_directions.add(direction)
                matched_tokens.append(keyword)
                break

    horizontal = "right" if "right" in matched_directions else "left" if "left" in matched_directions else None
    vertical = "top" if "top" in matched_directions else "bottom" if "bottom" in matched_directions else None
    if horizontal and vertical:
        direction_bias = f"{horizontal}_{vertical}"
    else:
        direction_bias = horizontal or vertical

    relation_tokens = [
        keyword
        for keyword in NEARBY_KEYWORDS
        if (keyword.lower() in lowered if keyword.isascii() else keyword in text)
    ]
    relation = "nearby" if relation_tokens or direction_bias else "unspecified"
    confidence = 0.75 if relation == "nearby" else 0.35
    if direction_bias:
        confidence += 0.1
    return {
        "raw": text,
        "relation": relation,
        "direction_bias": direction_bias,
        "matched_tokens": list(dict.fromkeys([*matched_tokens, *relation_tokens])),
        "confidence": round(min(confidence, 0.95), 2),
    }


def _entity_bbox(entity: dict[str, Any]) -> dict[str, list[float]] | None:
    bbox = entity.get("bbox")
    if isinstance(bbox, dict):
        try:
            return normalize_rect(bbox, label="entity.bbox")
        except ValueError:
            return None
    xs: list[float] = []
    ys: list[float] = []
    for key in ("start_point", "end_point", "position", "center", "insertion_point"):
        point = entity.get(key)
        if isinstance(point, list) and len(point) >= 2:
            xs.append(float(point[0]))
            ys.append(float(point[1]))
    points = entity.get("points")
    if isinstance(points, list):
        for point in points:
            if isinstance(point, list) and len(point) >= 2:
                xs.append(float(point[0]))
                ys.append(float(point[1]))
    radius = entity.get("radius")
    center = entity.get("center")
    if isinstance(radius, (int, float)) and isinstance(center, list) and len(center) >= 2:
        return {
            "min": [float(center[0]) - float(radius), float(center[1]) - float(radius)],
            "max": [float(center[0]) + float(radius), float(center[1]) + float(radius)],
        }
    if not xs or not ys:
        return None
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    if min_x == max_x:
        max_x += 1e-6
    if min_y == max_y:
        max_y += 1e-6
    return {"min": [min_x, min_y], "max": [max_x, max_y]}


def _union_bbox(left: dict[str, list[float]], right: dict[str, list[float]]) -> dict[str, list[float]]:
    return {
        "min": [min(float(left["min"][0]), float(right["min"][0])), min(float(left["min"][1]), float(right["min"][1]))],
        "max": [max(float(left["max"][0]), float(right["max"][0])), max(float(left["max"][1]), float(right["max"][1]))],
    }


def _rect_center(bbox: dict[str, list[float]]) -> list[float]:
    return [
        (float(bbox["min"][0]) + float(bbox["max"][0])) / 2.0,
        (float(bbox["min"][1]) + float(bbox["max"][1])) / 2.0,
    ]


def _combined_entity_bbox(entities: list[dict[str, Any]]) -> dict[str, list[float]] | None:
    xs: list[float] = []
    ys: list[float] = []
    for entity in entities:
        bbox = _entity_bbox(entity)
        if bbox is None:
            continue
        xs.extend([bbox["min"][0], bbox["max"][0]])
        ys.extend([bbox["min"][1], bbox["max"][1]])
    if not xs or not ys:
        return None
    return {"min": [min(xs), min(ys)], "max": [max(xs), max(ys)]}


def _max_nearby_distance(anchor_bbox: dict[str, list[float]], width: float, depth: float) -> float:
    anchor = normalize_rect(anchor_bbox, label="anchor_bbox")
    anchor_width = anchor["max"][0] - anchor["min"][0]
    anchor_depth = anchor["max"][1] - anchor["min"][1]
    return max(1200.0, max(anchor_width, anchor_depth, width, depth) * 2.0)


def _positive_float(value: Any, label: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{label} must be a positive number.")
    return float(value)


def _plan_from_resolution(
    resolution: dict[str, Any],
    *,
    object_type: str,
    object_name: str,
    width: float | int,
    depth: float | int,
) -> dict[str, Any]:
    return {
        "version": "0.1",
        "domain": "generic",
        "intent": "draw_object",
        "object": {"type": object_type, "name": object_name, "width": width, "depth": depth},
        "placement": {
            "mode": "absolute",
            "base_point": resolution["base_point"],
            "placement_resolution": resolution,
        },
        "drawing": {"layer": PREVIEW_LAYER, "include_label": False, "include_dimensions": False},
        "confidence": 0.9,
        "needs_confirmation": False,
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _preview_safety() -> dict[str, bool]:
    return {
        "preview_layer_only": True,
        "saved_dwg": False,
        "deleted_entities": False,
        "modified_formal_layers": False,
    }


def _evidence_boundary() -> dict[str, str]:
    return {
        "checked": "current-view nearby placement, deterministic base_point, preview-layer handles and bbox readback",
        "not_checked": "object-family mastery, construction drawing accuracy, user visual acceptance, table C improvement",
    }
