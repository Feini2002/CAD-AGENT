"""Shared contract helpers for model-backed pipeline Agent reviews."""

from __future__ import annotations

from typing import Any


COMMON_MODEL_REVIEW_FIELDS = (
    "decision",
    "statePatch",
    "finalResponseAllowedClaims",
    "evidenceUsed",
    "evidenceMissing",
    "assumptions",
    "alternativesConsidered",
    "blockingReasons",
    "nextRequiredEvidence",
    "learningCandidate",
    "toolIntent",
)

STATE_PATCH_REQUIRED_FIELDS = (
    "phase",
    "phaseLabelForUser",
    "completedEvidence",
    "pendingEvidence",
    "pendingUserAction",
    "blockedReason",
    "nextSafeAction",
)

UNSAFE_EXECUTION_KEYS = (
    "cadCommands",
    "executeNow",
    "executionAuthorized",
    "mayExecuteCad",
    "saveCurrentDwg",
    "savedCurrentDwg",
    "deleteEntities",
    "deletedEntities",
    "moveEntities",
    "purge",
    "cleanup",
    "verifiedStatusClaim",
    "tableCClaim",
    "userAccepted",
)


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def unique_strings(value: Any) -> list[str]:
    result: list[str] = []
    for item in _list(value):
        text = str(item).strip()
        if text and text not in result:
            result.append(text)
    return result


def validate_common_model_review_fields(report: dict[str, Any]) -> dict[str, Any]:
    """Validate fields every model-backed Agent prompt must return."""

    if not isinstance(report, dict):
        return {
            "status": "fail",
            "issues": ["model review must be a JSON object"],
            "missingFields": list(COMMON_MODEL_REVIEW_FIELDS),
        }
    missing = [field for field in COMMON_MODEL_REVIEW_FIELDS if field not in report]
    issues: list[str] = []
    if missing:
        issues.append("missing required common model review fields")

    state_patch = report.get("statePatch")
    if "statePatch" in report and not isinstance(state_patch, dict):
        issues.append("statePatch must be an object")
    if isinstance(state_patch, dict):
        missing_state = [field for field in STATE_PATCH_REQUIRED_FIELDS if field not in state_patch]
        if missing_state:
            issues.append("statePatch missing required fields")
            missing.extend(f"statePatch.{field}" for field in missing_state)
        for field in ("completedEvidence", "pendingEvidence"):
            if field in state_patch and not isinstance(state_patch.get(field), list):
                issues.append(f"statePatch.{field} must be a list")

    for field in (
        "finalResponseAllowedClaims",
        "evidenceUsed",
        "evidenceMissing",
        "assumptions",
        "alternativesConsidered",
        "blockingReasons",
        "nextRequiredEvidence",
    ):
        if field in report and not isinstance(report.get(field), list):
            issues.append(f"{field} must be a list")
    if "learningCandidate" in report and not isinstance(report.get("learningCandidate"), dict):
        issues.append("learningCandidate must be an object")
    if "softJudgment" in report and not isinstance(report.get("softJudgment"), dict):
        issues.append("softJudgment must be an object")

    unsafe_present = [key for key in UNSAFE_EXECUTION_KEYS if key in report]
    if unsafe_present:
        issues.append("model review must not include direct execution, save/delete, verified, table C, or user-acceptance claims")

    return {
        "status": "pass" if not issues else "fail",
        "issues": issues,
        "missingFields": missing,
        "checked": ["common model review fields"] if not issues else [],
    }


def common_agent_output_fields(review: dict[str, Any], *, status: str) -> dict[str, Any]:
    """Copy safe common model fields into a converted Agent output."""

    return {
        "statePatch": _dict(review.get("statePatch")),
        "decision": str(review.get("decision") or ""),
        "finalResponseAllowedClaims": unique_strings(review.get("finalResponseAllowedClaims")) if status == "pass" else [],
        "evidenceUsed": unique_strings(review.get("evidenceUsed")),
        "evidenceMissing": unique_strings(review.get("evidenceMissing")),
        "assumptions": unique_strings(review.get("assumptions")),
        "alternativesConsidered": unique_strings(review.get("alternativesConsidered")),
        "nextRequiredEvidence": unique_strings(review.get("nextRequiredEvidence")),
        "learningCandidate": _dict(review.get("learningCandidate")),
        "softJudgment": _dict(review.get("softJudgment")),
        "toolIntent": review.get("toolIntent") if isinstance(review.get("toolIntent"), dict) else None,
    }
