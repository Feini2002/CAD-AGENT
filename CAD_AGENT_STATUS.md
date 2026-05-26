# 通用 CAD Agent 开发包当前进展

最后更新：2026-05-26

本文是当前进展页，只保留“现在到哪、证据是什么、风险边界是什么”。历史流水见 `CAD_AGENT_CHANGELOG.md`，能力矩阵见 `CORE_STATUS.md`，唯一 `PlanMD` / 主计划见 `CORE_RESTRUCTURE_PLAN.md`。后续任务和优先级只写入 PlanMD，避免状态页变成第二份计划。

## 当前阶段

### 2026-05-26 Codex 本地真实 CAD 校验扩样主线写入 PlanMD

- 用户明确指出当前缺大量“本地真实 CAD 校验层”的测试；已写入唯一 `PlanMD`，作为下一轮默认优先补强方向。
- `CORE_RESTRUCTURE_PLAN.md` 新增“本地真实 CAD 校验扩样主线”，先列出 10 类测试方向：环境与安全守卫、baseline 回归、基础实体矩阵、CAD_PLAN fixture suite、block / attribute / hatch、样本项目闭环、多场景组合、负向安全、视觉辅助一致性、趋势和审计。
- 同步拆出 `LCAD-01` 到 `LCAD-11` 小任务包，从 manifest / strict runner / ActiveDocument guard 开始，再扩 baseline、primitive、CAD_PLAN fixtures、block / attribute / hatch、project sample、scene composition、negative safety 和 evidence trend rollup。
- 这只是计划写入，不新增真实 CAD 运行证据；当前真实 CAD 几何结论仍只限既有 baseline、受控 block alpha 和少量 composition 样本。

### 2026-05-26 Codex 本地 CAD 回归矩阵加固

- 当前最新回归基线：`456 tests OK`。
- 新增本地 CAD 回归矩阵：`core/verification/local_cad_regression.py` + `scripts/run_local_cad_regression.py`，把 baseline 总控、project sample CAD check 和 interior composition CAD check 统一汇总为 `local_cad_regression_report.json`。
- no-CAD 安全复验：`scripts/run_local_cad_regression.py --no-cad --output-dir output\validation_runs\local-cad-regression-no-cad` 为 `status=pass`，`step_count=3`，`deferred_case_count=2`，`geometry_verified_case_count=0`。
- 严格模式门禁：真实 CAD 模式可加 `--require-cad-verified`；project sample 或 composition 任一子项不是 `geometry_verified` 时，矩阵顶层失败，避免 deferred / 顶层 pass 被误读。
- 依赖保护：composition CAD check 只有在 `interior_delivery_benchmark` 成功产出 artifacts 后才运行；前置失败时记录 `not_run` 和 `blocked_by`，不会拿空目录或旧产物继续写 CAD。
- 本轮未运行真实 AutoCAD，不新增 `geometry_verified` 结论；新增的是“本地真实 CAD 回归入口和 no-CAD 负向证据门禁”。

### 2026-05-26 Codex 进入下一阶段前雕琢

