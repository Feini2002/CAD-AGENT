# V-PROOF-51：负向真实 CAD 守卫（无 handles）

最后更新：2026-05-28

> 机器入口：`core/verification/negative_plan_registry.py`、`scripts/run_vproof_51_negative_cad_sync.py`
> 登记行：`negative.cad_plan.real_cad_guard`
> RCAD 证据：`output/validation_runs/rcad-20-negative-cad-20260527-escalated/negative_cad_runner_report.json`

## 退出条件

真实 AutoCAD 会话下 `run_negative_cad_runner.py --real-cad` 报告满足：

- `status=pass`、`mode=real_cad`
- `evidence_state=negative_guard_verified`
- `created_handles=[]`
- `safety.saved_dwg=false`、不删除、不改正式层
- `preview_layer_entity_delta=0`、`modelspace_entity_delta=0`

## 可声称

- registry 行 `negative.cad_plan.real_cad_guard` 已绑定 RCAD-20 真实 CAD 报告路径。
- 与 `LCAD-10.3`、`RCAD-20` 烟囱一致。

## 不得声称

- 不得把本包写成 `geometry_verified` 或把 `claim_level` 升为 `verified` / `showcase`。
- 不得用本包抬高表 C 主指标（guard-only smoke 行）。

## 复跑

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_negative_cad_runner.py --real-cad --output-dir output\validation_runs\rcad-20-negative-cad-20260527-escalated
& $py scripts\run_vproof_51_negative_cad_sync.py --report output\validation_runs\rcad-20-negative-cad-20260527-escalated\negative_cad_runner_report.json
```
