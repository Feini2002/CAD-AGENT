"""V-PROOF-52: register LCAD-14 guard full CAD strict chain in cad_capability_registry."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.verification.capability_registry import index_capability_rows, validate_capability_registry
from core.verification.capability_registry_seed_common import PREVIEW_SAFETY
from core.verification.evidence_contract import validate_evidence_triplet
from core.verification.evidence_vocabulary import (
    EVIDENCE_CAD_CAPABILITY_VERIFIED,
    EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
    EVIDENCE_NEGATIVE_GUARD_VERIFIED,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)
from core.verification.guard_full_cad_runner import run_guard_full_cad_runner

VPROOF_52_PACKAGE_ID = "V-PROOF-52-GUARD-CAD"
VPROOF_52_BOUNDARY_DOC = "docs/verification/vproof_52_guard_cad.md"
VPROOF_52_DEFAULT_OUTPUT = "output/validation_runs/vproof-52-guard-cad-no-cad"
RCAD_21_CANONICAL_REPORT = (
    "output/validation_runs/rcad-21-guard-full-20260527/guard_full_cad_report.json"
)
GUARD_FULL_STRICT_CAPABILITY_ID = "guard.cad.full_chain.strict"
GUARD_WRITE_GUARD_CAPABILITY_ID = "guard.cad.write_guard"
GUARD_NEGATIVE_CAD_CAPABILITY_ID = "guard.cad.negative_cad"
GUARD_CAPABILITY_PROBE_CAPABILITY_ID = "guard.cad.capability_probe"


def _subreport_rel(output_root: str, key: str) -> str:
    paths = {
        "write_guard": f"{output_root}/subreports/write_guard/write_guard_cad_runner_report.json",
        "negative_cad": f"{output_root}/subreports/negative_cad/negative_cad_runner_report.json",
        "capability_probe": f"{output_root}/subreports/capability_probe/cad_capability_probe.json",
    }
    return paths[key]


def build_guard_cad_registry_rows(
    *,
    output_root: str = VPROOF_52_DEFAULT_OUTPUT,
    report_rel: str = RCAD_21_CANONICAL_REPORT,
) -> list[dict[str, Any]]:
    return [
        {
            "capability_id": GUARD_FULL_STRICT_CAPABILITY_ID,
            "display_name": "Guard full CAD strict chain rollup",
            "category": "other",
            "claim_level": "smoke",
            "ladder_level": "L0",
            "domain": "generic",
            "tags": ["guard", "LCAD-14", "V-PROOF-52", "RCAD-21"],
            "notes": [
                "V-PROOF-52 parent row: strict_gate on write_guard + negative_cad + capability_probe.",
                "strict pass is guard/snapshot audit only; not arbitrary CAD_PLAN geometry_verified.",
            ],
            "source_refs": [
                {
                    "source_kind": "rcad",
                    "source_path": "scripts/run_guard_full_cad_runner.py",
                    "source_key": "RCAD-21",
                }
            ],
            "cad_case": {
                "case_kind": "script",
                "requires_real_cad": True,
                "entrypoint": "scripts/run_guard_full_cad_runner.py",
                "output_path": report_rel,
                "safety": dict(PREVIEW_SAFETY),
            },
        },
        {
            "capability_id": GUARD_WRITE_GUARD_CAPABILITY_ID,
            "display_name": "Guard chain / write guard subreport",
            "category": "other",
            "claim_level": "smoke",
            "ladder_level": "L0",
            "domain": "generic",
            "tags": ["guard", "LCAD-14", "V-PROOF-52"],
            "notes": ["V-PROOF-52 sub-row: preview write guard + negative plan validation."],
            "source_refs": [
                {
                    "source_kind": "rcad",
                    "source_path": "scripts/run_write_guard_cad_runner.py",
                    "source_key": "write_guard",
                }
            ],
            "cad_case": {
                "case_kind": "script",
                "requires_real_cad": False,
                "entrypoint": "scripts/run_guard_full_cad_runner.py",
                "output_path": _subreport_rel(output_root, "write_guard"),
                "safety": dict(PREVIEW_SAFETY),
            },
        },
        {
            "capability_id": GUARD_NEGATIVE_CAD_CAPABILITY_ID,
            "display_name": "Guard chain / negative CAD subreport",
            "category": "other",
            "claim_level": "smoke",
            "ladder_level": "L0",
            "domain": "generic",
            "tags": ["guard", "LCAD-14", "V-PROOF-52"],
            "notes": ["V-PROOF-52 sub-row: negative_guard_verified in strict chain."],
            "source_refs": [
                {
                    "source_kind": "rcad",
                    "source_path": "scripts/run_negative_cad_runner.py",
                    "source_key": "negative_cad",
                }
            ],
            "cad_case": {
                "case_kind": "script",
                "requires_real_cad": True,
                "entrypoint": "scripts/run_guard_full_cad_runner.py",
                "output_path": _subreport_rel(output_root, "negative_cad"),
                "safety": dict(PREVIEW_SAFETY),
            },
        },
        {
            "capability_id": GUARD_CAPABILITY_PROBE_CAPABILITY_ID,
            "display_name": "Guard chain / capability probe subreport",
            "category": "other",
            "claim_level": "smoke",
            "ladder_level": "L0",
            "domain": "generic",
            "tags": ["guard", "LCAD-14", "V-PROOF-52"],
            "notes": [
                "V-PROOF-52 sub-row: cad_capability_verified + session_guard in strict chain.",
            ],
            "source_refs": [
                {
                    "source_kind": "rcad",
                    "source_path": "scripts/run_cad_capability_probe.py",
                    "source_key": "capability_probe",
                }
            ],
            "cad_case": {
                "case_kind": "script",
                "requires_real_cad": True,
                "entrypoint": "scripts/run_guard_full_cad_runner.py",
                "output_path": _subreport_rel(output_root, "capability_probe"),
                "safety": dict(PREVIEW_SAFETY),
            },
        },
    ]


def merge_guard_cad_registry_rows(registry: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, int]:
    from core.verification.negative_plan_registry import merge_negative_plan_registry_rows

    return merge_negative_plan_registry_rows(registry, rows)


def validate_guard_full_strict_report(report: dict[str, Any], *, require_real_cad: bool) -> list[str]:
    errors: list[str] = []
    if str(report.get("status", "")) != "pass":
        errors.append(f"status must be pass, got {report.get('status')!r}")
    if require_real_cad and str(report.get("mode", "")) != "real_cad":
        errors.append(f"mode must be real_cad, got {report.get('mode')!r}")
    if report.get("strict") is not True:
        errors.append("strict must be true")
    strict_gate = report.get("strict_gate")
    if not isinstance(strict_gate, dict):
        errors.append("strict_gate object required")
    elif strict_gate.get("status") != "pass":
        errors.append(f"strict_gate.status must be pass, got {strict_gate.get('status')!r}")
    subreports = report.get("subreports")
    if isinstance(subreports, dict):
        write_guard = subreports.get("write_guard", {})
        if isinstance(write_guard, dict) and write_guard.get("status") != "pass":
            errors.append("subreports.write_guard.status must be pass")
        neg = subreports.get("negative_cad", {})
        if isinstance(neg, dict):
            if neg.get("status") != "pass":
                errors.append("subreports.negative_cad.status must be pass")
            elif neg.get("evidence_state") != EVIDENCE_NEGATIVE_GUARD_VERIFIED:
                errors.append("subreports.negative_cad.evidence_state must be negative_guard_verified")
        probe = subreports.get("capability_probe", {})
        if isinstance(probe, dict):
            if probe.get("status") != "cad_capability_verified":
                errors.append("subreports.capability_probe.status must be cad_capability_verified")
            if probe.get("session_guard_status") != "consistent":
                errors.append("subreports.capability_probe.session_guard_status must be consistent")
    return errors


@dataclass
class GuardRegistryWritebackRequest:
    capability_id: str
    report_path: str
    evidence_state: str


@dataclass
class GuardRegistryWritebackResult:
    capability_id: str
    status: str
    message: str
    report_path: str | None = None


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def apply_guard_registry_smoke_writeback(
    registry: dict[str, Any],
    request: GuardRegistryWritebackRequest,
    *,
    project_root: Path,
    row_index: dict[str, dict[str, Any]] | None = None,
    dry_run: bool = True,
    accepted_statuses: frozenset[str] | None = None,
) -> GuardRegistryWritebackResult:
    index = row_index or index_capability_rows(registry)
    row = index.get(request.capability_id)
    if row is None:
        return GuardRegistryWritebackResult(
            capability_id=request.capability_id,
            status="not_found",
            message=f"Unknown capability_id: {request.capability_id}",
        )
    if str(row.get("claim_level", "")) != "smoke":
        return GuardRegistryWritebackResult(
            capability_id=request.capability_id,
            status="rejected",
            message="Guard registry writeback only supports claim_level=smoke.",
        )

    report_path = Path(request.report_path)
    resolved = (project_root / report_path).resolve() if not report_path.is_absolute() else report_path.resolve()
    if not resolved.is_file():
        return GuardRegistryWritebackResult(
            capability_id=request.capability_id,
            status="rejected",
            message=f"report not found: {request.report_path}",
            report_path=request.report_path,
        )
    payload = json.loads(resolved.read_text(encoding="utf-8"))
    allowed = accepted_statuses or frozenset({"pass"})
    if str(payload.get("status", "")) not in allowed:
        return GuardRegistryWritebackResult(
            capability_id=request.capability_id,
            status="rejected",
            message=f"report status must be one of {sorted(allowed)}, got {payload.get('status')!r}",
            report_path=request.report_path,
        )

    triplet = {
        "evidence_state": request.evidence_state,
        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
    }
    triplet_error = validate_evidence_triplet(triplet)
    if triplet_error:
        return GuardRegistryWritebackResult(
            capability_id=request.capability_id,
            status="rejected",
            message=triplet_error,
            report_path=request.report_path,
        )

    rel_report = str(report_path).replace("\\", "/")
    if not dry_run:
        row["evidence"] = {**triplet, "report_path": rel_report, "last_verified_at": _utc_now_iso()}
        notes = row.get("notes")
        if not isinstance(notes, list):
            notes = []
        note = f"V-PROOF-52 smoke writeback from {rel_report}"
        if note not in notes:
            notes.append(note)
        row["notes"] = notes

    return GuardRegistryWritebackResult(
        capability_id=request.capability_id,
        status="applied",
        message="dry-run: would update smoke evidence." if dry_run else "smoke evidence updated.",
        report_path=rel_report,
    )


def resolve_guard_full_cad_report_path(
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
            raise FileNotFoundError(f"guard full CAD report not found: {resolved}")
        payload = json.loads(resolved.read_text(encoding="utf-8"))
        return resolved, payload, str(resolved.relative_to(root)).replace("\\", "/")

    canonical = root / RCAD_21_CANONICAL_REPORT
    if canonical.is_file():
        payload = json.loads(canonical.read_text(encoding="utf-8"))
        return canonical, payload, RCAD_21_CANONICAL_REPORT

    if run_real_cad:
        report = run_guard_full_cad_runner(
            root=root,
            output_dir=output_dir,
            use_real_cad=True,
            strict=True,
        )
        if report.get("status") == "external_blocker":
            raise RuntimeError("AutoCAD unavailable for guard full CAD runner")
        out = output_dir / "guard_full_cad_report.json"
        if not out.is_file():
            raise FileNotFoundError("guard_full_cad_runner did not write report")
        rel = str(out.relative_to(root)).replace("\\", "/")
        return out, report, rel

    raise FileNotFoundError(
        "Guard full CAD report missing. Provide --report, restore RCAD-21 evidence, or pass --real-cad."
    )


def assert_vproof_52_guard_cad_contract(*, project_root: Path) -> None:
    root = project_root.resolve()
    registry_path = root / "examples/capability_proof/cad_capability_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    index = index_capability_rows(registry)
    for capability_id in (
        GUARD_FULL_STRICT_CAPABILITY_ID,
        GUARD_WRITE_GUARD_CAPABILITY_ID,
        GUARD_NEGATIVE_CAD_CAPABILITY_ID,
        GUARD_CAPABILITY_PROBE_CAPABILITY_ID,
    ):
        if capability_id not in index:
            raise AssertionError(f"missing registry row: {capability_id}")
    row = index[GUARD_FULL_STRICT_CAPABILITY_ID]
    report_rel = str(row.get("evidence", {}).get("report_path", ""))
    if not report_rel:
        raise AssertionError("guard full strict row missing evidence.report_path")
    report_path = root / report_rel
    if not report_path.is_file():
        raise AssertionError(f"guard report not found: {report_rel}")
    errors = validate_guard_full_strict_report(
        json.loads(report_path.read_text(encoding="utf-8")),
        require_real_cad=True,
    )
    if errors:
        raise AssertionError(f"invalid guard full CAD report: {errors[:3]}")
    boundary = root / VPROOF_52_BOUNDARY_DOC
    if not boundary.is_file():
        raise AssertionError(f"missing V-PROOF-52 boundary doc: {VPROOF_52_BOUNDARY_DOC}")
    schema_errors = validate_capability_registry(registry)
    if schema_errors:
        raise AssertionError(f"registry validation failed: {schema_errors[:3]}")


def run_vproof_52_guard_cad_sync(
    *,
    project_root: Path,
    output_dir: Path,
    report_path: Path | None = None,
    run_real_cad: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    root = project_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_root = str(output_dir.relative_to(root)).replace("\\", "/")

    resolved, report, report_rel = resolve_guard_full_cad_report_path(
        project_root=root,
        report_path=report_path,
        output_dir=output_dir,
        run_real_cad=run_real_cad,
    )
    require_real = str(report.get("mode", "")) == "real_cad"
    validation_errors = validate_guard_full_strict_report(report, require_real_cad=require_real)
    if validation_errors:
        raise ValueError(f"guard full CAD report invalid: {validation_errors}")

    if resolved.parent.resolve() != output_dir.resolve():
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "guard_full_cad_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    registry_path = root / "examples/capability_proof/cad_capability_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    report_base = str(Path(report_rel).parent).replace("\\", "/")

    def _resolve_sub_path(key: str, default_suffix: str) -> str:
        raw = (report.get("subreport_paths") or {}).get(key, default_suffix)
        raw = str(raw).replace("\\", "/")
        if raw.startswith("output/"):
            return raw
        return f"{report_base}/{raw}"

    rows = build_guard_cad_registry_rows(output_root=report_base, report_rel=report_rel)
    merge_guard_cad_registry_rows(registry, rows)
    index = index_capability_rows(registry)

    writeback_results: list[GuardRegistryWritebackResult] = []
    parent_state = (
        EVIDENCE_CAD_CAPABILITY_VERIFIED if require_real else EVIDENCE_DRY_RUN_VALID_PLAN_ONLY
    )
    writeback_results.append(
        apply_guard_registry_smoke_writeback(
            registry,
            GuardRegistryWritebackRequest(
                capability_id=GUARD_FULL_STRICT_CAPABILITY_ID,
                report_path=report_rel,
                evidence_state=parent_state,
            ),
            project_root=root,
            row_index=index,
            dry_run=dry_run,
        )
    )
    sub_requests = [
        (
            GUARD_WRITE_GUARD_CAPABILITY_ID,
            _resolve_sub_path("write_guard", "subreports/write_guard/write_guard_cad_runner_report.json"),
            EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
        ),
        (
            GUARD_NEGATIVE_CAD_CAPABILITY_ID,
            _resolve_sub_path("negative_cad", "subreports/negative_cad/negative_cad_runner_report.json"),
            EVIDENCE_NEGATIVE_GUARD_VERIFIED,
        ),
        (
            GUARD_CAPABILITY_PROBE_CAPABILITY_ID,
            _resolve_sub_path("capability_probe", "subreports/capability_probe/cad_capability_probe.json"),
            EVIDENCE_CAD_CAPABILITY_VERIFIED,
        ),
    ]
    for capability_id, rel_path, evidence_state in sub_requests:
        sub_report_file = root / rel_path
        if not sub_report_file.is_file():
            continue
        accepted = (
            frozenset({"pass", "cad_capability_verified"})
            if capability_id == GUARD_CAPABILITY_PROBE_CAPABILITY_ID
            else frozenset({"pass"})
        )
        writeback_results.append(
            apply_guard_registry_smoke_writeback(
                registry,
                GuardRegistryWritebackRequest(
                    capability_id=capability_id,
                    report_path=rel_path,
                    evidence_state=evidence_state,
                ),
                project_root=root,
                row_index=index,
                dry_run=dry_run,
                accepted_statuses=accepted,
            )
        )

    if not dry_run:
        registry["updated_at"] = datetime.now(timezone.utc).date().isoformat()
        registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    applied = sum(1 for item in writeback_results if item.status == "applied")
    rejected = sum(1 for item in writeback_results if item.status == "rejected")
    summary = {
        "package_id": VPROOF_52_PACKAGE_ID,
        "report_path": report_rel,
        "report_mode": report.get("mode"),
        "strict_gate_status": report.get("strict_gate", {}).get("status"),
        "writeback_applied_count": applied,
        "writeback_rejected_count": rejected,
        "writeback_results": [item.__dict__ for item in writeback_results],
        "output_root": output_root,
    }
    (output_dir / "vproof_52_guard_cad_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary
