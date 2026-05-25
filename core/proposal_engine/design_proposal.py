"""Build minimal design proposals before generating CAD plans."""

from __future__ import annotations

from typing import Any

from core.proposal_engine.proposal_to_plan import proposal_to_plans


def create_design_proposal(
    *,
    brief: dict[str, Any],
    project_model: dict[str, Any],
    object_spec: dict[str, Any],
    layout_proposal: dict[str, Any],
) -> dict[str, Any]:
    candidate = layout_proposal["candidates"][0]
    checks = candidate.get("checks", [])
    failed_checks = [check["name"] for check in checks if check.get("status") == "fail"]
    return {
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
            "from_library": [
                f"object spec {object_spec['object_id']}",
                f"style profile {object_spec.get('style_profile_id', 'unknown')}",
            ],
            "inferred": failed_checks or ["No failed layout checks in the selected candidate."],
        },
        "needs_confirmation": bool(failed_checks) or brief.get("needs_confirmation", False),
        "next_cad_plans": [],
    }


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
