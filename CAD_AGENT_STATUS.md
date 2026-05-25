# 通用 CAD Agent 开发包当前进展

最后更新：2026-05-25

## 当前阶段

阶段 2：第二轮仓库重装已深度推进，通用 CAD Agent Core Lab 从“执行原型”进入“非 CAD 底座闭环原型”阶段。

新增横向机制：卡壳自查、截图能力检查和无 CAD 自检入口已建立。后续任何阶段出现“画不准、画不出来、验证不了”，先按 `CAD_AGENT_BLOCKER_PLAYBOOK.md` 排查。

规则入口已写入根目录 `AGENTS.md`：负责触发 CAD 相关任务、恢复上下文、执行绘图自检门和默认中文输出规则。为提高后续开发时的上下文缓存命中率，日常恢复已新增稳定短入口 `CORE_CONTEXT_BRIEF.md`，详细计划、变更流水和问题库改为按任务展开。

新增架构方向：已按 `CORE_RESTRUCTURE_PLAN.md` 执行第一轮大规模仓库重装，并在第二轮继续推进非 CAD 全量底座：通用底座优先，场景 Agent 轻量化。

本轮已形成一条不依赖真实 CAD 的最小闭环：`DESIGN_BRIEF + DRAWING_MODEL + preferences -> PROJECT_MODEL -> OBJECT_SPEC -> LAYOUT_PROPOSAL -> DESIGN_PROPOSAL -> CAD_PLAN -> dry-run report -> VERIFICATION_REPORT(unverified)`。真实 CAD 落图、截图和实体回读仍登记为延后补验，当前不声称几何准确。

本次状态同步复验（2026-05-25 15:17）：全量 `unittest discover -s tests` 仍为 165 tests OK；`self_check.py` pass；`render_preview.py --check` ready；blank-shell pipeline status ok；blank-shell 4 场景 benchmark status pass；`scripts/run_cad_validation.py --no-cad --output-dir output\validation_runs\docs-sync-no-cad` status pass。

这个开发包不绑定当前家装图纸。当前电脑和当前 DWG 只作为第一套验证环境。后续应能迁移到任意安装好 Codex、CAD、CAD-MCP/Python 的电脑，并适配住宅、工装、店铺、办公、餐饮、展陈等项目。

## 已完成

