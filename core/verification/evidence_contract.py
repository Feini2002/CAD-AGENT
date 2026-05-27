"""Shared evidence-state vocabulary and CAD capability contract metadata."""

from __future__ import annotations

from typing import Any

from core.verification.evidence_vocabulary import (
    BENCHMARK_FAILURE_CATEGORIES,
    CONTRACT_VERSION,
    DEFERRED_VERIFICATION,
    ENTITY_CONTRACTS,
    EVIDENCE_BENCHMARK_PASS_NON_CAD,
    EVIDENCE_BLOCKED_EXPECTED_NON_CAD,
    EVIDENCE_CAD_CAPABILITY_VERIFIED,
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
    EVIDENCE_INVALID_CONFIGURATION,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    EVIDENCE_STATE_VALUES,
    FAILURE_EVIDENCE_STATES,
    GEOMETRY_ACCURACY_VALUES,
    GEOMETRY_NOT_VERIFIED_BY_SCREENSHOT,
    GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE,
    GEOMETRY_VERIFIED_BY_READBACK,
    GEOMETRY_VERIFIED_EVIDENCE_STATES,
    NON_CAD_GEOMETRY_ACCURACY,
    REQUIRED_CAPABILITY_PROBE_FIELDS,
    REQUIRED_READBACK_REPORT_FIELDS,
    SCREENSHOT_NOT_APPLICABLE,
    SCREENSHOT_ROLE_VALUES,
    SCREENSHOT_VISUAL_AID_ONLY,
)


def validate_evidence_state(value: object) -> str:
    if not isinstance(value, str) or not value:
        return "evidence_state must be a non-empty string"
    if value not in EVIDENCE_STATE_VALUES:
        return f"unknown evidence_state: {value!r}; allowed={sorted(EVIDENCE_STATE_VALUES)}"
    return ""


def validate_geometry_accuracy(value: object) -> str:
    if not isinstance(value, str) or not value:
        return "geometry_accuracy must be a non-empty string"
    if value not in GEOMETRY_ACCURACY_VALUES:
        return f"unknown geometry_accuracy: {value!r}; allowed={sorted(GEOMETRY_ACCURACY_VALUES)}"
    return ""


def validate_screenshot_role(value: object) -> str:
    if not isinstance(value, str) or not value:
        return "screenshot_role must be a non-empty string"
    if value not in SCREENSHOT_ROLE_VALUES:
        return f"unknown screenshot_role: {value!r}; allowed={sorted(SCREENSHOT_ROLE_VALUES)}"
    return ""


def validate_evidence_triplet(
    payload: dict[str, Any],
    *,
    label: str = "evidence",
) -> str:
    for field, validator in (
        ("evidence_state", validate_evidence_state),
        ("geometry_accuracy", validate_geometry_accuracy),
        ("screenshot_role", validate_screenshot_role),
    ):
        if field not in payload:
            continue
        error = validator(payload.get(field))
        if error:
            return f"{label}.{error}"
    return ""


def is_geometry_verified_evidence_state(evidence_state: str) -> bool:
    return evidence_state in GEOMETRY_VERIFIED_EVIDENCE_STATES


def evidence_summary_rollup(evidence_state_counts: dict[str, int]) -> dict[str, int]:
    """Derive machine-assertable counters from raw evidence_state_counts."""

    return {
        "benchmark_pass_non_cad_count": evidence_state_counts.get(EVIDENCE_BENCHMARK_PASS_NON_CAD, 0),
        "blocked_expected_non_cad_count": evidence_state_counts.get(EVIDENCE_BLOCKED_EXPECTED_NON_CAD, 0),
        "invalid_configuration_count": evidence_state_counts.get(EVIDENCE_INVALID_CONFIGURATION, 0),
        "readback_geometry_verified_count": evidence_state_counts.get(EVIDENCE_READBACK_GEOMETRY_VERIFIED, 0),
        "cad_capability_verified_count": evidence_state_counts.get(EVIDENCE_CAD_CAPABILITY_VERIFIED, 0),
        "deferred_cad_readback_count": evidence_state_counts.get(EVIDENCE_DEFERRED_CAD_READBACK, 0),
        "dry_run_valid_plan_only_count": evidence_state_counts.get(EVIDENCE_DRY_RUN_VALID_PLAN_ONLY, 0),
    }


