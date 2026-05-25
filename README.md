# CAD Agent Core Lab

可迁移的通用 CAD Agent 实验仓库，面向 Codex + CAD-MCP / AutoCAD / ZWCAD。用结构化 `CAD_PLAN` 连接白话需求与可验证的预览落图，不绑定某一张家装图、某台电脑，也不等同于某一个工装/家装/店铺 Agent。

GitHub：[github.com/Feini2002/CAD-AGENT](https://github.com/Feini2002/CAD-AGENT)

## 提交与推送说明

本目录应作为独立 Git 仓库维护，远端默认使用：

```powershell
git remote add origin https://github.com/Feini2002/CAD-AGENT.git
```

如果目录是从工作区拷贝来的、没有 `.git`，先初始化再提交：

```powershell
git init
git branch -M main
git add .
git commit -m "docs: refresh CAD Agent core lab"
git push -u origin main
```

提交前不要把本机运行日志、截图、验证输出、`__pycache__` 或临时 DWG 文件放进版本库；这些应由 `.gitignore` 排除。真实项目资料放在 `projects/`，但不得包含用户未确认可公开的原始 DWG。

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

**阶段 2 已深度推进**：仓库已从「零散脚本包」重装成「Core Lab」目录结构；非 CAD 底座已有一条可运行闭环（brief / drawing / preferences → project → object / layout / proposal → CAD_PLAN → dry-run report → unverified verification report）。本轮新增 safety policy、project builder、model loop 引用检查、手工 drawing model、block selector/placement、多对象 layout、model_to_plan、created handles 证据门、场景 preferences，以及能力目录/runtime、artifact graph、geometry backend 抽象、benchmark runner、对象解释和候选比较。真实 CAD 落图、截图和实体回读仍需等 CAD 环境恢复后统一补验。

最近复验（2026-05-25 15:17）：165 tests OK，`self_check.py` pass，`render_preview.py --check` ready，blank-shell pipeline ok，4 场景 blank-shell benchmark pass，`run_cad_validation.py --no-cad` pass。该结果只证明非 CAD 链路和无 CAD 验证总控可用，不证明真实 CAD 几何准确。

### 已完成（能直接用）

| 项目 | 说明 |
| --- | --- |
| 目录重装 | `core/`、`agents/`、`libraries/`、`projects/`、`docs/` 等结构已建立 |
| CAD_PLAN 校验 / 预演 | `validate_plan`、`dry_run_plan`，测试柜 `examples/plans/draw_test_cabinet.json` 已验证 |
| 预览落图 | `execute_plan` 可把测试柜画到 `CODEX_PREVIEW`（AutoCAD COM） |
| 环境自检 | `self_check.py` 不碰 DWG 即可检查文件、示例计划、工具链 |
| 截图检查 | `render_preview.py --check` 可检查截图能力 |
| 规则固化 | `AGENTS.md`、`CAD_AGENT_RULES.md`、`CAD_AGENT_BLOCKER_PLAYBOOK.md` |
| 场景 Agent 脚手架 | 工装/家装/办公/餐饮/展陈/自定义 六个目录，已补商业/住宅/办公/餐饮 preferences；仍只做轻量差异 |
| 兼容层 | 旧 `scripts/`、`drivers/` 仍可用，真实实现已在 `core/` |
| 测试 | `python -m unittest discover -s tests` 当前 165 项通过 |
| 高层 schema | `DESIGN_BRIEF`、`DRAWING_MODEL`、`PROJECT_MODEL`、`OBJECT_SPEC`、`STYLE_PROFILE`、`BLOCK_LIBRARY`、`LAYOUT_PROPOSAL`、`DESIGN_PROPOSAL`、`VERIFICATION_REPORT` 已有最小 schema 与 example |
| 验证报告 | `core/verification/verification_report.py` 能区分已执行、已截图、几何验证、失败和未验证；缺 created handles 或截图文件不存在时不升级证据状态 |
| 非 CAD pipeline | `scripts/run_non_cad_pipeline.py` 可生成 project/object/layout/proposal/CAD_PLAN/dry-run/verification artifacts |
| 非 CAD benchmark | `scripts/run_benchmark_suite.py` 可重复运行 minimal benchmark 与 4 case blank-shell benchmark 并输出 pass/fail 汇总 |
| 状态短入口 | `CORE_CONTEXT_BRIEF.md` 作为日常恢复入口，主计划仍为 `CORE_RESTRUCTURE_PLAN.md`（用户说 `plan.md` 时默认指它） |
| 设计引擎原型 | object/style/block/layout/proposal/plan 第一批 Core 原型已建立 |

### 未完成（别误以为已经有了）

| 项目 | 状态 | 说明 |
| --- | --- | --- |
| 实体回读 `entity readback` | 原型 | 有 COM-like 实体标准化、created handles 摘要入口和 `--connect-cad` 显式入口，但真实 AutoCAD 回读还需实机验证 |
| 高层 schema | 原型 | 9 个高层 schema、examples、workflow 引用检查已建立，后续要扩展反例 fixture 和职责边界测试 |
| 设计大脑 | 原型 | object/style/block/layout/proposal/plan 已有第一批实现，尚未覆盖复杂图纸理解、真实块插入和多方案设计推理 |
| `core/safety` | 原型 | `core/safety/policy.py` 已接入执行层；正式图层、保存、覆盖、删除仍需要显式批准 |
| 场景 Agent 业务 | 数据层原型 | `agents/*` 仍不得实现 Core 算法；商业/住宅/办公 preferences 已有，更多场景差异待补 |
| 遗留目录收束 | 原型 | `cad_agent/` 已标注 legacy；`libraries/domain_presets/` 为新入口，`libraries/domains/` 作为兼容副本保留 |

### Clone 后推荐动手顺序

**第 0 步：确认环境（约 30 分钟）**

按下文 **「换机清单」**：**先排查 → 按需增量（已有 CAD/CAD-MCP 不重复装）→ 全量验收全过**。任一项验收未通过则不算环境就绪。

**第 1 步：恢复上下文（约 5 分钟阅读）**

后续日常开发优先走短入口：

1. `AGENTS.md` — Codex 必须遵守的规则入口
2. `CORE_CONTEXT_BRIEF.md` — 稳定短上下文入口，先看当前状态和按需展开表
3. 只读取当前任务需要的详细文件，例如 `CORE_STATUS.md`、目标 Phase、相关测试或问题条目

首次 clone、换机、交接或完整审计时，再按 `CORE_CONTEXT_BRIEF.md` 的“按需展开”表读取详细文件。

**第 2 步：选一条开发主线（三选一，不要并行铺太开）**

| 路线 | 适合做什么 | 建议入口文件 |
| --- | --- | --- |
| **A. 实体回读** | 让「画准了」有证据，补真实 CAD 验证闭环 | `core/verification/inspect_dwg.py`、`scripts/inspect_dwg.py` |
| **B. 高层数据模型** | 深化 schema 反例、引用检查、项目模型和计划生成 | `core/schemas/`、`core/model_loop/`、`core/project_model/`、`core/plan_engine/` |
| **C. 非 CAD pipeline** | 在 CAD 不稳定时继续推进通用底座闭环 | `core/workflows/non_cad_pipeline.py`、`scripts/run_non_cad_pipeline.py` |

仓库当前瓶颈是：**没有真实回读 = 无法证明几何正确**；**高层模型已有最小闭环，但复杂设计推理、通道模型、真实块库和多方案比较还不够厚**。你更急哪边就先走哪条。

**第 3 步：暂不要做的事**

- 不要先扩写 `agents/commercial_fitout` 或 `agents/residential` 的业务规则
- 不要默认画正式图层或保存 DWG
- 不要把具体家装项目上下文写进根目录规则

### 阶段对照（方便你对齐路线图）

```text
阶段 0  架构冻结              done
阶段 1  仓库重装 + 执行原型    done（prototype）
阶段 2  Core 状态看板 + 非 CAD 底座闭环   prototype（CORE_STATUS 持续更新）
阶段 3+ 数据模型 / 读图 / 对象 / 布局 / 方案   prototype，复杂自动化仍待深化
```

详细阶段划分见 `CORE_ROADMAP.md`。

### 问 Codex 恢复进度时可以这样说

```text
读取本仓库 AGENTS.md 和 CORE_CONTEXT_BRIEF.md，告诉我 CAD Agent 当前开发状态和下一步建议。
```

---

## 恢复上下文（日常开发）

每次回来默认先读：

1. `AGENTS.md` — 根规则
2. `CORE_CONTEXT_BRIEF.md` — 稳定短入口

然后按任务展开：

| 场景 | 再读 |
| --- | --- |
| 看能力状态 | `CORE_STATUS.md` |
| 执行或调整 Phase | `CORE_RESTRUCTURE_PLAN.md` 的目标 Phase |
| 汇报当前进度 | `CAD_AGENT_STATUS.md` |
| 改规则或安全边界 | `CAD_AGENT_RULES.md` |
| 排查卡壳或回归 | `CAD_AGENT_BLOCKER_PLAYBOOK.md`、`CAD_AGENT_ISSUES.md` 相关条目 |
| 追溯最近改动 | `CAD_AGENT_CHANGELOG.md` 最近小节 |

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
& $py scripts\inspect_dwg.py --plan examples\plans\draw_test_cabinet.json --format json --no-cad
& $py scripts\run_non_cad_pipeline.py examples\workflows\full_non_cad_core_loop.json --output-dir output\test_artifacts\non_cad_pipeline\manual
& $py scripts\run_benchmark_suite.py examples\benchmarks\non_cad_core_benchmark.json --output-root output\test_artifacts\benchmarks\manual
& $py scripts\run_cad_validation.py --no-cad
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

**不重复安装原则：** 新电脑若 **已有** AutoCAD、CAD-MCP、Cursor 等，**不要无脑重装一遍**。应先 **排查现状**，只对 **缺失或验收失败** 的项做增量安装/配置；最终仍须达到下文全量标准，并通过全部验收命令。

本仓库 clone 下来 **只有代码和规则**；下列组件必须在新电脑上 **全部就绪**（可以是原有 + 补齐，不必全是新装的）。

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

**不是换机清单、但本机也尚未完整具备的能力：** 真实 CAD 实体回读闭环、复杂设计大脑、`zwcad_com` 真驱动——换机全配也不会自动拥有，属于后续开发项。

### 开发机参考版本（2026-05-25 实测通过）

新机请尽量对齐；至少应能通过下文 **全部** 验收命令且结果一致。

| 项目 | 开发机实测 |
| --- | --- |
| Python | 3.12.13（`CAD-MCP\.venv`） |
| Pillow | 12.2.0 |
| pywin32 / win32gui | 正常 import |
| AutoCAD | COM 已连上活动图纸 |
| 单元测试 | `unittest discover -s tests` → 165 passed |

### 换机流程总览

```text
先排查（已有啥） → 按需增量（只补缺的） → clone 本仓库 → 全量验收（必须全过）
```

验收标准不变：**终点必须与本机同级**；路径可以是「新机本来就有一半，只补另一半」。

### 第一步：先排查（在新电脑上执行）

在 PowerShell 里跑下面命令，对照「结果」列打勾，记下 **缺什么**（不要跳过这一步直接装）。

```powershell
# --- 基础环境 ---
Write-Host "OS:" (Get-CimInstance Win32_OperatingSystem).Caption
git --version 2>$null; if (-not $?) { Write-Host "[缺] Git" }

# --- CAD-MCP 目录与 Python ---
$mcpRoot = "$env:USERPROFILE\.codex\mcp\CAD-MCP"
$py = "$mcpRoot\.venv\Scripts\python.exe"
Write-Host "CAD-MCP 目录:" (Test-Path $mcpRoot)
Write-Host "CAD-MCP venv:" (Test-Path $py)
if (Test-Path $py) {
  & $py -c "import sys; print('Python', sys.version.split()[0])"
  & $py -c "import PIL; print('Pillow', PIL.__version__)" 2>$null; if (-not $?) { Write-Host "[缺] Pillow" }
  & $py -c "import win32com.client; print('pywin32 OK')" 2>$null; if (-not $?) { Write-Host "[缺] pywin32" }
  & $py -c "import win32gui; print('win32gui OK')" 2>$null; if (-not $?) { Write-Host "[缺] win32gui" }
} else {
  Write-Host "[缺] 整个 CAD-MCP .venv 或路径不同"
}

# --- AutoCAD 是否在跑（粗查；细查靠后面 COM 命令）---
$acad = Get-Process acad -ErrorAction SilentlyContinue
Write-Host "AutoCAD 进程:" ($null -ne $acad)
```

**需人工确认（脚本查不准）：**

| 项 | 怎么查 | 已有则 |
| --- | --- | --- |
| AutoCAD 已授权安装 | 开始菜单 / `acad.exe` 能启动 | 跳过装 CAD，只做 COM 验收 |
| Cursor / Codex | 能否打开 IDE | 跳过装 IDE |
| CAD-MCP 已在 MCP 里启用 | IDE → MCP 列表里有 CAD-MCP 且为开启 | 跳过配 MCP，只做画线测试 |
| 工作区 `AGENTS.md` | 工作区根是否有 CAD 触发规则 | 已有则不必复制父仓规则 |

### 第二步：按需增量（只补排查里「缺」的）

| 排查结果 | 要不要重装 | 建议动作 |
| --- | --- | --- |
| 已有 **AutoCAD**，能打开 DWG | **不要** 重装 CAD | 保持安装；验收时打开 DWG 即可。版本与开发机差太多时，只关注 COM 能否连通 |
| 已有 **CAD-MCP 目录** + `.venv` | **不要** 整包重装 | 用现有路径作 `$py`；缺包则 **只** `pip install` 缺的（如 `Pillow`、`pywin32`） |
| 有 CAD-MCP 但 **没有 `.venv`** 或 venv 坏了 | 不必重装 MCP 源码 | 在 `CAD-MCP` 目录内 **重建 venv** 并 `pip install -r requirements.txt`，再补 `pip install Pillow` |
| **没有** CAD-MCP | 需要新装 | 按你平时的方式装到 `%USERPROFILE%\.codex\mcp\CAD-MCP\`（与开发机同来源/commit 更稳） |
| 已有 **Cursor**，MCP 未配 | **不要** 重装 Cursor | 只在 MCP 设置里 **添加/启用** CAD-MCP |
| 没有 IDE | 需要装 | 安装 Cursor 或 Codex，并启用 CAD-MCP |
| **Git** 已有 | 不要重装 | 直接 `git clone` 本仓库 |
| 父工作区 **没有** `AGENTS.md` | — | 把本仓库放进有规则的父仓，或在工作区根补一份 CAD 触发 `AGENTS.md` |

**常见误区：**

- 新机 **已经装过 AutoCAD** → 不会也不能被本仓库「再装一遍」；重复的是 **验收**，不是安装程序。  
- 新机 **已经有 CAD-MCP** → 通常 **不用** 再下载一份；缺的是 **venv 依赖** 或 **MCP 开关**，用 `pip` / IDE 设置补齐即可。  
- `$py` **必须固定用 CAD-MCP 的 venv**；若你已有 MCP 但 Python 在别的路径，以 **能 import pywin32 + Pillow 且能 COM** 为准，路径写在个人笔记里，不要混用系统 Python。

### 第三步：clone 本仓库

Git 已有则直接：

```powershell
git clone https://github.com/Feini2002/CAD-AGENT.git
cd CAD-AGENT
```

### 第四步：统一 `$py` 并做全量验收

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
# 若你排查时 MCP 不在默认路径，改成实测通过的那个 python.exe，但仍是 CAD-MCP 的 venv
```

1. **打开 AutoCAD** 并加载一张测试 DWG（活动文档）。  
2. 执行下文 **全量验收命令**（**每一项都必须通过**）。  
3. 在 Cursor/Codex 里用 **CAD-MCP** 手动画一次简单图（矩形/直线），确认 MCP 链路与脚本链都可用。

只有 **第四步全部通过**，才算换机完成；前面三步允许「已有则跳过安装」。

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
& $py scripts\run_benchmark_suite.py examples\benchmarks\non_cad_core_benchmark.json --output-root output\test_artifacts\benchmarks\manual

# 3) AutoCAD COM（必须先打开 DWG）
& $py -c "from core.cad_io.autocad_com import AutoCADComDriver; d=AutoCADComDriver(); print('COM OK:', d.doc.Name)"

# 4) 真机预览落图（必须执行，不是可选项）
& $py scripts\execute_plan.py examples\plans\draw_test_cabinet.json

# 5) 截图（必须能落盘）
& $py scripts\render_preview.py --capture-screen --output output\previews\migration-check.png

# 6) 自主 CAD 验证总控（回家或换机时推荐使用）
& $py scripts\run_cad_validation.py --output-dir output\validation_runs\migration-check
```

### 通过标准（缺一即视为换机未完成）

| 步骤 | 期望结果 |
| --- | --- |
| Pillow / pywin32 / win32gui | 打印版本或 `OK`，无 ImportError |
| `self_check.py` | JSON 中 `"status": "pass"` |
| `validate_plan` | 输出 `VALID CAD_PLAN` |
| `dry_run_plan` | 正常预演输出 |
| `render_preview --check` | `"status": "ready"`，且 `pillow_imagegrab: true` |
| `unittest` | `OK`，165 tests |
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
