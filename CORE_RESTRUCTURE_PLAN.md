# CAD Agent Core Remaining Work Plan

状态：第一轮仓库重装后剩余计划

本文由原 `CORE_RESTRUCTURE_PLAN.md` 修剪而来。第一轮大规模仓库重装已经完成：`core/`、`agents/`、`libraries/`、`projects/`、`tests/core/` 等结构已建立，执行/校验/预演/截图/自检/驱动能力已迁入 Core，并保留旧入口兼容。

因此，本文不再重复已完成的重装步骤，只保留尚未完成、后续仍要推进的 Core 工作。

## 1. 仍需遵守的总原则

```text
通用 CAD Agent Core Lab
= 大通用底座 + 轻量场景 Agent + 项目案例验证场
```

- 通用能力优先进入 `core/`。
- 场景 Agent 只保留轻量差异，不复制 Core 能力。
- 跨场景资源进入 `libraries/`。
- 真实项目资料进入 `projects/`。
- CAD-MCP / AutoCAD / ZWCAD 是执行工具，不是系统大脑。
- `CAD_PLAN` 是最终落图指令，不是设计大脑。
- 所有绘图默认保护原图，先走 `CODEX_PREVIEW`、validate、dry-run、验证。

判断规则：

```text
两个以上场景会复用 -> core
只有一个场景会用 -> agents/<scenario>
图库、材料、风格、尺寸、人体工学、图层标准 -> libraries
真实项目输入输出 -> projects
架构、路线、决策记录 -> docs
```

## 2. 第二轮遗留目录收束

第一轮为了降低风险，暂时保留了两个遗留目录。第二轮需要单独处理。

### 2.1 收束 `cad_agent/`

当前状态：

```text
cad_agent/
  CAD_WORKFLOW.md
  CAD_PLAN_SCHEMA.md
  SAFETY_RULES.md
```

目标：

- 将架构说明类内容并入 `docs/architecture/`。
- 将安全规则类内容并入 `core/safety/` 或其 README。
- 保留必要兼容说明，避免旧文档引用断裂。

完成标准：

- `cad_agent/` 不再作为新开发入口。
- `README.md`、`AGENTS.md`、`CORE_STATUS.md` 中的入口都指向 Core。
- 如果保留 `cad_agent/`，必须明确标注为 legacy。

### 2.2 收束 `libraries/domains/`

当前状态：

```text
libraries/domains/
```

目标：

- 判断每个 domain 文件是场景 Agent 差异，还是通用 domain preset。
- 场景差异迁入对应 `agents/<scenario>/`。
- 通用默认值可迁入 `libraries/domain_presets/`。
- 不再让旧 domain 包承担场景 Agent 职责。

完成标准：

- `libraries/domains/` 要么消失，要么改名并标注为兼容/预设目录。
- 工装、家装、办公等真实场景规则只在 `agents/` 中轻量维护。

## 3. Core 高层数据模型

下一批应优先建立高层 schema，因为它们决定后续“设计大脑”的边界。

待建 schema：

- `design_brief.schema.json`
- `drawing_model.schema.json`
- `project_model.schema.json`
- `object_spec.schema.json`
- `style_profile.schema.json`
- `block_library.schema.json`
- `layout_proposal.schema.json`
- `design_proposal.schema.json`
- `verification_report.schema.json`

完成标准：

- 每个 schema 有最小 example。
- 每个 example 可被校验。
- 高层模型和最终 `CAD_PLAN` 的职责边界清楚。

## 4. Entity Readback 与验证报告

当前 `core/verification/inspect_dwg.py` 仍偏脚手架。

目标：

- 回读 CAD 实体。
- 检查图层、数量、尺寸、范围、文字和标注。
- 生成 `VERIFICATION_REPORT`。
- 将截图证据和实体回读证据关联起来。

完成标准：

- 能检查 `CODEX_PREVIEW` 图层新增实体。
- 能报告关键尺寸。
- 能区分“已执行”“已截图”“已几何验证”。
- 没有验证证据时，不声称图纸已经画准。

## 5. Object Engine 与 Style Engine

目标是让通用底座能从白话生成参数化对象，而不是只画简单矩形。

第一批对象：

- cabinet
- shelf
- table

第一批风格：

- modern
- european
- minimal

示例目标：

```text
画一个欧式风格柜子，宽 1800，高 2400，深 600。
```

完成标准：

- 生成 `OBJECT_SPEC`。
- 生成对象方案说明。
- 转换成 CAD_PLAN。
- 绘制到 `CODEX_PREVIEW`。
- 验证主要尺寸、图层和关键构成。