- 当前最新回归基线：`452 tests OK`；`scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings。
- no-CAD 总控复验：`scripts/run_cad_validation.py --no-cad --output-dir output\validation_runs\codex-polish-final-no-cad` 为 `status=pass`。
- 可迁移性修复：`CAD_AGENT_BLOCKER_PLAYBOOK.md` 的 CAD-MCP Python 命令不再写死固定 Windows 用户目录，改为 `$env:USERPROFILE` 派生；新增文档治理测试防止活跃手册回退到固定用户路径。
- CLI 易用性修复：`run_office_scene_beta_benchmark.py`、`run_residential_scene_beta_benchmark.py`、`run_restaurant_scene_beta_benchmark.py` 现在同时支持 `--output` 和 `--output-root`，与通用 benchmark runner 的参数习惯对齐。
- 复验脚本：blank-shell benchmark 8/8、office alpha 18/18、interior delivery 3/3、project sample 2/2、proposal confirmed 2/2、CAD beta evidence rollup 5/5、scene beta 三套合计 25/25 均通过。本轮未运行真实 CAD，不新增 `geometry_verified` 结论。

### 2026-05-26 Codex 维护 4-7 包：结构整理和优化

- 当前最新回归基线：`450 tests OK`；`scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings。
- 结构整理：新增 `core/path_safety.py`，公共化 project root / output root / safe path segment 校验，减少各 runner 私有路径判断重复。
- 安全入口加固：project sample CAD check、composition CAD check、beta suite、proposal confirmed、drawing-read、blank-shell / non-CAD pipeline 等入口在写 artifact、读取 workflow 或连接 AutoCAD 前先做边界校验；无效输入统一输出结构化 invalid / blocker，不再抛散乱异常或越界写入。
- Schema registry 整理：所有 `core/schemas/*.schema.json` 已纳入 `MODEL_SCHEMAS`，并补齐 invalid fixtures，防止 schema 文件存在但 validator 不知道。
- 文档治理：`docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` 不再承载下一包建议或剩余 Backlog 副表；状态页只记录证据和风险，优先级仍只以唯一 `PlanMD` 为准。

### 2026-05-26 Codex 维护 1-3 包：证据止血、基线同步、路径安全

- 当前最新回归基线：`432 tests OK`；`scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings。
- 证据口径修正：`BETA-PROJECT-SAMPLE-05` 当前仓库存档 no-CAD 报告是 `deferred`，不是真实 AutoCAD `geometry_verified`；新增 `--require-cad-verified` 后，deferred 报告会返回非 0，避免交接或 CI 误判。
- 路径安全加固：样本 manifest input 必须留在样本目录内；benchmark / drawing-read `case_id` 必须是安全 path segment；benchmark output root、drawing-read output root、CAD validation output dir 均限制在仓库 `output/` 下。
- 验收脚本：focused 1-3 包测试 48 OK；no-CAD validation `output\validation_runs\codex-maintenance-fix-no-cad` pass；blank-shell benchmark 8/8 pass；office alpha benchmark 18/18 pass；interior delivery benchmark 3/3 pass；strict no-CAD project sample CAD check 按预期返回 1 并保存 deferred 报告。

### 2026-05-26 Codex 深度全量安全复盘与加固

- 本轮历史回归基线：`424 tests OK`；`scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings。
- 本轮从 Cursor 大量改动后做了全量盘查：Python AST 解析 `248` 个文件 0 errors，JSON 解析 `166` 个文件 0 errors，坏证据词 / 系统临时目录回归 / 旧 blank-shell 内部入口引用均未命中。
- 修复 `tests/core/test_project_sample_protocol.py` 使用系统 temp 造成的 `PermissionError` 回归，测试临时目录统一回到 `output/test_artifacts`。
- 加固 benchmark evidence gate：所有 `examples/benchmarks/*.json` case 必须包含 `expected.evidence_state` / `geometry_accuracy` / `screenshot_role`；`proposal_confirmed_benchmark` 现在输出并校验 `evidence_summary`。
- 修复项目样例 CAD check 与 drawing standard profile 的证据词表偏差：失败/延期路径统一使用 `deferred_cad_readback_required` + `not_verified_without_cad_readback`，`screenshot_role` 统一使用 `not_applicable` / `visual_aid_only` 合法词。
- repo audit 暴露的 6 个过大 Python 文件已拆分：benchmark expected 比对、evidence vocabulary、composition preview、blank-shell candidate sets、CAD validation 测试 payload、benchmark validation tests 均已独立成小模块；旧公开入口保持兼容。
- 验收脚本：`self_check.py` pass；`render_preview.py --check` ready（当前环境 AutoCAD window unavailable，截图仍仅为视觉辅助）；`run_project_sample_protocol_scan.py` pass；`run_project_sample_benchmark.py` 2/2 pass；`run_proposal_confirmed_benchmark.py` 2/2 pass；`run_cad_beta_evidence_rollup.py` 5/5 pass；office/residential/restaurant scene beta benchmark 分别 9/9、8/8、8/8 pass。

