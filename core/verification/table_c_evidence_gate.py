"""Aggregate evidence and visual gates before table C writeback."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.path_safety import resolve_under_project_output, resolve_under_project_root
from core.verification.capability_coverage import run_capability_coverage
from core.verification.capability_evidence_audit import audit_capability_evidence


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")


def _load_report(path: Path, *, project_root: Path, label: str) -> dict[str, Any]:
    report_file = resolve_under_project_root(project_root, path, label=label)
    payload = json.loads(report_file.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a JSON object")
    payload["_source_path"] = _rel(report_file, project_root)
    return payload


def run_table_c_evidence_gate(
    project_root: Path,
    *,
    output_path: Path,
    registry_path: Path | None = None,
    evidence_audit_report_path: Path | None = None,
    visual_review_report_path: Path | None = None,
    coverage_output_path: Path | None = None,
    require_visual_pass: bool = True,
    generated_at: str | None = None,
) -> dict[str, Any]:
    root = project_root.resolve()
    target = resolve_under_project_output(root, output_path, label="output_path")
    target.parent.mkdir(parents=True, exist_ok=True)

    if evidence_audit_report_path is None:
        evidence_audit = audit_capability_evidence(
            root,
            registry_path=registry_path,
            output_path=target.parent / "evidence_audit_report.json",
            generated_at=generated_at,
        )
    else:
        evidence_audit = _load_report(evidence_audit_report_path, project_root=root, label="evidence_audit_report_path")

    if visual_review_report_path is None:
        visual_review: dict[str, Any] = {
            "status": "not_run",
            "writeback_allowed": False,
            "failure_category": "visual_review_missing",
            "message": "visual review report is required when require_visual_pass=true",
        }
    else:
        visual_review = _load_report(visual_review_report_path, project_root=root, label="visual_review_report_path")

    evidence_ok = evidence_audit.get("status") == "pass"
    visual_ok = (not require_visual_pass) or (
        visual_review.get("status") == "pass" and visual_review.get("writeback_allowed") is True
    )
    writeback_allowed = evidence_ok and visual_ok

    coverage: dict[str, Any]
    if writeback_allowed and coverage_output_path is not None:
        coverage = run_capability_coverage(
            root,
            registry_path=registry_path,
            output_path=coverage_output_path,
            require_evidence_audit_pass=True,
        )
    elif writeback_allowed:
        coverage = {"status": "not_run", "reason": "coverage_output_path not provided"}
    else:
        coverage = {
            "status": "skipped",
            "reason": "table C evidence gate failed; registry writeback and coverage refresh are blocked",
        }

    status = "pass" if writeback_allowed and coverage.get("status") in {"pass", "not_run"} else "fail"
    report = {
        "version": "0.1",
        "report_id": "table-c-evidence-gate",
        "status": status,
        "generated_at": generated_at or _utc_now_iso(),
        "writeback_allowed": writeback_allowed,
        "checks": [
            {
                "name": "capability_evidence_audit",
                "status": "pass" if evidence_ok else "fail",
                "message": "verified/showcase evidence audit passed" if evidence_ok else "evidence audit failed",
            },
            {
                "name": "visual_cad_review",
                "status": "pass" if visual_ok else "fail",
                "message": "visual review passed" if visual_ok else "visual review blocks table C writeback",
            },
        ],
        "evidence_audit": evidence_audit,
        "visual_review": visual_review,
        "coverage": coverage,
        "notes": [
            "Registry writeback must not run unless writeback_allowed=true.",
            "Screenshot/visual review failure blocks this workflow, but screenshots do not replace geometry readback.",
        ],
    }
    if status != "pass":
        report["failure_category"] = "table_c_evidence_gate_failed"

    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["output_path"] = _rel(target, root)
    return report
