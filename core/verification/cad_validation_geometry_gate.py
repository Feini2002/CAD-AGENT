"""Classify CAD validation steps into geometry vs infrastructure gates (CAD-VAL-01)."""

from __future__ import annotations

from typing import Any

GEOMETRY_STEP_IDS = frozenset(
    {
        "validate_sample_plan",
        "dry_run_sample_plan",
        "execute_sample_plan",
        "inspect_readback",
        "cad_capability_probe",
        "block_alpha_validate_plan",
        "block_alpha_dry_run",
        "block_alpha_execute",
        "block_alpha_readback",
    }
)

INFRASTRUCTURE_STEP_IDS = frozenset(
    {
        "python_import_pillow",
        "python_import_pywin32",
        "python_import_win32gui",
        "self_check",
        "unit_tests",
        "render_preview_check",
        "non_cad_benchmark",
        "capture_screen",
        "block_alpha_capture_screen",
        "block_alpha_deferred_evidence",
        "autocad_com_connect",
    }
)


def step_gate_bucket(step_id: str) -> str:
    if step_id in GEOMETRY_STEP_IDS:
        return "geometry"
    if step_id in INFRASTRUCTURE_STEP_IDS:
        return "infrastructure"
    return "other"


def _gate_status(records: list[dict[str, Any]], *, bucket: str) -> dict[str, Any]:
    scoped = [record for record in records if step_gate_bucket(str(record.get("id", ""))) == bucket]
    failed_required = [
        record
        for record in scoped
        if record.get("status") == "fail" and record.get("required", True)
    ]
    if not failed_required:
        status = "pass"
    else:
        external_categories = {"cad_connection_failed", "missing_dependency", "screenshot_failed"}
        if all(record.get("failure_category") in external_categories for record in failed_required):
            status = "external_blocker"
        else:
            status = "fail"
    return {
        "status": status,
        "step_count": len(scoped),
        "failed_required_step_ids": [str(record.get("id", "")) for record in failed_required],
    }


def build_geometry_infrastructure_gates(records: list[dict[str, Any]]) -> dict[str, Any]:
    geometry = _gate_status(records, bucket="geometry")
    infrastructure = _gate_status(records, bucket="infrastructure")
    return {
        "geometry_gate": geometry,
        "infrastructure_gate": infrastructure,
    }


def resolve_report_status_with_geometry_gate(
    records: list[dict[str, Any]],
    *,
    geometry_gate_mode: bool,
) -> str:
    if not geometry_gate_mode:
        return _legacy_overall_status(records)
    geometry_status = _gate_status(records, bucket="geometry")["status"]
    if geometry_status == "pass":
        return "pass"
    if geometry_status == "external_blocker":
        return "external_blocker"
    return "fail"


def _legacy_overall_status(records: list[dict[str, Any]]) -> str:
    failed = [record for record in records if record.get("status") == "fail" and record.get("required", True)]
    if not failed:
        return "pass"
    external_categories = {"cad_connection_failed", "missing_dependency", "screenshot_failed"}
    if all(record.get("failure_category") in external_categories for record in failed):
        return "external_blocker"
    return "fail"
