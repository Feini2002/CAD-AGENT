# Cursor 开发包交付交接包（汇总）

最后更新：2026-05-26  
维护者：Cursor Agent 会话  
用途：供 Codex 或其它 agent **按开发包**做高智力校验、审计与换机接手。

> 本文是**唯一按包汇总的交接入口**。机器可读证据在 `output/validation_runs/`；简版流水在根目录 `CAD_AGENT_CHANGELOG.md`。

---

## 目录

| 序号 | 开发包 | 状态 | 真实 CAD |
| --- | --- | --- | --- |
| 0 | [会话探针：CAD-MCP + 截图自检](#0-会话探针cad-mcp--截图自检无代码变更) | 只读核查 | 未执行仓库脚本 |
| 1 | [R-CAD-VIEW-CAPTURE](#1-r-cad-view-capture) | baseline 完成 | 是 |
| 2 | [R-CAD-CONTRACT](#2-r-cad-contract) | baseline 完成 | 是 |
| 3 | [R-BLOCK-METADATA](#3-r-block-metadata) | baseline 完成 | 否 |
| 4 | [R-BLOCK-PLAN](#4-r-block-plan) | baseline 完成 | 否 |
| 5 | [R-BLOCK-CAD-01](#5-r-block-cad-01) | 完成 | 否 |
| 6 | [R-BLOCK-CAD-02](#6-r-block-cad-02) | 完成 | 否 |
| 7 | [R-BLOCK-CAD-03](#7-r-block-cad-03) | 完成 | 否 |
| 8 | [R-BLOCK-CAD-04](#8-r-block-cad-04) | 完成 | 否（no-CAD 实跑） |
| 9 | [R-BLOCK-CAD-05](#9-r-block-cad-05) | 完成 | **是** |
| audit | [Codex 深度全量安全复盘](#codex-深度全量安全复盘非-planmd-开发包) | 审计完成 | 否 |
| maintenance-4-7 | [Codex 维护 4-7 包](#codex-维护-4-7-包结构整理路径公共化schema-registry文档主从治理) | 完成 | 否 |
| — | [当前交接说明](#当前交接说明) | 只引用 PlanMD | — |

---

## 交接包标准模板（每包 9 项）

1. 本次开发包名  
2. 修改文件列表  
3. 关键设计说明  
4. 新增/修改测试  
5. 实际运行的命令和结果  
6. 是否运行真实 CAD（**必须**写「是」或「否」）  
7. 机器可读证据路径（见下表）  
8. **结论分类表**（**必须**区分 non-CAD 与 `geometry_verified`）  
9. 剩余风险（未做 CAD 时须写明几何未验证）

**Evidence gate 必读**：[`docs/verification/evidence_gate_handoff_rules.md`](../verification/evidence_gate_handoff_rules.md)（R4-05）；词表见 [`evidence_state_vocabulary.md`](../verification/evidence_state_vocabulary.md)。

### 第 7 项：证据路径（按运行类型）

| 运行类型 | 路径示例 |
| --- | --- |
| `--no-cad` validation | `output/validation_runs/<包名>-no-cad/report.json`（核对 `evidence_summary.non_cad_only`） |
| 全量 CAD validation | 上列 + `readback_report.json`、步骤子报告、窗口截图 |
| Benchmark suite | `output/test_artifacts/benchmarks/<run>/benchmark_summary.json` |
| 受控 block alpha CAD | `output/validation_runs/r-block-alpha-cad/block_alpha_report.json` |

### 第 8 项：结论分类表（必填格式）

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| （本包完成了什么） | `non_cad_only` / `benchmark_pass_non_cad` / `readback_geometry_verified` 等 | **是** 或 **否** |

禁止：仅用「测试通过」「suite pass」代替证据类型；禁止把截图写成几何已验证。

---

## 0. 会话探针：CAD-MCP + 截图自检（无代码变更）

**日期**：2026-05-26（Cursor 会话首轮）  
**性质**：环境核查，**未改仓库代码**。

### 1. 开发包名

无（非 PlanMD 开发包）；会话目标为确认 Cursor 是否具备 CAD-MCP 与截图自检能力。

### 2. 修改文件列表

无。

### 3. 关键设计说明

- 核查 `C:\Users\123235\.cursor\mcp.json`：`cad-mcp` 已注册，入口为 `.cursor\mcp\CAD-MCP\.venv` + `server.py`。
- 当前会话 MCP 工具目录 `mcps/user-cad-mcp` 约 11 个绘图工具可用。
- 仓库内 `scripts/self_check.py`、`scripts/render_preview.py --check` 在本机通过；检测到 AutoCAD 2026 窗口。

### 4. 新增/修改测试

无。

### 5. 实际运行的命令和结果

```powershell
$py = "C:\Users\123235\.cursor\mcp\CAD-MCP\.venv\Scripts\python.exe"
cd "D:\工作文件\CAD-AGENT"
& $py scripts\self_check.py          # status: pass
& $py scripts\render_preview.py --check   # status: ready, autocad_window ready
```

### 6. 是否运行真实 CAD

未运行 `run_cad_validation.py` 或落图；仅环境探针与 `--check`。

### 7. CAD 证据路径

无（无 `output/validation_runs` 本轮目录）。

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| MCP 已配置、截图依赖就绪 | 环境 non-CAD 探针 |
| 几何准确 | **未声称** |

### 9. 剩余风险

- Cursor MCP 路径与文档中的 `\.codex\mcp\CAD-MCP` 可能并存，执行脚本时需以本机 `mcp.json` 为准。

---

## 1. R-CAD-VIEW-CAPTURE

**日期**：2026-05-26  
**PlanMD 顺序**：开发包 #5（先于 CONTRACT 实现，同日完成）

### 1. 开发包名

`R-CAD-VIEW-CAPTURE` — AutoCAD 窗口级 / 视口级视觉辅助截图，避免 Codex 全屏遮挡。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/render_preview.py` | `--check` 结构化能力；`--capture-autocad-window`；`--execution-summary` 聚焦 |
| `scripts/render_preview.py` | 兼容包装 |
| `core/cad_io/autocad_com.py` | `zoom_to_bbox` / `zoom_to_handles` |
| `core/verification/cad_validation_runner.py` | 总控改用窗口截图 `cad-validation-window.png` |
| `tests/core/test_render_preview.py` | 窗口截图与能力字段 |
| `tests/core/test_cad_validation_runner.py` | 总控命令断言 |
| `CORE_*` / `CAD_AGENT_*` / `docs/planning/phase-r-rebirth-implementation-plan.md` 等 | 状态与执行记录 |

### 3. 关键设计说明

- 截图范围：AutoCAD **客户区**，非全屏；可选按本轮 `created_handles` bbox 缩放视图后再截。
- 总控步骤 `capture_screen` 使用 `--capture-autocad-window --execution-summary ...`。
- **硬规则**：`screenshot_role=visual_aid_only`；截图不参与 `geometry_verified` 判定。
- 无 CAD 时 `--check` 不得误报 `autocad_window` ready。

### 4. 新增/修改测试

- `tests.core.test_render_preview`
- `tests.core.test_cad_validation_runner`  
- 聚焦运行：**11 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_render_preview tests.core.test_cad_validation_runner
& $py scripts\render_preview.py --check
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\r-cad-view-no-cad
# status=pass（含 unittest discover）
& $py scripts\run_cad_validation.py --output-dir output\validation_runs\r-cad-view-cad
# status=pass
```

### 6. 是否运行真实 CAD

**是**（`r-cad-view-cad`）。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| 总控 | `output/validation_runs/r-cad-view-cad/report.json` → `status=pass` |
| 回读 | `output/validation_runs/r-cad-view-cad/readback_report.json` → `status=geometry_verified` |
| 能力探针 | `output/validation_runs/r-cad-view-cad/cad_capability_probe.json` → `status=cad_capability_verified` |
| 截图 | `output/validation_runs/r-cad-view-cad/cad-validation-window.png` |
| 执行摘要 | `output/validation_runs/r-cad-view-cad/execution_summary.json` |

**baseline `draw_test_cabinet` created handles（本轮落图）**：

`631`, `632`, `633`, `634`, `635`, `636`, `67B`

**截图元数据（stdout 摘录）**：`mode=autocad_window`，`focus.status=zoomed_to_bbox`，`handle_count=7`

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| 窗口级截图可用、总控 pass | non-CAD + 真实 CAD 流程 |
| baseline 柜体 readback | **`geometry_verified`**（created handles 定向回读） |
| 能力探针 | **`cad_capability_verified`**（primitive probe，≠ 任意 CAD_PLAN） |
| 截图本身 | **visual_aid_only**，非几何证据 |

### 9. 剩余风险

- 未覆盖多显示器、更细绘图区裁剪、遮挡边界。
- 不能把截图 pass 扩大为块库或任意 plan 几何通过。

---

## 2. R-CAD-CONTRACT

**日期**：2026-05-26  
**PlanMD 顺序**：开发包 #1

### 1. 开发包名

`R-CAD-CONTRACT` — 基础图元探针与 readback 报告固化为机器可读 CAD 能力契约。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/evidence_contract.py` | **新增**：证据词表、`ENTITY_CONTRACTS`、probe/readback 注解与门禁校验 |
| `core/verification/cad_capability_probe.py` | 输出 `evidence_state` / `geometry_accuracy` / `screenshot_role` / `contract` |
| `core/verification/verification_report.py` | readback 报告证据字段 |
| `core/verification/cad_validation_runner.py` | 证据字段硬门禁；步骤透传 |
| `core/schemas/verification_report.schema.json` | 可选证据字段 |
| `examples/verification_reports/minimal_cabinet_verification.json` | 示例补字段 |
| `docs/planning/phase-r-cad-capability-contract.md` | 契约文档 + 机器可读字段表 |
| `tests/core/test_cad_capability_probe.py` | 证据字段断言 |
| `tests/core/test_cad_validation_runner.py` | 缺证据字段门禁 |
| `CORE_*` / `CAD_AGENT_*` | 状态同步 |

### 3. 关键设计说明

- 分离两类几何结论：
  - `cad_capability_verified` + `verified_by_cad_capability_readback`（primitive 探针）
  - `readback_geometry_verified` + `verified_by_cad_readback`（plan 级 created handles 回读）
- `cad_validation_runner` 顶层 pass 仍依赖 `readback_report.status=geometry_verified` 与 `cad_capability_probe.status=cad_capability_verified`。
- `block_reference` / `insert_block_alpha` 在契约中标记为 **deferred**。

### 4. 新增/修改测试

- `tests.core.test_cad_capability_probe`
- `tests.core.test_cad_validation_runner`
- `tests.core.test_geometry_checks`
- `tests.core.test_verification_report`  
- 相关集：**28 tests OK**（该包子集）；全量随后 **228 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_cad_capability_probe tests.core.test_cad_validation_runner tests.core.test_geometry_checks tests.core.test_verification_report
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\r-cad-contract-no-cad
# status=pass
& $py scripts\run_cad_validation.py --output-dir output\validation_runs\r-cad-contract-cad
# status=pass
```

### 6. 是否运行真实 CAD

**是**（`r-cad-contract-cad`）。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| 总控 | `output/validation_runs/r-cad-contract-cad/report.json` → `status=pass` |
| 回读 | `output/validation_runs/r-cad-contract-cad/readback_report.json` → `status=geometry_verified`，`evidence_state=readback_geometry_verified` |
| 能力探针 | `output/validation_runs/r-cad-contract-cad/cad_capability_probe.json` → `cad_capability_verified`，`evidence_state=cad_capability_verified` |
| 截图 | `output/validation_runs/r-cad-contract-cad/cad-validation-window.png` |

**baseline created handles**：`751`–`756`, `79B`

**capability probe created handles（独立探针落图）**：`7E0`–`7E9`, `82D`（共 11）

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| 证据字段、runner 门禁、schema | **non-CAD**（+ 真实 CAD 总控流程 pass） |
| baseline plan readback | **`geometry_verified`** |
| capability probe | **`cad_capability_verified`**（有限 primitive 样本） |
| block insertion | **未验证**（契约中 deferred） |

### 9. 剩余风险

- 不能把 `cad_capability_verified` 说成任意 CAD_PLAN 或真实块库已通过。
- `r-cad-view-cad` 的 readback 若在 CONTRACT 之前生成，可能无 `evidence_state` 字段（后续 run 会有）。

---

## 3. R-BLOCK-METADATA

**日期**：2026-05-26  
**PlanMD 顺序**：开发包 #2

### 1. 开发包名

`R-BLOCK-METADATA` — `BLOCK_LIBRARY v0.2`、受控测试块 metadata、`object_spec_to_block_reference`。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/schemas/block_library.schema.json` | 支持 `0.1` / `0.2` |
| `libraries/blocks/block_library.example.json` | 升为 `0.2`；`controlled-test-block-001` + symbol_fallback 块 |
| `libraries/blocks/controlled/CODEX_TEST_BLOCK_001.metadata.json` | **新增**侧车 metadata |
| `core/block_engine/block_library.py` | `normalize_block`、`validate_block_library`、`object_spec_to_block_reference` |
| `core/block_engine/block_selector.py` | `validation.status` 过滤 |
| `core/block_engine/block_placement.py` | `cad_identity`、`layer_role` |
| `tests/core/test_block_engine.py` | v0.2 / 受控块 / fallback |
| `tests/fixtures/invalid_models/block_library*.invalid.json` | 反例 |
| `docs/planning/phase-r-block-library-roadmap.md` | 状态更新 |
| `CORE_*` / `CAD_AGENT_*` | 状态同步 |

### 3. 关键设计说明

- `controlled-test-block-001` → `CODEX_TEST_BLOCK_001`，`validation.status=metadata_only`。
- 其余示例块为 `symbol_fallback`，不接真实公司块库。
- `0.1` 库（`examples/block_libraries/minimal_builtin_blocks.json`）仍可加载，`normalize_block` 补全 v0.2 派生字段。
- selector 排除 `deferred_cad_readback` 等不可选状态。

### 4. 新增/修改测试

- `tests.core.test_block_engine`
- `tests.core.test_schema_validation`（block_library 反例）  
- 全量：**234 tests OK**；`run_repo_audit.py --fail-on-findings` → **0 findings**；blank-shell benchmark **pass**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_block_engine tests.core.test_schema_validation
& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\r-block-metadata-check
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\r-block-metadata-no-cad
# status=pass
```

### 6. 是否运行真实 CAD

**否**（仅 no-CAD 总控）。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| 总控 | `output/validation_runs/r-block-metadata-no-cad/report.json` → `status=pass` |

无 `readback_report.json`、无截图、无 `created_handles`（符合预期）。

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| schema、loader、selector、benchmark、repo audit | **non-CAD** |
| 真实块插入 / block readback | **未验证** |
| `geometry_verified` | **未达到** |

### 9. 剩余风险

- metadata 就绪 ≠ AutoCAD 中已有 `CODEX_TEST_BLOCK_001` 块定义。
- 下一包 `R-BLOCK-CAD-ALPHA` 才做真实插入与 readback。

---

## 4. R-BLOCK-PLAN

**日期**：2026-05-26  
**PlanMD 顺序**：开发包 #3

### 1. 开发包名

`R-BLOCK-PLAN` — 受控 `insert_block_alpha` CAD_PLAN intent（validate / dry-run / fake execute）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/plan_engine/block_alpha_plan.py` | **新增** validate + dry-run |
| `examples/plans/insert_block_alpha_test.json` | **新增**合法示例 |
| `tests/fixtures/invalid_plans/insert_block_alpha_formal_layer.invalid.json` | 反例 |
| `core/plan_engine/validate_plan.py` | 支持 `insert_block_alpha` |
| `core/plan_engine/dry_run_report.py` | 分支 dry-run |
| `core/plan_engine/dry_run_plan.py` | 改用 `create_dry_run_report` |
| `core/execution/execute_plan.py` | fake `insert_block_alpha` 执行路径 |
| `core/schemas/cad_plan.schema.json` | intent 扩展 |
| `schemas/cad_plan.schema.json` | 同步 |
| `tests/core/test_plan_engine.py` | validate / dry-run / 反例 |
| `tests/core/test_execute_plan.py` | fake driver 记录 |
| `CORE_*` / `CAD_AGENT_*` | 状态同步 |

### 3. 关键设计说明

- 最小合法 plan：`block_id`、`cad_identity.block_name`、`base_point`、`rotation`、`scale`、`layer=CODEX_PREVIEW`。
- validate 拒绝：正式图层、`空 block_name`、非法 `scale`、缺 `base_point`。
- dry-run 输出 bbox / anchor / rotation / layer role，`evidence_state=dry_run_valid_plan_only`。
- `execute_plan` 仅调用 fake driver `insert_block_alpha()`，**不连 AutoCAD**。
- 与 `draw_object` 分 intent 维护，避免混用 width/depth 规则。

### 4. 新增/修改测试

- `tests.core.test_plan_engine`（含 insert_block_alpha 用例）
- `tests.core.test_execute_plan`
- `tests.core.test_validation_edges`  
- 全量：**239 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\validate_plan.py examples\plans\insert_block_alpha_test.json
# VALID CAD_PLAN
& $py scripts\dry_run_plan.py examples\plans\insert_block_alpha_test.json
# status valid, geometry_accuracy=not_verified_without_cad_readback
& $py -m unittest tests.core.test_plan_engine tests.core.test_execute_plan tests.core.test_validation_edges
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\r-block-plan-no-cad
# status=pass
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| 总控 | `output/validation_runs/r-block-plan-no-cad/report.json` → `status=pass` |

无 `readback_report.json`、无截图。fake execute 测试桩 handle：`BLOCK-H1`（仅单测，非 CAD 文件）。

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| validate / dry-run / fake execute / 总控 no-CAD | **non-CAD** |
| `dry_run_valid_plan_only` | **non-CAD**（明确未几何验证） |
| `geometry_verified` | **未达到** |
| 真实块插入 | **deferred** → `R-BLOCK-CAD-ALPHA` |

### 9. 剩余风险

- `AutoCADComDriver` 尚未实现真实 `insert_block_alpha`。
- 不能把 dry-run / fake execute pass 说成块已在 DWG 中插准。

---

## 5. R-BLOCK-CAD-01

**日期**：2026-05-26  
**父包**：`R-BLOCK-CAD-ALPHA`  
**PlanMD 顺序**：二级小包 #1

### 1. 开发包名

`R-BLOCK-CAD-01` — 受控块定义查找 / 最小创建策略（`CODEX_TEST_BLOCK_001`）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/cad_io/autocad_com.py` | `ensure_controlled_block_definition()`、`block_definition_exists()`、结构化 `definition_missing` |
| `tests/core/test_autocad_com_driver.py` | 5 项受控块定义单测 |
| `docs/planning/phase-r-cad-capability-contract.md` | 受控块定义解析说明 |
| `docs/planning/phase-r-rebirth-implementation-plan.md` | 标记小包完成 |
| `CAD_AGENT_CHANGELOG.md` / `CAD_AGENT_STATUS.md` / `CORE_CONTEXT_BRIEF.md` | 状态同步 |

### 3. 关键设计说明

- 优先 `doc.Blocks.Item("CODEX_TEST_BLOCK_001")` 复用已有块表记录。
- 缺失时在块定义空间用 layer `0` 画 100×50 矩形（4 条 `AddLine`），**不保存 DWG、不写正式项目图层**。
- 成功返回 `status=ready` + `source=existing|created`；失败返回 `status=definition_missing` + `failure_category=definition_missing`。
- 本包不实现 `insert_block_alpha` COM 插入，也不声称 `geometry_verified`。

### 4. 新增/修改测试

- `tests.core.test_autocad_com_driver.ControlledBlockDefinitionTests`（5 项）
- 全量：**244 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_autocad_com_driver -v
# Ran 9 tests OK
& $py -m unittest discover -s tests -q
# Ran 244 tests OK
```

### 6. 是否运行真实 CAD

**否**（仅 mock `doc.Blocks` 单测）。

### 7. CAD 证据路径

无 `output/validation_runs` 证据。本包只验证 driver 策略与失败分类，不连 AutoCAD。

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| 块定义解析策略 / driver 单测 | **non-CAD** |
| `geometry_verified` | **未达到** |
| 真实块引用插入 | **deferred** → `R-BLOCK-CAD-02` |

### 9. 剩余风险

- DWG 中是否已有 `CODEX_TEST_BLOCK_001` 仍须在真实 CAD 会话下由 `R-BLOCK-CAD-02` 起验证。
- 不能把“可创建块定义”说成“块引用已插准”。

---

## 6. R-BLOCK-CAD-02

**日期**：2026-05-26  
**父包**：`R-BLOCK-CAD-ALPHA`  
**PlanMD 顺序**：二级小包 #2

### 1. 开发包名

`R-BLOCK-CAD-02` — `AutoCADComDriver.insert_block_alpha()` 最小 COM 写入（`CODEX_PREVIEW`、统一 scale）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/cad_io/autocad_com.py` | `insert_block_alpha()`、`BlockAlphaInsertionError`、`block_insert_failure()` |
| `tests/core/test_autocad_com_driver.py` | 5 项 insert 单测 |
| `tests/core/test_execute_plan.py` | COM driver 与 `execute_plan` 契约单测 |
| `docs/planning/phase-r-cad-capability-contract.md` | 补充写入路径说明 |
| `docs/planning/phase-r-rebirth-implementation-plan.md` | 标记小包完成 |
| `CAD_AGENT_CHANGELOG.md` / `CAD_AGENT_STATUS.md` / `CORE_CONTEXT_BRIEF.md` | 状态同步 |

### 3. 关键设计说明

- 执行顺序：`ensure_controlled_block_definition()` → `ModelSpace.InsertBlock` → `_apply_common(layer=CODEX_PREVIEW)`。
- 仅接受 `layer=CODEX_PREVIEW` 与统一 `scale`；非 preview layer 在 driver 层 `ValueError`，validate/execute 上游也会拒绝。
- 块属性（`attributes`）显式 deferred，抛出 `attribute_unverified`。
- 返回 `handle` + `geometry_accuracy=not_verified_without_cad_readback`；不得据此声称几何通过。

### 4. 新增/修改测试

- `ControlledBlockDefinitionTests` 内 5 项 `insert_block_alpha` 用例
- `test_insert_block_alpha_autocad_driver_matches_execute_plan_contract`
- 全量：**250 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_autocad_com_driver tests.core.test_execute_plan -q
& $py -m unittest discover -s tests -q
# Ran 250 tests OK
```

### 6. 是否运行真实 CAD

**否**（mock `InsertBlock` / `execute_plan` 桩）。

### 7. CAD 证据路径

无 `output/validation_runs` 证据。

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| COM 写入接口 / driver+execute 单测 | **non-CAD** |
| `geometry_verified` | **未达到** |
| `block_reference` readback | **deferred** → `R-BLOCK-CAD-03` |

### 9. 剩余风险

- 真实 AutoCAD `InsertBlock` 行为（旋转弧度、块基点）须在用户会话下由 `R-BLOCK-CAD-05` 验证。
- 不能把“接口可调用”说成“块引用几何已 verified”。

---

## 7. R-BLOCK-CAD-03

**日期**：2026-05-26  
**父包**：`R-BLOCK-CAD-ALPHA`  
**PlanMD 顺序**：二级小包 #3

### 1. 开发包名

`R-BLOCK-CAD-03` — `block_reference` readback 标准化（normalize + 几何对照检查）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/inspect_dwg.py` | `AcDbBlockReference` normalize + `GetBoundingBox` |
| `core/verification/geometry_checks.py` | `check_block_reference_readback()`、失败分类 |
| `core/verification/evidence_contract.py` | `readback_normalize_baseline` |
| `tests/core/test_geometry_checks.py` | 5 项 block readback 用例 |
| `tests/core/test_verification_report.py` | block normalize 用例 |
| `docs/planning/phase-r-cad-capability-contract.md` | 状态说明 |
| `CAD_AGENT_*` / `CORE_CONTEXT_BRIEF.md` | 状态同步 |

### 3. 关键设计说明

- COM 实体标准化输出契约字段：`handle`、`type`、`block_name`、`insertion_point`、`rotation`（度）、`scale`、`layer`、`bbox`。
- `check_block_reference_readback()` 对照 `insert_block_alpha` plan 期望值，容差：插入点 1mm、旋转 0.5°、bbox 2mm。
- 缺字段 → `readback_missing`；块名/插入点/旋转不符 → 对应 failure_category。
- 本包不接入 CAD validation runner，不运行真实 CAD。

### 4. 新增/修改测试

- `tests.core.test_geometry_checks`（block readback 5 项）
- `tests.core.test_verification_report`（normalize block）
- 全量：**255 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_geometry_checks tests.core.test_verification_report tests.core.test_autocad_com_driver -q
& $py -m unittest discover -s tests -q
# Ran 255 tests OK
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

无 `output/validation_runs` 证据。

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| readback normalize / 几何对照单测 | **non-CAD** |
| `geometry_verified` | **未达到** |
| validation runner block alpha step | **deferred** → `R-BLOCK-CAD-04` |

### 9. 剩余风险

- 真实 AutoCAD `EffectiveName` / `GetBoundingBox` / 旋转弧度语义须在 `R-BLOCK-CAD-05` 用户会话下复验。
- 不能把 normalize 单测 pass 说成块 alpha 已在 DWG 中几何 verified。

---

## 8. R-BLOCK-CAD-04

**日期**：2026-05-26  
**父包**：`R-BLOCK-CAD-ALPHA`  
**PlanMD 顺序**：二级小包 #4

### 1. 开发包名

`R-BLOCK-CAD-04` — CAD validation runner 接入 block alpha（no-CAD deferred + CAD 步骤骨架）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/cad_validation_runner.py` | block alpha steps + gate + `report.block_alpha` |
| `core/verification/block_alpha_validation.py` | **新增** 报告构建与证据校验 |
| `scripts/run_block_alpha_validation.py` | **新增** CLI |
| `tests/core/test_block_alpha_validation.py` | **新增** |
| `tests/core/test_cad_validation_runner.py` | no-CAD deferred + CAD 步骤用例 |
| `CAD_AGENT_*` / `CORE_CONTEXT_BRIEF.md` | 状态同步 |

### 3. 关键设计说明

- **no-CAD**：`block_alpha_deferred_evidence` 写 `block_alpha_report.json`，`evidence_state=deferred_cad_readback_required`；硬门禁禁止 `geometry_verified`。
- **CAD**：`block_alpha_execute` + `block_alpha_readback`；readback 须 `geometry_verified` 才 pass（`R-BLOCK-CAD-05` 真实验收）。
- 顶层 `report.json` 增加 `block_alpha.geometry_verified`，避免把总控 pass 误解为块几何已 verified。

### 4. 新增/修改测试

- `tests.core.test_block_alpha_validation`（3 项）
- `tests.core.test_cad_validation_runner`（含 no-CAD deferred）
- 全量：**259 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_block_alpha_validation tests.core.test_cad_validation_runner -q
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\r-block-alpha-no-cad-test
# report.status=pass; block_alpha.geometry_verified=false
```

### 6. 是否运行真实 CAD

**否**（no-CAD 总控实跑；未执行 `block_alpha_execute` COM 插入）。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| 总控 | `output/validation_runs/r-block-alpha-no-cad-test/report.json` |
| block alpha | `output/validation_runs/r-block-alpha-no-cad-test/block_alpha_report.json` → `status=deferred` |

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| validate / dry-run / no-CAD deferred / 总控 pass | **non-CAD** |
| `block_alpha.geometry_verified` | **false**（符合预期） |
| 真实块引用几何 verified | **deferred** → `R-BLOCK-CAD-05` |

### 9. 剩余风险

- 真实 AutoCAD 下 `block_alpha_readback` 是否达到 `geometry_verified` 须在用户会话执行 `R-BLOCK-CAD-05`。
- 不能把 no-CAD 总控 pass 说成块已在 DWG 中插准。

---

## 9. R-BLOCK-CAD-05

**日期**：2026-05-26  
**父包**：`R-BLOCK-CAD-ALPHA`（**二级小包全部完成**）

### 1. 开发包名

`R-BLOCK-CAD-05` — 真实 AutoCAD 受控块 alpha：插入 + created handles 定向 readback + 窗口截图。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/cad_io/autocad_com.py` | 受控块定义 footprint 与 metadata 对齐（900×450） |
| `core/verification/cad_validation_runner.py` | `--block-alpha-only`、`block_alpha_capture_screen` |
| `core/verification/block_alpha_validation.py` | readback 报告挂截图路径 |
| `scripts/run_block_alpha_validation.py` | 截图证据 |
| `docs/verification/block_alpha_cad_evidence.md` | **新增** 证据索引 |
| `CAD_AGENT_*` / `CORE_CONTEXT_BRIEF.md` | 状态同步 |

### 3. 关键设计说明

- 使用 `run_cad_validation.py --block-alpha-only` 只跑 block alpha 相关步骤，避免与 cabinet baseline 混跑。
- 真实插入 `CODEX_TEST_BLOCK_001` 到 `CODEX_PREVIEW`，`created_handles` 定向 readback，不用全 ModelSpace 扫描。
- 截图 `block-alpha-window.png` 仅为 `visual_aid_only`，不参与几何 pass 判定。

### 4. 新增/修改测试

- 全量：**259 tests OK**（footprint 对齐后无回归）

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_cad_validation.py --block-alpha-only --output-dir output\validation_runs\r-block-alpha-cad
# report.status=pass
# block_alpha.geometry_verified=true
# block_alpha_report.status=geometry_verified
```

### 6. 是否运行真实 CAD

**是**（AutoCAD `Drawing1.dwg`，用户会话 COM 可用）。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| 总控 | `output/validation_runs/r-block-alpha-cad/report.json` |
| 执行 | `output/validation_runs/r-block-alpha-cad/block_alpha_execution_summary.json` |
| readback | `output/validation_runs/r-block-alpha-cad/block_alpha_report.json` |
| 截图 | `output/validation_runs/r-block-alpha-cad/block-alpha-window.png` |
| 说明 | `docs/verification/block_alpha_cad_evidence.md` |

`created_handles`: `["878"]`

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| 受控 block alpha 样本 readback | **`geometry_verified`** / `readback_geometry_verified` |
| 截图 | `visual_aid_only`（辅助） |
| 任意块库 / 项目图纸 | **不可声称** |

### 9. 剩余风险

- DWG 中若已存在旧版 100×50 受控块定义，需删除或换名后重跑，否则 bbox 可能不一致（本轮为新插入 + readback pass）。
- 不能把本次 pass 说成公司块库或 office micro-scene 已完成。

---

## 10. R-OFFICE-MICRO-01

**日期**：2026-05-26  
**父包**：`R-OFFICE-MICRO`

### 1. 开发包名

`R-OFFICE-MICRO-01` — office alpha 对象级扩展：电脑桌、储物柜柜前净空、文件柜。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `libraries/objects/object_defaults.json` | 新增 `computer_desk`、`storage_cabinet`、`file_cabinet`（含 `placement_role`、`clearance_refs`、`assertion_hints`） |
| `core/object_engine/parametric_objects.py` | `create_object_spec` 透传 `placement_role`、`clearance_refs`、`assertion_hints` |
| `core/benchmarks/runner.py` | `contains_clearance_refs` 断言；object_spec metrics 输出 `clearance_ref_roles`、`placement_role` |
| `examples/benchmarks/office_alpha_benchmark.json` | 新增 3 个 object_spec cases（7 cases 合计） |
| `tests/core/test_benchmarks.py` | office alpha 契约改为 7/7 pass |
| `docs/planning/phase-r-office-benchmark-cases.md` | 落地状态同步 |
| `CAD_AGENT_*` / `CORE_CONTEXT_BRIEF.md` | 状态同步 |

### 3. 关键设计说明

- 电脑桌默认 `1200×700×750`，`placement_role=screen_workstation`，组件含 `monitor_zone`、`cable_side_hint`。
- 储物柜 / 文件柜在 defaults 中带 `cabinet_front_clearance`（`front_depth_mm=800`），benchmark 用 `contains_clearance_refs` 机器断言。
- 仍为 non-CAD object_spec pipeline：`evidence_state=benchmark_pass_non_cad`，几何未做 CAD readback。

### 4. 新增/修改测试

- `tests.core.test_benchmarks.test_office_alpha_benchmark_runs_phase_r_contract`：7 cases、clearance / placement 断言
- 全量：**259 tests OK**（无新增独立单测文件）

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_benchmarks -v
# 11 tests OK

& $py -m unittest discover -s tests -q
# Ran 259 tests OK

& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\office_object_r1
# suite status=pass, 7/7 cases
```

### 6. 是否运行真实 CAD

**否**（仅 object_spec validate / dry-run / unverified verification）。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| benchmark 汇总 | `output/test_artifacts/benchmarks/office_object_r1/`（各 case 子目录含 `object_spec.json`、`dry_run_report.json` 等） |
| 规格参考 | `docs/planning/phase-r-office-benchmark-cases.md` |

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| 7 个 office alpha cases（含 3 个新 object cases） | **`benchmark_pass_non_cad`** |
| 几何准确性 | `not_verified_without_cad_readback` |
| 截图 | `visual_aid_only`（本包未要求截图） |
| micro-scene / failure / 办公真实 CAD | **不可声称** |

### 9. 剩余风险

- `cabinet_front_clearance` 目前只在 object spec 语义层存在，未接入 placement / collision 或真实 CAD 净空几何验证。
- 不能把 7/7 non-CAD pass 说成办公微场景、入口通道或失败样本已完成。

---

## 11. R-OFFICE-MICRO-02

**日期**：2026-05-26  
**父包**：`R-OFFICE-MICRO`

### 1. 开发包名

`R-OFFICE-MICRO-02` — office alpha 微场景 benchmark：单桌椅、桌后柜、双工位主通道、入口接待净空。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/composition_engine/templates.py` | 4 个 office micro-scene 模板；`composition_micro_scene_metrics()` |
| `core/benchmarks/runner.py` | `contains_binding_relations`、`contains_circulation_roles`；composition metrics 透传 |
| `examples/benchmarks/office_alpha_benchmark.json` | 4 个 `composition_spec` micro-scene cases（11 cases 合计） |
| `tests/core/test_composition_engine.py`、`tests/core/test_benchmarks.py` | 微场景契约测试 |
| `CAD_AGENT_*` / `CORE_CONTEXT_BRIEF.md` / `phase-r-office-benchmark-cases.md` | 状态同步 |

### 3. 关键设计说明

- 微场景走既有 `composition_spec` pipeline，不新增布局算法；`bindings`、`clearance_refs`、`circulation` 为结构化语义字段。
- `single_desk_chair_pair`：椅绑桌 + `chair_pullback_clearance`。
- `desk_with_back_cabinet`：桌/椅/背柜 + 椅后与柜前双净空 refs。
- `two_workstations_shared_aisle`：双工位 + `main_aisle` circulation 语义。
- `entry_reception_clearance`：接待桌 + `entry_clearance` ref。

### 4. 新增/修改测试

- `test_office_micro_scene_compositions_expose_bindings_and_clearance`
- `test_office_alpha_benchmark_runs_phase_r_contract`：11/11
- 全量：**260 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_benchmarks tests.core.test_composition_engine -v
& $py -m unittest discover -s tests -q
& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\office_micro_r2
# 11/11 pass
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| benchmark 汇总 | `output/test_artifacts/benchmarks/office_micro_r2/` |
| 各 case | 含 `composition_spec.json`、`preview.svg`、`cad_plans.json` 等 |

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| 11 个 office alpha cases | **`benchmark_pass_non_cad`** |
| 微场景绑定 / 净空 / 通道 | 语义层可机器断言；**非几何验证** |
| 场景级扩展 / failure / 办公真实 CAD | **不可声称** |

### 9. 剩余风险

- `main_aisle` / `entry_clearance` 仅为 composition 元数据，未与 blank-shell placement 或 CAD 几何联动。
- 不能把 micro-scene pass 说成通道连续性或入口净空已在 DWG 中验证。

---

## 12. R-OFFICE-MICRO-03

**日期**：2026-05-26  
**父包**：`R-OFFICE-MICRO`

### 1. 开发包名

`R-OFFICE-MICRO-03` — office alpha 场景级 blank-shell benchmark：长条主通道、障碍避让、会议/电脑混合区。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `examples/shell_models/office_long_narrow_shell.json` 等 3 个 shell | **新增** 场景 shell |
| `examples/workflows/blank_shell_office_*_layout_loop.json` ×3 | **新增** 场景 workflow |
| `core/workflows/blank_shell_pipeline.py` | metrics 增加 `no_place_zone_count`、`fixed_obstacle_count`、`shell_id` |
| `core/benchmarks/runner.py` | `_actual_from_pipeline` 透传场景 metrics |
| `examples/benchmarks/office_alpha_benchmark.json` | +3 blank_shell scene cases（14 cases 合计） |
| `tests/core/test_benchmarks.py`、`tests/core/test_schema_validation.py` | 契约与 schema 校验 |

### 3. 关键设计说明

- 场景 case 走既有 `blank_shell` pipeline，不新增布局算法。
- `long_narrow_office_main_aisle`：22000×4200 长条 shell，断言 circulation / zone / placement 与 `shell-office-long-narrow`。
- `office_obstacle_avoidance_riser`：双障碍 + 双 `no_place_zone`，断言 `no_place_zone_count` / `fixed_obstacle_count`。
- `meeting_computer_mixed_zone`：混合区 shell，`object_types` 含 `computer_desk` + `table`。

### 4. 新增/修改测试

- `test_office_alpha_benchmark_runs_phase_r_contract`：14/14
- shell schema 校验覆盖 3 个新 shell
- 全量：**260 tests OK**（无新增独立测试文件）

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_benchmarks tests.core.test_schema_validation -v
& $py -m unittest discover -s tests -q
& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\office_scene_r1
# 14/14 pass
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| benchmark 汇总 | `output/test_artifacts/benchmarks/office_scene_r1/` |

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| 14 个 office alpha cases | **`benchmark_pass_non_cad`** |
| 场景 shell / placement 指标 | 可机器断言；**非几何验证** |
| failure cases / 办公真实 CAD 几何 | **不可声称** |

### 9. 剩余风险

- `failed_check_count=0` 只表示当前 Alpha placement 未报 fail，不证明真实通道连续或障碍已避让。
- failure benchmark 已改由 `R-OFFICE-MICRO-04` 承接（见 §13）。

---

## 13. R-OFFICE-MICRO-04

**日期**：2026-05-26  
**父包**：`R-OFFICE-MICRO`

### 1. 开发包名

`R-OFFICE-MICRO-04` — office alpha failure benchmark：过小房间、门前净空冲突、椅后/柜前净空冲突。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/layout_engine/office_layout_failure.py` | **新增** failure 分类与 composition 净空冲突检测 |
| `core/workflows/blank_shell_pipeline.py` | `layout_expectation` 硬阻断 partial layout |
| `core/benchmarks/runner.py` | `failure_category`、`contains_blocked_reason`、`blocked_expected_non_cad` |
| `core/composition_engine/templates.py` | +2 failure composition 模板 |
| `examples/shell_models/office_too_small_workstation_shell.json` | **新增** |
| `examples/workflows/blank_shell_office_too_small_workstation_layout_loop.json` | **新增** |
| `examples/benchmarks/office_alpha_benchmark.json` | +3 failure cases（17 cases 合计） |
| `tests/core/test_office_layout_failure.py` | **新增** |
| `tests/core/test_benchmarks.py` | office alpha 17/17 契约 |

### 3. 关键设计说明

- failure case 必须 `pipeline_status=blocked` 且 `evidence_state=blocked_expected_non_cad`，禁止少放对象后返回 pass。
- `too_small_room_for_workstation`：过小 shell + `require_all_placed` → `insufficient_space`。
- `door_clearance_conflict` / `cabinet_pullback_conflict`：composition 模板故意重叠净空语义，runner 在 dry-run 前阻断。

### 4. 新增/修改测试

- `tests/core/test_office_layout_failure.py`：3 tests
- `test_office_alpha_benchmark_runs_phase_r_contract`：17/17
- 全量：**293 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_office_layout_failure tests.core.test_benchmarks -v
& $py -m unittest discover -s tests -q
& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\office_failure_r4
# 17/17 pass（14 benchmark_pass_non_cad + 3 blocked_expected_non_cad）
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| benchmark 汇总 | `output/test_artifacts/benchmarks/office_failure_r4/` |

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| 14 个 pass office cases | **`benchmark_pass_non_cad`** |
| 3 个 failure cases | **`blocked_expected_non_cad`**（`insufficient_space` / `entry_clearance_conflict` / `clearance_conflict`） |
| 办公真实 CAD 几何 | **不可声称** |

### 9. 剩余风险

- failure 检测基于 conservative bbox / 净空语义，不是完整碰撞或通道算法。
- office alpha 汇总见 `docs/verification/office_alpha_benchmark_evidence.md`（`R-OFFICE-MICRO-05`）。

---

## 14. R-OFFICE-MICRO-05

**日期**：2026-05-26  
**父包**：`R-OFFICE-MICRO`（**父包 5/5 收口**）

### 1. 开发包名

`R-OFFICE-MICRO-05` — office alpha 报告汇总、证据计数与不可声称边界。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/benchmarks/runner.py` | `summarize_benchmark_evidence()`；suite 写入 `benchmark_summary.json` |
| `docs/verification/office_alpha_benchmark_evidence.md` | **新增** Alpha 证据与退出门槛 |
| `docs/planning/phase-r-office-benchmark-cases.md` | Alpha 退出门槛表、收口证据链接 |
| `tests/core/test_benchmarks.py` | `evidence_summary` 与 summary 文件契约 |
| `CAD_AGENT_*` / `CORE_CONTEXT_BRIEF.md` | 状态同步 |

### 3. 关键设计说明

- `benchmark_summary.json` 为 suite 级机器可读出口：`evidence_state_counts`、`failure_category_counts`、`non_cad_only`。
- office alpha **仅**证明 non-CAD 规格与 failure 语义；`geometry_verified_case_count` 必须为 0。
- 父包 `R-OFFICE-MICRO` 完成后，下一队列按 PlanMD 为 `R4-EVIDENCE-GATES`。

### 4. 新增/修改测试

- `test_office_alpha_benchmark_runs_phase_r_contract`：断言 `evidence_summary`
- `test_summarize_benchmark_evidence_counts_states`
- 全量：**294 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_benchmarks -v
& $py -m unittest discover -s tests -q
& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\office_alpha_r_micro
# 17/17 pass；benchmark_summary.json: 14 benchmark_pass_non_cad + 3 blocked_expected_non_cad
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| benchmark 汇总 | `output/test_artifacts/benchmarks/office_alpha_r_micro/benchmark_summary.json` |
| 证据说明 | `docs/verification/office_alpha_benchmark_evidence.md` |

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| office alpha 17 cases | suite `pass`；**全部 non-CAD** |
| `R-OFFICE-MICRO` 父包 | **5/5 完成** |
| 办公真实 CAD 几何 | **不可声称** |

### 9. 剩余风险

- 证据汇总依赖 runner 派生字段；跨 suite 统一门禁待 `R4-EVIDENCE-GATES`。
- office 布局真实 CAD readback 仍 deferred。

---

## 15. R4-01

**日期**：2026-05-26  
**父包**：`R4-EVIDENCE-GATES`

### 1. 开发包名

`R4-01` — 统一 evidence classifier / vocabulary，避免 benchmark / CAD runner 各自拼词。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/evidence_contract.py` | 词表常量、`classify_benchmark_pipeline_evidence`、校验函数 |
| `core/benchmarks/runner.py` | 使用统一分类器；expected/actual 未知词失败 |
| `core/composition_engine/templates.py` | 从契约导入几何/截图常量 |
| `core/plan_engine/block_alpha_plan.py` | `EVIDENCE_DRY_RUN_VALID_PLAN_ONLY` 常量 |
| `core/schemas/verification_report.schema.json` | evidence_state enum 补全 |
| `docs/verification/evidence_state_vocabulary.md` | **新增** 词表说明 |
| `tests/core/test_evidence_classifier.py` | **新增** |

### 3. 关键设计说明

- 所有 benchmark `evidence_state` 必须由 `classify_benchmark_pipeline_evidence` 或契约常量产生。
- `run_benchmark_suite` 汇总时若 actual 含未知 `evidence_state` 会抛错。
- `blocked_expected_non_cad` / `invalid_configuration` 正式纳入 schema 与 `EVIDENCE_STATE_VALUES`。

### 4. 新增/修改测试

- `tests/core/test_evidence_classifier.py`：4 tests
- `test_benchmark_case_rejects_unknown_expected_evidence_state`
- 全量：**299 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_evidence_classifier tests.core.test_benchmarks tests.core.test_verification_report -v
& $py -m unittest discover -s tests -q
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

无（词表与 non-CAD benchmark 校验）。

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| evidence 词表 | 机器可读、可校验 |
| benchmark actual | 统一派生，禁止未知词 |

### 9. 剩余风险

- failure / suite 硬断言已由 `R4-02`、`R4-03` 覆盖；CAD runner gate 见 `R4-04`。

---

## 16. R4-02

**日期**：2026-05-26  
**父包**：`R4-EVIDENCE-GATES`

### 1. 开发包名

`R4-02` — blocked / invalid failure benchmark 机器断言与静默 pass 防护。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/evidence_contract.py` | `validate_failure_expected_contract`、`BENCHMARK_FAILURE_CATEGORIES` |
| `core/benchmarks/runner.py` | `maximums`、`_compare_failure_outcome_guards`、配置期 failure 校验 |
| `examples/workflows/blank_shell_office_invalid_input_layout_loop.json` | **新增** invalid 样本 |
| `examples/benchmarks/office_alpha_benchmark.json` | +1 invalid case；too_small `maximums` |
| `docs/verification/evidence_state_vocabulary.md` | failure 断言说明 |
| `tests/core/test_benchmarks.py`、`tests/core/test_evidence_classifier.py` | failure 契约测试 |

### 3. 关键设计说明

- failure case 配置期必须声明 `failure_category` 或 `contains_blocked_reason`。
- 运行期禁止 `pipeline_status=ok` + `blocked_expected_non_cad` 组合（静默 pass guard）。
- `too_small` 用 `maximums.cad_plan_count: 0` 防止“少出图仍 pass”。

### 4. 新增/修改测试

- `test_benchmark_case_rejects_failure_expected_without_structured_reason`
- office alpha **18/18** pass
- 全量：**302 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_benchmarks tests.core.test_evidence_classifier -v
& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\r4_office_r2
# 18/18 pass
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/r4_office_r2/benchmark_summary.json`

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| 3× blocked + 1× invalid failure | 机器断言通过 |
| 14× pass cases | 仍为非 CAD |

### 9. 剩余风险

- suite 汇总已由 `R4-03` 覆盖；CAD runner 见 `R4-04`。

---

## 17. R4-03

**日期**：2026-05-26  
**父包**：`R4-EVIDENCE-GATES`

### 1. 开发包名

`R4-03` — 三组 benchmark suite 证据汇总计数与 `expected_evidence_summary` 机器断言。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/evidence_contract.py` | `evidence_summary_rollup`、`validate_evidence_summary` |
| `core/benchmarks/runner.py` | rollup 字段、`expected_evidence_summary` 比对 |
| `examples/benchmarks/*_benchmark.json` ×3 | 增加 `expected_evidence_summary` |
| `docs/verification/evidence_state_vocabulary.md` | suite 汇总说明 |
| `tests/core/test_benchmarks.py` | `test_r4_three_benchmark_suites_match_expected_evidence_summary` |

### 3. 关键设计说明

- `benchmark_summary.json` 的 `evidence_summary` 现含 `benchmark_pass_non_cad_count`、`blocked_expected_non_cad_count`、`invalid_configuration_count` 等 rollup。
- 三组 Core benchmark 均断言 `non_cad_only=true`、`readback_geometry_verified_count=0`。
- office alpha：14 pass + 3 blocked + 1 invalid = 18。

### 4. 新增/修改测试

- `test_r4_three_benchmark_suites_match_expected_evidence_summary`
- 全量：**304 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_benchmarks.BenchmarkRunnerTests.test_r4_three_benchmark_suites_match_expected_evidence_summary -v
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\r4_blank_shell
& $py scripts\run_benchmark_suite.py examples\benchmarks\interior_delivery_benchmark.json --output-root output\test_artifacts\benchmarks\r4_interior
& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\r4_office
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

| suite | 路径 |
| --- | --- |
| blank-shell | `output/test_artifacts/benchmarks/r4_blank_shell/benchmark_summary.json` |
| interior | `output/test_artifacts/benchmarks/r4_interior/benchmark_summary.json` |
| office | `output/test_artifacts/benchmarks/r4_office/benchmark_summary.json` |

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| 三组 suite | 全部 `pass`；证据汇总可机器断言 |
| 几何 verified | **0**（`non_cad_only=true`） |

### 9. 剩余风险

- CAD validation 顶层 gate 已由 `R4-04` 落地；交接填写规范见 `R4-05`。

---

## 18. R4-04

**日期**：2026-05-26  
**父包**：`R4-EVIDENCE-GATES`

### 1. 开发包名

`R4-04` — CAD validation runner 与统一 evidence 词表对齐，禁止顶层 pass 掩盖子报告未验证。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/cad_validation_evidence.py` | **新增** summary + 顶层 gate |
| `core/verification/cad_validation_runner.py` | `evidence_summary`、步骤证据校验、gate 降级 |
| `tests/core/test_cad_validation_evidence.py` | **新增** |
| `tests/core/test_cad_validation_runner.py` | evidence_summary / 无效 evidence 回归 |
| `docs/verification/evidence_state_vocabulary.md` | CAD validation 小节 |

### 3. 关键设计说明

- `report.json` 新增 `evidence_summary`（与 benchmark 同词表 rollup）。
- `--no-cad` 顶层 pass 必须 `non_cad_only=true`。
- 含 CAD 顶层 pass 必须 `inspect_readback` + `cad_capability_probe` 步骤证据态 verified。
- 步骤 stdout 中未知 `evidence_state` 直接使步骤 fail。

### 4. 新增/修改测试

- `tests/core/test_cad_validation_evidence.py`
- `test_top_level_pass_downgraded_when_readback_evidence_state_invalid`
- 全量：**308 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_cad_validation_runner tests.core.test_cad_validation_evidence -v
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\r4-no-cad
# status=pass, evidence_summary.non_cad_only=true
```

### 6. 是否运行真实 CAD

**否**（`--no-cad` 探针）。

### 7. CAD 证据路径

`output/validation_runs/r4-no-cad/report.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| no-CAD 总控 pass | `non_cad_only` | **否** |
| 含 CAD 真实几何 | 须用户会话下全量 CAD 复验 | 非本包范围 |

### 9. 剩余风险

- 交接模板 evidence 字段说明待 `R4-05` 统一（已完成见 §19）。

---

## 19. R4-05

**日期**：2026-05-26  
**父包**：`R4-EVIDENCE-GATES`（**父包 5/5 收口**）

### 1. 开发包名

`R4-05` — 将 evidence gate 规则写入交接模板、状态文档与 Codex 校验指引。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `docs/verification/evidence_gate_handoff_rules.md` | **新增** 交接与审计规则 |
| `docs/verification/evidence_state_vocabulary.md` | 交叉引用 handoff 规则 |
| `docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` | 扩展 9 项模板；§18 R4-04；§19 本包 |
| `docs/handoffs/README.md` | 维护规则增加 evidence gate 链接 |
| `docs/planning/phase-r-rebirth-implementation-plan.md` | R4 执行记录与勾选 |
| `CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md`、`CORE_CONTEXT_BRIEF.md` | R4 父包收口 |

### 3. 关键设计说明

- 每包第 8 项必须使用「结论 + 证据类型 + geometry_verified」三列表格。
- Codex 校验清单与机器路径约定写入 `evidence_gate_handoff_rules.md`，避免各包重复解释。
- `R4-EVIDENCE-GATES` 代码面（R4-01～04）与文档面（R4-05）均已闭环。

### 4. 新增/修改测试

无（文档包）。回归基线仍为 **308 tests OK**（未改 Core 逻辑）。

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest discover -s tests -p "test_*.py" -q
# 308 tests OK（文档包前基线）
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

无新增；规范引用既有路径见 `evidence_gate_handoff_rules.md` §3。

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 交接 evidence gate 文档化 | `non_cad_only`（文档交付） | **否** |

### 9. 剩余风险

- 历史章节（§0～§14）未逐条回填新表格格式；新包须按扩展模板填写。
- 下一小包：`Y-MC-02`（proposal 比较摘要）。

---

## 20. Y-MC-01

**日期**：2026-05-26  
**父包**：`Y-MULTI-CANDIDATE`

### 1. 开发包名

`Y-MC-01` — blank-shell pipeline 在 artifact 中保留 circulation / zone / placement 多候选明细（`candidate_sets.json`）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/workflows/blank_shell_pipeline.py` | `build_blank_shell_candidate_sets()`、`_evaluate_zone_placement_candidates()`、`candidate_sets` 写出 |
| `tests/core/test_blank_shell_pipeline.py` | `candidate_sets` artifact 与分支覆盖测试 |

### 3. 关键设计说明

- `candidate_sets.json` 含 `circulation_branches[]`：每个 circulation 策略下全部 zone 的 placement 尝试（含 `summary`、`placements`、`rank_key`）。
- `selection` 记录最终选用的 circulation / zone（仍优先 `straight_spine` + 最优 placement rank）。
- `circulation_candidates.json` / `placements.json` 保持兼容；下游 layout 仍用选中结果。

### 4. 新增/修改测试

- `test_blank_shell_pipeline_writes_expected_artifacts` 增加 `candidate_sets` 断言
- `test_candidate_sets_include_all_circulation_branches`
- 全量：**309 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_blank_shell_pipeline -v
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\y_mc_01
# 4/4 pass
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/y_mc_01/<case>/candidate_sets.json`（benchmark 各 case 目录）

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 多候选 artifact 可机器读取 | `benchmark_pass_non_cad` | **否** |
| 多 circulation / zone 探索 | `non_cad_only` | **否** |

### 9. 剩余风险

- benchmark 多候选硬断言已由 `Y-MC-03` 覆盖。
- 仍不声称完整自动设计大脑或多方案已自动择优。

---

## 21. Y-MC-02

**日期**：2026-05-26  
**父包**：`Y-MULTI-CANDIDATE`

### 1. 开发包名

`Y-MC-02` — proposal 输出可断言的 `comparison_detail`（对象覆盖率、失败分布、通道连续性、排序原因）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/proposal_engine/proposal_comparison.py` | `build_blank_shell_comparison_detail()`、分支候选摘要 |
| `core/proposal_engine/design_proposal.py` | 接入 `candidate_sets`；`comparison_detail` / narrative |
| `core/schemas/design_proposal.schema.json` | 可选 `comparison_detail` |
| `core/workflows/blank_shell_pipeline.py` | 传入 `candidate_sets` / `object_types` |
| `tests/core/test_proposal_multi_candidate.py`、`test_blank_shell_pipeline.py` | 结构化断言 |

### 3. 关键设计说明

- `comparison_detail.metrics`：`object_coverage_rate`、`failed_check_count`、`failed_reason_distribution`、`circulation_branch_count` 等。
- `circulation_continuity.continuity`：`pass` / `degraded` / `blocked`。
- `needs_confirmation` 仅看**选中** circulation 分支 + layout 失败，未选中分支失败仅作说明。

### 4. 新增/修改测试

- `test_blank_shell_comparison_detail_is_structured_and_assertable`
- pipeline artifact 断言 `comparison_detail`
- 全量：**310 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_proposal_multi_candidate tests.core.test_blank_shell_pipeline -v
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\y_mc_02
# 4/4 pass
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/y_mc_02/<case>/design_proposal.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 多候选比较摘要可机器读取 | `benchmark_pass_non_cad` | **否** |
| 候选说明保留 | `non_cad_only` | **否** |

### 9. 剩余风险

- benchmark 对 `comparison_detail` 的硬断言已由 `Y-MC-03` 完成。

---

## 22. Y-MC-03

**日期**：2026-05-26  
**父包**：`Y-MULTI-CANDIDATE`

### 1. 开发包名

`Y-MC-03` — blank-shell benchmark 多候选指标机器断言。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/benchmarks/runner.py` | actual 字段 + `requires_comparison_detail` 等 |
| `examples/benchmarks/blank_shell_core_benchmark.json` | 四 case 硬断言 |
| `core/workflows/blank_shell_pipeline.py`、`proposal_comparison.py` | metrics 派生 |
| `tests/core/test_benchmarks.py` | `test_y_mc_03_*` |

### 3. 关键设计说明

- 候选数：`candidate_count`、`zone_placement_candidate_count`、`circulation_branch_count`。
- 对象覆盖：`object_coverage_rate` / `comparison_detail_minimums`。
- 失败分布：`selected_failed_reason_distribution`、`failed_reason_distribution_empty`。

### 4. 新增/修改测试

- `test_y_mc_03_blank_shell_benchmark_multi_candidate_assertions`
- 全量：**311 tests OK**

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_benchmarks.BenchmarkRunnerTests.test_y_mc_03_blank_shell_benchmark_multi_candidate_assertions -v
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\y_mc_03
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/y_mc_03/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 多候选 benchmark 契约 | `benchmark_pass_non_cad` | **否** |

### 9. 剩余风险

- 近真实 / 失败 shell 样本已由 `Y-MC-04` 纳入 blank-shell core benchmark。

---

## 23. Y-MC-04

**日期**：2026-05-26  
**父包**：`Y-MULTI-CANDIDATE`

### 1. 开发包名

`Y-MC-04` — blank-shell core 增补近真实 shell 与结构化 failure 样本（8 cases）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `examples/shell_models/blank_shell_corridor_riser_block_shell.json` | **新增** |
| `examples/workflows/blank_shell_corridor_riser_block_layout_loop.json` | **新增** |
| `examples/benchmarks/blank_shell_core_benchmark.json` | +4 cases |
| `core/workflows/blank_shell_pipeline.py` | blocked metrics |
| `tests/core/test_benchmarks.py` | Y-MC-04 测试 |

### 3. 关键设计说明

- Pass：`long_narrow`、`obstacle`（障碍不压、对象仍放置）。
- Blocked：`too_small`、`corridor_riser_blocks_main_path`（`cad_plan_count: 0`）。

### 4. 新增/修改测试

- 全量：**312 tests OK**

### 5. 实际运行的命令和结果

```powershell
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\y_mc_04
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/y_mc_04/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 8-case blank-shell suite | `benchmark_pass_non_cad` / `blocked_expected_non_cad` | **否** |

### 9. 剩余风险

- 多候选边界文档已由 `Y-MC-05` 收口。

---

## 24. Y-MC-05

**日期**：2026-05-26  
**父包**：`Y-MULTI-CANDIDATE`（**父包 5/5 收口**）

### 1. 开发包名

`Y-MC-05` — Phase Y 状态同步与多候选不可声称边界文档化。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `docs/verification/blank_shell_multi_candidate_boundaries.md` | **新增** 边界与 benchmark 契约 |
| `docs/planning/phase-y-blank-shell-hardening-plan.md` | `Y-MC` 映射与退出标准更新 |
| `docs/architecture/shell-layout-foundation-design.md` | §0.1 落地状态 |
| `CORE_*` / `CAD_AGENT_*` / `phase-r-rebirth-implementation-plan.md` | 父包收口 |

### 3. 关键设计说明

- 多候选是 **Alpha 硬化**：可解释、可 benchmark，**不是**完整自动设计大脑。
- 全部 blank-shell core 证据为 non-CAD；`geometry_verified` 仍为 0。
- 后置：复杂几何、自动读图、BETA-PROPOSAL 确认流。

### 4. 新增/修改测试

无（文档包）。基线 **312 tests OK**；benchmark 复验 8/8 pass。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_blank_shell_pipeline tests.core.test_proposal_multi_candidate tests.core.test_benchmarks -q
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\y_mc_05
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/y_mc_05/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| `Y-MULTI-CANDIDATE` 父包收口 | `non_cad_only`（文档 + benchmark） | **否** |

### 9. 剩余风险

- 下一主线 `X-SCENE-ALPHA`；Scene Agent 不得复制 Core 多候选算法。

---

## 25. X-SCENE-01

**日期**：2026-05-26  
**父包**：`X-SCENE-ALPHA`

### 1. 开发包名

`X-SCENE-01` — 锁定 office / residential / restaurant 与可观察 preferences 差异。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/agents/scene_alpha.py` | **新增** 场景校验与权重辅助 |
| `agents/scene_alpha_manifest.json` | **新增** 三场景 manifest |
| `agents/*/preferences.json` | `scene_alpha.tier` + `circulation_strategy_weights` |
| `docs/verification/scene_alpha_preferences_contract.md` | **新增** |
| `tests/agents/test_scene_preferences.py` | X-SCENE-01 断言 |

### 3. 关键设计说明

- 场景层只表达偏好，不复制 Core pipeline / 几何算法。
- 可观察差异：对象优先级、通道宽度、动线权重导致的 Top-1 候选变化。

### 4. 新增/修改测试

- **315 tests OK**；`tests/agents/test_scene_preferences.py` 中 `test_x_scene_01_*`。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.agents.test_scene_preferences -v
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

无（preferences 契约包）。

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Scene Alpha preferences 契约 | unit tests only | **否** |

### 9. 剩余风险

- 偏好差异须接入同一 Core benchmark（`X-SCENE-02`）。

---

## 26. X-SCENE-02

**日期**：2026-05-26  
**父包**：`X-SCENE-ALPHA`

### 1. 开发包名

`X-SCENE-02` — 三场景复用同一 `blank_shell` Core pipeline / benchmark。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `examples/benchmarks/scene_alpha_benchmark.json` | **新增** 3 cases |
| `core/workflows/blank_shell_pipeline.py` | `scene_preferences` 驱动动线选型；metrics 导出场景字段 |
| `core/benchmarks/runner.py` | `selected_circulation_strategy`、`preferences_scenario`、`preferences_path_contains` |
| `core/layout_engine/zone_splitter.py` | L 形走道 `path_surface` 并集切区 |
| `agents/scene_alpha_manifest.json` | 挂接 benchmark suite |
| `tests/core/test_benchmarks.py` | `test_x_scene_02_*` |
| `tests/core/test_zone_splitter.py` | along_wall 可用区断言 |

### 3. 关键设计说明

- 三场景共用 `pipeline: blank_shell` + 既有 workflow；`agents/` 无 Core 逻辑副本。
- `circulation_strategy_weights` 在 pipeline 内选 Top-1（与 X-SCENE-01 单测一致）。
- `zone_splitter` 对多段 `path_surface` 取并集 bbox，避免 along_wall 只按首段切区导致放置失败。

### 4. 新增/修改测试

- **317 tests OK**
- `test_x_scene_02_scene_alpha_multi_scene_benchmark`

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.agents.test_scene_preferences tests.core.test_benchmarks.BenchmarkRunnerTests.test_x_scene_02_scene_alpha_multi_scene_benchmark -v
& $py scripts\run_benchmark_suite.py examples\benchmarks\scene_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\x_scene_02
```

3/3 pass；`selected_circulation_strategy`：office `straight_spine`、residential `along_wall`、restaurant `l_spine`。

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/x_scene_02/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 三场景 blank_shell benchmark | `benchmark_pass_non_cad` | **否** |

### 9. 剩余风险

- 下一小包 `X-SCENE-03`：边界扫描；仍不能把 non-CAD pass 说成几何已验证。

---

## 27. X-SCENE-03

**日期**：2026-05-26  
**父包**：`X-SCENE-ALPHA`

### 1. 开发包名

`X-SCENE-03` — 加强 Scene Agent 边界扫描。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/agents/scene_boundary_scan.py` | **新增** 静态扫描器 |
| `tests/agents/test_scene_agent_boundaries.py` | `test_x_scene_03_*`、接入扫描器 |
| `agents/SCENE_AGENT_RULES.md` | 边界扫描章节 |
| `docs/verification/scene_alpha_agent_boundaries.md` | **新增** |
| `agents/residential/rules.md`、`agents/restaurant/rules.md` | Core 边界表述补强 |

### 3. 关键设计说明

- `agents/` 不得含 `*.py`；禁止 CAD 执行、回读、几何库、blank-shell pipeline 实现符号及 `from core.*` 实现导入。
- `SCENE_AGENT_RULES.md` 为禁止项目录文档，扫描时排除以免自引用误报。
- 合成违规样例测试确保扫描器可检出越界。

### 4. 新增/修改测试

- **322 tests OK**
- `test_x_scene_03_agent_tree_passes_boundary_scan` 等

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.agents.test_scene_agent_boundaries tests.agents.test_scene_preferences -v
```

0 violations on `agents/` tree.

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

无（静态边界包）。

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Scene Agent 边界扫描 | unit tests + static scan | **否** |

### 9. 剩余风险

- 静态子串扫描不能替代 runtime 审计；下一小包 `X-SCENE-04` 补解释模板与交接。

---

## 28. X-SCENE-04

**日期**：2026-05-26  
**父包**：`X-SCENE-ALPHA`

### 1. 开发包名

`X-SCENE-04` — 场景解释模板与交接（偏好如何影响 Core）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/agents/scene_explanation.py` | **新增** `build_scene_explanation()` |
| `docs/verification/scene_alpha_explanation_template.md` | **新增** |
| `tests/agents/test_scene_explanation.py` | **新增** `test_x_scene_04_*` |
| `agents/office|residential|restaurant/rules.md` | Preference→Core + 不可声称 |
| `docs/onboarding/first-handoff.md` | Scene Alpha 接手段 |
| `core/agents/scene_boundary_scan.py` | `rules.md` 文档引用例外 |

### 3. 关键设计说明

- 场景层只解释偏好如何进入 Core（path_generation、blank_shell_pipeline 等），不声称独立 Agent 大脑。
- `rules.md` 可写 Core 入口名；`preferences.json` 仍受完整边界扫描。

### 4. 新增/修改测试

- **326 tests OK**

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.agents.test_scene_explanation -v
& $py scripts\run_benchmark_suite.py examples\benchmarks\scene_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\x_scene_04
```

3/3 pass。

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/x_scene_04/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Scene Alpha 解释模板 | docs + unit tests + non-CAD benchmark | **否** |

### 9. 剩余风险

- 下一小包 `X-SCENE-05`：父包总验收与状态收口。

---

## 29. X-SCENE-05

**日期**：2026-05-26  
**父包**：`X-SCENE-ALPHA`（**父包 5/5 收口**）

### 1. 开发包名

`X-SCENE-05` — Scene Alpha 总验收与状态同步。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `docs/verification/scene_alpha_acceptance.md` | **新增** 父包可声称/不可声称 |
| `tests/agents/test_scene_alpha_acceptance.py` | **新增** `test_x_scene_05_*` |
| `agents/scene_alpha_manifest.json` | `acceptance_doc`、`parent_package_status` |
| `docs/planning/phase-x-scene-agent-alpha-plan.md` | 退出标准已满足 |
| `CORE_*` / `CAD_AGENT_*` / `phase-r-rebirth-implementation-plan.md` | 父包收口 |

### 3. 关键设计说明

- 汇总 01–04：preferences 差异、三场景 benchmark、边界扫描、解释模板。
- **可声称**三场景复用同一 Core `blank_shell` pipeline（non-CAD）。
- **不可声称** `geometry_verified`、Scene Agent 产品完成。

### 4. 新增/修改测试

- **332 tests OK**；`test_scene_alpha_acceptance`（6 cases）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.agents.test_scene_alpha_acceptance tests.agents -v
& $py -m unittest discover -s tests -p test_*.py -q
& $py scripts\run_benchmark_suite.py examples\benchmarks\scene_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\x_scene_05
```

3/3 pass；全量 **332 tests OK**。

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/x_scene_05/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| `X-SCENE-ALPHA` 父包收口 | non-CAD benchmark + agent tests + static scan | **否** |

### 9. 剩余风险

- 后置主线见 `CORE_RESTRUCTURE_PLAN.md`（真实 CAD 扩展、项目样本、Scene Beta 等）。

---

## 父包收口：`X-SCENE-ALPHA`（5/5）

| 小包 | 状态 |
| --- | --- |
| X-SCENE-01 | ✅ preferences 契约 |
| X-SCENE-02 | ✅ 三场景 benchmark |
| X-SCENE-03 | ✅ 边界扫描 |
| X-SCENE-04 | ✅ 解释模板 |
| X-SCENE-05 | ✅ 总验收 |

**统一证据**：`docs/verification/scene_alpha_acceptance.md`；`332 tests OK`；scene alpha benchmark `readback_geometry_verified_count=0`。

---

## 30. BETA-CAD-BLOCK-01

**日期**：2026-05-26  
**父包**：后置主线「真实 CAD 能力扩展」

### 1. 开发包名

`BETA-CAD-BLOCK-01` — 受控 block beta：多锚点、rotation、uniform scale。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `examples/plans/block_alpha_beta_suite.json` | **新增** 8 cases |
| `core/verification/block_alpha_beta_suite.py` | **新增** runner |
| `scripts/run_block_alpha_beta_suite.py` | **新增** CLI |
| `tests/core/test_block_alpha_beta_suite.py` | **新增** |
| `docs/verification/beta_cad_block_01_boundaries.md` | **新增** |

### 3. 关键设计说明

- 仍仅限 `controlled-test-block-001` / `CODEX_PREVIEW`；uniform scale only。
- 8 cases 覆盖 3 锚点、2 旋转、2 缩放、1 组合变换。

### 4. 新增/修改测试

- **336 tests OK**（+4）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_block_alpha_beta_suite -v
& $py scripts\run_block_alpha_beta_suite.py --output-root output\test_artifacts\block_alpha_beta\beta_cad_block_01
```

8/8 pass；`geometry_verified_count=0`。

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

`output/test_artifacts/block_alpha_beta/beta_cad_block_01/block_alpha_beta_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Block transform beta (no-CAD) | `dry_run_valid_plan_only` | **否** |

### 9. 剩余风险

- 真实 CAD 多变换 readback 留给 `BETA-CAD-BLOCK-02` 及后续。

---

## 31. BETA-CAD-BLOCK-02

**日期**：2026-05-26  
**父包**：后置主线「真实 CAD 能力扩展」

### 1. 开发包名

`BETA-CAD-BLOCK-02` — 受控属性块 / tag readback 探针。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/block_attribute_probe.py` | **新增** |
| `core/verification/inspect_dwg.py` | `GetAttributes()` 归一化 |
| `core/verification/block_alpha_validation.py` | 合并 attribute 判定 |
| `core/plan_engine/block_alpha_plan.py` | `attribute_readback_probe` 校验 |
| `examples/plans/insert_block_alpha_attribute_probe.json` | **新增** |
| `tests/core/test_block_attribute_probe.py` | **新增** |

### 3. 关键设计说明

- 无 probe 标记 → attribute 检查 `not_run`（不误报）。
- 有 probe 但实体无 tag → `deferred` / `attribute_unverified`，禁止 `geometry_verified`。
- COM insert 仍拒绝 attributes 写入。

### 4. 新增/修改测试

- **344 tests OK**（+8）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_block_attribute_probe -v
```

### 6. 是否运行真实 CAD

**否**（模拟实体 + 报告逻辑；COM insert 仍 deferred）。

### 7. CAD 证据路径

无（探针逻辑包）。

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Attribute readback probe | unit tests + simulated entity | **否** |

### 9. 剩余风险

- 真实 CAD 受控属性块 DWG 与 COM 写入留给后续包。

---

## §32 `BETA-CAD-BLOCK-03` — Entity-Level Capability Probe Evidence

**日期**：2026-05-26  
**父包**：后置主线「真实 CAD 能力扩展」

### 1. 开发包名

`BETA-CAD-BLOCK-03` — hatch / polyline / layer mapping 受控写读探针（entity-level evidence）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/entity_level_evidence.py` | **新增** |
| `core/verification/cad_capability_probe.py` | `entity_evidence[]` + hatch deferred 槽位 |
| `core/verification/evidence_contract.py` | `hatch` 契约、`validate` 门槛 |
| `core/verification/inspect_dwg.py` | Hatch 归一化 |
| `docs/verification/beta_cad_block_03_boundaries.md` | **新增** |
| `tests/core/test_entity_level_probe.py` | **新增** |
| `tests/core/test_cad_capability_probe.py` | entity_evidence 断言 |
| `tests/core/test_cad_validation_runner.py` | probe payload 含 entity_evidence |

### 3. 关键设计说明

- polyline：写入点集 / closed / `layer_role=preview` → readback 对比 + layer mapping。
- hatch：仅结构化 **deferred**（`hatch_unverified`），无 COM 写入。
- `cad_capability_verified` 仍可通过（hatch deferred 不阻断）。

### 4. 新增/修改测试

- **350 tests OK**（+6）

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest discover -s tests -p "test_*.py" -q
# Ran 350 tests in 3.6s — OK
```

### 6. 是否运行真实 CAD

**否**（FakeCadDriver + 报告/门控逻辑）。

### 7. CAD 证据路径

无（non-CAD 单测）。

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Entity-level probe contract | unit tests + fake driver probe | **否**（hatch deferred；非用户 AutoCAD 会话） |

### 9. 剩余风险

- 真实 CAD hatch 写入/readback 留给后续包。
- 正式图层 / `drawing_standard_profile` 未覆盖（`BETA-CAD-BLOCK-04`）。

---

## §33 `BETA-CAD-BLOCK-04` — Drawing Standard Profile

**日期**：2026-05-26  
**父包**：后置主线「真实 CAD 能力扩展」

### 1. 开发包名

`BETA-CAD-BLOCK-04` — 最小 `drawing_standard_profile` 与 role→预览层/样式映射。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/drawing_standard/drawing_standard_profile.py` | **新增** |
| `libraries/drawing_standards/codex_preview_beta.json` | **新增** |
| `libraries/layer_presets/codex_preview_beta.json` | **新增** |
| `core/schemas/drawing_standard_profile.schema.json` | **新增** |
| `core/schemas/layer_preset.schema.json` | **新增** |
| `core/verification/drawing_standard_beta_suite.py` | **新增** |
| `examples/plans/drawing_standard_beta_suite.json` | **新增** |
| `scripts/run_drawing_standard_beta_suite.py` | **新增** |
| `core/plan_engine/block_alpha_plan.py` | dry-run 支持 profile |
| `core/verification/entity_level_evidence.py` | profile layer mapping |

### 3. 关键设计说明

- `preview_only`：CAD 执行一律 `CODEX_PREVIEW`；`A-FURN` 等为语义层。
- `object_role_bindings` + `resolve_object_role` / `apply_drawing_standard_to_plan`。
- 6-case beta suite：role 解析 + block insert dry-run + primitive 样式。

### 4. 新增/修改测试

- **359 tests OK**（+9）

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest discover -s tests -p "test_*.py" -q
# Ran 359 tests — OK
```

### 6. 是否运行真实 CAD

**否**（schema + dry-run + fake 逻辑）。

### 7. CAD 证据路径

无（non-CAD）。artifact：`output/test_artifacts/drawing_standard_beta/beta_cad_block_04/`。

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Drawing standard profile beta | schema + dry-run suite | **否** |

### 9. 剩余风险

- 正式图层写入、公司制图标准、真实 CAD 样式仍 deferred（`BETA-CAD-BLOCK-05` 汇总边界）。

---

## §34 `BETA-CAD-BLOCK-05` — CAD Beta 证据 Rollup（父包收口）

**日期**：2026-05-26  
**父包**：后置主线「真实 CAD 能力扩展」**5/5 收口**

### 1. 开发包名

`BETA-CAD-BLOCK-05` — 汇总 01–04 non-CAD 证据 + 不可声称边界。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/cad_beta_evidence_rollup.py` | **新增** |
| `core/verification/fake_cad_driver.py` | **新增**（自 probe 测试抽出） |
| `scripts/run_cad_beta_evidence_rollup.py` | **新增** |
| `docs/verification/beta_cad_block_acceptance.md` | **新增** |
| `docs/verification/beta_cad_block_evidence_rollup.md` | **新增** |
| `docs/verification/beta_cad_block_05_boundaries.md` | **新增** |
| `tests/core/test_cad_beta_block_acceptance.py` | **新增** |

### 3. 关键设计说明

- rollup 依次执行 block alpha suite、attribute 合成探针、Fake capability probe、drawing standard suite、文档包校验。
- `evidence_summary.geometry_verified_count` 恒为 0；真实 CAD 仅 `real_cad_reference` 路径引用。

### 4. 新增/修改测试

- **362 tests OK**（+3）

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_cad_beta_block_acceptance -v
& $py scripts\run_cad_beta_evidence_rollup.py
```

### 6. 是否运行真实 CAD

**否**（rollup non-CAD；引用历史 validation 路径不重跑 COM）。

### 7. CAD 证据路径

`output/test_artifacts/cad_beta_evidence/beta_cad_block_05/cad_beta_evidence_rollup.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| BETA-CAD-BLOCK 父包 rollup | machine rollup + acceptance doc | **否** |

### 9. 剩余风险

- 正式图层 / 公司块库 / hatch 真实 CAD 仍 deferred；见 `BETA-PROJECT-SAMPLE` 后置主线。

---

## §35 `BETA-PROJECT-SAMPLE-01` — 脱敏样本目录协议

**日期**：2026-05-26  
**父包**：后置主线「真实项目样本闭环」

### 1. 开发包名

`BETA-PROJECT-SAMPLE-01` — `projects/` 脱敏样本目录协议与 manifest 扫描。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `projects/README.md` | 扩展六大章节协议 |
| `projects/sample_blank_shell/sample.manifest.json` | **新增** |
| `projects/sample_blank_shell/README.md` | **新增** |
| `core/project_samples/protocol.py` | **新增** |
| `core/schemas/project_sample_manifest.schema.json` | **新增** |
| `scripts/run_project_sample_protocol_scan.py` | **新增** |
| `docs/verification/beta_project_sample_01_boundaries.md` | **新增** |

### 3. 关键设计说明

- 每样本：`README.md` + `sample.manifest.json` + `input/` + `expected/expected_notes.md`。
- 禁止提交 `.dwg` / `.dxf`；`evidence_claim` 默认 `non_cad_pipeline_only`。

### 4. 新增/修改测试

- **366 tests OK**（+4）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_project_sample_protocol -v
& $py scripts\run_project_sample_protocol_scan.py
```

### 6. 是否运行真实 CAD

**否**（文档与目录协议 only）。

### 7. CAD 证据路径

`output/test_artifacts/project_samples/beta_project_sample_01/protocol_scan.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Sample protocol scan pass | manifest schema + directory scan | **否** |

### 9. 剩余风险

- 尚无端到端样本 workflow/benchmark（`BETA-PROJECT-SAMPLE-02` 起）。

---

## §36 `BETA-PROJECT-SAMPLE-02` — 样本 Shell / Project Model Fixture

**日期**：2026-05-26  
**父包**：后置主线「真实项目样本闭环」

### 1. 开发包名

`BETA-PROJECT-SAMPLE-02` — `sample_blank_shell` shell + PROJECT_MODEL 金样与 manifest loader。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/project_samples/loader.py` | **新增** |
| `projects/sample_blank_shell/fixtures/` | brief + drawing |
| `projects/sample_blank_shell/expected/project_model.expected.json` | **新增** |
| `projects/sample_blank_shell/sample.manifest.json` | 扩展 input_files |
| `tests/core/test_project_sample_loader.py` | **新增** |

### 3. 关键设计说明

- `load_sample_inputs` 先跑协议扫描再按 manifest 加载。
- `build_sample_project_model` = brief + drawing + shell → `PROJECT_MODEL`。
- 金样全量 equality + schema 校验。

### 4. 新增/修改测试

- **371 tests OK**（+5）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_project_sample_loader -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

无（non-CAD fixture / builder）

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Sample PROJECT_MODEL fixture | loader tests + golden JSON | **否** |

### 9. 剩余风险

- 尚未有样本级 workflow / CAD_PLAN 输出（`BETA-PROJECT-SAMPLE-03`）。

---

## §37 `BETA-PROJECT-SAMPLE-03` — 样本 Workflow 输出

**日期**：2026-05-26  
**父包**：后置主线「真实项目样本闭环」

### 1. 开发包名

`BETA-PROJECT-SAMPLE-03` — `sample_blank_shell` blank-shell workflow → CAD_PLAN / dry-run / verification。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `examples/workflows/sample_blank_shell_project_loop.json` | **新增** |
| `core/project_samples/workflow.py` | **新增** |
| `scripts/run_project_sample_workflow.py` | **新增** |
| `tests/core/test_project_sample_workflow.py` | **新增** |

### 3. 关键设计说明

- inputs 指向 `projects/sample_blank_shell/` fixtures。
- 契约：`dry_run valid`、`verification unverified`、`CODEX_PREVIEW` layer。
- `sample_workflow_report.json` 固定 `geometry_verified: false`。

### 4. 新增/修改测试

- **373 tests OK**（+2）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_project_sample_workflow -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/project_samples/beta_project_sample_03/`（含 `cad_plan.json`、`dry_run_report.json`、`verification_report.json`）

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Sample workflow non-CAD | pipeline artifacts + contract validator | **否** |

### 9. 剩余风险

- 未纳入 benchmark（已由 `BETA-PROJECT-SAMPLE-04` 收口）；无真实 CAD readback（`05`）。

---

## §38 `BETA-PROJECT-SAMPLE-04` — 样本 Benchmark

**日期**：2026-05-26  
**父包**：后置主线「真实项目样本闭环」

### 1. 开发包名

`BETA-PROJECT-SAMPLE-04` — 将 `projects/` 路径样本 workflow 纳入 benchmark（成功 + structured blocked）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `projects/sample_blank_shell_too_small/` | **新增**（过小 shell + manifest + fixtures） |
| `examples/workflows/sample_blank_shell_too_small_loop.json` | **新增** |
| `examples/benchmarks/project_sample_benchmark.json` | **新增**（2 cases） |
| `core/project_samples/benchmark.py` | **新增** |
| `scripts/run_project_sample_benchmark.py` | **新增** |
| `tests/core/test_project_sample_benchmark.py` | **新增** |
| `docs/verification/beta_project_sample_04_boundaries.md` | **新增** |

### 3. 关键设计说明

- **pass**：`sample_blank_shell_project_loop` → `benchmark_pass_non_cad`，`cad_plan_count≥5`。
- **blocked**：过小 shell + `require_all_placed` → `blocked_expected_non_cad`，`cad_plan_count=0`。
- `evidence_summary.readback_geometry_verified_count=0`；禁止把 benchmark pass 当成几何已验证。

### 4. 新增/修改测试

- **377 tests OK**（+4）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_project_sample_benchmark -v
& $py scripts\run_project_sample_benchmark.py
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/beta_project_sample_04/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Sample benchmark pass | `benchmark_pass_non_cad` | **否** |
| Sample benchmark blocked | `blocked_expected_non_cad` | **否** |

### 9. 剩余风险

- 无真实 CAD `CODEX_PREVIEW` readback（已由 `BETA-PROJECT-SAMPLE-05` 提供 CLI；unittest 使用 `FakeCadDriver`）。

---

## §39 `BETA-PROJECT-SAMPLE-05` — 样本可选真实 CAD 验证

**日期**：2026-05-26  
**父包**：后置主线「真实项目样本闭环」收口

### 1. 开发包名

`BETA-PROJECT-SAMPLE-05` — `sample_blank_shell` 多 CAD_PLAN 在 `CODEX_PREVIEW` 批量落图 + created-handle readback。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/project_samples/cad_check.py` | **新增** |
| `scripts/run_project_sample_cad_check.py` | **新增** |
| `tests/core/test_project_sample_cad_check.py` | **新增** |
| `docs/verification/beta_project_sample_05_boundaries.md` | **新增** |
| `docs/verification/beta_project_sample_acceptance.md` | **新增**（父包 01–05） |

### 3. 关键设计说明

- 复用 `execute_plan_batch`；默认偏移 `[28000, 12000, 0]` 避开既有 benchmark 区域。
- `--no-cad` → `deferred_cad_readback_required`；真实 CAD 需用户 AutoCAD 会话。
- `safety` 固定：不保存 DWG、不删实体、不改正式图层。

### 4. 新增/修改测试

- **381 tests OK**（+4）；`FakeCadDriver` → `geometry_verified`。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_project_sample_cad_check -v
& $py scripts\run_project_sample_cad_check.py --no-cad
```

### 6. 是否运行真实 CAD

**否**（CI / 本回合）；CLI 支持用户会话下真实 CAD。

### 7. CAD 证据路径

- deferred：`output/validation_runs/beta-project-sample-05-cad/project_sample_cad_check_report.json`
- 真实 CAD：同上路径，`status=geometry_verified`（需用户本地执行）

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Fake driver batch readback | `readback_geometry_verified` | **是**（测试环境） |
| `--no-cad` CLI | `deferred_cad_readback_required` | **否** |

### 9. 剩余风险

- 本回合未在用户 AutoCAD 会话复验真实 COM；不得把 deferred CLI 当成几何已验证。

---

## §40 `BETA-PROPOSAL-01` — 候选评分与排序原因

**日期**：2026-05-26  
**父包**：后置主线「多方案设计与交互确认」

### 1. 开发包名

`BETA-PROPOSAL-01` — 固化 `score_breakdown` 与结构化 `ranking_reasons`。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/proposal_engine/candidate_scoring.py` | **新增** |
| `core/schemas/proposal_candidate_scoring.schema.json` | **新增** |
| `core/schemas/design_proposal.schema.json` | 扩展 candidates |
| `core/proposal_engine/proposal_comparison.py` | 接入 scoring |
| `core/proposal_engine/design_proposal.py` | 接入 scoring |
| `tests/core/test_proposal_candidate_scoring.py` | **新增** |
| `examples/design_proposals/*.json` | 补全 scoring 字段 |

### 3. 关键设计说明

- `score_breakdown.components`：`layout_base` / `check_penalty` / `preference_boost`。
- `ranking_reasons[].code` 受控词表（如 `highest_weighted_score`、`scene_preference_boost`）。
- layout comparison 与 design proposal 候选均可机器断言。

### 4. 新增/修改测试

- **384 tests OK**（+3）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_proposal_candidate_scoring -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

无（non-CAD proposal 层）

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Proposal scoring contract | schema + unit tests | **否** |

### 9. 剩余风险

- 尚无 benchmark 级对比摘要硬断言（`BETA-PROPOSAL-02`）；无用户确认流（`03`–`05`）。

---

## §41 `BETA-PROPOSAL-02` — 候选对比摘要 Benchmark

**日期**：2026-05-26  
**父包**：后置主线「多方案设计与交互确认」

### 1. 开发包名

`BETA-PROPOSAL-02` — `proposal_comparison_summary` + benchmark 硬断言。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/proposal_engine/comparison_summary.py` | **新增** |
| `core/schemas/proposal_comparison_summary.schema.json` | **新增** |
| `examples/benchmarks/proposal_comparison_benchmark.json` | **新增**（4 cases） |
| `core/workflows/blank_shell_pipeline.py` | summary artifact + metrics |
| `core/benchmarks/runner.py` | 新断言键 + `placed_count` |
| `tests/core/test_proposal_comparison_benchmark.py` | **新增** |

### 3. 关键设计说明

- 从 `comparison_detail` 提炼四类摘要区块；`ranking_reason_codes` 聚合结构化 reason code。
- Benchmark 断言：`requires_proposal_comparison_summary`、`proposal_comparison_summary_minimums`、`contains_ranking_reason_code` 等。

### 4. 新增/修改测试

- **387 tests OK**（+3）；benchmark 4/4 pass。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_proposal_comparison_benchmark -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/beta_proposal_02/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Comparison summary benchmark | `benchmark_pass_non_cad` | **否** |

### 9. 剩余风险

- 无局部修改重算 CAD_PLAN（`BETA-PROPOSAL-04`–`05`）。

---

## §42 `BETA-PROPOSAL-03` — 用户确认输入 Schema

**日期**：2026-05-26  
**父包**：后置主线「多方案设计与交互确认」

### 1. 开发包名

`BETA-PROPOSAL-03` — `PROPOSAL_USER_CONFIRMATION` schema + apply round-trip。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/schemas/proposal_user_confirmation.schema.json` | **新增** |
| `core/proposal_engine/user_confirmation.py` | **新增** |
| `examples/confirmations/*.json` | **新增** |
| `scripts/apply_proposal_user_confirmation.py` | **新增** |
| `tests/core/test_proposal_user_confirmation.py` | **新增** |

### 3. 关键设计说明

- `action`: `accept` / `accept_with_risks` / `reject_all`。
- `rejected_candidates[].reason_code` 受控词表；`local_preferences` 承载权重与备注。
- `apply_user_confirmation` 写入 `user_confirmation` 并更新 `confirmed_candidate_id`。

### 4. 新增/修改测试

- **393 tests OK**（+6）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_proposal_user_confirmation -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

无

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Confirmation schema round-trip | unit tests | **否** |

### 9. 剩余风险

- blank-shell circulation `candidate_id` 与 layout `candidate_id` 对齐仍待 `04`/`05` 深化。

---

## §43 `BETA-PROPOSAL-04` — 局部修改重算 CAD_PLAN

**日期**：2026-05-26  
**父包**：后置主线「多方案设计与交互确认」

### 1. 开发包名

`BETA-PROPOSAL-04` — placement 局部修改后仅重算下游 CAD_PLAN 产物。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/proposal_engine/partial_replan.py` | **新增** |
| `scripts/run_proposal_partial_replan.py` | **新增** |
| `tests/core/test_proposal_partial_replan.py` | **新增** |
| `docs/verification/beta_proposal_04_boundaries.md` | **新增** |

### 3. 关键设计说明

- `modules_skipped`：shell / project / circulation / candidate_sets / function_zones。
- `placement_offsets` 按 `object_spec_id` 应用；可来自 CLI 或 `user_confirmation.local_preferences`。
- `ensure_layout_confirmed_candidate_id` 桥接 circulation 与 layout candidate id。

### 4. 新增/修改测试

- **395 tests OK**（+2）；上游 artifact SHA256 不变回归。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_proposal_partial_replan -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/proposal_partial_replan/retail_baseline/partial_replan_report.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Partial replan non-CAD | dry-run valid + module skip report | **否** |

### 9. 剩余风险

- 未选方案证据归档与确认后受控落图（`BETA-PROPOSAL-05`）。

---

## §44 `BETA-PROPOSAL-05` / 父包 `BETA-PROPOSAL` 收口

**日期**：2026-05-26  
**父包**：后置主线「多方案设计与交互确认」

### 1. 开发包名

`BETA-PROPOSAL-05` — 确认后受控 CAD_PLAN bundle + 未选方案证据；父包 01–05 收口。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/proposal_engine/confirmed_finalize.py` | **新增** |
| `core/schemas/confirmed_cad_plan_bundle.schema.json` | **新增** |
| `examples/benchmarks/proposal_confirmed_benchmark.json` | **新增** |
| `core/proposal_engine/confirmed_benchmark.py` | **新增** |
| `core/proposal_engine/proposal_acceptance.py` | **新增** |
| `tests/core/test_proposal_confirmed_*.py` | **新增** |

### 3. 关键设计说明

- `finalize_confirmed_cad_plans`：确认 → partial replan → validate + dry-run → bundle。
- `unselected_candidate_evidence` 保留未选候选、拒绝原因、comparison 摘要。
- 受控策略：`CODEX_PREVIEW`、`needs_confirmation=false`、不保存 DWG。

### 4. 新增/修改测试

- **400 tests OK**（+5）；confirmed benchmark 2/2 pass。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_proposal_confirmed_finalize tests.core.test_proposal_confirmed_benchmark -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/beta_proposal_05/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Confirmed CAD_PLAN bundle | validate + dry_run valid | **否** |
| 未选方案证据 | `unselected_candidate_evidence.json` | **否** |

### 9. 剩余风险

- 真实 CAD 落图与 created-handle readback 不在本父包范围。

---

## §45 `BETA-DRAWING-READ-01` — 只读 DWG entity summary

**日期**：2026-05-26  
**父包**：后置主线「自动读图 / 空壳识别」

### 1. 开发包名

`BETA-DRAWING-READ-01` — 只读 ModelSpace / fixture 实体汇总（层、类型、bbox、handle 样本）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/drawing_analysis/dwg_read_only.py` | **新增** |
| `core/schemas/dwg_entity_summary.schema.json` | **新增** |
| `examples/drawing_read/sample_modelspace_entities.json` | **新增** |
| `scripts/run_dwg_entity_summary.py` | **新增** |
| `tests/core/test_dwg_read_only.py` | **新增** |
| `core/verification/fake_cad_driver.py` | `snapshot_modelspace()` |
| `docs/verification/beta_drawing_read_01_boundaries.md` | **新增** |

### 3. 关键设计说明

- 只读策略：`READ_ONLY_POLICY` 禁止 mutate/save/write；默认 fixture，可选 `--use-cad` 读活动 AutoCAD。
- `build_dwg_entity_summary` 聚合 `type_counts`、`layer_statistics`、`bbox_union`、`handles_sample`。
- 不解析任意 DWG 文件路径；不输出墙/门/柱语义（留给 READ-02）。

### 4. 新增/修改测试

- **404 tests OK**（+4）；`test_dwg_read_only.py` schema + 计数 + FakeCadDriver。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_dwg_read_only -v
& $py scripts\run_dwg_entity_summary.py
```

### 6. 是否运行真实 CAD

**否**（默认 fixture；`--use-cad` 未在本包验收中执行）

### 7. CAD 证据路径

`output/test_artifacts/drawing_read/beta_drawing_read_01/summary.json`（CLI 默认输出）

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Entity summary fixture | schema + layer/type counts | **否** |
| 只读策略 | `read_only: true` + policy constants | **否** |

### 9. 剩余风险

- 未做墙/门/柱语义提取（`BETA-DRAWING-READ-02`）。
- 真实大 DWG 全 ModelSpace 扫描性能与层过滤待后续 benchmark 覆盖。

---

## §46 `BETA-DRAWING-READ-02` — 几何特征候选提取

**日期**：2026-05-26  
**父包**：后置主线「自动读图 / 空壳识别」

### 1. 开发包名

`BETA-DRAWING-READ-02` — 从规范化实体 + entity summary 启发式提取墙线段、门洞、柱、禁放区候选。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/drawing_analysis/geometry_candidates.py` | **新增** |
| `core/schemas/dwg_geometry_candidates.schema.json` | **新增** |
| `examples/drawing_read/sample_geometry_feature_fixture.json` | **新增** |
| `scripts/run_geometry_candidates.py` | **新增** |
| `tests/core/test_geometry_candidates.py` | **新增** |
| `docs/verification/beta_drawing_read_02_boundaries.md` | **新增** |

### 3. 关键设计说明

- 层名 / 块名启发式 + summary 层内 line 主导辅助；每项含 `confidence` 与 `detection_rule`。
- 输出 `dwg_geometry_candidates`；**不**生成 `SHELL_MODEL`，不驱动落 CAD。
- `read_geometry_candidates_from_fixture` 内部复用 READ-01 summary 作为 `entity_summary_ref`。

### 4. 新增/修改测试

- **407 tests OK**（+3）；fixture 断言 4 墙 + 1 门 + 1 柱 + 1 禁放区。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_geometry_candidates -v
& $py scripts\run_geometry_candidates.py
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/drawing_read/beta_drawing_read_02/candidates.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Geometry candidates fixture | schema + counts | **否** |
| 启发式提取 | layer/block heuristics only | **否** |

### 9. 剩余风险

- 置信度与人工确认点未机器化（`BETA-DRAWING-READ-03`）。
- 未确认候选不得进入 blank-shell 落图。

---

## §47 `BETA-DRAWING-READ-03` — Shell 候选置信度报告

**日期**：2026-05-26  
**父包**：后置主线「自动读图 / 空壳识别」

### 1. 开发包名

`BETA-DRAWING-READ-03` — 从几何候选汇总置信度、结构化缺口与人工确认点，输出草案 shell。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/drawing_analysis/shell_candidate_report.py` | **新增** |
| `core/schemas/shell_candidate_confidence_report.schema.json` | **新增** |
| `examples/drawing_read/sample_geometry_walls_only_fixture.json` | **新增** |
| `scripts/run_shell_candidate_report.py` | **新增** |
| `tests/core/test_shell_candidate_report.py` | **新增** |
| `docs/verification/beta_drawing_read_03_boundaries.md` | **新增** |

### 3. 关键设计说明

- `confidence` 五维分数 + `shell_candidate_draft`（boundary / openings / obstacles / no_place）。
- `gaps` 含 `missing_entry_opening` 等 blocker；`human_confirmation_items` 含 `confirm_boundary_bbox` / `resolve_gap`。
- `ready_for_human_confirmation_file`：无 blocker 且 overall ≥ 0.65；**不**等同可落 CAD。

### 4. 新增/修改测试

- **410 tests OK**（+3）；完整 fixture ready=true；缺门洞 fixture blocker。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_shell_candidate_report -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/drawing_read/beta_drawing_read_03/report.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Confidence report complete fixture | schema + confidence keys | **否** |
| Blocker gap incomplete fixture | `missing_entry_opening` | **否** |

### 9. 剩余风险

- 人工确认文件 → `SHELL_MODEL` 回写未实现（`BETA-DRAWING-READ-04`）。

---

## §48 `BETA-DRAWING-READ-04` — 人工确认回写 SHELL_MODEL

**日期**：2026-05-26  
**父包**：后置主线「自动读图 / 空壳识别」

### 1. 开发包名

`BETA-DRAWING-READ-04` — `shell_drawing_read_confirmation` 校验并合成可通过 `shell_loader` 的 `SHELL_MODEL`。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/drawing_analysis/shell_confirmation.py` | **新增** |
| `core/schemas/shell_drawing_read_confirmation.schema.json` | **新增** |
| `examples/drawing_read/sample_shell_drawing_read_confirmation.json` | **新增** |
| `scripts/apply_shell_drawing_read_confirmation.py` | **新增** |
| `tests/core/test_shell_confirmation.py` | **新增** |
| `docs/verification/beta_drawing_read_04_boundaries.md` | **新增** |

### 3. 关键设计说明

- `validate_confirmation_against_report`：必填 `confirmed_items` 覆盖 report `required` 项；`accept` 要求 `ready_for_human_confirmation_file`。
- `apply_shell_drawing_read_confirmation` → 临时 JSON → `load_manual_shell()`（bbox 内含校验）。
- `overrides.excluded_draft_ids` 可省略草案禁放区/障碍。

### 4. 新增/修改测试

- **414 tests OK**（+4）；`shell_model.schema.json` 校验通过。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_shell_confirmation -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/drawing_read/beta_drawing_read_04/shell_model.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| SHELL_MODEL from confirmation | shell_loader + schema | **否** |
| 缺必填确认项 | validation error | **否** |

### 9. 剩余风险

- 读图链路未 benchmark 化（`BETA-DRAWING-READ-05`）。
- SHELL_MODEL 进入 blank-shell 落图仍须单独 CAD 验证。

---

## §49 `BETA-DRAWING-READ-05` / 父包 `BETA-DRAWING-READ` 收口

**日期**：2026-05-26  
**父包**：后置主线「自动读图 / 空壳识别」

### 1. 开发包名

`BETA-DRAWING-READ-05` — 读图链路 benchmark；父包 READ-01..05 收口。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/drawing_analysis/drawing_read_benchmark.py` | **新增** |
| `examples/benchmarks/drawing_read_benchmark.json` | **新增** |
| `scripts/run_drawing_read_benchmark.py` | **新增** |
| `tests/core/test_drawing_read_benchmark.py` | **新增** |
| `docs/verification/beta_drawing_read_05_boundaries.md` | **新增** |
| `docs/verification/beta_drawing_read_acceptance.md` | **新增** |

### 3. 关键设计说明

- 串联 READ-02..04：`geometry_candidates` → `confidence_report` → 可选 `SHELL_MODEL` export。
- 失败样本输出 `structured_blockers`（如 `missing_entry_opening`）；`evidence_state=blocked_expected_non_cad`。
- `expected_evidence_summary` 机器断言：2 pass + 1 blocked。

### 4. 新增/修改测试

- **416 tests OK**（+2）；benchmark 3/3 pass。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_drawing_read_benchmark -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/beta_drawing_read_05/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Full chain pass | benchmark_pass_non_cad + shell export | **否** |
| Walls-only blocked | structured_blockers + blocked_expected_non_cad | **否** |

### 9. 剩余风险

- 真实 DWG / 大图纸读图未纳入 benchmark。
- SHELL_MODEL 进入 blank-shell 仍须单独 CAD 验证。

---

## §50 `BETA-SCENE-01` — Office Scene Beta

**日期**：2026-05-26  
**父包**：后置主线「场景 Agent Beta」

### 1. 开发包名

`BETA-SCENE-01` — office 场景 beta 偏好 + 统一 benchmark（对象 / 微场景 / 场景 / 失败）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/agents/scene_beta.py` | **新增** |
| `core/agents/office_scene_beta.py` | **新增** |
| `agents/scene_beta_manifest.json` | **新增** |
| `agents/office/preferences.json` | `scene_beta` + 扩展 object_preferences |
| `examples/benchmarks/office_scene_beta_benchmark.json` | **新增** |
| `scripts/run_office_scene_beta_benchmark.py` | **新增** |
| `tests/agents/test_scene_beta_office.py` | **新增** |

### 3. 关键设计说明

- Scene 层仅偏好与 benchmark 编排；复用 Core `object_spec` / `composition_spec` / `blank_shell`。
- 9 cases 含 `case_tier` 四类；blank-shell 断言 `preferences_scenario=office` 与 `straight_spine`。
- 失败样本保留 `blocked_expected_non_cad` 与结构化 `failure_category`。

### 4. 新增/修改测试

- **418 tests OK**（+2）；benchmark 9/9 pass；evidence 7 pass + 2 blocked。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.agents.test_scene_beta_office -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/beta_scene_01/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Office beta benchmark | benchmark_pass_non_cad + blocked_expected | **否** |
| Scene beta 偏好契约 | manifest + preference validation | **否** |

### 9. 剩余风险

- residential / restaurant beta 未覆盖（`BETA-SCENE-02/03`）。
- 场景解释模板增强在 `BETA-SCENE-04`。

---

## §51 `BETA-SCENE-02` — Residential Scene Beta

**日期**：2026-05-26  
**父包**：后置主线「场景 Agent Beta」

### 1. 开发包名

`BETA-SCENE-02` — residential 卧室 / 餐厅 / 收纳组合 + blank-shell benchmark。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/agents/scene_beta.py` | 扩展 residential 校验 |
| `core/agents/residential_scene_beta.py` | **新增** |
| `agents/residential/preferences.json` | `scene_beta` + 对象偏好扩展 |
| `examples/benchmarks/residential_scene_beta_benchmark.json` | **新增** |
| `agents/scene_beta_manifest.json` | 增加 residential |
| `tests/agents/test_scene_beta_residential.py` | **新增** |

### 3. 关键设计说明

- `case_tier`：object / bedroom / dining / storage / blank_shell / failure。
- blank-shell 断言 `along_wall` 与 `preferences_scenario=residential`。
- 复用 Core `bedroom_bed_rug`、`dining_table_set` composition。

### 4. 新增/修改测试

- **420 tests OK**（+2）；benchmark 8/8 pass；7 pass + 1 blocked。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.agents.test_scene_beta_residential -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/beta_scene_02/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Residential beta benchmark | benchmark_pass_non_cad + blocked | **否** |

### 9. 剩余风险

- restaurant/commercial beta 未覆盖（`BETA-SCENE-03`）。

---

## §52 `BETA-SCENE-03` — Restaurant / Commercial Scene Beta

**日期**：2026-05-26  
**父包**：后置主线「场景 Agent Beta」

### 1. 开发包名

`BETA-SCENE-03` — restaurant 入口 / 堂食桌椅 / 后场收纳 + blank-shell benchmark。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/agents/scene_beta.py` | 扩展 restaurant 校验 |
| `core/agents/restaurant_scene_beta.py` | **新增** |
| `agents/restaurant/preferences.json` | `scene_beta` |
| `examples/benchmarks/restaurant_scene_beta_benchmark.json` | **新增** |
| `agents/scene_beta_manifest.json` | 增加 restaurant |

### 3. 关键设计说明

- `case_tier`：object / entrance / seating / back_of_house / blank_shell / failure。
- blank-shell 断言 `l_spine`、`shell-restaurant-small-front`、`no_place_zone_count`。
- 入口组合复用 `entry_reception_clearance`；堂食复用 `dining_table_set`。

### 4. 新增/修改测试

- **422 tests OK**（+2）；benchmark 8/8 pass。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.agents.test_scene_beta_restaurant -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/beta_scene_03/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Restaurant beta benchmark | benchmark_pass_non_cad + blocked | **否** |

### 9. 剩余风险

- 餐饮专用 composition 模板仍偏少（`BETA-SCENE-04` 解释模板）。

---

## Codex 深度全量安全复盘（非 PlanMD 开发包）

**日期**：2026-05-26  
**性质**：Cursor 大改后的安全审计、Bug 筛查、维护性拆分与证据门禁加固；不是新的功能开发包。

### 1. 开发包名

无（Codex audit / hardening）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/benchmarks/runner.py` / `core/benchmarks/expectations.py` | 拆出 expected / evidence summary 比对；强制 case evidence triplet |
| `core/proposal_engine/confirmed_benchmark.py` | 输出并校验 `evidence_summary` |
| `core/verification/evidence_contract.py` / `evidence_vocabulary.py` | 拆出 evidence vocabulary |
| `core/project_samples/cad_check.py` | 修正 no-CAD / failure evidence vocabulary |
| `libraries/drawing_standards/codex_preview_beta.json` | 修正 `screenshot_role=not_applicable` |
| `core/composition_engine/preview.py` / `templates.py` | 拆出 SVG preview helper |
| `core/workflows/blank_shell_candidates.py` / `blank_shell_pipeline.py` | 拆出 candidate set 生成逻辑 |
| `tests/core/*` | 增补 evidence gate、项目样例、benchmark validation、CAD validation payload fixture 回归 |
| `CAD_AGENT_STATUS.md` / `CORE_STATUS.md` / `CAD_AGENT_CHANGELOG.md` / `CAD_AGENT_ISSUES.md` / `CORE_CONTEXT_BRIEF.md` | 同步复盘证据和风险记录 |

### 3. 关键设计说明

- benchmark pass 必须带机器可读 evidence triplet；summary 不匹配即失败。
- project sample / drawing standard 不允许临时发明 evidence 状态词。
- repo audit 的大文件 finding 用低风险职责拆分解决，保持原公开入口兼容。

### 4. 新增/修改测试

- 新增/扩展：benchmark expected evidence triplet、confirmed benchmark evidence summary、project sample CAD check failure vocabulary、drawing standard `screenshot_role`、benchmark validation、CAD validation payload fixture 拆分回归。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest discover -s tests -q
# 424 tests OK

& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
# 0 findings

& $py scripts\run_project_sample_benchmark.py
# pass, 2/2

& $py scripts\run_proposal_confirmed_benchmark.py
# pass, 2/2

& $py scripts\run_cad_beta_evidence_rollup.py
# pass, 5/5

& $py scripts\run_office_scene_beta_benchmark.py
& $py scripts\run_residential_scene_beta_benchmark.py
& $py scripts\run_restaurant_scene_beta_benchmark.py
# pass: 9/9, 8/8, 8/8
```

### 6. 是否运行真实 CAD

**否**。本轮只做 no-CAD / benchmark / fake-driver /静态与测试验证；未写入真实 DWG。

### 7. CAD 证据路径

- `output/test_artifacts/benchmarks/beta_project_sample_04/benchmark_summary.json`
- `output/test_artifacts/benchmarks/beta_proposal_05/benchmark_summary.json`
- `output/test_artifacts/cad_beta_evidence/beta_cad_block_05/`
- `output/test_artifacts/benchmarks/beta_scene_01/benchmark_summary.json`
- `output/test_artifacts/benchmarks/beta_scene_02/benchmark_summary.json`
- `output/test_artifacts/benchmarks/beta_scene_03/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 全量单测和静态审计通过 | test / repo_audit | **否** |
| benchmark evidence gate 已强制 triplet + summary | benchmark_pass_non_cad / blocked_expected_non_cad | **否** |
| project sample / proposal / scene beta 验收脚本通过 | non-CAD benchmark | **否** |

### 9. 剩余风险

- 本轮不新增真实 CAD `geometry_verified` 结论。
- `render_preview.py --check` ready 只说明截图工具可用；截图仍是 `visual_aid_only`。
- 真实项目 DWG、正式图层、公司块库和 ActiveDocument guard 仍是后续风险。

---

## Codex 维护 1-3 包（证据止血、基线同步、路径安全）

**日期**：2026-05-26  
**性质**：用户批准的“先止血、再加固”维护包；不是新的业务功能包。

### 1. 开发包名

`P0-EVIDENCE-TRUTH-FIX` + `BASELINE-SINGLE-SOURCE` + `PATH-AND-OUTPUT-SAFETY`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `scripts/run_project_sample_cad_check.py` | 新增 `--require-cad-verified`，deferred / failed 报告返回非 0 |
| `core/project_samples/protocol.py` / `loader.py` | manifest input path 必须留在样本目录内 |
| `core/benchmarks/runner.py` | benchmark `case_id` 安全 path segment；`output_root` 限制在 `output/` |
| `core/drawing_analysis/drawing_read_benchmark.py` | drawing-read `case_id` 与 `output_root` 边界加固 |
| `core/verification/cad_validation_runner.py` | `output_dir` 限制在 `output/`；清理 stale artifact 前验证派生产物边界 |
| `tests/core/*` | 增补 strict CAD evidence、manifest/path escape、output boundary 回归 |
| `CORE_CONTEXT_BRIEF.md` / `CORE_STATUS.md` / `CAD_AGENT_STATUS.md` / `CORE_RESTRUCTURE_PLAN.md` / `CAD_AGENT_CHANGELOG.md` / `CAD_AGENT_ISSUES.md` / `docs/verification/beta_project_sample_*` | 同步证据口径和风险记录 |

### 3. 关键设计说明

- `BETA-PROJECT-SAMPLE-05` 的 no-CAD 报告只能是 `deferred`，不能被当成真实 AutoCAD `geometry_verified`。
- 所有从 manifest、suite case、CLI output dir 派生的路径，必须先 resolve 并验证仍在预期边界内。
- benchmark/drawing-read case id 只允许作为单个 path segment，不允许 `../`、`\` 或绝对路径形态。

### 4. 新增/修改测试

- `test_cli_require_cad_verified_rejects_deferred_no_cad_report`
- `test_manifest_input_path_must_stay_inside_sample_directory`
- `test_scan_fails_when_manifest_input_escapes_sample_directory`
- benchmark / drawing-read unsafe `case_id` 与 output root 测试
- CAD validation output dir 边界测试

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_project_sample_cad_check tests.core.test_project_sample_loader tests.core.test_project_sample_protocol tests.core.test_benchmarks tests.core.test_drawing_read_benchmark tests.core.test_cad_validation_runner
# 48 tests OK

& $py -m unittest discover -s tests
# 432 tests OK

& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
# 0 findings

& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\codex-maintenance-fix-no-cad
# status=pass

& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\codex_maintenance_fix_blank_shell
# 8/8 pass

& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\codex_maintenance_fix_office_alpha
# 18/18 pass

& $py scripts\run_benchmark_suite.py examples\benchmarks\interior_delivery_benchmark.json --output-root output\test_artifacts\benchmarks\codex_maintenance_fix_interior_delivery
# 3/3 pass

& $py scripts\run_project_sample_cad_check.py --no-cad --require-cad-verified --output-dir output\validation_runs\codex-maintenance-project-sample-strict-no-cad
# expected exit 1; report status=deferred
```

### 6. 是否运行真实 CAD

**否**。本轮只做 no-CAD / fake-driver / benchmark / 单测验证；未写入真实 DWG。

### 7. CAD 证据路径

- `output\validation_runs\codex-maintenance-fix-no-cad\report.json`
- `output\validation_runs\codex-maintenance-project-sample-strict-no-cad\project_sample_cad_check_report.json`
- `output\test_artifacts\benchmarks\codex_maintenance_fix_blank_shell\benchmark_summary.json`
- `output\test_artifacts\benchmarks\codex_maintenance_fix_office_alpha\benchmark_summary.json`
- `output\test_artifacts\benchmarks\codex_maintenance_fix_interior_delivery\benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 全量单测与 repo audit 通过 | test / repo_audit | **否** |
| no-CAD validation 通过 | deferred_cad_readback_required / non-CAD gate | **否** |
| project sample strict mode 正确拒绝 deferred | negative evidence gate | **否** |
| blank-shell / office / interior benchmark 通过 | benchmark_pass_non_cad / blocked_expected_non_cad / invalid_configuration | **否** |

### 9. 剩余风险

- 本轮不新增真实 CAD `geometry_verified` 结论。
- `BETA-PROJECT-SAMPLE-05` 真实样本 CAD readback 仍需用户 AutoCAD 会话单独运行。
- ActiveDocument guard、正式图层保护和真实项目 DWG 仍属于后续安全加固范围。

---

## Codex 维护 4-7 包（结构整理、路径公共化、Schema registry、文档主从治理）

**日期**：2026-05-26  
**性质**：用户批准的 4-7 包结构整理和优化；承接 1-3 包“先止血、再加固”后的维护收口，不新增业务场景能力。

### 1. 开发包名

`STRUCTURE-GOVERNANCE-DRIFT-FIX` + `SHARED-PATH-SAFETY-CONSOLIDATION` + `SCHEMA-REGISTRY-CONSISTENCY` + `VALIDATION-GATE-CLEANUP`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/path_safety.py` | 新增公共路径安全 helper：project root、output root、safe path segment、relative boundary |
| `core/benchmarks/runner.py` / `core/drawing_analysis/drawing_read_benchmark.py` / `core/verification/cad_validation_runner.py` / `core/workflows/blank_shell_pipeline.py` / `core/capabilities/runners.py` | 替换分散路径判断，统一走 `core.path_safety` |
| `core/verification/block_alpha_beta_suite.py` / `drawing_standard_beta_suite.py` / `cad_beta_evidence_rollup.py` / `core/proposal_engine/*` | beta / proposal 输出目录和 case id 边界加固 |
| `core/project_samples/cad_check.py` | workflow output、CAD output 均限制在 project `output/` 下 |
| `scripts/run_composition_cad_check.py` | 在导入 / 连接 AutoCAD 前先验证 benchmark output root 和 output dir |
| `core/schemas/registry.py` | 登记所有 `core/schemas/*.schema.json` 并补齐模型识别 |
| `tests/core/*` / `tests/fixtures/invalid_models/*` | 增补路径越界、schema registry、文档治理和 non-CAD pipeline invalid 回归 |
| `CORE_CONTEXT_BRIEF.md` / `CORE_STATUS.md` / `CAD_AGENT_STATUS.md` / `CORE_RESTRUCTURE_PLAN.md` / `CAD_AGENT_CHANGELOG.md` / `CAD_AGENT_ISSUES.md` / 本文 | 同步 4-7 包证据、风险和唯一 PlanMD 口径 |

### 3. 关键设计说明

- 路径边界从各 runner 私有实现收敛为 `core.path_safety`，降低后续新增脚本漏检 output root / case id 的风险。
- 真实 CAD 相关脚本必须先验证路径，再连接 AutoCAD；参数非法时不应进入 COM 侧。
- `non_cad_pipeline` 对越界 workflow、越界 output、缺输入文件返回结构化 invalid / blocker，便于 benchmark 和交接机器判断。
- schema registry 以“文件存在即必须登记”为门禁，避免 schema 只停留在静态文档。
- handoff 只记录已完成包，不承载“下一包建议”或后置 Backlog 副表；优先级继续只以 `CORE_RESTRUCTURE_PLAN.md` 为准。

### 4. 新增/修改测试

- 路径边界：block alpha beta suite、drawing standard beta suite、CAD beta rollup、proposal confirmed benchmark、project sample CAD check、composition CAD check。
- schema registry：`test_every_core_schema_file_is_registered`，并补齐每个新增 schema 的 invalid fixture。
- 文档治理：`test_planmd_governance` 禁止 handoff / status / PlanMD 回流第二套计划短语。
- non-CAD pipeline：越界 output、越界 workflow input、缺 required input 返回 structured invalid。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_block_alpha_beta_suite tests.core.test_drawing_standard_beta_suite tests.core.test_cad_beta_block_acceptance tests.core.test_proposal_confirmed_benchmark tests.core.test_schema_validation tests.core.test_planmd_governance tests.core.test_non_cad_pipeline tests.core.test_project_sample_cad_check tests.core.test_composition_cad_check
# 46 tests OK

& $py -m unittest discover -s tests
# 450 tests OK

& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
# 0 findings

& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\codex-maintenance-4-7-no-cad
# status=pass
```

### 6. 是否运行真实 CAD

**否**。本轮只做 no-CAD / 单测 / repo audit / 文档治理验证；未连接 AutoCAD 写入真实 DWG。

### 7. CAD 证据路径

- `output\validation_runs\codex-maintenance-4-7-no-cad\report.json`
- 本轮 focused / full unittest 和 repo audit 为终端验证证据，无新增 `output\validation_runs` 真实 CAD 目录。

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 全量单测与 repo audit 通过 | test / repo_audit | **否** |
| 路径安全公共化与越界拒绝可回归 | structured invalid / negative path boundary tests | **否** |
| schema registry 覆盖所有 schema 文件 | schema validation tests | **否** |
| no-CAD validation 通过 | deferred_cad_readback_required / non-CAD gate | **否** |
| handoff / status 不再承载副计划 | doc governance tests | **否** |

### 9. 剩余风险

- 本轮不新增真实 CAD `geometry_verified` 结论。
- ActiveDocument guard、正式图层保护、公司块库和真实项目 DWG 仍属于后续真实 CAD 安全主线。
- 文档治理已有回归测试，但未来新增规划文档时仍需人工判断其是否又变成第二套计划。

---

## LCAD-02-STRICT-MATRIX-RUNNER（manifest selected / all / strict runner）

**日期**：2026-05-26

**性质**：本地真实 CAD 校验扩样主线第 2 包；让 local CAD regression runner 真正支持 selected / all / strict 调度。

### 1. 开发包名

`LCAD-02-STRICT-MATRIX-RUNNER`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/local_cad_regression.py` | 新增 manifest case 选择器、selected case 参数、summary rollup 字段、CLI `--case` 和 `--strict` |
| `tests/core/test_local_cad_regression.py` | 新增 selected case、未知 case 拒绝和 strict rollup 测试 |
| `README.md` / `CORE_CONTEXT_BRIEF.md` / `CORE_STATUS.md` / `CAD_AGENT_STATUS.md` / `CORE_RESTRUCTURE_PLAN.md` / `CAD_AGENT_CHANGELOG.md` / 本文 | 同步 LCAD-02 证据、下一包顺序和进度估算 |

### 3. 关键设计说明

- 默认不传 `--case` 时继续运行 manifest 的 all cases，保持 LCAD-01 的全量行为。
- `--case <case_id>` 可重复传入，只跑被选中的 manifest case；未知 case 会在执行任何命令前被拒绝。
- `--strict` 是 `--require-cad-verified` 的简写别名，便于本地真实 CAD smoke 使用。
- summary 统一输出 `strict`、`manifest_case_count`、`selected_case_count`、`selected_case_ids`，方便后续趋势 rollup 和失败归因。

### 4. 新增/修改测试

- `test_lcad_02_selected_case_runs_only_project_sample_from_manifest`
- `test_lcad_02_unknown_selected_case_is_rejected_before_running_commands`
- `test_real_cad_strict_mode_fails_when_project_sample_is_not_geometry_verified` 补充 `summary.strict`

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_local_cad_regression -v
# 9 tests OK

& $py scripts\run_local_cad_regression.py --no-cad --case project_sample_cad_check --output-dir output\validation_runs\lcad-02-selected-project-sample-no-cad
# status=pass; selected_case_count=1; step_count=1; deferred_case_count=1

& $py scripts\run_local_cad_regression.py --strict --output-dir output\validation_runs\lcad-02-strict-all-cad
# status=pass; selected_case_count=3; step_count=4; geometry_verified_case_count=6; created_handle_count=90
```

真实 CAD strict all run 的 baseline 子流程内还执行了全量单测：`461 tests OK`。

### 6. 是否运行真实 CAD

**是**。本包运行了 `--strict` 全量真实 CAD regression。当前测试 CAD 文件允许写入和编辑；脚本仍记录 `layer=CODEX_PREVIEW`、`saved_dwg=false`、`deleted_entities=false`、`modified_formal_layers=false`。

### 7. CAD 证据路径

- `output\validation_runs\lcad-02-selected-project-sample-no-cad\local_cad_regression_report.json`
- `output\validation_runs\lcad-02-strict-all-cad\local_cad_regression_report.json`
- `output\validation_runs\lcad-02-strict-all-cad\baseline_cad_validation\report.json`
- `output\validation_runs\lcad-02-strict-all-cad\project_sample_cad\project_sample_cad_check_report.json`
- `output\validation_runs\lcad-02-strict-all-cad\composition_cad\composition_cad_check_report.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| runner 支持 selected case | fake runner / CLI no-CAD selected evidence | **否** |
| runner 支持 all case strict rollup | strict CAD matrix | **是，6 个 case** |
| 当前测试 CAD 会话写入实体已汇总 | created_handle_count | **是，90 个 handles** |
| 未知 selected case 会在执行前拒绝 | negative unit test | **否** |

### 9. 剩余风险

- `LCAD-02` 解决调度和 rollup，不解决 ActiveDocument / no-save / no-delete 的前后守卫；下一包 `LCAD-03` 处理。
- 当前 `--case` 选择只基于 manifest case id；更细的子 case 过滤、历史趋势聚合和失败趋势归因留给后续 `LCAD-11`。
- 真实 CAD 结论仍只覆盖当前测试会话，不扩大到任意项目 DWG、正式图层、公司块库、属性块或 hatch。

---

## COMPLEX-CAD-SMOKE（复杂混合图形 CAD smoke）

**日期**：2026-05-26

**性质**：用户要求重新校验 CAD 测试层能否绘制复杂测试图形后的前置加固包；已纳入默认本地 CAD regression manifest。

### 1. 开发包名

`COMPLEX-CAD-SMOKE`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/complex_cad_smoke.py` | 新增复杂混合图形 smoke runner，绘制并回读 line / polyline / circle / arc / text / dimension |
| `scripts/run_complex_cad_smoke.py` | 新增 CLI wrapper，支持真实 CAD 与 `--no-cad` deferred |
| `examples/cad_regression/local_cad_regression_manifest.json` | 增加第 4 个默认 case：`complex_cad_smoke` |
| `core/verification/local_cad_regression.py` | 接入 complex case、selected case、no-CAD deferred 和 full strict rollup |
| `core/verification/local_cad_regression_manifest.py` | 拆出 manifest 读取、语义校验、summary 和 case 选择，保持主矩阵文件低于 repo audit 行数上限 |
| `tests/core/test_complex_cad_smoke.py` | 新增复杂 smoke 单测 |
| `tests/core/test_local_cad_regression.py` | 增加 complex manifest / selected / deferred rollup 覆盖 |
| `README.md` / `CORE_CONTEXT_BRIEF.md` / `CORE_STATUS.md` / `CAD_AGENT_STATUS.md` / `CORE_RESTRUCTURE_PLAN.md` / `CAD_AGENT_CHANGELOG.md` / 本文 | 同步证据、边界和进度 |

### 3. 关键设计说明

- 复杂 smoke 只写 `CODEX_PREVIEW`，不保存 DWG，不删除实体，不修改正式图层。
- 图形包含外框、3 条竖向网格线、3 条横向网格线、1 条斜线、1 条开放多段线、3 个圆、2 段弧、4 段文字和 2 个标注。
- 几何通过必须满足 created handles 定向回读、type counts 匹配、layer counts 全在 `CODEX_PREVIEW`、bbox 为 `3600 x 2200`。
- 直接 CLI 输出复用 `core.path_safety`，`--output-dir` 必须留在仓库 `output/` 下。
- 截图 `complex-cad-smoke-window.png` 只作为视觉辅助，不替代 readback。

### 4. 新增/修改测试

- `test_complex_smoke_draws_mixed_entities_and_verifies_created_handles`
- `test_complex_smoke_no_cad_is_deferred_not_geometry_verified`
- `test_complex_smoke_fails_when_created_handle_is_not_read_back`
- `test_complex_smoke_cli_output_must_stay_under_project_output`
- `test_complex_cad_smoke_can_be_selected_from_manifest`
- no-CAD full matrix deferred rollup 增加 `complex_cad_smoke`

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_complex_cad_smoke -v
# 4 tests OK

& $py scripts\run_complex_cad_smoke.py --no-cad --output-dir output\validation_runs\complex-cad-smoke-no-cad
# status=deferred; geometry_verified=false; created_handle_count=0

& $py scripts\run_complex_cad_smoke.py --output-dir output\validation_runs\complex-cad-smoke-real-final
# status=geometry_verified; created_handle_count=23; bbox=3600 x 2200

& $py scripts\render_preview.py --capture-autocad-window --execution-summary output\validation_runs\complex-cad-smoke-real-final\complex_cad_execution_summary.json --output output\validation_runs\complex-cad-smoke-real-final\complex-cad-smoke-window.png --fallback-screen
# status=captured; mode=autocad_window; handle_count=23

& $py scripts\run_local_cad_regression.py --strict --output-dir output\validation_runs\complex-cad-regression-strict-final
# status=pass; selected_case_count=4; step_count=5; geometry_verified_case_count=7; created_handle_count=113
```

真实 CAD full strict run 的 baseline 子流程内还执行了全量单测：`466 tests OK`。

### 6. 是否运行真实 CAD

**是**。当前测试 CAD 文件允许写入和编辑；脚本仍记录只写 `CODEX_PREVIEW`，且 `saved_dwg=false`、`deleted_entities=false`、`modified_formal_layers=false`。

### 7. CAD 证据路径

- `output\validation_runs\complex-cad-smoke-no-cad\complex_cad_smoke_report.json`
- `output\validation_runs\complex-cad-smoke-real-final\complex_cad_smoke_report.json`
- `output\validation_runs\complex-cad-smoke-real-final\complex_cad_execution_summary.json`
- `output\validation_runs\complex-cad-smoke-real-final\complex-cad-smoke-window.png`
- `output\validation_runs\complex-cad-regression-strict-final\local_cad_regression_report.json`
- `output\validation_runs\complex-cad-regression-strict-final\complex_cad_smoke\complex_cad_smoke_report.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 复杂混合图形可在当前测试 CAD 会话中绘制并回读 | created handles readback / strict CAD smoke | **是，23 个 handles** |
| 默认 local CAD regression manifest 已包含 complex case | manifest / full strict matrix | **是，full strict 矩阵 7 个 verified case** |
| no-CAD 模式不会误报几何通过 | deferred_cad_readback_required | **否** |
| 截图可用于人工检查图形是否可见 | visual aid | **否，截图不替代几何回读** |

### 9. 剩余风险

- 本包是复杂混合 smoke，不等于完整 `LCAD-05` primitive matrix 或 `LCAD-06` CAD_PLAN fixture suite 完成。
- ActiveDocument / no-save / no-delete 前后守卫仍属于 `LCAD-03`，没有因为复杂 smoke 通过而跳过。
- 真实 CAD 结论只覆盖当前测试 DWG 会话和受控图形，不扩大到任意项目 DWG、正式图层、公司块库、属性块或 hatch。

---

## LCAD-01-REGRESSION-MANIFEST（本地真实 CAD regression manifest）

**日期**：2026-05-26

**性质**：本地真实 CAD 校验扩样主线第 1 包；定义 regression manifest，并在当前测试 CAD 会话下完成 strict smoke。

### 1. 开发包名

`LCAD-01-REGRESSION-MANIFEST`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/local_cad_regression.py` | 新增默认 manifest 路径、manifest schema/语义校验、报告顶层 manifest metadata、CLI `--manifest` |
| `core/schemas/cad_regression_manifest.schema.json` | 新增 CAD regression manifest schema |
| `core/schemas/registry.py` | 登记 `cad_regression_manifest` 并支持模型类型推断 |
| `examples/cad_regression/local_cad_regression_manifest.json` | 新增默认 manifest；LCAD-01 初版覆盖 baseline / project sample / composition 三个 case，后续 complex smoke 已扩为 4 case |
| `tests/core/test_local_cad_regression.py` | 新增 LCAD-01 manifest、坏 manifest 和 no-CAD metadata 回归测试 |
| `tests/core/test_schema_validation.py` / `tests/fixtures/invalid_models/cad_regression_manifest.invalid.json` | 新增 schema 示例和反例覆盖 |
| `README.md` / `CORE_CONTEXT_BRIEF.md` / `CORE_STATUS.md` / `CAD_AGENT_STATUS.md` / `CORE_RESTRUCTURE_PLAN.md` / `CAD_AGENT_CHANGELOG.md` / 本文 | 同步状态、证据、计划和交接口径 |

### 3. 关键设计说明

- manifest 是本地真实 CAD regression 的 case contract，不替代 runner 本身；`LCAD-02` 才继续推进 selected / all / strict manifest runner。
- 每个 case 必须声明 `requires_real_cad`、`expected_evidence_state`、`output_path`、入口命令和安全边界。
- 安全边界仍以机器可读字段保存：`layer=CODEX_PREVIEW`、`saved_dwg=false`、`deleted_entities=false`、`modified_formal_layers=false`。
- `run_local_cad_regression.py` 默认加载 `examples/cad_regression/local_cad_regression_manifest.json`，并允许用 `--manifest` 指定替代 manifest。

### 4. 新增/修改测试

- `test_lcad_01_default_manifest_declares_cases_and_safety_boundaries`
- `test_lcad_01_manifest_rejects_missing_required_fields`
- `test_lcad_01_no_cad_report_includes_manifest_metadata`
- schema registry 示例/反例覆盖 `cad_regression_manifest`

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_local_cad_regression -v
# 7 tests OK

& $py -m unittest tests.core.test_schema_validation -v
# 10 tests OK

& $py scripts\run_local_cad_regression.py --no-cad --output-dir output\validation_runs\lcad-01-manifest-no-cad
# status=pass; step_count=3; deferred_case_count=2; geometry_verified_case_count=0

& $py scripts\run_local_cad_regression.py --output-dir output\validation_runs\lcad-01-manifest-cad-smoke --require-cad-verified
# status=pass; step_count=4; geometry_verified_case_count=6; created_handle_count=90
```

真实 CAD strict smoke 的 baseline 子流程内还执行了全量单测：`459 tests OK`。

### 6. 是否运行真实 CAD

**是**。用户明确说明当前 CAD 是测试文件，可随意测试、写入和编辑后，已运行真实 CAD strict smoke。脚本实际仍写入 `CODEX_PREVIEW`，并在报告中记录 `saved_dwg=false`、`deleted_entities=false`、`modified_formal_layers=false`。

### 7. CAD 证据路径

- `output\validation_runs\lcad-01-manifest-no-cad\local_cad_regression_report.json`
- `output\validation_runs\lcad-01-manifest-cad-smoke\local_cad_regression_report.json`
- `output\validation_runs\lcad-01-manifest-cad-smoke\baseline_cad_validation\report.json`
- `output\validation_runs\lcad-01-manifest-cad-smoke\project_sample_cad\project_sample_cad_check_report.json`
- `output\validation_runs\lcad-01-manifest-cad-smoke\composition_cad\composition_cad_check_report.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 默认 regression manifest 已定义并可校验 | schema / manifest tests | **否** |
| no-CAD manifest dry-run 通过 | deferred_cad_readback_required / non-CAD gate | **否** |
| 当前测试 CAD 会话下 strict smoke 通过 | created handles readback / strict CAD matrix | **是，6 个 case** |
| 当前测试 CAD 会话写入实体已汇总 | created_handle_count | **是，90 个 handles** |

### 9. 剩余风险

- `LCAD-01` 只完成 manifest contract 和当前 3-case smoke；selected / all / strict 调度已由后续 `LCAD-02` 补齐。
- 真实 CAD 结论只覆盖当前测试 DWG 会话，不扩大到任意项目 DWG、正式图层、公司块库、属性块或 hatch。
- ActiveDocument / no-save / no-delete 前后守卫仍属于 `LCAD-03`，本包只保留机器可读安全字段和现有脚本行为。

---

## LOCAL-CAD-REGRESSION（本地 CAD 回归矩阵加固）

**日期**：2026-05-26  
**性质**：进入下一开发阶段前的本地 CAD 校验层加固；新增统一矩阵入口，不新增真实 CAD 几何结论。

### 1. 开发包名

`LOCAL-CAD-REGRESSION`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/local_cad_regression.py` | 新增本地 CAD 回归矩阵聚合器，汇总 baseline CAD validation、project sample CAD check 和 composition CAD check |
| `scripts/run_local_cad_regression.py` | 新增 CLI wrapper，支持 `--no-cad` 和 `--require-cad-verified` |
| `tests/core/test_local_cad_regression.py` | 新增 no-CAD deferred、严格模式、composition 依赖跳过和 output 边界测试 |
| `CORE_CONTEXT_BRIEF.md` / `CORE_STATUS.md` / `CAD_AGENT_STATUS.md` / `CORE_RESTRUCTURE_PLAN.md` / `CAD_AGENT_CHANGELOG.md` / `CAD_AGENT_ISSUES.md` / 本文 | 同步本包证据、风险和唯一 PlanMD 口径 |

### 3. 关键设计说明

- `--no-cad` 模式默认安全：不连接 AutoCAD，不写真实 DWG，只把真实 CAD 子项记录为 deferred / non-CAD evidence。
- 真实 CAD 严格模式使用 `--require-cad-verified`；project sample 或 composition 任一子项不是 `geometry_verified`，矩阵顶层失败。
- composition CAD check 依赖 `interior_delivery_benchmark` 先成功产出 artifacts；前置失败时记录 `not_run` 和 `blocked_by`，不会继续写 CAD。
- 输出统一落在仓库 `output/` 下，并复用 `core.path_safety` 的 output dir 边界。

### 4. 新增/修改测试

- `test_no_cad_mode_builds_deferred_matrix_without_running_cad_only_checks`
- `test_real_cad_strict_mode_fails_when_project_sample_is_not_geometry_verified`
- `test_composition_cad_check_is_skipped_when_benchmark_artifacts_fail`
- `test_output_dir_must_stay_under_project_output`

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_local_cad_regression
# 4 tests OK

& $py scripts\run_local_cad_regression.py --no-cad --output-dir output\validation_runs\local-cad-regression-no-cad
# status=pass; step_count=3; deferred_case_count=2; geometry_verified_case_count=0

& $py -m unittest discover -s tests
# 456 tests OK
```

### 6. 是否运行真实 CAD

**否**。本轮只运行 no-CAD 矩阵和单测；未连接 AutoCAD 写入真实 DWG。

### 7. CAD 证据路径

- `output\validation_runs\local-cad-regression-no-cad\local_cad_regression_report.json`
- `output\validation_runs\local-cad-regression-no-cad\baseline_cad_validation\report.json`
- `output\validation_runs\local-cad-regression-no-cad\project_sample_cad\project_sample_cad_check_report.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 本地 CAD 回归矩阵 no-CAD 模式通过 | deferred_cad_readback_required / non-CAD gate | **否** |
| project sample CAD check 在 no-CAD 下输出 deferred | deferred_cad_readback_required | **否** |
| composition CAD check 在 no-CAD 下被明确延期 | deferred local matrix step | **否** |
| 严格模式会拒绝非 `geometry_verified` 子项 | negative evidence gate | **否** |

### 9. 剩余风险

- 本包不新增真实 CAD `geometry_verified` 结论。
- 真实 CAD 矩阵仍需在用户 AutoCAD 会话下单独运行，建议使用 `--require-cad-verified`。
- 该矩阵目前覆盖 baseline、project sample 和 composition 三条入口；公司块库、属性块、hatch 和真实项目 DWG 仍需后续扩样。

---

## DEMAND-01-DEMAND-SIDE-AGENT-SUITE（需求侧多角色 Agent 套件）

**日期**：2026-05-26  
**性质**：需求侧压力测试层与 benchmark 扩展；不新增真实 CAD 几何结论。

### 1. 开发包名

`DEMAND-01-DEMAND-SIDE-AGENT-SUITE`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `agents/demand_side/role_agents.json` | 新增 12 个需求侧角色，覆盖 residential / office / restaurant / commercial_fitout / exhibition / custom |
| `agents/demand_side/README.md` | 说明需求侧 Agent 是数据型压力测试层，不直接执行 CAD |
| `core/demand_agents/` | 新增加载、校验、scene 覆盖汇总和 demand case 校验 |
| `core/benchmarks/runner.py` | 新增 `demand_case` pipeline，分派到现有 object / composition / blank-shell benchmark |
| `examples/benchmarks/demand_side_agent_benchmark.json` | 新增 10 个跨场景需求 case |
| `tests/core/test_demand_agents.py` | 新增角色覆盖、需求 case、未知 Agent 拒绝和 benchmark 执行测试 |
| `docs/superpowers/specs/2026-05-26-demand-side-agent-suite-design.md` | 新增本包设计记录 |
| `docs/superpowers/plans/2026-05-26-demand-side-agent-suite.md` | 新增本包实施计划记录 |
| `CORE_CONTEXT_BRIEF.md` / `CORE_RESTRUCTURE_PLAN.md` / `CORE_STATUS.md` / `CAD_AGENT_STATUS.md` / `CAD_AGENT_CHANGELOG.md` / `agents/SCENE_AGENT_RULES.md` / `docs/architecture/core-scene-agent-boundaries.md` / 本文 | 同步需求侧 Agent 层口径、证据和边界 |

### 3. 关键设计说明

- `agents/demand_side/` 只保存角色、用户原话、需求焦点和 Core 能力映射，不是 Scene Product；按用户澄清，它是开发期脚手架，能力沉淀完成后可清理角色表。
- `demand_case` benchmark 不重新实现绘图能力，只把需求记录分派到已有 `object_spec`、`composition_spec` 或 `blank_shell` pipeline。
- benchmark 结果保留 `demand_agent_id`、`scene_id`、`request_text`、`target_pipeline`、`core_capability_targets`，方便后续按需求侧追踪缺口。
- 第一批需求 case 选取当前 Core 已能表达的对象和组合，目标是先建立“需求记录 -> 可跑验收 -> 缺口定位”的闭环。

### 4. 新增/修改测试

- `test_demand_agent_registry_covers_current_scene_agents`
- `test_demand_agent_records_keep_user_voice_and_core_mapping`
- `test_demand_case_records_reference_known_agents_and_target_pipeline`
- `test_demand_agent_benchmark_runs_cross_scene_demands`
- `test_demand_case_rejects_unknown_agent_reference`
- 全量测试同时覆盖 `test_scene_agent_boundaries`，确认 `agents/demand_side/` 没有越界 Python / CAD 执行实现。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_demand_agents
# 先红灯：ModuleNotFoundError: No module named 'core.demand_agents.loaders'

& $py -m unittest tests.core.test_demand_agents
# 5 tests OK

& $py -m unittest tests.core.test_demand_agents tests.core.test_benchmarks tests.agents.test_scene_agent_boundaries
# 29 tests OK

& $py scripts\run_benchmark_suite.py examples\benchmarks\demand_side_agent_benchmark.json --output-root output\test_artifacts\benchmarks\demand_side_agents_manual
# status=pass; total=10; passed=10; failed=0; non_cad_only=true

& $py -m unittest discover -s tests
# 474 tests OK

& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
# status=pass; finding_count=0
```

### 6. 是否运行真实 CAD

**否**。本包只建立需求侧 non-CAD benchmark 与数据层，不连接 AutoCAD，不写入真实 DWG。

### 7. CAD 证据路径

- `output\test_artifacts\benchmarks\demand_side_agents\benchmark_summary.json`
- `output\test_artifacts\benchmarks\demand_side_agents_manual\benchmark_summary.json`

这些路径是 non-CAD benchmark 证据，不是 created handles readback。

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 需求侧角色 registry 可加载并覆盖 6 个场景 | unit tests / data validation | **否** |
| 10 个 demand case 可分派到现有 Core benchmark pipeline | non-CAD benchmark | **否** |
| 未知 `demand_agent_id` 会被拒绝 | negative unit test | **否** |
| 全量单测未回归 | unittest | **否** |

### 9. 剩余风险

- 本包不证明真实 CAD 几何准确；后续若要说某个需求“可交付 CAD”，仍需 validate、dry-run、`CODEX_PREVIEW`、created handles readback 和 `geometry_verified`。
- 需求侧 Agent 目前是数据和 benchmark 层，不是能自主持续对话的运行时 Agent。
- 第一批 demand case 优先覆盖当前可表达对象 / 组合；更复杂需求如真实块库、属性块、hatch、立面深化和真实项目样本仍需后续小包补齐。

---

## OBJ-DETAIL-01-COMPONENT-PLAN（对象组件级 CAD_PLAN 展开）

**日期**：2026-05-26  
**性质**：将需求侧“精细餐桌 / 办公椅”等诉求沉淀为 Core 对象生成能力；当前为 non-CAD 验证。

### 1. 开发包名

`OBJ-DETAIL-01-COMPONENT-PLAN`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/object_engine/detail_plan.py` | 新增对象组件级 `CAD_PLAN` 展开，覆盖 table / bed / chair / sofa / desk |
| `core/benchmarks/runner.py` | 新增 `object_detail_spec` pipeline，并允许 demand case 分派到该 pipeline |
| `core/demand_agents/loaders.py` | 允许 `object_detail_spec` 作为需求目标 pipeline |
| `examples/benchmarks/demand_side_agent_benchmark.json` | 将“比较精细的餐桌”和“办公椅”需求切到 `object_detail_spec` |
| `tests/core/test_object_engine.py` | 新增对象细化 plan 生成、validate 和 dry-run 测试 |
| `tests/core/test_benchmarks.py` | 新增 `object_detail_spec` benchmark contract 测试 |
| `tests/core/test_demand_agents.py` | 更新 demand target pipeline 断言 |
| `core/object_engine/README.md` / `CORE_CONTEXT_BRIEF.md` / `CORE_RESTRUCTURE_PLAN.md` / `CORE_STATUS.md` / `CAD_AGENT_STATUS.md` / `CAD_AGENT_CHANGELOG.md` / 本文 | 同步对象细化能力、证据和边界 |

### 3. 关键设计说明

- `object_detail_spec` 不引入新 CAD primitive；它把一个 `OBJECT_SPEC` 展开成多份安全 `draw_object` CAD_PLAN，继续复用现有 validate / dry-run / execution 合同。
- table 输出桌面 + 4 个支撑；chair 输出座面、靠背 + 4 个支撑；bed 输出底座、睡眠面和床头；sofa 输出座面、靠背和两侧扶手；desk 输出台面和两侧支撑。
- 默认继续 `CODEX_PREVIEW`、不加文字、不加尺寸标注。
- 该能力提升“生成能力和理解能力”，而不是扩充最终产品中的角色表。

### 4. 新增/修改测试

- `test_detailed_table_plan_expands_into_component_level_preview_plans`
- `test_detailed_furniture_plans_cover_bed_chair_and_sofa_components`
- `test_object_detail_spec_benchmark_case_runs_component_plan_contract`
- 需求侧 benchmark 更新后验证“精细餐桌”和“办公椅”均走 `object_detail_spec`。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_object_engine tests.core.test_benchmarks.BenchmarkRunnerTests.test_object_detail_spec_benchmark_case_runs_component_plan_contract
# 先红灯：No module named 'core.object_engine.detail_plan'；case.pipeline is not supported: object_detail_spec

& $py -m unittest tests.core.test_object_engine tests.core.test_benchmarks.BenchmarkRunnerTests.test_object_detail_spec_benchmark_case_runs_component_plan_contract
# 8 tests OK

& $py -m unittest tests.core.test_demand_agents
# 5 tests OK

& $py scripts\run_benchmark_suite.py examples\benchmarks\demand_side_agent_benchmark.json --output-root output\test_artifacts\benchmarks\demand_side_agents_manual_after_detail
# status=pass; total=10; passed=10; failed=0; non_cad_only=true

& $py scripts\run_benchmark_suite.py examples\benchmarks\demand_side_agent_benchmark.json --output-root output\test_artifacts\benchmarks\demand_side_agents_cad_preflight
# status=pass; total=10; passed=10; failed=0; non_cad_only=true

# 使用 core.execution.batch_plan_runner.execute_plan_batch 将 10 个 demand case 写入 CODEX_PREVIEW 并回读 handles
# output\validation_runs\demand-side-agent-cad-real-20260526\demand_side_agent_cad_check_report.json
# status=geometry_verified; case_count=10; verified_case_count=10; created_handle_count=100

# 聚焦 100 个 created handles 并截取 AutoCAD 窗口视觉辅助
# output\validation_runs\demand-side-agent-cad-real-20260526\demand-side-agent-cad-window-focused.png
# mode=autocad_window; focus.status=zoomed_to_bbox; handle_count=100

& $py -m unittest tests.core.test_object_engine tests.core.test_benchmarks tests.core.test_demand_agents tests.agents.test_scene_agent_boundaries
# 37 tests OK

& $py -m unittest discover -s tests
# 477 tests OK

& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
# status=pass; finding_count=0
```

### 6. 是否运行真实 CAD

**是**。本包后续补跑真实 CAD：10 个 demand-side case 写入当前 AutoCAD `CODEX_PREVIEW` 图层，并按 created handles 定向回读。脚本未保存 DWG、未删除实体、未修改正式图层。

### 7. CAD 证据路径

- `output\test_artifacts\benchmarks\object_detail_contract\residential-detailed-table\detail_cad_plans.json`
- `output\test_artifacts\benchmarks\demand_side_agents_manual_after_detail\benchmark_summary.json`
- `output\test_artifacts\benchmarks\demand_side_agents_manual_after_detail\demand_residential_beginner_dining_table\detail_cad_plans.json`
- `output\test_artifacts\benchmarks\demand_side_agents_manual_after_detail\demand_office_admin_task_chair\detail_cad_plans.json`
- `output\test_artifacts\benchmarks\demand_side_agents_cad_preflight\benchmark_summary.json`
- `output\validation_runs\demand-side-agent-cad-real-20260526\demand_side_agent_cad_check_report.json`
- `output\validation_runs\demand-side-agent-cad-real-20260526\all_created_handles_execution_summary.nobom.json`
- `output\validation_runs\demand-side-agent-cad-real-20260526\demand-side-agent-cad-window-focused.png`

其中 `demand_side_agent_cad_check_report.json` 是真实 CAD created handles readback 证据；PNG 截图只是视觉辅助。

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| table / bed / chair / sofa 可展开组件级 CAD_PLAN | unit tests / validate / dry-run | **否** |
| `object_detail_spec` benchmark pipeline 可运行 | non-CAD benchmark | **否** |
| 需求侧“精细餐桌”和“办公椅”已命中对象细化能力 | demand benchmark + CAD batch readback | **是，随 10 个 demand case 验证** |
| 10 个 demand-side case 写入 `CODEX_PREVIEW` 并回读 | created handles readback | **是，10/10 cases，100 handles** |

### 9. 剩余风险

- 组件级对象仍是预览矩形组合，不是正式块库、属性块或复杂家具符号。
- 餐桌、椅子、床、沙发、办公桌之外的复杂对象仍需逐类扩展。
- 真实 CAD 结论只覆盖本轮 `CODEX_PREVIEW` 写入和 10 个 demand-side case，不扩大为任意项目 DWG、公司块库、属性块或 hatch。

---

## 当前交接说明

本文只保留已经交付开发包的 9 项交接记录与 Codex 校验指引，不再承载当前队列、后置 Backlog 或未来小包表。后续优先级、Phase 顺序、退出门槛和后置主线唯一以 `CORE_RESTRUCTURE_PLAN.md` 为准；本文仅在对应小包真正交付后追加交接章节。

2026-05-26 口径校准：本文中的历史开发包仍可作为交接证据，但不能把 scene preferences、Scene Alpha 验收或 scene beta non-CAD benchmark 解释为具体场景产品完成。Core / 场景边界以 `../architecture/core-scene-agent-boundaries.md`、`CORE_STATUS.md` 和 `CAD_AGENT_STATUS.md` 的最新口径为准。

---

## LCAD-08（Project sample CAD rollup）

**日期**：2026-05-26  
**性质**：双脱敏项目样本 CODEX_PREVIEW CAD 执行 + created handles readback rollup。

### 1. 开发包名

`LCAD-08-PROJECT-SAMPLE-CAD`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `examples/cad_regression/project_sample_cad_rollup.json` | 双样本 manifest |
| `core/project_samples/project_sample_cad_rollup.py` | rollup runner |
| `scripts/run_project_sample_cad_rollup.py` | CLI |
| `docs/verification/project_sample_cad_boundaries.md` | 边界说明 |
| `tests/core/test_project_sample_cad_rollup.py` | 3 tests |

### 5. 实际运行的命令和结果

```powershell
python -m unittest tests.core.test_project_sample_cad_rollup -v
# 3 tests OK

python scripts/run_project_sample_cad_rollup.py --output-dir output/validation_runs/project-sample-cad-rollup-real
# status=geometry_verified, 2/2 samples, handles 20+12
```

### 6. 是否运行真实 CAD

**是**。`sample_blank_shell` 20 handles；`commercial_fitout_sample` 12 handles；均 `CODEX_PREVIEW`。

### 7. 机器可读证据路径

- `output/validation_runs/project-sample-cad-rollup-real/project_sample_cad_rollup_report.json`
- per-sample：`cad/sample_blank_shell/project_sample_cad_check_report.json`
- per-sample：`cad/commercial_fitout_sample/commercial_fitout_cad_smoke_report.json`

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 双样本 rollup readback | real_cad_readback | **是**（注册样本范围） |

---

## LCAD-07（Block / attribute / hatch boundary）

**日期**：2026-05-26  
**性质**：机器可读 block / attribute / hatch 能力边界；支持项 verified，hatch deferred。

### 1. 开发包名

`LCAD-07-BLOCK-ATTRIBUTE-HATCH`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `examples/cad_regression/cad_block_attribute_hatch_boundary.json` | 能力矩阵 fixture |
| `core/verification/cad_block_attribute_hatch_boundary.py` | 契约断言 |
| `docs/verification/cad_block_attribute_hatch_boundaries.md` | 人类可读边界 |

### 5. 实际运行的命令和结果

```powershell
python -m unittest tests.core.test_cad_block_attribute_hatch_boundary tests.core.test_block_attribute_probe -v
# 12 tests OK
```

### 6. 是否运行真实 CAD

**否**（边界汇总 + 既有单测；真实 block alpha 证据见历史 `block_alpha_cad_evidence.md`）。

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 受控 block + attribute probe | unit_test + 历史 real CAD | **是**（受控范围） |
| hatch | structured deferred | **否** |

---

## C-CFIT-07（Product boundary rollup）

**日期**：2026-05-26  
**性质**：汇总 commercial_fitout Scene Product Alpha 可声明 / 不可声明能力，统一状态页口径。

### 1. 开发包名

`C-CFIT-07-PRODUCT-BOUNDARY-ROLLUP`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `agents/commercial_fitout/capabilities/product_alpha_boundary.json` | 机器可读边界 rollup |
| `core/agents/commercial_fitout_product_boundary.py` | 加载 / 契约断言 / 状态页摘要 |
| `core/schemas/commercial_fitout_product_alpha_boundary.schema.json` | Schema |
| `agents/commercial_fitout/subscenes.json` | `product_alpha_status` → `product_boundary` |
| `docs/verification/commercial_fitout_product_alpha_boundaries.md` | 人类可读汇总 |
| `CORE_STATUS.md` / `CAD_AGENT_STATUS.md` | 保守上调 commercial_fitout 为 Scene Product Alpha |

### 3. 关键设计说明

- `declares_scene_product_complete` 固定为 `false`。
- 仅 1 项 `geometry_verified` 能力，且必须带 `commercial_fitout_sample` 范围注释。
- C 路线 `C-CFIT-01`..`06` 全部列入 `completed_packages`。

### 4. 新增/修改测试

- `tests.agents.test_commercial_fitout_product_boundary`（5 tests）

### 5. 实际运行的命令和结果

```powershell
python -m unittest tests.agents.test_commercial_fitout_product_boundary tests.agents.test_commercial_fitout_scope -v
# 10 tests OK
```

### 6. 是否运行真实 CAD

**否**（文档与契约汇总包）。

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Scene Product Alpha 边界已机器化 | schema + unit_test | **否**（rollup 本身） |
| 工装 ≠ Scene Product | 文档 + 契约 | **否** |

### 9. 剩余风险

- 真实 AutoCAD、多项目样本、公司块库仍为 `next_gaps_to_scene_product`。

---

## C-CFIT-06（Real CAD smoke）

**日期**：2026-05-26  
**性质**：工装脱敏样本确认后 `CAD_PLAN` 在 `CODEX_PREVIEW` 执行 + created handles readback。

### 1. 开发包名

`C-CFIT-06-REAL-CAD-SMOKE`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/agents/commercial_fitout_cad_smoke.py` | 确认产物收集 + batch 执行 + smoke 报告 |
| `core/schemas/commercial_fitout_cad_smoke_report.schema.json` | 报告 schema（含 `product_claim_boundary`） |
| `scripts/run_commercial_fitout_cad_smoke.py` | CLI |
| `tests/agents/test_commercial_fitout_cad_smoke.py` | 3 tests |

### 3. 关键设计说明

- 先确保 `run_fitout_sample_confirmation_loop` 产出 `cad_plan_items`（desk / chair / cabinet）。
- `execute_plan_batch` + `build_verification_report` 与 project sample CAD check 同路径。
- `product_claim_boundary` 明确 **不** 声明完整工装 Scene Product。

### 4. 新增/修改测试

- `tests.agents.test_commercial_fitout_cad_smoke`（3 tests）

### 5. 实际运行的命令和结果

```powershell
python -m unittest tests.agents.test_commercial_fitout_cad_smoke -v
# 3 tests OK

python scripts/run_commercial_fitout_cad_smoke.py --output-dir output/validation_runs/commercial-fitout-cad-smoke-real
# exit 2: AutoCAD unavailable (deferred)
```

### 6. 是否运行真实 CAD

**否**（本环境无活动 AutoCAD）。单测使用 FakeCadDriver 完成 readback `geometry_verified`。

### 7. 机器可读证据路径

- 单测：`output/test_artifacts/commercial_fitout_sample/cad_smoke_*`
- 真实 CAD（待补）：`output/validation_runs/commercial-fitout-cad-smoke-real/commercial_fitout_cad_smoke_report.json`

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 3 个确认后 CAD_PLAN batch readback | unit_test (FakeCadDriver) | **是**（仅 `commercial_fitout_sample` 范围） |
| 真实 AutoCAD 会话 | deferred | **否**（待用户打开 CAD 补跑） |

### 9. 剩余风险

- 真实 AutoCAD 未在本会话验证；不得将 FakeCadDriver 证据扩大为生产环境几何结论。
- `FITOUT_*` 块仍为占位；当前 smoke 走 `draw_object` 矩形预览。

---

## C-CFIT-05（Sample project confirmation）

**日期**：2026-05-26  
**性质**：工装脱敏样本从 `SHELL_MODEL` / `DESIGN_PROPOSAL` 到用户确认 bundle 的 non-CAD 闭环。

### 1. 开发包名

`C-CFIT-05-SAMPLE-PROJECT-CONFIRMATION`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `projects/commercial_fitout_sample/` | 新增脱敏样本 manifest / shell / brief / expected |
| `examples/workflows/commercial_fitout_sample_confirmation_loop.json` | 工装确认 workflow |
| `core/agents/commercial_fitout_sample_confirmation.py` | 确认前 gate + 确认后 bundle（assumptions / risks） |
| `core/schemas/commercial_fitout_sample_confirmation_bundle.schema.json` | 样本确认 bundle schema |
| `core/workflows/blank_shell_pipeline.py` | `confirmation_pending` 部分产物路径 |
| `core/proposal_engine/partial_replan.py` | 先写 cad_plan_items 再 verification |
| `scripts/run_commercial_fitout_sample_confirmation.py` | CLI |
| `tests/agents/test_commercial_fitout_sample_confirmation.py` | 4 tests |

### 3. 关键设计说明

- `design_brief.needs_confirmation=true` 时 pipeline 状态为 `confirmation_pending`，不写出 `cad_plan` / `dry_run_report`。
- 用户确认后走 `finalize_confirmed_cad_plans` + `commercial_fitout_sample_confirmation_bundle.json`（记录 assumptions / risks）。
- 全部 `CAD_PLAN` 保持 `CODEX_PREVIEW` 且 `needs_confirmation=false`（确认后）。

### 4. 新增/修改测试

- `tests.agents.test_commercial_fitout_sample_confirmation`（4 tests）

### 5. 实际运行的命令和结果

```powershell
python -m unittest tests.agents.test_commercial_fitout_sample_confirmation -v
# 4 tests OK
```

### 6. 是否运行真实 CAD

**否**。`geometry_verified=false`；仅 non-CAD validate / dry-run / unverified verification。

### 7. 机器可读证据路径

- 单测产物：`output/test_artifacts/commercial_fitout_sample/`
- CLI 默认：`output/validation_runs/commercial-fitout-sample-confirmation/`

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 确认前无 CAD_PLAN 产物 | unit_test | **否** |
| 确认后 confirmed bundle + assumptions/risks | unit_test + schema | **否** |

### 9. 剩余风险

- 真实 CAD smoke 与 created handles readback 留给 `C-CFIT-06-REAL-CAD-SMOKE`。
- `FITOUT_*` 块仍为占位 metadata，未绑定公司图块库。

---

## C-CFIT-04（Micro-scene benchmark）

**日期**：2026-05-26  
**性质**：工装成功 / 失败微场景 non-CAD benchmark，失败 case 结构化 blocked。

### 1. 开发包名

`C-CFIT-04-MICRO-SCENE-BENCHMARK`

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_commercial_fitout_layout_failure tests.agents.test_commercial_fitout_micro_scene_benchmark -v
# 6 tests OK
& $py scripts\run_commercial_fitout_micro_scene_benchmark.py
# summary pass 8/8
```

### 6. 是否运行真实 CAD

**否**（non-CAD composition / object_spec benchmark only）。

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 4 pass + 4 blocked_expected_non_cad micro-scenes | unit_test + benchmark suite | **否** |

---

## C-CFIT-03（Block mapping）

**日期**：2026-05-26  
**性质**：工装受控块 metadata、mapping 与 OBJECT_SPEC fallback。

### 1. 开发包名

`C-CFIT-03-BLOCK-MAPPING`

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.agents.test_commercial_fitout_block_mapping -v
# 7 tests OK
```

### 6. 是否运行真实 CAD

**否**（symbol_fallback 块 metadata；无 `cad_insertion_verified`）。

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 受控 FITOUT 块名 + mapping + OBJECT_SPEC fallback | unit_test + schema | **否** |

---

## C-CFIT-02（Object catalog）

**日期**：2026-05-26  
**性质**：工装 Scene Product Alpha 对象体系 fixture，可被 Core layout / object pipeline 读取。

### 1. 开发包名

`C-CFIT-02-OBJECT-CATALOG`

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.agents.test_commercial_fitout_catalog -v
# 5 tests OK
```

### 6. 是否运行真实 CAD

**否**（catalog → OBJECT_SPEC → layout non-CAD only）。

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 14 项 object catalog + layout pipeline 可读 | unit_test + schema | **否** |

---

## C-CFIT-01（Scope and subscenes）

**日期**：2026-05-26  
**性质**：工装 Scene Product Alpha 首版范围与子场景收敛。

### 1. 开发包名

`C-CFIT-01-SCOPE-AND-SUBSCENES`

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.agents.test_commercial_fitout_scope -v
# 5 tests OK
```

### 6. 是否运行真实 CAD

**否**（范围与边界扫描 only）。

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 三子场景范围 + 不做完整施工图 + agent 边界扫描 | unit_test + schema | **否** |

---

## B-ORCH-05（Route audit report）

**日期**：2026-05-26  
**性质**：中控路由审计报告，汇总 workflow 选择、场景启用与证据边界。

### 1. 开发包名

`B-ORCH-05-ROUTE-AUDIT-REPORT`

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_route_audit_report tests.core.test_workflow_dispatch -v
# 11 tests OK
```

### 6. 是否运行真实 CAD

**否**（`readback_geometry_verified` 在 allow_cad 且无 readback 时标记 deferred）。

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| route audit report schema + orchestrate 附带写入 | unit_test | **否** |

---

## B-ORCH-04（Workflow dispatch）

**日期**：2026-05-26  
**性质**：中控 workflow 分派，复用既有 Core runners。

### 1. 开发包名

`B-ORCH-04-WORKFLOW-DISPATCH`

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_workflow_dispatch -v
# 7 tests OK（含 non_cad_pipeline 与 symbol_glyph 执行）
```

### 6. 是否运行真实 CAD

**否**（CAD 路由默认 deferred，除非 `include_cad=true`）。

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| orchestrator non-CAD dispatch | unit_test | **否** |

---

## B-ORCH-03（Activation policy）

**日期**：2026-05-26  
**性质**：场景启用策略，默认 `no_scene`，模糊时追问。

### 1. 开发包名

`B-ORCH-03-ACTIVATION-POLICY`

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_activation_policy -v
# 7 tests OK
```

### 6. 是否运行真实 CAD

**否**。

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| no_scene / manifest / trigger / clarification 路由 | unit_test | **否** |

---

## B-ORCH-02（Scene registry）

**日期**：2026-05-26  
**性质**：Scene Registry fixture，可被 orchestrator / router 读取。

### 1. 开发包名

`B-ORCH-02-SCENE-REGISTRY`

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_scene_registry -v
# 7 tests OK
```

### 6. 是否运行真实 CAD

**否**。

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 7 场景 registry 可读且语义校验通过 | unit_test | **否** |

---

## B-ORCH-01（Request context）

**日期**：2026-05-26  
**性质**：统一请求上下文与门禁，缺输入时不 dispatch / 不落图。

### 1. 开发包名

`B-ORCH-01-REQUEST-CONTEXT`

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_request_context -v
# 6 tests OK
```

### 6. 是否运行真实 CAD

**否**。

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| REQUEST_CONTEXT gate（ready/blocked/clarify） | unit_test | **否** |

---

## D-SYMBOL-07（Block fallback policy）

**日期**：2026-05-26  
**性质**：OBJECT_SPEC 渲染路径解析与反静默退化门禁。

### 1. 开发包名

`D-SYMBOL-07-BLOCK-FALLBACK-POLICY`

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_symbol_fallback_policy -v
# 6 tests OK
```

### 6. 是否运行真实 CAD

**否**（non-CAD 路径解析 + dry-run 证据）。

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| block/symbol/component/bbox/deferred 分层 evidence | unit_test | **否** |
| 受控 block 优先于 symbol（cad_insertion_verified） | unit_test | **否** |

---

## D-SYMBOL-06（CAD readback smoke）

**日期**：2026-05-26  
**性质**：代表 desk glyph 真实 CAD 写入 + created handles readback（FakeCad 已验证契约）。

### 1. 开发包名

`D-SYMBOL-06-CAD-READBACK-SMOKE`

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_symbol_glyph_cad_smoke -v
# 5 tests OK

& $py scripts/run_symbol_glyph_cad_smoke.py --no-cad --output-dir output/validation_runs/symbol-glyph-deferred-cli
# status=deferred（无 AutoCAD 连接）
```

### 6. 是否运行真实 CAD

**否**（本轮 CI/单元测试使用 `FakeCadDriver`）。本机有 AutoCAD 时可运行：

```powershell
& $py scripts/run_symbol_glyph_cad_smoke.py --output-dir output/validation_runs/symbol-glyph-real
```

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| desk glyph execute + readback 契约 | unit_test / FakeCadDriver | **是**（fake readback） |
| 真实 AutoCAD COM 落图 | 待本机 smoke | 待跑 |

---

## D-SYMBOL-05（Readability gate）

**日期**：2026-05-26  
**性质**：符号可读性报告，补充而非替代 `geometry_verified`。

### 1. 开发包名

`D-SYMBOL-05-READABILITY-GATE`

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_symbol_readability tests.core.test_object_to_symbol -v
# 11 tests OK
```

### 6. 是否运行真实 CAD

**否**。

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| symbol_readability_report 五态区分 | non_cad_only / unit_test | **否** |

---

## D-SYMBOL-04（Object to symbol）

**日期**：2026-05-26  
**性质**：`OBJECT_SPEC` → `SYMBOL_SPEC` 统一映射与显式 fallback。

### 1. 开发包名

`D-SYMBOL-04-OBJECT-TO-SYMBOL`

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_object_to_symbol tests.core.test_symbol_archetypes -v
# 11 tests OK
```

### 6. 是否运行真实 CAD

**否**。

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 6 类对象 symbol 映射 + validate/dry-run | non_cad_only / unit_test | **否** |

---

## D-SYMBOL-03（Archetype grammar）

**日期**：2026-05-26  
**性质**：6 类 archetype 必备符号部件与相对位置约束。

### 1. 开发包名

`D-SYMBOL-03-ARCHETYPE-GRAMMAR`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/symbol_engine/archetypes.py` | grammar + position rules |
| `core/symbol_engine/symbol_spec.py` | 接入 archetype 校验 |
| `core/symbol_engine/primitives.py` | seat_split / drawer_line / door_swing |
| `examples/symbol_specs/*.json` | 6 archetype 示例 |
| `tests/core/test_symbol_archetypes.py` | 新增 |

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_symbol_archetypes tests.core.test_symbol_spec tests.core.test_symbol_primitives -v
# 18 tests OK
```

### 6. 是否运行真实 CAD

**否**。

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 6 archetype grammar + validate/dry-run | non_cad_only / unit_test | **否** |

### 9. 剩余风险

- `OBJECT_SPEC` → `SYMBOL_SPEC` 自动映射尚未实现（`D-SYMBOL-04`）。

---

## D-SYMBOL-02（Primitives）

**日期**：2026-05-26  
**性质**：符号 primitive 渲染与 `draw_symbol_glyph` CAD_PLAN 入口。

### 1. 开发包名

`D-SYMBOL-02-PRIMITIVES`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/symbol_engine/primitives.py` | part → glyph 几何 |
| `core/plan_engine/symbol_glyph_plan.py` | validate / dry-run |
| `core/plan_engine/validate_plan.py` | `draw_symbol_glyph` intent |
| `core/plan_engine/dry_run_report.py` | glyph dry-run |
| `core/schemas/cad_plan.schema.json` | intent 枚举 |
| `tests/core/test_symbol_primitives.py` | 新增 |

### 3. 关键设计说明

- `symbol_spec_to_cad_plan()` 输出 `draw_symbol_glyph`，默认禁止 label/dimension。
- glyph primitive 支持 rectangle / line / polyline / circle / arc；拒绝 text/dimension。
- 真实 CAD 执行（`execute_plan`）尚未接线，留给后续 readback 包。

### 4. 新增/修改测试

- `tests.core.test_symbol_primitives`（5 tests）+ `test_symbol_spec`（12 tests OK）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_symbol_primitives tests.core.test_symbol_spec -v
# 12 tests OK
```

### 6. 是否运行真实 CAD

**否**。

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| symbol glyph CAD_PLAN validate + dry-run | non_cad_only / unit_test | **否** |

### 9. 剩余风险

- `execute_plan` 未支持 `draw_symbol_glyph`；archetype 必备部件规则未建立。

---

## D-SYMBOL-01（Spec schema）

**日期**：2026-05-26  
**性质**：SYMBOL-CORE 第 1 子包；`SYMBOL_SPEC` / `SYMBOL_GRAPH` 数据模型与反静默 bbox 门禁。

### 1. 开发包名

`D-SYMBOL-01-SPEC-SCHEMA`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/schemas/symbol_spec.schema.json` | SYMBOL_SPEC schema |
| `core/schemas/symbol_graph.schema.json` | SYMBOL_GRAPH schema |
| `core/schemas/registry.py` | 注册与 infer |
| `core/symbol_engine/symbol_spec.py` | 语义校验 |
| `examples/symbol_specs/surface_desk_plan.json` | 合法示例 |
| `examples/symbol_graphs/single_desk_placement.json` | 合法示例 |
| `tests/fixtures/invalid_models/symbol_*.invalid.json` | 非法 fixture |
| `tests/core/test_symbol_spec.py` | 新增 |

### 3. 关键设计说明

- `fallback_policy.mode` 必须显式声明；`symbol_readable` 禁止 outline-only parts。
- `fallback_bbox_placeholder` 要求 `bbox_fallback_declared=true` 与 `reason`。
- 尚未实现 primitive 渲染或真实 CAD readback（留给 `D-SYMBOL-02`~`06`）。

### 4. 新增/修改测试

- `tests.core.test_symbol_spec`（7 tests）+ `test_schema_validation`（17 tests OK）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_symbol_spec tests.core.test_schema_validation -v
# 17 tests OK
```

### 6. 是否运行真实 CAD

**否**。

### 7. 机器可读证据路径

- 示例：`examples/symbol_specs/surface_desk_plan.json`

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| SYMBOL_SPEC / SYMBOL_GRAPH schema + 反静默 bbox 门禁 | non_cad_only / unit_test | **否** |

### 9. 剩余风险

- primitive 层、archetype grammar、object 映射与 CAD readback 尚未实现。

---

## A-LCAD-04-TO-06（Smoke and plan matrix）

**日期**：2026-05-26  
**性质**：LCAD 扩样合并包；primitive matrix + 批量 `CAD_PLAN` fixture suite + manifest 接线。

### 1. 开发包名

`A-LCAD-04-TO-06-SMOKE-AND-PLAN-MATRIX`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/primitive_matrix.py` | 图元矩阵 wrapper |
| `core/verification/cad_plan_fixture_suite.py` | validate / dry-run / 可选执行 |
| `core/verification/local_cad_regression.py` | 新 manifest case 接线 |
| `core/verification/fake_cad_driver.py` | `insert_block_alpha` |
| `examples/cad_regression/cad_plan_fixture_manifest.json` | 3 fixture |
| `examples/cad_regression/fixtures/*.json` | cabinet / desk / block preview |
| `examples/cad_regression/local_cad_regression_manifest.json` | +3 case |
| `scripts/run_primitive_matrix.py` | CLI |
| `scripts/run_cad_plan_fixture_suite.py` | CLI |
| `tests/core/test_primitive_matrix.py` | 新增 |
| `tests/core/test_cad_plan_fixture_suite.py` | 新增 |
| `tests/core/test_local_cad_regression.py` | manifest 7 case |

### 3. 关键设计说明

- no-CAD 路径：fixture 只做 validate + dry-run；primitive matrix 用 `FakeCadDriver`。
- 有 CAD 路径：`cad_plan_fixture_suite_cad` 在 `--no-cad` 矩阵中 deferred；`--strict` 要求 `geometry_verified` 或 `pass`。
- 失败 fixture 在 suite 报告里按 `status=fail` 汇总，不静默 pass。

### 4. 新增/修改测试

- `tests.core.test_cad_plan_fixture_suite`（2 tests）
- `tests.core.test_primitive_matrix`（1 test）
- `tests.core.test_local_cad_regression` + `test_schema_validation`（23 tests OK）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_cad_plan_fixture_suite tests.core.test_primitive_matrix tests.core.test_local_cad_regression tests.core.test_schema_validation -v
# 23 tests OK
```

### 6. 是否运行真实 CAD

**否**（`self_check` 显示 `autocad_window.status=unavailable`）。

### 7. 机器可读证据路径

- `output/test_artifacts/cad_plan_fixture_suite/no_cad/cad_plan_fixture_suite_report.json`
- `output/test_artifacts/primitive_matrix/no_cad/primitive_matrix_report.json`

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| primitive matrix + 3 fixture validate/dry-run + fake 执行 | non_cad_only / unit_test | **否** |

### 9. 剩余风险

- `cad_plan_fixture_suite_cad`、`primitive_matrix`（无 `--no-cad`）的真实 CAD readback 待用户在 AutoCAD 可用时补跑 strict matrix。

---

## A-LCAD-03.4（Created-handle scope）

**日期**：2026-05-26  
**性质**：几何验证只认本轮 created handles；readback 报告记录 scope 统计。

### 1. 开发包名

`A-LCAD-03.4-CREATED-HANDLE-SCOPE`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/created_handle_scope.py` | scope 分析与 check |
| `core/verification/verification_report.py` | `actual.created_handle_scope` |
| `core/verification/evidence_contract.py` | geometry_verified 门禁 |
| `core/verification/cad_capability_probe.py` | probe 报告字段 |
| `core/verification/complex_cad_smoke.py` | smoke 报告字段 |
| `tests/core/test_created_handle_scope.py` | 新增 |

### 3. 关键设计说明

- `geometry_verified` 要求 `miss_count=0` 且 `extra_entity_count=0`。
- `created_handles_scope` check 从 warning 升级为 fail。

### 4. 新增/修改测试

- `tests.core.test_created_handle_scope`（3 tests）+ 相关回归 47 tests OK

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_created_handle_scope tests.core.test_verification_report tests.core.test_cad_capability_probe tests.core.test_complex_cad_smoke tests.core.test_cad_validation_runner tests.core.test_block_alpha_validation -v
# 47 tests OK
```

### 6. 是否运行真实 CAD

**否**。

### 7. 机器可读证据路径

- readback / probe 报告的 `actual.created_handle_scope` 或顶层 `created_handle_scope`

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| created-handle scope 统计与门禁 | non_cad_only / unit_test | **否** |

### 9. 剩余风险

- 真实大图里历史实体 before/after 差分仍未作为默认门禁；留给后续 LCAD 扩样。

---

## A-LCAD-03.3（No-save / no-delete guard）

**日期**：2026-05-26  
**性质**：CAD 安全 A 路线第 3 子包；运行时拦截 save/delete/formal-layer 写入。

### 1. 开发包名

`A-LCAD-03.3-NO-SAVE-NO-DELETE-GUARD`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/safety/write_guard.py` | 新增写入守卫与负向探针 |
| `core/cad_io/autocad_com.py` | 图层守卫 + save/delete 入口 |
| `core/verification/fake_cad_driver.py` | 同步守卫 |
| `core/verification/cad_capability_probe.py` | `write_guard` 报告与 check |
| `tests/core/test_cad_write_guard.py` | 新增 |

### 3. 关键设计说明

- 默认 preview-only 会话禁止 `WALL` 等正式图层写入、`Save`、覆盖、删除。
- capability probe 在真实写入后跑负向自检，确认被拦截且无新增正式实体。

### 4. 新增/修改测试

- `tests.core.test_cad_write_guard`（4 tests）
- `tests.core.test_cad_capability_probe` 扩展 `write_guard_negative`

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_cad_write_guard tests.core.test_cad_capability_probe tests.core.test_autocad_com_driver tests.core.test_execute_plan tests.core.test_complex_cad_smoke -v
# 35 tests OK
```

### 6. 是否运行真实 CAD

**否**（fake-driver / no-CAD）。

### 7. 机器可读证据路径

- 单测 artifact 目录；真实 CAD 跑 probe 时写入 `cad_capability_probe.json` 的 `write_guard` 字段。

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| save/delete/formal-layer 负向守卫可用 | non_cad_only / unit_test | **否** |

### 9. 剩余风险

- 真实 CAD 会话下 COM 若绕过 driver 直接 `doc.Save()` 仍依赖 AutoCAD 侧纪律；`03.4` 继续收紧 readback scope。

---

## A-LCAD-03.1（ActiveDocument snapshot）

**日期**：2026-05-26  
**性质**：CAD 安全与证据链 A 路线第 1 子包；记录连接前后 ActiveDocument 与 modelspace 摘要，不新增真实 CAD 几何结论。

### 1. 开发包名

`A-LCAD-03.1-ACTIVE-DOC-SNAPSHOT`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/cad_session_guard.py` | 新增 snapshot / compare / session guard report |
| `core/verification/cad_capability_probe.py` | 接入 `active_document_guard` 与 `active_document_snapshot.json` |
| `core/verification/fake_cad_driver.py` | 补 `FullName`、`Documents.Count` 供单测 |
| `tests/core/test_cad_session_guard.py` | 新增 6 项 session guard 单测 |
| `tests/core/test_cad_capability_probe.py` | 断言 guard 字段与 snapshot 文件 |
| `docs/planning/一键推进.md` 等状态文档 | 移出已完成包，下一包改为 03.2 |

### 3. 关键设计说明

- 连接前固定 `before_connect=blocked(cad_not_connected)`；连接后、写入后各采一次 snapshot。
- snapshot 含文档 `name` / `full_name` / `fingerprint`、preview 层实体计数、modelspace `type_counts` / `layer_counts` 摘要。
- `Documents.Count > 1` 时 session guard 状态为 `blocked`（多文档不确定）。
- 本包只做记录与比对，preview-only / no-save 硬门禁留给 `A-LCAD-03.2`~`03.3`。

### 4. 新增/修改测试

- `tests.core.test_cad_session_guard`（6 tests）
- `tests.core.test_cad_capability_probe`（扩展 guard 断言）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_cad_session_guard tests.core.test_cad_capability_probe -v
# 9 tests OK
```

### 6. 是否运行真实 CAD

**否**。本轮仅 fake-driver / no-CAD 单测；未声明新的 `geometry_verified`。

### 7. 机器可读证据路径

- 单测产物目录：`output/test_artifacts/`（由 `artifact_path` 生成）
- 真实 CAD 运行 capability probe 时，同目录会额外写出 `active_document_snapshot.json`

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| ActiveDocument 前后 snapshot 可写入 report | non_cad_only / unit_test | **否** |
| capability probe 已携带 `active_document_guard` | non_cad_only | **否** |

### 9. 剩余风险

- preview-only audit、no-save/no-delete 负向守卫仍未完成（`A-LCAD-03.2`~`03.3`）。
- 真实 CAD 会话下 multi-document / 文档切换行为尚未实跑验证。

---

## Codex 校验快速指引

1. 读本文对应开发包章节（9 项是否齐全）；第 8 项须为「结论 + 证据类型 + geometry_verified」表。  
2. 对照 `git diff` 与「修改文件列表」。  
3. 按 [`evidence_gate_handoff_rules.md`](../verification/evidence_gate_handoff_rules.md) §4 打开机器路径（`report.json` / `benchmark_summary.json`）。  
4. 禁止把截图、`dry_run_valid_plan_only` 或 `benchmark_pass_non_cad` 当成几何已验证。  
5. 能力边界以 `CORE_CONTEXT_BRIEF.md`「不能声称的事」为准。

---

## 进度估算（交接时快照）

```text
总进度：约 59%
Core 底座开发进度：约 73%
Agent 多场景实现进度：约 25%
```

*百分比仅作节奏参考，以测试与 `output/validation_runs` 证据为准。当前百分比按“真实工程可用度 / 场景产品化成熟度”估算，不把 non-CAD scene benchmark 直接算作 Scene Product 完成。*
