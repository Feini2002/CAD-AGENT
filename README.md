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

跑一遍下文 **「换机验收命令」** 中第 2 步（不碰 CAD 的部分）。全部通过说明「执行层原型」环境 OK。若失败，先读 `CAD_AGENT_BLOCKER_PLAYBOOK.md`，不要急着写新功能。

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

---

## 换机清单（环境依赖）

**最后更新：2026-05-25**

本仓库 **clone 下来只有代码和规则**，不包含 Python 虚拟环境、AutoCAD、Codex、CAD-MCP。文档里的 `$py` 路径是示例，换机后必须改成你本机真实路径。

### 口诀

```text
clone 就能写逻辑；
Windows + AutoCAD + pywin32 才能真画；
Codex + CAD-MCP 才能对话里画；
Pillow 才能舒服地做截图验收。
```

### 仓库里有什么 / 没有什么

| 在 Git 里 | 不在 Git 里（每台机器自备） |
| --- | --- |
| 规则、`CAD_PLAN` schema、示例计划 | Python 解释器 / 虚拟环境 |
| `core/` 脚本与测试 | AutoCAD 或 ZWCAD 安装 |
| 文档与 `AGENTS.md` | Codex、CAD-MCP 及 MCP 配置 |
| | pywin32、Pillow 等 Python 包 |
| | 具体项目 DWG |

`validate_plan` 只用 Python 标准库，**不强制**第三方包；落图和截图才需要额外依赖。

### 依赖分级（按你想做的事准备）

#### A 级：最低配置（改文档、schema、校验/预演、跑测试）

| 依赖 | 用途 |
| --- | --- |
| **Python 3.10+** | 跑 `scripts/`、`unittest` |
| **Git** | clone |

**不需要：** AutoCAD、Codex、CAD-MCP、Pillow。

可跑：`validate_plan`、`dry_run_plan`、`self_check`（多数项）、`unittest discover -s tests`（不连真 CAD）。

#### B 级：真机落图（`execute_plan` → AutoCAD）

| 依赖 | 用途 |
| --- | --- |
| **Windows** | COM 仅支持 Windows |
| **AutoCAD 已安装并打开** | 驱动连接 `AutoCAD.Application` → `ActiveDocument` |
| **pywin32** | `win32com.client` |

**注意：** `core/cad_io/zwcad_com.py` 目前是占位，**不能**代替 AutoCAD。Mac / Linux 可做逻辑开发，**不能**用当前 COM 驱动真画。

#### C 级：截图验收

| 依赖 | 用途 |
| --- | --- |
| **Pillow** | `PIL.ImageGrab` 全屏截图 |
| **win32gui**（建议有） | `render_preview --check` 会探测；缺失时可能 warn |

没有 Pillow：校验/预演/测试仍可做，但 `--capture-screen` 不可用。

#### D 级：Codex 对话里通过 MCP 画图

与 `execute_plan.py`（COM 脚本）是 **两条独立通路**：

| 通路 | 依赖 |
| --- | --- |
| 本仓库脚本 | Python +（落图时）B 级 |
| Codex 调 MCP | **Codex** + **CAD-MCP 服务** + CAD 已打开 |

另：若在「新家改造」整仓工作，父目录 `AGENTS.md` 会触发 CAD 规则；**只 clone 本仓库** 时，需自行把规则接到 Codex/Cursor，或把 `AGENTS.md` 放到工作区根目录。

### 换机后会不会「完全没法开发」？

| 场景 | 结果 |
| --- | --- |
| 只 clone，不装 Python | 只能看代码，不能跑脚本 |
| 有 Python，无 CAD | **可以** 做大部分开发与 13 项测试；**不能** 真机落图 |
| Windows + AutoCAD + pywin32，无 Codex | 脚本链路可完整跑通 |
| 和现机一样全配 | 与开发机一致：逻辑 + 落图 + 截图 + MCP |

**功能缺口（不是换机问题）：** 实体回读、设计大脑、ZWCAD 真驱动尚未实现，换再多机器也不会有这些能力。

### 推荐准备顺序

