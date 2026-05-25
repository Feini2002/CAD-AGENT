# CAD Deferred Verification Template

用于 CAD 环境恢复后，一次性补验证真实落图、截图和实体回读。

## 基本信息

| 项 | 内容 |
| --- | --- |
| verification_id | V-CAD-XXX |
| plan_path |  |
| source_workflow |  |
| expected_layer | CODEX_PREVIEW |
| expected_objects |  |
| tolerance_mm | 1.0 |

## 执行前非 CAD 证据

```powershell
$py = 'C:\Users\123235\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe'
& $py scripts\validate_plan.py <plan_path>
& $py scripts\dry_run_plan.py <plan_path>
& $py scripts\inspect_dwg.py --plan <plan_path> --format json --no-cad
```

## 真实 CAD 补验命令

```powershell
$py = 'C:\Users\123235\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe'
& $py -c "from core.cad_io.autocad_com import AutoCADComDriver; d=AutoCADComDriver(connect_existing_only=True); print('COM OK:', d.doc.Name)"
& $py scripts\execute_plan.py <plan_path>
& $py scripts\inspect_dwg.py --connect-cad --plan <plan_path> --format json
& $py scripts\render_preview.py --capture-screen --output output\previews\<verification_id>.png
```

## 通过标准

- 只写入 `CODEX_PREVIEW`，不保存当前 DWG，不修改正式图层。
- 回读实体包含本次新增对象，并能被 created handles 或 before/after diff 隔离。
- bbox、基点、图层、文字、标注与 `CAD_PLAN` / dry-run 预期一致。
- 截图文件存在，可作为视觉辅助证据；截图不替代实体回读。
- `VERIFICATION_REPORT.status` 只有在 readback scope 明确且检查全通过时才可升级为 `geometry_verified`。

## 结果记录

| 项 | 结果 |
| --- | --- |
| validate_plan |  |
| dry_run_plan |  |
| execute_plan |  |
| inspect_dwg --connect-cad |  |
| screenshot_path |  |
| verification_report_status |  |
| residual_risk |  |

