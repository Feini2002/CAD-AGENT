# 通用 CAD Agent 当前状态

最后更新：2026-06-06。本文只保留当前事实、风险和入口；日期流水、开发包细节和旧证据全文统一查 `docs/status/changelog.md`、`docs/handoffs/package-index.md` 与 `output/validation_runs/**`。

## 当前一句话

系统已从“底座施工期”进入 **ARCH-CONVERGENCE-01 架构归并期**：先不新开正式对象训练，而是把探索式开发中形成的 Core 规则、`CAD_PLAN`、A-to-A、模型型 Agent、Worker / bridge、资产智能、训练地图、工作台、表 A/B/C 和证据治理，统一归入七层任务生命周期。当前治理原则是保留规则 / 调用 / 证据链，但重画主构图，避免继续形成第二套 plan、第二套 next 或第二套能力口径。

后续任务和优先级只写入 PlanMD 与 `docs/planning/任务清单.md`；本文不承载后续开发清单。

## 当前主方向

- 当前主工程：`ARCH-CONVERGENCE-01`，设计见 `docs/architecture/system-architecture-convergence.md`，OpenSpec 见 `openspec/changes/unify-system-architecture-canvas/`。
- 唯一 `PlanMD`：`CORE_RESTRUCTURE_PLAN.md`。
- 默认短上下文：`CORE_CONTEXT_BRIEF.md`。
- 主训对象：`agents/cad_designer/`；当前主场景插件：`agents/residential/`。正式对象训练暂缓到架构归并完成后恢复。
- 旧表 C / 90% 现在解释为 `Core Proof Coverage`，只说明底座证据覆盖；不得代表 `Agent Task Maturity` 或 `Project Delivery Readiness`。
- 真实 CAD 声明链：结构化意图 / `CAD_PLAN` -> validate -> dry-run -> `CODEX_PREVIEW` -> created handles readback -> bbox / layer / entity audit -> 必要截图辅助 -> closeout。
- 模型型 Agent 边界：`gpt-5.5` / Prompt Pack 只做判断、复审、建议和工具请求；活体调用必须有 `modelInvoked=true`、`modelUnavailable=false`、`schemaValid=true` 和 trace；不得替代 UTF-8 门禁、CAD_PLAN 校验、dry-run、readback、sourceSpec、reuseReplay、表 C 或用户验收。
- 资产智能边界：reference/raw 只做输入证据，system asset 必须有 registry、native / visible evidence、reuse probe 或 replay；metadata-only / candidate 不能说成 verified。
- 训练边界：quick trial 不沉淀；focused retraining 只覆盖点名项；formal acceptance 才允许完整验收、同步和 promotion。

## 当前有效包

- `MODEL-AGENT-RUNTIME-TOOL-CONTRACT-REACT-P10-01`：Stage 4 受控 CAD 工具已进入 preview-only 门禁；真实 AutoCAD / COM / handle readback 不可用时只能 blocked / not_verified。
- `LOCAL-LIVE-MODEL-BRIDGE-HARDENING-MD-CLOSEOUT-01`：Worker 编排 + 本地活体模型桥路线已从独立架构 MD 收口到 `CORE_RESTRUCTURE_PLAN.md` §3.1 和 `core/orchestrator/local_live_model_bridge*.py`。当前本地 runtime 已加固：未知阶段不静默降级、run id 防碰撞、live bridge 能力登记、submit lease identity、trace 包 diagnostics 和 fake CAD `proofStatus=not_verified`；后续剩余项是 Cloudflare Worker / Durable Object / Queue 迁移、bridge-owned Codex config、真实 live provider 复验和真实 CAD-MCP preview-only 证据。
- `DESIGN-STYLE-PROMPT-PACK-ABC-TRAINING-01` 及后续语义拆分包：设计阶段已支持 design director、style generator、design reviewer，并能区分规则讨论、语义分析、单方案、多方案和候选数量。
- `ASSET-LOCAL-RAG-MVP-01`、`OBJECT-FAMILY-SOFA-TRIAL-MVP-01`、`ASSET-PROMOTION-CANDIDATES-MVP-01`、`OBJECT-FAMILY-SOFA-REPLAY-RCAD-01`：资产智能后四项已形成从本地 RAG、no-CAD draft、review-only 晋升候选到 sofa 真实 CAD replay 的链路；其中 replay 证明的是 sofa 对象族 `draw_symbol_glyph` handles / bbox / 图层闭合，不证明跨 DWG 系统资产复用 verified。
- `SYSTEM-ASSET-LIBRARY-GOVERNANCE-01` 与 `SEDIMENTATION-PROTOCOL-01`：系统资产沉淀必须过 asset governor、source boundary、native visible evidence、reuseWorkflowProbe / reuseReplay 和仓库视觉布局复审。
- `CAD-TRAINING-PROMOTION-GATE-01`、`TRAINING-SCOPE-GUARD-01`、`TRAINING-LATENCY-ROUTING-01`、`TRAINING-PARKING-ANCHOR-01`：训练从“想到啥改啥”收束为 quick / focused / formal 三档，并要求 promotion gate、范围记录和 evidence boundary。

