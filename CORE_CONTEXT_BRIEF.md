# Core Context Brief

最后更新：2026-05-28（DOC-ARCH-REBASE）

本文是后续 Codex / Cursor 接手本仓库时的稳定短上下文入口。默认先读 `AGENTS.md`，再读本文；只有执行具体包、完整复盘、排查失败、修改规则或同步状态时，才展开详细文档。

## 当前一句话

本仓库是可迁移的通用 CAD Agent Core Lab。真实 CAD 准确性只按 `CAD_PLAN` → validate → dry-run → `CODEX_PREVIEW` → created handles 回读 → `geometry_verified` 证明；不能用截图、no-CAD benchmark、RCAD 台账或工程百分比替代。

## 当前精简进度

表 C 只认机器报告：`output/validation_runs/capability-lab/cad_capability_coverage.json`。

| 口径 | 当前值 | 说明 |
| --- | --- | --- |
| **真实 CAD 实力** | **约 8.87%**，最高已证 **L4** | 表 C 主指标；本轮文档重构不改变表 C |
| CAD 证明覆盖率 | 约 48.58%（137/282；112 verified + 25 showcase） | coverage JSON 机器值 |
| 工程节奏 | 总约 95%（Core 96%，Agent 93%） | 表 A 折叠 |
| 任务台账 | 能力证明约 78%，代码轨约 89%，CAD 补验 100% | 表 B 折叠；CAD 补验 **≠ 画图实力** |

## 当前 next

| 用户口令 | 默认动作 |
| --- | --- |
| `一键推进` | 下一代码包按 `CORE_RESTRUCTURE_PLAN.md` 决策 |
| `能力证明` / `覆盖率` | 推进 `docs/planning/任务清单.md` §3 的 next |
| `CAD 补验` / `开 CAD 了` | §5 暂无 pending；默认转入表 C / 能力证明 |
| `真实 CAD 实力` / `推进表 C` | 按 §0.1 编排 V-PROOF + RCAD + registry 回写 + coverage |
| `刷新表 C` | 只复跑 `scripts/run_capability_coverage.py` |

## 最近有效事实

- `DOC-ARCH-REBASE` 正在把根目录长文档迁移到 `docs/status/`、`docs/governance/`、`docs/runbooks/`，把 handoff 巨型文件拆成 current / index / archive / template，并新增 `scripts/run_doc_governance_audit.py`。
- `STRUCT-MERGE-01` 已完成：`drawing_policy.py` 合并进 `templates.py`，并修复 `block_matrix_registry` 对 `showcase` claim_level 的同步识别；全测曾为 864 tests OK。
- `VCAD-02` 已完成真实 AutoCAD 视觉表达 P1：99 created handles 回读，`visual_geometry_verified`；这是视觉表达证据，不改变表 C。
- `V-PROOF-42-COMPOSITION-EXPAND` 已完成真实 CAD 刷新：4/4 office composition case `geometry_verified`，40 created handles 回读；coverage 数值保持 8.87% 主指标。
- `V-PROOF-60`~`66` 已建立 showcase / Ladder 初版，最高已证 L4；当前主瓶颈仍是 showcase 就绪度。

## 主从关系

- `CORE_RESTRUCTURE_PLAN.md` 是唯一 `PlanMD`。
- `docs/planning/任务清单.md` 是唯一执行台账和即时 `next` 镜像。
- `CORE_STATUS.md` 解释能力状态和表 C；机器值以 coverage JSON 为准。
- `docs/status/current.md` 写当前状态；`docs/status/changelog.md` 写历史流水；`docs/status/issues.md` 写风险和教训。
- `docs/handoffs/current.md` 写最近包交接；`docs/handoffs/package-index.md` 查全量包；历史包在 `docs/handoffs/archive/`。
- `output/validation_runs/**` 是机器证据本体，不因 Markdown 整合而移动。

## 不能声称

- 不能把 Core 约 96%、RCAD 29/29 或 no-CAD benchmark 说成“已经能画准施工图”。
- 不能把截图、SVG/PNG 预览、dry-run 或 `benchmark_pass_non_cad` 当成几何准确证据。
- 不能把 `negative_guard_verified`、fake driver 结果或 no-CAD deferred 当成真实 CAD 几何通过。
- 不能默认保存、覆盖、删除 DWG，不能修改正式图层；真实 CAD 默认只写 `CODEX_PREVIEW`。

## 按需展开

| 目标 | 先读 |
| --- | --- |
| 执行当前开发包 / 调整优先级 | `CORE_RESTRUCTURE_PLAN.md` + `docs/planning/任务清单.md` |
| 汇报完整能力成熟度 / 展开 A/B/C | `CORE_STATUS.md` + `docs/status/current.md` + coverage JSON |
| CAD 补验 / 画不准 / 环境不通 | `docs/runbooks/blocker-playbook.md` + `docs/runbooks/cad-validation.md` |
| 查历史变更流水 | `docs/status/changelog.md` |
| 查失败教训和活跃风险 | `docs/status/issues.md` |
| 查按包交接 | `docs/handoffs/current.md` + `docs/handoffs/package-index.md` |
| 新人接手 | `docs/onboarding/first-handoff.md` |
| 文档治理 | `docs/planning/phases/phase-z-doc-governance.md` + `scripts/run_doc_governance_audit.py` |

## 常用验证

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest discover -s tests
& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
& $py scripts\run_doc_governance_audit.py
& $py scripts\run_dev_volume_audit.py
& $py scripts\run_capability_coverage.py --output output\validation_runs\capability-lab\cad_capability_coverage.json
```

## 缓存友好约定

- 本文只写短摘要、当前 next、口径和入口，不写长历史。
- 历史进 `docs/status/changelog.md` 或 `docs/history/`。
- 失败教训进 `docs/status/issues.md`。
- 计划和优先级进 `CORE_RESTRUCTURE_PLAN.md`，执行计数进 `docs/planning/任务清单.md`。
