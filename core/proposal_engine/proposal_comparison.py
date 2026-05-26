"""Compare design or layout candidates before CAD_PLAN generation."""

from __future__ import annotations

from typing import Any

from core.proposal_engine.candidate_scoring import (
    build_circulation_ranking_reasons,
    build_circulation_score_breakdown,
    enrich_ranked_layout_candidate,
)
from core.proposal_engine.comparison_summary import build_proposal_comparison_summary


def _failed_checks(candidate: dict[str, Any]) -> list[str]:
    checks = candidate.get("checks", [])
    if not isinstance(checks, list):
        return []
    return [
        str(check.get("name", "unknown"))
        for check in checks
        if isinstance(check, dict) and check.get("status") == "fail"
    ]


def compare_layout_candidates(layout_proposal: dict[str, Any], preferences: dict[str, Any] | None = None) -> dict[str, Any]:
    preferences = preferences or {}
    candidate_weights = preferences.get("candidate_weights", {})
    if not isinstance(candidate_weights, dict):
        candidate_weights = {}
    weight_source = str(preferences.get("weight_source", "default"))
    candidates = layout_proposal.get("candidates", [])
    if not isinstance(candidates, list) or not candidates:
        return {
            "status": "invalid",
            "errors": ["LAYOUT_PROPOSAL must contain at least one candidate."],
            "ranked_candidates": [],
            "recommendation_id": "",
        }

    ranked = sorted(
        [candidate for candidate in candidates if isinstance(candidate, dict)],
        key=lambda candidate: float(candidate.get("score", 0)) + float(candidate_weights.get(str(candidate.get("candidate_id", "")), 0)),
        reverse=True,
    )
    ranked_candidates: list[dict[str, Any]] = []
    for rank, candidate in enumerate(ranked, start=1):
        failed_checks = _failed_checks(candidate)
        candidate_id = str(candidate.get("candidate_id", f"candidate-{rank:03d}"))
        base_score = float(candidate.get("score", 0))
        scene_weight = float(candidate_weights.get(candidate_id, 0))
        ranked_candidates.append(
            enrich_ranked_layout_candidate(
                {
                    "rank": rank,
                    "candidate_id": candidate_id,
                    "score": base_score,
                    "scene_weight": scene_weight,
                    "weighted_score": base_score + scene_weight,
                    "weight_source": weight_source,
                    "failed_checks": failed_checks,
                    "tradeoffs": (
                        [f"Failed check: {name}" for name in failed_checks]
                        if failed_checks
                        else ["No failed layout checks in the current non-CAD model."]
                    ),
                }
            )
        )

    return {
        "status": "ok",
        "errors": [],
        "layout_id": str(layout_proposal.get("layout_id", "")),
        "recommendation_id": ranked_candidates[0]["candidate_id"],
        "ranked_candidates": ranked_candidates,
    }


def _failed_reason_distribution(candidates: list[dict[str, Any]]) -> dict[str, int]:
    distribution: dict[str, int] = {}
    for candidate in candidates:
        summary = candidate.get("summary", {})
        if not isinstance(summary, dict):
            continue
        for reason in summary.get("failure_reasons", []):
            key = str(reason)
            distribution[key] = distribution.get(key, 0) + 1
    return dict(sorted(distribution.items(), key=lambda item: (-item[1], item[0])))


def _circulation_continuity_label(*, selected_status: str, compared_statuses: list[str]) -> str:
    if selected_status == "pass" and all(status in {"", "pass"} for status in compared_statuses):
        return "pass"
    if selected_status == "pass":
        return "degraded"
    if selected_status == "blocked":
        return "blocked"
    return "unknown"


def _best_zone_candidate(branch: dict[str, Any]) -> dict[str, Any]:
    zone_candidates = branch.get("zone_placement_candidates", [])
    if not zone_candidates:
        return {
            "zone_id": "",
            "summary": {
                "placement_count": 0,
                "placed_count": 0,
                "failed_count": 0,
                "failure_reasons": [],
                "object_types": [],
            },
            "rank_key": [],
            "selected": False,
        }
    return max(zone_candidates, key=lambda candidate: tuple(candidate.get("rank_key", [])))


