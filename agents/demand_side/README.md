# Demand Side Role Agents

本目录记录“需求侧角色 Agent”。它们模拟不同场景里的真实用户如何向 CAD Agent 提需求，用于压力测试 Core 和场景轻量层。

这是开发期脚手架，不是最终产品形态。它的价值在于驱动对象生成、组合生成、读图、布局、验证等能力开发；等能力沉淀完成后，可以清理角色表和需求侧表单，只保留最终能力与回归测试。

这些 Agent 是数据记录，不是绘图实现：

- 不写 Python。
- 不直接执行 CAD。
- 不绕过 `CAD_PLAN`、validate、dry-run 或真实 CAD readback。
- 不把 non-CAD benchmark pass 写成 Scene Product 完成。

第一版角色覆盖 `residential`、`office`、`restaurant`、`commercial_fitout`、`exhibition` 和 `custom` 六个当前场景。
