# Verification Templates

本目录保存 CAD Agent Core 的验证模板。当前 CAD 环境可能不稳定时，非 CAD
能力可以先通过单测、schema、dry-run、fake readback 和 benchmark 自检；凡是需要
真实 AutoCAD / CAD-MCP / 截图 / 实体回读证明的内容，统一登记到
唯一 PlanMD `../../CORE_RESTRUCTURE_PLAN.md` 的 CAD 延后补验清单，并按本目录模板补证据。

新增能力的记录规则：

- 不依赖 CAD 的能力：当轮必须跑自动化测试，并在计划中标明对应命令。
- 依赖真实 CAD 的能力：先登记补验项，不得在补验前声明几何准确。
- 生成新的 CAD_PLAN：必须保留 validate、dry-run 和后续 execute/readback/screenshot 的补验入口。

