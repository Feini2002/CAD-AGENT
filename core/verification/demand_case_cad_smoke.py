"""Run demand-side benchmark cases through real CAD execution (V-PROOF-22)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.benchmarks.runner import run_benchmark_suite
from core.execution.batch_plan_runner import execute_plan_batch
from core.plan_engine.validate_plan import load_json, validate_plan
from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    SCREENSHOT_NOT_APPLICABLE,
)
from core.verification.preview_only_audit import build_preview_only_audit

DEFAULT_MANIFEST = Path("examples") / "capability_proof" / "demand_case_cad_manifest.json"
BASE_OFFSET = [96000.0, 60000.0, 0.0]
CASE_SPACING_X = 6000.0


def load_demand_case_cad_manifest(path: Path) -> dict[str, Any]:
    manifest = load_json(path)
    if manifest.get("manifest_id") != "demand_case_cad":
        raise ValueError("demand_case_cad manifest_id must be 'demand_case_cad'.")
    cases = manifest.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("demand_case_cad manifest requires a non-empty cases array.")
    return manifest


def _plan_paths_for_case(case_dir: Path) -> list[Path]:
    single = case_dir / "cad_plan.json"
    if single.is_file():
        return [single]
    items_dir = case_dir / "cad_plan_items"
    if items_dir.is_dir():
        plans = sorted(items_dir.glob("cad_plan_*.json"))
        if plans:
            return plans
    raise FileNotFoundError(f"No CAD_PLAN artifacts in {case_dir}")


def run_demand_case_cad_smoke(
    *,
    root: Path,
    output_dir: Path | None = None,
    manifest_path: Path | None = None,
    no_cad: bool = False,
    driver: Any | None = None,
    skip_benchmark: bool = False,
) -> dict[str, Any]:
    manifest_path = manifest_path or (root / DEFAULT_MANIFEST)
    manifest = load_demand_case_cad_manifest(manifest_path)
    suite_path = root / str(manifest["benchmark_suite_path"])
    benchmark_root = (output_dir or root) / "demand_benchmark"
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)

    if not skip_benchmark:
        benchmark_result = run_benchmark_suite(suite_path, output_root=benchmark_root)
        if benchmark_result.get("status") != "pass":
            return {
                "version": "0.1",
                "suite_id": "demand_case_cad_smoke",
                "status": "fail",
                "failure_category": "benchmark_failed",
                "benchmark_result": benchmark_result,
                "cases": [],
            }

    case_rows: list[dict[str, Any]] = []
    for index, item in enumerate(manifest["cases"]):
        case_id = str(item["case_id"])
        capability_id = str(item.get("registry_capability_id", ""))
        case_dir = benchmark_root / case_id
        row: dict[str, Any] = {
            "case_id": case_id,
            "registry_capability_id": capability_id,
            "case_output_dir": str(case_dir),
        }
        if not case_dir.is_dir():
            row["status"] = "fail"
            row["geometry_verified"] = False
            row["failure_category"] = "missing_benchmark_output"
            case_rows.append(row)
            continue

        try:
            plan_paths = _plan_paths_for_case(case_dir)
        except FileNotFoundError as exc:
            row["status"] = "fail"
            row["geometry_verified"] = False
            row["failure_category"] = "missing_cad_plan"
            row["message"] = str(exc)
            case_rows.append(row)
            continue

        for plan_path in plan_paths:
            errors = validate_plan(load_json(plan_path))
            if errors:
                row["status"] = "fail"
                row["geometry_verified"] = False
                row["validate_errors"] = errors
                break
        else:
            if no_cad or driver is None:
                row["cad_execution_status"] = "deferred"
                row["geometry_verified"] = False
                row["evidence_state"] = EVIDENCE_DEFERRED_CAD_READBACK
                row["status"] = "pass"
            else:
                offset = [
                    BASE_OFFSET[0] + index * CASE_SPACING_X,
                    BASE_OFFSET[1],
                    BASE_OFFSET[2],
                ]
                cad_dir = (output_dir or root) / "demand_cad" / case_id
                batch = execute_plan_batch(plan_paths, output_dir=cad_dir, driver=driver, offset=offset)
                verified = batch.get("status") == "geometry_verified"
                row["cad_execution_status"] = "executed" if verified else "fail"
                row["geometry_verified"] = verified
                row["created_handle_count"] = batch.get("created_handle_count", 0)
                row["evidence_state"] = (
                    EVIDENCE_READBACK_GEOMETRY_VERIFIED if verified else EVIDENCE_DEFERRED_CAD_READBACK
                )
                row["status"] = "pass" if verified else "fail"
                if verified:
                    row["verification_report_path"] = str(
                        cad_dir / "verification_reports" / "verification_report_001.json"
                    )
        case_rows.append(row)

    verified_count = sum(1 for row in case_rows if row.get("geometry_verified"))
    report = {
        "version": "0.1",
        "suite_id": "demand_case_cad_smoke",
        "status": "geometry_verified" if verified_count == len(case_rows) and verified_count > 0 else "fail",
        "geometry_verified": verified_count == len(case_rows) and verified_count > 0,
        "case_count": len(case_rows),
        "geometry_verified_count": verified_count,
        "safety": build_preview_only_audit(),
        "cases": case_rows,
    }
    if verified_count > 0 and not no_cad:
        report["evidence_state"] = EVIDENCE_READBACK_GEOMETRY_VERIFIED
        report["geometry_accuracy"] = GEOMETRY_VERIFIED_BY_READBACK
        report["screenshot_role"] = SCREENSHOT_NOT_APPLICABLE
    if output_dir is not None:
        (output_dir / "demand_case_cad_smoke_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return report
