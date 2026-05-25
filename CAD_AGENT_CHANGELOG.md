# CAD Agent 变更记录

这个文件记录 CAD Agent 测试工作区的结构、规则、Schema、脚本和重要决策变化。

## 2026-05-25

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
