"""Visual review gate for a freshly drawn CAD run."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from core.path_safety import resolve_under_project_output, resolve_under_project_root
from core.verification.evidence_contract import (
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    SCREENSHOT_VISUAL_AID_ONLY,
    validate_created_handles_match,
    validate_readback_report_evidence,
)
from core.verification.render_preview import build_screenshot_decision, prepare_autocad_for_capture, visual_preview_payload


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")


def _load_json(path: Path, *, label: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not path.is_file():
        return None, {"name": label, "status": "fail", "message": f"missing file: {path}"}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, {"name": label, "status": "fail", "message": str(exc)}
    if not isinstance(payload, dict):
        return None, {"name": label, "status": "fail", "message": f"{label} must be a JSON object"}
    return payload, None


def _check(name: str, passed: bool, message: str) -> dict[str, str]:
    return {"name": name, "status": "pass" if passed else "fail", "message": message}


def _created_handles_from_readback(readback: dict[str, Any]) -> object:
    actual = readback.get("actual")
    if isinstance(actual, dict):
        return actual.get("created_handles")
    return readback.get("created_handles")


def _default_capture(output: Path, *, execution_summary: Path | None = None) -> dict[str, Any]:
    return prepare_autocad_for_capture(output, execution_summary=execution_summary)


def run_visual_cad_review(
    project_root: Path,
    *,
    output_dir: Path,
    execution_summary_path: Path | None = None,
    readback_report_path: Path | None = None,
    screenshot_path: Path | None = None,
    capture: bool = False,
    capture_func: Callable[[Path], dict[str, Any]] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    root = project_root.resolve()
    out_dir = resolve_under_project_output(root, output_dir, label="output_dir")
    out_dir.mkdir(parents=True, exist_ok=True)
    screenshot = resolve_under_project_root(
        root,
        screenshot_path or (out_dir / "cad-visual-review.png"),
        label="screenshot_path",
    )
    execution_file = (
        resolve_under_project_root(root, execution_summary_path, label="execution_summary_path")
        if execution_summary_path is not None
        else None
    )
    readback_file = (
        resolve_under_project_root(root, readback_report_path, label="readback_report_path")
        if readback_report_path is not None
        else None
    )

    checks: list[dict[str, Any]] = []
    screenshot_decision = build_screenshot_decision(
        task_kind="visual_review",
        evidence_stage="visual_review",
        execution_summary=execution_file,
        capture_requested=capture or screenshot_path is not None,
        formal_acceptance=True,
        agent_role="pipeline_audit",
    )
    capture_result: dict[str, Any] = {"status": "not_run"}
    if capture:
        try:
            capture_result = (
                capture_func(screenshot)
                if capture_func is not None
                else _default_capture(screenshot, execution_summary=execution_file)
            )
        except Exception as exc:
            capture_result = {
                "status": "failed",
                "failure_category": "screenshot_failed",
                "message": str(exc),
                "output": str(screenshot),
            }
    if not isinstance(capture_result.get("screenshotDecision"), dict):
        capture_result["screenshotDecision"] = screenshot_decision
    if capture_result.get("status") == "failed":
        checks.append(_check("capture_autocad_window", False, str(capture_result.get("message", "capture failed"))))

    screenshot_ok = screenshot.is_file() and screenshot.stat().st_size > 0
    checks.append(
        _check(
            "screenshot_available",
            screenshot_ok,
            f"screenshot exists: {screenshot}" if screenshot_ok else f"screenshot missing or empty: {screenshot}",
        )
    )

    execution_summary: dict[str, Any] = {}
    if execution_file is None:
        checks.append(_check("execution_summary_available", False, "execution summary path is required"))
    else:
        execution_summary, error = _load_json(execution_file, label="execution_summary_available")
        if error:
            checks.append(error)
            execution_summary = {}
        else:
            checks.append(_check("execution_summary_available", True, f"loaded {execution_file}"))

    readback_report: dict[str, Any] = {}
    if readback_file is None:
        checks.append(_check("readback_report_available", False, "readback report path is required"))
    else:
        readback_report, error = _load_json(readback_file, label="readback_report_available")
        if error:
            checks.append(error)
            readback_report = {}
        else:
            checks.append(_check("readback_report_available", True, f"loaded {readback_file}"))

    execution_handles = execution_summary.get("created_handles") if execution_summary else []
    readback_handles = _created_handles_from_readback(readback_report) if readback_report else []
    handle_match_error = validate_created_handles_match(
        expected_created_handles=execution_handles,
        actual_created_handles=readback_handles,
        label="visual_review",
    )
    checks.append(_check("created_handles_match", not handle_match_error, handle_match_error or "created handles match"))

    readback_validation = validate_readback_report_evidence(readback_report) if readback_report else "missing readback"
    readback_ok = not readback_validation and readback_report.get("evidence_state") == EVIDENCE_READBACK_GEOMETRY_VERIFIED
    checks.append(
        _check(
            "readback_geometry_verified",
            readback_ok,
            readback_validation or "readback report is geometry_verified",
        )
    )

    checks.append(
        _check(
            "screenshot_role_visual_aid_only",
            screenshot_ok,
            "screenshot is visual_aid_only and cannot replace CAD readback"
            if screenshot_ok
            else "visual review requires a screenshot checkpoint",
        )
    )

    failed = [check for check in checks if check.get("status") != "pass"]
    report: dict[str, Any] = {
        "version": "0.1",
        "report_id": "table-c-visual-cad-review",
        "status": "pass" if not failed else "fail",
        "generated_at": generated_at or _utc_now_iso(),
        "screenshot_path": _rel(screenshot, root),
        "execution_summary_path": _rel(execution_file, root) if execution_file else "",
        "readback_report_path": _rel(readback_file, root) if readback_file else "",
        "screenshot_role": SCREENSHOT_VISUAL_AID_ONLY if screenshot_ok else "not_applicable",
        "capture_result": capture_result,
        "screenshotDecision": capture_result.get("screenshotDecision", screenshot_decision),
        "visualPreview": visual_preview_payload(capture_result),
        "checks": checks,
        "writeback_allowed": not failed,
        "notes": [
            "Visual review is a hard gate for table C writeback in this workflow.",
            "Screenshots remain visual aids and do not prove geometry without readback.",
        ],
    }
    if failed:
        report["failure_category"] = "visual_review_failed"

    target = out_dir / "visual_review_report.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["output_path"] = _rel(target, root)
    return report
