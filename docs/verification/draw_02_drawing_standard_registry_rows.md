# DRAW-02：Drawing Standard Registry 行绑定

最后更新：2026-05-27

本文是 **§4.2 P4 Core** 包 `DRAW-02-DRAWING-STANDARD-REGISTRY-ROWS` 的边界说明。它在 `DRAW-01` 边界契约之上，把 `drawing_standard_beta_suite.json` 的 **6 个 case + 1 个 suite 父行** 绑定进 `cad_capability_registry.json`，并提供 **smoke 级证据回写 API**（`apply_smoke_registry_evidence_writeback`），服务 **`V-PROOF-44`** 与后续 **`RCAD-23`**。

## 登记行（7 行）

| capability_id | 绑定 |
| --- | --- |
| `drawing_standard.beta.drawing_standard_beta_04` | suite 汇总 `drawing_standard_beta_summary.json` |
| `drawing_standard.beta.role_furniture_preview_layer` | case `role_furniture_preview_layer` |
| `drawing_standard.beta.role_clearance_hatch_style` | case `role_clearance_hatch_style` |
| `drawing_standard.beta.layer_role_shell_semantic_only` | case `layer_role_shell_semantic_only` |
| `drawing_standard.beta.block_insert_plan_resolution` | case `block_insert_plan_resolution` |
| `drawing_standard.beta.primitive_text_style` | case `primitive_text_style` |
| `drawing_standard.beta.primitive_dimension_style` | case `primitive_dimension_style` |

默认 `claim_level=smoke`、`ladder_level=L0`；证据态为 `dry_run_valid_plan_only`（经 smoke writeback 写入 `evidence.report_path`）。

## 机器入口

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_draw_02_drawing_standard_registry_rows -v
& $py scripts\run_drawing_standard_beta_suite.py --output-root output\validation_runs\draw-02-drawing-standard-registry-no-cad
```

契约：`core/drawing_standard/drawing_standard_registry.assert_drawing_standard_registry_contract()`

## 可声称

- 每个 beta case 在登记表有唯一 `capability_id`，`source_refs.source_key` 与 `cad_case.output_path` 可机器审计。
- no-CAD beta suite 6/6 pass 后，可通过 `sync_drawing_standard_registry_from_suite()` 把 smoke 证据路径写入对应行。
- `V-PROOF-44` 代码轨前置（登记行 + smoke writeback）已完成；真实 CAD 子集仍走 `RCAD-23`。

## 不得声称

- 不得因 smoke writeback 或 `dry_run_valid_plan_only` 就把行标为 `verified` / `showcase` 或计入表 C 几何证明。
- 不得把 beta suite pass 说成真实 AutoCAD 已按正式图层写入。
- `apply_smoke_registry_evidence_writeback` **不能**替代 `apply_writeback`（后者仅接受 `geometry_verified` 报告升级 `verified`）。

## 后续

| 包 / RCAD | 说明 |
| --- | --- |
| `V-PROOF-44` | 能力证明轨可把 smoke 行升级为 verified（需 RCAD-23 几何证据） |
| `RCAD-23` | 用户会话跑 `run_drawing_standard_beta_suite.py` 真实 CAD |
| `SYMBOL-08` | **done** — 四级 fallback 边界（见 `symbol_08_glyph_fallback_boundary.md`） |
| `SYMBOL-09` | P4 下一包（block-first tier） |