- 已验证 Codex 可以通过 CAD MCP 在本机当前打开的 AutoCAD 图纸里绘制矩形、圆、直线和文字；这只是环境验证，不是项目绑定。
- 已确认长期路线：不从白话直接跳到画图，中间先生成结构化 `CAD_PLAN`。
- 已创建本通用 CAD Agent 开发包，用于集中管理规则、Schema、示例、脚本和开发记录。
- 已把旧说明文档归档到 `docs/archive/`。
- 已建立第一版通用目录框架。
- 已创建第一版 `draw_test_cabinet.json`。
- 已创建并验证 `scripts/validate_plan.py`。
- 已创建并验证 `scripts/dry_run_plan.py`。
- 已将项目定位修正为“可迁移通用 CAD Agent 开发包”，不绑定当前根目录或当前家装图纸。
- 已实现 `scripts/execute_plan.py` 的第一版执行核心：读取 CAD_PLAN、校验、计算预览矩形/文字/尺寸，并调用驱动层。
- 已实现 `drivers/autocad_com.py` 的第一版 AutoCAD COM 驱动。
- 已新增并迁移 `tests/core/test_execute_plan.py`，覆盖测试柜预览绘制调用。
- 已通过 CAD-MCP 在当前打开的 CAD 文件中把 1800 x 600 测试柜画入 `CODEX_PREVIEW` 图层，并添加文字和基础尺寸标注。
- 已创建 `CAD_AGENT_BLOCKER_PLAYBOOK.md`，作为卡壳自查和自我迭代方法论。
- 已创建 `scripts/self_check.py`，可在不触碰当前 DWG 的情况下检查核心文件、示例计划、预览执行和截图工具链。
- 已让 `scripts/render_preview.py` 支持截图能力检查和可选屏幕截图。
- 已增加 `tests/test_render_preview.py` 和 `tests/test_self_check.py`。
- 已新增根目录 `AGENTS.md`，把 CAD 绘图自检门和卡壳自查规则固化为 Codex 入口规则。
- 已创建 `CORE_RESTRUCTURE_PLAN.md`，记录未来大规模仓库重装设计：以通用 Core 为主线，业务场景 Agent 作为轻量配置层。
- 已创建 `CORE_STATUS.md` 和 `CORE_ROADMAP.md`，用能力矩阵追踪通用底座进度。
- 已创建 `core/`、`agents/`、`projects/`、`docs/architecture`、`docs/decisions`、`docs/roadmap` 等目标结构。
- 已将计划校验、dry-run、执行、截图、自检、DWG 检查、CAD 驱动迁入 `core/` 对应模块。
- 已保留 `scripts/` 和 `drivers/` 兼容包装器，旧命令和旧导入仍可用。
- 已创建 6 个轻量场景 Agent 脚手架：`commercial_fitout`、`residential`、`office`、`restaurant`、`exhibition`、`custom`。
- 已将核心测试迁入 `tests/core/`，并增加重构兼容测试。
- 第一轮保留的 `cad_agent/` 和 `libraries/domains/` 已在第二轮标注为 legacy，并建立 Core/预设新入口。
- 已修剪 `CORE_RESTRUCTURE_PLAN.md`，让它只保留第一轮重装后仍未完成的剩余工作。
- 已新增 9 个高层 schema 与最小 example：`DESIGN_BRIEF`、`DRAWING_MODEL`、`PROJECT_MODEL`、`OBJECT_SPEC`、`STYLE_PROFILE`、`BLOCK_LIBRARY`、`LAYOUT_PROPOSAL`、`DESIGN_PROPOSAL`、`VERIFICATION_REPORT`。
- 已新增 `core/schemas/validator.py`，用于无外部依赖校验高层模型 examples。
- 已新增 `core/verification/verification_report.py`，能区分 `executed_only`、`screenshot_captured`、`geometry_verified`、`unverified` 和 `failed`；失败优先，且校验基点、目标图层文字/标注和 readback scope。
- 已增强 `core/verification/inspect_dwg.py`：默认不连接 CAD，显式 `--connect-cad` 才回读真实 AutoCAD；支持 `--plan` 与 `--format json` 输出验证报告。
- 已为 `core/cad_io/autocad_com.py` 增加 `snapshot_modelspace()` 只读回读入口。
- 已新增 `core/object_engine/parametric_objects.py`，支持 cabinet、shelf、table 的最小 `OBJECT_SPEC -> CAD_PLAN`。
- 已新增 `core/style_engine/style_profile.py` 和 `libraries/styles/modern.json`、`european.json`、`minimal.json`。
- 已新增 `core/block_engine/block_library.py` 与示例块库元数据。
- 已新增 `core/layout_engine/basic_layout.py`，支持基础 bbox、碰撞和单对象边界内布置。
- 已新增 `core/proposal_engine/design_proposal.py`，支持先生成 `DESIGN_PROPOSAL` 再转 `CAD_PLAN`。
- 已给 `DESIGN_PROPOSAL` 和 `CAD_PLAN` 增加确认门：`needs_confirmation=true` 默认不得转计划或执行。
- 已将 `cad_agent/` 三份旧文档标注为 legacy，并新增 `docs/architecture/cad_workflow.md`、`docs/architecture/cad_plan_boundary.md`。
- 已新增 `libraries/domain_presets/` 作为 domain preset 新入口；`libraries/domains/` 仅作为 legacy 兼容副本保留。
- 已新增 `agents/SCENE_AGENT_RULES.md` 和 `commercial_fitout` 两个 workflow 的独立说明，明确场景 Agent 不实现 Core 算法。
- 已把测试从 `TemporaryDirectory` 调整为 `output/test_artifacts`，避免系统临时目录清理权限导致误判。
- 已新增 `core/safety/policy.py`，并让 `execute_plan_file()` 调用安全策略；默认只允许 `CODEX_PREVIEW`，正式图层、删除、保存、覆盖和未确认计划需要显式批准。
- 已新增 `core/project_model/project_builder.py`，支持从 `DESIGN_BRIEF + DRAWING_MODEL` 生成最小 `PROJECT_MODEL`，并对坏 spaces、缺单位、坏边界给出明确错误。
- 已新增 `core/model_loop/reference_checker.py` 和 `core/schemas/registry.py`，支持 workflow schema 校验、模型类型注册和跨模型引用检查。
- 已新增 `core/drawing_analysis/manual_model.py`、`entity_summary.py`，支持手工 drawing model 输入和简化实体统计。
- 已新增 `projects/sample_blank_shell/input/shell.manual.json`，作为不依赖 CAD 的空壳手工输入样例。
- 已新增 `core/block_engine/block_selector.py`、`block_placement.py`，支持块库元数据筛选、fallback object spec 和 block insertion intent。
- 已扩展 `core/layout_engine/`，增加 collision、clearance、scoring 与多对象 layout candidates。
- 已新增 `core/layout_engine/circulation.py`，让 `main_aisle_width_mm` 进入主通道宽度检查。
- 已拆分 `core/object_engine/object_to_plan.py` 和 `core/proposal_engine/proposal_to_plan.py`，把对象/方案生成与计划转换分开。
- 已扩展 cabinet/shelf/table 的基础构件表达，并让 proposal evidence 区分 `from_user`、`from_drawing`、`from_library` 和 `inferred`。
- 已新增 `core/plan_engine/model_to_plan.py`、`dry_run_report.py`，支持高层模型转安全 `CAD_PLAN` 和机器可读 dry-run report。
- 已新增 `core/workflows/non_cad_pipeline.py` 与 `scripts/run_non_cad_pipeline.py`，形成完整非 CAD pipeline，并输出中间 artifacts。
- 已强化 `VERIFICATION_REPORT` 证据门：裸 `entities_are_scoped=True` 不再足以升级为 `geometry_verified`；必须有 created handles 覆盖，截图路径也必须真实存在。
- 已扩展 `VERIFICATION_REPORT`：增加 before/after snapshot diff、批量汇总和失败修复建议字段。
- 已为 `commercial_fitout`、`residential`、`office` 增加 `preferences.json`，并让非 CAD pipeline 读取场景偏好。
- 已将外部方法论抽象为本仓库 Core 底座：`core/capabilities/registry.py`、`core/workflows/artifact_graph.py`、`core/geometry_backends/registry.py`、`core/benchmarks/runner.py`。
- 已新增 `scripts/run_benchmark_suite.py`，让非 CAD pipeline 样例可作为重复 benchmark 执行。
- 已新增 `core/object_engine/object_explainer.py` 和 `core/proposal_engine/proposal_comparison.py`，补齐对象来源说明与候选方案比较。
- 已补齐 schema invalid fixtures、多场景 `PROJECT_MODEL` examples，以及更多通用 block metadata。
- 已新增 `SHELL_MODEL`、`CIRCULATION_MODEL`、`FUNCTION_ZONE` schema/example/invalid fixture，并补充多场景 preferences 差异化回归测试。
- 已完成 Phase P 补强：`tests/core/test_shell_loader.py` 增加 legacy drawing-style 手工输入兼容回归，确认旧 `spaces/entrances/avoid_zones` 仍可规范化为 `SHELL_MODEL`。
- 已完成 Phase Q：新增 `core/geometry_backends/rect2d.py` 与 `core/geometry_backends/orthogonal.py`，提供无依赖矩形、bbox 扣减、path strip、门洞/障碍距离和正交多边形基础校验；layout 的 bbox inside / overlap / clearance 已开始复用该几何底座。
- 已完成 Phase R：新增 `core/layout_engine/path_generation.py`，可从 `PROJECT_MODEL.shell_context` 生成 `straight_spine`、`l_spine`、`along_wall` 动线候选；候选包含 `polyline`、`path_surface`、`connects`、`blocked_reasons` 和 `score`。
- 已完成 Phase S：新增 `core/layout_engine/zone_splitter.py`，可从 bbox shell 和 circulation path surface 切出左右 `FUNCTION_ZONE`，并输出面积、深度、frontage、候选功能、约束、score 和 uncertainties。
- 已完成 Phase T：新增 `libraries/objects/object_defaults.json` 和 `core/layout_engine/placement.py`，扩展 desk/chair/bed/sofa/counter/display_unit 等对象，并支持 block 优先、OBJECT_SPEC fallback 的 zone placement。
- 已完成 Phase U：`DESIGN_PROPOSAL` 已支持多候选 `candidates[]`、`confirmed_candidate_id`、`comparison_summary`，proposal evidence 增加 `from_shell` 与 `from_algorithm`，proposal comparison 支持带来源的场景权重。
- 已完成 Phase V：新增 `core/workflows/blank_shell_pipeline.py` 与 `scripts/run_blank_shell_pipeline.py`，可串联 `SHELL_MODEL -> PROJECT_MODEL -> CIRCULATION_MODEL -> FUNCTION_ZONE -> placements -> LAYOUT_PROPOSAL -> DESIGN_PROPOSAL -> CAD_PLAN -> dry-run -> VERIFICATION_REPORT(unverified)`。
- Phase V benchmark 已从“同一 workflow 重复 4 次”补强为 retail / office / residential / restaurant 四个不同 workflow case；新增 office、residential、restaurant shell examples 和 restaurant preferences。
- 本轮大范围审计已修复三类隐蔽问题：block 尺寸与 CAD_PLAN 默认对象尺寸不一致、`path_to_rect_strips()` 不处理重复连续点、zone 剩余空间为负时 placement fallback 抛异常。

