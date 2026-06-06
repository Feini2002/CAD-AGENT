# CAD Agent 变更记录

这个文件记录 CAD Agent 测试工作区的结构、规则、Schema、脚本和重要决策变化。

## 2026-06-07

### MAIN-AGENT-COGNITION-PROOF-TEMP-PLAN-01：主 Agent 认知提升证明临时计划

- **触发**：用户指出系统可能持续堆规则、Prompt、测试和训练记录，但主 Agent 未必真的在后续任务中改变判断；如果没有这个评价维度，所谓“变聪明”可能只是机制变厚。
- **硬口径**：任何声称主 Agent 变聪明的改动，都必须证明它改变了主 Agent 在真实任务中的判断；否则只能叫机制建设，不能叫认知提升。
- **同步**：将该口径写入 `CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`AGENTS.md`、`CORE_STATUS.md`、`README.md`、`agents/pipeline/README.md`、`docs/governance/cad-agent-rules.md`、`docs/training/README.md`、`docs/architecture/cad-agent-task-chain.md` 和 `docs/status/current.md`。
- **临时计划**：新增 `output/debug/main-agent-cognition-proof-temp.md`，规划 `MAIN-AGENT-COGNITION-PROOF`，专测主 Agent 是否因历史经验、模型判断或上下文证据改变 route、dispatch、tool choice、blocking、requiredAgents、learningCandidate 或下一次 replay。
- **边界**：该临时 MD 不是事实源，不证明真实 CAD 能力、不提升表 C、不部署 Worker、不代表主 Agent 已经 Codex-like；后续若执行，应迁移为正式 OpenSpec change。

### ADAPTIVE-CAPABILITY-GROWTH-TRAINING-01：自适应能力成长训练闭环与临时 MD 删除

- **触发**：用户要求把 adaptive capability growth 临时调研稿里关于“训练过的能力不能只回到烟测表达”的问题做仓库级收尾，补齐安全边界、反面论证、未实现项和验证后删除临时 MD。
- **实现**：新增 `core/training/capability_growth_profile.py`、`core/training/adaptive_replay_planner.py`、`core/training/expression_regression_gate.py` 和 `core/training/adaptive_growth_closeout.py`；`foundation_batch_training` 与 `scripts/run_cad_foundation_remaining_training.py` 接入 `--replay-mode smoke_replay|growth_replay|standard_replay` 和 repo-local `--capability-profile`。`growth_replay` 会把能力画像、历史 lessons、required features、negative examples 和 retest boundary 写入 adaptive replay 证据。
- **安全边界**：能力画像只接受仓库内 active / protected 事实源；`output/debug`、工作台派生数据、诊断报告、外部路径、缺失文件、截图和模型 pass 都不能当 hard baseline。缺正例、反例、原任务回测或 required / observed feature 对比时，closeout 只能 `blocked` / `not_verified`。
- **临时 MD 收尾**：OpenSpec change `adaptive-capability-growth-training` 的任务清单已完成；临时调研稿在事实回写后删除，不登记为训练事实源。
- **边界**：本包不连接真实 AutoCAD、不保存 / 修改 DWG、不部署 Worker、不写训练事实源、不刷新工作台、不提升表 C；只证明 no-CAD / fake-CAD runner、路由、回归门禁和完成声明边界。

## 2026-06-06

### WORKER-RUNTIME-TRACE-WORKBENCH-MVP-01：训练工作台链路追踪小面板

- **触发**：用户希望在当前训练工作台页面里看到从 Codex 白话、Worker 通道、Agent 拆分、validate / dry-run、本地 bridge / CAD-MCP 到 CAD 预览和收尾门禁的链路状态、耗时、卡点和证据路径，用于后续调试。
- **实现**：新增 `scripts/build_runtime_trace_snapshot.py`，从最近一次 `model-agent-live-collab-proof-*` run package、Worker 部署清单、CAD preview/readback 报告、截图和视觉复核报告生成 `output/runtime_traces/latest.json`；`start_training_workbench.bat` 在刷新训练台快照后同步生成该链路快照，失败不阻断页面打开。
- **前端**：`capability-map.html` 的训练飞控台新增“链路追踪”面板，展示总状态、总耗时、通过步骤、阻断数、Worker version/runId、每一步 owner/status/duration/evidence/blocker，并在本地 HTTP 页面中每 5 秒刷新快照。
- **白话化加固**：面板改为新手可读的“现在发生了什么 / 下一步看这里 / 记录会不会膨胀 / 紧凑步骤小窗”结构，状态翻译为“已通过 / 卡住了 / 未检查”，并把 `storagePolicy` 显示为“只覆盖 latest.json，不追加历史；原始 CAD 证据包由仓库保留策略单独治理”。长证据路径改为悬停提示，不再占用主窗口正文。
- **验证**：`scripts/build_runtime_trace_snapshot.py` 通过 `py_compile` 并生成 `traceStatus=blocked` 快照；本地训练台 HTTP `200`；Chrome headless 截图 `output/previews/runtime-trace-workbench-compact-20260606.png` 已确认面板渲染、文本可读且状态卡片未明显重叠。
- **边界**：该面板是只读本地快照，不主动执行 CAD、不调用 Worker、不证明真实 `gpt-5.5` provider、不提升表 C；当前显示的 `blocked` 来自上一轮 closeout / visual review 缺字段，不是新训练失败。

### WORKER-BRIDGE-CAD-PREVIEW-SMOKE-01：Worker 通道与本机 CAD 安全预览 quick smoke

- **触发**：用户已打开 CAD，要求把通道测试、安全预览和少量 CAD 模拟绘制连续跑完，但不进入正式训练。
- **远程通道**：使用用户 Wrangler OAuth 登录态重新部署 `cadagent`，通过临时 secrets-file 注入本轮 `WORKER_API_TOKEN`、`BRIDGE_API_TOKEN`、`ADMIN_API_TOKEN`，临时文件删除且 secret 未提交；最新 version 为 `21fc6755-27d0-4e97-b13a-ef1e660c8401`。
- **smoke 加固**：远程 Durable Object 会持久记录 revoked bridge，因此 `workers/orchestrator/test/orchestrator-smoke.mjs` 新增 `WORKER_SMOKE_SKIP_REVOKE=true` 模式，让远程 smoke 避免永久污染测试 bridge；本地 runtime tests 仍覆盖 revoked bridge 行为。
- **远程验证**：远程 smoke pass，`runId=run_20260606151438_worker_orchestration_ready_f6260886`、`state=completed`，覆盖 health、auth negative、bridge register/list/offline、lease、heartbeat、submit、idempotency conflict、dangerous result block、diagnostics。
- **CAD 预览**：运行 `scripts/run_model_agent_live_collab_proof.py --fixture-model --driver-mode autocad_existing`；本机 AutoCAD 当前文档 `测试文件.dwg` 中只写 `CODEX_PREVIEW`，`createdHandleCount=7`、`readbackEntityCount=7`、`cadGeometryVerified=true`、`savedCurrentDwg=false`，run package 为 `output/runs/model-agent-live-collab-proof-20260606-151512/`。
- **截图与边界**：截图 `output/previews/worker-bridge-cad-preview-20260606-151512.png` 已按本次 7 个 handles 聚焦，角色为 `visual_aid_only`。本包不是正式训练，不提升表 C，不证明真实 `gpt-5.5` provider；表 C 视觉复核脚本因 readback 报告缺旧字段 `evidence_state` 未作为正式 closeout 放行。

### WORKER-ORCHESTRATOR-CLOUDFLARE-DEPLOY-01：Cloudflare Worker 初始远程部署与 smoke

- **部署**：用户授权后使用 Wrangler OAuth 登录态部署 Worker。Cloudflare / Wrangler 要求 Worker `name` 为小写字母数字加短横线，因此用户指定的 `CADAgent` 规范化为 `cadagent`。部署 URL：`https://cadagent.cmw1196466375.workers.dev`；当前 version：`ecf455d4-89f0-4b14-92aa-0c3885c7c491`。
- **配置**：`wrangler.jsonc` 改为 `name=cadagent`、`ENVIRONMENT=cloudflare-initial`；`package.json` 新增受控部署脚本；`run-wrangler.mjs` 只在 `CADAGENT_DEPLOY_APPROVED=true` 且 `deploy --strict --secrets-file` 时允许真实部署，继续阻断裸 deploy、`secret put` 和 `dev --remote`。
- **secret**：部署时临时生成 `WORKER_API_TOKEN`、`BRIDGE_API_TOKEN`、`ADMIN_API_TOKEN`，通过 `wrangler deploy --strict --secrets-file <temporary-json>` 上传；临时文件部署后删除，真实 secret 未写入仓库。
- **验证**：部署前 `npm.cmd run worker:check` pass；远程 smoke 首次立即运行遇到 Cloudflare `1042` 传播 / 路由瞬态，重新部署并等待 30 秒后通过。最终远程 smoke 输出 `status=pass`、`runId=run_20260606144204_worker_orchestration_ready_06e12cd1`、`state=completed`。
- **边界**：本包只证明远程 Worker / Durable Object 编排激活；未接 Queue / Workflows、未启动真实 local bridge runner、未调用真实 `gpt-5.5` runner、未连接 AutoCAD / CAD-MCP、未写 / 保存 DWG，不提升表 C。

### WORKER-ORCHESTRATOR-PREDEPLOY-HARDENING-01：Cloudflare Worker 预部署编排层落地与临时 playMD 删除

- **实现**：新增 `workers/orchestrator/**`、根级 `wrangler.jsonc`、`package.json` / `package-lock.json` worker 脚本和 `.gitignore` 规则，形成 Cloudflare Worker + Durable Object run state 的预部署编排层。当前覆盖 run / task graph、bridge 注册 / lease / heartbeat / submit、heartbeat token、bridge token、idempotency、timeout / retry / DLQ、bridge stale / offline、backpressure、circuit breaker、kill switch、redaction 和严格 JSON API 边界。
- **加固**：submit 必须绑定 lease identity、attempt、result hash 和 `heartbeatToken`；revoked bridge 的 lease / heartbeat / submit replay 会在 idempotency 之前被阻断；task graph 写入前拒绝重复 `taskId`、缺失依赖和循环依赖；wrapper 只允许本地 `dev --local`、`types` 和 `deploy --dry-run`，阻断真实 deploy、`secret put` 和 `dev --remote`；secret scan 覆盖 `.dev.vars*`。
- **文档收尾**：删除本轮临时 Worker 执行 playMD；保留 `WORKER_ORCHESTRATOR_DEPLOY_CHECKLIST.md` 作为远程部署前停闸清单；同步 `CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/status/current.md`、`docs/status/changelog.md`、`docs/handoffs/current.md`、`docs/handoffs/package-index.md` 和 `CORE_STATUS.md`。
- **验证**：`npm.cmd run worker:check` 通过，其中 runtime tests 14 pass，TypeScript `--noEmit`、secret scan、wrangler types 和 `wrangler deploy --dry-run` 均通过；本地 `wrangler dev --local` HTTP smoke 通过，包含 wrong submit `heartbeatToken`、idempotency conflict、dangerous CAD intent、backpressure 和 cleanup；wrapper 负向验证确认真实 deploy、`secret put`、`dev --remote` 被阻断。
- **边界**：本包只到 local / dry-run 预部署骨架；未执行 Cloudflare remote deploy，未写真实 Cloudflare secret，未接 Queue / Workflows，未运行 bridge-owned Codex config，未触发真实 `gpt-5.5` runner，未连接 AutoCAD / CAD-MCP，未写 / 保存 DWG，不提升表 C。

### ARCH-CONVERGENCE-01：架构归并画布与旧指标降级

- **触发**：用户指出当前系统像一张被多轮探索式开发画满的画布：早期表 A/B/C、V-PROOF、RCAD，后续训练、资产、多 Agent、模型桥、Worker 编排和工作台都很充实，但没有统一主构图；旧“真实 CAD 实力 90%”会误导真实训练判断。
- **决策**：正式对象训练暂缓，先做仓库级架构归并。新增七层画布：系统入口、任务对象、决策编排、能力与证据、执行工具、审计修复、沉淀成长。后续每个模块必须说明自己属于哪一层、输入输出是什么、不能越过哪一层。
- **口径归并**：旧表 C / 90% 降级为 `Core Proof Coverage`（底座证据覆盖），不得代表 `Agent Task Maturity`（端到端任务成熟度）或 `Project Delivery Readiness`（真实项目交付准备度）。当前 Agent 真实任务成熟度仍按早期看待，需要通过训练案例、用户 feedback、created handles readback、局部修复和资产复用 replay 逐步建立。
- **文档同步**：新增 `docs/architecture/system-architecture-convergence.md`；新增 OpenSpec change `openspec/changes/unify-system-architecture-canvas/`；同步 `CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`AGENTS.md`、`docs/governance/cad-agent-rules.md`、`docs/planning/任务清单.md`、`docs/status/current.md`、`docs/status/issues.md` 和 `docs/training/README.md`。
- **边界**：本轮只做架构设计、规则和计划同步；不连接 AutoCAD、不写 / 保存 DWG、不删除实体、不提升表 C、不运行正式训练、不改训练事实源或系统资产 registry。后续执行按 OpenSpec tasks 做脚本和派生显示审计。

### LOCAL-LIVE-MODEL-BRIDGE-HARDENING-MD-CLOSEOUT-01：模型桥安全加固与独立 MD 收口

- **实现**：加固 `LocalLiveModelBridgeRuntime`：未知 `target_stage` 直接失败，同秒 run id 增加随机后缀，live 阶段未登记 / 能力不匹配 bridge 不能 lease，`submit_result` 校验 lease identity；CAD fake preflight 拆分 `runtimeStatus` 与 `proofStatus`，避免把编排通过说成真实几何证明。
- **诊断**：`diagnose_run()` 不再只信 `worker_run_state` 的模型摘要，必须沿 `traceRef` 校验 `trace_review.json`、`trace_manifest.json`、`command.json` 和 `normalized_output.json`，且要求 `modelProviderStatus.route=codex_cli_local` 与 sanitized `codex.cmd exec --model gpt-5.5` 命令证据。
- **文档收口**：原独立本地活体模型桥架构 MD 的剩余内容迁入 `CORE_RESTRUCTURE_PLAN.md` §3.1，主动入口改为主计划、runtime、diagnostics 和状态 / 交接记录；独立 MD 删除，避免形成第二套主计划。
- **边界**：本包不新增真实 CAD 证明；fake driver 仍只证明编排和 preview-only 安全边界，真实 `cad_mcp_preview_live` 仍需 AutoCAD / CAD-MCP handles readback。

### LOCAL-LIVE-MODEL-BRIDGE-DIAGNOSTICS-01：分层放行口径与运行诊断脚本

- **触发**：用户补充架构口径：可以一次性搭完整 Worker-first 系统骨架，但运行放行必须按 `worker_orchestration_ready -> local_bridge_connected -> single_agent_live -> multi_agent_live -> cad_mcp_preview_live` 分层启用；默认只证明 Worker 编排，不得一次性无条件打开真实 bridge、GPT-5.5 或 CAD-MCP。
- **实现**：新增 `core.orchestrator.local_live_model_bridge_diagnostics.diagnose_run()` 和 `scripts/diagnose_local_live_model_bridge.py`，只读 `worker_run_state.json` / `cadPreview` 等运行证据，输出 `local-live-model-bridge-diagnostic/v1`，定位 `firstBlockedAt`、`blockedReasons` 和 `nextAction`。`worker_run_state` 同步写入 `featureGates`，默认关闭真实 bridge / GPT-5.5 / 多 Agent / CAD preview / 保存授权等高风险层；CLI 默认只诊断，`--fail-on-blocked` 可作为门禁失败码。
- **文档同步**：当时更新独立架构 MD，明确“一次搭完整骨架、feature gates 分层放行”的口径，并把诊断入口写入 W1；后续在 `LOCAL-LIVE-MODEL-BRIDGE-HARDENING-MD-CLOSEOUT-01` 中已迁入 `CORE_RESTRUCTURE_PLAN.md` 并删除独立 MD。
- **边界**：诊断脚本不会启动 bridge、不会调用 GPT-5.5、不会连接 CAD、不会保存 DWG；fake driver 仍只证明编排，不证明真实 AutoCAD 几何，也不提升表 C。

### LOCAL-LIVE-MODEL-BRIDGE-ARCHITECTURE-01：Worker 编排 + 本地活体 GPT-5.5 模型桥路线

- **触发**：用户最终选择长期发展优先接入 Cloudflare Worker，希望先把远程触发、多状态机、队列、retry、heartbeat 和多 Agent 依赖编排框架打好，再解决本地 bridge 调 Codex CLI / GPT-5.5 的活体问题。
- **方案**：当时新增独立架构 MD，把路线收束为 Worker 编排 + 本地 bridge 执行：先完成 `worker_orchestration_ready`，再完成 `local_bridge_connected`，最后完成 `single_agent_live`，证明一个 Agent 在 Worker run package 下经本机 `codex.cmd exec --model gpt-5.5` 输出 strict JSON、schema validation、trace 和下游 decision；再扩到 `multi_agent_live`；最后通过 Tool Contract ReAct 接入 CAD-MCP preview-only 闭环。
- **执行契约扩充**：按用户要求继续扩充同一 MD，补入 Cloudflare 产品分工、Worker API 最小端点、`task_envelope` / `agent_output` / `run_state` 数据合同、Worker 侧系统角色、模型型 Agent Prompt 合同、队列 / 依赖 / 状态机规则、安全与数据边界，以及 W0-W5 后续执行目标计划。随后继续补入超时预算、熔断器、retry / DLQ、backpressure、防重复提交、bridge 离线降级、provider / CAD-MCP 不可用降级、kill switch、观测脱敏和安全认证边界；这些剩余项后续迁入 `CORE_RESTRUCTURE_PLAN.md` §3.1。
- **同步**：更新 `CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`docs/status/current.md`、`docs/planning/任务清单.md`、`docs/architecture/README.md`、`docs/architecture/cad-agent-task-chain.md` 和 `agents/pipeline/README.md`，统一“活体 Agent”的机器定义：必须有 Worker run state、`modelInvoked=true`、`modelUnavailable=false`、`schemaValid=true`、provider status、sanitized command 和 trace。
- **边界**：本轮只整理架构和状态文档；未真实调用模型 provider，未部署 Cloudflare Worker，未连接 AutoCAD，未写 / 保存 DWG，未运行 CAD-MCP，不修改训练事实源、系统资产 registry、Agent memory、Prompt addendum 或表 C。Worker 负责编排和远程触发，不能保存 Codex 登录态、不能直接执行 `codex.cmd`，也不能替代本地 bridge。

## 2026-06-05

### MODEL-AGENT-LOCAL-HARDENING-RECHECK-01：无网络 Agent 链路复校与 fixture live proof

- **触发**：用户要求再次修复校验，确保除后续单独处理的网络 / provider 问题外，Agent 端类层面的整条链路不再卡在本地 fixture、handoff、ToolIntent 或 closeout 报告粗糙点上。
- **修复**：`scripts/run_model_agent_live_collab_proof.py` 新增 `--fixture-model`，可用本地 schema-shaped 模型输出跑通 `design_director -> style_generator -> design_reviewer -> visual_intent -> intent -> audit -> delivery` 链路；该模式不调用 Codex CLI、不访问模型 provider，并在输出中写入 `localFixtureModel` 和 `localAgentChainProof`。
- **报告收口**：`core.orchestrator.closeout_gate` 将状态机 `missingEvidence` 与用户可读 `blocking_reasons` 分开，避免把 `created_handles_readback=ok`、`real CAD geometry verified` 这类目标证据标签混入阻断原因；阻断原因现在保持否定性表达。
- **验证**：新增 `tests.core.test_model_agent_live_collab_cli` 覆盖 CLI fixture proof；新增 closeout 回归防止正向 evidence 标签混入 blocking reasons。本轮最终验证命令和结果见交付回复。
- **边界**：fixture proof 只证明本地 Agent 链路、schema、handoff、ToolIntent 和 fake-driver 边界；仍不证明真实 OpenAI provider、真实 `gpt-5.5` 判断质量、真实 AutoCAD 几何、截图视觉验收或用户验收。

### MODEL-AGENT-LOCAL-HARDENING-01：模型型 Agent 本地边界与 closeout 链路加固

- **触发**：用户要求执行 `docs/architecture/model-agent-local-hardening-plan.md`，并允许创建辅助 Agent 协作，目标是在网络 / OpenAI provider 不稳定时先把本地模型桥、Agent 交接、工具请求和交付闭环做成可测试状态。
- **实现**：新增 `model-export-manifest/v1` 与调用前阻断、repo-external Codex CLI cwd、context leak audit、统一错误 taxonomy、visible audit fields、`handoff_packet/v1`、ToolIntent `resultStatus`、closeout state machine，以及无网络 proof 脚本 `scripts/run_model_agent_local_hardening_proof.py`。
- **链路**：模型桥现在每次 trace 写入 `export_manifest.json` / `context_leak_audit.json`，manifest blocked 时不启动 runner；no-CAD model chain 会写上游 handoff packet 并让下游引用 packet path/hash；closeout gate 由状态机明确区分 CAD evidence missing、visual evidence missing 和 ready for user review。
- **验证**：本轮最终验证命令和结果见交付回复；本地 proof 输出 `status=pass`、`repoExternalCwd=true`、`unexpectedProjectContextLoaded=false`，并显式列出未证明真实 OpenAI provider、真实 `gpt-5.5` 判断质量、真实 AutoCAD 几何和用户验收。
- **边界**：本包不联网调用真实模型、不连接 AutoCAD、不写入或保存 DWG、不提升表 C；模型 pass 仍不能替代 UTF-8、schema、validate / dry-run、CAD handles readback、截图辅助、sourceSpec、reuseReplay 或用户验收。

### CORE-PLANMD-ARCH-ROUTER-01：唯一主 PlanMD 改写为系统宪章 / 架构路由器
- **触发**：用户要求在系统从“无智能 / 底座施工 / 规则型 Agent / 模型型 Agent”多轮演进后，重新讨论主方向，收束主 PlanMD 中已经完成、过细或不再适合当未来路线的内容，同时保留规则、调用边界和证据链。
- **实现**：将 `CORE_RESTRUCTURE_PLAN.md` 改写为 118 行控制面：只保留本文职责、主架构链路、不可破坏边界、事实源地图、未来开发路由、Decision Gates、执行入口、完成声明标准和历史归档；删除旧包过程、sofa 试点长细节和模型 runtime P7-P10 施工摘要在主计划中的堆叠。
- **主路线**：未来路线收束为模型型 Agent 活体协作证明、资产智能 verified reuse、高风险 A-to-A hard gate、证据 / 数据治理、真实案例 / 复合任务小闭环、表 C / 真实 CAD 回归和文档治理；训练内容只保留 `Visual-First` / `visual_parts` 边界和事实源链接，不扩写训练项。
- **边界**：本轮不连接 AutoCAD、不写 / 保存 DWG、不删除 CAD 实体、不改正式图层、不修改训练事实源、系统资产 registry、Agent memory 或 Prompt addendum；表 C 只保持现有机器口径，不刷新、不提升。
- **验证**：`scripts/run_doc_governance_audit.py --fail-on-findings` pass；相关回归 `tests.core.test_doc_governance tests.core.test_planmd_governance tests.core.test_self_check tests.core.test_core_restructure` 48 OK。

### ARCH-DOC-GOVERNANCE-CONSOLIDATION-02：活跃文档瘦身与旧入口兼容收口
- **触发**：用户要求在系统从底座施工期转入模型型 Agent / 训练治理期后，先做架构与 MD 治理，删除或整合多余解释，保留规则、调用边界和证据链。
- **实现**：将 `docs/status/current.md` 压缩为当前状态入口，只保留主方向、有效包、风险和入口；把旧流水继续放 `docs/status/changelog.md` / `docs/handoffs/archive/**`。`docs/handoffs/current.md` 只保留最近资产智能链路活跃包，旧 current 窗口已迁入 `docs/handoffs/archive/2026-06.md`；`docs/handoffs/package-index.md` 改为当前窗口 + 月归档索引。同步压缩 `AGENTS.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_RESTRUCTURE_PLAN.md` 的重复说明，并修正 `docs/ROADMAP.md` / `docs/roadmap/README.md` 对已删除中文 stub 的描述。
- **治理同步**：`core.verification.self_check` 不再要求已按迁移表删除的根 stub；`tests/core/test_doc_governance.py` 与 `tests/core/test_planmd_governance.py` 改为检查当前事实源路径。
- **验证**：`scripts/run_doc_governance_audit.py --fail-on-findings` pass；相关回归 `tests.core.test_doc_governance tests.core.test_planmd_governance tests.core.test_self_check tests.core.test_core_restructure` 48 OK；`scripts/self_check.py` pass；`git diff --check` 仅 Windows 换行提示。
- **边界**：本轮不连接 AutoCAD、不写 / 保存 DWG、不删除 CAD 实体、不改正式图层、不提升表 C；没有清理 `output/validation_runs/**`、训练事实源、系统资产 registry、Agent memory 或 Prompt addendum。

### MODEL-AGENT-RUNTIME-TOOL-CONTRACT-REACT-P10-01：Stage 4 受控 CAD 工具收束
- **触发**：用户要求把 `docs/architecture/model-agent-runtime-dispatch-plan.md` 剩余部分一口气执行完，自行校验，确认执行完成后删除该专项 MD，并把记录同步回主 PlanMD 与规则 / 架构文档。
- **实现**：`core.orchestrator.tool_contract` 新增 Stage 4 controlled-CAD 工具 `preview_cad_execute` / `execute_cad_plan_preview`。受控执行必须先看到同一 CAD_PLAN 的 `validate_plan` 与 `dry_run_plan` pass 报告，只允许 preview-only 写 `CODEX_PREVIEW`，写出 `cad_reports/execution_summary.json`、`cad_reports/readback_summary.json` 和 `cad_reports/cad_preview_tool_report.json`，保持 `savedCurrentDwg=false`；fake-driver preflight 只证明编排并标 `cadGeometryVerified=false`，真实 AutoCAD / COM / handle readback 不可用时 trace 只能 blocked / not_verified。
- **文档收束**：删除 `docs/architecture/model-agent-runtime-dispatch-plan.md`，将模型型 Agent runtime / Tool Contract ReAct 的当前口径同步到 `CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/governance/cad-agent-rules.md`、`docs/architecture/cad-agent-task-chain.md`、`docs/architecture/README.md`、`docs/planning/README.md`、`agents/pipeline/README.md` 和 `docs/status/current.md`。
- **边界**：本包不保存当前 DWG、不改正式图层、不删除实体、不提升表 C；截图仍是 `visual_aid_only`，不能替代 created handles readback、closeout gate 或用户验收。
- **验证**：新增 / 更新 `tests.core.test_tool_contract_react` 覆盖缺 Stage 3 报告阻断、fake-driver no-CAD 预检边界和正式图层阻断；本轮最终验证命令和结果见交付回复。

### MODEL-AGENT-RUNTIME-DISPATCH-CLOSEOUT-DOC-SYNC-01：P9 后架构收束与主文档同步
- **触发**：用户要求到 P9 为止做收束校验，把 `docs/architecture/model-agent-runtime-dispatch-plan.md` 未完成内容再次整合精简，并写入主 PlanMD 与规则 / 架构文档。
- **实现**：将 `model-agent-runtime-dispatch-plan.md` 从施工型长计划压缩为模型型 Agent runtime / Tool Contract ReAct 架构快照：P0-P9 统一标记为已落地 Core 入口，P10 Stage 4 受控 CAD 工具保留为下一步且未开始。同步更新 `CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/governance/cad-agent-rules.md`、`docs/architecture/cad-agent-task-chain.md`、`docs/architecture/README.md`、`docs/status/current.md` 和 `agents/pipeline/README.md` 的系统架构口径。
- **边界**：本包只做文档 / 架构同步和 no-CAD 收束校验；不连接 AutoCAD、不写 / 保存 DWG、不删除实体、不改正式图层、不提升表 C。Stage 3 验证 pass 仍不能替代 CAD write、created handles readback、用户验收或表 C。
- **验证**：本轮收束校验命令和结果见交付回复。

### MODEL-AGENT-TOOL-CONTRACT-REACT-P9-01：确定性验证工具接入
- **触发**：继续执行 `docs/architecture/model-agent-runtime-dispatch-plan.md`，在 P8 Stage 1/2 工具执行后推进 P9。
- **实现**：`core.orchestrator.tool_contract.run_tool_intent()` 新增 Stage 3 deterministic verify tools。`validate_plan` 写 `cad_reports/validation_report.json`，`dry_run` / `dry_run_plan` 写 `cad_reports/dry_run_report.json`，`preview_only_audit` 写 `cad_reports/preview_only_audit.json`，`closeout_gate` 调用现有 closeout gate 写 `closeout_decision.json`。
- **链路**：no-CAD model chain 会执行允许的 `permissionClass=deterministic_verify` 工具请求，并把 tool trace 的 `resultStatus`、`reportPath` 和摘要写入下游 `evidenceBundle.upstreamOutputs`，供后续 audit / delivery 输出读取。模型型 Agent 只能请求验证，不能决定 pass/fail；工具返回 fail 或 `needs_more_evidence` 时 trace 和链路进入 blocked。
- **边界**：本包仍不连接 AutoCAD、不写 / 保存 DWG、不删除实体、不改正式图层、不提升表 C。Stage 3 pass 只证明确定性 JSON gate 通过，不证明 CAD geometry、created handles readback、截图视觉验收、用户接受或系统资产复用 verified。
- **验证**：新增 / 更新 `tests.core.test_tool_contract_react` 与 `tests.core.test_model_agent_chain_runtime` 覆盖 validate pass/fail、dry-run 状态归一、preview-only audit fail、closeout evidence missing blocked、以及 candidate CAD_PLAN -> validate_plan -> evidenceBundle 传递；本轮验证命令和结果见交付回复。

### MODEL-AGENT-TOOL-CONTRACT-REACT-P8-01：只读工具与安全生成工具接入
- **触发**：继续执行 `docs/architecture/model-agent-runtime-dispatch-plan.md`，在 P7 tool intent / trace contract 后推进 P8。
- **实现**：`core.orchestrator.tool_contract` 新增 `run_tool_intent()`。Stage 1 allowlisted read-only tools 支持读取 run package、rule context、schema、上游 agent output 和 trace summary；Stage 2 safe generation tools 只写当前 run 的 `candidate_outputs/`，用于候选 `agent_outputs`、draft intent、CAD_PLAN candidate 和 learningCandidate。
- **链路**：`run_no_cad_model_agent_chain()` 现在会执行允许的 Stage 1/2 `toolIntent`，写 `tool_traces/<agent>.<intent>.json`，并把 tool trace 路径/摘要/hash 放入后续 Agent 的 upstream evidence refs。provider unavailable 时保持 deterministic blocked，不生成伪造 tool trace 或 candidate output。
- **边界**：本包仍不连接 AutoCAD、不写 / 保存 DWG、不删除实体、不改正式图层、不运行 validate / dry-run、不提升表 C；Stage 2 候选输出不改 registry、training source 或系统资产 verified 状态。P9 才接入确定性验证工具，P10 才试点受控 CAD 工具。
- **验证**：新增 / 更新 `tests.core.test_tool_contract_react` 与 `tests.core.test_model_agent_chain_runtime` 覆盖 Stage 1、Stage 2、trace 传递和 provider unavailable 边界；本轮验证命令和结果见交付回复。

### MODEL-AGENT-TOOL-CONTRACT-REACT-P7-01：Tool Contract ReAct schema 与执行前门禁
- **触发**：用户要求按 `docs/architecture/model-agent-runtime-dispatch-plan.md` 一步一步执行，并先执行当前应做的第一步；P0-P6 已有落地状态，因此本轮执行 P7。
- **实现**：新增 `core.orchestrator.tool_contract`，定义模型型 Agent 的 `toolIntent` 执行前门禁；新增 `core/schemas/tool_intent.schema.json` 与 `core/schemas/tool_trace.schema.json`，并登记到 schema registry。模型型输出 schema 增加可选 `toolIntent`，no-CAD model chain 会把 intent 写成 `tool_traces/<agent>.<intent>.json`，下游可读但不代表工具已执行。
- **门禁**：allowlisted read-only 工具可返回 `allowed_not_executed`；高风险工具缺 `targetScope`、模型直接请求保存当前 DWG、删除实体或修改正式图层会在执行前 `blocked`；其它非只读 intent 默认 `needs_more_evidence`，等待 P8-P10 明确工具合同。
- **验证**：新增 `tests.core.test_tool_contract_react` 和运行时 trace 覆盖；本轮验证命令和结果见交付回复。
- **边界**：本包不连接 AutoCAD、不写 / 保存 DWG、不删除实体、不改正式图层、不提升表 C；只是把模型“请求工具”和 Orchestrator “是否允许/阻断/待证据”分离并可追溯。

### MODEL-AGENT-RUNTIME-DISPATCH-IMPLEMENTATION-01：规则上下文包与 no-CAD 多 Agent 活体链路
- **触发**：用户要求一口气执行 `model-agent-runtime-dispatch-plan.md`，把模型型多 Agent 真实调用体系从专项计划推进到可测试 Core 入口。
- **实现**：新增 `core.orchestrator.rule_context_pack`，生成 `rule-context-pack/v1`，覆盖 L0/L1/L2/L3 本地规则检索、`sourceRefs`、`ruleDigest`、`hardGates`、`forbiddenActions`、`missingContext`、`contextBudget` 和派生快照排除。Orchestrator Host 现在写 `rule_context_pack.json` 与 `model_trigger_decision.json`，并把二者放入模型 payload；普通状态 / 进度查询即使模型开关打开也不调模型。
- **链路**：新增 `core.orchestrator.model_agent_chain_runtime.run_no_cad_model_agent_chain()`，串起 `pipeline_orchestrator -> pipeline_design_director -> pipeline_style_generator -> pipeline_design_reviewer -> pipeline_intent -> pipeline_audit -> pipeline_delivery.chain`。下游 payload / prompt 带上游 `agent_outputs/*.json` 路径、摘要和 hash；全链固定 `cadExecutionAuthorized=false`、`savedCurrentDwg=false`。
- **learning / closeout 边界**：no-CAD 链路会对每个模型输出补 `learningCandidate` 或 `not_required`；provider unavailable、schema invalid 或 gate blocked 时进入 `review_required`，但只作为候选，不静默改规则、checker 或训练事实源。
- **验证**：新增红灯测试后实现并转绿：`tests.core.test_rule_context_pack`、`tests.core.test_model_agent_chain_runtime`、`tests.core.test_orchestrator_host_runtime`。相邻模型运行时回归 `tests.core.test_rule_context_pack tests.core.test_model_agent_chain_runtime tests.core.test_model_prompt_library tests.core.test_model_review tests.core.test_orchestrator_host_runtime tests.core.test_a_to_a_task_contract tests.core.test_workflow_dispatch tests.core.test_run_package_state tests.core.test_closeout_gate tests.core.test_reviewer_host_runtime tests.core.test_training_learning_promotion tests.core.test_training_workbench_sync tests.core.test_workbench_trace_viewer` 为 111 OK；`scripts/run_a_to_a_orchestration_gate_check.py` pass；`compileall core/orchestrator core/model_review ...` OK；`scripts/run_doc_governance_audit.py` 仍返回 6 条既有 active doc size findings。
- **边界**：本包未连接 AutoCAD、未写 / 保存 DWG、不提升表 C；模型链只生成 CAD 写入前的上游设计 / intent / audit 证据，真实 CAD 仍需 validate -> dry-run -> `CODEX_PREVIEW` -> created handles readback -> screenshot visual aid -> closeout。

### MODEL-RUNTIME-SPECIAL-PLAN-02：模型型多 Agent 调用体系专项计划抽离
- **触发**：用户要求把主 PlanMD 中关于模型型 Agent 真实调用、上下文控制、规则熟悉度、RAG / IG 检索和调度体系的内容先挪成专门 MD，便于人工润色后再回写主计划。
- **实现**：新增 `docs/architecture/model-agent-runtime-dispatch-plan.md`，把 `rule_context_pack`、规则事实源层级、本地规则检索 / IG、模型触发策略、`model_dispatch_runner`、首条 no-CAD 多 Agent 链、P0-P6 实施计划、硬门禁和用户手改后的回写协议集中到专项文档。
- **主计划收束**：`CORE_RESTRUCTURE_PLAN.md` 的 §0.1 收缩为入口引用，只保留当前 next 和关键边界；避免模型 runtime 细节继续挤在唯一 PlanMD 里，也避免形成第二套主计划。
- **入口同步**：更新 `docs/architecture/README.md`、`docs/planning/README.md` 和 `CORE_CONTEXT_BRIEF.md`，让后续接手优先读专项文档，再回到主 PlanMD。
- **边界**：本轮只做文档抽离和计划润色；未真实调用 `gpt-5.5`，未连接 AutoCAD，未写 / 保存 DWG，不提升表 C。

### MODEL-DISPATCH-RUNNER-FUTURE-PLAN-01：5.5 多 Agent 活体协作改造计划收束
- **触发**：用户根据截图要求继续整理未来改造计划，重点从“规则 / 合同已搭好”推进到“关键 Agent 真实调用 5.5 思考并上下游互读”。
- **计划收束**：`CORE_RESTRUCTURE_PLAN.md` 将下一步明确为“模型调用版 dispatch runner / GPT-5.5 多 Agent 活体协作 MVP”，并拆为 P0 runner、P1 第一条 no-CAD 链路、P2 触发路由、P3 closeout / learning、P4 CAD 前置集成。
- **架构同步**：`agents/pipeline/README.md` 新增模型调用触发策略和 Dispatch Runner MVP；`docs/architecture/cad-agent-task-chain.md` 补充触发条件、`--invoke-model` runner、`modelProviderStatus=unavailable` 和不能伪装模型思考的边界。
- **边界**：本轮是未来计划和架构文档收束；未真实调用 `gpt-5.5`，未连接 AutoCAD，未写 / 保存 DWG，不提升表 C。

### MAIN-ARCH-DOC-CONSOLIDATION-01：主架构文档与根目录入口收束
- **触发**：用户要求在系统升级到主 Agent / 多 Agent 真实调动方向后，扫一遍代码和文档，把 README、规则文档和无关紧要 Markdown 入口整理清楚，并列出后续加固方向。
- **实现**：更新 `README.md`、`docs/architecture/README.md`、`docs/architecture/cad-agent-task-chain.md`、`agents/pipeline/README.md`、`docs/governance/cad-agent-rules.md`、`CORE_CONTEXT_BRIEF.md` 和 `docs/README.md`，把主链路统一为“白话 -> request context / run package -> semantic route -> Orchestrator Host / A-to-A contract -> required agents + hard gates -> 结构化执行路径 -> verification / closeout -> Reviewer Host -> promotion / sync”。同步把 Prompt Pack ready 数量统一为 9 个，并明确多 Agent 活体协作必须证明下游读取上游 `agent_outputs/*.json`。
- **文档清理**：删除 10 个根目录旧 Stub 入口：`当前状态入口.md`、`变更记录入口.md`、`问题风险入口.md`、`长期规则入口.md`、`路线图入口.md`、`训练错误记录入口.md`、`视觉优先训练计划入口.md`、`CAD自动验证入口.md`、`CAD符号语法入口.md`、`CAD卡壳排障入口.md`；对应入口合并到根 `README.md` 和 `docs/README.md`。
- **治理同步**：更新 `core.maintenance.doc_governance` 和 `tests/core/test_doc_governance.py`，让审计规则接受“已在 `docs/README.md` 记录迁移对照的 Stub 删除”，并把架构 hardening 检查从旧单行链路升级到 run package / Orchestrator / Reviewer 链路。
- **验证**：`tests.core.test_doc_governance` 4 个针对性测试通过；`tests.core.test_doc_governance.DocGovernanceTests.test_cli_emits_aggregate_report` 通过；`scripts/run_doc_governance_audit.py` 返回 0，root Stub、architecture hardening、links、source_of_truth、table_c、handoff、training_context、output_policy、openspec_contracts、data_bloat_governance 均 pass。剩余 6 条为既有 active doc size 预算提醒。
- **边界**：本轮是文档治理和架构口径收束，不连接 AutoCAD、不写 / 保存 DWG、不提升表 C；代码层发现的运行包 trace viewer 状态文件口径等问题列入后续加固，而不是在本包静默扩大范围。

### DESIGN-SEMANTIC-DECOMPOSITION-SMARTER-02：语义合同二次智能加固
- **触发**：用户要求再次加固上一轮逻辑，让系统不要只做到“不是死命令”，还要更智能地区分问题、分析、执行、候选数量和否定语义。
- **实现**：`semanticDecomposition` 新增 `semantic_question`、`semantic_analysis_only`、`requestedCandidateCount`、`candidateLabelPolicy`、`countSignalTerms`、`creativityPolicy` 和 `confidence`。语义问题和规则提醒不触发执行型设计 Agent；只分析语义且明确不要落图 / 不生成方案时保持 ordinary orchestration；两个方案会提取为 `requestedCandidateCount=2`，不被改成 A/B/C；否定创造性时输出 `creativityPolicy=suppressed_by_user`。
- **模型输出 gate**：`style_generation_review.schema.json`、`_design_agent_failures()` 和 Prompt / Agent JSON 同步要求 style generator 回填 `candidateCountPolicy`、`requestedCandidateCount`、`candidateLabelPolicy`、`creativityPolicy`、`semanticRoutingConfidence`，让模型不能只给候选而不说明数量与语义来源。
- **验证**：红测先失败于旧逻辑误触发、无法识别只分析、无法提取两个方案和创造性否定；实现后 `tests.core.test_a_to_a_task_contract` -> 21 OK，`tests.core.test_a_to_a_task_contract tests.core.test_model_prompt_library` -> 27 OK，相邻回归 45 OK，`scripts/run_a_to_a_orchestration_gate_check.py` pass，`compileall core/orchestrator core/model_review core/training scripts/run_a_to_a_orchestration_gate_check.py scripts/build_capability_map_data.py` OK，`scripts/sync_training_workbench.py --skip-coverage` pass / Agent check 50/50。
- **边界**：本包只改语义合同、Prompt/schema gate 和派生快照；未连接 AutoCAD、未写 / 保存 DWG、不提升表 C。

### DESIGN-SEMANTIC-DECOMPOSITION-CONTEXTUAL-01：A-to-A 语义信号上下文化
- **触发**：用户提醒“新样式、创造性表达、A/B/C、发后选”不能被当作死命令；平常在对话框 / CLI 层发指令时，系统应先做语义拆解，再决定是否触发设计 Agent、是否生成多候选、是否请用户选择。
- **实现**：`core.orchestrator.a_to_a_task_contract` 新增 `semanticDecomposition`，输出 `requestMode`、软 / 硬语义信号和 `designRouting`。规则提醒类消息进入 `ordinary_orchestration`；明确多方案 / 候选比较 / 请用户选择才进入 `style_candidate_generation`；单方案或用户说“不用多方案 / 不用 A/B/C”时进入 `design_stage`，默认只要求 `pipeline_design_director`。
- **样式合同**：`style_generation_review.schema.json` 增加 `styleDecision=waived|single|multiple` 和 `styleWaiverReason`，允许 style generator 明确不生成候选、生成单方案或生成 2-3 套候选。同步 `pipeline_style_generator` prompt / boundary / negative examples、Agent JSON、pipeline manifest、工作台生成源和 `agents/COMMON_PROMPT_CONTRACT.md`。
- **验证**：先写红测确认旧逻辑把“不要当做死命令”的提醒误判为 `style_candidate_generation`，并强制 `styleCandidates` 2-3 个；实现后 `tests.core.test_a_to_a_task_contract tests.core.test_model_prompt_library` -> 23 OK，相邻回归 41 OK，`scripts/run_a_to_a_orchestration_gate_check.py` pass，`compileall core/orchestrator core/model_review core/training scripts/run_a_to_a_orchestration_gate_check.py scripts/build_capability_map_data.py` OK，`scripts/sync_training_workbench.py --skip-coverage` pass / Agent check 50/50。
- **边界**：本包只改语义合同、Prompt 合同和派生快照；未连接 AutoCAD、未写 / 保存 DWG、不提升表 C。

### DESIGN-STYLE-PROMPT-PACK-ABC-TRAINING-01：设计三 Agent Prompt Pack 与 A/B/C 样式候选训练
- **触发**：用户要求继续优化：把 `design_director` / `style_generator` / `design_reviewer` 从 `plannedPacks` 升级为真实 Prompt Pack；A-to-A contract 自动识别设计 / 样式语义；给 `style_candidates.json` 定 schema 并由 CAD 执行器消费；跑一个不复刻旧样式的新场景 A/B/C 尺寸样式训练案例。
- **实现**：新增三套 Prompt Pack 和 strict schema：`pipeline_design_director`、`pipeline_style_generator`、`pipeline_design_reviewer`；更新 prompt manifest、Agent JSON 与 pipeline manifest。`a_to_a_task_contract` 新增 `design_stage`、`style_candidate_generation`、`design_review` 三类 task kind 和 `design_intelligence` hard gate，遇到“新样式 / 创造性表达 / 方案候选 / A/B/C / 尺寸样式”等语义会要求三位设计 Agent 输出并阻断缺字段输出。
- **样式候选执行**：新增 `core/schemas/style_candidates.schema.json` 与 `core.execution.style_candidate_execute`，执行器会验证 `style_candidates.json`，把每个候选转为只写 `CODEX_PREVIEW` 的 `CAD_PLAN`，再调用现有执行链路生成 execution summary。新增 `core.training.style_candidate_training` 和 `scripts/run_style_candidate_training.py`，生成“小户型玄关鞋柜”A/B/C 三套尺寸样式候选，并检查未复用旧 10 个尺寸样式。
- **训练证据**：fake-CAD 训练输出位于 `output/training_queues/style-candidate-abc-new-scene/`，结果为 `status=needs_user_choice`、`styleCandidateIds=["A","B","C"]`、`readbackStatus=pass`、`designReviewStatus=pass`、`savedCurrentDwg=false`，请用户后续从 A/B/C 中选择或混合方向。
- **验证**：`scripts/run_a_to_a_orchestration_gate_check.py` pass；相邻单测 `tests.core.test_model_prompt_library tests.core.test_a_to_a_task_contract tests.core.test_style_candidates_execution tests.core.test_style_candidate_training tests.core.test_orchestrator_host_runtime tests.core.test_workflow_dispatch` -> 38 OK；`compileall core/model_review core/orchestrator core/execution core/training scripts/run_style_candidate_training.py` OK；`scripts/run_style_candidate_training.py --fake-cad --summary-only` pass。
- **边界**：真实 CAD replay 当前为 `external_blocker/cad_connection_failed`：本机能看到 `acad` 进程，但 `GetActiveObject` 取不到活动 `AutoCAD.Application`；未保存当前业务 DWG、不改正式图层、不提升表 C。fake-CAD 只能证明 contract / executor / training loop，不证明真实 CAD 几何。

### OBJECT-FAMILY-SOFA-REPLAY-RCAD-01：sofa 对象族真实 CAD replay 能力证明
- **触发**：主计划 §0.1 在小型 RAG、sofa no-CAD trial 和自动晋升候选之后，要求至少为对象族补一次真实 CAD replay：created handles、bbox、图层、readback、截图辅助和 closeout 全链路通过。
- **实现**：新增 `core/assets/object_family_cad_replay.py` 与 `scripts/run_object_family_cad_replay.py`，公开 `run_object_family_cad_replay()`。runner 会复用 `build_object_family_trial()` 的 CAD_PLAN 草案，按 replay base point 平移 glyph primitives，重新 `validate_plan()` / dry-run，再通过 `execute_plan_file(..., preview_only=True, allow_unconfirmed=True)` 只写 `CODEX_PREVIEW`。
- **真实 CAD 证据**：外部 COM 连接当前活动文档 `projects/测试文件.dwg` 后执行 `scripts/run_object_family_cad_replay.py --output-dir output/validation_runs/object-family-sofa-replay-20260605-rcad --base-x 62000 --base-y 36000`，报告 `object_family_cad_replay_report.json` 为 `geometry_verified`：created handles 17 个，readback hit 17 / miss 0，bbox `[62000.0, 36100.0]` 到 `[64200.0, 36900.0]`，type count `line=17`，layer count `CODEX_PREVIEW=17`，`savedCurrentDwg=false`。
- **截图 / closeout**：`scripts/render_preview.py --capture-autocad-window --execution-summary ...` 生成 `output/previews/object-family-sofa-replay-20260605-rcad.png`，截图为 `visual_aid_only`；`scripts/run_visual_cad_review.py` 输出 `visual-review/visual_review_report.json`，status pass；最小 run package `output/runs/object-family-sofa-replay-20260605-rcad-closeout/` 运行 `closeout_gate` 后 `closeout_decision.json` 为 `ready_for_delivery`、`can_deliver=true`。
- **验证**：先写红测确认模块缺失；实现后 `tests.core.test_object_family_cad_replay` 2 OK；相邻回归 `tests.core.test_object_family_cad_replay tests.core.test_object_family_trial tests.core.test_local_asset_rag tests.core.test_asset_promotion_candidates tests.core.test_symbol_glyph_cad_smoke tests.core.test_execute_plan` 24 OK；修复 readback report 契约后 visual review pass。
- **边界**：本包不保存当前 DWG、不改正式图层、不删除实体、不提升表 C。它证明 sofa 对象族 `draw_symbol_glyph` replay，而不是系统资产跨 DWG 复用 verified、precise sourceSpec/reuseReplay、规则 / checker 自动晋升或用户人工验收。

### ASSET-PROMOTION-CANDIDATES-MVP-01：资产智能自动晋升候选
- **触发**：主计划 §0.1 在对象族试点之后要求做自动晋升候选；Agent 只能提出规则 / 检查器 / 资产 / 训练项候选，由 `pipeline_learning_promoter` 审核写入，不能静默修改长期事实源。
- **实现**：新增 `core/assets/promotion_candidates.py`，公开 `build_asset_intelligence_promotion_candidates()`。它从 ready 的 sofa object-family trial 生成 task rule、checker、asset candidate、training item 四类候选，并附 promotion gate / review payload。
- **审查边界**：输出固定 `review.requiredAgentId=pipeline_learning_promoter`、`mutatedTargets=[]`。`updateTaskRules`、`updateChecker`、`updateAgentCalibration` 是 `needs_reviewed_package`；`updateTrainingSource=not_required`，因为 no-CAD 试点不是正式训练验收报告。asset candidate 在 precise sourceSpec、real CAD replay 和 reuse probe / replay 前不能晋升为 verified。
- **验证**：先写红测确认模块缺失；实现后 `tests.core.test_asset_promotion_candidates` 2 OK；相邻回归 `tests.core.test_asset_promotion_candidates tests.core.test_object_family_trial tests.core.test_local_asset_rag tests.core.test_training_learning_promotion tests.core.test_plan_engine` 26 OK；真实仓库函数链返回 `review_required 4 [] needs_reviewed_package`。
- **边界**：本包未连接 AutoCAD、未写 / 保存 DWG、不提升表 C。主计划下一步转入真实 CAD replay 能力证明。

### OBJECT-FAMILY-SOFA-TRIAL-MVP-01：sofa 对象族 no-CAD 试点
- **触发**：主计划 §0.1 在小型 RAG 之后要求选一个对象族试点，优先 sofa 或 dimension style，跑通检索 -> 设计候选 -> `CAD_PLAN` -> 执行计划 -> readback 证据口径。
- **实现**：新增 `core/assets/object_family_trial.py`，公开 `build_object_family_trial()`。当前 MVP 只支持 sofa；非 sofa 请求返回 `unsupported_object_family`，避免试点未审查就泛化。sofa 试点会调用 `build_local_asset_rag_pack()`，生成 3 个设计候选，选择 component-readable 的 `draw_symbol_glyph` 草案，并用现有 `validate_plan()` / `create_dry_run_report()` 验证草案。
- **CAD_PLAN 草案**：输出 `intent=draw_symbol_glyph`、`object.type=symbol_glyph`、`drawing.layer=CODEX_PREVIEW`、`needs_confirmation=true`，用 back / seat / arm_left / arm_right / seat_division 五个 primitive 表达沙发构件。
- **执行 / readback 口径**：`executionPlan.cadWritePolicy=not_executed_no_cad`；后续真实 CAD replay 才能检查 created handles、bbox、layer、entity types、readback entity count 和 `savedCurrentDwg=false`。dry-run 只证明计划可校验，不证明几何准确。
- **验证**：先写红测确认模块缺失；实现后 `tests.core.test_object_family_trial` 2 OK；相邻回归 `tests.core.test_object_family_trial tests.core.test_local_asset_rag tests.core.test_plan_engine tests.core.test_semantic_asset_rules tests.core.test_system_asset_reuse` 32 OK；真实仓库调用返回 `cad_plan_draft_ready 3 valid not_executed_no_cad`。
- **边界**：本包未连接 AutoCAD、未写 / 保存 DWG、不提升表 C。主计划下一步转入自动晋升候选；真实 CAD 能力证明仍需另包 replay。

### ASSET-LOCAL-RAG-MVP-01：资产智能小型本地 RAG
- **触发**：`CORE_RESTRUCTURE_PLAN.md` §0.1 要求资产智能后四项按轻量顺序推进，第一步是小型 RAG，只检索系统资产、规则、训练记忆和失败样本，不铺大知识库。
- **实现**：新增 `core/assets/local_rag.py`，公开 `build_local_asset_rag_pack()` / `write_local_asset_rag_pack()`。输出 `local_asset_small_rag_pack`，包含 `sourcePolicy`、`scannedSources`、`sourceSummary`、`encodingPreflight`、分 source kind 的引用条目、matched terms、snippet 和 evidence boundary。
- **来源边界**：允许来源固定为 `system_asset`、`semantic_rule`、`training_memory`、`failure_sample`；显式排除 `reference_asset`、外网、raw download 和 embedding index。该包只做 lexical local context，不证明真实 CAD 几何、created handles、用户视觉验收、模型判断质量或资产 verified 晋升。
- **验证**：先写红测确认模块缺失；实现后 `tests.core.test_local_asset_rag` 2 OK，相邻回归 `tests.core.test_local_asset_rag tests.core.test_semantic_asset_rules tests.core.test_system_asset_reuse tests.core.test_training_learning_promotion` 30 OK。
- **边界**：本包未连接 AutoCAD、未写 / 保存 DWG、不提升表 C。主计划下一步转入 sofa 或 dimension style 对象族试点。

### DESIGN-STAGE-MODEL-BRIDGE-CLOSEOUT-01：设计阶段 5.5 模型桥补齐
- **触发**：用户补充图片指出，上一波 5.5 扩展更多覆盖执行、回读、审计、资产沉淀和交付复核，但真正弱点在 CAD_PLAN 之前的设计判断、样式生成和设计复核；主 Agent 应模拟专业设计师，先构思并分发，而不是只做任务路由。
- **实现**：新增 `pipeline_design_director`、`pipeline_style_generator`、`pipeline_design_reviewer` 三个 Agent 合同，分别负责图纸类型 / 表达目的 / 设计意图 / 约束判断、2-3 套参数化样式候选生成、CAD readback 后的专业设计复核。`CORE_RESTRUCTURE_PLAN.md` 与 `agents/pipeline/pipeline_manifest.json` 已记录“设计智能链路”，把 `brief -> design_director -> style_generator -> visual_intent / intent -> execute -> readback / audit -> design_reviewer -> learning_promoter` 固定为创造性样式任务的默认闭环。
- **机器登记**：`agents/pipeline/pipeline_manifest.json` 新增 `design_intelligence` hard gate、三类设计 task kind、设计 Agent artifacts 和 forbidden patterns；`core/model_review/prompt_packs/manifest.json` 新增三个 planned Prompt Pack；`scripts/build_capability_map_data.py` 新增三张工作台 Agent / Prompt 卡片、设计失败模式归因，并把 `cad_designer` callable list 接到设计链。
- **Prompt / 规则同步**：`core/training/learning_promotion.py` 和生成结果 `agents/COMMON_PROMPT_CONTRACT.md` 新增“设计智能与创造性样式规则”；同步 `AGENTS.md`、`CORE_RESTRUCTURE_PLAN.md`、`agents/pipeline/README.md`、`docs/governance/cad-agent-rules.md` 和 `docs/status/current.md`。
- **验证**：`scripts/sync_training_workbench.py --skip-coverage` pass，Agent check 50/50 pass，工作台现在为 `agentProfiles=28`、`promptContracts=28`；后续验证还包括 JSON 加载、A-to-A 门禁、Prompt / workbench 回归和 diff check。
- **边界**：本包只补规则、合同、生成源和计划；未真实调用 `gpt-5.5` provider，未连接 AutoCAD，未写 / 保存 DWG，不提升表 C。设计模型输出仍只读，不能替代 CAD validate / dry-run / readback、用户验收或资产 verified 晋升。

### MODEL-5-5-AGENT-EXPANSION-RULES-01：5.5 模型桥扩大判断节点与自动成长规则
- **触发**：用户明确表示不在意额度，不需要复杂额度控制，希望系统以理想化准确性为目标扩大 `gpt-5.5` 模型桥使用，并要求所有使用模型桥的 Agent 能持续记录错误、总结正确经验、自动成长。
- **实现**：5.5 扩展顺序、全部 pipeline Agent / 主训练 Agent / 场景插件的模型判断场景、初步 Prompt 规范和验证口径已收口到 `CORE_RESTRUCTURE_PLAN.md` 与 `agents/pipeline/pipeline_manifest.json`；`agents/pipeline/pipeline_manifest.json` 新增 `model_bridge_expansion` 机器登记，记录 `defaultModel=gpt-5.5`、`accuracy_first_no_quota_partition`、自动成长合同、19 个 pipeline Agent 的 `agentJudgmentNodes`、场景训练节点和新增模型 review artifact 名称；`core/model_review/prompt_packs/manifest.json` 新增 `plannedPacks`，为后续逐个补 Prompt Pack 保留队列。
- **Prompt 合同**：更新 `core/training/learning_promotion.py` 的共享 Prompt 生成源，并通过工作台同步刷新 `agents/COMMON_PROMPT_CONTRACT.md`。新规则要求模型桥 Agent 输出 `learningCandidate` / `not_required`，记录 `errorPattern`、`correctPattern`、`promptDelta`、`checkerDelta`、`retestOriginalTask` 和 `responsibleAgentIds`，由 `pipeline_learning_promoter` 写回 Agent memory / prompt addendum。
- **同步范围**：同步 `AGENTS.md`、`CORE_RESTRUCTURE_PLAN.md`、`agents/pipeline/README.md` 与 `docs/governance/cad-agent-rules.md`，明确模型桥只读、不能执行 CAD、不能保存 / 删除 / 改正式图层、不能替代 CAD readback / sourceSpec / reuseReplay / 表 C / 用户验收。
- **验证**：`scripts/sync_training_workbench.py --skip-coverage` -> pass，Agent check 50/50 pass；`agents/COMMON_PROMPT_CONTRACT.md` 已由生成源刷新，包含 `CORE_RESTRUCTURE_PLAN.md`、`learningCandidate` 和自动升级条款。
- **边界**：本轮只写规则、Prompt 规范和机器登记；未真实调用 `gpt-5.5` provider，未连接 AutoCAD，未写 / 保存 DWG，不提升表 C；P1/P2/P3 planned Prompt Pack 后续仍需逐个实现 schema / prompt / converter / trace / test。

### TRAINING-EVIDENCE-GITIGNORE-PORTABILITY-01：训练证据 Git 迁移放行
- **触发**：用户准备下次直接用另一台电脑的仓库覆盖本机，并担心 `.gitignore` 导致训练文件没有随 Git / 仓库迁移，进而让工作台误以为需要重训。
- **实现**：`.gitignore` 从只放行少量训练报告，改为默认放行可迁移证据目录：`output/training_queues/**`、`output/training_learning/**`、`output/validation_runs/**`、`output/previews/**`、`output/runs/**` 和 `output/model_reviews/**`。仍忽略 `output/debug/`、`output/test_artifacts/`、`.env`、虚拟环境、Python 缓存、日志和 CAD 锁文件。
- **边界**：私人仓库可以保留完整训练证据，但仍不建议删除 `.gitignore`；本机缓存、密钥、虚拟环境和锁文件不应进入迁移事实源。
- **验证**：`git check-ignore` 确认训练 / learning / validation / preview / run package / model trace 路径未被忽略，debug / test artifacts / env / venv / pycache / dwl 仍被忽略。

## 2026-06-04

### WORKBENCH-TRAINING-EVIDENCE-PORTABILITY-01：工作台跨电脑训练证据口径
- **触发**：用户看到训练工作台显示 `217` 个训练计划、`0` 个已结束训练，询问是否因为换电脑缓存丢失而必须重训。
- **实现**：`scripts/build_capability_map_data.py` 新增 `trainingSourceSummary`，统计 active / archived 训练事实源、本机验收通过项、archived 验收报告和建议恢复路径；`capability-map.html` 顶部同步栏新增“训练证据同步”，明确训练状态不是浏览器缓存，换电脑后应优先同步旧电脑的 `output/training_queues/**`、`output/training_learning/**`、Agent memory / Prompt addendum 和 `docs/training/training-sources.json`。
- **当前判断**：本机 `localAcceptedTrainingProgramCount=0`、active 训练验收报告 0、archived 训练验收报告 4、缺失 active fact source 0；因此不应直接判定“需要全部重训”，而应先恢复另一台电脑的训练证据。只有找不回 created handles/readback/验收报告时，才重跑对应训练项。
- **验证**：新增红测后 `tests.core.test_training_workbench_sync` -> 19 OK；`sync_training_workbench.py --skip-coverage` -> pass，Agent check 50/50 pass；`node --check capability-map-data.js` -> OK。
- **边界**：本包只同步工作台页面口径和派生快照；未连接 AutoCAD、未写 / 保存 DWG、不提升表 C。

### REVIEWER-HOST-CLOSEOUT-RUNTIME-01：Reviewer Host 交付收口运行时
- **触发**：用户要求把临时文档里除真实 CAD 人工校验以外的内容全部实施并优化，然后删除临时 MD。
- **实现**：新增 / 收口 `core.orchestrator.reviewer_host_runtime`，读取 run package 的 `closeout_decision.json`、CAD reports、visual acceptance 和状态文件，写出 `agent_outputs/pipeline_delivery.json`、`final_report.md` 与 `reviewer_host_closeout_result.json`。
- **门禁**：缺 `created_handles_readback`、`savedCurrentDwg=false`、`targetLayer=CODEX_PREVIEW`、visual acceptance 或邻区保护时，交付口径固定为 `not_verified`，`finalResponseAllowedClaims=[]`，run state 推进到 `blocked`；截图只作为视觉辅助。
- **验证**：先写红测确认模块缺失；实现后 `python -m unittest tests.core.test_reviewer_host_runtime` -> 3 OK。
- **边界**：本包未连接 AutoCAD、未写 / 保存 DWG、未删除实体、未真实调用模型 provider、不提升表 C。

### WORKBENCH-TRACE-VIEWER-01：工作台模型 Trace 派生视图
- **触发**：临时计划要求训练工作台能查看模型型 Agent 调用、gate 决策、closeout、delete scope 和 neighbor protection，但不能把 JS 当事实源。
- **实现**：新增 `core.orchestrator.workbench_trace_viewer`，只读扫描 `output/runs/**` 与 `output/model_reviews/traces/**`，生成 `modelTraceViewer` 派生快照；`scripts/build_capability_map_data.py` 接入该字段；`capability-map.html` 新增“模型 Trace”页签；`scripts/run_training_workbench_agent_check.py` 新增派生边界、truth sources 和 HTML 视图检查。
- **验证**：先写红测确认模块缺失；实现后 `python -m unittest tests.core.test_workbench_trace_viewer` -> 2 OK；`scripts/build_capability_map_data.py` 写出快照；`scripts/run_training_workbench_agent_check.py` -> pass，47/47 checks。
- **边界**：`capability-map-data.js` / HTML 只显示派生视图，不证明 Agent 调用真实发生、不证明 CAD 几何、不替代 source JSON、created handles readback、表 C 或用户验收。

### MODEL-BACKED-TEMP-PLAN-CLOSEOUT-01：临时计划卡迁移与删除
- **触发**：除真实 CAD 人工校验以外的临时计划均已实施，需要把长期记录压入主计划、README、状态和交接文档后删除临时 MD。
- **迁移**：`CORE_RESTRUCTURE_PLAN.md` 新增“模型型 Agent Runtime 收口”，保留已落地清单和真实 CAD 人工校验路线；`README.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`docs/planning/任务清单.md`、`agents/pipeline/README.md`、状态页和交接索引同步。
- **删除**：临时 MD 不再作为恢复入口；后续模型型 Agent 方向以 `CORE_RESTRUCTURE_PLAN.md` 与 pipeline README 为准。
- **边界**：真实 CAD 校验方法只是后续人工验收路线；本轮未连接 AutoCAD、未写 / 保存 DWG、未真实调用模型、不提升表 C。

### ORCHESTRATOR-HOST-RUNTIME-01：主编排 Host 运行时

- **触发**：用户要求继续实施临时计划中未执行的下一包，并说明真实 CAD 可在打开后自行校验；本包先落地 no-CAD / no-provider 的主编排 Host runtime。
- **实现**：新增 `core.orchestrator.orchestrator_host_runtime`，读取 `output/runs/<run_id>/user_request.json` 与 `context_pack.json`，结合 `agents/pipeline/pipeline_manifest.json`、Prompt Pack manifest、`build_a_to_a_task_contract()` 和语义资产路由，写出 `dispatch_plan.json`、`task_contract.json`、`required_agents.json`、`risk_assessment.json`。
- **分发规则**：普通可见 CAD 交付自动要求 `pipeline_visual_acceptance_reviewer` / `visual_acceptance_review` / `cad_readback`；删除 / 清理自动要求 `delete_scope_gate` 和 victim set preview；旁边 / 相邻放置自动要求 `neighbor_protection` 和 occupied bbox；系统资产沉淀自动要求 asset governor、librarian、DWG curator、reuse auditor 和 data-bloat gate；未登记 Agent 只能进入 `additionalAgentRequests`，不能进入 effective required agents。
- **模型边界**：默认 `CodexCliReviewConfig(enabled=False)`，`modelInvoked=false`，只生成确定性分发计划；以后显式授权模型调用时，同一入口可调用 `pipeline_orchestrator` Prompt Pack 写 trace，但模型结果仍不能执行 CAD 或替代 readback / closeout。
- **验证**：先写红测确认 `core.orchestrator.orchestrator_host_runtime` 缺失；实现后 `tests.core.test_orchestrator_host_runtime` 6 OK，相邻回归 `tests.core.test_orchestrator_host_runtime tests.core.test_model_prompt_library tests.core.test_model_review tests.core.test_run_package_state tests.core.test_closeout_gate tests.core.test_delete_neighbor_gates tests.core.test_a_to_a_task_contract` 59 OK；`compileall core/orchestrator/orchestrator_host_runtime.py core/orchestrator/__init__.py` OK。
- **边界**：本包未连接 AutoCAD、未写 / 保存 DWG、未删除实体、未真实调用模型 provider、不提升表 C。Reviewer Host closeout runtime 已由后续包补上。

### MODEL-BACKED-TEMP-PLAN-COMPRESSION-02：临时计划卡二次压缩与真实 CAD 校验方法

- **触发**：用户要求继续压缩模型型 Agent 临时计划卡，只留下尚未实施计划，并补充后续用真实 CAD 校验模型型 Agent 链路的方法。
- **压缩**：临时计划卡已移除已完成包表格和长验收快照；该记录写入时剩余三包为 `orchestrator-host-runtime` / `reviewer-host-closeout-runtime` / `workbench-trace-viewer`。当前 `orchestrator-host-runtime` 已由 `ORCHESTRATOR-HOST-RUNTIME-01` 完成，临时卡只剩后两包。
- **真实 CAD 校验方法**：新增环境与编码预检、Prompt Pack no-CAD dry-run、代表性可见 CAD 交付链路、删除 / 局部修复链路、系统资产沉淀 / 复用链路和最终声明口径。默认只写 `CODEX_PREVIEW`，不保存当前业务 DWG，不改正式图层，不把截图或模型 pass 当几何证明。
- **同步**：同步 `README.md`、`agents/pipeline/README.md`、`docs/planning/任务清单.md`、`docs/status/current.md`、`docs/handoffs/current.md`、`docs/handoffs/package-index.md` 和 `CORE_CONTEXT_BRIEF.md`，避免后续接手误以为已完成包仍在待办里。
- **验证**：`git diff --check` exit 0（仅 CRLF warning）；`scripts/run_doc_governance_audit.py` exit 0，status=`findings`，仍为 5 个 active doc size findings，其余 source-of-truth / handoff / links / Table C / OpenSpec / data-bloat governance 检查通过。
- **边界**：本轮只做文档治理；未连接 AutoCAD、未写 / 保存 DWG、未删除实体、未真实调用模型 provider、不提升表 C。

### MODEL-AGENT-PROMPT-LIBRARY-01：模型型 Agent 真实 Prompt Pack 库

- **触发**：用户要求继续下一包，把模型型 Agent 从“角色契约 / 规则门禁”推进到真实 Prompt、边界规定、任务分发字段、状态机口径和可校验输出，重点让主 Agent 与辅助 Agent 的职责真正可调用、可追踪、可阻断。
- **实现**：新增 `core.model_review.prompt_library` 和 `core/model_review/prompt_packs/manifest.json`；落地 6 个 Prompt Pack：`pipeline_visual_acceptance_reviewer`、`pipeline_repair`、`pipeline_asset_governor`、`pipeline_visual_layout_reviewer`、`pipeline_orchestrator`、`pipeline_delivery`。每个包都有 `prompt.md`、`boundary_rules.md`、`negative_examples.md`、`input_schema.json`，并引用 `core/model_review/schemas/*.schema.json` 作为 strict output schema。
- **Prompt 合同**：模型输出统一要求 `statePatch`、`finalResponseAllowedClaims`、`evidenceUsed`、`evidenceMissing`；视觉验收补 `canAskUserToReview` / `lookHereFirst`；修复补 `rootCause`、`repairMode`、`protectedNeighbors`、`requiresUserPermission`、局部修复 / 禁止全量重画说明；资产守门补 `assetLifecycleDecision`、`sourceBoundaryDecision`、`requiredChildAgents`、`nativeVisibleEvidenceRequired`、`reuseProofRequired`。
- **运行入口**：`run_prompt_pack_review()` 通过现有 `run_codex_cli_review()` 写 trace，并把 `prompt_pack_context.json` 写入 `output/runs/<run_id>/model_traces/<agent_id>/<trace_id>/`；视觉验收输出仍写 `agent_outputs/pipeline_visual_acceptance_reviewer.json`，供 closeout gate 读取。`scripts/probe_codex_cli_model_review.py` 新增 `--prompt-pack` / `--agent-id` dry-run 入口，默认不触发真实模型。
- **验证**：先写红灯测试覆盖 manifest、prompt 渲染、repair schema 对齐、fake runner trace/converted output、probe dry-run 和角色专属 schema 字段；实现后 `tests.core.test_model_prompt_library` 6 OK，`tests.core.test_model_review` 20 OK，整体回归 `tests.core.test_model_prompt_library tests.core.test_model_review tests.core.test_run_package_state tests.core.test_closeout_gate tests.core.test_delete_neighbor_gates tests.core.test_a_to_a_task_contract` 53 OK；`compileall core/model_review scripts/probe_codex_cli_model_review.py` OK；synthetic probe 与 `--prompt-pack pipeline_repair` dry-run OK。
- **边界**：本包不连接 AutoCAD、不写 / 保存 DWG、不删除 / 移动实体、不真实调用模型 provider、不提升表 C。Prompt Pack 只提供只读模型复审 / 分发 / 建议合同，不能替代 CAD readback、validate / dry-run、sourceSpec、reuse replay、delete scope、neighbor protection、closeout gate 或用户验收。

### MODEL-BACKED-TEMP-PLAN-COMPRESSION-01：已实施包整体校验与临时计划卡瘦身

- **触发**：前四个模型型 Agent 升级包已落地，需要先做整体回归校验，再把模型型 Agent 临时计划卡从实施流水压缩成控制面，只保留剩余待实施计划。
- **校验**：整体回归 `tests.core.test_model_review tests.core.test_run_package_state tests.core.test_closeout_gate tests.core.test_delete_neighbor_gates tests.core.test_a_to_a_task_contract` 47 OK；`compileall core/model_review core/orchestrator scripts/probe_codex_cli_model_review.py` OK；`scripts/probe_codex_cli_model_review.py` dry-run OK，`wouldInvoke=true`、`modelInvoked=false`。
- **压缩**：临时 MD 现只保留当前结论、整体验收快照、已完成包压缩记录、当前硬边界、剩余待实施计划和推荐下一包；已完成包详情改查 `docs/status/changelog.md`、`docs/status/current.md`、`docs/handoffs/current.md` 和 `docs/handoffs/package-index.md`。
- **剩余计划**：该包压缩时曾推荐 `model-agent-prompt-library`；该推荐已由 `MODEL-AGENT-PROMPT-LIBRARY-01` 完成，后续 `orchestrator-host-runtime`、`reviewer-host-closeout-runtime` 和 `workbench-trace-viewer` 均已补齐。当前只保留真实 CAD / 真实模型链路验收边界。
- **边界**：本轮未连接 AutoCAD、未写入 / 保存 DWG、未删除实体、未真实调用模型 provider、不提升表 C。

### DELETE-SCOPE-NEIGHBOR-PROTECTION-GATE-01：删除范围与邻区保护报告生成器

- **触发**：临时方案推荐顺序第 4 项要求把误删问题前移到执行前阻断，而不是等视觉 reviewer 事后发现；closeout gate 已要求 `neighbor_protection=pass`，删除任务还要求 `delete_scope_gate=pass`。
- **实现**：新增 `core.orchestrator.delete_neighbor_gates`，提供 `build_delete_scope_gate()`、`write_delete_scope_gate()`、`build_neighbor_protection_gate()`、`write_neighbor_protection_gate()`；writer 固定输出 `cad_reports/delete_scope_gate.json` 和 `cad_reports/neighbor_protection.json`，供 run package / closeout gate 读取。
- **门禁**：`delete`、`purge`、`delete_replace`、`cleanup`、`clear_previous` 必须声明 `targetHandles` 或 `scopeBbox`，并提供 victim set preview；目标层必须是 `CODEX_PREVIEW`；`whole_modelspace`、`whole_codex_preview`、`global_preview_bbox`、`all_visible`、`training_panel`、`current_screen` 默认 hard fail，除非用户显式授权且任务本身就是全局清理。
- **邻区保护**：旁边 / adjacent / nearby 放置必须先有 occupied bbox 检查；target bbox 与已占用对象碰撞会 fail；执行后可用 `neighborBefore` / `neighborAfter` 比对邻区 handles 和 bbox，A2 局部修复误删 A1 frame 会被阻断。
- **验证**：先写红测确认模块不存在；实现后 `tests.core.test_delete_neighbor_gates` 7 OK，覆盖无范围 cleanup、全局来源、victim preview、protected zone、occupied bbox、collision、neighbor diff 和 writer；相邻回归 `tests.core.test_delete_neighbor_gates tests.core.test_closeout_gate tests.core.test_run_package_state tests.core.test_model_review tests.core.test_a_to_a_task_contract` 47 OK。
- **边界**：本包不连接 AutoCAD、不写 / 保存 DWG、不删除 / 移动实体、不真实调用模型 provider、不提升表 C；它只生成执行前 / 执行后可审计 JSON 报告，不能替代 CAD readback、视觉验收或用户验收。

### VISUAL-ACCEPTANCE-CLOSEOUT-GATE-01：可见 CAD 交付 closeout 门禁

- **触发**：临时方案推荐顺序第 3 项要求解决“视觉 Agent 存在但没进场”的问题；可见 CAD 交付前必须有独立 closeout 决策，不能由主编排自己给自己放行。
- **实现**：新增 `core.orchestrator.closeout_gate`，提供 `build_closeout_decision()` 与 `run_closeout_gate()`；从 `output/runs/<run_id>/` 读取 `dispatch_plan.json`、`task_contract.json`、`cad_reports/validation_report.json`、`cad_reports/dry_run_report.json`、`cad_reports/readback_summary.json`、`agent_outputs/visual_acceptance_output.json`、`cad_reports/neighbor_protection.json` 和按需的 `delete_scope_gate.json` / `asset_source_boundary.json`。
- **门禁**：只有 `validate_plan=pass`、`dry_run=pass`、`created_handles_readback=ok`、`savedCurrentDwg=false`、`targetLayer=CODEX_PREVIEW`、`visual_acceptance_review=pass`、`neighbor_protection=pass` 及按需 delete / asset gate 全部通过时，才写 `status=ready_for_delivery`、`can_deliver=true`；否则写 `status=not_verified`、阻断原因和建议修复，并推进运行包 `state.json` 到 `blocked`。
- **证据边界**：`screenshots/` 只登记为 `visual_aid_only`，不能替代 created handles readback 或 visual acceptance；`final_response_allowed_claims` 不允许声明用户已验收或几何全图无误。
- **验证**：先写红测确认 `core.orchestrator.closeout_gate` 不存在；实现后 `tests.core.test_closeout_gate` 4 OK，覆盖 pass、缺视觉验收、截图不能替代 readback、删除 / 资产任务缺对应 gate 阻断。
- **边界**：本包不调用真实模型 provider、不连接 AutoCAD、不写 / 保存 DWG、不提升表 C；它是 Reviewer Host runtime 前的确定性 closeout hard gate。

### RUN-PACKAGE-STATE-MACHINE-01：模型型 Agent 运行包状态机

- **触发**：临时方案第 2 包要求每次任务都有独立 `output/runs/<run_id>/` 运行包，不能靠聊天上下文记忆上一轮做过什么。
- **实现**：新增 `core.orchestrator.run_package_state`，提供 `create_run_package()`、`load_run_state()`、`advance_run_state()`；创建时写入 `user_request.json`、`context_pack.json`、`task_contract.json`、`dispatch_plan.json`、`state.json`、`final_report.md` 和 `agent_outputs/`、`cad_reports/`、`screenshots/`、`model_traces/`。
- **状态机**：`state.json` 固定登记 `created`、`context_collected`、`orchestrator_reviewed`、`dispatch_ready`、`cad_executed`、`visual_reviewed`、`repair_needed`、`blocked`、`ready_for_delivery`、`delivered`；每个阶段都有 `inputFiles`、`outputFiles`、`status`、`blockingReason`，中断后可直接从文件恢复。进入 `blocked` 必须写明阻断原因。
- **验证**：先写红测确认模块不存在；实现后 `tests.core.test_run_package_state` 4 OK，覆盖运行包结构、路径收束、阶段 IO、状态恢复、阻断原因和非法阶段拒绝。
- **边界**：本包不调用真实模型 provider、不连接 AutoCAD、不写 / 保存 DWG、不提升表 C；它只提供 Host runtime / closeout gate 后续可复用的文件化事实源。

### MODEL-REVIEW-TRACE-OBSERVABILITY-01：模型复审 Trace 可观测层

- **触发**：临时方案要求先解决模型型 Agent 调用黑箱问题，再继续补 Prompt / Host runtime；用户补充要求 trace 不能只留给人手读，Agent / trace reviewer 也要能自动复盘并给出白话摘要。
- **实现**：`run_codex_cli_review()` 新增 `agent_id`、`task_type`、`trace_id`、`trace_dir` 和输入摘要引用，默认为每次调用写入 `output/model_reviews/traces/<timestamp>_<agentId>_<traceId>/`；trace 包含 `prompt.md`、schema 快照、sanitized `command.json`、stdout/stderr、预留 `events.jsonl`、`last_message.json`、`normalized_output.json`、`gate_decision.json` 和 `trace_manifest.json`。
- **自动复盘**：新增 `core.model_review.trace_review`，从本次 trace 生成机器可读 `trace_review.json` 和给用户看的 `trace_summary.md`，总结模型是否真的进场、输入是否足够、schema 输出是否可信、gate 为什么通过或阻断、下一步应修哪里。
- **验收修复**：修复 trace gate 只看 provider / schema 而忽略模型自报 `status=fail`、`blockingReasons` 或 `issues` 的假绿问题；阻断原因聚合也加固为不会把字符串拆成单字符。
- **验证**：`tests.core.test_model_review` 20 OK，覆盖成功调用、禁用未调用、非零退出、模型自报 fail 时 trace / summary 阻断。
- **边界**：本包不调用真实模型 provider、不连接 AutoCAD、不写 / 保存 DWG、不提升表 C；trace review 只用于调试和交付说明，不能替代 schema 校验、CAD readback、A-to-A hard gate 或用户验收。

### SYSTEM-ASSET-A1-REPAIR-SCOPE-GUARD-01：A2 修复越界误删 A1 框线的回滚加固

- **触发**：用户指出上一轮只授权修改 A2，但 A1 线型 / 图层 / 填充标准表格的线框被误删，属于非常错误的越界修改。
- **根因**：`scripts/layout_system_asset_shelves.py` 新增的 `CODEX_PREVIEW` 清理函数没有目标 bbox / handles 约束，常规 layout 运行时全图删除该层实体；A1 表格框线当时也在 `CODEX_PREVIEW` 上，因此被一起清掉。
- **代码修复**：`_purge_forbidden_preview_layer_content()` 改为显式 `scope_bbox` 才执行；无范围时返回 `not_run`，避免再次全局删除。新增回归测试覆盖 A2 范围清理不影响 A1、无范围不执行。
- **真实 CAD 修复**：在 `libraries/system_library/drawing_standards/basic/standard_assets.dwg` 原位恢复 A1 线型表边框、列线、行线和分组线，新增 191 条 `ASSET_PROOF_CONTENT` 线实体，不删除现有实体，不保存当前业务 DWG。
- **证据**：修复报告 `output/validation_runs/system-assets/asset-library-shelves/a1_linetype_frame_repair_report.json`；视觉辅助截图 `output/previews/system-asset-a1-restored-a2-cleaned.png`；A1 回读显示 `ASSET_PROOF_CONTENT|AcDbLine=199`、`CODEX_PREVIEW=0`。

## 2026-06-03

### MODEL-BACKED-VISUAL-ACCEPTANCE-REVIEWER-P4：通用视觉验收模型型复审 Agent

- **触发**：用户指出 A2 截图中的核心失败不是框线本身，而是框内文字像乱码、内容不对、左侧贴边冲突、不美观且不可复用；系统需要先把“用户可见验收”的模型型 reviewer 框架接入，而不是立刻铺开所有 prompt 教学。
- **实现**：新增 `pipeline_visual_acceptance_reviewer`、`core/model_review/visual_acceptance_review.py` 和 `visual_acceptance_review.schema.json`，把美观度、文字可读性、乱码、遮挡、裁剪、对齐、意图匹配、可复用边界和非截图证据纳入只读模型复审字段。
- **门禁**：`visual_acceptance_review` 已接入 `a_to_a_task_contract` 和 `pipeline_manifest`；资产 DWG 仓库布局现在同时要求专用 `visual_layout_review` 与通用 `visual_acceptance_review`。模型输出只能进入 `modelBackedVisualAcceptance`，不能执行 CAD、保存 DWG、删除实体、替代用户验收、CAD readback、sourceSpec / reuse replay 或表 C 证据。
- **二次加固**：模型自称 `status=pass` 但任一关键视觉布尔字段为 false 时，转换输出仍为 fail 并写入 `blockingReasons`；英文触发词从宽泛 `acceptance` 收窄为 `user acceptance` / `acceptance review` / `acceptance gate`，避免普通 acceptance report 误触发视觉验收 Agent。
- **三次加固**：新增 `core/model_review/provider_status.py`，所有模型 reviewer 输出统一 `modelProviderStatus`，包含 `modelInvoked`、`modelUnavailable`、`schemaValid`、`route`、`required` 和 `blocking`；路线策略登记 `codex_cli_local`、`local_model`、`remote_summary_only`、`remote_full_visual`，远端 summary / 截图 / 报告路线必须先有用户授权。
- **同步与验证**：`capability-map-data.js` 已同步为 `agentProfiles=25`、`promptContracts=25`；模型型复审 Agent 为 `pipeline_visual_layout_reviewer` 和 `pipeline_visual_acceptance_reviewer`。验证覆盖 `tests.core.test_model_review`、`tests.core.test_a_to_a_task_contract`、`tests.core.test_training_workbench_sync`、`scripts/run_a_to_a_orchestration_gate_check.py` 和 `scripts/sync_training_workbench.py`。
- **边界**：本包未真实调用远端 / 本地模型，未连接 AutoCAD，未写入 / 保存 DWG，不提升表 C；A2 当前图仍需后续单独做真实局部修复和人工复审。

### A2-ASSET-WAREHOUSE-EVIDENCE-CLOSURE-REALCAD-01：A2 仓库真实 CAD 修复与证据闭合

- **触发**：前序模型型 reviewer / 仓库治理包已经让 missing evidence refs 与 latest shelf layout report 缺失正确暴露为 fail；用户要求做“证据闭合 / A2 仓库真实 CAD 修复包”，并校验临时 MD 仍有无未解决事项。
- **实现**：新增 `core/assets/asset_evidence_closure.py` 和 `scripts/close_system_asset_evidence_refs.py`，把 active evidence refs 指向本轮 current shelf report、聚焦截图、dimension / linetype reuse plan-only probe，并把历史缺失引用作为闭合边界记录；不创建空 stub 伪造历史证据。
- **真实 CAD**：重新运行 `scripts/layout_system_asset_shelves.py`，打开 / 激活 / 保存 `libraries/system_library/drawing_standards/basic/standard_assets.dwg`。本轮 `protectedContentReadback.entityCount=349`，A1 受保护内容 179 个实体，A2 受保护内容 170 个实体；新建仓库脚手架 `createdHandleCount=219`，`createdEntityReadback.status=ok`，`visualClearanceAudit.status=pass`，`visualReadabilityAudit.status=pass`。
- **证据**：shelf report 位于 `output/validation_runs/system-assets/asset-library-shelves/shelf_layout_report.json`；治理决策位于 `output/validation_runs/system-assets/library-governance/final_hardening_decision.json`；聚焦截图位于 `output/previews/system-asset-warehouse-evidence-closure-a2-focused.png`；闭合报告位于 `output/validation_runs/system-assets/evidence-closure/drawing_standards_basic_evidence_closure.json`。
- **验证**：`run_asset_library_governance_check.py` pass，`sediment_system_asset.py --verify --category drawing_standards.basic` pass，`tests.core.test_asset_evidence_closure tests.core.test_asset_library_governance tests.core.test_system_asset_sedimentation` 共 32 OK，Python compile pass，`sync_training_workbench.py` pass / Agent check 43/43 pass。
- **边界**：本轮只保存系统资产 DWG，不保存当前业务 DWG；没有真实调用 `gpt-5.5`；截图是视觉辅助，用户人工视觉复审仍待确认；`run_data_bloat_audit.py --summary-only` 仍因表 C coverage 历史 `report_path_missing=303` blocked，需要单独恢复 / 重跑表 C 证据或审查降级 claims。

### MODEL-BACKED-ASSET-GOVERNOR-REPAIR-P3：资产守门员模型辅助与 repair proposal 边界

- **触发**：用户要求继续把当前偏规则 / 契约型的 pipeline Agent 向“少数模型型评审 + 强规则门禁”推进，但不希望模型直接拥有删除、保存或 CAD 执行权限。
- **实现**：新增 `core/model_review/asset_governor_review.py` 与 `repair_plan_review.py` 及对应 schema。资产守门员可读取模型辅助分类、来源边界和 clean source 建议并生成 `modelAssistedDecision`；修复 Agent 可读取 `modelBackedRepairPlan` / `repairPlanCandidate`，但必须保持 `executionPolicy=proposal_only`。
- **门禁**：模型建议不能覆盖 `sourceBoundaryDecision`、CAD readback、reuse probe、保存边界或 verified 晋升；repair plan 模型候选不能带 `cadCommands`、广域删除、保存当前 DWG、正式图层编辑或执行授权。
- **同步**：更新 `pipeline_asset_governor`、`pipeline_repair`、manifest、共享 Prompt 生成源和 Agent check；`scripts/sync_training_workbench.py` 现在每次刷新 `agents/COMMON_PROMPT_CONTRACT.md`，避免没有新训练验收报告时共享规则漂移。
- **验证**：P3 相关单测 57 OK；`scripts/run_a_to_a_orchestration_gate_check.py` pass；`scripts/sync_training_workbench.py --skip-coverage` pass，Agent check 43/43 pass；Python compile 与 5 个 Agent / schema JSON 加载通过。`run_asset_library_governance_check.py` 仍因既有 referenced evidence 文件和 latest shelf layout report 缺失 fail。
- **边界**：未真实调用 `gpt-5.5`，未连接 AutoCAD，未写入 / 保存 DWG，不提升表 C，不修复 A2 当前仓库排版。

### DATA-BLOAT-EVIDENCE-CLOSURE-01：训练事实源缺失路径归档与工作台同步恢复

- **触发**：`capability-map-data.js` 瘦身后，工作台同步仍因 13 个 active training `fact_source` 指向不存在的历史 output 路径而失败；用户要求修复治理验收中“证据路径缺失”的问题，并确认这属于小修而非重构。
- **修复**：审查 `docs/training/training-sources.json` 中 13 个当前工作区不可达的历史训练 / 资产事实源，将其从 `active` 改为 `archived`，保留原路径并写入 `archiveReason`，避免用空 stub、派生快照或 sync report 伪造证据。
- **测试加固**：`tests/core/test_training_workbench_sync.py` 不再依赖真实 manifest 处于坏状态；同步通过用例改为要求当前 manifest 闭合，负例改成测试内注入缺失 fact source。
- **验证**：先跑单测确认 sync 仍失败形成红测；修复后 `scripts/sync_training_workbench.py` pass，Agent check 43/43 pass，`training_source_paths_exist` pass；`tests.core.test_training_workbench_sync tests.core.test_data_bloat_audit` 21 OK；`scripts/run_training_workbench_agent_check.py` pass。
- **边界**：`scripts/run_data_bloat_audit.py --summary-only` 仍返回 blocked，但只剩 coverage `report_path_missing=303`。这 303 条来自表 C registry 历史 showcase 证据路径缺失，需要恢复 / 重跑 Table C 证据或审查降级 claim，不能用本轮小修清零。

### DATA-BLOAT-GOVERNANCE-BEFORE-TRAINING-01：训练前数据防膨胀与 A-to-A 共识收尾

- **触发**：用户担心进入训练阶段后，`capability-map-data.js`、debug 中间物、test artifacts、retry / dry-run / execution summary 和旧截图会持续膨胀；同时担心后续 Agent 忘记本轮优化，训练越跑越堆。
- **反方校验结论**：多 Agent 评审认为第一包不应直接 chunk，也不应把 `2MB/30000行` 作为立刻 hard fail；应先把 evidence closure、protected / candidate / blocked / derived 分类和 A-to-A hard gate 写入系统规则。诊断报告和工作台快照不能反向成为训练事实源。
- **规则接通**：更新 `AGENTS.md`、`CORE_CONTEXT_BRIEF.md`、`docs/architecture/cad-agent-task-chain.md`、`docs/training/README.md`、`docs/governance/cad-agent-rules.md`、`agents/cad_designer/rules.md`、`agents/COMMON_PROMPT_CONTRACT.md`、`agents/pipeline/README.md` 和 `agents/pipeline/pipeline_manifest.json`。`pipeline_manifest.json` 新增 task kind → hard gate 映射、`data_bloat_governance` 阻断完成声明、治理报告 artifact 模板和 `workbench_snapshot_refresh` 轻量例外。
- **机器治理**：`core/maintenance/doc_governance.py` 新增 `data_bloat_governance` 子项；`tests/core/test_doc_governance.py` 补坏 manifest / 好 manifest 回归，防止后续 Agent 或配置改动漏掉这条门禁。
- **边界**：本轮不实现 `scripts/run_data_bloat_audit.py`、不改 `build_capability_map_data.py` compact 输出、不移动 / 删除 output，不运行 CAD，不提升表 C；相关文档把未实现项标为 `pending_implementation`，不得误报已落地。

### REPO-AUDIT-TABLEC-BOUNDARY-01：审计阻断口径与表 C claim 边界

- **触发**：用户指出当前仓库有大量变更、未跟踪文件、`sys.path` 入口问题，以及 `verified_count=0` / `showcase_count=303` 容易被误读。
- **修复**：删除 `core/execution/execute_plan.py`、`core/verification/self_check.py` 的本地 `sys.path.insert`；新增 core 模块路径污染回归测试。`run_repo_audit` 新增 `severity_counts`、`blocking_finding_count` 和 CLI `--fail-on-severity`，用于阻断 medium/high，同时保留 low 大文件治理项。
- **表 C**：`capability_coverage` 新增 `claim_level_boundary`，明确 `showcase` 有证据路径但不等同严格几何 verified；当前机器报告为 `strict_geometry_verified_count=0`、`evidence_path_showcase_count=303`。
- **验证**：`tests.core.test_script_bootstrap` 6 OK；`tests.core.test_repo_audit tests.core.test_script_bootstrap` 15 OK；`tests.core.test_capability_coverage` 6 OK；`scripts/run_repo_audit.py --max-python-lines 500 --fail-on-severity medium` 返回 0，报告 20 low、0 medium、0 high。

### DEV-VOLUME-AUDIT-SCOPING-01：工作树体量审计分组与中风险阻断

- **触发**：用户指出当前仓库 changed / untracked 数量过大，旧 `run_dev_volume_audit.py` 只给原始数量和 findings，无法判断哪些目录需要分包收口、哪些只是派生大文件。
- **修复**：`core.maintenance.dev_volume_audit` 新增 `severity_counts`、`blocking_severity`、`blocking_finding_count`，并输出 `untracked_by_area` 与 `untracked_groups`；`scripts/run_dev_volume_audit.py` 新增 `--fail-on-severity low|medium|high`，保留 `--fail-on-findings` 严格模式。路径分类新增 `agents` 和 `openspec`，避免把 pipeline / change contract 混成 `other` 或普通 `status_docs`。
- **二次补强**：报告新增 `tracked_by_area`、`changed_groups`、`tracked_groups` 和 `by_group_line_delta`，让已跟踪变更、未跟踪变更和派生大文件都能按功能簇分开看，支持后续按包拆分，而不是只按总数判断。
- **输出润色**：报告新增 `top_changed_groups`、`top_tracked_groups`、`top_untracked_groups`；CLI 新增 `--summary-only --top-groups N`，日常验证可一屏看到阻断原因、top 收口簇和最大 tracked delta，不必展开完整 group map。
- **当前事实**：真实仓库运行 `scripts/run_dev_volume_audit.py --fail-on-severity medium` 仍返回 1：`changed_file_count=185`、`untracked_file_count=105`、`severity_counts={low:2, medium:2, high:0}`、`blocking_finding_count=2`。主要未跟踪簇为 `agents/pipeline=17`、`tests/core=17`、`openspec/changes=13`、`core/training=10`，不是可直接删除的缓存。
- **验证**：先写红测确认缺字段和 CLI 参数会失败，再实现转绿；`tests.core.test_dev_volume_audit` 10 OK；相关回归 `tests.core.test_dev_volume_audit tests.core.test_repo_audit tests.core.test_script_bootstrap tests.core.test_capability_coverage tests.core.test_training_workbench_sync` 46 OK。
- **边界**：本轮只让 dev volume 审计可定位、可作为中风险 gate；未删除、未 stage、未提交任何用户已有未跟踪文件。工作树体量收口仍需要后续按功能包拆分、提交或明确清理策略。

### A-TO-A-TASK-CONTRACT-GATE-01：主 Agent 任务合同与视觉布局复审门禁

- **触发**：用户指出系统已有视觉验收能力，但通用资产 DWG 仓库式排版仍多轮偏离，本质是 A-to-A 层面没有由主 Agent 把规则拆分、派发给责任 Agent，并在缺少责任结论时阻断。
- **根因**：`orchestrate_request()` 只有 request gate、scene activation、semantic asset route 和 workflow dispatch；缺少 `TaskContract` 来声明本次必须有哪些 Agent 输出、哪些 hard gate 必须通过。资产库排版语义也没有专门的视觉布局复审 Agent，因此截图非空、对象数量或普通 readback 容易被误当成视觉验收。
- **实现**：新增 `core/orchestrator/a_to_a_task_contract.py`，识别 `system_asset_sedimentation`、`asset_dwg_layout` 和 `visual_layout_review`；接入 `workflow_dispatch`，合同 blocked 时输出 `a-to-a hard gate` 阻断原因；新增 `pipeline_visual_layout_reviewer` Agent，登记 `asset_dwg_layout` flow、`visual_layout_review`、`asset_dwg_curation`、`asset_reuse_audit` 等 hard gate。
- **治理检查**：新增 `scripts/run_a_to_a_orchestration_gate_check.py`，检查 manifest、Agent 登记、合同识别、缺 Agent 输出阻断和 pass 输出放行。
- **二次加固**：`pipeline_visual_layout_reviewer` 不能只给 `status=pass`；`layoutMatchesMetaphor`、`primaryShelvesClear`、`futureExpansionClear`、`retrievalPathReadable`、`visualNoiseAcceptable` 任一缺失或非 pass，都会让 `visual_layout_review` 失败并阻断交付。
- **验证**：`tests.core.test_a_to_a_task_contract` 5 OK；相关回归 `tests.core.test_a_to_a_task_contract tests.core.test_workflow_dispatch tests.core.test_system_asset_sedimentation tests.core.test_semantic_asset_rules` 42 OK；`scripts/run_a_to_a_orchestration_gate_check.py` status=`pass`。本包未写 CAD、未保存 DWG、不提升表 C。

### SYSTEM-ASSET-DWG-VISUAL-WAREHOUSE-AUDIT-R5：视觉仓库验收与实体回读门禁

- **触发**：用户复核指出上一版验收口径仍偏了：脚本能写 metadata、DWG 能保存、截图能看到框线，并不等于“仓库货架架构”真的成立；验收必须能说明主货架 / 子货架、资产归属、空货位、index-only、zone bbox 和回读证据。
- **根因**：`scripts/run_asset_library_governance_check.py` 只检查 Agent 注册、协议文字和分区名称；`nativeLayout.visualRackPlan` 还是弱 metadata，缺少仓库架构、acceptance criteria 和 bbox 比例门禁。R4 的真实 DWG 视觉已经改对方向，但机器验收还没有阻止“标签式仓库”继续 pass。
- **Core 加固**：新增 `audit_visual_rack_plan()`，审计 `schemaVersion >= 2`、`layoutMode=classified_expandable_visual_warehouse_v2`、`warehouseArchitecture`、`acceptanceCriteria`、rack family 归属、slot ownership、copy policy、扩展空位和主仓区面积比例；`refresh_system_asset_layout_metadata()` 传入弱 `visualRackPlan` 时现在直接 fail，不写 `assets.json` / registry。
- **脚本加固**：`scripts/layout_system_asset_shelves.py` 写入前先跑 plan audit；真实写入后回读本轮 created handles，报告 `createdEntityReadback.status=ok`、`resolvedHandleCount=209`、`unresolvedHandleCount=0`、`unmanagedLayerCount=0`、`byLayer` 和 `unionBbox`。最终 pass 需要 `rackPlanAudit=pass`、实体回读 ok、metadata refresh pass 和系统资产 DWG 保存成功。
- **治理检查**：`scripts/run_asset_library_governance_check.py` 现在读取 `libraries/system_library/drawing_standards/basic/assets.json` 的 `nativeLayout.visualRackPlan` 并复用同一审计器；旧 R4 快照会 fail，刷新后 `visualRackPlan v2 warehouse audit` 进入 checked。
- **真实 CAD 证据**：`standard_assets.dwg` 已保存，上一版 209 个货架 handles 按报告清理，本轮新建 209 个 handles；`primaryWarehouseAreaRatio=0.8694`，`ownedSlotCount=11`，`expansionSlotCount=9`，`savedCurrentBusinessDwg=false`。报告为 `output/validation_runs/system-assets/asset-library-shelves/shelf_layout_report.json`，治理报告为 `output/validation_runs/system-assets/library-governance/final_hardening_decision.json`，截图为 `output/previews/system-asset-library-shelves-r2.png`。
- **验证**：`tests.core.test_system_asset_sedimentation` 22 OK；`scripts/layout_system_asset_shelves.py` status=`pass`；`scripts/run_asset_library_governance_check.py --output output/validation_runs/system-assets/library-governance/final_hardening_decision.json` status=`pass`；`scripts/sediment_system_asset.py --verify --category drawing_standards.basic` status=`pass`；`scripts/render_preview.py --capture-autocad-window ...` status=`captured`。
- **边界**：这证明系统资产 DWG 货架脚手架、仓库语义和本轮 created entities 回读过关；截图仍是 `visual_aid_only`，对象 block 本体仍进入各自分类 DWG，本轮不保存当前业务 DWG、不提升表 C。

### SYSTEM-ASSET-DWG-THREE-COLUMN-WAREHOUSE-R4：通用底座三列仓库与对象索引货架

- **触发**：用户继续指出 R3 虽已把现有内容放进大货架，但仓库还应明确区分“通用底座脚手架”和“对象类资产入口”，并让后续床铺、桌子、沙发等对象资产有可扩展置物架，而不是继续混在 drawing standards 的画布里。
- **Agent 复核**：资产 DWG 编排、资产馆员、复用审计和视觉排版视角共同收敛为三列方案：A 区承载绘图标准 clean source，B 区只承载跨库索引，不承载对象 block 本体；标签、证据、预留卡和隔离区默认 `never_copy`。
- **真实 CAD 改造**：`scripts/layout_system_asset_shelves.py` 将布局升级为 `r4_three_column_warehouse_with_object_index`：左列 `A1 线型 / 图层 / 填充标准`，中列 `A2 尺寸 / 文字 / 引线标准`，右列 `B 对象资产索引 / 跨库入口`，底部为 `02_PREVIEW_CARDS`、`03_REVIEW_QUARANTINE`、`99_EVIDENCE_LINKS`。顶部只保留安静索引，不再让导向箭头穿过内容。
- **分类槽位**：A 区稳定槽位为 `A01_LAYER_STANDARD`、`A02_LINETYPE_STANDARD`、`A03_PLOT_COLOR_LINEWEIGHT`、`A04_TEXT_STYLE`、`A05_DIMENSION_STYLE`、`A06_LEADER_SYMBOL_STYLE`、`A07_TABLE_TITLEBLOCK`、`A08_SCALE_UNIT_BASELINE`；B 区为 `B01_BEDS`、`B02_TABLES`、`B03_SEATING`、`B04_STORAGE`、`B05_DOORS_WINDOWS`、`B06_KITCHEN_BATH`、`B07_LIGHTING_EQUIPMENT`、`B08_CUSTOM_EXPANSION`，均为 `index_only / never_copy`。
- **检索同步**：`nativeLayout.visualRackPlan` 写入 `assets.json` / registry，包含 `displayPolicy`、`copySafety`、rack family、slot status、对象分类 `nativeDwg` 入口和 review zones，使未来检索能按 rack / slot / index-only 语义复用。
- **验证**：`scripts/layout_system_asset_shelves.py` status=`pass`，删除上一版 209 个货架句柄并新建 209 个 handles，`savedAssetDwg=true`、`savedCurrentBusinessDwg=false`，`polishHardeningDecision.status=complete_for_current_scope`；`tests.core.test_system_asset_sedimentation` + `tests.core.test_semantic_asset_rules` 22 OK；`scripts/sediment_system_asset.py --verify --category drawing_standards.basic` status=`pass`；`scripts/render_preview.py --check` status=`ready`；截图 `output/previews/system-asset-library-r4-three-column.png`。
- **边界**：本轮只重排系统资产 DWG 的可视仓库脚手架、槽位语义和检索元数据；对象资产真实 block 仍应进入各自分类 DWG，不保存当前业务 DWG，不提升表 C。

### SYSTEM-ASSET-DWG-CLASSIFIED-RACKS-R3：现有资产归入分类大货架

- **触发**：用户指出上一版仍像“左侧小预留格 + 中间堆旧内容”：线型表和尺寸样式面板没有真正进入对应货架，预留框尺寸也明显装不下现有资产。
- **真实 CAD 改造**：`scripts/layout_system_asset_shelves.py` 的布局逻辑改为让现有资产内容本身成为 `01_CLEAN_ASSETS` 主货架。`A 通用底座脚手架` 现在直接包住线型表和尺寸样式面板，`02_PREVIEW_CARDS` 下移为复审暂存带，不再承载已沉淀资产主体。
- **分类槽位**：`A02_LINETYPE` 对应 `linetype_style_summary_table`，`A03_DIMENSION_STYLE` 对应 `interior_dimension_style_visual_standard`；底部预留 `A01_LAYER_LINEWEIGHT`、`A04_TEXT_STYLE`、`A05_LEADER_ANNOTATION`、`A06_HATCH_PATTERN`、`A07_TABLE_TITLEBLOCK`、`A08_SYMBOL_NAMING`。右侧 `B_OBJECT_BLOCKS` 预留床铺、桌子、沙发椅子、柜体、门窗、厨卫、灯具设备和自定义扩展。
- **检索同步**：`refresh_system_asset_layout_metadata()` 新增 `visual_rack_plan` 参数，写入 `nativeLayout.visualRackPlan`；报告同步输出 `rackPlan`，使 DWG 视觉槽位和 JSON 检索语义一致。
- **验证**：`scripts/layout_system_asset_shelves.py` status=`pass`，删除上一版 229 个货架句柄并新建 219 个 handles，`savedAssetDwg=true`、`savedCurrentBusinessDwg=false`；`tests.core.test_system_asset_sedimentation` 18/18 OK；`scripts/sediment_system_asset.py --verify --category drawing_standards.basic` status=`pass`；`scripts/render_preview.py --check` status=`ready`；截图 `output/previews/system-asset-library-classified-racks-r3.png`。
- **边界**：本轮只重排系统资产 DWG 的仓库脚手架和槽位语义，不迁移 / 复制当前业务 DWG，不保存当前业务 DWG，不提升表 C。

### SYSTEM-ASSET-DWG-SHELVES-R1：系统资产 DWG 可视货架与动线落地

- **触发**：用户确认守门员和 Agent 规则还不够直观，希望先把通用资产 DWG 改成“仓库置物架”：先搭好索引台、货架、通道、隔离区和可扩展货位，后续资产再一个个归位。
- **真实 CAD 落地**：新增 `scripts/layout_system_asset_shelves.py`，连接 AutoCAD 后打开 / 激活 `libraries/system_library/drawing_standards/basic/standard_assets.dwg`，默认只按上一份货架报告中的 handles 清理旧脚手架，只有显式 `--clear-all-shelf-layers` 才做全层清理，不保存当前业务 DWG。
- **排版结构**：DWG 中新增 `00_INDEX`、`01_CLEAN_ASSETS`、`02_PREVIEW_CARDS`、`03_REVIEW_QUARANTINE`、`99_EVIDENCE_LINKS` 和 `EXPANSION_BAY_A`；左侧是干净源货架，中间是复审卡片，右侧是扩展货架，下方是隔离区和证据索引，紫色箭头表达沉淀动线。
- **检索同步**：新增 `refresh_system_asset_layout_metadata()`，把已有资产条目的旧网格布局刷新为 v2 `layoutPlan` / `libraryGovernance`，并同步 `libraries/system_library/registry.json`；这避免 DWG 可视排版与 registry 检索货位脱节。
- **R2 硬化**：收尾审查 Agent 建议区分“货架脚手架已写入”和“资产源几何已迁入”，并降低误删风险；现已在报告中写入 `nativeLayoutWrite=asset_library_shelf_scaffold_written_to_standard_assets_dwg` 和 `nativeWriteBoundary`，cleanup 也改为 `previous_report_handles`。
- **验证**：`scripts/layout_system_asset_shelves.py` status=`pass`，清理旧货架层 91 个对象并新建 91 个 handles，`savedAssetDwg=true`、`savedCurrentBusinessDwg=false`；`scripts/sediment_system_asset.py --verify --category drawing_standards.basic` status=`pass`；`tests.core.test_system_asset_sedimentation` 18/18 OK；截图 `output/previews/system-asset-library-shelves-r1.png`。
- **边界**：本轮是系统资产 DWG 的可视货架和元数据货位刷新，不把训练面板内容转成可复制源，不提升表 C，不保存当前业务 DWG。

### SYSTEM-ASSET-LIBRARY-GOVERNANCE-01：系统资产库守门员与 layoutPlan v2

- **触发**：用户指出系统资产 DWG 不应原封不动搬运训练内容；训练标题、说明文字、边框或证据路径若混入资产库，会让未来检索命中但复制源不干净。
- **OpenSpec**：新增 `openspec/changes/harden-system-asset-library-governance/`，定义 `system-asset-library-governance` 能力：沉淀先过守门员、资产 DWG 分区排版、训练污染清洗、复用审计和收尾润色加固判断。
- **Agent**：新增 `pipeline_asset_governor`，并注册 `pipeline_asset_librarian`、`pipeline_asset_dwg_curator`、`pipeline_asset_reuse_auditor`；全局 manifest 新增 `system_asset_sedimentation` flow、`asset_governance` hard gate 和禁止“训练画布当资产库”规则。
- **Core / CLI**：新增 `core.assets.system_asset_library_governance`；`system_asset_sedimentation` 生成 `native.layoutPlan` v2 与 `libraryGovernance`，registry / CLI 输出 `assetGovernanceDecision` 和 `polishHardeningDecision`。layoutPlan v2 包含五区、slot、plannedBbox、cleanSource、previewCard、evidenceLinks、cleanupPolicy 和兼容旧读取的 grid。
- **文档**：系统资产沉淀协议、system library README、CAD Designer rules、全局 Agent 流水线和训练 README 已同步：来源不清进入 metadata-only / `03_REVIEW_QUARANTINE`，训练标题 / 临时说明 / 边框 / 尺寸线 / 证据文字默认不得进入 `01_CLEAN_ASSETS`。
- **验证**：新增 / 扩展 `tests.core.test_system_asset_sedimentation`，覆盖 layoutPlan v2、quarantine / metadata-only、Agent manifest 注册和 CLI governance 输出；聚焦测试已通过。
- **边界**：本包不执行真实 CAD-native DWG 重排，不保存当前业务 DWG，不提升表 C；layoutPlan v2 和守门员决策不等于原生 DWG 已重新排版。

### TRAINING-ARTIFACT-RETENTION-01：训练截图保留策略执行器

- **触发**：用户询问训练过程中大量截图是否有删除规则，确认文档已有“只长期保留最终报告、队列状态、learning ledger / Agent memory / Prompt addendum 和最近一份人工复核预览图”的规则，但执行层还没有统一清理器。
- **实现**：新增 `core.training.artifact_retention`，按 scan roots 收集 `.png/.jpg/.jpeg` 候选，按 reference roots 扫描 JSON / Markdown / JS / Python / HTML 文本引用；被最终报告、工作台同步、learning ledger、Agent / docs 引用的截图保留，每个目录最近一份预览图保留，其余未引用旧图进入归档计划。
- **CLI**：新增 `scripts/run_training_artifact_retention.py`。默认扫描 `output/previews` 和 `output/training_queues`，写入 `output/validation_runs/training-artifact-retention/retention_report.json`；默认 dry-run，显式 `--write` 才移动到 `archive/training_artifacts/`，不做不可逆删除。
- **训练入口接入**：`scripts/run_training_queue.py` 和 `scripts/run_cad_foundation_remaining_training.py` 在 pass + post-sync 后写入 `postTrainingArtifactRetention`；默认 dry-run，可用 `--no-artifact-retention` 跳过，可用 `--artifact-retention-write` 归档未引用旧图。
- **验证**：新增 `tests.core.test_training_artifact_retention`；训练队列和剩余 21 项入口均覆盖 retention hook。相关 focused tests 已通过。
- **边界**：本包不删除文件，只在显式 write 时归档图片；不清理被报告引用的证据，不移动最终报告 / queue state / ledger / memory / Prompt addendum；截图仍是 `visual_aid_only`，不替代 CAD handles / readback / audit。

### REPAIR-RUN-BEFORE-DELIVERY-01：修复交付默认运行门禁

- **触发**：用户指出上轮截图协议修复只跑了 unit / OpenSpec，没有默认补跑真实 CAD / 截图实际链路；以后所有修复都要默认运行后再交付。
- **规则**：`AGENTS.md` 新增“修复交付必须运行”；`docs/governance/cad-agent-rules.md` 新增 §2.3。普通代码 / 文档 / 规则修复至少跑对应测试、校验、审计或格式检查；CAD 落图、截图、训练、runner、验证、资产复用 / 沉淀或局部修复链路改动，除单测外必须补一条代表性实际链路。
- **CAD 不可用处理**：真实 CAD / GUI / COM 因沙箱、权限、窗口、授权或活动 DWG 不可用时，先按 blocker 流程自救并必要时申请外部执行；仍不可用时只能报 `blocked` / `not_run` / `not_verified`，不得用“完成”口吻。
- **截图链路补跑**：`scripts/render_preview.py --check` 返回 `status=ready`，识别到 `Autodesk AutoCAD 2026 - [Drawing2.dwg]`；旧 summary 的 `target_handle=2A28` 捕获成功但返回 `focus_target_unavailable / resolved_count=0`，验证目标不可用时不会静默退回全图；提权只读 COM 回读当前 `CODEX_PREVIEW` 得到 385 个实体后，用真实句柄 `1F7C` 运行 `scripts/render_preview.py --capture-autocad-window --target-handle 1F7C --layer CODEX_PREVIEW`，返回 `focus.status=zoomed_to_bbox`、`resolved_count=1`、`source=target_handles`、`foreground_first=false`、`occlusion_safe=true`。
- **截图证据**：聚焦截图为 `output/previews/repair-run-before-delivery-focused-handle.png`，像素检查为 `size=(1701, 1388)`、`gray_extrema=(0,255)`、`gray_stddev=30.422`，非空白；截图仍是 `visual_aid_only`，不替代 created handles / readback / audit。
- **边界**：本轮只补规则和截图实际链路复验；未保存当前业务 DWG、未修改正式图层、未删除实体、不提升表 C。

### TASK-SCOPED-CAD-PREVIEW-CAPTURE-01：任务级精准截图协议

- **触发**：用户指出 AutoCAD 在后台或当前桌面不是顶层时，测试截图容易看不到；同时大 DWG 中有海量图块，截图必须聚焦本次任务 / 本次局部修复对象，而不是当前 CAD 整体视图。
- **OpenSpec**：新增 `openspec/changes/task-scoped-cad-preview-capture/`，能力契约为 `task-scoped-cad-preview`；明确截图口径为“低打扰、强聚焦、弱证据”。
- **底层实现**：`core/verification/render_preview.py` 新增任务级 focus target 选择：`target_handles`、`repair_plan.target_handles`、`repair_plan.target_bbox`、显式 `target_bbox` 优先于整批 `execution_summary.created_handles`；CLI 新增 `--target-handle`、`--target-handles`、`--bbox`、`--repair-plan`，并让 `--layer` 进入聚焦链路。
- **防退全图**：`AutoCADComDriver.zoom_to_handles_extents()` 在句柄 extents 不可用时返回 `focus_target_unavailable`，不再静默 `ZoomExtents`；`render_preview` 也会把 `zoom_extents` 归类为 focus target unavailable，避免海量图块重新进入视野。
- **Runner 接入**：`visual_cad_review` 默认用 `prepare_autocad_for_capture(..., execution_summary=...)`；`cross_machine_reverify` 会把 execute stdout 写为 `migration-reverify-execution-summary.json` 并传给截图；`foundation_batch_training` 在 `capture_preview=true` 时写入 `remaining_21_preview.png` 和结构化 `visualPreview`。
- **证据边界**：所有 preview payload 均保留 `role=visual_aid_only`；截图只用于目视复核和局部修复确认，不替代 created handles / readback / audit 的几何证明。
- **验证**：CAD-MCP venv focused tests `tests.core.test_render_preview`、`tests.core.test_table_c_evidence_gate`、`tests.core.test_beta_cross_machine_02_gate`、`tests.core.test_cad_foundation_remaining_training` 共 40 tests OK；`openspec.cmd validate --all --strict --json --no-interactive` 11/11 changes pass。
- **边界**：本包不运行真实 CAD、不保存当前 DWG、不修改正式图层、不提升表 C；线型表、尺寸样式和复杂 visual smoke 的批量接入作为后续扩展。

## 2026-06-02

### CAD-TRAINING-PROMOTION-GATE-01：训练沉淀 Promotion Gate 与 A-to-A 校准门禁

- **触发**：用户要求把“白话 -> 执行 -> 校验 -> 失败修复 -> 规则沉淀 -> A-to-A 校准 -> 原任务回测 -> 事实源同步”作为训练链路可自动同步的环节，避免每次训练结束后还要人工追问“规则漏没漏写、工作台有没有同步、Agent 有没有校准”。
- **实现**：新增 `core.training.promotion_gate`，正式训练 promotion 会输出 `promotionGate`，包含 `updateTrainingSource`、`updateWorkbench`、`updateBaseRules`、`updateTaskRules`、`updateAgentCalibration`、`updateChecker`、`retestOriginalTask` 七项决策和 `agentCalibration` 正反例 / 证据边界。
- **防误沉淀**：`quick_trial` 被排除在 promotable acceptance 之外，只能是 `promotionLevel=observation`；未知 `capabilityId` 不再 fallback 到 `cad_designer`；底座规则、单项规则和检查器 delta 只标为 `needs_reviewed_package`，不由训练脚本静默写长期规则。
- **纠错链路**：`write_learning_promotion_report` 会为失败 / 纠错报告写入候选 `promotionGate`，说明是否需要 reviewed package、Agent 校准和原任务回测；`mutated_targets` 仍为空，实际规则修改必须另包执行。
- **工作台门禁**：`scripts/run_training_workbench_agent_check.py` 新增 `systemized_training_has_promotion_gate` 和 `promotion_gate_decisions_complete`；`scripts/sync_training_workbench.py` 的 sync report 暴露 `learning_promotion.promotionGate`。
- **同步结果**：已运行 `scripts/sync_training_workbench.py --skip-coverage`，刷新 `capability-map-data.js`、`output/training_learning/agent_learning_ledger.json` 和 Agent memory / prompt 派生文件；Agent check 39/39 pass。
- **验证**：`tests.core.test_training_learning_promotion` 10/10 OK；`tests.core.test_training_workbench_sync` 15/15 OK。
- **边界**：本包不运行真实 CAD、不提升表 C、不自动修改全局规则 / 检查器 / 资产 registry；这些仍需 reviewed package 和原任务回测证据。

### CAD-AGENT-TASK-CHAIN-01：系统任务链路整合

- **触发**：用户指出上一版训练闭环仍有价值，但还缺少“白话 -> Agent 语义拆分 -> 根据规则拆复杂任务 -> 分发执行”的执行层闭环；两条链路都应沉淀到系统文档。
- **实现**：新增 `docs/architecture/cad-agent-task-chain.md`，把执行编排链路和训练学习链路合并为系统默认流程，覆盖输入分流、语义拆分、单一子任务模型、Agent 分发、执行前门禁、验证、训练回流、A-to-A 校准和事实源同步。
- **入口同步**：`CORE_CONTEXT_BRIEF.md`、`docs/architecture/README.md`、`docs/training/global-agent-pipeline.md`、`docs/training/README.md` 和 `docs/governance/cad-agent-rules.md` 已接入该总链路，避免后续只按训练 README 或单个 Agent pipeline 片面恢复。
- **风险记录**：`docs/status/issues.md` 新增“执行闭环和训练闭环割裂”问题，明确后续根源修复必须判断是否同步底座规则、单一任务规则、检查器、Prompt / memory 和 A-to-A 校准。
- **边界**：本包只做架构 / 规则文档沉淀，不运行真实 CAD、不新增训练证据、不提升表 C。

### CAD-NATIVE-ASSET-REUSE-HARDENING-01：真实 CAD 跨 DWG 复用加固验证

- **触发**：用户打开 AutoCAD 后，要求自动加固校验上一轮“语义资产复用升级”中尚未新增真实 CAD-native 证据的边界。
- **执行**：先跑 `scripts/render_preview.py --check` 和 `scripts/self_check.py`；普通沙箱下 `scripts/reuse_system_asset.py --workflow "放一个线型表到当前图"` 因 COM 隔离无法取得活动 `AutoCAD.Application`，按 GUI/COM 权限规则提权后重试成功。
- **真实 CAD 复用**：从 `libraries/system_library/drawing_standards/basic/standard_assets.dwg` 复用 `linetype_style_summary_table` 到当前 `Drawing2.dwg` 的 `CODEX_PREVIEW`；`copyMethod=copyobjects_handle_diff`，source selected 450、created handles 450、readback 450、`savedCurrentDwg=false`。
- **截图证据**：`scripts/render_preview.py --capture-autocad-window --execution-summary ...` 成功用 AutoCAD 客户区 `PrintWindow` 截图，按 450 个 handles 的几何 extents 自动取景，截图路径为 `output/previews/system-asset-reuse-hardening-20260602.png`。
- **机器证据**：复用报告为 `output/validation_runs/system-assets/cad-native-hardening/reuse_workflow_real.json`；补充硬断言检查了 status、workflowStatus、task count、created/readback count、target layer、copy method 和 `savedCurrentDwg=false`。
- **边界**：本轮只证明已沉淀线型表资产可真实跨 DWG 写入当前业务 DWG 的预览层且不保存当前业务 DWG；系统资产 DWG 新增原生内容后的 `Saved=true` / 打开复审链路，仍需在真正“沉淀资产 CAD-native 写入”时单独验证。

### UTF8-FIRST-CAD-ASSET-GUARD-01：中文编码前置门禁

- **触发**：用户指出通用资产 DWG 沉淀第一步曾出现中文乱码，虽然后续截图自验修复，但底座不应先做错再修。
- **实现**：新增 `core.runtime.encoding_guard`，检测 `??`、`�`、`绾垮瀷` / `鏍峰` 等典型中文编码损坏；`scripts/_bootstrap.py` 强制设置 `PYTHONUTF8=1`、`PYTHONIOENCODING=utf-8` 并重配 stdout/stderr。
- **沉淀入口**：`core.assets.system_asset_sedimentation.sediment_system_asset` 在写 `assets.json` / `registry.json` 前执行 `encodingPreflight`；项目路径、资产名、别名、用途、来源文档、反馈路径等已损坏时直接 fail，不写合同、不打开 / 保存 CAD。
- **绘图入口**：`core.training.linetype_table_demo.validate_visible_text` 在绘制前检查 visible text，问号化和伪中文 mojibake 都会前置失败。
- **CLI**：`scripts/sediment_system_asset.py` 与 `scripts/draw_linetype_table.py` 输出严格 JSON。
- **验证**：`tests.core.test_script_bootstrap` + `tests.core.test_system_asset_sedimentation` + `tests.core.test_linetype_table_demo` + `tests.core.test_system_asset_reuse` 35/35 OK，覆盖 UTF-8 环境强制、沉淀前拒绝乱码且不写 registry、CLI 结构化 JSON fail、线型表绘制前拒绝 mojibake。
- **边界**：该门禁防止已损坏的文本进入 CAD / 资产合同；若外部终端已经把用户输入破坏，它会阻断并要求改用 UTF-8 文件 / 模块 payload，而不是尝试猜回原文。

### SYSTEM-ASSET-REUSE-WORKFLOW-01：跨 DWG 复用工作流与主系统理解力

- **触发**：用户指出未来系统资产库会有很多内容，真实需求不只是跨 DWG 复制，而是语义拆分、任务分配、资产寻找和精准复用。
- **实现**：`core.assets.system_asset_reuse` 从单资产 query 扩展为 workflow 层，新增显式 / 隐式资产触发判断、候选排序、多资产任务拆分、`partial` 阻断、目标槽位分配和 workflow apply 汇总回读；润色加固后，copy 返回 handles 但当前 DWG 读不回时不再判为 `asset_reused`，而是停在 readback blocked 状态。
- **CLI**：`scripts/reuse_system_asset.py` 新增 `--workflow`，可 plan-only 生成 `system_asset_reuse_workflow`，也可连接当前 AutoCAD 执行 ready 子任务；输出使用严格 JSON，禁止 `NaN` / `Infinity` 等非标准 JSON 值。
- **规则**：`AGENTS.md`、`docs/governance/cad-agent-rules.md`、`docs/architecture/system-asset-sedimentation-protocol.md` 和 `docs/architecture/system-asset-reuse-workflow.md` 已写入跨 DWG 复用工作流：无显式“资产”但强匹配时先查系统库；无资产信号返回 `not_asset_reuse_request` 后交回普通 `CAD_PLAN`；来源不清必须保留 `needs_precise_native_source`。
- **验证**：`tests.core.test_system_asset_reuse` 13/13 OK；关联 `tests.core.test_system_asset_reuse` + `tests.core.test_system_asset_sedimentation` + `tests.core.test_linetype_table_demo` 27/27 OK，覆盖隐式强匹配、多资产拆分、单句多资产识别、partial 阻断、workflow fake-driver 写入回读、无 ready plan 阻断、读不回不算通过、负向探针和 CLI plan-only。
- **边界**：本包增强主系统理解与 workflow 合同；真实 CAD 复制能力沿用 `SYSTEM-ASSET-REUSE-INSERT-01` 证据。复杂 block 属性保持、CTB/STB / plot、跨图样式依赖和自动布局避让仍需后续专项验证。

### SYSTEM-ASSET-REUSE-INSERT-01：系统资产语义检索与跨 DWG 复用

- **触发**：用户要求跨另一个 DWG 的插入复用落地；未来可能说“从 XX 资产调用 XX 放到当前 DWG”，甚至不特别描述资产来源时，Agent 也要智能判断是否应从已沉淀资产库检索并写入当前文件。
- **实现**：新增 `core/assets/system_asset_reuse.py` 与 CLI `scripts/reuse_system_asset.py`。入口会读取 `libraries/system_library/registry.json`，按 asset id、名称、别名、用途、标签、场景标签和 `retrieval.matchText` 做语义匹配，并生成 source spec / target layer / base point / save boundary 复用计划。
- **CAD 写入**：`AutoCADComDriver.copy_entities_from_dwg()` 支持从系统资产 native DWG 复制到当前活动 DWG；优先尝试 AutoCAD `CopyObjects`，若 COM 返回不稳定则用源 DWG readback 重放 line / text / circle / arc / polyline，保留常见颜色、线宽、线型和线型比例。写入默认只作用于 `CODEX_PREVIEW`，并保持 `savedCurrentDwg=false`。
- **阻断边界**：匹配到资产但没有 `includedHandles`、`blockName`、verified `style_standard` 或其它精确来源时返回 `needs_precise_native_source`；不得从 whole modelspace、current screen、all visible 或训练面板硬拷贝。
- **真实 CAD 验证**：用新的未保存临时 DWG 作为当前目标，从 `libraries/system_library/drawing_standards/basic/standard_assets.dwg` 复用 `linetype_style_summary_table`；source selected 450，created handles 450，readback 450，目标 `Drawing7.dwg` 未保存。报告 `output/validation_runs/system-assets/asset-reuse/linetype_table_reuse_real.json`，截图 `output/previews/system-asset-reuse-linetype-table-20260602.png`。
- **资产合同**：`linetype_style_summary_table` 已追加 `reuseReplay` 证据，`verification.status=native_dwg_reuse_verified`，并把 `CAD insertion replay from a different drawing` 从 `notChecked` 移入 checked。
- **验证**：`tests.core.test_system_asset_reuse` + `tests.core.test_system_asset_sedimentation` 15/15 OK；`git diff --check` 对本轮代码文件无空白错误。
- **边界**：当前证明系统资产展示几何 / 样式表可跨 DWG 写入当前预览层；复杂对象 block 属性、跨图 block definition 属性保持、CTB/STB / plot 输出和保存业务 DWG 仍需后续专项验证。

### SYSTEM-ASSET-NATIVE-SAVE-REVIEW-01：系统资产 DWG 保存与复审授权

- **触发**：用户要求后续说“沉淀 XXX 资产”时，对应系统资产 DWG 添加内容后都必须保存，并在沉淀后默认打开对应 DWG 供人工复审。
- **规则**：`AGENTS.md`、`docs/governance/cad-agent-rules.md` 和系统资产协议已明确：沉淀口令默认授权 Codex 对对应分类的系统资产 DWG 执行必要的创建、打开 / 激活、写入和保存。
- **保存门槛**：只要本轮向 `libraries/system_library/**/**/*_assets.dwg` 或资产合同解析出的 `nativeDwg` 添加、替换或修复了原生 CAD 内容，必须保存该 DWG，并回读活动文档路径、`Saved=true` 和关键实体 / 样式证据。
- **人工复审**：沉淀收尾默认打开 / 激活对应系统资产 DWG，让用户直接在 AutoCAD 里复审；若来源不足或没有生成 DWG，则只登记合同并说明未打开原因。
- **边界**：该授权只覆盖系统资产库 DWG，不覆盖用户当前业务 DWG、原始图纸、正式图层、全模型空间清理或非系统资产文件的保存 / 覆盖；这些仍需另行明确授权。
- **验证**：文档口径更新后运行 `git diff --check` 通过；本包只改规则和状态记录，不连接真实 CAD、不提升表 C。

### LINETYPE-TABLE-INTEGRATED-LAYOUT-02：线型表整合双栏与样例自适应

- **触发**：用户指出 42 行线型表不应因 24 行被硬分页到旁边，`开启范围线` 圆弧样例越过本行框线，且表格行距不应被固定尺寸策略卡死。
- **判断**：24 行不是 CAD 或表格上限，而是 Agent / 生成器采用了过保守的 `paged_table` 布局建议；`开启范围线` 属于样例几何按固定半径和偏移绘制，未受样例单元格 bbox 约束。
- **实现**：`core.training.linetype_table_demo` 改为 `integrated_dual_panel` 单外框双栏；行高策略为 `adaptive_min_height`，样例绘制策略为 `fit_to_sample_cell_bbox`，`swing_arc` 和 `batting` 等复合样例按单元格高度自适应半径、振幅和边距。
- **覆盖扩展**：线型表扩为 42 行，覆盖基础图案线型、工程与家装语义、专业管线语义、边界与控制线、复合模拟线型；继续保留颜色、线宽、线型比例、`by_layer` 和多对象组合回读。
- **真实 CAD**：已清理目标区域旧 `CODEX_PREVIEW` 表格并重画最终版；451/451 handles 回读，`sampleOutOfCellCount=0`、`solidFillEntityCount=0`、`styleVerification.status=pass`；最终报告 `output/validation_runs/linetype-table/integrated-real/linetype_table_report.json`，截图 `output/previews/linetype-table-integrated-20260602.png`。
- **验证**：`tests.core.test_linetype_table_demo` 3/3 OK；后续联合测试和 `git diff --check` 见本轮交付。
- **边界**：真实 CAD 操作只作用于 `CODEX_PREVIEW`；未保存 DWG，未修改正式图层，不提升表 C。

### LINETYPE-TABLE-LAYOUT-01：线型表布局生成器根修

- **触发**：用户指出线型归纳表出现不需要的实心填充，标题区排版不舒服，左侧序号可用阿拉伯数字，且“基础图案线型 / 工程与家装语义 / 复合模拟线型”等分组标题被竖线切割。
- **判断**：主要根因是表格布局生成器缺少合并行和布局审计，不是单纯语义理解或 Prompt 问题；Prompt 只能提醒，真正防复发需要代码和测试约束。
- **实现**：`core.training.linetype_table_demo` 将序号改为 `1..26`，标题区按整行合并处理，分组标题行不画内部竖线，普通数据行才画分段竖线；生成器明确不使用填充 / 遮罩。
- **报告加固**：报告新增 `layoutPolicy`、`layoutChecks` 和 `created_handles`；机器检查包含 `solidFillEntityCount=0`、`groupRowVerticalSegmentCount=0`、`rowNumberStyle=arabic`，后续重取景和局部修复可按句柄执行。
- **真实 CAD**：已清理旧表区域并在 `CODEX_PREVIEW` 重画最终版；260/260 handles 回读，问号文本 0、英文混入 0，流式绘制记录 26 个 item complete；最终报告 `output/validation_runs/linetype-table/layout-fix-real/linetype_table_report.json`，截图 `output/previews/linetype-table-layout-fixed-focused-20260602.png`。
- **验证**：`tests.core.test_linetype_table_demo` 3/3 OK；`tests.core.test_linetype_table_demo tests.core.test_cad_foundation_remaining_training` 19/19 OK；`git diff --check` 对本轮文件无空白错误。
- **边界**：本轮只修改预览表生成器、脚本报告和状态记录；真实 CAD 操作只作用于 `CODEX_PREVIEW`，未保存 DWG，未修改正式图层，不提升表 C。

### LOCAL-REPAIR-FIRST-01：原位局部修复优先

- **触发**：用户指出回测校验发现局部错误后，不应每次在旁边重新画完整测试内容；例如文字问号乱码应删改对应文字并在原位置补回，而不是另起一整张表。
- **规则**：新增“原位局部修复优先”：已有上一轮 `execution_summary`、created handles 或 CAD readback 时，先生成 `repair_plan`，按 `target_handles`、`target_bbox`、实体类型和失败原因定位错误对象。
- **允许操作**：用户开放删除编辑命令后，默认只允许对 `CODEX_PREVIEW` 中被证据锁定的错误对象执行 `update`、`delete_replace` 或 `add_missing`；不得扩大为清空整图、全模型空间、全部可见对象、正式图层、保存或覆盖 DWG。
- **训练链路**：feedback fail 后优先原位修复；局部乱码、单条线型错误、某个 hatch 比例不对、局部缺线或标注错位，不得在旁边整套重画。
- **退回重画条件**：只有 handles 失效、对象被炸开 / 删除、局部修复会破坏整体拓扑，或根因来自全局坐标系 / 比例 / 布局时，才允许整块重画，并须先说明原因。
- **边界**：本包只改规则、排障手册和训练链路口径；不连接真实 CAD、不删除现有实体、不保存 DWG、不提升表 C。

### VISUAL-FOCUS-SCOPE-01：截图 / 这里 / 旁边统一为视觉限定锚点

- **触发**：用户澄清“旁边”只是一个例子；截图指示、图片里的标记、或者不截图但说“旁边”，本质都是希望 Agent 按用户当前眼睛看到的 CAD 画面定位。
- **实现**：`core.quick_tasks.nearby_draw` 新增 `visual_context` 与 `input_scope`，识别“截图 / 图片 / 这里 / 看到 / 旁边 / 附近 / 方向词”等视觉限定请求，并把视觉来源、锚点策略、checked / not_checked 写入报告和 `placement_resolution`。
- **CLI**：`scripts/run_quick_nearby_draw.py` 新增 `--visual-source` 与 `--visual-target-hint`，可显式记录 `user_screenshot`、`current_cad_view`、`marked_region` 等来源。
- **阻断**：截图或视觉词不会自动变成 CAD 坐标；没有当前视口、焦点不唯一、或截图像素无法映射到 CAD 视口时仍返回 `blocked` / `needs_confirmation`，不硬猜落图。
- **验证**：`tests.core.test_quick_nearby_draw` 从 2 个扩展到 4 个用例，覆盖“按截图这里画”走 selected/current-view 锚点，以及多焦点当前视口需要确认。
- **边界**：本包提升的是视觉限定请求的路由和证据字段，不运行真实 CAD，不保存 DWG，不证明截图像素到 CAD 坐标映射，不提升表 C。

### QUICK-NEARBY-DRAW-01：旁边快画轻量入口

- **触发**：真实 quick trial 曾因读上下文、查 helper、手写全局 bbox 脚本、误画重画和清理误对象耗时 4 分钟以上；核心慢点不是 CAD 写入，而是没有固定快入口。
- **实现**：新增 `core/quick_tasks/nearby_draw.py` 和 `scripts/run_quick_nearby_draw.py`。入口直接执行 `CAD_VIEW_CONTEXT -> placement_resolution -> CODEX_PREVIEW -> created handles/bbox readback`，默认不写中间 CAD_PLAN / dry-run / 多份 JSON；只有传 `--output-dir` 才保存报告。
- **对象**：当前支持 `sofa / couch / 沙发` 轻量平面符号和通用矩形，沙发默认 `1800 x 750`，控制在 12 个 preview handles，避免超过 quick trial 的 20 对象升级边界。
- **阻断**：读不到当前视口、焦点不唯一或无可用槽位时返回 `blocked` / `needs_confirmation`，不退回全局 `CODEX_PREVIEW` bbox 或远处空白。
- **验证**：`tests.core.test_quick_nearby_draw` 2/2 OK；`tests.core.test_quick_nearby_draw` + `tests.core.test_designer_view_nearby_placement` + `tests.core.test_quick_composite_task` 16/16 OK；`scripts/run_quick_nearby_draw.py --no-cad --phrase "在旁边画个沙发" --object-type sofa` pass，fake end-to-end 约 0.0005s。
- **边界**：提速的是 quick trial 执行路径；真实 CAD 仍受 COM snapshot / draw / readback 影响，不保存 DWG、不删除实体、不提升表 C，不代表用户视觉验收或施工图准确。

### CAD-STYLE-SEMANTICS-CONTRACT-01：CAD 线宽线型颜色语义样式契约

- **触发**：用户指出第 22 项当前只有粗 / 中 / 细三条测试线，远不足以支撑家装家具图块和完整家装方案中的线宽、线型、颜色语义判断。
- **OpenSpec**：新增 `openspec/changes/introduce-cad-style-semantics-contract/`，包含 proposal / design / specs / tasks；新 capability 为 `cad-style-semantics`。
- **契约**：`drawing_standard_profile` 新增 `style_tokens`，`CAD_PLAN.drawing` 新增 `style_token`、`style_role`、`style_resolution`、`entity_style_overrides` 和 `style_assumptions` 等加法字段。
- **默认种子**：`codex_preview_beta` 增加墙体粗连续线、家具中线、家具中心线、家具内部细线、隐藏虚线、标注虚线等 style token；preview-only 仍只写 `CODEX_PREVIEW`，同时保留 `semantic_layer`。
- **证据流**：`apply_drawing_standard_to_plan` 负责解析 token；dry-run 和 preview execution summary 输出 `style_evidence`；`draw_symbol_glyph` primitive 可覆盖局部 style token，用于家具图块内部线条层级。
- **Review 后加固**：独立 Review Agent 指出颜色继承、未解析 token 和颜色回读闭环不足；已补 `by_layer` 不覆盖实体颜色、`style_token` / `layer_role` 冲突拒绝、未解析 `style_token` 校验失败、fake / COM-like readback 保留 `Color`。
- **验证**：`tests.core.test_drawing_standard_profile`、`tests.core.test_execute_plan`、`tests.core.test_symbol_glyph_cad_smoke`、`tests.core.test_validation_edges`、`tests.core.test_verification_report` 48 tests OK；后续 full unittest / OpenSpec / doc audit 见本轮交付。
- **边界**：本包不运行真实 CAD、不保存 DWG、不导出原生绘图标准库、不验证 CTB/STB 或 plot 输出、不提升表 C；截图仍不能替代 CAD 属性回读或打印验证。

### PROMPT-CONTRACT-SHARED-01：共享 Prompt 合同与 addendum 去重护栏

- **触发**：系统主 Agent 与多个 pipeline Agent 的 `prompt_addendum.md` 重复沉淀了同一批 CAD 安全、证据和视觉反馈规则；规则本身正确，但多处分叉会增加后续同步成本。
- **收束**：新增 `agents/COMMON_PROMPT_CONTRACT.md`，统一维护中文标注、画布避让、created handles 回读、`CODEX_PREVIEW`、视觉 / 位置反馈和证据边界等共用规则。
- **生成器**：`core/training/learning_promotion.py` 继续在 `training_memory.json` 保留完整经验，但生成 `prompt_addendum.md` 时过滤共用规则，只写角色专属新增；每个 agent update 的 source refs 同步包含共享合同。
- **工作台契约**：`scripts/build_capability_map_data.py` 让每个 Prompt contract 都引用共享合同；`scripts/sync_training_workbench.py --skip-coverage` 已重建 `capability-map-data.js` 并刷新 learning promotion。
- **护栏**：`scripts/run_training_workbench_agent_check.py` 新增 `common_prompt_contract_referenced` 和 `prompt_addenda_do_not_duplicate_common_rules` 两项检查，防止 addendum 后续重新复制通用规则。
- **验证**：`tests.core.test_training_workbench_sync` + `tests.core.test_training_learning_promotion` 19 tests OK；Agent check 37/37 pass。
- **边界**：本包只治理 Prompt 合同、工作台 source refs 和训练沉淀生成逻辑；不运行真实 CAD、不修改 DWG、不提升表 C。

### DESIGNER-VIEW-NEARBY-PLACEMENT-01：设计师视角“旁边 / 附近”放置语义

- **触发**：用户指出“在旁边画个沙发看看”的“旁边”更接近自己当前眼睛看到的 CAD 视角，而不是全局坐标或全图最右侧空白。
- **OpenSpec**：新增 `openspec/changes/define-designer-view-nearby-placement/`，包含 proposal / design / specs / tasks；新 capability 为 `designer-view-nearby-placement`。
- **实现**：新增 `core/placement/designer_view_nearby.py`，引入 `CAD_VIEW_CONTEXT -> focus_anchor -> placement_resolution -> CAD_PLAN absolute base_point` 链路；新增 `core/schemas/cad_view_context.schema.json` 和 `core/schemas/placement_resolution.schema.json`。
- **规则**：`agents/cad_designer/rules.md` 写入“旁边 / 附近”必须按当前视口、选中对象、最近 handles 或可见内容簇解析；不得先画远再 zoom/pan 伪装同屏可见。
- **验收入口**：新增 no-CAD fixture 和 `tests/core/test_designer_view_nearby_placement.py`；新增 `scripts/run_designer_view_nearby_smoke.py`，真实 CAD 时只写 `CODEX_PREVIEW`，用 created handles / bbox 对原始视口做邻近审计。
- **复盘加固**：本轮真实 quick trial 曾绕过上述入口，手写全局 `CODEX_PREVIEW` bbox 右侧放置脚本，导致沙发落到当前左上视觉焦点很远处；共享 Prompt 合同已补充“邻近词必须走当前视口链路，读不到焦点则 blocked / needs_confirmation，不得临时脚本绕过”。
- **边界**：本包证明的是当前视域邻近放置语义，不训练具体沙发 / 家具对象族，不提升表 C，不替代施工图准确性或用户目视验收。

### SYSTEM-ASSET-SEDIMENTATION-PROTOCOL-01：系统资产沉淀协议

- **触发**：用户明确提出未来会指认当前 CAD 文件中的对象或标准为“通用资产”，希望 Agent 自动知道要放到仓库中的稳定分类资产库，而不是只停留在当前 DWG 或训练报告里。
- **协议**：系统资产沉淀升级为四件套：机器契约、CAD 原生资产位置、应用 / 验收工具、全局索引。说明文档为 `docs/architecture/system-asset-sedimentation-protocol.md`。
- **实现**：新增 `core/assets/system_asset_sedimentation.py` 与 CLI `scripts/sediment_system_asset.py`；支持把点分分类如 `furniture.seating.sofas` 映射到 `libraries/system_library/furniture/seating/sofas/`，连续沉淀同类资产时更新同一个 `assets.json` 和同一个 `*_assets.dwg` 位置。
- **V2/V3 加固**：资产条目新增 `candidate/systemized/verified/deprecated` 状态流、`retrieval` 检索契约、`native.layoutPlan` 分类 DWG 排版槽位、`versioning` 冲突 / 变体记录、`verification` 元数据验收和 `feedbackLoop` 失败回流；V3 追加 `assetKind`、`sourceBoundary`、`exportManifest` 与 `antiContamination`，对象 block export 只允许精确 handles / bbox / named block 来源，样式标准强制走 `style_export`；同 ID 尺寸或 blockName 冲突时可 `update_existing`、`reject` 或 `new_variant`。
- **初始资产包**：新增 `libraries/system_library/registry.json`；登记 `drawing_standards.basic` 包并预留 `standard_assets.dwg`；登记 `furniture.seating.sofas` 包并预留 `sofa_assets.dwg`。
- **边界**：当前实现只登记合同、索引、排版计划和元数据验收，不连接 AutoCAD、不保存 DWG、不导出 block、不删除实体、不修改正式图层；`nativeDwgExists=false` 或 `native DWG geometry` 在 `notChecked` 时不得声称原生 DWG 已沉淀完成。
- **验证**：`tests.core.test_system_asset_sedimentation` 11/11 OK；CLI smoke 在临时 project root 写入 sofa 资产合同并覆盖 block export manifest；`scripts/sediment_system_asset.py --verify --category furniture.seating.sofas` / `drawing_standards.basic` 只验证元数据合同；后续真实 CAD 原生导出需另包接入。

### TRAINING-LINEWEIGHT-LINETYPE-STANDARD-01：第 22 项线宽线型标准复训

- **触发**：用户截图指出第 22 项“线宽线型标准”虽然 CAD 开启了显示线宽，但测试线条实际没有变化，线宽、虚线 / 线型差异都没有被证明。
- **根因**：`cad-layer-lineweight-standard` 面板原先只画三条普通 `draw_line`；`AutoCADComDriver.draw_line` 和 `FakeCadDriver.draw_line` 对传入样式参数没有写入实体属性；训练报告只检查句柄、图层和中文标注，没有回读 `Lineweight` / `Linetype`。
- **修复**：第 22 项样例改为三档真实 CAD 属性：粗线墙体 `Lineweight=70` + 连续线，中线家具 `Lineweight=35` + `CENTER`，细线标注 `Lineweight=13` + `DASHED`，虚线 / 中心线额外设置 `LinetypeScale=25`；真实 AutoCAD driver 支持加载并设置线型，Fake driver 和 `inspect_dwg` 支持回读样式属性。
- **验收加固**：`foundation_batch_training` 新增 `lineweight_linetype_standard` 检查和 item 级 `styleEvidence`，必须回读到 `lineweights=[13,35,70]`、`linetypes=[CENTER,CONTINUOUS,DASHED]`、`linetypeScales=[1.0,25.0]` 才算通过。
- **真实 CAD focused 复训**：只跑 `--only cad-layer-lineweight-standard`，`scope.mode=focused`，1/1 pass、12/12 handles 回读、全部 `CODEX_PREVIEW`、未保存 DWG；报告为 `output/training_queues/cad-foundation-remaining-21/focused/cad-layer-lineweight-standard/remaining_21_report.json`，截图为 `output/previews/task22-lineweight-linetype-focused.png`。
- **边界**：这是基础第 22 项 focused 纠偏和验收闸门加固；不覆盖剩余 21 项整批验收，不提升表 C，不代表完整施工图能力。

## 2026-06-01

### TRAINING-STREAM-DEMO-01：基础训练可选流式演示模式

- **触发**：剩余 21 项基础训练已能高速批量跑完，但旁观时希望看到面板逐步完成和关键图元短暂停顿，而不是只看最终结果。
- **实现**：`scripts/run_cad_foundation_remaining_training.py` 支持显式 `--stream-demo` hybrid streaming；默认高速批量执行不变且不插入 refresh / zoom / delay。流式模式支持面板完成后暂停、演示用 refresh / 可选 zoom，以及每面板有限数量关键图元短暂停顿；典型参数为 `--stream-demo --stream-item-delay 0.35 --stream-operation-delay 0.12 --stream-operation-budget 5`，需要禁用自动缩放时可加 `--stream-no-zoom`。
- **验证**：unit tests / fake CLI smoke 已覆盖流式参数、报告字段和演示检查；真实 CAD smoke 已通过，证据在 `output/validation_runs/stream-demo-real/remaining_21_report.json` 和 `output/previews/stream-demo-real.png`。
- **边界**：流式演示只影响显示节奏，不改变真实验收。通过仍看 `CODEX_PREVIEW` handles/readback、图层守卫、dry-run、watchdog 和报告；不保存 DWG、不覆盖原图、不写正式图层；截图只作 visual aid，不提升表 C。

### TRAINING-LATENCY-ROUTING-01：训练轻重链路量化路由

- **触发**：用户指出“画个正方体 + 填充”这类小动作本应几秒级完成，但实际被套入大量训练验收、截图、同步和沉淀工序，导致链路过重。
- **规则新增**：`AGENTS.md`、`docs/training/README.md`、`docs/governance/cad-agent-rules.md` 和 `agents/cad_designer/rules.md` 写入三档量化路由：`quick_trial`、`focused_retraining`、`formal_acceptance`。
- **量化口径**：`quick_trial` 默认 ≤ 2 分钟，只写 `CODEX_PREVIEW`，最多 1 次 CAD 写入 + 1 次关键回读，跳过完整 validate / dry-run、截图、工作台同步和 learning promotion；`focused_retraining` 默认 ≤ 8 分钟，只覆盖点名能力或显式列表；`formal_acceptance` 才执行完整训练闭环，且每个子动作仍受 30 秒 watchdog。
- **升级条件**：快试若需要修改已有实体、超过 20 个新对象、涉及正式图层 / 保存 / 删除、关键回读失败、用户要求正式准确性或超过 2 分钟仍无关键证据，必须说明原因并升级到 focused / formal，不得静默套重链路。
- **同步 / 验证**：`docs/training/pipeline-changelog.md`、`docs/status/current.md`、`docs/status/issues.md` 和 `CORE_CONTEXT_BRIEF.md` 已登记本规则；`scripts/sync_training_workbench.py` pass，Agent check 35/35 pass。
- **边界**：本包只改规则和链路文档，不运行真实 CAD、不删除旧预览实体、不提升表 C。

### COMPOSITE-TASK-ROUTING-01：未列入计划的复合任务动态编排规则

- **触发**：用户说明未来会临场组合已有能力，例如“截图里的沙发 + 标注尺寸”，但不会把每个组合都写入 V2 训练计划，否则计划会无限膨胀。
- **规则新增**：`AGENTS.md`、`docs/training/README.md`、`agents/cad_designer/rules.md`、`docs/training/cad-designer-growth-path.md` 和 `docs/governance/cad-agent-rules.md` 写入复合任务协议：训练地图只列原子能力和代表性课程，临场组合默认动态编排。
- **链路口径**：复合任务先拆为输入来源、对象 / 场景识别、尺度来源、绘图 / 修改 / 标注意图、`CAD_PLAN` 或结构化意图、validate / dry-run、`CODEX_PREVIEW`、readback / audit。
- **证据边界**：必须声明 `evidence_source`；截图只能证明视觉定位和推断，截图 + 参照尺寸只能做比例估算，只有 DWG / created handles / 原 `CAD_PLAN` / 用户给定尺寸才能进入对应几何或标注审计。
- **沉淀规则**：单次组合不污染 V2 训练地图；只有重复失败、可机器检查、可泛化为课程族或需要稳定验收器时，才晋升训练项、benchmark、检查器或规则包。
- **同步**：`docs/training/pipeline-changelog.md`、`docs/status/current.md`、`docs/status/issues.md` 和 `CORE_CONTEXT_BRIEF.md` 已登记本规则。
- **边界**：本包只改规则和链路文档，不运行真实 CAD、不新增训练项、不提升表 C。

### TRAINING-HATCH-SOLID-SEMANTIC-01：第 12 项箭头语义位置实心填充校正

- **触发**：用户指出“箭头处加强测试”不是在右侧另起模块，而是要读图中箭头 / 蓝圈语义，在原第 12 项面板上方空白处画同尺寸实心填充方块。
- **根因**：第一次落图沿用 focused retraining 停放区逻辑，第二次又用旧 execution summary 坐标，导致 `SOLID` 方块落到右侧模块附近，而不是图三原面板箭头位置。
- **修复**：改为从当前 AutoCAD `CODEX_PREVIEW` 里读取原第 12 项 8 个非 `SOLID` hatch 样本 bbox，反推当前原面板位置和样本边长，再在面板上方箭头语义位置画 1 个同尺寸 `SOLID` 实心正方形。
- **机器证据**：实心方块边长 `245.0`，created handles=`2BF8, 2BF9`，回读 `polyline + hatch` 2/2，`pattern=SOLID`，全部在 `CODEX_PREVIEW`，未保存 DWG、未删除实体。
- **视觉证据**：截图 `output/previews/cad-foundation-12-arrow-solid-fill-corrected.png`；结构化报告 `output/training_queues/cad-foundation-remaining-21/focused/image-arrow-solid-fill-square/report.json`。
- **边界**：保留此前误画在右侧的预览实体，避免未经明确批准删除 CAD 对象；本轮是读图语义定位修正，不提升表 C，不代表完整施工图能力。

### TRAINING-HATCH-FULL-FILL-01：第 12 项全填充 focused 测试

- **触发**：用户要求第 12 项“填充与边界”加强测试全填充情况。
- **脚本修复**：`core/training/foundation_panel_drawings.py` 新增 `SOLID_HATCH_SAMPLES` 与 `hatch_full_fill` 选项，生成 8 个 `SOLID` 实心填充样本；`scripts/run_cad_foundation_remaining_training.py` 新增 `--hatch-full-fill` focused CLI 开关。
- **布局修复**：全填充样本尺寸和标签间距收紧，避免第二排标签与底部“已检查”行叠字；说明文字移到样本网格右侧空白区。
- **验证**：`tests.core.test_cad_foundation_remaining_training` 8 tests OK；真实 CAD focused 复训 1/1 pass、31/31 handles 回读、8 个 hatch、全部 `CODEX_PREVIEW`、未保存 DWG。
- **边界**：这是基础第 12 项 focused 复训入口和视觉样本增强；focused 报告不覆盖整批验收状态，不提升表 C。

### TRAINING-SCOPE-GUARD-01：单项加深训练不得扩大为整批训练

- **触发**：用户指出“任务 12 加深训练”被执行成剩余 21 项整批复跑，超出点名范围；类似地，若用户只给某个填充图案截图要求比例测试，也不应执行范围外动作。
- **硬规则**：`AGENTS.md`、`docs/training/README.md`、`docs/governance/cad-agent-rules.md` 和 `agents/cad_designer/rules.md` 写入训练范围边界：单项 / 子主题默认 focused retraining；只有明确说“全部 / 整批 / 重新跑所有 / 刷新整个队列”才允许 full batch。
- **脚本修复**：`core/training/foundation_batch_training.py` 新增 `selected_capability_ids`、`scopeReason`、`trainingOptions` 和 `anchor_output_dir`；报告、plan、execution summary、queue state 写入 `scope.mode=focused`、`requestedCapabilityIds` 和子参数，且 focused 状态不覆盖整批验收。
- **CLI 入口**：`scripts/run_cad_foundation_remaining_training.py` 新增 `--only`、`--scope-reason`、`--hatch-pattern`、`--hatch-scales`；默认 focused 输出到 `output/training_queues/cad-foundation-remaining-21/focused/<capability_id>/`，并使用整批输出目录作为停放区 anchor 来源。
- **第 12 项子训练**：`core/training/foundation_panel_drawings.py` 支持 hatch pattern focus 和 scale list；例如 `--only cad-hatch-boundary --hatch-pattern ANSI31 --hatch-scales 0.25,0.5,1,2` 只生成该图案的 4 个比例样本。
- **验证**：新增 focused 范围和 hatch 子范围回归测试；fake-cad focused CLI 证明只生成 `cad-hatch-boundary` 1/1，`postTrainingSync=not_required`，不会触发整批重新验收或完整工作台同步。
- **边界**：这是范围控制和轻量复训入口修复；不运行真实 CAD 整批复训，不提升表 C，不删除旧预览实体。

### TRAINING-HATCH-PATTERN-SAMPLES-01：第 12 项填充图样与比例复训

- **触发**：用户要求在当前训练面板附近重新训练第 12 项“填充与边界”，创建 6-10 个小正方形，测试 CAD 常用自带填充图样，并对同一图样做不同比例对比。
- **脚本修复**：`core/training/foundation_panel_drawings.py` 将第 12 项从单个斜线填充升级为 8 个小方格样板，覆盖 `ANSI31`、`ANSI32`、`ANSI37`、`AR-CONC`、`BRICK`、`GRAVEL`、`EARTH`；其中 `ANSI31` 使用 0.45 与 1.1 两种比例对比。
- **回读增强**：`core/cad_io/autocad_com.py` 写入 hatch `PatternScale`；`core/verification/inspect_dwg.py` 回读 hatch `scale`，让 execution summary 能证明图样和比例，而不是只靠截图。
- **真实 CAD 复训**：重跑 `scripts/run_cad_foundation_remaining_training.py`，`parking_anchor.source=previous_handles`，第 12 项 31/31 handles 回读，整轮 257/257 handles 回读、8 个 hatch、全部 `CODEX_PREVIEW`、未保存 DWG、未写正式图层。
- **机器证据**：execution summary 中 hatch patterns 为 `ANSI31, ANSI31, ANSI32, ANSI37, AR-CONC, BRICK, GRAVEL, EARTH`，scales 为 `0.45, 1.1, 0.8, 0.75, 0.7, 0.65, 0.55, 0.6`。
- **验证**：新增/更新 hatch 图样与比例回归测试；相关 26 tests OK；截图刷新为 `output/training_queues/cad-foundation-remaining-21/remaining-21-chinese/remaining_21_preview.png`。
- **边界**：本轮是基础第 12 项填充指令复训，不提升表 C，不代表完整施工图能力；未删除旧预览实体。

### TRAINING-PARKING-ANCHOR-01：训练面板停放区跟随用户移动位置

- **触发**：用户说明会为了查看方便手动移动已训练出的面板，不希望后续复训目标按整个画布最右侧不断漂移。
- **规则新增**：训练复跑应优先读取上一轮 created handles，并以这些 handles 当前回读到的 bbox 作为训练停放区参考；旧 handles 无法回读时，才退回全局 `CODEX_PREVIEW` bbox 或原点。
- **脚本修复**：`core/training/foundation_batch_training.py` 新增 `parking_anchor` 选择逻辑，报告记录 `source=previous_handles / global_preview_bbox / origin`、参考 bbox、basePoint 和回读句柄数。
- **回归测试**：`tests/core/test_cad_foundation_remaining_training.py` 新增模拟：用户移动上一轮训练面板，同时远处存在其它预览实体；二次复训必须跟随上一轮 handles 的新位置，不得被远处实体拖到全画布右侧。
- **边界**：本规则不删除旧预览实体、不保存 DWG、不修改正式图层；若用户炸开、删除或复制重画导致原 handles 失效，脚本只能退回全局 bbox 选区或要求人工确认。

### TRAINING-FOUNDATION-CHINESE-LABEL-RETRAIN-01：基础剩余 21 项中文标注复训

- **触发**：用户截图指出 `CAD 基础操作` 剩余 21 项训练面板仍残留多个英文可见标注，如 `checked`、`handles`、`bbox`、`locked`、`Rev-A`、`AUDIT/PURGE` 和 `checked/not_checked`。
- **根因**：批量训练的 `chinese_labels` 验收只要求每条文字含有中文，无法阻断中英混排；第 29 项标题还从工作台数据源继承了旧的 `handle 与 bbox 报告`。
- **修复**：`core/training/foundation_panel_drawings.py` 将面板可见文案和第 29 项标题改为中文；`scripts/build_capability_map_data.py` 将对应训练项名称 / 焦点改为“句柄与边界框”；`core/training/foundation_batch_training.py` 新增 `latin_terms=0` 运行时验收，报告文案也改为中文。
- **回归测试**：`tests/core/test_cad_foundation_remaining_training.py` 新增可见文字英文术语扫描，覆盖 fake CAD 文本实体和报告标题；相关 20 tests OK。
- **真实 CAD 复训**：重跑 `scripts/run_cad_foundation_remaining_training.py`，21/21 pass、235/235 句柄回读、全部 `CODEX_PREVIEW`、`chinese_labels` 为 `text_labels=65 latin_terms=0`；重新截图 `output/training_queues/cad-foundation-remaining-21/remaining-21-chinese/remaining_21_preview.png`。
- **沉淀与同步**：`scripts/sync_training_workbench.py` pass，Agent check 35/35 pass，learning promotion 31 items / 7 agents；真实输出文本扫描 86 条，英文术语 0 条。
- **边界**：本轮是基础训练中文标注复训和验收闸门加固，不提升表 C，不代表完整施工图能力；未保存 DWG、未写正式图层、未删除正式实体。

### TRAINING-FOUNDATION-REFLOW-RULE-01：基础能力回流复训规则

- **触发**：用户指出复杂任务训练中可能反过来暴露基础功能不扎实，已完成基础训练不应被理解成永久封存交付状态。
- **规则新增**：`AGENTS.md`、`docs/governance/cad-agent-rules.md`、`docs/training/README.md`、`docs/training/cad-designer-growth-path.md` 和 `agents/cad_designer/rules.md` 已写入“基础训练允许回流复训”口径。
- **复训闭环**：复杂任务触发基础缺口后，必须记录触发任务和失败症状，映射到一个或多个基础训练项，修改相关脚本 / Prompt / 检查器 / 规则，重新训练基础项，再回测原复杂任务。
- **证据口径**：旧 `systemized/pass` 证据保留为历史版本；新复训报告追加到 `training-sources.json`、learning ledger、Agent memory / Prompt addendum 和工作台同步链路。
- **边界**：本规则不自动把 CAD 基础操作 31/31 改成未完成，不提升表 C；它只是允许并要求后续发现基本功问题时做二次 / 三次加强训练。

### TRAINING-FOUNDATION-REMAINING-21-01：CAD 基础操作剩余 21 项自动化训练闭环

- **触发**：用户指出训练工作台 `CAD 基础操作` 还有 21 个未完成项，要求写自动化脚本并自行完成训练、验收、沉淀和前端同步。
- **脚本入口**：新增 `scripts/run_cad_foundation_remaining_training.py`；默认连接当前 AutoCAD COM，只写 `CODEX_PREVIEW`，执行剩余 21 项中文训练面板，生成结构化训练计划、dry-run、execution summary、验收报告和队列状态。
- **Core 训练模块**：新增 `core/training/foundation_batch_training.py` 与 `core/training/foundation_panel_drawings.py`，覆盖多段线清理、hatch、boundary、圆角倒角、拉伸、block、xref/layout/plot、红线、线宽线型、选择、阵列、测量、清理、标注、文字引线、handle/bbox、图层污染和安全回滚。
- **验收与安全**：真实 CAD 跑通 `cad-foundation-remaining-21`：21/21 pass，235/235 handles 回读，全部在 `CODEX_PREVIEW`；formal layer write / save / overwrite / delete 均被写保护拦截；单步 watchdog 均低于 30 秒；截图 `output/training_queues/cad-foundation-remaining-21/remaining-21-chinese/remaining_21_preview.png` 已生成。
- **沉淀与前端**：`docs/training/training-sources.json` 登记新队列状态和验收报告；`scripts/sync_training_workbench.py` pass，Agent check 35/35 pass；learning promotion 合计 31 项、7 个责任智能体；工作台中 CAD 基础操作 31/31 已 `systemized/pass`。
- **修复顺手项**：learning promotion 和工作台读取训练验收 JSON 时改用 `utf-8-sig`，避免 PowerShell 或外部工具写入 BOM 后漏接事实源；通用验收检查支持 `all_items_generated`，不再只认历史 `all_10_items_generated`。
- **验证**：`tests.core.test_cad_foundation_remaining_training` 与 `tests.core.test_training_learning_promotion` 合计 6 tests OK；真实 CAD 脚本 pass；`scripts/sync_training_workbench.py` pass。
- **边界**：本包证明 CAD Designer Agent 的基础 CAD 操作训练项已通过并沉淀；不提升表 C，不声明完整施工图能力；截图只作目视辅助，机器结论以 handles/readback/checks 为准。

### REPO-CONTEXT-HYGIENE-02：默认上下文瘦身与训练事实源 manifest

- **触发**：用户担心旧 Core 开发留下太多 MD、旧状态和无关材料，会成为后续 Agent 的上下文负担，要求直接执行小型治理方案。
- **入口收敛**：`AGENTS.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_RESTRUCTURE_PLAN.md` 已统一读取顺序；默认从短入口恢复，只按任务展开 1-2 个文件，不再默认扫 `README`、状态页、handoff 和长期规则全文。
- **历史降噪**：旧表 C 当前值从长期规则移出；`post-backlog.md` 的 99.68% 改为历史快照；旧路线图 stub 改指 `路线图入口.md` / `docs/roadmap/current.md`；Visual-First 旧计划和 shell layout 长文标记为 HISTORY-ONLY。
- **训练事实源**：新增 `docs/training/training-sources.json`，登记队列状态、最终验收报告、learning ledger、Agent memory / Prompt addendum，并明确 `capability-map-data.js`、`capability-map.html` 是派生快照。
- **代码边界**：新增 `core/training/source_manifest.py`；`scripts/build_capability_map_data.py`、`scripts/sync_training_workbench.py` 和 `scripts/run_training_workbench_agent_check.py` 接入 manifest；`core/` 中已清掉对 `scripts/` 的反向导入。
- **收尾验收**：本轮 1-5 子包已按“上下文瘦身、历史降噪、事实源登记、工作台强校验、Core 边界与交接复核”闭环；后续只在新增训练队列或继续拆 `build_capability_map_data.py` 时再开小包。
- **验证**：训练工作台同步 pass，Agent check 35/35 pass；`tests.core.test_training_workbench_sync`、`tests.core.test_training_learning_promotion`、`tests.core.test_script_bootstrap`、`tests.core.test_preview_only_audit`、`tests.core.test_cad_session_guard` 合计 30 tests OK。
- **边界**：本包不移动最终训练证据、不重构 Core 主体、不提升表 C、不新增真实 CAD 几何证明。

### TRAINING-TIMEOUT-CIRCUIT-BREAKER-01：自动化训练 30 秒超时与熔断保护

- **触发**：用户准备未来大面积铺开自动化训练 CAD 任务，要求先写入防长时间卡住的保护机制，默认 30 秒限定，出问题时 Agent 先自己尝试解决。
- **规则新增**：`AGENTS.md`、`docs/governance/cad-agent-rules.md`、`docs/training/README.md` 和 `agents/cad_designer/rules.md` 已写入单步 watchdog：CAD / 脚本 / 截图 / 回读 / 同步子动作默认最多等待 30 秒。
- **自救边界**：超时后先读取 stdout / stderr、最近报告、队列状态和 CAD 会话状态，判断 CAD 窗口、COM 可见性、文件锁、路径、依赖、截图工具或快照过期等问题；同类重试最多 1 次，或最多 2 个相邻恢复动作。
- **熔断条件**：同一训练项连续 2 次 30 秒超时，或同一队列连续 3 个子动作超时 / 失败，必须暂停到 `blocked` / `needs_user_review` 或等价状态。
- **记录要求**：脚本输出或训练记录应包含 `timeoutSeconds: 30`、`selfRecoveryAttempted`、`circuitBreakerTriggered`、`blockedReason`、卡点、自救动作、保留证据和下一步建议。
- **边界**：本包是规则层保护，未把所有训练执行器改成强制 timeout wrapper；后续脚本实现必须按此口径落字段和状态。

### TRAINING-ARTIFACT-RETENTION-01：训练产物最小保留规则

- **触发**：用户指出不希望每次训练后堆积一批测试脚本和临时产物，要求写规则，并确认第一批 10 项测试是否记录了错误点和优化点。
- **现状检查**：`output/training_queues/cad-foundation-first-10/` 当前没有遗留 `.py` 一次性脚本，主要是队列状态、最终 10 项验收报告 / 预览图，以及少量中间 retry / execution summary；总量约 300KB。
- **保留规则**：`AGENTS.md`、`agents/cad_designer/rules.md`、`docs/training/README.md` 已写入训练产物保留策略：长期只保留最终验收报告、队列状态、learning ledger / Agent memory / Prompt addendum 和最近一份人工复核预览图。
- **清理规则**：中间 retry 目录、临时 `CAD_PLAN` / dry-run / execution summary、旧截图和一次性脚本应在验收沉淀后清理；删除前必须确认最终报告、工作台数据、learning ledger、Agent memory 和 `training-errors.md` 不再引用这些路径。
- **第一批教训记录**：第一项默认 probe 语义不明、等待久、重叠已有图块的失败已写入 `docs/training/training-errors.md`；10 项通过后的通用优化点已写入 `output/training_learning/agent_learning_ledger.json` 和责任智能体 Prompt addendum。
- **边界**：本包只新增保留 / 清理规则，未实际删除第一批证据文件；当前最终验收报告仍被工作台和 learning ledger 引用，不能直接删。

### TRAINING-QUEUE-AUTO-SYNC-01：训练脚本通过后自动收尾同步

- **触发**：用户不希望每次训练验收后都口头提醒“同步前端 / 沉淀 Prompt / 更新工作台”，要求检查是否已有机制并写入总脚本或训练规则。
- **现状判断**：`scripts/sync_training_workbench.py` 已是总收尾入口，负责 learning promotion、`capability-map-data.js` 重建、coverage 刷新和 Agent check；缺口在训练队列入口 `scripts/run_training_queue.py`，它原先只推进队列状态，不自动调用收尾同步。
- **脚本修复**：`scripts/run_training_queue.py` 新增 `run_training_queue()` 包装函数；`--decision pass` 后自动调用 `sync_training_workbench`，中间项用轻量同步，队列 `completed` 后跑完整同步；JSON 输出新增 `postTrainingSync`。
- **调试开关**：新增 `--no-post-sync`，仅用于调试或隔离测试；正常训练不得要求用户手动再同步。
- **规则同步**：`AGENTS.md`、`agents/cad_designer/rules.md`、`docs/training/README.md` 已写明训练脚本记录 `pass` 或 `completed` 后必须自动收尾。
- **验证**：`tests/core/test_training_queue_runner.py` 新增 post-sync 行为测试；训练队列、工作台同步和 learning promotion 相关测试 20/20 OK；`scripts/sync_training_workbench.py` pass，Agent check 31/31 pass。
- **边界**：自动同步只保证训练工作台、Agent 记忆和 Prompt 沉淀闭环；不新增真实 CAD 几何证明，不提升表 C。

### TRAINING-WORKBENCH-STAGE-PROMOTION-01：学习沉淀后训练阶段显示 5/5

- **触发**：用户指出前端仍显示“第 4/5 阶段”，容易理解成训练还没结束。
- **修复**：`scripts/build_capability_map_data.py` 的阶段状态现在区分“已通过验收但未沉淀”（4/5 用户反馈通过）和“已通过验收且已 promotion 到责任智能体”（5/5 已沉淀）。
- **测试**：`tests/core/test_training_workbench_sync.py` 新增断言，已学习沉淀的训练项必须生成 `stageState.id=systemized`、`rank=4`、`label=已沉淀`。
- **验证**：相关工作台与 learning promotion 单测 13/13 OK；`scripts/sync_training_workbench.py` pass，Agent check 31/31 pass；浏览器本地页面显示“已沉淀 / 第 5/5 阶段”。
- **边界**：5/5 只表示本训练项已验收并沉淀到训练规则 / Prompt，不提升表 C，不等于完整施工图能力。

### TRAINING-WORKBENCH-PLAIN-ACCEPTANCE-01：训练通过文案改为用户可读白话

- **触发**：用户指出前端“已通过训练 / 用户反馈通过”仍展示后台验收报告路径和沉淀文件，无法直接看懂这项训练到底学会了什么。
- **数据口径**：`scripts/build_capability_map_data.py` 为训练验收结果新增 `plainLanguageSummary`，阶段说明和训练轨道说明改为“中文标注、CODEX_PREVIEW、handles 回读、未保存 DWG、未写正式图层”等白话证据摘要。
- **学习沉淀口径**：`core/training/learning_promotion.py` 的 `build_learning_index()` 现在给每个已沉淀能力生成 `plainLanguageSummary` 和 `visibleLessons`，前端展示规则教训，不展示后台 source refs。
- **前端展示**：`capability-map.html` 的“已学习 / 训练沉淀”展示改为责任智能体吸收经验和可执行规则摘要，移除可见的“沉淀文件：...”路径。
- **同步门槛**：`scripts/run_training_workbench_agent_check.py` 新增 `accepted_training_has_plain_language_summary` 与 `accepted_training_visible_text_hides_backend_paths`；已验收训练若缺白话摘要或可见文案含 `.json` / `output/`，工作台同步失败。
- **验证**：相关 `tests/core/test_training_workbench_sync.py` 与 `tests/core/test_training_learning_promotion.py` 共 13/13 OK；`scripts/sync_training_workbench.py` pass，Agent check 31/31 pass；浏览器打开本地工作台后，基础图元行显示白话摘要且未出现后台路径。
- **边界**：后台仍保留 source refs 供机器追溯；本包只提升前端可读性和回归校验，不提升表 C，不代表新增真实施工图能力。

### TRAINING-LEARNING-PROMOTION-01：训练验收后的智能体沉淀闭环

- **触发**：用户指出前 10 项基础训练测试文件已经构成验收，但工作台和智能体契约没有强制把验收结果沉淀为 Agent 经验、Prompt 优化和责任智能体状态，存在“前端显示通过但智能体没有变聪明”的风险。
- **沉淀管道**：扩展 `core/training/learning_promotion.py`，新增 `promote_training_acceptance()` 和 `build_learning_index()`；通过的训练报告会写入 `output/training_learning/agent_learning_ledger.json`，并为涉及的责任智能体生成 `training_memory.json` 和 `prompt_addendum.md`。
- **同步入口**：新增 `scripts/promote_training_acceptance.py`；`scripts/sync_training_workbench.py` 现在会先执行 learning promotion，再重建 `capability-map-data.js` 和 Agent check。
- **前端状态**：`scripts/build_capability_map_data.py` 将 `trainingLearning`、`learningPromotion`、Agent learning refs 和 Prompt source refs 写入工作台数据；`capability-map.html` 在训练阶段、责任智能体 chip 和详情面板显示“已学习 / 已沉淀 Prompt”。
- **硬门槛**：`scripts/run_training_workbench_agent_check.py` 新增 `accepted_training_has_learning_promotion`、`agent_learning_refs_exist`、`prompt_contracts_include_learning_refs`、`html_learning_promotion_present` 检查；有已验收训练但缺学习沉淀时，前端同步必须失败。
- **Agent 契约**：`agents/cad_designer/agent.json` 和 `agents/cad_designer/rules.md` 明确每次验收后必须执行 learning promotion；不得只改前端状态。
- **验证**：`tests/core/test_training_learning_promotion.py`、`tests/core/test_training_workbench_sync.py`、`tests/core/test_training_queue_runner.py` 合计 18/18 OK；`scripts/sync_training_workbench.py` pass，Agent check 29/29 pass；当前中文 10 项验收沉淀到 7 个责任智能体。
- **边界**：本包证明训练验收会更新 Agent 经验 / Prompt / 前端阶段；不提升表 C，不代表完整施工图能力。

### TRAINING-QUEUE-FOUNDATION-10-01：CAD 基础前 10 项监督式训练队列

- **触发**：用户希望框选的 10 个 CAD 基础操作训练项不再逐条口头启动，而是通过一个监督式自动训练队列推进；Codex 和 CAD 会保持打开，卡壳时由对话框提示验收内容和下一步操作。
- **队列入口**：新增 `core/training/queue_runner.py` 与 `scripts/run_training_queue.py`；默认预设 `cad-foundation-first-10` 覆盖 `cad-primitives`、`cad-selection-edit`、`cad-transform`、`cad-offset-trim`、`cad-layer-discipline`、`cad-closure-constraints`、`cad-readback-audit`、`cad-units-scale`、`cad-coordinate-input`、`cad-osnap-ortho-polar`。
- **监督式状态机**：状态写入 `output/training_queues/cad-foundation-first-10/queue_state.json`；每次只暂停在 1 个训练项，输出 humanMessage、reviewChecklist 和下一步命令；用户通过 `--decision pass` 推进，通过 `--decision fail --feedback ...` 阻塞并回到反馈修复。
- **安全边界**：队列脚本只编排训练，不无人值守保存或覆盖 DWG；真实落图仍必须只写 `CODEX_PREVIEW`，并保留 validate、dry-run、handles 回读、审计和用户验收。
- **文档同步**：训练 README、任务清单和短上下文新增“跑前 10 项队列 / 监督式基础队列”口令。
- **测试**：新增 `tests/core/test_training_queue_runner.py`，覆盖预设 10 项、首次暂停、pass 推进、fail 阻塞和 CLI JSON 输出；目标测试 5/5 OK。
- **边界**：这是训练编排脚本，不新增真实 CAD 几何证明、不提升表 C、不表示 10 项已训练通过。

### TRAINING-WORKBENCH-FOUNDATION-ASSET-NA-01：基础 CAD 操作与资产沉淀口径拆分

- **触发**：用户指出基础图元、选择编辑等 L0 训练不应被计划表暗示为需要标准图块或自产资产沉淀。
- **数据口径**：`scripts/build_capability_map_data.py` 对 `kind=foundation` 的训练项新增 `not_applicable / 不适用` 状态；`raw`（图库）和 `system`（自产）不再显示“未纳入”，而是明确“不需要标准图块 / 不沉淀为自产资产”。
- **成功门槛**：基础操作训练的 `successCriteria` 改为结构化意图 / `CAD_PLAN`、created handles、entity type、bbox、关键端点、闭合 / gap / open endpoint、`CODEX_PREVIEW` 图层安全和审计证据。
- **页面同步**：`capability-map.html` 支持 `not_applicable` 标签和样式；已运行 `scripts/sync_training_workbench.py` 重建 `capability-map-data.js`，Agent check 25/25 pass。
- **文档同步**：训练 README、V2 训练计划、成长路径、任务清单和 `agents/cad_designer/rules.md` 明确：基础操作中的 `block` 指命令 / 引用机制，不等于标准图块资产；基础课程默认沉淀 Prompt、检查器、失败经验或规则，不进入 `system_library`。
- **测试**：`tests/core/test_training_workbench_sync.py` 新增基础操作不要求资产库断言，并复跑该测试文件 9/9 OK。
- **边界**：这是计划表逻辑修正，不新增真实 CAD 几何证明、不提升表 C、不表示基础课程已经训练通过。

### DESIGNER-TRAINING-BATCH-CHECKERS-01：V2.1 训练批次依赖图与验收器骨架

- **触发**：用户确认 V2 后继续推进，但要求不要把训练计划写成固定天数，而是按原逻辑改训练计划表。
- **数据结构**：`scripts/build_capability_map_data.py` 新增 `trainingBatches` 和 `validationCheckers`，把 217 项组织成 8 个批次，并登记 10 个机器验收器 skeleton。
- **批次口径**：批次按能力依赖推进：基础生产卫生 → 安全编辑与图层纪律 → 高频家具符号 → 储位厨卫对象 → 房间平面组合 → 图纸表达与局部套图 → 标注表格与低噪声交付 → 跨图纸交付闭环。
- **验收器口径**：骨架覆盖图层安全、闭合几何、handles 回读、净距碰撞、开启域、厨房工作三角、尺寸链、跨图一致性、表格数量和 checked/not_checked。
- **校验**：`scripts/run_training_workbench_agent_check.py` 新增批次、训练项、前置依赖和验收器引用校验；`tests/core/test_training_workbench_sync.py` 新增批次 / 验收器结构测试。
- **边界**：V2.1 只组织训练顺序和应检项；这些 checker 仍是 skeleton，不是已实现 CAD proof，不提升表 C。

### DESIGNER-TRAINING-PLAN-V2-01：正式训练前训练地图扩容

- **触发**：用户确认正式训练前不希望边训练边扩计划，要求按真实设计师成长路径和市场需求，把现有工作台分类扩成大体量训练地图。
- **调研方式**：并行拆出市场岗位需求、设计师教育路径、家装 CAD 交付物、家具对象库 / 人体工学四个视角；来源包括 BLS / O*NET、CIDA / NCIDQ、NKBA、AutoCAD 课程、室内施工图清单、GB 住宅空间功能和 CAD block 分类。
- **数据扩容**：`scripts/build_capability_map_data.py` 新增 V2 训练 seed 生成器，保留 `CAD 基础操作 / 基础家具 / 储位家具 / 厨卫对象 / 基础绘图 / 标注表达` 六类筛选，总训练计划项从 32 扩到 217。
- **训练体量**：V2 后分类计数为 CAD 基础操作 31、基础家具 46、储位家具 29、厨卫对象 36、基础绘图 43、标注表达 32。
- **文档同步**：新增 `docs/training/cad-designer-training-plan-v2.md`，并更新成长路径、训练 README、任务清单、短上下文和状态页。
- **测试**：`tests/core/test_training_workbench_sync.py` 新增 `test_training_plan_v2_has_large_scale_coverage`，先红后绿，锁住大体量覆盖、分类底线、关键训练项和 ID 去重。
- **边界**：V2 是训练地图扩容，不新增真实 CAD 几何证明、不提升表 C、不声明已会完整施工图；HTML 快照仍必须由 `scripts/sync_training_workbench.py` 同步生成。

### PRE-TRAINING-REPO-SWEEP-01：正式训练前仓库级 Bug 筛查与收尾

- **触发**：正式进入训练前，要求做一次仓库级 Bug 筛查、润色修复和收尾。
- **根因 1**：当前 Windows / 沙箱环境下，Python `tempfile.TemporaryDirectory()` / `mkdtemp()` 创建的目录会出现后续写入 `PermissionError`；这会让 raw intake、session guard、preview-only audit 等测试误红，但业务代码本身没有写错。
- **修复 1**：新增 `tests.helpers.temporary_artifact_dir()`，改用 `output/test_artifacts/` 下普通 `Path.mkdir()` 创建的可写临时目录，并切换 `test_asset_raw_intake`、`test_cad_session_guard`、`test_preview_only_audit`。
- **根因 2**：`test_agent_check_cli_validates_generated_snapshot` 直接校验根目录 `capability-map-data.js`；全量测试或 coverage 刷新后，静态快照可能早于 coverage JSON，导致测试顺序相关失败。
- **修复 2**：该测试先生成自己的临时 `capability-map-data-agent-check.js`，再调用 `run_training_workbench_agent_check.py --data ...` 校验；根目录工作台新鲜度仍由 `sync_training_workbench.py` 和实际 Agent check 负责。
- **同步**：复跑 `scripts/sync_training_workbench.py`，刷新 coverage、`capability-map-data.js` 和 `output/validation_runs/training-workbench-sync/*`，Agent check 20/20 pass。
- **验证**：全量 `unittest discover -s tests` 1050 OK；`run_doc_governance_audit.py` pass；`run_capability_coverage.py` pass；`sync_training_workbench.py` pass；`run_training_workbench_agent_check.py` pass；`openspec.cmd validate --all --strict --json --no-interactive` 4/4 pass；`git fsck --full --strict --no-dangling` pass；冲突标记扫描无命中；`run_core_platform_gate.py --skip-unittest` pass。
- **剩余风险**：`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 仍因 7 个 low `large_python_file` findings 返回 1；`run_dev_volume_audit.py` 仍因生成快照大 delta 报 low findings；两者均已登记，未作为本轮阻塞训练的运行时 bug。
- **边界**：未运行真实 CAD，未修改或保存用户 DWG；本轮不新增真实 CAD 几何证明、不提升表 C，只修训练前仓库健康和同步可靠性。

### OPENSPEC-SYSTEM-CONTRACT-01：OpenSpec 初始化可用性与系统契约润色

- **触发**：用户要求初始化 OpenSpec 确保能用，并再次润色系统契约、判断是否有必要优化。
- **复核结论**：OpenSpec 已可用；`openspec.cmd list --json` 能列出 completed changes，逐 change `status --json` 正常，`validate --all --strict --json --no-interactive` 通过；`status --json` 不带 `--change` 报错是 CLI 用法边界。
- **契约润色**：新增 `openspec/README.md`，更新 `openspec/config.yaml`、`AGENTS.md` 和 `CORE_RESTRUCTURE_PLAN.md`，明确 readiness 命令、completed changes 与 main specs 关系、归档引用边界。
- **OpenSpec**：新增 `openspec/changes/polish-openspec-system-contract/`，包含 proposal / design / spec / tasks；新增 capability `openspec-readiness-contract`。
- **边界**：本包不归档旧 change、不改 CAD 执行、不改表 C、不把 OpenSpec 变成第二套 PlanMD。

### DESIGNER-AGENT-GROWTH-PATH-01：总设计师 Agent 成长路径

- **触发**：用户确认仓库改动方案走 B 中改：新增总 Agent，把其它智能体作为知识储备和流程能力；第一阶段毕业目标走 C，但第一批训练课程从 A 的 CAD 基础能力开始铺。
- **OpenSpec**：新增 `openspec/changes/introduce-designer-agent-growth-path/`，包含 proposal / design / spec / tasks；新增 capability `designer-agent-growth-path`。
- **Agent 契约**：新增 `agents/cad_designer/agent.json` 与 `agents/cad_designer/rules.md`，定义 CAD Designer Agent 的第一阶段毕业目标、基础课程、可调用 pipeline Agent 和证据边界。
- **成长文档**：新增 `docs/training/cad-designer-growth-path.md`，固定 L0-L6 成长阶段、第一阶段“电子设计师雏形”和 7 个 L0 基础课程。
- **工作台数据**：`scripts/build_capability_map_data.py` 新增 `designerAgent`、`growthStages`、`foundationCourses`，并把 `cad-primitives`、`cad-selection-edit`、`cad-transform`、`cad-offset-trim`、`cad-layer-discipline`、`cad-closure-constraints`、`cad-readback-audit` 纳入能力矩阵。
- **页面口径**：`capability-map.html` 顶部和证据边界改为 CAD Designer Agent 的能力护照视角，新增 `CAD 基础操作` 分组。
- **测试**：新增 focused 断言 `test_designer_agent_growth_path_declared`，先红后绿，确保总设计师 Agent、成长阶段和基础课程进入工作台快照。
- **边界**：本包不新增真实 CAD 几何证据、不提升表 C、不声明系统已经会画完整施工图；基础课程通过只表示训练路径进度。

### CAPABILITY-MAP-SYNC-01：训练工作台同步与 Agent 校验

- **触发**：用户确认训练工作台要成为日常训练计划入口，要求 HTML 能同步显示最新训练状态和真实能力边界，并在收尾前创建 Agent 校验防止跑偏。
- **同步链路**：新增 `scripts/sync_training_workbench.py`，默认先运行 `run_capability_coverage` 刷新表 C coverage，再重建 `capability-map-data.js`，最后运行 Agent 校验并输出 `output/validation_runs/training-workbench-sync/training_workbench_sync_report.json` / `.md`。
- **Agent 校验**：新增 `scripts/run_training_workbench_agent_check.py`，检查 schema v2、训练计划、责任智能体 profile / prompt contract、Prompt source refs、表 C headline 与 coverage JSON、快照生成时间、同步命令、启动入口和页面同步提示。
- **启动入口**：新增 `start_training_workbench.bat`，双击后先同步，再用本地 `http.server` 打开 `http://127.0.0.1:8765/capability-map.html`；页面在 HTTP 模式下轮询 `capability-map-data.js`，发现新快照时提示刷新。
- **数据修复**：`scripts/build_capability_map_data.py` 改为从 `agents/pipeline/pipeline_manifest.json` 推导 pipeline source refs，从 `agents/demand_side/role_agents.json` 绑定需求侧角色，修复旧的 `agents/pipeline_execute/agent.json` 等不存在路径。
- **前端润色**：`capability-map.html` 顶部新增同步状态条，显示 HTML 快照时间、表 C coverage 时间、同步命令和刷新入口；继续强调训练阶段 / Prompt 契约不等于真实 CAD 几何通过。
- **规则同步**：`AGENTS.md` 增加训练工作台同步规则；`README.md`、`CORE_CONTEXT_BRIEF.md`、状态 / issues / handoff 同步入口与边界。
- **验证**：TDD 新增 focused 测试 `tests/core/test_training_workbench_sync.py` 先红后绿，5 tests OK；`scripts/sync_training_workbench.py` pass，Agent 校验 17/17 pass，表 C headline 90.99%。
- **边界**：本包只保证 HTML 快照能被同步并校验不跑偏；不新增真实 CAD 几何证据，不提升表 C，不替代 `CODEX_PREVIEW`、created handles 回读、审计和用户反馈。

### ARCH-BOUNDARY-HARDENING-01：架构瘦身与边界加固 01

- **触发**：用户认可“不要做系统重构 2.0”，要求按“架构瘦身与边界加固 01”收束当前架构：区分稳定 Core、训练实验和 case 代码，并先处理 verification、capability-map、资产闭环和 `projects/.../runs` 晋升边界。
- **OpenSpec**：新增 `openspec/changes/architecture-boundary-hardening-01/`，包含 proposal / design / specs / tasks；新增 capability `module-boundary-contract`，明确该 change 不是第二套主计划。
- **架构快照**：新增 `docs/architecture/current-module-boundaries.md`，固定 `Stable Core`、`Training Experiments`、`Case-Only` 三桶；为 `core/verification/` 定义 `report contract`、`runner`、`registry writeback`、`visual audit`、CAD/session safety 拆分图；为 capability map 定义 data generator、page shell、display configuration 和证据边界拆分图。
- **对象资产试点**：选择 `projects/residential_sofa_2seat_20260528` 作为首个对象族候选，但明确必须走 `raw reference -> knowledge summary -> candidate -> executable check -> system asset -> CAD_PLAN -> readback`，不能把 raw reference 或 candidate 直接当系统资产。
- **守护测试**：新增 `tests/core/test_architecture_boundary_hardening.py`，检查架构快照可发现、三桶分类、拆分图、对象资产试点、case-run 晋升门槛和 OpenSpec 不替代 `CORE_RESTRUCTURE_PLAN.md`。
- **收尾修复**：`core/verification/render_preview.py` 的 optional module 检测补上 `ModuleNotFoundError` 降级；系统 Python 缺少 `PIL` 时 screenshot tooling 只进入 warn，不再让 self-check 或 wrapper 测试异常失败。
- **验证**：新增边界测试 5 OK；失败集复测 19 OK；CAD-MCP venv 全量 `unittest discover -s tests` 1044 OK（2 skipped）；`run_doc_governance_audit.py` pass；CAD-MCP venv `scripts/self_check.py` pass。
- **边界**：本包是收束契约和守护测试，不是大规模移动代码；未改变 CAD 执行、registry、表 C 或真实 CAD 证据。

### REPO-POWER-LOSS-HEALTH-01：断电后仓库健康检查与测试契约修复

- **触发**：用户说明电脑刚刚断电，要求整体检查仓库是否有文件受损，并修复需要修的地方。
- **检查**：`git fsck --full --strict --no-dangling` 通过；全仓库冲突标记扫描无命中；JSON 文件解析 0 error；UTF-8 抽检确认中文上下文文件未损坏；非测试产物 0 字节文件仅有临时服务输出日志 `tmp-capability-map-server.out.log`。
- **根因**：全量单测最初失败不是 Git 损坏，而是迁移后的契约未同步：self-check 仍查旧英文根级文件名，pipeline 测试未纳入 `pipeline_asset_retriever`，round12 测试仍按旧“允许交付”口径断言，RCAD-20/21 live contract 在本机缺少未随仓库携带的真实 CAD JSON 时不应伪造证据。
- **修复**：更新 `core/verification/self_check.py` 的 required files；同步 `tests/core/test_planmd_governance.py`、`tests/agents/test_pipeline_visual_contracts.py`、`tests/core/test_visual_parts_case_contract.py`、`tests/core/test_vproof_51_negative_cad.py`、`tests/core/test_vproof_52_guard_cad.py`；修复 `tests/core/test_route_audit_report.py` 每次全量测试重写 tracked 示例 JSON 时间戳的副作用。
- **收尾**：`.gitignore` 增加 `tmp-*.log`，让本地临时服务日志不再污染工作区；状态页最近门禁同步为 1039 tests OK（2 skipped）。
- **验证**：目标失败集 40 tests OK（2 skipped）；全量 `python -m unittest discover -s tests` 1039 tests OK（2 skipped）；`scripts/self_check.py` pass；`git diff --check` 仅有 Windows 换行提示。
- **边界**：未补造真实 CAD 证据；RCAD-20/21 对应 JSON 不在当前工作区时只跳过 live contract；不改变表 C、不运行真实 CAD、不保存或修改用户 DWG。

## 2026-05-31

### CAPABILITY-MAP-TRAINING-WORKBENCH-03：训练计划表单与智能体 Prompt 工作台

- **触发**：用户指出“CD / CAD 能力训练看板”越改越复杂，真正需要围绕训练计划和智能体 Prompt，看清不同能力项训到哪、谁负责、下一轮怎么练，以及每个智能体 Prompt 和调用能力成熟度如何调整。
- **方案**：保留用户认可的能力矩阵分组（基础家具 / 储位家具 / 厨卫对象 / 基础绘图 / 标注表达），默认首页改为“训练计划表单”；第二主视图改为“智能体 Prompt 工作台”，左侧选智能体、右侧看当前 Prompt 描述、职责边界、输入输出、硬门槛、禁止事项、调用契约、可调 Prompt 点和源文件入口。
- **数据生成**：`scripts/build_capability_map_data.py` 升级到 schema v2，新增 `trainingStageColumns`、`trainingPrograms`、`agentProfiles`、`promptContracts`、`tableCBoundary`；为 pipeline / scene / demand 智能体生成自然中文 Prompt 契约，避免前端展示英文碎片。
- **前端重构**：`capability-map.html` 改为训练工作台：桌面端固定列宽展示能力矩阵和右侧训练详情；移动端隐藏宽表格，改用训练计划卡片展示阶段、下一轮训练、责任智能体和四条沉淀轨道；智能体页前置“本轮最值得调的 3 条 Prompt”。
- **口径修正**：`Prompt 已定义` 改为 `目标已声明`；训练阶段显示 `第 x/5 阶段` 而非伪百分比；智能体卡片改为 `契约完整度 / 调用契约 / 训练覆盖面 / 证据状态`，并显示依据和缺口；表 C 顶部降权为机器快照，完整解释放入证据边界。
- **验证**：已跑 `build_capability_map_data.py`、`py_compile`、`node --check capability-map-data.js`、HTML 内联脚本语法检查；Chrome DevTools 验证桌面计划页、桌面智能体页、移动计划页、移动智能体页截图，移动端无明显文本溢出。
- **边界**：本包只改训练看板可视化和生成数据，不改变表 C、registry、真实 CAD 能力、CAD 执行链路或用户 DWG；页面里的阶段和契约分只用于训练调度与 Prompt 调整。

## 2026-05-29

### CAPABILITY-MAP-AGENT-COCKPIT-02：智能体控制台详情弹窗

- **触发**：用户指出能力看板里的智能体清单仍不可控，无法知道每个 Agent 背后的 JSON / MD / prompt 规则、运作架构和可优化点。
- **执行**：`capability-map.html` 的智能体卡片改为可点击详情弹窗，新增“运作架构 / 规则提示词 / 可优化点 / 文件翻译”四个视图；卡片不再用 `+数字` 折叠智能体信息。
- **数据生成**：扩展 `scripts/build_capability_map_data.py`，从 `agents/**/agent.json`、`rules.md`、pipeline doc 和 demand role 数据生成中文职责、输入输出、通过门槛、禁止事项、文档含义、改动建议和优化提示；重建 `capability-map-data.js`。
- **验证**：已跑生成器、`py_compile`、`node --check capability-map-data.js`、HTML 内联脚本语法检查和数据断言；浏览器插件因当前额度限制未能完成点击截图验证。
- **边界**：本包只做控制台可视化和数据快照，不直接编辑源 JSON/MD，不改变真实 CAD 能力表 C，不替代 validate / dry-run / CODEX_PREVIEW / 回读 / 截图链路。

### CAD-ASSET-RAW-INTAKE-AUTO-01：标准图库自动 raw intake

- **触发**：用户明确希望只告诉 Agent “文件夹是什么、里面大概是什么”，不再手填来源 / 授权 / 对象范围 / 图纸类型表格；同时要求优化链路和 Agent prompt 定义。
- **执行**：新增 `core/assets/raw_intake.py` 与 `scripts/run_asset_raw_intake.py`，从 `standard_cad_library_raw/<source_slug>/original/` 自动扫描有效文件，保守推断 `object_tags`、`view_type`、`domain`、`part_tags`，并生成 `source_note`、reference source、单对象 `reference_asset` JSON、`agent_inferred` annotation 和 `knowledge/source_notes`。
- **Agent / 文档**：更新 `asset_retriever`、`context_curator`、`orchestrator` 和 `pipeline_manifest`，把 `standard_library_intake` 设为非绘图分支；重写 asset intake 模板和 raw README，明确“用户只需放文件夹 + 一句说明，Agent 先扫，不追表”。
- **测试**：新增 `tests/core/test_asset_raw_intake.py`，覆盖跳过锁文件、保守默认、schema 校验、不写 `system_library` 和路径穿越拦截；补齐 asset / retrieval schema invalid fixtures。
- **边界**：自动 intake 不解析 CAD 几何、不导入真实图库、不晋升自产资产、不改变表 C；推断错误时以 `unknown` / `reference_only` 保守落库。

### OPENSPEC-CONTRACT-LITE-01：OpenSpec 变更契约轻量护栏

- **触发**：用户要求参照 `CodeGraph + OpenSpec` 重大项目治理表单和截图建议，做一个不破坏现有主线的小型架构升级，重点提升变更契约能力。
- **执行**：新增 OpenSpec change `establish-change-contract-lite`，包含 proposal / design / tasks / specs；在 `AGENTS.md` 与 `CORE_RESTRUCTURE_PLAN.md` 明确 OpenSpec 只作为复杂变更契约层；新增 `check_openspec_contracts()` 并接入 `build_doc_governance_report()`。
- **机器护栏**：doc governance 现在会检查根级 `openspec/tasks.md`、缺少 `CORE_RESTRUCTURE_PLAN.md` 边界的 OpenSpec config，以及 active change 自称主计划 / 总 backlog。
- **边界**：不改 CAD 执行逻辑、不改表 C、不改训练案例、不迁移历史文档；本包是治理小优化，不是 OpenSpec 接管仓库。

### ROOT-MD-CHINESE-NAMES-01：根目录历史入口中文化

- **触发**：用户指出根目录很多 Markdown 文件名仍停留在早期开发阶段，无法一眼判断用途，要求先把根目录大量 MD 改成中文说明。
- **执行**：将 10 个根目录历史 stub 改为中文文件名：`CAD自动验证入口.md`、`CAD卡壳排障入口.md`、`变更记录入口.md`、`问题风险入口.md`、`长期规则入口.md`、`当前状态入口.md`、`路线图入口.md`、`CAD符号语法入口.md`、`训练错误记录入口.md`、`视觉优先训练计划入口.md`。
- **同步**：更新 `core/maintenance/doc_governance.py` 和 `tests/core/test_doc_governance.py` 的 root stub 检查清单；保留 `AGENTS.md`、`README.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_STATUS.md` 这些机器入口不改名。
- **边界**：本包只做文件名可读化，不重写 stub 正文，也不改变训练链路、表 C 或 CAD 能力。

### OPENSPEC-INIT-01：根目录 OpenSpec 初始化

- **触发**：用户要求在当前根目录初始化 OpenSpec，用于后续复杂变更的 proposal/spec/design/tasks 契约化。
- **执行**：运行 `openspec.cmd init . --tools none` 创建 `openspec/changes/`、`openspec/changes/archive/`、`openspec/specs/`；新增 `openspec/config.yaml` 和 `.gitkeep`，让初始化结果可随仓库迁移。
- **定位**：OpenSpec 只作为单个复杂变更的契约层；`CORE_RESTRUCTURE_PLAN.md` 仍是唯一 `PlanMD` / 主计划，`openspec/changes/*` 不承载第二套总 backlog。
- **验证**：`openspec.cmd list --json` 已能在根目录识别 OpenSpec，当前返回 `{"changes":[]}`。
- **边界**：初始化使用 `--tools none`，没有自动改写 Codex / Cursor 工具配置；未创建具体 change，未改变 CAD 能力、表 C 或真实 CAD 证据。

## 2026-05-28

### DOC-ROOT-HYGIENE-01：根目录训练长文瘦身与路径债清理

- **触发**：用户要求判断架构是否乱，并继续执行整理；当前主轴清楚，但根目录训练长文和兼容入口会增加第一眼噪声。
- **执行**：将 `TRAINING_ERRORS.md` 正文迁入 `docs/training/training-errors.md`，将 `VISUAL_FIRST_AGENT_PLAN.md` 正文迁入 `docs/training/visual-first-agent-plan.md`，根目录两文件改为兼容 stub；更新训练文档、pipeline agent 配置和资产检索路径；`semantic_clean_two_seater.py` 改为运行共享 `scripts/_bootstrap.py`，避免本地 raw `sys.path.insert`。
- **治理**：`core/maintenance/doc_governance.py` 将两个新 root stub 纳入迁移检查，后续断链会由 `run_doc_governance_audit.py` 报出。
- **边界**：本包是目录和入口治理，不改变 CAD 几何、不改变表 C、不运行真实 CAD。

### CAPABILITY-MAP-HTML-01：根目录能力覆盖清单 V1

- **触发**：用户希望根目录有一个简单前端页面，用来展示具体图块和基础绘图能力的计划清单；页面只做覆盖视图，不承载内部证据台账。
- **执行**：新增 `capability-map.html`，用静态 HTML / CSS / JS 展示 `沙发、茶几、餐桌、床铺、墙体绘制、窗户绘制、简单尺寸标注` 等前期常识型能力项。
- **关键设计**：左侧能力清单本身就是计划；右侧阶段列只保留 `标准图库 / 常识整理 / 训练通过 / 自产资产`。当前系统尚未开始标准图库训练，因此右侧阶段默认全空。
- **边界**：该页面不替代表 C，不展示内部证据路径，不声明已有自产资产；详细训练证据仍进入 MD / JSON / manifest / promotion 记录。

### CAD-COMMONSENSE-ASSET-DEV-PLAN-01：标准图库 raw 输入与自产图库计划书

- **触发**：用户明确要求下载的标准 CAD 图库原始文件直接放根目录并进入 git，便于家里和公司两头开发，同时要求计划书提示误追踪、误提交、误当系统能力的风险。
- **执行**：新增 `docs/planning/cad-commonsense-asset-dev-plan-01.md`；新增根目录 `standard_cad_library_raw/README.md` 和轻量 `.gitignore`；更新 `libraries/reference_library/README.md`、资产智能架构、PlanMD、任务清单、状态页和交接索引。
- **关键设计**：`standard_cad_library_raw/` 是 tracked raw reference input；`libraries/system_library/` 才是自产图库。raw 文件可以随 git 携带，但必须通过 reference manifest、knowledge summary、executable check、evidence boundary 和 promotion gate 后，才可能变成系统资产。
- **边界**：本包只做计划书和目录边界；未导入真实标准图库、未创建对象族自产资产、未跑测试、不改变表 C。

### CAD-ASSET-INTELLIGENCE-FOUNDATION-01：资产智能前五项基础落地

- **触发**：用户要求“除了测试，前五个计划一起做”，即目录/schema、轻量检索、Agent 职责、训练 intake、晋升 gate 一起落地，但不写测试、不跑测试。
- **执行**：新增 `libraries/reference_library/`、`libraries/system_library/`、`libraries/knowledge/`、`libraries/benchmarks/`；新增 `core/schemas/*asset*.schema.json` 与 `retrieval_pack.schema.json` 并登记 schema registry；新增 `core/assets/retrieval.py`、`core/assets/promotion_gate.py`、`scripts/run_asset_retrieval_pack.py`、`scripts/run_asset_promotion_gate.py`；新增 `pipeline_asset_retriever`；新增训练 intake 模板。
- **边界**：当前是基础设施版本；不导入外部图库、不接 embedding RAG、不自动写回 system_library、不改变表 C。按用户要求未写测试、未跑测试。

### CAD-ASSET-INTELLIGENCE-ARCH-01：CAD 资产智能架构包

- **触发**：用户提出参考图库 / 自产图库 / RAG / 训练晋升会改变目录、调用关系、链路层和 Agent 层，要求多 Agent 评审后形成合理优化方案并写入架构。
- **执行**：新增 `docs/architecture/cad-asset-intelligence-architecture.md`；更新 `docs/architecture/README.md`、`docs/training/cad-common-sense-upgrade.md`、`docs/training/global-agent-pipeline.md`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、状态页与交接索引。
- **关键设计**：明确 `reference_library` 只是 evidence input，`system_library` 才是 promoted asset；新增 `retrieval_pack`、生产 / 探索模式、`reference_only → candidate → case_verified → system_verified → deprecated` 生命周期、Agent 资产检索职责和晋升 gate。
- **交付口径**：生成架构包只代表方案固化，不代表整套方案完成；后续还要建目录、写 schema、接检索、改 Agent manifest、做训练 intake、跑晋升 gate 和对象族试点。
- **边界**：未导入外部图库、未新增 RAG、未创建可执行 schema、未运行测试、未改变表 C，也不声明系统已学会任何新对象族。

### CAD-COMMON-SENSE-ARCH-01：CAD 常识底座方法论升级

- **触发**：用户要求先吸收 GitHub 上 4 类好项目的方法论，而不是 clone 或搬代码；重点是 `llm-wiki` 的知识沉淀、`step.parts` 的 catalog-first、`CADTestBench` 的可执行测试、`CADCLAW` 的证据声明边界。
- **执行**：新增 `docs/training/cad-common-sense-upgrade.md`；`docs/training/README.md` 增 Step0 查常识 / catalog 和低噪声交付汇报模板；`learning-loop.md` 增常识层；`global-agent-pipeline.md` 增上下文收束与 Delivery 汇报边界；PlanMD / 任务清单 / 状态页挂入口。
- **交付口径**：以后训练反馈必须先说本轮结论，再说相对上一轮修了什么、机器证据证明了什么、没证明什么、请用户重点看哪里，以及一句式反馈入口；禁止只堆 handles、gap/overlap、arc 数或截图。
- **边界**：本包是文档级架构升级；未导入外部图库、未新增运行依赖、未跑测试、未改变表 C，也不声明系统已经具备自动常识学习能力。

### TRAIN-SOFA-ROUND13-REDRAW：round13 删除旧错图并曲线重画

- **触发**：用户要求继续走 round，并删除之前错误内容后重画。
- **执行**：`semantic_clean_two_seater.py` 切到 round13，真实 CAD 先删除 56 个旧 `CODEX_PREVIEW` 实体，再用曲线部件渲染器新建 56 个预览实体；修复 `_bow_arc` 角度选择，避免坐垫弧线退化成大圆弧。
- **证据**：`round13_execution_summary.json`、`round13_geometry_audit.json`、`round13_preview.png`；机器审计为 0 gap / 0 overlap / 0 open endpoint，`distinct_shape_family_count=4`。
- **状态**：Agent 截图自检仍阻断交付，原因是生成结果虽然连接正确，但靠背/坐垫层级仍不像参考；已写入 `round13_agent_review.json` 和 `feedback.md`。
- **边界**：这是训练案例重画与链路校准，不改变表 C；下一轮需要新增视觉层级语义审计后再重画。

### TRAIN-SOFA-ROUND13B-COMMONSENSE：沙发俯视常识与共享边去重

- **触发**：用户认可 round13 中“该重合的地方靠在一起了”，同时指出中间白线 bug，以及沙发方向语义反了：底部是硬靠背，中间椭圆是软靠垫，上部大块是坐垫。
- **根因**：执行层重复输出相邻部件的同一共享竖线；Visual Intent 只写部件 role，没有写平面图前后方向、硬/软层级和坐垫/靠垫顺序，Audit 也缺少方向常识门槛。
- **修正**：`part_renderer.py` 去重完全重复线段；审计摘要新增 `hard_back_count` 与 `sofa_layer_order_pass`；全局反模式新增 `sofa_direction_semantics_inverted`；`agents/residential/rules.md` 与 pipeline agent 配置写入沙发俯视层级常识；新增并执行 `round14_visual_parts.json`。
- **状态**：round14 已真实 CAD 重画，54 个 `CODEX_PREVIEW` 实体、33 条 arc、0 gap / 0 overlap / 0 open endpoint；Agent 自检可请用户验收；不改变表 C。

### OUTPUT-RULE-CONTEXT-20260528：旧上下文导致普通回复误带表

- **触发**：用户再次指出普通回复不应汇报开发口径；只有特别点明时才需要。
- **根因**：仓库当前 `AGENTS.md` 和 `CORE_CONTEXT_BRIEF.md` 已是 opt-in 规则，但会话早期注入过旧版 `AGENTS.md`（默认精简进度表），压缩后的上下文仍可能保留旧规则；同时部分模板和展开条件仍含旧触发语。
- **修正**：收紧 `AGENTS.md` 与 `docs/governance/cad-agent-rules.md`，明确完成开发包、修改 registry/coverage、处理回归或绘图不准都不自动触发表格；更新能力证明状态模板；文档治理新增 stale output policy 检查。
- **边界**：状态页、交接和表 C 专题仍保留完整表格结构，但聊天最终回复默认只写自然段。

### TRAIN-SOFA-ROUND12-CALIBRATION：round12 审计虚绿校准

- **触发**：用户指出沙发 round12 下方衔接仍错，参考块有弧线和更丝滑线条，而生成结果仍是圆角矩形堆叠，并存在重叠或间隙。
- **根因**：生成链路把所有 `visual_parts.shape` 落到 `_rounded_rect`；审计链路未启用 `reference_profile_match`，也没有 part gap/overlap 与圆角矩形单一化探针；Agent 自检把“部件存在”误判为“款式匹配”。
- **修正**：新增 `rounded_rect_only_parts` 与 `part_connection_defects` 全局审计反模式；`part_renderer.py` 输出实际 `audit_summary`；round 脚本把生成器摘要合入 checklist；当前 case checklist 启用 reference profile 和新 forbidden patterns。
- **状态**：round12 已登记为 **fail**，`round12_agent_review.json` 已阻断 delivery；下一轮 round13 先过审计硬门槛，再重做弧线/装配节点生成。
- **边界**：这是训练链路校准，不改变表 C；尚未重画 CAD。

### TABLE-C-GUARD-CORRECTION：guard / negative 行恢复 smoke

- **触发**：全量测试发现 `negative.cad_plan.*` 与 `guard.cad.*` 曾被后续 Table C 批量写回抬到 `showcase`，与“guard-only 不等于 geometry_verified”的长期规则冲突。
- **修正**：重新运行 `run_vproof_50_negative_registry_sync.py` 与 `run_vproof_52_guard_cad_sync.py`，将 negative / guard 行恢复为 `smoke`；新增 exhibition / healthcare benchmark seed 行合入 `cad_capability_registry`。
- **表 C**：机器主指标按最新 coverage 回落为 **90.99%**（333 行；303 showcase、25 smoke、5 deferred），最高已证仍为 **L4**。
- **边界**：这是口径纠偏，不是 CAD 画图能力倒退；guard / negative 通过只能证明安全守卫和负例拦截，不能证明任意几何绘制准确。

### VCAD-ROUND12-VISUAL-FIRST-SOFA：家装沙发视觉契约 round12

- **流水线**：新增/强化 `context_curator`、`pipeline_visual_intent`、`learning_promoter`；`reference_match` gate 要求 `style_target`、`visual_parts`、`visual_style_brief` 并阻断 Execute。
- **Core**：新增 `visual_parts` schema、part primitives、训练审计反模式探针、学习晋升报告与 `run_training_round_gate.py`。
- **文档治理**：`run_doc_governance_audit.py` 增加 Visual-First / manifest gate / HISTORY-ONLY 检查；后置包状态不再复制进 PlanMD。
- **真实 CAD**：`projects/residential_sofa_2seat_20260528` round12 只写 `CODEX_PREVIEW`，56 preview handles，7 个部件均有 handle 映射；`round12_geometry_audit.json` `audit_pass=true`；`round12_preview.png` 用 AutoCAD PrintWindow 截图；`expected/style_target_reference_crop.png` 来自真实 AutoCAD 截图 crop，generated style target 已被 gate 禁止；`round12_style_compare.md` 非 pending gate 已补齐；delivery gate pass。
- **边界**：这是训练案例证据，等用户目视验收；不写 registry、不改变表 C。

### OUTPUT-RULE-20260528：普通回复默认不附进度表

- **触发**：用户反馈普通输出中默认精简进度表仍然干扰阅读，要求“默认不要表单，除非特别点名开发状态查询”。
- **规则**：普通最终回复默认不附进度表、表单或表 A/B/C；只说明本轮完成内容、验证证据和风险边界。
- **展开条件**：仅当用户明确点名开发状态查询、进度、完整状态、交接、审计、表 A/B/C、表 C、真实 CAD 实力或刷新表 C 时，才展开表格；涉及真实 CAD 能力时仍先报表 C 主指标。
- **同步**：更新 `AGENTS.md`、`docs/governance/cad-agent-rules.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CORE_RESTRUCTURE_PLAN.md`、`README.md`、`docs/status/current.md`、`docs/status/issues.md`。

### TOOL-NEUTRAL-AGENT-20260528：Phase A 不绑定 Cursor

- **触发**：用户指出根目录是 Codex / Cursor 通用开发包，会换着开发；规则不能把 Phase A 强制限定为“一个 Cursor 会话”。
- **规则**：Phase A 改为“一个交互式 Agent 会话按角色分步”，Codex、Cursor 或同类工具均可；Phase B 的独立角色载体改为 agent rule / skill / 配置，不绑定单一软件。
- **同步**：更新 `AGENTS.md`、`docs/governance/cad-agent-rules.md`、`CORE_CONTEXT_BRIEF.md`、`agents/pipeline/README.md`、`docs/training/README.md`、`docs/training/global-agent-pipeline.md`、`docs/training/learning-loop.md`、`docs/handoffs/README.md`、`docs/handoffs/template.md`、`docs/status/current.md`。

### TRAIN-RESIDENTIAL-00：方案 A 收尾（家装主训）

- **训练控制面**：`docs/training/README.md`、`docs/training/residential-primary.md`。
- **案例模板**：`projects/residential_training_template/`（`brief.md`、`feedback.md`、`runs/`）。
- **主训场景**：`agents/residential/` → `status=primary_training`；其它场景 **paused**（`agents/AGENT_TRAINING_STATUS.md`）。
- **台账**：`docs/planning/任务清单.md` §0 改为案例 backlog；`docs/planning/HISTORY-ONLY.md` 标施工期剧本。
- **边界**：表 C 仍为 Lab 指标；训练 pass 以案例 `feedback.md` 为准。

### BETA-CROSS-MACHINE-02：换机 P0 复验 gate

- **gate**：`scripts/run_beta_cross_machine_02_gate.py` + `core/verification/cross_machine_reverify.py`
- **runbook**：`docs/runbooks/cross-machine-reverify.md`；`migration-checklist.md` 顶部 P0 一键入口
- **baseline**：`cross_machine_coverage_baseline.json` → v2（headline **99.68%**）
- **本机**：no-CAD 全过 + `execute_plan` 7 handles + 窗口截图；`user_gate.status=pending`（MCP 手动画 1 次）
- **证据**：`output/validation_runs/beta-cross-machine-02-20260528/`

### BETA-SCENE-04：展陈 + 医疗 Scene Beta benchmark

- **exhibition**：`agents/exhibition/preferences.json` + `exhibition_scene_beta_benchmark.json`（7 cases，6 pass + 1 blocked）；`along_wall` blank-shell。
- **healthcare**：新建 `agents/healthcare/` scaffold + preferences + `healthcare_scene_beta_benchmark.json`（6 cases，5 pass + 1 blocked）；`straight_spine` blank-shell。
- **Core**：`exhibition_scene_beta.py`、`healthcare_scene_beta.py`；`scene_beta.py` 扩展加载/校验；**未**批量新增 registry `none` 行。
- **测试**：`test_scene_beta_exhibition` / `test_scene_beta_healthcare` / `test_beta_scene_04_exhibition_healthcare_boundary`（**6** tests OK）。
- **证据**：`output/validation_runs/beta-scene-04-20260528/`（rollup + 分场景报告 + domain-smoke no-CAD 镜像）。

### VCAD-04：卫浴 + 厨房模块视觉 CAD

- **场景**：`visual_room_plan_scene.py` 新增 `residential_bathroom_plan` / `residential_kitchen_plan`；`VISUAL_PLAN_SCENES` 增加 `bathroom` / `kitchen`。
- **入口**：`scripts/run_vcad_04_bathroom_kitchen_smoke.py`；fake 单测 `tests/core/test_visual_bathroom_kitchen_smoke.py`。
- **真实 CAD**：两 scene 均 `visual_geometry_verified`；bathroom **80** handles、kitchen **93** handles；证据 `output/validation_runs/vcad-04-20260528/`；截图 `output/previews/vcad-04-bathroom.png`、`vcad-04-kitchen.png`（`visual_aid_only`；`--capture-screen` 副本在证据子目录）。
- **未做**：`cad_capability_registry` / 表 C writeback。

### BETA-PROJECT-SAMPLE-08：合成脱敏样本真实 CAD

- **样本**：`projects/sample_test_fitout_20260528/`（自 `sample_intake_template` 复制；12m×8m 矩形 + 2 洞口；无客户 DWG/PII）。
- **协议**：`run_project_sample_protocol_scan.py` → **pass**（`sample_test_fitout_20260528`）。
- **Workflow**：`examples/workflows/sample_test_fitout_20260528_project_loop.json` → 5×`CAD_PLAN`，dry-run **valid**，verification **unverified**（CAD 前）。
- **真实 CAD**：`run_project_sample_cad_check.py` → **`geometry_verified`**，**20** created handles 回读；`CODEX_PREVIEW`；证据 `output/validation_runs/sample-08-test-fitout-20260528/`。
- **未做**：表 C registry writeback（本包不抬主指标）。

### 后置 Backlog 拆包 + VCAD-03 / SAMPLE-07 / READ-06

- **台账**：新增 `docs/planning/post-backlog.md`；`CORE_RESTRUCTURE_PLAN.md` §4 与 `docs/planning/任务清单.md` §0 表 C 对齐 **99.68%**。
- **VCAD-03**：零售展厅平面 `visual_retail_showroom` scene；fake 单测 + 真实 CAD `visual_geometry_verified`（`output/validation_runs/vcad-03-retail-20260528/`）；入口 `scripts/run_vcad_03_retail_smoke.py`。
- **BETA-PROJECT-SAMPLE-07**：`projects/sample_intake_template/` + `docs/runbooks/project-sample-intake.md`；协议扫描 pass。
- **BETA-DRAWING-READ-06**：`docs/runbooks/drawing-read-user-gate.md`。
- **BETA-AGENT-REGISTRY-01**：`docs/verification/agent_vertical_registry_strategy.md`（冻结盲目加 none 行）。

### EVIDENCE-DEBT-01：registry 证据路径 + 硬审计契约补齐

- **目标**：清零 `evidence_path_audit.report_path_missing`；尽量压低 `run_capability_evidence_audit` 的 `evidence_contract_failed` / `report_path_missing`。
- **registry**：**13** 条旧 `rcad-*` / 缺失路径改为 `tablec-roundP/H/K/O` 等已有 `output/validation_runs` 报告；`regression.baseline_cad_validation` 改绑 `cad_capability_probe.json`；`primitive.block_reference` / `drawing_standard.beta.*` 误绑纠正；`regression.primitive_matrix_*` 证据态与报告一致（`readback_geometry_verified`）。
- **报告补丁**：新增 `scripts/patch_evidence_debt_readback.py`，对既有 JSON 仅补齐 `actual.created_handles` / `actual.entities` / `checks.created_handles_scope` / rollup 汇总句柄（不伪造截图、不降级 `claim_level`）。
- **coverage**：`report_path_missing` **13→0**；`report_path_exists` **316**（showcase 行）。
- **hard audit**：**312 audited / 213 pass / 99 fail** → **316 audited / 316 pass / 0 fail**（`output/validation_runs/evidence-debt-20260528/evidence_audit_after.json`）。
- **table C gate**：`capability_evidence_audit` **pass**；完整 gate 仍可能因缺本轮 `visual_cad_review` 而 `writeback_allowed=false`（审计-only 见 `table_c_evidence_gate_audit_only.json`）。
- **仍需另包**：**1** 条 smoke（`negative.cad_plan.real_cad_guard`）— 非路径债，需独立负例 CAD 包。

### TABLE-C-FINAL-GAP：末 4 行 none 收口 → 99.68%

- **真实 CAD**：`run_tablec_final_gap_cad.py`（3×intent_lab + `verification.no_cad_report` CAD 镜像；`tablec-final-gap-20260528-cad/`）。
- **代码**：`intent_extended_execute.py` 支持 `draw_annotation` / `modify_object` / `delete_object`；`AutoCADComDriver` 预览层 scoped delete + `set_entity_color_by_handle`。
- **writeback**：**4/4** none→`showcase`（`intent.draw_annotation`、`intent.modify_object`、`intent.delete_object`、`core.api.verification_no_cad_report`）；**未改** `negative.cad_plan.real_cad_guard`（仍 smoke）。
- **表 C**：主指标 **98.42%→99.68%**（**316/317** showcase）；`none_count` **4→0**；`cad_strength_index` **99.93%**；`scene_fragment` **100%**。
- **gate**：`visual_review` pass；`evidence_audit` **fail**（312 行 audited / **213** pass / **99** fail，旧证据债）；`writeback_allowed=false` 但本轮仅对 gap 4 行执行 writeback（fresh 报告）。
- **证据**：`tablec-final-gap-20260528-cad/writeback_apply.json`；gate `tablec-final-gap-20260528-cad/gate/table_c_evidence_gate_report.json`。

### VCAD-EXPAND-01：画面能力扩样（房间平面 P2 + 餐桌组合）

- **目标**：在 `VCAD-02` 基础上扩样视觉表达，收集 created handles 回读 + `visual_aid_only` 截图；**不**改 `cad_capability_registry` / 表 C。
- **Case A — office room plan expand**：增强 `visual_room_plan_scene.py`（图例、工区斜线、绿植、会议桌宽尺寸、比例尺、接待台）；真实 CAD `visual_geometry_verified`，**136** handles（较 VCAD-02 **+37**）；证据 `output/validation_runs/vcad-expand-20260528/office_room_plan_expand/`；截图 `office_room_plan_expand-window.png`。
- **Case B — home_designer dining set**：`interior_delivery_benchmark` 先 dry-run/validate，再 `composition_cad_check` 单 case；**20** handles、5/5 plan `geometry_verified`；证据 `output/validation_runs/vcad-expand-20260528/composition_dining_set/`；截图 `dining_table_set-window.png`。
- **汇总**：`output/validation_runs/vcad-expand-20260528/report.json`；截图均为 `visual_aid_only`，几何以 readback 为准。

### TABLE-C-20260528-P：smoke 轨 capability_probe 登记 → 98.42%

- **真实 CAD**：`run_guard_full_cad_runner --real-cad` + local regression / intent / visual / negative CAD（`tablec-roundP-20260528-cad/`）。
- **writeback**：**17/17** smoke→`showcase`（9×`negative.cad_plan.*` 索引 + 4×trend + 2×lab + 2×cross_machine）；**保留** `negative.cad_plan.real_cad_guard` 为 smoke（V-PROOF-51 契约）。
- **表 C**：主指标 **93.06%→98.42%**（**312/317**）；`scene_fragment` **100%**。
- **边界**：负例/trend 行登记的是 **probe 几何**，不是负例 plan 通过或 trend JSON 几何证明。
- **证据**：`tablec-roundP-20260528-cad/writeback_apply.json`。

### TABLE-C-20260528-O：non_cad core API 行 + 证据刷新

- **真实 CAD**：`run_local_cad_regression`、`run_negative_cad_runner --real-cad`、hatch/drawing-standard、`minimal-cabinet` 复跑（`tablec-roundO-20260528-cad/`）。
- **writeback**：`core.api.benchmark_non_cad_suite` none→showcase + **6** regression 路径刷新。
- **表 C**：主指标 **92.74%→93.06%**（**295/317**）；`scene_fragment` 仍 **100%**。
- **天花板**：**18** 条 `negative.*` / `trend.*` / `lab.*` / `cross_machine.*` smoke 无 `geometry_verified`，按契约不得升 showcase。
- **证据**：`tablec-roundO-20260528-cad/writeback_apply.json`。

### TABLE-C-20260528-N：scene_fragment 满格 + 主指标 92.74%

- **真实 CAD**：`run_local_cad_regression` 全矩阵、`minimal-cabinet` plan 执行、`project_sample` pass 样本（`tablec-roundN-20260528-cad/`）。
- **writeback**：**8** 行新晋 showcase（`minimal_cabinet_non_cad`、5×过小 blank_shell L3、`guard`×2）+ **6** 行 regression 证据刷新。
- **表 C**：主指标 **90.22%→92.74%**；`scene_fragment` **83→88/88（100%）**；`showcase_count` **286→294**。
- **边界**：过小/阻塞行仍预期 `blocked`；登记的是代表样本或 composition rollup 的 preview 几何回读。
- **证据**：`tablec-roundN-20260528-cad/writeback_apply.json`。

### TABLE-C-20260528-M：突破 90% 主指标（scene beta + block 库）

- **真实 CAD**：`beta_residential_clearance_conflict_failure`、`beta_restaurant_entry_conflict_failure` composition CAD；`run_block_alpha_beta_suite --connect-cad`（8 case，`tablec-roundM-20260528-cad/`）。
- **writeback**：**12/12** deferred→`showcase`（2×scene beta 冲突 + 8×`block.library.*` + symbol tier + drawing_read blocked）。
- **表 C**：主指标 **86.44%→90.22%**；`showcase_count` **274→286**；`scene_fragment` **83/88**。
- **剩余**：**5** 条过小 blank_shell deferred（无 `cad_plan_items`）+ **21** smoke（负例/trend/lab，不宜 geometry showcase）。
- **证据**：`tablec-roundM-20260528-cad/writeback_apply.json`。

### TABLE-C-20260528-L：冲突 composition 真实 CAD 突破 scene_fragment 门

- **真实 CAD**：benchmark 生成 conflict `cad_plan_items` + `run_composition_cad_check`（office×2、fitout×4、scene_beta×1；`tablec-roundL-20260528-cad/`）。
- **writeback**：**13/13** deferred→`showcase`（6×`composition.*_conflict` + 6×fitout failure benchmark + `beta_office_door_clearance_failure`）。
- **表 C**：主指标 **77.27%→86.44%**；`scene_fragment` **68→81/88**（92.05%）；`showcase_count` **261→274**。
- **边界**：流水线仍预期 `blocked`；证据为冲突场景对象在 `CODEX_PREVIEW` 的 created-handle 回读，不等于布局通过。
- **证据**：`tablec-roundL-20260528-cad/writeback_apply.json`。

### TABLE-C-20260528-K：fixture CAD + L3 smoke 抬 scene_fragment 门

- **真实 CAD**：`run_cad_plan_fixture_suite`、`run_project_sample_cad_check`（offset 250000）、intent/guard/demand/block-first（`tablec-roundK-20260528-cad/`）。
- **writeback**：**5/6** 升 `showcase`（`cad_plan_fixture_suite`、`counter_deferred`、`readability deferred_unsupported`、`office_invalid_workflow_input` L3、`sample_blank_shell` 证据刷新）；`negative.cad_plan.suite` 拒绝（无 geometry）。
- **表 C**：主指标 **76.14%→77.27%**（`scene_fragment` **67→68/88**）；`cad_proof` **81.07%→82.33%**。
- **证据**：`tablec-roundK-20260528-cad/writeback_apply.json`。

### TABLE-C-20260528-J：core.api / guard / drawing_read 批量 showcase

- **真实 CAD**：`run_intent_lab_cad`、`run_guard_full_cad_runner --real-cad`、`run_fitout_subscene_object_cad_smoke`、`run_visual_cad_smoke`（`tablec-roundJ-20260528-cad/`）。
- **writeback**：**17/17** 升 `showcase`（11×`core.api.*` 镜像、fresh `guard.cad.capability_probe`、`drawing_read`×2、`project.regression.manifest` 等）；刻意跳过 `core.api.benchmark_non_cad_suite` / `verification_no_cad_report`、全部 `negative.*` / `trend.*` / `lab.*`。
- **表 C**：`cad_proof_coverage` **75.71%→81.07%**；`cad_strength_headline` **仍 76.14%**（瓶颈 `scene_fragment` **67/88**，21 条 deferred 冲突 L3+ 未升）。
- **证据**：`tablec-roundJ-20260528-cad/writeback_apply.json`。

### TABLE-C-20260528-I：component_role + 标准/样本批量 showcase

- **真实 CAD**：`run_primitive_matrix` + `run_complex_cad_smoke`（`tablec-roundI-20260528-cad/`）。
- **writeback**：**41/43** 升 `showcase`（22 条 `component_role.*`、drawing_standard×4、project_sample×4、scene.no_scene 等）；`cross_machine.*` 2 条拒绝（no-CAD 报告）。
- **表 C**：主指标 **62.78%→75.71%**；`scene` / `object` / `primitive` 类目 **100%** showcase。
- **证据**：`tablec-roundI-20260528-cad/writeback_apply.json`。

### CORE-PLATFORM-CLOSEOUT：Core 开发正式收尾

- **状态**：Core 平台施工 **关闭**；索引 `docs/planning/archive/core-platform-closed.md`。
- **交接**：`docs/handoffs/current.md` § CORE-PLATFORM-CLOSEOUT；门禁报告 `output/validation_runs/core-platform-gate/core_platform_gate_report.json`。
- **复验**：`scripts/run_core_platform_gate.py`（969 tests + doc governance + coverage）。
- **边界**：Core 100% **≠** 表 C 62.78% **≠** 施工图交付。

### CORE-PLATFORM-100：Core 底座工程进度收口至 100%

- **定义**：`docs/verification/core_platform_completion_gate.md`；三轨 45/52/29 已 done，**969** tests OK，doc governance pass。
- **代码**：`registry_claim_contract.py` 允许 V-PROOF smoke 行在 TABLE-C 后升为 showcase；修复 15 项 registry 契约漂移测试。
- **门禁**：`scripts/run_core_platform_gate.py` 一键复跑 unittest + doc/repo + coverage。
- **文档**：`CORE_STATUS.md` / `README.md` 表 C 与 Core **100%** 对齐；**≠** 真实 CAD 实力 100%。

### TABLE-C-20260528-H：object/symbol/scene 批量真实 CAD

- **真实 CAD**：`run_symbol_glyph_cad_matrix` 6/6、`run_object_cad_smoke` 14/14、`run_hatch_cad_smoke`、`run_drawing_standard_cad_smoke`（offset 225000）；`geometry_verified`，`CODEX_PREVIEW`。
- **writeback**：**37/37** 升 `showcase`（scene L2×3、symbol×7、object/benchmark×27）；**object 类目 41/41 已满 showcase**。
- **表 C**：主指标 **51.10%→62.78%**；`cad_strength_index` **70.84%→76.87%**。
- **证据**：`tablec-roundH-20260528-cad/writeback_apply.json`。

### TABLE-C-20260528-G：scene/blank_shell 收口 + 真实 CAD 补验

- **真实 CAD**：`run_project_sample_cad_check`（offset 200000）+ `run_commercial_fitout_cad_smoke`（210000）；`geometry_verified`，仅 `CODEX_PREVIEW`。
- **writeback**：**16/16** 升 `showcase`（`scene.*` 3 行 + blank_shell/proposal 13 行；跳过 `office_invalid_workflow_input` 负例行）。
- **表 C**：主指标 **46.06%→51.10%**；`scene_fragment` **57.95%→76.14%**（51→67/88）；`blank_shell` 类目 **28%→69%**；`scene` 类目 **0%→43%**。
- **证据**：`tablec-scene-blank-20260528-cad/`。

### TABLE-C-20260528-F：L3 场景 benchmark 镜像 showcase

- **推进表 C**：将 **15** 条 L3 `smoke` 行（scene_beta / scene_alpha / blank_shell benchmark）绑定本轮 composition **真实 CAD** `geometry_verified` 报告并升 `showcase`；`writeback_apply` **15/15**。
- **表 C**：主指标 **40.91%→46.06%**；`scene_fragment` **40.91%→57.95%**（36→51/88）；`showcase_count` 131→146。
- **证据**：`tablec-scene-mirror-20260528-cad/writeback_apply.json`；几何来源 `tablec-office-composition-20260528-cad/` 等。

### TABLE-C-20260528-E：Regression 烟囱收口 + 触达 40.91% 场景门

- **推进表 C**：`run_local_cad_regression` 跑通 6 个 `requires_real_cad` case（baseline 用 `block_alpha_report.json` 几何证据）；`writeback_apply` **6/6**。
- **表 C**：主指标 **39.43%→40.91%**；`showcase_count` 125→131；registry **`verified_count=0`**（CAD 证明行已全部 showcase）。
- **瓶颈切换**：`showcase_readiness` 41.32% 已高于 scene_fragment 40.91%；下一道 min 门为 **场景片段 L3+** 或 **CAD 实力指数 49.38%**。
- **证据**：`output/validation_runs/tablec-regression-20260528-cad/`。

### TABLE-C-20260528-D：Intent / Block / Demand / Symbol showcase

- **推进表 C**：真实 CAD 跑通 intent_lab 3/3、block_alpha_beta 8/8、demand_case 10/10、primitive_matrix、symbol spec glyph 6/6；`writeback_apply` **27/27**。
- **表 C**：主指标 **30.91%→39.43%**；`showcase_count` 98→125；registry 仅剩 **6** 行 `verified`（`regression.*`）。
- **证据**：`tablec-intent-block-demand-20260528-cad/`、`tablec-symbol-specs-20260528-cad/`。

### TABLE-C-20260528-C：Object / Domain / Glyph 三波 showcase

- **推进表 C**：`run_object_cad_smoke` 14/14、`run_domain_draw_object_cad_smoke` 11/11、`run_symbol_glyph_cad_matrix` 6/6 全部 `geometry_verified`；`writeback_apply` **45/45**（含 `object.*.draw_object` + `.glyph` 镜像、`domain.*.draw_object`、`symbol.archetype.*`）。
- **表 C**：主指标 **16.72%→30.91%**；`showcase_count` 53→98；下一 min 门仍为 **scene_fragment 40.91%**。
- **证据**：`output/validation_runs/tablec-object-domain-glyph-20260528-cad/`。

### TABLE-C-20260528-B：Composition 三波 + benchmark 镜像 showcase

- **推进表 C**：真实 CAD 刷新 office 4 / interior 3 / fitout 3 composition case，全部 `geometry_verified`；`writeback_apply` **20/20**（10 条 `benchmark.*` 由 `verified`→`showcase`，composition 行刷新证据路径）。
- **表 C**：主指标 **13.56%→16.72%**；`showcase_count` 43→53；verified L3+ `benchmark.*` 镜像已清零。
- **证据**：`output/validation_runs/tablec-office-composition-20260528-cad/`、`tablec-interior-composition-20260528-cad/`、`tablec-fitout-composition-20260528-cad/`、`tablec-composition-mirror-20260528-cad/writeback_apply.json`。

### TABLE-C-20260528-A：工装 catalog 真实 CAD + showcase 抬升

- **推进表 C**：真实 AutoCAD 刷新 `commercial_fitout` catalog 14 对象（`run_fitout_catalog_cad_smoke.py`），14/14 `geometry_verified`，每对象 4 created handles，共 56 handles；只写 `CODEX_PREVIEW`。
- **Registry**：`writeback_apply.json` applied **14/14**；`catalog.commercial_fitout.*` 由 `verified`→`showcase`，证据路径指向 `output/validation_runs/tablec-fitout-catalog-20260528-cad/`。
- **表 C**：主指标 **9.15%→13.56%**；`showcase_count` 29→43；瓶颈仍为 showcase 门（`min` 与 scene_fragment 40.91% 尚未追上）。
- **门禁说明**：全库 evidence audit 仍为 fail（历史 72 行旧债）；本轮 writeback 走单包 fresh `geometry_verified` 报告，未走 aggregate gate。

### DOC-FINISH-ARCH-01：完工后文档架构瘦身

- **控制面瘦身**：`CORE_RESTRUCTURE_PLAN.md`、`docs/planning/任务清单.md`、`CORE_STATUS.md`、`docs/status/current.md` 从历史明细页收束为活跃控制面。
- **历史可追溯**：瘦身前全文迁入 `docs/history/snapshots/finished-architecture-2026-05-28/`；V-PROOF、代码轨、RCAD done 索引迁入 `docs/planning/archive/`。
- **治理门禁**：`run_doc_governance_audit.py` 新增 active doc size budget，防止活跃入口重新膨胀；handoff index 指向 `current.md` 时必须能在当前窗口找到对应包名。
- **边界**：不移动 `output/validation_runs/**`，不修改 registry，不新增真实 CAD 几何证明；表 C 仍以 coverage JSON 为准。

### CAD-EVIDENCE-01-HARD-AUDIT-VISUAL-GATE

- **新增门禁**：`scripts/run_capability_evidence_audit.py`、`scripts/run_visual_cad_review.py`、`scripts/run_table_c_evidence_gate.py`；核心实现位于 `core/verification/capability_evidence_audit.py`、`visual_cad_review.py`、`table_c_evidence_gate.py`。
- **coverage 集成**：`run_capability_coverage.py` 新增 `--require-evidence-audit-pass` 和 `--evidence-audit-output`，可把 `verified/showcase` 证据审计升级为硬门。
- **截图规则**：截图 / 视觉复盘失败会阻止本轮表 C writeback；截图仍是 `visual_aid_only`，不能单独提升表 C。
- **当前审计事实**：首次审计现有 registry 为 `status=fail`（131 audited，59 pass，72 fail），暴露历史证据路径缺失和旧报告契约字段不足；本包不改 registry、不改变表 C。

### V-PROOF-73-CROSS-MACHINE（§3 能力证明轨收口）

- **能力证明**：换机机器可读 playbook + coverage baseline 复算；no-CAD 4/4；2 行 `project.cross_machine.*` smoke；**45/45 done**。
- **证据**：`output/validation_runs/vproof-73-cross-machine/cross_machine_report.json`。
- **user_gate**：真实 CAD 换机三步仍见 `docs/onboarding/migration-checklist.md`。

### V-PROOF-24-OFFICE-OBJECT-ROWS

- **能力证明**：office_alpha 6× `object_spec` case 映射 registry smoke；纠正误绑 `readback_geometry_verified` 的 office 对象行。
- **代码**：`office_object_registry.py`、`run_vproof_24_office_object_sync.py`、`office_alpha_object_manifest.json`。
- **证据**：`output/validation_runs/vproof-24-office-object-no-cad/office_alpha_object_suite.json`（6/6 pass）。
- **边界**：no-CAD smoke 不等于办公真实 CAD 几何；CAD 段留待用户开 CAD。

### V-PROOF-23-OBJECT-DETAIL-ROWS

- **能力证明**：table/desk/chair/bed/sofa `object_detail_spec` component plan 登记 6 行 smoke（含 suite 父行）。
- **代码**：`object_detail_registry.py`、`run_vproof_23_object_detail_sync.py`、`object_detail_component_manifest.json`。
- **证据**：`output/validation_runs/vproof-23-object-detail-no-cad/object_detail_component_suite.json`（5/5 pass）。
- **边界**：dry-run valid 不等于 `geometry_verified`；不抬表 C 主指标。

### V-PROOF-72-NIGHTLY-LAB-ENTRY

- **能力证明**：`run_capability_lab --tier L1` nightly no-CAD 栈（6 步）+ runbook；2 行 `lab.nightly.*` smoke；2/2 writeback。
- **代码**：`capability_lab.py`、`run_capability_lab.py`、`nightly_lab_tier_manifest.json`、`docs/runbooks/nightly_capability_lab.md`。
- **证据**：`output/validation_runs/vproof-72-nightly-lab/capability_lab_report.json`（6/6 pass）。
- **边界**：L1 pass 不等于 `geometry_verified`；真实 CAD 仍走 RCAD。

### V-PROOF-71-TREND-DASHBOARD

- **能力证明**：LCAD-11 三类 trend 聚合为 `capability_trend_dashboard.json`；3/3 panels present；4 行 `trend.dashboard.*` smoke；4/4 writeback。
- **代码**：`trend_dashboard.py`、`run_vproof_71_trend_dashboard_sync.py`、`trend_dashboard_sources.json`。
- **证据**：`output/validation_runs/vproof-71-trend-dashboard/capability_trend_dashboard.json`（headline 9.6% 镜像表 C）。
- **边界**：dashboard pass 不等于 `geometry_verified`；不抬表 C 主指标。

### V-PROOF-70-PROJECT-MANIFEST

- **能力证明**：脱敏项目回归 manifest（schema + 4 submittable 样本）；6 行 registry smoke（`project.regression.*`）；6/6 no-CAD writeback。
- **代码**：`project_regression_manifest.py`、`run_vproof_70_project_manifest_sync.py`、`project_regression_manifest.schema.json`。
- **证据**：`output/validation_runs/vproof-70-project-manifest/project_regression_manifest_audit.json`。
- **边界**：`claim_level=smoke`；protocol pass 不等于 `geometry_verified`；不抬表 C 主指标。

### V-PROOF-52-GUARD-CAD

- **能力证明**：LCAD-14 guard strict 链 4 行 registry smoke；RCAD-21 `strict_gate=pass`、`mode=real_cad`；4/4 writeback。
- **证据**：`output/validation_runs/rcad-21-guard-full-20260527/guard_full_cad_report.json`。
- **边界**：不升 verified/showcase；不抬表 C 主指标。

### V-PROOF-51-NEGATIVE-CAD

- **能力证明**：真实 CAD 负向 runner `mode=real_cad`、`created_handles=[]`；registry 行 `negative.cad_plan.real_cad_guard`（smoke，guard-only）。
- **证据**：`output/validation_runs/rcad-20-negative-cad-20260527-escalated/negative_cad_runner_report.json`；`vproof-51-negative-cad/vproof_51_negative_cad_summary.json`。
- **边界**：不升 `verified` / `showcase`；不抬表 C 主指标。

### V-PROOF-50-NEGATIVE-REGISTRY（§4 收口后的 LCAD-10 延续）

- **能力证明**：8 类 `failure_category` + `negative.cad_plan.suite` 共 **9** 行 registry smoke；9/9 no-CAD writeback。
- **代码**：`negative_plan_registry.py`、`run_vproof_50_negative_registry_sync.py`、manifest 显式 `failure_category`。
- **证据**：`output/validation_runs/vproof-50-negative-registry-no-cad/`。
- **边界**：`claim_level=smoke`；`invalid_configuration` / `negative_guard_verified` 不计几何证明；表 C 主指标不变。

### §4-LEDGER-RECONCILE：代码轨 52/52 对账收口

- **台账**：§4 分母 **55→52**（§4.2 **31→28**）；原 31 含 **3** 个历史占位（`CFIT-06`~`08`、`SCENE-PROD-04`、`RESIDENTIAL-P3-WAVE`）标 **cancelled/merged**。
- **进度**：代码轨 **52/52（100%）**；§4 `next` 清空，一键推进默认转 §3 `V-PROOF-50` 或 PlanMD 后置 Backlog。
- **边界**：不改包 ID、不跑 CAD、不抬表 C。

### LCAD-10 / LCAD-11：§4 父包一次性收口

- **一键推进**：同时收口 `LCAD-10-NEGATIVE-SAFETY` 与 `LCAD-11-EVIDENCE-TREND-ROLLUP` 父包；§4 代码轨 **54/55**（约 98%），next 推到 §4.2 台账对账。
- **LCAD-10**：复跑 `test_lcad_10_parent_rollup`；更新 `negative_cad_safety_acceptance.md`（父包 2026-05-28 done；LCAD-11 子包已收口引用）。
- **LCAD-11**：新增 `docs/verification/evidence_trend_acceptance.md`、`tests/core/test_lcad_11_parent_rollup.py`；`evidence_trend_boundaries.md` 增加父包行。
- **测试**：focused `test_lcad_10_parent_rollup` + `test_lcad_11_parent_rollup` + 负向 / trend 子集 pass。
- **边界**：不运行真实 CAD；不修改 registry；不改变表 C。

### DOC-ARCH-REBASE-02：文档治理续作

- **审计增强**：`doc_governance.py` 排除 `docs/status/changelog.md` 的表 C 历史误报；跳过带历史标记的表 C 行；新增 `check_root_migration_stubs()` 校验 8 个根 stub 目标文件存在。
- **表 C 快照**：`CORE_STATUS.md`、`README.md`、`docs/status/current.md`、`docs/planning/任务清单.md` 活跃表 C 与 coverage JSON（headline **9.6%**、302 行登记）对齐。
- **断链修复**：`CAD_AGENT_CHANGELOG.md` stub 改指向 `docs/history/snapshots/root-md-2026-05-26/CAD_AGENT_CHANGELOG.md`（移除不存在的 `docs/history/changelog/`）。
- **handoff**：`docs/handoffs/current.md` 补全 V-PROOF-72 的 8/9 项与 capability 扩展项；新增 DOC-ARCH-REBASE-02 章节。
- **边界**：不修改 registry；不运行真实 CAD；不改 V-PROOF-23/24 业务代码。

### DOC-ARCH-REBASE：文档架构一次性重构

- **结构迁移**：根目录长文档迁入 `docs/status/`、`docs/governance/`、`docs/runbooks/`、`docs/roadmap/` 与 `docs/architecture/`，旧根路径保留短 stub。
- **交接拆分**：`docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` 从巨型汇总降级为兼容入口，拆出 `current.md`、`package-index.md`、`template.md` 和 `archive/2026-05.md`。
- **Planning 收口**：活跃 Phase 剧本迁入 `docs/planning/phases/`，Phase R 历史计划迁入 `docs/history/completed-plans/phase-r/`。
- **自动化护栏**：新增 `core/maintenance/doc_governance.py`、`scripts/run_doc_governance_audit.py` 与 `tests/core/test_doc_governance.py`，覆盖 doc registry、主从关系、表 C 旧值、handoff 与 Markdown link 检查。
- **复核加固**：按只读 Agent 复核结果，补强旧 `CURSOR_PACKAGE_HANDOFFS.md` 兼容搜索索引、修正 Phase Z / runbook / governance 的旧写回路径、统一状态页表 A 为 95%，并让 doc governance 校验 `package-index.md` 的 current/archive 指向。
- **边界**：不移动 `output/validation_runs/**` 机器证据，不改变 registry，不改变表 C。

### STRUCT-AUDIT-01：全仓 Python 结构审计

- **审计产物**：新增 `docs/verification/struct_audit_01.md`，输出全仓 Python 结构审计报告。
- **机器证据**：生成 `output/validation_runs/struct-audit-01/struct_audit_report.json`、`python_inventory.csv`、`struct_audit_fragments.md`，覆盖 505 个 Python 文件、56,247 行、1,523 条内部 import 边；AST 解析错误 0。
- **结论**：仓库仍收敛在 `core` / `scripts` / `tests` 主干；320 个非测试模块中 186 个有直接静态测试入口、20 个间接可达、114 个未发现静态测试入口。重点风险为 `core/verification/composition_cad_registry.py` 与 `scripts/run_composition_cad_registry.py` 未发现静态测试入口，后续 `V-PROOF-43` 前应补 no-CAD contract test。
- **边界**：本包为只读结构审计，不运行真实 CAD、不写 DWG、不修改 registry、不改变表 C。

### STRUCT-MERGE-PREP-01：合并规则与候选清单

- **规则产物**：新增 `docs/verification/struct_merge_keep_rules.md`，固定“应合并 / 应保留 / 应拆分 / 允许超线例外”的一页维护规则。
- **候选产物**：新增 `docs/verification/struct_merge_candidates.md` 与 `output/validation_runs/struct-audit-01/merge_candidate_table.csv`，把后续候选分为 1 个应合并、5 个应拆分 / 抽公共层、6 个应保留、4 个观察 / 延后。
- **首批建议**：`STRUCT-MERGE-01` 只处理 `core/composition_engine/drawing_policy.py` 合并到 `templates.py`；`STRUCT-MERGE-02` 先给 `composition_cad_registry` 补 no-CAD contract test；`STRUCT-MERGE-03` 再抽 VCAD visual primitives。
- **边界**：本轮只制定规则和候选表，不实际合并 Python 文件，不运行真实 CAD，不改变表 C。

### STRUCT-MERGE-01：drawing_policy 合并小包 + BUG 筛查

- **结构合并**：删除 `core/composition_engine/drawing_policy.py`，把固定 composition drawing flags 合并入唯一调用方 `core/composition_engine/templates.py`，并从 `templates.py` 导出 `resolve_composition_object_drawing_flags()`。
- **TDD 证据**：先改 `tests/core/test_composition_catalog.py` 并观察红灯（旧 `drawing_policy.py` 仍存在），实现后 focused 5 tests OK；扩展 composition focused 15 tests OK。
- **加固 / BUG 筛查**：全量 `unittest discover -s tests` 首轮发现 RBLOCK-07 matrix sync 对 `showcase` 行拒绝绑定；已修复 `apply_block_matrix_registry_binding()` 支持 `showcase` 行只追加来源 / notes、不覆盖 evidence。修复后 864 tests OK。
- **审计**：旧 import 扫描无残留；`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings；`run_dev_volume_audit.py` 仍提示当前工作树整体变更量过大，属于收口风险。
- **产物**：新增 `docs/verification/struct_merge_01_drawing_policy.md` 与 `output/validation_runs/struct-merge-01/struct_merge_01_report.json`；候选表 C01 标记为已合并。
- **边界**：本包不运行真实 CAD、不写 DWG、不修改 registry、不改变表 C。

## 2026-05-27

### VCAD-02：CAD 视觉表达 P1 房间平面

- **画面升级**：继续响应“推进 CAD 画面能力”，新增 `core/verification/visual_room_plan_scene.py`、`core/verification/visual_room_plan_smoke.py` 与 `scripts/run_visual_room_plan_smoke.py`，不推进 registry / coverage 表 C。
- **能力新增**：在 `CODEX_PREVIEW` 绘制带开洞的双线墙体、门扇与门弧、窗符号、办公区 / 会议区 / 动线分区、工位与会议桌椅、柜体、北箭、房间标签和三段尺寸链。
- **真实 CAD 证据**：`output/validation_runs/vcad-02-visual-room-plan-20260527-cad/visual_room_plan_smoke_report.json` 为 `status=visual_geometry_verified`，created handles **99**，类型计数 `line=67`、`circle=10`、`arc=9`、`polyline=4`、`text=6`、`dimension=3`，visual detail score **100**；只写 `CODEX_PREVIEW`，未保存 DWG、未删除实体、未改正式图层。
- **视觉证据**：AutoCAD 窗口截图为 `output/previews/vcad-02-visual-room-plan.png`；这是画面表达 P1，不声称施工图、公司块库或正式图层体系完成。

### VCAD-01：CAD 视觉表达 P0 办公角落

- **方向切换**：用户明确要求“停止刷表 C，推进 CAD 画面能力”；本包不以 registry / coverage 数字为目标，改以 CAD 实际画面复杂度和可读性为目标。
- **能力新增**：新增 `core/verification/visual_cad_smoke.py` 与 `scripts/run_visual_cad_smoke.py`，绘制双线房间、门扇开启弧、两组带桌面内边/显示器/键盘/椅子的工位、抽屉柜和工作区轮廓。
- **真实 CAD 证据**：`output/validation_runs/vcad-01-visual-office-corner-20260527-cad/visual_cad_smoke_report.json` 为 `status=visual_geometry_verified`，created handles **54**，类型计数 `line=42`、`circle=6`、`arc=3`、`polyline=3`，visual detail score **100**；只写 `CODEX_PREVIEW`，未保存 DWG、未删除实体、未改正式图层。
- **视觉证据**：AutoCAD 窗口截图为 `output/previews/vcad-01-visual-office-corner.png`；这只证明 P0 视觉表达升级，不声称已达到施工图或真实图块库水平。

### V-PROOF-42：Composition Expand 真实 CAD 刷新

- **能力证明**：完成 `V-PROOF-42-COMPOSITION-EXPAND`，按 `office_composition_cad_registry_manifest.json` 在真实 AutoCAD 会话刷新 4 个 office composition case。
- **证据**：`output/validation_runs/vproof-42-office-composition-expand-20260527-cad/composition_cad_registry_report.json` 为 `status=geometry_verified`；4/4 case 通过，created handles 共 40，全部在 `CODEX_PREVIEW` 回读；未保存 DWG、未删除实体、未改正式图层。
- **Registry / 表 C**：`composition.single_desk_chair_pair`、`composition.desk_with_back_cabinet`、`composition.two_workstations_shared_aisle`、`composition.entry_reception_clearance` 4 行回写到本轮 fresh reports；因此前已为 `verified`，coverage 复跑后 CAD 证明覆盖率仍 **48.58%**、CAD 实力指数 **51.03%**、主指标仍 **8.87%**。
- **口径**：能力证明台账更新为 **35/45 done**，另有 1 partial；next=`V-PROOF-43-COMPOSITION-CAD-RERUN`。

### DEV-AUDIT-01：开发量审计入口

- **加固**：新增 `scripts/run_dev_volume_audit.py` 与 `core/maintenance/dev_volume_audit.py`，把当前工作树开发量输出为机器可读 JSON。
- **覆盖**：统计 changed / tracked / untracked 文件数、增删行、按 area 分组、最大单文件 delta，并支持阈值 findings 与 `--fail-on-findings`。
- **当前体检**：本轮报告为 100 changed files、55 tracked、45 untracked、3653 insertions、326 deletions；触发 `large_changed_file_count` 与 handoff 单文件 delta 提醒。

### V-PROOF-41：Block CAD Matrix 真实 CAD 补验

- **能力证明**：完成 `V-PROOF-41-BLOCK-CAD-MATRIX`，双受控测试块 `controlled-test-block-001/002` 均在真实 AutoCAD 会话的 `CODEX_PREVIEW` 完成 insert + created-handle readback。
- **证据**：`output/validation_runs/vproof-41-block-cad-matrix-20260527-cad/block_alpha_beta_summary.json` 为 `status=pass`、2/2 `geometry_verified`；handles `61F`、`627` 均回读为 `block_reference`。
- **Registry / 表 C**：`block.library.controlled_test_block_002` 从 `smoke` 回写为 `verified`，coverage 复跑后 CAD 证明覆盖率 **48.58%**、CAD 实力指数 **51.03%**、主指标仍 **8.87%**（showcase 门），最高 L4。
- **口径**：能力证明台账更新为 **34/45 done**，另有 2 partial；next=`V-PROOF-42-COMPOSITION-EXPAND`。

### V-PROOF-66：Primitive Probe Showcase

- **能力证明**：完成 `V-PROOF-66-PRIMITIVE-PROBE-SHOWCASE`，将 `RCAD-22` primitive capability probe 中已回读的 7 个 primitive 行整理进 showcase，并补入 `drawing_standard.beta.drawing_standard_beta_04` suite 行。
- **Showcase**：新增 `showcase/L1/primitive_probe_matrix/` gallery，并在 `showcase_index.json` 追加 8 个条目。
- **Registry / 表 C**：`primitive.arc/circle/dimension/line/polyline/rectangle/text` 与 `drawing_standard.beta.drawing_standard_beta_04` 从 `verified` 升到 `showcase`；coverage 复跑后 CAD 证明覆盖率 **48.23%**、CAD 实力指数 **50.82%**、主指标升至 **8.87%**，最高 L4。

### V-PROOF-65：Showcase Second Wave

- **能力证明**：完成 `V-PROOF-65-SHOWCASE-SECOND-WAVE`，将 hatch、block-first、drawing-standard block insert 三组已验证能力整理进 showcase。
- **Showcase**：新增 `showcase/L1/primitive_hatch_smoke/`、`showcase/L1/symbol_block_first/`、`showcase/L0/drawing_standard_block_insert/` 三组 gallery，并在 `showcase_index.json` 追加 4 个条目。
- **Registry / 表 C**：`primitive.hatch`、`symbol.block_first.symbol_block_first_tier_01`、`symbol.block_first.controlled_block_wins`、`drawing_standard.beta.block_insert_plan_resolution` 从 `verified` 升到 `showcase`；coverage 复跑后 CAD 证明覆盖率 **48.23%**、CAD 实力指数 **50.82%**、主指标升至 **6.03%**，最高 L4。

### V-PROOF-64：Ladder Boundary + Block Matrix Showcase

- **能力证明**：完成 `V-PROOF-64-LADDER-BOUNDARY-DOC`，新增 `docs/verification/capability_ladder_boundaries.md`，把 Ladder L0-L5 与“能声称 / 不能声称”边界集中成页。
- **Showcase**：新增 `docs/verification/capability_showcase/showcase/L2/block_insert_matrix/gallery_index.json`，将 `block.insert_block_alpha.matrix` 绑定到 `RCAD-24` 的 8/8 real CAD block_reference readback suite。
- **Registry / 表 C**：`block.insert_block_alpha.matrix` 从 `verified` 升到 `showcase`；coverage 复跑后 CAD 证明覆盖率 **48.23%**、CAD 实力指数 **50.82%**、主指标升至 **4.61%**，最高 L4。

### V-PROOF-45：Block Beta Rows 回写表 C

- **能力证明**：完成 `V-PROOF-45-BLOCK-BETA-ROWS`，把 `RCAD-24` 的 `block_alpha_beta_summary.json` 作为 suite 级真实 CAD readback 证据回写。
- **代码**：`capability_registry_writeback` 现在只在 `status=pass`、`non_cad_only=false`、`geometry_verified_count>0` 且 `evidence_summary` 声明 `readback_geometry_verified` 时接受 suite summary；no-CAD suite 仍拒绝。
- **Registry / 表 C**：`block.insert_block_alpha.matrix` 从 `smoke` 升到 `verified`；coverage 复跑后 CAD 证明覆盖率 **48.23%**、CAD 实力指数 **50.82%**、主指标仍 **4.26%**。

### V-PROOF-41：Block CAD Matrix

- **代码链路**：`insert_block_alpha` 安全 allowlist 扩为 `controlled-test-block-001/002` 两个受控测试块；仍限定 `CODEX_PREVIEW`、统一缩放、无属性写入，不扩大到项目块库。
- **产物**：新增 `examples/plans/block_cad_matrix_vproof_41.json`，更新 block alpha plan/COM driver/fake driver/beta suite 与 RBLOCK-05 合约文档。
- **证据**：`output/validation_runs/vproof-41-block-cad-matrix-20260527-cad/block_alpha_beta_summary.json` 为 2/2 `geometry_verified`；`block.library.controlled_test_block_002` 已回写 verified。
- **边界**：只证明两个受控测试块的 preview-only block reference 插入与回读，不扩大到任意项目块库、属性块、正式图层或施工图块。

### V-PROOF-40：Block Matrix Plan 表 C 收口

- **能力证明**：完成 `V-PROOF-40-BLOCK-MATRIX-PLAN`，正式收口 block insert matrix 的 anchor / rotation / scale / attribute 维度表。
- **证据**：`scripts/run_block_matrix_registry_sync.py --output output/validation_runs/vproof-40-block-matrix-plan-no-cad --apply` 通过，输出 `block_matrix_registry_sync_summary.json`；`matrix_status=pass`，5 个 binding applied，0 rejected。
- **修复**：`run_block_matrix_registry_no_cad_sync()` 现在会把相对 output 路径解析到 project root 下，避免 CLI 相对路径触发 `relative_to(project_root)` 失败；新增 focused 回归测试。
- **Registry / 表 C**：`block.insert_block_alpha.matrix` 仅写入 smoke evidence；4 个维度 verified 行保留既有真实 CAD readback 证据，只追加 matrix manifest 来源。coverage 复跑后仍为 CAD 证明覆盖率 **47.87%**、CAD 实力指数 **50.75%**、真实 CAD 实力主指标 **4.26%**。
- **口径**：能力证明台账更新为 **29/43（约 67%）**，next=`V-PROOF-41-BLOCK-CAD-MATRIX`。本包不运行真实 CAD，不新增 `geometry_verified`。

### V-PROOF-43：Composition CAD 复验 + 表 C 抬升

- **推进表 C**：完成 `V-PROOF-43-COMPOSITION-CAD-RERUN`；真实 CAD 刷新 interior 3 case + office 4 case 升 `showcase`。
- **真实 CAD**：`vproof-43-composition-rerun-20260528-cad` 3/3 `geometry_verified`（40 handles）；`vproof-tablec-office-composition-20260528-cad` 4/4（40 handles）；只写 `CODEX_PREVIEW`。
- **Registry**：`writeback_apply.json` applied **7/7**；4 行 `verified`→`showcase`（office composition）；3 行 showcase 证据路径刷新。
- **表 C**：主指标 **8.87%→10.28%**；`showcase_count` 25→29；`verified_count` 112→108；瓶颈仍为 showcase 门（min 门）。

### RESIDENTIAL-PROD-03：Residential P3 父包收口

- **一键推进**：完成 `RESIDENTIAL-PROD-03-RESIDENTIAL-P3-WAVE-ROLLUP`，收口住宅 alpha + beta 子包与 no-CAD 复跑。
- **证据**：`res-prod-03-p3-rollup-no-cad/residential_p3_wave_summary.json`；alpha pass + beta 8/8。
- **口径**：代码轨 **52/55（约 95%）**；next=LCAD-10 父包收口。不抬表 C。

### RESIDENTIAL-PROD-02：Residential Beta 边界

- **一键推进**：完成 `RESIDENTIAL-PROD-02-RESIDENTIAL-BETA-BOUNDARY`，住宅 scene beta 8 case + registry 8 行收成 P3 契约。
- **证据**：`res-prod-02-boundary-no-cad/residential_beta_boundary_summary.json`；8/8 pass，7×`benchmark_pass_non_cad` + 1×`blocked_expected_non_cad`。
- **口径**：代码轨 **51/55（约 93%）**；next=`RESIDENTIAL-PROD-03`。不抬表 C。

### RESIDENTIAL-PROD-01：Residential Alpha 边界

- **一键推进**：完成 `RESIDENTIAL-PROD-01-RESIDENTIAL-ALPHA-BOUNDARY`，补齐 P3 住宅 alpha 与 `OFFICE-PROD-01` / `REST-PROD-01` 对称的 manifest + contract。
- **产物**：`residential_alpha_boundary.py`、`residential_prod_alpha_manifest.json`、`residential_prod_01_residential_alpha_boundary.md`、CLI 与 7 项 focused test。
- **证据**：`output/validation_runs/res-prod-01-boundary-no-cad/residential_alpha_boundary_summary.json` 为 `status=pass`；`scene_alpha_residential_blank_shell` no-CAD、`along_wall` 动线、`benchmark_pass_non_cad`。
- **口径**：代码轨 **50/55（约 91%）**；next=`RESIDENTIAL-PROD-02`（scheduled）。不运行真实 CAD，不抬表 C。

### SCENE-PROD-06：多场景回归门禁

- **一键推进**：完成 `SCENE-PROD-06-MULTI-SCENE-REGRESSION-GATE`，把 office / residential / restaurant 三套 scene beta benchmark 汇总为一个 no-CAD gate。
- **产物**：新增 `core/agents/scene_regression_gate.py`、`scripts/run_scene_prod_06_regression_gate.py`、`docs/verification/scene_prod_06_multi_scene_regression_gate.md` 与 `tests/core/test_scene_prod_06_regression_gate.py`。
- **证据**：`output/validation_runs/scene-prod-06-regression-gate-no-cad/scene_regression_gate_summary.json` 顶层 `status=pass`；25/25 selected benchmark pass，21 个 `benchmark_pass_non_cad`、4 个 `blocked_expected_non_cad`、`readback_geometry_verified_count=0`；repo audit 0 findings。
- **口径**：代码轨更新为 **49/55（约 89%）**；本包不连接 AutoCAD，不新增真实 CAD `geometry_verified`，不把场景偏好和 benchmark 通过扩大为 Scene Product。

### RCAD-06：Hatch COM 受控 smoke 真实 CAD 补验

- **CAD 补验**：完成 `RCAD-06-HATCH`；`AutoCADComDriver.draw_hatch()` 现在支持受控真实 COM hatch smoke，先写闭合 boundary polyline，再写 ANSI31 hatch，仍由 preview-only guard 保护。
- **产物**：新增 `core/verification/hatch_cad_smoke.py`、`scripts/run_hatch_cad_smoke.py`、`tests/core/test_hatch_cad_smoke.py`；更新 `docs/verification/hatch_com_deferred_boundary.md`，把 real COM verified 与 fake/no-CAD deferred 分开。
- **真实 CAD 证据**：`output/validation_runs/rcad-06-hatch-cad-20260527-escalated/hatch_cad_smoke_report.json` 为 `status=geometry_verified`、`evidence_state=readback_geometry_verified`，created handles `61C` / `61D`，回读 `hatch=1`、`polyline=1`，pattern `ANSI31`，bbox `100 x 80`。
- **Registry / 表 C**：`primitive.hatch` 由 `deferred` 回写为 `verified`；`hatch_writeback.json` applied 1。复跑 coverage 后，`total_count=282`、`verified_count=123`、`showcase_count=12`、CAD 证明覆盖率 **47.87%**、CAD 实力指数 **50.75%**、真实 CAD 实力主指标 **4.26%**、最高已证 **L4**。
- **口径**：RCAD 烟囱更新为 **29/29 verified**；只证明受控 `CODEX_PREVIEW` ANSI31 hatch smoke，不扩大到任意 hatch、正式图层或施工图交付。

### RCAD-28：BETA-CAD-BLOCK evidence rollup + trend 补验

- **CAD 补验**：完成 `RCAD-28-BETA-EVIDENCE-ROLLUP`；`scripts/run_cad_beta_evidence_rollup.py --output-root output/validation_runs/rcad-28-beta-evidence-rollup-20260527-final` 输出 `status=pass`，5/5 subpackages pass。
- **Trend hook**：`core/verification/cad_beta_evidence_rollup.py` 新增 `cad_beta_evidence_rollup_trend.json` 输出，并用 `validate_evidence_trend_report()` 硬校验。
- **测试**：`tests/core/test_cad_beta_block_acceptance.py` 固定 trend 文件存在、schema 校验 0 errors、`non_cad_only=true`、`geometry_verified_count=0`、`dry_run_valid_plan_only_count=5`。
- **边界**：本包按设计是 non-CAD 父包 evidence rollup，不连接 AutoCAD、不新增 created handles、不提升表 C；本条为历史快照，RCAD 烟囱当时为 **28/29 verified**，当前已随 `RCAD-06-HATCH` 更新为 **29/29 verified**。
- **表 C**：本条为历史快照；当前最新 coverage 为 `total_count=282`、`verified_count=112`、`showcase_count=25`、CAD 证明覆盖率 **48.58%**、CAD 实力指数 **51.03%**、真实 CAD 实力主指标 **8.87%**、最高已证 **L4**。

### RCAD-27：local CAD regression trend rollup 真实 CAD 补验

- **CAD 补验**：完成 `RCAD-27-TREND-ROLLUP-CAD`；`scripts/run_local_cad_regression.py --strict` 在用户 AutoCAD 会话完成 local CAD regression strict 矩阵。
- **证据**：真实 CAD 输出 `output/validation_runs/rcad-27-trend-rollup-cad-20260527-escalated/local_cad_regression_report.json`，`status=pass`，9/9 `geometry_verified_case_count`，created handles 105；趋势复算输出 `output/validation_runs/rcad-27-trend-rollup-cad-20260527-escalated/evidence_trend/local_cad_regression_trend.json`。
- **前置修正**：no-CAD 兼容矩阵先暴露 `tests/core/test_planmd_governance.py` 中旧进度断言仍找 `94%`，已同步为当前 `CORE_STATUS.md` 的 `95%`。
- **安全边界**：只写 `CODEX_PREVIEW` / `CODEX_DIAGNOSTIC` 允许层，未保存 DWG、未删除实体、未修改正式图层；截图仍仅作视觉辅助，几何证明以 created handles 回读为准。
- **口径**：RCAD 烟囱更新为 **27/29 verified**，next=`RCAD-28-BETA-EVIDENCE-ROLLUP`；本轮未回写 registry / showcase，因此表 C 机器值不变。

### RCAD-24：block alpha beta 真实 CAD 补验

- **CAD 补验**：完成 `RCAD-24-BLOCK-ALPHA-BETA`；`scripts/run_block_alpha_beta_suite.py --connect-cad` 现在可逐个执行 8 个 beta case，并用 created handles 回读 `block_reference`。
- **几何修正**：`core/block_engine/block_placement.py` 的 block bbox 从“宽深互换近似”修正为围绕 insertion point 旋转四角后取外包框，匹配 AutoCAD 的 block reference bbox。
- **证据**：真实 CAD 复跑输出 `output/validation_runs/rcad-24-block-beta-cad-after-rotfix-20260527/block_alpha_beta_summary.json`，`status=pass`，8/8 `geometry_verified`，created handles `373`~`37A`，全部在 `CODEX_PREVIEW`。
- **验证**：`python -m unittest tests.core.test_block_engine tests.core.test_block_alpha_beta_suite` → 19 tests OK；no-CAD suite 8/8 pass 且 `geometry_verified_count=0`；真实 CAD suite 8/8 `geometry_verified`。
- **口径**：RCAD 烟囱更新为 **26/29 verified**；本轮未改 registry / showcase / coverage，因此表 C 机器值不变。

### SCENE-PROD-05：Scene Beta 解释模板收口

- **一键推进**：完成 `SCENE-PROD-05-SCENE-EXPLANATION-TEMPLATE`；新增 scene beta explanation helper、边界文档、CLI 和 focused test，说明三场景 preferences 如何影响 Core / benchmark。
- **产物**：`scene_beta_explanation.py`、`scene_prod_05_scene_explanation_template.md`、`run_scene_beta_explanation_template.py`、`test_scene_prod_05_scene_explanation_template.py`。
- **验证**：先写测试并观察缺模块失败；实现后 focused 5 tests OK，`run_scene_beta_explanation_template.py` 输出 `status=pass`，三场景解释对象可机器读取。
- **口径**：代码轨 **48/55（约 87%）**，next=`SCENE-PROD-06-MULTI-SCENE-REGRESSION-GATE`。本包只证明 no-CAD explanation contract，不新增真实 CAD `geometry_verified`。

### REST-PROD-04：P3 多场景父包收口

- **一键推进**：完成 `REST-PROD-04-MULTI-SCENE-P3-ROLLUP`；新增跨场景 P3 parent contract、acceptance 文档、CLI 和 focused test，统一收口 office / restaurant 两个 P3 父包。
- **产物**：`multi_scene_p3_wave.py`、`rest_prod_04_multi_scene_p3_rollup_acceptance.md`、`run_multi_scene_p3_rollup.py`、`test_rest_prod_04_multi_scene_p3_rollup.py`。
- **验证**：先写测试并观察缺模块失败；实现后 focused 5 tests OK，`run_multi_scene_p3_rollup.py` 输出 `status=pass`，alpha 19 + beta 17 no-CAD case 可审计。
- **口径**：代码轨 **47/55（约 85%）**，next=`SCENE-PROD-05-SCENE-EXPLANATION-TEMPLATE`。本包只证明 no-CAD parent contract / `benchmark_pass_non_cad`，不新增真实 CAD `geometry_verified`。

### REST-PROD-03：餐饮 P3 波次父包收口

- **一键推进**：完成 `REST-PROD-03-RESTAURANT-P3-WAVE-ROLLUP`；按 `OFFICE-PROD-03` 模式新增 restaurant P3 parent contract、acceptance 文档、CLI 和 focused test。
- **产物**：`restaurant_p3_wave.py`、`restaurant_prod_03_p3_wave_acceptance.md`、`run_restaurant_p3_wave_rollup.py`、`test_rest_prod_03_p3_wave_rollup.py`。
- **验证**：先写测试并观察缺模块失败；实现后 focused 6 tests OK，`run_restaurant_p3_wave_rollup.py --run-benchmarks` 输出 `status=pass`，alpha case + beta 8/8 no-CAD 通过。
- **口径**：代码轨 **46/55（约 84%）**，next=`REST-PROD-04-MULTI-SCENE-P3-ROLLUP`。本包只证明 no-CAD contract / `benchmark_pass_non_cad`，不新增真实 CAD `geometry_verified`。

### REST-PROD-02：餐饮 beta 边界收口

- **一键推进**：完成 `REST-PROD-02-RESTAURANT-BETA-BOUNDARY`；按 `OFFICE-PROD-02` 模式新增 restaurant beta contract、manifest、边界文档、CLI 和 focused test。
- **产物**：`restaurant_beta_boundary.py`、`restaurant_prod_beta_manifest.json`、`restaurant_prod_02_restaurant_beta_boundary.md`、`run_restaurant_beta_boundary_contract.py`、`test_rest_prod_02_restaurant_beta_boundary.py`。
- **验证**：先写测试并观察缺模块失败；实现后 focused 6 tests OK；restaurant beta benchmark 8/8 no-CAD pass（7 pass + 1 blocked_expected）。
- **口径**：代码轨 **45/55（约 82%）**；next=`REST-PROD-03-RESTAURANT-P3-WAVE-ROLLUP`。本包只证明 no-CAD contract / `benchmark_pass_non_cad`，不新增真实 CAD `geometry_verified`。

### REST-PROD-01：餐饮 alpha 边界收口

- **一键推进**：完成 `REST-PROD-01-RESTAURANT-ALPHA-BOUNDARY`；按 `OFFICE-PROD-01` 模式新增 restaurant alpha contract、manifest、边界文档、CLI 和 focused test。
- **产物**：`restaurant_alpha_boundary.py`、`restaurant_prod_alpha_manifest.json`、`restaurant_prod_01_restaurant_alpha_boundary.md`、`run_restaurant_alpha_boundary_contract.py`、`test_rest_prod_01_restaurant_alpha_boundary.py`。
- **验证**：先写测试并观察缺模块失败；实现后 focused 7 tests OK；CLI 输出 `output/validation_runs/rest-prod-01-boundary-no-cad/restaurant_alpha_boundary_summary.json`，`status=pass`。
- **口径**：该轮代码轨为 **44/55（约 80%）**；后续已推进到 `REST-PROD-02`。本包只证明 no-CAD contract / `benchmark_pass_non_cad`，不新增真实 CAD `geometry_verified`。

### V-PROOF-35：fallback tier rows 表 C 推进

- **能力证明**：完成 `V-PROOF-35-FALLBACK-TIER-ROWS`；`cad_capability_registry` 新增 `symbol.fallback_tier.block`、`symbol.fallback_tier.symbol_glyph`、`symbol.fallback_tier.component_preview`、`symbol.fallback_tier.bbox_placeholder`、`symbol.fallback_tier.deferred_unsupported_symbol` 5 行。
- **边界**：4 行为 `smoke`，1 行为 `deferred`；全部保持 `not_verified_without_cad_readback`，不把 fallback 解析 / dry-run / deferred 扩大为 `geometry_verified`。
- **契约**：`assert_symbol_glyph_fallback_boundary_contract()` 现在检查 V-PROOF-35 行存在且不得为 `verified/showcase`。
- **表 C**：本条为历史快照；当前最新 coverage 为 `total_count=282`、CAD 证明覆盖率 **48.58%**（137/282；112 verified + 25 showcase）、CAD 实力指数 **51.03%**、真实 CAD 实力主指标 **8.87%**、最高已证 **L4**。
- **验证**：focused 21 tests OK；`scripts/run_capability_coverage.py --output output/validation_runs/capability-lab/cad_capability_coverage.json` pass。本轮未运行真实 CAD。

### 诊断层隔离小收口：探针标注不再污染 `CODEX_PREVIEW`

- **问题**：能力探针 / complex smoke 为验证 `draw_text` 与 `add_dimension` 会绘制文字和尺寸，旧实现把这些诊断对象与几何探针一起写入 `CODEX_PREVIEW`，容易在用户视口里看起来像“生成图块仍带标注”。
- **变更**：新增 `CODEX_DIAGNOSTIC` 作为 preview-only 允许诊断层；`cad_capability_probe` 与 `complex_cad_smoke` 将文字和尺寸写入诊断层，几何对象仍写入 `CODEX_PREVIEW`。
- **加固**：诊断层写入现在必须显式传入 `layer_role="diagnostic"`；默认 preview 角色写 `CODEX_DIAGNOSTIC` 会被 `CadWriteGuard` 拦截，避免诊断层被误用为第二个普通出图层。
- **证据**：报告新增 `diagnostic_layer`、`preview_type_counts`、`diagnostic_type_counts` 和双层 `layer_counts`，用于区分用户可见几何与诊断标注。
- **验证**：`python -m unittest tests.core.test_autocad_write_guard tests.core.test_cad_capability_probe tests.core.test_complex_cad_smoke` 通过。

### V-PROOF-44 + RCAD-23：drawing standard beta 表 C 推进

- **能力证明**：完成 `V-PROOF-44-DRAWING-STANDARD-ROWS` 的真实 CAD 子集回写；只升级 suite 与 `block_insert_plan_resolution`。
- **真实 CAD**：`scripts/run_drawing_standard_cad_smoke.py` 在用户 AutoCAD 会话通过；证据 `output/validation_runs/rcad-23-drawing-standard-beta-20260527-escalated/drawing_standard_cad_smoke_report.json` 为 `status=geometry_verified`，created handle `36A`，styled `insert_block_alpha` 在 `CODEX_PREVIEW` 回读为 `block_reference`。
- **登记**：`drawing_standard.beta.drawing_standard_beta_04` 与 `drawing_standard.beta.block_insert_plan_resolution` 回写 `verified`；object role、primitive style、semantic layer case 保持 smoke。
- **表 C**：复跑 coverage 后，CAD 证明覆盖率 **48.38%**（134/277；122 verified + 12 showcase），CAD 实力指数 **51.33%**，真实 CAD 实力主指标仍 **4.33%**（showcase readiness 瓶颈），最高已证 **L4**。
- **验证**：focused 23 tests OK；`--no-cad` deferred 报告 OK；沙箱内 COM 为 `external_blocker`，沙箱外用户 CAD 会话验证通过。

### V-PROOF-34 + RCAD-25：block-first 表 C 推进

- **能力证明**：完成 `V-PROOF-34-BLOCK-FIRST-ROW`；把 SYMBOL-09 block-first suite 与 `controlled-block-wins` 从 smoke 推进到真实 CAD verified。
- **真实 CAD**：`scripts/run_symbol_block_first_cad_smoke.py` 在用户 AutoCAD 会话通过；证据 `output/validation_runs/rcad-25-symbol-block-first-20260527-escalated/symbol_block_first_cad_smoke_report.json` 为 `status=geometry_verified`，created handle `369`，`CODEX_TEST_BLOCK_001` 在 `CODEX_PREVIEW` 回读为 `block_reference`。
- **登记**：仅 `symbol.block_first.symbol_block_first_tier_01` 与 `symbol.block_first.controlled_block_wins` 回写 `verified`；两个 glyph fallback case 保持 smoke。
- **表 C**：复跑 coverage 后，CAD 证明覆盖率 **47.65%**（132/277；120 verified + 12 showcase），CAD 实力指数 **51.19%**，真实 CAD 实力主指标仍 **4.33%**（showcase readiness 瓶颈），最高已证 **L4**。
- **验证**：focused 17 tests OK；`--no-cad` deferred 报告 OK；沙箱内 COM 为 `external_blocker`，沙箱外用户 CAD 会话验证通过。

### OFFICE-PROD-03：办公 P3 波次父包收口

- **一键推进**：完成 `OFFICE-PROD-03-OFFICE-P3-WAVE-ROLLUP`；收口 `OFFICE-PROD-01` alpha 边界与 `OFFICE-PROD-02` beta 边界。
- **产物**：`office_p3_wave.py`、`run_office_p3_wave_rollup.py`、`office_prod_03_p3_wave_acceptance.md`、`test_office_prod_03_p3_wave_rollup.py`。
- **验证**：focused 6 tests OK；CLI summary pass；office alpha 18/18 no-CAD，office beta 9/9 no-CAD（7 pass + 2 blocked_expected）。
- **口径**：代码轨 **43/55（约 78%）**；next=`REST-PROD-01-RESTAURANT-ALPHA-BOUNDARY`。本包未运行真实 CAD，不新增 `geometry_verified`。

### RCAD-22：capability probe beta 真实 CAD 补验

- **CAD 补验**：`scripts/run_cad_capability_probe.py` 在用户 AutoCAD 会话 `Drawing1.dwg` 通过；`status=cad_capability_verified`。
- **证据**：`output/validation_runs/rcad-22-capability-probe-beta-20260527-escalated/cad_capability_probe.json`，11 handles，全部在 `CODEX_PREVIEW`，bbox 900×450，`session_guard.status=consistent`。
- **登记**：刷新 `primitive.arc/circle/dimension/line/polyline/rectangle/text` 的 report path；`primitive.hatch` 保持 deferred，不计作几何 verified。
- **口径**：RCAD **23/29（约 79%）**；next=`RCAD-23-DRAWING-STANDARD-BETA`。当前表 C 机器值为真实 CAD 实力主指标 **4.33%**、CAD 证明覆盖率 **46.93%**。

### 最终回复精简口径：默认轻量表，按需展开 A/B/C

- 按用户反馈，把 CAD Agent 聊天最终回复从“默认完整三表”改为“默认 1 张精简进度表”：表 C 主指标优先、本轮进展 / 验证、表 A 折叠工程节奏、表 B 本轮相关中文轨道（能力证明 / 代码轨 / CAD 补验）。
- 保留完整 A/B/C 作为状态页、交接、审计、进度盘点和表 C 专题的展开模板；无论精简或展开，都不得省略表 C 主指标或混用工程进度、任务台账与真实 CAD 实力。
- 明确本次不重构 §3 43 包、§4 55 包、§5 29 包真实分母；只允许在最终回复里做展示聚合。
- 同步 `AGENTS.md`、`CAD_AGENT_RULES.md`、`README.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`docs/planning/任务清单.md`、`docs/onboarding/first-handoff.md` 与 `capability_proof_status_template.md` 的口径。
- 本轮是文档规则治理，不新增真实 CAD `geometry_verified` 能力。

### 文档治理收尾：表 A/B/C 与主从关系同步

- 复跑 `scripts/run_capability_coverage.py --output output/validation_runs/capability-lab/cad_capability_coverage.json`，当前机器值为 `total_count=277`、`cad_proof_count=130`、CAD 证明覆盖率 **46.93%**、真实 CAD 实力主指标 **4.33%**、最高已证 **L4**。
- 同步 `docs/planning/任务清单.md` §0：能力证明约 **24/43** done，代码轨约 **42/55** done，RCAD 烟囱 **22/29** verified；明确表 B 不等于表 C。
- 压缩 `CORE_CONTEXT_BRIEF.md` 为短入口，保留当前结论、三表快照、next、不能声称和按需展开表，旧流水继续查 changelog / handoff / history。
- 加固主从关系：`CORE_RESTRUCTURE_PLAN.md` 决定方向、优先级和退出门槛；`docs/planning/任务清单.md` 只做执行台账和即时 `next` 镜像；README、状态页、handoff 不再生成第三套计划。
- 同步 `tests/core/test_capability_coverage.py` 的 showcase 断言，避免测试仍假设 seed registry 没有 showcase 行。
- 收口 repo audit 尾巴：7 个新脚本改用共享 `scripts/_bootstrap.py`，不再直接 `sys.path.insert`。
- 本轮为文档治理和状态同步，不新增真实 CAD `geometry_verified` 能力。

### RCAD-15：沙发 symbol glyph 真实 CAD 补验

- **CAD 补验**：`run_symbol_glyph_cad_smoke.py` + `seating_sofa_plan.json`；`status=geometry_verified`、6 handles、仅 `CODEX_PREVIEW`。
- **证据**：`output/validation_runs/rcad-15-symbol-glyph-sofa-20260527/symbol_glyph_cad_smoke_report.json`
- **登记**：`object.sofa.glyph` 证据路径刷新；`symbol.spec.symbol_sofa_plan` 保持 `showcase`（writeback 曾误降为 verified，已手工恢复）。
- **口径**：RCAD **22/29（约 76%）**；next=`RCAD-22` / `RCAD-23`。

### OFFICE-PROD-02：P3 办公 beta 边界（第二包）

- **一键推进**：完成 `OFFICE-PROD-02-OFFICE-BETA-BOUNDARY`；链式 alpha + scene_beta 9 case。
- **产物**：`office_beta_boundary.py`、`office_prod_beta_manifest.json`、`office_prod_02_office_beta_boundary.md`（6 tests OK）。
- **口径**：**41/55（约 75%）**；next=`REST-PROD-01` 或 `OFFICE-PROD-03`。本包未运行真实 CAD。

### OFFICE-PROD-01：P3 办公 alpha 边界（进波首包）

- **一键推进**：完成 `OFFICE-PROD-01-OFFICE-ALPHA-BOUNDARY`；P3 他场景产品化进波。
- **产物**：`office_alpha_boundary.py`、`office_prod_alpha_manifest.json`、`office_prod_01_office_alpha_boundary.md`（7 tests OK）。
- **口径**：**40/55（约 73%）**；next=`OFFICE-PROD-02`。本包未运行真实 CAD。

### CORE-P4：P4 Core 波次父包收口

- **一键推进**：完成 `CORE-P4-WAVE-PARENT-ROLLUP`；`DRAW-01`/`02` + `SYMBOL-08`/`09` rollup + acceptance。
- **产物**：`p4_core_wave.py`、`p4_core_wave_acceptance.md`、`test_p4_core_wave_parent_rollup.py`（6 tests OK）。
- **口径**：**39/52（约 75%）**；P4/P5 波次已收口；next=P3 `user_gate`。本包未运行真实 CAD。

### RBLOCK-08：P5 图块波次父包收口

- **一键推进**：完成 `RBLOCK-08-P5-WAVE-PARENT-ROLLUP`；`RBLOCK-03`~`07` rollup + acceptance。
- **产物**：`block_p5_wave.py`、`block_p5_wave_acceptance.md`、`test_rblock_08_p5_wave_parent_rollup.py`（6 tests OK）。
- **口径**：**38/51（约 75%）**；§4.2 P5 已收口。本包未运行真实 CAD。

### RBLOCK-07：块矩阵 registry 行绑定

- **一键推进**：完成 `RBLOCK-07-BLOCK-MATRIX-REGISTRY-ROWS`；5 行 registry 绑定 + matrix smoke writeback API。
- **产物**：`block_matrix_registry.py`、`cad_capability_registry.json`（+1 smoke 行）、`rblock_07_block_matrix_registry_rows.md`（8 tests OK）。
- **口径**：**37/51（约 73%）**；next=`RBLOCK-08-P5-WAVE-PARENT-ROLLUP`。本包未运行真实 CAD。

### RBLOCK-06：属性块探针边界

- **一键推进**：完成 `RBLOCK-06-BLOCK-ATTRIBUTE-BOUNDARY`；`BETA-CAD-BLOCK-02` manifest + 契约 + attribute deferred smoke。
- **产物**：`block_attribute_boundary.py`、`block_attribute_probe_manifest.json`、`rblock_06_block_attribute_boundary.md`（7 tests OK）。
- **口径**：**36/51（约 71%）**；next=`RBLOCK-07-BLOCK-MATRIX-REGISTRY-ROWS`。本包未运行真实 CAD。

### RBLOCK-05：第二受控测试块 metadata

- **一键推进**：完成 `RBLOCK-05-SECOND-CONTROLLED-BLOCK`；`controlled-test-block-002` library + sidecar；`insert_block_alpha` allowlist 未放宽。
- **产物**：`second_controlled_block_manifest.json`、`second_controlled_block_boundary.py`、`rblock_05_second_controlled_block.md`（8 tests OK）。
- **口径**：**35/51（约 69%）**；next=`RBLOCK-06-BLOCK-ATTRIBUTE-BOUNDARY`。本包未运行真实 CAD。

### RBLOCK-04：块插入矩阵 manifest

- **一键推进**：完成 `RBLOCK-04-BLOCK-MATRIX-MANIFEST`；anchor/rotation/scale/attribute 四维矩阵 + registry 四行绑定。
- **产物**：`block_insert_matrix_manifest.json`、`block_matrix_manifest.py`、`run_block_insert_matrix_manifest.py`、`rblock_04_block_matrix_manifest.md`（7 tests OK）。
- **口径**：**34/51（约 67%）**；next=`RBLOCK-05-SECOND-CONTROLLED-BLOCK`。本包未运行真实 CAD。

### RBLOCK-03：P5 受控 block alpha 边界

- **一键推进**：完成 `RBLOCK-03-BLOCK-ALPHA-BOUNDARY`；P5 图块波次进队。
- **产物**：`block_alpha_boundary.py`、`rblock_03_block_alpha_boundary.md`（5 tests OK）。
- **口径**：**33/51（约 65%）**；next=`RBLOCK-04-BLOCK-MATRIX-MANIFEST`。本包未运行真实 CAD。

### SYMBOL-09：block-first tier 机器入口

- **一键推进**：完成 `SYMBOL-09-BLOCK-FIRST-TIER`；block-first smoke + registry 四行。
- **产物**：`block_first_tier.py`、`block_first_boundary.py`、`symbol_block_first_tier_manifest.json`、`run_block_first_tier_smoke.py`（7 tests OK）。
- **口径**：**32/50（约 64%）**；§4.2 P4 收口；next=P5 或 P3。本包未运行真实 CAD。

### SYMBOL-08：symbol glyph 四级 fallback 边界

- **一键推进**：完成 `SYMBOL-08-GLYPH-FALLBACK-BOUNDARY`；fallback tier 契约 + 无静默退化 benchmark 复验。
- **产物**：`symbol_fallback_boundary.py`、`symbol_08_glyph_fallback_boundary.md`、`test_symbol_08_glyph_fallback_boundary.py`（+ 复用 fallback policy 6 tests）。
- **口径**：**31/50（约 62%）**；next=`SYMBOL-09-BLOCK-FIRST-TIER`。本包未运行真实 CAD。

### DRAW-02：drawing standard registry 行绑定

- **一键推进**：完成 `DRAW-02-DRAWING-STANDARD-REGISTRY-ROWS`；登记表 +7 行；smoke evidence writeback API。
- **产物**：`drawing_standard_registry.py`、`draw_02_drawing_standard_registry_rows.md`、`test_draw_02_drawing_standard_registry_rows.py`（8 tests OK）。
- **口径**：**30/50（约 60%）**；next=`SYMBOL-08-GLYPH-FALLBACK-BOUNDARY`。本包未运行真实 CAD。

### DRAW-01：P4 Core 首包 — drawing standard 边界

- **一键推进**：完成 `DRAW-01-DRAWING-STANDARD-BOUNDARY`；P4 Core 波次进队。
- **产物**：`drawing_standard_boundary.py`、`draw_01_drawing_standard_boundary.md`、`test_draw_01_drawing_standard_boundary.py`（4 tests OK）；no-CAD beta suite 6/6。
- **口径**：**29/50（约 58%）**；next=`DRAW-02-DRAWING-STANDARD-REGISTRY-ROWS`。本包未运行真实 CAD。

### CFIT-13：P2 工装波次父包收口

- **一键推进**：完成 `CFIT-13-P2-WAVE-PARENT-ROLLUP`；收口 `CFIT-09`…`CFIT-12`。
- **产物**：`commercial_fitout_p2_wave.py`、`commercial_fitout_p2_wave_acceptance.md`、`test_cfit_13_p2_wave_parent_rollup.py`（6 tests OK）。
- **口径**：**28/49（约 57%）**；§4.2 P2 done；next 待 P3/P4 波次进队。本包未运行真实 CAD。

### V-PROOF-63：L4 工装双样本项目切片 + 表 C 抬升

- **§0.1**：`run_project_sample_cad_rollup.py` 真实 CAD **4/4**（含 meeting/reception 各 12 handles）。
- **Registry**：新增 L4 `project.sample.*` 2 行 + showcase；另 3 条 L3 室内组合升 showcase。
- **表 C**：主指标 **2.67% → 4.55%**；`highest_proven_ladder_level=L4`；登记 **49.24%**（130/264）。
- **能力证明**：**28/43（约 65%）**；next=`V-PROOF-34` 或 `V-PROOF-64`。

### V-PROOF-61 / 60：L2 符号画廊 + showcase 索引（表 C 抬升）

- **§0.1 推进表 C**：真实 CAD 跑通 desk/chair/table/sofa 四 glyph（`capability-proof-vproof61-20260527`）；另 2 条 L3 fitout composition 升为 `showcase`。
- **Showcase**：`showcase_index.json` 现 **7** 条（4×L2 + 3×L3）；`V-PROOF-60` done、`V-PROOF-61` done。
- **表 C**：主指标 **0.38% → 2.67%**；`showcase_count=7`；登记仍 **48.85%**（128/262）。
- **能力证明**：**27/43（约 63%）**；`RCAD-15` sofa 证据已刷新（可登记烟囱 verified）。

### V-PROOF-62：L3 工装微场景 showcase + 真实 CAD

- **§0.1 真实 CAD 实力**：`run_composition_cad_registry.py`（fitout manifest）真实 AutoCAD **3/3** `geometry_verified`（28 created handles）。
- **Showcase**：`docs/verification/capability_showcase/` + `showcase/L3/fitout_open_office_desk_chair/snippet_index.json`；registry 首条 `claim_level=showcase`（`composition.fitout_open_office_desk_chair`）。
- **表 C**：主指标 **0% → 0.38%**；`showcase_count=1`；登记仍 **48.85%**（128/262 cad_proof）。
- **能力证明**：**26/43（约 60%）**；`V-PROOF-60` partial；next=`V-PROOF-34` 或扩 showcase。

### 表 C：真实 CAD 实力与四进度口径

- **机器指标**：`capability_coverage.py` 新增 `cad_strength_*`（`cad_strength_headline_percent` = min(加权指数, L3+, showcase)）。
- **文档**：`AGENTS.md` 交付改为表 A+B+C；`任务清单.md` §0 四口径；§5 改称 RCAD 烟囱包；`RCAD-10/19/21` 登记 verified。
- **当前值**：主指标 **0%**（showcase=0）；实力指数 **50.52%**；L3+ **39.53%**；RCAD 烟囱 **69%**（20/29）。

### 口令：真实 CAD 实力 / 推进表 C

- **`任务清单.md` §0.1**：第四口令编排表 C（`V-PROOF` + 链式 RCAD + registry 回写 + coverage）；**刷新表 C** 仅复跑不新开包。
- **同步**：`AGENTS.md`、`CAD_AGENT_RULES.md`、`README.md`、`capability_proof_status_template.md`。

### 表 C 会话：RCAD-18 真实 CAD + registry 回写

- **CAD**：`capability-proof-table-c-20260527` — fitout subscene smoke 4/4 `geometry_verified`（真实 AutoCAD readback）。
- **Registry**：4 行 catalog `--apply`（meeting_table/chair、reception_desk、waiting_sofa 证据路径刷新）。
- **Coverage 复跑**：主指标仍 **0%**（showcase=0）；指数 **50.52%**；登记 **48.85%**（128/262）。
- **RCAD**：`RCAD-18` verified；烟囱 **21/29**。

### CFIT-12：fitout subscene representative object CAD smoke

- **一键推进**：完成 `CFIT-12-FITOUT-SUBSCENE-OBJECT-CAD-SMOKE`（对齐 `V-PROOF-25`）。
- **产物**：`fitout_subscene_object_cad_smoke_manifest.json`、`fitout_subscene_object_cad_smoke.py`、`run_fitout_subscene_object_cad_smoke.py`。
- **覆盖**：meeting_room 2 对象 + reception 2 对象；fake 4/4 geometry_verified。
- **口径**：**27/49（约 55%）**；next=`CFIT-13`。本包未运行真实 CAD；`RCAD-18` 脚本路径已就绪。

### CFIT-11：three-sample product boundary / rollup sync

- **一键推进**：完成 `CFIT-11-THREE-SAMPLE-BOUNDARY-SYNC`。
- **口径**：`product_alpha_boundary.json` 新增 `deidentified_project_samples[]`；`fitout_sample_specs` 增加 `subscene_id` / `project_rel`；`assert_fitout_three_sample_rollup_sync()` 纳入 product boundary 契约。
- **验证**：CFIT-11 5 tests + product boundary / rollup 14 tests OK；fake rollup 仍 4/4 geometry_verified。
- **口径**：**26/49（约 53%）**；next=`CFIT-12`。本包未运行真实 CAD。

### CFIT-10：reception commercial fitout project sample

- **一键推进**：完成 `CFIT-10-RECEPTION-PROJECT-SAMPLE`。
- **样本**：`projects/commercial_fitout_reception_sample/` + workflow；rollup 登记第四行。
- **三子场景样本**：open_office / meeting_room / reception 各一组脱敏样本路径。
- **验证**：CFIT-10 4 tests OK；rollup fake 4/4 geometry_verified。
- **口径**：**25/49（约 51%）**；next=`CFIT-11`。

### CFIT-09：second commercial fitout project sample

- **一键推进**：完成 `CFIT-09-SECOND-PROJECT-SAMPLE`（§4.2 P2 工装波次首包）。
- **样本**：新增 `projects/commercial_fitout_meeting_sample/` 与 `commercial_fitout_meeting_sample_confirmation_loop.json`。
- **多样本注册**：`fitout_sample_specs.py`；confirmation / CAD smoke / rollup 按 workflow 解析 `sample_id`。
- **rollup**：`project_sample_cad_rollup.json` 登记第三样本；fake driver 单测 3/3 geometry_verified。
- **口径同步**：一键推进 **24/49（约 49%）**；next=`CFIT-10`。本包未运行真实 CAD 项目补验。

### LCAD-14：guard full CAD strict rollup

- **一键推进**：完成 `LCAD-14-GUARD-FULL-CAD`，新增 `guard_full_cad_runner` 与 `run_guard_full_cad_runner.py`，strict 汇总 write guard、negative CAD、capability probe 三段子报告。
- **strict 门禁**：`guard_full_cad_report.json` 的 `strict_gate` 断言子报告 pass、`negative_guard_verified`、`cad_capability_verified` 与 `session_guard.status=consistent`。
- **边界文档**：新增 `docs/verification/guard_full_cad_boundary.md`；真实 AutoCAD 会话 strict 复验入口为 `RCAD-21`（`--real-cad`）。
- **测试**：focused 3 tests OK；no-CAD 证据 `output/validation_runs/lcad-14-guard-full-no-cad/`。
- **口径同步**：一键推进 **23/49（约 47%）**；§4.1 活跃队列已收口；§4.2 待波次。本包未运行真实 CAD，不新增 `geometry_verified`。

### LCAD-13：session snapshot in capability probe

- **一键推进**：完成 `LCAD-13-SESSION-SNAPSHOT-CAD`，把 `cad_session_guard` before/after snapshot 接入 `run_cad_capability_probe()`。
- **探针契约**：写入前采集 `after_connect`、写入后采集 `after_write`；报告含 `session_guard`，并写出 `active_document_snapshot.json`。
- **证据门禁**：`validate_capability_probe_evidence` 在 `cad_capability_verified` 时要求 `session_guard.status=consistent` 与 `active_document_identity_stable=pass`。
- **边界文档**：新增 `docs/verification/session_snapshot_capability_probe_boundary.md`，服务 `V-PROOF-52` guard/snapshot 字段断言边界。
- **测试**：focused session/probe/validation-runner tests OK；no-CAD 证据 `output/validation_runs/lcad-13-session-snapshot-no-cad/`；repo audit 0 findings。
- **口径同步**：一键推进进度更新为 **22/49（约 45%）**；next=`LCAD-14`。本包未运行真实 CAD，不新增 `geometry_verified`。

### LCAD-12：hatch COM structured deferred

- **一键推进**：完成 `LCAD-12-HATCH-COM`，选择安全 structured deferred 收口，不冒充真实 AutoCAD hatch 写入。
- **Driver 边界**：`AutoCADComDriver.draw_hatch()` 与 `FakeCadDriver.draw_hatch()` 都先执行 preview-only 写入守卫；预览层调用只返回 `primitive=hatch`、`status=deferred`、`failure_category=hatch_unverified`、`created_handles=[]`、`geometry_verified=false`。
- **安全口径**：真实 COM driver 不调用 `AddHatch`、不创建 handle；正式图层调用会在写入前被 `CadWriteGuardViolation` 拦截。
- **边界文档**：新增 `docs/verification/hatch_com_deferred_boundary.md`，固定 `V-PROOF-53` 当前只获得能力槽位和失败分类，不获得真实几何证明。
- **测试**：RED 阶段两个 driver 均缺 `draw_hatch`，边界文档不存在；补实现后 focused hatch tests 8 tests OK，聚焦回归 25 tests OK，沙箱外全量 685 tests OK。
- **口径同步**：一键推进进度更新为 **21/49（约 43%）**；next=`LCAD-13`。本包未运行真实 CAD，不新增 `geometry_verified`。

### CAD-VAL-02：environment gate optional

- **一键推进**：完成 `CAD-VAL-02-ENVIRONMENT-GATE-OPTIONAL`，`run_cad_validation` 新增 `environment_optional` / `--environment-optional` 显式模式。
- **门禁口径**：该模式下顶层 `status` 按 `geometry_gate` 计算；`unit_tests`、截图、Pillow / pywin32 / win32gui 等基础设施失败仍保留在 `infrastructure_gate`，并标记 `infrastructure_debt=true`。
- **边界文档**：新增 `docs/verification/cad_validation_environment_gate.md`，明确非几何失败不能混成几何失败，也不能被静默吞掉。
- **证据**：`output/validation_runs/cad-val-02-environment-optional/report.json`；当前沙箱内 `unit_tests` 受 Windows Temp ACL 误伤，报告为 `status=pass`、`legacy_status=fail`、`geometry_gate.status=pass`、`infrastructure_gate.failed_required_step_ids=[unit_tests]`。
- **测试**：RED 阶段 `run_cad_validation()` 不支持 `environment_optional`；补实现后 focused 16 tests OK。
- **口径同步**：一键推进进度更新为 **20/49（约 41%）**；next=`LCAD-12`。本包未运行真实 CAD，不新增 `geometry_verified`。

### LCAD-11.5：trend boundary doc

- **一键推进**：完成 `LCAD-11.5-TREND-BOUNDARY-DOC`，新增 `docs/verification/evidence_trend_boundaries.md`。
- **边界内容**：覆盖 `LCAD-11.1`~`11.4` 的 trend JSON、`local_cad_regression_trend.json`、`cad_validation_trend_index.json`、`capability_coverage_trend.json`、coverage `snapshot.metrics` 与 `V-PROOF-71` Dashboard 用途。
- **不得声称**：trend JSON、schema pass、no-CAD pass、截图、dry-run、coverage metric 均不能替代真实 AutoCAD created-handle readback；`cad_proof_coverage_rate` 不是几何准确率。
- **测试**：RED 阶段边界文档不存在；补文档后 `tests.core.test_evidence_trend_boundaries_doc` pass，focused 11 tests OK。
- **口径同步**：一键推进进度更新为 **19/49（约 39%）**；next=`CAD-VAL-02`。本包未运行真实 CAD，不新增 `geometry_verified`。

### LCAD-11.4：coverage trend hook

- **一键推进**：完成 `LCAD-11.4-COVERAGE-TREND-HOOK`，`run_capability_coverage` 在常规 `cad_capability_coverage.json` 外同步输出 `evidence_trend/capability_coverage_trend.json`。
- **趋势 hook**：复用统一 evidence trend schema；coverage 的 `total_count`、`verified_count`、`cad_proof_coverage_rate` 等 V-PROOF-02 字段放在 `snapshot.metrics`，不把本包伪装成新增几何证据。
- **证据**：`output/validation_runs/lcad-11-4-coverage-trend-hook/evidence_trend/capability_coverage_trend.json`；schema 校验无错误。coverage 仍为 262 行、128 verified、`cad_proof_coverage_rate=48.85%`。
- **测试**：RED 阶段 `trend_path.is_file()` 失败；补实现后 focused 18 tests OK，`run_capability_coverage.py --output output/validation_runs/lcad-11-4-coverage-trend-hook/cad_capability_coverage.json` 为 `status=pass`。
- **口径同步**：一键推进进度更新为 **18/49（约 37%）**；next=`LCAD-11.5`。本包未运行真实 CAD，不新增 `geometry_verified`。

### LCAD-11.3：cad validation 历史趋势索引

- **一键推进**：完成 `LCAD-11.3-VALIDATION-TREND-INDEX`，新增 `core/verification/cad_validation_trend_index.py`，`run_cad_validation` 每次写出 `report.json/md` 后同步生成 `evidence_trend/cad_validation_trend_index.json`。
- **趋势索引**：按同级 validation run 的 `report.json` 生成 `source_kind=cad_validation` snapshots，并复用 `LCAD-11.1` 的 evidence trend schema；历史真实 CAD snapshots 可进入索引，但 no-CAD snapshot 不会提升几何证明。
- **证据**：`output/validation_runs/lcad-11-3-validation-trend-index/evidence_trend/cad_validation_trend_index.json`；schema 校验无错误，当前 `snapshot_count=11`，包含本轮 no-CAD validation 报告。
- **测试**：RED 阶段缺少 `core.verification.cad_validation_trend_index`；补实现后新增 `tests/core/test_cad_validation_trend_index.py`。focused 26 tests OK；沙箱内 no-CAD validation 被 Windows Temp ACL 误伤，按审批沙箱外重跑 `run_cad_validation --no-cad` 为 `status=pass`，内部全量 `676 tests OK`。
- **口径同步**：一键推进进度更新为 **17/49（约 35%）**；next=`LCAD-11.4`。本包未运行真实 CAD，不新增 `geometry_verified`。

### LCAD-11.2：local CAD regression 趋势 JSON

- **一键推进**：完成 `LCAD-11.2-REGRESSION-TREND-JSON`，`run_local_cad_regression` 在主报告外同步输出 `evidence_trend/local_cad_regression_trend.json`。
- **趋势 rollup**：新增 local regression snapshot，汇总 `evidence_state_counts`、`geometry_accuracy_counts`、`screenshot_role_counts` 与 `summary`；no-CAD 运行固定为 deferred/non-CAD，不提升几何证明。
- **证据**：`output/validation_runs/lcad-11-2-regression-trend-json/evidence_trend/local_cad_regression_trend.json`；schema 校验无错误，`snapshot_count=1`、`deferred_cad_readback_count=8`、`geometry_verified_count=0`、`non_cad_only=true`。
- **测试**：RED 阶段 `trend_path.is_file()` 失败；补实现后新增 `tests/core/test_local_cad_regression_trend.py`。focused 24 tests OK；含治理测试 focused 31 tests OK；沙箱内 no-CAD 回归被 Windows Temp ACL 误伤，按审批沙箱外重跑 `run_local_cad_regression --no-cad` 为 `status=pass`，内部全量 `675 tests OK`。
- **口径同步**：一键推进进度更新为 **16/49（约 33%）**；next=`LCAD-11.3`。本包未运行真实 CAD，不新增 `geometry_verified`。

### V-PROOF-33：readability rows 绑定

- **能力证明**：`V-PROOF-33-READABILITY-REPORT-ROWS` 从 partial 收口为 done；`examples/capability_proof/cad_capability_registry.json` 新增 5 个 `symbol.readability_status.*` smoke 行。
- **Schema / 测试**：`cad_capability_registry.schema.json` 增加 `readability_status` 字段；`tests/core/test_capability_readability.py` 增加 registry 绑定断言，先 RED 后 GREEN。
- **证据**：`output/validation_runs/vproof-33-readability-rows/capability_readability_report.json` 与 `output/validation_runs/vproof-33-readability-rows/cad_capability_coverage.json`。
- **覆盖率**：登记表从 257 行扩为 **262** 行；`verified_count` 仍为 **128**，`cad_proof_coverage_rate=48.85%`。这是分母扩充，不新增真实 CAD `geometry_verified`。
- **校验**：focused 29 tests OK、全量 674 tests OK、repo audit 0 findings、`git diff --check` 无空白错误。
- **口径同步**：能力证明进度更新为 **24/43（约 56%）**；next=`V-PROOF-34` 或 fitout composition CAD。

### RCAD-20：真实 CAD 负向安全补验

- **CAD 补验**：执行 `RCAD-20-NEGATIVE-CAD`。沙箱内首次运行 `--real-cad` 为 `external_blocker`（看不到用户 AutoCAD COM）；按审批沙箱外重跑后通过。
- **证据路径**：`output/validation_runs/rcad-20-negative-cad-20260527-escalated/negative_cad_runner_report.json`。
- **结论**：`status=pass`、`evidence_state=negative_guard_verified`、`created_handles=[]`、`saved_dwg=false`、`deleted_entities=false`、`modified_formal_layers=false`、`preview_layer_entity_delta=0`、`modelspace_entity_delta=0`。
- **覆盖率**：复算 `cad_capability_coverage_after_rcad20.json` 与 `cad_capability_coverage_after_doc_sync.json` 后仍为 **128/257（49.81%）**；`negative_guard_verified` 是 guard-only，不计入几何证明。
- **校验**：focused 34 tests OK、全量 673 tests OK、repo audit 0 findings、`self_check.py` pass、`render_preview.py --check` ready、`git diff --check` 无空白错误。

### LCAD-11.1：evidence trend 词表契约

- **一键推进**：完成 `LCAD-11.1-EVIDENCE-VOCAB`，新增 `core/verification/evidence_trend.py`、`core/schemas/evidence_trend.schema.json`、`examples/evidence_trends/minimal_evidence_trend.json` 与 `tests/core/test_evidence_trend.py`。
- **趋势字段**：固定 `snapshots[]`、`source_kind`、完整 `evidence_state_counts`、`geometry_accuracy_counts`、`screenshot_role_counts`、`summary` 与 `metrics` 字段，供后续 `LCAD-11.2` / `11.3` / `11.4` 复用。
- **词表边界**：schema 的 evidence enum 与 `EVIDENCE_STATE_VALUES` 对齐；`negative_guard_verified` 在趋势汇总中只计入 `guard_only_count`，不计入 `cad_proof_state_count` 或 `geometry_verified_count`。
- **测试**：RED 阶段缺少 `core.verification.evidence_trend`；补实现后 focused 31 tests OK，隔离 tempfile ACL 后全量 673 tests OK，repo audit 0 findings，`git diff --check` 无空白错误。
- **口径同步**：一键推进进度更新为 **15/49（约 31%）**；next=`LCAD-11.2`。

### LCAD-10.5：负向安全父包收口

- **一键推进**：完成 `LCAD-10.5-PARENT-ROLLUP`，新增 `docs/verification/negative_cad_safety_acceptance.md`。
- **父包结论**：`LCAD-10-NEGATIVE-SAFETY` 收口，汇总 `LCAD-10.1~10.4` 的负向 fixture、write guard、负向 runner 和边界文档；明确 `negative_guard_verified` 仍为 guard-only，不新增真实 CAD 几何结论。
- **测试**：新增 `tests/core/test_lcad_10_parent_rollup.py`，覆盖 acceptance 文档与 handoff 索引；focused 6 tests OK，隔离 tempfile ACL 后全量 670 tests OK，repo audit 0 findings。
- **口径同步**：一键推进进度更新为 **14/49（约 29%）**；next=`LCAD-11.1`。

### LCAD-10.4：负向 CAD 安全边界文档

- **一键推进**：完成 `LCAD-10.4-NEGATIVE-BOUNDARY-DOC`，新增 `docs/verification/negative_cad_safety_boundaries.md`。
- **边界内容**：明确 LCAD-10.1~10.4 的职责、8 类 `failure_category`、write guard 安全扫描字段、`RCAD-20` 真实 CAD 补验门槛，以及 `negative_guard_verified` 不计入 `geometry_verified` / CAD 几何覆盖率。
- **测试**：新增 `tests/core/test_negative_cad_safety_boundaries_doc.py`，防止边界文档缺少关键声明；focused 4 tests OK，隔离 tempfile ACL 后全量 668 tests OK，repo audit 0 findings。
- **口径同步**：一键推进进度更新为 **13/49（约 27%）**；next=`LCAD-10.5`。

### NEG-CAD-PROOF-SYNC：负向安全 runner + 覆盖率可读证据 + composition 收口

- **LCAD-10.3**：新增 `core/verification/negative_cad_runner.py` 与 `scripts/run_negative_cad_runner.py`，汇总 negative CAD_PLAN 8/8、write guard、ActiveDocument snapshot、no-handle/no-save/no-delete/no-formal-layer 证据。
- **真实 COM 写入前置守卫**：`AutoCADComDriver` 的 line / rectangle / circle / arc / polyline / text / dimension 在任何 COM `Add*` 前先检查 preview layer，修复负向正式图层写入“抛错前可能已创建实体”的风险。
- **覆盖率可读报告**：新增 `core/verification/capability_readability.py` 与 `scripts/run_capability_readability_report.py`，输出 geometry verified / guard-only / deferred / smoke / none / blockers 分组。证据：`output/validation_runs/neg-cad-proof-sync/capability-readability-final/capability_readability_report.json`。
- **证据**：`output/validation_runs/neg-cad-proof-sync/negative-runner-fake-final/negative_cad_runner_report.json` 为 `status=pass`、`evidence_state=negative_guard_verified`、`created_handles=[]`；`negative-runner-real` 当前为 `external_blocker`（沙箱身份看不到用户 AutoCAD COM），不新增真实 CAD 几何结论。
- **composition 收口**：保留 JSON catalog + schema 工业化方向；`drawing_policy.py` 改为全局默认无标注，运行时对象级 `include_label/include_dimensions` 不再能覆盖 composition 输出。
- **自检补强**：`shell_confirmation.py` 对临时 JSON 清理的 `PermissionError` 做兜底，避免沙箱/ACL 清理失败掩盖已成功的 SHELL_MODEL 构建。
- **口径同步**：CAD 证明覆盖率统一为 **128/257（49.81%）**；代码轨完成度更新为 **12/49（约 24%）**，next=`LCAD-10.4`。
- **验证**：focused 35 tests OK；隔离 `tempfile` ACL 后全量 667 tests OK；repo audit 0 findings；`self_check.py` pass；`render_preview.py --check` ready（当前 AutoCAD window unavailable）。

### CAD 能力覆盖表提升（fitout composition + benchmark 镜像）

- **Fitout composition CAD**：`fitout_composition_cad_registry_manifest.json`；3/3 `geometry_verified`（`capability-lab-coverage-wave-20260527/fitout_composition_cad/`）。
- **登记表镜像**：`build_coverage_expansion_writeback.py` 将 interior/office/fitout benchmark 行与 `block.library.controlled_test_block_001` 绑定既有 CAD 证据；office `object_spec` benchmark 行镜像 `object.*.draw_object` 报告。
- **覆盖率**：**128/257（49.81%）**（自 108/42.0% 起 +20 行 verified）。
- **composition_cad_registry**：`benchmark_output_subdir` 可配置，支持多 benchmark suite。

### CAD 校验波次：glyph 矩阵 + office composition + LCAD-10.2

- **V-PROOF-32**：`symbol_glyph_cad_matrix_manifest.json` + `symbol_glyph_cad_matrix.py` + `run_symbol_glyph_cad_matrix.py`；真实 CAD **6/6** `geometry_verified`（`capability-lab-cad-validation-20260527/symbol_glyph_matrix/`）。
- **V-PROOF-42 片段**：`office_composition_cad_registry_manifest.json`；`composition_cad_check` 支持 manifest `case_ids`；office 4 case CAD **4/4** verified（`smoke`→`verified`）。
- **LCAD-10.2**：`write_guard_cad_runner.py` + `run_write_guard_cad_runner.py`（负向 plan 8/8 + fake write-guard pass）。
- **覆盖率**：**108/257（42.02%）**；证据 `capability-lab-cad-validation-20260527/`。
- **测试**：658 OK。

### 安全层校验收口（驱动守卫 + 路径边界）

- **驱动层一致防御**：新增 `core/cad_io/preview_write_guard_mixin.py`；`AutoCADComDriver` 与 `FakeCadDriver` 共用 `CadWriteGuard`，在 `ensure_layer` / `_apply_common` 阻断正式层写入，并统一阻断 `save_document` / `delete_entity_by_handle`。
- **路径边界**：`intent_lab_cad` 的 `plan_path` 与 `output_dir` 分别走 `resolve_under_project_root` / `resolve_under_project_output`；`run_intent_lab_cad.py`、`run_block_alpha_validation.py` CLI 入口同步加固。
- **测试**：新增 `tests/core/test_path_safety.py`、`tests/core/test_autocad_write_guard.py`；全量 **654 OK**。

### V-PROOF-22 / V-PROOF-31 / V-PROOF-43 能力证明轨

- **V-PROOF-22**：`demand_case_cad_manifest.json` + `demand_case_cad_smoke.py` + `run_demand_case_cad_smoke.py`；10/10 demand case 真实 CAD → registry `benchmark.demand_side_agent_benchmark.*` verified。
- **V-PROOF-31**：`surface_monitor_plan.json` / `surface_rug_plan.json`；`symbol_spec.schema` 增 `monitor`/`rug`；glyph CAD + `object.*.glyph` 与 `symbol.spec.*` 回写。
- **V-PROOF-43 片段**：`composition_cad_registry_manifest` + `composition_cad_registry.py`；`composition_cad_check` 迁入 `core/`；3 个 interior delivery composition 行 verified。
- **覆盖率**：batch **17** 行 → **`verified_count=104`（40.47% / 257）**；证据 `capability-lab-vproof-20260527/`。
- **测试**：649 OK。

### CAD 证明覆盖率 wave（object + domain + glyph + block）

- **V-PROOF-31 片段**：`examples/symbol_specs/seating_sofa_plan.json` + sofa glyph CAD smoke。
- **Object Lab 扩样**：`object_cad_smoke_manifest` 增至 **14** 类（+file_cabinet/storage_cabinet/computer_desk/display_unit/monitor/rug）；`capability-lab-coverage-wave-20260527/object_cad_smoke/` 14/14 `geometry_verified`。
- **Domain draw_object**：`domain_draw_object_cad_smoke.py` + `run_domain_draw_object_cad_smoke.py`；11 个 deferred domain 行真实 CAD。
- **回写**：`build_coverage_writeback_batch.py` batch **35** 行 → **`verified_count=87`（34.12% / 255）**；含 glyph 别名×5、block.insert_block_alpha×4、`symbol.spec.symbol_sofa_plan`。
- **测试**：647 OK。

### 登记表完善：fitout catalog 全量 CAD + batch 回写

- **Fitout catalog CAD**：`core/verification/fitout_catalog_cad_smoke.py` + `scripts/run_fitout_catalog_cad_smoke.py`；14/14 `geometry_verified`（`capability-lab-registry-20260527/fitout_catalog_cad/`）。
- **回写工具**：`scripts/build_registry_writeback_batch.py`（从 fitout smoke 报告 + glyph/regression 路径生成 batch）。
- **登记表**：batch **22** 行 `--apply`（11 catalog 自 deferred→verified；6 glyph；2 regression 路径刷新；3 catalog 已 verified 刷新证据）→ **`verified_count=59`（23.23% / 254）**。
- **CAD 校验波次**：`cad-validation-wave-20260527/` baseline geometry gate + composition retry 证据已链入 registry。
- **测试**：645 OK（`test_local_cad_regression` strict fake 补 `--no-cad` primitive 分支）。

### V-PROOF-14/15/20/21/30 能力证明轨

- **V-PROOF-14/15**：`core/verification/intent_lab_cad.py` + `scripts/run_intent_lab_cad.py`；`intent.draw_object` / `intent.draw_symbol_glyph` / `intent.insert_block_alpha` 真实 CAD + 登记表 verified。
- **V-PROOF-20**：`commercial_fitout_catalog_manifest.json`（14 项）+ `run_commercial_fitout_catalog_inventory.py`。
- **V-PROOF-21**：`object_cad_smoke_manifest.json` + 8 类 `examples/plans/object_smoke/` + `run_object_cad_smoke.py`；`object.*.draw_object` 八类 verified。
- **V-PROOF-30**：6 个 `symbol.archetype.*` 行绑定既有 glyph CAD 证据并 verified。
- **覆盖率**：batch 回写 +17 → **`verified_count=42`（16.54% / 254）**；证据 `capability-lab-vproof-20260527/`。
- **测试**：643 OK。

### CAD 证明覆盖率 sprint（symbol 全量 + fitout 样本）

- **Symbol Lab 补验**：`workstation` / `shelf` / `bed` / `cabinet` 四套 glyph smoke（`capability-lab-coverage-20260527/symbol-*`），均 `geometry_verified`；`run_symbol_glyph_cad_smoke.py` 增 `--base-x` / `--base-y` 避免叠图。
- **Commercial fitout**：`run_commercial_fitout_cad_smoke.py` → 3 plan batch、12 handles、`geometry_verified`；回写 `domain.commercial_fitout.draw_object` + `catalog.commercial_fitout.{desk,office_chair,file_cabinet}`。
- **登记表**：batch 回写 **+8** → **`verified_count=25`（9.84% / 254）**；symbol 类 **7/27** verified。
- **测试**：638 OK。

### V-PROOF-12/13 + RCAD-14/26 round2（能力证明 + CAD 补验）

- **V-PROOF-12**：`examples/capability_proof/primitive_matrix_cad_manifest.json`；`core/verification/primitive_matrix_cad_manifest.py`；`scripts/run_primitive_matrix_inventory.py`；`local_cad_regression_manifest` 增 `primitive_matrix_cad`；`primitive_matrix` 报告补 `evidence_state` 三字段（真实 CAD 时 `status=geometry_verified`）。
- **V-PROOF-13**：`cad_plan_fixture_manifest` 扩至 **6** fixture（glyph/storage/bench 等）；`cad_plan_fixture_suite` suite 级 `geometry_verified` + per-fixture `evidence_state`。
- **RCAD-14**：`examples/symbol_specs/surface_table_plan.json` + `symbol.spec.surface_table_plan` 登记行；`output/validation_runs/capability-lab-round2-20260527/rcad-14-table/` geometry verified（9 handles）。
- **CAD 证据**：`capability-lab-round2-20260527/` — primitive matrix（11 handles）、fixture suite 6/6 pass；回写 **+3** regression/symbol 行 + primitive probe 时间戳刷新 → **`verified_count=17`（6.69% / 254）**。
- **测试**：638 OK。

### §5 CAD 补验 + 登记表回写 sprint

- **E0**：`self_check.py`、`render_preview.py --check` pass（AutoCAD 2026 会话可用）。
- **严格本地矩阵**：`output/validation_runs/capability-lab-sprint-20260527/`（`run_local_cad_regression.py --strict`），7 case、`geometry_verified_case_count` 见 `local_cad_regression_report.json`。
- **补验**：`capability-lab-sprint-20260527-extra/` — primitive matrix CAD、`symbol_glyph` desk/chair、`commercial_fitout_cad_smoke`。
- **回写**：manifest suggest **4** 行 + primitive/symbol batch **10** 行 → 登记表 **`verified_count=14`**（**5.56%** / 252）；`run_capability_coverage.py` 已复跑。
- **未回写**：`regression.cad_plan_fixture_suite_cad`（suite 顶层 `pass` 非 `geometry_verified`）；`primitive.hatch`（probe 未覆盖）；fitout catalog 行尚无独立 RCAD registry 行。

### Composition 模板：JSON catalog + 全局无标注策略

- 组合模板自 `HEAD` 行为中性导出为 `libraries/composition_templates/catalog.json`，由 `composition_template_catalog.schema.json` 与 `catalog_loader.py` 加载；删除未跟踪的 `composition_templates_catalog_{core,fitout}.py`，修复拆分引入的床 `include_label: true` 漂移。
- 新增 `drawing_policy.py`：组合预览默认 `include_label=false` / `include_dimensions=false`；catalog 禁止启用标注。本轮后续已收紧为全局无标注，运行时 `composition_spec` 上的对象级标注开关也会被忽略。
- `templates.py` 保留运行时 API 并 re-export `COMPOSITION_TEMPLATES`；新增 `tests/core/test_composition_catalog.py`。

### Repo audit：大文件拆分（0 findings）

- `core/composition_engine/templates.py`（702 行）拆为 JSON catalog + `composition_template_catalog.py` loader；`templates.py` 仅保留运行时 API（~140 行）。
- `core/verification/local_cad_regression.py`（565 行）拆为 `local_cad_regression_{runtime,matrix}.py`；门面模块保留 CLI 与 re-export。
- 顺带拆分超标文件：`cad_validation_runner_report.py`、`capability_registry_seed_{common,extended}.py`。
- 证据：`scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings` → `finding_count=0`；**637 tests OK**。

### 并行：V1 Intent Lab + LCAD-10.1 + CAD-VAL-01 + RCAD-01 复验

- **V-PROOF-10 / V-PROOF-11**：`examples/capability_proof/intent_lab_manifest.json` 覆盖 6 个 `ALLOWED_INTENTS`；`examples/plans/intent_lab/*.json` 最小 plan；`core/verification/intent_lab.py` + `scripts/run_intent_lab_inventory.py`。
- **LCAD-10.1**：`examples/plans/negative/`（8 负向 plan + manifest）；`core/verification/negative_cad_plans.py` + `scripts/run_negative_cad_plan_suite.py`；`cad_plan.schema.json` 增 `draw_symbol_glyph` 与 absolute `base_point` 约束。
- **CAD-VAL-01**：`core/verification/cad_validation_geometry_gate.py`；`run_cad_validation.py` 支持 `--geometry-gate` / `--require-geometry-pass`（几何 vs 基础设施分层）。
- **RCAD-01**：真实 CAD 复验 `output/validation_runs/rcad-01-baseline-geometry/`（`inspect_readback` + `cad_capability_probe` + `block_alpha_readback` 几何证据）；`regression.baseline_cad_validation` 回写 `verified`；覆盖率 **0.4%**（1/252）。
- 证据：**637 tests OK**；`run_intent_lab_inventory.py` / `run_negative_cad_plan_suite.py` exit 0。

### V-PROOF-04/05：三口径状态页 + 能力证明 handoff 扩展

- **V-PROOF-04**：`CORE_STATUS.md` 固定「三进度口径」节（表 A / 表 B / CAD 证明覆盖率 / Ladder）；新增 `docs/verification/capability_proof_status_template.md`；`CAD_AGENT_STATUS.md` 同步并明确 **Core 94% ≠ CAD 证明覆盖率**。
- **V-PROOF-05**：`CURSOR_PACKAGE_HANDOFFS.md` 增加能力证明包附加项 10~12；`evidence_gate_handoff_rules.md` §7、`capability_proof_handoff_template.md`、`docs/handoffs/README.md` 维护规则更新。
- 证据：`tests/core/test_planmd_governance.py` 新增 3 项；全量 unittest 通过。无代码行为变更。

### V-PROOF-03：CAD 能力登记表 loader + RCAD 回写 API

- 扩展 `core/verification/capability_registry.py`：`RegistryBundle`、`load_registry_bundle`、`save_capability_registry`（写前校验）。
- 新增 `core/verification/capability_registry_writeback.py`：`apply_writeback` / `apply_writebacks`、`extract_geometry_evidence_from_report`、`suggest_writebacks_from_regression_output`、`run_registry_writeback`。
- 新增 `scripts/run_capability_registry_writeback.py`：`--capability-id`+`--report`、`--batch`、`--suggest-from-regression`、`--apply`。
- 证据：`tests/core/test_capability_registry_writeback.py` 6 tests OK；全量 unittest 通过。默认不修改种子登记表；回写需显式 `--apply`。

### V-PROOF-02：CAD 能力证明覆盖率报告

- 新增 `core/verification/capability_registry.py`（load + validate）、`core/verification/capability_coverage.py`、`scripts/run_capability_coverage.py`。
- 默认输出 `output/validation_runs/capability-lab/cad_capability_coverage.json`：`total_count=252`、`verified_count=0`、`cad_proof_coverage_rate=0.0`；含 `by_category`、`category_cad_proof`、`trend`（LCAD-11.4 趋势槽位）。
- 证据：`tests/core/test_capability_coverage.py` 4 tests OK；全量 `623 tests OK`。本轮未运行真实 CAD。

### V-PROOF-01：CAD 能力登记表种子（252 行）

- 新增 `core/verification/capability_registry_seed.py` 与 `scripts/build_cad_capability_registry_seed.py`，从 intent、primitive、object catalog、fitout catalog、composition、symbol、Core API、scene、benchmark suite、local CAD regression manifest、block library 等自动生成登记行。
- 产物：`examples/capability_proof/cad_capability_registry.json`（**252** capabilities；`claim_level` 分布为 none / deferred / smoke，**0** 行 `verified`/`showcase`）。
- 证据：`tests/core/test_cad_capability_registry_seed.py` 4 tests OK；全量 unittest 与种子脚本校验通过。本轮未运行真实 CAD。

### V-PROOF-00：CAD 能力登记表 Schema

- 新增 `core/schemas/cad_capability_registry.schema.json`：能力行 `capability_id` / `category` / `claim_level` / `ladder_level`、`cad_case`、`evidence` 三字段、`source_refs` 与 CODEX_PREVIEW `safety` 契约。
- 登记进 `MODEL_SCHEMAS`；`infer_model_type()` 可识别 `cad_capability_registry`。
- 新增 `core/verification/capability_registry_contract.py`：`claim_level` 级合同校验（subset schema 不支持的 verified/deferred 规则）。
- 样例与负例：`examples/capability_proof/minimal_cad_capability_registry.json`、`tests/fixtures/invalid_models/cad_capability_registry.invalid.json`。
- 证据：`tests/core/test_cad_capability_registry_schema.py` 6 tests OK；全量 `615 tests OK`。本轮未运行真实 CAD。

### P0：schema registry + FakeDriver + 关键 pytest 全绿

- `core/schemas/registry.py` 补齐 commercial fitout / project sample / orchestrator 等模型登记与 invalid fixtures；`schemas/cad_plan.schema.json` 与 `core/schemas/cad_plan.schema.json` 同步（含 `commercial_fitout` domain）。
- `core/plan_engine/validate_plan.py` 的 `ALLOWED_DOMAINS` 增加 `commercial_fitout`。
- `core/verification/fake_cad_driver.py` 加固：`CadWriteGuard`、`insert_block_alpha`、受控块定义、`open_document_count`。
- `core/composition_engine/templates.py` 增加 fitout 组合模板；`core/benchmarks/runner.py` 使用 `evaluate_fitout_composition_layout_failure`，并补齐 `object_spec` / demand / object_detail 路径。
- 证据：全量 `609 tests OK`（`python -m unittest discover -s tests`）。`run_repo_audit.py` 仍有 2 个 `large_python_file`（`templates.py` 702 行、`local_cad_regression.py` 565 行），未纳入 P0 退出标准。

### 交付汇报：固定表 A + 表 B（六个指标）

- `AGENTS.md`「交付必须带进度估算」改为 canonical 双表模板：表 A（总进度 / Core / Agent）、表 B（能力证明 §3 / 一键推进 §4 / CAD 补验 §5），并写明与 `docs/planning/任务清单.md` §0 的关系及禁止混用口径。
- 同步 `README.md`、`CORE_CONTEXT_BRIEF.md`、`CAD_AGENT_RULES.md` §0.4；工作区 `AGENTS.md` 增加双表交付要求。

## 2026-05-26

### Codex 本地 CAD 回归矩阵加固

- 新增 `core/verification/local_cad_regression.py` 与 `scripts/run_local_cad_regression.py`，把 baseline CAD validation、project sample CAD check、interior composition CAD check 汇总成一个本地 CAD 回归矩阵。
- `--no-cad` 模式输出 deferred / non-CAD 证据，不连接 AutoCAD、不声称 `geometry_verified`；真实 CAD 严格模式可用 `--require-cad-verified`，任一 CAD 子项不是 `geometry_verified` 时顶层失败。
- composition CAD check 增加前置 artifact 门禁：只有 `interior_delivery_benchmark` 成功后才运行真实 CAD 批量检查，前置失败时记录 `not_run` / `blocked_by`。
- 新增回归测试覆盖 no-CAD deferred 矩阵、严格模式拒绝 deferred、前置 benchmark 失败跳过 composition，以及 output dir 边界。
- 证据：focused `tests.core.test_local_cad_regression` 4 tests OK；`scripts/run_local_cad_regression.py --no-cad --output-dir output\validation_runs\local-cad-regression-no-cad` pass，`geometry_verified_case_count=0`；全量 `456 tests OK`。本轮未运行真实 AutoCAD，不新增 `geometry_verified` 结论。

### Codex 进入下一阶段前雕琢：可迁移命令、CLI 兼容和全量复验

- `CAD_AGENT_BLOCKER_PLAYBOOK.md` 的当前工具入口不再写死固定 Windows 用户目录下的 CAD-MCP Python 路径，改为 `$env:USERPROFILE` 派生 `$py`，保持换机 / 换用户可运行。
- 新增文档治理回归：活跃 CAD 文档不得重新引入固定 Windows 用户目录下的 CAD-MCP 路径。
- `run_office_scene_beta_benchmark.py`、`run_residential_scene_beta_benchmark.py`、`run_restaurant_scene_beta_benchmark.py` 新增 `--output-root` 兼容别名，同时保留原 `--output`。
- 新增 CLI 回归测试：三组 scene beta wrapper 均可用 `--output-root` 输出 benchmark artifact。
- 证据：全量 `452 tests OK`；repo audit 0 findings；`run_cad_validation.py --no-cad --output-dir output\validation_runs\codex-polish-final-no-cad` pass；blank-shell 8/8、office alpha 18/18、interior delivery 3/3、project sample 2/2、proposal confirmed 2/2、CAD beta rollup 5/5、scene beta 25/25 pass。本轮未运行真实 CAD，不新增 `geometry_verified` 结论。

### Codex 维护 4-7 包：结构整理、路径公共化、Schema registry、文档主从治理

- 新增 `core/path_safety.py`：统一 `find_project_root`、`resolve_under_project_output`、`resolve_under_project_root`、`validate_safe_path_segment` 和 `is_relative_to`，替换 benchmark、drawing-read、CAD validation、blank-shell、capability runner、proposal / beta suite 中分散的路径判断。
- 加固真实 CAD 与 artifact 入口：project sample CAD check、composition CAD check 在连接 AutoCAD 或写报告前先验证 workflow / benchmark / output 路径留在仓库 `output/`；non-CAD pipeline 对越界 workflow、越界 output、缺输入文件返回结构化 invalid，不再抛散乱异常。
- `core/schemas/registry.py` 现在登记所有 `core/schemas/*.schema.json`，并补齐对应 invalid fixtures，避免 schema 文件新增后未被 validator 覆盖。
- 文档治理收口：`docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` 不再承载“下一包建议 / 剩余开发包表”；`CAD_AGENT_STATUS.md` 和 `CORE_RESTRUCTURE_PLAN.md` 更新为 Phase X/Y/R 已收口但不扩大能力声称的口径。
- 证据：focused 4-7 包测试 `46 tests OK`；全量 `450 tests OK`；repo audit 0 findings；`run_cad_validation.py --no-cad --output-dir output\validation_runs\codex-maintenance-4-7-no-cad` pass。本轮未运行真实 CAD，不新增 `geometry_verified` 结论。

### Codex 维护 1-3 包：证据止血、基线同步、路径安全

- `run_project_sample_cad_check.py` 新增 `--require-cad-verified`：报告不是 `geometry_verified` 时返回非 0；`--no-cad` 仍保存 `deferred_cad_readback_required` 报告，但不能被 CI / 交接误当成真实 CAD 通过。
- `projects/` 样本 manifest 输入路径现在必须解析在样本目录内；protocol scan 新增 `manifest_input_outside_sample`，loader 同步拒绝越界读取。
- benchmark / drawing-read benchmark 的 `case_id` 现在必须是安全 path segment；benchmark output root、drawing-read output root、CAD validation output dir 均限制在仓库 `output/` 下；CAD validation 清理 stale artifact 前会再次确认目标留在本轮 `output_dir` 内。
- 状态文档同步口径：`BETA-PROJECT-SAMPLE-05` 当前仓库存档 no-CAD 报告是 deferred，不是真实 AutoCAD `geometry_verified`；真实样本 CAD readback 仍需用户会话单独运行。
- 证据：focused 1-3 包测试 `48 tests OK`；全量 `432 tests OK`；repo audit 0 findings；`run_cad_validation.py --no-cad --output-dir output\validation_runs\codex-maintenance-fix-no-cad` pass；blank-shell benchmark 8/8 pass；office alpha benchmark 18/18 pass；interior delivery benchmark 3/3 pass；`run_project_sample_cad_check.py --no-cad --require-cad-verified` 按预期返回 1 并写出 deferred 报告。

### Codex 深度全量安全复盘与加固

- 修复 Cursor 大量改动后的 4 类回归/风险：项目样例协议测试误用系统 temp、benchmark case 缺失完整 evidence triplet、proposal confirmed benchmark 缺少 `evidence_summary`、项目样例 CAD check / drawing standard profile 使用非法证据词。
- benchmark runner 新增强制校验：所有 case expected 必须包含 `evidence_state`、`geometry_accuracy`、`screenshot_role`；suite `expected_evidence_summary` 与实际 rollup 不一致时失败。
- `core/project_samples/cad_check.py` 的 no-CAD / failure / fake CAD 路径统一使用 evidence contract 合法词；`libraries/drawing_standards/codex_preview_beta.json` 的 `screenshot_role` 修正为 `not_applicable`。
- 维护性拆分：新增 `core/benchmarks/expectations.py`、`core/verification/evidence_vocabulary.py`、`core/composition_engine/preview.py`、`core/workflows/blank_shell_candidates.py`、`tests/core/cad_validation_payloads.py`、`tests/core/test_benchmark_validation.py`，使 repo audit 大文件 findings 从 6 个降为 0。
- 静态与回归证据：`424 tests OK`；repo audit 0 findings；Python AST `248` files / 0 errors；JSON `166` files / 0 errors；坏证据词和系统 temp 回归未命中。
- 验收脚本证据：`self_check.py` pass；`render_preview.py --check` ready；project sample protocol scan pass；project sample benchmark 2/2 pass；proposal confirmed benchmark 2/2 pass；CAD beta rollup 5/5 pass；office/residential/restaurant scene beta benchmark 分别 9/9、8/8、8/8 pass。

### BETA-SCENE-03 restaurant / commercial scene beta benchmark

- `restaurant_scene_beta_benchmark.json`（8 cases：入口/堂食/后场/blank-shell/failure）。
- `restaurant/preferences.json` 增加 `scene_beta`；`restaurant_scene_beta.py`。
- 证据：`422 tests OK`（+2）。

### BETA-SCENE-02 residential scene beta benchmark

- `residential_scene_beta_benchmark.json`（8 cases：卧室/餐厅/收纳/blank-shell/failure）。
- `residential/preferences.json` 增加 `scene_beta`；`residential_scene_beta.py`。
- 证据：`420 tests OK`（+2）。

### BETA-SCENE-01 office scene beta benchmark

- `scene_beta.py` + `office_scene_beta_benchmark.json`（9 cases：object / micro_scene / blank_shell / failure）。
- `agents/office/preferences.json` 扩展 `scene_beta` 与 office 对象偏好；`run_office_scene_beta_benchmark.py`。
- 证据：`418 tests OK`（+2）。

### BETA-DRAWING-READ-05 / 父包 BETA-DRAWING-READ 收口

- `drawing_read_benchmark.json`（3 cases：全链路 pass、候选 pass、缺门洞 blocked + `structured_blockers`）。
- `drawing_read_benchmark.py` + `run_drawing_read_benchmark.py`；`beta_drawing_read_acceptance.md`。
- 证据：`416 tests OK`（+2）。

### BETA-DRAWING-READ-04 shell confirmation → SHELL_MODEL

- `shell_confirmation.py`：`shell_drawing_read_confirmation` schema、对照 report 校验、`apply` → `load_manual_shell`。
- 示例 `sample_shell_drawing_read_confirmation.json`；CLI `apply_shell_drawing_read_confirmation.py`。
- 证据：`414 tests OK`（+4）。

### BETA-DRAWING-READ-03 shell candidate confidence report

- `shell_candidate_report.py`：overall/boundary/openings 置信度、`gaps`、`human_confirmation_items`、`ready_for_human_confirmation_file`。
- `sample_geometry_walls_only_fixture.json` 负样本（缺门洞 blocker）；CLI `run_shell_candidate_report.py`。
- 证据：`410 tests OK`（+3）。

### BETA-DRAWING-READ-02 geometry feature candidates

- `geometry_candidates.py`：墙线段 / 门洞 / 柱 / 禁放区启发式候选；`dwg_geometry_candidates.schema.json`。
- Fixture `sample_geometry_feature_fixture.json`；CLI `run_geometry_candidates.py`。
- 证据：`407 tests OK`（+3）。

### BETA-DRAWING-READ-01 read-only DWG entity summary

- `dwg_read_only.py`：`build_dwg_entity_summary`、fixture / active CAD / driver 入口；`dwg_entity_summary.schema.json`。
- `FakeCadDriver.snapshot_modelspace()` 供只读汇总；CLI `run_dwg_entity_summary.py`。
- 证据：`404 tests OK`（+4，含 READ-02 前基线）。

### BETA-PROPOSAL-05 / BETA-PROPOSAL 父包收口

- `finalize_confirmed_cad_plans()` 输出受控 CAD_PLAN bundle + `unselected_candidate_evidence`；validate/dry-run 全通过。
- `proposal_confirmed_benchmark.json`（2 cases）；`beta_proposal_acceptance.md` rollup。
- 证据：`400 tests OK`（+5）。

### BETA-PROPOSAL-04 partial CAD_PLAN replan

- `partial_replan.py`：`recompute_cad_plans_from_pipeline_artifacts()` 跳过上行动线，仅更新 placements/layout/CAD_PLAN/验证产物。
- CLI `run_proposal_partial_replan.py`；`partial_replan_report.json` 记录 skipped/recomputed 模块。
- 证据：`395 tests OK`（+2）。

### BETA-PROPOSAL-03 user confirmation input schema

- `proposal_user_confirmation.schema.json` + `user_confirmation.py`（validate / build / apply / round-trip）。
- 示例 `examples/confirmations/`；CLI `apply_proposal_user_confirmation.py`。
- 证据：`393 tests OK`（+6）。

### BETA-PROPOSAL-02 proposal comparison summary benchmark

- `proposal_comparison_summary`（object_coverage / circulation / conflicts / failure_reasons）；pipeline 写出 `proposal_comparison_summary.json`。
- `proposal_comparison_benchmark.json` 4 cases；runner 新增 `requires_proposal_comparison_summary` 等断言键。
- 证据：`387 tests OK`（+3）。

### BETA-PROPOSAL-01 proposal candidate scoring fields

- 新增 `candidate_scoring.py`、`proposal_candidate_scoring.schema.json`；`DESIGN_PROPOSAL.candidates[]` 要求 `score_breakdown` + `ranking_reasons[{code,message}]`。
- `compare_layout_candidates` / `create_design_proposal` / blank-shell 分支接入；示例 proposal JSON 已更新。
- 证据：`384 tests OK`（+3）。

### BETA-PROJECT-SAMPLE-05 / BETA-PROJECT-SAMPLE 父包收口

- `core/project_samples/cad_check.py` + `run_project_sample_cad_check.py`：`sample_blank_shell` 多 CAD_PLAN 批量 CODEX_PREVIEW 执行与 created-handle readback；`--no-cad` → `deferred_cad_readback_required`。
- `beta_project_sample_acceptance.md` 记录 01–05 可声称 / 不可声称边界。
- 证据：`381 tests OK`（+4）；fake driver `geometry_verified`；真实 CAD 需在用户 AutoCAD 会话下单独运行 CLI。

### BETA-PROJECT-SAMPLE-04 project sample benchmark (pass + blocked)

- 新增 `projects/sample_blank_shell_too_small/`、`sample_blank_shell_too_small_loop.json`、`project_sample_benchmark.json`（2 cases）。
- `core/project_samples/benchmark.py` + `run_project_sample_benchmark.py`；`blocked_expected_non_cad` + `cad_plan_count=0` 硬断言。
- 证据：`377 tests OK`（+4）；`output/test_artifacts/benchmarks/beta_project_sample_04/benchmark_summary.json`。

### BETA-PROJECT-SAMPLE-03 sample workflow CAD_PLAN / dry-run / verification

- `sample_blank_shell_project_loop.json` + `run_sample_blank_shell_workflow()`；产出 CAD_PLAN、`dry_run valid`、`verification unverified`。
- CLI `run_project_sample_workflow.py`；`sample_workflow_report.json` 明确 `geometry_verified: false`。
- 证据：`373 tests OK`（+2）。

### BETA-PROJECT-SAMPLE-02 sample shell / project model fixtures

- `sample_blank_shell` 增加 `fixtures/`、`expected/project_model.expected.json`；`core/project_samples/loader.py`。
- manifest 驱动 `load_sample_inputs` / `build_sample_project_model`；金样回归测试。
- 证据：`371 tests OK`（+5）。

### BETA-PROJECT-SAMPLE-01 de-identified project sample protocol

- 扩展 `projects/README.md`；新增 `project_sample_manifest.schema.json`、`core/project_samples/protocol.py`。
- 基线样本 `sample_blank_shell/sample.manifest.json` + 样本 README；协议扫描拒绝提交 DWG。
- 证据：`366 tests OK`（+4）。

### BETA-CAD-BLOCK-05 / BETA-CAD-BLOCK 父包收口

- 新增 `cad_beta_evidence_rollup.py`、`beta_cad_block_acceptance.md`、rollup CLI；`fake_cad_driver.py` 供 probe 复用。
- rollup 汇总 01–04 non-CAD 子包 + 05 文档包；`geometry_verified_count=0`。
- 证据：`362 tests OK`；`output/test_artifacts/cad_beta_evidence/beta_cad_block_05/`。

### BETA-CAD-BLOCK-04 drawing_standard_profile

- 新增 `core/drawing_standard/`、`codex_preview_beta` profile / layer preset、schema 与 6-case beta suite。
- `preview_only` 下 CAD 执行层统一 `CODEX_PREVIEW`；语义层保留 `A-FURN` 等映射；`insert_block_alpha` dry-run 可带 `drawing_standard_profile_id`。
- 证据：`359 tests OK`（+9）。non-CAD only。

### BETA-CAD-BLOCK-03 entity-level capability probe evidence

- 新增 `entity_level_evidence.py`；`cad_capability_probe` 输出 `entity_evidence[]`（polyline 写读对比、layer_role→`CODEX_PREVIEW`、hatch `deferred`）。
- `ENTITY_CONTRACTS` 增加 `hatch`（deferred）；`inspect_dwg` 识别 Hatch；`validate_capability_probe_evidence` 在 verified 时要求 entity_evidence。
- 证据：`350 tests OK`（+6）。hatch 非真实 CAD 验证。

### BETA-CAD-BLOCK-02 block attribute / tag readback probe

- 新增 `block_attribute_probe.py`；`inspect_dwg` 归一化 `GetAttributes()`；`build_block_alpha_readback_report` 合并 attribute 判定。
- `attribute_readback_probe` 计划可声明期望 tag；缺 tag → `attribute_unverified` deferred，不误报 `geometry_verified`。
- 证据：`344 tests OK`。

### BETA-CAD-BLOCK-01 controlled block transform beta suite

- 新增 `block_alpha_beta_suite.json`（8 cases）、`block_alpha_beta_suite.py`、`run_block_alpha_beta_suite.py`。
- 多 `base_point`、rotation（45°/90°）、uniform scale（0.5/1.25/0.75）validate + dry-run。
- 证据：`336 tests OK`；`output/test_artifacts/block_alpha_beta/beta_cad_block_01/`。non-CAD only。

### X-SCENE-05 / X-SCENE-ALPHA 父包收口

- 新增 `docs/verification/scene_alpha_acceptance.md`、`tests/agents/test_scene_alpha_acceptance.py`。
- 总验收：scene alpha benchmark 3/3、`agents/` 边界扫描 0 violations、验证文档 bundle 齐全。
- **可声称**：office / residential / restaurant 复用同一 `blank_shell` Core pipeline（non-CAD）。
- **不可声称**：`geometry_verified`、Scene Agent 产品完成、真实项目/块库全量准确。
- 证据：`332 tests OK`；`output/test_artifacts/benchmarks/x_scene_05/`。

### X-SCENE-04 Scene Alpha explanation template

- 新增 `core/agents/scene_explanation.py`、`docs/verification/scene_alpha_explanation_template.md`、`tests/agents/test_scene_explanation.py`。
- 三场景 `rules.md` 增加 Preference→Core 映射与不可声称；`first-handoff.md` Scene Alpha 接手段。
- `scene_boundary_scan`：`rules.md` 仅做 import 扫描，允许文档引用 Core 入口名。
- 证据：`326 tests OK`；`output/test_artifacts/benchmarks/x_scene_04/` 3/3 pass。

### X-SCENE-03 Scene Agent boundary scan

- 新增 `core/agents/scene_boundary_scan.py`；扩展 `tests/agents/test_scene_agent_boundaries.py`（`test_x_scene_03_*`）。
- 更新 `agents/SCENE_AGENT_RULES.md`、`docs/verification/scene_alpha_agent_boundaries.md`；Alpha 场景 `rules.md` 补强 Core 边界表述。
- 证据：`322 tests OK`；`agents/` 树扫描 0 violations。

### X-SCENE-02 Scene Alpha multi-scene benchmark

- 新增 `examples/benchmarks/scene_alpha_benchmark.json`（office / residential / restaurant 三 case，均 `pipeline: blank_shell`）。
- `blank_shell_pipeline`：`scene_preferences` 驱动 `_select_circulation_for_zones`；metrics 导出 `preferences_scenario` / `selected_circulation_strategy`。
- `runner._actual_from_pipeline` + `preferences_path_contains` 断言；`zone_splitter` 用全部 `path_surface` 并集 bbox 切区（修复 along_wall 单区与走道重叠）。
- 证据：`317 tests OK`；`output/test_artifacts/benchmarks/x_scene_02/` 3/3 pass。

### X-SCENE-01 Scene Alpha preferences contract

- 锁定 `office` / `residential` / `restaurant`；`circulation_strategy_weights` + `agents/scene_alpha_manifest.json`。
- 新增 `core/agents/scene_alpha.py`；`tests/agents/test_scene_preferences.py` 扩展 X-SCENE-01 断言。
- 证据：`315 tests OK`。

### Y-MC-05 multi-candidate boundaries（Y-MULTI-CANDIDATE 收口）

- 新增 `docs/verification/blank_shell_multi_candidate_boundaries.md`；更新 `phase-y-blank-shell-hardening-plan.md`、`shell-layout-foundation-design.md`。
- 父包 `Y-MULTI-CANDIDATE` **5/5** 完成；下一主线 `X-SCENE-ALPHA`。
- 证据：`312 tests OK`；`output/test_artifacts/benchmarks/y_mc_05/` 8/8 pass。

### Y-MC-04 blank-shell near-real and failure shell cases

- `blank_shell_core_benchmark.json` 扩至 8 cases：`long_narrow`、`obstacle`、 `too_small`、`corridor_riser_blocks_main_path`。
- 新增 `blank_shell_corridor_riser_block_shell.json` + workflow；blocked 路径 metrics 含 `fixed_obstacle_count`。
- 证据：`312 tests OK`；`output/test_artifacts/benchmarks/y_mc_04/` 8/8 pass。

### Y-MC-03 benchmark multi-candidate assertions

- `runner._actual_from_pipeline` 输出 `zone_placement_candidate_count`、`object_coverage_rate`、`selected_failed_reason_distribution` 等。
- `blank_shell_core_benchmark.json` 四 case 增加 `requires_comparison_detail` 与多候选 `minimums` / `maximums`。
- 证据：`311 tests OK`；`output/test_artifacts/benchmarks/y_mc_03/` 4/4 pass。

### Y-MC-02 proposal comparison_detail

- `build_blank_shell_comparison_detail()`：对象覆盖率、失败检查数/分布、通道连续性、circulation 分支排序原因。
- `create_design_proposal()` 接入 `candidate_sets`；`comparison_summary` 为 narrative；未选中分支失败不触发 `needs_confirmation`。
- 证据：`310 tests OK`；blank-shell benchmark `y_mc_02` 4/4 pass。

### Y-MC-01 blank-shell candidate_sets artifact

- `build_blank_shell_candidate_sets()`：按 circulation 分支保留 zone/placement 候选明细，写入 `candidate_sets.json`。
- pipeline metrics 增加 `zone_placement_candidates`、`selected_circulation_strategy`、`selected_zone_id`。
- 证据：`309 tests OK`；blank-shell benchmark `output/test_artifacts/benchmarks/y_mc_01/` 4/4 pass。

### R4-05 evidence gate handoff rules（R4-EVIDENCE-GATES 收口）

- 新增 `docs/verification/evidence_gate_handoff_rules.md`：每包第 8 项三列表格、Codex 校验清单、禁止声称。
- 扩展 `docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` 标准模板与 Codex 指引；§18 R4-04、§19 R4-05。
- 父包 `R4-EVIDENCE-GATES` **5/5** 完成；下一主线 `Y-MULTI-CANDIDATE`。

### R4-04 CAD validation evidence alignment

- 新增 `core/verification/cad_validation_evidence.py`：`build_cad_validation_evidence_summary`、`cad_validation_evidence_gate_failure`。
- `cad_validation_runner` 写入 `report.json.evidence_summary`；no-CAD pass 要求 `non_cad_only`；含 CAD pass 要求 readback/capability 证据态。
- 步骤 stdout 未知 `evidence_state` 会使步骤 fail。
- 证据：`308 tests OK`；`output/validation_runs/r4-no-cad/report.json`。

### R4-03 benchmark suite evidence summary

- `summarize_benchmark_evidence` 输出 rollup 计数与 `screenshot_role_counts`；`validate_evidence_summary` 校验一致性。
- 三组 benchmark JSON 增加 `expected_evidence_summary`；suite 跑完后写入 `benchmark_summary.json` 并比对。
- 新增 `test_r4_three_benchmark_suites_match_expected_evidence_summary`。
- 证据：`304 tests OK`；`output/test_artifacts/benchmarks/r4_blank_shell/`、`r4_interior/`、`r4_office/`。

### R4-02 blocked / invalid failure benchmark assertions

- `validate_failure_expected_contract()`：failure case 必须 `failure_category` 或 `contains_blocked_reason`；`blocked`/`invalid` 与 `evidence_state` 配对。
- runner 支持 `maximums` 断言与 `_compare_failure_outcome_guards()` 静默 pass 防护。
- office alpha +1：`office_invalid_workflow_input`（`invalid_configuration`）；`too_small` 增加 `maximums.cad_plan_count: 0`。
- 证据：`302 tests OK`；`output/test_artifacts/benchmarks/r4_office_r2/`。

### R4-01 evidence classifier / vocabulary

- 扩展 `core/verification/evidence_contract.py`：`EVIDENCE_BLOCKED_EXPECTED_NON_CAD`、`EVIDENCE_DRY_RUN_VALID_PLAN_ONLY`、`EVIDENCE_INVALID_CONFIGURATION`、`EVIDENCE_STATE_VALUES`、`classify_benchmark_pipeline_evidence()`、校验函数。
- `core/benchmarks/runner.py` 移除本地 `_derive_evidence_state`，expected/actual 证据字段统一走词表校验。
- `composition_engine/templates.py`、`block_alpha_plan.py` 改用契约常量；`verification_report.schema.json` 补全 enum。
- 新增 `docs/verification/evidence_state_vocabulary.md`、`tests/core/test_evidence_classifier.py`。
- 证据：`299 tests OK`。

### R-OFFICE-MICRO-05 office alpha 收口

- `run_benchmark_suite` 写入 `benchmark_summary.json`，新增 `summarize_benchmark_evidence()`（`evidence_state` / `failure_category` 计数）。
- 新增 `docs/verification/office_alpha_benchmark_evidence.md`：17 cases 证据汇总、Alpha 退出门槛、可声称/不可声称边界。
- 同步 `phase-r-office-benchmark-cases.md`、`CAD_AGENT_STATUS.md`、handoff §14；`R-OFFICE-MICRO` 父包 5/5 完成。
- 证据：`294 tests OK`；`output/test_artifacts/benchmarks/office_alpha_r_micro/`。

### R-OFFICE-MICRO-04 office failure benchmark

- 新增 `core/layout_engine/office_layout_failure.py`：composition 净空冲突检测与 blank-shell `layout_expectation` 硬阻断。
- `blank_shell_pipeline` 支持 `layout_expectation.mode=require_all_placed`，过小房间样本返回 `insufficient_space`。
- `composition_engine` 新增 `door_clearance_conflict`、`cabinet_pullback_conflict` 失败模板。
- benchmark runner 支持 `failure_category`、`contains_blocked_reason`，blocked pipeline 映射 `evidence_state=blocked_expected_non_cad`。
- `office_alpha_benchmark.json` 扩至 **17 cases**（+3 failure）。
- 证据：`293 tests OK`；`output/test_artifacts/benchmarks/office_failure_r4/` → 17/17 pass（non-CAD，含 3 blocked）。

### Codex 第二轮风险验收与证据门禁继续加固

- 针对第二轮多 agent 挑刺审查，修复 CAD validation runner 只验证报告内部自洽、未与上一阶段 `execution_summary.json` 交叉比对 created handles 的缺口；新增 `core/verification/cad_validation_gates.py`。
- 加固 `block_alpha_report.status=geometry_verified`：必须有 `created_handles_scope=pass`、唯一 created handle、`block_reference` 实体 payload，以及 `block_name` / `insertion_point` / `rotation` / `scale` / `layer` / `bbox` 几何字段。
- 加固 `AutoCADComDriver.insert_block_alpha()` 失败路径：attributes、非法 base point、非受控 identity 在 COM 写入前拒绝；插入后若 handle 缺失或后置校验失败，会尝试删除刚插入的 block reference；复用同名 `CODEX_TEST_BLOCK_001` 前会校验受控 definition 形状。
- 修正 `insert_block_alpha` plan / dry-run 与 driver 的 scale 契约：plan 层拒绝非统一 scale，dry-run bbox 应用统一 scale。
- 测试拆分以保持 repo audit 行数门禁：新增 `tests/core/test_autocad_block_alpha_hardening.py`、`tests/core/test_cad_validation_runner_handle_scope.py`。
- 最新证据：`290 tests OK`；repo audit 0 findings；office alpha benchmark 14/14 pass；`run_cad_validation.py --no-cad --block-alpha-only` pass with deferred evidence；standalone block alpha negative no-CAD exit 1。
- 真实 AutoCAD 复验通过：`output/validation_runs/codex-second-gate-block-alpha-cad-final/report.json`（block handle `99B`）与 `output/validation_runs/codex-second-gate-full-cad-final/report.json`（baseline handles `99C..9E6`，block handle `ABC`）。
- 负向 COM 探针通过：非法 `block_id`、非法 `block_name`、attributes、非法 `base_point` 均被拒绝，当前测试 DWG ModelSpace 实体数 `131 -> 131`。

### Codex 风险验收与证据门禁加固

- 针对多 agent 审查发现的风险，补强 `insert_block_alpha` 三层门禁：`CAD_PLAN` 校验、`execute_plan` 调用链和 `AutoCADComDriver` 现在只允许 `block_id=controlled-test-block-001` 与 `block_name=CODEX_TEST_BLOCK_001`。
- 加固 CAD 证据契约：`readback_report.status=geometry_verified` 必须带非空 `actual.created_handles`、实体回读 payload 和 `created_handles_scope=pass`；`block_alpha_report.status=geometry_verified` 必须带非空 `created_handles` 且 `entity.type=block_reference`。
- 修复 `run_cad_validation.py --no-cad --block-alpha-only` 漏掉 `block_alpha_deferred_evidence` 的问题；`scripts/run_block_alpha_validation.py` 在 readback failed 时现在返回非 0。
- 为上述风险新增回归测试，当前全量 `267 tests OK`；`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings。
- 结构拆分：新增 `core/cad_io/autocad_block_alpha.py`、`core/verification/cad_validation_types.py`、`core/verification/cad_validation_block_alpha.py`，将 `autocad_com.py` 和 `cad_validation_runner.py` 降到 repo audit 行数限制以内。
- 真实 AutoCAD 复验通过：`output/validation_runs/codex-review-block-alpha-cad-after-gate/report.json` 为 `status=pass`，block handle `879` 定向 readback 全 pass；`output/validation_runs/codex-review-full-cad-after-gate/report.json` 为 `status=pass`，baseline handles `87A..8C4` 与 block handle `99A` 均完成 created-handle readback。
- 负向 COM 探针通过：直接调用 driver 写入任意 `block_id` / 任意 `block_name` 均被拒绝，当前测试 DWG 的 `CODEX_PREVIEW` 实体数保持 `111 -> 111`，没有新增实体。

### PlanMD 后置拆分合并与 Markdown 架构收束

- 按用户要求暂停“额外后备计划”口径，把五大后置主线的小包明细合并为 `CORE_RESTRUCTURE_PLAN.md` 的唯一承载。
- 从 `docs/planning/phase-r-rebirth-implementation-plan.md` 移除后置 Backlog 明细副本，改为只保留 Phase R 当前执行剧本和一条主 PlanMD 引用。
- 补强 `CORE_RESTRUCTURE_PLAN.md`、`AGENTS.md`、`docs/README.md`、`CORE_CONTEXT_BRIEF.md`、`CAD_AGENT_STATUS.md` 和 `docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` 的主从规则：后置 Backlog、未来小包、优先级和退出标准只在主 PlanMD 维护。
- 本轮只做 Markdown 架构收束，不运行真实 CAD，不改变能力成熟度百分比。

### 五大后置主线 Backlog 登记

- 回答“当前小包完成后继续往哪里走”的问题，不新增第二套主计划。
- 在 `CORE_RESTRUCTURE_PLAN.md` 增加“当前小包队列完成后的后置 Backlog”，明确只有当前活跃小包收口或用户明确切换后才启用。
- 五大后置主线为：真实 CAD 能力扩展、真实项目样本闭环、多方案设计与交互确认、自动读图 / 空壳识别、场景 Agent Beta。
- 当时曾在 `docs/planning/phase-r-rebirth-implementation-plan.md` 复制五大主线细化表；随后已按用户要求合并回唯一 PlanMD，不再由执行剧本承载后置小包明细。
- 同步 `CORE_CONTEXT_BRIEF.md` 与 `CAD_AGENT_STATUS.md`，声明该 Backlog 不改变当前 Cursor / Codex 小包执行优先级，也不提升功能成熟度百分比。

### R-OFFICE-MICRO-03 office 场景级 benchmark

- 新增 3 个 office shell + workflow：`long_narrow`、`obstacle_riser`、`mixed_zone`。
- `blank_shell_pipeline` metrics 增加 `no_place_zone_count`、`fixed_obstacle_count`、`shell_id`。
- `office_alpha_benchmark.json` 扩至 **14 cases**（+3 blank_shell scene）。
- 证据：`260 tests OK`；`output/test_artifacts/benchmarks/office_scene_r1/` → 14/14 pass（non-CAD）。

### R-OFFICE-MICRO-02 office 微场景 benchmark

- `composition_engine` 新增 4 个 office micro-scene 模板：`single_desk_chair_pair`、`desk_with_back_cabinet`、`two_workstations_shared_aisle`、`entry_reception_clearance`（含 `bindings`、`clearance_refs`、`circulation`）。
- benchmark runner 支持 `contains_binding_relations`、`contains_circulation_roles`。
- `office_alpha_benchmark.json` 扩至 **11 cases**（+4 composition_spec micro-scenes）。
- 证据：`260 tests OK`；`output/test_artifacts/benchmarks/office_micro_r2/` → 11/11 pass（non-CAD）。

### R-OFFICE-MICRO-01 office 对象级 benchmark 扩展

- `object_defaults.json` 新增 `computer_desk`、`storage_cabinet`、`file_cabinet`（含 `placement_role`、`clearance_refs`、组件 roles）。
- `create_object_spec` 透传 `placement_role` / `clearance_refs` / `assertion_hints`。
- benchmark runner 支持 `contains_clearance_refs` 与 `clearance_ref_roles` metrics。
- `office_alpha_benchmark.json` 由 4 cases 扩至 **7 cases**（新增 `computer_desk_default_spec`、`storage_cabinet_front_clearance`、`file_cabinet_default_spec`）。
- 证据：`259 tests OK`；`run_benchmark_suite.py … office_alpha_benchmark.json` → **7/7 pass**（`output/test_artifacts/benchmarks/office_object_r1/`）。
- 仍为 non-CAD；不能声称办公微场景、通道或真实 CAD 几何准确。

### R-BLOCK-CAD-05 真实 AutoCAD block alpha 验收

- 受控块定义 footprint 与 metadata 对齐（900×450），保证 readback bbox 与 plan 一致。
- `run_cad_validation.py --block-alpha-only` 聚焦 block alpha CAD 步骤；新增 `block_alpha_capture_screen`。
- 用户会话真实 CAD 验收：`output/validation_runs/r-block-alpha-cad/report.json` → `status=pass`；`block_alpha_report.json` → `geometry_verified` / `readback_geometry_verified`；`created_handles=["878"]`；截图 `block-alpha-window.png`（仅视觉辅助）。
- 证据说明：`docs/verification/block_alpha_cad_evidence.md`。
- 不能把受控样本 pass 扩大到任意块库或项目图纸。

### R-BLOCK-CAD-04 CAD validation runner 接入 block alpha

- `cad_validation_runner` 新增 `block_alpha_validate_plan` / `block_alpha_dry_run` / `block_alpha_deferred_evidence`（no-CAD）与 `block_alpha_execute` / `block_alpha_readback`（CAD）。
- 新增 `core/verification/block_alpha_validation.py`、`scripts/run_block_alpha_validation.py`；顶层 `report.json` 含 `block_alpha` 摘要，硬门禁禁止 no-CAD 误报 `geometry_verified`。
- no-CAD 实跑：`output/validation_runs/r-block-alpha-no-cad-test/report.json` → `status=pass`，`block_alpha.geometry_verified=false`。
- 全量 **259 tests OK**；真实 CAD block alpha 总验收仍 deferred 至 `R-BLOCK-CAD-05`。

### R-BLOCK-CAD-03 block_reference readback 标准化

- `normalize_com_entity()` 识别 `AcDbBlockReference`，输出 `block_name`、`insertion_point`、`rotation`（度）、`scale`、`bbox`。
- `geometry_checks.check_block_reference_readback()` 对照 `insert_block_alpha` plan 断言，失败分类含 `readback_missing`、`block_name_mismatch`、`anchor_mismatch`、`rotation_mismatch`。
- `evidence_contract` 中 `block_reference.implementation_status` 更新为 `readback_normalize_baseline`。
- 全量 **255 tests OK**；validation runner 接入仍 deferred 至 `R-BLOCK-CAD-04`。

### R-BLOCK-CAD-02 insert_block_alpha COM 写入

- `AutoCADComDriver.insert_block_alpha()`：先 `ensure_controlled_block_definition()`，再 `ModelSpace.InsertBlock`；仅 `CODEX_PREVIEW`、统一 scale；`definition_missing` / `insert_failed` / `attribute_unverified` 通过 `BlockAlphaInsertionError` 结构化抛出。
- 新增 driver 与 `execute_plan` 契约单测；全量 **250 tests OK**。
- 未运行真实 CAD；几何 readback 仍 deferred 至 `R-BLOCK-CAD-03`。

### R-BLOCK-CAD-01 受控块定义解析

- `AutoCADComDriver` 新增 `block_definition_exists()`、`ensure_controlled_block_definition()` 与最小矩形块定义创建路径；优先复用 DWG 内 `CODEX_TEST_BLOCK_001`，缺失时在 layer `0` 写入 100×50 临时几何，不写正式图层、不保存 DWG。
- 查找/创建失败时返回结构化 `definition_missing`（`status` + `failure_category` + `block_name` + `message`）。
- `docs/planning/phase-r-cad-capability-contract.md` 补充受控块定义解析说明。
- 新增 5 项 `tests.core.test_autocad_com_driver` 用例；全量 **244 tests OK**。
- 未运行真实 CAD；`insert_block_alpha` COM 插入仍 deferred 至 `R-BLOCK-CAD-02`。

### 剩余开发包二级小包拆分

- 按用户截图中的“开发包清单”继续细化当前未开始的包，不新增第二套主计划。
- 在 `CORE_RESTRUCTURE_PLAN.md` 新增并加固“剩余开发包二级拆分索引”，把 `R-BLOCK-CAD-ALPHA`、`R-OFFICE-MICRO`、`R4-EVIDENCE-GATES`、`Y-MULTI-CANDIDATE`、`X-SCENE-ALPHA` 拆成 25 个二级小包，并补充目标、文件范围、依赖顺序、子校验、退出标准、证据状态和 handoff 更新七项完整性门槛。
- 在 `docs/planning/phase-r-rebirth-implementation-plan.md` 为每个未开始父包补“二级小包拆解”和推荐执行顺序，明确文件范围、子校验命令和退出标准；其中 office 子包统一命名为 `R-OFFICE-MICRO-01..05`，避免与旧的 R-OFFICE 高层任务编号混淆。
- 在 `docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` 补齐“剩余开发包细分索引”，让 Cursor / Codex 后续按小包追加 9 项交接记录。
- 本轮只拆分 Markdown 计划，不修改代码、不运行真实 CAD、不声称剩余小包已完成。

### Cursor 开发包交接包文档

- 新增 `docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md`：按开发包汇总 Cursor 交付的 9 项标准交接（含会话探针、`R-CAD-VIEW-CAPTURE`、`R-CAD-CONTRACT`、`R-BLOCK-METADATA`、`R-BLOCK-PLAN` 回填）。
- 新增 `docs/handoffs/README.md` 索引；`AGENTS.md`、`CORE_CONTEXT_BRIEF.md`、`docs/README.md` 增加入口。
- 约定：每完成一个 PlanMD 开发包，必须同步更新交接包文档。

### R-BLOCK-PLAN insert_block_alpha CAD_PLAN

- 新增 `core/plan_engine/block_alpha_plan.py` 与 `examples/plans/insert_block_alpha_test.json`，引入受控 `insert_block_alpha` intent。
- `validate_plan` 现拒绝正式图层、空 `cad_identity.block_name`、非法 `scale` 与缺 `base_point`；仅允许 `CODEX_PREVIEW`。
- `create_dry_run_report` / `dry_run_plan.py` 对 block alpha 输出 bbox、anchor、rotation、layer role 检查，并标记 `evidence_state=dry_run_valid_plan_only` 与 `geometry_accuracy=not_verified_without_cad_readback`。
- `execute_plan.py` 通过 fake driver `insert_block_alpha()` 记录执行意图，不触碰真实 AutoCAD。
- 更新 `core/schemas/cad_plan.schema.json` 与 `schemas/cad_plan.schema.json`。
- 复验：`239 tests OK`；`run_cad_validation.py --no-cad --output-dir output\validation_runs\r-block-plan-no-cad` pass。

### R-BLOCK-METADATA 图块库 v0.2 与受控测试块

- 扩展 `core/schemas/block_library.schema.json` 支持 `0.1` / `0.2`；`0.2` 块含 `source`、`cad_identity`、`anchor_points`、`footprint_2d`、`clearance_zones`、`symbol_2d`、`layer_bindings`、`validation`。
- 升级 `libraries/blocks/block_library.example.json` 为 `0.2`，新增 `controlled-test-block-001`（`metadata_only`）与其余 `symbol_fallback` 家具元数据；侧车文件 `libraries/blocks/controlled/CODEX_TEST_BLOCK_001.metadata.json`。
- 扩展 `core/block_engine/block_library.py`：`normalize_block()`、`validate_block_library()`、`object_spec_to_block_reference()`；`0.1` 示例仍可加载并自动补全 v0.2 派生字段。
- 扩展 `block_selector` / `block_placement`：按 `validation.status` 过滤、`cad_identity` 与 `layer_role` 进入 preview intent。
- 复验：`234 tests OK`；repo audit 0 findings；blank-shell benchmark pass；`run_cad_validation.py --no-cad --output-dir output\validation_runs\r-block-metadata-no-cad` pass。
- 边界不变：不声称真实块插入、公司块库或 `geometry_verified` block readback 已完成。

### R-CAD-CONTRACT 证据契约与硬门禁

- 新增 `core/verification/evidence_contract.py`：集中定义 `ENTITY_CONTRACTS`、`deferred_verification`、证据状态词表，以及 capability probe / readback 报告的注解与校验函数。
- `cad_capability_probe` 现输出 `contract_version`、`evidence_state`、`geometry_accuracy`、`screenshot_role`、`contract`、`limitations`；`cad_capability_verified` 使用 `verified_by_cad_capability_readback`，与 baseline `readback_geometry_verified` 分离。
- `build_verification_report` 现输出 `evidence_state`、`geometry_accuracy`、`screenshot_role`；`geometry_verified` 时标记 `readback_geometry_verified` / `verified_by_cad_readback`。
- `cad_validation_runner` 在 `inspect_readback` 与 `cad_capability_probe` 步骤增加证据字段硬门禁；步骤记录会透传子报告证据字段。
- 更新 `core/schemas/verification_report.schema.json`、`examples/verification_reports/minimal_cabinet_verification.json`、`docs/planning/phase-r-cad-capability-contract.md` 与 Phase R 执行记录。
- 复验：`228 tests OK`；`run_cad_validation.py --no-cad --output-dir output\validation_runs\r-cad-contract-no-cad` 与真实 CAD `r-cad-contract-cad` 均为 `status=pass`。
- 边界不变：不声称 block insertion、真实块库或任意 CAD_PLAN 已验证；截图仍只作视觉辅助。

### 交付进度估算规则写入主入口

- 按用户要求在 `README.md` 增加“交付进度规则”：后续每次 CAD Agent 相关交付，最终回复必须带 `总进度`、`Core 底座开发进度`、`Agent 多场景实现进度` 三项估算。
- 同步 `AGENTS.md` 和 `CORE_CONTEXT_BRIEF.md`，让 Codex 恢复上下文和最终交付时都能看到该要求。
- 将 `CAD_AGENT_RULES.md` 的进度字段名从旧口径统一为 `总进度`、`Core 底座开发进度`、`Agent 多场景实现进度`，默认权重仍为 Core 70%、Agent 30%。
- 更新 `CAD_AGENT_STATUS.md` 的当前进度估算字段名；本次仅固化交付格式，不提升进度百分比。

### R-CAD-VIEW-CAPTURE 实现与真实 CAD 验证

- 按用户要求优先完成窗口级截图小开发包，避免继续依赖全屏截图导致 Codex 或其他窗口遮挡 AutoCAD 画面。
- 扩展 `core/verification/render_preview.py`：`--check` 现在输出 `capture_modes`、`autocad_window`、`autocad_viewport_or_client` 等结构化字段；新增 `--capture-autocad-window`、`--execution-summary`、`--layer` 和 `--fallback-screen`，默认尝试恢复并置前 AutoCAD 窗口，再截取客户区。
- 扩展 `core/cad_io/autocad_com.py`：新增按实体 bbox 计算视图范围、`zoom_to_bbox()` 和 `zoom_to_handles()`，用于在截图前按本轮 created handles 缩放到当前输出范围。
- 更新 `core/verification/cad_validation_runner.py`：真实 CAD 总控截图步骤改为 `cad-validation-window.png`，命令使用 `scripts/render_preview.py --capture-autocad-window --execution-summary <execution_summary.json>`；旧全屏截图路径只作为 stale artifact 清理项保留。
- 扩展测试 `tests/core/test_render_preview.py` 与 `tests/core/test_cad_validation_runner.py`，覆盖无 AutoCAD 窗口时不误报 ready、窗口级截图 bbox、缺窗口失败分类，以及总控必须调用 `--capture-autocad-window`。
- 同步 `CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_RESTRUCTURE_PLAN.md`、`docs/planning/phase-r-rebirth-implementation-plan.md`、`docs/planning/phase-w-cad-validation-plan.md`、`CAD_AGENT_BLOCKER_PLAYBOOK.md`、`CAD_AGENT_AUTONOMOUS_VALIDATION.md`、`docs/onboarding/migration-checklist.md` 和 `CAD_AGENT_ISSUES.md`，把当前执行口径从全屏截图更新为窗口级视觉辅助截图。
- 复验通过：focused tests 11 项 OK；`scripts\render_preview.py --check` 在无可用窗口时只报告 `screen`，不误报窗口级 ready；`scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\r-cad-view-no-cad` 顶层 `status=pass`；真实 CAD `scripts\run_cad_validation.py --output-dir output\validation_runs\r-cad-view-cad` 顶层 `status=pass`。
- 真实 CAD 证据：`output\validation_runs\r-cad-view-cad\cad-validation-window.png` 为 AutoCAD 客户区截图，`capture_screen.stdout.txt` 记录 `mode=autocad_window`、窗口标题 `Autodesk AutoCAD 2026 - [Drawing1.dwg]`、`bbox=[6,0,1914,1028]`、`focus.status=zoomed_to_bbox`、`handle_count=7`；`readback_report.json.status=geometry_verified`，`cad_capability_probe.json.status=cad_capability_verified`。
- 边界不变：截图只作为视觉辅助；真实 CAD 几何准确仍必须以 validate、dry-run、`CODEX_PREVIEW`、created handles 定向回读和 `geometry_verified` 为准。全程只写入 `CODEX_PREVIEW`，未保存 DWG、未覆盖原图、未删除实体、未修改正式图层。

### CAD 窗口级截图开发包登记

- 按用户指出“直接按当前屏幕截图会被 Codex 窗口遮挡”的问题，将 AutoCAD 窗口级 / 视口级截图能力拆成独立开发包 `R-CAD-VIEW-CAPTURE`。
- 在 `CORE_RESTRUCTURE_PLAN.md` 的当前活跃队列和开发包表中加入 `R-CAD-VIEW-CAPTURE`，目标是优先截取 AutoCAD 客户区或按本轮 created handles bbox 缩放后的实体范围截图。
- 在 `docs/planning/phase-r-rebirth-implementation-plan.md` 增加该包的文件范围、开发步骤、子校验命令和通过标准，明确截图仍是 `visual_aid_only`，不能替代 created handles readback。
- 同步 `CORE_CONTEXT_BRIEF.md` 与 `CAD_AGENT_STATUS.md`，把下一轮开发包数量从八个更新为九个；该条为计划登记时状态，随后同日已完成 `R-CAD-VIEW-CAPTURE` baseline 实现与真实 CAD 验证，见上方记录。

### 下一轮开发拆解与子校验计划

- 按用户要求将“先推进 R-CAD / R-BLOCK、补 office micro-scene 与 failure benchmark、强化 blank-shell 多候选、保持 Core 优先”的开发建议落入 Markdown。
- 在 `CORE_RESTRUCTURE_PLAN.md` 新增“下一轮开发拆解与子校验”，把后续工作拆成 `R-CAD-CONTRACT`、`R-BLOCK-METADATA`、`R-BLOCK-PLAN`、`R-BLOCK-CAD-ALPHA`、`R-CAD-VIEW-CAPTURE`、`R-OFFICE-MICRO`、`R4-EVIDENCE-GATES`、`Y-MULTI-CANDIDATE`、`X-SCENE-ALPHA` 九个开发包。
- 在 `docs/planning/phase-r-rebirth-implementation-plan.md` 新增文件级开发拆解，明确每个开发包的目标、文件范围、开发步骤、子校验命令和通过标准。
- 本轮只细化计划与校验路径，不修改代码、不运行真实 CAD、不提升能力成熟度，也不把 block insertion、office micro-scene 或 blank-shell 多候选写成已完成能力。

### PlanMD 主线权威收束

- 按用户要求继续雕琢整体文档架构，明确 `CORE_RESTRUCTURE_PLAN.md` 是唯一 `PlanMD` / 开发主线；根目录没有独立 `plan.md`，用户说 `PlanMD`、`plan.md` 或主 plan 时都指向该文件。
- 在 `CORE_RESTRUCTURE_PLAN.md` 新增 “PlanMD 主线协议”，把文档层级收束为：PlanMD 决定当前队列、Phase 顺序、优先级、Decision Gate 和退出标准；`docs/planning/phase-*.md` 只做辅助执行剧本；状态、路线、架构、治理、交接、验证、历史和 review 文档只服务主线。
- 更新 `AGENTS.md`、`CORE_CONTEXT_BRIEF.md`、`CAD_AGENT_RULES.md`、`README.md`、`docs/README.md`、`docs/planning/README.md`、`docs/onboarding/first-handoff.md` 与 `docs/governance/multi-agent-contribution.md`，让后续 Codex 恢复上下文时不会把多个 Markdown 误读成多条并列计划。
- 给 Phase R/W/X/Y/Z 相关 `docs/planning/*.md` 顶部补充“辅助执行剧本，不是独立 PlanMD”的提示，并把同步日期调整到 2026-05-26。
- 最后一轮按用户担心补强“防偏离边界”：PlanMD 只是文档治理和开发排序，不改变通用 CAD Agent Core Lab、Core 优先、`CAD_PLAN` 中间层、真实 CAD created-handle 回读门槛、场景 Agent 轻量化和保护用户 DWG 的根方向。
- 修正 `CAD_AGENT_RULES.md` 中进度估算的旧基准，使其与 `CORE_STATUS.md` / `CAD_AGENT_STATUS.md` 当前口径一致：通用底座约 70%，多场景 Agent 约 34%，总体约 59%。
- 本轮仍只改 Markdown，不改代码、不运行 CAD、不扩大任何真实 CAD 几何验证结论。

### 二次文档架构雕琢

- 按用户要求以“今天开发收尾”为边界，只做 Markdown 和文档入口重构，不修改 `core/`、`scripts/`、`drivers/`、`tests/`、`agents/`、`libraries/`、`projects/`、`examples/` 或 `schemas/`。
- 派出 AI 产品经理与深度架构程序员两个只读 agent 审阅仓库信息架构，结论收束为：代码边界基本成立，当前主要问题是入口权威性、计划散落、历史材料仍在根目录。
- 将低频文档迁出根目录：`SHELL_LAYOUT_FOUNDATION_DESIGN.md` 迁到 `docs/architecture/shell-layout-foundation-design.md`，`SHELL_LAYOUT_TIME_ESTIMATE.md` 迁到 `docs/history/shell-layout-time-estimate.md`，`CAD_AGENT_DECISIONS.md` 迁到 `docs/decisions/cad-agent-decisions.md`。
- 将已执行的 `docs/planning/core-platform-md-split-plan.md` 迁为 `docs/history/core-platform-md-split-plan-2026-05-25.md`，并新增 `docs/history/README.md`。
- 将 README 中的长篇换机清单拆到 `docs/onboarding/migration-checklist.md`，README 只保留入口链接；同步修正 README 中 `219 tests` 到 `223 tests`，并修正“没有真实回读”这类过期口径为“真实回读覆盖仍有限”。
- 将 `CORE_RESTRUCTURE_PLAN.md` 标题和职责收束为唯一主计划，新增“当前活跃工作队列”；`CORE_STATUS.md` 与 `CAD_AGENT_STATUS.md` 不再承载独立下一步清单，只保留能力、证据、缺口和风险边界。
- 更新 `CORE_CONTEXT_BRIEF.md`、`CAD_AGENT_RULES.md`、`docs/planning/README.md`、`docs/architecture/README.md`、`docs/onboarding/first-handoff.md` 和 Phase 文档中的旧路径、旧计划口径与主从关系。
- 新增 `docs/README.md` 作为文档区总地图，更新 `docs/onboarding/README.md` 补换机清单入口，并将 `docs/ROADMAP.md` 降级为兼容跳转，避免旧阶段路线干扰当前 `CORE_ROADMAP.md` 与主计划。

## 2026-05-25

### Phase R 角色组合真实 CAD 落图与回读

- 根据用户指出“这些东西不是在 CAD 里面”，将此前仅有 SVG/浏览器 PNG 的角色组合自检推进到真实 AutoCAD：新增 `core/execution/batch_plan_runner.py`，支持对多份 CAD_PLAN 做坐标偏移、逐 plan 执行、created handles 汇总和 `geometry_verified` 回读报告。
- 新增 `scripts/run_composition_cad_check.py`，把 `examples/benchmarks/interior_delivery_benchmark.json` 产出的卧室床+地毯、餐桌组合、办公桌组合三组 CAD_PLAN 批量写入当前 AutoCAD 的 `CODEX_PREVIEW` 图层，并输出 `composition_cad_check_report.json`。
- 为避免覆盖或删除旧预览对象，真实 CAD 组合校验脚本支持 `--start-x`、`--start-y`、`--spacing-x` 参数；本轮最终使用 `--start-x 26000 --start-y 8000 --spacing-x 4200` 绘制到上方空白区域，未删除旧实体、未保存 DWG、未修改正式图层。
- 修复组合落图的 CAD 标注可读性问题：地毯作为底衬不再生成文字实体，大尺寸对象文字高度封顶，餐椅标签缩短为 `Chair`，避免真实 CAD 组合视图被文字遮挡。
- 新增和扩展测试：`tests/core/test_batch_plan_runner.py` 覆盖批量计划偏移与 fake readback，`tests/core/test_run_composition_cad_check.py` 覆盖 fresh CAD region 偏移参数，`tests/core/test_composition_engine.py` 与 `tests/core/test_execute_plan.py` 锁定组合标注策略和文字高度上限。
- 真实 CAD 复验通过：`output\validation_runs\interior-composition-cad-label-clean-y8000\composition_cad_check_report.json` 顶层 `status=geometry_verified`，3/3 cases verified，created handles 共 55 个；截图证据为 `output\validation_runs\interior-composition-cad-label-clean-y8000\composition-cad-screen-clean-y8000.png`。
- 最终回归通过：`unittest discover -s tests` 为 223 tests OK，`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings，`run_benchmark_suite.py examples\benchmarks\interior_delivery_benchmark.json` 为 3/3 pass，`run_cad_validation.py --no-cad --output-dir output\validation_runs\manual-no-cad-after-composition-cad` 为 `status=pass`。
- 证据边界更新：现在可以说这 3 个简单矩形对象组合已经真实落到 AutoCAD 并完成 created handles 回读；仍不能说已经完成真实家具块库、块插入、复杂符号、任意组合或真实项目图纸自动设计。
- 粗估进度小幅上调为：通用底座约 70%，多场景 Agent 约 34%，总体约 59%。该上调来自真实 CAD 组合回读闭环，不等同于达到 80% 或完成块库能力。

### Phase R 角色驱动组合交付自检

- 按用户提出的“模拟室内设计行业用户拿系统交付图块组合”的新维度，新增通用 `core/composition_engine/`，不把卧室、餐桌或办公桌组合写死进某个场景 Agent。
- 新增 `composition_spec` 生成能力：当前可把 `bedroom_bed_rug`、`dining_table_set`、`office_desk_combo` 转成组合规格、多份安全 `CAD_PLAN`、dry-run 报告、unverified verification 报告和 SVG 视觉辅助预览。
- 扩展 `libraries/objects/object_defaults.json`，新增 `rug` 与 `monitor` 对象默认规格，支持床+地毯、餐桌+椅、办公桌+椅+显示器三类组合。
- 扩展 `core/benchmarks/runner.py`：新增 `composition_spec` pipeline、`contains_object_roles` 断言、组合级 metrics、每个组合 CAD_PLAN 的 dry-run / verification 汇总和 `preview_svg` artifact。
- 新增 `examples/benchmarks/interior_delivery_benchmark.json`，模拟 `interior_designer`、`home_designer`、`office_planner` 三个角色，分别验收卧室床+地毯、餐桌组合和办公桌组合。
- 新增 `tests/core/test_composition_engine.py`，并扩展 `tests/core/test_benchmarks.py`，按 TDD 覆盖组合生成、plan-ready、视觉辅助 artifact 与 persona benchmark。
- 浏览器视觉检查发现首版 SVG 标题区与图形区过近，已修正 `write_composition_preview_svg()` 的标题留白并重新生成截图。
- 新鲜复验：`unittest discover -s tests` 为 219 tests OK；`run_benchmark_suite.py examples\benchmarks\interior_delivery_benchmark.json` 为 3/3 pass；三张浏览器截图保存到 `output\test_artifacts\benchmarks\interior_delivery_manual\*\preview-browser.png`。
- 证据边界保持不变：本轮组合交付是 non-CAD benchmark 和视觉辅助预览，显式保留 `geometry_accuracy=not_verified_without_cad_readback` 与 `screenshot_role=visual_aid_only`，不能声称真实 CAD created-handle 几何已验证。
- 粗估进度小幅上调为：通用底座约 67%，多场景 Agent 约 31%，总体约 56%。该上调来自角色组合自检和 benchmark 证据增强，不来自真实 CAD 几何扩展。

### Phase R office benchmark 与证据状态 runner

- 按“继续通用底座深度开发”推进 Phase R 的 benchmark 代码切口，不运行真实 CAD，不修改 DWG。
- 扩展 `core/benchmarks/runner.py`：benchmark actual 现在包含 `evidence_state`、`geometry_accuracy`、`screenshot_role`、`object_types`、`component_roles` 和对象尺寸；expected 支持 `minimums`、`contains_object_types` 与 `contains_component_roles` 断言；新增 `object_spec` benchmark pipeline。
- 扩展 `core/workflows/blank_shell_pipeline.py`：metrics 增加 `object_types`，让 benchmark 能验证场景对象覆盖。
- 加固 benchmark 门禁：suite 中空 cases、非 object case、缺 `expected` 或空断言不再静默 pass；blank-shell 现在为每个生成的 CAD_PLAN 输出 `dry_run_reports.json` 与 `verification_reports.json`，runner 使用汇总状态而不是只看第一个 plan。
- 新增 `examples/benchmarks/office_alpha_benchmark.json`，当前包含 desk / chair / cabinet object spec 与 `office_small_suite_alpha` scene 共 4 个 cases，验证对象尺寸、组件角色、场景对象类型、最小指标和 `benchmark_pass_non_cad` 证据状态。
- 扩展 `tests/core/test_benchmarks.py`，按 TDD 增加 Phase R 证据状态与 office alpha benchmark 回归测试。
- 新鲜复验：`unittest discover -s tests` 为 214 tests OK；`run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json` 为 4/4 pass；`run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json` 为 4/4 pass；`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings。
- 证据边界保持不变：office alpha benchmark 是非 CAD 证据，显式写 `geometry_accuracy=not_verified_without_cad_readback` 和 `screenshot_role=visual_aid_only`，不能声称真实 CAD 几何准确。
- 粗估进度小幅上调为：通用底座约 64%，多场景 Agent 约 29%，总体约 54%。该上调来自 benchmark/office alpha 证据增强，不来自真实 CAD 几何扩展。

### Phase R 执行开发包细化

- 按用户要求继续执行修改后的 Phase R plan，创建多个只读专项 agent 细化 CAD 能力契约、办公 benchmark、图块库路线和多 agent 协作治理。
- 新增 `docs/planning/phase-r-rebirth-implementation-plan.md`，将 Phase R 拆成 R0-R5、R-GOV / R-CAD / R-BLOCK / R-OFFICE 任务和证据状态门禁。
- 新增 `docs/planning/phase-r-cad-capability-contract.md`，定义 line / rectangle / circle / arc / polyline / text / dimension / block_reference 的 write-read-verify 契约和 `insert_block_alpha` 草案。
- 新增 `docs/planning/phase-r-block-library-roadmap.md`，定义 `BLOCK_LIBRARY v0.2`、OBJECT_SPEC、drawing standard profile、受控测试块和 block insertion 迁移路线。
- 新增 `docs/planning/phase-r-office-benchmark-cases.md`，将办公桌、办公椅、电脑桌、柜体、入口、主通道和失败样本整理为 object / micro-scene / scene / failure benchmark cases。
- 新增 `docs/governance/multi-agent-contribution.md` 与 `docs/onboarding/first-handoff.md`，固化多 agent 协作边界、新人接手入口和不可声称边界。
- 更新 `CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CORE_ROADMAP.md`、`README.md` 和 `docs/planning/README.md`，让后续开发优先读取 Phase R 执行包。
- 本轮仍只改 Markdown；不修改代码、不运行 CAD、不把执行计划当成功能完成。

### Phase R 新鲜视角评审与重生式开发计划

- 按用户要求，创建多个只读专家 agent，从 CAD 自动化、图块库/制图标准、空间设计业务、平台架构、验证/benchmark 五个新鲜视角审视当前系统。
- 新增 `docs/reviews/fresh-eyes-review-2026-05-25.md`，记录多 agent 首次接手式评审结论。
- 新增 `docs/planning/phase-r-fresh-perspective-rebirth-plan.md`，将“重生式开发”收敛为 CAD 能力契约、办公基础闭环、图块库设计、benchmark 证据门禁和平台协作治理。
- 更新 `CORE_RESTRUCTURE_PLAN.md`：新增 Phase R、当前可信基线索引、Phase 状态语义、Interface Ownership Map、Decision Gates 和 Alpha 里程碑判定。
- 更新 `CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CORE_ROADMAP.md`、`README.md` 和 `docs/planning/README.md`，把 Phase R 纳入后续开发入口。
- 本轮仍只改 Markdown；不修改代码、不运行 CAD、不把新鲜视角评审当成 Core Alpha 完成。

### 主平台 Markdown 拆分执行

- 按 `docs/planning/core-platform-md-split-plan.md` 执行主平台 Markdown 拆分。
- 新增 `docs/planning/phase-w-cad-validation-plan.md`、`docs/planning/phase-x-scene-agent-alpha-plan.md`、`docs/planning/phase-y-blank-shell-hardening-plan.md`、`docs/planning/phase-z-doc-governance-plan.md`，分别承接 Phase W/X/Y/Z 的长篇执行剧本。
- 将 `CORE_RESTRUCTURE_PLAN.md` 收缩为主计划总控索引，保留当前复盘、能力边界、文档职责、阶段路线、Phase 执行入口、分歧点和完成判定。
- 更新 `CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`README.md` 和 `docs/planning/README.md`，让后续开发按目标 Phase 读取 `docs/planning/phase-*.md`。
- 根据只读复核 agent 反馈，修正 `README.md` 中旧的 196 项测试、21:42 复验时间、旧 CAD 证据路径和 entity readback 状态漂移，并修正 Phase Z 文档里 “本文收缩为总控索引” 的指代。
- 本次仍只改 Markdown 文档；真实 CAD 结论仍只覆盖已验证的 baseline plan 和 CAD capability probe，不扩大到真实项目图纸、块库、块插入或任意 CAD_PLAN。

### 主平台 Markdown 精细化拆分计划

- 用户要求本轮不改代码，先构建主平台 Markdown 拆分计划，为下一步执行降低上下文抖动。
- 新增 `docs/planning/` 作为规划类文档目录，并新增 `docs/planning/core-platform-md-split-plan.md`。
- 计划将 `CORE_RESTRUCTURE_PLAN.md` 收缩为总控索引，把 Phase W/X/Y/Z 的长篇执行剧本迁入 `docs/planning/phase-*.md`。
- 同步更新 `CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`CAD_AGENT_STATUS.md` 和 `README.md` 的入口说明。
- 本轮不修改 `core/`、`scripts/`、`drivers/`、`tests/`、`agents/` 或 CAD 图纸；真实 CAD 结论边界保持不变。

### 开发进度百分比口径固化

- 按用户要求新增长期规则：后续每次 CAD Agent 相关改动后，都要大概估算并汇报 `通用底座进度`、`多场景 Agent 进度` 和 `总体进度`。
- 固定默认权重：总体进度按 `通用底座 70% + 多场景 Agent 30%` 加权；百分比只作节奏判断，不替代真实验证证据。
- 写入 `CAD_AGENT_RULES.md` 的 `0.4 开发进度百分比估算口径`。
- 在 `CORE_STATUS.md` 和 `CAD_AGENT_STATUS.md` 写入当前基准估算：通用底座约 63%，多场景 Agent 约 28%，总体约 53%。
- 明确该估算允许 5-10 个百分点误差；只有形成可复验证据、状态同步和边界说明后才小幅上调，发现回归或验证缺口时可以下调。

### 基础图元 CAD 探针扩展与截图复验

- 用户要求用截图方式真实检验当前系统是否能调用 CAD 画出具体内容，并指出此前 CAD 测试覆盖过浅。
- 按 TDD 补充失败测试：`tests/core/test_autocad_com_driver.py` 覆盖 `draw_line`、`draw_circle`、`draw_arc`、`draw_polyline` 的 COM 调用参数；`tests/core/test_verification_report.py` 覆盖圆、弧、多段线回读标准化；`tests/core/test_cad_capability_probe.py` 要求能力探针从 7 个实体扩展到 11 个实体。
- 扩展 `core/cad_io/autocad_com.py`：新增独立直线、圆、弧、轻量多段线写入；弧角度从度转换为 AutoCAD COM 需要的弧度；多段线点集转换为 `VT_ARRAY | VT_R8` 2D 坐标数组。
- 扩展 `core/verification/inspect_dwg.py`：回读时识别 `circle`、`arc`、`polyline`，并为圆、弧、多段线补充中心、半径、角度、点集、闭合状态和 bbox 信息。
- 扩展 `core/verification/cad_capability_probe.py`：能力矩阵现在绘制并回读 1 个矩形边框、1 条独立直线、1 个圆、1 段弧、1 条闭合多段线、1 段文字和 2 个标注，预期类型统计为 `line=5`、`circle=1`、`arc=1`、`polyline=1`、`text=1`、`dimension=2`。
- 真实 CAD 单独探针通过：`output\validation_runs\manual-primitive-cad-probe\cad_capability_probe.json` 为 `status=cad_capability_verified`，entity_count 为 11，bbox 为 `900.0 x 450.0`，全部实体在 `CODEX_PREVIEW`。
- 缩放 AutoCAD 视图后截取视觉证据：`output\validation_runs\manual-primitive-cad-probe\cad-primitive-screen.png`，大小 538584 bytes；图面可见青色 `CAD_CAPABILITY_PROBE` 基础图元和黄色 `测试柜` baseline。
- 重新运行真实 CAD 总控通过：`output\validation_runs\manual-cad-after-primitive-probe\report.json` 顶层 `status=pass`，`readback_report.json.status=geometry_verified`，`cad_capability_probe.json.status=cad_capability_verified`。
- 安全边界保持不变：只写入 `CODEX_PREVIEW`，未保存 DWG，未覆盖原图，未删除实体，未修改正式图层。当前仍不能扩大为块插入、块库、正式图层或任意业务 CAD_PLAN 全部准确。

### CAD 调用底座能力矩阵加固

- 新增 `core/verification/cad_capability_probe.py` 与 `scripts/run_cad_capability_probe.py`，用于真实 AutoCAD COM 能力探针：活动文档读取、`CODEX_PREVIEW` 图层、矩形 4 线、文字、2 个标注、created handles、handle 定向回读、类型统计、bbox 和安全边界。
- 将 `cad_capability_probe` 纳入 `core/verification/cad_validation_runner.py` 的真实 CAD step；`run_cad_validation.py` 现在不仅要求 `readback_report.json.status=geometry_verified`，还要求 `cad_capability_probe.json.status=cad_capability_verified` 且 checks 全部 `pass`。
- 新增 `tests/core/test_cad_capability_probe.py`，并扩展 `tests/core/test_cad_validation_runner.py`，覆盖能力探针成功、连接失败、handle 回读缺失、以及总控不得把非 `cad_capability_verified` 探针误判为 pass。
- 离线复验通过：`unittest discover -s tests` 为 207 tests OK；`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings；`scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\cad-foundation-no-cad-final-20260525` 为 `status=pass`。
- 单独真实 CAD 能力探针通过：`output\validation_runs\cad-foundation-capability-probe-20260525\cad_capability_probe.json` 为 `status=cad_capability_verified`，created handles 为 `3966, 3967, 3968, 3969, 396A, 396B, 39A6`。
- 整合真实 CAD 总控通过：`output\validation_runs\cad-foundation-full-cad-20260525\report.json` 顶层 `status=pass`；`readback_report.json.status=geometry_verified`；`cad_capability_probe.json.status=cad_capability_verified`，探针 handles 为 `3A5E, 3A5F, 3A60, 3A61, 3A62, 3A63, 3A9E`。
- 新增 `docs/verification/cad_foundation_capability_check.md` 记录本轮证据。全程只写入 `CODEX_PREVIEW`，未保存 DWG，未覆盖原图，未删除实体，未修改正式图层。

### Phase W 全量修复：readback 硬门禁与真实 CAD 定向回读

- 执行全量修复复验时发现一个关键门禁问题：`output\validation_runs\full-repair-cad-20260525-212001\report.json` 顶层为 `status=pass`，但 `readback_report.json.status=screenshot_captured`，`geometry_readback` 为 `not_run`，`created_handles_scope` 为 `warning`。该结果不能证明几何准确。
- 按 Phase W W.10 自动修复仓库内问题：`core/verification/cad_validation_runner.py` 现在会在 `inspect_readback` 返回 0 后继续解析 readback JSON，只有 `status=geometry_verified` 且全部 checks 为 `pass` 才允许 step 通过；否则归类为 `readback_failed`。
- 修复真实大 DWG 回读性能风险：`core/verification/inspect_dwg.py` 和 `core/cad_io/autocad_com.py` 支持按 `execution_summary.created_handles` 调用 `Document.HandleToObject(handle)` 定向回读本轮实体，避免全量枚举 ModelSpace。
- 新增 / 扩展测试：`tests/core/test_cad_validation_runner.py` 覆盖非 `geometry_verified` readback 不得让 CAD 总验证通过；`tests/core/test_verification_report.py` 覆盖按 handles 回读时不得扫描 ModelSpace。
- 复验通过：`unittest discover -s tests` 为 203 tests OK；`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings；`scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\full-repair-no-cad-final-20260525` 为 `status=pass`。
- 真实 CAD 复验通过：`output\validation_runs\full-repair-cad-retry-20260525-212916\report.json` 顶层 `status=pass`；`execution_summary.json` 记录 created handles `38E9, 38EA, 38EB, 38EC, 38ED, 38EE, 392A`；`cad-validation-screen.png` 已生成；`readback_report.json.status=geometry_verified`，`readback_scope` / `layer_entities` / `bbox_size` / `base_point` / `label_text` / `dimension_count` / `created_handles_scope` 全部 `pass`。
- 全程只写入 `CODEX_PREVIEW`，未保存 DWG，未覆盖原图，未删除实体，未修改正式图层。当前仍只允许声明 Phase W baseline `examples\plans\draw_test_cabinet.json` 的真实 CAD 几何通过。

### Phase W 真实 CAD 调用排查与 baseline 回读闭环通过

- 对“CAD 已打开但脚本无法调用”做沙箱内/用户会话对照诊断：默认命令身份 `desktop-r40v31q\codexsandboxoffline` 看不到用户桌面的 `acad.exe`、窗口和 ROT/COM 活动对象；沙箱外用户身份 `desktop-r40v31q\user` 可见 AutoCAD PID 20880、窗口 `Autodesk AutoCAD 2026 - [A1_page2_vector_full.dwg]`，且 `AutoCAD.Application`、`AutoCAD.Application.25.1`、`AutoCAD.Application.25` 均可 `GetActiveObject`。
- 诊断证据：沙箱内 `output\validation_runs\cad-com-diagnostic-20260525-210153\cad_com_diagnostic.json`；用户会话 `output\validation_runs\cad-com-diagnostic-elevated-20260525-210219\cad_com_diagnostic.json`。
- 在用户会话下复跑 W-07 首次推进到 `execute_sample_plan`，发现真实 AutoCAD `ModelSpace.AddLine` 对普通 Python tuple 报 `-2147024809` 参数无效；按 W.10 自动修复仓库内 driver 问题。
- `core/cad_io/autocad_com.py` 新增 AutoCAD COM point 转换：坐标写入前转成 `VT_ARRAY | VT_R8` float VARIANT；同步扩展 `tests/core/test_autocad_com_driver.py`，并适配 `tests/core/test_execute_plan.py` 的 fake driver 测试。
- 复跑真实 CAD 总验证通过：`output\validation_runs\cad-readback-alpha-elevated-retry-20260525-210850\report.json` 顶层 `status=pass`，`execution_summary.json` 记录 created handles `3773, 3774, 3775, 3776, 3777, 3778, 37B5`，`cad-validation-screen.png` 已生成，`readback_report.json.status=geometry_verified`。
- 已逐项审查 `readback_report.json` 关键 checks：`readback_scope`、`layer_entities`、`bbox_size`、`base_point`、`label_text`、`dimension_count`、`created_handles_scope` 全部 `pass`。全程只写入 `CODEX_PREVIEW`，未保存 DWG、未覆盖原图、未删除实体、未修改正式图层。
- 当前允许声明 Phase W baseline `examples\plans\draw_test_cabinet.json` 的真实 CAD 几何已通过；不扩大为真实项目图纸、块库或任意 CAD_PLAN 全部准确。

### Phase W W-05/W-06 推进与 COM 诊断加固

- 执行 Phase W W-05：审查 `output\validation_runs\phase-w-preflight-no-cad\report.json`，确认 no-cad preflight 顶层 `status=pass`，失败步骤数量为 0，因此无需进入失败分类修复。
- 执行 Phase W W-06：用只读 `AutoCADComDriver(connect_existing_only=True)` 探测当前 AutoCAD 前置条件，不落图、不保存、不修改图层；证据写入 `output\validation_runs\phase-w-w06-cad-probe\autocad_com_connect.stdout.txt` 与 `autocad_com_connect.stderr.txt`。
- W-06 当前结论为 `external_blocker`：当前环境无法通过 `AutoCAD.Application` 连接活动文档，底层 COM 返回 `(-2147221005, '无效的类字符串', None, None)`。因此本轮未进入 W-07 真实 CAD 总验证。
- 完成一项小型加固：`core/cad_io/autocad_com.py` 在 `connect_existing_only=True` 连接失败时保留底层 COM detail，避免把 ProgID / 注册 / 运行状态问题压成泛化错误。
- 新增 `tests/core/test_autocad_com_driver.py`，锁定 AutoCAD COM 连接失败时必须保留底层错误细节；相关 focused tests 通过，最终全量 `unittest discover -s tests` 当前为 199 tests OK。
- 复跑无 CAD 总控：`scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\phase-w-preflight-no-cad-after-w06-hardening` 顶层 `status=pass`。
- 同步更新 `README.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CORE_RESTRUCTURE_PLAN.md`、`CAD_AGENT_STATUS.md` 和 `CAD_AGENT_ISSUES.md`；继续明确 no-cad pass 与 W-06 COM 探针都不等于真实 CAD 几何验证。

### Phase W W-07/W-16 总验证收束

- 执行 W-07 真实 CAD 总验证：首次运行 `output\validation_runs\cad-readback-alpha\report.json` 暴露出 runner 缺陷，即 `autocad_com_connect` 已失败后仍继续执行落图、截图和回读，导致顶层状态被连锁错误污染为 `fail`。
- 按 W.10 自动修复仓库内问题：为 `cad_validation_runner` 增加 CAD 依赖门，`autocad_com_connect` 或 `execute_sample_plan` 失败后，后续依赖 CAD step 标记为 `not_run` 并保留 stdout/stderr 证据。
- 补充 runner 派生 artifact 清理：每轮开始清理本轮可能生成的 `execution_summary.json`、`readback_report.json` 和 `cad-validation-screen.png`，避免复用输出目录时旧证据冒充本轮结果。
- 加固 AutoCAD COM 连接兼容：`AutoCADComDriver` 现在会尝试常见版本化 ProgID，例如 `AutoCAD.Application.25.1`、`AutoCAD.Application.25`，并在失败时列出所有候选错误。
- 新增 / 扩展测试：`tests/core/test_cad_validation_runner.py` 覆盖 CAD 前置失败时依赖步骤必须 `not_run`；`tests/core/test_autocad_com_driver.py` 覆盖版本化 ProgID fallback。
- 复跑 W-07：最新报告为 `output\validation_runs\cad-readback-alpha-retry-20260525-205208\report.json`，顶层状态为 `external_blocker`。非 CAD 步骤均 pass，`autocad_com_connect` 为 `cad_connection_failed`，后续落图、截图、回读均 `not_run`。
- 完成 W-15 / W-16：新增 `docs/verification/cad_readback_alpha_check.md`，并同步更新 README、短上下文、能力矩阵、主计划、当前状态和问题记录。当前仍不能声明 baseline 真实 CAD 几何通过。
- 用户再次确认 CAD 已打开后，重跑 W-07 到 `output\validation_runs\cad-readback-alpha-retry-20260525-205208\report.json`；结果仍为 `external_blocker`。补充环境探测：系统存在两个 `acad.exe` 进程，但 `MainWindowTitle` 为空，窗口枚举未发现可见 AutoCAD/DWG 窗口，版本化 COM Dispatch 探测 30 秒超时。本轮继续不生成几何通过结论。

### Phase W CAD 验收剧本细化

- 基于当前系统遗留的 CAD 层面待检查内容，重构 `CORE_RESTRUCTURE_PLAN.md` 的 Phase W，不执行 CAD 验证，只把后续可执行步骤写入主计划。
- Phase W 现在包含：已完成内容聚合、验证范围、执行前条件、输出目录、证据清单、执行顺序总表、CAD 待检查矩阵、W-01 到 W-16 分步执行清单、失败分类、自动修复策略、`geometry_verified` 升级门槛、停止问用户条件、继续自动修条件、退出标准和完成后同步文档。
- 明确一个关键门禁：`scripts/run_cad_validation.py` 顶层 `status=pass` 仍不足以单独证明真实 CAD 几何准确；后续执行 Phase W 时必须继续审查 `readback_report.json.status` 和关键 checks，只有 `status=geometry_verified` 且证据完整时才允许声明 baseline 真实 CAD 几何通过。
- 同步更新 `CAD_AGENT_STATUS.md`，提示后续有 AutoCAD 和测试 DWG 时直接按主计划 Phase W 的 W-01 到 W-16 执行。

### 系统层状态复盘与下一阶段计划更新

- 基于 Phase O-V、系统层安全补强和最新非 CAD 基线，对根目录开发状态文档做系统级复盘；本轮不执行功能开发，只更新计划、状态、路线、设计映射和维护口径。
- 重写 `CORE_RESTRUCTURE_PLAN.md`：明确根目录没有独立 `plan.md`，当前主计划就是 `CORE_RESTRUCTURE_PLAN.md`；下一阶段收束为 Phase W 真实 CAD 回读闭环、Phase X 场景 Agent Alpha、Phase Y 空壳布局硬化、Phase Z 文档治理和回归基线。
- 重写 `CORE_STATUS.md` 为能力矩阵页，区分 `alpha_ready_non_cad`、`prototype`、`blocked_by_cad` 等状态，并明确 blank-shell pipeline 可用但不等于真实 CAD 几何准确。
- 压缩 `CAD_AGENT_STATUS.md` 为当前进展页，删除长历史式重复描述，历史细节继续由本文承载。
- 重写 `CORE_CONTEXT_BRIEF.md`，保持短入口职责，更新当前结论、下一步路线、按需展开表和文档自查命令。
- 重写 `CORE_ROADMAP.md`，从旧阶段 0-10 的错位描述调整为高层路线：已完成路线、当前 Phase W/X/Y/Z、长期路线和路线约束。
- 更新 `README.md` 的当前状态、主计划说明和后续开发主线，避免继续把旧阶段口径当作当前计划。
- 更新 `SHELL_LAYOUT_FOUNDATION_DESIGN.md`：说明它已从早期蓝图部分落地为 Phase P-V 的 blank-shell pipeline，并列出已完成能力与剩余差距。
- 更新 `SHELL_LAYOUT_TIME_ESTIMATE.md`：标注其为历史估算和预期管理材料，不作为当前开发进度来源。
- 更新 `CAD_AGENT_DECISIONS.md`：标记 D003 已被根目录 `AGENTS.md` 取代，并新增 D007 短上下文入口、D008 主 plan 映射两条决策。
- 本次复盘未删除根目录 Markdown。判断这些文件不是完全重复，而是需要职责分层；后续若继续瘦身，优先迁移到 `docs/archive/` 或 `docs/planning/`，不直接删除历史依据。

### 系统层安全重构收尾

- 完成 repo audit、测试/脚本/legacy driver bootstrap、capability registry facade 拆分、pipeline failure hardening、verification edge tests、文档同步和最终复核。
- 新增 `docs/verification/system_hardening_audit.md` 作为长期审计报告；大型维护规则已迁移到 `CAD_AGENT_RULES.md`，临时执行计划已删除。
- `scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings` 当前为 pass，0 findings；重复路径注入只保留在共享 bootstrap 与测试 fixture 中。
- 补强 repo audit 的路径污染识别：覆盖 `sys.path.append/extend`、`import sys as ...`、`from sys import path ...` 与 `__path__.append(...)` 等常见形态。
- 补强 blank-shell pipeline 与 capability runner 路径边界：workflow 输入必须留在 project root 内，输出 artifacts 必须留在 `output/` 下；缺文件、坏 JSON、越界路径返回结构化失败，不再 traceback 或写到仓库外。
- 修复 `run_validation()` 兼容入口的相对 `output_dir` 解析，使其跟随显式 `root`，避免 `root != cwd` 时报告写错位置。
- 完成最终无 CAD 验证：focused hardening tests 通过，全量 `unittest discover -s tests` 196 项通过，`self_check.py` pass，`render_preview.py --check` ready，blank-shell pipeline status ok，blank-shell 4 场景 benchmark 4/4 pass，`run_cad_validation.py --no-cad --output-dir output\validation_runs\hardening-polish-no-cad` status pass。

### 开发状态同步与非 CAD 基线复验

- 检查当前仓库状态后，确认没有独立 `plan.md`；按 `CORE_RESTRUCTURE_PLAN.md` 的约定，用户提到 `plan.md` 时默认指该主计划文件。
- 同步更新 `CORE_RESTRUCTURE_PLAN.md` 的状态口径：Phase O-V 非 CAD 主线已通过，下一步进入 Phase W 真实 CAD readback 补验与 Phase X 场景 Agent Alpha 验收。
- 复验当时的非 CAD 基线：`unittest discover -s tests`、`self_check.py`、`validate_plan.py`、`dry_run_plan.py`、`render_preview.py --check` 和 `inspect_dwg.py --no-cad` 均通过；当前测试数量以本日“系统层安全重构收尾”记录为准。
- 复验 blank-shell 链路：`scripts/run_blank_shell_pipeline.py examples\workflows\blank_shell_layout_loop.json --output-dir output\test_artifacts\blank_shell_pipeline\docs-sync` 为 status ok；`scripts/run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\docs-sync` 为 4/4 pass。
- 复验无 CAD 总控：`scripts/run_cad_validation.py --no-cad` 为 status pass；当前报告路径以本日“系统层安全重构收尾”记录为准。
- 更新 `README.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md` 和 `CORE_CONTEXT_BRIEF.md`，统一写清“非 CAD 通过不等于真实 CAD 几何准确”的证据边界。

### 稳定短上下文入口

- 新增 `CORE_CONTEXT_BRIEF.md`，作为后续 Codex 日常恢复上下文的稳定短入口，集中记录当前结论、下一步路线、按需展开表、安全门、常用验证和缓存友好约定。
- 更新 `AGENTS.md`：默认先读 `CORE_CONTEXT_BRIEF.md`，只有完整汇报、执行 Phase、卡壳回归或修改规则/记录时才展开旧的完整上下文文件组。
- 更新 `README.md` 的恢复上下文说明和推荐提问方式，把日常入口从多份大文档改为 `AGENTS.md` + `CORE_CONTEXT_BRIEF.md`。
- 更新 `CAD_AGENT_RULES.md`，新增“上下文缓存友好入口”规则，要求短入口保持稳定，详细历史继续留在计划、changelog 和 issues 中按需读取。
- 更新 `CORE_RESTRUCTURE_PLAN.md` 和 `CAD_AGENT_STATUS.md`，同步短入口与按需展开的恢复策略。

### Git 提交与推送说明

- 在 `README.md` 增加提交与推送说明，记录默认 GitHub 远端、无 `.git` 拷贝目录的初始化流程，以及提交前不纳入本机日志、截图、验证输出和临时 DWG 的规则。
- 更新 `.gitignore`，忽略 `output/*` 生成产物与 `cad_mcp.log`，保留 `output/previews/README.md` 这类目录说明文件的例外。
- 更新 `CAD_AGENT_STATUS.md`，同步这次文档与仓库卫生调整。

### Core 主计划交付协议补强

- 补强 `CORE_RESTRUCTURE_PLAN.md`：新增“执行交付协议”，明确后续 Codex 必须按 phase 执行、每个 phase 先拆 2-5 分钟小步、测试先行、证据落盘和状态同步。
- 新增 Phase O-X 依赖与交付物表，避免后续执行者跳阶段或把未验证能力当作可用能力。
- 将 `CAD_AGENT_AUTONOMOUS_VALIDATION.md` 与 `scripts/run_cad_validation.py` 纳入 Phase O、Phase W 和固定自检流程：非 CAD 阶段可跑 `--no-cad`，真实 CAD 阶段用结构化报告作为总证据。
- 新增本文交付自检清单和文本自查命令，交付前扫描不可执行占位、旧 phase 口径和脚本引用漂移。
- 调整完成判定说明：只讨论计划时不执行 phase；若计划本身改变工作流或交付规则，仍按根目录 `AGENTS.md` 同步状态和变更记录。
- 继续拆细 Phase O-X：每个 phase 增加编号化细化执行清单，覆盖上下文审计、测试先行、红灯确认、最小实现、专项验证、证据归档、文档同步和复核，便于后续 Codex 一次执行较长时间而不丢失阶段边界。
- 新增建议 Agent 分工模式：`context-auditor`、`schema-contract-agent`、`unit-test-agent`、`engine-agent`、`pipeline-agent`、`cad-validation-agent`、`docs-sync-agent`、`review-agent`，明确这些是执行分工建议，不要求新增仓库代码文件。
- 执行 Phase O：为 `core/capabilities/registry.py` 增加能力成熟度 `maturity` 与已知限制 `known_limits`，并用 `tests/core/test_capabilities.py` 锁定 registry 合约。
- 更新 `CORE_STATUS.md` 的状态口径与关键能力限制说明，明确当前 layout、drawing、proposal、verification 仍是 prototype，不能误报为空壳自动设计或几何准确。
- Phase O 验证通过：`tests.core.test_capabilities`、全量 `unittest discover -s tests`、`self_check.py`、validate、dry-run、`render_preview.py --check`、`inspect_dwg.py --no-cad`、非 CAD benchmark 和 `scripts/run_cad_validation.py --no-cad --output-dir output\validation_runs\phase-o-no-cad`。
- 执行 Phase P：新增 `core/drawing_analysis/shell_loader.py`，可将人工空壳 JSON 规范化为 `SHELL_MODEL`，并校验 units、boundary、opening width、fixed obstacles 和 no-place zones。
- 扩展 `core/schemas/shell_model.schema.json` 和 `core/schemas/project_model.schema.json`，让 `SHELL_MODEL` 支持 `boundary.type`、openings、fixed obstacles、no-place zones、required connections、building elements、uncertainties 和 source，让 `PROJECT_MODEL` 可保留 shell_id、source 与 uncertainties。
- 更新 `core/project_model/project_builder.py` 与 `core/capabilities/registry.py`：`project_model.build` 可接收可选 `shell_model`，新增 capability `drawing_analysis.load_shell_model`。
- 新增 `examples/shell_models/retail_blank_shell.json`、`examples/shell_models/office_blank_shell.json` 和 `tests/fixtures/invalid_models/shell_model.opening_missing_width.invalid.json`；`projects/sample_blank_shell/input/shell.manual.json` 已从旧 drawing-style 手工输入升级为 `SHELL_MODEL`。
- Phase P 验证通过：`tests.core.test_shell_loader`、`tests.core.test_project_model`、`tests.core.test_schema_validation`、`tests.core.test_capabilities`、shell example schema validator、全量 `unittest discover -s tests`、非 CAD benchmark 和 `scripts/run_cad_validation.py --no-cad --output-dir output\validation_runs\phase-p-no-cad`。
- 补强 Phase P：`tests/core/test_shell_loader.py` 增加 legacy drawing-style 输入兼容回归，确认旧 `DRAWING_MODEL.spaces` 风格手工标注仍可由 `load_manual_shell()` 规范化为 `SHELL_MODEL`。
- 执行 Phase Q：新增 `core/geometry_backends/rect2d.py` 和 `core/geometry_backends/orthogonal.py`，提供无依赖 rect 操作、bbox no-place-zone 保守扣减、path strip、门洞/障碍距离和正交多边形校验。
- 更新 `core/geometry_backends/registry.py`，登记默认 `rect2d` 与 `orthogonal_polygon` 后端；保留 `cadquery`、`build123d`、`ifcopenshell` 为未来可选槽位，不引入新依赖。
- 迁移 `core/layout_engine/basic_layout.py` 与 `clearance.py` 的 bbox inside / overlap / clearance gap 到 `core.geometry_backends.rect2d`，减少 layout 层散落几何算法。
- Phase Q 目标测试通过：`tests.core.test_geometry_rect2d`、`tests.core.test_geometry_orthogonal`、`tests.core.test_geometry_backends` 与 `tests.core.test_shell_loader`。
- 执行 Phase R：新增 `core/layout_engine/path_generation.py`，实现 `generate_circulation_candidates(project_model, preferences)`，输出 `straight_spine`、`l_spine`、`along_wall` 三类 `CIRCULATION_MODEL` 候选。
- 扩展 `PROJECT_MODEL`：`project_builder` 现在保留 `shell_context.openings`、`fixed_obstacles`、`no_place_zones`、`required_connections` 和 `building_elements`，供后续动线和功能区切分复用。
- 扩展 `core/schemas/circulation_model.schema.json`：路径必须包含 `polyline`、`connects`、`path_surface`、`blocked_reasons` 和 `score`；新增 `examples/circulation_models/retail_straight_spine.json` 与 `retail_l_spine.json`。
- 更新 `core/capabilities/registry.py`，登记 `layout.generate_circulation_candidates`，让动线生成成为可发现、可验证、非 CAD 的 Core capability。
- Phase R 目标测试通过：`tests.core.test_project_model`、`tests.core.test_circulation_generation`、`tests.core.test_schema_validation`、`tests.core.test_capabilities`，并通过 circulation example schema validator。
- 执行 Phase S：新增 `core/layout_engine/zone_splitter.py`，实现 `split_zones(shell_model, circulation_model, constraints)`，可围绕 circulation path surface 切出左右 `FUNCTION_ZONE` 候选。
- 扩展 `core/schemas/function_zone.schema.json`：zone 现在包含 `geometry`、`area`、`depth`、`frontage`、`side_of_path`、`candidate_functions`、`score` 和 `uncertainties`；同步更新 minimal zone example。
- 新增 `examples/function_zones/retail_zone_left.json` 与 `office_zone_desk_band.json`，并扩展 `tests/core/test_zone_splitter.py` 与 `tests/core/test_schema_validation.py`。
- 更新 `core/capabilities/registry.py`，登记 `layout.split_function_zones`，让 shell -> circulation -> function zones 的非 CAD 能力链可发现。
- 修复 `rect2d.subtract_no_place_zones()` 状态语义：不相交的 no-place-zone 不再误报 `partial`，并增加回归测试。
- Phase S 目标测试通过：`tests.core.test_zone_splitter`、`tests.core.test_schema_validation`、`tests.core.test_capabilities`、function zone schema validator。
- 执行 Phase T：新增 `libraries/objects/object_defaults.json`，将对象默认尺寸从代码常量迁出，并扩展 `desk`、`chair`、`bed`、`sofa`、`counter`、`display_unit`。
- 新增 `core/layout_engine/placement.py`，实现由 FUNCTION_ZONE、对象尺寸和 block metadata 驱动的保守 placement，输出 `bbox`、`clearance_bbox`、`source` 和失败原因。
- 扩展 `libraries/blocks/block_library.example.json`，增加 desk、sofa、display_unit 示例块；找不到块时保留 `OBJECT_SPEC` fallback。
- 扩展 `object_spec.schema.json` 与示例：新增 `examples/object_specs/desk_1400x700.json`、`sofa_2200x900.json`。
- 更新 `core/capabilities/registry.py`，登记 `layout.create_zone_placements`，让 function zones -> placements 的非 CAD 能力链可发现。
- Phase T 目标测试通过：`tests.core.test_placement_engine`、`tests.core.test_object_engine`、`tests.core.test_block_engine`、object spec schema validator。
- 执行 Phase U：扩展 `DESIGN_PROPOSAL` schema，支持 `candidates[]`、`confirmed_candidate_id`、`comparison_summary`，并把 evidence 拆为 `from_user`、`from_drawing`、`from_shell`、`from_library`、`from_algorithm`、`inferred`。
- 更新 `design_proposal.py`，可将多个 layout candidates 包装为多候选 proposal；更新 `proposal_to_plan.py` 与 `plan_engine/model_to_plan.py`，支持按 `confirmed_candidate_id` 选择要转 CAD_PLAN 的候选。
- 更新 `proposal_comparison.py`，支持带 `weight_source` 的场景权重参与候选排序，防止偏好权重变成隐式常量。
- 新增 `examples/design_proposals/blank_shell_retail_options.json` 和 `tests/core/test_proposal_multi_candidate.py`。
- Phase U 目标测试通过：`tests.core.test_proposal_multi_candidate`、`tests.core.test_proposal_engine`、`tests.core.test_proposal_comparison`、design proposal schema validator。
- 执行 Phase V：新增 `core/workflows/blank_shell_pipeline.py` 与 `scripts/run_blank_shell_pipeline.py`，串联 `SHELL_MODEL -> PROJECT_MODEL -> CIRCULATION_MODEL -> FUNCTION_ZONE -> placements -> LAYOUT_PROPOSAL -> DESIGN_PROPOSAL -> CAD_PLAN -> dry-run -> VERIFICATION_REPORT(unverified)`。
- 新增 `examples/workflows/blank_shell_layout_loop.json`、`blank_shell_office_layout_loop.json`、`blank_shell_residential_layout_loop.json`、`blank_shell_restaurant_layout_loop.json`，以及 `examples/benchmarks/blank_shell_core_benchmark.json`。
- 新增 `examples/shell_models/office_small_suite_shell.json`、`residential_living_room_shell.json`、`restaurant_small_front_shell.json` 和 `agents/restaurant/preferences.json`，让 blank-shell benchmark 覆盖四个不同 workflow，而不是同一输入重复运行。
- 新增 `projects/sample_blank_shell/expected/expected_notes.md`，明确空壳 pipeline 的非 CAD 预期和 `unverified` 证据边界。
- 更新 `core/benchmarks/runner.py`，让 benchmark runner 可调度 `pipeline: blank_shell` case，并记录 candidates、zones、placements、CAD_PLAN、失败检查、dry-run 和 verification 指标。
- 更新 `core/capabilities/registry.py`，登记 `workflow.blank_shell_pipeline`，让完整空壳 pipeline 成为可发现、可运行、可验证的 Core capability。
- 大范围审计修复：blank-shell pipeline 现在从 placement 实际来源派生 `OBJECT_SPEC`，避免 block 尺寸与 CAD_PLAN 默认对象尺寸不一致；`path_to_rect_strips()` 跳过重复连续点；zone placement 在剩余空间不足时返回 blocked placement 而不是异常。
- 更新测试：新增/扩展 `tests/core/test_blank_shell_pipeline.py`、`tests/core/test_benchmarks.py`、`tests/core/test_benchmark_cli.py`、`tests/core/test_geometry_rect2d.py`、`tests/core/test_placement_engine.py`、`tests/core/test_capabilities.py` 与 `tests/agents/test_scene_preferences.py`。
- Phase V 目标测试通过：`tests.core.test_blank_shell_pipeline`、`tests.core.test_benchmarks`、`tests.core.test_benchmark_cli`、`tests.core.test_capabilities`、`tests.agents.test_scene_preferences`；当前全量测试数量以本日“系统层安全重构收尾”记录为准。

### CAD 自主验证闭环

- 新增 `CAD_AGENT_AUTONOMOUS_VALIDATION.md`，把“不要遇到第一处失败就停”的口头要求固化为可复用执行手册。
- 新增 `core/verification/cad_validation_runner.py` 和 `scripts/run_cad_validation.py`，提供一键 CAD 验证总控：依赖探针、自检、单元测试、validate、dry-run、截图能力、benchmark、AutoCAD COM 连接、预览落图、截图和实体回读。
- 验证脚本会写入 `output/validation_runs/<timestamp>/report.json`、`report.md`、各步骤 stdout/stderr、`execution_summary.json`、`readback_report.json` 和截图路径。
- 新增失败分类：`missing_dependency`、`cad_connection_failed`、`repo_regression`、`cad_plan_invalid`、`dry_run_failed`、`execution_failed`、`screenshot_failed`、`readback_failed`，让 Codex 能区分仓库内可修问题和用户侧外部阻塞。
- 新增 `tests/core/test_cad_validation_runner.py`，覆盖 CAD 连接失败归类为 `external_blocker`，以及全部步骤成功时输出 `pass`。
- 在 `CAD_AGENT_RULES.md` 增加“CAD 层面验证要走自主验证闭环”，要求 Codex 对仓库内问题自行最小复现、最小修复并复验。
- 更新 `CAD_AGENT_STATUS.md`，把回家或换机验证入口调整为 `CAD_AGENT_AUTONOMOUS_VALIDATION.md` + `scripts/run_cad_validation.py`。

### 外部方法论内化为 Core runtime

- 不复制外部项目代码，只抽象其工程思路，新增 `core/capabilities/registry.py`：能力可发现、输入先校验、输出 contract、风险等级、CAD 依赖和验证命令登记。
- 新增 `core/workflows/artifact_graph.py`，把 workflow artifacts 转成依赖顺序、路径检查和循环依赖检测。
- 新增 `core/geometry_backends/registry.py`，默认使用无依赖 `cad_plan_rect2d`；将 `cadquery`、`build123d`、`ifcopenshell` 仅登记为未来可选后端槽位，不成为当前依赖。
- 新增 `core/benchmarks/runner.py`、`scripts/run_benchmark_suite.py` 和 `examples/benchmarks/non_cad_core_benchmark.json`，让非 CAD pipeline 具备可重复 benchmark 基线。
- 新增 `core/object_engine/object_explainer.py` 和 `core/proposal_engine/proposal_comparison.py`，补齐对象尺寸/构件来源说明和多候选 layout 比较。
- 补齐 `tests/fixtures/invalid_models/`，让每个注册模型至少有一个 invalid fixture。
- 扩展 `examples/project_models/` 到 generic、retail、residential、office 多场景；扩展 `libraries/blocks/block_library.example.json` 到更多通用块类别。
- 新增 `docs/verification/` 与 CAD 延后补验模板，继续明确非 CAD 结果不能替代真实 CAD 落图、截图和实体回读。
- 单元测试扩展到 109 项；新增 capability、artifact graph、geometry backend、benchmark、object explanation、proposal comparison、shell/circulation/function-zone schema、schema invalid fixture、multi-domain project model、scene preference diff 和 block library 覆盖。

### 非 CAD 全量底座闭环深化

- 根据多个并行 Agent 对 plan、schema、engine、verification、safety 和 pipeline 的审计结果，继续推进第二轮非 CAD 底座开发。
- 新增 `core/safety/policy.py`，并接入 `core/execution/execute_plan.py`；默认只允许 `CODEX_PREVIEW`，正式图层、删除、保存、覆盖和未确认计划必须有显式批准。
- 新增 `core/project_model/project_builder.py`、`core/model_loop/reference_checker.py`、`core/schemas/registry.py`，补齐项目模型构建、workflow schema 校验和跨模型引用检查。
- 新增 `core/drawing_analysis/manual_model.py`、`entity_summary.py`，支持 CAD 不可用时通过手工 JSON 或简化实体列表继续推进图纸理解。
- 新增 `core/block_engine/block_selector.py`、`block_placement.py`，支持块库元数据筛选、fallback object spec 和 block insertion intent。
- 扩展 `core/layout_engine/`：增加 collision、clearance、scoring 和多对象 candidates。
- 拆分 `core/object_engine/object_to_plan.py` 与 `core/proposal_engine/proposal_to_plan.py`，让对象/方案生成与 `CAD_PLAN` 转换分离。
- 新增 `core/plan_engine/model_to_plan.py`、`dry_run_report.py`，支持高层模型到安全预览计划和机器可读 dry-run report。
- 新增 `core/workflows/non_cad_pipeline.py` 与 `scripts/run_non_cad_pipeline.py`，输出 `PROJECT_MODEL`、`OBJECT_SPEC`、`LAYOUT_PROPOSAL`、`DESIGN_PROPOSAL`、`CAD_PLAN`、dry-run report 和 `VERIFICATION_REPORT(unverified)`。
- 强化验证证据门：裸 `entities_are_scoped=True` 不再足以升级为 `geometry_verified`；必须有 created handles 覆盖；截图路径不存在时不算截图证据。
- 为 `commercial_fitout`、`residential`、`office` 增加 `preferences.json`，并在 pipeline 中接入场景偏好。
- 新增 `tests/core/test_style_engine.py`，让 modern / european / minimal style token 对对象构件差异形成回归约束。
- 扩展 cabinet/shelf/table 的基础组件表达，并为 schema 职责边界增加测试：`DESIGN_BRIEF` 不承载落图图层，`CAD_PLAN` 不承载方案推理 evidence。
- 扩展 `DESIGN_PROPOSAL.evidence`，加入 `from_library` 来源字段。
- 新增 `core/layout_engine/circulation.py`，让场景 preferences 中的 `main_aisle_width_mm` 进入 Core layout circulation check。
- 新增 `projects/sample_blank_shell/input/shell.manual.json`，作为非 CAD 空壳布局底座的手工输入样例。
- 扩展 `core/verification/verification_report.py`，增加 before/after snapshot diff、批量 report 汇总和失败修复建议字段。
- 扩展测试到 89 项；当前非 CAD 基线为 `unittest discover -s tests` 通过、`self_check.py` pass、`render_preview.py --check` ready、非 CAD pipeline status ok。

### 第二轮 Core 大规模重装

- 将 `CORE_RESTRUCTURE_PLAN.md` 从剩余工作概览扩展为非 CAD 全量底座开发计划，新增 Phase A-M、待校验登记表、每阶段非 CAD 验证命令和 CAD 延后补验总清单。
- 收束 `cad_agent/`：三份旧文档已标注为 legacy，新增 `docs/architecture/cad_workflow.md` 和 `docs/architecture/cad_plan_boundary.md` 作为 Core 架构入口。
- 收束 `libraries/domains/`：新建 `libraries/domain_presets/` 并复制 domain preset；旧目录保留 legacy README 作为兼容入口。
- 新增 9 个高层 schema 与最小 example：`DESIGN_BRIEF`、`DRAWING_MODEL`、`PROJECT_MODEL`、`OBJECT_SPEC`、`STYLE_PROFILE`、`BLOCK_LIBRARY`、`LAYOUT_PROPOSAL`、`DESIGN_PROPOSAL`、`VERIFICATION_REPORT`。
- 新增 `core/schemas/validator.py`，提供无外部依赖的 schema example 校验入口。
- 新增 `core/verification/verification_report.py`，并增强 `core/verification/inspect_dwg.py`：默认不连接 CAD，显式 `--connect-cad` 才读取真实 AutoCAD；支持 `--plan`、`--format json`、`--no-cad`。
- 为 `core/cad_io/autocad_com.py` 增加 `snapshot_modelspace()` 只读实体快照入口。
- 新增第一批设计引擎原型：`core/object_engine/parametric_objects.py`、`core/style_engine/style_profile.py`、`core/block_engine/block_library.py`、`core/layout_engine/basic_layout.py`、`core/proposal_engine/design_proposal.py`。
- 新增 `libraries/styles/modern.json`、`european.json`、`minimal.json` 和 `libraries/blocks/block_library.example.json`。
- 新增 `agents/SCENE_AGENT_RULES.md` 和 `agents/commercial_fitout/workflows/blank_store_to_layout.md`、`existing_plan_to_elevation.md`，明确场景 Agent 只存偏好和 workflow，不复制 Core 算法。
- 新增/扩展测试：高层 schema 校验、对象/风格/块/布局/方案原型、验证报告、场景 Agent 边界；第一批单测从 13 项扩展到 35 项，随后非 CAD 底座深化扩展到 89 项。
- 修复测试环境问题：将需要写文件的测试改用 `output/test_artifacts`，避免当前沙箱无法删除系统临时目录导致失败。
- 根据复盘 Agent 审查补强验证与确认门：`VERIFICATION_REPORT` 失败优先、校验基点、按目标图层统计文字/标注、未隔离本次执行实体时不声称 `geometry_verified`；`DESIGN_PROPOSAL.needs_confirmation=true` 时不得转 `CAD_PLAN`；`CAD_PLAN.needs_confirmation=true` 时执行层默认拒绝执行。
- 增强场景 Agent 边界测试：扫描 `agents/` Python 文件，禁止在场景层实现 CAD 执行、回读或校验核心能力。
- 记录 CAD 不可稳定打开时的验证策略：非 CAD 层按单测、schema、dry-run、自检和 fake readback 完整验证；真实 CAD 落图、实体回读和截图补验写入 `CORE_RESTRUCTURE_PLAN.md` 延后清单。

### 默认中文沟通规则

- 将根目录 `AGENTS.md` 从英文规则改为中文规则，并新增“默认中文输出”要求。
- 将 `skills/cad-drawing/SKILL.md` 改为中文说明，并要求面向用户的解释、状态汇报、方案讨论、追问和结论默认使用中文。
- 在 `CAD_AGENT_RULES.md` 增加“默认中文沟通”规则，明确代码、命令、路径、Schema 字段、JSON key、工具名和 API 名称可保留英文或原文。
- 更新 `CAD_AGENT_STATUS.md` 和 `CAD_AGENT_ISSUES.md`，记录这次由用户反馈触发的语言策略修正。

### 空壳布局底座设计沉淀

- 新增根目录 `SHELL_LAYOUT_FOUNDATION_DESIGN.md`。
- 将“空壳 CAD / 空户型 -> 空壳模型 -> 项目约束 -> 动线 -> 功能区 -> 对象/图块 -> 布局方案 -> CAD_PLAN -> 预览和验证”的通用 Core 子能力路线沉淀为设计说明。
- 明确该能力属于 Core 子能力组合，不是公司专用平面方案 Agent。
- 明确第一版允许人工标注空壳输入，不要求一次性自动识别任意 DWG。
- 明确 Core 与 `agents/`、`libraries/`、`projects/` 的边界，避免后续实现跑偏。
- 补充数据模型建议、模块职责、分阶段路线、执行自检链路、验收标准和风险规则。
- 更新 `CAD_AGENT_STATUS.md`，说明该文档是后续开发蓝图，不代表功能已实现。

### 架构重装设计

- 新增根目录 `CORE_RESTRUCTURE_PLAN.md`，作为下一轮大规模仓库重装前的设计草案。
- 明确未来仓库定位从“单一 CAD 绘图流程”升级为“通用 CAD Agent Core Lab”。
- 明确开发重心：通用底座优先，场景 Agent 轻量化。
- 明确 `core/`、`agents/`、`libraries/`、`projects/`、`docs/`、`tests/` 的目标职责。
- 明确未来 Core 能力模块：CAD IO、图纸理解、项目模型、对象引擎、风格引擎、图库块引擎、布局引擎、方案引擎、计划引擎、执行、验证和安全。
- 暂停沿旧路线继续堆叠阶段 5 之前，先等待用户确认是否执行仓库重装。

### 第一轮仓库重装

- 新增 `CORE_STATUS.md` 和 `CORE_ROADMAP.md`，用能力矩阵和 Core 阶段路线追踪通用底座进度。
- 创建目标结构：`core/`、`agents/`、`projects/`、`docs/architecture`、`docs/decisions`、`docs/roadmap`、`tests/core`、`tests/agents`、`tests/fixtures`。
- 将现有核心实现迁入 Core：
  - `core/plan_engine/validate_plan.py`
  - `core/plan_engine/dry_run_plan.py`
  - `core/execution/execute_plan.py`
  - `core/verification/inspect_dwg.py`
  - `core/verification/render_preview.py`
  - `core/verification/self_check.py`
  - `core/cad_io/autocad_com.py`
  - `core/cad_io/dxf_writer.py`
  - `core/cad_io/zwcad_com.py`
- 保留旧入口兼容：
  - `scripts/*.py` 作为 Core CLI 薄包装器。
  - `drivers/*.py` 作为 `core.cad_io` 薄包装器。
  - `schemas/*.json` 与 `core/schemas/*.json` 过渡期保持一致。
- 新增轻量场景 Agent 脚手架：`commercial_fitout`、`residential`、`office`、`restaurant`、`exhibition`、`custom`。
- 将核心测试迁入 `tests/core/`，并新增 `tests/core/test_core_restructure.py`，覆盖旧入口兼容、新 Core 入口、schema 一致性和 Agent manifest。
- 更新 `README.md`、`AGENTS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_RULES.md`、`docs/ROADMAP.md`，让入口文档与 Core Lab 架构一致。
- 修剪 `CORE_RESTRUCTURE_PLAN.md`：删除已经完成的第一轮重装待办，保留遗留目录收束、高层 schema、实体回读、对象/风格、图库块、布局、图纸理解、项目模型和方案引擎等剩余计划。

### 阶段 4：预览绘制最小闭环

- 新增 `tests/test_execute_plan.py`，用记录型 driver 验证执行器会请求绘制测试柜矩形、文字和两条基础尺寸标注。
- 将 `scripts/execute_plan.py` 从脚手架推进为第一版真实执行核心：
  - 读取 CAD_PLAN。
  - 复用 `validate_plan.py` 校验。
  - 仅支持当前安全范围内的 `draw_object` + `absolute` placement。
  - 默认只允许 `CODEX_PREVIEW` 图层。
  - 计算矩形、中心文字和水平/竖向尺寸标注位置。
  - 通过 driver 接口调用绘制层。
- 将 `drivers/autocad_com.py` 从占位推进为第一版 AutoCAD COM 驱动：
  - 可连接当前 AutoCAD 应用。
  - 可确保图层存在。
  - 可绘制矩形四边、文字和对齐尺寸标注。
- 使用 CAD-MCP 在当前打开的 CAD 文件中完成实际预览绘制：
  - 绘制 1800 x 600 测试柜矩形。
  - 添加中心文字 `测试柜`。
  - 添加水平和竖向基础尺寸标注。
  - 全部绘制到 `CODEX_PREVIEW` 图层。

### 验证

- `validate_plan.py` 对 `examples/plans/draw_test_cabinet.json` 返回 `VALID CAD_PLAN`。
- `dry_run_plan.py` 能正确预演测试柜对象、尺寸、位置、图层、文字和尺寸开关。
- `tests/test_execute_plan.py` 通过。
- CAD-MCP 绘图调用返回 AutoCAD COM 对象，说明实体已写入当前打开的 CAD 文档。

### 卡壳自查机制

- 新增 `CAD_AGENT_BLOCKER_PLAYBOOK.md`，沉淀“画不准、画不出来、验证不了”时的自查、复现、截图、修复和记录流程。
- 在 `CAD_AGENT_RULES.md` 增加“卡壳时先自查，不盲目重试”规则。
- 在 `README.md` 增加卡壳恢复入口和自检命令。
- 更新 `CAD_AGENT_STATUS.md`，记录横向自查机制。

### 自检与截图入口

- 新增 `scripts/self_check.py`，用于检查核心文件、示例 CAD_PLAN、预览执行路径和截图工具链。
- 扩展 `scripts/render_preview.py`，支持 `--check` 检查截图能力，支持 `--capture-screen` 保存当前可见屏幕截图。
- 新增 `tests/test_render_preview.py`。
- 新增 `tests/test_self_check.py`。

### AGENTS 规则入口

- 新增根目录 `AGENTS.md`，用短规则触发 CAD Agent 上下文读取和绘图自检门。
- 历史阶段曾新增 `CAD测试相关文件/AGENTS.md`，在 CAD 开发包内部固化恢复入口、绘图准确性验收门、卡壳自查流程和原图保护规则；当前现行入口已迁移为仓库根目录 `AGENTS.md` + Core 文档结构。

### 补充原因

- 用户希望未来任意阶段卡壳时，Codex 能先自己找原因，而不是反复试错或把问题直接丢回用户。
- 阶段 4 和后续绘图能力都需要视觉证据；原有目录只有截图输出占位和脚手架，没有可运行的截图检查/自检入口。
- 用户希望这些规则被放入可被 Codex 自动读取的 `AGENTS.md`，避免未来只靠聊天记忆执行。

### 补充验证

- 已确认 CAD-MCP 虚拟环境具备 `PIL`、`win32gui`、`win32com`。
- 新增测试先失败，随后通过实现修复。

## 2026-05-24

### 通用化调整

- 将 `README.md` 定位从当前测试目录调整为“通用 CAD Agent 开发包”。
- 明确本文件夹不绑定当前家装图纸、不绑定当前电脑。
- 明确完整能力由“本文件夹 + 运行环境 + 项目图纸”共同组成。
- 将 `CAD_AGENT_STATUS.md` 当前阶段更新为“阶段 3：CAD_PLAN 校验和 dry-run 已跑通，下一步进入预览绘制”。
- 在 `CAD_AGENT_RULES.md` 增加“通用开发包定位”。
- 扩展 domain 枚举，支持 `exhibition`、`hotel`、`education`、`healthcare`、`industrial`、`custom`。
- 增加办公、餐饮、展厅、酒店、教育、医疗、工业、通用自定义行业包占位。
- 统一 `README.md` 的恢复入口说明：先看 README，再看 4 个项目管理文件。

### 通用化原因

- 用户确认最终目标是可迁移的通用 CAD Agent 开发包。
- 该文件夹未来应能复制到其他电脑和其他 CAD 项目中复用。
- 具体家装图纸只是第一套测试现场，不应污染通用规则。

### 新增

- 创建 `CAD测试相关文件/README.md`，作为测试工作区入口。
- 创建 `CAD_AGENT_STATUS.md`，记录当前开发阶段。
- 创建 `CAD_AGENT_RULES.md`，记录长期规则。
- 创建 `CAD_AGENT_CHANGELOG.md`，记录变更历史。
- 创建 `CAD_AGENT_ISSUES.md`，记录错误和修复。
- 创建 `CAD_AGENT_DECISIONS.md`，记录关键决策和原因。
- 创建第一版目录框架：`cad_agent/`、`skills/`、`schemas/`、`examples/`、`scripts/`、`drivers/`、`libraries/`、`tests/`、`output/`。
- 创建第一版 `CAD_PLAN` Schema 和测试柜示例。
- 创建 `cad-drawing` Skill 骨架。
- 创建 `scripts/validate_plan.py`，用于校验第一版 CAD_PLAN。
- 创建 `scripts/dry_run_plan.py`，用于预演 CAD_PLAN。

### 调整

- 将旧的 `CAD_AGENT_BUILD_GUIDE.md`、`CODEX_CAD_DEV_LOG.md`、`CODEX_CAD_RULES.md` 移动到 `docs/archive/`。

### 决策

- 当前先不创建根目录 `AGENTS.md`，避免过早影响所有 Codex 行为。
- 当前先不引入 SQL。
- 当前先不做完整自动设计。
- 当前先以 `CAD_PLAN` 作为白话和 CAD 绘制之间的中间层。

### 原因

- 用户希望隔几天回来仍能知道开发进度。
- 用户希望规则能随着需求、测试、错误不断迭代。
- 用户希望整个根目录作为 CAD 测试方向，但 CAD 相关资料不要散落在根目录。

### 验证

- 使用 CAD-MCP 虚拟环境 Python 成功运行 `validate_plan.py`。
- 使用 CAD-MCP 虚拟环境 Python 成功运行 `dry_run_plan.py`。
- 发现全局 `python` 命令不可用，已记录到 `CAD_AGENT_ISSUES.md`。
- 发现中文终端输出需要显式 UTF-8，已记录到 `CAD_AGENT_ISSUES.md`。
## 2026-06-02

### CAD-SEMANTIC-ASSET-REUSE-UPGRADE-01：语义规则库 + 资产复用 + 线型表审计底座

- **触发**：用户要求把线型表、语义规则库、跨 DWG 复用和系统资产沉淀作为大型系统升级推进，并通过多个 Agent 查漏、阶段把控和最终验收。
- **OpenSpec**：新增 `openspec/changes/cad-semantic-asset-reuse-upgrade/`，覆盖 semantic rules、system asset reuse hardening、line-type table audit 和 variable row support。
- **实现**：新增 `core/assets/semantic_rules.py`，记录资产沉淀、线型表、资产复用、局部修复的触发、路由、门禁和证据边界；`core/assets/system_asset_reuse.py` 在匹配前运行 registry 编码预检，报告 `semanticRules`，并用 lifecycle / native / source readiness 做稳定候选排序。
- **主调度**：新增 `core/orchestrator/semantic_asset_route.py` 并接入 `orchestrate_request`，让主系统在普通 workflow dispatch 旁边记录 `semantic_asset_route`，证明“先判断资产复用，再回落普通 CAD_PLAN / workflow”。
- **线型表**：新增 `core/training/linetype_table_audit.py`；`draw_linetype_table(..., rows=...)` 支持可变行数，报告新增 `layoutAudit`，审计 canonical 中文、无填充、样线格 containment、自适应行高、样式差异和截图证据边界。
- **验证**：`tests.core.test_semantic_asset_rules tests.core.test_workflow_dispatch tests.core.test_system_asset_reuse tests.core.test_system_asset_sedimentation tests.core.test_linetype_table_demo tests.core.test_script_bootstrap` 相关回归通过；CLI plan-only 报告 `output/validation_runs/system-assets/semantic-upgrade/reuse_workflow_plan.json`；fake CAD 审计报告 `output/validation_runs/linetype-table/semantic-upgrade/linetype_table_report.json`。
- **边界**：本轮不保存当前业务 DWG，不提升表 C；线型表 fake CAD 审计证明 Core 生成和 readback 约束，真实 CAD 打印 / CTB / STB 仍需专项证据。

### VISUAL-CAD-ASSET-RETRIEVAL-01：当前 DWG 视觉优先图块检索 V0

- **触发**：用户指出“语义 + 截图找沙发块”不应长期依赖全量线弧构造扫描，未来大图库必须先做视觉判断和快速召回。
- **OpenSpec**：新增 `openspec/changes/visual-first-cad-asset-retrieval/`，包含 proposal / design / specs / tasks；新 capability 为 `visual-cad-asset-retrieval`。
- **实现**：新增 `core/visual_retrieval/` 和 `scripts/run_visual_block_retrieval.py`。V0 从查询文本/视觉提示生成 `VisualQueryProfile`，按 bbox 宽高比、家具尺度、来源图层、语义词和可选 block definition 摘要给当前 DWG 块参照排序。
- **自测**：新增 `tests/core/test_visual_cad_asset_retrieval.py`，3 tests OK。真实 CAD 模拟命令 `根据截图找到三人沙发对应图块` 命中 `handle=4A2`、`block_name=5S03232`；报告 `output/validation_runs/visual-cad-asset-retrieval/sofa_query_report.json` 和复跑 `output/validation_runs/visual-cad-asset-retrieval/sofa_query_report_rerun.json`，端到端样本为 `4.165127s` / `3.682856s`，复跑排序阶段 `0.000167s`。
- **边界**：只读检索；不保存 DWG、不删除实体、不写正式图层。视觉相似度只用于候选召回，不证明真实 CAD 尺寸；本轮不提升表 C，不完成跨文件图库 embedding。

### SOFA-DIMENSION-ANNOTATION-01：截图找沙发并标注尺寸

- **触发**：用户给出沙发截图并要求“找到这个沙发，进行尺寸标注”。
- **实现**：新增 `core/visual_retrieval/dimension_annotation.py` 与 `scripts/run_sofa_dimension_annotation.py`；`AutoCADComDriver.add_dimension` 支持 `text_override`，fake driver 同步覆盖回读。
- **真实 CAD**：先 dry-run 生成结构化标注意图，再在 `CODEX_PREVIEW` 写入两条 aligned dimension。目标块 `4A2 / 5S03232`，bbox 尺寸 `2800 x 960`；新建标注 handles `2D8A`、`2DE0`，回读 layer=`CODEX_PREVIEW`、text=`2800` / `960`。
- **证据**：报告 `output/validation_runs/visual-cad-asset-retrieval/sofa_dimension_annotation_report.json`；截图 `output/previews/sofa_dimension_annotation.png`；测试 `tests.core.test_visual_dimension_annotation` + `tests.core.test_visual_cad_asset_retrieval` 共 5 OK。
- **边界**：不修改目标沙发块、不保存 DWG、不删除实体、不改正式图层；尺寸证明来自 active DWG bbox 与新建标注 readback，截图仅用于目标识别。

### QUICK-COMPOSITE-CACHE-01：通用轻型复合任务 + 当前 DWG 缓存

- **触发**：用户确认采用方案 B，希望“找图块 + 标注”这类轻型复合任务随着沉淀变快，且升级必须通用、不能只服务单一沙发案例。
- **OpenSpec**：新增 `openspec/changes/quick-composite-cad-task-cache/`，约束范围为当前 DWG 快路径、缓存候选源、通用 bbox 标注动作和 preview-only 安全。
- **实现**：新增 `core/visual_retrieval/current_dwg_cache.py`、`core/quick_tasks/find_and_annotate.py`、`scripts/run_quick_composite_task.py`；`find_and_annotate_bbox_dimensions` 可对任意带 bbox 的 block candidate 生成宽/深标注动作。
- **自测**：新增 `tests/core/test_current_dwg_block_cache.py` 与 `tests/core/test_quick_composite_task.py`；相关 9 tests OK。真实 CAD dry-run 第一次 `candidate_source=live_snapshot`、内部 `1.084232s`；第二次 `candidate_source=cache`、内部 `0.002923s`，目标仍为 `4A2 / 5S03232`。
- **边界**：本轮不做跨文件图库、thumbnail、embedding；缓存只用于当前 DWG 轻量候选召回，执行证据仍看 active CAD readback；第二次真实 CAD 自测用 dry-run，未重复写入新标注。
## 2026-06-02

### DESIGNER-VIEW-NEARBY-HARDENING-02：旁边语义真实中文解析与多焦点保护
- **触发**：继续加固“旁边 / 附近”的设计师视角理解，避免真实中文方向词、生活化语气词和多焦点视口造成误落图。
- **实现**：`core/placement/designer_view_nearby.py` 新增 `phrase_analysis`，识别左边、右边、上方、下方、附近、旁边等真实中文 / 英文邻近词；上下方向只认明确短语，避免把“试一下 / 看一下”里的“下”误判为下方。
- **加固**：没有 selected / recent handles 且当前视口存在多个分离、评分接近的可见焦点时，返回 `needs_confirmation` 和 `anchor_candidates`，不再把全视口所有对象合并成一个大锚点。
- **Prompt**：`agents/cad_designer/prompt_addendum.md` 和 `agents/cad_designer/rules.md` 已写入内置 Agent 的旁边理解规则。
- **边界**：本加固提高的是当前视口邻近放置理解力，不证明对象族掌握、施工图准确、表 C 提升或用户审美验收。
## 2026-06-02

### LINETYPE-TABLE-DEMO-UTF8-STREAM-01：线型表中文编码与流式演示根修

- 新增 `core/training/linetype_table_demo.py`，把 26 行中文线型表、可见文本门禁、created handles 精确回读、流式 recorder 事件和报告生成封成可复用入口。
- 新增 `scripts/draw_linetype_table.py`，后续线型表演示默认从 UTF-8 模块 payload 执行，不再把中文绘图脚本经 PowerShell 管道传给 Python；脚本默认启用逐行流式演示。
- 新增 `tests/core/test_linetype_table_demo.py`，覆盖乱码问号检测、中文回读无英文字母、26 行流式 `item_complete` 事件、脚本入口 fake CAD 执行。
- 验证：`python -m unittest tests.core.test_linetype_table_demo` 通过；`scripts/draw_linetype_table.py --fake-cad` 通过并生成 `output/validation_runs/linetype-table/cli-fake/linetype_table_report.json`。
- 边界：本包是绘图工作流根修，不提升表 C，不保存 DWG，不修改正式图层。

## 2026-06-03

### DIMENSION-STYLE-FOCUSED-10-01：十个中文尺寸样式真实 CAD 训练

- **触发**：用户要求尺寸样式加强训练，直接在已打开 AutoCAD 中创建 10 个符合市场规范的中文尺寸标注样式，训练后再决定是否沉淀资产。
- **实现**：新增 `core/training/dimension_style_training.py` 和 `scripts/run_dimension_style_training.py`，包含 10 个中文尺寸样式、中文编码预检、`CODEX_CN_TEXT` 文本样式、DimStyle 变量写入 / 回读、样例面板落图、created handles 审计和 focused scope 报告。
- **排障**：根因是 Codex 命令线程位于 `CodexSandboxDesktop...`，AutoCAD 在用户可见的 `Default` 桌面；训练入口和截图入口均新增 input desktop 切换。另修复 `AcDb2LineAngularDimension` 被误分类为普通线的问题，审计现在要求期望尺寸句柄必须回读为 `dimension`。
- **真实 CAD 证据**：在 `Drawing2.dwg` 的 `CODEX_PREVIEW` 创建 143 个对象，19 个尺寸实体回读，10/10 样式审计通过，报告 `output/training_queues/dimension-style-focused-10/real-cad/dimension_style_training_report.json`，截图 `output/previews/dimension-style-focused-10-real.png`。
- **验证**：`tests.core.test_dimension_style_training tests.core.test_verification_report` 共 19 OK；`tests.core.test_render_preview` 共 9 OK；真实报告 `encodingPreflight=pass`、`savedCurrentDwg=false`、`assetSedimentation=not_started`。
- **边界**：本轮不保存当前业务 DWG，不删除实体，不覆盖已有 `Standard`，不沉淀资产；后续沉淀需要走系统资产四件套。

### DATA-BLOAT-A0-A3-IMPLEMENTATION-01：训练前防膨胀 A0-A3 实施

- **触发**：前一轮已把数据防膨胀写进规则和 A-to-A 共识，但没有真正的审计 CLI、compact 快照和 retention manifest。
- **实现**：新增 `core/maintenance/data_bloat_audit.py` 和 `scripts/run_data_bloat_audit.py`，只读输出 `protected` / `derived` / `candidate` / `blocked`；active fact_source 缺失、派生快照误登记 fact_source、coverage `report_path_missing` 会 hard block。`capability-map-data.js` 生成器改为 compact 单行并去掉重复 legacy aliases；HTML 新增 `normalizeWorkbenchData()` 兼容旧快照。retention 扫描根扩到 debug / test artifacts，引用根扩到 handoffs、projects、validation runs、system library，`.json` / `.dwg` / `.dwt` 显式保护，写归档时生成 relocation manifest 与 SHA256。
- **验证**：A0 / A3 单测 8 OK；A1 新增 compact / normalize 测试和 A3 全套 retention 测试 7 OK；`python scripts\build_capability_map_data.py` 成功，真实快照为 1,361,055 bytes / 1 行；`node --check capability-map-data.js` pass；retention dry-run pass，`candidateCount=0`、`protectedArtifactCount=16`、未归档；`run_data_bloat_audit.py --summary-only` 返回 blocked，快照 ratchet 无 warning。
- **当前阻断**：`scripts\sync_training_workbench.py` 仍 fail，Agent check 仅 `training_source_paths_exist` 失败：13 个 active fact_source 缺失；coverage `evidence_path_audit.report_path_missing=303`。这符合 A0 设计，不能把页面健康显示当成证据链闭合。
- **边界**：本包不删除、不移动、不归档真实仓库文件；不连接 AutoCAD、不写 DWG、不提升表 C。

### DIMENSION-STYLE-ARCH-SCALE-RETRAIN-01：建筑尺寸样式比例重训

- **触发**：用户指出上一版虽有建筑标注形态，但样式仍可能重复，且建筑标记比例偏大；要求删除失败测试结果、重画，并由独立 Agent 校验。
- **方案**：经规范评审 Agent 和训练架构 Agent 讨论，第一轮不扩成 20/30 个名称，而是保留 10 个 canonical 样式，并为每个样式追加 3 个比例 / 跨度样例，训练底座学习“样式家族 + 比例语感”。
- **实现**：`dimension_style_training.py` 新增 `scaleSamples`、比例样例绘制与审计字段；建筑 tick 类 `DIMASZ` 从 2.4–2.8 收敛到 1.2–1.7；审计新增 `scaleVariantCount`，并规避 fake driver 缺少 `DIMBLK` readback 的误判。
- **真实 CAD 证据**：用上一轮失败报告限定删除 `CODEX_PREVIEW` handles 153/153，重画 `createdHandleCount=304`；报告 `status=pass`、`canonicalStyleCount=10`、`scaleVariantCount=30`、`dimensionReadbackCount=49`、`audit.failedStyleCount=0`、`duplicateStyleFingerprints=0`、`savedCurrentDwg=false`。
- **截图 / Agent 校验**：截图 `output/previews/dimension-style-focused-10-architectural-scale-retrain.png`；独立校验 Agent 判定 `pass`，认为 10 个面板已不是重复凑数，建筑 tick 比例更接近常见施工图，可交给用户人工验收。
- **用户复核修复**：用户指出 06 标高符号比例样例越框；已把 level marker 右侧比例样例改为紧凑三行标高符号 + 短竖向高度验证，并新增面板级 `panelHandlesByStyle` / `panelBoundsByStyle` / `panel_containment` 审计。旧 304 handles 清理后重画 `createdHandleCount=322`，06 面板 `panelReadbackCount=63`、`failures=[]`，修复截图 `output/previews/dimension-style-focused-10-level-marker-containment-repair.png`。
- **分类纠偏 / r3**：用户继续指出 06 视觉不常规，设计师 Agent 与训练架构 Agent 均判定标高符号应归为 `annotation_symbol_style.level_marker`，不应计入 dimension style。已用真实 AutoCAD dimension entity 的“室内-洞口宽高尺寸”替换 06，同时修复 04 局部尺寸文字粘连、05/06 右侧比例样例过度拥挤；r3 真实 CAD 清理 301 handles 后重画 `createdHandleCount=328`，`dimensionReadbackCount=44`，`audit.failedStyleCount=0`，`savedCurrentDwg=false`，报告 `output/training_queues/dimension-style-focused-10/real-cad-opening-dimension-rework-r3/dimension_style_training_report.json`，截图 `output/previews/dimension-style-focused-10-opening-dimension-rework-r3.png`。
- **边界**：本轮仍是 focused retraining，不保存当前业务 DWG、不沉淀资产、不提升表 C；用户验收后若要沉淀，应走尺寸样式 `style_standard / style_export` 资产协议。

### SCREENSHOT-ORCHESTRATION-HARDENING-01：截图底座任务级编排与 Agent 共识

- **触发**：用户指出两个截图痛点：AutoCAD 在后台或未置顶时 Codex 测试看不到；DWG / 测试文件含海量图块时，默认截整个 CAD 当前视图无法证明本次精准任务，尤其是 10 个内容里只修复单项时需要只识别该修复对象。
- **OpenSpec**：新增 `openspec/changes/harden-agent-screenshot-orchestration/`，约束截图 decision、runner payload、Agent 共用合同和工作台检查。
- **实现**：`core/verification/render_preview.py` 新增 `build_screenshot_decision()`，并把 `screenshotDecision` 接入 `prepare_autocad_for_capture()` 与 `visual_preview_payload()`；聚焦顺序固定为本地 `target_handles` / `repair_plan` / bbox 优先，再退到 `execution_summary.created_handles`，目标不可用时报告不可用，不静默把 whole modelspace 当作精准截图。
- **Runner**：`core/verification/visual_cad_review.py` 和 `core/training/foundation_batch_training.py` 的截图报告 now 带 `screenshotDecision`、`visualPreview` 和 `visual_aid_only` 边界。
- **Agent 共识**：`agents/COMMON_PROMPT_CONTRACT.md` 增加“截图编排规则”；`core/training/learning_promotion.py` 把该规则写入共用合同生成源，防止工作台同步重写时丢失；`scripts/run_training_workbench_agent_check.py` 新增 `screenshot_orchestration_rules_in_common_contract`。
- **验证**：相关单测 `tests.core.test_render_preview`、`tests.core.test_table_c_evidence_gate`、`tests.core.test_cad_foundation_remaining_training`、`tests.core.test_training_workbench_sync`、`tests.core.test_training_learning_promotion` 共 66 OK；`openspec.cmd validate --all --strict --json --no-interactive` 12/12 pass；`scripts/sync_training_workbench.py` pass，Agent check 40/40 pass。
- **真实 CAD 截图**：`scripts/render_preview.py --check` 为 ready；`render_preview.py --capture-autocad-window --execution-summary projects/residential_sofa_2seat_20260528/runs/round14_execution_summary.json --target-handle 1F7C --output output/previews/screenshot-orchestration-target-1F7C.png --no-foreground` 成功，`mode=autocad_window_printwindow`、`foreground_first=false`、`focus.source=target_handles`、`resolved_count=1`；PNG 尺寸 `1701x1388`，像素非空。截图仍是视觉辅助，不提升表 C，不保存当前业务 DWG。

### DIMENSION-STYLE-PANEL-REPAIR-HARDENING-01：尺寸样式训练单格局部修复

- **触发**：用户指出“为什么要重画 10 个”，并提醒既有规则应支持单个框改动只删改那一个。
- **根因**：`run_dimension_style_training.py` 旧 cleanup 入口只读取上一轮报告的全局 `createdHandles`，绘制器也无条件输出标题并遍历全部 10 个 canonical 样式；即便报告已有 `panelHandlesByStyle` / `panelBoundsByStyle`，执行链路也没有消费这些 panel 级证据。
- **实现**：新增 `--only-style`，支持用 `styleId`、中文 CAD 样式名或可见标题匹配目标；局部 cleanup 只删除 `panelHandlesByStyle[目标样式]`，并把 `panelBoundsByStyle[目标样式]` 传给绘制器原位重画。缺少 panel handles 或 bbox 时直接 fail，不退回全量删除 / 全量重画。
- **审计**：`run_dimension_style_training()` 新增 `focused_repair` 模式，局部修复只检查目标格自身 readback、尺寸实体、图层、测量值和 containment；整批训练才检查端部家族覆盖广度。
- **真实 CAD 验证**：基于 r3 报告局部修复 06 `室内-洞口宽高尺寸`，真实 CAD 输出 `deletedCount=56`、`createdHandleCount=56`、`styleCount=1`、`dimensionReadbackCount=2`、`failedStyleCount=0`、`deletionScope=previous_panelHandlesByStyle`、`savedCurrentDwg=false`。报告：`output/training_queues/dimension-style-focused-10/real-cad-only-style-repair-hardening/dimension_style_training_report.json`；截图：`output/previews/dimension-style-focused-10-only-style-repair-hardening.png`。
- **验证**：新增单测覆盖“只删除目标 panel handles”和“局部重绘复用上一轮 panel bbox”；相关回归 56 OK；语法 `compile()` 通过。`py_compile` 被既有 `__pycache__` 写权限拒绝，未作为失败源码证据。
- **边界**：本轮只加固尺寸样式训练的局部修复执行半径，不保存当前业务 DWG，不沉淀资产，不提升表 C。

### DIMENSION-STYLE-05-06-VISUAL-FIX-01：05/06 面板视觉回归修复

- **触发**：用户截图复核指出 05/06 看起来仍有视觉 bug：06 `900` 贴近完成面，右侧比例样例过小，05/06 观感不齐。
- **根因**：上一轮只让实体 / 数值审计通过，没有把右侧样例可读性和横向尺寸文字 bbox 与完成面的间距做成硬门槛；AutoCAD 还会把横向尺寸文字自动放到尺寸线上方，导致单纯移动 text point 不足以解决贴线。
- **实现**：05/06 主示例使用 `sampleDisplayScales=[2.4, 2.0, 12.0]`，避免 2100 高度顶到标题区；06 横向尺寸线进一步下移；05/06 右侧比例样例改为固定大字号教学示意，不再被真实跨度压缩。
- **回归**：`tests/core/test_dimension_style_training.py` 新增断言，要求 06 `900` 横向尺寸 bbox 顶部低于竖向尺寸底点 / 完成面至少 120 个单位，防止报告 pass 但视觉贴线复发。
- **真实 CAD 证据**：05 最终局部修复 `real-cad-visual-fix-05-r8`，删除 / 重画 37 个 handles；06 最终局部修复 `real-cad-visual-fix-06-r9`，删除 / 重画 56 个 handles；均 `status=pass`、`savedCurrentDwg=false`。截图：`output/previews/dimension-style-05-06-visual-fix-final-r5.png`，裁剪图：`output/previews/dimension-style-05-06-visual-fix-final-r5-crop.png`。
- **验证**：`tests.core.test_dimension_style_training` 7 OK；`validate_visible_text()` pass；`scripts/run_dimension_style_training.py --fake-cad --output-dir output/training_queues/dimension-style-focused-10/fake-visual-fix-final-r10 --summary-only` pass，`dimensionReadbackCount=44`、`failedStyleCount=0`。
- **边界**：本轮仍是 focused 局部修复，只写 `CODEX_PREVIEW`，不保存当前业务 DWG、不沉淀资产、不提升表 C。

### DIMENSION-STYLE-ASSET-SEDIMENTATION-01：室内尺寸样式视觉标准系统资产

- **触发**：用户要求把 05/06 视觉修复后的尺寸样式标准“先沉淀下来”。
- **合同**：新增系统资产 `interior_dimension_style_visual_standard`，分类 `drawing_standards.basic`，名称“室内尺寸样式视觉标准”；合同写入 `libraries/system_library/drawing_standards/basic/assets.json`，全局索引写入 `libraries/system_library/registry.json`。
- **资产边界**：该资产为 `style_standard`，`exportMode=style_export`，`antiContamination=style_export_only`；明确禁止从 whole modelspace、current screen、training panel 或全 `CODEX_PREVIEW` 误导出对象 block。
- **原生 DWG**：已打开 / 激活 / 保存 `libraries/system_library/drawing_standards/basic/standard_assets.dwg`，写入 10 个中文 DimStyle 和 `CODEX_CN_TEXT`，报告 `output/validation_runs/system-assets/dimension-style-standard-dwg/native_dimension_style_report.json`；AutoCAD 活动文档保留在 `standard_assets.dwg` 供人工复审，当前业务 DWG 未保存。
- **状态**：资产验证状态为 `native_style_definition_written`，表示原生样式定义与变量回读已完成；仍未完成跨 DWG style import / reuse replay、plot/CTB/STB 输出和用户视觉复审，因此不标记为 reuse verified。
- **验证**：`sediment_system_asset.py --verify --category drawing_standards.basic --asset-id interior_dimension_style_visual_standard` pass；`sync_training_workbench.py` pass，Agent check 40/40 pass；`tests.core.test_system_asset_sedimentation tests.core.test_semantic_asset_rules tests.core.test_dimension_style_training` 共 24 OK。

### DIMENSION-STYLE-ASSET-ATOA-HARDENING-01：尺寸样式资产复用与 A-to-A 联通加固

- **触发**：用户追问规则、A-to-A、复用和系统理解力是否打牢固，要求继续加固。
- **根因**：资产合同和 `standard_assets.dwg` 已写入，registry 语义检索也能命中 `interior_dimension_style_visual_standard`；但复用计划仍被 `needs_precise_native_source` 阻断，因为复用器只识别 included handles / blockName / verified style native DWG，未把 `native_style_definition_written` 当作可计划的样式源；同时 registry 资产行缺少 `nativeDwgExists`，A-to-A 共用规则也没有专门锁住样式资产复用边界。
- **实现**：`core.assets.system_asset_reuse` 对 `style_standard + style_export + native_style_definition_written` 生成 `sourceSpec.mode=style_definition`，并在 apply 阶段无 style importer 时返回 `style_reuse_deferred_cad_required`，不复制 `CODEX_PREVIEW` 图元、不保存业务 DWG。
- **索引加固**：`core.assets.system_asset_sedimentation` 的 registry asset row 现在带 `nativeDwgExists`；当前 `libraries/system_library/registry.json` 的尺寸样式资产行已补该字段。
- **A-to-A**：`core/training/learning_promotion.py` 新增“系统资产与样式复用规则”，同步生成到 `agents/COMMON_PROMPT_CONTRACT.md`；`scripts/run_training_workbench_agent_check.py` 新增 `system_asset_reuse_rules_in_common_contract`，防止同步后规则漂移。
- **事实源**：`docs/training/training-sources.json` 新增系统资产合同、native 写入报告和复用探针报告；探针 `output/validation_runs/system-assets/dimension-style-standard-dwg/reuse_workflow_probe.json` 证明白话 query 可生成 ready workflow，`sourceSpec.mode=style_definition`。
- **验证**：新回归覆盖 native-written 样式资产复用计划、deferred apply 和 registry `nativeDwgExists` 字段；相关 54 tests OK；资产 verify pass；`sync_training_workbench.py` pass，Agent check 41/41 pass。
- **边界**：这次把“可理解、可检索、可生成 style_definition 计划、A-to-A 共享规则”打通；真正跨 DWG 自动 import DimStyle 仍是后续 style importer / readback gate，不在本轮冒充已复用完成。

### DIMENSION-STYLE-ASSET-VISIBLE-PANEL-01：尺寸样式系统资产 DWG 可见面板补写

- **触发**：用户打开 `standard_assets.dwg` 后指出没有看到尺寸样式内容，只有线型表。
- **根因**：上一轮 native 写入只保存了 10 个中文 DimStyle 和 `CODEX_CN_TEXT`，这属于不可见样式表定义；资产 DWG 模型空间没有同步写入可人工复审的尺寸样式面板。
- **修复**：直接在 `libraries/system_library/drawing_standards/basic/standard_assets.dwg` 模型空间追加 10 个尺寸样式可见面板，停放在既有线型表右侧，不保存当前业务 DWG。
- **真实 CAD 证据**：`output/validation_runs/system-assets/dimension-style-standard-dwg/native_visible_panel_r1/native_visible_panel_summary.json` 为 `status=pass`，`createdHandleCount=325`、`dimensionReadbackCount=44`、`failedStyleCount=0`、`savedAssetDwg=true`、`savedCurrentBusinessDwg=false`；截图为 `output/previews/system-asset-dimension-style-visible-panel-r1-focused.png`。
- **资产合同**：`libraries/system_library/drawing_standards/basic/assets.json` 和 `libraries/system_library/registry.json` 已补 `nativeVisiblePanelEvidence`、visible panel 报告和截图证据；asset lifecycle 标为 `verified`，但 `verificationStatus` 保持 `native_style_definition_written`，以免破坏样式复用计划识别。
- **编码纠偏**：一次内联脚本更新 JSON 时把新增中文字段写成 `????`，`system_asset_reuse_workflow` 的 registry encodingPreflight 已正确阻断；已改用补丁修复坏中文并扫空 `???`，复跑复用探针后 `encodingPreflight=pass`、workflow `status=ready`。
- **验证**：资产 verify pass；`scripts/reuse_system_asset.py --workflow --plan-only ...` pass 并生成 `sourceSpec.mode=style_definition`；`scripts/sync_training_workbench.py` pass，Agent check 41/41；相关 54 tests OK；`node --check capability-map-data.js` 和 `git diff --check` pass。
- **边界**：本轮证明系统资产 DWG 里已有可见尺寸样式面板和 CAD readback 证据；真正跨 DWG style import / plot / CTB / STB 和用户视觉验收仍未完成。

### SYSTEM-ASSET-TRUE-SEDIMENTATION-GATES-01：真沉淀与 A-to-A 复用门禁

- **触发**：用户指出两类问题不能再靠事后加固：一是资产合同 / DimStyle 写入不等于通用资产 DWG 中可见可验收；二是语义能命中不等于可执行复用和 A-to-A 联通已经提升。
- **实现**：`core.assets.system_asset_sedimentation.verify_system_asset_package()` 新增声明级门禁。`style_standard + style_export + native_style_definition_written / written_to_standard_assets_dwg` 必须有 `nativeVisiblePanelEvidence` 或等价可见 native 证据；`lifecycle=verified` 必须有 `reuseWorkflowProbe` 或真实 `reuseReplay`。
- **registry 透传**：`_registry_asset_entry()` 会把合同中的 `nativeVisiblePanelEvidence` 和 `reuseWorkflowProbe` 摘要写入 `libraries/system_library/registry.json`，防止合同有证据、全局检索 / A-to-A 看不到。
- **语义 / A-to-A**：`core.assets.semantic_rules` 的沉淀规则增加 `native_visible_asset_gate` 与 `reuse_workflow_probe`；复用规则增加 `reuse_workflow_probe`。`core.training.learning_promotion` 的共用 Prompt 生成源新增 `nativeVisiblePanelEvidence` / `reuseWorkflowProbe` 规则，`run_training_workbench_agent_check.py` 同步检查这些短语。
- **当前资产回填**：`interior_dimension_style_visual_standard` 的合同和 registry 已补 `reuseWorkflowProbe`，事实源新增 `dimension-style-visual-standard-reuse-probe-after-visible-panel`，指向 `output/validation_runs/system-assets/dimension-style-standard-dwg/reuse_workflow_probe_after_visible_panel.json`。
- **验证**：先写红灯测试证明旧 verify 会漏放缺门禁资产，再实现转绿；`tests.core.test_system_asset_sedimentation tests.core.test_semantic_asset_rules tests.core.test_training_workbench_sync` 共 35 OK；`scripts/sediment_system_asset.py --verify --category drawing_standards.basic` pass，checked 包含 `native visible asset evidence` 和 `executable reuse workflow probe`；`scripts/sync_training_workbench.py` pass，Agent check 41/41。
- **边界**：`reuseWorkflowProbe status=ready` 证明 registry 编码、语义匹配、workflow 和 `sourceSpec` 联通；它仍不等于已经在当前业务 DWG 完成 style import。实际 `asset_reused` 仍需 created handles / readback。

### SYSTEM-ASSET-SHELF-CLEARANCE-REPAIR-01：系统资产 DWG 货架重叠纠偏

- **触发**：用户复审 `standard_assets.dwg` 截图后指出仍有框线 / 标签压住资产内容，视觉排版凌乱；上一轮 `visualRackPlan` 与 created-handle readback 通过，但没有审计新画货架实体与既有资产内容 bbox 是否相交。
- **根因**：`scripts/layout_system_asset_shelves.py` 旧布局用整张非货架内容的 union bbox 按 62% 硬切 A1/A2，再把 SOURCE 边界和槽位标签固定画入内容区；治理门禁只验 plan 架构和本轮 created handles 是否存在，未把保护内容簇与货架实体 bbox 做 clearance。
- **实现**：新增真实内容簇读取与 `content_cluster_bbox_clearance_v1` 布局，按非货架实体 bbox 聚类 A1 线型表和 A2 尺寸面板；SOURCE 边界只围在保护内容外侧，标签移到 header/footer；`createdEntityReadback` 记录全量 `entityBboxes`；新增 `visualClearanceAudit`，任何货架框线、标签、route 或 slot grid bbox 与保护内容相交即 fail。
- **架构加固**：`audit_visual_rack_plan()` 接入可选 `clearance_report`；`run_asset_library_governance_check.py` 现在必须读取最新 `shelf_layout_report.json`，确认 `savedAssetDwg=true`、`savedCurrentBusinessDwg=false`、created entity readback ok、protected content readback ok 且 `overlapCount=0`，否则治理验收失败。
- **真实 CAD 证据**：重新打开 / 保存 `libraries/system_library/drawing_standards/basic/standard_assets.dwg`，清理上一轮 209 个货架 handles 后新建 209 个；保护内容 readback 349 个非货架实体，A1/A2 两簇；`visualClearanceAudit.status=pass`、`overlapCount=0`。报告 `output/validation_runs/system-assets/asset-library-shelves/shelf_layout_report.json`；截图 `output/previews/system-asset-library-shelves-r3.png`。
- **验证**：新增红灯测试覆盖 clearance 失败和 A2 内容被 union 分割线切掉；资产相关回归 `tests.core.test_system_asset_sedimentation tests.core.test_system_asset_reuse tests.core.test_semantic_asset_rules` 共 43 OK；`scripts/run_asset_library_governance_check.py` pass；`scripts/sediment_system_asset.py --verify --category drawing_standards.basic` pass；`scripts/render_preview.py --check` ready；OpenSpec 13/13 pass；`scripts/sync_training_workbench.py` pass，Agent check 41/41。
- **边界**：本轮证明系统资产 DWG 货架脚手架与既有 A1/A2 资产内容不再 bbox 重叠；截图仍是人工复审辅助，不替代 handles / bbox / readback。对象 block 本体进入各自分类 DWG、真实跨 DWG 对象复用 replay 仍按单资产另证。

### SYSTEM-ASSET-WAREHOUSE-READABILITY-HARDENING-01：系统资产 DWG 视觉仓库可读性门禁

- **触发**：用户再次复审截图指出上一轮虽然 `overlapCount=0`，但 A1/A2 分区仍拥挤、源边界语义混乱，视觉验收不合格；追问应改规则、Agent Prompt、A-to-A 还是布局。
- **根因**：旧门禁只检查 visualRackPlan 结构、created handles、shelf/content bbox 不相交，缺少“仓库是否可读”的机器指标；`pipeline_visual_layout_reviewer` 的输出字段也只要求五个泛化 pass，缺少 aisle、density、source/proof、layer semantics 和 non-screenshot evidence。
- **实现**：`audit_visual_rack_plan()` 新增 `readability_report`；`layout_system_asset_shelves.py` 新增 `visualReadabilityAudit`，检查 A1/A2 与 A2/B 通道、A1/A2 内容宽度占比、proof content 图层、source/proof 分离；旧 proof panel 从 `CODEX_PREVIEW` 迁到 `ASSET_PROOF_CONTENT`，A2 内容簇按 handles 右移，`ASSET_SOURCE_BOUNDARY` 改成小 source token，不再大框包住 proof panel。
- **A-to-A / Prompt**：`visual_layout_review` 现在必须有 `layoutReadabilityAcceptable`、`aisleClearanceAcceptable`、`contentDensityAcceptable`、`sourceProofRolesSeparated`、`layerSemanticsAcceptable`、`nonScreenshotEvidenceChecked`；同步更新 `pipeline_visual_layout_reviewer`、`agents/COMMON_PROMPT_CONTRACT.md`、Prompt 生成源和工作台 Agent check。
- **真实 CAD 证据**：重新保存 `standard_assets.dwg`，`shelf_layout_report.json` 为 `status=pass`、`createdHandleCount=219`、`contentMutationCount=519`、`visualClearanceAudit.overlapCount=0`、`visualReadabilityAudit.issueCount=0`；A1/A2 通道 1600，A2/B 通道 1400，A1 内容占比 0.7792，A2 内容占比 0.7146，proof content 图层只剩 `ASSET_PROOF_CONTENT`。截图：`output/previews/system-asset-warehouse-readability.png`。
- **验证**：新增红灯测试覆盖旧 reviewer 字段漏放、Core readability fail、零重叠但拥挤 / CODEX_PREVIEW 图层 fail；`tests.core.test_a_to_a_task_contract` 6 OK，`tests.core.test_system_asset_sedimentation` 27 OK；`scripts/run_a_to_a_orchestration_gate_check.py` pass；`scripts/run_asset_library_governance_check.py` pass；`scripts/render_preview.py --check` ready，AutoCAD 窗口截图 captured。
- **边界**：截图仍是 visual_aid_only；本轮证明系统资产 DWG 货架可读性和保存 / readback 门禁通过，不代表对象资产跨 DWG 复用 replay 已完成。

### MAIN-AGENT-DISPATCH-AWARENESS-01：主 Agent 轻量自检与动态加派门禁

- **触发**：用户希望系统主 Agent “知道自己是谁、要干嘛”，并能判断是否需要加派新的 Agent，但后续确认只做轻量版，不做对话人格模拟。
- **实现**：`core.orchestrator.a_to_a_task_contract` 新增 `mainAgentSelfCheck` 与 `dispatchDecision`。高风险任务声明主 Agent 身份、任务理解、责任边界、已知限制和决策依据；动态加派只允许 manifest 已登记 Agent，未登记新 Agent 进入 `additionalAgentRequests`，状态为 `needs_reviewed_package` / `needs_openspec_change`，不得临场生效。
- **门禁**：新增 `main_agent_dispatch_awareness` hard gate；`workflow_dispatch` 继续只消费合同 blocked 结果，不另建第二套判断。`agents/pipeline/pipeline_manifest.json` 新增主 Agent 身份、registered-only 动态派发策略、未登记 Agent 请求策略和 forbidden patterns。
- **A-to-A 检查**：`scripts/run_a_to_a_orchestration_gate_check.py` 现在检查 main agent identity、dynamic dispatch policy、unregistered agent policy、未登记 Agent 不激活、forced unregistered effective agent 阻断，以及 `layoutReadabilityAcceptable`。
- **验证**：先写红灯测试确认新字段缺失会失败；实现后 `tests.core.test_a_to_a_task_contract` 11 OK，`tests.core.test_workflow_dispatch` 9 OK，`scripts/run_a_to_a_orchestration_gate_check.py` status=`pass`。
- **边界**：本轮是 no-CAD 编排门禁加固，未写 CAD、未保存 DWG、不提升表 C；主 Agent 自检是工程责任边界，不是人格或真实 CAD 证据。

### ARCHITECTURE-DOC-HARDENING-02：架构链路与硬门禁索引轻量加固

- **触发**：按用户给出的优化清单，做中等范围“架构收口 + 轻量加固”，不展开大拆迁。
- **实现**：根 `README.md`、`docs/architecture/README.md` 和 `docs/architecture/current-module-boundaries.md` 统一为 `User Request -> semantic route -> A-to-A contract -> CAD_PLAN / asset workflow / training route -> execution -> verification -> promotion/sync` 链路；架构 README 新增 UTF-8、CAD_PLAN validate/dry-run、`CODEX_PREVIEW/no-save`、A-to-A、资产来源、复用 readback、训练 promotion 和 workbench sync 的硬门禁索引；模块边界补 `core/orchestrator`、`core/assets`、`core/training`、`core/verification`、`agents/pipeline`、`agents/<scenario>` 的禁止边界。
- **OpenSpec**：复用已 complete 的 `openspec/changes/architecture-boundary-hardening-01/` 作为历史边界合同，在 tasks 中记录 follow-up；未新开重复 change，未归档其它 completed changes。
- **审计**：`core.maintenance.doc_governance` 新增 `architecture_hardening` 子报告，并补 `tests.core.test_doc_governance` 回归，缺链路 / 门禁 / 模块 token 会进入 findings。
- **验证**：`python -m unittest tests.core.test_doc_governance -v` 27 OK；`scripts/run_doc_governance_audit.py` status=`pass`、`finding_count=0`、`architecture_hardening.checked_file_count=3`。
- **边界**：本轮只做文档架构和审计入口加固；未改 CAD 执行、未连接 AutoCAD、未保存 DWG、不提升表 C。

### MODEL-BACKED-AGENT-REVIEWERS-P1：Codex CLI 模型复审桥与视觉 reviewer MVP

- **触发**：用户追问系统里的 Agent 是否只是规则型“假智能体”、能否不用 API key 而改用 Codex CLI 调用 5.5 模型，并要求先把方案写成临时 MD 后执行第一包。
- **方案**：当时新增模型型 Agent 临时计划卡，并明确主 `PlanMD` 仍是 `CORE_RESTRUCTURE_PLAN.md`；该临时卡现已迁入主计划并删除。模型型 Agent 只作为少数高风险 reviewer，规则型门禁继续负责 CAD 证据。
- **实现**：新增 `core/model_review/`，封装 `codex.cmd exec` 的只读模型复审桥，支持 `--model`、`--image`、`--output-schema`、`--output-last-message`、`--sandbox read-only` 和 `--ephemeral`；默认 `enabled=false`，单测用 fake runner，不静默消耗模型额度。
- **视觉门禁**：新增视觉仓库复审 schema 和转换器；A-to-A `visual_layout_review` 支持 `modelBackedReviewRequired`，模型缺失、schema fail、`modelInvoked=false` 或 blocking 时阻断；`audit_visual_rack_plan()` 和 `run_asset_library_governance_check.py` 可读取 `modelVisualReview`。
- **认知规则**：`pipeline_visual_layout_reviewer`、pipeline manifest、`agents/COMMON_PROMPT_CONTRACT.md`、`agents/pipeline/README.md` 和治理规则已写明契约型 / 规则型 / 模型型 Agent 边界：模型 pass 不替代编码、handles、bbox、图层、sourceSpec、reuse replay、保存状态或用户复审。
- **验证**：`tests.core.test_model_review` 5 OK，`tests.core.test_a_to_a_task_contract` 11 OK，`tests.core.test_training_workbench_sync` 18 OK，`tests.core.test_system_asset_sedimentation` 27 OK；`scripts/run_a_to_a_orchestration_gate_check.py` pass；`codex.cmd exec --help` pass。`scripts/run_asset_library_governance_check.py` 仍因既有 latest shelf layout report 缺失 fail；该包当时暴露的 13 个 active fact source 缺失已由后续 `DATA-BLOAT-EVIDENCE-CLOSURE-01` 归档修复。
- **边界**：本包未真实调用 `gpt-5.5`，未连接 AutoCAD，未写入 / 保存 DWG，未修复 A2 当前仓库排版和 `CODEX_PREVIEW` 遗留污染，不提升表 C。

### SYSTEM-ASSET-WAREHOUSE-GOVERNANCE-P2：仓库治理 full layer census 与证据文件门禁

- **触发**：继续执行临时方案第二包，针对 A2 仓库总览“像乱码”的根因补硬门禁：旧报告只采样 `layerSamples`，可能漏掉 A1/A2 内真实 `CODEX_PREVIEW` 污染；资产合同引用的证据文件缺失也曾被 verify / governance 弱放行。
- **实现**：`layout_system_asset_shelves.py` 的 protected content readback 现在输出全量 `layers` / `layerCounts`；`audit_visual_rack_plan()` 新增 `protected_content_report`，sample-only fail，full census 中出现 `CODEX_PREVIEW` 或 `ASSET_SOURCE_BOUNDARY` 即 fail。
- **治理脚本**：`scripts/run_asset_library_governance_check.py` 会把 latest shelf report 的 `protectedContentReadback` 传入 Core audit，并递归检查 `evidenceRefs`、`evidenceLinks.refs`、`nativeVisiblePanelEvidence`、`reuseWorkflowProbe` 等白名单字段引用的本地证据文件是否存在。
- **Agent / Prompt**：`pipeline_visual_layout_reviewer`、共用 Prompt 合同、Prompt 生成源、工作台 Agent check 和治理规则已补 full layer census 与 evidence file exists 边界。
- **验证**：先写红灯测试后实现；`tests.core.test_asset_library_governance` 3 OK；`tests.core.test_system_asset_sedimentation` 27 OK；`tests.core.test_model_review tests.core.test_a_to_a_task_contract` 16 OK；`tests.core.test_training_workbench_sync` 18 OK。真实 `scripts/run_asset_library_governance_check.py` 现在 fail，暴露多个 referenced evidence 文件缺失和 latest shelf layout report 缺失；该包当时暴露的 13 个 active fact source 缺失已由后续 `DATA-BLOAT-EVIDENCE-CLOSURE-01` 归档修复，visual warehouse / model-backed 规则检查均 pass。
- **边界**：本包只加治理门禁和报告字段，不连接 AutoCAD、不重排 / 保存 `standard_assets.dwg`、不恢复缺失历史证据、不提升表 C。
