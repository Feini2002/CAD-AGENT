"""Phase 10 focused harness rehearsal planning contract.

P10A is intentionally non-executing: it materializes a confirmed rehearsal
scope and deterministic preview run plan, but does not connect to CAD or write
preview geometry. Actual CAD writes remain a later, scoped rehearsal step.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable

from core.path_safety import find_project_root, resolve_under_project_output
from core.plan_engine.validate_plan import validate_plan
from core.safety.policy import PREVIEW_LAYER
from core.contracts.phase9_exit_gate import evaluate_phase9_exit_gate


PHASE10_REHEARSAL_SCOPE_PROPOSAL_SCHEMA = "phase10-rehearsal-scope-proposal/v1"
PHASE10_REHEARSAL_PLAN_RESULT_SCHEMA = "phase10-rehearsal-plan-result/v1"
PHASE10_REHEARSAL_RESULT_SCHEMA = "phase10-rehearsal-result/v1"
PHASE10_REHEARSAL_EXECUTION_SCHEMA = "phase10-rehearsal-execution/v1"
PHASE10_REHEARSAL_LAUNCH_PACKET_SCHEMA = "phase10-rehearsal-launch-packet/v1"
PHASE10_REHEARSAL_CLOSEOUT_SCHEMA = "phase10-rehearsal-closeout/v1"
PHASE10_REHEARSAL_SCOPE_RECEIPT_SCHEMA = "phase10-rehearsal-scope-receipt/v1"
PHASE10_REHEARSAL_SCOPE_SCHEMA = "phase10-rehearsal-scope/v1"
PHASE10_REHEARSAL_PLAN_SCHEMA = "phase10-rehearsal-plan/v1"
PHASE10_REHEARSAL_DIFF_SCHEMA = "phase10-rehearsal-diff-summary/v1"
PHASE10_REHEARSAL_FAILURE_LEDGER_SCHEMA = "phase10-rehearsal-failure-ledger/v1"
PHASE10_PACKAGE_ID = "phase10.focused-harness-rehearsal"
PHASE10_TASK_ID = "phase10.focused-harness-rehearsal.plan"
PHASE10_RESULT_TASK_ID = "phase10.focused-harness-rehearsal.result"
PHASE10_EXECUTION_TASK_ID = "phase10.focused-harness-rehearsal.execute"
PHASE10_LAUNCH_TASK_ID = "phase10.focused-harness-rehearsal.launch-preflight"
PHASE10_CLOSEOUT_TASK_ID = "phase10.focused-harness-rehearsal.closeout"
PHASE10_SCOPE_RECEIPT_TASK_ID = "phase10.focused-harness-rehearsal.scope-receipt"
PHASE10_SCOPE_PROPOSAL_TASK_ID = "phase10.focused-harness-rehearsal.scope-proposal"
DEFAULT_PHASE10_BACKEND = "cad-session-host"
MIN_REHEARSAL_RUN_COUNT = 2
PHASE10_REAL_BACKENDS = {"cad-session-host", "cad_session_host"}
PreviewExecutor = Callable[..., Any]

PHASE10_FORBIDDEN_EFFECTS = (
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

PHASE10_PLANNED_RUN_EFFECTS = (
    "cad_plan_validate",
    "cad_plan_dry_run",
    "cad_preview_write",
    "created_handles_readback",
    "evidence_package_write",
)


def build_phase10_rehearsal_scope_proposal(
    *,
    phase9_exit_run_dir: str | Path,
    output_dir: str | Path,
    run_count: int = MIN_REHEARSAL_RUN_COUNT,
    backend: str = DEFAULT_PHASE10_BACKEND,
    object_family: str | None = None,
    capability: str | None = None,
    scope_id: str | None = None,
) -> dict[str, Any]:
    """Derive a non-confirmed P10 scope candidate from ready Phase 9 evidence."""

    project_root = find_project_root(Path.cwd())
    resolved_output_dir = resolve_under_project_output(
        project_root,
        Path(output_dir),
        label="phase10 rehearsal scope proposal output_dir",
    )
    resolved_output_dir.mkdir(parents=True, exist_ok=True)

    blockers: list[str] = []
    gate: dict[str, Any] = {}
    report: dict[str, Any] = {}
    cad_plan: dict[str, Any] = {}
    phase9_dir_text = str(phase9_exit_run_dir or "").strip()
    resolved_phase9_dir: Path | None = None
    report_path: Path | None = None
    cad_plan_path: Path | None = None

    if not phase9_dir_text:
        blockers.append("phase10_scope_proposal_phase9_exit_missing")
    else:
        try:
            resolved_phase9_dir = resolve_under_project_output(
                project_root,
                Path(phase9_dir_text),
                label="phase10 rehearsal scope proposal phase9_exit_run_dir",
            )
        except (OSError, ValueError):
            blockers.append("phase10_scope_proposal_phase9_exit_invalid")

    if resolved_phase9_dir is not None:
        report_path = resolved_phase9_dir / "phase9_preview_report.json"
        try:
            gate = evaluate_phase9_exit_gate(run_dir=resolved_phase9_dir)
        except (OSError, ValueError, json.JSONDecodeError):
            blockers.append("phase10_scope_proposal_phase9_exit_invalid")
        else:
            if gate.get("phase10Allowed") is not True:
                blockers.append("phase10_scope_proposal_phase9_exit_not_ready")

        if report_path.is_file():
            try:
                report = _read_json(report_path)
            except (OSError, ValueError, json.JSONDecodeError):
                blockers.append("phase10_scope_proposal_phase9_report_invalid")
        else:
            blockers.append("phase10_scope_proposal_phase9_report_missing")

    source_artifacts = report.get("artifacts") if isinstance(report.get("artifacts"), dict) else {}
    cad_plan_ref = str(source_artifacts.get("cadPlan") or "")
    if not cad_plan_ref and resolved_phase9_dir is not None:
        cad_plan_ref = str(resolved_phase9_dir / "phase9_single_preview_cad_plan.json")
    if cad_plan_ref:
        try:
            cad_plan_path = resolve_under_project_output(
                project_root,
                Path(cad_plan_ref),
                label="phase10 rehearsal scope proposal cad_plan",
            )
        except (OSError, ValueError):
            blockers.append("phase10_scope_proposal_cad_plan_invalid")
        else:
            if cad_plan_path.is_file():
                try:
                    cad_plan = _read_json(cad_plan_path)
                except (OSError, ValueError, json.JSONDecodeError):
                    blockers.append("phase10_scope_proposal_cad_plan_invalid")
            else:
                blockers.append("phase10_scope_proposal_cad_plan_missing")
    else:
        blockers.append("phase10_scope_proposal_cad_plan_missing")

    obj = cad_plan.get("object") if isinstance(cad_plan.get("object"), dict) else {}
    drawing = cad_plan.get("drawing") if isinstance(cad_plan.get("drawing"), dict) else {}
    object_family_value = str(object_family or obj.get("type") or "").strip()
    capability_value = str(capability or _default_scope_capability(object_family_value)).strip()
    requested_run_count = _int_or_zero(run_count)
    backend_value = str(backend or "").strip()
    scope_id_value = str(scope_id or _default_scope_id(object_family_value, capability_value)).strip()

    if not object_family_value and not capability_value:
        blockers.append("phase10_scope_proposal_target_missing")
    if backend_value not in PHASE10_REAL_BACKENDS:
        blockers.append("phase10_scope_proposal_real_backend_required")
    if requested_run_count < MIN_REHEARSAL_RUN_COUNT:
        blockers.append("phase10_scope_proposal_repetition_count_too_low")
    if cad_plan:
        if str(drawing.get("layer") or "") != PREVIEW_LAYER:
            blockers.append("phase10_scope_proposal_non_preview_layer_forbidden")
        if validate_plan(cad_plan):
            blockers.append("phase10_scope_proposal_cad_plan_invalid")

    blocking_reasons = _unique(blockers)
    status = "ready" if not blocking_reasons else "blocked"
    proposal_path = resolved_output_dir / "phase10_rehearsal_scope_proposal.json"
    candidate_scope = {
        "scopeId": scope_id_value,
        "scopeConfirmed": False,
        "objectFamily": object_family_value,
        "capability": capability_value,
        "backend": backend_value,
        "runCount": requested_run_count,
        "phase9ExitRunDir": str(resolved_phase9_dir or phase9_dir_text),
        "cadPlans": [cad_plan] if cad_plan else [],
    }
    proposal = {
        "schemaVersion": PHASE10_REHEARSAL_SCOPE_PROPOSAL_SCHEMA,
        "phase": "Phase 10",
        "packageId": PHASE10_PACKAGE_ID,
        "taskId": PHASE10_SCOPE_PROPOSAL_TASK_ID,
        "status": status,
        "verificationStatus": "not_verified",
        "proposalReady": status == "ready",
        "scopeConfirmed": False,
        "liveRunsConfirmed": False,
        "cadWritesAttempted": False,
        "phase9ExitRunDir": str(resolved_phase9_dir or phase9_dir_text),
        "phase9ExitGate": gate,
        "outputDir": str(resolved_output_dir),
        "proposalPath": str(proposal_path),
        "sourceArtifacts": {
            "phase9Report": str(report_path) if report_path else "",
            "cadPlan": str(cad_plan_path) if cad_plan_path else "",
        },
        "candidateScope": candidate_scope,
        "confirmationTemplate": (
            "Confirm this Phase 10 rehearsal scope explicitly before creating a "
            "scope receipt or running live CAD previews."
        ),
        "blockingReasons": blocking_reasons,
        "missingEvidence": [] if status == "ready" else ["phase10_scope_proposal_source_evidence"],
        "allowedEffects": ["phase10_rehearsal_scope_proposal_write"],
        "nextAllowedEffects": ["operator_scope_confirmation", "phase10_rehearsal_plan_write_after_confirmation"]
        if status == "ready"
        else [],
        "forbiddenEffects": list(PHASE10_FORBIDDEN_EFFECTS),
        "requiredOperatorActions": [
            "review_phase10_scope_candidate",
            "explicitly_confirm_scope_before_receipt",
            "write_rehearsal_plan_with_scopeConfirmed_true",
            "write_matching_phase10_scope_receipt",
        ],
        "completionBoundary": "scope_proposal_is_not_operator_confirmation_or_cad_execution",
        "notEvidenceFor": [
            "phase10_scope_confirmation",
            "phase10_live_preview_execution",
            "phase10_closeout",
            "training_resume",
            "table_c_progress",
            "plugin_readiness",
        ],
    }
    _write_json(proposal_path, proposal)
    return proposal


def prepare_phase10_rehearsal_plan(
    *,
    scope: dict[str, Any],
    output_dir: str | Path,
) -> dict[str, Any]:
    """Materialize a P10 rehearsal scope and run plan without executing CAD."""

    project_root = find_project_root(Path.cwd())
    resolved_output_dir = resolve_under_project_output(
        project_root,
        Path(output_dir),
        label="phase10 rehearsal output_dir",
    )
    resolved_output_dir.mkdir(parents=True, exist_ok=True)

    normalized_scope = _normalize_scope(scope)
    blockers = _scope_blockers(normalized_scope)
    status = "ready" if not blockers else "blocked"
    run_specs = [] if blockers else _build_run_specs(normalized_scope, resolved_output_dir)

    scope_payload = {
        "schemaVersion": PHASE10_REHEARSAL_SCOPE_SCHEMA,
        "phase": "Phase 10",
        "packageId": PHASE10_PACKAGE_ID,
        "scopeId": normalized_scope["scopeId"],
        "scopeConfirmed": normalized_scope["scopeConfirmed"],
        "objectFamily": normalized_scope["objectFamily"],
        "capability": normalized_scope["capability"],
        "backend": normalized_scope["backend"],
        "runCount": normalized_scope["runCount"],
        "phase9ExitRunDir": normalized_scope["phase9ExitRunDir"],
        "targetLayer": PREVIEW_LAYER,
        "cadPlans": normalized_scope["cadPlans"],
        "safety": _safety_policy(),
    }
    plan_payload = {
        "schemaVersion": PHASE10_REHEARSAL_PLAN_SCHEMA,
        "phase": "Phase 10",
        "packageId": PHASE10_PACKAGE_ID,
        "taskId": PHASE10_TASK_ID,
        "status": status,
        "scopeId": normalized_scope["scopeId"],
        "backend": normalized_scope["backend"],
        "runCount": normalized_scope["runCount"],
        "phase9ExitRunDir": normalized_scope["phase9ExitRunDir"],
        "cadWritesAttempted": False,
        "runSpecs": run_specs,
        "blockingReasons": blockers,
        "allowedEffects": ["phase10_rehearsal_plan_write"],
        "plannedRunAllowedEffects": list(PHASE10_PLANNED_RUN_EFFECTS),
        "forbiddenEffects": list(PHASE10_FORBIDDEN_EFFECTS),
        "safety": _safety_policy(),
        "completionBoundary": "rehearsal_plan_is_not_cad_execution_or_training_resume",
        "notEvidenceFor": ["training_resume", "table_c_progress", "plugin_readiness"],
    }

    scope_path = resolved_output_dir / "phase10_rehearsal_scope.json"
    plan_path = resolved_output_dir / "phase10_rehearsal_plan.json"
    _write_json(scope_path, scope_payload)
    _write_json(plan_path, plan_payload)

    return {
        "schemaVersion": PHASE10_REHEARSAL_PLAN_RESULT_SCHEMA,
        "phase": "Phase 10",
        "packageId": PHASE10_PACKAGE_ID,
        "taskId": PHASE10_TASK_ID,
        "status": status,
        "backend": normalized_scope["backend"],
        "scopeId": normalized_scope["scopeId"],
        "outputDir": str(resolved_output_dir),
        "scopePath": str(scope_path),
        "planPath": str(plan_path),
        "cadWritesAttempted": False,
        "runSpecs": run_specs,
        "blockingReasons": blockers,
        "allowedEffects": list(plan_payload["allowedEffects"]),
        "plannedRunAllowedEffects": list(plan_payload["plannedRunAllowedEffects"]),
        "forbiddenEffects": list(PHASE10_FORBIDDEN_EFFECTS),
        "completionBoundary": plan_payload["completionBoundary"],
        "notEvidenceFor": list(plan_payload["notEvidenceFor"]),
    }


def build_phase10_rehearsal_scope_receipt(
    *,
    plan_path: str | Path,
    output_dir: str | Path | None = None,
    live_runs_confirmed: bool = False,
    confirmation_statement: str = "",
) -> dict[str, Any]:
    """Record explicit operator scope confirmation without executing CAD."""

    project_root = find_project_root(Path.cwd())
    resolved_plan_path = resolve_under_project_output(
        project_root,
        Path(plan_path),
        label="phase10 rehearsal scope receipt plan_path",
    )
    plan = _read_json(resolved_plan_path)
    resolved_output_dir = resolve_under_project_output(
        project_root,
        Path(output_dir) if output_dir is not None else resolved_plan_path.parent,
        label="phase10 rehearsal scope receipt output_dir",
    )
    resolved_output_dir.mkdir(parents=True, exist_ok=True)

    run_specs, blockers = _execution_run_specs(project_root=project_root, plan=plan)
    statement = str(confirmation_statement or "").strip()
    if live_runs_confirmed is not True:
        blockers.append("phase10_scope_receipt_live_runs_not_confirmed")
    if not statement:
        blockers.append("phase10_scope_receipt_confirmation_missing")

    blocking_reasons = _unique(blockers)
    status = "ready" if not blocking_reasons else "blocked"
    receipt_path = resolved_output_dir / "phase10_rehearsal_scope_receipt.json"
    receipt = {
        "schemaVersion": PHASE10_REHEARSAL_SCOPE_RECEIPT_SCHEMA,
        "phase": "Phase 10",
        "packageId": PHASE10_PACKAGE_ID,
        "taskId": PHASE10_SCOPE_RECEIPT_TASK_ID,
        "status": status,
        "verificationStatus": "not_verified",
        "scopeConfirmed": bool(live_runs_confirmed is True and statement),
        "liveRunsConfirmed": bool(live_runs_confirmed),
        "cadWritesAttempted": False,
        "planPath": str(resolved_plan_path),
        "planHash": _json_fingerprint(plan),
        "outputDir": str(resolved_output_dir),
        "receiptPath": str(receipt_path),
        "scopeId": str(plan.get("scopeId") or ""),
        "backend": str(plan.get("backend") or ""),
        "runCount": _int_or_zero(plan.get("runCount")),
        "plannedRunCount": len(run_specs),
        "targetLayer": PREVIEW_LAYER,
        "runSpecs": run_specs,
        "confirmationStatement": statement,
        "blockingReasons": blocking_reasons,
        "missingEvidence": ["phase10_scope_confirmation_receipt"] if status != "ready" else [],
        "allowedEffects": ["phase10_rehearsal_scope_receipt_write"],
        "nextAllowedEffects": ["phase10_rehearsal_launch_packet_write"] if status == "ready" else [],
        "forbiddenEffects": list(PHASE10_FORBIDDEN_EFFECTS),
        "requiredOperatorActions": [
            "confirm_named_phase10_scope",
            "confirm_preview_layer_only",
            "confirm_no_current_dwg_save",
            "confirm_repeated_live_runs",
        ],
        "completionBoundary": "scope_receipt_records_operator_confirmation_not_cad_execution",
        "notEvidenceFor": [
            "phase10_live_preview_not_executed_by_scope_receipt",
            "training_resume",
            "table_c_progress",
            "plugin_readiness",
        ],
    }
    _write_json(receipt_path, receipt)
    return receipt


def evaluate_phase10_rehearsal_runs(
    *,
    run_dirs: list[str | Path] | None = None,
    rehearsal_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    plan_path: str | Path | None = None,
) -> dict[str, Any]:
    """Aggregate existing rehearsal run reports without executing CAD."""

    project_root = find_project_root(Path.cwd())
    requested_run_dirs = list(run_dirs or [])
    resolved_output_dir = _resolve_rehearsal_output_dir(
        project_root=project_root,
        output_dir=output_dir,
        rehearsal_dir=rehearsal_dir,
        run_dirs=requested_run_dirs,
    )
    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    resolved_run_dirs = _resolve_rehearsal_run_dirs(
        project_root=project_root,
        rehearsal_dir=rehearsal_dir or output_dir,
        run_dirs=requested_run_dirs,
        plan_path=plan_path,
    )

    run_summaries = [
        _read_rehearsal_run_summary(run_dir=run_dir, index=index)
        for index, run_dir in enumerate(resolved_run_dirs, start=1)
    ]
    aggregate_blockers: list[str] = []
    if len(resolved_run_dirs) < MIN_REHEARSAL_RUN_COUNT:
        aggregate_blockers.append("phase10_rehearsal_run_count_too_low")
    if not resolved_run_dirs:
        aggregate_blockers.append("phase10_rehearsal_no_run_dirs")
    for summary in run_summaries:
        aggregate_blockers.extend([str(item) for item in summary.get("blockingReasons", [])])

    diff_summary = _build_rehearsal_diff_summary(run_summaries)
    if diff_summary["comparableRunCount"] >= MIN_REHEARSAL_RUN_COUNT and not diff_summary["stableGeometry"]:
        aggregate_blockers.append("phase10_rehearsal_geometry_diff_detected")
    blocking_reasons = _unique(aggregate_blockers)
    missing_evidence = _unique(
        [
            str(item)
            for summary in run_summaries
            for item in summary.get("missingEvidence", [])
        ]
    )
    status = "ready" if not blocking_reasons else "blocked"
    verification_status = "verified" if status == "ready" else "not_verified"
    cad_geometry_verified = status == "ready"

    failure_ledger = _build_rehearsal_failure_ledger(
        run_summaries=run_summaries,
        aggregate_blockers=blocking_reasons,
        status=status,
    )
    diff_path = resolved_output_dir / "phase10_rehearsal_diff_summary.json"
    failure_ledger_path = resolved_output_dir / "phase10_rehearsal_failure_ledger.json"
    result_path = resolved_output_dir / "phase10_rehearsal_result.json"
    _write_json(diff_path, diff_summary)
    _write_json(failure_ledger_path, failure_ledger)

    result = {
        "schemaVersion": PHASE10_REHEARSAL_RESULT_SCHEMA,
        "phase": "Phase 10",
        "packageId": PHASE10_PACKAGE_ID,
        "taskId": PHASE10_RESULT_TASK_ID,
        "status": status,
        "verificationStatus": verification_status,
        "cadGeometryVerified": cad_geometry_verified,
        "cadWritesAttempted": False,
        "runCount": len(resolved_run_dirs),
        "verifiedRunCount": sum(1 for item in run_summaries if item.get("status") == "geometry_verified"),
        "comparableRunCount": diff_summary["comparableRunCount"],
        "stableGeometry": diff_summary["stableGeometry"],
        "runDirs": [str(item) for item in resolved_run_dirs],
        "runSummaries": run_summaries,
        "blockingReasons": blocking_reasons,
        "missingEvidence": missing_evidence,
        "outputDir": str(resolved_output_dir),
        "diffSummaryPath": str(diff_path),
        "failureLedgerPath": str(failure_ledger_path),
        "resultPath": str(result_path),
        "allowedEffects": ["phase10_rehearsal_result_write"],
        "forbiddenEffects": list(PHASE10_FORBIDDEN_EFFECTS),
        "completionBoundary": "rehearsal_result_is_read_only_aggregation_not_cad_execution",
        "notEvidenceFor": [
            "phase10_live_preview_not_executed_by_aggregator",
            "training_resume",
            "table_c_progress",
            "plugin_readiness",
        ],
    }
    _write_json(result_path, result)
    return result


def execute_phase10_rehearsal_plan(
    *,
    plan_path: str | Path,
    output_dir: str | Path | None = None,
    scope_receipt_path: str | Path | None = None,
    live_runs_confirmed: bool = False,
    preview_executor: PreviewExecutor | None = None,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Execute a ready P10 run plan only after explicit live-run confirmation."""

    project_root = find_project_root(Path.cwd())
    resolved_plan_path = resolve_under_project_output(
        project_root,
        Path(plan_path),
        label="phase10 rehearsal execution plan_path",
    )
    plan = _read_json(resolved_plan_path)
    resolved_output_dir = resolve_under_project_output(
        project_root,
        Path(output_dir) if output_dir is not None else resolved_plan_path.parent,
        label="phase10 rehearsal execution output_dir",
    )
    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    resolved_scope_receipt_path = _resolve_scope_receipt_path(
        project_root=project_root,
        output_dir=resolved_output_dir,
        scope_receipt_path=scope_receipt_path,
        label="phase10 rehearsal execution scope_receipt_path",
    )

    run_specs, blockers = _execution_run_specs(project_root=project_root, plan=plan)
    scope_receipt, scope_receipt_blockers = _read_scope_receipt_artifact(resolved_scope_receipt_path)
    blockers.extend(scope_receipt_blockers)
    blockers.extend(
        _scope_receipt_blockers(
            receipt=scope_receipt,
            plan=plan,
            plan_path=resolved_plan_path,
            run_specs=run_specs,
        )
    )
    executor_mode = "injected_executor" if preview_executor is not None else "cad_agent_harness_preview"
    if live_runs_confirmed is not True:
        blockers.append("phase10_live_runs_not_confirmed")
    if preview_executor is None and not _session_host_env_ready(env):
        blockers.append("phase10_session_host_env_missing")

    execution_path = resolved_output_dir / "phase10_rehearsal_execution.json"
    if blockers:
        result = _execution_result_payload(
            status="blocked",
            verification_status="not_verified",
            cad_geometry_verified=False,
            cad_writes_attempted=False,
            executed_run_count=0,
            plan_path=resolved_plan_path,
            scope_receipt_path=resolved_scope_receipt_path,
            output_dir=resolved_output_dir,
            execution_path=execution_path,
            run_specs=run_specs,
            run_results=[],
            aggregate_result={},
            blocking_reasons=_unique(blockers),
            executor_mode=executor_mode,
        )
        _write_json(execution_path, result)
        return result

    executor = preview_executor or _default_preview_executor
    run_results: list[dict[str, Any]] = []
    executor_blockers: list[str] = []
    for spec in run_specs:
        try:
            preview_result = executor(
                cad_plan=dict(spec["cadPlan"]),
                output_dir=spec["outputDir"],
                backend=spec["backend"],
                run_id=spec["runId"],
            )
            run_results.append(
                {
                    "runId": spec["runId"],
                    "outputDir": spec["outputDir"],
                    "status": str(_preview_result_field(preview_result, "status") or "unknown"),
                    "verificationStatus": str(
                        _preview_result_field(preview_result, "verificationStatus") or "not_verified"
                    ),
                }
            )
        except Exception as exc:  # pragma: no cover - defensive runtime capture.
            executor_blockers.append("phase10_rehearsal_preview_execution_failed")
            run_results.append(
                {
                    "runId": spec["runId"],
                    "outputDir": spec["outputDir"],
                    "status": "blocked",
                    "verificationStatus": "not_verified",
                    "error": str(exc),
                }
            )

    aggregate = evaluate_phase10_rehearsal_runs(
        run_dirs=[spec["outputDir"] for spec in run_specs],
        output_dir=resolved_output_dir,
    )
    all_blockers = _unique([*executor_blockers, *[str(item) for item in aggregate.get("blockingReasons", [])]])
    status = "ready" if not all_blockers else "blocked"
    verification_status = str(aggregate.get("verificationStatus") or "not_verified") if status == "ready" else "not_verified"
    cad_geometry_verified = bool(aggregate.get("cadGeometryVerified", False)) if status == "ready" else False
    result = _execution_result_payload(
        status=status,
        verification_status=verification_status,
        cad_geometry_verified=cad_geometry_verified,
        cad_writes_attempted=True,
        executed_run_count=len(run_results),
        plan_path=resolved_plan_path,
        scope_receipt_path=resolved_scope_receipt_path,
        output_dir=resolved_output_dir,
        execution_path=execution_path,
        run_specs=run_specs,
        run_results=run_results,
        aggregate_result=aggregate,
        blocking_reasons=all_blockers,
        executor_mode=executor_mode,
    )
    _write_json(execution_path, result)
    return result


