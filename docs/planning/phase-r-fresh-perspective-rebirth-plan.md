# Phase R Fresh Perspective Rebirth Plan

状态：新鲜视角评审后新增，执行拆单已细化
最后同步：2026-05-26

> 本文是 Phase R 的辅助执行剧本，不是独立 PlanMD。Phase R 是否优先、何时退出、下一步进入哪条工作队列，以根目录 `CORE_RESTRUCTURE_PLAN.md` 为准；本文只展开“重生式开发”的背景、角色和执行参考。

## 目标

把多 agent 新鲜视角评审制度化，并把下一轮深度开发聚焦到四条可验证主线：

1. CAD 实体能力契约和块插入闭环。
2. 办公基础业务场景 Alpha。
3. 图块库、对象语义、图层/样式标准。
4. 对象级 / 微场景 / 场景级 benchmark 和证据状态门禁。

## 已细化执行入口

本计划已经拆成更小的执行文档。后续进入 Phase R 时，不要只读本文，应按任务打开对应文档：

| 文档 | 用途 |
| --- | --- |
| `phase-r-rebirth-implementation-plan.md` | Phase R R0-R5 执行总表、任务编号、证据状态和同步清单 |
| `phase-r-cad-capability-contract.md` | 基础 CAD 实体能力契约、`insert_block_alpha` 草案和 readback 门禁 |
| `phase-r-block-library-roadmap.md` | `BLOCK_LIBRARY v0.2`、OBJECT_SPEC、drawing standard profile 和受控测试块路线 |
| `phase-r-office-benchmark-cases.md` | 办公桌、椅、电脑桌、柜体、入口、通道和失败样本 benchmark |
| `../governance/multi-agent-contribution.md` | 多 agent 协作协议、可写边界和场景发现升级为 Core 的流程 |
| `../onboarding/first-handoff.md` | 新 agent / 新开发者接手时的最短入口和不可声称边界 |

## 角色矩阵

后续触发 Phase R 时，至少创建这些只读评审角色：

| 角色 | 只读输入 | 输出 |
| --- | --- | --- |
| CAD 自动化与 COM 执行底座专家 | Phase W、CAD validation、CORE_STATUS | 实体能力契约、真实 CAD 补验优先级 |
| CAD 图块库与制图标准专家 | `libraries/blocks/`、`core/block_engine/`、schemas、object defaults | 图块 schema、对象语义、图层/样式标准建议 |
| 空间设计 / 办公工装业务专家 | Phase X/Y、office/commercial agent、scene rules | 基础业务闭环、对象组合、失败场景 |
| 平台架构 / Agent 产品负责人 | README、短入口、主计划、roadmap/status | 新人接手路径、协作协议、主计划结构 |
| 验证 / Benchmark 专家 | verification docs、benchmark runner、Phase W/Y | benchmark 分层、硬门禁、证据状态命名 |

所有角色默认只读，不允许修改文件。建议输出进入 `docs/reviews/fresh-eyes-review-YYYY-MM-DD.md`。

## 新主线 R1：CAD 能力契约

目标：把当前基础图元探针固化为面向 CAD_PLAN 的稳定契约。

必须定义：

| 实体 | 写入字段 | 回读字段 | 验收重点 |
| --- | --- | --- | --- |
| line | start/end/layer | handle/type/start/end/bbox/layer | 长度、端点、图层 |
| rectangle | bbox/layer | handle group/bbox/layer | 宽高、基点、数量 |
| circle | center/radius/layer | center/radius/bbox/layer | 半径、中心、bbox |
| arc | center/radius/start/end/layer | center/radius/angle/bbox/layer | 角度、半径、方向 |
| polyline | points/closed/layer | points/closed/bbox/layer | 闭合性、点数、bbox |
| text | content/position/style/layer | text/base point/layer | 内容、位置、样式 |
| dimension | points/text/layer | dimension count/bbox/layer | 数量、关联位置 |

硬边界：

- 只有真实 CAD readback 能证明几何准确。
- 截图只能是视觉辅助。
- 新实体类型如果当轮没有真实 CAD 回读，必须登记 deferred verification。

## 新主线 R2：块插入和图块库设计

目标：从参数化 fallback 走向可控 block insertion alpha。

图块库需要补强字段：

- `units`
- `schema_version`
- `block_version`
- `source`
- `cad_identity`
- `anchor_points`
- `connection_points`
- `footprint_2d`
- `clearance_zones`
- `symbol_2d`
- `attributes`
- `layer_bindings`
- `style_bindings`
- `validation`

受控推进顺序：

1. 扩展 `BLOCK_LIBRARY` / `OBJECT_SPEC` / `CAD_PLAN` 的块引用设计。
2. 定义 layer preset、text style、dim style、hatch style。
3. 支持 block insertion intent 到 CAD_PLAN。
4. 用受控测试块做真实 CAD 插入和 readback。
5. 再做属性块。
6. 再做 hatch。
7. 最后形成 `drawing_standard_profile`。

不得做：

- 不直接接真实公司块库。
- 不把真实块库路径、块名映射、属性规则写进场景 Agent。
- 不把 block insertion alpha 和基础图元 `cad_capability_verified` 混为一谈。

## 新主线 R3：办公基础闭环 Alpha

目标：用非常朴素但真实的办公/工装样本打穿业务闭环。

