# REST-PROD-03：Restaurant P3 波次父包收口

最后更新：2026-05-27

本文是 **§4.2 P3 他场景产品化** 中餐饮波次的父包 acceptance / rollup，收口 `REST-PROD-01` 与 `REST-PROD-02`。本包只对齐代码轨、文档边界和 no-CAD benchmark 入口，**不**新增真实 CAD `geometry_verified` 结论。

## 收口结论

| 子包 | 状态 | 产物 | 结论 |
| --- | --- | --- | --- |
| `REST-PROD-01` | done | `restaurant_alpha_boundary.py`、`restaurant-prod-alpha-01`、scene alpha restaurant case | 餐饮 alpha 边界可审计 |
| `REST-PROD-02` | done | `restaurant_beta_boundary.py`、`restaurant-prod-beta-01`、8-case scene beta benchmark | 餐饮 beta 边界可审计 |
| `REST-PROD-03` | done | 本文 + `restaurant_p3_wave.py` + 父包单测 | 餐饮 P3 代码轨正式收口 |

## 机器入口（P3 Restaurant 全链路）

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_rest_prod_03_p3_wave_rollup -v
& $py scripts\run_restaurant_p3_wave_rollup.py --run-benchmarks --output output\validation_runs\rest-prod-03-p3-rollup-no-cad
```

契约断言：`core.agents.restaurant_p3_wave.assert_restaurant_p3_wave_contract()`

## 可声称

- `REST-PROD-01` / `REST-PROD-02` 的 manifest、boundary doc、benchmark suite 和 registry beta rows 均可被父包契约统一审计。
- no-CAD：scene alpha restaurant case 为 `benchmark_pass_non_cad`；restaurant scene beta benchmark **8/8**（7 pass + 1 blocked_expected）。
- `BETA-SCENE-03` 的餐饮代码轨前置已收口；后续能力证明和真实 CAD 仍走 §3 / §5。

## 不得声称

- 不得因 `REST-PROD-03` 或 no-CAD benchmark pass 声称餐饮场景已真实 CAD `geometry_verified`。
- 不得把 `benchmark_pass_non_cad`、`blocked_expected_non_cad`、manifest 或 registry smoke/deferred 行当作表 C 主指标上涨。
- 不得把 `agents/restaurant` scaffold 写成完整餐饮产品 Agent；本包只收口 P3 餐饮波次边界。
- 不得扩大到消防疏散、后厨工艺、规范审核、正式图层写入或公司块库。

## 后续映射

| 后续项 | 说明 |
| --- | --- |
| `V-PROOF-24` | 若后续登记餐饮对象 / scene benchmark 行，仍需 claim_level 与证据路径 |
| `REST-PROD-04` | 可用于多场景 P3 rollup 或解释模板收口 |
| 表 C | 仍只认 `run_capability_coverage.py` 与真实 verified/showcase 登记 |

## Acceptance 判定

`REST-PROD-03-RESTAURANT-P3-WAVE-ROLLUP` **done** 当：

1. `REST-PROD-01` 与 `REST-PROD-02` 子包契约均通过。
2. 本文、alpha/beta boundary doc 和 manifest 均存在。
3. `assert_restaurant_p3_wave_contract()` 通过。
4. focused 单测与 `run_restaurant_p3_wave_rollup.py --run-benchmarks` 通过。
