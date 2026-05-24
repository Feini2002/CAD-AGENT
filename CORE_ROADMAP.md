# Core Roadmap

本文按 `CORE_RESTRUCTURE_PLAN.md` 的阶段 0-10 追踪通用 CAD Agent Core Lab 的路线。核心原则保持不变：通用底座优先，场景 Agent 轻量化。

## 阶段 0：架构冻结

目标：

- 固定 `CORE_RESTRUCTURE_PLAN.md`。
- 明确仓库定位为通用 CAD Agent Core Lab。
- 明确 `CAD_PLAN` 是落图指令，不是设计大脑。
- 明确下一步只做仓库重装，不做业务扩张。

完成标准：

- 根目录存在 `CORE_RESTRUCTURE_PLAN.md`。
- 用户确认方案。

当前状态：done。架构草案已存在，并已完成第一轮仓库重装。

## 阶段 1：仓库重装

目标：

- 创建 `core/`、`agents/`、`projects/` 等基础结构。
- 将现有执行层文件逐步迁移到对应目录。
- 更新 README、AGENTS、STATUS、ROADMAP。
- 不大改逻辑。

完成标准：

- 旧验证命令仍能跑。
- 当前测试仍能通过。
- 文件职责更清晰。

当前状态：prototype。`core/`、`agents/`、`projects/` 等结构已创建；现有脚本、schema、drivers 和 tests 已迁移或建立兼容包装器。

## 阶段 2：Core 状态看板

目标：

- 新增 `CORE_STATUS.md`。
- 用能力矩阵追踪通用底座进度。
- 区分 prototype、scaffold、not_started、blocked。

完成标准：

- 能回答“通用底座开发到哪了？”。
- 能看出哪些能力已有原型，哪些只是设计占位。

当前状态：done。已建立第一版能力矩阵，并记录迁移后的 Core 入口。

## 阶段 3：Core 数据模型

目标：

- 建立通用 schema：`DESIGN_BRIEF`、`DRAWING_MODEL`、`PROJECT_MODEL`、`OBJECT_SPEC`、`STYLE_PROFILE`、`BLOCK_LIBRARY`、`LAYOUT_PROPOSAL`、`DESIGN_PROPOSAL`、`VERIFICATION_REPORT`。
- 每个 schema 配最小 example。

完成标准：

- 每个 example 可以校验。
- 高层模型和最终 `CAD_PLAN` 的职责边界清楚。

当前状态：not_started。

## 阶段 4：对象与风格底座

目标：

- 从白话生成参数化对象。
- 第一批对象：柜子、货架、桌子。
- 第一批风格：现代、欧式、极简。

完成标准：

- 生成 `OBJECT_SPEC`。
- 生成方案说明。
- 生成 CAD_PLAN。
- 绘制到 `CODEX_PREVIEW`。
- 验证主要尺寸和图层。

当前状态：not_started。现有测试柜是执行层样例，不等同于对象引擎。

## 阶段 5：图库块底座

目标：

- 建立公司图库块元数据格式。
- 支持块分类、尺寸、插入点、旋转规则、避让范围、适用场景。

完成标准：

- 能登记一批块。
- 能按用途选择块。
- 能插入块到预览层。

当前状态：not_started。

## 阶段 6：布局底座

目标：

- 在给定边界、入口和对象集合时生成基础布局。
- 先做通用布局，不绑定工装。

完成标准：

- 可生成候选布局。
- 可做碰撞检查。
- 可检查基本通道。
- 可输出 `LAYOUT_PROPOSAL`。

当前状态：not_started。

## 阶段 7：图纸理解底座

目标：

- 从已有 DWG/PDF 提取实体和文字。
- 生成 `DRAWING_MODEL`。

完成标准：

- 能列出图层、实体数量、文字、尺寸、块。
- 能初步识别空间名和边界候选。
- 能把不确定点列出来。

当前状态：not_started。

## 阶段 8：方案推理底座

目标：

- 从 `DESIGN_BRIEF + PROJECT_MODEL` 生成 `DESIGN_PROPOSAL`。
- 不直接画图，先让用户确认方案。

完成标准：

- 方案包含依据、推断、不确定点。
- 用户确认后可转 CAD_PLAN。

当前状态：not_started。

## 阶段 9：轻量场景 Agent

目标：

- 建立第一个 `commercial_fitout` Agent。
- 只写场景差异，不复制 Core。

完成标准：

- 支持 `existing_plan_to_elevation` 工作流草案。
- 支持 `blank_store_to_layout` 工作流草案。
- 共用 Core 数据模型和执行层。

当前状态：agent scaffold done, formal capability not_started。场景 Agent 目录与轻量规则已建立，但还没有实现真实场景能力。

## 阶段 10：真实项目闭环

目标：

- 用真实或近真实项目验证 Core。

完成标准：

```text
输入 -> 分析 -> 项目模型 -> 方案 -> CAD_PLAN -> 预览 -> 验证 -> 修改记录
```

当前状态：not_started。

## 路线约束

- 先让 Core 能复用，再让场景 Agent 变聪明。
- 不把工装、家装、办公、餐饮、展陈的通用能力重复写进各自 Agent。
- 第一轮已迁移现有 `scripts/`、`schemas/`、`drivers/`、`tests/` 的核心实现，同时保留旧入口兼容。
- 任何落图能力都必须继续遵守 `CODEX_PREVIEW`、validate、dry-run、自检和验证门。
