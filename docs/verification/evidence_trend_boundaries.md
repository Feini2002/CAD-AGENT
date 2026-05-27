# LCAD-11.5：Evidence Trend 声明边界

最后更新：2026-05-27

> 机器入口：`core/verification/evidence_trend.py`、`run_local_cad_regression.py`、`run_cad_validation.py`、`run_capability_coverage.py`  
> 当前趋势证据：
> - `output/validation_runs/lcad-11-2-regression-trend-json/evidence_trend/local_cad_regression_trend.json`
> - `output/validation_runs/lcad-11-3-validation-trend-index/evidence_trend/cad_validation_trend_index.json`
> - `output/validation_runs/lcad-11-4-coverage-trend-hook/evidence_trend/capability_coverage_trend.json`

本文只定义 LCAD-11 evidence trend 系列的用途、可声称内容和不得声称边界。趋势报告是机器可读索引和汇总，不是新的 CAD 落图证据；它不能替代真实 AutoCAD created-handle readback。

## 包边界

| 包 ID | 状态 | 证明内容 | 机器证据 |
| --- | --- | --- | --- |
| `LCAD-11.1` | done | evidence trend schema、词表和完整 count 字段 | `core/schemas/evidence_trend.schema.json` |
| `LCAD-11.2` | done | `run_local_cad_regression` 输出 `local_cad_regression_trend.json` | `output/validation_runs/lcad-11-2-regression-trend-json/evidence_trend/local_cad_regression_trend.json` |
| `LCAD-11.3` | done | `run_cad_validation` 输出 `cad_validation_trend_index.json` | `output/validation_runs/lcad-11-3-validation-trend-index/evidence_trend/cad_validation_trend_index.json` |
| `LCAD-11.4` | done | `run_capability_coverage` 输出 `capability_coverage_trend.json` | `output/validation_runs/lcad-11-4-coverage-trend-hook/evidence_trend/capability_coverage_trend.json` |
| `LCAD-11.5` | done | 本文：趋势报告「不能声称」说明 | `tests.core.test_evidence_trend_boundaries_doc` |

## 三类趋势报告

| 报告 | source_kind | 可读含义 | 不能替代 |
| --- | --- | --- | --- |
| `local_cad_regression_trend.json` | `local_cad_regression` | local CAD regression case 的 evidence_state 汇总 | 真实 CAD strict 复跑、created-handle readback |
| `cad_validation_trend_index.json` | `cad_validation` | 同级 validation run 的历史 `report.json` 索引 | 本轮新增真实 CAD 几何证明 |
| `capability_coverage_trend.json` | `capability_coverage` | registry coverage 指标快照；coverage 字段在 `snapshot.metrics` | registry 行回写、真实 CAD 证据、showcase |

## 可声称

- 可以声明 LCAD-11 系列已经提供统一 evidence trend JSON 结构，供 `V-PROOF-71` 趋势 Dashboard 消费。
- 可以声明 `local_cad_regression_trend.json` 的 no-CAD run 会把真实 CAD case 标为 `deferred_cad_readback_required`，不把 deferred 当成 `geometry_verified`。
- 可以声明 `cad_validation_trend_index.json` 是历史索引；它可能吸收旧的真实 CAD snapshots，也可能包含本轮 no-CAD snapshot。
- 可以声明 `capability_coverage_trend.json` 把 `cad_proof_coverage_rate`、`verified_count`、`total_count` 等覆盖率指标放入 `snapshot.metrics`。
- 可以声明当前覆盖率仍为 262 行、128 verified、`cad_proof_coverage_rate=48.85%`，以 coverage 报告和 registry 为准。

## 不得声称

- 不得声称 trend JSON 自身新增 `geometry_verified`。
- 不得声称 `snapshot.metrics.cad_proof_coverage_rate` 等同于真实 CAD 几何准确率。
- 不得声称 `capability_coverage_trend.json` 可以替代 registry 行级 `claim_level=verified` 回写。
- 不得声称 `cad_validation_trend_index.json` 中含历史几何 snapshots，就代表本轮执行了真实 CAD。
- 不得声称 no-CAD pass、schema pass、dry-run pass、截图或 trend schema pass 可以替代 created-handle readback。
- 不得把 `negative_guard_verified`、`deferred_cad_readback_required`、`dry_run_valid_plan_only` 算作几何证明。

## 展示与状态口径

| 口径 | 看哪 | 说明 |
| --- | --- | --- |
| 工程完备度 | `CORE_STATUS.md` 表 A | 回答底座开发节奏，不代表 CAD 证明覆盖率 |
| 任务包完成度 | `docs/planning/任务清单.md` 表 B | 回答三指令队列推进，不代表真实几何准确 |
| CAD 证明覆盖率 | `cad_capability_coverage.json` / `capability_coverage_trend.json` 的 `snapshot.metrics` | 只统计 `verified` + `showcase` registry 行 |
| 单次真实 CAD 几何 | 对应 `report.json`、`readback_report.json`、created handles | 必须有实际 CAD 输出和回读 |

## 复跑命令

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_local_cad_regression.py --no-cad --output-dir output\validation_runs\lcad-11-2-regression-trend-json
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\lcad-11-3-validation-trend-index
& $py scripts\run_capability_coverage.py --output output\validation_runs\lcad-11-4-coverage-trend-hook\cad_capability_coverage.json
```

## 子校验

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_evidence_trend_boundaries_doc tests.core.test_evidence_trend tests.core.test_capability_coverage tests.core.test_cad_validation_trend_index tests.core.test_local_cad_regression_trend
```
