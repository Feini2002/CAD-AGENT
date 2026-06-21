"""Phase 7 in-memory Evidence Ledger skeleton.

The ledger is append-only and stores references to evidence packages. It does
not persist ledger files, copy protected evidence, move artifacts, call CAD, or
read/write DWG/DWT files.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any

from core.contracts.vnext import EvidencePackage


class AppendOnlyLedgerError(ValueError):
    """Raised when a caller attempts to mutate ledger history."""


class DuplicateLedgerIdError(AppendOnlyLedgerError):
    """Raised when append would overwrite an existing ledger_id."""


@dataclass(frozen=True)
class EvidenceLedgerRecord:
    ledger_id: str
    task_id: str
    contract_id: str
    evidence_package_id: str
    evidence_type: str
    producer: str
    tool_card_id: str
    verification_status: str
    blocked_reason: str = ""
    not_verified_reason: str = ""
    source_ref: str = ""
    content_hash: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    schema_version: str = "evidence-ledger-record/v1"


LedgerEntry = EvidenceLedgerRecord


class InMemoryEvidenceLedger:
    """Append-only fixture ledger for Phase 7 tests and contract wiring."""

    def __init__(self, records: list[EvidenceLedgerRecord] | tuple[EvidenceLedgerRecord, ...] | None = None) -> None:
        self._records_by_id: dict[str, EvidenceLedgerRecord] = {}
        self._records: list[EvidenceLedgerRecord] = []
        for record in records or ():
            self.append(record)

    @property
    def records(self) -> tuple[EvidenceLedgerRecord, ...]:
        return tuple(self._records)

    def append(self, record: EvidenceLedgerRecord) -> EvidenceLedgerRecord:
        ledger_id = str(record.ledger_id)
        if ledger_id in self._records_by_id:
            raise DuplicateLedgerIdError(f"duplicate ledger_id rejected: {ledger_id}")
        self._records_by_id[ledger_id] = record
        self._records.append(record)
        return record

    def get(self, ledger_id: str) -> EvidenceLedgerRecord | None:
        return self._records_by_id.get(str(ledger_id))

    def records_for_task(self, task_id: str) -> tuple[EvidenceLedgerRecord, ...]:
        task_key = str(task_id)
        return tuple(record for record in self._records if record.task_id == task_key)

    def overwrite(self, *_args: Any, **_kwargs: Any) -> None:
        raise AppendOnlyLedgerError("EvidenceLedger is append-only; overwrite is forbidden")

    def delete(self, *_args: Any, **_kwargs: Any) -> None:
        raise AppendOnlyLedgerError("EvidenceLedger is append-only; delete is forbidden")


def evidence_package_content_hash(evidence: EvidencePackage) -> str:
    payload = json.dumps(asdict(evidence), sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
