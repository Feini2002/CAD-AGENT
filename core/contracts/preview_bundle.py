"""Phase 9 read-only preview bundle producer.

The bundle is a view over an existing Phase 9 run directory. It copies
selected JSON artifacts into a stable, relative-path bundle layout for humans
and agents to inspect. It does not create CAD evidence or upgrade completion.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from core.path_safety import find_project_root, resolve_under_project_output


BUNDLE_RESULT_SCHEMA = "phase9-preview-bundle-result/v1"
BUNDLE_SCHEMA = "phase9-preview-bundle/v1"
BUNDLE_SUMMARY_SCHEMA = "phase9-preview-bundle-summary/v1"
BUNDLE_SESSION_SCHEMA = "phase9-preview-session/v1"
BUNDLE_TRAJECTORY_SCHEMA = "phase9-preview-trajectory/v1"
DEFAULT_BUNDLE_DIRNAME = "preview_bundle"


@dataclass(frozen=True)
class Phase9PreviewBundleResult:
    schema_version: str
    status: str
    verification_status: str
    cad_geometry_verified: bool
    run_dir: str
    bundle_dir: str
    manifest_path: str
    summary_path: str
    session_path: str
    trajectory_path: str
    evidence_package_ref: str
    missing_evidence: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    artifacts: dict[str, dict[str, str]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schemaVersion": self.schema_version,
            "status": self.status,
            "verificationStatus": self.verification_status,
            "cadGeometryVerified": self.cad_geometry_verified,
            "runDir": self.run_dir,
            "bundleDir": self.bundle_dir,
            "manifestPath": self.manifest_path,
            "summaryPath": self.summary_path,
            "sessionPath": self.session_path,
            "trajectoryPath": self.trajectory_path,
            "evidencePackageRef": self.evidence_package_ref,
            "missingEvidence": list(self.missing_evidence),
            "blockingReasons": list(self.blocking_reasons),
            "warnings": list(self.warnings),
            "artifacts": dict(self.artifacts),
        }


def build_phase9_preview_bundle(
    *,
    run_dir: str | Path,
    bundle_dir: str | Path | None = None,
    include_session: bool = True,
    include_trajectory: bool = True,
) -> dict[str, Any]:
    """Build a read-only preview bundle for an existing Phase 9 run."""

    project_root = find_project_root(Path.cwd())
    resolved_run_dir = resolve_under_project_output(project_root, Path(run_dir), label="phase9 run_dir")
    if not resolved_run_dir.is_dir():
        raise ValueError(f"phase9 run dir does not exist: {resolved_run_dir}")
    resolved_bundle_dir = _resolve_bundle_dir(project_root, resolved_run_dir, bundle_dir)
    artifacts_dir = resolved_bundle_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    report_path = resolved_run_dir / "phase9_preview_report.json"
    if not report_path.is_file():
        raise ValueError(f"phase9 report missing: {report_path}")
    report = _read_json(report_path)
    report_artifacts = dict(report.get("artifacts") if isinstance(report.get("artifacts"), dict) else {})
    report_artifacts.setdefault("report", str(report_path))

    artifacts, warnings = _copy_report_artifacts(
        run_dir=resolved_run_dir,
        artifacts_dir=artifacts_dir,
        report_artifacts=report_artifacts,
    )
    summary = _build_summary(report=report, artifacts=artifacts, warnings=warnings)
    summary_path = resolved_bundle_dir / "summary.json"
    _write_json(summary_path, summary)

    session_path = ""
    if include_session:
        session_path_obj = resolved_bundle_dir / "session.json"
        _write_json(session_path_obj, _build_session(report=report, summary=summary))
        session_path = str(session_path_obj)

    trajectory_path = ""
    if include_trajectory:
        trajectory_path_obj = resolved_bundle_dir / "trajectory.json"
        _write_json(trajectory_path_obj, _build_trajectory(report=report, summary=summary))
        trajectory_path = str(trajectory_path_obj)

    manifest = {
        "schemaVersion": BUNDLE_SCHEMA,
        "phase": "Phase 9",
        "packageId": str(report.get("packageId") or ""),
        "taskId": str(report.get("taskId") or ""),
        "sourceRunDir": ".",
        "summary": "summary.json",
        "session": "session.json" if session_path else "",
        "trajectory": "trajectory.json" if trajectory_path else "",
        "artifactsDir": "artifacts",
        "artifacts": artifacts,
        "warnings": warnings,
        "completionBoundary": "preview_bundle_is_read_only_not_readback_evidence",
    }
    manifest_path = resolved_bundle_dir / "manifest.json"
    _write_json(manifest_path, manifest)

    result = Phase9PreviewBundleResult(
        schema_version=BUNDLE_RESULT_SCHEMA,
        status=summary["status"],
        verification_status=summary["verificationStatus"],
        cad_geometry_verified=bool(summary["cadGeometryVerified"]),
        run_dir=str(resolved_run_dir),
        bundle_dir=str(resolved_bundle_dir),
        manifest_path=str(manifest_path),
        summary_path=str(summary_path),
        session_path=session_path,
        trajectory_path=trajectory_path,
        evidence_package_ref=str(summary.get("evidencePackageRef") or ""),
        missing_evidence=[str(item) for item in summary.get("missingEvidence", [])],
        blocking_reasons=[str(item) for item in summary.get("blockingReasons", [])],
        warnings=warnings,
        artifacts=artifacts,
    )
    return result.to_dict()


def _resolve_bundle_dir(project_root: Path, run_dir: Path, bundle_dir: str | Path | None) -> Path:
    candidate = run_dir / DEFAULT_BUNDLE_DIRNAME if bundle_dir is None else Path(bundle_dir)
    resolved = resolve_under_project_output(project_root, candidate, label="phase9 preview bundle_dir")
    if not resolved.is_relative_to(run_dir):
        raise ValueError("phase9 preview bundle_dir must stay under the source run_dir")
    return resolved


def _copy_report_artifacts(
    *,
    run_dir: Path,
    artifacts_dir: Path,
    report_artifacts: dict[str, Any],
) -> tuple[dict[str, dict[str, str]], list[str]]:
    copied: dict[str, dict[str, str]] = {}
    warnings: list[str] = []
    for artifact_key, source_ref in _artifact_source_refs(report_artifacts):
        source_path = Path(source_ref)
        if not source_path.is_absolute():
            source_path = run_dir / source_path
        source_path = source_path.resolve()
        if not source_path.is_file() or not source_path.is_relative_to(run_dir):
            warnings.append(f"artifact_source_not_traceable:{artifact_key}")
            continue
        artifact_id = source_path.stem
        destination = artifacts_dir / source_path.name
        if source_path != destination.resolve():
            shutil.copyfile(source_path, destination)
        copied[artifact_id] = {
            "path": _posix_relative(destination, artifacts_dir.parent),
            "sourceRef": str(source_path),
            "mediaType": _media_type(destination),
            "role": _artifact_role(artifact_id),
        }
    return dict(sorted(copied.items())), _unique(warnings)


def _artifact_source_refs(report_artifacts: dict[str, Any]) -> list[tuple[str, str]]:
    refs = [
        (str(key), str(value))
        for key, value in report_artifacts.items()
        if key != "outputDir" and isinstance(value, str) and value
    ]
    return sorted(set(refs), key=lambda item: (item[1], item[0]))


def _build_summary(
    *,
    report: dict[str, Any],
    artifacts: dict[str, dict[str, str]],
    warnings: list[str],
) -> dict[str, Any]:
    report_artifacts = dict(report.get("artifacts") if isinstance(report.get("artifacts"), dict) else {})
    evidence_ref = str(report_artifacts.get("evidencePackage") or "")
    return {
        "schemaVersion": BUNDLE_SUMMARY_SCHEMA,
        "phase": "Phase 9",
        "packageId": str(report.get("packageId") or ""),
        "taskId": str(report.get("taskId") or ""),
        "status": str(report.get("status") or "not_verified"),
        "verificationStatus": str(report.get("verificationStatus") or "not_verified"),
        "cadGeometryVerified": bool(report.get("cadGeometryVerified") is True),
        "targetLayer": str(report.get("targetLayer") or ""),
        "savedCurrentDwg": bool(report.get("savedCurrentDwg", False)),
        "createdHandleCount": int(report.get("createdHandleCount") or 0),
        "readbackEntityCount": int(report.get("readbackEntityCount") or 0),
        "missingEvidence": [str(item) for item in report.get("missingEvidence", [])],
        "blockingReasons": [str(item) for item in report.get("blockingReasons", [])],
        "bundleWarnings": list(warnings),
        "evidencePackageRef": evidence_ref,
        "evidenceContentHash": str(report.get("evidenceContentHash") or ""),
        "sourceReport": (artifacts.get("phase9_preview_report") or {}).get("path", ""),
        "completionBoundary": "preview_bundle_is_read_only_not_readback_evidence",
        "notEvidenceFor": ["real_cad_readback", "cad_geometry_verified", "phase10_exit"],
    }


def _build_session(*, report: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": BUNDLE_SESSION_SCHEMA,
        "generatedAt": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "taskId": summary["taskId"],
        "status": summary["status"],
        "verificationStatus": summary["verificationStatus"],
        "cadGeometryVerified": summary["cadGeometryVerified"],
        "events": [
            {
                "name": "phase9_report_loaded",
                "status": summary["status"],
                "sourceSchemaVersion": str(report.get("schemaVersion") or ""),
            },
            {
                "name": "preview_bundle_materialized",
                "status": "read_only",
                "boundary": summary["completionBoundary"],
            },
        ],
    }


def _build_trajectory(*, report: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": BUNDLE_TRAJECTORY_SCHEMA,
        "taskId": summary["taskId"],
        "steps": [
            {
                "name": "cad_plan_validate",
                "status": str(report.get("validationStatus") or ""),
            },
            {
                "name": "cad_plan_dry_run",
                "status": str(report.get("dryRunStatus") or ""),
            },
            {
                "name": "created_handles_readback",
                "status": "observed" if summary["readbackEntityCount"] else "not_verified",
            },
            {
                "name": "completion_judge",
                "status": summary["verificationStatus"],
                "missingEvidence": list(summary["missingEvidence"]),
            },
        ],
        "boundary": summary["completionBoundary"],
    }


def _artifact_role(artifact_id: str) -> str:
    if artifact_id.endswith("cad_plan"):
        return "input"
    if artifact_id.endswith("report"):
        return "report"
    if "evidence" in artifact_id or "ledger" in artifact_id:
        return "evidence_ref"
    return "supporting"


def _media_type(path: Path) -> str:
    if path.suffix.casefold() == ".json":
        return "application/json"
    return "application/octet-stream"


def _posix_relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


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


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
