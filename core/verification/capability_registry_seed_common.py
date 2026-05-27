"""Build the V-PROOF-01 CAD capability registry seed from existing repo inventories."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from core.capabilities.specs import CAPABILITIES
from core.composition_engine.templates import COMPOSITION_TEMPLATES
from core.plan_engine.validate_plan import ALLOWED_DOMAINS, ALLOWED_INTENTS
from core.verification.evidence_vocabulary import ENTITY_CONTRACTS

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_ROOT = PROJECT_ROOT / "examples" / "benchmarks"
REGISTRY_OUTPUT = PROJECT_ROOT / "examples" / "capability_proof" / "cad_capability_registry.json"

PREVIEW_SAFETY: dict[str, Any] = {
    "layer": "CODEX_PREVIEW",
    "saved_dwg": False,
    "deleted_entities": False,
    "modified_formal_layers": False,
}


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "unknown"


def _preview_cad_case(
    *,
    case_kind: str,
    requires_real_cad: bool,
    plan_path: str | None = None,
    benchmark_suite_path: str | None = None,
    benchmark_case_id: str | None = None,
    manifest_path: str | None = None,
    manifest_case_id: str | None = None,
    entrypoint: str | None = None,
    command: list[str] | None = None,
    output_path: str | None = None,
    workflow_id: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "case_kind": case_kind,
        "requires_real_cad": requires_real_cad,
        "safety": dict(PREVIEW_SAFETY),
    }
    if plan_path:
        payload["plan_path"] = plan_path
    if benchmark_suite_path:
        payload["benchmark_suite_path"] = benchmark_suite_path
    if benchmark_case_id:
        payload["benchmark_case_id"] = benchmark_case_id
    if manifest_path:
        payload["manifest_path"] = manifest_path
    if manifest_case_id:
        payload["manifest_case_id"] = manifest_case_id
    if entrypoint:
        payload["entrypoint"] = entrypoint
    if command:
        payload["command"] = command
    if output_path:
        payload["output_path"] = output_path
    if workflow_id:
        payload["workflow_id"] = workflow_id
    return payload


def _source(source_kind: str, source_path: str, source_key: str | None = None) -> dict[str, str]:
    item = {"source_kind": source_kind, "source_path": source_path}
    if source_key:
        item["source_key"] = source_key
    return item


def _intent_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for intent in sorted(ALLOWED_INTENTS):
        rows.append(
            {
                "capability_id": f"intent.{_slug(intent)}",
                "display_name": f"CAD_PLAN intent {intent}",
                "category": "intent",
                "claim_level": "none",
                "ladder_level": "L0",
                "domain": "generic",
                "intent": intent,
                "notes": ["Structural intent inventory; CAD proof tracked per primitive/object/benchmark row."],
                "source_refs": [_source("documentation", "core/plan_engine/validate_plan.py", intent)],
            }
        )
    return rows


def _primitive_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entity, contract in sorted(ENTITY_CONTRACTS.items()):
        intents = contract.get("intents", [])
        primary_intent = intents[0] if intents else "draw_object"
        status = contract.get("implementation_status", "")
        claim_level = "deferred"
        deferred_reason = (
            f"Primitive {entity} requires cad_capability_probe or CAD_PLAN readback before claim_level=verified."
        )
        if status == "deferred_verification":
            deferred_reason = f"{entity} entity contract is explicitly deferred in Phase R."
        rows.append(
            {
                "capability_id": f"primitive.{_slug(entity)}",
                "display_name": f"CAD primitive {entity}",
                "category": "primitive",
                "claim_level": claim_level,
                "ladder_level": "L1",
                "domain": "generic",
                "intent": primary_intent if primary_intent in ALLOWED_INTENTS else "draw_object",
                "deferred_reason": deferred_reason,
                "cad_case": _preview_cad_case(
                    case_kind="script",
                    requires_real_cad=True,
                    entrypoint="scripts/run_cad_validation.py",
                    command=["scripts/run_cad_validation.py", "--output-dir", "output/validation_runs/{run}/"],
                    output_path="cad_capability_probe.json",
                ),
                "tags": [entity],
                "source_refs": [_source("documentation", "core/verification/evidence_vocabulary.py", entity)],
            }
        )
    return rows


def _domain_draw_object_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for domain in sorted(ALLOWED_DOMAINS):
        rows.append(
            {
                "capability_id": f"domain.{_slug(domain)}.draw_object",
                "display_name": f"draw_object in {domain} domain",
                "category": "intent",
                "claim_level": "deferred",
                "ladder_level": "L1",
                "domain": domain,
                "intent": "draw_object",
                "deferred_reason": "Per-domain CAD readback not yet bound to a single cad_case row.",
                "cad_case": _preview_cad_case(
                    case_kind="cad_plan",
                    requires_real_cad=True,
                    plan_path="examples/plans/draw_test_cabinet.json",
                ),
                "source_refs": [_source("documentation", "core/schemas/cad_plan.schema.json", domain)],
            }
        )
    return rows


def _object_catalog_rows() -> list[dict[str, Any]]:
    defaults = json.loads((PROJECT_ROOT / "libraries" / "objects" / "object_defaults.json").read_text(encoding="utf-8"))
    objects = defaults.get("objects", {})
    rows: list[dict[str, Any]] = []
    for object_type in sorted(objects):
        spec = objects[object_type]
        rows.append(
            {
                "capability_id": f"object.{_slug(object_type)}.draw_object",
                "display_name": f"Parametric {object_type} draw_object",
                "category": "object",
                "claim_level": "deferred",
                "ladder_level": "L1",
                "domain": "generic",
                "intent": "draw_object",
                "object_type": object_type,
                "deferred_reason": "Object-type CAD smoke must link geometry_verified readback (V-PROOF-21).",
                "cad_case": _preview_cad_case(
                    case_kind="cad_plan",
                    requires_real_cad=True,
                    plan_path="examples/plans/draw_test_cabinet.json",
                ),
                "source_refs": [_source("object_catalog", "libraries/objects/object_defaults.json", object_type)],
            }
        )
        rows.append(
            {
                "capability_id": f"object.{_slug(object_type)}.glyph",
                "display_name": f"Symbol glyph fallback for {object_type}",
                "category": "symbol",
                "claim_level": "deferred",
                "ladder_level": "L2",
                "domain": "generic",
                "intent": "draw_symbol_glyph",
                "object_type": object_type,
                "deferred_reason": "Glyph CAD matrix pending V-PROOF-32.",
                "cad_case": _preview_cad_case(case_kind="none", requires_real_cad=False),
                "source_refs": [_source("object_catalog", "libraries/objects/object_defaults.json", object_type)],
            }
        )
    return rows


def _fitout_catalog_rows() -> list[dict[str, Any]]:
    catalog_path = PROJECT_ROOT / "agents" / "commercial_fitout" / "capabilities" / "object_catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for item in catalog.get("objects", []):
        if not isinstance(item, dict):
            continue
        catalog_object_id = str(item.get("catalog_object_id", ""))
        rows.append(
            {
                "capability_id": f"catalog.commercial_fitout.{_slug(catalog_object_id)}",
                "display_name": str(item.get("display_name", catalog_object_id)),
                "category": "object",
                "claim_level": "deferred",
                "ladder_level": "L3",
                "domain": "commercial_fitout",
                "object_type": str(item.get("core_object_type", "")),
                "deferred_reason": "Commercial fitout catalog CAD smoke deferred until C-CFIT / V-PROOF-21.",
                "cad_case": _preview_cad_case(case_kind="none", requires_real_cad=False),
                "tags": list(item.get("subscenes", [])),
                "source_refs": [_source("object_catalog", str(catalog_path.relative_to(PROJECT_ROOT)), catalog_object_id)],
            }
        )
    return rows


