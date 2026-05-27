# commercial_fitout_meeting_sample

## 样本标识

| 字段 | 值 |
| --- | --- |
| `sample_id` | `commercial_fitout_meeting_sample` |
| `domain` | `office` |
| `deidentified` | `true` |
| `evidence_claim` | `non_cad_pipeline_only` |

机器清单：`sample.manifest.json`。

## 输入说明

| 文件 | 角色 | Schema |
| --- | --- | --- |
| `input/shell.manual.json` | 脱敏会议室 `SHELL_MODEL` | `shell_model` |
| `fixtures/design_brief.json` | 工装 brief（`needs_confirmation: true`） | `design_brief` |
| `fixtures/drawing_model.json` | 占位 drawing（无实体） | `drawing_model` |
| `expected/expected_notes.md` | 人类可读预期 | — |

不得在本样本目录提交原始 `.dwg` / `.dxf`。真实 CAD smoke 通过 `project_sample_cad_rollup` 或 `run_commercial_fitout_cad_smoke.py`（仅 `CODEX_PREVIEW` + created handles readback）。

## Workflow（CFIT-09）

| 入口 | 路径 |
| --- | --- |
| Workflow JSON | `examples/workflows/commercial_fitout_meeting_sample_confirmation_loop.json` |
| CLI | `scripts/run_commercial_fitout_sample_confirmation.py`（`--workflow` 待后续包显式暴露时可用） |
| Core | `core/agents/commercial_fitout_sample_confirmation.py` + `fitout_sample_specs.py` |

## 预期输出

1. **确认前**：`confirmation_pending`，仅有 `design_proposal` 等上游产物，**无** `cad_plan` / `dry_run_report`。
2. **用户确认后**：`confirmed_cad_plan_bundle.json` + `commercial_fitout_meeting_sample_confirmation_bundle.json`。
3. `verification_report` 在 non-CAD 路径下为 `unverified`。

详见 `expected/expected_notes.md`。

## 不可声称

- **不能** 因本样本 non-CAD 通过而声称 **`geometry_verified`**。
- **不能** 将本样本扩大为完整工装 Scene Product 或公司图块库能力。
- **不能** 在用户确认前生成可执行 `CAD_PLAN` 或保存 DWG。
