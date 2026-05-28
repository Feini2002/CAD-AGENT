# Core Status

最后更新：2026-05-28（完工后架构瘦身）

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

## 四进度口径（固定模板，V-PROOF-04 + 表 C）

以下口径 **禁止** 混用。聊天最终回复默认不附进度表；只有用户点名开发状态查询、进度、完整状态、交接、审计、表 A/B/C、表 C 或真实 CAD 实力时，才展开下列表格，并先报表 C 主指标。

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

### 表 C — 真实 CAD 实力

| 指标 | 当前值 |
| --- | --- |
| **真实 CAD 实力（主指标）** | **90.99%** |
| CAD 证明覆盖率 | **90.99%** |
| CAD 实力指数（Ladder 加权） | **93.53%** |
| 场景片段实力（L3+） | **93.62%** |
| 展示就绪度（showcase） | **90.99%** |
| 最高已证 Ladder | **L4** |

机器报告：`output/validation_runs/capability-lab/cad_capability_coverage.json`。若 Markdown 与 JSON 冲突，以 JSON 为准。

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

## 当前关键风险

| 风险 | 处理口径 |
| --- | --- |
| 表 C 旧证据债 | 新 writeback 先跑 hard audit + visual review + table C gate；旧债另开小包 |
| CAD 画面观感不足 | 用户要求画面时走 `VCAD-*`；截图只作 `visual_aid_only` |
| 自动读图未交付预备 | 保持人工确认 gate，不从未确认读图结果直接落 CAD |
| 文档再膨胀 | `run_doc_governance_audit.py` 检查活跃入口体量、链接、handoff 和表 C |

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
