# sample_blank_shell

## 样本标识

| 字段 | 值 |
| --- | --- |
| `sample_id` | `sample_blank_shell` |
| `domain` | `generic` |
| `deidentified` | `true` |
| `evidence_claim` | `non_cad_pipeline_only` |

机器清单：`sample.manifest.json`。

## 输入说明

| 文件 | 角色 | Schema |
| --- | --- | --- |
| `input/shell.manual.json` | `SHELL_MODEL` 手工空壳 | `shell_model` |
| `fixtures/design_brief.json` | 项目 brief | `design_brief` |
| `fixtures/drawing_model.json` | 占位 drawing（无实体） | `drawing_model` |
| `expected/project_model.expected.json` | `PROJECT_MODEL` 金样 | `project_model` |

不得在本样本目录提交原始 `.dwg` / `.dxf`；如需真实 CAD 验证，使用用户本地 DWG + `CODEX_PREVIEW`，且不覆盖原文件。

## Workflow（BETA-PROJECT-SAMPLE-03）

| 入口 | 路径 |
| --- | --- |
| Workflow JSON | `examples/workflows/sample_blank_shell_project_loop.json` |
| CLI | `scripts/run_project_sample_workflow.py` |
| 默认输出 | `output/test_artifacts/project_samples/beta_project_sample_03/` |

## 预期输出

经 blank-shell workflow 应能生成（可写入 `output/`，本仓库不强制提交二进制）：

- `PROJECT_MODEL`、`CIRCULATION_MODEL`、`FUNCTION_ZONE` 候选
- `LAYOUT_PROPOSAL`、`DESIGN_PROPOSAL`
- `CAD_PLAN` + `dry_run_report`
- `verification_report`（non-CAD 时为 `unverified`）

人类可读预期见 `expected/expected_notes.md`。

## 不可声称

- **不能** 因本样本 non-CAD 通过而声称 **`geometry_verified`**。
- **不能** 将本样本扩大为任意真实项目 / 公司图纸能力。
- **不能** 在未经用户确认的情况下把样本结果写回正式图层或保存 DWG。
