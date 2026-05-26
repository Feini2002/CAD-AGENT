# Phase R Rebirth Implementation Plan

状态：Phase R 执行剧本已细化  
最后同步：2026-05-26

> 本文是 Phase R 执行剧本，不是独立 PlanMD。优先级、待办和退出标准以根目录 `CORE_RESTRUCTURE_PLAN.md` 为准；本文只保留任务背景、拆单依据和执行参考。

## 执行边界

- Phase R 的目标是让下一轮通用底座开发更准，不是魔改系统。
- 当前系统仍是通用 CAD Agent Core Lab，不变成办公专用、工装专用或 CAD-MCP 专用项目。
- 场景 Agent 只做业务词汇、默认尺度、对象组合语义、候选排序权重和解释模板。
- Core 算法、CAD_PLAN、CAD 执行、截图、回读、验证、benchmark 总控必须留在 `core/`、`libraries/`、`examples/`、`tests/` 或 `docs/` 的对应位置。
- 本轮文档执行不改变功能成熟度百分比；后续只有形成可复验证据才调整进度。

## 证据状态词

| evidence_state | 含义 | 可以声称 | 不能声称 |
| --- | --- | --- | --- |
| `benchmark_pass_non_cad` | 非 CAD benchmark 跑通 | 结构化 pipeline / case 在无 CAD 下可复验 | 真实 CAD 几何准确 |
| `dry_run_valid_plan_only` | CAD_PLAN 校验和 dry-run 通过 | 计划结构和预演合法 | 实体已经画准 |
| `screenshot_captured_visual_only` | 截图已保存 | 有视觉辅助证据 | 几何已由截图证明 |
| `readback_geometry_verified` | 真实 CAD created handles 范围内回读通过 | 对该有限样本的几何准确有证据 | 任意 CAD_PLAN、真实块库或真实项目全量准确 |
| `blocked_expected_non_cad` | 失败样本按预期结构化 blocked / invalid | 系统能解释失败原因 | 系统能自动修复布局 |
| `deferred_cad_readback_required` | 需要真实 CAD 补验 | 当前有计划或 metadata | 当前已经 CAD 验证 |

报告中涉及无 CAD、dry-run 或截图时，必须显式写：

```json
{
  "geometry_accuracy": "not_verified_without_cad_readback",
  "screenshot_role": "visual_aid_only"
}
```

## R0-R6 总表

| 批次 | 目标 | 主要文档 | 状态 | 退出标准 |
| --- | --- | --- | --- | --- |
| R0 | 建立 Phase R 执行索引 | 本文 | `done_for_docs` | 有总表、任务编号、证据状态、同步清单 |
| R1 | CAD 能力契约 | `phase-r-cad-capability-contract.md` | `ready_for_implementation` | 图元和 block alpha 的 write-read-verify 契约清楚 |
| R2 | 图块库与制图标准路线 | `phase-r-block-library-roadmap.md` | `ready_for_implementation` | block metadata、OBJECT_SPEC、drawing standard profile 边界清楚 |
| R3 | 办公基础闭环 Alpha | `phase-r-office-benchmark-cases.md` | `partially_implemented_non_cad` | desk / chair / cabinet object cases 与第一条 office scene 可跑；微场景和失败样本仍需扩展 |
| R4 | Benchmark 与证据门禁 | 本文 + R1/R3/R6 | `partially_implemented_non_cad` | runner 已支持证据状态、最小指标、对象类型、组件角色、对象角色、object_spec / composition_spec pipeline、配置校验和每个 CAD_PLAN 的 dry-run / verification 汇总；更多 failure 分类待扩展 |
| R5 | 平台协作与新人接手 | `docs/governance/`、`docs/onboarding/` | `ready_for_use` | 新 agent 可从短入口理解边界和任务 |
| R6 | 角色驱动组合交付自检 | `examples/benchmarks/interior_delivery_benchmark.json`、`core/composition_engine/`、`scripts/run_composition_cad_check.py` | `limited_cad_batch_readback_verified` | 卧室床+地毯、餐桌组合、办公桌组合可生成组合规格、多 CAD_PLAN、dry-run、unverified verification 和 SVG/PNG 视觉辅助预览；3 个简单组合已补跑真实 AutoCAD batch readback，后续更多组合、真实块库和复杂家具符号仍 deferred |

## 实施顺序

