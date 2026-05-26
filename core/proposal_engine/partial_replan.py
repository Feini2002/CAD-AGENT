"""Recompute CAD_PLAN artifacts after local edits without rerunning upstream modules (BETA-PROPOSAL-04)."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from core.plan_engine.dry_run_report import create_dry_run_report
from core.plan_engine.model_to_plan import model_to_plans
from core.proposal_engine.user_confirmation import apply_user_confirmation, load_user_confirmation
from core.verification.verification_report import build_verification_report, summarize_verification_reports
from core.workflows.blank_shell_pipeline import (
    _layout_from_placements,
    _object_spec_from_placement,
    _summarize_dry_run_reports,
)

SKIPPED_UPSTREAM_MODULES = (
    "shell_model",
    "project_model",
    "circulation_candidates",
    "candidate_sets",
    "function_zones",
)

RECOMPUTED_DOWNSTREAM_MODULES = (
    "placements",
    "layout_proposal",
    "design_proposal",
    "cad_plan",
    "cad_plans",
    "cad_plan_items",
    "dry_run_report",
    "dry_run_reports",
    "verification_report",
    "verification_reports",
)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def apply_placement_offsets(
    placements: list[dict[str, Any]],
    object_specs: list[dict[str, Any]],
    offsets: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Apply per-object_spec_id [dx, dy, dz?] offsets to placement base points."""

    if not offsets:
        return placements, []

    updated: list[dict[str, Any]] = []
    applied: list[str] = []
    for placement, spec in zip(placements, object_specs):
        patched = copy.deepcopy(placement)
        object_id = str(spec.get("object_id", ""))
        delta = offsets.get(object_id)
        if isinstance(delta, list) and len(delta) >= 2:
            base = list(patched.get("base_point", [0, 0, 0]))
            if len(base) == 2:
                base = [base[0], base[1], 0]
            dz = float(delta[2]) if len(delta) > 2 else 0.0
            patched["base_point"] = [base[0] + float(delta[0]), base[1] + float(delta[1]), base[2] + dz]
            applied.append(object_id)
        updated.append(patched)
    return updated, applied


def ensure_layout_confirmed_candidate_id(proposal: dict[str, Any], layout: dict[str, Any]) -> dict[str, Any]:
    """Map circulation-style confirmed ids to layout candidate ids for model_to_plans."""

    layout_ids = {
        str(candidate.get("candidate_id", ""))
        for candidate in layout.get("candidates", [])
        if isinstance(candidate, dict)
    }
    current = str(proposal.get("confirmed_candidate_id", ""))
    if current in layout_ids:
        return proposal

    patched = copy.deepcopy(proposal)
    comparison = proposal.get("comparison_detail", {})
    if isinstance(comparison, dict):
        selected = comparison.get("selected", {})
        if isinstance(selected, dict):
            layout_candidate_id = str(selected.get("layout_candidate_id", ""))
            if layout_candidate_id in layout_ids:
                patched["confirmed_candidate_id"] = layout_candidate_id
                return patched

    if layout_ids:
        patched["confirmed_candidate_id"] = next(iter(layout_ids))
    return patched


