# OFFICE-PROD-01：Office Alpha 边界（P3 进波首包）

最后更新：2026-05-27

本文是 **§4.2 P3 他场景产品化波次** 首包 `OFFICE-PROD-01-OFFICE-ALPHA-BOUNDARY` 的边界说明。它在既有 `R-OFFICE-MICRO` / `office_alpha_benchmark` 之上，把办公场景 **alpha** 层收成 P3 可审计契约，服务 **`V-PROOF-24-OFFICE-OBJECT-ROWS`** 与后续 `REST-PROD` 波次。

## 范围

| 项 | 路径 / 入口 |
| --- | --- |
| 场景 Agent | `agents/office/`（`agent.json`、`preferences.json`、`rules.md`） |
| Alpha benchmark | `examples/benchmarks/office_alpha_benchmark.json`（`suite_id=office-alpha-benchmark`，18 cases） |
| 历史证据 | `docs/verification/office_alpha_benchmark_evidence.md` |
| Manifest | `examples/capability_proof/office_prod_alpha_manifest.json`（`manifest_id=office-prod-alpha-01`） |
| 契约 | `core/agents/office_alpha_boundary.assert_office_alpha_boundary_contract()` |

## 机器入口

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_office_prod_01_office_alpha_boundary -v
& $py scripts\run_office_alpha_boundary_contract.py
& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\validation_runs\office-prod-01-benchmark-no-cad
```

## 可声称

- 办公场景 preferences 通过 `validate_scene_alpha_preferences`；与 scene alpha 三场景之一对齐。
- `office-alpha-benchmark` 18 case 结构可审计；no-CAD benchmark **18/18** 可复跑（`benchmark_pass_non_cad` / `blocked_expected_non_cad`）；证据态为 `dry_run_valid_plan_only` 级别（非 geometry_verified）。
- P3 办公波次已**进波**；`REST-PROD` / 第三场景仍 scheduled。

## 不得声称

- 不得因 benchmark pass 就声称办公真实 CAD 布局已 `geometry_verified`。
- 不得把 `agents/office` scaffold 说成 Scene Product 已交付或表 C 主指标已上升。
- 不得扩大到工装 `commercial_fitout` 项目样本或公司块库。

## 后续

| 包 | 说明 |
| --- | --- |
| `OFFICE-PROD-02`+ | 办公 beta benchmark / registry 行（待进队） |
| `REST-PROD` | 餐饮场景产品化 |
| `V-PROOF-24` | office 对象 case → registry |

## Acceptance

`OFFICE-PROD-01` **done** 当：本文存在；契约通过；focused 单测 OK；next=`OFFICE-PROD-02` 或 `REST-PROD` 首包。
