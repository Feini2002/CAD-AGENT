from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "capability-map-data.js"


TRAINING_STAGES: list[dict[str, Any]] = [
    {"id": "not_started", "label": "未开训", "rank": 0, "note": "已进入计划视野，但还没有形成可复盘案例。"},
    {"id": "prompt_defined", "label": "目标已声明", "rank": 1, "note": "已有下一轮训练目标，等待案例验证。"},
    {"id": "case_training", "label": "案例训练中", "rank": 2, "note": "正在通过真实训练轮次验证 Prompt、规则和链路。"},
    {"id": "user_feedback_pass", "label": "用户反馈通过", "rank": 3, "note": "用户已认可当前案例效果，但仍不替代表 C 机器证明。"},
    {"id": "systemized", "label": "已沉淀", "rank": 4, "note": "经验已进入规则、检查器或资产库，可复用到下一轮。"},
]


TRAINING_STAGE_COLUMNS: list[dict[str, str]] = [
    {"id": "raw", "label": "标准图库", "shortLabel": "图库"},
    {"id": "knowledge", "label": "常识整理", "shortLabel": "常识"},
    {"id": "trained", "label": "训练沉淀", "shortLabel": "训练"},
    {"id": "system", "label": "自产资产", "shortLabel": "自产"},
]


ASSET_STATE_LABELS = {
    "empty": "未纳入",
    "planned": "计划中",
    "training": "训练中",
    "evidence": "已有证据",
    "systemized": "已沉淀",
}


AGENT_GROUP_LABELS = {
    "scene": "场景智能体",
    "pipeline": "训练流水线智能体",
    "demand": "需求侧角色",
}


AGENT_STATUS_LABELS = {
    "primary_training": "主训中",
    "active": "活跃",
    "paused": "暂停训练",
    "data_only": "仅数据角色",
}


