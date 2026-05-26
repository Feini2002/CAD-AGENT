"""Block / symbol / component / bbox fallback resolution with explicit evidence states."""

from __future__ import annotations

from typing import Any

from core.object_engine.detail_plan import object_spec_to_detail_cad_plans
from core.plan_engine.block_alpha_plan import CONTROLLED_BLOCK_ID, CONTROLLED_BLOCK_NAME, PREVIEW_LAYER
from core.symbol_engine.object_to_symbol import object_spec_to_symbol_spec
from core.symbol_engine.primitives import symbol_spec_to_cad_plan
from core.symbol_engine.readability import build_symbol_readability_report
from core.symbol_engine.symbol_spec import validate_symbol_spec
from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)


FALLBACK_RENDER_TIERS = (
    "block",
    "symbol_glyph",
    "component_preview",
    "bbox_placeholder",
    "deferred",
)

TIER_TO_CAD_INTENT: dict[str, str | None] = {
    "block": "insert_block_alpha",
    "symbol_glyph": "draw_symbol_glyph",
    "component_preview": "draw_object",
    "bbox_placeholder": "draw_object",
    "deferred": None,
}

FALLBACK_MODE_TO_TIER: dict[str, str] = {
    "block_preferred": "block",
    "symbol_readable": "symbol_glyph",
    "visual_review_required": "symbol_glyph",
    "fallback_component_preview": "component_preview",
    "fallback_bbox_placeholder": "bbox_placeholder",
    "deferred_unsupported_symbol": "deferred",
}

TIER_RANK = {tier: index for index, tier in enumerate(FALLBACK_RENDER_TIERS)}

_DETAIL_PREVIEW_TYPES = frozenset({"table", "bed", "chair", "sofa", "desk"})


def tier_evidence_state(tier: str, *, cad_geometry_verified: bool = False) -> str:
    if tier == "deferred":
        return EVIDENCE_DEFERRED_CAD_READBACK
    if cad_geometry_verified:
        from core.verification.evidence_contract import EVIDENCE_READBACK_GEOMETRY_VERIFIED

        return EVIDENCE_READBACK_GEOMETRY_VERIFIED
    return EVIDENCE_DRY_RUN_VALID_PLAN_ONLY


def _check(name: str, status: str, message: str) -> dict[str, str]:
    return {"name": name, "status": status, "message": message}


def _block_executable(block_reference: dict[str, Any] | None) -> tuple[bool, str]:
    if not isinstance(block_reference, dict):
        return False, "no block reference selected"
    block_id = str(block_reference.get("block_id", ""))
    validation = block_reference.get("validation", {})
    status = str(validation.get("status", "")) if isinstance(validation, dict) else ""
    if block_id != CONTROLLED_BLOCK_ID:
        return False, f"block_id {block_id!r} is not the controlled alpha block"
    if status != "cad_insertion_verified":
        return False, f"validation.status={status!r}; cad_insertion_verified required for block tier"
    cad_name = str(block_reference.get("cad_identity", {}).get("block_name", ""))
    if cad_name != CONTROLLED_BLOCK_NAME:
        return False, f"cad_identity.block_name must be {CONTROLLED_BLOCK_NAME!r}"
    return True, "controlled block with cad_insertion_verified"


def block_reference_to_insert_block_alpha_plan(
    block_reference: dict[str, Any],
    *,
    base_point: list[float | int],
    layer: str = PREVIEW_LAYER,
    domain: str = "generic",
) -> dict[str, Any]:
    block_id = str(block_reference["block_id"])
    cad_identity = block_reference.get("cad_identity", {})
    if block_id != CONTROLLED_BLOCK_ID:
        raise ValueError(f"Only controlled block {CONTROLLED_BLOCK_ID!r} can become insert_block_alpha plans.")
    return {
        "version": "0.1",
        "domain": domain,
        "intent": "insert_block_alpha",
        "object": {
            "type": "block_reference",
            "name": str(block_reference.get("name", "Controlled block")),
            "block_id": block_id,
            "cad_identity": {"block_name": str(cad_identity.get("block_name", CONTROLLED_BLOCK_NAME))},
        },
        "placement": {"mode": "absolute", "base_point": list(base_point), "rotation": 0, "scale": [1, 1, 1]},
        "drawing": {"layer": layer},
        "confidence": 1.0,
        "needs_confirmation": False,
    }


