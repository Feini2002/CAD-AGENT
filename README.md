# CAD Agent Core Lab

CAD Agent Core Lab 是一个可迁移的 CAD Agent 开发包，用来训练“极端白话需求 -> 主 Agent 理解和分发 -> 子 Agent 协同判断 -> 结构化绘图意图 -> CAD 预览落图 -> 机器审计 -> 用户验收”的完整闭环。它不把一句自然语言直接丢给 AutoCAD 硬画，而是把 CAD 生成拆成可审计、可回放、可修复、可跨机器迁移的工程链路。

当前最新架构是 **CAD Designer Agent 成长路径 + Visual-First + CAD 常识底座 + 资产智能管线 + 主 Agent / 多 Agent 编排**：

- **CAD Designer Agent**：把系统当作电子设计师训练，从基础图元、选择、移动、旋转、偏移、修剪、图层、闭合和回读开始，逐步进入对象符号、房间平面、专业表达和施工图。
- **Visual-First**：先看真实参考、截图裁剪或 CAD 参考块，再生成 `style_target`、`visual_parts` 和绘图约束。
- **CAD 常识底座**：把“沙发要有座面和靠背”“参考不等于复制”等基础知识沉淀为可查、可测、可声明边界的规则候选。
- **资产智能管线**：把 `standard_cad_library_raw/`、`reference_library`、`system_library`、`retrieval_pack`、promotion gate 串起来，区分“参考输入”和“系统已验证自产能力”。
- **主 Agent / 多 Agent 编排**：`pipeline_orchestrator` 负责理解白话、生成 `a_to_a_task_contract`、动态加派已登记 Agent、收 hard gate 输出并阻断不可靠完成口吻；Context / Asset / Design / Intent / Execute / Audit / Repair / Delivery / Learning Promotion 等子 Agent 分工协作。
- **GPT-5.5 模型桥**：通过本地 Codex CLI / 未来 SDK 做只读推理、设计判断、复审和交付建议；模型可以想、评、分发和建议修复，但不能直接写 CAD、保存 DWG、删除实体或替代 readback。
- **证据优先**：截图、dry-run、Markdown、图库命中都不能单独证明真实 CAD 能力；对外声称完成前必须有结构化意图、真实输出、created handles 回读、审计和必要截图。

一句话：这个仓库训练的不是“会画一张图的脚本”，而是一个能把用户白话拆成责任、证据和执行路径，再调用流程 Agent、场景规则和资产库，并在真实 CAD 约束下逐轮变准的电子设计师。

## 最新端到端架构

这条链路有两个硬约束：

1. `CAD_PLAN` 或结构化绘图意图必须先于真实 CAD 执行。
2. 资产检索、常识命中、参考图命中只算上游证据，不能跳过 validate、dry-run、`CODEX_PREVIEW`、readback 和 audit。

同一口径收束为：

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
  -> promotion / sync
```

其中 `semantic route` 先识别普通绘图、系统资产复用 / 沉淀、训练 / 复训、局部修复、设计候选或只读治理等语义；复杂或高风险任务必须生成 `a_to_a_task_contract`，由必需 Agent 输出和 hard gate 决定是否能继续。下游只能进入 `CAD_PLAN`、`asset workflow` 或 `training route` 等结构化路径；无论哪条路，执行后都要回到 verification / closeout，并按证据边界决定是否 delivery、promotion / sync。

## 模型型 Agent 升级方向

当前多 Agent 系统正在从“角色契约 + 规则门禁”升级为 **可追踪的模型型 Agent 运行时**。升级目标不是让模型绕过 Core 自由写 CAD，而是让少数主脑和复审 Agent 通过本地 Codex CLI 做可审计推理、分发、视觉复审和交付判断。

目标运行形态：

```text
User Request
  -> output/runs/<run_id>/user_request.json + state.json
  -> Orchestrator Host
  -> dispatch_plan.json + task_contract.json + required_agents.json + risk_assessment.json
  -> model / rule agents with trace and strict JSON
  -> CAD validate / dry-run / execute / readback
  -> closeout_decision.json
  -> Reviewer Host
  -> agent_outputs/pipeline_delivery.json + final_report.md
  -> learning / workbench derived snapshot
