# BETA-PROPOSAL-05 确认后受控 CAD_PLAN

最后更新：2026-05-26

> 机器入口：`confirmed_finalize.py`、`confirmed_cad_plan_bundle.json`、`proposal_confirmed_benchmark.json`。

## 目标

用户确认后输出 **受控 CAD_PLAN bundle**：

- 全部 `CAD_PLAN`：`CODEX_PREVIEW`、`needs_confirmation=false`
- `validate_plan` + `dry_run` 全通过
- **`unselected_candidate_evidence`** 保留未选候选与拒绝原因

## 已交付

| 项 | 说明 |
| --- | --- |
| Core | `finalize_confirmed_cad_plans()` |
| Bundle | `confirmed_cad_plan_bundle.json` + schema |
| Benchmark | `proposal_confirmed_benchmark.json`（2 cases） |
| 父包 rollup | `proposal_acceptance.py` |
| CLI | `run_proposal_confirmed_finalize.py`、`run_proposal_confirmed_benchmark.py` |

## 不能声称什么

- validate + dry-run pass **≠** `geometry_verified`。
- 保留未选证据 **≠** 自动否决或替用户做最终决策。

## 子校验

```powershell
& $py -m unittest tests.core.test_proposal_confirmed_finalize tests.core.test_proposal_confirmed_benchmark -v
```

## 父包收口

`BETA-PROPOSAL-01`～`05` 见 `beta_proposal_acceptance.md`。
