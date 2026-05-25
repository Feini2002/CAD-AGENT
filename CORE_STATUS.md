# Core Status

最后更新：2026-05-25

本文追踪通用 CAD Agent Core Lab 的底座能力状态。当前目标是先把仓库从“执行层脚手架”整理成“通用底座优先、场景 Agent 轻量化”的结构，而不是扩写某一个工装、家装或店铺 Agent。

## 状态口径

| 状态 | 含义 |
| --- | --- |
| prototype | 已有最小闭环或脚本原型，可以作为迁移来源，但接口和目录仍可能调整 |
| alpha_ready | 已有较稳定入口、专项测试、基线验证和明确证据路径，可作为 Alpha 阶段能力使用 |
| blocked_by_cad | 非 CAD 逻辑已有基础，但完成声明依赖真实 CAD 落图、截图或实体回读补验 |
| scaffold | 已有目录或文档占位，职责明确，但核心逻辑尚未实现 |
| not_started | 仅在路线图或架构中定义，尚未开始实现 |
| blocked | 已知依赖缺失或验证路径缺失，不能继续声称可用 |

## 能力矩阵

| 能力 | 状态 | 当前依据 | 下一步 |
| --- | --- | --- | --- |
| CAD execution | prototype | `core/execution/execute_plan.py` 可执行最小 `CAD_PLAN` 并默认写入 `CODEX_PREVIEW`；`scripts/execute_plan.py` 保留兼容包装器 | 补更多对象类型与正式实体回读 |
| preview safety | prototype | `core/safety/policy.py` 已提供可调用策略，执行层默认只允许 `CODEX_PREVIEW`，未确认计划、正式图层、保存、覆盖、删除需要显式批准 | 补更严格的批准证据格式与审计记录 |
| validate | prototype | `core/plan_engine/validate_plan.py` 已可校验测试柜 CAD_PLAN；旧 `scripts/validate_plan.py` 兼容 | 扩展到高层模型 |
| dry-run | prototype | `core/plan_engine/dry_run_plan.py` 已可预演测试柜；`core/plan_engine/dry_run_report.py` 已输出机器可读 report；旧 `scripts/dry_run_plan.py` 兼容 | 扩展批量 dry-run 汇总 |
| self_check | prototype | `core/verification/self_check.py` 已作为基础自检入口；旧 `scripts/self_check.py` 兼容 | 补更多环境探针 |
| render_preview | prototype | `core/verification/render_preview.py --check` 和截图入口已建立；旧 `scripts/render_preview.py` 兼容 | 连接实体回读报告 |
| CAD IO adapter | prototype | `core/cad_io/autocad_com.py` 可连接 AutoCAD COM；旧 `drivers/` 兼容 | 设计统一驱动接口 |
| entity readback | prototype | `core/verification/inspect_dwg.py` 已支持无 CAD 报告壳、COM-like 实体标准化、`--execution-summary` created handles 入口、`--connect-cad` 显式真实回读入口 | 在真实 CAD 环境验证 `snapshot_modelspace`、handles 和 report 升级路径 |
| schemas | prototype | `core/schemas/` 已有 CAD_PLAN、CAD_CONTEXT、CAD_OBJECT 兼容副本，并新增 9 个高层 schema、examples、registry、workflow schema/reference checker；每个注册模型已有 invalid fixture | 继续扩展更贴近真实项目的正反例 |
| capability runtime | prototype | `core/capabilities/registry.py` 已登记 Core 能力、输入 schema、输出 contract、风险等级、CAD 依赖、验证命令、`maturity` 和 `known_limits`，并支持 `run_capability()`；已新增 `drawing_analysis.load_shell_model`、`layout.generate_circulation_candidates`、`layout.split_function_zones`、`layout.create_zone_placements` 与 `workflow.blank_shell_pipeline` | 补更多 Core 能力与审计记录字段 |
| artifact graph | prototype | `core/workflows/artifact_graph.py` 可从 workflow artifacts 生成依赖顺序、路径检查和循环依赖错误 | 后续接入更多 workflow 类型和产物差异检查 |
| geometry backends | alpha_ready | `core/geometry_backends/rect2d.py` 已提供面积、中心点、相交、包含、间距、膨胀、bbox no-place-zone 保守扣减、path strip 和门洞/障碍距离检查；`orthogonal.py` 已提供闭合、正交、自交、bbox、面积校验；registry 可发现 `rect2d`、`orthogonal_polygon`、`cad_plan_rect2d`，外部几何库仍只是可选槽位 | 当前只覆盖矩形和简单正交多边形，不替代成熟几何库；是否引入 `shapely` / CAD kernel 仍需用户决策 |
| benchmarks | prototype | `core/benchmarks/runner.py` 与 `scripts/run_benchmark_suite.py` 可重复运行 minimal non-CAD benchmark；`examples/benchmarks/blank_shell_core_benchmark.json` 已覆盖 retail、office、residential、restaurant 四个不同 blank-shell workflow 并输出 pass/fail 汇总 | 扩展历史趋势记录和更多真实项目回归样本 |
| drawing_model | prototype | `core/drawing_analysis/manual_model.py` 和 `entity_summary.py` 可从手工标注或简化实体列表生成/汇总 `DRAWING_MODEL`，并保留不确定点；`core/drawing_analysis/shell_loader.py` 已可把人工空壳 JSON 规范化为 `SHELL_MODEL` | 接真实 DWG/PDF 提取，继续保持人工空壳与自动读图边界清楚 |
| project_model | prototype | `core/project_model/project_builder.py` 可从 `DESIGN_BRIEF + DRAWING_MODEL` 或 `DESIGN_BRIEF + SHELL_MODEL` 合并生成 `PROJECT_MODEL`，并保留 shell_id、约束、来源、不确定点和 `shell_context` 中的入口、障碍、避让区、必连通点 | 增加多场景 examples、冲突处理和 shell/circulation/zones 串联 |
| object_engine | prototype | `core/object_engine/parametric_objects.py` 从 `libraries/objects/object_defaults.json` 读取默认尺寸，可生成 cabinet/shelf/table/desk/chair/bed/sofa/counter/display_unit 的 `OBJECT_SPEC`，并包含基础构件角色；`object_to_plan.py` 负责安全预览计划转换 | 扩展尺寸来源说明、更多对象规格和真实块库映射 |
| style_engine | prototype | `core/style_engine/style_profile.py` 可加载 modern/european/minimal 风格配置 | 将风格 token 连接到对象细节生成 |
| block_engine | prototype | `core/block_engine/block_library.py`、`block_selector.py`、`block_placement.py` 可做元数据筛选、fallback object spec 和 insertion intent；示例块库已覆盖 cabinet/table/shelf/chair/counter/desk/sofa/display_unit；旋转/插入点 bbox 已有保守规则 | 接真实块插入和块引用验证 |
| layout_engine | prototype | `core/layout_engine/basic_layout.py`、`collision.py`、`clearance.py`、`circulation.py`、`path_generation.py`、`zone_splitter.py`、`placement.py` 已支持多对象候选、边界/碰撞/clearance/主通道检查、动线候选、功能区切分和 zone-driven placement；bbox containment / overlap / clearance 已复用 `core.geometry_backends.rect2d` | 扩展更真实的通道、zone 和 placement 优化 |
| shell/circulation/function zones | prototype | `SHELL_MODEL`、`CIRCULATION_MODEL`、`FUNCTION_ZONE` schema、example 和 invalid fixture 已建立；Phase P/R/S 已完成 shell loader、project merge、straight / L / along-wall 动线候选与 bbox shell 左右功能区切分；Phase V 已接入 placement/proposal/CAD_PLAN pipeline | 扩展正交 shell 与更真实空间语义 |
| proposal_engine | prototype | `core/proposal_engine/design_proposal.py` 可生成多候选方案，并区分 user/drawing/shell/library/algorithm/inferred evidence；`proposal_to_plan.py` 支持 `confirmed_candidate_id` 并保持确认门；`proposal_comparison.py` 已支持 layout candidates 排序、tradeoffs 和带来源的场景权重 | 扩展真实多方案设计推理、候选转计划和用户确认流 |
| plan_engine | prototype | validate/dry-run 兼容入口已稳定；`model_to_plan.py` 可把高层对象/布局/方案转为一个或多个安全 `CAD_PLAN` envelope | 扩展 plan_id、批量失败隔离和 generated examples |
| verification | prototype | `VERIFICATION_REPORT`、fake readback、plan geometry checks、created handles 证据门、截图存在性检查、before/after snapshot diff、批量汇总和修复建议已建立；无真实 CAD readback 时仍只能给出 `unverified` 口径 | 接真实 CAD 回读和真实 before/after diff |
| safety | prototype | `core/safety/policy.py` 已接入 `execute_plan_file()`，场景 Agent 边界测试禁止绕过执行/验证核心 | 强化批准来源与审计 evidence |
| commercial_fitout_agent | prototype | `agents/commercial_fitout/` 已建立轻量脚手架、workflow 名称和 preferences 数据；多场景 preference 差异已进入 layout 回归测试 | 继续只写场景差异，不实现 Core 算法 |
| residential_agent | prototype | `agents/residential/` 已建立轻量脚手架和 preferences 数据；多场景 preference 差异已进入 layout 回归测试 | 继续只写场景差异 |

