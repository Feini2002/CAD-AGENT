"""Summarize simplified entity readback/manual entity lists."""

from __future__ import annotations

from typing import Any


def summarize_entities(entities: list[dict[str, Any]]) -> dict[str, Any]:
    type_counts = {"line_count": 0, "text_count": 0, "dimension_count": 0, "block_count": 0}
    layer_counts: dict[str, int] = {}
    for entity in entities:
        entity_type = entity.get("type")
        if entity_type == "line":
            type_counts["line_count"] += 1
        elif entity_type == "text":
            type_counts["text_count"] += 1
        elif entity_type == "dimension":
            type_counts["dimension_count"] += 1
        elif entity_type == "block":
            type_counts["block_count"] += 1
        layer = str(entity.get("layer", "UNKNOWN"))
        layer_counts[layer] = layer_counts.get(layer, 0) + 1

    layers = [
        {"name": name, "role": "unknown", "entity_count": count}
        for name, count in sorted(layer_counts.items(), key=lambda item: (-item[1], item[0]))
    ]
    return {"layers": layers, "entities_summary": type_counts}
