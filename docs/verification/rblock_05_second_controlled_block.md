# RBLOCK-05：第二受控测试块 Metadata

最后更新：2026-05-27

本文是 **§4.2 P5 图块波次** 包 `RBLOCK-05-SECOND-CONTROLLED-BLOCK` 的边界说明。在 `RBLOCK-03`/`RBLOCK-04` 受控 block alpha 与矩阵 manifest 之上，登记 **第二块** 受控测试 fixture 的 library + sidecar metadata，为 **`V-PROOF-41-BLOCK-CAD-MATRIX`** 多块真实 CAD 做准备。

## 受控块对照

| 字段 | 主块（001） | 第二块（002） |
| --- | --- | --- |
| `block_id` | `controlled-test-block-001` | `controlled-test-block-002` |
| `block_name` | `CODEX_TEST_BLOCK_001` | `CODEX_TEST_BLOCK_002` |
| footprint | 900×450 mm | 600×300 mm |
| `validation.status` | `metadata_only` | `metadata_only` |

Manifest：`examples/capability_proof/second_controlled_block_manifest.json`（`manifest_id=second-controlled-block-01`）。

Sidecar：`libraries/blocks/controlled/CODEX_TEST_BLOCK_002.metadata.json`。

## 机器入口

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_rblock_05_second_controlled_block -v
& $py scripts\run_second_controlled_block_contract.py
```

契约：`core/block_engine/second_controlled_block_boundary.assert_second_controlled_block_contract()`

## 可声称

- `BLOCK_LIBRARY v0.2` 现含 **两块** 受控测试块 metadata，schema 校验通过。
- `object_spec_to_block_reference` 可按 `preferred_block_refs` 选中 `controlled-test-block-002`（metadata 层）。
- `insert_block_alpha` V-PROOF-41 后仅放行两个受控测试块：`controlled-test-block-001` / `CODEX_TEST_BLOCK_001` 与 `controlled-test-block-002` / `CODEX_TEST_BLOCK_002`。
- `V-PROOF-41` 代码轨可生成双受控块 CAD matrix；真实 CAD `geometry_verified` 仍必须来自 created handles 回读。

## 不得声称

- 不得因 library 登记 002 就声称第二块已真实 CAD `geometry_verified`。
- 不得把 metadata 可选中误解为任意项目块可写；`insert_block_alpha` 只允许 001/002 两个受控测试块。
- 不得扩大到公司块库或第三块以上未登记 fixture。

## 后续

| 包 | 说明 |
| --- | --- |
| `RBLOCK-06` | 属性块探针边界（**done**） |
| `RBLOCK-07` | 块矩阵 registry 行 writeback |
| `V-PROOF-41` | 第二/第三受控块真实 CAD |

## Acceptance

`RBLOCK-05` **done** 当：本文存在；`assert_second_controlled_block_contract` 通过；focused 单测 OK；next=`RBLOCK-06`。
