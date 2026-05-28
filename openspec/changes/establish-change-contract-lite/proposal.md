## Why

当前仓库已经有清晰主线：`CORE_RESTRUCTURE_PLAN.md` 是唯一 PlanMD，训练、表 C、真实 CAD 验证和状态记录各有入口。OpenSpec 已初始化后，需要一层轻量变更契约，帮助重大或跨模块变更先写清楚 proposal/design/tasks/specs，同时防止 `openspec/changes/*` 演变成第二套主计划。

本次升级回应 `CodeGraph + OpenSpec Architecture Governance` 表单中的“事实先行、规格承接、小步闭环”原则，但只采用适合本仓库的小型版本：强化契约能力，不做文档换血。

## What Changes

- 新增 OpenSpec 变更契约能力：定义什么情况必须开 change、什么情况不应开 change、change 产物如何服从唯一 PlanMD。
- 在仓库规则和 PlanMD 中补充 OpenSpec 路由口径：OpenSpec 是单个复杂变更的契约层，不承载全局 backlog、next、优先级或退出标准。
- 扩展文档治理检查：识别 OpenSpec 误用，例如根目录 `openspec/tasks.md`、change 文档声明自己是主计划，或 `openspec/config.yaml` 未保留唯一主线约束。
- 增加最小测试，保证以上治理规则可被 `run_doc_governance_audit.py` 间接覆盖。
- 不改变 CAD 执行逻辑、表 C registry、训练案例、真实 CAD 验证证据或 Core 模块结构。

## Capabilities

### New Capabilities

- `change-contract-governance`: Defines the lightweight OpenSpec contract rules for scoped changes while preserving `CORE_RESTRUCTURE_PLAN.md` as the only master planning line.

### Modified Capabilities

- None.

## Impact

- Documentation:
  - `AGENTS.md`
  - `CORE_RESTRUCTURE_PLAN.md`
  - status / changelog / handoff records for this package
- Governance code:
  - `core/maintenance/doc_governance.py`
  - `tests/core/test_doc_governance.py`
- OpenSpec artifacts:
  - `openspec/changes/establish-change-contract-lite/`

Evidence boundary: this change improves project governance only. It does not prove any new CAD geometry capability, does not change Table C, and does not relax the existing CAD completion evidence requirements.
