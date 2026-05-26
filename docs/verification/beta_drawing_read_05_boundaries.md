# BETA-DRAWING-READ-05 读图链路 Benchmark

最后更新：2026-05-26

> 机器入口：`core/drawing_analysis/drawing_read_benchmark.py`、`scripts/run_drawing_read_benchmark.py`。

## 目标

将 READ-01..04 固化为 **`drawing_read_benchmark.json`**：

| Case | 说明 |
| --- | --- |
| `geometry_feature_full_chain_pass` | fixture → 候选 → 报告 → 确认 → `SHELL_MODEL` |
| `modelspace_summary_and_candidates_pass` | 含 entity summary 的候选链路 |
| `walls_only_missing_opening_blocked` | 缺门洞 → `structured_blockers` + `blocked_expected_non_cad` |

## 已交付

| 项 | 说明 |
| --- | --- |
| Suite | `examples/benchmarks/drawing_read_benchmark.json` |
| Runner | `run_drawing_read_benchmark` + `benchmark_summary.json` |
| CLI | `run_drawing_read_benchmark.py` |
| 测试 | `tests/core/test_drawing_read_benchmark.py` |

## 不能声称什么

- benchmark pass **≠** `geometry_verified` 或真实 DWG 读图准确。
- blocked 样本 **≠** 已生成可用 SHELL_MODEL。
- 本包 **不** 驱动 blank-shell 落 CAD。

## 子校验

```powershell
& $py -m unittest tests.core.test_drawing_read_benchmark -v
& $py scripts\run_drawing_read_benchmark.py
```

## 父包收口

自动读图 / 空壳识别 READ-01..05 边界汇总见 `beta_drawing_read_acceptance.md`。