AGENT_PROMPTS: dict[str, dict[str, Any]] = {
    "residential": {
        "name": "家装场景智能体",
        "group": "scene",
        "status": "primary_training",
        "summary": "你是家装主训场景智能体，负责把用户的家装白话、房间偏好和家具常识转成可被训练流水线消费的中文规则约束。",
        "role": "你负责把家装用户的白话需求、房间语境、家具常识和用户反馈，转成流水线可以继续训练的中文场景规则。",
        "inputs": ["用户原话和本轮训练目标", "家装场景规则、对象默认值和上轮反馈", "当前能力项的风险点和下一轮可验收目标"],
        "outputs": ["场景词汇和对象常识约束", "家具方向、贴墙、净距、组合关系等可训练偏好", "需要交给视觉语义或需求拆解智能体的提示"],
        "gates": [{"label": "边界清楚", "value": "只声明家装场景规则，不代替执行、审计或真实 CAD 证明。"}],
        "must_not": ["不得把场景偏好写成跨场景 Core 规则。", "不得把用户一句话脑补成确定尺寸或正式落图结果。"],
        "calls": ["家装规则读取", "对象默认值引用", "用户反馈归因", "训练目标拆分"],
        "tips": ["把用户指出的家装常识错误沉淀到 rules.md，而不是只改单个案例。", "优先补家具方向、贴墙、通行净距和部件语义，因为这些最影响用户观感。", "每次训练后检查是否需要新增可机器审计的规则。"],
        "docs": ["agents/residential/agent.json", "agents/residential/rules.md"],
    },
    "commercial_fitout": {
        "name": "商业空间智能体",
        "group": "scene",
        "status": "paused",
        "summary": "你是商业空间场景智能体，保留零售、接待、会议室和开放办公等规则脚手架，当前不并行主训。",
    },
    "office": {
        "name": "办公场景智能体",
        "group": "scene",
        "status": "paused",
        "summary": "你是办公场景智能体，保留办公布局、工位和会议空间偏好，当前只作为后续训练候选。",
    },
    "restaurant": {
        "name": "餐饮场景智能体",
        "group": "scene",
        "status": "paused",
        "summary": "你是餐饮场景智能体，保留堂食区、服务动线和入口避让常识，当前不并行扩面。",
    },
    "exhibition": {
        "name": "展陈场景智能体",
        "group": "scene",
        "status": "paused",
        "summary": "你是展陈场景智能体，保留展台、展墙和参观路线规则，当前不并行主训。",
    },
    "healthcare": {
        "name": "医疗场景智能体",
        "group": "scene",
        "status": "paused",
        "summary": "你是医疗场景智能体，保留医疗空间脚手架和安全边界，当前不并行主训。",
    },
    "custom": {
        "name": "自定义场景智能体",
        "group": "scene",
        "status": "paused",
        "summary": "你是自定义场景智能体，用于跨场景或模糊需求占位，默认需要人工确认边界。",
    },
    "pipeline_context_curator": {
        "name": "上下文整理智能体",
        "group": "pipeline",
        "status": "active",
        "summary": "你是上下文整理智能体，负责在每一轮训练开始前收束案例状态、用户反馈和历史噪声，避免后续智能体读错上下文。",
        "role": "你负责在训练开始前收束上下文，把当前案例、用户反馈、历史失败和待训练目标整理成干净的输入包。",
        "inputs": ["当前案例目录和轮次记录", "用户最新反馈", "训练计划表单中的能力项与失败类型", "已有规则、资产和审计结果"],
        "outputs": ["本轮上下文包", "本轮必须保留和必须忽略的信息", "需要交给后续智能体的阻塞点或缺口"],
        "gates": [{"label": "不带旧噪声", "value": "过期计划、无关失败和已废弃假设不能继续传下去。"}],
        "must_not": ["不得把历史结论当成本轮用户确认。", "不得在上下文不足时直接推动执行。"],
        "calls": ["案例上下文读取", "反馈摘要", "训练状态过滤", "源文件索引"],
    },
    "pipeline_asset_retriever": {
        "name": "资产检索智能体",
        "group": "pipeline",
        "status": "active",
        "summary": "你是资产检索智能体，负责在落图前检索标准图库、常识、自产资产和历史失败，并明确哪些只是参考证据。",
        "role": "你负责在落图前检索标准图库、对象默认值、自产资产、常识规则和历史失败，并明确哪些只是参考证据。",
        "inputs": ["用户需求和当前能力项", "标准图库、原始图库和自产资产入口", "对象默认值、场景规则和历史失败记录"],
        "outputs": ["资产与常识检索包", "命中的参考资料及其可信边界", "缺失字段、未知项和不能晋升系统能力的说明"],
        "gates": [{"label": "边界声明", "value": "命中图库或参考资料只算上游证据，不算 CAD 能力通过。"}],
        "must_not": ["不得把检索命中说成能力证明。", "不得复制厂商资产几何。", "不得跳过视觉部件契约。"],
        "calls": ["标准图库扫描", "参考资产接收", "对象默认值检索", "历史失败检索"],
    },
    "pipeline_orchestrator": {
        "name": "流程编排智能体",
        "group": "pipeline",
        "status": "active",
        "summary": "你是流程编排智能体，负责判断当前训练应停在哪个阶段、下一步该调用谁，以及是否需要阻塞或回环。",
        "role": "你负责决定本轮训练该停在哪个阶段、下一步调用哪个智能体，以及是否需要阻塞、回环或进入沉淀。",
        "inputs": ["上下文包", "训练计划状态", "各智能体产物和阻塞说明", "证据边界与用户反馈"],
        "outputs": ["下一步智能体调用顺序", "阻塞原因或回环原因", "是否允许进入落图、审计或沉淀的判断"],
        "gates": [{"label": "阶段清晰", "value": "必须说明当前停在计划、Prompt、案例训练、反馈通过还是已沉淀。"}],
        "must_not": ["不得把页面状态当成真实通过。", "不得跳过失败归因。"],
        "calls": ["训练阶段判断", "流水线调度", "阻塞判定", "回环策略"],
    },
    "pipeline_visual_intent": {
        "name": "视觉语义智能体",
        "group": "pipeline",
        "status": "active",
        "summary": "你是视觉语义智能体，负责把白话和参考图拆成部件级视觉契约，尤其要说明方向、部件、闭合关系和禁止偷懒模式。",
        "role": "你负责把用户白话、参考图和场景常识拆成部件级视觉契约，重点说明方向、部件、闭合关系和禁止偷懒模式。",
        "inputs": ["用户白话需求", "参考截图或目标图", "资产与常识检索包", "场景规则和对象默认值"],
        "outputs": ["部件级视觉契约", "方向、层级、闭合状态和贴合关系", "必须绘制与禁止绘制的视觉模式"],
        "gates": [{"label": "部件可追踪", "value": "关键部件要有编号、角色、形状和闭合状态。"}],
        "must_not": ["不得直接执行 CAD。", "不得用外框盒子冒充真实部件。", "不得把修尺寸当成修视觉语义。"],
        "calls": ["参考图语义拆解", "部件契约生成", "方向语义判断", "禁止模式生成"],
    },
    "pipeline_intent": {
        "name": "需求拆解智能体",
        "group": "pipeline",
        "status": "active",
        "summary": "你是需求拆解智能体，负责把白话和视觉契约整理成可校验的结构化意图，并决定能否进入 CAD_PLAN。",
        "role": "你负责把白话和视觉契约整理成可校验的结构化意图，并判断能不能进入 CAD_PLAN。",
        "inputs": ["上下文包", "视觉契约", "场景规则", "资产与常识检索结果", "本轮训练目标"],
        "outputs": ["结构化意图", "CAD_PLAN 候选或暂缓说明", "审计清单和不可执行原因"],
        "gates": [{"label": "意图完整", "value": "对象、尺寸、方向、基点、图层和证据边界要能被下一步读取。"}],
        "must_not": ["不得把自然语言直接跳到 CAD。", "不得省略 validate 和 dry-run 前置条件。"],
        "calls": ["结构化意图生成", "CAD_PLAN 生成前检查", "Schema 对齐", "审计清单生成"],
    },
    "pipeline_execute": {
        "name": "落图执行智能体",
        "group": "pipeline",
        "status": "active",
        "summary": "你是落图执行智能体，只能按已声明的 CAD_PLAN 或 visual_parts 写入 CODEX_PREVIEW，不临场发明对象。",
        "role": "你负责把已经声明并校验过的 CAD_PLAN 或 visual_parts 落到 CODEX_PREVIEW，只执行计划内对象，不临场发明。",
        "inputs": ["通过校验的 CAD_PLAN 或 visual_parts", "可执行尺寸、基点、图层和对象清单", "write guard 与预览图层约束"],
        "outputs": ["执行摘要", "创建对象、图层和 handles 回读线索", "未执行、阻塞或需审计的说明"],
        "gates": [{"label": "只写预览", "value": "默认只写 CODEX_PREVIEW，不保存或覆盖 DWG。"}],
        "must_not": ["不得保存或覆盖 DWG。", "不得修改正式图层。", "不得跳过 validate / dry-run。", "不得绘制未在计划中声明的结构。"],
        "calls": ["CAD_PLAN 执行入口", "CODEX_PREVIEW 写入保护", "AutoCAD COM / CAD-MCP 执行桥接", "执行摘要回写"],
    },
    "pipeline_audit": {
        "name": "机器审计智能体",
        "group": "pipeline",
        "status": "active",
        "summary": "你是机器审计智能体，负责分开判断几何、语义、图层、标注和用户可见效果，不能把机器绿当成最终验收。",
        "role": "你负责把机器审计、几何回读、图层、标注和用户可见效果分开判断，指出本轮是否还需要修。",
        "inputs": ["执行摘要", "handles 回读或截图", "CAD_PLAN / visual_parts", "成功门槛和不通过边界"],
        "outputs": ["机器审计结论", "用户可见风险", "需要修复的根因和下一步证据要求"],
        "gates": [{"label": "不混口径", "value": "机器绿、用户认可和表 C 指标必须分开说。"}],
        "must_not": ["不得把机器审计通过当最终验收。", "不得只报数字不说明用户该看哪里。"],
        "calls": ["几何回读", "截图检查", "图层审计", "失败归因"],
    },
    "pipeline_repair": {
        "name": "修复回环智能体",
        "group": "pipeline",
        "status": "active",
        "summary": "你是修复回环智能体，负责基于根因做最小修复，并把修复后的结果重新送回执行和审计。",
        "role": "你负责基于审计根因做最小修复，把修复说明回送执行和审计，而不是无边界重画。",
        "inputs": ["审计失败点", "原始 CAD_PLAN / visual_parts", "可修复范围和禁止改动范围", "用户反馈"],
        "outputs": ["修复计划", "修改后的结构化意图或 CAD_PLAN", "需要重新执行与审计的证据清单"],
        "gates": [{"label": "最小修复", "value": "只改根因相关内容，不扩大范围。"}],
        "must_not": ["不得靠反复改尺寸掩盖语义错误。", "不得把未验证修复交付给用户。"],
        "calls": ["失败根因定位", "CAD_PLAN 最小修复", "回归审计触发"],
    },
    "pipeline_delivery": {
        "name": "交付汇报智能体",
        "group": "pipeline",
        "status": "active",
        "summary": "你是交付汇报智能体，负责用低噪声中文说明本轮结论、证据边界和用户最该验收的位置。",
        "role": "你负责用低噪声中文交付本轮训练结论、证据路径、没证明的边界和用户最该验收的位置。",
        "inputs": ["审计结果", "截图或回读证据", "训练目标", "失败沉淀建议", "用户反馈入口"],
        "outputs": ["本轮结论", "相对上一轮变化", "证据证明了什么、没证明什么", "用户验收重点"],
        "gates": [{"label": "先说结论", "value": "训练期交付先讲本轮结果，再讲证据和边界。"}],
        "must_not": ["不得用表格堆满普通训练交付。", "不得暗示真实 CAD 能力已经由训练页证明。"],
        "calls": ["训练交付模板", "证据路径整理", "用户验收提示", "边界说明"],
    },
    "pipeline_learning_promoter": {
        "name": "训练沉淀智能体",
        "group": "pipeline",
        "status": "active",
        "summary": "你是训练沉淀智能体，负责把失败和用户反馈分流到案例、场景规则、pipeline、Core 检查器或系统资产库。",
        "role": "你负责把失败、通过经验和用户反馈分流到案例反馈、场景规则、pipeline 规则、Core 检查器或系统资产库。",
        "inputs": ["审计与用户反馈", "失败根因", "是否重复出现", "可晋升的检查器或资产候选"],
        "outputs": ["沉淀位置建议", "下一轮 Prompt 调整点", "是否允许晋升规则、测试或资产库的判断"],
        "gates": [{"label": "先分层", "value": "单案例问题留在案例，重复问题才考虑规则或 Core。"}],
        "must_not": ["不得把一次失败直接污染通用规则。", "不得把参考图库直接晋升自产资产。"],
        "calls": ["训练错误台账", "场景规则沉淀", "Core 检查器候选", "系统资产晋升判断"],
    },
    "demand_side_roles": {
        "name": "需求侧角色智能体",
        "group": "demand",
        "status": "data_only",
        "summary": "你是需求侧角色数据智能体，只负责生成更像真实用户的训练需求和 benchmark，不直接参与 CAD 执行。",
        "role": "你负责生成更像真实用户的训练需求、角色口吻和 benchmark 场景，只作为输入数据，不参与 CAD 执行。",
        "inputs": ["场景 ID", "用户角色", "需求焦点", "样例请求和验收偏好"],
        "outputs": ["自然语言训练需求", "用户角色画像", "能力目标和验收关注点"],
        "gates": [{"label": "用途边界", "value": "只生成需求，不直接绘图，也不替代真实用户反馈。"}],
        "must_not": ["不得当作执行智能体。", "不得替代真实用户反馈。"],
        "calls": ["需求样本生成", "角色口吻生成", "benchmark 场景生成"],
    },
}


