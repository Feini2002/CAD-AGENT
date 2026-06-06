# CAD Autonomous Validation Report

- status: `fail`
- root: `C:\Users\User\Desktop\CAD-AGENT`
- output_dir: `C:\Users\User\Desktop\CAD-AGENT\output\validation_runs\cad-validation-debt-closure-20260605\real_cad_validation`
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
| `autocad_com_connect` | `fail` | `cad_connection_failed` |
| `execute_sample_plan` | `not_run` | `-` |
| `capture_screen` | `not_run` | `-` |
| `inspect_readback` | `not_run` | `-` |
| `cad_capability_probe` | `not_run` | `-` |
| `block_alpha_execute` | `not_run` | `-` |
| `block_alpha_capture_screen` | `not_run` | `-` |
| `block_alpha_readback` | `not_run` | `-` |

## Next Actions

- CAD validation pass requires block_alpha.geometry_verified when block_alpha_readback ran
- 几何门禁已通过，但环境/截图/单测等基础设施步骤仍有失败；请单独修复基础设施后再做完整 baseline。
- 打开 AutoCAD 和一张测试 DWG，确认没有授权弹窗阻塞，再重新运行本脚本。
- 仓库测试或自检失败。Codex 应先做最小复现和最小修复，再重新运行本脚本。
