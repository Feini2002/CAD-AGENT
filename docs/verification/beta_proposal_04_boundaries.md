# BETA-PROPOSAL-04 局部修改后重算 CAD_PLAN

最后更新：2026-05-26

> 机器入口：`core/proposal_engine/partial_replan.py`、`scripts/run_proposal_partial_replan.py`。

## 目标

在已有 blank-shell pipeline 产物上，仅根据 **placement 局部修改**（或 `user_confirmation.local_preferences.placement_offsets`）重算：

- `layout_proposal`（同步 placements）
- `cad_plan` / `cad_plans` / `cad_plan_items`
- `dry_run_*` / `verification_*`

**不重跑**：`shell_model`、`project_model`、`circulation_candidates`、`candidate_sets`、`function_zones`。

## 已交付

| 项 | 说明 |
| --- | --- |
| Core | `recompute_cad_plans_from_pipeline_artifacts()` |
| 报告 | `partial_replan_report.json`（`modules_skipped` / `modules_recomputed`） |
| CLI | `run_proposal_partial_replan.py` |
| 测试 | workflow 回归：上游 artifact hash 不变、CAD base_point 变化、dry-run valid |

## 不能声称什么

- 局部 replan **≠** `geometry_verified`。
- 未重跑上游 **≠** 修改 shell / 动线后仍自动一致（需完整 pipeline）。

## 子校验

```powershell
& $py -m unittest tests.core.test_proposal_partial_replan -v
```

## 下一小包

`BETA-PROPOSAL-05`（已完成）：见 `beta_proposal_05_boundaries.md`。
