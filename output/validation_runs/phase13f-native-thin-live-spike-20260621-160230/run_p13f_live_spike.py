from __future__ import annotations

import json
import os
from pathlib import Path

from core.contracts.cad_agent_harness import run_harness_command
from core.contracts.native_thin_backend import (
    build_native_thin_backend_authorization_gate,
    build_native_thin_backend_execution_receipt,
    build_native_thin_backend_launch_packet,
    build_native_thin_backend_readiness_packet,
    build_native_thin_backend_scope_receipt,
)

out = Path(os.environ["P13F_OUT_DIR"])
plan = {
    "version": "0.1",
    "domain": "generic",
    "intent": "draw_object",
    "object": {"type": "table", "name": "P13F native thin scoped preview", "width": 1200, "depth": 600},
    "placement": {"mode": "absolute", "base_point": [100, 200, 0]},
    "drawing": {"layer": "CODEX_PREVIEW", "include_label": False, "include_dimensions": False},
    "confidence": 0.91,
    "needs_confirmation": False,
}
scope_receipt = build_native_thin_backend_scope_receipt(
    cad_plan=plan,
    output_dir=out,
    scope_confirmed=True,
    confirmation_statement="User authorized P13F minimal real native backend live spike: scoped preview only.",
    backend_identity="native-thin-skeleton",
    readback_plan={"required": True, "strategy": "created_handles_bbox_props"},
    rollback_plan={"required": True, "strategy": "rollback_batch"},
    no_save_guard={"required": True, "saveAllowed": False},
)
launch_packet = build_native_thin_backend_launch_packet(
    scope_receipt_path=scope_receipt["artifacts"]["nativeThinScopeReceipt"],
    output_dir=out,
)
pending_gate = build_native_thin_backend_authorization_gate(launch_packet=launch_packet)
ready_gate = build_native_thin_backend_authorization_gate(
    launch_packet=launch_packet,
    output_dir=out,
    user_authorization={
        "explicit": True,
        "scopeConfirmed": True,
        "cadPlanConfirmed": True,
        "codexPreviewConfirmed": True,
        "readbackConfirmed": True,
        "rollbackConfirmed": True,
        "noSaveConfirmed": True,
        "backendIdentityConfirmed": True,
        "launchPacketHash": pending_gate["launchPacketHash"],
        "statement": "P13F live spike authorization: CODEX_PREVIEW only, readback, rollback, no-save, native-thin backend identity confirmed.",
    },
)
execution_receipt = build_native_thin_backend_execution_receipt(
    authorization_gate_path=ready_gate["artifacts"]["nativeThinAuthorizationGate"],
    output_dir=out,
)
readiness = build_native_thin_backend_readiness_packet(
    execution_receipt_path=execution_receipt["artifacts"]["nativeThinExecutionReceipt"],
    output_dir=out,
)
operator_authorization = {
    "explicit": True,
    "scopeConfirmed": True,
    "cadPlanConfirmed": True,
    "codexPreviewConfirmed": True,
    "readbackConfirmed": True,
    "rollbackConfirmed": True,
    "noSaveConfirmed": True,
    "backendIdentityConfirmed": True,
    "launchPacketHash": readiness["launchPacketHash"],
    "authorizationReceiptHash": readiness["authorizationReceiptHash"],
    "environmentReady": True,
    "statement": "User authorized P13F minimal live spike: scope, CAD_PLAN, CODEX_PREVIEW-only, readback, rollback, no-save, backend identity, launch hash, authorization receipt hash, and environment readiness confirmed.",
}
environment = {
    "nativeThinBackendAvailable": True,
    "autocadConnectionAvailable": True,
    "readbackRunnerAvailable": True,
    "rollbackRunnerAvailable": True,
    "noSaveGuardActive": True,
    "backendIdentity": {"backend": "native-thin-skeleton"},
    "targetLayer": "CODEX_PREVIEW",
    "dwgSaveAllowed": False,
    "formalLayerWriteAllowed": False,
    "accoreConsolePath": r"D:\Design\CAD\AutoCAD 2026\accoreconsole.exe",
    "pluginDllPath": str((Path.cwd() / "native_plugins" / "native_thin_backend" / "bin" / "Release" / "net8.0-windows" / "NativeThinBackend.dll").resolve()),
}
(out / "native_thin_operator_authorization_p13f.json").write_text(json.dumps(operator_authorization, ensure_ascii=False, indent=2), encoding="utf-8")
(out / "native_thin_live_environment_p13f.json").write_text(json.dumps(environment, ensure_ascii=False, indent=2), encoding="utf-8")
result = run_harness_command(
    "native-thin-live-spike",
    backend="native-thin-live-backend",
    readiness_packet_path=readiness["artifacts"]["nativeThinReadinessPacket"],
    operator_authorization=operator_authorization,
    native_live_environment=environment,
    output_dir=out,
)
result_path = out / "native_thin_live_spike_harness_result.json"
result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
summary = {
    "outputDir": str(out),
    "status": result.get("status"),
    "verificationStatus": result.get("verificationStatus"),
    "cadGeometryVerified": result.get("cadGeometryVerified"),
    "cadWritesAttempted": result.get("cadWritesAttempted"),
    "nativePluginInvoked": result.get("nativePluginInvoked"),
    "savedCurrentDwg": result.get("savedCurrentDwg"),
    "createdHandles": result.get("createdHandles"),
    "rollbackStatus": result.get("rollbackStatus"),
    "blockingReasons": result.get("blockingReasons"),
    "missingEvidence": result.get("missingEvidence"),
    "artifacts": result.get("artifacts"),
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
