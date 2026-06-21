"""Phase 12 mock plugin-like transaction contract.

This module models native-plugin transaction semantics without calling a
plugin, AutoCAD, CAD-MCP, or any DWG writer. Its outputs are deterministic
contract evidence only; they cannot satisfy real CAD readback.
"""

from __future__ import annotations

from typing import Any

from core.contracts.vnext import EvidenceItem, EvidencePackage


MOCK_PLUGIN_TRANSACTION_SCHEMA = "mock-plugin-transaction/p12/v1"
MOCK_PLUGIN_BACKEND = "mock_plugin_like"
P12_TRANSACTION_ALLOWED_EFFECTS = (
    "mock_plugin_transaction_execute",
    "mock_plugin_preview_commit",
    "mock_plugin_rollback_batch",
    "mock_ledger_ref_write",
)
P12_TRANSACTION_FORBIDDEN_EFFECTS = (
    "cad_execute",
    "real_cad_readback",
    "dwg_save",
    "save_current_dwg",
    "formal_layer_write",
    "delete_entities",
    "delete_non_created_entities",
    "registry_mutation",
    "table_c_mutation",
    "training_source_mutation",
    "protected_evidence_mutation",
    "plugin_call",
    "plugin_execute",
)

_MODE_OUTCOMES = {
    "success": {
        "status": "ready",
        "proofStatus": "mock_committed_preview",
        "rollbackStatus": "not_required",
        "committedPreview": True,
        "documentState": "preview_committed",
        "blockedReason": "",
        "retryable": False,
        "createdHandles": ["mock-handle-001", "mock-handle-002"],
    },
    "failure": {
        "status": "blocked",
        "proofStatus": "mock_failure_before_commit",
        "rollbackStatus": "not_started",
        "committedPreview": False,
        "documentState": "unchanged",
        "blockedReason": "mock_execution_failed_before_preview_commit",
        "retryable": True,
        "createdHandles": [],
    },
    "rollback_success": {
        "status": "blocked",
        "proofStatus": "mock_rollback_verified",
        "rollbackStatus": "rolled_back",
        "committedPreview": False,
        "documentState": "rolled_back",
        "blockedReason": "mock_audit_failed_after_preview_batch",
        "retryable": True,
        "createdHandles": ["mock-handle-001", "mock-handle-002"],
    },
    "rollback_failed": {
        "status": "blocked",
        "proofStatus": "mock_rollback_failed",
        "rollbackStatus": "rollback_failed",
        "committedPreview": False,
        "documentState": "in_flight_unknown",
        "blockedReason": "mock_rollback_failed_after_preview_batch",
        "retryable": False,
        "createdHandles": ["mock-handle-001", "mock-handle-002"],
    },
    "blocked": {
        "status": "blocked",
        "proofStatus": "mock_blocked_before_transaction",
        "rollbackStatus": "not_started",
        "committedPreview": False,
        "documentState": "unchanged",
        "blockedReason": "mock_policy_blocked",
        "retryable": False,
        "createdHandles": [],
    },
}


