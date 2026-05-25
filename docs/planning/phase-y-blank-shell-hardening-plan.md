# Phase Y Blank Shell Hardening Plan

状态：由 `CORE_RESTRUCTURE_PLAN.md` 拆分而来
最后同步：2026-05-26

> 本文是 Phase Y 辅助执行剧本，不是独立 PlanMD。执行顺序、优先级和退出标准以根目录 `CORE_RESTRUCTURE_PLAN.md` 为准；执行前仍需先读 `AGENTS.md` 与 `CORE_CONTEXT_BRIEF.md`，并遵守 `CODEX_PREVIEW`、不保存、不覆盖、不删除、不改正式图层的 CAD 安全边界。

## Phase Y：空壳布局硬化与真实样本扩展

目标：把当前“能跑通的 blank-shell pipeline”推进成更可靠的非 CAD 布局实验台，重点补多候选、失败基准、复杂几何和真实样本，而不是继续堆单一 happy path。

### 当前前置事实

- Phase P-V 已完成第一条端到端非 CAD 链路。
- 当前 pipeline 实际更像“选出一条主路线并生成一组可落图对象”，不是成熟多方案生成器。
- 当前几何底座以 bbox 和简单正交多边形为主。
- benchmark 已有 4 个场景 case，但真实项目样本和历史趋势不足。

### 文件范围

- 可能修改：`core/workflows/blank_shell_pipeline.py`
- 可能修改：`core/layout_engine/path_generation.py`
- 可能修改：`core/layout_engine/zone_splitter.py`
- 可能修改：`core/layout_engine/placement.py`
- 可能修改：`core/proposal_engine/proposal_comparison.py`
- 可能新增：`examples/workflows/*`
- 可能新增：`examples/shell_models/*`
- 可能新增：`projects/*/expected/*`
- 修改：`tests/core/test_blank_shell_pipeline.py`
- 修改：`tests/core/test_benchmarks.py`

### 执行参考

- Y-01 扩展 pipeline 输出，让多个 circulation candidates 和多个 zone choices 能形成多个 layout candidates，而不是只保留一条主候选。
- Y-02 为每个候选记录失败检查：边界、碰撞、clearance、主通道、no-place-zone、门洞/消防避让。
- Y-03 增加失败 benchmark：输入可运行但空间不足、入口冲突、对象放不下时，应输出 blocked/invalid 原因，不 traceback。
- Y-04 增加至少 2 个更接近真实项目的 shell sample，保留人工标注来源和不确定点。
- Y-05 评估是否引入成熟几何库，例如 `shapely`；若引入，先写决策记录、环境清单和 fallback 策略。
- Y-06 扩展 benchmark summary，记录 case、候选数量、失败原因分布、unverified verification 状态和执行耗时。
- Y-07 更新 `docs/architecture/shell-layout-foundation-design.md` 的“已落地 / 待硬化”映射，不把它写成流水账。

### 验证命令

```powershell
& $py -m unittest tests.core.test_blank_shell_pipeline tests.core.test_blank_shell_pipeline_failures
& $py -m unittest tests.core.test_benchmarks tests.core.test_benchmark_cli
& $py scripts\run_blank_shell_pipeline.py examples\workflows\blank_shell_layout_loop.json --output-dir output\test_artifacts\blank_shell_pipeline\phase-y
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\phase-y
```

### 退出标准

- pipeline 能输出多个可解释候选，或明确说明为什么只能输出一个候选。
- benchmark 同时覆盖 pass case 和 failure case。
- 所有失败都能被结构化归类。
- 文档继续区分“非 CAD 布局可用”、“Phase W baseline 已验证”和“真实项目/任意 CAD_PLAN 仍需补验”。

---


## 状态同步要求

完成或调整本 Phase 后，同步：

- `CORE_RESTRUCTURE_PLAN.md`
- `CORE_CONTEXT_BRIEF.md`
- `CORE_STATUS.md`
- `CAD_AGENT_STATUS.md`
- `CAD_AGENT_CHANGELOG.md`

只有出现失败、回归、CAD 环境问题或验证教训时，才同步 `CAD_AGENT_ISSUES.md`。