```

核心边界：

- **Trace / Run Package 优先**：先记录每次模型型 Agent 的 `agentId`、`taskType`、prompt、schema、sanitized command、stdout/stderr、last message、normalized output、gate decision、`trace_review.json`、`trace_summary.md` 和 `output/runs/<run_id>/state.json`，再逐个打磨 Prompt。
- **Worker 编排 + 本地活体模型桥优先**：路线已收口到 `CORE_RESTRUCTURE_PLAN.md` 和 `core/orchestrator/local_live_model_bridge*.py`；先用本地 stand-in 固定 run state、task envelope、bridge lease / heartbeat、trace diagnostics 和 feature gates，再迁移到 Cloudflare Worker / Durable Object / Queue，最后扩真实多 Agent 互读和 CAD-MCP preview-only。
- **活体协作优先验证**：下一步要先跑通 4-6 个 Agent 的 no-CAD / no-save 连续模型调用链，让下游 Agent 读取上游 `agent_outputs/*.json` 后再判断，而不是各自独立输出意见。
- **事实源不用 JS**：长期事实源使用 JSON、Markdown 和 reports；`capability-map-data.js` / `capability-map.html` 只作为工作台展示派生文件。
- **两个主脑优先**：先建设 Orchestrator Host 和 Reviewer Host；其他 Agent 作为被调用的模型 / 规则角色，不临场激活未登记 Agent。
- **模型只读**：模型可以判断、分发、复审和建议修复，但不能直接写 CAD、删除实体、保存 DWG、修改正式图层或替代 readback / sourceSpec / reuse replay。
- **可见 CAD 交付必须 closeout**：focused / formal CAD 可见交付应经过视觉验收、邻区保护、created handles readback 和保存边界检查；截图非空不能等于视觉通过。

模型型 Agent 升级记录已并入 `CORE_RESTRUCTURE_PLAN.md` 和 `agents/pipeline/README.md`，临时执行卡已删除。`model-review-trace-observability` 已落文件化 trace 与自动复盘摘要；`run-package-state-machine` 已落可恢复 `output/runs/<run_id>/state.json`；`visual-acceptance-closeout-gate` 已落确定性 `closeout_decision.json`；`delete-scope-and-neighbor-protection-gate` 已落 `delete_scope_gate.json` / `neighbor_protection.json` 生成器；`model-agent-prompt-library` 已落 9 个真实 Prompt Pack；`orchestrator-host-runtime` 已能从 run package 写分发计划、任务合同、required agents 和风险评估；`reviewer-host-closeout-runtime` 已能生成 `agent_outputs/pipeline_delivery.json` 与 `final_report.md`；`workbench-trace-viewer` 已接入训练工作台的“模型 Trace”派生视图。真实 CAD 校验方法保留在主计划中，默认只写 `CODEX_PREVIEW`、不保存当前业务 DWG、不把截图或模型 pass 当几何证明。

## 架构分层

- `core/`：通用能力层，负责 CAD IO、执行、安全、schema、审计、训练 gate 和能力登记。
- `agents/cad_designer/`：总设计师 Agent 契约，定义成长阶段、第一阶段毕业目标、基础课程和证据边界。
- `agents/pipeline/`：全局多 Agent 流水线，定义理解、视觉约束、意图、执行、审计、修复、交付、学习晋升等角色。
- `agents/<scenario>/`：轻量场景 Agent，保存住宅、展陈、医疗等场景偏好和词汇，不复制 Core 能力。
- `standard_cad_library_raw/`：用户下载的标准 CAD 图库原始文件，允许随 git 迁移，但只算 raw reference input。
- `libraries/`：共享样式、图层、尺寸、材料、块库和可复用资源；资产智能链路区分 `reference_library` 与 `system_library`。
- `projects/`：真实或脱敏训练案例，每个案例保存 brief、feedback、expected、runs 和必要脚本。
- `scripts/`：验证、gate、coverage、CAD smoke、截图和迁移检查入口。
- `tests/`：单元测试、契约测试、训练 gate 测试和回归测试。
- `docs/`：架构、训练、治理、状态、交接和历史记录。

当前架构边界快照见 `docs/architecture/current-module-boundaries.md`。后续重构先按 `Stable Core`、`Training Experiments`、`Case-Only` 三类判断归属，再决定是否迁移代码；`openspec/changes/architecture-boundary-hardening-01/` 只记录本轮边界加固契约，不替代 `CORE_RESTRUCTURE_PLAN.md`。

## 资产智能管线

资产智能不是“把图库塞进仓库就算会画”，而是把外部参考、系统自产资产和可执行证据分开管理。`standard_cad_library_raw/` 和 `libraries/reference_library/` 只说明参考来源；`libraries/system_library/` 才承载系统自产资产，但仍必须有 schema、lineage、native 证据、复用 probe / replay 和 evidence boundary。`retrieval_pack` 只能作为 `CAD_PLAN` 上游上下文；只有经过来源门、结构门、执行门、审计门和泛化门，资产才可能从案例候选晋升为系统级能力。

## Visual-First 训练

Visual-First 的核心要求是：**先看真实参考，再画 CAD**。对 reference-match 任务，`style_target` 不能是凭空生成的示意图，必须来自 AutoCAD 截图裁剪、用户提供参考图或真实 CAD 参考块。典型 round 产物保存在 `projects/<case_id>/runs/`：`visual_parts`、`intent`、`execution_summary`、`vector_readback`、`geometry_audit`、`preview`、`agent_review` 和 `style_compare`。

## 历史训练样例

`projects/residential_sofa_2seat_20260528/` 是第一条完整训练闭环样例，不是当前唯一主线。当前主线以 `CAD Designer Agent` 成长路径、V2 训练地图和 `docs/planning/任务清单.md` §0 为准；沙发案例只作为历史证据和训练教训来源。

## 安全边界

- 默认只写 `CODEX_PREVIEW`。
- 默认不保存当前 DWG。
- 不覆盖原始 DWG。
- 不修改正式图层，不删除用户原有实体。
- 截图只能作为视觉辅助，不能替代 geometry/readback 证据。
- 对外声称 CAD 完成前，必须有结构化意图、validate、dry-run、真实输出、created handles 回读、审计和必要截图。

## 换电脑继续

仓库按可迁移开发包设计。换机前先确认 `git status --short`，把有效源码、文档、Agent 契约、OpenSpec、系统资产索引和必要 fixture 纳入 checkpoint；第三方 DWG 只有来源和再分发边界清楚时才随仓库迁移。新电脑 clone 后恢复 AutoCAD / CAD-MCP / Python 环境，读取 `CORE_CONTEXT_BRIEF.md` 和 `docs/onboarding/first-handoff.md`，再跑 `scripts/self_check.py`、`scripts/render_preview.py --check` 和必要 coverage / audit。

## 关键入口

- `AGENTS.md`：Agent 行为规则和 CAD 安全边界。
- `CORE_CONTEXT_BRIEF.md`：短上下文入口，新会话优先读。
- `CORE_RESTRUCTURE_PLAN.md`：唯一 PlanMD / 主计划。
- `CORE_STATUS.md`：能力状态和表 C 口径。
- `docs/training/README.md`：训练期主链路。
- `docs/training/cad-designer-growth-path.md`：总设计师 Agent 成长路径和第一批基础 CAD 课程。
- `docs/training/global-agent-pipeline.md`：多 Agent 流水线说明。
- `docs/architecture/cad-asset-intelligence-architecture.md`：参考图库、自产图库、检索、审计和晋升架构。
- `docs/planning/cad-commonsense-asset-dev-plan-01.md`：标准图库 raw 输入到自产图库晋升的计划书。
- `capability-map.html`：具体图块和基础绘图能力的训练工作台，作为训练计划视图，不替代内部证据文档；日常打开优先用 `start_training_workbench.bat`，或先跑 `scripts/sync_training_workbench.py` 刷新数据。
- `scripts/sync_training_workbench.py`、`scripts/run_training_workbench_agent_check.py`：刷新训练工作台数据快照并校验是否跑偏。
- `scripts/run_asset_raw_intake.py`、`scripts/run_asset_retrieval_pack.py`、`scripts/run_asset_promotion_gate.py`：标准图库自动 intake、资产检索包和晋升 gate 的基础入口。
- `docs/planning/任务清单.md`：当前训练 backlog 和 next。
- `docs/status/current.md`：当前状态摘要。
- `docs/status/issues.md`：失败教训和活跃风险。
- `docs/handoffs/current.md`：最近包交接。

旧根目录 Stub 入口已合并到本节和 `docs/README.md`，例如“当前状态入口 / 变更记录入口 / CAD 卡壳排障入口”等不再单独保留；需要对应内容时直接打开上面的事实源。
