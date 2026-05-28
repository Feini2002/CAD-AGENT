#!/usr/bin/env python3
"""Run TABLE-C final-gap CAD evidence for the last none registry rows."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.capabilities.runners import _verification_no_cad_report
from core.execution.execute_plan import execute_plan_file
from core.path_safety import resolve_under_project_output
from core.verification.evidence_contract import (
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    SCREENSHOT_NOT_APPLICABLE,
)
from core.verification.verification_report import build_verification_report


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _run_verification_no_cad_api_evidence(*, output_dir: Path, driver: object) -> dict:
    plan_path = PROJECT_ROOT / "examples" / "plans" / "draw_test_cabinet.json"
    api_dir = output_dir / "verification_no_cad_api"
    cad_dir = output_dir / "verification_no_cad_cad"
    api_dir.mkdir(parents=True, exist_ok=True)
    cad_dir.mkdir(parents=True, exist_ok=True)

    no_cad_report = _verification_no_cad_report({"plan_path": str(plan_path.relative_to(PROJECT_ROOT)).replace("\\", "/")})
    _write_json(api_dir / "no_cad_api_report.json", no_cad_report)

    execution_summary = execute_plan_file(
        plan_path,
        driver=driver,  # type: ignore[arg-type]
        preview_only=True,
        allow_unconfirmed=False,
    )
    created_handles = execution_summary.get("created_handles", [])
    if not isinstance(created_handles, list) or not created_handles:
        raise RuntimeError("verification_no_cad CAD mirror did not create handles")

    entities = driver.snapshot_handles(handles=[str(handle) for handle in created_handles], layer="CODEX_PREVIEW")  # type: ignore[attr-defined]
    cad_report = build_verification_report(
        plan_path=plan_path,
        entities=entities,
        created_handles=[str(handle) for handle in created_handles],
        execution_summary=execution_summary,
    )
    report_path = cad_dir / "verification_reports" / "verification_report_001.json"
    _write_json(report_path, cad_report)
    _write_json(
        cad_dir / "execution_summary.json",
        {
            "status": "executed",
            "layer": "CODEX_PREVIEW",
            "preview_only": True,
            "created_handles": [str(handle) for handle in created_handles],
        },
    )
    if cad_report.get("status") != "geometry_verified":
        raise RuntimeError(f"verification_no_cad CAD mirror not geometry_verified: {cad_report.get('status')}")

    return {
        "capability_id": "core.api.verification_no_cad_report",
        "no_cad_api_report": str(api_dir.relative_to(PROJECT_ROOT)).replace("\\", "/") + "/no_cad_api_report.json",
        "cad_report": str(report_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "created_handle_count": len(created_handles),
        "status": cad_report.get("status"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run TABLE-C final-gap CAD evidence bundle.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/validation_runs/tablec-final-gap-20260528-cad"),
    )
    parser.add_argument("--no-cad", action="store_true")
    args = parser.parse_args()

    output_dir = resolve_under_project_output(PROJECT_ROOT, args.output_dir, label="output_dir")
    output_dir.mkdir(parents=True, exist_ok=True)

    summary: dict = {
        "version": "0.1",
        "suite_id": "tablec_final_gap_cad",
        "output_dir": str(output_dir.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "no_cad": args.no_cad,
        "intents": [],
        "verification_no_cad": None,
    }

    if args.no_cad:
        _write_json(output_dir / "tablec_final_gap_summary.json", summary)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    from core.cad_io.autocad_com import AutoCADComDriver

    driver = AutoCADComDriver(connect_existing_only=True)

    from core.verification.intent_lab_cad import run_intent_lab_cad_suite

    intent_dir = output_dir / "intent-lab"
    intent_report = run_intent_lab_cad_suite(
        root=PROJECT_ROOT,
        manifest_path=PROJECT_ROOT / "examples" / "capability_proof" / "intent_lab_manifest.json",
        output_dir=intent_dir,
        no_cad=False,
        driver_factory=lambda: driver,
    )
    intent_subset = [
        row
        for row in intent_report.get("intents", [])
        if row.get("intent") in {"draw_annotation", "modify_object", "delete_object"}
    ]
    summary["intents"] = intent_subset
    if not all(row.get("geometry_verified") for row in intent_subset):
        summary["status"] = "fail"
        _write_json(output_dir / "tablec_final_gap_summary.json", summary)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 1

    summary["verification_no_cad"] = _run_verification_no_cad_api_evidence(output_dir=output_dir, driver=driver)
    summary["status"] = "geometry_verified"
    summary["evidence_state"] = EVIDENCE_READBACK_GEOMETRY_VERIFIED
    summary["geometry_accuracy"] = GEOMETRY_VERIFIED_BY_READBACK
    summary["screenshot_role"] = SCREENSHOT_NOT_APPLICABLE
    _write_json(output_dir / "tablec_final_gap_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
