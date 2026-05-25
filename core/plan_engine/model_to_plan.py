"""Convert high-level Core models to safe CAD_PLAN envelopes."""

from __future__ import annotations

from typing import Any

from core.object_engine.parametric_objects import object_spec_to_cad_plan
from core.plan_engine.validate_plan import validate_plan


def _source_refs(
    *,
    object_spec: dict[str, Any],
    layout_proposal: dict[str, Any] | None = None,
    design_proposal: dict[str, Any] | None = None,
) -> dict[str, str]:
    refs = {"object_id": str(object_spec.get("object_id"))}
    if layout_proposal:
        refs["layout_id"] = str(layout_proposal.get("layout_id"))
    if design_proposal:
        refs["proposal_id"] = str(design_proposal.get("proposal_id"))
    return refs


def model_to_plans(
    *,
    object_spec: dict[str, Any] | None = None,
    object_specs: list[dict[str, Any]] | None = None,
    layout_proposal: dict[str, Any] | None = None,
    design_proposal: dict[str, Any] | None = None,
    confirmed: bool = False,
) -> dict[str, Any]:
    if design_proposal and design_proposal.get("needs_confirmation") and not confirmed:
        return {
            "status": "blocked",
            "errors": ["DESIGN_PROPOSAL needs confirmation before CAD_PLAN generation."],
            "plans": [],
        }

    specs = object_specs or ([object_spec] if object_spec is not None else [])
    if not specs:
        return {"status": "blocked", "errors": ["At least one OBJECT_SPEC is required."], "plans": []}

    selected_candidate = None
    if layout_proposal:
        layout_candidates = layout_proposal["candidates"]
        requested_candidate_id = (design_proposal or {}).get("confirmed_candidate_id")
        if requested_candidate_id:
            selected_candidate = next(
                (candidate for candidate in layout_candidates if candidate.get("candidate_id") == requested_candidate_id),
                None,
            )
            if selected_candidate is None:
                return {
                    "status": "blocked",
                    "errors": [f"No layout candidate found for confirmed_candidate_id: {requested_candidate_id}"],
                    "plans": [],
                }
        else:
            selected_candidate = layout_candidates[0]
        checks = selected_candidate.get("checks", [])
        failed = [check.get("name", "unknown") for check in checks if check.get("status") == "fail"]
        if failed and not confirmed:
            return {"status": "blocked", "errors": [f"Layout checks failed: {failed}"], "plans": []}

    placements_by_object: dict[str, dict[str, Any]] = {}
    if selected_candidate is not None:
        placements_by_object = {
            placement["object_id"]: placement
            for placement in selected_candidate.get("placements", [])
        }

    envelopes: list[dict[str, Any]] = []
    all_errors: list[str] = []
    for spec in specs:
        placement = placements_by_object.get(spec["object_id"], {})
        plan = object_spec_to_cad_plan(spec, base_point=placement.get("base_point"))
        errors = validate_plan(plan)
        all_errors.extend(errors)
        envelopes.append(
            {
                "plan_id": f"plan-{spec['object_id']}",
                "source_model_refs": _source_refs(
                    object_spec=spec,
                    layout_proposal=layout_proposal,
                    design_proposal=design_proposal,
                ),
                "requires_confirmation": bool(design_proposal and design_proposal.get("needs_confirmation")),
                "validation_errors": errors,
                "cad_plan": plan,
            }
        )
    return {"status": "ok" if not all_errors else "invalid", "errors": all_errors, "plans": envelopes}
