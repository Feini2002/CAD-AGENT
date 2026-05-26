"""Finalize user-confirmed CAD_PLAN bundles with unselected candidate evidence (BETA-PROPOSAL-05)."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from core.plan_engine.dry_run_report import create_dry_run_report
from core.plan_engine.validate_plan import validate_plan
from core.proposal_engine.partial_replan import recompute_cad_plans_from_pipeline_artifacts
from core.proposal_engine.user_confirmation import (
    build_user_confirmation,
    load_user_confirmation,
)

BUNDLE_VERSION = "0.1"
CONTROLLED_CAD_POLICY = {
    "layer": "CODEX_PREVIEW",
    "needs_confirmation": False,
    "saved_dwg": False,
}


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build_unselected_candidate_evidence(
    proposal: dict[str, Any],
    confirmation: dict[str, Any],
) -> dict[str, Any]:
    """Preserve non-selected proposal candidates and rejection reasons for audit."""

    selected = str(confirmation.get("selected_candidate_id", ""))
    candidates = [item for item in proposal.get("candidates", []) if isinstance(item, dict)]
    not_selected = [
        {
            "candidate_id": str(item.get("candidate_id", "")),
            "layout_candidate_id": str(item.get("layout_candidate_id", "")),
            "score": float(item.get("score", 0)),
            "summary": str(item.get("summary", "")),
            "failed_checks": list(item.get("failed_checks", [])),
            "ranking_reasons": list(item.get("ranking_reasons", [])),
            "score_breakdown": copy.deepcopy(item.get("score_breakdown", {})),
        }
        for item in candidates
        if str(item.get("candidate_id", "")) != selected
    ]
    return {
        "selected_candidate_id": selected,
        "rejected_candidates": list(confirmation.get("rejected_candidates", [])),
        "candidates_not_selected": not_selected,
        "unselected_candidate_count": len(not_selected),
        "comparison_summary": str(proposal.get("comparison_summary", "")),
        "proposal_comparison_summary": copy.deepcopy(proposal.get("proposal_comparison_summary", {})),
        "comparison_detail_preserved": bool(proposal.get("comparison_detail")),
    }


def enforce_controlled_cad_plans(cad_plans: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for index, plan in enumerate(cad_plans):
        prefix = f"cad_plans[{index}]"
        errors.extend(validate_plan(plan))
        drawing = plan.get("drawing", {})
        if drawing.get("layer") != CONTROLLED_CAD_POLICY["layer"]:
            errors.append(f"{prefix}.drawing.layer must be {CONTROLLED_CAD_POLICY['layer']}")
        if plan.get("needs_confirmation") is not False:
            errors.append(f"{prefix}.needs_confirmation must be false after confirmation")
    return errors


def build_default_confirmation_for_proposal(
    proposal: dict[str, Any],
    *,
    action: str = "accept",
    selected_candidate_id: str | None = None,
) -> dict[str, Any]:
    candidates = [item for item in proposal.get("candidates", []) if isinstance(item, dict)]
    if not candidates:
        raise ValueError("proposal has no candidates")
    selected = selected_candidate_id or str(candidates[0].get("candidate_id", ""))
    rejected = [
        {
            "candidate_id": str(item.get("candidate_id", "")),
            "reason_code": "user_rejected",
            "reason_note": "Not selected in default confirmation builder.",
        }
        for item in candidates
        if str(item.get("candidate_id", "")) != selected
    ]
    return build_user_confirmation(
        proposal=proposal,
        selected_candidate_id=selected,
        action=action,
        rejected_candidates=rejected,
    )


def finalize_confirmed_cad_plans(
    artifact_dir: Path,
    confirmation_path: Path,
    *,
    placement_offsets: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Apply confirmation, regenerate controlled CAD_PLANs, validate/dry-run, retain unselected evidence."""

    replan = recompute_cad_plans_from_pipeline_artifacts(
        artifact_dir,
        placement_offsets=placement_offsets,
        confirmation_path=confirmation_path,
        apply_confirmation=True,
    )
    if replan.get("status") != "ok":
        return {
            "version": BUNDLE_VERSION,
            "status": "blocked",
            "errors": replan.get("errors", ["partial replan failed"]),
            "replan": replan,
        }

    artifact_dir = artifact_dir.resolve()
    proposal = _read_json(artifact_dir / "design_proposal.json")
    confirmation = load_user_confirmation(confirmation_path)
    cad_plans = _read_json(artifact_dir / "cad_plans.json")
    if not isinstance(cad_plans, list) or not cad_plans:
        return {"version": BUNDLE_VERSION, "status": "invalid", "errors": ["cad_plans.json empty"]}

    validation_errors = enforce_controlled_cad_plans(cad_plans)
    dry_run_reports = [create_dry_run_report(plan) for plan in cad_plans]
    invalid_dry_runs = [report for report in dry_run_reports if report.get("status") != "valid"]
    if invalid_dry_runs:
        validation_errors.append(f"dry_run invalid count: {len(invalid_dry_runs)}")

    unselected = build_unselected_candidate_evidence(proposal, confirmation)
    bundle = {
        "version": BUNDLE_VERSION,
        "proposal_id": str(proposal.get("proposal_id", "")),
        "confirmation_id": str(confirmation.get("confirmation_id", "")),
        "confirmed_candidate_id": str(proposal.get("confirmed_candidate_id", "")),
        "controlled_cad_policy": dict(CONTROLLED_CAD_POLICY),
        "confirmed_cad_plans": cad_plans,
        "unselected_candidate_evidence": unselected,
        "validation": {
            "plan_count": len(cad_plans),
            "valid_count": len(cad_plans) if not validation_errors else 0,
            "errors": validation_errors,
            "all_valid": not validation_errors,
        },
        "dry_run": {
            "plan_count": len(dry_run_reports),
            "valid_count": sum(1 for report in dry_run_reports if report.get("status") == "valid"),
            "status_counts": {},
        },
    }
    status_counts: dict[str, int] = {}
    for report in dry_run_reports:
        key = str(report.get("status", "unknown"))
        status_counts[key] = status_counts.get(key, 0) + 1
    bundle["dry_run"]["status_counts"] = status_counts

    finalize_report = {
        "version": BUNDLE_VERSION,
        "status": "ok" if not validation_errors else "invalid",
        "artifact_dir": str(artifact_dir),
        "cad_plan_count": len(cad_plans),
        "unselected_candidate_count": unselected["unselected_candidate_count"],
        "validation_all_valid": not validation_errors,
        "dry_run_valid_count": bundle["dry_run"]["valid_count"],
        "confirmed_candidate_id": bundle["confirmed_candidate_id"],
        "errors": validation_errors,
    }

    _write_json(artifact_dir / "confirmed_cad_plan_bundle.json", bundle)
    _write_json(artifact_dir / "unselected_candidate_evidence.json", unselected)
    _write_json(artifact_dir / "confirmed_finalize_report.json", finalize_report)

    if validation_errors:
        finalize_report["bundle"] = bundle
        return finalize_report
    return finalize_report