| 顺序 | 任务组 | 先做 | 后做 | 验证 |
| --- | --- | --- | --- | --- |
| 1 | R-GOV | 文档入口、协作协议、first handoff | 状态文档同步 | 文档引用和占位词扫描 |
| 2 | R-CAD | 能力契约表、block alpha intent 草案 | schema / driver / readback 测试计划 | 先 non-CAD tests，再真实 CAD readback |
| 3 | R-BLOCK | `BLOCK_LIBRARY v0.2` 字段和受控测试块 metadata | block insertion dry-run / real CAD alpha | metadata validation、readback report |
| 4 | R-CAD-VIEW | AutoCAD 窗口级 / 视口级截图开发包 | runner 视觉辅助证据接入 | 截图干净可看，但仍不参与几何通过 |
| 5 | R-OFFICE | office 对象字段、benchmark cases | shell/workflow/runner 断言实现 | office alpha benchmark |
| 6 | R4 hard gate | 统一报告证据状态和 failure 分类 | 将门禁接入 runner | 不允许顶层 pass 掩盖未验证 |
| 7 | R-COMP | 角色需求组合模板、composition benchmark | 真实 CAD 批量执行与 readback | interior delivery benchmark；截图仅作为视觉辅助 |

## 下一轮文件级开发拆解

本节服务根目录 `CORE_RESTRUCTURE_PLAN.md` 的“下一轮开发拆解与子校验”。执行时按包推进，不要跳过子校验；一个包没有通过前，不把后续包的能力写成已完成。

### Package 1：`R-CAD-CONTRACT`

**目标**：把已验证的基础图元能力从“探针结果”提升为稳定契约，方便后续 block alpha 复用同一套字段和 failure class。

**文件范围**

- 修改：`docs/planning/phase-r-cad-capability-contract.md`
- 可能修改：`core/verification/cad_capability_probe.py`
- 可能修改：`core/verification/inspect_dwg.py`
- 测试：`tests/core/test_cad_capability_probe.py`
- 测试：`tests/core/test_cad_validation_runner.py`

**开发步骤**

- [x] 梳理 `line`、`rectangle`、`circle`、`arc`、`polyline`、`text`、`dimension` 的 expected / actual / checks 字段，补齐契约文档中字段名和容差。
- [x] 在测试里断言 capability probe 输出包含 `evidence_state`、`geometry_accuracy`、`screenshot_role` 或等价门禁字段；如果当前实现没有这些字段，先写失败测试。
- [x] 只做最小实现：probe 或 runner 的输出字段必须能被机器断言，不依赖 Markdown 解释。
- [x] 确认无真实 CAD 时不会误报 `geometry_verified`，而是进入 deferred 或 no-CAD 状态。

**执行记录（2026-05-26）**

- 新增 `core/verification/evidence_contract.py` 作为机器可读契约与证据词表；`cad_capability_probe`、`build_verification_report` 与 CAD validation runner 硬门禁已接入。
- `tests.core.test_cad_capability_probe`、`tests.core.test_cad_validation_runner`、`tests.core.test_verification_report` 通过。
- `scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\r-cad-contract-no-cad`：`status=pass`。

**子校验**

```powershell
& $py -m unittest tests.core.test_cad_capability_probe tests.core.test_cad_validation_runner tests.core.test_geometry_checks
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\r-cad-contract-no-cad
```

**通过标准**

- non-CAD 测试通过。
- 报告字段能区分 `cad_capability_verified`、`readback_geometry_verified` 和 `not_verified_without_cad_readback`。
- 文档没有声称 block insertion、真实块库或任意 CAD_PLAN 已验证。

### Package 2：`R-BLOCK-METADATA`

**目标**：定义 `BLOCK_LIBRARY v0.2` 与受控测试块 metadata，让后续 block intent 有稳定输入。

**文件范围**

- 修改：`core/schemas/block_library.schema.json`
- 修改：`libraries/blocks/block_library.example.json`
- 修改：`core/block_engine/block_library.py`
- 修改：`core/block_engine/block_selector.py`
- 测试：`tests/core/test_block_engine.py`
- 测试：`tests/core/test_schema_validation.py`

**开发步骤**