SCENE_DEFAULT_INPUTS = ["当前场景规则", "用户白话需求", "训练计划中的能力项"]
SCENE_DEFAULT_OUTPUTS = ["场景词汇解释", "对象默认偏好", "交给流水线的训练提示"]
SCENE_DEFAULT_GATES = [{"label": "保持轻量", "value": "只补场景差异，不把场景偏好写进 Core。"}]
SCENE_DEFAULT_MUST_NOT = ["不得直接执行 CAD。", "不得替代主训家装案例。"]
SCENE_DEFAULT_CALLS = ["场景规则读取", "训练需求解释"]


CAPABILITIES: list[dict[str, Any]] = [
    {"id": "sofa", "name": "沙发", "kind": "object", "group": "基础家具", "priority": "P0", "owner": "residential", "pipeline": ["pipeline_asset_retriever", "pipeline_visual_intent", "pipeline_intent", "pipeline_execute", "pipeline_audit", "pipeline_repair", "pipeline_learning_promoter"], "focus": "方向语义、扶手/靠背/坐垫部件、共享边去重", "weaknesses": ["sofa_direction_semantics_inverted", "duplicate_shared_edges"], "next": "开一轮沙发方向语义与贴合关系训练"},
    {"id": "tea-table", "name": "茶几", "kind": "object", "group": "基础家具", "priority": "P0", "owner": "residential", "pipeline": ["pipeline_asset_retriever", "pipeline_intent", "pipeline_execute", "pipeline_audit"], "focus": "比例、与沙发组合距离、中心对齐", "weaknesses": ["retrieval_hit_as_capability"], "next": "补标准尺寸和组合关系检查"},
    {"id": "dining-table", "name": "餐桌", "kind": "object", "group": "基础家具", "priority": "P0", "owner": "residential", "pipeline": ["pipeline_asset_retriever", "pipeline_intent", "pipeline_execute", "pipeline_audit"], "focus": "桌面尺寸、椅子围合、通行净距", "weaknesses": ["silent_bbox_fallback"], "next": "训练餐桌+餐椅组合"},
    {"id": "dining-chair", "name": "餐椅", "kind": "object", "group": "基础家具", "priority": "P0", "owner": "residential", "pipeline": ["pipeline_asset_retriever", "pipeline_intent", "pipeline_execute"], "focus": "朝向、椅背表达、与桌边关系", "weaknesses": ["missing_furniture_parts"], "next": "补椅背和入座方向规则"},
    {"id": "bed", "name": "床铺", "kind": "object", "group": "基础家具", "priority": "P0", "owner": "residential", "pipeline": ["pipeline_asset_retriever", "pipeline_visual_intent", "pipeline_intent", "pipeline_execute", "pipeline_audit"], "focus": "床头方向、床垫/枕头/床头柜组合", "weaknesses": ["plan_view_role_direction_errors"], "next": "开卧室组合训练"},
    {"id": "nightstand", "name": "床头柜", "kind": "object", "group": "基础家具", "priority": "P1", "owner": "residential", "pipeline": ["pipeline_asset_retriever", "pipeline_intent", "pipeline_execute"], "focus": "成对摆放、床侧净距、比例", "weaknesses": ["size_only_repair_loop"], "next": "补床侧组合默认值"},
    {"id": "wardrobe", "name": "衣柜", "kind": "object", "group": "基础家具", "priority": "P1", "owner": "residential", "pipeline": ["pipeline_asset_retriever", "pipeline_intent", "pipeline_audit"], "focus": "开门净空、贴墙、与床通道", "weaknesses": ["machine_green_delivery"], "next": "训练衣柜开门净空 audit"},
    {"id": "tv-cabinet", "name": "电视柜", "kind": "object", "group": "基础家具", "priority": "P1", "owner": "residential", "pipeline": ["pipeline_asset_retriever", "pipeline_intent", "pipeline_execute"], "focus": "朝向、墙面关系、电视/柜比例", "weaknesses": ["clone_reference_fragments"], "next": "补客厅视线方向规则"},
    {"id": "desk", "name": "书桌", "kind": "object", "group": "基础家具", "priority": "P1", "owner": "residential", "pipeline": ["pipeline_asset_retriever", "pipeline_intent", "pipeline_execute"], "focus": "座椅空间、靠窗/靠墙偏好", "weaknesses": ["silent_bbox_fallback"], "next": "补书桌+椅组合训练"},
    {"id": "low-cabinet", "name": "矮柜", "kind": "object", "group": "基础家具", "priority": "P2", "owner": "residential", "pipeline": ["pipeline_asset_retriever", "pipeline_intent"], "focus": "低柜高度语义、墙边摆放", "weaknesses": ["retrieval_hit_as_capability"], "next": "先补对象默认值"},
    {"id": "basin", "name": "洗手台", "kind": "object", "group": "厨卫对象", "priority": "P1", "owner": "residential", "pipeline": ["pipeline_asset_retriever", "pipeline_intent", "pipeline_execute", "pipeline_audit"], "focus": "台盆、柜体、水龙头语义和卫浴墙面关系", "weaknesses": ["missing_furniture_parts"], "next": "训练卫浴对象部件表达"},
    {"id": "toilet", "name": "马桶", "kind": "object", "group": "厨卫对象", "priority": "P1", "owner": "residential", "pipeline": ["pipeline_asset_retriever", "pipeline_intent", "pipeline_execute"], "focus": "朝向、离墙尺寸、检修空间", "weaknesses": ["machine_size_drift_only"], "next": "补洁具默认净距"},
    {"id": "stove", "name": "灶台", "kind": "object", "group": "厨卫对象", "priority": "P2", "owner": "residential", "pipeline": ["pipeline_asset_retriever", "pipeline_intent"], "focus": "台面、火口、厨房操作三角", "weaknesses": ["unsupported_or_risky"], "next": "先补厨房对象 catalog"},
    {"id": "fridge", "name": "冰箱", "kind": "object", "group": "厨卫对象", "priority": "P2", "owner": "residential", "pipeline": ["pipeline_asset_retriever", "pipeline_intent"], "focus": "门开启方向、散热间距、厨房动线", "weaknesses": ["silent_bbox_fallback"], "next": "补冰箱门向和净距"},
    {"id": "wall", "name": "墙体绘制", "kind": "draw", "group": "基础绘图", "priority": "P0", "owner": "pipeline_execute", "pipeline": ["pipeline_intent", "pipeline_execute", "pipeline_audit"], "focus": "闭合轮廓、墙厚、图层归类", "weaknesses": ["duplicate_shared_edges"], "next": "强化墙线重复与开口检查"},
    {"id": "door", "name": "门绘制", "kind": "draw", "group": "基础绘图", "priority": "P0", "owner": "pipeline_execute", "pipeline": ["pipeline_intent", "pipeline_execute", "pipeline_audit"], "focus": "门洞、开启弧、门扇方向", "weaknesses": ["plan_view_role_direction_errors"], "next": "补门向语义训练"},
    {"id": "window", "name": "窗户绘制", "kind": "draw", "group": "基础绘图", "priority": "P0", "owner": "pipeline_execute", "pipeline": ["pipeline_intent", "pipeline_execute", "pipeline_audit"], "focus": "窗洞、窗线层级、墙体嵌入", "weaknesses": ["machine_green_delivery"], "next": "补窗洞与墙体关系 audit"},
    {"id": "door-opening", "name": "门洞绘制", "kind": "draw", "group": "基础绘图", "priority": "P1", "owner": "pipeline_execute", "pipeline": ["pipeline_intent", "pipeline_execute", "pipeline_audit"], "focus": "洞口扣减、门套语义、墙段连续", "weaknesses": ["duplicate_shared_edges"], "next": "训练洞口扣减检查"},
    {"id": "window-opening", "name": "窗洞绘制", "kind": "draw", "group": "基础绘图", "priority": "P1", "owner": "pipeline_execute", "pipeline": ["pipeline_intent", "pipeline_execute", "pipeline_audit"], "focus": "窗洞宽度、离地语义、墙内关系", "weaknesses": ["machine_size_drift_only"], "next": "补窗洞标准语义"},
    {"id": "room-outline", "name": "房间轮廓绘制", "kind": "draw", "group": "基础绘图", "priority": "P1", "owner": "pipeline_intent", "pipeline": ["pipeline_context_curator", "pipeline_intent", "pipeline_execute", "pipeline_audit"], "focus": "房间闭合、基点、尺寸约束", "weaknesses": ["silent_bbox_fallback"], "next": "强化房间轮廓 validate"},
    {"id": "column", "name": "柱子绘制", "kind": "draw", "group": "基础绘图", "priority": "P2", "owner": "pipeline_execute", "pipeline": ["pipeline_intent", "pipeline_execute"], "focus": "结构柱尺寸、图层、与墙体关系", "weaknesses": ["retrieval_hit_as_capability"], "next": "补柱子对象规范"},
    {"id": "furniture-layout", "name": "基础家具摆放", "kind": "draw", "group": "基础绘图", "priority": "P2", "owner": "residential", "pipeline": ["pipeline_asset_retriever", "pipeline_intent", "pipeline_execute", "pipeline_audit", "pipeline_learning_promoter"], "focus": "组合关系、通道、朝向和避让", "weaknesses": ["visual_fail_size_only_repair"], "next": "开客厅/卧室组合训练"},
    {"id": "dimension", "name": "简单尺寸标注", "kind": "annotation", "group": "标注表达", "priority": "P1", "owner": "pipeline_delivery", "pipeline": ["pipeline_intent", "pipeline_execute", "pipeline_audit", "pipeline_delivery"], "focus": "标注对象、尺寸线位置、比例和避让", "weaknesses": ["missing_annotation"], "next": "补尺寸标注检查器"},
    {"id": "text", "name": "简单文字标注", "kind": "annotation", "group": "标注表达", "priority": "P1", "owner": "pipeline_delivery", "pipeline": ["pipeline_intent", "pipeline_execute", "pipeline_delivery"], "focus": "文字内容、图层、与对象关联", "weaknesses": ["missing_annotation"], "next": "训练对象名称标注"},
    {"id": "layers", "name": "基础图层归类", "kind": "annotation", "group": "标注表达", "priority": "P2", "owner": "pipeline_audit", "pipeline": ["pipeline_execute", "pipeline_audit", "pipeline_delivery"], "focus": "CODEX_PREVIEW、正式图层保护、对象分层", "weaknesses": ["formal_layer_write_risk"], "next": "补图层归类审计"},
]


