# CAD_PLAN Boundary

`CAD_PLAN` 是最终落图指令，不是设计大脑。

## CAD_PLAN 应该包含

- 要画的对象类型和名称。
- 已确定的尺寸、基点和图层。
- 绘图意图，例如 `draw_object`。
- 是否加标签、标注等执行层开关。
- 置信度和是否需要确认。

## CAD_PLAN 不应该包含

- 用户需求的完整推理过程。
- 多方案比较。
- 布局评分和候选集。
- 图纸理解的不确定点全集。
- 场景 Agent 的业务偏好全集。

这些内容分别进入：

- `DESIGN_BRIEF`
- `DRAWING_MODEL`
- `PROJECT_MODEL`
- `OBJECT_SPEC`
- `STYLE_PROFILE`
- `BLOCK_LIBRARY`
- `LAYOUT_PROPOSAL`
- `DESIGN_PROPOSAL`
- `VERIFICATION_REPORT`

## 当前执行边界

当前 `core.execution.execute_plan` 仍是最小原型，只支持：

- `intent=draw_object`
- `placement.mode=absolute`
- `drawing.layer=CODEX_PREVIEW`
- 用 `width` 和 `depth` 绘制平面预览矩形
- 可选文字和两条基础尺寸标注

后续对象、风格、布局和方案引擎都必须先生成合法 `CAD_PLAN`，再进入执行层。
