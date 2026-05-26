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

## 当前总状态

当前 Core 已完成 Phase O-V 的非 CAD 主线和一次系统层安全补强。最新记录为：

```text
239 tests OK
self_check.py pass
render_preview.py --check ready
repo audit 0 findings
blank-shell pipeline ok
blank-shell 4 场景 benchmark pass
office alpha benchmark 4 cases pass
interior delivery benchmark 3 persona composition cases pass
interior delivery real CAD composition check 3/3 geometry_verified
run_cad_validation.py --no-cad pass
Phase W W-07 CAD foundation run_cad_validation.py pass
R-BLOCK-PLAN insert_block_alpha validate/dry-run/fake execute
R-BLOCK-METADATA BLOCK_LIBRARY v0.2 + controlled-test-block-001 metadata
R-CAD-CONTRACT evidence fields on probe/readback + validation hard gates
R-CAD-VIEW-CAPTURE run_cad_validation.py pass, cad-validation-window.png captured
readback_report.json status geometry_verified, evidence_state readback_geometry_verified
cad_capability_probe.json status cad_capability_verified, evidence_state cad_capability_verified
primitive probe covers line/circle/arc/polyline/text/dimensions
```

这证明非 CAD 链路、benchmark、验证总控和维护门禁可用；Phase W baseline 真实 CAD 总验证已在用户会话下完成落图、截图、实体回读和 `geometry_verified` 闭环。本轮还加固了 CAD COM 调用底座：即使 `run_cad_validation.py` 顶层为 `pass`，也必须要求 `readback_report.json.status=geometry_verified`、`cad_capability_probe.json.status=cad_capability_verified` 且关键 checks 全部通过。最新能力探针已覆盖独立直线、圆、弧、闭合多段线、文字、标注和矩形边框。用户指出角色组合截图不在 CAD 后，本轮已将 3 个室内组合案例接入真实 AutoCAD 批量落图与 created handles 回读，最新证据为 `output\validation_runs\interior-composition-cad-label-clean-y8000\composition_cad_check_report.json`，3/3 cases `geometry_verified`。2026-05-26 又完成 `R-CAD-VIEW-CAPTURE` baseline：CAD 总控截图步骤改为 AutoCAD 客户区窗口级截图，并可按本轮 created handles bbox 缩放视图，证据为 `output\validation_runs\r-cad-view-cad\cad-validation-window.png`。该结论仍只覆盖当前简单矩形对象组合、baseline `examples\plans\draw_test_cabinet.json` 与当前能力探针，不扩大为真实项目图纸、块库、块插入或任意 CAD_PLAN 全部准确；截图也仍只是视觉辅助。

## 当前进度估算

估算口径：通用底座和多场景 Agent 各自按 100% 计算；总体默认按 `通用底座 70% + 多场景 Agent 30%` 加权。该估算只用于节奏判断，误差允许约 5-10 个百分点，不能替代测试和真实 CAD 证据。

| 维度 | 当前估算 | 判断依据 | 主要剩余缺口 |
| --- | ---: | --- | --- |
| 通用底座进度 | 约 73% | Core 结构、schema、非 CAD pipeline、benchmark、自检、repo audit、真实 CAD baseline 回读、基础图元能力探针已形成闭环；Phase R runner 已补证据状态、对象规格 pipeline、角色驱动组合 pipeline、对象/组件/角色断言、视觉辅助预览和 3 个组合案例真实 CAD batch readback | 自动 DWG/PDF 识别、复杂几何、多候选硬化、真实项目样本、真实块插入/块库/hatch/属性块、更大规模批量 CAD readback 验证 |
| 多场景 Agent 进度 | 约 34% | 多个 `agents/<scenario>` 目录、manifest、preferences 和边界测试已有；4 场景 blank-shell benchmark 已能跑通，office alpha 已有 4 个 non-CAD object/scene cases，interior delivery benchmark 已覆盖卧室/餐桌/办公桌 3 个 persona composition cases，并完成对应真实 CAD 组合回读 | Phase X 正式 Alpha 验收未做，场景差异影响仍浅，真实场景样本、场景工作流、micro-scene、failure 语义和复杂 CAD 组合回读不足 |
| 总体进度 | 约 62% | `73% * 0.70 + 34% * 0.30` | 取决于 Core 继续硬化和场景 Agent 从 preferences / composition 原型推进到可验收 Alpha |

