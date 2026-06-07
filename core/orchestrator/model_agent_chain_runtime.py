"""No-CAD model-agent chain runtime for design-stage collaboration."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from core.model_review.codex_cli_client import CodexCliReviewConfig, Runner
from core.model_review.evidence_portfolio import build_evidence_portfolio
from core.model_review.prompt_library import run_prompt_pack_review
from core.orchestrator.agent_cognition import build_behavior_change_proof
from core.orchestrator.agent_handoff import build_handoff_packet, validate_handoff_packet
from core.orchestrator.orchestrator_host_runtime import run_orchestrator_host_runtime
from core.orchestrator.reviewer_host_runtime import run_reviewer_host_closeout_runtime
from core.orchestrator.rule_context_pack import build_rule_context_pack
from core.orchestrator.run_package_state import advance_run_state
from core.orchestrator.tool_contract import run_tool_intent
from core.runtime.encoding_guard import assert_no_text_encoding_corruption


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHAIN_RESULT_FILE = "model_agent_chain_result.json"
LIVE_COLLAB_PROOF_RESULT_FILE = "model_agent_live_collab_proof_result.json"
LIVE_COLLAB_COMPLETION_AUDIT_FILE = "model_agent_live_collab_completion_audit.json"
LIVE_PROOF_CAD_PLAN_PATH = "candidate_outputs/cad_plan.candidate.json"
MODEL_CHAIN = [
    "pipeline_design_director",
    "pipeline_style_generator",
    "pipeline_design_reviewer",
]
VIRTUAL_COGNITIVE_ROLES = {
    "design_brain": {
        "roleLabel": "Design Brain",
        "memberAgentIds": MODEL_CHAIN,
        "purpose": "Share design-stage evidence and reasoning context while preserving registered Agent responsibilities.",
        "schemaMergeStatus": "not_started",
        "handoffMergeStatus": "not_started",
        "gatePolicy": "preserve_original_agent_ids_schemas_handoffs_and_a_to_a_gates",
    }
}
TASK_TYPES = {
    "pipeline_design_director": "design_director_review",
    "pipeline_style_generator": "style_generation_review",
    "pipeline_design_reviewer": "design_review",
}
SCHEMAS = {
    "pipeline_design_director": "core/model_review/schemas/design_director_review.schema.json",
    "pipeline_style_generator": "core/model_review/schemas/style_generation_review.schema.json",
    "pipeline_design_reviewer": "core/model_review/schemas/design_review.schema.json",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _unique(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _virtual_cognitive_role_manifest() -> dict[str, Any]:
    return {
        "schemaVersion": "virtual-cognitive-roles/v1",
        "status": "spike",
        "roles": [
            {
                "roleId": role_id,
                **role,
                "evidenceBoundary": [
                    "virtual role grouping does not merge schemas",
                    "virtual role grouping does not replace handoff packets",
                    "virtual role grouping does not alter A-to-A hard gates",
                ],
            }
            for role_id, role in VIRTUAL_COGNITIVE_ROLES.items()
        ],
    }


def _virtual_cognitive_role_context(agent_id: str, upstream_outputs: list[dict[str, Any]]) -> dict[str, Any]:
    for role_id, role in VIRTUAL_COGNITIVE_ROLES.items():
        members = [str(item) for item in role.get("memberAgentIds", [])]
        if agent_id not in members:
            continue
        refs: list[str] = ["virtual_cognitive_roles.json"]
        upstream_agent_ids: list[str] = []
        for item in upstream_outputs:
            upstream_agent = str(item.get("agentId") or "")
            if upstream_agent:
                upstream_agent_ids.append(upstream_agent)
            for key in ("path", "handoffPath", "reportPath"):
                value = str(item.get(key) or "")
                if value and value not in refs:
                    refs.append(value)
        return {
            "schemaVersion": "virtual-cognitive-role-context/v1",
            "roleId": role_id,
            "roleLabel": str(role.get("roleLabel") or role_id),
            "currentAgentId": agent_id,
            "memberAgentIds": members,
            "upstreamAgentIds": upstream_agent_ids,
            "sharedContextRefs": refs,
            "purpose": str(role.get("purpose") or ""),
            "preservationPolicy": str(role.get("gatePolicy") or ""),
            "schemaMergeStatus": str(role.get("schemaMergeStatus") or "not_started"),
            "handoffMergeStatus": str(role.get("handoffMergeStatus") or "not_started"),
            "evidenceBoundary": [
                "This is a virtual cognitive grouping only.",
                "Keep each registered Agent's schema, prompt pack, handoff packet, and gate responsibility intact.",
            ],
        }
    return {}


def _request_text(run_dir: Path) -> str:
    user_request = _read_json(run_dir / "user_request.json").get("userRequest", "")
    if isinstance(user_request, dict):
        for key in ("text", "user_request", "request", "prompt"):
            if user_request.get(key):
                return str(user_request[key])
    return str(user_request)


def _request_context(run_dir: Path) -> dict[str, Any]:
    context_pack = _read_json(run_dir / "context_pack.json")
    context = context_pack.get("requestContext") or context_pack.get("request_context")
    return context if isinstance(context, dict) else {}


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def _agent_output_summary(run_dir: Path, agent_id: str) -> dict[str, Any]:
    rel_path = f"agent_outputs/{agent_id}.json"
    path = run_dir / rel_path
    payload = _read_json(path)
    provider = payload.get("modelProviderStatus")
    if not isinstance(provider, dict):
        provider = {}
    summary_parts = [
        str(payload.get("status") or ""),
        str(payload.get("deliveryDecision") or ""),
        str(payload.get("styleDecision") or ""),
        str(payload.get("drawingTypeDecision") or ""),
    ]
    summary = {
        "agentId": agent_id,
        "path": rel_path,
        "status": str(payload.get("status") or "missing"),
        "summary": " ".join(part for part in summary_parts if part),
        "sha256": _sha256(path),
        "modelInvoked": provider.get("modelInvoked", payload.get("modelInvoked")),
        "schemaValid": provider.get("schemaValid", payload.get("schemaValid")),
        "modelUnavailable": provider.get("modelUnavailable", payload.get("modelUnavailable")),
    }
    handoff_rel = f"agent_outputs/{agent_id}.handoff.json"
    handoff_path = run_dir / handoff_rel
    if handoff_path.is_file():
        summary["handoffPath"] = handoff_rel
        summary["handoffSha256"] = _sha256(handoff_path)
    return summary


def _status_passes(output: dict[str, Any]) -> bool:
    provider = output.get("modelProviderStatus")
    if isinstance(provider, dict) and (
        provider.get("modelUnavailable") is True or provider.get("schemaValid") is False or provider.get("blocking") is True
    ):
        return False
    return str(output.get("status") or "").casefold() in {"pass", "ready", "ok"}


def _learning_candidate(agent_id: str, output: dict[str, Any]) -> dict[str, Any]:
    provider = output.get("modelProviderStatus")
    if not isinstance(provider, dict):
        provider = {}
    status = str(output.get("status") or "").casefold()
    needs_review = (
        status in {"fail", "unavailable", "blocked"}
        or provider.get("modelUnavailable") is True
        or provider.get("schemaValid") is False
        or provider.get("blocking") is True
    )
    if not needs_review:
        return {"decision": "not_required"}
    return {
        "decision": "review_required",
        "trigger": "model_fail_or_schema_invalid",
        "responsibleAgentIds": [agent_id],
        "errorPattern": str(output.get("reason") or output.get("stderr") or "model output failed gate")[:240],
        "correctPattern": "Return strict schema-valid JSON with explicit evidenceUsed/evidenceMissing and no CAD authorization.",
        "promptDelta": "Review Prompt Pack boundary rules and required fields for this agent.",
        "checkerDelta": "Keep schema/provider/trace gate checks mandatory before downstream use.",
        "retestOriginalTask": True,
    }


def _ensure_learning_decision(run_dir: Path, agent_id: str, output: dict[str, Any]) -> dict[str, Any]:
    current = output.get("learningCandidate")
    if isinstance(current, dict) and current:
        return output
    updated = dict(output)
    updated["learningCandidate"] = _learning_candidate(agent_id, updated)
    _write_json(run_dir / "agent_outputs" / f"{agent_id}.json", updated)
    return updated


def _handle_tool_intent(
    *,
    run_dir: Path,
    run_id: str,
    agent_id: str,
    output: dict[str, Any],
) -> tuple[list[str], list[str], list[dict[str, Any]], list[dict[str, Any]]]:
    intent = output.get("toolIntent")
    if intent is None:
        return [], [], [], []
    if not isinstance(intent, dict):
        return [f"{agent_id} toolIntent is not a JSON object"], [], [], []
    trace = run_tool_intent(run_dir, intent, run_id=run_id)
    written = [str(trace.get("downstreamArtifactPath") or "")]
    decision = str(trace.get("orchestratorDecision") or "")
    summaries = [
        {
            "agentId": f"{agent_id}:toolIntent",
            "path": str(trace.get("downstreamArtifactPath") or ""),
            "status": decision,
            "summary": str(trace.get("downstreamReadableSummary") or ""),
            "sha256": _sha256(run_dir / str(trace.get("downstreamArtifactPath") or "")),
            "toolName": str(trace.get("toolName") or ""),
            "executionStatus": str(trace.get("executionStatus") or ""),
            "resultStatus": str(trace.get("resultStatus") or (trace.get("result") or {}).get("status") or ""),
            "reportPath": str((trace.get("result") or {}).get("reportPath") or ""),
        }
    ]
    if decision == "blocked":
        reasons = [str(item) for item in trace.get("blockingReasons", []) if str(item)]
        return [f"{agent_id} tool intent blocked: {reason}" for reason in reasons], written, summaries, [trace]
    if decision == "needs_more_evidence":
        return [f"{agent_id} tool intent needs_more_evidence"], written, summaries, [trace]
    return [], written, summaries, [trace]


def _compact_summary(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    keys = (
        "status",
        "resultStatus",
        "toolStage",
        "reportPath",
        "readbackStatus",
        "cadGeometryVerified",
        "savedCurrentDwg",
        "targetLayer",
        "createdHandleCount",
        "orchestratorDecision",
        "executionStatus",
        "blockingReasons",
        "issues",
        "errors",
        "warnings",
    )
    return {key: payload[key] for key in keys if key in payload}


def _decision_snapshot(
    *,
    dispatch_plan: dict[str, Any],
    output: dict[str, Any],
    trace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    tool_choice: list[str] = []
    if trace is not None and trace.get("toolName"):
        tool_choice.append(str(trace.get("toolName")))
    reasons = output.get("blockingReasons")
    return {
        "route": str(dispatch_plan.get("route") or ""),
        "requiredAgents": [str(item) for item in dispatch_plan.get("requiredAgents", [])],
        "toolChoice": tool_choice,
        "blockingReasons": [str(item) for item in reasons] if isinstance(reasons, list) else [],
    }


def _tool_self_correction_context(
    *,
    run_dir: Path,
    agent_id: str,
    round1_output_ref: str,
    trace: dict[str, Any],
) -> dict[str, Any]:
    result = trace.get("result") if isinstance(trace.get("result"), dict) else {}
    report_path = str(result.get("reportPath") or "")
    report = _read_json(run_dir / report_path) if report_path else {}
    trace_ref = str(trace.get("downstreamArtifactPath") or "")
    return {
        "schemaVersion": "tool-self-correction-context/v1",
        "status": "ready",
        "agentId": agent_id,
        "round1OutputRef": round1_output_ref,
        "toolTraceRef": trace_ref,
        "toolIntentId": str(trace.get("toolIntentId") or ""),
        "toolName": str(trace.get("toolName") or ""),
        "orchestratorDecision": str(trace.get("orchestratorDecision") or ""),
        "executionStatus": str(trace.get("executionStatus") or ""),
        "resultStatus": str(trace.get("resultStatus") or result.get("status") or ""),
        "reportPath": report_path,
        "blockingReasons": [str(item) for item in trace.get("blockingReasons", []) if str(item)],
        "toolResultSummary": _compact_summary(result),
        "reportSummary": _compact_summary(report),
        "instructions": [
            "Use this tool result to revise your own previous judgement.",
            "Do not request another tool in this self-correction pass.",
            "Do not override orchestrator blocking reasons with unsupported pass claims.",
        ],
        "evidenceBoundary": [
            "tool trace is orchestrator-owned evidence",
            "self-correction remains no-CAD and cannot authorize save/delete/formal-layer writes",
        ],
    }


def _run_agent_self_correction_after_tool(
    *,
    run_dir: Path,
    agent_id: str,
    request_text: str,
    request_context: dict[str, Any],
    dispatch_plan: dict[str, Any],
    rule_context_pack: dict[str, Any],
    upstream_outputs: list[dict[str, Any]],
    round1_output: dict[str, Any],
    trace: dict[str, Any],
    evidence_portfolio_ref: str | None,
    config: CodexCliReviewConfig,
    runner: Runner | None,
    cwd: str | Path | None,
) -> tuple[dict[str, Any], list[str], list[str]]:
    round1_rel = f"agent_outputs/{agent_id}.round1.json"
    _write_json(run_dir / round1_rel, round1_output)
    context = _tool_self_correction_context(
        run_dir=run_dir,
        agent_id=agent_id,
        round1_output_ref=round1_rel,
        trace=trace,
    )
    extra_refs = [round1_rel]
    if context.get("toolTraceRef"):
        extra_refs.append(str(context["toolTraceRef"]))
    if context.get("reportPath"):
        extra_refs.append(str(context["reportPath"]))
    output = run_prompt_pack_review(
        agent_id=agent_id,
        payload=_payload(
            agent_id=agent_id,
            request_text=request_text,
            request_context=request_context,
            dispatch_plan=dispatch_plan,
            rule_context_pack=rule_context_pack,
            upstream_outputs=upstream_outputs,
            self_correction_context=context,
            extra_evidence_refs=extra_refs,
            evidence_portfolio_ref=evidence_portfolio_ref,
        ),
        run_dir=run_dir,
        output_path=run_dir / "agent_outputs" / f"{agent_id}.json",
        raw_output_path=run_dir / "agent_outputs" / f"{agent_id}.self_correction.raw_model_review.json",
        config=config,
        runner=runner,
        cwd=cwd or PROJECT_ROOT,
        trace_id=f"{agent_id.replace('_', '-')}-self-correction",
    )
    output = _ensure_learning_decision(run_dir, agent_id, output)
    blocking: list[str] = []
    if output.get("toolIntent") is not None:
        blocking.append(f"{agent_id} nested_tool_intent_not_allowed")
        updated = dict(output)
        reasons = [str(item) for item in updated.get("blockingReasons", []) if str(item)] if isinstance(updated.get("blockingReasons"), list) else []
        reasons.append("nested_tool_intent_not_allowed")
        updated["blockingReasons"] = reasons
        _write_json(run_dir / "agent_outputs" / f"{agent_id}.json", updated)
        output = updated
    return output, [round1_rel, f"agent_outputs/{agent_id}.json"], blocking


def _payload(
    *,
    agent_id: str,
    request_text: str,
    request_context: dict[str, Any],
    dispatch_plan: dict[str, Any],
    rule_context_pack: dict[str, Any],
    upstream_outputs: list[dict[str, Any]],
    self_correction_context: dict[str, Any] | None = None,
    extra_evidence_refs: list[str] | None = None,
    evidence_portfolio_ref: str | None = None,
) -> dict[str, Any]:
    rule_pack_ref = f"rule_context_packs/{agent_id}.json"
    upstream_refs = []
    for item in upstream_outputs:
        if item.get("path"):
            upstream_refs.append(str(item.get("path")))
        if item.get("handoffPath"):
            upstream_refs.append(str(item.get("handoffPath")))
    virtual_role_context = _virtual_cognitive_role_context(agent_id, upstream_outputs)
    evidence_refs = [
        "user_request.json",
        "context_pack.json",
        "dispatch_plan.json",
        "virtual_cognitive_roles.json",
        rule_pack_ref,
        *upstream_refs,
        *[str(item) for item in extra_evidence_refs or []],
    ]
    if evidence_portfolio_ref:
        evidence_refs.append(evidence_portfolio_ref)
    return {
        "userRequest": request_text,
        "taskContext": {
            "taskKind": TASK_TYPES.get(agent_id, agent_id),
            "route": dispatch_plan.get("route", "standard_draw"),
            "requestContext": request_context,
            "dispatchPlanRef": "dispatch_plan.json",
            "noCadChain": True,
        },
        "evidenceRefs": _unique(evidence_refs),
        "statePatchRequest": {
            "phase": "orchestrator_reviewed",
            "phaseLabelForUser": "模型型 Agent 只读设计链路",
        },
        "ruleContextPack": rule_context_pack,
        "agentSpecific": {
            "agentId": agent_id,
            "chainRole": TASK_TYPES.get(agent_id, agent_id),
            "dispatchPlan": dispatch_plan,
            "upstreamOutputs": upstream_outputs,
            "upstreamOutputRefs": upstream_refs,
            "upstreamHandoffPackets": [
                {
                    "path": str(item.get("handoffPath")),
                    "sha256": str(item.get("handoffSha256")),
                }
                for item in upstream_outputs
                if item.get("handoffPath")
            ],
            "virtualCognitiveRole": virtual_role_context,
            "selfCorrectionContext": self_correction_context or {},
            "evidencePortfolioRef": evidence_portfolio_ref or "",
            "cadExecutionAuthorized": False,
            "savedCurrentDwg": False,
        },
    }


def _write_deterministic_downstream_outputs(
    *,
    run_dir: Path,
    upstream_outputs: list[dict[str, Any]],
    blocking_reasons: list[str],
) -> list[str]:
    status = "blocked" if blocking_reasons else "ready"
    intent_path = run_dir / "agent_outputs" / "pipeline_intent.json"
    audit_path = run_dir / "agent_outputs" / "pipeline_audit.json"
    delivery_path = run_dir / "agent_outputs" / "pipeline_delivery.chain.json"
    _write_json(
        intent_path,
        {
            "schemaVersion": "no-cad-chain-intent-draft/v1",
            "status": status,
            "cadPlanDraftStatus": "not_executed_no_cad_chain",
            "sourceAgentOutputs": [item.get("path") for item in upstream_outputs],
            "evidenceBundle": {"upstreamOutputs": upstream_outputs},
            "structuredIntentDraft": {
                "kind": "design_stage_intent",
                "cadExecutionAuthorized": False,
                "requiresBeforeCad": ["validate_plan", "dry_run", "created_handles_readback"],
            },
            "blockingReasons": blocking_reasons,
            "evidenceBoundary": [
                "intent draft is upstream context only",
                "does not write CAD",
                "does not prove CAD geometry",
            ],
        },
    )
    _write_json(
        audit_path,
        {
            "schemaVersion": "no-cad-chain-audit/v1",
            "status": "pass" if not blocking_reasons else "fail",
            "evidenceBundle": {"upstreamOutputs": upstream_outputs},
            "checked": [
                "downstream prompt referenced upstream agent_outputs",
                "cadExecutionAuthorized=false",
                "savedCurrentDwg=false",
            ],
            "blockingReasons": blocking_reasons,
            "learningCandidate": {"decision": "not_required" if not blocking_reasons else "review_required"},
        },
    )
    _write_json(
        delivery_path,
        {
            "schemaVersion": "no-cad-chain-delivery/v1",
            "status": status,
            "deliveryDecision": "not_verified" if blocking_reasons else "ready_for_pre_cad_review",
            "evidenceBundle": {"upstreamOutputs": upstream_outputs},
            "allowedClaims": [
                "no-CAD model agent chain produced upstream design context",
                "CAD execution has not run",
            ]
            if not blocking_reasons
            else [],
            "blockingReasons": blocking_reasons,
            "cadExecutionAuthorized": False,
            "savedCurrentDwg": False,
            "evidenceDoesNotProve": [
                "CAD geometry",
                "created handles readback",
                "user acceptance",
                "table C capability increase",
            ],
        },
    )
    return [
        "agent_outputs/pipeline_intent.json",
        "agent_outputs/pipeline_audit.json",
        "agent_outputs/pipeline_delivery.chain.json",
    ]


def _live_proof_cad_plan(*, base_point: list[float] | None = None) -> dict[str, Any]:
    base = list(base_point or [68000.0, 36000.0, 0.0])
    if len(base) == 2:
        base.append(0.0)
    return {
        "version": "0.1",
        "domain": "generic",
        "intent": "draw_object",
        "object": {
            "type": "table",
            "name": "茶几",
            "width": 1200,
            "depth": 600,
        },
        "placement": {
            "mode": "absolute",
            "base_point": [float(base[0]), float(base[1]), float(base[2])],
            "placement_phrase": "MODEL-AGENT-LIVE-COLLAB-PROOF-01 preview-only target",
        },
        "drawing": {
            "layer": "CODEX_PREVIEW",
            "include_label": True,
            "include_dimensions": True,
        },
        "confidence": 0.9,
        "needs_confirmation": False,
    }


def _tool_intent(
    *,
    agent_id: str,
    intent_id: str,
    tool_name: str,
    purpose: str,
    permission_class: str,
    risk_level: str,
    inputs: dict[str, Any],
    target_scope: dict[str, Any],
    expected_evidence: list[str],
    forbidden_effects: list[str],
    requested_effects: list[str] | None = None,
) -> dict[str, Any]:
    intent = {
        "schemaVersion": "tool-intent/v1",
        "toolIntentId": intent_id,
        "requestedByAgentId": agent_id,
        "toolName": tool_name,
        "purpose": purpose,
        "inputs": inputs,
        "targetScope": target_scope,
        "riskLevel": risk_level,
        "permissionClass": permission_class,
        "expectedEvidence": expected_evidence,
        "forbiddenEffects": forbidden_effects,
    }
    if requested_effects:
        intent["requestedEffects"] = requested_effects
    return intent


def _summaries_for(run_dir: Path, agent_ids: list[str]) -> list[dict[str, Any]]:
    return [_agent_output_summary(run_dir, agent_id) for agent_id in agent_ids]


def _detect_live_chain_conflicts(run_dir: Path) -> dict[str, Any]:
    design = _read_json(run_dir / "agent_outputs" / "pipeline_design_director.json")
    style = _read_json(run_dir / "agent_outputs" / "pipeline_style_generator.json")
    conflicts: list[str] = []
    if design.get("status") and not _status_passes(design):
        conflicts.append("pipeline_design_director did not pass")
    if style.get("status") and not _status_passes(style):
        conflicts.append("pipeline_style_generator did not pass")
    candidates = style.get("styleCandidates")
    selected = str(style.get("selectedStyleCandidate") or "")
    if isinstance(candidates, list) and selected:
        candidate_ids = {str(item.get("id")) for item in candidates if isinstance(item, dict) and item.get("id")}
        if candidate_ids and selected not in candidate_ids:
            conflicts.append(f"selected style candidate {selected!r} is not in styleCandidates")
    for payload, agent_id in ((design, "pipeline_design_director"), (style, "pipeline_style_generator")):
        if payload.get("cadExecutionAuthorized") is True or payload.get("savedCurrentDwg") is True:
            conflicts.append(f"{agent_id} tried to authorize CAD or save DWG")
    return {
        "status": "pass" if not conflicts else "fail",
        "checked": [
            "model outputs have pass-like status",
            "style selected candidate is present when candidates are declared",
            "model agent outputs did not authorize CAD or save DWG",
        ],
        "conflicts": conflicts,
    }


def _write_live_visual_intent(
    *,
    run_dir: Path,
    source_outputs: list[dict[str, Any]],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    output = {
        "schemaVersion": "deterministic-visual-intent/v1",
        "status": "blocked" if blocking_reasons else "ready",
        "agentId": "pipeline_visual_intent",
        "sourceAgentOutputs": [str(item.get("path")) for item in source_outputs if item.get("path")],
        "visualParts": [
            {"id": "table-outline", "type": "rectangle", "role": "茶几外轮廓"},
            {"id": "table-label", "type": "text", "role": "中文对象标注"},
            {"id": "table-dimensions", "type": "dimension", "role": "宽深尺寸表达"},
        ],
        "styleTarget": {
            "selectedStyleCandidate": "A",
            "lineColor": "yellow",
            "targetLayer": "CODEX_PREVIEW",
        },
        "cadExecutionAuthorized": False,
        "savedCurrentDwg": False,
        "blockingReasons": blocking_reasons,
        "modelProviderStatus": {
            "modelInvoked": False,
            "route": "deterministic_downstream_agent",
            "schemaValid": True,
            "blocking": bool(blocking_reasons),
        },
    }
    _write_json(run_dir / "agent_outputs" / "pipeline_visual_intent.json", output)
    return output


def _write_live_intent(
    *,
    run_dir: Path,
    cad_plan: dict[str, Any],
    source_outputs: list[dict[str, Any]],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    plan_path = run_dir / LIVE_PROOF_CAD_PLAN_PATH
    _write_json(plan_path, cad_plan)
    output = {
        "schemaVersion": "deterministic-intent/v1",
        "status": "blocked" if blocking_reasons else "ready",
        "agentId": "pipeline_intent",
        "cadPlanDraftStatus": "candidate_written",
        "cadPlanRef": LIVE_PROOF_CAD_PLAN_PATH,
        "sourceAgentOutputs": [str(item.get("path")) for item in source_outputs if item.get("path")],
        "structuredIntentDraft": {
            "kind": "preview_cad_plan_candidate",
            "targetLayer": "CODEX_PREVIEW",
            "cadExecutionAuthorized": False,
            "savedCurrentDwg": False,
            "requiresBeforeCad": ["validate_plan", "dry_run_plan"],
        },
        "blockingReasons": blocking_reasons,
        "modelProviderStatus": {
            "modelInvoked": False,
            "route": "deterministic_downstream_agent",
            "schemaValid": True,
            "blocking": bool(blocking_reasons),
        },
    }
    _write_json(run_dir / "agent_outputs" / "pipeline_intent.json", output)
    return output


def _run_live_proof_tools(run_dir: Path, *, run_id: str, driver_mode: str) -> list[dict[str, Any]]:
    validate_trace = run_tool_intent(
        run_dir,
        _tool_intent(
            agent_id="pipeline_audit",
            intent_id="intent-validate-cad-plan",
            tool_name="validate_plan",
            purpose="validate live-collab CAD_PLAN candidate before any preview CAD execution",
            permission_class="deterministic_verify",
            risk_level="low",
            inputs={"planPath": LIVE_PROOF_CAD_PLAN_PATH},
            target_scope={"scopeType": "run_artifact", "targetPath": LIVE_PROOF_CAD_PLAN_PATH},
            expected_evidence=["cad_reports/validation_report.json"],
            forbidden_effects=["cad_write", "dwg_save", "delete_entities"],
        ),
        run_id=run_id,
    )
    dry_run_trace = run_tool_intent(
        run_dir,
        _tool_intent(
            agent_id="pipeline_audit",
            intent_id="intent-dry-run-cad-plan",
            tool_name="dry_run_plan",
            purpose="dry-run live-collab CAD_PLAN candidate before preview CAD execution",
            permission_class="deterministic_verify",
            risk_level="low",
            inputs={"planPath": LIVE_PROOF_CAD_PLAN_PATH},
            target_scope={"scopeType": "run_artifact", "targetPath": LIVE_PROOF_CAD_PLAN_PATH},
            expected_evidence=["cad_reports/dry_run_report.json"],
            forbidden_effects=["cad_write", "dwg_save", "delete_entities"],
        ),
        run_id=run_id,
    )
    preview_trace = run_tool_intent(
        run_dir,
        _tool_intent(
            agent_id="pipeline_intent",
            intent_id="intent-preview-cad-execute",
            tool_name="preview_cad_execute",
            purpose="execute live-collab CAD_PLAN through controlled CODEX_PREVIEW preview CAD tool",
            permission_class="cad_preview",
            risk_level="high",
            inputs={"planPath": LIVE_PROOF_CAD_PLAN_PATH, "driverMode": driver_mode},
            target_scope={
                "scopeType": "run_artifact",
                "targetPath": LIVE_PROOF_CAD_PLAN_PATH,
                "targetLayer": "CODEX_PREVIEW",
                "previewOnly": True,
                "savedCurrentDwg": False,
            },
            expected_evidence=[
                "cad_reports/execution_summary.json",
                "cad_reports/readback_summary.json",
                "cad_reports/cad_preview_tool_report.json",
            ],
            requested_effects=["cad_preview_write"],
            forbidden_effects=["dwg_save", "delete_entities", "cad_write_formal_layer"],
        ),
        run_id=run_id,
    )
    return [validate_trace, dry_run_trace, preview_trace]


def _trace_summary(trace: dict[str, Any]) -> dict[str, Any]:
    return {
        "agentId": f"{trace.get('requestedByAgentId')}:toolIntent",
        "path": str(trace.get("downstreamArtifactPath") or ""),
        "status": str(trace.get("orchestratorDecision") or ""),
        "summary": str(trace.get("downstreamReadableSummary") or ""),
        "sha256": "",
        "toolName": str(trace.get("toolName") or ""),
        "executionStatus": str(trace.get("executionStatus") or ""),
        "resultStatus": str((trace.get("result") or {}).get("status") or ""),
        "reportPath": str((trace.get("result") or {}).get("reportPath") or ""),
    }


def _write_live_audit(
    *,
    run_dir: Path,
    upstream_outputs: list[dict[str, Any]],
    conflict_report: dict[str, Any],
    tool_traces: list[dict[str, Any]],
) -> dict[str, Any]:
    trace_outputs = [_trace_summary(trace) for trace in tool_traces]
    blocking_reasons = [str(item) for item in conflict_report.get("conflicts", []) if str(item)]
    for trace in tool_traces:
        if str(trace.get("orchestratorDecision") or "") == "blocked":
            blocking_reasons.extend(str(item) for item in trace.get("blockingReasons", []) if str(item))
    output = {
        "schemaVersion": "deterministic-live-collab-audit/v1",
        "status": "fail" if blocking_reasons else "pass",
        "agentId": "pipeline_audit",
        "evidenceBundle": {"upstreamOutputs": [*upstream_outputs, *trace_outputs]},
        "checked": [
            "downstream agents referenced upstream agent_outputs JSON",
            "validate_plan and dry_run_plan ran before preview CAD execution",
            "controlled CAD execution stayed under CODEX_PREVIEW contract",
            "savedCurrentDwg=false is delegated to CAD preview tool report/readback",
        ],
        "conflictHandling": conflict_report,
        "blockingReasons": list(dict.fromkeys(blocking_reasons)),
        "learningCandidate": {"decision": "not_required" if not blocking_reasons else "review_required"},
        "modelProviderStatus": {
            "modelInvoked": False,
            "route": "deterministic_downstream_agent",
            "schemaValid": True,
            "blocking": bool(blocking_reasons),
        },
    }
    _write_json(run_dir / "agent_outputs" / "pipeline_audit.json", output)
    return output


def _live_status(*, cad_report: dict[str, Any], closeout: dict[str, Any], conflict_report: dict[str, Any]) -> str:
    if conflict_report.get("status") != "pass" and cad_report.get("cadGeometryVerified") is True:
        return "cad_geometry_verified_model_chain_blocked"
    if closeout.get("can_deliver") is True:
        return "ready_for_delivery"
    if cad_report.get("cadGeometryVerified") is True:
        return "cad_geometry_verified_closeout_blocked"
    return "not_verified"


def _path_exists(run_dir: Path, rel_path: str) -> bool:
    return (run_dir / rel_path).is_file()


def _requirement(status: str, *, evidence: list[str], missing: list[str] | None = None, notes: list[str] | None = None) -> dict[str, Any]:
    return {
        "status": status,
        "evidence": evidence,
        "missing": missing or [],
        "notes": notes or [],
    }


def write_model_agent_live_collab_completion_audit(run_dir: str | Path) -> dict[str, Any]:
    """Write a requirement-by-requirement audit for the live collaboration proof."""

    run_root = Path(run_dir)
    result = _read_json(run_root / LIVE_COLLAB_PROOF_RESULT_FILE)
    closeout = _read_json(run_root / "closeout_decision.json")
    cad_report = _read_json(run_root / "cad_reports" / "cad_preview_tool_report.json")
    readback = _read_json(run_root / "cad_reports" / "readback_summary.json")
    agent_outputs = result.get("agentOutputChain", [])
    output_by_agent = {
        str(item.get("agentId")): item
        for item in agent_outputs
        if isinstance(item, dict) and item.get("agentId")
    }
    model_agents = ["pipeline_design_director", "pipeline_style_generator", "pipeline_design_reviewer"]
    downstream_agents = ["pipeline_visual_intent", "pipeline_intent", "pipeline_audit", "pipeline_delivery"]
    live_model_invoked = all(
        output_by_agent.get(agent_id, {}).get("modelInvoked") is True
        and output_by_agent.get(agent_id, {}).get("schemaValid") is True
        and output_by_agent.get(agent_id, {}).get("modelUnavailable") is not True
        for agent_id in model_agents
    )
    model_decision_blockers = [
        f"{agent_id} status={output_by_agent.get(agent_id, {}).get('status')}"
        for agent_id in model_agents
        if str(output_by_agent.get(agent_id, {}).get("status") or "").casefold() not in {"pass", "ready", "ok"}
    ]
    downstream_files = [f"agent_outputs/{agent_id}.json" for agent_id in downstream_agents]
    downstream_written = all(_path_exists(run_root, path) for path in downstream_files)
    trace_files = [
        "tool_traces/pipeline_audit.intent-validate-cad-plan.json",
        "tool_traces/pipeline_audit.intent-dry-run-cad-plan.json",
        "tool_traces/pipeline_intent.intent-preview-cad-execute.json",
    ]
    tool_traces_written = all(_path_exists(run_root, path) for path in trace_files)
    cad_validated = (
        cad_report.get("cadGeometryVerified") is True
        and readback.get("readbackStatus") == "ok"
        and readback.get("created_handles_readback") == "ok"
        and readback.get("savedCurrentDwg") is False
        and readback.get("targetLayer") == "CODEX_PREVIEW"
    )
    closeout_deliverable = closeout.get("can_deliver") is True
    screenshots = closeout.get("evidence_boundary", {}).get("screenshots", {})
    screenshot_count = int(screenshots.get("count") or 0) if isinstance(screenshots, dict) else 0
    requirements = {
        "liveModelAgentInvocation": _requirement(
            "achieved" if live_model_invoked else "blocked",
            evidence=[f"agent_outputs/{agent_id}.json" for agent_id in model_agents],
            missing=[]
            if live_model_invoked
            else [
                "schema-valid modelInvoked=true output for pipeline_design_director",
                "schema-valid modelInvoked=true output for pipeline_style_generator",
                "schema-valid modelInvoked=true output for pipeline_design_reviewer",
            ],
            notes=[
                "Invocation achieved means provider call + schema validation succeeded; business pass/fail is tracked by chain status.",
                *model_decision_blockers,
            ]
            if live_model_invoked
            else [
                "Do not treat deterministic or provider-unavailable outputs as live model collaboration.",
                "External model invocation was not available in the final local run.",
            ],
        ),
        "downstreamAgentJsonHandoff": _requirement(
            "achieved" if downstream_written else "missing",
            evidence=downstream_files,
            missing=[] if downstream_written else [path for path in downstream_files if not _path_exists(run_root, path)],
            notes=["pipeline_visual_intent/pipeline_intent/pipeline_audit are deterministic downstream outputs in this proof."],
        ),
        "schemaTraceAndConflictHandling": _requirement(
            "achieved" if tool_traces_written and result.get("conflictHandling") else "missing",
            evidence=[*trace_files, LIVE_COLLAB_PROOF_RESULT_FILE],
            missing=[] if tool_traces_written else [path for path in trace_files if not _path_exists(run_root, path)],
            notes=["Conflict handling stays fail/blocking when model outputs are unavailable."],
        ),
        "realCadPreviewValidation": _requirement(
            "achieved" if cad_validated else "blocked",
            evidence=[
                "cad_reports/validation_report.json",
                "cad_reports/dry_run_report.json",
                "cad_reports/cad_preview_tool_report.json",
                "cad_reports/readback_summary.json",
            ],
            missing=[] if cad_validated else ["created_handles_readback=ok", "cadGeometryVerified=true", "savedCurrentDwg=false"],
            notes=["Real CAD proof is scoped to created handles on CODEX_PREVIEW; it does not prove user acceptance."],
        ),
        "closeoutDeliveryClaim": _requirement(
            "achieved" if closeout_deliverable else "blocked",
            evidence=["closeout_decision.json", "agent_outputs/pipeline_delivery.json"],
            missing=[str(item) for item in closeout.get("blocking_reasons", []) if str(item)] if not closeout_deliverable else [],
            notes=["A blocked closeout is correct when visual acceptance or neighbor protection is missing."],
        ),
        "screenshotVisualAid": _requirement(
            "achieved" if screenshot_count > 0 else "missing",
            evidence=[str(path) for path in screenshots.get("files", [])] if isinstance(screenshots, dict) else [],
            missing=[] if screenshot_count > 0 else ["screenshots/preview.png"],
            notes=["Screenshot is visual_aid_only and cannot replace handle readback or visual acceptance review."],
        ),
    }
    incomplete = {
        key: value
        for key, value in requirements.items()
        if value.get("status") != "achieved"
    }
    audit = {
        "schemaVersion": "model-agent-live-collab-completion-audit/v1",
        "status": "complete" if not incomplete else "not_complete",
        "runId": str(result.get("runId") or run_root.name),
        "requirements": requirements,
        "blockingRequirements": sorted(incomplete.keys()),
        "logicAssessment": {
            "status": "correctly_blocking" if incomplete else "deliverable",
            "summary": (
                "The logic correctly allows real preview CAD validation while preventing delivery claims "
                "when live model outputs, visual acceptance, or neighbor protection evidence are missing."
                if incomplete
                else "All required proof gates are satisfied for this run package."
            ),
        },
        "generatedAt": _utc_now(),
    }
    _write_json(run_root / LIVE_COLLAB_COMPLETION_AUDIT_FILE, audit)
    if result:
        result["completionAudit"] = {
            "path": LIVE_COLLAB_COMPLETION_AUDIT_FILE,
            "status": audit["status"],
            "blockingRequirements": audit["blockingRequirements"],
        }
        _write_json(run_root / LIVE_COLLAB_PROOF_RESULT_FILE, result)
    return audit


def run_model_agent_live_collab_proof(
    run_dir: str | Path,
    *,
    config: CodexCliReviewConfig | None = None,
    runner: Runner | None = None,
    cwd: str | Path | None = None,
    driver_mode: str = "autocad_existing",
    base_point: list[float] | None = None,
    continue_cad_on_model_blocked: bool = False,
) -> dict[str, Any]:
    """Run model-agent collaboration proof and then a controlled preview-CAD check.

    The model portion proves downstream JSON handoff. The CAD portion is
    orchestrator-owned and preview-only; it does not save or delete.
    """

    run_root = Path(run_dir)
    chain_result = run_no_cad_model_agent_chain(run_root, config=config, runner=runner, cwd=cwd)
    run_id = str(chain_result.get("runId") or run_root.name)
    model_agent_outputs = _summaries_for(
        run_root,
        ["pipeline_design_director", "pipeline_style_generator", "pipeline_design_reviewer"],
    )
    conflict_report = _detect_live_chain_conflicts(run_root)
    blocking_reasons = [str(item) for item in conflict_report.get("conflicts", []) if str(item)]

    visual_intent = _write_live_visual_intent(
        run_dir=run_root,
        source_outputs=model_agent_outputs,
        blocking_reasons=blocking_reasons,
    )
    visual_intent_summary = _agent_output_summary(run_root, "pipeline_visual_intent")
    cad_plan = _live_proof_cad_plan(base_point=base_point)
    encoding_preflight = assert_no_text_encoding_corruption(_request_text(run_root), visual_intent, cad_plan)
    intent_output = _write_live_intent(
        run_dir=run_root,
        cad_plan=cad_plan,
        source_outputs=[*model_agent_outputs, visual_intent_summary],
        blocking_reasons=blocking_reasons,
    )
    intent_summary = _agent_output_summary(run_root, "pipeline_intent")

    tool_traces: list[dict[str, Any]] = []
    cad_continuation_policy = {
        "mode": "normal_after_model_chain_pass" if not blocking_reasons else "blocked_before_cad",
        "modelBlockingReasons": blocking_reasons,
        "cadToolsRan": False,
    }
    if blocking_reasons and not continue_cad_on_model_blocked:
        cad_report = {
            "status": "not_verified",
            "resultStatus": "blocked",
            "driverMode": driver_mode,
            "cadGeometryVerified": False,
            "savedCurrentDwg": False,
            "blockingReasons": blocking_reasons,
        }
    else:
        if blocking_reasons:
            cad_continuation_policy["mode"] = "explicit_continue_after_model_block"
        tool_traces = _run_live_proof_tools(run_root, run_id=run_id, driver_mode=driver_mode)
        cad_continuation_policy["cadToolsRan"] = True
        cad_report = _read_json(run_root / "cad_reports" / "cad_preview_tool_report.json")

    audit_output = _write_live_audit(
        run_dir=run_root,
        upstream_outputs=[*model_agent_outputs, visual_intent_summary, intent_summary],
        conflict_report=conflict_report,
        tool_traces=tool_traces,
    )
    audit_summary = _agent_output_summary(run_root, "pipeline_audit")
    reviewer_result = run_reviewer_host_closeout_runtime(
        run_root,
        config=CodexCliReviewConfig(enabled=False),
        cwd=cwd or PROJECT_ROOT,
    )
    delivery_summary = _agent_output_summary(run_root, "pipeline_delivery")
    closeout = reviewer_result["closeoutDecision"]
    status = _live_status(cad_report=cad_report, closeout=closeout, conflict_report=conflict_report)
    result = {
        "schemaVersion": "model-agent-live-collab-proof-result/v1",
        "status": status,
        "runId": run_id,
        "modelChainStatus": chain_result.get("status"),
        "agentOutputChain": [
            *model_agent_outputs,
            visual_intent_summary,
            intent_summary,
            audit_summary,
            delivery_summary,
        ],
        "cadProof": {
            "status": cad_report.get("status"),
            "resultStatus": cad_report.get("resultStatus"),
            "driverMode": cad_report.get("driverMode", driver_mode),
            "createdHandleCount": cad_report.get("createdHandleCount", 0),
            "readbackStatus": cad_report.get("readbackStatus", ""),
            "readbackEntityCount": cad_report.get("readbackEntityCount", 0),
            "cadGeometryVerified": cad_report.get("cadGeometryVerified") is True,
            "savedCurrentDwg": cad_report.get("savedCurrentDwg") is True,
            "reportPath": "cad_reports/cad_preview_tool_report.json",
        },
        "encodingPreflight": encoding_preflight,
        "conflictHandling": conflict_report,
        "cadContinuationPolicy": cad_continuation_policy,
        "closeoutEvidence": {
            "status": closeout.get("status"),
            "canDeliver": closeout.get("can_deliver") is True,
            "blockingReasons": [str(item) for item in closeout.get("blocking_reasons", []) if str(item)],
            "evidenceBoundary": closeout.get("evidence_boundary", {}),
        },
        "writtenFiles": [
            CHAIN_RESULT_FILE,
            "agent_outputs/pipeline_visual_intent.json",
            "agent_outputs/pipeline_intent.json",
            "agent_outputs/pipeline_audit.json",
            "agent_outputs/pipeline_delivery.json",
            LIVE_PROOF_CAD_PLAN_PATH,
            "cad_reports/validation_report.json",
            "cad_reports/dry_run_report.json",
            "cad_reports/cad_preview_tool_report.json",
            "cad_reports/execution_summary.json",
            "cad_reports/readback_summary.json",
            "closeout_decision.json",
            "final_report.md",
            LIVE_COLLAB_COMPLETION_AUDIT_FILE,
        ],
        "evidenceBoundary": [
            "design_director/style_generator/design_reviewer are model-backed when modelProviderStatus.modelInvoked=true",
            "pipeline_visual_intent/pipeline_intent/pipeline_audit are deterministic downstream agents in this proof",
            "CAD execution is controlled by tool_contract, not by model output",
            "savedCurrentDwg=false is required; user acceptance and table C increase are not proven",
        ],
        "generatedAt": _utc_now(),
    }
    _write_json(run_root / LIVE_COLLAB_PROOF_RESULT_FILE, result)
    completion_audit = write_model_agent_live_collab_completion_audit(run_root)
    result["completionAudit"] = {
        "path": LIVE_COLLAB_COMPLETION_AUDIT_FILE,
        "status": completion_audit["status"],
        "blockingRequirements": completion_audit["blockingRequirements"],
    }
    if status == "ready_for_delivery":
        advance_run_state(run_root, "ready_for_delivery", input_files=["user_request.json", "context_pack.json"], output_files=result["writtenFiles"])
    else:
        advance_run_state(
            run_root,
            "blocked",
            input_files=["user_request.json", "context_pack.json"],
            output_files=result["writtenFiles"],
            blocking_reason="; ".join(result["closeoutEvidence"]["blockingReasons"]),
        )
    _write_json(run_root / LIVE_COLLAB_PROOF_RESULT_FILE, result)
    write_model_agent_live_collab_completion_audit(run_root)
    return result


def run_no_cad_model_agent_chain(
    run_dir: str | Path,
    *,
    config: CodexCliReviewConfig | None = None,
    runner: Runner | None = None,
    cwd: str | Path | None = None,
) -> dict[str, Any]:
    """Run the first no-CAD design collaboration chain with upstream JSON refs."""

    run_root = Path(run_dir)
    cfg = config or CodexCliReviewConfig.from_environment()
    request_text = _request_text(run_root)
    request_context = _request_context(run_root)
    orchestrator_result = run_orchestrator_host_runtime(run_root, config=cfg, runner=runner, cwd=cwd)
    dispatch_plan = orchestrator_result["dispatchPlan"]
    run_id = str(dispatch_plan.get("runId") or run_root.name)

    upstream_outputs: list[dict[str, Any]] = []
    if (run_root / "agent_outputs" / "pipeline_orchestrator.json").is_file():
        upstream_outputs.append(_agent_output_summary(run_root, "pipeline_orchestrator"))

    blocking_reasons: list[str] = []
    cognitive_loop_events: list[dict[str, Any]] = []
    written_files = [
        "dispatch_plan.json",
        "task_contract.json",
        "required_agents.json",
        "risk_assessment.json",
        "rule_context_pack.json",
        "virtual_cognitive_roles.json",
    ]
    _write_json(run_root / "virtual_cognitive_roles.json", _virtual_cognitive_role_manifest())
    portfolio = build_evidence_portfolio(
        run_dir=run_root,
        user_request=request_text,
        route=str(dispatch_plan.get("route") or ""),
        task_kind=str(dispatch_plan.get("taskKind") or ""),
        hard_gates=[str(item) for item in dispatch_plan.get("hardGates", [])],
        evidence_refs=[
            "dispatch_plan.json",
            "task_contract.json",
            "required_agents.json",
            "risk_assessment.json",
            "rule_context_pack.json",
        ],
        memory_refs=[],
        history_refs=["docs/status/issues.md"],
    )
    evidence_portfolio_ref = str(portfolio.get("portfolioRef") or "")
    if evidence_portfolio_ref:
        written_files.append(evidence_portfolio_ref)
    if portfolio.get("status") == "blocked":
        blocking_reasons.extend(str(item) for item in portfolio.get("blockingReasons", []))

    for index, agent_id in enumerate(MODEL_CHAIN):
        rule_pack = build_rule_context_pack(
            run_id=str(dispatch_plan.get("runId") or run_root.name),
            agent_id=agent_id,
            task_kind=TASK_TYPES[agent_id],
            trigger_signals=["design_judgment", "multi_agent_chain", "no_cad_preflight"],
            retrieval_queries=[request_text, agent_id, TASK_TYPES[agent_id]],
            schemas=[SCHEMAS[agent_id]],
            hard_gates=list(dispatch_plan.get("hardGates", [])),
            forbidden_actions=["cad_write", "dwg_save", "delete_entities", "table_c_claim"],
            evidence_bundle={
                "cadPlan": None,
                "readback": None,
                "screenshot": None,
                "upstreamOutputs": upstream_outputs,
            },
            upstream_outputs=upstream_outputs,
        )
        rule_pack_rel = f"rule_context_packs/{agent_id}.json"
        _write_json(run_root / rule_pack_rel, rule_pack)
        written_files.append(rule_pack_rel)
        if rule_pack["status"] != "ready":
            blocking_reasons.extend(str(item) for item in rule_pack.get("missingContext", []))

        output = run_prompt_pack_review(
            agent_id=agent_id,
            payload=_payload(
                agent_id=agent_id,
                request_text=request_text,
                request_context=request_context,
                dispatch_plan=dispatch_plan,
                rule_context_pack=rule_pack,
                upstream_outputs=upstream_outputs,
                evidence_portfolio_ref=evidence_portfolio_ref,
            ),
            run_dir=run_root,
            output_path=run_root / "agent_outputs" / f"{agent_id}.json",
            config=cfg,
            runner=runner,
            cwd=cwd or PROJECT_ROOT,
            trace_id=agent_id.replace("_", "-"),
        )
        output = _ensure_learning_decision(run_root, agent_id, output)
        written_files.append(f"agent_outputs/{agent_id}.json")
        output_path = run_root / "agent_outputs" / f"{agent_id}.json"
        tool_blocking, tool_written, tool_summaries, tool_traces = _handle_tool_intent(
            run_dir=run_root,
            run_id=run_id,
            agent_id=agent_id,
            output=output,
        )
        blocking_reasons.extend(tool_blocking)
        written_files.extend(path for path in tool_written if path)
        upstream_outputs.extend(summary for summary in tool_summaries if summary.get("path"))
        if tool_traces:
            round1_output = dict(output)
            trace = tool_traces[0]
            output, correction_written, correction_blocking = _run_agent_self_correction_after_tool(
                run_dir=run_root,
                agent_id=agent_id,
                request_text=request_text,
                request_context=request_context,
                dispatch_plan=dispatch_plan,
                rule_context_pack=rule_pack,
                upstream_outputs=upstream_outputs,
                round1_output=round1_output,
                trace=trace,
                evidence_portfolio_ref=evidence_portfolio_ref,
                config=cfg,
                runner=runner,
                cwd=cwd,
            )
            written_files.extend(correction_written)
            blocking_reasons.extend(correction_blocking)
            output_path = run_root / "agent_outputs" / f"{agent_id}.json"
            proof = build_behavior_change_proof(
                agent_id=agent_id,
                before_decision=_decision_snapshot(dispatch_plan=dispatch_plan, output=round1_output, trace=trace),
                after_decision=_decision_snapshot(dispatch_plan=dispatch_plan, output=output, trace=trace),
                memory_applied_in_future_run=False,
                retested_original_task=False,
            )
            cognitive_loop_events.append(
                {
                    "schemaVersion": "agent-cognitive-loop-event/v1",
                    "agentId": agent_id,
                    "roundCount": 2,
                    "maxRounds": 2,
                    "toolName": str(trace.get("toolName") or ""),
                    "toolTraceRef": str(trace.get("downstreamArtifactPath") or ""),
                    "round1Decision": str(round1_output.get("decision") or round1_output.get("status") or ""),
                    "finalDecision": str(output.get("decision") or output.get("status") or ""),
                    "decisionChanged": str(round1_output.get("decision") or round1_output.get("status") or "")
                    != str(output.get("decision") or output.get("status") or ""),
                    "changedBlockingReason": proof["changedBlockingReason"],
                    "behaviorChangeProof": proof,
                    "evidenceBoundary": [
                        "self-correction is no-CAD",
                        "tool trace is orchestrator-owned evidence",
                        "behavior proof does not replace CAD validation/readback",
                    ],
                }
            )
        to_agent_ids = MODEL_CHAIN[index + 1 :] or ["pipeline_intent", "pipeline_audit", "pipeline_delivery"]
        handoff_packet = build_handoff_packet(
            output,
            from_agent_id=agent_id,
            to_agent_ids=to_agent_ids,
            source_path=output_path,
        )
        handoff_validation = validate_handoff_packet(handoff_packet)
        handoff_rel = f"agent_outputs/{agent_id}.handoff.json"
        _write_json(run_root / handoff_rel, handoff_packet)
        written_files.append(handoff_rel)
        if handoff_validation["status"] != "pass":
            blocking_reasons.append(f"handoff_invalid: {agent_id}")
        if not _status_passes(output):
            blocking_reasons.append(f"{agent_id} model output not pass")
        upstream_outputs.append(_agent_output_summary(run_root, agent_id))

    written_files.extend(
        _write_deterministic_downstream_outputs(
            run_dir=run_root,
            upstream_outputs=upstream_outputs,
            blocking_reasons=blocking_reasons,
        )
    )
    status = "blocked" if blocking_reasons else "ready"
    result = {
        "schemaVersion": "no-cad-model-agent-chain-result/v1",
        "status": status,
        "runId": str(dispatch_plan.get("runId") or run_root.name),
        "route": dispatch_plan.get("route"),
        "agentsCalled": MODEL_CHAIN,
        "virtualCognitiveRolesRef": "virtual_cognitive_roles.json",
        "upstreamOutputs": upstream_outputs,
        "cognitiveLoopSummary": {
            "schemaVersion": "agent-cognitive-loop-summary/v1",
            "status": "observed" if cognitive_loop_events else "not_triggered",
            "roundCount": 2 if cognitive_loop_events else 1,
            "maxRounds": 2,
            "events": cognitive_loop_events,
            "toolTraceRefs": [str(item.get("toolTraceRef") or "") for item in cognitive_loop_events if item.get("toolTraceRef")],
            "evidenceBoundary": [
                "cognitive loop summary is no-CAD",
                "no save/delete/formal-layer permission is implied",
            ],
        },
        "blockingReasons": blocking_reasons,
        "cadExecutionAuthorized": False,
        "savedCurrentDwg": False,
        "nextCadPreflight": ["validate_plan", "dry_run", "created_handles_readback"],
        "evidenceBoundary": [
            "model chain is no-CAD and no-save",
            "model pass does not replace CAD readback",
            "output can only feed a later CAD_PLAN/intent preflight",
        ],
        "writtenFiles": written_files,
        "generatedAt": _utc_now(),
    }
    _write_json(run_root / CHAIN_RESULT_FILE, result)
    written_files.append(CHAIN_RESULT_FILE)
    if status == "ready":
        advance_run_state(run_root, "dispatch_ready", input_files=["user_request.json", "context_pack.json"], output_files=written_files)
    else:
        advance_run_state(
            run_root,
            "blocked",
            input_files=["user_request.json", "context_pack.json"],
            output_files=written_files,
            blocking_reason="; ".join(blocking_reasons),
        )
    return result
