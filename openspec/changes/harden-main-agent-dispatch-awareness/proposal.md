## Why

现有 A-to-A TaskContract 已能按固定语义要求资产类 Agent 和视觉布局复审，但主 Agent 的“我是谁、我这轮该负责什么、我是否需要加派 Agent”还没有成为机器可读验收项。这样容易出现两类漂移：主 Agent 口头说自己会判断，却没有报告字段可追踪；或者临场觉得需要新角色，却绕过 Agent 注册、reviewed package 和 hard gate。

本变更把主 Agent 自我认知和加派判断沉淀为合同字段与验收门禁：主 Agent 必须先声明身份、任务理解、责任边界、已登记 Agent 加派决策和未登记 Agent 的 reviewed-package 候选，才允许高风险 workflow 进入完成口吻。

## What Changes

- 在 `a_to_a_task_contract` 中新增主 Agent 自检段：`mainAgentSelfCheck`，记录 `identity`、`mission`、`taskUnderstanding`、`responsibilityBoundary`、`knownLimits` 和 `decisionBasis`。
- 新增主 Agent 加派决策段：`dispatchDecision`，记录 `registeredAdditionalAgents`、`additionalAgentRequests`、`reasoning`、`blockedUntilAgentsReport` 和 `reviewedPackageRequired`。
- 对已登记 Agent：允许主 Agent 根据语义、现有输出、hard gate 和 manifest 动态加入本轮 `requiredAgents`，并把加派理由写入合同。
- 对未登记 Agent：只允许写入 `additionalAgentRequests`，状态为 `needs_reviewed_package` 或 `needs_openspec_change`；不得临场加入 `requiredAgents` 后放行，也不得声称该 Agent 已生效。
- 加固 `workflow_dispatch`：当 `mainAgentSelfCheck` 缺失、加派理由缺失、未登记 Agent 被当成已生效 Agent、或 `blockedUntilAgentsReport=true` 但仍尝试交付完成时，必须以 A-to-A hard gate 阻断。
- 加固 `pipeline_manifest.json`：登记主 Agent 身份、可自动加派的已登记 Agent 范围、未登记 Agent 请求边界和禁止模式。
- 加固 `run_a_to_a_orchestration_gate_check.py` 和单元测试：覆盖主 Agent 自检、已登记 Agent 动态加派、未登记 Agent 候选阻断、视觉布局 readability 字段和 dispatch 阻断。
- 同步架构文档、规则、状态和 changelog，明确“主 Agent 有意识”在系统里等价于可验证的身份、目标、边界、决策依据和责任分发记录，而不是不可审计的人格化口号。

## Capabilities

### New Capabilities

- `main-agent-dispatch-awareness`: 主 Agent 在高风险编排前必须生成机器可读自检和加派决策，区分已登记 Agent 的动态加派、未登记 Agent 的 reviewed-package 候选，以及完成声明的阻断边界。

### Modified Capabilities

无稳定 OpenSpec spec 可修改；现有 `harden-a-to-a-task-contract-gates` 作为已完成变更背景，本变更新增更高一层的主 Agent 自检和动态派发能力。

## Impact

- Core：`core/orchestrator/a_to_a_task_contract.py`、`core/orchestrator/workflow_dispatch.py`、必要时 `core/orchestrator/route_audit_report.py`。
- Agents：`agents/pipeline/pipeline_manifest.json`、`agents/pipeline/README.md`、`agents/COMMON_PROMPT_CONTRACT.md`，必要时主编排 Agent 定义。
- CLI / checks：`scripts/run_a_to_a_orchestration_gate_check.py`。
- Tests：`tests/core/test_a_to_a_task_contract.py`、`tests/core/test_workflow_dispatch.py`。
- Docs：`docs/architecture/cad-agent-task-chain.md`、`docs/architecture/system-asset-sedimentation-protocol.md`、`docs/governance/cad-agent-rules.md`、`CORE_CONTEXT_BRIEF.md`、`docs/status/current.md`、`docs/status/changelog.md`、必要时 `docs/status/issues.md`。
- Non-goals：本变更不创建真正的新全局 Agent，不自动保存 DWG，不替代 CAD readback / visual review / reuse replay，不提升表 C，不把主 Agent 自我描述当作几何或资产复用证据。
