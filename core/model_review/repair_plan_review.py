"""Model-backed repair-plan review contracts.

Model repair output is a proposal only. It may identify handles, bboxes, and
candidate operations for a later rule/CAD executor, but it never authorizes
direct CAD commands, saves, broad deletes, or formal-layer edits.
"""

from __future__ import annotations

from typing import Any

from core.model_review.common_contract import (
    COMMON_MODEL_REVIEW_FIELDS,
    common_agent_output_fields,
    validate_common_model_review_fields,
)
from core.model_review.provider_status import with_model_provider_status


REPAIR_PLAN_REQUIRED_FIELDS = (
    "status",
    "scopeMode",
    "rootCause",
    "repairMode",
    "targetHandles",
    "targetBbox",
    "targetLayers",
    "whyLocalRepairIsEnough",
    "whyFullRedrawIsNotAllowedOrNeeded",
    "requiresUserPermission",
    "protectedNeighbors",
    "operations",
    "evidenceRequired",
    "executionPolicy",
    "blockingReasons",
    *COMMON_MODEL_REVIEW_FIELDS,
)
PASS_STATUSES = {"pass", "ready", "ok", "complete", "complete_for_current_scope"}
ALLOWED_SCOPE_MODES = {"local_repair", "focused_repair", "repair_candidate", "manual_review"}
FORBIDDEN_SCOPE_MODES = {"whole_modelspace", "all_visible", "current_screen", "training_panel", "global_preview_bbox"}
ALLOWED_OPERATION_ACTIONS = {"update", "delete_replace", "add_missing", "annotate_for_review"}


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _unique_strings(values: Any) -> list[str]:
    result: list[str] = []
    for value in _list(values):
        text = str(value).strip()
        if text and text not in result:
            result.append(text)
    return result


def _status_passes(value: object) -> bool:
    return str(value or "").casefold() in PASS_STATUSES


def validate_repair_plan_model_review(report: dict[str, Any]) -> dict[str, Any]:
    """Validate that a model repair plan is safe as a proposal only."""

    if not isinstance(report, dict):
        return {
            "status": "fail",
            "issues": ["model repair plan must be a JSON object"],
            "missingFields": list(REPAIR_PLAN_REQUIRED_FIELDS),
        }
    missing = [field for field in REPAIR_PLAN_REQUIRED_FIELDS if field not in report]
    issues: list[str] = []
    if missing:
        issues.append("missing required model repair plan fields")
    scope_mode = str(report.get("scopeMode") or "")
    if scope_mode in FORBIDDEN_SCOPE_MODES:
        issues.append("model repair plan must target local handles or bbox, not broad modelspace/screen scope")
    elif scope_mode and scope_mode not in ALLOWED_SCOPE_MODES:
        issues.append("model repair plan has unknown scopeMode")
    if "targetHandles" in report and not isinstance(report.get("targetHandles"), list):
        issues.append("targetHandles must be a list")
    if "targetBbox" in report and not isinstance(report.get("targetBbox"), dict):
        issues.append("targetBbox must be an object")
    if "targetLayers" in report and not isinstance(report.get("targetLayers"), list):
        issues.append("targetLayers must be a list")
    for field in ("rootCause", "repairMode", "whyLocalRepairIsEnough", "whyFullRedrawIsNotAllowedOrNeeded"):
        if field in report and not isinstance(report.get(field), str):
            issues.append(f"{field} must be a string")
    if "requiresUserPermission" in report and not isinstance(report.get("requiresUserPermission"), bool):
        issues.append("requiresUserPermission must be boolean")
    if "protectedNeighbors" in report and not isinstance(report.get("protectedNeighbors"), list):
        issues.append("protectedNeighbors must be a list")
    if "evidenceRequired" in report and not isinstance(report.get("evidenceRequired"), list):
        issues.append("evidenceRequired must be a list")
    if "blockingReasons" in report and not isinstance(report.get("blockingReasons"), list):
        issues.append("blockingReasons must be a list")
    if str(report.get("executionPolicy") or "") != "proposal_only":
        issues.append("model repair plan executionPolicy must be proposal_only")
    if report.get("cadCommands"):
        issues.append("model repair plan must not include direct CAD commands")
    if report.get("saveCurrentDwg") is True or report.get("savedCurrentDwg") is True:
        issues.append("model repair plan must not save current DWG")
    if report.get("executionAuthorized") is True or report.get("mayExecuteCad") is True:
        issues.append("model repair plan must not authorize execution")
    common_validation = validate_common_model_review_fields(report)
    issues.extend(str(issue) for issue in common_validation.get("issues", []))
    missing.extend(str(field) for field in common_validation.get("missingFields", []) if str(field) not in missing)
    operations = report.get("operations")
    if "operations" in report and not isinstance(operations, list):
        issues.append("operations must be a list")
    for index, operation in enumerate(_list(operations)):
        if not isinstance(operation, dict):
            issues.append(f"operations[{index}] must be an object")
            continue
        action = str(operation.get("action") or "")
        if action not in ALLOWED_OPERATION_ACTIONS:
            issues.append(f"operations[{index}].action is not allowed")
        if action == "delete_replace" and not _list(operation.get("targetHandles")) and not _dict(operation.get("targetBbox")):
            issues.append("delete_replace operations must name targetHandles or targetBbox")
    return {
        "status": "pass" if not issues else "fail",
        "issues": issues,
        "missingFields": missing,
        "checked": ["proposal-only repair plan fields"] if not issues else [],
    }


