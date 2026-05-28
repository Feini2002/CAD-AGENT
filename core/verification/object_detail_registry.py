"""V-PROOF-23: register object_detail_spec component plans in cad_capability_registry."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.benchmarks.runner import run_benchmark_case
from core.object_engine.parametric_objects import create_object_spec
from core.verification.capability_registry import index_capability_rows, validate_capability_registry
from core.verification.capability_registry_seed_common import PREVIEW_SAFETY, _slug
from core.verification.evidence_contract import validate_evidence_triplet
from core.verification.evidence_vocabulary import (
    EVIDENCE_BENCHMARK_PASS_NON_CAD,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
    SCREENSHOT_VISUAL_AID_ONLY,
)
from core.verification.negative_plan_registry import merge_negative_plan_registry_rows

VPROOF_23_PACKAGE_ID = "V-PROOF-23-OBJECT-DETAIL-ROWS"
VPROOF_23_BOUNDARY_DOC = "docs/verification/vproof_23_object_detail_rows.md"
VPROOF_23_DEFAULT_OUTPUT = "output/validation_runs/vproof-23-object-detail-no-cad"
DEFAULT_MANIFEST_REL = "examples/capability_proof/object_detail_component_manifest.json"
COMPONENT_DETAIL_SUITE_CAPABILITY_ID = "object.component_detail.suite"
DETAIL_PLAN_MODULE = "core/object_engine/detail_plan.py"


def default_manifest_path(root: Path) -> Path:
    return root / DEFAULT_MANIFEST_REL


def load_object_detail_component_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("manifest_id") != "object-detail-component":
        raise ValueError("manifest_id must be 'object-detail-component'.")
    objects = manifest.get("objects")
    if not isinstance(objects, list) or not objects:
        raise ValueError("object_detail_component_manifest requires a non-empty objects array.")
    return manifest


def capability_id_for_component_detail(object_type: str) -> str:
    return f"object.{_slug(object_type)}.component_detail"


def expected_object_types(*, manifest: dict[str, Any]) -> list[str]:
    return [str(item["object_type"]) for item in manifest["objects"] if isinstance(item, dict)]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _benchmark_case_for_object(object_type: str, *, manifest: dict[str, Any]) -> dict[str, Any]:
    entry = next(
        (item for item in manifest["objects"] if isinstance(item, dict) and item.get("object_type") == object_type),
        None,
    )
    if entry is None:
        raise ValueError(f"unknown object_type in manifest: {object_type}")
    required_roles = [str(role) for role in entry.get("required_component_roles", [])]
    min_count = int(entry.get("min_detail_plan_count", 1))
    spec = create_object_spec(object_type)
    expected: dict[str, Any] = {
        "pipeline_status": "ok",
        "dry_run_status": "valid",
        "verification_status": "unverified",
        "evidence_state": EVIDENCE_BENCHMARK_PASS_NON_CAD,
        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": SCREENSHOT_VISUAL_AID_ONLY,
        "object_type": object_type,
        "detail_plan_count": min_count,
    }
    if required_roles:
        expected["contains_component_roles"] = required_roles
    return {
        "case_id": f"object_detail_{object_type}",
        "pipeline": "object_detail_spec",
        "object_type": object_type,
        "width": spec["size"]["width"],
        "depth": spec["size"]["depth"],
        "height": spec["size"]["height"],
        "expected": expected,
    }


def run_object_detail_component_suite(
    *,
    project_root: Path,
    output_dir: Path,
    manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = project_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = manifest or load_object_detail_component_manifest(default_manifest_path(root))

    case_results: list[dict[str, Any]] = []
    for object_type in expected_object_types(manifest=manifest):
        case = _benchmark_case_for_object(object_type, manifest=manifest)
        result = run_benchmark_case(case, root=root, output_root=output_dir)
        case_results.append(result)

    failed = [item for item in case_results if item.get("status") != "pass"]
    status = "pass" if not failed else "fail"
    report = {
        "version": "0.1",
        "package_id": VPROOF_23_PACKAGE_ID,
        "status": status,
        "suite_id": "object-detail-component",
        "case_count": len(case_results),
        "pass_count": sum(1 for item in case_results if item.get("status") == "pass"),
        "cases": case_results,
    }
    report_path = output_dir / "object_detail_component_suite.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["report_path"] = str(report_path.relative_to(root)).replace("\\", "/")
    if status != "pass":
        raise ValueError(f"object_detail_component_suite failed: {[item['case_id'] for item in failed]}")
    return report


def build_object_detail_registry_rows(
    *,
    manifest: dict[str, Any],
    output_root: str,
) -> list[dict[str, Any]]:
    manifest_rel = DEFAULT_MANIFEST_REL
    report_rel = f"{output_root}/object_detail_component_suite.json"
    rows: list[dict[str, Any]] = [
        {
            "capability_id": COMPONENT_DETAIL_SUITE_CAPABILITY_ID,
            "display_name": "Object component detail plan suite",
            "category": "object",
            "claim_level": "smoke",
            "ladder_level": "L0",
            "domain": "generic",
            "tags": ["object", "OBJ-DETAIL", "V-PROOF-23"],
            "notes": [
                "V-PROOF-23 parent row: object_detail_spec component CAD_PLAN expansion.",
                "benchmark_pass_non_cad does not imply geometry_verified.",
            ],
            "source_refs": [
                {
                    "source_kind": "documentation",
                    "source_path": manifest_rel,
                    "source_key": str(manifest.get("manifest_id", "")),
                }
            ],
            "cad_case": {
                "case_kind": "script",
                "requires_real_cad": False,
                "entrypoint": "scripts/run_vproof_23_object_detail_sync.py",
                "output_path": report_rel,
                "safety": dict(PREVIEW_SAFETY),
            },
        }
    ]
    for entry in manifest["objects"]:
        if not isinstance(entry, dict):
            continue
        object_type = str(entry["object_type"])
        capability_id = str(entry.get("registry_capability_id") or capability_id_for_component_detail(object_type))
        roles = ", ".join(str(role) for role in entry.get("required_component_roles", []))
        rows.append(
            {
                "capability_id": capability_id,
                "display_name": f"Component detail plan / {object_type}",
                "category": "object",
                "claim_level": "smoke",
                "ladder_level": "L0",
                "domain": "generic",
                "intent": "draw_object",
                "object_type": object_type,
                "tags": ["object", "OBJ-DETAIL", "V-PROOF-23", "component_plan"],
                "notes": [
                    f"V-PROOF-23 component_detail row for {object_type}.",
                    f"required_roles={roles}",
                    "dry-run valid only; not CAD geometry proof.",
                ],
                "source_refs": [
                    {
                        "source_kind": "documentation",
                        "source_path": DETAIL_PLAN_MODULE,
                        "source_key": object_type,
                    },
                    {
                        "source_kind": "documentation",
                        "source_path": manifest_rel,
                        "source_key": object_type,
                    },
                ],
                "cad_case": {
                    "case_kind": "script",
                    "requires_real_cad": False,
                    "entrypoint": "scripts/run_vproof_23_object_detail_sync.py",
                    "output_path": report_rel,
                    "safety": dict(PREVIEW_SAFETY),
                },
            }
        )
    return rows


def merge_object_detail_registry_rows(registry: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, int]:
    return merge_negative_plan_registry_rows(registry, rows)


@dataclass
class ObjectDetailWritebackRequest:
    capability_id: str
    report_path: str


@dataclass
class ObjectDetailWritebackResult:
    capability_id: str
    status: str
    message: str
    report_path: str | None = None


def apply_object_detail_smoke_writeback(
    registry: dict[str, Any],
    request: ObjectDetailWritebackRequest,
    *,
    project_root: Path,
    row_index: dict[str, dict[str, Any]] | None = None,
    dry_run: bool = True,
) -> ObjectDetailWritebackResult:
    index = row_index or index_capability_rows(registry)
    row = index.get(request.capability_id)
    if row is None:
        return ObjectDetailWritebackResult(
            capability_id=request.capability_id,
            status="not_found",
            message=f"Unknown capability_id: {request.capability_id}",
        )
    if str(row.get("claim_level", "")) != "smoke":
        return ObjectDetailWritebackResult(
            capability_id=request.capability_id,
            status="rejected",
            message="Object detail writeback only supports claim_level=smoke.",
        )

    resolved = project_root / request.report_path.replace("\\", "/")
    if not resolved.is_file():
        return ObjectDetailWritebackResult(
            capability_id=request.capability_id,
            status="rejected",
            message=f"report not found: {request.report_path}",
            report_path=request.report_path,
        )
    payload = json.loads(resolved.read_text(encoding="utf-8"))
    if str(payload.get("status", "")) != "pass":
        return ObjectDetailWritebackResult(
            capability_id=request.capability_id,
            status="rejected",
            message=f"report status must be pass, got {payload.get('status')!r}",
            report_path=request.report_path,
        )

    triplet = {
        "evidence_state": EVIDENCE_BENCHMARK_PASS_NON_CAD,
        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
    }
    triplet_error = validate_evidence_triplet(triplet)
    if triplet_error:
        return ObjectDetailWritebackResult(
            capability_id=request.capability_id,
            status="rejected",
            message=triplet_error,
            report_path=request.report_path,
        )

    rel_report = request.report_path.replace("\\", "/")
    if not dry_run:
        row["evidence"] = {**triplet, "report_path": rel_report, "last_verified_at": _utc_now_iso()}
        notes = row.get("notes")
        if not isinstance(notes, list):
            notes = []
        note = f"V-PROOF-23 smoke writeback from {rel_report}"
        if note not in notes:
            notes.append(note)
        row["notes"] = notes

    return ObjectDetailWritebackResult(
        capability_id=request.capability_id,
        status="applied",
        message="dry-run: would update smoke evidence." if dry_run else "smoke evidence updated.",
        report_path=rel_report,
    )


def assert_object_detail_registry_contract(*, project_root: Path) -> None:
    root = project_root.resolve()
    manifest = load_object_detail_component_manifest(default_manifest_path(root))
    registry_path = root / "examples/capability_proof/cad_capability_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    index = index_capability_rows(registry)

    if COMPONENT_DETAIL_SUITE_CAPABILITY_ID not in index:
        raise AssertionError(f"missing suite row: {COMPONENT_DETAIL_SUITE_CAPABILITY_ID}")

    for object_type in expected_object_types(manifest=manifest):
        capability_id = capability_id_for_component_detail(object_type)
        row = index.get(capability_id)
        if row is None:
            raise AssertionError(f"missing component_detail row: {capability_id}")
        from core.verification.registry_claim_contract import assert_smoke_or_cad_proof_claim

        assert_smoke_or_cad_proof_claim(row, capability_id, context="V-PROOF-23")

    schema_errors = validate_capability_registry(registry)
    if schema_errors:
        raise AssertionError(f"registry validation failed: {schema_errors[:3]}")

    boundary = root / VPROOF_23_BOUNDARY_DOC
    if not boundary.is_file():
        raise AssertionError(f"missing boundary doc: {VPROOF_23_BOUNDARY_DOC}")


def run_vproof_23_object_detail_sync(
    *,
    project_root: Path,
    output_dir: Path,
    manifest_path: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    root = project_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_root = str(output_dir.relative_to(root)).replace("\\", "/")

    manifest = load_object_detail_component_manifest(
        manifest_path or default_manifest_path(root),
    )
    suite_report = run_object_detail_component_suite(
        project_root=root,
        output_dir=output_dir,
        manifest=manifest,
    )
    report_rel = f"{output_root}/object_detail_component_suite.json"

    registry_path = root / "examples/capability_proof/cad_capability_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    rows = build_object_detail_registry_rows(manifest=manifest, output_root=output_root)
    merge_stats = merge_object_detail_registry_rows(registry, rows)
    index = index_capability_rows(registry)

    writeback_results = [
        apply_object_detail_smoke_writeback(
            registry,
            ObjectDetailWritebackRequest(capability_id=COMPONENT_DETAIL_SUITE_CAPABILITY_ID, report_path=report_rel),
            project_root=root,
            row_index=index,
            dry_run=dry_run,
        )
    ]
    for entry in manifest["objects"]:
        if not isinstance(entry, dict):
            continue
        object_type = str(entry["object_type"])
        capability_id = str(entry.get("registry_capability_id") or capability_id_for_component_detail(object_type))
        writeback_results.append(
            apply_object_detail_smoke_writeback(
                registry,
                ObjectDetailWritebackRequest(capability_id=capability_id, report_path=report_rel),
                project_root=root,
                row_index=index,
                dry_run=dry_run,
            )
        )

    if not dry_run:
        registry["updated_at"] = datetime.now(timezone.utc).date().isoformat()
        registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    applied = sum(1 for item in writeback_results if item.status == "applied")
    rejected = sum(1 for item in writeback_results if item.status == "rejected")
    return {
        "package_id": VPROOF_23_PACKAGE_ID,
        "suite_status": suite_report["status"],
        "object_type_count": len(expected_object_types(manifest=manifest)),
        "registry_row_count": len(rows),
        "merge_added": merge_stats["added"],
        "merge_updated": merge_stats["updated"],
        "writeback_applied_count": applied,
        "writeback_rejected_count": rejected,
        "writeback_results": [item.__dict__ for item in writeback_results],
        "output_root": output_root,
    }
