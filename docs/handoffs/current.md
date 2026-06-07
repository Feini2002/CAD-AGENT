# 当前交接包窗口
## ENTRYPOINT-CUSTODY-PERMISSION-SELFTRAINING-01 — 入口 custody manifest、runtime guard / lease 权限位、denylist / kill switch、route custody 摘要、all-31 replay fail-closed、training claim audit 和 model trace claim audit 已收口为机器包；临时架构 MD 已删除，事实源见 `config/entrypoint_custody_manifest.json`、`core/entrypoint_custody/**`、`scripts/run_entrypoint_custody_audit.py`、`scripts/run_training_report_claim_audit.py`、`scripts/run_model_trace_claim_audit.py` 与 `tests/core/test_legacy_entrypoint_custody_closure.py`。收尾真实 CAD smoke 只写 `CODEX_PREVIEW`，10/10 handles 回读，`saved_dwg=false`；边界是不提升表 C、不恢复正式训练、不表示所有脚本都已强制接 runtime guard。
## 自适应能力成长训练包 — 已落为 `core/training/*growth*`、runner `--replay-mode growth_replay`、OpenSpec 与测试；不运行真实 CAD、不部署 Worker、不写训练事实源、不提升表 C。handoff 索引见 `docs/handoffs/package-index.md`，完整历史 ID 见 `docs/status/changelog.md`。
## WORKER-ORCHESTRATOR-CLOUDFLARE-DEPLOY-01
1. **包名**：`WORKER-ORCHESTRATOR-CLOUDFLARE-DEPLOY-01`
2. **修改文件列表**：更新 `wrangler.jsonc`、`package.json`、`workers/orchestrator/scripts/run-wrangler.mjs`、`workers/orchestrator/src/worker-configuration.d.ts`、`WORKER_ORCHESTRATOR_DEPLOY_CHECKLIST.md`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`docs/status/current.md`、`docs/status/changelog.md`、`docs/handoffs/current.md` 和 `docs/handoffs/package-index.md`。
3. **关键设计说明**：Cloudflare Worker 已按平台规则部署为 `cadagent`；用户原始命名 `CADAgent` 因 Wrangler 校验要求小写而规范化。部署使用 `deploy --strict --secrets-file`，真实 deploy 仍需 `CADAGENT_DEPLOY_APPROVED=true`，wrapper 继续阻断裸 deploy、`secret put` 和 `dev --remote`。
4. **新增/修改测试**：未新增 runtime 测试；本包新增远程部署 smoke 验证和 wrapper 真实 deploy 放行门禁。
5. **实际运行的命令和结果**：`npm.cmd run worker:check` -> pass；`wrangler whoami` -> 已登录 `cmw1196466375@gmail.com` 且具备 Workers 写权限；`wrangler deploy --strict --secrets-file <temporary-json>` -> deployed `cadagent`，URL `https://cadagent.cmw1196466375.workers.dev`，version `ecf455d4-89f0-4b14-92aa-0c3885c7c491`；远程 `npm.cmd run worker:smoke` -> pass，`runId=run_20260606144204_worker_orchestration_ready_06e12cd1`、`state=completed`。
6. **是否运行真实 CAD**：否。本包只运行 Worker / Durable Object 远程编排 smoke；未连接 AutoCAD、未运行 CAD-MCP、未写 / 保存 DWG、未删除实体、未改正式图层。
7. **机器可读证据路径**：部署配置在 `wrangler.jsonc`；远程 smoke 脚本为 `workers/orchestrator/test/orchestrator-smoke.mjs`；部署停闸和记录为 `WORKER_ORCHESTRATOR_DEPLOY_CHECKLIST.md`。
8. **结论分类**：Cloudflare remote `worker_orchestration_ready` 已激活并通过 smoke；不等于 `local_bridge_connected`、`single_agent_live`、`multi_agent_live` 或 `cad_mcp_preview_live`。
9. **剩余风险**：Queue / Workflows、真实 bridge-owned Codex config、真实 `gpt-5.5` runner、多 Agent live、CAD-MCP preview handles readback、token rotation、rollback drill 和生产环境分层仍需后续单独包证明。
---
## WORKER-ORCHESTRATOR-PREDEPLOY-HARDENING-01
1. **包名**：`WORKER-ORCHESTRATOR-PREDEPLOY-HARDENING-01`
2. **修改文件列表**：新增 `workers/orchestrator/**`、`wrangler.jsonc`、`package.json`、`package-lock.json`、`WORKER_ORCHESTRATOR_DEPLOY_CHECKLIST.md`；更新 `.gitignore`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`docs/status/current.md`、`docs/status/changelog.md`、`docs/handoffs/current.md` 和 `docs/handoffs/package-index.md`；删除本轮临时 Worker playMD。
3. **关键设计说明**：本包把 Worker-first 编排从临时 playMD 推进为 Cloudflare Worker 预部署代码骨架：Worker API + Durable Object run state，任务图提交前校验，bridge 注册 / lease / heartbeat / submit，heartbeat token、bridge token、idempotency、timeout / retry / DLQ、stale / offline bridge 处理、backpressure、circuit breaker、kill switch、日志脱敏、secret scan 和 wrapper 级 deploy guard。远程部署前必须继续走 `WORKER_ORCHESTRATOR_DEPLOY_CHECKLIST.md`。
4. **新增/修改测试**：新增 runtime contract tests、HTTP smoke、boundary check、secret scan 和 wrangler wrapper 负向验证；runtime tests 覆盖 wrong submit `heartbeatToken`、revoked bridge replay、重复 / 缺失 / 环形 task graph、DLQ、bridge offline / stale、max concurrent leases、capability gap、backpressure、security blocked 等路径。
5. **实际运行的命令和结果**：`npm.cmd run worker:check` -> pass（runtime tests 14 pass，TypeScript `--noEmit` pass，secret scan pass，wrangler types pass，`wrangler deploy --dry-run` pass）；本地 `wrangler dev --local` + `npm.cmd run worker:smoke` -> pass，最终 run id 为 `run_20260606130602_worker_orchestration_ready_1be702ae`；`node workers/orchestrator/scripts/run-wrangler.mjs deploy` / `secret put WORKER_API_TOKEN` / `dev --remote` 均按预期 exit 2 并被 wrapper 阻断。
6. **是否运行真实 CAD**：否。本包只做 Worker / Durable Object 编排预部署骨架、代码测试和文档收尾；未连接 AutoCAD、未运行 CAD-MCP、未写 / 保存 DWG、未删除实体、未改正式图层。
7. **机器可读证据路径**：核心代码在 `workers/orchestrator/src/`；runtime tests 在 `workers/orchestrator/test/orchestrator-runtime.test.ts`；HTTP smoke 在 `workers/orchestrator/test/orchestrator-smoke.mjs`；wrapper / secret / boundary checks 在 `workers/orchestrator/scripts/`；部署停闸清单为 `WORKER_ORCHESTRATOR_DEPLOY_CHECKLIST.md`。
8. **结论分类**：local / dry-run `worker_orchestration_ready` 预部署骨架已加固并收尾；临时 playMD 已删除，长期事实源已回写。未声明 Cloudflare remote deploy、真实 secret、Queue / Workflows、真实 bridge runner、真实模型活体调用或 CAD-MCP preview verified。
9. **剩余风险**：远程 Cloudflare 环境、`wrangler secret put`、Queue / Workflows、bridge-owned Codex config、真实 local bridge / `gpt-5.5` runner、多 Agent live 和真实 CAD-MCP preview handles readback 仍需后续分层证明。
---
## 架构归并画布包
1. **包名**：架构归并画布、三成熟度口径与工作台表 C 收口；包 ID 见 `CORE_RESTRUCTURE_PLAN.md` §0.2
2. **修改文件列表**：重写 `docs/architecture/system-architecture-convergence.md`，调整 `docs/architecture/README.md` 的入口顺序；更新 `core/maintenance/doc_governance.py`、`tests/core/test_doc_governance.py`、`agents/pipeline/pipeline_manifest.json`、`scripts/run_a_to_a_orchestration_gate_check.py`、`tests/core/test_a_to_a_task_contract.py`、`core/verification/capability_coverage.py`、`scripts/build_capability_map_data.py`、`scripts/run_training_workbench_agent_check.py`、`capability-map.html`、`capability-map-data.js`、`output/validation_runs/capability-lab/cad_capability_coverage.json`、`docs/status/issues.md`、`docs/handoffs/current.md`、`docs/handoffs/package-index.md` 和 `openspec/changes/unify-system-architecture-canvas/tasks.md`。
3. **关键设计说明**：本包把 `system-architecture-convergence.md` 收束为七层任务生命周期：系统入口、任务对象、决策编排、能力与证据、执行工具、审计修复、沉淀成长。旧表格、底座、训练、资产、多 Agent、Worker / bridge、截图和工作台全部归位到这些层内；旧表 C / 90.99% 统一改称 `Core Proof Coverage`，只代表底座证据覆盖，不代表 `Agent Task Maturity` 或 `Project Delivery Readiness`。OpenSpec 仍是单个复杂变更契约，不成为第二套主计划。
4. **新增/修改测试**：新增文档治理语义测试，阻断活跃状态文档把表 C 写成端到端真实 CAD 能力；新增 OpenSpec tasks 不能宣称全局 backlog 的回归测试；新增 A-to-A manifest 测试，要求仓库级治理任务具备 `system_architecture_canvas` hard gate。
5. **实际运行的命令和结果**：`scripts/sync_training_workbench.py` -> pass，Agent check 60/60；`scripts/run_a_to_a_orchestration_gate_check.py` -> pass；`tests.core.test_doc_governance tests.core.test_planmd_governance tests.core.test_a_to_a_task_contract tests.core.test_training_workbench_sync tests.core.test_capability_coverage -v` -> 91 OK；`scripts/run_doc_governance_audit.py` -> pass，`finding_count=0`；`openspec.cmd validate --all --strict --json --no-interactive` -> 17/17 valid。
6. **是否运行真实 CAD**：否。本包是架构、规则、脚本口径和派生工作台显示收口；未连接 AutoCAD、未写 / 保存 DWG、未删除实体、未改正式图层。
7. **机器可读证据路径**：OpenSpec 契约在 `openspec/changes/unify-system-architecture-canvas/`；派生 coverage 快照为 `output/validation_runs/capability-lab/cad_capability_coverage.json`；工作台派生数据为 `capability-map-data.js`；A-to-A hard gate 来源为 `agents/pipeline/pipeline_manifest.json`。
8. **结论分类**：架构归并画布、三成熟度口径、工作台表 C 显示口径、文档治理阻断和 A-to-A 仓库级 hard gate 已收口；正式训练仍默认暂缓，除非用户显式覆盖。
9. **剩余风险**：本包不提升表 C、不证明 Agent 端到端任务成熟、不证明真实项目交付准备度；后续恢复训练前仍需按当前文档确认三口径边界，并对具体训练 / CAD 包单独生成 CAD 证据。

