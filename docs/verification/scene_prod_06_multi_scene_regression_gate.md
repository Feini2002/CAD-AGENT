# SCENE-PROD-06 Multi-Scene Regression Gate

最后更新：2026-05-27

## 包边界

`SCENE-PROD-06-MULTI-SCENE-REGRESSION-GATE` 对应 `BETA-SCENE-05`，用于把 office / residential / restaurant 三个 scene beta benchmark 放进同一个 no-CAD 回归门禁，并同步检查 `SCENE-PROD-05` 解释模板和 `REST-PROD-04` 多场景 P3 rollup 仍可读。

入口：

- `core.agents.scene_regression_gate.run_scene_prod_06_regression_gate`
- `scripts/run_scene_prod_06_regression_gate.py`

## 门禁内容

| 场景 | benchmark | 期望 |
| --- | --- | --- |
| office | `examples/benchmarks/office_scene_beta_benchmark.json` | 9/9 pass |
| residential | `examples/benchmarks/residential_scene_beta_benchmark.json` | 8/8 pass |
| restaurant | `examples/benchmarks/restaurant_scene_beta_benchmark.json` | 8/8 pass |

附加门禁：

- `scene_beta_explanation_status_summary()` 必须覆盖三个场景。
- `multi_scene_p3_wave_status_summary()` 必须继续能读取 office + restaurant P3 rollup。
- `readback_geometry_verified_count` 必须为 0。
- 交付时必须运行 repo audit：`scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings`。

## 证据口径

本包只允许下列 no-CAD 证据态：

- `benchmark_pass_non_cad`
- `blocked_expected_non_cad`
- `not_verified_without_cad_readback`

## 不得声称

- 不得把 selected benchmarks pass 写成真实 CAD `geometry_verified`。
- 不得把场景偏好解释模板写成完整 Scene Product。
- 不得把 office / residential / restaurant benchmark 通过扩大为真实项目 DWG 或施工图准确。
- 不得用 repo audit 通过替代 CAD created handles readback。
