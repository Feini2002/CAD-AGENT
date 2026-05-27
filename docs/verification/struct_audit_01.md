# STRUCT-AUDIT-01 全仓 Python 结构审计报告

日期：2026-05-28

## 1. 范围

本报告执行“全仓库结构审计”步骤：扫描仓库内所有 Python 文件的行数、职责、内部 import 关系和测试覆盖入口。审计只读代码与测试结构，不运行真实 CAD，不写 DWG，不修改 `cad_capability_registry`，也不改变表 C。

机器产物：

| 产物 | 内容 |
| --- | --- |
| `output/validation_runs/struct-audit-01/struct_audit_report.json` | 全量 JSON：逐文件行数、职责、imports、直接/间接测试入口、import 边 |
| `output/validation_runs/struct-audit-01/python_inventory.csv` | 全量 CSV：便于表格筛选的逐文件清单 |
| `output/validation_runs/struct-audit-01/struct_audit_fragments.md` | 本报告用到的机器摘要表 |

## 2. 方法

- 使用 AST 解析所有 `*.py`，跳过 `.git`、缓存目录、虚拟环境、`node_modules` 和 `output`。
- 模块职责优先取模块 docstring 第一行；无 docstring 时取顶层公共函数/类，脚本入口取 `argparse.ArgumentParser(description=...)`。
- 内部 import 解析覆盖 `core`、`scripts`、`tests`、`drivers` 等仓库内模块；脚本中的 `_bootstrap` 兼容导入归并到 `scripts._bootstrap`。
- 测试覆盖入口为静态近似：记录 test 文件直接 import 的模块，并沿内部 import 图计算从测试入口可达的间接模块。它不能识别纯 subprocess、字符串路径或动态 import。

## 3. 总览

| 指标 | 当前值 |
| --- | ---: |
| Python 文件数 | 505 |
| Python 总行数 | 56,247 |
| AST 解析错误 | 0 |
| 内部 import 边 | 1,523 |
| 测试文件 | 185 |
| 脚本文件 | 91 |
| 非测试模块 | 320 |
| 有直接静态测试入口的非测试模块 | 186 |
| 仅间接可达的非测试模块 | 20 |
| 未发现静态测试入口的非测试模块 | 114 |

### 目录责任分布

| area | files | lines | tests | scripts |
| --- | ---: | ---: | ---: | ---: |
| `core` | 226 | 35,228 | 0 | 0 |
| `drivers` | 3 | 21 | 0 | 0 |
| `scripts` | 91 | 4,119 | 0 | 91 |
| `tests` | 185 | 16,879 | 185 | 0 |

结论：仓库主干已经明显收敛到 `core` + `scripts` + `tests`。`drivers` 只剩薄兼容包装；当前没有 Python 文件落在 `agents`、`libraries`、`projects`、`cad_agent` 等目录。

## 4. Import 结构

### 高 fan-in 模块

| path | internal importers | 说明 |
| --- | ---: | --- |
| `tests/bootstrap.py` | 145 | 测试统一入口，符合既有 bootstrap 收敛方向 |
| `scripts/_bootstrap.py` | 93 | 脚本统一入口，是 CLI 稳定性的关键点 |
| `tests/helpers.py` | 84 | 测试工具层，改动会影响大面积测试 |
| `core/schemas/validator.py` | 68 | CAD_PLAN / schema 验证主入口 |
| `core/verification/evidence_contract.py` | 63 | evidence state 和几何证据契约主入口 |
| `core/path_safety.py` | 55 | 路径边界安全主入口 |
| `core/plan_engine/validate_plan.py` | 44 | plan validation 核心门禁 |
| `core/cad_io/autocad_com.py` | 33 | 真实 AutoCAD COM 写入链路关键适配层 |

这些模块不是问题本身，但属于“改动要加倍小心”的共享基座。任何后续修改应优先跑 focused tests，再跑全量或 repo audit。

### 高 fan-out 模块

| path | internal imports | 说明 |
| --- | ---: | --- |
| `core/capabilities/runners.py` | 14 | capability runner 聚合层 |
| `core/workflows/blank_shell_pipeline.py` | 14 | blank-shell pipeline 聚合层 |
| `core/benchmarks/runner.py` | 13 | benchmark suite 聚合层 |
| `core/verification/cad_beta_evidence_rollup.py` | 12 | beta evidence rollup 聚合层 |
| `core/verification/symbol_glyph_cad_smoke.py` | 11 | symbol glyph CAD smoke 聚合层 |
| `core/orchestrator/workflow_dispatch.py` | 10 | workflow dispatch 聚合层 |

