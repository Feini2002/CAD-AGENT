# CAD Agent 变更记录

本文现在只保留高频变更摘要。压缩前完整流水已归档到 `docs/history/root-md-full-snapshot-2026-05-26/CAD_AGENT_CHANGELOG.md`；需要追溯逐包细节时读归档，不把旧完成记录重新复制回根目录。

## 2026-05-27

### 任务清单精细化拆包（§4.1 + §5 RCAD）

- `docs/planning/任务清单.md`：§4.1 展开 `LCAD-10.1`~`10.5`、`LCAD-11.1`~`11.5`、`CAD-VAL-01/02`、`LCAD-12`~`14` 共 **15** 行；§5 **RCAD-00~28** 逐项命令与 `cad_status`；§4.2 积压标明 25 包占位。
- §0 三指令分母更新：能力证明 43、代码轨 49、CAD 补验 29。

### 任务清单重命名 + 三指令执行进度

- `docs/planning/一键推进.md` 重命名为 **`docs/planning/任务清单.md`**（含 §3 能力证明 / §4 代码 / §5 CAD 补验）。
- §0 新增 **三指令执行进度** 表（能力证明约 5%、一键推进约 20%、CAD 补验约 50%）；完成包后由 Agent 更新。
- `AGENTS.md` 交付格式固定 **表 A 工程节奏 + 表 B 三指令进度 + 表 C 能力口径**。

## 2026-05-26

### 路线 F：能力证明体系登记 + 任务清单板块拆分

