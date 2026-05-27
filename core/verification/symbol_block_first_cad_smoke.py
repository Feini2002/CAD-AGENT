"""RCAD-25: real-CAD smoke evidence for SYMBOL-09 block-first selection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from core.execution.execute_plan import execute_plan_file
from core.path_safety import find_project_root, resolve_under_project_output, resolve_under_project_root
from core.symbol_engine.block_first_boundary import (
    SYMBOL_09_SUITE_CAPABILITY_ID,
    capability_id_for_block_first_case,
)
from core.symbol_engine.block_first_tier import default_manifest_path, run_block_first_tier_smoke
from core.verification.block_alpha_validation import (
    build_block_alpha_no_cad_report,
    build_block_alpha_readback_report,
    default_block_alpha_plan_path,
    validate_block_alpha_report_evidence,
    write_block_alpha_report,
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

BLOCK_FIRST_VERIFIED_CASE_ID = "controlled-block-wins"
RCAD_25_PACKAGE_ID = "RCAD-25-SYMBOL-BLOCK-FIRST"
V_PROOF_34_PACKAGE_ID = "V-PROOF-34-BLOCK-FIRST-ROW"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _case_by_id(smoke: dict[str, Any], case_id: str) -> dict[str, Any]:
    for case in smoke.get("cases", []):
        if isinstance(case, dict) and case.get("case_id") == case_id:
            return case
    raise ValueError(f"block-first smoke missing case: {case_id}")


def _assert_controlled_block_case(smoke: dict[str, Any]) -> dict[str, Any]:
    case = _case_by_id(smoke, BLOCK_FIRST_VERIFIED_CASE_ID)
    if case.get("status") != "pass":
        raise ValueError(f"{BLOCK_FIRST_VERIFIED_CASE_ID} did not pass block-first smoke")
    if case.get("selected_render_path") != "block":
        raise ValueError(f"{BLOCK_FIRST_VERIFIED_CASE_ID} did not select block render path")
    if case.get("selected_cad_intent") != "insert_block_alpha":
        raise ValueError(f"{BLOCK_FIRST_VERIFIED_CASE_ID} did not select insert_block_alpha")
    return case


def build_symbol_block_first_cad_smoke_report(
    *,
    block_first_smoke: dict[str, Any],
    block_alpha_report: dict[str, Any],
    plan_path: Path,
    execution_summary: dict[str, Any] | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Combine no-CAD block-first selection and block-alpha CAD readback evidence."""

    controlled_case = _assert_controlled_block_case(block_first_smoke)
    block_alpha_validation_error = validate_block_alpha_report_evidence(
        block_alpha_report,
        no_cad=block_alpha_report.get("status") == "deferred",
    )
    geometry_verified = (
        block_alpha_report.get("status") == "geometry_verified"
        and block_alpha_report.get("evidence_state") == EVIDENCE_READBACK_GEOMETRY_VERIFIED
        and not block_alpha_validation_error
    )
    status = "geometry_verified" if geometry_verified else str(block_alpha_report.get("status", "failed"))
    if status not in {"geometry_verified", "deferred"}:
        status = "failed"

    verified_ids = []
    if geometry_verified:
        verified_ids = [
            SYMBOL_09_SUITE_CAPABILITY_ID,
            capability_id_for_block_first_case(BLOCK_FIRST_VERIFIED_CASE_ID),
        ]

    fallback_cases = []
    for case in block_first_smoke.get("cases", []):
        if not isinstance(case, dict) or case.get("case_id") == BLOCK_FIRST_VERIFIED_CASE_ID:
            continue
        fallback_cases.append(
            {
                "case_id": case.get("case_id"),
                "selected_render_path": case.get("selected_render_path"),
                "selected_cad_intent": case.get("selected_cad_intent"),
                "geometry_verified": False,
                "upgrade_scope": "not_upgraded_by_rcad_25",
            }
        )

    report = {
        "version": "0.1",
        "package_id": RCAD_25_PACKAGE_ID,
        "paired_package_id": V_PROOF_34_PACKAGE_ID,
        "status": status,
        "evidence_state": (
            EVIDENCE_READBACK_GEOMETRY_VERIFIED if geometry_verified else EVIDENCE_DEFERRED_CAD_READBACK
        ),
        "geometry_accuracy": GEOMETRY_VERIFIED_BY_READBACK if geometry_verified else NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": (
            block_alpha_report.get("screenshot_role")
            or (SCREENSHOT_VISUAL_AID_ONLY if geometry_verified else SCREENSHOT_NOT_APPLICABLE)
        ),
        "plan_path": str(plan_path),
        "block_first_case_id": BLOCK_FIRST_VERIFIED_CASE_ID,
        "selected_render_path": controlled_case.get("selected_render_path"),
        "selected_cad_intent": controlled_case.get("selected_cad_intent"),
        "geometry_verified": geometry_verified,
        "verified_capability_ids": verified_ids,
        "fallback_cases_not_upgraded": fallback_cases,
        "created_handles": block_alpha_report.get("created_handles", []),
        "block_alpha_report": str(output_dir / "block_alpha_report.json") if output_dir else "",
        "execution_summary": execution_summary or {},
        "checks": [
            {
                "name": "block_first_selected_insert_block_alpha",
                "status": "pass",
                "message": "controlled-block-wins selected block render path and insert_block_alpha intent.",
            },
            {
                "name": "block_alpha_readback_geometry",
                "status": "pass" if geometry_verified else "not_run" if status == "deferred" else "fail",
                "message": (
                    "insert_block_alpha created handle was read back as expected block_reference."
                    if geometry_verified
                    else block_alpha_validation_error or "real CAD readback deferred."
                ),
            },
        ],
        "limitations": [
            "RCAD-25 upgrades only the SYMBOL-09 suite row and controlled-block-wins row.",
            "Glyph fallback cases remain non-CAD smoke rows until separately verified.",
        ],
    }
    return report


def run_symbol_block_first_cad_smoke(
    *,
    output_dir: Path,
    root: Path | None = None,
    no_cad: bool = False,
    plan_path: Path | None = None,
    driver_factory: Callable[[], Any] | None = None,
) -> dict[str, Any]:
    root = (root or find_project_root(Path(__file__))).resolve()
    output_dir = resolve_under_project_output(root, output_dir, label="output_dir")
    plan_path = resolve_under_project_root(root, plan_path or default_block_alpha_plan_path(root), label="plan")

    smoke_output = output_dir / "block_first_no_cad"
    block_first_smoke = run_block_first_tier_smoke(default_manifest_path(root), output_root=smoke_output)
    _assert_controlled_block_case(block_first_smoke)

    if no_cad:
        block_alpha_report = build_block_alpha_no_cad_report(plan_path=plan_path)
        execution_summary: dict[str, Any] | None = None
    else:
        if driver_factory is None:
            from core.cad_io.autocad_com import AutoCADComDriver

            driver_factory = lambda: AutoCADComDriver(connect_existing_only=True)
        driver = driver_factory()
        execution_summary = execute_plan_file(plan_path, driver=driver, preview_only=True)
        _write_json(output_dir / "block_alpha_execution_summary.json", execution_summary)
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
    report = build_symbol_block_first_cad_smoke_report(
        block_first_smoke=block_first_smoke,
        block_alpha_report=block_alpha_report,
        plan_path=plan_path,
        execution_summary=execution_summary,
        output_dir=output_dir,
    )
    _write_json(output_dir / "symbol_block_first_cad_smoke_report.json", report)
    return report