def bbox_placeholder_to_cad_plan(
    symbol_spec: dict[str, Any],
    *,
    base_point: list[float | int] | None = None,
    layer: str = PREVIEW_LAYER,
    domain: str = "generic",
) -> dict[str, Any]:
    footprint = symbol_spec["footprint"]
    placement = list(base_point or [0.0, 0.0, 0.0])
    if len(placement) == 2:
        placement.append(0.0)
    return {
        "version": "0.1",
        "domain": domain,
        "intent": "draw_object",
        "object": {
            "type": str(symbol_spec.get("object_type", "object")),
            "name": f"{symbol_spec.get('object_type', 'object')} bbox placeholder",
            "width": float(footprint["width_mm"]),
            "depth": float(footprint["depth_mm"]),
            "height": float(footprint.get("height_mm", 0)),
            "symbol_id": symbol_spec.get("symbol_id"),
        },
        "placement": {"mode": "absolute", "base_point": placement},
        "drawing": {"layer": layer, "include_label": False, "include_dimensions": False},
        "confidence": 0.5,
        "needs_confirmation": False,
    }


def _component_preview_available(object_spec: dict[str, Any], *, fallback_mode: str | None) -> tuple[bool, str]:
    if fallback_mode == "fallback_component_preview":
        if object_spec.get("components"):
            return True, "explicit fallback_component_preview with components"
        return True, "explicit fallback_component_preview (object-level preview)"
    object_type = str(object_spec.get("type", ""))
    if object_type not in _DETAIL_PREVIEW_TYPES:
        return False, f"object type {object_type!r} has no component preview builder"
    if not object_spec.get("components"):
        return False, "object has no components for component preview"
    return True, "component-level detail preview available"


def _symbol_glyph_available(symbol_spec: dict[str, Any], *, mapping_status: str, fallback_mode: str | None) -> tuple[bool, str]:
    if fallback_mode in {"fallback_bbox_placeholder", "deferred_unsupported_symbol", "fallback_component_preview"}:
        return False, f"fallback_policy.mode={fallback_mode!r} excludes symbol glyph tier"
    if mapping_status != "symbol_mapped":
        return False, f"mapping_status={mapping_status!r} is not symbol_mapped"
    errors = validate_symbol_spec(symbol_spec)
    if errors:
        return False, "symbol spec invalid: " + "; ".join(errors[:2])
    try:
        from core.symbol_engine.archetypes import validate_archetype_grammar

        grammar_errors = validate_archetype_grammar(symbol_spec)
        if grammar_errors:
            return False, "archetype grammar failed: " + "; ".join(grammar_errors[:2])
    except ValueError as exc:
        return False, str(exc)
    return True, "symbol_mapped with valid SYMBOL_SPEC and archetype grammar"


