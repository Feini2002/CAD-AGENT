# CAD Autonomous Validation Report

- status: `fail`
- root: `C:\Users\User\Desktop\CAD-AGENT`
- output_dir: `C:\Users\User\Desktop\CAD-AGENT\output\validation_runs\cad-validation-debt-closure-20260605\real_cad_validation_escalated`
- include_cad: `True`

## Steps

| step | status | category |
| --- | --- | --- |
| `python_import_pillow` | `pass` | `-` |
| `python_import_pywin32` | `pass` | `-` |
| `python_import_win32gui` | `pass` | `-` |
| `self_check` | `pass` | `-` |
| `unit_tests` | `fail` | `repo_regression` |
| `validate_sample_plan` | `pass` | `-` |
| `dry_run_sample_plan` | `pass` | `-` |
| `render_preview_check` | `pass` | `-` |
| `non_cad_benchmark` | `pass` | `-` |
| `block_alpha_validate_plan` | `pass` | `-` |
| `block_alpha_dry_run` | `pass` | `-` |
| `autocad_com_connect` | `pass` | `-` |
| `execute_sample_plan` | `pass` | `-` |
| `capture_screen` | `pass` | `-` |
| `inspect_readback` | `fail` | `readback_failed` |
| `cad_capability_probe` | `fail` | `cad_capability_failed` |
| `block_alpha_execute` | `pass` | `-` |
| `block_alpha_capture_screen` | `pass` | `-` |
| `block_alpha_readback` | `pass` | `-` |

## Next Actions

- 仓库测试或自检失败。Codex 应先做最小复现和最小修复，再重新运行本脚本。
- 实体回读失败。Codex 应检查 `inspect_dwg.py`、created handles 和 AutoCAD COM 回读逻辑。
- CAD COM 能力探针失败。Codex 应检查 driver primitive write、handle readback、实体标准化和安全层约束。
