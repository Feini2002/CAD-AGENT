"""V-PROOF-24: office_alpha object_spec benchmark rows — no-CAD registry smoke only."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.benchmarks.runner import run_benchmark_case, run_benchmark_suite
from core.verification.capability_registry import index_capability_rows, validate_capability_registry
from core.verification.capability_registry_seed_common import PREVIEW_SAFETY
from core.verification.capability_registry_writeback import capability_id_for_benchmark_case
from core.verification.evidence_contract import validate_evidence_triplet
from core.verification.evidence_vocabulary import (
    EVIDENCE_BENCHMARK_PASS_NON_CAD,
    EVIDENCE_BLOCKED_EXPECTED_NON_CAD,
    EVIDENCE_INVALID_CONFIGURATION,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)
from core.verification.negative_plan_registry import merge_negative_plan_registry_rows

VPROOF_24_PACKAGE_ID = "V-PROOF-24-OFFICE-OBJECT-ROWS"
VPROOF_24_BOUNDARY_DOC = "docs/verification/vproof_24_office_object_rows.md"
VPROOF_24_DEFAULT_OUTPUT = "output/validation_runs/vproof-24-office-object-no-cad"
DEFAULT_MANIFEST_REL = "examples/capability_proof/office_alpha_object_manifest.json"
OFFICE_ALPHA_BENCHMARK_PATH = "examples/benchmarks/office_alpha_benchmark.json"
OFFICE_ALPHA_SUITE_ID = "office-alpha-benchmark"
OFFICE_OBJECT_SUITE_CAPABILITY_ID = "benchmark.office_alpha_benchmark.object_spec_suite"


def default_manifest_path(root: Path) -> Path:
    return root / DEFAULT_MANIFEST_REL


def load_office_alpha_object_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("manifest_id") != "office-alpha-object-rows":
        raise ValueError("manifest_id must be 'office-alpha-object-rows'.")
    cases = manifest.get("object_cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("office_alpha_object_manifest requires a non-empty object_cases array.")
    return manifest


def expected_office_object_case_ids(*, manifest: dict[str, Any]) -> list[str]:
    return [str(case_id) for case_id in manifest["object_cases"]]


def capability_id_for_office_object_case(case_id: str) -> str:
    return capability_id_for_benchmark_case(OFFICE_ALPHA_SUITE_ID, case_id)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _evidence_state_for_case_result(case_result: dict[str, Any]) -> str:
    actual = case_result.get("actual", {})
    if not isinstance(actual, dict):
        return EVIDENCE_BENCHMARK_PASS_NON_CAD
    state = str(actual.get("evidence_state", ""))
    if state in {
        EVIDENCE_BENCHMARK_PASS_NON_CAD,
        EVIDENCE_BLOCKED_EXPECTED_NON_CAD,
        EVIDENCE_INVALID_CONFIGURATION,
    }:
        return state
    if case_result.get("status") == "pass":
        return EVIDENCE_BENCHMARK_PASS_NON_CAD
    return EVIDENCE_INVALID_CONFIGURATION


def run_office_object_benchmark_subset(
    *,
    project_root: Path,
    output_dir: Path,
    manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = project_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = manifest or load_office_alpha_object_manifest(default_manifest_path(root))
    suite_path = root / str(manifest.get("benchmark_suite_path", OFFICE_ALPHA_BENCHMARK_PATH))
    suite = json.loads(suite_path.read_text(encoding="utf-8"))
    wanted = set(expected_office_object_case_ids(manifest=manifest))
    cases_by_id = {
        str(case["case_id"]): case
        for case in suite.get("cases", [])
        if isinstance(case, dict) and str(case.get("case_id", "")) in wanted
    }
    missing = sorted(wanted - set(cases_by_id))
    if missing:
        raise ValueError(f"office_alpha benchmark missing object cases: {missing}")

    case_results = [
        run_benchmark_case(cases_by_id[case_id], root=root, output_root=output_dir, suite=suite)
        for case_id in expected_office_object_case_ids(manifest=manifest)
    ]
    failed = [item for item in case_results if item.get("status") != "pass"]
    status = "pass" if not failed else "fail"
    report = {
        "version": "0.1",
        "package_id": VPROOF_24_PACKAGE_ID,
        "status": status,
        "suite_id": OFFICE_ALPHA_SUITE_ID,
        "benchmark_suite_path": str(suite_path.relative_to(root)).replace("\\", "/"),
        "case_count": len(case_results),
        "pass_count": sum(1 for item in case_results if item.get("status") == "pass"),
        "cases": case_results,
    }
    report_path = output_dir / "office_alpha_object_suite.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["report_path"] = str(report_path.relative_to(root)).replace("\\", "/")
    if status != "pass":
        raise ValueError(f"office_alpha_object_suite failed: {[item['case_id'] for item in failed]}")
    return report


def build_office_object_registry_rows(
    *,
    manifest: dict[str, Any],
    output_root: str,
) -> list[dict[str, Any]]:
    suite_rel = str(manifest.get("benchmark_suite_path", OFFICE_ALPHA_BENCHMARK_PATH)).replace("\\", "/")
    report_rel = f"{output_root}/office_alpha_object_suite.json"
    rows: list[dict[str, Any]] = [
        {
            "capability_id": OFFICE_OBJECT_SUITE_CAPABILITY_ID,
            "display_name": "office-alpha-benchmark / object_spec suite",
            "category": "object",
            "claim_level": "smoke",
            "ladder_level": "L0",
            "domain": "office",
            "tags": ["office", "R-OFFICE", "V-PROOF-24", "object_spec"],
            "notes": [
                "V-PROOF-24 parent row for office_alpha object_spec cases.",
                "no-CAD smoke only; real CAD deferred until user opens CAD.",
            ],
            "source_refs": [
                {
                    "source_kind": "benchmark",
                    "source_path": suite_rel,
                    "source_key": "object_spec_suite",
                },
                {
                    "source_kind": "documentation",
                    "source_path": DEFAULT_MANIFEST_REL,
                    "source_key": str(manifest.get("manifest_id", "")),
                },
            ],
            "cad_case": {
                "case_kind": "script",
                "requires_real_cad": False,
                "entrypoint": "scripts/run_vproof_24_office_object_sync.py",
                "output_path": report_rel,
                "safety": dict(PREVIEW_SAFETY),
            },
        }
    ]
    for case_id in expected_office_object_case_ids(manifest=manifest):
        capability_id = capability_id_for_office_object_case(case_id)
        rows.append(
            {
                "capability_id": capability_id,
                "display_name": f"office-alpha-benchmark / {case_id}",
                "category": "object",
                "claim_level": "smoke",
                "ladder_level": "L0",
                "domain": "office",
                "tags": ["office", "R-OFFICE", "V-PROOF-24", "object_spec"],
                "notes": [
                    f"V-PROOF-24 office object_spec row for {case_id}.",
                    "Downgraded from mistaken geometry_verified writeback when present.",
                    "benchmark_pass_non_cad does not imply geometry_verified.",
                ],
                "source_refs": [
                    {
                        "source_kind": "benchmark",
                        "source_path": suite_rel,
                        "source_key": case_id,
                    }
                ],
                "cad_case": {
                    "case_kind": "benchmark_case",
                    "requires_real_cad": False,
                    "benchmark_suite_path": suite_rel,
                    "benchmark_case_id": case_id,
                    "safety": dict(PREVIEW_SAFETY),
                },
            }
        )
    return rows


def merge_office_object_registry_rows(registry: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, int]:
    return merge_negative_plan_registry_rows(registry, rows)


@dataclass
class OfficeObjectWritebackRequest:
    capability_id: str
    report_path: str
    evidence_state: str = EVIDENCE_BENCHMARK_PASS_NON_CAD


@dataclass
class OfficeObjectWritebackResult:
    capability_id: str
    status: str
    message: str
    report_path: str | None = None


def apply_office_object_smoke_writeback(
    registry: dict[str, Any],
    request: OfficeObjectWritebackRequest,
    *,
    project_root: Path,
    row_index: dict[str, dict[str, Any]] | None = None,
    dry_run: bool = True,
) -> OfficeObjectWritebackResult:
    index = row_index or index_capability_rows(registry)
    row = index.get(request.capability_id)
    if row is None:
        return OfficeObjectWritebackResult(
            capability_id=request.capability_id,
            status="not_found",
            message=f"Unknown capability_id: {request.capability_id}",
        )
    if str(row.get("claim_level", "")) != "smoke":
        return OfficeObjectWritebackResult(
            capability_id=request.capability_id,
            status="rejected",
            message="Office object writeback only supports claim_level=smoke.",
        )

    resolved = project_root / request.report_path.replace("\\", "/")
    if not resolved.is_file():
        return OfficeObjectWritebackResult(
            capability_id=request.capability_id,
            status="rejected",
            message=f"report not found: {request.report_path}",
            report_path=request.report_path,
        )
    payload = json.loads(resolved.read_text(encoding="utf-8"))
    if str(payload.get("status", "")) != "pass":
        return OfficeObjectWritebackResult(
            capability_id=request.capability_id,
            status="rejected",
            message=f"report status must be pass, got {payload.get('status')!r}",
            report_path=request.report_path,
        )

    triplet = {
        "evidence_state": request.evidence_state,
        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
    }
    triplet_error = validate_evidence_triplet(triplet)
    if triplet_error:
        return OfficeObjectWritebackResult(
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
        note = f"V-PROOF-24 smoke writeback from {rel_report}"
        if note not in notes:
            notes.append(note)
        row["notes"] = notes

    return OfficeObjectWritebackResult(
        capability_id=request.capability_id,
        status="applied",
        message="dry-run: would update smoke evidence." if dry_run else "smoke evidence updated.",
        report_path=rel_report,
    )


def assert_office_object_registry_contract(*, project_root: Path) -> None:
    root = project_root.resolve()
    manifest = load_office_alpha_object_manifest(default_manifest_path(root))
    registry_path = root / "examples/capability_proof/cad_capability_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    index = index_capability_rows(registry)

    if OFFICE_OBJECT_SUITE_CAPABILITY_ID not in index:
        raise AssertionError(f"missing suite row: {OFFICE_OBJECT_SUITE_CAPABILITY_ID}")

    for case_id in expected_office_object_case_ids(manifest=manifest):
        capability_id = capability_id_for_office_object_case(case_id)
        row = index.get(capability_id)
        if row is None:
            raise AssertionError(f"missing office object row: {capability_id}")
        from core.verification.registry_claim_contract import assert_smoke_or_cad_proof_claim

        assert_smoke_or_cad_proof_claim(row, capability_id, context="V-PROOF-24")
        cad_case = row.get("cad_case", {})
        if str(cad_case.get("benchmark_case_id", "")) != case_id:
            raise AssertionError(f"{capability_id} benchmark_case_id mismatch")

    schema_errors = validate_capability_registry(registry)
    if schema_errors:
        raise AssertionError(f"registry validation failed: {schema_errors[:3]}")

    boundary = root / VPROOF_24_BOUNDARY_DOC
    if not boundary.is_file():
        raise AssertionError(f"missing boundary doc: {VPROOF_24_BOUNDARY_DOC}")


def run_vproof_24_office_object_sync(
    *,
    project_root: Path,
    output_dir: Path,
    manifest_path: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    root = project_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_root = str(output_dir.relative_to(root)).replace("\\", "/")

    manifest = load_office_alpha_object_manifest(manifest_path or default_manifest_path(root))
    subset_report = run_office_object_benchmark_subset(
        project_root=root,
        output_dir=output_dir,
        manifest=manifest,
    )
    report_rel = f"{output_root}/office_alpha_object_suite.json"
    cases_by_id = {
        str(item["case_id"]): item for item in subset_report.get("cases", []) if isinstance(item, dict)
    }

    registry_path = root / "examples/capability_proof/cad_capability_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    rows = build_office_object_registry_rows(manifest=manifest, output_root=output_root)
    merge_stats = merge_office_object_registry_rows(registry, rows)
    index = index_capability_rows(registry)

    writeback_results = [
        apply_office_object_smoke_writeback(
            registry,
            OfficeObjectWritebackRequest(
                capability_id=OFFICE_OBJECT_SUITE_CAPABILITY_ID,
                report_path=report_rel,
            ),
            project_root=root,
            row_index=index,
            dry_run=dry_run,
        )
    ]
    for case_id in expected_office_object_case_ids(manifest=manifest):
        case_result = cases_by_id.get(case_id, {})
        evidence_state = _evidence_state_for_case_result(case_result)
        writeback_results.append(
            apply_office_object_smoke_writeback(
                registry,
                OfficeObjectWritebackRequest(
                    capability_id=capability_id_for_office_object_case(case_id),
                    report_path=report_rel,
                    evidence_state=evidence_state,
                ),
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
        "package_id": VPROOF_24_PACKAGE_ID,
        "subset_status": subset_report["status"],
        "object_case_count": len(expected_office_object_case_ids(manifest=manifest)),
        "registry_row_count": len(rows),
        "merge_added": merge_stats["added"],
        "merge_updated": merge_stats["updated"],
        "writeback_applied_count": applied,
        "writeback_rejected_count": rejected,
        "writeback_results": [item.__dict__ for item in writeback_results],
        "output_root": output_root,
    }


def run_office_alpha_full_benchmark_for_evidence(
    *,
    project_root: Path,
    output_dir: Path,
) -> dict[str, Any]:
    """Optional helper: run full office_alpha suite (18 cases) for evidence artifacts."""
    root = project_root.resolve()
    suite_path = root / OFFICE_ALPHA_BENCHMARK_PATH
    return run_benchmark_suite(suite_path, output_root=output_dir)
