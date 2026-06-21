"""Phase 5 vNext contract skeletons.

Sources:
- docs/rfcs/vnext-super-cad-agent-architecture.md
- docs/rfcs/vnext-tool-layer-native-plugin-roadmap.md

This module intentionally stops at contract description and fail-closed
judgement. It does not execute CAD, save DWG files, call plugins, mutate
protected evidence, restore training, or advance Table C.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


PHASE5_FORBIDDEN_EFFECTS = {
    "cad_execute",
    "dwg_save",
    "save_current_dwg",
    "delete_entities",
    "formal_layer_write",
    "plugin_call",
    "plugin_execute",
    "table_c_mutation",
    "registry_mutation",
    "training_source_mutation",
    "protected_evidence_mutation",
}

_PASS_STATUSES = {"pass", "ok", "ready", "verified"}
_READBACK_OK_STATUSES = {"ok", "pass", "verified"}
_FAKE_BACKENDS = {"fake", "fake_cad", "fake_driver", "fake_driver_preflight", "mock", "dry_run"}
_REAL_CAD_BACKENDS = {
    "real_cad",
    "cad_mcp",
    "autocad_existing",
    "active_autocad",
    "autocad_com_existing",
    "cad_session_host",
    "autocad_plugin",
    "cloud_automation",
}
_PERMISSION_RANK = {
    "read_only": 0,
    "deterministic_verify": 1,
    "cad_preview": 2,
    "cad_write": 3,
    "dwg_save": 4,
    "plugin_execute": 4,
}
_PROTECTED_PREFIXES = ("output/", "projects/", "libraries/", "openspec/")
_PROTECTED_EXACT = {
    "docs/training/training-sources.json",
    "libraries/system_library/registry.json",
    "agents/pipeline/pipeline_manifest.json",
    "config/entrypoint_custody_manifest.json",
}
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class TaskObject:
    """Describes user intent, success criteria, and required evidence."""

    task_id: str
    task_kind: str
    user_intent: str
    inputs: dict[str, Any] = field(default_factory=dict)
    target_scope: dict[str, Any] = field(default_factory=dict)
    constraints: list[str] = field(default_factory=list)
    safety_boundaries: list[str] = field(
        default_factory=lambda: [
            "description_only",
            "no_direct_cad_execution",
            "no_dwg_save",
            "no_plugin_call",
            "no_table_c_mutation",
        ]
    )
    success_criteria: list[str] = field(default_factory=list)
    evidence_requirements: list[str] = field(default_factory=list)
    schema_version: str = "task-object/v1"


@dataclass(frozen=True)
class ToolContract:
    """Describes an allowed tool request; it is not an executor."""

    tool_call_id: str
    task_id: str
    tool_id: str
    operation: str
    permission_class: str
    requested_effects: list[str] = field(default_factory=list)
    evidence_required: list[str] = field(default_factory=list)
    target_scope: dict[str, Any] = field(default_factory=dict)
    dry_run_required: bool = True
    readback_required: bool = True
    save_allowed: bool = False
    descriptive_only: bool = True
    schema_version: str = "tool-contract/vnext-skeleton/v1"


@dataclass(frozen=True)
class ContractDecision:
    status: str
    reasons: list[str] = field(default_factory=list)
    checked: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ToolCard:
    """Registers a tool capability and its maximum permission class."""

    tool_id: str
    permission_class: str
    allowed_effects: list[str] = field(default_factory=list)
    forbidden_effects: list[str] = field(default_factory=list)
    schema_version: str = "tool-card/vnext-skeleton/v1"

    def authorize(self, contract: ToolContract) -> ContractDecision:
        reasons: list[str] = []
        checked = [f"tool_id={self.tool_id}", f"permission_class={self.permission_class}"]
        if contract.tool_id != self.tool_id:
            reasons.append(f"ToolContract targets {contract.tool_id}, not ToolCard {self.tool_id}")

        card_rank = _PERMISSION_RANK.get(self.permission_class)
        contract_rank = _PERMISSION_RANK.get(contract.permission_class)
        if card_rank is None:
            reasons.append(f"unknown ToolCard permission class: {self.permission_class}")
        if contract_rank is None:
            reasons.append(f"unknown ToolContract permission class: {contract.permission_class}")
        if card_rank is not None and contract_rank is not None and contract_rank > card_rank:
            reasons.append(
                f"permission class exceeds ToolCard: {contract.permission_class} > {self.permission_class}"
            )

        requested = {str(effect) for effect in contract.requested_effects}
        allowed = {str(effect) for effect in self.allowed_effects}
        forbidden = {str(effect) for effect in self.forbidden_effects}
        for effect in sorted(requested.intersection(forbidden)):
            reasons.append(f"requested effect is forbidden by ToolCard: {effect}")
        for effect in sorted(requested.intersection(PHASE5_FORBIDDEN_EFFECTS)):
            reasons.append(f"Phase 5 skeleton forbids effect: {effect}")
        if allowed:
            for effect in sorted(requested - allowed):
                reasons.append(f"requested effect is not allowed by ToolCard: {effect}")

        return ContractDecision(status="blocked" if reasons else "allowed", reasons=reasons, checked=checked)


@dataclass(frozen=True)
class EvidenceItem:
    kind: str
    status: str
    backend: str = ""
    readback_status: str = ""
    cad_geometry_verified: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_real_cad_readback(self) -> bool:
        backend = str(self.backend or self.metadata.get("backend") or self.metadata.get("driverMode") or "")
        driver_mode = str(self.metadata.get("driverMode") or "")
        fake_flag = bool(self.metadata.get("fake") is True or self.metadata.get("isFake") is True)
        return (
            self.kind == "cad_readback"
            and self.status.casefold() in _PASS_STATUSES
            and str(self.readback_status or self.metadata.get("readbackStatus") or "").casefold()
            in _READBACK_OK_STATUSES
            and self.cad_geometry_verified is True
            and backend.casefold() in _REAL_CAD_BACKENDS
            and backend.casefold() not in _FAKE_BACKENDS
            and driver_mode.casefold() not in _FAKE_BACKENDS
            and not fake_flag
        )

    def satisfies(self, requirement: str) -> bool:
        key = str(requirement).casefold()
        if key == "real_cad_readback":
            return self.is_real_cad_readback()
        if key == "no_save_guard":
            saved = self.metadata.get("savedCurrentDwg", self.metadata.get("saved_current_dwg"))
            return self.kind == "no_save_guard" and self.status.casefold() in _PASS_STATUSES or saved is False
        return self.kind.casefold() == key and self.status.casefold() in _PASS_STATUSES


@dataclass(frozen=True)
class EvidencePackage:
    """Carries deterministic evidence; model prose is only an evidence item."""

    task_id: str
    items: list[EvidenceItem] = field(default_factory=list)
    schema_version: str = "evidence-package/vnext-skeleton/v1"

    @classmethod
    def from_model_text(cls, *, task_id: str, text: str) -> "EvidencePackage":
        return cls(
            task_id=task_id,
            items=[
                EvidenceItem(
                    kind="model_text",
                    status="informational",
                    metadata={
                        "text": str(text),
                        "boundary": "model text cannot replace deterministic EvidencePackage checks",
                    },
                )
            ],
        )

    def real_cad_readback_items(self) -> list[EvidenceItem]:
        return [item for item in self.items if item.is_real_cad_readback()]

    def satisfies(self, requirement: str) -> bool:
        return any(item.satisfies(requirement) for item in self.items)


@dataclass(frozen=True)
class CompletionDecision:
    status: str
    verification_status: str
    missing_evidence: list[str] = field(default_factory=list)
    checked_evidence: list[str] = field(default_factory=list)
    can_claim_complete: bool = False


@dataclass(frozen=True)
class ContractRoundtripResult:
    status: str
    verification_status: str
    task: TaskObject
    tool_card: ToolCard
    tool_contract: ToolContract
    authorization: ContractDecision
    evidence: EvidencePackage
    completion: CompletionDecision
    missing_evidence: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)
    allowed_claims: list[str] = field(default_factory=list)
    not_proven: list[str] = field(default_factory=list)
    cad_geometry_verified: bool = False


@dataclass(frozen=True)
class ReadOnlyCADPlanAdapterResult:
    status: str
    verification_status: str
    task: TaskObject
    cad_plan_candidate: dict[str, Any]
    tool_card: ToolCard
    tool_contract: ToolContract
    authorization: ContractDecision
    validation_errors: list[str]
    dry_run_result: dict[str, Any]
    evidence: EvidencePackage
    completion: CompletionDecision
    missing_evidence: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)
    allowed_claims: list[str] = field(default_factory=list)
    not_proven: list[str] = field(default_factory=list)
    cad_geometry_verified: bool = False


class CompletionJudge:
    """Fail-closed completion judgement for Phase 5 contracts."""

    def judge(self, *, task: TaskObject, evidence: EvidencePackage) -> CompletionDecision:
        required = [str(item) for item in task.evidence_requirements if str(item)]
        checked = [item for item in required if evidence.satisfies(item)]
        missing = [item for item in required if item not in checked]
        if missing:
            status = (
                "not_verified"
                if missing == ["real_cad_readback"] and _has_non_cad_ready_evidence(evidence)
                else "blocked"
            )
            return CompletionDecision(
                status=status,
                verification_status="not_verified",
                missing_evidence=missing,
                checked_evidence=checked,
                can_claim_complete=False,
            )
        cad_verified = evidence.satisfies("real_cad_readback")
        return CompletionDecision(
            status="ready",
            verification_status="verified" if cad_verified else "not_verified",
            missing_evidence=[],
            checked_evidence=checked,
            can_claim_complete=cad_verified,
        )

    def judge_with_ledger(
        self,
        *,
        task: TaskObject,
        evidence_packages: dict[str, EvidencePackage],
        ledger: Any,
    ) -> CompletionDecision:
        """Fail closed unless required evidence has a matching ledger record."""

        from core.contracts.evidence_ledger import EvidenceLedgerRecord, evidence_package_content_hash

        required = [str(item) for item in task.evidence_requirements if str(item)]
        packages = evidence_packages if isinstance(evidence_packages, dict) else {}
        records = (
            list(ledger.records_for_task(task.task_id))
            if hasattr(ledger, "records_for_task")
            else []
        )

        checked: list[str] = []
        missing: list[str] = []
        blocking_reasons: list[str] = []
        for requirement in required:
            matching_records = [
                record
                for record in records
                if isinstance(record, EvidenceLedgerRecord)
                and str(record.evidence_type).casefold() == requirement.casefold()
            ]
            if not matching_records:
                missing.append(requirement)
                continue

            requirement_checked = False
            for record in matching_records:
                evidence = packages.get(record.evidence_package_id)
                if not isinstance(evidence, EvidencePackage):
                    blocking_reasons.append(
                        f"ledger record {record.ledger_id} points to missing EvidencePackage {record.evidence_package_id}"
                    )
                    continue
                if record.task_id != task.task_id or evidence.task_id != task.task_id:
                    blocking_reasons.append(f"ledger record {record.ledger_id} task_id does not match task")
                    continue
                if record.content_hash and record.content_hash != evidence_package_content_hash(evidence):
                    blocking_reasons.append(f"ledger record {record.ledger_id} content_hash does not match package")
                    continue
                if not evidence.satisfies(record.evidence_type):
                    blocking_reasons.append(
                        f"ledger record {record.ledger_id} does not match EvidencePackage evidence_type"
                    )
                    continue
                if (
                    requirement.casefold() == "real_cad_readback"
                    and str(record.verification_status).casefold() != "verified"
                ):
                    blocking_reasons.append(
                        f"ledger record {record.ledger_id} real_cad_readback is not verified"
                    )
                    continue
                requirement_checked = True
                break

            if requirement_checked:
                checked.append(requirement)
            else:
                missing.append(requirement)

        if missing or blocking_reasons:
            status = (
                "not_verified"
                if not blocking_reasons
                and missing == ["real_cad_readback"]
                and any(_has_non_cad_ready_evidence(evidence) for evidence in packages.values())
                else "blocked"
            )
            return CompletionDecision(
                status=status,
                verification_status="not_verified",
                missing_evidence=list(dict.fromkeys(missing)),
                checked_evidence=checked,
                can_claim_complete=False,
            )

        cad_verified = "real_cad_readback" in {item.casefold() for item in checked}
        return CompletionDecision(
            status="ready",
            verification_status="verified" if cad_verified else "not_verified",
            missing_evidence=[],
            checked_evidence=checked,
            can_claim_complete=cad_verified,
        )


def build_tool_contract_from_task(task: TaskObject, tool_card: ToolCard) -> ToolContract:
    inputs = task.inputs if isinstance(task.inputs, dict) else {}
    requested_effects = _text_list(inputs.get("requestedEffects")) or ["contract_roundtrip"]
    return ToolContract(
        tool_call_id=str(inputs.get("toolCallId") or f"{task.task_id}.tool-contract"),
        task_id=task.task_id,
        tool_id=str(inputs.get("toolId") or tool_card.tool_id),
        operation=str(inputs.get("operation") or "audit"),
        permission_class=str(inputs.get("permissionClass") or tool_card.permission_class),
        requested_effects=requested_effects,
        evidence_required=list(task.evidence_requirements),
        target_scope=dict(task.target_scope),
    )


def build_read_only_cad_plan_tool_contract(task: TaskObject, tool_card: ToolCard) -> ToolContract:
    inputs = task.inputs if isinstance(task.inputs, dict) else {}
    requested_effects = _text_list(inputs.get("requestedEffects")) or [
        "cad_plan_validate",
        "cad_plan_dry_run",
    ]
    return ToolContract(
        tool_call_id=str(inputs.get("toolCallId") or f"{task.task_id}.cad-plan-read-only-adapter"),
        task_id=task.task_id,
        tool_id=str(inputs.get("toolId") or tool_card.tool_id),
        operation=str(inputs.get("operation") or "validate_dry_run"),
        permission_class=str(inputs.get("permissionClass") or tool_card.permission_class),
        requested_effects=requested_effects,
        evidence_required=list(task.evidence_requirements),
        target_scope=dict(task.target_scope),
        dry_run_required=True,
        readback_required=False,
        save_allowed=False,
        descriptive_only=True,
    )


def cad_plan_candidate_from_task(task: TaskObject) -> dict[str, Any]:
    inputs = task.inputs if isinstance(task.inputs, dict) else {}
    direct = inputs.get("cadPlan", inputs.get("cad_plan"))
    if isinstance(direct, dict):
        return dict(direct)

    structured = inputs.get("structuredIntent", inputs.get("structured_intent"))
    if isinstance(structured, dict):
        for key in ("cadPlan", "cad_plan", "plan"):
            nested = structured.get(key)
            if isinstance(nested, dict):
                return dict(nested)
        return dict(structured)
    return {}


def run_read_only_cad_plan_adapter(
    *,
    task: TaskObject,
    tool_card: ToolCard,
    model_text: str | None = None,
) -> ReadOnlyCADPlanAdapterResult:
    """Wrap CAD_PLAN validate/dry-run as contract evidence without CAD execution."""

    from core.plan_engine.dry_run_report import create_dry_run_report
    from core.plan_engine.validate_plan import validate_plan

    cad_plan_candidate = cad_plan_candidate_from_task(task)
    tool_contract = build_read_only_cad_plan_tool_contract(task, tool_card)
    authorization = tool_card.authorize(tool_contract)

    validation_errors = [str(item) for item in validate_plan(cad_plan_candidate)]
    if validation_errors:
        dry_run_result: dict[str, Any] = {
            "version": "0.1",
            "status": "invalid",
            "validation_errors": validation_errors,
            "human_summary": "CAD_PLAN dry-run not attempted because validate failed.",
        }
    else:
        try:
            dry_run_result = create_dry_run_report(cad_plan_candidate)
        except Exception as exc:  # pragma: no cover - exception type is fixture dependent
            dry_run_result = {
                "version": "0.1",
                "status": "error",
                "validation_errors": [],
                "error": f"{type(exc).__name__}: {exc}",
                "human_summary": "CAD_PLAN dry-run failed before CAD execution.",
            }

    evidence = read_only_cad_plan_evidence_package(
        task_id=task.task_id,
        validation_errors=validation_errors,
        dry_run_result=dry_run_result,
        model_text=model_text,
    )
    completion = CompletionJudge().judge(task=task, evidence=evidence)
    dry_run_pass = evidence.satisfies("cad_plan_dry_run")

    blocking_reasons: list[str] = []
    if authorization.status != "allowed":
        blocking_reasons.extend(authorization.reasons)
    if validation_errors:
        blocking_reasons.append(f"validate failed: {'; '.join(validation_errors)}")
    if not dry_run_pass:
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

    adapter_ready = authorization.status == "allowed" and evidence.satisfies("cad_plan_read_only_adapter")
    allowed_claims = ["contract_ready_non_cad"] if adapter_ready else []
    not_proven = [
        "CAD geometry verified",
        "created handles readback",
        "DWG save or original drawing mutation safety beyond declared no-save evidence",
        "plugin, Worker, training, registry, or Table C progress",
    ]
    return ReadOnlyCADPlanAdapterResult(
        status=status,
        verification_status="not_verified",
        task=task,
        cad_plan_candidate=cad_plan_candidate,
        tool_card=tool_card,
        tool_contract=tool_contract,
        authorization=authorization,
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


def read_only_cad_plan_evidence_package(
    *,
    task_id: str,
    validation_errors: list[str],
    dry_run_result: dict[str, Any],
    model_text: str | None = None,
) -> EvidencePackage:
    validate_pass = not validation_errors
    dry_run_errors = _text_list(dry_run_result.get("validation_errors"))
    dry_run_status = str(dry_run_result.get("status") or "").casefold()
    dry_run_pass = dry_run_status in {"valid", "pass", "ok", "ready"} and not dry_run_errors
    adapter_pass = validate_pass and dry_run_pass
    items = [
        EvidenceItem(
            kind="cad_plan_validate",
            status="pass" if validate_pass else "fail",
            backend="validate_plan",
            metadata={
                "errors": list(validation_errors),
                "proves": "schema and CAD_PLAN legality only",
            },
        ),
        EvidenceItem(
            kind="cad_plan_dry_run",
            status="pass" if dry_run_pass else "fail",
            backend="dry_run",
            metadata={
                "dryRunStatus": str(dry_run_result.get("status") or ""),
                "validationErrors": dry_run_errors,
                "error": str(dry_run_result.get("error") or ""),
                "proves": "dry-run feasibility only",
            },
        ),
        EvidenceItem(
            kind="cad_plan_read_only_adapter",
            status="pass" if adapter_pass else "fail",
            backend="contract_adapter",
            metadata={
                "boundary": "read-only adapter evidence does not include created handles readback",
            },
        ),
        EvidenceItem(
            kind="no_save_guard",
            status="pass",
            backend="contract_adapter",
            metadata={
                "savedCurrentDwg": False,
                "boundary": "adapter does not execute CAD or save DWG",
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
                    "boundary": "model text cannot override deterministic adapter evidence",
                },
            )
        )
    return EvidencePackage(task_id=task_id, items=items)


def run_no_cad_contract_roundtrip(
    *,
    task: TaskObject,
    tool_card: ToolCard,
    evidence: EvidencePackage | None,
) -> ContractRoundtripResult:
    """Run a contract-only roundtrip without CAD, Worker, plugin, DWG, or registry writes."""

    tool_contract = build_tool_contract_from_task(task, tool_card)
    authorization = tool_card.authorize(tool_contract)
    empty_evidence = EvidencePackage(task_id=task.task_id, items=[])
    evidence_package = evidence if isinstance(evidence, EvidencePackage) else empty_evidence
    completion = CompletionJudge().judge(task=task, evidence=evidence_package)
    cad_verified = evidence_package.satisfies("real_cad_readback")

    blocking_reasons: list[str] = []
    if authorization.status != "allowed":
        blocking_reasons.extend(authorization.reasons)
    if evidence is None:
        blocking_reasons.append("EvidencePackage missing")
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
        status = completion.status

    contract_ready = authorization.status == "allowed" and evidence_package.satisfies("no_cad_contract_roundtrip")
    allowed_claims = ["contract roundtrip ready"] if contract_ready else []
    not_proven = [
        "CAD geometry verified",
        "real CAD readback",
        "DWG save or original drawing mutation safety beyond declared no-save evidence",
        "plugin, Worker, training, registry, or Table C progress",
    ]
    return ContractRoundtripResult(
        status=status,
        verification_status="verified" if cad_verified else "not_verified",
        task=task,
        tool_card=tool_card,
        tool_contract=tool_contract,
        authorization=authorization,
        evidence=evidence_package,
        completion=completion,
        missing_evidence=list(completion.missing_evidence),
        blocking_reasons=list(dict.fromkeys(blocking_reasons)),
        allowed_claims=allowed_claims,
        not_proven=not_proven,
        cad_geometry_verified=cad_verified,
    )


def protected_evidence_write_decision(path: str | Path) -> ContractDecision:
    normalized = _normalize_repo_path(path)
    reasons: list[str] = []
    if normalized in _PROTECTED_EXACT or any(normalized.startswith(prefix) for prefix in _PROTECTED_PREFIXES):
        reasons.append(f"write blocked for protected evidence path: {normalized}")
    return ContractDecision(
        status="blocked" if reasons else "allowed",
        reasons=reasons,
        checked=["Phase 5 skeleton protected evidence boundary"],
    )


def _text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return [str(value)] if str(value) else []


def _has_non_cad_ready_evidence(evidence: EvidencePackage) -> bool:
    return (
        evidence.satisfies("no_cad_contract_roundtrip")
        or evidence.satisfies("cad_plan_read_only_adapter")
        or evidence.satisfies("legacy_gateway_adapter")
    )


def _normalize_repo_path(path: str | Path) -> str:
    raw = Path(path)
    try:
        if raw.is_absolute():
            rel = raw.resolve().relative_to(_PROJECT_ROOT)
        else:
            rel = raw
    except ValueError:
        rel = raw
    return rel.as_posix().replace("\\", "/").lstrip("./").casefold()
