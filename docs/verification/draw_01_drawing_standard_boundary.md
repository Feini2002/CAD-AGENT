# DRAW-01：Drawing Standard 边界（P4 Core 首包）

最后更新：2026-05-27

本文是 **§4.2 P4 Core 波次** 首包 `DRAW-01-DRAWING-STANDARD-BOUNDARY` 的可审计边界。它把既有 `BETA-CAD-BLOCK-04` 产物收成 P4 契约入口，服务 **`V-PROOF-44-DRAWING-STANDARD-ROWS`** 与 **`RCAD-23-DRAWING-STANDARD-BETA`**，**不**在本包内新增真实 CAD `geometry_verified` 结论。

## 范围

| 项 | 路径 / 入口 |
| --- | --- |
| Profile | `libraries/drawing_standards/codex_preview_beta.json` |
| Layer preset | `libraries/layer_presets/codex_preview_beta.json` |
| Schema | `core/schemas/drawing_standard_profile.schema.json` |
| 解析 | `core/drawing_standard/drawing_standard_profile.py` |
| Beta suite | `examples/plans/drawing_standard_beta_suite.json`（`suite_id=drawing-standard-beta-04`，6 cases） |
| Runner | `scripts/run_drawing_standard_beta_suite.py` |
| 契约 | `core/drawing_standard/drawing_standard_boundary.assert_drawing_standard_boundary_contract()` |
| 历史边界 | `docs/verification/beta_cad_block_04_boundaries.md` |

## 策略不变量（必须保持）

| 模式 | `layer_role=furniture` | CAD 写入层 | 语义层 |
| --- | --- | --- | --- |
| `preview_only` | 是 | `CODEX_PREVIEW` | `A-FURN`（dry-run / 文档） |

`cad_execution_mode=preview_only` 时，任何 `layer_role` / `object_role` 的真实 COM 写入层必须为 `CODEX_PREVIEW`，不得静默落到 `A-FURN` 等正式层。

## 机器入口

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_draw_01_drawing_standard_boundary -v
& $py scripts\run_drawing_standard_beta_suite.py --output-root output\validation_runs\draw-01-drawing-standard-no-cad
```

## 可声称

- `codex_preview_beta` profile 与 layer preset、6-case beta suite、schema registry 登记可通过 `assert_drawing_standard_boundary_contract()` 审计。
- no-CAD beta suite 6/6 pass 可证明 role→layer/style 解析与 dry-run 合法（`evidence_state=dry_run_valid_plan_only`）。
- P4 Core 波次已从 DRAW 边界包进队；后续 registry 行与真实 CAD 走能力证明轨 / RCAD。

## 不得声称

- 不得因 DRAW-01 或 no-CAD beta suite pass 就声称正式项目图层 / 公司制图标准已在真实 DWG 落地。
- 不得把 `semantic_layer=A-FURN` 写成真实 AutoCAD 已写入正式层（preview 策略强制 `CODEX_PREVIEW`）。
- 不得把本包计入表 C 主指标；`V-PROOF-44` registry 回写与 `RCAD-23` 真实 CAD 须单独完成。
- Beta suite pass **≠** `geometry_verified`；截图仅作视觉辅助。

## 后续映射

| 后续项 | 说明 |
| --- | --- |
| `DRAW-02` | **done** — 7 行登记 + smoke writeback（见 `draw_02_drawing_standard_registry_rows.md`） |
| `V-PROOF-44` | 能力证明轨登记 drawing_standard 子集 |
| `RCAD-23` | 用户会话真实 CAD beta 子集 |
| `SYMBOL-08`~`09` | P4 符号 / block-first tier 包（与 `V-PROOF-34` / `RCAD-25` 衔接） |

## Acceptance 判定

`DRAW-01` 可标为 **done**，当且仅当：

1. 本文与 `beta_cad_block_04_boundaries.md` 均存在。
2. `assert_drawing_standard_boundary_contract()` 通过。
3. focused 单测与 no-CAD beta suite 6/6 pass。
4. 任务清单 §4.2 将 `DRAW-01` 标为 done（`DRAW-02` 已收口，代码轨 next=`SYMBOL-08`）。
