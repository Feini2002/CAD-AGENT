"""Closeout claim classifier for adaptive CAD training growth."""

from __future__ import annotations

from typing import Any


CLAIM_STATES = {
    "verified",
    "ready_for_user_review",
    "not_run",
    "not_verified",
    "blocked",
    "needs_more_evidence",
    "not_implemented",
}


def _checks_pass(checks: list[dict[str, Any]]) -> bool:
    return bool(checks) and all(str(check.get("status")) == "pass" for check in checks)


def classify_adaptive_growth_closeout(
    *,
    status: str,
    checks: list[dict[str, Any]],
    readback_count: int,
    created_handle_count: int,
    replay_mode: str,
    visual_reviewed: bool,
    worker_trace_implemented: bool = False,
) -> dict[str, Any]:
    if status == "blocked":
        claim_state = "blocked"
    elif status in {"not_run", "skipped"}:
        claim_state = "not_run"
    elif not _checks_pass(checks):
        claim_state = "needs_more_evidence"
    elif created_handle_count and readback_count == created_handle_count:
        claim_state = "verified"
    elif created_handle_count and readback_count != created_handle_count:
        claim_state = "not_verified"
    elif visual_reviewed:
        claim_state = "ready_for_user_review"
    else:
        claim_state = "needs_more_evidence"

    allowed_claims = []
    if claim_state == "verified":
        allowed_claims.append(f"{replay_mode} deterministic checks and created-handle readback passed")
    elif claim_state == "ready_for_user_review":
        allowed_claims.append("visual review is ready for user review only")
    elif claim_state == "not_verified":
        allowed_claims.append("output exists but CAD readback proof is incomplete")
    elif claim_state == "blocked":
        allowed_claims.append("adaptive growth path is blocked")

    return {
        "schemaVersion": "adaptive-growth-closeout/v1",
        "status": "pass",
        "claimState": claim_state,
        "allowedClaimStates": sorted(CLAIM_STATES),
        "allowedClaims": allowed_claims,
        "disallowedClaimStates": [
            "project delivery ready",
            "construction document ready",
            "table C improved",
            "worker state proves CAD",
            "model judgment proves CAD",
            "screenshot proves geometry",
            "not_implemented" if not worker_trace_implemented else "",
        ],
        "evidenceBoundary": {
            "checked": ["checks", "created_handle_count", "readback_count"],
            "notChecked": ["用户人工视觉验收", "项目交付准备度", "Worker adaptive trace"],
            "forbiddenClaims": [
                "不能用 fake CAD、no-CAD draft、Worker state、模型 pass 或截图替代 CAD readback",
            ],
        },
    }
