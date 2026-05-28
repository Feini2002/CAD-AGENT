# V-PROOF-23：component plan（object_detail_spec）进 registry

最后更新：2026-05-28

> 机器入口：`core/verification/object_detail_registry.py`、`scripts/run_vproof_23_object_detail_sync.py`
> Manifest：`examples/capability_proof/object_detail_component_manifest.json`

本文登记 `object_detail_spec` 组件级 CAD_PLAN（table / desk / chair / bed / sofa），与 OBJ-DETAIL / `core/object_engine/detail_plan.py` 对齐。仅 **smoke / no-CAD** 证据。

## 登记口径

| capability_id 模式 | object_type | claim_level | evidence_state |
| --- | --- | --- | --- |
| `object.component_detail.suite` | 汇总 | `smoke` | `benchmark_pass_non_cad` |
| `object.<type>.component_detail` | table, desk, chair, bed, sofa | `smoke` | `benchmark_pass_non_cad` |

## 可声称

- 五类家具的组件 plan 可经 dry-run 校验并写入 registry smoke 行。
- 与 `tests/core/test_object_engine.py` 中 component role 断言一致。
- 为后续真实 CAD 组件落图预留 `cad_case` 绑定，但不自动升级 `verified`。

## 不得声称

- 不得把 `benchmark_pass_non_cad` 或 dry-run valid 计为 `geometry_verified` 或抬高表 C。
- 不得把 smoke 行写成 `verified` / `showcase`。
- 不得声称 registry 登记等于 office/residential 真实家具符号已画准。

## 复跑

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_vproof_23_object_detail_sync.py
& $py -m unittest tests.core.test_vproof_23_object_detail_rows -v
```
