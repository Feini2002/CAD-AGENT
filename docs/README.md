# Docs Map（辅助文档地图）

本文是 `docs/` 的导航页。当前唯一 `PlanMD` / 开发主线仍是根目录 `CORE_RESTRUCTURE_PLAN.md`；本目录只存放执行剧本、架构说明、治理规则、交接入口、验证材料和历史记录。

## 当前入口

| 需要什么 | 入口 |
| --- | --- |
| 唯一 PlanMD、方向、Phase 优先级、Decision Gate | `../CORE_RESTRUCTURE_PLAN.md` |
| 三指令执行台账、包计数、即时 `next` | `planning/任务清单.md` |
| 日常恢复短上下文 | `../CORE_CONTEXT_BRIEF.md` |
| 能力矩阵和成熟度 | `../CORE_STATUS.md` |
| 当前状态快照 | `../CAD_AGENT_STATUS.md` |
| 新人或新 Agent 接手 | `onboarding/first-handoff.md` |
| Codex 校验 Cursor 按包交付 | `handoffs/CURSOR_PACKAGE_HANDOFFS.md` |
| 换机和回家验收 | `onboarding/migration-checklist.md` |

## 目录职责

| 目录 | 职责 | 不承载 |
| --- | --- | --- |
| `architecture/` | Core、`CAD_PLAN`、空壳布局等架构边界和设计依据 | 当前待办优先级 |
| `planning/` | Phase 执行剧本，服务 PlanMD 落地 | 独立 PlanMD 或后置计划副本 |
| `governance/` | 多 agent 协作、可写边界、治理流程 | 历史流水 |
| `onboarding/` | 新人接手、换机验收和最短阅读路径 | 长期路线 |
| `handoffs/` | Cursor 按开发包的 9 项交接汇总（给 Codex 审计） | 第二套 PlanMD |
| `verification/` | 验证模板、真实 CAD 证据；多候选见 `blank_shell_multi_candidate_boundaries.md`；Scene Alpha 见 `scene_alpha_preferences_contract.md` | 未验证能力声明 |
| `reviews/` | 只读评审和新鲜视角纪要 | 正式执行计划 |
| `decisions/` | 架构决策记录和原因 | 状态页 |
| `roadmap/` | 路线图兼容入口；当前路线看 `../CORE_ROADMAP.md` | 当前 PlanMD |
| `history/` | 需要随仓库迁移的历史材料和已执行记录 | 当前计划入口 |

## PlanMD 主从规则

- `PlanMD` 只负责文档治理和开发排序，不改变通用 CAD Agent Core Lab 的方向。
- `CORE_RESTRUCTURE_PLAN.md` 是唯一可以决定“为什么做、先做哪条主线、做到什么算退出”的 Markdown。
- `planning/任务清单.md` 是执行台账，只维护 §3/§4/§5 包状态、计数和即时 `next` 镜像；若它和 PlanMD 冲突，先修 PlanMD 边界，再同步任务清单。
- `planning/` 里的其它文件虽然保留 `plan` 文件名，但身份是 Phase 执行剧本；它们只能展开主计划中的当前条目，不能复制后置 Backlog 小包表。
- 状态、路线、架构、验证、review、history 文档都只能补充上下文和证据，不能覆盖 PlanMD。
- 如果某个辅助文档需要新增待办、调整优先级或改变退出标准，先改 `../CORE_RESTRUCTURE_PLAN.md`，再回填辅助文档。

## 固定规则

- “方向、优先级、退出标准、后置 Backlog 拆分”只写入 `../CORE_RESTRUCTURE_PLAN.md`；三指令即时 `next` 镜像写在 `planning/任务清单.md` §0。
- `docs/planning/` 可以有执行步骤，但必须服从主计划。
- 历史材料进入 `history/`；本机私有历史仍可进入被 `.gitignore` 排除的 `archive/`。
- 任何涉及真实 CAD 几何准确的结论，都必须回到 `../AGENTS.md`、`../CAD_AGENT_RULES.md` 和 `verification/` 的证据门槛。
