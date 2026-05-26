"""Created-handle scoped readback analysis for geometry verification."""

from __future__ import annotations

from typing import Any


def normalize_handle_list(handles: object) -> list[str]:
    if not isinstance(handles, list):
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for handle in handles:
        text = str(handle).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        normalized.append(text)
    return normalized


def analyze_created_handle_scope(
    *,
    input_handles: list[str],
    readback_entities: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compare requested created handles against entities returned by scoped readback."""

    handle_set = set(normalize_handle_list(input_handles))
    entity_handles = {
        str(entity.get("handle"))
        for entity in readback_entities
        if isinstance(entity, dict) and entity.get("handle") is not None
    }
    hit_handles = sorted(handle_set & entity_handles)
    miss_handles = sorted(handle_set - entity_handles)
    extra_handles = sorted(entity_handles - handle_set)
    return {
        "input_handles": sorted(handle_set),
        "input_handle_count": len(handle_set),
        "hit_count": len(hit_handles),
        "miss_count": len(miss_handles),
        "extra_entity_count": len(extra_handles),
        "hit_handles": hit_handles,
        "miss_handles": miss_handles,
        "extra_handles": extra_handles,
    }


def created_handle_scope_ok(scope: dict[str, Any]) -> bool:
    return (
        int(scope.get("input_handle_count", 0)) > 0
        and int(scope.get("miss_count", 0)) == 0
        and int(scope.get("extra_entity_count", 0)) == 0
    )


def created_handle_scope_check(scope: dict[str, Any]) -> dict[str, str]:
    ok = created_handle_scope_ok(scope)
    if ok:
        message = (
            f"Scoped readback matches created handles: input={scope['input_handle_count']} "
            f"hit={scope['hit_count']} miss={scope['miss_count']} extra={scope['extra_entity_count']}"
        )
    else:
        message = (
            f"Scoped readback mismatch: input={scope.get('input_handle_count', 0)} "
            f"hit={scope.get('hit_count', 0)} miss={scope.get('miss_handles', [])} "
            f"extra={scope.get('extra_handles', [])}"
        )
    return {
        "name": "created_handles_scope",
        "status": "pass" if ok else "fail",
        "message": message,
    }


def filter_entities_to_created_handles(
    entities: list[dict[str, Any]],
    *,
    input_handles: list[str],
) -> list[dict[str, Any]]:
    handle_set = set(normalize_handle_list(input_handles))
    if not handle_set:
        return []
    return [entity for entity in entities if isinstance(entity, dict) and str(entity.get("handle")) in handle_set]
