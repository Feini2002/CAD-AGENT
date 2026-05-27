"""RBLOCK-07: block insert matrix manifest → cad_capability_registry bindings."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.block_engine.block_matrix_manifest import (
    BLOCK_MATRIX_DIMENSIONS,
    RBLOCK_04_REGISTRY_CAPABILITY_IDS,
    default_manifest_path,
    load_block_insert_matrix_manifest,
    run_block_insert_matrix_manifest,
)
from core.drawing_standard.drawing_standard_registry import (
    SmokeEvidenceWritebackRequest,
    apply_smoke_registry_evidence_writeback,
)
from core.schemas.registry import get_schema_path
from core.verification.capability_registry import index_capability_rows, validate_capability_registry
from core.verification.capability_registry_seed_common import PREVIEW_SAFETY
from core.verification.evidence_vocabulary import EVIDENCE_DRY_RUN_VALID_PLAN_ONLY

RBLOCK_07_PACKAGE_ID = "RBLOCK-07-BLOCK-MATRIX-REGISTRY-ROWS"
RBLOCK_07_BOUNDARY_DOC = "docs/verification/rblock_07_block_matrix_registry_rows.md"
RBLOCK_07_DEFAULT_OUTPUT = "output/validation_runs/rblock-07-block-matrix-registry-no-cad"
MATRIX_MANIFEST_PATH = "examples/capability_proof/block_insert_matrix_manifest.json"
MATRIX_SUITE_CAPABILITY_ID = "block.insert_block_alpha.matrix"
MATRIX_MANIFEST_SOURCE_KEY = "block-insert-matrix-01"

DIMENSION_TO_CAPABILITY_ID = dict(zip(BLOCK_MATRIX_DIMENSIONS, RBLOCK_04_REGISTRY_CAPABILITY_IDS))


def capability_id_for_matrix_dimension(dimension: str) -> str:
    if dimension not in DIMENSION_TO_CAPABILITY_ID:
        raise ValueError(f"unknown matrix dimension: {dimension!r}")
    return DIMENSION_TO_CAPABILITY_ID[dimension]


def build_block_matrix_suite_registry_row(
    *,
    output_root: str = RBLOCK_07_DEFAULT_OUTPUT,
) -> dict[str, Any]:
    return {
        "capability_id": MATRIX_SUITE_CAPABILITY_ID,
        "display_name": "Block insert matrix suite (no-CAD)",
        "category": "block",
        "claim_level": "smoke",
        "ladder_level": "L0",
        "domain": "generic",
        "intent": "insert_block_alpha",
        "tags": ["block_matrix", "V-PROOF-40", "RBLOCK-07"],
        "notes": [
            "RBLOCK-07 parent smoke row for block-insert-matrix-01.",
            "dry_run_valid_plan_only does not imply geometry_verified.",
        ],
        "source_refs": [
            {
                "source_kind": "benchmark",
                "source_path": MATRIX_MANIFEST_PATH,
                "source_key": MATRIX_MANIFEST_SOURCE_KEY,
            }
        ],
        "cad_case": {
            "case_kind": "script",
            "requires_real_cad": False,
            "entrypoint": "scripts/run_block_insert_matrix_manifest.py",
            "output_path": f"{output_root}/block_insert_matrix_summary.json",
            "safety": dict(PREVIEW_SAFETY),
        },
    }


@dataclass
class MatrixRegistryBindingRequest:
    capability_id: str
    dimension: str
    report_path: str
    note: str | None = None


@dataclass
class MatrixRegistryBindingResult:
    capability_id: str
    status: str
    message: str
    report_path: str | None = None


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _manifest_source_key(dimension: str) -> str:
    if dimension == "suite":
        return MATRIX_MANIFEST_SOURCE_KEY
    return dimension


def _manifest_source_ref(dimension: str) -> dict[str, str]:
    return {
        "source_kind": "benchmark",
        "source_path": MATRIX_MANIFEST_PATH,
        "source_key": _manifest_source_key(dimension),
    }


def _has_manifest_source_ref(row: dict[str, Any], dimension: str) -> bool:
    source_key = _manifest_source_key(dimension)
    for ref in row.get("source_refs", []):
        if not isinstance(ref, dict):
            continue
        if ref.get("source_path") == MATRIX_MANIFEST_PATH and ref.get("source_key") == source_key:
            return True
    return False


def apply_block_matrix_registry_binding(
    registry: dict[str, Any],
    request: MatrixRegistryBindingRequest,
    *,
    project_root: Path,
    row_index: dict[str, dict[str, Any]] | None = None,
    dry_run: bool = True,
) -> MatrixRegistryBindingResult:
    """Bind matrix dimension smoke report to registry row without upgrading verified evidence."""

    index = row_index or index_capability_rows(registry)
    row = index.get(request.capability_id)
    if row is None:
        return MatrixRegistryBindingResult(
            capability_id=request.capability_id,
            status="not_found",
            message=f"Unknown capability_id: {request.capability_id}",
        )

    claim_level = str(row.get("claim_level", ""))
    if claim_level == "smoke":
        smoke_result = apply_smoke_registry_evidence_writeback(
            registry,
            SmokeEvidenceWritebackRequest(
                capability_id=request.capability_id,
                report_path=request.report_path,
                evidence_state=EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
                note=request.note,
            ),
            project_root=project_root,
            row_index=index,
            dry_run=dry_run,
        )
        return MatrixRegistryBindingResult(
            capability_id=request.capability_id,
            status=smoke_result.status,
            message=smoke_result.message,
            report_path=smoke_result.report_path,
        )

    if claim_level not in {"verified", "showcase", "deferred"}:
        return MatrixRegistryBindingResult(
            capability_id=request.capability_id,
            status="rejected",
            message=f"Matrix binding does not support claim_level={claim_level!r}.",
        )

    rel_report = str(request.report_path).replace("\\", "/")
    binding_note = request.note or (
        f"RBLOCK-07 matrix smoke binding ({request.dimension}): {rel_report}"
    )

    if not dry_run:
        if not _has_manifest_source_ref(row, request.dimension):
            refs = row.get("source_refs")
            if not isinstance(refs, list):
                refs = []
            refs.append(_manifest_source_ref(request.dimension))
            row["source_refs"] = refs

        notes = row.get("notes")
        if not isinstance(notes, list):
            notes = []
        if binding_note not in notes:
            notes.append(binding_note)
        row["notes"] = notes

        cad_case = row.get("cad_case")
        if isinstance(cad_case, dict) and not cad_case.get("output_path"):
            cad_case["output_path"] = rel_report

    return MatrixRegistryBindingResult(
        capability_id=request.capability_id,
        status="applied",
        message="dry-run: would bind matrix smoke path." if dry_run else "matrix smoke path bound.",
        report_path=rel_report,
    )


def build_matrix_registry_binding_requests(
    matrix_result: dict[str, Any],
    *,
    output_root: Path,
    project_root: Path,
) -> list[MatrixRegistryBindingRequest]:
    summary_rel = str(output_root.relative_to(project_root)).replace("\\", "/")
    requests: list[MatrixRegistryBindingRequest] = [
        MatrixRegistryBindingRequest(
            capability_id=MATRIX_SUITE_CAPABILITY_ID,
            dimension="suite",
            report_path=f"{summary_rel}/block_insert_matrix_summary.json",
        )
    ]
    for dimension in BLOCK_MATRIX_DIMENSIONS:
        requests.append(
            MatrixRegistryBindingRequest(
                capability_id=capability_id_for_matrix_dimension(dimension),
                dimension=dimension,
                report_path=f"{summary_rel}/dimension_{dimension}.json",
            )
        )
    return requests


def sync_block_matrix_registry_from_manifest(
    registry: dict[str, Any],
    matrix_result: dict[str, Any],
    *,
    output_root: Path,
    project_root: Path,
    dry_run: bool = False,
) -> list[MatrixRegistryBindingResult]:
    if str(matrix_result.get("status", "")) != "pass":
        raise ValueError("matrix_result.status must be pass before registry sync")

    index = index_capability_rows(registry)
    requests = build_matrix_registry_binding_requests(
        matrix_result,
        output_root=output_root,
        project_root=project_root,
    )
    return [
        apply_block_matrix_registry_binding(
            registry,
            request,
            project_root=project_root,
            row_index=index,
            dry_run=dry_run,
        )
        for request in requests
    ]


def assert_block_matrix_registry_contract(*, project_root: Path) -> None:
    """Raise when RBLOCK-07 matrix registry bindings are missing or inconsistent."""

    root = project_root.resolve()
    from core.block_engine.block_attribute_boundary import assert_block_attribute_boundary_contract

    assert_block_attribute_boundary_contract(project_root=root)

    if not (root / RBLOCK_07_BOUNDARY_DOC).is_file():
        raise AssertionError(f"missing RBLOCK-07 boundary doc: {RBLOCK_07_BOUNDARY_DOC}")

    registry_path = root / "examples/capability_proof/cad_capability_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    index = index_capability_rows(registry)

    if MATRIX_SUITE_CAPABILITY_ID not in index:
        raise AssertionError(f"missing registry row: {MATRIX_SUITE_CAPABILITY_ID}")

    for dimension in BLOCK_MATRIX_DIMENSIONS:
        cap_id = capability_id_for_matrix_dimension(dimension)
        row = index.get(cap_id)
        if row is None:
            raise AssertionError(f"missing registry row: {cap_id}")
        if not _has_manifest_source_ref(row, dimension):
            raise AssertionError(f"{cap_id} missing manifest source_ref for dimension {dimension!r}")

    schema_errors = validate_capability_registry(registry)
    if schema_errors:
        raise AssertionError(f"registry validation failed: {schema_errors[:3]}")

    if not get_schema_path("cad_capability_registry").is_file():
        raise AssertionError("missing cad_capability_registry schema")

    manifest_path = default_manifest_path(root)
    smoke = run_block_insert_matrix_manifest(manifest_path, output_root=None)
    if smoke.get("status") != "pass":
        raise AssertionError(f"block matrix manifest must pass: {smoke.get('summary')}")


def run_block_matrix_registry_no_cad_sync(
    *,
    project_root: Path,
    output_dir: Path,
    dry_run: bool = False,
) -> dict[str, Any]:
    root = project_root.resolve()
    output = output_dir if output_dir.is_absolute() else root / output_dir
    output = output.resolve()
    manifest_path = default_manifest_path(project_root)
    matrix_result = run_block_insert_matrix_manifest(manifest_path, output_root=output)
    registry_path = root / "examples/capability_proof/cad_capability_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    writeback_results = sync_block_matrix_registry_from_manifest(
        registry,
        matrix_result,
        output_root=output,
        project_root=root,
        dry_run=dry_run,
    )
    if not dry_run:
        registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    applied = sum(1 for item in writeback_results if item.status == "applied")
    rejected = sum(1 for item in writeback_results if item.status == "rejected")
    return {
        "package_id": RBLOCK_07_PACKAGE_ID,
        "matrix_status": matrix_result.get("status"),
        "binding_applied_count": applied,
        "binding_rejected_count": rejected,
        "binding_results": [item.__dict__ for item in writeback_results],
        "output_root": str(output.relative_to(root)).replace("\\", "/"),
    }


def block_matrix_registry_status_summary(*, project_root: Path) -> dict[str, Any]:
    manifest = load_block_insert_matrix_manifest(default_manifest_path(project_root))
    return {
        "package_id": RBLOCK_07_PACKAGE_ID,
        "manifest_id": manifest.get("manifest_id"),
        "matrix_suite_capability_id": MATRIX_SUITE_CAPABILITY_ID,
        "dimension_binding_count": len(BLOCK_MATRIX_DIMENSIONS),
    }
