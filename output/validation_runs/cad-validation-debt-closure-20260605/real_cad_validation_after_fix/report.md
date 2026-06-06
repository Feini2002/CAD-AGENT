# CAD Autonomous Validation Report

- status: `pass`
- root: `C:\Users\User\Desktop\CAD-AGENT`
- output_dir: `C:\Users\User\Desktop\CAD-AGENT\output\validation_runs\cad-validation-debt-closure-20260605\real_cad_validation_after_fix`
- include_cad: `True`
- geometry_gate_mode: `true`
- geometry_gate.status: `pass`
- infrastructure_gate.status: `fail`
- legacy_status: `fail`

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
| `inspect_readback` | `pass` | `-` |
| `cad_capability_probe` | `pass` | `-` |
| `block_alpha_execute` | `pass` | `-` |
| `block_alpha_capture_screen` | `pass` | `-` |
| `block_alpha_readback` | `pass` | `-` |

## Next Actions

- 几何门禁已通过，但环境/截图/单测等基础设施步骤仍有失败；请单独修复基础设施后再做完整 baseline。
- 仓库测试或自检失败。Codex 应先做最小复现和最小修复，再重新运行本脚本。
