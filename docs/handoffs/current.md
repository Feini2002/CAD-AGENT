# 当前交接包窗口

## VCAD-ROUND12-VISUAL-FIRST-SOFA

1. **包名**：`VCAD-ROUND12-VISUAL-FIRST-SOFA`
2. **修改文件列表**：`agents/pipeline/*`；`core/schemas/visual_parts.schema.json`；`core/drawing/part_primitives.py`；`core/verification/training_geometry_audit.py`；`core/training/learning_promotion.py`；`scripts/run_training_round_gate.py`；`projects/residential_sofa_2seat_20260528/**`；相关 tests 与文档治理文件。
3. **验证命令**：81 个相关 tests OK；`scripts/run_doc_governance_audit.py --fail-on-findings` pass；`scripts/run_training_round_gate.py --stage delivery --fail-on-blocked` pass。
4. **证据路径**：`projects/residential_sofa_2seat_20260528/runs/round12_preview.png`；`round12_execution_summary.json`；`round12_geometry_audit.json`；`round12_agent_review.json`；`round12_style_compare.md`；`expected/style_target_reference_crop.png`。
5. **风险边界**：训练案例待用户目视验收；不写 registry、不改变表 C；截图是视觉辅助，几何证据看 created handles 和 audit。
6. **真实 CAD**：是；只写 `CODEX_PREVIEW`，56 preview handles，7 个声明部件均有 handle 映射，未保存 DWG。
7. **输出**：Visual-First 多 Agent gate、visual_parts schema、学习晋升 gate、round12 真实 CAD 证据链。
8. **结论分类**：训练案例 round12 delivery gate pass；`feedback.md` 状态为 `待你验收`。
9. **后续接手**：用户若 fail，按 `round12_agent_review.json` + 新反馈进入 Repair；若 pass，再沉淀少量规则到 `agents/residential/rules.md`。

---

## TABLE-C-FINAL-GAP：表 C 末 4 行收口

1. **包名**：`TABLE-C-FINAL-GAP`
2. **修改文件列表**：`core/execution/intent_extended_execute.py`；`execute_plan.py`；`autocad_com.py`；`fake_cad_driver.py`；`intent_lab_manifest.json` + 3×intent_lab plan；`scripts/run_tablec_final_gap_cad.py`、`build_tablec_final_gap_writeback.py`；registry writeback 4 行；`docs/status/changelog.md`。
3. **关键设计说明**：`delete_object` 在 `CODEX_PREVIEW` 上 bootstrap 矩形后 scoped delete；`verification_no_cad_report` 用 no-CAD API 报告 + `draw_test_cabinet` 真实 CAD 镜像升 showcase。
4. **真实 CAD**：是；只写 `CODEX_PREVIEW`，未保存 DWG。
5. **证据**：`output/validation_runs/tablec-final-gap-20260528-cad/`；writeback `writeback_apply.json`（4/4 applied）。
6. **表 C**：**98.42%→99.68%**（316/317）；`negative.cad_plan.real_cad_guard` 仍 smoke。
7. **风险**：全库 `evidence_audit` 仍有 **99** 行旧债 fail；全量 gate `writeback_allowed=false`，后续 writeback 须先还债或分批审计。

---

## CORE-PLATFORM-CLOSEOUT：Core 平台开发收尾

1. **包名**：`CORE-PLATFORM-CLOSEOUT`
2. **修改文件列表**：`registry_claim_contract.py`；`run_core_platform_gate.py`；`core_platform_completion_gate.md`；`docs/planning/archive/core-platform-closed.md`；对齐 15 项 registry 契约测试；更新 `CORE_STATUS.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_RESTRUCTURE_PLAN.md`、`README.md`、`docs/status/*`。
3. **关键设计说明**：**Core 100%** = 三轨收口 + 969 tests + doc governance + coverage 可复跑；**禁止**与表 C / 施工图能力混称。后续默认走 PlanMD 后置 Backlog 或表 C，不再开 Core 施工包。
4. **新增/修改测试**：`test_capability_coverage`、`test_planmd_governance`、`test_symbol_08` 等对齐 showcase-first registry；全量 **969** tests OK。
5. **实际运行的命令和结果**：`scripts/run_core_platform_gate.py` → `status=pass`；`run_doc_governance_audit.py` → pass；`python -m unittest discover -s tests` → 969 OK。
6. **是否运行真实 CAD**：否（本包为平台收尾，非表 C 扩样）。
7. **机器可读证据路径**：`output/validation_runs/core-platform-gate/core_platform_gate_report.json`；表 C 快照 `output/validation_runs/capability-lab/cad_capability_coverage.json`（headline **62.78%**，仅作并列参考）。
8. **结论分类表**：

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Core 平台工程底座 100% 收口 | platform gate / unittest | 否 |
| 三轨 45/52/29 已 done | planning archive 索引 | 否 |
| 表 C 主指标仍为 62.78% | coverage JSON | 否（本包未改几何证明） |

