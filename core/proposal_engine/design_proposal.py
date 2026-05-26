"""Build minimal design proposals before generating CAD plans."""

from __future__ import annotations

from typing import Any

from core.proposal_engine.candidate_scoring import (
    build_circulation_ranking_reasons,
    build_circulation_score_breakdown,
    build_layout_ranking_reasons,
    build_score_breakdown,
    estimate_check_penalty,
)
from core.proposal_engine.comparison_summary import (
    build_proposal_comparison_summary,
    build_proposal_comparison_summary_from_layout,
)
from core.proposal_engine.proposal_comparison import (
    build_blank_shell_comparison_detail,
    compare_layout_candidates,
    _circulation_branch_proposal_candidate,
)
from core.proposal_engine.proposal_to_plan import proposal_to_plans


def _candidate_summary(
    candidate: dict[str, Any],
    *,
    rank: int = 1,
    weight_source: str = "default",
) -> dict[str, Any]:
    checks = candidate.get("checks", [])
    failed_checks = [check.get("name", "unknown") for check in checks if check.get("status") == "fail"]
    candidate_id = str(candidate.get("candidate_id", "candidate-001"))
    base_score = float(candidate.get("score", 0))
    ranked_stub = {
        "rank": rank,
        "score": base_score,
        "scene_weight": 0.0,
        "weighted_score": base_score,
        "weight_source": weight_source,
        "failed_checks": failed_checks,
    }
    return {
        "candidate_id": candidate_id,
        "layout_candidate_id": candidate_id,
        "score": base_score,
        "summary": f"Layout candidate {candidate_id} with score {candidate.get('score', 0)}.",
        "strengths": ["No failed checks in the current non-CAD model."] if not failed_checks else ["Candidate remains explainable despite failed checks."],
        "risks": [f"Failed check: {name}" for name in failed_checks],
        "failed_checks": failed_checks,
        "applicable_scenarios": ["generic_preview"],
        "confirmation_questions": [f"Confirm handling for failed check: {name}" for name in failed_checks],
        "score_breakdown": build_score_breakdown(
            rank=rank,
            base_score=base_score,
            scene_weight=0.0,
            weighted_score=base_score,
            weight_source=weight_source,
            check_penalty=estimate_check_penalty(len(failed_checks)),
        ),
        "ranking_reasons": build_layout_ranking_reasons(ranked_stub),
    }


def _attach_layout_comparison_scoring(
    proposal_candidates: list[dict[str, Any]],
    layout_comparison: dict[str, Any],
) -> list[dict[str, Any]]:
    ranked_by_id = {
        str(item["candidate_id"]): item
        for item in layout_comparison.get("ranked_candidates", [])
        if isinstance(item, dict)
    }
    enriched: list[dict[str, Any]] = []
    for candidate in proposal_candidates:
        merged = dict(candidate)
        ranked = ranked_by_id.get(str(candidate.get("candidate_id", "")))
        if ranked:
            merged["score"] = float(ranked.get("weighted_score", merged.get("score", 0)))
            merged["score_breakdown"] = ranked.get("score_breakdown", merged.get("score_breakdown"))
            merged["ranking_reasons"] = ranked.get("ranking_reasons", merged.get("ranking_reasons"))
        enriched.append(merged)
    return enriched


