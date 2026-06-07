"""Dispatch REQUEST_CONTEXT to existing Core workflow entrypoints."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any, Callable

from core.orchestrator.a_to_a_task_contract import build_a_to_a_task_contract
from core.orchestrator.activation_policy import (
    ACTIVATION_NEEDS_CLARIFICATION,
    evaluate_scene_activation,
    merge_activation_into_request_gate,
)
from core.orchestrator.request_context import evaluate_request_gate
from core.orchestrator.semantic_asset_route import resolve_semantic_asset_route
from core.orchestrator.route_audit_report import build_route_audit_report, write_route_audit_report
from core.orchestrator.scene_registry import DEFAULT_SCENE_ID, load_scene_registry
from core.path_safety import resolve_under_project_output, resolve_under_project_root
from core.entrypoint_custody.manifest import load_entrypoint_manifest, manifest_entry_for


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROUTES_PATH = PROJECT_ROOT / "examples" / "orchestrator" / "workflow_routes.json"

DISPATCH_READY = "ready"
DISPATCH_BLOCKED = "blocked"
DISPATCH_DEFERRED = "deferred"


def _available_inputs(context: dict[str, Any]) -> set[str]:
    inputs = context.get("inputs", {})
    if not isinstance(inputs, dict):
        return set()
    available = inputs.get("available", [])
    if not isinstance(available, list):
        return set()
    return {str(key) for key in available}


def _input_paths(context: dict[str, Any]) -> dict[str, str]:
    inputs = context.get("inputs", {})
    if not isinstance(inputs, dict):
        return {}
    paths = inputs.get("paths", {})
    return dict(paths) if isinstance(paths, dict) else {}


def _entrypoint_custody_summary(entrypoint: str) -> dict[str, Any]:
    if not entrypoint:
        return {
            "status": "not_applicable",
            "entrypoint": "",
            "registered": False,
            "reason": "no entrypoint selected",
        }
    manifest = load_entrypoint_manifest()
    entry = manifest_entry_for(entrypoint, manifest)
    if not entry:
        return {
            "status": "blocked",
            "entrypoint": entrypoint,
            "registered": False,
            "reasonCode": "workflow_route_entrypoint_unregistered",
            "manifestRef": manifest.get("manifestPath", ""),
        }
    return {
        "status": "registered",
        "entrypoint": entrypoint,
        "registered": True,
        "custodyStatus": entry.get("custodyStatus"),
        "architectureLayer": entry.get("architectureLayer"),
        "directInvocationPolicy": entry.get("directInvocationPolicy"),
        "requiresCustodyGate": bool(entry.get("requiresCustodyGate")),
        "requiresLease": bool(entry.get("requiresLease")),
        "allowedWriteScope": entry.get("allowedWriteScope", []),
        "evidenceBoundary": entry.get("evidenceBoundary", []),
        "manifestRef": f"{manifest.get('manifestPath', '')}#{entrypoint}",
    }


def load_workflow_routes(path: Path | None = None) -> dict[str, Any]:
    routes_path = path or DEFAULT_ROUTES_PATH
    return json.loads(routes_path.read_text(encoding="utf-8"))


def _route_matches(context: dict[str, Any], route: dict[str, Any]) -> bool:
    request_kind = str(context.get("request_kind", ""))
    kinds = route.get("request_kinds", [])
    if request_kind not in kinds:
        return False
    required_any = route.get("required_any_inputs", [])
    if not isinstance(required_any, list) or not required_any:
        return request_kind in kinds
    available = _available_inputs(context)
    return bool(available.intersection(required_any))


def resolve_workflow_route(
    request_context: dict[str, Any],
    routes_table: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Pick the highest-priority workflow route for a request context."""

    table = routes_table or load_workflow_routes()
    routes = sorted(
        [route for route in table.get("routes", []) if isinstance(route, dict) and _route_matches(request_context, route)],
        key=lambda item: int(item.get("priority", 999)),
    )
    if not routes:
        return {
            "workflow_id": "",
            "status": DISPATCH_DEFERRED,
            "reason": f"no workflow route for request_kind={request_context.get('request_kind')!r}",
            "entrypoint": "",
            "requires_cad": False,
            "entrypointCustody": _entrypoint_custody_summary(""),
        }
    route = routes[0]
    entrypoint = str(route.get("entrypoint", ""))
    return {
        "workflow_id": str(route.get("workflow_id", "")),
        "status": DISPATCH_READY,
        "reason": f"matched route priority={route.get('priority')}",
        "entrypoint": entrypoint,
        "default_workflow_path": route.get("default_workflow_path"),
        "requires_cad": bool(route.get("requires_cad")),
        "route": route,
        "entrypointCustody": _entrypoint_custody_summary(entrypoint),
    }


