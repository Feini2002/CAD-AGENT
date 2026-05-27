"""Human-readable capability proof grouping for coverage reports."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.path_safety import find_project_root, resolve_under_project_output, resolve_under_project_root
from core.verification.capability_coverage import DEFAULT_REGISTRY_PATH, run_capability_coverage
from core.verification.capability_registry import load_capability_registry
from core.verification.evidence_vocabulary import (
    EVIDENCE_NEGATIVE_GUARD_VERIFIED,
    GEOMETRY_VERIFIED_EVIDENCE_STATES,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")


def _row_summary(row: dict[str, Any]) -> dict[str, Any]:
    evidence = row.get("evidence") if isinstance(row.get("evidence"), dict) else {}
    cad_case = row.get("cad_case") if isinstance(row.get("cad_case"), dict) else {}
    return {
        "capability_id": row.get("capability_id"),
        "display_name": row.get("display_name"),
        "category": row.get("category"),
        "domain": row.get("domain", "generic"),
        "claim_level": row.get("claim_level"),
        "ladder_level": row.get("ladder_level"),
        "evidence_state": evidence.get("evidence_state"),
        "geometry_accuracy": evidence.get("geometry_accuracy"),
        "report_path": evidence.get("report_path"),
        "deferred_reason": row.get("deferred_reason"),
        "entrypoint": cad_case.get("entrypoint"),
    }


def _sample(rows: list[dict[str, Any]], limit: int = 12) -> list[dict[str, Any]]:
    return [_row_summary(row) for row in rows[:limit]]


def _load_guard_report(path: Path, *, project_root: Path) -> dict[str, Any]:
    report_path = resolve_under_project_root(project_root, path, label="guard_report_path")
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Guard report must be an object: {report_path}")
    return {
        "path": _rel(report_path, project_root),
        "status": payload.get("status"),
        "suite_id": payload.get("suite_id"),
        "evidence_state": payload.get("evidence_state"),
        "created_handles": payload.get("created_handles", []),
        "safety": payload.get("safety", {}),
    }


def build_capability_readability_report(
    registry: dict[str, Any],
    coverage_report: dict[str, Any],
    *,
    project_root: Path,
    guard_reports: list[dict[str, Any]] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    rows = [row for row in registry.get("capabilities", []) if isinstance(row, dict)]
    geometry_rows = [
        row
        for row in rows
        if isinstance(row.get("evidence"), dict)
        and row["evidence"].get("evidence_state") in GEOMETRY_VERIFIED_EVIDENCE_STATES
    ]
    deferred_rows = [row for row in rows if row.get("claim_level") == "deferred"]
    smoke_rows = [row for row in rows if row.get("claim_level") == "smoke"]
    none_rows = [row for row in rows if row.get("claim_level") == "none"]
    blocked_rows = [
        row
        for row in deferred_rows
        if "blocked" in str(row.get("deferred_reason", "")).lower()
        or "hatch" in str(row.get("capability_id", "")).lower()
    ]
    verified_guard_reports = [
        report
        for report in guard_reports or []
        if report.get("status") == "pass"
        and report.get("evidence_state") == EVIDENCE_NEGATIVE_GUARD_VERIFIED
        and report.get("created_handles") == []
    ]

    coverage_summary = coverage_report.get("summary", {}) if isinstance(coverage_report, dict) else {}
    recommended = deferred_rows[:8] + none_rows[:4]
    return {
        "version": "0.1",
        "report_id": "cad-capability-readability",
        "status": "pass",
        "generated_at": generated_at or _utc_now_iso(),
        "coverage_report_id": coverage_report.get("report_id"),
        "summary": {
            "total_count": coverage_summary.get("total_count", len(rows)),
            "cad_proof_coverage_percent": coverage_summary.get("cad_proof_coverage_percent", 0.0),
            "verified_geometry_count": len(geometry_rows),
            "verified_guard_count": len(verified_guard_reports),
            "deferred_cad_count": len(deferred_rows),
            "smoke_only_count": len(smoke_rows),
            "none_count": len(none_rows),
            "blocked_count": len(blocked_rows),
        },
        "readable_sections": {
            "what_can_be_claimed_as_geometry": {
                "meaning": "Rows with geometry-verified evidence_state; these may support limited CAD geometry claims.",
                "count": len(geometry_rows),
                "sample": _sample(geometry_rows),
            },
            "what_is_guard_only": {
                "meaning": "Negative guard evidence proves forbidden writes were blocked; it is not positive geometry proof.",
                "count": len(verified_guard_reports),
                "reports": verified_guard_reports,
            },
            "what_is_deferred": {
                "meaning": "Registered rows that still require real CAD readback or an explicit blocker resolution.",
                "count": len(deferred_rows),
                "sample": _sample(deferred_rows),
            },
            "what_is_smoke_only": {
                "meaning": "Rows with smoke/non-CAD proof only; do not treat these as geometry verified.",
                "count": len(smoke_rows),
                "sample": _sample(smoke_rows),
            },
            "what_has_no_proof": {
                "meaning": "Inventory rows with no CAD proof yet.",
                "count": len(none_rows),
                "sample": _sample(none_rows),
            },
            "known_blockers": {
                "meaning": "Deferred rows likely blocked by implementation or CAD capability gaps.",
                "count": len(blocked_rows),
                "sample": _sample(blocked_rows),
            },
        },
        "recommended_next_capability_ids": [
            str(row.get("capability_id")) for row in recommended if row.get("capability_id")
        ],
        "notes": [
            "Geometry claims require readback_geometry_verified or cad_capability_verified evidence.",
            "negative_guard_verified is safety evidence only and must not be counted as geometry accuracy.",
            "Screenshots remain visual aids unless paired with created-handle readback.",
        ],
    }


def run_capability_readability_report(
    project_root: Path,
    *,
    registry_path: Path | None = None,
    output_dir: Path | None = None,
    guard_report_paths: list[Path] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    root = project_root.resolve()
    registry_file = registry_path or (root / DEFAULT_REGISTRY_PATH)
    registry = load_capability_registry(registry_file, project_root=root)
    coverage = run_capability_coverage(
        root,
        registry_path=registry_file,
        output_path=None,
        generated_at=generated_at,
    )
    if coverage.get("status") != "pass":
        return {
            "version": "0.1",
            "report_id": "cad-capability-readability",
            "status": "invalid",
            "generated_at": generated_at or _utc_now_iso(),
            "coverage_errors": coverage.get("errors", []),
        }

    guard_reports = [
        _load_guard_report(path, project_root=root)
        for path in guard_report_paths or []
    ]
    report = build_capability_readability_report(
        registry,
        coverage,
        project_root=root,
        guard_reports=guard_reports,
        generated_at=generated_at,
    )
    if output_dir is not None:
        target_dir = resolve_under_project_output(root, output_dir, label="output_dir")
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "capability_readability_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        report["output_path"] = _rel(target_dir / "capability_readability_report.json", root)
    return report


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Build a readable CAD capability coverage report.")
    parser.add_argument("--root", type=Path, default=find_project_root(Path(__file__)))
    parser.add_argument("--registry-path", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--output-dir", type=Path, default=Path("output/validation_runs/capability-lab-readability"))
    parser.add_argument(
        "--guard-report",
        action="append",
        type=Path,
        default=[],
        help="Optional negative_cad_runner_report.json path to include as guard-only proof.",
    )
    args = parser.parse_args()

    report = run_capability_readability_report(
        args.root,
        registry_path=args.registry_path,
        output_dir=args.output_dir,
        guard_report_paths=args.guard_report,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
