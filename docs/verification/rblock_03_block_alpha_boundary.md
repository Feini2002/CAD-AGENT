# RBLOCK-03：受控 Block Alpha 边界（P5 图块波次首包）

最后更新：2026-05-27

本文是 **§4.2 P5 图块波次** 首包 `RBLOCK-03-BLOCK-ALPHA-BOUNDARY` 的可审计边界。它把既有 `R-BLOCK-CAD-01`~`05` 与 `BETA-CAD-BLOCK-01` 产物收成 P5 契约入口，服务 **`V-PROOF-40-BLOCK-MATRIX-PLAN`** 与后续 **`RBLOCK-04`**，**不**在本包内新增真实 CAD `geometry_verified`。

## 范围

| 项 | 路径 / 入口 |
| --- | --- |
| 受控块 | `controlled-test-block-001` / `CODEX_TEST_BLOCK_001` |
| 块库 | `libraries/blocks/block_library.example.json` |
| Beta suite | `examples/plans/block_alpha_beta_suite.json`（`suite_id=block-alpha-beta-01`，8 cases） |
| 示例 CAD_PLAN | `examples/plans/insert_block_alpha_test.json` |
| Runner | `scripts/run_block_alpha_beta_suite.py`、`scripts/run_block_alpha_validation.py` |
| 契约 | `core/block_engine/block_alpha_boundary.assert_block_alpha_boundary_contract()` |
| 历史验收 | `docs/verification/beta_cad_block_acceptance.md` |

## 策略不变量

- 真实 CAD 插入**仅**允许受控测试块 `controlled-test-block-001`，图层 **仅** `CODEX_PREVIEW`。
- `block-alpha-beta-01` 覆盖多锚点、旋转、统一缩放；no-CAD 为 `dry_run_valid_plan_only`。
- `metadata_only` / `symbol_fallback` 块不得冒充 `cad_insertion_verified` block tier（见 `SYMBOL-09`）。

## 机器入口

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_rblock_03_block_alpha_boundary -v
& $py scripts\run_block_alpha_beta_suite.py --output-root output\validation_runs\rblock-03-block-alpha-no-cad
```

## 可声称

- 受控块 metadata、8-case beta suite、schema 与 runner 可通过契约审计；beta suite 8/8 no-CAD pass。
- P5 图块波次已进队；块矩阵 manifest / 第二受控块仍走 `RBLOCK-04`+。

## 不得声称

- 不得因 RBLOCK-03 或 beta suite pass 就声称公司块库或任意 DWG 块插入已 `geometry_verified`。
- 不得把 `R-BLOCK-CAD-05` 历史证据自动扩大到本包登记或表 C。
- 截图不能代替 created-handle readback。

## 后续

| 包 | 说明 |
| --- | --- |
| `RBLOCK-04` | 块矩阵 rotation × scale × attribute manifest（`V-PROOF-40`） |
| `RBLOCK-05`~`07` | 第二/第三受控块、属性边界、registry 行 |
| `RBLOCK-08` | P5 父包收口 |
| `V-PROOF-41` / RCAD | 真实 CAD 块矩阵补验 |

## Acceptance

`RBLOCK-03` **done** 当：本文存在；契约通过；focused 单测 OK；任务清单 next=`RBLOCK-04`。
