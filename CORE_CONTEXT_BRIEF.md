# Core Context Brief
最后更新：2026-06-07（ARCH-CONVERGENCE-01：架构归并画布工程仍是当前主线；正式对象训练暂缓。历史旧表 A/B/C、表 C 90.99% 和旧称“真实 CAD 实力”降级为 `Core Proof Coverage` / 底座证据覆盖，不再代表 `Agent Task Maturity` 或 `Project Delivery Readiness`；Worker 编排 + 本地活体模型桥路线已从独立 MD 收口到 `CORE_RESTRUCTURE_PLAN.md`、`workers/orchestrator/**` 与 `core/orchestrator/local_live_model_bridge*.py`，当前 Worker 已远程部署为 `cadagent` 并通过最新 `worker_orchestration_ready` smoke；adaptive capability growth training 已从临时 MD 落地为 no-CAD inventory、profile、growth replay planner、expression regression gate、runner 参数和 closeout claim gate，临时 MD删除，不声明 Worker 重新部署、正式训练集成或表 C 提升；新增认知提升硬口径：声称主 Agent 变聪明必须证明真实任务判断改变，否则只是机制建设；资产智能、sofa 对象族 replay、模型型 Agent Host/runtime、A-to-A、截图编排、训练防膨胀和 CAD Designer Agent 成长路径均保留并归入七层任务生命周期）
本文是后续 Codex / Cursor / 其它 agent 工具接手本仓库时的稳定短上下文入口。若 `AGENTS.md` 已被工具自动加载，会话恢复从本文开始；人工迁移或新工具接手时先看 `AGENTS.md`，再看本文。普通任务只按“按需展开”表追加 1-2 个文件；不要默认全文扫 `README.md`、`docs/status/current.md`、`docs/handoffs/current.md` 或长期规则。
## 当前一句话
本仓库是可迁移的 CAD Agent Core Lab；**当前阶段：ARCH-CONVERGENCE-01 架构归并画布工程**。先读 `docs/architecture/system-architecture-convergence.md`、`CORE_RESTRUCTURE_PLAN.md` §0.2 和 `openspec/changes/unify-system-architecture-canvas/`。本阶段目标不是继续加模块或立刻训练，而是把探索式开发形成的旧表 A/B/C、V-PROOF、RCAD、训练地图、资产库、多 Agent、Worker / bridge、GPT-5.5 模型桥、截图和工作台，全部归入七层任务生命周期。旧表 C 历史 90.99% 只表示 `Core Proof Coverage`；真实任务能力另看 `Agent Task Maturity`，当前仍是早期；真实项目交付另看 `Project Delivery Readiness`。CAD Designer Agent 成长路径、V2 训练地图、基础 CAD 操作 31/31、资产智能和 Visual-First / visual_parts 链路继续保留，但正式对象训练默认暂停，待架构归并和脚本 / 工作台口径同步后恢复。
正式训练、focused 复训、正式收尾型工作台同步、系统资产沉淀或仓库级治理产生新 output / debug / test artifacts 前后，默认还要做数据防膨胀与证据闭合判断：区分 `protected`、`candidate`、`blocked`、`derived`，先 dry-run / audit，再决定是否归档；`capability-map-data.js`、HTML、sync report、retention report 和 data-bloat audit 只是派生或诊断产物，不得反向当作训练事实源。
## 默认输出口径
普通最终回复默认**不附进度表、表单或表 A/B/C**；只说明本轮完成内容、证据和风险。架构归并期尤其不要主动用旧表 C 作为主叙事。只有用户明确点名开发状态查询、进度、完整状态、交接、审计、表 A/B/C、表 C、Core Proof Coverage 或刷新表 C 时，才展开历史表格；展开时必须说明表 C 不是端到端真实能力。

## 当前精简进度

表 C 只认机器报告：`output/validation_runs/capability-lab/cad_capability_coverage.json`。

