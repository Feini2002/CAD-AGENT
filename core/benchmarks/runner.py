"""Benchmark runner for repeatable non-CAD Core verification suites."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.schemas.validator import load_json
from core.workflows.non_cad_pipeline import run_non_cad_pipeline
from core.workflows.blank_shell_pipeline import run_blank_shell_pipeline


def _find_project_root(path: Path) -> Path:
    for parent in [path.parent, *path.parents]:
        if (parent / "CORE_RESTRUCTURE_PLAN.md").exists():
            return parent
    return path.parent


def _actual_from_pipeline(result: dict[str, Any]) -> dict[str, Any]:
    dry_run_report = result.get("dry_run_report", {}) if isinstance(result.get("dry_run_report"), dict) else {}
    verification_report = (
        result.get("verification_report", {}) if isinstance(result.get("verification_report"), dict) else {}
    )
    return {
        "pipeline_status": result.get("status", "unknown"),
        "dry_run_status": dry_run_report.get("status", "unknown"),
        "verification_status": verification_report.get("status", "unknown"),
        "candidate_count": result.get("metrics", {}).get("circulation_candidates", 0),
        "zone_count": result.get("metrics", {}).get("zones", 0),
        "placement_count": result.get("metrics", {}).get("placements", 0),
        "cad_plan_count": result.get("metrics", {}).get("cad_plans", 0),
        "failed_check_count": result.get("metrics", {}).get("failed_checks", 0),
    }


def _compare_expected(actual: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key, expected_value in expected.items():
        actual_value = actual.get(key)
        if actual_value != expected_value:
            errors.append(f"{key}: expected {expected_value}, got {actual_value}")
    return errors


def run_benchmark_case(
    case: dict[str, Any],
    *,
    root: Path,
    output_root: Path,
) -> dict[str, Any]:
    case_id = str(case["case_id"])
    workflow_path = root / str(case["workflow"])
    case_output = output_root / case_id
    if case.get("pipeline") == "blank_shell":
        result = run_blank_shell_pipeline(workflow_path, output_dir=case_output)
    else:
        result = run_non_cad_pipeline(workflow_path, output_dir=case_output)
    actual = _actual_from_pipeline(result)
    expected = case.get("expected", {})
    errors = _compare_expected(actual, expected if isinstance(expected, dict) else {})
    status = "pass" if not errors else "fail"
    return {
        "case_id": case_id,
        "status": status,
        "errors": errors,
        "actual": actual,
        "expected": expected,
        "artifacts": result.get("artifacts", {}),
        "output_dir": str(case_output),
    }


def run_benchmark_suite(suite_path: Path, *, output_root: Path) -> dict[str, Any]:
    root = _find_project_root(suite_path.resolve())
    suite = load_json(suite_path)
    if not isinstance(suite, dict):
        raise ValueError("Benchmark suite must be a JSON object.")
    cases = suite.get("cases", [])
    if not isinstance(cases, list):
        raise ValueError("Benchmark suite cases must be a list.")

    output_root.mkdir(parents=True, exist_ok=True)
    case_results = [
        run_benchmark_case(case, root=root, output_root=output_root)
        for case in cases
        if isinstance(case, dict)
    ]
    passed = sum(1 for case in case_results if case["status"] == "pass")
    failed = len(case_results) - passed
    return {
        "status": "pass" if failed == 0 else "fail",
        "suite_id": suite.get("suite_id", suite_path.stem),
        "summary": {
            "total": len(case_results),
            "passed": passed,
            "failed": failed,
        },
        "cases": case_results,
    }