## 当前结论

当前仓库已经具备 Core 执行底座与非 CAD 设计链路的早期闭环，并新增了方法论内化层：能力目录/runtime、workflow 产物图、几何后端抽象、benchmark runner、对象解释和候选比较。它们让非 CAD 底座更可治理、可追踪、可替换和可评测，但仍不等同于完整自动设计大脑，也不替代真实 CAD 落图、截图和实体回读补验。后续 70%-80% 的开发仍应进入 `core/`：数据模型、图纸理解、项目模型、对象、风格、图库块、布局、方案、计划、执行、验证和安全。

场景 Agent 只能保持轻量：它们复用 Core，只补场景词汇、默认参数、业务偏好、专用工作流和少量专用规则。

`CORE_RESTRUCTURE_PLAN.md` 已从第一轮重装设计草案修剪为剩余工作计划。后续读取它时，应把它当作“还没做什么”的清单，而不是已完成迁移的待办。

最近复验：2026-05-25 17:19 已跑通非 CAD 基线，`unittest discover -s tests` 为 196 tests OK，`self_check.py` 为 pass，`render_preview.py --check` 为 ready，`scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 pass 且 0 findings，`scripts/run_blank_shell_pipeline.py examples\workflows\blank_shell_layout_loop.json --output-dir output\test_artifacts\blank_shell_pipeline\hardening-polish` 为 ok，`scripts/run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\hardening-polish` 为 4/4 pass，`scripts/run_cad_validation.py --no-cad --output-dir output\validation_runs\hardening-polish-no-cad` 为 pass。真实 CAD 验证本轮未运行；该复验只证明非 CAD 链路和无 CAD 验证总控可用，不证明真实 CAD 几何准确。

## 遗留目录

第一轮重装保留了两个遗留目录，避免一次迁移同时改变过多引用：

- `cad_agent/`：已标注为 legacy；核心说明收束到 `docs/architecture/`、`core/schemas/` 和 `core/safety/`。
- `libraries/domains/`：保留 legacy 兼容副本；新入口为 `libraries/domain_presets/`。

保留它们不是新主线。后续新增通用能力仍应进入 `core/`，新增场景差异仍应进入 `agents/`。

## 近期风险

- 第一轮迁移已建立兼容包装器；后续移除旧入口前必须先更新所有文档和测试。
- `cad_agent/` 与 `libraries/domains/` 已完成第二轮 legacy 标注和新入口收束；后续不作为新开发入口。
- `entity readback` 已有最小可测协议、created handles 证据门和执行摘要入口，但真实 AutoCAD COM 回读尚需在已打开 DWG 中集成验证；在此之前仍不能把执行返回值等同于完整几何验收。
- 若过早扩写工装或家装 Agent，容易把通用能力写死到单一场景。
