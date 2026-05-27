"""LCAD-08: rollup CAD readback across registered de-identified project samples."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.agents.commercial_fitout_cad_smoke import run_commercial_fitout_cad_smoke_with_workflow
from core.path_safety import find_project_root, resolve_under_project_output
from core.project_samples.cad_check import (
    connect_autocad_driver,
    run_project_sample_cad_check_with_workflow,
)
from core.schemas.validator import validate_value
from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
)
from core.verification.preview_only_audit import build_preview_only_audit

REPORT_VERSION = "0.1"
DEFAULT_MANIFEST_REL = Path("examples/cad_regression/project_sample_cad_rollup.json")
SCHEMA_PATH_REL = Path("core/schemas/project_sample_cad_rollup.schema.json")
SAFETY_CLAIMS = build_preview_only_audit(layer="CODEX_PREVIEW")

REQUIRED_SAMPLE_IDS = frozenset(
    {
        "sample_blank_shell",
        "commercial_fitout_sample",
        "commercial_fitout_meeting_sample",
        "commercial_fitout_reception_sample",
    }
)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_project_sample_cad_manifest(path: Path | None = None, *, project_root: Path | None = None) -> dict[str, Any]:
    root = project_root or find_project_root(Path(__file__))
    manifest_path = path or (root / DEFAULT_MANIFEST_REL)
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def validate_project_sample_cad_manifest(manifest: dict[str, Any], *, project_root: Path | None = None) -> list[str]:
    root = project_root or find_project_root(Path(__file__))
    schema = json.loads((root / SCHEMA_PATH_REL).read_text(encoding="utf-8"))
    return validate_value(manifest, schema)


def _run_sample_entry(
    entry: dict[str, Any],
    *,
    project_root: Path,
    workflow_output_dir: Path,
    cad_output_dir: Path,
    driver: Any | None,
    no_cad: bool,
) -> dict[str, Any]:
    sample_id = str(entry["sample_id"])
    runner = str(entry["runner"])
    offset = list(entry.get("cad_offset", [0, 0, 0]))

    if runner == "blank_shell_workflow":
        report = run_project_sample_cad_check_with_workflow(
            project_root=project_root,
            workflow_output_dir=workflow_output_dir,
            cad_output_dir=cad_output_dir,
            sample_id=sample_id,
            driver=driver,
            no_cad=no_cad,
            offset=offset,
        )
    elif runner == "fitout_confirmation_workflow":
        workflow_path = project_root / str(entry["workflow_path"])
        report = run_commercial_fitout_cad_smoke_with_workflow(
            project_root=project_root,
            workflow_output_dir=workflow_output_dir,
            cad_output_dir=cad_output_dir,
            workflow_path=workflow_path,
            driver=driver,
            no_cad=no_cad,
            offset=offset,
        )
    else:
        raise ValueError(f"unknown runner: {runner!r}")

    report_path = cad_output_dir / str(entry["report_filename"])
    return {
        "sample_id": sample_id,
        "runner": runner,
        "workflow_output_dir": str(workflow_output_dir),
        "cad_output_dir": str(cad_output_dir),
        "report_path": str(report_path) if report_path.is_file() else "",
        "status": str(report.get("status", "")),
        "geometry_verified": bool(report.get("geometry_verified")),
        "evidence_state": str(report.get("evidence_state", "")),
        "created_handle_count": int(report.get("created_handle_count", 0)),
        "plan_count": int(report.get("plan_count", 0)),
        "report": report,
    }


def run_project_sample_cad_rollup(
    output_dir: Path,
    *,
    project_root: Path | None = None,
    manifest_path: Path | None = None,
    driver: Any | None = None,
    no_cad: bool = False,
) -> dict[str, Any]:
    """Run CAD check for each registered project sample and emit rollup report."""

    root = project_root or find_project_root(Path(__file__))
    output_dir = resolve_under_project_output(root, output_dir, label="output_dir")
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_project_sample_cad_manifest(manifest_path, project_root=root)
    manifest_errors = validate_project_sample_cad_manifest(manifest, project_root=root)
    if manifest_errors:
        return {
            "version": REPORT_VERSION,
            "package_id": manifest.get("package_id", "LCAD-08-PROJECT-SAMPLE-CAD"),
            "status": "invalid",
            "errors": manifest_errors,
            "samples": [],
        }

    sample_results: list[dict[str, Any]] = []
    for entry in manifest.get("samples", []):
        if not isinstance(entry, dict):
            continue
        sample_id = str(entry["sample_id"])
        workflow_dir = output_dir / "workflows" / sample_id
        cad_dir = output_dir / "cad" / sample_id
        sample_results.append(
            _run_sample_entry(
                entry,
                project_root=root,
                workflow_output_dir=workflow_dir,
                cad_output_dir=cad_dir,
                driver=driver,
                no_cad=no_cad,
            )
        )

    verified_count = sum(1 for item in sample_results if item.get("geometry_verified"))
    deferred_count = sum(1 for item in sample_results if item.get("status") == "deferred")
    failed_count = sum(
        1
        for item in sample_results
        if item.get("status") not in {"geometry_verified", "deferred"} and not item.get("geometry_verified")
    )

    if verified_count == len(sample_results) and sample_results:
        status = "geometry_verified"
        evidence_state = EVIDENCE_READBACK_GEOMETRY_VERIFIED
    elif deferred_count == len(sample_results):
        status = "deferred"
        evidence_state = EVIDENCE_DEFERRED_CAD_READBACK
    elif verified_count > 0:
        status = "mixed"
        evidence_state = EVIDENCE_DEFERRED_CAD_READBACK
    else:
        status = "failed"
        evidence_state = EVIDENCE_DEFERRED_CAD_READBACK

    rollup = {
        "version": REPORT_VERSION,
        "rollup_id": str(manifest.get("rollup_id", "")),
        "package_id": str(manifest.get("package_id", "LCAD-08-PROJECT-SAMPLE-CAD")),
        "status": status,
        "evidence_state": evidence_state,
        "geometry_verified": status == "geometry_verified",
        "sample_count": len(sample_results),
        "geometry_verified_count": verified_count,
        "deferred_count": deferred_count,
        "failed_count": failed_count,
        "output_dir": str(output_dir),
        "safety": dict(SAFETY_CLAIMS),
        "samples": [
            {
                "sample_id": item["sample_id"],
                "runner": item["runner"],
                "status": item["status"],
                "geometry_verified": item["geometry_verified"],
                "evidence_state": item["evidence_state"],
                "created_handle_count": item["created_handle_count"],
                "plan_count": item["plan_count"],
                "report_path": item["report_path"],
            }
            for item in sample_results
        ],
    }
    _write_json(output_dir / "project_sample_cad_rollup_report.json", rollup)
    return rollup


def assert_project_sample_cad_rollup_contract(rollup: dict[str, Any]) -> None:
    sample_ids = {str(item.get("sample_id")) for item in rollup.get("samples", []) if isinstance(item, dict)}
    missing = REQUIRED_SAMPLE_IDS - sample_ids
    if missing:
        raise AssertionError(f"rollup missing samples: {sorted(missing)!r}")

    if rollup.get("geometry_verified"):
        if not all(item.get("geometry_verified") for item in rollup.get("samples", []) if isinstance(item, dict)):
            raise AssertionError("rollup geometry_verified=true but not all samples verified")
        for item in rollup.get("samples", []):
            if isinstance(item, dict) and int(item.get("created_handle_count", 0)) < 1:
                raise AssertionError(f"sample {item.get('sample_id')} has no created handles")
