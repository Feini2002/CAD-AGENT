# 全局流水线 Agent（`agents/pipeline/`）

本目录是 **多 Agent CAD 系统的角色注册表**，不是第二套 Core。

**精度优先：** 不准就不交付。见 [`docs/training/precision-first.md`](../../docs/training/precision-first.md)。

## Agent 类型认知

这里的 Agent 分三层理解：

- **契约型 Agent**：`agent.json`、manifest 和 A-to-A hard gate 定义责任、输入、输出和阻断条件；它能被机器检查，但不一定独立调用模型。
- **规则型 Agent**：由 `core/`、`scripts/` 和审计器执行确定性检查，例如编码、handles、bbox、layer、保存状态、sourceSpec 和 reuse probe。
- **模型型 Agent**：显式通过 `core/model_review` 调用 `codex.cmd exec` 或未来 SDK 桥，对截图 / readback / plan 做只读判断，并输出 schema 化 JSON。

当前模型桥策略已按“准确性优先，不按额度分档”扩展登记。`pipeline_visual_layout_reviewer` 和 `pipeline_visual_acceptance_reviewer` 仍是视觉复审主入口：前者用于系统资产 DWG / 仓库式布局，识别“仓库太挤、通道不清、source/proof 角色混淆”等问题；后者用于普通 CAD 训练 / 落图后的用户可见验收，识别“截图看起来像乱码、文字贴边、遮挡、裁剪、不对齐、美观度不足、不可复用”等规则指标难以完全覆盖的问题。它们都不能写 CAD、不能保存 DWG，也不能替代 CAD readback、资产复用 replay 或用户验收。

第 3 包把模型辅助范围扩展到 `pipeline_asset_governor` 和 `pipeline_repair`：前者只记录 `modelAssistedDecision`，辅助分类、来源边界和 clean source 建议；后者只接收 `modelBackedRepairPlan` / `repairPlanCandidate`。这两类输出都必须保持只读建议，不能覆盖规则门禁，不能直接执行 CAD 命令、删除实体或保存 DWG。

当前长期规则记录见 [`CORE_RESTRUCTURE_PLAN.md`](../../CORE_RESTRUCTURE_PLAN.md)。`pipeline_manifest.json` 的 `model_bridge_expansion` 是机器可读登记，`core/model_review/prompt_packs/manifest.json` 的 `packs` / `plannedPacks` 是 Prompt Pack 实施队列；当前已有 9 个 Prompt Pack ready，其中设计三节点已从 `plannedPacks` 升级为 ready。

## 5.5 模型桥扩展节点

| 优先级 | Agent | 使用场景 | 状态 |
| --- | --- | --- | --- |
| P0 | `pipeline_visual_acceptance_reviewer` | CAD 输出截图后、交付前、训练验收前、修复后 | Prompt Pack ready |
| P0 | `pipeline_delivery` | 最终回复前、closeout 前、是否请用户验收 | Prompt Pack ready |
| P0 | `pipeline_repair` | 用户说不对、机器审计失败、模型视觉复审失败 | Prompt Pack ready |
| P0 | `pipeline_orchestrator` | 复杂任务、训练收尾、资产沉淀、复合任务分发 | Prompt Pack ready |
| P0 | `pipeline_design_director` | 场景 brief 后、CAD_PLAN 前、复杂设计任务分发前 | Prompt Pack ready |
| P0 | `pipeline_style_generator` | 新样式、新尺寸表达、图纸表达方案、多候选 | Prompt Pack ready |
| P0 | `pipeline_design_reviewer` | CAD readback 后、用户验收前、候选对比后 | Prompt Pack ready |
| P1 | `pipeline_visual_intent` | 参考图、截图、风格目标、视觉对象拆解 | planned |
| P1 | `pipeline_intent` | 白话转结构化意图 / `CAD_PLAN` 前 | planned |
| P1 | `pipeline_audit` | 机器审计后、closeout 前、训练 pass 候选 | planned |
| P1 | `pipeline_asset_governor` | 资产沉淀、来源边界、clean source 判断 | Prompt Pack ready |
| P1 | `pipeline_asset_dwg_curator` | 系统资产 DWG 排版、仓库货架、native 可见面板 | planned |
| P1 | `pipeline_visual_layout_reviewer` | 资产库 DWG / 仓库式布局视觉复审 | Prompt Pack ready |
| P2 | `pipeline_context_curator` | 中断恢复、长历史、训练 / 资产上下文起点 | planned |
| P2 | `pipeline_asset_retriever` | 资产检索、参考图库、历史案例匹配 | planned |
| P2 | `pipeline_asset_librarian` | 资产分类、命名、去重、registry 更新 | planned |
| P2 | `pipeline_asset_reuse_auditor` | 资产复用 probe / replay / claim 审核 | planned |
| P2 | `pipeline_learning_promoter` | 训练通过、失败复盘、Prompt / memory 沉淀 | planned |
| P3 | `pipeline_execute` | CAD_PLAN 执行前安全守卫 | guard-only |

