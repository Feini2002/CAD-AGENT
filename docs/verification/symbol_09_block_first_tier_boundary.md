# SYMBOL-09：Block-First Tier 机器入口与 Deferred 边界

最后更新：2026-05-27

本文是 **§4.2 P4 Core** 包 `SYMBOL-09-BLOCK-FIRST-TIER` 的边界说明。它在 `SYMBOL-08` 四级 fallback 之上，固定 **block-first** 层（`block` tier / `insert_block_alpha`）的机器入口、**deferred 到 glyph** 条件与登记表绑定，服务 **`V-PROOF-34-BLOCK-FIRST-ROW`** 与 **`RCAD-25-SYMBOL-BLOCK-FIRST`**。

## Block-First 语义

| 条件 | `block` tier | 结果 |
| --- | --- | --- |
| 受控块 `controlled-test-block-001` + `validation.status=cad_insertion_verified` | available | `selected_render_path=block`，`insert_block_alpha` CAD_PLAN |
| 块库仅 `metadata_only` / 未 verified | unavailable（structured） | 落到 `symbol_glyph` 等下级 tier，**不得** silent degradation |
| 无块库 / `block_preferred` 但块不可用 | unavailable | 显式走 glyph 或更低 tier，须 `silent_degradation=false` |

常量：`TIER_TO_CAD_INTENT["block"] == "insert_block_alpha"`；解析入口 `resolve_symbol_render_resolution(..., block_library=...)`。

## 机器入口

| 项 | 路径 |
| --- | --- |
| Manifest | `examples/capability_proof/symbol_block_first_tier_manifest.json`（`manifest_id=symbol-block-first-tier-01`，3 cases） |
| Runner | `scripts/run_block_first_tier_smoke.py` |
| 实现 | `core/symbol_engine/block_first_tier.py` |
| 契约 | `core/symbol_engine/block_first_boundary.assert_block_first_tier_boundary_contract()` |
| Registry | `symbol.block_first.*` 四行（suite + 3 cases） |

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_symbol_09_block_first_tier -v
& $py scripts\run_block_first_tier_smoke.py --output-root output\validation_runs\symbol-09-block-first-no-cad
```

## 可声称

- block-first smoke manifest 3/3 pass（controlled block 胜出 / metadata-only 落 glyph / 无库落 glyph）。
- 登记表四行与 manifest case 一一对应；smoke evidence writeback API 可绑定 `dry_run_valid_plan_only` 报告路径。
- `V-PROOF-34` 代码轨前置完成；真实 CAD 块插入仍须 `RCAD-25` 用户会话。

## 不得声称

- 不得因 block-first smoke 或 registry 行存在就声称受控块已在真实 AutoCAD `geometry_verified`。
- 不得把 `metadata_only` 块库当成 block tier 已通过。
- 不得跳过可用 block tier 而静默退化（沿用 `detect_silent_degradation`）。
- 本包不计入表 C 主指标。

## 后续

| 项 | 说明 |
| --- | --- |
| `V-PROOF-34` | 将 smoke 行升级为 `verified`（需 RCAD-25 几何证据） |
| `RCAD-25` | 真实 CAD block-first smoke |
| P4 下一波 | P3 `user_gate` 或 P5 图块波次占位 |

## Acceptance

`SYMBOL-09` **done** 当：本文存在；`assert_block_first_tier_boundary_contract()` 通过；focused 单测 OK；P4 父包见 `p4_core_wave_acceptance.md`（`CORE-P4-WAVE-PARENT-ROLLUP`）。
