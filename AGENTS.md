# CAD Agent 规则

本目录是可迁移的 CAD Agent 开发包，不绑定某一张 DWG、某一套家装图纸或某一台电脑。

本仓库的规则、训练链路和交接材料面向 Codex、Cursor 及其它同类 agent 工具通用；不得把开发流程强制绑定到某一个软件。文档中如出现 Codex / Cursor 名称，应理解为可选载体或历史文件名，除非上下文明确是在描述该工具专属能力。

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
3. `docs/roadmap/current.md`
4. `CORE_RESTRUCTURE_PLAN.md`
5. `docs/status/current.md`
6. `docs/governance/cad-agent-rules.md`
7. `docs/runbooks/blocker-playbook.md`
8. `docs/status/changelog.md`
9. `docs/status/issues.md`

## 单一 PlanMD 开发主线

当前唯一 `PlanMD` / 开发主线是 `CORE_RESTRUCTURE_PLAN.md`。根目录没有独立 `plan.md`；用户提到 `PlanMD`、`plan.md`、主计划或主 plan 时，默认指 `CORE_RESTRUCTURE_PLAN.md`。

- `PlanMD` 只做文档治理和开发排序，不改变本仓库“通用 CAD Agent Core Lab”的方向。
- `CORE_RESTRUCTURE_PLAN.md` 决定当前活跃工作队列、Phase 顺序、优先级、Decision Gate 和退出标准。
- `docs/planning/phases/*.md` 只是辅助执行剧本，可以写命令和检查表，但不能成为第二套主计划，也不能保留后置 Backlog 副本。
- `CORE_STATUS.md`、`docs/status/current.md` 只写能力、证据、风险和当前状态，不承载独立下一步。
- 新增待办、调整优先级、改变退出标准或拆分未来小包时，先同步 `CORE_RESTRUCTURE_PLAN.md`，再更新辅助 MD 的引用或状态说明。
- 若文档整理和 Core 优先、`CAD_PLAN` 中间层、真实 CAD 验证门槛或场景轻量化发生冲突，必须以这些根边界为准。

## 交付默认简洁回复

面向用户的最终回复默认**不要附进度表、表单或表 A/B/C**。普通开发、调查、修复、绘图或规则更新完成后，用简洁自然段说明：本轮做了什么、关键证据、有没有风险或未验证项。

只有用户明确点名 **开发状态查询 / 进度 / 完整状态 / 交接 / 审计 / 表 A / 表 B / 表 C / 真实 CAD 实力 / 刷新表 C / 报进度表** 时，才使用进度表格；其中涉及真实 CAD 能力时，必须先报 **表 C 真实 CAD 实力主指标**。详细口径见 `docs/governance/cad-agent-rules.md` §0.4；任务包计数与 next 以 `docs/planning/任务清单.md` §0 为准。

**Agent 训练期例外（方案 A）：** 当 `docs/training/README.md` 所指的 **Agent 训练**（任意场景案例 `projects/<case_id>/`、`开一轮训练`、用户未点名表 C/A/B）时，最终回复同样不要附进度表或表 A/B/C；只汇报案例进展、CAD 证据路径与待你验收项。落图工序必须遵循该文档 **「理想链路（全局 · 训练期）」**（机器审计 → 截图 → Agent 自检 → 未过则自修，再请你验收）。

**展开条件：** 遇到下列情况，才展开完整 **表 A / 表 B / 表 C**；其中用户问「真实 CAD 实力 / 推进表 C / 表 C / 刷新表 C」时，必须先展开完整表 C。

- 用户要求完整状态汇报、交接、审计、进度盘点或对比。
- 完成或更新能力证明、代码轨、CAD 补验包，并改变 `docs/planning/任务清单.md` §0 的计数或 next。
- 修改 `cad_capability_registry`、showcase、coverage JSON，或需要解释真实 CAD 能力瓶颈。
- 出现回归、绘图不准、口径漂移，或用户质疑“能不能画准”。

**完整口径定义：**

