"""Machine-readable proposal comparison summary (BETA-PROPOSAL-02)."""

from __future__ import annotations

from typing import Any

SUMMARY_VERSION = "0.1"


def _collect_ranking_reason_codes(comparison_detail: dict[str, Any]) -> list[str]:
    codes: list[str] = []
    for branch in comparison_detail.get("ranked_circulation_branches", []):
        if not isinstance(branch, dict):
            continue
        for reason in branch.get("ranking_reasons", []):
            if isinstance(reason, dict) and reason.get("code"):
                code = str(reason["code"])
                if code not in codes:
                    codes.append(code)
    layout_comparison = comparison_detail.get("layout_comparison", {})
    if isinstance(layout_comparison, dict):
        for ranked in layout_comparison.get("ranked_candidates", []):
            if not isinstance(ranked, dict):
                continue
            for reason in ranked.get("ranking_reasons", []):
                if isinstance(reason, dict) and reason.get("code"):
                    code = str(reason["code"])
                    if code not in codes:
                        codes.append(code)
    return codes


def build_proposal_comparison_summary(comparison_detail: dict[str, Any]) -> dict[str, Any]:
    """Build benchmark-assertable summary from blank-shell comparison_detail."""

    metrics = comparison_detail.get("metrics", {}) if isinstance(comparison_detail.get("metrics"), dict) else {}
    continuity_block = (
        comparison_detail.get("circulation_continuity", {})
        if isinstance(comparison_detail.get("circulation_continuity"), dict)
        else {}
    )
    selected = comparison_detail.get("selected", {}) if isinstance(comparison_detail.get("selected"), dict) else {}
    layout_comparison = (
        comparison_detail.get("layout_comparison", {})
        if isinstance(comparison_detail.get("layout_comparison"), dict)
        else {}
    )
    top_ranked = layout_comparison.get("ranked_candidates", [{}])
    top_layout = top_ranked[0] if isinstance(top_ranked, list) and top_ranked else {}
    layout_failed_checks = list(top_layout.get("failed_checks", [])) if isinstance(top_layout, dict) else []

    return {
        "version": SUMMARY_VERSION,
        "object_coverage": {
            "requested_types": list(metrics.get("object_types_requested", [])),
            "placed_types": list(metrics.get("object_types_placed", [])),
            "coverage_rate": float(metrics.get("object_coverage_rate", 0)),
            "placed_count": int(metrics.get("placed_count", 0)),
            "placement_count": int(metrics.get("placement_count", 0)),
        },
        "circulation": {
            "continuity": str(continuity_block.get("continuity", "unknown")),
            "selected_strategy": str(selected.get("circulation_strategy", "")),
            "blocked_strategies": list(continuity_block.get("blocked_strategies", [])),
            "branch_count": int(metrics.get("circulation_branch_count", 0)),
        },
        "conflicts": {
            "failed_check_count": int(metrics.get("failed_check_count", 0)),
            "layout_failed_checks": layout_failed_checks,
            "placement_failed_count": int(metrics.get("selected_placement_failed_count", 0)),
        },
        "failure_reasons": {
            "all_distribution": dict(metrics.get("failed_reason_distribution", {})),
            "selected_distribution": dict(metrics.get("selected_failed_reason_distribution", {})),
        },
        "ranking_reason_codes": _collect_ranking_reason_codes(comparison_detail),
        "narrative": str(comparison_detail.get("narrative", "")),
    }


def build_proposal_comparison_summary_from_layout(
    layout_comparison: dict[str, Any],
    *,
    narrative: str = "",
) -> dict[str, Any]:
    """Fallback summary when only layout candidates were compared."""

    ranked = layout_comparison.get("ranked_candidates", [])
    top = ranked[0] if isinstance(ranked, list) and ranked else {}
    failed_checks = list(top.get("failed_checks", [])) if isinstance(top, dict) else []
    codes: list[str] = []
    if isinstance(top, dict):
        for reason in top.get("ranking_reasons", []):
            if isinstance(reason, dict) and reason.get("code"):
                codes.append(str(reason["code"]))
    return {
        "version": SUMMARY_VERSION,
        "object_coverage": {
            "requested_types": [],
            "placed_types": [],
            "coverage_rate": 0.0,
            "placed_count": 0,
            "placement_count": 0,
        },
        "circulation": {
            "continuity": "unknown",
            "selected_strategy": "",
            "blocked_strategies": [],
            "branch_count": 0,
        },
        "conflicts": {
            "failed_check_count": len(failed_checks),
            "layout_failed_checks": failed_checks,
            "placement_failed_count": 0,
        },
        "failure_reasons": {
            "all_distribution": {},
            "selected_distribution": {},
        },
        "ranking_reason_codes": codes,
        "narrative": narrative or f"Compared {len(ranked)} layout candidate(s).",
    }


def flatten_proposal_comparison_summary_metrics(summary: dict[str, Any]) -> dict[str, Any]:
    """Flatten summary for benchmark runner actual fields."""

    object_coverage = summary.get("object_coverage", {})
    circulation = summary.get("circulation", {})
    conflicts = summary.get("conflicts", {})
    failure_reasons = summary.get("failure_reasons", {})
    return {
        "has_proposal_comparison_summary": True,
        "object_coverage_rate": float(object_coverage.get("coverage_rate", 0)),
        "object_types_requested": list(object_coverage.get("requested_types", [])),
        "object_types_placed": list(object_coverage.get("placed_types", [])),
        "placed_count": int(object_coverage.get("placed_count", 0)),
        "placement_count": int(object_coverage.get("placement_count", 0)),
        "circulation_continuity": str(circulation.get("continuity", "")),
        "selected_circulation_strategy": str(circulation.get("selected_strategy", "")),
        "blocked_circulation_strategies": list(circulation.get("blocked_strategies", [])),
        "circulation_branch_count": int(circulation.get("branch_count", 0)),
        "failed_check_count": int(conflicts.get("failed_check_count", 0)),
        "layout_failed_checks": list(conflicts.get("layout_failed_checks", [])),
        "selected_placement_failed_count": int(conflicts.get("placement_failed_count", 0)),
        "failed_reason_distribution": dict(failure_reasons.get("all_distribution", {})),
        "selected_failed_reason_distribution": dict(failure_reasons.get("selected_distribution", {})),
        "ranking_reason_codes": list(summary.get("ranking_reason_codes", [])),
    }


def validate_proposal_comparison_summary(summary: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for section in ("object_coverage", "circulation", "conflicts", "failure_reasons"):
        if section not in summary:
            errors.append(f"{section} is required")
    if summary.get("version") != SUMMARY_VERSION:
        errors.append(f"version must be {SUMMARY_VERSION}")
    continuity = summary.get("circulation", {}).get("continuity")
    if continuity not in {"pass", "degraded", "blocked", "unknown"}:
        errors.append(f"circulation.continuity invalid: {continuity!r}")
    return errors
