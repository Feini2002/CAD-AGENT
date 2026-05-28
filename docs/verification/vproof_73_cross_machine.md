# V-PROOF-73：换机 Playbook + 覆盖率复算（PROJ-03）

最后更新：2026-05-28

> 机器入口：`core/verification/cross_machine_proof.py`、`scripts/run_vproof_73_cross_machine_sync.py`
> 人类 Runbook：`docs/onboarding/migration-checklist.md`
> Baseline：`examples/capability_proof/cross_machine_coverage_baseline.json`

## 登记行（2）

| capability_id | 说明 |
| --- | --- |
| `project.cross_machine.playbook` | 机器可读换机步骤 + user_gate 清单 |
| `project.cross_machine.coverage_recalc` | 本机 coverage 与 baseline 对比 |

全部 `claim_level=smoke`、`ladder_level=L0`。

## 退出条件

- `cross_machine_report.json`：`status=pass`（no-CAD 四步全绿）
- coverage 复算与 baseline **headline / total_count** 在容差内（同 registry 应一致）
- user_gate 三步在报告中列为 `pending`（不要求本包跑真实 CAD）
- 2 行 registry smoke；2/2 writeback

## no-CAD 机器审计（本包自动）

1. `git --version`
2. CAD-MCP `.venv` Python 存在
3. `scripts/self_check.py`
4. `run_capability_coverage.py` + 与 baseline 对比

## user_gate（人工，见 migration-checklist）

1. AutoCAD 已开 + `CODEX_PREVIEW` DWG
2. `run_cad_validation.py` 全量或 geometry-gate pass
3. Cursor/Codex + CAD-MCP 落图 smoke

## 不得声称

- 不得把 no-CAD 机器审计 pass 说成换机已完成或 `geometry_verified`。
- 不得把 coverage 复算 pass 说成表 C 主指标提升。
- baseline 仅在 canonical registry 变更时更新；换机后若 headline 不一致先查 registry 是否同步。

## 复跑

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_vproof_73_cross_machine_sync.py
```

换机全量验收仍按 `docs/onboarding/migration-checklist.md` 逐步执行。
