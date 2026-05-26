"""CAD validation report evidence summary and top-level evidence gates."""

from __future__ import annotations

from typing import Any

from core.verification.evidence_contract import (
    EVIDENCE_CAD_CAPABILITY_VERIFIED,
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_NOT_VERIFIED_BY_SCREENSHOT,
    GEOMETRY_VERIFIED_BY_READBACK,
    SCREENSHOT_VISUAL_AID_ONLY,
    evidence_summary_rollup,
    validate_evidence_state,
    validate_evidence_summary,
    validate_geometry_accuracy,
    validate_screenshot_role,
)

READBACK_STEP_IDS = frozenset({"inspect_readback", "block_alpha_readback"})
CAPABILITY_STEP_IDS = frozenset({"cad_capability_probe"})
DEFERRED_STEP_IDS = frozenset({"block_alpha_deferred_evidence"})
SCREENSHOT_STEP_IDS = frozenset({"capture_screen", "block_alpha_capture_screen"})


def apply_screenshot_step_evidence(record: dict[str, Any], step_id: str) -> None:
    if step_id in SCREENSHOT_STEP_IDS:
        record["screenshot_role"] = SCREENSHOT_VISUAL_AID_ONLY
        record["geometry_accuracy"] = GEOMETRY_NOT_VERIFIED_BY_SCREENSHOT


def validate_step_evidence_fields(record: dict[str, Any], *, step_id: str) -> str:
    label = f"step[{step_id}]"
    for field, validator in (
        ("evidence_state", validate_evidence_state),
        ("geometry_accuracy", validate_geometry_accuracy),
        ("screenshot_role", validate_screenshot_role),
    ):
        if field not in record:
            continue
        error = validator(record.get(field))
        if error:
            return f"{label}.{error}"
    return ""


def build_cad_validation_evidence_summary(
    records: list[dict[str, Any]],
    *,
    include_cad: bool,
) -> dict[str, Any]:
    """Aggregate evidence fields from validation step records."""

    evidence_state_counts: dict[str, int] = {}
    geometry_accuracy_counts: dict[str, int] = {}
    screenshot_role_counts: dict[str, int] = {}
    steps_with_evidence = 0
    for record in records:
        step_id = str(record.get("id", ""))
        error = validate_step_evidence_fields(record, step_id=step_id)
        if error:
            raise ValueError(error)
        evidence_state = record.get("evidence_state")
        if not evidence_state:
            continue
        steps_with_evidence += 1
        key = str(evidence_state)
        evidence_state_counts[key] = evidence_state_counts.get(key, 0) + 1
        geometry_accuracy = record.get("geometry_accuracy")
        if geometry_accuracy:
            geometry_key = str(geometry_accuracy)
            geometry_accuracy_counts[geometry_key] = geometry_accuracy_counts.get(geometry_key, 0) + 1
        screenshot_role = record.get("screenshot_role")
        if screenshot_role:
            role_key = str(screenshot_role)
            screenshot_role_counts[role_key] = screenshot_role_counts.get(role_key, 0) + 1

    rollup = evidence_summary_rollup(evidence_state_counts)
    readback_count = rollup["readback_geometry_verified_count"]
    capability_count = rollup["cad_capability_verified_count"]
    summary = {
        "steps_with_evidence_count": steps_with_evidence,
        "evidence_state_counts": evidence_state_counts,
        "geometry_accuracy_counts": geometry_accuracy_counts,
        "screenshot_role_counts": screenshot_role_counts,
        "include_cad": include_cad,
        **rollup,
        "geometry_verified_case_count": readback_count,
        "non_cad_only": readback_count == 0 and capability_count == 0,
    }
    summary_error = validate_evidence_summary(
        {
            **summary,
            "case_count": steps_with_evidence,
        }
    )
    if summary_error:
        raise ValueError(summary_error)
    return summary


def cad_validation_evidence_gate_failure(report: dict[str, Any]) -> str:
    """Reject top-level pass that contradicts sub-report evidence contracts."""

    summary = report.get("evidence_summary")
    if not isinstance(summary, dict):
        return "report.json missing evidence_summary"

    steps = {str(step.get("id", "")): step for step in report.get("steps", []) if isinstance(step, dict)}
    status = str(report.get("status", ""))
    include_cad = bool(report.get("include_cad"))
    block_alpha_only = bool(report.get("block_alpha_only"))

    if status == "pass" and not include_cad:
        if not summary.get("non_cad_only"):
            return "no-CAD validation pass requires evidence_summary.non_cad_only=true"
        if int(summary.get("readback_geometry_verified_count", 0)) > 0:
            return "no-CAD validation pass must not include readback_geometry_verified evidence"
        if int(summary.get("cad_capability_verified_count", 0)) > 0:
            return "no-CAD validation pass must not include cad_capability_verified evidence"
        deferred = steps.get("block_alpha_deferred_evidence")
        if deferred and deferred.get("status") == "pass":
            if deferred.get("evidence_state") != EVIDENCE_DEFERRED_CAD_READBACK:
                return (
                    "block_alpha_deferred_evidence must use "
                    f"evidence_state={EVIDENCE_DEFERRED_CAD_READBACK!r} on no-CAD pass"
                )
        return ""

    if status != "pass" or not include_cad:
        return ""

    if block_alpha_only:
        readback_step = steps.get("block_alpha_readback")
        if readback_step and readback_step.get("status") == "pass":
            if readback_step.get("evidence_state") != EVIDENCE_READBACK_GEOMETRY_VERIFIED:
                return (
                    "CAD validation pass requires block_alpha_readback "
                    f"evidence_state={EVIDENCE_READBACK_GEOMETRY_VERIFIED!r}"
                )
        elif readback_step and readback_step.get("status") not in {"not_run", "fail"}:
            return "CAD validation pass requires block_alpha_readback step evidence"
        return ""

    readback_step = steps.get("inspect_readback")
    capability_step = steps.get("cad_capability_probe")
    if readback_step and readback_step.get("status") == "pass":
        if readback_step.get("evidence_state") != EVIDENCE_READBACK_GEOMETRY_VERIFIED:
            return (
                "CAD validation pass requires inspect_readback "
                f"evidence_state={EVIDENCE_READBACK_GEOMETRY_VERIFIED!r}"
            )
        if readback_step.get("geometry_accuracy") != GEOMETRY_VERIFIED_BY_READBACK:
            return (
                "CAD validation pass requires inspect_readback "
                f"geometry_accuracy={GEOMETRY_VERIFIED_BY_READBACK!r}"
            )
    elif readback_step and readback_step.get("status") not in {"not_run", "fail"}:
        return "CAD validation pass requires inspect_readback step evidence"

    if capability_step and capability_step.get("status") == "pass":
        if capability_step.get("evidence_state") != EVIDENCE_CAD_CAPABILITY_VERIFIED:
            return (
                "CAD validation pass requires cad_capability_probe "
                f"evidence_state={EVIDENCE_CAD_CAPABILITY_VERIFIED!r}"
            )
    elif capability_step and capability_step.get("status") not in {"not_run", "fail"}:
        return "CAD validation pass requires cad_capability_probe step evidence"

    block_alpha = report.get("block_alpha")
    if isinstance(block_alpha, dict) and block_alpha.get("step_id") == "block_alpha_readback":
        if not block_alpha.get("geometry_verified"):
            return "CAD validation pass requires block_alpha.geometry_verified when block_alpha_readback ran"
    return ""
