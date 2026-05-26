"""Commercial fitout sample CODEX_PREVIEW CAD smoke with created-handle readback (C-CFIT-06)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.agents.commercial_fitout_sample_confirmation import (
    FITOUT_SAMPLE_ID,
    run_fitout_sample_confirmation_loop,
)
from core.execution.batch_plan_runner import execute_plan_batch
from core.path_safety import find_project_root, resolve_under_project_output
from core.project_samples.cad_check import collect_sample_plan_paths, connect_autocad_driver
from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)
from core.verification.preview_only_audit import build_preview_only_audit

DEFAULT_CAD_OFFSET = [64000, 36000, 0]
PREVIEW_LAYER = "CODEX_PREVIEW"
REPORT_VERSION = "0.1"
SAFETY_CLAIMS = build_preview_only_audit(layer=PREVIEW_LAYER)

PRODUCT_CLAIM_BOUNDARY = {
    "declares_scene_product": False,
    "declares_full_fitout_delivery": False,
    "geometry_verified_scope": "commercial_fitout_sample_confirmed_plans_only",
    "sample_id": FITOUT_SAMPLE_ID,
}


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_fitout_sample_confirmed_plans(
    workflow_output_dir: Path,
    *,
    project_root: Path,
) -> dict[str, Any]:
    """Run C-CFIT-05 confirmation loop when cad_plan_items are missing."""

    plan_dir = workflow_output_dir / "cad_plan_items"
    if plan_dir.is_dir() and any(plan_dir.glob("cad_plan_*.json")):
        return {"status": "ok", "skipped_confirmation_loop": True}
    return run_fitout_sample_confirmation_loop(
        workflow_output_dir,
        project_root=project_root,
    )


def build_deferred_commercial_fitout_cad_smoke_report(
    *,
    workflow_output_dir: Path,
    output_dir: Path,
    reason: str = "no_cad",
) -> dict[str, Any]:
    plan_count = 0
    try:
        plan_count = len(collect_sample_plan_paths(workflow_output_dir))
    except ValueError:
        plan_count = 0

    return {
        "version": REPORT_VERSION,
        "sample_id": FITOUT_SAMPLE_ID,
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
        "product_claim_boundary": dict(PRODUCT_CLAIM_BOUNDARY),
    }


def run_commercial_fitout_cad_smoke(
    workflow_output_dir: Path,
    *,
    output_dir: Path,
    project_root: Path | None = None,
    driver: Any | None = None,
    no_cad: bool = False,
    offset: list[float | int] | None = None,
) -> dict[str, Any]:
    """Execute confirmed fitout sample CAD_PLAN items on CODEX_PREVIEW and read back handles."""

    root_hint = workflow_output_dir if workflow_output_dir.is_absolute() else Path.cwd()
    root = project_root or find_project_root(root_hint)
    workflow_output_dir = resolve_under_project_output(
        root,
        workflow_output_dir,
        label="workflow_output_dir",
    )
    output_dir = resolve_under_project_output(root, output_dir, label="output_dir")
    output_dir.mkdir(parents=True, exist_ok=True)

    if no_cad or driver is None:
        report = build_deferred_commercial_fitout_cad_smoke_report(
            workflow_output_dir=workflow_output_dir,
            output_dir=output_dir,
            reason="no_cad" if no_cad else "driver_not_provided",
        )
        _write_json(output_dir / "commercial_fitout_cad_smoke_report.json", report)
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
        "version": REPORT_VERSION,
        "sample_id": FITOUT_SAMPLE_ID,
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
        "product_claim_boundary": dict(PRODUCT_CLAIM_BOUNDARY),
    }
    _write_json(output_dir / "commercial_fitout_cad_smoke_report.json", report)
    return report


def run_commercial_fitout_cad_smoke_with_workflow(
    *,
    project_root: Path,
    workflow_output_dir: Path,
    cad_output_dir: Path,
    driver: Any | None = None,
    no_cad: bool = False,
    offset: list[float | int] | None = None,
) -> dict[str, Any]:
    """Ensure confirmed plans exist, then run CODEX_PREVIEW CAD smoke."""

    project_root = project_root.resolve()
    workflow_output_dir = resolve_under_project_output(
        project_root,
        workflow_output_dir,
        label="workflow_output_dir",
    )
    cad_output_dir = resolve_under_project_output(project_root, cad_output_dir, label="output_dir")

    prep = ensure_fitout_sample_confirmed_plans(workflow_output_dir, project_root=project_root)
    if prep.get("skipped_confirmation_loop") is not True and prep.get("status") != "ok":
        raise ValueError(f"fitout confirmation loop failed: {prep}")

    return run_commercial_fitout_cad_smoke(
        workflow_output_dir,
        output_dir=cad_output_dir,
        project_root=project_root,
        driver=driver,
        no_cad=no_cad,
        offset=offset,
    )


__all__ = [
    "DEFAULT_CAD_OFFSET",
    "PRODUCT_CLAIM_BOUNDARY",
    "build_deferred_commercial_fitout_cad_smoke_report",
    "connect_autocad_driver",
    "ensure_fitout_sample_confirmed_plans",
    "run_commercial_fitout_cad_smoke",
    "run_commercial_fitout_cad_smoke_with_workflow",
]
