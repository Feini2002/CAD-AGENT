# CFIT-11：工装三样本 product boundary / rollup 口径同步

最后更新：2026-05-27

## CFIT-11-THREE-SAMPLE-BOUNDARY-SYNC

`CFIT-11` 在 `CFIT-09` / `CFIT-10` 三子场景脱敏样本路径齐备后，把 **Scene Product Alpha 边界** 与 **LCAD-08 project_sample_cad_rollup** 登记口径收成单一机器可读契约。

| 子场景 | `sample_id` | 项目目录 | Rollup 行 |
| --- | --- | --- | --- |
| `open_office` | `commercial_fitout_sample` | `projects/commercial_fitout_sample` | 是 |
| `meeting_room` | `commercial_fitout_meeting_sample` | `projects/commercial_fitout_meeting_sample` | 是 |
| `reception` | `commercial_fitout_reception_sample` | `projects/commercial_fitout_reception_sample` | 是 |

机器入口：

- `agents/commercial_fitout/capabilities/product_alpha_boundary.json` → `deidentified_project_samples[]`
- `core/agents/fitout_sample_specs.py` → `subscene_id` / `project_rel` / `workflow_rel`
- `examples/cad_regression/project_sample_cad_rollup.json` → 四行样本（含 `sample_blank_shell`）
- `core/agents/commercial_fitout_product_boundary.py` → `assert_fitout_three_sample_rollup_sync()`

## 退出条件（本包）

- `assert_product_boundary_contract()` 通过（含三样本 rollup 同步断言）。
- `fitout_sample_specs` 三键与 `primary_subscenes` 一一对应。
- fake driver `run_project_sample_cad_rollup` 仍为 4/4 `geometry_verified`（单测）。

## 不得声称

- 不得因口径同步就声称 `RCAD-10` / `RCAD-19` 已在真实 AutoCAD 会话通过。
- 不得将 fake rollup 4/4 说成三子场景均已真实 CAD 几何证明。
- `CFIT-11` 只固定**声明边界与登记一致性**；真实几何仍按样本逐项 RCAD 补验。