9. **剩余风险**：表 C 旧 evidence audit 债（约 72 fail）仍须另包；Agent 约 93%；公司块库 / 正式图层 / 自动读图不在 Core 收口范围内。

10. **能力登记表**：本包不新增 registry 行。
11. **CAD 证明覆盖率**：未以本包为目标；当前机器值见 coverage JSON。
12. **展示等级 Ladder**：最高已证仍为 L4；本包不提升 Ladder。

---

## DOC-FINISH-ARCH-01：完工后文档架构瘦身

1. **包名**：`DOC-FINISH-ARCH-01-FINISHED-ARCHITECTURE-SLIM`
2. **修改文件列表**：瘦身 `CORE_RESTRUCTURE_PLAN.md`、`docs/planning/任务清单.md`、`CORE_STATUS.md`、`docs/status/current.md`；新增 `docs/planning/archive/*`；新增历史快照 `docs/history/snapshots/finished-architecture-2026-05-28/`；更新 doc governance、handoff index、changelog、issues 和入口 README。
3. **关键设计说明**：活跃入口只保留规则、口令、路由、当前表 C、风险和证据入口；done 包明细迁入 archive/history。新增 active doc size budget，防止 PlanMD、任务清单、Core Status、current status 重新长成施工期明细页；handoff index 指向 `current.md` 时必须能在当前窗口找到对应包名。
4. **新增/修改测试**：新增 `check_active_doc_size_budgets()` 行数预算测试；新增 handoff index 当前窗口一致性测试。
5. **实际运行的命令和结果**：`python -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v`：25 tests OK；`scripts/run_doc_governance_audit.py --fail-on-findings`：`status=pass`、0 findings；`scripts/run_capability_coverage.py --output output/validation_runs/capability-lab/cad_capability_coverage.json`：`status=pass`、表 C 主指标 9.15%；全量 `python -m unittest discover -s tests` 首轮在沙箱内因系统临时目录权限报 2 个 `PermissionError`，按权限规则提权复跑后 **969 tests OK**。
6. **是否运行真实 CAD**：否。
7. **机器可读证据路径**：`docs/history/snapshots/finished-architecture-2026-05-28/`、`docs/planning/archive/`；本包不新增 `output/validation_runs/**` CAD 证据。
8. **结论分类表**：

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 活跃文档控制面已瘦身 | doc governance / Markdown audit | 否 |
| done 明细已迁入 archive/history | history snapshot / planning archive | 否 |
| 表 C 机器值未改变 | existing coverage JSON | 否 |

9. **剩余风险**：本包不清理旧 `docs/verification/*.md` 路径和历史 changelog 大文件；这些仍是后续可选治理包。旧 verified/showcase 证据债仍需通过 table C hard gate 单独补齐。

---

## CAD-EVIDENCE-01-HARD-AUDIT-VISUAL-GATE

