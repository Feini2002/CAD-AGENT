# CAD Agent Core Lab

可迁移的通用 CAD Agent 实验仓库，面向 Codex + CAD-MCP / AutoCAD / ZWCAD。用结构化 `CAD_PLAN` 连接白话需求与可验证的预览落图，不绑定某一张家装图、某台电脑，也不等同于某一个工装/家装/店铺 Agent。

GitHub：[github.com/Feini2002/CAD-AGENT](https://github.com/Feini2002/CAD-AGENT)

## 设计主线

```text
大通用 CAD 底座优先
场景 Agent 轻量化
真实项目作为验证样本
```

CAD-MCP / AutoCAD / ZWCAD 是执行工具，`CAD_PLAN` 是最终落图指令。仓库要沉淀的是：白话理解、图纸理解、项目模型、对象与风格、图库块、布局、方案、执行、安全和验证。

---

## Clone 后先看这里：开发到哪了、从哪动手

**最后更新：2026-05-25**

### 一句话结论

**阶段 1 已完成**：仓库已从「零散脚本包」重装成「Core Lab」目录结构；**执行链路的早期原型能跑**（校验 → 预演 → 预览落图 → 自检），但 **设计大脑几乎还没做**——读图、项目模型、参数化对象、布局、方案说明、实体回读都未开工或仅有占位。

可以把它理解成：**外壳和流水线搭好了，脑子还没长出来。**

### 已完成（能直接用）

| 项目 | 说明 |
| --- | --- |
| 目录重装 | `core/`、`agents/`、`libraries/`、`projects/`、`docs/` 等结构已建立 |
| CAD_PLAN 校验 / 预演 | `validate_plan`、`dry_run_plan`，测试柜 `examples/plans/draw_test_cabinet.json` 已验证 |
| 预览落图 | `execute_plan` 可把测试柜画到 `CODEX_PREVIEW`（AutoCAD COM） |
| 环境自检 | `self_check.py` 不碰 DWG 即可检查文件、示例计划、工具链 |
| 截图检查 | `render_preview.py --check` 可检查截图能力 |
| 规则固化 | `AGENTS.md`、`CAD_AGENT_RULES.md`、`CAD_AGENT_BLOCKER_PLAYBOOK.md` |
| 场景 Agent 脚手架 | 工装/家装/办公/餐饮/展陈/自定义 六个目录，**只有占位，无业务逻辑** |
| 兼容层 | 旧 `scripts/`、`drivers/` 仍可用，真实实现已在 `core/` |
| 测试 | `python -m unittest discover -s tests` 当前 13 项通过 |

### 未完成（别误以为已经有了）

| 项目 | 状态 | 说明 |
| --- | --- | --- |
| 实体回读 `entity readback` | 未开始 | 还不能用 CAD 实体坐标证明「画准了」 |
| 高层 schema | 占位 | `DESIGN_BRIEF`、`DRAWING_MODEL`、`PROJECT_MODEL` 等尚未建立 |
| 设计大脑 | 未开始 | `drawing_model`、`object_engine`、`layout_engine`、`proposal_engine` 等 |
| `core/safety` | 占位 | 安全规则仍在文档里，未收成可测试模块 |
| 场景 Agent 业务 | 占位 | `agents/*` 不要扩写，等 Core 可复用后再补差异 |
| 遗留目录收束 | 待第二轮 | `cad_agent/`、`libraries/domains/` 仍保留 |

### Clone 后推荐动手顺序

**第 0 步：确认环境（约 10 分钟）**

```powershell
# 在仓库根目录执行
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe'   # 按你本机路径改

& $py scripts\self_check.py
& $py scripts\validate_plan.py examples\plans\draw_test_cabinet.json
& $py scripts\dry_run_plan.py examples\plans\draw_test_cabinet.json
& $py -m unittest discover -s tests
```

以上全部通过，说明「执行层原型」环境 OK。若失败，先读 `CAD_AGENT_BLOCKER_PLAYBOOK.md`，不要急着写新功能。

**第 1 步：恢复上下文（约 5 分钟阅读）**

按顺序扫一遍：

1. 本文「Clone 后先看这里」
2. `CORE_STATUS.md` — 能力矩阵（最细）
3. `CAD_AGENT_STATUS.md` — 变更历史与已验证命令
4. `CORE_RESTRUCTURE_PLAN.md` — **还没做什么**（剩余工作清单）
5. `AGENTS.md` — Codex 绘图时必须遵守的规则

**第 2 步：选一条开发主线（二选一，不要并行铺太开）**

| 路线 | 适合做什么 | 建议入口文件 |
| --- | --- | --- |
| **A. 实体回读** | 让「画准了」有证据，补验证闭环 | `core/verification/inspect_dwg.py`、`scripts/inspect_dwg.py` |
| **B. 高层数据模型** | 从 `CAD_PLAN` 往上长设计大脑 | `core/schemas/`，新建 `DESIGN_BRIEF` / `DRAWING_MODEL` 等 schema |

仓库当前瓶颈是：**没有回读 = 无法证明几何正确**；**没有高层模型 = 只能从白话硬写 CAD_PLAN**。你更急哪边就先走哪条。

**第 3 步：暂不要做的事**

- 不要先扩写 `agents/commercial_fitout` 或 `agents/residential` 的业务规则
- 不要默认画正式图层或保存 DWG
- 不要把具体家装项目上下文写进根目录规则

### 阶段对照（方便你对齐路线图）

```text
阶段 0  架构冻结              done
阶段 1  仓库重装 + 执行原型    done（prototype）
阶段 2  Core 状态看板          scaffold（CORE_STATUS 已有，持续更新）
阶段 3+ 数据模型 / 读图 / 对象 / 布局 / 方案   not_started 或 scaffold
```

详细阶段划分见 `CORE_ROADMAP.md`。

### 问 Codex 恢复进度时可以这样说

```text
读取本仓库 README 和 CORE_STATUS.md，告诉我 CAD Agent 开发到哪一步了，下一步建议做什么。
```

---

## 恢复上下文（日常开发）

每次回来先读：

1. `CORE_STATUS.md` — 通用底座开发进度
2. `CORE_ROADMAP.md` — Core 阶段路线
3. `CORE_RESTRUCTURE_PLAN.md` — 剩余工作（不是已完成清单）
4. `CAD_AGENT_STATUS.md` — 历史进展与迁移状态
5. `CAD_AGENT_RULES.md`、`AGENTS.md` — 长期规则与绘图自检门槛
6. `CAD_AGENT_CHANGELOG.md`、`CAD_AGENT_ISSUES.md` — 变更与问题记录

## 目录结构

```text
core/       通用底座：读图、模型、对象、风格、布局、计划、执行、验证、安全
agents/     轻量场景 Agent（仅差异，不复制 Core）
libraries/  跨场景资源：块、风格、材料、尺寸、图层标准等
projects/   真实或样例项目资料
scripts/    旧命令兼容包装器 → 实现在 core/
drivers/    旧导入兼容包装器 → 实现在 core/cad_io/
schemas/    过渡期 schema 副本
tests/      Core 与 Agent 测试
docs/       架构、决策、路线
skills/     Codex CAD skill 草稿
```

## 常用命令

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe'

& $py scripts\validate_plan.py examples\plans\draw_test_cabinet.json
& $py scripts\dry_run_plan.py examples\plans\draw_test_cabinet.json
& $py scripts\execute_plan.py examples\plans\draw_test_cabinet.json   # 需 CAD 已打开
& $py scripts\self_check.py
& $py scripts\render_preview.py --check
& $py -m unittest discover -s tests

# 新 Core 入口
& $py -m core.plan_engine.validate_plan examples\plans\draw_test_cabinet.json
```

## 安全原则

- 默认只画到 `CODEX_PREVIEW`
- 不默认保存当前 DWG，不覆盖原始 DWG，不删除已有实体
- 不修改正式图层，除非用户明确批准
- 白话需求必须先变成 `CAD_PLAN` 或更高层结构化意图，再校验、预演、执行
- 声称「画准了」之前必须有截图或实体回读（见 `AGENTS.md`、`CAD_AGENT_BLOCKER_PLAYBOOK.md`）

## 防跑偏

```text
两个以上场景会复用  -> core/
只有一个场景会用      -> agents/<scenario>/
跨场景资源            -> libraries/
真实项目资料          -> projects/
架构/路线/决策        -> docs/
```

不要把仓库改成工装专用 Agent，也不要把通用能力写死到某个场景 Agent。

## 换电脑 / 新项目

1. `git clone` 本仓库
2. 安装 Codex、CAD、CAD-MCP，确认 `$py` 路径
3. 跑一遍「Clone 后推荐动手顺序」第 0 步
4. 接入具体 DWG 时，在 `projects/<项目名>/` 放 `cad_context.json`，不要把项目上下文写进通用规则
