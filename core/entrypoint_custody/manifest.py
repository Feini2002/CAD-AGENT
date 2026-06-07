"""Machine-readable custody manifest for script and workflow entrypoints."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "config" / "entrypoint_custody_manifest.json"
DEFAULT_DENYLIST_PATH = PROJECT_ROOT / "config" / "entrypoint_denylist.json"
DEFAULT_KILL_SWITCH_PATH = PROJECT_ROOT / "config" / "entrypoint_kill_switch.json"

REQUIRED_ENTRY_FIELDS = {
    "entrypoint",
    "custodyStatus",
    "architectureLayer",
    "owner",
    "directInvocationPolicy",
    "requiresCustodyGate",
    "requiresLease",
    "leaseArgHashRequired",
    "riskClass",
    "allowedWriteScope",
    "maySaveCurrentDwg",
    "mayWriteTrainingFactSource",
    "mayWriteRegistry",
    "requiredGates",
    "evidenceProduced",
    "evidenceBoundary",
    "historyOnly",
}

VALID_CUSTODY_STATUSES = {
    "central_orchestrated",
    "delegated_tool",
    "diagnostic_readonly",
    "derived_display",
    "training_controlled",
    "asset_controlled",
    "capability_proof_history",
    "scene_benchmark_history",
    "deprecated_blocked",
}

VALID_DIRECT_POLICIES = {
    "allowed_readonly",
    "diagnostic_only",
    "blocked_without_lease",
    "deprecated_blocked",
}

HIGH_RISK_CLASSES = {
    "cad_or_dwg_write",
    "training_fact_write",
    "registry_write",
    "asset_controlled_write",
}


def _read_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return default


def _entry_map(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries = payload.get("entrypoints", [])
    if not isinstance(entries, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if isinstance(entry, dict) and entry.get("entrypoint"):
            result[str(entry["entrypoint"])] = entry
    return result


def load_entrypoint_manifest(path: Path | None = None) -> dict[str, Any]:
    manifest_path = path or DEFAULT_MANIFEST_PATH
    payload = _read_json(manifest_path, {})
    if not isinstance(payload, dict):
        payload = {}
    payload.setdefault("schemaVersion", "entrypoint-custody-manifest/v1")
    payload.setdefault("entrypoints", [])
    payload["manifestPath"] = str(manifest_path)
    payload["entrypointMap"] = _entry_map(payload)
    return payload


def load_denylist(path: Path | None = None) -> dict[str, Any]:
    denylist_path = path or DEFAULT_DENYLIST_PATH
    payload = _read_json(denylist_path, {})
    if not isinstance(payload, dict):
        payload = {}
    payload.setdefault("schemaVersion", "entrypoint-denylist/v1")
    payload.setdefault("denyPatterns", [])
    payload["denylistPath"] = str(denylist_path)
    return payload


def load_kill_switch(path: Path | None = None) -> dict[str, Any]:
    kill_switch_path = path or DEFAULT_KILL_SWITCH_PATH
    payload = _read_json(kill_switch_path, {})
    if not isinstance(payload, dict):
        payload = {}
    payload.setdefault("schemaVersion", "entrypoint-kill-switch/v1")
    payload.setdefault("globalEntrypointExecutionDisabled", False)
    payload.setdefault("disabledEntrypoints", [])
    payload.setdefault("disabledReason", "")
    payload["killSwitchPath"] = str(kill_switch_path)
    return payload


def manifest_entry_for(entrypoint: str, manifest: dict[str, Any] | None = None) -> dict[str, Any] | None:
    payload = manifest or load_entrypoint_manifest()
    entry_map = payload.get("entrypointMap")
    if not isinstance(entry_map, dict):
        entry_map = _entry_map(payload)
    entry = entry_map.get(entrypoint)
    return entry if isinstance(entry, dict) else None


def validate_manifest_entry(entry: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    missing = sorted(field for field in REQUIRED_ENTRY_FIELDS if field not in entry)
    if missing:
        findings.append(
            {
                "code": "manifest_entry_missing_required_fields",
                "severity": "blocked",
                "entrypoint": entry.get("entrypoint", ""),
                "missingFields": missing,
                "message": "manifest entry is missing required custody fields.",
            }
        )
    status = str(entry.get("custodyStatus", ""))
    if status and status not in VALID_CUSTODY_STATUSES:
        findings.append(
            {
                "code": "manifest_entry_invalid_custody_status",
                "severity": "blocked",
                "entrypoint": entry.get("entrypoint", ""),
                "custodyStatus": status,
                "message": "custodyStatus is not a known entrypoint class.",
            }
        )
    policy = str(entry.get("directInvocationPolicy", ""))
    if policy and policy not in VALID_DIRECT_POLICIES:
        findings.append(
            {
                "code": "manifest_entry_invalid_direct_invocation_policy",
                "severity": "blocked",
                "entrypoint": entry.get("entrypoint", ""),
                "directInvocationPolicy": policy,
                "message": "directInvocationPolicy is not recognized.",
            }
        )
    risk_class = str(entry.get("riskClass", ""))
    high_risk = risk_class in HIGH_RISK_CLASSES or status in {"training_controlled", "asset_controlled"}
    if high_risk:
        if not bool(entry.get("requiresCustodyGate")):
            findings.append(
                {
                    "code": "high_risk_entrypoint_missing_custody_gate",
                    "severity": "blocked",
                    "entrypoint": entry.get("entrypoint", ""),
                    "message": "high-risk entrypoint must require runtime custody guard.",
                }
            )
        if not bool(entry.get("requiresLease")):
            findings.append(
                {
                    "code": "high_risk_entrypoint_missing_lease",
                    "severity": "blocked",
                    "entrypoint": entry.get("entrypoint", ""),
                    "message": "high-risk entrypoint must require a custody lease.",
                }
            )
        if policy != "blocked_without_lease":
            findings.append(
                {
                    "code": "high_risk_entrypoint_allows_direct_invocation",
                    "severity": "blocked",
                    "entrypoint": entry.get("entrypoint", ""),
                    "message": "high-risk entrypoint must be blocked without lease.",
                }
            )
    return findings

