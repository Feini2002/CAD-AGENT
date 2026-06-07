# Core Status
最后更新：2026-06-07（架构归并画布工程仍是当前主线；旧表 C / 90% 口径降级为 `Core Proof Coverage`；adaptive growth、入口 custody 和主 Agent 认知证明已纳入架构边界，但都不代表正式训练恢复、表 C 提升或端到端真实 CAD 成熟）

本文只回答“当前能力成熟到哪里、证据是什么、风险边界是什么”。历史长流水已归档到 `docs/history/snapshots/finished-architecture-2026-05-28/CORE_STATUS.md`，近期流水看 `docs/status/current.md`，唯一 PlanMD 看 `CORE_RESTRUCTURE_PLAN.md`。

## 状态口径

| 状态 | 含义 |
| --- | --- |
| `alpha_ready_non_cad` | 非 CAD 链路已有稳定入口、测试和基线证据 |
| `alpha_verified_cad` | 有限 baseline CAD_PLAN 完成真实 AutoCAD 落图、截图辅助、实体回读和 `geometry_verified` |
| `prototype` | 有最小实现或脚本原型，但接口、样本或验证仍需增强 |
| `blocked_by_cad` | 仓库入口存在，但完成声明依赖真实 CAD 会话和 readback |
| `scaffold` | 目录、文档或数据壳已建立，核心能力尚未形成 |
| `blocked` | 缺依赖、缺证据或有已知失败，不能继续声称可用 |

## 成熟度口径（架构归并期）

当前不再把旧表 A / B / C 作为系统主叙事。后续状态优先拆成三层：

| 口径 | 当前判断 | 说明 |
| --- | --- | --- |
| `Core Proof Coverage` | 历史机器值约 **90.99%**，最高已证 L4 | 旧表 C / coverage JSON / registry 的底座证据覆盖；说明底层零件有历史 proof，不说明真实任务会画准 |
| `Agent Task Maturity` | 早期，可按 **5%-10%** 的训练感受谨慎看待 | 需要 CAD Designer Agent 通过对象课、案例 feedback、真实 readback、局部修复和学习沉淀逐步提升 |
| `Project Delivery Readiness` | 更早期 | 不能由表 C、RCAD、截图、dry-run、fake driver 或模型 pass 推导 |

旧表 A / B / C 仍保留为历史和底座回归口径，只在完整状态审计、历史对账、registry / coverage 修改或用户明确点名时展开。

## 四进度口径（固定模板，V-PROOF-04 + 表 C）

以下口径 **禁止** 混用。聊天最终回复默认不附进度表；只有用户点名开发状态查询、进度、完整状态、交接、审计、表 A/B/C、表 C 或历史 coverage 时，才展开下列表格。若用户说“真实 CAD 实力”，必须先澄清旧表 C 只是 `Core Proof Coverage`，不是 Agent 端到端真实能力。

```text
cad_capability_registry: 333 rows
cad_proof_coverage_percent=90.99%（0 verified + 303 showcase；25 smoke + 5 deferred）
cad_strength_headline_percent=90.99%（min 门；showcase_count=303；最高已证 L4）
Core 平台: 100%（三轨收口 + 969 tests；见 core_platform_completion_gate.md）
RCAD 烟囱: 29/29 verified；≠ 真实 CAD 实力
复跑: scripts/run_capability_coverage.py --output output/validation_runs/capability-lab/cad_capability_coverage.json
```

### 表 A — 工程节奏

| 指标 | 当前值 | 说明 |
| --- | --- | --- |
| 总进度 | 约 **97%** | Core×70% + Agent×30% 的折叠口径 |
| Core 底座 | **100%** | 三轨收口 + 969 tests OK + doc/repo gate；**≠** 表 C / 施工图能力 100% |
| Agent 多场景 | 约 **93%** | office / restaurant / residential 的 Alpha/Beta/P3 基线已收口；仍非 Scene Product |

### 表 B — 任务台账

| 轨道 | 当前值 | 说明 |
| --- | --- | --- |
| 能力证明 `V-PROOF` | **45/45 done** | 历史明细见 `docs/planning/archive/vproof-packages-done.md` |
| 代码轨 | **52/52 done** | 历史 55 口径已对账为 52 执行包 |
| RCAD 烟囱 | **29/29 verified** | 包完成度，不等于施工图能力 |

