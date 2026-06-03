from __future__ import annotations

from typing import Any


GATE_DECISION_KEYS = (
    "updateTrainingSource",
    "updateWorkbench",
    "updateBaseRules",
    "updateTaskRules",
    "updateAgentCalibration",
    "updateChecker",
    "retestOriginalTask",
)


def _unique(items: list[str]) -> list[str]:
    result: list[str] = []
    for item in items:
        if item and item not in result:
            result.append(item)
    return result


def _decision(
    *,
    required: bool,
    status: str,
    reason: str,
    target: str = "",
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "required": required,
        "status": status,
        "reason": reason,
        "target": target,
        "evidence": evidence or [],
    }


def _system_learning_reports(reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for report in reports:
        learning = report.get("systemLearning") or report.get("learningPromotionGate") or {}
        if isinstance(learning, dict):
            rows.append(learning)
    return rows


def _collect_list(reports: list[dict[str, Any]], key: str) -> list[str]:
    values: list[str] = []
    for report in reports:
        raw = report.get(key, [])
        if isinstance(raw, str):
            values.append(raw)
        elif isinstance(raw, list):
            values.extend(str(item) for item in raw if item)
    for learning in _system_learning_reports(reports):
        raw = learning.get(key, [])
        if isinstance(raw, str):
            values.append(raw)
        elif isinstance(raw, list):
            values.extend(str(item) for item in raw if item)
    return _unique(values)


def _original_task_ref(reports: list[dict[str, Any]]) -> str:
    for report in reports:
        for key in ("originalTaskRef", "original_task_ref"):
            if report.get(key):
                return str(report[key])
    for learning in _system_learning_reports(reports):
        for key in ("originalTaskRef", "original_task_ref"):
            if learning.get(key):
                return str(learning[key])
    return ""


def _is_quick_trial(reports: list[dict[str, Any]]) -> bool:
    return any(str(report.get("mode", "")).lower() == "quick_trial" for report in reports)


def build_training_promotion_gate(
    *,
    reports: list[dict[str, Any]],
    accepted_items: list[dict[str, Any]],
    agent_updates: list[dict[str, Any]],
    source_reports: list[str],
) -> dict[str, Any]:
    """Build the mandatory training promotion checklist without mutating targets."""

    quick_trial = _is_quick_trial(reports)
    promotable = bool(accepted_items) and not quick_trial
    source_evidence = _unique(source_reports)
    affected_agents = _unique(
        [
            str(agent_id)
            for update in agent_updates
            for agent_id in [update.get("agentId", "")]
            if agent_id
        ]
    )
    capability_ids = _unique(
        [
            str(item.get("capabilityId", ""))
            for item in accepted_items
            if item.get("capabilityId")
        ]
    )
    base_rule_deltas = _collect_list(reports, "baseRuleDeltas")
    task_rule_deltas = _collect_list(reports, "taskRuleDeltas")
    checker_deltas = _collect_list(reports, "checkerDeltas")
    original_task_ref = _original_task_ref(reports)

    if quick_trial or not promotable:
        promotion_level = "observation"
        quick_reason = "快试或未通过正式验收，只能保留观察证据，不自动写训练事实源、工作台或 Agent 校准。"
        decisions = {
            "updateTrainingSource": _decision(required=False, status="not_required", reason=quick_reason),
            "updateWorkbench": _decision(required=False, status="not_required", reason=quick_reason),
            "updateBaseRules": _decision(required=False, status="not_required", reason="无正式规则 delta。"),
            "updateTaskRules": _decision(required=False, status="not_required", reason="无正式单项任务规则 delta。"),
            "updateAgentCalibration": _decision(required=False, status="not_required", reason=quick_reason),
            "updateChecker": _decision(required=False, status="not_required", reason="无检查器 delta。"),
            "retestOriginalTask": _decision(required=False, status="not_required", reason="没有需要回测的正式原任务。"),
        }
    else:
        promotion_level = "systemized"
        decisions = {
            "updateTrainingSource": _decision(
                required=True,
                status="ready",
                reason="正式训练验收通过后必须登记或核对训练事实源。",
                target="docs/training/training-sources.json",
                evidence=source_evidence,
            ),
            "updateWorkbench": _decision(
                required=True,
                status="required",
                reason="训练事实变化后必须刷新 capability-map-data.js / HTML 派生快照。",
                target="scripts/sync_training_workbench.py",
                evidence=source_evidence,
            ),
            "updateBaseRules": _decision(
                required=bool(base_rule_deltas),
                status="needs_reviewed_package" if base_rule_deltas else "not_required",
                reason=(
                    "存在底座规则 delta，只能进入 reviewed package，不能由训练脚本静默改长期规则。"
                    if base_rule_deltas
                    else "本轮没有底座规则 delta。"
                ),
                target="docs/governance/cad-agent-rules.md",
                evidence=base_rule_deltas,
            ),
            "updateTaskRules": _decision(
                required=bool(task_rule_deltas),
                status="needs_reviewed_package" if task_rule_deltas else "not_required",
                reason=(
                    "存在单项任务规则 delta，需要写入对应任务规则或检查器并单独验收。"
                    if task_rule_deltas
                    else "本轮没有单项任务规则 delta。"
                ),
                evidence=task_rule_deltas,
            ),
            "updateAgentCalibration": _decision(
                required=True,
                status="ready" if affected_agents else "blocked",
                reason="正式训练沉淀必须同步责任 Agent memory / prompt addendum，形成 A-to-A 校准输入。",
                target="agents/**/training_memory.json",
                evidence=affected_agents,
            ),
            "updateChecker": _decision(
                required=bool(checker_deltas),
                status="needs_reviewed_package" if checker_deltas else "not_required",
                reason=(
                    "存在检查器 delta，需要单独实现和红绿测试。"
                    if checker_deltas
                    else "本轮没有检查器 delta。"
                ),
                evidence=checker_deltas,
            ),
            "retestOriginalTask": _decision(
                required=bool(original_task_ref),
                status="required" if original_task_ref else "not_required",
                reason=(
                    "本轮声明了原任务引用，沉淀后必须回测原任务。"
                    if original_task_ref
                    else "没有声明原任务引用；保持 not_checked，不能声称已回测原任务。"
                ),
                target=original_task_ref,
                evidence=[original_task_ref] if original_task_ref else [],
            ),
        }

    return {
        "schemaVersion": 1,
        "status": "ready",
        "promotionLevel": promotion_level,
        "decisionOrder": list(GATE_DECISION_KEYS),
        "decisions": decisions,
        "acceptedCapabilityIds": capability_ids,
        "sourceReportPaths": source_evidence,
        "agentCalibration": {
            "required": decisions["updateAgentCalibration"]["required"],
            "affectedAgentIds": affected_agents,
            "positiveExamples": [
                "白话训练验收通过后，按责任 Agent 列表写入 training_memory.json 与 prompt_addendum.md。",
                "有底座规则、任务规则或检查器 delta 时，只生成候选和 reviewed package 要求。",
            ],
            "negativeExamples": [
                "快试、截图推断或缺 handles/readback 的反馈不得自动写全局规则。",
                "不能用截图或一次通过冒充真实 CAD 几何证明。",
                "不能把需要人工复审的底座规则 delta 静默写入长期规则。",
            ],
            "evidenceBoundary": "promotion gate 只记录沉淀决策和 A-to-A 校准输入；表 C、资产 verified、原任务回测必须另有证据。",
        },
        "blockedReasons": [
            key
            for key in GATE_DECISION_KEYS
            if decisions[key]["required"] and decisions[key]["status"] == "blocked"
        ],
    }


def build_failure_promotion_gate(
    *,
    failure: dict[str, Any],
    decision: dict[str, Any],
) -> dict[str, Any]:
    """Build a reviewed-package gate for failure / correction lessons."""

    requires_review = bool(decision.get("requires_human_review"))
    promotion_level = "learning_candidate" if requires_review else "case_lesson"
    promotion_target = str(decision.get("promotion_target") or "")
    category = str(decision.get("category") or "")
    original_task_ref = str(failure.get("originalTaskRef") or failure.get("original_task_ref") or "")
    affected_agents = _unique(
        [
            str(agent_id)
            for agent_id in failure.get("affectedAgentIds", [])
            if agent_id
        ]
    )
    if not affected_agents and category in {"pipeline", "scene_rule", "core_probe_candidate"}:
        affected_agents = ["cad_designer", "pipeline_intent", "pipeline_execute", "pipeline_audit"]

    task_rule_required = category in {"pipeline", "scene_rule", "case_geometry", "core_probe_candidate"}
    base_rule_required = category in {"core_probe_candidate"}
    checker_required = category in {"core_probe_candidate", "case_geometry"}
    agent_calibration_required = requires_review or bool(affected_agents)

    decisions = {
        "updateTrainingSource": _decision(
            required=False,
            status="not_required",
            reason="失败 / 纠错报告先进入案例教训或候选沉淀，不直接登记为训练验收事实源。",
        ),
        "updateWorkbench": _decision(
            required=False,
            status="not_required",
            reason="未形成正式训练验收通过证据，不刷新为工作台已沉淀状态。",
        ),
        "updateBaseRules": _decision(
            required=base_rule_required,
            status="needs_reviewed_package" if base_rule_required else "not_required",
            reason=(
                "涉及 Core / 底座检查器候选，需要 reviewed package 后才能改长期规则。"
                if base_rule_required
                else "本轮失败归因不要求直接改底座规则。"
            ),
            target="docs/governance/cad-agent-rules.md" if base_rule_required else "",
        ),
        "updateTaskRules": _decision(
            required=task_rule_required,
            status="needs_reviewed_package" if task_rule_required else "not_required",
            reason=(
                "失败已归因到可复用链路 / 场景 / 单项任务规则，需要 reviewed package。"
                if task_rule_required
                else "只需记录为案例记忆。"
            ),
            target=promotion_target,
        ),
        "updateAgentCalibration": _decision(
            required=agent_calibration_required,
            status="needs_reviewed_package" if agent_calibration_required else "not_required",
            reason=(
                "纠错影响责任 Agent 行为，需要写明 A-to-A 校准并经回测。"
                if agent_calibration_required
                else "只记录案例记忆，不改变责任 Agent。"
            ),
            target="agents/**/training_memory.json",
            evidence=affected_agents,
        ),
        "updateChecker": _decision(
            required=checker_required,
            status="needs_reviewed_package" if checker_required else "not_required",
            reason=(
                "失败可机器化为检查器候选，需要单独实现红绿测试。"
                if checker_required
                else "本轮没有检查器候选。"
            ),
        ),
        "retestOriginalTask": _decision(
            required=bool(original_task_ref),
            status="required" if original_task_ref else "not_required",
            reason=(
                "纠错报告声明了原任务引用，规则 / 校准落地后必须回测原任务。"
                if original_task_ref
                else "未声明原任务引用，不能声称已回测。"
            ),
            target=original_task_ref,
            evidence=[original_task_ref] if original_task_ref else [],
        ),
    }

    return {
        "schemaVersion": 1,
        "status": "ready",
        "promotionLevel": promotion_level,
        "decisionOrder": list(GATE_DECISION_KEYS),
        "decisions": decisions,
        "failureCategory": category,
        "promotionTarget": promotion_target,
        "agentCalibration": {
            "required": agent_calibration_required,
            "affectedAgentIds": affected_agents,
            "positiveExamples": [
                "纠错命令先生成候选沉淀和目标文件，不直接静默修改全局规则。",
                "规则或 Agent 校准落地后，回测原任务再同步事实源。",
            ],
            "negativeExamples": [
                "不能把单次反馈直接升级为全局规则。",
                "不能只写聊天总结而不写候选目标和回测要求。",
            ],
            "evidenceBoundary": "失败 promotion gate 只证明已识别沉淀候选；规则、检查器、Agent 校准和回测仍需 reviewed package 证据。",
        },
        "blockedReasons": [],
    }