## 正在做

- 本轮已完成开发状态检查与文档同步：`CORE_RESTRUCTURE_PLAN.md`（用户提到 `plan.md` 时默认指该主计划）、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`README.md`、`CORE_CONTEXT_BRIEF.md` 和 `CAD_AGENT_CHANGELOG.md` 已对齐当前“Phase O-V 非 CAD 已通过、Phase W/X 待推进”的口径。
- 已补充 `README.md` 的 Git 提交/推送说明，并收紧 `.gitignore`，避免本机日志和生成输出进入可迁移开发包。
- 第二轮非 CAD 底座第一条闭环已完成；`CORE_RESTRUCTURE_PLAN.md` 已整理为 Phase O-X 的 Core 可用 Alpha 深水计划、待校验登记表、非 CAD 自检命令和 CAD 延后补验总清单。
- 当前仍不扩张单一工装或家装 Agent，场景层只新增边界规则和 workflow 说明，避免把通用能力写死到场景层。
- 已补充默认中文沟通规则：面向用户的说明、状态、方案讨论、追问和结论默认使用中文；代码、命令、路径、Schema 字段和工具名保留原文。
- 已新增根目录 `SHELL_LAYOUT_FOUNDATION_DESIGN.md`，沉淀“空壳布局底座”设计说明。该文档是后续 Core 子能力开发蓝图，不代表功能已实现。
- 已新增 `CAD_AGENT_AUTONOMOUS_VALIDATION.md` 和 `scripts/run_cad_validation.py`，用于换机或真实 CAD 环境中一次性执行自检、落图、截图、回读和结构化报告；Codex 后续不得遇到第一处失败就停止，应按报告分类自动修复仓库内问题并复验。
- 已补强 `CORE_RESTRUCTURE_PLAN.md` 的交付级执行协议：明确一次只执行一个 phase、每个 phase 的固定工作循环、证据状态口径、Phase O-X 依赖交付物、文档交付自检，以及 `run_cad_validation.py` 在 Phase O / Phase W / 固定自检中的使用方式。
- 已继续细化 `CORE_RESTRUCTURE_PLAN.md` 的 Phase O-X：每个 phase 增加 O-01 / P-01 等可逐项执行的小清单，并补入 `context-auditor`、`unit-test-agent`、`engine-agent`、`pipeline-agent`、`cad-validation-agent`、`docs-sync-agent`、`review-agent` 等建议分工，方便后续 Codex 长时间、分阶段、自检式执行。
- Phase O 已完成：`core/capabilities/registry.py` 现在为每个公开能力暴露 `maturity` 和 `known_limits`；`CORE_STATUS.md` 已补充 `alpha_ready` / `blocked_by_cad` 状态口径，并收紧 layout、drawing、proposal、verification 的限制说明。Phase O 证据路径：`output\validation_runs\phase-o-no-cad\report.json`，状态为 `pass`。
- Phase P 已完成并补强：新增 `core/drawing_analysis/shell_loader.py`，`projects/sample_blank_shell/input/shell.manual.json` 已升级为 `SHELL_MODEL`，新增 retail / office blank shell examples，`project_builder` 支持 `shell_model` 输入并保留 shell_id、constraints、source、uncertainties；已补 legacy drawing-style 输入兼容测试。Phase P 证据路径：`output\validation_runs\phase-p-no-cad\report.json`，状态为 `pass`。
- Phase Q 已完成：`rect2d` / `orthogonal_polygon` 默认几何能力已登记，目标测试组通过；`path_to_rect_strips()` 已补重复连续点回归。
- Phase R 已完成：`PROJECT_MODEL` 已保留 `shell_context`；`layout.generate_circulation_candidates` capability 已登记；`examples/circulation_models/retail_straight_spine.json` 和 `retail_l_spine.json` 均通过 schema 校验。
- Phase S 已完成：`layout.split_function_zones` capability 已登记；`examples/function_zones/retail_zone_left.json` 与 `office_zone_desk_band.json` 均通过 schema 校验。
- Phase T 已完成：`layout.create_zone_placements` capability 已登记；`examples/object_specs/desk_1400x700.json` 与 `sofa_2200x900.json` 均通过 schema 校验；placement 已补剩余空间不足时的 blocked 结果。
- Phase V 已完成：新增 `tests/core/test_blank_shell_pipeline.py`、`tests/core/test_benchmark_cli.py` 覆盖 pipeline 与 CLI；`workflow.blank_shell_pipeline` 已进入 capability registry。后续进入 Phase W / X 前，仍需真实 CAD readback 补验和更多场景偏好 Alpha 验收。
- 已新增 `CORE_CONTEXT_BRIEF.md` 作为稳定短上下文入口，并更新 `AGENTS.md`、`README.md` 与 `CAD_AGENT_RULES.md`：后续日常开发默认先读短入口，再按任务读取详细文档，避免每轮无差别展开大计划、变更流水和历史问题。

