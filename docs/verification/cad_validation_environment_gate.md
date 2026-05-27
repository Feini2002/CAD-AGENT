# CAD-VAL-02：CAD Validation 环境门禁边界

最后更新：2026-05-27

> 机器入口：`scripts/run_cad_validation.py`  
> 相关字段：`geometry_gate`、`infrastructure_gate`、`infrastructure_debt`、`environment_optional`

本文定义 CAD validation 中几何门禁与环境门禁的边界。它的目的不是降低真实 CAD 几何要求，而是避免 `unit_tests`、截图依赖或 Pillow / pywin32 / win32gui 等环境步骤的非几何失败，被误读为 CAD 几何失败。

## 门禁分组

| 分组 | 代表步骤 | 说明 |
| --- | --- | --- |
| `geometry_gate` | `validate_sample_plan`、`dry_run_sample_plan`、`execute_sample_plan`、`inspect_readback`、`cad_capability_probe`、`block_alpha_readback` | 只回答 CAD_PLAN、执行、实体回读与 created-handle readback 是否满足几何证据要求 |
| `infrastructure_gate` | `python_import_pillow`、`python_import_pywin32`、`python_import_win32gui`、`self_check`、`unit_tests`、`render_preview_check`、`non_cad_benchmark`、`capture_screen`、`autocad_com_connect` | 只回答环境、依赖、截图、仓库回归和 AutoCAD 连接等基础设施状态 |

## `--environment-optional`

`--environment-optional` 会保留 `infrastructure_gate` 的失败信息，但顶层 `status` 按 `geometry_gate` 口径计算。

适用场景：

- 当前只想判断几何链路是否通过，不希望 `unit_tests` 的 Windows Temp ACL 偶发失败拖死几何结论。
- 当前只想保留 `render_preview_check` 或截图工具失败为环境债，不把它混成 CAD 几何失败。
- 当前需要在报告中看到 `infrastructure_debt=true`，并继续输出完整 evidence report。

## 可声称

- 可以声明 `geometry_gate=pass` 表示本轮几何门禁通过。
- 可以声明 `infrastructure_gate=fail` 表示存在非几何失败或环境债。
- 可以声明 `infrastructure_debt=true` 表示顶层 status 没有被环境失败拖死，但仍需后续修复。
- 可以声明 `--environment-optional` 是显式模式，不是默认吞错。

## 不得声称

- 不得声称 `--environment-optional` 会让失败步骤消失；失败仍必须保留在 `infrastructure_gate.failed_required_step_ids`。
- 不得声称 `infrastructure_gate=pass` 才能证明几何准确；几何准确以 `geometry_gate` 和真实 CAD created-handle readback 为准。
- 不得声称截图、Pillow、unit_tests 或 `render_preview_check` 通过即可证明 `geometry_verified`。
- 不得声称 `geometry_gate=pass` 覆盖任意 CAD_PLAN、正式图层或用户 DWG；它只覆盖本次 runner 的输入和证据。
- 不得在缺少真实 AutoCAD 输出和 created-handle readback 时，把 no-CAD 或 dry-run 结果声称为 `geometry_verified`。

## 复跑命令

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_cad_validation.py --no-cad --environment-optional --output-dir output\validation_runs\cad-val-02-environment-optional
```

## 子校验

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_cad_validation_geometry_gate tests.core.test_cad_validation_environment_gate_doc tests.core.test_cad_validation_runner
```
