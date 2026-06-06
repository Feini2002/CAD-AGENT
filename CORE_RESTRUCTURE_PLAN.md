# CAD Agent Core PlanMD（唯一主线）
最后更新：2026-06-06
状态：系统宪章 / 架构路由器版。Core 底座施工已收口；当前优先进入 **ARCH-CONVERGENCE-01 架构归并画布工程**，先把探索式长出的底座、训练、资产、多 Agent、模型桥和旧指标重新挂到统一任务生命周期，再恢复正式对象训练。

## 0. 本文职责

- 本文是唯一 `PlanMD`。用户说 `plan.md`、主计划、主 PlanMD、开发主线，默认指这里。
- 本文决定“下一类工作该走哪条架构路线”，不记录每个已完成包的长证据、单次训练流水、OpenSpec completed 任务列表或表 C 历史数字。
- 近期执行计数和用户口令镜像写入 `docs/planning/任务清单.md`；训练细节写入 `docs/training/**`；状态和风险写入 `docs/status/**`；机器证据在 `output/validation_runs/**`、`output/runs/**`。
- 改优先级或新增未来包时，先更新本文的路由 / 门槛，再更新对应台账；不得让辅助 MD 形成第二套 `next`、backlog 或退出标准。

## 0.1 主架构链路

```text
User Request / DWG / screenshot / feedback
  -> request context / run package
  -> semantic route
  -> Orchestrator Host / A-to-A contract
  -> required agents + hard gates
  -> CAD_PLAN / asset workflow / training route
  -> validate / dry-run / tool contract
  -> CODEX_PREVIEW or authorized system asset DWG
  -> created handles readback / audit / visual aid
  -> Reviewer Host / delivery claims
  -> learning promotion / sync / archive
```

长期主方向：以 `CAD Designer Agent` 为训练主体，以 Core + A-to-A + `CAD_PLAN` + 真实 CAD readback 为硬底座，把白话设计任务收束为可验证、可复训、可沉淀的 CAD 执行链路。当前短周期先暂停新的正式对象训练，做架构归并；训练恢复后继续保留 `Visual-First` / `visual_parts` / `reference_match` 边界。训练内容只在 `docs/training/**` 和 `docs/planning/任务清单.md` 展开；本文只保留训练边界、架构路由和退出标准。

## 0.2 ARCH-CONVERGENCE-01：架构归并画布工程

本工程是当前最高优先级。它不是改汇报措辞，而是把表 A/B/C、V-PROOF、RCAD、训练地图、资产、多 Agent、模型桥、Worker、截图和工作台归入统一任务生命周期。
总设计文档：`docs/architecture/system-architecture-convergence.md`。OpenSpec 契约：`openspec/changes/unify-system-architecture-canvas/`。七层画布为：系统入口、任务对象、决策编排、能力与证据、执行工具、审计修复、沉淀成长。
旧表 C 历史旧称“真实 CAD 实力”，现统一降级为 `Core Proof Coverage`：只说明底座证据覆盖，不代表 `Agent Task Maturity` 或 `Project Delivery Readiness`。
当前执行：先同步主控文档、规则、状态、训练入口和 OpenSpec；后续新对话按 OpenSpec `tasks.md` 审计 coverage / workbench / doc governance / A-to-A gate 等脚本。归并完成前，不默认新开正式训练、表 C 推进或系统资产大沉淀；用户明确覆盖时仍走 quick / focused / formal 边界。

## 1. 不可破坏边界

