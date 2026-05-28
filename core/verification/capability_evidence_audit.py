"""Hard-audit verified/showcase CAD capability evidence."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.path_safety import resolve_under_project_output, resolve_under_project_root
from core.verification.capability_registry import (
    DEFAULT_REGISTRY_PATH,
    load_capability_registry,
    validate_capability_registry,
)
from core.verification.evidence_contract import (
    EVIDENCE_CAD_CAPABILITY_VERIFIED,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    validate_capability_probe_evidence,
    validate_readback_report_evidence,
)

CAD_PROOF_LEVELS = {"verified", "showcase"}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")


def _row_result(
    *,
    row: dict[str, Any],
    status: str,
    message: str,
    report_path: str = "",
    failure_category: str = "",
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "capability_id": str(row.get("capability_id", "")),
        "claim_level": str(row.get("claim_level", "")),
        "status": status,
        "report_path": report_path,
        "message": message,
    }
    if failure_category:
        result["failure_category"] = failure_category
    return result


def _load_json_report(report_file: Path) -> tuple[dict[str, Any] | None, str]:
    try:
        payload = json.loads(report_file.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, str(exc)
    if not isinstance(payload, dict):
        return None, "report must be a JSON object"
    return payload, ""


def _audit_proof_row(row: dict[str, Any], *, project_root: Path) -> dict[str, Any]:
    evidence = row.get("evidence")
    if not isinstance(evidence, dict):
        return _row_result(
            row=row,
            status="fail",
            message="verified/showcase row requires evidence object",
            failure_category="missing_evidence",
        )

    report_path = evidence.get("report_path")
    if not isinstance(report_path, str) or not report_path.strip():
        return _row_result(
            row=row,
            status="fail",
            message="verified/showcase row requires evidence.report_path",
            failure_category="missing_report_path",
        )

    try:
        report_file = resolve_under_project_root(project_root, Path(report_path), label="evidence.report_path")
    except ValueError as exc:
        return _row_result(
            row=row,
            status="fail",
            report_path=report_path,
            message=str(exc),
            failure_category="unsafe_report_path",
        )

    if not report_file.is_file():
        return _row_result(
            row=row,
            status="fail",
            report_path=report_path,
            message=f"report not found: {report_path}",
            failure_category="report_path_missing",
        )

    report, load_error = _load_json_report(report_file)
    if report is None:
        return _row_result(
            row=row,
            status="fail",
            report_path=report_path,
            message=load_error,
            failure_category="report_json_invalid",
        )

    evidence_state = str(evidence.get("evidence_state", ""))
    if evidence_state == EVIDENCE_READBACK_GEOMETRY_VERIFIED:
        validation_error = validate_readback_report_evidence(report)
    elif evidence_state == EVIDENCE_CAD_CAPABILITY_VERIFIED:
        validation_error = validate_capability_probe_evidence(report)
    else:
        validation_error = f"unsupported geometry evidence_state for table C audit: {evidence_state!r}"

    if validation_error:
        return _row_result(
            row=row,
            status="fail",
            report_path=report_path,
            message=validation_error,
            failure_category="evidence_contract_failed",
        )

    return _row_result(
        row=row,
        status="pass",
        report_path=report_path,
        message="evidence report satisfies table C hard audit",
    )


def build_capability_evidence_audit_report(
    registry: dict[str, Any],
    *,
    registry_path: Path,
    project_root: Path,
    generated_at: str | None = None,
) -> dict[str, Any]:
    rows = [row for row in registry.get("capabilities", []) if isinstance(row, dict)]
    proof_rows = [row for row in rows if row.get("claim_level") in CAD_PROOF_LEVELS]
    results = [_audit_proof_row(row, project_root=project_root) for row in proof_rows]
    failed = [row for row in results if row.get("status") != "pass"]
    rel_registry = _rel(registry_path, project_root)
    return {
        "version": "0.1",
        "report_id": "table-c-capability-evidence-audit",
        "status": "pass" if not failed else "fail",
        "generated_at": generated_at or _utc_now_iso(),
        "registry_path": rel_registry,
        "summary": {
            "audited_count": len(results),
            "passed_count": len(results) - len(failed),
            "failed_count": len(failed),
        },
        "rows": results,
        "notes": [
            "Only verified/showcase registry rows are audited.",
            "Screenshots are visual aids; table C geometry proof still requires CAD readback evidence.",
        ],
    }


def audit_capability_evidence(
    project_root: Path,
    *,
    registry_path: Path | None = None,
    output_path: Path | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    root = project_root.resolve()
    registry_file = registry_path or (root / DEFAULT_REGISTRY_PATH)
    registry = load_capability_registry(registry_file, project_root=root)
    validation_errors = validate_capability_registry(registry)
    if validation_errors:
        report: dict[str, Any] = {
            "version": "0.1",
            "report_id": "table-c-capability-evidence-audit",
            "status": "fail",
            "generated_at": generated_at or _utc_now_iso(),
            "registry_path": str(registry_file),
            "summary": {"audited_count": 0, "passed_count": 0, "failed_count": len(validation_errors)},
            "errors": validation_errors,
            "rows": [],
        }
    else:
        report = build_capability_evidence_audit_report(
            registry,
            registry_path=resolve_under_project_root(root, registry_file, label="registry_path"),
            project_root=root,
            generated_at=generated_at,
        )

    if output_path is not None:
        target = resolve_under_project_output(root, output_path, label="output_path")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report["output_path"] = _rel(target, root)
    return report
