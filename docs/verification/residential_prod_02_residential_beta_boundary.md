# RESIDENTIAL-PROD-02：Residential Scene Beta 边界（P3 第二包）

最后更新：2026-05-28

本文是 **§4.2 P3 他场景产品化波次** 包 `RESIDENTIAL-PROD-02-RESIDENTIAL-BETA-BOUNDARY` 的边界说明。它在 `RESIDENTIAL-PROD-01` 与既有 **`BETA-SCENE-02`** 之上，把住宅 **scene_beta** benchmark（object / bedroom / dining / storage / blank_shell / failure）收成 P3 可审计契约。

## 范围

| 项 | 路径 / 入口 |
| --- | --- |
| 前置 | `RESIDENTIAL-PROD-01`（`assert_residential_alpha_boundary_contract`） |
| Beta benchmark | `examples/benchmarks/residential_scene_beta_benchmark.json`（`suite_id=residential-scene-beta-benchmark`，8 cases） |
| Runner | `core.agents.residential_scene_beta.run_residential_scene_beta_benchmark()` |
| Preferences | `agents/residential/preferences.json` → `scene_beta.tier=beta` |
| Manifest | `examples/capability_proof/residential_prod_beta_manifest.json`（`manifest_id=residential-prod-beta-01`） |
| Registry | 8 行 `benchmark.residential_scene_beta_benchmark.*` |
| 契约 | `core.agents.residential_beta_boundary.assert_residential_beta_boundary_contract()` |

## 机器入口

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_res_prod_02_residential_beta_boundary -v
& $py scripts\run_residential_beta_boundary_contract.py --run-benchmark
& $py scripts\run_residential_scene_beta_benchmark.py --output-root output\validation_runs\res-prod-02-beta-no-cad
```

## 可声称

- 住宅 scene_beta preferences 通过 `validate_scene_beta_residential_preferences`；suite 含六类 case tier。
- no-CAD benchmark **8/8** pass；证据汇总 7×`benchmark_pass_non_cad` + 1×`blocked_expected_non_cad`；证据态为 `dry_run_valid_plan_only`（非 geometry_verified）。
- `cad_capability_registry` 已登记 8 行 residential scene beta case；`BETA-SCENE-02` 代码轨前置已可审计。

## 不得声称

- 不得因 beta benchmark pass 就声称卧室、餐厅、收纳或 blank-shell 已在真实 CAD `geometry_verified`。
- 不得把 registry smoke / deferred 行说成 verified / showcase 或抬高表 C 主指标。
- 不得把住宅 beta benchmark 扩大为完整家装规范设计、消防疏散或公司块库能力。
- 不得跳过 `CAD_PLAN` validate / dry-run / created handles 回读，把 no-CAD benchmark 当成真实几何证明。

## 后续

| 包 | 说明 |
| --- | --- |
| `RESIDENTIAL-PROD-03` | 住宅 P3 父包可按 `OFFICE-PROD-03` 模式收口 |
| `BETA-SCENE-02` | 已有 residential beta benchmark；本包把它产品化为 P3 边界 |
| `SCENE-PROD-06` | 多场景回归门禁已含 residential beta |

## Acceptance

`RESIDENTIAL-PROD-02` **done** 当：本文存在；manifest 存在；契约通过；focused 单测 OK；residential beta no-CAD benchmark 复跑通过；任务清单 §4 next 推进到 `RESIDENTIAL-PROD-03` 或余量包。