- [x] 为 `BLOCK_LIBRARY v0.2` 增加 `units`、`source`、`cad_identity`、`anchor_points`、`footprint_2d`、`clearance_zones`、`layer_bindings`、`validation` 字段。
- [x] 在 `libraries/blocks/block_library.example.json` 中只放受控测试块和 symbol fallback，不引用真实公司块库。
- [x] loader 保持兼容：旧 `0.1` 示例若仍存在，要么可读，要么给出结构化 schema error。
- [x] selector 能按 `category`、`domain`、`tags`、`validation.status` 过滤。
- [x] fallback object spec 仍可用，不能因为 block metadata 缺失而破坏 blank-shell pipeline。

**执行记录（2026-05-26）**

- `libraries/blocks/block_library.example.json` 升级为 `0.2`，新增 `controlled-test-block-001`（`CODEX_TEST_BLOCK_001`）与其余 `symbol_fallback` 元数据块。
- 新增 `object_spec_to_block_reference()`、`normalize_block()`、`validate_block_library()`；`0.1` 示例 `examples/block_libraries/minimal_builtin_blocks.json` 仍可加载。
- `234 tests OK`；`run_repo_audit.py --fail-on-findings` 0 findings；`blank_shell_core_benchmark` pass；`run_cad_validation.py --no-cad --output-dir output\validation_runs\r-block-metadata-no-cad` pass。

**子校验**

```powershell
& $py -m unittest tests.core.test_block_engine tests.core.test_schema_validation
& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
```

**通过标准**

- block metadata 正反例可被 schema 校验。
- 受控测试块能被 selector 找到。
- 现有 blank-shell benchmark 不因 metadata 扩展回归。

### Package 3：`R-BLOCK-PLAN`

**目标**：增加受控 `insert_block_alpha` CAD_PLAN intent，让 validate、dry-run 和 fake driver 能先跑通。

**文件范围**

- 修改：`core/schemas/cad_plan.schema.json`
- 修改：`schemas/cad_plan.schema.json`
- 修改：`core/plan_engine/validate_plan.py`
- 修改：`core/plan_engine/dry_run_plan.py`
- 修改：`core/execution/execute_plan.py`
- 测试：`tests/core/test_plan_engine.py`
- 测试：`tests/core/test_execute_plan.py`
- 示例：`examples/plans/insert_block_alpha_test.json`

**开发步骤**

- [x] 新增最小合法 `insert_block_alpha` 示例，字段只包含 `block_id`、`block_name`、`base_point`、`rotation`、`scale`、`layer` 和可选 `attributes`。
- [x] 新增 invalid fixture：缺 `block_name`、越权 layer、非法 scale、非 preview 写入。
- [x] validate 阶段拒绝正式图层、空 block identity 和缺 base point。
- [x] dry-run 阶段输出 bbox / anchor / rotation / layer role 检查，且写明 `geometry_accuracy=not_verified_without_cad_readback`。
- [x] fake execution driver 只记录 block insert call，不触碰真实 CAD。

**执行记录（2026-05-26）**

- 新增 `core/plan_engine/block_alpha_plan.py`、`examples/plans/insert_block_alpha_test.json`；`validate_plan` / `dry_run_report` / `execute_plan` 已支持 `insert_block_alpha`。
- `scripts\validate_plan.py` 与 `scripts\dry_run_plan.py` 对示例 plan 通过；相关单测 19 项 OK；全量 `unittest discover -s tests` 通过；`run_cad_validation.py --no-cad --output-dir output\validation_runs\r-block-plan-no-cad` pass。

**子校验**

```powershell
& $py scripts\validate_plan.py examples\plans\insert_block_alpha_test.json
& $py scripts\dry_run_plan.py examples\plans\insert_block_alpha_test.json
& $py -m unittest tests.core.test_plan_engine tests.core.test_execute_plan tests.core.test_validation_edges
```

**通过标准**

- 合法 block alpha plan 通过 validate / dry-run。
- 非 preview、缺 identity、非法 scale 的 plan 失败且有明确错误。
- fake driver 有可断言的 `insert_block_alpha` 调用记录。

### Package 4：`R-BLOCK-CAD-ALPHA`

**目标**：只在用户会话真实 AutoCAD 中验证受控测试块插入，不接真实公司块库。

**文件范围**

- 修改：`core/cad_io/autocad_com.py`
- 修改：`core/verification/inspect_dwg.py`
- 修改：`core/verification/cad_validation_runner.py`
- 修改：`scripts/run_cad_validation.py`
- 测试：`tests/core/test_autocad_com_driver.py`
- 测试：`tests/core/test_cad_validation_runner.py`
- 证据：`docs/verification/` 或 `output/validation_runs/`

