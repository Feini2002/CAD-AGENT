"""Run autonomous CAD validation probes and write evidence reports."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


CommandRunner = Callable[[list[str], Path, int], CommandResult]


@dataclass(frozen=True)
class ValidationStep:
    id: str
    title: str
    command: list[str]
    failure_category: str
    required: bool = True
    timeout_seconds: int = 120
    cad_required: bool = False
    stdout_artifact: str | None = None


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


def _base_steps(root: Path) -> list[ValidationStep]:
    plan = str(root / "examples" / "plans" / "draw_test_cabinet.json")
    benchmark = str(root / "examples" / "benchmarks" / "non_cad_core_benchmark.json")
    benchmark_output = str(root / "output" / "test_artifacts" / "benchmarks" / "cad_validation")
    return [
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


def _cad_steps(root: Path, output_dir: Path) -> list[ValidationStep]:
    plan = str(root / "examples" / "plans" / "draw_test_cabinet.json")
    screenshot = str(output_dir / "cad-validation-screen.png")
    execution_summary = str(output_dir / "execution_summary.json")
    return [
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
            "Capture CAD visual checkpoint",
            [_python(), "scripts/render_preview.py", "--capture-screen", "--output", screenshot],
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
    ]


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _step_record(step: ValidationStep, result: CommandResult, output_dir: Path) -> dict[str, Any]:
    safe_id = step.id.replace("/", "_")
    stdout_path = output_dir / f"{safe_id}.stdout.txt"
    stderr_path = output_dir / f"{safe_id}.stderr.txt"
    _write_text(stdout_path, result.stdout)
    _write_text(stderr_path, result.stderr)
    if step.stdout_artifact and result.stdout:
        _write_text(Path(step.stdout_artifact), result.stdout)

    status = "pass" if result.returncode == 0 else "fail"
    return {
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
        "stdout_excerpt": result.stdout[-1200:],
        "stderr_excerpt": result.stderr[-1200:],
    }


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
    return actions


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
    command_runner: CommandRunner = default_command_runner,
) -> dict[str, Any]:
    project_root = root.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    steps = _base_steps(project_root)
    if include_cad:
        steps.extend(_cad_steps(project_root, output_dir))

    records: list[dict[str, Any]] = []
    for step in steps:
        try:
            result = command_runner(step.command, project_root, step.timeout_seconds)
        except subprocess.TimeoutExpired as exc:
            result = CommandResult(returncode=124, stdout=str(exc.stdout or ""), stderr=f"Timed out after {step.timeout_seconds} seconds")
        except Exception as exc:  # Keep the report useful even when a probe crashes.
            result = CommandResult(returncode=1, stdout="", stderr=f"{type(exc).__name__}: {exc}")
        record = _step_record(step, result, output_dir)
        records.append(record)

    report: dict[str, Any] = {
        "status": _overall_status(records),
        "root": str(project_root),
        "output_dir": str(output_dir),
        "include_cad": include_cad,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "steps": records,
    }
    report["next_actions"] = _next_actions(report)

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
    args = parser.parse_args()

    root = args.root.resolve()
    output_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    report = run_cad_validation(root=root, output_dir=output_dir, include_cad=not args.no_cad)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] == "pass":
        return 0
    if report["status"] == "external_blocker":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
