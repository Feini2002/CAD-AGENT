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

当前状态：prototype。CAD_PLAN、CAD_CONTEXT、CAD_OBJECT schema 已复制到本模块；高层模型 schema 已建立第一批最小版本：

- `design_brief.schema.json`
- `drawing_model.schema.json`
- `project_model.schema.json`
- `object_spec.schema.json`
- `style_profile.schema.json`
- `block_library.schema.json`
- `layout_proposal.schema.json`
- `design_proposal.schema.json`
- `verification_report.schema.json`
- `symbol_spec.schema.json`
- `symbol_graph.schema.json`
- `reference_asset.schema.json`
- `system_asset.schema.json`
- `asset_annotation.schema.json`
- `asset_promotion.schema.json`
- `asset_evidence_boundary.schema.json`
- `retrieval_pack.schema.json`

旧 `schemas/` 下只保留第一轮兼容副本，不继续扩展为所有高层 schema 的镜像。

## 校验入口

`core/schemas/validator.py` 提供无外部依赖的轻量 JSON Schema 子集校验，用于验证 `examples/` 中的高层模型示例。`CAD_PLAN` 的执行前校验仍由 `core.plan_engine.validate_plan` 负责。

边界：

- 高层模型描述设计意图、图纸理解、项目上下文和方案。
- `CAD_PLAN` 只作为最终落图指令。
- 场景 Agent 可以扩展字段或默认值，但不应复制 Core schema。
