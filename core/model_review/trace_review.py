"""Deterministic trace reviewer for model-backed agent calls.

The reviewer reads the trace files produced by the Codex CLI bridge and writes
a compact machine-readable verdict plus a human-facing summary. It does not call
models and does not replace schema validation, CAD readback, or A-to-A gates.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PASS_STATUSES = {"pass", "ready", "ok", "schema_valid"}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"_readError": str(exc)}
    return value if isinstance(value, dict) else {"_readError": "JSON value was not an object"}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _status_label(ok: bool) -> str:
    return "可用" if ok else "不可用"


def _text_items(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return [str(value)] if str(value) else []


def _collect_blocking_reasons(
    *,
    provider_status: dict[str, Any],
    gate_decision: dict[str, Any],
    normalized_output: dict[str, Any],
) -> list[str]:
    reasons: list[str] = []
    if provider_status.get("modelInvoked") is not True:
        reasons.append("modelInvoked is not true")
    if provider_status.get("modelUnavailable") is True:
        reasons.append("modelUnavailable is true")
    if provider_status.get("schemaValid") is not True:
        reasons.append("schemaValid is not true")
    gate_status = str(gate_decision.get("status") or "").casefold()
    if gate_status not in PASS_STATUSES:
        reasons.append(f"gate decision is {gate_status or 'missing'}")
    for key in ("reason", "stderr"):
        value = normalized_output.get(key)
        if value:
            reasons.append(str(value))
            break
    for item in _text_items(gate_decision.get("blockingReasons")):
        text = str(item)
        if text and text not in reasons:
            reasons.append(text)
    return reasons


def build_trace_review(trace_dir: Path) -> dict[str, Any]:
    """Read a model review trace directory and build a compact review object."""

    root = Path(trace_dir)
    manifest = _read_json(root / "trace_manifest.json")
    command = _read_json(root / "command.json")
    normalized_output = _read_json(root / "normalized_output.json")
    gate_decision = _read_json(root / "gate_decision.json")

    provider_status = normalized_output.get("modelProviderStatus")
    if not isinstance(provider_status, dict):
        provider_status = {}
    files = manifest.get("files") if isinstance(manifest.get("files"), dict) else {}

    prompt_recorded = (root / "prompt.md").is_file()
    schema_recorded = (root / "schema.json").is_file()
    command_recorded = not command.get("_readError") and command.get("status") in {"built", "not_built"}
    output_recorded = not normalized_output.get("_readError")
    gate_recorded = not gate_decision.get("_readError")
    trace_usable = bool(prompt_recorded and schema_recorded and output_recorded and gate_recorded)

    model_invocation_usable = (
        provider_status.get("modelInvoked") is True and provider_status.get("modelUnavailable") is not True
    )
    input_sufficient = bool(prompt_recorded and schema_recorded and command_recorded)
    model_output_trust = (
        "schema_valid"
        if provider_status.get("schemaValid") is True
        else "unavailable"
        if provider_status.get("modelUnavailable") is True
        else "schema_invalid"
    )
    gate_status = str(gate_decision.get("status") or "missing")
    gate_passed = gate_status.casefold() in PASS_STATUSES and provider_status.get("blocking") is not True
    blocking_reasons = _collect_blocking_reasons(
        provider_status=provider_status,
        gate_decision=gate_decision,
        normalized_output=normalized_output,
    )
    status = "pass" if trace_usable and model_invocation_usable and model_output_trust == "schema_valid" and gate_passed else "blocked"

    next_repair_focus: list[str] = []
    if not trace_usable:
        next_repair_focus.append("补齐 trace_manifest / prompt / schema / normalized_output / gate_decision 文件。")
    if not model_invocation_usable:
        next_repair_focus.append("检查模型开关、Codex CLI 可执行文件、登录态、额度或 provider 权限。")
    if model_output_trust != "schema_valid":
        next_repair_focus.append("检查 schema required 字段和模型 last message JSON。")
    if not gate_passed:
        next_repair_focus.append("按 gate_decision.json 的阻断原因修复，再重新调用模型 reviewer。")
    if not next_repair_focus:
        next_repair_focus.append("本次 trace 可进入后续任务级 gate 验证。")

    summary_lines = [
        f"trace 可复盘性：{_status_label(trace_usable)}",
        f"模型调用可用性：{_status_label(model_invocation_usable)}",
        f"输入充分性：{_status_label(input_sufficient)}",
        f"模型输出可信度：{model_output_trust}",
        f"错误分类：{provider_status.get('errorCategory') or 'none'}",
        f"gate 结论：{gate_status}",
    ]
    if files.get("exportManifest"):
        summary_lines.append(f"导出边界清单：{files['exportManifest']}")
    if files.get("contextLeakAudit"):
        summary_lines.append(f"上下文泄漏审计：{files['contextLeakAudit']}")
    if blocking_reasons:
        summary_lines.append("阻断原因：" + "；".join(blocking_reasons[:5]))

    return {
        "schemaVersion": 1,
        "status": status,
        "traceDir": str(root),
        "traceId": str(manifest.get("traceId") or ""),
        "agentId": str(manifest.get("agentId") or ""),
        "taskType": str(manifest.get("taskType") or ""),
        "traceUsable": trace_usable,
        "modelInvocationUsable": model_invocation_usable,
        "inputSufficient": input_sufficient,
        "modelOutputTrust": model_output_trust,
        "errorCategory": str(provider_status.get("errorCategory") or ""),
        "gateDecisionStatus": gate_status,
        "blockingReasons": blocking_reasons,
        "nextRepairFocus": next_repair_focus,
        "plainSummary": summary_lines,
        "evidenceBoundary": [
            "trace review only summarizes model invocation evidence",
            "does not replace schema validation",
            "does not replace CAD handles / bbox / layer readback",
            "does not replace A-to-A hard gate or user acceptance",
        ],
    }


def _summary_markdown(review: dict[str, Any]) -> str:
    lines = [
        "# Model Review Trace Summary",
        "",
        f"- Agent: {review.get('agentId') or 'unknown'}",
        f"- Task: {review.get('taskType') or 'unknown'}",
        f"- Trace: {review.get('traceId') or 'unknown'}",
        f"- 状态: {review.get('status')}",
        "",
        "## 本次复盘",
    ]
    lines.extend(f"- {line}" for line in review.get("plainSummary", []))
    lines.extend(["", "## 下一步"])
    lines.extend(f"- {item}" for item in review.get("nextRepairFocus", []))
    lines.extend(
        [
            "",
            "## 边界",
            "- 本摘要只用于调试模型型 Agent 调用，不替代 schema 校验、CAD readback、A-to-A hard gate 或用户验收。",
            "",
        ]
    )
    return "\n".join(lines)


def write_trace_review(trace_dir: Path) -> dict[str, Any]:
    """Write trace_review.json and trace_summary.md for a trace directory."""

    root = Path(trace_dir)
    review = build_trace_review(root)
    _write_json(root / "trace_review.json", review)
    (root / "trace_summary.md").write_text(_summary_markdown(review), encoding="utf-8")
    return review