def build_phase10_rehearsal_launch_packet(
    *,
    plan_path: str | Path,
    output_dir: str | Path | None = None,
    scope_receipt_path: str | Path | None = None,
    live_runs_confirmed: bool = False,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build an operator launch packet for P10B without executing CAD."""

    project_root = find_project_root(Path.cwd())
    resolved_plan_path = resolve_under_project_output(
        project_root,
        Path(plan_path),
        label="phase10 rehearsal launch plan_path",
    )
    plan = _read_json(resolved_plan_path)
    resolved_output_dir = resolve_under_project_output(
        project_root,
        Path(output_dir) if output_dir is not None else resolved_plan_path.parent,
        label="phase10 rehearsal launch output_dir",
    )
    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    resolved_scope_receipt_path = _resolve_scope_receipt_path(
        project_root=project_root,
        output_dir=resolved_output_dir,
        scope_receipt_path=scope_receipt_path,
        label="phase10 rehearsal launch scope_receipt_path",
    )

    run_specs, blockers = _execution_run_specs(project_root=project_root, plan=plan)
    scope_receipt, scope_receipt_blockers = _read_scope_receipt_artifact(resolved_scope_receipt_path)
    blockers.extend(scope_receipt_blockers)
    blockers.extend(
        _scope_receipt_blockers(
            receipt=scope_receipt,
            plan=plan,
            plan_path=resolved_plan_path,
            run_specs=run_specs,
        )
    )
    scope_receipt_ready = bool(
        scope_receipt
        and not _scope_receipt_blockers(
            receipt=scope_receipt,
            plan=plan,
            plan_path=resolved_plan_path,
            run_specs=run_specs,
        )
    )
    session_host_ready = _session_host_env_ready(env)
    if live_runs_confirmed is not True:
        blockers.append("phase10_live_runs_not_confirmed")
    if not session_host_ready:
        blockers.append("phase10_session_host_env_missing")

    blocking_reasons = _unique(blockers)
    launch_allowed = not blocking_reasons
    packet_path = resolved_output_dir / "phase10_rehearsal_launch_packet.json"
    packet = {
        "schemaVersion": PHASE10_REHEARSAL_LAUNCH_PACKET_SCHEMA,
        "phase": "Phase 10",
        "packageId": PHASE10_PACKAGE_ID,
        "taskId": PHASE10_LAUNCH_TASK_ID,
        "status": "ready" if launch_allowed else "blocked",
        "verificationStatus": "not_verified",
        "launchAllowed": launch_allowed,
        "cadWritesAttempted": False,
        "liveRunsConfirmed": bool(live_runs_confirmed),
        "sessionHostEnvReady": session_host_ready,
        "sessionHostEnv": _session_host_env_summary(env),
        "planPath": str(resolved_plan_path),
        "outputDir": str(resolved_output_dir),
        "launchPacketPath": str(packet_path),
        "plannedRunCount": len(run_specs),
        "runSpecs": run_specs,
        "launchCommand": _launch_command_payload(
            project_root=project_root,
            plan_path=resolved_plan_path,
            scope_receipt_path=resolved_scope_receipt_path,
            output_dir=resolved_output_dir,
        ),
        "requiredOperatorActions": [
            "confirm_named_phase10_scope",
            "write_phase10_scope_receipt",
            "set_CAD_SESSION_HOST_URL",
            "set_CAD_SESSION_TOKEN",
            "run_rehearsal_run_with_confirm_live_runs",
        ],
        "blockingReasons": blocking_reasons,
        "missingEvidence": _launch_missing_evidence(blocking_reasons, launch_allowed=launch_allowed),
        "scopeReceiptPath": str(resolved_scope_receipt_path),
        "scopeReceiptPlanHash": str(scope_receipt.get("planHash") or "") if scope_receipt else "",
        "scopeReceiptReady": scope_receipt_ready,
        "allowedEffects": ["phase10_rehearsal_launch_packet_write"],
        "nextAllowedEffects": ["phase10_rehearsal_live_preview_runs"] if launch_allowed else [],
        "forbiddenEffects": list(PHASE10_FORBIDDEN_EFFECTS),
        "completionBoundary": "launch_packet_is_operator_preflight_not_cad_execution",
        "notEvidenceFor": [
            "phase10_live_preview_not_executed_by_preflight",
            "training_resume",
            "table_c_progress",
            "plugin_readiness",
        ],
    }
    _write_json(packet_path, packet)
    return packet


def evaluate_phase10_rehearsal_closeout(
    *,
    rehearsal_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    scope_receipt_path: str | Path | None = None,
    launch_packet_path: str | Path | None = None,
    execution_path: str | Path | None = None,
    result_path: str | Path | None = None,
) -> dict[str, Any]:
    """Close out P10B from existing artifacts without executing CAD."""

    project_root = find_project_root(Path.cwd())
    resolved_output_dir = _resolve_closeout_output_dir(
        project_root=project_root,
        rehearsal_dir=rehearsal_dir,
        output_dir=output_dir,
        launch_packet_path=launch_packet_path,
        execution_path=execution_path,
        result_path=result_path,
    )
    resolved_output_dir.mkdir(parents=True, exist_ok=True)

    launch_path = _resolve_closeout_artifact_path(
        project_root=project_root,
        explicit_path=launch_packet_path,
        default_path=resolved_output_dir / "phase10_rehearsal_launch_packet.json",
        label="phase10 rehearsal closeout launch_packet_path",
    )
    execution_artifact_path = _resolve_closeout_artifact_path(
        project_root=project_root,
        explicit_path=execution_path,
        default_path=resolved_output_dir / "phase10_rehearsal_execution.json",
        label="phase10 rehearsal closeout execution_path",
    )
    result_artifact_path = _resolve_closeout_artifact_path(
        project_root=project_root,
        explicit_path=result_path,
        default_path=resolved_output_dir / "phase10_rehearsal_result.json",
        label="phase10 rehearsal closeout result_path",
    )
    receipt_artifact_path = _resolve_closeout_artifact_path(
        project_root=project_root,
        explicit_path=scope_receipt_path,
        default_path=resolved_output_dir / "phase10_rehearsal_scope_receipt.json",
        label="phase10 rehearsal closeout scope_receipt_path",
    )

    launch_packet, launch_blockers = _read_closeout_json_artifact(
        launch_path,
        expected_schema=PHASE10_REHEARSAL_LAUNCH_PACKET_SCHEMA,
        missing_blocker="phase10_closeout_launch_packet_missing",
        invalid_blocker="phase10_closeout_launch_packet_invalid",
    )
    execution, execution_blockers = _read_closeout_json_artifact(
        execution_artifact_path,
        expected_schema=PHASE10_REHEARSAL_EXECUTION_SCHEMA,
        missing_blocker="phase10_closeout_execution_missing",
        invalid_blocker="phase10_closeout_execution_invalid",
    )
    result, result_blockers = _read_closeout_json_artifact(
        result_artifact_path,
        expected_schema=PHASE10_REHEARSAL_RESULT_SCHEMA,
        missing_blocker="phase10_closeout_result_missing",
        invalid_blocker="phase10_closeout_result_invalid",
    )
    scope_receipt, scope_receipt_blockers = _read_closeout_json_artifact(
        receipt_artifact_path,
        expected_schema=PHASE10_REHEARSAL_SCOPE_RECEIPT_SCHEMA,
        missing_blocker="phase10_closeout_scope_receipt_missing",
        invalid_blocker="phase10_closeout_scope_receipt_invalid",
    )

    blockers = _unique(
        [
            *scope_receipt_blockers,
            *_closeout_scope_receipt_blockers(scope_receipt),
            *launch_blockers,
            *_closeout_launch_blockers(launch_packet),
            *execution_blockers,
            *_closeout_execution_blockers(execution),
            *result_blockers,
            *_closeout_result_blockers(result),
            *_closeout_artifact_integrity_blockers(
                launch_packet=launch_packet,
                scope_receipt=scope_receipt,
                execution=execution,
                result=result,
                scope_receipt_path=receipt_artifact_path,
                result_path=result_artifact_path,
            ),
        ]
    )
    status = "ready" if not blockers else "blocked"
    closeout_path = resolved_output_dir / "phase10_rehearsal_closeout.json"
    closeout = {
        "schemaVersion": PHASE10_REHEARSAL_CLOSEOUT_SCHEMA,
        "phase": "Phase 10",
        "packageId": PHASE10_PACKAGE_ID,
        "taskId": PHASE10_CLOSEOUT_TASK_ID,
        "status": status,
        "verificationStatus": "verified" if status == "ready" else "not_verified",
        "phase10CloseoutAllowed": status == "ready",
        "phase11Allowed": status == "ready",
        "cadGeometryVerified": status == "ready",
        "cadWritesAttempted": False,
        "sourceCadWritesAttempted": bool(execution.get("cadWritesAttempted", False)),
        "stableGeometry": bool(result.get("stableGeometry", False)) if result else False,
        "runCount": int(result.get("runCount") or 0) if result else 0,
        "verifiedRunCount": int(result.get("verifiedRunCount") or 0) if result else 0,
        "outputDir": str(resolved_output_dir),
        "closeoutPath": str(closeout_path),
        "sourceArtifacts": {
            "scopeReceipt": str(receipt_artifact_path),
            "launchPacket": str(launch_path),
            "execution": str(execution_artifact_path),
            "result": str(result_artifact_path),
            "diffSummary": str(result.get("diffSummaryPath") or "") if result else "",
            "failureLedger": str(result.get("failureLedgerPath") or "") if result else "",
        },
        "blockingReasons": blockers,
        "missingEvidence": _closeout_missing_evidence(blockers, execution=execution, result=result),
        "allowedEffects": ["phase10_rehearsal_closeout_write"],
        "forbiddenEffects": list(PHASE10_FORBIDDEN_EFFECTS),
        "completionBoundary": "phase10_closeout_consumes_existing_live_rehearsal_artifacts_only",
        "allowedClaims": ["phase10_focused_rehearsal_stable"] if status == "ready" else [],
        "notEvidenceFor": [
            "training_resume",
            "table_c_progress",
            "plugin_readiness",
            "new_cad_execution_by_closeout",
        ],
    }
    _write_json(closeout_path, closeout)
    return closeout


def _resolve_closeout_output_dir(
    *,
    project_root: Path,
    rehearsal_dir: str | Path | None,
    output_dir: str | Path | None,
    launch_packet_path: str | Path | None,
    execution_path: str | Path | None,
    result_path: str | Path | None,
) -> Path:
    if output_dir is not None:
        candidate = Path(output_dir)
    elif rehearsal_dir is not None:
        candidate = Path(rehearsal_dir)
    elif execution_path is not None:
        candidate = Path(execution_path).parent
    elif result_path is not None:
        candidate = Path(result_path).parent
    elif launch_packet_path is not None:
        candidate = Path(launch_packet_path).parent
    else:
        raise ValueError("output_dir or rehearsal_dir is required for phase10 rehearsal closeout")
    return resolve_under_project_output(project_root, candidate, label="phase10 rehearsal closeout output_dir")


def _resolve_closeout_artifact_path(
    *,
    project_root: Path,
    explicit_path: str | Path | None,
    default_path: Path,
    label: str,
) -> Path:
    candidate = Path(explicit_path) if explicit_path is not None else default_path
    return resolve_under_project_output(project_root, candidate, label=label)


def _read_closeout_json_artifact(
    path: Path,
    *,
    expected_schema: str,
    missing_blocker: str,
    invalid_blocker: str,
) -> tuple[dict[str, Any], list[str]]:
    if not path.is_file():
        return {}, [missing_blocker]
    try:
        payload = _read_json(path)
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return {}, [invalid_blocker]
    if payload.get("schemaVersion") != expected_schema:
        return payload, [invalid_blocker]
    return payload, []


def _closeout_launch_blockers(launch_packet: dict[str, Any]) -> list[str]:
    if not launch_packet:
        return []
    blockers: list[str] = []
    if launch_packet.get("status") != "ready":
        blockers.append("phase10_closeout_launch_packet_not_ready")
    if launch_packet.get("launchAllowed") is not True:
        blockers.append("phase10_closeout_launch_not_allowed")
    if launch_packet.get("liveRunsConfirmed") is not True:
        blockers.append("phase10_closeout_launch_live_runs_not_confirmed")
    if launch_packet.get("sessionHostEnvReady") is not True:
        blockers.append("phase10_closeout_launch_session_host_env_missing")
    if launch_packet.get("scopeReceiptReady") is not True:
        blockers.append("phase10_closeout_launch_scope_receipt_not_ready")
    if launch_packet.get("cadWritesAttempted") is not False:
        blockers.append("phase10_closeout_preflight_claimed_cad_write")
    blockers.extend(str(item) for item in launch_packet.get("blockingReasons", []) if str(item))
    return blockers


def _closeout_scope_receipt_blockers(scope_receipt: dict[str, Any]) -> list[str]:
    if not scope_receipt:
        return []
    blockers: list[str] = []
    if scope_receipt.get("status") != "ready":
        blockers.append("phase10_closeout_scope_receipt_not_ready")
    if scope_receipt.get("scopeConfirmed") is not True:
        blockers.append("phase10_closeout_scope_receipt_not_confirmed")
    if scope_receipt.get("liveRunsConfirmed") is not True:
        blockers.append("phase10_closeout_scope_receipt_live_runs_not_confirmed")
    if scope_receipt.get("cadWritesAttempted") is not False:
        blockers.append("phase10_closeout_scope_receipt_claimed_cad_write")
    if scope_receipt.get("blockingReasons"):
        blockers.append("phase10_closeout_scope_receipt_blocked")
    if scope_receipt.get("missingEvidence"):
        blockers.append("phase10_closeout_scope_receipt_missing_evidence")
    return blockers


def _closeout_execution_blockers(execution: dict[str, Any]) -> list[str]:
    if not execution:
        return []
    blockers: list[str] = []
    if execution.get("status") != "ready":
        blockers.append("phase10_closeout_execution_not_ready")
    if execution.get("verificationStatus") != "verified":
        blockers.append("phase10_closeout_execution_not_verified")
    if execution.get("cadGeometryVerified") is not True:
        blockers.append("phase10_closeout_execution_geometry_not_verified")
    if execution.get("cadWritesAttempted") is not True:
        blockers.append("phase10_closeout_execution_cad_write_missing")
    if execution.get("liveRunsConfirmed") is not True:
        blockers.append("phase10_closeout_execution_live_runs_not_confirmed")
    if str(execution.get("executorMode") or "") != "cad_agent_harness_preview":
        blockers.append("phase10_closeout_executor_mode_not_production")
    if _int_or_zero(execution.get("executedRunCount")) < MIN_REHEARSAL_RUN_COUNT:
        blockers.append("phase10_closeout_executed_run_count_too_low")
    if execution.get("blockingReasons"):
        blockers.append("phase10_closeout_execution_blocked")
    if execution.get("missingEvidence"):
        blockers.append("phase10_closeout_execution_missing_evidence")
    return blockers


def _closeout_result_blockers(result: dict[str, Any]) -> list[str]:
    if not result:
        return []
    blockers: list[str] = []
    if result.get("status") != "ready":
        blockers.append("phase10_closeout_result_not_ready")
    if result.get("verificationStatus") != "verified":
        blockers.append("phase10_closeout_result_not_verified")
    if result.get("cadGeometryVerified") is not True:
        blockers.append("phase10_closeout_result_geometry_not_verified")
    if result.get("stableGeometry") is not True:
        blockers.append("phase10_closeout_result_geometry_not_stable")
    if _int_or_zero(result.get("runCount")) < MIN_REHEARSAL_RUN_COUNT:
        blockers.append("phase10_closeout_result_run_count_too_low")
    if _int_or_zero(result.get("verifiedRunCount")) < MIN_REHEARSAL_RUN_COUNT:
        blockers.append("phase10_closeout_verified_run_count_too_low")
    if _int_or_zero(result.get("comparableRunCount")) < MIN_REHEARSAL_RUN_COUNT:
        blockers.append("phase10_closeout_comparable_run_count_too_low")
    if result.get("blockingReasons"):
        blockers.append("phase10_closeout_result_blocked")
    if result.get("missingEvidence"):
        blockers.append("phase10_closeout_result_missing_evidence")
    return blockers


def _closeout_artifact_integrity_blockers(
    *,
    launch_packet: dict[str, Any],
    scope_receipt: dict[str, Any],
    execution: dict[str, Any],
    result: dict[str, Any],
    scope_receipt_path: Path,
    result_path: Path,
) -> list[str]:
    if (
        launch_packet.get("schemaVersion") != PHASE10_REHEARSAL_LAUNCH_PACKET_SCHEMA
        or scope_receipt.get("schemaVersion") != PHASE10_REHEARSAL_SCOPE_RECEIPT_SCHEMA
        or execution.get("schemaVersion") != PHASE10_REHEARSAL_EXECUTION_SCHEMA
        or result.get("schemaVersion") != PHASE10_REHEARSAL_RESULT_SCHEMA
    ):
        return []

    blockers: list[str] = []
    if len({_path_key(scope_receipt.get("planPath")), _path_key(launch_packet.get("planPath")), _path_key(execution.get("planPath"))}) != 1:
        blockers.append("phase10_closeout_artifact_plan_path_mismatch")

    resolved_receipt_path = _path_key(scope_receipt_path)
    declared_receipt_paths = [
        _path_key(scope_receipt.get("receiptPath")),
        _path_key(launch_packet.get("scopeReceiptPath")),
        _path_key(execution.get("scopeReceiptPath")),
    ]
    if not resolved_receipt_path or any(path != resolved_receipt_path for path in declared_receipt_paths):
        blockers.append("phase10_closeout_artifact_scope_receipt_path_mismatch")
    if str(launch_packet.get("scopeReceiptPlanHash") or "") != str(scope_receipt.get("planHash") or ""):
        blockers.append("phase10_closeout_artifact_scope_receipt_hash_mismatch")

    output_dirs = [
        _path_key(scope_receipt.get("outputDir")),
        _path_key(launch_packet.get("outputDir")),
        _path_key(execution.get("outputDir")),
        _path_key(result.get("outputDir")),
    ]
    if not output_dirs[0] or len(set(output_dirs)) != 1:
        blockers.append("phase10_closeout_artifact_output_dir_mismatch")

    aggregate = execution.get("aggregateResult") if isinstance(execution.get("aggregateResult"), dict) else {}
    if not aggregate:
        blockers.append("phase10_closeout_execution_aggregate_missing")
    else:
        resolved_result_path = _path_key(result_path)
        declared_result_paths = [
            _path_key(result.get("resultPath")),
            _path_key(aggregate.get("resultPath")),
        ]
        if not resolved_result_path or any(path != resolved_result_path for path in declared_result_paths):
            blockers.append("phase10_closeout_artifact_result_path_mismatch")
        if _closeout_result_fingerprint(aggregate) != _closeout_result_fingerprint(result):
            blockers.append("phase10_closeout_artifact_result_mismatch")

    receipt_specs = _dict_list(scope_receipt.get("runSpecs"))
    launch_specs = _dict_list(launch_packet.get("runSpecs"))
    execution_specs = _dict_list(execution.get("runSpecs"))
    run_results = _dict_list(execution.get("runResults"))
    if (
        _run_specs_fingerprint(receipt_specs) != _run_specs_fingerprint(launch_specs)
        or _run_specs_fingerprint(launch_specs) != _run_specs_fingerprint(execution_specs)
    ):
        blockers.append("phase10_closeout_artifact_run_specs_mismatch")

    spec_dirs = _output_dir_keys(execution_specs, "outputDir")
    run_result_dirs = _output_dir_keys(run_results, "outputDir")
    result_dirs = _path_list_keys(result.get("runDirs"))
    summary_dirs = _output_dir_keys(_dict_list(result.get("runSummaries")), "runDir")
    if not spec_dirs or spec_dirs != run_result_dirs or spec_dirs != result_dirs or result_dirs != summary_dirs:
        blockers.append("phase10_closeout_artifact_run_dirs_mismatch")

    expected_count = _int_or_zero(result.get("runCount"))
    count_values = [
        _int_or_zero(scope_receipt.get("plannedRunCount")),
        _int_or_zero(launch_packet.get("plannedRunCount")),
        _int_or_zero(execution.get("plannedRunCount")),
        _int_or_zero(execution.get("executedRunCount")),
        expected_count,
        len(execution_specs),
        len(run_results),
        len(result_dirs),
    ]
    if expected_count < MIN_REHEARSAL_RUN_COUNT or any(count != expected_count for count in count_values):
        blockers.append("phase10_closeout_artifact_run_count_mismatch")

    return _unique(blockers)


def _closeout_missing_evidence(
    blockers: list[str],
    *,
    execution: dict[str, Any],
    result: dict[str, Any],
) -> list[str]:
    missing = [
        str(item)
        for item in [
            *_string_list(execution.get("missingEvidence") if execution else []),
            *_string_list(result.get("missingEvidence") if result else []),
        ]
        if str(item)
    ]
    if blockers and not missing:
        missing.append("phase10_verified_live_rehearsal_closeout")
    if any("scope_receipt" in str(item) for item in blockers):
        missing.append("phase10_scope_confirmation_receipt")
    return _unique(missing)


def _normalize_scope(scope: dict[str, Any]) -> dict[str, Any]:
    cad_plans = scope.get("cadPlans", [])
    if not isinstance(cad_plans, list):
        cad_plans = []
    return {
        "scopeId": str(scope.get("scopeId") or "phase10.unconfirmed"),
        "scopeConfirmed": bool(scope.get("scopeConfirmed") is True),
        "objectFamily": str(scope.get("objectFamily") or ""),
        "capability": str(scope.get("capability") or ""),
        "backend": str(scope.get("backend") or DEFAULT_PHASE10_BACKEND),
        "runCount": _int_or_zero(scope.get("runCount")),
        "phase9ExitRunDir": str(scope.get("phase9ExitRunDir") or ""),
        "cadPlans": [dict(item) for item in cad_plans if isinstance(item, dict)],
    }


def _default_scope_capability(object_family: str) -> str:
    family = _slug(object_family or "cad_object")
    return f"single_{family}_preview_repeatability"


def _default_scope_id(object_family: str, capability: str) -> str:
    if object_family:
        return f"phase10.{_slug(object_family)}.rehearsal.proposal"
    if capability:
        return f"phase10.{_slug(capability)}.rehearsal.proposal"
    return "phase10.unconfirmed.rehearsal.proposal"


def _slug(value: str) -> str:
    text = str(value or "").strip().lower()
    chars = [char if char.isalnum() else "_" for char in text]
    slug = "_".join(part for part in "".join(chars).split("_") if part)
    return slug or "cad_object"


def _scope_blockers(scope: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if scope["scopeConfirmed"] is not True:
        blockers.append("phase10_scope_not_confirmed")
    if not scope["objectFamily"] and not scope["capability"]:
        blockers.append("phase10_scope_target_missing")
    if scope["backend"] not in PHASE10_REAL_BACKENDS:
        blockers.append("phase10_real_backend_required")
    if scope["runCount"] < MIN_REHEARSAL_RUN_COUNT:
        blockers.append("phase10_repetition_count_too_low")
    if not scope["cadPlans"]:
        blockers.append("phase10_cad_plan_missing")
    blockers.extend(_phase9_exit_reference_blockers(scope["phase9ExitRunDir"]))

    for plan in scope["cadPlans"]:
        drawing = plan.get("drawing") if isinstance(plan.get("drawing"), dict) else {}
        if str(drawing.get("layer") or "") != PREVIEW_LAYER:
            blockers.append("phase10_non_preview_layer_forbidden")
        if validate_plan(plan):
            blockers.append("phase10_cad_plan_invalid")
    return _unique(blockers)


def _phase9_exit_reference_blockers(run_dir: str) -> list[str]:
    if not run_dir:
        return ["phase9_exit_reference_missing"]
    try:
        gate = evaluate_phase9_exit_gate(run_dir=Path(run_dir))
    except (OSError, ValueError, json.JSONDecodeError):
        return ["phase9_exit_reference_invalid"]
    if gate.get("phase10Allowed") is not True:
        return ["phase9_exit_not_ready"]
    return []


def _build_run_specs(scope: dict[str, Any], output_dir: Path) -> list[dict[str, Any]]:
    plans = list(scope["cadPlans"])
    specs: list[dict[str, Any]] = []
    for index in range(1, int(scope["runCount"]) + 1):
        plan = plans[(index - 1) % len(plans)]
        specs.append(
            {
                "runId": f"phase10-rehearsal-run-{index:02d}",
                "command": "preview",
                "backend": scope["backend"],
                "targetLayer": PREVIEW_LAYER,
                "outputDir": str(output_dir / f"run_{index:02d}"),
                "cadPlan": plan,
                "requiredEvidence": ["real_cad_readback", "no_save_guard"],
                "safety": _safety_policy(),
            }
        )
    return specs


def _execution_run_specs(*, project_root: Path, plan: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    blockers: list[str] = []
    if plan.get("schemaVersion") != PHASE10_REHEARSAL_PLAN_SCHEMA:
        blockers.append("phase10_rehearsal_plan_schema_invalid")
    if plan.get("status") != "ready":
        blockers.append("phase10_rehearsal_plan_not_ready")
    if plan.get("backend") not in PHASE10_REAL_BACKENDS:
        blockers.append("phase10_rehearsal_plan_backend_not_real")

    raw_specs = plan.get("runSpecs") if isinstance(plan.get("runSpecs"), list) else []
    if len(raw_specs) < MIN_REHEARSAL_RUN_COUNT:
        blockers.append("phase10_rehearsal_plan_run_count_too_low")

    run_specs: list[dict[str, Any]] = []
    for index, raw_spec in enumerate(raw_specs, start=1):
        if not isinstance(raw_spec, dict):
            blockers.append("phase10_rehearsal_run_spec_invalid")
            continue
        spec = dict(raw_spec)
        run_id = str(spec.get("runId") or f"phase10-rehearsal-run-{index:02d}")
        backend = str(spec.get("backend") or plan.get("backend") or "")
        target_layer = str(spec.get("targetLayer") or "")
        cad_plan = spec.get("cadPlan") if isinstance(spec.get("cadPlan"), dict) else {}
        output_ref = str(spec.get("outputDir") or "")
        if spec.get("command") != "preview":
            blockers.append("phase10_rehearsal_run_spec_command_invalid")
        if backend not in PHASE10_REAL_BACKENDS:
            blockers.append("phase10_rehearsal_run_spec_backend_not_real")
        if target_layer != PREVIEW_LAYER:
            blockers.append("phase10_rehearsal_run_spec_layer_not_preview")
        drawing = cad_plan.get("drawing") if isinstance(cad_plan.get("drawing"), dict) else {}
        if str(drawing.get("layer") or "") != PREVIEW_LAYER:
            blockers.append("phase10_rehearsal_run_spec_plan_layer_not_preview")
        if validate_plan(cad_plan):
            blockers.append("phase10_rehearsal_run_spec_cad_plan_invalid")
        if not output_ref:
            blockers.append("phase10_rehearsal_run_spec_output_missing")
            continue
        try:
            run_output_dir = resolve_under_project_output(
                project_root,
                Path(output_ref),
                label="phase10 rehearsal execution run outputDir",
            )
        except ValueError:
            blockers.append("phase10_rehearsal_run_spec_output_invalid")
            continue
        run_specs.append(
            {
                "runId": run_id,
                "command": "preview",
                "backend": backend,
                "targetLayer": target_layer,
                "outputDir": str(run_output_dir),
                "cadPlan": dict(cad_plan),
            }
        )
    return run_specs, _unique(blockers)


def _execution_result_payload(
    *,
    status: str,
    verification_status: str,
    cad_geometry_verified: bool,
    cad_writes_attempted: bool,
    executed_run_count: int,
    plan_path: Path,
    scope_receipt_path: Path,
    output_dir: Path,
    execution_path: Path,
    run_specs: list[dict[str, Any]],
    run_results: list[dict[str, Any]],
    aggregate_result: dict[str, Any],
    blocking_reasons: list[str],
    executor_mode: str,
) -> dict[str, Any]:
    not_evidence_for = [
        "training_resume",
        "table_c_progress",
        "plugin_readiness",
    ]
    if executor_mode == "injected_executor":
        not_evidence_for.append("injected_executor_result_is_not_production_cad_proof")
    return {
        "schemaVersion": PHASE10_REHEARSAL_EXECUTION_SCHEMA,
        "phase": "Phase 10",
        "packageId": PHASE10_PACKAGE_ID,
        "taskId": PHASE10_EXECUTION_TASK_ID,
        "status": status,
        "verificationStatus": verification_status,
        "cadGeometryVerified": cad_geometry_verified,
        "cadWritesAttempted": cad_writes_attempted,
        "liveRunsConfirmed": cad_writes_attempted,
        "executorMode": executor_mode,
        "plannedRunCount": len(run_specs),
        "executedRunCount": executed_run_count,
        "planPath": str(plan_path),
        "scopeReceiptPath": str(scope_receipt_path),
        "outputDir": str(output_dir),
        "executionPath": str(execution_path),
        "runSpecs": run_specs,
        "runResults": run_results,
        "aggregateResult": aggregate_result,
        "blockingReasons": list(blocking_reasons),
        "missingEvidence": [str(item) for item in aggregate_result.get("missingEvidence", [])]
        if aggregate_result
        else [],
        "allowedEffects": ["phase10_rehearsal_live_preview_runs"] if cad_writes_attempted else [],
        "forbiddenEffects": list(PHASE10_FORBIDDEN_EFFECTS),
        "completionBoundary": "rehearsal_execution_requires_confirmed_scope_and_session_host_readback",
        "notEvidenceFor": not_evidence_for,
    }


def _session_host_env_ready(env: dict[str, str] | None) -> bool:
    source = os.environ if env is None else env
    return bool(str(source.get("CAD_SESSION_HOST_URL") or "").strip()) and bool(
        str(source.get("CAD_SESSION_TOKEN") or "").strip()
    )


def _session_host_env_summary(env: dict[str, str] | None) -> dict[str, bool]:
    source = os.environ if env is None else env
    return {
        "urlConfigured": bool(str(source.get("CAD_SESSION_HOST_URL") or "").strip()),
        "tokenConfigured": bool(str(source.get("CAD_SESSION_TOKEN") or "").strip()),
        "timeoutConfigured": bool(str(source.get("CAD_SESSION_HOST_TIMEOUT_SECONDS") or "").strip()),
    }


def _resolve_scope_receipt_path(
    *,
    project_root: Path,
    output_dir: Path,
    scope_receipt_path: str | Path | None,
    label: str,
) -> Path:
    candidate = Path(scope_receipt_path) if scope_receipt_path is not None else output_dir / "phase10_rehearsal_scope_receipt.json"
    return resolve_under_project_output(project_root, candidate, label=label)


def _read_scope_receipt_artifact(path: Path) -> tuple[dict[str, Any], list[str]]:
    if not path.is_file():
        return {}, ["phase10_scope_receipt_missing"]
    try:
        payload = _read_json(path)
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return {}, ["phase10_scope_receipt_invalid"]
    if payload.get("schemaVersion") != PHASE10_REHEARSAL_SCOPE_RECEIPT_SCHEMA:
        return payload, ["phase10_scope_receipt_invalid"]
    return payload, []


def _scope_receipt_blockers(
    *,
    receipt: dict[str, Any],
    plan: dict[str, Any],
    plan_path: Path,
    run_specs: list[dict[str, Any]],
) -> list[str]:
    if not receipt:
        return []
    blockers: list[str] = []
    if receipt.get("status") != "ready":
        blockers.append("phase10_scope_receipt_not_ready")
    if receipt.get("scopeConfirmed") is not True:
        blockers.append("phase10_scope_receipt_not_confirmed")
    if receipt.get("liveRunsConfirmed") is not True:
        blockers.append("phase10_scope_receipt_live_runs_not_confirmed")
    if _path_key(receipt.get("planPath")) != _path_key(plan_path):
        blockers.append("phase10_scope_receipt_plan_path_mismatch")
    if str(receipt.get("planHash") or "") != _json_fingerprint(plan):
        blockers.append("phase10_scope_receipt_plan_hash_mismatch")
    if str(receipt.get("scopeId") or "") != str(plan.get("scopeId") or ""):
        blockers.append("phase10_scope_receipt_scope_mismatch")
    if str(receipt.get("backend") or "") != str(plan.get("backend") or ""):
        blockers.append("phase10_scope_receipt_backend_mismatch")
    if _int_or_zero(receipt.get("plannedRunCount")) != len(run_specs):
        blockers.append("phase10_scope_receipt_run_count_mismatch")
    if _run_specs_fingerprint(_dict_list(receipt.get("runSpecs"))) != _run_specs_fingerprint(run_specs):
        blockers.append("phase10_scope_receipt_run_specs_mismatch")
    if str(receipt.get("confirmationStatement") or "").strip() == "":
        blockers.append("phase10_scope_receipt_confirmation_missing")
    return _unique(blockers)


def _launch_missing_evidence(blockers: list[str], *, launch_allowed: bool) -> list[str]:
    missing: list[str] = []
    if any(str(item).startswith("phase10_scope_receipt") for item in blockers):
        missing.append("phase10_scope_confirmation_receipt")
    if not launch_allowed:
        missing.append("real_cad_readback")
    return _unique(missing)


def _launch_command_payload(
    *,
    project_root: Path,
    plan_path: Path,
    scope_receipt_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    script_path = project_root / "scripts" / "cad_agent_harness.py"
    argv = [
        sys.executable,
        str(script_path),
        "rehearsal-run",
        "--plan",
        str(plan_path),
        "--scope-receipt",
        str(scope_receipt_path),
        "--output-dir",
        str(output_dir),
        "--confirm-live-runs",
        "--json",
    ]
    return {
        "argv": argv,
        "cwd": str(project_root),
        "requiresEnv": ["CAD_SESSION_HOST_URL", "CAD_SESSION_TOKEN"],
        "cadWritesWhenRun": True,
    }


def _default_preview_executor(*, cad_plan: dict[str, Any], output_dir: str, backend: str, run_id: str) -> dict[str, Any]:
    from core.contracts.cad_agent_harness import run_harness_command

    return run_harness_command(
        "preview",
        cad_plan=dict(cad_plan),
        output_dir=output_dir,
        backend=backend,
    )


def _preview_result_field(value: Any, field_name: str) -> Any:
    if isinstance(value, dict):
        return value.get(field_name)
    if hasattr(value, "report") and isinstance(value.report, dict):
        return value.report.get(field_name)
    return None


def _resolve_rehearsal_output_dir(
    *,
    project_root: Path,
    output_dir: str | Path | None,
    rehearsal_dir: str | Path | None,
    run_dirs: list[str | Path],
) -> Path:
    if output_dir is not None:
        candidate = Path(output_dir)
    elif rehearsal_dir is not None:
        candidate = Path(rehearsal_dir)
    elif run_dirs:
        candidate = Path(run_dirs[0]).parent
    else:
        raise ValueError("output_dir or rehearsal_dir is required for phase10 rehearsal result")
    return resolve_under_project_output(project_root, candidate, label="phase10 rehearsal result output_dir")


def _resolve_rehearsal_run_dirs(
    *,
    project_root: Path,
    rehearsal_dir: str | Path | None,
    run_dirs: list[str | Path],
    plan_path: str | Path | None,
) -> list[Path]:
    if run_dirs:
        return [
            resolve_under_project_output(project_root, Path(item), label="phase10 rehearsal run_dir")
            for item in run_dirs
        ]
    if rehearsal_dir is None:
        return []
    resolved_rehearsal_dir = resolve_under_project_output(
        project_root,
        Path(rehearsal_dir),
        label="phase10 rehearsal_dir",
    )
    resolved_plan_path = _resolve_rehearsal_plan_path(project_root, resolved_rehearsal_dir, plan_path)
    if resolved_plan_path is not None and resolved_plan_path.is_file():
        plan = _read_json(resolved_plan_path)
        specs = plan.get("runSpecs") if isinstance(plan.get("runSpecs"), list) else []
        return [
            resolve_under_project_output(
                project_root,
                Path(str(spec.get("outputDir") or "")),
                label="phase10 rehearsal runSpec outputDir",
            )
            for spec in specs
            if isinstance(spec, dict) and str(spec.get("outputDir") or "")
        ]
    if not resolved_rehearsal_dir.is_dir():
        return []
    return sorted(path for path in resolved_rehearsal_dir.iterdir() if path.is_dir() and path.name.startswith("run_"))


def _resolve_rehearsal_plan_path(
    project_root: Path,
    rehearsal_dir: Path,
    plan_path: str | Path | None,
) -> Path | None:
    candidate = Path(plan_path) if plan_path is not None else rehearsal_dir / "phase10_rehearsal_plan.json"
    resolved = resolve_under_project_output(project_root, candidate, label="phase10 rehearsal plan_path")
    return resolved


def _read_rehearsal_run_summary(*, run_dir: Path, index: int) -> dict[str, Any]:
    run_id = run_dir.name or f"run_{index:02d}"
    report_path = run_dir / "phase9_preview_report.json"
    if not run_dir.is_dir():
        return _missing_run_summary(
            run_id=run_id,
            run_dir=run_dir,
            blockers=["phase10_rehearsal_run_missing"],
        )
    if not report_path.is_file():
        return _missing_run_summary(
            run_id=run_id,
            run_dir=run_dir,
            blockers=["phase10_rehearsal_report_missing"],
        )
    try:
        report = _read_json(report_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return _missing_run_summary(
            run_id=run_id,
            run_dir=run_dir,
            blockers=["phase10_rehearsal_report_invalid"],
        )

    missing_evidence = _string_list(report.get("missingEvidence"))
    upstream_blockers = _string_list(report.get("blockingReasons"))
    created_count, created_valid = _non_negative_int_field(report.get("createdHandleCount"))
    readback_count, readback_valid = _non_negative_int_field(report.get("readbackEntityCount"))
    target_layer = str(report.get("targetLayer") or "")
    backend = str(report.get("driverBackend") or "")
    geometry_audit = report.get("geometryAudit") if isinstance(report.get("geometryAudit"), dict) else {}
    blockers: list[str] = []
    if backend not in PHASE10_REAL_BACKENDS:
        blockers.append("phase10_run_backend_not_real")
    if target_layer != PREVIEW_LAYER:
        blockers.append("phase10_run_layer_not_preview")
    if report.get("savedCurrentDwg") is not False:
        blockers.append("phase10_run_saved_current_dwg")
    if report.get("cadGeometryVerified") is not True:
        blockers.append("phase10_run_geometry_not_verified")
    if str(report.get("verificationStatus") or "").casefold() != "verified":
        blockers.append("phase10_run_verification_status_not_verified")
    if not created_valid or created_count <= 0:
        blockers.append("phase10_run_created_handles_missing")
    if not readback_valid or readback_count <= 0:
        blockers.append("phase10_run_readback_missing")
    if missing_evidence:
        blockers.append("phase10_run_missing_evidence")
    if upstream_blockers:
        blockers.append("phase10_run_report_blocked")
    if geometry_audit.get("allReadbackOnPreviewLayer") is not True:
        blockers.append("phase10_run_preview_layer_audit_failed")
    geometry_signature = _geometry_signature(report, readback_count=readback_count)
    if not geometry_signature:
        blockers.append("phase10_run_geometry_signature_missing")

    return {
        "runId": run_id,
        "runDir": str(run_dir),
        "reportPath": str(report_path),
        "status": str(report.get("status") or "unknown"),
        "verificationStatus": str(report.get("verificationStatus") or "not_verified"),
        "driverBackend": backend,
        "targetLayer": target_layer,
        "savedCurrentDwg": bool(report.get("savedCurrentDwg", True)),
        "cadGeometryVerified": bool(report.get("cadGeometryVerified", False)),
        "createdHandleCount": created_count,
        "readbackEntityCount": readback_count,
        "geometrySignature": geometry_signature,
        "missingEvidence": missing_evidence,
        "upstreamBlockingReasons": upstream_blockers,
        "blockingReasons": _unique(blockers),
    }


def _missing_run_summary(*, run_id: str, run_dir: Path, blockers: list[str]) -> dict[str, Any]:
    return {
        "runId": run_id,
        "runDir": str(run_dir),
        "reportPath": str(run_dir / "phase9_preview_report.json"),
        "status": "missing",
        "verificationStatus": "not_verified",
        "driverBackend": "",
        "targetLayer": "",
        "savedCurrentDwg": False,
        "cadGeometryVerified": False,
        "createdHandleCount": 0,
        "readbackEntityCount": 0,
        "geometrySignature": {},
        "missingEvidence": ["real_cad_readback"],
        "upstreamBlockingReasons": [],
        "blockingReasons": list(blockers),
    }


def _geometry_signature(report: dict[str, Any], *, readback_count: int) -> dict[str, Any]:
    audit = report.get("geometryAudit") if isinstance(report.get("geometryAudit"), dict) else {}
    bbox = audit.get("bbox") if isinstance(audit.get("bbox"), dict) else {}
    bbox_size = _number_list(bbox.get("size"))
    if not bbox_size:
        return {}
    return {
        "bboxSize": bbox_size,
        "readbackEntityCount": readback_count,
        "layerCounts": _normalized_count_map(audit.get("layerCounts")),
        "typeCounts": _normalized_count_map(audit.get("typeCounts")),
    }


def _build_rehearsal_diff_summary(run_summaries: list[dict[str, Any]]) -> dict[str, Any]:
    comparable = [item for item in run_summaries if isinstance(item.get("geometrySignature"), dict) and item["geometrySignature"]]
    baseline = dict(comparable[0]["geometrySignature"]) if comparable else {}
    baseline_run_id = str(comparable[0]["runId"]) if comparable else ""
    diffs: list[dict[str, Any]] = []
    for summary in comparable[1:]:
        signature = dict(summary["geometrySignature"])
        if signature != baseline:
            diffs.append(
                {
                    "runId": str(summary.get("runId") or ""),
                    "runDir": str(summary.get("runDir") or ""),
                    "field": "geometrySignature",
                    "expected": baseline,
                    "actual": signature,
                }
            )
    return {
        "schemaVersion": PHASE10_REHEARSAL_DIFF_SCHEMA,
        "phase": "Phase 10",
        "packageId": PHASE10_PACKAGE_ID,
        "stableGeometry": not diffs,
        "baselineRunId": baseline_run_id,
        "baselineGeometrySignature": baseline,
        "runCount": len(run_summaries),
        "comparableRunCount": len(comparable),
        "diffCount": len(diffs),
        "diffs": diffs,
        "completionBoundary": "diff_summary_compares_existing_readback_reports_only",
    }


def _build_rehearsal_failure_ledger(
    *,
    run_summaries: list[dict[str, Any]],
    aggregate_blockers: list[str],
    status: str,
) -> dict[str, Any]:
    failures = [
        {
            "runId": str(summary.get("runId") or ""),
            "runDir": str(summary.get("runDir") or ""),
            "blockingReasons": [str(item) for item in summary.get("blockingReasons", [])],
            "missingEvidence": [str(item) for item in summary.get("missingEvidence", [])],
            "upstreamBlockingReasons": [str(item) for item in summary.get("upstreamBlockingReasons", [])],
        }
        for summary in run_summaries
        if summary.get("blockingReasons")
    ]
    return {
        "schemaVersion": PHASE10_REHEARSAL_FAILURE_LEDGER_SCHEMA,
        "phase": "Phase 10",
        "packageId": PHASE10_PACKAGE_ID,
        "status": status,
        "failureCount": len(failures),
        "failures": failures,
        "aggregateBlockingReasons": list(aggregate_blockers),
        "completionBoundary": "failure_ledger_records_rehearsal_result_only",
    }


def _safety_policy() -> dict[str, Any]:
    return {
        "saveAllowed": False,
        "deleteAllowed": False,
        "formalLayersAllowed": False,
        "targetLayer": PREVIEW_LAYER,
        "backendMustBeExplicit": True,
    }


def _int_or_zero(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return 0
    return parsed if parsed >= 0 else 0


def _non_negative_int_field(value: Any) -> tuple[int, bool]:
    if isinstance(value, bool):
        return 0, False
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return 0, False
    if parsed < 0:
        return 0, False
    return parsed, True


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return []


def _dict_list(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [dict(item) for item in value if isinstance(item, dict)]
    return []


def _path_key(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return str(Path(text).resolve()).casefold()


def _path_list_keys(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [key for key in (_path_key(item) for item in value) if key]


def _output_dir_keys(items: list[dict[str, Any]], field_name: str) -> list[str]:
    return [key for key in (_path_key(item.get(field_name)) for item in items) if key]


def _run_specs_fingerprint(specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "runId": str(spec.get("runId") or ""),
            "command": str(spec.get("command") or ""),
            "backend": str(spec.get("backend") or ""),
            "targetLayer": str(spec.get("targetLayer") or ""),
            "outputDir": _path_key(spec.get("outputDir")),
            "cadPlan": spec.get("cadPlan") if isinstance(spec.get("cadPlan"), dict) else {},
        }
        for spec in specs
    ]


def _json_fingerprint(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _closeout_result_fingerprint(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": str(payload.get("status") or ""),
        "verificationStatus": str(payload.get("verificationStatus") or ""),
        "cadGeometryVerified": payload.get("cadGeometryVerified") is True,
        "runCount": _int_or_zero(payload.get("runCount")),
        "verifiedRunCount": _int_or_zero(payload.get("verifiedRunCount")),
        "comparableRunCount": _int_or_zero(payload.get("comparableRunCount")),
        "stableGeometry": payload.get("stableGeometry") is True,
        "runDirs": _path_list_keys(payload.get("runDirs")),
        "blockingReasons": _string_list(payload.get("blockingReasons")),
        "missingEvidence": _string_list(payload.get("missingEvidence")),
        "outputDir": _path_key(payload.get("outputDir")),
        "diffSummaryPath": _path_key(payload.get("diffSummaryPath")),
        "failureLedgerPath": _path_key(payload.get("failureLedgerPath")),
        "resultPath": _path_key(payload.get("resultPath")),
    }


def _number_list(value: Any) -> list[float]:
    if not isinstance(value, list):
        return []
    result: list[float] = []
    for item in value:
        try:
            result.append(round(float(item), 6))
        except (TypeError, ValueError):
            return []
    return result


def _normalized_count_map(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, int] = {}
    for key, item in value.items():
        parsed, valid = _non_negative_int_field(item)
        if valid:
            result[str(key)] = parsed
    return dict(sorted(result.items()))


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON artifact root must be an object")
    return dict(payload)


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
