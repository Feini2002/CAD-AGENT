# LCAD-10-NEGATIVE-SAFETY 父包收口

最后更新：2026-05-28

本文是 `LCAD-10-NEGATIVE-SAFETY` 的父包 acceptance / rollup。它只收口负向 CAD 安全链路，不新增真实 CAD 几何结论，不把 `negative_guard_verified` 计入几何证明。

## 收口结论

| 子包 | 状态 | 产物 | 结论 |
| --- | --- | --- | --- |
| `LCAD-10.1` | done | `examples/plans/negative/`、`scripts/run_negative_cad_plan_suite.py` | 负向 `CAD_PLAN` fixture 可被 schema / validator 拒收 |
| `LCAD-10.2` | done | `scripts/run_write_guard_cad_runner.py` | preview-only write guard 可阻断正式图层写入、保存、覆盖、删除 |
| `LCAD-10.3` | done | `scripts/run_negative_cad_runner.py` | fake/no-CAD 负向 runner 输出 `negative_guard_verified`、`created_handles=[]` |
| `LCAD-10.4` | done | `docs/verification/negative_cad_safety_boundaries.md` | 负向与安全边界扫描文档已固定 |
| `LCAD-10.5` | done | 本文 + handoff / CHANGELOG / 任务清单同步 | 父包 `LCAD-10-NEGATIVE-SAFETY` 收口 |

## 机器入口

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_negative_cad_plan_suite.py
& $py scripts\run_write_guard_cad_runner.py --output-dir output\validation_runs\lcad-10-write-guard
& $py scripts\run_negative_cad_runner.py --output-dir output\validation_runs\neg-cad-proof-sync\negative-runner-fake-final
& $py -m unittest tests.core.test_lcad_10_parent_rollup tests.core.test_negative_cad_safety_boundaries_doc tests.core.test_negative_cad_plans tests.core.test_write_guard_cad_runner tests.core.test_negative_cad_runner
```

## 可声称

- 负向 CAD_PLAN fixture 覆盖了当前登记的主要 failure categories，并能被拒收。
- preview-only 安全守卫会拒绝正式层写入、保存、覆盖和删除。
- fake/no-CAD 负向 runner 可生成 guard-only 证据：`negative_guard_verified`、`created_handles=[]`、`preview_layer_entity_delta=0`、`modelspace_entity_delta=0`。
- 后续 `RCAD-20` 已于 2026-05-27 在用户 CAD 会话下完成真实 CAD 负向安全补验：`status=pass`、`evidence_state=negative_guard_verified`、`created_handles=[]`、entity delta 为 0。
- `negative_cad_safety_boundaries.md` 已把 `RCAD-20`、`V-PROOF-50`、`V-PROOF-51` 的声明边界写清楚。

## 不得声称

- 不得把后续 `RCAD-20` 的真实 CAD `negative_guard_verified` 当成父包新增的几何证明。
- 不得声称 `negative_guard_verified` 等于 `geometry_verified`。
- 不得把 `created_handles=[]`、schema pass、dry-run pass、截图或 write guard pass 当成正向绘图几何准确。
- 不得把本父包计入 CAD 证明覆盖率；它只提供 guard-only 证据，不计入几何证明。
- 不得声称任意 `CAD_PLAN`、真实项目 DWG、公司块库或正式图层操作已安全可用。

## 后续映射

| 后续项 | 当前状态 | 说明 |
| --- | --- | --- |
| `RCAD-20` | verified（2026-05-27） | 真实 CAD 负向安全 runner 已在用户 CAD 会话通过；证据：`output/validation_runs/rcad-20-negative-cad-20260527-escalated/negative_cad_runner_report.json` |
| `V-PROOF-50` | scheduled | 负向 plan 清单进 registry；每类 `failure_category` 一行 |
| `V-PROOF-51` | scheduled | 真实 CAD：无 handles、不保存 |
| `LCAD-11.1`~`11.5` | done | evidence trend 子包与 `LCAD-11-EVIDENCE-TREND-ROLLUP` 父包已收口；见 `evidence_trend_acceptance.md` |

## Acceptance 判定

`LCAD-10-NEGATIVE-SAFETY` 可以标为代码轨父包收口，当且仅当：

1. `LCAD-10.1` 到 `LCAD-10.5` 均为 done。
2. 本文与 `negative_cad_safety_boundaries.md` 均存在并通过文档契约测试。
3. focused 负向测试通过。
4. 状态页、任务清单、CHANGELOG 和 handoff 均把 `LCAD-10-NEGATIVE-SAFETY` 标为 done。

本 acceptance 不新增真实 CAD 几何结论。父包已于 2026-05-28 收口。