**开发步骤**

- [ ] `AutoCADComDriver` 增加最小 `insert_block_alpha` 方法，找不到受控块定义时必须结构化失败。
- [ ] readback normalize 支持 `block_reference`，至少输出 `handle`、`type`、`block_name`、`insertion_point`、`rotation`、`scale`、`layer`、`bbox`。
- [ ] validation runner 增加 block alpha step，但默认在无 CAD 环境下跳过并标记 deferred。
- [ ] 真实 CAD 验证只写 `CODEX_PREVIEW`，记录本轮 created handles，不扫描全 ModelSpace。
- [ ] 截图只挂为视觉辅助，不参与几何通过判断。

**子校验**

```powershell
& $py -m unittest tests.core.test_autocad_com_driver tests.core.test_cad_validation_runner
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\r-block-alpha-no-cad
& $py scripts\run_cad_validation.py --output-dir output\validation_runs\r-block-alpha-cad
```

**通过标准**

- no-CAD 路径不误报真实 CAD 通过。
- 真实 CAD 路径必须有非空 created handles。
- readback checks 全部 pass 后，才允许 `evidence_state=readback_geometry_verified`。

### Package 5：`R-CAD-VIEW-CAPTURE`

**目标**：把现有全屏截图升级为 AutoCAD 窗口级 / 视口级视觉辅助截图。优先截取 AutoCAD 客户区或绘图区；在有本轮 created handles 时，先按 handles 回读 bbox 缩放视图，再截图。该包对应此前讨论中的 `W-SCREENSHOT-CAD-WINDOW` 诉求，但纳入 Phase R 的 CAD 证据链加固中执行。

**文件范围**

- 修改：`core/verification/render_preview.py`
- 修改：`scripts/render_preview.py`
- 可能修改：`core/cad_io/autocad_com.py`
- 可能修改：`core/verification/cad_validation_runner.py`
- 测试：`tests/core/test_render_preview.py`
- 测试：`tests/core/test_cad_validation_runner.py`
- 证据：`output/validation_runs/<run>/cad-validation-window.png` 或同等窗口级截图路径

**开发步骤**

- [x] 为 `render_preview.py --check` 增加结构化能力字段，至少区分 `screen`、`autocad_window`、`autocad_viewport_or_client`，无 CAD 环境时不得误报窗口级能力 ready。
- [x] 增加 AutoCAD 主窗口定位逻辑：优先使用 `win32gui` 枚举可见窗口并匹配 `Autodesk AutoCAD` / 活动 DWG 标题；失败时输出 `screenshot_failed` 可读原因，不把失败归为几何问题。
- [x] 增加窗口级截图入口，例如 `--capture-autocad-window` 或等价模式；截图范围应避开 Codex 窗口遮挡，至少截 AutoCAD 主窗口客户区。
- [x] 增加实体范围截图入口：当 runner 提供本轮 `created_handles` 或 readback bbox 时，可先调用 AutoCAD 视图缩放到本轮实体范围，再生成视觉辅助截图。
- [x] `run_cad_validation.py` 接入新截图模式时，仍必须把截图标记为 `screenshot_role=visual_aid_only`，不得让截图参与 `geometry_verified` 判定。
- [x] 保留全屏截图作为 fallback；fallback 发生时，报告必须显式写出截图可能被其他窗口遮挡。

**子校验**

```powershell
& $py -m unittest tests.test_render_preview tests.core.test_cad_validation_runner
& $py scripts\render_preview.py --check
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\r-cad-view-no-cad
& $py scripts\run_cad_validation.py --output-dir output\validation_runs\r-cad-view-cad
```

**执行记录（2026-05-26）**

- `tests.core.test_render_preview` + `tests.core.test_cad_validation_runner`：11 tests OK。
- `scripts\render_preview.py --check`：无可用 AutoCAD 窗口时只报告 `screen`，不误报 `autocad_window` ready。
- `scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\r-cad-view-no-cad`：`status=pass`，内含 `unittest discover -s tests` 227 tests OK。
- `scripts\run_cad_validation.py --output-dir output\validation_runs\r-cad-view-cad`：`status=pass`；截图 `output\validation_runs\r-cad-view-cad\cad-validation-window.png`；截图 stdout 记录 `mode=autocad_window`、`focus.status=zoomed_to_bbox`、`handle_count=7`；`readback_report.json.status=geometry_verified`。

