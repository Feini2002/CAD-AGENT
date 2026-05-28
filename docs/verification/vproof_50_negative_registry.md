# V-PROOF-50：负向 plan 清单进 registry

最后更新：2026-05-28

> 机器入口：`core/verification/negative_plan_registry.py`、`scripts/run_vproof_50_negative_registry_sync.py`
> 负向 manifest：`examples/plans/negative/negative_plan_manifest.json`

本文登记 LCAD-10 负向 `failure_category` 与 guard suite 的 registry 行。只提供 **smoke / guard-only** 证据，不新增 `geometry_verified`。

## 登记口径

| capability_id 模式 | failure_category | claim_level | evidence_state |
| --- | --- | --- | --- |
| `negative.cad_plan.<category>` | 8 类 fixture 拒收 | `smoke` | `invalid_configuration` |
| `negative.cad_plan.suite` | 负向 runner 汇总 | `smoke` | `negative_guard_verified` |

## 可声称

- 每个 `failure_category` 在 `cad_capability_registry.json` 有独立 smoke 行，并绑定 manifest `source_key`。
- fake/no-CAD 同步后，suite 与各类别行带有可复跑报告路径。
- 与 `LCAD-10`、`RCAD-20` 链路一致；真实 CAD 负向安全仍以 `RCAD-20` 报告为准。

## 不得声称

- 不得把 `invalid_configuration` 或 `negative_guard_verified` 计为几何证明或抬高表 C 主指标。
- 不得把 smoke 行写成 `verified` / `showcase`。
- 不得声称 registry 登记等于任意正向 `CAD_PLAN` 已能画准。

## 复跑

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_vproof_50_negative_registry_sync.py
& $py -m unittest tests.core.test_vproof_50_negative_registry tests.core.test_negative_cad_plans
```