## 下一步

1. 回家或新机器验证时，先读取 `CAD_AGENT_AUTONOMOUS_VALIDATION.md`，运行 `scripts/run_cad_validation.py`，按报告分类继续修复或确认外部阻塞。
2. 继续补齐 `CORE_RESTRUCTURE_PLAN.md` 中更深层未完成方向：更复杂 drawing analysis、真实多方案设计推理、多场景 benchmark、真实 CAD readback 闭环。
3. 每完成一个 phase，同步更新 `CORE_RESTRUCTURE_PLAN.md` 的待校验登记表、`CAD_AGENT_STATUS.md` 和 `CAD_AGENT_CHANGELOG.md`。
4. CAD 环境恢复后，按 `CORE_RESTRUCTURE_PLAN.md` 的 CAD 补验清单验证 `execute_plan`、`inspect_dwg --connect-cad`、created handles 和截图证据。

## 通用适用范围

当前目标不是只服务某一张家装图，而是形成可迁移能力：

```text
住宅家装
商业工装
零售店铺
办公空间
餐饮空间
展厅展陈
其他 CAD 平面/布置/标注场景
```

如果进入某个具体项目，应先创建或读取该项目自己的 `cad_context.json`，不要把具体项目上下文写死到通用规则里。

## 已验证命令

