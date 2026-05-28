# V-PROOF-24：office_alpha 对象 case registry（no-CAD smoke）

最后更新：2026-05-28

> 机器入口：`core/verification/office_object_registry.py`、`scripts/run_vproof_24_office_object_sync.py`
> Manifest：`examples/capability_proof/office_alpha_object_manifest.json`
> Benchmark：`examples/benchmarks/office_alpha_benchmark.json`（6 个 `object_spec` case）

本轮只做 **no-CAD benchmark + registry smoke**；纠正误绑 `readback_geometry_verified` 的 office 对象行。真实 CAD 段留待用户开 CAD 后走 RCAD / 补验。

## 登记口径

| capability_id | case_id | claim_level | evidence_state |
| --- | --- | --- | --- |
| `benchmark.office_alpha_benchmark.object_spec_suite` | 汇总 | `smoke` | `benchmark_pass_non_cad` |
| `benchmark.office_alpha_benchmark.<case_id>` | 6× object_spec | `smoke` | `benchmark_pass_non_cad` |

对象 case：`office_desk_default_spec`、`office_chair_default_spec`、`office_cabinet_default_spec`、`computer_desk_default_spec`、`storage_cabinet_front_clearance`、`file_cabinet_default_spec`。

## 可声称

- office_alpha 六个对象 case 在 registry 有独立 smoke 行，且 `benchmark_case_id` 与 suite 一致。
- no-CAD 子集 6/6 pass 后可复跑 sync 写回证据路径。
- 与 `OFFICE-PROD-01`~`03` 边界文档一致；composition / failure case 不在本包范围。

## 不得声称

- 不得把本包 smoke 写成办公场景真实 CAD 几何已证。
- 不得用历史 `object_cad_smoke` 回写路径冒充 office benchmark no-CAD 证据。
- 不得在未开 CAD 时声称 `geometry_verified`。

## 复跑

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_vproof_24_office_object_sync.py
& $py -m unittest tests.core.test_vproof_24_office_object_rows -v
```

## 可选 CAD 段（用户开 CAD 后）

- 对单对象 case 跑真实 `draw_object` + created handles 回读，再经 `capability_registry_writeback` 升级；须单独 RCAD 包，不在 V-PROOF-24 默认范围。
