# P5 图块波次父包收口

最后更新：2026-05-27

本文是 **§4.2 P5 图块波次**（`RBLOCK-03` … `RBLOCK-07`）的父包 acceptance / rollup。它只收口代码轨与机器入口对齐，**不**在本父包内新增真实 CAD `geometry_verified` 结论。

## 收口结论

| 子包 | 状态 | 产物 | 结论 |
| --- | --- | --- | --- |
| `RBLOCK-03` | done | `block_alpha_boundary.py`、`block-alpha-beta-01` | 受控 block alpha 边界 + 8-case no-CAD |
| `RBLOCK-04` | done | `block_insert_matrix_manifest.json`（`manifest_id=block-insert-matrix-01`）、四维矩阵 runner | anchor/rotation/scale/attribute manifest |
| `RBLOCK-05` | done | `controlled-test-block-002` metadata | 第二受控块；`insert_block_alpha` 仍仅 001 |
| `RBLOCK-06` | done | `block_attribute_probe` 边界、deferred 不误报 | `BETA-CAD-BLOCK-02` 纳入 P5 |
| `RBLOCK-07` | done | 5 行 registry 绑定 + matrix smoke writeback | `block.insert_block_alpha.matrix` smoke 父行 |
| `RBLOCK-08` | done | 本文 + `block_p5_wave.py` + 父包单测 | P5 图块波次代码轨收口 |

## 机器入口（P5 全链路）

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_rblock_08_p5_wave_parent_rollup -v
& $py scripts\run_block_alpha_beta_suite.py --output-root output\validation_runs\rblock-08-p5-beta-no-cad
& $py scripts\run_block_insert_matrix_manifest.py --output-root output\validation_runs\rblock-08-p5-matrix-no-cad
& $py scripts\run_block_matrix_registry_sync.py --output output\validation_runs\rblock-08-p5-registry-no-cad
```

契约断言：`core/block_engine/block_p5_wave.assert_block_p5_wave_contract()`

## 可声称

- P5 六子包 boundary MD、三份 manifest、registry 矩阵 5 行绑定均可 `assert_block_p5_wave_contract()` 审计。
- no-CAD：block-alpha-beta **8/8**、insert-matrix **8/8**、attribute deferred smoke、registry binding API 齐备；证据态为 `dry_run_valid_plan_only`（非 geometry_verified）。
- `V-PROOF-40` / `V-PROOF-41` 代码轨前置（边界 + manifest + registry）已完成；真实 CAD 仍走 RCAD / 能力证明轨。

## 不得声称

- 不得因 P5 父包收口或 no-CAD pass 就声称第二受控块或属性块已在真实 AutoCAD `geometry_verified`。
- 不得把 verified 四维行的历史 readback 证据说成仅由本父包新产生。
- 不得把本父包计入表 C 主指标；表 C 仍看 `run_capability_coverage.py` 与 showcase/verified 登记。
- `V-PROOF-41` 多块真实 CAD、`RCAD-05` attribute 补验须单独在用户会话完成。

## 后续映射

| 后续项 | 说明 |
| --- | --- |
| `V-PROOF-40` | 块矩阵 plan 能力证明（registry 行已绑定） |
| `V-PROOF-41` | 第二/第三受控块真实 CAD |
| `RCAD-04`~`05` | block alpha / attribute 烟囱包 |
| §4.2 P3 | `OFFICE-PROD` 等仍为 **user_gate** |

## Acceptance 判定

`RBLOCK-08` / P5 图块波次可标为 **done**，当且仅当：

1. `RBLOCK-03` … `RBLOCK-07` 均为 done。
2. 本文与五份子包 boundary MD 均存在并通过文档/契约测试。
3. `assert_block_p5_wave_contract()` 通过。
4. 任务清单 §4.2 P5 波次收口；代码轨 next 转入 PlanMD 下一波次或 P3 user_gate。
