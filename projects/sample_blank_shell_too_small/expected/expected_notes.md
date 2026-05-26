# Sample Too-Small Shell Expected Notes

本样本用于 **structured blocked** benchmark，不得当作成功布局参考。

- workflow 设置 `layout_expectation.mode=require_all_placed`。
- 预期 pipeline `status=blocked`，`failure_category=insufficient_space`。
- **不得** 输出 `cad_plan`（`cad_plan_count=0`）。
- 不得声称 `geometry_verified`。
