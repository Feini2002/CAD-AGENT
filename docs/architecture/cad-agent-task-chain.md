# CAD Agent 系统任务链路

最后更新：2026-06-02

## 目标

本文把两条必要链路合并为系统默认流程：

- **执行编排链路**：白话需求 -> Agent 语义拆分 -> 规则匹配 -> 复杂任务拆成单一子任务 -> 分发 -> 执行 -> 审计 -> 交付。
- **训练学习链路**：训练计划 / 精准复训 -> 机器校验 -> 原任务回测 -> 底座规则 / 单一任务规则同步 -> A-to-A 校准 -> 事实源同步。

两条链路互相补充。执行链路保证当轮任务不从白话直接跳 CAD；训练链路保证失败和新能力不会只停留在一次对话、截图或临时脚本里。

## 总链路

```text
用户白话 / 截图 / DWG 上下文
  -> 0. 输入分流
  -> 1. 语义拆分
  -> 2. 复杂任务拆成单一子任务
  -> 3. 按规则分发给责任 Agent / Core 入口
  -> 4. 执行前门禁
  -> 5. CAD / 资产 / 文档执行
  -> 6. 机器回读 + 视觉辅助审计
  -> 7. 聚合交付或局部修复
  -> 8. 失败 / 新模式回流训练
  -> 9. 底座规则 + 单一任务规则 + A-to-A 校准同步
  -> 10. 事实源 / 工作台 / 状态文档同步
```

## 0. 输入分流

第一步先判断用户语义属于哪类路线，不能直接按最近脚本执行。

| 路线 | 触发语义 | 默认动作 |
| --- | --- | --- |
| `quick_trial` | 试一下、快画、先看看、不沉淀 | 最小结构化意图 + 预览层写入 + 关键 readback |
| `ordinary_execution` | 普通绘图、修改、标注 | 结构化意图 / `CAD_PLAN` + validate / dry-run + 执行审计 |
| `asset_reuse` | 调用、复用、插入、放一个已沉淀对象，或强匹配系统资产 | 查系统资产库，生成跨 DWG 复用 workflow |
| `asset_sedimentation` | 沉淀、收进资产库、通用资产 | 走系统资产四件套，必要时保存并打开系统资产 DWG |
| `focused_retraining` | 训练某项、任务 X、加深、某图案比例 | 只覆盖点名能力，记录 `scope.mode=focused` |
| `formal_acceptance` | 验收、训练通过、记入工作台、整批、推进表 C | 完整校验、证据、同步和状态回写 |
| `local_repair` | 不对、这里错、继续修、局部反馈 | 优先按 handles / bbox 原位局部修复 |

若路线不确定，先返回 `needs_confirmation` 或保守走普通结构化意图；不得把轻量试画静默升级成整批训练，也不得把资产强匹配静默改成临场重画。

## 1. 语义拆分

语义拆分要把白话转换成可检查字段：

- 输入来源：截图、当前 DWG、created handles、选中对象、用户给定尺寸、系统资产库。
- 目标对象：要画、要改、要复用、要沉淀、要训练、要审计的对象。
- 证据边界：截图推断、比例估算、真实 DWG readback、用户明确尺寸、not_checked。
- 安全边界：是否允许删除、是否保存、是否写正式图层、是否跨 DWG、是否打开系统资产 DWG。
- 规则命中：训练轻重链路、资产复用规则、系统资产沉淀协议、原位局部修复、中文编码前置门禁。

输出可以是 `CAD_PLAN`、`retrieval_pack`、`system_asset_reuse_workflow`、`repair_plan`、focused training scope 或文档任务计划，但必须是结构化结果，不能只保留一段白话解释。

## 2. 复杂任务拆成单一子任务

复合任务先拆成可分发的单一子任务，每个子任务至少带这些字段：

| 字段 | 含义 |
| --- | --- |
| `taskId` | 稳定编号，便于审计和回测 |
| `kind` | `semantic_intent` / `asset_reuse` / `cad_plan_draw` / `local_repair` / `focused_retraining` / `documentation_sync` 等 |
| `ownerAgent` | 责任 Agent 或 Core 入口 |
| `inputs` | 白话片段、handles、bbox、资产 id、截图、DWG 上下文 |
| `rules` | 本子任务必须遵守的规则文档或机器规则 |
| `evidenceRequired` | 需要 validate、dry-run、readback、截图、Agent review 还是用户反馈 |
| `allowedWriteScope` | `CODEX_PREVIEW`、系统资产 DWG、文档、无写入等 |
| `blockedReason` | 阻断原因，不能用空结果代替失败 |

单一子任务之间可以串联，也可以并行评审，但最终必须由 Orchestrator 聚合状态：`completed`、`partial`、`blocked`、`needs_confirmation`。

## 3. 分发和责任

