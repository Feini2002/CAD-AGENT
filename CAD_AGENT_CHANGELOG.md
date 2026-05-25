# CAD Agent 变更记录

这个文件记录 CAD Agent 测试工作区的结构、规则、Schema、脚本和重要决策变化。

## 2026-05-26

### PlanMD 主线权威收束

- 按用户要求继续雕琢整体文档架构，明确 `CORE_RESTRUCTURE_PLAN.md` 是唯一 `PlanMD` / 开发主线；根目录没有独立 `plan.md`，用户说 `PlanMD`、`plan.md` 或主 plan 时都指向该文件。
- 在 `CORE_RESTRUCTURE_PLAN.md` 新增 “PlanMD 主线协议”，把文档层级收束为：PlanMD 决定当前队列、Phase 顺序、优先级、Decision Gate 和退出标准；`docs/planning/phase-*.md` 只做辅助执行剧本；状态、路线、架构、治理、交接、验证、历史和 review 文档只服务主线。
- 更新 `AGENTS.md`、`CORE_CONTEXT_BRIEF.md`、`CAD_AGENT_RULES.md`、`README.md`、`docs/README.md`、`docs/planning/README.md`、`docs/onboarding/first-handoff.md` 与 `docs/governance/multi-agent-contribution.md`，让后续 Codex 恢复上下文时不会把多个 Markdown 误读成多条并列计划。
- 给 Phase R/W/X/Y/Z 相关 `docs/planning/*.md` 顶部补充“辅助执行剧本，不是独立 PlanMD”的提示，并把同步日期调整到 2026-05-26。
- 最后一轮按用户担心补强“防偏离边界”：PlanMD 只是文档治理和开发排序，不改变通用 CAD Agent Core Lab、Core 优先、`CAD_PLAN` 中间层、真实 CAD created-handle 回读门槛、场景 Agent 轻量化和保护用户 DWG 的根方向。
- 修正 `CAD_AGENT_RULES.md` 中进度估算的旧基准，使其与 `CORE_STATUS.md` / `CAD_AGENT_STATUS.md` 当前口径一致：通用底座约 70%，多场景 Agent 约 34%，总体约 59%。
- 本轮仍只改 Markdown，不改代码、不运行 CAD、不扩大任何真实 CAD 几何验证结论。

### 二次文档架构雕琢

- 按用户要求以“今天开发收尾”为边界，只做 Markdown 和文档入口重构，不修改 `core/`、`scripts/`、`drivers/`、`tests/`、`agents/`、`libraries/`、`projects/`、`examples/` 或 `schemas/`。
- 派出 AI 产品经理与深度架构程序员两个只读 agent 审阅仓库信息架构，结论收束为：代码边界基本成立，当前主要问题是入口权威性、计划散落、历史材料仍在根目录。
- 将低频文档迁出根目录：`SHELL_LAYOUT_FOUNDATION_DESIGN.md` 迁到 `docs/architecture/shell-layout-foundation-design.md`，`SHELL_LAYOUT_TIME_ESTIMATE.md` 迁到 `docs/history/shell-layout-time-estimate.md`，`CAD_AGENT_DECISIONS.md` 迁到 `docs/decisions/cad-agent-decisions.md`。
- 将已执行的 `docs/planning/core-platform-md-split-plan.md` 迁为 `docs/history/core-platform-md-split-plan-2026-05-25.md`，并新增 `docs/history/README.md`。
- 将 README 中的长篇换机清单拆到 `docs/onboarding/migration-checklist.md`，README 只保留入口链接；同步修正 README 中 `219 tests` 到 `223 tests`，并修正“没有真实回读”这类过期口径为“真实回读覆盖仍有限”。
- 将 `CORE_RESTRUCTURE_PLAN.md` 标题和职责收束为唯一主计划，新增“当前活跃工作队列”；`CORE_STATUS.md` 与 `CAD_AGENT_STATUS.md` 不再承载独立下一步清单，只保留能力、证据、缺口和风险边界。
- 更新 `CORE_CONTEXT_BRIEF.md`、`CAD_AGENT_RULES.md`、`docs/planning/README.md`、`docs/architecture/README.md`、`docs/onboarding/first-handoff.md` 和 Phase 文档中的旧路径、旧计划口径与主从关系。
- 新增 `docs/README.md` 作为文档区总地图，更新 `docs/onboarding/README.md` 补换机清单入口，并将 `docs/ROADMAP.md` 降级为兼容跳转，避免旧阶段路线干扰当前 `CORE_ROADMAP.md` 与主计划。

## 2026-05-25

### Phase R 角色组合真实 CAD 落图与回读

- 根据用户指出“这些东西不是在 CAD 里面”，将此前仅有 SVG/浏览器 PNG 的角色组合自检推进到真实 AutoCAD：新增 `core/execution/batch_plan_runner.py`，支持对多份 CAD_PLAN 做坐标偏移、逐 plan 执行、created handles 汇总和 `geometry_verified` 回读报告。
- 新增 `scripts/run_composition_cad_check.py`，把 `examples/benchmarks/interior_delivery_benchmark.json` 产出的卧室床+地毯、餐桌组合、办公桌组合三组 CAD_PLAN 批量写入当前 AutoCAD 的 `CODEX_PREVIEW` 图层，并输出 `composition_cad_check_report.json`。
- 为避免覆盖或删除旧预览对象，真实 CAD 组合校验脚本支持 `--start-x`、`--start-y`、`--spacing-x` 参数；本轮最终使用 `--start-x 26000 --start-y 8000 --spacing-x 4200` 绘制到上方空白区域，未删除旧实体、未保存 DWG、未修改正式图层。
- 修复组合落图的 CAD 标注可读性问题：地毯作为底衬不再生成文字实体，大尺寸对象文字高度封顶，餐椅标签缩短为 `Chair`，避免真实 CAD 组合视图被文字遮挡。
- 新增和扩展测试：`tests/core/test_batch_plan_runner.py` 覆盖批量计划偏移与 fake readback，`tests/core/test_run_composition_cad_check.py` 覆盖 fresh CAD region 偏移参数，`tests/core/test_composition_engine.py` 与 `tests/core/test_execute_plan.py` 锁定组合标注策略和文字高度上限。
- 真实 CAD 复验通过：`output\validation_runs\interior-composition-cad-label-clean-y8000\composition_cad_check_report.json` 顶层 `status=geometry_verified`，3/3 cases verified，created handles 共 55 个；截图证据为 `output\validation_runs\interior-composition-cad-label-clean-y8000\composition-cad-screen-clean-y8000.png`。
- 最终回归通过：`unittest discover -s tests` 为 223 tests OK，`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings，`run_benchmark_suite.py examples\benchmarks\interior_delivery_benchmark.json` 为 3/3 pass，`run_cad_validation.py --no-cad --output-dir output\validation_runs\manual-no-cad-after-composition-cad` 为 `status=pass`。
- 证据边界更新：现在可以说这 3 个简单矩形对象组合已经真实落到 AutoCAD 并完成 created handles 回读；仍不能说已经完成真实家具块库、块插入、复杂符号、任意组合或真实项目图纸自动设计。
- 粗估进度小幅上调为：通用底座约 70%，多场景 Agent 约 34%，总体约 59%。该上调来自真实 CAD 组合回读闭环，不等同于达到 80% 或完成块库能力。

### Phase R 角色驱动组合交付自检

- 按用户提出的“模拟室内设计行业用户拿系统交付图块组合”的新维度，新增通用 `core/composition_engine/`，不把卧室、餐桌或办公桌组合写死进某个场景 Agent。
- 新增 `composition_spec` 生成能力：当前可把 `bedroom_bed_rug`、`dining_table_set`、`office_desk_combo` 转成组合规格、多份安全 `CAD_PLAN`、dry-run 报告、unverified verification 报告和 SVG 视觉辅助预览。
- 扩展 `libraries/objects/object_defaults.json`，新增 `rug` 与 `monitor` 对象默认规格，支持床+地毯、餐桌+椅、办公桌+椅+显示器三类组合。
- 扩展 `core/benchmarks/runner.py`：新增 `composition_spec` pipeline、`contains_object_roles` 断言、组合级 metrics、每个组合 CAD_PLAN 的 dry-run / verification 汇总和 `preview_svg` artifact。
- 新增 `examples/benchmarks/interior_delivery_benchmark.json`，模拟 `interior_designer`、`home_designer`、`office_planner` 三个角色，分别验收卧室床+地毯、餐桌组合和办公桌组合。
- 新增 `tests/core/test_composition_engine.py`，并扩展 `tests/core/test_benchmarks.py`，按 TDD 覆盖组合生成、plan-ready、视觉辅助 artifact 与 persona benchmark。
- 浏览器视觉检查发现首版 SVG 标题区与图形区过近，已修正 `write_composition_preview_svg()` 的标题留白并重新生成截图。
- 新鲜复验：`unittest discover -s tests` 为 219 tests OK；`run_benchmark_suite.py examples\benchmarks\interior_delivery_benchmark.json` 为 3/3 pass；三张浏览器截图保存到 `output\test_artifacts\benchmarks\interior_delivery_manual\*\preview-browser.png`。
- 证据边界保持不变：本轮组合交付是 non-CAD benchmark 和视觉辅助预览，显式保留 `geometry_accuracy=not_verified_without_cad_readback` 与 `screenshot_role=visual_aid_only`，不能声称真实 CAD created-handle 几何已验证。
- 粗估进度小幅上调为：通用底座约 67%，多场景 Agent 约 31%，总体约 56%。该上调来自角色组合自检和 benchmark 证据增强，不来自真实 CAD 几何扩展。

### Phase R office benchmark 与证据状态 runner

- 按“继续通用底座深度开发”推进 Phase R 的 benchmark 代码切口，不运行真实 CAD，不修改 DWG。
- 扩展 `core/benchmarks/runner.py`：benchmark actual 现在包含 `evidence_state`、`geometry_accuracy`、`screenshot_role`、`object_types`、`component_roles` 和对象尺寸；expected 支持 `minimums`、`contains_object_types` 与 `contains_component_roles` 断言；新增 `object_spec` benchmark pipeline。
- 扩展 `core/workflows/blank_shell_pipeline.py`：metrics 增加 `object_types`，让 benchmark 能验证场景对象覆盖。
- 加固 benchmark 门禁：suite 中空 cases、非 object case、缺 `expected` 或空断言不再静默 pass；blank-shell 现在为每个生成的 CAD_PLAN 输出 `dry_run_reports.json` 与 `verification_reports.json`，runner 使用汇总状态而不是只看第一个 plan。
- 新增 `examples/benchmarks/office_alpha_benchmark.json`，当前包含 desk / chair / cabinet object spec 与 `office_small_suite_alpha` scene 共 4 个 cases，验证对象尺寸、组件角色、场景对象类型、最小指标和 `benchmark_pass_non_cad` 证据状态。
- 扩展 `tests/core/test_benchmarks.py`，按 TDD 增加 Phase R 证据状态与 office alpha benchmark 回归测试。
- 新鲜复验：`unittest discover -s tests` 为 214 tests OK；`run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json` 为 4/4 pass；`run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json` 为 4/4 pass；`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings。
- 证据边界保持不变：office alpha benchmark 是非 CAD 证据，显式写 `geometry_accuracy=not_verified_without_cad_readback` 和 `screenshot_role=visual_aid_only`，不能声称真实 CAD 几何准确。
- 粗估进度小幅上调为：通用底座约 64%，多场景 Agent 约 29%，总体约 54%。该上调来自 benchmark/office alpha 证据增强，不来自真实 CAD 几何扩展。

