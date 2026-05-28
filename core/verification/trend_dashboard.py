"""V-PROOF-71: machine-readable trend dashboard rollup (LCAD-11 absorption)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.schemas.validator import validate_value
from core.verification.capability_coverage import (
    build_capability_coverage_trend_report,
    run_capability_coverage,
)
from core.verification.cad_validation_trend_index import (
    CAD_VALIDATION_TREND_INDEX_FILENAME,
    write_cad_validation_trend_index,
)
from core.verification.capability_registry import index_capability_rows, validate_capability_registry
from core.verification.capability_registry_seed_common import PREVIEW_SAFETY
from core.verification.evidence_contract import validate_evidence_triplet
from core.verification.evidence_trend import validate_evidence_trend_report
from core.verification.evidence_vocabulary import (
    EVIDENCE_BENCHMARK_PASS_NON_CAD,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)

VPROOF_71_PACKAGE_ID = "V-PROOF-71-TREND-DASHBOARD"
VPROOF_71_BOUNDARY_DOC = "docs/verification/vproof_71_trend_dashboard.md"
VPROOF_71_EVIDENCE_BOUNDARY_DOC = "docs/verification/evidence_trend_boundaries.md"
VPROOF_71_DEFAULT_OUTPUT = "output/validation_runs/vproof-71-trend-dashboard"
DEFAULT_SOURCES_REL = Path("examples/capability_proof/trend_dashboard_sources.json")
DASHBOARD_SCHEMA_REL = Path("core/schemas/capability_trend_dashboard.schema.json")

DASHBOARD_ROLLUP_CAPABILITY_ID = "trend.dashboard.rollup"
DASHBOARD_REGRESSION_CAPABILITY_ID = "trend.dashboard.local_cad_regression"
DASHBOARD_VALIDATION_CAPABILITY_ID = "trend.dashboard.cad_validation_index"
DASHBOARD_COVERAGE_CAPABILITY_ID = "trend.dashboard.capability_coverage"

PANEL_CAPABILITY_IDS = {
    "local_cad_regression": DASHBOARD_REGRESSION_CAPABILITY_ID,
    "cad_validation": DASHBOARD_VALIDATION_CAPABILITY_ID,
    "capability_coverage": DASHBOARD_COVERAGE_CAPABILITY_ID,
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_trend_dashboard_sources(
    path: Path | None = None,
    *,
    project_root: Path,
) -> dict[str, Any]:
    sources_path = path or (project_root / DEFAULT_SOURCES_REL)
    return json.loads(sources_path.read_text(encoding="utf-8"))


def _resolve_first_existing(root: Path, candidates: list[str]) -> Path | None:
    for rel in candidates:
        candidate = root / rel.replace("\\", "/")
        if candidate.is_file():
            return candidate
    return None


def _load_trend_report(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _panel_metrics_from_trend(trend: dict[str, Any]) -> dict[str, Any]:
    summary = trend.get("summary") if isinstance(trend.get("summary"), dict) else {}
    metrics: dict[str, Any] = {
        "snapshot_count": summary.get("snapshot_count", len(trend.get("snapshots", []))),
        "geometry_verified_count": summary.get("geometry_verified_count", 0),
        "non_cad_only": summary.get("non_cad_only"),
    }
    snapshots = trend.get("snapshots")
    if isinstance(snapshots, list) and snapshots:
        latest = snapshots[-1]
        if isinstance(latest, dict):
            latest_metrics = latest.get("metrics")
            if isinstance(latest_metrics, dict) and latest_metrics:
                metrics["latest_snapshot_metrics"] = latest_metrics
    return metrics


def _ensure_capability_coverage_trend(
    *,
    project_root: Path,
    panel: dict[str, Any],
) -> Path:
    root = project_root.resolve()
    trend_candidates = [str(item) for item in panel.get("trend_report_paths", [])]
    trend_path = _resolve_first_existing(root, trend_candidates)
    if trend_path is not None:
        return trend_path

    coverage_rel = str(
        panel.get("coverage_report_path")
        or load_trend_dashboard_sources(project_root=root).get("coverage_report_path", "")
    )
    coverage_path = root / coverage_rel.replace("\\", "/")
    if not coverage_path.is_file():
        run_capability_coverage(
            root,
            output_path=coverage_path,
        )
    coverage_report = json.loads(coverage_path.read_text(encoding="utf-8"))
    if coverage_report.get("status") != "pass":
        raise ValueError(f"coverage report not pass: {coverage_rel}")

    trend = build_capability_coverage_trend_report(
        coverage_report=coverage_report,
        coverage_report_path=coverage_path,
        project_root=root,
    )
    trend_rel = trend_candidates[0] if trend_candidates else (
        "output/validation_runs/capability-lab/evidence_trend/capability_coverage_trend.json"
    )
    trend_path = root / trend_rel.replace("\\", "/")
    trend_path.parent.mkdir(parents=True, exist_ok=True)
    trend_path.write_text(json.dumps(trend, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return trend_path


def _ensure_cad_validation_trend(
    *,
    project_root: Path,
    panel: dict[str, Any],
    output_dir: Path,
) -> Path | None:
    root = project_root.resolve()
    trend_candidates = [str(item) for item in panel.get("trend_report_paths", [])]
    existing = _resolve_first_existing(root, trend_candidates)
    if existing is not None:
        return existing

    reports_root = root / str(panel.get("reports_root", "output/validation_runs"))
    if not reports_root.is_dir():
        return None
    generated_at = _utc_now_iso()
    return write_cad_validation_trend_index(
        project_root=root,
        reports_root=reports_root,
        output_dir=output_dir,
        generated_at=generated_at,
    )


def build_trend_dashboard_panel(
    *,
    project_root: Path,
    panel: dict[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    panel_id = str(panel["panel_id"])
    source_kind = str(panel.get("source_kind", panel_id))
    required = bool(panel.get("required"))

    trend_path: Path | None
    if panel_id == "capability_coverage":
        trend_path = _ensure_capability_coverage_trend(project_root=project_root, panel=panel)
    elif panel_id == "cad_validation":
        trend_path = _ensure_cad_validation_trend(project_root=project_root, panel=panel, output_dir=output_dir)
    else:
        trend_path = _resolve_first_existing(
            project_root,
            [str(item) for item in panel.get("trend_report_paths", [])],
        )

    if trend_path is None:
        return {
            "panel_id": panel_id,
            "source_kind": source_kind,
            "trend_report_path": "",
            "trend_status": "missing",
            "present": False,
            "required": required,
            "snapshot_count": 0,
            "geometry_verified_count": 0,
            "non_cad_only": True,
        }

    rel_path = str(trend_path.resolve().relative_to(project_root.resolve())).replace("\\", "/")
    try:
        trend = _load_trend_report(trend_path)
    except json.JSONDecodeError as exc:
        return {
            "panel_id": panel_id,
            "source_kind": source_kind,
            "trend_report_path": rel_path,
            "trend_status": "invalid",
            "present": False,
            "required": required,
            "snapshot_count": 0,
            "geometry_verified_count": 0,
            "non_cad_only": True,
            "metrics": {"error": str(exc)},
        }

    trend_errors = validate_evidence_trend_report(trend)
    metrics = _panel_metrics_from_trend(trend)
    return {
        "panel_id": panel_id,
        "source_kind": source_kind,
        "trend_report_path": rel_path,
        "trend_status": "pass" if not trend_errors and trend.get("status") == "pass" else "invalid",
        "present": trend_errors == [] and trend.get("status") == "pass",
        "required": required,
        "snapshot_count": int(metrics.get("snapshot_count", 0)),
        "geometry_verified_count": int(metrics.get("geometry_verified_count", 0)),
        "non_cad_only": bool(metrics.get("non_cad_only", True)),
        "metrics": metrics,
    }


def _coverage_headline_from_panel(panel: dict[str, Any]) -> dict[str, Any]:
    metrics = panel.get("metrics") if isinstance(panel.get("metrics"), dict) else {}
    latest = metrics.get("latest_snapshot_metrics")
    if not isinstance(latest, dict):
        latest = metrics
    return {
        "source_path": panel.get("trend_report_path", ""),
        "cad_strength_headline_percent": float(latest.get("cad_strength_headline_percent", 0.0)),
        "cad_proof_coverage_percent": float(latest.get("cad_proof_coverage_percent", 0.0)),
        "highest_proven_ladder_level": str(latest.get("highest_proven_ladder_level", "")),
        "verified_count": latest.get("verified_count"),
        "showcase_count": latest.get("showcase_count"),
        "total_count": latest.get("total_count"),
    }


def build_capability_trend_dashboard(
    *,
    project_root: Path,
    sources: dict[str, Any],
    output_dir: Path,
    generated_at: str | None = None,
) -> dict[str, Any]:
    panels = [
        build_trend_dashboard_panel(project_root=project_root, panel=panel, output_dir=output_dir)
        for panel in sources.get("panels", [])
        if isinstance(panel, dict)
    ]
    if not panels:
        raise ValueError("trend dashboard requires at least one panel")

    required_panels = [panel for panel in panels if panel.get("required")]
    present_panels = [panel for panel in panels if panel.get("present")]
    all_required_present = all(panel.get("present") for panel in required_panels)
    all_trend_pass = all(panel.get("trend_status") == "pass" for panel in present_panels)

    coverage_panel = next((panel for panel in panels if panel.get("panel_id") == "capability_coverage"), None)
    if coverage_panel is None or not coverage_panel.get("present"):
        status = "blocked"
        coverage_headline = {
            "source_path": "",
            "cad_strength_headline_percent": 0.0,
            "cad_proof_coverage_percent": 0.0,
        }
    else:
        coverage_headline = _coverage_headline_from_panel(coverage_panel)
        status = "pass" if all_required_present and all_trend_pass else "blocked"

    dashboard = {
        "version": "0.1",
        "package_id": VPROOF_71_PACKAGE_ID,
        "status": status,
        "generated_at": generated_at or _utc_now_iso(),
        "boundary_doc": VPROOF_71_EVIDENCE_BOUNDARY_DOC,
        "panels": panels,
        "coverage_headline": coverage_headline,
        "summary": {
            "panel_count": len(panels),
            "required_panel_count": len(required_panels),
            "present_panel_count": len(present_panels),
            "all_required_present": all_required_present,
            "all_trend_reports_pass": all_trend_pass,
        },
        "notes": [
            "V-PROOF-71 absorbs LCAD-11.1~11.4 evidence trend outputs.",
            "Table C headline values are mirrored from capability_coverage panel only.",
            "Trend dashboard pass does not imply geometry_verified.",
        ],
    }
    return dashboard


def validate_capability_trend_dashboard(
    dashboard: dict[str, Any],
    *,
    project_root: Path,
) -> list[str]:
    schema = json.loads((project_root / DASHBOARD_SCHEMA_REL).read_text(encoding="utf-8"))
    return validate_value(dashboard, schema)


def merge_trend_dashboard_registry_rows(registry: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, int]:
    from core.verification.negative_plan_registry import merge_negative_plan_registry_rows

    return merge_negative_plan_registry_rows(registry, rows)


def build_trend_dashboard_registry_rows(*, output_root: str) -> list[dict[str, Any]]:
    dashboard_report = f"{output_root}/capability_trend_dashboard.json"

    def _row(capability_id: str, display_name: str, panel_id: str, source_key: str) -> dict[str, Any]:
        return {
            "capability_id": capability_id,
            "display_name": display_name,
            "category": "other",
            "claim_level": "smoke",
            "ladder_level": "L0",
            "domain": "generic",
            "tags": ["trend", "LCAD-11", "V-PROOF-71"],
            "notes": [
                "V-PROOF-71 trend dashboard smoke row.",
                "Dashboard pass is trend index only; not geometry_verified.",
            ],
            "source_refs": [
                {
                    "source_kind": "documentation",
                    "source_path": str(DEFAULT_SOURCES_REL).replace("\\", "/"),
                    "source_key": source_key,
                }
            ],
            "cad_case": {
                "case_kind": "script",
                "requires_real_cad": False,
                "entrypoint": "scripts/run_vproof_71_trend_dashboard_sync.py",
                "output_path": dashboard_report,
                "safety": dict(PREVIEW_SAFETY),
            },
        }

    return [
        _row(DASHBOARD_ROLLUP_CAPABILITY_ID, "Capability trend dashboard rollup", "rollup", "rollup"),
        _row(
            DASHBOARD_REGRESSION_CAPABILITY_ID,
            "Trend panel: local CAD regression",
            "local_cad_regression",
            "local_cad_regression",
        ),
        _row(
            DASHBOARD_VALIDATION_CAPABILITY_ID,
            "Trend panel: cad validation index",
            "cad_validation",
            CAD_VALIDATION_TREND_INDEX_FILENAME,
        ),
        _row(
            DASHBOARD_COVERAGE_CAPABILITY_ID,
            "Trend panel: capability coverage",
            "capability_coverage",
            "capability_coverage",
        ),
    ]


def apply_trend_dashboard_smoke_writeback(
    registry: dict[str, Any],
    *,
    capability_id: str,
    report_path: str,
    project_root: Path,
    row_index: dict[str, dict[str, Any]] | None = None,
    dry_run: bool = True,
) -> str:
    index = row_index or index_capability_rows(registry)
    row = index.get(capability_id)
    if row is None:
        return "not_found"
    if str(row.get("claim_level", "")) != "smoke":
        return "rejected"

    resolved = project_root / report_path.replace("\\", "/")
    if not resolved.is_file():
        return "rejected"
    payload = json.loads(resolved.read_text(encoding="utf-8"))
    if payload.get("status") != "pass":
        return "rejected"

    triplet = {
        "evidence_state": EVIDENCE_BENCHMARK_PASS_NON_CAD,
        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
    }
    if validate_evidence_triplet(triplet):
        return "rejected"
    if not dry_run:
        row["evidence"] = {**triplet, "report_path": report_path, "last_verified_at": _utc_now_iso()}
    return "applied"


def run_vproof_71_trend_dashboard_sync(
    *,
    project_root: Path,
    output_dir: Path,
    sources_path: Path | None = None,
    dry_run: bool = False,
    refresh_coverage: bool = True,
) -> dict[str, Any]:
    root = project_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_root = str(output_dir.relative_to(root)).replace("\\", "/")
    sources = load_trend_dashboard_sources(sources_path, project_root=root)

    if refresh_coverage:
        coverage_rel = str(sources.get("coverage_report_path", "")).replace("\\", "/")
        if coverage_rel:
            run_capability_coverage(root, output_path=root / coverage_rel)

    dashboard = build_capability_trend_dashboard(
        project_root=root,
        sources=sources,
        output_dir=output_dir,
    )
    schema_errors = validate_capability_trend_dashboard(dashboard, project_root=root)
    if schema_errors:
        dashboard["status"] = "invalid"
        dashboard["schema_errors"] = schema_errors

    dashboard_path = output_dir / "capability_trend_dashboard.json"
    dashboard_path.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if dashboard.get("status") != "pass":
        return {
            "package_id": VPROOF_71_PACKAGE_ID,
            "dashboard_status": dashboard.get("status"),
            "schema_errors": schema_errors,
            "output_root": output_root,
        }

    registry_path = root / "examples/capability_proof/cad_capability_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    rows = build_trend_dashboard_registry_rows(output_root=output_root)
    merge_trend_dashboard_registry_rows(registry, rows)
    index = index_capability_rows(registry)

    report_rel = f"{output_root}/capability_trend_dashboard.json"
    writeback_applied = 0
    writeback_rejected = 0
    targets = [DASHBOARD_ROLLUP_CAPABILITY_ID, *PANEL_CAPABILITY_IDS.values()]
    for capability_id in targets:
        status = apply_trend_dashboard_smoke_writeback(
            registry,
            capability_id=capability_id,
            report_path=report_rel,
            project_root=root,
            row_index=index,
            dry_run=dry_run,
        )
        if status == "applied":
            writeback_applied += 1
        else:
            writeback_rejected += 1

    if not dry_run:
        registry["updated_at"] = datetime.now(timezone.utc).date().isoformat()
        registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "package_id": VPROOF_71_PACKAGE_ID,
        "dashboard_status": dashboard.get("status"),
        "present_panel_count": dashboard["summary"]["present_panel_count"],
        "coverage_headline_percent": dashboard["coverage_headline"].get("cad_strength_headline_percent"),
        "registry_row_count": len(rows),
        "writeback_applied_count": writeback_applied,
        "writeback_rejected_count": writeback_rejected,
        "output_root": output_root,
    }


def assert_vproof_71_trend_dashboard_contract(*, project_root: Path) -> None:
    root = project_root.resolve()
    boundary = root / VPROOF_71_BOUNDARY_DOC
    if not boundary.is_file():
        raise AssertionError(f"missing boundary doc: {VPROOF_71_BOUNDARY_DOC}")

    registry = json.loads((root / "examples/capability_proof/cad_capability_registry.json").read_text(encoding="utf-8"))
    index = index_capability_rows(registry)
    for capability_id in (DASHBOARD_ROLLUP_CAPABILITY_ID, *PANEL_CAPABILITY_IDS.values()):
        if capability_id not in index:
            raise AssertionError(f"missing registry row: {capability_id}")

    schema_errors = validate_capability_registry(registry)
    if schema_errors:
        raise AssertionError(f"registry validation failed: {schema_errors[:3]}")