| 边界 | 固定要求 |
| --- | --- |
| Core 边界 | 本仓库是通用 CAD Agent Core Lab。可复用能力进 `core/`，共享资源进 `libraries/`，项目资料进 `projects/`，场景差异只放 `agents/<scenario>/`。 |
| CAD 执行 | 白话不得直接落 CAD；正式链路必须先有结构化意图或 `CAD_PLAN`，再走 validate、dry-run、`CODEX_PREVIEW`、created handles readback。 |
| 写入安全 | 默认不保存当前业务 DWG、不覆盖原图、不删未证据锁定对象、不改正式图层；局部错误优先原位 `repair_plan`。 |
| 模型型 Agent | 模型只做判断、复审、建议和工具请求；不能替代 CAD readback、sourceSpec、reuseReplay、表 C、删除范围门禁或用户验收。 |
| A-to-A | 高风险任务必须生成 `a_to_a_task_contract`，列出 required agents 和 hard gates；缺输出、缺字段或 gate fail 时只能 blocked。 |
| 系统资产 | reference/raw 只能作输入；`verified` 必须有 registry、native visible evidence、reuseWorkflowProbe 或 reuseReplay，不得用截图或 metadata-only 冒充。 |
| 训练 | `quick_trial` 不沉淀；`focused_retraining` 不扩大范围；`formal_acceptance` 才允许完整验收、promotion 和工作台同步。 |
| 证据 / 表 C | 截图、dry-run、fake driver、no-CAD draft、模型 pass、工作台页面都不能冒充真实 CAD 几何证明；表 A/B/C 三套口径不得互相替代。 |
| OpenSpec | 只作为单个复杂变更契约层，不承载第二套主计划、全局 backlog 或根级 `openspec/tasks.md`。 |
| 数据治理 | 训练收尾、系统资产、仓库级清理或正式工作台同步前后，必须保护 active fact source，先做 evidence-closure / retention dry-run。 |

## 2. 事实源地图

| 事实类型 | 主入口 |
| --- | --- |
| 全局规则 | `AGENTS.md`、`docs/governance/cad-agent-rules.md` |
| 短上下文 | `CORE_CONTEXT_BRIEF.md` |
| 唯一主计划 | `CORE_RESTRUCTURE_PLAN.md` |
| 执行台账 / 用户口令 | `docs/planning/任务清单.md` |
| 训练路线 | `docs/training/README.md`、`docs/training/cad-designer-growth-path.md`、`docs/training/training-sources.json` |
| Agent / 模型桥 | `agents/pipeline/pipeline_manifest.json`、`agents/pipeline/README.md`、`core/model_review/prompt_packs/**`、`core/model_review/**`、`core/orchestrator/local_live_model_bridge*.py` |
| 系统资产 | `libraries/system_library/registry.json`、`libraries/system_library/**/assets.json`、`*_assets.dwg` |
| 当前状态 / 风险 | `CORE_STATUS.md`、`docs/status/current.md`、`docs/status/issues.md` |
| 历史流水 / 交接 | `docs/status/changelog.md`、`docs/handoffs/current.md`、`docs/handoffs/package-index.md`、`docs/handoffs/archive/**` |
| 机器证据 | `output/validation_runs/**`、`output/runs/**`、coverage JSON、model trace JSON |
| 复杂变更契约 | `openspec/changes/<change>/**` |

## 3. 未来开发路由

