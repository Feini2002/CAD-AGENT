# Architecture Docs

当前架构边界快照：
- `current-module-boundaries.md`：`ARCH-BOUNDARY-HARDENING-01` 的 Stable Core / Training Experiments / Case-Only 分类，以及统一请求链路、模块禁止边界、verification、capability-map、对象资产试点和 `projects/.../runs` 晋升门槛。

架构设计和重构说明放在这里。当前根目录 `CORE_RESTRUCTURE_PLAN.md` 是唯一 `PlanMD` / 开发主线；本目录只解释架构边界和设计依据，不承载独立下一步。

## 统一请求链路

```text
User Request -> semantic route -> A-to-A contract -> CAD_PLAN / asset workflow / training route -> execution -> verification -> promotion/sync
```

这条链路是架构说明、模块边界和训练 / 资产 / CAD 执行文档的共同口径。`semantic route` 负责把白话请求分流为普通绘图、系统资产复用 / 沉淀、训练 / 复训、局部修复或只读识别；`A-to-A contract` 只描述责任分发和 hard gate，不替代 CAD readback。下游只允许进入 `CAD_PLAN`、`asset workflow` 或 `training route`，然后统一收束到 execution、verification 和 promotion/sync。

## 当前核心入口

- `cad_workflow.md`：从结构化意图到预览、验证、确认的通用流程。
- `cad_plan_boundary.md`：`CAD_PLAN` 与高层设计模型的职责边界。
- `cad-agent-task-chain.md`：白话语义拆分、复杂任务拆分、分发执行、训练回流、规则同步和 A-to-A 校准的系统任务链路。
- `cad-asset-intelligence-architecture.md`：参考图库、自产图库、对象语法、检索、审计和晋升的资产化能力架构。
- `../planning/cad-commonsense-asset-dev-plan-01.md`：标准图库 raw 输入、reference 标注、knowledge 编译和自产图库晋升的执行计划。
- `shell-layout-foundation-design.md`：空壳空间理解与布局底座的设计背景、已落地映射和待硬化边界。

## 系统硬门禁索引

这些门禁是跨文档统一的入口，不随单个完成包漂移：

| 门禁 | 必须防止什么 | 主要入口 |
| --- | --- | --- |
| UTF-8 preflight | 中文、路径、资产名或 visible text 进入 CAD 前已经 mojibake | `scripts/_bootstrap.py`、`core.runtime.encoding_guard` |
| CAD_PLAN validate/dry-run | 白话或未校验结构直接落 CAD | `scripts/validate_plan.py`、`scripts/dry_run_plan.py`、`core.plan_engine` |
| CODEX_PREVIEW/no-save | 保存当前业务 DWG、覆盖原图、修改正式图层 | `core.execution`、`core.cad_io`、`core.safety` |
| A-to-A hard gate | 缺必需 Agent 输出却声称完成 | `docs/architecture/cad-agent-task-chain.md`、`scripts/run_a_to_a_orchestration_gate_check.py` |
| asset source boundary | 把 whole modelspace、current screen、training panel 误做系统资产 | `docs/architecture/system-asset-sedimentation-protocol.md`、`core.assets.semantic_rules` |
| reuse readback | 语义命中或 plan-only 被误报为已复用 | `docs/architecture/system-asset-reuse-workflow.md`、`scripts/reuse_system_asset.py` |
| training promotion gate | quick trial 或单次训练误写事实源 / 工作台 / Agent 校准 | `core.training.promotion_gate`、`docs/training/README.md` |
| workbench sync | `capability-map.html` 被误读为事实源或最新状态 | `scripts/sync_training_workbench.py`、`scripts/run_training_workbench_agent_check.py` |
