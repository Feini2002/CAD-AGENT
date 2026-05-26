# CAD Agent 规则

本目录是可迁移的 CAD Agent 开发包，不绑定某一张 DWG、某一套家装图纸或某一台电脑。

## 默认中文输出

面向用户的说明、状态汇报、方案讨论、结论和追问默认使用中文。只有以下内容保留英文或原文：

- 代码、命令、路径、文件名、Schema 字段和 JSON key
- CAD / Python / Git / MCP / AutoCAD 等工具、库、API 的专有名称
- 用户明确要求英文输出时

如果引用外部技能、插件或工具模板中的英文规则，应先理解其含义，再用中文向用户转述；不要把英文模板原样作为最终答复。

## 先恢复上下文

在进行 CAD Agent 开发、绘图、调试或状态汇报前，默认使用短入口恢复上下文，减少每轮开发的上下文抖动：

1. 先读取 `CORE_CONTEXT_BRIEF.md`
2. 再按当前任务读取 `CORE_CONTEXT_BRIEF.md` 里“按需展开”表指定的详细文件

只有在下列情况才全文读取旧的完整上下文文件组：

- 用户要求完整状态汇报、交接或审计
- 要执行 `CORE_RESTRUCTURE_PLAN.md` 中某个 Phase
- 遇到卡壳、回归、绘图不准或 CAD 环境问题
- 要修改规则、计划、状态、变更记录或问题记录

完整上下文文件组为：

1. `README.md`
2. `CORE_STATUS.md`
3. `CORE_ROADMAP.md`
4. `CORE_RESTRUCTURE_PLAN.md`
5. `CAD_AGENT_STATUS.md`
6. `CAD_AGENT_RULES.md`
7. `CAD_AGENT_BLOCKER_PLAYBOOK.md`
8. `CAD_AGENT_CHANGELOG.md`
9. `CAD_AGENT_ISSUES.md`

## 单一 PlanMD 开发主线

当前唯一 `PlanMD` / 开发主线是 `CORE_RESTRUCTURE_PLAN.md`。根目录没有独立 `plan.md`；用户提到 `PlanMD`、`plan.md`、主计划或主 plan 时，默认指 `CORE_RESTRUCTURE_PLAN.md`。

- `PlanMD` 只做文档治理和开发排序，不改变本仓库“通用 CAD Agent Core Lab”的方向。
- `CORE_RESTRUCTURE_PLAN.md` 决定当前活跃工作队列、Phase 顺序、优先级、Decision Gate 和退出标准。
- `docs/planning/phase-*.md` 只是辅助执行剧本，可以写命令和检查表，但不能成为第二套主计划，也不能保留后置 Backlog 副本。
- `CORE_STATUS.md`、`CAD_AGENT_STATUS.md` 只写能力、证据、风险和当前状态，不承载独立下一步。
- 新增待办、调整优先级、改变退出标准或拆分未来小包时，先同步 `CORE_RESTRUCTURE_PLAN.md`，再更新辅助 MD 的引用或状态说明。
- 若文档整理和 Core 优先、`CAD_PLAN` 中间层、真实 CAD 验证门槛或场景轻量化发生冲突，必须以这些根边界为准。

## 交付必须带进度估算

每次 CAD Agent 相关交付的最终回复，都必须附带粗估开发进度，固定包含：

- `总进度`
- `Core 底座开发进度`
- `Agent 多场景实现进度`

默认按 `总进度 = Core 底座开发进度 * 70% + Agent 多场景实现进度 * 30%` 估算。百分比只是产品和工程节奏参考，不得替代测试、benchmark、截图、created handles 回读或 `geometry_verified` 证据。

## Core 优先

本仓库是通用 CAD Agent Core Lab。可复用能力放入 `core/`，共享资源放入 `libraries/`，项目专属资料放入 `projects/`，只有场景差异放入 `agents/<scenario>/`。

不要把仓库改成工装专用、家装专用或 CAD-MCP 专用项目。场景 Agent 必须保持轻量，并复用 Core。

## 不从白话直接跳到 CAD

自然语言必须先变成 `CAD_PLAN` 或明确的结构化绘图意图，再执行 CAD 绘制；只有明确的临时低风险测试可以例外。真实落图前必须先校验和 dry-run。

## 强制绘图准确性门槛

在告诉用户 CAD 图纸已经完成或准确之前，Codex 必须用证据核验：

- 预期对象、尺寸、基点、图层、文字、标注和允许误差
- `scripts/validate_plan.py` 结果
- `scripts/dry_run_plan.py` 结果
- 使用新架构时，对应的 `core.plan_engine` 入口结果
- `CODEX_PREVIEW` 上的实际 CAD 输出
- `scripts/render_preview.py --capture-screen` 截图，或检查路径中的 CAD 实体回读
- 实际输出与预期 `CAD_PLAN` 或结构化意图的对比

如果实际输出和预期不一致，Codex 不得把错误结果当成完成品交给用户。必须诊断差异，做最小安全修复，重新绘制或运行，并再次验证。

## 卡壳或绘图不准流程

当用户说“画不准”“画不出来”“不对”“继续修”，或 Codex 无法证明图纸准确时，按 `CAD_AGENT_BLOCKER_PLAYBOOK.md` 执行。

最低必跑探针：

```powershell
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' 'scripts\self_check.py'
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' 'scripts\render_preview.py' --check
```

如果需要视觉证据且用户没有禁止截图，保存一个检查点：

```powershell
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' 'scripts\render_preview.py' --capture-screen --output 'output\previews\manual-check.png'
```

如果截图或回读不可用，应说明暂时无法证明准确性，并优先补齐缺失的验证机制，再声称完成。

## 保护用户 DWG

- 默认使用 `CODEX_PREVIEW`。
- 默认不保存当前 DWG。
- 不覆盖原始 DWG 文件。
- 未经用户明确批准，不修改正式图层、不删除实体、不执行不可逆 CAD 操作。

## 保持记录更新

当 CAD Agent 规则、脚本、测试、工作流文档或状态发生变化时，更新：

- `CAD_AGENT_STATUS.md`
- `CAD_AGENT_CHANGELOG.md`
- 如果变更源自失败、风险或调试教训，更新 `CAD_AGENT_ISSUES.md`

每完成一个 PlanMD 开发包，还必须更新 Cursor 交接包汇总：

- `docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md`（按固定 9 项模板追加该包章节，供 Codex 校验）
- 索引说明见 `docs/handoffs/README.md`
