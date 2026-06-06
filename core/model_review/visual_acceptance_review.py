"""Model-backed general visual acceptance review contracts.

This reviewer is for user-visible CAD output quality after execution/audit. It
is read-only: it can block delivery or suggest a repair plan, but it never
authorizes CAD writes, deletes, saves, or verified capability claims.
"""

from __future__ import annotations

from typing import Any

from core.model_review.common_contract import (
    COMMON_MODEL_REVIEW_FIELDS,
    common_agent_output_fields,
    validate_common_model_review_fields,
)
from core.model_review.provider_status import with_model_provider_status


MODEL_BACKED_VISUAL_ACCEPTANCE_KEY = "modelBackedVisualAcceptance"
VISUAL_ACCEPTANCE_BOOLEAN_FIELDS = (
    "canAskUserToReview",
    "aestheticAcceptable",
    "textReadable",
    "noMojibake",
    "noSevereOverlap",
    "noSevereClipping",
    "alignmentAcceptable",
    "contentMatchesIntent",
    "reusableOutputLikely",
    "evidenceBoundaryRespected",
    "nonScreenshotEvidenceChecked",
)
VISUAL_ACCEPTANCE_REQUIRED_FIELDS = (
    "status",
    *VISUAL_ACCEPTANCE_BOOLEAN_FIELDS,
    "blockingReasons",
    "visualProblems",
    "lookHereFirst",
    "repairRecommendation",
    *COMMON_MODEL_REVIEW_FIELDS,
)
PASS_STATUSES = {"pass", "ready", "ok", "complete", "complete_for_current_scope"}


def _status_passes(value: object) -> bool:
    return str(value or "").casefold() in PASS_STATUSES


def _bool_to_gate(value: object) -> str:
    return "pass" if value is True else "fail"


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def validate_visual_acceptance_model_review(report: dict[str, Any]) -> dict[str, Any]:
    """Validate the minimum shape required from a model visual acceptor."""

    if not isinstance(report, dict):
        return {
            "status": "fail",
            "issues": ["model visual acceptance review must be a JSON object"],
            "missingFields": list(VISUAL_ACCEPTANCE_REQUIRED_FIELDS),
        }
    missing = [field for field in VISUAL_ACCEPTANCE_REQUIRED_FIELDS if field not in report]
    issues: list[str] = []
    if missing:
        issues.append("missing required model visual acceptance fields")
    for field in VISUAL_ACCEPTANCE_BOOLEAN_FIELDS:
        if field in report and not isinstance(report.get(field), bool):
            issues.append(f"{field} must be boolean")
    if "blockingReasons" in report and not isinstance(report.get("blockingReasons"), list):
        issues.append("blockingReasons must be a list")
    if "visualProblems" in report and not isinstance(report.get("visualProblems"), list):
        issues.append("visualProblems must be a list")
    if "lookHereFirst" in report and not isinstance(report.get("lookHereFirst"), list):
        issues.append("lookHereFirst must be a list")
    if "repairRecommendation" in report and not isinstance(report.get("repairRecommendation"), dict):
        issues.append("repairRecommendation must be an object")
    if report.get("cadCommands"):
        issues.append("model visual acceptance review must not include direct CAD commands")
    if report.get("saveCurrentDwg") is True or report.get("savedCurrentDwg") is True:
        issues.append("model visual acceptance review must not save current DWG")
    if report.get("executionAuthorized") is True or report.get("mayExecuteCad") is True:
        issues.append("model visual acceptance review must not authorize execution")
    common_validation = validate_common_model_review_fields(report)
    issues.extend(str(issue) for issue in common_validation.get("issues", []))
    missing.extend(str(field) for field in common_validation.get("missingFields", []) if str(field) not in missing)
    return {
        "status": "pass" if not issues else "fail",
        "issues": issues,
        "missingFields": missing,
        "checked": ["required visual acceptance model review fields"] if not issues else [],
    }


def model_review_to_visual_acceptance_output(review: dict[str, Any]) -> dict[str, Any]:
    """Convert model JSON into the visual-acceptance Agent output shape."""

    validation = validate_visual_acceptance_model_review(review)
    blocking_reasons = [str(item) for item in _list(review.get("blockingReasons")) if str(item)]
    failed_visual_fields = [
        field for field in VISUAL_ACCEPTANCE_BOOLEAN_FIELDS if review.get(field) is not True
    ]
    model_review = with_model_provider_status(
        {**review, "validation": validation},
        validation=validation,
        provider="model_review",
        route=str(review.get("modelRoute") or "codex_cli_local"),
    )
    status = (
        "pass"
        if validation["status"] == "pass"
        and _status_passes(review.get("status"))
        and not failed_visual_fields
        and not blocking_reasons
        else "fail"
    )
    output: dict[str, Any] = {
        "status": status,
        "visualAcceptanceDecision": str(review.get("status") or validation["status"]),
        MODEL_BACKED_VISUAL_ACCEPTANCE_KEY: model_review,
        "modelBackedVisualAcceptanceRequired": True,
        "modelProviderStatus": model_review["modelProviderStatus"],
        "blockingReasons": [
            *blocking_reasons,
            *[f"{field}=false" for field in failed_visual_fields if field in review],
            *[str(issue) for issue in validation.get("issues", [])],
        ],
        "visualProblems": [str(item) for item in _list(review.get("visualProblems")) if str(item)],
        "lookHereFirst": [str(item) for item in _list(review.get("lookHereFirst")) if str(item)],
        "repairRecommendation": review.get("repairRecommendation")
        if isinstance(review.get("repairRecommendation"), dict)
        else {},
        "executionAuthorized": False,
        "mayExecuteCad": False,
        "savedCurrentDwg": False,
        "deletedEntities": False,
        "evidenceBoundary": {
            "checked": ["model visual readability and acceptance shape"] if status == "pass" else [],
            "notChecked": [
                "CAD geometry correctness",
                "created handles/readback",
                "current DWG save state",
                "asset sourceSpec/reuse replay",
                "user acceptance",
            ],
        },
        **common_agent_output_fields(review, status=status),
    }
    for field in VISUAL_ACCEPTANCE_BOOLEAN_FIELDS:
        output[field] = _bool_to_gate(review.get(field))
    return output
