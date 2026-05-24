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

**第 0 步：确认环境（约 30 分钟）**

按下文 **「换机清单（与本机同等级，全量配置）」** 完成全量安装，并跑通 **全部** 验收命令（含 AutoCAD 已开、COM、`execute_plan`、截图、CAD-MCP 对话画图）。任一项未通过则不算环境就绪。

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

## 换机清单（与本机同等级，全量配置）

**最后更新：2026-05-25**

本文只描述 **与本机开发环境同等、百分百对齐** 的换机方式：不接受「最低配置」「仅逻辑开发」「暂不装 CAD」等缩水方案。少装任何一项，都不算换机完成。

本仓库 clone 下来 **只有代码和规则**；下列组件必须在新电脑上 **全部** 自备并验收通过。

### 仓库里有什么 / 没有什么

| 在 Git 里 | 必须在新机单独安装 |
| --- | --- |
| 规则、`CAD_PLAN` schema、示例计划 | **Windows** |
| `core/` 脚本与测试 | **AutoCAD**（当前驱动仅 COM，不用 ZWCAD 占位） |
| 本目录 `AGENTS.md` | **Codex 或 Cursor** + **CAD-MCP**（MCP 已启用） |
| | **CAD-MCP 虚拟环境**（固定用作 `$py`） |
| | **pywin32、Pillow、win32gui**（在 CAD-MCP `.venv` 内） |
| | 工作区根目录 **CAD 触发规则**（见下） |
| | 用于测试的 **已打开 DWG** |

### 全量组件对照表（开发机标准）

| # | 组件 | 要求 | 用途 |
| --- | --- | --- | --- |
| 1 | 操作系统 | **Windows 10/11** | AutoCAD COM 仅 Windows |
| 2 | Git | 已安装 | clone 本仓库 |
| 3 | AutoCAD | 已安装，换机验收时 **必须已打开** 一张 DWG | `execute_plan`、COM 探测、MCP 落图 |
| 4 | CAD-MCP | 安装到 `%USERPROFILE%\.codex\mcp\CAD-MCP\` | Codex/Cursor 调 CAD；提供统一 Python |
| 5 | CAD-MCP `.venv` | 使用其 `Scripts\python.exe` 作为 **唯一** `$py` | 所有 `scripts/`、`unittest`、Core 模块 |
| 6 | Python 包 | **pywin32**、**Pillow**、**win32gui** 均可 import | COM 落图 + 全屏截图验收 |
| 7 | Codex / Cursor | 已安装，MCP 配置指向 CAD-MCP | 对话里画图、读规则 |
| 8 | 工作区规则 | 父目录有 `AGENTS.md` 触发 CAD 任务（见安装顺序） | 与「新家改造」整仓行为一致 |
| 9 | 本仓库 | `git clone` 后在仓库根目录操作 | 开发主体 |

**两条落图通路都必须通**（与本机一致，不是二选一）：

| 通路 | 验收方式 |
| --- | --- |
| 脚本链 | `execute_plan.py` → AutoCAD COM → `CODEX_PREVIEW` |
| MCP 链 | Codex/Cursor 调 CAD-MCP，在已打开 DWG 里能画简单实体 |

**不是换机清单、但本机也尚未具备的能力：** 实体回读、设计大脑、`zwcad_com` 真驱动——换机全配也不会自动拥有，属于后续开发项。

### 开发机参考版本（2026-05-25 实测通过）

新机请尽量对齐；至少应能通过下文 **全部** 验收命令且结果一致。

| 项目 | 开发机实测 |
| --- | --- |
| Python | 3.12.13（`CAD-MCP\.venv`） |
| Pillow | 12.2.0 |
| pywin32 / win32gui | 正常 import |
| AutoCAD | COM 已连上活动图纸 |
| 单元测试 | `unittest discover -s tests` → 13 passed |

### 全量安装顺序（按序执行，不可跳步）

1. **Windows** 电脑就绪。  
2. 安装 **Git**，clone 本仓库：

   ```powershell
   git clone https://github.com/Feini2002/CAD-AGENT.git
   cd CAD-AGENT
   ```

3. 安装 **AutoCAD**（与开发机同系列版本更稳，至少能 COM 连接）。  
4. 安装 **CAD-MCP** 到 `%USERPROFILE%\.codex\mcp\CAD-MCP\`，创建/修复其 `.venv`，并安装依赖（含 `pywin32`；另需 **Pillow**，开发机 venv 中已存在，新机若缺则 `pip install Pillow`）。  
5. 安装 **Codex** 或 **Cursor**，在 MCP 设置中 **启用 CAD-MCP**（与开发机相同配置）。  
6. **工作区规则（与「新家改造」整仓一致时）：**  
   - 要么：把本仓库放在有根目录 `AGENTS.md` 的父工作区下（父 `AGENTS.md` 会指向 `CAD测试相关文件/` 或 clone 后的本目录）；  
   - 要么：在 Cursor/Codex 工作区根单独放置等效的 CAD 触发 `AGENTS.md` + 本仓库内 `AGENTS.md` 均可被读到。  
7. 设置 `$py`（**只**用 CAD-MCP 的 venv，不要用系统 Python 或其它 venv 凑合）：

   ```powershell
   $py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
   ```

8. **打开 AutoCAD** 并加载一张测试用 DWG（保持为活动文档）。  
9. 在仓库根目录执行下文 **全量验收命令**，**每一项都必须通过**。  
10. 在 Codex/Cursor 里用 **CAD-MCP** 画一次简单图（矩形/直线即可），确认 MCP 链路与脚本链都可用。

### 全量验收命令（全部必跑，全部必须通过）

在仓库根目录执行。`$py` 必须指向 CAD-MCP 的 `.venv`。

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"

# 1) Python 与关键依赖（缺任一项即未达标）
& $py -c "import sys; print('Python', sys.version)"
& $py -c "import PIL; print('Pillow', PIL.__version__)"
& $py -c "import win32com.client; print('pywin32 OK')"
& $py -c "import win32gui; print('win32gui OK')"

# 2) 仓库自检与计划链路
& $py scripts\self_check.py
& $py scripts\validate_plan.py examples\plans\draw_test_cabinet.json
& $py scripts\dry_run_plan.py examples\plans\draw_test_cabinet.json
& $py scripts\render_preview.py --check
& $py -m unittest discover -s tests

# 3) AutoCAD COM（必须先打开 DWG）
& $py -c "from core.cad_io.autocad_com import AutoCADComDriver; d=AutoCADComDriver(); print('COM OK:', d.doc.Name)"

# 4) 真机预览落图（必须执行，不是可选项）
& $py scripts\execute_plan.py examples\plans\draw_test_cabinet.json

# 5) 截图（必须能落盘）
& $py scripts\render_preview.py --capture-screen --output output\previews\migration-check.png
```

