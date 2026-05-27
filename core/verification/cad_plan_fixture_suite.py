"""Validate, dry-run and optionally execute regression CAD_PLAN fixtures."""

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
from core.verification.preview_only_audit import attach_preview_only_audit, build_preview_only_audit


DEFAULT_FIXTURE_MANIFEST_RELATIVE_PATH = Path("examples") / "cad_regression" / "cad_plan_fixture_manifest.json"


def load_cad_plan_fixture_manifest(path: Path) -> dict[str, Any]:
    manifest = load_json(path)
    if manifest.get("version") != "0.1":
        raise ValueError("cad_plan_fixture_manifest version must be '0.1'.")
    if manifest.get("suite_id") != "cad_plan_fixture_suite":
        raise ValueError("cad_plan_fixture_manifest suite_id must be 'cad_plan_fixture_suite'.")
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        raise ValueError("cad_plan_fixture_manifest requires a non-empty fixtures array.")
    for index, fixture in enumerate(fixtures):
        if not isinstance(fixture, dict):
            raise ValueError(f"fixtures[{index}] must be an object.")
        for key in ("id", "title", "plan_path"):
            if key not in fixture:
                raise ValueError(f"fixtures[{index}] missing required field: {key}")
    return manifest


def _resolve_plan_path(root: Path, plan_path: str) -> Path:
    path = Path(plan_path)
    return path if path.is_absolute() else (root / path).resolve()


def _run_fixture_no_cad(*, plan_path: Path) -> dict[str, Any]:
    errors = validate_plan(load_json(plan_path))
    dry_run = create_dry_run_report(plan_path)
    return {
        "validate_errors": errors,
        "validate_status": "pass" if not errors else "fail",
        "dry_run_status": str(dry_run.get("status", "")),
        "dry_run_evidence_state": str(dry_run.get("evidence_state", "")),
    }


def _run_fixture_cad(*, plan_path: Path, driver: Any) -> dict[str, Any]:
    summary = execute_plan_file(plan_path, driver=driver, preview_only=True, allow_unconfirmed=True)
    attach_preview_only_audit(summary, layer=str(summary.get("layer", "CODEX_PREVIEW")))
    created_handles = summary.get("created_handles", [])
    handle_count = len(created_handles) if isinstance(created_handles, list) else 0
    return {
        "cad_execution_status": "executed" if summary.get("status") == "executed" and handle_count > 0 else "fail",
        "created_handle_count": handle_count,
        "execution_summary": summary,
    }


def run_cad_plan_fixture_suite(
    *,
    root: Path,
    manifest_path: Path | None = None,
    output_dir: Path | None = None,
    no_cad: bool = False,
    driver_factory: Callable[[], Any] | None = None,
) -> dict[str, Any]:
    manifest_path = manifest_path or (root / DEFAULT_FIXTURE_MANIFEST_RELATIVE_PATH)
    manifest = load_cad_plan_fixture_manifest(manifest_path)
    fixture_results: list[dict[str, Any]] = []
    cad_execution_results: list[dict[str, Any]] = []
    driver = None if no_cad or driver_factory is None else driver_factory()

    for fixture in manifest["fixtures"]:
        plan_path = _resolve_plan_path(root, str(fixture["plan_path"]))
        result: dict[str, Any] = {
            "id": fixture["id"],
            "title": fixture["title"],
            "plan_path": str(plan_path),
        }
        no_cad_result = _run_fixture_no_cad(plan_path=plan_path)
        result.update(no_cad_result)
        if no_cad:
            result["cad_execution_status"] = "deferred"
            result["geometry_verified"] = False
            result["evidence_state"] = EVIDENCE_DEFERRED_CAD_READBACK
        elif fixture.get("cad_execution", True):
            if driver is None:
                result["cad_execution_status"] = "blocked"
                result["geometry_verified"] = False
                result["evidence_state"] = EVIDENCE_DEFERRED_CAD_READBACK
            else:
                result.update(_run_fixture_cad(plan_path=plan_path, driver=driver))
                executed = result.get("cad_execution_status") == "executed"
                result["geometry_verified"] = executed
                result["evidence_state"] = (
                    EVIDENCE_READBACK_GEOMETRY_VERIFIED if executed else EVIDENCE_DEFERRED_CAD_READBACK
                )
        else:
            result["cad_execution_status"] = "skipped"
            result["geometry_verified"] = False
            result["evidence_state"] = EVIDENCE_DEFERRED_CAD_READBACK

        fixture_pass = result["validate_status"] == "pass" and result["dry_run_status"] == "valid"
        if not no_cad and fixture.get("cad_execution", True):
            fixture_pass = fixture_pass and result.get("cad_execution_status") == "executed"
        result["status"] = "pass" if fixture_pass else "fail"
        fixture_results.append(result)
        if fixture.get("cad_execution", True):
            cad_execution_results.append(result)

    passed = sum(1 for item in fixture_results if item["status"] == "pass")
    cad_geometry_verified = (
        not no_cad
        and bool(cad_execution_results)
        and all(item.get("geometry_verified") for item in cad_execution_results)
    )
    suite_pass = passed == len(fixture_results)
    report = {
        "version": "0.1",
        "suite_id": "cad_plan_fixture_suite",
        "status": "pass" if suite_pass else "fail",
        "no_cad": no_cad,
        "fixture_count": len(fixture_results),
        "passed_fixture_count": passed,
        "cad_executable_fixture_count": len(cad_execution_results),
        "geometry_verified_fixture_count": sum(1 for item in fixture_results if item.get("geometry_verified")),
        "safety": build_preview_only_audit(),
        "fixtures": fixture_results,
    }
    if no_cad:
        report["evidence_state"] = EVIDENCE_DEFERRED_CAD_READBACK
        report["geometry_accuracy"] = NON_CAD_GEOMETRY_ACCURACY
        report["screenshot_role"] = SCREENSHOT_NOT_APPLICABLE
    elif suite_pass and cad_geometry_verified:
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
        (output_dir / "cad_plan_fixture_suite_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return report
