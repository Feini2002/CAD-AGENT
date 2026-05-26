# Core Status

最后更新：2026-05-26

本文是通用 CAD Agent Core Lab 的能力状态页。它只回答“当前能力成熟到哪里、证据是什么、缺口是什么”，不承载长历史和独立计划；历史变更看 `CAD_AGENT_CHANGELOG.md`，唯一 `PlanMD` / 主计划看 `CORE_RESTRUCTURE_PLAN.md`。

## 状态口径

| 状态 | 含义 |
| --- | --- |
| `alpha_ready_non_cad` | 非 CAD 链路已有稳定入口、测试和基线证据，可作为 Alpha 原型使用 |
| `alpha_verified_cad` | 已对有限 baseline CAD_PLAN 完成真实 AutoCAD 落图、截图、实体回读和 `geometry_verified` 闭环 |
| `prototype` | 已有最小实现或脚本原型，但接口、样本或验证仍需增强 |
| `blocked_by_cad` | 仓库内入口已存在，但完成声明依赖真实 CAD 落图、截图辅助或实体回读；几何准确声明以实体回读为准 |
| `scaffold` | 目录、文档或数据壳已建立，核心能力尚未形成 |
| `not_started` | 仅在计划中定义，尚未开始 |
| `blocked` | 缺依赖、缺证据或有已知失败，不能继续声称可用 |

## Core / 场景成熟度口径

本页从 2026-05-26 起把“通用底座进度”和“具体场景 Agent 产品化进度”分开估算，避免把场景 preferences 或 non-CAD benchmark 误当成业务场景已完成。

| 层级 | 当前含义 | 本仓库当前判断 |
| --- | --- | --- |
| Core 底座 | 通用 schema、workflow、CAD_PLAN、执行、验证、benchmark、读图、对象、图块和安全门禁 | Alpha 原型较厚，有限真实 CAD 样本已通过，但真实项目和公司块库仍不足 |
| Scene Alpha 壳层 | preferences、词汇、默认参数、排序权重、解释模板和边界扫描 | office / residential / restaurant 已完成 Alpha 验收 |
| Scene Beta 能力包 | 某场景对象、微场景、failure benchmark 和 non-CAD 证据 | office / residential / restaurant 已有 non-CAD beta benchmark |
| Scene Product 场景产品 | 真实项目样本、图块策略、真实 CAD smoke、用户确认流和交付边界 | 尚未完成；工装等具体场景需要后续专项开发 |

## 当前总状态

### 2026-05-26 Codex 复杂 CAD smoke 与全量 strict regression 已完成

```text
466 tests OK (real CAD baseline sub-run)
complex CAD smoke no-CAD: output\validation_runs\complex-cad-smoke-no-cad
complex CAD smoke real CAD: output\validation_runs\complex-cad-smoke-real-final
full strict CAD matrix: output\validation_runs\complex-cad-regression-strict-final
strict matrix summary: selected_case_count=4, step_count=5, geometry_verified_case_count=7, created_handle_count=113
complex smoke summary: created_handle_count=23, bbox=3600 x 2200, type_counts={line:11, polyline:1, circle:3, arc:2, text:4, dimension:2}
```

本轮按用户要求重新校验 CAD 测试层是否能绘制更复杂图形，并把复杂图形 smoke 纳入默认本地 CAD regression manifest。`complex_cad_smoke` 在 `CODEX_PREVIEW` 中绘制外框、网格、斜线、开放多段线、圆、弧、文字和标注，随后按 created handles 定向回读并校验类型统计、图层和 bbox。真实 CAD 单项与全量 strict regression 均通过；截图 `output\validation_runs\complex-cad-smoke-real-final\complex-cad-smoke-window.png` 只作为视觉辅助，不替代 readback。该能力仍只代表受控测试图形和当前测试会话，不扩大为任意真实 DWG、公司块库、属性块、hatch 或完整场景产品能力。

### 2026-05-26 Codex LCAD-02 strict matrix runner 已完成

