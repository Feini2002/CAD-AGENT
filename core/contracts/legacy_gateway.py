"""Phase 6 Legacy Gateway skeleton.

This module only registers legacy gateway adapter boundaries. It does not
execute CAD, call AutoCAD, read DWG files, save DWG files, mutate registries,
advance Table C, or call plugins.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.contracts.vnext import (
    CompletionDecision,
    CompletionJudge,
    ContractDecision,
    EvidenceItem,
    EvidencePackage,
    TaskObject,
    ToolCard,
    ToolContract,
    cad_plan_candidate_from_task,
)


LEGACY_GATEWAY_FORBIDDEN_EFFECTS = [
    "cad_execute",
    "cad_preview_write",
    "dwg_save",
    "save_current_dwg",
    "delete_entities",
    "formal_layer_write",
    "plugin_call",
    "plugin_execute",
    "registry_mutation",
    "table_c_mutation",
    "training_source_mutation",
    "protected_evidence_mutation",
]
PREVIEW_LAYER = "CODEX_PREVIEW"


@dataclass(frozen=True)
class LegacyGatewayAdapter:
    adapter_id: str
    operation: str
    legacy_entrypoint: str
    tool_card: ToolCard
    allowed_evidence: tuple[str, ...] = field(default_factory=tuple)
    boundary: str = "registered_only"
    executes_cad: bool = False
    reads_dwg: bool = False
    writes_dwg: bool = False
    saves_dwg: bool = False
    mutates_registry: bool = False
    advances_table_c: bool = False


@dataclass(frozen=True)
class LegacyValidateDryRunAdapterResult:
    status: str
    verification_status: str
    task: TaskObject
    cad_plan_candidate: dict[str, Any]
    validate_adapter: LegacyGatewayAdapter
    dry_run_adapter: LegacyGatewayAdapter
    validate_contract: ToolContract
    dry_run_contract: ToolContract
    validate_authorization: ContractDecision
    dry_run_authorization: ContractDecision
    validate_request: dict[str, Any]
    dry_run_request: dict[str, Any]
    validation_errors: list[str]
    dry_run_result: dict[str, Any]
    evidence: EvidencePackage
    completion: CompletionDecision
    missing_evidence: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)
    allowed_claims: list[str] = field(default_factory=list)
    not_proven: list[str] = field(default_factory=list)
    cad_geometry_verified: bool = False


@dataclass(frozen=True)
class LegacyRegistrationGuardResult:
    status: str
    verification_status: str
    task: TaskObject
    adapter: LegacyGatewayAdapter
    tool_contract: ToolContract
    authorization: ContractDecision
    request: dict[str, Any]
    evidence: EvidencePackage
    completion: CompletionDecision
    missing_evidence: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)
    allowed_claims: list[str] = field(default_factory=list)
    not_proven: list[str] = field(default_factory=list)
    cad_geometry_verified: bool = False


def legacy_gateway_adapter_cards() -> dict[str, LegacyGatewayAdapter]:
    return {
        "legacy.validate": LegacyGatewayAdapter(
            adapter_id="legacy.validate",
            operation="validate",
            legacy_entrypoint="core.plan_engine.validate_plan.validate_plan",
            tool_card=ToolCard(
                tool_id="legacy.validate",
                permission_class="deterministic_verify",
                allowed_effects=["legacy_validate_registered"],
                forbidden_effects=list(LEGACY_GATEWAY_FORBIDDEN_EFFECTS),
            ),
            allowed_evidence=("cad_plan_validate",),
            boundary="schema and CAD_PLAN legality only",
        ),
        "legacy.dry_run": LegacyGatewayAdapter(
            adapter_id="legacy.dry_run",
            operation="dry_run",
            legacy_entrypoint="core.plan_engine.dry_run_report.create_dry_run_report",
            tool_card=ToolCard(
                tool_id="legacy.dry_run",
                permission_class="deterministic_verify",
                allowed_effects=["legacy_dry_run_registered"],
                forbidden_effects=list(LEGACY_GATEWAY_FORBIDDEN_EFFECTS),
            ),
            allowed_evidence=("cad_plan_dry_run",),
            boundary="dry-run feasibility only",
        ),
        "legacy.preview": LegacyGatewayAdapter(
            adapter_id="legacy.preview",
            operation="preview",
            legacy_entrypoint="core.execution.execute_plan.execute_plan_file",
            tool_card=ToolCard(
                tool_id="legacy.preview",
                permission_class="cad_preview",
                allowed_effects=["legacy_preview_registered"],
                forbidden_effects=list(LEGACY_GATEWAY_FORBIDDEN_EFFECTS),
            ),
            allowed_evidence=("legacy_preview_registered", "no_save_guard"),
            boundary="registration only; no AutoCAD call and no CAD write in this package",
        ),
        "legacy.readback": LegacyGatewayAdapter(
            adapter_id="legacy.readback",
            operation="readback",
            legacy_entrypoint="core.verification.cad_validation_gates.readback_gate_failure",
            tool_card=ToolCard(
                tool_id="legacy.readback",
                permission_class="read_only",
                allowed_effects=["legacy_readback_registered"],
                forbidden_effects=list(LEGACY_GATEWAY_FORBIDDEN_EFFECTS),
            ),
            allowed_evidence=("real_cad_readback",),
            boundary="registration only; no DWG read in this package; created handles required for geometry",
        ),
    }


def build_legacy_tool_contract(
    *,
    task: TaskObject,
    adapter: LegacyGatewayAdapter,
    requested_effects: list[str] | None = None,
) -> ToolContract:
    inputs = task.inputs if isinstance(task.inputs, dict) else {}
    tool_call_id = str(inputs.get("toolCallId") or f"{task.task_id}.{adapter.adapter_id}")
    effects = list(requested_effects) if requested_effects is not None else list(adapter.tool_card.allowed_effects)
    return ToolContract(
        tool_call_id=tool_call_id,
        task_id=task.task_id,
        tool_id=adapter.tool_card.tool_id,
        operation=adapter.operation,
        permission_class=adapter.tool_card.permission_class,
        requested_effects=effects,
        evidence_required=list(adapter.allowed_evidence),
        target_scope=dict(task.target_scope),
        dry_run_required=adapter.operation == "dry_run",
        readback_required=adapter.operation == "readback",
        save_allowed=False,
        descriptive_only=True,
    )


def build_legacy_validate_request(*, contract: ToolContract, cad_plan: dict[str, Any]) -> dict[str, Any]:
    adapter = legacy_gateway_adapter_cards()["legacy.validate"]
    return _legacy_request_from_contract(contract=contract, adapter=adapter, cad_plan=cad_plan)


def build_legacy_dry_run_request(*, contract: ToolContract, cad_plan: dict[str, Any]) -> dict[str, Any]:
    adapter = legacy_gateway_adapter_cards()["legacy.dry_run"]
    return _legacy_request_from_contract(contract=contract, adapter=adapter, cad_plan=cad_plan)


def build_legacy_preview_request(*, contract: ToolContract, cad_plan: dict[str, Any]) -> dict[str, Any]:
    adapter = legacy_gateway_adapter_cards()["legacy.preview"]
    request = _legacy_request_from_contract(contract=contract, adapter=adapter, cad_plan=cad_plan)
    request.update(
        {
            "layer": _preview_layer_from_plan(cad_plan),
            "savedCurrentDwg": False,
        }
    )
    return request


def build_legacy_readback_request(*, contract: ToolContract, readback_report: dict[str, Any]) -> dict[str, Any]:
    adapter = legacy_gateway_adapter_cards()["legacy.readback"]
    return {
        "tool_call_id": contract.tool_call_id,
        "task_id": contract.task_id,
        "tool_id": contract.tool_id,
        "operation": contract.operation,
        "permission_class": contract.permission_class,
        "legacy_entrypoint": adapter.legacy_entrypoint,
        "boundary": adapter.boundary,
        "created_handles": _created_handles(readback_report),
        "descriptive_only": contract.descriptive_only,
        "save_allowed": contract.save_allowed,
        "readback_required": contract.readback_required,
        "executes_cad": False,
        "reads_dwg": False,
        "writes_dwg": False,
        "saves_dwg": False,
        "savedCurrentDwg": False,
    }


def run_legacy_validate_dry_run_adapters(
    *,
    task: TaskObject,
    model_text: str | None = None,
) -> LegacyValidateDryRunAdapterResult:
    """Wrap legacy CAD_PLAN validate/dry-run entrypoints without CAD execution."""

    from core.plan_engine.dry_run_report import create_dry_run_report
    from core.plan_engine.validate_plan import validate_plan

    adapters = legacy_gateway_adapter_cards()
    validate_adapter = adapters["legacy.validate"]
    dry_run_adapter = adapters["legacy.dry_run"]
    cad_plan_candidate = cad_plan_candidate_from_task(task)

    validate_contract = build_legacy_tool_contract(task=task, adapter=validate_adapter)
    dry_run_contract = build_legacy_tool_contract(task=task, adapter=dry_run_adapter)
    validate_authorization = validate_adapter.tool_card.authorize(validate_contract)
    dry_run_authorization = dry_run_adapter.tool_card.authorize(dry_run_contract)
    validate_request = build_legacy_validate_request(contract=validate_contract, cad_plan=cad_plan_candidate)
    dry_run_request = build_legacy_dry_run_request(contract=dry_run_contract, cad_plan=cad_plan_candidate)

    validation_errors = [str(item) for item in validate_plan(validate_request["cad_plan"])]
    if validation_errors:
        dry_run_result: dict[str, Any] = {
            "version": "0.1",
            "status": "invalid",
            "validation_errors": validation_errors,
            "human_summary": "Legacy CAD_PLAN dry-run not attempted because validate failed.",
        }
    else:
        try:
            dry_run_result = create_dry_run_report(dry_run_request["cad_plan"])
        except Exception as exc:  # pragma: no cover - exception shape depends on legacy fixture
            dry_run_result = {
                "version": "0.1",
                "status": "error",
                "validation_errors": [],
                "error": f"{type(exc).__name__}: {exc}",
                "human_summary": "Legacy CAD_PLAN dry-run failed before CAD execution.",
            }

    evidence = legacy_validate_dry_run_evidence_package(
        task_id=task.task_id,
        validation_errors=validation_errors,
        dry_run_result=dry_run_result,
        model_text=model_text,
    )
    completion = CompletionJudge().judge(task=task, evidence=evidence)

    blocking_reasons: list[str] = []
    for authorization in (validate_authorization, dry_run_authorization):
        if authorization.status != "allowed":
            blocking_reasons.extend(authorization.reasons)
    if validation_errors:
        blocking_reasons.append(f"validate failed: {'; '.join(validation_errors)}")
    if not evidence.satisfies("cad_plan_dry_run"):
        dry_reason = str(dry_run_result.get("error") or dry_run_result.get("status") or "unknown")
        blocking_reasons.append(f"dry-run failed: {dry_reason}")
    if completion.status == "blocked":
        blocking_reasons.extend(f"missing evidence: {item}" for item in completion.missing_evidence)

    if blocking_reasons:
        status = "blocked"
        completion = CompletionDecision(
            status="blocked",
            verification_status="not_verified",
            missing_evidence=completion.missing_evidence,
            checked_evidence=completion.checked_evidence,
            can_claim_complete=False,
        )
    elif completion.status == "not_verified":
        status = "not_verified"
    else:
        status = "contract_ready_non_cad"
        completion = CompletionDecision(
            status="contract_ready_non_cad",
            verification_status="not_verified",
            missing_evidence=[],
            checked_evidence=completion.checked_evidence,
            can_claim_complete=False,
        )

    adapter_ready = (
        validate_authorization.status == "allowed"
        and dry_run_authorization.status == "allowed"
        and evidence.satisfies("legacy_gateway_adapter")
    )
    allowed_claims = ["contract_ready_non_cad"] if adapter_ready else []
    not_proven = [
        "real_cad_readback",
        "created_handles_readback",
        "geometry_verified",
        "cad_preview_written",
    ]
    return LegacyValidateDryRunAdapterResult(
        status=status,
        verification_status="not_verified",
        task=task,
        cad_plan_candidate=cad_plan_candidate,
        validate_adapter=validate_adapter,
        dry_run_adapter=dry_run_adapter,
        validate_contract=validate_contract,
        dry_run_contract=dry_run_contract,
        validate_authorization=validate_authorization,
        dry_run_authorization=dry_run_authorization,
        validate_request=validate_request,
        dry_run_request=dry_run_request,
        validation_errors=validation_errors,
        dry_run_result=dry_run_result,
        evidence=evidence,
        completion=completion,
        missing_evidence=list(completion.missing_evidence),
        blocking_reasons=list(dict.fromkeys(blocking_reasons)),
        allowed_claims=allowed_claims,
        not_proven=not_proven,
        cad_geometry_verified=False,
    )


def run_legacy_preview_registration(
    *,
    task: TaskObject,
    requested_effects: list[str] | None = None,
    model_text: str | None = None,
) -> LegacyRegistrationGuardResult:
    """Register a legacy preview request without executing CAD or writing DWG."""

    adapter = legacy_gateway_adapter_cards()["legacy.preview"]
    cad_plan_candidate = cad_plan_candidate_from_task(task)
    tool_contract = build_legacy_tool_contract(task=task, adapter=adapter, requested_effects=requested_effects)
    authorization = adapter.tool_card.authorize(tool_contract)
    request = build_legacy_preview_request(contract=tool_contract, cad_plan=cad_plan_candidate)

    blocking_reasons: list[str] = []
    if authorization.status != "allowed":
        blocking_reasons.extend(authorization.reasons)
    layer = str(request.get("layer") or "")
    if layer != PREVIEW_LAYER:
        blocking_reasons.append("preview layer must be CODEX_PREVIEW")

    evidence = legacy_preview_registration_evidence_package(
        task_id=task.task_id,
        layer=layer,
        registered=not blocking_reasons,
        model_text=model_text,
    )
    completion = CompletionJudge().judge(task=task, evidence=evidence)
    if completion.status == "blocked":
        blocking_reasons.extend(f"missing evidence: {item}" for item in completion.missing_evidence)

    if blocking_reasons:
        status = "blocked"
        completion = CompletionDecision(
            status="blocked",
            verification_status="not_verified",
            missing_evidence=completion.missing_evidence,
            checked_evidence=completion.checked_evidence,
            can_claim_complete=False,
        )
    else:
        status = "preview_registered_non_cad"
        completion = CompletionDecision(
            status="preview_registered_non_cad",
            verification_status="not_verified",
            missing_evidence=[],
            checked_evidence=completion.checked_evidence,
            can_claim_complete=False,
        )

    registered = status == "preview_registered_non_cad"
    return LegacyRegistrationGuardResult(
        status=status,
        verification_status="not_verified",
        task=task,
        adapter=adapter,
        tool_contract=tool_contract,
        authorization=authorization,
        request=request,
        evidence=evidence,
        completion=completion,
        missing_evidence=list(completion.missing_evidence),
        blocking_reasons=list(dict.fromkeys(blocking_reasons)),
        allowed_claims=["preview_registered_non_cad"] if registered else [],
        not_proven=[
            "cad_preview_written",
            "real_cad_readback",
            "created_handles_readback",
            "geometry_verified",
        ],
        cad_geometry_verified=False,
    )


def run_legacy_readback_registration(
    *,
    task: TaskObject,
    readback_report: dict[str, Any],
    requested_effects: list[str] | None = None,
    model_text: str | None = None,
) -> LegacyRegistrationGuardResult:
    """Register legacy readback evidence without reading a DWG."""

    adapter = legacy_gateway_adapter_cards()["legacy.readback"]
    tool_contract = build_legacy_tool_contract(task=task, adapter=adapter, requested_effects=requested_effects)
    authorization = adapter.tool_card.authorize(tool_contract)
    request = build_legacy_readback_request(contract=tool_contract, readback_report=readback_report)
    handles = _created_handles(readback_report)

    evidence = legacy_readback_registration_evidence_package(
        task_id=task.task_id,
        readback_report=readback_report,
        registered=authorization.status == "allowed",
        model_text=model_text,
    )
    completion = CompletionJudge().judge(task=task, evidence=evidence)
    cad_verified = evidence.satisfies("real_cad_readback")

    blocking_reasons: list[str] = []
    if authorization.status != "allowed":
        blocking_reasons.extend(authorization.reasons)
    if not handles:
        blocking_reasons.append("created handles are required before legacy readback can verify geometry")
    if completion.status == "blocked":
        blocking_reasons.extend(f"missing evidence: {item}" for item in completion.missing_evidence)

    status = completion.status
    if blocking_reasons:
        status = "blocked"
        completion = CompletionDecision(
            status="blocked",
            verification_status="not_verified",
            missing_evidence=completion.missing_evidence,
            checked_evidence=completion.checked_evidence,
            can_claim_complete=False,
        )

    return LegacyRegistrationGuardResult(
        status=status,
        verification_status="verified" if cad_verified else "not_verified",
        task=task,
        adapter=adapter,
        tool_contract=tool_contract,
        authorization=authorization,
        request=request,
        evidence=evidence,
        completion=completion,
        missing_evidence=list(completion.missing_evidence),
        blocking_reasons=list(dict.fromkeys(blocking_reasons)),
        allowed_claims=["real_cad_readback"] if cad_verified else [],
        not_proven=[] if cad_verified else ["real_cad_readback", "created_handles_readback", "geometry_verified"],
        cad_geometry_verified=cad_verified,
    )


def legacy_validate_evidence_package(
    *,
    task_id: str,
    validation_errors: list[str],
) -> EvidencePackage:
    validate_pass = not validation_errors
    return EvidencePackage(
        task_id=task_id,
        items=[
            EvidenceItem(
                kind="cad_plan_validate",
                status="pass" if validate_pass else "fail",
                backend="legacy_validate",
                metadata={
                    "errors": list(validation_errors),
                    "proves": "schema and CAD_PLAN legality only",
                    "boundary": "validate pass does not prove dry-run, preview, readback, or geometry",
                },
            )
        ],
    )


def legacy_dry_run_evidence_package(
    *,
    task_id: str,
    dry_run_result: dict[str, Any],
) -> EvidencePackage:
    dry_run_errors = _text_list(dry_run_result.get("validation_errors"))
    dry_run_status = str(dry_run_result.get("status") or "").casefold()
    dry_run_pass = dry_run_status in {"valid", "pass", "ok", "ready"} and not dry_run_errors and not dry_run_result.get(
        "error"
    )
    return EvidencePackage(
        task_id=task_id,
        items=[
            EvidenceItem(
                kind="cad_plan_dry_run",
                status="pass" if dry_run_pass else "fail",
                backend="legacy_dry_run",
                metadata={
                    "dryRunStatus": str(dry_run_result.get("status") or ""),
                    "validationErrors": dry_run_errors,
                    "error": str(dry_run_result.get("error") or ""),
                    "proves": "dry-run feasibility only",
                    "boundary": "dry-run pass does not prove preview write, readback, or geometry",
                },
            )
        ],
    )


def legacy_validate_dry_run_evidence_package(
    *,
    task_id: str,
    validation_errors: list[str],
    dry_run_result: dict[str, Any],
    model_text: str | None = None,
) -> EvidencePackage:
    items = [
        *legacy_validate_evidence_package(task_id=task_id, validation_errors=validation_errors).items,
        *legacy_dry_run_evidence_package(task_id=task_id, dry_run_result=dry_run_result).items,
    ]
    adapter_pass = all(item.status == "pass" for item in items)
    items.extend(
        [
            EvidenceItem(
                kind="legacy_gateway_adapter",
                status="pass" if adapter_pass else "fail",
                backend="legacy_gateway",
                metadata={
                    "boundary": "legacy validate/dry-run adapter evidence contains no created handles readback",
                    "proves": "contract_ready_non_cad only",
                },
            ),
            EvidenceItem(
                kind="no_save_guard",
                status="pass",
                backend="legacy_gateway",
                metadata={
                    "savedCurrentDwg": False,
                    "boundary": "adapter does not call preview, AutoCAD, CAD-MCP, plugins, or save DWG",
                },
            ),
        ]
    )
    if model_text is not None:
        items.append(
            EvidenceItem(
                kind="model_text",
                status="informational",
                metadata={
                    "text": str(model_text),
                    "boundary": "model text cannot override deterministic legacy gateway evidence",
                },
            )
        )
    return EvidencePackage(task_id=task_id, items=items)


def legacy_preview_registration_evidence_package(
    *,
    task_id: str,
    layer: str,
    registered: bool,
    model_text: str | None = None,
) -> EvidencePackage:
    items = [
        EvidenceItem(
            kind="legacy_preview_registered",
            status="pass" if registered else "fail",
            backend="legacy_gateway",
            metadata={
                "layer": str(layer),
                "savedCurrentDwg": False,
                "proves": "preview registration only",
                "boundary": "preview registered does not write CAD or prove readback",
            },
        ),
        EvidenceItem(
            kind="no_save_guard",
            status="pass",
            backend="legacy_gateway",
            metadata={
                "savedCurrentDwg": False,
                "boundary": "preview registration does not save or modify DWG",
            },
        ),
    ]
    if model_text is not None:
        items.append(
            EvidenceItem(
                kind="model_text",
                status="informational",
                metadata={
                    "text": str(model_text),
                    "boundary": "model text cannot turn preview registration into CAD write evidence",
                },
            )
        )
    return EvidencePackage(task_id=task_id, items=items)


def legacy_readback_registration_evidence_package(
    *,
    task_id: str,
    readback_report: dict[str, Any],
    registered: bool,
    model_text: str | None = None,
) -> EvidencePackage:
    handles = _created_handles(readback_report)
    items = [
        EvidenceItem(
            kind="legacy_readback_registered",
            status="pass" if registered else "fail",
            backend="legacy_gateway",
            metadata={
                "created_handles": handles,
                "proves": "readback registration only",
                "boundary": "created handles are required before geometry can be verified",
            },
        ),
        *legacy_readback_evidence_package(task_id=task_id, readback_report=readback_report).items,
        EvidenceItem(
            kind="no_save_guard",
            status="pass",
            backend="legacy_gateway",
            metadata={
                "savedCurrentDwg": False,
                "boundary": "readback registration does not save or modify DWG",
            },
        ),
    ]
    if model_text is not None:
        items.append(
            EvidenceItem(
                kind="model_text",
                status="informational",
                metadata={
                    "text": str(model_text),
                    "boundary": "model text cannot replace created handles readback evidence",
                },
            )
        )
    return EvidencePackage(task_id=task_id, items=items)


def legacy_readback_evidence_package(
    *,
    task_id: str,
    readback_report: dict[str, Any],
) -> EvidencePackage:
    handles = _created_handles(readback_report)
    has_handles = bool(handles)
    status = str(readback_report.get("status") or "")
    backend = str(
        readback_report.get("backend")
        or readback_report.get("evidenceSource")
        or readback_report.get("evidence_source")
        or ""
    )
    readback_status = str(readback_report.get("readbackStatus") or readback_report.get("readback_status") or "")
    geometry_verified = status == "geometry_verified" and has_handles
    return EvidencePackage(
        task_id=task_id,
        items=[
            EvidenceItem(
                kind="cad_readback",
                status="pass" if geometry_verified else "fail",
                backend=backend,
                readback_status=readback_status,
                cad_geometry_verified=geometry_verified,
                metadata={
                    "created_handles": handles,
                    "readbackStatus": readback_status,
                    "sourceStatus": status,
                    "boundary": "created handles are required before geometry can be verified",
                },
            )
        ],
    )


def legacy_non_readback_evidence_package(
    *,
    task_id: str,
    include_model_text: str | None = None,
) -> EvidencePackage:
    items = [
        EvidenceItem(kind="dry_run", status="pass", backend="dry_run"),
        EvidenceItem(kind="screenshot", status="pass", metadata={"role": "visual_aid_only"}),
        EvidenceItem(kind="no_save_guard", status="pass", metadata={"savedCurrentDwg": False}),
    ]
    if include_model_text is not None:
        items.append(
            EvidenceItem(
                kind="model_text",
                status="informational",
                metadata={
                    "text": str(include_model_text),
                    "boundary": "model text cannot replace legacy readback evidence",
                },
            )
        )
    return EvidencePackage(task_id=task_id, items=items)


def legacy_gateway_phase6_closeout_summary() -> dict[str, Any]:
    """Summarize Phase 6 gateway readiness without executing CAD or reading DWG."""

    adapters = legacy_gateway_adapter_cards()
    adapter_summaries: dict[str, dict[str, Any]] = {}
    for adapter_id, adapter in adapters.items():
        task = TaskObject(
            task_id=f"phase6-closeout-{adapter.operation}",
            task_kind="legacy_gateway_phase6_closeout",
            user_intent="Inspect legacy gateway registration boundary.",
            evidence_requirements=list(adapter.allowed_evidence),
        )
        contract = build_legacy_tool_contract(task=task, adapter=adapter)
        decision = adapter.tool_card.authorize(contract)
        adapter_summaries[adapter_id] = {
            "tool_contract_status": decision.status,
            "has_tool_card": adapter.tool_card.tool_id == adapter_id,
            "has_permission_class": bool(adapter.tool_card.permission_class),
            "has_evidence_boundary": bool(adapter.allowed_evidence),
            "permission_class": adapter.tool_card.permission_class,
            "allowed_evidence": list(adapter.allowed_evidence),
            "executes_cad": adapter.executes_cad,
            "writes_dwg": adapter.writes_dwg,
            "saves_dwg": adapter.saves_dwg,
            "mutates_registry": adapter.mutates_registry,
            "advances_table_c": adapter.advances_table_c,
        }

    no_handles_evidence = legacy_readback_evidence_package(
        task_id="phase6-closeout-no-handles",
        readback_report={
            "status": "geometry_verified",
            "backend": "real_cad",
            "readbackStatus": "ok",
            "actual": {"created_handles": []},
        },
    )
    non_readback_evidence = legacy_non_readback_evidence_package(
        task_id="phase6-closeout-non-readback",
        include_model_text="Dry-run, screenshot, and model text cannot verify CAD geometry.",
    )
    ready = (
        set(adapters) == {"legacy.validate", "legacy.dry_run", "legacy.preview", "legacy.readback"}
        and all(item["tool_contract_status"] == "allowed" for item in adapter_summaries.values())
        and all(item["has_tool_card"] for item in adapter_summaries.values())
        and all(item["has_permission_class"] for item in adapter_summaries.values())
        and all(item["has_evidence_boundary"] for item in adapter_summaries.values())
        and not no_handles_evidence.satisfies("real_cad_readback")
        and not non_readback_evidence.satisfies("real_cad_readback")
    )
    return {
        "status": "phase6_closeout_ready" if ready else "blocked",
        "next_phase": "Phase 7: Evidence Ledger",
        "adapter_ids": sorted(adapters),
        "adapters": adapter_summaries,
        "bypasses_phase5_contracts": False,
        "cad_execution_invoked": False,
        "dwg_written_or_saved": False,
        "protected_evidence_mutated": False,
        "completion_judge_distinctions": {
            "schema_plan_valid": "cad_plan_validate",
            "dry_run_feasible": "cad_plan_dry_run",
            "preview_registered": "legacy_preview_registered",
            "readback_verified": "real_cad_readback",
            "geometry_verified": "created_handles_real_cad_readback",
        },
        "no_handles_can_geometry_verify": no_handles_evidence.satisfies("real_cad_readback"),
        "non_readback_evidence_can_masquerade": non_readback_evidence.satisfies("real_cad_readback"),
    }


def _created_handles(readback_report: dict[str, Any]) -> list[str]:
    direct = readback_report.get("created_handles", readback_report.get("createdHandles"))
    if direct is None and isinstance(readback_report.get("actual"), dict):
        actual = readback_report["actual"]
        direct = actual.get("created_handles", actual.get("createdHandles"))
    if not isinstance(direct, list):
        return []
    return [str(handle) for handle in direct if str(handle)]


def _legacy_request_from_contract(
    *,
    contract: ToolContract,
    adapter: LegacyGatewayAdapter,
    cad_plan: dict[str, Any],
) -> dict[str, Any]:
    return {
        "tool_call_id": contract.tool_call_id,
        "task_id": contract.task_id,
        "tool_id": contract.tool_id,
        "operation": contract.operation,
        "permission_class": contract.permission_class,
        "legacy_entrypoint": adapter.legacy_entrypoint,
        "cad_plan": dict(cad_plan),
        "boundary": adapter.boundary,
        "descriptive_only": contract.descriptive_only,
        "save_allowed": contract.save_allowed,
        "readback_required": contract.readback_required,
        "executes_cad": False,
        "writes_dwg": False,
        "saves_dwg": False,
    }


def _preview_layer_from_plan(cad_plan: dict[str, Any]) -> str:
    drawing = cad_plan.get("drawing")
    if isinstance(drawing, dict) and drawing.get("layer"):
        return str(drawing.get("layer"))
    return PREVIEW_LAYER


def _text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value if str(item)]
    text = str(value)
    return [text] if text else []
