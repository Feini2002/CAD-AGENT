# OFFICE-PROD-03：Office P3 波次父包收口

最后更新：2026-05-27

本文是 **§4.2 P3 他场景产品化** 中办公波次的父包 acceptance / rollup，收口 `OFFICE-PROD-01` 与 `OFFICE-PROD-02`。本包只对齐代码轨、文档边界和 no-CAD benchmark 入口，**不**新增真实 CAD `geometry_verified` 结论。

## 收口结论

| 子包 | 状态 | 产物 | 结论 |
| --- | --- | --- | --- |
| `OFFICE-PROD-01` | done | `office_alpha_boundary.py`、`office-prod-alpha-01`、18-case alpha benchmark | 办公 alpha 边界可审计 |
| `OFFICE-PROD-02` | done | `office_beta_boundary.py`、`office-prod-beta-01`、9-case scene beta benchmark | 办公 beta 边界可审计 |
| `OFFICE-PROD-03` | done | 本文 + `office_p3_wave.py` + 父包单测 | 办公 P3 代码轨正式收口 |

## 机器入口（P3 Office 全链路）

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_office_prod_03_p3_wave_rollup -v
& $py scripts\run_office_p3_wave_rollup.py --run-benchmarks --output output\validation_runs\office-prod-03-p3-rollup-no-cad
```

契约断言：`core.agents.office_p3_wave.assert_office_p3_wave_contract()`

## 可声称

- `OFFICE-PROD-01` / `OFFICE-PROD-02` 的 manifest、boundary doc、benchmark suite 和 registry beta rows 均可被父包契约统一审计。
- no-CAD：office alpha benchmark **18/18**，office scene beta benchmark **9/9**（7 pass + 2 blocked_expected）。
- `V-PROOF-24` 的办公代码轨前置已收口；后续能力证明和真实 CAD 仍走 §3 / §5。

## 不得声称

- 不得因 `OFFICE-PROD-03` 或 no-CAD benchmark pass 声称办公场景已真实 CAD `geometry_verified`。
- 不得把 `benchmark_pass_non_cad`、`blocked_expected_non_cad`、manifest 或 registry smoke 行当作表 C 主指标上涨。
- 不得把 `agents/office` scaffold 写成完整办公产品 Agent；本包只收口 P3 办公波次边界。

## 后续映射

| 后续项 | 说明 |
| --- | --- |
| `V-PROOF-24` | office object / scene benchmark 行的能力证明 |
| `REST-PROD-01` | P3 他场景下一包：餐饮 alpha 边界 |
| 表 C | 仍只认 `run_capability_coverage.py` 与真实 verified/showcase 登记 |

## Acceptance 判定

`OFFICE-PROD-03-OFFICE-P3-WAVE-ROLLUP` **done** 当：

1. `OFFICE-PROD-01` 与 `OFFICE-PROD-02` 子包契约均通过。
2. 本文、alpha/beta boundary doc 和 manifest 均存在。
3. `assert_office_p3_wave_contract()` 通过。
4. focused 单测与 `run_office_p3_wave_rollup.py --run-benchmarks` 通过。