```text
461 tests OK (real CAD baseline sub-run)
selected no-CAD run: output\validation_runs\lcad-02-selected-project-sample-no-cad
strict all CAD run: output\validation_runs\lcad-02-strict-all-cad
strict all summary: selected_case_count=3, step_count=4, geometry_verified_case_count=6, created_handle_count=90
```

本轮完成 `LCAD-02-STRICT-MATRIX-RUNNER`：本地 CAD regression runner 现在支持按 manifest case id 选择执行（`--case` 可重复）、默认 all-case 执行、`--strict` 严格别名，以及统一 rollup 字段 `manifest_case_count`、`selected_case_count`、`selected_case_ids`、`strict`。selected no-CAD run 证明可以只跑 `project_sample_cad_check` 而不触发 baseline 或 composition；真实 CAD strict all run 证明默认全量 manifest case 仍可在当前测试会话下产生 created-handle readback。下一缺口是 `LCAD-03` 的 ActiveDocument / no-save / no-delete 前后守卫。

### 2026-05-26 Codex LCAD-01 regression manifest 已完成

```text
459 tests OK (real CAD baseline sub-run)
local CAD regression manifest no-CAD pass: output\validation_runs\lcad-01-manifest-no-cad
local CAD regression strict CAD smoke pass: output\validation_runs\lcad-01-manifest-cad-smoke
strict CAD smoke summary: step_count=4, geometry_verified_case_count=6, created_handle_count=90
```

本轮完成 `LCAD-01-REGRESSION-MANIFEST`：新增 `core/schemas/cad_regression_manifest.schema.json`、默认 manifest 示例和 manifest loader 校验，矩阵报告现在会带上 manifest metadata。LCAD-01 初版 manifest 覆盖 baseline CAD validation、project sample CAD check 和 interior composition CAD check 三个 case；每个 case 必须声明是否需要真实 CAD、期望 evidence state、输出路径、入口命令和 `CODEX_PREVIEW` 安全边界。用户明确允许当前测试 CAD 文件可写入/编辑后，已额外跑通真实 CAD strict smoke，当时测试会话下生成 6 个 `geometry_verified` case 和 90 个 created handles；后续 complex smoke 已把默认 manifest 扩为 4 case。本结论只覆盖对应 manifest 和测试会话，不扩大为任意项目 DWG、公司块库或完整场景产品能力。

### 2026-05-26 Codex 本地真实 CAD 校验扩样主线写入 PlanMD

本轮按用户要求只做主计划层面的构思和拆包，不新增真实 CAD 执行证据。`CORE_RESTRUCTURE_PLAN.md` 已新增“本地真实 CAD 校验扩样主线”：先定义环境与安全守卫、baseline 回归、基础实体矩阵、CAD_PLAN fixture suite、block / attribute / hatch、样本项目闭环、多场景组合、负向安全、视觉辅助一致性、趋势和审计 10 类测试方向；再拆分 `LCAD-01` 到 `LCAD-11` 小任务包。该计划明确下一轮默认优先补真实 AutoCAD 用户会话下的 `geometry_verified` 样本，不允许用 non-CAD benchmark、截图或 fake driver 替代真实几何证据。

### 2026-05-26 Codex 本地 CAD 回归矩阵加固

```text
456 tests OK
local CAD regression no-CAD pass: output\validation_runs\local-cad-regression-no-cad
local CAD regression summary: step_count=3, deferred_case_count=2, geometry_verified_case_count=0
```

本轮新增 `core/verification/local_cad_regression.py` 与 `scripts/run_local_cad_regression.py`，把 baseline CAD validation、project sample CAD check 和 interior composition CAD check 收拢为本地 CAD 回归矩阵。默认 `--no-cad` 模式不连接 AutoCAD，只输出可机器读取的 deferred / non-CAD 证据；真实 CAD 严格模式可加 `--require-cad-verified`，任一子项不是 `geometry_verified` 就会失败。composition CAD check 现在受前置 benchmark artifact 门禁保护，benchmark 未通过时不会继续写入 CAD。本轮未运行真实 AutoCAD，不新增 `geometry_verified` 结论。

### 2026-05-26 Codex 进入下一阶段前雕琢

