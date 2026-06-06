# Docs Map（文档控制面）

当前唯一 `PlanMD` / 开发主线仍是根目录 `CORE_RESTRUCTURE_PLAN.md`。`docs/` 只承载状态、治理、runbook、架构、验证、交接和历史，不承载第二套计划。

## 当前入口

| 需要什么 | 入口 |
| --- | --- |
| 唯一 PlanMD、方向、优先级、Decision Gate | `../CORE_RESTRUCTURE_PLAN.md` |
| 日常恢复短上下文 | `../CORE_CONTEXT_BRIEF.md` |
| 能力矩阵和表 C 解释 | `../CORE_STATUS.md` |
| 当前状态快照 | `status/current.md` |
| 变更流水 | `status/changelog.md` |
| 风险与教训 | `status/issues.md` |
| 三指令执行台账 / 即时 `next` | `planning/任务清单.md` |
| 当前交接窗口 | `handoffs/current.md` |
| 全量交接索引 | `handoffs/package-index.md` |
| 新人或新 Agent 接手 | `onboarding/first-handoff.md` |
| CAD 验证 / 卡壳流程 | `runbooks/cad-validation.md`、`runbooks/blocker-playbook.md` |
| 旧根目录入口迁移对照 | 本表和根目录 `README.md` 的“关键入口” |

## 目录职责

| 目录 | 职责 | 不承载 |
| --- | --- | --- |
| `status/` | 当前状态、changelog、issues | 机器证据本体 |
| `governance/` | 规则、文档治理、多 agent 协作边界 | 历史流水 |
| `runbooks/` | CAD 验证、排障、迁移验收操作手册 | 长期计划 |
| `architecture/` | Core、`CAD_PLAN`、符号语法、场景边界 | 当前待办 |
| `planning/` | 执行台账和 Phase 路由 | 独立 PlanMD |
| `handoffs/` | 按包交接 current / index / archive | 第二套 Backlog |
| `verification/` | 证据边界、模板、门禁、验收解释 | 未验证能力声明 |
| `history/` | 已完成计划、旧快照、长历史 | 当前状态 |

## 主从规则

- 计划和优先级只看 `../CORE_RESTRUCTURE_PLAN.md`。
- 执行计数和即时 `next` 只看 `planning/任务清单.md`。
- 表 C 机器值只看 `../output/validation_runs/capability-lab/cad_capability_coverage.json`。
- 机器证据只看 `../output/validation_runs/**`。
- Markdown 可以解释证据，但不能替代 JSON、readback、created handles 或 `geometry_verified`。

## 旧根入口迁移

根目录旧 Stub 入口不再保留；需要对应内容时直接打开目标事实源。

| 旧入口 | 目标 |
| --- | --- |
| `当前状态入口.md` | `docs/status/current.md` |
| `变更记录入口.md` | `docs/status/changelog.md` |
| `问题风险入口.md` | `docs/status/issues.md` |
| `长期规则入口.md` | `docs/governance/cad-agent-rules.md` |
| `路线图入口.md` | `docs/roadmap/current.md` |
| `训练错误记录入口.md` | `docs/training/training-errors.md` |
| `视觉优先训练计划入口.md` | `docs/training/visual-first-agent-plan.md` |
| `CAD自动验证入口.md` | `docs/runbooks/cad-validation.md` |
| `CAD符号语法入口.md` | `docs/architecture/symbol-grammar.md` |
| `CAD卡壳排障入口.md` | `docs/runbooks/blocker-playbook.md` |
