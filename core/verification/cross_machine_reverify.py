"""BETA-CROSS-MACHINE-02: migration re-verify gate (no-CAD + optional real CAD user steps)."""

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
from core.verification.cross_machine_proof import (
    PLAYBOOK_MANIFEST_REL,
    REPORT_SCHEMA_REL,
    build_cross_machine_report,
    load_cross_machine_playbook_manifest,
)

BETA_CROSS_MACHINE_02_PACKAGE_ID = "BETA-CROSS-MACHINE-02"
BETA_CROSS_MACHINE_02_RUNBOOK = "docs/runbooks/cross-machine-reverify.md"
BETA_CROSS_MACHINE_02_HUMAN_CHECKLIST = "docs/onboarding/migration-checklist.md"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _cad_mcp_python() -> Path:
    return Path(os.environ.get("USERPROFILE", "")) / ".codex" / "mcp" / "CAD-MCP" / ".venv" / "Scripts" / "python.exe"


def _run_subprocess(
    command: list[str],
    *,
    project_root: Path,
    timeout: int = 600,
) -> dict[str, Any]:
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
        timeout=timeout,
    )
    return {
        "command": command,
        "exit_code": completed.returncode,
        "status": "pass" if completed.returncode == 0 else "fail",
        "stdout": completed.stdout or "",
        "stdout_tail": (completed.stdout or "")[-3000:],
        "stderr_tail": (completed.stderr or "")[-1500:],
    }


def _schema_no_cad_steps(steps: list[dict[str, Any]]) -> list[dict[str, str]]:
    cleaned: list[dict[str, str]] = []
    for step in steps:
        status = str(step.get("status", "fail"))
        if status not in {"pass", "fail", "skipped"}:
            status = "fail"
        cleaned.append(
            {
                "step_id": str(step.get("step_id", "")),
                "title": str(step.get("title", "")),
                "status": status,
            }
        )
    return cleaned