def model_review_to_repair_plan_candidate(review: dict[str, Any]) -> dict[str, Any]:
    """Convert model JSON into a non-executable repair-plan candidate."""

    validation = validate_repair_plan_model_review(review)
    model_review = with_model_provider_status(
        {**review, "validation": validation},
        validation=validation,
        provider="model_review",
        route=str(review.get("modelRoute") or "codex_cli_local"),
    )
    blocking_reasons = [str(item) for item in _list(review.get("blockingReasons")) if str(item)]
    status = "pass" if validation["status"] == "pass" and _status_passes(review.get("status")) and not blocking_reasons else "fail"
    operations = [
        dict(operation)
        for operation in _list(review.get("operations"))
        if isinstance(operation, dict) and str(operation.get("action") or "") in ALLOWED_OPERATION_ACTIONS
    ]
    candidate = {
        "scopeMode": str(review.get("scopeMode") or ""),
        "targetHandles": _unique_strings(review.get("targetHandles")),
        "targetBbox": _dict(review.get("targetBbox")),
        "targetLayers": _unique_strings(review.get("targetLayers")),
        "rootCause": str(review.get("rootCause") or ""),
        "repairMode": str(review.get("repairMode") or ""),
        "whyLocalRepairIsEnough": str(review.get("whyLocalRepairIsEnough") or ""),
        "whyFullRedrawIsNotAllowedOrNeeded": str(review.get("whyFullRedrawIsNotAllowedOrNeeded") or ""),
        "requiresUserPermission": bool(review.get("requiresUserPermission")),
        "protectedNeighbors": _unique_strings(review.get("protectedNeighbors")),
        "operations": operations,
        "evidenceRequired": _unique_strings(review.get("evidenceRequired")),
        "executionPolicy": "proposal_only",
    } if status == "pass" else {}
    return {
        "status": status,
        "repairPlanCandidate": candidate,
        "modelBackedRepairPlan": model_review,
        "modelProviderStatus": model_review["modelProviderStatus"],
        "blockingReasons": [*blocking_reasons, *[str(issue) for issue in validation.get("issues", [])]],
        "executionAuthorized": False,
        "mayExecuteCad": False,
        "savedCurrentDwg": False,
        "deletedEntities": False,
        "evidenceBoundary": {
            "checked": ["model repair plan proposal shape"] if status == "pass" else [],
            "notChecked": [
                "CAD execution",
                "entity deletion",
                "current DWG save state",
                "formal layer modification",
                "post-repair readback",
            ],
        },
        **common_agent_output_fields(review, status=status),
    }
