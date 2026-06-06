"""Model-backed asset-governor review contracts.

The asset-governor model reviewer is advisory. It may suggest
classification, source-boundary, clean-source, and repair-plan candidates, but
it must not grant CAD execution, save permission, or override rule gates.
"""

from __future__ import annotations

from typing import Any

from core.model_review.common_contract import (
    COMMON_MODEL_REVIEW_FIELDS,
    common_agent_output_fields,
    validate_common_model_review_fields,
)
from core.model_review.provider_status import with_model_provider_status


ASSET_GOVERNOR_REQUIRED_FIELDS = (
    "status",
    "assetLifecycleDecision",
    "sourceBoundaryDecision",
    "cleanSourceAllowed",
    "quarantineReason",
    "requiredChildAgents",
    "nativeVisibleEvidenceRequired",
    "reuseProofRequired",
    "classificationSuggestion",
    "sourceBoundaryRecommendation",
    "cleanSourceRecommendation",
    "repairPlanRecommendation",
    "blockingReasons",
    "evidenceRequired",
    *COMMON_MODEL_REVIEW_FIELDS,
)
PASS_STATUSES = {"pass", "ready", "ok", "complete", "complete_for_current_scope"}
UNSAFE_EXECUTION_KEYS = (
    "cadCommands",
    "executeNow",
    "executionAuthorized",
    "mayExecuteCad",
    "saveCurrentDwg",
    "savedCurrentDwg",
    "deleteEntities",
    "deletedEntities",
)


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _status_passes(value: object) -> bool:
    return str(value or "").casefold() in PASS_STATUSES


def validate_asset_governor_model_review(report: dict[str, Any]) -> dict[str, Any]:
    """Validate the minimum shape required from a model asset governor."""

    if not isinstance(report, dict):
        return {
            "status": "fail",
            "issues": ["model asset governor review must be a JSON object"],
            "missingFields": list(ASSET_GOVERNOR_REQUIRED_FIELDS),
        }
    missing = [field for field in ASSET_GOVERNOR_REQUIRED_FIELDS if field not in report]
    issues: list[str] = []
    if missing:
        issues.append("missing required model asset governor fields")
    for field in (
        "classificationSuggestion",
        "sourceBoundaryRecommendation",
        "cleanSourceRecommendation",
        "repairPlanRecommendation",
    ):
        if field in report and not isinstance(report.get(field), dict):
            issues.append(f"{field} must be an object")
    for field in ("blockingReasons", "evidenceRequired"):
        if field in report and not isinstance(report.get(field), list):
            issues.append(f"{field} must be a list")
    for field in ("assetLifecycleDecision", "sourceBoundaryDecision", "quarantineReason"):
        if field in report and not isinstance(report.get(field), str):
            issues.append(f"{field} must be a string")
    for field in ("cleanSourceAllowed", "nativeVisibleEvidenceRequired", "reuseProofRequired"):
        if field in report and not isinstance(report.get(field), bool):
            issues.append(f"{field} must be boolean")
    if "requiredChildAgents" in report and not isinstance(report.get("requiredChildAgents"), list):
        issues.append("requiredChildAgents must be a list")
    clean = _dict(report.get("cleanSourceRecommendation"))
    if "cleanSourceAllowed" in clean and not isinstance(clean.get("cleanSourceAllowed"), bool):
        issues.append("cleanSourceRecommendation.cleanSourceAllowed must be boolean")
    unsafe_present = [key for key in UNSAFE_EXECUTION_KEYS if key in report]
    if unsafe_present:
        issues.append("model asset governor review must not include direct execution or save/delete authorization")
    common_validation = validate_common_model_review_fields(report)
    issues.extend(str(issue) for issue in common_validation.get("issues", []))
    missing.extend(str(field) for field in common_validation.get("missingFields", []) if str(field) not in missing)
    return {
        "status": "pass" if not issues else "fail",
        "issues": issues,
        "missingFields": missing,
        "checked": ["required model asset governor fields"] if not issues else [],
    }


def model_review_to_asset_governor_assistance(review: dict[str, Any]) -> dict[str, Any]:
    """Convert model JSON into advisory asset-governor evidence."""

    validation = validate_asset_governor_model_review(review)
    model_review = with_model_provider_status(
        {**review, "validation": validation},
        validation=validation,
        provider="model_review",
        route=str(review.get("modelRoute") or "codex_cli_local"),
    )
    blocking_reasons = [str(item) for item in _list(review.get("blockingReasons")) if str(item)]
    issues = [str(issue) for issue in validation.get("issues", [])]
    status = "pass" if validation["status"] == "pass" and _status_passes(review.get("status")) and not blocking_reasons else "fail"
    return {
        "status": status,
        "modelInvoked": bool(model_review.get("modelInvoked", True)),
        "modelProviderStatus": model_review["modelProviderStatus"],
        "assetLifecycleDecision": str(review.get("assetLifecycleDecision") or ""),
        "sourceBoundaryDecision": str(review.get("sourceBoundaryDecision") or ""),
        "cleanSourceAllowed": bool(review.get("cleanSourceAllowed")),
        "quarantineReason": str(review.get("quarantineReason") or ""),
        "requiredChildAgents": [str(item) for item in _list(review.get("requiredChildAgents")) if str(item)],
        "nativeVisibleEvidenceRequired": bool(review.get("nativeVisibleEvidenceRequired")),
        "reuseProofRequired": bool(review.get("reuseProofRequired")),
        "classificationSuggestion": _dict(review.get("classificationSuggestion")),
        "sourceBoundaryRecommendation": _dict(review.get("sourceBoundaryRecommendation")),
        "cleanSourceRecommendation": _dict(review.get("cleanSourceRecommendation")),
        "repairPlanRecommendation": _dict(review.get("repairPlanRecommendation")),
        "blockingReasons": [*blocking_reasons, *issues],
        "evidenceRequired": [str(item) for item in _list(review.get("evidenceRequired")) if str(item)],
        "validation": validation,
        "executionAuthorized": False,
        "mayExecuteCad": False,
        "savedCurrentDwg": False,
        "deletedEntities": False,
        "evidenceBoundary": {
            "checked": ["model asset classification and source-boundary suggestions"],
            "notChecked": [
                "CAD handles/readback",
                "native DWG save state",
                "clean source permission",
                "reuse replay",
            ],
        },
        **common_agent_output_fields(review, status=status),
    }
