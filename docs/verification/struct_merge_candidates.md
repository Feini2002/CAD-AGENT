# STRUCT-MERGE-PREP-01 候选清单

日期：2026-05-28

本候选表来自 `STRUCT-AUDIT-01` 的 `struct_audit_report.json` 与人工抽查。表中“应合并”表示进入后续 `STRUCT-MERGE-xx` 小包候选，不代表本轮已经改代码。

## 1. 总览

| 类别 | 数量 | 说明 |
| --- | ---: | --- |
| 应合并 | 1 | 小而内部、合并后更好读 |
| 应拆分 / 抽公共层 | 5 | 大文件、私有 helper 跨模块、编排层变厚 |
| 应保留 | 6 | CLI / safety / evidence / algorithm 边界 |
| 观察 / 延后 | 4 | 需要引用审计或先补测试 |

## 2. 候选表

| ID | 判定 | 文件 / 组 | 原因 | 建议动作 | 验证入口 |
| --- | --- | --- | --- | --- | --- |
| C01 | 已合并（STRUCT-MERGE-01） | `core/composition_engine/drawing_policy.py` → `core/composition_engine/templates.py` | 21 行，只被 `templates.py` 和测试使用；策略固定为 composition 内部细节 | 已合并，旧文件已删除 | `tests/core/test_composition_catalog.py` + composition focused tests + repo audit |
| C02 | 应保留并先补测试 | `core/verification/composition_cad_registry.py`、`scripts/run_composition_cad_registry.py` | `V-PROOF-43` 关键入口，但静态审计未发现测试入口 | 先补 no-CAD contract test / monkeypatch test，再决定是否拆 runner | 新增 `tests/core/test_composition_cad_registry.py` + repo audit |
| C03 | 应拆分 / 抽公共层 | `core/verification/visual_cad_smoke.py`、`core/verification/visual_room_plan_scene.py`、`core/verification/visual_room_plan_smoke.py` | `visual_room_plan_scene.py` 跨模块 import `_arc/_line/_rect` 等私有 helper；`visual_cad_smoke.py` 已 493 行 | 抽 `visual_primitives.py` 或 `visual_draw_helpers.py`，保留两个 VCAD runner | `tests/core/test_visual_cad_smoke.py`、`tests/core/test_visual_room_plan_smoke.py`、repo audit |
| C04 | 应拆分 | `core/verification/complex_cad_smoke.py` | 493 行，真实 CAD smoke 场景数据、绘制、报告容易继续堆在一起 | 下次触碰时拆出 scene spec / report builder；不与 VCAD 合并 | `tests/core/test_complex_cad_smoke.py` + fake-driver focused test |
| C05 | 应拆分 | `core/benchmarks/runner.py` | 500 行，刚好顶到 repo audit 阈值；fan-in 24，属于共享基座 | 保留 public API，拆 loader / execution / report helper | `tests/core/test_benchmarks.py`、benchmark 相关 focused tests、repo audit |
| C06 | 应拆分 | `core/verification/cad_validation_runner.py` | 472 行，真实 CAD validation 编排层；继续加逻辑会靠近阈值 | 新逻辑只进 `cad_validation_runner_report.py` / gates / helper，不回堆主 runner | `tests/core/test_cad_validation_runner.py`、`test_cad_validation_geometry_gate.py`、repo audit |
| C07 | 应拆分 | `core/verification/cad_capability_probe.py` | 477 行，真实 AutoCAD probe，风险高且接近阈值 | 下次新增 probe 时拆 readback / report / capability rows helper | `tests/core/test_cad_capability_probe.py` + fake-driver focused test |
| C08 | 应保留 | `scripts/*.py` 薄 CLI wrappers，尤其 `self_check.py`、`dry_run_plan.py`、`run_cad_validation.py`、`run_*_cad_smoke.py` | 虽小且多无静态测试入口，但它们是用户 / 文档 / AGENTS 的一键命令 | 不为减少文件数合并；可补 CLI smoke tests 或统一 helper | 相关 CLI focused tests + `rg` 文档引用 |
| C09 | 观察 / 延后 | `drivers/autocad_com.py`、`drivers/dxf_writer.py`、`drivers/zwcad_com.py` | 7 行兼容包装，有 `test_core_restructure` 覆盖；可能仍被旧脚本导入 | 先做外部引用审计，再决定 deprecate 或保留 | `rg "from drivers|import drivers"` + `tests/core/test_core_restructure.py` |
| C10 | 应保留 | `core/schemas/validator.py`、`core/path_safety.py`、`core/verification/evidence_contract.py` | 高 fan-in 基座：68 / 55 / 63 importers | 不合并；只允许小修 + focused tests | schema / path safety / evidence focused tests + repo audit |
| C11 | 应保留 | `core/layout_engine/scoring.py`、`collision.py`、`clearance.py`、`circulation.py` | 文件小但各自是独立 layout 检查语义，间接测试覆盖高 | 不因小文件合并回 `basic_layout.py` | `tests/core/test_layout_engine.py`、`test_geometry_candidates.py` |
| C12 | 应保留 | `core/cad_io/autocad_com.py`、`core/cad_io/autocad_block_alpha.py`、`core/cad_io/preview_write_guard_mixin.py` | CAD COM / block / preview safety 边界清晰，不能为了少文件数混合 | 保持边界；新增 CAD 行为另开 focused tests | `tests/core/test_autocad_com_driver.py`、`test_autocad_write_guard.py` |
| C13 | 观察 / 抽模板 | `scripts/run_office_alpha_boundary_contract.py`、`scripts/run_restaurant_alpha_boundary_contract.py`、对应 beta / p3 CLI | CLI 结构重复，但命令名有交接价值 | 保留命令名，若继续增长则抽 shared summary writer，不合并入口文件 | `tests/core/test_office_prod_*`、`tests/core/test_rest_prod_*` |
| C14 | 应保留 | `core/agents/office_*_boundary.py`、`core/agents/restaurant_*_boundary.py` | 场景 contract 有重复形态，但业务边界不同；合并会让错误更隐蔽 | 第三个场景出现相同模板时再抽 `scene_contract_helpers.py` | office / restaurant focused tests |
| C15 | 应保留 | `core/verification/cad_validation_runner_report.py`、`core/verification/cad_validation_gates.py` | 已经是从 runner 拆出的报告 / gate helper | 不回并；作为 C06 后续拆分承接点 | cad validation focused tests |
| C16 | 允许超线例外 | `core/benchmarks/runner.py` | 当前 500 行但 repo audit 仍 pass；共享 public runner | 本轮不动；下一次新增逻辑必须先拆 | repo audit 阈值门禁 |

## 3. 推荐后续小包顺序

| 小包 | 范围 | 理由 |
| --- | --- | --- |
| `STRUCT-MERGE-01` | C01 | 已完成：`drawing_policy.py` 合并入 `templates.py` |
| `STRUCT-MERGE-02` | C02 | 为 `V-PROOF-43` 补测试入口，先固边界再改 CAD evidence |
| `STRUCT-MERGE-03` | C03 | 解决私有 helper 跨模块和 VCAD 文件膨胀 |
| `STRUCT-SPLIT-01` | C05 或 C06 | 大文件拆分，单包只碰一个 runner |

本表不要求一次性处理所有候选；每次只取 1-3 组，并按规则页的小批门槛验证。
