"""Repository data-bloat audit for training workbench and short-lived artifacts."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from core.training.source_manifest import DEFAULT_MANIFEST_RELATIVE_PATH, training_sources


DEFAULT_CAPABILITY_MAP_PATH = Path("capability-map-data.js")
DEFAULT_COVERAGE_PATH = Path("output") / "validation_runs" / "capability-lab" / "cad_capability_coverage.json"
DEFAULT_OUTPUT_PATH = Path("output") / "validation_runs" / "data-bloat-audit" / "data_bloat_audit_report.json"
DEFAULT_SIZE_WARNING_BYTES = 2_000_000
DEFAULT_LINE_WARNING_COUNT = 30_000
LEGACY_WORKBENCH_ALIASES = {"capabilities", "agents", "stages", "coverageSnapshot"}
DERIVED_FACT_SOURCE_PATHS = {
    "capability-map-data.js",
    "capability-map.html",
    "output/validation_runs/training-workbench-sync/training_workbench_sync_report.json",
    "output/validation_runs/training-artifact-retention/retention_report.json",
    "output/validation_runs/data-bloat-audit/data_bloat_audit_report.json",
}
SHORT_LIVED_ROOTS = (Path("output") / "debug", Path("output") / "test_artifacts")
DATA_ASSIGNMENT_RE = re.compile(r"^\s*window\.CAD_CAPABILITY_MAP_DATA\s*=\s*(?P<payload>\{.*\})\s*;\s*$", re.S)


def _resolve_under_root(path: Path, root: Path) -> Path:
    resolved = path if path.is_absolute() else root / path
    resolved = resolved.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"path must stay under project root: {resolved}") from exc
    return resolved


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _manifest_path(row: dict[str, Any], root: Path) -> Path | None:
    raw_path = str(row.get("path", "")).strip()
    if not raw_path:
        return None
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def _read_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _load_workbench_payload(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    match = DATA_ASSIGNMENT_RE.match(text)
    if not match:
        return {}
    try:
        payload = json.loads(match.group("payload"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _file_stats(path: Path) -> dict[str, int | bool]:
    if not path.is_file():
        return {"exists": False, "bytes": 0, "lineCount": 0}
    data = path.read_bytes()
    return {
        "exists": True,
        "bytes": len(data),
        "lineCount": data.count(b"\n"),
    }


def _warning(code: str, message: str, *, severity: str = "warning", **extra: Any) -> dict[str, Any]:
    return {"code": code, "severity": severity, "message": message, **extra}


def _candidate_files(roots: Iterable[Path], root: Path, *, excluded_paths: set[str] | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    excluded_paths = excluded_paths or set()
    for relative_root in roots:
        scan_root = root / relative_root
        if not scan_root.exists():
            continue
        for path in sorted(item for item in scan_root.rglob("*") if item.is_file()):
            display_path = _display_path(path, root)
            if display_path in excluded_paths:
                continue
            rows.append(
                {
                    "path": display_path,
                    "kind": "short_lived_artifact",
                    "reason": "default_short_retention_root",
                    "bytes": path.stat().st_size,
                }
            )
    return rows


def _coverage_blockers(coverage_path: Path, root: Path) -> list[dict[str, Any]]:
    data = _read_json(coverage_path, {})
    audit = data.get("evidence_path_audit", {}) if isinstance(data, dict) else {}
    missing_count = int(audit.get("report_path_missing", 0) or 0)
    if missing_count <= 0:
        return []
    return [
        {
            "code": "coverage_report_path_missing",
            "severity": "blocked",
            "path": _display_path(coverage_path, root),
            "missingCount": missing_count,
            "missingReportPaths": audit.get("missing_report_paths", []) or audit.get("missingReportPaths", []),
            "message": "coverage evidence_path_audit still reports missing report paths.",
        }
    ]


def _manifest_classification(root: Path, manifest_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    protected: list[dict[str, Any]] = []
    derived: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    for row in training_sources(root, manifest_path=manifest_path, active_only=True):
        resolved = _manifest_path(row, root)
        display = _display_path(resolved, root) if resolved else ""
        role = row.get("role", "")
        item = {
            "id": row.get("id", ""),
            "kind": row.get("kind", ""),
            "role": role,
            "path": display,
            "exists": bool(resolved and resolved.is_file()),
        }
        if role == "derived":
            derived.append({**item, "reason": "derived_snapshot_not_fact_source"})
            continue
        if role == "fact_source":
            if display in DERIVED_FACT_SOURCE_PATHS:
                blocked.append(
                    {
                        **item,
                        "code": "derived_artifact_registered_as_fact_source",
                        "severity": "blocked",
                        "message": "derived snapshot/report must not be registered as an active fact_source.",
                    }
                )
                continue
            if item["exists"]:
                protected.append({**item, "reason": "active_fact_source"})
            else:
                blocked.append(
                    {
                        **item,
                        "code": "active_fact_source_missing",
                        "severity": "blocked",
                        "message": "active fact_source is declared but the file is missing.",
                    }
                )
    return protected, derived, blocked


def _capability_map_ratchet(
    snapshot_path: Path,
    root: Path,
    *,
    size_warning_bytes: int,
    line_warning_count: int,
) -> dict[str, Any]:
    stats = _file_stats(snapshot_path)
    payload = _load_workbench_payload(snapshot_path)
    warnings: list[dict[str, Any]] = []
    if not stats["exists"]:
        warnings.append(
            _warning(
                "capability_map_snapshot_missing",
                "capability-map-data.js is missing.",
                severity="blocked",
            )
        )
    if int(stats["bytes"]) > size_warning_bytes:
        warnings.append(
            _warning(
                "snapshot_size_warning",
                "capability-map-data.js is above the warning byte threshold.",
                bytes=stats["bytes"],
                thresholdBytes=size_warning_bytes,
            )
        )
    if int(stats["lineCount"]) > line_warning_count:
        warnings.append(
            _warning(
                "snapshot_line_warning",
                "capability-map-data.js is above the warning line threshold.",
                lineCount=stats["lineCount"],
                thresholdLines=line_warning_count,
            )
        )
    legacy_keys = sorted(LEGACY_WORKBENCH_ALIASES.intersection(payload))
    if legacy_keys:
        warnings.append(
            _warning(
                "legacy_alias_present",
                "workbench snapshot still contains legacy duplicate aliases.",
                keys=legacy_keys,
            )
        )
    return {
        "path": _display_path(snapshot_path, root),
        **stats,
        "warningCount": len(warnings),
        "warnings": warnings,
    }


def run_data_bloat_audit(
    *,
    project_root: Path,
    capability_map_path: Path = DEFAULT_CAPABILITY_MAP_PATH,
    training_source_manifest_path: Path = DEFAULT_MANIFEST_RELATIVE_PATH,
    coverage_path: Path = DEFAULT_COVERAGE_PATH,
    size_warning_bytes: int = DEFAULT_SIZE_WARNING_BYTES,
    line_warning_count: int = DEFAULT_LINE_WARNING_COUNT,
    output_path: Path | None = None,
    write: bool = False,
) -> dict[str, Any]:
    root = project_root.resolve()
    snapshot_path = _resolve_under_root(capability_map_path, root)
    manifest_path = _resolve_under_root(training_source_manifest_path, root)
    resolved_coverage_path = _resolve_under_root(coverage_path, root)
    protected, derived, manifest_blocked = _manifest_classification(root, manifest_path)
    coverage_blocked = _coverage_blockers(resolved_coverage_path, root)
    ratchet = {
        "capabilityMapData": _capability_map_ratchet(
            snapshot_path,
            root,
            size_warning_bytes=size_warning_bytes,
            line_warning_count=line_warning_count,
        )
    }
    ratchet_warnings = ratchet["capabilityMapData"]["warnings"]
    blocked = [
        *manifest_blocked,
        *coverage_blocked,
        *(item for item in ratchet_warnings if item.get("severity") == "blocked"),
    ]
    warning_count = sum(1 for item in ratchet_warnings if item.get("severity") != "blocked")
    excluded_candidate_paths = {item["path"] for item in [*protected, *derived, *blocked] if item.get("path")}
    candidates = _candidate_files(SHORT_LIVED_ROOTS, root, excluded_paths=excluded_candidate_paths)
    status = "blocked" if blocked else "warning" if warning_count else "pass"

    report: dict[str, Any] = {
        "version": "0.1",
        "status": status,
        "generatedAt": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "write": bool(write),
        "root": str(root),
        "policy": {
            "mode": "read_only_data_bloat_audit",
            "cleanup": False,
            "archive": False,
            "sizeWarningBytes": size_warning_bytes,
            "lineWarningCount": line_warning_count,
        },
        "ratchet": ratchet,
        "protected": protected,
        "derived": derived,
        "candidate": candidates,
        "blocked": blocked,
        "summary": {
            "protectedCount": len(protected),
            "derivedCount": len(derived),
            "candidateCount": len(candidates),
            "blockedCount": len(blocked),
            "warningCount": warning_count,
        },
        "outputPath": None,
    }

    if write and output_path:
        resolved_output = _resolve_under_root(output_path, root)
        resolved_output.parent.mkdir(parents=True, exist_ok=True)
        resolved_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report["outputPath"] = _display_path(resolved_output, root)
    return report
