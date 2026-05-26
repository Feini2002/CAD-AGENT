"""Read-only DWG / ModelSpace entity summary (BETA-DRAWING-READ-01)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.verification.inspect_dwg import normalize_com_entity, snapshot_entities

SUMMARY_VERSION = "0.1"
READ_ONLY_POLICY = {
    "mutate_dwg": False,
    "save_dwg": False,
    "modify_layers": False,
    "write_entities": False,
}
HANDLE_SAMPLE_LIMIT = 20
EMPTY_BBOX = {"min": [0.0, 0.0], "max": [0.0, 0.0]}


def _entity_bbox(entity: dict[str, Any]) -> dict[str, list[float]] | None:
    bbox = entity.get("bbox")
    if isinstance(bbox, dict) and "min" in bbox and "max" in bbox:
        return {"min": list(bbox["min"]), "max": list(bbox["max"])}
    entity_type = str(entity.get("type", ""))
    if entity_type == "line":
        start = entity.get("start_point", [])
        end = entity.get("end_point", [])
        if len(start) >= 2 and len(end) >= 2:
            return {
                "min": [min(float(start[0]), float(end[0])), min(float(start[1]), float(end[1]))],
                "max": [max(float(start[0]), float(end[0])), max(float(start[1]), float(end[1]))],
            }
    return None


def _union_bbox(current: dict[str, list[float]] | None, addition: dict[str, list[float]] | None) -> dict[str, list[float]] | None:
    if addition is None:
        return current
    if current is None:
        return {"min": list(addition["min"]), "max": list(addition["max"])}
    return {
        "min": [min(current["min"][0], addition["min"][0]), min(current["min"][1], addition["min"][1])],
        "max": [max(current["max"][0], addition["max"][0]), max(current["max"][1], addition["max"][1])],
    }


def build_dwg_entity_summary(
    entities: list[dict[str, Any]],
    *,
    source: dict[str, str],
    document_name: str = "",
    limitations: list[str] | None = None,
) -> dict[str, Any]:
    """Aggregate normalized entities into a read-only machine-readable summary."""

    type_counts: dict[str, int] = {}
    layer_map: dict[str, dict[str, Any]] = {}
    handles: list[str] = []
    bbox_union: dict[str, list[float]] | None = None

    for entity in entities:
        if not isinstance(entity, dict):
            continue
        entity_type = str(entity.get("type", "unknown"))
        type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        layer = str(entity.get("layer", "UNKNOWN"))
        if layer not in layer_map:
            layer_map[layer] = {"layer": layer, "entity_count": 0, "type_counts": {}, "bbox_union": None}
        layer_entry = layer_map[layer]
        layer_entry["entity_count"] += 1
        layer_types = layer_entry["type_counts"]
        layer_types[entity_type] = layer_types.get(entity_type, 0) + 1
        entity_bbox = _entity_bbox(entity)
        layer_entry["bbox_union"] = _union_bbox(layer_entry["bbox_union"], entity_bbox)
        bbox_union = _union_bbox(bbox_union, entity_bbox)
        handle = str(entity.get("handle", ""))
        if handle:
            handles.append(handle)

    layer_statistics = []
    for layer in sorted(layer_map.keys()):
        entry = layer_map[layer]
        layer_statistics.append(
            {
                "layer": entry["layer"],
                "entity_count": entry["entity_count"],
                "type_counts": dict(sorted(entry["type_counts"].items())),
                "bbox_union": entry["bbox_union"] or EMPTY_BBOX,
            }
        )

    return {
        "version": SUMMARY_VERSION,
        "read_only": True,
        "source": source,
        "drawing": {"document_name": document_name, "units": "mm"},
        "entity_count": len(entities),
        "handle_count": len(handles),
        "type_counts": dict(sorted(type_counts.items())),
        "layer_statistics": layer_statistics,
        "bbox_union": bbox_union or EMPTY_BBOX,
        "handles_sample": handles[:HANDLE_SAMPLE_LIMIT],
        "limitations": list(limitations or []),
    }


def read_entity_summary_from_fixture(fixture_path: Path) -> dict[str, Any]:
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("entities"), list):
        entities = [item for item in payload["entities"] if isinstance(item, dict)]
        document_name = str(payload.get("document_name", ""))
    elif isinstance(payload, list):
        entities = [item for item in payload if isinstance(item, dict)]
        document_name = ""
    else:
        raise ValueError("fixture must be an entity array or {entities: []} object")
    return build_dwg_entity_summary(
        entities,
        source={"type": "fixture", "path": str(fixture_path)},
        document_name=document_name,
        limitations=["fixture read only; not a live DWG parse"],
    )


def read_active_cad_entity_summary(*, layer: str | None = None) -> dict[str, Any]:
    """Connect to active AutoCAD and summarize ModelSpace (read-only)."""

    from core.cad_io.autocad_com import AutoCADComDriver

    driver = AutoCADComDriver(connect_existing_only=True)
    entities = snapshot_entities(driver, layer=layer)
    document_name = str(getattr(getattr(driver, "doc", None), "Name", ""))
    return build_dwg_entity_summary(
        entities,
        source={"type": "active_cad", "document_name": document_name},
        document_name=document_name,
        limitations=[],
    )


def read_entity_summary_from_driver(driver: Any, *, layer: str | None = None, source_type: str = "driver") -> dict[str, Any]:
    """Test/helper entry: summarize entities from a driver or fake driver."""

    entities = snapshot_entities(driver, layer=layer)
    document_name = str(getattr(getattr(driver, "doc", None), "Name", "test.dwg"))
    return build_dwg_entity_summary(
        entities,
        source={"type": source_type, "document_name": document_name},
        document_name=document_name,
    )