### Phase R 执行开发包细化

- 按用户要求继续执行修改后的 Phase R plan，创建多个只读专项 agent 细化 CAD 能力契约、办公 benchmark、图块库路线和多 agent 协作治理。
- 新增 `docs/planning/phase-r-rebirth-implementation-plan.md`，将 Phase R 拆成 R0-R5、R-GOV / R-CAD / R-BLOCK / R-OFFICE 任务和证据状态门禁。
- 新增 `docs/planning/phase-r-cad-capability-contract.md`，定义 line / rectangle / circle / arc / polyline / text / dimension / block_reference 的 write-read-verify 契约和 `insert_block_alpha` 草案。
- 新增 `docs/planning/phase-r-block-library-roadmap.md`，定义 `BLOCK_LIBRARY v0.2`、OBJECT_SPEC、drawing standard profile、受控测试块和 block insertion 迁移路线。
- 新增 `docs/planning/phase-r-office-benchmark-cases.md`，将办公桌、办公椅、电脑桌、柜体、入口、主通道和失败样本整理为 object / micro-scene / scene / failure benchmark cases。
- 新增 `docs/governance/multi-agent-contribution.md` 与 `docs/onboarding/first-handoff.md`，固化多 agent 协作边界、新人接手入口和不可声称边界。
- 更新 `CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CORE_ROADMAP.md`、`README.md` 和 `docs/planning/README.md`，让后续开发优先读取 Phase R 执行包。
- 本轮仍只改 Markdown；不修改代码、不运行 CAD、不把执行计划当成功能完成。

### Phase R 新鲜视角评审与重生式开发计划

- 按用户要求，创建多个只读专家 agent，从 CAD 自动化、图块库/制图标准、空间设计业务、平台架构、验证/benchmark 五个新鲜视角审视当前系统。
- 新增 `docs/reviews/fresh-eyes-review-2026-05-25.md`，记录多 agent 首次接手式评审结论。
- 新增 `docs/planning/phase-r-fresh-perspective-rebirth-plan.md`，将“重生式开发”收敛为 CAD 能力契约、办公基础闭环、图块库设计、benchmark 证据门禁和平台协作治理。
- 更新 `CORE_RESTRUCTURE_PLAN.md`：新增 Phase R、当前可信基线索引、Phase 状态语义、Interface Ownership Map、Decision Gates 和 Alpha 里程碑判定。
- 更新 `CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CORE_ROADMAP.md`、`README.md` 和 `docs/planning/README.md`，把 Phase R 纳入后续开发入口。
- 本轮仍只改 Markdown；不修改代码、不运行 CAD、不把新鲜视角评审当成 Core Alpha 完成。

### 主平台 Markdown 拆分执行

- 按 `docs/planning/core-platform-md-split-plan.md` 执行主平台 Markdown 拆分。
- 新增 `docs/planning/phase-w-cad-validation-plan.md`、`docs/planning/phase-x-scene-agent-alpha-plan.md`、`docs/planning/phase-y-blank-shell-hardening-plan.md`、`docs/planning/phase-z-doc-governance-plan.md`，分别承接 Phase W/X/Y/Z 的长篇执行剧本。
- 将 `CORE_RESTRUCTURE_PLAN.md` 收缩为主计划总控索引，保留当前复盘、能力边界、文档职责、阶段路线、Phase 执行入口、分歧点和完成判定。
- 更新 `CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`README.md` 和 `docs/planning/README.md`，让后续开发按目标 Phase 读取 `docs/planning/phase-*.md`。
- 根据只读复核 agent 反馈，修正 `README.md` 中旧的 196 项测试、21:42 复验时间、旧 CAD 证据路径和 entity readback 状态漂移，并修正 Phase Z 文档里 “本文收缩为总控索引” 的指代。
- 本次仍只改 Markdown 文档；真实 CAD 结论仍只覆盖已验证的 baseline plan 和 CAD capability probe，不扩大到真实项目图纸、块库、块插入或任意 CAD_PLAN。

### 主平台 Markdown 精细化拆分计划

- 用户要求本轮不改代码，先构建主平台 Markdown 拆分计划，为下一步执行降低上下文抖动。
- 新增 `docs/planning/` 作为规划类文档目录，并新增 `docs/planning/core-platform-md-split-plan.md`。
- 计划将 `CORE_RESTRUCTURE_PLAN.md` 收缩为总控索引，把 Phase W/X/Y/Z 的长篇执行剧本迁入 `docs/planning/phase-*.md`。
- 同步更新 `CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`CAD_AGENT_STATUS.md` 和 `README.md` 的入口说明。
- 本轮不修改 `core/`、`scripts/`、`drivers/`、`tests/`、`agents/` 或 CAD 图纸；真实 CAD 结论边界保持不变。

### 开发进度百分比口径固化

- 按用户要求新增长期规则：后续每次 CAD Agent 相关改动后，都要大概估算并汇报 `通用底座进度`、`多场景 Agent 进度` 和 `总体进度`。
- 固定默认权重：总体进度按 `通用底座 70% + 多场景 Agent 30%` 加权；百分比只作节奏判断，不替代真实验证证据。
- 写入 `CAD_AGENT_RULES.md` 的 `0.4 开发进度百分比估算口径`。
- 在 `CORE_STATUS.md` 和 `CAD_AGENT_STATUS.md` 写入当前基准估算：通用底座约 63%，多场景 Agent 约 28%，总体约 53%。
- 明确该估算允许 5-10 个百分点误差；只有形成可复验证据、状态同步和边界说明后才小幅上调，发现回归或验证缺口时可以下调。

### 基础图元 CAD 探针扩展与截图复验

