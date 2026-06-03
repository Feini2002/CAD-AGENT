"""A-to-A task contract gates for orchestration-critical agent outputs."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


PASS_STATUSES = frozenset({"pass", "ready", "ok", "complete", "complete_for_current_scope"})
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_MANIFEST_PATH = PROJECT_ROOT / "agents" / "pipeline" / "pipeline_manifest.json"
MAIN_AGENT_GATE = "main_agent_dispatch_awareness"
HIGH_RISK_TASK_KINDS = frozenset({"system_asset_sedimentation", "asset_dwg_layout", "visual_layout_review"})

ASSET_AGENT_GATES: dict[str, str] = {
    "pipeline_asset_governor": "asset_governance",
    "pipeline_asset_librarian": "asset_library_indexing",
    "pipeline_asset_dwg_curator": "asset_dwg_curation",
    "pipeline_asset_reuse_auditor": "asset_reuse_audit",
}
VISUAL_LAYOUT_AGENT = "pipeline_visual_layout_reviewer"
VISUAL_LAYOUT_GATE = "visual_layout_review"
VISUAL_LAYOUT_CHECKS = (
    "layoutMatchesMetaphor",
    "primaryShelvesClear",
    "layoutReadabilityAcceptable",
    "aisleClearanceAcceptable",
    "contentDensityAcceptable",
    "sourceProofRolesSeparated",
    "layerSemanticsAcceptable",
    "futureExpansionClear",
    "retrievalPathReadable",
    "visualNoiseAcceptable",
    "nonScreenshotEvidenceChecked",
)

ASSET_TERMS = (
    "system asset",
    "asset library",
    "standard asset",
    "asset dwg",
    "native dwg",
    "dwg",
    "系统资产",
    "资产库",
    "通用资产",
    "底座资产",
    "原生资产",
)
SEDIMENTATION_TERMS = (
    "sediment",
    "promote asset",
    "systemize asset",
    "收进资产库",
    "收入资产库",
    "沉淀",
    "作为通用资产",
    "作为系统资产",
)
VISUAL_LAYOUT_TERMS = (
    "warehouse",
    "shelf",
    "rack",
    "layout",
    "circulation",
    "expandable",
    "display form",
    "visual review",
    "仓库",
    "货架",
    "置物架",
    "货位",
    "动线",
    "排版",
    "布局",
    "展示形式",
    "可扩展",
    "分类分位置",
    "工作台",
    "索引",
)
PIPELINE_AGENT_ID_PATTERN = re.compile(r"\bpipeline_[a-z0-9_]+\b")


def _request_text(context: dict[str, Any]) -> str:
    fields = [
        context.get("user_request"),
        context.get("request_kind"),
        context.get("scene_hint"),
    ]
    notes = context.get("notes", [])
    if isinstance(notes, list):
        fields.extend(notes)
    return " ".join(str(item) for item in fields if item is not None).casefold()


def _has_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term.casefold() in text for term in terms)


def _semantic_route_targets_asset(semantic_asset_route: dict[str, Any] | None) -> bool:
    if not isinstance(semantic_asset_route, dict):
        return False
    if semantic_asset_route.get("status") not in {"ready", "candidate", "needs_review"}:
        return False
    workflow = semantic_asset_route.get("workflow", {})
    if isinstance(workflow, dict) and workflow.get("reusePlans"):
        return True
    return bool(semantic_asset_route.get("assetId") or semantic_asset_route.get("matchedAssets"))


def _task_kind(context: dict[str, Any], semantic_asset_route: dict[str, Any] | None) -> tuple[str, list[str]]:
    text = _request_text(context)
    is_asset = _has_any(text, ASSET_TERMS) or _semantic_route_targets_asset(semantic_asset_route)
    is_sedimentation = _has_any(text, SEDIMENTATION_TERMS)
    is_visual_layout = _has_any(text, VISUAL_LAYOUT_TERMS)

    semantics: list[str] = []
    if is_asset:
        semantics.append("system_asset")
    if is_sedimentation:
        semantics.append("asset_sedimentation")
    if is_visual_layout:
        semantics.append("visual_layout")

    if is_asset and is_visual_layout:
        return "asset_dwg_layout", semantics
    if is_sedimentation:
        return "system_asset_sedimentation", semantics
    if is_visual_layout:
        return "visual_layout_review", semantics
    return "ordinary_orchestration", semantics


def _required_agents_for(task_kind: str) -> list[str]:
    if task_kind == "asset_dwg_layout":
        return [*ASSET_AGENT_GATES.keys(), VISUAL_LAYOUT_AGENT]
    if task_kind == "system_asset_sedimentation":
        return list(ASSET_AGENT_GATES.keys())
    if task_kind == "visual_layout_review":
        return [VISUAL_LAYOUT_AGENT]
    return []


def _base_required_agents_for(task_kind: str) -> list[str]:
    if task_kind == "asset_dwg_layout":
        return list(ASSET_AGENT_GATES.keys())
    if task_kind == "system_asset_sedimentation":
        return list(ASSET_AGENT_GATES.keys())
    return []


def _hard_gates_for(required_agents: list[str]) -> list[str]:
    gates: list[str] = []
    for agent_id in required_agents:
        if agent_id == VISUAL_LAYOUT_AGENT:
            gates.append(VISUAL_LAYOUT_GATE)
        else:
            gate = ASSET_AGENT_GATES.get(agent_id)
            if gate:
                gates.append(gate)
    return gates


def _load_pipeline_manifest() -> dict[str, Any]:
    try:
        return json.loads(PIPELINE_MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _registered_agent_ids(manifest: dict[str, Any]) -> set[str]:
    agents = manifest.get("agents", [])
    if not isinstance(agents, list):
        return set()
    return {str(agent.get("agent_id", "")) for agent in agents if isinstance(agent, dict) and agent.get("agent_id")}


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _agent_outputs(context: dict[str, Any]) -> dict[str, Any]:
    outputs = context.get("agent_outputs", {})
    return outputs if isinstance(outputs, dict) else {}


def _status_passes(output: dict[str, Any]) -> bool:
    return str(output.get("status", "")).casefold() in PASS_STATUSES


def _visual_layout_failures(output: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for key in VISUAL_LAYOUT_CHECKS:
        value = str(output.get(key, "")).casefold()
        if value not in PASS_STATUSES:
            failures.append(key)
    if output.get("screenshotCapturedOnly") is True:
        failures.append("screenshotCapturedOnly")
    blocking_reasons = output.get("blockingReasons")
    if blocking_reasons:
        failures.append("blockingReasons")
    return failures


def _requested_agent_ids(context: dict[str, Any]) -> list[str]:
    requested: list[str] = []
    explicit = context.get("additional_agent_requests", [])
    if isinstance(explicit, list):
        for item in explicit:
            if isinstance(item, str):
                requested.append(item)
            elif isinstance(item, dict) and item.get("requestedAgentId"):
                requested.append(str(item["requestedAgentId"]))
    requested.extend(PIPELINE_AGENT_ID_PATTERN.findall(_request_text(context)))
    return _unique(requested)


def _build_main_agent_self_check(
    context: dict[str, Any],
    *,
    task_kind: str,
    triggered_semantics: list[str],
) -> dict[str, Any]:
    if task_kind not in HIGH_RISK_TASK_KINDS:
        return {
            "status": "observation",
            "identity": "pipeline_orchestrator_main_agent",
            "mission": "classify request, build task contract, dispatch responsible agents, block unsupported completion claims",
            "taskUnderstanding": {"taskKind": task_kind, "triggeredSemantics": triggered_semantics, "riskLevel": "normal"},
            "responsibilityBoundary": {
                "mayDispatchAgents": True,
                "mayExecuteCad": False,
                "mayClaimCompleteWithoutAgentOutputs": False,
            },
            "knownLimits": [],
            "decisionBasis": ["request semantics", "pipeline manifest"],
        }

    self_check = {
        "status": "pass",
        "identity": "pipeline_orchestrator_main_agent",
        "mission": "classify request, build task contract, dispatch responsible agents, block unsupported completion claims",
        "taskUnderstanding": {
            "taskKind": task_kind,
            "triggeredSemantics": triggered_semantics,
            "riskLevel": "high",
        },
        "responsibilityBoundary": {
            "mayDispatchAgents": True,
            "mayExecuteCad": False,
            "mayClaimCompleteWithoutAgentOutputs": False,
        },
        "knownLimits": [
            "cannot replace CAD readback",
            "cannot approve visual layout without visual_layout_review",
            "cannot activate unregistered agents",
        ],
        "decisionBasis": [
            "request semantics",
            "semantic asset route",
            "pipeline manifest",
            "hard gate definitions",
            "agent output status",
        ],
    }
    override = context.get("main_agent_self_check_override")
    if isinstance(override, dict):
        self_check.update(override)
    return self_check


def _build_dispatch_decision(
    context: dict[str, Any],
    *,
    task_kind: str,
    triggered_semantics: list[str],
    effective_required_agents: list[str],
    registered_agents: set[str],
    missing: list[str],
    failed_gates: list[str],
) -> tuple[dict[str, Any], list[str], list[str]]:
    base_required_agents = _base_required_agents_for(task_kind)
    registered_additions: list[dict[str, str]] = []
    if VISUAL_LAYOUT_AGENT in effective_required_agents and (
        "visual_layout" in triggered_semantics or task_kind == "visual_layout_review"
    ):
        registered_additions.append(
            {
                "agentId": VISUAL_LAYOUT_AGENT,
                "reason": "visual layout semantics require warehouse/shelf readability review",
                "hardGate": VISUAL_LAYOUT_GATE,
            }
        )

    requested_agents = _requested_agent_ids(context)
    additional_requests: list[dict[str, str]] = []
    for agent_id in requested_agents:
        if agent_id not in registered_agents:
            additional_requests.append(
                {
                    "requestedAgentId": agent_id,
                    "reason": "main agent detected a possible new responsibility role in the request",
                    "status": "needs_reviewed_package",
                }
            )

    unregistered_effective = sorted(agent_id for agent_id in effective_required_agents if agent_id not in registered_agents)
    awareness_failures: list[str] = []
    awareness_reasons: list[str] = []
    if unregistered_effective:
        awareness_failures.append(MAIN_AGENT_GATE)
        awareness_reasons.append("unregistered required agents: " + ", ".join(unregistered_effective))

    reviewed_package_required = bool(additional_requests)
    blocked_until_report = bool(missing or failed_gates or unregistered_effective or reviewed_package_required)
    status = "blocked" if blocked_until_report else "ready"
    if reviewed_package_required:
        awareness_reasons.append(
            "reviewed package required for requested agents: "
            + ", ".join(item["requestedAgentId"] for item in additional_requests)
        )

    return (
        {
            "status": status,
            "baseRequiredAgents": base_required_agents,
            "registeredAdditionalAgents": registered_additions,
            "effectiveRequiredAgents": effective_required_agents,
            "additionalAgentRequests": additional_requests,
            "blockedUntilAgentsReport": blocked_until_report,
            "reviewedPackageRequired": reviewed_package_required,
            "reasoning": [
                "high-risk semantics require explicit responsibility dispatch",
                "registered agents may become effective required agents",
                "unregistered agent needs stay reviewed-package candidates",
            ],
        },
        awareness_failures,
        awareness_reasons,
    )


def _evaluate_outputs(required_agents: list[str], outputs: dict[str, Any]) -> tuple[list[str], list[str], dict[str, Any]]:
    missing: list[str] = []
    failed_gates: list[str] = []
    summary: dict[str, Any] = {}

    for agent_id in required_agents:
        output = outputs.get(agent_id)
        if not isinstance(output, dict):
            missing.append(agent_id)
            summary[agent_id] = {"status": "missing"}
            continue

        status = str(output.get("status", "")).casefold()
        gate = VISUAL_LAYOUT_GATE if agent_id == VISUAL_LAYOUT_AGENT else ASSET_AGENT_GATES.get(agent_id, "")
        summary[agent_id] = {"status": status or "unknown", "gate": gate}

        if not _status_passes(output):
            if gate:
                failed_gates.append(gate)
            continue

        if agent_id == VISUAL_LAYOUT_AGENT:
            visual_failures = _visual_layout_failures(output)
            if visual_failures:
                failed_gates.append(VISUAL_LAYOUT_GATE)
                summary[agent_id]["visualFailures"] = visual_failures

    return missing, sorted(set(failed_gates)), summary


def build_a_to_a_task_contract(
    request_context: dict[str, Any],
    *,
    semantic_asset_route: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the main-agent contract that decides which child agents are mandatory."""

    task_kind, triggered_semantics = _task_kind(request_context, semantic_asset_route)
    manifest = _load_pipeline_manifest()
    registered_agents = _registered_agent_ids(manifest)
    forced = request_context.get("force_effective_required_agents", [])
    forced_agents = [str(agent_id) for agent_id in forced] if isinstance(forced, list) else []
    required_agents = _unique([*_required_agents_for(task_kind), *forced_agents])
    hard_gates = _hard_gates_for(required_agents)
    missing, failed_gates, output_summary = _evaluate_outputs(required_agents, _agent_outputs(request_context))
    self_check = _build_main_agent_self_check(
        request_context,
        task_kind=task_kind,
        triggered_semantics=triggered_semantics,
    )
    awareness_reasons: list[str] = []
    if task_kind in HIGH_RISK_TASK_KINDS and str(self_check.get("status", "")).casefold() not in PASS_STATUSES:
        failed_gates = sorted(set([*failed_gates, MAIN_AGENT_GATE]))
        awareness_reasons.append("main agent self-check failed: " + str(self_check.get("reason", self_check.get("status"))))

    dispatch_decision, awareness_failures, dispatch_awareness_reasons = _build_dispatch_decision(
        request_context,
        task_kind=task_kind,
        triggered_semantics=triggered_semantics,
        effective_required_agents=required_agents,
        registered_agents=registered_agents,
        missing=missing,
        failed_gates=failed_gates,
    )
    if awareness_failures:
        failed_gates = sorted(set([*failed_gates, *awareness_failures]))
    awareness_reasons.extend(dispatch_awareness_reasons)

    blocking_reasons: list[str] = []
    if missing:
        blocking_reasons.append("missing required agent outputs: " + ", ".join(missing))
    if failed_gates:
        blocking_reasons.append("failed hard gates: " + ", ".join(failed_gates))
    blocking_reasons.extend(awareness_reasons)

    return {
        "version": "0.1",
        "kind": "a_to_a_task_contract",
        "taskKind": task_kind,
        "status": "blocked" if blocking_reasons else "ready",
        "triggeredSemantics": triggered_semantics,
        "requiredAgents": required_agents,
        "mainAgentSelfCheck": self_check,
        "dispatchDecision": dispatch_decision,
        "hardGates": hard_gates,
        "missingRequiredAgents": missing,
        "failedHardGates": failed_gates,
        "blockingReasons": blocking_reasons,
        "agentOutputSummary": output_summary,
        "deliveryBoundary": {
            "mayClaimComplete": not blocking_reasons,
            "mustReportBlockedAgentGates": bool(blocking_reasons),
        },
    }