GROUP_OVERRIDES = {
    "nightstand": "储位家具",
    "wardrobe": "储位家具",
    "tv-cabinet": "储位家具",
    "low-cabinet": "储位家具",
}


FAILURE_LABELS = {
    "sofa_direction_semantics_inverted": "方向语义反了",
    "duplicate_shared_edges": "共享边重复",
    "silent_bbox_fallback": "弱资产时画空 bbox",
    "retrieval_hit_as_capability": "检索命中被当能力",
    "machine_green_delivery": "机器绿但视觉未验",
    "clone_reference_fragments": "误克隆参考碎片",
    "size_only_repair_loop": "只靠尺寸修复",
    "missing_furniture_parts": "家具部件缺失",
    "plan_view_role_direction_errors": "平面角色方向错误",
    "machine_size_drift_only": "仅尺寸漂移",
    "unsupported_or_risky": "暂不支持或风险高",
    "visual_fail_size_only_repair": "视觉失败却只调尺寸",
    "missing_annotation": "标注缺失",
    "formal_layer_write_risk": "正式图层写入风险",
}


FAILURE_NOTES = {
    "sofa_direction_semantics_inverted": "沙发硬背、软靠垫、坐垫的前后语义容易被倒置。",
    "duplicate_shared_edges": "相邻部件允许贴合，但同一 CAD 段不能重复生成。",
    "silent_bbox_fallback": "资产或常识不足时不能悄悄退化为空外框。",
    "retrieval_hit_as_capability": "检索到素材只算参考输入，不算系统能力。",
    "machine_green_delivery": "机器审计绿灯不能直接替代用户可见验收。",
    "clone_reference_fragments": "参考图不能被碎片化克隆为系统资产。",
    "size_only_repair_loop": "视觉语义错时，只调尺寸会进入无效回环。",
    "missing_furniture_parts": "对象必须拆清关键部件，不应只画外轮廓。",
    "plan_view_role_direction_errors": "平面图方向、入座方向和开门方向需要显式说明。",
    "machine_size_drift_only": "只盯尺寸漂移会漏掉语义或视觉错误。",
    "unsupported_or_risky": "高风险或未支持对象应先阻塞并补常识。",
    "visual_fail_size_only_repair": "视觉失败时应回到视觉语义智能体。",
    "missing_annotation": "标注训练要明确对象、位置、比例和避让。",
    "formal_layer_write_risk": "训练默认只写 CODEX_PREVIEW，不碰正式图层。",
}


