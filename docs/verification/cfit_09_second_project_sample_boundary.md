# CFIT-09：第二组工装脱敏项目样本边界

最后更新：2026-05-27

## CFIT-09-SECOND-PROJECT-SAMPLE

`CFIT-09-SECOND-PROJECT-SAMPLE` 在 `projects/commercial_fitout_meeting_sample/` 落地第二组脱敏工装项目样本，并登记到 `examples/cad_regression/project_sample_cad_rollup.json`，为 `RCAD-10-PROJECT-SECOND-SAMPLE` 提供机器可读路径。

| 项 | 值 |
| --- | --- |
| `sample_id` | `commercial_fitout_meeting_sample` |
| 子场景 | `meeting_room`（见 `agents/commercial_fitout/subscenes.json`） |
| Workflow | `examples/workflows/commercial_fitout_meeting_sample_confirmation_loop.json` |
| 规格注册 | `core/agents/fitout_sample_specs.py` |

## 退出条件（本包）

- `scan_projects_root(projects/)` 包含新样本且 `status=pass`。
- `run_fitout_sample_pre_confirmation` / 完整 confirmation loop 在 fake/no-CAD 下可跑通。
- `project_sample_cad_rollup` manifest 含第三行样本；fake driver rollup 为 3× `geometry_verified`（单测）。

## 不得声称

- 不得因样本目录存在就声称 `RCAD-10` 已在真实 AutoCAD 会话通过。
- 不得将 meeting 样本 non-CAD 通过说成开放办公样本或完整工装产品已完成。
- 第二样本只证明**路径定稿 + 管道可复用**；真实 CAD 几何仍须 created-handle readback 证据。
