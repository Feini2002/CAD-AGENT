"""DRAW-02: bind drawing_standard beta suite cases to cad_capability_registry rows."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.drawing_standard.drawing_standard_profile import DEFAULT_DRAWING_STANDARD_PROFILE_ID
from core.schemas.registry import get_schema_path
from core.verification.capability_registry import index_capability_rows, validate_capability_registry
from core.verification.capability_registry_seed_common import PREVIEW_SAFETY, _slug
from core.verification.drawing_standard_beta_suite import (
    default_suite_path,
    load_drawing_standard_beta_suite,
    run_drawing_standard_beta_suite,
)
from core.verification.evidence_contract import validate_evidence_triplet
from core.verification.evidence_vocabulary import (
    EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)

DRAW_02_PACKAGE_ID = "DRAW-02-DRAWING-STANDARD-REGISTRY-ROWS"
DRAW_02_BOUNDARY_DOC = "docs/verification/draw_02_drawing_standard_registry_rows.md"
DRAW_02_DEFAULT_OUTPUT = "output/validation_runs/draw-02-drawing-standard-registry-no-cad"

DRAWING_STANDARD_SUITE_PATH = "examples/plans/drawing_standard_beta_suite.json"
DRAWING_STANDARD_SUITE_ID = "drawing-standard-beta-04"
DRAWING_STANDARD_SUITE_CAPABILITY_ID = "drawing_standard.beta.drawing_standard_beta_04"


def capability_id_for_drawing_standard_beta_case(case_id: str) -> str:
    return f"drawing_standard.beta.{_slug(case_id)}"


def expected_drawing_standard_beta_case_ids(*, project_root: Path) -> list[str]:
    suite = load_drawing_standard_beta_suite(default_suite_path(project_root))
    return [str(case["case_id"]) for case in suite["cases"]]


def build_drawing_standard_registry_row(
    *,
    case_id: str | None,
    suite_id: str = DRAWING_STANDARD_SUITE_ID,
    profile_id: str = DEFAULT_DRAWING_STANDARD_PROFILE_ID,
    output_root: str = DRAW_02_DEFAULT_OUTPUT,
) -> dict[str, Any]:
    """Build one registry row template for the suite parent or a beta case."""

    if case_id is None:
        capability_id = DRAWING_STANDARD_SUITE_CAPABILITY_ID
        display_name = f"Drawing standard beta suite ({profile_id})"
        source_key = suite_id
        report_rel = f"{output_root}/drawing_standard_beta_summary.json"
    else:
        capability_id = capability_id_for_drawing_standard_beta_case(case_id)
        display_name = f"Drawing standard beta / {case_id}"
        source_key = case_id
        report_rel = f"{output_root}/{case_id}/case_result.json"

    return {
        "capability_id": capability_id,
        "display_name": display_name,
        "category": "other",
        "claim_level": "smoke",
        "ladder_level": "L0",
        "domain": "generic",
        "tags": ["drawing_standard", "V-PROOF-44", "DRAW-02"],
        "notes": [
            "DRAW-02 registry row bound to drawing_standard_beta_suite case.",
            "dry_run_valid_plan_only does not imply geometry_verified; RCAD-23 for real CAD.",
        ],
        "source_refs": [
            {
                "source_kind": "benchmark",
                "source_path": DRAWING_STANDARD_SUITE_PATH,
                "source_key": source_key,
            }
        ],
        "cad_case": {
            "case_kind": "script",
            "requires_real_cad": False,
            "entrypoint": "scripts/run_drawing_standard_beta_suite.py",
            "output_path": report_rel,
            "safety": dict(PREVIEW_SAFETY),
        },
    }


def build_drawing_standard_registry_rows(
    *,
    project_root: Path,
    output_root: str = DRAW_02_DEFAULT_OUTPUT,
) -> list[dict[str, Any]]:
    rows = [build_drawing_standard_registry_row(case_id=None, output_root=output_root)]
    for case_id in expected_drawing_standard_beta_case_ids(project_root=project_root):
        rows.append(build_drawing_standard_registry_row(case_id=case_id, output_root=output_root))
    return rows


def assert_drawing_standard_registry_contract(*, project_root: Path) -> None:
    """Raise when DRAW-02 registry rows or suite bindings are missing or inconsistent."""

    root = project_root.resolve()
    registry_path = root / "examples/capability_proof/cad_capability_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    index = index_capability_rows(registry)

    expected_case_ids = expected_drawing_standard_beta_case_ids(project_root=root)
    if len(expected_case_ids) != 6:
        raise AssertionError(f"expected 6 beta cases, got {len(expected_case_ids)}")

    suite_row = index.get(DRAWING_STANDARD_SUITE_CAPABILITY_ID)
    if suite_row is None:
        raise AssertionError(f"missing registry row: {DRAWING_STANDARD_SUITE_CAPABILITY_ID}")

    for case_id in expected_case_ids:
        capability_id = capability_id_for_drawing_standard_beta_case(case_id)
        row = index.get(capability_id)
        if row is None:
            raise AssertionError(f"missing registry row for beta case: {capability_id}")
        source_refs = row.get("source_refs", [])
        if not any(ref.get("source_key") == case_id for ref in source_refs if isinstance(ref, dict)):
            raise AssertionError(f"{capability_id} source_key must include {case_id!r}")
        cad_case = row.get("cad_case", {})
        output_path = str(cad_case.get("output_path", ""))
        if case_id not in output_path:
            raise AssertionError(f"{capability_id} cad_case.output_path must reference case_id")

    schema_errors = validate_capability_registry(registry)
    if schema_errors:
        raise AssertionError(f"registry validation failed: {schema_errors[:3]}")

    boundary = root / DRAW_02_BOUNDARY_DOC
    if not boundary.is_file():
        raise AssertionError(f"missing DRAW-02 boundary doc: {DRAW_02_BOUNDARY_DOC}")

    if not get_schema_path("drawing_standard_profile").is_file():
        raise AssertionError("missing drawing_standard_profile schema")


@dataclass
class SmokeEvidenceWritebackRequest:
    capability_id: str
    report_path: str
    evidence_state: str = EVIDENCE_DRY_RUN_VALID_PLAN_ONLY
    note: str | None = None


@dataclass
class SmokeEvidenceWritebackResult:
    capability_id: str
    status: str
    message: str
    report_path: str | None = None


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_pass_report(path: Path, *, project_root: Path) -> tuple[dict[str, Any] | None, str]:
    resolved = (project_root / path).resolve() if not path.is_absolute() else path.resolve()
    if not resolved.is_file():
        return None, f"report not found: {path}"
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, str(exc)
    if not isinstance(payload, dict):
        return None, "report must be a JSON object"
    if str(payload.get("status", "")) != "pass":
        return None, f"report status must be pass, got {payload.get('status')!r}"
    return payload, ""


def apply_smoke_registry_evidence_writeback(
    registry: dict[str, Any],
    request: SmokeEvidenceWritebackRequest,
    *,
    project_root: Path,
    row_index: dict[str, dict[str, Any]] | None = None,
    dry_run: bool = True,
) -> SmokeEvidenceWritebackResult:
    """Update smoke-row evidence from a non-CAD pass report (DRAW-02 / V-PROOF-44)."""

    index = row_index or index_capability_rows(registry)
    row = index.get(request.capability_id)
    if row is None:
        return SmokeEvidenceWritebackResult(
            capability_id=request.capability_id,
            status="not_found",
            message=f"Unknown capability_id: {request.capability_id}",
        )
    if str(row.get("claim_level", "")) != "smoke":
        return SmokeEvidenceWritebackResult(
            capability_id=request.capability_id,
            status="rejected",
            message="Smoke evidence writeback only supports claim_level=smoke.",
        )

    report_path = Path(request.report_path)
    payload, error = _load_pass_report(report_path, project_root=project_root)
    if payload is None:
        return SmokeEvidenceWritebackResult(
            capability_id=request.capability_id,
            status="rejected",
            message=error,
            report_path=request.report_path,
        )

    triplet = {
        "evidence_state": request.evidence_state,
        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
    }
    triplet_error = validate_evidence_triplet(triplet)
    if triplet_error:
        return SmokeEvidenceWritebackResult(
            capability_id=request.capability_id,
            status="rejected",
            message=triplet_error,
            report_path=request.report_path,
        )

    rel_report = str(report_path).replace("\\", "/")
    if not dry_run:
        row["evidence"] = {
            **triplet,
            "report_path": rel_report,
            "last_verified_at": _utc_now_iso(),
        }
        notes = row.get("notes")
        if not isinstance(notes, list):
            notes = []
        note = request.note or f"DRAW-02 smoke writeback from {rel_report}"
        if note not in notes:
            notes.append(note)
        row["notes"] = notes

    return SmokeEvidenceWritebackResult(
        capability_id=request.capability_id,
        status="applied",
        message="dry-run: would update smoke evidence." if dry_run else "smoke evidence updated.",
        report_path=rel_report,
    )


def build_smoke_writeback_requests_from_suite_output(
    suite_result: dict[str, Any],
    *,
    output_root: Path,
    project_root: Path,
) -> list[SmokeEvidenceWritebackRequest]:
    requests: list[SmokeEvidenceWritebackRequest] = []
    summary_rel = str(output_root.relative_to(project_root)).replace("\\", "/")
    requests.append(
        SmokeEvidenceWritebackRequest(
            capability_id=DRAWING_STANDARD_SUITE_CAPABILITY_ID,
            report_path=f"{summary_rel}/drawing_standard_beta_summary.json",
        )
    )
    for case in suite_result.get("cases", []):
        if not isinstance(case, dict):
            continue
        case_id = str(case.get("case_id", ""))
        if not case_id:
            continue
        requests.append(
            SmokeEvidenceWritebackRequest(
                capability_id=capability_id_for_drawing_standard_beta_case(case_id),
                report_path=f"{summary_rel}/{case_id}/case_result.json",
            )
        )
    return requests


def sync_drawing_standard_registry_from_suite(
    registry: dict[str, Any],
    suite_result: dict[str, Any],
    *,
    output_root: Path,
    project_root: Path,
    dry_run: bool = False,
) -> list[SmokeEvidenceWritebackResult]:
    """Apply smoke evidence writeback for suite parent + each beta case."""

    if str(suite_result.get("status", "")) != "pass":
        raise ValueError("suite_result.status must be pass before registry sync")

    index = index_capability_rows(registry)
    requests = build_smoke_writeback_requests_from_suite_output(
        suite_result,
        output_root=output_root,
        project_root=project_root,
    )
    return [
        apply_smoke_registry_evidence_writeback(
            registry,
            request,
            project_root=project_root,
            row_index=index,
            dry_run=dry_run,
        )
        for request in requests
    ]


def run_drawing_standard_registry_no_cad_sync(
    *,
    project_root: Path,
    output_dir: Path,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Run beta suite, sync smoke evidence into registry rows, return summary."""

    suite_path = default_suite_path(project_root)
    suite_result = run_drawing_standard_beta_suite(suite_path, output_root=output_dir)
    registry_path = project_root / "examples/capability_proof/cad_capability_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    writeback_results = sync_drawing_standard_registry_from_suite(
        registry,
        suite_result,
        output_root=output_dir,
        project_root=project_root,
        dry_run=dry_run,
    )
    if not dry_run:
        registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    applied = sum(1 for item in writeback_results if item.status == "applied")
    rejected = sum(1 for item in writeback_results if item.status == "rejected")
    return {
        "package_id": DRAW_02_PACKAGE_ID,
        "suite_status": suite_result.get("status"),
        "writeback_applied_count": applied,
        "writeback_rejected_count": rejected,
        "writeback_results": [item.__dict__ for item in writeback_results],
        "output_root": str(output_dir).replace("\\", "/"),
    }
