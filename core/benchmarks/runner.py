"""Benchmark runner for repeatable non-CAD Core verification suites."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.composition_engine.templates import (
    composition_micro_scene_metrics,
    composition_to_cad_plans,
    create_composition_spec,
    write_composition_preview_svg,
)
from core.benchmarks.expectations import (
    _compare_evidence_summary,
    _compare_expected,
    _validate_expected_evidence_fields,
    summarize_benchmark_evidence,
)
from core.object_engine.parametric_objects import create_object_spec, object_spec_to_cad_plan
from core.plan_engine.dry_run_report import create_dry_run_report
from core.schemas.validator import load_json
from core.verification.evidence_contract import classify_benchmark_pipeline_evidence, validate_failure_expected_contract
from core.verification.verification_report import build_verification_report, summarize_verification_reports
from core.layout_engine.office_layout_failure import evaluate_composition_layout_failure
from core.path_safety import resolve_under_project_output, validate_safe_path_segment
from core.workflows.non_cad_pipeline import run_non_cad_pipeline
from core.workflows.blank_shell_pipeline import run_blank_shell_pipeline


def _find_project_root(path: Path) -> Path:
    for parent in [path.parent, *path.parents]:
        if (parent / "CORE_RESTRUCTURE_PLAN.md").exists():
            return parent
    return path.parent


def _resolve_output_root(root: Path, output_root: Path) -> Path:
    return resolve_under_project_output(root, output_root, label="output_root")


def _validate_case_id(case_id: str, *, label: str) -> None:
    validate_safe_path_segment(case_id, label=f"{label}.case_id")


def _actual_from_pipeline(result: dict[str, Any]) -> dict[str, Any]:
    dry_run_report = result.get("dry_run_report", {}) if isinstance(result.get("dry_run_report"), dict) else {}
    dry_run_summary = result.get("dry_run_summary", {}) if isinstance(result.get("dry_run_summary"), dict) else {}
    verification_report = (
        result.get("verification_report", {}) if isinstance(result.get("verification_report"), dict) else {}
    )
    verification_summary = (
        result.get("verification_summary", {}) if isinstance(result.get("verification_summary"), dict) else {}
    )
    metrics = result.get("metrics", {}) if isinstance(result.get("metrics"), dict) else {}
    errors = result.get("errors", []) if isinstance(result.get("errors"), list) else []
    pipeline_status = result.get("status", "unknown")
    dry_run_status = dry_run_summary.get("status", dry_run_report.get("status", "unknown"))
    verification_status = verification_summary.get("status", verification_report.get("status", "unknown"))
    evidence = classify_benchmark_pipeline_evidence(
        pipeline_status=pipeline_status,
        dry_run_status=dry_run_status,
        verification_status=verification_status,
    )
    return {
        "pipeline_status": pipeline_status,
        "dry_run_status": dry_run_status,
        "verification_status": verification_status,
        **evidence,
        "candidate_count": metrics.get("circulation_candidates", 0),
        "zone_placement_candidate_count": metrics.get("zone_placement_candidates", 0),
        "circulation_branch_count": metrics.get("circulation_branch_count", 0),
        "object_coverage_rate": metrics.get("object_coverage_rate", 0),
        "selected_placement_failed_count": metrics.get("selected_placement_failed_count", 0),
        "selected_circulation_strategy": metrics.get("selected_circulation_strategy", ""),
        "preferences_scenario": metrics.get("preferences_scenario", ""),
        "preferences_path": metrics.get("preferences_path", ""),
        "has_comparison_detail": bool(metrics.get("has_comparison_detail", False)),
        "has_proposal_comparison_summary": bool(metrics.get("has_proposal_comparison_summary", False)),
        "ranking_reason_codes": metrics.get("ranking_reason_codes", []),
        "layout_failed_checks": metrics.get("layout_failed_checks", []),
        "blocked_circulation_strategies": metrics.get("blocked_circulation_strategies", []),
        "circulation_continuity": metrics.get("circulation_continuity", ""),
        "failed_reason_distribution": metrics.get("failed_reason_distribution", {}),
        "selected_failed_reason_distribution": metrics.get("selected_failed_reason_distribution", {}),
        "zone_count": metrics.get("zones", 0),
        "placed_count": metrics.get("placed_count", 0),
        "placement_count": metrics.get("placements", metrics.get("placement_count", 0)),
        "cad_plan_count": metrics.get("cad_plans", 0),
        "failed_check_count": metrics.get("failed_checks", 0),
        "object_types": metrics.get("object_types", []),
        "object_roles": metrics.get("object_roles", []),
        "object_type": metrics.get("object_type"),
        "object_count": metrics.get("object_count"),
        "composition_id": metrics.get("composition_id"),
        "persona_role": metrics.get("persona_role"),
        "visual_preview_status": metrics.get("visual_preview_status"),
        "width": metrics.get("width"),
        "depth": metrics.get("depth"),
        "height": metrics.get("height"),
        "component_roles": metrics.get("component_roles", []),
        "clearance_refs": metrics.get("clearance_refs", []),
        "clearance_ref_roles": metrics.get("clearance_ref_roles", []),
        "placement_role": metrics.get("placement_role"),
        "binding_relations": metrics.get("binding_relations", []),
        "circulation_roles": metrics.get("circulation_roles", []),
        "no_place_zone_count": metrics.get("no_place_zone_count", 0),
        "fixed_obstacle_count": metrics.get("fixed_obstacle_count", 0),
        "shell_id": metrics.get("shell_id"),
        "failed_check_count": metrics.get("failed_checks", metrics.get("failed_check_count", 0)),
        "failure_category": metrics.get("failure_category", ""),
        "blocked_reasons": metrics.get("blocked_reasons", errors),
    }


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _validate_benchmark_case(case: Any, *, label: str = "case") -> None:
    if not isinstance(case, dict):
        raise ValueError(f"{label} must be an object.")
    case_id = case.get("case_id")
    if not isinstance(case_id, str) or not case_id:
        raise ValueError(f"{label}.case_id must be a non-empty string.")
    _validate_case_id(case_id, label=label)
    expected = case.get("expected")
    if not isinstance(expected, dict) or not expected:
        raise ValueError(f"{label}.expected must be a non-empty object.")
    evidence_errors = _validate_expected_evidence_fields(expected, label=label)
    if evidence_errors:
        raise ValueError("; ".join(evidence_errors))
    failure_errors = validate_failure_expected_contract(expected, label=label)
    if failure_errors:
        raise ValueError("; ".join(failure_errors))
    pipeline = case.get("pipeline", "non_cad")
    if pipeline not in {"non_cad", "blank_shell", "object_spec", "composition_spec"}:
        raise ValueError(f"{label}.pipeline is not supported: {pipeline}")
    if pipeline == "object_spec":
        if not isinstance(case.get("object_type"), str) or not case.get("object_type"):
            raise ValueError(f"{label}.object_type must be a non-empty string for object_spec pipeline.")
        return
    if pipeline == "composition_spec":
        if not isinstance(case.get("composition_id"), str) or not case.get("composition_id"):
            raise ValueError(f"{label}.composition_id must be a non-empty string for composition_spec pipeline.")
        return
    if not isinstance(case.get("workflow"), str) or not case.get("workflow"):
        raise ValueError(f"{label}.workflow must be a non-empty string.")


def _run_object_spec_case(case: dict[str, Any], *, case_output: Path) -> dict[str, Any]:
    object_type = str(case["object_type"])
    spec = create_object_spec(
        object_type,
        name=case.get("name") if isinstance(case.get("name"), str) else None,
        width=case.get("width") if isinstance(case.get("width"), (int, float)) else None,
        depth=case.get("depth") if isinstance(case.get("depth"), (int, float)) else None,
        height=case.get("height") if isinstance(case.get("height"), (int, float)) else None,
    )
    cad_plan = object_spec_to_cad_plan(spec)
    dry_run_report = create_dry_run_report(cad_plan)
    paths = {
        "object_spec": case_output / "object_spec.json",
        "cad_plan": case_output / "cad_plan.json",
        "dry_run_report": case_output / "dry_run_report.json",
        "verification_report": case_output / "verification_report.json",
    }
    _write_json(paths["object_spec"], spec)
    _write_json(paths["cad_plan"], cad_plan)
    _write_json(paths["dry_run_report"], dry_run_report)
    verification_report = build_verification_report(plan_path=paths["cad_plan"])
    _write_json(paths["verification_report"], verification_report)
    return {
        "status": "ok",
        "artifacts": {key: str(path) for key, path in paths.items()},
        "dry_run_report": dry_run_report,
        "verification_report": verification_report,
        "metrics": {
            "object_types": [object_type],
            "object_type": object_type,
            "width": spec["size"]["width"],
            "depth": spec["size"]["depth"],
            "height": spec["size"]["height"],
            "component_roles": sorted({str(component.get("role")) for component in spec.get("components", [])}),
            "clearance_refs": spec.get("clearance_refs", []),
            "clearance_ref_roles": sorted(
                {
                    str(ref.get("role"))
                    for ref in spec.get("clearance_refs", [])
                    if isinstance(ref, dict) and ref.get("role")
                }
            ),
            "placement_role": spec.get("placement_role"),
        },
    }


def _summarize_dry_run_reports(reports: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    for report in reports:
        status = str(report.get("status", "unknown"))
        status_counts[status] = status_counts.get(status, 0) + 1
    valid_count = status_counts.get("valid", 0)
    return {
        "version": "0.1",
        "status": "valid" if reports and valid_count == len(reports) else "invalid",
        "plan_count": len(reports),
        "valid_count": valid_count,
        "invalid_count": len(reports) - valid_count,
        "status_counts": status_counts,
    }


def _summarize_plan_verification_reports(reports: list[dict[str, Any]]) -> dict[str, Any]:
    summary = summarize_verification_reports(reports)
    status_counts = summary["status_counts"]
    if summary["all_geometry_verified"]:
        status = "geometry_verified"
    elif reports and status_counts.get("unverified", 0) == len(reports):
        status = "unverified"
    elif status_counts.get("failed", 0) > 0:
        status = "failed"
    else:
        status = "mixed"
    return {**summary, "status": status}


def _run_composition_spec_case(case: dict[str, Any], *, case_output: Path) -> dict[str, Any]:
    composition = create_composition_spec(
        str(case["composition_id"]),
        persona_role=str(case.get("persona_role", "simulated_user")),
        request_text=str(case.get("request_text", "")),
    )
    cad_plans = composition_to_cad_plans(composition)
    dry_run_reports = [create_dry_run_report(cad_plan) for cad_plan in cad_plans]

    paths = {
        "composition_spec": case_output / "composition_spec.json",
        "cad_plan": case_output / "cad_plan.json",
        "cad_plans": case_output / "cad_plans.json",
        "dry_run_report": case_output / "dry_run_report.json",
        "dry_run_reports": case_output / "dry_run_reports.json",
        "verification_report": case_output / "verification_report.json",
        "verification_reports": case_output / "verification_reports.json",
        "preview_svg": case_output / "preview.svg",
    }
    cad_plan_paths = [case_output / "cad_plan_items" / f"cad_plan_{index + 1:03d}.json" for index in range(len(cad_plans))]
    _write_json(paths["composition_spec"], composition)
    _write_json(paths["cad_plan"], cad_plans[0])
    _write_json(paths["cad_plans"], cad_plans)
    for plan_path, cad_plan in zip(cad_plan_paths, cad_plans):
        _write_json(plan_path, cad_plan)
    _write_json(paths["dry_run_report"], dry_run_reports[0])
    _write_json(paths["dry_run_reports"], dry_run_reports)
    verification_reports = [build_verification_report(plan_path=plan_path) for plan_path in cad_plan_paths]
    _write_json(paths["verification_report"], verification_reports[0])
    _write_json(paths["verification_reports"], verification_reports)
    layout_failure = evaluate_composition_layout_failure(composition)
    if layout_failure is not None:
        return {
            "status": layout_failure["status"],
            "errors": layout_failure["blocked_reasons"],
            "artifacts": {key: str(path) for key, path in paths.items()},
            "metrics": {
                "composition_id": composition["composition_id"],
                "persona_role": composition["persona_role"],
                "failure_category": layout_failure["failure_category"],
                "blocked_reasons": layout_failure["blocked_reasons"],
                **composition_micro_scene_metrics(composition),
            },
        }

    preview_result = write_composition_preview_svg(composition, cad_plans, paths["preview_svg"])
    micro_metrics = composition_micro_scene_metrics(composition)

    return {
        "status": "ok",
        "artifacts": {key: str(path) for key, path in paths.items()},
        "dry_run_report": dry_run_reports[0],
        "dry_run_reports": dry_run_reports,
        "dry_run_summary": _summarize_dry_run_reports(dry_run_reports),
        "verification_report": verification_reports[0],
        "verification_reports": verification_reports,
        "verification_summary": _summarize_plan_verification_reports(verification_reports),
        "metrics": {
            "composition_id": composition["composition_id"],
            "persona_role": composition["persona_role"],
            "object_count": len(composition["objects"]),
            "object_types": sorted({str(item.get("type")) for item in composition["objects"]}),
            "object_roles": sorted({str(item.get("role")) for item in composition["objects"]}),
            "cad_plans": len(cad_plans),
            "visual_preview_status": preview_result["status"],
            **micro_metrics,
        },
    }


def run_benchmark_case(
    case: dict[str, Any],
    *,
    root: Path,
    output_root: Path,
) -> dict[str, Any]:
    output_root = _resolve_output_root(root, output_root)
    _validate_benchmark_case(case)
    case_id = str(case["case_id"])
    case_output = output_root / case_id
    if case.get("pipeline") == "object_spec":
        result = _run_object_spec_case(case, case_output=case_output)
    elif case.get("pipeline") == "composition_spec":
        result = _run_composition_spec_case(case, case_output=case_output)
    elif case.get("pipeline") == "blank_shell":
        workflow_path = root / str(case["workflow"])
        result = run_blank_shell_pipeline(workflow_path, output_dir=case_output)
    else:
        workflow_path = root / str(case["workflow"])
        result = run_non_cad_pipeline(workflow_path, output_dir=case_output)
    actual = _actual_from_pipeline(result)
    expected = case["expected"]
    errors = _compare_expected(actual, expected)
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
    output_root = _resolve_output_root(root, output_root)
    suite = load_json(suite_path)
    if not isinstance(suite, dict):
        raise ValueError("Benchmark suite must be a JSON object.")
    cases = suite.get("cases", [])
    if not isinstance(cases, list):
        raise ValueError("Benchmark suite cases must be a list.")
    if not cases:
        raise ValueError("Benchmark suite cases must not be empty.")

    output_root.mkdir(parents=True, exist_ok=True)
    for index, case in enumerate(cases):
        _validate_benchmark_case(case, label=f"cases[{index}]")
    case_results = [run_benchmark_case(case, root=root, output_root=output_root) for case in cases]
    passed = sum(1 for case in case_results if case["status"] == "pass")
    failed = len(case_results) - passed
    evidence_summary = summarize_benchmark_evidence(case_results)
    summary_errors = _compare_evidence_summary(
        evidence_summary,
        suite.get("expected_evidence_summary", {}),
    ) if isinstance(suite.get("expected_evidence_summary"), dict) else []
    suite_result = {
        "status": "pass" if failed == 0 and not summary_errors else "fail",
        "suite_id": suite.get("suite_id", suite_path.stem),
        "summary": {
            "total": len(case_results),
            "passed": passed,
            "failed": failed,
        },
        "evidence_summary": evidence_summary,
        "evidence_summary_errors": summary_errors,
        "cases": case_results,
    }
    _write_json(output_root / "benchmark_summary.json", suite_result)
    return suite_result
