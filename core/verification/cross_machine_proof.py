"""V-PROOF-73: cross-machine playbook + coverage recalc (PROJ-03, user_gate for real CAD)."""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.schemas.validator import validate_value
from core.verification.capability_coverage import run_capability_coverage
from core.verification.capability_registry import index_capability_rows, validate_capability_registry
from core.verification.capability_registry_seed_common import PREVIEW_SAFETY
from core.verification.evidence_contract import validate_evidence_triplet
from core.verification.evidence_vocabulary import (
    EVIDENCE_BENCHMARK_PASS_NON_CAD,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)

VPROOF_73_PACKAGE_ID = "V-PROOF-73-CROSS-MACHINE"
VPROOF_73_BOUNDARY_DOC = "docs/verification/vproof_73_cross_machine.md"
VPROOF_73_RUNBOOK_DOC = "docs/onboarding/migration-checklist.md"
VPROOF_73_DEFAULT_OUTPUT = "output/validation_runs/vproof-73-cross-machine"
BASELINE_REL = Path("examples/capability_proof/cross_machine_coverage_baseline.json")
PLAYBOOK_MANIFEST_REL = Path("examples/capability_proof/cross_machine_playbook_manifest.json")
REPORT_SCHEMA_REL = Path("core/schemas/cross_machine_report.schema.json")

CROSS_MACHINE_PLAYBOOK_CAPABILITY_ID = "project.cross_machine.playbook"
CROSS_MACHINE_COVERAGE_RECALC_CAPABILITY_ID = "project.cross_machine.coverage_recalc"

HEADLINE_TOLERANCE_PERCENT = 0.05


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_cross_machine_baseline(*, project_root: Path) -> dict[str, Any]:
    path = project_root / BASELINE_REL
    return json.loads(path.read_text(encoding="utf-8"))


def load_cross_machine_playbook_manifest(*, project_root: Path) -> dict[str, Any]:
    path = project_root / PLAYBOOK_MANIFEST_REL
    return json.loads(path.read_text(encoding="utf-8"))


def _cad_mcp_python() -> Path:
    return Path(os.environ.get("USERPROFILE", "")) / ".codex" / "mcp" / "CAD-MCP" / ".venv" / "Scripts" / "python.exe"


