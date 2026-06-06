"""Read-only diagnostics for local live model bridge run packages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


STAGES = [
    "worker_orchestration_ready",
    "local_bridge_connected",
    "single_agent_live",
    "multi_agent_live",
    "cad_mcp_preview_live",
    "current_dwg_save",
]
STAGE_ORDER = {stage: index for index, stage in enumerate(STAGES)}
LIVE_MODEL_STAGES = {"single_agent_live", "multi_agent_live", "cad_mcp_preview_live"}


def diagnose_run(run_dir: str | Path) -> dict[str, Any]:
    """Return a layered failure report for one Worker-first run directory."""

    root = Path(run_dir)
    state_path = root / "worker_run_state.json"
    state = _read_json(state_path)
    if not state:
        return _report(
            run_dir=root,
            state={},
            diagnostics=[
                _stage(
                    "worker_orchestration_ready",
                    "blocked",
                    ["worker_run_state.json missing or invalid"],
                    "create_worker_run_or_check_run_dir",
                    evidence=[_rel(root, state_path)],
                )
            ],
        )

    target_stage = str(state.get("completionClaim") or state.get("currentStage") or "worker_orchestration_ready")
    diagnostics = [
        _diagnose_worker(root, state),
        _diagnose_bridge(state, target_stage),
        _diagnose_single_agent(root, state, target_stage),
        _diagnose_multi_agent(root, state, target_stage),
        _diagnose_cad_preview(state, target_stage),
        _diagnose_save_authorization(state),
    ]
    return _report(run_dir=root, state=state, diagnostics=diagnostics)


def _diagnose_worker(root: Path, state: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if state.get("schemaVersion") != "worker_run_state/v1":
        reasons.append("worker_run_state schema invalid")
    if not state.get("runId"):
        reasons.append("runId missing")
    if not isinstance(state.get("tasks"), list):
        reasons.append("tasks missing")
    if _has_security_block(state):
        reasons.extend(_unique([*_list(state.get("securityBlocks")), *_list(state.get("blockedReasons"))]))
    return _stage(
        "worker_orchestration_ready",
        "blocked" if reasons else "pass",
        reasons,
        "fix_worker_state_or_security_gate" if reasons else "",
        evidence=[_rel(root, root / "worker_run_state.json")],
    )


def _diagnose_bridge(state: dict[str, Any], target_stage: str) -> dict[str, Any]:
    if not _gate_enabled(state, target_stage, "local_bridge_connected"):
        return _stage("local_bridge_connected", "not_enabled", [], "enable_bridge_gate_when_needed")
    breakers = state.get("circuitBreakers") if isinstance(state.get("circuitBreakers"), dict) else {}
    bridge_breaker = breakers.get("local_bridge") if isinstance(breakers.get("local_bridge"), dict) else {}
    reasons = _unique([
        str(bridge_breaker.get("reason") or ""),
        *_list(state.get("blockedReasons")),
    ])
    bridge_bad = state.get("state") == "waiting_for_bridge" or bridge_breaker.get("state") == "open"
    if bridge_bad:
        return _stage("local_bridge_connected", "blocked", reasons or ["bridge unavailable"], "start_or_register_local_bridge")
    if not any(str(task.get("leasedBy") or "") for task in _tasks(state)):
        return _stage("local_bridge_connected", "waiting", ["no task lease recorded"], "start_or_register_local_bridge")
    return _stage("local_bridge_connected", "pass", [], "")


def _diagnose_single_agent(root: Path, state: dict[str, Any], target_stage: str) -> dict[str, Any]:
    if not _gate_enabled(state, target_stage, "single_agent_live"):
        return _stage("single_agent_live", "not_enabled", [], "enable_single_agent_live_gate_when_needed")
    return _model_stage(root, "single_agent_live", state, minimum_completed_agents=1)


def _diagnose_multi_agent(root: Path, state: dict[str, Any], target_stage: str) -> dict[str, Any]:
    if not _gate_enabled(state, target_stage, "multi_agent_live"):
        return _stage("multi_agent_live", "not_enabled", [], "enable_multi_agent_live_gate_when_needed")
    return _model_stage(root, "multi_agent_live", state, minimum_completed_agents=3)


def _diagnose_cad_preview(state: dict[str, Any], target_stage: str) -> dict[str, Any]:
    if not _gate_enabled(state, target_stage, "cad_mcp_preview_live"):
        return _stage("cad_mcp_preview_live", "not_enabled", [], "enable_cad_preview_gate_when_needed")
    preview = state.get("cadPreview") if isinstance(state.get("cadPreview"), dict) else {}
    reasons: list[str] = []
    if not preview:
        reasons.append("cad preview report missing")
    if preview.get("targetLayer") not in {"CODEX_PREVIEW", ""}:
        reasons.append("target layer is not CODEX_PREVIEW")
    if preview.get("savedCurrentDwg") is True:
        reasons.append("current DWG was saved without this gate")
    if preview.get("cadGeometryVerified") is not True:
        reasons.append("real CAD geometry not verified")
    if str(preview.get("driverMode") or "") == "fake_driver_preflight":
        reasons.append("fake driver proves orchestration only")
    status = "pass" if not reasons else "blocked"
    return _stage("cad_mcp_preview_live", status, reasons, "open_autocad_or_use_cad_ready_gate" if reasons else "")


def _diagnose_save_authorization(state: dict[str, Any]) -> dict[str, Any]:
    preview = state.get("cadPreview") if isinstance(state.get("cadPreview"), dict) else {}
    if preview.get("savedCurrentDwg") is True:
        return _stage(
            "current_dwg_save",
            "blocked",
            ["current DWG save is outside live bridge proof"],
            "remove_save_or_require_explicit_system_asset_save_gate",
        )
    return _stage("current_dwg_save", "not_enabled", [], "save remains disabled by default")


def _model_stage(root: Path, stage: str, state: dict[str, Any], *, minimum_completed_agents: int) -> dict[str, Any]:
    tasks = _tasks(state)
    completed_model_tasks = [
        task
        for task in tasks
        if task.get("state") == "completed"
        and isinstance(task.get("result"), dict)
        and task["result"].get("modelInvoked") is True
        and task["result"].get("modelUnavailable") is not True
        and task["result"].get("schemaValid") is True
    ]
    reasons: list[str] = []
    if state.get("modelInvoked") is not True and not completed_model_tasks:
        reasons.append("model was not invoked")
    if state.get("modelUnavailable") is True:
        reasons.append("model provider unavailable")
    if state.get("schemaValid") is False and state.get("modelInvoked") is True:
        reasons.append("model output schema invalid")
    evidence: list[str] = []
    for task in completed_model_tasks:
        trace_reasons, trace_evidence = _validate_model_trace(root, task)
        reasons.extend(trace_reasons)
        evidence.extend(trace_evidence)
    for task in tasks:
        if task.get("state") == "blocked":
            reasons.append(str(task.get("blockedReason") or f"{task.get('agentId')} blocked"))
    if len(completed_model_tasks) < minimum_completed_agents:
        reasons.append(f"completed live model agents below {minimum_completed_agents}")
    return _stage(
        stage,
        "pass" if not reasons else "blocked",
        _unique(reasons),
        "check_codex_cli_model_bridge_or_agent_schema" if reasons else "",
        evidence=_unique(evidence),
    )


def _validate_model_trace(root: Path, task: dict[str, Any]) -> tuple[list[str], list[str]]:
    result = task.get("result") if isinstance(task.get("result"), dict) else {}
    trace_ref = str(result.get("traceRef") or "")
    if not trace_ref:
        return ["model traceRef missing"], []
    summary_path = root / trace_ref
    if not summary_path.is_file():
        return [f"model trace missing: {trace_ref}"], [_rel(root, summary_path)]
    trace_dir = summary_path.parent
    reasons: list[str] = []
    evidence = [_rel(root, summary_path)]
    trace_review_path = trace_dir / "trace_review.json"
    trace_manifest_path = trace_dir / "trace_manifest.json"
    command_path = trace_dir / "command.json"
    normalized_output_path = trace_dir / "normalized_output.json"
    for path in (trace_review_path, trace_manifest_path, command_path, normalized_output_path):
        evidence.append(_rel(root, path))
        if not path.is_file():
            reasons.append(f"model trace file missing: {_rel(root, path)}")
    trace_review = _read_json(trace_review_path)
    if trace_review and trace_review.get("status") != "pass":
        reasons.append("model trace review blocked")
    trace_manifest = _read_json(trace_manifest_path)
    if trace_manifest:
        if trace_manifest.get("provider") != "codex_cli":
            reasons.append(f"model trace provider is {trace_manifest.get('provider') or 'missing'}")
        if trace_manifest.get("route") != "codex_cli_local":
            reasons.append(f"model trace route is {trace_manifest.get('route') or 'missing'}")
    command = _read_json(command_path)
    if command:
        command_list = command.get("command") if isinstance(command.get("command"), list) else []
        if command.get("status") != "built":
            reasons.append("model command was not built")
        if command.get("sanitized") is not True:
            reasons.append("model command was not sanitized")
        if "exec" not in {str(item) for item in command_list}:
            reasons.append("codex exec command missing")
        if "--model" not in {str(item) for item in command_list}:
            reasons.append("model command missing --model")
    normalized_output = _read_json(normalized_output_path)
    provider = normalized_output.get("modelProviderStatus") if isinstance(normalized_output.get("modelProviderStatus"), dict) else {}
    if provider:
        route = str(provider.get("route") or "")
        if route != "codex_cli_local":
            reasons.append(f"model provider route is {route or 'missing'}")
        if provider.get("modelInvoked") is not True:
            reasons.append("model provider did not invoke")
        if provider.get("modelUnavailable") is True:
            reasons.append("model provider unavailable")
        if provider.get("schemaValid") is not True:
            reasons.append("model provider schema invalid")
    else:
        reasons.append("modelProviderStatus missing from normalized output")
    return _unique(reasons), _unique(evidence)


def _report(*, run_dir: Path, state: dict[str, Any], diagnostics: list[dict[str, Any]]) -> dict[str, Any]:
    first = next((item for item in diagnostics if item.get("status") == "blocked"), None)
    return {
        "schemaVersion": "local-live-model-bridge-diagnostic/v1",
        "status": "blocked" if first else "pass",
        "runId": str(state.get("runId") or ""),
        "runDir": str(run_dir),
        "completionClaim": str(state.get("completionClaim") or ""),
        "state": str(state.get("state") or ""),
        "firstBlockedAt": str(first.get("stage") if first else ""),
        "blockedReasons": _list(first.get("blockedReasons")) if first else [],
        "nextAction": str(first.get("nextAction") if first else ""),
        "stageDiagnostics": diagnostics,
        "evidenceBoundary": [
            "diagnostic is read-only and does not start bridge, invoke GPT-5.5, connect CAD, or save DWG",
            "worker_orchestration_ready is the default proof layer",
            "live bridge, GPT-5.5, multi-agent, and CAD-MCP proof layers must be enabled by explicit conditions",
            "fake_driver_preflight never proves real AutoCAD geometry",
        ],
    }


def _stage(stage: str, status: str, blocked_reasons: list[str], next_action: str, *, evidence: list[str] | None = None) -> dict[str, Any]:
    return {
        "stage": stage,
        "status": status,
        "blockedReasons": _unique(blocked_reasons),
        "nextAction": next_action,
        "evidence": evidence or [],
    }


def _stage_required(target_stage: str, stage: str) -> bool:
    return STAGE_ORDER.get(target_stage, 0) >= STAGE_ORDER[stage]


def _gate_enabled(state: dict[str, Any], target_stage: str, stage: str) -> bool:
    gates = state.get("featureGates") if isinstance(state.get("featureGates"), dict) else {}
    gate = gates.get(stage) if isinstance(gates.get(stage), dict) else {}
    if gate:
        return gate.get("enabled") is True
    return _stage_required(target_stage, stage)


def _tasks(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in state.get("tasks", []) if isinstance(item, dict)]


def _has_security_block(state: dict[str, Any]) -> bool:
    breakers = state.get("circuitBreakers") if isinstance(state.get("circuitBreakers"), dict) else {}
    security = breakers.get("security_gate") if isinstance(breakers.get("security_gate"), dict) else {}
    return bool(state.get("securityBlocks") or security.get("state") == "open")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if isinstance(value, str) and value:
        return [value]
    return []


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = item.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
