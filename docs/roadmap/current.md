# Core Roadmap

最后更新：2026-05-28

本文是高层路线图，只描述方向和阶段关系。唯一 `PlanMD` / 具体执行清单见 `CORE_RESTRUCTURE_PLAN.md`，能力成熟度见 `CORE_STATUS.md`。本文不承载独立下一步。

## 路线原则

```text
通用 Core 优先
场景 Agent 轻量复用
真实 CAD 证据优先于口头完成声明
非 CAD benchmark 不能替代真实 CAD readback
Scene Alpha / Beta 不能替代 Scene Product
```

## 场景成熟度口径

| 层级 | 路线含义 | 当前状态 |
| --- | --- | --- |
| Core 底座 | 先把通用 CAD_PLAN、执行、验证、benchmark、读图、对象和图块能力打稳 | Alpha 原型较厚，真实 CAD 扩样仍需继续 |
| Scene Alpha 壳层 | 用 preferences 和解释模板证明多个场景可以复用同一 Core | 已完成三场景 Alpha 验收 |
| Scene Beta 能力包 | 给单场景补对象、微场景、failure benchmark 和 non-CAD 证据 | office / residential / restaurant 已有 beta benchmark |
| Scene Product 场景产品 | 面向真实业务场景闭环：项目样本、图块策略、真实 CAD smoke、用户确认流 | `commercial_fitout` 已进入 Scene Product Alpha 边缘：三组脱敏样本、代表对象 smoke 与部分真实 CAD 证据已建立；仍未达到完整产品化交付。其他场景仍为 Alpha/Beta |

## 已完成路线

| 阶段 | 当前状态 | 说明 |
| --- | --- | --- |
| 架构冻结 | done | 仓库定位为可迁移 CAD Agent Core Lab，`CAD_PLAN` 是落图中间层 |
| 仓库重装 | done | `core/`、`agents/`、`libraries/`、`projects/`、`tests/` 结构已建立，旧 `scripts/` / `drivers/` 保留兼容包装器 |
| 状态看板 | done | `CORE_STATUS.md`、`docs/status/current.md`、`CORE_CONTEXT_BRIEF.md` 已建立 |
| 高层模型 | prototype | DESIGN / DRAWING / PROJECT / OBJECT / STYLE / BLOCK / LAYOUT / PROPOSAL / VERIFICATION 及 SHELL / CIRCULATION / FUNCTION_ZONE 已有 schema 与 examples |
| 非 CAD Core 原型 | prototype | object/style/block/layout/proposal/plan/verification/safety/capability/benchmark/composition 已形成第一批原型 |
| blank-shell pipeline | alpha_ready_non_cad | Phase P-V 已跑通 shell -> project -> circulation -> zones -> placement -> proposal -> CAD_PLAN -> dry-run -> unverified report |
| 系统层安全补强 | done | repo audit、路径边界、pipeline failure hardening、verification edge tests、无 CAD 总控已补强 |

## 当前主线

### Phase W：真实 CAD 回读闭环

目标：完成真实 AutoCAD 环境中的落图、截图、实体回读和 verification report。

为什么优先：没有这一步，系统只能说“非 CAD 链路可用”，不能说“图纸画准了”。

入口：

- `docs/runbooks/cad-validation.md`
- `scripts/run_cad_validation.py`
- `core/verification/inspect_dwg.py`
- `core/verification/verification_report.py`

### Phase X：场景 Agent Alpha

目标：让 office / residential / restaurant 等场景通过 preferences 复用同一 Core pipeline，证明场景层是轻量差异层。

为什么重要：证明场景 Agent 是轻量差异层，不是复制 Core 算法。该阶段只到 Scene Alpha，不代表具体场景产品完成。

入口：

- `agents/*/preferences.json`
- `agents/SCENE_AGENT_RULES.md`
- `tests/agents/`

### Phase Y：空壳布局硬化

目标：把当前可跑通的 blank-shell pipeline 强化成多候选、可解释失败、更多真实样本的非 CAD 实验台。

为什么重要：当前 pipeline 仍偏单条主候选，不能当作完整自动设计大脑。

入口：

- `core/workflows/blank_shell_pipeline.py`
- `core/layout_engine/`
- `core/proposal_engine/`
- `examples/benchmarks/blank_shell_core_benchmark.json`

### Phase Z：维护治理

目标：保持文档职责清晰、验证命令稳定、历史与问题可追溯。

为什么重要：当前系统经历深度开发和安全补强，后续最大风险之一是状态文档再次分散或过期。

入口：

- `CORE_CONTEXT_BRIEF.md`
- `CORE_RESTRUCTURE_PLAN.md`
- `CORE_STATUS.md`
- `docs/status/current.md`
- `docs/status/changelog.md`
- `docs/status/issues.md`

### Phase R：新鲜视角评审

目标：用多个第一次接触系统的只读专家视角，校准下一轮深度开发方向，避免沿惯性补功能或把场景能力写偏。

为什么重要：当前 Core 已有有限 baseline CAD 闭环和第一批 persona composition 自检，但仍需要持续判断真正缺口是 CAD 能力契约、办公基础闭环、图块库设计、benchmark 门禁、角色组合真实 CAD readback，还是文档/协作治理。

入口：

- `docs/reviews/fresh-eyes-review-2026-05-25.md`
- `docs/history/completed-plans/phase-r/fresh-perspective-rebirth-plan.md`
- `docs/history/completed-plans/phase-r/rebirth-implementation-plan.md`
- `docs/history/completed-plans/phase-r/cad-capability-contract.md`
- `docs/history/completed-plans/phase-r/block-library-roadmap.md`
- `docs/planning/phase-r-office-benchmark-cases.md`
- `examples/benchmarks/interior_delivery_benchmark.json`
- `docs/governance/multi-agent-contribution.md`
- `docs/onboarding/first-handoff.md`

## 长期路线

| 方向 | 当前状态 | 后续判断点 |
| --- | --- | --- |
| 自动 DWG/PDF 空壳识别 | not_started / prototype 边缘 | 是否优先继续人工 JSON 闭环，还是投入自动识别 |
| 成熟几何库 | undecided | 是否引入 `shapely` 或其他几何库，需用户决策和环境清单 |
| 真实块库 | prototype | 是否接入公司块库，如何处理隐私和路径迁移 |
| 多方案设计推理 | prototype | 何时从可解释候选进入更复杂设计策略 |
| 真实项目回归集 | not_started | 哪些项目可作为可提交样本，哪些只能留本机 |
| 工装 Scene Product Alpha | partially_verified | 已有开放办公、会议室、前台接待三样本与部分真实 CAD smoke；仍需用户确认流、图块策略和更多项目级 readback 才能称为完整 Scene Product |
| 换机验收 | blocked_by_cad | 用 `run_cad_validation.py` 在新机器上跑完整 CAD 验证 |

## 路线约束

- 不把工装、家装、办公、餐饮、展陈的通用能力重复写进各自 Agent。
- 不把 Scene Alpha / Beta 的 preferences、rules 或 non-CAD benchmark 当成 Scene Product。
- 不从白话直接跳到 CAD；必须先结构化为 `CAD_PLAN` 或更高层模型。
- 不把截图当作几何准确证据。
- 不保存、覆盖、删除或修改正式图层，除非用户明确批准。
- 任何阶段完成后都要同步状态和证据。
