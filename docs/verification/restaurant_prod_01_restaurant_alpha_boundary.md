# REST-PROD-01：Restaurant Alpha 边界（P3 他场景进波）

最后更新：2026-05-27

本文是 **§4.2 P3 他场景产品化波次** 的 `REST-PROD-01-RESTAURANT-ALPHA-BOUNDARY` 边界说明。它沿用 `OFFICE-PROD-01` 的收口模式，把餐饮场景在 `scene-alpha-benchmark` 中的 alpha case 固定成可审计契约，并衔接已有 **`BETA-SCENE-03`** 餐饮 beta benchmark。

## 范围

| 项 | 路径 / 入口 |
| --- | --- |
| 场景 Agent | `agents/restaurant/`（`agent.json`、`preferences.json`、`rules.md`） |
| Alpha benchmark | `examples/benchmarks/scene_alpha_benchmark.json`（`suite_id=scene-alpha-benchmark`，餐饮 case=`scene_alpha_restaurant_blank_shell`） |
| Manifest | `examples/capability_proof/restaurant_prod_alpha_manifest.json`（`manifest_id=restaurant-prod-alpha-01`） |
| 契约 | `core.agents.restaurant_alpha_boundary.assert_restaurant_alpha_boundary_contract()` |

## 机器入口

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_rest_prod_01_restaurant_alpha_boundary -v
& $py scripts\run_restaurant_alpha_boundary_contract.py
& $py scripts\run_benchmark_suite.py examples\benchmarks\scene_alpha_benchmark.json --output-root output\validation_runs\rest-prod-01-benchmark-no-cad
```

## 可声称

- 餐饮场景 preferences 通过 `validate_scene_alpha_preferences`，并仍属于 Scene Alpha 三场景之一。
- `scene_alpha_restaurant_blank_shell` 可复跑 no-CAD benchmark，选中 `l_spine` 动线，输出 `benchmark_pass_non_cad` / `dry_run_valid_plan_only` 级别证据。
- `REST-PROD-01` 已把 restaurant alpha 边界接入 P3 他场景产品化队列；它复用 Core，不实现新的 CAD 执行层。

## 不得声称

- 不得因 benchmark pass 就声称餐饮真实 CAD 布局已 `geometry_verified`。
- 不得把 `agents/restaurant` scaffold、preferences 或 `BETA-SCENE-03` 说成完整餐饮 Scene Product 已交付。
- 不得从餐饮 alpha case 扩大到后厨、消防、规范审核、公司块库或正式图层写入。
- 不得跳过 `CAD_PLAN` validate / dry-run / created handles 回读，把 no-CAD benchmark 当成真实几何证明。

## 后续

| 包 | 说明 |
| --- | --- |
| `REST-PROD-02` | 餐饮 beta 边界或 beta rollup 可按 `OFFICE-PROD-02` 模式收口 |
| `BETA-SCENE-03` | 已有餐饮 beta benchmark；本包只把 alpha 入口产品化 |
| `V-PROOF-24` | 后续若登记餐饮对象 rows，仍需明确 claim_level 与证据路径 |

## Acceptance

`REST-PROD-01` **done** 当：本文存在；manifest 存在；`assert_restaurant_alpha_boundary_contract()` 通过；focused 单测 OK；benchmark no-CAD 复跑通过；任务清单 §4 next 推进到后续 REST 包。