### 表 C — Core Proof Coverage（历史旧名：真实 CAD 实力）

| 指标 | 当前值 |
| --- | --- |
| **Core Proof Coverage（旧主指标）** | **90.99%** |
| CAD 证明覆盖率 | **90.99%** |
| CAD 实力指数（Ladder 加权） | **93.53%** |
| 场景片段实力（L3+） | **93.62%** |
| 展示就绪度（showcase） | **90.99%** |
| 最高已证 Ladder | **L4** |

机器报告：`output/validation_runs/capability-lab/cad_capability_coverage.json`。若 Markdown 与 JSON 冲突，以 JSON 为准。该表只证明底座证据覆盖，不证明 `Agent Task Maturity` 或 `Project Delivery Readiness`。

## 能力矩阵摘要

| 能力域 | 当前成熟度 | 证据入口 | 边界 |
| --- | --- | --- | --- |
| `CAD_PLAN` validate / dry-run | `alpha_ready_non_cad` | `scripts/validate_plan.py`、`scripts/dry_run_plan.py`、tests | 不证明真实 CAD 落图 |
| CAD validation runner | `alpha_verified_cad`（有限 baseline） | `scripts/run_cad_validation.py`、`output/validation_runs/**` | 只证明指定 plan / suite |
| Capability registry / 表 C | `alpha_ready_non_cad` | registry JSON、coverage JSON、table C gate | 证据路径与 hard audit 已清零；仅 `real_cad_guard` smoke |
| Block / symbol / hatch 受控样本 | `partially_verified` | RCAD-06、RCAD-23~25、block alpha/beta reports | 不扩大到真实公司块库或任意 hatch |
| Composition / VCAD 视觉表达 | `partially_verified` | V-PROOF-42/43、VCAD-01/02 reports | 视觉截图不替代 readback |
| Scene Agent | `alpha_ready_non_cad` | office / residential / restaurant benchmarks | 场景层不实现 Core 算法或 CAD 执行 |
| 自动读图 / shell 识别 | `prototype` | drawing-read fixtures / boundary docs | 未确认 shell candidates 不得直接落 CAD |
| Adaptive capability growth / `growth_replay` | `alpha_ready_non_cad` | `core/training/capability_growth_profile.py`、`core/training/adaptive_replay_planner.py`、`core/training/expression_regression_gate.py`、`core/training/adaptive_growth_closeout.py`、`scripts/run_cad_foundation_remaining_training.py --replay-mode growth_replay`、相关 tests、OpenSpec `adaptive-capability-growth-training` | 只证明能力画像、路由、回归门禁和完成声明边界；不证明真实 CAD 几何、用户验收、Worker 部署、系统资产 verified、正式训练集成或表 C 提升 |
| Entrypoint custody / replay claim audit | `alpha_ready_mixed` | `core.entrypoint_custody`、`config/entrypoint_custody_manifest.json`、`config/entrypoint_denylist.json`、`config/entrypoint_kill_switch.json`、`scripts/run_entrypoint_custody_audit.py`、`core.training.report_claim_audit`、`scripts/run_training_report_claim_audit.py`、`core.model_review.trace_claim_audit`、`scripts/run_model_trace_claim_audit.py`、`tests/core/test_entrypoint_custody.py`、`tests/core/test_legacy_entrypoint_custody_closure.py`、`output/validation_runs/legacy-entrypoint-closeout-cad-preview/` | 证明入口保管账、runtime guard / lease 权限位判定、workflow route custody 摘要、全仓 repo script manifest 分类、all-31 replay fail-closed、training/model 声明审计和一条真实 `CODEX_PREVIEW` smoke readback 已闭合；不证明全仓脚本已强制接 guard、不证明表 C 提升或正式训练恢复 |
| 主 Agent 认知证明 | `alpha_ready_non_cad` | `openspec/changes/prove-main-agent-cognition-loop/`、`core/model_review/evidence_portfolio.py`、`core/orchestrator/agent_cognition.py`、`core/orchestrator/model_agent_chain_runtime.py`、`core/orchestrator/orchestrator_host_runtime.py`、相关 tests | 已证明 no-CAD 工具结果可回喂同一 Agent 并写 `cognitiveLoopSummary`，行为改变 proof 能区分机制建设和认知证据，soft gate / route budget / Agent Task Maturity 指标有边界；仍不证明真实 CAD 几何、真实任务稳定变聪明、用户验收、表 C 或项目交付准备 |
| 模型型 Agent trace / run package / Host runtime / Reviewer closeout / Workbench Trace Viewer / Worker orchestrator remote | `alpha_ready_mixed` | `core/model_review/`、`core/orchestrator/run_package_state.py`、`core/orchestrator/closeout_gate.py`、`core/orchestrator/delete_neighbor_gates.py`、`core/orchestrator/orchestrator_host_runtime.py`、`core/orchestrator/reviewer_host_runtime.py`、`core/orchestrator/workbench_trace_viewer.py`、`core/orchestrator/local_live_model_bridge*.py`、`workers/orchestrator/**`、`WORKER_ORCHESTRATOR_DEPLOY_CHECKLIST.md`、相关 tests、`capability-map.html`、`CORE_RESTRUCTURE_PLAN.md` | 只证明模型调用证据、任务状态、分发计划、closeout 决策、删除范围 / 邻区保护、delivery 口径、派生 trace 视图和 `cadagent` 远程 Worker / Durable Object 编排可复盘；最新远程 smoke 为 `run_20260606151438_worker_orchestration_ready_f6260886`。本机 quick CAD preview 已在真实 AutoCAD 中只写 `CODEX_PREVIEW` 并回读 7 个 handles，`savedCurrentDwg=false`；但仍未接 Queue / Workflows、长期真实 bridge runner、真实 `gpt-5.5` provider 或正式训练集成，不替代 A-to-A hard gate、用户验收或表 C |

