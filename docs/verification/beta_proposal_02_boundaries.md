# BETA-PROPOSAL-02 候选对比摘要 Benchmark

最后更新：2026-05-26

> 机器入口：`proposal_comparison_summary.json`、`examples/benchmarks/proposal_comparison_benchmark.json`。

## 目标

将 `comparison_detail` 提炼为 benchmark 可断言的 **`proposal_comparison_summary`**：

| 区块 | 字段 |
| --- | --- |
| `object_coverage` | 请求/已放置类型、覆盖率、计数 |
| `circulation` | 连续性、选中策略、blocked 策略 |
| `conflicts` | failed checks、placement 失败 |
| `failure_reasons` | 全量 / 选中分布 |
| `ranking_reason_codes` | 结构化排序原因 code 列表 |

## 已交付

| 项 | 说明 |
| --- | --- |
| Core | `comparison_summary.py`、`build_proposal_comparison_summary()` |
| Pipeline | `proposal_comparison_summary.json` artifact + metrics 扁平化 |
| Benchmark | `proposal_comparison_benchmark.json`（4 cases）+ runner 新断言键 |
| CLI | `scripts/run_proposal_comparison_benchmark.py` |
| 测试 | `tests/core/test_proposal_comparison_benchmark.py` |

## Benchmark 断言键（新增）

- `requires_proposal_comparison_summary`
- `proposal_comparison_summary_minimums`
- `circulation_continuity_equals`
- `contains_ranking_reason_code`
- `blocked_circulation_strategies_include`

## 不能声称什么

- 对比摘要 **≠** 用户已确认方案。
- summary pass **≠** `geometry_verified`。

## 子校验

```powershell
& $py -m unittest tests.core.test_proposal_comparison_benchmark -v
& $py scripts\run_proposal_comparison_benchmark.py
```

## 下一小包

`BETA-PROPOSAL-03`（已完成）：见 `beta_proposal_03_boundaries.md`。