### 通过标准（缺一即视为换机未完成）

| 步骤 | 期望结果 |
| --- | --- |
| Pillow / pywin32 / win32gui | 打印版本或 `OK`，无 ImportError |
| `self_check.py` | JSON 中 `"status": "pass"` |
| `validate_plan` | 输出 `VALID CAD_PLAN` |
| `dry_run_plan` | 正常预演输出 |
| `render_preview --check` | `"status": "ready"`，且 `pillow_imagegrab: true` |
| `unittest` | `OK`，13 tests |
| COM 探测 | 打印当前活动 DWG 文件名 |
| `execute_plan` | 图上出现 `CODEX_PREVIEW` 测试柜 |
| `--capture-screen` | 生成 `output\previews\migration-check.png` |
| **CAD-MCP 对话画图** | 在 IDE 里手动确认一次成功 |

任一步失败：**先读 `CAD_AGENT_BLOCKER_PLAYBOOK.md`**，修到与本机同级再开发；不要用「先写代码以后再配环境」的方式凑合。

### 换机时建议随身带的记录

| 记录项 | 说明 |
| --- | --- |
| AutoCAD 版本号 | COM 行为可能因版本略有差异 |
| CAD-MCP 安装来源 / commit | 不在本 repo 内 |
| Cursor / Codex 的 MCP 配置截图或导出 | 避免 MCP 未启用 |
| 父工作区 `AGENTS.md` 是否就位 | 影响是否自动读 CAD 规则 |
| 常用测试 DWG | 仓库不附带项目图 |

### 换机后接新项目

1. 在 `projects/<项目名>/` 放输入输出与 `cad_context.json`。  
2. 不要把具体家装/工装上下文写进本仓库通用规则。  
3. 继续默认只画 `CODEX_PREVIEW`；正式图层须用户明确批准。
