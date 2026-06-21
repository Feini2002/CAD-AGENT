"""Phase 8 read-only Workbench projection skeleton.

The projection consumes TaskObject, EvidencePackage, EvidenceLedgerRecord, and
CompletionJudge output. It does not append, overwrite, delete, persist files,
copy protected evidence, call CAD, or read/write DWG/DWT files.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any

from core.contracts.evidence_ledger import EvidenceLedgerRecord, evidence_package_content_hash
from core.contracts.vnext import CompletionJudge, EvidencePackage, TaskObject


SCHEMA_VERSION = "workbench-projection/v1"


@dataclass(frozen=True)
class WorkbenchProjection:
    schema_version: str
    task_id: str
    task_kind: str
    required_evidence: list[str] = field(default_factory=list)
    checked_evidence: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    completion_status: str = "blocked"
    verification_status: str = "not_verified"
    can_claim_complete: bool = False
    cad_geometry_verified: bool = False
    ledger_records_summary: list[dict[str, Any]] = field(default_factory=list)
    evidence_package_refs: list[dict[str, Any]] = field(default_factory=list)
    blocked_reason: str = ""
    not_verified_reason: str = ""
    source_refs: list[str] = field(default_factory=list)
    content_hashes: list[str] = field(default_factory=list)
    producers: list[str] = field(default_factory=list)
    tool_card_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_workbench_projection(
    *,
    task: TaskObject,
    evidence_packages: dict[str, EvidencePackage],
    ledger: Any,
    judge: CompletionJudge | None = None,
) -> WorkbenchProjection:
    """Build a read-only view model over ledger-backed completion state."""

    packages = evidence_packages if isinstance(evidence_packages, dict) else {}
    records = _records_for_task(ledger, task.task_id)
    completion = (judge or CompletionJudge()).judge_with_ledger(
        task=task,
        evidence_packages=packages,
        ledger=ledger,
    )
    required = _required_evidence(task)
    diagnostics = _diagnose_projection(
        task=task,
        required_evidence=required,
        records=records,
        evidence_packages=packages,
    )
    blocked_reasons = _unique(
        [
            *diagnostics,
            *[record.blocked_reason for record in records],
        ]
    )
    not_verified_reasons = _unique(
        [
            *[record.not_verified_reason for record in records],
            *(diagnostics if completion.status == "not_verified" else []),
        ]
    )
    checked_lower = {str(item).casefold() for item in completion.checked_evidence}
    cad_geometry_verified = (
        completion.can_claim_complete
        and completion.verification_status == "verified"
        and "real_cad_readback" in checked_lower
    )

    return WorkbenchProjection(
        schema_version=SCHEMA_VERSION,
        task_id=task.task_id,
        task_kind=task.task_kind,
        required_evidence=required,
        checked_evidence=list(completion.checked_evidence),
        missing_evidence=list(completion.missing_evidence),
        completion_status=completion.status,
        verification_status=completion.verification_status,
        can_claim_complete=completion.can_claim_complete,
        cad_geometry_verified=cad_geometry_verified,
        ledger_records_summary=[
            _ledger_record_summary(record=record, evidence_packages=packages) for record in records
        ],
        evidence_package_refs=_evidence_package_refs(evidence_packages=packages, records=records),
        blocked_reason=_reason_text(blocked_reasons) if completion.status == "blocked" else "",
        not_verified_reason=_reason_text(not_verified_reasons),
        source_refs=_unique([record.source_ref for record in records]),
        content_hashes=_unique([record.content_hash for record in records]),
        producers=_unique([record.producer for record in records]),
        tool_card_ids=_unique([record.tool_card_id for record in records]),
    )


def _records_for_task(ledger: Any, task_id: str) -> list[EvidenceLedgerRecord]:
    if not hasattr(ledger, "records_for_task"):
        return []
    return [
        record
        for record in ledger.records_for_task(task_id)
        if isinstance(record, EvidenceLedgerRecord)
    ]


def _required_evidence(task: TaskObject) -> list[str]:
    return [str(item) for item in task.evidence_requirements if str(item)]


def _diagnose_projection(
    *,
    task: TaskObject,
    required_evidence: list[str],
    records: list[EvidenceLedgerRecord],
    evidence_packages: dict[str, EvidencePackage],
) -> list[str]:
    issues: list[str] = []
    for requirement in required_evidence:
        matching_records = [
            record for record in records if record.evidence_type.casefold() == requirement.casefold()
        ]
        if not matching_records:
            issues.append(f"missing ledger record for required evidence: {requirement}")
            continue
        requirement_has_valid_record = False
        for record in matching_records:
            issue = _record_issue(task=task, record=record, evidence_packages=evidence_packages)
            if issue:
                issues.append(issue)
            else:
                requirement_has_valid_record = True
        if not requirement_has_valid_record and not any(
            requirement.casefold() in issue.casefold() for issue in issues
        ):
            issues.append(f"no valid ledger record for required evidence: {requirement}")
    return _unique(issues)


def _record_issue(
    *,
    task: TaskObject,
    record: EvidenceLedgerRecord,
    evidence_packages: dict[str, EvidencePackage],
) -> str:
    evidence = evidence_packages.get(record.evidence_package_id)
    if not isinstance(evidence, EvidencePackage):
        return (
            f"ledger record {record.ledger_id} points to missing EvidencePackage "
            f"{record.evidence_package_id}"
        )
    if record.task_id != task.task_id or evidence.task_id != task.task_id:
        return f"ledger record {record.ledger_id} task_id does not match task"
    if record.content_hash and record.content_hash != evidence_package_content_hash(evidence):
        return f"ledger record {record.ledger_id} content_hash does not match package"
    if not evidence.satisfies(record.evidence_type):
        return f"ledger record {record.ledger_id} does not match EvidencePackage evidence_type"
    if (
        record.evidence_type.casefold() == "real_cad_readback"
        and record.verification_status.casefold() != "verified"
    ):
        return f"ledger record {record.ledger_id} real_cad_readback is not verified"
    return ""


def _ledger_record_summary(
    *,
    record: EvidenceLedgerRecord,
    evidence_packages: dict[str, EvidencePackage],
) -> dict[str, Any]:
    evidence = evidence_packages.get(record.evidence_package_id)
    package_found = isinstance(evidence, EvidencePackage)
    package_hash = evidence_package_content_hash(evidence) if package_found else ""
    hash_matches = None
    if record.content_hash:
        hash_matches = bool(package_found and record.content_hash == package_hash)
    return {
        "ledger_id": record.ledger_id,
        "task_id": record.task_id,
        "contract_id": record.contract_id,
        "evidence_package_id": record.evidence_package_id,
        "evidence_type": record.evidence_type,
        "verification_status": record.verification_status,
        "package_status": "present" if package_found else "missing",
        "package_task_id": evidence.task_id if package_found else "",
        "package_content_hash": package_hash,
        "hash_matches": hash_matches,
        "evidence_satisfied": bool(package_found and evidence.satisfies(record.evidence_type)),
        "producer": record.producer,
        "tool_card_id": record.tool_card_id,
        "source_ref": record.source_ref,
        "content_hash": record.content_hash,
        "blocked_reason": record.blocked_reason,
        "not_verified_reason": record.not_verified_reason,
        "metadata": dict(record.metadata),
    }


def _evidence_package_refs(
    *,
    evidence_packages: dict[str, EvidencePackage],
    records: list[EvidenceLedgerRecord],
) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for package_id, evidence in evidence_packages.items():
        if not isinstance(evidence, EvidencePackage):
            continue
        package_records = [record for record in records if record.evidence_package_id == package_id]
        refs.append(
            {
                "evidence_package_id": str(package_id),
                "task_id": evidence.task_id,
                "content_hash": evidence_package_content_hash(evidence),
                "evidence_types": _unique([item.kind for item in evidence.items]),
                "source_refs": _unique([record.source_ref for record in package_records]),
                "producer": _unique([record.producer for record in package_records]),
                "tool_card_id": _unique([record.tool_card_id for record in package_records]),
                "real_cad_readback": evidence.satisfies("real_cad_readback"),
            }
        )
    return refs


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(str(value) for value in values if str(value)))


def _reason_text(values: list[str]) -> str:
    return "; ".join(_unique(values))
