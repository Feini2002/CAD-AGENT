# STRUCT-MERGE-01 Drawing Policy 合并小包

日期：2026-05-28

## 1. 范围

本包执行 `STRUCT-MERGE-PREP-01` 候选 C01：把 `core/composition_engine/drawing_policy.py` 的 composition 绘图策略合并到唯一调用方 `core/composition_engine/templates.py`。

本包不运行真实 CAD，不写 DWG，不修改 registry，不改变表 C。

## 2. 变更

| 类型 | 文件 | 说明 |
| --- | --- | --- |
| 修改 | `core/composition_engine/templates.py` | 内联 `resolve_composition_object_drawing_flags()` 与默认策略常量，并从 `__all__` 导出 |
| 删除 | `core/composition_engine/drawing_policy.py` | 删除仅 21 行的内部细节文件 |
| 修改 | `tests/core/test_composition_catalog.py` | 测试改从 `templates.py` 导入策略，并断言旧文件不再存在 |

## 3. TDD 证据

| 阶段 | 命令 | 结果 |
| --- | --- | --- |
| RED | `python -m unittest tests.core.test_composition_catalog` | 失败：`drawing_policy.py` 仍存在 |
| GREEN | `python -m unittest tests.core.test_composition_catalog` | 5 tests OK |
| 扩展 focused | `python -m unittest tests.core.test_composition_catalog tests.core.test_composition_engine tests.core.test_composition_cad_check tests.core.test_composition_cad_case_ids tests.core.test_run_composition_cad_check` | 15 tests OK |

## 4. 加固 / BUG 筛查

| 检查 | 结果 |
| --- | --- |
| 旧 import 扫描 | `rg "from core\.composition_engine\.drawing_policy|import core\.composition_engine\.drawing_policy" core tests scripts` 无结果 |
| 直接 import 检查 | `from core.composition_engine.templates import resolve_composition_object_drawing_flags` 通过 |
| repo audit | `scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings` 通过，0 findings |
| 全量 unittest | 首轮发现 RBLOCK-07 两个失败；修复后 864 tests OK |
| dev volume audit | 当前工作树仍触发 `large_changed_file_count`、`large_untracked_file_count`、`large_single_file_delta`，属于本轮之前累积的大工作树收口风险；本包未扩大 Python 大文件 |

## 5. 结论

`drawing_policy.py` 是 C01 高确定性候选：只承载 composition 内部固定策略，没有独立测试价值，合并后减少一次阅读跳转。合并后的行为仍由 composition catalog / composition CAD focused tests 覆盖。

本包没有发现新的 composition 行为 bug；全量 BUG 筛查发现并修复了一个既有 RBLOCK-07 回归：`block.insert_block_alpha.matrix` 已升级为 `showcase` 后，`apply_block_matrix_registry_binding()` 没有把 `showcase` 当作可绑定的已验证类行，导致 dry-run matrix sync 只 applied 4/5。修复后 `showcase` 行只追加 matrix binding 来源，不覆盖既有 evidence。

剩余风险是工作树总体变更量已经较大，后续结构小包应继续保持 1-3 组候选以内。
