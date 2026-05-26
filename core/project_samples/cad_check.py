"""Optional real CAD verification for project samples (BETA-PROJECT-SAMPLE-05)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.execution.batch_plan_runner import execute_plan_batch
from core.path_safety import find_project_root, resolve_under_project_output
from core.project_samples.workflow import DEFAULT_SAMPLE_ID, run_sample_blank_shell_workflow
from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)
from core.verification.preview_only_audit import build_preview_only_audit

DEFAULT_CAD_OFFSET = [28000, 12000, 0]
PREVIEW_LAYER = "CODEX_PREVIEW"
SAFETY_CLAIMS = build_preview_only_audit(layer=PREVIEW_LAYER)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def collect_sample_plan_paths(workflow_output_dir: Path) -> list[Path]:
    """Return sorted CAD_PLAN item paths produced by blank-shell pipeline."""

    plan_dir = workflow_output_dir / "cad_plan_items"
    if not plan_dir.is_dir():
        raise ValueError(f"Missing cad_plan_items directory: {plan_dir}")
    plans = sorted(plan_dir.glob("cad_plan_*.json"))
    if not plans:
        raise ValueError(f"No cad_plan_*.json files found in {plan_dir}")
    return plans


def build_deferred_project_sample_cad_report(
    *,
    sample_id: str,
    workflow_output_dir: Path,
    output_dir: Path,
    reason: str = "no_cad",
) -> dict[str, Any]:
    """Structured deferred report when real AutoCAD is not available."""

    plan_count = 0
    try:
        plan_count = len(collect_sample_plan_paths(workflow_output_dir))
    except ValueError:
        plan_count = 0

    return {
        "version": "0.1",
        "sample_id": sample_id,
        "status": "deferred",
        "evidence_state": EVIDENCE_DEFERRED_CAD_READBACK,
        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
        "geometry_verified": False,
        "workflow_output_dir": str(workflow_output_dir),
        "output_dir": str(output_dir),
        "plan_count": plan_count,
        "created_handle_count": 0,
        "deferred_reason": reason,
        "safety": dict(SAFETY_CLAIMS),
    }


def run_project_sample_cad_check(
    workflow_output_dir: Path,
    *,
    output_dir: Path,
    sample_id: str = DEFAULT_SAMPLE_ID,
    driver: Any | None = None,
    no_cad: bool = False,
    offset: list[float | int] | None = None,
) -> dict[str, Any]:
    """Execute sample CAD_PLAN items on CODEX_PREVIEW and read back created handles."""

    root_hint = workflow_output_dir if workflow_output_dir.is_absolute() else Path.cwd()
    project_root = find_project_root(root_hint)
    workflow_output_dir = resolve_under_project_output(
        project_root,
        workflow_output_dir,
        label="workflow_output_dir",
    )
    output_dir = resolve_under_project_output(project_root, output_dir, label="output_dir")
    output_dir.mkdir(parents=True, exist_ok=True)

    if no_cad or driver is None:
        report = build_deferred_project_sample_cad_report(
            sample_id=sample_id,
            workflow_output_dir=workflow_output_dir,
            output_dir=output_dir,
            reason="no_cad" if no_cad else "driver_not_provided",
        )
        _write_json(output_dir / "project_sample_cad_check_report.json", report)
        return report

    plan_paths = collect_sample_plan_paths(workflow_output_dir)
    batch_result = execute_plan_batch(
        plan_paths,
        output_dir=output_dir / "batch",
        driver=driver,
        offset=offset or DEFAULT_CAD_OFFSET,
    )

    geometry_verified = batch_result.get("status") == "geometry_verified"
    report = {
        "version": "0.1",
        "sample_id": sample_id,
        "status": batch_result.get("status", "failed"),
        "evidence_state": EVIDENCE_READBACK_GEOMETRY_VERIFIED
        if geometry_verified
        else EVIDENCE_DEFERRED_CAD_READBACK,
        "geometry_accuracy": GEOMETRY_VERIFIED_BY_READBACK if geometry_verified else NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
        "geometry_verified": geometry_verified,
        "workflow_output_dir": str(workflow_output_dir),
        "output_dir": str(output_dir),
        "plan_count": batch_result.get("plan_count", len(plan_paths)),
        "created_handle_count": batch_result.get("created_handle_count", 0),
        "created_handles": batch_result.get("created_handles", []),
        "batch_execution": batch_result,
        "safety": dict(SAFETY_CLAIMS),
    }
    _write_json(output_dir / "project_sample_cad_check_report.json", report)
    return report


def run_project_sample_cad_check_with_workflow(
    *,
    project_root: Path,
    workflow_output_dir: Path,
    cad_output_dir: Path,
    sample_id: str = DEFAULT_SAMPLE_ID,
    driver: Any | None = None,
    no_cad: bool = False,
    offset: list[float | int] | None = None,
) -> dict[str, Any]:
    """Run sample workflow (if needed) then optional CAD check."""

    project_root = project_root.resolve()
    workflow_output_dir = resolve_under_project_output(
        project_root,
        workflow_output_dir,
        label="workflow_output_dir",
    )
    cad_output_dir = resolve_under_project_output(project_root, cad_output_dir, label="output_dir")
    if not (workflow_output_dir / "cad_plan_items").is_dir():
        pipeline = run_sample_blank_shell_workflow(
            sample_id,
            project_root=project_root,
            output_dir=workflow_output_dir,
        )
        if pipeline.get("status") != "ok":
            raise ValueError(f"sample workflow failed: {pipeline}")

    return run_project_sample_cad_check(
        workflow_output_dir,
        output_dir=cad_output_dir,
        sample_id=sample_id,
        driver=driver,
        no_cad=no_cad,
        offset=offset,
    )


def connect_autocad_driver() -> Any:
    from core.cad_io.autocad_com import AutoCADComDriver

    return AutoCADComDriver(connect_existing_only=True)
