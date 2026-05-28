# RESIDENTIAL-PROD-03：Residential P3 波次父包收口

最后更新：2026-05-28

本文是 **§4.2 P3 他场景产品化** 中住宅波次的父包 acceptance / rollup，收口 `RESIDENTIAL-PROD-01` 与 `RESIDENTIAL-PROD-02`。本包只对齐代码轨、文档边界和 no-CAD benchmark 入口，**不**新增真实 CAD `geometry_verified` 结论。

## 收口结论

| 子包 | 状态 | 产物 | 结论 |
| --- | --- | --- | --- |
| `RESIDENTIAL-PROD-01` | done | `residential_alpha_boundary.py`、`residential-prod-alpha-01`、scene alpha residential case | 住宅 alpha 边界可审计 |
| `RESIDENTIAL-PROD-02` | done | `residential_beta_boundary.py`、`residential-prod-beta-01`、8-case scene beta benchmark | 住宅 beta 边界可审计 |
| `RESIDENTIAL-PROD-03` | done | 本文 + `residential_p3_wave.py` + 父包单测 | 住宅 P3 代码轨正式收口 |

## 机器入口（P3 Residential 全链路）

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_res_prod_03_p3_wave_rollup -v
& $py scripts\run_residential_p3_wave_rollup.py --run-benchmarks --output output\validation_runs\res-prod-03-p3-rollup-no-cad
```

契约断言：`core.agents.residential_p3_wave.assert_residential_p3_wave_contract()`

## 可声称

- `RESIDENTIAL-PROD-01` / `RESIDENTIAL-PROD-02` 的 manifest、boundary doc、benchmark suite 和 registry beta rows 均可被父包契约统一审计。
- no-CAD：scene alpha residential case 为 `benchmark_pass_non_cad`；residential scene beta benchmark **8/8**（7 pass + 1 blocked_expected）。
- `BETA-SCENE-02` 的住宅代码轨前置已收口；后续能力证明和真实 CAD 仍走 §3 / §5。

## 不得声称

- 不得因 `RESIDENTIAL-PROD-03` 或 no-CAD benchmark pass 声称住宅场景已真实 CAD `geometry_verified`。
- 不得把 `benchmark_pass_non_cad`、`blocked_expected_non_cad`、manifest 或 registry smoke/deferred 行当作表 C 主指标上涨。
- 不得把 `agents/residential` scaffold 写成完整住宅产品 Agent；本包只收口 P3 住宅波次边界。
- 不得扩大到规范审核、正式图层写入或公司块库。

## 后续映射

| 后续项 | 说明 |
| --- | --- |
| `REST-PROD-04` | 多场景 P3 父包可扩展纳入住宅三场景对称 |
| `SCENE-PROD-06` | 多场景回归门禁已含 residential beta |
| 表 C | 仍只认 `run_capability_coverage.py` 与真实 verified/showcase 登记 |

## Acceptance 判定

`RESIDENTIAL-PROD-03-RESIDENTIAL-P3-WAVE-ROLLUP` **done** 当：

1. `RESIDENTIAL-PROD-01` 与 `RESIDENTIAL-PROD-02` 子包契约均通过。
2. 本文、alpha/beta boundary doc 和 manifest 均存在。
3. `assert_residential_p3_wave_contract()` 通过。
4. focused 单测与 `run_residential_p3_wave_rollup.py --run-benchmarks` 通过。
