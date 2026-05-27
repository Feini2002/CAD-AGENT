"""Markdown and next-action helpers for CAD validation reports."""

from __future__ import annotations

from typing import Any

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


def _markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# CAD Autonomous Validation Report",
        "",
        f"- status: `{report['status']}`",
        f"- root: `{report['root']}`",
        f"- output_dir: `{report['output_dir']}`",
        f"- include_cad: `{report['include_cad']}`",
    ]
    if report.get("geometry_gate_mode"):
        geometry_gate = report.get("geometry_gate", {})
        infrastructure_gate = report.get("infrastructure_gate", {})
        lines.extend(
            [
                f"- geometry_gate_mode: `true`",
                f"- geometry_gate.status: `{geometry_gate.get('status', '')}`",
                f"- infrastructure_gate.status: `{infrastructure_gate.get('status', '')}`",
                f"- legacy_status: `{report.get('legacy_status', '')}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Steps",
            "",
            "| step | status | category |",
            "| --- | --- | --- |",
        ]
    )
    for step in report["steps"]:
        category = step["failure_category"] or "-"
        lines.append(f"| `{step['id']}` | `{step['status']}` | `{category}` |")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {action}" for action in report["next_actions"])
    lines.append("")
    return "\n".join(lines)


