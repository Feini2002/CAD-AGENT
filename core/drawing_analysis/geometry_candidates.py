"""Extract wall / door / column / no-place-zone candidates (BETA-DRAWING-READ-02)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from core.drawing_analysis.dwg_read_only import _entity_bbox, build_dwg_entity_summary, read_entity_summary_from_fixture

CANDIDATES_VERSION = "0.1"

_LAYER_HINTS: dict[str, tuple[str, ...]] = {
    "wall": ("wall", "walls", "a-wall", "wall-"),
    "door": ("door", "opening", "open-", "a-door"),
    "column": ("column", "col-", "a-col", "pillar", "struct"),
    "no_place": ("no-place", "noplace", "no_place", "obstacle", "fixed", "no-go"),
}

_BLOCK_NAME_HINTS: dict[str, tuple[str, ...]] = {
    "door": ("door", "opening", "entry"),
    "column": ("col", "column", "pillar"),
    "no_place": ("obstacle", "column", "equipment"),
}


def _layer_token(layer: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", layer.lower()).strip("-")


def _layer_matches_role(layer: str, role: str) -> bool:
    token = _layer_token(layer)
    return any(hint in token for hint in _LAYER_HINTS[role])


def _block_matches_role(block_name: str, role: str) -> bool:
    name = block_name.lower()
    return any(hint in name for hint in _BLOCK_NAME_HINTS.get(role, ()))


def _confidence(*, layer_hit: bool, type_hit: bool, name_hit: bool = False) -> float:
    score = 0.35
    if layer_hit:
        score += 0.4
    if type_hit:
        score += 0.15
    if name_hit:
        score += 0.1
    return min(score, 0.95)


def _segment_from_line(entity: dict[str, Any]) -> dict[str, list[float]] | None:
    start = entity.get("start_point", [])
    end = entity.get("end_point", [])
    if len(start) < 2 or len(end) < 2:
        return None
    return {
        "start": [float(start[0]), float(start[1])],
        "end": [float(end[0]), float(end[1])],
    }


def _candidate(
    *,
    candidate_id: str,
    kind: str,
    entity: dict[str, Any],
    detection_rule: str,
    confidence: float,
    geometry: dict[str, Any],
) -> dict[str, Any]:
    bbox = _entity_bbox(entity) or {"min": [0.0, 0.0], "max": [0.0, 0.0]}
    return {
        "candidate_id": candidate_id,
        "kind": kind,
        "source_handles": [str(entity.get("handle", ""))] if entity.get("handle") else [],
        "layer": str(entity.get("layer", "UNKNOWN")),
        "bbox": bbox,
        "confidence": round(confidence, 2),
        "detection_rule": detection_rule,
        "geometry": geometry,
    }


def extract_geometry_candidates(
    entities: list[dict[str, Any]],
    *,
    summary: dict[str, Any] | None = None,
    source: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Heuristic extraction from normalized entities (optionally aligned with entity summary)."""

    wall_segments: list[dict[str, Any]] = []
    door_openings: list[dict[str, Any]] = []
    columns: list[dict[str, Any]] = []
    no_place_zones: list[dict[str, Any]] = []
    index = 0

    layer_stats = {}
    if summary:
        layer_stats = {item["layer"]: item for item in summary.get("layer_statistics", [])}

    for entity in entities:
        if not isinstance(entity, dict):
            continue
        entity_type = str(entity.get("type", ""))
        layer = str(entity.get("layer", "UNKNOWN"))
        handle = str(entity.get("handle", f"anon-{index}"))
        index += 1
        layer_hint = layer_stats.get(layer, {})
        layer_dominated_by_lines = (
            layer_hint.get("type_counts", {}).get("line", 0) >= 2 if layer_hint else False
        )

        if entity_type == "line" and (_layer_matches_role(layer, "wall") or layer_dominated_by_lines):
            segment = _segment_from_line(entity)
            if segment is None:
                continue
            wall_segments.append(
                _candidate(
                    candidate_id=f"wall-{handle}",
                    kind="wall_segment",
                    entity=entity,
                    detection_rule="layer_wall_or_dominant_line_layer",
                    confidence=_confidence(layer_hit=_layer_matches_role(layer, "wall"), type_hit=True),
                    geometry={"segment": segment},
                )
            )
            continue

        if entity_type == "block_reference":
            block_name = str(entity.get("block_name", ""))
            if _layer_matches_role(layer, "door") or _block_matches_role(block_name, "door"):
                door_openings.append(
                    _candidate(
                        candidate_id=f"door-{handle}",
                        kind="door_opening",
                        entity=entity,
                        detection_rule="layer_or_block_name_door",
                        confidence=_confidence(
                            layer_hit=_layer_matches_role(layer, "door"),
                            type_hit=True,
                            name_hit=_block_matches_role(block_name, "door"),
                        ),
                        geometry={
                            "block_name": block_name,
                            "insertion_point": list(entity.get("insertion_point", [0, 0, 0])[:2]),
                        },
                    )
                )
                continue
            if _layer_matches_role(layer, "column") or _block_matches_role(block_name, "column"):
                columns.append(
                    _candidate(
                        candidate_id=f"column-{handle}",
                        kind="column",
                        entity=entity,
                        detection_rule="layer_or_block_name_column",
                        confidence=_confidence(
                            layer_hit=_layer_matches_role(layer, "column"),
                            type_hit=True,
                            name_hit=_block_matches_role(block_name, "column"),
                        ),
                        geometry={
                            "block_name": block_name,
                            "insertion_point": list(entity.get("insertion_point", [0, 0, 0])[:2]),
                        },
                    )
                )
                continue

        if entity_type in {"polyline", "hatch", "rectangle"} and _layer_matches_role(layer, "no_place"):
            no_place_zones.append(
                _candidate(
                    candidate_id=f"no-place-{handle}",
                    kind="no_place_zone",
                    entity=entity,
                    detection_rule="layer_no_place_geometry",
                    confidence=_confidence(layer_hit=True, type_hit=True),
                    geometry={"entity_type": entity_type},
                )
            )

    return {
        "version": CANDIDATES_VERSION,
        "read_only": True,
        "source": source or {"type": "entities"},
        "entity_summary_ref": {
            "version": summary.get("version") if summary else None,
            "entity_count": summary.get("entity_count") if summary else len(entities),
        },
        "wall_segment_candidates": wall_segments,
        "door_opening_candidates": door_openings,
        "column_candidates": columns,
        "no_place_zone_candidates": no_place_zones,
        "counts": {
            "wall_segments": len(wall_segments),
            "door_openings": len(door_openings),
            "columns": len(columns),
            "no_place_zones": len(no_place_zones),
        },
        "limitations": [
            "heuristic layer/block naming only; not architectural inference",
            "does not emit SHELL_MODEL; human confirmation required (READ-04)",
        ],
    }


def read_geometry_candidates_from_fixture(fixture_path: Path) -> dict[str, Any]:
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("entities"), list):
        entities = [item for item in payload["entities"] if isinstance(item, dict)]
    elif isinstance(payload, list):
        entities = [item for item in payload if isinstance(item, dict)]
    else:
        raise ValueError("fixture must be an entity array or {entities: []} object")
    summary = build_dwg_entity_summary(
        entities,
        source={"type": "fixture", "path": str(fixture_path)},
        document_name=str(payload.get("document_name", "")) if isinstance(payload, dict) else "",
        limitations=["fixture read only"],
    )
    return extract_geometry_candidates(
        entities,
        summary=summary,
        source={"type": "fixture", "path": str(fixture_path)},
    )
