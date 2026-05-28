# sample_test_fitout_20260528

## 样本标识

| 字段 | 值 |
| --- | --- |
| `sample_id` | `sample_test_fitout_20260528` |
| `domain` | `office` |
| `deidentified` | `true` |
| `evidence_claim` | `non_cad_with_optional_cad_preview` |

机器清单：`sample.manifest.json`。本样本为 **BETA-PROJECT-SAMPLE-08** 合成脱敏数据（矩形空壳 + 2 洞口），不含客户 DWG/PII。

## 输入说明

| 文件 | 角色 | Schema |
| --- | --- | --- |
| `input/shell.manual.json` | 手工 `SHELL_MODEL`（12m×8m 矩形 + 2 洞口） | `shell_model` |
| `fixtures/design_brief.json` | 项目 brief | `design_brief` |
| `fixtures/drawing_model.json` | 占位 drawing | `drawing_model` |
| `expected/expected_notes.md` | 预期说明 | — |

禁止提交 `.dwg` / `.dxf`。真实 CAD 仅在用户会话 + `CODEX_PREVIEW` 下执行，且不保存正式 DWG。

## 预期输出

| 入口 | 路径 |
| --- | --- |
| Workflow JSON | `examples/workflows/sample_test_fitout_20260528_project_loop.json` |
| 协议扫描 | `scripts/run_project_sample_protocol_scan.py` |
| Workflow CLI | `scripts/run_project_sample_workflow.py --sample-id sample_test_fitout_20260528` |
| CAD check | `scripts/run_project_sample_cad_check.py --sample-id sample_test_fitout_20260528 --require-cad-verified` |

证据目录：`output/validation_runs/sample-08-test-fitout-20260528/`。

## 不可声称

- **不能** 将本合成样本等同于任意真实客户项目或公司施工图能力。
- **不能** 在缺少 created-handle readback 时声称 **`geometry_verified`**。
- **不能** 写正式图层、保存 DWG 或覆盖用户原始图纸。
