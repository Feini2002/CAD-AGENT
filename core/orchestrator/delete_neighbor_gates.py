"""Pre-execution delete scope and neighbor protection evidence gates."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from core.geometry_backends.rect2d import normalize_rect, rect_intersects
from core.safety.policy import PREVIEW_LAYER


DELETE_SCOPE_GATE_FILE = "delete_scope_gate.json"
NEIGHBOR_PROTECTION_FILE = "neighbor_protection.json"

DESTRUCTIVE_OPERATIONS = {"delete", "purge", "delete_replace", "cleanup", "clear_previous"}
FORBIDDEN_GLOBAL_SOURCES = {
    "whole_modelspace",
    "whole_codex_preview",
    "global_preview_bbox",
    "all_visible",
    "training_panel",
    "current_screen",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _get(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in payload:
            return payload.get(key)
    return None


def _items(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def _strings(value: Any) -> list[str]:
    return [str(item) for item in _items(value) if str(item)]


def _normalize_operation(value: Any) -> str:
    return str(value or "").strip().casefold().replace("-", "_")


def _is_destructive_operation(operation: str) -> bool:
    if operation in DESTRUCTIVE_OPERATIONS:
        return True
    return any(token in operation for token in DESTRUCTIVE_OPERATIONS)


def _is_nearby_operation(operation: str, request: dict[str, Any]) -> bool:
    if request.get("requiresOccupiedBboxCheck") is True or request.get("requires_occupied_bbox_check") is True:
        return True
    return any(token in operation for token in ["nearby", "adjacent", "next_to"])


def _source_modes(request: dict[str, Any]) -> list[str]:
    modes = _strings(
        _get(
            request,
            "sourceSpec",
            "source_spec",
            "sourceMode",
            "source_mode",
            "sourceBoundaryMode",
            "source_boundary_mode",
            "globalSource",
            "global_source",
        )
    )
    source = request.get("source")
    if isinstance(source, dict):
        modes.extend(_strings(source.get("type")))
    return [mode.casefold() for mode in modes]


def _scope_bbox(request: dict[str, Any], blocking_reasons: list[str]) -> dict[str, list[float]] | None:
    value = _get(request, "scopeBbox", "scope_bbox")
    if value is None:
        return None
    try:
        return normalize_rect(value, label="scope_bbox")
    except ValueError as error:
        blocking_reasons.append(f"scope_bbox invalid: {error}")
        return None


def _target_bbox(request: dict[str, Any], blocking_reasons: list[str]) -> dict[str, list[float]] | None:
    value = _get(request, "targetBbox", "target_bbox", "targetBboxExpected", "target_bbox_expected")
    if value is None:
        return None
    try:
        return normalize_rect(value, label="target_bbox")
    except ValueError as error:
        blocking_reasons.append(f"target bbox invalid: {error}")
        return None


def _entity_bbox(entity: dict[str, Any], *, label: str, blocking_reasons: list[str]) -> dict[str, list[float]] | None:
    try:
        return normalize_rect(entity.get("bbox"), label=label)
    except ValueError as error:
        blocking_reasons.append(f"{label} invalid: {error}")
        return None


def _entity_handle(entity: dict[str, Any], index: int) -> str:
    return str(entity.get("handle") or entity.get("Handle") or f"entity-{index}")


def _entity_type(entity: dict[str, Any]) -> str:
    return str(entity.get("entityType") or entity.get("entity_type") or entity.get("type") or "")


def _entity_zone(entity: dict[str, Any]) -> str:
    return str(entity.get("zone") or entity.get("zoneId") or entity.get("zone_id") or "")


def _zone_id(zone: dict[str, Any], index: int) -> str:
    return str(zone.get("zoneId") or zone.get("zone_id") or zone.get("id") or zone.get("name") or f"zone-{index}")


def _zone_bbox(zone: dict[str, Any], *, label: str, blocking_reasons: list[str]) -> dict[str, list[float]] | None:
    try:
        value = zone.get("bbox") if "bbox" in zone else zone
        return normalize_rect(value, label=label)
    except ValueError as error:
        blocking_reasons.append(f"{label} invalid: {error}")
        return None


def _victim_preview(
    request: dict[str, Any],
    *,
    blocking_reasons: list[str],
) -> list[dict[str, Any]]:
    preview: list[dict[str, Any]] = []
    victims = _items(_get(request, "victimEntities", "victim_entities", "victims", "victimSetPreview"))
    for index, item in enumerate(victims):
        if not isinstance(item, dict):
            blocking_reasons.append(f"victim[{index}] must be an object")
            continue
        bbox = _entity_bbox(item, label=f"victim[{index}].bbox", blocking_reasons=blocking_reasons)
        preview.append(
            {
                "handle": _entity_handle(item, index),
                "layer": str(item.get("layer") or item.get("Layer") or ""),
                "bbox": bbox,
                "entityType": _entity_type(item),
                "zone": _entity_zone(item),
            }
        )
    return preview


def _protected_zone_hits(
    victim_set: list[dict[str, Any]],
    zones: list[Any],
    *,
    blocking_reasons: list[str],
) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for zone_index, raw_zone in enumerate(zones):
        if not isinstance(raw_zone, dict):
            blocking_reasons.append(f"protected_zones[{zone_index}] must be an object")
            continue
        zone_name = _zone_id(raw_zone, zone_index)
        zone_bbox = _zone_bbox(raw_zone, label=f"protected_zones[{zone_index}].bbox", blocking_reasons=blocking_reasons)
        if zone_bbox is None:
            continue
        for victim in victim_set:
            victim_bbox = victim.get("bbox")
            if isinstance(victim_bbox, dict) and rect_intersects(victim_bbox, zone_bbox):
                handle = str(victim["handle"])
                hits.append({"handle": handle, "zone": zone_name})
                blocking_reasons.append(f"victim {handle} intersects protected zone {zone_name}")
    return hits


def build_delete_scope_gate(request: dict[str, Any]) -> dict[str, Any]:
    """Build a conservative delete-scope report without touching CAD."""

    blocking_reasons: list[str] = []
    checked: list[str] = []
    not_checked: list[str] = []
    operation = _normalize_operation(_get(request, "operation", "intent", "task"))
    destructive = _is_destructive_operation(operation)
    target_handles = _strings(_get(request, "targetHandles", "target_handles"))
    scope_bbox = _scope_bbox(request, blocking_reasons)
    target_layer = str(_get(request, "targetLayer", "target_layer", "requestedLayer", "requested_layer") or "")

    if destructive:
        if not target_handles and scope_bbox is None:
            blocking_reasons.append("delete scope missing: target_handles or scope_bbox required")
            not_checked.append("delete_scope")
        else:
            checked.append("delete_scope=declared")
        if target_layer != PREVIEW_LAYER:
            blocking_reasons.append(f"target layer must be {PREVIEW_LAYER}")
            not_checked.append(f"targetLayer={PREVIEW_LAYER}")
        else:
            checked.append(f"targetLayer={PREVIEW_LAYER}")
    else:
        checked.append("non_destructive_operation")

    global_cleanup_authorized = (
        request.get("userAuthorizedGlobalCleanup") is True
        or request.get("user_authorized_global_cleanup") is True
    )
    task_is_global_cleanup = request.get("taskIsGlobalCleanup") is True or request.get("task_is_global_cleanup") is True
    for mode in _source_modes(request):
        if mode not in FORBIDDEN_GLOBAL_SOURCES:
            continue
        if global_cleanup_authorized and task_is_global_cleanup:
            checked.append(f"global source {mode} explicitly authorized")
        else:
            blocking_reasons.append(f"global source {mode} forbidden")

    victim_set = _victim_preview(request, blocking_reasons=blocking_reasons)
    if destructive:
        if not victim_set:
            blocking_reasons.append("victim set preview missing")
            not_checked.append("victim_set_preview")
        else:
            checked.append(f"victim_set_preview={len(victim_set)}")

    target_handle_set = set(target_handles)
    for victim in victim_set:
        handle = str(victim["handle"])
        bbox = victim.get("bbox")
        if target_handle_set and handle not in target_handle_set:
            blocking_reasons.append(f"victim {handle} outside target_handles")
        if scope_bbox is not None and isinstance(bbox, dict) and not rect_intersects(scope_bbox, bbox):
            blocking_reasons.append(f"victim {handle} outside scope_bbox")

    protected_hits = _protected_zone_hits(
        victim_set,
        _items(_get(request, "protectedZones", "protected_zones")),
        blocking_reasons=blocking_reasons,
    )
    adjacent_count = len(_items(_get(request, "adjacentZones", "adjacent_zones")))
    if adjacent_count:
        checked.append(f"adjacent_zones_checked={adjacent_count}")

    status = "pass" if not blocking_reasons else "fail"
    return {
        "schemaVersion": "delete-scope-gate/v1",
        "status": status,
        "delete_scope_gate": status,
        "operation": operation,
        "mayExecuteCad": status == "pass",
        "savedCurrentDwg": False,
        "targetLayer": target_layer,
        "scope": {
            "targetHandles": target_handles,
            "scopeBbox": scope_bbox,
            "sourceModes": _source_modes(request),
        },
        "victimSetPreview": victim_set,
        "protectedZoneHits": protected_hits,
        "blockingReasons": blocking_reasons,
        "checked": checked,
        "notChecked": sorted(set(not_checked)),
        "generatedAt": _utc_now(),
        "writer": "core.orchestrator.delete_neighbor_gates",
    }


def _bbox_equal(first: dict[str, list[float]], second: dict[str, list[float]], *, tolerance: float) -> bool:
    return all(
        abs(first[key][index] - second[key][index]) <= tolerance
        for key in ["min", "max"]
        for index in [0, 1]
    )


def _entities_by_handle(
    entities: list[Any],
    *,
    label: str,
    blocking_reasons: list[str],
) -> dict[str, dict[str, Any]]:
    by_handle: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(entities):
        if not isinstance(item, dict):
            blocking_reasons.append(f"{label}[{index}] must be an object")
            continue
        handle = _entity_handle(item, index)
        bbox = _entity_bbox(item, label=f"{label}[{index}].bbox", blocking_reasons=blocking_reasons)
        by_handle[handle] = {
            "handle": handle,
            "layer": str(item.get("layer") or item.get("Layer") or ""),
            "bbox": bbox,
            "entityType": _entity_type(item),
            "zone": _entity_zone(item),
        }
    return by_handle


def _occupied_bbox_collisions(
    target_bbox: dict[str, list[float]] | None,
    occupied: list[Any],
    *,
    blocking_reasons: list[str],
) -> list[dict[str, Any]]:
    if target_bbox is None:
        return []
    collisions: list[dict[str, Any]] = []
    for index, item in enumerate(occupied):
        if not isinstance(item, dict):
            blocking_reasons.append(f"occupiedBboxes[{index}] must be an object")
            continue
        bbox = _entity_bbox(item, label=f"occupiedBboxes[{index}].bbox", blocking_reasons=blocking_reasons)
        if bbox is None or not rect_intersects(target_bbox, bbox):
            continue
        handle = _entity_handle(item, index)
        collision = {
            "handle": handle,
            "layer": str(item.get("layer") or item.get("Layer") or ""),
            "bbox": bbox,
            "zone": _entity_zone(item),
        }
        collisions.append(collision)
        blocking_reasons.append(f"target bbox collides with occupied bbox {handle}")
    return collisions


def build_neighbor_protection_gate(request: dict[str, Any]) -> dict[str, Any]:
    """Build an occupied-bbox and neighbor readback-diff report without writing CAD."""

    blocking_reasons: list[str] = []
    checked: list[str] = []
    not_checked: list[str] = []
    operation = _normalize_operation(_get(request, "operation", "intent", "task"))
    nearby = _is_nearby_operation(operation, request)
    target_bbox = _target_bbox(request, blocking_reasons)
    occupied = _items(_get(request, "occupiedBboxes", "occupied_bboxes", "obstacles", "visibleObstacles"))

    collisions: list[dict[str, Any]] = []
    if nearby:
        if target_bbox is None:
            blocking_reasons.append("target bbox missing for nearby placement")
            not_checked.append("target_bbox")
        if not occupied:
            blocking_reasons.append("occupied bbox check missing")
            not_checked.append("occupied_bbox_check")
        else:
            checked.append(f"occupied_bbox_check={len(occupied)}")
            collisions = _occupied_bbox_collisions(target_bbox, occupied, blocking_reasons=blocking_reasons)
            if not collisions and target_bbox is not None:
                checked.append("occupied_bbox_collision=none")

    before_raw = _items(_get(request, "neighborBefore", "neighbor_before", "beforeNeighbors", "before_neighbors"))
    after_raw_value = _get(request, "neighborAfter", "neighbor_after", "afterNeighbors", "after_neighbors")
    after_raw = _items(after_raw_value)
    missing_handles: list[str] = []
    changed_bboxes: list[dict[str, Any]] = []
    if before_raw or after_raw_value is not None:
        if before_raw and after_raw_value is None:
            blocking_reasons.append("neighbor readback after missing")
            not_checked.append("neighbor_readback_diff")
        else:
            before = _entities_by_handle(before_raw, label="neighborBefore", blocking_reasons=blocking_reasons)
            after = _entities_by_handle(after_raw, label="neighborAfter", blocking_reasons=blocking_reasons)
            tolerance = float(_get(request, "bboxTolerance", "bbox_tolerance") or 1e-6)
            for handle, before_entity in before.items():
                after_entity = after.get(handle)
                if after_entity is None:
                    missing_handles.append(handle)
                    blocking_reasons.append(f"neighbor {handle} missing after execution")
                    continue
                before_bbox = before_entity.get("bbox")
                after_bbox = after_entity.get("bbox")
                if isinstance(before_bbox, dict) and isinstance(after_bbox, dict):
                    if not _bbox_equal(before_bbox, after_bbox, tolerance=tolerance):
                        changed_bboxes.append({"handle": handle, "before": before_bbox, "after": after_bbox})
                        blocking_reasons.append(f"neighbor {handle} bbox changed after execution")
            checked.append("neighbor_readback_diff=checked")

    status = "pass" if not blocking_reasons else "fail"
    return {
        "schemaVersion": "neighbor-protection-gate/v1",
        "status": status,
        "neighbor_protection": status,
        "operation": operation,
        "mayExecuteCad": status == "pass",
        "savedCurrentDwg": False,
        "targetBbox": target_bbox,
        "collisions": collisions,
        "neighborDiff": {
            "missingHandles": missing_handles,
            "changedBboxes": changed_bboxes,
        },
        "blockingReasons": blocking_reasons,
        "checked": checked,
        "notChecked": sorted(set(not_checked)),
        "generatedAt": _utc_now(),
        "writer": "core.orchestrator.delete_neighbor_gates",
    }


def write_delete_scope_gate(run_dir: str | Path, request: dict[str, Any]) -> dict[str, Any]:
    """Write ``cad_reports/delete_scope_gate.json`` for a run package."""

    run_dir = Path(run_dir)
    report = build_delete_scope_gate(request)
    _write_json(run_dir / "cad_reports" / DELETE_SCOPE_GATE_FILE, report)
    return report


def write_neighbor_protection_gate(run_dir: str | Path, request: dict[str, Any]) -> dict[str, Any]:
    """Write ``cad_reports/neighbor_protection.json`` for a run package."""

    run_dir = Path(run_dir)
    report = build_neighbor_protection_gate(request)
    _write_json(run_dir / "cad_reports" / NEIGHBOR_PROTECTION_FILE, report)
    return report