## 模型桥 Agent 自动成长

所有 `ready`、`planned` 或 `guard-only` 的模型桥 Agent 都是可自动升级的训练目标。每次模型调用都必须进入 trace；每次 `model_fail`、`schema_invalid`、用户反馈 fail、机器审计 fail、closeout blocked 或修复成功，都要产出 `learningCandidate` 或显式 `not_required`。可沉淀经验由 `pipeline_learning_promoter` 写入责任 Agent 的 `training_memory.json` / `prompt_addendum.md`，并在需要时提出 checker、base rule、task rule 或原任务回测请求。

模型桥学习只提升 Agent 判断和 Prompt 质量；不提升表 C，不替代 CAD readback，不替代 sourceSpec / reuseReplay，不替代用户验收。

自适应能力成长复训只允许把可审计 lesson 作为上游输入。`growth_replay` 需要 repo-local active / protected profile source、正反例、required / observed features、表达比较和原任务回测边界；debug、derived、external、missing source、截图或模型 pass 不能作为 hard baseline。模型型 Agent 可以提出 lesson candidate 或复审表达是否退化，但不能把候选直接写入规则、checker、Agent memory、训练事实源、Worker 或表 C。

主 Agent 认知提升必须可观察：如果一次改动没有改变 `pipeline_orchestrator` 的 route、dispatch、requiredAgents、tool choice、blocking reason、learningCandidate 或下一次 replay 结果，就只能称为机制建设，不能称为主脑变聪明。

## 当前真实度分层

当前系统已经越过“只有死规则”的阶段，但还没到“所有 Agent 都真实独立协作”的终态。后续判断 Agent 是否真实，统一按这四层表达：

| 层级 | 含义 | 不能声称 |
| --- | --- | --- |
| 契约存在 | `agent.json` / manifest / hard gate 已登记 | 不能说模型已参与判断 |
| Prompt Pack ready | 有 prompt、schema、negative examples 和 converter | 不能说已在真实任务中协同 |
| 单 Agent 模型调用 | 某个 Agent 有 `modelInvoked=true` trace 和 schema 校验 | 不能说多 Agent 已互相读取 |
| 多 Agent 活体协作 | 下游读取上游 `agent_outputs/*.json`，payload / prompt / trace 可看到上游路径、摘要或 hash | 仍不能替代 CAD readback / 用户验收 |

当前 no-CAD / no-save MVP 已有 Core 入口：`core.orchestrator.model_agent_chain_runtime.run_no_cad_model_agent_chain()`。它证明上游互读和只读模型链路，不证明真实 CAD 几何。

## Worker 编排 + 本地活体模型桥优先路线

当前长期路线已收口到 `CORE_RESTRUCTURE_PLAN.md` §3 / §3.1 和 `core/orchestrator/local_live_model_bridge*.py`：第一步先用本地 stand-in 固定 `run_id`、`task envelope`、状态机、bridge lease / heartbeat / submit、trace diagnostics 和 feature gates；第二步迁移到 Cloudflare Worker / Durable Object / Queue；第三步再证明 `single_agent_live`：一个指定 Agent，例如 `pipeline_design_director`，真实经本机 `codex.cmd exec --model gpt-5.5` 获取 schema-valid JSON，并把结果写回 `agent_outputs/<agent_id>.json`，供系统继续 decision。

