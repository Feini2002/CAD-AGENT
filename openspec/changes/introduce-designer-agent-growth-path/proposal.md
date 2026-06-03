## Why

现有训练工作台以对象/流程能力矩阵为中心，能追踪沙发、门窗、标注等单项训练，但不像真实设计师从 CAD 基础操作逐步成长到专业图纸表达。现在需要把训练目标升级为“电子设计师总 Agent”的成长路径，同时保留已有多 Agent 流水线和能力矩阵。

## What Changes

- 新增 `CAD Designer Agent` 作为训练期的顶层目标对象，定位为“会调用流程 Agent、场景规则和资产库的电子设计师”。
- 将现有对象/绘图/标注能力矩阵改为总设计师 Agent 的能力护照，而不是互相并列的最终主体。
- 新增成长路径：从 CAD 基础图元与编辑命令，逐步到几何约束、对象符号、房间平面、专业表达和施工图。
- 第一阶段毕业目标采用“电子设计师雏形”：基础命令、家装对象、审计自检一起练，但第一批课程从 CAD 基础能力铺开。
- 训练工作台需要能展示总 Agent、成长阶段、基础课程入口、当前毕业目标、责任流水线和验收边界。
- 不改变真实 CAD 完成声明门槛；训练通过、工作台进度、表 C 仍保持边界隔离。

## Capabilities

### New Capabilities

- `designer-agent-growth-path`: 约束总设计师 Agent 的训练目标、成长阶段、第一阶段课程、能力护照和验收边界。

### Modified Capabilities

- 无。

## Impact

- 影响训练期文档：`docs/training/README.md`、新增总设计师 Agent 成长路径文档、`CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md`。
- 影响 Agent 注册/说明：新增或引用 `agents/cad_designer/`，并保持场景 Agent 轻量边界不变。
- 影响训练工作台数据：`scripts/build_capability_map_data.py`、生成的 `capability-map-data.js`，以及必要的 HTML 文案。
- 影响验收：新增工作台 Agent 自检、OpenSpec tasks 完成状态、文档治理/训练台同步检查。
- 非目标：不新增真实 CAD 几何能力证明，不提升表 C，不把基础课程进度声明为施工图能力。