| 责任层 | 主要职责 |
| --- | --- |
| Orchestrator | 分流、拆任务、收敛状态，禁止跳过结构化意图直接落 CAD |
| Intent Agent | 白话、截图、场景词汇和约束拆成 intent / `CAD_PLAN` |
| Asset Agent | 查 `libraries/system_library/registry.json`，处理候选、来源门禁和跨 DWG 复用 |
| Execute Agent / Core | 只读结构化输入，写 `CODEX_PREVIEW` 或授权的系统资产 DWG |
| Audit Agent | 对照 intent / CAD_PLAN / handles / readback 做机器审计和视觉辅助复核 |
| Repair Agent | 生成 `repair_plan`，优先原位局部修复 |
| Learning Agent | 判断是否晋升为训练项、规则、检查器或 Agent memory |
| Delivery Agent | 只汇报已证明内容、未证明边界和用户应复审点 |

## 4. 执行前门禁

执行前必须先过对应门禁：

- 中文内容过 `encodingPreflight`，坏中文第一步阻断。
- 普通绘图必须先有结构化意图，正式任务优先 `validate_plan` / `dry_run_plan`。
- 系统资产复用必须先过 registry 检索、候选排序、精确来源门禁和 readback 计划。
- 系统资产沉淀必须先明确分类、机器契约、原生 DWG 位置、验证状态和保存边界。
- 局部修复必须先定位 `target_handles` / `target_bbox`，不能默认旁边重画一套。
- 训练任务必须先确定 `quick_trial`、`focused_retraining` 或 `formal_acceptance`，不能自动放大范围。

## 5. 执行和验证

完成声明必须由证据支撑：

- CAD 写入证据：created handles、目标图层、bbox、实体类型、样式、保存状态。
- 几何证据：validate / dry-run、readback、审计报告、必要截图。
- 资产证据：matched asset、source spec、native DWG、copy method、created/readback count、`savedCurrentDwg`。
- 训练证据：scope、训练报告、队列状态、Agent 自检、learning promotion 或明确 skipped。
- 文档证据：状态、changelog、issues、handoff / index、工作台同步或说明为什么不需要。

截图只作视觉辅助。只有截图时不能声称真实 CAD 尺寸准确；有 DWG / handles / `CAD_PLAN` / 用户明确尺寸时，才能提升为几何或标注证据。

## 6. 训练学习闭环

当任务暴露稳定问题，或用户要求“加强训练 / 根源修复 / 沉淀”，进入训练学习闭环：

```text
失败或新能力
  -> 归因到基础能力 / 对象能力 / 场景能力 / 资产能力 / 工具链问题
  -> 记录触发任务和证据边界
  -> 修改底座规则、单一任务规则、Prompt addendum、检查器或脚本
  -> focused retraining 或 formal acceptance
  -> 回测原任务
  -> A-to-A 校准
  -> 同步事实源和工作台
```

训练通过不是永久封存。后续复杂任务暴露基础项不稳时，要回流到对应基础项复训，追加新证据并回测原复杂任务。

## 7. A-to-A 校准

A-to-A 校准不是一句“已学习”。它必须说明每个责任 Agent 以后怎么变：

| 校准项 | 要写清楚什么 |
| --- | --- |
| `ruleDelta` | 底座规则变化，例如不从白话直接落 CAD、资产复用先查库 |
| `taskRuleDelta` | 单一任务变化，例如线型表样例必须 containment 审计 |
| `positiveExamples` | 以后应怎样拆分和执行 |
| `negativeExamples` | 以后禁止怎样做，例如整屏 block export、旁边重画 |
| `evidenceBoundary` | 哪些证据能证明，哪些只能 not_checked |
| `affectedAgents` | Intent、Asset、Execute、Audit、Repair、Learning、Delivery 各自影响 |

校准后要回写到合适事实源：共享 Prompt 合同、责任 Agent addendum / memory、训练事实源、治理规则、检查器、资产 registry 或 changelog。不能只写在本轮聊天记录里。

## 7.1 A-to-A TaskContract 门禁

主 Agent 在分发高风险任务前必须生成 `a_to_a_task_contract`，不能只凭自然语言判断“要不要叫某个 Agent”。合同至少包含：

- `taskKind`：如 `system_asset_sedimentation`、`asset_dwg_layout`、`visual_layout_review` 或普通编排。
- `triggeredSemantics`：本次命中的系统资产、沉淀、视觉布局等语义。
- `requiredAgents`：本次必须交付结论的责任 Agent。
- `hardGates`：每个责任 Agent 对应的机器门禁。
- `missingRequiredAgents` / `failedHardGates`：缺失或失败时必须写明，并阻断 `delivery_complete_claim`。

系统资产沉淀默认要求 `pipeline_asset_governor`、`pipeline_asset_librarian`、`pipeline_asset_dwg_curator`、`pipeline_asset_reuse_auditor` 四个 Agent 的结论。系统资产 DWG 排版、仓库货架、置物架、动线、可扩展货位、展示形式等视觉布局任务，还必须额外要求 `pipeline_visual_layout_reviewer` 输出 `visual_layout_review`。该视觉复审只判断布局语义和检索体验是否符合用户隐喻；截图非空、模型空间有对象、机器回读数量正确，都不能替代该门禁。