```text
452 tests OK
repo audit 0 findings
run_cad_validation.py --no-cad pass: output\validation_runs\codex-polish-final-no-cad
blank-shell benchmark 8/8 pass (non-CAD)
office alpha benchmark 18/18 pass (non-CAD)
interior delivery benchmark 3/3 pass (non-CAD)
project sample benchmark 2/2 pass (non-CAD)
proposal confirmed benchmark 2/2 pass (non-CAD)
CAD beta evidence rollup 5/5 pass (non-CAD rollup)
office/residential/restaurant scene beta benchmark 25/25 pass (non-CAD)
```

本轮是进入下一开发阶段前的维护雕琢，不新增真实 CAD 能力结论。已修复活跃排障手册硬编码固定 Windows 用户目录的 CAD-MCP Python 路径问题，改为 `$env:USERPROFILE` 派生；scene beta 三个 CLI wrapper 保留 `--output`，同时兼容通用 benchmark 习惯的 `--output-root`。新增回归测试锁定这两类可迁移性 / 易用性边界。本轮未运行真实 CAD，不新增 `geometry_verified` 结论。上述 scene beta 仍属于 non-CAD 场景能力包，不等于具体办公、住宅、餐饮或工装 Agent 已产品化。

### 2026-05-26 Codex 维护 4-7 包：结构整理和优化

```text
450 tests OK
repo audit 0 findings
focused 4-7 package tests 46 OK
run_cad_validation.py --no-cad pass: output\validation_runs\codex-maintenance-4-7-no-cad
```

本轮把 1-3 包止血后的安全边界整理为可复用结构：新增 `core/path_safety.py`，统一 project root / output root / safe path segment 校验；project sample CAD check、composition CAD check、beta suite、proposal confirmed、drawing-read、blank-shell / non-CAD pipeline 等入口在连接真实 CAD 或写 artifact 前先拒绝越界路径。`core/schemas/*.schema.json` 已全部纳入 registry 和 invalid fixture 覆盖；handoff、状态页和 PlanMD 口径已去除“下一包/剩余表”副计划，后续优先级继续只以 `CORE_RESTRUCTURE_PLAN.md` 为准。本轮未运行真实 CAD，不新增 `geometry_verified` 结论。

### 2026-05-26 Codex 维护 1-3 包：先止血、再加固

```text
432 tests OK
repo audit 0 findings
focused 1-3 package tests 48 OK
run_cad_validation.py --no-cad pass: output\validation_runs\codex-maintenance-fix-no-cad
blank-shell benchmark 8/8 pass (non-CAD)
office alpha benchmark 18/18 pass (non-CAD)
interior delivery benchmark 3/3 pass (non-CAD)
project sample strict no-CAD check returns 1 with deferred report
```

本轮补上三类维护边界：`run_project_sample_cad_check.py --require-cad-verified` 防止把 no-CAD deferred 当作真实 CAD 几何通过；`projects/` 样本 manifest 输入路径限制在样本目录内；benchmark / drawing-read case_id 与 output root、CAD validation output dir 均限制在安全边界内。当前仓库存档的 `BETA-PROJECT-SAMPLE-05` no-CAD 报告仍是 `deferred`，不是真实 AutoCAD `geometry_verified`；真实样本 CAD 几何声明必须另跑用户会话下的 created-handle readback。

### 2026-05-26 Codex 深度全量安全复盘

```text
424 tests OK
repo audit 0 findings
Python AST parse 248 files / 0 errors
JSON parse 166 files / 0 errors
project sample protocol scan pass, 2 samples
project sample benchmark pass, 2/2 cases
proposal confirmed benchmark pass, 2/2 cases
CAD beta evidence rollup pass, 5/5 subpackages
office scene beta benchmark pass, 9/9 cases
residential scene beta benchmark pass, 8/8 cases
restaurant scene beta benchmark pass, 8/8 cases
```