def _import_entrypoint(spec: str) -> Callable[..., Any]:
    module_name, func_name = spec.split(":", 1)
    module = importlib.import_module(module_name)
    func = getattr(module, func_name)
    if not callable(func):
        raise TypeError(f"Entrypoint is not callable: {spec}")
    return func


def _run_object_symbol_glyph(context: dict[str, Any], *, output_dir: Path) -> dict[str, Any]:
    from core.plan_engine.dry_run_report import create_dry_run_report
    from core.plan_engine.validate_plan import validate_plan
    from core.schemas.validator import load_json
    from core.symbol_engine.fallback_policy import resolve_symbol_render_resolution

    paths = _input_paths(context)
    object_spec_path = paths.get("object_spec")
    if not object_spec_path:
        return {"status": "invalid", "errors": ["object_spec path is required"]}
    object_spec = load_json(resolve_under_project_root(PROJECT_ROOT, Path(object_spec_path), label="object_spec"))
    resolution = resolve_symbol_render_resolution(object_spec)
    plan = resolution.get("cad_plan")
    if not isinstance(plan, dict):
        return {"status": "invalid", "errors": ["symbol render resolution produced no cad_plan"]}
    errors = validate_plan(plan)
    dry_run = create_dry_run_report(plan) if not errors else {"status": "invalid", "validation_errors": errors}
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "symbol_render_resolution.json").write_text(
        json.dumps(resolution, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "cad_plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "dry_run_report.json").write_text(
        json.dumps(dry_run, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "status": "ok" if dry_run.get("status") == "valid" else "invalid",
        "workflow_id": "object_symbol_glyph",
        "resolution": resolution,
        "dry_run_report": dry_run,
        "artifacts": {
            "symbol_render_resolution": str(output_dir / "symbol_render_resolution.json"),
            "cad_plan": str(output_dir / "cad_plan.json"),
            "dry_run_report": str(output_dir / "dry_run_report.json"),
        },
    }


def _run_workflow_file_entrypoint(
    route: dict[str, Any],
    *,
    output_dir: Path,
    workflow_path: Path | None = None,
) -> dict[str, Any]:
    entrypoint = str(route.get("entrypoint", ""))
    runner = _import_entrypoint(entrypoint)
    default_path = route.get("default_workflow_path")
    resolved_workflow = workflow_path
    if resolved_workflow is None and isinstance(default_path, str) and default_path.strip():
        resolved_workflow = resolve_under_project_root(PROJECT_ROOT, Path(default_path), label="workflow_path")
    if resolved_workflow is None:
        return {"status": "invalid", "errors": ["workflow_path is required for this route"]}
    result = runner(resolved_workflow, output_dir=output_dir)
    if isinstance(result, dict):
        result.setdefault("workflow_id", route.get("workflow_id"))
    return result


def execute_workflow_dispatch(
    dispatch: dict[str, Any],
    request_context: dict[str, Any],
    *,
    output_dir: Path,
    workflow_path: Path | None = None,
    include_cad: bool = False,
) -> dict[str, Any]:
    """Invoke the resolved workflow entrypoint without duplicating runner logic."""

    if dispatch.get("status") != DISPATCH_READY:
        return {"status": "skipped", "reason": dispatch.get("reason", "dispatch not ready")}

    route = dispatch.get("route", {})
    if not isinstance(route, dict):
        return {"status": "invalid", "errors": ["missing route metadata"]}

    if bool(route.get("requires_cad")) and not include_cad:
        return {
            "status": "deferred",
            "workflow_id": route.get("workflow_id"),
            "reason": "route requires_cad; execution deferred",
        }

    output_dir = resolve_under_project_output(PROJECT_ROOT, output_dir, label="output_dir")
    workflow_id = str(route.get("workflow_id", ""))

    if workflow_id == "object_symbol_glyph":
        return _run_object_symbol_glyph(request_context, output_dir=output_dir)

    paths = _input_paths(request_context)
    if workflow_path is None and paths.get("workflow"):
        workflow_path = resolve_under_project_root(PROJECT_ROOT, Path(paths["workflow"]), label="workflow")

    if workflow_id == "project_sample_blank_shell":
        from core.project_samples.workflow import run_sample_blank_shell_workflow

        return run_sample_blank_shell_workflow(output_dir=output_dir, workflow_path=workflow_path)

    return _run_workflow_file_entrypoint(route, output_dir=output_dir, workflow_path=workflow_path)


def orchestrate_request(
    request_context: dict[str, Any],
    *,
    registry: dict[str, Any] | None = None,
    routes_table: dict[str, Any] | None = None,
    output_dir: Path | None = None,
    execute: bool = False,
    include_cad: bool = False,
) -> dict[str, Any]:
    """Full orchestrator pass: gate, activation, dispatch, optional execution."""

    scene_registry = registry or load_scene_registry()
    gate = evaluate_request_gate(request_context)
    activation = evaluate_scene_activation(request_context, scene_registry)
    gate = merge_activation_into_request_gate(request_context, gate, activation)
    semantic_asset_route = resolve_semantic_asset_route(request_context)
    a_to_a_task_contract = build_a_to_a_task_contract(
        request_context,
        semantic_asset_route=semantic_asset_route,
    )
    dispatch = resolve_workflow_route(request_context, routes_table)

    if gate.get("status") != "ready":
        dispatch = {**dispatch, "status": DISPATCH_BLOCKED, "reason": f"request gate status={gate.get('status')}"}
    elif activation.get("activation_status") == ACTIVATION_NEEDS_CLARIFICATION:
        dispatch = {**dispatch, "status": DISPATCH_BLOCKED, "reason": "scene activation needs clarification"}

    if a_to_a_task_contract.get("status") == "blocked":
        reasons = a_to_a_task_contract.get("blockingReasons", [])
        reason_text = "; ".join(str(reason) for reason in reasons) if isinstance(reasons, list) else str(reasons)
        dispatch = {
            **dispatch,
            "status": DISPATCH_BLOCKED,
            "reason": f"a-to-a hard gate status=blocked: {reason_text}",
        }

    entrypoint_custody = dispatch.get("entrypointCustody", {})
    if isinstance(entrypoint_custody, dict) and entrypoint_custody.get("status") == "blocked":
        dispatch = {
            **dispatch,
            "status": DISPATCH_BLOCKED,
            "reason": f"entrypoint custody blocked: {entrypoint_custody.get('reasonCode')}",
        }

    if bool(dispatch.get("requires_cad")) and not bool(request_context.get("cad_policy", {}).get("allow_cad")):
        dispatch = {**dispatch, "status": DISPATCH_BLOCKED, "reason": "cad_policy.allow_cad is false"}

    report: dict[str, Any] = {
        "version": "0.1",
        "context_id": request_context.get("context_id"),
        "request_gate": gate,
        "scene_activation": activation,
        "activated_scene_id": activation.get("activated_scene_id", DEFAULT_SCENE_ID),
        "semantic_asset_route": semantic_asset_route,
        "a_to_a_task_contract": a_to_a_task_contract,
        "workflow_dispatch": dispatch,
        "may_execute": dispatch.get("status") == DISPATCH_READY and gate.get("may_dispatch_workflow", False),
        "execution": None,
    }

    if execute and report["may_execute"] and output_dir is not None:
        report["execution"] = execute_workflow_dispatch(
            dispatch,
            request_context,
            output_dir=output_dir,
            include_cad=include_cad,
        )
    elif execute and not report["may_execute"]:
        report["execution"] = {"status": "skipped", "reason": "orchestrator gate blocked execution"}

    route_audit = build_route_audit_report(request_context, report, registry=scene_registry)
    report["route_audit_report"] = route_audit
    if output_dir is not None:
        write_route_audit_report(output_dir / "route_audit_report.json", route_audit)

    return report
