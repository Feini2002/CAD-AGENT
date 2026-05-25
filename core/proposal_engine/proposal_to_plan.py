"""Convert confirmed design proposals into CAD_PLAN lists without executing CAD."""

from __future__ import annotations

from typing import Any

from core.object_engine.object_to_plan import object_to_plan


def proposal_to_plans(
    proposal: dict[str, Any],
    *,
    object_spec: dict[str, Any],
    layout_proposal: dict[str, Any],
    confirmed: bool = False,
) -> list[dict[str, Any]]:
    if proposal.get("needs_confirmation") and not confirmed:
        raise ValueError("DESIGN_PROPOSAL needs confirmation before it can become CAD_PLAN.")
    requested_candidate_id = proposal.get("confirmed_candidate_id")
    layout_candidates = layout_proposal["candidates"]
    if requested_candidate_id:
        candidate = next(
            (item for item in layout_candidates if item.get("candidate_id") == requested_candidate_id),
            None,
        )
        if candidate is None:
            raise ValueError(f"No layout candidate found for confirmed_candidate_id: {requested_candidate_id}")
    else:
        candidate = layout_candidates[0]
    failed_checks = [
        check.get("name", "unknown")
        for check in candidate.get("checks", [])
        if check.get("status") == "fail"
    ]
    if failed_checks and not confirmed:
        raise ValueError(f"Layout checks failed and need confirmation: {failed_checks}")
    object_id = object_spec.get("object_id")
    placement = next(
        (item for item in candidate.get("placements", []) if item.get("object_id") == object_id),
        None,
    )
    if placement is None:
        raise ValueError(f"No placement found for object_id: {object_id}")
    return [object_to_plan(object_spec, base_point=placement["base_point"])]
