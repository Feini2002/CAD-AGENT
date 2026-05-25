# Scene Agent Rules

场景 Agent 是轻量偏好层，不是第二套 Core。

## 可以放在 Agent 中

- 场景词汇。
- 默认参数。
- 业务偏好。
- workflow 名称和步骤说明。
- 评分权重。
- 对 `libraries/` 资源的优先级。

## 不可以放在 Agent 中

- 通用对象生成算法。
- 通用碰撞检测。
- 通用通道宽度算法。
- 通用图纸读取。
- 通用 `CAD_PLAN` 校验、dry-run、执行、截图、实体回读。
- 真实项目资料。
- 公司专属块库本体。

这些能力应放在 `core/`、`libraries/` 或 `projects/` 的对应边界内。

## 执行要求

Agent workflow 必须先输出高层模型或结构化意图，再进入 `CAD_PLAN`。真实落图前仍然需要 validate、dry-run、`CODEX_PREVIEW` 和 `VERIFICATION_REPORT`。