最低对象集合：

- `office_desk`
- `office_chair`
- `computer_desk`
- `storage_cabinet`
- `file_cabinet`
- `main_aisle`
- `entry_clearance`
- `chair_pullback_clearance`
- `cabinet_front_clearance`
- `no_place_zone`

必须模拟的场景：

| 场景 | 目的 | 预期结果 |
| --- | --- | --- |
| 小办公室单入口 | 2-4 张桌、椅、电脑位、文件柜 | 入口避让、椅后通道、柜前净空均可解释 |
| 长条形办公室 | 沿墙或中轴工位 | 主通道连续，不切断通行 |
| 有障碍柱/避让区 | no-place-zone | 桌柜不压避让区 |
| 入口接待/等候 | 前台或接待桌靠近入口 | 不挡门、不让访客动线穿过办公位 |
| 办公桌 + 背柜 | 柜体靠墙和柜前空间 | 椅后与柜前净空不冲突 |
| 会议/电脑桌混合 | 会议椅、屏幕墙/白板 | 会议区与办公区动线可解释 |
| 失败样本 | 空间太小、对象过多 | 输出 blocked/invalid 和结构化失败原因 |

场景 Agent 只负责：

- 业务词汇。
- 默认尺度偏好。
- 对象组合语义。
- 候选排序权重。
- 业务解释模板。
- 对 `libraries/` 中对象/块元数据的权重选择。

场景 Agent 不得实现：

- 碰撞检测。
- 通道生成。
- 多边形/净空算法。
- CAD_PLAN 校验、dry-run、执行、截图、回读。
- 真实项目数据或公司块库本体。

## 新主线 R4：Benchmark 与证据状态

目标：把简单办公对象和失败场景变成可重复 benchmark。

三层 benchmark：

| 层级 | 示例 | 验收 |
| --- | --- | --- |
| 对象级 | desk、chair、computer_desk、cabinet | OBJECT_SPEC 尺寸、fallback、CAD_PLAN 对象数和 bbox |
| 微场景 | single_desk_chair、computer_desk_pair、two_workstations、tight_room_blocked、door_clearance_conflict | 对象关系、通道、冲突或 blocked 原因 |
| 场景级 | office blank-shell workflow | candidate_count、zone_count、placement_count、object_types、failed_check_count、cad_plan_count |

证据状态命名建议：

- `benchmark_pass_non_cad`
- `dry_run_valid_plan_only`
- `screenshot_captured_visual_only`
- `readback_geometry_verified`

报告应显式写：

```json
{
  "geometry_accuracy": "not_verified_without_cad_readback",
  "screenshot_role": "visual_aid_only"
}
```

## 新主线 R5：平台协作与新人接手

目标：让新 agent 不读完整历史也能知道从哪开始、不能说什么、改哪里。

建议新增或强化：

- `docs/onboarding/first-handoff.md`
- `docs/governance/multi-agent-contribution.md`
- `docs/reviews/fresh-eyes-review-YYYY-MM-DD.md`
- 主计划中的当前可信基线索引。
- Phase 状态语义。
- Decision Gate。
- Interface Ownership Map。
- Alpha 判定结构。

## 主计划结构建议

`CORE_RESTRUCTURE_PLAN.md` 应继续保持索引，但新增五个短表：

1. 当前可信基线。
2. Phase 状态语义。
3. Decision Gates。
4. Interface Ownership Map。
5. Alpha 里程碑判定。

## 验证方式

本文作为 Phase R 的上层辅助剧本时，主要验证文档引用、证据口径和主线挂载是否正确；不因为本文存在就声称新增功能完成。若实际执行 R-CAD、R-BLOCK、R-OFFICE 或 R-COMP 代码任务，必须回到 `CORE_RESTRUCTURE_PLAN.md` 的活跃队列和对应执行文档，按测试、benchmark 或真实 CAD readback 重新验证。

```powershell
rg -n "Phase R|Fresh|fresh-eyes|office_desk|computer_desk|BLOCK_LIBRARY|geometry_accuracy|readback_geometry_verified" CORE_RESTRUCTURE_PLAN.md CORE_CONTEXT_BRIEF.md CAD_AGENT_STATUS.md CORE_STATUS.md README.md docs/planning docs/reviews docs/governance docs/onboarding
rg -n "TB[D]|TO[D]O|以后再[说]|补一[下]|随[便]|先占[位]" CORE_RESTRUCTURE_PLAN.md CORE_CONTEXT_BRIEF.md CAD_AGENT_STATUS.md CORE_STATUS.md README.md docs/planning docs/reviews docs/governance docs/onboarding
```

## 退出标准

- 多 agent 新鲜视角已记录到 `docs/reviews/`。
- Phase R 已挂入 `CORE_RESTRUCTURE_PLAN.md` 的 Phase 执行入口。
- Phase R 已拆成执行总表、CAD 能力契约、图块库路线、办公 benchmark、协作治理和新人接手入口。
- 主计划包含可信基线、Phase 状态、Decision Gate、接口归属和 Alpha 判定结构。
- `CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md` 已同步。
- 仍明确：本文只定义 Phase R 方向和执行入口；任何代码、benchmark 或真实 CAD 结论都必须看对应提交和证据，不扩大 Phase W baseline 或 3 个简单组合案例的结论。
