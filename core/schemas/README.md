# core/schemas

职责：定义通用 CAD Agent Core 的机器可校验数据模型。这里服务所有场景 Agent，不为某一个工装、家装或店铺项目写死字段。

优先模型：

- `DESIGN_BRIEF`
- `DRAWING_MODEL`
- `PROJECT_MODEL`
- `OBJECT_SPEC`
- `STYLE_PROFILE`
- `BLOCK_LIBRARY`
- `LAYOUT_PROPOSAL`
- `DESIGN_PROPOSAL`
- `VERIFICATION_REPORT`
- `CAD_PLAN`

当前状态：scaffold。CAD_PLAN、CAD_CONTEXT、CAD_OBJECT schema 已复制到本模块；旧 `schemas/` 下保留过渡期兼容副本。

边界：

- 高层模型描述设计意图、图纸理解、项目上下文和方案。
- `CAD_PLAN` 只作为最终落图指令。
- 场景 Agent 可以扩展字段或默认值，但不应复制 Core schema。