**通过标准**

- 无 CAD 环境下 `--check` 不误报 AutoCAD 窗口级截图 ready。
- 有真实 AutoCAD 时，窗口级截图文件存在，且截图范围不包含 Codex 主窗口遮挡。
- 若有 created handles bbox，截图前视图缩放到本轮实体范围或报告明确说明为何无法缩放。
- `readback_report.json.status=geometry_verified` 的门槛仍只依赖 created handles 回读，不依赖截图。

### Package 6：`R-OFFICE-MICRO`

**目标**：把 office alpha 从对象级 + 单 scene 扩到对象、微场景、场景和失败样本四类 benchmark。

**文件范围**

- 修改：`examples/benchmarks/office_alpha_benchmark.json`
- 新增或修改：`examples/shell_models/*.json`
- 新增或修改：`examples/workflows/*.json`
- 修改：`core/benchmarks/runner.py`
- 测试：`tests/core/test_benchmarks.py`
- 测试：`tests/core/test_benchmark_cli.py`

**开发步骤**

- [ ] 新增 `computer_desk_default_spec`、`storage_cabinet_front_clearance`、`single_desk_chair_pair`。
- [ ] 新增长条办公室、入口净空、障碍避让相关 shell / workflow 样本。
- [ ] 新增失败样本 `too_small_room_for_workstation`、`door_clearance_conflict`、`cabinet_pullback_conflict`。
- [ ] runner 支持断言 `blocked_reason`、`clearance_refs`、`failure_category`。
- [ ] 所有无 CAD case 都必须输出 `geometry_accuracy=not_verified_without_cad_readback`。

**子校验**

```powershell
& $py -m unittest tests.core.test_benchmarks tests.core.test_benchmark_cli
& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\office_alpha_r_micro
```

**通过标准**

- office benchmark 覆盖 object / micro-scene / scene / failure 四类。
- 失败样本不能静默减少对象后返回 pass，必须是 `blocked_expected_non_cad` 或 `invalid`。
- benchmark summary 可机器读取通过数、失败分类和证据状态。

### Package 7：`R4-EVIDENCE-GATES`

**目标**：统一证据状态和失败分类，防止“顶层 pass 掩盖未验证”。

**文件范围**

- 修改：`core/benchmarks/runner.py`
- 修改：`core/verification/verification_report.py`
- 修改：`core/verification/cad_validation_runner.py`
- 测试：`tests/core/test_benchmarks.py`
- 测试：`tests/core/test_verification_report.py`
- 测试：`tests/core/test_cad_validation_runner.py`

**开发步骤**

- [ ] 固化 `benchmark_pass_non_cad`、`dry_run_valid_plan_only`、`readback_geometry_verified`、`blocked_expected_non_cad`、`deferred_cad_readback_required`。
- [ ] 所有 benchmark actual 都输出 `evidence_state`、`geometry_accuracy`、`screenshot_role`。
- [ ] runner 对 failure case 增加 expected blocked / invalid 断言。
- [ ] CAD runner 顶层 `pass` 必须依赖 readback / capability 子报告硬门禁。

**子校验**

```powershell
& $py -m unittest tests.core.test_benchmarks tests.core.test_verification_report tests.core.test_cad_validation_runner
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\r4_blank_shell
& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\r4_office
& $py scripts\run_benchmark_suite.py examples\benchmarks\interior_delivery_benchmark.json --output-root output\test_artifacts\benchmarks\r4_interior
```

**通过标准**

- benchmark 与 CAD validation 报告中的证据词一致。
- 无 CAD benchmark 永远不会显示几何已验证。
- blocked / invalid failure case 可被 expected assertions 断言。

### Package 8：`Y-MULTI-CANDIDATE`

**目标**：让 blank-shell pipeline 不只输出一条主候选，而是输出可解释的多候选、比较摘要和失败原因分布。

**文件范围**

- 修改：`core/workflows/blank_shell_pipeline.py`
- 修改：`core/layout_engine/placement.py`
- 修改：`core/proposal_engine/design_proposal.py`
- 修改：`examples/benchmarks/blank_shell_core_benchmark.json`
- 测试：`tests/core/test_blank_shell_pipeline.py`
- 测试：`tests/core/test_proposal_multi_candidate.py`

**开发步骤**

