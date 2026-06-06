"""Deterministic closeout gate for user-visible CAD delivery."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from core.model_review.provider_status import PASS_STATUSES
from core.orchestrator.closeout_state_machine import evaluate_closeout_state
from core.orchestrator.run_package_state import advance_run_state


CLOSEOUT_DECISION_FILE = "closeout_decision.json"
PREVIEW_LAYER = "CODEX_PREVIEW"

_VALIDATION_REPORTS = [
    "cad_reports/validation_report.json",
    "cad_reports/validate_plan_report.json",
    "cad_reports/validate_plan.json",
]
_DRY_RUN_REPORTS = [
    "cad_reports/dry_run_report.json",
    "cad_reports/dry_run_plan.json",
    "cad_reports/dry_run.json",
]
_READBACK_REPORTS = [
    "readback_summary.json",
    "cad_reports/readback_summary.json",
    "cad_reports/execution_summary.json",
]
_VISUAL_ACCEPTANCE_REPORTS = [
    "visual_acceptance_output.json",
    "agent_outputs/visual_acceptance_output.json",
    "agent_outputs/pipeline_visual_acceptance_reviewer.json",
]
_NEIGHBOR_PROTECTION_REPORTS = [
    "cad_reports/neighbor_protection.json",
    "cad_reports/neighbor_protection_gate.json",
]
_DELETE_SCOPE_REPORTS = [
    "cad_reports/delete_scope_gate.json",
]
_ASSET_SOURCE_REPORTS = [
    "cad_reports/asset_source_boundary.json",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _load_first(run_dir: Path, rel_paths: list[str]) -> tuple[dict[str, Any] | None, str | None]:
    for rel_path in rel_paths:
        path = run_dir / rel_path
        if path.is_file():
            return _read_json(path), rel_path
    return None, None


def _status_passes(value: object) -> bool:
    return str(value or "").casefold() in PASS_STATUSES


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _status_from_report(report: dict[str, Any] | None) -> object:
    if not isinstance(report, dict):
        return None
    return report.get("status") or report.get("gateStatus") or report.get("decision")


def _bool_from_report(report: dict[str, Any], *keys: str) -> bool | None:
    for key in keys:
        if key in report:
            value = report.get(key)
            if isinstance(value, bool):
                return value
    return None


def _created_readback_status(report: dict[str, Any]) -> object:
    nested = report.get("createdEntityReadback")
    if isinstance(nested, dict) and nested.get("status") is not None:
        return nested.get("status")
    return (
        report.get("created_handles_readback")
        or report.get("createdHandlesReadback")
        or report.get("readbackStatus")
        or report.get("createdHandleReadback")
        or report.get("status")
    )


def _target_layer(report: dict[str, Any]) -> str:
    return str(report.get("targetLayer") or report.get("target_layer") or "")


def _requested(dispatch: dict[str, Any], contract: dict[str, Any], *keys: str, gate: str) -> bool:
    for key in keys:
        if dispatch.get(key) is True or contract.get(key) is True:
            return True
    for container in [dispatch.get("hardGates"), contract.get("hardGates"), contract.get("requiredGates")]:
        if gate in [str(item) for item in _list(container)]:
            return True
    return False


def _blocking_reason_for_missing_evidence(item: str) -> str:
    mapping = {
        "schemaValid=true when model output is required": "model output schema is not valid",
        "validate_plan=pass": "validate_plan did not pass",
        "dry_run=pass": "dry_run did not pass",
        "created_handles_readback=ok": "created_handles_readback not ok",
        f"targetLayer={PREVIEW_LAYER}": f"targetLayer is not {PREVIEW_LAYER}",
        "savedCurrentDwg=false": "savedCurrentDwg is not false",
        "real CAD geometry verified": "real CAD geometry not verified",
        "visual_acceptance_review=pass": "visual_acceptance_review missing or not pass",
        "neighbor_protection=pass": "neighbor_protection missing or not pass",
    }
    return mapping.get(item, f"{item} missing")


def _blocking_reason_already_present(blocking_reasons: list[str], item: str, reason: str) -> bool:
    if reason in blocking_reasons:
        return True
    prefixes = {
        "schemaValid=true when model output is required": "model output schema",
        "validate_plan=pass": "validate_plan ",
        "dry_run=pass": "dry_run ",
        "created_handles_readback=ok": "created_handles_readback ",
        f"targetLayer={PREVIEW_LAYER}": "targetLayer ",
        "savedCurrentDwg=false": "savedCurrentDwg ",
        "real CAD geometry verified": "real CAD geometry ",
        "visual_acceptance_review=pass": "visual_acceptance_review ",
        "neighbor_protection=pass": "neighbor_protection ",
    }
    prefix = prefixes.get(item)
    return bool(prefix and any(str(value).startswith(prefix) for value in blocking_reasons))


def _screenshot_files(run_dir: Path) -> list[str]:
    screenshot_dir = run_dir / "screenshots"
    if not screenshot_dir.is_dir():
        return []
    return sorted(str(path.relative_to(run_dir)).replace("\\", "/") for path in screenshot_dir.iterdir() if path.is_file())


def build_closeout_decision(run_dir: str | Path) -> dict[str, Any]:
    """Build a closeout decision from an existing run package without writing CAD."""

    run_dir = Path(run_dir)
    dispatch = _read_json(run_dir / "dispatch_plan.json") if (run_dir / "dispatch_plan.json").is_file() else {}
    contract = _read_json(run_dir / "task_contract.json") if (run_dir / "task_contract.json").is_file() else {}
    blocking_reasons: list[str] = []
    required_repairs: list[Any] = []
    checked: list[str] = []
    not_checked: list[str] = []
    input_files: list[str] = ["dispatch_plan.json", "task_contract.json", "state.json"]

    def require_status(label: str, rel_paths: list[str]) -> tuple[dict[str, Any] | None, str | None]:
        report, rel_path = _load_first(run_dir, rel_paths)
        if rel_path:
            input_files.append(rel_path)
        if report is None:
            blocking_reasons.append(f"{label} missing")
            not_checked.append(label)
            return None, None
        if not _status_passes(_status_from_report(report)):
            blocking_reasons.append(f"{label} not pass")
            not_checked.append(label)
            return report, rel_path
        checked.append(f"{label}=pass")
        return report, rel_path

    require_status("validate_plan", _VALIDATION_REPORTS)
    require_status("dry_run", _DRY_RUN_REPORTS)
    readback, readback_path = _load_first(run_dir, _READBACK_REPORTS)
    if readback_path:
        input_files.append(readback_path)
    if readback is None:
        blocking_reasons.append("created_handles_readback missing")
        not_checked.append("created_handles_readback")
        not_checked.append("savedCurrentDwg=false")
        not_checked.append(f"targetLayer={PREVIEW_LAYER}")
    else:
        if not _status_passes(_created_readback_status(readback)):
            blocking_reasons.append("created_handles_readback not ok")
            not_checked.append("created_handles_readback")
        else:
            checked.append("created_handles_readback=ok")
        saved_current_dwg = _bool_from_report(readback, "savedCurrentDwg", "saved_current_dwg")
        if saved_current_dwg is not False:
            blocking_reasons.append("savedCurrentDwg is not false")
            not_checked.append("savedCurrentDwg=false")
        else:
            checked.append("savedCurrentDwg=false")
        target_layer = _target_layer(readback)
        if target_layer != PREVIEW_LAYER:
            blocking_reasons.append(f"targetLayer is not {PREVIEW_LAYER}")
            not_checked.append(f"targetLayer={PREVIEW_LAYER}")
        else:
            checked.append(f"targetLayer={PREVIEW_LAYER}")

    visual, visual_path = _load_first(run_dir, _VISUAL_ACCEPTANCE_REPORTS)
    if visual_path:
        input_files.append(visual_path)
    if visual is None:
        blocking_reasons.append("visual_acceptance_review missing")
        not_checked.append("visual_acceptance_review")
    elif not _status_passes(_status_from_report(visual)):
        blocking_reasons.append("visual_acceptance_review not pass")
        blocking_reasons.extend(str(item) for item in _list(visual.get("blockingReasons")) if str(item))
        required_repairs.extend(_list(visual.get("visualProblems")))
        repair = visual.get("repairRecommendation")
        if isinstance(repair, dict) and repair:
            required_repairs.append(repair)
        not_checked.append("visual_acceptance_review")
    else:
        checked.append("visual_acceptance_review=pass")

    require_status("neighbor_protection", _NEIGHBOR_PROTECTION_REPORTS)
    delete_requested = _requested(
        dispatch,
        contract,
        "hasDeleteOperation",
        "requiresDeleteScopeGate",
        "deleteRequested",
        gate="delete_scope_gate",
    )
    asset_requested = _requested(
        dispatch,
        contract,
        "hasAssetOperation",
        "requiresAssetSourceBoundary",
        "assetRequested",
        gate="asset_source_boundary",
    )
    if delete_requested:
        require_status("delete_scope_gate", _DELETE_SCOPE_REPORTS)
    if asset_requested:
        require_status("asset_source_boundary", _ASSET_SOURCE_REPORTS)

    screenshots = _screenshot_files(run_dir)
    state_machine = evaluate_closeout_state(
        validation_ok="validate_plan=pass" in checked,
        dry_run_ok="dry_run=pass" in checked,
        readback_ok="created_handles_readback=ok" in checked,
        target_layer=_target_layer(readback) if isinstance(readback, dict) else "",
        saved_current_dwg=_bool_from_report(readback, "savedCurrentDwg", "saved_current_dwg") if isinstance(readback, dict) else True,
        driver_mode=str(readback.get("driverMode") or readback.get("driver_mode") or "") if isinstance(readback, dict) else "",
        cadGeometryVerified=readback.get("cadGeometryVerified") if isinstance(readback, dict) else None,
        visual_acceptance_ok="visual_acceptance_review=pass" in checked,
        neighbor_protection_ok="neighbor_protection=pass" in checked,
    )
    for item in [str(value) for value in state_machine.get("missingEvidence", []) if str(value)]:
        reason = _blocking_reason_for_missing_evidence(item)
        if not _blocking_reason_already_present(blocking_reasons, item, reason) and item not in checked:
            blocking_reasons.append(reason)
        if item not in not_checked and item not in checked:
            not_checked.append(item)
    can_deliver = not blocking_reasons and state_machine["state"] == "ready_for_user_review"
    status = "ready_for_delivery" if can_deliver else "not_verified"
    allowed_claims = (
        [
            "closeout gates passed for the recorded run package evidence",
            "visible CAD delivery is ready for user review",
            "savedCurrentDwg=false",
            f"targetLayer={PREVIEW_LAYER}",
        ]
        if can_deliver
        else []
    )
    return {
        "schemaVersion": "closeout-decision/v1",
        "status": status,
        "can_deliver": can_deliver,
        "closeoutState": state_machine["state"],
        "stateMachineVersion": state_machine["stateMachineVersion"],
        "requiredEvidence": state_machine["requiredEvidence"],
        "missingEvidence": state_machine["missingEvidence"],
        "blocking_reasons": blocking_reasons,
        "required_repairs": required_repairs,
        "evidence_boundary": {
            "checked": checked,
            "not_checked": sorted(set(not_checked)),
            "screenshots": {
                "role": "visual_aid_only",
                "count": len(screenshots),
                "files": screenshots,
                "cannotReplace": ["created_handles_readback", "visual_acceptance_review"],
            },
            "notProven": [
                "user acceptance",
                "geometry outside the reported created handles/readback",
                "future edits after this closeout decision",
            ],
        },
        "final_response_allowed_claims": allowed_claims,
        "input_files": sorted(set(input_files)),
        "output_files": [CLOSEOUT_DECISION_FILE],
        "generatedAt": _utc_now(),
        "writer": "core.orchestrator.closeout_gate",
    }


def run_closeout_gate(run_dir: str | Path) -> dict[str, Any]:
    """Write ``closeout_decision.json`` and advance the run package state."""

    run_dir = Path(run_dir)
    decision = build_closeout_decision(run_dir)
    _write_json(run_dir / CLOSEOUT_DECISION_FILE, decision)
    if decision["can_deliver"]:
        advance_run_state(
            run_dir,
            "ready_for_delivery",
            input_files=decision["input_files"],
            output_files=[CLOSEOUT_DECISION_FILE],
        )
    else:
        reason = "; ".join(str(item) for item in decision["blocking_reasons"]) or "closeout not verified"
        advance_run_state(
            run_dir,
            "blocked",
            input_files=decision["input_files"],
            output_files=[CLOSEOUT_DECISION_FILE],
            blocking_reason=reason,
        )
    return decision
