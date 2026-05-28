"""V-PROOF-70: submittable de-identified project regression manifest."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.project_samples.project_sample_cad_rollup import (
    DEFAULT_MANIFEST_REL as CAD_ROLLUP_MANIFEST_REL,
    load_project_sample_cad_manifest,
)
from core.project_samples.protocol import scan_projects_root
from core.schemas.validator import validate_value
from core.verification.capability_registry import index_capability_rows, validate_capability_registry
from core.verification.capability_registry_seed_common import PREVIEW_SAFETY, _slug
from core.verification.evidence_contract import validate_evidence_triplet
from core.verification.evidence_vocabulary import (
    EVIDENCE_BENCHMARK_PASS_NON_CAD,
    EVIDENCE_BLOCKED_EXPECTED_NON_CAD,
    EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)

VPROOF_70_PACKAGE_ID = "V-PROOF-70-PROJECT-MANIFEST"
VPROOF_70_BOUNDARY_DOC = "docs/verification/vproof_70_project_manifest.md"
VPROOF_70_DEFAULT_OUTPUT = "output/validation_runs/vproof-70-project-manifest"
DEFAULT_MANIFEST_REL = Path("examples/capability_proof/project_regression_manifest.json")
SCHEMA_REL = Path("core/schemas/project_regression_manifest.schema.json")
REGRESSION_MANIFEST_CAPABILITY_ID = "project.regression.manifest"


def capability_id_for_project_regression_sample(sample_id: str) -> str:
    return f"project.regression.sample.{_slug(sample_id)}"


def load_project_regression_manifest(
    path: Path | None = None,
    *,
    project_root: Path,
) -> dict[str, Any]:
    manifest_path = path or (project_root / DEFAULT_MANIFEST_REL)
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def validate_project_regression_manifest(
    manifest: dict[str, Any],
    *,
    project_root: Path,
) -> list[str]:
    schema = json.loads((project_root / SCHEMA_REL).read_text(encoding="utf-8"))
    return validate_value(manifest, schema)


def submittable_samples(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in manifest.get("samples", []) if isinstance(row, dict) and row.get("submittable") is True]


def assert_project_regression_manifest_consistency(
    manifest: dict[str, Any],
    *,
    project_root: Path,
) -> None:
    root = project_root.resolve()
    submittable = submittable_samples(manifest)
    minimum = int(manifest.get("minimum_sample_count", 2))
    if len(submittable) < minimum:
        raise AssertionError(f"expected at least {minimum} submittable samples, got {len(submittable)}")

    rollup_ids: set[str] = set()
    rollup_path = root / str(manifest.get("cad_regression_rollup_path", CAD_ROLLUP_MANIFEST_REL))
    if rollup_path.is_file():
        rollup = load_project_sample_cad_manifest(rollup_path, project_root=root)
        rollup_ids = {str(item["sample_id"]) for item in rollup.get("samples", []) if isinstance(item, dict)}

    for row in manifest.get("samples", []):
        if not isinstance(row, dict):
            continue
        sample_id = str(row["sample_id"])
        sample_root = root / str(row["sample_root"])
        manifest_path = root / str(row["manifest_path"])
        if sample_root.name != sample_id:
            raise AssertionError(f"sample_root directory name must match sample_id: {sample_id}")
        if not manifest_path.is_file():
            raise AssertionError(f"missing sample.manifest.json for {sample_id}")
        if row.get("submittable") and row.get("in_cad_regression_rollup") and sample_id not in rollup_ids:
            raise AssertionError(f"submittable sample {sample_id} missing from cad regression rollup manifest")

    scan = scan_projects_root(root / str(manifest.get("projects_root", "projects")))
    scan_by_id = {str(item["sample_id"]): item for item in scan.get("samples", []) if isinstance(item, dict)}
    for row in submittable:
        sample_id = str(row["sample_id"])
        scanned = scan_by_id.get(sample_id)
        if scanned is None:
            raise AssertionError(f"protocol scan missing sample: {sample_id}")
        if scanned.get("status") != "pass":
            raise AssertionError(f"protocol scan failed for submittable sample: {sample_id}")


def run_project_regression_manifest_audit(
    *,
    project_root: Path,
    manifest_path: Path | None = None,
    output_dir: Path,
) -> dict[str, Any]:
    root = project_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = load_project_regression_manifest(manifest_path, project_root=root)
    errors = validate_project_regression_manifest(manifest, project_root=root)
    if errors:
        return {
            "package_id": VPROOF_70_PACKAGE_ID,
            "status": "invalid",
            "errors": errors,
            "samples": [],
        }

    scan = scan_projects_root(root / str(manifest.get("projects_root", "projects")))
    assert_project_regression_manifest_consistency(manifest, project_root=root)

    submittable = submittable_samples(manifest)
    report = {
        "version": "0.1",
        "package_id": VPROOF_70_PACKAGE_ID,
        "status": "pass",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "manifest_path": str((manifest_path or (root / DEFAULT_MANIFEST_REL)).relative_to(root)).replace("\\", "/"),
        "submittable_sample_count": len(submittable),
        "total_sample_count": len(manifest.get("samples", [])),
        "protocol_scan_status": scan.get("status"),
        "protocol_scan_sample_count": scan.get("sample_count"),
        "samples": [
            {
                "sample_id": str(row["sample_id"]),
                "submittable": bool(row.get("submittable")),
                "protocol_status": next(
                    (
                        item.get("status")
                        for item in scan.get("samples", [])
                        if isinstance(item, dict) and item.get("sample_id") == row.get("sample_id")
                    ),
                    "missing",
                ),
            }
            for row in manifest.get("samples", [])
            if isinstance(row, dict)
        ],
    }
    (output_dir / "project_regression_manifest_audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def merge_project_regression_registry_rows(registry: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, int]:
    from core.verification.negative_plan_registry import merge_negative_plan_registry_rows

    return merge_negative_plan_registry_rows(registry, rows)


def build_project_regression_registry_rows(
    *,
    project_root: Path,
    manifest: dict[str, Any],
    output_root: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [
        {
            "capability_id": REGRESSION_MANIFEST_CAPABILITY_ID,
            "display_name": "Project regression manifest (de-identified samples)",
            "category": "project_sample",
            "claim_level": "smoke",
            "ladder_level": "L0",
            "domain": "generic",
            "tags": ["project", "V-PROOF-70", "PROJ-02"],
            "notes": [
                "V-PROOF-70 submittable project regression manifest.",
                "Protocol scan pass does not imply geometry_verified.",
            ],
            "source_refs": [
                {
                    "source_kind": "documentation",
                    "source_path": str(DEFAULT_MANIFEST_REL).replace("\\", "/"),
                    "source_key": str(manifest.get("manifest_id", "")),
                }
            ],
            "cad_case": {
                "case_kind": "script",
                "requires_real_cad": False,
                "entrypoint": "scripts/run_vproof_70_project_manifest_sync.py",
                "output_path": f"{output_root}/project_regression_manifest_audit.json",
                "safety": dict(PREVIEW_SAFETY),
            },
        }
    ]
    for row in manifest.get("samples", []):
        if not isinstance(row, dict):
            continue
        sample_id = str(row["sample_id"])
        evidence_claim = str(row.get("evidence_claim", ""))
        rows.append(
            {
                "capability_id": capability_id_for_project_regression_sample(sample_id),
                "display_name": str(row.get("display_name") or sample_id),
                "category": "project_sample",
                "claim_level": "smoke",
                "ladder_level": "L0",
                "domain": str(row.get("domain", "generic")),
                "tags": ["project", "V-PROOF-70", "PROJ-02"],
                "notes": [
                    f"submittable={bool(row.get('submittable'))}",
                    "in_cad_regression_rollup="
                    f"{bool(row.get('in_cad_regression_rollup'))}",
                ],
                "source_refs": [
                    {
                        "source_kind": "documentation",
                        "source_path": str(row["manifest_path"]),
                        "source_key": sample_id,
                    }
                ],
                "cad_case": {
                    "case_kind": "script",
                    "requires_real_cad": False,
                    "entrypoint": "scripts/run_project_sample_protocol_scan.py",
                    "output_path": f"{output_root}/project_regression_manifest_audit.json",
                    "safety": dict(PREVIEW_SAFETY),
                },
            }
        )
    return rows


def _evidence_state_for_sample(row: dict[str, Any], *, protocol_status: str) -> str:
    if not row.get("submittable"):
        return EVIDENCE_BLOCKED_EXPECTED_NON_CAD
    if protocol_status != "pass":
        return EVIDENCE_DRY_RUN_VALID_PLAN_ONLY
    return EVIDENCE_BENCHMARK_PASS_NON_CAD


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def apply_project_regression_smoke_writeback(
    registry: dict[str, Any],
    *,
    capability_id: str,
    report_path: str,
    evidence_state: str,
    project_root: Path,
    row_index: dict[str, dict[str, Any]] | None = None,
    dry_run: bool = True,
) -> tuple[str, str]:
    index = row_index or index_capability_rows(registry)
    row = index.get(capability_id)
    if row is None:
        return ("not_found", f"Unknown capability_id: {capability_id}")
    if str(row.get("claim_level", "")) != "smoke":
        return ("rejected", "Project regression writeback only supports claim_level=smoke.")

    resolved = (project_root / report_path).resolve()
    if not resolved.is_file():
        return ("rejected", f"report not found: {report_path}")
    payload = json.loads(resolved.read_text(encoding="utf-8"))
    if str(payload.get("status", "")) != "pass":
        return ("rejected", f"report status must be pass, got {payload.get('status')!r}")

    triplet = {
        "evidence_state": evidence_state,
        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
    }
    triplet_error = validate_evidence_triplet(triplet)
    if triplet_error:
        return ("rejected", triplet_error)

    rel_report = str(report_path).replace("\\", "/")
    if not dry_run:
        row["evidence"] = {**triplet, "report_path": rel_report, "last_verified_at": _utc_now_iso()}
    return ("applied", "dry-run" if dry_run else "smoke evidence updated")


def run_vproof_70_project_manifest_sync(
    *,
    project_root: Path,
    output_dir: Path,
    manifest_path: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    root = project_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_root = str(output_dir.relative_to(root)).replace("\\", "/")

    audit = run_project_regression_manifest_audit(
        project_root=root,
        manifest_path=manifest_path,
        output_dir=output_dir,
    )
    if audit.get("status") != "pass":
        raise ValueError(f"project regression manifest audit failed: {audit.get('errors', audit)}")

    manifest = load_project_regression_manifest(manifest_path, project_root=root)
    registry_path = root / "examples/capability_proof/cad_capability_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    rows = build_project_regression_registry_rows(
        project_root=root,
        manifest=manifest,
        output_root=output_root,
    )
    merge_project_regression_registry_rows(registry, rows)
    index = index_capability_rows(registry)

    audit_rel = f"{output_root}/project_regression_manifest_audit.json"
    writeback_applied = 0
    writeback_rejected = 0

    manifest_status, _ = apply_project_regression_smoke_writeback(
        registry,
        capability_id=REGRESSION_MANIFEST_CAPABILITY_ID,
        report_path=audit_rel,
        evidence_state=EVIDENCE_BENCHMARK_PASS_NON_CAD,
        project_root=root,
        row_index=index,
        dry_run=dry_run,
    )
    if manifest_status == "applied":
        writeback_applied += 1
    else:
        writeback_rejected += 1

    scan_by_id = {str(item["sample_id"]): str(item.get("protocol_status", "")) for item in audit.get("samples", [])}
    for row in manifest.get("samples", []):
        if not isinstance(row, dict):
            continue
        capability_id = capability_id_for_project_regression_sample(str(row["sample_id"]))
        evidence_state = _evidence_state_for_sample(
            row,
            protocol_status=scan_by_id.get(str(row["sample_id"]), "fail"),
        )
        status, _ = apply_project_regression_smoke_writeback(
            registry,
            capability_id=capability_id,
            report_path=audit_rel,
            evidence_state=evidence_state,
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
        "package_id": VPROOF_70_PACKAGE_ID,
        "audit_status": audit.get("status"),
        "submittable_sample_count": audit.get("submittable_sample_count"),
        "registry_row_count": len(rows),
        "submittable_count": len(submittable_samples(manifest)),
        "writeback_applied_count": writeback_applied,
        "writeback_rejected_count": writeback_rejected,
        "output_root": output_root,
    }


def assert_vproof_70_project_manifest_contract(*, project_root: Path) -> None:
    root = project_root.resolve()
    manifest = load_project_regression_manifest(project_root=root)
    assert_project_regression_manifest_consistency(manifest, project_root=root)
    registry = json.loads((root / "examples/capability_proof/cad_capability_registry.json").read_text(encoding="utf-8"))
    index = index_capability_rows(registry)
    if REGRESSION_MANIFEST_CAPABILITY_ID not in index:
        raise AssertionError(f"missing registry row: {REGRESSION_MANIFEST_CAPABILITY_ID}")
    for row in submittable_samples(manifest):
        capability_id = capability_id_for_project_regression_sample(str(row["sample_id"]))
        if capability_id not in index:
            raise AssertionError(f"missing registry row: {capability_id}")
    boundary = root / VPROOF_70_BOUNDARY_DOC
    if not boundary.is_file():
        raise AssertionError(f"missing boundary doc: {VPROOF_70_BOUNDARY_DOC}")
    schema_errors = validate_capability_registry(registry)
    if schema_errors:
        raise AssertionError(f"registry validation failed: {schema_errors[:3]}")