主编排入口 `core.orchestrator.workflow_dispatch.orchestrate_request()` 必须把合同写入报告。只要合同为 `blocked`，`workflow_dispatch` 就必须显示 `a-to-a hard gate` 阻断原因，不得继续执行或声称完成。仓库级检查入口为 `scripts/run_a_to_a_orchestration_gate_check.py`。

### 7.1.1 主 Agent 自检与动态加派

高风险合同还必须写入 `mainAgentSelfCheck` 和 `dispatchDecision`。这里的“主 Agent 有意识”不是模拟对话人格，而是机器可读的工程自我模型：主 Agent 必须声明自己是 `pipeline_orchestrator_main_agent`，职责是识别任务、生成合同、加派已登记责任 Agent、收证据并阻断不可靠完成声明；同时声明自己不能亲自替代 CAD readback、视觉布局复审、资产守门员或复用审计。

`dispatchDecision` 只允许把 `agents/pipeline/pipeline_manifest.json` 中已登记的 Agent 加入 `effectiveRequiredAgents`，并必须写明加派原因和对应 hard gate。未登记的新 Agent 只能进入 `additionalAgentRequests`，状态为 `needs_reviewed_package` 或 `needs_openspec_change`；不得临场激活，也不得放入本轮 `effectiveRequiredAgents` 后声称已经生效。若 `mainAgentSelfCheck` 失败、加派理由缺失、未登记 Agent 被强行生效，或仍缺必需 Agent 输出，合同必须追加 `main_agent_dispatch_awareness` gate 并阻断交付完成口吻。

## 7.2 Promotion Gate

训练、复训或纠错收尾必须生成机器可读 `promotionGate`，用于回答“这次到底要不要写规则 / 校准 Agent / 刷新工作台 / 回测原任务”。

| 字段 | 作用 |
| --- | --- |
| `promotionLevel` | `observation` / `case_lesson` / `learning_candidate` / `systemized` / `verified` |
| `decisions.updateTrainingSource` | 是否登记或核对 `docs/training/training-sources.json` |
| `decisions.updateWorkbench` | 是否运行 `scripts/sync_training_workbench.py` 刷新 HTML 派生快照 |
| `decisions.updateBaseRules` | 是否需要 reviewed package 修改底座规则 |
| `decisions.updateTaskRules` | 是否需要 reviewed package 修改单一任务规则 / 场景规则 |
| `decisions.updateAgentCalibration` | 是否同步责任 Agent memory / prompt addendum |
| `decisions.updateChecker` | 是否需要新增或修改机器检查器 |
| `decisions.retestOriginalTask` | 是否必须回测触发本次纠错的原任务 |
| `agentCalibration` | 受影响 Agent、正反例、证据边界和 A-to-A 校准输入 |

`quick_trial` 默认只能生成 `observation`，不写训练事实源、不刷新工作台、不写 Agent 校准。`focused_retraining` / `formal_acceptance` 只有在验收报告可 promotion、handles/readback 和 Agent 自检通过后，才允许进入 `systemized`。底座规则、检查器、资产 verified、系统资产 DWG 保存、正式图层和原任务回测都不能被 promotion gate 静默完成；gate 只能把它们标为 `needs_reviewed_package` 或 `required`。

## 8. 不晋升的情况

以下情况默认不晋升为训练项或系统规则：

- 一次性 quick trial，且没有重复失败或可复用检查器。
- 只有截图视觉推断，缺少 CAD readback 或明确尺寸。
- 用户明确说“先别沉淀 / 不进训练”。
- 资产来源不清，只能保持 `candidate` / `metadata_only`。
- 单个案例的偶发几何 bug，尚不能泛化为规则。

但这些仍可写入案例反馈或 `training-errors.md`，等待重复出现后再晋升。

## 9. 事实源同步

按影响范围同步事实源：

- 训练事实：`docs/training/training-sources.json`、learning ledger、Agent memory / Prompt addendum、`scripts/sync_training_workbench.py`。
- 系统规则：`docs/governance/cad-agent-rules.md`、`AGENTS.md`、相关 runbook。
- 架构规则：`docs/architecture/*.md`、必要时 OpenSpec change。
- 系统资产：`libraries/system_library/registry.json`、分类 `assets.json`、对应 `*_assets.dwg` / `.dwt`。
- 状态记录：`docs/status/current.md`、`docs/status/changelog.md`、失败 / 风险进入 `docs/status/issues.md`。
- 交接记录：完成一个开发包时更新 `docs/handoffs/current.md` 和 `docs/handoffs/package-index.md`。

同步失败时不得声称工作台、规则或资产库已经更新。

## 完成定义

一个任务链路只有同时满足以下条件，才算闭环：

1. 白话已被拆成结构化意图或明确阻断原因。
2. 复杂任务已拆成单一子任务，并有责任 Agent / Core 入口。
3. CAD、资产、训练或文档执行均在允许写入范围内。
4. 证据能支撑最终措辞，未证明项明确 not_checked。
5. 若暴露稳定问题，已回流到规则 / 训练 / 检查器 / A-to-A 校准。
6. 必要事实源已同步，后续 Agent 能从文档或机器规则里恢复这条链路。
