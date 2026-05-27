"""Batch draw_object CAD smoke for core object types (V-PROOF-21)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from core.execution.batch_plan_runner import execute_plan_batch
from core.plan_engine.validate_plan import load_json, validate_plan
from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)
from core.verification.preview_only_audit import build_preview_only_audit

DEFAULT_OBJECT_CAD_SMOKE_MANIFEST = Path("examples") / "capability_proof" / "object_cad_smoke_manifest.json"
DEFAULT_SMOKE_OFFSET = [72000, 42000, 0]
SMOKE_SPACING_X = 4500


def load_object_cad_smoke_manifest(path: Path) -> dict[str, Any]:
    manifest = load_json(path)
    if manifest.get("version") != "0.1":
        raise ValueError("object_cad_smoke_manifest version must be '0.1'.")
    if manifest.get("manifest_id") != "object_cad_smoke":
        raise ValueError("object_cad_smoke_manifest manifest_id must be 'object_cad_smoke'.")
    objects = manifest.get("objects")
    if not isinstance(objects, list) or not objects:
        raise ValueError("object_cad_smoke_manifest requires a non-empty objects array.")
    return manifest


def _resolve_plan_path(root: Path, plan_path: str) -> Path:
    path = Path(plan_path)
    return path if path.is_absolute() else (root / path).resolve()


def run_object_cad_smoke(
    *,
    root: Path,
    manifest_path: Path | None = None,
    output_dir: Path | None = None,
    no_cad: bool = False,
    driver: Any | None = None,
    base_offset: list[float] | None = None,
) -> dict[str, Any]:
    manifest_path = manifest_path or (root / DEFAULT_OBJECT_CAD_SMOKE_MANIFEST)
    manifest = load_object_cad_smoke_manifest(manifest_path)
    object_rows: list[dict[str, Any]] = []
    plan_paths: list[Path] = []
    cad_rows: list[dict[str, Any]] = []

    for index, item in enumerate(manifest["objects"]):
        plan_path = _resolve_plan_path(root, str(item["plan_path"]))
        errors = validate_plan(load_json(plan_path)) if plan_path.exists() else ["plan file not found"]
        row: dict[str, Any] = {
            "object_type": item["object_type"],
            "registry_capability_id": item.get("registry_capability_id"),
            "plan_path": str(plan_path),
            "validate_status": "pass" if not errors else "fail",
            "validate_errors": errors,
        }
        if errors:
            row["cad_execution_status"] = "skipped"
            row["geometry_verified"] = False
            row["evidence_state"] = EVIDENCE_DEFERRED_CAD_READBACK
            row["status"] = "fail"
            object_rows.append(row)
            continue

        if not item.get("cad_execution", True) or no_cad or driver is None:
            row["cad_execution_status"] = "deferred" if no_cad else "skipped"
            row["geometry_verified"] = False
            row["evidence_state"] = EVIDENCE_DEFERRED_CAD_READBACK
            row["status"] = "pass"
            object_rows.append(row)
            continue

        offset = list(base_offset or DEFAULT_SMOKE_OFFSET)
        offset[0] = float(offset[0]) + index * SMOKE_SPACING_X
        plan_paths.append(plan_path)
        cad_rows.append({"row": row, "offset": offset})

    batch_report: dict[str, Any] = {}
    if plan_paths and driver is not None and output_dir is not None:
        batch_dir = output_dir / "batch"
        for index, entry in enumerate(cad_rows):
            single_dir = batch_dir / f"object_{index + 1:02d}"
            single_dir.mkdir(parents=True, exist_ok=True)
            batch_result = execute_plan_batch(
                [plan_paths[index]],
                output_dir=single_dir,
                driver=driver,
                offset=entry["offset"],
            )
            row = entry["row"]
            verified = batch_result.get("status") == "geometry_verified"
            row["cad_execution_status"] = "executed" if verified else "fail"
            row["geometry_verified"] = verified
            row["evidence_state"] = EVIDENCE_READBACK_GEOMETRY_VERIFIED if verified else EVIDENCE_DEFERRED_CAD_READBACK
            row["created_handle_count"] = batch_result.get("created_handle_count", 0)
            row["verification_report_path"] = str(
                single_dir / "verification_reports" / "verification_report_001.json"
            )
            row["status"] = "pass" if row["validate_status"] == "pass" and verified else "fail"
            object_rows.append(row)
        batch_report = {"per_object_batch": True, "object_count": len(cad_rows)}

    passed = sum(1 for row in object_rows if row["status"] == "pass")
    cad_verified = [row for row in object_rows if row.get("geometry_verified")]
    report = {
        "version": "0.1",
        "suite_id": "object_cad_smoke",
        "status": "pass" if passed == len(object_rows) else "fail",
        "no_cad": no_cad,
        "object_count": len(object_rows),
        "passed_object_count": passed,
        "geometry_verified_object_count": len(cad_verified),
        "safety": build_preview_only_audit(),
        "objects": object_rows,
        "batch": batch_report,
    }
    if no_cad:
        report["evidence_state"] = EVIDENCE_DEFERRED_CAD_READBACK
        report["geometry_accuracy"] = NON_CAD_GEOMETRY_ACCURACY
        report["screenshot_role"] = SCREENSHOT_NOT_APPLICABLE
        report["geometry_verified"] = False
    elif cad_verified and len(cad_verified) == len([r for r in object_rows if r.get("cad_execution_status") == "executed"]):
        report["status"] = "geometry_verified"
        report["geometry_verified"] = True
        report["evidence_state"] = EVIDENCE_READBACK_GEOMETRY_VERIFIED
        report["geometry_accuracy"] = GEOMETRY_VERIFIED_BY_READBACK
        report["screenshot_role"] = SCREENSHOT_NOT_APPLICABLE
    else:
        report["geometry_verified"] = False
        report["evidence_state"] = EVIDENCE_DEFERRED_CAD_READBACK
        report["geometry_accuracy"] = NON_CAD_GEOMETRY_ACCURACY
        report["screenshot_role"] = SCREENSHOT_NOT_APPLICABLE

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "object_cad_smoke_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return report
