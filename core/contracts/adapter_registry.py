"""Phase 11-14 ToolCard and adapter registry intake.

The registry sits behind the Tool Gateway and in front of concrete adapters.
It registers existing harness, cad-session-host, and legacy preview/readback
paths as bounded adapters, plus the Phase 12 mock plugin-like transaction
adapter, Phase 13 native thin backend skeleton / preflight / authorization
packets / readiness authorization requests, and the P13F scoped native live
spike adapter. Phase 14 adds the no-CAD Engineering Kernel DiffPackage adapter.
It never allows generic native_plugin_execute/cad_execute/dwg_save effects to
bypass ToolCard / ToolContract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.contracts.legacy_gateway import legacy_gateway_adapter_cards
from core.contracts.engineering_kernel import (
    P14_ENGINEERING_KERNEL_ALLOWED_EFFECTS,
    P14_ENGINEERING_KERNEL_FORBIDDEN_EFFECTS,
)
from core.contracts.mock_plugin_transaction import (
    P12_TRANSACTION_ALLOWED_EFFECTS,
    P12_TRANSACTION_FORBIDDEN_EFFECTS,
)
from core.contracts.native_thin_backend import (
    P13_NATIVE_LIVE_ALLOWED_EFFECTS,
    P13_NATIVE_LIVE_FORBIDDEN_EFFECTS,
    P13_NATIVE_ALLOWED_EFFECTS,
    P13_NATIVE_FORBIDDEN_EFFECTS,
)
from core.contracts.phase10_rehearsal import PHASE10_FORBIDDEN_EFFECTS
from core.contracts.vnext import (
    CompletionDecision,
    CompletionJudge,
    ContractDecision,
    EvidenceItem,
    EvidencePackage,
    TaskObject,
    ToolCard,
    ToolContract,
)
from core.safety.policy import PREVIEW_LAYER


P11_ADAPTER_REGISTRY_SCHEMA = "tool-adapter-registry/p11/v1"
HARNESS_RESULT_SCHEMA = "cad-agent-harness-result/v1"

P11_FORBIDDEN_EFFECTS = tuple(
    dict.fromkeys(
        [
            "cad_execute",
            *PHASE10_FORBIDDEN_EFFECTS,
        ]
    )
)


@dataclass(frozen=True)
class RegisteredAdapter:
    adapter_id: str
    operation: str
    entrypoint: str
    tool_card: ToolCard
    command: str = ""
    backend: str = ""
    allowed_evidence: tuple[str, ...] = field(default_factory=tuple)
    boundary: str = "registered_adapter_only"
    consumes_harness_result: bool = False
    executes_cad: bool = False
    reads_dwg: bool = False
    writes_dwg: bool = False
    saves_dwg: bool = False
    mutates_registry: bool = False
    advances_table_c: bool = False
    calls_plugin: bool = False


@dataclass(frozen=True)
class AdapterAuthorizationResult:
    status: str
    adapter: RegisteredAdapter
    tool_contract: ToolContract
    authorization: ContractDecision
    blocking_reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class HarnessResultConsumptionResult:
    status: str
    verification_status: str
    adapter: RegisteredAdapter
    tool_contract: ToolContract
    authorization: ContractDecision
    evidence: EvidencePackage
    completion: CompletionDecision
    missing_evidence: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)
    allowed_claims: list[str] = field(default_factory=list)
    not_proven: list[str] = field(default_factory=list)
    cad_geometry_verified: bool = False
    cad_writes_attempted: bool = False
    source_cad_writes_attempted: bool = False


def default_adapter_registry() -> dict[str, RegisteredAdapter]:
    """Return the P11 in-memory adapter registry."""

    registry: dict[str, RegisteredAdapter] = {}
    registry.update(_legacy_registered_adapters())
    registry.update(_harness_registered_adapters())
    registry.update(_cad_session_host_registered_adapters())
    registry.update(_mock_plugin_registered_adapters())
    registry.update(_native_thin_registered_adapters())
    registry.update(_engineering_kernel_registered_adapters())
    return dict(sorted(registry.items()))


def adapter_for_harness_command(
    *,
    command: str,
    backend: str = "none",
    adapter_id: str | None = None,
) -> RegisteredAdapter:
    registry = default_adapter_registry()
    if adapter_id:
        return registry[str(adapter_id)]

    normalized_command = str(command).strip()
    normalized_backend = _normalize_backend(backend)
    if normalized_command == "preview" and normalized_backend in {"none", "cad-session-host", "cad_session_host"}:
        return registry["cad-session-host.preview"]
    if normalized_command == "readback" and normalized_backend in {"cad-session-host", "cad_session_host"}:
        return registry["cad-session-host.readback"]
    if normalized_command == "mock-plugin-transaction" and normalized_backend in {
        "none",
        "mock-plugin-like",
        "mock_plugin_like",
    }:
        return registry["mock-plugin.transaction"]
    if normalized_command == "native-thin-backend" and normalized_backend in {
        "none",
        "native-thin-skeleton",
        "native_thin_skeleton",
    }:
        return registry["native-thin.backend"]
    if normalized_command == "native-thin-live-spike" and normalized_backend in {
        "none",
        "native-thin-live-backend",
        "native_thin_live_backend",
    }:
        return registry["native-thin.live-spike"]
    if normalized_command == "engineering-kernel-diff" and normalized_backend in {
        "none",
        "engineering-kernel",
        "engineering_kernel",
    }:
        return registry["engineering-kernel.diff-package"]

    registry_id = f"harness.{normalized_command}"
    return registry[registry_id]


def authorize_harness_command(
    *,
    command: str,
    backend: str = "none",
    requested_effects: list[str] | None = None,
    adapter_id: str | None = None,
    task_id: str = "phase11.tool-gateway.adapter-request",
) -> AdapterAuthorizationResult:
    adapter = adapter_for_harness_command(command=command, backend=backend, adapter_id=adapter_id)
    return authorize_registered_adapter(
        adapter_id=adapter.adapter_id,
        task_id=task_id,
        requested_effects=requested_effects,
    )


def authorize_registered_adapter(
    *,
    adapter_id: str,
    task_id: str,
    requested_effects: list[str] | None = None,
    target_scope: dict[str, Any] | None = None,
) -> AdapterAuthorizationResult:
    adapter = default_adapter_registry()[str(adapter_id)]
    contract = build_tool_contract_for_adapter(
        adapter=adapter,
        task_id=task_id,
        requested_effects=requested_effects,
        target_scope=target_scope,
    )
    authorization = adapter.tool_card.authorize(contract)
    return AdapterAuthorizationResult(
        status=authorization.status,
        adapter=adapter,
        tool_contract=contract,
        authorization=authorization,
        blocking_reasons=list(authorization.reasons),
    )


def build_tool_contract_for_adapter(
    *,
    adapter: RegisteredAdapter,
    task_id: str,
    requested_effects: list[str] | None = None,
    target_scope: dict[str, Any] | None = None,
) -> ToolContract:
    effects = list(requested_effects) if requested_effects is not None else list(adapter.tool_card.allowed_effects)
    return ToolContract(
        tool_call_id=f"{task_id}.{adapter.adapter_id}",
        task_id=str(task_id),
        tool_id=adapter.tool_card.tool_id,
        operation=adapter.operation,
        permission_class=adapter.tool_card.permission_class,
        requested_effects=effects,
        evidence_required=list(adapter.allowed_evidence),
        target_scope=dict(target_scope or {}),
        dry_run_required=adapter.operation == "dry_run",
        readback_required="real_cad_readback" in adapter.allowed_evidence,
        save_allowed=False,
        descriptive_only=not adapter.executes_cad,
    )


def annotate_harness_result_with_registry(
    result: dict[str, Any],
    authorization_result: AdapterAuthorizationResult,
) -> dict[str, Any]:
    payload = dict(result)
    payload["adapterId"] = authorization_result.adapter.adapter_id
    payload["registeredAdapter"] = _adapter_payload(authorization_result.adapter)
    payload["registryAdapter"] = _adapter_payload(authorization_result.adapter)
    payload["toolCard"] = _tool_card_payload(authorization_result.adapter.tool_card)
    payload["toolContract"] = _tool_contract_payload(authorization_result.tool_contract)
    payload["registryAuthorization"] = _authorization_payload(authorization_result.authorization)
    payload["gatewayBoundary"] = authorization_result.adapter.boundary
    return payload


def blocked_harness_result_for_authorization(
    *,
    command: str,
    backend: str,
    authorization_result: AdapterAuthorizationResult,
) -> dict[str, Any]:
    adapter = authorization_result.adapter
    return annotate_harness_result_with_registry(
        {
            "schemaVersion": HARNESS_RESULT_SCHEMA,
            "command": str(command),
            "status": "blocked",
            "verificationStatus": "not_verified",
            "taskId": authorization_result.tool_contract.task_id,
            "toolCallId": authorization_result.tool_contract.tool_call_id,
            "backend": backend if backend != "none" else adapter.backend or "none",
            "targetLayer": PREVIEW_LAYER,
            "savedCurrentDwg": False,
            "cadGeometryVerified": False,
            "createdHandles": [],
            "readbackEntities": [],
            "evidencePackageRef": "",
            "blockingReasons": list(authorization_result.blocking_reasons),
            "missingEvidence": list(authorization_result.tool_contract.evidence_required),
            "validationErrors": [],
            "safety": {
                "saveAllowed": False,
                "deleteAllowed": False,
                "formalLayersAllowed": False,
                "connectExistingOnly": True,
            },
            "allowedEffects": list(adapter.tool_card.allowed_effects),
            "forbiddenEffects": list(adapter.tool_card.forbidden_effects),
            "artifacts": {},
            "cadWritesAttempted": False,
            "nativePluginInvoked": False,
        },
        authorization_result,
    )


def consume_harness_result_via_registry(
    harness_result: dict[str, Any],
    *,
    adapter_id: str | None = None,
) -> HarnessResultConsumptionResult:
    payload = dict(harness_result if isinstance(harness_result, dict) else {})
    command = str(payload.get("command") or "")
    backend = str(payload.get("backend") or "none")
    try:
        adapter = adapter_for_harness_command(command=command, backend=backend, adapter_id=adapter_id)
    except KeyError:
        adapter = default_adapter_registry()["harness.rehearsal-result"]
        authorization = authorize_registered_adapter(
            adapter_id=adapter.adapter_id,
            task_id=str(payload.get("taskId") or "phase11.harness-result-consumption"),
        )
        return _blocked_consumption_result(
            adapter=adapter,
            authorization=authorization,
            payload=payload,
            blockers=["harness_result_adapter_not_registered"],
        )

    authorization = authorize_registered_adapter(
        adapter_id=adapter.adapter_id,
        task_id=str(payload.get("taskId") or "phase11.harness-result-consumption"),
    )
    blockers = list(authorization.blocking_reasons)
    if payload.get("schemaVersion") != HARNESS_RESULT_SCHEMA:
        blockers.append("harness_result_schema_invalid")
    if not adapter.consumes_harness_result:
        blockers.append("adapter_does_not_consume_harness_result")
    if adapter.command and command != adapter.command:
        blockers.append("harness_result_command_mismatch")
    if str(payload.get("status") or "") != "ready":
        blockers.append("harness_result_status_not_ready")
    if _bool(payload.get("cadWritesAttempted")):
        blockers.append("harness_result_consumer_must_be_read_only")
    blockers.extend(_string_list(payload.get("blockingReasons")))
    missing_evidence = _string_list(payload.get("missingEvidence"))

    source_cad_writes_attempted = _bool(payload.get("sourceCadWritesAttempted"))
    cad_writes_attempted = _bool(payload.get("cadWritesAttempted"))
    cad_geometry_verified = (
        not blockers
        and not missing_evidence
        and payload.get("cadGeometryVerified") is True
        and str(payload.get("verificationStatus") or "") == "verified"
    )
    evidence = _harness_result_evidence_package(
        task_id=str(payload.get("taskId") or authorization.tool_contract.task_id),
        adapter=adapter,
        payload=payload,
        cad_geometry_verified=cad_geometry_verified,
    )
    task = TaskObject(
        task_id=authorization.tool_contract.task_id,
        task_kind="phase11_harness_result_consumption",
        user_intent="Consume an existing harness result through the P11 adapter registry.",
        evidence_requirements=list(adapter.allowed_evidence),
    )
    completion = CompletionJudge().judge(task=task, evidence=evidence)
    if completion.status == "blocked":
        missing_evidence.extend(completion.missing_evidence)
    if blockers or missing_evidence:
        return HarnessResultConsumptionResult(
            status="blocked",
            verification_status="not_verified",
            adapter=adapter,
            tool_contract=authorization.tool_contract,
            authorization=authorization.authorization,
            evidence=evidence,
            completion=CompletionDecision(
                status="blocked",
                verification_status="not_verified",
                missing_evidence=_unique(missing_evidence),
                checked_evidence=completion.checked_evidence,
                can_claim_complete=False,
            ),
            missing_evidence=_unique(missing_evidence),
            blocking_reasons=_unique(blockers),
            allowed_claims=[],
            not_proven=_not_proven(),
            cad_geometry_verified=False,
            cad_writes_attempted=cad_writes_attempted,
            source_cad_writes_attempted=source_cad_writes_attempted,
        )

    claim = _consumption_claim_for_adapter(adapter)
    return HarnessResultConsumptionResult(
        status="ready",
        verification_status="verified" if cad_geometry_verified else "not_verified",
        adapter=adapter,
        tool_contract=authorization.tool_contract,
        authorization=authorization.authorization,
        evidence=evidence,
        completion=completion,
        missing_evidence=[],
        blocking_reasons=[],
        allowed_claims=[claim] if claim else [],
        not_proven=_not_proven(),
        cad_geometry_verified=cad_geometry_verified,
        cad_writes_attempted=cad_writes_attempted,
        source_cad_writes_attempted=source_cad_writes_attempted,
    )


def _legacy_registered_adapters() -> dict[str, RegisteredAdapter]:
    result: dict[str, RegisteredAdapter] = {}
    for adapter_id, legacy in legacy_gateway_adapter_cards().items():
        result[adapter_id] = RegisteredAdapter(
            adapter_id=adapter_id,
            operation=legacy.operation,
            entrypoint=legacy.legacy_entrypoint,
            tool_card=legacy.tool_card,
            command=legacy.operation,
            allowed_evidence=tuple(legacy.allowed_evidence),
            boundary=legacy.boundary,
            executes_cad=legacy.executes_cad,
            reads_dwg=legacy.reads_dwg,
            writes_dwg=legacy.writes_dwg,
            saves_dwg=legacy.saves_dwg,
            mutates_registry=legacy.mutates_registry,
            advances_table_c=legacy.advances_table_c,
        )
    return result


def _harness_registered_adapters() -> dict[str, RegisteredAdapter]:
    specs = [
        (
            "harness.validate",
            "validate",
            "validate",
            "deterministic_verify",
            ["cad_plan_validate"],
            ("cad_plan_validate",),
            "harness validate command behind Tool Gateway; no CAD execution",
            False,
        ),
        (
            "harness.dry-run",
            "dry-run",
            "dry_run",
            "deterministic_verify",
            ["cad_plan_dry_run"],
            ("cad_plan_dry_run",),
            "harness dry-run command behind Tool Gateway; no CAD execution",
            False,
        ),
        (
            "harness.probe",
            "probe",
            "probe",
            "read_only",
            ["harness_probe_result"],
            ("harness_probe_result",),
            "harness probe is a readiness summary; it does not touch AutoCAD",
            False,
        ),
        (
            "harness.bundle",
            "bundle",
            "bundle",
            "deterministic_verify",
            ["preview_bundle_write"],
            ("preview_bundle",),
            "preview bundle producer organizes existing artifacts only",
            False,
        ),
        (
            "harness.exit-gate",
            "exit-gate",
            "exit_gate",
            "read_only",
            ["phase9_exit_gate_consume"],
            ("phase9_exit_gate",),
            "Phase 9 exit gate consumes existing artifacts only",
            True,
        ),
        (
            "harness.rehearsal-scope-proposal",
            "rehearsal-scope-proposal",
            "rehearsal_scope_proposal",
            "deterministic_verify",
            ["phase10_rehearsal_scope_proposal_write"],
            ("phase10_rehearsal_scope_proposal",),
            "P10 scope proposal writes a review artifact only",
            False,
        ),
        (
            "harness.rehearsal-plan",
            "rehearsal-plan",
            "rehearsal_plan",
            "deterministic_verify",
            ["phase10_rehearsal_plan_write"],
            ("phase10_rehearsal_plan",),
            "P10 plan materializes run specs without CAD execution",
            False,
        ),
        (
            "harness.rehearsal-scope-receipt",
            "rehearsal-scope-receipt",
            "rehearsal_scope_receipt",
            "deterministic_verify",
            ["phase10_rehearsal_scope_receipt_write"],
            ("phase10_scope_confirmation_receipt",),
            "P10 receipt records operator confirmation without CAD execution",
            False,
        ),
        (
            "harness.rehearsal-preflight",
            "rehearsal-preflight",
            "rehearsal_preflight",
            "deterministic_verify",
            ["phase10_rehearsal_launch_packet_write"],
            ("phase10_rehearsal_launch_packet",),
            "P10 preflight emits an auditable launch packet only",
            False,
        ),
        (
            "harness.rehearsal-result",
            "rehearsal-result",
            "rehearsal_result",
            "read_only",
            ["phase10_rehearsal_result_consume"],
            ("phase10_rehearsal_result", "real_cad_readback", "no_save_guard"),
            "P10 result adapter consumes existing run readback summaries only",
            True,
        ),
        (
            "harness.rehearsal-closeout",
            "rehearsal-closeout",
            "rehearsal_closeout",
            "read_only",
            ["phase10_rehearsal_closeout_consume"],
            ("phase10_rehearsal_closeout", "real_cad_readback", "no_save_guard"),
            "P10 closeout adapter consumes existing closeout artifacts only",
            True,
        ),
        (
            "harness.rehearsal-run",
            "rehearsal-run",
            "rehearsal_run",
            "cad_preview",
            ["phase10_rehearsal_live_preview_runs"],
            ("real_cad_readback", "no_save_guard"),
            "P10 live run requires confirmed scope, session-host env, and no-save guard",
            False,
        ),
        (
            "harness.preview",
            "preview",
            "preview",
            "cad_preview",
            ["cad_preview_write", "created_handles_readback", "evidence_package_write"],
            ("real_cad_readback", "no_save_guard"),
            "generic harness preview remains behind ToolCard and ToolContract",
            False,
        ),
        (
            "harness.readback",
            "readback",
            "readback",
            "read_only",
            ["harness_readback_consume"],
            ("real_cad_readback", "no_save_guard"),
            "harness readback consumes an existing run directory",
            True,
        ),
        (
            "harness.evidence",
            "evidence",
            "evidence",
            "read_only",
            ["evidence_package_consume"],
            ("real_cad_readback", "no_save_guard"),
            "harness evidence consumes an existing run directory",
            True,
        ),
    ]
    result: dict[str, RegisteredAdapter] = {}
    for adapter_id, command, operation, permission, allowed, evidence, boundary, consumes in specs:
        executes = adapter_id in {"harness.preview", "harness.rehearsal-run"}
        result[adapter_id] = RegisteredAdapter(
            adapter_id=adapter_id,
            command=command,
            operation=operation,
            entrypoint="core.contracts.cad_agent_harness.run_harness_command",
            tool_card=ToolCard(
                tool_id=adapter_id,
                permission_class=permission,
                allowed_effects=list(allowed),
                forbidden_effects=list(P11_FORBIDDEN_EFFECTS),
            ),
            allowed_evidence=evidence,
            boundary=boundary,
            consumes_harness_result=consumes,
            executes_cad=executes,
            writes_dwg=False,
            saves_dwg=False,
        )
    return result


def _cad_session_host_registered_adapters() -> dict[str, RegisteredAdapter]:
    preview_card = ToolCard(
        tool_id="cad-session-host.preview",
        permission_class="cad_preview",
        allowed_effects=["cad_preview_write", "created_handles_readback", "evidence_package_write"],
        forbidden_effects=list(P11_FORBIDDEN_EFFECTS),
    )
    readback_card = ToolCard(
        tool_id="cad-session-host.readback",
        permission_class="read_only",
        allowed_effects=["created_handles_readback"],
        forbidden_effects=list(P11_FORBIDDEN_EFFECTS),
    )
    return {
        "cad-session-host.preview": RegisteredAdapter(
            adapter_id="cad-session-host.preview",
            command="preview",
            operation="preview",
            backend="cad-session-host",
            entrypoint="core.cad_io.cad_session_host.CadSessionHostClient",
            tool_card=preview_card,
            allowed_evidence=("real_cad_readback", "no_save_guard"),
            boundary="cad-session-host preview may only write CODEX_PREVIEW and must read back created handles",
            executes_cad=True,
            writes_dwg=False,
            saves_dwg=False,
        ),
        "cad-session-host.readback": RegisteredAdapter(
            adapter_id="cad-session-host.readback",
            command="readback",
            operation="readback",
            backend="cad-session-host",
            entrypoint="core.cad_io.cad_session_host.CadSessionHostClient",
            tool_card=readback_card,
            allowed_evidence=("real_cad_readback", "no_save_guard"),
            boundary="cad-session-host readback consumes created handles only",
            consumes_harness_result=True,
            executes_cad=False,
            reads_dwg=False,
            writes_dwg=False,
            saves_dwg=False,
        ),
    }


def _mock_plugin_registered_adapters() -> dict[str, RegisteredAdapter]:
    return {
        "mock-plugin.transaction": RegisteredAdapter(
            adapter_id="mock-plugin.transaction",
            command="mock-plugin-transaction",
            operation="mock_plugin_transaction",
            backend="mock-plugin-like",
            entrypoint="core.contracts.mock_plugin_transaction.execute_mock_plugin_transaction",
            tool_card=ToolCard(
                tool_id="mock-plugin.transaction",
                permission_class="deterministic_verify",
                allowed_effects=list(P12_TRANSACTION_ALLOWED_EFFECTS),
                forbidden_effects=list(P12_TRANSACTION_FORBIDDEN_EFFECTS),
            ),
            allowed_evidence=("mock_plugin_transaction", "mock_ledger_refs", "no_save_guard"),
            boundary=(
                "P12 mock plugin-like transaction validates rollback and committed_preview "
                "semantics without AutoCAD, native plugin execution, or real CAD readback"
            ),
            consumes_harness_result=False,
            executes_cad=False,
            reads_dwg=False,
            writes_dwg=False,
            saves_dwg=False,
            mutates_registry=False,
            advances_table_c=False,
            calls_plugin=False,
        ),
        "native-thin.live-spike": RegisteredAdapter(
            adapter_id="native-thin.live-spike",
            command="native-thin-live-spike",
            operation="native_thin_scoped_live_spike",
            backend="native-thin-live-backend",
            entrypoint="core.contracts.native_thin_backend.execute_native_thin_live_spike",
            tool_card=ToolCard(
                tool_id="native-thin.live-spike",
                permission_class="cad_preview",
                allowed_effects=list(P13_NATIVE_LIVE_ALLOWED_EFFECTS),
                forbidden_effects=list(P13_NATIVE_LIVE_FORBIDDEN_EFFECTS),
            ),
            allowed_evidence=(
                "native_thin_live_spike_result",
                "real_cad_readback",
                "native_thin_rollback_proof",
                "native_thin_no_save_audit",
                "no_save_guard",
            ),
            boundary=(
                "P13F scoped native thin live spike only: CODEX_PREVIEW write, created handles "
                "readback, bbox/layer/entity audit, rollback proof, and no-save audit. Generic "
                "native_plugin_execute, cad_execute, dwg_save, and formal_layer_write effects remain blocked."
            ),
            consumes_harness_result=False,
            executes_cad=True,
            reads_dwg=True,
            writes_dwg=True,
            saves_dwg=False,
            mutates_registry=False,
            advances_table_c=False,
            calls_plugin=True,
        ),
    }


def _native_thin_registered_adapters() -> dict[str, RegisteredAdapter]:
    return {
        "native-thin.backend": RegisteredAdapter(
            adapter_id="native-thin.backend",
            command="native-thin-backend",
            operation="native_thin_backend",
            backend="native-thin-skeleton",
            entrypoint="core.contracts.native_thin_backend.execute_native_thin_backend_skeleton",
            tool_card=ToolCard(
                tool_id="native-thin.backend",
                permission_class="deterministic_verify",
                allowed_effects=list(P13_NATIVE_ALLOWED_EFFECTS),
                forbidden_effects=list(P13_NATIVE_FORBIDDEN_EFFECTS),
            ),
            allowed_evidence=(
                "native_thin_backend_contract",
                "native_thin_no_save_audit",
                "native_thin_rollback_proof",
                "native_thin_authorization_gate",
                "native_thin_execution_receipt",
                "native_thin_readiness_packet",
                "native_thin_operator_authorization_request",
                "native_thin_live_spike_execution_gate",
                "native_thin_external_blocker_closeout",
                "no_save_guard",
            ),
            boundary=(
                "P13 native thin backend records transaction, no-save, rollback, scope receipt, "
                "launch packet, authorization gate, execution receipt, readiness authorization request, "
                "and P13E live spike gate / external blocker closeout fields without AutoCAD connection, "
                "native plugin execution, or real CAD readback"
            ),
            consumes_harness_result=False,
            executes_cad=False,
            reads_dwg=False,
            writes_dwg=False,
            saves_dwg=False,
            mutates_registry=False,
            advances_table_c=False,
            calls_plugin=False,
        )
    }


def _engineering_kernel_registered_adapters() -> dict[str, RegisteredAdapter]:
    return {
        "engineering-kernel.diff-package": RegisteredAdapter(
            adapter_id="engineering-kernel.diff-package",
            command="engineering-kernel-diff",
            operation="engineering_kernel_diff_package",
            backend="engineering-kernel",
            entrypoint="core.contracts.engineering_kernel.execute_engineering_kernel_diff",
            tool_card=ToolCard(
                tool_id="engineering-kernel.diff-package",
                permission_class="deterministic_verify",
                allowed_effects=list(P14_ENGINEERING_KERNEL_ALLOWED_EFFECTS),
                forbidden_effects=list(P14_ENGINEERING_KERNEL_FORBIDDEN_EFFECTS),
            ),
            allowed_evidence=(
                "engineering_kernel_graphs",
                "engineering_kernel_diff_package",
                "backend_candidate_profile",
                "no_save_guard",
            ),
            boundary=(
                "P14 Engineering Kernel DiffPackage builds task, geometry, semantic, version, "
                "and evidence graphs from CAD_PLAN plus existing backend evidence/candidate docs only. "
                "It does not execute AutoCAD, invoke native plugins, read back new handles, save DWG, "
                "write formal layers, train, or advance Table C."
            ),
            consumes_harness_result=False,
            executes_cad=False,
            reads_dwg=False,
            writes_dwg=False,
            saves_dwg=False,
            mutates_registry=False,
            advances_table_c=False,
            calls_plugin=False,
        )
    }


def _harness_result_evidence_package(
    *,
    task_id: str,
    adapter: RegisteredAdapter,
    payload: dict[str, Any],
    cad_geometry_verified: bool,
) -> EvidencePackage:
    command = str(payload.get("command") or adapter.command)
    result_kind = _result_kind_for_command(command)
    status = "pass" if cad_geometry_verified else "fail"
    items = [
        EvidenceItem(
            kind="harness_result_registry_consumed",
            status="pass" if payload.get("schemaVersion") == HARNESS_RESULT_SCHEMA else "fail",
            backend="adapter_registry",
            metadata={
                "adapterId": adapter.adapter_id,
                "command": command,
                "boundary": adapter.boundary,
            },
        ),
        EvidenceItem(
            kind=result_kind,
            status=status,
            backend="adapter_registry",
            metadata={
                "adapterId": adapter.adapter_id,
                "status": str(payload.get("status") or ""),
                "verificationStatus": str(payload.get("verificationStatus") or ""),
                "cadWritesAttempted": _bool(payload.get("cadWritesAttempted")),
                "sourceCadWritesAttempted": _bool(payload.get("sourceCadWritesAttempted")),
            },
        ),
        EvidenceItem(
            kind="cad_readback",
            status=status,
            backend="cad_session_host",
            readback_status="verified" if cad_geometry_verified else "not_verified",
            cad_geometry_verified=cad_geometry_verified,
            metadata={
                "backend": "cad_session_host",
                "savedCurrentDwg": False,
                "runCount": payload.get("runCount"),
                "verifiedRunCount": payload.get("verifiedRunCount"),
                "stableGeometry": payload.get("stableGeometry"),
                "boundary": "registry consumes existing harness readback proof only",
            },
        ),
        EvidenceItem(
            kind="no_save_guard",
            status="pass",
            backend="adapter_registry",
            metadata={
                "savedCurrentDwg": False,
                "boundary": "registry consumption does not save or mutate the current DWG",
            },
        ),
    ]
    return EvidencePackage(task_id=task_id, items=items)


def _blocked_consumption_result(
    *,
    adapter: RegisteredAdapter,
    authorization: AdapterAuthorizationResult,
    payload: dict[str, Any],
    blockers: list[str],
) -> HarnessResultConsumptionResult:
    evidence = _harness_result_evidence_package(
        task_id=str(payload.get("taskId") or authorization.tool_contract.task_id),
        adapter=adapter,
        payload=payload,
        cad_geometry_verified=False,
    )
    return HarnessResultConsumptionResult(
        status="blocked",
        verification_status="not_verified",
        adapter=adapter,
        tool_contract=authorization.tool_contract,
        authorization=authorization.authorization,
        evidence=evidence,
        completion=CompletionDecision(
            status="blocked",
            verification_status="not_verified",
            missing_evidence=list(adapter.allowed_evidence),
            checked_evidence=[],
            can_claim_complete=False,
        ),
        missing_evidence=list(adapter.allowed_evidence),
        blocking_reasons=_unique(blockers),
        allowed_claims=[],
        not_proven=_not_proven(),
        cad_geometry_verified=False,
        cad_writes_attempted=_bool(payload.get("cadWritesAttempted")),
        source_cad_writes_attempted=_bool(payload.get("sourceCadWritesAttempted")),
    )


def _adapter_payload(adapter: RegisteredAdapter) -> dict[str, Any]:
    return {
        "schemaVersion": P11_ADAPTER_REGISTRY_SCHEMA,
        "adapterId": adapter.adapter_id,
        "operation": adapter.operation,
        "command": adapter.command,
        "backend": adapter.backend,
        "entrypoint": adapter.entrypoint,
        "boundary": adapter.boundary,
        "allowedEvidence": list(adapter.allowed_evidence),
        "consumesHarnessResult": adapter.consumes_harness_result,
        "executesCad": adapter.executes_cad,
        "readsDwg": adapter.reads_dwg,
        "writesDwg": adapter.writes_dwg,
        "savesDwg": adapter.saves_dwg,
        "mutatesRegistry": adapter.mutates_registry,
        "advancesTableC": adapter.advances_table_c,
        "callsPlugin": adapter.calls_plugin,
    }


def _tool_card_payload(card: ToolCard) -> dict[str, Any]:
    return {
        "schemaVersion": card.schema_version,
        "toolId": card.tool_id,
        "permissionClass": card.permission_class,
        "allowedEffects": list(card.allowed_effects),
        "forbiddenEffects": list(card.forbidden_effects),
    }


def _tool_contract_payload(contract: ToolContract) -> dict[str, Any]:
    return {
        "schemaVersion": contract.schema_version,
        "toolCallId": contract.tool_call_id,
        "taskId": contract.task_id,
        "toolId": contract.tool_id,
        "operation": contract.operation,
        "permissionClass": contract.permission_class,
        "requestedEffects": list(contract.requested_effects),
        "evidenceRequired": list(contract.evidence_required),
        "targetScope": dict(contract.target_scope),
        "dryRunRequired": contract.dry_run_required,
        "readbackRequired": contract.readback_required,
        "saveAllowed": contract.save_allowed,
        "descriptiveOnly": contract.descriptive_only,
    }


def _authorization_payload(authorization: ContractDecision) -> dict[str, Any]:
    return {
        "status": authorization.status,
        "reasons": list(authorization.reasons),
        "checked": list(authorization.checked),
    }


def _normalize_backend(backend: str) -> str:
    text = str(backend or "none").strip()
    if text in {"cad_session_host", "cad-session-host"}:
        return text
    return text or "none"


def _result_kind_for_command(command: str) -> str:
    if command == "rehearsal-closeout":
        return "phase10_rehearsal_closeout"
    if command == "rehearsal-result":
        return "phase10_rehearsal_result"
    return "harness_result"


def _consumption_claim_for_adapter(adapter: RegisteredAdapter) -> str:
    if adapter.adapter_id == "harness.rehearsal-closeout":
        return "phase10_rehearsal_closeout_consumed"
    if adapter.adapter_id == "harness.rehearsal-result":
        return "phase10_rehearsal_result_consumed"
    return "harness_result_consumed"


def _not_proven() -> list[str]:
    return [
        "new_cad_execution_by_registry_consumption",
        "training_resume",
        "table_c_progress",
        "plugin_readiness",
        "native_plugin_readiness",
        "formal_layer_write",
        "current_dwg_save",
    ]


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return []


def _bool(value: Any) -> bool:
    return value is True


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
