"""Local implementation of the Worker-first live model bridge contract."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Iterable
from uuid import uuid4

from core.orchestrator.local_live_model_bridge_state import (
    AGENT_OUTPUT_SCHEMA,
    TASK_ENVELOPE_SCHEMA,
    WORKER_RUN_STATE_SCHEMA,
    LocalLiveModelBridgeStateMixin,
    iso,
    slug,
    utc_now,
    write_json,
)


class LocalLiveModelBridgeRuntime(LocalLiveModelBridgeStateMixin):
    """Deterministic local stand-in for the planned Worker + bridge runtime."""

    def __init__(self, root_dir: str | Path, *, now: Callable[[], datetime] | None = None) -> None:
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self._now = now or utc_now

    def create_run(
        self,
        *,
        request_summary: str,
        workspace_id: str,
        target_stage: str,
        agent_ids: Iterable[str] | None = None,
        dependencies: dict[str, list[str]] | None = None,
        requested_by: str = "codex_chat",
        task_specs: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        now = self._now()
        run_id = f"run_{now.strftime('%Y%m%d%H%M%S')}_{slug(target_stage)}_{uuid4().hex[:8]}"
        tasks = self._build_tasks(
            run_id=run_id,
            workspace_id=workspace_id,
            requested_by=requested_by,
            target_stage=target_stage,
            agent_ids=list(agent_ids or []),
            dependencies=dependencies or {},
            task_specs=task_specs,
        )
        state = {
            "schemaVersion": WORKER_RUN_STATE_SCHEMA,
            "runId": run_id,
            "runDir": str(self._run_dir(run_id)),
            "workspaceId": workspace_id,
            "requestedBy": requested_by,
            "state": "queued" if tasks else "created",
            "currentStage": target_stage,
            "completionClaim": target_stage,
            "featureGates": self._feature_gates_for_stage(target_stage),
            "requestSummary": request_summary,
            "tasks": tasks,
            "modelInvoked": False,
            "modelUnavailable": False,
            "schemaValid": False,
            "cadGeometryVerified": False,
            "retryCount": 0,
            "timeoutCount": 0,
            "dlqCount": 0,
            "securityBlocks": [],
            "blockedReasons": [],
            "acceptedIdempotencyKeys": [],
            "circuitBreakers": self._default_circuit_breakers(),
            "auditEvents": [
                self._audit_event("run_created", run_id=run_id, summary=f"created {len(tasks)} worker task(s)", at=now)
            ],
            "createdAt": iso(now),
            "updatedAt": iso(now),
        }
        self._save_state(state)
        self._progress_run(state)
        return state

    def get_run(self, run_id: str) -> dict[str, Any]:
        return self._load_state(run_id)

    def register_bridge(self, *, bridge_id: str, capabilities: list[str], version: str = "") -> dict[str, Any]:
        registry = self._load_bridge_registry()
        now = self._now()
        bridge = {
            "schemaVersion": "local_bridge_registration/v1",
            "bridgeId": bridge_id,
            "state": "online",
            "capabilities": [str(item) for item in capabilities if str(item)],
            "version": version,
            "registeredAt": registry.get(bridge_id, {}).get("registeredAt") or iso(now),
            "lastSeenAt": iso(now),
            "offlineReason": "",
        }
        registry[bridge_id] = bridge
        self._save_bridge_registry(registry)
        return bridge

    def mark_bridge_offline(self, bridge_id: str, *, reason: str) -> dict[str, Any]:
        registry = self._load_bridge_registry()
        now = self._now()
        bridge = dict(registry.get(bridge_id) or {})
        bridge.update(
            {
                "schemaVersion": "local_bridge_registration/v1",
                "bridgeId": bridge_id,
                "state": "offline",
                "lastSeenAt": iso(now),
                "offlineReason": reason,
            }
        )
        bridge.setdefault("capabilities", [])
        bridge.setdefault("version", "")
        bridge.setdefault("registeredAt", iso(now))
        registry[bridge_id] = bridge
        self._save_bridge_registry(registry)
        return bridge

    def cancel_run(self, run_id: str, *, reason: str) -> dict[str, Any]:
        state = self._load_state(run_id)
        normalized = reason.strip() or "cancelled"
        for task in state.get("tasks", []):
            if task.get("state") not in {"completed", "blocked", "failed"}:
                task["state"] = "cancelled"
                task["blockedReason"] = normalized
        state["state"] = "cancelled"
        state["blockedReasons"] = [normalized]
        state.setdefault("auditEvents", []).append(self._audit_event("run_cancelled", run_id=run_id, summary=normalized))
        self._touch(state)
        self._save_state(state)
        return state

    def lease_task(self, *, bridge_id: str, capabilities: list[str], heartbeat_token: str, run_id: str | None = None) -> dict[str, Any]:
        registry = self._load_bridge_registry()
        bridge = registry.get(bridge_id)
        claimed_capabilities = [str(item) for item in capabilities if str(item)]
        if bridge and bridge.get("state") != "online":
            self._mark_waiting_for_bridge(
                run_id=run_id,
                bridge_id=bridge_id,
                reason=str(bridge.get("offlineReason") or "bridge_unavailable"),
            )
            return {"status": "bridge_unavailable", "bridgeId": bridge_id}
        for state in self._iter_states(run_id=run_id):
            self._progress_run(state)
            requires_registered_bridge = self._requires_registered_bridge(state)
            if requires_registered_bridge and bridge is None:
                self._mark_waiting_for_bridge(run_id=state["runId"], bridge_id=bridge_id, reason="bridge_unregistered")
                return {"status": "bridge_unregistered", "bridgeId": bridge_id}
            effective_capabilities = (
                [str(item) for item in bridge.get("capabilities", []) if str(item)]
                if isinstance(bridge, dict)
                else claimed_capabilities
            )
            if bridge and not set(claimed_capabilities).issubset(set(effective_capabilities)):
                self._mark_waiting_for_bridge(run_id=state["runId"], bridge_id=bridge_id, reason="capability_mismatch")
                return {"status": "capability_mismatch", "bridgeId": bridge_id}
            task = self._next_leaseable_task(state, effective_capabilities)
            if task is None:
                if requires_registered_bridge and self._has_pending_capability_gap(state, effective_capabilities):
                    self._mark_waiting_for_bridge(run_id=state["runId"], bridge_id=bridge_id, reason="capability_mismatch")
                    return {"status": "capability_mismatch", "bridgeId": bridge_id}
                continue
            now = self._now()
            task.update(
                {
                    "state": "leased",
                    "leasedBy": bridge_id,
                    "heartbeatToken": heartbeat_token,
                    "heartbeatAt": iso(now),
                    "leaseExpiresAt": iso(now + timedelta(seconds=int(task.get("timeoutSeconds") or 30))),
                    "attempt": int(task.get("attempt") or 0) + 1,
                }
            )
            state["state"] = "leasing"
            state.setdefault("auditEvents", []).append(
                self._audit_event(
                    "task_leased",
                    run_id=state["runId"],
                    task_id=task["taskId"],
                    summary=bridge_id,
                    at=now,
                )
            )
            self._touch(state, at=now)
            self._save_state(state)
            return dict(task["envelope"])
        return {"status": "no_task"}

    def heartbeat_task(self, run_id: str, task_id: str, *, bridge_id: str, heartbeat_token: str, bridge_status: str) -> dict[str, Any]:
        state = self._load_state(run_id)
        task = self._task_by_id(state, task_id)
        if task is None:
            return {"status": "rejected", "reason": "unknown_task"}
        if task.get("leasedBy") != bridge_id or task.get("heartbeatToken") != heartbeat_token:
            return {"status": "rejected", "reason": "lease_mismatch"}
        now = self._now()
        task["state"] = "running"
        task["heartbeatAt"] = iso(now)
        state["state"] = "running"
        state.setdefault("auditEvents", []).append(
            self._audit_event(
                "task_heartbeat",
                run_id=run_id,
                task_id=task_id,
                summary=bridge_status,
                at=now,
            )
        )
        registry = self._load_bridge_registry()
        if bridge_id in registry:
            registry[bridge_id]["lastSeenAt"] = iso(now)
            registry[bridge_id]["state"] = "online"
            self._save_bridge_registry(registry)
        self._touch(state, at=now)
        self._save_state(state)
        return {"status": "accepted", "runId": run_id, "taskId": task_id, "taskState": task["state"]}

    def expire_timed_out_tasks(self, *, run_id: str | None = None) -> dict[str, Any]:
        last_state: dict[str, Any] = {"status": "no_run"}
        now = self._now()
        for state in self._iter_states(run_id=run_id):
            changed = False
            for task in state.get("tasks", []):
                if task.get("state") not in {"leased", "running"}:
                    continue
                expires_at = self._parse_time(str(task.get("leaseExpiresAt") or ""))
                if expires_at is None or expires_at > now:
                    continue
                changed = True
                state["timeoutCount"] = int(state.get("timeoutCount") or 0) + 1
                if int(task.get("attempt") or 0) < int(task.get("maxAttempts") or 1):
                    task["state"] = "retry_scheduled"
                    task["retryCount"] = int(task.get("retryCount") or 0) + 1
                    state["retryCount"] = int(state.get("retryCount") or 0) + 1
                    event_type, reason = "task_retry_scheduled", "bridge_timeout"
                else:
                    task["state"] = "blocked"
                    task["blockedReason"] = "task_timeout"
                    event_type, reason = "task_blocked", "task_timeout"
                state.setdefault("auditEvents", []).append(
                    self._audit_event(
                        event_type,
                        run_id=state["runId"],
                        task_id=task["taskId"],
                        summary=reason,
                        at=now,
                    )
                )
            if changed:
                self._progress_run(state)
                self._touch(state, at=now)
                self._save_state(state)
            last_state = state
        return last_state

    def submit_result(
        self,
        run_id: str,
        task_id: str,
        *,
        result: dict[str, Any],
        idempotency_key: str,
        bridge_id: str = "",
        heartbeat_token: str = "",
    ) -> dict[str, Any]:
        state = self._load_state(run_id)
        key = idempotency_key.strip()
        if key in state.setdefault("acceptedIdempotencyKeys", []):
            return {"status": "duplicate", "runId": run_id, "taskId": task_id}
        task = self._task_by_id(state, task_id)
        if task is None:
            return {"status": "rejected", "reason": "unknown_task"}
        if task.get("state") in {"leased", "running"}:
            if task.get("leasedBy") != bridge_id or task.get("heartbeatToken") != heartbeat_token:
                return {"status": "rejected", "reason": "lease_mismatch"}
        output = self._normalize_agent_output(state, task, result)
        state["acceptedIdempotencyKeys"].append(key)
        task["result"] = output
        task["resultIdempotencyKey"] = key
        if output["schemaValid"] is not True:
            task["state"] = "blocked"
            task["blockedReason"] = "schema_validation_failed"
            state["circuitBreakers"]["codex_cli_model_review"].update(
                {"state": "open", "reason": "schema_validation_failed"}
            )
        elif output["status"] in {"blocked", "failed"}:
            task["state"] = "blocked"
            task["blockedReason"] = output.get("blockedReason") or output["status"]
        else:
            task["state"] = "completed"
            task["completedAt"] = iso(self._now())
        state["modelInvoked"] = bool(state.get("modelInvoked") or output.get("modelInvoked"))
        state["modelUnavailable"] = bool(state.get("modelUnavailable") or output.get("modelUnavailable"))
        state["schemaValid"] = bool(output.get("schemaValid"))
        state.setdefault("auditEvents", []).append(
            self._audit_event(
                "task_result_accepted",
                run_id=run_id,
                task_id=task_id,
                summary=str(output.get("summary") or output.get("status") or ""),
            )
        )
        self._progress_run(state)
        self._touch(state)
        self._save_state(state)
        return {"status": "accepted", "runId": run_id, "taskId": task_id, "runState": state}

    def run_single_agent_live(self, **kwargs: Any) -> dict[str, Any]:
        return self._run_model_agents(target_stage="single_agent_live", agents=[kwargs.pop("agent_id")], dependencies={}, **kwargs)

    def run_multi_agent_live(self, **kwargs: Any) -> dict[str, Any]:
        agents = ["pipeline_design_director", "pipeline_style_generator", "pipeline_design_reviewer"]
        dependencies = {
            "pipeline_style_generator": ["pipeline_design_director"],
            "pipeline_design_reviewer": ["pipeline_style_generator"],
        }
        return self._run_model_agents(target_stage="multi_agent_live", agents=agents, dependencies=dependencies, **kwargs)

    def run_cad_mcp_preview_live(self, *, cad_plan: dict[str, Any], driver_mode: str, **kwargs: Any) -> dict[str, Any]:
        state = self.run_multi_agent_live(**kwargs)
        if state.get("state") == "blocked":
            return state
        from core.orchestrator.tool_contract import run_tool_intent
        from core.runtime.encoding_guard import assert_no_text_encoding_corruption

        run_id = state["runId"]
        run_dir = self._run_dir(run_id)
        plan_rel = "candidate_outputs/cad_plan.candidate.json"
        encoding_preflight = assert_no_text_encoding_corruption(kwargs["request_summary"], cad_plan)
        write_json(run_dir / plan_rel, cad_plan)
        validate_trace = run_tool_intent(
            run_dir,
            self._tool_intent(
                "pipeline_audit",
                "intent-validate-cad-plan",
                "validate_plan",
                "deterministic_verify",
                "low",
                {"planPath": plan_rel},
                {"scopeType": "run_artifact", "targetPath": plan_rel},
            ),
            run_id=run_id,
        )
        dry_trace = run_tool_intent(
            run_dir,
            self._tool_intent(
                "pipeline_audit",
                "intent-dry-run-cad-plan",
                "dry_run_plan",
                "deterministic_verify",
                "low",
                {"planPath": plan_rel},
                {"scopeType": "run_artifact", "targetPath": plan_rel},
            ),
            run_id=run_id,
        )
        preview_trace = run_tool_intent(
            run_dir,
            self._tool_intent(
                "pipeline_intent",
                "intent-preview-cad-execute",
                "preview_cad_execute",
                "cad_preview",
                "high",
                {"planPath": plan_rel, "driverMode": driver_mode},
                {
                    "scopeType": "run_artifact",
                    "targetPath": plan_rel,
                    "targetLayer": "CODEX_PREVIEW",
                    "previewOnly": True,
                    "savedCurrentDwg": False,
                },
                requested_effects=["cad_preview_write"],
            ),
            run_id=run_id,
        )
        return self._record_cad_preview_result(run_id, encoding_preflight, validate_trace, dry_trace, preview_trace, driver_mode)

    def _run_model_agents(
        self,
        *,
        request_summary: str,
        workspace_id: str,
        bridge_id: str,
        config: Any,
        runner: Any,
        cwd: str | Path | None = None,
        target_stage: str,
        agents: list[str],
        dependencies: dict[str, list[str]],
    ) -> dict[str, Any]:
        state = self.create_run(
            request_summary=request_summary,
            workspace_id=workspace_id,
            target_stage=target_stage,
            agent_ids=agents,
            dependencies=dependencies,
        )
        run_id = state["runId"]
        run_dir = self._run_dir(run_id)
        upstream_refs: list[str] = []
        for agent_id in agents:
            current = self.get_run(run_id)
            task = next(item for item in current["tasks"] if item["agentId"] == agent_id)
            token = f"{task['taskId']}-heartbeat"
            envelope = self.lease_task(
                bridge_id=bridge_id,
                capabilities=["codex_cli_model_review"],
                heartbeat_token=token,
                run_id=run_id,
            )
            if envelope.get("status"):
                return self.get_run(run_id)
            self.heartbeat_task(run_id, task["taskId"], bridge_id=bridge_id, heartbeat_token=token, bridge_status="running")
            output_rel = f"agent_outputs/{agent_id}.json"
            trace_rel = f"model_traces/{agent_id}/{agent_id.replace('_', '-')}/trace_summary.md"
            output = self._run_prompt_agent(agent_id, request_summary, envelope, run_dir, output_rel, config, runner, cwd, upstream_refs)
            provider = output.get("modelProviderStatus") if isinstance(output.get("modelProviderStatus"), dict) else {}
            provider_passed = provider.get("schemaValid") is True and provider.get("modelUnavailable") is not True
            blocked_reason = ""
            if provider.get("modelUnavailable") is True:
                blocked_reason = "model_unavailable"
            elif provider.get("schemaValid") is not True:
                blocked_reason = "schema_validation_failed"
            self.submit_result(
                run_id,
                task["taskId"],
                result={
                    "schemaVersion": AGENT_OUTPUT_SCHEMA,
                    "status": "completed" if provider_passed else "blocked",
                    "decision": str(output.get("decision") or "continue"),
                    "modelInvoked": provider.get("modelInvoked") is True or output.get("modelInvoked") is True,
                    "modelUnavailable": provider.get("modelUnavailable") is True,
                    "schemaValid": provider.get("schemaValid") is True,
                    "summary": str(output.get("designIntent") or output.get("styleDecision") or output.get("designReview") or ""),
                    "blockedReason": blocked_reason,
                    "evidenceRefs": [output_rel, *upstream_refs],
                    "traceRef": trace_rel,
                },
                idempotency_key=f"{run_id}:{task['taskId']}:{target_stage}",
                bridge_id=bridge_id,
                heartbeat_token=token,
            )
            if self.get_run(run_id).get("state") == "blocked":
                break
            upstream_refs.append(output_rel)
        return self.get_run(run_id)

    def _run_prompt_agent(
        self,
        agent_id: str,
        request_summary: str,
        envelope: dict[str, Any],
        run_dir: Path,
        output_rel: str,
        config: Any,
        runner: Any,
        cwd: str | Path | None,
        upstream_refs: list[str],
    ) -> dict[str, Any]:
        from core.model_review.prompt_library import run_prompt_pack_review

        payload = {
            "userRequest": request_summary,
            "taskContext": {
                "taskKind": str(envelope.get("outputSchema") or ""),
                "route": "local_live_model_bridge",
                "requestContext": {"source": "local_live_model_bridge"},
                "noCadChain": True,
            },
            "evidenceRefs": ["worker_run_state.json", f"task_envelopes/{envelope.get('taskId')}.json", *upstream_refs],
            "statePatchRequest": {"phase": str(envelope.get("stage") or ""), "phaseLabelForUser": str(envelope.get("stage") or "")},
            "agentSpecific": {
                "agentId": agent_id,
                "workerTaskEnvelope": envelope,
                "upstreamOutputs": [{"path": ref, "source": "worker_agent_output"} for ref in upstream_refs],
                "upstreamOutputRefs": upstream_refs,
                "cadExecutionAuthorized": False,
                "savedCurrentDwg": False,
            },
        }
        return run_prompt_pack_review(
            agent_id=agent_id,
            payload=payload,
            run_dir=run_dir,
            output_path=run_dir / output_rel,
            config=config,
            runner=runner,
            cwd=cwd,
            trace_id=agent_id.replace("_", "-"),
        )

    def _tool_intent(
        self,
        agent_id: str,
        intent_id: str,
        tool_name: str,
        permission_class: str,
        risk_level: str,
        inputs: dict[str, Any],
        target_scope: dict[str, Any],
        *,
        requested_effects: list[str] | None = None,
    ) -> dict[str, Any]:
        forbidden = (
            ["dwg_save", "delete_entities", "cad_write_formal_layer"]
            if permission_class == "cad_preview"
            else ["cad_write", "dwg_save", "delete_entities"]
        )
        intent = {
            "schemaVersion": "tool-intent/v1",
            "toolIntentId": intent_id,
            "requestedByAgentId": agent_id,
            "toolName": tool_name,
            "purpose": f"run {tool_name} through local live model bridge",
            "inputs": inputs,
            "targetScope": target_scope,
            "riskLevel": risk_level,
            "permissionClass": permission_class,
            "expectedEvidence": ["cad_reports"],
            "forbiddenEffects": forbidden,
        }
        if requested_effects:
            intent["requestedEffects"] = requested_effects
        return intent

    def _record_cad_preview_result(
        self,
        run_id: str,
        encoding_preflight: dict[str, Any],
        validate_trace: dict[str, Any],
        dry_trace: dict[str, Any],
        preview_trace: dict[str, Any],
        driver_mode: str,
    ) -> dict[str, Any]:
        preview = preview_trace.get("result") if isinstance(preview_trace.get("result"), dict) else {}
        state = self.get_run(run_id)
        state["completionClaim"] = "cad_mcp_preview_live"
        state["currentStage"] = "cad_mcp_preview_live"
        state["featureGates"] = self._feature_gates_for_stage("cad_mcp_preview_live")
        state["cadGeometryVerified"] = preview.get("cadGeometryVerified") is True
        runtime_status = "completed" if preview.get("status") == "pass" else "blocked"
        proof_status = "verified" if state["cadGeometryVerified"] else "not_verified"
        state["runtimeStatus"] = runtime_status
        state["proofStatus"] = proof_status
        state["encodingPreflight"] = encoding_preflight
        state["cadPreview"] = {
            "status": str(preview.get("status") or ""),
            "proofStatus": proof_status,
            "resultStatus": str(preview.get("resultStatus") or preview_trace.get("resultStatus") or ""),
            "driverMode": str(preview.get("driverMode") or driver_mode),
            "targetLayer": str(preview.get("targetLayer") or ""),
            "savedCurrentDwg": preview.get("savedCurrentDwg") is True,
            "cadGeometryVerified": preview.get("cadGeometryVerified") is True,
            "createdHandleCount": int(preview.get("createdHandleCount") or 0),
            "readbackStatus": str(preview.get("readbackStatus") or ""),
            "reportPath": str(preview.get("reportPath") or "cad_reports/cad_preview_tool_report.json"),
        }
        state["cadPreviewToolTraces"] = [
            str(item.get("downstreamArtifactPath") or "")
            for item in (validate_trace, dry_trace, preview_trace)
        ]
        state["writtenFiles"] = [
            "candidate_outputs/cad_plan.candidate.json",
            "cad_reports/validation_report.json",
            "cad_reports/dry_run_report.json",
            "cad_reports/cad_preview_tool_report.json",
            "cad_reports/execution_summary.json",
            "cad_reports/readback_summary.json",
            *state["cadPreviewToolTraces"],
        ]
        state["evidenceBoundary"] = [
            "model agents only produced schema-valid design judgement and handoff context",
            "preview CAD execution is orchestrator-owned through Tool Contract",
            "savedCurrentDwg=false and targetLayer=CODEX_PREVIEW are required",
            "fake_driver_preflight does not prove real AutoCAD geometry",
        ]
        state["state"] = runtime_status
        state.setdefault("auditEvents", []).append(
            self._audit_event(
                "cad_mcp_preview_tool_contract_completed",
                run_id=run_id,
                summary=str(preview.get("resultStatus") or preview_trace.get("resultStatus") or ""),
            )
        )
        self._touch(state)
        self._save_state(state)
        return state

    def _requires_registered_bridge(self, state: dict[str, Any]) -> bool:
        gates = state.get("featureGates") if isinstance(state.get("featureGates"), dict) else {}
        gate = gates.get("local_bridge_connected") if isinstance(gates.get("local_bridge_connected"), dict) else {}
        return gate.get("enabled") is True

    def _has_pending_capability_gap(self, state: dict[str, Any], capabilities: list[str]) -> bool:
        capability_set = set(capabilities)
        for task in state.get("tasks", []):
            if task.get("state") not in {"pending", "retry_scheduled"}:
                continue
            allowed = set(task.get("allowedTools", []))
            if allowed and not allowed.issubset(capability_set):
                return True
        return False


__all__ = [
    "AGENT_OUTPUT_SCHEMA",
    "TASK_ENVELOPE_SCHEMA",
    "WORKER_RUN_STATE_SCHEMA",
    "LocalLiveModelBridgeRuntime",
]
