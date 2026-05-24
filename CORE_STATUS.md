# Core Status

最后更新：2026-05-25

本文追踪通用 CAD Agent Core Lab 的底座能力状态。当前目标是先把仓库从“执行层脚手架”整理成“通用底座优先、场景 Agent 轻量化”的结构，而不是扩写某一个工装、家装或店铺 Agent。

## 状态口径

| 状态 | 含义 |
| --- | --- |
| prototype | 已有最小闭环或脚本原型，可以作为迁移来源，但接口和目录仍可能调整 |
| scaffold | 已有目录或文档占位，职责明确，但核心逻辑尚未实现 |
| not_started | 仅在路线图或架构中定义，尚未开始实现 |
| blocked | 已知依赖缺失或验证路径缺失，不能继续声称可用 |

## 能力矩阵

| 能力 | 状态 | 当前依据 | 下一步 |
| --- | --- | --- | --- |
| CAD execution | prototype | `core/execution/execute_plan.py` 可执行最小 `CAD_PLAN` 并默认写入 `CODEX_PREVIEW`；`scripts/execute_plan.py` 保留兼容包装器 | 补更多对象类型与正式实体回读 |
| preview safety | prototype | 规则要求默认预览层、不保存、不覆盖、不删正式实体 | 抽象到 `core/safety`，形成可测试策略 |
| validate | prototype | `core/plan_engine/validate_plan.py` 已可校验测试柜 CAD_PLAN；旧 `scripts/validate_plan.py` 兼容 | 扩展到高层模型 |
| dry-run | prototype | `core/plan_engine/dry_run_plan.py` 已可预演测试柜；旧 `scripts/dry_run_plan.py` 兼容 | 统一输出格式 |
| self_check | prototype | `core/verification/self_check.py` 已作为基础自检入口；旧 `scripts/self_check.py` 兼容 | 补更多环境探针 |
| render_preview | prototype | `core/verification/render_preview.py --check` 和截图入口已建立；旧 `scripts/render_preview.py` 兼容 | 连接实体回读报告 |
| CAD IO adapter | prototype | `core/cad_io/autocad_com.py` 可连接 AutoCAD COM；旧 `drivers/` 兼容 | 设计统一驱动接口 |
| entity readback | not_started | 仅有 `scripts/inspect_dwg.py` 方向或占位 | 定义实体读取协议和 `VERIFICATION_REPORT` |
| schemas | scaffold | `core/schemas/` 已有 CAD_PLAN、CAD_CONTEXT、CAD_OBJECT 兼容副本；高层模型未建 | 新增 DESIGN_BRIEF、DRAWING_MODEL 等 schema |
| drawing_model | not_started | 仅在 `CORE_RESTRUCTURE_PLAN.md` 定义 | 建立 `DRAWING_MODEL` schema 和最小提取样例 |
| project_model | scaffold | 职责已定义，尚无 schema 与实现 | 建立 `PROJECT_MODEL` schema 与合并规则 |
| object_engine | not_started | 尚无参数化对象生成核心 | 先做柜子、货架、桌子最小对象规格 |
| style_engine | not_started | 尚无风格到绘制规则转换 | 先定义现代、欧式、极简风格配置 |
| block_engine | not_started | 尚无公司图库块元数据核心 | 定义 `BLOCK_LIBRARY` schema 和登记流程 |
| layout_engine | not_started | 尚无通用布局、碰撞、通道检查 | 先做边界内布置和基础碰撞检查 |
| proposal_engine | not_started | 尚无方案说明层 | 定义 `DESIGN_PROPOSAL`，先说明再落图 |
| plan_engine | scaffold | validate/dry-run 原型可迁移 | 负责高层模型到 CAD_PLAN 的转换 |
| verification | scaffold | 自检、截图、未来回读都应归入此处 | 输出统一 `VERIFICATION_REPORT` |
| safety | scaffold | 安全规则分散在 AGENTS 和 CAD_AGENT_RULES | 形成所有 Agent 必须遵守的安全门 |
| commercial_fitout_agent | scaffold | `agents/commercial_fitout/` 已建立轻量脚手架和两个 workflow 名称 | 等 Core 可复用后只写场景差异 |
| residential_agent | scaffold | `agents/residential/` 已建立轻量脚手架 | 等 Core 可复用后只写场景差异 |

## 当前结论

当前仓库已经具备 Core 执行底座早期原型，但还没有形成完整的设计大脑。后续 70%-80% 的开发应进入 `core/`：数据模型、图纸理解、项目模型、对象、风格、图库块、布局、方案、计划、执行、验证和安全。

场景 Agent 只能保持轻量：它们复用 Core，只补场景词汇、默认参数、业务偏好、专用工作流和少量专用规则。

`CORE_RESTRUCTURE_PLAN.md` 已从第一轮重装设计草案修剪为剩余工作计划。后续读取它时，应把它当作“还没做什么”的清单，而不是已完成迁移的待办。

## 遗留目录

第一轮重装保留了两个遗留目录，避免一次迁移同时改变过多引用：

- `cad_agent/`：旧通用工作流/安全/Schema 说明，待第二轮收束到 `docs/architecture/` 与 `core/safety/`。
- `libraries/domains/`：旧行业包占位，待第二轮审查后拆分到 `agents/` 或 `libraries/domain_presets/`。

保留它们不是新主线。后续新增通用能力仍应进入 `core/`，新增场景差异仍应进入 `agents/`。

## 近期风险

- 第一轮迁移已建立兼容包装器；后续移除旧入口前必须先更新所有文档和测试。
- `cad_agent/` 与 `libraries/domains/` 暂留为遗留目录，第二轮需要单独收束。
- `entity readback` 尚未完成，现阶段不能把截图或执行返回值等同于完整几何验收。
- 若过早扩写工装或家装 Agent，容易把通用能力写死到单一场景。
