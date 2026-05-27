# Phase Z Documentation Governance Plan

状态：由 `CORE_RESTRUCTURE_PLAN.md` 拆分而来
最后同步：2026-05-27

> 本文是 Phase Z 辅助执行剧本，不是独立 PlanMD。执行顺序、优先级和退出标准以根目录 `CORE_RESTRUCTURE_PLAN.md` 为准；执行前仍需先读 `AGENTS.md` 与 `CORE_CONTEXT_BRIEF.md`，并遵守 `CODEX_PREVIEW`、不保存、不覆盖、不删除、不改正式图层的 CAD 安全边界。

## Phase Z：长期维护、文档治理和回归基线

目标：把“深度开发后容易混乱”的状态文档、验证命令、问题记录和审计规则固定下来，让后续 Codex 不需要重新考古。

### 执行参考

- 已完成：Z-00 按 `docs/history/core-platform-md-split-plan-2026-05-25.md` 拆分主平台 Markdown：`CORE_RESTRUCTURE_PLAN.md` 收缩为总控索引，Phase W/X/Y/Z 执行剧本迁入 `docs/planning/`。
- Z-01 每次开发先读 `CORE_CONTEXT_BRIEF.md`，只在执行 phase、完整复盘、排查失败或修改规则时展开大文档。
- Z-02 每次 phase 完成后同步唯一 PlanMD `CORE_RESTRUCTURE_PLAN.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md`。
- Z-03 只有遇到失败、回归、排障教训或长期风险时，才更新 `CAD_AGENT_ISSUES.md`。
- Z-04 `CAD_AGENT_STATUS.md` 只保留当前状态，不再堆长历史；历史交给 `CAD_AGENT_CHANGELOG.md`。
- Z-04b `docs/planning/phase-*.md` 只保留辅助执行剧本身份；新增待办、优先级或退出标准时先回写 PlanMD。
- 已完成：Z-05 `docs/history/shell-layout-time-estimate.md` 只作为历史估算，不作为执行计划。
- Z-06 如果未来要迁移根目录文档，优先迁移到 `docs/history/`、`docs/architecture/`、`docs/decisions/` 或 `docs/verification/`，并更新所有引用。
- Z-07 文档改动后至少跑文本自查，防止过期 phase、占位词、不存在命令、重复 `next`、表 A/B/C 旧数值或“默认完整三表”旧规则继续扩散。

### 文档自查命令

```powershell
rg -n "TB[D]|TO[D]O|以后再[说]|补一[下]|随[便]|先占[位]" README.md CORE_CONTEXT_BRIEF.md CORE_STATUS.md CORE_ROADMAP.md CORE_RESTRUCTURE_PLAN.md CAD_AGENT_STATUS.md
rg -n "Phase A[-][N]|A[-][M]|阶段 5：图库块底[座]|阶段 6：布局底[座]|阶段 7：图纸理解底[座]" CORE_ROADMAP.md CORE_RESTRUCTURE_PLAN.md CAD_AGENT_STATUS.md README.md
rg -n "run_cad_validation|run_blank_shell_pipeline|CORE_CONTEXT_BRIEF" README.md CORE_CONTEXT_BRIEF.md CORE_RESTRUCTURE_PLAN.md CAD_AGENT_RULES.md CAD_AGENT_STATUS.md
rg -n "21/29|72%|48\\.85%|50\\.52%|39\\.53%|展示就绪度.*0%|最高已证 \\*\\*L3|下一步计划" README.md CORE_CONTEXT_BRIEF.md CORE_STATUS.md CAD_AGENT_STATUS.md docs/planning/任务清单.md
rg -n "next=.*或|或 `REST-PROD|唯一.*next|第二套.*计划" CORE_CONTEXT_BRIEF.md CORE_RESTRUCTURE_PLAN.md docs/planning/任务清单.md docs/README.md docs/handoffs/README.md
```

### 固定非 CAD 回归命令

```powershell
& $py -m unittest discover -s tests
& $py scripts\self_check.py
& $py scripts\render_preview.py --check
& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
& $py scripts\run_blank_shell_pipeline.py examples\workflows\blank_shell_layout_loop.json --output-dir output\test_artifacts\blank_shell_pipeline\manual
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\blank_shell_manual
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\manual-no-cad
```

---


## 状态同步要求

完成或调整本 Phase 后，同步：

- `CORE_RESTRUCTURE_PLAN.md`
- `CORE_CONTEXT_BRIEF.md`
- `CORE_STATUS.md`
- `CAD_AGENT_STATUS.md`
- `CAD_AGENT_CHANGELOG.md`

只有出现失败、回归、CAD 环境问题或验证教训时，才同步 `CAD_AGENT_ISSUES.md`。