def recompute_cad_plans_from_pipeline_artifacts(
    artifact_dir: Path,
    *,
    placement_offsets: dict[str, Any] | None = None,
    confirmation_path: Path | None = None,
    apply_confirmation: bool = True,
) -> dict[str, Any]:
    """Patch placements/layout and regenerate CAD_PLAN + dry-run + verification only."""

    artifact_dir = artifact_dir.resolve()
    required = {
        "placements": artifact_dir / "placements.json",
        "layout_proposal": artifact_dir / "layout_proposal.json",
        "design_proposal": artifact_dir / "design_proposal.json",
        "project_model": artifact_dir / "project_model.json",
    }
    missing = [name for name, path in required.items() if not path.is_file()]
    if missing:
        return {
            "status": "invalid",
            "errors": [f"missing pipeline artifacts: {', '.join(missing)}"],
            "modules_skipped": list(SKIPPED_UPSTREAM_MODULES),
            "modules_recomputed": [],
        }

    placements = _read_json(required["placements"])
    layout = _read_json(required["layout_proposal"])
    proposal = _read_json(required["design_proposal"])
    project_model = _read_json(required["project_model"])

    if not isinstance(placements, list):
        return {"status": "invalid", "errors": ["placements.json must be an array"], "modules_skipped": [], "modules_recomputed": []}

    if confirmation_path and apply_confirmation:
        confirmation = load_user_confirmation(confirmation_path)
        proposal = apply_user_confirmation(proposal, confirmation)

    offsets = dict(placement_offsets or {})
    user_confirmation = proposal.get("user_confirmation", {})
    if isinstance(user_confirmation, dict):
        local_prefs = user_confirmation.get("local_preferences", {})
        if isinstance(local_prefs, dict):
            pref_offsets = local_prefs.get("placement_offsets", {})
            if isinstance(pref_offsets, dict):
                for key, value in pref_offsets.items():
                    offsets.setdefault(str(key), value)

    object_specs = [_object_spec_from_placement(item) for item in placements if isinstance(item, dict)]
    placements, applied_offsets = apply_placement_offsets(placements, object_specs, offsets)
    layout = _layout_from_placements(
        project_model=project_model,
        object_specs=object_specs,
        placements=placements,
    )
    proposal = ensure_layout_confirmed_candidate_id(proposal, layout)

    confirmed = bool(proposal.get("user_confirmation")) or not proposal.get("needs_confirmation", False)
    plan_result = model_to_plans(
        object_specs=object_specs,
        layout_proposal=layout,
        design_proposal=proposal,
        confirmed=confirmed,
    )
    if plan_result["status"] != "ok":
        return {
            "status": "blocked",
            "errors": plan_result.get("errors", []),
            "modules_skipped": list(SKIPPED_UPSTREAM_MODULES),
            "modules_recomputed": ["placements", "layout_proposal", "design_proposal"],
            "placement_offsets_applied": applied_offsets,
        }

    cad_plans = [item["cad_plan"] for item in plan_result["plans"]]
    dry_run_reports = [create_dry_run_report(cad_plan) for cad_plan in cad_plans]
    dry_run_summary = _summarize_dry_run_reports(dry_run_reports)
    cad_plan_items_dir = artifact_dir / "cad_plan_items"
    cad_plan_items_dir.mkdir(parents=True, exist_ok=True)
    cad_plan_paths = [cad_plan_items_dir / f"cad_plan_{index + 1:03d}.json" for index in range(len(cad_plans))]

    _write_json(required["placements"], placements)
    _write_json(required["layout_proposal"], layout)
    _write_json(required["design_proposal"], proposal)
    _write_json(artifact_dir / "cad_plan.json", cad_plans[0])
    _write_json(artifact_dir / "cad_plans.json", cad_plans)
    for path, plan in zip(cad_plan_paths, cad_plans):
        _write_json(path, plan)
    verification_reports = [build_verification_report(plan_path=path) for path in cad_plan_paths]
    _write_json(artifact_dir / "dry_run_report.json", dry_run_reports[0])
    _write_json(artifact_dir / "dry_run_reports.json", dry_run_reports)
    _write_json(artifact_dir / "verification_report.json", verification_reports[0])
    _write_json(artifact_dir / "verification_reports.json", verification_reports)

    report = {
        "version": "0.1",
        "status": "ok",
        "artifact_dir": str(artifact_dir),
        "modules_skipped": list(SKIPPED_UPSTREAM_MODULES),
        "modules_recomputed": list(RECOMPUTED_DOWNSTREAM_MODULES),
        "placement_offsets_applied": applied_offsets,
        "cad_plan_count": len(cad_plans),
        "dry_run_summary": dry_run_summary,
        "verification_summary": summarize_verification_reports(verification_reports),
        "confirmed_candidate_id": proposal.get("confirmed_candidate_id", ""),
    }
    _write_json(artifact_dir / "partial_replan_report.json", report)
    return report
