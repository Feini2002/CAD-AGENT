# CAD Agent Core Lab

## 系统简介

CAD Agent Core Lab 是一个可迁移的通用 CAD Agent 开发包，用结构化 `CAD_PLAN` 连接自然语言需求、设计模型、CAD 执行和可验证结果。它不绑定某一张 DWG、某一套家装图纸或某一台电脑，也不把工装、家装、办公等场景写成彼此割裂的独立系统。

核心方向是：

- `core/` 沉淀通用能力：读图、模型、对象、风格、布局、计划、执行、验证和安全边界。
- `agents/<scenario>/` 只保留轻量场景差异，复用 Core，不复制 Core 算法。
- `libraries/` 存放跨场景资源，例如对象默认值、块库、风格、材料、尺寸和图层标准。
- `projects/` 存放真实或样例项目资料。
- `docs/` 存放架构、计划、治理、交接、验证、决策和历史记录；Cursor 按包交付见 [`docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md`](docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md)。

仓库的绘图原则是先把白话需求转成 `CAD_PLAN` 或更高层结构化意图，再做校验、dry-run、执行和回读验证。真实 CAD 输出默认只落到 `CODEX_PREVIEW`，不默认保存 DWG，不覆盖原始文件，不删除已有实体，不修改正式图层。

## 开发状况

当前仓库已经完成 Phase O-V 非 CAD 主线、系统层安全补强，以及 blank-shell pipeline 的第一轮落地。主链路已经跑通：

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
-> VERIFICATION_REPORT
```

最新稳定结论：

- 当前唯一 `PlanMD` / 开发主线是 `CORE_RESTRUCTURE_PLAN.md`。
- `CORE_CONTEXT_BRIEF.md` 是日常恢复上下文的短入口。
- `docs/planning/phase-*.md` 是 Phase 执行剧本，不是第二套主计划；后置 Backlog 和未来小包只看 `CORE_RESTRUCTURE_PLAN.md`。
- `core.plan_engine`、benchmark runner、composition engine、CAD validation runner 已进入可运行原型状态。
- blank-shell benchmark、office alpha benchmark、interior delivery benchmark 已有可重复运行的用例。
- 真实 CAD 验证已覆盖 baseline、基础图元能力探针和 3 个简单 interior composition cases，并取得 `geometry_verified` 证据。

仍需注意：这些验证不能扩大解释为真实项目图纸、块库、块插入或任意 `CAD_PLAN` 都已经准确。当前系统是 Core Alpha 原型，不是完整自动设计大脑。

## 交付进度规则

后续每次 CAD Agent 相关交付，最终回复默认用 **1 张精简进度表** 汇报，第一行先报 **表 C 真实 CAD 实力主指标**；完整表 A/B/C 只在状态汇报、交接、审计、进度盘点或表 C 专题时展开。格式以 `AGENTS.md`「交付默认精简进度」为准。

- **默认轻量表**：表 C 主指标、本轮进展 / 验证、表 A 折叠工程节奏、表 B 本轮相关中文轨道（能力证明 / 代码轨 / CAD 补验）。
- **表 A — 工程节奏**：总进度、Core 底座开发进度、Agent 多场景实现进度（默认 Core 70% + Agent 30%）。
- **表 B — 任务清单三指令执行进度**：能力证明（§3）、一键推进 / 代码轨（§4）、**RCAD 烟囱包**（§5）；计数见 `docs/planning/任务清单.md` §0。
- **表 C — 真实 CAD 实力**：登记表 Ladder 加权 + L3+ 片段 + showcase 门；机器值见 `scripts/run_capability_coverage.py`。
- **用户口令**：`一键推进`（§4）、`能力证明`（§3）、`CAD 补验`（§5）、**`真实 CAD 实力` / `推进表 C`**（§0.1 编排表 C）；详见 `docs/planning/任务清单.md` §0。

表 A、表 B、表 C 不是同一套数，禁止混用。估算口径见 `CAD_AGENT_RULES.md` §0.4。百分比不替代 created handles 回读、`geometry_verified` 与关键 checks。

## 继续开发入口

README 只做入口说明，不维护独立后续计划。实际优先级、Decision Gate 和退出标准看 `CORE_RESTRUCTURE_PLAN.md`；三指令执行台账、包计数和当前 `next` 看 `docs/planning/任务清单.md` §0。