**必做（避免 clone 后跑不起来）**

1. `git clone https://github.com/Feini2002/CAD-AGENT.git`
2. 准备 Python，二选一：
   - **方案 A（与文档一致）：** 安装 CAD-MCP 到 `%USERPROFILE%\.codex\mcp\CAD-MCP\`，使用其 `.venv`（与 Codex MCP 配置一致）
   - **方案 B：** 在仓库根目录 `python -m venv .venv`，激活后安装：`pip install pywin32 Pillow`（仅 Windows 落图+截图需要）
3. 设置本机 Python 路径（不要照抄别人的用户名）：

```powershell
$py = 'C:\Users\你的用户名\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe'
# 或: $py = '.\.venv\Scripts\python.exe'
```

4. 在仓库根目录跑 **不依赖 CAD** 的验收（见下文「换机验收命令」）。

**要做真机落图时再加**

5. Windows + 安装 AutoCAD  
6. 打开一张 DWG，再执行 `execute_plan`  
7. 在图里确认 `CODEX_PREVIEW` 图层出现测试柜

**要用 Codex 对话画时再加**

8. 安装 Codex（或 Cursor 等）并配置 **CAD-MCP** MCP  
9. 确认 MCP 能连上、CAD 已开  
10. 用 MCP 画一次简单图，确认与脚本链路至少有一条可用

**建议随身记录（不在本 repo 里）**

| 记录项 | 原因 |
| --- | --- |
| 本机 `$py` 实际路径 | 文档示例路径会因用户名变化 |
| CAD-MCP 安装方式/版本 | 未纳入 git |
| AutoCAD 版本 | COM 行为可能略有差异 |
| 常用测试 DWG 路径 | 仓库不绑定具体项目图 |

### 换机验收命令

在仓库根目录执行；`$py` 换成你的 Python。

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe'   # 改成你的路径

# 1) 依赖探测
& $py -c "import PIL; print('Pillow', PIL.__version__)"
& $py -c "import win32com.client; print('pywin32 OK')"
& $py -c "import win32gui; print('win32gui OK')"

# 2) 不碰 CAD 的仓库自检
& $py scripts\self_check.py
& $py scripts\validate_plan.py examples\plans\draw_test_cabinet.json
& $py scripts\dry_run_plan.py examples\plans\draw_test_cabinet.json
& $py scripts\render_preview.py --check
& $py -m unittest discover -s tests

# 3) 真机 COM（需 AutoCAD 已打开；失败则只做 1)+2) 仍可开发逻辑）
& $py -c "from core.cad_io.autocad_com import AutoCADComDriver; d=AutoCADComDriver(); print('COM OK:', d.doc.Name)"

# 4) 可选：真机预览落图
& $py scripts\execute_plan.py examples\plans\draw_test_cabinet.json
```

**通过标准（参考）：**

| 命令 | 期望 |
| --- | --- |
| `self_check.py` | `"status": "pass"` |
| `validate_plan` | `VALID CAD_PLAN` |
| `render_preview --check` | `"status": "ready"`，`pillow_imagegrab: true` |
| `unittest` | `OK`（当前 13 项） |
| COM 探测 | 打印活动 DWG 文件名 |
| `execute_plan` | 图上 `CODEX_PREVIEW` 有测试柜 |

任一步失败：先读 `CAD_AGENT_BLOCKER_PLAYBOOK.md`，不要先写新功能。

### 本机参考环境（2026-05-25 实测）

在 `C:\Users\User\.codex\mcp\CAD-MCP\.venv` 上曾验证通过：

- Python 3.12.13、Pillow 12.2.0、pywin32、win32gui  
- `self_check` / validate / dry-run / unittest / `render_preview --check` / AutoCAD COM 均 OK  

新机版本不必完全一致，但上述命令应能达到同样结论。

### 换机后接新项目

1. 在 `projects/<项目名>/` 放输入输出与 `cad_context.json`  
2. 不要把具体家装/工装上下文写进本仓库通用规则  
3. 继续默认只画 `CODEX_PREVIEW`，正式图层须用户明确批准
