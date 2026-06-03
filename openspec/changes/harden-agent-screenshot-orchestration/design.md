## Context

`task-scoped-cad-preview-capture` 已完成底层能力：`prepare_autocad_for_capture()` 可按 `target_handles`、`repair_plan`、`target_bbox` 或 `execution_summary.created_handles` 聚焦，并用 AutoCAD 客户区 `PrintWindow` 截图。剩余缺口在编排层：不同 runner 和 Agent 需要自己判断何时截图、传什么目标、如何报告截图边界，容易漏掉局部目标或把截图误当几何证明。

## Goals / Non-Goals

**Goals:**

- 新增统一截图编排模型，输出可测试的 `screenshotDecision` / `visualPreview` payload。
- 让 runner 和训练入口能用同一函数表达截图意图，默认选择最精确的 focus target。
- 让 Agent 共享合同和工作台校验明确截图能力：何时调用、如何聚焦、证据边界是什么。
- 保留真实 CAD 修复交付门禁：本变更收尾必须跑真实或代表性截图链路。

**Non-Goals:**

- 不重写 `PrintWindow` / COM 截图底层实现。
- 不把截图升级为几何准确证据。
- 不保存当前业务 DWG，不修改正式图层，不扩大删除 / 编辑权限。

## Decisions

1. **在 `render_preview.py` 内新增轻量编排函数，而不是新建独立服务。**
   - 原因：现有截图焦点选择、CLI 参数、payload 都在该模块内，新增决策层可复用内部 normalization。
   - 替代方案：新建 `core/verification/screenshot_orchestrator.py`。暂不采用，避免在短期内拆散已经稳定的截图底座。

2. **以结构化原因驱动截图，而不是依赖自然语言 prompt。**
   - 编排输入使用 `task_kind`、`evidence_stage`、`repair_plan`、`target_handles`、`execution_summary`、`agent_role` 等字段。
   - 输出说明 `shouldCapture`、`required`、`focusSource`、`visualAidOnly`、`recommendedCall` 和 blocker 原因，供 runner / Agent check 检查。

3. **Agent 理解通过共享合同 + 机器校验双层保证。**
   - `agents/COMMON_PROMPT_CONTRACT.md` 记录通用截图原则。
   - `scripts/run_training_workbench_agent_check.py` 检查每个责任 Agent 是否引用共享合同，且共享合同包含截图编排、局部聚焦和 `visual_aid_only` 边界。

4. **runner 接入以最小改动为主。**
   - 已接入 `prepare_autocad_for_capture()` 的入口保留，但要报告截图决策 payload。
   - 仍直接调用 `visual_preview_payload()` 的地方改为通过统一决策生成证据字段。

## Risks / Trade-offs

- **风险：Agent 只背提示词但 runner 不执行。** → 用测试锁住 runner payload 和工作台 Agent check。
- **风险：截图决策过重，拖慢 quick trial。** → 决策允许 `required=false`，`quick_trial` 只在用户要求正式复核、视觉问题或关键回读不足时升级截图。
- **风险：真实 CAD 当前不可连接。** → 按 `REPAIR-RUN-BEFORE-DELIVERY-01` 自救和必要提权；仍失败时标记 `not_verified`，不使用完成口吻。
