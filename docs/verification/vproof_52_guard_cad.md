# V-PROOF-52：Guard 全链路真实 CAD strict

最后更新：2026-05-28

> 机器入口：`core/verification/guard_cad_registry.py`、`scripts/run_vproof_52_guard_cad_sync.py`
> RCAD 证据：`output/validation_runs/rcad-21-guard-full-20260527/guard_full_cad_report.json`

## 登记行（4）

| capability_id | 子报告 |
| --- | --- |
| `guard.cad.full_chain.strict` | 顶层 `guard_full_cad_report.json` + `strict_gate` |
| `guard.cad.write_guard` | write guard |
| `guard.cad.negative_cad` | negative CAD |
| `guard.cad.capability_probe` | capability probe + session_guard |

全部 `claim_level=smoke`；strict pass 为 guard/snapshot 审计，**不等于**任意 `CAD_PLAN` 几何 `geometry_verified`。

## 退出条件

- `status=pass`、`mode=real_cad`、`strict=true`
- `strict_gate.status=pass`
- 三段子报告 summary 字段满足 LCAD-14 边界

## 不得声称

- 不得把 strict pass 升为 `verified` / `showcase` 或抬高表 C 主指标。
- 不得把 fake/no-CAD strict 报告说成真实 CAD 已验证（须引用 RCAD-21 路径）。

## 复跑

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_guard_full_cad_runner.py --real-cad --strict --output-dir output\validation_runs\rcad-21-guard-full-20260527
& $py scripts\run_vproof_52_guard_cad_sync.py --report output\validation_runs\rcad-21-guard-full-20260527\guard_full_cad_report.json
```
