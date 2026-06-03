"""Lightweight current-DWG block cache for quick visual composite tasks."""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from core.visual_retrieval.cad_block_retrieval import block_candidate_from_entity


CACHE_SCHEMA = "current_dwg_block_cache.v1"


def document_identity_from_driver(driver: Any) -> dict[str, str]:
    doc = getattr(driver, "doc", None)
    return {
        "name": str(getattr(doc, "Name", "")),
        "full_name": str(getattr(doc, "FullName", "")),
    }


def build_block_cache_manifest(
    *,
    entities: list[dict[str, Any]],
    document: dict[str, str],
    source: str,
    snapshot_seconds: float = 0.0,
) -> dict[str, Any]:
    candidates = []
    for entity in entities:
        candidate = block_candidate_from_entity(entity)
        if candidate is None:
            continue
        candidates.append(asdict(candidate))

    return {
        "schema": CACHE_SCHEMA,
        "document": {
            "name": str(document.get("name", "")),
            "full_name": str(document.get("full_name", "")),
        },
        "source": source,
        "created_at_epoch": round(time.time(), 3),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "timings": {
            "snapshot_seconds": round(float(snapshot_seconds), 6),
        },
    }


def build_block_cache_manifest_from_driver(driver: Any) -> dict[str, Any]:
    started = time.perf_counter()
    entities = driver.snapshot_modelspace()
    finished = time.perf_counter()
    return build_block_cache_manifest(
        entities=entities,
        document=document_identity_from_driver(driver),
        source="live_snapshot",
        snapshot_seconds=finished - started,
    )


def cache_matches_document(manifest: dict[str, Any] | None, document: dict[str, str]) -> bool:
    if not isinstance(manifest, dict) or manifest.get("schema") != CACHE_SCHEMA:
        return False
    cached_doc = manifest.get("document")
    if not isinstance(cached_doc, dict):
        return False
    cached_full_name = str(cached_doc.get("full_name", "")).casefold()
    active_full_name = str(document.get("full_name", "")).casefold()
    if cached_full_name and active_full_name:
        return cached_full_name == active_full_name
    return str(cached_doc.get("name", "")).casefold() == str(document.get("name", "")).casefold()


def entities_from_cache_manifest(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    entities: list[dict[str, Any]] = []
    for item in manifest.get("candidates", []):
        if not isinstance(item, dict):
            continue
        source_entity = item.get("source_entity")
        if isinstance(source_entity, dict):
            entities.append(source_entity)
            continue
        bbox = item.get("bbox")
        entities.append(
            {
                "handle": str(item.get("handle", "")),
                "type": "block_reference",
                "block_name": str(item.get("block_name", "")),
                "layer": str(item.get("layer", "")),
                "bbox": bbox if isinstance(bbox, dict) else None,
            }
        )
    return entities


def load_block_cache_manifest(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Block cache manifest must be a JSON object.")
    return value


def write_block_cache_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
