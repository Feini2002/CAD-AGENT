# Blank-Shell 多候选能力边界（Y-MULTI-CANDIDATE 收口）

最后更新：2026-05-26

> 机器实现以 `core/workflows/blank_shell_pipeline.py`、`core/proposal_engine/proposal_comparison.py`、`examples/benchmarks/blank_shell_core_benchmark.json` 为准。证据词表见 [`evidence_gate_handoff_rules.md`](evidence_gate_handoff_rules.md)。

## 父包 `Y-MULTI-CANDIDATE` 已交付（01–05）

| 小包 | 能力 | 主要 artifact / 入口 |
| --- | --- | --- |
| `Y-MC-01` | 保留 circulation / zone / placement 候选明细 | `candidate_sets.json` |
| `Y-MC-02` | proposal 比较摘要 | `design_proposal.comparison_detail` + `comparison_summary` |
| `Y-MC-03` | benchmark 多候选硬断言 | `blank_shell_core_benchmark.json`（`requires_comparison_detail` 等） |
| `Y-MC-04` | 近真实 / 失败 shell 样本 | 8 cases（6 pass + 2 `blocked_expected_non_cad`） |
| `Y-MC-05` | 本文 + Phase Y 状态同步 | 文档与 benchmark 复验 |

**最新证据（2026-05-26）**：`312 tests OK`；`output/test_artifacts/benchmarks/y_mc_05/`（blank-shell core 8/8 pass）。

## 现在可以声称什么

- blank-shell pipeline 会输出 **多个 circulation 分支** 下的 zone/placement 尝试，并写入 `candidate_sets.json`。
- `create_design_proposal()` 在传入 `candidate_sets` 时生成 **`comparison_detail`**（对象覆盖率、失败检查数、选中分支失败分布、通道连续性标签、排序原因）。
- **`blank_shell_core_benchmark.json`** 对 pass case 断言候选数、覆盖率等；对 failure case 断言 `blocked_expected_non_cad` 且 **`cad_plan_count == 0`**（禁止静默少放对象 pass）。
- 近真实样本包括 **狭长主通道**、**障碍/台阶避让**；失败样本包括 **过小房间**、**通道障碍阻断主路径**。

## 不能声称什么（必须继续遵守）

- **不是**完整自动设计大脑：不会自动在真实项目中选出最终方案，也不替代设计师决策。
- **不是**真实 CAD 几何准确：blank-shell benchmark 全部为 **`benchmark_pass_non_cad`** / **`blocked_expected_non_cad`**；`readback_geometry_verified_count` 必须为 **0**。
- **不是**任意 DWG 自动读壳：仍依赖人工 `SHELL_MODEL` JSON；自动 DWG/PDF 识别未闭环。
- **不是**用户确认后的多方案交互产品：`needs_confirmation` 仍可能为 true；无完整 BETA-PROPOSAL 确认流。
- 未选中 circulation 分支上的 placement 失败 **仅作说明**，除非选中分支或 layout 检查失败，否则不单独阻塞 pipeline（见 `Y-MC-02`）。
- 不能把 `comparison_summary` 或截图当成 `geometry_verified`。

## Benchmark 契约摘要（`blank_shell_core_benchmark.json`）

| 汇总 | 值 |
| --- | --- |
| `case_count` | 8 |
| `benchmark_pass_non_cad_count` | 6 |
| `blocked_expected_non_cad_count` | 2 |
| `non_cad_only` | true |

Pass case 典型断言：`requires_comparison_detail`、`candidate_count >= 2`、`zone_placement_candidate_count >= 2`、对象覆盖率下限（按 case）。

Failure case 典型断言：`pipeline_status=blocked`、`maximums.cad_plan_count=0`、`contains_blocked_reason` 子串、`failure_category`。

## 与 Phase Y 的关系

`Y-MULTI-CANDIDATE` 完成了 Phase Y 计划中 **多候选 artifact、失败 benchmark、比较摘要** 的 Alpha 硬化子集；Phase Y 其余项（复杂几何库、自动读图、真实项目大样本库）仍在 `CORE_RESTRUCTURE_PLAN.md` 后置 Backlog，不在本父包范围。

## 下一主线（PlanMD）

**`X-SCENE-ALPHA`** 父包已收口（2026-05-26）。多候选硬化与 Scene Alpha 并存；Scene Agent 仍不得复制 Core 算法。
