# CFIT-10：前台接待脱敏项目样本边界

最后更新：2026-05-27

## CFIT-10-RECEPTION-PROJECT-SAMPLE

`CFIT-10-RECEPTION-PROJECT-SAMPLE` 在 `projects/commercial_fitout_reception_sample/` 落地第三组工装脱敏样本（`reception` 子场景），并登记 `project_sample_cad_rollup.json` 第四行工装样本，为 `RCAD-19-FITOUT-RECEPTION` 提供路径。

| 项 | 值 |
| --- | --- |
| `sample_id` | `commercial_fitout_reception_sample` |
| 子场景 | `reception` |
| Workflow | `examples/workflows/commercial_fitout_reception_sample_confirmation_loop.json` |

与 `CFIT-09`（会议室）及 `commercial_fitout_sample`（开放办公）共同覆盖 `primary_subscenes` 三子场景各一组脱敏样本。

## 不得声称

- 不得因样本目录存在就声称 `RCAD-19` 已在真实 AutoCAD 会话通过。
- 不得将前台样本 non-CAD 通过说成三子场景均已真实 CAD 几何证明。