def validate_evidence_summary(summary: dict[str, Any], *, label: str = "evidence_summary") -> str:
    """Validate aggregated benchmark evidence summary consistency."""

    if not isinstance(summary, dict):
        return f"{label} must be an object"
    case_count = summary.get("case_count")
    state_counts = summary.get("evidence_state_counts")
    if not isinstance(case_count, int) or case_count < 0:
        return f"{label}.case_count must be a non-negative integer"
    if not isinstance(state_counts, dict):
        return f"{label}.evidence_state_counts must be an object"
    counted = sum(int(value) for value in state_counts.values())
    if counted != case_count:
        return f"{label} evidence_state_counts sum to {counted}, expected {case_count}"
    for state, count in state_counts.items():
        if validate_evidence_state(state):
            return f"{label} has unknown evidence_state {state!r}"
    geometry_counts = summary.get("geometry_accuracy_counts")
    if isinstance(geometry_counts, dict):
        for accuracy in geometry_counts:
            if validate_geometry_accuracy(accuracy):
                return f"{label} has unknown geometry_accuracy {accuracy!r}"
    readback_count = int(summary.get("readback_geometry_verified_count", 0))
    non_cad_only = summary.get("non_cad_only")
    if non_cad_only is True and readback_count > 0:
        return f"{label} non_cad_only=true but readback_geometry_verified_count={readback_count}"
    if non_cad_only is False and readback_count == 0 and case_count > 0:
        pass
    rollup = evidence_summary_rollup(state_counts)
    for key, expected_count in rollup.items():
        if summary.get(key) != expected_count:
            return f"{label}.{key}={summary.get(key)!r}; expected {expected_count}"
    return ""


def validate_failure_expected_contract(expected: dict[str, Any], *, label: str = "case") -> list[str]:
    """Ensure failure benchmark cases declare blocked/invalid outcomes and structured reasons."""

    errors: list[str] = []
    evidence_state = expected.get("evidence_state")
    if evidence_state not in FAILURE_EVIDENCE_STATES:
        if expected.get("failure_category"):
            errors.append(f"{label}.expected.failure_category is only valid for failure evidence_state")
        if expected.get("contains_blocked_reason"):
            errors.append(f"{label}.expected.contains_blocked_reason is only valid for failure evidence_state")
        pipeline_status = expected.get("pipeline_status")
        if pipeline_status in {"blocked", "invalid"}:
            errors.append(
                f"{label}.expected.pipeline_status={pipeline_status!r} requires "
                f"evidence_state in {sorted(FAILURE_EVIDENCE_STATES)}"
            )
        return errors

    pipeline_status = expected.get("pipeline_status")
    if evidence_state == EVIDENCE_BLOCKED_EXPECTED_NON_CAD and pipeline_status != "blocked":
        errors.append(f"{label}.expected blocked_expected_non_cad requires pipeline_status=blocked")
    if evidence_state == EVIDENCE_INVALID_CONFIGURATION and pipeline_status != "invalid":
        errors.append(f"{label}.expected invalid_configuration requires pipeline_status=invalid")

    failure_category = expected.get("failure_category")
    blocked_reason = expected.get("contains_blocked_reason")
    has_failure_category = isinstance(failure_category, str) and bool(failure_category)
    has_blocked_reason = isinstance(blocked_reason, str) and bool(blocked_reason)
    if not has_failure_category and not has_blocked_reason:
        errors.append(
            f"{label}.expected failure case requires failure_category or contains_blocked_reason"
        )
    if has_failure_category and failure_category not in BENCHMARK_FAILURE_CATEGORIES:
        errors.append(
            f"{label}.expected.failure_category={failure_category!r} is not in benchmark failure vocabulary"
        )
    return errors


