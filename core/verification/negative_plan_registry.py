"""V-PROOF-50: register negative CAD_PLAN failure categories in cad_capability_registry."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.verification.capability_registry import index_capability_rows, validate_capability_registry
from core.verification.capability_registry_seed_common import PREVIEW_SAFETY, _slug
from core.verification.evidence_contract import validate_evidence_triplet
from core.verification.evidence_vocabulary import (
    EVIDENCE_INVALID_CONFIGURATION,
    EVIDENCE_NEGATIVE_GUARD_VERIFIED,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)
from core.verification.negative_cad_plans import (
    DEFAULT_NEGATIVE_MANIFEST,
    load_negative_plan_manifest,
    run_negative_cad_plan_suite,
)
from core.verification.negative_cad_runner import run_negative_cad_runner

VPROOF_50_PACKAGE_ID = "V-PROOF-50-NEGATIVE-REGISTRY"
VPROOF_50_BOUNDARY_DOC = "docs/verification/vproof_50_negative_registry.md"
VPROOF_50_DEFAULT_OUTPUT = "output/validation_runs/vproof-50-negative-registry-no-cad"
NEGATIVE_MANIFEST_PATH = "examples/plans/negative/negative_plan_manifest.json"
NEGATIVE_SUITE_CAPABILITY_ID = "negative.cad_plan.suite"
VPROOF_51_PACKAGE_ID = "V-PROOF-51-NEGATIVE-CAD"
VPROOF_51_BOUNDARY_DOC = "docs/verification/vproof_51_negative_cad.md"
VPROOF_51_DEFAULT_OUTPUT = "output/validation_runs/vproof-51-negative-cad"
RCAD_20_CANONICAL_REPORT = (
    "output/validation_runs/rcad-20-negative-cad-20260527-escalated/negative_cad_runner_report.json"
)
NEGATIVE_REAL_CAD_CAPABILITY_ID = "negative.cad_plan.real_cad_guard"


def capability_id_for_negative_failure_category(failure_category: str) -> str:
    return f"negative.cad_plan.{_slug(failure_category)}"


def expected_negative_failure_categories(*, project_root: Path) -> list[str]:
    manifest = load_negative_plan_manifest(project_root / DEFAULT_NEGATIVE_MANIFEST)
    categories: list[str] = []
    for fixture in manifest["fixtures"]:
        category = str(fixture.get("failure_category") or fixture["id"])
        if category not in categories:
            categories.append(category)
    return categories


def build_negative_plan_registry_row(
    *,
    failure_category: str | None,
    output_root: str = VPROOF_50_DEFAULT_OUTPUT,
) -> dict[str, Any]:
    if failure_category is None:
        capability_id = NEGATIVE_SUITE_CAPABILITY_ID
        display_name = "Negative CAD_PLAN guard suite"
        source_key = "cad_plan_negative"
        report_rel = f"{output_root}/negative_cad_runner_report.json"
        notes = [
            "V-PROOF-50 parent row for LCAD-10 negative CAD runner.",
            "negative_guard_verified is guard-only; does not imply geometry_verified.",
        ]
    else:
        capability_id = capability_id_for_negative_failure_category(failure_category)
        display_name = f"Negative CAD_PLAN / {failure_category}"
        source_key = failure_category
        report_rel = f"{output_root}/negative_cad_plan_suite.json"
        notes = [
            "V-PROOF-50 registry row: validator must reject this failure_category.",
            "invalid_configuration does not count as CAD geometry proof.",
        ]

    return {
        "capability_id": capability_id,
        "display_name": display_name,
        "category": "other",
        "claim_level": "smoke",
        "ladder_level": "L0",
        "domain": "generic",
        "tags": ["negative", "LCAD-10", "V-PROOF-50"],
        "notes": notes,
        "source_refs": [
            {
                "source_kind": "cad_plan",
                "source_path": NEGATIVE_MANIFEST_PATH,
                "source_key": source_key,
            }
        ],
        "cad_case": {
            "case_kind": "script",
            "requires_real_cad": False,
            "entrypoint": "scripts/run_negative_cad_plan_suite.py",
            "output_path": report_rel,
            "safety": dict(PREVIEW_SAFETY),
        },
    }


def build_negative_plan_registry_rows(
    *,
    project_root: Path,
    output_root: str = VPROOF_50_DEFAULT_OUTPUT,
) -> list[dict[str, Any]]:
    rows = [build_negative_plan_registry_row(failure_category=None, output_root=output_root)]
    for category in expected_negative_failure_categories(project_root=project_root):
        rows.append(build_negative_plan_registry_row(failure_category=category, output_root=output_root))
    return rows


def merge_negative_plan_registry_rows(registry: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, int]:
    index = index_capability_rows(registry)
    added = 0
    updated = 0
    for row in rows:
        capability_id = str(row["capability_id"])
        if capability_id in index:
            existing = index[capability_id]
            existing.clear()
            existing.update(row)
            updated += 1
        else:
            registry.setdefault("capabilities", []).append(row)
            index[capability_id] = row
            added += 1
    return {"added": added, "updated": updated}


def assert_negative_plan_registry_contract(*, project_root: Path) -> None:
    root = project_root.resolve()
    registry_path = root / "examples/capability_proof/cad_capability_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    index = index_capability_rows(registry)

    categories = expected_negative_failure_categories(project_root=root)
    if len(categories) < 8:
        raise AssertionError(f"expected at least 8 failure categories, got {len(categories)}")

    suite_row = index.get(NEGATIVE_SUITE_CAPABILITY_ID)
    if suite_row is None:
        raise AssertionError(f"missing registry row: {NEGATIVE_SUITE_CAPABILITY_ID}")

    for category in categories:
        capability_id = capability_id_for_negative_failure_category(category)
        row = index.get(capability_id)
        if row is None:
            raise AssertionError(f"missing registry row for failure_category: {category}")
        if str(row.get("claim_level", "")) != "smoke":
            raise AssertionError(f"{capability_id} must remain claim_level=smoke")
        refs = row.get("source_refs", [])
        if not any(ref.get("source_key") == category for ref in refs if isinstance(ref, dict)):
            raise AssertionError(f"{capability_id} source_key must include {category!r}")

    schema_errors = validate_capability_registry(registry)
    if schema_errors:
        raise AssertionError(f"registry validation failed: {schema_errors[:3]}")

    boundary = root / VPROOF_50_BOUNDARY_DOC
    if not boundary.is_file():
        raise AssertionError(f"missing V-PROOF-50 boundary doc: {VPROOF_50_BOUNDARY_DOC}")


@dataclass
class NegativeRegistryWritebackRequest:
    capability_id: str
    report_path: str
    evidence_state: str


@dataclass
class NegativeRegistryWritebackResult:
    capability_id: str
    status: str
    message: str
    report_path: str | None = None


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def apply_negative_registry_smoke_writeback(
    registry: dict[str, Any],
    request: NegativeRegistryWritebackRequest,
    *,
    project_root: Path,
    row_index: dict[str, dict[str, Any]] | None = None,
    dry_run: bool = True,
) -> NegativeRegistryWritebackResult:
    index = row_index or index_capability_rows(registry)
    row = index.get(request.capability_id)
    if row is None:
        return NegativeRegistryWritebackResult(
            capability_id=request.capability_id,
            status="not_found",
            message=f"Unknown capability_id: {request.capability_id}",
        )
    if str(row.get("claim_level", "")) != "smoke":
        return NegativeRegistryWritebackResult(
            capability_id=request.capability_id,
            status="rejected",
            message="Negative registry writeback only supports claim_level=smoke.",
        )

    report_path = Path(request.report_path)
    resolved = (project_root / report_path).resolve() if not report_path.is_absolute() else report_path.resolve()
    if not resolved.is_file():
        return NegativeRegistryWritebackResult(
            capability_id=request.capability_id,
            status="rejected",
            message=f"report not found: {request.report_path}",
            report_path=request.report_path,
        )
    payload = json.loads(resolved.read_text(encoding="utf-8"))
    if str(payload.get("status", "")) != "pass":
        return NegativeRegistryWritebackResult(
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
        return NegativeRegistryWritebackResult(
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
        note = f"V-PROOF-50 smoke writeback from {rel_report}"
        if note not in notes:
            notes.append(note)
        row["notes"] = notes

    return NegativeRegistryWritebackResult(
        capability_id=request.capability_id,
        status="applied",
        message="dry-run: would update smoke evidence." if dry_run else "smoke evidence updated.",
        report_path=rel_report,
    )


def run_vproof_50_negative_registry_sync(
    *,
    project_root: Path,
    output_dir: Path,
    dry_run: bool = False,
) -> dict[str, Any]:
    root = project_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_root = str(output_dir.relative_to(root)).replace("\\", "/")

    plan_report = run_negative_cad_plan_suite(root=root)
    plan_report_path = output_dir / "negative_cad_plan_suite.json"
    plan_report_path.write_text(json.dumps(plan_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if plan_report["status"] != "pass":
        raise ValueError("negative_cad_plan_suite must pass before registry sync")

    runner_report = run_negative_cad_runner(root=root, output_dir=output_dir, use_real_cad=False)
    if runner_report.get("status") != "pass":
        raise ValueError("negative_cad_runner fake mode must pass before registry sync")

    registry_path = root / "examples/capability_proof/cad_capability_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    rows = build_negative_plan_registry_rows(project_root=root, output_root=output_root)
    merge_stats = merge_negative_plan_registry_rows(registry, rows)

    plan_rel = f"{output_root}/negative_cad_plan_suite.json"
    runner_rel = f"{output_root}/negative_cad_runner_report.json"
    index = index_capability_rows(registry)
    writeback_results: list[NegativeRegistryWritebackResult] = [
        apply_negative_registry_smoke_writeback(
            registry,
            NegativeRegistryWritebackRequest(
                capability_id=NEGATIVE_SUITE_CAPABILITY_ID,
                report_path=runner_rel,
                evidence_state=EVIDENCE_NEGATIVE_GUARD_VERIFIED,
            ),
            project_root=root,
            row_index=index,
            dry_run=dry_run,
        )
    ]
    for category in expected_negative_failure_categories(project_root=root):
        writeback_results.append(
            apply_negative_registry_smoke_writeback(
                registry,
                NegativeRegistryWritebackRequest(
                    capability_id=capability_id_for_negative_failure_category(category),
                    report_path=plan_rel,
                    evidence_state=EVIDENCE_INVALID_CONFIGURATION,
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
        "package_id": VPROOF_50_PACKAGE_ID,
        "plan_suite_status": plan_report["status"],
        "runner_status": runner_report.get("status"),
        "failure_category_count": len(expected_negative_failure_categories(project_root=root)),
        "registry_row_count": len(rows),
        "merge_added": merge_stats["added"],
        "merge_updated": merge_stats["updated"],
        "writeback_applied_count": applied,
        "writeback_rejected_count": rejected,
        "writeback_results": [item.__dict__ for item in writeback_results],
        "output_root": output_root,
    }


def build_negative_real_cad_registry_row(
    *,
    output_root: str = VPROOF_51_DEFAULT_OUTPUT,
    report_rel: str = RCAD_20_CANONICAL_REPORT,
) -> dict[str, Any]:
    return {
        "capability_id": NEGATIVE_REAL_CAD_CAPABILITY_ID,
        "display_name": "Negative CAD_PLAN real CAD guard (no handles)",
        "category": "other",
        "claim_level": "smoke",
        "ladder_level": "L0",
        "domain": "generic",
        "tags": ["negative", "LCAD-10", "V-PROOF-51", "RCAD-20"],
        "notes": [
            "V-PROOF-51 binds RCAD-20 real AutoCAD negative_guard_verified evidence.",
            "claim_level remains smoke; negative_guard_verified is not geometry_verified.",
        ],
        "source_refs": [
            {
                "source_kind": "rcad",
                "source_path": "scripts/run_negative_cad_runner.py",
                "source_key": "RCAD-20",
            }
        ],
        "cad_case": {
            "case_kind": "script",
            "requires_real_cad": True,
            "entrypoint": "scripts/run_negative_cad_runner.py",
            "output_path": report_rel,
            "safety": dict(PREVIEW_SAFETY),
        },
    }


def validate_negative_real_cad_report(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if str(report.get("status", "")) != "pass":
        errors.append(f"status must be pass, got {report.get('status')!r}")
    if str(report.get("mode", "")) != "real_cad":
        errors.append(f"mode must be real_cad, got {report.get('mode')!r}")
    if str(report.get("evidence_state", "")) != EVIDENCE_NEGATIVE_GUARD_VERIFIED:
        errors.append(
            f"evidence_state must be {EVIDENCE_NEGATIVE_GUARD_VERIFIED!r}, got {report.get('evidence_state')!r}"
        )
    handles = report.get("created_handles")
    if handles != []:
        errors.append(f"created_handles must be [], got {handles!r}")
    safety = report.get("safety")
    if not isinstance(safety, dict):
        errors.append("safety object required")
    else:
        for key, expected in (
            ("saved_dwg", False),
            ("deleted_entities", False),
            ("modified_formal_layers", False),
        ):
            if safety.get(key) is not expected:
                errors.append(f"safety.{key} must be {expected}")
    session_guard = report.get("session_guard")
    if isinstance(session_guard, dict):
        comparison = session_guard.get("comparison")
        if isinstance(comparison, dict):
            for key in ("preview_layer_entity_delta", "modelspace_entity_delta"):
                if int(comparison.get(key, -1)) != 0:
                    errors.append(f"session_guard.comparison.{key} must be 0")
    return errors


def resolve_negative_real_cad_report_path(
    *,
    project_root: Path,
    report_path: Path | None,
    output_dir: Path,
    run_real_cad: bool,
) -> tuple[Path, dict[str, Any], str]:
    root = project_root.resolve()
    if report_path is not None:
        resolved = report_path if report_path.is_absolute() else root / report_path
        if not resolved.is_file():
            raise FileNotFoundError(f"negative CAD report not found: {resolved}")
        payload = json.loads(resolved.read_text(encoding="utf-8"))
        return resolved, payload, str(resolved.relative_to(root)).replace("\\", "/")

    canonical = root / RCAD_20_CANONICAL_REPORT
    if canonical.is_file():
        payload = json.loads(canonical.read_text(encoding="utf-8"))
        return canonical, payload, RCAD_20_CANONICAL_REPORT

    if run_real_cad:
        report = run_negative_cad_runner(root=root, output_dir=output_dir, use_real_cad=True)
        if report.get("status") == "external_blocker":
            raise RuntimeError(str(report.get("connection", {}).get("message", "AutoCAD unavailable")))
        out = output_dir / "negative_cad_runner_report.json"
        if not out.is_file():
            raise FileNotFoundError("negative_cad_runner did not write report.json")
        rel = str(out.relative_to(root)).replace("\\", "/")
        return out, report, rel

    raise FileNotFoundError(
        "Real CAD negative report missing. Provide --report, restore RCAD-20 evidence, or pass --real-cad."
    )


def apply_negative_real_cad_guard_writeback(
    registry: dict[str, Any],
    *,
    report_rel: str,
    report: dict[str, Any],
    project_root: Path,
    row_index: dict[str, dict[str, Any]] | None = None,
    dry_run: bool = True,
) -> NegativeRegistryWritebackResult:
    index = row_index or index_capability_rows(registry)
    row = index.get(NEGATIVE_REAL_CAD_CAPABILITY_ID)
    if row is None:
        return NegativeRegistryWritebackResult(
            capability_id=NEGATIVE_REAL_CAD_CAPABILITY_ID,
            status="not_found",
            message="Missing negative.cad_plan.real_cad_guard registry row.",
        )

    validation_errors = validate_negative_real_cad_report(report)
    if validation_errors:
        return NegativeRegistryWritebackResult(
            capability_id=NEGATIVE_REAL_CAD_CAPABILITY_ID,
            status="rejected",
            message="; ".join(validation_errors[:5]),
            report_path=report_rel,
        )

    triplet = {
        "evidence_state": EVIDENCE_NEGATIVE_GUARD_VERIFIED,
        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
    }
    triplet_error = validate_evidence_triplet(triplet)
    if triplet_error:
        return NegativeRegistryWritebackResult(
            capability_id=NEGATIVE_REAL_CAD_CAPABILITY_ID,
            status="rejected",
            message=triplet_error,
            report_path=report_rel,
        )

    if not dry_run:
        row["evidence"] = {**triplet, "report_path": report_rel, "last_verified_at": _utc_now_iso()}
        cad_case = row.get("cad_case")
        if isinstance(cad_case, dict):
            cad_case["requires_real_cad"] = True
            cad_case["output_path"] = report_rel
        notes = row.get("notes")
        if not isinstance(notes, list):
            notes = []
        note = f"V-PROOF-51 real CAD guard writeback from {report_rel}"
        if note not in notes:
            notes.append(note)
        row["notes"] = notes

    return NegativeRegistryWritebackResult(
        capability_id=NEGATIVE_REAL_CAD_CAPABILITY_ID,
        status="applied",
        message="dry-run: would bind real CAD negative guard." if dry_run else "real CAD guard evidence bound.",
        report_path=report_rel,
    )


def assert_vproof_51_negative_cad_contract(*, project_root: Path) -> None:
    root = project_root.resolve()
    registry_path = root / "examples/capability_proof/cad_capability_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    index = index_capability_rows(registry)
    row = index.get(NEGATIVE_REAL_CAD_CAPABILITY_ID)
    if row is None:
        raise AssertionError(f"missing registry row: {NEGATIVE_REAL_CAD_CAPABILITY_ID}")
    if str(row.get("claim_level", "")) != "smoke":
        raise AssertionError("real_cad_guard row must stay claim_level=smoke")
    evidence = row.get("evidence", {})
    report_rel = str(evidence.get("report_path", ""))
    if not report_rel:
        raise AssertionError("real_cad_guard row missing evidence.report_path")
    report_path = root / report_rel
    if not report_path.is_file():
        raise AssertionError(f"real CAD negative report not found: {report_rel}")
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    errors = validate_negative_real_cad_report(payload)
    if errors:
        raise AssertionError(f"invalid real CAD negative report: {errors[:3]}")
    boundary = root / VPROOF_51_BOUNDARY_DOC
    if not boundary.is_file():
        raise AssertionError(f"missing V-PROOF-51 boundary doc: {VPROOF_51_BOUNDARY_DOC}")
    schema_errors = validate_capability_registry(registry)
    if schema_errors:
        raise AssertionError(f"registry validation failed: {schema_errors[:3]}")


def run_vproof_51_negative_cad_sync(
    *,
    project_root: Path,
    output_dir: Path,
    report_path: Path | None = None,
    run_real_cad: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    root = project_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    resolved, report, report_rel = resolve_negative_real_cad_report_path(
        project_root=root,
        report_path=report_path,
        output_dir=output_dir,
        run_real_cad=run_real_cad,
    )
    validation_errors = validate_negative_real_cad_report(report)
    if validation_errors:
        raise ValueError(f"negative real CAD report invalid: {validation_errors}")

    summary_path = output_dir / "vproof_51_negative_cad_summary.json"
    if resolved.parent.resolve() != output_dir.resolve():
        (output_dir / "negative_cad_runner_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    registry_path = root / "examples/capability_proof/cad_capability_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    merge_negative_plan_registry_rows(registry, [build_negative_real_cad_registry_row(report_rel=report_rel)])
    index = index_capability_rows(registry)
    writeback = apply_negative_real_cad_guard_writeback(
        registry,
        report_rel=report_rel,
        report=report,
        project_root=root,
        row_index=index,
        dry_run=dry_run,
    )

    if not dry_run:
        registry["updated_at"] = datetime.now(timezone.utc).date().isoformat()
        registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = {
        "package_id": VPROOF_51_PACKAGE_ID,
        "report_path": report_rel,
        "report_mode": report.get("mode"),
        "created_handles": report.get("created_handles"),
        "writeback_status": writeback.status,
        "writeback_message": writeback.message,
        "validation_error_count": len(validation_errors),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary["output_root"] = str(output_dir.relative_to(root)).replace("\\", "/")
    return summary
