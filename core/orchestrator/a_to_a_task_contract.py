"""A-to-A task contract gates for orchestration-critical agent outputs."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


PASS_STATUSES = frozenset({"pass", "ready", "ok", "complete", "complete_for_current_scope"})
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_MANIFEST_PATH = PROJECT_ROOT / "agents" / "pipeline" / "pipeline_manifest.json"
MAIN_AGENT_GATE = "main_agent_dispatch_awareness"
HIGH_RISK_TASK_KINDS = frozenset(
    {
        "system_asset_sedimentation",
        "asset_dwg_layout",
        "visual_layout_review",
        "visual_acceptance_review",
        "design_stage",
        "style_candidate_generation",
        "design_review",
    }
)

ASSET_AGENT_GATES: dict[str, str] = {
    "pipeline_asset_governor": "asset_governance",
    "pipeline_asset_librarian": "asset_library_indexing",
    "pipeline_asset_dwg_curator": "asset_dwg_curation",
    "pipeline_asset_reuse_auditor": "asset_reuse_audit",
}
VISUAL_LAYOUT_AGENT = "pipeline_visual_layout_reviewer"
VISUAL_LAYOUT_GATE = "visual_layout_review"
VISUAL_ACCEPTANCE_AGENT = "pipeline_visual_acceptance_reviewer"
VISUAL_ACCEPTANCE_GATE = "visual_acceptance_review"
DESIGN_DIRECTOR_AGENT = "pipeline_design_director"
STYLE_GENERATOR_AGENT = "pipeline_style_generator"
DESIGN_REVIEWER_AGENT = "pipeline_design_reviewer"
DESIGN_INTELLIGENCE_GATE = "design_intelligence"
DESIGN_AGENT_GATES: dict[str, str] = {
    DESIGN_DIRECTOR_AGENT: DESIGN_INTELLIGENCE_GATE,
    STYLE_GENERATOR_AGENT: DESIGN_INTELLIGENCE_GATE,
    DESIGN_REVIEWER_AGENT: DESIGN_INTELLIGENCE_GATE,
}
VISUAL_LAYOUT_CHECKS = (
    "layoutMatchesMetaphor",
    "primaryShelvesClear",
    "layoutReadabilityAcceptable",
    "aisleClearanceAcceptable",
    "contentDensityAcceptable",
    "sourceProofRolesSeparated",
    "layerSemanticsAcceptable",
    "futureExpansionClear",
    "retrievalPathReadable",
    "visualNoiseAcceptable",
    "nonScreenshotEvidenceChecked",
)
MODEL_BACKED_VISUAL_REVIEW_KEY = "modelBackedReview"
VISUAL_ACCEPTANCE_CHECKS = (
    "aestheticAcceptable",
    "textReadable",
    "noMojibake",
    "noSevereOverlap",
    "noSevereClipping",
    "alignmentAcceptable",
    "contentMatchesIntent",
    "reusableOutputLikely",
    "evidenceBoundaryRespected",
    "nonScreenshotEvidenceChecked",
)
MODEL_BACKED_VISUAL_ACCEPTANCE_KEY = "modelBackedVisualAcceptance"

ASSET_TERMS = (
    "system asset",
    "asset library",
    "standard asset",
    "asset dwg",
    "native dwg",
    "dwg",
    "系统资产",
    "资产库",
    "通用资产",
    "底座资产",
    "原生资产",
)
SEDIMENTATION_TERMS = (
    "sediment",
    "promote asset",
    "systemize asset",
    "收进资产库",
    "收入资产库",
    "沉淀",
    "作为通用资产",
    "作为系统资产",
)
VISUAL_LAYOUT_TERMS = (
    "warehouse",
    "shelf",
    "rack",
    "layout",
    "circulation",
    "expandable",
    "display form",
    "visual review",
    "仓库",
    "货架",
    "置物架",
    "货位",
    "动线",
    "排版",
    "布局",
    "展示形式",
    "可扩展",
    "分类分位置",
    "工作台",
    "索引",
)
VISUAL_ACCEPTANCE_TERMS = (
    "visual acceptance",
    "visual review",
    "visible quality",
    "readability review",
    "aesthetic",
    "overlap",
    "clipping",
    "mojibake",
    "user acceptance",
    "acceptance review",
    "acceptance gate",
    "视觉验收",
    "视觉复审",
    "用户可见验收",
    "可见质量",
    "美观度",
    "美观",
    "遮挡",
    "裁剪",
    "贴边",
    "乱码",
    "可复用",
    "用户验收",
)
DESIGN_STAGE_TERMS = (
    "design strategy",
    "design director",
    "designer judgment",
    "professional designer",
    "设计策略",
    "设计判断",
    "设计意图",
    "专业设计师",
    "先构思",
    "构思",
)
STYLE_CANDIDATE_TERMS = (
    "new style",
    "creative expression",
    "style candidate",
    "candidate comparison",
    "dimension style",
    "a/b/c",
    "abc",
    "three candidates",
    "three options",
    "新样式",
    "创造性表达",
    "创意表达",
    "方案候选",
    "候选方案",
    "多候选",
    "三套",
    "三种",
    "a/b/c",
    "A/B/C",
    "尺寸样式",
    "表达方案",
    "风格候选",
)
DESIGN_REVIEW_TERMS = (
    "design review",
    "after cad readback",
    "after readback",
    "candidate comparison after render",
    "设计复核",
    "专业复核",
    "回读后",
    "readback 后",
    "落图后复核",
)
ACTIONABLE_DESIGN_REQUEST_KINDS = frozenset({"draw", "layout", "proposal", "project_sample"})
ACTIONABLE_DESIGN_TERMS = (
    "draw",
    "generate",
    "create",
    "make",
    "build",
    "render",
    "画",
    "生成",
    "落图",
    "绘制",
    "做一个",
    "做成",
)
SEMANTIC_CONTRACT_GUIDANCE_TERMS = (
    "semantic contract",
    "semantic decomposition",
    "semantic split",
    "not a hard command",
    "not a fixed command",
    "cortex",
    "cli layer",
    "dialog",
    "语义合同",
    "语义拆解",
    "语义进行拆解",
    "精确拆分",
    "精确拆解",
    "不要当做死命令",
    "不要当作死命令",
    "不是死命令",
    "不当做死命令",
    "不当作死命令",
    "提醒",
    "如果系统已经做到",
    "对话框",
    "CLI层面",
    "CLI 层面",
    "Cortex",
)
SEMANTIC_QUESTION_TERMS = (
    "is it",
    "should i",
    "should you",
    "must you",
    "rule",
    "rules",
    "question",
    "answer",
    "是不是",
    "是否",
    "会不会",
    "要不要",
    "必须",
    "规则",
    "口径",
    "先回答",
    "问一下",
    "？",
    "?",
)
SEMANTIC_ANALYSIS_ONLY_TERMS = (
    "semantic analysis only",
    "analyze semantics",
    "split semantics",
    "先拆解",
    "先分析",
    "帮我拆解语义",
    "拆解语义",
    "语义拆解",
    "先把语义",
    "先在对话框",
    "先在这里",
)
NO_EXECUTION_TERMS = (
    "do not execute",
    "don't execute",
    "do not draw",
    "don't draw",
    "analysis only",
    "不要执行",
    "不用执行",
    "不要落图",
    "不用落图",
    "先不要落图",
    "不要生成方案",
    "不用生成方案",
    "先别画",
    "先不画",
)
STYLE_RELAXATION_TERMS = (
    "not every time",
    "not always",
    "do not always",
    "don't always",
    "no abc",
    "no a/b/c",
    "no multiple options",
    "no multiple candidates",
    "不一定每次",
    "不一定都",
    "不需要每次",
    "不用每次",
    "不要每次",
    "无需每次",
    "不需要 A/B/C",
    "不需要A/B/C",
    "不用 A/B/C",
    "不用A/B/C",
    "不要 A/B/C",
    "不要A/B/C",
    "不需要 ABC",
    "不需要ABC",
    "不用 ABC",
    "不用ABC",
    "不要 ABC",
    "不要ABC",
    "不需要多方案",
    "不用多方案",
    "不要多方案",
    "无需多方案",
    "不需要多候选",
    "不用多候选",
    "不要多候选",
    "不需要三套",
    "不用三套",
    "不要三套",
    "不需要三种",
    "不用三种",
    "不要三种",
    "不要当做死命令",
    "不要当作死命令",
)
CREATIVITY_SUPPRESSION_TERMS = (
    "no creativity",
    "do not be creative",
    "don't be creative",
    "no creative expression",
    "不要创造性",
    "不用创造性",
    "不要创意",
    "不用创意",
    "不要发挥",
    "别发挥",
    "不要创造性发挥",
)
STYLE_EXPLICIT_MULTI_TERMS = (
    "a/b/c",
    "abc",
    "three candidates",
    "three options",
    "multiple candidates",
    "multiple options",
    "candidate comparison",
    "style candidate",
    "A/B/C",
    "三套",
    "三种",
    "多候选",
    "多方案",
    "方案候选",
    "候选方案",
    "风格候选",
    "让我选",
    "请我选",
    "供我选择",
    "发后选",
)
TWO_CANDIDATE_TERMS = (
    "two candidates",
    "two options",
    "2 candidates",
    "2 options",
    "2 个",
    "2个",
    "2 套",
    "2套",
    "2 种",
    "2种",
    "两个方案",
    "两个尺寸",
    "两套",
    "两种",
    "两个",
)
THREE_CANDIDATE_TERMS = (
    "three candidates",
    "three options",
    "3 candidates",
    "3 options",
    "3 个",
    "3个",
    "3 套",
    "3套",
    "3 种",
    "3种",
    "a/b/c",
    "abc",
    "A/B/C",
    "三个方案",
    "三套",
    "三种",
    "三个",
)
PIPELINE_AGENT_ID_PATTERN = re.compile(r"\bpipeline_[a-z0-9_]+\b")


def _request_text(context: dict[str, Any]) -> str:
    fields = [
        context.get("user_request"),
        context.get("request_kind"),
        context.get("scene_hint"),
    ]
    notes = context.get("notes", [])
    if isinstance(notes, list):
        fields.extend(notes)
    return " ".join(str(item) for item in fields if item is not None).casefold()


def _has_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term.casefold() in text for term in terms)


def _matched_terms(text: str, terms: tuple[str, ...]) -> list[str]:
    return [term for term in terms if term.casefold() in text]


def _is_actionable_design_context(context: dict[str, Any], text: str) -> bool:
    request_kind = str(context.get("request_kind", "")).casefold()
    return request_kind in ACTIONABLE_DESIGN_REQUEST_KINDS or _has_any(text, ACTIONABLE_DESIGN_TERMS)


def _is_semantic_question(text: str) -> bool:
    return _has_any(text, SEMANTIC_QUESTION_TERMS) and (
        _has_any(text, SEMANTIC_CONTRACT_GUIDANCE_TERMS)
        or _has_any(text, STYLE_CANDIDATE_TERMS)
        or _has_any(text, STYLE_EXPLICIT_MULTI_TERMS)
    )


def _is_semantic_analysis_only(text: str) -> bool:
    return _has_any(text, SEMANTIC_ANALYSIS_ONLY_TERMS) and _has_any(text, NO_EXECUTION_TERMS)


def _requested_candidate_count(text: str, *, relaxed: bool) -> tuple[int | None, str, list[str]]:
    two_matches = _matched_terms(text, TWO_CANDIDATE_TERMS)
    if two_matches:
        return 2, "numeric_or_named_options", two_matches
    three_matches = _matched_terms(text, THREE_CANDIDATE_TERMS)
    if three_matches and not relaxed:
        label_policy = "abc" if _has_any(text, ("a/b/c", "abc", "A/B/C")) else "numeric_or_named_options"
        return 3, label_policy, three_matches
    return None, "not_applicable", []


def _semantic_decomposition(
    context: dict[str, Any],
    *,
    text: str | None = None,
) -> dict[str, Any]:
    request_text = _request_text(context) if text is None else text
    actionable = _is_actionable_design_context(context, request_text)
    guidance = _has_any(request_text, SEMANTIC_CONTRACT_GUIDANCE_TERMS)
    relaxed = _has_any(request_text, STYLE_RELAXATION_TERMS)
    semantic_question = _is_semantic_question(request_text)
    semantic_analysis_only = _is_semantic_analysis_only(request_text)
    creativity_suppressed = _has_any(request_text, CREATIVITY_SUPPRESSION_TERMS)
    requested_count, label_policy, count_terms = _requested_candidate_count(request_text, relaxed=relaxed)
    explicit_multi = actionable and not semantic_question and not semantic_analysis_only and (
        (requested_count is not None and requested_count >= 2)
        or (_has_any(request_text, STYLE_EXPLICIT_MULTI_TERMS) and not relaxed)
    )
    design_hint = actionable and (
        _has_any(request_text, DESIGN_STAGE_TERMS)
        or _has_any(request_text, STYLE_CANDIDATE_TERMS)
        or _has_any(request_text, STYLE_EXPLICIT_MULTI_TERMS)
    )
    design_review = actionable and not semantic_question and not semantic_analysis_only and _has_any(
        request_text, DESIGN_REVIEW_TERMS
    )

    if semantic_question:
        request_mode = "semantic_question"
        decision = "no_design_agents"
        candidate_policy = "contextual_not_forced"
        confidence = "high"
    elif semantic_analysis_only:
        request_mode = "semantic_analysis_only"
        decision = "semantic_analysis_only"
        candidate_policy = "contextual_not_forced"
        confidence = "high"
    elif guidance and not actionable:
        request_mode = "semantic_contract_guidance"
        decision = "no_design_agents"
        candidate_policy = "contextual_not_forced"
        confidence = "high"
    elif explicit_multi:
        request_mode = "actionable_task"
        decision = "style_candidates_required"
        candidate_policy = "explicit_count" if requested_count else "explicit_multi_candidate"
        confidence = "high"
    elif design_review:
        request_mode = "actionable_task"
        decision = "design_review_required"
        candidate_policy = "respect_user_request"
        confidence = "medium"
    elif design_hint:
        request_mode = "actionable_task"
        decision = "design_strategy_required"
        candidate_policy = "single_or_auto_selected_allowed" if relaxed else "contextual_not_forced"
        confidence = "medium"
    else:
        request_mode = "actionable_task" if actionable else "general"
        decision = "no_design_agents"
        candidate_policy = "not_applicable"
        confidence = "low" if actionable else "high"

    signals: list[dict[str, Any]] = []
    for name, terms, strength in (
        ("design_stage", DESIGN_STAGE_TERMS, "hard" if decision != "no_design_agents" else "soft"),
        ("style_candidate_language", STYLE_CANDIDATE_TERMS, "hard" if explicit_multi else "soft"),
        ("design_review", DESIGN_REVIEW_TERMS, "hard" if design_review else "soft"),
        ("style_candidate_relaxation", STYLE_RELAXATION_TERMS, "soft"),
        ("candidate_count", TWO_CANDIDATE_TERMS + THREE_CANDIDATE_TERMS, "hard" if requested_count else "soft"),
        ("creativity_suppression", CREATIVITY_SUPPRESSION_TERMS, "soft"),
        ("semantic_contract_guidance", SEMANTIC_CONTRACT_GUIDANCE_TERMS, "soft"),
        ("semantic_question", SEMANTIC_QUESTION_TERMS, "soft"),
        ("semantic_analysis_only", SEMANTIC_ANALYSIS_ONLY_TERMS + NO_EXECUTION_TERMS, "soft"),
    ):
        matches = _matched_terms(request_text, terms)
        if matches:
            signals.append({"semantic": name, "strength": strength, "matchedTerms": matches})

    return {
        "schemaVersion": "a2a-semantic-decomposition/v1",
        "requestMode": request_mode,
        "signals": signals,
        "designRouting": {
            "decision": decision,
            "candidateCountPolicy": candidate_policy,
            "requestedCandidateCount": requested_count,
            "candidateLabelPolicy": label_policy,
            "countSignalTerms": count_terms,
            "creativityPolicy": "suppressed_by_user" if creativity_suppressed else "contextual_not_forced",
            "styleHintsAreCommands": False,
            "confidence": confidence,
            "reason": (
                "explicit multi-candidate request"
                if explicit_multi
                else "semantic analysis requested before execution"
                if semantic_analysis_only
                else "semantic question, not an execution request"
                if semantic_question
                else "style words are contextual hints, not mandatory A/B/C commands"
            ),
        },
    }


def _semantic_route_targets_asset(semantic_asset_route: dict[str, Any] | None) -> bool:
    if not isinstance(semantic_asset_route, dict):
        return False
    if semantic_asset_route.get("status") not in {"ready", "candidate", "needs_review"}:
        return False
    workflow = semantic_asset_route.get("workflow", {})
    if isinstance(workflow, dict) and workflow.get("reusePlans"):
        return True
    return bool(semantic_asset_route.get("assetId") or semantic_asset_route.get("matchedAssets"))


def _task_kind(context: dict[str, Any], semantic_asset_route: dict[str, Any] | None) -> tuple[str, list[str], dict[str, Any]]:
    text = _request_text(context)
    decomposition = _semantic_decomposition(context, text=text)
    is_asset = _has_any(text, ASSET_TERMS) or _semantic_route_targets_asset(semantic_asset_route)
    is_sedimentation = _has_any(text, SEDIMENTATION_TERMS)
    is_visual_layout = _has_any(text, VISUAL_LAYOUT_TERMS)

    semantics: list[str] = []
    if is_asset:
        semantics.append("system_asset")
    if is_sedimentation:
        semantics.append("asset_sedimentation")
    if is_visual_layout:
        semantics.append("visual_layout")
    is_visual_acceptance = _has_any(text, VISUAL_ACCEPTANCE_TERMS)
    if is_visual_acceptance:
        semantics.append("visual_acceptance")
    design_decision = decomposition["designRouting"]["decision"]
    is_design_stage = design_decision == "design_strategy_required"
    is_style_candidate = design_decision == "style_candidates_required"
    is_design_review = design_decision == "design_review_required"
    if decomposition["requestMode"] == "semantic_contract_guidance":
        semantics.append("semantic_contract_guidance")
    if is_design_stage:
        semantics.append("design_stage")
        if _has_any(text, STYLE_CANDIDATE_TERMS):
            semantics.append("design_style_hint")
    if is_style_candidate:
        semantics.append("style_candidate_generation")
    if is_design_review or (_is_actionable_design_context(context, text) and _has_any(text, DESIGN_REVIEW_TERMS)):
        semantics.append("design_review")

    if is_asset and is_visual_layout:
        return "asset_dwg_layout", semantics, decomposition
    if is_sedimentation:
        return "system_asset_sedimentation", semantics, decomposition
    if is_visual_layout:
        return "visual_layout_review", semantics, decomposition
    if is_visual_acceptance:
        return "visual_acceptance_review", semantics, decomposition
    if is_style_candidate:
        return "style_candidate_generation", semantics, decomposition
    if is_design_review:
        return "design_review", semantics, decomposition
    if is_design_stage:
        return "design_stage", semantics, decomposition
    return "ordinary_orchestration", semantics, decomposition


def _required_agents_for(task_kind: str) -> list[str]:
    if task_kind == "asset_dwg_layout":
        return [*ASSET_AGENT_GATES.keys(), VISUAL_LAYOUT_AGENT, VISUAL_ACCEPTANCE_AGENT]
    if task_kind == "system_asset_sedimentation":
        return list(ASSET_AGENT_GATES.keys())
    if task_kind == "visual_layout_review":
        return [VISUAL_LAYOUT_AGENT]
    if task_kind == "visual_acceptance_review":
        return [VISUAL_ACCEPTANCE_AGENT]
    if task_kind == "style_candidate_generation":
        return [DESIGN_DIRECTOR_AGENT, STYLE_GENERATOR_AGENT, DESIGN_REVIEWER_AGENT]
    if task_kind == "design_review":
        return [DESIGN_DIRECTOR_AGENT, DESIGN_REVIEWER_AGENT]
    if task_kind == "design_stage":
        return [DESIGN_DIRECTOR_AGENT]
    return []


def _base_required_agents_for(task_kind: str) -> list[str]:
    if task_kind == "asset_dwg_layout":
        return list(ASSET_AGENT_GATES.keys())
    if task_kind == "system_asset_sedimentation":
        return list(ASSET_AGENT_GATES.keys())
    if task_kind in {"design_stage", "style_candidate_generation", "design_review"}:
        return [DESIGN_DIRECTOR_AGENT]
    return []


def _hard_gates_for(required_agents: list[str]) -> list[str]:
    gates: list[str] = []
    for agent_id in required_agents:
        if agent_id == VISUAL_LAYOUT_AGENT:
            gates.append(VISUAL_LAYOUT_GATE)
        elif agent_id == VISUAL_ACCEPTANCE_AGENT:
            gates.append(VISUAL_ACCEPTANCE_GATE)
        else:
            gate = ASSET_AGENT_GATES.get(agent_id)
            if gate:
                gates.append(gate)
            design_gate = DESIGN_AGENT_GATES.get(agent_id)
            if design_gate:
                gates.append(design_gate)
    return _unique(gates)


def _load_pipeline_manifest() -> dict[str, Any]:
    try:
        return json.loads(PIPELINE_MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _registered_agent_ids(manifest: dict[str, Any]) -> set[str]:
    agents = manifest.get("agents", [])
    if not isinstance(agents, list):
        return set()
    return {str(agent.get("agent_id", "")) for agent in agents if isinstance(agent, dict) and agent.get("agent_id")}


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _agent_outputs(context: dict[str, Any]) -> dict[str, Any]:
    outputs = context.get("agent_outputs", {})
    return outputs if isinstance(outputs, dict) else {}


def _status_passes(output: dict[str, Any]) -> bool:
    return str(output.get("status", "")).casefold() in PASS_STATUSES


def _visual_layout_failures(output: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for key in VISUAL_LAYOUT_CHECKS:
        value = str(output.get(key, "")).casefold()
        if value not in PASS_STATUSES:
            failures.append(key)
    if output.get("screenshotCapturedOnly") is True:
        failures.append("screenshotCapturedOnly")
    blocking_reasons = output.get("blockingReasons")
    if blocking_reasons:
        failures.append("blockingReasons")
    model_review_required = output.get("modelBackedReviewRequired") is True
    model_review = output.get(MODEL_BACKED_VISUAL_REVIEW_KEY)
    if model_review_required and not isinstance(model_review, dict):
        failures.append(MODEL_BACKED_VISUAL_REVIEW_KEY)
    if isinstance(model_review, dict):
        model_status = str(model_review.get("status", "")).casefold()
        validation = model_review.get("validation", {})
        validation_status = str(validation.get("status", "")) if isinstance(validation, dict) else ""
        provider_status = model_review.get("modelProviderStatus", {})
        if isinstance(provider_status, dict) and (
            provider_status.get("modelUnavailable") is True
            or provider_status.get("schemaValid") is False
            or provider_status.get("blocking") is True
        ):
            failures.append(MODEL_BACKED_VISUAL_REVIEW_KEY)
        if model_status not in PASS_STATUSES or (validation_status and validation_status.casefold() not in PASS_STATUSES):
            failures.append(MODEL_BACKED_VISUAL_REVIEW_KEY)
        if model_review.get("modelInvoked") is False and model_review_required:
            failures.append(MODEL_BACKED_VISUAL_REVIEW_KEY)
    return failures


def _visual_acceptance_failures(output: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for key in VISUAL_ACCEPTANCE_CHECKS:
        value = str(output.get(key, "")).casefold()
        if value not in PASS_STATUSES:
            failures.append(key)
    if output.get("screenshotCapturedOnly") is True:
        failures.append("screenshotCapturedOnly")
    blocking_reasons = output.get("blockingReasons")
    if blocking_reasons:
        failures.append("blockingReasons")
    model_review_required = output.get("modelBackedVisualAcceptanceRequired") is True
    model_review = output.get(MODEL_BACKED_VISUAL_ACCEPTANCE_KEY)
    if model_review_required and not isinstance(model_review, dict):
        failures.append(MODEL_BACKED_VISUAL_ACCEPTANCE_KEY)
    if isinstance(model_review, dict):
        model_status = str(model_review.get("status", "")).casefold()
        validation = model_review.get("validation", {})
        validation_status = str(validation.get("status", "")) if isinstance(validation, dict) else ""
        provider_status = model_review.get("modelProviderStatus", {})
        if isinstance(provider_status, dict) and (
            provider_status.get("modelUnavailable") is True
            or provider_status.get("schemaValid") is False
            or provider_status.get("blocking") is True
        ):
            failures.append(MODEL_BACKED_VISUAL_ACCEPTANCE_KEY)
        if model_status not in PASS_STATUSES or (validation_status and validation_status.casefold() not in PASS_STATUSES):
            failures.append(MODEL_BACKED_VISUAL_ACCEPTANCE_KEY)
        if model_review.get("modelInvoked") is False and model_review_required:
            failures.append(MODEL_BACKED_VISUAL_ACCEPTANCE_KEY)
    return failures


def _requested_agent_ids(context: dict[str, Any]) -> list[str]:
    requested: list[str] = []
    explicit = context.get("additional_agent_requests", [])
    if isinstance(explicit, list):
        for item in explicit:
            if isinstance(item, str):
                requested.append(item)
            elif isinstance(item, dict) and item.get("requestedAgentId"):
                requested.append(str(item["requestedAgentId"]))
    requested.extend(PIPELINE_AGENT_ID_PATTERN.findall(_request_text(context)))
    return _unique(requested)


def _build_main_agent_self_check(
    context: dict[str, Any],
    *,
    task_kind: str,
    triggered_semantics: list[str],
) -> dict[str, Any]:
    if task_kind not in HIGH_RISK_TASK_KINDS:
        return {
            "status": "observation",
            "identity": "pipeline_orchestrator_main_agent",
            "mission": "classify request, build task contract, dispatch responsible agents, block unsupported completion claims",
            "taskUnderstanding": {"taskKind": task_kind, "triggeredSemantics": triggered_semantics, "riskLevel": "normal"},
            "responsibilityBoundary": {
                "mayDispatchAgents": True,
                "mayExecuteCad": False,
                "mayClaimCompleteWithoutAgentOutputs": False,
            },
            "knownLimits": [],
            "decisionBasis": ["request semantics", "pipeline manifest"],
        }

    self_check = {
        "status": "pass",
        "identity": "pipeline_orchestrator_main_agent",
        "mission": "classify request, build task contract, dispatch responsible agents, block unsupported completion claims",
        "taskUnderstanding": {
            "taskKind": task_kind,
            "triggeredSemantics": triggered_semantics,
            "riskLevel": "high",
        },
        "responsibilityBoundary": {
            "mayDispatchAgents": True,
            "mayExecuteCad": False,
            "mayClaimCompleteWithoutAgentOutputs": False,
        },
        "knownLimits": [
            "cannot replace CAD readback",
            "cannot approve visual layout without visual_layout_review",
            "cannot approve user-visible quality without visual_acceptance_review when requested",
            "cannot activate unregistered agents",
        ],
        "decisionBasis": [
            "request semantics",
            "semantic asset route",
            "pipeline manifest",
            "hard gate definitions",
            "agent output status",
        ],
    }
    override = context.get("main_agent_self_check_override")
    if isinstance(override, dict):
        self_check.update(override)
    return self_check


def _build_dispatch_decision(
    context: dict[str, Any],
    *,
    task_kind: str,
    triggered_semantics: list[str],
    effective_required_agents: list[str],
    registered_agents: set[str],
    missing: list[str],
    failed_gates: list[str],
) -> tuple[dict[str, Any], list[str], list[str]]:
    base_required_agents = _base_required_agents_for(task_kind)
    registered_additions: list[dict[str, str]] = []
    if VISUAL_LAYOUT_AGENT in effective_required_agents and (
        "visual_layout" in triggered_semantics or task_kind == "visual_layout_review"
    ):
        registered_additions.append(
            {
                "agentId": VISUAL_LAYOUT_AGENT,
                "reason": "visual layout semantics require warehouse/shelf readability review",
                "hardGate": VISUAL_LAYOUT_GATE,
            }
        )
    if VISUAL_ACCEPTANCE_AGENT in effective_required_agents and (
        "visual_acceptance" in triggered_semantics
        or task_kind in {"visual_acceptance_review", "asset_dwg_layout"}
    ):
        registered_additions.append(
            {
                "agentId": VISUAL_ACCEPTANCE_AGENT,
                "reason": "user-visible visual quality semantics require model-backed acceptance review",
                "hardGate": VISUAL_ACCEPTANCE_GATE,
            }
        )
    if DESIGN_DIRECTOR_AGENT in effective_required_agents and (
        "design_stage" in triggered_semantics
        or "design_style_hint" in triggered_semantics
        or "style_candidate_generation" in triggered_semantics
        or "design_review" in triggered_semantics
        or task_kind in {"design_stage", "style_candidate_generation", "design_review"}
    ):
        registered_additions.append(
            {
                "agentId": DESIGN_DIRECTOR_AGENT,
                "reason": "design/style semantics require professional design strategy before CAD_PLAN",
                "hardGate": DESIGN_INTELLIGENCE_GATE,
            }
        )
    if STYLE_GENERATOR_AGENT in effective_required_agents and (
        "style_candidate_generation" in triggered_semantics
        or task_kind in {"style_candidate_generation", "design_review"}
    ):
        registered_additions.append(
            {
                "agentId": STYLE_GENERATOR_AGENT,
                "reason": "explicit multi-candidate semantics require parameterized style generation",
                "hardGate": DESIGN_INTELLIGENCE_GATE,
            }
        )
    if DESIGN_REVIEWER_AGENT in effective_required_agents and (
        "style_candidate_generation" in triggered_semantics
        or "design_review" in triggered_semantics
        or task_kind in {"style_candidate_generation", "design_review"}
    ):
        registered_additions.append(
            {
                "agentId": DESIGN_REVIEWER_AGENT,
                "reason": "visible output or candidate comparison requires professional design review before delivery",
                "hardGate": DESIGN_INTELLIGENCE_GATE,
            }
        )

    requested_agents = _requested_agent_ids(context)
    additional_requests: list[dict[str, str]] = []
    for agent_id in requested_agents:
        if agent_id not in registered_agents:
            additional_requests.append(
                {
                    "requestedAgentId": agent_id,
                    "reason": "main agent detected a possible new responsibility role in the request",
                    "status": "needs_reviewed_package",
                }
            )

    unregistered_effective = sorted(agent_id for agent_id in effective_required_agents if agent_id not in registered_agents)
    awareness_failures: list[str] = []
    awareness_reasons: list[str] = []
    if unregistered_effective:
        awareness_failures.append(MAIN_AGENT_GATE)
        awareness_reasons.append("unregistered required agents: " + ", ".join(unregistered_effective))

    reviewed_package_required = bool(additional_requests)
    blocked_until_report = bool(missing or failed_gates or unregistered_effective or reviewed_package_required)
    status = "blocked" if blocked_until_report else "ready"
    if reviewed_package_required:
        awareness_reasons.append(
            "reviewed package required for requested agents: "
            + ", ".join(item["requestedAgentId"] for item in additional_requests)
        )

    return (
        {
            "status": status,
            "baseRequiredAgents": base_required_agents,
            "registeredAdditionalAgents": registered_additions,
            "effectiveRequiredAgents": effective_required_agents,
            "additionalAgentRequests": additional_requests,
            "blockedUntilAgentsReport": blocked_until_report,
            "reviewedPackageRequired": reviewed_package_required,
            "reasoning": [
                "high-risk semantics require explicit responsibility dispatch",
                "registered agents may become effective required agents",
                "unregistered agent needs stay reviewed-package candidates",
            ],
        },
        awareness_failures,
        awareness_reasons,
    )


def _evaluate_outputs(required_agents: list[str], outputs: dict[str, Any]) -> tuple[list[str], list[str], dict[str, Any]]:
    missing: list[str] = []
    failed_gates: list[str] = []
    summary: dict[str, Any] = {}

    for agent_id in required_agents:
        output = outputs.get(agent_id)
        if not isinstance(output, dict):
            missing.append(agent_id)
            summary[agent_id] = {"status": "missing"}
            continue

        status = str(output.get("status", "")).casefold()
        if agent_id == VISUAL_LAYOUT_AGENT:
            gate = VISUAL_LAYOUT_GATE
        elif agent_id == VISUAL_ACCEPTANCE_AGENT:
            gate = VISUAL_ACCEPTANCE_GATE
        elif agent_id in DESIGN_AGENT_GATES:
            gate = DESIGN_AGENT_GATES[agent_id]
        else:
            gate = ASSET_AGENT_GATES.get(agent_id, "")
        summary[agent_id] = {"status": status or "unknown", "gate": gate}

        if agent_id == VISUAL_LAYOUT_AGENT:
            visual_failures = _visual_layout_failures(output)
            if visual_failures:
                failed_gates.append(VISUAL_LAYOUT_GATE)
                summary[agent_id]["visualFailures"] = visual_failures
        if agent_id == VISUAL_ACCEPTANCE_AGENT:
            visual_acceptance_failures = _visual_acceptance_failures(output)
            if visual_acceptance_failures:
                failed_gates.append(VISUAL_ACCEPTANCE_GATE)
                summary[agent_id]["visualAcceptanceFailures"] = visual_acceptance_failures
        if agent_id in DESIGN_AGENT_GATES:
            design_failures = _design_agent_failures(agent_id, output)
            if design_failures:
                failed_gates.append(DESIGN_INTELLIGENCE_GATE)
                summary[agent_id]["designFailures"] = design_failures

        if not _status_passes(output):
            if gate:
                failed_gates.append(gate)
            continue

    return missing, sorted(set(failed_gates)), summary


def _missing_fields(output: dict[str, Any], required: tuple[str, ...]) -> list[str]:
    return [field for field in required if field not in output]


def _design_agent_failures(agent_id: str, output: dict[str, Any]) -> list[str]:
    if agent_id == DESIGN_DIRECTOR_AGENT:
        return _missing_fields(
            output,
            (
                "designStrategy",
                "drawingTypeDecision",
                "expressionPurpose",
                "designIntent",
                "requiredChildAgents",
                "openQuestions",
                "evidenceBoundary",
            ),
        )
    if agent_id == STYLE_GENERATOR_AGENT:
        failures = _missing_fields(
            output,
            (
                "styleDecision",
                "styleCandidates",
                "selectedStyleCandidate",
                "styleParameterGrammar",
                "candidateTradeoffs",
                "needsUserChoice",
                "styleWaiverReason",
                "candidateCountPolicy",
                "requestedCandidateCount",
                "candidateLabelPolicy",
                "creativityPolicy",
                "semanticRoutingConfidence",
            ),
        )
        style_decision = str(output.get("styleDecision", "")).casefold()
        if style_decision not in {"waived", "single", "multiple"}:
            failures.append("styleDecision_enum")
        candidates = output.get("styleCandidates")
        if isinstance(candidates, list):
            if style_decision == "waived" and len(candidates) > 0:
                failures.append("styleCandidates_waived_must_be_empty")
            elif style_decision == "single" and len(candidates) != 1:
                failures.append("styleCandidates_single_count")
            elif style_decision == "multiple" and (len(candidates) < 2 or len(candidates) > 3):
                failures.append("styleCandidates_count")
        elif "styleCandidates" not in failures:
            failures.append("styleCandidates_shape")
        if style_decision == "waived" and not str(output.get("styleWaiverReason", "")).strip():
            failures.append("styleWaiverReason_empty")
        return failures
    if agent_id == DESIGN_REVIEWER_AGENT:
        return _missing_fields(
            output,
            (
                "designReview",
                "professionalDrawingLike",
                "readability",
                "industryHabitFit",
                "scaleAndProportionFit",
                "styleCandidateFit",
                "contentMatchesDesignPurpose",
                "needsUserChoice",
                "repairOrRegenerateRecommendation",
            ),
        )
    return []


def build_a_to_a_task_contract(
    request_context: dict[str, Any],
    *,
    semantic_asset_route: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the main-agent contract that decides which child agents are mandatory."""

    task_kind, triggered_semantics, semantic_decomposition = _task_kind(request_context, semantic_asset_route)
    manifest = _load_pipeline_manifest()
    registered_agents = _registered_agent_ids(manifest)
    forced = request_context.get("force_effective_required_agents", [])
    forced_agents = [str(agent_id) for agent_id in forced] if isinstance(forced, list) else []
    required_agents = _unique([*_required_agents_for(task_kind), *forced_agents])
    hard_gates = _hard_gates_for(required_agents)
    missing, failed_gates, output_summary = _evaluate_outputs(required_agents, _agent_outputs(request_context))
    self_check = _build_main_agent_self_check(
        request_context,
        task_kind=task_kind,
        triggered_semantics=triggered_semantics,
    )
    awareness_reasons: list[str] = []
    if task_kind in HIGH_RISK_TASK_KINDS and str(self_check.get("status", "")).casefold() not in PASS_STATUSES:
        failed_gates = sorted(set([*failed_gates, MAIN_AGENT_GATE]))
        awareness_reasons.append("main agent self-check failed: " + str(self_check.get("reason", self_check.get("status"))))

    dispatch_decision, awareness_failures, dispatch_awareness_reasons = _build_dispatch_decision(
        request_context,
        task_kind=task_kind,
        triggered_semantics=triggered_semantics,
        effective_required_agents=required_agents,
        registered_agents=registered_agents,
        missing=missing,
        failed_gates=failed_gates,
    )
    if awareness_failures:
        failed_gates = sorted(set([*failed_gates, *awareness_failures]))
    awareness_reasons.extend(dispatch_awareness_reasons)

    blocking_reasons: list[str] = []
    if missing:
        blocking_reasons.append("missing required agent outputs: " + ", ".join(missing))
    if failed_gates:
        blocking_reasons.append("failed hard gates: " + ", ".join(failed_gates))
    blocking_reasons.extend(awareness_reasons)

    return {
        "version": "0.1",
        "kind": "a_to_a_task_contract",
        "taskKind": task_kind,
        "status": "blocked" if blocking_reasons else "ready",
        "triggeredSemantics": triggered_semantics,
        "semanticDecomposition": semantic_decomposition,
        "requiredAgents": required_agents,
        "mainAgentSelfCheck": self_check,
        "dispatchDecision": dispatch_decision,
        "hardGates": hard_gates,
        "missingRequiredAgents": missing,
        "failedHardGates": failed_gates,
        "blockingReasons": blocking_reasons,
        "agentOutputSummary": output_summary,
        "deliveryBoundary": {
            "mayClaimComplete": not blocking_reasons,
            "mustReportBlockedAgentGates": bool(blocking_reasons),
        },
    }
