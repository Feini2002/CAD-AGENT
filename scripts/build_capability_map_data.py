from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    from _bootstrap import ensure_project_root_on_path
except ModuleNotFoundError:  # Imported as scripts.build_capability_map_data.
    from scripts._bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.training.learning_promotion import acceptance_report_is_promotable, build_learning_index
from core.training.source_manifest import (
    DEFAULT_MANIFEST_RELATIVE_PATH,
    display_training_sources,
    training_source_paths,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "capability-map-data.js"
COMMON_PROMPT_CONTRACT = "agents/COMMON_PROMPT_CONTRACT.md"
COVERAGE_PATH = ROOT / "output" / "validation_runs" / "capability-lab" / "cad_capability_coverage.json"
TRAINING_SOURCE_MANIFEST_PATH = ROOT / DEFAULT_MANIFEST_RELATIVE_PATH
DEFAULT_TRAINING_ACCEPTANCE_REPORT_PATHS = [
    ROOT
    / "output"
    / "training_queues"
    / "cad-foundation-first-10"
    / "unsupervised-10-chinese"
    / "unsupervised_10_chinese_report.json",
]
DEFAULT_TRAINING_LEARNING_LEDGER_PATH = ROOT / "output" / "training_learning" / "agent_learning_ledger.json"


def manifest_acceptance_report_paths() -> list[Path]:
    paths = training_source_paths(
        ROOT,
        manifest_path=TRAINING_SOURCE_MANIFEST_PATH,
        role="fact_source",
        kind="training_acceptance_report",
    )
    return paths or list(DEFAULT_TRAINING_ACCEPTANCE_REPORT_PATHS)


def manifest_learning_ledger_path() -> Path:
    paths = training_source_paths(
        ROOT,
        manifest_path=TRAINING_SOURCE_MANIFEST_PATH,
        role="fact_source",
        kind="training_learning_ledger",
    )
    return paths[0] if paths else DEFAULT_TRAINING_LEARNING_LEDGER_PATH


TRAINING_ACCEPTANCE_REPORT_PATHS = manifest_acceptance_report_paths()
TRAINING_LEARNING_LEDGER_PATH = manifest_learning_ledger_path()


def training_acceptance_report_paths() -> list[Path]:
    return list(TRAINING_ACCEPTANCE_REPORT_PATHS)


def training_learning_ledger_path() -> Path:
    return TRAINING_LEARNING_LEDGER_PATH


def training_source_rows() -> list[dict[str, Any]]:
    return display_training_sources(ROOT, TRAINING_SOURCE_MANIFEST_PATH)


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

DESIGNER_GROWTH_STAGES: list[dict[str, Any]] = [
    {
        "id": "foundation_operations",
        "label": "L0 CAD 基础操作",
        "rank": 0,
        "status": "active",
        "goal": "能按结构化意图稳定画出基础图元，并完成选择、移动、复制、旋转、偏移、修剪、图层和回读自检。",
        "evidenceBoundary": "只证明基础课程训练状态，不提升表 C，也不代表专业平面图或施工图可交付。",
    },
    {
        "id": "geometry_constraints",
        "label": "L1 几何洁净与约束",
        "rank": 1,
        "status": "planned",
        "goal": "掌握闭合、端点、共享边、对齐、洞口和尺寸约束。",
        "evidenceBoundary": "需要机器审计和案例反馈后才可声明训练通过。",
    },
    {
        "id": "object_symbols",
        "label": "L2 对象符号语法",
        "rank": 2,
        "status": "planned",
        "goal": "能把家具、门窗、洁具等对象拆成可审计部件和符号语法。",
        "evidenceBoundary": "对象符号通过不等于场景方案通过。",
    },
    {
        "id": "room_plan_composition",
        "label": "L3 房间平面组合",
        "rank": 3,
        "status": "planned",
        "goal": "能组合墙体、门窗、家具、通道和朝向，形成可读房间平面。",
        "evidenceBoundary": "必须区分案例通过、用户反馈通过和表 C 机器指标。",
    },
    {
        "id": "professional_expression",
        "label": "L4 专业表达",
        "rank": 4,
        "status": "planned",
        "goal": "能处理标注、图层、文字、比例、线型和出图表达。",
        "evidenceBoundary": "表达训练不能替代真实 CAD 几何回读。",
    },
    {
        "id": "construction_documents",
        "label": "L5 施工图表达",
        "rank": 5,
        "status": "future",
        "goal": "逐步训练平面、立面、节点、详图、材料和施工说明之间的关系。",
        "evidenceBoundary": "未达到本阶段前不得声称会画完整施工图。",
    },
    {
        "id": "design_judgment",
        "label": "L6 设计判断",
        "rank": 6,
        "status": "future",
        "goal": "训练方案比较、设计取舍、规范意识和用户偏好迭代。",
        "evidenceBoundary": "设计判断需要用户反馈和多案例沉淀，不由单次机器审计证明。",
    },
]

FOUNDATION_COURSES: list[dict[str, Any]] = [
    {"id": "cad-primitives", "name": "基础图元绘制", "kind": "foundation", "group": "CAD 基础操作", "priority": "P0", "owner": "cad_designer", "pipeline": ["pipeline_intent", "pipeline_execute", "pipeline_audit"], "focus": "线、矩形、圆、圆弧、多段线的基点、尺寸和闭合输入", "weaknesses": ["foundation_command_missing", "closed_geometry_unverified"], "next": "训练线 / 矩形 / 圆 / 多段线基础落图与回读", "growthStageId": "foundation_operations", "courseOrder": 1},
    {"id": "cad-selection-edit", "name": "选择与基础编辑", "kind": "foundation", "group": "CAD 基础操作", "priority": "P0", "owner": "cad_designer", "pipeline": ["pipeline_execute", "pipeline_audit"], "focus": "选择范围、复制、移动、删除、撤销边界和不碰正式图层", "weaknesses": ["selection_scope_unclear", "formal_layer_write_risk"], "next": "训练选择集、移动、复制和删除边界", "growthStageId": "foundation_operations", "courseOrder": 2},
    {"id": "cad-transform", "name": "旋转镜像缩放", "kind": "foundation", "group": "CAD 基础操作", "priority": "P0", "owner": "cad_designer", "pipeline": ["pipeline_intent", "pipeline_execute", "pipeline_audit"], "focus": "基点、角度、方向、镜像对称和组合对象变换", "weaknesses": ["transform_reference_error", "plan_view_role_direction_errors"], "next": "训练旋转、镜像、缩放的基点和方向语义", "growthStageId": "foundation_operations", "courseOrder": 3},
    {"id": "cad-offset-trim", "name": "偏移修剪延伸", "kind": "foundation", "group": "CAD 基础操作", "priority": "P0", "owner": "cad_designer", "pipeline": ["pipeline_intent", "pipeline_execute", "pipeline_audit", "pipeline_repair"], "focus": "偏移距离、修剪边界、延伸到墙线、清理毛刺和端点", "weaknesses": ["trim_offset_cleanup_gap", "duplicate_shared_edges"], "next": "训练 offset / trim / extend 后的洁净度审计", "growthStageId": "foundation_operations", "courseOrder": 4},
    {"id": "cad-layer-discipline", "name": "图层与线型基础", "kind": "foundation", "group": "CAD 基础操作", "priority": "P0", "owner": "cad_designer", "pipeline": ["pipeline_execute", "pipeline_audit", "pipeline_delivery"], "focus": "CODEX_PREVIEW、对象图层、颜色、线型和正式图层保护", "weaknesses": ["layer_discipline_missing", "formal_layer_write_risk"], "next": "训练预览图层、对象分层和正式图层保护", "growthStageId": "foundation_operations", "courseOrder": 5},
    {"id": "cad-closure-constraints", "name": "闭合对齐约束", "kind": "foundation", "group": "CAD 基础操作", "priority": "P0", "owner": "cad_designer", "pipeline": ["pipeline_intent", "pipeline_execute", "pipeline_audit", "pipeline_repair"], "focus": "闭合轮廓、端点重合、共享边去重、中心对齐和边界约束", "weaknesses": ["closed_geometry_unverified", "duplicate_shared_edges"], "next": "训练闭合轮廓、对齐和共享边去重", "growthStageId": "foundation_operations", "courseOrder": 6},
    {"id": "cad-readback-audit", "name": "回读与自检基础", "kind": "foundation", "group": "CAD 基础操作", "priority": "P0", "owner": "cad_designer", "pipeline": ["pipeline_audit", "pipeline_delivery", "pipeline_learning_promoter"], "focus": "created handles、bbox、实体类型、gap/overlap/open endpoint 和自检汇报", "weaknesses": ["readback_audit_missing", "machine_green_delivery"], "next": "训练 handles 回读、机器审计和低噪声自检汇报", "growthStageId": "foundation_operations", "courseOrder": 7},
]

V2_GROUP_DEFAULTS: dict[str, dict[str, Any]] = {
    "CAD 基础操作": {
        "kind": "foundation",
        "owner": "cad_designer",
        "pipeline": ["pipeline_intent", "pipeline_execute", "pipeline_audit"],
        "weaknesses": ["foundation_command_missing", "readback_audit_missing"],
        "next_prefix": "训练生产级 CAD 基础动作",
    },
    "基础家具": {
        "kind": "object",
        "owner": "residential",
        "pipeline": ["pipeline_asset_retriever", "pipeline_visual_intent", "pipeline_intent", "pipeline_execute", "pipeline_audit", "pipeline_learning_promoter"],
        "weaknesses": ["missing_furniture_parts", "plan_view_role_direction_errors"],
        "next_prefix": "训练家具对象符号、尺度和组合关系",
    },
    "储位家具": {
        "kind": "object",
        "owner": "residential",
        "pipeline": ["pipeline_asset_retriever", "pipeline_visual_intent", "pipeline_intent", "pipeline_execute", "pipeline_audit", "pipeline_repair", "pipeline_learning_promoter"],
        "weaknesses": ["missing_furniture_parts", "machine_green_delivery"],
        "next_prefix": "训练柜体模数、开启域和收纳净空",
    },
    "厨卫对象": {
        "kind": "object",
        "owner": "residential",
        "pipeline": ["pipeline_asset_retriever", "pipeline_intent", "pipeline_execute", "pipeline_audit", "pipeline_repair"],
        "weaknesses": ["unsupported_or_risky", "machine_size_drift_only"],
        "next_prefix": "训练厨卫设备、洁具净空和点位语义",
    },
    "基础绘图": {
        "kind": "draw",
        "owner": "pipeline_execute",
        "pipeline": ["pipeline_context_curator", "pipeline_intent", "pipeline_execute", "pipeline_audit", "pipeline_repair"],
        "weaknesses": ["duplicate_shared_edges", "closed_geometry_unverified"],
        "next_prefix": "训练室内图纸交付物的几何与审计链路",
    },
    "标注表达": {
        "kind": "annotation",
        "owner": "pipeline_delivery",
        "pipeline": ["pipeline_intent", "pipeline_execute", "pipeline_audit", "pipeline_delivery"],
        "weaknesses": ["missing_annotation", "machine_green_delivery"],
        "next_prefix": "训练标注、编号、图例和表格表达",
    },
}


V2_TRAINING_SEEDS: dict[str, list[tuple[str, str, str, str]]] = {
    "CAD 基础操作": [
        ("cad-units-scale", "单位与比例设置", "P0", "毫米单位、绘图比例、模型空间和图纸空间比例边界"),
        ("cad-coordinate-input", "坐标输入基础", "P0", "绝对坐标、相对坐标、极坐标和基点复用"),
        ("cad-osnap-ortho-polar", "捕捉与正交极轴", "P0", "OSNAP、ORTHO、POLAR 对端点、中心点和垂直水平关系的约束"),
        ("cad-polyline-width-cleanup", "多段线宽度与清理", "P0", "多段线闭合、宽度、端点和对象类型回读"),
        ("cad-hatch-boundary", "填充与边界", "P0", "hatch 材料区、闭合边界、孤岛和图层归属"),
        ("cad-boundary-region", "边界生成", "P1", "从线段生成闭合 boundary / region 并复算面积"),
        ("cad-fillet-chamfer", "圆角倒角", "P1", "倒角半径、直角转折、家具圆角和节点清理"),
        ("cad-stretch-edit", "拉伸编辑", "P1", "局部拉伸后保持门洞、墙厚和家具组合关系"),
        ("cad-block-insert-attribute", "块插入与属性", "P0", "block 插入点、属性字段、编号和图层继承"),
        ("cad-block-rotate-scale", "块旋转缩放", "P0", "家具块旋转、镜像、比例和朝向语义"),
        ("cad-xref-underlay-protect", "底图引用保护", "P0", "xref、PDF underlay、原始底图锁定和预览层隔离"),
        ("cad-layout-viewport", "布局与视口", "P1", "paper space、viewport、比例锁定和视口裁切"),
        ("cad-plot-scale-titleblock", "打印比例与图框", "P1", "plot style、标题栏、出图比例和页面尺寸"),
        ("cad-redline-revision", "红线与修订", "P1", "revision cloud、红线说明、修改范围和版本标记"),
        ("cad-layer-lineweight-standard", "线宽线型标准", "P0", "图层、颜色、线型、线宽和对象语义一致"),
        ("cad-selection-by-room", "按房间安全选择", "P1", "按房间、图层、对象类型选择并避免误动正式图层"),
        ("cad-array-copy-pattern", "阵列与复制模式", "P1", "灯具、餐椅、柜格等重复对象的阵列间距"),
        ("cad-measure-distance-area", "距离面积测量", "P1", "测距、面积、总尺寸与分段尺寸一致性"),
        ("cad-purge-audit-cleanup", "图纸清理审计", "P2", "AUDIT / PURGE 思路、重复线、零长度线和无效对象清理"),
        ("cad-dim-style-baseline", "尺寸样式基线", "P1", "尺寸文字、箭头、基线、连续标注和比例"),
        ("cad-text-mleader-style", "文字引线样式", "P1", "mtext、leader、注释比例和对象关联"),
        ("cad-handle-bbox-report", "句柄与边界框报告", "P0", "创建句柄、边界框、实体类型和回读报告"),
        ("cad-layer-pollution-check", "图层污染检查", "P0", "训练默认只写 CODEX_PREVIEW 并检测正式图层污染"),
        ("cad-safe-undo-rollback", "安全撤销回滚", "P1", "执行失败后的回滚边界、对象删除和证据记录"),
    ],
    "基础家具": [
        ("furniture-single-bed", "单人床", "P0", "床垫、枕位、床头靠墙和两侧通行"),
        ("furniture-double-bed", "双人床", "P0", "床架、床垫、床头轴线和床头柜组合"),
        ("furniture-queen-bed", "Queen 床", "P0", "主卧床型、床头方向、过道和门扇避让"),
        ("furniture-king-bed", "King 床", "P1", "大床外包络、三面通行和床尾家具关系"),
        ("furniture-bunk-bed", "上下铺", "P1", "双层投影、梯位、护栏和儿童房组合"),
        ("furniture-kids-bed", "儿童床", "P1", "儿童床尺寸、圆角、防撞和玩具柜关系"),
        ("furniture-sofa-bed", "沙发床", "P1", "沙发态与展开态、展开虚线和碰撞检查"),
        ("furniture-loveseat-sofa", "双人沙发", "P0", "坐垫分格、扶手、茶几距离和朝向"),
        ("furniture-three-seat-sofa", "三人沙发", "P0", "三坐垫、靠背、电视视线和主通道"),
        ("furniture-sectional-sofa", "L 型沙发", "P0", "L 形转角、贵妃位左右、茶几和地毯关系"),
        ("furniture-lounge-chair", "休闲椅", "P1", "阅读朝向、宽坐面、落地灯和边距"),
        ("furniture-armchair", "单人扶手椅", "P1", "椅背、扶手、会客中心和旋转后退空间"),
        ("furniture-recliner-chair", "躺椅", "P1", "躺卧方向、展开长度和不挡门窗"),
        ("furniture-rocking-chair", "摇椅", "P2", "弧形底、摇摆轴和前后摆幅"),
        ("furniture-dining-chair", "餐椅", "P0", "椅面、椅背、面向桌心和拉椅净空"),
        ("furniture-bar-stool", "吧椅", "P1", "座高、脚踏、吧台朝向和膝部空间"),
        ("furniture-task-chair", "办公椅", "P1", "五星脚、旋转、面向书桌和后退空间"),
        ("furniture-entry-bench", "换鞋凳", "P1", "玄关长凳、鞋柜组合和入户门扇避让"),
        ("furniture-bed-end-bench", "床尾凳", "P1", "床尾平行、床尾通行和比例"),
        ("furniture-ottoman", "矮凳/脚凳", "P2", "可移动软凳、沙发组合和通道避让"),
        ("furniture-rectangular-dining-table-4p", "四人长方餐桌", "P0", "四椅阵列、餐边柜和椅后净空"),
        ("furniture-rectangular-dining-table-6p", "六人长方餐桌", "P0", "六椅阵列、吊灯中心和四周通行"),
        ("furniture-round-dining-table", "圆餐桌", "P1", "圆桌、放射椅位、人数和环形净空"),
        ("furniture-extendable-dining-table", "可伸缩餐桌", "P1", "收合/展开两态、餐椅增减和展开碰撞"),
        ("furniture-coffee-table", "茶几扩展", "P0", "圆角/矩形茶几、沙发中心对齐和间距"),
        ("furniture-side-table", "边几", "P1", "沙发侧边、台灯、扶手高度和通行避让"),
        ("furniture-corner-table", "角几", "P2", "转角小几、单椅组合和转角碰撞"),
        ("furniture-console-table", "玄关台", "P1", "窄长台、靠墙、镜面和门厅净宽"),
        ("furniture-writing-desk", "书桌", "P0", "桌面、桌腿、靠窗/靠墙偏好和椅后空间"),
        ("furniture-l-desk", "L 型书桌", "P1", "主副工作边、转角腿部空间和文件柜"),
        ("furniture-kids-study-desk", "儿童学习桌", "P1", "采光方向、书架、插座和椅后空间"),
        ("furniture-vanity-table", "梳妆台", "P1", "镜面中心、抽屉开启和衣柜关系"),
        ("furniture-tv-low-console", "电视低柜", "P1", "电视中心线、背景墙和沙发视轴"),
        ("furniture-platform-tatami", "地台/榻榻米", "P1", "平台边界、模块、标高和台阶防绊"),
        ("furniture-floor-table", "和室矮桌", "P2", "低桌、坐垫围合和地台组合"),
        ("furniture-screen-partition", "屏风/隔断", "P1", "薄隔断、开合方向、透空和通行避让"),
        ("furniture-high-chair", "高脚儿童椅", "P2", "儿童椅托盘、餐桌组合和入口侧避让"),
        ("furniture-beanbag", "懒人沙发", "P2", "软包非规则外包络和游戏阅读区"),
        ("furniture-nesting-table", "嵌套边桌", "P2", "套叠态、抽出方向和展开占地"),
        ("furniture-piano", "钢琴/电钢", "P2", "琴键侧、琴凳后退、插座和墙边关系"),
    ],
    "储位家具": [
        ("storage-swing-wardrobe", "平开衣柜", "P0", "柜体、门扇弧、柜深和门扇碰撞"),
        ("storage-sliding-wardrobe", "推拉衣柜", "P0", "双轨、滑动方向、前方取物净空和床侧关系"),
        ("storage-open-clothes-rack", "开放挂衣架", "P1", "立柱、横杆、挂衣深度和玄关/卧室摆位"),
        ("storage-walk-in-closet-single", "一字衣帽间", "P1", "单排柜、入口方向、换衣通道和镜面"),
        ("storage-walk-in-closet-l", "L 型衣帽间", "P1", "两墙柜、转角死角和转角五金"),
        ("storage-walk-in-closet-u", "U 型衣帽间", "P2", "三面柜、中央通道和岛柜避让"),
        ("storage-drawer-dresser", "抽屉斗柜", "P1", "抽屉线、拉出域、床侧关系和防碰撞"),
        ("storage-tall-chest", "高斗柜", "P2", "竖向抽屉、靠墙、防倾倒和取物空间"),
        ("storage-bedside-cabinet", "床头柜", "P0", "成对摆放、抽屉方向、床侧净距和比例"),
        ("storage-bookcase", "书柜", "P1", "层板格、深度、书桌关系和开门/取书"),
        ("storage-open-shelving", "开放书架", "P1", "开放格、靠墙、窗帘避让和阅读区"),
        ("storage-wall-shelf", "墙搁板", "P2", "墙面法线、标高、头部碰撞和下方对象"),
        ("storage-shoe-cabinet", "鞋柜", "P0", "鞋柜深度、换鞋凳、入户门和门厅净宽"),
        ("storage-tilt-out-shoe-cabinet", "翻斗鞋柜", "P1", "翻斗开启域、薄柜深度和翻板碰撞"),
        ("storage-sideboard", "餐边柜", "P1", "柜深、餐桌关系、柜门开启和椅后净空"),
        ("storage-wine-cabinet", "酒柜", "P2", "瓶格、玻璃门、展示面和开门范围"),
        ("storage-tv-wall", "电视收纳墙", "P1", "低柜、高柜、开放格、电视位和观看轴"),
        ("storage-kitchen-base-cabinet", "厨房地柜", "P0", "地柜模数、踢脚、台面和操作走道"),
        ("storage-kitchen-wall-cabinet", "厨房吊柜", "P0", "吊柜深度、底标高、开门和烟机碰撞"),
        ("storage-pantry-tall-cabinet", "高柜/pantry", "P1", "落地高柜、冰箱烤箱组合和工作三角避让"),
        ("storage-corner-cabinet", "转角柜", "P1", "L 角柜、转盘、盲区和相邻柜体关系"),
        ("storage-pull-out-basket-cabinet", "拉篮窄柜", "P1", "窄柜宽度、抽拉方向和灶台旁碰撞"),
        ("storage-bathroom-vanity-cabinet", "浴室柜", "P0", "台盆柜、门/抽、台盆中心和前方净空"),
        ("storage-balcony-cabinet", "阳台储物柜", "P1", "洗衣区、防水区、门窗和晾晒避让"),
        ("storage-under-stair-cabinet", "楼梯下柜", "P2", "斜顶柜、低净高、开门方向和碰头风险"),
    ],
    "厨卫对象": [
        ("kitchen-single-sink", "单槽水槽", "P0", "水槽、龙头、中心线和两侧落物区"),
        ("kitchen-double-sink", "双槽水槽", "P1", "双槽分隔、主副槽、备餐区和管线关系"),
        ("kitchen-gas-cooktop", "燃气灶", "P0", "火口、操作面、烟机中心和两侧台面"),
        ("kitchen-induction-cooktop", "电磁灶", "P1", "平面灶面、控制侧、电位和水槽距离"),
        ("kitchen-range-hood", "油烟机", "P0", "烟机宽度、排烟方向、灶具中心和吊柜碰撞"),
        ("kitchen-built-in-oven", "嵌入式烤箱", "P1", "箱体、下翻门、高柜电位和散热"),
        ("kitchen-steam-oven", "蒸烤一体机", "P2", "箱体、门开向、设备位和散热空间"),
        ("kitchen-fridge", "冰箱", "P0", "门铰链、门扇、散热间距和落物台"),
        ("kitchen-french-door-fridge", "对开门冰箱", "P1", "双门弧线、两侧门扇和高柜关系"),
        ("kitchen-dishwasher", "洗碗机", "P1", "下翻门、水槽距离和前方站立空间"),
        ("kitchen-microwave", "微波炉", "P2", "门开向、取物高度、插座和吊柜/高柜"),
        ("kitchen-island", "厨房岛台", "P1", "独立台面、操作边、座位边和四周通道"),
        ("kitchen-peninsula", "半岛台", "P1", "连墙台面、开放侧、端部回转和餐厨关系"),
        ("kitchen-bar-counter", "吧台", "P2", "高台、座位侧、吧椅座高和膝部空间"),
        ("kitchen-prep-counter-run", "备餐连续台面", "P0", "连续台面、水槽旁备餐区和灶槽距离"),
        ("kitchen-trash-pullout", "垃圾分类拉桶", "P2", "柜内桶、抽拉域、水槽旁位置和碰撞"),
        ("kitchen-washer", "洗衣机", "P1", "前开/上开门、给排水、地漏和门开启"),
        ("kitchen-stacked-dryer", "干衣机叠放", "P2", "叠放箱体、门向、维修净空和阳台柜关系"),
        ("kitchen-work-triangle", "厨房工作三角", "P0", "水槽、灶具、冰箱之间的三角距离和阻断检查"),
        ("bathroom-toilet", "马桶", "P0", "坐便器、水箱、中心线、侧方和前方净空"),
        ("bathroom-smart-toilet", "智能马桶", "P1", "电源点、水阀、防水距离和操作侧"),
        ("bathroom-squat-toilet", "蹲便器", "P2", "脚位方向、排污中心、防滑和门扇避让"),
        ("bathroom-bidet", "净身器/bidet", "P2", "洁具中心距、两件间距和使用正向"),
        ("bathroom-pedestal-basin", "柱盆", "P1", "盆体、立柱、镜面和前方净空"),
        ("bathroom-vessel-basin", "台上盆", "P1", "台面、盆、龙头侧和柜门人体净空"),
        ("bathroom-double-vanity", "双台盆", "P2", "双盆中心距、双人位和镜柜关系"),
        ("bathroom-shower-enclosure", "淋浴房", "P0", "玻璃围合、门弧、花洒墙、地漏和湿区"),
        ("bathroom-shower-screen", "一字淋浴屏", "P1", "玻璃线、开口侧、干湿分区和地漏关系"),
        ("bathroom-bathtub", "浴缸", "P1", "矩形/椭圆浴缸、入浴侧、龙头和检修"),
        ("bathroom-shower-bench", "浴凳", "P2", "坐高、扶手、花洒朝向和淋浴回转"),
        ("bathroom-mirror-cabinet-drain-group", "镜柜/毛巾杆/地漏组", "P1", "镜柜标高、毛巾杆、坡向点和头碰风险"),
        ("bathroom-clearance", "卫浴净空", "P0", "30×48 in 净空、60 in 回转和门扇侵入检查"),
    ],
    "基础绘图": [
        ("drawing-field-measurement", "量房图", "P0", "量房尺寸、缺项追问、墙柱门窗和尺寸链"),
        ("drawing-existing-structure-plan", "原始结构图", "P0", "原墙、柱、梁、门窗洞口、管井和阳台"),
        ("drawing-wall-centerline", "墙轴线图", "P0", "墙轴、墙厚、中心线和偏移关系"),
        ("drawing-room-outline-polyline", "房间闭合轮廓", "P0", "多段线闭合房间、面积复算和 open endpoint"),
        ("drawing-column-beam-plan", "柱梁绘制", "P1", "结构柱、梁位、图层和墙体关系"),
        ("drawing-door-opening-plan", "门洞绘制", "P0", "门洞扣减、门垛、洞口宽度和墙段连续"),
        ("drawing-window-opening-plan", "窗洞绘制", "P0", "窗洞、窗线、墙体嵌入和离地语义"),
        ("drawing-pipe-shaft-plan", "管井绘制", "P1", "管井外包络、不可侵占边界和洁具关系"),
        ("drawing-balcony-outline", "阳台轮廓", "P1", "阳台边界、推拉门、洗衣机和地漏关系"),
        ("drawing-stair-outline", "楼梯轮廓", "P2", "踏步、方向箭头、低净高和楼梯下柜关系"),
        ("drawing-demolition-plan", "拆除图", "P0", "拆除墙体、保留构件、云线和正式层保护"),
        ("drawing-new-partition-plan", "新建墙体图", "P0", "新建墙体、门垛、墙体材料和墙厚一致"),
        ("drawing-furniture-layout-plan", "平面布置图", "P0", "家具、通道、门窗开启和房间归属"),
        ("drawing-furniture-dimension-plan", "家具尺寸图", "P1", "家具外轮廓、定位尺寸和 bbox 一致"),
        ("drawing-floor-finish-plan", "地面铺装图", "P1", "材料 hatch、铺贴方向、拼缝和过门石"),
        ("drawing-material-transition-plan", "材料分界图", "P1", "不同材料分界线、端点闭合和区域不重叠"),
        ("drawing-rcp-plan", "顶面/RCP", "P0", "吊顶轮廓、灯槽、风口、检修口和标高"),
        ("drawing-ceiling-dimension-plan", "吊顶尺寸图", "P1", "吊顶跌级、边距、灯槽宽度和尺寸标注"),
        ("drawing-lighting-location-plan", "灯具定位图", "P0", "灯具中心点、阵列间距、回路和家具中心线"),
        ("drawing-switch-plan", "开关布置图", "P1", "开关点位、控制回路、门边距离和编号"),
        ("drawing-outlet-plan", "插座布置图", "P1", "强电插座、设备电位、离墙距离和高度标注"),
        ("drawing-low-voltage-plan", "弱电点位图", "P2", "网口、电视口、弱电箱和家具设备关系"),
        ("drawing-plumbing-point-plan", "给排水点位图", "P1", "冷热水、排水、洁具中心和地漏坡向"),
        ("drawing-hvac-ac-plan", "空调风口图", "P2", "空调内机、风口、检修口和吊顶关系"),
        ("drawing-tv-wall-elevation", "电视墙立面", "P1", "电视中心、收纳墙、插座高度和材料编号"),
        ("drawing-headboard-wall-elevation", "床头墙立面", "P1", "床头背景、灯位、开关和床头柜高度"),
        ("drawing-kitchen-elevation", "橱柜立面", "P0", "地柜、吊柜、高柜、台面和设备高度"),
        ("drawing-bathroom-elevation", "卫浴立面", "P1", "台盆、镜柜、淋浴、毛巾杆和标高"),
        ("drawing-section-callout-detail", "剖面与详图索引", "P1", "剖切线、详图索引和局部 bbox 对应"),
        ("drawing-ceiling-detail", "吊顶节点", "P1", "跌级、灯槽、龙骨层次和节点尺寸"),
        ("drawing-waterproofing-detail", "防水节点", "P1", "防水翻边、湿区边界和材料层次"),
        ("drawing-baseboard-trim-detail", "踢脚/收口节点", "P2", "踢脚线、地墙收口和材料过渡"),
        ("drawing-door-window-schedule-link", "门窗表联动", "P1", "门窗编号、图面数量和 schedule 行一致"),
        ("drawing-cabinet-schedule-link", "柜体表联动", "P1", "柜体编号、规格、位置和图面符号一致"),
        ("drawing-full-house-mini-set-audit", "小套图一致性审计", "P0", "平面、顶面、立面、表格之间的编号和尺寸一致"),
    ],
    "标注表达": [
        ("annotation-dimension-chain", "尺寸链", "P0", "总尺寸、分段尺寸、定位尺寸和几何一致"),
        ("annotation-room-name", "房间名标注", "P0", "房间名称、文字高度、居中和图层"),
        ("annotation-room-tag", "房间编号", "P1", "room tag、面积、功能和房间闭合轮廓关联"),
        ("annotation-door-window-tag", "门窗编号", "P1", "门窗 tag、洞口、门窗表和编号唯一"),
        ("annotation-furniture-tag", "家具编号", "P0", "家具 tag、数量、尺寸和 FF&E 表关联"),
        ("annotation-equipment-tag", "设备编号", "P1", "设备编号、型号、位置和设备表关联"),
        ("annotation-plumbing-fixture-tag", "洁具编号", "P1", "洁具 tag、中心线、点位和洁具表关联"),
        ("annotation-lighting-fixture-tag", "灯具编号", "P1", "灯具 tag、回路、灯具表和中心点"),
        ("annotation-material-tag", "材料编号", "P1", "材料编号、hatch 区域、图例和材料表"),
        ("annotation-finish-tag", "饰面标注", "P1", "floor/wall/base/ceiling 字段和房间关联"),
        ("annotation-keynote", "施工说明 keynote", "P1", "keynote 编号、callout 和说明表一致"),
        ("annotation-legend", "图例", "P1", "符号、图例、说明和对象类型一致"),
        ("annotation-symbol-table", "符号表", "P2", "符号名称、图层、用途和插入样例"),
        ("annotation-abbreviation-table", "缩写表", "P2", "缩写、中文说明和图纸中使用位置"),
        ("annotation-title-block", "标题栏", "P1", "项目名、图名、比例、日期和版本"),
        ("annotation-drawing-index", "图纸目录", "P1", "图号、图名、版本和套图完整性"),
        ("annotation-sheet-number-scale", "图号与比例", "P1", "sheet number、scale、viewport 和标题栏一致"),
        ("annotation-text-style", "文字样式", "P1", "文字高度、字体、注释比例和图层"),
        ("annotation-dimension-style", "尺寸样式", "P1", "尺寸线、箭头、文字和比例统一"),
        ("annotation-lineweight-hierarchy", "线宽层级", "P1", "墙体、家具、标注、辅助线的线宽层次"),
        ("annotation-elevation-marker", "立面索引", "P1", "立面箭头、编号、视图方向和目标墙体"),
        ("annotation-section-marker", "剖面索引", "P1", "剖切线、方向、编号和详图入口"),
        ("annotation-detail-marker", "详图索引", "P1", "局部详图编号、比例和源图定位"),
        ("annotation-revision-cloud", "修订云线", "P2", "修订范围、版本说明和红线边界"),
        ("annotation-material-schedule", "材料表", "P1", "材料编号、位置、规格和图面 count 一致"),
        ("annotation-equipment-schedule", "设备表", "P1", "设备编号、型号、尺寸、数量和图面符号一致"),
        ("annotation-cabinet-schedule", "柜体表", "P1", "柜体编号、W-H-D、位置和立面/平面联动"),
        ("annotation-ffe-schedule", "FF&E 表", "P0", "家具、灯具、饰品、尺寸、材质、数量和备注"),
        ("annotation-checked-not-checked", "checked/not_checked 说明", "P0", "机器证据证明了什么、没证明什么和用户验收重点"),
    ],
}


def build_v2_training_capabilities() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group, seeds in V2_TRAINING_SEEDS.items():
        defaults = V2_GROUP_DEFAULTS[group]
        for item_id, name, priority, focus in seeds:
            rows.append(
                {
                    "id": item_id,
                    "name": name,
                    "kind": defaults["kind"],
                    "group": group,
                    "priority": priority,
                    "owner": defaults["owner"],
                    "pipeline": list(defaults["pipeline"]),
                    "focus": focus,
                    "weaknesses": list(defaults["weaknesses"]),
                    "next": f"{defaults['next_prefix']}：{name}",
                }
            )
    return rows


V2_TRAINING_CAPABILITIES = build_v2_training_capabilities()


VALIDATION_CHECKERS: list[dict[str, Any]] = [
    {
        "id": "checker-preview-layer-safety",
        "name": "CODEX_PREVIEW 图层安全",
        "category": "safety",
        "implementationStatus": "skeleton",
        "plannedInputs": ["created handles", "entity layer list", "target drawing layer policy"],
        "plannedOutputs": ["formal_layer_touched", "preview_layer_only", "unknown_layer_entities"],
        "failureExamples": ["训练落图写入正式图层", "复制对象保留了来源图层", "回滚后遗留非 CODEX_PREVIEW 对象"],
        "evidenceBoundary": "Skeleton only; not yet a CAD proof and not counted in Table C.",
    },
    {
        "id": "checker-closed-geometry",
        "name": "闭合几何与端点洁净",
        "category": "geometry",
        "implementationStatus": "skeleton",
        "plannedInputs": ["polyline endpoints", "bbox", "gap / overlap / open endpoint report"],
        "plannedOutputs": ["open_endpoint_count", "gap_count", "overlap_count", "duplicate_edge_count"],
        "failureExamples": ["房间轮廓未闭合", "共享边重复生成", "修剪后留下短毛刺"],
        "evidenceBoundary": "Skeleton only; not yet a CAD proof and not counted in Table C.",
    },
    {
        "id": "checker-readback-evidence",
        "name": "handles 回读证据完整性",
        "category": "evidence",
        "implementationStatus": "skeleton",
        "plannedInputs": ["created handles", "entity type summary", "audit review"],
        "plannedOutputs": ["missing_handles", "unread_entities", "checked_not_checked_summary"],
        "failureExamples": ["只给截图没有 handles", "机器审计通过但未说明没证明什么", "实体类型与训练目标不匹配"],
        "evidenceBoundary": "Skeleton only; not yet a CAD proof and not counted in Table C.",
    },
    {
        "id": "checker-clearance-collision",
        "name": "净距与碰撞",
        "category": "clearance",
        "implementationStatus": "skeleton",
        "plannedInputs": ["object bbox", "required clearance envelope", "room boundary"],
        "plannedOutputs": ["collision_pairs", "clearance_shortfall", "blocked_passage"],
        "failureExamples": ["床侧通道不足", "椅后净空不足", "洁具前方净空被门扇侵入"],
        "evidenceBoundary": "Skeleton only; not yet a CAD proof and not counted in Table C.",
    },
    {
        "id": "checker-open-swing-domain",
        "name": "开门 / 抽屉 / 翻板开启域",
        "category": "clearance",
        "implementationStatus": "skeleton",
        "plannedInputs": ["door arcs", "drawer pull direction", "cabinet front line", "nearby object bbox"],
        "plannedOutputs": ["swing_collision", "pullout_blocked", "opening_domain_missing"],
        "failureExamples": ["衣柜门弧碰床", "抽屉拉出域被椅子挡住", "淋浴门开启方向未声明"],
        "evidenceBoundary": "Skeleton only; not yet a CAD proof and not counted in Table C.",
    },
    {
        "id": "checker-work-triangle",
        "name": "厨房工作三角",
        "category": "planning",
        "implementationStatus": "skeleton",
        "plannedInputs": ["sink center", "cooktop center", "fridge front center", "obstruction bbox"],
        "plannedOutputs": ["triangle_lengths", "obstructed_leg", "missing_anchor"],
        "failureExamples": ["冰箱未参与三角", "灶槽距离过远", "岛台阻断工作路径"],
        "evidenceBoundary": "Skeleton only; not yet a CAD proof and not counted in Table C.",
    },
    {
        "id": "checker-dimension-chain",
        "name": "尺寸链闭合",
        "category": "annotation",
        "implementationStatus": "skeleton",
        "plannedInputs": ["overall dimension", "segment dimensions", "object bbox"],
        "plannedOutputs": ["dimension_sum_delta", "missing_dimension_anchor", "scale_mismatch"],
        "failureExamples": ["分段尺寸相加不等于总尺寸", "家具定位缺少基准", "图纸空间比例与标注不一致"],
        "evidenceBoundary": "Skeleton only; not yet a CAD proof and not counted in Table C.",
    },
    {
        "id": "checker-cross-sheet-consistency",
        "name": "跨图纸一致性",
        "category": "delivery",
        "implementationStatus": "skeleton",
        "plannedInputs": ["plan tags", "elevation markers", "schedules", "sheet index"],
        "plannedOutputs": ["missing_sheet_ref", "orphan_marker", "schedule_mismatch"],
        "failureExamples": ["平面有立面索引但无对应立面", "材料编号图面和材料表不一致", "门窗表数量与图面不一致"],
        "evidenceBoundary": "Skeleton only; not yet a CAD proof and not counted in Table C.",
    },
    {
        "id": "checker-schedule-count",
        "name": "表格数量对账",
        "category": "delivery",
        "implementationStatus": "skeleton",
        "plannedInputs": ["tagged symbols", "schedule rows", "quantity fields"],
        "plannedOutputs": ["missing_schedule_row", "quantity_delta", "duplicate_tag"],
        "failureExamples": ["家具编号重复", "FF&E 表漏项", "柜体表规格与平面符号不一致"],
        "evidenceBoundary": "Skeleton only; not yet a CAD proof and not counted in Table C.",
    },
    {
        "id": "checker-checked-not-checked",
        "name": "checked / not_checked 汇报完整性",
        "category": "delivery",
        "implementationStatus": "skeleton",
        "plannedInputs": ["audit result", "screenshot path", "readback summary", "user feedback target"],
        "plannedOutputs": ["checked_items", "not_checked_items", "user_review_focus"],
        "failureExamples": ["只堆数字没有说明用户看哪里", "把未回读项写成已通过", "没有给下一轮反馈入口"],
        "evidenceBoundary": "Skeleton only; not yet a CAD proof and not counted in Table C.",
    },
]


TRAINING_BATCHES: list[dict[str, Any]] = [
    {
        "id": "batch-foundation-production-hygiene",
        "label": "基础生产卫生",
        "rank": 1,
        "goal": "先让 CAD Designer Agent 会稳定生成、回读和说明基础 CAD 图元。",
        "programIds": [
            "cad-primitives",
            "cad-coordinate-input",
            "cad-osnap-ortho-polar",
            "cad-polyline-width-cleanup",
            "cad-closure-constraints",
            "cad-handle-bbox-report",
        ],
        "dependsOn": [],
        "checkerIds": ["checker-closed-geometry", "checker-readback-evidence"],
        "evidenceRequired": ["结构化意图或 CAD_PLAN", "created handles / bbox 回读", "checked / not_checked 自检"],
        "passBoundary": "只证明基础图元和回读训练进入可复盘状态，不代表对象或房间方案能力。",
    },
    {
        "id": "batch-safe-editing-and-layer-discipline",
        "label": "安全编辑与图层纪律",
        "rank": 2,
        "goal": "训练选择、变换、偏移修剪、图层隔离和出图前清理，防止误动正式图层。",
        "programIds": [
            "cad-selection-edit",
            "cad-transform",
            "cad-offset-trim",
            "cad-layer-discipline",
            "cad-xref-underlay-protect",
            "cad-layer-pollution-check",
            "cad-safe-undo-rollback",
        ],
        "dependsOn": ["batch-foundation-production-hygiene"],
        "checkerIds": ["checker-preview-layer-safety", "checker-closed-geometry", "checker-readback-evidence"],
        "evidenceRequired": ["预览图层写入证明", "编辑前后实体数量和 bbox 对比", "回滚或失败边界说明"],
        "passBoundary": "只证明安全编辑和图层纪律训练，不代表复杂家具或套图交付已通过。",
    },
    {
        "id": "batch-core-furniture-symbols",
        "label": "高频家具符号",
        "rank": 3,
        "goal": "把床、沙发、餐桌椅、书桌和电视柜等高频对象训练成有方向、部件和净距的平面符号。",
        "programIds": [
            "furniture-double-bed",
            "furniture-loveseat-sofa",
            "furniture-sectional-sofa",
            "furniture-rectangular-dining-table-4p",
            "furniture-writing-desk",
            "furniture-tv-low-console",
        ],
        "dependsOn": ["batch-safe-editing-and-layer-discipline"],
        "checkerIds": ["checker-clearance-collision", "checker-open-swing-domain", "checker-readback-evidence"],
        "evidenceRequired": ["对象外包络和部件语义", "朝向 / 贴墙 / 使用侧说明", "净距或碰撞的 checked / not_checked"],
        "passBoundary": "只证明单对象或小组合训练，不代表房间布局整体通过。",
    },
    {
        "id": "batch-storage-kitchen-bath-objects",
        "label": "储位厨卫对象",
        "rank": 4,
        "goal": "训练柜体、厨房设备和洁具的开启域、管线点位、工作三角和人体净空。",
        "programIds": [
            "storage-swing-wardrobe",
            "storage-kitchen-base-cabinet",
            "storage-kitchen-wall-cabinet",
            "kitchen-single-sink",
            "kitchen-gas-cooktop",
            "kitchen-fridge",
            "kitchen-work-triangle",
            "bathroom-toilet",
            "bathroom-clearance",
        ],
        "dependsOn": ["batch-core-furniture-symbols"],
        "checkerIds": ["checker-clearance-collision", "checker-open-swing-domain", "checker-work-triangle"],
        "evidenceRequired": ["柜门 / 抽屉 / 洁具使用域", "厨卫点位和中心线", "工作三角或净空未验证项说明"],
        "passBoundary": "只证明厨卫和柜体对象进入训练路径，不代表整套厨房或卫生间施工图通过。",
    },
    {
        "id": "batch-room-plan-composition",
        "label": "房间平面组合",
        "rank": 5,
        "goal": "把量房、原始结构、门窗洞口、房间闭合轮廓和家具布置合成可审计房间平面。",
        "programIds": [
            "drawing-field-measurement",
            "drawing-existing-structure-plan",
            "drawing-room-outline-polyline",
            "drawing-door-opening-plan",
            "drawing-window-opening-plan",
            "drawing-furniture-layout-plan",
        ],
        "dependsOn": ["batch-storage-kitchen-bath-objects"],
        "checkerIds": ["checker-closed-geometry", "checker-clearance-collision", "checker-open-swing-domain"],
        "evidenceRequired": ["房间闭合轮廓", "门窗与墙体扣减关系", "家具归属、通道和门扇侵入说明"],
        "passBoundary": "只证明单房间或局部平面组合训练，不代表全屋套图通过。",
    },
    {
        "id": "batch-sheet-expression",
        "label": "图纸表达与局部套图",
        "rank": 6,
        "goal": "训练拆改、新建、地面、顶面、灯具、电气、立面和节点之间的表达关系。",
        "programIds": [
            "drawing-demolition-plan",
            "drawing-new-partition-plan",
            "drawing-floor-finish-plan",
            "drawing-rcp-plan",
            "drawing-lighting-location-plan",
            "drawing-outlet-plan",
            "drawing-kitchen-elevation",
            "drawing-bathroom-elevation",
        ],
        "dependsOn": ["batch-room-plan-composition"],
        "checkerIds": ["checker-dimension-chain", "checker-cross-sheet-consistency", "checker-readback-evidence"],
        "evidenceRequired": ["图纸类型边界", "立面 / 平面索引关系", "尺寸、标高或点位未验证项"],
        "passBoundary": "只证明局部图纸表达训练，不代表完整施工图交付。",
    },
    {
        "id": "batch-annotation-and-schedules",
        "label": "标注表格与低噪声交付",
        "rank": 7,
        "goal": "训练尺寸链、编号、图例、标题栏、材料表、FF&E 表和 checked / not_checked 汇报。",
        "programIds": [
            "annotation-dimension-chain",
            "annotation-furniture-tag",
            "annotation-legend",
            "annotation-title-block",
            "annotation-drawing-index",
            "annotation-material-schedule",
            "annotation-ffe-schedule",
            "annotation-checked-not-checked",
        ],
        "dependsOn": ["batch-sheet-expression"],
        "checkerIds": ["checker-dimension-chain", "checker-schedule-count", "checker-checked-not-checked"],
        "evidenceRequired": ["标注对象与几何对象关联", "表格数量和图面符号对账", "用户验收重点"],
        "passBoundary": "只证明交付表达训练，不替代用户反馈和真实 CAD 几何证明。",
    },
    {
        "id": "batch-cross-sheet-delivery-closure",
        "label": "跨图纸交付闭环",
        "rank": 8,
        "goal": "训练平面、立面、索引、门窗表、柜体表、材料表和图纸目录之间的对账闭环。",
        "programIds": [
            "drawing-door-window-schedule-link",
            "drawing-cabinet-schedule-link",
            "drawing-full-house-mini-set-audit",
            "annotation-door-window-tag",
            "annotation-cabinet-schedule",
            "annotation-sheet-number-scale",
            "annotation-elevation-marker",
        ],
        "dependsOn": ["batch-annotation-and-schedules"],
        "checkerIds": ["checker-cross-sheet-consistency", "checker-schedule-count", "checker-checked-not-checked"],
        "evidenceRequired": ["跨图纸引用清单", "孤立索引 / 漏表 / 数量差异报告", "用户验收和下一轮补课项"],
        "passBoundary": "只证明小套图一致性训练框架，不声明完整施工图能力或表 C 提升。",
    },
]


def training_batches(programs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    program_ids = {program["capabilityId"] for program in programs}
    rows: list[dict[str, Any]] = []
    for batch in sorted(TRAINING_BATCHES, key=lambda item: int(item["rank"])):
        rows.append(
            {
                **batch,
                "programCount": len([program_id for program_id in batch["programIds"] if program_id in program_ids]),
                "missingProgramIds": [program_id for program_id in batch["programIds"] if program_id not in program_ids],
                "evidenceBoundary": "批次依赖图只组织训练顺序和验收证据；不提升表 C、不代表检查器已实现。",
            }
        )
    return rows


ASSET_STATE_LABELS = {
    "empty": "未纳入",
    "not_applicable": "不适用",
    "planned": "计划中",
    "training": "训练中",
    "evidence": "已有证据",
    "systemized": "已沉淀",
}


AGENT_GROUP_LABELS = {
    "designer": "总设计师智能体",
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
    "cad_designer": {
        "name": "CAD Designer Agent",
        "group": "designer",
        "status": "primary_training",
        "summary": "你是训练期的总设计师智能体，负责像真实设计师一样从 CAD 基础操作成长到可调用场景、资产、执行、审计和修复流程的电子设计师。",
        "role": "你负责统筹 CAD 学徒式成长路径：先掌握基础图元和编辑命令，再调用场景智能体、资产检索、需求拆解、执行、审计、修复和沉淀流程完成设计训练。",
        "inputs": ["用户训练目标和毕业阶段", "成长路径与基础课程", "场景规则、资产检索包和案例反馈", "pipeline Agent 的输入输出与证据边界"],
        "outputs": ["本轮应训练的成长阶段", "需要调用的流程 Agent 和资产范围", "基础课程或案例训练的验收边界", "不能声称的能力和下一轮补课目标"],
        "gates": [{"label": "成长路径优先", "value": "先确认当前是基础课程、对象课程、场景组合还是专业表达，再进入具体流水线。"}, {"label": "证据边界", "value": "课程进度、案例 pass、表 C 和真实 CAD 几何证明必须分开。"}],
        "must_not": ["不得绕过 CAD_PLAN / 结构化意图直接落图。", "不得把基础课程通过说成会画施工图。", "不得把其它 Agent 当成并列最终交付主体。"],
        "calls": ["pipeline_context_curator", "pipeline_asset_retriever", "pipeline_intent", "pipeline_execute", "pipeline_audit", "pipeline_repair", "pipeline_delivery", "pipeline_learning_promoter", "residential"],
        "tips": ["每轮先判断成长阶段，再选择训练案例或基础课程。", "基础 CAD 操作必须先能被回读和审计，再向对象符号和房间组合扩展。", "用户反馈通过后再判断是否沉淀到场景规则、检查器或系统资产。"],
        "docs": ["agents/cad_designer/agent.json", "agents/cad_designer/rules.md", "docs/training/cad-designer-growth-path.md", "docs/training/cad-designer-training-plan-v2.md"],
    },
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
    *FOUNDATION_COURSES,
    *V2_TRAINING_CAPABILITIES,
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
    "foundation_command_missing": "基础命令缺口",
    "selection_scope_unclear": "选择范围不清",
    "transform_reference_error": "变换基准错误",
    "trim_offset_cleanup_gap": "偏移修剪后不洁净",
    "layer_discipline_missing": "图层纪律缺失",
    "closed_geometry_unverified": "闭合未回读",
    "readback_audit_missing": "回读审计缺失",
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
    "foundation_command_missing": "基础图元、选择或编辑命令没有形成可复盘课程时，后续对象训练会变成补丁。",
    "selection_scope_unclear": "选择集边界不清会误动已有对象或正式图层。",
    "transform_reference_error": "旋转、镜像、缩放若缺少基点和方向语义，平面对象容易翻转或错位。",
    "trim_offset_cleanup_gap": "偏移、修剪和延伸后如果不查端点、缺口和毛刺，墙体和部件会虚绿。",
    "layer_discipline_missing": "基础训练也必须遵守 CODEX_PREVIEW 和对象图层边界。",
    "closed_geometry_unverified": "闭合轮廓必须通过端点、bbox 或 gap/open endpoint 回读确认。",
    "readback_audit_missing": "没有 created handles 和审计记录，课程通过就不可复盘。",
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
    "foundation_command_missing": 88,
    "selection_scope_unclear": 76,
    "transform_reference_error": 74,
    "trim_offset_cleanup_gap": 82,
    "layer_discipline_missing": 70,
    "closed_geometry_unverified": 84,
    "readback_audit_missing": 86,
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
    "foundation_command_missing": ["cad_designer", "pipeline_intent", "pipeline_execute"],
    "selection_scope_unclear": ["cad_designer", "pipeline_execute", "pipeline_audit"],
    "transform_reference_error": ["cad_designer", "pipeline_intent", "pipeline_execute", "pipeline_audit"],
    "trim_offset_cleanup_gap": ["cad_designer", "pipeline_execute", "pipeline_audit", "pipeline_repair"],
    "layer_discipline_missing": ["cad_designer", "pipeline_execute", "pipeline_audit"],
    "closed_geometry_unverified": ["cad_designer", "pipeline_execute", "pipeline_audit"],
    "readback_audit_missing": ["cad_designer", "pipeline_audit", "pipeline_delivery"],
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
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError):
        return fallback


def training_learning_index() -> dict[str, Any]:
    ledger = read_json(training_learning_ledger_path(), {})
    if not ledger:
        return {
            "status": "missing",
            "sourceReportPaths": [],
            "acceptedItemCount": 0,
            "promotedAgentCount": 0,
            "byAgent": {},
            "byCapability": {},
        }
    return build_learning_index(ledger)


def training_acceptance_by_capability(
    learning_index: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    accepted: dict[str, dict[str, Any]] = {}
    learning_by_capability = (learning_index or training_learning_index()).get("byCapability", {})
    for path in training_acceptance_report_paths():
        report = read_json(path, {})
        if not acceptance_report_is_promotable(report):
            continue
        for item in report.get("items", []):
            if item.get("status") != "pass":
                continue
            capability_id = str(item.get("capabilityId", ""))
            if not capability_id:
                continue
            handle_count = int(item.get("handle_count", 0) or 0)
            readback_count = int(item.get("readback_count", 0) or 0)
            title = str(item.get("title") or capability_id)
            accepted[capability_id] = {
                "status": "pass",
                "source": path.resolve().relative_to(ROOT).as_posix(),
                "plainLanguageSummary": training_acceptance_plain_summary(
                    title,
                    handle_count=handle_count,
                    readback_count=readback_count,
                ),
                "queueId": report.get("queueId", ""),
                "mode": report.get("mode", ""),
                "handleCount": handle_count,
                "readbackCount": readback_count,
                "generatedAt": report.get("generated_at", ""),
                "learningPromotion": learning_by_capability.get(capability_id, {}),
                "evidenceBoundary": "训练验收证据只证明本项基础课程通过，不提升表 C，也不等于完整施工图能力。",
            }
    return accepted


def pipeline_agent_doc_map() -> dict[str, list[str]]:
    manifest = read_json(ROOT / "agents" / "pipeline" / "pipeline_manifest.json", {})
    rows: dict[str, list[str]] = {}
    for agent in manifest.get("agents", []):
        agent_id = agent.get("agent_id")
        path = agent.get("path")
        if agent_id and path:
            rows[agent_id] = [f"agents/pipeline/{path}"]
    return rows


def default_agent_docs(agent_id: str) -> list[str]:
    pipeline_docs = pipeline_agent_doc_map()
    if agent_id in pipeline_docs:
        return pipeline_docs[agent_id]
    if agent_id == "demand_side_roles":
        return ["agents/demand_side/role_agents.json", "agents/demand_side/README.md"]

    docs = [f"agents/{agent_id}/agent.json"]
    rules_path = ROOT / "agents" / agent_id / "rules.md"
    if rules_path.exists():
        docs.append(f"agents/{agent_id}/rules.md")
    return docs


def parse_iso_datetime(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def unique(items: list[str]) -> list[str]:
    result: list[str] = []
    for item in items:
        if item and item not in result:
            result.append(item)
    return result


def training_acceptance_plain_summary(
    title: str,
    *,
    handle_count: int,
    readback_count: int,
) -> str:
    subject = title or "本项训练"
    return (
        f"{subject}已完成中文 CAD 基础训练：画面使用中文标注，"
        f"全部落在 CODEX_PREVIEW，{readback_count}/{handle_count} 个 handles 已回读；"
        "同时确认未保存 DWG、未写正式图层，可作为本项训练通过证据。"
    )


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
        template["docs"] = default_agent_docs(agent_id)
    template.setdefault("tips", ["先明确输入、输出和通过门槛。", "把禁止事项写成可检查条款。", "重复失败时再晋升为测试或 Core 检查器。"])
    template.setdefault("docs", default_agent_docs(agent_id))
    return template


def agent_name(agent_id: str) -> str:
    return agent_template(agent_id)["name"]


def matrix_group(capability: dict[str, Any]) -> str:
    return GROUP_OVERRIDES.get(capability["id"], capability["group"])


def kind_label(kind: str, suffix: str) -> str:
    return {
        "foundation": f"基础课程{suffix}",
        "object": f"对象{suffix}",
        "draw": f"绘图{suffix}",
        "annotation": f"标注{suffix}",
    }.get(kind, f"训练{suffix}")


def risk_items(ids: list[str]) -> list[dict[str, str]]:
    return [{"id": item, "label": FAILURE_LABELS[item], "note": FAILURE_NOTES[item]} for item in ids]


def stage_state(capability: dict[str, Any], acceptance: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    accepted = (acceptance or {}).get(capability["id"])
    if accepted:
        learned = accepted.get("learningPromotion", {}).get("status") == "promoted"
        stage = dict(TRAINING_STAGES[4] if learned else TRAINING_STAGES[3])
        acceptance_summary = accepted.get("plainLanguageSummary") or training_acceptance_plain_summary(
            capability["name"],
            handle_count=int(accepted.get("handleCount", 0) or 0),
            readback_count=int(accepted.get("readbackCount", 0) or 0),
        )
        learning_summary = accepted.get("learningPromotion", {}).get("plainLanguageSummary", "")
        stage["note"] = f"{acceptance_summary} {learning_summary}".strip() if learned else acceptance_summary
        stage["evidence"] = accepted
        return stage
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


def is_fully_complete_training_program(
    state: dict[str, Any],
    accepted: dict[str, Any] | None,
) -> bool:
    if not accepted:
        return False
    return (
        accepted.get("status") == "pass"
        and state.get("id") == "systemized"
        and accepted.get("learningPromotion", {}).get("status") == "promoted"
    )


def training_plan_visibility(programs: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [program for program in programs if program.get("isFullyComplete")]
    return {
        "defaultMode": "hide_fully_completed",
        "fullyCompletedCount": len(completed),
        "visibleByDefaultCount": len(programs) - len(completed),
        "completionRule": "只有 trainingAcceptance.status=pass、learningPromotion.status=promoted 且 stageState.id=systemized 时才默认折叠。",
    }


def asset_state(state: str, note: str, *, applicable: bool = True) -> dict[str, Any]:
    return {"state": state, "label": ASSET_STATE_LABELS[state], "note": note, "applicable": applicable}


def asset_states(
    capability: dict[str, Any],
    acceptance: dict[str, dict[str, Any]] | None = None,
) -> dict[str, dict[str, str]]:
    pipeline = set(capability["pipeline"])
    if capability["kind"] == "foundation":
        accepted = (acceptance or {}).get(capability["id"])
        learned = accepted and accepted.get("learningPromotion", {}).get("status") == "promoted"
        raw = asset_state(
            "not_applicable",
            "基础操作训练不需要标准图块；以 CAD_PLAN、命令参数、created handles、bbox 和回读审计证明。",
            applicable=False,
        )
        knowledge = asset_state(
            "evidence" if learned else "planned",
            (
                "已从训练验收报告沉淀常识证据：中文标注、画布避让、CODEX_PREVIEW、handles 回读和 checked/not_checked 已写入责任智能体记忆与 Prompt。"
                if learned
                else f"围绕“{capability['focus']}”整理命令语义、参数边界、图层纪律和审计口径。"
            ),
        )
        trained = "evidence" if accepted else "planned" if capability["priority"] in {"P0", "P1"} else "empty"
        system = asset_state(
            "not_applicable",
            "基础操作不沉淀为自产资产；可沉淀 Prompt 约束、检查器、失败经验或通用规则。",
            applicable=False,
        )
        return {
            "raw": raw,
            "knowledge": knowledge,
            "trained": asset_state(
                trained,
                (
                    accepted.get("plainLanguageSummary", "")
                    if accepted
                    else f"基础课程训练目标：{capability['next']}。"
                    if trained != "empty"
                    else "尚未进入基础课程训练。"
                ),
            ),
            "system": system,
        }

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


def training_objective(capability: dict[str, Any]) -> str:
    if capability["kind"] == "foundation":
        return f"围绕“{capability['focus']}”开一轮基础操作训练，以回读和审计证据证明命令、参数和图层边界。"
    return f"围绕“{capability['focus']}”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。"


def success_criteria(capability: dict[str, Any]) -> list[str]:
    if capability["kind"] == "foundation":
        return [
            "能把中文基础操作需求转成结构化意图或 CAD_PLAN。",
            "能回读 created handles、entity type、bbox、关键端点、闭合 / gap / open endpoint 等机器证据。",
            "如进入真实落图，必须只写 CODEX_PREVIEW，并保留 validate、dry-run、回读或审计证据。",
        ]
    return [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。",
    ]


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


def training_programs(learning_index: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    rows = []
    acceptance = training_acceptance_by_capability(learning_index)
    for item in CAPABILITIES:
        agent_ids = capability_agent_ids(item)
        state = stage_state(item, acceptance)
        accepted = acceptance.get(item["id"])
        fully_complete = is_fully_complete_training_program(state, accepted)
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
                "assetStates": asset_states(item, acceptance),
                "trainingAcceptance": accepted or {},
                "learningPromotion": (accepted or {}).get("learningPromotion", {}),
                "isFullyComplete": fully_complete,
                "completionFoldState": "folded_by_default" if fully_complete else "visible_by_default",
                "completionFoldReason": (
                    "训练已验收、已沉淀到责任智能体，默认折叠以突出下一轮计划。"
                    if fully_complete
                    else "仍未同时满足验收通过、学习沉淀和 systemized 阶段，默认保留在下一轮视野中。"
                ),
                "trainingObjective": training_objective(item),
                "successCriteria": success_criteria(item),
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


def agent_learning_docs(agent_id: str, learning_index: dict[str, Any] | None = None) -> list[str]:
    learning = (learning_index or training_learning_index()).get("byAgent", {}).get(agent_id, {})
    return [str(path) for path in learning.get("sourceRefs", []) if path]


def agent_profiles(programs: list[dict[str, Any]], learning_index: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    profiles = []
    learning_by_agent = (learning_index or training_learning_index()).get("byAgent", {})
    for agent_id in AGENT_PROMPTS:
        template = agent_template(agent_id)
        related = [program for program in programs if agent_id in program["responsibleAgentIds"]]
        learning = learning_by_agent.get(agent_id, {})
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
                "learningPromotion": learning,
                "maturity": {},
                "docs": unique([*template["docs"], *agent_learning_docs(agent_id, learning_index)]),
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


def prompt_contracts(learning_index: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    rows = []
    for agent_id in AGENT_PROMPTS:
        template = agent_template(agent_id)
        source_paths = unique([*template["docs"], COMMON_PROMPT_CONTRACT, *agent_learning_docs(agent_id, learning_index)])
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
                "sourceRefs": [{"path": path, "title": "源文件", "kind": "文件", "meaning": "用于维护该智能体的中文 Prompt 契约。", "changeGuide": "修改后重新生成本页数据并复查页面。"} for path in source_paths],
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
    data = read_json(COVERAGE_PATH, {})
    summary = data.get("summary", {})
    return {
        "label": "表 C 真实 CAD 机器快照",
        "generatedAt": data.get("generated_at", ""),
        "sourcePath": "output/validation_runs/capability-lab/cad_capability_coverage.json",
        "sourceExists": COVERAGE_PATH.exists(),
        "cadProofCoveragePercent": summary.get("cad_proof_coverage_percent", 0),
        "cadStrengthIndexPercent": summary.get("cad_strength_index_percent", 0),
        "sceneFragmentStrengthPercent": summary.get("scene_fragment_strength_percent", 0),
        "showcaseReadinessPercent": summary.get("showcase_readiness_percent", 0),
        "headlinePercent": summary.get("cad_strength_headline_percent", 0),
        "highestProvenLadder": summary.get("highest_proven_ladder_level", "unknown"),
        "note": "这是 registry 和 coverage JSON 的机器指标快照，只能说明表 C 口径；不能和训练计划成熟度、智能体 Prompt 成熟度混算。",
    }


def workbench_sync_status(generated_at: str, table_c: dict[str, Any]) -> dict[str, Any]:
    coverage_generated_at = table_c.get("generatedAt", "")
    generated_dt = parse_iso_datetime(generated_at)
    coverage_dt = parse_iso_datetime(coverage_generated_at)
    generated_after_coverage = bool(generated_dt and coverage_dt and generated_dt >= coverage_dt)
    return {
        "mode": "static_snapshot",
        "generatedAt": generated_at,
        "dataPath": "capability-map-data.js",
        "htmlPath": "capability-map.html",
        "coverageSourcePath": table_c.get("sourcePath", "output/validation_runs/capability-lab/cad_capability_coverage.json"),
        "coverageGeneratedAt": coverage_generated_at,
        "coverageSourceExists": bool(table_c.get("sourceExists")),
        "generatedAfterCoverage": generated_after_coverage,
        "recommendedCommand": "$py scripts\\sync_training_workbench.py",
        "agentCheckCommand": "$py scripts\\run_training_workbench_agent_check.py",
        "launcher": "start_training_workbench.bat",
        "hotUpdate": {
            "mode": "http_polling",
            "description": "通过 bat 启动本地 http.server 后，页面会轮询 capability-map-data.js；检测到新快照时提示刷新。",
        },
        "evidenceBoundary": "本页由同步脚本生成，只显示训练状态和表 C 快照；真实 CAD 能力仍以 coverage JSON、registry 和 created-handle 回读为准。",
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
        {"title": "总设计师 Agent", "path": "agents/cad_designer/agent.json + rules.md", "desc": "训练期顶层目标，像设计师一样从基础 CAD 操作成长到调用多 Agent 流水线。"},
        {"title": "成长路径", "path": "docs/training/cad-designer-growth-path.md", "desc": "定义第一阶段毕业目标、基础课程、能力护照和证据边界。"},
        {"title": "V2 训练地图", "path": "docs/training/cad-designer-training-plan-v2.md", "desc": "正式训练前的大体量训练地图扩容，保留六类筛选并扩成 217 个训练计划项；V2.1 补训练批次依赖图和验收器骨架。"},
        {"title": "训练事实源清单", "path": "docs/training/training-sources.json", "desc": "登记训练验收报告、队列状态、learning ledger、Agent memory 和派生快照边界。"},
        {"title": "场景 Agent", "path": "agents/<scene>/agent.json + rules.md", "desc": "领域词汇、偏好、场景边界和训练状态。"},
        {"title": "Pipeline Agent", "path": "agents/pipeline/*/agent.json", "desc": "上下文、资产、视觉意图、执行、审计、修复、沉淀等链路职责。"},
        {"title": "能力覆盖快照", "path": "output/validation_runs/capability-lab/cad_capability_coverage.json", "desc": "表 C 机器指标来源，不和本页阶段混用。"},
        {"title": "标准图库 raw", "path": "standard_cad_library_raw/", "desc": "外来参考素材入口，默认 reference_only，不直接算系统能力。"},
        {"title": "训练反馈", "path": "projects/<case>/feedback.md + docs/training/training-errors.md", "desc": "点对点训练和失败复盘的沉淀位置。"},
    ]


def foundation_courses(programs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_capability = {program["capabilityId"]: program for program in programs}
    rows = []
    for item in sorted(FOUNDATION_COURSES, key=lambda course: int(course.get("courseOrder", 0))):
        program = by_capability.get(item["id"], {})
        rows.append(
            {
                "id": item["id"],
                "name": item["name"],
                "order": item["courseOrder"],
                "growthStageId": item["growthStageId"],
                "programId": program.get("id", f"program-{item['id']}"),
                "priority": item["priority"],
                "focus": item["focus"],
                "nextTrainingTarget": item["next"],
                "responsibleAgentIds": capability_agent_ids(item),
                "passGate": [
                    "能从结构化意图进入 validate / dry-run 或声明 deferred。",
                    "若真实落图，必须只写 CODEX_PREVIEW 并保留 created handles / readback 线索。",
                    "必须说明 checked / not_checked，不把课程通过说成施工图能力。",
                ],
                "evidenceBoundary": "基础课程只证明 CAD Designer Agent 的训练进度；不提升表 C、不替代案例用户验收、不代表完整施工图能力。",
            }
        )
    return rows


def capability_passport(programs: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, int] = {}
    priorities: dict[str, int] = {}
    for program in programs:
        groups[program["matrixGroup"]] = groups.get(program["matrixGroup"], 0) + 1
        priorities[program["priority"]] = priorities.get(program["priority"], 0) + 1
    return {
        "label": "能力护照",
        "totalPrograms": len(programs),
        "groupCounts": groups,
        "priorityCounts": priorities,
        "meaning": "现有能力矩阵保留为 CAD Designer Agent 的能力护照；它说明训练覆盖面，不说明真实 CAD 几何通过率。",
    }


def designer_agent_summary(programs: list[dict[str, Any]]) -> dict[str, Any]:
    template = agent_template("cad_designer")
    return {
        "id": "cad_designer",
        "name": template["name"],
        "status": template["status"],
        "statusLabel": AGENT_STATUS_LABELS[template["status"]],
        "roleSummary": template["summary"],
        "graduationTarget": "第一阶段毕业目标：电子设计师雏形。正式训练前 V2 地图已扩到 217 项；训练仍从 CAD 基础操作开始，再进入对象、房间、专业表达和审计自检。",
        "firstStageGoal": DESIGNER_GROWTH_STAGES[0],
        "trainingPlanVersion": "V2",
        "trainingPlanDoc": "docs/training/cad-designer-training-plan-v2.md",
        "callableAgents": template["calls"],
        "foundationCourseIds": [course["id"] for course in FOUNDATION_COURSES],
        "capabilityPassport": capability_passport(programs),
        "sourceRefs": template["docs"],
        "evidenceBoundary": "Designer Agent 课程进度只代表训练路径和验收安排，不提升表 C、不替代真实 CAD created-handle 回读、不代表用户项目或施工图已通过。",
    }


def build_data() -> dict[str, Any]:
    generated_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    table_c = table_c_boundary()
    learning = training_learning_index()
    programs = training_programs(learning)
    profiles = agent_profiles(programs, learning)
    designer = designer_agent_summary(programs)
    return {
        "schemaVersion": 2,
        "generatedAt": generated_at,
        "designerAgent": designer,
        "growthStages": DESIGNER_GROWTH_STAGES,
        "foundationCourses": foundation_courses(programs),
        "trainingBatches": training_batches(programs),
        "validationCheckers": VALIDATION_CHECKERS,
        "trainingStages": TRAINING_STAGES,
        "trainingStageColumns": TRAINING_STAGE_COLUMNS,
        "capabilityCatalog": capability_catalog(),
        "trainingPrograms": programs,
        "trainingPlanVisibility": training_plan_visibility(programs),
        "agentProfiles": profiles,
        "promptContracts": prompt_contracts(learning),
        "trainingLearning": learning,
        "trainingSources": training_source_rows(),
        "tableCBoundary": table_c,
        "coverageSnapshot": table_c,
        "workbenchSync": workbench_sync_status(generated_at, table_c),
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


def write_data(output: Path = OUTPUT) -> dict[str, Any]:
    data = build_data()
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(f"window.CAD_CAPABILITY_MAP_DATA = {payload};\n", encoding="utf-8")
    return data


def main() -> None:
    write_data(OUTPUT)
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
