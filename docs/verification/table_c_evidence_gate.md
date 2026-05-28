# Table C Evidence Gate

最后更新：2026-05-28

本文记录 `CAD-EVIDENCE-01-HARD-AUDIT-VISUAL-GATE` 的边界。该门禁用于 **表 C / registry writeback 前** 的硬证据审计和截图复盘，不直接提升表 C。

## 目标

表 C 推进前必须同时满足：

1. `verified` / `showcase` registry 行的 `evidence.report_path` 存在。
2. 证据报告满足 `readback_geometry_verified` 或 `cad_capability_verified` 契约。
3. 新一轮真实 CAD 输出有截图复盘报告。
4. 截图复盘 `status=pass`，否则本轮不得 registry writeback。

## 命令

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"

& $py scripts\run_capability_evidence_audit.py `
  --output output\validation_runs\table-c-evidence-gate\evidence_audit_report.json

& $py scripts\run_visual_cad_review.py `
  --execution-summary <execution_summary.json> `
  --readback-report <readback_report.json> `
  --screenshot <cad-window.png> `
  --output-dir output\validation_runs\table-c-evidence-gate

& $py scripts\run_table_c_evidence_gate.py `
  --evidence-audit-report output\validation_runs\table-c-evidence-gate\evidence_audit_report.json `
  --visual-review-report output\validation_runs\table-c-evidence-gate\visual_review_report.json `
  --coverage-output output\validation_runs\capability-lab\cad_capability_coverage.json
```

`scripts\run_capability_coverage.py` 也支持：

```powershell
& $py scripts\run_capability_coverage.py --require-evidence-audit-pass
```

## 硬门规则

| 条件 | 结果 |
| --- | --- |
| evidence audit 失败 | 阻止 writeback |
| screenshot 缺失或为空 | 阻止 writeback |
| visual review 失败 | 阻止 writeback |
| readback report 不是 `geometry_verified` | 阻止 writeback |
| `geometry_verified` 缺 created handles / entities / all-pass checks | 阻止 writeback |
| screenshot-only / no-CAD / dry-run-only | 不得提升表 C |

## 当前基线

本包首次对现有 registry 跑硬审计：

```text
output/validation_runs/table-c-evidence-gate/evidence_audit_report.json
status=fail
audited_count=131
passed_count=59
failed_count=72
```

这说明历史 `verified/showcase` 行里存在两类证据债：

- `report_path_missing`
- 旧报告缺少新契约要求的 `checks`、`actual.created_handles`、`actual.entities` 或 `contract_version`

该失败不改变当前表 C 机器值；它只表示后续 **新一轮表 C writeback** 必须先过硬门，旧证据债需另开补齐包处理。

## 边界

- 截图是硬门，但仍只是 `visual_aid_only`。
- 几何准确只能由 created handles readback 与 `geometry_verified` 证明。
- 该门禁默认只读 registry 和报告；不会保存 DWG、删除实体或修改正式图层。
