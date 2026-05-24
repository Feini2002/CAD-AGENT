# CAD Agent Core Lab

**English:** A portable, scenario-agnostic CAD Agent lab for Codex. It turns natural-language design intent into validated `CAD_PLAN` files, dry-runs them, and draws only to `CODEX_PREVIEW` until a human approves formal layers.

**中文：** 可迁移的通用 CAD Agent 实验仓库，面向 Codex + CAD-MCP / AutoCAD / ZWCAD。用结构化 `CAD_PLAN` 连接白话需求与可验证的预览落图，不绑定某一张家装图、某台电脑或某一个工装/家装/店铺 Agent。

Repository: [github.com/Feini2002/CAD-AGENT](https://github.com/Feini2002/CAD-AGENT)

## 设计主线

```text
大通用 CAD 底座优先
场景 Agent 轻量化
真实项目作为验证样本
```

CAD-MCP / AutoCAD / ZWCAD 是执行工具，`CAD_PLAN` 是最终落图指令。仓库要沉淀的是：白话理解、图纸理解、项目模型、对象与风格、图库块、布局、方案、执行、安全和验证。

## 恢复上下文

每次回来先读：

1. `CORE_STATUS.md` — 通用底座开发进度
2. `CORE_ROADMAP.md` — Core 阶段路线
3. `CORE_RESTRUCTURE_PLAN.md` — 大重装架构与剩余工作
4. `CAD_AGENT_STATUS.md` — 历史进展与迁移状态
5. `CAD_AGENT_RULES.md` 和 `AGENTS.md` — 长期规则与绘图自检门槛
6. `CAD_AGENT_CHANGELOG.md`、`CAD_AGENT_ISSUES.md` — 变更与问题记录

## 目录结构

```text
core/       通用 CAD Agent 底座：读图、模型、对象、风格、布局、计划、执行、验证、安全
agents/     轻量场景 Agent：场景词汇、默认偏好、专用 workflow，不复制 Core
libraries/  跨场景资源：块、对象、风格、材料、尺寸、人体工学、图层标准
projects/   真实或样例项目输入输出，不污染通用规则
scripts/    兼容旧命令的薄包装器，实现已迁入 core/
drivers/    兼容旧导入的薄包装器，驱动已迁入 core/cad_io/
schemas/    过渡期 schema 兼容副本，正式 schema 进入 core/schemas/
tests/      Core 与 Agent 测试
docs/       架构、决策、路线与历史文档
skills/     Codex CAD skill 草稿，逐步对齐 Core 架构
```

## 当前能力（prototype / scaffold）

| 能力 | 状态 | 入口 |
| --- | --- | --- |
| CAD_PLAN 校验 | prototype | `scripts/validate_plan.py` / `core.plan_engine.validate_plan` |
| CAD_PLAN 预演 | prototype | `scripts/dry_run_plan.py` / `core.plan_engine.dry_run_plan` |
| 预览落图 | prototype | `scripts/execute_plan.py` → `CODEX_PREVIEW` |
| 环境自检 | prototype | `scripts/self_check.py` |
| 截图能力检查 | prototype | `scripts/render_preview.py --check` |
| 场景 Agent | scaffold | `agents/*`（工装、家装、办公、餐饮、展陈、自定义） |
| 设计大脑（读图/对象/布局/方案） | not_started | 见 `CORE_STATUS.md` |

## 快速开始

前置：本机已安装 Codex、CAD 软件、CAD-MCP 虚拟环境 Python，且 AutoCAD COM 可用（当前验证环境）。

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe'

& $py 'scripts\validate_plan.py' 'examples\plans\draw_test_cabinet.json'
& $py 'scripts\dry_run_plan.py' 'examples\plans\draw_test_cabinet.json'
& $py 'scripts\self_check.py'
& $py 'scripts\render_preview.py' --check
& $py -m unittest discover -s tests
```

新 Core 入口示例：

```powershell
& $py -m core.plan_engine.validate_plan 'examples\plans\draw_test_cabinet.json'
```

## 安全原则

- 默认只画到 `CODEX_PREVIEW`
- 不默认保存当前 DWG，不覆盖原始 DWG，不删除已有实体
- 不修改正式图层，除非用户明确批准
- 白话需求必须先变成 `CAD_PLAN` 或更高层结构化意图，再校验、dry-run、执行
- 声称“画准了”之前必须有截图或实体回读证据（见 `AGENTS.md`、`CAD_AGENT_BLOCKER_PLAYBOOK.md`）

## 防跑偏规则

新增能力前先判断：

```text
两个以上场景会复用  -> core/
只有一个场景会用      -> agents/<scenario>/
跨场景资源            -> libraries/
真实项目资料          -> projects/
架构/路线/决策        -> docs/
```

不要把仓库改成工装专用 Agent，也不要把通用能力写死到某个场景 Agent。

## 迁移到新电脑

复制本仓库后检查：

1. CAD 软件与 Codex 可读本目录
2. CAD-MCP / AutoCAD COM / Python 可用
3. `draw_test_cabinet.json` 能通过 validate 与 dry-run
4. 需要真实落图时再接入具体项目 DWG，并创建项目级 `cad_context.json`
