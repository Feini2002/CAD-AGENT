# RBLOCK-07：Block Insert 矩阵 Registry 行绑定

最后更新：2026-05-27

本文是 **§4.2 P5 图块波次** 包 `RBLOCK-07-BLOCK-MATRIX-REGISTRY-ROWS` 的边界说明。它在 `RBLOCK-04`~`06` 之上，把 `block-insert-matrix-01` 四维矩阵与 `cad_capability_registry` 绑定，并提供 **矩阵 smoke 回写 API**（`apply_block_matrix_registry_binding` / `sync_block_matrix_registry_from_manifest`），服务 **`V-PROOF-40`**。

## 登记行（5 行）

| capability_id | 绑定 |
| --- | --- |
| `block.insert_block_alpha.matrix` | suite 汇总 `block_insert_matrix_summary.json`（**smoke**） |
| `block.insert_block_alpha.anchor` | 维度 `anchor`（verified + manifest `source_ref`） |
| `block.insert_block_alpha.rotation` | 维度 `rotation` |
| `block.insert_block_alpha.scale` | 维度 `scale` |
| `block.insert_block_alpha.attributes` | 维度 `attribute`（manifest `source_key=attribute`） |

Manifest：`examples/capability_proof/block_insert_matrix_manifest.json`。

## 机器入口

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_rblock_07_block_matrix_registry_rows -v
& $py scripts\run_block_matrix_registry_sync.py --output output\validation_runs\rblock-07-block-matrix-registry-no-cad
```

契约：`core/block_engine/block_matrix_registry.assert_block_matrix_registry_contract()`

## 可声称

- 矩阵四维 + suite 父行与 manifest / runner 输出路径可机器审计。
- no-CAD 矩阵 8/8 pass 后，suite 行可 `dry_run_valid_plan_only` smoke writeback；verified 行仅追加 manifest `source_ref` 与 notes，**不覆盖**既有 `readback_geometry_verified` 证据。
- `V-PROOF-40` 代码轨 registry 绑定前置完成。

## 不得声称

- 不得因矩阵 smoke binding 就把 verified 行重新说成仅 dry-run 已几何验证。
- 不得用 `apply_block_matrix_registry_binding` 替代真实 CAD `apply_writeback` 升级 verified。
- 不得把 suite smoke pass 计入表 C 主指标几何证明。

## 后续

| 包 | 说明 |
| --- | --- |
| `RBLOCK-08` | P5 父包收口（**done**） |
| `V-PROOF-40` / RCAD | 真实 CAD 矩阵补验 |

## Acceptance

`RBLOCK-07` **done** 当：本文存在；契约通过；focused 单测 OK；next=`RBLOCK-08`。