def create_design_proposal(
    *,
    brief: dict[str, Any],
    project_model: dict[str, Any],
    object_spec: dict[str, Any],
    layout_proposal: dict[str, Any],
    candidate_sets: dict[str, Any] | None = None,
    object_types: list[str] | None = None,
    preferences: dict[str, Any] | None = None,
) -> dict[str, Any]:
    layout_candidates = layout_proposal.get("candidates", [])
    candidate = layout_candidates[0]
    comparison_detail: dict[str, Any] | None = None
    if isinstance(candidate_sets, dict) and candidate_sets.get("circulation_branches"):
        comparison_detail = build_blank_shell_comparison_detail(
            candidate_sets=candidate_sets,
            layout_proposal=layout_proposal,
            object_types=object_types,
            preferences=preferences,
        )
        sorted_branches = sorted(
            [branch for branch in candidate_sets["circulation_branches"] if isinstance(branch, dict)],
            key=lambda item: float(item.get("score", 0)),
            reverse=True,
        )
        proposal_candidates = [
            _circulation_branch_proposal_candidate(branch, rank=index + 1)
            for index, branch in enumerate(sorted_branches)
        ]
    else:
        proposal_candidates = [
            _candidate_summary(item, rank=index + 1)
            for index, item in enumerate(layout_candidates)
            if isinstance(item, dict)
        ]
    layout_comparison = compare_layout_candidates(layout_proposal, preferences)
    proposal_candidates = _attach_layout_comparison_scoring(proposal_candidates, layout_comparison)
    layout_failed_checks = [
        str(check.get("name", "unknown"))
        for check in layout_candidates[0].get("checks", [])
        if isinstance(check, dict) and check.get("status") == "fail"
    ]
    if comparison_detail:
        selected_strategy = str(comparison_detail["selected"].get("circulation_strategy", ""))
        selected_candidate_id = f"circulation-{selected_strategy}" if selected_strategy else ""
        selected_proposal = next(
            (item for item in proposal_candidates if item["candidate_id"] == selected_candidate_id),
            proposal_candidates[0] if proposal_candidates else None,
        )
        failed_checks = list(layout_failed_checks)
        if selected_proposal:
            failed_checks.extend(
                failed for failed in selected_proposal["failed_checks"] if failed not in failed_checks
            )
    else:
        failed_checks = [
            failed
            for proposal_candidate in proposal_candidates
            for failed in proposal_candidate["failed_checks"]
        ]
        failed_checks = list(dict.fromkeys(failed_checks + layout_failed_checks))
    comparison_summary = (
        comparison_detail["narrative"]
        if comparison_detail
        else f"{len(proposal_candidates)} layout candidate(s) prepared for comparison."
    )
    algorithm_evidence = [
        f"layout candidates: {len(layout_candidates)}",
        f"proposal candidates: {len(proposal_candidates)}",
        f"layout recommendation: {layout_comparison.get('recommendation_id', '')}",
    ]
    if comparison_detail:
        metrics = comparison_detail["metrics"]
        algorithm_evidence.extend(
            [
                f"object coverage: {metrics['object_coverage_rate']}",
                f"failed checks: {metrics['failed_check_count']}",
                f"circulation continuity: {comparison_detail['circulation_continuity']['continuity']}",
                f"circulation branches compared: {metrics['circulation_branch_count']}",
            ]
        )
    proposal: dict[str, Any] = {
        "version": "0.1",
        "proposal_id": f"proposal-{project_model['project_id']}",
        "brief_id": brief["brief_id"],
        "project_id": project_model["project_id"],
        "summary": f"Prepare a preview CAD_PLAN for {object_spec['name']} on CODEX_PREVIEW.",
        "decisions": [
            f"Use object spec {object_spec['object_id']}.",
            f"Use layout candidate {candidate['candidate_id']} with score {candidate['score']}.",
        ],
        "evidence": {
            "from_user": [brief["user_request"]],
            "from_drawing": [f"space count: {len(project_model['spaces'])}"],
            "from_shell": [f"shell_id: {project_model.get('shell_id', 'none')}"],
            "from_library": [
                f"object spec {object_spec['object_id']}",
                f"style profile {object_spec.get('style_profile_id', 'unknown')}",
            ],
            "from_algorithm": algorithm_evidence,
            "inferred": failed_checks or ["No failed layout checks in the selected candidate."],
        },
        "candidates": proposal_candidates,
        "confirmed_candidate_id": "",
        "comparison_summary": comparison_summary,
        "needs_confirmation": bool(failed_checks) or brief.get("needs_confirmation", False),
        "next_cad_plans": [],
    }
    if comparison_detail:
        proposal["comparison_detail"] = comparison_detail
        proposal["proposal_comparison_summary"] = comparison_detail.get(
            "proposal_comparison_summary"
        ) or build_proposal_comparison_summary(comparison_detail)
    elif layout_comparison.get("status") == "ok":
        proposal["proposal_comparison_summary"] = build_proposal_comparison_summary_from_layout(
            layout_comparison,
            narrative=comparison_summary,
        )
    return proposal


def proposal_to_plan(
    proposal: dict[str, Any],
    *,
    object_spec: dict[str, Any],
    layout_proposal: dict[str, Any],
    confirmed: bool = False,
) -> dict[str, Any]:
    if proposal.get("needs_confirmation") and not confirmed:
        raise ValueError("DESIGN_PROPOSAL needs confirmation before it can become a CAD_PLAN.")
    failed_checks = [
        check.get("name", "unknown")
        for check in layout_proposal["candidates"][0].get("checks", [])
        if check.get("status") == "fail"
    ]
    if failed_checks and not confirmed:
        raise ValueError(f"Layout checks failed and need confirmation: {failed_checks}")
    plan = proposal_to_plans(
        proposal,
        object_spec=object_spec,
        layout_proposal=layout_proposal,
        confirmed=confirmed,
    )[0]
    proposal["next_cad_plans"] = [f"generated:{object_spec['object_id']}"]
    return plan