| 口径 | 当前值 | 说明 |
| --- | --- | --- |
| **Core Proof Coverage** | 历史约 **90.99%**（旧表 C 主指标） | 只表示底座证据覆盖；**不代表** Agent 任务成熟度或项目交付准备度 |
| Agent Task Maturity | 早期，可按 **5%-10%** 的训练感受谨慎看待 | 需靠对象课、案例 feedback、readback、修复闭环和沉淀提升 |
| 工程节奏 | 总约 **97%**（**Core 100%**，Agent 93%） | 表 A；Core 见 `core_platform_completion_gate.md` |
| 训练台账 | 成长路径 + 案例 backlog：`docs/planning/任务清单.md` §0 | 主训 **CAD Designer Agent**；家装为当前主场景插件 |

## 当前 next

**架构归并期（ARCH-CONVERGENCE-01）**：先按 `docs/architecture/system-architecture-convergence.md` 与 `openspec/changes/unify-system-architecture-canvas/tasks.md` 归并架构和脚本口径；正式对象训练、整批训练和表 C 推进暂缓。用户明确覆盖暂停时，仍可按 quick / focused / formal 原边界执行。

| 用户口令 | 默认动作 |
| --- | --- |
| **架构归并** / **重画架构** / **先整理框架** | 执行 `ARCH-CONVERGENCE-01`；同步规则、状态、PlanMD、OpenSpec、脚本口径和工作台派生显示 |
| **CAD 基础课** / **总设计师训练** | 当前不默认新开正式训练；先提醒架构归并正在进行。用户明确覆盖时，再从基础家具 / 对象课程 / 案例 feedback 中选 1 个训练目标 |
| **跑前 10 项队列** / **监督式基础队列** | 运行 `$py scripts\run_training_queue.py --preset cad-foundation-first-10`；每次暂停 1 项并提示用户验收 checklist / pass / fail 下一步；`--decision pass` 后脚本自动做训练工作台 post-sync；每个自动化子动作默认 30 秒 watchdog，超时先自救，连续超时熔断暂停 |
| **开一轮训练** / **家装案例** | `brief.md` → 计划 → `CODEX_PREVIEW` → `feedback.md` |
| **试一下** / **快画** / **小动作** / **先别沉淀** | 走 `quick_trial`：≤2 分钟，只写 `CODEX_PREVIEW`，做关键 readback，跳过完整训练同步；回复说明“快试未沉淀” |
| **记反馈** | 更新案例 `feedback.md` + 任务清单 backlog |
| **优化常识底座** | 读 `docs/training/cad-common-sense-upgrade.md`；只吸收方法论或资料为 summary / candidate / executable_check / evidence_boundary |
| **优化资产图库** | 读 `docs/architecture/cad-asset-intelligence-architecture.md` + `docs/planning/cad-commonsense-asset-dev-plan-01.md`；raw 标准图库放 `standard_cad_library_raw/`，默认跑 `scripts/run_asset_raw_intake.py --write`；自产图库放 `libraries/system_library/` |
| `刷新表 C` | 只跑 coverage（Lab） |
| `打开训练工作台` / `刷新训练工作台` | 优先运行 `start_training_workbench.bat` 或 `$py scripts\sync_training_workbench.py` |
| `画不准` | `docs/runbooks/blocker-playbook.md` |
| Lab 三轨 / Core 施工 | 已收口 → `archive/`、`post-backlog.md` |

## 最近有效事实

