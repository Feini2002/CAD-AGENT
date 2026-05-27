# RBLOCK-04：Block Insert 矩阵 Manifest

最后更新：2026-05-27

本文是 **§4.2 P5 图块波次** 包 `RBLOCK-04-BLOCK-MATRIX-MANIFEST` 的边界说明。它在 `RBLOCK-03` 受控 block alpha 边界之上，把 **anchor / rotation / scale / attribute** 四维矩阵收成机器可读 manifest，并与 `cad_capability_registry` 四行 `block.insert_block_alpha.*` 绑定，服务 **`V-PROOF-40-BLOCK-MATRIX-PLAN`**。

## 矩阵维度

| 维度 | registry `capability_id` | 机器用例 |
| --- | --- | --- |
| `anchor` | `block.insert_block_alpha.anchor` | beta `beta_anchor_*` ×3 |
| `rotation` | `block.insert_block_alpha.rotation` | beta `beta_rotation_45/90` |
| `scale` | `block.insert_block_alpha.scale` | beta `beta_scale_half/125` |
| `attribute` | `block.insert_block_alpha.attributes` | `insert_block_alpha_attribute_probe.json` |

另含组合 smoke：`beta_combined_transform`（rotation+scale，无独立 registry 行）。

Manifest：`examples/capability_proof/block_insert_matrix_manifest.json`（`manifest_id=block-insert-matrix-01`）。

## 机器入口

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_rblock_04_block_matrix_manifest -v
& $py scripts\run_block_insert_matrix_manifest.py --output-root output\validation_runs\rblock-04-block-matrix-no-cad
```

契约：`core/block_engine/block_matrix_manifest.assert_block_matrix_manifest_contract()`

## 可声称

- 四维矩阵与 beta suite / attribute probe plan / registry 四行一一可审计。
- no-CAD 矩阵 runner 全维度 pass（`dry_run_valid_plan_only`）。
- `V-PROOF-40` 代码轨前置完成；registry 行升级 verified 走 `RBLOCK-07` / 真实 CAD。

## 不得声称

- 不得因矩阵 manifest pass 就声称四维度均已真实 CAD `geometry_verified`（registry 行可有历史 verified，本包不新增）。
- 不得扩大到非受控块或公司块库。
- 不得把组合 smoke 当成第四/registry 额外 verified 维度。

## 后续

| 包 | 说明 |
| --- | --- |
| `RBLOCK-05` | 第二受控测试块 metadata（**done**） |
| `RBLOCK-07` | 矩阵行 smoke writeback 绑定 |
| `V-PROOF-41` | 第二/第三块真实 CAD |

## Acceptance

`RBLOCK-04` **done** 当：本文存在；契约通过；focused 单测 OK；next=`RBLOCK-05`。