- [ ] pipeline 保留多个 circulation / zone / placement 候选，而不是只把 best candidate 写入 layout。
- [ ] proposal 输出候选评分、失败原因、对象覆盖率、通道连续性摘要。
- [ ] benchmark 增加 `candidate_count >= 2`、`comparison_summary`、`failed_reason_distribution` 断言。
- [ ] 失败样本保留 blocked reason，不通过少放对象伪装成功。

**子校验**

```powershell
& $py -m unittest tests.core.test_blank_shell_pipeline tests.core.test_proposal_multi_candidate
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\y_multi_candidate
```

**通过标准**

- 至少 4 个 blank-shell benchmark 仍通过。
- 每个 case 有多个候选或结构化说明为什么只有一个候选。
- 报告明确 non-CAD 几何未验证。

### Package 9：`X-SCENE-ALPHA`

**目标**：验证至少 3 个场景复用同一 Core pipeline，场景层只提供轻量差异。

**文件范围**

- 修改：`agents/*/preferences.json`
- 修改：`agents/*/rules.md`
- 修改：`examples/benchmarks/*.json`
- 测试：`tests/agents/test_scene_preferences.py`
- 测试：`tests/agents/test_scene_agent_boundaries.py`

**开发步骤**

- [ ] 选择至少 3 个场景，例如 office、residential、restaurant。
- [ ] 为每个场景定义 preferences 差异、对象排序权重和解释模板，不写算法。
- [ ] 同一 Core pipeline 跑通多场景 benchmark。
- [ ] agent boundary test 扫描禁止项：CAD 执行、readback、碰撞算法、几何库调用。

**子校验**

```powershell
& $py -m unittest tests.agents.test_scene_preferences tests.agents.test_scene_agent_boundaries
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\x_scene_alpha
```

**通过标准**

- 至少 3 个场景 benchmark 复用 Core pipeline。
- preferences 差异能被测试观察到。
- 场景层没有实现 Core 算法、CAD 执行或 readback。

## 任务清单

| 编号 | 任务 | 交付物 | 依赖 |
| --- | --- | --- | --- |
| R-GOV-01 | 建立 Phase R 执行总表 | 本文 | 无 |
| R-GOV-02 | 固化多 agent 角色、可写边界、交付物和冲突处理 | `docs/governance/multi-agent-contribution.md` | 无 |
| R-GOV-03 | 编写新人 first handoff | `docs/onboarding/first-handoff.md` | 无 |
| R-GOV-04 | 固定证据状态命名 | 本文、R1、R3 | 无 |
| R-GOV-05 | 定义每轮同步 checklist | 本文 | 无 |
| R-CAD-01 | 写入 CAD 实体能力契约表 | `phase-r-cad-capability-contract.md` | Phase W baseline |
| R-CAD-02 | 设计 `insert_block_alpha` 最小 intent | `phase-r-cad-capability-contract.md` | R-BLOCK-01 |
| R-CAD-03 | 定义 block reference readback 字段和验收报告字段 | `phase-r-cad-capability-contract.md` | R-CAD-02 |
| R-CAD-04 | 列出 deferred verification | `phase-r-cad-capability-contract.md` | 无 |
| R-CAD-VIEW-01 | 定义 AutoCAD 窗口级截图能力字段和失败分类 | `core/verification/render_preview.py`、`tests/core/test_render_preview.py` | Phase W screenshot baseline |
| R-CAD-VIEW-02 | 增加 AutoCAD 主窗口定位和客户区截图入口 | `core/verification/render_preview.py`、`scripts/render_preview.py` | R-CAD-VIEW-01 |
| R-CAD-VIEW-03 | 支持按 created handles bbox 缩放视图后截图 | `core/cad_io/autocad_com.py`、`core/verification/cad_validation_runner.py` | R-CAD-VIEW-02 |
| R-CAD-VIEW-04 | 将窗口级截图接入 CAD validation 但保留 visual-aid-only 语义 | `core/verification/cad_validation_runner.py`、`tests/core/test_cad_validation_runner.py` | R-CAD-VIEW-03 |
| R-BLOCK-01 | 定义 `BLOCK_LIBRARY v0.2` 字段矩阵 | `phase-r-block-library-roadmap.md` | 无 |
| R-BLOCK-02 | 定义 OBJECT_SPEC 到 block reference 的接口 | `phase-r-block-library-roadmap.md` | R-BLOCK-01 |
| R-BLOCK-03 | 建立最小 `drawing_standard_profile` 路线 | `phase-r-block-library-roadmap.md` | 无 |
| R-BLOCK-04 | 规划受控测试块，不接真实公司块库 | `phase-r-block-library-roadmap.md` | R-BLOCK-01 |
| R-OFFICE-01 | 定义 office 最小对象字段 | `phase-r-office-benchmark-cases.md` | 无 |
| R-OFFICE-02 | 设计 office alpha benchmark cases | `phase-r-office-benchmark-cases.md` | R-OFFICE-01 |
| R-OFFICE-03 | 定义失败样本门槛 | `phase-r-office-benchmark-cases.md` | R-OFFICE-02 |
| R-OFFICE-04 | 规定 office agent 禁止事项 | `phase-r-office-benchmark-cases.md` | 无 |
| R-COMP-01 | 建立通用 composition engine，不把组合写入单一场景 agent | `core/composition_engine/` | R4 |
| R-COMP-02 | 建立 interior delivery persona benchmark | `examples/benchmarks/interior_delivery_benchmark.json` | R-COMP-01 |
| R-COMP-03 | 为组合输出多 CAD_PLAN、dry-run、unverified verification 与视觉辅助预览 | benchmark artifacts | R-COMP-01 |
| R-COMP-04 | 将组合从 non-CAD visual aid 推进到真实 CAD created handles readback | 已有 `output\validation_runs\interior-composition-cad-label-clean-y8000\composition_cad_check_report.json`；后续扩展更多组合和 block insertion | R-CAD |