Cursor 大改后的深度复盘已完成一轮加固：benchmark expected evidence triplet 现在强制包含 `evidence_state` / `geometry_accuracy` / `screenshot_role`，proposal confirmed benchmark 输出并校验 `evidence_summary`；项目样例 CAD check 和 drawing standard profile 已回到统一 evidence vocabulary；repo audit 暴露的 6 个大文件职责风险已拆为小模块。该轮结论仍主要证明 non-CAD benchmark、样本协议、证据门禁和有限 CAD 验证链路，不扩大为真实项目 DWG 或任意 CAD_PLAN 全量几何准确。

### 2026-05-26 Codex 风险验收补记

```text
290 tests OK
repo audit 0 findings
office alpha benchmark 14/14 pass (non-CAD)
run_cad_validation.py --no-cad --block-alpha-only pass with block_alpha_deferred_evidence
real CAD block alpha pass: output\validation_runs\codex-review-block-alpha-cad-after-gate
real CAD full validation pass: output\validation_runs\codex-review-full-cad-after-gate
negative COM probe pass: arbitrary block_id/name rejected, CODEX_PREVIEW entity count 111 -> 111
second gate real CAD block alpha pass: output\validation_runs\codex-second-gate-block-alpha-cad-final
second gate real CAD full validation pass: output\validation_runs\codex-second-gate-full-cad-final
second gate negative COM probe pass: illegal identity/attributes/base_point rejected, ModelSpace count 131 -> 131
```

本轮将 block alpha 和 CAD readback 证据门禁从“字段自报”加固为 created-handle 绑定：`geometry_verified` 必须有非空 `created_handles`、实体回读 payload 和 `created_handles_scope=pass`；block alpha 还必须证明 `entity.type=block_reference`。该结论仍只覆盖受控样本和当前测试 CAD 会话，不扩大到真实块库、属性块、正式图层或任意项目图纸。

当前 Core 已完成 Phase O-V 的非 CAD 主线和一次系统层安全补强。最新记录为：

```text
452 tests OK
self_check.py pass
render_preview.py --check ready
repo audit 0 findings
focused 4-7 package tests 46 OK
Python AST parse 248 files / 0 errors
JSON parse 166 files / 0 errors
blank-shell pipeline ok
office/residential/restaurant scene beta benchmark 25/25 cases pass
project sample benchmark 2/2 cases pass
proposal confirmed benchmark 2/2 cases pass
CAD beta evidence rollup 5/5 subpackages pass
interior delivery real CAD composition check 3/3 geometry_verified
project sample strict no-CAD check rejected deferred as expected
run_cad_validation.py --no-cad pass
run_cad_validation.py --no-cad pass: output\validation_runs\codex-polish-final-no-cad
Phase W W-07 CAD foundation run_cad_validation.py pass
R-BLOCK-PLAN insert_block_alpha validate/dry-run/fake execute
R-BLOCK-CAD-ALPHA real CAD block alpha geometry_verified (controlled sample)
R-BLOCK-METADATA BLOCK_LIBRARY v0.2 + controlled-test-block-001 metadata
R-CAD-CONTRACT evidence fields on probe/readback + validation hard gates
R-CAD-VIEW-CAPTURE run_cad_validation.py pass, cad-validation-window.png captured
readback_report.json status geometry_verified, evidence_state readback_geometry_verified
cad_capability_probe.json status cad_capability_verified, evidence_state cad_capability_verified
primitive probe covers line/circle/arc/polyline/text/dimensions
```

这证明非 CAD 链路、benchmark、验证总控和维护门禁可用；Phase W baseline 真实 CAD 总验证已在用户会话下完成落图、截图、实体回读和 `geometry_verified` 闭环。本轮还加固了 CAD COM 调用底座：即使 `run_cad_validation.py` 顶层为 `pass`，也必须要求 `readback_report.json.status=geometry_verified`、`cad_capability_probe.json.status=cad_capability_verified` 且关键 checks 全部通过。最新能力探针已覆盖独立直线、圆、弧、闭合多段线、文字、标注和矩形边框。用户指出角色组合截图不在 CAD 后，本轮已将 3 个室内组合案例接入真实 AutoCAD 批量落图与 created handles 回读，最新证据为 `output\validation_runs\interior-composition-cad-label-clean-y8000\composition_cad_check_report.json`，3/3 cases `geometry_verified`。2026-05-26 又完成 `R-CAD-VIEW-CAPTURE` baseline：CAD 总控截图步骤改为 AutoCAD 客户区窗口级截图，并可按本轮 created handles bbox 缩放视图，证据为 `output\validation_runs\r-cad-view-cad\cad-validation-window.png`。该结论仍只覆盖当前简单矩形对象组合、baseline `examples\plans\draw_test_cabinet.json` 与当前能力探针，不扩大为真实项目图纸、块库、块插入或任意 CAD_PLAN 全部准确；截图也仍只是视觉辅助。

