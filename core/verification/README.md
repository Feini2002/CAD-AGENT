# core/verification

职责：验证 CAD 输出是否符合计划和用户意图，输出 `VERIFICATION_REPORT`。

目标能力：

- 回读 CAD 实体。
- 检查图层、数量、尺寸、范围、文字和标注。
- 保存截图或预览证据。
- 对比实际结果与 CAD_PLAN 或结构化意图。

当前迁移来源：

- `scripts/render_preview.py`
- `scripts/inspect_dwg.py`
- `scripts/self_check.py`
- `CAD_AGENT_BLOCKER_PLAYBOOK.md`

当前状态：prototype。自检、截图检查、`VERIFICATION_REPORT`、fake readback 几何比较、COM-like 实体标准化和 `inspect_dwg.py --connect-cad` 显式入口已建立；真实 CAD 实体回读仍需在已打开 DWG 中实机验证。

边界：

- 没有截图或实体回读证据时，不能声称图已经画准。
- 视觉证据和实体回读应互相补充；冲突时优先定位差异原因。
- 场景 Agent 不应绕过 Core 验证门。
