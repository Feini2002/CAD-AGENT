# 通用 CAD Agent 开发包当前进展

最后更新：2026-05-26

本文是当前进展页，只保留“现在到哪、证据是什么、风险边界是什么”。历史流水见 `CAD_AGENT_CHANGELOG.md`，能力矩阵见 `CORE_STATUS.md`，唯一 `PlanMD` / 主计划见 `CORE_RESTRUCTURE_PLAN.md`。后续任务和优先级只写入 PlanMD，避免状态页变成第二份计划。

## 当前阶段

当前处于：

```text
Phase O-V 非 CAD 主线已完成
系统层安全补强与自检已完成
Phase W 已执行到 W-16；baseline 真实 CAD 回读闭环已验证通过
Phase R 角色驱动组合交付已从 non-CAD benchmark 推进到 3 个组合的真实 CAD batch readback
```

也就是说，仓库已经具备一条可运行的非 CAD 空壳布局 Alpha 原型链路；本轮已查明默认沙箱命令无法调用已打开 CAD 的根因，并在用户会话下完成 Phase W baseline 真实 CAD 落图、截图、实体回读和 `geometry_verified` 闭环。最新加固还补上了“顶层 pass 但 readback 未验证”的门禁漏洞，改为优先按本轮 created handles 定向回读真实 CAD 实体，并新增 CAD COM 能力矩阵探针验证底层调用能力。2026-05-25 22:08 又将能力矩阵从矩形/文字/标注扩展到独立直线、圆、弧和闭合多段线，并留下缩放后的截图证据。2026-05-25 之后，本轮角色组合交付已按用户指出的“必须在 CAD 里面”修正：卧室床+地毯、餐桌组合、办公桌组合已在 AutoCAD `CODEX_PREVIEW` 图层完成真实批量落图、created handles 定向回读和截图验证。

## 已确认事实

