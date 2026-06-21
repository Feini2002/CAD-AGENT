"""Phase 9 single CAD preview/readback contract runner.

This package is intentionally narrow: one deterministic preview task, writes
only to CODEX_PREVIEW, no current-DWG save, and completion only after created
handles are read back from a real CAD backend.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from core.contracts.evidence_ledger import (
    EvidenceLedgerRecord,
    InMemoryEvidenceLedger,
    evidence_package_content_hash,
)
from core.contracts.vnext import CompletionDecision, CompletionJudge, EvidenceItem, EvidencePackage, TaskObject
from core.execution.execute_plan import execute_plan_file
from core.path_safety import find_project_root, resolve_under_project_output
from core.plan_engine.dry_run_report import create_dry_run_report
from core.plan_engine.validate_plan import validate_plan
from core.verification.inspect_dwg import snapshot_entities_by_handles
from core.verification.preview_only_audit import (
    PREVIEW_ONLY_AUDIT_EXPECTED,
    build_preview_only_audit,
    preview_only_audit_check,
    with_legacy_safety_aliases,
)


PREVIEW_LAYER = "CODEX_PREVIEW"
PHASE9_PACKAGE_ID = "phase9.package1.single-cad-preview"
PHASE9_TASK_ID = "phase9.single-preview.task"
PHASE9_SCOPE_ID = "phase9.single-preview.scope"
PHASE9_EVIDENCE_PACKAGE_ID = "phase9-single-preview-evidence"
PHASE9_FORBIDDEN_EFFECTS = (
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
    "phase10_rehearsal",
)
REAL_CAD_BACKENDS = {
    "real_cad",
    "cad_mcp",
    "autocad_existing",
    "active_autocad",
    "autocad_com_existing",
    "cad_session_host",
    "autocad_plugin",
    "cloud_automation",
}
FAKE_CAD_BACKENDS = {"fake", "fake_cad", "fake_driver", "fake_driver_preflight", "mock", "dry_run"}
NOT_CHECKED_BOUNDARY = ["user_visual_acceptance", "phase10_rehearsal"]


@dataclass(frozen=True)
class Phase9SinglePreviewResult:
    status: str
    verification_status: str
    task: TaskObject
    scope: dict[str, Any]
    cad_plan: dict[str, Any]
    validation_errors: list[str]
    dry_run_result: dict[str, Any]
    preflight: dict[str, Any]
    execution_summary: dict[str, Any]
    readback_entities: list[dict[str, Any]]
    evidence: EvidencePackage
    completion: CompletionDecision
    ledger: InMemoryEvidenceLedger
    report: dict[str, Any]
    autocad_readiness_probe: dict[str, Any]
    evidence_package_id: str
    evidence_content_hash: str
    missing_evidence: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)
    allowed_claims: list[str] = field(default_factory=list)
    not_proven: list[str] = field(default_factory=list)
    cad_geometry_verified: bool = False
    created_handle_count: int = 0
    readback_entity_count: int = 0
    output_dir: str = ""
    artifacts: dict[str, str] = field(default_factory=dict)
    external_blocker: str = ""


def phase9_default_single_preview_plan() -> dict[str, Any]:
    """Return the locked minimal CAD_PLAN for Phase 9 package 1."""

    return {
        "version": "0.1",
        "domain": "generic",
        "intent": "draw_object",
        "object": {
            "type": "table",
            "name": "phase9_preview_table",
            "width": 900,
            "depth": 450,
        },
        "placement": {
            "mode": "absolute",
            "base_point": [72000, 42000, 0],
        },
        "drawing": {
            "layer": PREVIEW_LAYER,
            "include_label": False,
            "include_dimensions": False,
        },
        "confidence": 0.91,
        "needs_confirmation": False,
    }


def build_phase9_preview_scope_record(
    cad_plan: dict[str, Any] | None = None,
    *,
    scope_id: str = PHASE9_SCOPE_ID,
) -> dict[str, Any]:
    plan = dict(cad_plan or phase9_default_single_preview_plan())
    drawing = plan.get("drawing") if isinstance(plan.get("drawing"), dict) else {}
    obj = plan.get("object") if isinstance(plan.get("object"), dict) else {}
    placement = plan.get("placement") if isinstance(plan.get("placement"), dict) else {}
    target_layer = str(drawing.get("layer") or "")
    return {
        "schemaVersion": "phase9-preview-scope/v1",
        "phase": "Phase 9",
        "packageId": PHASE9_PACKAGE_ID,
        "scopeId": scope_id,
        "maxPreviewTaskCount": 1,
        "targetLayer": target_layer,
        "requiredTargetLayer": PREVIEW_LAYER,
        "cadPlanIntent": str(plan.get("intent") or ""),
        "cadPlanObject": {
            "type": str(obj.get("type") or ""),
            "name": str(obj.get("name") or ""),
            "size": [obj.get("width"), obj.get("depth")],
        },
        "targetScope": {
            "placementMode": str(placement.get("mode") or ""),
            "basePoint": list(placement.get("base_point") or []),
            "createdHandlesOnly": True,
        },
        "allowedEffects": [
            "cad_plan_validate",
            "cad_plan_dry_run",
            "cad_preview_write",
            "created_handles_readback",
            "evidence_package_write",
        ],
        "forbiddenEffects": list(PHASE9_FORBIDDEN_EFFECTS),
        "savePolicy": {
            "savedCurrentDwg": False,
            "saveAllowed": False,
            "overwriteAllowed": False,
        },
        "writePolicy": {
            "previewOnly": True,
            "allowedLayers": [PREVIEW_LAYER],
            "formalLayersAllowed": False,
            "deleteAllowed": False,
            "mutateCreatedHandlesOnly": True,
        },
        "evidenceRequired": ["real_cad_readback", "no_save_guard"],
    }


def build_phase9_preview_task(
    cad_plan: dict[str, Any] | None = None,
    *,
    task_id: str = PHASE9_TASK_ID,
) -> TaskObject:
    plan = dict(cad_plan or phase9_default_single_preview_plan())
    scope = build_phase9_preview_scope_record(plan)
    return TaskObject(
        task_id=task_id,
        task_kind="phase9_single_cad_preview",
        user_intent=(
            "Run one scoped CAD preview on CODEX_PREVIEW and verify only through "
            "created-handle readback without saving the current DWG."
        ),
        inputs={
            "cadPlan": plan,
            "scopeRecord": scope,
            "requestedEffects": ["cad_preview_write", "created_handles_readback"],
            "permissionClass": "cad_preview",
        },
        target_scope=scope,
        constraints=[
            "max_one_preview_task",
            "target_layer_must_be_CODEX_PREVIEW",
            "savedCurrentDwg_must_be_false",
            "no_formal_layer_write",
            "no_delete_entities",
            "no_registry_or_table_c_mutation",
        ],
        safety_boundaries=[
            "single_item_preview_only",
            "no_dwg_save",
            "no_formal_layer_write",
            "no_plugin_call",
            "no_training_source_mutation",
            "no_table_c_mutation",
        ],
        success_criteria=[
            "CAD_PLAN validates",
            "dry-run is valid",
            "created handles are captured",
            "created handles are read back from a real CAD backend",
            "readback entities are only on CODEX_PREVIEW",
            "savedCurrentDwg is false",
        ],
        evidence_requirements=["real_cad_readback", "no_save_guard"],
    )


def build_phase9_evidence_package(
    *,
    task: TaskObject | None = None,
    task_id: str | None = None,
    execution_summary: dict[str, Any],
    readback_entities: list[dict[str, Any]],
    driver_backend: str,
    validation_errors: list[str] | None = None,
    dry_run_result: dict[str, Any] | None = None,
    scope: dict[str, Any] | None = None,
    blocking_reasons: list[str] | None = None,
    model_text: str | None = None,
    screenshot_ref: str | None = None,
    autocad_readiness_probe: dict[str, Any] | None = None,
) -> EvidencePackage:
    if task is None:
        task = build_phase9_preview_task(task_id=task_id or PHASE9_TASK_ID)
    validation_errors = [str(item) for item in validation_errors or []]
    dry_run_result = dict(dry_run_result or {})
    blocking_reasons = [str(item) for item in blocking_reasons or []]
    scope = dict(scope or build_phase9_preview_scope_record(task.inputs.get("cadPlan", {})))

    created_handles = _created_handles(execution_summary)
    readback_handles = _readback_handles(readback_entities)
    missing_handles = [handle for handle in created_handles if handle not in readback_handles]
    unexpected_layers = sorted(
        {
            str(entity.get("layer") or "")
            for entity in readback_entities
            if str(entity.get("layer") or "") != PREVIEW_LAYER
        }
    )
    saved_current_dwg = _saved_current_dwg(execution_summary)
    safety = execution_summary.get("safety") if isinstance(execution_summary.get("safety"), dict) else {}
    preview_audit = preview_only_audit_check(safety)
    no_save_pass = saved_current_dwg is False and safety.get("saved_dwg") is not True
    scope_pass = (
        scope.get("targetLayer") == PREVIEW_LAYER
        and scope.get("maxPreviewTaskCount") == 1
        and bool(created_handles)
        and not missing_handles
        and not unexpected_layers
    )
    preflight_pass = not validation_errors and dry_run_result.get("status") == "valid"
    readback_ok = (
        _is_real_cad_backend(driver_backend)
        and no_save_pass
        and scope_pass
        and preflight_pass
        and preview_audit.get("status") == "pass"
        and bool(readback_entities)
        and not blocking_reasons
    )

    items = [
        EvidenceItem(
            kind="phase9_scope_lock",
            status="pass" if scope.get("targetLayer") == PREVIEW_LAYER and scope.get("maxPreviewTaskCount") == 1 else "fail",
            backend="phase9_contract",
            metadata={
                "scopeId": scope.get("scopeId"),
                "targetLayer": scope.get("targetLayer"),
                "maxPreviewTaskCount": scope.get("maxPreviewTaskCount"),
                "forbiddenEffects": list(scope.get("forbiddenEffects") or []),
            },
        ),
        EvidenceItem(
            kind="cad_plan_validate",
            status="pass" if not validation_errors else "fail",
            backend="phase9_preflight",
            metadata={"validationErrors": validation_errors},
        ),
        EvidenceItem(
            kind="cad_plan_dry_run",
            status="pass" if dry_run_result.get("status") == "valid" else "fail",
            backend="phase9_preflight",
            metadata={
                "dryRunStatus": dry_run_result.get("status", ""),
                "layer": dry_run_result.get("layer", ""),
            },
        ),
        EvidenceItem(
            kind="autocad_readiness_probe",
            status="pass" if (autocad_readiness_probe or {}).get("status") == "ready" else "not_run",
            backend=str(driver_backend),
            metadata=dict(autocad_readiness_probe or {}),
        ),
        EvidenceItem(
            kind="no_save_guard",
            status="pass" if no_save_pass else "fail",
            backend="phase9_preview",
            metadata={
                "savedCurrentDwg": saved_current_dwg,
                "saved_current_dwg": saved_current_dwg,
                "saved_dwg": safety.get("saved_dwg"),
                "expected": dict(PREVIEW_ONLY_AUDIT_EXPECTED),
            },
        ),
        EvidenceItem(
            kind="cad_readback",
            status="pass" if readback_ok else "fail",
            backend=str(driver_backend),
            readback_status="ok" if readback_ok else ("not_real_backend" if readback_entities else "not_run"),
            cad_geometry_verified=readback_ok,
            metadata={
                "backend": str(driver_backend),
                "driverMode": str(driver_backend),
                "createdHandles": created_handles,
                "createdHandleCount": len(created_handles),
                "readbackEntityCount": len(readback_entities),
                "readbackHandles": readback_handles,
                "missingCreatedHandles": missing_handles,
                "unexpectedLayers": unexpected_layers,
                "savedCurrentDwg": saved_current_dwg,
                "previewOnlyAudit": preview_audit,
                "bbox": _bbox_from_entities(readback_entities),
                "layerCounts": _layer_counts(readback_entities),
                "typeCounts": _type_counts(readback_entities),
                "blockingReasons": blocking_reasons,
            },
        ),
    ]
    if model_text:
        items.append(
            EvidenceItem(
                kind="model_text",
                status="informational",
                metadata={
                    "text": str(model_text),
                    "boundary": "model text cannot replace created-handle CAD readback",
                },
            )
        )
    if screenshot_ref:
        items.append(
            EvidenceItem(
                kind="screenshot",
                status="informational",
                metadata={
                    "sourceRef": str(screenshot_ref),
                    "boundary": "screenshot is visual aid only and cannot satisfy real_cad_readback",
                },
            )
        )
    return EvidencePackage(task_id=task.task_id, items=items)


def run_phase9_single_preview(
    *,
    cad_plan: dict[str, Any] | None = None,
    output_dir: str | Path | None = None,
    driver_factory: Callable[[], Any] | None = None,
    driver_backend: str = "autocad_com_existing",
    task_id: str = PHASE9_TASK_ID,
) -> Phase9SinglePreviewResult:
    plan = dict(cad_plan or phase9_default_single_preview_plan())
    task = build_phase9_preview_task(plan, task_id=task_id)
    scope = build_phase9_preview_scope_record(plan)

    project_root = find_project_root(Path.cwd())
    resolved_output = _resolve_output_dir(project_root, output_dir)
    artifacts: dict[str, str] = {}
    if resolved_output is not None:
        resolved_output.mkdir(parents=True, exist_ok=True)
        artifacts["outputDir"] = str(resolved_output)

    cad_plan_path = _write_json_artifact(resolved_output, "phase9_single_preview_cad_plan.json", plan)
    if cad_plan_path:
        artifacts["cadPlan"] = cad_plan_path

    validation_errors = [str(item) for item in validate_plan(plan)]
    dry_run_result = _dry_run(plan, validation_errors)
    dry_run_path = _write_json_artifact(resolved_output, "phase9_single_preview_dry_run.json", dry_run_result)
    if dry_run_path:
        artifacts["dryRun"] = dry_run_path

    preflight = _build_preflight(plan, scope, validation_errors, dry_run_result)
    blocking_reasons = list(preflight["blockingReasons"])
    autocad_readiness_probe = _not_run_readiness_probe(
        driver_backend=driver_backend,
        reason="preflight_blocked" if blocking_reasons else "pending",
    )
    readback_entities: list[dict[str, Any]] = []
    execution_summary: dict[str, Any] = {
        "status": "not_run",
        "intent": plan.get("intent", ""),
        "layer": _plan_layer(plan),
        "preview_only": True,
        "created_handles": [],
        "savedCurrentDwg": False,
        "safety": with_legacy_safety_aliases(build_preview_only_audit(layer=PREVIEW_LAYER)),
    }
    external_blocker = ""

    if not blocking_reasons:
        driver: Any | None = None
        try:
            driver = _build_driver(driver_factory)
            active_doc = _active_document_summary(driver)
            autocad_readiness_probe = _ready_readiness_probe(
                driver=driver,
                driver_backend=driver_backend,
                preview_attempted=False,
            )
            if hasattr(driver, "ensure_layer"):
                driver.ensure_layer(PREVIEW_LAYER)
            plan_path_for_execute = Path(cad_plan_path) if cad_plan_path else _write_temp_plan(plan)
            autocad_readiness_probe["previewAttempted"] = True
            execution_summary = dict(
                execute_plan_file(
                    plan_path_for_execute,
                    driver=driver,
                    preview_only=True,
                    allow_unconfirmed=False,
                    allow_destructive=False,
                )
            )
            execution_summary["activeDocument"] = active_doc
            execution_summary["driverBackend"] = driver_backend
            execution_summary["savedCurrentDwg"] = False
            if "safety" not in execution_summary:
                execution_summary["safety"] = with_legacy_safety_aliases(build_preview_only_audit(layer=PREVIEW_LAYER))
            created_handles = _created_handles(execution_summary)
            if created_handles:
                readback_entities = snapshot_entities_by_handles(driver, created_handles)
            missing_handles = [handle for handle in created_handles if handle not in _readback_handles(readback_entities)]
            if not created_handles:
                blocking_reasons.append("created handles readback blocked: preview execution returned no created handles")
            if missing_handles:
                blocking_reasons.append(
                    "created handles readback blocked: missing created handles "
                    + ", ".join(missing_handles)
                )
            unexpected_layers = sorted(
                {
                    str(entity.get("layer") or "")
                    for entity in readback_entities
                    if str(entity.get("layer") or "") != PREVIEW_LAYER
                }
            )
            if unexpected_layers:
                blocking_reasons.append(
                    "created handles readback blocked: unexpected layers "
                    + ", ".join(unexpected_layers)
                )
        except Exception as exc:  # pragma: no cover - real CAD availability is environment-specific.
            external_blocker = f"{type(exc).__name__}: {exc}"
            blocking_reasons.append(f"external CAD preview blocker: {external_blocker}")
            execution_summary["status"] = "not_run"
            execution_summary["externalBlocker"] = external_blocker
            if driver is None:
                autocad_readiness_probe = _blocked_readiness_probe(
                    driver_backend=driver_backend,
                    blocker=external_blocker,
                )
            elif autocad_readiness_probe.get("status") != "ready":
                autocad_readiness_probe = _blocked_readiness_probe(
                    driver_backend=driver_backend,
                    blocker=external_blocker,
                )

    probe_path = _write_json_artifact(resolved_output, "phase9_autocad_readiness_probe.json", autocad_readiness_probe)
    if probe_path:
        artifacts["autoCADReadinessProbe"] = probe_path
    execution_path = _write_json_artifact(resolved_output, "phase9_single_preview_execution_summary.json", execution_summary)
    if execution_path:
        artifacts["executionSummary"] = execution_path
    readback_path = _write_json_artifact(
        resolved_output,
        "phase9_single_preview_readback_entities.json",
        {"entities": readback_entities},
    )
    if readback_path:
        artifacts["readbackEntities"] = readback_path

    evidence = build_phase9_evidence_package(
        task=task,
        execution_summary=execution_summary,
        readback_entities=readback_entities,
        driver_backend=driver_backend,
        validation_errors=validation_errors,
        dry_run_result=dry_run_result,
        scope=scope,
        blocking_reasons=blocking_reasons,
        autocad_readiness_probe=autocad_readiness_probe,
    )
    completion = CompletionJudge().judge(task=task, evidence=evidence)
    content_hash = evidence_package_content_hash(evidence)
    ledger = _build_ledger(
        task=task,
        evidence=evidence,
        content_hash=content_hash,
        source_ref=artifacts.get("executionSummary", ""),
        blocking_reasons=blocking_reasons,
    )
    cad_geometry_verified = evidence.satisfies("real_cad_readback") and evidence.satisfies("no_save_guard")
    created_count = len(_created_handles(execution_summary))
    readback_count = len(readback_entities)
    missing_evidence = list(completion.missing_evidence)
    status = _result_status(
        cad_geometry_verified=cad_geometry_verified,
        external_blocker=external_blocker,
        blocking_reasons=blocking_reasons,
        completion=completion,
        created_count=created_count,
        readback_count=readback_count,
    )
    verification_status = "verified" if cad_geometry_verified else "not_verified"
    allowed_claims = ["single_preview_geometry_verified"] if cad_geometry_verified else []
    not_proven = [] if cad_geometry_verified else ["real_cad_geometry_verified"]
    if NOT_CHECKED_BOUNDARY:
        not_proven.extend(NOT_CHECKED_BOUNDARY)

    report = _build_report(
        status=status,
        verification_status=verification_status,
        task=task,
        scope=scope,
        validation_errors=validation_errors,
        dry_run_result=dry_run_result,
        preflight=preflight,
        execution_summary=execution_summary,
        readback_entities=readback_entities,
        evidence=evidence,
        completion=completion,
        content_hash=content_hash,
        blocking_reasons=blocking_reasons,
        missing_evidence=missing_evidence,
        cad_geometry_verified=cad_geometry_verified,
        driver_backend=driver_backend,
        artifacts=artifacts,
        external_blocker=external_blocker,
        autocad_readiness_probe=autocad_readiness_probe,
    )
    evidence_path = _write_json_artifact(resolved_output, "phase9_single_preview_evidence_package.json", asdict(evidence))
    if evidence_path:
        artifacts["evidencePackage"] = evidence_path
    ledger_path = _write_json_artifact(
        resolved_output,
        "phase9_single_preview_ledger_records.json",
        [asdict(record) for record in ledger.records],
    )
    if ledger_path:
        artifacts["ledgerRecords"] = ledger_path
    report["artifacts"] = dict(artifacts)
    report_path = _write_json_artifact(resolved_output, "phase9_preview_report.json", report)
    if report_path:
        artifacts["report"] = report_path
        report["artifacts"] = dict(artifacts)

    return Phase9SinglePreviewResult(
        status=status,
        verification_status=verification_status,
        task=task,
        scope=scope,
        cad_plan=plan,
        validation_errors=validation_errors,
        dry_run_result=dry_run_result,
        preflight=preflight,
        execution_summary=execution_summary,
        readback_entities=readback_entities,
        evidence=evidence,
        completion=completion,
        ledger=ledger,
        report=report,
        autocad_readiness_probe=autocad_readiness_probe,
        evidence_package_id=PHASE9_EVIDENCE_PACKAGE_ID,
        evidence_content_hash=content_hash,
        missing_evidence=missing_evidence,
        blocking_reasons=blocking_reasons,
        allowed_claims=allowed_claims,
        not_proven=not_proven,
        cad_geometry_verified=cad_geometry_verified,
        created_handle_count=created_count,
        readback_entity_count=readback_count,
        output_dir=str(resolved_output) if resolved_output else "",
        artifacts=artifacts,
        external_blocker=external_blocker,
    )


def _resolve_output_dir(project_root: Path, output_dir: str | Path | None) -> Path | None:
    if output_dir is None:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_dir = Path("output") / "validation_runs" / f"phase9-single-preview-{stamp}"
    return resolve_under_project_output(project_root, Path(output_dir), label="phase9 output_dir")


def _write_json_artifact(output_dir: Path | None, filename: str, payload: Any) -> str:
    if output_dir is None:
        return ""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    return str(path)


def _write_temp_plan(plan: dict[str, Any]) -> Path:
    project_root = find_project_root(Path.cwd())
    output_dir = _resolve_output_dir(project_root, None)
    path = output_dir / "phase9_single_preview_cad_plan.json"
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _dry_run(plan: dict[str, Any], validation_errors: list[str]) -> dict[str, Any]:
    if validation_errors:
        return {
            "version": "0.1",
            "status": "invalid",
            "validation_errors": list(validation_errors),
            "human_summary": "CAD_PLAN dry-run not attempted because validate failed.",
        }
    try:
        return create_dry_run_report(plan)
    except Exception as exc:
        return {
            "version": "0.1",
            "status": "error",
            "validation_errors": [],
            "error": f"{type(exc).__name__}: {exc}",
            "human_summary": "CAD_PLAN dry-run failed before CAD execution.",
        }


def _build_preflight(
    plan: dict[str, Any],
    scope: dict[str, Any],
    validation_errors: list[str],
    dry_run_result: dict[str, Any],
) -> dict[str, Any]:
    blocking_reasons: list[str] = []
    target_layer = _plan_layer(plan)
    if scope.get("maxPreviewTaskCount") != 1:
        blocking_reasons.append("Phase 9 package 1 allows exactly one preview task")
    if target_layer != PREVIEW_LAYER:
        blocking_reasons.append(f"target layer must be {PREVIEW_LAYER}; got {target_layer!r}")
    if validation_errors:
        blocking_reasons.append("validate failed: " + "; ".join(validation_errors))
    if dry_run_result.get("status") != "valid":
        blocking_reasons.append(f"dry-run failed: {dry_run_result.get('status', 'unknown')}")
    return {
        "status": "blocked" if blocking_reasons else "ready",
        "targetLayer": target_layer,
        "requiredTargetLayer": PREVIEW_LAYER,
        "validationStatus": "valid" if not validation_errors else "invalid",
        "dryRunStatus": str(dry_run_result.get("status", "")),
        "blockingReasons": blocking_reasons,
    }


def _build_driver(driver_factory: Callable[[], Any] | None) -> Any:
    if driver_factory is not None:
        return driver_factory()
    from core.cad_io.autocad_com import AutoCADComDriver

    return AutoCADComDriver(connect_existing_only=True)


def _not_run_readiness_probe(*, driver_backend: str, reason: str) -> dict[str, Any]:
    return {
        "schemaVersion": "phase9-autocad-readiness-probe/v1",
        "status": "not_run",
        "driverBackend": str(driver_backend),
        "connectExistingOnly": True,
        "applicationAvailable": False,
        "activeDocumentAvailable": False,
        "activeDocumentAccessible": False,
        "activeDocument": {},
        "previewAttempted": False,
        "notRunReason": str(reason),
        "blocker": "",
    }


def _blocked_readiness_probe(*, driver_backend: str, blocker: str) -> dict[str, Any]:
    return {
        "schemaVersion": "phase9-autocad-readiness-probe/v1",
        "status": "external_blocker",
        "driverBackend": str(driver_backend),
        "connectExistingOnly": True,
        "applicationAvailable": False,
        "activeDocumentAvailable": False,
        "activeDocumentAccessible": False,
        "activeDocument": {},
        "previewAttempted": False,
        "notRunReason": "",
        "blocker": str(blocker),
    }


def _ready_readiness_probe(*, driver: Any, driver_backend: str, preview_attempted: bool) -> dict[str, Any]:
    doc_summary: dict[str, str] = {}
    doc_access_error = ""
    doc = getattr(driver, "doc", None)
    try:
        doc_summary = _active_document_summary(driver)
        doc_accessible = doc is not None
    except Exception as exc:
        doc_accessible = False
        doc_access_error = f"{type(exc).__name__}: {exc}"
    return {
        "schemaVersion": "phase9-autocad-readiness-probe/v1",
        "status": "ready" if getattr(driver, "app", None) is not None and doc_accessible else "external_blocker",
        "driverBackend": str(driver_backend),
        "connectExistingOnly": True,
        "applicationAvailable": getattr(driver, "app", None) is not None,
        "activeDocumentAvailable": doc is not None,
        "activeDocumentAccessible": doc_accessible,
        "activeDocument": doc_summary,
        "previewAttempted": bool(preview_attempted),
        "notRunReason": "",
        "blocker": doc_access_error,
    }


def _active_document_summary(driver: Any) -> dict[str, str]:
    doc = getattr(driver, "doc", None)
    return {
        "name": str(getattr(doc, "Name", getattr(doc, "name", "")) or ""),
        "fullName": str(getattr(doc, "FullName", getattr(doc, "fullName", "")) or ""),
    }


def _created_handles(summary: dict[str, Any]) -> list[str]:
    value = summary.get("created_handles", summary.get("createdHandles"))
    return _string_list(value)


def _readback_handles(entities: list[dict[str, Any]]) -> list[str]:
    return [str(entity.get("handle") or "") for entity in entities if str(entity.get("handle") or "")]


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if isinstance(value, tuple):
        return [str(item) for item in value if str(item)]
    if isinstance(value, dict):
        if isinstance(value.get("handles"), list):
            return [str(item) for item in value["handles"] if str(item)]
        if value.get("handle"):
            return [str(value["handle"])]
    return []


def _saved_current_dwg(summary: dict[str, Any]) -> bool | None:
    if "savedCurrentDwg" in summary:
        return bool(summary["savedCurrentDwg"])
    if "saved_current_dwg" in summary:
        return bool(summary["saved_current_dwg"])
    safety = summary.get("safety")
    if isinstance(safety, dict):
        if "saved_dwg" in safety:
            return bool(safety["saved_dwg"])
        if "saves_dwg" in safety:
            return bool(safety["saves_dwg"])
    return None


def _plan_layer(plan: dict[str, Any]) -> str:
    drawing = plan.get("drawing")
    return str(drawing.get("layer") if isinstance(drawing, dict) else "")


def _is_real_cad_backend(driver_backend: str) -> bool:
    value = str(driver_backend).casefold()
    return value in REAL_CAD_BACKENDS and value not in FAKE_CAD_BACKENDS


def _type_counts(entities: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entity in entities:
        entity_type = str(entity.get("type", "unknown"))
        counts[entity_type] = counts.get(entity_type, 0) + 1
    return dict(sorted(counts.items()))


def _layer_counts(entities: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entity in entities:
        layer = str(entity.get("layer", ""))
        counts[layer] = counts.get(layer, 0) + 1
    return dict(sorted(counts.items()))


def _bbox_from_entities(entities: list[dict[str, Any]]) -> dict[str, Any] | None:
    points: list[list[float]] = []
    for entity in entities:
        for key in ("start_point", "end_point", "position", "center", "insertion_point"):
            value = entity.get(key)
            if isinstance(value, list) and len(value) >= 2:
                points.append([float(value[0]), float(value[1])])
        for value in entity.get("points", []):
            if isinstance(value, list) and len(value) >= 2:
                points.append([float(value[0]), float(value[1])])
        bbox = entity.get("bbox")
        if isinstance(bbox, dict):
            for key in ("min", "max"):
                value = bbox.get(key)
                if isinstance(value, list) and len(value) >= 2:
                    points.append([float(value[0]), float(value[1])])
    if not points:
        return None
    min_x = min(point[0] for point in points)
    min_y = min(point[1] for point in points)
    max_x = max(point[0] for point in points)
    max_y = max(point[1] for point in points)
    return {"min": [min_x, min_y], "max": [max_x, max_y], "size": [max_x - min_x, max_y - min_y]}


def _build_ledger(
    *,
    task: TaskObject,
    evidence: EvidencePackage,
    content_hash: str,
    source_ref: str,
    blocking_reasons: list[str],
) -> InMemoryEvidenceLedger:
    ledger = InMemoryEvidenceLedger()
    for requirement in task.evidence_requirements:
        satisfies = evidence.satisfies(requirement)
        ledger.append(
            EvidenceLedgerRecord(
                ledger_id=f"{task.task_id}.{requirement}",
                task_id=task.task_id,
                contract_id=PHASE9_PACKAGE_ID,
                evidence_package_id=PHASE9_EVIDENCE_PACKAGE_ID,
                evidence_type=str(requirement),
                producer="phase9_single_preview",
                tool_card_id="phase9_single_preview_runner",
                verification_status="verified" if satisfies and requirement == "real_cad_readback" else (
                    "pass" if satisfies else "not_verified"
                ),
                blocked_reason="; ".join(blocking_reasons) if blocking_reasons and not satisfies else "",
                not_verified_reason="" if satisfies else f"missing verified {requirement}",
                source_ref=source_ref,
                content_hash=content_hash,
                metadata={"phase": "Phase 9", "packageId": PHASE9_PACKAGE_ID},
            )
        )
    return ledger


def _result_status(
    *,
    cad_geometry_verified: bool,
    external_blocker: str,
    blocking_reasons: list[str],
    completion: CompletionDecision,
    created_count: int,
    readback_count: int,
) -> str:
    if cad_geometry_verified:
        return "geometry_verified"
    if external_blocker:
        return "external_blocker"
    if blocking_reasons:
        return "blocked"
    if created_count and readback_count and completion.missing_evidence == ["real_cad_readback"]:
        return "not_verified"
    if completion.status == "not_verified":
        return "not_verified"
    return "blocked"


def _build_report(
    *,
    status: str,
    verification_status: str,
    task: TaskObject,
    scope: dict[str, Any],
    validation_errors: list[str],
    dry_run_result: dict[str, Any],
    preflight: dict[str, Any],
    execution_summary: dict[str, Any],
    readback_entities: list[dict[str, Any]],
    evidence: EvidencePackage,
    completion: CompletionDecision,
    content_hash: str,
    blocking_reasons: list[str],
    missing_evidence: list[str],
    cad_geometry_verified: bool,
    driver_backend: str,
    artifacts: dict[str, str],
    external_blocker: str,
    autocad_readiness_probe: dict[str, Any],
) -> dict[str, Any]:
    created_handles = _created_handles(execution_summary)
    readback_handles = _readback_handles(readback_entities)
    bbox = _bbox_from_entities(readback_entities)
    return {
        "schemaVersion": "phase9-single-preview-report/v1",
        "phase": "Phase 9",
        "packageId": PHASE9_PACKAGE_ID,
        "taskId": task.task_id,
        "status": status,
        "verificationStatus": verification_status,
        "targetLayer": scope.get("targetLayer"),
        "requiredTargetLayer": PREVIEW_LAYER,
        "driverBackend": driver_backend,
        "savedCurrentDwg": _saved_current_dwg(execution_summary),
        "cadGeometryVerified": cad_geometry_verified,
        "validationStatus": "valid" if not validation_errors else "invalid",
        "validationErrors": list(validation_errors),
        "dryRunStatus": dry_run_result.get("status", ""),
        "preflight": preflight,
        "autoCADReadinessProbe": dict(autocad_readiness_probe),
        "createdHandles": created_handles,
        "createdHandleCount": len(created_handles),
        "readbackHandles": readback_handles,
        "readbackEntityCount": len(readback_entities),
        "activeDocument": execution_summary.get("activeDocument", {}),
        "geometryAudit": {
            "bbox": bbox,
            "layerCounts": _layer_counts(readback_entities),
            "typeCounts": _type_counts(readback_entities),
            "allReadbackOnPreviewLayer": all(
                str(entity.get("layer") or "") == PREVIEW_LAYER for entity in readback_entities
            )
            if readback_entities
            else False,
        },
        "checks": [
            preview_only_audit_check(execution_summary.get("safety")),
            {
                "name": "created_handles_readback",
                "status": "pass" if created_handles and set(created_handles).issubset(set(readback_handles)) else "fail",
                "message": "All created handles were read back."
                if created_handles and set(created_handles).issubset(set(readback_handles))
                else "Created handles are missing from readback or were not created.",
            },
            {
                "name": "real_cad_readback",
                "status": "pass" if evidence.satisfies("real_cad_readback") else "fail",
                "message": "Created-handle readback is verified on a real CAD backend."
                if evidence.satisfies("real_cad_readback")
                else "Real CAD readback evidence is missing or not verified.",
            },
        ],
        "evidencePackageId": PHASE9_EVIDENCE_PACKAGE_ID,
        "evidenceContentHash": content_hash,
        "completion": asdict(completion),
        "missingEvidence": list(missing_evidence),
        "blockingReasons": list(blocking_reasons),
        "externalBlocker": external_blocker,
        "evidenceBoundary": {
            "checked": ["cad_plan_validate", "cad_plan_dry_run", "created_handles_readback", "no_save_guard"],
            "notChecked": list(NOT_CHECKED_BOUNDARY),
            "screenshotUse": "visual_aid_only_not_completion_evidence",
        },
        "artifacts": dict(artifacts),
    }
