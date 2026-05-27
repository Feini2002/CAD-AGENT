"""Execute local CAD regression matrix cases and build reports."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from core.path_safety import resolve_under_project_output
from core.verification.cad_validation_types import CommandRunner
from core.verification.local_cad_regression_manifest import (
    DEFAULT_MANIFEST_RELATIVE_PATH,
    PREVIEW_LAYER,
    load_regression_manifest,
    manifest_case_ids,
    manifest_summary,
    select_manifest_case_ids,
)
from core.verification.evidence_trend import (
    build_evidence_trend_report,
    build_evidence_trend_snapshot,
    empty_evidence_state_counts,
    validate_evidence_trend_report,
)
from core.verification.evidence_vocabulary import (
    EVIDENCE_CAD_CAPABILITY_VERIFIED,
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_NOT_VERIFIED_BY_SCREENSHOT,
    GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE,
    GEOMETRY_VERIFIED_BY_READBACK,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
    SCREENSHOT_VISUAL_AID_ONLY,
)
from core.verification.local_cad_regression_runtime import (
    _build_summary,
    _deferred_step,
    _markdown_report,
    _not_run_step,
    _overall_status,
    _python,
    _run_step,
    _write_text,
    default_command_runner,
)

def _step_evidence_state(step: dict[str, Any]) -> str:
    payload = step.get("payload") if isinstance(step.get("payload"), dict) else {}
    evidence_state = payload.get("evidence_state")
    if isinstance(evidence_state, str) and evidence_state:
        return evidence_state
    evidence_summary = payload.get("evidence_summary")
    if isinstance(evidence_summary, dict):
        if int(evidence_summary.get("readback_geometry_verified_count") or 0) > 0:
            return EVIDENCE_READBACK_GEOMETRY_VERIFIED
        if int(evidence_summary.get("cad_capability_verified_count") or 0) > 0:
            return EVIDENCE_CAD_CAPABILITY_VERIFIED
        if int(evidence_summary.get("deferred_cad_readback_required_count") or 0) > 0:
            return EVIDENCE_DEFERRED_CAD_READBACK
    if payload.get("status") == "geometry_verified" or payload.get("geometry_verified") is True:
        return EVIDENCE_READBACK_GEOMETRY_VERIFIED
    return EVIDENCE_DEFERRED_CAD_READBACK


def _write_evidence_trend_report(
    *,
    output_dir: Path,
    report: dict[str, Any],
) -> None:
    project_root = Path(str(report.get("root", output_dir))).resolve()
    counts = empty_evidence_state_counts()
    accuracy_counts = {
        GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE: 0,
        GEOMETRY_VERIFIED_BY_READBACK: 0,
        NON_CAD_GEOMETRY_ACCURACY: 0,
        GEOMETRY_NOT_VERIFIED_BY_SCREENSHOT: 0,
    }
    screenshot_counts = {
        SCREENSHOT_NOT_APPLICABLE: 0,
        SCREENSHOT_VISUAL_AID_ONLY: 0,
    }
    for step in report.get("steps", []):
        if not isinstance(step, dict):
            continue
        state = _step_evidence_state(step)
        counts[state] += 1
        if state == EVIDENCE_CAD_CAPABILITY_VERIFIED:
            accuracy_counts[GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE] += 1
        elif state == EVIDENCE_READBACK_GEOMETRY_VERIFIED:
            accuracy_counts[GEOMETRY_VERIFIED_BY_READBACK] += 1
        else:
            accuracy_counts[NON_CAD_GEOMETRY_ACCURACY] += 1
        screenshot_counts[SCREENSHOT_NOT_APPLICABLE] += 1

    snapshot = build_evidence_trend_snapshot(
        snapshot_id="local-cad-regression-latest",
        series_id="local_cad_regression",
        source_kind="local_cad_regression",
        source_path=str((output_dir / "local_cad_regression_report.json").resolve().relative_to(project_root)).replace("\\", "/"),
        snapshot_at=str(report.get("generated_at", "")),
        evidence_state_counts=counts,
        geometry_accuracy_counts=accuracy_counts,
        screenshot_role_counts=screenshot_counts,
        metrics=report.get("summary", {}),
    )
    trend = build_evidence_trend_report(
        report_id="local-cad-regression-trend",
        generated_at=str(report.get("generated_at", "")),
        snapshots=[snapshot],
        notes=[
            "LCAD-11.2 local CAD regression trend rollup.",
            "No-CAD runs remain deferred/non-CAD and do not add geometry_verified evidence.",
        ],
    )
    errors = validate_evidence_trend_report(trend)
    if errors:
        raise ValueError("invalid local CAD regression trend report: " + "; ".join(errors))
    trend_dir = output_dir / "evidence_trend"
    _write_text(trend_dir / "local_cad_regression_trend.json", json.dumps(trend, ensure_ascii=False, indent=2) + "\n")

def run_local_cad_regression(
    *,
    root: Path,
    output_dir: Path,
    include_cad: bool,
    require_cad_verified: bool = False,
    manifest_path: Path | None = None,
    selected_case_ids: list[str] | None = None,
    command_runner: CommandRunner = default_command_runner,
) -> dict[str, Any]:
    """Run a local CAD regression matrix and aggregate machine-readable evidence."""

    project_root = root.resolve()
    resolved_manifest_path = manifest_path or project_root / DEFAULT_MANIFEST_RELATIVE_PATH
    if not resolved_manifest_path.is_absolute():
        resolved_manifest_path = project_root / resolved_manifest_path
    manifest = load_regression_manifest(resolved_manifest_path)
    active_case_ids = select_manifest_case_ids(manifest, selected_case_ids)

    output_dir = resolve_under_project_output(project_root, output_dir, label="output_dir")
    output_dir.mkdir(parents=True, exist_ok=True)

    baseline_dir = output_dir / "baseline_cad_validation"
    baseline_command = [
        _python(),
        "scripts/run_cad_validation.py",
        "--output-dir",
        str(baseline_dir),
    ]
    if not include_cad:
        baseline_command.append("--no-cad")

    steps: list[dict[str, Any]] = []

    if "baseline_cad_validation" in active_case_ids:
        steps.append(
            _run_step(
                step_id="baseline_cad_validation",
                title="Baseline CAD validation runner",
                command=baseline_command,
                output_dir=output_dir,
                root=project_root,
                command_runner=command_runner,
                failure_category="baseline_cad_validation_failed",
            )
        )

    project_sample_command = [
        _python(),
        "scripts/run_project_sample_cad_check.py",
        "--workflow-output-dir",
        str(output_dir / "project_sample_workflow"),
        "--output-dir",
        str(output_dir / "project_sample_cad"),
        "--start-x",
        "34000",
        "--start-y",
        "18000",
    ]
    if include_cad:
        if require_cad_verified:
            project_sample_command.append("--require-cad-verified")
    else:
        project_sample_command.append("--no-cad")

    if "project_sample_cad_check" in active_case_ids:
        steps.append(
            _run_step(
                step_id="project_sample_cad_check",
                title="Project sample CODEX_PREVIEW CAD check",
                command=project_sample_command,
                output_dir=output_dir,
                root=project_root,
                command_runner=command_runner,
                failure_category="cad_geometry_not_verified",
                strict_geometry=include_cad and require_cad_verified,
            )
        )

    if "composition_cad_check" in active_case_ids:
        if include_cad:
            benchmark_output = output_dir / "interior_delivery_benchmark"
            steps.append(
                _run_step(
                    step_id="interior_delivery_benchmark",
                    title="Prepare interior delivery CAD_PLAN artifacts",
                    command=[
                        _python(),
                        "scripts/run_benchmark_suite.py",
                        "examples/benchmarks/interior_delivery_benchmark.json",
                        "--output-root",
                        str(benchmark_output),
                    ],
                    output_dir=output_dir,
                    root=project_root,
                    command_runner=command_runner,
                    failure_category="benchmark_failed",
                )
            )
            if steps[-1]["status"] == "pass":
                steps.append(
                    _run_step(
                        step_id="composition_cad_check",
                        title="Interior composition CODEX_PREVIEW CAD batch check",
                        command=[
                            _python(),
                            "scripts/run_composition_cad_check.py",
                            "--benchmark-output-root",
                            str(benchmark_output),
                            "--output-dir",
                            str(output_dir / "composition_cad"),
                            "--start-x",
                            "38000",
                            "--start-y",
                            "22000",
                            "--spacing-x",
                            "4200",
                        ],
                        output_dir=output_dir,
                        root=project_root,
                        command_runner=command_runner,
                        failure_category="cad_geometry_not_verified",
                        strict_geometry=require_cad_verified,
                    )
                )
            else:
                steps.append(
                    _not_run_step(
                        step_id="composition_cad_check",
                        title="Interior composition CODEX_PREVIEW CAD batch check",
                        blocked_by="interior_delivery_benchmark",
                    )
                )
        else:
            steps.append(
                _deferred_step(
                    step_id="composition_cad_check",
                    title="Interior composition CODEX_PREVIEW CAD batch check",
                    reason="real CAD batch readback is intentionally skipped in --no-cad mode",
                )
            )

    if "primitive_matrix_cad" in active_case_ids:
        if include_cad:
            steps.append(
                _run_step(
                    step_id="primitive_matrix_cad",
                    title="Primitive capability matrix (real CAD)",
                    command=[
                        _python(),
                        "scripts/run_primitive_matrix.py",
                        "--output-dir",
                        str(output_dir / "primitive_matrix_cad"),
                    ],
                    output_dir=output_dir,
                    root=project_root,
                    command_runner=command_runner,
                    failure_category="primitive_matrix_failed",
                    strict_geometry=require_cad_verified,
                )
            )
        else:
            steps.append(
                _deferred_step(
                    step_id="primitive_matrix_cad",
                    title="Primitive capability matrix (real CAD)",
                    reason="real CAD primitive matrix is intentionally skipped in --no-cad mode",
                )
            )

    if "primitive_matrix_no_cad" in active_case_ids:
        primitive_command = [
            _python(),
            "scripts/run_primitive_matrix.py",
            "--no-cad",
            "--output-dir",
            str(output_dir / "primitive_matrix"),
        ]
        steps.append(
            _run_step(
                step_id="primitive_matrix_no_cad",
                title="Primitive capability matrix (no-CAD)",
                command=primitive_command,
                output_dir=output_dir,
                root=project_root,
                command_runner=command_runner,
                failure_category="primitive_matrix_failed",
                strict_geometry=False,
            )
        )

    if "cad_plan_fixture_suite_no_cad" in active_case_ids:
        fixture_no_cad_command = [
            _python(),
            "scripts/run_cad_plan_fixture_suite.py",
            "--no-cad",
            "--output-dir",
            str(output_dir / "cad_plan_fixture_suite"),
        ]
        steps.append(
            _run_step(
                step_id="cad_plan_fixture_suite_no_cad",
                title="CAD_PLAN fixture suite validate and dry-run",
                command=fixture_no_cad_command,
                output_dir=output_dir,
                root=project_root,
                command_runner=command_runner,
                failure_category="cad_plan_fixture_suite_failed",
            )
        )

    if "cad_plan_fixture_suite_cad" in active_case_ids:
        if include_cad:
            fixture_cad_command = [
                _python(),
                "scripts/run_cad_plan_fixture_suite.py",
                "--output-dir",
                str(output_dir / "cad_plan_fixture_suite_cad"),
            ]
            steps.append(
                _run_step(
                    step_id="cad_plan_fixture_suite_cad",
                    title="CAD_PLAN fixture suite CODEX_PREVIEW execution",
                    command=fixture_cad_command,
                    output_dir=output_dir,
                    root=project_root,
                    command_runner=command_runner,
                    failure_category="cad_geometry_not_verified",
                    strict_geometry=require_cad_verified,
                )
            )
        else:
            steps.append(
                _deferred_step(
                    step_id="cad_plan_fixture_suite_cad",
                    title="CAD_PLAN fixture suite CODEX_PREVIEW execution",
                    reason="real CAD fixture execution is intentionally skipped in --no-cad mode",
                )
            )

    if "complex_cad_smoke" in active_case_ids:
        complex_command = [
            _python(),
            "scripts/run_complex_cad_smoke.py",
            "--output-dir",
            str(output_dir / "complex_cad_smoke"),
        ]
        if not include_cad:
            complex_command.append("--no-cad")
        steps.append(
            _run_step(
                step_id="complex_cad_smoke",
                title="Complex mixed-primitive CODEX_PREVIEW CAD smoke",
                command=complex_command,
                output_dir=output_dir,
                root=project_root,
                command_runner=command_runner,
                failure_category="cad_geometry_not_verified",
                strict_geometry=include_cad and require_cad_verified,
            )
        )

    summary = _build_summary(
        steps,
        include_cad=include_cad,
        selected_case_ids=active_case_ids,
        manifest_case_count=len(manifest_case_ids(manifest)),
        strict=require_cad_verified,
    )
    report = {
        "version": "0.1",
        "status": _overall_status(summary),
        "root": str(project_root),
        "output_dir": str(output_dir),
        "include_cad": include_cad,
        "require_cad_verified": require_cad_verified,
        "selected_case_ids": active_case_ids,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "manifest": manifest_summary(manifest),
        "safety": {
            "layer": PREVIEW_LAYER,
            "saved_dwg": False,
            "deleted_entities": False,
            "modified_formal_layers": False,
        },
        "summary": summary,
        "steps": steps,
    }
    _write_text(output_dir / "local_cad_regression_report.json", json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    _write_text(output_dir / "local_cad_regression_report.md", _markdown_report(report))
    _write_evidence_trend_report(output_dir=output_dir, report=report)
    return report


