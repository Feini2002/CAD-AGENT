# Phase Y Blank Shell Hardening Plan

状态：由 `CORE_RESTRUCTURE_PLAN.md` 拆分而来
最后同步：2026-05-26（`Y-MULTI-CANDIDATE` / `Y-MC-05` 收口）

> 本文是 Phase Y 辅助执行剧本，不是独立 PlanMD。执行顺序、优先级和退出标准以根目录 `CORE_RESTRUCTURE_PLAN.md` 为准；多候选 **Alpha 硬化** 的不可声称边界见 [`docs/verification/blank_shell_multi_candidate_boundaries.md`](../../verification/blank_shell_multi_candidate_boundaries.md)。

## Phase Y：空壳布局硬化与真实样本扩展

目标：把当前“能跑通的 blank-shell pipeline”推进成更可靠的非 CAD 布局实验台，重点补多候选、失败基准、复杂几何和真实样本，而不是继续堆单一 happy path。

### 当前前置事实（2026-05-26）

- Phase P-V 端到端非 CAD 链路已完成。
- **`Y-MULTI-CANDIDATE`（`Y-MC-01`～`05`）已收口**：`candidate_sets.json`、`comparison_detail`、blank-shell **8-case** benchmark（含 2 个 structured blocked failure）。
- 当前 pipeline 仍会 **择优选出一条主路线** 生成 CAD_PLAN；多候选用于 **解释、比较与 benchmark**，不是成熟多方案自动决策产品。
- 几何底座仍以 bbox 与简单正交多边形为主；benchmark 证据为 non-CAD only。

### `Y-MULTI-CANDIDATE` 与 Phase Y 映射

| Phase Y 意图 | `Y-MC` 落地 | 状态 |
| --- | --- | --- |
| 多 circulation / zone / placement 候选可追溯 | `Y-MC-01` `candidate_sets.json` | **完成** |
| 候选比较摘要（覆盖率、失败、通道、排序） | `Y-MC-02` `comparison_detail` | **完成** |
| benchmark 机器断言 | `Y-MC-03` | **完成** |
| 近真实 + failure shell 样本 | `Y-MC-04`（8 cases） | **完成** |
| 文档与不可声称边界 | `Y-MC-05` + 本文 | **完成** |
| 成熟几何库（如 shapely） | — | 长期候选 |
| 自动 DWG/PDF 读壳 | — | 长期候选 |
| 大规模真实项目回归库 | — | 长期候选 |

### 文件范围（历史 + 已修改）

- `core/workflows/blank_shell_pipeline.py` — `build_blank_shell_candidate_sets`、`comparison` metrics
- `core/proposal_engine/proposal_comparison.py` — `build_blank_shell_comparison_detail`
- `core/proposal_engine/design_proposal.py` — `comparison_detail`
- `core/benchmarks/runner.py` — 多候选 actual / expected 比较器
- `examples/benchmarks/blank_shell_core_benchmark.json` — 8 cases
- `examples/shell_models/blank_shell_corridor_riser_block_shell.json` 等
- `tests/core/test_blank_shell_pipeline.py`、`test_proposal_multi_candidate.py`、`test_benchmarks.py`

### 验证命令（收口复验）

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_blank_shell_pipeline tests.core.test_proposal_multi_candidate tests.core.test_benchmarks -q
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\y_mc_05
```

### 退出标准（Alpha 硬化 — 已满足部分）

- [x] pipeline 输出多个可解释候选（`candidate_sets` + `comparison_detail`）。
- [x] benchmark 同时覆盖 pass 与 failure case（8 cases；2× blocked）。
- [x] failure 结构化归类（`insufficient_space` 等 + `layout_expectation`）。
- [x] 文档区分 non-CAD 布局、Phase W CAD baseline、非自动设计大脑（见边界文档）。
- [ ] 复杂几何库决策与落地（长期候选）。
- [ ] 自动读图闭环（长期候选）。
- [ ] 真实项目大样本库（长期候选）。

---

## 状态同步要求

完成或调整本 Phase 后，同步：

- `CORE_RESTRUCTURE_PLAN.md`
- `CORE_CONTEXT_BRIEF.md`
- `CORE_STATUS.md`
- `docs/status/current.md`
- `docs/status/changelog.md`
- `docs/verification/blank_shell_multi_candidate_boundaries.md`（多候选边界）

只有出现失败、回归、CAD 环境问题或验证教训时，才同步 `docs/status/issues.md`。
