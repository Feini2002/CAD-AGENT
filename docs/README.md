# Docs Map（辅助文档地图）

本文是 `docs/` 的导航页。当前唯一 `PlanMD` / 开发主线仍是根目录 `CORE_RESTRUCTURE_PLAN.md`；本目录只存放执行剧本、架构说明、治理规则、交接入口、验证材料和历史记录。

## 当前入口

| 需要什么 | 入口 |
| --- | --- |
| 唯一 PlanMD、当前活跃工作队列、Phase 优先级 | `../CORE_RESTRUCTURE_PLAN.md` |
| 日常恢复短上下文 | `../CORE_CONTEXT_BRIEF.md` |
| 能力矩阵和成熟度 | `../CORE_STATUS.md` |
| 当前状态快照 | `../CAD_AGENT_STATUS.md` |
| 新人或新 Agent 接手 | `onboarding/first-handoff.md` |
| 换机和回家验收 | `onboarding/migration-checklist.md` |

## 目录职责

| 目录 | 职责 | 不承载 |
| --- | --- | --- |
| `architecture/` | Core、`CAD_PLAN`、空壳布局等架构边界和设计依据 | 当前待办优先级 |
| `planning/` | Phase 执行剧本，服务 PlanMD 落地 | 独立 PlanMD |
| `governance/` | 多 agent 协作、可写边界、治理流程 | 历史流水 |
| `onboarding/` | 新人接手、换机验收和最短阅读路径 | 长期路线 |
| `verification/` | 验证模板、真实 CAD 证据记录和补验材料 | 未验证能力声明 |
| `reviews/` | 只读评审和新鲜视角纪要 | 正式执行计划 |
| `decisions/` | 架构决策记录和原因 | 状态页 |
| `roadmap/` | 路线图兼容入口；当前路线看 `../CORE_ROADMAP.md` | 当前 PlanMD |
| `history/` | 需要随仓库迁移的历史材料和已执行记录 | 当前计划入口 |

## PlanMD 主从规则

- `PlanMD` 只负责文档治理和开发排序，不改变通用 CAD Agent Core Lab 的方向。
- `CORE_RESTRUCTURE_PLAN.md` 是唯一可以决定“当前做什么、先做什么、做到什么算退出”的 Markdown。
- `planning/` 里的文件虽然保留 `plan` 文件名，但身份是 Phase 执行剧本；它们只能展开主计划中的条目。
- 状态、路线、架构、验证、review、history 文档都只能补充上下文和证据，不能覆盖 PlanMD。
- 如果某个辅助文档需要新增待办、调整优先级或改变退出标准，先改 `../CORE_RESTRUCTURE_PLAN.md`，再回填辅助文档。

## 固定规则

- “下一步、待办、优先级、退出标准”只写入 `../CORE_RESTRUCTURE_PLAN.md`。
- `docs/planning/` 可以有执行步骤，但必须服从主计划。
- 历史材料进入 `history/`；本机私有历史仍可进入被 `.gitignore` 排除的 `archive/`。
- 任何涉及真实 CAD 几何准确的结论，都必须回到 `../AGENTS.md`、`../CAD_AGENT_RULES.md` 和 `verification/` 的证据门槛。
