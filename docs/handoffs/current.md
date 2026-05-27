# 当前交接包窗口

本文件只保留最近活跃结构治理包。完整历史见 `archive/2026-05.md`，全量索引见 `package-index.md`。

## STRUCT-AUDIT-01：全仓 Python 结构审计

1. **本次开发包名**

`STRUCT-AUDIT-01`：全仓 Python 结构审计。

2. **修改文件列表**

| 类型 | 文件 |
| --- | --- |
| 新增 | `docs/verification/struct_audit_01.md` |
| 新增 | `output/validation_runs/struct-audit-01/struct_audit_report.json` |
| 新增 | `output/validation_runs/struct-audit-01/python_inventory.csv` |
| 新增 | `output/validation_runs/struct-audit-01/struct_audit_fragments.md` |
| 修改 | `docs/status/current.md`、`docs/status/changelog.md`、本文 |

3. **关键设计说明**

- 用 AST 做只读结构扫描，覆盖 Python 行数、模块职责、内部 import 图和测试入口近似关系。
- 全量逐文件结果落在机器 JSON / CSV；人工报告只保留总览、风险和后续建议。
- 测试覆盖入口是静态近似，不把 subprocess、字符串路径或动态 import 误报成直接覆盖。

4. **新增/修改测试**

未新增测试；本包是只读结构审计与文档产物。

5. **实际运行的命令和结果**

| 命令 | 结果 |
| --- | --- |
| `rg --files -g '*.py'` | 枚举 Python 文件 |
| 自定义 AST 静态审计脚本（CAD-MCP venv Python） | 505 个 Python 文件、56,247 行、1,523 条内部 import 边、AST 解析错误 0 |

6. **是否运行真实 CAD**

否。

7. **机器可读证据路径**

- `output/validation_runs/struct-audit-01/struct_audit_report.json`
- `output/validation_runs/struct-audit-01/python_inventory.csv`
- `output/validation_runs/struct-audit-01/struct_audit_fragments.md`

8. **结论分类表**

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 全仓 Python 结构审计报告完成；未发现 AST 解析错误；识别 import 图和静态测试入口风险 | `non_cad_only` | 否 |

9. **剩余风险**

- 这是静态结构审计，不能证明运行时覆盖率，也不能证明 CAD 几何准确。
- `core/verification/composition_cad_registry.py` 与 `scripts/run_composition_cad_registry.py` 未发现静态测试入口；推进 `V-PROOF-43` 前建议补 focused no-CAD contract test。
- 多个 verification / CAD runner 接近 500 行维护阈值，后续新增逻辑应避免继续堆大文件。

---

## STRUCT-MERGE-PREP-01：合并规则与候选清单

1. **本次开发包名**

`STRUCT-MERGE-PREP-01`：执行结构治理第 2 / 3 步，制定合并 / 保留规则并生成候选清单。

2. **修改文件列表**

| 类型 | 文件 |
| --- | --- |
| 新增 | `docs/verification/struct_merge_keep_rules.md` |
| 新增 | `docs/verification/struct_merge_candidates.md` |
| 新增 | `output/validation_runs/struct-audit-01/merge_candidate_table.csv` |
| 修改 | `docs/verification/struct_audit_01.md` |
| 修改 | `docs/status/current.md`、`docs/status/changelog.md`、本文 |

3. **关键设计说明**

- 规则页把“小文件合并”和“必须保留的边界”分开，避免为了减少文件数破坏 CLI、CAD safety、evidence contract 或 registry / coverage 入口。
- 候选表按 `应合并`、`应拆分 / 抽公共层`、`应保留`、`观察 / 延后` 分类，而不是直接执行批量移动。
- 首批建议只把 `core/composition_engine/drawing_policy.py` 列为真正合并候选；`composition_cad_registry` 先补测试，VCAD / benchmark / CAD runner 走拆分或保留路线。

4. **新增/修改测试**

未新增测试；本包只产出规则和候选表，不改 Python 行为。

5. **实际运行的命令和结果**

| 命令 | 结果 |
| --- | --- |
| `rg` / AST 审计 JSON 人工复核 | 形成 16 条候选记录 |
| `Select-String` / 文件抽查 | 确认 `drawing_policy` 单一内部使用、`composition_cad_registry` 缺静态测试入口、VCAD 私有 helper 跨模块等依据 |

6. **是否运行真实 CAD**

否。

7. **机器可读证据路径**

