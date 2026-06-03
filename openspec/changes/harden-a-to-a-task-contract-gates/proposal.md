## Why

系统资产 DWG 仓库式排版连续偏离用户意图时，问题不是单纯缺视觉能力，而是 A-to-A 编排层没有先把任务拆成责任 Agent 合同。已有视觉验收、资产守门员或 CAD readback 如果没有被主 Agent 明确派发并作为 hard gate 回收，就会被执行链绕过。

本变更把“主 Agent 是否该派发哪些 Agent”从临场判断升级为机器可读 `a_to_a_task_contract`：先声明本次任务语义、必需 Agent、hard gates、缺失输出和失败门禁，再决定是否允许 dispatch / delivery。

## What Changes

- 新增 A-to-A TaskContract 构建器，用于识别系统资产沉淀、系统资产 DWG 仓库式排版和视觉布局复审任务。
- 主编排入口在 ordinary workflow dispatch 前生成合同；合同 blocked 时，`workflow_dispatch` 必须以 `a-to-a hard gate` 阻断。
- 新增 `pipeline_visual_layout_reviewer` Agent，专门复审仓库 / 货架 / 置物架 / 动线 / 可扩展货位 / 展示形式等视觉布局语义。
- 扩展 pipeline manifest：登记 `asset_dwg_layout` flow、`visual_layout_review` hard gate、`asset_dwg_curation` 和 `asset_reuse_audit` hard gate。
- 新增仓库级治理检查脚本，验证 Agent 注册、合同识别、缺 Agent 输出阻断和 pass 输出放行。
- 同步架构文档、全局规则、短上下文、状态、changelog 和 issues。

## Capabilities

### New Capabilities

- `a-to-a-task-orchestration`: 主 Agent 任务合同、必需 Agent 派发、缺失输出阻断和视觉布局复审 hard gate。

### Modified Capabilities

- `system-asset-library-governance`: 系统资产沉淀和系统资产 DWG 布局现在必须由 A-to-A TaskContract 显式声明责任 Agent 与 hard gates。

## Impact

- Core：`core/orchestrator/a_to_a_task_contract.py`、`core/orchestrator/workflow_dispatch.py`
- Agents：`agents/pipeline/pipeline_manifest.json`、`agents/pipeline/visual_layout_reviewer/agent.json`
- CLI / checks：`scripts/run_a_to_a_orchestration_gate_check.py`
- Tests：`tests/core/test_a_to_a_task_contract.py`
- Docs：`AGENTS.md`、`CORE_CONTEXT_BRIEF.md`、`docs/architecture/cad-agent-task-chain.md`、`docs/status/*`
- Non-goals：本变更不重画系统资产 DWG、不保存当前业务 DWG、不替代真实 CAD readback、不提升表 C。