- 用户要求用截图方式真实检验当前系统是否能调用 CAD 画出具体内容，并指出此前 CAD 测试覆盖过浅。
- 按 TDD 补充失败测试：`tests/core/test_autocad_com_driver.py` 覆盖 `draw_line`、`draw_circle`、`draw_arc`、`draw_polyline` 的 COM 调用参数；`tests/core/test_verification_report.py` 覆盖圆、弧、多段线回读标准化；`tests/core/test_cad_capability_probe.py` 要求能力探针从 7 个实体扩展到 11 个实体。
- 扩展 `core/cad_io/autocad_com.py`：新增独立直线、圆、弧、轻量多段线写入；弧角度从度转换为 AutoCAD COM 需要的弧度；多段线点集转换为 `VT_ARRAY | VT_R8` 2D 坐标数组。
- 扩展 `core/verification/inspect_dwg.py`：回读时识别 `circle`、`arc`、`polyline`，并为圆、弧、多段线补充中心、半径、角度、点集、闭合状态和 bbox 信息。
- 扩展 `core/verification/cad_capability_probe.py`：能力矩阵现在绘制并回读 1 个矩形边框、1 条独立直线、1 个圆、1 段弧、1 条闭合多段线、1 段文字和 2 个标注，预期类型统计为 `line=5`、`circle=1`、`arc=1`、`polyline=1`、`text=1`、`dimension=2`。
- 真实 CAD 单独探针通过：`output\validation_runs\manual-primitive-cad-probe\cad_capability_probe.json` 为 `status=cad_capability_verified`，entity_count 为 11，bbox 为 `900.0 x 450.0`，全部实体在 `CODEX_PREVIEW`。
- 缩放 AutoCAD 视图后截取视觉证据：`output\validation_runs\manual-primitive-cad-probe\cad-primitive-screen.png`，大小 538584 bytes；图面可见青色 `CAD_CAPABILITY_PROBE` 基础图元和黄色 `测试柜` baseline。
- 重新运行真实 CAD 总控通过：`output\validation_runs\manual-cad-after-primitive-probe\report.json` 顶层 `status=pass`，`readback_report.json.status=geometry_verified`，`cad_capability_probe.json.status=cad_capability_verified`。
- 安全边界保持不变：只写入 `CODEX_PREVIEW`，未保存 DWG，未覆盖原图，未删除实体，未修改正式图层。当前仍不能扩大为块插入、块库、正式图层或任意业务 CAD_PLAN 全部准确。

### CAD 调用底座能力矩阵加固

- 新增 `core/verification/cad_capability_probe.py` 与 `scripts/run_cad_capability_probe.py`，用于真实 AutoCAD COM 能力探针：活动文档读取、`CODEX_PREVIEW` 图层、矩形 4 线、文字、2 个标注、created handles、handle 定向回读、类型统计、bbox 和安全边界。
- 将 `cad_capability_probe` 纳入 `core/verification/cad_validation_runner.py` 的真实 CAD step；`run_cad_validation.py` 现在不仅要求 `readback_report.json.status=geometry_verified`，还要求 `cad_capability_probe.json.status=cad_capability_verified` 且 checks 全部 `pass`。
- 新增 `tests/core/test_cad_capability_probe.py`，并扩展 `tests/core/test_cad_validation_runner.py`，覆盖能力探针成功、连接失败、handle 回读缺失、以及总控不得把非 `cad_capability_verified` 探针误判为 pass。
- 离线复验通过：`unittest discover -s tests` 为 207 tests OK；`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings；`scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\cad-foundation-no-cad-final-20260525` 为 `status=pass`。
- 单独真实 CAD 能力探针通过：`output\validation_runs\cad-foundation-capability-probe-20260525\cad_capability_probe.json` 为 `status=cad_capability_verified`，created handles 为 `3966, 3967, 3968, 3969, 396A, 396B, 39A6`。
- 整合真实 CAD 总控通过：`output\validation_runs\cad-foundation-full-cad-20260525\report.json` 顶层 `status=pass`；`readback_report.json.status=geometry_verified`；`cad_capability_probe.json.status=cad_capability_verified`，探针 handles 为 `3A5E, 3A5F, 3A60, 3A61, 3A62, 3A63, 3A9E`。
- 新增 `docs/verification/cad_foundation_capability_check.md` 记录本轮证据。全程只写入 `CODEX_PREVIEW`，未保存 DWG，未覆盖原图，未删除实体，未修改正式图层。

### Phase W 全量修复：readback 硬门禁与真实 CAD 定向回读

- 执行全量修复复验时发现一个关键门禁问题：`output\validation_runs\full-repair-cad-20260525-212001\report.json` 顶层为 `status=pass`，但 `readback_report.json.status=screenshot_captured`，`geometry_readback` 为 `not_run`，`created_handles_scope` 为 `warning`。该结果不能证明几何准确。
- 按 Phase W W.10 自动修复仓库内问题：`core/verification/cad_validation_runner.py` 现在会在 `inspect_readback` 返回 0 后继续解析 readback JSON，只有 `status=geometry_verified` 且全部 checks 为 `pass` 才允许 step 通过；否则归类为 `readback_failed`。
- 修复真实大 DWG 回读性能风险：`core/verification/inspect_dwg.py` 和 `core/cad_io/autocad_com.py` 支持按 `execution_summary.created_handles` 调用 `Document.HandleToObject(handle)` 定向回读本轮实体，避免全量枚举 ModelSpace。
- 新增 / 扩展测试：`tests/core/test_cad_validation_runner.py` 覆盖非 `geometry_verified` readback 不得让 CAD 总验证通过；`tests/core/test_verification_report.py` 覆盖按 handles 回读时不得扫描 ModelSpace。
- 复验通过：`unittest discover -s tests` 为 203 tests OK；`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings；`scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\full-repair-no-cad-final-20260525` 为 `status=pass`。
- 真实 CAD 复验通过：`output\validation_runs\full-repair-cad-retry-20260525-212916\report.json` 顶层 `status=pass`；`execution_summary.json` 记录 created handles `38E9, 38EA, 38EB, 38EC, 38ED, 38EE, 392A`；`cad-validation-screen.png` 已生成；`readback_report.json.status=geometry_verified`，`readback_scope` / `layer_entities` / `bbox_size` / `base_point` / `label_text` / `dimension_count` / `created_handles_scope` 全部 `pass`。
- 全程只写入 `CODEX_PREVIEW`，未保存 DWG，未覆盖原图，未删除实体，未修改正式图层。当前仍只允许声明 Phase W baseline `examples\plans\draw_test_cabinet.json` 的真实 CAD 几何通过。

### Phase W 真实 CAD 调用排查与 baseline 回读闭环通过

- 对“CAD 已打开但脚本无法调用”做沙箱内/用户会话对照诊断：默认命令身份 `desktop-r40v31q\codexsandboxoffline` 看不到用户桌面的 `acad.exe`、窗口和 ROT/COM 活动对象；沙箱外用户身份 `desktop-r40v31q\user` 可见 AutoCAD PID 20880、窗口 `Autodesk AutoCAD 2026 - [A1_page2_vector_full.dwg]`，且 `AutoCAD.Application`、`AutoCAD.Application.25.1`、`AutoCAD.Application.25` 均可 `GetActiveObject`。
- 诊断证据：沙箱内 `output\validation_runs\cad-com-diagnostic-20260525-210153\cad_com_diagnostic.json`；用户会话 `output\validation_runs\cad-com-diagnostic-elevated-20260525-210219\cad_com_diagnostic.json`。
- 在用户会话下复跑 W-07 首次推进到 `execute_sample_plan`，发现真实 AutoCAD `ModelSpace.AddLine` 对普通 Python tuple 报 `-2147024809` 参数无效；按 W.10 自动修复仓库内 driver 问题。
- `core/cad_io/autocad_com.py` 新增 AutoCAD COM point 转换：坐标写入前转成 `VT_ARRAY | VT_R8` float VARIANT；同步扩展 `tests/core/test_autocad_com_driver.py`，并适配 `tests/core/test_execute_plan.py` 的 fake driver 测试。
- 复跑真实 CAD 总验证通过：`output\validation_runs\cad-readback-alpha-elevated-retry-20260525-210850\report.json` 顶层 `status=pass`，`execution_summary.json` 记录 created handles `3773, 3774, 3775, 3776, 3777, 3778, 37B5`，`cad-validation-screen.png` 已生成，`readback_report.json.status=geometry_verified`。
- 已逐项审查 `readback_report.json` 关键 checks：`readback_scope`、`layer_entities`、`bbox_size`、`base_point`、`label_text`、`dimension_count`、`created_handles_scope` 全部 `pass`。全程只写入 `CODEX_PREVIEW`，未保存 DWG、未覆盖原图、未删除实体、未修改正式图层。
- 当前允许声明 Phase W baseline `examples\plans\draw_test_cabinet.json` 的真实 CAD 几何已通过；不扩大为真实项目图纸、块库或任意 CAD_PLAN 全部准确。

### Phase W W-05/W-06 推进与 COM 诊断加固

