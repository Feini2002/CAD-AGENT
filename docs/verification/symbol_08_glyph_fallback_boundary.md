# SYMBOL-08：Symbol Glyph 四级 Fallback 边界

最后更新：2026-05-27

本文是 **§4.2 P4 Core** 包 `SYMBOL-08-GLYPH-FALLBACK-BOUNDARY` 的可审计边界。它把 `core/symbol_engine/fallback_policy.py` 的四级可执行渲染层级与 `deferred` 结构化出口固定为契约，服务 **`V-PROOF-35-FALLBACK-TIER-ROWS`** 与 **D-SYMBOL-07**（无静默退化），**不**在本包内新增真实 CAD `geometry_verified`。

## 四级 Fallback（优先级从高到低）

| 层级 | tier | `fallback_policy.mode`（示例） | CAD intent | 说明 |
| --- | --- | --- | --- | --- |
| 1 | `block` | `block_preferred` | `insert_block_alpha` | 受控块 `cad_insertion_verified` 时优先 |
| 2 | `symbol_glyph` | `symbol_readable` / `visual_review_required` | `draw_symbol_glyph` | 符号可读 + grammar 通过 |
| 3 | `component_preview` | `fallback_component_preview` | `draw_object`（detail plans） | 立面/组件预览 |
| 4 | `bbox_placeholder` | `fallback_bbox_placeholder` + `bbox_fallback_declared` | `draw_object`（bbox） | 显式声明的占位框 |
| — | `deferred` | `deferred_unsupported_symbol` | — | 无更高层可用时的结构化 defer |

机器常量：`FALLBACK_RENDER_TIERS`、`FALLBACK_MODE_TO_TIER`、`TIER_TO_CAD_INTENT`、`detect_silent_degradation()`。

## 关联产物

| 项 | 路径 |
| --- | --- |
| 策略实现 | `core/symbol_engine/fallback_policy.py` |
| 契约 | `core/symbol_engine/symbol_fallback_boundary.assert_symbol_glyph_fallback_boundary_contract()` |
| 单测 | `tests/core/test_symbol_fallback_policy.py` |
| Benchmark | `examples/benchmarks/symbol_fallback_policy_benchmark.json`（`suite_id=symbol-fallback-policy-01`，3 cases） |
| Registry | `benchmark.symbol_fallback_policy_01.*` 三行（non-CAD benchmark） |

## 机器入口

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_symbol_08_glyph_fallback_boundary tests.core.test_symbol_fallback_policy -v
```

## 可声称

- 四级 tier 顺序、`mode→tier` 映射与 benchmark 三 case（desk glyph / elevation component / counter deferred）可通过契约复验。
- `resolve_symbol_render_resolution` 在 benchmark case 上 `silent_degradation=false`，且 `detect_silent_degradation` 无错误。
- 每层默认证据态为 `dry_run_valid_plan_only`（`deferred` 为 `deferred_cad_readback_required`），不等于几何已证。

## 不得声称

- 不得因 fallback 解析或 benchmark pass 就声称 symbol/block 已在真实 AutoCAD `geometry_verified`。
- 不得跳过可用 `symbol_glyph` 而静默落到 `bbox_placeholder`（`detect_silent_degradation` 必须可审计）。
- 不得把本包计入表 C 主指标；`V-PROOF-35` 各 tier 的 registry 行已登记为 `smoke` / `deferred`，仍不等于真实 CAD 几何证明。

## 后续映射

| 后续项 | 说明 |
| --- | --- |
| `V-PROOF-35` | **done** — 四级 fallback 各 tier 已登记 `cad_capability_registry`；4 smoke + 1 deferred |
| `SYMBOL-09` | **done** — block-first 入口（见 `symbol_09_block_first_tier_boundary.md`） |
| `D-SYMBOL-07` | 无静默退化门禁（本包提供 detect API 边界） |

## Acceptance 判定

`SYMBOL-08` 可标为 **done**，当且仅当：

1. 本文存在且通过文档/契约测试。
2. `assert_symbol_glyph_fallback_boundary_contract()` 通过。
3. `test_symbol_fallback_policy` + `test_symbol_08_glyph_fallback_boundary` focused tests OK。
4. 任务清单 §4.2 将 `SYMBOL-08` 标为 done，代码轨 next 转入 `SYMBOL-09`。
