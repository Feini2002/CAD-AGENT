"""Model-backed visual layout review contracts."""

from __future__ import annotations

from typing import Any

from core.model_review.common_contract import (
    COMMON_MODEL_REVIEW_FIELDS,
    common_agent_output_fields,
    validate_common_model_review_fields,
)
from core.model_review.provider_status import with_model_provider_status


MODEL_BACKED_VISUAL_REVIEW_KEY = "modelBackedReview"
VISUAL_BOOLEAN_FIELDS = (
    "layoutMatchesMetaphor",
    "primaryShelvesClear",
    "layoutReadabilityAcceptable",
    "aisleClearanceAcceptable",
    "contentDensityAcceptable",
    "sourceProofRolesSeparated",
    "layerSemanticsAcceptable",
    "futureExpansionClear",
    "retrievalPathReadable",
    "visualNoiseAcceptable",
    "nonScreenshotEvidenceChecked",
)
VISUAL_REQUIRED_FIELDS = (
    "status",
    *VISUAL_BOOLEAN_FIELDS,
    "blockingReasons",
    "visualProblems",
    "repairRecommendation",
    "softJudgment",
    *COMMON_MODEL_REVIEW_FIELDS,
)
PASS_STATUSES = {"pass", "ready", "ok", "complete", "complete_for_current_scope"}


def _status_passes(value: object) -> bool:
    return str(value or "").casefold() in PASS_STATUSES


def _bool_to_gate(value: object) -> str:
    return "pass" if value is True else "fail"


def validate_visual_layout_model_review(report: dict[str, Any]) -> dict[str, Any]:
    """Validate the minimum shape required from a model visual reviewer."""

    if not isinstance(report, dict):
        return {
            "status": "fail",
            "issues": ["model review must be a JSON object"],
            "missingFields": list(VISUAL_REQUIRED_FIELDS),
        }
    missing = [field for field in VISUAL_REQUIRED_FIELDS if field not in report]
    issues: list[str] = []
    if missing:
        issues.append("missing required model review fields")
    for field in VISUAL_BOOLEAN_FIELDS:
        if field in report and not isinstance(report.get(field), bool):
            issues.append(f"{field} must be boolean")
    if "blockingReasons" in report and not isinstance(report.get("blockingReasons"), list):
        issues.append("blockingReasons must be a list")
    if "visualProblems" in report and not isinstance(report.get("visualProblems"), list):
        issues.append("visualProblems must be a list")
    if "repairRecommendation" in report and not isinstance(report.get("repairRecommendation"), dict):
        issues.append("repairRecommendation must be an object")
    common_validation = validate_common_model_review_fields(report)
    issues.extend(str(issue) for issue in common_validation.get("issues", []))
    missing.extend(str(field) for field in common_validation.get("missingFields", []) if str(field) not in missing)
    status = "pass" if not issues else "fail"
    return {
        "status": status,
        "issues": issues,
        "missingFields": missing,
        "checked": ["required visual model review fields"] if not issues else [],
    }


def model_review_to_visual_agent_output(review: dict[str, Any]) -> dict[str, Any]:
    """Convert model JSON into the visual-layout Agent output shape."""

    validation = validate_visual_layout_model_review(review)
    failed_visual_fields = [field for field in VISUAL_BOOLEAN_FIELDS if review.get(field) is not True]
    model_review = with_model_provider_status(
        {**review, "validation": validation},
        validation=validation,
        provider="model_review",
        route=str(review.get("modelRoute") or "codex_cli_local"),
    )
    output: dict[str, Any] = {
        "status": "pass"
        if validation["status"] == "pass" and _status_passes(review.get("status")) and not failed_visual_fields
        else "fail",
        "visualLayoutReviewDecision": str(review.get("status") or validation["status"]),
        MODEL_BACKED_VISUAL_REVIEW_KEY: model_review,
        "modelBackedReviewRequired": True,
        "modelProviderStatus": model_review["modelProviderStatus"],
        "blockingReasons": list(review.get("blockingReasons", [])) if isinstance(review.get("blockingReasons"), list) else [],
        "visualProblems": list(review.get("visualProblems", [])) if isinstance(review.get("visualProblems"), list) else [],
        "repairRecommendation": review.get("repairRecommendation") if isinstance(review.get("repairRecommendation"), dict) else {},
        **common_agent_output_fields(review, status="pass" if validation["status"] == "pass" and _status_passes(review.get("status")) and not failed_visual_fields else "fail"),
    }
    output["blockingReasons"].extend(f"{field}=false" for field in failed_visual_fields if field in review)
    if validation["issues"]:
        output["blockingReasons"].extend(validation["issues"])
    for field in VISUAL_BOOLEAN_FIELDS:
        output[field] = _bool_to_gate(review.get(field))
    return output