def classify_benchmark_pipeline_evidence(
    *,
    pipeline_status: Any,
    dry_run_status: Any,
    verification_status: Any,
) -> dict[str, str]:
    """Map benchmark pipeline statuses to the shared evidence vocabulary."""

    if verification_status == "geometry_verified":
        return {
            "evidence_state": EVIDENCE_READBACK_GEOMETRY_VERIFIED,
            "geometry_accuracy": GEOMETRY_VERIFIED_BY_READBACK,
            "screenshot_role": SCREENSHOT_VISUAL_AID_ONLY,
        }
    if pipeline_status == "blocked":
        return {
            "evidence_state": EVIDENCE_BLOCKED_EXPECTED_NON_CAD,
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "screenshot_role": SCREENSHOT_VISUAL_AID_ONLY,
        }
    if pipeline_status == "invalid":
        return {
            "evidence_state": EVIDENCE_INVALID_CONFIGURATION,
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "screenshot_role": SCREENSHOT_VISUAL_AID_ONLY,
        }
    if pipeline_status == "ok" and dry_run_status == "valid" and verification_status == "unverified":
        return {
            "evidence_state": EVIDENCE_BENCHMARK_PASS_NON_CAD,
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "screenshot_role": SCREENSHOT_VISUAL_AID_ONLY,
        }
    if dry_run_status == "valid":
        return {
            "evidence_state": EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "screenshot_role": SCREENSHOT_VISUAL_AID_ONLY,
        }
    return {
        "evidence_state": EVIDENCE_DEFERRED_CAD_READBACK,
        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": SCREENSHOT_VISUAL_AID_ONLY,
    }


def contract_metadata() -> dict[str, Any]:
    return {
        "version": CONTRACT_VERSION,
        "entities": ENTITY_CONTRACTS,
        "deferred_verification": list(DEFERRED_VERIFICATION),
    }


def capability_probe_evidence(*, status: str) -> dict[str, str]:
    if status == "cad_capability_verified":
        return {
            "evidence_state": EVIDENCE_CAD_CAPABILITY_VERIFIED,
            "geometry_accuracy": GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE,
            "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
        }
    if status == "external_blocker":
        return {
            "evidence_state": EVIDENCE_DEFERRED_CAD_READBACK,
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
        }
    return {
        "evidence_state": EVIDENCE_DEFERRED_CAD_READBACK,
        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
    }


def readback_report_evidence(*, status: str, screenshot_path: str | None = None) -> dict[str, str]:
    screenshot_role = SCREENSHOT_VISUAL_AID_ONLY if screenshot_path else SCREENSHOT_NOT_APPLICABLE
    if status == "geometry_verified":
        return {
            "evidence_state": EVIDENCE_READBACK_GEOMETRY_VERIFIED,
            "geometry_accuracy": GEOMETRY_VERIFIED_BY_READBACK,
            "screenshot_role": screenshot_role,
        }
    return {
        "evidence_state": EVIDENCE_DEFERRED_CAD_READBACK,
        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": screenshot_role,
    }


def apply_capability_probe_contract(report: dict[str, Any]) -> dict[str, Any]:
    status = str(report.get("status", ""))
    evidence = capability_probe_evidence(status=status)
    report["contract_version"] = CONTRACT_VERSION
    report.update(evidence)
    report["contract"] = contract_metadata()
    report["deferred_verification"] = list(DEFERRED_VERIFICATION)
    limitations = list(report.get("limitations", []))
    limitations.append(
        "cad_capability_verified only covers preview-layer primitive write/readback; "
        "it does not prove block insertion, real block libraries, or arbitrary CAD_PLAN accuracy."
    )
    report["limitations"] = limitations
    return report


def apply_readback_report_contract(report: dict[str, Any], *, screenshot_path: str | None = None) -> dict[str, Any]:
    status = str(report.get("status", ""))
    evidence = readback_report_evidence(status=status, screenshot_path=screenshot_path)
    report.update(evidence)
    if status != "geometry_verified":
        limitations = list(report.get("limitations", []))
        if NON_CAD_GEOMETRY_ACCURACY not in " ".join(limitations):
            limitations.append("Geometry accuracy requires created-handle readback with geometry_verified status.")
        report["limitations"] = limitations
    return report


