"""Learning-promotion and round-gate helpers for training cases."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.training.promotion_gate import build_failure_promotion_gate, build_training_promotion_gate


ROUND_GATE_STAGES = {"visual_contract", "delivery"}
ITEM_COUNT_ACCEPTANCE_CHECKS = {
    "all_10_items_generated",
    "all_21_items_generated",
    "all_items_generated",
}
REQUIRED_ACCEPTANCE_CHECKS = {
    "persistent_handle_readback",
    "preview_layer_only",
    "dwg_not_saved",
    "chinese_labels",
}
AGENT_LEARNING_FILES = ("training_memory.json", "prompt_addendum.md")
COMMON_PROMPT_CONTRACT_REL = "agents/COMMON_PROMPT_CONTRACT.md"
COMMON_PROMPT_GUIDANCE = (
    "CAD 测试必须使用中文标注；图层名、文件名、Schema key 等技术名允许保留原文。",
    "落图前先选择不覆盖旧图形的测试画布，避免重叠用户已有图块。",
    "通过前必须回读 created handles，并说明 checked / not_checked。",
    "真实 CAD 测试默认只写 CODEX_PREVIEW，不保存 DWG，不污染正式图层。",
)
POSITION_FEEDBACK_PROMPT_GUIDANCE = (
    "用户用箭头、蓝圈或截图指定 CAD 位置时，先识别被指对象及相对位置，不得默认另起训练模块。",
    "图像反馈类 CAD 修正应优先从当前 AutoCAD 实体回读参照 bbox，再按当前画面语义定位；不要套旧 execution summary 坐标。",
    "若用户要求同尺寸补画样本，先从已存在样本 bbox 推导尺寸，再画新对象并回读 created handles。",
    "误画在其它区域的预览实体默认保留，未经用户明确批准不得删除 CAD 对象或保存 DWG。",
)
SCREENSHOT_ORCHESTRATION_PROMPT_GUIDANCE = (
    "CAD 截图必须走任务级截图编排：局部修复优先传 target_handles、repair_plan.target_handles 或 repair_plan.target_bbox；没有局部目标时才退到 execution_summary.created_handles。",
    "AutoCAD 会话截图默认保留 CAD / IDE 布局，用 AutoCAD 客户区 PrintWindow；只有 PrintWindow 失败或 CAD 完全不可见时才短暂置顶。",
    "单项复验、focused retraining、视觉复核和正式验收需要截图时，Agent 必须报告 screenshotDecision 和 visualPreview，并说明截图只是 visual_aid_only。",
    "截图不得替代 created handles、CAD readback、bbox / 属性审计或用户验收；目标句柄不可用时报告 focus_target_unavailable，不得把 whole modelspace / 当前屏幕当作成功证据。",
)
SYSTEM_ASSET_REUSE_PROMPT_GUIDANCE = (
    "白话出现调用、复用、套用或强匹配系统库资产时，先检索 libraries/system_library/registry.json，并生成 system_asset_reuse_workflow；弱匹配只给候选，不直接落图。",
    "线型、尺寸、文字、引线等 style_standard 资产只走 style_export / style_definition / 原生样式源；不得把 training_panel、current_screen、whole_modelspace 或全 CODEX_PREVIEW 复制成对象 block。",
    "沉淀 style_standard 或其它系统资产时，元数据合同不等于真沉淀；native_style_definition_written 必须同时有 nativeVisiblePanelEvidence 或等价可见 native 证据，verified 资产还必须有 reuseWorkflowProbe 或真实 reuseReplay。",
    "native_style_definition_written 表示系统资产 DWG 已有原生样式定义，可生成 style_definition 复用计划；跨 DWG 真正应用仍需 style import / readback gate，且不得保存当前业务 DWG。",
    "资产复用交付必须报告 matched asset、sourceSpec、target、readbackStatus 和 savedCurrentDwg=false；样式 importer 缺失时返回 deferred，不得声称 asset_reused。",
)
SYSTEM_ASSET_VISUAL_WAREHOUSE_PROMPT_GUIDANCE = (
    "系统资产 DWG 仓库验收不能只看截图非空、DWG 已保存或 overlapCount=0；还必须检查通道可读、内容密度、源/证明角色分离、图层语义和非截图证据。",
    "pipeline_visual_layout_reviewer 必须输出 layoutReadabilityAcceptable、aisleClearanceAcceptable、contentDensityAcceptable、sourceProofRolesSeparated、layerSemanticsAcceptable 和 nonScreenshotEvidenceChecked；缺任一字段时 visual_layout_review 继续阻断。",
    "protectedContentReadback 必须提供 full layer census，例如 layers / layerCounts；layerSamples 只能作展示样本，不能证明 A1/A2 没有 CODEX_PREVIEW 污染。",
    "资产合同、nativeVisiblePanelEvidence、reuseWorkflowProbe 和 evidenceLinks 引用的本地证据文件必须存在；缺失时资产库治理不得 pass。",
    "样式标准的可视面板只表示 proof panel；真正可复用来源是命名样式定义或精确边界 clean source，标签、边框、尺寸线、截图、证据卡片和 proof panel 默认 never-copy。",
    "系统资产 DWG 的 proof content 不得继续留在 CODEX_PREVIEW；应迁到 ASSET_PROOF_CONTENT 等角色图层，并把 ASSET_SOURCE_BOUNDARY 控制为小的 source token，而不是框住证明图形的大边框。",
)
DESIGN_INTELLIGENCE_PROMPT_GUIDANCE = (
    "5.5 模型桥必须覆盖设计阶段：主 Agent 不只路由任务，还要像专业设计师一样先判断图纸类型、表达目的、设计意图、行业常识、约束和应分发的 Agent。",
    "创造性或样式敏感任务不得从 brief 直接跳到 CAD_PLAN；应先由 pipeline_design_director 生成 designStrategy，再按语义决定是否让 pipeline_style_generator waiver、生成单方案或生成 2-3 套参数化候选，最后在需要时由 pipeline_design_reviewer 于 CAD readback 后复核。",
    "“新样式、创造性表达、A/B/C、候选、发后选”只是语义信号，不是死命令；只有用户明确要多方案、对比或选择时才强制多候选，否则允许单方案、自动选择或不进入样式候选。",
    "对话框 / CLI 层必须先看 semanticDecomposition：规则问题、提醒和只分析语义不触发执行型设计 Agent；明确“两套 / 两个方案”时按 2 个候选处理，不得强行变成 A/B/C；用户否定创造性时 creativityPolicy=suppressed_by_user。",
    "样式候选必须写清尺寸、比例、文字层级、线距、颜色 / 图层策略、图纸密度、对象类型和选择理由；不能只复制固定模板或只说“看起来更好”。",
    "pipeline_design_reviewer 必须判断输出是否像专业图纸、是否可读、是否符合行业习惯、是否匹配设计目的、是否需要请用户选择 A/B/C 或继续润色。",
    "设计阶段模型输出仍然只读，不能执行 CAD、不能保存 DWG、不能替代 validate / dry-run / created handles readback / 用户验收；设计经验通过 learningCandidate 进入 Agent 自动成长。",
)
MODEL_BACKED_AGENT_PROMPT_GUIDANCE = (
    "当前 agents/ 目录里的多数 Agent 是角色契约和规则门禁，不等于每个角色都会独立调用模型；只有显式经过 core/model_review、codex.cmd exec 或未来 SDK 桥并产生 modelBackedReview 的步骤，才算模型型复审。",
    "不使用 API key 的本机方案默认走 codex.cmd exec：输入截图、readback 摘要和 schema，输出严格 JSON；该调用依赖本机 Codex 登录态、模型权限和额度。",
    "当前模型型 reviewer 的统一底座策略是本机 Codex CLI + gpt-5.5 + model_reasoning_effort=medium；准确性优先模式下不按额度分档，登记为模型桥判断节点的 Agent 应尽量调用 5.5 复审，实际可用性由 modelProviderStatus 记录。",
    "所有模型型 reviewer 必须输出 modelProviderStatus，并统一声明 modelInvoked、modelUnavailable、schemaValid、route 和 required；modelUnavailable=true 或 schemaValid=false 时不得静默通过。",
    "模型调用路线先分为 codex_cli_local、local_model、remote_summary_only 和 remote_full_visual；任何远端 summary / 截图 / 报告路线都必须先有用户授权。",
    "模型型复审默认只读，不能写 CAD、不能保存 DWG、不能删除或移动实体，也不能扩大用户授权范围。",
    "需要工具时只能输出 schema 化 toolIntent，由 Orchestrator 的 Tool Contract ReAct gate 决定 allowed / blocked / needs_more_evidence；Stage 1/2/3/4 工具结果以 tool_trace 和 JSON report 为准。Stage 4 受控 CAD 只允许 preview_cad_execute / execute_cad_plan_preview，且必须 validate + dry-run 已 pass、只写 CODEX_PREVIEW、savedCurrentDwg=false；模型不能自行宣布 validate、dry-run、audit、closeout、CAD 写入或真实 readback 已经通过。",
    "模型 pass 只表示从截图 / 摘要视角看可读性或语义问题较少；不能替代 UTF-8 编码门禁、CAD created handles 回读、bbox / layer / overlap / readability 审计、资产 sourceSpec、reuseReplay 或用户验收。",
    "模型 fail、schema 不合格、输出缺字段、未实际调用却被声明为 required，必须阻断 visual_layout_review 或对应 hard gate，并给出 repairRecommendation / blockingReasons。",
    "pipeline_asset_governor 可记录 modelAssistedDecision，辅助分类、来源边界和 clean source 建议；这些建议只读，不能覆盖 sourceBoundaryDecision、CAD readback、reuse probe、保存边界或 verified 晋升门禁。",
    "pipeline_visual_acceptance_reviewer 可记录 modelBackedVisualAcceptance，辅助判断美观度、文字可读性、乱码、遮挡、裁剪、对齐、意图匹配和可复用边界；模型通过不能替代用户验收、CAD readback 或修复回归。",
    "pipeline_repair 可消费 modelBackedRepairPlan / repairPlanCandidate，但 executionPolicy 必须是 proposal_only；模型修复计划不能包含 cadCommands、保存当前 DWG、广域删除、正式图层编辑或执行授权。",
    "5.5 模型桥扩展清单和初步 Prompt 规范收口在 CORE_RESTRUCTURE_PLAN.md 与 agents/pipeline/pipeline_manifest.json；P0 为设计智能、视觉验收、交付、修复和主编排，P1 为视觉语义、意图、审计和资产治理，P2 为上下文、检索、馆员、复用审计和学习沉淀，P3 为 execute 执行前安全守卫。",
    "每个使用 5.5 模型桥的 Agent 都必须输出 learningCandidate 或等价字段，记录 errorPattern、correctPattern、promptDelta、checkerDelta、retestOriginalTask 和 responsibleAgentIds；没有可沉淀经验时显式写 not_required。",
    "模型 fail、用户反馈 fail、机器审计 fail 或 closeout blocked 后，pipeline_learning_promoter 必须把可沉淀经验写入责任 Agent 的 training_memory.json / prompt_addendum.md；共用规则只更新 agents/COMMON_PROMPT_CONTRACT.md 及其生成源。",
    "模型桥 Agent 的成长目标是自动升级：持续吸收错误记录、总结正确经验、回测原任务、修正 Prompt 和检查器；但训练沉淀不提升表 C，不替代 CAD readback、sourceSpec、reuseReplay 或用户验收。",
)
SHARED_PROMPT_GUIDANCE = (
    set(COMMON_PROMPT_GUIDANCE)
    | set(POSITION_FEEDBACK_PROMPT_GUIDANCE)
    | set(SCREENSHOT_ORCHESTRATION_PROMPT_GUIDANCE)
    | set(SYSTEM_ASSET_REUSE_PROMPT_GUIDANCE)
    | set(SYSTEM_ASSET_VISUAL_WAREHOUSE_PROMPT_GUIDANCE)
    | set(DESIGN_INTELLIGENCE_PROMPT_GUIDANCE)
    | set(MODEL_BACKED_AGENT_PROMPT_GUIDANCE)
)


def _round_prefix(round_id: str | int) -> str:
    text = str(round_id)
    return text if text.startswith("round") else f"round{text}"


def _relpath(root: Path, path: Path) -> str:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    try:
        return resolved_path.relative_to(resolved_root).as_posix()
    except ValueError:
        return resolved_path.as_posix()


def _agent_dir(root: Path, agent_id: str) -> Path:
    if agent_id.startswith("pipeline_"):
        return root / "agents" / "pipeline" / agent_id.removeprefix("pipeline_")
    return root / "agents" / agent_id


def _program_map(programs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(program.get("capabilityId", "")): program for program in programs}


def _report_checks_pass(report: dict[str, Any]) -> bool:
    checks = {str(item.get("name")): item.get("status") for item in report.get("checks", [])}
    item_count_ok = any(checks.get(name) == "pass" for name in ITEM_COUNT_ACCEPTANCE_CHECKS)
    return item_count_ok and all(checks.get(name) == "pass" for name in REQUIRED_ACCEPTANCE_CHECKS)


def acceptance_report_is_promotable(report: dict[str, Any]) -> bool:
    if str(report.get("mode", "")).lower() == "quick_trial":
        return False
    if report.get("status") != "pass":
        return False
    if report.get("visual_self_check", {}).get("status") != "pass":
        return False
    return _report_checks_pass(report)


def _lesson_for_item(item: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    handle_count = int(item.get("handle_count") or 0)
    readback_count = int(item.get("readback_count") or 0)
    feedback = str(item.get("feedback") or "")
    title = str(item.get("title") or item.get("capabilityId") or "")
    custom_guidance = [str(text) for text in item.get("promptGuidance", []) if isinstance(text, str) and text.strip()]
    return {
        "capabilityId": str(item.get("capabilityId") or ""),
        "title": title,
        "summary": f"{title} 已通过中文训练验收，handles {readback_count}/{handle_count} 已回读。",
        "promptGuidance": _merge_unique(
            [
                *COMMON_PROMPT_GUIDANCE,
                *SCREENSHOT_ORCHESTRATION_PROMPT_GUIDANCE,
                *custom_guidance,
            ]
        ),
        "evidence": {
            "queueId": report.get("queueId", ""),
            "mode": report.get("mode", ""),
            "handleCount": handle_count,
            "readbackCount": readback_count,
            "feedback": feedback,
        },
        "sourceGeneratedAt": str(report.get("generated_at") or ""),
    }


def _merge_unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _memory_payload(
    *,
    agent_id: str,
    lessons: list[dict[str, Any]],
    source_reports: list[str],
    updated_at: str,
) -> dict[str, Any]:
    accepted = _merge_unique([lesson["capabilityId"] for lesson in lessons])
    prompt_updates = _merge_unique(
        [
            guidance
            for lesson in lessons
            for guidance in lesson.get("promptGuidance", [])
            if isinstance(guidance, str)
        ]
    )
    return {
        "schemaVersion": 1,
        "agentId": agent_id,
        "learningState": "prompt_updated",
        "updatedAt": updated_at,
        "sourceReports": source_reports,
        "acceptedCapabilities": accepted,
        "acceptedCapabilityCount": len(accepted),
        "lessonCount": len(lessons),
        "lessons": lessons,
        "promptUpdateSummary": prompt_updates,
        "evidenceBoundary": "训练沉淀只更新 Agent 经验、Prompt 和检查口径；不提升表 C，不代表完整施工图能力。",
    }


def _prompt_addendum(agent_id: str, memory: dict[str, Any]) -> str:
    role_specific_guidance = [
        guidance
        for guidance in memory.get("promptUpdateSummary", [])
        if isinstance(guidance, str) and guidance not in SHARED_PROMPT_GUIDANCE
    ]
    lines = [
        "# Training Prompt Addendum",
        "",
        f"Agent: `{agent_id}`",
        f"Updated: `{memory['updatedAt']}`",
        "",
        "## 共用 Prompt 合同",
        f"- 通用 CAD 安全、证据和视觉反馈规则见 `{COMMON_PROMPT_CONTRACT_REL}`。",
        "",
        "## 已验收能力",
    ]
    for capability_id in memory.get("acceptedCapabilities", []):
        lines.append(f"- `{capability_id}`")
    lines.extend(["", "## 角色专属 Prompt 优化"])
    if not role_specific_guidance:
        lines.append("- 本轮没有新增角色专属规则；共用规则只在共享合同维护。")
    for guidance in role_specific_guidance:
        lines.append(f"- {guidance}")
    lines.extend(["", "## 证据边界", "见共用 Prompt 合同；本文件只记录角色专属训练沉淀。", ""])
    return "\n".join(lines)


def _common_prompt_contract() -> str:
    lines = [
        "# Common Prompt Contract",
        "",
        "本文件是 CAD Designer Agent 与 pipeline Agent 的共享 Prompt 合同。各 Agent 的 `prompt_addendum.md` 只保留角色专属训练经验；以下通用安全、证据和反馈规则统一从这里读取，避免多处复制后漂移。",
        "",
        "## 通用 CAD 训练规则",
        "",
    ]
    lines.extend(f"- {guidance}" for guidance in COMMON_PROMPT_GUIDANCE)
    lines.extend(["", "## 视觉与位置反馈规则", ""])
    lines.extend(f"- {guidance}" for guidance in POSITION_FEEDBACK_PROMPT_GUIDANCE)
    lines.extend(["", "## 截图编排规则", ""])
    lines.extend(f"- {guidance}" for guidance in SCREENSHOT_ORCHESTRATION_PROMPT_GUIDANCE)
    lines.extend(["", "## 系统资产与样式复用规则", ""])
    lines.extend(f"- {guidance}" for guidance in SYSTEM_ASSET_REUSE_PROMPT_GUIDANCE)
    lines.extend(["", "## 系统资产 DWG 视觉仓库验收规则", ""])
    lines.extend(f"- {guidance}" for guidance in SYSTEM_ASSET_VISUAL_WAREHOUSE_PROMPT_GUIDANCE)
    lines.extend(["", "## 设计智能与创造性样式规则", ""])
    lines.extend(f"- {guidance}" for guidance in DESIGN_INTELLIGENCE_PROMPT_GUIDANCE)
    lines.extend(["", "## 模型型 Agent / Codex CLI 复审边界", ""])
    lines.extend(f"- {guidance}" for guidance in MODEL_BACKED_AGENT_PROMPT_GUIDANCE)
    lines.extend(["", "## 证据边界", "", "训练沉淀只更新 Agent 经验、Prompt 和检查口径；不提升表 C，不代表完整施工图能力。", ""])
    return "\n".join(lines)


def _write_common_prompt_contract(root: Path) -> Path:
    path = root / COMMON_PROMPT_CONTRACT_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_common_prompt_contract(), encoding="utf-8")
    return path


def write_common_prompt_contract(root: Path) -> Path:
    """Refresh the shared prompt contract from current global guidance."""
    return _write_common_prompt_contract(root)


def promote_training_acceptance(
    *,
    root: Path,
    report_paths: list[Path],
    programs: list[dict[str, Any]],
    ledger_path: Path | None = None,
) -> dict[str, Any]:
    """Promote passed training acceptance reports into agent memory and prompt addenda."""

    root = Path(root)
    program_by_id = _program_map(programs)
    source_reports: list[str] = []
    accepted_reports: list[dict[str, Any]] = []
    agent_lessons: dict[str, list[dict[str, Any]]] = {}
    accepted_items: list[dict[str, Any]] = []

    for report_path in report_paths:
        path = Path(report_path)
        if not path.exists():
            continue
        report, error = _read_json(path)
        if error or not report or not acceptance_report_is_promotable(report):
            continue
        accepted_reports.append(report)
        source_rel = _relpath(root, path)
        source_reports.append(source_rel)
        for item in report.get("items", []):
            if item.get("status") != "pass":
                continue
            capability_id = str(item.get("capabilityId") or "")
            if not capability_id:
                continue
            program = program_by_id.get(capability_id, {})
            if not program:
                continue
            agent_ids = list(program.get("responsibleAgentIds") or ["cad_designer"])
            lesson = _lesson_for_item(item, report)
            lesson["responsibleAgentIds"] = agent_ids
            lesson["sourceReport"] = source_rel
            accepted_items.append(lesson)
            for agent_id in agent_ids:
                agent_lessons.setdefault(agent_id, []).append(lesson)

    if not accepted_items:
        promotion_gate = build_training_promotion_gate(
            reports=accepted_reports,
            accepted_items=[],
            agent_updates=[],
            source_reports=source_reports,
        )
        result = {
            "schemaVersion": 1,
            "status": "no_promotable_acceptance",
            "sourceReportPaths": source_reports,
            "acceptedItemCount": 0,
            "promotedAgentCount": 0,
            "agentUpdates": [],
            "promotionGate": promotion_gate,
        }
        target = ledger_path or root / "output" / "training_learning" / "agent_learning_ledger.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result

    updated_at = str(accepted_items[-1].get("sourceGeneratedAt") or "")
    if not updated_at:
        first_report = Path(report_paths[0])
        report, _ = _read_json(first_report) if first_report.exists() else ({}, None)
        updated_at = str((report or {}).get("generated_at") or "")

    agent_updates: list[dict[str, Any]] = []
    common_prompt_path = _write_common_prompt_contract(root)
    for agent_id, lessons in sorted(agent_lessons.items()):
        agent_dir = _agent_dir(root, agent_id)
        agent_dir.mkdir(parents=True, exist_ok=True)
        memory_path = agent_dir / "training_memory.json"
        prompt_path = agent_dir / "prompt_addendum.md"
        memory = _memory_payload(
            agent_id=agent_id,
            lessons=lessons,
            source_reports=source_reports,
            updated_at=updated_at,
        )
        memory_path.write_text(json.dumps(memory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        prompt_path.write_text(_prompt_addendum(agent_id, memory), encoding="utf-8")
        agent_updates.append(
            {
                "agentId": agent_id,
                "learningState": "prompt_updated",
                "acceptedCapabilities": memory["acceptedCapabilities"],
                "acceptedCapabilityCount": memory["acceptedCapabilityCount"],
                "lessonCount": memory["lessonCount"],
                "sourceRefs": [_relpath(root, memory_path), _relpath(root, prompt_path), _relpath(root, common_prompt_path)],
                "promptUpdateSummary": memory["promptUpdateSummary"],
            }
        )

    promotion_gate = build_training_promotion_gate(
        reports=accepted_reports,
        accepted_items=accepted_items,
        agent_updates=agent_updates,
        source_reports=source_reports,
    )
    result = {
        "schemaVersion": 1,
        "status": "promoted",
        "sourceReportPaths": source_reports,
        "acceptedItemCount": len(accepted_items),
        "promotedAgentCount": len(agent_updates),
        "agentUpdates": agent_updates,
        "acceptedItems": accepted_items,
        "promotionGate": promotion_gate,
        "evidenceBoundary": "训练验收已沉淀到对应 Agent 记忆和 Prompt 附加文件；这仍不提升表 C。",
    }
    target = ledger_path or root / "output" / "training_learning" / "agent_learning_ledger.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def build_learning_index(ledger: dict[str, Any]) -> dict[str, Any]:
    by_agent: dict[str, dict[str, Any]] = {}
    by_capability: dict[str, dict[str, Any]] = {}
    promotion_gate = ledger.get("promotionGate", {})
    lessons_by_capability = {
        str(item.get("capabilityId")): item
        for item in ledger.get("acceptedItems", [])
        if item.get("capabilityId")
    }
    for update in ledger.get("agentUpdates", []):
        agent_id = str(update.get("agentId") or "")
        if not agent_id:
            continue
        accepted = [str(item) for item in update.get("acceptedCapabilities", []) if item]
        by_agent[agent_id] = {
            "agentId": agent_id,
            "learningState": update.get("learningState", ""),
            "acceptedCapabilities": accepted,
            "acceptedCapabilityCount": len(accepted),
            "sourceRefs": update.get("sourceRefs", []),
            "promptUpdateSummary": update.get("promptUpdateSummary", []),
            "promotionGate": promotion_gate,
        }
        for capability_id in accepted:
            entry = by_capability.setdefault(
                capability_id,
                {
                    "status": "promoted",
                    "capabilityId": capability_id,
                    "agentUpdates": [],
                    "promotedAgentIds": [],
                    "sourceRefs": [],
                    "promptUpdateSummary": [],
                },
            )
            entry["agentUpdates"].append(
                {
                    "agentId": agent_id,
                    "learningState": update.get("learningState", ""),
                    "sourceRefs": update.get("sourceRefs", []),
                }
            )
            entry["promotedAgentIds"].append(agent_id)
            entry["sourceRefs"].extend(update.get("sourceRefs", []))
            entry["promptUpdateSummary"].extend(update.get("promptUpdateSummary", []))

    for entry in by_capability.values():
        entry["promotedAgentIds"] = _merge_unique(entry["promotedAgentIds"])
        entry["sourceRefs"] = _merge_unique(entry["sourceRefs"])
        entry["promptUpdateSummary"] = _merge_unique(entry["promptUpdateSummary"])
        entry["promotedAgentCount"] = len(entry["promotedAgentIds"])
        entry["promotionGate"] = promotion_gate
        lesson = lessons_by_capability.get(entry["capabilityId"], {})
        visible_lessons = [
            str(item)
            for item in lesson.get("promptGuidance", entry["promptUpdateSummary"])
            if item
        ][:4]
        title = str(lesson.get("title") or entry["capabilityId"])
        if lesson:
            entry["plainLanguageSummary"] = (
                f"已把“{title}”的训练经验沉淀到 {entry['promotedAgentCount']} 个责任智能体；"
                "后续遇到同类任务，会优先按这些中文规则执行。"
            )
        else:
            entry["plainLanguageSummary"] = (
                f"已把这项训练经验沉淀到 {entry['promotedAgentCount']} 个责任智能体；"
                "后续会按已更新的中文 Prompt 执行。"
            )
        entry["visibleLessons"] = visible_lessons

    return {
        "status": ledger.get("status", "missing"),
        "sourceReportPaths": ledger.get("sourceReportPaths", []),
        "acceptedItemCount": ledger.get("acceptedItemCount", 0),
        "promotedAgentCount": ledger.get("promotedAgentCount", 0),
        "promotionGate": promotion_gate,
        "byAgent": by_agent,
        "byCapability": by_capability,
    }


def _failure_text(failure: dict[str, Any]) -> str:
    fields = [
        "summary",
        "phenomenon",
        "root_cause",
        "fix",
        "failure_type",
        "category",
    ]
    return " ".join(str(failure.get(field, "")) for field in fields).lower()


def classify_learning_failure(
    failure: dict[str, Any],
    *,
    case_id: str,
    scene: str,
) -> dict[str, Any]:
    """Classify a training failure into the narrowest safe promotion target."""

    text = _failure_text(failure)
    if any(token in text for token in ("链路", "pipeline", "delivery", "跳过", "误请", "reference_match")):
        category = "pipeline"
        target = "docs/training/pipeline-changelog.md"
        scope = "global_pipeline"
    elif any(
        token in text
        for token in ("方法论", "反模式", "forbidden", "closed_outer_shell", "missing_required_parts", "probe")
    ):
        category = "core_probe_candidate"
        target = "core/verification/training_geometry_audit.py"
        scope = "global_core"
    elif any(token in text for token in ("场景", "家装", "scene", "vocabulary", "词汇", "product family")):
        category = "scene_rule"
        target = f"agents/{scene}/rules.md"
        scope = "scene"
    elif any(token in text for token in ("几何", "geometry", "尺寸", "断线", "style", "visual")):
        category = "case_geometry"
        target = f"projects/{case_id}/expected/audit_checklist.json"
        scope = "case"
    else:
        category = "case_memory"
        target = f"projects/{case_id}/feedback.md"
        scope = "case"

    return {
        "category": category,
        "scope": scope,
        "promotion_target": target,
        "requires_human_review": category != "case_memory",
    }


def write_learning_promotion_report(
    case_dir: Path,
    round_id: str | int,
    failure: dict[str, Any],
    *,
    scene: str,
) -> Path:
    case_dir = Path(case_dir)
    round_name = _round_prefix(round_id)
    case_id = case_dir.name
    decision = classify_learning_failure(failure, case_id=case_id, scene=scene)
    promotion_gate = build_failure_promotion_gate(failure=failure, decision=decision)
    report = {
        "case_id": case_id,
        "round": round_name,
        "scene": scene,
        "failure": failure,
        "decision": decision,
        "promotionGate": promotion_gate,
        "mutated_targets": [],
        "notes": [
            "This report records promotion intent only.",
            "Apply target edits in a separate reviewed package.",
        ],
    }
    output_path = case_dir / "runs" / f"{round_name}_learning_promotion.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        return None, f"{path.name}: invalid JSON ({exc.msg})"
    if not isinstance(data, dict):
        return None, f"{path.name}: JSON root must be an object"
    return data, None


def _case_relative_file(case_dir: Path, rel_path: str) -> Path | None:
    candidate = (case_dir / rel_path).resolve()
    try:
        candidate.relative_to(case_dir.resolve())
    except ValueError:
        return None
    return candidate


def _style_compare_is_pending(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    return "pending execution" in text or "- [ ]" in text or "not yet executed" in text


def _check_style_target_contract(
    case_dir: Path,
    visual_parts: dict[str, Any],
    blocking: list[str],
) -> None:
    style_target = visual_parts.get("style_target")
    if not isinstance(style_target, str) or not style_target.strip():
        blocking.append("style_target_missing")
        return

    target_path = _case_relative_file(case_dir, style_target)
    if target_path is None:
        blocking.append("style_target_outside_case")
    elif not target_path.is_file():
        blocking.append(f"style_target_file_missing:{style_target}")

    source = visual_parts.get("style_target_source")
    if source not in {"reference_crop", "user_reference", "reference_screenshot"}:
        blocking.append("style_target_source_not_reference_derived")

    evidence = visual_parts.get("style_target_evidence")
    if not isinstance(evidence, dict):
        blocking.append("style_target_evidence_missing")
        return

    if evidence.get("generated") is True:
        blocking.append("generated_style_target_forbidden")
    if evidence.get("derived_from_real_cad_screenshot") is not True:
        blocking.append("style_target_not_real_cad_screenshot")

    source_image = evidence.get("source_image")
    if not isinstance(source_image, str) or not source_image.strip():
        blocking.append("style_target_source_image_missing")
    else:
        source_path = _case_relative_file(case_dir, source_image)
        if source_path is None:
            blocking.append("style_target_source_image_outside_case")
        elif not source_path.is_file():
            blocking.append(f"style_target_source_image_file_missing:{source_image}")


def _required_artifacts(round_name: str, stage: str) -> list[tuple[str, Path]]:
    if stage == "visual_contract":
        return [
            ("feedback", Path("feedback.md")),
            ("visual_parts", Path("runs") / f"{round_name}_visual_parts.json"),
            ("style_compare", Path("runs") / f"{round_name}_style_compare.md"),
            ("agent_review", Path("runs") / f"{round_name}_agent_review.json"),
        ]
    return [
        ("feedback", Path("feedback.md")),
        ("execution_summary", Path("runs") / f"{round_name}_execution_summary.json"),
        ("geometry_audit", Path("runs") / f"{round_name}_geometry_audit.json"),
        ("style_compare", Path("runs") / f"{round_name}_style_compare.md"),
        ("agent_review", Path("runs") / f"{round_name}_agent_review.json"),
        ("preview", Path("runs") / f"{round_name}_preview.png"),
    ]


def run_training_round_gate(
    case_dir: Path,
    round_id: str | int,
    *,
    stage: str = "visual_contract",
) -> dict[str, Any]:
    if stage not in ROUND_GATE_STAGES:
        raise ValueError(f"Unsupported stage: {stage}")

    case_dir = Path(case_dir)
    round_name = _round_prefix(round_id)
    missing: list[str] = []
    blocking: list[str] = []
    parse_errors: list[str] = []

    for _, rel_path in _required_artifacts(round_name, stage):
        path = case_dir / rel_path
        if not path.is_file():
            missing.append(rel_path.name)

    if not missing and stage == "visual_contract":
        visual_parts_path = case_dir / "runs" / f"{round_name}_visual_parts.json"
        visual_parts, error = _read_json(visual_parts_path)
        if error:
            parse_errors.append(error)
        elif not visual_parts or not visual_parts.get("object") or not visual_parts.get("parts"):
            blocking.append("visual_parts_incomplete")
        else:
            _check_style_target_contract(case_dir, visual_parts, blocking)

    if not missing and stage == "delivery":
        audit_path = case_dir / "runs" / f"{round_name}_geometry_audit.json"
        audit, error = _read_json(audit_path)
        if error:
            parse_errors.append(error)
        elif not audit or audit.get("audit_pass") is not True:
            blocking.append("audit_not_passed")

        review_path = case_dir / "runs" / f"{round_name}_agent_review.json"
        review, error = _read_json(review_path)
        if error:
            parse_errors.append(error)
        elif not review or review.get("delivery_allowed") is not True:
            blocking.append("delivery_not_allowed")

        style_compare_path = case_dir / "runs" / f"{round_name}_style_compare.md"
        if _style_compare_is_pending(style_compare_path):
            blocking.append("style_compare_pending")

    status = "pass" if not missing and not blocking and not parse_errors else "fail"
    return {
        "status": status,
        "case_id": case_dir.name,
        "round": round_name,
        "stage": stage,
        "missing_artifacts": missing,
        "blocking_reasons": blocking,
        "parse_errors": parse_errors,
    }
