"""Map OBJECT_SPEC dictionaries to SYMBOL_SPEC with explicit fallback states."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.symbol_engine.symbol_spec import validate_symbol_spec


SUPPORTED_OBJECT_TYPES = frozenset(
    {"table", "desk", "chair", "sofa", "bed", "cabinet", "shelf", "display_unit"}
)

OBJECT_TYPE_TO_ARCHETYPE: dict[str, str] = {
    "table": "surface",
    "desk": "surface",
    "chair": "seating",
    "sofa": "seating",
    "bed": "sleeping",
    "cabinet": "storage",
    "shelf": "display",
    "display_unit": "display",
}


@dataclass(frozen=True)
class ObjectToSymbolResult:
    symbol_spec: dict[str, Any]
    mapping_status: str
    archetype: str
    fallback_mode: str | None = None
    mapping_reason: str = ""


def _size(spec: dict[str, Any]) -> dict[str, float]:
    raw = spec["size"]
    return {
        "width_mm": float(raw["width"]),
        "depth_mm": float(raw["depth"]),
        "height_mm": float(raw["height"]),
    }


def _inset_mm(width: float, depth: float, ratio: float = 0.06) -> float:
    return max(20.0, min(width, depth) * ratio)


def _component_roles(spec: dict[str, Any]) -> set[str]:
    roles: set[str] = set()
    for component in spec.get("components", []):
        if isinstance(component, dict) and isinstance(component.get("role"), str):
            roles.add(component["role"])
    return roles


def _parts_surface(spec: dict[str, Any], footprint: dict[str, float]) -> list[dict[str, Any]]:
    inset = _inset_mm(footprint["width_mm"], footprint["depth_mm"])
    object_id = spec["object_id"]
    return [
        {"part_id": f"{object_id}-outline", "kind": "outline", "role": "primary_shell"},
        {
            "part_id": f"{object_id}-edge",
            "kind": "inner_offset",
            "role": "edge_readability",
            "params": {"inset_mm": inset},
        },
        {
            "part_id": f"{object_id}-support",
            "kind": "leg_marker",
            "role": "support",
            "params": {"marker_size_mm": min(80.0, footprint["width_mm"] / 8)},
        },
        {
            "part_id": f"{object_id}-facing",
            "kind": "orientation_marker",
            "role": "facing",
            "params": {"span_ratio": 0.35, "axis": "y"},
        },
    ]


def _parts_seating(spec: dict[str, Any], footprint: dict[str, float]) -> list[dict[str, Any]]:
    object_id = spec["object_id"]
    roles = _component_roles(spec)
    parts: list[dict[str, Any]] = [
        {"part_id": f"{object_id}-outline", "kind": "outline", "role": "primary_shell"},
        {
            "part_id": f"{object_id}-facing",
            "kind": "orientation_marker",
            "role": "facing",
            "params": {"span_ratio": 0.3, "axis": "y"},
        },
    ]
    if "back" in roles or spec["type"] == "sofa":
        parts.insert(
            1,
            {
                "part_id": f"{object_id}-seat",
                "kind": "seat_split",
                "role": "seat_zone",
                "params": {"span_ratio": 0.4 if spec["type"] == "sofa" else 0.35},
            },
        )
    else:
        parts.insert(
            1,
            {
                "part_id": f"{object_id}-seat",
                "kind": "seat_split",
                "role": "seat_zone",
                "params": {"span_ratio": 0.38},
            },
        )
    if "arm" in roles and "thick_band" not in {p["kind"] for p in parts}:
        parts.append(
            {
                "part_id": f"{object_id}-arms",
                "kind": "thick_band",
                "role": "arm_band",
                "params": {"band_width_mm": max(60.0, footprint["depth_mm"] * 0.2)},
            },
        )
    return parts


def _parts_sleeping(spec: dict[str, Any], footprint: dict[str, float]) -> list[dict[str, Any]]:
    object_id = spec["object_id"]
    inset = _inset_mm(footprint["width_mm"], footprint["depth_mm"], ratio=0.05)
    return [
        {"part_id": f"{object_id}-outline", "kind": "outline", "role": "primary_shell"},
        {
            "part_id": f"{object_id}-mattress",
            "kind": "inner_offset",
            "role": "mattress",
            "params": {"inset_mm": inset},
        },
        {
            "part_id": f"{object_id}-head",
            "kind": "orientation_marker",
            "role": "headboard",
            "params": {"span_ratio": 0.25, "axis": "y"},
        },
    ]


def _parts_storage(spec: dict[str, Any], footprint: dict[str, float]) -> list[dict[str, Any]]:
    object_id = spec["object_id"]
    roles = _component_roles(spec)
    parts: list[dict[str, Any]] = [
        {"part_id": f"{object_id}-outline", "kind": "outline", "role": "primary_shell"},
    ]
    if roles & {"front_panel", "door", "drawer"} or any("door" in role for role in roles):
        spacing = max(120.0, footprint["height_mm"] / max(len(spec.get("components", [])) or 1, 1))
        parts.append(
            {
                "part_id": f"{object_id}-drawers",
                "kind": "drawer_line",
                "role": "drawer_front",
                "params": {"line_spacing_mm": min(spacing, footprint["height_mm"] * 0.45)},
            }
        )
    else:
        parts.append(
            {
                "part_id": f"{object_id}-shelf-split",
                "kind": "split_line",
                "role": "shelf_band",
                "params": {"axis": "x"},
            }
        )
    return parts


def _parts_display(spec: dict[str, Any], footprint: dict[str, float]) -> list[dict[str, Any]]:
    object_id = spec["object_id"]
    return [
        {"part_id": f"{object_id}-outline", "kind": "outline", "role": "primary_shell"},
        {"part_id": f"{object_id}-bands", "kind": "split_line", "role": "shelf_band", "params": {"axis": "x"}},
        {
            "part_id": f"{object_id}-view",
            "kind": "orientation_marker",
            "role": "viewing",
            "params": {"span_ratio": 0.3, "axis": "y"},
        },
    ]


_ARCHETYPE_PART_BUILDERS = {
    "surface": _parts_surface,
    "seating": _parts_seating,
    "sleeping": _parts_sleeping,
    "storage": _parts_storage,
    "display": _parts_display,
}


def _build_fallback_symbol_spec(
    spec: dict[str, Any],
    *,
    archetype: str,
    mode: str,
    reason: str,
) -> dict[str, Any]:
    footprint = _size(spec)
    object_id = spec["object_id"]
    fallback_policy: dict[str, Any] = {"mode": mode, "reason": reason}
    if mode == "fallback_bbox_placeholder":
        fallback_policy["bbox_fallback_declared"] = True
    return {
        "version": "0.1",
        "symbol_id": f"symbol-{object_id}",
        "object_type": spec["type"],
        "archetype": archetype,
        "view": "plan" if spec.get("drawing_intent") == "plan_preview" else "elevation",
        "footprint": footprint,
        "orientation": {"rotation_deg": 0, "facing": "north"},
        "parts": [{"part_id": f"{object_id}-bbox", "kind": "outline", "role": "placeholder"}],
        "readability_constraints": {
            "min_part_count": 1,
            "requires_non_bbox_parts": False,
            "allows_text_labels": False,
            "allows_dimensions": False,
        },
        "fallback_policy": fallback_policy,
        "evidence": {
            "source_object_id": object_id,
            "mapping_status": "fallback_explicit",
        },
    }


def object_spec_to_symbol_spec(spec: dict[str, Any]) -> ObjectToSymbolResult:
    """Map a validated OBJECT_SPEC to SYMBOL_SPEC or an explicit fallback SYMBOL_SPEC."""

    object_type = str(spec.get("type", ""))
    archetype = OBJECT_TYPE_TO_ARCHETYPE.get(object_type)
    if archetype is None:
        fallback = _build_fallback_symbol_spec(
            spec,
            archetype="surface",
            mode="deferred_unsupported_symbol",
            reason=f"object type `{object_type}` has no symbol archetype mapping",
        )
        return ObjectToSymbolResult(
            symbol_spec=fallback,
            mapping_status="deferred",
            archetype="surface",
            fallback_mode="deferred_unsupported_symbol",
            mapping_reason=fallback["fallback_policy"]["reason"],
        )

    if spec.get("drawing_intent") == "elevation_preview":
        fallback = _build_fallback_symbol_spec(
            spec,
            archetype=archetype,
            mode="fallback_component_preview",
            reason="elevation_preview is deferred to component preview until symbol elevation grammar exists",
        )
        return ObjectToSymbolResult(
            symbol_spec=fallback,
            mapping_status="fallback_explicit",
            archetype=archetype,
            fallback_mode="fallback_component_preview",
            mapping_reason=fallback["fallback_policy"]["reason"],
        )

    footprint = _size(spec)
    builder = _ARCHETYPE_PART_BUILDERS[archetype]
    symbol_spec: dict[str, Any] = {
        "version": "0.1",
        "symbol_id": f"symbol-{spec['object_id']}",
        "object_type": object_type,
        "archetype": archetype,
        "view": "plan",
        "footprint": footprint,
        "orientation": {"rotation_deg": 0, "facing": "north"},
        "parts": builder(spec, footprint),
        "readability_constraints": {
            "min_part_count": 2,
            "requires_non_bbox_parts": True,
            "allows_text_labels": False,
            "allows_dimensions": False,
        },
        "fallback_policy": {
            "mode": "symbol_readable",
            "reason": f"{object_type} mapped to {archetype} archetype grammar",
        },
        "evidence": {
            "source_object_id": spec["object_id"],
            "mapping_status": "symbol_mapped",
        },
    }

    errors = validate_symbol_spec(symbol_spec)
    if errors:
        fallback = _build_fallback_symbol_spec(
            spec,
            archetype=archetype,
            mode="fallback_component_preview",
            reason="symbol mapping failed archetype grammar: " + "; ".join(errors),
        )
        return ObjectToSymbolResult(
            symbol_spec=fallback,
            mapping_status="fallback_explicit",
            archetype=archetype,
            fallback_mode="fallback_component_preview",
            mapping_reason=fallback["fallback_policy"]["reason"],
        )

    return ObjectToSymbolResult(
        symbol_spec=symbol_spec,
        mapping_status="symbol_mapped",
        archetype=archetype,
        fallback_mode="symbol_readable",
        mapping_reason=symbol_spec["fallback_policy"]["reason"],
    )
