"""Automatic promotion candidates for asset-intelligence trials.

Candidates produced here are review inputs only. The learning promoter or a
reviewed package must decide whether to write rules, checkers, assets, or
training items.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _decision(*, required: bool, status: str, reason: str, target: str = "", evidence: list[str] | None = None) -> dict[str, Any]:
    return {
        "required": required,
        "status": status,
        "reason": reason,
        "target": target,
        "evidence": evidence or [],
    }


def _boundary() -> dict[str, list[str]]:
    return {
        "checked": ["source_trial_status", "candidate_generation", "no_cad_written", "no_target_mutation"],
        "notChecked": [
            "reviewed_package_approval",
            "rule_quality_after_edit",
            "checker_execution_against_real_cad",
            "asset_verified_reuse_replay",
            "training_source_update",
        ],
        "assumptions": [
            "promotion_candidates_are_proposals_only",
            "pipeline_learning_promoter_must_review_before_writes",
            "real_cad_replay_required_before_verified_asset_claim",
        ],
    }


def _promotion_gate(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    evidence = [str(candidate.get("candidateId", "")) for candidate in candidates if candidate.get("candidateId")]
    return {
        "promotionLevel": "learning_candidate",
        "decision": "review_required",
        "requiredReviewer": "pipeline_learning_promoter",
        "decisions": {
            "updateTrainingSource": _decision(
                required=False,
                status="not_required",
                reason="no-CAD object-family trial is not a formal training acceptance report.",
            ),
            "updateWorkbench": _decision(
                required=False,
                status="not_required",
                reason="candidate generation alone does not change training facts or Table C.",
            ),
            "updateBaseRules": _decision(
                required=False,
                status="not_required",
                reason="sofa trial candidates target task rules and checkers, not global base rules yet.",
            ),
            "updateTaskRules": _decision(
                required=True,
                status="needs_reviewed_package",
                reason="sofa component semantics may become task guidance only after review.",
                target="agents/cad_designer/rules.md",
                evidence=evidence,
            ),
            "updateAgentCalibration": _decision(
                required=True,
                status="needs_reviewed_package",
                reason="candidate guidance may calibrate cad_designer / intent / audit only after review.",
                target="agents/cad_designer/prompt_addendum.md",
                evidence=evidence,
            ),
            "updateChecker": _decision(
                required=True,
                status="needs_reviewed_package",
                reason="sofa readback requirements need an executable checker before promotion.",
                target="libraries/benchmarks/object_checks/",
                evidence=evidence,
            ),
            "retestOriginalTask": _decision(
                required=True,
                status="deferred_until_checker_or_replay",
                reason="no original CAD task can be retested until the checker or replay package exists.",
                evidence=evidence,
            ),
        },
    }


def _sofa_candidates(trial: dict[str, Any]) -> list[dict[str, Any]]:
    object_family = str(trial.get("objectFamily") or "sofa")
    selected = trial.get("selectedCandidate") if isinstance(trial.get("selectedCandidate"), dict) else {}
    required_parts = [str(part) for part in selected.get("requiredParts", []) if part]
    evidence_refs = [
        "object_family_trial.selectedCandidate",
        "object_family_trial.cadPlanDraft",
        "object_family_trial.readbackEvidenceRequirements",
    ]
    return [
        {
            "candidateId": "sofa_component_task_rule",
            "candidateType": "task_rule",
            "status": "needs_reviewed_package",
            "target": "agents/cad_designer/rules.md",
            "objectFamily": object_family,
            "proposal": "Sofa symbols should keep back, seat, arms, and seat division as separable visual parts before CAD execution.",
            "evidence": evidence_refs,
            "requiredParts": required_parts,
        },
        {
            "candidateId": "sofa_readback_checker",
            "candidateType": "checker",
            "status": "needs_reviewed_package",
            "target": "libraries/benchmarks/object_checks/sofa_component_readback.json",
            "objectFamily": object_family,
            "proposal": "Add a checker requiring created handles, CODEX_PREVIEW layer, bbox, entity type census, and part coverage for sofa replay.",
            "evidence": evidence_refs,
            "requiredParts": required_parts,
        },
        {
            "candidateId": "sofa_asset_candidate",
            "candidateType": "asset_candidate",
            "status": "candidate_only",
            "target": "libraries/system_library/furniture/seating/sofas/assets.json",
            "objectFamily": object_family,
            "proposal": "Keep the sofa draft as an asset candidate until a precise sourceSpec and real CAD replay exist.",
            "evidence": evidence_refs,
            "blockedUntil": ["precise_sourceSpec", "real_cad_replay", "reuseWorkflowProbe_or_reuseReplay"],
            "requiredParts": required_parts,
        },
        {
            "candidateId": "sofa_object_family_training_item",
            "candidateType": "training_item",
            "status": "needs_reviewed_package",
            "target": "docs/training/cad-designer-training-plan-v2.md",
            "objectFamily": object_family,
            "proposal": "Consider a focused sofa object-family training item after checker and real replay evidence exist.",
            "evidence": evidence_refs,
            "blockedUntil": ["checker_reviewed", "real_cad_replay"],
            "requiredParts": required_parts,
        },
    ]


def build_asset_intelligence_promotion_candidates(trial: dict[str, Any]) -> dict[str, Any]:
    """Build reviewed-package candidates from an object-family trial."""

    if trial.get("status") != "cad_plan_draft_ready":
        return {
            "schemaVersion": 1,
            "kind": "asset_intelligence_promotion_candidates",
            "status": "blocked",
            "sourceTrialStatus": trial.get("status", ""),
            "objectFamily": trial.get("objectFamily", ""),
            "blockingReasons": ["source_trial_not_ready", *[str(reason) for reason in trial.get("blockingReasons", [])]],
            "candidates": [],
            "mutatedTargets": [],
            "review": {"requiredAgentId": "pipeline_learning_promoter", "status": "not_ready"},
            "promotionGate": {"promotionLevel": "blocked", "decision": "source_trial_not_ready", "decisions": {}},
            "evidenceBoundary": _boundary(),
        }

    candidates = _sofa_candidates(trial)
    return {
        "schemaVersion": 1,
        "kind": "asset_intelligence_promotion_candidates",
        "status": "review_required",
        "candidateSetId": f"asset-promotion.sofa.{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "sourceTrialId": trial.get("trialId", ""),
        "objectFamily": trial.get("objectFamily", ""),
        "candidates": candidates,
        "mutatedTargets": [],
        "review": {
            "requiredAgentId": "pipeline_learning_promoter",
            "status": "ready_for_review",
            "allowedActions": ["accept_candidate", "request_changes", "reject_candidate"],
            "forbiddenActions": ["mutate_targets_without_review", "mark_asset_verified_without_replay"],
        },
        "promotionGate": _promotion_gate(candidates),
        "evidenceBoundary": _boundary(),
    }
