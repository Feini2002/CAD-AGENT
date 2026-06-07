"""No-CAD proof helpers for main-Agent cognition claims."""

from __future__ import annotations

from typing import Any


DECISION_KEYS = ("route", "requiredAgents", "toolChoice", "blockingReasons")


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value else []
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        text = str(item).strip()
        if text and text not in result:
            result.append(text)
    return result


def _decision_summary(decision: dict[str, Any]) -> str:
    parts = []
    for key in DECISION_KEYS:
        value = decision.get(key)
        if isinstance(value, list):
            value = ",".join(_strings(value))
        parts.append(f"{key}={value or ''}")
    return "; ".join(parts)


def build_behavior_change_proof(
    *,
    agent_id: str,
    before_decision: dict[str, Any],
    after_decision: dict[str, Any],
    memory_applied_in_future_run: bool,
    retested_original_task: bool,
    prediction: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a machine-checkable before/after decision proof."""

    changed_route = str(before_decision.get("route") or "") != str(after_decision.get("route") or "")
    changed_agents = _strings(before_decision.get("requiredAgents")) != _strings(after_decision.get("requiredAgents"))
    changed_tools = _strings(before_decision.get("toolChoice")) != _strings(after_decision.get("toolChoice"))
    changed_blocking = _strings(before_decision.get("blockingReasons")) != _strings(after_decision.get("blockingReasons"))
    changed_any = changed_route or changed_agents or changed_tools or changed_blocking
    prediction = prediction or {}
    return {
        "schemaVersion": "main-agent-behavior-change-proof/v1",
        "agentId": str(agent_id),
        "beforeDecision": _decision_summary(before_decision),
        "afterDecision": _decision_summary(after_decision),
        "changedRoute": changed_route,
        "changedRequiredAgents": changed_agents,
        "changedToolChoice": changed_tools,
        "changedBlockingReason": changed_blocking,
        "retestedOriginalTask": bool(retested_original_task),
        "memoryAppliedInFutureRun": bool(memory_applied_in_future_run),
        "predictionReconciliation": {
            "statement": str(prediction.get("statement") or ""),
            "reconciled": bool(prediction.get("reconciled")),
            "outcome": str(prediction.get("outcome") or "pending"),
        },
        "claimStatus": "behavior_change_evidence" if changed_any else "mechanism_only",
        "allowedClaim": (
            "可声称本轮记录了主 Agent 行为改变证据，但仍不是 CAD 几何或项目交付证明"
            if changed_any
            else "只可声称机制建设或记录补全，不能声称主 Agent 认知提升"
        ),
        "evidenceBoundary": [
            "behavior change proof is no-CAD",
            "does not replace CAD_PLAN validation, dry-run, CODEX_PREVIEW readback, or user acceptance",
            "does not change Core Proof Coverage",
        ],
    }


def summarize_agent_task_maturity(
    *,
    behavior_proofs: list[dict[str, Any]],
    prediction_records: list[dict[str, Any]],
    overclaim_blocks: int,
    repeated_corrections: int,
) -> dict[str, Any]:
    """Summarize Agent Task Maturity signals without touching Table C."""

    proof_count = len(behavior_proofs)
    route_changes = sum(1 for item in behavior_proofs if item.get("changedRoute") is True)
    tool_changes = sum(1 for item in behavior_proofs if item.get("changedToolChoice") is True)
    blocking_changes = sum(1 for item in behavior_proofs if item.get("changedBlockingReason") is True)
    reconciled = [item for item in prediction_records if item.get("reconciled") is True]
    correct = [item for item in reconciled if str(item.get("outcome")) == "correct"]
    prediction_accuracy = (len(correct) / len(reconciled)) if reconciled else 0.0
    return {
        "schemaVersion": "agent-task-maturity-metrics/v1",
        "behaviorChangeProofCount": proof_count,
        "routeAccuracySignal": route_changes / proof_count if proof_count else 0.0,
        "toolChoiceChangeSignal": tool_changes / proof_count if proof_count else 0.0,
        "blockingReasonChangeSignal": blocking_changes / proof_count if proof_count else 0.0,
        "predictionAccuracy": prediction_accuracy,
        "overclaimBlockCount": int(overclaim_blocks),
        "repeatedCorrectionCount": int(repeated_corrections),
        "evidenceBoundary": {
            "metricFamily": "Agent Task Maturity",
            "notProofOf": ["Core Proof Coverage", "CAD geometry", "Project Delivery Readiness"],
        },
    }