---

## 本地模型桥收口包

1. **包名**：本地模型桥安全加固与独立 MD 收口；handoff 索引见 `docs/handoffs/package-index.md`，完整历史 ID 见 `docs/status/changelog.md`
2. **修改文件列表**：更新 `core/orchestrator/local_live_model_bridge.py`、`core/orchestrator/local_live_model_bridge_state.py`、`core/orchestrator/local_live_model_bridge_diagnostics.py`、`tests/core/test_local_live_model_bridge.py`、`tests/core/test_local_live_model_bridge_flows.py`、`tests/core/test_local_live_model_bridge_diagnostics.py`；同步 `CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`README.md`、`agents/pipeline/README.md`、`docs/architecture/README.md`、`docs/architecture/cad-agent-task-chain.md`、`docs/status/current.md`、`docs/status/changelog.md`、`docs/status/issues.md`、`docs/planning/任务清单.md`、`docs/handoffs/current.md` 和 `docs/handoffs/package-index.md`；删除原独立本地活体模型桥架构 MD。
3. **关键设计说明**：本包把上一轮讨论出的偏差收束为 runtime hard gate：未知 `target_stage` 直接失败，同秒 run id 防碰撞，live 阶段未登记 / 能力不匹配 bridge 不能 lease，`submit_result` 校验 lease identity；diagnostics 必须追到 `traceRef` 对应的完整 model trace 包；CAD fake preflight 拆分 `runtimeStatus` 与 `proofStatus`，fake driver 只能 `proofStatus=not_verified`。独立架构 MD 的剩余路线迁入 `CORE_RESTRUCTURE_PLAN.md` §3.1，避免形成第二套主计划。
4. **新增/修改测试**：新增 / 更新本地 live bridge、flows 和 diagnostics 测试，覆盖未知阶段、run id 碰撞、bridge registration / capability gate、submit identity、trace missing / bad route / missing codex exec、fake CAD proof 状态。
5. **实际运行的命令和结果**：红灯先失败于未知阶段未阻断、run id 碰撞、submit identity 缺口、trace 证据未校验、fake CAD proof 状态缺失和未登记 bridge 仍继续模型调用；实现后 `tests.core.test_local_live_model_bridge tests.core.test_local_live_model_bridge_diagnostics tests.core.test_local_live_model_bridge_flows` -> 18 OK；相邻回归 `tests.core.test_local_live_model_bridge tests.core.test_local_live_model_bridge_diagnostics tests.core.test_local_live_model_bridge_flows tests.core.test_model_prompt_library tests.core.test_model_review` -> 49 OK；`py_compile core/orchestrator/local_live_model_bridge*.py scripts/diagnose_local_live_model_bridge.py scripts/probe_codex_cli_model_review.py` -> OK；旧 MD 文件名扫描 -> 无残留；`scripts/run_doc_governance_audit.py --fail-on-findings` pass；`openspec.cmd validate --all --strict --json --no-interactive` -> 16/16 pass；`git diff --check` 仅报告既有 Windows 行尾提示，无 whitespace error；严格 diagnostics 对最新真实 `single_agent_live` run 返回 `status=pass`。
6. **是否运行真实 CAD**：否。本包未新开真实 CAD；fake driver 仍只证明编排和 preview-only 安全边界，不证明真实 CAD 几何。
7. **机器可读证据路径**：最新真实 `single_agent_live` 证据为 `output/model_reviews/local_live_model_bridge_runtime_smoke_fresh_usable_20260606/run_20260606073718_single_agent_live_1a45fb4a/worker_run_state.json`，trace 包在同目录 `model_traces/pipeline_design_director/pipeline-design-director/`；沙箱网络阻断样本为 `output/model_reviews/local_live_model_bridge_runtime_smoke_fresh_20260606/run_20260606073443_single_agent_live_129a671e/`；业务证据不足导致 trace review blocked 的反例为 `output/model_reviews/local_live_model_bridge_runtime_smoke_fresh_approved_20260606/run_20260606073558_single_agent_live_84582a6a/`。
8. **结论分类**：本地 runtime / diagnostics 加固与独立 MD 收口已完成；最新 `single_agent_live` 真实 provider smoke 通过严格 diagnostics。未运行真实 CAD，不提升表 C，不声明真实 CAD preview verified。
9. **剩余风险**：远程 Cloudflare 环境、Queue / Workflows 接入、bridge-owned Codex config、真实 `single_agent_live` / `multi_agent_live` 复验和真实 CAD-MCP preview-only handles readback 仍需后续单独包证明；当前 Worker / Durable Object 只到本地 / dry-run 预部署骨架。

---

## LOCAL-LIVE-MODEL-BRIDGE-RUNTIME-GATES-01

1. **包名**：`LOCAL-LIVE-MODEL-BRIDGE-RUNTIME-GATES-01`
2. **修改文件列表**：新增 / 更新 `core/orchestrator/local_live_model_bridge.py`、`core/orchestrator/local_live_model_bridge_state.py`、`core/orchestrator/local_live_model_bridge_diagnostics.py`、`scripts/diagnose_local_live_model_bridge.py`、`tests/core/test_local_live_model_bridge.py`、`tests/core/test_local_live_model_bridge_flows.py`、`tests/core/test_local_live_model_bridge_diagnostics.py`；同步 `CORE_RESTRUCTURE_PLAN.md`、`docs/status/changelog.md`。
3. **关键设计说明**：本包把 Worker-first MVP 从架构口径推进为本地可测试骨架：run state、task envelope、bridge 注册 / lease / heartbeat / submit、idempotency、timeout / retry、circuit breaker、security gate、single-agent live、multi-agent live、CAD preview-only Tool Contract 和分层诊断入口均已落地。`worker_run_state` 增加 `featureGates`，默认只放行 `worker_orchestration_ready`；真实 bridge、GPT-5.5、多 Agent、CAD preview 和保存授权都必须按目标阶段 / 显式条件逐层启用。
4. **新增/修改测试**：新增本地 live bridge 编排、flows 和 diagnostics 测试，覆盖 W1-W5 fixture 行为、feature gates 默认关闭、bridge 离线定位、fake CAD 不冒充真实几何、CLI `--fail-on-blocked`。
5. **实际运行的命令和结果**：`tests.core.test_local_live_model_bridge_diagnostics tests.core.test_local_live_model_bridge tests.core.test_local_live_model_bridge_flows tests.core.test_model_prompt_library` -> 20 OK；`py_compile core/orchestrator/local_live_model_bridge*.py scripts/diagnose_local_live_model_bridge.py scripts/probe_codex_cli_model_review.py` -> OK；`scripts/diagnose_local_live_model_bridge.py --run-dir output/model_reviews/local_live_model_bridge_runtime_smoke/run_20260606064624_single_agent_live` -> `status=pass`、`single_agent_live` 通过、后续层 `not_enabled`；bridge 离线样本 `scripts/diagnose_local_live_model_bridge.py --run-dir output/model_reviews/local_live_model_bridge_diagnostics_smoke/run_20260606070743_single_agent_live` -> `firstBlockedAt=local_bridge_connected`、`nextAction=start_or_register_local_bridge`；同一样本加 `--fail-on-blocked` 返回预期 exit code 1；`scripts/run_doc_governance_audit.py --fail-on-findings` pass；`scripts/run_repo_audit.py --max-python-lines 500 --fail-on-severity medium` 无 medium/high 阻断；`openspec.cmd validate --all --strict --json --no-interactive` -> 16/16 pass。
6. **是否运行真实 CAD**：否。本包未新开真实 CAD；上一轮尝试 `autocad_existing` 因本机无活动 `AutoCAD.Application` COM 实例而正确 blocked。fake driver 只证明编排和 preview-only 安全边界，不证明真实 CAD 几何。
7. **机器可读证据路径**：`output/model_reviews/local_live_model_bridge_runtime_smoke/run_20260606064624_single_agent_live/worker_run_state.json`；`output/model_reviews/local_live_model_bridge_runtime_smoke/diagnostic_latest.json`；`output/model_reviews/local_live_model_bridge_diagnostics_smoke/diagnostic_bridge_offline.json`；真实 CAD 阻断报告为 `output/runs/model-agent-live-collab-proof-20260606-064743/cad_reports/cad_preview_tool_report.json`。
8. **结论分类**：Worker-first 系统骨架、分层 feature gate、运行诊断脚本和 fixture 验证已落地；`single_agent_live` 有历史真实 provider smoke 证据；`cad_mcp_preview_live` 只到 fake-driver / blocked-diagnostic 边界，不提升表 C。
9. **剩余风险**：真实 CAD-MCP preview 仍需在有 AutoCAD / CAD-MCP 的环境中单独触发；后续若接 Cloudflare Worker 真实部署，还需把本地 stand-in 状态机迁移到 Worker / Durable Object / Queue，并保留同一分层 gate 语义。

---

## LOCAL-LIVE-MODEL-BRIDGE-ARCHITECTURE-01

1. **包名**：`LOCAL-LIVE-MODEL-BRIDGE-ARCHITECTURE-01`
2. **修改文件列表**：曾新增独立本地活体模型桥架构 MD，并同步 `CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`README.md`、`agents/pipeline/README.md`、`docs/architecture/README.md`、`docs/architecture/cad-agent-task-chain.md`、`docs/status/current.md`、`docs/status/changelog.md`、`docs/status/issues.md`、`docs/planning/任务清单.md`、`docs/handoffs/current.md` 和 `docs/handoffs/package-index.md`；该独立 MD 已在本地模型桥收口包中迁移后删除。
3. **关键设计说明**：本包把“长期先接 Cloudflare Worker 编排层，再用本地 bridge 执行 Codex CLI / GPT-5.5”沉淀为架构路线：Worker 产品分工、API 最小端点、`task_envelope` / `agent_output` / `run_state` 数据合同、Worker 侧系统角色、模型型 Agent Prompt 合同、队列 / 依赖 / 状态机规则、超时 / 熔断 / retry / DLQ / backpressure / kill switch、安全与数据边界，以及 W0-W5 执行目标计划。完成声明分为 `worker_orchestration_ready`、`local_bridge_connected`、`single_agent_live`、`multi_agent_live`、`cad_mcp_preview_live` 和 `formal_training_integrated`；这些剩余路线当前维护在 `CORE_RESTRUCTURE_PLAN.md` §3.1。
4. **新增/修改测试**：未新增测试；这是架构文档与状态同步包。
5. **实际运行的命令和结果**：`scripts/run_doc_governance_audit.py --fail-on-findings` pass，`finding_count=0`。
6. **是否运行真实 CAD**：否。本包不连接 AutoCAD、不写 / 保存 DWG、不删除实体、不改正式图层。
7. **机器可读证据路径**：当前已迁移到 `CORE_RESTRUCTURE_PLAN.md` §3.1；无新增 CAD evidence、model provider proof 或 coverage JSON。
8. **结论分类**：Worker 编排 + 本地活体模型桥路线及执行契约已沉淀为主架构记录；它不证明 Worker 已部署、不证明真实模型已再次调用、不证明 CAD 几何、不提升表 C。
9. **剩余风险**：后续实现时需要分别证明 `worker_orchestration_ready`、`local_bridge_connected` 和 `single_agent_live`；接入 CAD-MCP 前要处理 bridge-owned Codex config 与 MCP 配置边界，避免 `--ignore-user-config` 连带忽略 MCP；Worker 保护机制必须先用 fixture 覆盖超时、熔断、重试耗尽、DLQ、bridge 离线和越权阻断。