def _probe_python_deps(python_exe: Path) -> list[dict[str, Any]]:
    probes = [
        ("pillow", "import PIL; print(PIL.__version__)"),
        ("pywin32", "import win32com.client; print('ok')"),
        ("win32gui", "import win32gui; print('ok')"),
    ]
    results: list[dict[str, Any]] = []
    for step_id, code in probes:
        completed = subprocess.run(
            [str(python_exe), "-c", code],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        results.append(
            {
                "step_id": step_id,
                "title": f"import {step_id}",
                "status": "pass" if completed.returncode == 0 else "fail",
                "message": (completed.stdout or completed.stderr or "").strip()[:200],
            }
        )
    return results


def _probe_autocad_com() -> dict[str, Any]:
    try:
        from core.cad_io.autocad_com import AutoCADComDriver

        driver = AutoCADComDriver(connect_existing_only=True)
        doc_name = str(getattr(getattr(driver, "doc", None), "Name", "") or "")
        return {
            "step_id": "autocad_session",
            "title": "AutoCAD COM active document",
            "status": "pass" if doc_name else "fail",
            "active_document": doc_name,
        }
    except Exception as exc:
        return {
            "step_id": "autocad_session",
            "title": "AutoCAD COM active document",
            "status": "fail",
            "error": str(exc),
        }


def _run_real_cad_user_gate(
    *,
    project_root: Path,
    python_exe: Path,
    output_dir: Path,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    results.append(_probe_autocad_com())
    if results[-1].get("status") != "pass":
        for pending in ("execute_plan_smoke", "cad_validation", "capture_window"):
            results.append(
                {
                    "step_id": pending,
                    "title": pending,
                    "status": "skipped",
                    "reason": "autocad_session failed",
                }
            )
        return results

    plan = project_root / "examples" / "plans" / "draw_test_cabinet.json"
    execute_run = _run_subprocess(
        [str(python_exe), "scripts/execute_plan.py", str(plan)],
        project_root=project_root,
        timeout=180,
    )
    handle_count = 0
    execution_payload: dict[str, Any] = {}
    if execute_run.get("status") == "pass":
        try:
            stdout = str(execute_run.get("stdout", "") or execute_run.get("stdout_tail", ""))
            start = stdout.find("{")
            end = stdout.rfind("}")
            if start >= 0 and end > start:
                payload = json.loads(stdout[start : end + 1])
                if isinstance(payload, dict):
                    execution_payload = payload
                handle_count = len(payload.get("created_handles", []) or [])
        except json.JSONDecodeError:
            handle_count = 0
    execute_step = {
        "step_id": "execute_plan_smoke",
        "title": "execute_plan draw_test_cabinet",
        **execute_run,
        "created_handle_count": handle_count,
    }
    results.append(execute_step)
    geometry_ok = execute_run.get("status") == "pass" and handle_count >= 4
    results.append(
        {
            "step_id": "migration_geometry_smoke",
            "title": "execute_plan created handles (migration smoke)",
            "status": "pass" if geometry_ok else "fail",
            "created_handle_count": handle_count,
            "geometry_verified": geometry_ok,
            "notes": "P0 gate uses execute_plan smoke; full run_cad_validation remains optional in migration-checklist.md.",
        }
    )

    preview_path = output_dir / "migration-reverify-window.png"
    execution_summary_path = output_dir / "migration-reverify-execution-summary.json"
    execution_summary_path.write_text(
        json.dumps(
            execution_payload
            or {
                "status": execute_run.get("status"),
                "created_handles": [],
                "created_handle_count": 0,
                "source": "execute_plan_smoke_stdout_unavailable",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    capture = _run_subprocess(
        [
            str(python_exe),
            "scripts/render_preview.py",
            "--capture-autocad-window",
            "--execution-summary",
            str(execution_summary_path),
            "--output",
            str(preview_path),
        ],
        project_root=project_root,
        timeout=120,
    )
    capture["step_id"] = "capture_window"
    capture["title"] = "AutoCAD window capture (visual_aid_only)"
    capture["screenshot_path"] = str(preview_path.relative_to(project_root)).replace("\\", "/")
    capture["status"] = "pass" if capture["status"] == "pass" and preview_path.is_file() else "fail"
    results.append(capture)

    results.append(
        {
            "step_id": "mcp_draw_smoke",
            "title": "CAD-MCP draw smoke in IDE",
            "status": "manual_pending",
            "notes": "Operator must confirm one MCP draw in Cursor/Codex; not automated in this gate.",
        }
    )
    return results


def build_beta_cross_machine_02_report(
    *,
    project_root: Path,
    output_dir: Path,
    python_executable: Path | None = None,
    include_real_cad: bool = True,
    skip_unittest: bool = False,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    root = project_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    python_exe = python_executable or _cad_mcp_python()
    if not python_exe.is_file():
        python_exe = Path(sys.executable)

    base = build_cross_machine_report(project_root=root, output_dir=output_dir, python_executable=python_exe)

    extra_steps: list[dict[str, Any]] = []
    extra_steps.extend(_probe_python_deps(python_exe))

    gate_args = [str(python_exe), "scripts/run_core_platform_gate.py", "--skip-unittest"] if skip_unittest else [
        str(python_exe),
        "scripts/run_core_platform_gate.py",
    ]
    gate_run = _run_subprocess(gate_args, project_root=root, timeout=900 if not skip_unittest else 120)
    extra_steps.append(
        {
            "step_id": "core_platform_gate",
            "title": "Core platform completion gate",
            "status": gate_run["status"],
            "exit_code": gate_run["exit_code"],
        }
    )

    user_gate_results: list[dict[str, Any]] = []
    if include_real_cad:
        user_gate_results = _run_real_cad_user_gate(project_root=root, python_exe=python_exe, output_dir=output_dir)

    manifest = load_cross_machine_playbook_manifest(project_root=root)
    pending_manual_ids = [
        str(item.get("step_id", ""))
        for item in manifest.get("user_gate_steps", [])
        if isinstance(item, dict)
    ]
    if include_real_cad:
        pending_manual_ids = [item.get("step_id", "mcp_draw_smoke") for item in user_gate_results if item.get("status") == "manual_pending"] or pending_manual_ids

    automated = [item for item in user_gate_results if item.get("status") not in ("manual_pending", "skipped")]
    user_fail = sum(1 for item in automated if item.get("status") != "pass")
    user_pass = sum(1 for item in automated if item.get("status") == "pass")

    no_cad_all = list(base.get("no_cad_steps", [])) + extra_steps
    no_cad_fail = sum(1 for item in no_cad_all if item.get("status") == "fail")
    overall = "pass"
    if no_cad_fail > 0:
        overall = "blocked"
    elif include_real_cad and user_fail > 0:
        overall = "blocked"

    user_gate_status = "pending" if pending_manual_ids else "acknowledged"

    report = {
        **base,
        "package_id": BETA_CROSS_MACHINE_02_PACKAGE_ID,
        "status": overall,
        "generated_at": _utc_now_iso(),
        "machine": {
            "platform": str(base.get("machine", {}).get("platform", platform.platform())),
            "python_version": str(base.get("machine", {}).get("python_version", sys.version.split()[0])),
            "cad_mcp_venv_present": bool(base.get("machine", {}).get("cad_mcp_venv_present")),
            "project_root": str(root),
        },
        "no_cad_steps": _schema_no_cad_steps(no_cad_all),
        "user_gate": {
            "status": user_gate_status,
            "pending_steps": pending_manual_ids,
            "human_runbook_path": BETA_CROSS_MACHINE_02_RUNBOOK,
        },
        "summary": {
            "no_cad_pass_count": sum(1 for item in no_cad_all if item.get("status") == "pass"),
            "no_cad_fail_count": no_cad_fail,
        },
        "notes": [
            "BETA-CROSS-MACHINE-02 extends V-PROOF-73 with core platform gate and optional real CAD smoke.",
            "user_gate.status=pending until MCP manual draw is acknowledged on this machine.",
            "Extended user_gate detail is written to beta_cross_machine_02_user_gate.json beside this report.",
        ],
    }
    return report, user_gate_results


def validate_beta_cross_machine_02_report(report: dict[str, Any], *, project_root: Path) -> list[str]:
    schema = json.loads((project_root / REPORT_SCHEMA_REL).read_text(encoding="utf-8"))
    return validate_value(report, schema)


def run_beta_cross_machine_02_gate(
    *,
    project_root: Path,
    output_dir: Path,
    include_real_cad: bool = True,
    skip_unittest: bool = False,
) -> dict[str, Any]:
    root = project_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    report, user_gate_results = build_beta_cross_machine_02_report(
        project_root=root,
        output_dir=output_dir,
        include_real_cad=include_real_cad,
        skip_unittest=skip_unittest,
    )
    schema_errors = validate_beta_cross_machine_02_report(report, project_root=root)
    if schema_errors:
        report = {**report, "status": "blocked", "schema_errors": schema_errors}

    report_path = output_dir / "beta_cross_machine_02_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    user_gate_path = output_dir / "beta_cross_machine_02_user_gate.json"
    user_gate_path.write_text(
        json.dumps(
            {
                "package_id": BETA_CROSS_MACHINE_02_PACKAGE_ID,
                "hostname": platform.node(),
                "automated_steps": user_gate_results,
                "full_checklist_path": BETA_CROSS_MACHINE_02_HUMAN_CHECKLIST,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    manifest_path = output_dir / "beta_cross_machine_02_summary.json"
    automated_pass = sum(1 for item in user_gate_results if item.get("status") == "pass")
    manifest_path.write_text(
        json.dumps(
            {
                "package_id": BETA_CROSS_MACHINE_02_PACKAGE_ID,
                "status": report.get("status"),
                "operator_status": "partial" if report.get("user_gate", {}).get("status") == "pending" else "complete",
                "output_root": str(output_dir.relative_to(root)).replace("\\", "/"),
                "report_path": str(report_path.relative_to(root)).replace("\\", "/"),
                "user_gate_status": report.get("user_gate", {}).get("status"),
                "pending_manual_steps": report.get("user_gate", {}).get("pending_steps", []),
                "automated_cad_pass_count": automated_pass,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return report
