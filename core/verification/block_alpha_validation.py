"""Block alpha validation evidence for CAD validation runner."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.plan_engine.validate_plan import load_json, validate_plan
from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
    SCREENSHOT_VISUAL_AID_ONLY,
)
from core.verification.block_attribute_probe import check_block_attribute_readback, merge_block_readback_checks
from core.verification.geometry_checks import check_block_reference_readback


BLOCK_ALPHA_PLAN_REL = "examples/plans/insert_block_alpha_test.json"
REQUIRED_BLOCK_ALPHA_ENTITY_FIELDS = (
    "block_name",
    "insertion_point",
    "rotation",
    "scale",
    "layer",
    "bbox",
)


def default_block_alpha_plan_path(root: Path) -> Path:
    return root / BLOCK_ALPHA_PLAN_REL


def build_block_alpha_no_cad_report(*, plan_path: Path) -> dict[str, Any]:
    return {
        "version": "0.1",
        "status": "deferred",
        "intent": "insert_block_alpha",
        "plan_path": str(plan_path),
        "evidence_state": EVIDENCE_DEFERRED_CAD_READBACK,
        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
        "checks": [
            {
                "name": "real_cad_block_readback",
                "status": "not_run",
                "message": "no-cad validation run; block insertion readback deferred",
            },
            {
                "name": "block_alpha_geometry_verified",
                "status": "not_run",
                "message": "must not claim geometry_verified without real CAD block_reference readback",
            },
        ],
        "limitations": [
            "Block alpha geometry requires real AutoCAD insert_block_alpha execution and created-handle readback.",
        ],
        "requires_real_cad": ["insert_block_alpha execution", "block_reference readback"],
    }


def build_block_alpha_readback_report(
    *,
    plan_path: Path,
    entities: list[dict[str, Any]],
    created_handles: list[str] | None = None,
    screenshot_path: Path | str | None = None,
) -> dict[str, Any]:
    plan = load_json(plan_path)
    errors = validate_plan(plan)
    if errors:
        return {
            "version": "0.1",
            "status": "failed",
            "intent": "insert_block_alpha",
            "plan_path": str(plan_path),
            "evidence_state": EVIDENCE_DEFERRED_CAD_READBACK,
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
            "validation_errors": errors,
            "checks": [{"name": "cad_plan", "status": "fail", "message": "; ".join(errors)}],
        }

    normalized_handles = [str(handle).strip() for handle in (created_handles or []) if str(handle).strip()]
    if not normalized_handles:
        return {
            "version": "0.1",
            "status": "failed",
            "intent": "insert_block_alpha",
            "plan_path": str(plan_path),
            "evidence_state": EVIDENCE_DEFERRED_CAD_READBACK,
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
            "checks": [
                {
                    "name": "created_handles_scope",
                    "status": "fail",
                    "failure_category": "readback_missing",
                    "message": "block alpha CAD readback requires non-empty created_handles from execute_plan",
                }
            ],
            "created_handles": [],
        }

    handle_set = set(normalized_handles)
    scoped = [entity for entity in entities if str(entity.get("handle")) in handle_set]

    if not scoped:
        return {
            "version": "0.1",
            "status": "failed",
            "intent": "insert_block_alpha",
            "plan_path": str(plan_path),
            "evidence_state": EVIDENCE_DEFERRED_CAD_READBACK,
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
            "checks": [
                {
                    "name": "block_reference_readback",
                    "status": "fail",
                    "failure_category": "readback_missing",
                    "message": "no block_reference entities read back for created handles",
                }
            ],
            "created_handles": normalized_handles,
        }

    entity = scoped[0]
    geometry_checks = check_block_reference_readback(plan, entity)
    entity_handles = {str(item.get("handle")) for item in scoped if item.get("handle")}
    scope_ok = bool(handle_set) and handle_set <= entity_handles
    geometry_checks.insert(
        0,
        {
            "name": "created_handles_scope",
            "status": "pass" if scope_ok else "fail",
            "message": "Readback covers created handles." if scope_ok else f"expected {sorted(handle_set)}, got {sorted(entity_handles)}",
            **({"failure_category": "readback_missing"} if not scope_ok else {}),
        },
    )

    attribute_assessment = check_block_attribute_readback(plan, entity)
    checks, geometry_verified, _evidence_override = merge_block_readback_checks(
        geometry_checks,
        attribute_assessment,
    )
    if not scope_ok:
        geometry_verified = False

    screenshot = Path(screenshot_path) if screenshot_path is not None else None
    screenshot_valid = screenshot is not None and screenshot.exists()
    report = {
        "version": "0.1",
        "status": "geometry_verified" if geometry_verified else "failed",
        "intent": "insert_block_alpha",
        "plan_path": str(plan_path),
        "evidence_state": EVIDENCE_READBACK_GEOMETRY_VERIFIED if geometry_verified else EVIDENCE_DEFERRED_CAD_READBACK,
        "geometry_accuracy": GEOMETRY_VERIFIED_BY_READBACK if geometry_verified else NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": SCREENSHOT_VISUAL_AID_ONLY if screenshot_valid else SCREENSHOT_NOT_APPLICABLE,
        "checks": checks,
        "created_handles": normalized_handles,
        "entity": entity,
        "attribute_readback": attribute_assessment,
        "evidence": {"screenshot": str(screenshot) if screenshot_valid else ""},
    }
    return report


def validate_block_alpha_report_evidence(report: dict[str, Any], *, no_cad: bool) -> str:
    if not isinstance(report, dict):
        return "block_alpha_report must be a JSON object."

    evidence_state = report.get("evidence_state")
    geometry_accuracy = report.get("geometry_accuracy")
    status = report.get("status")

    if no_cad:
        if status == "geometry_verified":
            return "block_alpha_report must not claim geometry_verified on no-cad runs"
        if status != "deferred":
            return "block_alpha_report no-cad evidence requires status='deferred'"
        if evidence_state != EVIDENCE_DEFERRED_CAD_READBACK:
            return f"block_alpha_report.evidence_state={evidence_state!r}; expected {EVIDENCE_DEFERRED_CAD_READBACK!r}"
        if geometry_accuracy != NON_CAD_GEOMETRY_ACCURACY:
            return f"block_alpha_report.geometry_accuracy={geometry_accuracy!r}; expected non-CAD accuracy marker"
        return ""

    if status == "geometry_verified":
        if evidence_state != EVIDENCE_READBACK_GEOMETRY_VERIFIED:
            return "block_alpha_report geometry_verified requires readback_geometry_verified evidence_state"
        if geometry_accuracy != GEOMETRY_VERIFIED_BY_READBACK:
            return "block_alpha_report geometry_verified requires verified_by_cad_readback geometry_accuracy"
        checks = report.get("checks", [])
        if not isinstance(checks, list) or not checks or any(not isinstance(check, dict) or check.get("status") != "pass" for check in checks):
            return "block_alpha_report geometry_verified requires all checks pass"
        if not any(
            isinstance(check, dict) and check.get("name") == "created_handles_scope" and check.get("status") == "pass"
            for check in checks
        ):
            return "block_alpha_report geometry_verified requires created_handles_scope pass check"
        created_handles = report.get("created_handles")
        if not isinstance(created_handles, list) or not created_handles:
            return "block_alpha_report geometry_verified requires non-empty created_handles"
        handle_set = {str(handle) for handle in created_handles if str(handle)}
        if len(handle_set) != 1:
            return "block_alpha_report geometry_verified requires exactly one block_reference created_handle"
        entity = report.get("entity")
        if not isinstance(entity, dict):
            return "block_alpha_report geometry_verified requires entity readback payload"
        if entity.get("type") != "block_reference":
            return "block_alpha_report geometry_verified requires entity.type=block_reference"
        if str(entity.get("handle", "")) not in handle_set:
            return "block_alpha_report geometry_verified entity.handle must be in created_handles"
        for field in REQUIRED_BLOCK_ALPHA_ENTITY_FIELDS:
            if field not in entity:
                return f"block_alpha_report geometry_verified requires entity.{field}"
        return ""

    if status == "deferred":
        if evidence_state != EVIDENCE_DEFERRED_CAD_READBACK:
            return f"block_alpha_report deferred run has unexpected evidence_state={evidence_state!r}"
        return ""

    return ""


def write_block_alpha_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def summarize_block_alpha_from_steps(steps: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {step["id"]: step for step in steps}
    deferred = by_id.get("block_alpha_deferred_evidence")
    readback = by_id.get("block_alpha_readback")
    source = readback or deferred
    geometry_verified = False
    evidence_state = EVIDENCE_DEFERRED_CAD_READBACK
    if source and source.get("status") == "pass":
        evidence_state = str(source.get("evidence_state") or evidence_state)
        geometry_verified = evidence_state == EVIDENCE_READBACK_GEOMETRY_VERIFIED
    return {
        "geometry_verified": geometry_verified,
        "evidence_state": evidence_state,
        "step_id": source.get("id") if source else "",
    }
