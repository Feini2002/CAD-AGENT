"""Drawing-read pipeline benchmark (BETA-DRAWING-READ-05)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.drawing_analysis.dwg_read_only import read_entity_summary_from_fixture
from core.drawing_analysis.geometry_candidates import read_geometry_candidates_from_fixture
from core.drawing_analysis.shell_candidate_report import build_shell_candidate_confidence_report
from core.drawing_analysis.shell_confirmation import (
    ShellConfirmationError,
    apply_shell_drawing_read_confirmation,
    load_shell_drawing_read_confirmation,
)
from core.verification.evidence_contract import (
    EVIDENCE_BENCHMARK_PASS_NON_CAD,
    EVIDENCE_BLOCKED_EXPECTED_NON_CAD,
)
from core.path_safety import resolve_under_project_output, validate_safe_path_segment

DEFAULT_BENCHMARK_REL = Path("examples/benchmarks/drawing_read_benchmark.json")


def default_drawing_read_benchmark_path(project_root: Path) -> Path:
    return project_root / DEFAULT_BENCHMARK_REL


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _resolve_output_root(project_root: Path, output_root: Path) -> Path:
    return resolve_under_project_output(project_root, output_root, label="output_root")


def _validate_case_id(case_id: str, *, label: str) -> None:
    validate_safe_path_segment(case_id, label=f"{label}.case_id")


def _structured_blockers(report: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "code": str(item.get("code", "")),
            "message": str(item.get("message", "")),
            "severity": str(item.get("severity", "")),
        }
        for item in report.get("gaps", [])
        if isinstance(item, dict)
    ]


def run_drawing_read_pipeline(
    fixture_path: Path,
    *,
    confirmation_path: Path | None = None,
    include_entity_summary: bool = False,
) -> dict[str, Any]:
    """Run READ-01..04 stages for a fixture and return metrics + artifacts."""

    geometry_candidates = read_geometry_candidates_from_fixture(fixture_path)
    entity_summary = read_entity_summary_from_fixture(fixture_path) if include_entity_summary else None
    report = build_shell_candidate_confidence_report(geometry_candidates)
    blockers = _structured_blockers(report)
    counts = geometry_candidates.get("counts", {})
    actual: dict[str, Any] = {
        "entity_count": int(geometry_candidates.get("entity_summary_ref", {}).get("entity_count", 0)),
        "wall_segment_count": int(counts.get("wall_segments", 0)),
        "opening_count": int(counts.get("door_openings", 0)),
        "column_count": int(counts.get("columns", 0)),
        "no_place_zone_count": int(counts.get("no_place_zones", 0)),
        "ready_for_human_confirmation_file": bool(report.get("ready_for_human_confirmation_file")),
        "confidence_overall": float(report.get("confidence", {}).get("overall", 0.0)),
        "structured_blockers": blockers,
        "blocker_codes": [item["code"] for item in blockers if item.get("severity") == "blocker"],
        "shell_export_status": "skipped",
    }
    artifacts: dict[str, str] = {
        "geometry_candidates": "",
        "confidence_report": "",
    }
    if entity_summary is not None:
        actual["entity_summary_entity_count"] = int(entity_summary.get("entity_count", 0))
        artifacts["entity_summary"] = ""

    if blockers and any(item["severity"] == "blocker" for item in blockers):
        return {
            "status": "blocked",
            "pipeline_status": "blocked",
            "evidence_state": EVIDENCE_BLOCKED_EXPECTED_NON_CAD,
            "geometry_accuracy": "not_verified_without_cad_readback",
            "screenshot_role": "visual_aid_only",
            "failure_category": "drawing_read_incomplete",
            "blocked_reasons": [item["message"] for item in blockers if item["severity"] == "blocker"],
            "metrics": actual,
            "artifacts": artifacts,
            "report": report,
            "geometry_candidates": geometry_candidates,
        }

    shell_export_status = "skipped"
    shell_id = ""
    if confirmation_path is not None:
        confirmation = load_shell_drawing_read_confirmation(confirmation_path)
        try:
            shell = apply_shell_drawing_read_confirmation(report, confirmation)
            shell_export_status = "ok"
            shell_id = str(shell.get("shell_id", ""))
            actual["shell_opening_count"] = len(shell.get("openings", []))
            actual["shell_obstacle_count"] = len(shell.get("fixed_obstacles", []))
            actual["shell_no_place_zone_count"] = len(shell.get("no_place_zones", []))
        except ShellConfirmationError as exc:
            return {
                "status": "blocked",
                "pipeline_status": "blocked",
                "evidence_state": EVIDENCE_BLOCKED_EXPECTED_NON_CAD,
                "geometry_accuracy": "not_verified_without_cad_readback",
                "screenshot_role": "visual_aid_only",
                "failure_category": "drawing_read_confirmation_rejected",
                "blocked_reasons": [str(exc)],
                "metrics": {**actual, "shell_export_status": "failed"},
                "artifacts": artifacts,
                "report": report,
                "geometry_candidates": geometry_candidates,
            }

    actual["shell_export_status"] = shell_export_status
    actual["shell_id"] = shell_id
    return {
        "status": "ok",
        "pipeline_status": "ok",
        "evidence_state": EVIDENCE_BENCHMARK_PASS_NON_CAD,
        "geometry_accuracy": "not_verified_without_cad_readback",
        "screenshot_role": "visual_aid_only",
        "metrics": actual,
        "artifacts": artifacts,
        "report": report,
        "geometry_candidates": geometry_candidates,
    }


def _compare_expected(actual: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("pipeline_status", "evidence_state", "geometry_accuracy", "screenshot_role", "failure_category"):
        if key not in expected:
            continue
        if actual.get(key) != expected[key]:
            errors.append(f"{key}: expected {expected[key]!r}, got {actual.get(key)!r}")

    if "ready_for_human_confirmation_file" in expected:
        value = actual.get("ready_for_human_confirmation_file")
        if value != expected["ready_for_human_confirmation_file"]:
            errors.append(
                f"ready_for_human_confirmation_file: expected {expected['ready_for_human_confirmation_file']!r}, "
                f"got {value!r}"
            )
    if "requires_shell_model" in expected:
        expected_export = "ok" if expected["requires_shell_model"] else "skipped"
        value = actual.get("shell_export_status")
        if value != expected_export:
            errors.append(f"requires_shell_model: expected shell_export_status={expected_export!r}, got {value!r}")

    if expected.get("shell_id") and actual.get("shell_id") != expected["shell_id"]:
        errors.append(f"shell_id: expected {expected['shell_id']!r}, got {actual.get('shell_id')!r}")

    blocker_code = expected.get("contains_blocker_code")
    if blocker_code:
        codes = actual.get("blocker_codes", [])
        if blocker_code not in codes:
            errors.append(f"contains_blocker_code: expected {blocker_code!r} in {codes}")

    for metric, minimum in (expected.get("minimums") or {}).items():
        value = actual.get(metric)
        if not isinstance(value, (int, float)) or value < minimum:
            errors.append(f"{metric}: expected at least {minimum}, got {value}")

    for metric, maximum in (expected.get("maximums") or {}).items():
        value = actual.get(metric)
        if not isinstance(value, (int, float)) or value > maximum:
            errors.append(f"{metric}: expected at most {maximum}, got {value}")

    return errors


def run_drawing_read_benchmark(
    *,
    project_root: Path,
    output_root: Path,
    suite_path: Path | None = None,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    output_root = _resolve_output_root(project_root, output_root)
    suite = json.loads((suite_path or default_drawing_read_benchmark_path(project_root)).read_text(encoding="utf-8"))
    cases_out: list[dict[str, Any]] = []

    for index, case in enumerate(suite.get("cases", [])):
        case_id = str(case["case_id"])
        _validate_case_id(case_id, label=f"cases[{index}]")
        case_dir = output_root / case_id
        case_dir.mkdir(parents=True, exist_ok=True)
        fixture = project_root / str(case["fixture"])
        confirmation = case.get("confirmation")
        confirmation_path = project_root / str(confirmation) if confirmation else None

        pipeline = run_drawing_read_pipeline(
            fixture,
            confirmation_path=confirmation_path,
            include_entity_summary=bool(case.get("include_entity_summary")),
        )
        _write_json(case_dir / "geometry_candidates.json", pipeline["geometry_candidates"])
        _write_json(case_dir / "confidence_report.json", pipeline["report"])

        metrics = dict(pipeline.get("metrics", {}))
        actual = {
            "pipeline_status": pipeline.get("pipeline_status"),
            "evidence_state": pipeline.get("evidence_state"),
            "geometry_accuracy": pipeline.get("geometry_accuracy"),
            "screenshot_role": pipeline.get("screenshot_role"),
            "failure_category": pipeline.get("failure_category", ""),
            "blocked_reasons": pipeline.get("blocked_reasons", []),
            "structured_blockers": metrics.get("structured_blockers", []),
            **metrics,
        }
        errors = _compare_expected(actual, case.get("expected", {}))
        cases_out.append(
            {
                "case_id": case_id,
                "status": "pass" if not errors else "fail",
                "errors": errors,
                "actual": actual,
                "expected": case.get("expected", {}),
                "output_dir": str(case_dir),
            }
        )

    passed = sum(1 for case in cases_out if case["status"] == "pass")
    summary = {"total": len(cases_out), "passed": passed, "failed": len(cases_out) - passed}
    evidence_summary = {
        "case_count": len(cases_out),
        "benchmark_pass_non_cad_count": sum(
            1 for case in cases_out if case.get("actual", {}).get("evidence_state") == EVIDENCE_BENCHMARK_PASS_NON_CAD
        ),
        "blocked_expected_non_cad_count": sum(
            1
            for case in cases_out
            if case.get("actual", {}).get("evidence_state") == EVIDENCE_BLOCKED_EXPECTED_NON_CAD
        ),
        "readback_geometry_verified_count": 0,
        "non_cad_only": True,
    }
    expected_summary = suite.get("expected_evidence_summary", {})
    summary_errors: list[str] = []
    for key, expected_value in expected_summary.items():
        if evidence_summary.get(key) != expected_value:
            summary_errors.append(f"expected_evidence_summary.{key}: expected {expected_value}, got {evidence_summary.get(key)}")

    result = {
        "status": "pass" if passed == len(cases_out) and not summary_errors else "fail",
        "suite_id": suite.get("suite_id", "drawing-read-benchmark"),
        "summary": summary,
        "evidence_summary": evidence_summary,
        "expected_evidence_summary_errors": summary_errors,
        "cases": cases_out,
    }
    _write_json(output_root / "benchmark_summary.json", result)
    return result