---

## CORE-PLANMD-ARCH-ROUTER-01
1. **包名**：`CORE-PLANMD-ARCH-ROUTER-01`
2. **修改文件列表**：重写 `CORE_RESTRUCTURE_PLAN.md`；同步 `docs/status/changelog.md`、`docs/handoffs/current.md`、`docs/handoffs/package-index.md`。
3. **关键设计说明**：主 PlanMD 从旧包过程墙改为系统宪章 / 架构路由器，只保留主架构链路、不可破坏边界、事实源地图、未来开发路由、Decision Gates、执行入口和完成声明标准；训练内容只保留 `Visual-First` / `visual_parts` 边界和事实源链接。
4. **新增/修改测试**：未新增测试；复用现有文档治理、PlanMD、self_check 与 Core 重构回归。
5. **实际运行的命令和结果**：`scripts/run_doc_governance_audit.py --fail-on-findings` pass；`tests.core.test_doc_governance tests.core.test_planmd_governance tests.core.test_self_check tests.core.test_core_restructure -v` -> 48 OK。
6. **是否运行真实 CAD**：否。本包只做文档 / 架构治理；未连接 AutoCAD、未写 / 保存 DWG、未删除实体、未改正式图层。
7. **机器可读证据路径**：`CORE_RESTRUCTURE_PLAN.md`；验证输出来自本轮终端命令；无新增 CAD evidence 或 coverage JSON。
8. **结论分类**：唯一主 PlanMD 已收束为系统宪章 / 架构路由器（文档治理 pass，训练事实源、系统资产 registry、表 C 均未改）。
9. **剩余风险**：后续若新增具体开发包，仍需写入 `docs/planning/任务清单.md` 或对应 OpenSpec；本文不再承载单次训练流水、对象试点长证据或 completed change 任务清单。
---
## OBJECT-FAMILY-SOFA-REPLAY-RCAD-01
1. **包名**：`OBJECT-FAMILY-SOFA-REPLAY-RCAD-01`
2. **修改文件列表**：新增 `core/assets/object_family_cad_replay.py`、`scripts/run_object_family_cad_replay.py`、`tests/core/test_object_family_cad_replay.py`；更新 `core/assets/__init__.py`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、状态、changelog、handoff 和 package index；新增真实证据目录 `output/validation_runs/object-family-sofa-replay-20260605-rcad/`、截图 `output/previews/object-family-sofa-replay-20260605-rcad.png`、closeout 包 `output/runs/object-family-sofa-replay-20260605-rcad-closeout/`。
3. **关键设计说明**：按主计划 §0.1 为 sofa 对象族补真实 CAD replay。runner 复用 no-CAD trial 的 `draw_symbol_glyph` CAD_PLAN 草案，平移到 replay base point，重新 validate / dry-run，再通过现有 preview-only `execute_plan_file()` 写入 `CODEX_PREVIEW`；几何证明只认 created handles readback、bbox、layer、type count 和 closeout gate。
4. **新增/修改测试**：新增 `tests/core/test_object_family_cad_replay.py`，覆盖 fake CAD replay 生成 17 个回读实体、bbox / layer / type count / `savedCurrentDwg=false` 合同，以及 CAD 连接失败时返回 `external_blocker`。
5. **实际运行的命令和结果**：先运行红测，失败于 `ModuleNotFoundError: No module named 'core.assets.object_family_cad_replay'`；实现后 `tests.core.test_object_family_cad_replay` -> 2 OK；相邻回归 `tests.core.test_object_family_cad_replay tests.core.test_object_family_trial tests.core.test_local_asset_rag tests.core.test_asset_promotion_candidates tests.core.test_symbol_glyph_cad_smoke tests.core.test_execute_plan` -> 24 OK；真实 CAD replay 命令返回 `status=geometry_verified`、17/17 handles、bbox / layer / type count 匹配；`render_preview.py --capture-autocad-window --execution-summary ...` 成功生成任务级截图；`run_visual_cad_review.py` -> pass；closeout gate -> `ready_for_delivery`。
6. **是否运行真实 CAD**：是。外部 COM 连接当前活动文档 `projects/测试文件.dwg`，只写 `CODEX_PREVIEW`，未保存当前 DWG、未改正式图层、未删除实体。
7. **机器可读证据路径**：`output/validation_runs/object-family-sofa-replay-20260605-rcad/object_family_cad_replay_report.json`、`execution_summary.json`、`readback_entities.json`、`visual-review/visual_review_report.json`；截图 `output/previews/object-family-sofa-replay-20260605-rcad.png`；closeout `output/runs/object-family-sofa-replay-20260605-rcad-closeout/closeout_decision.json`。
8. **结论分类**：sofa 对象族真实 CAD replay 已落地（code + tests + real CAD + readback + screenshot visual aid + closeout，geometry_verified=是）。
9. **剩余风险**：这不是系统资产跨 DWG 复用 verified，不包含 precise sourceSpec / reuseReplay，不自动写规则、checker、资产或训练事实源；用户人工视觉验收仍未替代。
10. **能力证明附加项**：`capability_id=object_family.sofa.replay`；`claim_level=real_cad_replay_geometry_verified`；`geometry_verified=true`；`targetLayer=CODEX_PREVIEW`；`savedCurrentDwg=false`。
11. **覆盖率 / 表 C 写回**：本包不写 `cad_capability_registry`、不刷新 `cad_capability_coverage.json`、不提升表 C；证据只作为资产智能对象族 replay 的局部能力证明。
12. **最高触及 Ladder**：对象族 `draw_symbol_glyph` replay / closeout 证据；不声明 L3+ 施工图能力，不声明系统资产复用 verified。
---
## ASSET-PROMOTION-CANDIDATES-MVP-01
1. **包名**：`ASSET-PROMOTION-CANDIDATES-MVP-01`
2. **修改文件列表**：新增 `core/assets/promotion_candidates.py`、`tests/core/test_asset_promotion_candidates.py`；更新 `core/assets/__init__.py`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、状态、changelog、handoff 和 package index。
3. **关键设计说明**：按主计划 §0.1 在 sofa 对象族 no-CAD 试点后落地自动晋升候选。`build_asset_intelligence_promotion_candidates()` 从 ready trial 生成 task rule、checker、asset candidate、training item 四类候选，并输出 `promotionGate` 和 `review`，但不直接修改任何长期目标。
4. **新增/修改测试**：新增 `tests/core/test_asset_promotion_candidates.py`，覆盖 ready sofa trial 生成 review-only 候选、`mutatedTargets=[]`、training source 不更新、task rules / checker 进入 `needs_reviewed_package`，以及 source trial 不 ready 时阻断。
5. **实际运行的命令和结果**：先运行红测，失败于 `ModuleNotFoundError: No module named 'core.assets.promotion_candidates'`；实现后 `tests.core.test_asset_promotion_candidates` -> 2 OK；相邻回归 `tests.core.test_asset_promotion_candidates tests.core.test_object_family_trial tests.core.test_local_asset_rag tests.core.test_training_learning_promotion tests.core.test_plan_engine` -> 26 OK；真实仓库函数链 `trial -> build_asset_intelligence_promotion_candidates(trial)` -> `review_required 4 [] needs_reviewed_package`。
6. **是否运行真实 CAD**：否。本包只生成候选和 review gate；未连接 AutoCAD、未写 / 保存 DWG、未删除实体、未改正式图层。
7. **机器可读证据路径**：`core/assets/promotion_candidates.py`；`tests/core/test_asset_promotion_candidates.py`；运行时输出形态为 `asset_intelligence_promotion_candidates`。
8. **结论分类**：资产智能自动晋升候选已落地（code + tests + real repo function call，geometry_verified=否）。
9. **剩余风险**：候选仍需 `pipeline_learning_promoter` / reviewed package 审核；不会自动写规则、checker、资产或训练事实源。主计划下一项是真实 CAD replay 能力证明。
---
## OBJECT-FAMILY-SOFA-TRIAL-MVP-01
1. **包名**：`OBJECT-FAMILY-SOFA-TRIAL-MVP-01`
2. **修改文件列表**：新增 `core/assets/object_family_trial.py`、`tests/core/test_object_family_trial.py`；更新 `core/assets/__init__.py`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、状态、changelog、handoff 和 package index。
3. **关键设计说明**：按主计划 §0.1 在小型 RAG 之后落地 sofa 对象族 no-CAD 试点。`build_object_family_trial()` 当前只支持 sofa，先调用 `local_rag`，再生成 3 个设计候选、一个 `draw_symbol_glyph` CAD_PLAN 草案、dry-run 报告、执行计划和 readback 证据要求。非 sofa 请求返回 `unsupported_object_family`，防止 MVP 未审查泛化。
4. **新增/修改测试**：新增 `tests/core/test_object_family_trial.py`，覆盖 sofa 试点生成 RAG / 候选 / 有效 CAD_PLAN / dry-run / readback 合同，以及非 sofa 请求不生成 CAD_PLAN 完成声明。
5. **实际运行的命令和结果**：先运行红测，失败于 `ModuleNotFoundError: No module named 'core.assets.object_family_trial'`；实现后 `tests.core.test_object_family_trial` -> 2 OK；相邻回归 `tests.core.test_object_family_trial tests.core.test_local_asset_rag tests.core.test_plan_engine tests.core.test_semantic_asset_rules tests.core.test_system_asset_reuse` -> 32 OK；真实仓库调用 `build_object_family_trial('复用沙发时检查靠背、坐垫和扶手')` -> `cad_plan_draft_ready 3 valid not_executed_no_cad`。
6. **是否运行真实 CAD**：否。本包只生成 no-CAD 试点包、CAD_PLAN 草案和 dry-run；未连接 AutoCAD、未写 / 保存 DWG、未删除实体、未改正式图层。
7. **机器可读证据路径**：`core/assets/object_family_trial.py`；`tests/core/test_object_family_trial.py`；运行时输出形态为 `object_family_trial`。
8. **结论分类**：sofa 对象族 no-CAD 试点已落地（code + tests + real repo function call，geometry_verified=否）。
9. **剩余风险**：该包证明的是检索到草案和证据口径，不证明真实 CAD replay。主计划下一项是自动晋升候选；最终仍需真实 CAD replay 才能声明对象族能力证明。
---
## ASSET-LOCAL-RAG-MVP-01
1. **包名**：`ASSET-LOCAL-RAG-MVP-01`
2. **修改文件列表**：新增 `core/assets/local_rag.py`、`tests/core/test_local_asset_rag.py`；更新 `core/assets/__init__.py`、`CORE_RESTRUCTURE_PLAN.md`、状态、changelog、handoff 和 package index。
3. **关键设计说明**：按主计划 §0.1 先落地小型本地 RAG。`build_local_asset_rag_pack()` 只从系统资产 JSON、语义规则、Agent training memory 和项目失败样本做 lexical 检索，输出 source policy、scanned sources、source summary、引用片段和 evidence boundary。它显式排除 reference asset、外网、raw download 和 embedding index。
4. **新增/修改测试**：新增 `tests/core/test_local_asset_rag.py`，覆盖只读允许来源、不把 reference manifest 纳入 RAG、空仓库时保持 upstream context / not capability proof 边界。
5. **实际运行的命令和结果**：先用固定 Python 运行红测，失败于 `ModuleNotFoundError: No module named 'core.assets.local_rag'`；实现后 `tests.core.test_local_asset_rag` -> 2 OK；相邻回归 `tests.core.test_local_asset_rag tests.core.test_semantic_asset_rules tests.core.test_system_asset_reuse tests.core.test_training_learning_promotion` -> 30 OK；真实仓库函数调用 `build_local_asset_rag_pack('复用沙发时检查靠背和坐垫')` -> `ready`，sourceSummary 为 `system_asset=5, semantic_rule=1, training_memory=4, failure_sample=5, reference_asset=0`。
6. **是否运行真实 CAD**：否。本包只做本地上下文检索，不连接 AutoCAD、不写 / 保存 DWG、不删除实体、不改正式图层。
7. **机器可读证据路径**：`core/assets/local_rag.py`；`tests/core/test_local_asset_rag.py`；运行时输出形态为 `local_asset_small_rag_pack`。
8. **结论分类**：资产智能小型本地 RAG 已落地（code + tests，geometry_verified=否）。
9. **剩余风险**：RAG 结果只说明本地上下文被检索到；下一步仍需对象族试点，把检索结果接到设计候选、`CAD_PLAN`、执行计划和 readback 证据口径。真实 CAD replay 仍未做。
---

> 历史交接包已移入 `archive/2026-06.md`；当前窗口只保留最近资产智能链路的活跃包。