- 执行 Phase W W-05：审查 `output\validation_runs\phase-w-preflight-no-cad\report.json`，确认 no-cad preflight 顶层 `status=pass`，失败步骤数量为 0，因此无需进入失败分类修复。
- 执行 Phase W W-06：用只读 `AutoCADComDriver(connect_existing_only=True)` 探测当前 AutoCAD 前置条件，不落图、不保存、不修改图层；证据写入 `output\validation_runs\phase-w-w06-cad-probe\autocad_com_connect.stdout.txt` 与 `autocad_com_connect.stderr.txt`。
- W-06 当前结论为 `external_blocker`：当前环境无法通过 `AutoCAD.Application` 连接活动文档，底层 COM 返回 `(-2147221005, '无效的类字符串', None, None)`。因此本轮未进入 W-07 真实 CAD 总验证。
- 完成一项小型加固：`core/cad_io/autocad_com.py` 在 `connect_existing_only=True` 连接失败时保留底层 COM detail，避免把 ProgID / 注册 / 运行状态问题压成泛化错误。
- 新增 `tests/core/test_autocad_com_driver.py`，锁定 AutoCAD COM 连接失败时必须保留底层错误细节；相关 focused tests 通过，最终全量 `unittest discover -s tests` 当前为 199 tests OK。
- 复跑无 CAD 总控：`scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\phase-w-preflight-no-cad-after-w06-hardening` 顶层 `status=pass`。
- 同步更新 `README.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CORE_RESTRUCTURE_PLAN.md`、`CAD_AGENT_STATUS.md` 和 `CAD_AGENT_ISSUES.md`；继续明确 no-cad pass 与 W-06 COM 探针都不等于真实 CAD 几何验证。

### Phase W W-07/W-16 总验证收束

- 执行 W-07 真实 CAD 总验证：首次运行 `output\validation_runs\cad-readback-alpha\report.json` 暴露出 runner 缺陷，即 `autocad_com_connect` 已失败后仍继续执行落图、截图和回读，导致顶层状态被连锁错误污染为 `fail`。
- 按 W.10 自动修复仓库内问题：为 `cad_validation_runner` 增加 CAD 依赖门，`autocad_com_connect` 或 `execute_sample_plan` 失败后，后续依赖 CAD step 标记为 `not_run` 并保留 stdout/stderr 证据。
- 补充 runner 派生 artifact 清理：每轮开始清理本轮可能生成的 `execution_summary.json`、`readback_report.json` 和 `cad-validation-screen.png`，避免复用输出目录时旧证据冒充本轮结果。
- 加固 AutoCAD COM 连接兼容：`AutoCADComDriver` 现在会尝试常见版本化 ProgID，例如 `AutoCAD.Application.25.1`、`AutoCAD.Application.25`，并在失败时列出所有候选错误。
- 新增 / 扩展测试：`tests/core/test_cad_validation_runner.py` 覆盖 CAD 前置失败时依赖步骤必须 `not_run`；`tests/core/test_autocad_com_driver.py` 覆盖版本化 ProgID fallback。
- 复跑 W-07：最新报告为 `output\validation_runs\cad-readback-alpha-retry-20260525-205208\report.json`，顶层状态为 `external_blocker`。非 CAD 步骤均 pass，`autocad_com_connect` 为 `cad_connection_failed`，后续落图、截图、回读均 `not_run`。
- 完成 W-15 / W-16：新增 `docs/verification/cad_readback_alpha_check.md`，并同步更新 README、短上下文、能力矩阵、主计划、当前状态和问题记录。当前仍不能声明 baseline 真实 CAD 几何通过。
- 用户再次确认 CAD 已打开后，重跑 W-07 到 `output\validation_runs\cad-readback-alpha-retry-20260525-205208\report.json`；结果仍为 `external_blocker`。补充环境探测：系统存在两个 `acad.exe` 进程，但 `MainWindowTitle` 为空，窗口枚举未发现可见 AutoCAD/DWG 窗口，版本化 COM Dispatch 探测 30 秒超时。本轮继续不生成几何通过结论。

### Phase W CAD 验收剧本细化

- 基于当前系统遗留的 CAD 层面待检查内容，重构 `CORE_RESTRUCTURE_PLAN.md` 的 Phase W，不执行 CAD 验证，只把后续可执行步骤写入主计划。
- Phase W 现在包含：已完成内容聚合、验证范围、执行前条件、输出目录、证据清单、执行顺序总表、CAD 待检查矩阵、W-01 到 W-16 分步执行清单、失败分类、自动修复策略、`geometry_verified` 升级门槛、停止问用户条件、继续自动修条件、退出标准和完成后同步文档。
- 明确一个关键门禁：`scripts/run_cad_validation.py` 顶层 `status=pass` 仍不足以单独证明真实 CAD 几何准确；后续执行 Phase W 时必须继续审查 `readback_report.json.status` 和关键 checks，只有 `status=geometry_verified` 且证据完整时才允许声明 baseline 真实 CAD 几何通过。
- 同步更新 `CAD_AGENT_STATUS.md`，提示后续有 AutoCAD 和测试 DWG 时直接按主计划 Phase W 的 W-01 到 W-16 执行。

### 系统层状态复盘与下一阶段计划更新

- 基于 Phase O-V、系统层安全补强和最新非 CAD 基线，对根目录开发状态文档做系统级复盘；本轮不执行功能开发，只更新计划、状态、路线、设计映射和维护口径。
- 重写 `CORE_RESTRUCTURE_PLAN.md`：明确根目录没有独立 `plan.md`，当前主计划就是 `CORE_RESTRUCTURE_PLAN.md`；下一阶段收束为 Phase W 真实 CAD 回读闭环、Phase X 场景 Agent Alpha、Phase Y 空壳布局硬化、Phase Z 文档治理和回归基线。
- 重写 `CORE_STATUS.md` 为能力矩阵页，区分 `alpha_ready_non_cad`、`prototype`、`blocked_by_cad` 等状态，并明确 blank-shell pipeline 可用但不等于真实 CAD 几何准确。
- 压缩 `CAD_AGENT_STATUS.md` 为当前进展页，删除长历史式重复描述，历史细节继续由本文承载。
- 重写 `CORE_CONTEXT_BRIEF.md`，保持短入口职责，更新当前结论、下一步路线、按需展开表和文档自查命令。
- 重写 `CORE_ROADMAP.md`，从旧阶段 0-10 的错位描述调整为高层路线：已完成路线、当前 Phase W/X/Y/Z、长期路线和路线约束。
- 更新 `README.md` 的当前状态、主计划说明和后续开发主线，避免继续把旧阶段口径当作当前计划。
- 更新 `SHELL_LAYOUT_FOUNDATION_DESIGN.md`：说明它已从早期蓝图部分落地为 Phase P-V 的 blank-shell pipeline，并列出已完成能力与剩余差距。
- 更新 `SHELL_LAYOUT_TIME_ESTIMATE.md`：标注其为历史估算和预期管理材料，不作为当前开发进度来源。
- 更新 `CAD_AGENT_DECISIONS.md`：标记 D003 已被根目录 `AGENTS.md` 取代，并新增 D007 短上下文入口、D008 主 plan 映射两条决策。
- 本次复盘未删除根目录 Markdown。判断这些文件不是完全重复，而是需要职责分层；后续若继续瘦身，优先迁移到 `docs/archive/` 或 `docs/planning/`，不直接删除历史依据。

### 系统层安全重构收尾

- 完成 repo audit、测试/脚本/legacy driver bootstrap、capability registry facade 拆分、pipeline failure hardening、verification edge tests、文档同步和最终复核。
- 新增 `docs/verification/system_hardening_audit.md` 作为长期审计报告；大型维护规则已迁移到 `CAD_AGENT_RULES.md`，临时执行计划已删除。
- `scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings` 当前为 pass，0 findings；重复路径注入只保留在共享 bootstrap 与测试 fixture 中。
- 补强 repo audit 的路径污染识别：覆盖 `sys.path.append/extend`、`import sys as ...`、`from sys import path ...` 与 `__path__.append(...)` 等常见形态。
- 补强 blank-shell pipeline 与 capability runner 路径边界：workflow 输入必须留在 project root 内，输出 artifacts 必须留在 `output/` 下；缺文件、坏 JSON、越界路径返回结构化失败，不再 traceback 或写到仓库外。
- 修复 `run_validation()` 兼容入口的相对 `output_dir` 解析，使其跟随显式 `root`，避免 `root != cwd` 时报告写错位置。
- 完成最终无 CAD 验证：focused hardening tests 通过，全量 `unittest discover -s tests` 196 项通过，`self_check.py` pass，`render_preview.py --check` ready，blank-shell pipeline status ok，blank-shell 4 场景 benchmark 4/4 pass，`run_cad_validation.py --no-cad --output-dir output\validation_runs\hardening-polish-no-cad` status pass。

### 开发状态同步与非 CAD 基线复验

