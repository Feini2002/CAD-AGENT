# LCAD-08：项目样本 CAD 闭环边界

最后更新：2026-05-27（CFIT-11 三工装样本口径同步）

> 机器入口：`examples/cad_regression/project_sample_cad_rollup.json`  
> 执行：`scripts/run_project_sample_cad_rollup.py`

## 注册样本

| sample_id | 工作流 | CAD 报告 |
| --- | --- | --- |
| `sample_blank_shell` | `sample_blank_shell_project_loop.json` | `project_sample_cad_check_report.json` |
| `commercial_fitout_sample` | `commercial_fitout_sample_confirmation_loop.json` | `commercial_fitout_cad_smoke_report.json` |
| `commercial_fitout_meeting_sample` | `commercial_fitout_meeting_sample_confirmation_loop.json` | `commercial_fitout_cad_smoke_report.json` |
| `commercial_fitout_reception_sample` | `commercial_fitout_reception_sample_confirmation_loop.json` | `commercial_fitout_cad_smoke_report.json` |

## 可声称（有证据时）

- 各样本在 `CODEX_PREVIEW` 上执行确认后的 `cad_plan_items`，并按 **created handles** 定向回读。
- Rollup 状态 `geometry_verified` 仅当 **全部** 注册样本均 verified。

## 工装三样本口径（CFIT-11）

| 子场景 | `sample_id` | 与 `product_alpha_boundary.json` |
| --- | --- | --- |
| `open_office` | `commercial_fitout_sample` | `deidentified_project_samples[0]` |
| `meeting_room` | `commercial_fitout_meeting_sample` | 同上表；`fitout_sample_specs.subscene_id` |
| `reception` | `commercial_fitout_reception_sample` | 同上；rollup manifest 第四行工装样本 |

同步断言：`core/agents/commercial_fitout_product_boundary.assert_fitout_three_sample_rollup_sync()`。

## 不可声称

- 任意真实项目 DWG / 公司图块库几何准确。
- 单一样本 verified 即代表全部工装 Scene Product 完成。
- fake rollup 4/4 即代表 meeting / reception 已在真实 AutoCAD 会话几何证明（仍须 `RCAD-10` / `RCAD-19`）。

## 子校验

```powershell
python -m unittest tests.core.test_project_sample_cad_rollup -v
python scripts/run_project_sample_cad_rollup.py --no-cad
```

## 真实 CAD 证据（2026-05-26）

`output/validation_runs/project-sample-cad-rollup-real/project_sample_cad_rollup_report.json`

| sample_id | status | created_handle_count | plan_count |
| --- | --- | ---: | ---: |
| `sample_blank_shell` | geometry_verified | 20 | 5 |
| `commercial_fitout_sample` | geometry_verified | 12 | 3 |

```powershell
python scripts/run_project_sample_cad_rollup.py --output-dir output/validation_runs/project-sample-cad-rollup-real
```
