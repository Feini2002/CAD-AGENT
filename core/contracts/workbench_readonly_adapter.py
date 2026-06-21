"""Phase 8 read-only Workbench adapter.

The adapter only reshapes WorkbenchProjection objects into existing workbench
view-model conventions. It does not call CAD, persist files, append ledger
records, mutate EvidencePackage objects, or write protected evidence paths.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from typing import Any

from core.contracts.workbench_projection import WorkbenchProjection


SCHEMA_VERSION = "workbench-readonly-adapter/v1"
PANEL_SCHEMA_VERSION = "workbench-contract-projections/v1"


def build_workbench_readonly_adapter(
    projections: Iterable[WorkbenchProjection | Mapping[str, Any]],
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a derived workbench payload from Phase 8 projections."""

    rows = [_projection_row(projection) for projection in projections]
    summary = _summary(rows)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": generated_at or _utc_now(),
        "read_only": True,
        "mutated_targets": [],
        "summary": summary,
        "sourcePolicy": {
            "derivedOnly": True,
            "readOnly": True,
            "mutatedTargets": [],
            "truthSources": [
                "TaskObject",
                "EvidenceLedgerRecord",
                "EvidencePackage",
                "CompletionJudge.judge_with_ledger",
                "WorkbenchProjection",
            ],
            "notProofOf": [
                "cad_geometry_without_real_cad_readback",
                "training_acceptance",
                "table_c_promotion",
                "registry_update",
                "plugin_availability",
            ],
            "forbiddenWrites": [
                "output/**",
                "projects/**",
                "libraries/**",
                "openspec/**",
                "docs/training/training-sources.json",
                "libraries/system_library/registry.json",
                "agents/pipeline/pipeline_manifest.json",
                "config/entrypoint_custody_manifest.json",
            ],
        },
        "views": {
            "evidenceCenter": {
                "schemaVersion": PANEL_SCHEMA_VERSION,
                "readOnly": True,
                "read_only": True,
                "mutatedTargets": [],
                "mutated_targets": [],
                "projectionSummary": summary,
                "contractWorkbenchProjections": rows,
            },
            "flightdeck": {
                "schemaVersion": PANEL_SCHEMA_VERSION,
                "readOnly": True,
                "mutatedTargets": [],
                "summary": summary,
                "items": rows,
            },
            "traceViewer": {
                "readOnly": True,
                "mutatedTargets": [],
                "summary": summary,
                "blockedTaskIds": [
                    row["task_id"] for row in rows if row["completion_status"] == "blocked"
                ],
                "notVerifiedTaskIds": [
                    row["task_id"]
                    for row in rows
                    if row["verification_status"] != "verified"
                    or row["completion_status"] == "not_verified"
                ],
            },
        },
    }


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _projection_row(projection: WorkbenchProjection | Mapping[str, Any]) -> dict[str, Any]:
    data = _projection_mapping(projection)
    ledger_records = _dict_list(data.get("ledger_records_summary"))
    package_refs = _dict_list(data.get("evidence_package_refs"))
    source_refs = _string_list(data.get("source_refs"))
    content_hashes = _string_list(data.get("content_hashes"))
    producers = _string_list(data.get("producers"))
    tool_card_ids = _string_list(data.get("tool_card_ids"))
    checked = _string_list(data.get("checked_evidence"))
    missing = _string_list(data.get("missing_evidence"))

    task_id = str(data.get("task_id") or "")
    task_kind = str(data.get("task_kind") or "")
    completion_status = str(data.get("completion_status") or "blocked")
    verification_status = str(data.get("verification_status") or "not_verified")
    can_claim_complete = data.get("can_claim_complete") is True
    cad_geometry_verified = data.get("cad_geometry_verified") is True
    blocked_reason = str(data.get("blocked_reason") or "")
    not_verified_reason = str(data.get("not_verified_reason") or "")

    return {
        "schema_version": str(data.get("schema_version") or ""),
        "task_id": task_id,
        "task_kind": task_kind,
        "completion_status": completion_status,
        "verification_status": verification_status,
        "can_claim_complete": can_claim_complete,
        "cad_geometry_verified": cad_geometry_verified,
        "required_evidence": _string_list(data.get("required_evidence")),
        "checked_evidence": checked,
        "missing_evidence": missing,
        "ledger_record_count": len(ledger_records),
        "ledger_records_summary": ledger_records,
        "ledger_summary": {
            "record_count": len(ledger_records),
            "verified_record_count": len(
                [
                    record
                    for record in ledger_records
                    if str(record.get("verification_status") or "") == "verified"
                ]
            ),
            "missing_package_count": len(
                [
                    record
                    for record in ledger_records
                    if str(record.get("package_status") or "") == "missing"
                ]
            ),
            "hash_mismatch_count": len(
                [record for record in ledger_records if record.get("hash_matches") is False]
            ),
        },
        "evidence_package_refs": package_refs,
        "evidence_package_count": len(package_refs),
        "blocked_reason": blocked_reason,
        "not_verified_reason": not_verified_reason,
        "source_ref": _first(source_refs),
        "content_hash": _first(content_hashes),
        "producer": _first(producers),
        "tool_card_id": _first(tool_card_ids),
        "source_refs": source_refs,
        "content_hashes": content_hashes,
        "producers": producers,
        "tool_card_ids": tool_card_ids,
        "read_only": True,
        "mutated_targets": [],
        "taskId": task_id,
        "taskKind": task_kind,
        "completionStatus": completion_status,
        "verificationStatus": verification_status,
        "canClaimComplete": can_claim_complete,
        "cadGeometryVerified": cad_geometry_verified,
    }


def _projection_mapping(projection: WorkbenchProjection | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(projection, WorkbenchProjection):
        return projection.to_dict()
    if isinstance(projection, Mapping):
        return dict(projection)
    to_dict = getattr(projection, "to_dict", None)
    if callable(to_dict):
        payload = to_dict()
        if isinstance(payload, Mapping):
            return dict(payload)
    raise TypeError("build_workbench_readonly_adapter expects WorkbenchProjection or mapping rows")


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    blocked = [row for row in rows if row["completion_status"] == "blocked"]
    not_verified = [
        row
        for row in rows
        if row["verification_status"] != "verified" or row["completion_status"] == "not_verified"
    ]
    return {
        "projectionCount": len(rows),
        "readyCount": len([row for row in rows if row["completion_status"] == "ready"]),
        "blockedCount": len(blocked),
        "notVerifiedCount": len(not_verified),
        "canClaimCompleteCount": len([row for row in rows if row["can_claim_complete"]]),
        "cadGeometryVerifiedCount": len([row for row in rows if row["cad_geometry_verified"]]),
        "ledgerRecordCount": sum(int(row["ledger_record_count"]) for row in rows),
        "missingEvidenceCount": sum(len(row["missing_evidence"]) for row in rows),
        "blockedTaskIds": [row["task_id"] for row in blocked],
        "notVerifiedTaskIds": [row["task_id"] for row in not_verified],
    }


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item)]


def _dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]


def _first(values: list[str]) -> str:
    return values[0] if values else ""
