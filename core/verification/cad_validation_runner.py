"""Run autonomous CAD validation probes and write evidence reports."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from core.verification.block_alpha_validation import (
    summarize_block_alpha_from_steps,
)
from core.verification.cad_validation_block_alpha import (
    block_alpha_base_steps,
    block_alpha_cad_steps,
    block_alpha_gate_failure,
)
from core.verification.cad_validation_gates import (
    cad_capability_gate_failure,
    created_handles_from_artifact,
    readback_gate_failure,
)
from core.verification.preview_only_audit import execution_summary_gate_failure
from core.verification.cad_validation_evidence import (
    apply_screenshot_step_evidence,
    build_cad_validation_evidence_summary,
    cad_validation_evidence_gate_failure,
    validate_step_evidence_fields,
)
from core.verification.cad_validation_types import CommandResult, CommandRunner, ValidationStep
from core.path_safety import is_relative_to, resolve_under_project_output

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


def _resolve_output_dir(project_root: Path, output_dir: Path) -> Path:
    return resolve_under_project_output(project_root, output_dir, label="output_dir")


def _resolve_derived_artifact(path: Path, output_dir: Path) -> Path:
    resolved_output = output_dir.resolve()
    resolved = path.resolve()
    if not is_relative_to(resolved, resolved_output):
        raise ValueError(f"derived artifact must stay under output_dir: {path}")
    return resolved


def _base_steps(root: Path, output_dir: Path, *, include_cad: bool) -> list[ValidationStep]:
    plan = str(root / "examples" / "plans" / "draw_test_cabinet.json")
    benchmark = str(root / "examples" / "benchmarks" / "non_cad_core_benchmark.json")
    benchmark_output = str(root / "output" / "test_artifacts" / "benchmarks" / "cad_validation")
    steps = [
        ValidationStep("python_import_pillow", "Import Pillow", [_python(), "-c", "import PIL; print(PIL.__version__)"], "missing_dependency"),
        ValidationStep("python_import_pywin32", "Import pywin32", [_python(), "-c", "import win32com.client; print('pywin32 OK')"], "missing_dependency"),
        ValidationStep("python_import_win32gui", "Import win32gui", [_python(), "-c", "import win32gui; print('win32gui OK')"], "missing_dependency"),
        ValidationStep("self_check", "Run repository self check", [_python(), "scripts/self_check.py"], "repo_regression"),
        ValidationStep("unit_tests", "Run unit tests", [_python(), "-m", "unittest", "discover", "-s", "tests"], "repo_regression", timeout_seconds=300),
        ValidationStep("validate_sample_plan", "Validate baseline CAD_PLAN", [_python(), "scripts/validate_plan.py", plan], "cad_plan_invalid"),
        ValidationStep("dry_run_sample_plan", "Dry-run baseline CAD_PLAN", [_python(), "scripts/dry_run_plan.py", plan], "dry_run_failed"),
        ValidationStep("render_preview_check", "Check screenshot capability", [_python(), "scripts/render_preview.py", "--check"], "screenshot_failed"),
        ValidationStep(
            "non_cad_benchmark",
            "Run non-CAD benchmark",
            [_python(), "scripts/run_benchmark_suite.py", benchmark, "--output-root", benchmark_output],
            "repo_regression",
            timeout_seconds=300,
        ),
    ]
    steps.extend(block_alpha_base_steps(root, output_dir, include_cad=include_cad, python_executable=_python()))
    return steps


def _cad_steps(root: Path, output_dir: Path) -> list[ValidationStep]:
    plan = str(root / "examples" / "plans" / "draw_test_cabinet.json")
    screenshot = str(output_dir / "cad-validation-window.png")
    execution_summary = str(output_dir / "execution_summary.json")
    capability_report = str(output_dir / "cad_capability_probe.json")
    steps = [
        ValidationStep(
            "autocad_com_connect",
            "Connect to active AutoCAD document",
            [
                _python(),
                "-c",
                "from core.cad_io.autocad_com import AutoCADComDriver; d=AutoCADComDriver(connect_existing_only=True); print('COM OK:', d.doc.Name)",
            ],
            "cad_connection_failed",
            cad_required=True,
        ),
        ValidationStep(
            "execute_sample_plan",
            "Execute baseline CAD_PLAN into CODEX_PREVIEW",
            [_python(), "scripts/execute_plan.py", plan],
            "execution_failed",
            cad_required=True,
            stdout_artifact=execution_summary,
        ),
        ValidationStep(
            "capture_screen",
            "Capture CAD window visual checkpoint",
            [
                _python(),
                "scripts/render_preview.py",
                "--capture-autocad-window",
                "--execution-summary",
                execution_summary,
                "--output",
                screenshot,
            ],
            "screenshot_failed",
            cad_required=True,
        ),
        ValidationStep(
            "inspect_readback",
            "Inspect CAD entities and build verification report",
            [
                _python(),
                "scripts/inspect_dwg.py",
                "--connect-cad",
                "--plan",
                plan,
                "--format",
                "json",
                "--execution-summary",
                execution_summary,
                "--screenshot",
                screenshot,
            ],
            "readback_failed",
            cad_required=True,
            stdout_artifact=str(output_dir / "readback_report.json"),
        ),
        ValidationStep(
            "cad_capability_probe",
            "Probe AutoCAD COM primitive write and handle readback capability",
            [_python(), "scripts/run_cad_capability_probe.py", "--output-dir", str(output_dir)],
            "cad_capability_failed",
            cad_required=True,
            stdout_artifact=capability_report,
        ),
    ]
    steps.extend(block_alpha_cad_steps(root, output_dir, python_executable=_python(), include_connect=False))
    return steps


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _step_record(step: ValidationStep, result: CommandResult, output_dir: Path) -> dict[str, Any]:
    safe_id = step.id.replace("/", "_")
    stdout_path = output_dir / f"{safe_id}.stdout.txt"
    stderr_path = output_dir / f"{safe_id}.stderr.txt"
    stdout = result.stdout
    stderr = result.stderr

    status = "pass" if result.returncode == 0 else "fail"
    if status == "pass" and step.id == "execute_sample_plan":
        gate_failure = execution_summary_gate_failure(
            stdout=stdout,
            path=Path(step.stdout_artifact) if step.stdout_artifact else output_dir / "execution_summary.json",
        )
        if gate_failure:
            status = "fail"
            stderr = f"{stderr.rstrip()}\n{gate_failure}\n" if stderr else f"{gate_failure}\n"
    if status == "pass" and step.id == "inspect_readback":
        gate_failure = readback_gate_failure(
            stdout,
            expected_created_handles=created_handles_from_artifact(output_dir / "execution_summary.json"),
        )
        if gate_failure:
            status = "fail"
            stderr = f"{stderr.rstrip()}\n{gate_failure}\n" if stderr else f"{gate_failure}\n"
    if status == "pass" and step.id == "cad_capability_probe":
        gate_failure = cad_capability_gate_failure(stdout)
        if gate_failure:
            status = "fail"
            stderr = f"{stderr.rstrip()}\n{gate_failure}\n" if stderr else f"{gate_failure}\n"
    if status == "pass" and step.id == "block_alpha_deferred_evidence":
        gate_failure = block_alpha_gate_failure(stdout, no_cad=True)
        if gate_failure:
            status = "fail"
            stderr = f"{stderr.rstrip()}\n{gate_failure}\n" if stderr else f"{gate_failure}\n"
    if status == "pass" and step.id == "block_alpha_readback":
        gate_failure = block_alpha_gate_failure(
            stdout,
            no_cad=False,
            expected_created_handles=created_handles_from_artifact(output_dir / "block_alpha_execution_summary.json"),
        )
        if gate_failure:
            status = "fail"
            stderr = f"{stderr.rstrip()}\n{gate_failure}\n" if stderr else f"{gate_failure}\n"

    _write_text(stdout_path, stdout)
    _write_text(stderr_path, stderr)
    if step.stdout_artifact and result.stdout:
        _write_text(Path(step.stdout_artifact), stdout)

    record = {
        "id": step.id,
        "title": step.title,
        "status": status,
        "failure_category": "" if status == "pass" else step.failure_category,
        "required": step.required,
        "cad_required": step.cad_required,
        "returncode": result.returncode,
        "command": step.command,
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "stdout_excerpt": stdout[-1200:],
        "stderr_excerpt": stderr[-1200:],
    }
    apply_screenshot_step_evidence(record, step.id)
    if step.id in {"inspect_readback", "cad_capability_probe", "block_alpha_deferred_evidence", "block_alpha_readback"} and stdout:
        try:
            payload = json.loads(stdout)
            if isinstance(payload, dict):
                for field in ("evidence_state", "geometry_accuracy", "screenshot_role"):
                    value = payload.get(field)
                    if isinstance(value, str) and value:
                        record[field] = value
        except json.JSONDecodeError:
            pass
    evidence_error = validate_step_evidence_fields(record, step_id=step.id)
    if evidence_error and status == "pass":
        status = "fail"
        stderr = f"{stderr.rstrip()}\n{evidence_error}\n" if stderr else f"{evidence_error}\n"
        record["status"] = status
        record["failure_category"] = record["failure_category"] or "cad_capability_failed"
    return record


def _skipped_step_record(step: ValidationStep, output_dir: Path, *, blocked_by: str) -> dict[str, Any]:
    safe_id = step.id.replace("/", "_")
    stdout_path = output_dir / f"{safe_id}.stdout.txt"
    stderr_path = output_dir / f"{safe_id}.stderr.txt"
    message = f"Skipped because prerequisite step `{blocked_by}` did not pass.\n"
    _write_text(stdout_path, message)
    _write_text(stderr_path, "")
    record = {
        "id": step.id,
        "title": step.title,
        "status": "not_run",
        "failure_category": "",
        "required": step.required,
        "cad_required": step.cad_required,
        "returncode": None,
        "command": step.command,
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "stdout_excerpt": message,
        "stderr_excerpt": "",
        "blocked_by": blocked_by,
    }
    apply_screenshot_step_evidence(record, step.id)
    return record


def _overall_status(records: list[dict[str, Any]]) -> str:
    failed = [record for record in records if record["status"] == "fail" and record["required"]]
    if not failed:
        return "pass"
    external_categories = {"cad_connection_failed", "missing_dependency", "screenshot_failed"}
    if all(record["failure_category"] in external_categories for record in failed):
        return "external_blocker"
    return "fail"


def _next_actions(report: dict[str, Any]) -> list[str]:
    failed = [step for step in report["steps"] if step["status"] == "fail"]
    if not failed:
        return ["全部验证步骤通过。可以继续执行计划中的下一阶段。"]

    actions: list[str] = []
    categories = {step["failure_category"] for step in failed}
    if "missing_dependency" in categories:
        actions.append("修复 CAD-MCP Python 环境缺失依赖，例如 Pillow、pywin32 或 win32gui，然后重新运行本脚本。")
    if "cad_connection_failed" in categories:
        actions.append("打开 AutoCAD 和一张测试 DWG，确认没有授权弹窗阻塞，再重新运行本脚本。")
    if "repo_regression" in categories:
        actions.append("仓库测试或自检失败。Codex 应先做最小复现和最小修复，再重新运行本脚本。")
    if "cad_plan_invalid" in categories or "dry_run_failed" in categories:
        actions.append("CAD_PLAN 校验或 dry-run 失败。Codex 应修计划生成或 schema 逻辑后复验。")
    if "execution_failed" in categories:
        actions.append("CAD 执行失败。Codex 应检查执行器、driver 和安全策略，修复后重新落图。")
    if "screenshot_failed" in categories:
        actions.append("截图失败。确认桌面会话可截图，或修复 `render_preview.py` 截图入口。")
    if "readback_failed" in categories:
        actions.append("实体回读失败。Codex 应检查 `inspect_dwg.py`、created handles 和 AutoCAD COM 回读逻辑。")
    if "cad_capability_failed" in categories:
        actions.append("CAD COM 能力探针失败。Codex 应检查 driver primitive write、handle readback、实体标准化和安全层约束。")
    if "block_alpha_failed" in categories or "block_alpha_readback_failed" in categories:
        actions.append("受控块 alpha 证据失败。检查 insert_block_alpha validate/dry-run、COM 插入与 block_reference readback 报告字段。")
    if "block_alpha_execution_failed" in categories:
        actions.append("insert_block_alpha 执行失败。检查 AutoCADComDriver.insert_block_alpha 与受控块定义策略。")
    return actions


def _clear_stale_derived_artifacts(steps: list[ValidationStep], output_dir: Path) -> None:
    paths = [Path(step.stdout_artifact) for step in steps if step.stdout_artifact]
    paths.append(output_dir / "cad-validation-screen.png")
    paths.append(output_dir / "cad-validation-window.png")
    paths.append(output_dir / "block_alpha_report.json")
    paths.append(output_dir / "block_alpha_execution_summary.json")
    for raw_path in paths:
        path = _resolve_derived_artifact(raw_path, output_dir)
        if path.exists():
            if not path.is_file():
                raise ValueError(f"derived artifact is not a file: {path}")
            path.unlink()


def _markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# CAD Autonomous Validation Report",
        "",
        f"- status: `{report['status']}`",
        f"- root: `{report['root']}`",
        f"- output_dir: `{report['output_dir']}`",
        f"- include_cad: `{report['include_cad']}`",
        "",
        "## Steps",
        "",
        "| step | status | category |",
        "| --- | --- | --- |",
    ]
    for step in report["steps"]:
        category = step["failure_category"] or "-"
        lines.append(f"| `{step['id']}` | `{step['status']}` | `{category}` |")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {action}" for action in report["next_actions"])
    lines.append("")
    return "\n".join(lines)


def run_cad_validation(
    *,
    root: Path,
    output_dir: Path,
    include_cad: bool,
    block_alpha_only: bool = False,
    command_runner: CommandRunner = default_command_runner,
) -> dict[str, Any]:
    project_root = root.resolve()
    output_dir = _resolve_output_dir(project_root, output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if block_alpha_only:
        steps = block_alpha_base_steps(project_root, output_dir, include_cad=include_cad, python_executable=_python())
        if include_cad:
            steps.extend(block_alpha_cad_steps(project_root, output_dir, python_executable=_python()))
    else:
        steps = _base_steps(project_root, output_dir, include_cad=include_cad)
        if include_cad:
            steps.extend(_cad_steps(project_root, output_dir))
    _clear_stale_derived_artifacts(steps, output_dir)

    records: list[dict[str, Any]] = []
    blocked_cad_step: str | None = None
    for step in steps:
        if step.cad_required and blocked_cad_step:
            records.append(_skipped_step_record(step, output_dir, blocked_by=blocked_cad_step))
            continue
        try:
            result = command_runner(step.command, project_root, step.timeout_seconds)
        except subprocess.TimeoutExpired as exc:
            result = CommandResult(returncode=124, stdout=str(exc.stdout or ""), stderr=f"Timed out after {step.timeout_seconds} seconds")
        except Exception as exc:  # Keep the report useful even when a probe crashes.
            result = CommandResult(returncode=1, stdout="", stderr=f"{type(exc).__name__}: {exc}")
        record = _step_record(step, result, output_dir)
        records.append(record)
        if record["status"] == "fail" and step.id in {"autocad_com_connect", "execute_sample_plan", "block_alpha_execute"}:
            blocked_cad_step = step.id

    report: dict[str, Any] = {
        "status": _overall_status(records),
        "root": str(project_root),
        "output_dir": str(output_dir),
        "include_cad": include_cad,
        "block_alpha_only": block_alpha_only,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "steps": records,
    }
    report["next_actions"] = _next_actions(report)
    report["block_alpha"] = summarize_block_alpha_from_steps(records)
    report["evidence_summary"] = build_cad_validation_evidence_summary(records, include_cad=include_cad)
    evidence_gate_failure = cad_validation_evidence_gate_failure(report)
    if evidence_gate_failure and report["status"] == "pass":
        report["status"] = "fail"
        report["evidence_gate_failure"] = evidence_gate_failure
        report["next_actions"] = [evidence_gate_failure, *report["next_actions"]]

    _write_text(output_dir / "report.json", json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    _write_text(output_dir / "report.md", _markdown_report(report))
    return report


def run_validation(
    *,
    output_dir: Path,
    include_cad: bool,
    runner: Callable[[list[str], Path], CommandResult] | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    """Compatibility wrapper for validation callers that do not need timeouts."""

    project_root = (root or Path(__file__).resolve().parents[2]).resolve()
    resolved_output_dir = output_dir if output_dir.is_absolute() else project_root / output_dir
    command_runner: CommandRunner
    if runner is None:
        command_runner = default_command_runner
    else:
        command_runner = lambda command, cwd, timeout_seconds: runner(command, cwd)
    return run_cad_validation(
        root=project_root,
        output_dir=resolved_output_dir,
        include_cad=include_cad,
        block_alpha_only=False,
        command_runner=command_runner,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run autonomous CAD Agent validation.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output") / "validation_runs" / datetime.now().strftime("%Y%m%d-%H%M%S"),
    )
    parser.add_argument("--no-cad", action="store_true", help="Run only non-CAD probes.")
    parser.add_argument(
        "--block-alpha-only",
        action="store_true",
        help="Run only insert_block_alpha validate/dry-run and CAD block alpha steps.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    output_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    report = run_cad_validation(
        root=root,
        output_dir=output_dir,
        include_cad=not args.no_cad,
        block_alpha_only=args.block_alpha_only,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] == "pass":
        return 0
    if report["status"] == "external_blocker":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