- **表 A — 工程节奏**：总进度、Core 底座开发进度、Agent 多场景实现进度；默认 `总进度 = Core × 70% + Agent × 30%`，允许约 5–10 个百分点主观误差。
- **表 B — 任务清单三指令执行进度**：§3 能力证明、§4 一键推进 / 代码轨、§5 RCAD 烟囱包；`执行进度 ≈ status=done 包数 ÷ 本板块任务包总量`，§5 使用 `cad_status=verified` 包数。
- **表 C — 真实 CAD 实力**：`scripts/run_capability_coverage.py` 的机器值，包括 `cad_proof_coverage_percent`、`cad_strength_index_percent`、`scene_fragment_strength_percent`、`showcase_readiness_percent`、`cad_strength_headline_percent` 和最高已证 Ladder。

**禁止混用：**

- 表 A 的「工程完备度 / 工程节奏」≠ 表 B 的「台账包完成度」≠ 表 C 的「真实 CAD 实力」。
- 表 B 的 RCAD 烟囱通过 ≠ `cad_capability_registry` 已满 `verified`，也不等于“已经能画准施工图”。
- 普通回复可以不附表 C 数字，但只要进入开发状态查询、真实 CAD 能力汇报或表格口径，就不得省略表 C 主指标；任何时候都不得用 Core 进度、RCAD 高完成度、截图、dry-run 或 no-CAD benchmark 暗示真实 CAD 几何已证明。
- 各表百分比均不替代测试、benchmark、截图、created handles 回读或 `geometry_verified` 证据。

完成能力证明 / 代码轨 / CAD 补验相关包后，应同步更新 `docs/planning/任务清单.md` §0 的计数与 next；改登记表或 showcase 后须复跑 `run_capability_coverage.py` 并更新表 C。

**用户口令（§0 四指令，详见 `docs/planning/任务清单.md`）**

| 用户说 | Agent 默认动作 |
| --- | --- |
| **一键推进** | §4 代码轨 1 包 |
| **能力证明** / **覆盖率** | §3 `V-PROOF` 1 包 |
| **CAD 补验** / **开 CAD 了** | §5 `RCAD` 1 包（真实 CAD） |
| **真实 CAD 实力** / **推进表 C** / **表 C** | §0.1：优先抬高表 C 的 1 个 `V-PROOF` + 链式 RCAD + registry 回写 + 复跑 coverage；**先报表 C** |
| **刷新表 C** | 仅 `run_capability_coverage.py` + 汇报表 C，不新开包 |

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
- `scripts/render_preview.py --capture-autocad-window`（必要时加 `--execution-summary`）截图；**默认保留 CAD/IDE 分屏**，仅 COM 重取景 + `PrintWindow`；PrintWindow 失败时才 `--force-foreground`。整屏 `--capture-screen` 仅作 fallback
- 实际输出与预期 `CAD_PLAN` 或结构化意图的对比

如果实际输出和预期不一致，Codex 不得把错误结果当成完成品交给用户。必须诊断差异，做最小安全修复，重新绘制或运行，并再次验证。

## 卡壳或绘图不准流程

当用户说“画不准”“画不出来”“不对”“继续修”，或 Codex 无法证明图纸准确时，按 `docs/runbooks/blocker-playbook.md` 执行。

最低必跑探针：

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py 'scripts\self_check.py'
& $py 'scripts\render_preview.py' --check
```

如果需要视觉证据且用户没有禁止截图，保存一个检查点：

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py 'scripts\render_preview.py' --capture-autocad-window --output 'output\previews\manual-check.png'
```

如果截图或回读不可用，应说明暂时无法证明准确性，并优先补齐缺失的验证机制，再声称完成。

## 保护用户 DWG

- 默认使用 `CODEX_PREVIEW`。
- 默认不保存当前 DWG。
- 不覆盖原始 DWG 文件。
- 未经用户明确批准，不修改正式图层、不删除实体、不执行不可逆 CAD 操作。

## 保持记录更新

当 CAD Agent 规则、脚本、测试、工作流文档或状态发生变化时，更新：

- `docs/status/current.md`
- `docs/status/changelog.md`
- 如果变更源自失败、风险或调试教训，更新 `docs/status/issues.md`

每完成一个 PlanMD 开发包，还必须更新 Agent 交接包汇总：

- `docs/handoffs/current.md`（按固定 9 项模板追加该包章节，供 Codex 校验）
- `docs/handoffs/package-index.md`（同步全量包索引）
- 索引说明见 `docs/handoffs/README.md`