这些模块天然是编排层，当前 fan-out 仍可解释；后续如果继续增长，应优先拆“报告组装 / 数据加载 / runner 调度”而不是拆业务语义。

## 5. 行数风险

当前没有文件超过既有 `run_repo_audit.py --max-python-lines 500` 阈值，但已有 6 个文件贴近上限：

| path | lines | 职责 |
| --- | ---: | --- |
| `core/benchmarks/runner.py` | 500 | non-CAD benchmark runner |
| `core/verification/complex_cad_smoke.py` | 493 | mixed-primitive real CAD smoke |
| `core/verification/visual_cad_smoke.py` | 493 | visual CAD smoke |
| `core/verification/capability_registry_writeback.py` | 478 | registry writeback |
| `core/verification/cad_capability_probe.py` | 477 | real CAD capability probe |
| `core/verification/cad_validation_runner.py` | 472 | autonomous CAD validation runner |

建议：下一轮若触碰这些文件，优先保持小补丁；若新增逻辑超过几十行，先考虑拆 helper 或报告构建器。

## 6. 测试覆盖入口

静态覆盖口径显示：320 个非测试模块中，186 个有直接 test import，20 个仅经 import 链间接可达，114 个未发现静态测试入口。

未发现静态测试入口的 114 个模块中：

| 分类 | 数量 | 说明 |
| --- | ---: | --- |
| `scripts` | 86 | 多数是 CLI 包装或一次性 runner，可能通过 subprocess / 文档命令覆盖，静态 import 不会识别 |
| `core` | 28 | 绝大多数是 `__init__.py` / facade；需重点看非 init 模块 |

值得关注的非 init Core 模块：

| path | lines | 原因 |
| --- | ---: | --- |
| `core/plan_engine/dry_run_plan.py` | 33 | 有 `scripts/dry_run_plan.py` 兼容包装，但静态分析未发现直接 test import |
| `core/verification/composition_cad_registry.py` | 104 | 标注为 `V-PROOF-43` 相关，且对应 `scripts/run_composition_cad_registry.py` 也未发现静态测试入口 |

建议：如果下一步推进 `V-PROOF-43-COMPOSITION-CAD-RERUN`，先给 `composition_cad_registry` 和 `run_composition_cad_registry` 补 focused no-CAD contract test，再跑真实 CAD 或 registry 回写。

## 7. 外部依赖形态

静态 import top-level 主要集中在标准库：`pathlib`、`typing`、`json`、`unittest`、`argparse`、`sys`、`datetime`、`dataclasses`。少量可选运行时依赖包括 `PIL`、`pythoncom`、`win32com`、`win32gui`，集中在 CAD / 截图 / COM 相关路径，符合当前 Windows + AutoCAD 工作站定位。

## 8. 结论

STRUCT-AUDIT-01 未发现 Python 语法错误；全仓结构整体仍保持“Core 可复用、scripts 薄入口、tests 密集回归”的形态。当前最值得立刻记住的风险不是目录失控，而是两个点：

1. `core/verification/composition_cad_registry.py` 是后续 `V-PROOF-43` 相关核心模块，但静态审计未发现测试入口。
2. 多个真实 CAD / verification runner 已接近 500 行维护阈值，后续新增逻辑应避免继续把编排、报告和 CAD 操作堆在同一文件。

本报告是结构审计，不构成 CAD 几何准确证明；真实 CAD 能力仍只能按 CAD_PLAN validate、dry-run、`CODEX_PREVIEW`、created handles 回读和 `geometry_verified` 证据判断。

## 9. 后续步骤 2 / 3

本报告之后已补充两份结构治理产物：

| 步骤 | 产物 | 说明 |
| --- | --- | --- |
| 2. 制定合并 / 保留规则 | `docs/verification/struct_merge_keep_rules.md` | 一页维护规则：何时合并、保留、拆分、允许超线例外 |
| 3. 生成候选清单 | `docs/verification/struct_merge_candidates.md` | 候选表：应合并、应保留、应拆分、观察 / 延后 |

机器可筛选版候选表见 `output/validation_runs/struct-audit-01/merge_candidate_table.csv`。