本轮新增并细化 Phase R 新鲜视角评审计划，并把代码切口继续落到 benchmark runner 与真实 CAD 批量执行：非 CAD benchmark 现在能显式输出 `evidence_state`、`geometry_accuracy`、`screenshot_role`，并支持 `minimums`、`contains_object_types`、`contains_component_roles`、`contains_object_roles` 断言、`object_spec` 与 `composition_spec` pipeline、suite/case 配置校验，以及 blank-shell / composition 每个 CAD_PLAN 的 dry-run / verification 汇总证据。`examples/benchmarks/office_alpha_benchmark.json` 当前覆盖 desk / chair / cabinet 对象规格与 office blank-shell scene，共 4 个 non-CAD cases；`examples/benchmarks/interior_delivery_benchmark.json` 覆盖卧室床+地毯、餐桌组合、办公桌组合 3 个 persona composition cases，并输出浏览器截图辅助证据。新增 `scripts/run_composition_cad_check.py` 后，这 3 个组合案例已经在真实 AutoCAD `CODEX_PREVIEW` 中完成批量落图和回读。该进展提升 benchmark 证据门禁，但仍不代表真实块库和复杂家具符号已经完成。

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
| block engine | `prototype` | `BLOCK_LIBRARY v0.2` schema、`object_spec_to_block_reference()`、受控 `controlled-test-block-001` 与 `symbol_fallback` 元数据；`0.1` 库仍可加载 | 真实块插入、block readback 与 `insert_block_alpha` 仍 deferred |
| layout engine | `prototype` | 多对象候选、碰撞、clearance、主通道、动线、功能区、zone placement 已建立 | Phase Y 强化多候选布局、失败基准和复杂空间 |
| shell / circulation / function zones | `alpha_ready_non_cad` | Phase P/R/S/V 已完成 shell loader、动线候选、功能区切分并接入 pipeline | 扩展正交 shell、真实空间语义和更复杂样本 |
| proposal engine | `prototype` | DESIGN_PROPOSAL 支持多候选、确认候选、比较摘要和来源化 evidence | 强化真实多方案设计推理和用户确认流 |
| plan engine | `prototype` | 高层对象/布局/方案可转安全 CAD_PLAN envelope；`insert_block_alpha` intent 已支持 validate / dry-run / fake execute | 真实 CAD block 插入与 readback 仍 deferred（`R-BLOCK-CAD-ALPHA`） |
| verification | `alpha_verified_cad` | fake readback、created handles 证据门、截图存在性、before/after diff 和修复建议已建立；Phase W baseline 真实 CAD readback 已通过 `geometry_verified` 门禁；`cad_validation_runner` 已禁止把非 `geometry_verified` 回读或非 `cad_capability_verified` 能力探针误判为 CAD pass | 继续扩大失败样本、真实项目样本和多对象 CAD_PLAN 验证 |
| benchmarks | `alpha_ready_non_cad` | minimal benchmark、blank-shell 4 场景 benchmark、office alpha benchmark 和 interior delivery benchmark 可重复运行；runner 支持 non-CAD 证据状态、最小指标、对象类型、组件角色、对象角色断言、suite/case 配置校验和 `object_spec` / `composition_spec` benchmark pipeline；blank-shell 与 composition 已输出每个 CAD_PLAN 的 dry-run / verification 汇总证据；interior delivery 另有真实 CAD batch check 证据 | Phase R/Y 增加更多 micro-scene、failure case、历史趋势、真实项目样本和更复杂组合真实 CAD readback |
| blank-shell pipeline | `alpha_ready_non_cad` | `run_blank_shell_pipeline.py` 串联 shell/project/circulation/zones/placements/layout/proposal/CAD_PLAN/dry-run/unverified report | Phase Y 强化多候选输出和失败解释 |
| scene agents | `prototype` | commercial/residential/office/restaurant preferences 已有，边界测试保护场景层不复制 Core | Phase X 做正式 Alpha 验收 |

## 近期关键风险

- 不能把 Phase W baseline、基础图元探针或 3 个室内组合案例的 `geometry_verified` / `cad_capability_verified` 扩大解释为真实项目图纸、块库、块插入或任意 CAD_PLAN 全部准确。
- blank-shell pipeline 已可运行，但当前不等于完整自动设计大脑。
- 场景 Agent 已有 preferences，但仍是轻量数据层原型。
- 若继续扩张场景业务而不强化 Core，会重新把通用能力写死到单场景。
- 根目录文档曾经有重复状态描述；当前已把 Phase W/X/Y/Z 长篇执行剧本迁入 `docs/planning/`，并新增 Phase R 新鲜视角评审计划。后续应以 `CORE_CONTEXT_BRIEF.md` 为短入口、本文为能力矩阵、`CORE_RESTRUCTURE_PLAN.md` 为主计划索引。

## 计划入口

后续优先级、Phase 顺序和退出标准只以唯一 `PlanMD`：`CORE_RESTRUCTURE_PLAN.md` 为准。本文只维护能力矩阵、成熟度、证据路径和能力缺口，避免状态页再次变成第二份计划。