- 新增 `docs/planning/capability-proof-architecture.md`（P0~P3、Ladder、claim_level、三进度口径）。
- 重写 `docs/planning/一键推进.md`：§3 **V-PROOF**（V0~V7 共 37+ 任务包）、§4 代码轨、§5 RCAD；RCAD 明确为 P1 执行层且须回写 registry。
- `CORE_RESTRUCTURE_PLAN.md` 新增 **路线 F**、Capability proof gate；后置 Backlog 四列（证明/代码/CAD）。
- 同步 `CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`AGENTS.md`、`CAD_AGENT_RULES.md` 三口径；禁止用 96% 代替 CAD 证明覆盖率。
- 能力证明 next：`V-PROOF-00-REGISTRY-SCHEMA`。

### CAD 补验会话 rcad补验-20260526

- RCAD-00/03/02/17/13：AutoCAD 2026 Drawing1；strict 矩阵几何 8 case、94 handles（顶层 fail 仅 baseline 非几何 M-01）。
- 工装 smoke：`rcad补验-20260526-cfit-smoke`，12 handles，3/3 `geometry_verified`。
- 椅符号：`rcad补验-20260526-symbol-chair`，6 handles。
- 汇总：`output/validation_runs/rcad补验-20260526/rcad_verify_summary.json`；`product_alpha_boundary.json` 移除过时 deferred 措辞。

### 一键推进版式优化

- 重写 `docs/planning/一键推进.md`：§0 上手、§2 活跃代码轨 + 积压索引、§3 RCAD 分组与 manifest 对照；去掉 55 行重复编号表。

### 路线 E：真实 CAD 校验（CAD-MCP）并入主计划

- `CORE_RESTRUCTURE_PLAN.md` 新增 **路线 E**：CAD-MCP 协议、父包索引、已验证 vs 待补验总表。
- `docs/planning/一键推进.md` 拆 **§3B RCAD-00~28**：逐步命令、输出目录、`cad_status`（verified/stale/pending/blocked）；§3A 中 CAD 项交叉引用 RCAD。
- 触发词：「CAD 补验」→ §3B 首项 `pending`（须先 `RCAD-00`）。

### 一键推进全量拆包

- §3A 代码轨（P0~P5）+ §3B CAD-MCP 轨；`next`（代码）=`LCAD-10.1-NEG-FIXTURES`。

### 文档全量对齐（休整 MD）

- 同步进度 86%/96%/52%；`LCAD-09` done；证据索引保留。

### 用户会话：全量 deferred CAD 补验

- 在 AutoCAD 已打开条件下跑 `user-cad-full-verify-20260526`：manifest strict 7/7 几何 case verified（94 handles）；primitive matrix / fixture suite / composition / complex smoke / project rollup / symbol glyph / block alpha 均通过 readback。
- 修复 `run_primitive_matrix.py`、`run_cad_plan_fixture_suite.py` 的 `resolve_under_project_output` 参数顺序。
- 全量 `run_cad_validation` 仍 fail（Pillow/截图/unit_tests 门禁，非几何 readback）。
- 汇总：`output/validation_runs/user-cad-full-verify-20260526/user_cad_full_verify_summary.json`

### LCAD-08 Project sample CAD rollup

- 新增 `project_sample_cad_rollup.json` + `run_project_sample_cad_rollup.py`：串联 `sample_blank_shell` 与 `commercial_fitout_sample`。
- 真实 CAD：`output/validation_runs/project-sample-cad-rollup-real`，2/2 `geometry_verified`，`created_handle_count` 20 + 12。
- `tests.core.test_project_sample_cad_rollup` 3 tests OK。
- 下一包：`LCAD-10-NEGATIVE-SAFETY`（composition 已在同会话 verified，LCAD-09 收口）。

### LCAD-09 Scene composition CAD

- 用户会话 manifest strict：`composition_cad` 3/3 cases `geometry_verified`；40 handles。
- 不扩大为 Scene Product；证据在 `user-cad-full-verify-20260526/manifest-strict-rerun/composition_cad/`。

### LCAD-07 Block / attribute / hatch boundary

- 新增 `examples/cad_regression/cad_block_attribute_hatch_boundary.json`：block/attribute verified、hatch structured deferred。
- 新增 `core/verification/cad_block_attribute_hatch_boundary.py` + schema + `docs/verification/cad_block_attribute_hatch_boundaries.md`。
- `tests.core.test_cad_block_attribute_hatch_boundary` + `test_block_attribute_probe` 12 tests OK。
- 下一包：`LCAD-08-PROJECT-SAMPLE-CAD`。

### C-CFIT-07 Product boundary rollup

- 新增 `agents/commercial_fitout/capabilities/product_alpha_boundary.json`：可声明能力、不可声明、下一阶段差距、状态页同步口径。
- 新增 `core/agents/commercial_fitout_product_boundary.py` + schema；`subscenes.json` / `preferences.json` → `product_boundary`。
- 重写 `docs/verification/commercial_fitout_product_alpha_boundaries.md` 为 C 路线汇总页。
- `tests.agents.test_commercial_fitout_product_boundary` 5 tests OK。**C 路线工装 Scene Product Alpha 收口。**
- 下一包：`A-LCAD-07-TO-11-HARDENING-TAIL`。

### C-CFIT-06 Real CAD smoke

- 新增 `core/agents/commercial_fitout_cad_smoke.py`、`scripts/run_commercial_fitout_cad_smoke.py`：确认后 `cad_plan_items` → `execute_plan_batch` → created handles readback。
- 报告含 `product_claim_boundary`（不声明完整工装 Scene Product）。
- `tests.agents.test_commercial_fitout_cad_smoke` 3 tests OK（FakeCadDriver `geometry_verified`）。
- 本机无活动 AutoCAD 时 CLI 返回 deferred；真实 CAD 须用户打开 CAD 后补跑。
- 下一包：`C-CFIT-07-PRODUCT-BOUNDARY-ROLLUP`。

### C-CFIT-05 Sample project confirmation

- 新增脱敏项目样本 `projects/commercial_fitout_sample/`（`needs_confirmation: true` brief + 手工 `SHELL_MODEL`）。
- `blank_shell_pipeline` 在仅因确认阻塞时返回 `confirmation_pending` 并写出 proposal 上游产物（无 `cad_plan`）。
- 新增 `core/agents/commercial_fitout_sample_confirmation.py`、`commercial_fitout_sample_confirmation_bundle.schema.json`、`scripts/run_commercial_fitout_sample_confirmation.py`。
- 修复 `partial_replan`：先写 `cad_plan_items` 再生成 verification report（支持确认后首次落盘）。
- `tests.agents.test_commercial_fitout_sample_confirmation` 4 tests OK。
- 下一包：`C-CFIT-06-REAL-CAD-SMOKE`。

### C-CFIT-04 Micro-scene benchmark

- 新增 7 个 `fitout_*` composition 模板 + `commercial_fitout_layout_failure.py`（入口 / 柜前净空 / 主通道 / 会议座位失败分类）。
- 新增 `examples/benchmarks/commercial_fitout_micro_scene_benchmark.json`（4 pass + 4 `blocked_expected_non_cad`）。
- 新增 `scripts/run_commercial_fitout_micro_scene_benchmark.py`；`runner` 对 fitout composition 使用 fitout failure 评估。
- `tests.core.test_commercial_fitout_layout_failure` + `tests.agents.test_commercial_fitout_micro_scene_benchmark` 6 tests OK。
- 下一包：`C-CFIT-05-SAMPLE-PROJECT-CONFIRMATION`。

### C-CFIT-03 Block mapping

- 新增 `agents/commercial_fitout/capabilities/block_mapping.json`、`libraries/blocks/commercial_fitout_block_library.json`（10 个 `FITOUT_*` 受控块）。
- 新增 `core/agents/commercial_fitout_block_mapping.py`：`resolve_catalog_object_render`、`assert_block_name_allowed`；`allow_arbitrary_block_names=false`。
- 找得到 mapping 块走 block metadata；否则回退 `OBJECT_SPEC`；工位组 bundle 支持 member_mappings。
- `tests.agents.test_commercial_fitout_block_mapping` 7 tests OK。
- 下一包：`C-CFIT-04-MICRO-SCENE-BENCHMARK`。

### C-CFIT-02 Object catalog

- 新增 `agents/commercial_fitout/capabilities/object_catalog.json`（14 项，覆盖三子场景 typical_objects）。
- 新增 `core/agents/commercial_fitout_catalog.py`：`catalog_entry_to_object_specs`、`object_specs_for_subscene`。
- 工位组 `workstation_cluster` 展开为 desk + chair；open_office 样本可喂 `create_layout_candidates`。
- `tests.agents.test_commercial_fitout_catalog` 5 tests OK。
- 下一包：`C-CFIT-03-BLOCK-MAPPING`。

### C-CFIT-01 Scope and subscenes

- 新增 `agents/commercial_fitout/SCOPE.md`、`subscenes.json`（`open_office` / `meeting_room` / `reception`）。
- 新增 `core/schemas/commercial_fitout_scope.schema.json`、`core/agents/commercial_fitout_scope.py`。
- 书面承诺不提供 `full_construction_documents`；零售 legacy workflow 标记 `deferred_legacy_workflows`。
- `scene_registry` 增加 `scope_path`；`tests.agents.test_commercial_fitout_scope` 5 tests OK。
- 下一包：`C-CFIT-02-OBJECT-CATALOG`。

### B-ORCH-05 Route audit report

- 新增 `core/orchestrator/route_audit_report.py`、`core/schemas/route_audit_report.schema.json`、`examples/orchestrator/sample_route_audit_report.json`。
- `orchestrate_request` 附带 `route_audit_report`；有 `output_dir` 时写入 `route_audit_report.json`。
- 证据分层：`available` / `deferred` / `not_claimable`；`allow_cad` 且无 readback 时标记 `readback_geometry_verified` deferred。
- `tests.core.test_route_audit_report` 4 tests OK；与 `test_workflow_dispatch` 共 11 tests OK。
- B 路线 `B-ORCH-01`~`05` 已全部收口；下一包：`C-CFIT-01-SCOPE-AND-SUBSCENES`。

### B-ORCH-04 Workflow dispatch

- 新增 `core/orchestrator/workflow_dispatch.py`、`examples/orchestrator/workflow_routes.json`。
- `orchestrate_request` 串联 gate + 场景激活 + 路由分派；`execute_workflow_dispatch` 动态调用既有 Core entrypoint（不复制 runner 逻辑）。
- non-CAD：`proposal_non_cad_loop` 跑通 `run_non_cad_pipeline`；draw：`object_symbol_glyph` 跑通 symbol resolve + dry-run。
- `tests.core.test_workflow_dispatch` 7 tests OK。
- 下一包：`B-ORCH-05-ROUTE-AUDIT-REPORT`。

### B-ORCH-03 Activation policy

- 新增 `core/orchestrator/activation_policy.py`：`evaluate_scene_activation`、`merge_activation_into_request_gate`。
- 优先级：manifest `scene_id` → `scene_hint` → 触发词匹配；无匹配默认 `no_scene`；多匹配 `needs_clarification`。
- 场景模块禁止 `may_bypass_core`；必须走 Core workflow。
- `tests.core.test_activation_policy` 7 tests OK。
- 下一包：`B-ORCH-04-WORKFLOW-DISPATCH`。

### B-ORCH-02 Scene registry

- 新增 `core/orchestrator/scene_registry.py`、`scene_registry.schema.json`、`examples/orchestrator/scene_registry.json`。
- 登记 `no_scene`、`office`、`residential`、`restaurant`、`commercial_fitout`、`exhibition`、`custom`；含成熟度、触发词、能力、禁用条件；禁止 `auto_activate` / `may_bypass_core`。
- `tests.core.test_scene_registry` 7 tests OK。
- 下一包：`B-ORCH-03-ACTIVATION-POLICY`。

### B-ORCH-01 Request context

- 新增 `core/orchestrator/request_context.py`、`request_context.schema.json`。
- `build_request_context` / `evaluate_request_gate`：记录用户意图、可用输入、CAD 策略、澄清状态；缺输入时 `blocked`，不直接落图。
- 示例：`examples/orchestrator/draw_desk_request_context.json`；`tests.core.test_request_context` 6 tests OK。
- 下一包：`B-ORCH-02-SCENE-REGISTRY`。

### D-SYMBOL-07 Block fallback policy

- 新增 `core/symbol_engine/fallback_policy.py`：`resolve_symbol_render_resolution`、`assess_render_tiers`、`detect_silent_degradation`。
- 优先级：受控 `cad_insertion_verified` block → `draw_symbol_glyph` → component preview → bbox placeholder → deferred。
- 每级输出 `evidence_state`；`silent_degradation` 标记跳过可用 symbol 的静默退化。
- `examples/benchmarks/symbol_fallback_policy_benchmark.json`；`tests.core.test_symbol_fallback_policy` 6 tests OK。
- 下一包：`B-ORCH-01-REQUEST-CONTEXT`。

### D-SYMBOL-06 CAD readback smoke

- `core/execution/execute_plan.py` 支持 `draw_symbol_glyph`（rectangle/line/circle/arc/polyline → `CODEX_PREVIEW`）。
- 新增 `core/execution/symbol_glyph_execute.py`、`core/verification/symbol_glyph_cad_smoke.py`、`scripts/run_symbol_glyph_cad_smoke.py`。
- 代表样本 `examples/symbol_specs/surface_desk_plan.json`：readback 期望 `line:9`、`circle:1`；报告含 `symbol_readability_report`。
- `tests.core.test_symbol_glyph_cad_smoke` 5 tests OK。
- 下一包：`D-SYMBOL-07-BLOCK-FALLBACK-POLICY`。

### D-SYMBOL-05 Readability gate

- 新增 `core/symbol_engine/readability.py`：`build_symbol_readability_report`、`evaluate_object_spec_readability`。
- 可读性状态：`symbol_readable`、`visual_review_required`、`fallback_component_preview`、`fallback_bbox_placeholder`、`deferred_unsupported_symbol`。
- 检查项覆盖非单 bbox、archetype grammar、最小尺寸、朝向 cue、无文字/尺寸依赖；`tests.core.test_symbol_readability` 6 tests。
- 下一包：`D-SYMBOL-06-CAD-READBACK-SMOKE`。

### D-SYMBOL-04 Object to symbol

- 新增 `core/symbol_engine/object_to_symbol.py`：`OBJECT_TYPE_TO_ARCHETYPE`、`object_spec_to_symbol_spec`、`ObjectToSymbolResult`。
- table / desk / chair / sofa / bed / cabinet 映射为可读 `SYMBOL_SPEC`；`counter` / `elevation_preview` 返回显式 fallback。
- 新增 object_spec 示例 table/chair/bed；`tests.core.test_object_to_symbol` 5 tests。
- 下一包：`D-SYMBOL-05-READABILITY-GATE`。

### D-SYMBOL-03 Archetype grammar

- 新增 `core/symbol_engine/archetypes.py`：`ARCHETYPE_GRAMMARS`、必备部件组、相对位置约束；并入 `validate_symbol_spec`。
- 新增 5 个 archetype 示例（seating / sleeping / storage / display / workstation）；primitive 支持 `seat_split` / `drawer_line` / `door_swing`。
- `tests.core.test_symbol_archetypes` 6 tests；symbol 合计 18 tests OK（no-CAD）。
- 下一包：`D-SYMBOL-04-OBJECT-TO-SYMBOL`。

### D-SYMBOL-02 Primitives

- 新增 `core/symbol_engine/primitives.py` 与 `core/plan_engine/symbol_glyph_plan.py`；CAD_PLAN 新 intent `draw_symbol_glyph`。
- 支持 outline / inner_offset / thick_band / split_line / leg_marker / arc_marker / orientation_marker → validate + dry-run。
- `tests.core.test_symbol_primitives` 5 tests；symbol 合计 12 tests OK（no-CAD）。
- 下一包：`D-SYMBOL-03-ARCHETYPE-GRAMMAR`。

### D-SYMBOL-01 Spec schema

- 新增 `symbol_spec.schema.json`、`symbol_graph.schema.json`；示例 `examples/symbol_specs/surface_desk_plan.json`、`examples/symbol_graphs/single_desk_placement.json`。
- 新增 `core/symbol_engine/symbol_spec.py`：`validate_symbol_spec` / `validate_symbol_graph` 与反静默 bbox 语义门禁。
- registry + invalid fixture + `tests.core.test_symbol_spec`；17 tests OK（no-CAD）。
- 下一包：`D-SYMBOL-02-PRIMITIVES`。

### A-LCAD-04-TO-06 Smoke and plan matrix

- 新增 `core/verification/primitive_matrix.py`、`cad_plan_fixture_suite.py`；脚本 `run_primitive_matrix.py`、`run_cad_plan_fixture_suite.py`。
- 新增 3 个 regression `CAD_PLAN` fixture 与 `cad_plan_fixture_manifest.json`；`local_cad_regression_manifest.json` 增至 7 case。
- `FakeCadDriver.insert_block_alpha` 支持 block fixture fake 执行；`local_cad_regression` 已接线新 case。
- focused 单测 23 tests OK（no-CAD / fake-driver）；本会话未跑真实 CAD `geometry_verified`。
- 下一包：`D-SYMBOL-01-SPEC-SCHEMA`。

### A-LCAD-03.4 Created-handle scope

- 新增 `core/verification/created_handle_scope.py`：`input_handle_count` / `hit_count` / `miss_count` / `extra_entity_count`。
- `build_verification_report`、`cad_capability_probe`、`complex_cad_smoke` 与 `evidence_contract` 已接入；`LCAD-03` 收口。
- 下一包：`A-LCAD-04-TO-06-SMOKE-AND-PLAN-MATRIX`。

### A-LCAD-03.3 No-save / no-delete guard

- 新增 `core/safety/write_guard.py`：`CadWriteGuard` 拦截正式图层写入、保存、覆盖、删除；`run_negative_write_guard_checks` 供 capability probe 调用。
- `AutoCADComDriver`、`FakeCadDriver` 已接入；`cad_capability_probe` 增加 `write_guard` 报告与 `write_guard_negative` check。
- 下一包：`A-LCAD-03.4-CREATED-HANDLE-SCOPE`。

### A-LCAD-03.2 Preview-only audit

- 新增 `core/verification/preview_only_audit.py`：统一 `layer` / `saved_dwg` / `deleted_entities` / `modified_formal_layers` 审计字段与 `execution_summary` 门禁。
- `execute_plan`、`cad_capability_probe`、`complex_cad_smoke`、`cad_validation_runner` 已接入；focused 单测通过。
- 下一包：`A-LCAD-03.3-NO-SAVE-NO-DELETE-GUARD`。

### A-LCAD-03.1 ActiveDocument snapshot

- 新增 `core/verification/cad_session_guard.py`：连接前 blocked、连接后/写入后 snapshot、文档指纹、preview 层实体计数、modelspace 摘要、多文档不确定时 `blocked`。
- `cad_capability_probe` 现输出 `active_document_guard` 与 `active_document_snapshot.json`；fake-driver 单测 9 tests OK。
- 下一包：`A-LCAD-03.2-PREVIEW-ONLY-AUDIT`。

### 一键推进台账

- 将旧台账重命名为 `docs/planning/一键推进.md`。
- 台账只保留未完成 plan、已开发但未完全校验内容和待开发任务包；已完成且校验结束的包不再放入。
- 台账改成极简顺序步骤：用户说“一键推进”时，默认读取该文档并推进“当前推进队列”的第一个未完成最小包。
- 当前推进队列包含 25 个细分执行包，顶层未完成包为 10 个。
- `docs/README.md`、`docs/planning/README.md`、`CORE_CONTEXT_BRIEF.md`、`CAD_AGENT_STATUS.md` 已补入口引用。

### 主计划系统优化路线拆分

- 按用户要求在唯一 `PlanMD` / `CORE_RESTRUCTURE_PLAN.md` 中新增“系统优化路线拆分”。
- A 路线：CAD 安全与证据链，围绕 ActiveDocument snapshot、preview-only audit、no-save/no-delete guard、created handles scope 和 LCAD 扩样尾段拆分。
- B 路线：`Core Orchestrator` + `Scene Router`，围绕 request context、scene registry、activation policy、workflow dispatch 和 route audit report 拆分。
- C 路线：`commercial_fitout` Scene Product Alpha，围绕子场景范围、对象体系、block metadata、微场景 benchmark、样本确认流、真实 CAD smoke 和产品边界 rollup 拆分。
- D 路线：`SYMBOL-CORE` CAD 符号语法与家具图库底座，围绕 `SYMBOL_SPEC`、symbol primitives、archetype grammar、readability gate、glyph CAD readback 和 block fallback policy 拆分。
- 当前默认执行顺序仍建议 A -> B -> C，D 可在对象 / 家具图库需求明确时优先；下一安全包保持 `LCAD-03-ACTIVE-DOCUMENT-GUARD`。

### 需求侧多角色 Agent benchmark

- 新增 `agents/demand_side/role_agents.json`，用 12 个需求侧角色覆盖 residential、office、restaurant、commercial_fitout、exhibition、custom 六个场景。
- 新增 `core/demand_agents/`，负责加载、校验角色和 demand case，拒绝未知 `demand_agent_id`。
- `core/benchmarks/runner.py` 新增 `demand_case` pipeline，可把需求记录分派到现有 `object_spec` / `object_detail_spec` / `composition_spec` / `blank_shell` pipeline，并保留 `scene_id`、`request_text`、`core_capability_targets` 等元数据。
- 新增 `examples/benchmarks/demand_side_agent_benchmark.json` 和 `tests/core/test_demand_agents.py`，第一批 10 个需求 case 为 non-CAD benchmark，不能替代真实 CAD readback；该层按用户澄清定位为开发期脚手架，后续能力沉淀后可清理角色表。

### 对象组件级 CAD_PLAN 展开

- 新增 `core/object_engine/detail_plan.py`，可把 table、bed、chair、sofa、desk 展开为组件级安全预览 `CAD_PLAN`。
- `core/benchmarks/runner.py` 新增 `object_detail_spec` pipeline，输出多份 component-level CAD_PLAN、dry-run 汇总和 verification report 汇总。
- `demand_side_agent_benchmark` 中“比较精细的餐桌”和“办公椅”需求已切到 `object_detail_spec`，餐桌输出桌面 + 四个支撑，办公椅输出座面、靠背和四个支撑。
- 真实 CAD 校验：`output\validation_runs\demand-side-agent-cad-real-20260526`，10/10 demand cases `geometry_verified`，`created_handle_count=100`；视觉辅助截图为 `demand-side-agent-cad-window-focused.png`。

### 默认出图无文字 / 尺寸标注

- 用户明确要求后，后续面向用户生产的 CAD 输出默认不加中文文字标注、不加英文文字标注，也默认不加尺寸标注。
- 保留文字和尺寸能力：`include_label`、`include_dimensions`、`draw_text`、`add_dimension` 仍可在明确需求或能力测试中显式启用。
- 已把对象转 `CAD_PLAN`、参数化对象转 `CAD_PLAN` 和组合模板默认值改为无文字 / 无尺寸标注，并补充默认关闭与显式开启的回归测试。

### 根目录 MD 精度压缩

- 按用户要求降低古老 plan 和完成流水在默认上下文中的权重。
- 压缩 `CORE_CONTEXT_BRIEF.md`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md`、`CAD_AGENT_ISSUES.md`。
- 压缩前完整快照保留在 `docs/history/root-md-full-snapshot-2026-05-26/`。
- 本次只做文档上下文治理，不改变开发跟进规则、CAD 验证门槛或唯一 PlanMD 主从关系。

