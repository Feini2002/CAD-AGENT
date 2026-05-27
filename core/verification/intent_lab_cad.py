"""Execute intent_lab CAD_PLAN rows on CODEX_PREVIEW (V-PROOF-14 / V-PROOF-15)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from core.execution.execute_plan import execute_plan_file
from core.plan_engine.dry_run_report import create_dry_run_report
from core.plan_engine.validate_plan import load_json, validate_plan
from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)
from core.path_safety import resolve_under_project_output, resolve_under_project_root
from core.verification.intent_lab import DEFAULT_INTENT_LAB_MANIFEST, load_intent_lab_manifest
from core.verification.preview_only_audit import attach_preview_only_audit, build_preview_only_audit


def _resolve_plan_path(root: Path, plan_path: str) -> Path:
    return resolve_under_project_root(root, Path(plan_path), label="plan_path")


def _run_intent_no_cad(*, plan_path: Path) -> dict[str, Any]:
    plan = load_json(plan_path)
    errors = validate_plan(plan)
    intent = str(plan.get("intent", ""))
    if intent in {"draw_object", "draw_symbol_glyph", "insert_block_alpha"}:
        dry_run = create_dry_run_report(plan_path)
        dry_run_status = str(dry_run.get("status", ""))
    else:
        dry_run_status = "valid"
    return {
        "validate_errors": errors,
        "validate_status": "pass" if not errors else "fail",
        "dry_run_status": dry_run_status,
    }


def _run_intent_cad(*, plan_path: Path, driver: Any) -> dict[str, Any]:
    summary = execute_plan_file(plan_path, driver=driver, preview_only=True, allow_unconfirmed=True)
    attach_preview_only_audit(summary, layer=str(summary.get("layer", "CODEX_PREVIEW")))
    created_handles = summary.get("created_handles", [])
    handle_count = len(created_handles) if isinstance(created_handles, list) else 0
    return {
        "cad_execution_status": "executed" if summary.get("status") == "executed" and handle_count > 0 else "fail",
        "created_handle_count": handle_count,
        "execution_summary": summary,
    }


def run_intent_lab_cad_suite(
    *,
    root: Path,
    manifest_path: Path | None = None,
    output_dir: Path | None = None,
    no_cad: bool = False,
    driver_factory: Callable[[], Any] | None = None,
) -> dict[str, Any]:
    manifest_path = manifest_path or (root / DEFAULT_INTENT_LAB_MANIFEST)
    manifest = load_intent_lab_manifest(manifest_path)
    if output_dir is not None:
        output_dir = resolve_under_project_output(root, output_dir, label="output_dir")
        output_dir.mkdir(parents=True, exist_ok=True)
    driver = None if no_cad or driver_factory is None else driver_factory()
    intent_results: list[dict[str, Any]] = []
    cad_execution_results: list[dict[str, Any]] = []

    for item in manifest["intents"]:
        plan_path = _resolve_plan_path(root, str(item["plan_path"]))
        result: dict[str, Any] = {
            "intent": item["intent"],
            "registry_capability_id": item.get("registry_capability_id"),
            "plan_path": str(plan_path),
        }
        result.update(_run_intent_no_cad(plan_path=plan_path))
        if no_cad or not item.get("cad_execution", False):
            result["cad_execution_status"] = "deferred" if no_cad else "skipped"
            result["geometry_verified"] = False
            result["evidence_state"] = EVIDENCE_DEFERRED_CAD_READBACK
            result["deferred_reason"] = item.get("deferred_reason") if not item.get("cad_execution", False) else ""
        elif driver is None:
            result["cad_execution_status"] = "blocked"
            result["geometry_verified"] = False
            result["evidence_state"] = EVIDENCE_DEFERRED_CAD_READBACK
        else:
            result.update(_run_intent_cad(plan_path=plan_path, driver=driver))
            executed = result.get("cad_execution_status") == "executed"
            result["geometry_verified"] = executed
            result["evidence_state"] = (
                EVIDENCE_READBACK_GEOMETRY_VERIFIED if executed else EVIDENCE_DEFERRED_CAD_READBACK
            )
            if executed:
                cad_execution_results.append(result)

        fixture_pass = result["validate_status"] == "pass" and result["dry_run_status"] == "valid"
        if item.get("cad_execution", False) and not no_cad:
            fixture_pass = fixture_pass and result.get("cad_execution_status") == "executed"
        result["status"] = "pass" if fixture_pass else "fail"
        intent_results.append(result)
        if output_dir is not None and result.get("geometry_verified"):
            per_intent_report = {
                "version": "0.1",
                "suite_id": f"intent_lab_cad_{result['intent']}",
                "intent": result["intent"],
                "registry_capability_id": result.get("registry_capability_id"),
                "status": "geometry_verified",
                "geometry_verified": True,
                "evidence_state": EVIDENCE_READBACK_GEOMETRY_VERIFIED,
                "geometry_accuracy": GEOMETRY_VERIFIED_BY_READBACK,
                "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
                "created_handle_count": result.get("created_handle_count", 0),
                "execution_summary": result.get("execution_summary"),
            }
            (output_dir / f"intent_{result['intent']}_cad_report.json").write_text(
                json.dumps(per_intent_report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    passed = sum(1 for row in intent_results if row["status"] == "pass")
    cad_geometry_verified = (
        not no_cad
        and bool(cad_execution_results)
        and all(row.get("geometry_verified") for row in cad_execution_results)
    )
    report = {
        "version": "0.1",
        "suite_id": "intent_lab_cad",
        "status": "pass" if passed == len(intent_results) else "fail",
        "no_cad": no_cad,
        "intent_count": len(intent_results),
        "passed_intent_count": passed,
        "cad_executable_intent_count": len(cad_execution_results),
        "safety": build_preview_only_audit(),
        "intents": intent_results,
    }
    if no_cad:
        report["evidence_state"] = EVIDENCE_DEFERRED_CAD_READBACK
        report["geometry_accuracy"] = NON_CAD_GEOMETRY_ACCURACY
        report["screenshot_role"] = SCREENSHOT_NOT_APPLICABLE
        report["geometry_verified"] = False
    elif passed == len(intent_results) and cad_geometry_verified:
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
        (output_dir / "intent_lab_cad_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return report
