## Context

当前训练期已经有 `agents/pipeline/` 多 Agent 流水线、`agents/residential/` 主训场景、资产检索与训练工作台。训练工作台展示的是对象/绘图/标注能力矩阵，适合看单项训练，但用户希望系统更像真实设计师成长：从 CAD 基础命令开始，逐步形成能调用流程 Agent、场景知识和资产库的电子设计师。

这次变更必须保持现有边界：`core/` 仍负责通用算法、CAD 执行、校验和审计；场景 Agent 仍是轻量规则层；OpenSpec 只承接本次复杂目标调整，不成为第二套主计划。

## Goals / Non-Goals

**Goals:**

- 引入 `CAD Designer Agent` 作为训练期总目标，统一“总设计师 Agent”口径。
- 建立成长阶段模型：基础 CAD 操作、几何约束、对象符号、房间平面、专业表达、施工图、设计判断。
- 第一阶段毕业目标采用“电子设计师雏形”，但首批课程从基础 CAD 操作开始。
- 训练工作台展示总 Agent、成长阶段、基础课程、责任流水线和验收边界。
- 保持现有能力矩阵，将其转换为总设计师 Agent 的能力护照。

**Non-Goals:**

- 不新增 CAD 几何执行算法。
- 不提升表 C，不把工作台训练状态当真实 CAD 能力证明。
- 不把 `agents/cad_designer/` 做成第二套 Core 或执行实现。
- 不改变 `CODEX_PREVIEW`、validate、dry-run、handle readback 等真实 CAD 门槛。

## Decisions

1. **采用中改 B：新增顶层 Agent，不推翻现有流水线**

   `CAD Designer Agent` 放在 `agents/cad_designer/`，只定义目标、学习方式、输入输出、调用边界和验收口径。现有 pipeline Agent 仍作为流程能力，家装 Agent 仍作为场景知识。这样能表达“电子设计师”的人格化训练目标，又不把执行逻辑塞进 Agent 目录。

2. **第一阶段目标采用 C，但课程从 A 铺开**

   第一阶段叫“电子设计师雏形”：要求基础命令、家装对象、审计自检一起训练；但首批课程只覆盖基础 CAD 操作，如线、矩形、圆、多段线、选择、移动、复制、旋转、镜像、偏移、修剪、图层、闭合。这样避免一开始只练家具对象，也避免陷入纯命令练习而脱离目标图纸。

3. **训练工作台增加成长视角，而不是替代能力矩阵**

   生成数据新增 `designerAgent`、`growthStages`、`foundationCourses`。HTML 可先用现有边界/智能体视图显示这些字段；后续再做更丰富的视觉交互。能力矩阵继续保留，并把基础 CAD 能力归入“基础绘图/基础操作”组。

4. **课程通过要有训练证据边界**

   每个基础课程只声明它训练了哪类操作、对应哪些 pipeline Agent、什么算 pass、什么不能声称。基础课程通过只代表训练台阶段通过，不代表施工图能力或表 C 变化。

5. **状态入口同步到主文档**

   `CORE_CONTEXT_BRIEF.md`、`docs/training/README.md`、`docs/planning/任务清单.md` 需要明确新目标模型，避免后续 Agent 仍按旧“对象矩阵优先”理解训练期。

## Risks / Trade-offs

- [Risk] 总 Agent 容易被误解为新的执行层 → Mitigation: `agents/cad_designer/` 禁止 Python 和 CAD 直接执行，只写契约和边界。
- [Risk] 基础课程进度被误读为真实 CAD 实力 → Mitigation: 工作台和文档明确表 C、训练 pass、案例 pass 三者隔离。
- [Risk] 中改范围扩散成 UI 大改 → Mitigation: 本轮优先改数据模型、文档和最小 HTML 文案，保留后续视觉重构空间。
- [Risk] 现有训练台已在用户工作区有未提交改动 → Mitigation: 只在现有脚本和数据上增量修改，不回滚已有变更。

## Migration Plan

1. 新增 `agents/cad_designer/` 契约文件和训练文档。
2. 更新 `scripts/build_capability_map_data.py`，输出总设计师 Agent 和成长课程数据。
3. 重新生成 `capability-map-data.js`。
4. 更新训练入口文档和任务清单。
5. 运行训练工作台同步/Agent 检查和文档治理检查。

Rollback 策略：删除新增 `agents/cad_designer/`、训练成长文档和生成数据字段，恢复工作台文案即可；不涉及数据库或 CAD 几何迁移。

## Open Questions

- 后续是否为成长路径单独做工作台 Tab，本轮先不强制。
- 基础课程是否需要真实 AutoCAD 每课一图，本轮先定义课程和验收边界，后续训练轮再补真实案例。
