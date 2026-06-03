"""Generic find-target-and-annotate-bbox-dimensions quick task."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from core.visual_retrieval import build_bbox_dimension_plan, execute_dimension_annotation_plan
from core.visual_retrieval.current_dwg_cache import (
    build_block_cache_manifest,
    cache_matches_document,
    document_identity_from_driver,
    entities_from_cache_manifest,
    load_block_cache_manifest,
    write_block_cache_manifest,
)
from core.visual_retrieval.cad_block_retrieval import retrieve_visual_blocks


def run_find_and_annotate_bbox_dimensions(
    driver: Any,
    *,
    query: str,
    visual_hint: str | None = None,
    cache_manifest: dict[str, Any] | None = None,
    cache_path: Path | None = None,
    refresh_cache: bool = False,
    top_k: int = 5,
    execute: bool = True,
) -> dict[str, Any]:
    started = time.perf_counter()
    active_document = document_identity_from_driver(driver)
    resolved_manifest = _load_candidate_cache(
        cache_manifest=cache_manifest,
        cache_path=cache_path,
        active_document=active_document,
        refresh_cache=refresh_cache,
    )

    candidate_source = "cache"
    cache_status = "hit"
    if resolved_manifest is not None:
        entities = entities_from_cache_manifest(resolved_manifest)
    else:
        snapshot_started = time.perf_counter()
        entities = driver.snapshot_modelspace()
        snapshot_finished = time.perf_counter()
        resolved_manifest = build_block_cache_manifest(
            entities=entities,
            document=active_document,
            source="live_snapshot",
            snapshot_seconds=snapshot_finished - snapshot_started,
        )
        if cache_path is not None:
            write_block_cache_manifest(cache_path, resolved_manifest)
        candidate_source = "live_snapshot"
        cache_status = "miss_or_stale"

    ranked = retrieve_visual_blocks(
        query=query,
        visual_hint=visual_hint,
        entities=entities,
        top_k=top_k,
    )
    if ranked.best_match is None:
        return {
            "status": "not_found",
            "candidate_source": candidate_source,
            "cache_status": cache_status,
            "active_document": active_document,
            "retrieval": ranked.to_dict(),
            "timings": {"end_to_end_seconds": round(time.perf_counter() - started, 6)},
        }

    target = ranked.best_match.candidate
    dimension_plan = build_bbox_dimension_plan(target)
    execution = None
    if execute:
        execution = execute_dimension_annotation_plan(driver, dimension_plan)

    finished = time.perf_counter()
    payload: dict[str, Any] = {
        "status": "pass" if execution is None or execution.get("status") == "pass" else "needs_review",
        "task": "find_and_annotate_bbox_dimensions",
        "candidate_source": candidate_source,
        "cache_status": cache_status,
        "active_document": active_document,
        "target": {
            "handle": target.handle,
            "block_name": target.block_name,
            "layer": target.layer,
            "bbox": target.bbox,
            "size": target.size,
            "aspect_ratio": target.aspect_ratio,
            "score": ranked.best_match.score,
            "reasons": ranked.best_match.reasons,
        },
        "retrieval": ranked.to_dict(),
        "action_plan": dimension_plan.to_dict(),
        "cache": {
            "schema": resolved_manifest.get("schema") if isinstance(resolved_manifest, dict) else None,
            "candidate_count": resolved_manifest.get("candidate_count") if isinstance(resolved_manifest, dict) else 0,
            "source": resolved_manifest.get("source") if isinstance(resolved_manifest, dict) else None,
        },
        "timings": {
            "end_to_end_seconds": round(finished - started, 6),
        },
        "safety": {
            "preview_layer_only": True,
            "saved_dwg": False,
            "deleted_entities": False,
            "modified_target_block": False,
            "modified_formal_layers": False,
        },
        "evidence_boundary": {
            "visual": "visual and semantic signals select the candidate",
            "cad": "target size comes from active-DWG bbox facts; created dimensions are verified by readback when executed",
            "not_claimed": "screenshot pixels are not treated as true CAD dimensions",
        },
    }
    if execution is not None:
        payload["execution"] = execution
    return payload


def _load_candidate_cache(
    *,
    cache_manifest: dict[str, Any] | None,
    cache_path: Path | None,
    active_document: dict[str, str],
    refresh_cache: bool,
) -> dict[str, Any] | None:
    if refresh_cache:
        return None
    if cache_manifest is not None and cache_matches_document(cache_manifest, active_document):
        return cache_manifest
    if cache_path is None or not cache_path.exists():
        return None
    try:
        loaded = load_block_cache_manifest(cache_path)
    except (OSError, ValueError):
        return None
    if cache_matches_document(loaded, active_document):
        return loaded
    return None