## 每轮完成后的同步清单

| 文件 | 同步内容 |
| --- | --- |
| `README.md` | 同步用户向入口、当前主线和 Phase R 执行入口 |
| `CORE_CONTEXT_BRIEF.md` | 只同步短结论、入口和不能声称 |
| `CORE_RESTRUCTURE_PLAN.md` | 同步 Phase 状态、可信基线、Decision Gate、执行入口 |
| `CORE_ROADMAP.md` | 同步高层路线入口，不写执行细节 |
| `CORE_STATUS.md` | 同步能力成熟度、证据、主要缺口；无功能证据时不调百分比 |
| `CAD_AGENT_STATUS.md` | 同步当前阶段、最近验证、最重要缺口 |
| `CAD_AGENT_CHANGELOG.md` | 追加结构、规则、脚本、状态变更 |
| `CAD_AGENT_ISSUES.md` | 只有失败、回归、风险或排障教训才更新 |
| `docs/planning/README.md` | 新增或迁移计划文档时更新 |

## 停止条件

遇到下面情况应停止执行并登记问题或询问用户：

- 需要修改正式图层、保存、覆盖或删除 DWG。
- 要接入真实公司块库路径或真实项目敏感资料。
- 要把场景 Agent 写成 Core 算法层。
- 要引入新的几何库、CAD 依赖或安装步骤。
- 真实 CAD readback 无法证明几何准确，但任务要求声明“画准了”。

## 当前结论

Phase R 已从“新鲜视角评审”推进到“可执行开发包”。当前优先顺序已收束到 `CORE_RESTRUCTURE_PLAN.md` 的“当前活跃工作队列”，本文保留原始拆分参考：

1. R-CAD：把现有基础图元探针固化为正式能力契约。
2. R-BLOCK：用受控测试块启动 block insertion alpha，不碰真实公司块库。
3. R-CAD-VIEW：窗口级截图 baseline 已把全屏截图升级为 AutoCAD 客户区视觉辅助证据，避免 Codex 窗口遮挡；后续扩展更细绘图区裁剪、多显示器和遮挡边界；几何准确仍只看 created handles readback。
4. R-COMP：`interior_delivery_benchmark.json` 已覆盖卧室床+地毯、餐桌组合、办公桌组合 3 个 persona composition cases；这些组合已经补跑真实 CAD 批量执行与 created handles readback，后续只能扩展到更多组合，不能把当前 3 个简单组合扩大为真实家具块库能力。
5. R-OFFICE：`office_alpha_benchmark.json` 已覆盖 desk / chair / cabinet object spec 与第一条 office scene；继续把电脑桌、入口、通道、micro-scene 和失败样本扩成多 case benchmark。
6. R4：runner 已开始区分 non-CAD、截图和真实 readback；后续要把 blocked / invalid failure 分类也纳入硬门禁。
