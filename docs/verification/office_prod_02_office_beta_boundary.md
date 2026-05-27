# OFFICE-PROD-02：Office Scene Beta 边界（P3 第二包）

最后更新：2026-05-27

本文是 **§4.2 P3 他场景产品化波次** 包 `OFFICE-PROD-02-OFFICE-BETA-BOUNDARY` 的边界说明。它在 `OFFICE-PROD-01` 与既有 **`BETA-SCENE-01`** 之上，把办公 **scene_beta** benchmark（object / micro_scene / blank_shell / failure）收成 P3 可审计契约，服务 **`V-PROOF-24-OFFICE-OBJECT-ROWS`**。

## 范围

| 项 | 路径 / 入口 |
| --- | --- |
| 前置 | `OFFICE-PROD-01`（`assert_office_alpha_boundary_contract`） |
| Beta benchmark | `examples/benchmarks/office_scene_beta_benchmark.json`（`suite_id=office-scene-beta-benchmark`，9 cases） |
| Runner | `core/agents/office_scene_beta.run_office_scene_beta_benchmark()` |
| Preferences | `agents/office/preferences.json` → `scene_beta.tier=beta` |
| Manifest | `examples/capability_proof/office_prod_beta_manifest.json`（`manifest_id=office-prod-beta-01`） |
| Registry | 9 行 `benchmark.office_scene_beta_benchmark.*` |
| 契约 | `core/agents/office_beta_boundary.assert_office_beta_boundary_contract()` |

## 机器入口

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_office_prod_02_office_beta_boundary -v
& $py scripts\run_office_beta_boundary_contract.py
& $py scripts\run_office_scene_beta_benchmark.py --output-root output\validation_runs\office-prod-02-beta-no-cad
```

## 可声称

- 办公 scene_beta preferences 通过 `validate_scene_beta_office_preferences`；suite 含四 tier（object/micro_scene/blank_shell/failure）。
- no-CAD benchmark **9/9** pass；证据汇总 7×`benchmark_pass_non_cad` + 2×`blocked_expected_non_cad`（预期失败样本）；证据态为 `dry_run_valid_plan_only`（非 geometry_verified）。
- `cad_capability_registry` 已登记 9 行 office scene beta case；`V-PROOF-24` 代码轨前置完成。

## 不得声称

- 不得因 beta benchmark pass 就声称办公 blank-shell 或微场景已在真实 CAD `geometry_verified`。
- 不得把 registry smoke 行说成 verified / showcase 或抬高表 C 主指标。
- 不得与工装 `commercial_fitout` 项目级 `geometry_verified` 混用。

## 后续

| 包 | 说明 |
| --- | --- |
| `OFFICE-PROD-03`+ | 办公 registry writeback / 父包收口（待进队） |
| `REST-PROD-01` | 餐饮场景进波 |
| `V-PROOF-24` | office 对象 verified 升级（需 RCAD） |

## Acceptance

`OFFICE-PROD-02` **done** 当：本文存在；契约通过；focused 单测 OK；next=`OFFICE-PROD-03` 或 `REST-PROD-01`。
