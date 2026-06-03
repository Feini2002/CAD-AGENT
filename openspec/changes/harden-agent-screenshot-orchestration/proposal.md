## Why

当前截图底座已经能按任务句柄或局部修复 bbox 聚焦，但调用仍分散在 runner、训练脚本和 Agent Prompt 里。用户要求系统各个 Agent 真实理解截图能力并智能调用，因此需要把“什么时候截图、截谁、截图证据怎么表述”提升为统一编排契约。

## What Changes

- 新增截图编排决策层，用结构化输入判断是否需要截图、应使用哪类 focus target、是否需要真实 CAD / PrintWindow / fallback。
- 将 Agent 共享合同和工作台 Agent check 接入截图能力理解，确保责任 Agent 知道截图是 `visual_aid_only`，并知道局部修复、单项复验、训练验收和视觉反馈时的默认调用方式。
- 将 runner / 训练入口统一到截图编排 payload，避免只手写 `capture_autocad_window()` 或忘传 `execution_summary` / `repair_plan`。
- 保留保护用户 DWG 边界：默认只写 / 只看 `CODEX_PREVIEW`，截图不保存当前业务 DWG，不修改正式图层。

## Capabilities

### New Capabilities

- `agent-screenshot-orchestration`: 系统根据任务上下文、局部修复目标、执行摘要、证据等级和 Agent 角色自动决定截图调用与证据表述。

### Modified Capabilities

- `task-scoped-cad-preview`: 复用已完成的任务级精准截图协议；本变更只增加调用编排和 Agent 理解，不改变其底层聚焦优先级。

## Impact

- 影响 `core/verification/render_preview.py` 及其测试。
- 影响 `core/verification/visual_cad_review.py`、`core/training/foundation_batch_training.py` 等调用方的 payload 口径。
- 影响 `agents/COMMON_PROMPT_CONTRACT.md`、各责任 Agent addendum / memory 的截图规则理解。
- 影响 `scripts/run_training_workbench_agent_check.py` 与训练工作台同步校验。
- 影响状态记录和交付验证：本包必须运行单测、OpenSpec strict validate、截图 check，并在 AutoCAD 可用时补真实精准截图链路。
