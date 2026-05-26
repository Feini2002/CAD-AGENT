"""Candidate-set generation for blank-shell layout workflows."""

from __future__ import annotations

from typing import Any

from core.layout_engine.placement import create_zone_placements
from core.layout_engine.zone_splitter import split_zones


def _placement_rank_key(zone: dict[str, Any], placements: list[dict[str, Any]]) -> tuple[bool, int, int, float]:
    placed_count = sum(1 for placement in placements if placement.get("status") == "placed")
    failed_count = len(placements) - placed_count
    return (
        failed_count == 0,
        placed_count,
        -failed_count,
        float(zone.get("score", 0)),
    )


def _summarize_placements(placements: list[dict[str, Any]]) -> dict[str, Any]:
    placed_count = sum(1 for placement in placements if placement.get("status") == "placed")
    failed_count = len(placements) - placed_count
    failure_reasons: list[str] = []
    for placement in placements:
        if placement.get("status") != "placed":
            failure_reasons.extend(str(item) for item in placement.get("failure_reasons", []))
    object_types = sorted(
        {
            str(placement.get("object_type"))
            for placement in placements
            if placement.get("object_type")
        }
    )
    return {
        "placement_count": len(placements),
        "placed_count": placed_count,
        "failed_count": failed_count,
        "failure_reasons": sorted(set(failure_reasons)),
        "object_types": object_types,
    }


def _evaluate_zone_placement_candidates(
    *,
    zones: list[dict[str, Any]],
    shell: dict[str, Any],
    object_types: list[str],
    block_library: dict[str, Any],
    preferences: dict[str, Any],
    path_surfaces: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidate_zones = zones or [
        {
            "zone_id": "zone-fallback",
            "geometry": shell["boundary"],
            "boundary": shell["boundary"],
            "score": 0,
        }
    ]
    evaluated: list[dict[str, Any]] = []
    for zone in candidate_zones:
        placements = create_zone_placements(
            [zone],
            object_types=object_types,
            block_library=block_library,
            preferences=preferences,
            path_surfaces=path_surfaces,
            fixed_obstacles=shell.get("fixed_obstacles", []),
        )
        rank_key = _placement_rank_key(zone, placements)
        evaluated.append(
            {
                "zone_id": str(zone.get("zone_id", "zone-unknown")),
                "zone_score": float(zone.get("score", 0)),
                "side_of_path": str(zone.get("side_of_path", "")),
                "summary": _summarize_placements(placements),
                "placements": placements,
                "rank_key": list(rank_key),
                "zone": zone,
            }
        )
    return sorted(evaluated, key=lambda item: tuple(item["rank_key"]), reverse=True)


def _pick_best_zone_placement(
    zone_placement_candidates: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not zone_placement_candidates:
        raise ValueError("zone_placement_candidates must not be empty")
    best = zone_placement_candidates[0]
    return best["zone"], best["placements"]


def _select_circulation_for_zones(
    circulation_candidates: list[dict[str, Any]],
    scene_preferences: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Pick circulation for zone split; honor scene `circulation_strategy_weights` when present."""

    if not circulation_candidates:
        raise ValueError("circulation_candidates must not be empty")
    scene_preferences = scene_preferences or {}
    circulation_block = scene_preferences.get("circulation", scene_preferences)
    if not isinstance(circulation_block, dict):
        circulation_block = {}
    weights = circulation_block.get("circulation_strategy_weights", {})
    if isinstance(weights, dict) and weights:
        return max(
            circulation_candidates,
            key=lambda candidate: float(candidate.get("score", 0))
            + float(weights.get(str(candidate.get("strategy", "")), 0)),
        )
    return next(
        (candidate for candidate in circulation_candidates if candidate.get("strategy") == "straight_spine"),
        circulation_candidates[0],
    )


def build_blank_shell_candidate_sets(
    *,
    shell: dict[str, Any],
    circulation_candidates: list[dict[str, Any]],
    object_types: list[str],
    block_library: dict[str, Any],
    placement_preferences: dict[str, Any],
    scene_preferences: dict[str, Any] | None = None,
    constraints: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    """Build multi-branch candidate_sets and return the selected circulation / zone / placements."""

    constraints = constraints or {}
    selected_circulation = _select_circulation_for_zones(circulation_candidates, scene_preferences)
    selected_strategy = str(selected_circulation.get("strategy", ""))
    circulation_branches: list[dict[str, Any]] = []
    zone_placement_candidate_total = 0

    for circulation in circulation_candidates:
        strategy = str(circulation.get("strategy", ""))
        zones = split_zones(shell, circulation, constraints)
        path_surfaces = circulation.get("paths", [{}])[0].get("path_surface", []) if circulation.get("paths") else []
        zone_placement_candidates = _evaluate_zone_placement_candidates(
            zones=zones,
            shell=shell,
            object_types=object_types,
            block_library=block_library,
            preferences=placement_preferences,
            path_surfaces=path_surfaces,
        )
        zone_placement_candidate_total += len(zone_placement_candidates)
        circulation_branches.append(
            {
                "circulation_candidate_id": f"circulation-{strategy or 'unknown'}",
                "strategy": strategy,
                "score": float(circulation.get("score", 0)),
                "status": str(circulation.get("status", "")),
                "selected": strategy == selected_strategy,
                "zone_count": len(zones),
                "zone_placement_candidates": [
                    {
                        "zone_id": candidate["zone_id"],
                        "zone_score": candidate["zone_score"],
                        "side_of_path": candidate["side_of_path"],
                        "summary": candidate["summary"],
                        "placements": candidate["placements"],
                        "rank_key": candidate["rank_key"],
                        "selected": False,
                    }
                    for candidate in zone_placement_candidates
                ],
            }
        )

    selected_branch = next(branch for branch in circulation_branches if branch["selected"])
    selected_zones = split_zones(shell, selected_circulation, constraints)
    best_zone_candidate = max(
        selected_branch["zone_placement_candidates"],
        key=lambda candidate: tuple(candidate["rank_key"]),
    )
    selected_zone_id = str(best_zone_candidate["zone_id"])
    placements = best_zone_candidate["placements"]
    target_zone = next(
        (zone for zone in selected_zones if str(zone.get("zone_id", "")) == selected_zone_id),
        selected_zones[0] if selected_zones else {"zone_id": selected_zone_id},
    )
    for candidate in selected_branch["zone_placement_candidates"]:
        candidate["selected"] = candidate["zone_id"] == selected_zone_id

    candidate_sets = {
        "version": "0.1",
        "selection": {
            "circulation_strategy": selected_strategy,
            "circulation_candidate_id": f"circulation-{selected_strategy or 'unknown'}",
            "zone_id": selected_zone_id,
        },
        "circulation_branches": circulation_branches,
        "counts": {
            "circulation_candidates": len(circulation_candidates),
            "circulation_branches": len(circulation_branches),
            "zone_placement_candidates": zone_placement_candidate_total,
        },
    }
    return candidate_sets, selected_circulation, selected_zones, target_zone, placements


def choose_zone_placements(
    *,
    zones: list[dict[str, Any]],
    shell: dict[str, Any],
    object_types: list[str],
    block_library: dict[str, Any],
    preferences: dict[str, Any],
    path_surfaces: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    zone_placement_candidates = _evaluate_zone_placement_candidates(
        zones=zones,
        shell=shell,
        object_types=object_types,
        block_library=block_library,
        preferences=preferences,
        path_surfaces=path_surfaces,
    )
    return _pick_best_zone_placement(zone_placement_candidates)