def build_blank_shell_comparison_detail(
    *,
    candidate_sets: dict[str, Any],
    layout_proposal: dict[str, Any],
    object_types: list[str] | None = None,
    preferences: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build structured comparison metrics for blank-shell multi-candidate artifacts."""

    layout_comparison = compare_layout_candidates(layout_proposal, preferences)
    selection = candidate_sets.get("selection", {}) if isinstance(candidate_sets.get("selection"), dict) else {}
    branches = [
        branch for branch in candidate_sets.get("circulation_branches", []) if isinstance(branch, dict)
    ]
    selected_strategy = str(selection.get("circulation_strategy", ""))
    selected_zone_id = str(selection.get("zone_id", ""))

    ranked_branches: list[dict[str, Any]] = []
    all_zone_candidates: list[dict[str, Any]] = []
    compared_statuses: list[str] = []
    selected_status = ""

    for branch in sorted(branches, key=lambda item: float(item.get("score", 0)), reverse=True):
        strategy = str(branch.get("strategy", ""))
        status = str(branch.get("status", ""))
        compared_statuses.append(status)
        if strategy == selected_strategy:
            selected_status = status
        best_zone = _best_zone_candidate(branch)
        all_zone_candidates.extend(
            candidate
            for candidate in branch.get("zone_placement_candidates", [])
            if isinstance(candidate, dict)
        )
        summary = best_zone.get("summary", {})
        branch_reasons = [
            f"circulation status={status or 'unknown'} score={branch.get('score', 0)}",
            (
                f"best zone {best_zone.get('zone_id', '')} placed "
                f"{summary.get('placed_count', 0)}/{summary.get('placement_count', 0)}"
            ),
        ]
        if branch.get("selected"):
            branch_reasons.append("selected as primary circulation branch")
        if best_zone.get("selected"):
            branch_reasons.append("selected zone for final layout")
        branch_rank = len(ranked_branches) + 1
        score_breakdown = build_circulation_score_breakdown(rank=branch_rank, branch=branch)
        structured_reasons = build_circulation_ranking_reasons(branch=branch, rank=branch_rank)
        ranked_branches.append(
            {
                "circulation_candidate_id": str(branch.get("circulation_candidate_id", "")),
                "strategy": strategy,
                "score": float(branch.get("score", 0)),
                "status": status,
                "selected": bool(branch.get("selected")),
                "zone_count": int(branch.get("zone_count", 0)),
                "best_zone_id": str(best_zone.get("zone_id", "")),
                "placed_count": int(summary.get("placed_count", 0)),
                "failed_count": int(summary.get("failed_count", 0)),
                "placement_count": int(summary.get("placement_count", 0)),
                "object_types_placed": list(summary.get("object_types", [])),
                "rank": branch_rank,
                "score_breakdown": score_breakdown,
                "ranking_reasons": structured_reasons,
                "ranking_reason_messages": branch_reasons,
            }
        )

    selected_branch = next((branch for branch in ranked_branches if branch["selected"]), ranked_branches[0] if ranked_branches else {})
    selected_zone_candidates = [
        candidate
        for branch in branches
        if branch.get("selected")
        for candidate in branch.get("zone_placement_candidates", [])
        if isinstance(candidate, dict) and candidate.get("selected")
    ]
    if not selected_zone_candidates and selected_branch:
        selected_zone_candidates = [
            candidate
            for branch in branches
            if str(branch.get("strategy", "")) == selected_strategy
            for candidate in branch.get("zone_placement_candidates", [])
            if isinstance(candidate, dict) and str(candidate.get("zone_id", "")) == selected_zone_id
        ]
    selected_failed_reason_distribution = _failed_reason_distribution(selected_zone_candidates)
    selected_layout = layout_comparison["ranked_candidates"][0] if layout_comparison.get("ranked_candidates") else {}
    layout_failed_checks = list(selected_layout.get("failed_checks", []))
    failed_reason_distribution = _failed_reason_distribution(all_zone_candidates)
    for reason, count in failed_reason_distribution.items():
        if count > 0 and reason not in layout_failed_checks:
            layout_failed_checks.append(reason)

    requested_types = [str(item) for item in (object_types or [])]
    placed_types = list(selected_branch.get("object_types_placed", []))
    placement_count = int(selected_branch.get("placement_count", 0))
    placed_count = int(selected_branch.get("placed_count", 0))
    object_coverage_rate = round(placed_count / placement_count, 4) if placement_count else 0.0

    continuity = _circulation_continuity_label(
        selected_status=selected_status,
        compared_statuses=[status for status in compared_statuses if status != selected_status],
    )
    ranking_reasons = [
        "Compared circulation strategies: " + ", ".join(branch["strategy"] for branch in ranked_branches if branch["strategy"]),
        f"Primary selection uses circulation={selected_strategy or 'unknown'} zone={selected_zone_id or 'unknown'}.",
        f"Object coverage {placed_count}/{placement_count} ({object_coverage_rate:.0%}) for requested types {requested_types or placed_types}.",
        f"Layout failed checks: {len(layout_failed_checks)}; circulation continuity={continuity}.",
    ]
    if selected_strategy == "straight_spine":
        ranking_reasons.append("straight_spine is preferred when available in the blank-shell pipeline.")
    if failed_reason_distribution:
        ranking_reasons.append(
            "Failure reasons across zone placement alternatives: "
            + ", ".join(f"{reason} x{count}" for reason, count in failed_reason_distribution.items())
        )

    narrative = (
        f"Compared {len(ranked_branches)} circulation branch(es) and "
        f"{candidate_sets.get('counts', {}).get('zone_placement_candidates', len(all_zone_candidates))} "
        f"zone placement alternative(s). "
        f"Selected {selected_strategy or 'unknown'} / {selected_zone_id or 'unknown'} with "
        f"object coverage {object_coverage_rate:.0%}, {len(layout_failed_checks)} failed check(s), "
        f"circulation continuity={continuity}."
    )

    comparison_detail = {
        "version": "0.1",
        "layout_comparison": layout_comparison,
        "selected": {
            "circulation_strategy": selected_strategy,
            "zone_id": selected_zone_id,
            "layout_candidate_id": str(layout_comparison.get("recommendation_id", "")),
        },
        "metrics": {
            "circulation_branch_count": len(ranked_branches),
            "zone_placement_candidate_count": int(
                candidate_sets.get("counts", {}).get("zone_placement_candidates", len(all_zone_candidates))
            ),
            "object_types_requested": requested_types,
            "object_types_placed": placed_types,
            "object_coverage_rate": object_coverage_rate,
            "placed_count": placed_count,
            "placement_count": placement_count,
            "failed_check_count": len(layout_failed_checks),
            "failed_reason_distribution": failed_reason_distribution,
            "selected_failed_reason_distribution": selected_failed_reason_distribution,
            "selected_placement_failed_count": int(selected_branch.get("failed_count", 0)),
        },
        "circulation_continuity": {
            "selected_status": selected_status,
            "continuity": continuity,
            "blocked_strategies": [
                branch["strategy"] for branch in ranked_branches if branch.get("status") == "blocked"
            ],
        },
        "ranking_reasons": ranking_reasons,
        "ranked_circulation_branches": ranked_branches,
        "narrative": narrative,
    }
    comparison_detail["proposal_comparison_summary"] = build_proposal_comparison_summary(comparison_detail)
    return comparison_detail


def _circulation_branch_proposal_candidate(branch: dict[str, Any], *, rank: int = 1) -> dict[str, Any]:
    best_zone = _best_zone_candidate(branch)
    summary = best_zone.get("summary", {})
    failed_reasons = list(summary.get("failure_reasons", []))
    candidate_id = str(branch.get("circulation_candidate_id", branch.get("strategy", "circulation-unknown")))
    strategy = str(branch.get("strategy", ""))
    return {
        "candidate_id": candidate_id,
        "layout_candidate_id": candidate_id,
        "score": float(branch.get("score", 0)),
        "score_breakdown": build_circulation_score_breakdown(rank=rank, branch=branch),
        "ranking_reasons": build_circulation_ranking_reasons(branch=branch, rank=rank),
        "summary": (
            f"Circulation {strategy} with best zone {best_zone.get('zone_id', '')} "
            f"({summary.get('placed_count', 0)}/{summary.get('placement_count', 0)} placed)."
        ),
        "strengths": (
            [f"Circulation status={branch.get('status', 'unknown')}."]
            if not failed_reasons
            else ["Candidate remains explainable despite placement failures."]
        ),
        "risks": [f"Placement failure: {reason}" for reason in failed_reasons] or ["No placement failures in best zone."],
        "failed_checks": failed_reasons,
        "applicable_scenarios": ["blank_shell_preview"],
        "confirmation_questions": (
            [f"Confirm handling for placement failure: {reason}" for reason in failed_reasons]
            if failed_reasons
            else [f"Confirm circulation strategy {strategy} is acceptable."]
        ),
    }
