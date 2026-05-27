# RBLOCK-06：属性块 / Tag Readback 探针边界

最后更新：2026-05-27

本文是 **§4.2 P5 图块波次** 包 `RBLOCK-06-BLOCK-ATTRIBUTE-BOUNDARY` 的边界说明。它在 `RBLOCK-04` 块矩阵 attribute 维度与既有 **`BETA-CAD-BLOCK-02`** 之上，把属性/tag readback 探针收成 P5 可审计契约，服务 **`RCAD-05-BLOCK-ATTRIBUTE`** 与 registry 行 `block.insert_block_alpha.attributes`。

## 探针计划

| 项 | 值 |
| --- | --- |
| CAD_PLAN | `examples/plans/insert_block_alpha_attribute_probe.json` |
| 标记 | `object.attribute_readback_probe=true` |
| 期望 tag | `ROOM`、`DESK_ID` |
| registry | `block.insert_block_alpha.attributes` |

Manifest：`examples/capability_proof/block_attribute_probe_manifest.json`（`manifest_id=block-attribute-probe-01`）。

历史说明：`docs/verification/beta_cad_block_02_boundaries.md`。

## 行为不变量

| 计划 | 实体 attributes | 顶层 geometry_verified |
| --- | --- | --- |
| 无 probe（如 `insert_block_alpha_test.json`） | 任意 | 按几何规则；attribute `not_run` |
| 有 probe | 缺失 | **否**（`deferred` + `attribute_unverified`） |
| 有 probe | tag 匹配 | 几何 pass 时可 **是** |
| 有 probe 但 plan 未带 probe 却带 attributes | validate 拒绝 | — |

COM `insert_block_alpha` **仍拒绝** 带 attributes 的写入（除非 probe 计划仅用于 readback 契约）；本包固化 no-CAD / 模拟实体 smoke。

## 机器入口

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_rblock_06_block_attribute_boundary -v
& $py scripts\run_block_attribute_boundary_contract.py
```

契约：`core/block_engine/block_attribute_boundary.assert_block_attribute_boundary_contract()`

## 可声称

- 探针 plan 通过 validate；缺 tag → structured deferred，不误报 `geometry_verified`。
- `RBLOCK-04` attribute 维度 no-CAD 为 `dry_run_valid_plan_only`（矩阵 runner 1/1 pass）。
- 与 `RBLOCK-04` attribute 矩阵维度、`block.insert_block_alpha.attributes` registry 行可审计对齐。
- `BETA-CAD-BLOCK-02` 已纳入 P5 波次边界（本文 + manifest + 契约）。

## 不得声称

- 不得因 no-CAD smoke pass 就声称真实 AutoCAD 属性块已全面 `geometry_verified`。
- 不得把探针推广到公司块库、动态块或任意 DWG。
- 截图不能代替 attribute tag readback。

## 后续

| 包 | 说明 |
| --- | --- |
| `RBLOCK-07` | 块矩阵 registry 行 smoke writeback（**done**） |
| `RBLOCK-08` | P5 父包收口 |
| `RCAD-05` / `V-PROOF-40` | 真实 CAD attribute 补验 |

## Acceptance

`RBLOCK-06` **done** 当：本文存在；契约通过；focused 单测 OK；next=`RBLOCK-07`。