FAILURE_WEIGHTS = {
    "sofa_direction_semantics_inverted": 92,
    "duplicate_shared_edges": 78,
    "silent_bbox_fallback": 70,
    "retrieval_hit_as_capability": 45,
    "machine_green_delivery": 50,
    "clone_reference_fragments": 58,
    "size_only_repair_loop": 64,
    "missing_furniture_parts": 72,
    "plan_view_role_direction_errors": 66,
    "machine_size_drift_only": 40,
    "unsupported_or_risky": 36,
    "visual_fail_size_only_repair": 62,
    "missing_annotation": 52,
    "formal_layer_write_risk": 34,
}


FAILURE_AGENTS = {
    "sofa_direction_semantics_inverted": ["residential", "pipeline_visual_intent", "pipeline_intent"],
    "duplicate_shared_edges": ["pipeline_execute", "pipeline_repair", "pipeline_audit"],
    "silent_bbox_fallback": ["pipeline_asset_retriever", "pipeline_intent"],
    "retrieval_hit_as_capability": ["pipeline_asset_retriever", "pipeline_learning_promoter"],
    "machine_green_delivery": ["pipeline_audit", "pipeline_delivery"],
    "clone_reference_fragments": ["pipeline_asset_retriever", "pipeline_visual_intent"],
    "size_only_repair_loop": ["pipeline_repair", "pipeline_audit"],
    "missing_furniture_parts": ["pipeline_visual_intent", "pipeline_execute", "pipeline_audit"],
    "plan_view_role_direction_errors": ["pipeline_visual_intent", "pipeline_intent", "pipeline_audit"],
    "machine_size_drift_only": ["pipeline_audit", "pipeline_repair"],
    "unsupported_or_risky": ["pipeline_asset_retriever", "pipeline_intent"],
    "visual_fail_size_only_repair": ["pipeline_repair", "pipeline_audit"],
    "missing_annotation": ["pipeline_delivery", "pipeline_audit"],
    "formal_layer_write_risk": ["pipeline_execute", "pipeline_audit"],
}


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return fallback


