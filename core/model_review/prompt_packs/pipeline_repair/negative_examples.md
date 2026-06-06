# Negative Examples

- 错误：`scopeMode="whole_modelspace"`，理由是“清理旧内容更快”。原因：广域范围默认 hard fail。
- 错误：`operations=[{"action":"delete_all"}]`。原因：只允许 `update/delete_replace/add_missing/annotate_for_review`。
- 错误：输出 `cadCommands` 或 `executionAuthorized=true`。原因：修复 Agent 只给 proposal_only。
- 错误：没有 target handles / bbox，却建议删除。原因：删除必须有目标证据、victim preview 和邻区保护。
- 错误：把模型修复建议说成“已完成修复”。原因：真实修复必须由 CAD 执行链路和 readback 证明。