## 当前风险

- 文档解释层容易再次膨胀；完成包明细必须进入 changelog / handoff archive，不回灌到短入口。
- 架构材料很多但主构图曾经分散；新增模块若不归入七层画布，会继续让系统看起来很满但不串通。
- 历史旧称“真实 CAD 实力 90.99%”容易误导用户理解为端到端能力；后续必须拆成 `Core Proof Coverage`、`Agent Task Maturity`、`Project Delivery Readiness`。
- 任何截图、dry-run、fake driver、no-CAD draft、模型 pass、工作台页面或 closeout 字样，都不能替代真实 CAD created handles readback。
- 系统资产库不能被训练标题、临时面板、proof 文案或不清晰来源污染；对象 block export 只接受 selected / created / active handles、明确 bbox 或 named block。
- 自动化训练和系统资产沉淀会产生大量证据产物；清理前必须先做 evidence-closure / retention dry-run，不能删除 active fact source 或仍被引用的报告。
- OpenSpec 只作为单个复杂变更的契约层，不承载总 backlog；根级 `openspec/tasks.md` 禁止出现。
- 表 C、工程节奏、任务台账是三套口径，不能互相替代。
- Worker 编排只证明远程触发、状态机、队列和结果回传框架成立；本地活体模型桥解决模型真实调用问题，不等于 CAD 已验证。Worker 实现必须默认覆盖超时、熔断、重试上限、DLQ、bridge 离线、幂等、backpressure 和 kill switch；若模型返回 `needs_more_evidence` / `unavailable` 且 provider status 正常，应按业务阻断处理，而不是误判为模型没活。

## 当前入口

| 需要 | 看哪 |
| --- | --- |
| 短上下文 | `CORE_CONTEXT_BRIEF.md` |
| 唯一主计划 | `CORE_RESTRUCTURE_PLAN.md` |
| 架构归并画布 | `docs/architecture/system-architecture-convergence.md` |
| 架构归并 OpenSpec | `openspec/changes/unify-system-architecture-canvas/` |
| 任务台账 / 用户四指令 | `docs/planning/任务清单.md` |
| 能力状态 / 表 C 解释 | `CORE_STATUS.md` |
| 训练主线 | `docs/training/README.md`、`docs/training/cad-designer-growth-path.md` |
| 系统任务链路 | `docs/architecture/cad-agent-task-chain.md` |
| Worker 编排 + 本地活体模型桥 | `CORE_RESTRUCTURE_PLAN.md`、`core/orchestrator/local_live_model_bridge*.py`、`scripts/diagnose_local_live_model_bridge.py` |
| 系统资产协议 | `docs/architecture/system-asset-sedimentation-protocol.md` |
| 风险和失败教训 | `docs/status/issues.md` |
| 历史流水 | `docs/status/changelog.md` |
| 当前交接 / 包索引 | `docs/handoffs/current.md`、`docs/handoffs/package-index.md` |

## 最近验证入口

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_doc_governance_audit.py
& $py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v
& $py scripts\run_capability_coverage.py --output output\validation_runs\capability-lab\cad_capability_coverage.json
```

普通文档治理只需跑文档治理审计和相关单测。涉及 CAD 落图、截图、训练、runner、验证、资产复用 / 沉淀或局部修复链路时，必须补最小实际链路；真实 CAD 不可用时只能报告 `not_run` / `not_verified`，不能用完成口吻声称图纸准确。
