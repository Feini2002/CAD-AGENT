"""Phase 13 native thin backend skeleton contract.

This module describes the native plugin backend boundary without connecting to
AutoCAD or invoking a plugin. It only produces deterministic contract evidence
for Tool Gateway / Adapter Registry intake.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Callable

from core.contracts.vnext import EvidenceItem, EvidencePackage
from core.safety.policy import PREVIEW_LAYER


NATIVE_THIN_BACKEND_SCHEMA = "native-thin-backend/p13/v1"
NATIVE_THIN_PREFLIGHT_SCHEMA = "native-thin-preflight/p13b/v1"
NATIVE_THIN_AUTHORIZATION_SCHEMA = "native-thin-authorization/p13c/v1"
NATIVE_THIN_EXECUTION_RECEIPT_SCHEMA = "native-thin-execution-receipt/p13c/v1"
NATIVE_THIN_READINESS_SCHEMA = "native-thin-readiness/p13d/v1"
NATIVE_THIN_LIVE_SPIKE_GATE_SCHEMA = "native-thin-live-spike-gate/p13e/v1"
NATIVE_THIN_LIVE_SPIKE_SCHEMA = "native-thin-live-spike/p13f/v1"
NATIVE_THIN_AUTOCAD_PLUGIN_RESULT_SCHEMA = "native-thin-autocad-plugin-result/p13f/v1"
NATIVE_THIN_BACKEND = "native_thin_skeleton"
NATIVE_THIN_LIVE_BACKEND = "native_thin_live_backend"
P13_NATIVE_ALLOWED_EFFECTS = (
    "native_thin_contract_prepare",
    "native_thin_no_save_audit",
    "native_thin_rollback_proof_record",
    "native_thin_ledger_ref_write",
    "native_thin_scope_receipt_write",
    "native_thin_preflight_packet_write",
    "native_thin_launch_packet_write",
    "native_thin_live_authorization_gate_write",
    "native_thin_execution_receipt_write",
    "native_thin_live_readiness_packet_write",
    "native_thin_operator_authorization_request_write",
    "native_thin_live_spike_execution_gate_write",
    "native_thin_external_blocker_closeout_write",
)
P13_NATIVE_FORBIDDEN_EFFECTS = (
    "native_plugin_execute",
    "plugin_execute",
    "plugin_call",
    "cad_execute",
    "cad_preview_write",
    "apply_preview_batch",
    "real_cad_readback",
    "dwg_save",
    "save_current_dwg",
    "commit_save",
    "save_copy",
    "formal_layer_write",
    "delete_entities",
    "delete_non_created_entities",
    "registry_mutation",
    "table_c_mutation",
    "training_source_mutation",
    "protected_evidence_mutation",
)
P13_NATIVE_LIVE_ALLOWED_EFFECTS = (
    "native_thin_scoped_live_spike_execute",
    "native_thin_created_handles_readback",
    "native_thin_bbox_layer_entity_audit",
    "native_thin_rollback_created_handles",
    "native_thin_no_save_audit",
)
P13_NATIVE_LIVE_FORBIDDEN_EFFECTS = P13_NATIVE_FORBIDDEN_EFFECTS

_MODE_OUTCOMES = {
    "contract_ready": {
        "status": "ready",
        "proofStatus": "native_skeleton_contract_ready",
        "blockedReason": "",
        "retryable": False,
    },
    "blocked": {
        "status": "blocked",
        "proofStatus": "native_skeleton_blocked_before_backend",
        "blockedReason": "native_backend_scope_not_confirmed",
        "retryable": False,
    },
}


def execute_native_thin_backend_skeleton(
    *,
    mode: str = "contract_ready",
    transaction_id: str = "tx-p13-native-skeleton-001",
    rollback_required: bool = True,
) -> dict[str, Any]:
    """Return a deterministic native thin backend skeleton result."""

    normalized_mode = str(mode or "contract_ready").strip()
    if normalized_mode not in _MODE_OUTCOMES:
        raise ValueError(f"unsupported native thin backend mode: {mode}")
    outcome = dict(_MODE_OUTCOMES[normalized_mode])
    tx_id = str(transaction_id)
    rollback_status = "not_started"
    document_state = "not_connected"
    no_save_audit = {
        "status": "not_run_no_cad",
        "saveAttempted": False,
        "saveAllowed": False,
        "savedCurrentDwg": False,
        "auditRef": f"native-ledger://{tx_id}/no-save.audit",
        "boundary": "no AutoCAD connection or native plugin execution in P13 first package",
    }
    rollback_proof = {
        "status": "not_run_no_transaction",
        "rollbackRequired": bool(rollback_required),
        "rollbackStatus": rollback_status,
        "verified": False,
        "proofRef": f"native-ledger://{tx_id}/rollback.applied",
        "boundary": "rollback proof awaits scoped real native backend transaction",
    }
    return {
        "schemaVersion": NATIVE_THIN_BACKEND_SCHEMA,
        "phase": "Phase 13",
        "packageId": "phase13.native-thin-backend",
        "taskId": "phase13.native-thin-backend",
        "transactionId": tx_id,
        "backend": NATIVE_THIN_BACKEND,
        "adapterId": "native-thin.backend",
        "mode": normalized_mode,
        "status": str(outcome["status"]),
        "verificationStatus": "not_verified",
        "proofStatus": str(outcome["proofStatus"]),
        "rollbackRequired": bool(rollback_required),
        "rollbackStatus": rollback_status,
        "committedPreview": False,
        "createdHandles": [],
        "createdHandlesRef": f"native-ledger://{tx_id}/created-handles",
        "blockedReason": str(outcome["blockedReason"]),
        "retryable": bool(outcome["retryable"]),
        "documentState": document_state,
        "documentStateBefore": document_state,
        "documentStateAfter": document_state,
        "cadGeometryVerified": False,
        "cadWritesAttempted": False,
        "nativePluginInvoked": False,
        "savedCurrentDwg": False,
        "previewStrategy": "memory_transaction",
        "targetLayer": "CODEX_PREVIEW",
        "noSaveAudit": no_save_audit,
        "rollbackProof": rollback_proof,
        "ledgerRefs": _ledger_refs(transaction_id=tx_id),
        "allowedEffects": list(P13_NATIVE_ALLOWED_EFFECTS),
        "forbiddenEffects": list(P13_NATIVE_FORBIDDEN_EFFECTS),
        "completionBoundary": "native_thin_skeleton_is_not_native_plugin_execution_or_real_cad_readback",
        "notEvidenceFor": [
            "native_plugin_execution",
            "real_cad_readback",
            "cad_geometry_verified",
            "training_resume",
            "table_c_progress",
            "current_dwg_save",
            "formal_layer_write",
        ],
    }


def native_thin_backend_evidence_package(result: dict[str, Any]) -> EvidencePackage:
    """Wrap native thin skeleton result as deterministic non-CAD evidence."""

    payload = dict(result)
    no_save = payload.get("noSaveAudit") if isinstance(payload.get("noSaveAudit"), dict) else {}
    rollback = payload.get("rollbackProof") if isinstance(payload.get("rollbackProof"), dict) else {}
    ledger_refs = payload.get("ledgerRefs") if isinstance(payload.get("ledgerRefs"), dict) else {}
    schema_ok = payload.get("schemaVersion") == NATIVE_THIN_BACKEND_SCHEMA
    return EvidencePackage(
        task_id=str(payload.get("taskId") or "phase13.native-thin-backend"),
        items=[
            EvidenceItem(
                kind="native_thin_backend_contract",
                status="pass" if schema_ok else "fail",
                backend=NATIVE_THIN_BACKEND,
                cad_geometry_verified=False,
                metadata={
                    "transactionId": str(payload.get("transactionId") or ""),
                    "proofStatus": str(payload.get("proofStatus") or ""),
                    "nativePluginInvoked": payload.get("nativePluginInvoked") is True,
                    "boundary": "skeleton contract only; no native plugin execution",
                },
            ),
            EvidenceItem(
                kind="native_thin_no_save_audit",
                status="pass" if no_save.get("savedCurrentDwg") is False else "fail",
                backend=NATIVE_THIN_BACKEND,
                cad_geometry_verified=False,
                metadata=dict(no_save),
            ),
            EvidenceItem(
                kind="native_thin_rollback_proof",
                status="pass" if rollback.get("rollbackStatus") == "not_started" else "fail",
                backend=NATIVE_THIN_BACKEND,
                cad_geometry_verified=False,
                metadata=dict(rollback),
            ),
            EvidenceItem(
                kind="native_thin_ledger_refs",
                status="pass" if ledger_refs else "fail",
                backend=NATIVE_THIN_BACKEND,
                cad_geometry_verified=False,
                metadata={"ledgerRefs": dict(ledger_refs)},
            ),
            EvidenceItem(
                kind="no_save_guard",
                status="pass" if payload.get("savedCurrentDwg") is False else "fail",
                backend=NATIVE_THIN_BACKEND,
                cad_geometry_verified=False,
                metadata={"savedCurrentDwg": payload.get("savedCurrentDwg")},
            ),
        ],
    )


def build_native_thin_backend_scope_receipt(
    *,
    cad_plan: dict[str, Any] | None,
    output_dir: str | Path | None = None,
    scope_confirmed: bool = False,
    confirmation_statement: str = "",
    backend_identity: str | dict[str, Any] = "",
    readback_plan: dict[str, Any] | None = None,
    rollback_plan: dict[str, Any] | None = None,
    no_save_guard: dict[str, Any] | None = None,
    transaction_id: str = "tx-p13b-native-preflight-001",
) -> dict[str, Any]:
    """Build a P13B native thin scope receipt without executing CAD or plugins."""

    backend = _backend_identity(backend_identity)
    readback = dict(readback_plan or {})
    rollback = dict(rollback_plan or {})
    no_save = dict(no_save_guard or {})
    blockers: list[str] = []
    if not scope_confirmed:
        blockers.append("native_scope_not_confirmed")
    if not isinstance(cad_plan, dict) or not cad_plan:
        blockers.append("cad_plan_required")
    else:
        if _cad_plan_layer(cad_plan) != PREVIEW_LAYER:
            blockers.append("target_layer_must_be_CODEX_PREVIEW")
    if not backend["backend"]:
        blockers.append("backend_identity_required")
    elif backend["backend"] != "native-thin-skeleton":
        blockers.append("backend_identity_must_be_native_thin_skeleton")
    if readback.get("required") is not True:
        blockers.append("readback_plan_required")
    if rollback.get("required") is not True:
        blockers.append("rollback_plan_required")
    if no_save.get("required") is not True:
        blockers.append("no_save_guard_required")
    if no_save and no_save.get("saveAllowed") is not False:
        blockers.append("no_save_guard_must_block_save")

    receipt = _p13b_base_packet(
        kind="scope_receipt",
        status="blocked" if blockers else "ready",
        transaction_id=transaction_id,
        cad_plan=cad_plan,
        backend_identity=backend,
        blocking_reasons=blockers,
        readback_plan=readback,
        rollback_plan=rollback,
        no_save_guard=no_save,
    )
    receipt["scopeConfirmed"] = bool(scope_confirmed)
    receipt["confirmationStatement"] = str(confirmation_statement)
    receipt["allowedEffects"] = ["native_thin_scope_receipt_write"]
    receipt["nextAllowedEffects"] = [
        "native_thin_preflight_packet_write",
        "native_thin_launch_packet_write",
    ]
    if output_dir is not None:
        receipt["artifacts"]["nativeThinScopeReceipt"] = _write_json(
            output_dir=output_dir,
            filename="native_thin_scope_receipt.json",
            payload=receipt,
        )
    return receipt


def build_native_thin_backend_launch_packet(
    *,
    scope_receipt: dict[str, Any] | None = None,
    scope_receipt_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    transaction_id: str = "tx-p13b-native-launch-001",
) -> dict[str, Any]:
    """Build a P13B launch packet that stops before real native execution."""

    receipt, receipt_blockers = _load_scope_receipt(scope_receipt=scope_receipt, scope_receipt_path=scope_receipt_path)
    blockers = list(receipt_blockers)
    if receipt and receipt.get("status") != "ready":
        blockers.append("native_scope_receipt_not_ready")
    backend = _backend_identity(dict(receipt.get("backendIdentity") or {}) if receipt else "")
    readback = dict(receipt.get("readbackPlan") or {}) if receipt else {}
    rollback = dict(receipt.get("rollbackPlan") or {}) if receipt else {}
    no_save = dict(receipt.get("noSaveGuard") or {}) if receipt else {}
    cad_plan = dict(receipt.get("cadPlan") or {}) if receipt else None
    if receipt and str(receipt.get("targetLayer") or "") != PREVIEW_LAYER:
        blockers.append("target_layer_must_be_CODEX_PREVIEW")
    if receipt and backend["backend"] != "native-thin-skeleton":
        blockers.append("backend_identity_must_be_native_thin_skeleton")
    if receipt and readback.get("required") is not True:
        blockers.append("readback_plan_required")
    if receipt and rollback.get("required") is not True:
        blockers.append("rollback_plan_required")
    if receipt and no_save.get("saveAllowed") is not False:
        blockers.append("no_save_guard_must_block_save")

    packet = _p13b_base_packet(
        kind="launch_packet",
        status="blocked" if blockers else "ready",
        transaction_id=transaction_id,
        cad_plan=cad_plan,
        backend_identity=backend,
        blocking_reasons=_unique(blockers),
        readback_plan=readback,
        rollback_plan=rollback,
        no_save_guard=no_save,
    )
    packet["scopeReceiptReady"] = bool(receipt and receipt.get("status") == "ready" and not blockers)
    receipt_artifacts = dict(receipt.get("artifacts") or {}) if receipt else {}
    packet["scopeReceiptPath"] = str(scope_receipt_path or receipt_artifacts.get("nativeThinScopeReceipt") or "")
    packet["launchPacketReady"] = packet["status"] == "ready"
    packet["launchAllowed"] = False
    packet["liveExecutionAuthorized"] = False
    packet["nextStep"] = "request_user_authorization_for_native_live_spike"
    packet["allowedEffects"] = ["native_thin_preflight_packet_write", "native_thin_launch_packet_write"]
    packet["nextAllowedEffects"] = []
    if output_dir is not None:
        packet["artifacts"]["nativeThinLaunchPacket"] = _write_json(
            output_dir=output_dir,
            filename="native_thin_launch_packet.json",
            payload=packet,
        )
    return packet


def build_native_thin_backend_authorization_gate(
    *,
    launch_packet: dict[str, Any] | None = None,
    launch_packet_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    user_authorization: dict[str, Any] | None = None,
    transaction_id: str = "tx-p13c-native-authorization-001",
) -> dict[str, Any]:
    """Build the P13C live-spike authorization gate without starting CAD."""

    packet, packet_blockers = _load_launch_packet(
        launch_packet=launch_packet,
        launch_packet_path=launch_packet_path,
    )
    blockers = list(packet_blockers)
    blockers.extend(_launch_packet_blockers(packet))
    packet_hash = _launch_packet_hash(packet) if packet else ""
    auth = dict(user_authorization or {})
    explicit_authorization = auth.get("explicit") is True

    if explicit_authorization:
        blockers.extend(_user_authorization_blockers(auth=auth, packet_hash=packet_hash))
    elif not blockers:
        blockers.append("native_live_user_authorization_required")

    status = "blocked" if blockers else "ready"
    if not explicit_authorization and blockers == ["native_live_user_authorization_required"]:
        authorization_status = "authorization_pending"
    elif status == "ready":
        authorization_status = "authorized"
    else:
        authorization_status = "blocked"

    gate = _p13c_authorization_base(
        kind="authorization_gate",
        status=status,
        transaction_id=transaction_id,
        launch_packet=packet,
        launch_packet_hash=packet_hash,
        authorization_status=authorization_status,
        blocking_reasons=_unique(blockers),
        user_authorization=auth,
    )
    gate["allowedEffects"] = ["native_thin_live_authorization_gate_write"]
    gate["nextAllowedEffects"] = ["native_thin_execution_receipt_write"] if gate["status"] == "ready" else []
    if output_dir is not None:
        gate["artifacts"]["nativeThinAuthorizationGate"] = _write_json(
            output_dir=output_dir,
            filename="native_thin_authorization_gate.json",
            payload=gate,
        )
    return gate


def build_native_thin_backend_execution_receipt(
    *,
    authorization_gate: dict[str, Any] | None = None,
    authorization_gate_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    transaction_id: str = "tx-p13c-native-execution-receipt-001",
) -> dict[str, Any]:
    """Build a scoped execution receipt without executing the native backend."""

    gate, gate_blockers = _load_authorization_gate(
        authorization_gate=authorization_gate,
        authorization_gate_path=authorization_gate_path,
    )
    blockers = list(gate_blockers)
    if gate:
        if gate.get("schemaVersion") != NATIVE_THIN_AUTHORIZATION_SCHEMA:
            blockers.append("native_authorization_gate_schema_invalid")
        if gate.get("status") != "ready" or gate.get("authorizationStatus") != "authorized":
            blockers.append("native_live_authorization_not_ready")
        if gate.get("liveExecutionAuthorized") is not True:
            blockers.append("native_live_authorization_not_ready")
        if gate.get("scopeMatch") is not True:
            blockers.append("native_scope_hash_mismatch")
    status = "blocked" if blockers else "ready"
    receipt = _p13c_execution_receipt_base(
        status=status,
        transaction_id=transaction_id,
        authorization_gate=gate,
        blocking_reasons=_unique(blockers),
    )
    receipt["allowedEffects"] = ["native_thin_execution_receipt_write"]
    receipt["nextAllowedEffects"] = []
    if output_dir is not None:
        receipt["artifacts"]["nativeThinExecutionReceipt"] = _write_json(
            output_dir=output_dir,
            filename="native_thin_execution_receipt.json",
            payload=receipt,
        )
    return receipt


def build_native_thin_backend_readiness_packet(
    *,
    execution_receipt: dict[str, Any] | None = None,
    execution_receipt_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    expected_authorization_receipt_hash: str = "",
    transaction_id: str = "tx-p13d-native-readiness-001",
) -> dict[str, Any]:
    """Build the P13D operator authorization request without executing CAD."""

    receipt, receipt_blockers = _load_execution_receipt(
        execution_receipt=execution_receipt,
        execution_receipt_path=execution_receipt_path,
    )
    blockers = list(receipt_blockers)
    blockers.extend(_execution_receipt_blockers(receipt))
    receipt_hash = _execution_receipt_hash(receipt) if receipt else ""
    expected_hash = str(expected_authorization_receipt_hash or "")
    if expected_hash and expected_hash != receipt_hash:
        blockers.append("native_authorization_receipt_hash_mismatch")

    status = "blocked" if blockers else "ready_for_user_authorization"
    readiness = _p13d_readiness_base(
        status=status,
        transaction_id=transaction_id,
        execution_receipt=receipt,
        receipt_hash=receipt_hash,
        expected_receipt_hash=expected_hash,
        blocking_reasons=_unique(blockers),
    )
    readiness["allowedEffects"] = [
        "native_thin_live_readiness_packet_write",
        "native_thin_operator_authorization_request_write",
    ]
    readiness["operatorAuthorizationRequest"] = _operator_authorization_request(readiness)
    if output_dir is not None:
        root = Path(output_dir)
        request_path = root / "native_thin_operator_authorization_request.json"
        packet_path = root / "native_thin_readiness_packet.json"
        readiness["artifacts"]["nativeThinOperatorAuthorizationRequest"] = str(request_path)
        readiness["artifacts"]["nativeThinReadinessPacket"] = str(packet_path)
        _write_json(
            output_dir=root,
            filename="native_thin_operator_authorization_request.json",
            payload=readiness["operatorAuthorizationRequest"],
        )
        _write_json(
            output_dir=root,
            filename="native_thin_readiness_packet.json",
            payload=readiness,
        )
    return readiness


def build_native_thin_backend_live_spike_execution_gate(
    *,
    readiness_packet: dict[str, Any] | None = None,
    readiness_packet_path: str | Path | None = None,
    operator_authorization: dict[str, Any] | None = None,
    environment: dict[str, Any] | None = None,
    output_dir: str | Path | None = None,
    transaction_id: str = "tx-p13e-native-live-spike-gate-001",
) -> dict[str, Any]:
    """Build the P13E live spike gate or external blocker closeout.

    This does not connect to AutoCAD or invoke a native plugin. It only proves
    whether a P13D readiness packet plus separate operator authorization is
    sufficient to reach the live-spike execution boundary.
    """

    readiness, readiness_blockers = _load_readiness_packet(
        readiness_packet=readiness_packet,
        readiness_packet_path=readiness_packet_path,
    )
    blockers = list(readiness_blockers)
    blockers.extend(_readiness_packet_blockers(readiness))
    readiness_hash = _readiness_packet_hash(readiness) if readiness else ""
    auth = dict(operator_authorization or {})
    auth_blockers: list[str] = []
    env_blockers: list[str] = []

    if not blockers:
        auth_blockers = _operator_live_spike_authorization_blockers(auth=auth, readiness=readiness or {})
        blockers.extend(auth_blockers)
    if not blockers:
        env_blockers = _live_spike_environment_blockers(environment=environment or {}, readiness=readiness or {})
        blockers.extend(env_blockers)

    if readiness_blockers or _readiness_packet_blockers(readiness):
        status = "blocked"
        closeout_status = "blocked"
        proof_status = "native_live_spike_readiness_blocked_no_execution"
    elif auth_blockers:
        status = "blocked"
        closeout_status = "missing_authorization"
        proof_status = "native_live_spike_missing_authorization_no_execution"
    elif env_blockers:
        status = "external_blocker"
        closeout_status = "external_blocker"
        proof_status = "native_live_spike_external_blocker_no_execution"
    else:
        status = "ready_to_execute"
        closeout_status = "ready_to_execute"
        proof_status = "native_live_spike_gate_ready_not_executed"

    readiness_payload = dict(readiness or {})
    live_authorized = status == "ready_to_execute"
    ledger_refs = _ledger_refs(transaction_id=str(transaction_id))
    result = {
        "schemaVersion": NATIVE_THIN_LIVE_SPIKE_GATE_SCHEMA,
        "phase": "Phase 13E",
        "packageId": "phase13e.native-thin-live-spike-gate",
        "taskId": "phase13e.native-thin-live-spike-gate",
        "kind": "minimal_live_spike_execution_gate",
        "transactionId": str(transaction_id),
        "adapterId": "native-thin.backend",
        "backend": NATIVE_THIN_BACKEND,
        "backendIdentity": _backend_identity(_dict_value(readiness_payload.get("backendIdentity"))),
        "status": status,
        "closeoutStatus": closeout_status,
        "verificationStatus": "not_verified",
        "proofStatus": proof_status,
        "operatorAuthorizationStatus": "authorized" if live_authorized else closeout_status,
        "realLiveSpikeAuthorizationRequired": not live_authorized,
        "operatorLiveSpikeAuthorized": live_authorized,
        "liveExecutionAuthorized": live_authorized,
        "executionStarted": False,
        "cadWritesAttempted": False,
        "nativePluginInvoked": False,
        "cadGeometryVerified": False,
        "savedCurrentDwg": False,
        "targetLayer": str(readiness_payload.get("targetLayer") or PREVIEW_LAYER),
        "cadPlan": dict(readiness_payload.get("cadPlan") or {}),
        "readbackPlan": dict(readiness_payload.get("readbackPlan") or {}),
        "rollbackPlan": dict(readiness_payload.get("rollbackPlan") or {}),
        "noSaveGuard": dict(readiness_payload.get("noSaveGuard") or {}),
        "readinessPacketHash": readiness_hash,
        "launchPacketHash": str(readiness_payload.get("launchPacketHash") or ""),
        "authorizationReceiptHash": str(readiness_payload.get("authorizationReceiptHash") or ""),
        "executionReceiptHash": str(readiness_payload.get("executionReceiptHash") or ""),
        "operatorAuthorizationRequest": dict(readiness_payload.get("operatorAuthorizationRequest") or {}),
        "operatorAuthorization": auth,
        "environmentReadiness": dict(environment or {}),
        "rollbackRequired": True,
        "rollbackStatus": "not_started",
        "rollbackProof": {
            "status": "not_run_no_transaction",
            "rollbackRequired": True,
            "rollbackStatus": "not_started",
            "verified": False,
            "proofRef": ledger_refs["rollback.applied"],
            "boundary": "P13E gate did not start a native transaction",
        },
        "committedPreview": False,
        "createdHandles": [],
        "createdHandlesRef": f"native-ledger://{transaction_id}/created-handles",
        "createdHandlesReadback": {
            "status": "not_run_no_execution",
            "readbackRequired": True,
            "createdHandles": [],
            "boundary": "created handles readback is required only after an authorized live write",
        },
        "bboxLayerEntityAudit": {
            "status": "not_run_no_execution",
            "bboxChecked": False,
            "layerChecked": False,
            "entityAuditChecked": False,
            "targetLayer": str(readiness_payload.get("targetLayer") or PREVIEW_LAYER),
            "boundary": "bbox / layer / entity audit requires created handles from an authorized live write",
        },
        "blockedReason": ";".join(_unique(blockers)),
        "blockingReasons": _unique(blockers),
        "missingEvidence": _unique(blockers),
        "retryable": False,
        "documentState": "not_connected",
        "documentStateBefore": "not_connected",
        "documentStateAfter": "not_connected",
        "previewStrategy": "memory_transaction",
        "noSaveAudit": {
            "status": "not_run_no_cad",
            "saveAttempted": False,
            "saveAllowed": False,
            "savedCurrentDwg": False,
            "auditRef": ledger_refs["no_save.audit"],
            "boundary": "P13E gate did not connect to AutoCAD and did not save DWG",
        },
        "ledgerRefs": ledger_refs,
        "allowedEffects": [
            "native_thin_live_spike_execution_gate_write",
            "native_thin_external_blocker_closeout_write",
        ],
        "nextAllowedEffects": [],
        "forbiddenEffects": list(P13_NATIVE_FORBIDDEN_EFFECTS),
        "completionBoundary": (
            "P13E gate/blocker closeout is not native plugin availability, real CAD "
            "readback, geometry verification, or DWG save proof"
        ),
        "nextStep": (
            "run_authorized_minimal_native_live_spike"
            if live_authorized
            else "request_separate_operator_authorization_or_fix_external_blocker"
        ),
        "artifacts": {},
        "notEvidenceFor": _native_not_evidence_for(),
    }
    if output_dir is not None:
        result["artifacts"]["nativeThinLiveSpikeExecutionGate"] = _write_json(
            output_dir=output_dir,
            filename="native_thin_live_spike_execution_gate.json",
            payload=result,
        )
    return result


def execute_native_thin_live_spike(
    *,
    readiness_packet: dict[str, Any] | None = None,
    readiness_packet_path: str | Path | None = None,
    operator_authorization: dict[str, Any] | None = None,
    environment: dict[str, Any] | None = None,
    output_dir: str | Path | None = None,
    runner: Callable[..., dict[str, Any]] | None = None,
    transaction_id: str = "tx-p13f-native-live-spike-001",
) -> dict[str, Any]:
    """Execute the P13F minimal live spike behind the P13E gate.

    The default runner uses AutoCAD Core Console and the native thin plugin. A
    caller may inject a runner in tests, but the proof still has to satisfy the
    same readback, rollback, and no-save checks before geometry can be verified.
    """

    root = Path(output_dir) if output_dir is not None else None
    gate = build_native_thin_backend_live_spike_execution_gate(
        readiness_packet=readiness_packet,
        readiness_packet_path=readiness_packet_path,
        operator_authorization=operator_authorization,
        environment=environment,
        output_dir=root,
        transaction_id=f"{transaction_id}.gate",
    )
    if gate.get("status") != "ready_to_execute":
        return _p13f_result_from_gate(gate=gate, output_dir=root, transaction_id=transaction_id)

    live_runner = runner or run_native_thin_autocad_core_console_spike
    try:
        plugin_result = live_runner(
            output_dir=str(root) if root is not None else "",
            cad_plan=dict(gate.get("cadPlan") or {}),
            readiness_packet=dict(readiness_packet or {}),
            readiness_packet_path=str(readiness_packet_path or ""),
            operator_authorization=dict(operator_authorization or {}),
            environment=dict(environment or {}),
            transaction_id=transaction_id,
        )
    except Exception as exc:  # pragma: no cover - defensive guard around external process.
        plugin_result = {
            "schemaVersion": NATIVE_THIN_AUTOCAD_PLUGIN_RESULT_SCHEMA,
            "status": "external_blocker",
            "verificationStatus": "not_verified",
            "backend": "autocad_plugin",
            "targetLayer": PREVIEW_LAYER,
            "transactionId": transaction_id,
            "nativePluginInvoked": False,
            "cadWritesAttempted": False,
            "savedCurrentDwg": False,
            "blockingReasons": [f"native_live_runner_exception:{type(exc).__name__}:{exc}"],
            "missingEvidence": ["real_cad_readback", "native_thin_rollback_proof", "no_save_guard"],
            "artifacts": {},
        }
    return _p13f_result_from_plugin(
        gate=gate,
        plugin_result=plugin_result,
        output_dir=root,
        transaction_id=transaction_id,
    )


def run_native_thin_autocad_core_console_spike(
    *,
    output_dir: str,
    cad_plan: dict[str, Any],
    readiness_packet: dict[str, Any],
    readiness_packet_path: str = "",
    operator_authorization: dict[str, Any] | None = None,
    environment: dict[str, Any] | None = None,
    transaction_id: str = "tx-p13f-native-live-spike-001",
) -> dict[str, Any]:
    """Run the minimal native thin plugin through AutoCAD Core Console."""

    root = Path(output_dir or Path("output") / "validation_runs" / "p13f-native-live-spike")
    root.mkdir(parents=True, exist_ok=True)
    env_payload = dict(environment or {})
    accoreconsole = Path(
        str(
            env_payload.get("accoreConsolePath")
            or os.environ.get("CAD_AGENT_ACCORECONSOLE")
            or r"D:\Design\CAD\AutoCAD 2026\accoreconsole.exe"
        )
    )
    plugin_dll = Path(
        str(
            env_payload.get("pluginDllPath")
            or os.environ.get("CAD_AGENT_NATIVE_THIN_PLUGIN_DLL")
            or _default_native_thin_plugin_dll()
        )
    )
    template_value = str(env_payload.get("templatePath") or os.environ.get("CAD_AGENT_NATIVE_THIN_TEMPLATE") or "")
    template_path = Path(template_value) if template_value else None
    report_path = root / "native_thin_plugin_result.json"
    script_path = root / "native_thin_core_console.scr"
    log_path = root / "native_thin_core_console.log"
    plan_path = root / "native_thin_live_cad_plan.json"
    plan_path.write_text(json.dumps(cad_plan, ensure_ascii=False, indent=2), encoding="utf-8")

    blockers: list[str] = []
    if not accoreconsole.is_file():
        blockers.append("accoreconsole_missing")
    if not plugin_dll.is_file():
        blockers.append("native_thin_plugin_dll_missing")
    if template_path is not None and not template_path.is_file():
        blockers.append("native_thin_template_missing")
    if blockers:
        return _external_blocker_plugin_result(
            transaction_id=transaction_id,
            blocking_reasons=blockers,
            artifacts={
                "accoreConsolePath": str(accoreconsole),
                "pluginDllPath": str(plugin_dll),
                "templatePath": str(template_path or ""),
                "nativePluginReport": str(report_path),
                "coreConsoleLog": str(log_path),
            },
        )

    script_path.write_text(
        "\n".join(
            [
                "_.FILEDIA",
                "0",
                "_.SECURELOAD",
                "0",
                "_.NETLOAD",
                f'"{plugin_dll}"',
                "CADAGENT_P13F_SPIKE",
                "_.QUIT",
                "N",
                "",
            ]
        ),
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["CAD_AGENT_NATIVE_THIN_REPORT"] = str(report_path)
    env["CAD_AGENT_NATIVE_THIN_TRANSACTION_ID"] = str(transaction_id)
    env["CAD_AGENT_NATIVE_THIN_PLAN"] = str(plan_path)
    if readiness_packet_path:
        env["CAD_AGENT_NATIVE_THIN_READINESS_PACKET"] = str(readiness_packet_path)
    if operator_authorization:
        authorization_path = root / "native_thin_operator_authorization_runtime.json"
        authorization_path.write_text(json.dumps(operator_authorization, ensure_ascii=False, indent=2), encoding="utf-8")
        env["CAD_AGENT_NATIVE_THIN_OPERATOR_AUTHORIZATION"] = str(authorization_path)

    try:
        command = [str(accoreconsole)]
        if template_path is not None:
            command.extend(["/i", str(template_path)])
        command.extend(["/s", str(script_path)])
        completed = subprocess.run(
            command,
            cwd=str(root),
            env=env,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=float(os.environ.get("CAD_AGENT_NATIVE_THIN_TIMEOUT_SECONDS", "180")),
        )
    except subprocess.TimeoutExpired as exc:
        log_path.write_text(str(exc), encoding="utf-8")
        return _external_blocker_plugin_result(
            transaction_id=transaction_id,
            blocking_reasons=["accoreconsole_timeout"],
            artifacts={
                "accoreConsolePath": str(accoreconsole),
                "pluginDllPath": str(plugin_dll),
                "templatePath": str(template_path or ""),
                "nativePluginReport": str(report_path),
                "coreConsoleLog": str(log_path),
            },
        )

    log_path.write_text(
        "\n".join(
            [
                f"exitCode={completed.returncode}",
                "=== stdout ===",
                completed.stdout or "",
                "=== stderr ===",
                completed.stderr or "",
            ]
        ),
        encoding="utf-8",
    )
    if not report_path.is_file():
        return _external_blocker_plugin_result(
            transaction_id=transaction_id,
            blocking_reasons=["native_thin_plugin_report_missing"],
            artifacts={
                "accoreConsolePath": str(accoreconsole),
                "pluginDllPath": str(plugin_dll),
                "templatePath": str(template_path or ""),
                "nativePluginReport": str(report_path),
                "coreConsoleLog": str(log_path),
                "coreConsoleExitCode": completed.returncode,
            },
        )

    report = dict(json.loads(report_path.read_text(encoding="utf-8")))
    artifacts = dict(report.get("artifacts") or {})
    artifacts.update(
        {
            "accoreConsolePath": str(accoreconsole),
            "pluginDllPath": str(plugin_dll),
            "templatePath": str(template_path or ""),
            "nativePluginReport": str(report_path),
            "coreConsoleLog": str(log_path),
            "coreConsoleExitCode": completed.returncode,
        }
    )
    report["artifacts"] = artifacts
    return report


def native_thin_live_spike_evidence_package(result: dict[str, Any]) -> EvidencePackage:
    payload = dict(result)
    verified = payload.get("cadGeometryVerified") is True and payload.get("verificationStatus") == "verified"
    no_save = dict(payload.get("noSaveAudit") or {})
    rollback = dict(payload.get("rollbackProof") or {})
    readback = dict(payload.get("createdHandlesReadback") or {})
    return EvidencePackage(
        task_id=str(payload.get("taskId") or "phase13f.native-thin-live-spike"),
        items=[
            EvidenceItem(
                kind="native_thin_live_spike_result",
                status="pass" if payload.get("schemaVersion") == NATIVE_THIN_LIVE_SPIKE_SCHEMA else "fail",
                backend=NATIVE_THIN_LIVE_BACKEND,
                cad_geometry_verified=verified,
                metadata={
                    "transactionId": str(payload.get("transactionId") or ""),
                    "proofStatus": str(payload.get("proofStatus") or ""),
                    "adapterId": str(payload.get("adapterId") or ""),
                },
            ),
            EvidenceItem(
                kind="cad_readback",
                status="pass" if verified else "fail",
                backend="autocad_plugin",
                readback_status=str(readback.get("readbackStatus") or readback.get("status") or ""),
                cad_geometry_verified=verified,
                metadata={
                    "backend": "autocad_plugin",
                    "createdHandles": list(payload.get("createdHandles") or []),
                    "savedCurrentDwg": payload.get("savedCurrentDwg"),
                },
            ),
            EvidenceItem(
                kind="native_thin_rollback_proof",
                status="pass" if rollback.get("verified") is True else "fail",
                backend=NATIVE_THIN_LIVE_BACKEND,
                cad_geometry_verified=False,
                metadata=dict(rollback),
            ),
            EvidenceItem(
                kind="native_thin_no_save_audit",
                status="pass" if no_save.get("savedCurrentDwg") is False else "fail",
                backend=NATIVE_THIN_LIVE_BACKEND,
                cad_geometry_verified=False,
                metadata=dict(no_save),
            ),
            EvidenceItem(
                kind="no_save_guard",
                status="pass" if payload.get("savedCurrentDwg") is False else "fail",
                backend=NATIVE_THIN_LIVE_BACKEND,
                cad_geometry_verified=False,
                metadata={"savedCurrentDwg": payload.get("savedCurrentDwg")},
            ),
        ],
    )


def _p13f_result_from_gate(
    *,
    gate: dict[str, Any],
    output_dir: Path | None,
    transaction_id: str,
) -> dict[str, Any]:
    ledger_refs = _ledger_refs(transaction_id=transaction_id)
    backend_identity = _p13f_live_backend_identity(gate=gate)
    result = {
        "schemaVersion": NATIVE_THIN_LIVE_SPIKE_SCHEMA,
        "phase": "Phase 13F",
        "packageId": "phase13f.native-thin-live-spike",
        "taskId": "phase13f.native-thin-live-spike",
        "kind": "minimal_native_thin_live_spike",
        "transactionId": str(transaction_id),
        "adapterId": "native-thin.live-spike",
        "backend": NATIVE_THIN_LIVE_BACKEND,
        "backendIdentity": backend_identity,
        "status": str(gate.get("status") or "blocked"),
        "closeoutStatus": str(gate.get("closeoutStatus") or "blocked"),
        "verificationStatus": "not_verified",
        "proofStatus": str(gate.get("proofStatus") or "native_live_spike_blocked_before_execution"),
        "operatorAuthorizationStatus": str(gate.get("operatorAuthorizationStatus") or ""),
        "realLiveSpikeAuthorizationRequired": bool(gate.get("realLiveSpikeAuthorizationRequired", True)),
        "operatorLiveSpikeAuthorized": bool(gate.get("operatorLiveSpikeAuthorized", False)),
        "liveExecutionAuthorized": bool(gate.get("liveExecutionAuthorized", False)),
        "executionStarted": False,
        "cadWritesAttempted": False,
        "nativePluginInvoked": False,
        "cadGeometryVerified": False,
        "savedCurrentDwg": False,
        "targetLayer": str(gate.get("targetLayer") or PREVIEW_LAYER),
        "cadPlan": dict(gate.get("cadPlan") or {}),
        "readbackPlan": dict(gate.get("readbackPlan") or {}),
        "rollbackPlan": dict(gate.get("rollbackPlan") or {}),
        "noSaveGuard": dict(gate.get("noSaveGuard") or {}),
        "readinessPacketHash": str(gate.get("readinessPacketHash") or ""),
        "launchPacketHash": str(gate.get("launchPacketHash") or ""),
        "authorizationReceiptHash": str(gate.get("authorizationReceiptHash") or ""),
        "executionReceiptHash": str(gate.get("executionReceiptHash") or ""),
        "operatorAuthorizationRequest": dict(gate.get("operatorAuthorizationRequest") or {}),
        "operatorAuthorization": dict(gate.get("operatorAuthorization") or {}),
        "environmentReadiness": dict(gate.get("environmentReadiness") or {}),
        "rollbackRequired": True,
        "rollbackStatus": "not_started",
        "rollbackProof": dict(gate.get("rollbackProof") or {}),
        "committedPreview": False,
        "createdHandles": [],
        "createdHandlesRef": f"native-ledger://{transaction_id}/created-handles",
        "createdHandlesReadback": dict(gate.get("createdHandlesReadback") or {}),
        "bboxLayerEntityAudit": dict(gate.get("bboxLayerEntityAudit") or {}),
        "blockedReason": str(gate.get("blockedReason") or ""),
        "blockingReasons": [str(item) for item in gate.get("blockingReasons", [])],
        "missingEvidence": [str(item) for item in gate.get("missingEvidence", [])],
        "retryable": False,
        "documentState": "not_connected",
        "documentStateBefore": "not_connected",
        "documentStateAfter": "not_connected",
        "previewStrategy": "native_thin_scoped_preview_rollback",
        "noSaveAudit": dict(gate.get("noSaveAudit") or {}),
        "ledgerRefs": ledger_refs,
        "allowedEffects": list(P13_NATIVE_LIVE_ALLOWED_EFFECTS),
        "forbiddenEffects": list(P13_NATIVE_LIVE_FORBIDDEN_EFFECTS),
        "completionBoundary": (
            "P13F live spike did not execute because P13E authorization/environment gate was not ready"
        ),
        "artifacts": dict(gate.get("artifacts") or {}),
        "notEvidenceFor": _native_not_evidence_for(),
    }
    return _write_p13f_result(result=result, output_dir=output_dir)


def _p13f_result_from_plugin(
    *,
    gate: dict[str, Any],
    plugin_result: dict[str, Any],
    output_dir: Path | None,
    transaction_id: str,
) -> dict[str, Any]:
    plugin = dict(plugin_result or {})
    ledger_refs = _ledger_refs(transaction_id=transaction_id)
    handles = [str(item) for item in plugin.get("createdHandles", [])]
    readback = dict(plugin.get("createdHandlesReadback") or {})
    audit = dict(plugin.get("bboxLayerEntityAudit") or {})
    rollback = dict(plugin.get("rollbackProof") or {})
    no_save = dict(plugin.get("noSaveAudit") or {})
    entities = [dict(item) for item in readback.get("entities", []) if isinstance(item, dict)]
    blocking_reasons = [str(item) for item in plugin.get("blockingReasons", [])]
    missing_evidence = [str(item) for item in plugin.get("missingEvidence", [])]
    external_blocker = str(plugin.get("status") or "") == "external_blocker"

    proof_blockers = list(blocking_reasons)
    if plugin.get("nativePluginInvoked") is not True:
        proof_blockers.append("native_plugin_invocation_not_proven")
    if plugin.get("cadWritesAttempted") is not True:
        proof_blockers.append("cad_write_attempt_not_proven")
    if plugin.get("savedCurrentDwg") is not False or no_save.get("savedCurrentDwg") is not False:
        proof_blockers.append("no_save_audit_not_verified")
    if no_save.get("saveAttempted") is not False:
        proof_blockers.append("no_save_guard_reported_save_attempt")
    if str(plugin.get("targetLayer") or "") != PREVIEW_LAYER:
        proof_blockers.append("target_layer_must_be_CODEX_PREVIEW")
    if not handles:
        proof_blockers.append("created_handles_required")
    if str(readback.get("status") or "").casefold() not in {"verified", "pass", "ok"}:
        proof_blockers.append("created_handles_readback_not_verified")
    if not entities:
        proof_blockers.append("readback_entities_required")
    for entity in entities:
        if str(entity.get("layer") or "") != PREVIEW_LAYER:
            proof_blockers.append("readback_entity_layer_must_be_CODEX_PREVIEW")
    if str(audit.get("status") or "").casefold() not in {"verified", "pass", "ok"}:
        proof_blockers.append("bbox_layer_entity_audit_not_verified")
    if audit.get("bboxChecked") is not True:
        proof_blockers.append("bbox_audit_required")
    if audit.get("layerChecked") is not True:
        proof_blockers.append("layer_audit_required")
    if audit.get("entityAuditChecked") is not True:
        proof_blockers.append("entity_audit_required")
    if rollback.get("verified") is not True:
        proof_blockers.append("rollback_proof_not_verified")
    if str(plugin.get("rollbackStatus") or rollback.get("rollbackStatus") or "").casefold() not in {
        "rolled_back",
        "rollback_verified",
        "verified",
    }:
        proof_blockers.append("rollback_status_not_verified")

    proof_blockers = _unique(proof_blockers)
    verified = not external_blocker and not proof_blockers
    status = "geometry_verified" if verified else "external_blocker" if external_blocker else "not_verified"
    verification_status = "verified" if verified else "not_verified"
    proof_status = (
        "native_live_spike_geometry_verified_with_rollback_no_save"
        if verified
        else "native_live_spike_external_blocker"
        if external_blocker
        else "native_live_spike_not_verified"
    )
    not_evidence_for = (
        [
            "training_resume",
            "table_c_progress",
            "current_dwg_save",
            "formal_layer_write",
        ]
        if verified
        else _native_not_evidence_for()
    )
    artifacts = dict(gate.get("artifacts") or {})
    artifacts.update(dict(plugin.get("artifacts") or {}))
    backend_identity = _p13f_live_backend_identity(gate=gate, plugin=plugin)
    result = {
        "schemaVersion": NATIVE_THIN_LIVE_SPIKE_SCHEMA,
        "phase": "Phase 13F",
        "packageId": "phase13f.native-thin-live-spike",
        "taskId": "phase13f.native-thin-live-spike",
        "kind": "minimal_native_thin_live_spike",
        "transactionId": str(transaction_id),
        "adapterId": "native-thin.live-spike",
        "backend": NATIVE_THIN_LIVE_BACKEND,
        "backendIdentity": backend_identity,
        "status": status,
        "closeoutStatus": status,
        "verificationStatus": verification_status,
        "proofStatus": proof_status,
        "operatorAuthorizationStatus": str(gate.get("operatorAuthorizationStatus") or ""),
        "realLiveSpikeAuthorizationRequired": False,
        "operatorLiveSpikeAuthorized": True,
        "liveExecutionAuthorized": True,
        "executionStarted": True,
        "cadWritesAttempted": plugin.get("cadWritesAttempted") is True,
        "nativePluginInvoked": plugin.get("nativePluginInvoked") is True,
        "cadGeometryVerified": verified,
        "savedCurrentDwg": plugin.get("savedCurrentDwg") is True,
        "targetLayer": str(plugin.get("targetLayer") or gate.get("targetLayer") or PREVIEW_LAYER),
        "cadPlan": dict(gate.get("cadPlan") or {}),
        "readbackPlan": dict(gate.get("readbackPlan") or {}),
        "rollbackPlan": dict(gate.get("rollbackPlan") or {}),
        "noSaveGuard": dict(gate.get("noSaveGuard") or {}),
        "readinessPacketHash": str(gate.get("readinessPacketHash") or ""),
        "launchPacketHash": str(gate.get("launchPacketHash") or ""),
        "authorizationReceiptHash": str(gate.get("authorizationReceiptHash") or ""),
        "executionReceiptHash": str(gate.get("executionReceiptHash") or ""),
        "operatorAuthorizationRequest": dict(gate.get("operatorAuthorizationRequest") or {}),
        "operatorAuthorization": dict(gate.get("operatorAuthorization") or {}),
        "environmentReadiness": dict(gate.get("environmentReadiness") or {}),
        "rollbackRequired": True,
        "rollbackStatus": str(plugin.get("rollbackStatus") or rollback.get("rollbackStatus") or ""),
        "rollbackProof": rollback,
        "committedPreview": plugin.get("committedPreview") is True,
        "createdHandles": handles,
        "createdHandlesRef": f"native-ledger://{transaction_id}/created-handles",
        "createdHandlesReadback": readback,
        "bboxLayerEntityAudit": audit,
        "blockedReason": ";".join(proof_blockers),
        "blockingReasons": proof_blockers,
        "missingEvidence": _unique([*missing_evidence, *proof_blockers]),
        "retryable": external_blocker,
        "documentState": str(plugin.get("documentState") or ""),
        "documentStateBefore": str(plugin.get("documentStateBefore") or ""),
        "documentStateAfter": str(plugin.get("documentStateAfter") or ""),
        "previewStrategy": "native_thin_scoped_preview_rollback",
        "noSaveAudit": no_save,
        "ledgerRefs": ledger_refs,
        "allowedEffects": list(P13_NATIVE_LIVE_ALLOWED_EFFECTS),
        "forbiddenEffects": list(P13_NATIVE_LIVE_FORBIDDEN_EFFECTS),
        "completionBoundary": (
            "P13F minimal native thin live spike is claimable only when AutoCAD/plugin "
            "created handles readback, bbox/layer/entity audit, rollback proof, and no-save audit all pass"
        ),
        "artifacts": artifacts,
        "pluginResult": plugin,
        "notEvidenceFor": not_evidence_for,
    }
    return _write_p13f_result(result=result, output_dir=output_dir)


def _p13f_live_backend_identity(*, gate: dict[str, Any], plugin: dict[str, Any] | None = None) -> dict[str, Any]:
    plugin_payload = dict(plugin or {})
    artifacts = dict(plugin_payload.get("artifacts") or {})
    return {
        "backend": NATIVE_THIN_LIVE_BACKEND,
        "adapterId": "native-thin.live-spike",
        "pluginBackend": str(plugin_payload.get("backend") or "not_invoked"),
        "nativePluginInvoked": plugin_payload.get("nativePluginInvoked") is True,
        "coreConsolePath": str(artifacts.get("accoreConsolePath") or ""),
        "pluginDllPath": str(artifacts.get("pluginDllPath") or ""),
        "sourceReadinessBackend": dict(gate.get("backendIdentity") or {}),
    }


def _external_blocker_plugin_result(
    *,
    transaction_id: str,
    blocking_reasons: list[str],
    artifacts: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schemaVersion": NATIVE_THIN_AUTOCAD_PLUGIN_RESULT_SCHEMA,
        "status": "external_blocker",
        "verificationStatus": "not_verified",
        "backend": "autocad_plugin",
        "targetLayer": PREVIEW_LAYER,
        "transactionId": str(transaction_id),
        "nativePluginInvoked": False,
        "cadWritesAttempted": False,
        "savedCurrentDwg": False,
        "committedPreview": False,
        "createdHandles": [],
        "createdHandlesReadback": {"status": "not_run", "entities": []},
        "bboxLayerEntityAudit": {"status": "not_run"},
        "rollbackRequired": True,
        "rollbackStatus": "not_started",
        "rollbackProof": {"status": "not_run", "verified": False, "rollbackStatus": "not_started"},
        "noSaveAudit": {"status": "not_run", "saveAttempted": False, "saveAllowed": False, "savedCurrentDwg": False},
        "blockingReasons": list(blocking_reasons),
        "missingEvidence": ["real_cad_readback", "native_thin_rollback_proof", "no_save_guard"],
        "artifacts": dict(artifacts),
    }


def _write_p13f_result(*, result: dict[str, Any], output_dir: Path | None) -> dict[str, Any]:
    if output_dir is not None:
        artifacts = dict(result.get("artifacts") or {})
        artifacts["nativeThinLiveSpikeResult"] = _write_json(
            output_dir=output_dir,
            filename="native_thin_live_spike_result.json",
            payload={**result, "artifacts": artifacts},
        )
        result["artifacts"] = artifacts
    return result


def _default_native_thin_plugin_dll() -> Path:
    root = Path(__file__).resolve().parents[2]
    return root / "native_plugins" / "native_thin_backend" / "bin" / "Release" / "net8.0-windows" / "NativeThinBackend.dll"


def _launch_packet_blockers(packet: dict[str, Any] | None) -> list[str]:
    if not packet:
        return []
    blockers: list[str] = []
    if packet.get("schemaVersion") != NATIVE_THIN_PREFLIGHT_SCHEMA:
        blockers.append("native_launch_packet_schema_invalid")
    if packet.get("kind") != "launch_packet":
        blockers.append("native_launch_packet_kind_invalid")
    if packet.get("status") != "ready" or packet.get("launchPacketReady") is not True:
        blockers.append("native_launch_packet_not_ready")
    if packet.get("targetLayer") != PREVIEW_LAYER:
        blockers.append("target_layer_must_be_CODEX_PREVIEW")
    backend = _backend_identity(dict(packet.get("backendIdentity") or {}))
    if backend["backend"] != "native-thin-skeleton":
        blockers.append("backend_identity_must_be_native_thin_skeleton")
    if not isinstance(packet.get("cadPlan"), dict) or not packet.get("cadPlan"):
        blockers.append("cad_plan_required")
    readback = dict(packet.get("readbackPlan") or {})
    rollback = dict(packet.get("rollbackPlan") or {})
    no_save = dict(packet.get("noSaveGuard") or {})
    if readback.get("required") is not True:
        blockers.append("readback_plan_required")
    if rollback.get("required") is not True:
        blockers.append("rollback_plan_required")
    if no_save.get("required") is not True:
        blockers.append("no_save_guard_required")
    if no_save.get("saveAllowed") is not False:
        blockers.append("no_save_guard_must_block_save")
    if packet.get("liveExecutionAuthorized") is True:
        blockers.append("native_launch_packet_must_not_pre_authorize_live_execution")
    if packet.get("cadWritesAttempted") is True:
        blockers.append("native_launch_packet_must_not_attempt_cad_write")
    if packet.get("nativePluginInvoked") is True:
        blockers.append("native_launch_packet_must_not_invoke_plugin")
    if packet.get("cadGeometryVerified") is True:
        blockers.append("native_launch_packet_must_not_claim_geometry_verified")
    return _unique(blockers)


def _execution_receipt_blockers(receipt: dict[str, Any] | None) -> list[str]:
    if not receipt:
        return []
    blockers: list[str] = []
    if receipt.get("schemaVersion") != NATIVE_THIN_EXECUTION_RECEIPT_SCHEMA:
        blockers.append("native_execution_receipt_schema_invalid")
    if receipt.get("kind") != "execution_receipt":
        blockers.append("native_execution_receipt_kind_invalid")
    if receipt.get("status") != "ready" or receipt.get("receiptStatus") != "scoped_execution_receipt_ready":
        blockers.append("native_execution_receipt_not_ready")
    if receipt.get("authorizationStatus") != "authorized":
        blockers.append("native_authorization_receipt_not_authorized")
    if receipt.get("liveExecutionAuthorized") is not True:
        blockers.append("native_authorization_receipt_not_authorized")
    if receipt.get("scopeMatch") is not True:
        blockers.append("native_scope_hash_mismatch")
    if not str(receipt.get("launchPacketHash") or ""):
        blockers.append("native_launch_packet_hash_required")
    if not str(receipt.get("scopeHash") or ""):
        blockers.append("native_scope_hash_required")
    if (
        str(receipt.get("launchPacketHash") or "")
        and str(receipt.get("scopeHash") or "")
        and str(receipt.get("launchPacketHash") or "") != str(receipt.get("scopeHash") or "")
    ):
        blockers.append("native_scope_hash_mismatch")
    if receipt.get("targetLayer") != PREVIEW_LAYER:
        blockers.append("target_layer_must_be_CODEX_PREVIEW")
    cad_plan = receipt.get("cadPlan") if isinstance(receipt.get("cadPlan"), dict) else None
    if not cad_plan:
        blockers.append("cad_plan_required")
    elif _cad_plan_layer(cad_plan) != PREVIEW_LAYER:
        blockers.append("target_layer_must_be_CODEX_PREVIEW")
    backend = _backend_identity(_dict_value(receipt.get("backendIdentity")))
    if backend["backend"] != "native-thin-skeleton":
        blockers.append("backend_identity_must_be_native_thin_skeleton")
    readback = dict(receipt.get("readbackPlan") or {})
    rollback = dict(receipt.get("rollbackPlan") or {})
    no_save = dict(receipt.get("noSaveGuard") or {})
    if readback.get("required") is not True:
        blockers.append("readback_plan_required")
    if rollback.get("required") is not True:
        blockers.append("rollback_plan_required")
    if no_save.get("required") is not True:
        blockers.append("no_save_guard_required")
    if no_save.get("saveAllowed") is not False:
        blockers.append("no_save_guard_must_block_save")
    if receipt.get("executionStarted") is True:
        blockers.append("native_execution_receipt_must_not_start_execution")
    if receipt.get("cadWritesAttempted") is True:
        blockers.append("native_execution_receipt_must_not_attempt_cad_write")
    if receipt.get("nativePluginInvoked") is True:
        blockers.append("native_execution_receipt_must_not_invoke_plugin")
    if receipt.get("cadGeometryVerified") is True:
        blockers.append("native_execution_receipt_must_not_claim_geometry_verified")
    if receipt.get("savedCurrentDwg") is True:
        blockers.append("native_execution_receipt_must_not_save_dwg")
    return _unique(blockers)


def _user_authorization_blockers(*, auth: dict[str, Any], packet_hash: str) -> list[str]:
    blockers: list[str] = []
    required_flags = {
        "scopeConfirmed": "native_authorization_scope_required",
        "cadPlanConfirmed": "native_authorization_cad_plan_required",
        "codexPreviewConfirmed": "native_authorization_codex_preview_required",
        "readbackConfirmed": "native_authorization_readback_required",
        "rollbackConfirmed": "native_authorization_rollback_required",
        "noSaveConfirmed": "native_authorization_no_save_required",
        "backendIdentityConfirmed": "native_authorization_backend_identity_required",
    }
    for key, blocker in required_flags.items():
        if auth.get(key) is not True:
            blockers.append(blocker)
    expected_hash = str(auth.get("launchPacketHash") or auth.get("scopeHash") or "")
    if not expected_hash:
        blockers.append("native_authorization_hash_required")
    elif packet_hash and expected_hash != packet_hash:
        blockers.append("native_scope_hash_mismatch")
    if not str(auth.get("statement") or "").strip():
        blockers.append("native_authorization_statement_required")
    return _unique(blockers)


def _p13c_authorization_base(
    *,
    kind: str,
    status: str,
    transaction_id: str,
    launch_packet: dict[str, Any] | None,
    launch_packet_hash: str,
    authorization_status: str,
    blocking_reasons: list[str],
    user_authorization: dict[str, Any],
) -> dict[str, Any]:
    packet = dict(launch_packet or {})
    backend_identity = _backend_identity(dict(packet.get("backendIdentity") or {}))
    live_authorized = status == "ready" and authorization_status == "authorized"
    proof_status = (
        "native_live_authorization_ready_no_execution"
        if live_authorized
        else "native_live_authorization_pending_no_execution"
        if authorization_status == "authorization_pending"
        else "native_live_authorization_blocked"
    )
    scope_match = (
        bool(launch_packet_hash)
        and str(user_authorization.get("launchPacketHash") or user_authorization.get("scopeHash") or launch_packet_hash)
        == launch_packet_hash
    )
    return {
        "schemaVersion": NATIVE_THIN_AUTHORIZATION_SCHEMA,
        "phase": "Phase 13C",
        "packageId": "phase13c.native-thin-authorization",
        "taskId": "phase13c.native-thin-authorization",
        "kind": kind,
        "transactionId": str(transaction_id),
        "adapterId": "native-thin.backend",
        "backend": NATIVE_THIN_BACKEND,
        "backendIdentity": backend_identity,
        "status": status,
        "authorizationStatus": authorization_status,
        "verificationStatus": "not_verified",
        "proofStatus": proof_status,
        "launchPacketReady": packet.get("status") == "ready" and packet.get("launchPacketReady") is True,
        "launchPacketHash": launch_packet_hash,
        "scopeHash": launch_packet_hash,
        "scopeMatch": scope_match,
        "scopeConfirmed": packet.get("scopeReceiptReady") is True,
        "targetLayer": str(packet.get("targetLayer") or PREVIEW_LAYER),
        "cadPlan": dict(packet.get("cadPlan") or {}),
        "readbackPlan": dict(packet.get("readbackPlan") or {}),
        "rollbackPlan": dict(packet.get("rollbackPlan") or {}),
        "noSaveGuard": dict(packet.get("noSaveGuard") or {}),
        "userAuthorization": dict(user_authorization),
        "liveExecutionAuthorized": live_authorized,
        "executionStarted": False,
        "rollbackRequired": True,
        "rollbackStatus": "not_started",
        "committedPreview": False,
        "createdHandles": [],
        "createdHandlesRef": f"native-ledger://{transaction_id}/created-handles",
        "blockedReason": ";".join(_unique(blocking_reasons)),
        "blockingReasons": _unique(blocking_reasons),
        "missingEvidence": [],
        "retryable": False,
        "documentState": "not_connected",
        "cadGeometryVerified": False,
        "cadWritesAttempted": False,
        "nativePluginInvoked": False,
        "savedCurrentDwg": False,
        "previewStrategy": "memory_transaction",
        "ledgerRefs": _ledger_refs(transaction_id=str(transaction_id)),
        "allowedEffects": [],
        "nextAllowedEffects": [],
        "forbiddenEffects": list(P13_NATIVE_FORBIDDEN_EFFECTS),
        "completionBoundary": (
            "P13C authorization gate only; it records explicit scope authorization "
            "and stops before AutoCAD or native plugin execution"
        ),
        "nextStep": (
            "build_native_thin_execution_receipt"
            if live_authorized
            else "request_user_authorization_for_native_live_spike"
        ),
        "artifacts": {},
        "notEvidenceFor": _native_not_evidence_for(),
    }


def _p13c_execution_receipt_base(
    *,
    status: str,
    transaction_id: str,
    authorization_gate: dict[str, Any] | None,
    blocking_reasons: list[str],
) -> dict[str, Any]:
    gate = dict(authorization_gate or {})
    live_authorized = status == "ready"
    proof_status = (
        "native_live_scoped_receipt_ready_no_execution"
        if live_authorized
        else "native_live_scoped_receipt_blocked_no_execution"
    )
    return {
        "schemaVersion": NATIVE_THIN_EXECUTION_RECEIPT_SCHEMA,
        "phase": "Phase 13C",
        "packageId": "phase13c.native-thin-execution-receipt",
        "taskId": "phase13c.native-thin-execution-receipt",
        "kind": "execution_receipt",
        "transactionId": str(transaction_id),
        "adapterId": "native-thin.backend",
        "backend": NATIVE_THIN_BACKEND,
        "backendIdentity": _backend_identity(dict(gate.get("backendIdentity") or {})),
        "status": status,
        "receiptStatus": "scoped_execution_receipt_ready" if live_authorized else "blocked",
        "authorizationStatus": str(gate.get("authorizationStatus") or "blocked"),
        "verificationStatus": "not_verified",
        "proofStatus": proof_status,
        "launchPacketHash": str(gate.get("launchPacketHash") or ""),
        "scopeHash": str(gate.get("scopeHash") or ""),
        "scopeMatch": gate.get("scopeMatch") is True,
        "targetLayer": str(gate.get("targetLayer") or PREVIEW_LAYER),
        "cadPlan": dict(gate.get("cadPlan") or {}),
        "readbackPlan": dict(gate.get("readbackPlan") or {}),
        "rollbackPlan": dict(gate.get("rollbackPlan") or {}),
        "noSaveGuard": dict(gate.get("noSaveGuard") or {}),
        "userAuthorization": dict(gate.get("userAuthorization") or {}),
        "liveExecutionAuthorized": live_authorized,
        "executionStarted": False,
        "rollbackRequired": True,
        "rollbackStatus": "not_started",
        "rollbackProof": {
            "status": "not_run_no_transaction",
            "rollbackRequired": True,
            "rollbackStatus": "not_started",
            "verified": False,
            "proofRef": f"native-ledger://{transaction_id}/rollback.applied",
            "boundary": "P13C receipt does not start a native transaction",
        },
        "committedPreview": False,
        "createdHandles": [],
        "createdHandlesRef": f"native-ledger://{transaction_id}/created-handles",
        "blockedReason": ";".join(_unique(blocking_reasons)),
        "blockingReasons": _unique(blocking_reasons),
        "missingEvidence": [],
        "retryable": False,
        "documentState": "not_connected",
        "documentStateBefore": "not_connected",
        "documentStateAfter": "not_connected",
        "cadGeometryVerified": False,
        "cadWritesAttempted": False,
        "nativePluginInvoked": False,
        "savedCurrentDwg": False,
        "noSaveAudit": {
            "status": "not_run_no_cad",
            "saveAttempted": False,
            "saveAllowed": False,
            "savedCurrentDwg": False,
            "auditRef": f"native-ledger://{transaction_id}/no-save.audit",
            "boundary": "P13C receipt records the no-save guard but does not connect to AutoCAD",
        },
        "previewStrategy": "memory_transaction",
        "ledgerRefs": _ledger_refs(transaction_id=str(transaction_id)),
        "allowedEffects": [],
        "nextAllowedEffects": [],
        "forbiddenEffects": list(P13_NATIVE_FORBIDDEN_EFFECTS),
        "completionBoundary": (
            "P13C execution receipt records authorization scope only; live spike execution "
            "requires a separate explicit operator launch and remains no-save / rollback guarded"
        ),
        "artifacts": {},
        "notEvidenceFor": _native_not_evidence_for(),
    }


def _p13d_readiness_base(
    *,
    status: str,
    transaction_id: str,
    execution_receipt: dict[str, Any] | None,
    receipt_hash: str,
    expected_receipt_hash: str,
    blocking_reasons: list[str],
) -> dict[str, Any]:
    receipt = dict(execution_receipt or {})
    ready_for_authorization = status == "ready_for_user_authorization"
    proof_status = (
        "native_live_readiness_ready_for_user_authorization_no_execution"
        if ready_for_authorization
        else "native_live_readiness_blocked_no_execution"
    )
    return {
        "schemaVersion": NATIVE_THIN_READINESS_SCHEMA,
        "phase": "Phase 13D",
        "packageId": "phase13d.native-thin-readiness",
        "taskId": "phase13d.native-thin-readiness",
        "kind": "operator_authorization_request",
        "transactionId": str(transaction_id),
        "adapterId": "native-thin.backend",
        "backend": NATIVE_THIN_BACKEND,
        "backendIdentity": _backend_identity(_dict_value(receipt.get("backendIdentity"))),
        "status": status,
        "authorizationRequestStatus": status,
        "verificationStatus": "not_verified",
        "proofStatus": proof_status,
        "receiptStatus": str(receipt.get("receiptStatus") or "blocked"),
        "p13cAuthorizationStatus": str(receipt.get("authorizationStatus") or "blocked"),
        "p13cLiveExecutionAuthorized": receipt.get("liveExecutionAuthorized") is True,
        "realLiveSpikeAuthorizationRequired": ready_for_authorization,
        "operatorLiveSpikeAuthorized": False,
        "liveExecutionAuthorized": False,
        "launchPacketHash": str(receipt.get("launchPacketHash") or ""),
        "scopeHash": str(receipt.get("scopeHash") or ""),
        "authorizationReceiptHash": receipt_hash,
        "executionReceiptHash": receipt_hash,
        "expectedAuthorizationReceiptHash": expected_receipt_hash,
        "scopeMatch": receipt.get("scopeMatch") is True,
        "targetLayer": str(receipt.get("targetLayer") or PREVIEW_LAYER),
        "cadPlan": dict(receipt.get("cadPlan") or {}),
        "readbackPlan": dict(receipt.get("readbackPlan") or {}),
        "rollbackPlan": dict(receipt.get("rollbackPlan") or {}),
        "noSaveGuard": dict(receipt.get("noSaveGuard") or {}),
        "executionStarted": False,
        "rollbackRequired": True,
        "rollbackStatus": "not_started",
        "rollbackProof": {
            "status": "not_run_no_transaction",
            "rollbackRequired": True,
            "rollbackStatus": "not_started",
            "verified": False,
            "proofRef": f"native-ledger://{transaction_id}/rollback.applied",
            "boundary": "P13D readiness does not start a native transaction",
        },
        "committedPreview": False,
        "createdHandles": [],
        "createdHandlesRef": f"native-ledger://{transaction_id}/created-handles",
        "blockedReason": ";".join(_unique(blocking_reasons)),
        "blockingReasons": _unique(blocking_reasons),
        "missingEvidence": [],
        "retryable": False,
        "documentState": "not_connected",
        "documentStateBefore": "not_connected",
        "documentStateAfter": "not_connected",
        "cadGeometryVerified": False,
        "cadWritesAttempted": False,
        "nativePluginInvoked": False,
        "savedCurrentDwg": False,
        "noSaveAudit": {
            "status": "not_run_no_cad",
            "saveAttempted": False,
            "saveAllowed": False,
            "savedCurrentDwg": False,
            "auditRef": f"native-ledger://{transaction_id}/no-save.audit",
            "boundary": "P13D readiness records no-save guard but does not connect to AutoCAD",
        },
        "previewStrategy": "memory_transaction",
        "ledgerRefs": _ledger_refs(transaction_id=str(transaction_id)),
        "allowedEffects": [],
        "nextAllowedEffects": [],
        "forbiddenEffects": list(P13_NATIVE_FORBIDDEN_EFFECTS),
        "completionBoundary": (
            "P13D readiness only; real native live spike must stop for a separate "
            "operator authorization and remains outside this contract"
        ),
        "nextStep": (
            "wait_for_separate_operator_authorization_for_real_native_live_spike"
            if ready_for_authorization
            else "fix_native_live_readiness_blockers"
        ),
        "operatorAuthorizationRequest": {},
        "artifacts": {},
        "notEvidenceFor": _native_not_evidence_for(),
    }


def _operator_authorization_request(readiness: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": NATIVE_THIN_READINESS_SCHEMA,
        "kind": "operator_authorization_request",
        "status": readiness["authorizationRequestStatus"],
        "requiresSeparateUserAuthorization": readiness["status"] == "ready_for_user_authorization",
        "requestedConfirmations": [
            "scope",
            "CAD_PLAN",
            "CODEX_PREVIEW",
            "readback_plan",
            "rollback_plan",
            "no_save_guard",
            "backend_identity",
            "launch_packet_hash",
            "authorization_receipt_hash",
        ],
        "adapterId": readiness["adapterId"],
        "backendIdentity": dict(readiness.get("backendIdentity") or {}),
        "targetLayer": str(readiness.get("targetLayer") or PREVIEW_LAYER),
        "cadPlan": dict(readiness.get("cadPlan") or {}),
        "readbackPlan": dict(readiness.get("readbackPlan") or {}),
        "rollbackPlan": dict(readiness.get("rollbackPlan") or {}),
        "noSaveGuard": dict(readiness.get("noSaveGuard") or {}),
        "launchPacketHash": str(readiness.get("launchPacketHash") or ""),
        "authorizationReceiptHash": str(readiness.get("authorizationReceiptHash") or ""),
        "executionReceiptHash": str(readiness.get("executionReceiptHash") or ""),
        "cadWritesAttempted": False,
        "nativePluginInvoked": False,
        "executionStarted": False,
        "cadGeometryVerified": False,
        "savedCurrentDwg": False,
        "authorizationBoundary": (
            "This request is not authorization by itself. The operator must separately "
            "confirm scope, CODEX_PREVIEW, readback, rollback, no-save guard, backend "
            "identity, launch packet hash, and authorization receipt hash before any real live spike."
        ),
        "notEvidenceFor": _native_not_evidence_for(),
    }


def _ledger_refs(*, transaction_id: str) -> dict[str, str]:
    base = f"native-ledger://{transaction_id}"
    return {
        "tool.requested": f"{base}/tool.requested",
        "tool.authorized": f"{base}/tool.authorized",
        "adapter.started": f"{base}/adapter.started",
        "adapter.completed": f"{base}/adapter.completed",
        "readback.recorded": f"{base}/readback.not-run",
        "audit.completed": f"{base}/audit.completed",
        "rollback.applied": f"{base}/rollback.applied",
        "no_save.audit": f"{base}/no-save.audit",
    }


def _p13b_base_packet(
    *,
    kind: str,
    status: str,
    transaction_id: str,
    cad_plan: dict[str, Any] | None,
    backend_identity: dict[str, Any],
    blocking_reasons: list[str],
    readback_plan: dict[str, Any],
    rollback_plan: dict[str, Any],
    no_save_guard: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schemaVersion": NATIVE_THIN_PREFLIGHT_SCHEMA,
        "phase": "Phase 13B",
        "packageId": "phase13b.native-thin-preflight",
        "taskId": "phase13b.native-thin-preflight",
        "kind": kind,
        "transactionId": str(transaction_id),
        "adapterId": "native-thin.backend",
        "backend": NATIVE_THIN_BACKEND,
        "backendIdentity": dict(backend_identity),
        "status": status,
        "verificationStatus": "not_verified",
        "proofStatus": "native_preflight_ready" if status == "ready" else "native_preflight_blocked",
        "targetLayer": _cad_plan_layer(cad_plan) or PREVIEW_LAYER,
        "cadPlan": dict(cad_plan or {}),
        "readbackPlan": dict(readback_plan),
        "rollbackPlan": dict(rollback_plan),
        "noSaveGuard": dict(no_save_guard),
        "rollbackRequired": True,
        "rollbackStatus": "not_started",
        "committedPreview": False,
        "createdHandles": [],
        "createdHandlesRef": f"native-ledger://{transaction_id}/created-handles",
        "blockedReason": ";".join(_unique(blocking_reasons)),
        "blockingReasons": _unique(blocking_reasons),
        "missingEvidence": [],
        "retryable": False,
        "documentState": "not_connected",
        "cadGeometryVerified": False,
        "cadWritesAttempted": False,
        "nativePluginInvoked": False,
        "savedCurrentDwg": False,
        "previewStrategy": "memory_transaction",
        "ledgerRefs": _ledger_refs(transaction_id=str(transaction_id)),
        "allowedEffects": [],
        "nextAllowedEffects": [],
        "forbiddenEffects": list(P13_NATIVE_FORBIDDEN_EFFECTS),
        "completionBoundary": "P13B preflight packet only; real native execution requires separate user authorization",
        "artifacts": {},
        "notEvidenceFor": [
            "native_plugin_execution",
            "real_cad_readback",
            "cad_geometry_verified",
            "training_resume",
            "table_c_progress",
            "current_dwg_save",
            "formal_layer_write",
        ],
    }


def _backend_identity(value: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(value, dict):
        raw = str(value.get("backend") or value.get("id") or "")
    else:
        raw = str(value or "")
    normalized = raw.strip().replace("_", "-")
    if normalized == "native-thin-skeleton":
        backend = "native-thin-skeleton"
    else:
        backend = normalized
    return {
        "backend": backend,
        "adapterId": "native-thin.backend",
        "pluginVersion": "not_invoked",
        "nativePluginInvoked": False,
    }


def _cad_plan_layer(cad_plan: dict[str, Any] | None) -> str:
    if not isinstance(cad_plan, dict):
        return ""
    drawing = cad_plan.get("drawing")
    if not isinstance(drawing, dict):
        return ""
    return str(drawing.get("layer") or "")


def _readiness_packet_blockers(readiness: dict[str, Any] | None) -> list[str]:
    if not readiness:
        return []
    blockers: list[str] = []
    if readiness.get("schemaVersion") != NATIVE_THIN_READINESS_SCHEMA:
        blockers.append("native_readiness_packet_schema_invalid")
    if readiness.get("kind") != "operator_authorization_request":
        blockers.append("native_readiness_packet_kind_invalid")
    if (
        readiness.get("status") != "ready_for_user_authorization"
        or readiness.get("authorizationRequestStatus") != "ready_for_user_authorization"
    ):
        blockers.append("native_readiness_packet_not_ready_for_user_authorization")
    if readiness.get("realLiveSpikeAuthorizationRequired") is not True:
        blockers.append("native_readiness_packet_must_request_live_authorization")
    if readiness.get("operatorLiveSpikeAuthorized") is True or readiness.get("liveExecutionAuthorized") is True:
        blockers.append("native_readiness_packet_must_not_pre_authorize_live_execution")
    if readiness.get("executionStarted") is True:
        blockers.append("native_readiness_packet_must_not_start_execution")
    if readiness.get("cadWritesAttempted") is True:
        blockers.append("native_readiness_packet_must_not_attempt_cad_write")
    if readiness.get("nativePluginInvoked") is True:
        blockers.append("native_readiness_packet_must_not_invoke_plugin")
    if readiness.get("cadGeometryVerified") is True:
        blockers.append("native_readiness_packet_must_not_claim_geometry_verified")
    if readiness.get("savedCurrentDwg") is True:
        blockers.append("native_readiness_packet_must_not_save_dwg")
    if readiness.get("targetLayer") != PREVIEW_LAYER:
        blockers.append("target_layer_must_be_CODEX_PREVIEW")
    if _cad_plan_layer(dict(readiness.get("cadPlan") or {})) != PREVIEW_LAYER:
        blockers.append("cad_plan_target_layer_must_be_CODEX_PREVIEW")
    backend = _backend_identity(dict(readiness.get("backendIdentity") or {}))
    if backend["backend"] != "native-thin-skeleton":
        blockers.append("backend_identity_must_be_native_thin_skeleton")
    readback = dict(readiness.get("readbackPlan") or {})
    rollback = dict(readiness.get("rollbackPlan") or {})
    no_save = dict(readiness.get("noSaveGuard") or {})
    if readback.get("required") is not True:
        blockers.append("readback_plan_required")
    if rollback.get("required") is not True:
        blockers.append("rollback_plan_required")
    if no_save.get("required") is not True:
        blockers.append("no_save_guard_required")
    if no_save.get("saveAllowed") is not False:
        blockers.append("no_save_guard_must_block_save")
    if not str(readiness.get("launchPacketHash") or ""):
        blockers.append("native_live_spike_launch_packet_hash_required")
    if not str(readiness.get("authorizationReceiptHash") or ""):
        blockers.append("native_live_spike_authorization_receipt_hash_required")
    request = readiness.get("operatorAuthorizationRequest")
    if not isinstance(request, dict) or not request:
        blockers.append("native_operator_authorization_request_required")
    elif request.get("requiresSeparateUserAuthorization") is not True:
        blockers.append("native_operator_authorization_request_must_require_separate_authorization")
    return _unique(blockers)


def _operator_live_spike_authorization_blockers(
    *, auth: dict[str, Any], readiness: dict[str, Any]
) -> list[str]:
    blockers: list[str] = []
    if auth.get("explicit") is not True:
        blockers.append("native_live_spike_operator_authorization_required")
    required_flags = {
        "scopeConfirmed": "native_live_spike_scope_confirmation_required",
        "cadPlanConfirmed": "native_live_spike_cad_plan_confirmation_required",
        "codexPreviewConfirmed": "native_live_spike_codex_preview_confirmation_required",
        "readbackConfirmed": "native_live_spike_readback_confirmation_required",
        "rollbackConfirmed": "native_live_spike_rollback_confirmation_required",
        "noSaveConfirmed": "native_live_spike_no_save_confirmation_required",
        "backendIdentityConfirmed": "native_live_spike_backend_identity_confirmation_required",
    }
    for key, blocker in required_flags.items():
        if auth.get(key) is not True:
            blockers.append(blocker)
    expected_launch = str(readiness.get("launchPacketHash") or "")
    actual_launch = str(auth.get("launchPacketHash") or "")
    if not actual_launch:
        blockers.append("native_live_spike_launch_packet_hash_required")
    elif expected_launch and actual_launch != expected_launch:
        blockers.append("native_live_spike_launch_packet_hash_mismatch")
    expected_receipt = str(readiness.get("authorizationReceiptHash") or "")
    actual_receipt = str(auth.get("authorizationReceiptHash") or "")
    if not actual_receipt:
        blockers.append("native_live_spike_authorization_receipt_hash_required")
    elif expected_receipt and actual_receipt != expected_receipt:
        blockers.append("native_live_spike_authorization_receipt_hash_mismatch")
    if not str(auth.get("statement") or "").strip():
        blockers.append("native_live_spike_authorization_statement_required")
    return _unique(blockers)


def _live_spike_environment_blockers(*, environment: dict[str, Any], readiness: dict[str, Any]) -> list[str]:
    if not environment:
        return ["native_live_backend_environment_required"]
    blockers: list[str] = []
    if environment.get("nativeThinBackendAvailable") is not True:
        blockers.append("native_live_backend_not_available")
    if environment.get("autocadConnectionAvailable") is not True:
        blockers.append("native_live_autocad_connection_required")
    if environment.get("readbackRunnerAvailable") is not True:
        blockers.append("native_live_readback_runner_required")
    if environment.get("rollbackRunnerAvailable") is not True:
        blockers.append("native_live_rollback_runner_required")
    if environment.get("noSaveGuardActive") is not True:
        blockers.append("native_live_no_save_guard_required")
    backend = _backend_identity(_dict_value(environment.get("backendIdentity")))
    expected_backend = _backend_identity(_dict_value(readiness.get("backendIdentity")))["backend"]
    if backend["backend"] != expected_backend:
        blockers.append("native_live_backend_identity_mismatch")
    target_layer = str(environment.get("targetLayer") or readiness.get("targetLayer") or PREVIEW_LAYER)
    if target_layer != PREVIEW_LAYER:
        blockers.append("target_layer_must_be_CODEX_PREVIEW")
    if environment.get("dwgSaveAllowed") is True:
        blockers.append("native_live_environment_must_not_allow_dwg_save")
    if environment.get("formalLayerWriteAllowed") is True:
        blockers.append("native_live_environment_must_not_allow_formal_layer_write")
    return _unique(blockers)


def _load_readiness_packet(
    *,
    readiness_packet: dict[str, Any] | None,
    readiness_packet_path: str | Path | None,
) -> tuple[dict[str, Any] | None, list[str]]:
    if isinstance(readiness_packet, dict):
        return dict(readiness_packet), []
    if readiness_packet_path is None:
        return None, ["native_readiness_packet_required"]
    path = Path(readiness_packet_path)
    if not path.is_file():
        return None, ["native_readiness_packet_missing"]
    return dict(json.loads(path.read_text(encoding="utf-8"))), []


def _load_scope_receipt(
    *,
    scope_receipt: dict[str, Any] | None,
    scope_receipt_path: str | Path | None,
) -> tuple[dict[str, Any] | None, list[str]]:
    if isinstance(scope_receipt, dict):
        return dict(scope_receipt), []
    if scope_receipt_path is None:
        return None, ["native_scope_receipt_required"]
    path = Path(scope_receipt_path)
    if not path.is_file():
        return None, ["native_scope_receipt_missing"]
    return dict(json.loads(path.read_text(encoding="utf-8"))), []


def _load_launch_packet(
    *,
    launch_packet: dict[str, Any] | None,
    launch_packet_path: str | Path | None,
) -> tuple[dict[str, Any] | None, list[str]]:
    if isinstance(launch_packet, dict):
        return dict(launch_packet), []
    if launch_packet_path is None:
        return None, ["native_launch_packet_required"]
    path = Path(launch_packet_path)
    if not path.is_file():
        return None, ["native_launch_packet_missing"]
    return dict(json.loads(path.read_text(encoding="utf-8"))), []


def _load_authorization_gate(
    *,
    authorization_gate: dict[str, Any] | None,
    authorization_gate_path: str | Path | None,
) -> tuple[dict[str, Any] | None, list[str]]:
    if isinstance(authorization_gate, dict):
        return dict(authorization_gate), []
    if authorization_gate_path is None:
        return None, ["native_authorization_gate_required"]
    path = Path(authorization_gate_path)
    if not path.is_file():
        return None, ["native_authorization_gate_missing"]
    return dict(json.loads(path.read_text(encoding="utf-8"))), []


def _load_execution_receipt(
    *,
    execution_receipt: dict[str, Any] | None,
    execution_receipt_path: str | Path | None,
) -> tuple[dict[str, Any] | None, list[str]]:
    if isinstance(execution_receipt, dict):
        return dict(execution_receipt), []
    if execution_receipt_path is None:
        return None, ["native_execution_receipt_required"]
    path = Path(execution_receipt_path)
    if not path.is_file():
        return None, ["native_execution_receipt_missing"]
    return dict(json.loads(path.read_text(encoding="utf-8"))), []


def _launch_packet_hash(packet: dict[str, Any]) -> str:
    critical_scope = {
        "schemaVersion": packet.get("schemaVersion"),
        "kind": packet.get("kind"),
        "adapterId": packet.get("adapterId"),
        "backendIdentity": packet.get("backendIdentity"),
        "targetLayer": packet.get("targetLayer"),
        "cadPlan": packet.get("cadPlan"),
        "readbackPlan": packet.get("readbackPlan"),
        "rollbackPlan": packet.get("rollbackPlan"),
        "noSaveGuard": packet.get("noSaveGuard"),
        "scopeReceiptPath": packet.get("scopeReceiptPath"),
    }
    return _stable_hash(critical_scope)


def _execution_receipt_hash(receipt: dict[str, Any]) -> str:
    critical_scope = {
        "schemaVersion": receipt.get("schemaVersion"),
        "kind": receipt.get("kind"),
        "adapterId": receipt.get("adapterId"),
        "backendIdentity": receipt.get("backendIdentity"),
        "receiptStatus": receipt.get("receiptStatus"),
        "authorizationStatus": receipt.get("authorizationStatus"),
        "launchPacketHash": receipt.get("launchPacketHash"),
        "scopeHash": receipt.get("scopeHash"),
        "scopeMatch": receipt.get("scopeMatch"),
        "targetLayer": receipt.get("targetLayer"),
        "cadPlan": receipt.get("cadPlan"),
        "readbackPlan": receipt.get("readbackPlan"),
        "rollbackPlan": receipt.get("rollbackPlan"),
        "noSaveGuard": receipt.get("noSaveGuard"),
        "executionStarted": receipt.get("executionStarted"),
        "cadWritesAttempted": receipt.get("cadWritesAttempted"),
        "nativePluginInvoked": receipt.get("nativePluginInvoked"),
        "cadGeometryVerified": receipt.get("cadGeometryVerified"),
        "savedCurrentDwg": receipt.get("savedCurrentDwg"),
    }
    return _stable_hash(critical_scope)


def _readiness_packet_hash(readiness: dict[str, Any]) -> str:
    critical_scope = {
        "schemaVersion": readiness.get("schemaVersion"),
        "kind": readiness.get("kind"),
        "adapterId": readiness.get("adapterId"),
        "backendIdentity": readiness.get("backendIdentity"),
        "status": readiness.get("status"),
        "authorizationRequestStatus": readiness.get("authorizationRequestStatus"),
        "targetLayer": readiness.get("targetLayer"),
        "cadPlan": readiness.get("cadPlan"),
        "readbackPlan": readiness.get("readbackPlan"),
        "rollbackPlan": readiness.get("rollbackPlan"),
        "noSaveGuard": readiness.get("noSaveGuard"),
        "launchPacketHash": readiness.get("launchPacketHash"),
        "authorizationReceiptHash": readiness.get("authorizationReceiptHash"),
        "executionReceiptHash": readiness.get("executionReceiptHash"),
        "cadWritesAttempted": readiness.get("cadWritesAttempted"),
        "nativePluginInvoked": readiness.get("nativePluginInvoked"),
        "executionStarted": readiness.get("executionStarted"),
        "cadGeometryVerified": readiness.get("cadGeometryVerified"),
        "savedCurrentDwg": readiness.get("savedCurrentDwg"),
    }
    return _stable_hash(critical_scope)


def _stable_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _native_not_evidence_for() -> list[str]:
    return [
        "native_plugin_execution",
        "real_cad_readback",
        "geometry_verified",
        "cad_geometry_verified",
        "training_resume",
        "table_c_progress",
        "current_dwg_save",
        "formal_layer_write",
    ]


def _write_json(*, output_dir: str | Path, filename: str, payload: dict[str, Any]) -> str:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    path = root / filename
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _dict_value(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    return {}