- 检查当前仓库状态后，确认没有独立 `plan.md`；按 `CORE_RESTRUCTURE_PLAN.md` 的约定，用户提到 `plan.md` 时默认指该主计划文件。
- 同步更新 `CORE_RESTRUCTURE_PLAN.md` 的状态口径：Phase O-V 非 CAD 主线已通过，下一步进入 Phase W 真实 CAD readback 补验与 Phase X 场景 Agent Alpha 验收。
- 复验当时的非 CAD 基线：`unittest discover -s tests`、`self_check.py`、`validate_plan.py`、`dry_run_plan.py`、`render_preview.py --check` 和 `inspect_dwg.py --no-cad` 均通过；当前测试数量以本日“系统层安全重构收尾”记录为准。
- 复验 blank-shell 链路：`scripts/run_blank_shell_pipeline.py examples\workflows\blank_shell_layout_loop.json --output-dir output\test_artifacts\blank_shell_pipeline\docs-sync` 为 status ok；`scripts/run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\docs-sync` 为 4/4 pass。
- 复验无 CAD 总控：`scripts/run_cad_validation.py --no-cad` 为 status pass；当前报告路径以本日“系统层安全重构收尾”记录为准。
- 更新 `README.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md` 和 `CORE_CONTEXT_BRIEF.md`，统一写清“非 CAD 通过不等于真实 CAD 几何准确”的证据边界。

### 稳定短上下文入口

- 新增 `CORE_CONTEXT_BRIEF.md`，作为后续 Codex 日常恢复上下文的稳定短入口，集中记录当前结论、下一步路线、按需展开表、安全门、常用验证和缓存友好约定。
- 更新 `AGENTS.md`：默认先读 `CORE_CONTEXT_BRIEF.md`，只有完整汇报、执行 Phase、卡壳回归或修改规则/记录时才展开旧的完整上下文文件组。
- 更新 `README.md` 的恢复上下文说明和推荐提问方式，把日常入口从多份大文档改为 `AGENTS.md` + `CORE_CONTEXT_BRIEF.md`。
- 更新 `CAD_AGENT_RULES.md`，新增“上下文缓存友好入口”规则，要求短入口保持稳定，详细历史继续留在计划、changelog 和 issues 中按需读取。
- 更新 `CORE_RESTRUCTURE_PLAN.md` 和 `CAD_AGENT_STATUS.md`，同步短入口与按需展开的恢复策略。

### Git 提交与推送说明

- 在 `README.md` 增加提交与推送说明，记录默认 GitHub 远端、无 `.git` 拷贝目录的初始化流程，以及提交前不纳入本机日志、截图、验证输出和临时 DWG 的规则。
- 更新 `.gitignore`，忽略 `output/*` 生成产物与 `cad_mcp.log`，保留 `output/previews/README.md` 这类目录说明文件的例外。
- 更新 `CAD_AGENT_STATUS.md`，同步这次文档与仓库卫生调整。

### Core 主计划交付协议补强

- 补强 `CORE_RESTRUCTURE_PLAN.md`：新增“执行交付协议”，明确后续 Codex 必须按 phase 执行、每个 phase 先拆 2-5 分钟小步、测试先行、证据落盘和状态同步。
- 新增 Phase O-X 依赖与交付物表，避免后续执行者跳阶段或把未验证能力当作可用能力。
- 将 `CAD_AGENT_AUTONOMOUS_VALIDATION.md` 与 `scripts/run_cad_validation.py` 纳入 Phase O、Phase W 和固定自检流程：非 CAD 阶段可跑 `--no-cad`，真实 CAD 阶段用结构化报告作为总证据。
- 新增本文交付自检清单和文本自查命令，交付前扫描不可执行占位、旧 phase 口径和脚本引用漂移。
- 调整完成判定说明：只讨论计划时不执行 phase；若计划本身改变工作流或交付规则，仍按根目录 `AGENTS.md` 同步状态和变更记录。
- 继续拆细 Phase O-X：每个 phase 增加编号化细化执行清单，覆盖上下文审计、测试先行、红灯确认、最小实现、专项验证、证据归档、文档同步和复核，便于后续 Codex 一次执行较长时间而不丢失阶段边界。
- 新增建议 Agent 分工模式：`context-auditor`、`schema-contract-agent`、`unit-test-agent`、`engine-agent`、`pipeline-agent`、`cad-validation-agent`、`docs-sync-agent`、`review-agent`，明确这些是执行分工建议，不要求新增仓库代码文件。
- 执行 Phase O：为 `core/capabilities/registry.py` 增加能力成熟度 `maturity` 与已知限制 `known_limits`，并用 `tests/core/test_capabilities.py` 锁定 registry 合约。
- 更新 `CORE_STATUS.md` 的状态口径与关键能力限制说明，明确当前 layout、drawing、proposal、verification 仍是 prototype，不能误报为空壳自动设计或几何准确。
- Phase O 验证通过：`tests.core.test_capabilities`、全量 `unittest discover -s tests`、`self_check.py`、validate、dry-run、`render_preview.py --check`、`inspect_dwg.py --no-cad`、非 CAD benchmark 和 `scripts/run_cad_validation.py --no-cad --output-dir output\validation_runs\phase-o-no-cad`。
- 执行 Phase P：新增 `core/drawing_analysis/shell_loader.py`，可将人工空壳 JSON 规范化为 `SHELL_MODEL`，并校验 units、boundary、opening width、fixed obstacles 和 no-place zones。
- 扩展 `core/schemas/shell_model.schema.json` 和 `core/schemas/project_model.schema.json`，让 `SHELL_MODEL` 支持 `boundary.type`、openings、fixed obstacles、no-place zones、required connections、building elements、uncertainties 和 source，让 `PROJECT_MODEL` 可保留 shell_id、source 与 uncertainties。
- 更新 `core/project_model/project_builder.py` 与 `core/capabilities/registry.py`：`project_model.build` 可接收可选 `shell_model`，新增 capability `drawing_analysis.load_shell_model`。
- 新增 `examples/shell_models/retail_blank_shell.json`、`examples/shell_models/office_blank_shell.json` 和 `tests/fixtures/invalid_models/shell_model.opening_missing_width.invalid.json`；`projects/sample_blank_shell/input/shell.manual.json` 已从旧 drawing-style 手工输入升级为 `SHELL_MODEL`。
- Phase P 验证通过：`tests.core.test_shell_loader`、`tests.core.test_project_model`、`tests.core.test_schema_validation`、`tests.core.test_capabilities`、shell example schema validator、全量 `unittest discover -s tests`、非 CAD benchmark 和 `scripts/run_cad_validation.py --no-cad --output-dir output\validation_runs\phase-p-no-cad`。
- 补强 Phase P：`tests/core/test_shell_loader.py` 增加 legacy drawing-style 输入兼容回归，确认旧 `DRAWING_MODEL.spaces` 风格手工标注仍可由 `load_manual_shell()` 规范化为 `SHELL_MODEL`。
- 执行 Phase Q：新增 `core/geometry_backends/rect2d.py` 和 `core/geometry_backends/orthogonal.py`，提供无依赖 rect 操作、bbox no-place-zone 保守扣减、path strip、门洞/障碍距离和正交多边形校验。
- 更新 `core/geometry_backends/registry.py`，登记默认 `rect2d` 与 `orthogonal_polygon` 后端；保留 `cadquery`、`build123d`、`ifcopenshell` 为未来可选槽位，不引入新依赖。
- 迁移 `core/layout_engine/basic_layout.py` 与 `clearance.py` 的 bbox inside / overlap / clearance gap 到 `core.geometry_backends.rect2d`，减少 layout 层散落几何算法。
- Phase Q 目标测试通过：`tests.core.test_geometry_rect2d`、`tests.core.test_geometry_orthogonal`、`tests.core.test_geometry_backends` 与 `tests.core.test_shell_loader`。
- 执行 Phase R：新增 `core/layout_engine/path_generation.py`，实现 `generate_circulation_candidates(project_model, preferences)`，输出 `straight_spine`、`l_spine`、`along_wall` 三类 `CIRCULATION_MODEL` 候选。
- 扩展 `PROJECT_MODEL`：`project_builder` 现在保留 `shell_context.openings`、`fixed_obstacles`、`no_place_zones`、`required_connections` 和 `building_elements`，供后续动线和功能区切分复用。
- 扩展 `core/schemas/circulation_model.schema.json`：路径必须包含 `polyline`、`connects`、`path_surface`、`blocked_reasons` 和 `score`；新增 `examples/circulation_models/retail_straight_spine.json` 与 `retail_l_spine.json`。
- 更新 `core/capabilities/registry.py`，登记 `layout.generate_circulation_candidates`，让动线生成成为可发现、可验证、非 CAD 的 Core capability。
- Phase R 目标测试通过：`tests.core.test_project_model`、`tests.core.test_circulation_generation`、`tests.core.test_schema_validation`、`tests.core.test_capabilities`，并通过 circulation example schema validator。
- 执行 Phase S：新增 `core/layout_engine/zone_splitter.py`，实现 `split_zones(shell_model, circulation_model, constraints)`，可围绕 circulation path surface 切出左右 `FUNCTION_ZONE` 候选。
- 扩展 `core/schemas/function_zone.schema.json`：zone 现在包含 `geometry`、`area`、`depth`、`frontage`、`side_of_path`、`candidate_functions`、`score` 和 `uncertainties`；同步更新 minimal zone example。
- 新增 `examples/function_zones/retail_zone_left.json` 与 `office_zone_desk_band.json`，并扩展 `tests/core/test_zone_splitter.py` 与 `tests/core/test_schema_validation.py`。
- 更新 `core/capabilities/registry.py`，登记 `layout.split_function_zones`，让 shell -> circulation -> function zones 的非 CAD 能力链可发现。
- 修复 `rect2d.subtract_no_place_zones()` 状态语义：不相交的 no-place-zone 不再误报 `partial`，并增加回归测试。
- Phase S 目标测试通过：`tests.core.test_zone_splitter`、`tests.core.test_schema_validation`、`tests.core.test_capabilities`、function zone schema validator。
- 执行 Phase T：新增 `libraries/objects/object_defaults.json`，将对象默认尺寸从代码常量迁出，并扩展 `desk`、`chair`、`bed`、`sofa`、`counter`、`display_unit`。
- 新增 `core/layout_engine/placement.py`，实现由 FUNCTION_ZONE、对象尺寸和 block metadata 驱动的保守 placement，输出 `bbox`、`clearance_bbox`、`source` 和失败原因。
- 扩展 `libraries/blocks/block_library.example.json`，增加 desk、sofa、display_unit 示例块；找不到块时保留 `OBJECT_SPEC` fallback。
- 扩展 `object_spec.schema.json` 与示例：新增 `examples/object_specs/desk_1400x700.json`、`sofa_2200x900.json`。
- 更新 `core/capabilities/registry.py`，登记 `layout.create_zone_placements`，让 function zones -> placements 的非 CAD 能力链可发现。
- Phase T 目标测试通过：`tests.core.test_placement_engine`、`tests.core.test_object_engine`、`tests.core.test_block_engine`、object spec schema validator。
- 执行 Phase U：扩展 `DESIGN_PROPOSAL` schema，支持 `candidates[]`、`confirmed_candidate_id`、`comparison_summary`，并把 evidence 拆为 `from_user`、`from_drawing`、`from_shell`、`from_library`、`from_algorithm`、`inferred`。
- 更新 `design_proposal.py`，可将多个 layout candidates 包装为多候选 proposal；更新 `proposal_to_plan.py` 与 `plan_engine/model_to_plan.py`，支持按 `confirmed_candidate_id` 选择要转 CAD_PLAN 的候选。
- 更新 `proposal_comparison.py`，支持带 `weight_source` 的场景权重参与候选排序，防止偏好权重变成隐式常量。
- 新增 `examples/design_proposals/blank_shell_retail_options.json` 和 `tests/core/test_proposal_multi_candidate.py`。
- Phase U 目标测试通过：`tests.core.test_proposal_multi_candidate`、`tests.core.test_proposal_engine`、`tests.core.test_proposal_comparison`、design proposal schema validator。
- 执行 Phase V：新增 `core/workflows/blank_shell_pipeline.py` 与 `scripts/run_blank_shell_pipeline.py`，串联 `SHELL_MODEL -> PROJECT_MODEL -> CIRCULATION_MODEL -> FUNCTION_ZONE -> placements -> LAYOUT_PROPOSAL -> DESIGN_PROPOSAL -> CAD_PLAN -> dry-run -> VERIFICATION_REPORT(unverified)`。
- 新增 `examples/workflows/blank_shell_layout_loop.json`、`blank_shell_office_layout_loop.json`、`blank_shell_residential_layout_loop.json`、`blank_shell_restaurant_layout_loop.json`，以及 `examples/benchmarks/blank_shell_core_benchmark.json`。
- 新增 `examples/shell_models/office_small_suite_shell.json`、`residential_living_room_shell.json`、`restaurant_small_front_shell.json` 和 `agents/restaurant/preferences.json`，让 blank-shell benchmark 覆盖四个不同 workflow，而不是同一输入重复运行。
- 新增 `projects/sample_blank_shell/expected/expected_notes.md`，明确空壳 pipeline 的非 CAD 预期和 `unverified` 证据边界。
- 更新 `core/benchmarks/runner.py`，让 benchmark runner 可调度 `pipeline: blank_shell` case，并记录 candidates、zones、placements、CAD_PLAN、失败检查、dry-run 和 verification 指标。
- 更新 `core/capabilities/registry.py`，登记 `workflow.blank_shell_pipeline`，让完整空壳 pipeline 成为可发现、可运行、可验证的 Core capability。
- 大范围审计修复：blank-shell pipeline 现在从 placement 实际来源派生 `OBJECT_SPEC`，避免 block 尺寸与 CAD_PLAN 默认对象尺寸不一致；`path_to_rect_strips()` 跳过重复连续点；zone placement 在剩余空间不足时返回 blocked placement 而不是异常。
- 更新测试：新增/扩展 `tests/core/test_blank_shell_pipeline.py`、`tests/core/test_benchmarks.py`、`tests/core/test_benchmark_cli.py`、`tests/core/test_geometry_rect2d.py`、`tests/core/test_placement_engine.py`、`tests/core/test_capabilities.py` 与 `tests/agents/test_scene_preferences.py`。
- Phase V 目标测试通过：`tests.core.test_blank_shell_pipeline`、`tests.core.test_benchmarks`、`tests.core.test_benchmark_cli`、`tests.core.test_capabilities`、`tests.agents.test_scene_preferences`；当前全量测试数量以本日“系统层安全重构收尾”记录为准。

