"""Expected-result comparison helpers for benchmark suites."""

from __future__ import annotations

from typing import Any

from core.verification.evidence_contract import (
    EVIDENCE_BENCHMARK_PASS_NON_CAD,
    EVIDENCE_BLOCKED_EXPECTED_NON_CAD,
    EVIDENCE_INVALID_CONFIGURATION,
    evidence_summary_rollup,
    validate_evidence_state,
    validate_evidence_summary,
    validate_evidence_triplet,
    validate_failure_expected_contract,
    validate_geometry_accuracy,
    validate_screenshot_role,
)


def _validate_expected_evidence_fields(expected: dict[str, Any], *, label: str) -> list[str]:
    errors: list[str] = []
    for required in ("evidence_state", "geometry_accuracy", "screenshot_role"):
        if required not in expected:
            errors.append(f"{label}.expected.{required} is required")
    for field, validator in (
        ("evidence_state", validate_evidence_state),
        ("geometry_accuracy", validate_geometry_accuracy),
        ("screenshot_role", validate_screenshot_role),
    ):
        if field not in expected:
            continue
        error = validator(expected.get(field))
        if error:
            errors.append(f"{label}.expected.{error}")
    triplet_error = validate_evidence_triplet(expected, label=f"{label}.expected")
    if triplet_error:
        errors.append(triplet_error)
    return errors


