"""Load and validate SYMBOL_SPEC / SYMBOL_GRAPH with anti-silent-bbox guards."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.schemas.registry import get_schema_path
from core.schemas.validator import load_json, validate_value


SYMBOL_PART_KINDS = (
    "outline",
    "inner_offset",
    "thick_band",
    "split_line",
    "leg_marker",
    "arc_marker",
    "seat_split",
    "drawer_line",
    "door_swing",
    "clearance_ghost",
    "orientation_marker",
)

ARCHETYPES = ("surface", "seating", "sleeping", "storage", "display", "workstation")

FALLBACK_MODES = (
    "block_preferred",
    "symbol_readable",
    "visual_review_required",
    "fallback_component_preview",
    "fallback_bbox_placeholder",
    "deferred_unsupported_symbol",
)

_BBOX_ONLY_KINDS = frozenset({"outline"})


def _schema_errors(data: dict[str, Any], model_type: str) -> list[str]:
    schema = json.loads(get_schema_path(model_type).read_text(encoding="utf-8"))
    return validate_value(data, schema)


def _part_kinds(parts: list[dict[str, Any]]) -> set[str]:
    kinds: set[str] = set()
    for part in parts:
        if isinstance(part, dict):
            kind = part.get("kind")
            if isinstance(kind, str):
                kinds.add(kind)
    return kinds


def validate_symbol_spec(data: dict[str, Any]) -> list[str]:
    """Validate schema and semantic rules; reject silent undeclared bbox fallback."""

    errors = _schema_errors(data, "symbol_spec")
    if errors:
        return errors

    parts = data.get("parts", [])
    if not isinstance(parts, list):
        return errors

    fallback = data.get("fallback_policy", {})
    if not isinstance(fallback, dict):
        return errors

    mode = str(fallback.get("mode", ""))
    kinds = _part_kinds(parts)
    readability = data.get("readability_constraints", {})
    min_part_count = 1
    requires_non_bbox = False
    if isinstance(readability, dict):
        if isinstance(readability.get("min_part_count"), int):
            min_part_count = max(1, int(readability["min_part_count"]))
        requires_non_bbox = bool(readability.get("requires_non_bbox_parts"))

    if len(parts) < min_part_count:
        errors.append(f"$.parts must contain at least {min_part_count} symbol parts for this spec.")

    if mode == "symbol_readable":
        if len(parts) < 2:
            errors.append("$.parts must contain at least 2 parts when fallback_policy.mode is symbol_readable.")
        if kinds and kinds.issubset(_BBOX_ONLY_KINDS):
            errors.append(
                "$.parts cannot be outline-only when fallback_policy.mode is symbol_readable; "
                "undeclared bbox fallback is not allowed."
            )
        if requires_non_bbox and kinds.issubset(_BBOX_ONLY_KINDS):
            errors.append("$.readability_constraints.requires_non_bbox_parts conflicts with outline-only parts.")

    if mode == "fallback_bbox_placeholder":
        if fallback.get("bbox_fallback_declared") is not True:
            errors.append(
                "$.fallback_policy.bbox_fallback_declared must be true when mode is fallback_bbox_placeholder."
            )
        if not fallback.get("reason"):
            errors.append("$.fallback_policy.reason is required when mode is fallback_bbox_placeholder.")

    if mode == "deferred_unsupported_symbol" and not fallback.get("reason"):
        errors.append("$.fallback_policy.reason is required when mode is deferred_unsupported_symbol.")

    if mode not in {"fallback_bbox_placeholder", "deferred_unsupported_symbol"}:
        if isinstance(data.get("archetype"), str) and data["archetype"] in ARCHETYPES:
            from core.symbol_engine.archetypes import validate_archetype_grammar

            errors.extend(validate_archetype_grammar(data))

    return errors


def validate_symbol_graph(data: dict[str, Any]) -> list[str]:
    errors = _schema_errors(data, "symbol_graph")
    if errors:
        return errors

    nodes = data.get("nodes", [])
    if not isinstance(nodes, list):
        return errors

    node_ids = [node.get("node_id") for node in nodes if isinstance(node, dict)]
    if len(node_ids) != len(set(node_ids)):
        errors.append("$.nodes must use unique node_id values.")

    edges = data.get("edges", [])
    if isinstance(edges, list):
        known = set(node_ids)
        for index, edge in enumerate(edges):
            if not isinstance(edge, dict):
                continue
            for endpoint_key in ("from_node_id", "to_node_id"):
                endpoint = edge.get(endpoint_key)
                if isinstance(endpoint, str) and endpoint not in known:
                    errors.append(f"$.edges[{index}].{endpoint_key} references unknown node_id `{endpoint}`.")

    return errors


def load_symbol_spec(path: Path) -> dict[str, Any]:
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError("SYMBOL_SPEC must be a JSON object.")
    errors = validate_symbol_spec(data)
    if errors:
        raise ValueError("Invalid SYMBOL_SPEC: " + "; ".join(errors))
    return data


def load_symbol_graph(path: Path) -> dict[str, Any]:
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError("SYMBOL_GRAPH must be a JSON object.")
    errors = validate_symbol_graph(data)
    if errors:
        raise ValueError("Invalid SYMBOL_GRAPH: " + "; ".join(errors))
    return data
