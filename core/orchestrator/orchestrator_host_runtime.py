"""Read-only Orchestrator Host runtime for model-backed agent dispatch."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from core.model_review.codex_cli_client import CodexCliReviewConfig, Runner
from core.model_review.prompt_library import list_prompt_packs, run_prompt_pack_review
from core.orchestrator.a_to_a_task_contract import build_a_to_a_task_contract
from core.orchestrator.run_package_state import advance_run_state
from core.orchestrator.request_context import build_request_context, evaluate_request_gate
from core.orchestrator.rule_context_pack import build_rule_context_pack
from core.orchestrator.semantic_asset_route import resolve_semantic_asset_route


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_MANIFEST_PATH = PROJECT_ROOT / "agents" / "pipeline" / "pipeline_manifest.json"
PROMPT_PACK_MANIFEST_PATH = PROJECT_ROOT / "core" / "model_review" / "prompt_packs" / "manifest.json"

DISPATCH_PLAN_FILE = "dispatch_plan.json"
TASK_CONTRACT_FILE = "task_contract.json"
REQUIRED_AGENTS_FILE = "required_agents.json"
RISK_ASSESSMENT_FILE = "risk_assessment.json"
RULE_CONTEXT_PACK_FILE = "rule_context_pack.json"
MODEL_TRIGGER_DECISION_FILE = "model_trigger_decision.json"

VISIBLE_CAD_ROUTES = frozenset({"standard_draw", "local_repair", "asset_reuse", "focused_retraining"})

QUICK_TRIAL_TERMS = ("试一下", "快画", "小动作", "先看看", "先别沉淀", "不沉淀", "quick trial")
DELETE_TERMS = ("删除", "清理", "删掉", "移除", "delete", "cleanup", "purge", "clear_previous")
REPAIR_TERMS = ("修复", "局部", "不对", "画不准", "改错", "乱码", "错线", "repair")
NEARBY_TERMS = ("旁边", "相邻", "附近", "邻区", "nearby", "adjacent", "next to")
ASSET_REUSE_TERMS = ("调用", "复用", "插入", "套用", "asset reuse", "reuse asset")
ASSET_TERMS = ("资产", "系统资产", "通用资产", "asset", "system asset")
SEDIMENTATION_TERMS = ("沉淀", "收进资产库", "收入资产库", "作为通用资产", "作为系统资产", "systemize asset")
FOCUSED_TRAINING_TERMS = ("训练", "复训", "加深", "任务 ", "任务", "focused retraining")
FORMAL_ACCEPTANCE_TERMS = ("验收", "训练通过", "记入工作台", "刷新队列", "formal acceptance")
REPOSITORY_GOVERNANCE_TERMS = ("压缩", "同步状态", "文档治理", "清理仓库", "data bloat", "artifact governance")
STATUS_QUERY_TERMS = ("状态", "进度", "表 c", "表C", "刷新表", "coverage", "status", "progress")
MODEL_TRIGGER_TERMS = (
    "设计",
    "风格",
    "专业",
    "构思",
    "候选",
    "a/b/c",
    "不像",
    "太乱",
    "不高级",
    "看着不对",
    "主观",
    "验收",
    "交付",
    "closeout",
    "模糊",
)
MODEL_REQUIRED_ROUTES = frozenset({"system_asset_sedimentation", "asset_reuse", "local_repair", "formal_acceptance"})

ROUTE_DEFAULT_AGENTS: dict[str, list[str]] = {
    "quick_trial": [
        "pipeline_context_curator",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit",
        "pipeline_delivery",
    ],
    "standard_draw": [
        "pipeline_context_curator",
        "pipeline_visual_intent",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit",
        "pipeline_visual_acceptance_reviewer",
        "pipeline_delivery",
    ],
    "local_repair": [
        "pipeline_context_curator",
        "pipeline_repair",
        "pipeline_execute",
        "pipeline_audit",
        "pipeline_visual_acceptance_reviewer",
        "pipeline_delivery",
    ],
    "asset_reuse": [
        "pipeline_context_curator",
        "pipeline_asset_retriever",
        "pipeline_asset_governor",
        "pipeline_asset_reuse_auditor",
        "pipeline_execute",
        "pipeline_audit",
        "pipeline_visual_acceptance_reviewer",
        "pipeline_delivery",
    ],
    "system_asset_sedimentation": [
        "pipeline_context_curator",
        "pipeline_asset_retriever",
        "pipeline_asset_governor",
        "pipeline_asset_librarian",
        "pipeline_asset_dwg_curator",
        "pipeline_asset_reuse_auditor",
        "pipeline_audit",
        "pipeline_learning_promoter",
        "pipeline_delivery",
    ],
    "focused_retraining": [
        "pipeline_context_curator",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit",
        "pipeline_visual_acceptance_reviewer",
        "pipeline_repair",
        "pipeline_learning_promoter",
        "pipeline_delivery",
    ],
    "formal_acceptance": [
        "pipeline_context_curator",
        "pipeline_audit",
        "pipeline_visual_acceptance_reviewer",
        "pipeline_learning_promoter",
        "pipeline_delivery",
    ],
    "repository_artifact_governance": [
        "pipeline_context_curator",
        "pipeline_audit",
        "pipeline_delivery",
    ],
}

ROUTE_HARD_GATES: dict[str, list[str]] = {
    "quick_trial": ["preview_only_boundary", "cad_readback"],
    "standard_draw": ["cad_plan_required", "validate_plan", "dry_run", "cad_readback", "visual_acceptance_review", "closeout_gate"],
    "local_repair": ["repair_plan", "cad_readback", "visual_acceptance_review", "closeout_gate"],
    "asset_reuse": [
        "asset_registry_encoding_preflight",
        "asset_source_boundary",
        "asset_reuse_audit",
        "cad_readback",
        "visual_acceptance_review",
        "closeout_gate",
    ],
    "system_asset_sedimentation": [
        "main_agent_dispatch_awareness",
        "asset_governance",
        "asset_library_indexing",
        "asset_dwg_curation",
        "asset_reuse_audit",
        "native_visible_asset_evidence",
        "reuse_workflow_probe",
        "data_bloat_governance",
    ],
    "focused_retraining": ["validate_plan", "dry_run", "cad_readback", "visual_acceptance_review", "learning", "closeout_gate"],
    "formal_acceptance": ["visual_acceptance_review", "cad_readback", "data_bloat_governance", "learning", "closeout_gate"],
    "repository_artifact_governance": ["source_of_truth_sync", "doc_governance_audit"],
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _load_pipeline_manifest() -> dict[str, Any]:
    return _read_json(PIPELINE_MANIFEST_PATH)


def _registered_agents(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    agents = manifest.get("agents", [])
    if not isinstance(agents, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for agent in agents:
        if isinstance(agent, dict) and agent.get("agent_id"):
            result[str(agent["agent_id"])] = agent
    return result


def _unique(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _request_payload_text(user_request_file: dict[str, Any]) -> str:
    value = user_request_file.get("userRequest", "")
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("text", "user_request", "request", "prompt"):
            if value.get(key):
                return str(value[key])
    return str(value)


def _request_context_from_run(run_dir: Path) -> tuple[str, dict[str, Any], dict[str, Any], dict[str, Any]]:
    user_request_file = _read_json(run_dir / "user_request.json")
    context_pack = _read_json(run_dir / "context_pack.json")
    request_text = _request_payload_text(user_request_file)
    request_context = context_pack.get("requestContext") or context_pack.get("request_context")
    if isinstance(request_context, dict):
        return request_text, user_request_file, context_pack, request_context

    user_request = user_request_file.get("userRequest", {})
    request_kind = "general"
    if isinstance(user_request, dict) and user_request.get("requestKind"):
        request_kind = str(user_request["requestKind"])
    request_context = build_request_context(
        context_id=str(user_request_file.get("runId") or run_dir.name),
        request_kind=request_kind,
        user_request=request_text,
        allow_cad=False,
    )
    return request_text, user_request_file, context_pack, request_context


def _has_any(text: str, terms: tuple[str, ...]) -> bool:
    lowered = text.casefold()
    return any(term.casefold() in lowered for term in terms)


def _route_for(request_text: str, request_context: dict[str, Any], task_kind: str) -> str:
    text = request_text or str(request_context.get("user_request", ""))
    if task_kind == "system_asset_sedimentation" or _has_any(text, SEDIMENTATION_TERMS):
        return "system_asset_sedimentation"
    if _has_any(text, ASSET_REUSE_TERMS) and _has_any(text, ASSET_TERMS):
        return "asset_reuse"
    if _has_any(text, REPOSITORY_GOVERNANCE_TERMS):
        return "repository_artifact_governance"
    if _has_any(text, FORMAL_ACCEPTANCE_TERMS):
        return "formal_acceptance"
    if _has_any(text, QUICK_TRIAL_TERMS):
        return "quick_trial"
    if _has_any(text, DELETE_TERMS) or _has_any(text, REPAIR_TERMS):
        return "local_repair"
    if _has_any(text, FOCUSED_TRAINING_TERMS):
        return "focused_retraining"
    return "standard_draw"


def _needs_delete_scope(text: str) -> bool:
    return _has_any(text, DELETE_TERMS)


def _needs_neighbor_protection(text: str, route: str) -> bool:
    return route == "local_repair" or _has_any(text, NEARBY_TERMS)


def _additional_requests_from_contract(contract: dict[str, Any]) -> list[dict[str, str]]:
    decision = contract.get("dispatchDecision", {})
    requests = decision.get("additionalAgentRequests", []) if isinstance(decision, dict) else []
    result: list[dict[str, str]] = []
    if isinstance(requests, list):
        for request in requests:
            if isinstance(request, dict) and request.get("requestedAgentId"):
                result.append(
                    {
                        "requestedAgentId": str(request["requestedAgentId"]),
                        "reason": str(request.get("reason", "unregistered agent requested")),
                        "status": str(request.get("status", "needs_reviewed_package")),
                    }
                )
    return result


def _required_agent_ids(
    *,
    route: str,
    contract: dict[str, Any],
    registered_agent_ids: set[str],
) -> tuple[list[str], list[dict[str, str]]]:
    requested = _unique([*ROUTE_DEFAULT_AGENTS.get(route, []), *[str(item) for item in contract.get("requiredAgents", [])]])
    additional = _additional_requests_from_contract(contract)
    effective: list[str] = []
    for agent_id in requested:
        if agent_id in registered_agent_ids:
            effective.append(agent_id)
        else:
            additional.append(
                {
                    "requestedAgentId": agent_id,
                    "reason": "required agent is not registered in pipeline manifest",
                    "status": "needs_reviewed_package",
                }
            )
    return _unique(effective), additional


def _hard_gates_for(route: str, *, request_text: str, contract: dict[str, Any]) -> list[str]:
    gates = [*ROUTE_HARD_GATES.get(route, []), *[str(item) for item in contract.get("hardGates", [])]]
    if _needs_delete_scope(request_text):
        gates.extend(["delete_scope_gate", "victim_set_preview"])
    if _needs_neighbor_protection(request_text, route):
        gates.extend(["neighbor_protection", "occupied_bbox_check"])
    if route in VISIBLE_CAD_ROUTES:
        gates.extend(["cad_readback", "visual_acceptance_review", "closeout_gate"])
    return _unique(gates)


def _agent_reason(agent_id: str, route: str, hard_gates: list[str]) -> str:
    if agent_id == "pipeline_visual_acceptance_reviewer":
        return "visible CAD output requires user-facing visual acceptance before delivery"
    if agent_id == "pipeline_repair":
        return "local repair or delete_replace request requires proposal-only repair planning"
    if agent_id == "pipeline_asset_governor":
        return "asset route requires source boundary and lifecycle governance"
    if agent_id == "pipeline_asset_dwg_curator":
        return "asset sedimentation needs native DWG layout and saved-DWG boundary checks"
    if agent_id == "pipeline_asset_reuse_auditor":
        return "asset route requires reuse probe/replay and savedCurrentDwg=false proof"
    if agent_id == "pipeline_execute":
        return "CAD execution remains delegated and gated; orchestrator host is read-only"
    if agent_id == "pipeline_audit":
        return "machine audit/readback evidence is required before delivery claims"
    return f"route={route} requires registered pipeline responsibility"


def _agent_gate(agent_id: str, hard_gates: list[str]) -> str:
    if agent_id == "pipeline_visual_acceptance_reviewer":
        return "visual_acceptance_review"
    if agent_id == "pipeline_repair":
        return "repair_plan"
    if agent_id == "pipeline_asset_governor":
        return "asset_governance"
    if agent_id == "pipeline_asset_dwg_curator":
        return "asset_dwg_curation"
    if agent_id == "pipeline_asset_reuse_auditor":
        return "asset_reuse_audit"
    if agent_id == "pipeline_audit":
        return "cad_readback" if "cad_readback" in hard_gates else "audit"
    return hard_gates[0] if hard_gates else "dispatch"


def _build_required_agents_report(
    *,
    run_id: str,
    route: str,
    agent_ids: list[str],
    additional_requests: list[dict[str, str]],
    registered_agents: dict[str, dict[str, Any]],
    prompt_pack_ids: set[str],
    hard_gates: list[str],
) -> dict[str, Any]:
    agents: list[dict[str, Any]] = []
    for agent_id in agent_ids:
        manifest_entry = registered_agents.get(agent_id, {})
        agents.append(
            {
                "agentId": agent_id,
                "registered": agent_id in registered_agents,
                "promptPackAvailable": agent_id in prompt_pack_ids,
                "mayExecuteCad": bool(manifest_entry.get("may_invoke_cad")),
                "reason": _agent_reason(agent_id, route, hard_gates),
                "hardGate": _agent_gate(agent_id, hard_gates),
            }
        )
    return {
        "schemaVersion": "orchestrator-host-required-agents/v1",
        "runId": run_id,
        "route": route,
        "agentIds": agent_ids,
        "agents": agents,
        "additionalAgentRequests": additional_requests,
        "unregisteredAgentPolicy": {
            "activationAllowed": False,
            "allowedStatuses": ["needs_reviewed_package", "needs_openspec_change"],
        },
    }


def _build_dispatch_plan(
    *,
    run_id: str,
    route: str,
    task_kind: str,
    request_text: str,
    agent_ids: list[str],
    hard_gates: list[str],
    additional_requests: list[dict[str, str]],
    request_gate: dict[str, Any],
) -> dict[str, Any]:
    blocking_reasons: list[str] = []
    if request_gate.get("status") in {"blocked", "needs_clarification"}:
        blocking_reasons.extend(str(item) for item in request_gate.get("blocked_reasons", []))
    if additional_requests:
        blocking_reasons.append(
            "unregistered agent requests require reviewed package: "
            + ", ".join(request["requestedAgentId"] for request in additional_requests)
        )

    status = "blocked" if blocking_reasons else "ready"
    tasks = [
        {
            "taskId": f"{index:02d}-{agent_id}",
            "agentId": agent_id,
            "status": "pending",
            "reason": _agent_reason(agent_id, route, hard_gates),
            "hardGate": _agent_gate(agent_id, hard_gates),
        }
        for index, agent_id in enumerate(agent_ids, start=1)
    ]
    return {
        "schemaVersion": "orchestrator-host-dispatch-plan/v1",
        "runId": run_id,
        "status": status,
        "route": route,
        "taskKind": task_kind,
        "userIntentSummary": request_text[:240],
        "requiredAgents": agent_ids,
        "tasks": tasks,
        "hardGates": hard_gates,
        "needsUserConfirmation": False,
        "blockedBeforeExecution": bool(blocking_reasons),
        "blockingReasons": blocking_reasons,
        "additionalAgentRequests": additional_requests,
        "evidenceBoundary": [
            "orchestrator host runtime is read-only",
            "dispatch plan does not execute CAD",
            "dispatch plan does not prove CAD geometry or user acceptance",
        ],
    }


def _build_task_contract(
    *,
    run_id: str,
    route: str,
    dispatch_plan: dict[str, Any],
    a_to_a_contract: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schemaVersion": "orchestrator-host-task-contract/v1",
        "runId": run_id,
        "status": dispatch_plan["status"],
        "route": route,
        "requiredAgents": dispatch_plan["requiredAgents"],
        "hardGates": dispatch_plan["hardGates"],
        "aToATaskContract": a_to_a_contract,
        "deliveryBoundary": {
            "mayClaimComplete": False,
            "mayExecuteCad": False,
            "mayRequestUserReview": False,
            "allowedClaim": "已生成主编排分发计划；尚未执行 CAD 或完成验收",
        },
    }


def _build_risk_assessment(
    *,
    run_id: str,
    route: str,
    request_text: str,
    hard_gates: list[str],
    dispatch_plan: dict[str, Any],
) -> dict[str, Any]:
    required_before_cad: list[str] = []
    if "delete_scope_gate" in hard_gates:
        required_before_cad.append("victim_set_preview")
    if "neighbor_protection" in hard_gates:
        required_before_cad.append("occupied_bbox_check")
    if "asset_source_boundary" in hard_gates or route.startswith("asset") or route == "system_asset_sedimentation":
        required_before_cad.append("sourceSpec")
    if route in VISIBLE_CAD_ROUTES or route == "system_asset_sedimentation":
        required_before_cad.extend(["validate_plan", "dry_run", "created_handles_readback"])
    required_before_cad = _unique(required_before_cad)

    return {
        "schemaVersion": "orchestrator-host-risk-assessment/v1",
        "runId": run_id,
        "status": "blocked" if dispatch_plan["status"] == "blocked" else "ready",
        "route": route,
        "riskLevel": "high" if route in {"system_asset_sedimentation", "asset_reuse", "local_repair"} else "normal",
        "riskFlags": {
            "visibleCadOutput": route in VISIBLE_CAD_ROUTES,
            "deleteOrCleanup": _needs_delete_scope(request_text),
            "nearbyPlacement": _has_any(request_text, NEARBY_TERMS),
            "systemAsset": route in {"asset_reuse", "system_asset_sedimentation"},
            "modelOnly": True,
        },
        "requiredBeforeCad": required_before_cad,
        "mustNotDo": [
            "do not write CAD from orchestrator host",
            "do not save current business DWG",
            "do not modify formal layers",
            "do not activate unregistered agents",
            "do not claim geometry verified from model or screenshot alone",
        ],
    }


def _model_trigger_decision(
    *,
    request_text: str,
    request_context: dict[str, Any],
    dispatch_plan: dict[str, Any],
) -> dict[str, Any]:
    request_kind = str(request_context.get("request_kind") or "")
    route = str(dispatch_plan.get("route") or "")
    text = request_text or str(request_context.get("user_request") or "")
    trigger_signals: list[str] = []
    if _has_any(text, MODEL_TRIGGER_TERMS):
        trigger_signals.append("subjective_or_design_judgment")
    if route in MODEL_REQUIRED_ROUTES:
        trigger_signals.append(f"high_risk_route:{route}")
    if "closeout_gate" in [str(item) for item in dispatch_plan.get("hardGates", [])] and _has_any(text, ("交付", "验收", "closeout")):
        trigger_signals.append("closeout_boundary")
    deterministic_status_query = request_kind in {"status", "query", "progress"} or _has_any(text, STATUS_QUERY_TERMS)
    if deterministic_status_query and route not in MODEL_REQUIRED_ROUTES:
        return {
            "schemaVersion": "model-trigger-decision/v1",
            "status": "deterministic_only",
            "modelRequired": False,
            "triggerSignals": [],
            "reason": "ordinary status/progress query is handled by deterministic rules",
            "deterministicRoute": True,
        }
    model_required = bool(trigger_signals)
    return {
        "schemaVersion": "model-trigger-decision/v1",
        "status": "model_required" if model_required else "deterministic_only",
        "modelRequired": model_required,
        "triggerSignals": trigger_signals,
        "reason": "model judgment required by trigger policy" if model_required else "no model trigger signals detected",
        "deterministicRoute": not model_required,
    }


def _model_payload(
    *,
    request_text: str,
    request_context: dict[str, Any],
    dispatch_plan: dict[str, Any],
    required_agents: dict[str, Any],
    risk_assessment: dict[str, Any],
    rule_context_pack: dict[str, Any],
    model_trigger_decision: dict[str, Any],
) -> dict[str, Any]:
    return {
        "userRequest": request_text,
        "taskContext": {
            "taskKind": dispatch_plan["taskKind"],
            "route": dispatch_plan["route"],
            "dispatchStatus": dispatch_plan["status"],
            "requestContext": request_context,
        },
        "evidenceRefs": [
            "user_request.json",
            "context_pack.json",
            RULE_CONTEXT_PACK_FILE,
            "agents/pipeline/pipeline_manifest.json",
            "core/model_review/prompt_packs/manifest.json",
        ],
        "ruleContextPack": rule_context_pack,
        "modelTriggerDecision": model_trigger_decision,
        "statePatchRequest": {
            "phase": "orchestrator_reviewed",
            "phaseLabelForUser": "主编排已生成分发计划",
        },
        "agentSpecific": {
            "dispatchPlan": dispatch_plan,
            "requiredAgents": required_agents,
            "riskAssessment": risk_assessment,
            "ruleContextPackStatus": rule_context_pack.get("status"),
            "modelTriggerDecision": model_trigger_decision,
        },
    }


def _maybe_run_model_review(
    *,
    run_dir: Path,
    request_text: str,
    request_context: dict[str, Any],
    dispatch_plan: dict[str, Any],
    required_agents: dict[str, Any],
    risk_assessment: dict[str, Any],
    rule_context_pack: dict[str, Any],
    model_trigger_decision: dict[str, Any],
    config: CodexCliReviewConfig | None,
    runner: Runner | None,
    cwd: str | Path | None,
) -> dict[str, Any]:
    cfg = config or CodexCliReviewConfig.from_environment()
    if not cfg.enabled:
        return {
            "status": "skipped",
            "modelInvoked": False,
            "reason": "orchestrator host model review disabled",
            "promptPackId": "pipeline_orchestrator",
            "modelTriggerDecision": model_trigger_decision,
        }
    if model_trigger_decision.get("modelRequired") is not True:
        return {
            "status": "skipped",
            "modelInvoked": False,
            "reason": "model trigger policy selected deterministic route",
            "promptPackId": "pipeline_orchestrator",
            "modelTriggerDecision": model_trigger_decision,
        }
    return run_prompt_pack_review(
        agent_id="pipeline_orchestrator",
        payload=_model_payload(
            request_text=request_text,
            request_context=request_context,
            dispatch_plan=dispatch_plan,
            required_agents=required_agents,
            risk_assessment=risk_assessment,
            rule_context_pack=rule_context_pack,
            model_trigger_decision=model_trigger_decision,
        ),
        run_dir=run_dir,
        output_path=run_dir / "agent_outputs" / "pipeline_orchestrator.json",
        config=cfg,
        runner=runner,
        cwd=cwd or PROJECT_ROOT,
        trace_id="orchestrator-dispatch",
    )


def run_orchestrator_host_runtime(
    run_dir: str | Path,
    *,
    config: CodexCliReviewConfig | None = None,
    runner: Runner | None = None,
    cwd: str | Path | None = None,
) -> dict[str, Any]:
    """Read a run package and write deterministic Orchestrator Host dispatch artifacts."""

    run_root = Path(run_dir)
    request_text, user_request_file, context_pack, request_context = _request_context_from_run(run_root)
    run_id = str(user_request_file.get("runId") or run_root.name)
    pipeline_manifest = _load_pipeline_manifest()
    registered_agents = _registered_agents(pipeline_manifest)
    prompt_pack_ids = set(list_prompt_packs())
    semantic_asset_route = resolve_semantic_asset_route(request_context)
    a_to_a_contract = build_a_to_a_task_contract(request_context, semantic_asset_route=semantic_asset_route)
    request_gate = evaluate_request_gate(request_context)
    route = _route_for(request_text, request_context, str(a_to_a_contract.get("taskKind") or "ordinary_orchestration"))
    agent_ids, additional_requests = _required_agent_ids(
        route=route,
        contract=a_to_a_contract,
        registered_agent_ids=set(registered_agents),
    )
    hard_gates = _hard_gates_for(route, request_text=request_text, contract=a_to_a_contract)
    dispatch_plan = _build_dispatch_plan(
        run_id=run_id,
        route=route,
        task_kind=str(a_to_a_contract.get("taskKind") or "ordinary_orchestration"),
        request_text=request_text,
        agent_ids=agent_ids,
        hard_gates=hard_gates,
        additional_requests=additional_requests,
        request_gate=request_gate,
    )
    required_agents = _build_required_agents_report(
        run_id=run_id,
        route=route,
        agent_ids=agent_ids,
        additional_requests=additional_requests,
        registered_agents=registered_agents,
        prompt_pack_ids=prompt_pack_ids,
        hard_gates=hard_gates,
    )
    task_contract = _build_task_contract(
        run_id=run_id,
        route=route,
        dispatch_plan=dispatch_plan,
        a_to_a_contract=a_to_a_contract,
    )
    risk_assessment = _build_risk_assessment(
        run_id=run_id,
        route=route,
        request_text=request_text,
        hard_gates=hard_gates,
        dispatch_plan=dispatch_plan,
    )
    rule_context_pack = build_rule_context_pack(
        run_id=run_id,
        agent_id="pipeline_orchestrator",
        task_kind=str(a_to_a_contract.get("taskKind") or "ordinary_orchestration"),
        trigger_signals=[route, *[str(item) for item in request_gate.get("triggered_semantics", [])]],
        retrieval_queries=[request_text, route, "orchestrator dispatch", "closeout claims"],
        schemas=["core/model_review/schemas/orchestrator_dispatch_review.schema.json"],
        hard_gates=hard_gates,
        forbidden_actions=["cad_write", "dwg_save", "delete_entities", "table_c_claim"],
        evidence_bundle={
            "cadPlan": None,
            "readback": None,
            "screenshot": None,
            "dispatchPlan": dispatch_plan,
            "riskAssessment": risk_assessment,
        },
    )
    model_trigger_decision = _model_trigger_decision(
        request_text=request_text,
        request_context=request_context,
        dispatch_plan=dispatch_plan,
    )
    if rule_context_pack["status"] != "ready":
        for reason in rule_context_pack.get("missingContext", []):
            text = str(reason)
            if text and text not in dispatch_plan["blockingReasons"]:
                dispatch_plan["blockingReasons"].append(text)
        dispatch_plan["status"] = "blocked"
        dispatch_plan["blockedBeforeExecution"] = True
        risk_assessment["status"] = "blocked"

    _write_json(run_root / DISPATCH_PLAN_FILE, dispatch_plan)
    _write_json(run_root / TASK_CONTRACT_FILE, task_contract)
    _write_json(run_root / REQUIRED_AGENTS_FILE, required_agents)
    _write_json(run_root / RISK_ASSESSMENT_FILE, risk_assessment)
    _write_json(run_root / RULE_CONTEXT_PACK_FILE, rule_context_pack)
    _write_json(run_root / MODEL_TRIGGER_DECISION_FILE, model_trigger_decision)

    model_review = _maybe_run_model_review(
        run_dir=run_root,
        request_text=request_text,
        request_context=request_context,
        dispatch_plan=dispatch_plan,
        required_agents=required_agents,
        risk_assessment=risk_assessment,
        rule_context_pack=rule_context_pack,
        model_trigger_decision=model_trigger_decision,
        config=config,
        runner=runner,
        cwd=cwd,
    )

    stage = "blocked" if dispatch_plan["status"] == "blocked" else "dispatch_ready"
    advance_run_state(
        run_root,
        stage,
        input_files=["user_request.json", "context_pack.json"],
        output_files=[
            DISPATCH_PLAN_FILE,
            TASK_CONTRACT_FILE,
            REQUIRED_AGENTS_FILE,
            RISK_ASSESSMENT_FILE,
            RULE_CONTEXT_PACK_FILE,
            MODEL_TRIGGER_DECISION_FILE,
        ],
        blocking_reason="; ".join(dispatch_plan["blockingReasons"]) if stage == "blocked" else "",
    )

    return {
        "schemaVersion": "orchestrator-host-runtime-result/v1",
        "runId": run_id,
        "writtenAt": _utc_now(),
        "dispatchPlan": dispatch_plan,
        "taskContract": task_contract,
        "requiredAgents": required_agents,
        "riskAssessment": risk_assessment,
        "ruleContextPack": rule_context_pack,
        "modelTriggerDecision": model_trigger_decision,
        "modelReview": model_review,
        "inputRefs": {
            "userRequest": "user_request.json",
            "contextPack": "context_pack.json",
            "ruleContextPack": RULE_CONTEXT_PACK_FILE,
            "modelTriggerDecision": MODEL_TRIGGER_DECISION_FILE,
            "pipelineManifest": str(PIPELINE_MANIFEST_PATH),
            "promptPackManifest": str(PROMPT_PACK_MANIFEST_PATH),
        },
    }