def execute_mock_plugin_transaction(
    *,
    mode: str = "success",
    transaction_id: str = "tx-p12-mock-001",
    rollback_required: bool = True,
) -> dict[str, Any]:
    """Return a deterministic mock plugin-like transaction result."""

    normalized_mode = str(mode or "success").strip()
    if normalized_mode not in _MODE_OUTCOMES:
        raise ValueError(f"unsupported mock transaction mode: {mode}")
    outcome = dict(_MODE_OUTCOMES[normalized_mode])
    created_handles = [str(item) for item in outcome["createdHandles"]]
    tx_id = str(transaction_id)
    return {
        "schemaVersion": MOCK_PLUGIN_TRANSACTION_SCHEMA,
        "phase": "Phase 12",
        "packageId": "phase12.mock-plugin-transaction",
        "taskId": "phase12.mock-plugin-transaction",
        "transactionId": tx_id,
        "backend": MOCK_PLUGIN_BACKEND,
        "adapterId": "mock-plugin.transaction",
        "mode": normalized_mode,
        "status": str(outcome["status"]),
        "verificationStatus": "not_verified",
        "proofStatus": str(outcome["proofStatus"]),
        "rollbackRequired": bool(rollback_required),
        "rollbackStatus": str(outcome["rollbackStatus"]),
        "committedPreview": bool(outcome["committedPreview"]),
        "createdHandles": created_handles,
        "createdHandlesRef": f"mock-ledger://{tx_id}/created-handles",
        "blockedReason": str(outcome["blockedReason"]),
        "retryable": bool(outcome["retryable"]),
        "documentState": str(outcome["documentState"]),
        "documentStateBefore": "mock_clean_memory_transaction",
        "documentStateAfter": str(outcome["documentState"]),
        "cadGeometryVerified": False,
        "cadWritesAttempted": False,
        "savedCurrentDwg": False,
        "targetLayer": "MOCK_PREVIEW_MEMORY",
        "ledgerRefs": _ledger_refs(transaction_id=tx_id, mode=normalized_mode),
        "allowedEffects": list(P12_TRANSACTION_ALLOWED_EFFECTS),
        "forbiddenEffects": list(P12_TRANSACTION_FORBIDDEN_EFFECTS),
        "completionBoundary": "mock_plugin_transaction_is_not_real_cad_readback",
        "notEvidenceFor": [
            "real_cad_readback",
            "cad_geometry_verified",
            "training_resume",
            "table_c_progress",
            "native_plugin_readiness",
            "current_dwg_save",
            "formal_layer_write",
        ],
    }


def mock_plugin_transaction_evidence_package(result: dict[str, Any]) -> EvidencePackage:
    """Wrap a mock transaction result as deterministic non-CAD evidence."""

    payload = dict(result)
    status = "pass" if payload.get("schemaVersion") == MOCK_PLUGIN_TRANSACTION_SCHEMA else "fail"
    ledger_refs = payload.get("ledgerRefs") if isinstance(payload.get("ledgerRefs"), dict) else {}
    ledger_status = "pass" if ledger_refs else "fail"
    return EvidencePackage(
        task_id=str(payload.get("taskId") or "phase12.mock-plugin-transaction"),
        items=[
            EvidenceItem(
                kind="mock_plugin_transaction",
                status=status,
                backend=MOCK_PLUGIN_BACKEND,
                cad_geometry_verified=False,
                metadata={
                    "transactionId": str(payload.get("transactionId") or ""),
                    "proofStatus": str(payload.get("proofStatus") or ""),
                    "rollbackStatus": str(payload.get("rollbackStatus") or ""),
                    "committedPreview": payload.get("committedPreview") is True,
                    "boundary": "mock transaction cannot satisfy real_cad_readback",
                },
            ),
            EvidenceItem(
                kind="mock_ledger_refs",
                status=ledger_status,
                backend=MOCK_PLUGIN_BACKEND,
                cad_geometry_verified=False,
                metadata={"ledgerRefs": dict(ledger_refs)},
            ),
            EvidenceItem(
                kind="no_save_guard",
                status="pass" if payload.get("savedCurrentDwg") is False else "fail",
                backend=MOCK_PLUGIN_BACKEND,
                cad_geometry_verified=False,
                metadata={"savedCurrentDwg": payload.get("savedCurrentDwg")},
            ),
        ],
    )


def _ledger_refs(*, transaction_id: str, mode: str) -> dict[str, str]:
    base = f"mock-ledger://{transaction_id}"
    refs = {
        "tool.requested": f"{base}/tool.requested",
        "tool.authorized": f"{base}/tool.authorized",
        "adapter.started": f"{base}/adapter.started",
        "adapter.completed": f"{base}/adapter.completed",
        "readback.recorded": f"{base}/mock-readback.recorded",
        "audit.completed": f"{base}/audit.completed",
    }
    if mode in {"failure", "rollback_success", "rollback_failed", "blocked"}:
        refs["rollback.applied"] = f"{base}/rollback.applied"
    return refs
