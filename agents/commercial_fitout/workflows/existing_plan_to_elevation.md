# existing_plan_to_elevation

已有平面到立面 workflow 只负责商业场景目标选择，不实现通用图纸理解或立面生成算法。

```text
Existing CAD/PDF
-> core.drawing_analysis creates DRAWING_MODEL
-> core.project_model creates PROJECT_MODEL
-> commercial_fitout chooses priority elevation targets
-> core.proposal_engine creates DESIGN_PROPOSAL
-> confirmed proposal converts to CAD_PLAN
-> core.execution draws to CODEX_PREVIEW
-> core.verification creates VERIFICATION_REPORT
```

## 场景偏好

- 展示墙优先。
- 收银背墙优先。
- 店铺入口和橱窗方向优先。

## 禁止事项

- 不在本 workflow 中读 CAD 实体。
- 不在本 workflow 中实现立面几何算法。
- 不绕过 `CAD_PLAN`、validate、dry-run 和验证门。
