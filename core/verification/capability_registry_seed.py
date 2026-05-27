"""Build the V-PROOF-01 CAD capability registry seed from existing repo inventories."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.verification.capability_registry_seed_common import (
    PREVIEW_SAFETY,
    REGISTRY_OUTPUT,
    _domain_draw_object_rows,
    _fitout_catalog_rows,
    _intent_rows,
    _object_catalog_rows,
    _preview_cad_case,
    _primitive_rows,
    _slug,
)
from core.verification.capability_registry_seed_extended import (
    _benchmark_rows,
    _block_insert_variants,
    _block_library_rows,
    _component_role_rows,
    _composition_rows,
    _core_capability_rows,
    _regression_manifest_rows,
    _scene_rows,
    _symbol_rows,
)

def build_seed_registry() -> dict[str, Any]:
    capabilities: list[dict[str, Any]] = []
    for builder in (
        _intent_rows,
        _primitive_rows,
        _domain_draw_object_rows,
        _object_catalog_rows,
        _fitout_catalog_rows,
        _composition_rows,
        _symbol_rows,
        _core_capability_rows,
        _scene_rows,
        _benchmark_rows,
        _regression_manifest_rows,
        _block_library_rows,
        _component_role_rows,
        _block_insert_variants,
    ):
        capabilities.extend(builder())

    deduped: dict[str, dict[str, Any]] = {}
    for row in capabilities:
        capability_id = str(row["capability_id"])
        if capability_id in deduped:
            raise ValueError(f"Duplicate capability_id while seeding: {capability_id}")
        if row.get("claim_level") == "deferred" and not row.get("deferred_reason"):
            row["deferred_reason"] = "Deferred CAD proof; link cad_case and RCAD report in V-PROOF-03."
        if row.get("claim_level") in {"smoke", "verified", "showcase"}:
            if row.get("cad_case", {}).get("case_kind") in {None, "", "none"}:
                row["cad_case"] = _preview_cad_case(case_kind="benchmark_case", requires_real_cad=False)
        deduped[capability_id] = row

    return {
        "version": "0.1",
        "registry_id": "cad-capability-registry-seed-v1",
        "description": "V-PROOF-01 seed registry: intents, primitives, objects, symbols, compositions, benchmarks, and RCAD manifest cases. Mostly none/deferred/smoke; verified rows require V-PROOF-03 backfill.",
        "updated_at": "2026-05-27",
        "capabilities": list(deduped.values()),
    }


def write_seed_registry(path: Path | None = None) -> Path:
    target = path or REGISTRY_OUTPUT
    target.parent.mkdir(parents=True, exist_ok=True)
    registry = build_seed_registry()
    target.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target
