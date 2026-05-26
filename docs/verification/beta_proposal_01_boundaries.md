# BETA-PROPOSAL-01 候选评分字段与排序原因

最后更新：2026-05-26

> 后置主线「多方案设计与交互确认」第 1 小包。

## 目标

固化 `DESIGN_PROPOSAL.candidates[]` 上的机器可读评分与排序解释：

| 字段 | 说明 |
| --- | --- |
| `score_breakdown` | `layout_base` / `check_penalty` / `preference_boost` + `weighted_score` |
| `ranking_reasons` | `{code, message, component?}` 列表 |

## 已交付

| 项 | 说明 |
| --- | --- |
| Schema | `proposal_candidate_scoring.schema.json`；`design_proposal.schema.json` 扩展 |
| Core | `core/proposal_engine/candidate_scoring.py` |
| 接入 | `compare_layout_candidates`、`create_design_proposal`、blank-shell `comparison_detail` 分支 |
| 测试 | `tests/core/test_proposal_candidate_scoring.py` |

## 不能声称什么

- 结构化 `ranking_reasons` **不是** 用户已确认的最终决策。
- `weighted_score` 高 **≠** `geometry_verified`。
- 本包 **不包含** 用户确认 schema（`BETA-PROPOSAL-03`）或确认后 CAD_PLAN（`05`）。

## 子校验

```powershell
& $py -m unittest tests.core.test_proposal_candidate_scoring -v
& $py -m unittest tests.core.test_proposal_comparison tests.core.test_proposal_multi_candidate -v
```

## 下一小包

`BETA-PROPOSAL-02`（已完成）：见 `beta_proposal_02_boundaries.md`。
