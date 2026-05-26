"""Gate helpers for CAD validation reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.verification.evidence_contract import (
    normalize_created_handles,
    validate_capability_probe_evidence,
    validate_created_handles_match,
    validate_readback_report_evidence,
)


def created_handles_from_artifact(path: Path) -> list[str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(payload, dict):
        return []
    return normalize_created_handles(payload.get("created_handles"))


def readback_gate_failure(stdout: str, *, expected_created_handles: object | None = None) -> str:
    try:
        report = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return f"readback_report.json is not valid JSON: {exc}"
    if not isinstance(report, dict):
        return "readback_report.json must be a JSON object."

    readback_status = report.get("status")
    checks = report.get("checks", [])
    non_pass_checks = []
    if isinstance(checks, list):
        for check in checks:
            if not isinstance(check, dict):
                non_pass_checks.append("unknown:invalid_check")
                continue
            if check.get("status") != "pass":
                non_pass_checks.append(f"{check.get('name', 'unknown')}:{check.get('status', 'unknown')}")
    else:
        non_pass_checks.append("checks:missing_or_invalid")

    if readback_status != "geometry_verified" or non_pass_checks:
        details = ", ".join(non_pass_checks) if non_pass_checks else "all checks pass"
        return f"readback_report.status={readback_status!r}; expected 'geometry_verified'; non_pass_checks={details}"

    evidence_failure = validate_readback_report_evidence(report)
    if evidence_failure:
        return evidence_failure
    if expected_created_handles is not None:
        actual = report.get("actual", {}).get("created_handles") if isinstance(report.get("actual"), dict) else []
        handle_failure = validate_created_handles_match(
            expected_created_handles=expected_created_handles,
            actual_created_handles=actual,
            label="readback_report",
        )
        if handle_failure:
            return handle_failure
    return ""


def cad_capability_gate_failure(stdout: str) -> str:
    try:
        report = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return f"cad_capability_probe.json is not valid JSON: {exc}"
    if not isinstance(report, dict):
        return "cad_capability_probe.json must be a JSON object."

    probe_status = report.get("status")
    checks = report.get("checks", [])
    non_pass_checks = []
    if isinstance(checks, list):
        for check in checks:
            if not isinstance(check, dict):
                non_pass_checks.append("unknown:invalid_check")
                continue
            if check.get("status") != "pass":
                non_pass_checks.append(f"{check.get('name', 'unknown')}:{check.get('status', 'unknown')}")
    else:
        non_pass_checks.append("checks:missing_or_invalid")

    if probe_status != "cad_capability_verified" or non_pass_checks:
        details = ", ".join(non_pass_checks) if non_pass_checks else "all checks pass"
        return f"cad_capability_probe.status={probe_status!r}; expected 'cad_capability_verified'; non_pass_checks={details}"

    return validate_capability_probe_evidence(report)
