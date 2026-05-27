"""Per-catalog-object draw_object CAD smoke for commercial_fitout (V-PROOF-21 extension)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.execution.batch_plan_runner import execute_plan_batch
from core.plan_engine.validate_plan import load_json, validate_plan
from core.verification.commercial_fitout_catalog_manifest import (
    DEFAULT_COMMERCIAL_FITOUT_CATALOG_MANIFEST,
    DEFAULT_OBJECT_CATALOG_PATH,
    load_commercial_fitout_catalog_manifest,
)
from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)
from core.verification.preview_only_audit import build_preview_only_audit

DEFAULT_BASE_OFFSET = [90000, 52000, 0]
CATALOG_SPACING_X = 5000


def _catalog_object_map(catalog_path: Path) -> dict[str, dict[str, Any]]:
    catalog = load_json(catalog_path)
    return {
        str(row["catalog_object_id"]): row
        for row in catalog.get("objects", [])
        if isinstance(row, dict) and row.get("catalog_object_id")
    }


def build_fitout_catalog_draw_plan(
    *,
    catalog_object_id: str,
    catalog_row: dict[str, Any],
    display_name: str,
) -> dict[str, Any]:
    object_type = str(catalog_row.get("core_object_type", "cabinet"))
    size = catalog_row.get("default_size", {})
    width = int(size.get("width", 1000))
    depth = int(size.get("depth", 600))
    return {
        "version": "0.1",
        "domain": "commercial_fitout",
        "intent": "draw_object",
        "object": {
            "type": object_type,
            "name": display_name or catalog_object_id,
            "width": width,
            "depth": depth,
        },
        "placement": {"mode": "absolute", "base_point": [0, 0, 0]},
        "drawing": {
            "layer": "CODEX_PREVIEW",
            "include_label": False,
            "include_dimensions": False,
        },
        "confidence": 1.0,
        "needs_confirmation": False,
    }


def run_fitout_catalog_cad_smoke(
    *,
    root: Path,
    manifest_path: Path | None = None,
    catalog_path: Path | None = None,
    output_dir: Path | None = None,
    no_cad: bool = False,
    driver: Any | None = None,
    base_offset: list[float] | None = None,
    catalog_object_ids: list[str] | None = None,
) -> dict[str, Any]:
    manifest_path = manifest_path or (root / DEFAULT_COMMERCIAL_FITOUT_CATALOG_MANIFEST)
    catalog_path = catalog_path or (root / DEFAULT_OBJECT_CATALOG_PATH)
    manifest = load_commercial_fitout_catalog_manifest(manifest_path)
    catalog_by_id = _catalog_object_map(catalog_path)

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
    plan_dir = (output_dir / "generated_plans") if output_dir else None
    if plan_dir is not None:
        plan_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    selected_ids = catalog_object_ids or [str(row["catalog_object_id"]) for row in manifest["catalog_entries"]]

    for index, catalog_object_id in enumerate(selected_ids):
        entry = next(
            (row for row in manifest["catalog_entries"] if row["catalog_object_id"] == catalog_object_id),
            None,
        )
        if entry is None:
            results.append(
                {
                    "catalog_object_id": catalog_object_id,
                    "status": "fail",
                    "validate_errors": [f"unknown catalog_object_id: {catalog_object_id}"],
                }
            )
            continue

        catalog_row = catalog_by_id.get(catalog_object_id)
        if catalog_row is None:
            results.append(
                {
                    "catalog_object_id": catalog_object_id,
                    "registry_capability_id": entry.get("registry_capability_id"),
                    "status": "fail",
                    "validate_errors": ["missing from object_catalog.json"],
                }
            )
            continue

        plan = build_fitout_catalog_draw_plan(
            catalog_object_id=catalog_object_id,
            catalog_row=catalog_row,
            display_name=str(catalog_row.get("display_name", catalog_object_id)),
        )
        errors = validate_plan(plan)
        row: dict[str, Any] = {
            "catalog_object_id": catalog_object_id,
            "registry_capability_id": entry.get("registry_capability_id"),
            "core_object_type": catalog_row.get("core_object_type"),
            "validate_status": "pass" if not errors else "fail",
            "validate_errors": errors,
        }

        if errors or no_cad or driver is None:
            row["cad_execution_status"] = "deferred" if no_cad else "skipped"
            row["geometry_verified"] = False
            row["evidence_state"] = EVIDENCE_DEFERRED_CAD_READBACK
            row["status"] = "fail" if errors else "pass"
            results.append(row)
            continue

        assert plan_dir is not None and output_dir is not None
        plan_path = plan_dir / f"{catalog_object_id}.json"
        plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        offset = list(base_offset or DEFAULT_BASE_OFFSET)
        offset[0] = float(offset[0]) + index * CATALOG_SPACING_X
        batch_dir = output_dir / "batch" / catalog_object_id
        batch_result = execute_plan_batch([plan_path], output_dir=batch_dir, driver=driver, offset=offset)
        verified = batch_result.get("status") == "geometry_verified"
        row.update(
            {
                "plan_path": str(plan_path.relative_to(root)).replace("\\", "/"),
                "cad_execution_status": "executed" if verified else "fail",
                "geometry_verified": verified,
                "evidence_state": EVIDENCE_READBACK_GEOMETRY_VERIFIED if verified else EVIDENCE_DEFERRED_CAD_READBACK,
                "created_handle_count": batch_result.get("created_handle_count", 0),
                "verification_report_path": str(
                    (batch_dir / "verification_reports" / "verification_report_001.json").relative_to(root)
                ).replace("\\", "/"),
                "status": "pass" if verified else "fail",
            }
        )
        results.append(row)

    passed = sum(1 for row in results if row.get("status") == "pass")
    verified_count = sum(1 for row in results if row.get("geometry_verified"))
    report = {
        "version": "0.1",
        "suite_id": "fitout_catalog_cad_smoke",
        "status": "pass" if passed == len(results) and verified_count == len(selected_ids) else "fail",
        "no_cad": no_cad,
        "catalog_object_count": len(results),
        "passed_catalog_object_count": passed,
        "geometry_verified_catalog_object_count": verified_count,
        "safety": build_preview_only_audit(),
        "catalog_objects": results,
    }
    if no_cad:
        report["evidence_state"] = EVIDENCE_DEFERRED_CAD_READBACK
        report["geometry_accuracy"] = NON_CAD_GEOMETRY_ACCURACY
        report["screenshot_role"] = SCREENSHOT_NOT_APPLICABLE
    elif verified_count == len(selected_ids) and verified_count > 0:
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
        (output_dir / "fitout_catalog_cad_smoke_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return report
