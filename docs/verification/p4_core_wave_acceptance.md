# P4 Core 波次父包收口

最后更新：2026-05-27

本文是 **§4.2 P4 Core 波次**（`DRAW-01` / `DRAW-02` / `SYMBOL-08` / `SYMBOL-09`）的父包 acceptance / rollup。它只收口代码轨与机器入口对齐，**不**在本父包内新增真实 CAD `geometry_verified` 结论。

## 收口结论

| 子包 | 状态 | 产物 | 结论 |
| --- | --- | --- | --- |
| `DRAW-01` | done | `drawing_standard_boundary.py`、`drawing-standard-beta` | 绘图标准 profile 边界 + 6-case no-CAD |
| `DRAW-02` | done | `drawing_standard_registry.py`、+7 registry 行 | smoke writeback API |
| `SYMBOL-08` | done | `symbol_fallback_boundary.py`、`symbol-fallback-policy-01` | 四级 fallback；`silent_degradation` 契约 |
| `SYMBOL-09` | done | `block_first_tier.py`、block-first manifest | 3-case tier smoke + registry +4 |
| `CORE-P4` | done | 本文 + `p4_core_wave.py` + 父包单测 | P4 Core 波次代码轨正式收口 |

## 机器入口（P4 全链路）

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_p4_core_wave_parent_rollup -v
& $py scripts\run_drawing_standard_beta_suite.py --output-root output\validation_runs\p4-draw-beta-no-cad
& $py scripts\run_block_first_tier_smoke.py --output-root output\validation_runs\p4-block-first-no-cad
```

契约断言：`core/p4_core_wave.assert_p4_core_wave_contract()`

## 可声称

- P4 四子包 boundary MD、drawing standard beta、block-first manifest、fallback benchmark 均可 `assert_p4_core_wave_contract()` 审计。
- no-CAD：drawing-standard-beta **6/6**、block-first tier **3/3**、fallback 无静默退化契约复验 pass。
- `V-PROOF-44` / `V-PROOF-34` / `V-PROOF-35` 代码轨前置已完成；真实 CAD 仍走 RCAD / 能力证明轨。

## 不得声称

- 不得因 P4 父包收口或 no-CAD pass 就声称 drawing standard 或 block-first 已在真实 AutoCAD `geometry_verified`。
- 不得把 smoke registry 行或 `dry_run_valid_plan_only` 说成表 C 主指标已上升。
- `RCAD-23` / `RCAD-25` 真实 CAD 补验须单独在用户会话完成。

## 后续映射

| 后续项 | 说明 |
| --- | --- |
| `V-PROOF-44` | drawing standard registry verified 升级 |
| `V-PROOF-34` | block-first tier verified |
| `V-PROOF-35` | fallback tier 登记 |
| §4.2 P5 | `RBLOCK-03`~`08`（**done**） |
| §4.2 P3 | `OFFICE-PROD-03` 已收口；next=`REST-PROD-01` |

## Acceptance 判定

`CORE-P4-WAVE-PARENT-ROLLUP` **done** 当：四子包均为 done；本文存在；`assert_p4_core_wave_contract()` 通过；focused 单测 OK。
