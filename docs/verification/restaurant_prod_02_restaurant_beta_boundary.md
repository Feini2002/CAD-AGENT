# REST-PROD-02：Restaurant Scene Beta 边界（P3 第二包）

最后更新：2026-05-27

本文是 **§4.2 P3 他场景产品化波次** 包 `REST-PROD-02-RESTAURANT-BETA-BOUNDARY` 的边界说明。它在 `REST-PROD-01` 与既有 **`BETA-SCENE-03`** 之上，把餐饮 **scene_beta** benchmark（object / entrance / seating / back_of_house / blank_shell / failure）收成 P3 可审计契约。

## 范围

| 项 | 路径 / 入口 |
| --- | --- |
| 前置 | `REST-PROD-01`（`assert_restaurant_alpha_boundary_contract`） |
| Beta benchmark | `examples/benchmarks/restaurant_scene_beta_benchmark.json`（`suite_id=restaurant-scene-beta-benchmark`，8 cases） |
| Runner | `core.agents.restaurant_scene_beta.run_restaurant_scene_beta_benchmark()` |
| Preferences | `agents/restaurant/preferences.json` → `scene_beta.tier=beta` |
| Manifest | `examples/capability_proof/restaurant_prod_beta_manifest.json`（`manifest_id=restaurant-prod-beta-01`） |
| Registry | 8 行 `benchmark.restaurant_scene_beta_benchmark.*` |
| 契约 | `core.agents.restaurant_beta_boundary.assert_restaurant_beta_boundary_contract()` |

## 机器入口

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_rest_prod_02_restaurant_beta_boundary -v
& $py scripts\run_restaurant_beta_boundary_contract.py --run-benchmark
& $py scripts\run_restaurant_scene_beta_benchmark.py --output-root output\validation_runs\rest-prod-02-beta-no-cad
```

## 可声称

- 餐饮 scene_beta preferences 通过 `validate_scene_beta_restaurant_preferences`；suite 含六类 case tier。
- no-CAD benchmark **8/8** pass；证据汇总 7×`benchmark_pass_non_cad` + 1×`blocked_expected_non_cad`；证据态为 `dry_run_valid_plan_only`（非 geometry_verified）。
- `cad_capability_registry` 已登记 8 行 restaurant scene beta case；`BETA-SCENE-03` 代码轨前置已可审计。

## 不得声称

- 不得因 beta benchmark pass 就声称餐饮入口、堂食、后场或 blank-shell 已在真实 CAD `geometry_verified`。
- 不得把 registry smoke / deferred 行说成 verified / showcase 或抬高表 C 主指标。
- 不得把餐饮 beta benchmark 扩大为完整餐饮规范设计、消防疏散、后厨工艺或公司块库能力。
- 不得跳过 `CAD_PLAN` validate / dry-run / created handles 回读，把 no-CAD benchmark 当成真实几何证明。

## 后续

| 包 | 说明 |
| --- | --- |
| `REST-PROD-03` | 餐饮 P3 父包可按 `OFFICE-PROD-03` 模式收口 |
| `BETA-SCENE-03` | 已有 restaurant beta benchmark；本包把它产品化为 P3 边界 |
| `V-PROOF-24` | 后续若登记餐饮对象 rows，仍需明确 claim_level 与证据路径 |

## Acceptance

`REST-PROD-02` **done** 当：本文存在；manifest 存在；契约通过；focused 单测 OK；restaurant beta no-CAD benchmark 复跑通过；任务清单 §4 next 推进到后续 REST 包。