PowerShell 中应优先使用 CAD-MCP 虚拟环境 Python：

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
& 'C:\Users\123235\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' scripts\validate_plan.py examples\plans\draw_test_cabinet.json
& 'C:\Users\123235\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' scripts\dry_run_plan.py examples\plans\draw_test_cabinet.json
& 'C:\Users\123235\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' scripts\self_check.py
& 'C:\Users\123235\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' scripts\render_preview.py --check
& 'C:\Users\123235\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' -m unittest discover -s tests
& 'C:\Users\123235\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' -m core.schemas.validator core\schemas\design_brief.schema.json examples\design_briefs\minimal_cabinet_brief.json
& 'C:\Users\123235\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' scripts\inspect_dwg.py --plan examples\plans\draw_test_cabinet.json --format json --no-cad
& 'C:\Users\123235\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' scripts\run_non_cad_pipeline.py examples\workflows\full_non_cad_core_loop.json --output-dir output\test_artifacts\non_cad_pipeline\manual
& 'C:\Users\123235\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' scripts\run_blank_shell_pipeline.py examples\workflows\blank_shell_layout_loop.json --output-dir output\test_artifacts\blank_shell_pipeline\manual
& 'C:\Users\123235\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' scripts\run_benchmark_suite.py examples\benchmarks\non_cad_core_benchmark.json --output-root output\test_artifacts\benchmarks\manual
& 'C:\Users\123235\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\blank_shell_manual
& 'C:\Users\123235\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\docs-sync-no-cad
```

结果：

```text
VALID CAD_PLAN
CAD_PLAN DRY RUN
core test_execute_plan: OK
unit test discover: 165 tests OK
self_check.py: status pass
render_preview.py --check: status ready
core.plan_engine.validate_plan: VALID CAD_PLAN
core.schemas.validator: VALID JSON MODEL
inspect_dwg --no-cad: JSON VERIFICATION_REPORT, status unverified
run_non_cad_pipeline: status ok, output project/object/layout/proposal/CAD_PLAN/dry-run/verification artifacts
run_blank_shell_pipeline: status ok, output shell/project/circulation/zones/placements/layout/proposal/CAD_PLAN/dry-run/verification artifacts
run_benchmark_suite: status pass, minimal-cabinet-non-cad passed
blank_shell_core_benchmark: status pass, 4 scenario workflow cases passed
run_cad_validation --no-cad: status pass, report at output\validation_runs\docs-sync-no-cad\report.json
```

## 暂不做

- 暂不做完整自动设计。
- 暂不做复杂房间识别。
- 暂不做 SQL 数据库。
- 暂不做全行业对象库。
- 暂不把所有行业细则写进根目录 `AGENTS.md`；根目录保留 CAD 相关任务触发规则、准确性门槛和上下文恢复入口，行业差异仍放在 `agents/`、`libraries/` 和项目资料里。

## 下次恢复开发时怎么问

你可以直接说：

```text
读取本仓库 AGENTS.md 和 CORE_CONTEXT_BRIEF.md，告诉我 CAD Agent 当前开发状态和下一步建议。
```

我应该优先读取：

```text
AGENTS.md
CORE_CONTEXT_BRIEF.md
```

如果要做完整交接、执行某个 Phase、排查失败或追溯历史，再按 `CORE_CONTEXT_BRIEF.md` 的“按需展开”表读取详细文件。
