# Core Status

最后更新：2026-06-06（ARCH-CONVERGENCE-01：架构归并画布工程成为当前主线；旧表 C / 90% 口径降级为 `Core Proof Coverage`，不再表示端到端真实 CAD 能力；训练暂缓，先同步架构、规则、状态和脚本口径）

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

## 成熟度口径（ARCH-CONVERGENCE-01）

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
| 模型型 Agent trace / run package / Host runtime / Reviewer closeout / Workbench Trace Viewer | `alpha_ready_non_cad` | `core/model_review/`、`core/orchestrator/run_package_state.py`、`core/orchestrator/closeout_gate.py`、`core/orchestrator/delete_neighbor_gates.py`、`core/orchestrator/orchestrator_host_runtime.py`、`core/orchestrator/reviewer_host_runtime.py`、`core/orchestrator/workbench_trace_viewer.py`、`core/orchestrator/local_live_model_bridge*.py`、相关 tests、`capability-map.html`、`CORE_RESTRUCTURE_PLAN.md` | 只证明模型调用证据、任务状态、分发计划、closeout 决策、删除范围 / 邻区保护、delivery 口径和派生 trace 视图可复盘；长期路线要求先有 `worker_orchestration_ready` / `local_bridge_connected`，再用完整 trace 包里的 `modelInvoked=true` / `modelUnavailable=false` / `schemaValid=true` 证明 `single_agent_live`；fake CAD preflight 只能是 `proofStatus=not_verified`，不替代 CAD readback、A-to-A hard gate、用户验收或表 C |

## 当前关键风险

| 风险 | 处理口径 |
| --- | --- |
| 表 C 旧证据债 | 新 writeback 先跑 hard audit + visual review + table C gate；旧债另开小包 |
| CAD 画面观感不足 | 用户要求画面时走 `VCAD-*`；截图只作 `visual_aid_only` |
| 自动读图未交付预备 | 保持人工确认 gate，不从未确认读图结果直接落 CAD |
| 文档再膨胀 | `run_doc_governance_audit.py` 检查活跃入口体量、链接、handoff 和表 C |
| 模型活体与业务通过混淆 | provider / schema 正常只说明 Agent 真调用了模型；若模型因证据不足返回 `needs_more_evidence` / `unavailable`，应视为正确业务阻断，不能误称链路没活或 CAD 已验证 |

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