| 路由 | 触发条件 | 退出标准 |
| --- | --- | --- |
| 架构归并画布 | 当前仓库级主工程；旧表格、训练、资产、多 Agent、模型桥和工作台已分片生长，需要统一主构图 | `docs/architecture/system-architecture-convergence.md`、`CORE_RESTRUCTURE_PLAN.md`、状态 / 规则 / 训练入口同步；OpenSpec `unify-system-architecture-canvas` valid；关键脚本审计完成并阻止旧“真实 CAD 实力”作为端到端能力主叙事 |
| 模型型 Agent 本地硬化（网络外） | 网络 / OpenAI provider 暂不可用，但需要先加固模型桥数据边界、可审计决策链、Agent 连续性、ToolIntent fixture 和 closeout 状态机 | 按 `docs/architecture/model-agent-local-hardening-plan.md` 完成本地 no-network proof：`export_manifest` 阻断未授权上下文、repo-external cwd / context leak audit 可测、`handoff_packet` 全链路可引用、错误 taxonomy 清晰、closeout state machine 不越权放行；不要求真实模型或真实 CAD。 |
| Worker 编排 + 本地活体模型桥 MVP | 需要先打好长期远程触发、多状态机、队列、retry、heartbeat 和多 Agent 依赖编排框架，再证明至少一个模型型 Agent 真正调用 `gpt-5.5`，并把 prompt / context / schema 输出接回系统 decision | 架构记录已从独立 MD 收口到本文和 `core/orchestrator/local_live_model_bridge*.py`。当前本地 stand-in 已覆盖 run id、task envelope、bridge 注册 / lease / heartbeat / submit、idempotency、timeout / retry、circuit breaker、security gate、single-agent live、multi-agent live、CAD preview-only Tool Contract 和分层诊断；运行能力必须由 feature gates 分层放行。后续真 Worker 版仍需迁移到 Cloudflare Worker / Durable Object / Queue，并保持同一 `worker_orchestration_ready -> local_bridge_connected -> single_agent_live -> multi_agent_live -> cad_mcp_preview_live` 完成声明。 |
| 模型型 Agent 活体协作证明 | 设计判断、主观复审、复杂分流或多 Agent 依赖链 | 下游 `agent_outputs/*.json` 显式引用上游输出；schema、trace、blocked 原因和 closeout gate 可审计；模型不越权执行 CAD；活体调用证明按 `single_agent_live` / `multi_agent_live` / `cad_mcp_preview_live` 分层声明。 |
| 资产智能 verified reuse | 用户要求调用 / 复用 / 沉淀系统资产，或语义强匹配系统库 | 有 sourceSpec、native evidence、reuseWorkflowProbe 或 reuseReplay、created handles readback；`savedCurrentDwg=false`；候选不能冒充 verified。 |
| 高风险 A-to-A hard gate 实战化 | 资产沉淀、资产 DWG 仓库布局、删除 / 局部修复、视觉验收、正式工作台收尾 | `a_to_a_task_contract` 覆盖 required agents；缺任一 hard gate 输出即阻断；视觉截图不能替代非截图证据。 |
| 证据与数据治理 | 文档 / output 膨胀、路径断链、派生快照堆积、资产或训练收尾 | retention / evidence-closure dry-run 分类 `protected/candidate/blocked/derived`；不删除 active fact source，不让 `report_path_missing` 变差。 |
| 真实案例 / 复合任务小闭环 | 用户给 DWG、截图、对象组合、修改 / 标注 / 尺度推断类任务 | 声明 evidence_source；走结构化意图或 `CAD_PLAN`、validate、dry-run、`CODEX_PREVIEW`、readback、audit、必要局部修复和反馈闭合。 |
| 表 C / 真实 CAD 回归 | 改 capability registry、showcase、验证证据、真实 CAD 能力口径 | 复跑 coverage；真实 CAD 能力只按 registry + evidence + coverage JSON；`刷新表 C` 只跑 coverage，不新开包。 |
| 文档治理 | 活跃控制文档超预算、入口漂移、历史包回流到主计划 | `scripts/run_doc_governance_audit.py --fail-on-findings` 通过；完成细节迁往 changelog / handoff / history / output。 |

`docs/planning/post-backlog.md` 只保留旧后置包和历史索引语义；新的未来路线以本文 §3 和 `docs/planning/任务清单.md` 为准。

### 3.1 Worker 编排 + 本地活体模型桥剩余执行清单

原独立本地活体模型桥架构 MD 已删除，剩余路线只在本文维护：

- **Cloudflare 迁移**：把当前本地 stand-in 状态机迁移到 Worker API + Durable Object run state；Queue / Workflows 可后接，但必须保留 lease、heartbeat、timeout、retry、audit event、idempotency 和 `featureGates` 语义。
- **Bridge 安全配置**：建立 bridge-owned `CODEX_HOME` / Codex config，避免 `--ignore-user-config` 连带丢 MCP 配置；Worker 永远只传 task envelope，不传 shell 命令。
- **真实活体复验**：每次声明 `single_agent_live` / `multi_agent_live` 都必须有 `traceRef` 指向完整 trace 包，且 diagnostics 能验证 `trace_review.json`、`trace_manifest.json`、sanitized `codex.cmd exec --model gpt-5.5`、`normalized_output.json.modelProviderStatus.route=codex_cli_local`。
- **CAD preview 证明分层**：`fake_driver_preflight` 只能给 `runtimeStatus=completed`、`proofStatus=not_verified`；只有真实 CAD / CAD-MCP created handles readback 通过，才能把 `cad_mcp_preview_live` 的几何证明说成 verified。
- **生产保护**：DLQ / backpressure / kill switch / 日志脱敏 / bridge token / replay 防护仍是 Cloudflare 版本上线前硬门槛；这些保护不被本地 fixture pass 替代。