## 6. Block Engine

目标是管理公司标准图库块，让布局和方案生成能复用真实块资源。

待实现：

- 块分类。
- 块尺寸。
- 插入点。
- 旋转规则。
- 避让范围。
- 适用场景。
- 按用途选择块。
- 插入块到预览层。

完成标准：

- 有 `BLOCK_LIBRARY` schema。
- 能登记一批块。
- 能按用途筛选块。
- 能通过 Core 执行层插入预览。

## 7. Layout Engine

目标是在给定边界、入口和对象集合时生成基础布局，不绑定工装或家装。

待实现：

- 边界内布置。
- 碰撞检查。
- 通道宽度检查。
- 对齐墙体。
- 主入口与主视觉关系。
- 多候选方案。
- 候选方案评分。

完成标准：

- 可输出 `LAYOUT_PROPOSAL`。
- 可说明布置依据和不确定点。
- 场景 Agent 只补偏好，例如店铺入口展示优先、卧室床头靠实墙。

## 8. Drawing Analysis

目标是从已有 DWG/PDF 或当前 CAD 文档生成 `DRAWING_MODEL`。

待实现：

- 读取图层。
- 读取实体数量。
- 读取文字。
- 读取尺寸。
- 读取块。
- 初步识别墙体、门窗、柱子、空间名、边界候选。
- 输出不确定点。

完成标准：

- 能生成图纸理解报告。
- 能把图纸信息转换为 `PROJECT_MODEL` 的输入。

## 9. Project Model

目标是把图纸实体、用户需求、项目类型和场景偏好合并为统一项目模型。

应包含：

- 单位、比例、图层约定。
- 项目类型。
- 空间列表。
- 空间边界。
- 入口、墙体、门窗、柱子。
- 可布置区域和不可用区域。
- 已有对象。
- 用户需求。
- 推断信息。
- 待确认问题。

完成标准：

- 有 `PROJECT_MODEL` schema。
- 能从 brief + drawing_model 生成最小 project_model。
- 后续布局、立面、对象生成都基于 project_model，而不是直接读白话或 CAD 实体。

## 10. Proposal Engine

目标是不直接画图，而是先生成方案说明。

`DESIGN_PROPOSAL` 应回答：

- 准备做什么。
- 为什么这样做。
- 哪些来自图纸。
- 哪些来自用户。
- 哪些是系统推断。
- 哪些需要确认。
- 用户确认后会生成哪些 CAD_PLAN。

完成标准：

- 支持从 `DESIGN_BRIEF + PROJECT_MODEL` 生成 proposal。
- proposal 可被 validate。
- proposal 可转 CAD_PLAN。

## 11. 轻量场景 Agent 后续工作

当前 6 个 Agent 只是 scaffold，不代表场景能力已经完成。

后续原则：

- 不在 Agent 中复制 Core。
- 只写场景词汇、默认参数、业务偏好、专用 workflow。
- 真实能力必须由 Core 提供。

优先验证 Agent：

```text
agents/commercial_fitout/
```

可先验证两个 workflow：

- `existing_plan_to_elevation`
- `blank_store_to_layout`

但这两个 workflow 只能作为 Core 的验证样本，不应把仓库主线改成工装专用。

## 12. 下一步推荐顺序

推荐按这个顺序推进：

1. 收束 `cad_agent/` 与 `libraries/domains/` 遗留目录。
2. 建立 Core 高层 schema 和 example。
3. 补 `entity readback` 与 `VERIFICATION_REPORT`。
4. 做 `OBJECT_SPEC + STYLE_PROFILE` 的第一个参数化柜子闭环。
5. 做 `BLOCK_LIBRARY`。
6. 做 `LAYOUT_PROPOSAL`。
7. 做 `DRAWING_MODEL`。
8. 做 `DESIGN_PROPOSAL`。
9. 用 `commercial_fitout` 的两个 workflow 验证 Core。

## 13. 以后如何判断是否跑偏

每次新增能力前问：

```text
1. 这个能力是否两个以上场景会用？
2. 如果会，是否应该进入 core？
3. 如果只属于某个场景，是否只放 agents/<scenario>？
4. 它是否依赖真实项目资料？如果是，是否应该放 projects/？
5. 它是否只是图库、风格、尺寸或材料？如果是，是否应该放 libraries/？
6. 它是否绕过了 validate、dry-run、CODEX_PREVIEW、verification？
```

如果回答不清楚，先补设计说明，不要直接写代码。
