"""RCAD-23: real-CAD smoke evidence for drawing standard beta rows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from core.drawing_standard.drawing_standard_profile import (
    DEFAULT_DRAWING_STANDARD_PROFILE_ID,
    apply_drawing_standard_to_plan,
    load_drawing_standard_profile,
)
from core.execution.execute_plan import execute_plan_file
from core.path_safety import find_project_root, resolve_under_project_output
from core.plan_engine.block_alpha_plan import CONTROLLED_BLOCK_ID, CONTROLLED_BLOCK_NAME
from core.verification.block_alpha_validation import (
    build_block_alpha_no_cad_report,
    build_block_alpha_readback_report,
    validate_block_alpha_report_evidence,
    write_block_alpha_report,
)
from core.verification.drawing_standard_beta_suite import (
    default_suite_path,
    load_drawing_standard_beta_suite,
    run_drawing_standard_beta_suite,
)
from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
    SCREENSHOT_VISUAL_AID_ONLY,
)
from core.verification.inspect_dwg import snapshot_entities_by_handles

RCAD_23_PACKAGE_ID = "RCAD-23-DRAWING-STANDARD-BETA"
V_PROOF_44_PACKAGE_ID = "V-PROOF-44-DRAWING-STANDARD-ROWS"
DRAWING_STANDARD_SUITE_CAPABILITY_ID = "drawing_standard.beta.drawing_standard_beta_04"
DRAWING_STANDARD_BLOCK_CASE_ID = "block_insert_plan_resolution"
DRAWING_STANDARD_BLOCK_CASE_CAPABILITY_ID = "drawing_standard.beta.block_insert_plan_resolution"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _case_by_id(suite: dict[str, Any], case_id: str) -> dict[str, Any]:
    for case in suite.get("cases", []):
        if isinstance(case, dict) and case.get("case_id") == case_id:
            return case
    raise ValueError(f"drawing standard suite missing case: {case_id}")


def materialize_drawing_standard_block_plan(*, root: Path) -> dict[str, Any]:
    suite = load_drawing_standard_beta_suite(default_suite_path(root))
    case = _case_by_id(suite, DRAWING_STANDARD_BLOCK_CASE_ID)
    placement = case.get("placement", {})
    if not isinstance(placement, dict):
        raise ValueError("block_insert_plan_resolution placement must be an object")
    profile_id = str(suite.get("profile_id", DEFAULT_DRAWING_STANDARD_PROFILE_ID))
    profile = load_drawing_standard_profile(profile_id)
    plan = {
        "version": "0.1",
        "domain": "generic",
        "intent": "insert_block_alpha",
        "object": {
            "type": "block_reference",
            "name": "Controlled Test Block",
            "block_id": CONTROLLED_BLOCK_ID,
            "cad_identity": {"block_name": CONTROLLED_BLOCK_NAME},
        },
        "placement": {
            "mode": "absolute",
            "base_point": placement.get("base_point", [1800, 900, 0]),
            "rotation": placement.get("rotation", 0),
            "scale": placement.get("scale", [1, 1, 1]),
        },
        "drawing": {},
        "confidence": 1.0,
        "needs_confirmation": False,
        "drawing_standard_profile_id": profile_id,
    }
    apply_drawing_standard_to_plan(plan, profile=profile, object_role=str(case.get("object_role", "block_insert")))
    return plan


def build_drawing_standard_cad_smoke_report(
    *,
    suite_result: dict[str, Any],
    block_alpha_report: dict[str, Any],
    plan_path: Path,
    execution_summary: dict[str, Any] | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    block_case = _case_by_id(suite_result, DRAWING_STANDARD_BLOCK_CASE_ID)
    if block_case.get("status") != "pass":
        raise ValueError("drawing standard block_insert_plan_resolution case must pass before CAD smoke")
    block_alpha_error = validate_block_alpha_report_evidence(
        block_alpha_report,
        no_cad=block_alpha_report.get("status") == "deferred",
    )
    geometry_verified = (
        block_alpha_report.get("status") == "geometry_verified"
        and block_alpha_report.get("evidence_state") == EVIDENCE_READBACK_GEOMETRY_VERIFIED
        and not block_alpha_error
    )
    status = "geometry_verified" if geometry_verified else str(block_alpha_report.get("status", "failed"))
    if status not in {"geometry_verified", "deferred"}:
        status = "failed"

    non_cad_cases = []
    for case in suite_result.get("cases", []):
        if not isinstance(case, dict) or case.get("case_id") == DRAWING_STANDARD_BLOCK_CASE_ID:
            continue
        non_cad_cases.append(
            {
                "case_id": case.get("case_id"),
                "status": case.get("status"),
                "geometry_verified": False,
                "upgrade_scope": "not_upgraded_by_rcad_23",
            }
        )

    verified_capability_ids = []
    if geometry_verified:
        verified_capability_ids = [
            DRAWING_STANDARD_SUITE_CAPABILITY_ID,
            DRAWING_STANDARD_BLOCK_CASE_CAPABILITY_ID,
        ]

    return {
        "version": "0.1",
        "package_id": RCAD_23_PACKAGE_ID,
        "paired_package_id": V_PROOF_44_PACKAGE_ID,
        "status": status,
        "evidence_state": (
            EVIDENCE_READBACK_GEOMETRY_VERIFIED if geometry_verified else EVIDENCE_DEFERRED_CAD_READBACK
        ),
        "geometry_accuracy": GEOMETRY_VERIFIED_BY_READBACK if geometry_verified else NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": (
            block_alpha_report.get("screenshot_role")
            or (SCREENSHOT_VISUAL_AID_ONLY if geometry_verified else SCREENSHOT_NOT_APPLICABLE)
        ),
        "suite_id": suite_result.get("suite_id"),
        "profile_id": suite_result.get("profile_id"),
        "block_case_id": DRAWING_STANDARD_BLOCK_CASE_ID,
        "plan_path": str(plan_path),
        "geometry_verified": geometry_verified,
        "verified_capability_ids": verified_capability_ids,
        "non_cad_cases_not_upgraded": non_cad_cases,
        "created_handles": block_alpha_report.get("created_handles", []),
        "block_alpha_report": str(output_dir / "block_alpha_report.json") if output_dir else "",
        "execution_summary": execution_summary or {},
        "checks": [
            {
                "name": "drawing_standard_beta_suite",
                "status": "pass" if suite_result.get("status") == "pass" else "fail",
                "message": "drawing standard beta suite passed before CAD smoke.",
            },
            {
                "name": "block_insert_plan_resolution_readback",
                "status": "pass" if geometry_verified else "not_run" if status == "deferred" else "fail",
                "message": (
                    "styled insert_block_alpha plan created a scoped block_reference readback."
                    if geometry_verified
                    else block_alpha_error or "real CAD readback deferred."
                ),
            },
        ],
        "limitations": [
            "RCAD-23 upgrades only the drawing standard suite row and block_insert_plan_resolution row.",
            "Object role, primitive style, and semantic layer cases remain non-CAD evidence until separately verified.",
        ],
    }


def run_drawing_standard_cad_smoke(
    *,
    output_dir: Path,
    root: Path | None = None,
    no_cad: bool = False,
    driver_factory: Callable[[], Any] | None = None,
) -> dict[str, Any]:
    root = (root or find_project_root(Path(__file__))).resolve()
    output_dir = resolve_under_project_output(root, output_dir, label="output_dir")
    suite_result = run_drawing_standard_beta_suite(
        default_suite_path(root),
        output_root=output_dir / "drawing_standard_no_cad",
    )
    if suite_result.get("status") != "pass":
        raise ValueError("drawing standard beta suite must pass before CAD smoke")

    plan = materialize_drawing_standard_block_plan(root=root)
    plan_path = output_dir / "drawing_standard_block_insert_plan.json"
    _write_json(plan_path, plan)

    if no_cad:
        execution_summary: dict[str, Any] | None = None
        block_alpha_report = build_block_alpha_no_cad_report(plan_path=plan_path)
    else:
        if driver_factory is None:
            from core.cad_io.autocad_com import AutoCADComDriver

            driver_factory = lambda: AutoCADComDriver(connect_existing_only=True)
        driver = driver_factory()
        execution_summary = execute_plan_file(plan_path, driver=driver, preview_only=True)
        _write_json(output_dir / "block_insert_execution_summary.json", execution_summary)
        created_handles = [
            str(handle).strip()
            for handle in execution_summary.get("created_handles", [])
            if str(handle).strip()
        ]
        entities = snapshot_entities_by_handles(driver, created_handles, layer="CODEX_PREVIEW")
        block_alpha_report = build_block_alpha_readback_report(
            plan_path=plan_path,
            entities=entities,
            created_handles=created_handles,
        )

    write_block_alpha_report(output_dir / "block_alpha_report.json", block_alpha_report)
    report = build_drawing_standard_cad_smoke_report(
        suite_result=suite_result,
        block_alpha_report=block_alpha_report,
        plan_path=plan_path,
        execution_summary=execution_summary,
        output_dir=output_dir,
    )
    _write_json(output_dir / "drawing_standard_cad_smoke_report.json", report)
    return report
