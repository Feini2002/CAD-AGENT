"""State helpers for the local live model bridge Worker contract."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import re
from pathlib import Path
from typing import Any, Iterable


WORKER_RUN_STATE_SCHEMA = "worker_run_state/v1"
TASK_ENVELOPE_SCHEMA = "worker_task_envelope/v1"
AGENT_OUTPUT_SCHEMA = "agent_output/v1"
FEATURE_GATE_STAGES = [
    "worker_orchestration_ready",
    "local_bridge_connected",
    "single_agent_live",
    "multi_agent_live",
    "cad_mcp_preview_live",
    "current_dwg_save",
]
FEATURE_GATE_ORDER = {stage: index for index, stage in enumerate(FEATURE_GATE_STAGES)}
FEATURE_GATE_NEXT_ACTION = {
    "local_bridge_connected": "register_or_start_local_bridge",
    "single_agent_live": "enable_codex_cli_model_review",
    "multi_agent_live": "enable_multi_agent_live_chain",
    "cad_mcp_preview_live": "enable_cad_preview_after_validate_and_dry_run",
    "current_dwg_save": "requires_explicit_save_authorization",
}
FORBIDDEN_WORKER_TOOLS = {"shell_arbitrary", "cmd", "powershell", "upload_full_repo"}
FORBIDDEN_WORKER_ACTIONS = {
    "shell_arbitrary",
    "save_current_dwg",
    "delete_unscoped_entities",
    "upload_full_repo",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slug(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_-]+", "-", value.strip()).strip("-").lower()
    return normalized or "run"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


class LocalLiveModelBridgeStateMixin:
    root_dir: Path

    def _feature_gates_for_stage(self, target_stage: str) -> dict[str, dict[str, Any]]:
        if target_stage not in FEATURE_GATE_ORDER:
            raise ValueError(f"unknown local live model bridge target_stage: {target_stage}")
        target_order = FEATURE_GATE_ORDER[target_stage]
        gates: dict[str, dict[str, Any]] = {}
        for stage in FEATURE_GATE_STAGES:
            enabled = stage != "current_dwg_save" and FEATURE_GATE_ORDER[stage] <= target_order
            gates[stage] = {
                "enabled": enabled,
                "enabledBy": f"target_stage:{target_stage}" if enabled else "default_closed",
                "nextAction": "" if enabled else FEATURE_GATE_NEXT_ACTION.get(stage, ""),
            }
        gates["worker_orchestration_ready"]["enabled"] = True
        gates["worker_orchestration_ready"]["enabledBy"] = (
            f"target_stage:{target_stage}" if target_stage != "worker_orchestration_ready" else "default_worker_only"
        )
        gates["worker_orchestration_ready"]["nextAction"] = ""
        gates["current_dwg_save"]["enabled"] = False
        gates["current_dwg_save"]["enabledBy"] = "default_closed"
        gates["current_dwg_save"]["nextAction"] = FEATURE_GATE_NEXT_ACTION["current_dwg_save"]
        return gates

    def _build_tasks(
        self,
        *,
        run_id: str,
        workspace_id: str,
        requested_by: str,
        target_stage: str,
        agent_ids: list[str],
        dependencies: dict[str, list[str]],
        task_specs: list[dict[str, Any]] | None,
    ) -> list[dict[str, Any]]:
        if task_specs is not None:
            return [
                self._task_from_spec(
                    run_id=run_id,
                    workspace_id=workspace_id,
                    requested_by=requested_by,
                    target_stage=target_stage,
                    index=index,
                    spec=spec,
                )
                for index, spec in enumerate(task_specs, start=1)
            ]
        task_ids = {agent_id: f"task_{agent_id}_001" for agent_id in agent_ids}
        return [
            self._task_from_spec(
                run_id=run_id,
                workspace_id=workspace_id,
                requested_by=requested_by,
                target_stage=target_stage,
                index=index,
                spec={
                    "taskId": task_ids[agent_id],
                    "agentId": agent_id,
                    "dependsOn": [task_ids[item] for item in dependencies.get(agent_id, []) if item in task_ids],
                    "allowedTools": ["codex_cli_model_review"],
                },
            )
            for index, agent_id in enumerate(agent_ids, start=1)
        ]

    def _task_from_spec(
        self,
        *,
        run_id: str,
        workspace_id: str,
        requested_by: str,
        target_stage: str,
        index: int,
        spec: dict[str, Any],
    ) -> dict[str, Any]:
        agent_id = str(spec.get("agentId") or f"agent_{index}")
        task_id = str(spec.get("taskId") or f"task_{agent_id}_{index:03d}")
        allowed_tools = [str(item) for item in spec.get("allowedTools", ["codex_cli_model_review"]) if str(item)]
        forbidden_actions = [
            str(item)
            for item in spec.get(
                "forbiddenActions",
                ["shell_arbitrary", "save_current_dwg", "delete_unscoped_entities", "upload_full_repo"],
            )
            if str(item)
        ]
        timeout_seconds = int(spec.get("timeoutSeconds") or 30)
        envelope = {
            "schemaVersion": TASK_ENVELOPE_SCHEMA,
            "runId": run_id,
            "taskId": task_id,
            "workspaceId": workspace_id,
            "requestedBy": requested_by,
            "stage": target_stage,
            "agentId": agent_id,
            "promptPackId": str(spec.get("promptPackId") or agent_id),
            "inputRefs": list(spec.get("inputRefs", [])) if isinstance(spec.get("inputRefs", []), list) else [],
            "allowedTools": allowed_tools,
            "forbiddenActions": forbidden_actions,
            "outputSchema": str(spec.get("outputSchema") or f"agent_output/{agent_id}/v1"),
            "timeoutSeconds": timeout_seconds,
            "idempotencyKey": str(spec.get("idempotencyKey") or f"{run_id}:{task_id}:attempt"),
        }
        return {
            "taskId": task_id,
            "agentId": agent_id,
            "state": "pending",
            "dependsOn": [str(item) for item in spec.get("dependsOn", []) if str(item)],
            "attempt": 0,
            "retryCount": 0,
            "maxAttempts": int(spec.get("maxAttempts") or 1),
            "timeoutSeconds": timeout_seconds,
            "leasedBy": "",
            "leaseExpiresAt": "",
            "heartbeatAt": "",
            "blockedReason": "",
            "allowedTools": allowed_tools,
            "forbiddenActions": forbidden_actions,
            "envelope": envelope,
        }

    def _progress_run(self, state: dict[str, Any]) -> None:
        changed = True
        while changed:
            changed = False
            for task in state.get("tasks", []):
                if task.get("state") not in {"pending", "retry_scheduled"}:
                    continue
                blocked_dependency = self._blocked_dependency(state, task)
                if blocked_dependency:
                    self._block_task(state, task, f"upstream {blocked_dependency} blocked")
                    changed = True
                    continue
                if not self._dependencies_completed(state, task):
                    continue
                if self._security_blocked(task):
                    self._block_task(state, task, "security_blocked", security=True)
                    changed = True
        tasks = state.get("tasks", [])
        if any(task.get("state") == "blocked" for task in tasks):
            state["state"] = "blocked"
        elif tasks and all(task.get("state") == "completed" for task in tasks):
            state["state"] = "completed"
        elif state.get("state") not in {"cancelled", "leasing"}:
            state["state"] = "queued"
        self._save_state(state)

    def _next_leaseable_task(self, state: dict[str, Any], capabilities: list[str]) -> dict[str, Any] | None:
        capability_set = set(capabilities)
        for task in state.get("tasks", []):
            if task.get("state") not in {"pending", "retry_scheduled"}:
                continue
            if not self._dependencies_completed(state, task):
                continue
            if self._security_blocked(task):
                self._block_task(state, task, "security_blocked", security=True)
                continue
            allowed = set(task.get("allowedTools", []))
            if allowed and not allowed.issubset(capability_set):
                continue
            return task
        return None

    def _normalize_agent_output(self, state: dict[str, Any], task: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
        status = str(result.get("status") or "completed")
        return {
            "schemaVersion": str(result.get("schemaVersion") or AGENT_OUTPUT_SCHEMA),
            "runId": state["runId"],
            "taskId": task["taskId"],
            "agentId": task["agentId"],
            "status": status,
            "decision": str(result.get("decision") or "continue"),
            "summary": str(result.get("summary") or ""),
            "modelInvoked": bool(result.get("modelInvoked")),
            "modelUnavailable": bool(result.get("modelUnavailable")),
            "schemaValid": bool(result.get("schemaValid")),
            "needsMoreEvidence": bool(result.get("needsMoreEvidence")),
            "blockedReason": str(result.get("blockedReason") or ""),
            "evidenceRefs": list(result.get("evidenceRefs", [])) if isinstance(result.get("evidenceRefs", []), list) else [],
            "traceRef": str(result.get("traceRef") or ""),
        }

    def _security_blocked(self, task: dict[str, Any]) -> bool:
        tools = {str(item) for item in task.get("allowedTools", [])}
        envelope_tools = {str(item) for item in task.get("envelope", {}).get("allowedTools", [])}
        requested = {str(item) for item in task.get("requestedActions", [])}
        actions = {str(item) for item in task.get("forbiddenActions", [])}
        return bool(
            tools & FORBIDDEN_WORKER_TOOLS
            or envelope_tools & FORBIDDEN_WORKER_TOOLS
            or requested & FORBIDDEN_WORKER_ACTIONS
            or ("shell_arbitrary" in actions and "shell_arbitrary" in tools)
        )

    def _block_task(self, state: dict[str, Any], task: dict[str, Any], reason: str, *, security: bool = False) -> None:
        task["state"] = "blocked"
        task["blockedReason"] = reason
        if reason and reason not in state.setdefault("blockedReasons", []):
            state["blockedReasons"].append(reason)
        if security:
            if "security_blocked" not in state.setdefault("securityBlocks", []):
                state["securityBlocks"].append("security_blocked")
            state["circuitBreakers"]["security_gate"]["state"] = "open"
            state["circuitBreakers"]["security_gate"]["reason"] = reason
        state.setdefault("auditEvents", []).append(
            self._audit_event("task_blocked", run_id=state["runId"], task_id=task["taskId"], summary=reason)
        )

    def _dependencies_completed(self, state: dict[str, Any], task: dict[str, Any]) -> bool:
        tasks = {str(item.get("taskId")): item for item in state.get("tasks", [])}
        return all(tasks.get(dep, {}).get("state") == "completed" for dep in task.get("dependsOn", []))

    def _blocked_dependency(self, state: dict[str, Any], task: dict[str, Any]) -> str:
        tasks = {str(item.get("taskId")): item for item in state.get("tasks", [])}
        for dep in task.get("dependsOn", []):
            if tasks.get(dep, {}).get("state") in {"blocked", "failed", "cancelled"}:
                return str(dep)
        return ""

    def _task_by_id(self, state: dict[str, Any], task_id: str) -> dict[str, Any] | None:
        for task in state.get("tasks", []):
            if task.get("taskId") == task_id:
                return task
        return None

    def _run_dir(self, run_id: str) -> Path:
        return self.root_dir / run_id

    def _state_path(self, run_id: str) -> Path:
        return self._run_dir(run_id) / "worker_run_state.json"

    def _save_state(self, state: dict[str, Any]) -> None:
        write_json(self._state_path(str(state["runId"])), state)
        for task in state.get("tasks", []):
            write_json(self._run_dir(str(state["runId"])) / "task_envelopes" / f"{task['taskId']}.json", task["envelope"])

    def _load_state(self, run_id: str) -> dict[str, Any]:
        return read_json(self._state_path(run_id))

    def _bridge_registry_path(self) -> Path:
        return self.root_dir / "bridge_registry.json"

    def _load_bridge_registry(self) -> dict[str, dict[str, Any]]:
        registry = read_json(self._bridge_registry_path())
        return {str(key): value for key, value in registry.items() if isinstance(value, dict)}

    def _save_bridge_registry(self, registry: dict[str, dict[str, Any]]) -> None:
        write_json(self._bridge_registry_path(), registry)

    def _mark_waiting_for_bridge(self, *, run_id: str | None, bridge_id: str, reason: str) -> None:
        for state in self._iter_states(run_id=run_id):
            if state.get("state") in {"completed", "blocked", "failed", "cancelled"}:
                continue
            state["state"] = "waiting_for_bridge"
            state["circuitBreakers"]["local_bridge"]["state"] = "open"
            state["circuitBreakers"]["local_bridge"]["reason"] = reason
            if reason not in state.setdefault("blockedReasons", []):
                state["blockedReasons"].append(reason)
            state.setdefault("auditEvents", []).append(
                self._audit_event("bridge_unavailable", run_id=state["runId"], summary=f"{bridge_id}: {reason}")
            )
            self._touch(state)
            self._save_state(state)

    def _iter_states(self, *, run_id: str | None = None) -> Iterable[dict[str, Any]]:
        if run_id:
            state = self._load_state(run_id)
            if state:
                yield state
            return
        for state_path in sorted(self.root_dir.glob("run_*/worker_run_state.json")):
            state = read_json(state_path)
            if state:
                yield state

    def _touch(self, state: dict[str, Any], *, at: datetime | None = None) -> None:
        state["updatedAt"] = iso(at or self._now())

    def _audit_event(
        self,
        event_type: str,
        *,
        run_id: str,
        summary: str,
        task_id: str = "",
        at: datetime | None = None,
    ) -> dict[str, Any]:
        return {
            "schemaVersion": "worker_audit_event/v1",
            "eventType": event_type,
            "runId": run_id,
            "taskId": task_id,
            "summary": summary,
            "at": iso(at or self._now()),
        }

    def _parse_time(self, value: str) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    def _default_circuit_breakers(self) -> dict[str, dict[str, Any]]:
        return {
            "local_bridge": {"state": "closed", "reason": "", "openedAt": ""},
            "codex_cli_model_review": {"state": "closed", "reason": "", "openedAt": ""},
            "cad_mcp_preview": {"state": "closed", "reason": "", "openedAt": ""},
            "worker_queue": {"state": "closed", "reason": "", "openedAt": ""},
            "security_gate": {"state": "closed", "reason": "", "openedAt": ""},
        }
