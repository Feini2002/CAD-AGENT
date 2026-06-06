"""No-CAD object-family trial builder for asset intelligence."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.assets.local_rag import PROJECT_ROOT, build_local_asset_rag_pack
from core.plan_engine.dry_run_report import create_dry_run_report
from core.plan_engine.validate_plan import validate_plan


PREVIEW_LAYER = "CODEX_PREVIEW"


def _boundary(*, checked: list[str] | None = None) -> dict[str, list[str]]:
    return {
        "checked": [*(checked or []), "no_cad_written", "no_current_dwg_save", "no_formal_layer_mutation"],
        "notChecked": [
            "real_cad_geometry",
            "created_handles_readback",
            "user_visual_acceptance",
            "closeout_gate",
            "asset_verified_reuse_replay",
        ],
        "assumptions": [
            "object_family_trial_is_no_cad_mvp",
            "cad_plan_draft_requires_user_or_downstream_confirmation_before_execute",
            "dry_run_does_not_prove_geometry_accuracy",
        ],
    }


def _sofa_candidates(retrieval_pack: dict[str, Any]) -> list[dict[str, Any]]:
    source_summary = retrieval_pack.get("sourceSummary") if isinstance(retrieval_pack.get("sourceSummary"), dict) else {}
    matched_context = sum(int(source_summary.get(kind, 0) or 0) for kind in ("system_asset", "training_memory", "failure_sample"))
    return [
        {
            "candidateId": "sofa_symbol_clean_source_first",
            "label": "clean sofa symbol draft",
            "route": "draw_symbol_glyph",
            "score": 0.78 if matched_context else 0.62,
            "requiredParts": ["back", "seat", "arm_left", "arm_right", "seat_division"],
            "rationale": "Prefer a clean component-readable sofa symbol before any CAD write or asset verified claim.",
            "constraints": ["CODEX_PREVIEW only", "needs created handles readback", "no dimensions in glyph draft"],
        },
        {
            "candidateId": "sofa_component_preview",
            "label": "component preview redraw",
            "route": "draw_symbol_glyph",
            "score": 0.68,
            "requiredParts": ["back", "seat", "arm_left", "arm_right"],
            "rationale": "Use when exact asset replay is not yet verified but a readable plan-view sofa is needed.",
            "constraints": ["component roles must stay separable", "dry-run first"],
        },
        {
            "candidateId": "sofa_reuse_probe_later",
            "label": "system asset reuse probe later",
            "route": "reuse_probe_then_cad_plan",
            "score": 0.55,
            "requiredParts": ["sourceSpec", "reuseWorkflowProbe", "readback"],
            "rationale": "Only promote to reuse after sourceSpec and readback replay are available.",
            "constraints": ["must not treat metadata as verified reuse", "requires CAD replay in a later package"],
        },
    ]


def _sofa_cad_plan(brief: str) -> dict[str, Any]:
    return {
        "version": "0.1",
        "domain": "residential",
        "intent": "draw_symbol_glyph",
        "object": {
            "type": "symbol_glyph",
            "symbol_id": "sofa.object_family_trial.v1",
            "name": "沙发对象族试点草案",
            "archetype": "seating",
            "source_brief": brief,
            "glyph_primitives": [
                {
                    "part_id": "back",
                    "kind": "support",
                    "primitive": "rectangle",
                    "corner1": [0, 650, 0],
                    "corner2": [2200, 900, 0],
                },
                {
                    "part_id": "seat",
                    "kind": "seat_surface",
                    "primitive": "rectangle",
                    "corner1": [180, 100, 0],
                    "corner2": [2020, 650, 0],
                },
                {
                    "part_id": "arm_left",
                    "kind": "arm",
                    "primitive": "rectangle",
                    "corner1": [0, 100, 0],
                    "corner2": [180, 900, 0],
                },
                {
                    "part_id": "arm_right",
                    "kind": "arm",
                    "primitive": "rectangle",
                    "corner1": [2020, 100, 0],
                    "corner2": [2200, 900, 0],
                },
                {
                    "part_id": "seat_division",
                    "kind": "inner_detail",
                    "primitive": "line",
                    "start_point": [1100, 120, 0],
                    "end_point": [1100, 630, 0],
                },
            ],
        },
        "placement": {
            "mode": "absolute",
            "base_point": [0, 0, 0],
            "placement_phrase": "object family trial origin; downstream task must resolve real placement",
        },
        "drawing": {
            "layer": PREVIEW_LAYER,
            "include_label": False,
            "include_dimensions": False,
        },
        "confidence": 0.66,
        "needs_confirmation": True,
    }


def _execution_plan() -> dict[str, Any]:
    return {
        "status": "not_executed",
        "cadWritePolicy": "not_executed_no_cad",
        "targetLayer": PREVIEW_LAYER,
        "saveCurrentDwg": False,
        "steps": [
            {"id": "validate_plan", "status": "ready", "cadRequired": False},
            {"id": "dry_run_plan", "status": "ready", "cadRequired": False},
            {"id": "execute_to_CODEX_PREVIEW_after_confirmation", "status": "deferred", "cadRequired": True},
            {"id": "created_handles_readback", "status": "deferred", "cadRequired": True},
            {"id": "visual_acceptance", "status": "deferred", "cadRequired": False},
            {"id": "closeout_gate", "status": "deferred", "cadRequired": False},
        ],
    }


def _readback_requirements() -> dict[str, Any]:
    return {
        "status": "required_before_geometry_claim",
        "requiredFields": [
            "created_handles",
            "created_handle_count",
            "readback_entity_count",
            "bbox",
            "layer",
            "entity_types",
            "savedCurrentDwg",
            "targetLayer",
        ],
        "passCriteria": [
            "created_handle_count > 0",
            "readback_entity_count == created_handle_count",
            "all created entities are on CODEX_PREVIEW",
            "savedCurrentDwg == false",
            "bbox covers back, seat, arms, and seat division",
        ],
    }


def build_object_family_trial(
    brief: str,
    *,
    object_family: str = "sofa",
    project_root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    """Build a no-CAD object-family trial package for the next asset-intelligence step."""

    family = object_family.strip().lower()
    if family not in {"sofa", "沙发"}:
        return {
            "schemaVersion": 1,
            "kind": "object_family_trial",
            "status": "unsupported_object_family",
            "objectFamily": object_family,
            "brief": brief,
            "blockingReasons": ["sofa_only_mvp"],
            "evidenceBoundary": _boundary(checked=["object_family_scope_guard"]),
        }

    retrieval_pack = build_local_asset_rag_pack(brief, project_root=project_root)
    design_candidates = _sofa_candidates(retrieval_pack)
    cad_plan = _sofa_cad_plan(brief)
    validation_errors = validate_plan(cad_plan)
    dry_run = create_dry_run_report(cad_plan)
    status = "cad_plan_draft_ready" if not validation_errors and dry_run.get("status") == "valid" else "blocked"

    return {
        "schemaVersion": 1,
        "kind": "object_family_trial",
        "status": status,
        "trialId": f"object-family.sofa.{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "objectFamily": "sofa",
        "brief": brief,
        "retrievalPack": retrieval_pack,
        "designCandidates": design_candidates,
        "selectedCandidate": design_candidates[0],
        "cadPlanDraft": cad_plan,
        "validationErrors": validation_errors,
        "dryRunReport": dry_run,
        "executionPlan": _execution_plan(),
        "readbackEvidenceRequirements": _readback_requirements(),
        "evidenceBoundary": _boundary(checked=["local_rag_retrieval", "design_candidate_generation", "cad_plan_validation", "dry_run_plan"]),
    }
