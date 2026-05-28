# RESIDENTIAL-PROD-01：Residential Alpha 边界（P3 他场景进波）

最后更新：2026-05-28

本文是 **§4.2 P3 他场景产品化波次** 的 `RESIDENTIAL-PROD-01-RESIDENTIAL-ALPHA-BOUNDARY` 边界说明。它沿用 `OFFICE-PROD-01` / `REST-PROD-01` 的收口模式，把住宅场景在 `scene-alpha-benchmark` 中的 alpha case 固定成可审计契约，并衔接已有 **`BETA-SCENE-02`** 住宅 beta benchmark。

## 范围

| 项 | 路径 / 入口 |
| --- | --- |
| 场景 Agent | `agents/residential/`（`agent.json`、`preferences.json`、`rules.md`） |
| Alpha benchmark | `examples/benchmarks/scene_alpha_benchmark.json`（`suite_id=scene-alpha-benchmark`，住宅 case=`scene_alpha_residential_blank_shell`） |
| Manifest | `examples/capability_proof/residential_prod_alpha_manifest.json`（`manifest_id=residential-prod-alpha-01`） |
| 契约 | `core.agents.residential_alpha_boundary.assert_residential_alpha_boundary_contract()` |

## 机器入口

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_res_prod_01_residential_alpha_boundary -v
& $py scripts\run_residential_alpha_boundary_contract.py
& $py scripts\run_benchmark_suite.py examples\benchmarks\scene_alpha_benchmark.json --output-root output\validation_runs\res-prod-01-benchmark-no-cad
```

## 可声称

- 住宅场景 preferences 通过 `validate_scene_alpha_preferences`，并仍属于 Scene Alpha 三场景之一。
- `scene_alpha_residential_blank_shell` 可复跑 no-CAD benchmark，选中 `along_wall` 动线，输出 `benchmark_pass_non_cad` / `dry_run_valid_plan_only` 级别证据。
- `RESIDENTIAL-PROD-01` 已把 residential alpha 边界接入 P3 他场景产品化队列；它复用 Core，不实现新的 CAD 执行层。

## 不得声称

- 不得因 benchmark pass 就声称住宅真实 CAD 布局已 `geometry_verified`。
- 不得把 `agents/residential` scaffold、preferences 或 `BETA-SCENE-02` 说成完整住宅 Scene Product 已交付。
- 不得从住宅 alpha case 扩大到规范审核、公司块库或正式图层写入。
- 不得跳过 `CAD_PLAN` validate / dry-run / created handles 回读，把 no-CAD benchmark 当成真实几何证明。

## 后续

| 包 | 说明 |
| --- | --- |
| `RESIDENTIAL-PROD-02` | 住宅 beta 边界可按 `OFFICE-PROD-02` 模式收口 |
| `BETA-SCENE-02` | 已有住宅 beta benchmark；本包只把 alpha 入口产品化 |
| `SCENE-PROD-06` | 多场景回归门禁已含 residential beta；本包补齐 P3 alpha 契约 |

## Acceptance

`RESIDENTIAL-PROD-01` **done** 当：本文存在；manifest 存在；`assert_residential_alpha_boundary_contract()` 通过；focused 单测 OK；benchmark no-CAD 复跑通过；任务清单 §4 next 推进到后续住宅 P3 包或其它 §4.2 余量包。
