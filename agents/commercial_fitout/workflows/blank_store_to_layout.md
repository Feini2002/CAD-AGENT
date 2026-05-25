# blank_store_to_layout

商业空壳布局 workflow 只负责施加商业场景偏好，不实现通用布局算法。

```text
DESIGN_BRIEF
-> PROJECT_MODEL
-> commercial_fitout preferences
-> core.layout_engine creates LAYOUT_PROPOSAL
-> core.proposal_engine creates DESIGN_PROPOSAL
-> confirmed proposal converts to CAD_PLAN
-> core.execution draws to CODEX_PREVIEW
-> core.verification creates VERIFICATION_REPORT
```

## 场景偏好

- 入口展示优先。
- 收银台靠近出入口控制点，但不阻断主动线。
- 主通道默认 1200 mm，次通道默认 900 mm。
- 货架、展示柜和重点陈列成组布置。

## 禁止事项

- 不在本 workflow 中实现碰撞检测。
- 不在本 workflow 中实现 CAD 实体生成。
- 不绕过 Core 直接绘图。
