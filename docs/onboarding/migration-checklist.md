> 本文从根目录 `README.md` 拆出，作为换机和回家验收的专用手册；README 只保留入口链接。

# 换机清单（与本机同等级，全量配置）

**最后更新：2026-05-26**

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

**不是换机清单、但本机也尚未完整具备的能力：** 真实项目图纸/块库/任意 CAD_PLAN 的全量几何补验、复杂设计大脑、`zwcad_com` 真驱动——换机全配也不会自动拥有，属于后续开发项。

### 开发机参考版本（2026-05-25 实测通过）

新机请尽量对齐；至少应能通过下文 **全部** 验收命令且结果一致。

| 项目 | 开发机实测 |
| --- | --- |
| Python | 3.12.13（`CAD-MCP\.venv`） |
| Pillow | 12.2.0 |
| pywin32 / win32gui | 正常 import |
| AutoCAD | COM 已连上活动图纸 |
| 单元测试 | `unittest discover -s tests` → 223 passed |

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
& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
& $py scripts\run_benchmark_suite.py examples\benchmarks\non_cad_core_benchmark.json --output-root output\test_artifacts\benchmarks\manual
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\blank_shell_manual
& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\office_alpha_manual
& $py scripts\run_benchmark_suite.py examples\benchmarks\interior_delivery_benchmark.json --output-root output\test_artifacts\benchmarks\interior_delivery_manual

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
| `unittest` | `OK`，223 tests |
| repo audit | `0 findings` |
| benchmark suites | `non_cad_core_benchmark`、`blank_shell_core_benchmark`、`office_alpha_benchmark`、`interior_delivery_benchmark` 均 pass；office alpha 为 `4/4 cases`，interior delivery 为 `3/3 cases` |
| COM 探测 | 打印当前活动 DWG 文件名 |
| `execute_plan` | 图上出现 `CODEX_PREVIEW` 测试柜 |
| `--capture-screen` | 生成 `output\previews\migration-check.png` |
| `run_cad_validation.py` | 顶层 `status=pass`，且 `readback_report.status=geometry_verified`、`cad_capability_probe.status=cad_capability_verified` |
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
