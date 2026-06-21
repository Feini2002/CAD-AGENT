"""Tool Contract ReAct gates for model-backed pipeline agents.

Model-backed agents may request tools by emitting a ``toolIntent`` object, but
the orchestrator owns execution. This module validates, records, and executes
only allowlisted read-only, run-local safe-generation, deterministic
verification, and controlled preview-CAD tools. It never executes shell, save,
delete, registry, training-source, table-C, or formal-layer writes.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any


TOOL_INTENT_SCHEMA_VERSION = "tool-intent/v1"
TOOL_TRACE_SCHEMA_VERSION = "tool-trace/v1"
TOOL_INTENT_SCHEMA_PATH = "core/schemas/tool_intent.schema.json"
TOOL_TRACE_SCHEMA_PATH = "core/schemas/tool_trace.schema.json"
PROJECT_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_TOOL_INTENT_FIELDS = {
    "schemaVersion",
    "toolIntentId",
    "requestedByAgentId",
    "toolName",
    "purpose",
    "inputs",
    "targetScope",
    "riskLevel",
    "permissionClass",
    "expectedEvidence",
    "forbiddenEffects",
}

READ_ONLY_TOOLS = {
    "read_run_package",
    "read_rule_context",
    "read_schema",
    "read_agent_output",
    "read_trace_summary",
}
READ_ONLY_PERMISSION_CLASSES = {"read_only"}
SAFE_GENERATE_TOOLS = {
    "write_agent_output_candidate",
    "write_draft_intent_candidate",
    "write_cad_plan_candidate",
    "write_learning_candidate",
}
SAFE_GENERATE_PERMISSION_CLASSES = {"safe_generate"}
DETERMINISTIC_VERIFY_TOOLS = {
    "validate_plan",
    "dry_run",
    "dry_run_plan",
    "preview_only_audit",
    "closeout_gate",
}
DETERMINISTIC_VERIFY_PERMISSION_CLASSES = {"deterministic_verify"}
CONTROLLED_CAD_TOOLS = {
    "preview_cad_execute",
    "execute_cad_plan_preview",
}
CONTROLLED_CAD_PERMISSION_CLASSES = {"cad_preview"}
HIGH_RISK_LEVELS = {"high", "critical"}
FORBIDDEN_DIRECT_TOOL_NAMES = {
    "save_dwg",
    "save_current_dwg",
    "dwg_save",
    "delete_entities",
    "delete_or_replace_entities",
    "modify_formal_layer",
    "write_formal_layer",
}
FORBIDDEN_DIRECT_EFFECTS = {
    "dwg_save",
    "save_current_dwg",
    "delete_entities",
    "modify_formal_layer",
    "cad_write_formal_layer",
    "table_c_claim",
    "registry_mutation",
    "training_source_mutation",
}
RUN_LOCAL_WRITE_ROOT = "candidate_outputs"
VALIDATION_REPORT_PATH = "cad_reports/validation_report.json"
DRY_RUN_REPORT_PATH = "cad_reports/dry_run_report.json"
PREVIEW_ONLY_AUDIT_REPORT_PATH = "cad_reports/preview_only_audit.json"
CAD_EXECUTION_SUMMARY_PATH = "cad_reports/execution_summary.json"
CAD_READBACK_SUMMARY_PATH = "cad_reports/readback_summary.json"
CAD_PREVIEW_TOOL_REPORT_PATH = "cad_reports/cad_preview_tool_report.json"
CLOSEOUT_DECISION_PATH = "closeout_decision.json"
PASS_STATUSES = {"pass", "ok", "ready", "valid", "executed"}
FAKE_DRIVER_MODES = {"fake", "fake_driver", "fake_preview", "fake_driver_preflight"}
AUTOCAD_EXISTING_DRIVER_MODES = {"autocad_existing", "active_autocad", "autocad_com_existing"}
CAD_SESSION_HOST_DRIVER_MODES = {"cad_session_host", "cad-session-host", "session_host"}
DEFAULT_CONTROLLED_CAD_DRIVER_MODE = "cad_session_host"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "unavailable", "reason": str(exc)}
    return value if isinstance(value, dict) else {"status": "unavailable", "reason": "JSON value was not an object"}


def _text_items(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return [str(value)] if str(value) else []


def _decoded_inputs(intent: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(intent.get("inputs")) if isinstance(intent.get("inputs"), dict) else {}
    for json_key, object_key in (("payloadJson", "payload"), ("auditJson", "audit")):
        if isinstance(inputs.get(object_key), dict):
            continue
        raw = inputs.get(json_key)
        if isinstance(raw, str) and raw.strip():
            try:
                decoded = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if isinstance(decoded, dict):
                inputs[object_key] = decoded
    return inputs


def _missing_required_fields(intent: dict[str, Any]) -> list[str]:
    return sorted(field for field in REQUIRED_TOOL_INTENT_FIELDS if field not in intent)


def _target_scope_missing(target_scope: Any) -> bool:
    if not isinstance(target_scope, dict):
        return True
    scope_type = str(target_scope.get("scopeType") or "").strip().casefold()
    if not scope_type or scope_type in {"unknown", "unspecified", "all", "whole_modelspace"}:
        return True
    evidence_keys = ("targetLayer", "targetHandles", "targetPath", "scopeRef", "bbox")
    return not any(target_scope.get(key) for key in evidence_keys)


def _safe_rel_fragment(value: str) -> str:
    allowed = []
    for char in str(value):
        if char.isalnum() or char in {"_", "-", "."}:
            allowed.append(char)
        else:
            allowed.append("_")
    text = "".join(allowed).strip("._")
    return text or "candidate"


def _resolve_under(root: Path, rel_path: str) -> Path:
    base = Path(root).resolve()
    target = (base / str(rel_path)).resolve()
    if not target.is_relative_to(base):
        raise ValueError(f"path escapes run directory: {rel_path}")
    return target


def _safe_schema_path(schema_ref: str) -> Path:
    target = (PROJECT_ROOT / str(schema_ref)).resolve()
    allowed_roots = [
        (PROJECT_ROOT / "core" / "schemas").resolve(),
        (PROJECT_ROOT / "core" / "model_review" / "schemas").resolve(),
    ]
    if not any(target.is_relative_to(root) for root in allowed_roots):
        raise ValueError(f"schema path is not allowlisted: {schema_ref}")
    return target


def _safe_generate_scope_issue(intent: dict[str, Any]) -> str:
    target_scope = intent.get("targetScope")
    if not isinstance(target_scope, dict):
        return "safe generation tool missing targetScope"
    scope_type = str(target_scope.get("scopeType") or "").casefold()
    target_path = str(target_scope.get("targetPath") or "")
    if scope_type not in {"run_candidate", "candidate_output", "current_run"}:
        return "safe generation tool must target current run candidate output"
    if target_path and not target_path.replace("\\", "/").startswith(f"{RUN_LOCAL_WRITE_ROOT}/"):
        return "safe generation targetPath must stay under candidate_outputs/"
    return ""


def _deterministic_verify_scope_issue(intent: dict[str, Any]) -> str:
    target_scope = intent.get("targetScope")
    if not isinstance(target_scope, dict):
        return "deterministic verification tool missing targetScope"
    scope_type = str(target_scope.get("scopeType") or "").casefold()
    if scope_type in {"all", "whole_modelspace", "current_dwg"}:
        return "deterministic verification cannot target all CAD state or current DWG"
    tool_name = str(intent.get("toolName") or "").casefold()
    if tool_name == "closeout_gate":
        if scope_type not in {"run_package", "current_run"}:
            return "closeout_gate must target the current run package"
        return ""
    inputs = _decoded_inputs(intent)
    target_path = str(
        target_scope.get("targetPath")
        or inputs.get("planPath")
        or inputs.get("cadPlanPath")
        or inputs.get("summaryPath")
        or inputs.get("executionSummaryPath")
        or inputs.get("path")
        or ""
    )
    if not target_path:
        return "deterministic verification tool requires a run-local targetPath"
    normalized = target_path.replace("\\", "/")
    if Path(target_path).is_absolute() or normalized.startswith("../") or "/../" in normalized:
        return "deterministic verification targetPath must stay inside the current run"
    return ""


def _controlled_cad_scope_issue(intent: dict[str, Any]) -> str:
    target_scope = intent.get("targetScope")
    if not isinstance(target_scope, dict):
        return "controlled CAD tool missing targetScope"
    scope_type = str(target_scope.get("scopeType") or "").casefold()
    if scope_type in {"all", "whole_modelspace", "current_dwg", "active_dwg"}:
        return "controlled CAD tool cannot target all CAD state or current DWG"
    if scope_type not in {"run_artifact", "cad_plan", "run_candidate", "current_run"}:
        return "controlled CAD tool must target a run-local CAD_PLAN artifact"

    inputs = _decoded_inputs(intent)
    target_path = str(
        target_scope.get("targetPath")
        or inputs.get("planPath")
        or inputs.get("cadPlanPath")
        or inputs.get("path")
        or ""
    )
    if not target_path:
        return "controlled CAD tool requires a run-local CAD_PLAN targetPath"
    normalized = target_path.replace("\\", "/")
    if Path(target_path).is_absolute() or normalized.startswith("../") or "/../" in normalized:
        return "controlled CAD tool targetPath must stay inside the current run"

    target_layer = str(target_scope.get("targetLayer") or inputs.get("targetLayer") or "")
    if target_layer and target_layer != "CODEX_PREVIEW":
        return "controlled CAD tool may only target CODEX_PREVIEW"
    return ""


def _forbidden_direct_request(intent: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    tool_name = str(intent.get("toolName") or "").strip().casefold()
    permission_class = str(intent.get("permissionClass") or "").strip().casefold()
    effects = {item.strip().casefold() for item in _text_items(intent.get("requestedEffects"))}

    if tool_name in FORBIDDEN_DIRECT_TOOL_NAMES:
        reasons.append(f"model requested forbidden direct tool: {tool_name}")
    if permission_class in {"save_current_dwg", "delete_or_replace", "formal_layer_write"}:
        reasons.append(f"model requested forbidden permission class: {permission_class}")
    forbidden_effects = sorted(effects.intersection(FORBIDDEN_DIRECT_EFFECTS))
    if forbidden_effects:
        reasons.append("model requested forbidden effect: " + ", ".join(forbidden_effects))
    return reasons


def evaluate_tool_intent(intent: dict[str, Any]) -> dict[str, Any]:
    """Return the orchestrator decision for one model-supplied tool intent."""

    missing = _missing_required_fields(intent)
    blocking_reasons: list[str] = []
    if missing:
        blocking_reasons.append("missing tool intent fields: " + ", ".join(missing))

    blocking_reasons.extend(_forbidden_direct_request(intent))

    risk_level = str(intent.get("riskLevel") or "").strip().casefold()
    permission_class = str(intent.get("permissionClass") or "").strip().casefold()
    tool_name = str(intent.get("toolName") or "").strip().casefold()
    if risk_level in HIGH_RISK_LEVELS and _target_scope_missing(intent.get("targetScope")):
        blocking_reasons.append("high-risk tool intent missing precise targetScope")
    if tool_name in SAFE_GENERATE_TOOLS:
        scope_issue = _safe_generate_scope_issue(intent)
        if scope_issue:
            blocking_reasons.append(scope_issue)
    if tool_name in DETERMINISTIC_VERIFY_TOOLS:
        scope_issue = _deterministic_verify_scope_issue(intent)
        if scope_issue:
            blocking_reasons.append(scope_issue)
    if tool_name in CONTROLLED_CAD_TOOLS:
        scope_issue = _controlled_cad_scope_issue(intent)
        if scope_issue:
            blocking_reasons.append(scope_issue)

    if blocking_reasons:
        decision = "blocked"
    elif tool_name in READ_ONLY_TOOLS and permission_class in READ_ONLY_PERMISSION_CLASSES:
        decision = "allowed"
    elif tool_name in SAFE_GENERATE_TOOLS and permission_class in SAFE_GENERATE_PERMISSION_CLASSES:
        decision = "allowed"
    elif tool_name in DETERMINISTIC_VERIFY_TOOLS and permission_class in DETERMINISTIC_VERIFY_PERMISSION_CLASSES:
        decision = "allowed"
    elif tool_name in CONTROLLED_CAD_TOOLS and permission_class in CONTROLLED_CAD_PERMISSION_CLASSES:
        decision = "allowed"
    else:
        decision = "needs_more_evidence"

    return {
        "schemaVersion": "tool-contract-gate/v1",
        "orchestratorDecision": decision,
        "blockingReasons": list(dict.fromkeys(blocking_reasons)),
        "toolIntentId": str(intent.get("toolIntentId") or ""),
        "requestedByAgentId": str(intent.get("requestedByAgentId") or ""),
        "toolName": str(intent.get("toolName") or ""),
        "riskLevel": str(intent.get("riskLevel") or ""),
        "permissionClass": str(intent.get("permissionClass") or ""),
        "deterministicEntryPoint": _deterministic_entry_point(tool_name, decision),
        "evidenceBoundary": [
            "tool intent gate only permits orchestrator-owned allowlisted execution",
            "model requests cannot authorize CAD writes outside controlled CODEX_PREVIEW execution, deletes, saves, registry mutations, or table C claims",
            "allowed verification or controlled-CAD intent only means the orchestrator may run the relevant gate; the model cannot decide pass/fail",
        ],
    }


def _deterministic_entry_point(tool_name: str, decision: str) -> str:
    if decision == "allowed" and tool_name in READ_ONLY_TOOLS:
        return f"core.orchestrator.tool_contract.allowlisted_readers.{tool_name}"
    if decision == "allowed" and tool_name in SAFE_GENERATE_TOOLS:
        return f"core.orchestrator.tool_contract.safe_generators.{tool_name}"
    if decision == "allowed" and tool_name in DETERMINISTIC_VERIFY_TOOLS:
        return f"core.orchestrator.tool_contract.deterministic_verifiers.{tool_name}"
    if decision == "allowed" and tool_name in CONTROLLED_CAD_TOOLS:
        return f"core.orchestrator.tool_contract.controlled_cad_tools.{tool_name}"
    return ""


def build_tool_trace(
    intent: dict[str, Any],
    *,
    run_id: str = "",
    result: dict[str, Any] | None = None,
    execution_status: str | None = None,
) -> dict[str, Any]:
    """Build a downstream-readable trace record for one tool intent."""

    decision = evaluate_tool_intent(intent)
    result_payload = result if isinstance(result, dict) else {}
    status = execution_status or "not_executed"
    if execution_status is None:
        if decision["orchestratorDecision"] == "blocked":
            status = "blocked_before_execution"
        elif decision["orchestratorDecision"] == "allowed":
            status = "allowed_not_executed"
    result_status = str(result_payload.get("resultStatus") or result_payload.get("status") or "not_verified")
    return {
        "schemaVersion": TOOL_TRACE_SCHEMA_VERSION,
        "runId": str(run_id),
        "toolIntentId": decision["toolIntentId"],
        "requestedByAgentId": decision["requestedByAgentId"],
        "toolName": decision["toolName"],
        "toolSchemaVersion": TOOL_INTENT_SCHEMA_VERSION,
        "riskLevel": decision["riskLevel"],
        "permissionClass": decision["permissionClass"],
        "targetScope": intent.get("targetScope") if isinstance(intent.get("targetScope"), dict) else {},
        "orchestratorDecision": decision["orchestratorDecision"],
        "blockingReasons": decision["blockingReasons"],
        "deterministicEntryPoint": decision["deterministicEntryPoint"],
        "executionStatus": status,
        "resultStatus": result_status,
        "result": result_payload,
        "expectedEvidence": _text_items(intent.get("expectedEvidence")),
        "evidenceBoundary": decision["evidenceBoundary"],
        "downstreamReadableSummary": _summary(decision),
        "downstreamArtifactPath": "",
        "generatedAt": _utc_now(),
    }


def _summary(decision: dict[str, Any]) -> str:
    status = decision["orchestratorDecision"]
    tool = decision["toolName"] or "unknown_tool"
    if status == "blocked":
        return f"{tool} blocked before execution: {'; '.join(decision['blockingReasons'])}"
    if status == "allowed":
        return f"{tool} is allowlisted; execution and pass/fail remain orchestrator-owned."
    return f"{tool} needs more evidence or a later stage contract before execution."


def write_tool_trace(run_dir: str | Path, intent: dict[str, Any], *, run_id: str = "") -> dict[str, Any]:
    """Write ``tool_traces/<agent>.<intent>.json`` and return the trace payload."""

    trace = build_tool_trace(intent, run_id=run_id)
    agent = str(trace["requestedByAgentId"] or "unknown_agent").replace("/", "_").replace("\\", "_")
    intent_id = str(trace["toolIntentId"] or "tool_intent").replace("/", "_").replace("\\", "_")
    rel_path = f"tool_traces/{agent}.{intent_id}.json"
    trace["downstreamArtifactPath"] = rel_path
    _write_json(Path(run_dir) / rel_path, trace)
    return trace


def run_tool_intent(run_dir: str | Path, intent: dict[str, Any], *, run_id: str = "") -> dict[str, Any]:
    """Execute one allowlisted tool intent and write its trace."""

    run_root = Path(run_dir)
    decision = evaluate_tool_intent(intent)
    execution_status = "not_executed"
    result: dict[str, Any] = {}
    if decision["orchestratorDecision"] == "blocked":
        execution_status = "blocked_before_execution"
    elif decision["orchestratorDecision"] == "allowed":
        tool_name = str(intent.get("toolName") or "").casefold()
        if tool_name in READ_ONLY_TOOLS:
            result = _execute_read_only_tool(run_root, tool_name, intent)
        elif tool_name in SAFE_GENERATE_TOOLS:
            result = _execute_safe_generation_tool(run_root, tool_name, intent)
        elif tool_name in DETERMINISTIC_VERIFY_TOOLS:
            result = _execute_deterministic_verify_tool(run_root, tool_name, intent)
        elif tool_name in CONTROLLED_CAD_TOOLS:
            result = _execute_controlled_cad_tool(run_root, tool_name, intent)
        execution_status = "executed" if result.get("status") == "pass" else "failed"
    trace = build_tool_trace(intent, run_id=run_id, result=result, execution_status=execution_status)
    if execution_status == "failed":
        reason = str(result.get("reason") or "tool execution failed")
        trace["blockingReasons"] = list(dict.fromkeys([*trace.get("blockingReasons", []), reason]))
        trace["orchestratorDecision"] = "blocked"
        trace["downstreamReadableSummary"] = f"{trace['toolName']} failed orchestrator-owned execution: {reason}"
    agent = str(trace["requestedByAgentId"] or "unknown_agent").replace("/", "_").replace("\\", "_")
    intent_id = str(trace["toolIntentId"] or "tool_intent").replace("/", "_").replace("\\", "_")
    rel_path = f"tool_traces/{agent}.{intent_id}.json"
    trace["downstreamArtifactPath"] = rel_path
    _write_json(run_root / rel_path, trace)
    return trace


def _execute_read_only_tool(run_root: Path, tool_name: str, intent: dict[str, Any]) -> dict[str, Any]:
    inputs = _decoded_inputs(intent)
    try:
        if tool_name == "read_run_package":
            return _read_run_package(run_root, inputs)
        if tool_name == "read_rule_context":
            return _read_rule_context(run_root, inputs)
        if tool_name == "read_schema":
            return _read_schema(inputs)
        if tool_name == "read_agent_output":
            return _read_agent_output(run_root, inputs)
        if tool_name == "read_trace_summary":
            return _read_trace_summary(run_root, inputs)
    except (OSError, ValueError) as exc:
        return {"status": "fail", "reason": str(exc)}
    return {"status": "fail", "reason": f"unsupported read-only tool: {tool_name}"}


def _execute_safe_generation_tool(run_root: Path, tool_name: str, intent: dict[str, Any]) -> dict[str, Any]:
    inputs = _decoded_inputs(intent)
    payload = inputs.get("payload")
    if not isinstance(payload, dict):
        return {"status": "fail", "reason": "safe generation input payload must be a JSON object"}
    try:
        if tool_name == "write_agent_output_candidate":
            agent_id = _safe_rel_fragment(str(inputs.get("agentId") or intent.get("requestedByAgentId") or "agent"))
            rel_path = f"{RUN_LOCAL_WRITE_ROOT}/agent_outputs/{agent_id}.json"
        elif tool_name == "write_draft_intent_candidate":
            rel_path = f"{RUN_LOCAL_WRITE_ROOT}/pipeline_intent.draft.json"
        elif tool_name == "write_cad_plan_candidate":
            rel_path = f"{RUN_LOCAL_WRITE_ROOT}/cad_plan.candidate.json"
        elif tool_name == "write_learning_candidate":
            agent_id = _safe_rel_fragment(str(inputs.get("agentId") or intent.get("requestedByAgentId") or "agent"))
            rel_path = f"{RUN_LOCAL_WRITE_ROOT}/learning_candidates/{agent_id}.json"
        else:
            return {"status": "fail", "reason": f"unsupported safe generation tool: {tool_name}"}
        target = _resolve_under(run_root, rel_path)
        _write_json(target, payload)
    except (OSError, ValueError) as exc:
        return {"status": "fail", "reason": str(exc)}
    return {
        "status": "pass",
        "toolStage": "stage2_safe_generation",
        "writtenPath": rel_path,
        "evidenceBoundary": [
            "safe generation writes only to candidate_outputs inside the current run",
            "candidate output does not mutate registry, training source, table C, or system asset verified status",
            "candidate CAD_PLAN still requires validate, dry-run, CAD preview, and readback before delivery",
        ],
    }


def _load_json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError("JSON payload must be an object")
    return value


def _path_from_intent(intent: dict[str, Any], *input_keys: str) -> str:
    inputs = _decoded_inputs(intent)
    target_scope = intent.get("targetScope") if isinstance(intent.get("targetScope"), dict) else {}
    for key in input_keys:
        value = inputs.get(key)
        if value:
            return str(value)
    return str(target_scope.get("targetPath") or "")


def _write_stage3_report(run_root: Path, rel_path: str, report: dict[str, Any]) -> None:
    _write_json(_resolve_under(run_root, rel_path), report)


def _execute_deterministic_verify_tool(run_root: Path, tool_name: str, intent: dict[str, Any]) -> dict[str, Any]:
    try:
        if tool_name == "validate_plan":
            return _verify_validate_plan(run_root, intent)
        if tool_name in {"dry_run", "dry_run_plan"}:
            return _verify_dry_run_plan(run_root, intent)
        if tool_name == "preview_only_audit":
            return _verify_preview_only_audit(run_root, intent)
        if tool_name == "closeout_gate":
            return _verify_closeout_gate(run_root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"status": "fail", "toolStage": "stage3_deterministic_verify", "reason": str(exc)}
    return {"status": "fail", "toolStage": "stage3_deterministic_verify", "reason": f"unsupported deterministic verify tool: {tool_name}"}


def _execute_controlled_cad_tool(run_root: Path, tool_name: str, intent: dict[str, Any]) -> dict[str, Any]:
    if tool_name not in CONTROLLED_CAD_TOOLS:
        return {"status": "fail", "toolStage": "stage4_controlled_cad", "reason": f"unsupported controlled CAD tool: {tool_name}"}

    inputs = _decoded_inputs(intent)
    plan_rel = _path_from_intent(intent, "planPath", "cadPlanPath", "path")
    if not plan_rel:
        return _write_controlled_cad_blocked_report(run_root, intent, plan_rel="", driver_mode="", reason="planPath is required")

    prereq_issue = _controlled_cad_prereq_issue(run_root, plan_rel)
    if prereq_issue:
        return _write_controlled_cad_blocked_report(run_root, intent, plan_rel=plan_rel, driver_mode="", reason=prereq_issue)

    raw_driver_mode = str(
        inputs.get("driverMode") or inputs.get("executionMode") or DEFAULT_CONTROLLED_CAD_DRIVER_MODE
    ).strip().casefold()
    try:
        driver, driver_mode, cad_geometry_verified = _build_controlled_cad_driver(raw_driver_mode)
        from core.execution.execute_plan import execute_plan_file

        execution_summary = execute_plan_file(
            _resolve_under(run_root, plan_rel),
            driver=driver,
            preview_only=True,
            allow_unconfirmed=False,
            allow_destructive=False,
        )
        summary = execution_summary if isinstance(execution_summary, dict) else {"rawExecutionSummary": execution_summary}
        created_handles = [str(handle) for handle in summary.get("created_handles", []) if str(handle)]
        readback = _controlled_cad_readback(
            driver,
            created_handles=created_handles,
            layer=str(summary.get("layer") or "CODEX_PREVIEW"),
            cad_geometry_verified=cad_geometry_verified,
        )
        if not created_handles:
            reason = "controlled CAD execution returned no created handles"
            return _write_controlled_cad_blocked_report(
                run_root,
                intent,
                plan_rel=plan_rel,
                driver_mode=driver_mode,
                reason=reason,
                execution_summary=dict(summary),
                readback_summary=readback,
            )

        summary.update(
            {
                "toolStage": "stage4_controlled_cad",
                "toolIntentId": str(intent.get("toolIntentId") or ""),
                "requestedByAgentId": str(intent.get("requestedByAgentId") or ""),
                "driverMode": driver_mode,
                "savedCurrentDwg": False,
                "cadGeometryVerified": cad_geometry_verified and readback["readbackStatus"] == "ok",
                "readbackStatus": readback["readbackStatus"],
                "readbackEntityCount": readback["readbackEntityCount"],
                "evidenceBoundary": [
                    "controlled CAD execution is preview-only and savedCurrentDwg=false",
                    "created handles and readback are recorded for downstream closeout",
                    "fake_driver_preflight proves tool orchestration only; it does not prove real AutoCAD geometry",
                    "screenshot remains visual aid only and does not replace handle readback or user acceptance",
                ],
            }
        )
        _write_json(_resolve_under(run_root, CAD_EXECUTION_SUMMARY_PATH), dict(summary))
        _write_json(_resolve_under(run_root, CAD_READBACK_SUMMARY_PATH), readback)
        report = _controlled_cad_report(
            intent,
            status="pass",
            result_status="ok" if summary["cadGeometryVerified"] else "not_verified",
            plan_rel=plan_rel,
            driver_mode=driver_mode,
            reason="" if summary["cadGeometryVerified"] else "no real AutoCAD geometry verification in fake-driver preflight",
            execution_summary=dict(summary),
            readback_summary=readback,
        )
        _write_json(_resolve_under(run_root, CAD_PREVIEW_TOOL_REPORT_PATH), report)
        return {
            "status": "pass",
            "resultStatus": str(report.get("resultStatus") or "not_verified"),
            "toolStage": "stage4_controlled_cad",
            "reportPath": CAD_PREVIEW_TOOL_REPORT_PATH,
            "executionSummaryPath": CAD_EXECUTION_SUMMARY_PATH,
            "readbackSummaryPath": CAD_READBACK_SUMMARY_PATH,
            "planPath": plan_rel,
            "driverMode": driver_mode,
            "createdHandleCount": len(created_handles),
            "readbackStatus": readback["readbackStatus"],
            "readbackEntityCount": readback["readbackEntityCount"],
            "targetLayer": readback["targetLayer"],
            "savedCurrentDwg": False,
            "cadGeometryVerified": bool(summary["cadGeometryVerified"]),
            "reason": str(report.get("reason") or ""),
            "evidenceBoundary": report["evidenceBoundary"],
        }
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        return _write_controlled_cad_blocked_report(
            run_root,
            intent,
            plan_rel=plan_rel,
            driver_mode=raw_driver_mode,
            reason=str(exc),
        )


def _controlled_cad_prereq_issue(run_root: Path, plan_rel: str) -> str:
    for rel_path, label in ((VALIDATION_REPORT_PATH, "validate_plan"), (DRY_RUN_REPORT_PATH, "dry_run_plan")):
        try:
            path = _resolve_under(run_root, rel_path)
        except ValueError as exc:
            return str(exc)
        if not path.is_file():
            return f"{label} report missing before controlled CAD execution: {rel_path}"
        payload = _read_json(path)
        status = str(payload.get("status") or "").casefold()
        if status not in PASS_STATUSES:
            reason = str(payload.get("reason") or payload.get("validationErrors") or payload.get("blockingReasons") or "")
            return f"{label} report is not pass before controlled CAD execution: {status or 'missing'} {reason}".strip()
        report_plan = str(payload.get("planPath") or "")
        if report_plan and report_plan.replace("\\", "/") != plan_rel.replace("\\", "/"):
            return f"{label} report planPath mismatch: expected {plan_rel}, got {report_plan}"
    return ""


def _build_controlled_cad_driver(driver_mode: str) -> tuple[Any, str, bool]:
    if driver_mode in FAKE_DRIVER_MODES:
        from core.verification.fake_cad_driver import FakeCadDriver

        return FakeCadDriver(), "fake_driver_preflight", False
    if driver_mode in CAD_SESSION_HOST_DRIVER_MODES:
        host_url = str(os.environ.get("CAD_SESSION_HOST_URL") or "").strip()
        token = str(os.environ.get("CAD_SESSION_TOKEN") or "").strip()
        if not host_url or not token:
            raise ValueError(
                "CAD_SESSION_HOST_URL and CAD_SESSION_TOKEN are required for cad_session_host driverMode"
            )
        timeout_seconds = float(os.environ.get("CAD_SESSION_HOST_TIMEOUT_SECONDS", "30"))
        from core.cad_io.cad_session_host import CadSessionHostClient

        return (
            CadSessionHostClient(
                base_url=host_url,
                token=token,
                timeout_seconds=timeout_seconds,
            ),
            "cad_session_host",
            True,
        )
    if driver_mode in AUTOCAD_EXISTING_DRIVER_MODES:
        from core.cad_io.autocad_com import AutoCADComDriver

        return AutoCADComDriver(connect_existing_only=True), "autocad_existing", True
    raise ValueError("driverMode must be cad_session_host, autocad_existing, or fake_driver_preflight")


def _controlled_cad_readback(
    driver: Any,
    *,
    created_handles: list[str],
    layer: str,
    cad_geometry_verified: bool,
) -> dict[str, Any]:
    entities: list[dict[str, Any]] = []
    raw_readback_status = "not_attempted"
    readback_error = ""
    snapshot = getattr(driver, "snapshot_handles", None)
    if created_handles and callable(snapshot):
        try:
            raw_entities = snapshot(handles=created_handles, layer=layer)
            entities = [entity for entity in raw_entities if isinstance(entity, dict)]
            if len(entities) == len(created_handles):
                raw_readback_status = "ok"
            elif entities:
                raw_readback_status = "partial"
            else:
                raw_readback_status = "empty"
        except Exception as exc:  # pragma: no cover - defensive around CAD COM drivers
            raw_readback_status = "failed"
            readback_error = str(exc)
    elif created_handles:
        raw_readback_status = "unavailable"

    readback_status = raw_readback_status if cad_geometry_verified else "not_verified"
    type_counts: dict[str, int] = {}
    layers = set()
    for entity in entities:
        entity_type = str(entity.get("type") or entity.get("object_name") or entity.get("ObjectName") or "unknown")
        type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        layer_value = str(entity.get("layer") or "")
        if layer_value:
            layers.add(layer_value)
    bbox = _union_bbox([entity.get("bbox") for entity in entities])
    return {
        "schemaVersion": "controlled-cad-readback-summary/v1",
        "status": readback_status,
        "created_handles_readback": readback_status,
        "readbackStatus": readback_status,
        "rawReadbackStatus": raw_readback_status,
        "readbackError": readback_error,
        "created_handles": created_handles,
        "createdHandleCount": len(created_handles),
        "readbackEntityCount": len(entities),
        "targetLayer": layer,
        "readbackLayers": sorted(layers),
        "entityTypeCounts": type_counts,
        "bbox": bbox,
        "cadGeometryVerified": cad_geometry_verified and raw_readback_status == "ok",
        "savedCurrentDwg": False,
        "evidenceBoundary": [
            "created handles are read back through snapshot_handles when available",
            "fake_driver_preflight readback is marked not_verified and cannot prove real CAD geometry",
            "savedCurrentDwg=false is part of the controlled CAD contract",
        ],
        "generatedAt": _utc_now(),
    }


def _union_bbox(raw_bboxes: list[Any]) -> dict[str, list[float]] | None:
    mins: list[list[float]] = []
    maxs: list[list[float]] = []
    for raw in raw_bboxes:
        if not isinstance(raw, dict):
            continue
        raw_min = raw.get("min")
        raw_max = raw.get("max")
        if isinstance(raw_min, list) and isinstance(raw_max, list) and len(raw_min) >= 2 and len(raw_max) >= 2:
            try:
                mins.append([float(raw_min[0]), float(raw_min[1])])
                maxs.append([float(raw_max[0]), float(raw_max[1])])
            except (TypeError, ValueError):
                continue
    if not mins or not maxs:
        return None
    return {
        "min": [min(point[0] for point in mins), min(point[1] for point in mins)],
        "max": [max(point[0] for point in maxs), max(point[1] for point in maxs)],
    }


def _write_controlled_cad_blocked_report(
    run_root: Path,
    intent: dict[str, Any],
    *,
    plan_rel: str,
    driver_mode: str,
    reason: str,
    execution_summary: dict[str, Any] | None = None,
    readback_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    report = _controlled_cad_report(
        intent,
        status="not_verified",
        result_status="blocked",
        plan_rel=plan_rel,
        driver_mode=driver_mode,
        reason=reason,
        execution_summary=execution_summary,
        readback_summary=readback_summary,
    )
    _write_json(_resolve_under(run_root, CAD_PREVIEW_TOOL_REPORT_PATH), report)
    if isinstance(execution_summary, dict):
        _write_json(_resolve_under(run_root, CAD_EXECUTION_SUMMARY_PATH), execution_summary)
    if isinstance(readback_summary, dict):
        _write_json(_resolve_under(run_root, CAD_READBACK_SUMMARY_PATH), readback_summary)
    return {
        "status": "fail",
        "resultStatus": "blocked",
        "toolStage": "stage4_controlled_cad",
        "reportPath": CAD_PREVIEW_TOOL_REPORT_PATH,
        "planPath": plan_rel,
        "driverMode": driver_mode,
        "savedCurrentDwg": False,
        "cadGeometryVerified": False,
        "reason": reason,
        "evidenceBoundary": report["evidenceBoundary"],
    }


def _controlled_cad_report(
    intent: dict[str, Any],
    *,
    status: str,
    result_status: str,
    plan_rel: str,
    driver_mode: str,
    reason: str,
    execution_summary: dict[str, Any] | None,
    readback_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    created_handles = []
    if isinstance(execution_summary, dict):
        created_handles = [str(handle) for handle in execution_summary.get("created_handles", []) if str(handle)]
    readback = readback_summary if isinstance(readback_summary, dict) else {}
    return {
        "schemaVersion": "controlled-cad-preview-tool-report/v1",
        "status": status,
        "resultStatus": result_status,
        "toolStage": "stage4_controlled_cad",
        "toolIntentId": str(intent.get("toolIntentId") or ""),
        "requestedByAgentId": str(intent.get("requestedByAgentId") or ""),
        "planPath": plan_rel,
        "driverMode": driver_mode,
        "created_handles": created_handles,
        "createdHandleCount": len(created_handles),
        "targetLayer": str(readback.get("targetLayer") or ""),
        "readbackStatus": str(readback.get("readbackStatus") or ""),
        "readbackEntityCount": int(readback.get("readbackEntityCount") or 0),
        "entityTypeCounts": readback.get("entityTypeCounts") if isinstance(readback.get("entityTypeCounts"), dict) else {},
        "bbox": readback.get("bbox"),
        "cadGeometryVerified": bool(readback.get("cadGeometryVerified") is True),
        "savedCurrentDwg": False,
        "reason": reason,
        "executionSummaryPath": CAD_EXECUTION_SUMMARY_PATH if execution_summary is not None else "",
        "readbackSummaryPath": CAD_READBACK_SUMMARY_PATH if readback_summary is not None else "",
        "evidenceBoundary": [
            "Stage 4 CAD tool execution is orchestrator-owned, not model-owned",
            "execution requires prior validate_plan and dry_run_plan pass reports for the same CAD_PLAN",
            "only CODEX_PREVIEW preview execution is allowed; savedCurrentDwg=false",
            "delete/replace, formal-layer write, registry mutation, training source mutation, and table C claims remain forbidden",
            "screenshot is visual_aid_only and cannot replace created handles readback, closeout gate, or user acceptance",
        ],
        "generatedAt": _utc_now(),
    }


def _verify_validate_plan(run_root: Path, intent: dict[str, Any]) -> dict[str, Any]:
    from core.plan_engine.validate_plan import validate_plan

    plan_rel = _path_from_intent(intent, "planPath", "cadPlanPath", "path")
    if not plan_rel:
        return {"status": "fail", "toolStage": "stage3_deterministic_verify", "reason": "planPath is required"}
    plan_path = _resolve_under(run_root, plan_rel)
    errors: list[str] = []
    try:
        plan = _load_json_object(plan_path)
        errors = validate_plan(plan)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors = [str(exc)]
    status = "pass" if not errors else "fail"
    report = {
        "schemaVersion": "deterministic-validate-plan-report/v1",
        "status": status,
        "toolStage": "stage3_deterministic_verify",
        "toolIntentId": str(intent.get("toolIntentId") or ""),
        "requestedByAgentId": str(intent.get("requestedByAgentId") or ""),
        "planPath": plan_rel,
        "validationErrors": errors,
        "evidenceBoundary": [
            "validate_plan is deterministic JSON validation only",
            "validation pass does not prove CAD geometry, CAD write, readback, screenshot, or user acceptance",
        ],
        "generatedAt": _utc_now(),
    }
    _write_stage3_report(run_root, VALIDATION_REPORT_PATH, report)
    return {
        "status": status,
        "toolStage": "stage3_deterministic_verify",
        "reportPath": VALIDATION_REPORT_PATH,
        "planPath": plan_rel,
        "validationErrors": errors,
        "reason": "; ".join(errors) if errors else "",
        "evidenceBoundary": report["evidenceBoundary"],
    }


def _verify_dry_run_plan(run_root: Path, intent: dict[str, Any]) -> dict[str, Any]:
    from core.plan_engine.dry_run_report import create_dry_run_report

    plan_rel = _path_from_intent(intent, "planPath", "cadPlanPath", "path")
    if not plan_rel:
        return {"status": "fail", "toolStage": "stage3_deterministic_verify", "reason": "planPath is required"}
    plan_path = _resolve_under(run_root, plan_rel)
    raw_report = create_dry_run_report(plan_path)
    raw_status = str(raw_report.get("status") or "").casefold()
    validation_errors = _text_items(raw_report.get("validation_errors") or raw_report.get("validationErrors"))
    status = "pass" if raw_status in {"valid", "pass", "ready", "ok"} and not validation_errors else "fail"
    report = {
        "schemaVersion": "deterministic-dry-run-report/v1",
        "status": status,
        "toolStage": "stage3_deterministic_verify",
        "toolIntentId": str(intent.get("toolIntentId") or ""),
        "requestedByAgentId": str(intent.get("requestedByAgentId") or ""),
        "planPath": plan_rel,
        "dryRunStatus": raw_report.get("status"),
        "validationErrors": validation_errors,
        "entityCount": len(raw_report.get("entities", [])) if isinstance(raw_report.get("entities"), list) else 0,
        "rawDryRunReport": raw_report,
        "evidenceBoundary": [
            "dry_run is deterministic pre-CAD planning evidence only",
            "dry_run pass does not execute CAD, create handles, save DWG, or prove visual acceptance",
        ],
        "generatedAt": _utc_now(),
    }
    _write_stage3_report(run_root, DRY_RUN_REPORT_PATH, report)
    return {
        "status": status,
        "toolStage": "stage3_deterministic_verify",
        "reportPath": DRY_RUN_REPORT_PATH,
        "planPath": plan_rel,
        "dryRunStatus": raw_report.get("status"),
        "validationErrors": validation_errors,
        "entityCount": report["entityCount"],
        "reason": "; ".join(validation_errors) if validation_errors else "",
        "evidenceBoundary": report["evidenceBoundary"],
    }


def _verify_preview_only_audit(run_root: Path, intent: dict[str, Any]) -> dict[str, Any]:
    from core.verification.preview_only_audit import execution_summary_gate_failure, preview_only_audit_check

    inputs = _decoded_inputs(intent)
    audit = inputs.get("audit")
    summary_rel = _path_from_intent(intent, "summaryPath", "executionSummaryPath", "path")
    if isinstance(audit, dict):
        check = preview_only_audit_check(audit)
        failure = "" if check.get("status") == "pass" else str(check.get("message") or "preview-only audit failed")
    elif summary_rel:
        failure = execution_summary_gate_failure(path=_resolve_under(run_root, summary_rel))
        check = {
            "name": "preview_only_audit",
            "status": "pass" if not failure else "fail",
            "message": "Execution summary preview-only audit fields are present and valid." if not failure else failure,
        }
    else:
        failure = "summaryPath or audit input is required"
        check = {"name": "preview_only_audit", "status": "fail", "message": failure}
    status = "pass" if not failure else "fail"
    report = {
        "schemaVersion": "deterministic-preview-only-audit-report/v1",
        "status": status,
        "toolStage": "stage3_deterministic_verify",
        "toolIntentId": str(intent.get("toolIntentId") or ""),
        "requestedByAgentId": str(intent.get("requestedByAgentId") or ""),
        "summaryPath": summary_rel,
        "check": check,
        "blockingReasons": [failure] if failure else [],
        "evidenceBoundary": [
            "preview-only audit checks no-save/no-delete/preview-layer safety fields",
            "preview-only audit does not prove geometry accuracy, readback completeness, or visual acceptance",
        ],
        "generatedAt": _utc_now(),
    }
    _write_stage3_report(run_root, PREVIEW_ONLY_AUDIT_REPORT_PATH, report)
    return {
        "status": status,
        "toolStage": "stage3_deterministic_verify",
        "reportPath": PREVIEW_ONLY_AUDIT_REPORT_PATH,
        "summaryPath": summary_rel,
        "reason": failure,
        "evidenceBoundary": report["evidenceBoundary"],
    }


def _verify_closeout_gate(run_root: Path) -> dict[str, Any]:
    from core.orchestrator.closeout_gate import run_closeout_gate

    decision = run_closeout_gate(run_root)
    blocking_reasons = [str(item) for item in decision.get("blocking_reasons", []) if str(item)]
    status = "pass" if decision.get("can_deliver") is True else "needs_more_evidence"
    return {
        "status": status,
        "toolStage": "stage3_deterministic_verify",
        "reportPath": CLOSEOUT_DECISION_PATH,
        "closeoutStatus": decision.get("status"),
        "canDeliver": bool(decision.get("can_deliver")),
        "blockingReasons": blocking_reasons,
        "reason": "; ".join(blocking_reasons) if blocking_reasons else "",
        "evidenceBoundary": [
            "closeout gate is authoritative for delivery claims inside this run package",
            "closeout pass still cannot claim user acceptance or table C increase",
        ],
    }


def _json_summary(path: Path, *, rel_path: str) -> dict[str, Any]:
    payload = _read_json(path)
    keys = sorted(payload.keys())[:20] if isinstance(payload, dict) else []
    return {
        "path": rel_path,
        "status": "pass" if path.is_file() and payload.get("status") != "unavailable" else "missing_or_unreadable",
        "keys": keys,
        "declaredStatus": str(payload.get("status") or ""),
    }


def _read_run_package(run_root: Path, inputs: dict[str, Any]) -> dict[str, Any]:
    paths = _text_items(inputs.get("paths")) or [
        "user_request.json",
        "context_pack.json",
        "dispatch_plan.json",
        "task_contract.json",
        "required_agents.json",
        "risk_assessment.json",
        "rule_context_pack.json",
        "state.json",
    ]
    read_files = []
    for rel_path in paths:
        target = _resolve_under(run_root, rel_path)
        read_files.append(_json_summary(target, rel_path=rel_path))
    return {
        "status": "pass",
        "toolStage": "stage1_read_only",
        "readFiles": read_files,
        "evidenceBoundary": ["read-only run package summary; does not execute or mutate files"],
    }


def _read_rule_context(run_root: Path, inputs: dict[str, Any]) -> dict[str, Any]:
    agent_id = str(inputs.get("agentId") or "")
    rel_path = str(inputs.get("path") or (f"rule_context_packs/{agent_id}.json" if agent_id else "rule_context_pack.json"))
    target = _resolve_under(run_root, rel_path)
    payload = _read_json(target)
    return {
        "status": "pass" if target.is_file() and payload.get("status") != "unavailable" else "fail",
        "toolStage": "stage1_read_only",
        "path": rel_path,
        "sourceRefs": payload.get("sourceRefs", []),
        "hardGates": payload.get("hardGates", []),
        "forbiddenActions": payload.get("forbiddenActions", []),
        "missingContext": payload.get("missingContext", []),
        "evidenceBoundary": ["read-only rule context summary; not a source mutation"],
    }


def _read_schema(inputs: dict[str, Any]) -> dict[str, Any]:
    schema_ref = str(inputs.get("schemaRef") or inputs.get("path") or "")
    if not schema_ref:
        return {"status": "fail", "reason": "schemaRef is required"}
    target = _safe_schema_path(schema_ref)
    payload = _read_json(target)
    properties = payload.get("properties") if isinstance(payload.get("properties"), dict) else {}
    return {
        "status": "pass" if target.is_file() and payload.get("status") != "unavailable" else "fail",
        "toolStage": "stage1_read_only",
        "schemaRef": schema_ref,
        "type": payload.get("type"),
        "required": payload.get("required", []),
        "properties": sorted(properties.keys()),
        "evidenceBoundary": ["read-only schema summary; not schema validation by itself"],
    }


def _read_agent_output(run_root: Path, inputs: dict[str, Any]) -> dict[str, Any]:
    agent_id = _safe_rel_fragment(str(inputs.get("agentId") or ""))
    rel_path = str(inputs.get("path") or f"agent_outputs/{agent_id}.json")
    target = _resolve_under(run_root, rel_path)
    payload = _read_json(target)
    return {
        "status": "pass" if target.is_file() and payload.get("status") != "unavailable" else "fail",
        "toolStage": "stage1_read_only",
        "path": rel_path,
        "summary": str(payload.get("status") or payload.get("deliveryDecision") or payload.get("styleDecision") or ""),
        "keys": sorted(payload.keys())[:20],
        "evidenceBoundary": ["read-only agent output summary; does not re-run the agent"],
    }


def _read_trace_summary(run_root: Path, inputs: dict[str, Any]) -> dict[str, Any]:
    rel_path = str(inputs.get("path") or "")
    if not rel_path:
        return {"status": "fail", "reason": "trace summary path is required"}
    target = _resolve_under(run_root, rel_path)
    if not target.is_file():
        return {"status": "fail", "reason": f"trace summary not found: {rel_path}"}
    text = target.read_text(encoding="utf-8-sig")
    return {
        "status": "pass",
        "toolStage": "stage1_read_only",
        "path": rel_path,
        "charCount": len(text),
        "excerpt": text[:1200],
        "evidenceBoundary": ["trace summary is read-only diagnostic context; it does not replace JSON gates"],
    }
