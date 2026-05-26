"""Build machine-readable route audit reports for Core Orchestrator decisions."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from core.orchestrator.scene_registry import DEFAULT_SCENE_ID, get_scene

_DISPATCH_READY = "ready"
_DISPATCH_DEFERRED = "deferred"


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MATURITY_NOT_CLAIMABLE: dict[str, list[str]] = {
    "core_only": ["scene_module_preferences", "scene_product_delivery"],
    "scene_alpha": ["scene_product_delivery", "scene_beta_object_system"],
    "scene_beta": ["scene_product_delivery"],
    "scaffold": ["scene_product_delivery", "real_cad_scene_product_smoke"],
    "scene_product": [],
}


def _orchestrator_status(gate: dict[str, Any], dispatch: dict[str, Any], may_execute: bool) -> str:
    if gate.get("status") != "ready":
        return str(gate.get("status", "blocked"))
    if dispatch.get("status") != _DISPATCH_READY:
        return str(dispatch.get("status", "deferred"))
    if may_execute:
        return "ready"
    return "blocked"


def _geometry_verified(execution: dict[str, Any] | None) -> bool:
    if not isinstance(execution, dict):
        return False
    if execution.get("geometry_verified") is True:
        return True
    readback = execution.get("readback") or execution.get("cad_readback")
    return isinstance(readback, dict) and readback.get("geometry_verified") is True


def _collect_evidence(
    *,
    request_context: dict[str, Any],
    orchestration: dict[str, Any],
    scene_record: dict[str, Any] | None,
    dispatch: dict[str, Any],
) -> tuple[list[str], list[str], list[str], list[dict[str, str]]]:
    available: list[str] = []
    deferred: list[str] = []
    not_claimable: list[str] = []
    deferred_items: list[dict[str, str]] = []

    gate = orchestration.get("request_gate", {})
    if gate.get("status") == "ready":
        available.append("request_context_gate_passed")
    else:
        deferred_items.append(
            {"item": "workflow_dispatch", "reason": f"request gate status={gate.get('status')}"}
        )

    execution = orchestration.get("execution")
    if isinstance(execution, dict):
        status = str(execution.get("status", ""))
        if status == "ok":
            available.append("non_cad_workflow_execution")
            if execution.get("dry_run_report", {}).get("status") == "valid":
                available.append("dry_run_valid_plan_only")
            if execution.get("artifacts"):
                available.append("workflow_artifacts_written")
        elif status == "deferred":
            deferred.append("cad_execution")
            deferred_items.append({"item": "cad_execution", "reason": str(execution.get("reason", "deferred"))})
        elif status == "skipped":
            deferred_items.append({"item": "workflow_execution", "reason": str(execution.get("reason", "skipped"))})
    elif orchestration.get("may_execute"):
        deferred.append("workflow_execution")
        deferred_items.append({"item": "workflow_execution", "reason": "execute flag was false"})
    else:
        deferred_items.append(
            {
                "item": "workflow_execution",
                "reason": str(dispatch.get("reason", "orchestrator blocked execution")),
            }
        )

    execution_dict = orchestration.get("execution") if isinstance(orchestration.get("execution"), dict) else None
    allow_cad = bool((request_context.get("cad_policy") or {}).get("allow_cad"))
    needs_readback = bool(dispatch.get("requires_cad")) or allow_cad
    if needs_readback and not _geometry_verified(execution_dict):
        deferred.append("readback_geometry_verified")
        if bool(dispatch.get("requires_cad")) and not any(item["item"] == "cad_execution" for item in deferred_items):
            deferred_items.append(
                {"item": "cad_execution", "reason": "workflow route requires real CAD readback"}
            )

    maturity = str(scene_record.get("maturity", "core_only")) if scene_record else "core_only"
    not_claimable.extend(MATURITY_NOT_CLAIMABLE.get(maturity, ["scene_product_delivery"]))

    activation = orchestration.get("scene_activation", {})
    if not activation.get("may_use_scene_module"):
        not_claimable.append("scene_specific_delivery")
    else:
        available.append("scene_module_preferences")

    return available, deferred, sorted(set(not_claimable)), deferred_items


def build_route_audit_report(
    request_context: dict[str, Any],
    orchestration: dict[str, Any],
    *,
    registry: dict[str, Any],
    report_id: str | None = None,
) -> dict[str, Any]:
    """Summarize routing, scene activation, evidence, and deferred capabilities."""

    gate = orchestration.get("request_gate", {})
    activation = orchestration.get("scene_activation", {})
    dispatch = orchestration.get("workflow_dispatch", {})
    activated_scene_id = str(activation.get("activated_scene_id", DEFAULT_SCENE_ID))
    scene_record = get_scene(registry, activated_scene_id) or get_scene(registry, DEFAULT_SCENE_ID)

    may_execute = bool(orchestration.get("may_execute"))
    status = _orchestrator_status(gate, dispatch, may_execute)
    available, deferred, not_claimable, deferred_items = _collect_evidence(
        request_context=request_context,
        orchestration=orchestration,
        scene_record=scene_record if isinstance(scene_record, dict) else None,
        dispatch=dispatch if isinstance(dispatch, dict) else {},
    )

    routing_summary = {
        "request_kind": str(request_context.get("request_kind", "")),
        "activated_scene_id": activated_scene_id,
        "scene_module_enabled": bool(activation.get("may_use_scene_module")),
        "selected_workflow_id": str(dispatch.get("workflow_id", "")),
        "workflow_selection_reason": str(dispatch.get("reason", "")),
        "orchestrator_status": status,
        "entrypoint": str(dispatch.get("entrypoint", "")),
        "may_execute": may_execute,
    }

    scene_section = {
        "activation_status": str(activation.get("activation_status", "")),
        "maturity": str(scene_record.get("maturity", "core_only")) if isinstance(scene_record, dict) else "core_only",
        "match_reason": str(activation.get("match_reason", "")),
        "scene_capabilities": list(scene_record.get("capabilities", [])) if isinstance(scene_record, dict) else [],
        "disabled_conditions": list(scene_record.get("disabled_conditions", []))
        if isinstance(scene_record, dict)
        else [],
    }

    human_summary = (
        f"request_kind={routing_summary['request_kind']}; "
        f"scene={activated_scene_id} ({scene_section['activation_status']}); "
        f"workflow={routing_summary['selected_workflow_id'] or 'none'}; "
        f"status={status}; "
        f"evidence_available={len(available)}; deferred={len(deferred)}"
    )

    return {
        "version": "0.1",
        "report_id": report_id or f"route-audit-{request_context.get('context_id', 'unknown')}",
        "context_id": request_context.get("context_id"),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "routing_summary": routing_summary,
        "scene": scene_section,
        "evidence": {
            "available": sorted(set(available)),
            "deferred": sorted(set(deferred)),
            "not_claimable": not_claimable,
        },
        "deferred_items": deferred_items,
        "request_gate_status": str(gate.get("status", "")),
        "workflow_dispatch_status": str(dispatch.get("status", "")),
        "execution_status": str((orchestration.get("execution") or {}).get("status", "not_run")),
        "human_summary": human_summary,
    }


def write_route_audit_report(path: Path, report: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
