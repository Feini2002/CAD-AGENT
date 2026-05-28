# V-PROOF-71：Evidence / Coverage 趋势 Dashboard

最后更新：2026-05-28

> 机器入口：`core/verification/trend_dashboard.py`、`scripts/run_vproof_71_trend_dashboard_sync.py`
> 源清单：`examples/capability_proof/trend_dashboard_sources.json`
> 边界（LCAD-11.5）：`docs/verification/evidence_trend_boundaries.md`

## 登记行（4）

| capability_id | 面板 |
| --- | --- |
| `trend.dashboard.rollup` | 顶层 dashboard JSON |
| `trend.dashboard.local_cad_regression` | `local_cad_regression_trend.json` |
| `trend.dashboard.cad_validation_index` | `cad_validation_trend_index.json` |
| `trend.dashboard.capability_coverage` | `capability_coverage_trend.json` |

全部 `claim_level=smoke`、`ladder_level=L0`。

## 退出条件

- `capability_trend_dashboard.json` schema pass、`status=pass`
- **必需**面板 `capability_coverage` present 且 trend `status=pass`
- `coverage_headline` 镜像表 C 机器字段（`cad_strength_headline_percent` 等）
- 可选面板：`local_cad_regression`、`cad_validation`（缺失不阻塞，但记入 `present_panel_count`）

## 不得声称

- 不得把 dashboard pass 升为 `verified` / `showcase` 或抬高表 C 主指标。
- 不得把 trend JSON / coverage metric 等同于 `geometry_verified`。
- 不得把历史 validation 索引中含几何 snapshot 说成本轮已跑真实 CAD。
- 表 C 仍以 `output/validation_runs/capability-lab/cad_capability_coverage.json` 为准。

## 复跑

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_vproof_71_trend_dashboard_sync.py
```
