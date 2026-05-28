# sample_intake_template

## 样本标识

| 字段 | 值 |
| --- | --- |
| `sample_id` | `REPLACE_WITH_YOUR_SAMPLE_ID` |
| `domain` | `office` |
| `deidentified` | `true` |
| `evidence_claim` | `non_cad_pipeline_only` |

复制本目录后，将文件夹重命名为你的 `sample_id`，并同步修改 `sample.manifest.json` 中的 `sample_id` 字段。

## 输入说明

| 文件 | 角色 |
| --- | --- |
| `input/shell.manual.json` | 手工 `SHELL_MODEL`（示例空壳） |
| `expected/expected_notes.md` | 非 CAD 预期说明 |

禁止提交 `.dwg` / `.dxf`。真实 CAD 仅在用户会话 + `CODEX_PREVIEW` 下可选执行。

## 预期输出

复制并填写后，至少应能跑通协议扫描；若接 workflow，预期包括 `CAD_PLAN`、`dry_run_report`、`verification_report`（non-CAD 时为 `unverified`）。详见 `expected/expected_notes.md`。

## 不可声称

- **不能** 因模板扫描 pass 而声称 **`geometry_verified`**。
- **不能** 将空模板当作真实项目或公司图纸能力证明。
- **不能** 在未经用户确认的情况下写回正式图层或保存 DWG。

## Intake 检查

见 `docs/runbooks/project-sample-intake.md`。
