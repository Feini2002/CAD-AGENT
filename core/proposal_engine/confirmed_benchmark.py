"""Confirmed CAD_PLAN finalize benchmark (BETA-PROPOSAL-05)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.path_safety import resolve_under_project_output, validate_safe_path_segment
from core.proposal_engine.confirmed_finalize import (
    build_default_confirmation_for_proposal,
    finalize_confirmed_cad_plans,
)
from core.verification.evidence_contract import (
    EVIDENCE_BENCHMARK_PASS_NON_CAD,
    EVIDENCE_DEFERRED_CAD_READBACK,
    GEOMETRY_NOT_VERIFIED_BY_SCREENSHOT,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_VISUAL_AID_ONLY,
    evidence_summary_rollup,
    validate_evidence_summary,
    validate_evidence_triplet,
)
from core.workflows.blank_shell_pipeline import run_blank_shell_pipeline

DEFAULT_BENCHMARK_REL = Path("examples/benchmarks/proposal_confirmed_benchmark.json")


def default_proposal_confirmed_benchmark_path(project_root: Path) -> Path:
    return project_root / DEFAULT_BENCHMARK_REL


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _expected_evidence_errors(expected: dict[str, Any], *, label: str) -> list[str]:
    errors: list[str] = []
    for required in ("evidence_state", "geometry_accuracy", "screenshot_role"):
        if required not in expected:
            errors.append(f"{label}.expected.{required} is required")
    triplet_error = validate_evidence_triplet(expected, label=f"{label}.expected")
    if triplet_error:
        errors.append(triplet_error)
    return errors


def _confirmed_case_evidence(actual: dict[str, Any]) -> dict[str, str]:
    if (
        actual.get("pipeline_status") == "ok"
        and actual.get("finalize_status") == "ok"
        and actual.get("validation_all_valid") is True
    ):
        return {
            "evidence_state": EVIDENCE_BENCHMARK_PASS_NON_CAD,
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "screenshot_role": SCREENSHOT_VISUAL_AID_ONLY,
        }
    return {
        "evidence_state": EVIDENCE_DEFERRED_CAD_READBACK,
        "geometry_accuracy": GEOMETRY_NOT_VERIFIED_BY_SCREENSHOT,
        "screenshot_role": SCREENSHOT_VISUAL_AID_ONLY,
    }


def _compare_expected_evidence(actual: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("evidence_state", "geometry_accuracy", "screenshot_role"):
        if actual.get(key) != expected.get(key):
            errors.append(f"{key}: expected {expected.get(key)}, got {actual.get(key)}")
    return errors


def _summarize_confirmed_evidence(cases: list[dict[str, Any]]) -> dict[str, Any]:
    evidence_state_counts: dict[str, int] = {}
    geometry_accuracy_counts: dict[str, int] = {}
    screenshot_role_counts: dict[str, int] = {}
    for case in cases:
        actual = case.get("actual", {}) if isinstance(case.get("actual"), dict) else {}
        evidence_state = str(actual.get("evidence_state", "unknown"))
        geometry_accuracy = str(actual.get("geometry_accuracy", "unknown"))
        screenshot_role = str(actual.get("screenshot_role", "unknown"))
        evidence_state_counts[evidence_state] = evidence_state_counts.get(evidence_state, 0) + 1
        geometry_accuracy_counts[geometry_accuracy] = geometry_accuracy_counts.get(geometry_accuracy, 0) + 1
        screenshot_role_counts[screenshot_role] = screenshot_role_counts.get(screenshot_role, 0) + 1
    rollup = evidence_summary_rollup(evidence_state_counts)
    readback_count = rollup["readback_geometry_verified_count"]
    summary = {
        "case_count": len(cases),
        "evidence_state_counts": evidence_state_counts,
        "geometry_accuracy_counts": geometry_accuracy_counts,
        "screenshot_role_counts": screenshot_role_counts,
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
        actual_value = actual.get(key)
        if actual_value != expected_value:
            errors.append(f"evidence_summary.{key}: expected {expected_value}, got {actual_value}")
    return errors


def run_proposal_confirmed_benchmark(
    *,
    project_root: Path,
    output_root: Path,
    suite_path: Path | None = None,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    output_root = resolve_under_project_output(project_root, output_root, label="output_root")
    suite = json.loads((suite_path or default_proposal_confirmed_benchmark_path(project_root)).read_text(encoding="utf-8"))
    cases_out: list[dict[str, Any]] = []
    for index, case in enumerate(suite.get("cases", [])):
        case_id = str(case["case_id"])
        validate_safe_path_segment(case_id, label=f"cases[{index}].case_id")
        case_dir = output_root / case_id
        workflow = project_root / str(case["workflow"])
        pipeline = run_blank_shell_pipeline(workflow, output_dir=case_dir)
        errors: list[str] = []
        finalize_status = "skipped"
        actual: dict[str, Any] = {"pipeline_status": pipeline.get("status", "unknown")}

        expected = case.get("expected", {})
        if not isinstance(expected, dict) or not expected:
            raise ValueError(f"cases[{index}].expected must be a non-empty object.")
        evidence_errors = _expected_evidence_errors(expected, label=f"cases[{index}]")
        if evidence_errors:
            raise ValueError("; ".join(evidence_errors))

        if pipeline.get("status") == "ok":
            proposal = json.loads((case_dir / "design_proposal.json").read_text(encoding="utf-8"))
            selected = case.get("selected_candidate_id")
            confirmation = build_default_confirmation_for_proposal(
                proposal,
                action=str(case.get("confirmation_action", "accept")),
                selected_candidate_id=str(selected) if selected else None,
            )
            confirmation_path = case_dir / "confirmation.json"
            _write_json(confirmation_path, confirmation)

            finalize = finalize_confirmed_cad_plans(case_dir, confirmation_path)
            finalize_status = str(finalize.get("status", "unknown"))
            actual.update(
                {
                    "finalize_status": finalize_status,
                    "cad_plan_count": int(finalize.get("cad_plan_count", 0)),
                    "unselected_candidate_count": int(finalize.get("unselected_candidate_count", 0)),
                    "validation_all_valid": bool(finalize.get("validation_all_valid")),
                    "dry_run_valid_count": int(finalize.get("dry_run_valid_count", 0)),
                }
            )
            if expected.get("finalize_status") and finalize_status != expected["finalize_status"]:
                errors.append(f"finalize_status: expected {expected['finalize_status']}, got {finalize_status}")
            for metric, minimum in (expected.get("minimums") or {}).items():
                value = actual.get(metric)
                if not isinstance(value, (int, float)) or value < minimum:
                    errors.append(f"{metric}: expected at least {minimum}, got {value}")
            if expected.get("requires_unselected_evidence") and actual.get("unselected_candidate_count", 0) < 1:
                errors.append("unselected_candidate_evidence: expected at least one non-selected candidate")
            if expected.get("validation_all_valid") and not actual.get("validation_all_valid"):
                errors.append("validation_all_valid: expected true")
        else:
            errors.append(f"pipeline failed: {pipeline.get('errors', [])}")

        actual.update(_confirmed_case_evidence(actual))
        errors.extend(_compare_expected_evidence(actual, expected))
        cases_out.append(
            {
                "case_id": case_id,
                "status": "pass" if not errors else "fail",
                "errors": errors,
                "actual": actual,
                "output_dir": str(case_dir),
            }
        )

    passed = sum(1 for case in cases_out if case["status"] == "pass")
    summary = {"total": len(cases_out), "passed": passed, "failed": len(cases_out) - passed}
    evidence_summary = _summarize_confirmed_evidence(cases_out)
    evidence_summary_errors = _compare_evidence_summary(
        evidence_summary,
        suite.get("expected_evidence_summary", {})
        if isinstance(suite.get("expected_evidence_summary"), dict)
        else {},
    )
    result = {
        "status": "pass" if passed == len(cases_out) and not evidence_summary_errors else "fail",
        "suite_id": suite.get("suite_id", "proposal-confirmed-benchmark"),
        "summary": summary,
        "evidence_summary": evidence_summary,
        "evidence_summary_errors": evidence_summary_errors,
        "cases": cases_out,
    }
    _write_json(output_root / "benchmark_summary.json", result)
    return result
