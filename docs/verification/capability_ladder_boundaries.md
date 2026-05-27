# Capability Ladder Boundaries

最后更新：2026-05-27（V-PROOF-64）

本文固定表 C / Capability Ladder 的可声称边界。Ladder 与 showcase 只汇总已有真实 CAD 证据；不得用截图、dry-run、no-CAD benchmark 或 RCAD 烟囱完成度替代 created-handle readback。

## Ladder 对照

| Ladder | 可声称 | 不得声称 |
| --- | --- | --- |
| L0 | CAD_PLAN / runner / registry 入口存在 | 不代表会画准 |
| L1 | 单个 primitive / controlled block reference 有真实回读 | 不代表完整对象、完整图纸或任意 DWG |
| L2 | 单对象或受控块矩阵可作为 showcase 浏览 | 不代表项目级交付 |
| L3 | 多对象微场景片段有真实 CAD 几何证据 | 不代表整套施工图 |
| L4 | 脱敏项目切片有真实 CAD 证据与 showcase | 不代表跨项目泛化或 L5 |
| L5 | 预留给交付级图纸包 | 当前未证明 |

## V-PROOF-64 本轮新增

- `block.insert_block_alpha.matrix` 从 verified 提升为 showcase，证据来自 `RCAD-24-BLOCK-ALPHA-BETA` 的 8/8 real CAD `block_reference` readback。
- 展示入口：`docs/verification/capability_showcase/showcase/L2/block_insert_matrix/gallery_index.json`。
- 该 showcase 只覆盖受控 `CODEX_TEST_BLOCK_001` block alpha beta suite；`V-PROOF-41` 已另行补齐第二受控块真实 CAD readback，但仍不扩大到任意项目块库或属性块。

## V-PROOF-65 本轮新增

- `primitive.hatch`、`symbol.block_first.symbol_block_first_tier_01`、`symbol.block_first.controlled_block_wins`、`drawing_standard.beta.block_insert_plan_resolution` 从 verified 提升为 showcase。
- 展示入口：`showcase/L1/primitive_hatch_smoke/`、`showcase/L1/symbol_block_first/`、`showcase/L0/drawing_standard_block_insert/`。
- 这些 showcase 只覆盖受控 ANSI31 hatch、受控 block-first 路径和 drawing-standard beta block insert 子 case；不能扩大为任意 hatch、任意块库或完整制图标准能力。

## V-PROOF-66 本轮新增

- `primitive.arc/circle/dimension/line/polyline/rectangle/text` 和 `drawing_standard.beta.drawing_standard_beta_04` 从 verified 提升为 showcase。
- 展示入口：`showcase/L1/primitive_probe_matrix/`；drawing-standard suite 继续复用 `showcase/L0/drawing_standard_block_insert/`。
- primitive probe 只覆盖受控 `CODEX_PREVIEW` capability probe；`primitive.rectangle` 在该报告中代表矩形线框，不代表独立 AutoCAD rectangle 对象。drawing-standard suite 只覆盖 RCAD-23 真实 CAD 子集，不代表完整制图标准交付。

## 汇报边界

- 表 C 主指标只取 `cad_strength_headline_percent`。
- `showcase_readiness_percent` 是当前主瓶颈时，应同时汇报 coverage、strength index、L3+ 与 showcase。
- 任何新增 showcase 行必须已有真实 CAD evidence triplet，并在 `cad_capability_registry.json` 中保留 `evidence.report_path`。
