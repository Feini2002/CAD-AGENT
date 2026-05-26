"""User confirmation input for design proposals (BETA-PROPOSAL-03)."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from core.schemas.validator import validate_json, validate_value

CONFIRMATION_VERSION = "0.1"
SCHEMA_NAME = "proposal_user_confirmation.schema.json"
SCHEMA_ROOT = Path(__file__).resolve().parents[1] / "schemas"

REJECTION_REASON_CODES = frozenset(
    {
        "user_rejected",
        "clearance_conflict",
        "circulation_unacceptable",
        "placement_failure",
        "cost_budget",
        "other",
    }
)

ACCEPT_ACTIONS = frozenset({"accept", "accept_with_risks"})


def schema_path() -> Path:
    return SCHEMA_ROOT / SCHEMA_NAME


def validate_confirmation_document(confirmation: dict[str, Any]) -> list[str]:
    schema = json.loads(schema_path().read_text(encoding="utf-8"))
    errors = validate_value(confirmation, schema)
    for index, rejected in enumerate(confirmation.get("rejected_candidates", [])):
        if not isinstance(rejected, dict):
            continue
        code = rejected.get("reason_code")
        if code not in REJECTION_REASON_CODES:
            errors.append(f"rejected_candidates[{index}].reason_code unknown: {code!r}")
    return errors


def validate_confirmation_against_proposal(
    confirmation: dict[str, Any],
    proposal: dict[str, Any],
) -> list[str]:
    """Cross-check confirmation payload against a DESIGN_PROPOSAL."""

    errors = validate_confirmation_document(confirmation)
    if errors:
        return errors

    if confirmation.get("proposal_id") != proposal.get("proposal_id"):
        errors.append(
            f"proposal_id mismatch: confirmation={confirmation.get('proposal_id')!r} "
            f"proposal={proposal.get('proposal_id')!r}"
        )

    candidate_ids = {
        str(item.get("candidate_id", ""))
        for item in proposal.get("candidates", [])
        if isinstance(item, dict)
    }
    selected = str(confirmation.get("selected_candidate_id", ""))
    action = str(confirmation.get("action", ""))

    if action in ACCEPT_ACTIONS:
        if selected not in candidate_ids:
            errors.append(f"selected_candidate_id not in proposal candidates: {selected!r}")
    elif action == "reject_all":
        if selected:
            errors.append("reject_all must use empty selected_candidate_id")
    else:
        errors.append(f"unknown action: {action!r}")

    for index, rejected in enumerate(confirmation.get("rejected_candidates", [])):
        if not isinstance(rejected, dict):
            continue
        rejected_id = str(rejected.get("candidate_id", ""))
        if rejected_id not in candidate_ids:
            errors.append(f"rejected_candidates[{index}].candidate_id not in proposal: {rejected_id!r}")
        if action in ACCEPT_ACTIONS and rejected_id == selected:
            errors.append(f"rejected_candidates[{index}] must not equal selected candidate")

    local_prefs = confirmation.get("local_preferences", {})
    if isinstance(local_prefs, dict):
        weights = local_prefs.get("candidate_weights", {})
        if isinstance(weights, dict):
            for candidate_id in weights:
                if candidate_id not in candidate_ids:
                    errors.append(f"local_preferences.candidate_weights unknown candidate: {candidate_id!r}")

    return errors


def build_user_confirmation(
    *,
    proposal: dict[str, Any],
    selected_candidate_id: str,
    action: str = "accept",
    rejected_candidates: list[dict[str, Any]] | None = None,
    local_preferences: dict[str, Any] | None = None,
    confirmation_id: str | None = None,
) -> dict[str, Any]:
    """Build a confirmation document for the given proposal."""

    if action not in ACCEPT_ACTIONS and action != "reject_all":
        raise ValueError(f"unsupported action: {action!r}")

    prefs = local_preferences or {}
    confirmation = {
        "version": CONFIRMATION_VERSION,
        "confirmation_id": confirmation_id or f"confirm-{proposal['proposal_id']}",
        "proposal_id": str(proposal["proposal_id"]),
        "action": action,
        "selected_candidate_id": "" if action == "reject_all" else selected_candidate_id,
        "rejected_candidates": list(rejected_candidates or []),
        "local_preferences": {
            "candidate_weights": dict(prefs.get("candidate_weights", {})),
            "weight_source": str(prefs.get("weight_source", "user_confirmation")),
            "placement_offsets": dict(prefs.get("placement_offsets", {})),
            "notes": list(prefs.get("notes", [])),
        },
        "confirmed_by": str(prefs.get("confirmed_by", "user")),
    }
    errors = validate_confirmation_against_proposal(confirmation, proposal)
    if errors:
        raise ValueError("; ".join(errors))
    return confirmation


def apply_user_confirmation(
    proposal: dict[str, Any],
    confirmation: dict[str, Any],
    *,
    in_place: bool = False,
) -> dict[str, Any]:
    """Apply user confirmation to a proposal copy and return the updated proposal."""

    errors = validate_confirmation_against_proposal(confirmation, proposal)
    if errors:
        raise ValueError("; ".join(errors))

    updated = proposal if in_place else copy.deepcopy(proposal)
    action = str(confirmation.get("action", ""))

    updated["user_confirmation"] = copy.deepcopy(confirmation)

    if action == "reject_all":
        updated["confirmed_candidate_id"] = ""
        updated["needs_confirmation"] = True
        return updated

    updated["confirmed_candidate_id"] = str(confirmation["selected_candidate_id"])
    if action == "accept":
        updated["needs_confirmation"] = False
    elif action == "accept_with_risks":
        updated["needs_confirmation"] = False
    return updated


def load_user_confirmation(path: Path) -> dict[str, Any]:
    confirmation = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(confirmation, dict):
        raise ValueError("confirmation file must contain a JSON object")
    errors = validate_confirmation_document(confirmation)
    if errors:
        raise ValueError("; ".join(errors))
    return confirmation


def save_user_confirmation(path: Path, confirmation: dict[str, Any]) -> None:
    errors = validate_confirmation_document(confirmation)
    if errors:
        raise ValueError("; ".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(confirmation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def confirmation_round_trip(
    proposal: dict[str, Any],
    *,
    selected_candidate_id: str,
    action: str = "accept",
    rejected_candidates: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build confirmation, apply to proposal, and return (confirmation, updated_proposal)."""

    confirmation = build_user_confirmation(
        proposal=proposal,
        selected_candidate_id=selected_candidate_id,
        action=action,
        rejected_candidates=rejected_candidates,
    )
    path_errors = validate_confirmation_document(confirmation)
    if path_errors:
        raise ValueError(path_errors)
    updated = apply_user_confirmation(proposal, confirmation)
    return confirmation, updated
