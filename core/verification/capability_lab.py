"""V-PROOF-72: Capability Lab tier orchestrator (nightly / CI entry)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.schemas.validator import validate_value
from core.verification.capability_registry import index_capability_rows, validate_capability_registry
from core.verification.capability_registry_seed_common import PREVIEW_SAFETY
from core.verification.evidence_contract import validate_evidence_triplet
from core.verification.evidence_vocabulary import (
    EVIDENCE_BENCHMARK_PASS_NON_CAD,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)

VPROOF_72_PACKAGE_ID = "V-PROOF-72-NIGHTLY-LAB-ENTRY"
VPROOF_72_BOUNDARY_DOC = "docs/verification/vproof_72_nightly_lab.md"
VPROOF_72_RUNBOOK_DOC = "docs/runbooks/nightly_capability_lab.md"
VPROOF_72_DEFAULT_OUTPUT = "output/validation_runs/vproof-72-nightly-lab"
DEFAULT_MANIFEST_REL = Path("examples/capability_proof/nightly_lab_tier_manifest.json")
REPORT_SCHEMA_REL = Path("core/schemas/capability_lab_report.schema.json")

LAB_NIGHTLY_ROLLUP_CAPABILITY_ID = "lab.nightly.rollup"
LAB_NIGHTLY_TIER_L1_CAPABILITY_ID = "lab.nightly.tier_l1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_nightly_lab_manifest(*, project_root: Path, path: Path | None = None) -> dict[str, Any]:
    manifest_path = path or (project_root / DEFAULT_MANIFEST_REL)
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def get_tier_spec(manifest: dict[str, Any], tier: str) -> dict[str, Any]:
    tiers = manifest.get("tiers")
    if not isinstance(tiers, dict) or tier not in tiers:
        raise ValueError(f"unknown lab tier: {tier!r}; allowed={sorted(tiers.keys()) if isinstance(tiers, dict) else []}")
    spec = tiers[tier]
    if not isinstance(spec, dict):
        raise ValueError(f"tier {tier!r} must be an object")
    return spec


def _format_args(args: list[str], *, output_dir: Path) -> list[str]:
    formatted: list[str] = []
    for arg in args:
        formatted.append(
            str(arg).format(output_dir=str(output_dir).replace("\\", "/"))
        )
    return formatted


def _evaluate_no_cad_lab_step(
    step_id: str,
    *,
    output_dir: Path,
    exit_code: int,
) -> tuple[bool, str]:
    if exit_code == 0:
        return True, "exit_zero"

    if step_id == "local_cad_regression_no_cad":
        report_path = output_dir / "local_cad_regression" / "local_cad_regression_report.json"
        if not report_path.is_file():
            return False, "missing_report"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
        if summary.get("non_cad_only") and summary.get("geometry_verified_case_count", 0) == 0:
            if int(summary.get("external_blocker_count", 0)) == 0:
                return True, "no_cad_deferred_accepted"
        return False, "regression_summary_not_acceptable"

    if step_id == "cad_validation_no_cad":
        report_path = output_dir / "cad_validation" / "report.json"
        if not report_path.is_file():
            return False, "missing_report"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("include_cad") is False and report.get("environment_optional") is True:
            failed_required = [
                step
                for step in report.get("steps", [])
                if isinstance(step, dict)
                and step.get("required")
                and step.get("status") not in {"pass", "skipped"}
                and step.get("cad_required")
            ]
            if not failed_required:
                return True, "no_cad_environment_optional_accepted"
        return False, "validation_report_not_acceptable"

    return False, "exit_nonzero"


def _run_script_step(
    *,
    project_root: Path,
    python_executable: Path,
    script_rel: str,
    args: list[str],
    dry_run: bool,
) -> dict[str, Any]:
    script_path = project_root / script_rel.replace("\\", "/")
    if not script_path.is_file():
        return {
            "status": "fail",
            "exit_code": 127,
            "command": str(script_path),
            "error": f"script not found: {script_rel}",
        }
    command = [str(python_executable), str(script_path), *args]
    command_display = " ".join(command)
    if dry_run:
        return {"status": "dry_run", "exit_code": 0, "command": command_display}

    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    completed = subprocess.run(
        command,
        cwd=str(project_root),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=600,
    )
    status = "pass" if completed.returncode == 0 else "fail"
    result: dict[str, Any] = {
        "status": status,
        "exit_code": completed.returncode,
        "command": command_display,
    }
    if status == "fail":
        stderr_tail = (completed.stderr or "")[-500:]
        stdout_tail = (completed.stdout or "")[-500:]
        result["stderr_tail"] = stderr_tail
        result["stdout_tail"] = stdout_tail
    return result


def _coverage_headline_from_report(output_dir: Path) -> float | None:
    coverage_path = output_dir / "cad_capability_coverage.json"
    if not coverage_path.is_file():
        return None
    try:
        payload = json.loads(coverage_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    summary = payload.get("summary")
    if isinstance(summary, dict):
        value = summary.get("cad_strength_headline_percent")
        if isinstance(value, (int, float)):
            return float(value)
    return None


def run_capability_lab(
    *,
    project_root: Path,
    tier: str,
    output_dir: Path,
    manifest_path: Path | None = None,
    python_executable: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    root = project_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = load_nightly_lab_manifest(project_root=root, path=manifest_path)
    tier_spec = get_tier_spec(manifest, tier)
    python_exe = python_executable or Path(sys.executable)

    step_results: list[dict[str, Any]] = []
    for step in tier_spec.get("steps", []):
        if not isinstance(step, dict):
            continue
        step_id = str(step.get("step_id", "unknown"))
        title = str(step.get("title", step_id))
        script = str(step.get("script", ""))
        accept_mode = str(step.get("accept_mode", "exit_zero"))
        raw_args = step.get("args", [])
        args = _format_args([str(item) for item in raw_args], output_dir=output_dir) if isinstance(raw_args, list) else []
        outcome = _run_script_step(
            project_root=root,
            python_executable=python_exe,
            script_rel=script,
            args=args,
            dry_run=dry_run,
        )
        if (
            not dry_run
            and accept_mode == "no_cad_lab"
            and outcome.get("status") == "fail"
        ):
            accepted, reason = _evaluate_no_cad_lab_step(
                step_id,
                output_dir=output_dir,
                exit_code=int(outcome.get("exit_code", 1)),
            )
            if accepted:
                outcome = {
                    **outcome,
                    "status": "pass",
                    "lab_accept_reason": reason,
                }
        step_results.append(
            {
                "step_id": step_id,
                "title": title,
                "accept_mode": accept_mode,
                **outcome,
            }
        )

    passed = sum(1 for item in step_results if item.get("status") in {"pass", "dry_run"})
    failed = sum(1 for item in step_results if item.get("status") == "fail")
    overall = "pass" if failed == 0 and step_results else "fail"
    if not step_results:
        overall = "blocked"

    output_root = str(output_dir.relative_to(root)).replace("\\", "/")
    headline = _coverage_headline_from_report(output_dir)

    report = {
        "version": "0.1",
        "package_id": VPROOF_72_PACKAGE_ID,
        "tier": tier,
        "status": overall,
        "generated_at": _utc_now_iso(),
        "requires_real_cad": bool(tier_spec.get("requires_real_cad")),
        "output_root": output_root,
        "steps": step_results,
        "summary": {
            "step_count": len(step_results),
            "passed_count": passed,
            "failed_count": failed,
            **({"cad_strength_headline_percent": headline} if headline is not None else {}),
        },
        "notes": [
            "L1 default is no-CAD nightly; deferred cases are expected.",
            "Lab pass does not imply geometry_verified or Table C improvement.",
        ],
    }
    return report


def validate_capability_lab_report(report: dict[str, Any], *, project_root: Path) -> list[str]:
    schema = json.loads((project_root / REPORT_SCHEMA_REL).read_text(encoding="utf-8"))
    return validate_value(report, schema)


def merge_nightly_lab_registry_rows(registry: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, int]:
    from core.verification.negative_plan_registry import merge_negative_plan_registry_rows

    return merge_negative_plan_registry_rows(registry, rows)


def build_nightly_lab_registry_rows(*, output_root: str) -> list[dict[str, Any]]:
    report_rel = f"{output_root}/capability_lab_report.json"

    def _row(capability_id: str, display_name: str, source_key: str) -> dict[str, Any]:
        return {
            "capability_id": capability_id,
            "display_name": display_name,
            "category": "other",
            "claim_level": "smoke",
            "ladder_level": "L0",
            "domain": "generic",
            "tags": ["lab", "nightly", "V-PROOF-72"],
            "notes": [
                "V-PROOF-72 nightly capability lab smoke row.",
                "Lab tier pass is orchestration only; not geometry_verified.",
            ],
            "source_refs": [
                {
                    "source_kind": "documentation",
                    "source_path": str(DEFAULT_MANIFEST_REL).replace("\\", "/"),
                    "source_key": source_key,
                }
            ],
            "cad_case": {
                "case_kind": "script",
                "requires_real_cad": False,
                "entrypoint": "scripts/run_capability_lab.py",
                "output_path": report_rel,
                "safety": dict(PREVIEW_SAFETY),
            },
        }

    return [
        _row(LAB_NIGHTLY_ROLLUP_CAPABILITY_ID, "Nightly capability lab rollup", "rollup"),
        _row(LAB_NIGHTLY_TIER_L1_CAPABILITY_ID, "Nightly capability lab tier L1 (no-CAD)", "L1"),
    ]


def apply_nightly_lab_smoke_writeback(
    registry: dict[str, Any],
    *,
    capability_id: str,
    report_path: str,
    project_root: Path,
    row_index: dict[str, dict[str, Any]] | None = None,
    dry_run: bool = True,
) -> str:
    index = row_index or index_capability_rows(registry)
    row = index.get(capability_id)
    if row is None:
        return "not_found"
    if str(row.get("claim_level", "")) != "smoke":
        return "rejected"

    resolved = project_root / report_path.replace("\\", "/")
    if not resolved.is_file():
        return "rejected"
    payload = json.loads(resolved.read_text(encoding="utf-8"))
    if payload.get("status") != "pass":
        return "rejected"

    triplet = {
        "evidence_state": EVIDENCE_BENCHMARK_PASS_NON_CAD,
        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
    }
    if validate_evidence_triplet(triplet):
        return "rejected"
    if not dry_run:
        row["evidence"] = {**triplet, "report_path": report_path, "last_verified_at": _utc_now_iso()}
    return "applied"


def run_vproof_72_nightly_lab_sync(
    *,
    project_root: Path,
    output_dir: Path,
    tier: str = "L1",
    manifest_path: Path | None = None,
    dry_run: bool = False,
    lab_dry_run: bool = False,
) -> dict[str, Any]:
    root = project_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    report = run_capability_lab(
        project_root=root,
        tier=tier,
        output_dir=output_dir,
        manifest_path=manifest_path,
        dry_run=lab_dry_run,
    )
    schema_errors = validate_capability_lab_report(report, project_root=root)
    if schema_errors:
        report["status"] = "fail"
        report["schema_errors"] = schema_errors

    report_path = output_dir / "capability_lab_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if report.get("status") != "pass":
        return {
            "package_id": VPROOF_72_PACKAGE_ID,
            "lab_status": report.get("status"),
            "tier": tier,
            "schema_errors": schema_errors,
            "failed_steps": [s["step_id"] for s in report.get("steps", []) if s.get("status") == "fail"],
        }

    output_root = str(output_dir.relative_to(root)).replace("\\", "/")
    registry_path = root / "examples/capability_proof/cad_capability_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    rows = build_nightly_lab_registry_rows(output_root=output_root)
    merge_nightly_lab_registry_rows(registry, rows)
    index = index_capability_rows(registry)

    report_rel = f"{output_root}/capability_lab_report.json"
    writeback_applied = 0
    writeback_rejected = 0
    for capability_id in (LAB_NIGHTLY_ROLLUP_CAPABILITY_ID, LAB_NIGHTLY_TIER_L1_CAPABILITY_ID):
        status = apply_nightly_lab_smoke_writeback(
            registry,
            capability_id=capability_id,
            report_path=report_rel,
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
        "package_id": VPROOF_72_PACKAGE_ID,
        "lab_status": report.get("status"),
        "tier": tier,
        "step_count": report["summary"]["step_count"],
        "passed_count": report["summary"]["passed_count"],
        "registry_row_count": len(rows),
        "writeback_applied_count": writeback_applied,
        "writeback_rejected_count": writeback_rejected,
        "output_root": output_root,
        "cad_strength_headline_percent": report["summary"].get("cad_strength_headline_percent"),
    }


def assert_vproof_72_nightly_lab_contract(*, project_root: Path) -> None:
    root = project_root.resolve()
    for rel in (VPROOF_72_BOUNDARY_DOC, VPROOF_72_RUNBOOK_DOC):
        if not (root / rel).is_file():
            raise AssertionError(f"missing doc: {rel}")

    manifest = load_nightly_lab_manifest(project_root=root)
    if "L1" not in manifest.get("tiers", {}):
        raise AssertionError("nightly lab manifest must define tier L1")

    registry = json.loads((root / "examples/capability_proof/cad_capability_registry.json").read_text(encoding="utf-8"))
    index = index_capability_rows(registry)
    for capability_id in (LAB_NIGHTLY_ROLLUP_CAPABILITY_ID, LAB_NIGHTLY_TIER_L1_CAPABILITY_ID):
        if capability_id not in index:
            raise AssertionError(f"missing registry row: {capability_id}")

    schema_errors = validate_capability_registry(registry)
    if schema_errors:
        raise AssertionError(f"registry validation failed: {schema_errors[:3]}")