1. **包名**：`CAD-EVIDENCE-01-HARD-AUDIT-VISUAL-GATE`
2. **修改文件列表**：新增 `core/verification/capability_evidence_audit.py`、`core/verification/visual_cad_review.py`、`core/verification/table_c_evidence_gate.py`、`scripts/run_capability_evidence_audit.py`、`scripts/run_visual_cad_review.py`、`scripts/run_table_c_evidence_gate.py`、`docs/verification/table_c_evidence_gate.md`、`tests/core/test_table_c_evidence_gate.py`；修改 `core/verification/capability_coverage.py`、`scripts/run_capability_coverage.py` 与状态 / 交接文档。
3. **关键设计说明**：表 C writeback 前必须先过两道硬门：`verified/showcase` 证据报告硬审计，以及截图视觉复盘。截图失败或视觉复盘失败时 `writeback_allowed=false`；截图仍只是 `visual_aid_only`，不能替代 created handles readback。
4. **新增/修改测试**：`tests/core/test_table_c_evidence_gate.py` 覆盖有效 readback、缺失报告、伪 `geometry_verified`、截图缺失、visual fail 阻止 gate、coverage 强制 evidence audit。
5. **实际运行的命令和结果**：focused `tests.core.test_doc_governance` + `tests.core.test_capability_coverage` + `tests.core.test_table_c_evidence_gate` 共 25 tests OK；`run_doc_governance_audit.py` 0 findings；现有 registry 硬审计实际为 fail（131 audited，59 pass，72 fail），总 gate 因 hard audit fail + visual missing 阻止 writeback；合成通过样例 gate `writeback_allowed=true`。
6. **是否运行真实 CAD**：否。
7. **机器可读证据路径**：`output/validation_runs/table-c-evidence-gate/evidence_audit_report.json`、`output/validation_runs/table-c-evidence-gate/table_c_evidence_gate_report.json`、`output/validation_runs/table-c-evidence-gate-visual-cli/visual_review_report.json`、`output/validation_runs/table-c-evidence-gate-cli-pass/table_c_evidence_gate_report.json`、`output/test_artifacts/table_c_evidence_gate/`。
8. **结论分类表**：

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 表 C hard audit / visual gate 入口已建立 | `non_cad_only` / unit tests | 否 |
| 当前历史 registry 未通过新 hard audit | `evidence_contract_failed` / `report_path_missing` | 否 |
| visual review 失败会阻止 writeback | `visual_review_failed` gate | 否 |

9. **剩余风险**：旧 `verified/showcase` 证据存在历史债，首次硬审计 72 行失败；本包不自动降级 registry、不改变表 C，后续需单独补齐或迁移旧证据格式。新表 C 推进包必须在 writeback 前提供真实 CAD readback + visual review pass。

---

## V-PROOF-73-CROSS-MACHINE

1. **包名**：`V-PROOF-73-CROSS-MACHINE`（PROJ-03）
2. **产物**：`cross_machine_proof.py`、`run_vproof_73_cross_machine_sync.py`、`vproof_73_cross_machine.md`、`cross_machine_playbook_manifest.json`
3. **证据**：`output/validation_runs/vproof-73-cross-machine/cross_machine_report.json`（no-CAD 4/4；coverage delta 0）
4. **registry**：2 行 `project.cross_machine.*` smoke；2/2 writeback
5. **测试**：`test_vproof_73_cross_machine.py` 7/7 OK
6. **表 C**：headline **约 9.15%**（317 行；smoke 不计证明率）
7. **§3**：**45/45 能力证明轨已收口**
8. **结论分类表**：

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 换机 playbook + coverage baseline 复算入口已建立 | `benchmark_pass_non_cad` | 否 |
| 2 行 `project.cross_machine.*` registry smoke 回写完成 | `smoke` / `benchmark_pass_non_cad` | 否 |

9. **剩余风险**：本包未执行真实 AutoCAD 换机落图；真实 CAD 会话、`run_cad_validation` 全量与 CAD-MCP 落图仍是人工换机 gate。

10. **能力登记表（registry）**：`examples/capability_proof/cad_capability_registry.json`；触及行如下。

| `capability_id` | `claim_level` | `ladder_level` | `evidence.report_path` |
| --- | --- | --- | --- |
| `project.cross_machine.*` | smoke | L0 | `output/validation_runs/vproof-73-cross-machine/cross_machine_report.json` |

11. **CAD 证明覆盖率**：本包 coverage delta 0；最新机器口径见 `output/validation_runs/capability-lab/cad_capability_coverage.json`。
12. **展示等级 Ladder**：本包不提升对外 Ladder 声称；最高已证仍为 L4。

**user_gate（换机人工，未在本包执行）**：AutoCAD 会话、`run_cad_validation` 全量、CAD-MCP 落图 → 见 `docs/onboarding/migration-checklist.md`

---

历史见 `archive/2026-05.md`。
