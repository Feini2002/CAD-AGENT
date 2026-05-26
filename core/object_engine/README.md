# core/object_engine

职责：生成跨场景可复用的参数化 CAD 对象，输出 `OBJECT_SPEC`，再交给方案、计划和执行链路。

首批目标对象：

- 柜子。
- 货架。
- 桌子。
- 床、椅子、沙发、办公桌等扩展对象。

未来对象：

- 墙板、隔断、复杂展示柜、属性块对象等。

当前状态：prototype。`parametric_objects.py` 已支持常见家具 / 商业对象的最小 `OBJECT_SPEC`，并可转换为预览用 `CAD_PLAN`。`detail_plan.py` 可把 table、bed、chair、sofa、desk 展开为组件级安全预览 `CAD_PLAN`，例如餐桌可生成桌面 + 四个支撑。现有能力仍是第一批原型，不代表复杂对象引擎、真实块库或属性块已完成。

边界：

- 本模块负责对象结构、尺寸、构件和表达方式。
- 风格规则来自 `core/style_engine`。
- 落图由 `core/plan_engine` 和 `core/execution` 完成。