- **ADAPTIVE-CAPABILITY-GROWTH-TRAINING-01**：adaptive capability growth 临时调研稿已收尾删除；OpenSpec change `adaptive-capability-growth-training` 的任务清单已完成。新增 `core.training.capability_growth_profile`、`adaptive_replay_planner`、`expression_regression_gate` 和 `adaptive_growth_closeout`，并接入 `scripts/run_cad_foundation_remaining_training.py --replay-mode smoke_replay|growth_replay|standard_replay --capability-profile <repo-local-json>`。能力成长画像只接受仓库内 active / protected 事实源；`output/debug`、派生工作台、诊断报告、外部路径和缺失文件不能作为 hard baseline。`growth_replay` 只能在 focused / formal 边界内提高表达要求，不能替代真实 CAD readback、用户验收、Worker 部署、系统资产 verified 或表 C 提升。
- **CAD-TRAINING-PROMOTION-GATE-01**：训练 / 复训 / 纠错收尾已新增机器 `promotionGate`。`quick_trial` 保持 `promotionLevel=observation`，不写训练事实源、工作台或 Agent 校准；正式训练通过后，ledger / workbench 必须声明 `updateTrainingSource`、`updateWorkbench`、`updateAgentCalibration`、`updateBaseRules`、`updateTaskRules`、`updateChecker`、`retestOriginalTask` 七项决策；未知 `capabilityId` 不再 fallback 到 `cad_designer`；规则 / 检查器 delta 只进入 `needs_reviewed_package`；`scripts/sync_training_workbench.py` 已刷新工作台，Agent check 39/39 pass。
- **ASSET-LOCAL-RAG-MVP-01**：资产智能后续项的第一步已完成。新增 `core.assets.local_rag`，输出 `local_asset_small_rag_pack`，只做系统资产 JSON、语义规则、Agent training memory 和项目失败样本的本地 lexical 检索；显式排除 reference asset、外网、raw download 和 embedding index。它只提供设计 / 审计 upstream context，不证明 CAD 几何、created handles、用户视觉验收、模型质量或资产 verified 晋升；下一步按主计划进入 sofa / dimension style 对象族试点。
- **OBJECT-FAMILY-SOFA-TRIAL-MVP-01**：sofa 对象族 no-CAD 试点已完成。新增 `core.assets.object_family_trial`，跑通本地 RAG -> 3 个设计候选 -> `draw_symbol_glyph` CAD_PLAN 草案 -> `validate_plan` -> dry-run -> 执行计划 / readback 证据要求；真实仓库调用返回 `cad_plan_draft_ready 3 valid not_executed_no_cad`。该包不写 CAD、不保存 DWG、不提升表 C；下一步是自动晋升候选，仍不得用 no-CAD draft 冒充真实 replay。
- **ASSET-PROMOTION-CANDIDATES-MVP-01**：自动晋升候选已完成。新增 `core.assets.promotion_candidates`，从 ready 的 sofa object-family trial 生成 task rule / checker / asset candidate / training item 四类候选；报告为 `review_required`，`mutatedTargets=[]`，`updateTaskRules` / `updateChecker` 为 `needs_reviewed_package`，`updateTrainingSource=not_required`。真实仓库调用返回 `review_required 4 [] needs_reviewed_package`；候选仍需 reviewed package，不能因 sofa replay 已通过就自动写规则、checker、资产或训练事实源。
- **OBJECT-FAMILY-SOFA-REPLAY-RCAD-01**：sofa 对象族真实 CAD replay 已完成。新增 `core.assets.object_family_cad_replay` 与 `scripts/run_object_family_cad_replay.py`，在 `projects/测试文件.dwg` 当前活动文档只写 `CODEX_PREVIEW`，不保存当前 DWG；证据目录 `output/validation_runs/object-family-sofa-replay-20260605-rcad/`：17/17 handles 回读，bbox `[62000,36100]` 到 `[64200,36900]`、图层和 type count 均匹配，截图 `output/previews/object-family-sofa-replay-20260605-rcad.png` 仅为视觉辅助，visual review pass，closeout 包 `output/runs/object-family-sofa-replay-20260605-rcad-closeout/` 为 `ready_for_delivery`。边界：这证明 sofa 对象族 draw_symbol_glyph replay，不证明系统资产复用 verified、跨 DWG sourceSpec/reuseReplay 或用户人工验收。
- **CAD-AGENT-TASK-CHAIN-01**：系统任务链路已沉淀到 `docs/architecture/cad-agent-task-chain.md`。后续不能只保留执行闭环或训练闭环的一半：白话先经输入分流、语义拆分、单一子任务和责任分发，再执行 / 审计 / 交付；稳定失败或新能力要回流到训练 / 复训、原任务回测、底座规则、单一任务规则、检查器、Prompt / memory、A-to-A 校准和事实源同步。
- **WORKER-BRIDGE-CAD-PREVIEW-SMOKE-01**：用户打开 CAD 后已执行 quick smoke。Worker `cadagent` 最新 version `21fc6755-27d0-4e97-b13a-ef1e660c8401`，远程 smoke pass，`runId=run_20260606151438_worker_orchestration_ready_f6260886`；本机受控 CAD preview run package `output/runs/model-agent-live-collab-proof-20260606-151512/`，只写 `CODEX_PREVIEW`，`createdHandleCount=7`、`readbackEntityCount=7`、`cadGeometryVerified=true`、`savedCurrentDwg=false`，截图 `output/previews/worker-bridge-cad-preview-20260606-151512.png`。边界：quick smoke 不是正式训练，不是真实 `gpt-5.5` provider proof，不提升表 C；视觉复核未作为正式 closeout 放行。
- **WORKER-RUNTIME-TRACE-WORKBENCH-MVP-01**：训练工作台新增只读“链路追踪”小面板。`scripts/build_runtime_trace_snapshot.py` 生成 `output/runtime_traces/latest.json`，`start_training_workbench.bat` 会在打开页面前尝试刷新；`capability-map.html` 展示白话、Worker、Agent 链、validate / dry-run、CAD-MCP preview/readback、截图和 closeout 的状态 / 耗时 / 证据 / blocker。该面板只读，不主动执行 CAD、不调用真实模型、不提升表 C。
- **LOCAL-LIVE-MODEL-BRIDGE-HARDENING-MD-CLOSEOUT-01**：原独立本地活体模型桥架构 MD 已收口删除，剩余路线迁入 `CORE_RESTRUCTURE_PLAN.md` §3.1。当前本地 runtime 已加固：未知 `target_stage` 不再静默降级，同秒 run id 不碰撞，live 阶段必须登记 bridge 能力，`submit_result` 校验 lease identity，diagnostics 必须追到完整 model trace 包，fake CAD preflight 明确 `proofStatus=not_verified`。后续只保留 bridge-owned Codex config、真实 `single_agent_live`/`multi_agent_live` 复验和真实 CAD-MCP preview 作为剩余工作；这不替代 CAD readback、用户验收或表 C。
- **MODEL-AGENT-RUNTIME-TOOL-CONTRACT-REACT-01**：模型型 Agent 升级方向已收束到 `CORE_RESTRUCTURE_PLAN.md` §0.1、`agents/pipeline/README.md` 和治理规则；原专项 MD 已在 P10 完成后删除。已落地文件化 trace、可恢复 `output/runs/<run_id>/state.json`、`closeout_decision.json`、`delete_scope_gate.json` / `neighbor_protection.json`、9 个真实 Prompt Pack、`core.orchestrator.orchestrator_host_runtime`、`core.orchestrator.reviewer_host_runtime`、`core.orchestrator.workbench_trace_viewer` 和 `core.orchestrator.tool_contract`。P7 已定义 `tool_intent` / `tool_trace` schema，P8 已执行 Stage 1 只读工具与 Stage 2 `candidate_outputs/` 安全生成，P9 已执行 Stage 3 `validate_plan` / `dry_run_plan` / `preview_only_audit` / `closeout_gate` 确定性验证并把 `reportPath` / `resultStatus` 回写下游 evidence bundle，P10 已执行 Stage 4 `preview_cad_execute` / `execute_cad_plan_preview` 受控 CAD 工具：必须先有同一 CAD_PLAN 的 validate + dry-run pass 报告，只写 `CODEX_PREVIEW`，输出 execution / readback / preview-tool 报告，`savedCurrentDwg=false`；fake-driver 预检保留 `cadGeometryVerified=false`，真实 AutoCAD readback 不可用只能 blocked / not_verified。模型型 Agent 只能请求工具，不能替代 CAD readback、删除范围门禁、sourceSpec、reuse replay、保存边界、表 C 或用户验收。
- **A-TO-A-TASK-CONTRACT-GATE-01**：主编排新增 `a_to_a_task_contract`。系统资产沉淀固定要求 `pipeline_asset_governor`、`pipeline_asset_librarian`、`pipeline_asset_dwg_curator`、`pipeline_asset_reuse_auditor`；系统资产 DWG 仓库 / 货架 / 置物架 / 动线 / 可扩展布局任务还必须要求 `pipeline_visual_layout_reviewer` / `visual_layout_review` 和 `pipeline_visual_acceptance_reviewer` / `visual_acceptance_review`。视觉布局 reviewer 必须显式输出 `layoutReadabilityAcceptable`、`aisleClearanceAcceptable`、`contentDensityAcceptable`、`sourceProofRolesSeparated`、`layerSemanticsAcceptable`、`nonScreenshotEvidenceChecked`；通用视觉验收 reviewer 必须显式输出 `aestheticAcceptable`、`textReadable`、`noMojibake`、`noSevereOverlap`、`noSevereClipping`、`alignmentAcceptable`、`contentMatchesIntent`、`reusableOutputLikely`、`evidenceBoundaryRespected`、`nonScreenshotEvidenceChecked`；缺任一必需 Agent 输出或字段时，`workflow_dispatch` 以 `a-to-a hard gate` 阻断；检查入口 `scripts/run_a_to_a_orchestration_gate_check.py`。
- **MAIN-AGENT-DISPATCH-AWARENESS-01**：高风险 A-to-A 合同轻量新增 `mainAgentSelfCheck` 与 `dispatchDecision`。主 Agent 自检只表示工程责任边界：识别任务、生成合同、动态加派已登记 Agent、收 hard gate 输出并阻断虚假完成；不模拟对话人格、不替代 CAD readback / 视觉复审 / 资产审计。未登记新 Agent 只能进入 `additionalAgentRequests`，状态为 `needs_reviewed_package` / `needs_openspec_change`，不得临场激活。
- **LOCAL-REPAIR-FIRST-01**：局部错误原位修复优先。用户指出局部乱码、缺线、错线型、错 hatch、标注或部件局部问题时，先读上一轮 `execution_summary` / created handles / CAD readback，生成 `repair_plan`，只对 `target_handles` / `target_bbox` 执行 `update`、`delete_replace` 或 `add_missing`；用户开放删除编辑命令只覆盖 `CODEX_PREVIEW` 中被证据锁定的错误对象，不允许整图清空、全模型空间删除、正式图层修改、保存或覆盖 DWG。handles 失效、对象被炸开 / 删除、局部修会破坏整体拓扑，或全局坐标 / 比例 / 布局根因错误时，才允许整块重画。
- **REPAIR-RUN-BEFORE-DELIVERY-01**：所有修复默认先运行覆盖原问题的最小实际链路再交付。普通代码 / 文档 / 规则修复至少跑对应测试、校验、审计或格式检查；CAD 落图、截图、训练、runner、验证、资产复用 / 沉淀或局部修复链路改动，除单测外还要补一条代表性实际链路。真实 CAD / GUI / COM 不可用时先按 blocker 自救并必要时申请外部执行；仍不可用只能报 `blocked` / `not_run` / `not_verified`，不得用完成口吻。
- **SCREENSHOT-ORCHESTRATION-HARDENING-01**：截图底座已改为任务级编排。截图入口先输出 `screenshotDecision`，局部 `target_handles` / `repair_plan` / bbox 优先，才退到 `execution_summary.created_handles`；默认用 AutoCAD 客户区 `PrintWindow`，不强制置顶，截图只作 `visual_aid_only`，不能替代 created handles / CAD readback / bbox 审计。Agent 共用合同和工作台 Agent check 已接入该规则；真实单 handle 截图证据为 `output/previews/screenshot-orchestration-target-1F7C.png`。
- **TRAINING-TIMEOUT-CIRCUIT-BREAKER-01**：自动化训练规则已要求 30 秒单步 watchdog、超时自救和连续超时熔断；规则层保护不等于脚本执行器已全量实现。
- **DESIGNER-AGENT-GROWTH-PATH-01**：主训目标是 `CAD Designer Agent` 成长路径；`agents/cad_designer/`、成长路径文档和 L0 基础课程已成为训练默认入口；不改表 C。
- **DESIGNER-TRAINING-PLAN-V2-01**：训练地图已扩到 217 项，V2.1 已有 8 个批次和 10 个验收器骨架；骨架不是 CAD proof，不代表已会施工图。
- **TRAINING-QUEUE-AUTO-SYNC-01**：监督式训练队列在 `--decision pass` 或队列完成后自动执行训练工作台 post-sync；用户不需要每轮额外提醒同步。
- **TRAINING-QUEUE-FOUNDATION-10-01**：第一批 10 个基础 CAD 操作项已验收并通过 learning promotion 沉淀到责任智能体；事实源登记见 `docs/training/training-sources.json`。
- **TRAINING-FOUNDATION-REMAINING-21-01**：剩余 21 个基础 CAD 操作项已由 `scripts/run_cad_foundation_remaining_training.py` 真实 CAD 批量训练；最终报告 `output/training_queues/cad-foundation-remaining-21/remaining-21-chinese/remaining_21_report.json` 已做中文标注复训，当前为 21/21 pass、235/235 句柄回读、`chinese_labels=text_labels=65 latin_terms=0`，可见文本扫描 86 条 / 英文术语 0 条，工作台同步 pass，learning promotion 合计 31 items / 7 agents。
- **TRAINING-HATCH-PATTERN-SAMPLES-01**：第 12 项“填充与边界”已按用户要求复训为 8 个小方格 hatch 样板；真实 CAD 回读 patterns=`ANSI31, ANSI31, ANSI32, ANSI37, AR-CONC, BRICK, GRAVEL, EARTH`，scales=`0.45, 1.1, 0.8, 0.75, 0.7, 0.65, 0.55, 0.6`，全部 `CODEX_PREVIEW`。
- **TRAINING-LATENCY-ROUTING-01**：训练期 CAD 小动作按三档量化路由执行：`quick_trial` ≤2 分钟、1 次 CAD 写入 + 1 次关键回读且不沉淀；`focused_retraining` ≤8 分钟、只覆盖点名能力；`formal_acceptance` 才跑完整验收 / 同步 / 表 C 相关链路。
- **TRAINING-SCOPE-GUARD-01**：单项 / 子主题加深训练不得自动扩大为整批训练；`scripts/run_cad_foundation_remaining_training.py` 支持 `--only`、`--hatch-pattern`、`--hatch-scales`，focused 报告写 `scope.mode=focused` 且不覆盖 full-batch 验收。
- **TRAINING-PARKING-ANCHOR-01**：用户可手动移动训练面板便于查看；复训脚本优先回读上一轮 created handles 的当前位置作为 `parking_anchor`，只有 handles 失效时才退回全局 `CODEX_PREVIEW` bbox，避免训练目标按全画布最右侧漂移。
- **TRAINING-FOUNDATION-REFLOW-RULE-01**：基础训练 `systemized/pass` 不是永久封存；复杂任务暴露基础薄弱时，要记录触发点、映射基础项、修改脚本 / Prompt / 检查器 / 规则，复训基础项并回测原任务，新证据追加到训练事实源和 learning promotion。
- **COMPOSITE-TASK-ROUTING-01**：未列入 V2 计划的临场复合任务走动态编排：拆能力节点、声明 `evidence_source`、走 `CAD_PLAN` / validate / dry-run / `CODEX_PREVIEW` / readback / audit；截图推断不得冒充 CAD 尺寸回读，单次组合不污染训练地图。
- **TRAINING-WORKBENCH-FOUNDATION-ASSET-NA-01**：基础 CAD 操作的“图库 / 自产”轨道为不适用；成功证据看 `CAD_PLAN`、handles、bbox、端点、闭合、图层和审计。
- **CAPABILITY-MAP-SYNC-01**：训练工作台是静态快照显示器，事实源来自 coverage、训练 source manifest、learning ledger 和 Agent memory；刷新必须跑 `scripts/sync_training_workbench.py`。
- **DATA-BLOAT-GOVERNANCE-BEFORE-TRAINING-01**：训练前 / 收尾新增数据防膨胀与证据闭合门禁。A-to-A 合同涉及训练收尾、正式工作台收尾、系统资产沉淀或仓库级治理时必须列 `data_bloat_governance` hard gate；由已登记 `pipeline_context_curator`、`pipeline_audit`、`pipeline_learning_promoter`、`pipeline_delivery` 协同确认 `protected` / `candidate` / `blocked` / `derived`，且 `run_doc_governance_audit.py` 已检查 manifest 映射。`workbench_snapshot_refresh` 只是轻量查看例外；`retention_report.json`、data-bloat audit report、sync report 和 `capability-map-data.js` 只能是 diagnostic / derived，不进入 `training-sources.json` 的 `fact_source`；清理 / 归档写入前必须先跑 retention dry-run 或等价 evidence-closure gate。
- **SYSTEM-ASSET-LIBRARY-GOVERNANCE-01 / SEDIMENTATION-PROTOCOL-01**：用户明确说“沉淀 XX 资产 / 通用资产 / 收进资产库”时，默认走系统资产四件套前先过 `pipeline_asset_governor` 资产库守门员；守门员判断来源边界、clean reusable source、子 Agent 派发和 `polishHardeningDecision`。系统资产 DWG 默认分 `00_INDEX`、`01_CLEAN_ASSETS`、`02_PREVIEW_CARDS`、`03_REVIEW_QUARANTINE`、`99_EVIDENCE_LINKS`，训练标题 / 临时说明 / 边框 / 尺寸线 / 审计文字 / 证据路径不得进入 `01_CLEAN_ASSETS`。入口 `scripts/sediment_system_asset.py`，协议 `docs/architecture/system-asset-sedimentation-protocol.md`；资产条目要求 `candidate/systemized/verified/deprecated` 状态流、`retrieval`、`native.layoutPlan` v2、`libraryGovernance`、`versioning`、`verification`、`feedbackLoop`、`exportManifest`、`antiContamination`。系统资产 DWG 仓库验收必须同时有 created-handle readback、`visualClearanceAudit.status=pass` 和 `visualReadabilityAudit.status=pass`；截图非空、保存成功或 `overlapCount=0` 不能替代通道、内容密度、source/proof 分离和图层语义审计。对象 block export 只能来自 selected/created/active handles、明确 bbox 或 named block，来源不足进入 metadata-only / quarantine；样式标准走 `style_export`。“沉淀”默认授权创建、打开 / 激活、写入和保存对应系统资产 DWG，但不覆盖用户当前业务 DWG；`--verify` 同时验元数据、layoutPlan v2、守门员决策和声明级门禁，缺 `nativeVisiblePanelEvidence`、`reuseWorkflowProbe` / `reuseReplay` 或 CAD readback 时不得声称真沉淀、可复用或 A-to-A 已打通。
- **SYSTEM-ASSET-REUSE-WORKFLOW-01**：跨 DWG 复用已升级为 workflow 底座；`core.assets.system_asset_reuse` 支持显式复用语义、隐式强匹配、候选排序、多资产任务拆分、`partial` 阻断、精确来源门禁和 fake-driver 回读，CLI 为 `scripts/reuse_system_asset.py --workflow`。主系统后续遇到“放一个线型表，再放一个沙发”或没有显式“资产”但强匹配系统库的请求时，应先生成 `system_asset_reuse_workflow`；无资产信号返回 `not_asset_reuse_request` 后再走普通 `CAD_PLAN`。润色加固后，单个复用计划只有 created handles 且 `readbackStatus=ok` 才能判为 `asset_reused`，CLI 输出必须是严格 JSON。
- **CAD-SEMANTIC-ASSET-REUSE-UPGRADE-01**：大型升级已新增 `core.assets.semantic_rules` 和 `core.training.linetype_table_audit`。白话请求先匹配语义规则库，再进入资产复用 / 沉淀 / 线型表 / 局部修复等链路；系统资产复用前对 registry 文本运行 `encodingPreflight`，坏中文返回 `asset_registry_encoding_failed`，弱匹配只给候选。线型表生成器支持 variable rows，报告新增独立 `layoutAudit`，审计中文 canonical 文本、无填充、样线格 containment、自适应行高、样式多样性和截图证据边界。
- **UTF8-FIRST-CAD-ASSET-GUARD-01**：中文编码问题必须前置根治，不得靠“先画错、截图发现、再修复”。`scripts/_bootstrap.py` 强制 `PYTHONUTF8=1` / `PYTHONIOENCODING=utf-8`；`core.runtime.encoding_guard` 检测 `??`、`�` 和典型 mojibake；系统资产沉淀在写 `assets.json` / `registry.json` 前运行 `encodingPreflight`，线型表在绘制前验证 visible text。失败时阻断，不写 CAD、不保存 DWG。
- **表 C / 旧施工包历史**：已迁入 `docs/status/changelog.md`、`docs/planning/archive/` 与 `docs/handoffs/archive/`；短上下文只保留当前机器值和活跃训练 / 架构事实。
## 主从关系

