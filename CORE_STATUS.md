# Core Status

最后更新：2026-05-25

本文追踪通用 CAD Agent Core Lab 的底座能力状态。当前目标是先把仓库从“执行层脚手架”整理成“通用底座优先、场景 Agent 轻量化”的结构，而不是扩写某一个工装、家装或店铺 Agent。

## 状态口径

| 状态 | 含义 |
| --- | --- |
| prototype | 已有最小闭环或脚本原型，可以作为迁移来源，但接口和目录仍可能调整 |
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
| capability runtime | prototype | `core/capabilities/registry.py` 已登记 Core 能力、输入 schema、输出 contract、风险等级、CAD 依赖和验证命令，并支持 `run_capability()` | 补更多 Core 能力与审计记录字段 |
| artifact graph | prototype | `core/workflows/artifact_graph.py` 可从 workflow artifacts 生成依赖顺序、路径检查和循环依赖错误 | 后续接入更多 workflow 类型和产物差异检查 |
| geometry backends | prototype | `core/geometry_backends/registry.py` 已提供无依赖 `cad_plan_rect2d` 后端，并把 `cadquery`、`build123d`、`ifcopenshell` 登记为未来可选槽位 | 是否引入成熟几何库仍需用户决策；当前不新增依赖 |
| benchmarks | prototype | `core/benchmarks/runner.py` 与 `scripts/run_benchmark_suite.py` 可重复运行 minimal non-CAD benchmark 并输出 pass/fail 汇总 | 扩展多场景 benchmark case 与历史趋势记录 |
| drawing_model | prototype | `core/drawing_analysis/manual_model.py` 和 `entity_summary.py` 可从手工标注或简化实体列表生成/汇总 `DRAWING_MODEL`，并保留不确定点 | 接真实 DWG/PDF 提取 |
| project_model | prototype | `core/project_model/project_builder.py` 可从 `DESIGN_BRIEF + DRAWING_MODEL` 合并生成 `PROJECT_MODEL`，并校验单位、空间与边界 | 增加多场景 examples 与冲突处理 |
| object_engine | prototype | `core/object_engine/parametric_objects.py` 可生成 cabinet/shelf/table 的 `OBJECT_SPEC`，并包含基础构件角色；`object_to_plan.py` 负责安全预览计划转换 | 扩展更多对象规格和尺寸来源说明 |
| style_engine | prototype | `core/style_engine/style_profile.py` 可加载 modern/european/minimal 风格配置 | 将风格 token 连接到对象细节生成 |
| block_engine | prototype | `core/block_engine/block_library.py`、`block_selector.py`、`block_placement.py` 可做元数据筛选、fallback object spec 和 insertion intent；示例块库已覆盖 cabinet/table/shelf/chair/counter；旋转/插入点 bbox 已有保守规则 | 接真实块插入和块引用验证 |
| layout_engine | prototype | `core/layout_engine/basic_layout.py`、`collision.py`、`clearance.py`、`circulation.py`、`scoring.py` 已支持多对象候选、边界/碰撞/clearance/主通道检查和评分 | 扩展功能区、避让区和更真实的通道模型 |
| shell/circulation/function zones | prototype | `SHELL_MODEL`、`CIRCULATION_MODEL`、`FUNCTION_ZONE` schema、example 和 invalid fixture 已建立 | 接入 layout/proposal 生成链路并扩展真实空间语义 |
| proposal_engine | prototype | `core/proposal_engine/design_proposal.py` 可生成方案并区分 user/drawing/library/inferred evidence；`proposal_to_plan.py` 负责确认门后的计划清单转换；`proposal_comparison.py` 已支持 layout candidates 排序与 tradeoffs | 扩展真实多方案设计推理和用户确认流 |
| plan_engine | prototype | validate/dry-run 兼容入口已稳定；`model_to_plan.py` 可把高层对象/布局/方案转为一个或多个安全 `CAD_PLAN` envelope | 扩展 plan_id、批量失败隔离和 generated examples |
| verification | prototype | `VERIFICATION_REPORT`、fake readback、plan geometry checks、created handles 证据门、截图存在性检查、before/after snapshot diff、批量汇总和修复建议已建立 | 接真实 CAD 回读和真实 before/after diff |
| safety | prototype | `core/safety/policy.py` 已接入 `execute_plan_file()`，场景 Agent 边界测试禁止绕过执行/验证核心 | 强化批准来源与审计 evidence |
| commercial_fitout_agent | prototype | `agents/commercial_fitout/` 已建立轻量脚手架、workflow 名称和 preferences 数据；多场景 preference 差异已进入 layout 回归测试 | 继续只写场景差异，不实现 Core 算法 |
| residential_agent | prototype | `agents/residential/` 已建立轻量脚手架和 preferences 数据；多场景 preference 差异已进入 layout 回归测试 | 继续只写场景差异 |

## 当前结论

当前仓库已经具备 Core 执行底座与非 CAD 设计链路的早期闭环，并新增了方法论内化层：能力目录/runtime、workflow 产物图、几何后端抽象、benchmark runner、对象解释和候选比较。它们让非 CAD 底座更可治理、可追踪、可替换和可评测，但仍不等同于完整自动设计大脑，也不替代真实 CAD 落图、截图和实体回读补验。后续 70%-80% 的开发仍应进入 `core/`：数据模型、图纸理解、项目模型、对象、风格、图库块、布局、方案、计划、执行、验证和安全。

场景 Agent 只能保持轻量：它们复用 Core，只补场景词汇、默认参数、业务偏好、专用工作流和少量专用规则。

`CORE_RESTRUCTURE_PLAN.md` 已从第一轮重装设计草案修剪为剩余工作计划。后续读取它时，应把它当作“还没做什么”的清单，而不是已完成迁移的待办。

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
