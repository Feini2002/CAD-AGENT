"""Block alpha steps and gates for the CAD validation runner."""

from __future__ import annotations

import json
from pathlib import Path

from core.verification.block_alpha_validation import validate_block_alpha_report_evidence
from core.verification.cad_validation_types import ValidationStep


def block_alpha_plan(root: Path) -> str:
    return str(root / "examples" / "plans" / "insert_block_alpha_test.json")


def block_alpha_base_steps(
    root: Path,
    output_dir: Path,
    *,
    include_cad: bool,
    python_executable: str,
) -> list[ValidationStep]:
    plan = block_alpha_plan(root)
    steps = [
        ValidationStep(
            "block_alpha_validate_plan",
            "Validate insert_block_alpha CAD_PLAN",
            [python_executable, "scripts/validate_plan.py", plan],
            "block_alpha_plan_invalid",
        ),
        ValidationStep(
            "block_alpha_dry_run",
            "Dry-run insert_block_alpha CAD_PLAN",
            [python_executable, "scripts/dry_run_plan.py", plan],
            "block_alpha_dry_run_failed",
        ),
    ]
    if not include_cad:
        steps.append(
            ValidationStep(
                "block_alpha_deferred_evidence",
                "Record deferred block alpha evidence (no CAD)",
                [
                    python_executable,
                    "scripts/run_block_alpha_validation.py",
                    "--no-cad",
                    "--output-dir",
                    str(output_dir),
                ],
                "block_alpha_failed",
                stdout_artifact=str(output_dir / "block_alpha_report.json"),
            )
        )
    return steps


def block_alpha_cad_steps(
    root: Path,
    output_dir: Path,
    *,
    python_executable: str,
    include_connect: bool = True,
) -> list[ValidationStep]:
    block_plan = block_alpha_plan(root)
    block_execution_summary = str(output_dir / "block_alpha_execution_summary.json")
    block_screenshot = str(output_dir / "block-alpha-window.png")
    steps: list[ValidationStep] = []
    if include_connect:
        steps.append(
            ValidationStep(
                "autocad_com_connect",
                "Connect to active AutoCAD document",
                [
                    python_executable,
                    "-c",
                    "from core.cad_io.autocad_com import AutoCADComDriver; d=AutoCADComDriver(connect_existing_only=True); print('COM OK:', d.doc.Name)",
                ],
                "cad_connection_failed",
                cad_required=True,
            )
        )
    steps.extend(
        [
            ValidationStep(
                "block_alpha_execute",
                "Execute insert_block_alpha CAD_PLAN into CODEX_PREVIEW",
                [python_executable, "scripts/execute_plan.py", block_plan],
                "block_alpha_execution_failed",
                cad_required=True,
                stdout_artifact=block_execution_summary,
            ),
            ValidationStep(
                "block_alpha_capture_screen",
                "Capture AutoCAD window visual aid for block alpha",
                [
                    python_executable,
                    "scripts/render_preview.py",
                    "--capture-autocad-window",
                    "--execution-summary",
                    block_execution_summary,
                    "--output",
                    block_screenshot,
                ],
                "screenshot_failed",
                cad_required=True,
            ),
            ValidationStep(
                "block_alpha_readback",
                "Inspect block_reference readback for insert_block_alpha",
                [
                    python_executable,
                    "scripts/run_block_alpha_validation.py",
                    "--connect-cad",
                    "--output-dir",
                    str(output_dir),
                    "--plan",
                    block_plan,
                    "--execution-summary",
                    block_execution_summary,
                ],
                "block_alpha_readback_failed",
                cad_required=True,
                stdout_artifact=str(output_dir / "block_alpha_report.json"),
            ),
        ]
    )
    return steps


def block_alpha_gate_failure(
    stdout: str,
    *,
    no_cad: bool,
    expected_created_handles: object | None = None,
) -> str:
    try:
        report = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return f"block_alpha_report.json is not valid JSON: {exc}"
    if not isinstance(report, dict):
        return "block_alpha_report.json must be a JSON object."

    evidence_failure = validate_block_alpha_report_evidence(report, no_cad=no_cad)
    if evidence_failure:
        return evidence_failure

    if no_cad:
        return ""

    if expected_created_handles is not None:
        from core.verification.evidence_contract import validate_created_handles_match

        handle_failure = validate_created_handles_match(
            expected_created_handles=expected_created_handles,
            actual_created_handles=report.get("created_handles"),
            label="block_alpha_report",
        )
        if handle_failure:
            return handle_failure

    status = report.get("status")
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

    if status != "geometry_verified" or non_pass_checks:
        details = ", ".join(non_pass_checks) if non_pass_checks else "all checks pass"
        return (
            f"block_alpha_report.status={status!r}; expected 'geometry_verified' on CAD runs; "
            f"non_pass_checks={details}"
        )
    return ""