## 当前进度估算

估算口径：通用底座和多场景 Agent 各自按 100% 计算；总体默认按 `通用底座 70% + 多场景 Agent 30%` 加权。`多场景 Agent` 现在按 Scene Product 方向估算，而不是按 preferences、rules 或 non-CAD benchmark 数量估算。该估算只用于节奏判断，误差允许约 5-10 个百分点，不能替代测试和真实 CAD 证据。

| 维度 | 当前估算 | 判断依据 | 主要剩余缺口 |
| --- | ---: | --- | --- |
| 通用底座进度 | 约 73% | Core 已覆盖 schema、dry-run、verification、benchmark evidence gate、CAD validation gate、project sample、drawing read、proposal confirmed、repo audit、有限真实 CAD baseline、LCAD-01/02 manifest + strict matrix runner，以及本轮复杂混合图形 CAD smoke；但 ActiveDocument guard、真实 CAD 扩样、公司块库和真实项目闭环仍不足 | `LCAD-03+` 真实 CAD 扩样、真实项目 DWG、公司块库、正式图层安全、更多复杂几何 |
| 多场景 Agent 进度 | 约 25% | 已有 Scene Alpha 壳层和 office / residential / restaurant non-CAD beta benchmark；但这些只是场景偏好和能力包验证，不是具体场景产品 | 需要选择首个具体场景，如工装，补对象体系、图块 metadata、业务规则、真实项目样本、真实 CAD smoke 和用户确认流 |
| 总体进度 | 约 59% | `73% * 0.70 + 25% * 0.30` | 取决于 ActiveDocument guard、后续真实 CAD 校验扩样和首个 Scene Product Alpha 是否闭环 |

本轮新增并细化 Phase R 新鲜视角评审计划，并把代码切口继续落到 benchmark runner 与真实 CAD 批量执行：非 CAD benchmark 现在能显式输出 `evidence_state`、`geometry_accuracy`、`screenshot_role`，并支持 `minimums`、`contains_object_types`、`contains_component_roles`、`contains_object_roles` 断言、`object_spec` 与 `composition_spec` pipeline、suite/case 配置校验，以及 blank-shell / composition 每个 CAD_PLAN 的 dry-run / verification 汇总证据。`examples/benchmarks/office_alpha_benchmark.json` 当前覆盖 object / micro-scene / blank-shell / failure / invalid 共 18 个 non-CAD cases；`examples/benchmarks/interior_delivery_benchmark.json` 覆盖卧室床+地毯、餐桌组合、办公桌组合 3 个 persona composition cases，并输出浏览器截图辅助证据。新增 `scripts/run_composition_cad_check.py` 后，这 3 个组合案例已经在真实 AutoCAD `CODEX_PREVIEW` 中完成批量落图和回读。该进展提升 benchmark 证据门禁，但仍不代表真实块库和复杂家具符号已经完成。

## 能力矩阵

