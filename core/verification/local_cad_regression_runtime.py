"""Runtime helpers for local CAD regression matrix steps."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from core.verification.cad_validation_types import CommandResult, CommandRunner

DEFAULT_TIMEOUT_SECONDS = 600

def default_command_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=timeout_seconds,
        check=False,
    )
    return CommandResult(returncode=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)


def _python() -> str:
    return sys.executable


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _extract_json(stdout: str) -> dict[str, Any]:
    text = stdout.strip()
    if not text:
        return {}
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return {}
        try:
            value = json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return {}
    return value if isinstance(value, dict) else {}


def _run_step(
    *,
    step_id: str,
    title: str,
    command: list[str],
    output_dir: Path,
    root: Path,
    command_runner: CommandRunner,
    failure_category: str,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    strict_geometry: bool = False,
) -> dict[str, Any]:
    safe_id = step_id.replace("/", "_")
    stdout_path = output_dir / f"{safe_id}.stdout.txt"
    stderr_path = output_dir / f"{safe_id}.stderr.txt"
    try:
        result = command_runner(command, root, timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        result = CommandResult(
            returncode=124,
            stdout=str(exc.stdout or ""),
            stderr=f"Timed out after {timeout_seconds} seconds",
        )
    except Exception as exc:  # Keep the matrix report inspectable on probe crashes.
        result = CommandResult(returncode=1, stdout="", stderr=f"{type(exc).__name__}: {exc}")

    _write_text(stdout_path, result.stdout)
    _write_text(stderr_path, result.stderr)
    payload = _extract_json(result.stdout)
    payload_status = str(payload.get("status") or "")

    status = "pass" if result.returncode == 0 else "fail"
    category = "" if status == "pass" else failure_category
    if result.returncode == 0 and payload_status == "deferred":
        status = "deferred"
    if payload_status == "external_blocker":
        status = "external_blocker"
        category = "cad_external_blocker"
    if strict_geometry and payload_status not in {"pass", "geometry_verified"}:
        status = "fail"
        category = "cad_geometry_not_verified"

    return {
        "id": step_id,
        "title": title,
        "status": status,
        "failure_category": category,
        "returncode": result.returncode,
        "command": command,
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "stdout_excerpt": result.stdout[-1200:],
        "stderr_excerpt": result.stderr[-1200:],
        "payload": payload,
    }


def _deferred_step(*, step_id: str, title: str, reason: str) -> dict[str, Any]:
    return {
        "id": step_id,
        "title": title,
        "status": "deferred",
        "failure_category": "",
        "returncode": None,
        "command": [],
        "stdout_path": "",
        "stderr_path": "",
        "stdout_excerpt": reason,
        "stderr_excerpt": "",
        "payload": {
            "status": "deferred",
            "geometry_verified": False,
            "deferred_reason": reason,
        },
    }


def _not_run_step(*, step_id: str, title: str, blocked_by: str) -> dict[str, Any]:
    message = f"Skipped because prerequisite step `{blocked_by}` did not pass."
    return {
        "id": step_id,
        "title": title,
        "status": "not_run",
        "failure_category": "",
        "returncode": None,
        "command": [],
        "stdout_path": "",
        "stderr_path": "",
        "stdout_excerpt": message,
        "stderr_excerpt": "",
        "blocked_by": blocked_by,
        "payload": {"status": "not_run", "blocked_by": blocked_by},
    }


def _geometry_verified_count(step: dict[str, Any]) -> int:
    payload = step.get("payload")
    if not isinstance(payload, dict):
        return 0
    if payload.get("status") == "geometry_verified" or payload.get("geometry_verified") is True:
        if isinstance(payload.get("verified_case_count"), int):
            return int(payload["verified_case_count"])
        return 1
    evidence_summary = payload.get("evidence_summary")
    if isinstance(evidence_summary, dict) and isinstance(evidence_summary.get("readback_geometry_verified_count"), int):
        return int(evidence_summary["readback_geometry_verified_count"])
    return 0


def _created_handle_count(step: dict[str, Any]) -> int:
    payload = step.get("payload")
    if not isinstance(payload, dict):
        return 0
    for key in ("created_handle_count",):
        value = payload.get(key)
        if isinstance(value, int):
            return value
    return 0


def _build_summary(
    steps: list[dict[str, Any]],
    *,
    include_cad: bool,
    selected_case_ids: list[str],
    manifest_case_count: int,
    strict: bool,
) -> dict[str, Any]:
    failed = [step for step in steps if step["status"] == "fail"]
    external = [step for step in steps if step["status"] == "external_blocker"]
    deferred = [step for step in steps if step["status"] == "deferred"]
    geometry_count = sum(_geometry_verified_count(step) for step in steps)
    return {
        "include_cad": include_cad,
        "strict": strict,
        "manifest_case_count": manifest_case_count,
        "selected_case_count": len(selected_case_ids),
        "selected_case_ids": selected_case_ids,
        "non_cad_only": geometry_count == 0,
        "step_count": len(steps),
        "failed_case_count": len(failed),
        "external_blocker_count": len(external),
        "deferred_case_count": len(deferred),
        "geometry_verified_case_count": geometry_count,
        "created_handle_count": sum(_created_handle_count(step) for step in steps),
    }


def _overall_status(summary: dict[str, Any]) -> str:
    if summary["failed_case_count"]:
        return "fail"
    if summary["external_blocker_count"]:
        return "external_blocker"
    return "pass"


def _markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Local CAD Regression Report",
        "",
        f"- status: `{report['status']}`",
        f"- include_cad: `{report['include_cad']}`",
        f"- require_cad_verified: `{report['require_cad_verified']}`",
        f"- output_dir: `{report['output_dir']}`",
        "",
        "## Matrix",
        "",
        "| step | status | category |",
        "| --- | --- | --- |",
    ]
    for step in report["steps"]:
        lines.append(f"| `{step['id']}` | `{step['status']}` | `{step['failure_category'] or '-'}` |")
    lines.append("")
    return "\n".join(lines)


