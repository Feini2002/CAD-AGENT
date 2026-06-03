## Why

用户用“在旁边画个……”这类白话时，真实意图通常不是给一个 CAD 世界坐标，而是希望 Agent 像设计师坐在电脑前一样，理解当前屏幕视域、视觉焦点和附近空位。现有 `CAD_PLAN.placement` 能表达 `absolute`、`space_reference` 和 `relative_to_object`，但缺少“当前我看到的这一屏旁边”的可审计解析过程，容易把测试内容画到全图远处、全局最右侧或需要移动视角才看得到的位置。

本变更把“旁边”正式定义为设计师视角下的邻近放置语义：先理解当前视口和可见内容，再把白话位置解析成确定的 CAD 坐标，并保留 evidence boundary。

## What Changes

- 新增“设计师视角邻近放置”能力：把“旁边 / 附近 / 边上 / 右边 / 上方”等白话位置解析为当前视口内、围绕视觉焦点簇的候选空位。
- 新增 `CAD_VIEW_CONTEXT` / 等价上下文契约，用于记录当前视口范围、可见实体摘要、焦点来源、最近 created handles、选中对象和屏内安全边界。
- 新增 placement resolution 报告：记录锚点来源、候选方向、距离 / 间距、可见性、碰撞避让、最终 `base_point` 和 `not_checked`。
- 扩展 `CAD_PLAN.placement` 的使用口径：白话“旁边”不得直接跳到任意绝对点，必须先经过视域邻近解析；最终执行仍使用确定的 `absolute base_point` 或明确的结构化 placement contract。
- 新增验证门槛：落图后回读 created handles / bbox，确认目标对象仍在当前视域或声明无法证明；不能通过自动 zoom / pan 把远处结果伪装成“旁边”。
- 保留 preview-only 安全边界：真实 CAD 小动作默认只写 `CODEX_PREVIEW`，不保存 DWG，不修改正式图层。
- 不改变表 C、capability registry 或施工图能力口径；本变更先建立通用底座语义和可执行任务，不声明已经会稳定绘制任何具体对象族。

## Capabilities

### New Capabilities

- `designer-view-nearby-placement`: 将当前设计师视角中的“旁边 / 附近”解析为可审计 CAD 放置位置，并证明新对象位于当前视口邻近空位。

### Modified Capabilities

- 无。

## Impact

- 影响 `CAD_PLAN` 生成链路、`placement` 语义、CAD 上下文采集、preview 执行审计和训练期主 Agent 的空间理解规则。
- 可能新增 `core/placement/` 或 `core/layout_engine/` 下的视域邻近解析器、`core/schemas/` 下的 view context / resolution schema、以及 scripts 自测入口。
- 需要新增单元测试和 no-CAD fixture，覆盖锚点选择、候选区排序、视口内约束、碰撞避让、无法放置时的阻断声明。
- 真实 AutoCAD 验收应使用当前视口 / 可见实体 / created handles 回读；不依赖截图即可完成基础证明，截图只作为人工视觉辅助。
