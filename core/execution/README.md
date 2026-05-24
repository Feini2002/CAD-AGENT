# core/execution

职责：执行已经校验和预演过的 `CAD_PLAN`，默认写入 `CODEX_PREVIEW`。

当前迁移来源：

- `scripts/execute_plan.py`

当前状态：prototype。现有执行器已能绘制最小测试柜对象、文字和基础尺寸标注。

边界：

- 不默认保存当前 DWG。
- 不默认覆盖原图。
- 不默认修改正式图层。
- 不删除正式实体。
- 高风险动作必须经过 `core/safety` 和用户明确批准。
