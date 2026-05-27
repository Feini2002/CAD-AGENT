# Core Context Brief

最后更新：2026-05-27（最终回复精简口径）

本文是后续 Codex / Cursor 接手本仓库时的稳定短上下文入口。默认先读 `AGENTS.md`，再读本文；只有执行具体包、完整复盘、排查失败、修改规则或同步状态时，才展开详细文档。

## 当前一句话

本仓库是可迁移的通用 CAD Agent Core Lab：Core 底座、非 CAD benchmark、真实 CAD 验证入口和能力登记体系已经较厚；真实 CAD 准确性仍只按 `CAD_PLAN` → validate → dry-run → `CODEX_PREVIEW` → created handles 回读 → `geometry_verified` 证明，不得用截图、RCAD 烟囱进度或工程百分比替代。

## 当前精简进度快照

聊天最终回复默认用精简表，完整 A/B/C 只在状态汇报、交接、审计、进度盘点或表 C 专题时展开。表 C 只认最新机器报告：`output/validation_runs/capability-lab/cad_capability_coverage.json`。本轮复跑时间：2026-05-27T09:03:34Z。

| 口径 | 当前值 | 说明 |
| --- | --- | --- |
| **真实 CAD 实力** | **约 4.35%**，最高已证 **L4** | 表 C 主指标；瓶颈是 showcase，就绪度约 4.35% |
| CAD 证明覆盖率 | 约 47.10%（130/276；118 verified + 12 showcase） | coverage JSON 机器值 |
| 工程节奏 | 总约 94%（Core 96%，Agent 88%） | 表 A 折叠 |
| 任务台账 | 能力证明约 56%（24/43），代码轨约 76%（42/55），CAD 补验约 76%（22/29 verified） | 表 B 折叠；CAD 补验 **≠ 画图实力** |

## 当前 next

| 用户口令 | 默认动作 |
| --- | --- |
| `一键推进` | 推进 `docs/planning/任务清单.md` §4 的 `OFFICE-PROD-03` |
| `能力证明` / `覆盖率` | 推进 §3 的 `V-PROOF-34-BLOCK-FIRST-ROW` |
| `CAD 补验` / `开 CAD 了` | 推进 §5 的 `RCAD-22-CAPABILITY-PROBE-BETA` |
| `真实 CAD 实力` / `推进表 C` | 按 §0.1 编排 `V-PROOF-34` + 链式 `RCAD-25` + registry 回写 + coverage 复跑 |
| `刷新表 C` | 只复跑 `scripts/run_capability_coverage.py`，不新开包 |

## 最近有效事实

- `RCAD-15-SYMBOL-GLYPH-SOFA` 已完成真实 CAD 补验：`seating_sofa_plan.json` → 6 handles、`geometry_verified`；RCAD 现为 22/29 verified。
- `OFFICE-PROD-02-OFFICE-BETA-BOUNDARY` 已完成：office scene_beta 9/9 no-CAD（7 pass + 2 blocked_expected），未运行真实 CAD。
- `CORE-P4`、`RBLOCK-08`、`CFIT-13` 已完成父包收口；这些是代码轨 / no-CAD 契约收口，不自动提升表 C。
- `V-PROOF-60`~`63` 已建立 showcase/Ladder 初版，最高已证 L4；当前主瓶颈仍是 showcase 分母，主指标约 4.35%。
- `CAD-VAL-02`、`LCAD-12`~`14` 已强化几何门禁、hatch deferred、session snapshot 和 guard full runner；guard-only 证据不计入几何 verified。

## 主从关系

- `CORE_RESTRUCTURE_PLAN.md` 是唯一 `PlanMD`：决定方向、优先级、Decision Gate、退出标准和后置 Backlog。
- `docs/planning/任务清单.md` 是唯一执行台账：维护能力证明、代码轨、CAD 补验包状态、计数和当前 `next` 镜像。
- `CORE_STATUS.md` / `CAD_AGENT_STATUS.md` 只写能力、证据、风险和当前状态，不承载独立下一步。
- `docs/planning/phase-*.md` 只是 Phase 辅助执行剧本，不能复制出第二套主计划或后置 Backlog。
- 若 Markdown 数字与 `cad_capability_coverage.json` 冲突，表 C 以 JSON 为准；若任务 next 冲突，先按 PlanMD 决策修正任务清单，再执行。

## 不能声称

- 不能把 Core 约 96%、RCAD 22/29 或任意 no-CAD benchmark 说成“已经能画准施工图”。
- 不能把截图、SVG/PNG 预览、`render_preview.py --check`、dry-run 或 `benchmark_pass_non_cad` 当成几何准确证据。
- 不能把 `negative_guard_verified`、fake driver `geometry_verified`、hatch structured deferred 或 no-CAD deferred 当成真实 CAD 几何通过。
- 不能把 `office/residential/restaurant` 的 preferences、rules、Alpha/Beta benchmark 写成 Scene Product 完成。
- 不能默认保存、覆盖、删除 DWG，不能修改正式图层；真实 CAD 默认只写 `CODEX_PREVIEW`。

## 按需展开

| 目标 | 先读 |
| --- | --- |
| 执行当前开发包 / 调整优先级 | `CORE_RESTRUCTURE_PLAN.md` + `docs/planning/任务清单.md` |
| 汇报完整能力成熟度 / 展开 A/B/C | `CORE_STATUS.md` + `CAD_AGENT_STATUS.md` + coverage JSON |
| CAD 补验 / 画不准 / 环境不通 | `CAD_AGENT_BLOCKER_PLAYBOOK.md` + `CAD_AGENT_AUTONOMOUS_VALIDATION.md` |
| 查历史变更流水 | `CAD_AGENT_CHANGELOG.md` |
| 查失败教训和活跃风险 | `CAD_AGENT_ISSUES.md` |
| 查 Cursor 按包交接 | `docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` + `docs/handoffs/README.md` |
| 新人接手 | `docs/onboarding/first-handoff.md` |
| 文档治理 | `docs/planning/phase-z-doc-governance-plan.md` |

## 常用验证

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest discover -s tests
& $py scripts\self_check.py
& $py scripts\render_preview.py --check
& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
& $py scripts\run_capability_coverage.py --output output\validation_runs\capability-lab\cad_capability_coverage.json
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\manual-no-cad
```

## 缓存友好约定

- 本文只写短摘要、当前 next、口径和入口，不写长历史。
- 大段历史进 `CAD_AGENT_CHANGELOG.md` 或 `docs/history/`。
- 失败教训进 `CAD_AGENT_ISSUES.md`。
- 计划和优先级进 `CORE_RESTRUCTURE_PLAN.md`，执行计数进 `docs/planning/任务清单.md`。
