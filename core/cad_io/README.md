# core/cad_io

职责：封装 CAD 软件连接和底层 IO 差异，为 Core 提供统一绘制、插块、读实体、截图和保存前检查接口。

目标适配：

- CAD-MCP
- AutoCAD COM
- ZWCAD COM
- DXF 输出

当前状态：prototype。现有 AutoCAD/ZWCAD/DXF 驱动已迁入本模块，`drivers/` 下保留兼容包装器。

边界：

- 本模块只负责“怎么和 CAD 交互”。
- 不负责理解用户白话、生成布局或决定设计方案。
- 所有正式写入、保存、覆盖和删除动作必须经过 `core/safety`。
