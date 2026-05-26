"""Standardized proposal candidate score breakdown and ranking reasons (BETA-PROPOSAL-01)."""

from __future__ import annotations

from typing import Any

SCORING_VERSION = "0.1"

RANKING_REASON_CODES = frozenset(
    {
        "highest_weighted_score",
        "no_failed_checks",
        "failed_checks_present",
        "scene_preference_boost",
        "circulation_status",
        "zone_placement_best",
        "circulation_branch_selected",
        "preference_straight_spine",
        "placement_failures",
    }
)


def build_ranking_reason(
    code: str,
    message: str,
    *,
    component: str = "",
) -> dict[str, str]:
    if code not in RANKING_REASON_CODES:
        raise ValueError(f"unknown ranking reason code: {code!r}")
    entry: dict[str, str] = {"code": code, "message": message}
    if component:
        entry["component"] = component
    return entry


def build_score_breakdown(
    *,
    rank: int,
    base_score: float,
    scene_weight: float,
    weighted_score: float,
    weight_source: str,
    check_penalty: float = 0.0,
) -> dict[str, Any]:
    return {
        "version": SCORING_VERSION,
        "rank": rank,
        "base_score": round(base_score, 4),
        "scene_weight": round(scene_weight, 4),
        "weighted_score": round(weighted_score, 4),
        "weight_source": weight_source,
        "components": {
            "layout_base": round(base_score, 4),
            "check_penalty": round(check_penalty, 4),
            "preference_boost": round(scene_weight, 4),
        },
    }


def estimate_check_penalty(failed_check_count: int) -> float:
    if failed_check_count <= 0:
        return 0.0
    return round(-0.35 * failed_check_count, 4)


def build_layout_ranking_reasons(ranked_entry: dict[str, Any]) -> list[dict[str, str]]:
    reasons: list[dict[str, str]] = []
    rank = int(ranked_entry.get("rank", 0))
    weighted_score = float(ranked_entry.get("weighted_score", 0))
    failed_checks = list(ranked_entry.get("failed_checks", []))
    scene_weight = float(ranked_entry.get("scene_weight", 0))
    weight_source = str(ranked_entry.get("weight_source", "default"))

    if rank == 1:
        reasons.append(
            build_ranking_reason(
                "highest_weighted_score",
                f"Rank 1 with weighted_score {weighted_score:.4f}.",
                component="weighted_score",
            )
        )
    if failed_checks:
        reasons.append(
            build_ranking_reason(
                "failed_checks_present",
                f"Failed checks: {', '.join(failed_checks)}.",
                component="check_penalty",
            )
        )
    else:
        reasons.append(
            build_ranking_reason(
                "no_failed_checks",
                "No failed layout checks in the current non-CAD model.",
                component="layout_base",
            )
        )
    if scene_weight > 0:
        reasons.append(
            build_ranking_reason(
                "scene_preference_boost",
                f"Scene preference boost +{scene_weight:.4f} from {weight_source}.",
                component="preference_boost",
            )
        )
    return reasons


def enrich_ranked_layout_candidate(ranked_entry: dict[str, Any]) -> dict[str, Any]:
    """Attach score_breakdown and structured ranking_reasons to a compare_layout_candidates row."""

    enriched = dict(ranked_entry)
    failed_count = len(enriched.get("failed_checks", []))
    enriched["score_breakdown"] = build_score_breakdown(
        rank=int(enriched["rank"]),
        base_score=float(enriched["score"]),
        scene_weight=float(enriched.get("scene_weight", 0)),
        weighted_score=float(enriched.get("weighted_score", enriched["score"])),
        weight_source=str(enriched.get("weight_source", "default")),
        check_penalty=estimate_check_penalty(failed_count),
    )
    enriched["ranking_reasons"] = build_layout_ranking_reasons(enriched)
    return enriched


def build_circulation_score_breakdown(
    *,
    rank: int,
    branch: dict[str, Any],
    weight_source: str = "blank_shell_pipeline",
) -> dict[str, Any]:
    base_score = float(branch.get("score", 0))
    best_zone = branch.get("zone_placement_candidates", [])
    failed_count = 0
    if isinstance(best_zone, list) and best_zone:
        summary = max(best_zone, key=lambda item: tuple(item.get("rank_key", []))).get("summary", {})
        if isinstance(summary, dict):
            failed_count = int(summary.get("failed_count", 0))
    scene_weight = 0.1 if branch.get("selected") else 0.0
    weighted_score = base_score + scene_weight
    return build_score_breakdown(
        rank=rank,
        base_score=base_score,
        scene_weight=scene_weight,
        weighted_score=weighted_score,
        weight_source=weight_source,
        check_penalty=estimate_check_penalty(failed_count),
    )


def build_circulation_ranking_reasons(*, branch: dict[str, Any], rank: int) -> list[dict[str, str]]:
    reasons: list[dict[str, str]] = []
    strategy = str(branch.get("strategy", ""))
    status = str(branch.get("status", "unknown"))
    reasons.append(
        build_ranking_reason(
            "circulation_status",
            f"Circulation strategy {strategy} status={status} score={branch.get('score', 0)}.",
            component="layout_base",
        )
    )
    if branch.get("selected"):
        reasons.append(
            build_ranking_reason(
                "circulation_branch_selected",
                f"Selected as primary circulation branch ({strategy}).",
                component="preference_boost",
            )
        )
    if rank == 1:
        reasons.append(
            build_ranking_reason(
                "highest_weighted_score",
                f"Highest circulation branch score among compared strategies.",
                component="weighted_score",
            )
        )
    zone_candidates = branch.get("zone_placement_candidates", [])
    if isinstance(zone_candidates, list) and zone_candidates:
        best = max(zone_candidates, key=lambda item: tuple(item.get("rank_key", [])))
        summary = best.get("summary", {})
        placed = int(summary.get("placed_count", 0)) if isinstance(summary, dict) else 0
        total = int(summary.get("placement_count", 0)) if isinstance(summary, dict) else 0
        reasons.append(
            build_ranking_reason(
                "zone_placement_best",
                f"Best zone {best.get('zone_id', '')} placed {placed}/{total}.",
                component="layout_base",
            )
        )
        failure_reasons = list(summary.get("failure_reasons", [])) if isinstance(summary, dict) else []
        if failure_reasons:
            reasons.append(
                build_ranking_reason(
                    "placement_failures",
                    "Placement failures: " + ", ".join(str(item) for item in failure_reasons),
                    component="check_penalty",
                )
            )
    return reasons


def validate_candidate_scoring(candidate: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    breakdown = candidate.get("score_breakdown")
    if not isinstance(breakdown, dict):
        errors.append("score_breakdown must be an object")
        return errors
    for key in ("version", "rank", "base_score", "weighted_score", "components"):
        if key not in breakdown:
            errors.append(f"score_breakdown.{key} is required")
    reasons = candidate.get("ranking_reasons")
    if not isinstance(reasons, list) or not reasons:
        errors.append("ranking_reasons must be a non-empty array")
        return errors
    for index, reason in enumerate(reasons):
        if not isinstance(reason, dict):
            errors.append(f"ranking_reasons[{index}] must be an object")
            continue
        code = reason.get("code")
        if code not in RANKING_REASON_CODES:
            errors.append(f"ranking_reasons[{index}].code unknown: {code!r}")
        if not reason.get("message"):
            errors.append(f"ranking_reasons[{index}].message is required")
    return errors