### complex CAD smoke 与 full strict regression

- 新增 `core/verification/complex_cad_smoke.py` 与 `scripts/run_complex_cad_smoke.py`。
- 覆盖外框、网格线、斜线、开放多段线、圆、弧、文字和标注。
- 真实 CAD 单项证据：`output\validation_runs\complex-cad-smoke-real-final`，`status=geometry_verified`，`created_handle_count=23`。
- 默认 regression manifest 已加入 `complex_cad_smoke`。
- 最新 full strict matrix：`output\validation_runs\complex-cad-regression-strict-final`，`selected_case_count=4`，`geometry_verified_case_count=7`，`created_handle_count=113`。

### LCAD-02 strict matrix runner

- `scripts/run_local_cad_regression.py` 支持 `--case` selected case、默认 all case、`--strict` 严格别名。
- summary 输出 `manifest_case_count`、`selected_case_count`、`selected_case_ids`、`strict`。
- selected no-CAD 证据：`output\validation_runs\lcad-02-selected-project-sample-no-cad`。
- strict all CAD 证据：`output\validation_runs\lcad-02-strict-all-cad`。

### LCAD-01 regression manifest

- 新增 `core/schemas/cad_regression_manifest.schema.json`、默认 manifest 示例和 manifest loader 校验。
- local CAD regression report 顶层输出 manifest metadata。
- no-CAD 证据：`output\validation_runs\lcad-01-manifest-no-cad`。
- 受控真实 CAD strict smoke：`output\validation_runs\lcad-01-manifest-cad-smoke`。