完成声明分层：`worker_orchestration_ready` 只证明 Worker run package / 状态机 / 队列合同成立；`local_bridge_connected` 只证明 Worker 能把任务交给本地 bridge 并收回状态；`single_agent_live` 才证明 GPT-5.5 被真实调用。活体调用必须同时满足 `modelInvoked=true`、`modelUnavailable=false`、`schemaValid=true`、`modelProviderStatus.route=codex_cli_local`，并且 `traceRef` 必须指向完整 trace 包：Worker run state、sanitized `codex.cmd exec --model gpt-5.5` command、prompt、schema、last message、normalized output、trace manifest 和 trace review。缺这些证据时，只能称为契约型、规则型、Prompt Pack ready 或 fixture proof。

接入 CAD-MCP 时，优先使用 bridge-owned Codex config，而不是依赖用户级坏配置；`--ignore-user-config` 可能会同时忽略 MCP 配置，不能无脑作为长期方案。Cloudflare Worker / Tunnel 是长期编排入口，但不能替代本地 bridge、Codex CLI、MCP、CAD readback 或 Tool Contract，也不能成为任意 shell 代理。

## 模型调用触发策略

不是把每个请求都打给 5.5。规则层先做轻量分流，Orchestrator Host 会写 `model_trigger_decision.json`；只有这些场景默认触发模型型 Agent：

- 语义模糊，需要先拆用户真实意图。
- 设计判断、创意表达、风格取舍、A/B/C 或候选数量需要专业判断。
- 用户反馈里有“看着不对、不高级、太乱、不像专业图纸”等主观质量问题。
- 机器审计绿了，但截图 / readback 暴露视觉、可读性或专业表达风险。
- 交付前需要判断“已经证明什么、不能说什么、是否该请用户复审”。

普通状态 / 进度查询、明确小修、编码门禁、registry 检索、validate、dry-run、created handles readback、bbox / layer / overlap 审计等确定性任务继续走规则型 Agent。模型不可用时必须返回 `modelProviderStatus=unavailable`，不能把未调用包装成主观判断。

## Dispatch Runner MVP

模型调用版 runner 当前以 Core API 落地：`run_prompt_pack_review()` 调用 Prompt Pack / schema / Codex CLI bridge，Orchestrator Host 和 no-CAD chain runtime 负责把 run package、Agent id、`rule_context_pack`、上游 `agent_outputs/*.json` 和 evidence bundle 拼进 payload；输出统一写入 `output/runs/<run_id>/agent_outputs/<agent_id>.json` 与 trace 目录。CLI 形式 `--invoke-model` 仍可后续薄封装。

runner 必须记录：sanitized `codex.cmd exec` 命令、prompt、schema、stdout / stderr、last message、normalized JSON、schema 校验、`modelInvoked`、`modelProviderStatus`、失败原因、`learningCandidate` / `not_required`、`trace_review.json` 和 `trace_summary.md`。下游 Agent 只能读取上游 JSON 后继续判断；缺上游、schema invalid、provider unavailable 或 evidence 不足时，合同进入 `blocked` / `needs_more_evidence`。

## Tool Contract ReAct

模型型 Agent 可以在 strict JSON 中附带可选 `toolIntent`，但这只表示“请求工具”，不代表工具已经执行。统一契约为 `core/schemas/tool_intent.schema.json`，运行痕迹为 `core/schemas/tool_trace.schema.json`；Orchestrator 通过 `core.orchestrator.tool_contract` 先做 schema / 权限 / 风险 / target scope gate，再写 `tool_traces/<agent>.<intent>.json` 供下游读取。

P7 只记录工具意图时，allowlisted read-only intent 的 trace 状态是 `allowed_not_executed`。P8 开始，no-CAD chain 可以通过 `run_tool_intent()` 执行受控 Stage 1/2 工具：Stage 1 只读读取 run package、rule context、schema、上游 agent outputs 和 trace summary；Stage 2 只写当前 run 的 `candidate_outputs/`，例如候选 `agent_outputs`、draft intent、CAD_PLAN candidate 和 learningCandidate。P9 已接入 Stage 3 确定性验证工具：`validate_plan`、`dry_run` / `dry_run_plan`、`preview_only_audit` 和 `closeout_gate`。模型型 Agent 只能请求验证，验证结论以工具 JSON 为准；验证 trace 会把 `reportPath` 和 `resultStatus` 放入下游 evidence bundle。