def _run_git_version() -> tuple[str, int]:
    completed = subprocess.run(
        ["git", "--version"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return (completed.stdout.strip() or completed.stderr.strip(), completed.returncode)


def _run_self_check(project_root: Path, python_exe: Path) -> int:
    script = project_root / "scripts" / "self_check.py"
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    completed = subprocess.run(
        [str(python_exe), str(script)],
        cwd=str(project_root),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    return completed.returncode


def compare_coverage_to_baseline(
    *,
    current_summary: dict[str, Any],
    baseline_summary: dict[str, Any],
) -> dict[str, Any]:
    baseline_headline = float(baseline_summary.get("cad_strength_headline_percent", 0.0))
    current_headline = float(current_summary.get("cad_strength_headline_percent", 0.0))
    headline_delta = round(current_headline - baseline_headline, 4)
    total_delta = int(current_summary.get("total_count", 0)) - int(baseline_summary.get("total_count", 0))

    within_tolerance = abs(headline_delta) <= HEADLINE_TOLERANCE_PERCENT and total_delta == 0
    status = "pass" if within_tolerance else "fail"
    return {
        "status": status,
        "baseline_headline_percent": baseline_headline,
        "current_headline_percent": current_headline,
        "headline_delta_percent": headline_delta,
        "total_count_delta": total_delta,
        "within_tolerance": within_tolerance,
    }


def build_cross_machine_report(
    *,
    project_root: Path,
    output_dir: Path,
    python_executable: Path | None = None,
) -> dict[str, Any]:
    root = project_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    python_exe = python_executable or Path(sys.executable)
    cad_mcp = _cad_mcp_python()
    cad_mcp_present = cad_mcp.is_file()

    step_results: list[dict[str, Any]] = []

    _, git_code = _run_git_version()
    step_results.append(
        {
            "step_id": "git_available",
            "title": "Git available",
            "status": "pass" if git_code == 0 else "fail",
        }
    )

    step_results.append(
        {
            "step_id": "cad_mcp_venv",
            "title": "CAD-MCP venv python exists",
            "status": "pass" if cad_mcp_present else "fail",
        }
    )

    self_check_code = _run_self_check(root, python_exe)
    step_results.append(
        {
            "step_id": "self_check",
            "title": "Repository self_check",
            "status": "pass" if self_check_code == 0 else "fail",
        }
    )

    coverage_path = output_dir / "cad_capability_coverage.json"
    coverage_report = run_capability_coverage(
        root,
        output_path=coverage_path,
    )
    baseline = load_cross_machine_baseline(project_root=root)
    baseline_summary = baseline.get("summary", {})
    current_summary = coverage_report.get("summary", {}) if isinstance(coverage_report.get("summary"), dict) else {}
    recalc = compare_coverage_to_baseline(
        current_summary=current_summary,
        baseline_summary=baseline_summary,
    )
    recalc["baseline_path"] = str(BASELINE_REL).replace("\\", "/")
    recalc["current_path"] = str(coverage_path.relative_to(root)).replace("\\", "/")

    step_results.append(
        {
            "step_id": "coverage_recalc",
            "title": "Capability coverage recalc vs baseline",
            "status": "pass" if recalc["status"] == "pass" and coverage_report.get("status") == "pass" else "fail",
        }
    )

    manifest = load_cross_machine_playbook_manifest(project_root=root)
    user_gate_steps = [
        str(item.get("step_id", ""))
        for item in manifest.get("user_gate_steps", [])
        if isinstance(item, dict)
    ]

    passed = sum(1 for item in step_results if item.get("status") == "pass")
    failed = sum(1 for item in step_results if item.get("status") == "fail")
    overall = "pass" if failed == 0 else "blocked"

    return {
        "version": "0.1",
        "package_id": VPROOF_73_PACKAGE_ID,
        "status": overall,
        "generated_at": _utc_now_iso(),
        "machine": {
            "platform": platform.platform(),
            "python_version": sys.version.split()[0],
            "cad_mcp_venv_present": cad_mcp_present,
            "project_root": str(root),
        },
        "no_cad_steps": step_results,
        "coverage_recalc": recalc,
        "user_gate": {
            "status": "pending",
            "pending_steps": user_gate_steps,
            "human_runbook_path": str(manifest.get("human_runbook_path", VPROOF_73_RUNBOOK_DOC)),
        },
        "summary": {
            "no_cad_pass_count": passed,
            "no_cad_fail_count": failed,
        },
        "notes": [
            "V-PROOF-73 no-CAD machine audit pass does not complete full migration.",
            "Real CAD steps remain user_gate per migration-checklist.md.",
            "Coverage recalc compares to committed baseline; identical registry should match within tolerance.",
        ],
    }


def validate_cross_machine_report(report: dict[str, Any], *, project_root: Path) -> list[str]:
    schema = json.loads((project_root / REPORT_SCHEMA_REL).read_text(encoding="utf-8"))
    return validate_value(report, schema)


def merge_cross_machine_registry_rows(registry: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, int]:
    from core.verification.negative_plan_registry import merge_negative_plan_registry_rows

    return merge_negative_plan_registry_rows(registry, rows)


def build_cross_machine_registry_rows(*, output_root: str) -> list[dict[str, Any]]:
    report_rel = f"{output_root}/cross_machine_report.json"

    def _row(capability_id: str, display_name: str, source_key: str) -> dict[str, Any]:
        return {
            "capability_id": capability_id,
            "display_name": display_name,
            "category": "project_sample",
            "claim_level": "smoke",
            "ladder_level": "L0",
            "domain": "generic",
            "tags": ["project", "PROJ-03", "V-PROOF-73", "migration"],
            "notes": [
                "V-PROOF-73 cross-machine smoke row.",
                "Playbook/recalc pass is machine audit only; not geometry_verified.",
            ],
            "source_refs": [
                {
                    "source_kind": "documentation",
                    "source_path": str(PLAYBOOK_MANIFEST_REL).replace("\\", "/"),
                    "source_key": source_key,
                }
            ],
            "cad_case": {
                "case_kind": "script",
                "requires_real_cad": False,
                "entrypoint": "scripts/run_vproof_73_cross_machine_sync.py",
                "output_path": report_rel,
                "safety": dict(PREVIEW_SAFETY),
            },
        }

    return [
        _row(CROSS_MACHINE_PLAYBOOK_CAPABILITY_ID, "Cross-machine migration playbook (machine)", "playbook"),
        _row(
            CROSS_MACHINE_COVERAGE_RECALC_CAPABILITY_ID,
            "Cross-machine coverage recalc vs baseline",
            "coverage_recalc",
        ),
    ]


def apply_cross_machine_smoke_writeback(
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


def run_vproof_73_cross_machine_sync(
    *,
    project_root: Path,
    output_dir: Path,
    dry_run: bool = False,
) -> dict[str, Any]:
    root = project_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_root = str(output_dir.relative_to(root)).replace("\\", "/")

    report = build_cross_machine_report(project_root=root, output_dir=output_dir)
    schema_errors = validate_cross_machine_report(report, project_root=root)
    if schema_errors:
        report["status"] = "blocked"
        report["schema_errors"] = schema_errors

    report_path = output_dir / "cross_machine_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if report.get("status") != "pass":
        return {
            "package_id": VPROOF_73_PACKAGE_ID,
            "report_status": report.get("status"),
            "schema_errors": schema_errors,
            "output_root": output_root,
        }

    registry_path = root / "examples/capability_proof/cad_capability_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    rows = build_cross_machine_registry_rows(output_root=output_root)
    merge_cross_machine_registry_rows(registry, rows)
    index = index_capability_rows(registry)

    report_rel = f"{output_root}/cross_machine_report.json"
    writeback_applied = 0
    writeback_rejected = 0
    for capability_id in (CROSS_MACHINE_PLAYBOOK_CAPABILITY_ID, CROSS_MACHINE_COVERAGE_RECALC_CAPABILITY_ID):
        status = apply_cross_machine_smoke_writeback(
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

    recalc = report.get("coverage_recalc", {})
    return {
        "package_id": VPROOF_73_PACKAGE_ID,
        "report_status": report.get("status"),
        "user_gate_pending": report.get("user_gate", {}).get("pending_steps", []),
        "coverage_headline_percent": recalc.get("current_headline_percent"),
        "headline_delta_percent": recalc.get("headline_delta_percent"),
        "registry_row_count": len(rows),
        "writeback_applied_count": writeback_applied,
        "writeback_rejected_count": writeback_rejected,
        "output_root": output_root,
    }


def assert_vproof_73_cross_machine_contract(*, project_root: Path) -> None:
    root = project_root.resolve()
    for rel in (VPROOF_73_BOUNDARY_DOC, VPROOF_73_RUNBOOK_DOC):
        if not (root / rel).is_file():
            raise AssertionError(f"missing doc: {rel}")

    registry = json.loads((root / "examples/capability_proof/cad_capability_registry.json").read_text(encoding="utf-8"))
    index = index_capability_rows(registry)
    for capability_id in (CROSS_MACHINE_PLAYBOOK_CAPABILITY_ID, CROSS_MACHINE_COVERAGE_RECALC_CAPABILITY_ID):
        if capability_id not in index:
            raise AssertionError(f"missing registry row: {capability_id}")

    schema_errors = validate_capability_registry(registry)
    if schema_errors:
        raise AssertionError(f"registry validation failed: {schema_errors[:3]}")
