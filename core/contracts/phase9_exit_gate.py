"""Phase 9 exit gate evaluator.

This gate is intentionally read-only. It cannot create CAD proof, cannot
upgrade preview bundles into readback evidence, and cannot authorize Phase 10
unless the Phase 9 report already proves real created-handle readback.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.path_safety import find_project_root, resolve_under_project_output


PHASE9_EXIT_GATE_SCHEMA = "phase9-exit-gate-result/v1"
DECISION_BOUNDARY = "phase9_exit_gate_does_not_create_or_upgrade_evidence"
REQUIRED_COMPLETION_EVIDENCE = frozenset({"real_cad_readback", "no_save_guard"})


def evaluate_phase9_exit_gate(
    *,
    run_dir: str | Path,
    bundle_dir: str | Path | None = None,
) -> dict[str, Any]:
    project_root = find_project_root(Path.cwd())
    resolved_run_dir = resolve_under_project_output(project_root, Path(run_dir), label="phase9 exit run_dir")
    if not resolved_run_dir.is_dir():
        raise ValueError(f"phase9 run dir does not exist: {resolved_run_dir}")

    report_path = resolved_run_dir / "phase9_preview_report.json"
    if not report_path.is_file():
        raise ValueError(f"phase9 report missing: {report_path}")
    report = _read_json(report_path)

    resolved_bundle_dir = _resolve_bundle_dir(project_root, resolved_run_dir, bundle_dir)
    bundle_summary = _read_bundle_summary(resolved_bundle_dir)
    bundle_manifest_path = str(resolved_bundle_dir / "manifest.json") if resolved_bundle_dir else ""
    bundle_summary_path = str(resolved_bundle_dir / "summary.json") if bundle_summary else ""

    completion = dict(report.get("completion") if isinstance(report.get("completion"), dict) else {})
    missing_evidence = [str(item) for item in report.get("missingEvidence", [])]
    blocking_reasons = [str(item) for item in report.get("blockingReasons", [])]
    created_count, created_count_valid = _non_negative_int(report.get("createdHandleCount"))
    readback_count, readback_count_valid = _non_negative_int(report.get("readbackEntityCount"))
    exit_blockers = _exit_blockers(
        report=report,
        completion=completion,
        bundle_summary=bundle_summary,
        created_count=created_count,
        created_count_valid=created_count_valid,
        readback_count=readback_count,
        readback_count_valid=readback_count_valid,
    )
    all_blockers = _unique([*blocking_reasons, *exit_blockers])
    phase10_allowed = not all_blockers

    return {
        "schemaVersion": PHASE9_EXIT_GATE_SCHEMA,
        "phase": "Phase 9",
        "gate": "P9 Exit",
        "status": "ready" if phase10_allowed else "blocked",
        "phase10Allowed": phase10_allowed,
        "decisionBoundary": DECISION_BOUNDARY,
        "runDir": str(resolved_run_dir),
        "reportPath": str(report_path),
        "previewBundleManifest": bundle_manifest_path,
        "previewBundleSummary": bundle_summary_path,
        "packageId": str(report.get("packageId") or ""),
        "taskId": str(report.get("taskId") or ""),
        "targetLayer": str(report.get("targetLayer") or ""),
        "driverBackend": str(report.get("driverBackend") or ""),
        "verificationStatus": str(report.get("verificationStatus") or "not_verified"),
        "cadGeometryVerified": bool(report.get("cadGeometryVerified") is True),
        "savedCurrentDwg": bool(report.get("savedCurrentDwg", False)),
        "createdHandleCount": created_count,
        "readbackEntityCount": readback_count,
        "completionCanClaimComplete": _completion_can_claim(completion),
        "completionStatus": str(completion.get("status") or ""),
        "missingEvidence": missing_evidence,
        "blockingReasons": all_blockers,
        "notEvidenceFor": ["phase10_rehearsal", "training_resume", "table_c_progress", "plugin_readiness"],
    }


def _exit_blockers(
    *,
    report: dict[str, Any],
    completion: dict[str, Any],
    bundle_summary: dict[str, Any] | None,
    created_count: int,
    created_count_valid: bool,
    readback_count: int,
    readback_count_valid: bool,
) -> list[str]:
    blockers: list[str] = []
    if report.get("targetLayer") != "CODEX_PREVIEW":
        blockers.append("p9_scope_not_codex_preview")
    if report.get("savedCurrentDwg") is not False:
        blockers.append("p9_no_save_guard_missing")
    if report.get("cadGeometryVerified") is not True:
        blockers.append("p9a_real_cad_readback_missing")
    if str(report.get("verificationStatus") or "").casefold() != "verified":
        blockers.append("p9_verification_status_not_verified")
    if _string_list(report.get("missingEvidence")):
        blockers.append("p9_missing_evidence_not_empty")
    if _completion_missing_evidence(completion):
        blockers.append("completion_missing_evidence_not_empty")
    if not REQUIRED_COMPLETION_EVIDENCE.issubset(set(_completion_checked_evidence(completion))):
        blockers.append("completion_checked_evidence_incomplete")
    if not created_count_valid:
        blockers.append("p9_created_handle_count_invalid")
    elif created_count <= 0:
        blockers.append("p9_created_handles_missing")
    if not readback_count_valid:
        blockers.append("p9_readback_entity_count_invalid")
    elif readback_count <= 0:
        blockers.append("p9_readback_entities_missing")
    if not _completion_can_claim(completion):
        blockers.append("completion_judge_not_ready")
    if bundle_summary is not None and _bundle_conflicts_with_report(report, bundle_summary):
        blockers.append("preview_bundle_conflicts_with_report")
    return _unique(blockers)


def _completion_can_claim(completion: dict[str, Any]) -> bool:
    return bool(completion.get("can_claim_complete", completion.get("canClaimComplete", False)) is True)


def _completion_missing_evidence(completion: dict[str, Any]) -> list[str]:
    return _string_list(completion.get("missing_evidence", completion.get("missingEvidence")))


def _completion_checked_evidence(completion: dict[str, Any]) -> list[str]:
    return _string_list(completion.get("checked_evidence", completion.get("checkedEvidence")))


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return []


def _non_negative_int(value: Any) -> tuple[int, bool]:
    if isinstance(value, bool):
        return 0, False
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return 0, False
    if parsed < 0:
        return 0, False
    return parsed, True


def _bundle_conflicts_with_report(report: dict[str, Any], summary: dict[str, Any]) -> bool:
    compared = (
        "status",
        "verificationStatus",
        "cadGeometryVerified",
        "targetLayer",
        "savedCurrentDwg",
        "createdHandleCount",
        "readbackEntityCount",
    )
    return any(summary.get(key) != report.get(key) for key in compared if key in summary or key in report)


def _resolve_bundle_dir(project_root: Path, run_dir: Path, bundle_dir: str | Path | None) -> Path | None:
    candidate = Path(bundle_dir) if bundle_dir is not None else run_dir / "preview_bundle"
    resolved = resolve_under_project_output(project_root, candidate, label="phase9 exit bundle_dir")
    if not resolved.exists():
        return None
    if not resolved.is_dir():
        raise ValueError(f"phase9 preview bundle_dir is not a directory: {resolved}")
    if not resolved.is_relative_to(run_dir):
        raise ValueError("phase9 preview bundle_dir must stay under the source run_dir")
    return resolved


def _read_bundle_summary(bundle_dir: Path | None) -> dict[str, Any] | None:
    if bundle_dir is None:
        return None
    summary_path = bundle_dir / "summary.json"
    if not summary_path.is_file():
        return None
    return _read_json(summary_path)


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _read_json(path: Path) -> dict[str, Any]:
    return dict(json.loads(path.read_text(encoding="utf-8")))