def unique(items: list[str]) -> list[str]:
    result: list[str] = []
    for item in items:
        if item and item not in result:
            result.append(item)
    return result


def agent_template(agent_id: str) -> dict[str, Any]:
    template = dict(AGENT_PROMPTS[agent_id])
    if "role" not in template:
        template["role"] = template["summary"]
        template["inputs"] = SCENE_DEFAULT_INPUTS
        template["outputs"] = SCENE_DEFAULT_OUTPUTS
        template["gates"] = SCENE_DEFAULT_GATES
        template["must_not"] = SCENE_DEFAULT_MUST_NOT
        template["calls"] = SCENE_DEFAULT_CALLS
        template["tips"] = ["补充场景词汇和边界时，先绑定具体案例。", "不要和当前家装主训并行抢主线。", "只有跨场景重复出现的问题才考虑沉淀到 Core。"]
        template["docs"] = [f"agents/{agent_id}/agent.json"]
    template.setdefault("tips", ["先明确输入、输出和通过门槛。", "把禁止事项写成可检查条款。", "重复失败时再晋升为测试或 Core 检查器。"])
    template.setdefault("docs", [f"agents/{agent_id}/agent.json"])
    return template


def agent_name(agent_id: str) -> str:
    return agent_template(agent_id)["name"]


def matrix_group(capability: dict[str, Any]) -> str:
    return GROUP_OVERRIDES.get(capability["id"], capability["group"])


def kind_label(kind: str, suffix: str) -> str:
    return {
        "object": f"对象{suffix}",
        "draw": f"绘图{suffix}",
        "annotation": f"标注{suffix}",
    }.get(kind, f"训练{suffix}")


def risk_items(ids: list[str]) -> list[dict[str, str]]:
    return [{"id": item, "label": FAILURE_LABELS[item], "note": FAILURE_NOTES[item]} for item in ids]


def stage_state(capability: dict[str, Any]) -> dict[str, Any]:
    if capability["id"] == "sofa":
        stage = dict(TRAINING_STAGES[2])
        stage["note"] = "沙发已有多轮家装训练上下文，本页继续把方向语义、部件和贴合关系作为下一轮目标。"
        return stage
    if capability["priority"] in {"P0", "P1"}:
        stage = dict(TRAINING_STAGES[1])
        stage["note"] = f"已在训练表单中声明下一轮目标：{capability['next']}。"
        return stage
    stage = dict(TRAINING_STAGES[0])
    stage["note"] = "已列入候选训练项，尚未进入当前主训案例。"
    return stage


def asset_state(state: str, note: str) -> dict[str, str]:
    return {"state": state, "label": ASSET_STATE_LABELS[state], "note": note}


def asset_states(capability: dict[str, Any]) -> dict[str, dict[str, str]]:
    pipeline = set(capability["pipeline"])
    raw = "planned" if "pipeline_asset_retriever" in pipeline else "empty"
    knowledge = "planned" if capability["priority"] in {"P0", "P1", "P2"} else "empty"
    if capability["id"] == "sofa":
        trained = "training"
    elif capability["priority"] in {"P0", "P1"}:
        trained = "planned"
    else:
        trained = "empty"
    system = "planned" if "pipeline_learning_promoter" in pipeline else "empty"
    return {
        "raw": asset_state(raw, "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。" if raw != "empty" else "此项当前不以标准图库接收为主。"),
        "knowledge": asset_state(knowledge, f"围绕“{capability['focus']}”整理中文常识、默认值和场景规则。" if knowledge != "empty" else "暂未绑定常识入口。"),
        "trained": asset_state(trained, f"下一轮训练目标：{capability['next']}。" if trained != "empty" else "尚未进入案例训练，先补 Prompt 或对象默认值。"),
        "system": asset_state(system, "只有经过 promotion gate、证据边界和回归检查后，才允许进入自产资产或通用规则。" if system != "empty" else "当前没有自产资产沉淀计划。"),
    }


def capability_agent_ids(capability: dict[str, Any]) -> list[str]:
    return unique([capability["owner"], *capability["pipeline"]])


def capability_catalog() -> list[dict[str, Any]]:
    rows = []
    for item in CAPABILITIES:
        agent_ids = capability_agent_ids(item)
        rows.append(
            {
                "id": item["id"],
                "name": item["name"],
                "kind": item["kind"],
                "kindLabel": kind_label(item["kind"], "能力"),
                "group": item["group"],
                "matrixGroup": matrix_group(item),
                "priority": item["priority"],
                "ownerAgentId": item["owner"],
                "ownerAgentName": agent_name(item["owner"]),
                "relatedAgentIds": agent_ids,
                "relatedAgents": [{"id": agent_id, "name": agent_name(agent_id)} for agent_id in agent_ids],
                "focus": item["focus"],
                "risks": risk_items(item["weaknesses"]),
                "nextTrainingTarget": item["next"],
            }
        )
    return rows


