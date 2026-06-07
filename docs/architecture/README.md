# Architecture Docs

架构设计和重构说明放在这里。当前根目录 `CORE_RESTRUCTURE_PLAN.md` 是唯一 `PlanMD` / 开发主线；本目录只解释架构边界和设计依据，不承载独立下一步。

## 架构归并画布

当前仓库级主设计入口是 [`system-architecture-convergence.md`](system-architecture-convergence.md)。它把探索式开发中分片长出的旧表 A/B/C、Core proof、训练地图、系统资产、多 Agent、GPT-5.5 模型桥、Worker 编排、截图、工作台和证据治理，统一归入七层任务生命周期：

```text
系统入口 -> 任务对象 -> 决策编排 -> 能力与证据
  -> 执行工具 -> 审计修复 -> 沉淀成长
```

后续新增架构包必须先说明自己属于哪一层、输入输出是什么、不能越过哪一层。旧表 C / coverage JSON 只能作为 `Core Proof Coverage`，不得再作为端到端真实 CAD 能力主叙事。

## 当前架构边界快照

- `current-module-boundaries.md`：`ARCH-BOUNDARY-HARDENING-01` 的 Stable Core / Training Experiments / Case-Only 分类，以及统一请求链路、模块禁止边界、verification、capability-map、对象资产试点和 `projects/.../runs` 晋升门槛。
- 旧入口收编、权限安全与训练回归加固已从临时方案收口为机器包：事实源在 `config/entrypoint_custody_manifest.json`、`core/entrypoint_custody/**`、`core/training/report_claim_audit.py`、`core/model_review/trace_claim_audit.py` 和对应 runner / tests；本目录不再保留第二份入口方案 MD。

## 统一请求链路

```text
User Request
  -> request context / run package
  -> semantic route
  -> Orchestrator Host / A-to-A contract
  -> required agents + hard gates
  -> CAD_PLAN / asset workflow / training route
  -> execution
  -> verification / closeout
  -> Reviewer Host / delivery claims
  -> promotion/sync
```

这条链路是架构说明、模块边界和训练 / 资产 / CAD 执行文档的共同口径。`semantic route` 负责把白话请求分流为普通绘图、系统资产复用 / 沉淀、训练 / 复训、局部修复、设计候选或只读识别；`Orchestrator Host` / `A-to-A contract` 只描述责任分发、模型 / 规则 Agent 输出和 hard gate，不替代 CAD readback。下游只允许进入 `CAD_PLAN`、`asset workflow` 或 `training route` 等结构化路径，然后统一收束到 execution、verification / closeout 和 promotion/sync。

## 当前核心入口

- `cad_workflow.md`：从结构化意图到预览、验证、确认的通用流程。
- `cad_plan_boundary.md`：`CAD_PLAN` 与高层设计模型的职责边界。
- `cad-agent-task-chain.md`：白话语义拆分、复杂任务拆分、分发执行、训练回流、规则同步、A-to-A 校准和 Tool Contract ReAct / Stage 4 受控 CAD 工具链路。
- `model-agent-local-hardening-plan.md`：模型型 Agent 在网络 / OpenAI provider 外部问题暂不处理时，先本地加固 export manifest、repo-external cwd、可审计决策链、handoff packet、ToolIntent fixture、错误 taxonomy 和 closeout 状态机的执行计划。
- Worker 编排 + 本地活体模型桥：路线已收口到 `CORE_RESTRUCTURE_PLAN.md` §3 / §3.1；本地 stand-in 和诊断入口在 `core/orchestrator/local_live_model_bridge*.py` 与 `scripts/diagnose_local_live_model_bridge.py`。
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
| model export manifest | 模型桥在网络调用前误带未授权本地文件、整仓上下文、全屏截图或项目规则文档 | `docs/architecture/model-agent-local-hardening-plan.md`、计划中的 `core/model_review/export_manifest.py` |
| model trace chain | 声称模型型 Agent 真实协作但没有 trace、schema、provider status 或上游输出引用 | `core/model_review/`、`core/orchestrator/orchestrator_host_runtime.py`、`core/orchestrator/reviewer_host_runtime.py` |
| local live model bridge | 声称 Worker 编排或 Agent 活体调用 GPT-5.5，但缺 Worker run state、`modelInvoked=true`、`modelUnavailable=false`、schema validation、sanitized `codex.cmd exec` trace、完整 trace 包或下游读取证据 | `CORE_RESTRUCTURE_PLAN.md`、`core/orchestrator/local_live_model_bridge*.py`、`core/model_review/`、`output/model_reviews/traces/**`、`output/runs/**/model_traces/**` |
| tool contract gate | 模型 toolIntent 越权、无 target scope、无 trace、把验证 pass 当 CAD 证据 | `core/orchestrator/tool_contract.py`、`core/schemas/tool_intent.schema.json`、`core/schemas/tool_trace.schema.json` |
| asset source boundary | 把 whole modelspace、current screen、training panel 误做系统资产 | `docs/architecture/system-asset-sedimentation-protocol.md`、`core.assets.semantic_rules` |
| reuse readback | 语义命中或 plan-only 被误报为已复用 | `docs/architecture/system-asset-reuse-workflow.md`、`scripts/reuse_system_asset.py` |
| training promotion gate | quick trial 或单次训练误写事实源 / 工作台 / Agent 校准 | `core.training.promotion_gate`、`docs/training/README.md` |
| workbench sync | `capability-map.html` 被误读为事实源或最新状态 | `scripts/sync_training_workbench.py`、`scripts/run_training_workbench_agent_check.py` |
| entrypoint custody / replay custody | 旧脚本、历史专项、诊断入口、派生显示或训练 replay 默认路径绕过中枢，或被活跃文档误当当前 next / 学习后重测 | `config/entrypoint_custody_manifest.json`、`core.entrypoint_custody.guard`、`scripts/run_entrypoint_custody_audit.py`、`scripts/run_training_report_claim_audit.py`、`scripts/run_model_trace_claim_audit.py` |
