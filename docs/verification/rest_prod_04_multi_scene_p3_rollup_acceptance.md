# REST-PROD-04：Multi-scene P3 父包收口

最后更新：2026-05-27

本文是 **§4.2 P3 他场景产品化** 的跨场景父包 acceptance / rollup，收口 `OFFICE-PROD-03` 与 `REST-PROD-03`。本包只对齐代码轨、验收文档和 no-CAD benchmark 证据边界，**不**新增真实 CAD `geometry_verified` 结论。

## 收口结论

| 子父包 | 状态 | 证据 | 结论 |
| --- | --- | --- | --- |
| `OFFICE-PROD-03` | done | office alpha 18/18 + beta 9/9 no-CAD | 办公 P3 代码轨已收口 |
| `REST-PROD-03` | done | restaurant alpha 1 case + beta 8/8 no-CAD | 餐饮 P3 代码轨已收口 |
| `REST-PROD-04` | done | 本文 + `multi_scene_p3_wave.py` + 父包单测 | P3 多场景父包已统一审计 |

## 机器入口

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_rest_prod_04_multi_scene_p3_rollup -v
& $py scripts\run_multi_scene_p3_rollup.py --output output\validation_runs\rest-prod-04-multi-scene-p3-rollup-no-cad
```

契约断言：`core.agents.multi_scene_p3_wave.assert_multi_scene_p3_wave_contract()`

## 可声称

- `OFFICE-PROD-03` 与 `REST-PROD-03` 的 parent contract、acceptance doc 和 child package rollup 均可被统一审计。
- no-CAD：office alpha **18/18**、office beta **9/9**、restaurant alpha **1 case**、restaurant beta **8/8** 均已通过；证据态包含 `benchmark_pass_non_cad` 与 `blocked_expected_non_cad`。
- `V-PROOF-24` 的办公产品化前置与 `BETA-SCENE-03` 的餐饮产品化前置已经完成代码轨父包收口。

## 不得声称

- 不得因 `REST-PROD-04` 或 no-CAD benchmark pass 声称办公 / 餐饮多场景已经真实 CAD `geometry_verified`。
- 不得把 `benchmark_pass_non_cad`、`blocked_expected_non_cad`、manifest、registry smoke/deferred 行或 parent rollup 当作表 C 主指标上涨。
- 不得把 `agents/office` 或 `agents/restaurant` scaffold 写成完整行业产品 Agent；本包只收口 P3 他场景产品化代码轨边界。
- 不得扩展到住宅、工装、展厅或正式项目 DWG 的真实几何准确声明。

## 后续映射

| 后续项 | 说明 |
| --- | --- |
| `V-PROOF-24` | 若后续登记 office / scene benchmark 行，仍需 claim_level 与证据路径 |
| `BETA-SCENE-03` | 餐饮 beta benchmark 仍是 no-CAD 产品化前置，不是 CAD 几何证明 |
| 表 C | 仍只认 `run_capability_coverage.py` 与真实 verified/showcase 登记 |

## Acceptance 判定

`REST-PROD-04-MULTI-SCENE-P3-ROLLUP` **done** 当且仅当：

1. `OFFICE-PROD-03` 与 `REST-PROD-03` 子父包契约均通过。
2. 本文与两个 child acceptance doc 均存在。
3. `assert_multi_scene_p3_wave_contract()` 通过。
4. focused 单测与 `run_multi_scene_p3_rollup.py` 通过。
