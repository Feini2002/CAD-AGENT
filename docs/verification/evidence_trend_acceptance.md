# LCAD-11-EVIDENCE-TREND-ROLLUP 父包收口

最后更新：2026-05-28

本文是 `LCAD-11-EVIDENCE-TREND-ROLLUP` 的父包 acceptance / rollup。它只收口 evidence trend 机器可读索引与汇总，不新增真实 CAD 几何结论，不把 trend JSON、schema pass 或 coverage metric 当成 `geometry_verified`。

## 收口结论

| 子包 | 状态 | 产物 | 结论 |
| --- | --- | --- | --- |
| `LCAD-11.1` | done | `core/verification/evidence_trend.py`、`core/schemas/evidence_trend.schema.json` | trend JSON 字段与 evidence 词表对齐 |
| `LCAD-11.2` | done | `run_local_cad_regression` → `local_cad_regression_trend.json` | no-CAD 可复跑趋势 rollup |
| `LCAD-11.3` | done | `run_cad_validation` → `cad_validation_trend_index.json` | validation 历次报告机器可读索引 |
| `LCAD-11.4` | done | `run_capability_coverage` → `capability_coverage_trend.json` | coverage 指标进入 `snapshot.metrics` |
| `LCAD-11.5` | done | `docs/verification/evidence_trend_boundaries.md` | 趋势报告「不能声称」边界已固定 |
| `LCAD-11` 父包 | done | 本文 + handoff / CHANGELOG / 任务清单同步 | 父包 `LCAD-11-EVIDENCE-TREND-ROLLUP` 收口 |

## 机器入口

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_local_cad_regression.py --no-cad --output-dir output\validation_runs\lcad-11-2-regression-trend-json
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\lcad-11-3-validation-trend-index
& $py scripts\run_capability_coverage.py --output output\validation_runs\lcad-11-4-coverage-trend-hook\cad_capability_coverage.json
& $py -m unittest tests.core.test_lcad_11_parent_rollup tests.core.test_evidence_trend_boundaries_doc tests.core.test_evidence_trend tests.core.test_capability_coverage tests.core.test_cad_validation_trend_index tests.core.test_local_cad_regression_trend
```

## 可声称

- LCAD-11 系列已提供统一 evidence trend JSON，供 `V-PROOF-71` 趋势 Dashboard 消费。
- `local_cad_regression_trend.json` 的 no-CAD run 会把真实 CAD case 标为 `deferred_cad_readback_required`，不把 deferred 当成 `geometry_verified`。
- `cad_validation_trend_index.json` 是历史索引；可吸收旧真实 CAD snapshots，也可包含本轮 no-CAD snapshot。
- `capability_coverage_trend.json` 把 `cad_proof_coverage_rate`、`verified_count`、`showcase_count` 等放入 `snapshot.metrics`；表 C 机器值仍以 `cad_capability_coverage.json` 为准。
- `RCAD-27` 已于 2026-05-27 在用户 CAD 会话完成真实 CAD regression strict：`status=pass`、9/9 `geometry_verified_case_count`、105 created handles；趋势复算为 `output/validation_runs/rcad-27-trend-rollup-cad-20260527-escalated/evidence_trend/local_cad_regression_trend.json`。
- `evidence_trend_boundaries.md` 已把 `V-PROOF-71`、三类 trend 报告与不得声称边界写清楚。

## 不得声称

- 不得声称 trend JSON 自身新增 `geometry_verified`。
- 不得声称 `snapshot.metrics.cad_proof_coverage_rate` 或表 C 主指标等同于真实 CAD 几何准确率。
- 不得声称 `capability_coverage_trend.json` 可替代 registry 行级 `claim_level=verified` / `showcase` 回写。
- 不得声称历史 trend 索引中含几何 snapshots 就代表本轮执行了真实 CAD。
- 不得把 no-CAD pass、schema pass、dry-run pass、截图或 trend schema pass 当成 created-handle readback。
- 不得把 `negative_guard_verified`、`deferred_cad_readback_required`、`dry_run_valid_plan_only` 计入几何证明。

## 后续映射

| 后续项 | 当前状态 | 说明 |
| --- | --- | --- |
| `RCAD-27` | verified（2026-05-27） | 真实 CAD local regression strict；趋势 JSON 见 escalated run |
| `V-PROOF-71` | **done** | `capability_trend_dashboard.json`；见 `vproof-71-trend-dashboard` |
| `V-PROOF-02` | 持续 | coverage 主报告；trend hook 由 LCAD-11.4 提供 |
| §4 代码轨 | done | 52/52 对账收口（2026-05-28）；继续见 PlanMD 后置或 §3 |

## Acceptance 判定

`LCAD-11-EVIDENCE-TREND-ROLLUP` 可以标为代码轨父包收口，当且仅当：

1. `LCAD-11.1` 到 `LCAD-11.5` 均为 done。
2. 本文与 `evidence_trend_boundaries.md` 均存在并通过文档契约测试。
3. focused trend 测试通过。
4. 状态页、任务清单、CHANGELOG 和 handoff 均把 §4 next 推出 LCAD-11 父包 pending。

本 acceptance 不新增真实 CAD 几何结论。
