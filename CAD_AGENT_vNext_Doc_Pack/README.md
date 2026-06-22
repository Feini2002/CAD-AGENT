# CAD-AGENT vNext 文档包

将 `docs/vnext/` 整体复制到仓库。

阅读与执行顺序：

1. `docs/vnext/ARCHITECTURE_DECISION.md`：架构边界、Gate 0 定义和 Gate 0 后路线。
2. `docs/vnext/IMPLEMENTATION_MASTER_PLAN.md`：唯一逐包执行计划；Codex 每次只执行一个 VN Work Package。

首次指令使用实施主计划第 28 节，只执行 `VN-00`。

不要在第一次提交中直接替换或删除旧 `CORE_*`、training、workbench、OpenSpec 和 output；先冻结、记录基线，再按 Work Package 迁移。
