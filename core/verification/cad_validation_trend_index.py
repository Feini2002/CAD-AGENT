"""Build a machine-readable trend index for run_cad_validation reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.verification.evidence_trend import (
    build_evidence_trend_report,
    build_evidence_trend_snapshot,
    empty_evidence_state_counts,
    validate_evidence_trend_report,
)
from core.verification.evidence_vocabulary import (
    EVIDENCE_CAD_CAPABILITY_VERIFIED,
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
)


CAD_VALIDATION_TREND_INDEX_FILENAME = "cad_validation_trend_index.json"


def _int_value(payload: dict[str, Any], key: str) -> int:
    value = payload.get(key, 0)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return 0
    return value


def _evidence_counts_from_summary(summary: dict[str, Any]) -> dict[str, int]:
    counts = empty_evidence_state_counts()
    raw_counts = summary.get("evidence_state_counts")
    if isinstance(raw_counts, dict):
        for state in counts:
            counts[state] = _int_value(raw_counts, state)
        return counts

    counts[EVIDENCE_READBACK_GEOMETRY_VERIFIED] = _int_value(summary, "readback_geometry_verified_count")
    counts[EVIDENCE_CAD_CAPABILITY_VERIFIED] = _int_value(summary, "cad_capability_verified_count")
    counts[EVIDENCE_DEFERRED_CAD_READBACK] = max(
        _int_value(summary, "deferred_cad_readback_count"),
        _int_value(summary, "deferred_cad_readback_required_count"),
    )
    counts[EVIDENCE_DRY_RUN_VALID_PLAN_ONLY] = _int_value(summary, "dry_run_valid_plan_only_count")
    return counts


def _snapshot_for_report(*, project_root: Path, report_path: Path, report: dict[str, Any]) -> dict[str, Any]:
    summary = report.get("evidence_summary") if isinstance(report.get("evidence_summary"), dict) else {}
    return build_evidence_trend_snapshot(
        snapshot_id=str(report_path.parent.name),
        series_id="cad_validation",
        source_kind="cad_validation",
        source_path=str(report_path.resolve().relative_to(project_root)).replace("\\", "/"),
        snapshot_at=str(report.get("generated_at", "")),
        evidence_state_counts=_evidence_counts_from_summary(summary),
        geometry_accuracy_counts=summary.get("geometry_accuracy_counts") if isinstance(summary, dict) else {},
        screenshot_role_counts=summary.get("screenshot_role_counts") if isinstance(summary, dict) else {},
        metrics={
            "status": report.get("status"),
            "legacy_status": report.get("legacy_status"),
            "include_cad": report.get("include_cad"),
            "block_alpha_only": report.get("block_alpha_only"),
            "geometry_gate_mode": report.get("geometry_gate_mode"),
        },
    )


def iter_cad_validation_report_paths(reports_root: Path) -> list[Path]:
    """Return direct child report.json paths under a validation run root."""

    if not reports_root.exists():
        return []
    paths = [
        child / "report.json"
        for child in reports_root.iterdir()
        if child.is_dir() and (child / "report.json").is_file()
    ]
    return sorted(paths, key=lambda path: str(path))


def build_cad_validation_trend_index(
    *,
    project_root: Path,
    reports_root: Path,
    generated_at: str,
) -> dict[str, Any]:
    snapshots: list[dict[str, Any]] = []
    for report_path in iter_cad_validation_report_paths(reports_root):
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(report, dict) and isinstance(report.get("evidence_summary"), dict):
            snapshots.append(_snapshot_for_report(project_root=project_root, report_path=report_path, report=report))
    snapshots.sort(key=lambda snapshot: (str(snapshot.get("snapshot_at", "")), str(snapshot.get("source_path", ""))))
    trend = build_evidence_trend_report(
        report_id="cad-validation-trend-index",
        generated_at=generated_at,
        snapshots=snapshots,
        notes=[
            "LCAD-11.3 cad validation trend index.",
            "This index is machine-readable evidence history; deferred/no-CAD snapshots do not add geometry_verified evidence.",
        ],
    )
    errors = validate_evidence_trend_report(trend)
    if errors:
        raise ValueError("invalid cad validation trend index: " + "; ".join(errors))
    return trend


def write_cad_validation_trend_index(
    *,
    project_root: Path,
    reports_root: Path,
    output_dir: Path,
    generated_at: str,
) -> Path:
    trend = build_cad_validation_trend_index(
        project_root=project_root,
        reports_root=reports_root,
        generated_at=generated_at,
    )
    trend_path = output_dir / "evidence_trend" / CAD_VALIDATION_TREND_INDEX_FILENAME
    trend_path.parent.mkdir(parents=True, exist_ok=True)
    trend_path.write_text(json.dumps(trend, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return trend_path
