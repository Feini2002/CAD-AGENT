# BETA-PROJECT-SAMPLE-04 项目样本 Benchmark

最后更新：2026-05-26

> 机器入口：`examples/benchmarks/project_sample_benchmark.json`、`scripts/run_project_sample_benchmark.py`。

## 目标

将 **`projects/` 路径** 的 blank-shell workflow 纳入 benchmark：

| case | 预期 |
| --- | --- |
| `sample_blank_shell_pass` | `benchmark_pass_non_cad`，`cad_plan_count≥5` |
| `sample_blank_shell_too_small_blocked` | `blocked_expected_non_cad`，`cad_plan_count=0` |

## 已交付

| 项 | 说明 |
| --- | --- |
| Benchmark | `project_sample_benchmark.json`（2 cases） |
| 失败样本 | `projects/sample_blank_shell_too_small/` + `sample_blank_shell_too_small_loop.json` |
| Runner | `core/project_samples/benchmark.py` |
| CLI | `scripts/run_project_sample_benchmark.py` |
| 测试 | `tests/core/test_project_sample_benchmark.py` |

## 证据摘要

`benchmark_summary.json` 应满足：

- `non_cad_only: true`
- `readback_geometry_verified_count: 0`
- `benchmark_pass_non_cad_count: 1`
- `blocked_expected_non_cad_count: 1`

## 不能声称什么

- benchmark pass **≠** `geometry_verified`。
- blocked case **不是** 真实项目交付物。

## 子校验

```powershell
& $py -m unittest tests.core.test_project_sample_benchmark -v
& $py scripts\run_project_sample_benchmark.py
```

## 下一小包

`BETA-PROJECT-SAMPLE-05`（已完成）：见 `beta_project_sample_05_boundaries.md`。
