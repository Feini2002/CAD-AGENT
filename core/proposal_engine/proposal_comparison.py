"""Compare design or layout candidates before CAD_PLAN generation."""

from __future__ import annotations

from typing import Any


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

    return {
        "status": "ok",
        "errors": [],
        "layout_id": str(layout_proposal.get("layout_id", "")),
        "recommendation_id": ranked_candidates[0]["candidate_id"],
        "ranked_candidates": ranked_candidates,
    }