高风险工具缺 `targetScope`、模型直接要求保存当前 DWG、删除实体或修改正式图层，都会在执行前 blocked。Stage 2 候选写入不能改 registry、training source、表 C 或系统资产 verified 状态；Stage 3 验证 pass 也只证明 schema / dry-run / audit / closeout JSON 通过，不能替代 CAD write、created handles readback、截图辅助、用户验收或表 C。Stage 4 受控 CAD 工具已限定为 Orchestrator 执行 `preview_cad_execute` / `execute_cad_plan_preview`：必须先有同一 CAD_PLAN 的 validate + dry-run pass 报告，只写 `CODEX_PREVIEW`，输出 execution/readback/tool report，保持 `savedCurrentDwg=false`；fake-driver preflight 不证明真实 CAD geometry。

## 设计智能链路

上一版模型桥重点补的是复审、修复和交付；现在补齐前半场设计链。主 Agent 应先像专业设计师一样理解场景，而不是只把白话转 CAD_PLAN：

```text
场景 brief
-> pipeline_design_director：判断图纸类型、表达目的、设计意图、约束和分发对象
-> pipeline_style_generator：按语义 waiver / 生成单方案 / 生成 2-3 套参数化候选
-> pipeline_visual_intent / pipeline_intent：把选定候选落成 visual_parts / intent / CAD_PLAN
-> pipeline_execute：真实落图
-> CAD readback / audit / visual acceptance
-> pipeline_design_reviewer：复核是否像专业图纸、是否可读、是否符合场景目的
-> pipeline_learning_promoter：把错误和正确经验沉淀
```

设计链路不能替代 CAD readback；它的产物必须可被下游转成结构化参数、validate、dry-run 和 `CODEX_PREVIEW` 证据。

## 模型型运行时升级方向

当前阶段不是“所有 Agent 都已经独立通过 CLI 对话”。已经落地的是模型复审桥、schema 输出槽位、文件化 Trace / 自动复盘摘要、`output/runs/<run_id>/state.json` 运行包状态机、确定性 `closeout_decision.json` 门禁、`delete_scope_gate.json` / `neighbor_protection.json` 生成器、9 个真实 Prompt Pack、`rule_context_pack`、`model_trigger_decision.json`、Tool Contract ReAct schema / gate、Orchestrator Host runtime、no-CAD model Agent chain runtime、Reviewer Host closeout runtime，以及工作台“模型 Trace”派生视图；多数 Agent 仍是契约型或规则型。后续模型型升级记录以 `CORE_RESTRUCTURE_PLAN.md` 为主入口；工作台只显示派生快照，不替代 run package、trace JSON、CAD readback 或用户验收。

目标形态：

- `pipeline_orchestrator` 升级为 **Orchestrator Host**：接收 run package，通过 `codex.cmd exec` 输出 `dispatch_plan.json`、`task_contract.json`、required agents 和 risk assessment。
- `pipeline_delivery` / 复审链路升级为 **Reviewer Host**：读取截图、readback、CAD reports、visual acceptance output 和 repair history，输出 `closeout_decision.json`，决定能否交付。
- 模型型子 Agent 统一经 `core/model_review` 调用本地 Codex CLI 或未来 SDK 桥；输出必须是 strict JSON，并经过 schema、provider status 和 A-to-A hard gate。
- 每次模型型调用必须有 trace：agentId、taskType、prompt、schema、sanitized command、stdout/stderr、events、last message、normalized output、modelProviderStatus、gate decision、`trace_review.json` 和 `trace_summary.md`。
- 多 Agent 活体协作必须证明“下游读了上游”：payload / prompt / trace 里要能看到上游 `agent_outputs/*.json` 的引用、冲突处理和互审结论。

事实源边界：

- 长期事实源是 `output/runs/<run_id>/**`、`output/model_reviews/traces/**`、训练 / 资产 / 状态 JSON 与 Markdown reports；run package 的 `state.json` 必须能说明当前阶段、阶段输入、阶段输出和阻断原因。
- `capability-map-data.js` 和 `capability-map.html` 只展示派生状态，不得作为 Agent 调用证据或训练事实源。
- 缺 trace、缺 required Agent output、缺 visual acceptance closeout、缺删除范围 gate 或缺邻区保护时，focused / formal CAD 可见交付必须保持 `blocked` / `not_verified`。