def _compare_expected(actual: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key, expected_value in expected.items():
        if key == "minimums" and isinstance(expected_value, dict):
            for metric, minimum in expected_value.items():
                actual_value = actual.get(metric)
                if not isinstance(actual_value, (int, float)) or actual_value < minimum:
                    errors.append(f"{metric}: expected at least {minimum}, got {actual_value}")
            continue
        if key == "maximums" and isinstance(expected_value, dict):
            for metric, maximum in expected_value.items():
                actual_value = actual.get(metric)
                if not isinstance(actual_value, (int, float)) or actual_value > maximum:
                    errors.append(f"{metric}: expected at most {maximum}, got {actual_value}")
            continue
        if key == "contains_object_types" and isinstance(expected_value, list):
            actual_types = set(actual.get("object_types", []))
            missing = [item for item in expected_value if item not in actual_types]
            if missing:
                errors.append(f"object_types: missing {missing}, got {sorted(actual_types)}")
            continue
        if key == "contains_component_roles" and isinstance(expected_value, list):
            actual_roles = set(actual.get("component_roles", []))
            missing = [item for item in expected_value if item not in actual_roles]
            if missing:
                errors.append(f"component_roles: missing {missing}, got {sorted(actual_roles)}")
            continue
        if key == "contains_object_roles" and isinstance(expected_value, list):
            actual_roles = set(actual.get("object_roles", []))
            missing = [item for item in expected_value if item not in actual_roles]
            if missing:
                errors.append(f"object_roles: missing {missing}, got {sorted(actual_roles)}")
            continue
        if key == "contains_clearance_refs" and isinstance(expected_value, list):
            actual_roles = set(actual.get("clearance_ref_roles", []))
            missing = [item for item in expected_value if item not in actual_roles]
            if missing:
                errors.append(f"clearance_refs: missing {missing}, got {sorted(actual_roles)}")
            continue
        if key == "contains_binding_relations" and isinstance(expected_value, list):
            actual_relations = set(actual.get("binding_relations", []))
            missing = [item for item in expected_value if item not in actual_relations]
            if missing:
                errors.append(f"binding_relations: missing {missing}, got {sorted(actual_relations)}")
            continue
        if key == "contains_circulation_roles" and isinstance(expected_value, list):
            actual_roles = set(actual.get("circulation_roles", []))
            missing = [item for item in expected_value if item not in actual_roles]
            if missing:
                errors.append(f"circulation_roles: missing {missing}, got {sorted(actual_roles)}")
            continue
        if key == "contains_blocked_reason" and isinstance(expected_value, str):
            reasons = [str(item) for item in actual.get("blocked_reasons", [])]
            if not any(expected_value in reason for reason in reasons):
                errors.append(f"blocked_reasons: expected substring {expected_value!r}, got {reasons}")
            continue
        if key == "requires_comparison_detail" and expected_value is True:
            if not actual.get("has_comparison_detail"):
                errors.append("comparison_detail: expected design_proposal.comparison_detail metrics in pipeline output")
            continue
        if key == "comparison_detail_minimums" and isinstance(expected_value, dict):
            for metric, minimum in expected_value.items():
                actual_value = actual.get(metric)
                if not isinstance(actual_value, (int, float)) or actual_value < minimum:
                    errors.append(f"comparison_detail.{metric}: expected at least {minimum}, got {actual_value}")
            continue
        if key == "requires_proposal_comparison_summary" and expected_value is True:
            if not actual.get("has_proposal_comparison_summary"):
                errors.append(
                    "proposal_comparison_summary: expected machine-readable summary in pipeline output"
                )
            continue
        if key == "proposal_comparison_summary_minimums" and isinstance(expected_value, dict):
            for metric, minimum in expected_value.items():
                actual_value = actual.get(metric)
                if not isinstance(actual_value, (int, float)) or actual_value < minimum:
                    errors.append(
                        f"proposal_comparison_summary.{metric}: expected at least {minimum}, got {actual_value}"
                    )
            continue
        if key == "circulation_continuity_equals" and isinstance(expected_value, str):
            if actual.get("circulation_continuity") != expected_value:
                errors.append(
                    f"circulation_continuity: expected {expected_value!r}, got {actual.get('circulation_continuity')!r}"
                )
            continue
        if key == "contains_ranking_reason_code" and isinstance(expected_value, str):
            codes = [str(item) for item in actual.get("ranking_reason_codes", [])]
            if expected_value not in codes:
                errors.append(
                    f"ranking_reason_codes: expected code {expected_value!r}, got {codes}"
                )
            continue
        if key == "blocked_circulation_strategies_include" and isinstance(expected_value, str):
            strategies = [str(item) for item in actual.get("blocked_circulation_strategies", [])]
            if expected_value not in strategies:
                errors.append(
                    f"blocked_circulation_strategies: expected {expected_value!r}, got {strategies}"
                )
            continue
        if key == "contains_failed_reasons" and isinstance(expected_value, list):
            distribution = actual.get("selected_failed_reason_distribution", {})
            if not isinstance(distribution, dict):
                distribution = {}
            missing = [item for item in expected_value if item not in distribution]
            if missing:
                errors.append(
                    f"selected_failed_reason_distribution: missing keys {missing}, got {sorted(distribution.keys())}"
                )
            continue
        if key == "failed_reason_distribution_empty" and expected_value is True:
            distribution = actual.get("selected_failed_reason_distribution", {})
            if isinstance(distribution, dict) and distribution:
                errors.append(f"selected_failed_reason_distribution: expected empty, got {distribution}")
            continue
        if key == "preferences_path_contains" and isinstance(expected_value, str):
            path = str(actual.get("preferences_path", ""))
            if expected_value not in path.replace("\\", "/"):
                errors.append(f"preferences_path: expected substring {expected_value!r}, got {path!r}")
            continue
        actual_value = actual.get(key)
        if actual_value != expected_value:
            errors.append(f"{key}: expected {expected_value}, got {actual_value}")
    errors.extend(_compare_failure_outcome_guards(actual, expected))
    return errors


def _compare_failure_outcome_guards(actual: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    """Reject silent pass (blocked layout reported as benchmark pass)."""

    errors: list[str] = []
    expected_state = expected.get("evidence_state")
    actual_state = actual.get("evidence_state")
    actual_pipeline = actual.get("pipeline_status")

    if expected_state == EVIDENCE_BLOCKED_EXPECTED_NON_CAD:
        if actual_pipeline == "ok":
            errors.append("silent pass guard: expected blocked failure but pipeline_status=ok")
        if actual_state == EVIDENCE_BENCHMARK_PASS_NON_CAD:
            errors.append("silent pass guard: expected blocked_expected_non_cad but got benchmark_pass_non_cad")
    if expected_state == EVIDENCE_INVALID_CONFIGURATION:
        if actual_pipeline == "ok":
            errors.append("silent pass guard: expected invalid configuration but pipeline_status=ok")
        if actual_state == EVIDENCE_BENCHMARK_PASS_NON_CAD:
            errors.append("silent pass guard: expected invalid_configuration but got benchmark_pass_non_cad")
    if expected_state == EVIDENCE_BENCHMARK_PASS_NON_CAD:
        if actual_pipeline in {"blocked", "invalid"}:
            errors.append(
                f"silent pass guard: expected non-CAD pass but pipeline_status={actual_pipeline!r}"
            )
        if actual_state in {EVIDENCE_BLOCKED_EXPECTED_NON_CAD, EVIDENCE_INVALID_CONFIGURATION}:
            errors.append(
                f"silent pass guard: expected benchmark_pass_non_cad but evidence_state={actual_state!r}"
            )
    return errors


def summarize_benchmark_evidence(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate machine-readable evidence counters for benchmark suite reports."""

    evidence_state_counts: dict[str, int] = {}
    pipeline_status_counts: dict[str, int] = {}
    geometry_accuracy_counts: dict[str, int] = {}
    screenshot_role_counts: dict[str, int] = {}
    failure_category_counts: dict[str, int] = {}
    for case in case_results:
        actual = case.get("actual", {}) if isinstance(case.get("actual"), dict) else {}
        evidence_state = str(actual.get("evidence_state", "unknown"))
        state_error = validate_evidence_state(evidence_state)
        if state_error:
            raise ValueError(f"{case.get('case_id', 'case')}: {state_error}")
        evidence_state_counts[evidence_state] = evidence_state_counts.get(evidence_state, 0) + 1
        pipeline_status = str(actual.get("pipeline_status", "unknown"))
        pipeline_status_counts[pipeline_status] = pipeline_status_counts.get(pipeline_status, 0) + 1
        geometry_accuracy = str(actual.get("geometry_accuracy", "unknown"))
        accuracy_error = validate_geometry_accuracy(geometry_accuracy)
        if accuracy_error:
            raise ValueError(f"{case.get('case_id', 'case')}: {accuracy_error}")
        geometry_accuracy_counts[geometry_accuracy] = geometry_accuracy_counts.get(geometry_accuracy, 0) + 1
        screenshot_role = str(actual.get("screenshot_role", "unknown"))
        role_error = validate_screenshot_role(screenshot_role)
        if role_error:
            raise ValueError(f"{case.get('case_id', 'case')}: {role_error}")
        screenshot_role_counts[screenshot_role] = screenshot_role_counts.get(screenshot_role, 0) + 1
        failure_category = actual.get("failure_category")
        if failure_category:
            key = str(failure_category)
            failure_category_counts[key] = failure_category_counts.get(key, 0) + 1
    case_count = len(case_results)
    rollup = evidence_summary_rollup(evidence_state_counts)
    readback_count = rollup["readback_geometry_verified_count"]
    summary = {
        "case_count": case_count,
        "evidence_state_counts": evidence_state_counts,
        "pipeline_status_counts": pipeline_status_counts,
        "geometry_accuracy_counts": geometry_accuracy_counts,
        "screenshot_role_counts": screenshot_role_counts,
        "failure_category_counts": failure_category_counts,
        **rollup,
        "geometry_verified_case_count": readback_count,
        "non_cad_only": readback_count == 0,
    }
    summary_error = validate_evidence_summary(summary)
    if summary_error:
        raise ValueError(summary_error)
    return summary


def _compare_evidence_summary(actual: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key, expected_value in expected.items():
        if key == "minimums" and isinstance(expected_value, dict):
            for metric, minimum in expected_value.items():
                actual_value = actual.get(metric)
                if not isinstance(actual_value, (int, float)) or actual_value < minimum:
                    errors.append(f"evidence_summary.{metric}: expected at least {minimum}, got {actual_value}")
            continue
        actual_value = actual.get(key)
        if actual_value != expected_value:
            errors.append(f"evidence_summary.{key}: expected {expected_value}, got {actual_value}")
    return errors
