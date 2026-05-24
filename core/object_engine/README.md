# core/object_engine

职责：生成跨场景可复用的参数化 CAD 对象，输出 `OBJECT_SPEC`，再交给方案、计划和执行链路。

首批目标对象：

- 柜子。
- 货架。
- 桌子。

未来对象：

- 收银台、床、墙板、隔断、展示柜等。

当前状态：not_started。现有测试柜只是执行层样例，不代表对象引擎已完成。

边界：

- 本模块负责对象结构、尺寸、构件和表达方式。
- 风格规则来自 `core/style_engine`。
- 落图由 `core/plan_engine` 和 `core/execution` 完成。