def training_programs() -> list[dict[str, Any]]:
    rows = []
    for item in CAPABILITIES:
        agent_ids = capability_agent_ids(item)
        state = stage_state(item)
        rows.append(
            {
                "id": f"program-{item['id']}",
                "capabilityId": item["id"],
                "name": item["name"],
                "title": f"{item['name']} · {item['next']}",
                "priority": item["priority"],
                "kind": item["kind"],
                "kindLabel": kind_label(item["kind"], "训练"),
                "group": item["group"],
                "matrixGroup": matrix_group(item),
                "ownerAgentId": item["owner"],
                "ownerAgentName": agent_name(item["owner"]),
                "responsibleAgentIds": agent_ids,
                "responsibleAgents": [{"id": agent_id, "name": agent_name(agent_id)} for agent_id in agent_ids],
                "pipeline": item["pipeline"],
                "focus": item["focus"],
                "weaknesses": risk_items(item["weaknesses"]),
                "nextTrainingTarget": item["next"],
                "stageState": state,
                "assetStates": asset_states(item),
                "trainingObjective": f"围绕“{item['focus']}”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
                "successCriteria": [
                    "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
                    "责任智能体能说清输入、输出、硬门槛和禁止事项。",
                    "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。",
                ],
                "notPassConditions": [
                    "只有计划、标签或检索命中，不能算训练通过。",
                    "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
                    "未写清失败根因和沉淀位置，不能算已沉淀。",
                ],
                "evidenceRequired": [
                    "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
                    "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
                    "训练失败时的根因、修复目标和下一轮 Prompt 调整点。",
                ],
            }
        )
    return rows


def maturity_metric(percent: int, note: str, basis: str, gap: str) -> dict[str, Any]:
    return {"percent": max(0, min(100, percent)), "note": note, "basis": basis, "gap": gap}