| 能力 | 状态 | 当前依据 | 主要缺口 |
| --- | --- | --- | --- |
| CAD execution | `alpha_verified_cad` | `core/execution/execute_plan.py` 已在真实 AutoCAD 中执行 baseline CAD_PLAN 到 `CODEX_PREVIEW`；`core/execution/batch_plan_runner.py` 已将 3 个室内组合 benchmark 的多 CAD_PLAN 批量写入真实 AutoCAD 并按 created handles 回读；最新组合证据为 `output\validation_runs\interior-composition-cad-label-clean-y8000\composition_cad_check_report.json` | 扩展到更多 CAD_PLAN、真实项目样本和块库插入验证 |
| CAD COM capability probe | `alpha_verified_cad` | `core/verification/cad_capability_probe.py` 已验证活动文档读取、`CODEX_PREVIEW` 图层、矩形边框、独立直线、圆、弧、闭合多段线、文字、标注、handles、定向回读、类型统计和 bbox；证据为 `output\validation_runs\manual-cad-after-primitive-probe\cad_capability_probe.json` | 扩展块插入、hatch、属性块、选择集和更复杂实体类型 |
| preview safety | `prototype` | `core/safety/policy.py` 默认只允许 `CODEX_PREVIEW`，正式图层/保存/覆盖/删除需要显式批准 | 补批准证据格式和审计字段 |
| validate / dry-run | `alpha_ready_non_cad` | `scripts/validate_plan.py`、`scripts/dry_run_plan.py` 和 core 入口稳定；baseline plan 通过 | 扩展批量 CAD_PLAN 和高层模型失败隔离 |
| self check / repo audit | `alpha_ready_non_cad` | `self_check.py`、`run_repo_audit.py --fail-on-findings` 已进入固定基线 | 继续把新维护风险纳入 audit |
| render preview | `alpha_verified_cad` | `render_preview.py --check` 输出结构化截图能力；`render_preview.py --capture-autocad-window --execution-summary ...` 已在真实 CAD 总控中生成 `output\validation_runs\r-cad-view-cad\cad-validation-window.png`，并按 created handles bbox 缩放视图 | 仍需扩展更细绘图区裁剪、多显示器和遮挡边界；截图不参与几何通过判断 |
| entity readback | `alpha_verified_cad` | `inspect_dwg.py --connect-cad` 已对真实 AutoCAD baseline 输出生成 `readback_report.json`；最新复验使用 created handles 定向回读，`status=geometry_verified` 且 `readback_scope`、`layer_entities`、`bbox_size`、`base_point`、`label_text`、`dimension_count`、`created_handles_scope` 全部 pass | 扩展 before/after snapshot、批量 plan 和真实图纸回读样本 |
| schemas | `alpha_ready_non_cad` | 高层 schema、examples、invalid fixtures、registry 和 validator 已建立 | 扩展真实项目正反例和跨模型引用边界 |
| capability runtime | `alpha_ready_non_cad` | `core/capabilities/` 已登记能力、风险、CAD 依赖、验证命令、maturity、known_limits；`workflow.blank_shell_pipeline` 可运行 | 增加审计记录字段和更多 workflow 类型 |
| artifact graph | `prototype` | workflow artifacts 可排序、检查路径和发现循环依赖 | 接更多工作流和产物差异检查 |
| geometry backends | `prototype` | `rect2d` 与 `orthogonal_polygon` 支持 bbox、正交多边形、no-place-zone、path strip 和基础距离检查 | Phase Y 评估复杂多边形/成熟几何库 |
| drawing analysis | `prototype` | manual drawing model、entity summary、manual shell loader 已可用 | 自动 DWG/PDF 空壳识别仍未开始闭环 |
| project model | `alpha_ready_non_cad` | `build_project_model()` 支持 `DESIGN_BRIEF + DRAWING_MODEL` 或 `DESIGN_BRIEF + SHELL_MODEL`，保留 shell_context | 增加冲突处理、真实样本和场景差异输入 |
| object engine | `prototype` | `object_defaults.json` 覆盖 cabinet/table/chair/desk/shelf/counter/bed/rug/sofa/display_unit/monitor，能生成 OBJECT_SPEC | 补尺寸来源说明和更多对象规格 |
| composition engine | `prototype` | `core/composition_engine/templates.py` 可将卧室床+地毯、餐桌+椅、办公桌+椅+显示器组合转成多 CAD_PLAN、dry-run、unverified verification 和 SVG/PNG 视觉辅助预览；当前 3 个模板已通过真实 CAD 批量落图与 created handles 回读 | 扩展更多组合模板、失败样本和 block insertion alpha |
| block engine | `alpha_verified_cad` | `BLOCK_LIBRARY v0.2`、受控 `controlled-test-block-001`；真实 CAD 受控块插入 + `block_reference` readback 已通过（`r-block-alpha-cad`） | 不扩大到公司块库、属性块或任意块名 |
| layout engine | `prototype` | 多 circulation/zone/placement 候选（`candidate_sets`）；blank-shell 8-case benchmark | 复杂几何、自动读图、真实项目大样本 |
| shell / circulation / function zones | `alpha_ready_non_cad` | Phase P/R/S/V 已完成 shell loader、动线候选、功能区切分并接入 pipeline | 扩展正交 shell、真实空间语义和更复杂样本 |
| proposal engine | `prototype` | `comparison_detail`（覆盖率/失败分布/通道连续性/排序原因，Y-MC-02）；多候选说明保留 | 用户确认流、真实多方案推理（BETA-PROPOSAL Backlog） |
| plan engine | `alpha_verified_cad` | `insert_block_alpha` intent：validate / dry-run / fake execute + 受控样本真实 CAD `geometry_verified` | 不声称任意 CAD_PLAN 或项目图纸块插入均已 verified |
| verification | `alpha_verified_cad` | fake readback、created handles 证据门、截图存在性、before/after diff 和修复建议已建立；`cad_validation_runner` 输出 `evidence_summary` 与顶层 evidence gate（R4-04）；交接 evidence 规则见 `evidence_gate_handoff_rules.md`（R4-05） | 继续扩大失败样本、真实项目样本和多对象 CAD_PLAN 验证 |
| benchmarks | `alpha_ready_non_cad` | minimal、blank-shell 8 cases、**office alpha 18 cases**（含 failure + `expected_evidence_summary`）、interior delivery benchmark 可重复运行；`R4-EVIDENCE-GATES` 已收口（词表、failure 断言、suite 汇总、CAD runner gate、`evidence_gate_handoff_rules.md`） | office / blank-shell 全量真实 CAD readback 仍待后续包 |
| blank-shell pipeline | `alpha_ready_non_cad` | `Y-MULTI-CANDIDATE` 已收口：8-case benchmark + 边界文档；非自动设计大脑 | 复杂几何、自动读图、真实项目样本库 |
| scene agents | `alpha_shell / beta_non_cad` | Scene Alpha 父包收口（`X-SCENE-ALPHA` 01–05）：三场景 blank_shell benchmark、边界扫描、解释模板；office / residential / restaurant 有 non-CAD beta benchmark | 尚未形成 Scene Product；工装等具体场景需要对象体系、图块 metadata、项目样本、真实 CAD smoke 和用户确认流 |

