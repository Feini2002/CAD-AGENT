"""Local CAD regression matrix for CODEX_PREVIEW readback checks."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from core.path_safety import resolve_under_project_output
from core.verification.cad_validation_types import CommandResult, CommandRunner
from core.verification.local_cad_regression_manifest import (
    DEFAULT_MANIFEST_RELATIVE_PATH,
    PREVIEW_LAYER,
    load_regression_manifest,
    manifest_case_ids,
    manifest_summary,
    select_manifest_case_ids,
)


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


def run_local_cad_regression(
    *,
    root: Path,
    output_dir: Path,
    include_cad: bool,
    require_cad_verified: bool = False,
    manifest_path: Path | None = None,
    selected_case_ids: list[str] | None = None,
    command_runner: CommandRunner = default_command_runner,
) -> dict[str, Any]:
    """Run a local CAD regression matrix and aggregate machine-readable evidence."""

    project_root = root.resolve()
    resolved_manifest_path = manifest_path or project_root / DEFAULT_MANIFEST_RELATIVE_PATH
    if not resolved_manifest_path.is_absolute():
        resolved_manifest_path = project_root / resolved_manifest_path
    manifest = load_regression_manifest(resolved_manifest_path)
    active_case_ids = select_manifest_case_ids(manifest, selected_case_ids)

    output_dir = resolve_under_project_output(project_root, output_dir, label="output_dir")
    output_dir.mkdir(parents=True, exist_ok=True)

    baseline_dir = output_dir / "baseline_cad_validation"
    baseline_command = [
        _python(),
        "scripts/run_cad_validation.py",
        "--output-dir",
        str(baseline_dir),
    ]
    if not include_cad:
        baseline_command.append("--no-cad")

    steps: list[dict[str, Any]] = []

    if "baseline_cad_validation" in active_case_ids:
        steps.append(
            _run_step(
                step_id="baseline_cad_validation",
                title="Baseline CAD validation runner",
                command=baseline_command,
                output_dir=output_dir,
                root=project_root,
                command_runner=command_runner,
                failure_category="baseline_cad_validation_failed",
            )
        )

    project_sample_command = [
        _python(),
        "scripts/run_project_sample_cad_check.py",
        "--workflow-output-dir",
        str(output_dir / "project_sample_workflow"),
        "--output-dir",
        str(output_dir / "project_sample_cad"),
        "--start-x",
        "34000",
        "--start-y",
        "18000",
    ]
    if include_cad:
        if require_cad_verified:
            project_sample_command.append("--require-cad-verified")
    else:
        project_sample_command.append("--no-cad")

    if "project_sample_cad_check" in active_case_ids:
        steps.append(
            _run_step(
                step_id="project_sample_cad_check",
                title="Project sample CODEX_PREVIEW CAD check",
                command=project_sample_command,
                output_dir=output_dir,
                root=project_root,
                command_runner=command_runner,
                failure_category="cad_geometry_not_verified",
                strict_geometry=include_cad and require_cad_verified,
            )
        )

    if "composition_cad_check" in active_case_ids:
        if include_cad:
            benchmark_output = output_dir / "interior_delivery_benchmark"
            steps.append(
                _run_step(
                    step_id="interior_delivery_benchmark",
                    title="Prepare interior delivery CAD_PLAN artifacts",
                    command=[
                        _python(),
                        "scripts/run_benchmark_suite.py",
                        "examples/benchmarks/interior_delivery_benchmark.json",
                        "--output-root",
                        str(benchmark_output),
                    ],
                    output_dir=output_dir,
                    root=project_root,
                    command_runner=command_runner,
                    failure_category="benchmark_failed",
                )
            )
            if steps[-1]["status"] == "pass":
                steps.append(
                    _run_step(
                        step_id="composition_cad_check",
                        title="Interior composition CODEX_PREVIEW CAD batch check",
                        command=[
                            _python(),
                            "scripts/run_composition_cad_check.py",
                            "--benchmark-output-root",
                            str(benchmark_output),
                            "--output-dir",
                            str(output_dir / "composition_cad"),
                            "--start-x",
                            "38000",
                            "--start-y",
                            "22000",
                            "--spacing-x",
                            "4200",
                        ],
                        output_dir=output_dir,
                        root=project_root,
                        command_runner=command_runner,
                        failure_category="cad_geometry_not_verified",
                        strict_geometry=require_cad_verified,
                    )
                )
            else:
                steps.append(
                    _not_run_step(
                        step_id="composition_cad_check",
                        title="Interior composition CODEX_PREVIEW CAD batch check",
                        blocked_by="interior_delivery_benchmark",
                    )
                )
        else:
            steps.append(
                _deferred_step(
                    step_id="composition_cad_check",
                    title="Interior composition CODEX_PREVIEW CAD batch check",
                    reason="real CAD batch readback is intentionally skipped in --no-cad mode",
                )
            )

    if "primitive_matrix_no_cad" in active_case_ids:
        primitive_command = [
            _python(),
            "scripts/run_primitive_matrix.py",
            "--output-dir",
            str(output_dir / "primitive_matrix"),
        ]
        if not include_cad:
            primitive_command.append("--no-cad")
        steps.append(
            _run_step(
                step_id="primitive_matrix_no_cad",
                title="Primitive capability matrix (no-CAD)",
                command=primitive_command,
                output_dir=output_dir,
                root=project_root,
                command_runner=command_runner,
                failure_category="primitive_matrix_failed",
                strict_geometry=include_cad and require_cad_verified,
            )
        )

    if "cad_plan_fixture_suite_no_cad" in active_case_ids:
        fixture_no_cad_command = [
            _python(),
            "scripts/run_cad_plan_fixture_suite.py",
            "--no-cad",
            "--output-dir",
            str(output_dir / "cad_plan_fixture_suite"),
        ]
        steps.append(
            _run_step(
                step_id="cad_plan_fixture_suite_no_cad",
                title="CAD_PLAN fixture suite validate and dry-run",
                command=fixture_no_cad_command,
                output_dir=output_dir,
                root=project_root,
                command_runner=command_runner,
                failure_category="cad_plan_fixture_suite_failed",
            )
        )

    if "cad_plan_fixture_suite_cad" in active_case_ids:
        if include_cad:
            fixture_cad_command = [
                _python(),
                "scripts/run_cad_plan_fixture_suite.py",
                "--output-dir",
                str(output_dir / "cad_plan_fixture_suite_cad"),
            ]
            steps.append(
                _run_step(
                    step_id="cad_plan_fixture_suite_cad",
                    title="CAD_PLAN fixture suite CODEX_PREVIEW execution",
                    command=fixture_cad_command,
                    output_dir=output_dir,
                    root=project_root,
                    command_runner=command_runner,
                    failure_category="cad_geometry_not_verified",
                    strict_geometry=require_cad_verified,
                )
            )
        else:
            steps.append(
                _deferred_step(
                    step_id="cad_plan_fixture_suite_cad",
                    title="CAD_PLAN fixture suite CODEX_PREVIEW execution",
                    reason="real CAD fixture execution is intentionally skipped in --no-cad mode",
                )
            )

    if "complex_cad_smoke" in active_case_ids:
        complex_command = [
            _python(),
            "scripts/run_complex_cad_smoke.py",
            "--output-dir",
            str(output_dir / "complex_cad_smoke"),
        ]
        if not include_cad:
            complex_command.append("--no-cad")
        steps.append(
            _run_step(
                step_id="complex_cad_smoke",
                title="Complex mixed-primitive CODEX_PREVIEW CAD smoke",
                command=complex_command,
                output_dir=output_dir,
                root=project_root,
                command_runner=command_runner,
                failure_category="cad_geometry_not_verified",
                strict_geometry=include_cad and require_cad_verified,
            )
        )

    summary = _build_summary(
        steps,
        include_cad=include_cad,
        selected_case_ids=active_case_ids,
        manifest_case_count=len(manifest_case_ids(manifest)),
        strict=require_cad_verified,
    )
    report = {
        "version": "0.1",
        "status": _overall_status(summary),
        "root": str(project_root),
        "output_dir": str(output_dir),
        "include_cad": include_cad,
        "require_cad_verified": require_cad_verified,
        "selected_case_ids": active_case_ids,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "manifest": manifest_summary(manifest),
        "safety": {
            "layer": PREVIEW_LAYER,
            "saved_dwg": False,
            "deleted_entities": False,
            "modified_formal_layers": False,
        },
        "summary": summary,
        "steps": steps,
    }
    _write_text(output_dir / "local_cad_regression_report.json", json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    _write_text(output_dir / "local_cad_regression_report.md", _markdown_report(report))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local CAD regression matrix for CODEX_PREVIEW checks.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output") / "validation_runs" / "local-cad-regression",
    )
    parser.add_argument("--no-cad", action="store_true", help="Run safe deferred matrix without connecting to AutoCAD.")
    parser.add_argument(
        "--require-cad-verified",
        action="store_true",
        help="Return non-zero unless real CAD checks produce geometry_verified evidence.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Alias for --require-cad-verified.",
    )
    parser.add_argument(
        "--case",
        dest="selected_case_ids",
        action="append",
        default=None,
        help="Run only a selected manifest case id. Repeat to run multiple cases. Default runs all manifest cases.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Optional local CAD regression manifest path. Relative paths are resolved under --root.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    output_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    require_cad_verified = args.require_cad_verified or args.strict
    report = run_local_cad_regression(
        root=root,
        output_dir=output_dir,
        include_cad=not args.no_cad,
        require_cad_verified=require_cad_verified,
        manifest_path=args.manifest,
        selected_case_ids=args.selected_case_ids,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] == "pass":
        return 0
    if report["status"] == "external_blocker":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
