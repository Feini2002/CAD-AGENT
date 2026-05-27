"""RCAD / verification report write-back into cad_capability_registry rows (V-PROOF-03)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.path_safety import resolve_under_project_output, resolve_under_project_root
from core.verification.capability_registry import (
    index_capability_rows,
    load_capability_registry,
    save_capability_registry,
    validate_capability_registry,
)
from core.verification.capability_registry_seed import _slug
from core.verification.evidence_contract import (
    is_geometry_verified_evidence_state,
    validate_evidence_triplet,
)
from core.verification.evidence_vocabulary import (
    EVIDENCE_CAD_CAPABILITY_VERIFIED,
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE,
    GEOMETRY_VERIFIED_BY_READBACK,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
    SCREENSHOT_VISUAL_AID_ONLY,
)

DEFAULT_MANIFEST_PATH = Path("examples/cad_regression/local_cad_regression_manifest.json")

GEOMETRY_STATUSES = frozenset(
    {
        "geometry_verified",
        "cad_capability_verified",
        "readback_geometry_verified",
    }
)

REPORT_FILE_CANDIDATES = (
    "readback_report.json",
    "block_alpha_report.json",
    "cad_capability_probe.json",
    "cad_plan_fixture_suite_report.json",
    "complex_cad_smoke_report.json",
    "primitive_matrix_report.json",
    "project_sample_cad_check_report.json",
    "composition_cad_check_report.json",
    "report.json",
)


@dataclass
class WritebackRequest:
    capability_id: str
    report_path: str
    claim_level: str = "verified"
    last_verified_at: str | None = None
    note: str | None = None


@dataclass
class WritebackResult:
    capability_id: str
    status: str
    message: str
    previous_claim_level: str | None = None
    new_claim_level: str | None = None
    report_path: str | None = None


@dataclass
class WritebackBatchReport:
    version: str = "0.1"
    status: str = "pass"
    dry_run: bool = True
    registry_path: str = ""
    applied_count: int = 0
    skipped_count: int = 0
    rejected_count: int = 0
    not_found_count: int = 0
    results: list[WritebackResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "status": self.status,
            "dry_run": self.dry_run,
            "registry_path": self.registry_path,
            "summary": {
                "applied_count": self.applied_count,
                "skipped_count": self.skipped_count,
                "rejected_count": self.rejected_count,
                "not_found_count": self.not_found_count,
            },
            "results": [
                {
                    "capability_id": item.capability_id,
                    "status": item.status,
                    "message": item.message,
                    "previous_claim_level": item.previous_claim_level,
                    "new_claim_level": item.new_claim_level,
                    "report_path": item.report_path,
                }
                for item in self.results
            ],
            "errors": self.errors,
        }


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel_path(path: Path, project_root: Path) -> str:
    return str(path.resolve().relative_to(project_root.resolve())).replace("\\", "/")


def capability_id_for_regression_case(case_id: str) -> str:
    return f"regression.{_slug(case_id)}"


def capability_id_for_benchmark_case(suite_id: str, case_id: str) -> str:
    return f"benchmark.{_slug(suite_id)}.{_slug(case_id)}"


def load_verification_report_file(path: Path, *, project_root: Path) -> dict[str, Any]:
    resolved = resolve_under_project_root(project_root, path, label="report_path")
    if not resolved.is_file():
        raise FileNotFoundError(f"Verification report not found: {resolved}")
    payload = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Verification report must be a JSON object.")
    return payload


def _infer_triplet_from_status(status: str) -> dict[str, str] | None:
    if status == "geometry_verified":
        return {
            "evidence_state": EVIDENCE_READBACK_GEOMETRY_VERIFIED,
            "geometry_accuracy": GEOMETRY_VERIFIED_BY_READBACK,
            "screenshot_role": SCREENSHOT_VISUAL_AID_ONLY,
        }
    if status == "cad_capability_verified":
        return {
            "evidence_state": EVIDENCE_CAD_CAPABILITY_VERIFIED,
            "geometry_accuracy": GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE,
            "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
        }
    if status == "readback_geometry_verified":
        return {
            "evidence_state": EVIDENCE_READBACK_GEOMETRY_VERIFIED,
            "geometry_accuracy": GEOMETRY_VERIFIED_BY_READBACK,
            "screenshot_role": SCREENSHOT_VISUAL_AID_ONLY,
        }
    return None


def _triplet_from_payload(payload: dict[str, Any]) -> dict[str, str] | None:
    evidence_state = payload.get("evidence_state")
    geometry_accuracy = payload.get("geometry_accuracy")
    screenshot_role = payload.get("screenshot_role")
    status = str(payload.get("status", ""))

    if not evidence_state and status in GEOMETRY_STATUSES:
        inferred = _infer_triplet_from_status(status)
        if inferred:
            evidence_state = inferred["evidence_state"]
            geometry_accuracy = inferred.get("geometry_accuracy", geometry_accuracy)
            screenshot_role = inferred.get("screenshot_role", screenshot_role)

    if not isinstance(evidence_state, str) or not evidence_state:
        return None
    if not isinstance(geometry_accuracy, str) or not geometry_accuracy:
        if evidence_state == EVIDENCE_CAD_CAPABILITY_VERIFIED:
            geometry_accuracy = GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE
        elif is_geometry_verified_evidence_state(evidence_state):
            geometry_accuracy = GEOMETRY_VERIFIED_BY_READBACK
        else:
            geometry_accuracy = NON_CAD_GEOMETRY_ACCURACY
    if not isinstance(screenshot_role, str) or not screenshot_role:
        screenshot_role = (
            SCREENSHOT_NOT_APPLICABLE
            if evidence_state == EVIDENCE_CAD_CAPABILITY_VERIFIED
            else SCREENSHOT_VISUAL_AID_ONLY
        )

    triplet = {
        "evidence_state": evidence_state,
        "geometry_accuracy": geometry_accuracy,
        "screenshot_role": screenshot_role,
    }
    if validate_evidence_triplet(triplet):
        return None
    if not is_geometry_verified_evidence_state(evidence_state):
        return None
    return triplet


def extract_geometry_evidence_from_report(
    report: dict[str, Any],
    *,
    report_path: Path | None = None,
    project_root: Path | None = None,
) -> tuple[dict[str, str] | None, str]:
    direct = _triplet_from_payload(report)
    if direct:
        return direct, ""

    evidence_summary = report.get("evidence_summary")
    if (
        isinstance(evidence_summary, dict)
        and report.get("status") == "pass"
        and not evidence_summary.get("non_cad_only", True)
        and int(evidence_summary.get("geometry_verified_count") or 0) > 0
    ):
        triplet = _triplet_from_payload(evidence_summary)
        if triplet:
            return triplet, ""

    steps = report.get("steps")
    if isinstance(steps, list):
        for step in steps:
            if not isinstance(step, dict):
                continue
            triplet = _triplet_from_payload(step)
            if triplet:
                return triplet, ""

    if report_path is not None and project_root is not None:
        case_dir = report_path.parent
        for name in REPORT_FILE_CANDIDATES:
            if report_path.name == name:
                continue
            sibling = case_dir / name
            if not sibling.is_file():
                continue
            try:
                sibling_report = load_verification_report_file(sibling, project_root=project_root)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            triplet = _triplet_from_payload(sibling_report)
            if triplet:
                return triplet, ""

    status = str(report.get("status", ""))
    if status in GEOMETRY_STATUSES:
        triplet = _infer_triplet_from_status(status)
        if triplet and not validate_evidence_triplet(triplet):
            return triplet, ""

    if report.get("evidence_state") == EVIDENCE_DEFERRED_CAD_READBACK:
        return None, "report declares deferred_cad_readback_required"
    return None, "report does not declare geometry-verified evidence"


def apply_writeback(
    registry: dict[str, Any],
    request: WritebackRequest,
    *,
    project_root: Path,
    row_index: dict[str, dict[str, Any]] | None = None,
    dry_run: bool = True,
) -> WritebackResult:
    index = row_index or index_capability_rows(registry)
    capability_id = request.capability_id
    row = index.get(capability_id)
    if row is None:
        return WritebackResult(
            capability_id=capability_id,
            status="not_found",
            message=f"Unknown capability_id: {capability_id}",
        )

    if request.claim_level not in {"verified", "showcase"}:
        return WritebackResult(
            capability_id=capability_id,
            status="rejected",
            message=f"Unsupported claim_level for writeback: {request.claim_level}",
            previous_claim_level=str(row.get("claim_level", "")),
        )

    try:
        report_path = resolve_under_project_root(project_root, Path(request.report_path), label="report_path")
        report = load_verification_report_file(report_path, project_root=project_root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return WritebackResult(
            capability_id=capability_id,
            status="rejected",
            message=str(exc),
            previous_claim_level=str(row.get("claim_level", "")),
            report_path=request.report_path,
        )

    triplet, reason = extract_geometry_evidence_from_report(
        report,
        report_path=report_path,
        project_root=project_root,
    )
    if triplet is None:
        return WritebackResult(
            capability_id=capability_id,
            status="rejected",
            message=reason or "not geometry verified",
            previous_claim_level=str(row.get("claim_level", "")),
            report_path=_rel_path(report_path, project_root),
        )

    previous = str(row.get("claim_level", ""))
    rel_report = _rel_path(report_path, project_root)
    if previous == request.claim_level and row.get("evidence", {}).get("report_path") == rel_report:
        return WritebackResult(
            capability_id=capability_id,
            status="skipped",
            message="Registry row already reflects this report and claim_level.",
            previous_claim_level=previous,
            new_claim_level=previous,
            report_path=rel_report,
        )

    if not dry_run:
        row["claim_level"] = request.claim_level
        row.pop("deferred_reason", None)
        row["evidence"] = {
            **triplet,
            "report_path": rel_report,
            "last_verified_at": request.last_verified_at or _utc_now_iso(),
        }
        cad_case = row.get("cad_case")
        if not isinstance(cad_case, dict) or cad_case.get("case_kind") in {None, "", "none"}:
            row["cad_case"] = {
                "case_kind": "script",
                "requires_real_cad": True,
                "entrypoint": "scripts/run_cad_validation.py",
                "output_path": rel_report,
                "safety": {
                    "layer": "CODEX_PREVIEW",
                    "saved_dwg": False,
                    "deleted_entities": False,
                    "modified_formal_layers": False,
                },
            }
        notes = row.get("notes")
        if not isinstance(notes, list):
            notes = []
        note = request.note or f"writeback from {rel_report}"
        if note not in notes:
            notes.append(note)
        row["notes"] = notes

    return WritebackResult(
        capability_id=capability_id,
        status="applied",
        message="claim_level upgraded from verification report." if not dry_run else "dry-run: would upgrade claim_level.",
        previous_claim_level=previous,
        new_claim_level=request.claim_level,
        report_path=rel_report,
    )


def apply_writebacks(
    registry: dict[str, Any],
    requests: list[WritebackRequest],
    *,
    project_root: Path,
    dry_run: bool = True,
) -> WritebackBatchReport:
    index = index_capability_rows(registry)
    batch = WritebackBatchReport(dry_run=dry_run)
    for request in requests:
        result = apply_writeback(registry, request, project_root=project_root, row_index=index, dry_run=dry_run)
        batch.results.append(result)
        if result.status == "applied":
            batch.applied_count += 1
        elif result.status == "skipped":
            batch.skipped_count += 1
        elif result.status == "not_found":
            batch.not_found_count += 1
        else:
            batch.rejected_count += 1
    if batch.rejected_count or batch.not_found_count:
        batch.status = "fail"
    return batch


def suggest_writebacks_from_regression_output(
    project_root: Path,
    *,
    output_dir: Path,
    manifest_path: Path | None = None,
) -> list[WritebackRequest]:
    root = project_root.resolve()
    manifest_file = manifest_path or (root / DEFAULT_MANIFEST_PATH)
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    run_root = resolve_under_project_output(root, output_dir, label="output_dir")
    suggestions: list[WritebackRequest] = []

    for case in manifest.get("cases", []):
        if not isinstance(case, dict):
            continue
        if not case.get("requires_real_cad", True):
            continue
        case_id = str(case.get("id", ""))
        output_rel = str(case.get("output_path", ""))
        if not case_id or not output_rel:
            continue
        primary = run_root / Path(output_rel.replace("/", "\\") if "\\" in output_rel else output_rel)
        candidates = [primary, *(run_root / primary.parent / name for name in REPORT_FILE_CANDIDATES)]
        seen: set[str] = set()
        for candidate in candidates:
            resolved = str(candidate.resolve())
            if resolved in seen or not candidate.is_file():
                continue
            seen.add(resolved)
            try:
                report = load_verification_report_file(candidate, project_root=root)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            triplet, _ = extract_geometry_evidence_from_report(
                report,
                report_path=candidate,
                project_root=root,
            )
            if triplet is None:
                continue
            suggestions.append(
                WritebackRequest(
                    capability_id=capability_id_for_regression_case(case_id),
                    report_path=_rel_path(candidate, root),
                    note=f"auto-suggested from regression case {case_id}",
                )
            )
            break
    return suggestions


def run_registry_writeback(
    project_root: Path,
    *,
    registry_path: Path,
    requests: list[WritebackRequest],
    dry_run: bool = True,
    save_registry_file: bool = False,
    batch_output_path: Path | None = None,
) -> WritebackBatchReport:
    root = project_root.resolve()
    registry_file = resolve_under_project_root(root, registry_path, label="registry_path")
    registry = load_capability_registry(registry_file, project_root=root)
    validation_errors = validate_capability_registry(registry)
    if validation_errors:
        batch = WritebackBatchReport(dry_run=dry_run, registry_path=_rel_path(registry_file, root), status="invalid")
        batch.errors = validation_errors
        return batch

    batch = apply_writebacks(registry, requests, project_root=root, dry_run=dry_run)
    batch.registry_path = _rel_path(registry_file, root)

    if save_registry_file and not dry_run and batch.applied_count > 0:
        registry["updated_at"] = _utc_now_iso()[:10]
        post_errors = save_capability_registry(registry, registry_file, project_root=root)
        if post_errors:
            batch.status = "invalid"
            batch.errors = post_errors
    elif batch.rejected_count or batch.not_found_count:
        batch.status = "fail"

    if batch_output_path is not None:
        target = resolve_under_project_output(root, batch_output_path, label="batch_output_path")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(batch.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return batch
