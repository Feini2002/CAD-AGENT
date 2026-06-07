"""Runtime guard for high-risk entrypoint invocation."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

from core.entrypoint_custody.manifest import (
    load_denylist,
    load_entrypoint_manifest,
    load_kill_switch,
    manifest_entry_for,
    validate_manifest_entry,
)


TRUSTED_LEASE_ISSUERS = {"workflow_dispatch", "tool_contract", "orchestrator_host", "test_fixture"}


def _utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def _parse_time(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _stable_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build_argv_hash(argv: list[str] | tuple[str, ...] | None) -> str:
    """Return a stable argv hash bound to the exact argument vector."""

    return "sha256:" + hashlib.sha256(_stable_json(list(argv or [])).encode("utf-8")).hexdigest()


def _read_json(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _block(reason_code: str, message: str, **extra: Any) -> dict[str, Any]:
    return {
        "custodyDecision": "blocked",
        "reasonCode": reason_code,
        "message": message,
        "leaseValidated": False,
        "writeScopeGranted": [],
        "writeScopeDenied": [],
        "preflightGateResults": [],
        "blockedReason": reason_code,
        **extra,
    }


def _denylist_match(entrypoint: str, argv: list[str], denylist: dict[str, Any]) -> dict[str, Any] | None:
    argv_text = " ".join(argv)
    patterns = denylist.get("denyPatterns", [])
    if not isinstance(patterns, list):
        return None
    for pattern in patterns:
        if not isinstance(pattern, dict):
            continue
        target = str(pattern.get("entrypoint", ""))
        if target not in {"*", entrypoint}:
            continue
        required_args = pattern.get("requiredArgs", [])
        denied_args = pattern.get("deniedArgs", [])
        if (required_args or denied_args) and isinstance(required_args, list) and all(str(arg) in argv for arg in required_args):
            if not denied_args or any(str(arg) in argv for arg in denied_args if str(arg)):
                return pattern
        contains = str(pattern.get("argvContains", ""))
        if contains and contains in argv_text:
            return pattern
    return None


def issue_custody_lease(
    *,
    entrypoint: str,
    argv: list[str] | tuple[str, ...] | None,
    run_id: str,
    task_id: str,
    issued_by: str = "workflow_dispatch",
    tool_intent_id: str = "",
    cad_plan_hash: str = "",
    permission_class: str = "diagnostic_only",
    allowed_write_scope: list[str] | None = None,
    may_write_cad: bool = False,
    may_save_current_dwg: bool = False,
    may_write_training_fact_source: bool = False,
    may_write_registry: bool = False,
    required_gates_satisfied: list[str] | None = None,
    ttl_seconds: int = 900,
    generated_at: str | None = None,
) -> dict[str, Any]:
    now = _parse_time(generated_at) if generated_at else _utc_now()
    if now is None:
        now = _utc_now()
    expires_at = now + timedelta(seconds=ttl_seconds)
    return {
        "schemaVersion": "entrypoint-custody-lease/v1",
        "leaseId": f"lease_{uuid4().hex}",
        "runId": run_id,
        "taskId": task_id,
        "issuedBy": issued_by,
        "entrypoint": entrypoint,
        "argvHash": build_argv_hash(list(argv or [])),
        "toolIntentId": tool_intent_id,
        "cadPlanHash": cad_plan_hash,
        "permissionClass": permission_class,
        "allowedWriteScope": list(allowed_write_scope or []),
        "mayWriteCad": may_write_cad,
        "maySaveCurrentDwg": may_save_current_dwg,
        "mayWriteTrainingFactSource": may_write_training_fact_source,
        "mayWriteRegistry": may_write_registry,
        "requiredGatesSatisfied": list(required_gates_satisfied or []),
        "issuedAt": now.isoformat().replace("+00:00", "Z"),
        "expiresAt": expires_at.isoformat().replace("+00:00", "Z"),
    }


def evaluate_entrypoint_custody(
    *,
    entrypoint: str,
    argv: list[str] | tuple[str, ...] | None = None,
    requested_write_scope: list[str] | None = None,
    requested_permission_class: str = "diagnostic_only",
    custody_lease: dict[str, Any] | None = None,
    custody_lease_path: Path | None = None,
    run_id: str = "",
    task_id: str = "",
    tool_intent_id: str = "",
    cad_plan_hash: str = "",
    may_save_current_dwg_requested: bool = False,
    may_write_training_fact_source_requested: bool = False,
    may_write_registry_requested: bool = False,
    target_layer: str = "",
    manifest: dict[str, Any] | None = None,
    denylist: dict[str, Any] | None = None,
    kill_switch: dict[str, Any] | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    argv_list = list(argv or [])
    requested_scope = list(requested_write_scope or [])
    active_manifest = manifest or load_entrypoint_manifest()
    entry = manifest_entry_for(entrypoint, active_manifest)
    if entry is None:
        return _block(
            "blocked_unregistered_entrypoint",
            "entrypoint is not registered in custody manifest.",
            entrypoint=entrypoint,
        )

    entry_findings = validate_manifest_entry(entry)
    if any(finding.get("severity") == "blocked" for finding in entry_findings):
        return _block(
            "blocked_invalid_manifest_entry",
            "entrypoint manifest entry is incomplete or invalid.",
            entrypoint=entrypoint,
            manifestFindings=entry_findings,
        )

    active_kill_switch = kill_switch or load_kill_switch()
    if bool(active_kill_switch.get("globalEntrypointExecutionDisabled")):
        return _block(
            "blocked_global_kill_switch",
            "global entrypoint kill switch is enabled.",
            entrypoint=entrypoint,
            disabledReason=active_kill_switch.get("disabledReason", ""),
        )
    disabled = {str(item) for item in active_kill_switch.get("disabledEntrypoints", []) if item}
    if entrypoint in disabled:
        return _block(
            "blocked_entrypoint_kill_switch",
            "entrypoint is disabled by kill switch.",
            entrypoint=entrypoint,
            disabledReason=active_kill_switch.get("disabledReason", ""),
        )

    active_denylist = denylist or load_denylist()
    denied = _denylist_match(entrypoint, argv_list, active_denylist)
    if denied is not None:
        return _block(
            str(denied.get("reasonCode") or "blocked_denylist_match"),
            str(denied.get("message") or "entrypoint argv matched denylist."),
            entrypoint=entrypoint,
            denyPattern=denied,
        )

    policy = str(entry.get("directInvocationPolicy", ""))
    requires_lease = bool(entry.get("requiresLease"))
    lease = custody_lease or _read_json(custody_lease_path)
    if policy == "deprecated_blocked" or str(entry.get("custodyStatus")) == "deprecated_blocked":
        return _block("blocked_deprecated_entrypoint", "entrypoint is deprecated and blocked.", entrypoint=entrypoint)
    if requires_lease and not lease:
        return _block(
            "blocked_missing_custody_lease",
            "high-risk entrypoint requires a custody lease.",
            entrypoint=entrypoint,
        )

    lease_validated = False
    if lease:
        if str(lease.get("issuedBy", "")) not in TRUSTED_LEASE_ISSUERS:
            return _block("blocked_untrusted_lease_issuer", "lease issuer is not trusted.", entrypoint=entrypoint)
        if str(lease.get("entrypoint", "")) != entrypoint:
            return _block("blocked_lease_entrypoint_mismatch", "lease entrypoint does not match.", entrypoint=entrypoint)
        if str(lease.get("argvHash", "")) != build_argv_hash(argv_list):
            return _block("blocked_lease_argv_hash_mismatch", "lease argvHash does not match.", entrypoint=entrypoint)
        if run_id and str(lease.get("runId", "")) != run_id:
            return _block("blocked_lease_run_mismatch", "lease runId does not match.", entrypoint=entrypoint)
        if task_id and str(lease.get("taskId", "")) != task_id:
            return _block("blocked_lease_task_mismatch", "lease taskId does not match.", entrypoint=entrypoint)
        if tool_intent_id and str(lease.get("toolIntentId", "")) != tool_intent_id:
            return _block("blocked_lease_tool_intent_mismatch", "lease toolIntentId does not match.", entrypoint=entrypoint)
        if cad_plan_hash and str(lease.get("cadPlanHash", "")) != cad_plan_hash:
            return _block("blocked_lease_cad_plan_hash_mismatch", "lease cadPlanHash does not match.", entrypoint=entrypoint)
        lease_permission_class = str(lease.get("permissionClass", ""))
        if requested_permission_class and lease_permission_class and lease_permission_class != requested_permission_class:
            return _block(
                "blocked_lease_permission_class_mismatch",
                "lease permissionClass does not match requested permission class.",
                entrypoint=entrypoint,
                leasePermissionClass=lease_permission_class,
                requestedPermissionClass=requested_permission_class,
            )
        cad_write_requested = requested_permission_class.startswith("cad_") or "CODEX_PREVIEW" in set(requested_scope)
        if cad_write_requested and not bool(lease.get("mayWriteCad")):
            return _block("blocked_lease_cad_write_not_granted", "lease does not grant CAD write permission.", entrypoint=entrypoint)
        if may_write_training_fact_source_requested and not bool(lease.get("mayWriteTrainingFactSource")):
            return _block(
                "blocked_lease_training_fact_write_not_granted",
                "lease does not grant training fact source write permission.",
                entrypoint=entrypoint,
            )
        if may_write_registry_requested and not bool(lease.get("mayWriteRegistry")):
            return _block(
                "blocked_lease_registry_write_not_granted",
                "lease does not grant registry write permission.",
                entrypoint=entrypoint,
            )
        expiry = _parse_time(str(lease.get("expiresAt", "")))
        active_now = _parse_time(now) if now else _utc_now()
        if expiry is None or active_now is None or expiry <= active_now:
            return _block("blocked_expired_custody_lease", "custody lease is expired.", entrypoint=entrypoint)
        lease_validated = True

    allowed_scope = [str(item) for item in entry.get("allowedWriteScope", []) if str(item)]
    if lease:
        lease_scope = [str(item) for item in lease.get("allowedWriteScope", []) if str(item)]
        if lease_scope:
            allowed_scope = [item for item in allowed_scope if item in set(lease_scope)]
    denied_scope = [scope for scope in requested_scope if scope not in set(allowed_scope)]
    if denied_scope:
        return _block(
            "blocked_write_scope_exceeds_manifest",
            "requested write scope exceeds manifest or lease grant.",
            entrypoint=entrypoint,
            writeScopeGranted=allowed_scope,
            writeScopeDenied=denied_scope,
        )
    if may_save_current_dwg_requested and not bool(entry.get("maySaveCurrentDwg")):
        return _block("blocked_current_dwg_save", "current business DWG save is not allowed.", entrypoint=entrypoint)
    if target_layer and target_layer != "CODEX_PREVIEW" and requested_permission_class.startswith("cad_"):
        return _block("blocked_non_preview_target_layer", "CAD write target layer must be CODEX_PREVIEW.", entrypoint=entrypoint)

    required_gates = [str(item) for item in entry.get("requiredGates", []) if str(item)]
    lease_gates = [str(item) for item in lease.get("requiredGatesSatisfied", [])] if lease else []
    missing_gates = [gate for gate in required_gates if lease and gate not in set(lease_gates)]
    if missing_gates:
        return _block(
            "blocked_required_gates_not_satisfied",
            "custody lease has not satisfied required gates.",
            entrypoint=entrypoint,
            missingGates=missing_gates,
        )

    return {
        "custodyDecision": "allowed",
        "reasonCode": "lease_validated" if lease_validated else "direct_readonly_allowed",
        "entrypoint": entrypoint,
        "custodyStatus": entry.get("custodyStatus"),
        "riskClass": entry.get("riskClass"),
        "directInvocationPolicy": policy,
        "leaseValidated": lease_validated,
        "writeScopeGranted": allowed_scope,
        "writeScopeDenied": [],
        "preflightGateResults": [f"{gate}:pass" for gate in required_gates if not lease or gate in set(lease_gates)],
        "blockedReason": None,
        "evidenceBoundary": entry.get("evidenceBoundary", []),
    }