def validate_capability_probe_evidence(report: dict[str, Any]) -> str:
    for field in REQUIRED_CAPABILITY_PROBE_FIELDS:
        if field not in report:
            return f"cad_capability_probe missing required field: {field}"

    status = str(report.get("status", ""))
    expected = capability_probe_evidence(status=status)
    for key, value in expected.items():
        if report.get(key) != value:
            return f"cad_capability_probe.{key}={report.get(key)!r}; expected {value!r} for status={status!r}"

    if status == "cad_capability_verified" and report.get("geometry_accuracy") == GEOMETRY_VERIFIED_BY_READBACK:
        return "cad_capability_probe must not claim baseline readback_geometry_verified geometry_accuracy"

    if status == "cad_capability_verified":
        from core.verification.entity_level_evidence import entity_level_evidence_allows_probe_pass

        entity_evidence = report.get("entity_evidence")
        if not isinstance(entity_evidence, list):
            return "cad_capability_probe missing entity_evidence list for cad_capability_verified"
        if not entity_level_evidence_allows_probe_pass(entity_evidence):
            return "cad_capability_probe entity_evidence incomplete for cad_capability_verified"

        session_guard = report.get("session_guard")
        if not isinstance(session_guard, dict):
            return "cad_capability_probe missing session_guard for cad_capability_verified"
        if session_guard.get("status") != "consistent":
            return (
                "cad_capability_probe session_guard.status="
                f"{session_guard.get('status')!r}; expected 'consistent'"
            )
        comparison = session_guard.get("comparison")
        if not isinstance(comparison, dict):
            return "cad_capability_probe session_guard missing comparison for cad_capability_verified"
        checks = comparison.get("checks", [])
        if not isinstance(checks, list):
            return "cad_capability_probe session_guard comparison checks invalid"
        identity_checks = [
            check
            for check in checks
            if isinstance(check, dict) and check.get("name") == "active_document_identity_stable"
        ]
        if not identity_checks or identity_checks[0].get("status") != "pass":
            return "cad_capability_probe requires active_document_identity_stable pass in session_guard"

    return ""


def validate_readback_report_evidence(report: dict[str, Any]) -> str:
    for field in REQUIRED_READBACK_REPORT_FIELDS:
        if field not in report:
            return f"readback_report missing required field: {field}"

    status = str(report.get("status", ""))
    screenshot_path = str(report.get("evidence", {}).get("screenshot", "") or "")
    expected = readback_report_evidence(status=status, screenshot_path=screenshot_path or None)
    for key, value in expected.items():
        if report.get(key) != value:
            return f"readback_report.{key}={report.get(key)!r}; expected {value!r} for status={status!r}"

    if status == "geometry_verified" and report.get("evidence_state") != EVIDENCE_READBACK_GEOMETRY_VERIFIED:
        return "readback_report geometry_verified requires evidence_state=readback_geometry_verified"

    if status == "geometry_verified":
        checks = report.get("checks", [])
        if not isinstance(checks, list) or not checks:
            return "readback_report geometry_verified requires non-empty checks"
        if any(not isinstance(check, dict) or check.get("status") != "pass" for check in checks):
            return "readback_report geometry_verified requires all checks pass"
        if not any(
            isinstance(check, dict) and check.get("name") == "created_handles_scope" and check.get("status") == "pass"
            for check in checks
        ):
            return "readback_report geometry_verified requires created_handles_scope pass check"
        actual = report.get("actual", {})
        if not isinstance(actual, dict):
            return "readback_report geometry_verified requires actual readback payload"
        created_handles = actual.get("created_handles")
        if not isinstance(created_handles, list) or not created_handles:
            return "readback_report geometry_verified requires non-empty actual.created_handles"
        entities = actual.get("entities")
        if not isinstance(entities, list) or not entities:
            return "readback_report geometry_verified requires non-empty actual.entities"
        handle_set = {str(handle) for handle in created_handles if str(handle)}
        entity_handles = {str(entity.get("handle")) for entity in entities if isinstance(entity, dict) and entity.get("handle")}
        if not handle_set or not handle_set <= entity_handles:
            return "readback_report geometry_verified actual.entities must cover actual.created_handles"

    if status != "geometry_verified" and report.get("geometry_accuracy") == GEOMETRY_VERIFIED_BY_READBACK:
        return "readback_report must not claim verified_by_cad_readback without geometry_verified status"

    return ""


def normalize_created_handles(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(handle).strip() for handle in value if str(handle).strip()]


def validate_created_handles_match(
    *,
    expected_created_handles: object,
    actual_created_handles: object,
    label: str,
) -> str:
    expected = normalize_created_handles(expected_created_handles)
    actual = normalize_created_handles(actual_created_handles)
    if not expected:
        return f"{label} requires non-empty execution_summary.created_handles"
    if not actual:
        return f"{label} requires non-empty report created_handles"
    if set(expected) != set(actual):
        return f"{label} created_handles mismatch with execution_summary: expected={expected}, actual={actual}"
    return ""