### 2026-05-26 Codex 第二轮风险验收补记

- 当轮回归基线：`290 tests OK`；`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings。
- 第二轮加固重点：CAD validation runner 现在会把 `inspect_readback` / `block_alpha_readback` 报告中的 created handles 与上一阶段 `execution_summary.json` / `block_alpha_execution_summary.json` 交叉比对，防止 fake JSON 自带另一套 handles 通过。
- `block_alpha_report.status=geometry_verified` 现在必须包含 `created_handles_scope=pass`、唯一 created handle、`block_reference` 实体 payload，以及 `block_name` / `insertion_point` / `rotation` / `scale` / `layer` / `bbox` 几何字段。
- `insert_block_alpha` 继续加固失败路径：attributes、非法 base point、非受控 identity 在任何 ModelSpace 写入前拒绝；插入后若 handle 缺失或后置校验失败，会尝试删除刚创建的 block reference；同名 `CODEX_TEST_BLOCK_001` 块定义复用前会校验 900x450、4 条线、layer `0`。
- 第二轮真实 CAD 验收：`output/validation_runs/codex-second-gate-block-alpha-cad-final/report.json` 和 `output/validation_runs/codex-second-gate-full-cad-final/report.json` 均为 `status=pass`；block handles 分别为 `99B` 和 `ABC`。
- 第二轮负向 COM 探针通过：非法 `block_id`、非法 `block_name`、attributes、非法 `base_point` 均被拒绝，当前测试 DWG 的 ModelSpace 实体数 `131 -> 131`。

### 2026-05-26 Codex 风险验收补记

- 当轮回归基线：`290 tests OK`；`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings。
- `office_alpha_benchmark.json` 复跑 14/14 pass（non-CAD），证据目录：`output/test_artifacts/benchmarks/codex_review_office_alpha_after_refactor/`。
- `run_cad_validation.py --no-cad --block-alpha-only` 现在包含 `block_alpha_deferred_evidence`，证据目录：`output/validation_runs/codex-review-block-alpha-only-no-cad-after-refactor/`。
- 真实 CAD block alpha 复验通过：`output/validation_runs/codex-review-block-alpha-cad-after-gate/report.json`，created handle `879`，`block_alpha.geometry_verified=true`。
- 完整真实 CAD validation 通过：`output/validation_runs/codex-review-full-cad-after-gate/report.json`，baseline handles `87A..8C4` 与 block handle `99A` 均完成 created-handle readback。
- 负向 COM 探针通过：任意 `block_id` / 任意 `block_name` 被拒绝，当前测试 DWG 的 `CODEX_PREVIEW` 实体数 `111 -> 111`，未新增实体。
- 本轮只证明受控 `CODEX_TEST_BLOCK_001` 样本和当前测试会话下的 validation 链路，不扩大到真实公司块库、属性块、正式图层或任意项目图纸。

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
- 本轮继续收束文档权威关系：`CORE_RESTRUCTURE_PLAN.md` 是唯一 PlanMD / 开发主线；`docs/planning/phase-*.md` 是辅助执行剧本；状态、路线、架构、治理、验证和历史文档只服务主线，不生成第二套待办，也不保留后置 Backlog 副本。
- 最后一轮防偏离收尾已明确：PlanMD 只做文档治理和开发排序，不改变通用 Core Lab、Core 优先、`CAD_PLAN` 中间层、真实 CAD 验证门槛和场景轻量化方向。
- Phase R 新鲜视角评审已启动并落文档：`docs/reviews/fresh-eyes-review-2026-05-25.md` 记录多名只读专家 agent 建议，`docs/planning/phase-r-fresh-perspective-rebirth-plan.md` 作为后续重生式开发校准入口。
- Phase R 已进一步细化为执行开发包：`docs/planning/phase-r-rebirth-implementation-plan.md`、`phase-r-cad-capability-contract.md`、`phase-r-block-library-roadmap.md`、`phase-r-office-benchmark-cases.md`、`docs/governance/multi-agent-contribution.md`、`docs/onboarding/first-handoff.md`。
- Phase R 第一批代码切口已落地：benchmark runner 支持 `evidence_state`、`geometry_accuracy`、`screenshot_role`、`minimums`、`contains_object_types`、`contains_component_roles`、suite/case 配置校验和 `object_spec` pipeline；blank-shell pipeline 已输出每个 CAD_PLAN 的 dry-run / verification 汇总证据；新增 `examples/benchmarks/office_alpha_benchmark.json`，用于验证 desk / chair / cabinet 对象规格、office blank-shell 对象类型和 non-CAD 证据状态。
- Phase R 第二批代码切口已落地：新增 `core/composition_engine/`，支持将卧室床+地毯、餐桌+椅、办公桌+椅+显示器这类角色需求转成组合规格、多 CAD_PLAN、dry-run、unverified verification 和 SVG/PNG 视觉辅助预览；benchmark runner 新增 `composition_spec` pipeline、`contains_object_roles` 断言和 `examples/benchmarks/interior_delivery_benchmark.json`，当前 3 个 persona composition cases 在 non-CAD 下通过。
- Phase R 第三批真实 CAD 校验已落地：新增 `core/execution/batch_plan_runner.py` 与 `scripts/run_composition_cad_check.py`，可将 benchmark 产出的多 CAD_PLAN 按 case 偏移批量写入 AutoCAD，并对本轮 created handles 做逐 plan `geometry_verified` 回读；脚本支持 `--start-x` / `--start-y` / `--spacing-x`，避免为了取干净截图而删除旧预览实体。
- `R-CAD-VIEW-CAPTURE` baseline 已落地：`render_preview.py` 支持 AutoCAD 窗口级截图与 created handles bbox 聚焦；`run_cad_validation.py` 已改为输出 `cad-validation-window.png`，截图继续只作为 `visual_aid_only`，几何准确仍由 created handles 回读决定。
- `R-CAD-CONTRACT` baseline 已落地：新增 `core/verification/evidence_contract.py`，`cad_capability_probe` 与 `readback_report` 现输出 `evidence_state`、`geometry_accuracy`、`screenshot_role`；CAD validation runner 对缺失或错配证据字段做硬门禁。证据：`output\validation_runs\r-cad-contract-no-cad\report.json`、`output\validation_runs\r-cad-contract-cad\report.json`。
- `R-BLOCK-METADATA` baseline 已落地：`libraries/blocks/block_library.example.json` 升级为 `0.2`，含受控 `controlled-test-block-001`（`CODEX_TEST_BLOCK_001`）与 `symbol_fallback` 元数据；新增 `object_spec_to_block_reference()` 与 `validation.status` 过滤。证据：`234 tests OK`、`output\validation_runs\r-block-metadata-no-cad\report.json`、blank-shell benchmark pass。
- `R-BLOCK-PLAN` baseline 已落地：`insert_block_alpha` CAD_PLAN intent 已接入 `validate_plan`、`dry_run_report`、`execute_plan`（fake driver 记录 `insert_block_alpha` 调用）；示例 `examples/plans/insert_block_alpha_test.json`。证据：`239 tests OK`、`output\validation_runs\r-block-plan-no-cad\report.json`。
- `R-BLOCK-CAD-01` 已落地：`AutoCADComDriver.ensure_controlled_block_definition()` 可复用或创建 `CODEX_TEST_BLOCK_001` 块表定义，失败时输出 `definition_missing`。证据：`244 tests OK`（`tests.core.test_autocad_com_driver` 含 5 项受控块定义单测）。
- `R-BLOCK-CAD-02` 已落地：`AutoCADComDriver.insert_block_alpha()` COM 写入路径（`CODEX_PREVIEW`、统一 scale、结构化失败）。证据：`250 tests OK`。
- `R-BLOCK-CAD-03` 已落地：`block_reference` readback 标准化（`inspect_dwg.normalize_com_entity` + `geometry_checks.check_block_reference_readback`）。证据：`255 tests OK`。
- `R-BLOCK-CAD-04` 已落地：CAD validation runner 接入 block alpha no-CAD deferred 步骤与 CAD readback 步骤；`report.block_alpha.geometry_verified` 显式为 false（no-CAD）。证据：`259 tests OK`、`output\validation_runs\r-block-alpha-no-cad-test\report.json`。
- `R-BLOCK-CAD-05` 已落地：真实 AutoCAD 受控块 alpha 验收通过（`--block-alpha-only`）。证据：`output\validation_runs\r-block-alpha-cad\report.json`、`block_alpha_report.json`（`geometry_verified`）、`block_alpha_execution_summary.json`（`created_handles=["878"]`）、`block-alpha-window.png`。仅覆盖受控样本 `insert_block_alpha_test.json`，不扩大到任意块库或项目图纸。
- `R-OFFICE-MICRO-01` 已落地：office alpha 对象级扩展至 7 cases（电脑桌、储物柜柜前净空、文件柜）。证据：`259 tests OK`、`output\test_artifacts\benchmarks\office_object_r1/`（7/7 pass，`benchmark_pass_non_cad`）。
- `R-OFFICE-MICRO-02` 已落地：4 个 office micro-scene composition cases。证据：`output\test_artifacts\benchmarks\office_micro_r2/`（11/11 pass）。
- `R-OFFICE-MICRO-03` 已落地：3 个 blank-shell 场景 cases（长条主通道、障碍避让、会议/电脑混合区）。证据：`output\test_artifacts\benchmarks\office_scene_r1/`（14/14 pass）。
- `R-OFFICE-MICRO-04` 已落地：3 个 failure cases。证据：`output\test_artifacts\benchmarks\office_failure_r4/`（17/17 pass，3× `blocked_expected_non_cad`）。
- `R-OFFICE-MICRO-05` / 父包 `R-OFFICE-MICRO` 已收口：office alpha 17 cases + `benchmark_summary.json` 证据汇总；`docs/verification/office_alpha_benchmark_evidence.md`。
- `R4-01` 已落地：统一 evidence 词表与 `classify_benchmark_pipeline_evidence`。
- `R4-02` 已落地：failure 契约校验、`maximums`、静默 pass guard；office alpha 18 cases。
- `R4-03` 已落地：三组 benchmark `expected_evidence_summary` 机器断言。
- `R4-04` 已落地：CAD validation `evidence_summary` + 顶层 evidence gate。证据：`308 tests OK`、`output/validation_runs/r4-no-cad/`。
- `R4-05` / 父包 **`R4-EVIDENCE-GATES` 已收口**：`docs/verification/evidence_gate_handoff_rules.md`；交接模板扩展。
- `Y-MC-01` 已落地：blank-shell pipeline 输出 `candidate_sets.json`（多 circulation 分支 + zone/placement 候选）。
- `Y-MC-02` 已落地：`design_proposal.comparison_detail`（覆盖率、失败分布、通道连续性、ranking_reasons）。
- `Y-MC-03` 已落地：blank-shell benchmark 多候选硬断言。
- `Y-MC-04` 已落地：blank-shell core **8 cases**（6 pass + 2 blocked）。
- `Y-MC-05` / 父包 **`Y-MULTI-CANDIDATE` 已收口**。
- **父包 `BETA-PROPOSAL` 01–05 收口**：多方案对比 + 用户确认 + 受控 CAD_PLAN bundle。见 `docs/verification/beta_proposal_acceptance.md`。
- **后置 `BETA-DRAWING-READ-01`**：只读 DWG entity summary（层/类型/bbox/handle 统计）。见 `docs/verification/beta_drawing_read_01_boundaries.md`。证据：`404 tests OK`。
- **后置 `BETA-DRAWING-READ-02`**：墙/门洞/柱/禁放区几何候选启发式提取。见 `docs/verification/beta_drawing_read_02_boundaries.md`。证据：`407 tests OK`。
- **后置 `BETA-DRAWING-READ-03`**：shell 候选置信度 / 缺口 / 人工确认点报告。见 `docs/verification/beta_drawing_read_03_boundaries.md`。证据：`410 tests OK`。
- **后置 `BETA-DRAWING-READ-04`**：人工确认回写 `SHELL_MODEL`（shell_loader + schema pass）。见 `docs/verification/beta_drawing_read_04_boundaries.md`。证据：`414 tests OK`。
- **父包 `BETA-DRAWING-READ` 01–05 收口**（`BETA-DRAWING-READ-05`）：读图链路 benchmark + 结构化 blocker。见 `docs/verification/beta_drawing_read_acceptance.md`。证据：`416 tests OK`。
- **后置 `BETA-SCENE-01`**：office scene beta 偏好 + 统一 benchmark（9 cases，7 pass + 2 blocked）。见 `docs/verification/beta_scene_01_boundaries.md`。证据：`418 tests OK`。
- **后置 `BETA-SCENE-02`**：residential beta（卧室/餐厅/收纳 + blank-shell）。见 `docs/verification/beta_scene_02_boundaries.md`。证据：`420 tests OK`。
- **后置 `BETA-SCENE-03`**：restaurant/commercial beta（入口/堂食/后场 + blank-shell）。见 `docs/verification/beta_scene_03_boundaries.md`。下一后置：`BETA-SCENE-04`。证据：`422 tests OK`。
- **后置 `BETA-PROPOSAL-05`**：确认后 `confirmed_cad_plan_bundle`。见 `docs/verification/beta_proposal_05_boundaries.md`。
- **后置 `BETA-PROPOSAL-04`**：局部修改重算 CAD_PLAN。见 `docs/verification/beta_proposal_04_boundaries.md`。
- **后置 `BETA-PROPOSAL-03`**：用户确认 schema + apply。见 `docs/verification/beta_proposal_03_boundaries.md`。
- **后置 `BETA-PROPOSAL-02`**：`proposal_comparison_summary` benchmark。见 `docs/verification/beta_proposal_02_boundaries.md`。
- **后置 `BETA-PROPOSAL-01`**：候选 `score_breakdown` / `ranking_reasons` 固化。见 `docs/verification/beta_proposal_01_boundaries.md`。
- **父包 `BETA-PROJECT-SAMPLE` 01–05 收口**：脱敏样本协议 → workflow → benchmark → 可选 CAD readback。见 `docs/verification/beta_project_sample_acceptance.md`。
- **后置 `BETA-PROJECT-SAMPLE-05`**：样本 CAD check（`project_sample_cad_check_report.json`）。见 `docs/verification/beta_project_sample_05_boundaries.md`。
- **后置 `BETA-PROJECT-SAMPLE-04`**：样本 benchmark（pass + blocked）；`project_sample_benchmark.json`。见 `docs/verification/beta_project_sample_04_boundaries.md`。
- **后置 `BETA-PROJECT-SAMPLE-03`**：样本 workflow → CAD_PLAN / dry-run / unverified report。见 `docs/verification/beta_project_sample_03_boundaries.md`。
- **后置 `BETA-PROJECT-SAMPLE-02`**：样本 shell / project model fixture + loader。见 `docs/verification/beta_project_sample_02_boundaries.md`。
- **后置 `BETA-PROJECT-SAMPLE-01`**：脱敏样本目录协议 + manifest 扫描。见 `docs/verification/beta_project_sample_01_boundaries.md`。
- **父包 `BETA-CAD-BLOCK` 已收口（01–05）**：见 `docs/verification/beta_cad_block_acceptance.md`。
- **后置 `BETA-CAD-BLOCK-04`**：`drawing_standard_profile`（`codex_preview_beta`）。见 `docs/verification/beta_cad_block_04_boundaries.md`。
- **后置 `BETA-CAD-BLOCK-03`**：capability probe entity-level evidence（polyline / layer mapping / hatch deferred）。见 `docs/verification/beta_cad_block_03_boundaries.md`。
- **后置 `BETA-CAD-BLOCK-02`**：属性块 / tag readback 探针（deferred 与不误报）。见 `docs/verification/beta_cad_block_02_boundaries.md`。
- **后置 `BETA-CAD-BLOCK-01`**：受控 block transform beta suite（non-CAD）。
- **父包 `X-SCENE-ALPHA` 已收口（01–05）**：三场景 preferences + benchmark + 边界扫描 + 解释模板 + 总验收。见 `docs/verification/scene_alpha_acceptance.md`。可声称 non-CAD 多场景复用 Core pipeline；不可声称真实 CAD 几何或 Scene Agent 产品完成。
- `X-SCENE-04`：场景解释模板（`build_scene_explanation`、三场景 `rules.md`）。
- `X-SCENE-03`：Scene Agent 静态边界扫描（`scene_boundary_scan`）。
- `X-SCENE-02`：三场景 `scene_alpha_benchmark.json`（3/3 non-CAD pass）；动线权重进入 pipeline 选型。
- `X-SCENE-01`：Scene Alpha preferences 契约（对象优先、通道宽度、动线权重）。见 `docs/verification/scene_alpha_preferences_contract.md`。

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
unittest discover -s tests: 452 tests OK
run_repo_audit.py --max-python-lines 500 --fail-on-findings: 0 findings
Python AST parse: 248 files checked, 0 errors
JSON parse: 166 files checked, 0 errors
focused 4-7 package tests: 46 tests OK
run_cad_validation.py --no-cad: output\validation_runs\codex-polish-final-no-cad status pass
self_check.py: pass
render_preview.py --check: ready（AutoCAD window 当前环境 unavailable；截图仍为 visual_aid_only）
run_project_sample_protocol_scan.py: pass, 2 samples
run_project_sample_benchmark.py: pass, 2/2 cases
run_proposal_confirmed_benchmark.py: pass, 2/2 cases
run_cad_beta_evidence_rollup.py: pass, 5/5 subpackages
run_office_scene_beta_benchmark.py --output-root: pass, 9/9 cases
run_residential_scene_beta_benchmark.py --output-root: pass, 8/8 cases
run_restaurant_scene_beta_benchmark.py --output-root: pass, 8/8 cases
run_benchmark_suite.py blank_shell_core_benchmark.json: output\test_artifacts\benchmarks\codex_polish_blank_shell 8/8 pass
run_benchmark_suite.py office_alpha_benchmark.json: output\test_artifacts\benchmarks\codex_polish_office_alpha 18/18 pass
run_benchmark_suite.py interior_delivery_benchmark.json: output\test_artifacts\benchmarks\codex_polish_interior_delivery 3/3 pass
focused 1-3 package tests: 48 tests OK
run_benchmark_suite.py blank_shell_core_benchmark.json: output\test_artifacts\benchmarks\codex_maintenance_fix_blank_shell 8/8 pass
run_benchmark_suite.py office_alpha_benchmark.json: output\test_artifacts\benchmarks\codex_maintenance_fix_office_alpha 18/18 pass
run_benchmark_suite.py interior_delivery_benchmark.json: output\test_artifacts\benchmarks\codex_maintenance_fix_interior_delivery 3/3 pass
run_project_sample_cad_check.py --no-cad --require-cad-verified: expected exit 1, report deferred at output\validation_runs\codex-maintenance-project-sample-strict-no-cad
run_cad_validation.py --no-cad: output\validation_runs\codex-maintenance-fix-no-cad status pass
run_cad_validation.py --no-cad: output\validation_runs\manual-no-cad-after-composition-cad status pass
run_cad_capability_probe.py: output\validation_runs\manual-primitive-cad-probe status cad_capability_verified
run_cad_validation.py: output\validation_runs\manual-cad-after-primitive-probe status pass
focused R-CAD-VIEW tests: tests.core.test_render_preview + tests.core.test_cad_validation_runner, 11 tests OK
run_cad_validation.py --no-cad: output\validation_runs\r-cad-view-no-cad status pass
run_cad_validation.py: output\validation_runs\r-cad-view-cad status pass
run_cad_validation.py --no-cad: output\validation_runs\r-cad-contract-no-cad status pass
run_cad_validation.py: output\validation_runs\r-cad-contract-cad status pass
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
总进度：约 95%（Core 底座开发 99% × 70% + Agent 多场景实现 85% × 30%）
Core 底座开发进度：约 99%
Agent 多场景实现进度：约 85%
```

解释：Core 底座已具备 schema / dry-run / verification / evidence gate / benchmark runner / CAD validation runner / 项目样例协议 / 读图候选 / proposal confirmed / scene beta non-CAD 验收等主链路，并完成本轮全量安全复盘、维护性拆分、路径安全公共化和 schema registry 收口。Agent 多场景已经覆盖 office、residential、restaurant 的 scene beta benchmark，但多数仍是 non-CAD 证据；不能把 benchmark pass 扩大为真实项目 DWG、正式图层、公司块库或任意 CAD_PLAN 的几何准确。

## 当前最重要缺口

| 缺口 | 影响 | 归属主线 |
| --- | --- | --- |
| 真实项目 DWG / 公司块库 / 正式图层尚未全量补验 | 当前证据不能扩大为任意项目几何准确 | 后续真实项目验收 |
| ActiveDocument guard 仍未落硬门禁 | 合法 preview plan 仍会写入当前激活 DWG 的 `CODEX_PREVIEW` 图层，需防误保存污染 | CAD 安全加固 |
| scene beta 多数仍是 non-CAD benchmark | office / residential / restaurant 通过不等于真实 CAD 落图 verified | Scene Beta / CAD 扩展 |
| 自动读图候选仍依赖人工确认 | 读图链路能产出候选和 blocker，但不能替代人工确认 `SHELL_MODEL` | Drawing Read |
| 截图能力仍是视觉辅助 | `render_preview.py --check` ready 不代表几何准确，准确性仍需 created-handle readback | Phase W / CAD 验证 |

## 计划入口

后续优先级、Phase 顺序、待办和退出标准只以唯一 `PlanMD`：`CORE_RESTRUCTURE_PLAN.md` 为准。本文只维护当前进展、最近验证、风险边界和状态快照。

2026-05-26 的九个 Phase R/X/Y 相关开发包与 25 个二级小包已经按历史记录和交接包收口，其中 `R-CAD-VIEW-CAPTURE` 的真实 CAD 证据为 `output\validation_runs\r-cad-view-cad\cad-validation-window.png`。这些记录现在只是历史快照；后续执行顺序、后置 Backlog 和新的维护包边界只在唯一 `PlanMD` 中维护。

同日登记的五大后置主线 Backlog（真实 CAD 能力扩展、真实项目样本闭环、多方案设计与交互确认、自动读图 / 空壳识别、场景 Agent Beta）仍只作为 PlanMD 中的未来路线，不在本文复制小包表，也不提升本页进度百分比。

## 后续恢复开发时怎么问

```text
读取本仓库 AGENTS.md 和 CORE_CONTEXT_BRIEF.md，告诉我 CAD Agent 当前开发状态和下一步建议。
```

若要执行主计划：

```text
读取 CORE_RESTRUCTURE_PLAN.md。若执行当前已登记开发包，再按目标阶段打开 docs/planning/phase-*.md；若查看后置 Backlog，只看 CORE_RESTRUCTURE_PLAN.md。
```