- `CORE_RESTRUCTURE_PLAN.md` 是唯一 `PlanMD`。
- `docs/planning/任务清单.md` 是唯一执行台账和即时 `next` 镜像。
- `CORE_STATUS.md` 解释能力状态和表 C；机器值以 coverage JSON 为准。
- `docs/status/current.md` 写当前状态；`docs/status/changelog.md` 写历史流水；`docs/status/issues.md` 写风险和教训。
- `docs/handoffs/current.md` 写最近包交接；`docs/handoffs/package-index.md` 查全量包；历史包在 `docs/handoffs/archive/`。
- `output/validation_runs/**` 是机器证据本体，不因 Markdown 整合而移动。

## 不能声称

- 不能把 Core 约 96%、RCAD 29/29 或 no-CAD benchmark 说成“已经能画准施工图”。
- 不能把截图、SVG/PNG 预览、dry-run 或 `benchmark_pass_non_cad` 当成几何准确证据。
- 不能把 `negative_guard_verified`、fake driver 结果或 no-CAD deferred 当成真实 CAD 几何通过。
- 不能把单元测试通过或“已写未运行边界”当成 CAD 链路修复交付；影响 CAD / 截图 / runner / 训练 / 验证的修复默认要跑实际链路，跑不了就报 `blocked` / `not_verified`。
- 不能默认保存、覆盖、删除 DWG，不能修改正式图层；真实 CAD 默认只写 `CODEX_PREVIEW`。