- `docs/verification/struct_merge_keep_rules.md`
- `docs/verification/struct_merge_candidates.md`
- `output/validation_runs/struct-audit-01/merge_candidate_table.csv`
- `output/validation_runs/struct-audit-01/struct_audit_report.json`

8. **结论分类表**

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 结构治理第 2 / 3 步完成：规则页 + 候选表已落盘 | `non_cad_only` | 否 |

9. **剩余风险**

- 候选表不是执行结果；任何 `STRUCT-MERGE-xx` 小包仍需 focused tests + repo audit。
- 不得把规则页或候选表当成真实 CAD 几何证明。
- 高风险 CAD runner 只能先拆 helper / 补测试，不能与真实 CAD 补验混在同一个结构包中。

---

## STRUCT-MERGE-01：drawing_policy 合并小包 + BUG 筛查

1. **本次开发包名**

`STRUCT-MERGE-01-DRAWING-POLICY`：执行第 4 步小批合并验证，并完成第 5 步状态 / 交接写回。

2. **修改文件列表**

| 类型 | 文件 |
| --- | --- |
| 修改 | `core/composition_engine/templates.py` |
| 修改 | `core/block_engine/block_matrix_registry.py` |
| 删除 | `core/composition_engine/drawing_policy.py` |
| 修改 | `tests/core/test_composition_catalog.py` |
| 新增 | `docs/verification/struct_merge_01_drawing_policy.md` |
| 新增 | `output/validation_runs/struct-merge-01/struct_merge_01_report.json` |
| 修改 | `docs/verification/struct_merge_candidates.md`、`output/validation_runs/struct-audit-01/merge_candidate_table.csv` |
| 修改 | `docs/status/current.md`、`docs/status/changelog.md`、`docs/status/issues.md`、本文 |

3. **关键设计说明**

- `drawing_policy.py` 只有 21 行，策略固定且只被 composition templates / 测试使用，没有独立运行价值。
- 合并后 `resolve_composition_object_drawing_flags()` 从 `templates.py` 导出，composition behavior 保持 label-free / dimension-free。
- 本包只处理 C01 一个高确定性候选；BUG 筛查另修复 RBLOCK-07 registry binding 对 `showcase` claim_level 的兼容，不触碰 registry JSON / coverage / 真实 CAD。

4. **新增/修改测试**

- 修改 `tests/core/test_composition_catalog.py`：从 `templates.py` 导入策略函数，并断言旧 `drawing_policy.py` 文件不存在。
- 红灯已确认：旧文件存在时 focused test 失败。

5. **实际运行的命令和结果**

| 命令 | 结果 |
| --- | --- |
| `python -m unittest tests.core.test_composition_catalog`（RED） | 失败：`drawing_policy.py` 仍存在 |
| `python -m unittest tests.core.test_composition_catalog`（GREEN） | 5 tests OK |
| `python -m unittest tests.core.test_composition_catalog tests.core.test_composition_engine tests.core.test_composition_cad_check tests.core.test_composition_cad_case_ids tests.core.test_run_composition_cad_check` | 15 tests OK |
| `rg "from core\.composition_engine\.drawing_policy\|import core\.composition_engine\.drawing_policy" core tests scripts` | 无旧 import 残留 |
| `python -m unittest tests.core.test_rblock_07_block_matrix_registry_rows -v` | 9 tests OK；修复前该 focused suite 有 2 failures |
| `python -m unittest discover -s tests` | 864 tests OK |
| `python scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings` | pass，0 findings |
| `python scripts/run_dev_volume_audit.py` | findings：当前工作树整体变更量偏大 |

6. **是否运行真实 CAD**

否。

7. **机器可读证据路径**

- `docs/verification/struct_merge_01_drawing_policy.md`
- `output/validation_runs/struct-merge-01/struct_merge_01_report.json`

8. **结论分类表**

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| C01 高确定性候选已完成小批合并，composition 行为 focused tests 通过 | `non_cad_only` | 否 |
| 未发现旧 `drawing_policy` import 残留，repo audit 0 findings，全量 864 tests OK | `non_cad_only` | 否 |
| RBLOCK-07 showcase claim_level binding 回归已修复 | `non_cad_only` | 否 |

9. **剩余风险**

- 本包不证明 CAD 几何准确，不改变表 C。
- `run_dev_volume_audit.py` 仍提示工作树整体变更量偏大，后续应继续小批收口，避免 handoff/status 文件继续膨胀。

---
