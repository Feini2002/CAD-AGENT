# core/plan_engine

职责：把对象、布局、立面、标注和方案转换成最终 `CAD_PLAN`，并提供 validate 与 dry-run。

当前迁移来源：

- `schemas/cad_plan.schema.json`
- `scripts/validate_plan.py`
- `scripts/dry_run_plan.py`
- `examples/plans/`

当前状态：prototype。validate/dry-run 实现已迁入本模块，`scripts/` 下保留兼容包装器。

边界：

- `CAD_PLAN` 是落图指令，不是设计大脑。
- 高层推理应发生在 project、object、layout 和 proposal 模块。
- 任何 CAD_PLAN 执行前必须先通过 validate 和 dry-run。