def agent_profiles(programs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    profiles = []
    for agent_id in AGENT_PROMPTS:
        template = agent_template(agent_id)
        related = [program for program in programs if agent_id in program["responsibleAgentIds"]]
        p0_count = sum(1 for program in related if program["priority"] == "P0")
        coverage_percent = 15 if not related else min(100, 25 + len(related) * 8 + p0_count * 6)
        call_count = len(template["calls"])
        call_percent = 82 if call_count >= 4 else 68 if call_count >= 2 else 48
        if template["status"] == "primary_training":
            evidence_percent = 68
        elif template["status"] == "active":
            evidence_percent = 46
        elif template["status"] == "data_only":
            evidence_percent = 34
        else:
            evidence_percent = 20
        operation = {
            "role": template["role"],
            "inputs": template["inputs"],
            "outputs": template["outputs"],
            "passGate": template["gates"],
            "mustNot": template["must_not"],
            "usesCore": template["calls"],
            "optimizationTips": template["tips"],
        }
        profiles.append(
            {
                "id": agent_id,
                "name": template["name"],
                "sourceName": agent_id,
                "group": template["group"],
                "groupLabel": AGENT_GROUP_LABELS[template["group"]],
                "status": template["status"],
                "statusLabel": AGENT_STATUS_LABELS[template["status"]],
                "trainingRole": template["role"],
                "roleSummary": template["summary"],
                "promptContractId": f"contract-{agent_id}",
                "ownedCapabilities": [
                    {
                        "id": program["capabilityId"],
                        "name": program["name"],
                        "priority": program["priority"],
                        "stageLabel": program["stageState"]["label"],
                        "nextTrainingTarget": program["nextTrainingTarget"],
                    }
                    for program in related
                ],
                "activeTrainingItems": [
                    {
                        "id": program["id"],
                        "capabilityId": program["capabilityId"],
                        "name": program["name"],
                        "priority": program["priority"],
                        "nextTrainingTarget": program["nextTrainingTarget"],
                    }
                    for program in related[:8]
                ],
                "promptCompleteness": maturity_metric(100, "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。", "5/5 类契约已声明", "下一轮可把描述写得更贴近真实训练话术。"),
                "callMaturity": maturity_metric(call_percent, f"已显式关联 {call_count} 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。", f"显式调用 {call_count} 项", "缺口：把调用结果和审计证据继续连起来。"),
                "trainingCoverage": maturity_metric(coverage_percent, f"关联 {len(related)} 个训练计划项，其中 P0 {p0_count} 个；表示训练表单覆盖度。", f"{len(related)} 个训练计划 / P0 {p0_count} 个", "缺口：继续把训练项和失败类型做点对点对应。"),
                "evidenceMaturity": maturity_metric(evidence_percent, f"训练状态：{AGENT_STATUS_LABELS[template['status']]}。这不是表 C 真实 CAD 机器指标。", f"训练状态：{AGENT_STATUS_LABELS[template['status']]}", "缺口：需要更多案例证据、用户反馈和可回读产物。"),
                "maturity": {},
                "docs": template["docs"],
                "operation": operation,
            }
        )
        profiles[-1]["maturity"] = {
            "promptCompleteness": profiles[-1]["promptCompleteness"],
            "callMaturity": profiles[-1]["callMaturity"],
            "trainingCoverage": profiles[-1]["trainingCoverage"],
            "evidenceMaturity": profiles[-1]["evidenceMaturity"],
        }
    return profiles


def prompt_boundary(agent_id: str) -> list[str]:
    template = agent_template(agent_id)
    if template["group"] == "scene":
        return [
            "负责提供场景词汇、对象常识、默认偏好和用户反馈教训。",
            "不直接执行 CAD，也不替代流水线里的审计、修复和交付。",
            "适合训练用户白话到场景规则的映射，例如家具方向、贴墙和净距。",
        ]
    if agent_id == "pipeline_execute":
        return [
            "只把已声明的 CAD_PLAN 或 visual_parts 落到 CODEX_PREVIEW。",
            "不得临场发明对象、尺寸或正式图层写入行为。",
            "执行结果必须能被 audit 和 repair 回读。",
        ]
    if agent_id == "pipeline_audit":
        return [
            "负责判断几何、语义、图层、标注和视觉可验收性。",
            "机器绿不能单独等于用户验收通过。",
            "发现重复失败时要给出可晋升检查器的候选。",
        ]
    if template["group"] == "demand":
        return [
            "只生成需求、角色口吻和 benchmark 场景。",
            "不直接绘图，不替代真实用户反馈。",
            "用于让训练输入更像真实白话需求。",
        ]
    return [
        "只负责训练流水线中的本环节判断和产物。",
        "输入不足时必须声明缺口、阻塞或下一步，而不是硬推到 CAD。",
        "输出必须能被下一环节读取，并保留证据边界。",
    ]


def prompt_contracts() -> list[dict[str, Any]]:
    rows = []
    for agent_id in AGENT_PROMPTS:
        template = agent_template(agent_id)
        rows.append(
            {
                "id": f"contract-{agent_id}",
                "agentId": agent_id,
                "agentName": template["name"],
                "sourceName": agent_id,
                "promptSummary": template["summary"],
                "roleSetting": template["role"],
                "responsibilityBoundary": prompt_boundary(agent_id),
                "inputRequirements": template["inputs"],
                "outputFormat": template["outputs"],
                "hardGates": template["gates"],
                "mustNot": template["must_not"],
                "callCapabilities": template["calls"],
                "adjustablePromptPoints": template["tips"],
                "sourceRefs": [{"path": path, "title": "源文件", "kind": "文件", "meaning": "用于维护该智能体的中文 Prompt 契约。", "changeGuide": "修改后重新生成本页数据并复查页面。"} for path in template["docs"]],
                "evidenceBoundary": "本契约只帮助前端展示和训练 Prompt，不代表表 C 真实 CAD 几何通过。",
            }
        )
    return rows


def failure_modes() -> list[dict[str, Any]]:
    return [
        {
            "id": key,
            "label": FAILURE_LABELS[key],
            "weight": FAILURE_WEIGHTS[key],
            "agents": FAILURE_AGENTS[key],
            "note": FAILURE_NOTES[key],
        }
        for key in FAILURE_WEIGHTS
    ]


def table_c_boundary() -> dict[str, Any]:
    path = ROOT / "output" / "validation_runs" / "capability-lab" / "cad_capability_coverage.json"
    data = read_json(path, {})
    summary = data.get("summary", {})
    return {
        "label": "表 C 真实 CAD 机器快照",
        "generatedAt": data.get("generated_at", ""),
        "sourcePath": "output/validation_runs/capability-lab/cad_capability_coverage.json",
        "cadProofCoveragePercent": summary.get("cad_proof_coverage_percent", 0),
        "cadStrengthIndexPercent": summary.get("cad_strength_index_percent", 0),
        "sceneFragmentStrengthPercent": summary.get("scene_fragment_strength_percent", 0),
        "showcaseReadinessPercent": summary.get("showcase_readiness_percent", 0),
        "headlinePercent": summary.get("cad_strength_headline_percent", 0),
        "highestProvenLadder": summary.get("highest_proven_ladder_level", "unknown"),
        "note": "这是 registry 和 coverage JSON 的机器指标快照，只能说明表 C 口径；不能和训练计划成熟度、智能体 Prompt 成熟度混算。",
    }


def learning_routes() -> list[dict[str, str]]:
    return [
        {"from": "单案例失败", "to": "projects/<case>/feedback.md", "desc": "先留在案例反馈，不立即污染通用规则。"},
        {"from": "重复失败", "to": "docs/training/training-errors.md", "desc": "记录模式、根因和下一轮训练约束。"},
        {"from": "场景常识", "to": "agents/<scene>/rules.md", "desc": "比如家装家具方向、组合关系、默认净距。"},
        {"from": "链路硬门槛", "to": "agents/pipeline/*/agent.json", "desc": "比如禁止 bbox fallback、必须声明证据边界。"},
        {"from": "可机器检查", "to": "core/verification 或 tests", "desc": "重复问题应晋升为检查器或回归测试。"},
        {"from": "可复用图块", "to": "libraries/system_library", "desc": "只有经过 promotion gate 的资产才进入自有图库。"},
    ]


def sources() -> list[dict[str, str]]:
    return [
        {"title": "场景 Agent", "path": "agents/<scene>/agent.json + rules.md", "desc": "领域词汇、偏好、场景边界和训练状态。"},
        {"title": "Pipeline Agent", "path": "agents/pipeline/*/agent.json", "desc": "上下文、资产、视觉意图、执行、审计、修复、沉淀等链路职责。"},
        {"title": "能力覆盖快照", "path": "output/validation_runs/capability-lab/cad_capability_coverage.json", "desc": "表 C 机器指标来源，不和本页阶段混用。"},
        {"title": "标准图库 raw", "path": "standard_cad_library_raw/", "desc": "外来参考素材入口，默认 reference_only，不直接算系统能力。"},
        {"title": "训练反馈", "path": "projects/<case>/feedback.md + docs/training/training-errors.md", "desc": "点对点训练和失败复盘的沉淀位置。"},
    ]


def build_data() -> dict[str, Any]:
    programs = training_programs()
    profiles = agent_profiles(programs)
    return {
        "schemaVersion": 2,
        "generatedAt": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "trainingStages": TRAINING_STAGES,
        "trainingStageColumns": TRAINING_STAGE_COLUMNS,
        "capabilityCatalog": capability_catalog(),
        "trainingPrograms": programs,
        "agentProfiles": profiles,
        "promptContracts": prompt_contracts(),
        "tableCBoundary": table_c_boundary(),
        "coverageSnapshot": table_c_boundary(),
        "stages": TRAINING_STAGE_COLUMNS,
        "agents": profiles,
        "capabilities": programs,
        "failureModes": failure_modes(),
        "learningRoutes": learning_routes(),
        "sources": sources(),
        "pipelineFlow": [
            {"id": "context", "title": "上下文整理", "desc": "先恢复上下文，过滤旧状态和历史噪声。"},
            {"id": "asset", "title": "资产检索", "desc": "查标准图库、常识、历史失败和证据边界。"},
            {"id": "visual", "title": "视觉语义", "desc": "把参考图和白话拆成部件级视觉契约。"},
            {"id": "intent", "title": "意图与计划", "desc": "白话转结构化意图，再进入 CAD_PLAN。"},
            {"id": "execute", "title": "执行审计修复", "desc": "落 CODEX_PREVIEW，审计，失败则修复并沉淀。"},
        ],
    }


def main() -> None:
    data = build_data()
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    OUTPUT.write_text(f"window.CAD_CAPABILITY_MAP_DATA = {payload};\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