## 近期关键风险

- 不能把 Phase W baseline、基础图元探针或 3 个室内组合案例的 `geometry_verified` / `cad_capability_verified` 扩大解释为真实项目图纸、块库、块插入或任意 CAD_PLAN 全部准确。
- blank-shell pipeline 已可运行，但当前不等于完整自动设计大脑。
- 场景 Agent 已有 preferences、Alpha 验收和若干 beta benchmark，但仍未进入真正 Scene Product；不能把“底座验证时顺带做的多场景样本”说成具体工装 / 办公 / 住宅 Agent 已完成。
- 若继续扩张场景业务而不强化 Core，会重新把通用能力写死到单场景。
- 根目录文档曾经有重复状态描述；当前已把 Phase W/X/Y/Z 长篇执行剧本迁入 `docs/planning/`，并新增 Phase R 新鲜视角评审计划。后续应以 `CORE_CONTEXT_BRIEF.md` 为短入口、本文为能力矩阵、`CORE_RESTRUCTURE_PLAN.md` 为主计划索引。

## 计划入口

后续优先级、Phase 顺序和退出标准只以唯一 `PlanMD`：`CORE_RESTRUCTURE_PLAN.md` 为准。本文只维护能力矩阵、成熟度、证据路径和能力缺口，避免状态页再次变成第二份计划。