### Core / Scene 边界重校准

- 新增 `docs/architecture/core-scene-agent-boundaries.md`。
- 统一 `Core 底座`、`Scene Alpha 壳层`、`Scene Beta 能力包`、`Scene Product 场景产品` 四级成熟度。
- 明确 office / residential / restaurant 的 preferences、rules、non-CAD benchmark 不能写成具体场景产品完成。
- 场景能力未来按 `Core Orchestrator -> Scene Router -> Scene Registry -> Scene Capability Module -> Core workflow` 调用；默认无场景时必须 `no_scene`。

### 本地真实 CAD 校验扩样主线

- 在唯一 `PlanMD` 中登记 `LCAD-01` 到 `LCAD-11`。
- 当前已完成 `LCAD-01`、`LCAD-02` 和 complex smoke 前置加固。
- 下一默认安全包为 `LCAD-03-ACTIVE-DOCUMENT-GUARD`。

### 维护加固摘要

- 本地 CAD 回归矩阵入口已建立：`core/verification/local_cad_regression.py`、`scripts/run_local_cad_regression.py`。
- 活跃排障手册中的 CAD-MCP Python 路径已改为 `$env:USERPROFILE` 派生。
- scene beta wrapper 已兼容 `--output-root`。
- `core/path_safety.py` 已公共化 output root、project root、safe path segment 等边界校验。
- `core/schemas/*.schema.json` 已纳入 registry 和 invalid fixture 覆盖。
- `run_project_sample_cad_check.py --require-cad-verified` 已防止 no-CAD deferred 被误判为真实 CAD verified。

## 旧记录索引

| 范围 | 位置 |
| --- | --- |
| 2026-05-24 到压缩前的完整 changelog | `docs/history/root-md-full-snapshot-2026-05-26/CAD_AGENT_CHANGELOG.md` |
| 主平台 Markdown 拆分历史 | `docs/history/core-platform-md-split-plan-2026-05-25.md` |
| 早期空壳布局时间估算 | `docs/history/shell-layout-time-estimate.md` |

## 记录规则

- 根 changelog 只写最近高频摘要和索引。
- 每个新开发包仍要登记变更，但控制在“目标、关键文件、证据、边界”四项内。
- 长篇逐步执行细节放入 `docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` 或 `docs/history/`，不再堆回根目录。
