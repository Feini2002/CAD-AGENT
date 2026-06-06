## Why

当前仓库已经拥有大量 CAD Agent 底座、训练、资产、多 Agent 和模型桥材料，但这些能力来自多轮探索式开发，像在同一张画布上分片生长。继续直接训练会把旧表 A / B / C、能力覆盖、训练地图、资产库、Worker / bridge 和 GPT-5.5 模型桥继续并列堆叠，难以判断每个模块属于哪一层、服务谁、不能越过谁。

本变更先做一次仓库级架构归并设计：不推翻旧模块，而是把它们重新归入统一任务生命周期，并把旧“真实 CAD 实力”口径降级为底座证据覆盖。

## What Changes

- 新增一张系统级“七层架构画布”，覆盖入口、任务对象、决策编排、能力证据、执行工具、审计修复和沉淀成长。
- 将表 A / B / C 从主叙事降级为底座证据层；表 C 不再表示端到端真实 CAD 能力，而是 `Core Proof Coverage`。
- 新增三类成熟度口径：`Core Proof Coverage`、`Agent Task Maturity`、`Project Delivery Readiness`。
- 暂缓新一轮正式训练，先完成架构归并文档、规则同步、PlanMD 重排和关键脚本口径审计。
- 将 Worker / bridge / GPT-5.5 归入决策编排层，将系统资产归入沉淀成长层，将工作台归入派生显示层。
- 更新唯一 PlanMD、状态入口、训练入口、治理规则和 OpenSpec 契约，避免形成第二套主计划。
- **BREAKING**: 面向状态查询和计划讨论时，“真实 CAD 实力 90%”不得再作为系统端到端真实能力表达；旧 coverage 只能作为底座证据覆盖。

## Capabilities

### New Capabilities

- `system-architecture-canvas`: 定义仓库级任务生命周期分层、旧模块归位、成熟度口径和跨层禁止规则。

### Modified Capabilities

- 无现有稳定 spec 需要 delta；当前仓库 `openspec/specs/` 仅保留 `.gitkeep`。

## Impact

- 文档：`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`AGENTS.md`、`docs/governance/cad-agent-rules.md`、`docs/planning/任务清单.md`、`docs/status/current.md`、`docs/status/changelog.md`、`docs/status/issues.md`、`docs/training/README.md`、`docs/architecture/**`。
- 脚本后续审计：`scripts/run_capability_coverage.py`、`scripts/build_capability_map_data.py`、`scripts/sync_training_workbench.py`、`scripts/run_training_workbench_agent_check.py`、`scripts/run_doc_governance_audit.py`、`scripts/run_a_to_a_orchestration_gate_check.py`。
- 用户口径：未来训练前先看 `Agent Task Maturity` 和案例 feedback；`Core Proof Coverage` 只作为底座回归和证据查询。
- CAD 安全：本变更不放宽任何 CAD 写入、保存、删除、正式图层、sourceSpec、readback 或用户验收门槛。
