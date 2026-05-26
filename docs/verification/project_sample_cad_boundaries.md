# LCAD-08：项目样本 CAD 闭环边界

最后更新：2026-05-26

> 机器入口：`examples/cad_regression/project_sample_cad_rollup.json`  
> 执行：`scripts/run_project_sample_cad_rollup.py`

## 注册样本

| sample_id | 工作流 | CAD 报告 |
| --- | --- | --- |
| `sample_blank_shell` | `sample_blank_shell_project_loop.json` | `project_sample_cad_check_report.json` |
| `commercial_fitout_sample` | `commercial_fitout_sample_confirmation_loop.json` | `commercial_fitout_cad_smoke_report.json` |

## 可声称（有证据时）

- 各样本在 `CODEX_PREVIEW` 上执行确认后的 `cad_plan_items`，并按 **created handles** 定向回读。
- Rollup 状态 `geometry_verified` 仅当 **全部** 注册样本均 verified。

## 不可声称

- 任意真实项目 DWG / 公司图块库几何准确。
- 单一样本 verified 即代表全部工装 Scene Product 完成。

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