### CAD 自主验证闭环

- 新增 `CAD_AGENT_AUTONOMOUS_VALIDATION.md`，把“不要遇到第一处失败就停”的口头要求固化为可复用执行手册。
- 新增 `core/verification/cad_validation_runner.py` 和 `scripts/run_cad_validation.py`，提供一键 CAD 验证总控：依赖探针、自检、单元测试、validate、dry-run、截图能力、benchmark、AutoCAD COM 连接、预览落图、截图和实体回读。
- 验证脚本会写入 `output/validation_runs/<timestamp>/report.json`、`report.md`、各步骤 stdout/stderr、`execution_summary.json`、`readback_report.json` 和截图路径。
- 新增失败分类：`missing_dependency`、`cad_connection_failed`、`repo_regression`、`cad_plan_invalid`、`dry_run_failed`、`execution_failed`、`screenshot_failed`、`readback_failed`，让 Codex 能区分仓库内可修问题和用户侧外部阻塞。
- 新增 `tests/core/test_cad_validation_runner.py`，覆盖 CAD 连接失败归类为 `external_blocker`，以及全部步骤成功时输出 `pass`。
- 在 `CAD_AGENT_RULES.md` 增加“CAD 层面验证要走自主验证闭环”，要求 Codex 对仓库内问题自行最小复现、最小修复并复验。
- 更新 `CAD_AGENT_STATUS.md`，把回家或换机验证入口调整为 `CAD_AGENT_AUTONOMOUS_VALIDATION.md` + `scripts/run_cad_validation.py`。

### 外部方法论内化为 Core runtime

- 不复制外部项目代码，只抽象其工程思路，新增 `core/capabilities/registry.py`：能力可发现、输入先校验、输出 contract、风险等级、CAD 依赖和验证命令登记。
- 新增 `core/workflows/artifact_graph.py`，把 workflow artifacts 转成依赖顺序、路径检查和循环依赖检测。
- 新增 `core/geometry_backends/registry.py`，默认使用无依赖 `cad_plan_rect2d`；将 `cadquery`、`build123d`、`ifcopenshell` 仅登记为未来可选后端槽位，不成为当前依赖。
- 新增 `core/benchmarks/runner.py`、`scripts/run_benchmark_suite.py` 和 `examples/benchmarks/non_cad_core_benchmark.json`，让非 CAD pipeline 具备可重复 benchmark 基线。
- 新增 `core/object_engine/object_explainer.py` 和 `core/proposal_engine/proposal_comparison.py`，补齐对象尺寸/构件来源说明和多候选 layout 比较。
- 补齐 `tests/fixtures/invalid_models/`，让每个注册模型至少有一个 invalid fixture。
- 扩展 `examples/project_models/` 到 generic、retail、residential、office 多场景；扩展 `libraries/blocks/block_library.example.json` 到更多通用块类别。
- 新增 `docs/verification/` 与 CAD 延后补验模板，继续明确非 CAD 结果不能替代真实 CAD 落图、截图和实体回读。
- 单元测试扩展到 109 项；新增 capability、artifact graph、geometry backend、benchmark、object explanation、proposal comparison、shell/circulation/function-zone schema、schema invalid fixture、multi-domain project model、scene preference diff 和 block library 覆盖。