## 4. Decision Gates

| Gate | 默认判定 |
| --- | --- |
| 保存 / 覆盖当前业务 DWG | 默认禁止；只有用户明确授权且证据链通过才允许。 |
| 删除 / 修改实体 | 只限 `CODEX_PREVIEW` 中被 handles、bbox、图层和错误原因锁定的对象；不得扩大到全模型空间。 |
| 正式图层 / 原图 | 默认不改；需要单独授权和回读证据。 |
| 自动读图 / 截图推断 | 只能作为视觉定位或推断；不能替代 DWG handles、CAD_PLAN 或真实尺寸 readback。 |
| 公司块库 / 系统资产库 | 必须先过 sourceSpec、encodingPreflight 和资产边界；来源不清只能 candidate / metadata-only。 |
| 方案自动落 CAD | 先生成结构化方案和 `CAD_PLAN`；validate / dry-run / hard gate 失败不得执行。 |
| 真实项目样本 | 优先只写 `CODEX_PREVIEW`；用户业务 DWG 不保存、不覆盖。 |
| 模型调用 | 只读判断 / 建议 / 工具请求；工具执行仍受确定性 gate 控制。 |
| 系统资产 DWG 写入 | 只对授权的 `libraries/system_library/**/**/*_assets.dwg` 生效，不扩展到当前业务 DWG。 |

## 5. 执行入口

固定 `$py="$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"` 后按需运行：

- 文档治理：`& $py scripts\run_doc_governance_audit.py --fail-on-findings`
- 自检：`& $py scripts\self_check.py`
- 表 C：`& $py scripts\run_capability_coverage.py --output output\validation_runs\capability-lab\cad_capability_coverage.json`
- A-to-A gate：`& $py scripts\run_a_to_a_orchestration_gate_check.py`
- 截图 / CAD 环境预检：`& $py scripts\render_preview.py --check`
- 本地活体模型桥分层诊断：`& $py scripts\diagnose_local_live_model_bridge.py --run-dir <run_dir>`
- OpenSpec：`openspec.cmd list --json`、`openspec.cmd validate --all --strict --json --no-interactive`

## 6. 完成声明标准

- 普通文档 / 代码治理：说明改动范围，跑对应审计 / 测试；没跑就标 `not_run`。
- 可见 CAD 输出：必须有 `CAD_PLAN` 或结构化意图、validate、dry-run、`CODEX_PREVIEW`、handles readback、截图辅助和差异说明。
- 模型型 Agent：必须有 trace、schema、provider status、tool contract 和 closeout gate；活体调用还必须证明 `modelInvoked=true`、`modelUnavailable=false`、`schemaValid=true`，模型 pass 不能替代确定性证据。
- 系统资产：必须说明 lifecycle、sourceSpec、native evidence、reuse probe / replay、保存边界和当前 DWG `savedCurrentDwg=false`。
- 训练：只按 `docs/training/**` 的 quick / focused / formal 路由收尾；本文不展开训练项。
- 表 C：只引用 coverage JSON 机器值，不用工程进度、截图或 no-CAD benchmark 暗示真实 CAD 能力。
- 架构归并：必须说明七层画布、旧模块归位、三类成熟度口径、训练暂停 / 恢复条件和脚本审计结果；文档清晰不等于 Agent 能力提升。

## 7. 历史归档

| 历史内容 | 存放处 |
| --- | --- |
| 旧 Lab 施工包 / Phase 明细 | `docs/planning/archive/**`、`docs/status/changelog.md`、`docs/handoffs/archive/**` |
| 旧主计划瘦身快照 | `docs/history/snapshots/**` |
| OpenSpec completed 任务 | `openspec/changes/<change>/**` 或归档后的 OpenSpec history |
| 单次运行证据 | `output/validation_runs/**`、`output/runs/**` |
| 最近接手窗口 | `docs/handoffs/current.md` |