## 当前关键风险

| 风险 | 处理口径 |
| --- | --- |
| 表 C 旧证据债 | 新 writeback 先跑 hard audit + visual review + table C gate；旧债另开小包 |
| CAD 画面观感不足 | 用户要求画面时走 `VCAD-*`；截图只作 `visual_aid_only` |
| 自动读图未交付预备 | 保持人工确认 gate，不从未确认读图结果直接落 CAD |
| 文档再膨胀 | `run_doc_governance_audit.py` 检查活跃入口体量、链接、handoff 和表 C |
| 模型活体与业务通过混淆 | provider / schema 正常只说明 Agent 真调用了模型；若模型因证据不足返回 `needs_more_evidence` / `unavailable`，应视为正确业务阻断，不能误称链路没活或 CAD 已验证 |
| 能力成长画像污染 | `growth_replay` 只能读仓库内 active / protected 事实源；`output/debug`、派生工作台、诊断报告、外部路径、缺失文件、截图或模型 pass 不能作为 hard baseline；缺正反例或原任务回测时只能 blocked / not_verified |
| 入口 custody 被过度解读 | 当前 manifest / audit 已能阻断活跃文档、route 和 repo script 分类漂移，但未补 runtime guard 调用点的高风险写入入口不能说成已物理不可绕过；收尾 CAD smoke 只证明指定 `CODEX_PREVIEW` 计划 |
| 主 Agent 认知幻觉 | 规则、Prompt Pack、trace、learningCandidate、`cognitiveLoopSummary` 或 no-CAD 测试 pass 只说明判断链可审计；只有真实任务中的 route、dispatch、tool choice、blocking 或 replay 结果因历史经验改变，才可称为真实任务层面的认知提升 |

更多失败教训见 `docs/status/issues.md`。

## 当前入口

| 需要 | 入口 |
| --- | --- |
| 下一步从哪选 | `CORE_RESTRUCTURE_PLAN.md` |
| 四口令 / 三轨计数 | `docs/planning/任务清单.md` |
| 当前流水 | `docs/status/current.md` |
| 变更流水 | `docs/status/changelog.md` |
| 交接 | `docs/handoffs/current.md`、`docs/handoffs/package-index.md` |
| CAD 卡壳 | `docs/runbooks/blocker-playbook.md` |

## 不可声称

- 不能用 Core 平台 100% 工程收口、RCAD 29/29、no-CAD benchmark 或截图声称“已经能画准施工图”。
- 不能把 `negative_guard_verified`、fake driver、dry-run pass 或 smoke 行当成 `geometry_verified`。
- 不能把 `VCAD-*` 视觉表达截图当作表 C 机器值提升。
- 不能保存、覆盖、删除 DWG 或修改正式图层，除非用户逐项明确批准。
