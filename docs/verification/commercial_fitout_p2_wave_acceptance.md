# CFIT P2 工装波次父包收口

最后更新：2026-05-27

本文是 **§4.2 P2 工装波次**（`CFIT-09` … `CFIT-12`）的父包 acceptance / rollup。它只收口代码轨与机器入口对齐，**不**在本父包内新增真实 CAD `geometry_verified` 结论。

## 收口结论

| 子包 | 状态 | 产物 | 结论 |
| --- | --- | --- | --- |
| `CFIT-09` | done | `projects/commercial_fitout_meeting_sample/`、meeting workflow、`fitout_sample_specs` | 第二组工装脱敏样本路径定稿 |
| `CFIT-10` | done | `projects/commercial_fitout_reception_sample/`、reception workflow、rollup 第四行 | 前台接待子场景样本登记 |
| `CFIT-11` | done | `product_alpha_boundary.json` 三样本同步、`assert_fitout_three_sample_rollup_sync()` | boundary / rollup / specs 口径一致 |
| `CFIT-12` | done | `fitout_subscene_object_cad_smoke_manifest.json` + runner | meeting/reception 代表对象 CAD smoke（fake 4/4） |
| `CFIT-13` | done | 本文 + `commercial_fitout_p2_wave.py` + 父包单测 | P2 工装波次代码轨收口 |

## 机器入口（P2 全链路）

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_cfit_13_p2_wave_parent_rollup tests.core.test_cfit_09_meeting_sample tests.core.test_cfit_10_reception_sample tests.core.test_cfit_11_three_sample_boundary_sync tests.core.test_cfit_12_fitout_subscene_object_cad_smoke -v
& $py scripts\run_project_sample_cad_rollup.py --no-cad --output-dir output\validation_runs\cfit-13-p2-rollup-no-cad
& $py scripts\run_fitout_subscene_object_cad_smoke.py --no-cad --output-dir output\validation_runs\cfit-13-subscene-smoke-no-cad
```

契约断言：`core/agents/commercial_fitout_p2_wave.assert_commercial_fitout_p2_wave_contract()`

## 可声称

- 三子场景（`open_office` / `meeting_room` / `reception`）各有脱敏项目样本、workflow、rollup 登记与 `fitout_sample_specs` 注册。
- `product_alpha_boundary` 与 rollup manifest 可通过 `assert_fitout_three_sample_rollup_sync()` 审计。
- meeting/reception 各有代表 catalog 对象的 subscene CAD smoke manifest，服务 `V-PROOF-25` / `RCAD-18` / `RCAD-19`。
- 工装微场景 composition CAD registry manifest（3 case）与 `V-PROOF-42` / `V-PROOF-62` 衔接。

## 不得声称

- 不得因 P2 父包收口或 no-CAD rollup/smoke 通过就声称工装 Scene Product 或任意项目已在真实 AutoCAD 会话 `geometry_verified`。
- 不得将 fake 4/4 subscene smoke 扩大为全部 catalog 14 项或开放办公全库已证。
- 不得把本父包计入表 C 主指标；真实 CAD 实力仍看 `cad_capability_registry` showcase/verified 与 `run_capability_coverage.py`。
- `RCAD-10` / `RCAD-18` / `RCAD-19` 的真实 CAD 补验须单独在用户会话完成并回写 registry。

## 后续映射

| 后续项 | 说明 |
| --- | --- |
| `V-PROOF-25` | CFIT-12 已提供 manifest；registry 回写见能力证明轨 |
| `V-PROOF-62` | 工装微场景 composition showcase（表 C 轨，非本父包） |
| `RCAD-10` / `18` / `19` | 项目 rollup / subscene 对象真实 CAD 烟囱包 |
| §4.2 P4 | `DRAW-01` 已进波；next=`DRAW-02`（P3 `OFFICE-PROD` 仍 user_gate） |

## Acceptance 判定

`CFIT-13` / P2 工装波次可标为 **done**，当且仅当：

1. `CFIT-09` … `CFIT-12` 均为 done。
2. 本文与四份子包 boundary MD 均存在并通过文档/契约测试。
3. `assert_commercial_fitout_p2_wave_contract()` 通过。
4. 任务清单 §4.2 将 `CFIT-13` 标为 done，代码轨 next 转入下一波次占位。
