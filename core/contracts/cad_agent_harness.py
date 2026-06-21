"""P9B agent-native CLI harness result contract.

This module is a thin facade over existing Phase 9 validation, dry-run, and
preview runner logic. It does not add CAD capabilities or completion authority.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from core.contracts.phase9_preview import (
    build_phase9_preview_scope_record,
    phase9_default_single_preview_plan,
    run_phase9_single_preview,
)
from core.contracts.adapter_registry import (
    annotate_harness_result_with_registry,
    authorize_harness_command,
    blocked_harness_result_for_authorization,
)
from core.plan_engine.dry_run_report import create_dry_run_report
from core.plan_engine.validate_plan import load_json, validate_plan
from core.safety.policy import PREVIEW_LAYER

SCHEMA_VERSION = "cad-agent-harness-result/v1"
SUPPORTED_COMMANDS = {
    "validate",
    "dry-run",
    "probe",
    "preview",
    "readback",
    "evidence",
    "bundle",
    "exit-gate",
    "rehearsal-closeout",
    "rehearsal-plan",
    "rehearsal-preflight",
    "rehearsal-result",
    "rehearsal-run",
    "rehearsal-scope-receipt",
    "rehearsal-scope-proposal",
    "mock-plugin-transaction",
    "native-thin-backend",
    "native-thin-live-spike",
    "engineering-kernel-diff",
}
DEFAULT_LIVE_BACKEND = "cad-session-host"

BACKEND_ALIASES = {
    "autocad-com-existing": "autocad_com_existing",
    "autocad_com_existing": "autocad_com_existing",
    "cad-session-host": "cad_session_host",
    "cad_session_host": "cad_session_host",
    "fake-driver": "fake_driver_preflight",
    "fake_driver_preflight": "fake_driver_preflight",
    "mock-plugin-like": "mock_plugin_like",
    "mock_plugin_like": "mock_plugin_like",
    "native-thin-skeleton": "native_thin_skeleton",
    "native_thin_skeleton": "native_thin_skeleton",
    "native-thin-live-backend": "native_thin_live_backend",
    "native_thin_live_backend": "native_thin_live_backend",
    "engineering-kernel": "engineering_kernel",
    "engineering_kernel": "engineering_kernel",
}

SAFE_DEFAULTS = {
    "saveAllowed": False,
    "deleteAllowed": False,
    "formalLayersAllowed": False,
    "connectExistingOnly": True,
}


def run_harness_command(
    command: str,
    *,
    cad_plan: dict[str, Any] | None = None,
    plan_path: str | Path | None = None,
    scope: dict[str, Any] | None = None,
    scope_path: str | Path | None = None,
    scope_receipt_path: str | Path | None = None,
    launch_packet_path: str | Path | None = None,
    authorization_gate_path: str | Path | None = None,
    execution_receipt_path: str | Path | None = None,
    readiness_packet_path: str | Path | None = None,
    operator_authorization: dict[str, Any] | None = None,
    operator_authorization_path: str | Path | None = None,
    native_live_environment: dict[str, Any] | None = None,
    native_live_environment_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    run_dir: str | Path | None = None,
    backend: str = "none",
    live_runs_confirmed: bool = False,
    confirmation_statement: str = "",
    requested_effects: list[str] | None = None,
    adapter_id: str | None = None,
    mock_transaction_mode: str = "success",
    native_backend_mode: str = "contract_ready",
    native_scope_confirmed: bool = False,
) -> dict[str, Any]:
    normalized = _normalize_command(command)
    registry_authorization = authorize_harness_command(
        command=normalized,
        backend=backend,
        requested_effects=requested_effects,
        adapter_id=adapter_id,
    )
    if registry_authorization.status != "allowed":
        return blocked_harness_result_for_authorization(
            command=normalized,
            backend=backend,
            authorization_result=registry_authorization,
        )

    def _registered(result: dict[str, Any]) -> dict[str, Any]:
        return annotate_harness_result_with_registry(result, registry_authorization)

    explicit_plan_provided = cad_plan is not None or plan_path is not None
    plan = _load_plan(cad_plan=cad_plan, plan_path=plan_path)

    if normalized == "validate":
        return _registered(_validate_result(plan))
    if normalized == "dry-run":
        return _registered(_dry_run_result(plan))
    if normalized == "probe":
        return _registered(_probe_result(plan=plan, backend=backend))
    if normalized == "preview":
        return _registered(_preview_result(plan=plan, output_dir=output_dir, backend=backend))
    if normalized == "readback":
        return _registered(_readback_result(run_dir=run_dir or output_dir))
    if normalized == "evidence":
        return _registered(_evidence_result(run_dir=run_dir or output_dir))
    if normalized == "bundle":
        return _registered(_bundle_result(run_dir=run_dir or output_dir))
    if normalized == "exit-gate":
        return _registered(_exit_gate_result(run_dir=run_dir or output_dir))
    if normalized == "rehearsal-closeout":
        return _registered(_rehearsal_closeout_result(rehearsal_dir=run_dir or output_dir))
    if normalized == "rehearsal-scope-proposal":
        return _registered(
            _rehearsal_scope_proposal_result(
                phase9_exit_run_dir=run_dir,
                output_dir=output_dir,
            )
        )
    if normalized == "rehearsal-plan":
        return _registered(
            _rehearsal_plan_result(
                scope=_load_scope(scope=scope, scope_path=scope_path, fallback_plan=plan),
                output_dir=output_dir,
            )
        )
    if normalized == "rehearsal-scope-receipt":
        return _registered(
            _rehearsal_scope_receipt_result(
                plan_path=plan_path,
                output_dir=output_dir,
                live_runs_confirmed=live_runs_confirmed,
                confirmation_statement=confirmation_statement,
            )
        )
    if normalized == "rehearsal-preflight":
        return _registered(
            _rehearsal_preflight_result(
                plan_path=plan_path,
                output_dir=output_dir,
                scope_receipt_path=scope_receipt_path,
                live_runs_confirmed=live_runs_confirmed,
            )
        )
    if normalized == "rehearsal-result":
        return _registered(_rehearsal_result_result(rehearsal_dir=run_dir or output_dir))
    if normalized == "rehearsal-run":
        return _registered(
            _rehearsal_run_result(
                plan_path=plan_path,
                output_dir=output_dir,
                scope_receipt_path=scope_receipt_path,
                live_runs_confirmed=live_runs_confirmed,
            )
        )
    if normalized == "mock-plugin-transaction":
        return _registered(_mock_plugin_transaction_result(mode=mock_transaction_mode))
    if normalized == "native-thin-backend":
        return _registered(
            _native_thin_backend_result(
                mode=native_backend_mode,
                cad_plan=plan if explicit_plan_provided else None,
                output_dir=output_dir,
                scope_receipt_path=scope_receipt_path,
                launch_packet_path=launch_packet_path,
                authorization_gate_path=authorization_gate_path,
                execution_receipt_path=execution_receipt_path,
                readiness_packet_path=readiness_packet_path,
                scope_confirmed=native_scope_confirmed,
                confirmation_statement=confirmation_statement,
            )
        )
    if normalized == "native-thin-live-spike":
        return _registered(
            _native_thin_live_spike_result(
                output_dir=output_dir,
                readiness_packet_path=readiness_packet_path,
                operator_authorization=_load_json_dict(
                    payload=operator_authorization,
                    path=operator_authorization_path,
                ),
                environment=_load_json_dict(
                    payload=native_live_environment,
                    path=native_live_environment_path,
                ),
            )
        )
    if normalized == "engineering-kernel-diff":
        return _registered(
            _engineering_kernel_diff_result(
                cad_plan=plan if explicit_plan_provided else plan,
                output_dir=output_dir,
            )
        )

    raise AssertionError(f"unhandled harness command: {normalized}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CAD Agent Phase 9 harness facade")
    parser.add_argument("command", choices=sorted(SUPPORTED_COMMANDS))
    parser.add_argument("--plan", dest="plan_path", default=None)
    parser.add_argument("--scope", dest="scope_path", default=None)
    parser.add_argument("--scope-receipt", dest="scope_receipt_path", default=None)
    parser.add_argument("--launch-packet", dest="launch_packet_path", default=None)
    parser.add_argument("--authorization-gate", dest="authorization_gate_path", default=None)
    parser.add_argument("--execution-receipt", dest="execution_receipt_path", default=None)
    parser.add_argument("--readiness-packet", dest="readiness_packet_path", default=None)
    parser.add_argument("--operator-authorization", dest="operator_authorization_path", default=None)
    parser.add_argument("--native-live-environment", dest="native_live_environment_path", default=None)
    parser.add_argument("--confirmation", dest="confirmation_statement", default="")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-dir", default=None)
    parser.add_argument("--backend", default="none")
    parser.add_argument("--confirm-live-runs", action="store_true", dest="live_runs_confirmed")
    parser.add_argument("--requested-effect", action="append", dest="requested_effects", default=None)
    parser.add_argument("--adapter-id", default=None)
    parser.add_argument("--mock-transaction-mode", default="success")
    parser.add_argument("--native-backend-mode", default="contract_ready")
    parser.add_argument("--confirm-native-scope", action="store_true", dest="native_scope_confirmed")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args(argv)

    result = run_harness_command(
        args.command,
        plan_path=args.plan_path,
        scope_path=args.scope_path,
        scope_receipt_path=args.scope_receipt_path,
        launch_packet_path=args.launch_packet_path,
        authorization_gate_path=args.authorization_gate_path,
        execution_receipt_path=args.execution_receipt_path,
        readiness_packet_path=args.readiness_packet_path,
        operator_authorization_path=args.operator_authorization_path,
        native_live_environment_path=args.native_live_environment_path,
        output_dir=args.output_dir,
        run_dir=args.run_dir,
        backend=args.backend,
        live_runs_confirmed=args.live_runs_confirmed,
        confirmation_statement=args.confirmation_statement,
        requested_effects=args.requested_effects,
        adapter_id=args.adapter_id,
        mock_transaction_mode=args.mock_transaction_mode,
        native_backend_mode=args.native_backend_mode,
        native_scope_confirmed=args.native_scope_confirmed,
    )
    text = json.dumps(result, ensure_ascii=False, indent=2 if args.json_output else None)
    print(text)
    return 0 if result.get("status") not in {"fail"} else 1


def _validate_result(plan: dict[str, Any]) -> dict[str, Any]:
    errors = [str(item) for item in validate_plan(plan)]
    return _base_result(
        command="validate",
        plan=plan,
        status="pass" if not errors else "fail",
        backend="none",
        validation_errors=errors,
        artifacts={},
    )


def _dry_run_result(plan: dict[str, Any]) -> dict[str, Any]:
    report = create_dry_run_report(plan)
    status = "pass" if report.get("status") == "valid" else "fail"
    return _base_result(
        command="dry-run",
        plan=plan,
        status=status,
        backend="none",
        validation_errors=[str(item) for item in report.get("validation_errors", [])],
        artifacts={"dryRunStatus": str(report.get("status", ""))},
    )


def _probe_result(*, plan: dict[str, Any], backend: str) -> dict[str, Any]:
    backend_label = backend if backend != "none" else DEFAULT_LIVE_BACKEND
    result = _base_result(
        command="probe",
        plan=plan,
        status="pass",
        backend=backend_label,
        artifacts={},
    )
    result["autoCADReadinessProbe"] = {
        "status": "not_run",
        "backend": _phase9_backend(backend_label),
        "previewAttempted": False,
        "boundary": "P9B probe command does not touch AutoCAD; P9A owns live COM readiness.",
    }
    return result


def _preview_result(
    *,
    plan: dict[str, Any],
    output_dir: str | Path | None,
    backend: str,
) -> dict[str, Any]:
    backend_label = backend if backend != "none" else DEFAULT_LIVE_BACKEND
    result = run_phase9_single_preview(
        cad_plan=plan,
        output_dir=output_dir,
        driver_factory=_driver_factory_for_backend(backend_label),
        driver_backend=_phase9_backend(backend_label),
    )
    return _from_phase9_report(
        command="preview",
        report=result.report,
        readback_entities=result.readback_entities,
        backend=backend_label,
    )


def _readback_result(run_dir: str | Path | None) -> dict[str, Any]:
    root = _require_run_dir(run_dir)
    readback_path = root / "phase9_single_preview_readback_entities.json"
    report = _read_report(root)
    payload = _read_json(readback_path) if readback_path.is_file() else {"entities": []}
    return _from_phase9_report(
        command="readback",
        report=report,
        readback_entities=[dict(item) for item in payload.get("entities", [])],
        backend=str(report.get("driverBackend") or "unknown"),
    )


def _evidence_result(run_dir: str | Path | None) -> dict[str, Any]:
    root = _require_run_dir(run_dir)
    report = _read_report(root)
    readback_path = root / "phase9_single_preview_readback_entities.json"
    payload = _read_json(readback_path) if readback_path.is_file() else {"entities": []}
    return _from_phase9_report(
        command="evidence",
        report=report,
        readback_entities=[dict(item) for item in payload.get("entities", [])],
        backend=str(report.get("driverBackend") or "unknown"),
    )


def _bundle_result(run_dir: str | Path | None) -> dict[str, Any]:
    root = _require_run_dir(run_dir)
    from core.contracts.preview_bundle import build_phase9_preview_bundle

    bundle = build_phase9_preview_bundle(run_dir=root)
    summary = _read_json(Path(bundle["summaryPath"]))
    result = _base_result(
        command="bundle",
        plan=None,
        status=str(summary.get("status") or "not_verified"),
        verification_status=str(summary.get("verificationStatus") or "not_verified"),
        backend="preview_bundle",
        target_layer=str(summary.get("targetLayer") or PREVIEW_LAYER),
        saved_current_dwg=bool(summary.get("savedCurrentDwg", False)),
        evidence_package_ref=str(summary.get("evidencePackageRef") or ""),
        blocking_reasons=[str(item) for item in summary.get("blockingReasons", [])],
        missing_evidence=[str(item) for item in summary.get("missingEvidence", [])],
        cad_geometry_verified=bool(summary.get("cadGeometryVerified", False)),
        artifacts={
            "previewBundleManifest": str(bundle["manifestPath"]),
            "previewBundleSummary": str(bundle["summaryPath"]),
            "previewBundleSession": str(bundle.get("sessionPath") or ""),
            "previewBundleTrajectory": str(bundle.get("trajectoryPath") or ""),
        },
    )
    result["bundle"] = bundle
    result["completionBoundary"] = str(summary.get("completionBoundary") or "")
    return result


def _exit_gate_result(run_dir: str | Path | None) -> dict[str, Any]:
    root = _require_run_dir(run_dir)
    from core.contracts.phase9_exit_gate import evaluate_phase9_exit_gate

    gate = evaluate_phase9_exit_gate(run_dir=root)
    result = _base_result(
        command="exit-gate",
        plan=None,
        status=str(gate.get("status") or "blocked"),
        verification_status=str(gate.get("verificationStatus") or "not_verified"),
        backend="phase9_exit_gate",
        target_layer=str(gate.get("targetLayer") or PREVIEW_LAYER),
        saved_current_dwg=bool(gate.get("savedCurrentDwg", False)),
        blocking_reasons=[str(item) for item in gate.get("blockingReasons", [])],
        missing_evidence=[str(item) for item in gate.get("missingEvidence", [])],
        cad_geometry_verified=bool(gate.get("cadGeometryVerified", False)),
        artifacts={
            "phase9ExitReport": str(gate.get("reportPath") or ""),
            "previewBundleManifest": str(gate.get("previewBundleManifest") or ""),
            "previewBundleSummary": str(gate.get("previewBundleSummary") or ""),
        },
    )
    result["phase10Allowed"] = bool(gate.get("phase10Allowed", False))
    result["completionCanClaimComplete"] = bool(gate.get("completionCanClaimComplete", False))
    result["decisionBoundary"] = str(gate.get("decisionBoundary") or "")
    result["exitGate"] = gate
    return result


def _rehearsal_plan_result(
    *,
    scope: dict[str, Any],
    output_dir: str | Path | None,
) -> dict[str, Any]:
    if output_dir is None:
        raise ValueError("--output-dir is required for rehearsal-plan")
    from core.contracts.phase10_rehearsal import prepare_phase10_rehearsal_plan

    plan = prepare_phase10_rehearsal_plan(scope=scope, output_dir=output_dir)
    result = _base_result(
        command="rehearsal-plan",
        plan=None,
        status=str(plan.get("status") or "blocked"),
        verification_status="not_verified",
        backend=str(plan.get("backend") or DEFAULT_LIVE_BACKEND),
        target_layer=PREVIEW_LAYER,
        saved_current_dwg=False,
        blocking_reasons=[str(item) for item in plan.get("blockingReasons", [])],
        missing_evidence=[],
        cad_geometry_verified=False,
        artifacts={
            "phase10RehearsalScope": str(plan.get("scopePath") or ""),
            "phase10RehearsalPlan": str(plan.get("planPath") or ""),
        },
    )
    result["taskId"] = str(plan.get("taskId") or "phase10-focused-rehearsal-plan")
    result["cadWritesAttempted"] = bool(plan.get("cadWritesAttempted", False))
    result["allowedEffects"] = [str(item) for item in plan.get("allowedEffects", [])]
    result["plannedRunAllowedEffects"] = [str(item) for item in plan.get("plannedRunAllowedEffects", [])]
    result["forbiddenEffects"] = [str(item) for item in plan.get("forbiddenEffects", [])]
    result["completionBoundary"] = str(plan.get("completionBoundary") or "")
    result["notEvidenceFor"] = [str(item) for item in plan.get("notEvidenceFor", [])]
    result["rehearsalPlan"] = plan
    return result


def _rehearsal_scope_proposal_result(
    *,
    phase9_exit_run_dir: str | Path | None,
    output_dir: str | Path | None,
) -> dict[str, Any]:
    if phase9_exit_run_dir is None:
        raise ValueError("--run-dir is required for rehearsal-scope-proposal")
    if output_dir is None:
        raise ValueError("--output-dir is required for rehearsal-scope-proposal")
    from core.contracts.phase10_rehearsal import build_phase10_rehearsal_scope_proposal

    proposal = build_phase10_rehearsal_scope_proposal(
        phase9_exit_run_dir=phase9_exit_run_dir,
        output_dir=output_dir,
    )
    source_artifacts = proposal.get("sourceArtifacts") if isinstance(proposal.get("sourceArtifacts"), dict) else {}
    result = _base_result(
        command="rehearsal-scope-proposal",
        plan=None,
        status=str(proposal.get("status") or "blocked"),
        verification_status=str(proposal.get("verificationStatus") or "not_verified"),
        backend="phase10_rehearsal_scope_proposal",
        target_layer=PREVIEW_LAYER,
        saved_current_dwg=False,
        blocking_reasons=[str(item) for item in proposal.get("blockingReasons", [])],
        missing_evidence=[str(item) for item in proposal.get("missingEvidence", [])],
        cad_geometry_verified=False,
        artifacts={
            "phase10RehearsalScopeProposal": str(proposal.get("proposalPath") or ""),
            "phase9ExitRun": str(proposal.get("phase9ExitRunDir") or ""),
            "phase9Report": str(source_artifacts.get("phase9Report") or ""),
            "sourceCadPlan": str(source_artifacts.get("cadPlan") or ""),
        },
    )
    result["taskId"] = str(proposal.get("taskId") or "phase10-focused-rehearsal-scope-proposal")
    result["cadWritesAttempted"] = bool(proposal.get("cadWritesAttempted", False))
    result["proposalReady"] = bool(proposal.get("proposalReady", False))
    result["scopeConfirmed"] = bool(proposal.get("scopeConfirmed", False))
    result["liveRunsConfirmed"] = bool(proposal.get("liveRunsConfirmed", False))
    result["candidateScope"] = dict(proposal.get("candidateScope") or {})
    result["allowedEffects"] = [str(item) for item in proposal.get("allowedEffects", [])]
    result["nextAllowedEffects"] = [str(item) for item in proposal.get("nextAllowedEffects", [])]
    result["completionBoundary"] = str(proposal.get("completionBoundary") or "")
    result["notEvidenceFor"] = [str(item) for item in proposal.get("notEvidenceFor", [])]
    result["rehearsalScopeProposal"] = proposal
    return result


def _rehearsal_result_result(rehearsal_dir: str | Path | None) -> dict[str, Any]:
    if rehearsal_dir is None:
        raise ValueError("--run-dir or --output-dir is required for rehearsal-result")
    from core.contracts.phase10_rehearsal import evaluate_phase10_rehearsal_runs

    rehearsal = evaluate_phase10_rehearsal_runs(rehearsal_dir=rehearsal_dir, output_dir=rehearsal_dir)
    result = _base_result(
        command="rehearsal-result",
        plan=None,
        status=str(rehearsal.get("status") or "blocked"),
        verification_status=str(rehearsal.get("verificationStatus") or "not_verified"),
        backend="phase10_rehearsal_result",
        target_layer=PREVIEW_LAYER,
        saved_current_dwg=False,
        blocking_reasons=[str(item) for item in rehearsal.get("blockingReasons", [])],
        missing_evidence=[str(item) for item in rehearsal.get("missingEvidence", [])],
        cad_geometry_verified=bool(rehearsal.get("cadGeometryVerified", False)),
        artifacts={
            "phase10RehearsalResult": str(rehearsal.get("resultPath") or ""),
            "phase10RehearsalDiffSummary": str(rehearsal.get("diffSummaryPath") or ""),
            "phase10RehearsalFailureLedger": str(rehearsal.get("failureLedgerPath") or ""),
        },
    )
    result["taskId"] = str(rehearsal.get("taskId") or "phase10-focused-rehearsal-result")
    result["cadWritesAttempted"] = bool(rehearsal.get("cadWritesAttempted", False))
    result["stableGeometry"] = bool(rehearsal.get("stableGeometry", False))
    result["runCount"] = int(rehearsal.get("runCount") or 0)
    result["verifiedRunCount"] = int(rehearsal.get("verifiedRunCount") or 0)
    result["completionBoundary"] = str(rehearsal.get("completionBoundary") or "")
    result["notEvidenceFor"] = [str(item) for item in rehearsal.get("notEvidenceFor", [])]
    result["rehearsalResult"] = rehearsal
    return result


def _rehearsal_scope_receipt_result(
    *,
    plan_path: str | Path | None,
    output_dir: str | Path | None,
    live_runs_confirmed: bool,
    confirmation_statement: str,
) -> dict[str, Any]:
    if plan_path is None:
        raise ValueError("--plan is required for rehearsal-scope-receipt")
    from core.contracts.phase10_rehearsal import build_phase10_rehearsal_scope_receipt

    receipt = build_phase10_rehearsal_scope_receipt(
        plan_path=plan_path,
        output_dir=output_dir,
        live_runs_confirmed=live_runs_confirmed,
        confirmation_statement=confirmation_statement,
    )
    result = _base_result(
        command="rehearsal-scope-receipt",
        plan=None,
        status=str(receipt.get("status") or "blocked"),
        verification_status=str(receipt.get("verificationStatus") or "not_verified"),
        backend="phase10_rehearsal_scope_receipt",
        target_layer=PREVIEW_LAYER,
        saved_current_dwg=False,
        blocking_reasons=[str(item) for item in receipt.get("blockingReasons", [])],
        missing_evidence=[str(item) for item in receipt.get("missingEvidence", [])],
        cad_geometry_verified=False,
        artifacts={
            "phase10RehearsalScopeReceipt": str(receipt.get("receiptPath") or ""),
            "phase10RehearsalPlan": str(receipt.get("planPath") or ""),
        },
    )
    result["taskId"] = str(receipt.get("taskId") or "phase10-focused-rehearsal-scope-receipt")
    result["cadWritesAttempted"] = bool(receipt.get("cadWritesAttempted", False))
    result["scopeConfirmed"] = bool(receipt.get("scopeConfirmed", False))
    result["liveRunsConfirmed"] = bool(receipt.get("liveRunsConfirmed", False))
    result["plannedRunCount"] = int(receipt.get("plannedRunCount") or 0)
    result["allowedEffects"] = [str(item) for item in receipt.get("allowedEffects", [])]
    result["nextAllowedEffects"] = [str(item) for item in receipt.get("nextAllowedEffects", [])]
    result["completionBoundary"] = str(receipt.get("completionBoundary") or "")
    result["notEvidenceFor"] = [str(item) for item in receipt.get("notEvidenceFor", [])]
    result["rehearsalScopeReceipt"] = receipt
    return result


def _rehearsal_preflight_result(
    *,
    plan_path: str | Path | None,
    output_dir: str | Path | None,
    scope_receipt_path: str | Path | None,
    live_runs_confirmed: bool,
) -> dict[str, Any]:
    if plan_path is None:
        raise ValueError("--plan is required for rehearsal-preflight")
    from core.contracts.phase10_rehearsal import build_phase10_rehearsal_launch_packet

    packet = build_phase10_rehearsal_launch_packet(
        plan_path=plan_path,
        output_dir=output_dir,
        scope_receipt_path=scope_receipt_path,
        live_runs_confirmed=live_runs_confirmed,
    )
    result = _base_result(
        command="rehearsal-preflight",
        plan=None,
        status=str(packet.get("status") or "blocked"),
        verification_status=str(packet.get("verificationStatus") or "not_verified"),
        backend="phase10_rehearsal_preflight",
        target_layer=PREVIEW_LAYER,
        saved_current_dwg=False,
        blocking_reasons=[str(item) for item in packet.get("blockingReasons", [])],
        missing_evidence=[str(item) for item in packet.get("missingEvidence", [])],
        cad_geometry_verified=False,
        artifacts={
            "phase10RehearsalLaunchPacket": str(packet.get("launchPacketPath") or ""),
            "phase10RehearsalScopeReceipt": str(packet.get("scopeReceiptPath") or ""),
        },
    )
    result["taskId"] = str(packet.get("taskId") or "phase10-focused-rehearsal-launch-preflight")
    result["cadWritesAttempted"] = bool(packet.get("cadWritesAttempted", False))
    result["launchAllowed"] = bool(packet.get("launchAllowed", False))
    result["liveRunsConfirmed"] = bool(packet.get("liveRunsConfirmed", False))
    result["sessionHostEnvReady"] = bool(packet.get("sessionHostEnvReady", False))
    result["scopeReceiptReady"] = bool(packet.get("scopeReceiptReady", False))
    result["plannedRunCount"] = int(packet.get("plannedRunCount") or 0)
    result["allowedEffects"] = [str(item) for item in packet.get("allowedEffects", [])]
    result["nextAllowedEffects"] = [str(item) for item in packet.get("nextAllowedEffects", [])]
    result["completionBoundary"] = str(packet.get("completionBoundary") or "")
    result["notEvidenceFor"] = [str(item) for item in packet.get("notEvidenceFor", [])]
    result["rehearsalLaunchPacket"] = packet
    return result


def _rehearsal_closeout_result(rehearsal_dir: str | Path | None) -> dict[str, Any]:
    if rehearsal_dir is None:
        raise ValueError("--run-dir or --output-dir is required for rehearsal-closeout")
    from core.contracts.phase10_rehearsal import evaluate_phase10_rehearsal_closeout

    closeout = evaluate_phase10_rehearsal_closeout(
        rehearsal_dir=rehearsal_dir,
        output_dir=rehearsal_dir,
    )
    result = _base_result(
        command="rehearsal-closeout",
        plan=None,
        status=str(closeout.get("status") or "blocked"),
        verification_status=str(closeout.get("verificationStatus") or "not_verified"),
        backend="phase10_rehearsal_closeout",
        target_layer=PREVIEW_LAYER,
        saved_current_dwg=False,
        blocking_reasons=[str(item) for item in closeout.get("blockingReasons", [])],
        missing_evidence=[str(item) for item in closeout.get("missingEvidence", [])],
        cad_geometry_verified=bool(closeout.get("cadGeometryVerified", False)),
        artifacts={
            "phase10RehearsalCloseout": str(closeout.get("closeoutPath") or ""),
            "phase10RehearsalLaunchPacket": str(
                dict(closeout.get("sourceArtifacts") or {}).get("launchPacket") or ""
            ),
            "phase10RehearsalExecution": str(
                dict(closeout.get("sourceArtifacts") or {}).get("execution") or ""
            ),
            "phase10RehearsalResult": str(
                dict(closeout.get("sourceArtifacts") or {}).get("result") or ""
            ),
        },
    )
    result["taskId"] = str(closeout.get("taskId") or "phase10-focused-rehearsal-closeout")
    result["cadWritesAttempted"] = bool(closeout.get("cadWritesAttempted", False))
    result["sourceCadWritesAttempted"] = bool(closeout.get("sourceCadWritesAttempted", False))
    result["phase10CloseoutAllowed"] = bool(closeout.get("phase10CloseoutAllowed", False))
    result["phase11Allowed"] = bool(closeout.get("phase11Allowed", False))
    result["stableGeometry"] = bool(closeout.get("stableGeometry", False))
    result["runCount"] = int(closeout.get("runCount") or 0)
    result["verifiedRunCount"] = int(closeout.get("verifiedRunCount") or 0)
    result["completionBoundary"] = str(closeout.get("completionBoundary") or "")
    result["allowedClaims"] = [str(item) for item in closeout.get("allowedClaims", [])]
    result["notEvidenceFor"] = [str(item) for item in closeout.get("notEvidenceFor", [])]
    result["rehearsalCloseout"] = closeout
    return result


def _rehearsal_run_result(
    *,
    plan_path: str | Path | None,
    output_dir: str | Path | None,
    scope_receipt_path: str | Path | None,
    live_runs_confirmed: bool,
) -> dict[str, Any]:
    if plan_path is None:
        raise ValueError("--plan is required for rehearsal-run")
    from core.contracts.phase10_rehearsal import execute_phase10_rehearsal_plan

    execution = execute_phase10_rehearsal_plan(
        plan_path=plan_path,
        output_dir=output_dir,
        scope_receipt_path=scope_receipt_path,
        live_runs_confirmed=live_runs_confirmed,
    )
    result = _base_result(
        command="rehearsal-run",
        plan=None,
        status=str(execution.get("status") or "blocked"),
        verification_status=str(execution.get("verificationStatus") or "not_verified"),
        backend="phase10_rehearsal_runner",
        target_layer=PREVIEW_LAYER,
        saved_current_dwg=False,
        blocking_reasons=[str(item) for item in execution.get("blockingReasons", [])],
        missing_evidence=[str(item) for item in execution.get("missingEvidence", [])],
        cad_geometry_verified=bool(execution.get("cadGeometryVerified", False)),
        artifacts={
            "phase10RehearsalExecution": str(execution.get("executionPath") or ""),
            "phase10RehearsalScopeReceipt": str(execution.get("scopeReceiptPath") or ""),
            "phase10RehearsalResult": str(
                dict(execution.get("aggregateResult") or {}).get("resultPath") or ""
            ),
            "phase10RehearsalDiffSummary": str(
                dict(execution.get("aggregateResult") or {}).get("diffSummaryPath") or ""
            ),
            "phase10RehearsalFailureLedger": str(
                dict(execution.get("aggregateResult") or {}).get("failureLedgerPath") or ""
            ),
        },
    )
    result["taskId"] = str(execution.get("taskId") or "phase10-focused-rehearsal-execute")
    result["cadWritesAttempted"] = bool(execution.get("cadWritesAttempted", False))
    result["liveRunsConfirmed"] = bool(execution.get("liveRunsConfirmed", False))
    result["executorMode"] = str(execution.get("executorMode") or "")
    result["executedRunCount"] = int(execution.get("executedRunCount") or 0)
    result["completionBoundary"] = str(execution.get("completionBoundary") or "")
    result["notEvidenceFor"] = [str(item) for item in execution.get("notEvidenceFor", [])]
    result["rehearsalExecution"] = execution
    return result


def _mock_plugin_transaction_result(*, mode: str) -> dict[str, Any]:
    from core.contracts.mock_plugin_transaction import execute_mock_plugin_transaction

    transaction = execute_mock_plugin_transaction(mode=mode)
    result = _base_result(
        command="mock-plugin-transaction",
        plan=None,
        status=str(transaction.get("status") or "blocked"),
        verification_status=str(transaction.get("verificationStatus") or "not_verified"),
        backend=str(transaction.get("backend") or "mock_plugin_like"),
        target_layer=str(transaction.get("targetLayer") or "MOCK_PREVIEW_MEMORY"),
        saved_current_dwg=False,
        created_handles=[str(item) for item in transaction.get("createdHandles", [])],
        readback_entities=[],
        evidence_package_ref=str(dict(transaction.get("ledgerRefs") or {}).get("tool.requested") or ""),
        blocking_reasons=[str(transaction.get("blockedReason"))] if transaction.get("blockedReason") else [],
        missing_evidence=[],
        cad_geometry_verified=False,
        artifacts={"createdHandlesRef": str(transaction.get("createdHandlesRef") or "")},
    )
    result["taskId"] = str(transaction.get("taskId") or "phase12.mock-plugin-transaction")
    result["toolCallId"] = "cad-agent-harness.mock-plugin-transaction"
    result["cadWritesAttempted"] = False
    result["proofStatus"] = str(transaction.get("proofStatus") or "")
    result["rollbackRequired"] = bool(transaction.get("rollbackRequired", False))
    result["rollbackStatus"] = str(transaction.get("rollbackStatus") or "")
    result["committedPreview"] = bool(transaction.get("committedPreview", False))
    result["blockedReason"] = str(transaction.get("blockedReason") or "")
    result["retryable"] = bool(transaction.get("retryable", False))
    result["documentState"] = str(transaction.get("documentState") or "")
    result["transaction"] = transaction
    result["ledgerRefs"] = dict(transaction.get("ledgerRefs") or {})
    result["allowedEffects"] = [str(item) for item in transaction.get("allowedEffects", [])]
    result["forbiddenEffects"] = [str(item) for item in transaction.get("forbiddenEffects", [])]
    result["completionBoundary"] = str(transaction.get("completionBoundary") or "")
    result["notEvidenceFor"] = [str(item) for item in transaction.get("notEvidenceFor", [])]
    return result


def _native_thin_backend_result(
    *,
    mode: str,
    cad_plan: dict[str, Any] | None = None,
    output_dir: str | Path | None = None,
    scope_receipt_path: str | Path | None = None,
    launch_packet_path: str | Path | None = None,
    authorization_gate_path: str | Path | None = None,
    execution_receipt_path: str | Path | None = None,
    readiness_packet_path: str | Path | None = None,
    scope_confirmed: bool = False,
    confirmation_statement: str = "",
) -> dict[str, Any]:
    from core.contracts.native_thin_backend import (
        build_native_thin_backend_authorization_gate,
        build_native_thin_backend_execution_receipt,
        build_native_thin_backend_launch_packet,
        build_native_thin_backend_live_spike_execution_gate,
        build_native_thin_backend_readiness_packet,
        build_native_thin_backend_scope_receipt,
        execute_native_thin_backend_skeleton,
    )

    normalized_mode = str(mode or "contract_ready").strip().replace("-", "_")
    if normalized_mode == "scope_receipt":
        native_result = build_native_thin_backend_scope_receipt(
            cad_plan=cad_plan,
            output_dir=output_dir,
            scope_confirmed=scope_confirmed,
            confirmation_statement=confirmation_statement,
            backend_identity="native-thin-skeleton",
            readback_plan={"required": True, "strategy": "created_handles_bbox_props"},
            rollback_plan={"required": True, "strategy": "rollback_batch"},
            no_save_guard={"required": True, "saveAllowed": False},
        )
    elif normalized_mode in {"preflight", "launch_packet"}:
        native_result = build_native_thin_backend_launch_packet(
            scope_receipt_path=scope_receipt_path,
            output_dir=output_dir,
        )
    elif normalized_mode in {"authorization", "authorization_gate"}:
        native_result = build_native_thin_backend_authorization_gate(
            launch_packet_path=launch_packet_path,
            output_dir=output_dir,
        )
    elif normalized_mode in {"execution_receipt", "execution"}:
        native_result = build_native_thin_backend_execution_receipt(
            authorization_gate_path=authorization_gate_path,
            output_dir=output_dir,
        )
    elif normalized_mode in {"readiness", "readiness_packet", "authorization_request", "operator_authorization_request"}:
        native_result = build_native_thin_backend_readiness_packet(
            execution_receipt_path=execution_receipt_path,
            output_dir=output_dir,
        )
    elif normalized_mode in {"live_spike_gate", "live_spike", "execution_gate", "p13e"}:
        native_result = build_native_thin_backend_live_spike_execution_gate(
            readiness_packet_path=readiness_packet_path,
            output_dir=output_dir,
        )
    else:
        native_result = execute_native_thin_backend_skeleton(mode=mode)
    result = _base_result(
        command="native-thin-backend",
        plan=None,
        status=str(native_result.get("status") or "blocked"),
        verification_status=str(native_result.get("verificationStatus") or "not_verified"),
        backend=str(native_result.get("backend") or "native_thin_skeleton"),
        target_layer=str(native_result.get("targetLayer") or PREVIEW_LAYER),
        saved_current_dwg=False,
        created_handles=[str(item) for item in native_result.get("createdHandles", [])],
        readback_entities=[],
        evidence_package_ref=str(dict(native_result.get("ledgerRefs") or {}).get("tool.requested") or ""),
        blocking_reasons=[str(native_result.get("blockedReason"))] if native_result.get("blockedReason") else [],
        missing_evidence=[],
        cad_geometry_verified=False,
        artifacts={
            "createdHandlesRef": str(native_result.get("createdHandlesRef") or ""),
            "nativeThinScopeReceipt": str(dict(native_result.get("artifacts") or {}).get("nativeThinScopeReceipt") or ""),
            "nativeThinLaunchPacket": str(dict(native_result.get("artifacts") or {}).get("nativeThinLaunchPacket") or ""),
            "nativeThinAuthorizationGate": str(
                dict(native_result.get("artifacts") or {}).get("nativeThinAuthorizationGate") or ""
            ),
            "nativeThinExecutionReceipt": str(
                dict(native_result.get("artifacts") or {}).get("nativeThinExecutionReceipt") or ""
            ),
            "nativeThinReadinessPacket": str(
                dict(native_result.get("artifacts") or {}).get("nativeThinReadinessPacket") or ""
            ),
            "nativeThinOperatorAuthorizationRequest": str(
                dict(native_result.get("artifacts") or {}).get("nativeThinOperatorAuthorizationRequest") or ""
            ),
            "nativeThinLiveSpikeExecutionGate": str(
                dict(native_result.get("artifacts") or {}).get("nativeThinLiveSpikeExecutionGate") or ""
            ),
        },
    )
    result["taskId"] = str(native_result.get("taskId") or "phase13.native-thin-backend")
    result["toolCallId"] = "cad-agent-harness.native-thin-backend"
    result["cadWritesAttempted"] = False
    result["proofStatus"] = str(native_result.get("proofStatus") or "")
    result["rollbackRequired"] = bool(native_result.get("rollbackRequired", False))
    result["rollbackStatus"] = str(native_result.get("rollbackStatus") or "")
    result["committedPreview"] = bool(native_result.get("committedPreview", False))
    result["blockedReason"] = str(native_result.get("blockedReason") or "")
    result["retryable"] = bool(native_result.get("retryable", False))
    result["documentState"] = str(native_result.get("documentState") or "")
    result["nativePluginInvoked"] = bool(native_result.get("nativePluginInvoked", False))
    result["noSaveAudit"] = dict(native_result.get("noSaveAudit") or {})
    result["rollbackProof"] = dict(native_result.get("rollbackProof") or {})
    result["scopeConfirmed"] = bool(native_result.get("scopeConfirmed", False))
    result["launchPacketReady"] = bool(native_result.get("launchPacketReady", False))
    result["authorizationStatus"] = str(native_result.get("authorizationStatus") or "")
    result["closeoutStatus"] = str(native_result.get("closeoutStatus") or "")
    result["operatorAuthorizationStatus"] = str(native_result.get("operatorAuthorizationStatus") or "")
    result["receiptStatus"] = str(native_result.get("receiptStatus") or "")
    result["authorizationRequestStatus"] = str(native_result.get("authorizationRequestStatus") or "")
    result["executionStarted"] = bool(native_result.get("executionStarted", False))
    result["launchPacketHash"] = str(native_result.get("launchPacketHash") or "")
    result["scopeHash"] = str(native_result.get("scopeHash") or "")
    result["authorizationReceiptHash"] = str(native_result.get("authorizationReceiptHash") or "")
    result["executionReceiptHash"] = str(native_result.get("executionReceiptHash") or "")
    result["readinessPacketHash"] = str(native_result.get("readinessPacketHash") or "")
    result["liveExecutionAuthorized"] = bool(native_result.get("liveExecutionAuthorized", False))
    result["operatorLiveSpikeAuthorized"] = bool(native_result.get("operatorLiveSpikeAuthorized", False))
    result["realLiveSpikeAuthorizationRequired"] = bool(
        native_result.get("realLiveSpikeAuthorizationRequired", False)
    )
    result["readbackPlan"] = dict(native_result.get("readbackPlan") or {})
    result["rollbackPlan"] = dict(native_result.get("rollbackPlan") or {})
    result["noSaveGuard"] = dict(native_result.get("noSaveGuard") or {})
    result["operatorAuthorizationRequest"] = dict(native_result.get("operatorAuthorizationRequest") or {})
    result["operatorAuthorization"] = dict(native_result.get("operatorAuthorization") or {})
    result["environmentReadiness"] = dict(native_result.get("environmentReadiness") or {})
    result["bboxLayerEntityAudit"] = dict(native_result.get("bboxLayerEntityAudit") or {})
    result["createdHandlesReadback"] = dict(native_result.get("createdHandlesReadback") or {})
    result["nativeThinBackend"] = native_result
    result["ledgerRefs"] = dict(native_result.get("ledgerRefs") or {})
    result["allowedEffects"] = [str(item) for item in native_result.get("allowedEffects", [])]
    result["forbiddenEffects"] = [str(item) for item in native_result.get("forbiddenEffects", [])]
    result["completionBoundary"] = str(native_result.get("completionBoundary") or "")
    result["notEvidenceFor"] = [str(item) for item in native_result.get("notEvidenceFor", [])]
    return result


def _native_thin_live_spike_result(
    *,
    output_dir: str | Path | None = None,
    readiness_packet_path: str | Path | None = None,
    operator_authorization: dict[str, Any] | None = None,
    environment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from core.contracts.native_thin_backend import execute_native_thin_live_spike

    native_result = execute_native_thin_live_spike(
        readiness_packet_path=readiness_packet_path,
        operator_authorization=operator_authorization,
        environment=environment,
        output_dir=output_dir,
    )
    readback = dict(native_result.get("createdHandlesReadback") or {})
    readback_entities = [dict(item) for item in readback.get("entities", []) if isinstance(item, dict)]
    artifacts = dict(native_result.get("artifacts") or {})
    result = _base_result(
        command="native-thin-live-spike",
        plan=None,
        status=str(native_result.get("status") or "blocked"),
        verification_status=str(native_result.get("verificationStatus") or "not_verified"),
        backend=str(native_result.get("backend") or "native_thin_live_backend"),
        target_layer=str(native_result.get("targetLayer") or PREVIEW_LAYER),
        saved_current_dwg=bool(native_result.get("savedCurrentDwg", False)),
        created_handles=[str(item) for item in native_result.get("createdHandles", [])],
        readback_entities=readback_entities,
        evidence_package_ref=str(dict(native_result.get("ledgerRefs") or {}).get("tool.requested") or ""),
        blocking_reasons=[str(item) for item in native_result.get("blockingReasons", [])],
        missing_evidence=[str(item) for item in native_result.get("missingEvidence", [])],
        cad_geometry_verified=bool(native_result.get("cadGeometryVerified", False)),
        artifacts={
            "createdHandlesRef": str(native_result.get("createdHandlesRef") or ""),
            "nativeThinLiveSpikeGate": str(artifacts.get("nativeThinLiveSpikeExecutionGate") or ""),
            "nativeThinLiveSpikeResult": str(artifacts.get("nativeThinLiveSpikeResult") or ""),
            "nativePluginReport": str(artifacts.get("nativePluginReport") or ""),
            "coreConsoleLog": str(artifacts.get("coreConsoleLog") or ""),
        },
    )
    result["taskId"] = str(native_result.get("taskId") or "phase13f.native-thin-live-spike")
    result["toolCallId"] = "cad-agent-harness.native-thin-live-spike"
    result["cadWritesAttempted"] = bool(native_result.get("cadWritesAttempted", False))
    result["nativePluginInvoked"] = bool(native_result.get("nativePluginInvoked", False))
    result["executionStarted"] = bool(native_result.get("executionStarted", False))
    result["proofStatus"] = str(native_result.get("proofStatus") or "")
    result["closeoutStatus"] = str(native_result.get("closeoutStatus") or "")
    result["rollbackRequired"] = bool(native_result.get("rollbackRequired", False))
    result["rollbackStatus"] = str(native_result.get("rollbackStatus") or "")
    result["committedPreview"] = bool(native_result.get("committedPreview", False))
    result["documentState"] = str(native_result.get("documentState") or "")
    result["noSaveAudit"] = dict(native_result.get("noSaveAudit") or {})
    result["rollbackProof"] = dict(native_result.get("rollbackProof") or {})
    result["bboxLayerEntityAudit"] = dict(native_result.get("bboxLayerEntityAudit") or {})
    result["createdHandlesReadback"] = readback
    result["readinessPacketHash"] = str(native_result.get("readinessPacketHash") or "")
    result["launchPacketHash"] = str(native_result.get("launchPacketHash") or "")
    result["authorizationReceiptHash"] = str(native_result.get("authorizationReceiptHash") or "")
    result["executionReceiptHash"] = str(native_result.get("executionReceiptHash") or "")
    result["operatorAuthorization"] = dict(native_result.get("operatorAuthorization") or {})
    result["environmentReadiness"] = dict(native_result.get("environmentReadiness") or {})
    result["nativeThinBackend"] = native_result
    result["ledgerRefs"] = dict(native_result.get("ledgerRefs") or {})
    result["allowedEffects"] = [str(item) for item in native_result.get("allowedEffects", [])]
    result["forbiddenEffects"] = [str(item) for item in native_result.get("forbiddenEffects", [])]
    result["completionBoundary"] = str(native_result.get("completionBoundary") or "")
    result["notEvidenceFor"] = [str(item) for item in native_result.get("notEvidenceFor", [])]
    return result


def _engineering_kernel_diff_result(
    *,
    cad_plan: dict[str, Any],
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    from core.contracts.engineering_kernel import execute_engineering_kernel_diff

    diff = execute_engineering_kernel_diff(cad_plan=cad_plan, output_dir=output_dir)
    artifacts = dict(diff.get("artifacts") or {})
    result = _base_result(
        command="engineering-kernel-diff",
        plan=cad_plan,
        status=str(diff.get("status") or "blocked"),
        verification_status=str(diff.get("verificationStatus") or "not_verified"),
        backend=str(diff.get("backend") or "engineering_kernel"),
        target_layer=str(diff.get("targetLayer") or PREVIEW_LAYER),
        saved_current_dwg=False,
        created_handles=[],
        readback_entities=[],
        evidence_package_ref=str(artifacts.get("engineeringKernelDiffPackage") or ""),
        blocking_reasons=[str(item) for item in diff.get("blockingReasons", [])],
        missing_evidence=[str(item) for item in diff.get("missingEvidence", [])],
        cad_geometry_verified=False,
        artifacts={
            "engineeringKernelGraphs": str(artifacts.get("engineeringKernelGraphs") or ""),
            "engineeringKernelDiffPackage": str(artifacts.get("engineeringKernelDiffPackage") or ""),
        },
    )
    result["taskId"] = str(diff.get("taskId") or "phase14.engineering-kernel.diff-package")
    result["toolCallId"] = "cad-agent-harness.engineering-kernel-diff"
    result["cadWritesAttempted"] = False
    result["sourceCadWritesAttempted"] = bool(diff.get("sourceCadWritesAttempted", False))
    result["nativePluginInvoked"] = False
    result["comparisonStatus"] = str(diff.get("comparisonStatus") or "")
    result["evidenceCompleteness"] = str(diff.get("evidenceCompleteness") or "")
    result["verifiedBackends"] = [str(item) for item in diff.get("verifiedBackends", [])]
    result["notRunBackends"] = [str(item) for item in diff.get("notRunBackends", [])]
    result["backendCandidateDocs"] = dict(diff.get("backendCandidateDocs") or {})
    result["geometryDelta"] = dict(diff.get("geometryDelta") or {})
    result["styleDelta"] = dict(diff.get("styleDelta") or {})
    result["semanticDelta"] = dict(diff.get("semanticDelta") or {})
    result["engineeringKernel"] = diff
    result["allowedEffects"] = [str(item) for item in diff.get("allowedEffects", [])]
    result["forbiddenEffects"] = [str(item) for item in diff.get("forbiddenEffects", [])]
    result["completionBoundary"] = str(diff.get("completionBoundary") or "")
    result["notEvidenceFor"] = [str(item) for item in diff.get("notEvidenceFor", [])]
    return result


def _from_phase9_report(
    *,
    command: str,
    report: dict[str, Any],
    readback_entities: list[dict[str, Any]],
    backend: str,
) -> dict[str, Any]:
    artifacts = dict(report.get("artifacts") if isinstance(report.get("artifacts"), dict) else {})
    return _base_result(
        command=command,
        plan=None,
        status=str(report.get("status") or "not_verified"),
        verification_status=str(report.get("verificationStatus") or "not_verified"),
        backend=backend,
        target_layer=str(report.get("targetLayer") or PREVIEW_LAYER),
        saved_current_dwg=bool(report.get("savedCurrentDwg", False)),
        created_handles=[str(item) for item in report.get("createdHandles", [])],
        readback_entities=readback_entities,
        evidence_package_ref=str(artifacts.get("evidencePackage") or ""),
        blocking_reasons=[str(item) for item in report.get("blockingReasons", [])],
        missing_evidence=[str(item) for item in report.get("missingEvidence", [])],
        cad_geometry_verified=bool(report.get("cadGeometryVerified", False)),
        artifacts=artifacts,
    )


def _base_result(
    *,
    command: str,
    plan: dict[str, Any] | None,
    status: str,
    backend: str,
    verification_status: str = "not_verified",
    target_layer: str | None = None,
    saved_current_dwg: bool = False,
    created_handles: list[str] | None = None,
    readback_entities: list[dict[str, Any]] | None = None,
    evidence_package_ref: str = "",
    blocking_reasons: list[str] | None = None,
    missing_evidence: list[str] | None = None,
    cad_geometry_verified: bool = False,
    validation_errors: list[str] | None = None,
    artifacts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    layer = target_layer or _plan_layer(plan) or PREVIEW_LAYER
    scope = build_phase9_preview_scope_record(plan or phase9_default_single_preview_plan())
    return {
        "schemaVersion": SCHEMA_VERSION,
        "command": command,
        "status": status,
        "verificationStatus": verification_status,
        "taskId": "phase9-single-preview-task",
        "toolCallId": f"cad-agent-harness.{command}",
        "backend": backend,
        "targetLayer": layer,
        "savedCurrentDwg": saved_current_dwg,
        "cadGeometryVerified": cad_geometry_verified,
        "createdHandles": list(created_handles or []),
        "readbackEntities": list(readback_entities or []),
        "evidencePackageRef": evidence_package_ref,
        "blockingReasons": list(blocking_reasons or []),
        "missingEvidence": list(missing_evidence or []),
        "validationErrors": list(validation_errors or []),
        "safety": dict(SAFE_DEFAULTS),
        "allowedEffects": list(scope.get("allowedEffects", [])),
        "forbiddenEffects": list(scope.get("forbiddenEffects", [])),
        "artifacts": dict(artifacts or {}),
    }


def _load_plan(
    *,
    cad_plan: dict[str, Any] | None,
    plan_path: str | Path | None,
) -> dict[str, Any]:
    if cad_plan is not None:
        return dict(cad_plan)
    if plan_path:
        return dict(load_json(Path(plan_path)))
    return phase9_default_single_preview_plan()


def _load_json_dict(*, payload: dict[str, Any] | None, path: str | Path | None) -> dict[str, Any] | None:
    if payload is not None:
        return dict(payload)
    if path:
        return dict(load_json(Path(path)))
    return None


def _load_scope(
    *,
    scope: dict[str, Any] | None,
    scope_path: str | Path | None,
    fallback_plan: dict[str, Any],
) -> dict[str, Any]:
    if scope is not None:
        return dict(scope)
    if scope_path:
        return dict(load_json(Path(scope_path)))
    return {
        "scopeConfirmed": False,
        "backend": DEFAULT_LIVE_BACKEND,
        "runCount": 0,
        "cadPlans": [dict(fallback_plan)],
    }


def _normalize_command(command: str) -> str:
    normalized = str(command).strip()
    if normalized not in SUPPORTED_COMMANDS:
        raise ValueError(f"unsupported harness command: {command}")
    return normalized


def _phase9_backend(backend: str) -> str:
    return BACKEND_ALIASES.get(str(backend), str(backend))


def _driver_factory_for_backend(backend: str):
    normalized = _phase9_backend(backend)
    if normalized == "fake_driver_preflight":
        from core.verification.fake_cad_driver import FakeCadDriver

        return FakeCadDriver
    if normalized == "cad_session_host":
        return _cad_session_host_driver_factory
    return None


def _cad_session_host_driver_factory():
    host_url = str(os.environ.get("CAD_SESSION_HOST_URL") or "").strip()
    token = str(os.environ.get("CAD_SESSION_TOKEN") or "").strip()
    if not host_url or not token:
        raise RuntimeError(
            "CAD_SESSION_HOST_URL and CAD_SESSION_TOKEN are required for cad-session-host backend."
        )
    timeout_seconds = float(os.environ.get("CAD_SESSION_HOST_TIMEOUT_SECONDS", "30"))
    from core.cad_io.cad_session_host import CadSessionHostClient

    return CadSessionHostClient(
        base_url=host_url,
        token=token,
        timeout_seconds=timeout_seconds,
    )


def _plan_layer(plan: dict[str, Any] | None) -> str:
    if not isinstance(plan, dict):
        return ""
    drawing = plan.get("drawing")
    if not isinstance(drawing, dict):
        return ""
    return str(drawing.get("layer") or "")


def _require_run_dir(run_dir: str | Path | None) -> Path:
    if run_dir is None:
        raise ValueError("--run-dir or --output-dir is required for this command")
    root = Path(run_dir)
    if not root.is_dir():
        raise ValueError(f"run dir does not exist: {root}")
    return root


def _read_report(run_dir: Path) -> dict[str, Any]:
    report_path = run_dir / "phase9_preview_report.json"
    if not report_path.is_file():
        raise ValueError(f"phase9 report missing: {report_path}")
    report = dict(_read_json(report_path))
    artifacts = dict(report.get("artifacts") if isinstance(report.get("artifacts"), dict) else {})
    artifacts.setdefault("report", str(report_path))
    report["artifacts"] = artifacts
    return report


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