### 非 CAD 全量底座闭环深化

- 根据多个并行 Agent 对 plan、schema、engine、verification、safety 和 pipeline 的审计结果，继续推进第二轮非 CAD 底座开发。
- 新增 `core/safety/policy.py`，并接入 `core/execution/execute_plan.py`；默认只允许 `CODEX_PREVIEW`，正式图层、删除、保存、覆盖和未确认计划必须有显式批准。
- 新增 `core/project_model/project_builder.py`、`core/model_loop/reference_checker.py`、`core/schemas/registry.py`，补齐项目模型构建、workflow schema 校验和跨模型引用检查。
- 新增 `core/drawing_analysis/manual_model.py`、`entity_summary.py`，支持 CAD 不可用时通过手工 JSON 或简化实体列表继续推进图纸理解。
- 新增 `core/block_engine/block_selector.py`、`block_placement.py`，支持块库元数据筛选、fallback object spec 和 block insertion intent。
- 扩展 `core/layout_engine/`：增加 collision、clearance、scoring 和多对象 candidates。
- 拆分 `core/object_engine/object_to_plan.py` 与 `core/proposal_engine/proposal_to_plan.py`，让对象/方案生成与 `CAD_PLAN` 转换分离。
- 新增 `core/plan_engine/model_to_plan.py`、`dry_run_report.py`，支持高层模型到安全预览计划和机器可读 dry-run report。
- 新增 `core/workflows/non_cad_pipeline.py` 与 `scripts/run_non_cad_pipeline.py`，输出 `PROJECT_MODEL`、`OBJECT_SPEC`、`LAYOUT_PROPOSAL`、`DESIGN_PROPOSAL`、`CAD_PLAN`、dry-run report 和 `VERIFICATION_REPORT(unverified)`。
- 强化验证证据门：裸 `entities_are_scoped=True` 不再足以升级为 `geometry_verified`；必须有 created handles 覆盖；截图路径不存在时不算截图证据。
- 为 `commercial_fitout`、`residential`、`office` 增加 `preferences.json`，并在 pipeline 中接入场景偏好。
- 新增 `tests/core/test_style_engine.py`，让 modern / european / minimal style token 对对象构件差异形成回归约束。
- 扩展 cabinet/shelf/table 的基础组件表达，并为 schema 职责边界增加测试：`DESIGN_BRIEF` 不承载落图图层，`CAD_PLAN` 不承载方案推理 evidence。
- 扩展 `DESIGN_PROPOSAL.evidence`，加入 `from_library` 来源字段。
- 新增 `core/layout_engine/circulation.py`，让场景 preferences 中的 `main_aisle_width_mm` 进入 Core layout circulation check。
- 新增 `projects/sample_blank_shell/input/shell.manual.json`，作为非 CAD 空壳布局底座的手工输入样例。
- 扩展 `core/verification/verification_report.py`，增加 before/after snapshot diff、批量 report 汇总和失败修复建议字段。
- 扩展测试到 89 项；当前非 CAD 基线为 `unittest discover -s tests` 通过、`self_check.py` pass、`render_preview.py --check` ready、非 CAD pipeline status ok。

### 第二轮 Core 大规模重装

- 将 `CORE_RESTRUCTURE_PLAN.md` 从剩余工作概览扩展为非 CAD 全量底座开发计划，新增 Phase A-M、待校验登记表、每阶段非 CAD 验证命令和 CAD 延后补验总清单。
- 收束 `cad_agent/`：三份旧文档已标注为 legacy，新增 `docs/architecture/cad_workflow.md` 和 `docs/architecture/cad_plan_boundary.md` 作为 Core 架构入口。
- 收束 `libraries/domains/`：新建 `libraries/domain_presets/` 并复制 domain preset；旧目录保留 legacy README 作为兼容入口。
- 新增 9 个高层 schema 与最小 example：`DESIGN_BRIEF`、`DRAWING_MODEL`、`PROJECT_MODEL`、`OBJECT_SPEC`、`STYLE_PROFILE`、`BLOCK_LIBRARY`、`LAYOUT_PROPOSAL`、`DESIGN_PROPOSAL`、`VERIFICATION_REPORT`。
- 新增 `core/schemas/validator.py`，提供无外部依赖的 schema example 校验入口。
- 新增 `core/verification/verification_report.py`，并增强 `core/verification/inspect_dwg.py`：默认不连接 CAD，显式 `--connect-cad` 才读取真实 AutoCAD；支持 `--plan`、`--format json`、`--no-cad`。
- 为 `core/cad_io/autocad_com.py` 增加 `snapshot_modelspace()` 只读实体快照入口。
- 新增第一批设计引擎原型：`core/object_engine/parametric_objects.py`、`core/style_engine/style_profile.py`、`core/block_engine/block_library.py`、`core/layout_engine/basic_layout.py`、`core/proposal_engine/design_proposal.py`。
- 新增 `libraries/styles/modern.json`、`european.json`、`minimal.json` 和 `libraries/blocks/block_library.example.json`。
- 新增 `agents/SCENE_AGENT_RULES.md` 和 `agents/commercial_fitout/workflows/blank_store_to_layout.md`、`existing_plan_to_elevation.md`，明确场景 Agent 只存偏好和 workflow，不复制 Core 算法。
- 新增/扩展测试：高层 schema 校验、对象/风格/块/布局/方案原型、验证报告、场景 Agent 边界；第一批单测从 13 项扩展到 35 项，随后非 CAD 底座深化扩展到 89 项。
- 修复测试环境问题：将需要写文件的测试改用 `output/test_artifacts`，避免当前沙箱无法删除系统临时目录导致失败。
- 根据复盘 Agent 审查补强验证与确认门：`VERIFICATION_REPORT` 失败优先、校验基点、按目标图层统计文字/标注、未隔离本次执行实体时不声称 `geometry_verified`；`DESIGN_PROPOSAL.needs_confirmation=true` 时不得转 `CAD_PLAN`；`CAD_PLAN.needs_confirmation=true` 时执行层默认拒绝执行。
- 增强场景 Agent 边界测试：扫描 `agents/` Python 文件，禁止在场景层实现 CAD 执行、回读或校验核心能力。
- 记录 CAD 不可稳定打开时的验证策略：非 CAD 层按单测、schema、dry-run、自检和 fake readback 完整验证；真实 CAD 落图、实体回读和截图补验写入 `CORE_RESTRUCTURE_PLAN.md` 延后清单。

### 默认中文沟通规则

- 将根目录 `AGENTS.md` 从英文规则改为中文规则，并新增“默认中文输出”要求。
- 将 `skills/cad-drawing/SKILL.md` 改为中文说明，并要求面向用户的解释、状态汇报、方案讨论、追问和结论默认使用中文。
- 在 `CAD_AGENT_RULES.md` 增加“默认中文沟通”规则，明确代码、命令、路径、Schema 字段、JSON key、工具名和 API 名称可保留英文或原文。
- 更新 `CAD_AGENT_STATUS.md` 和 `CAD_AGENT_ISSUES.md`，记录这次由用户反馈触发的语言策略修正。

### 空壳布局底座设计沉淀

- 新增根目录 `SHELL_LAYOUT_FOUNDATION_DESIGN.md`。
- 将“空壳 CAD / 空户型 -> 空壳模型 -> 项目约束 -> 动线 -> 功能区 -> 对象/图块 -> 布局方案 -> CAD_PLAN -> 预览和验证”的通用 Core 子能力路线沉淀为设计说明。
- 明确该能力属于 Core 子能力组合，不是公司专用平面方案 Agent。
- 明确第一版允许人工标注空壳输入，不要求一次性自动识别任意 DWG。
- 明确 Core 与 `agents/`、`libraries/`、`projects/` 的边界，避免后续实现跑偏。
- 补充数据模型建议、模块职责、分阶段路线、执行自检链路、验收标准和风险规则。
- 更新 `CAD_AGENT_STATUS.md`，说明该文档是后续开发蓝图，不代表功能已实现。

### 架构重装设计

- 新增根目录 `CORE_RESTRUCTURE_PLAN.md`，作为下一轮大规模仓库重装前的设计草案。
- 明确未来仓库定位从“单一 CAD 绘图流程”升级为“通用 CAD Agent Core Lab”。
- 明确开发重心：通用底座优先，场景 Agent 轻量化。
- 明确 `core/`、`agents/`、`libraries/`、`projects/`、`docs/`、`tests/` 的目标职责。
- 明确未来 Core 能力模块：CAD IO、图纸理解、项目模型、对象引擎、风格引擎、图库块引擎、布局引擎、方案引擎、计划引擎、执行、验证和安全。
- 暂停沿旧路线继续堆叠阶段 5 之前，先等待用户确认是否执行仓库重装。