def assess_render_tiers(
    object_spec: dict[str, Any],
    *,
    mapping: Any,
    symbol_spec: dict[str, Any],
    block_selection: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Return per-tier availability assessments (does not select a winner)."""

    block_reference = None
    if isinstance(block_selection, dict):
        block_reference = block_selection.get("block_reference")
    fallback_mode = str(symbol_spec.get("fallback_policy", {}).get("mode", ""))

    tiers: list[dict[str, Any]] = []

    block_ok, block_reason = _block_executable(block_reference if block_selection and block_selection.get("status") == "selected" else None)
    tiers.append(
        {
            "tier": "block",
            "available": block_ok,
            "evidence_state": tier_evidence_state("block"),
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "cad_intent": TIER_TO_CAD_INTENT["block"],
            "reason": block_reason,
        }
    )

    symbol_ok, symbol_reason = _symbol_glyph_available(
        symbol_spec,
        mapping_status=str(mapping.mapping_status),
        fallback_mode=fallback_mode or None,
    )
    tiers.append(
        {
            "tier": "symbol_glyph",
            "available": symbol_ok,
            "evidence_state": tier_evidence_state("symbol_glyph"),
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "cad_intent": TIER_TO_CAD_INTENT["symbol_glyph"],
            "reason": symbol_reason,
        }
    )

    component_ok, component_reason = _component_preview_available(object_spec, fallback_mode=fallback_mode or None)
    tiers.append(
        {
            "tier": "component_preview",
            "available": component_ok,
            "evidence_state": tier_evidence_state("component_preview"),
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "cad_intent": TIER_TO_CAD_INTENT["component_preview"],
            "reason": component_reason,
        }
    )

    bbox_declared = bool(symbol_spec.get("fallback_policy", {}).get("bbox_fallback_declared"))
    bbox_ok = fallback_mode == "fallback_bbox_placeholder" and bbox_declared
    tiers.append(
        {
            "tier": "bbox_placeholder",
            "available": bbox_ok,
            "evidence_state": tier_evidence_state("bbox_placeholder"),
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "cad_intent": TIER_TO_CAD_INTENT["bbox_placeholder"],
            "reason": "bbox_fallback_declared" if bbox_ok else "bbox tier requires fallback_bbox_placeholder + bbox_fallback_declared",
        }
    )

    tiers.append(
        {
            "tier": "deferred",
            "available": True,
            "evidence_state": tier_evidence_state("deferred"),
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "cad_intent": None,
            "reason": "structured defer when no higher tier is available",
        }
    )
    return tiers


def detect_silent_degradation(report: dict[str, Any]) -> list[str]:
    """Return human-readable errors when render path degrades without explicit declaration."""

    errors: list[str] = []
    if report.get("silent_degradation"):
        errors.append(str(report.get("silent_degradation_reason", "silent degradation detected")))

    selected = str(report.get("selected_render_path", ""))
    declared_mode = str(report.get("declared_fallback_mode", ""))
    declared_tier = FALLBACK_MODE_TO_TIER.get(declared_mode, "deferred")
    mapping_status = str(report.get("mapping_status", ""))

    tier_by_name = {item["tier"]: item for item in report.get("tier_assessments", []) if isinstance(item, dict)}
    symbol_tier = tier_by_name.get("symbol_glyph", {})

    if symbol_tier.get("available") and selected in {"bbox_placeholder", "component_preview", "deferred"}:
        if declared_mode == "symbol_readable" and mapping_status == "symbol_mapped":
            errors.append(
                f"symbol_glyph tier was available but selected_render_path={selected!r} while declared mode is symbol_readable"
            )
        if selected == "bbox_placeholder" and declared_mode != "fallback_bbox_placeholder":
            errors.append("bbox_placeholder selected without fallback_bbox_placeholder declaration")

    if TIER_RANK.get(selected, 99) > TIER_RANK.get(declared_tier, 99) and mapping_status == "symbol_mapped":
        errors.append(
            f"selected tier {selected!r} is below declared fallback mode {declared_mode!r} ({declared_tier!r}) without fallback_explicit mapping"
        )
    return errors


def resolve_symbol_render_resolution(
    object_spec: dict[str, Any],
    *,
    block_library: dict[str, Any] | None = None,
    base_point: list[float | int] | None = None,
    layer: str = PREVIEW_LAYER,
    domain: str = "generic",
) -> dict[str, Any]:
    """Resolve OBJECT_SPEC to a render path, CAD plan(s), and per-tier evidence assessments."""

    placement = list(base_point or [0.0, 0.0, 0.0])
    if len(placement) == 2:
        placement.append(0.0)

    mapping = object_spec_to_symbol_spec(object_spec)
    symbol_spec = mapping.symbol_spec
    declared_mode = str(symbol_spec.get("fallback_policy", {}).get("mode", ""))

    block_selection: dict[str, Any] | None = None
    if block_library is not None:
        from core.block_engine.block_library import object_spec_to_block_reference

        block_selection = object_spec_to_block_reference(object_spec, block_library)

    tier_assessments = assess_render_tiers(
        object_spec,
        mapping=mapping,
        symbol_spec=symbol_spec,
        block_selection=block_selection,
    )

    selected_render_path = "deferred"
    for item in tier_assessments:
        if item.get("available"):
            selected_render_path = str(item["tier"])
            break

    for item in tier_assessments:
        item["selected"] = item.get("tier") == selected_render_path

    selected_tier = next(item for item in tier_assessments if item["selected"])
    cad_plans: list[dict[str, Any]] = []
    if selected_render_path == "block" and block_selection:
        block_ref = block_selection.get("block_reference")
        if isinstance(block_ref, dict):
            cad_plans.append(
                block_reference_to_insert_block_alpha_plan(
                    block_ref,
                    base_point=placement,
                    layer=layer,
                    domain=domain,
                )
            )
    elif selected_render_path == "symbol_glyph":
        cad_plans.append(symbol_spec_to_cad_plan(symbol_spec, base_point=placement, layer=layer, domain=domain))
    elif selected_render_path == "component_preview":
        cad_plans.extend(
            object_spec_to_detail_cad_plans(object_spec, base_point=placement, layer=layer, domain=domain)
        )
    elif selected_render_path == "bbox_placeholder":
        cad_plans.append(bbox_placeholder_to_cad_plan(symbol_spec, base_point=placement, layer=layer, domain=domain))

    declared_tier = FALLBACK_MODE_TO_TIER.get(declared_mode, "deferred")
    degradation_chain: list[str] = []
    for tier in FALLBACK_RENDER_TIERS:
        if tier == selected_render_path:
            break
        record = next((item for item in tier_assessments if item["tier"] == tier), None)
        if record and record.get("available"):
            degradation_chain.append(f"skipped_available:{tier}")
        elif record and not record.get("available"):
            degradation_chain.append(f"unavailable:{tier}")

    silent_degradation = False
    silent_reason = ""
    symbol_available = any(
        item.get("tier") == "symbol_glyph" and item.get("available") for item in tier_assessments
    )
    if symbol_available and selected_render_path in {"bbox_placeholder", "component_preview", "deferred"}:
        if declared_mode == "symbol_readable" and mapping.mapping_status == "symbol_mapped":
            silent_degradation = True
            silent_reason = "symbol_readable mapping skipped available symbol_glyph tier"
    if TIER_RANK.get(selected_render_path, 99) > TIER_RANK.get(declared_tier, 99) and mapping.mapping_status == "symbol_mapped":
        silent_degradation = True
        silent_reason = (
            f"render path {selected_render_path!r} is below declared mode {declared_mode!r} without fallback_explicit mapping"
        )

    readability_report = build_symbol_readability_report(symbol_spec)

    report: dict[str, Any] = {
        "version": "0.1",
        "object_id": object_spec.get("object_id"),
        "symbol_id": symbol_spec.get("symbol_id"),
        "object_type": object_spec.get("type"),
        "mapping_status": mapping.mapping_status,
        "declared_fallback_mode": declared_mode,
        "declared_render_tier": declared_tier,
        "selected_render_path": selected_render_path,
        "selected_cad_intent": TIER_TO_CAD_INTENT.get(selected_render_path),
        "selected_evidence_state": selected_tier.get("evidence_state"),
        "geometry_accuracy": selected_tier.get("geometry_accuracy"),
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
        "silent_degradation": silent_degradation,
        "silent_degradation_reason": silent_reason,
        "degradation_chain": degradation_chain,
        "tier_assessments": tier_assessments,
        "cad_plan_count": len(cad_plans),
        "cad_plans": cad_plans,
        "cad_plan": cad_plans[0] if len(cad_plans) == 1 else None,
        "symbol_readability_report": readability_report,
        "symbol_readability_status": readability_report.get("readability_status"),
        "mapping_reason": mapping.mapping_reason,
        "geometry_verified": False,
    }
    report["silent_degradation_errors"] = detect_silent_degradation(report)
    return report