## 按需展开

| 目标 | 先读 |
| --- | --- |
| 系统任务链路 / 白话拆分 / A-to-A 校准 | `docs/architecture/cad-agent-task-chain.md` |
| 模型型 Agent / Trace / Prompt / Host runtime | `CORE_RESTRUCTURE_PLAN.md` §0.1 + `agents/pipeline/README.md` |
| CAD Designer Agent 成长路径 / 基础课程 | `docs/training/cad-designer-growth-path.md` + `agents/cad_designer/rules.md` |
| 训练一轮 / 建案例 | `docs/training/README.md` + `docs/planning/任务清单.md` §0 |
| 执行开发包 / 调整优先级 | `CORE_RESTRUCTURE_PLAN.md` + 任务清单 |
| 汇报完整能力成熟度 / 展开 A/B/C | `CORE_STATUS.md` + `docs/status/current.md` + coverage JSON |
| CAD 补验 / 画不准 / 环境不通 | `docs/runbooks/blocker-playbook.md` + `docs/runbooks/cad-validation.md` |
| 查历史变更流水 | `docs/status/changelog.md` |
| 查失败教训和活跃风险 | `docs/status/issues.md` |
| 查按包交接 | `docs/handoffs/current.md` + `docs/handoffs/package-index.md` |
| 新人接手 | `docs/onboarding/first-handoff.md` |
| 文档治理 | `docs/planning/phases/phase-z-doc-governance.md` + `scripts/run_doc_governance_audit.py` |

## 常用验证
固定 `$py="$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"` 后运行：`-m unittest discover -s tests`、`scripts\run_repo_audit.py --max-python-lines 500 --fail-on-severity medium`、`scripts\run_doc_governance_audit.py`、`scripts\run_dev_volume_audit.py --summary-only --top-groups 5 --fail-on-severity medium`、`scripts\run_capability_coverage.py --output output\validation_runs\capability-lab\cad_capability_coverage.json`。

## 缓存友好约定

- 本文只写短摘要、当前 next、口径和入口，不写长历史。
- 历史进 `docs/status/changelog.md` 或 `docs/history/`。
- 失败教训进 `docs/status/issues.md`。
- 计划和优先级进 `CORE_RESTRUCTURE_PLAN.md`，执行计数进 `docs/planning/任务清单.md`。