### 第一轮仓库重装

- 新增 `CORE_STATUS.md` 和 `CORE_ROADMAP.md`，用能力矩阵和 Core 阶段路线追踪通用底座进度。
- 创建目标结构：`core/`、`agents/`、`projects/`、`docs/architecture`、`docs/decisions`、`docs/roadmap`、`tests/core`、`tests/agents`、`tests/fixtures`。
- 将现有核心实现迁入 Core：
  - `core/plan_engine/validate_plan.py`
  - `core/plan_engine/dry_run_plan.py`
  - `core/execution/execute_plan.py`
  - `core/verification/inspect_dwg.py`
  - `core/verification/render_preview.py`
  - `core/verification/self_check.py`
  - `core/cad_io/autocad_com.py`
  - `core/cad_io/dxf_writer.py`
  - `core/cad_io/zwcad_com.py`
- 保留旧入口兼容：
  - `scripts/*.py` 作为 Core CLI 薄包装器。
  - `drivers/*.py` 作为 `core.cad_io` 薄包装器。
  - `schemas/*.json` 与 `core/schemas/*.json` 过渡期保持一致。
- 新增轻量场景 Agent 脚手架：`commercial_fitout`、`residential`、`office`、`restaurant`、`exhibition`、`custom`。
- 将核心测试迁入 `tests/core/`，并新增 `tests/core/test_core_restructure.py`，覆盖旧入口兼容、新 Core 入口、schema 一致性和 Agent manifest。
- 更新 `README.md`、`AGENTS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_RULES.md`、`docs/ROADMAP.md`，让入口文档与 Core Lab 架构一致。
- 修剪 `CORE_RESTRUCTURE_PLAN.md`：删除已经完成的第一轮重装待办，保留遗留目录收束、高层 schema、实体回读、对象/风格、图库块、布局、图纸理解、项目模型和方案引擎等剩余计划。

### 阶段 4：预览绘制最小闭环

- 新增 `tests/test_execute_plan.py`，用记录型 driver 验证执行器会请求绘制测试柜矩形、文字和两条基础尺寸标注。
- 将 `scripts/execute_plan.py` 从脚手架推进为第一版真实执行核心：
  - 读取 CAD_PLAN。
  - 复用 `validate_plan.py` 校验。
  - 仅支持当前安全范围内的 `draw_object` + `absolute` placement。
  - 默认只允许 `CODEX_PREVIEW` 图层。
  - 计算矩形、中心文字和水平/竖向尺寸标注位置。
  - 通过 driver 接口调用绘制层。
- 将 `drivers/autocad_com.py` 从占位推进为第一版 AutoCAD COM 驱动：
  - 可连接当前 AutoCAD 应用。
  - 可确保图层存在。
  - 可绘制矩形四边、文字和对齐尺寸标注。
- 使用 CAD-MCP 在当前打开的 CAD 文件中完成实际预览绘制：
  - 绘制 1800 x 600 测试柜矩形。
  - 添加中心文字 `测试柜`。
  - 添加水平和竖向基础尺寸标注。
  - 全部绘制到 `CODEX_PREVIEW` 图层。

### 验证

- `validate_plan.py` 对 `examples/plans/draw_test_cabinet.json` 返回 `VALID CAD_PLAN`。
- `dry_run_plan.py` 能正确预演测试柜对象、尺寸、位置、图层、文字和尺寸开关。
- `tests/test_execute_plan.py` 通过。
- CAD-MCP 绘图调用返回 AutoCAD COM 对象，说明实体已写入当前打开的 CAD 文档。

### 卡壳自查机制

- 新增 `CAD_AGENT_BLOCKER_PLAYBOOK.md`，沉淀“画不准、画不出来、验证不了”时的自查、复现、截图、修复和记录流程。
- 在 `CAD_AGENT_RULES.md` 增加“卡壳时先自查，不盲目重试”规则。
- 在 `README.md` 增加卡壳恢复入口和自检命令。
- 更新 `CAD_AGENT_STATUS.md`，记录横向自查机制。

### 自检与截图入口

- 新增 `scripts/self_check.py`，用于检查核心文件、示例 CAD_PLAN、预览执行路径和截图工具链。
- 扩展 `scripts/render_preview.py`，支持 `--check` 检查截图能力，支持 `--capture-screen` 保存当前可见屏幕截图。
- 新增 `tests/test_render_preview.py`。
- 新增 `tests/test_self_check.py`。

### AGENTS 规则入口

- 新增根目录 `AGENTS.md`，用短规则触发 CAD Agent 上下文读取和绘图自检门。
- 历史阶段曾新增 `CAD测试相关文件/AGENTS.md`，在 CAD 开发包内部固化恢复入口、绘图准确性验收门、卡壳自查流程和原图保护规则；当前现行入口已迁移为仓库根目录 `AGENTS.md` + Core 文档结构。

### 补充原因

- 用户希望未来任意阶段卡壳时，Codex 能先自己找原因，而不是反复试错或把问题直接丢回用户。
- 阶段 4 和后续绘图能力都需要视觉证据；原有目录只有截图输出占位和脚手架，没有可运行的截图检查/自检入口。
- 用户希望这些规则被放入可被 Codex 自动读取的 `AGENTS.md`，避免未来只靠聊天记忆执行。

### 补充验证

- 已确认 CAD-MCP 虚拟环境具备 `PIL`、`win32gui`、`win32com`。
- 新增测试先失败，随后通过实现修复。

## 2026-05-24

### 通用化调整

- 将 `README.md` 定位从当前测试目录调整为“通用 CAD Agent 开发包”。
- 明确本文件夹不绑定当前家装图纸、不绑定当前电脑。
- 明确完整能力由“本文件夹 + 运行环境 + 项目图纸”共同组成。
- 将 `CAD_AGENT_STATUS.md` 当前阶段更新为“阶段 3：CAD_PLAN 校验和 dry-run 已跑通，下一步进入预览绘制”。
- 在 `CAD_AGENT_RULES.md` 增加“通用开发包定位”。
- 扩展 domain 枚举，支持 `exhibition`、`hotel`、`education`、`healthcare`、`industrial`、`custom`。
- 增加办公、餐饮、展厅、酒店、教育、医疗、工业、通用自定义行业包占位。
- 统一 `README.md` 的恢复入口说明：先看 README，再看 4 个项目管理文件。

### 通用化原因

- 用户确认最终目标是可迁移的通用 CAD Agent 开发包。
- 该文件夹未来应能复制到其他电脑和其他 CAD 项目中复用。
- 具体家装图纸只是第一套测试现场，不应污染通用规则。

### 新增

- 创建 `CAD测试相关文件/README.md`，作为测试工作区入口。
- 创建 `CAD_AGENT_STATUS.md`，记录当前开发阶段。
- 创建 `CAD_AGENT_RULES.md`，记录长期规则。
- 创建 `CAD_AGENT_CHANGELOG.md`，记录变更历史。
- 创建 `CAD_AGENT_ISSUES.md`，记录错误和修复。
- 创建 `CAD_AGENT_DECISIONS.md`，记录关键决策和原因。
- 创建第一版目录框架：`cad_agent/`、`skills/`、`schemas/`、`examples/`、`scripts/`、`drivers/`、`libraries/`、`tests/`、`output/`。
- 创建第一版 `CAD_PLAN` Schema 和测试柜示例。
- 创建 `cad-drawing` Skill 骨架。
- 创建 `scripts/validate_plan.py`，用于校验第一版 CAD_PLAN。
- 创建 `scripts/dry_run_plan.py`，用于预演 CAD_PLAN。

### 调整

- 将旧的 `CAD_AGENT_BUILD_GUIDE.md`、`CODEX_CAD_DEV_LOG.md`、`CODEX_CAD_RULES.md` 移动到 `docs/archive/`。

### 决策

- 当前先不创建根目录 `AGENTS.md`，避免过早影响所有 Codex 行为。
- 当前先不引入 SQL。
- 当前先不做完整自动设计。
- 当前先以 `CAD_PLAN` 作为白话和 CAD 绘制之间的中间层。

### 原因

- 用户希望隔几天回来仍能知道开发进度。
- 用户希望规则能随着需求、测试、错误不断迭代。
- 用户希望整个根目录作为 CAD 测试方向，但 CAD 相关资料不要散落在根目录。

### 验证

- 使用 CAD-MCP 虚拟环境 Python 成功运行 `validate_plan.py`。
- 使用 CAD-MCP 虚拟环境 Python 成功运行 `dry_run_plan.py`。
- 发现全局 `python` 命令不可用，已记录到 `CAD_AGENT_ISSUES.md`。
- 发现中文终端输出需要显式 UTF-8，已记录到 `CAD_AGENT_ISSUES.md`。