- 本仓库是通用 CAD Agent Core Lab，不绑定当前 DWG、当前家装图或当前电脑。
- 用户提到 `PlanMD`、`plan.md`、主计划或主 plan 时，当前默认指 `CORE_RESTRUCTURE_PLAN.md`；根目录没有独立 `plan.md`。
- `docs/architecture/shell-layout-foundation-design.md` 的核心路线已经被纳入主计划，并在 Phase P-V 中部分落地。
- `scripts/run_cad_validation.py` 已成为 CAD 层面检查总控入口。
- `CORE_RESTRUCTURE_PLAN.md` 已收缩为主计划总控索引；Phase W/X/Y/Z 的长篇执行剧本已迁入 `docs/planning/`。
- `CORE_CONTEXT_BRIEF.md` 是日常恢复上下文的短入口。
- Phase W W-05 已审查 `output\validation_runs\phase-w-preflight-no-cad\report.json`：无失败步骤需要分类。
- Phase W W-06 只读 AutoCAD COM 探针曾在默认沙箱身份下落证据到 `output\validation_runs\phase-w-w06-cad-probe\`，并暴露 `AutoCAD.Application` ProgID / 用户会话隔离问题；后续用户会话诊断已确认 COM 可用。
- Phase W W-07 真实 CAD 底座最新稳定报告为 `output\validation_runs\manual-cad-after-primitive-probe\report.json`，顶层 `status=pass`；`readback_report.json.status=geometry_verified`；`cad_capability_probe.json.status=cad_capability_verified`；关键 checks 全部 `pass`。
- 本轮已确认此前“CAD 已打开但无法调用”的主因是执行上下文隔离：默认沙箱身份 `desktop-r40v31q\codexsandboxoffline` 看不到用户桌面的 AutoCAD 进程、窗口和 ROT/COM 活动对象；用户会话身份 `desktop-r40v31q\user` 下 `AutoCAD.Application`、`.25.1`、`.25` 均可 `GetActiveObject`。
- 已完成七项加固：`AutoCADComDriver(connect_existing_only=True)` 连接失败时保留底层 COM detail 并尝试版本化 ProgID；`cad_validation_runner` 在 CAD 前置失败后跳过依赖步骤并清理旧派生 artifact；`AutoCADComDriver` 现在把点坐标转换为 AutoCAD COM 需要的 `VT_ARRAY | VT_R8` float VARIANT；`cad_validation_runner` 对 `inspect_readback` 增加 `geometry_verified` 和 checks 全 pass 硬门禁；`inspect_dwg.py` / `AutoCADComDriver` 支持按 created handles 定向回读，避免真实大图全量 ModelSpace 扫描；`cad_capability_probe` 已纳入总控，验证活动文档、preview 图层、矩形/文字/标注写入、handle 回读、类型统计、bbox 和安全边界；能力探针现已覆盖 `draw_line`、`draw_circle`、`draw_arc`、`draw_polyline` 并能回读识别 `line` / `circle` / `arc` / `polyline`。
- 主平台 Markdown 精细化拆分已执行；后续恢复开发时先读 `CORE_CONTEXT_BRIEF.md`，再按目标阶段读取 `docs/planning/phase-*.md`。
- 二次文档架构雕琢已执行：`docs/README.md` 成为文档区总地图，`docs/ROADMAP.md` 降级为兼容跳转，`docs/onboarding/README.md` 已补换机清单入口。
- 本轮继续收束文档权威关系：`CORE_RESTRUCTURE_PLAN.md` 是唯一 PlanMD / 开发主线；`docs/planning/phase-*.md` 是辅助执行剧本；状态、路线、架构、治理、验证和历史文档只服务主线，不生成第二套待办。
- 最后一轮防偏离收尾已明确：PlanMD 只做文档治理和开发排序，不改变通用 Core Lab、Core 优先、`CAD_PLAN` 中间层、真实 CAD 验证门槛和场景轻量化方向。
- Phase R 新鲜视角评审已启动并落文档：`docs/reviews/fresh-eyes-review-2026-05-25.md` 记录多名只读专家 agent 建议，`docs/planning/phase-r-fresh-perspective-rebirth-plan.md` 作为后续重生式开发校准入口。
- Phase R 已进一步细化为执行开发包：`docs/planning/phase-r-rebirth-implementation-plan.md`、`phase-r-cad-capability-contract.md`、`phase-r-block-library-roadmap.md`、`phase-r-office-benchmark-cases.md`、`docs/governance/multi-agent-contribution.md`、`docs/onboarding/first-handoff.md`。
- Phase R 第一批代码切口已落地：benchmark runner 支持 `evidence_state`、`geometry_accuracy`、`screenshot_role`、`minimums`、`contains_object_types`、`contains_component_roles`、suite/case 配置校验和 `object_spec` pipeline；blank-shell pipeline 已输出每个 CAD_PLAN 的 dry-run / verification 汇总证据；新增 `examples/benchmarks/office_alpha_benchmark.json`，用于验证 desk / chair / cabinet 对象规格、office blank-shell 对象类型和 non-CAD 证据状态。
- Phase R 第二批代码切口已落地：新增 `core/composition_engine/`，支持将卧室床+地毯、餐桌+椅、办公桌+椅+显示器这类角色需求转成组合规格、多 CAD_PLAN、dry-run、unverified verification 和 SVG/PNG 视觉辅助预览；benchmark runner 新增 `composition_spec` pipeline、`contains_object_roles` 断言和 `examples/benchmarks/interior_delivery_benchmark.json`，当前 3 个 persona composition cases 在 non-CAD 下通过。
- Phase R 第三批真实 CAD 校验已落地：新增 `core/execution/batch_plan_runner.py` 与 `scripts/run_composition_cad_check.py`，可将 benchmark 产出的多 CAD_PLAN 按 case 偏移批量写入 AutoCAD，并对本轮 created handles 做逐 plan `geometry_verified` 回读；脚本支持 `--start-x` / `--start-y` / `--spacing-x`，避免为了取干净截图而删除旧预览实体。
- `R-CAD-VIEW-CAPTURE` baseline 已落地：`render_preview.py` 支持 AutoCAD 窗口级截图与 created handles bbox 聚焦；`run_cad_validation.py` 已改为输出 `cad-validation-window.png`，截图继续只作为 `visual_aid_only`，几何准确仍由 created handles 回读决定。

## 当前可用链路

非 CAD blank-shell pipeline 当前可串联：

```text
SHELL_MODEL
-> PROJECT_MODEL
-> CIRCULATION_MODEL
-> FUNCTION_ZONE
-> placements
-> LAYOUT_PROPOSAL
-> DESIGN_PROPOSAL
-> CAD_PLAN
-> dry-run
-> VERIFICATION_REPORT(unverified)
```

当前已覆盖 retail、office、residential、restaurant 四个 benchmark workflow case。

## 最近验证记录

最近复验时间：2026-05-26。

```text
unittest discover -s tests: 227 tests OK
run_repo_audit.py --max-python-lines 500 --fail-on-findings: 0 findings
run_benchmark_suite.py examples\benchmarks\interior_delivery_benchmark.json: pass, 3/3 cases
run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json: pass, 4/4 cases
run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json: pass, 4/4 cases
self_check.py: pass（最近稳定基线）
render_preview.py --check: ready（最近稳定基线）
run_cad_validation.py --no-cad: output\validation_runs\manual-no-cad-after-composition-cad status pass
run_cad_capability_probe.py: output\validation_runs\manual-primitive-cad-probe status cad_capability_verified
run_cad_validation.py: output\validation_runs\manual-cad-after-primitive-probe status pass
focused R-CAD-VIEW tests: tests.core.test_render_preview + tests.core.test_cad_validation_runner, 11 tests OK
run_cad_validation.py --no-cad: output\validation_runs\r-cad-view-no-cad status pass
run_cad_validation.py: output\validation_runs\r-cad-view-cad status pass
run_composition_cad_check.py: output\validation_runs\interior-composition-cad-label-clean-y8000 status geometry_verified, 3/3 cases, 55 created handles
最新真实 CAD 报告: output\validation_runs\manual-cad-after-primitive-probe\report.json
最新窗口级截图 CAD 报告: output\validation_runs\r-cad-view-cad\report.json
最新角色组合真实 CAD 报告: output\validation_runs\interior-composition-cad-label-clean-y8000\composition_cad_check_report.json
readback_report.json: status geometry_verified
cad_capability_probe.json: status cad_capability_verified
baseline created_handles: 3C50, 3C51, 3C52, 3C53, 3C54, 3C55, 3C91
capability probe handles: 3CCD, 3CCE, 3CCF, 3CD0, 3CD1, 3CD2, 3CD3, 3CD4, 3CD5, 3CD6, 3D11
关键 checks: readback_scope / layer_entities / bbox_size / base_point / label_text / dimension_count / created_handles_scope 全部 pass
能力探针 checks: active_document_read / layer_policy / layer_ensure / rectangle_handles / line_handle / circle_handle / arc_handle / polyline_handle / text_handle / dimension_handles / handle_readback_count / readback_layer_scope / readback_type_counts / readback_bbox / safety_preview_only 全部 pass
截图证据: output\validation_runs\manual-primitive-cad-probe\cad-primitive-screen.png, 538584 bytes
窗口级截图证据: output\validation_runs\r-cad-view-cad\cad-validation-window.png, mode autocad_window, focus zoomed_to_bbox, 7 created handles
角色组合视觉辅助截图: output\test_artifacts\benchmarks\interior_delivery_manual\interior_designer_bedroom_bed_rug\preview-browser.png; output\test_artifacts\benchmarks\interior_delivery_manual\home_designer_dining_table_set\preview-browser.png; output\test_artifacts\benchmarks\interior_delivery_manual\office_planner_desk_combo\preview-browser.png
角色组合真实 CAD 截图: output\validation_runs\interior-composition-cad-label-clean-y8000\composition-cad-screen-clean-y8000.png
```

W-07 真实 CAD 总验证入口已经完成 baseline 落图、截图和实体回读闭环，并额外完成 CAD COM 能力矩阵探针。因此可以声明 Phase W baseline 真实 CAD 几何通过、当前用户会话下 CAD COM preview 写入与 handle 回读底座可用；扩展后的底层图元探针也已验证 1 个矩形边框、1 条独立直线、1 个圆、1 段弧、1 条闭合多段线、1 段文字和 2 个标注。该结论仍只覆盖 `examples\plans\draw_test_cabinet.json` 和当前能力探针，不能扩大为真实项目图纸、块库、块插入或任意 CAD_PLAN 全部已验证。后续判断必须继续以 `readback_report.json.status=geometry_verified`、`cad_capability_probe.json.status=cad_capability_verified` 和关键 checks 全部 `pass` 为准，不得只看 runner 顶层 `status=pass`。

## 当前进度估算

按 `CAD_AGENT_RULES.md` 的粗估口径，当前基准为：

```text
总进度：约 59%（Core 底座开发 70% + Agent 多场景实现 30%）
Core 底座开发进度：约 70%
Agent 多场景实现进度：约 34%
```

解释：Core 已经从脚手架推进到可复验 Alpha 底座，本轮又补上 Phase R benchmark 证据状态、对象规格 pipeline、角色驱动组合 pipeline、对象/组件/角色断言、视觉辅助预览，以及 3 个组合案例的真实 AutoCAD 批量落图与 created handles 回读；但复杂几何、真实样本、块库、块插入、自动图纸理解还没闭合。场景 Agent 目前主要是 preferences、manifest、目录、边界测试、office alpha non-CAD object/scene cases、3 个 interior delivery persona composition cases 和对应真实 CAD 组合回读，尚未完成 Phase X 的正式 Alpha 验收。

## 当前最重要缺口

| 缺口 | 影响 | 归属主线 |
| --- | --- | --- |
| 真实项目图纸 / 块库 / 任意 CAD_PLAN 尚未补验 | baseline 已通过，但不能扩大为全量 CAD 几何准确 | Phase Y / 后续真实项目验收 |
| 角色组合真实 CAD 覆盖仍较窄 | 当前只验证了 3 个简单矩形对象组合和文字/尺寸策略，还不是块插入、复杂家具符号或任意组合 | Phase R / Phase W |
| 场景 Agent preferences 尚未正式 Alpha 验收 | 不能证明多场景复用成熟 | Phase X |
| blank-shell pipeline 仍偏单条主候选 | 不能称为完整多方案设计脑 | Phase Y |
| 真实项目样本和失败基准不足 | benchmark 代表性有限 | Phase Y |
| 文档历史状态曾经分散重复 | 后续 Codex 容易读错阶段 | Phase Z |
| office alpha benchmark 仍缺 micro-scene / failure 样本 | 已覆盖 desk / chair / cabinet object spec 与第一条 scene case，但还没有覆盖入口、通道、冲突和失败样本 | Phase R / Phase Y |
| CAD 窗口级截图仍需扩展到更多边界 | baseline 已能截 AutoCAD 客户区并按本轮 created handles 缩放视图；后续仍需覆盖更细绘图区裁剪、多显示器和遮挡边界；几何准确仍以 created handles 回读为准 | Phase W / Phase R |

## 计划入口

后续优先级、Phase 顺序、待办和退出标准只以唯一 `PlanMD`：`CORE_RESTRUCTURE_PLAN.md` 为准。本文只维护当前进展、最近验证、风险边界和状态快照。

2026-05-26 已把下一轮开发建议拆成九个可执行开发包：`R-CAD-CONTRACT`、`R-BLOCK-METADATA`、`R-BLOCK-PLAN`、`R-BLOCK-CAD-ALPHA`、`R-CAD-VIEW-CAPTURE`、`R-OFFICE-MICRO`、`R4-EVIDENCE-GATES`、`Y-MULTI-CANDIDATE`、`X-SCENE-ALPHA`。其中 `R-CAD-VIEW-CAPTURE` 已完成 baseline 实现与真实 CAD 验证，证据为 `output\validation_runs\r-cad-view-cad\cad-validation-window.png`；截图能力提升不改变几何门槛，真实 CAD 几何仍只看 created handles 回读和 `geometry_verified`。

## 后续恢复开发时怎么问

```text
读取本仓库 AGENTS.md 和 CORE_CONTEXT_BRIEF.md，告诉我 CAD Agent 当前开发状态和下一步建议。
```

若要执行主计划：

```text
读取 CORE_RESTRUCTURE_PLAN.md，再按目标阶段打开 docs/planning/phase-*.md 执行。
```
