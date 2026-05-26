# BETA-CAD-BLOCK-01 受控 Block Beta 边界

最后更新：2026-05-26

> 后置主线：**真实 CAD 能力扩展** 第 1 小包。机器入口：`examples/plans/block_alpha_beta_suite.json`、`core/verification/block_alpha_beta_suite.py`。

## 目标

在 `R-BLOCK-CAD-ALPHA` 与 `R4-EVIDENCE-GATES` 收口基础上，扩展受控 `insert_block_alpha` **non-CAD** beta 用例：多插入锚点（`base_point`）、多 `rotation`、多 **uniform** `scale`。

## 已交付

| 项 | 说明 |
| --- | --- |
| Suite | 8 cases：`beta_anchor_*`、`beta_rotation_*`、`beta_scale_*`、`beta_combined_transform` |
| Runner | `run_block_alpha_beta_suite()`；CLI `scripts/run_block_alpha_beta_suite.py` |
| 测试 | `tests/core/test_block_alpha_beta_suite.py` |

## 现在可以声称什么

- 受控块 `controlled-test-block-001` / `CODEX_TEST_BLOCK_001` 的 CAD_PLAN 在多种锚点、旋转、统一缩放下均可 **validate + dry-run valid**。
- 全部用例 `evidence_state=dry_run_valid_plan_only`，`geometry_accuracy=not_verified_without_cad_readback`。

## 不能声称什么

- **不是**真实 CAD `geometry_verified`（本包未跑 COM 插入与 created-handle readback）。
- **不是**任意公司块库或项目块；仍仅限受控测试块。
- **不是**非 uniform scale（alpha 仍拒绝 `[1,2,1]` 等）。

## 子校验

```powershell
& $py -m unittest tests.core.test_block_alpha_beta_suite -v
& $py scripts\run_block_alpha_beta_suite.py --output-root output\test_artifacts\block_alpha_beta\beta_cad_block_01
```

## 下一小包

`BETA-CAD-BLOCK-03`：hatch / polyline / layer mapping 受控写读探针。
