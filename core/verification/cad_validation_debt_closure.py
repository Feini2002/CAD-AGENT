"""Build a machine-readable closure report for CAD validation governance debt."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BLOCKED_STATUSES = {"blocked_batch_debt", "blocked_user_confirmation", "not_checked"}
RESOLVED_OR_BOUNDED_STATUSES = {
    "classified",
    "enforced",
    "bounded_by_real_cad",
    "bounded_by_readback",
    "guard_verified",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _read_json(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _item(
    item_id: str,
    title: str,
    status: str,
    *,
    metrics: dict[str, Any] | None = None,
    action: str,
    evidence: dict[str, Any] | None = None,
    boundary: str,
) -> dict[str, Any]:
    return {
        "id": item_id,
        "title": title,
        "status": status,
        "metrics": metrics or {},
        "action": action,
        "evidence": evidence or {},
        "boundary": boundary,
    }


def build_cad_validation_debt_closure_report(
    *,
    coverage_report: dict[str, Any],
    evidence_audit_report: dict[str, Any] | None = None,
    cad_validation_report: dict[str, Any] | None = None,
    data_bloat_report: dict[str, Any] | None = None,
    drawing_read_report: dict[str, Any] | None = None,
    repair_gate_status: str = "not_checked",
    repair_gate_command: str = "",
    generated_at: str | None = None,
) -> dict[str, Any]:
    summary = coverage_report.get("summary", {})
    total_count = _int(summary.get("total_count"))
    cad_proof_count = _int(summary.get("cad_proof_count"))
    showcase_count = _int(summary.get("showcase_count"))
    smoke_count = _int(summary.get("smoke_count"))
    deferred_count = _int(summary.get("deferred_count"))
    remaining_to_full = max(total_count - cad_proof_count, 0)
    coverage_percent = _float(summary.get("cad_proof_coverage_percent"))
    headline_percent = _float(summary.get("cad_strength_headline_percent"))

    evidence_summary = (evidence_audit_report or {}).get("summary", {})
    missing_report_paths = _int(
        coverage_report.get("evidence_path_audit", {}).get(
            "report_path_missing",
            evidence_summary.get("failed_count"),
        )
    )

    cad_geometry_gate = (cad_validation_report or {}).get("geometry_gate", {})
    cad_evidence_summary = (cad_validation_report or {}).get("evidence_summary", {})
    readback_count = _int(cad_evidence_summary.get("readback_geometry_verified_count"))
    capability_count = _int(cad_evidence_summary.get("cad_capability_verified_count"))
    visual_aid_count = _int((cad_evidence_summary.get("screenshot_role_counts") or {}).get("visual_aid_only"))

    drawing_read_non_cad = bool((drawing_read_report or {}).get("evidence_summary", {}).get("non_cad_only", True))
    repair_gate_checked = repair_gate_status == "pass"

    items = [
        _item(
            "table_c_gap",
            "Table C headline gap",
            "blocked_batch_debt",
            metrics={
                "cad_proof_coverage_percent": coverage_percent,
                "cad_strength_headline_percent": headline_percent,
                "total_count": total_count,
                "cad_proof_count": cad_proof_count,
                "remaining_to_full_count": remaining_to_full,
            },
            action="Open a dedicated registry/evidence recovery batch; do not claim full Table C from this run.",
            evidence={"coverage_status": coverage_report.get("status", "")},
            boundary="Refreshing coverage recalculates the gap; it does not close missing evidence.",
        ),
        _item(
            "registry_proof_split",
            "Registry proof level split",
            "classified",
            metrics={
                "total_count": total_count,
                "showcase_count": showcase_count,
                "smoke_count": smoke_count,
                "deferred_count": deferred_count,
                "weak_count": smoke_count + deferred_count,
            },
            action="Keep showcase/smoke/deferred separated in reports and delivery language.",
            boundary="Smoke and deferred rows remain registered but cannot be called geometry proof.",
        ),
        _item(
            "smoke_deferred_boundary",
            "Smoke and deferred proof boundary",
            "enforced",
            metrics={"smoke_count": smoke_count, "deferred_count": deferred_count},
            action="Treat smoke/deferred rows as guard or backlog only until a readback report exists.",
            boundary="These rows must not raise cad_proof_count or geometry_verified claims.",
        ),
        _item(
            "evidence_report_path_missing",
            "Missing historical evidence reports",
            "blocked_batch_debt",
            metrics={
                "missing_report_path_count": missing_report_paths,
                "audit_status": (evidence_audit_report or {}).get("status", "not_run"),
                "data_bloat_status": (data_bloat_report or {}).get("status", "not_run"),
            },
            action="Recover real reports, rerun impacted CAD proof, or downgrade stale registry claims.",
            evidence={"audit_failed_count": evidence_summary.get("failed_count")},
            boundary="Do not create empty reports or derived snapshots to satisfy this debt.",
        ),
        _item(
            "rcad_scope_boundary",
            "RCAD smoke versus real capability scope",
            "bounded_by_real_cad" if cad_geometry_gate.get("status") == "pass" else "not_checked",
            metrics={
                "geometry_gate_status": cad_geometry_gate.get("status", "not_run"),
                "readback_geometry_verified_count": readback_count,
                "cad_capability_verified_count": capability_count,
                "block_alpha_geometry_verified": bool((cad_validation_report or {}).get("block_alpha", {}).get("geometry_verified")),
            },
            action="Use this run as representative CAD validation evidence; keep construction drawing claims separate.",
            boundary="A passing geometry gate does not prove arbitrary construction drawing accuracy.",
        ),
        _item(
            "drawing_read_boundary",
            "Automatic drawing read boundary",
            "blocked_user_confirmation" if drawing_read_non_cad else "bounded_by_real_cad",
            metrics={
                "benchmark_status": (drawing_read_report or {}).get("status", "not_run"),
                "non_cad_only": drawing_read_non_cad,
                "readback_geometry_verified_count": _int(
                    (drawing_read_report or {}).get("evidence_summary", {}).get("readback_geometry_verified_count")
                ),
            },
            action="Keep drawing-read output behind human confirmation before CAD execution.",
            boundary="Shell candidates and non-CAD benchmarks cannot directly write CAD.",
        ),
        _item(
            "screenshot_boundary",
            "Screenshot evidence boundary",
            "bounded_by_readback" if readback_count + capability_count > 0 and visual_aid_count > 0 else "not_checked",
            metrics={
                "visual_aid_only_count": visual_aid_count,
                "readback_geometry_verified_count": readback_count,
                "cad_capability_verified_count": capability_count,
            },
            action="Require screenshots to accompany, not replace, created-handle readback.",
            boundary="Screenshot pixels are visual aid only.",
        ),
        _item(
            "local_repair_scope",
            "Local repair and delete scope boundary",
            "guard_verified" if repair_gate_checked else "not_checked",
            metrics={"repair_gate_status": repair_gate_status},
            action="Use target handles / bbox / neighbor protection before update, delete, or redraw.",
            evidence={"repair_gate_command": repair_gate_command},
            boundary="No global cleanup, deletion, formal-layer edits, or save without explicit authorization.",
        ),
    ]

    blocked_count = sum(1 for item in items if item["status"] in BLOCKED_STATUSES)
    resolved_or_bounded_count = sum(1 for item in items if item["status"] in RESOLVED_OR_BOUNDED_STATUSES)
    report_status = "pass" if blocked_count == 0 else "partial"
    return {
        "version": "0.1",
        "report_id": "cad-validation-debt-closure",
        "status": report_status,
        "generated_at": generated_at or _utc_now_iso(),
        "summary": {
            "debt_count": len(items),
            "resolved_or_bounded_count": resolved_or_bounded_count,
            "blocked_count": blocked_count,
        },
        "items": items,
        "safety": {
            "writes_cad": False,
            "saves_current_dwg": False,
            "deletes_entities": False,
            "modifies_formal_layers": False,
            "registry_writeback": False,
        },
    }


def run_cad_validation_debt_closure(
    *,
    coverage_path: Path,
    output_path: Path,
    evidence_audit_path: Path | None = None,
    cad_validation_path: Path | None = None,
    data_bloat_path: Path | None = None,
    drawing_read_path: Path | None = None,
    repair_gate_status: str = "not_checked",
    repair_gate_command: str = "",
) -> dict[str, Any]:
    report = build_cad_validation_debt_closure_report(
        coverage_report=json.loads(coverage_path.read_text(encoding="utf-8")),
        evidence_audit_report=_read_json(evidence_audit_path),
        cad_validation_report=_read_json(cad_validation_path),
        data_bloat_report=_read_json(data_bloat_path),
        drawing_read_report=_read_json(drawing_read_path),
        repair_gate_status=repair_gate_status,
        repair_gate_command=repair_gate_command,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["output_path"] = str(output_path)
    return report