## 全局 Agent

| ID | 职责 |
| --- | --- |
| `pipeline_context_curator` | 收束上下文、案例状态和历史噪声 |
| `pipeline_asset_retriever` | 在 CAD_PLAN 前产出 `retrieval_pack` |
| `pipeline_asset_governor` | 资产库守门员，沉淀前判断能否进库、派哪些子 Agent、是否还需润色加固 |
| `pipeline_asset_librarian` | 资产馆员，管分类、命名、去重、检索词、状态和资产卡片 |
| `pipeline_asset_dwg_curator` | 资产 DWG 编排员，管分区排版、训练污染清洗、槽位和 native 写入证据边界 |
| `pipeline_asset_reuse_auditor` | 资产复用审计员，管复用回放、created handles、readback 和 verified 门禁 |
| `pipeline_orchestrator` | 编排轮次，禁止亲自落图 |
| `pipeline_visual_intent` | 参考图 / 样式目标 → `visual_parts` |
| `pipeline_visual_layout_reviewer` | 系统资产 DWG / 仓库式布局的视觉复审把关 |
| `pipeline_visual_acceptance_reviewer` | 普通 CAD 输出的模型型视觉验收复审，把关乱码、遮挡、裁剪、对齐、美观度和可复用边界 |
| `pipeline_intent` | 白话 → `intent.json` + checklist |
| `pipeline_execute` | 落 `CODEX_PREVIEW` |
| `pipeline_audit` | `training_geometry_audit` + checklist |
| `pipeline_repair` | 读 failures，最小修复，回环 |
| `pipeline_delivery` | 截图 + 自检 + 请你 feedback |
| `pipeline_learning_promoter` | training-sources、ledger、Agent memory / Prompt addendum 的沉淀边界 |

清单：`pipeline_manifest.json`
架构说明：`docs/training/global-agent-pipeline.md`

## 数据防膨胀协同

训练、复训、工作台同步、系统资产沉淀或仓库级治理会产生大量 output / debug / test artifacts 时，不新增临场 Agent；由已登记 Agent 共同承担 `data_bloat_governance`：

- `pipeline_context_curator`：识别 active `fact_source`、历史引用根和当前工作区已有证据。
- `pipeline_audit`：核对 protected / candidate / blocked / derived 分类，发现断链或仍被引用的清理候选时阻断。
- `pipeline_learning_promoter`：确认 learning ledger、Agent memory / Prompt addendum 和 training-sources 的事实源边界没有被诊断报告污染。
- `pipeline_delivery`：交付时只汇报 dry-run / audit 摘要，不把 retention report、data-bloat audit 或 workbench sync report 当成训练通过证据。

## 主 Agent 派发边界

`pipeline_orchestrator` 是主编排 Agent。它的“自我意识”只表示工程上的可审计自我模型：知道自己负责分流、拆任务、生成 `a_to_a_task_contract`、加派已登记 Agent、收 hard gate 输出，并在证据不足时阻断完成口吻；它不亲自替代 CAD 执行、资产守门、复用审计或视觉布局复审。

高风险任务会在合同里写入 `mainAgentSelfCheck` 和 `dispatchDecision`。主 Agent 只允许自动加派 manifest 已登记 Agent；未登记的新 Agent 只能作为 `additionalAgentRequests`，进入 `needs_reviewed_package` / `needs_openspec_change`，不得临场生效。

## 与场景 Agent 的关系

- **全局 Agent**：任何 `projects/<case>/` 共用，调用 `core/`
- **场景 Agent**（`agents/residential/` 等）：只给 Intent 提供词汇与偏好，**不**实现 COM/审计

## 当前阶段

**Phase A（现在）：** 一个交互式 Agent 会话按角色分步；Codex、Cursor 或同类工具均可，产物路径与本 manifest 一致。
**Phase B：** 每角色独立 agent rule / skill / 配置，Orchestrator 派发；具体载体不绑定单一软件。
**Phase C：** SDK 自动化 + `runs/state.json` 状态机。

## 边界

遵守 `agents/SCENE_AGENT_RULES.md`：**本目录不得出现 `*.py`**。
