# CAD Agent 问题与修复记录

这个文件只记录开发和测试过程中遇到的问题。它不是普通日志，而是“以后别再踩同一个坑”的记录。

## 记录模板

```md
## 问题：一句话概括

日期：

现象：

影响：

原因：

修复：

以后规则：

相关文件：
```

## 已知问题

### 问题：`unittest discover -s tests` 会把 `tests/core` 当成 `core` 包

日期：2026-05-25

现象：

第一轮仓库重装后运行：

```powershell
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' -m unittest discover -s tests
```

出现 `ModuleNotFoundError: No module named 'core.execution'`、`No module named 'core.verification'` 等错误。

影响：

真实 `core/` 包已经存在，但测试发现从 `tests/` 作为起点时，会把 `tests/core` 导入成名为 `core` 的测试包，遮住项目根目录下的真实 `core/`。

原因：

`tests/core/__init__.py` 让测试目录成为 `core` 包，而测试命令的 top-level 默认是 `tests`。

修复：

在 `tests/core/__init__.py` 中扩展包搜索路径，把项目根目录下的真实 `core/` 加入 `__path__`，从而保留 `tests/core` 目录结构和旧 `unittest discover -s tests` 命令兼容。

以后规则：

如果继续使用 `tests/core` 目录名，要保留该兼容处理，或改用显式 top-level 的测试命令。迁移测试结构时必须跑完整 `unittest discover -s tests`。

### 问题：Core 迁移后 `self_check.py` 容易误判项目根目录

日期：2026-05-25

现象：

`self_check.py` 从 `scripts/` 迁到 `core/verification/` 后，如果继续使用 `Path(__file__).resolve().parents[1]` 推断项目根，会把 `core/` 当成根目录。

影响：

自检会错误判断必需文件缺失，或者把输出路径、示例计划路径解析到错误位置。

原因：

文件所在目录层级从 `scripts/self_check.py` 变为 `core/verification/self_check.py`，父级数量变化。

修复：

Core 实现中改为 `Path(__file__).resolve().parents[2]`，旧 `scripts/self_check.py` 只保留薄包装器。

以后规则：

迁移 CLI 脚本到 Core 后，必须重新检查所有基于 `__file__` 的根目录推断。

### 问题：卡壳时缺少统一自查和截图证据入口

日期：2026-05-25

现象：

目录里已有 `output/previews/` 和 `scripts/render_preview.py`，但 `render_preview.py` 只是脚手架；`inspect_dwg.py` 也只是回读验证脚手架。遇到“画不准、画不出来”时，缺少统一方法告诉 Codex 先查什么、如何留证据、何时修工具。

影响：

后续阶段 4 预览绘制和阶段 5 回读验证容易反复盲试；视觉问题也可能因为没有截图而无法复盘。

原因：

早期重点是搭建 CAD_PLAN、validate 和 dry-run 最小闭环，截图、自检、卡壳恢复还没有实现。

修复：

- 新增 `CAD_AGENT_BLOCKER_PLAYBOOK.md`。
- 新增 `scripts/self_check.py`。
- 扩展 `scripts/render_preview.py --check` 和 `--capture-screen`。
- 新增相关单测。

以后规则：

遇到卡壳先运行自检，视觉问题先确认截图能力；如果截图或自检能力不存在，先补工具入口，再继续绘图修复。

相关文件：

- `CAD_AGENT_BLOCKER_PLAYBOOK.md`
- `CAD_AGENT_RULES.md`
- `scripts/self_check.py`
- `scripts/render_preview.py`
- `tests/test_render_preview.py`
- `tests/test_self_check.py`

### 问题：早期测试目录未包化导致模块名运行失败

日期：2026-05-25

现象：

使用下面命令运行新增测试时失败：

```powershell
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' -m unittest tests.test_execute_plan
```

影响：

测试文件本身可用，但当时 `tests/` 目录还不是 Python package，模块名方式发现测试会失败。

原因：

当时还没有创建 `tests/__init__.py`，项目测试规模也很小。

修复：

早期临时修复是直接按文件路径运行：

```powershell
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' 'CAD测试相关文件\tests\test_execute_plan.py'
```

后续仓库重装时已创建 `tests/__init__.py`、`tests/core/__init__.py`，并迁移到：

```powershell
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' -m unittest discover -s 'CAD测试相关文件\tests'
```

以后规则：

当前优先使用 `unittest discover -s tests`。如果使用 `tests/core` 目录名，必须保留 `tests/core/__init__.py` 中对真实 `core/` 包路径的兼容处理。

### 问题：中文 Markdown 在 PowerShell 默认输出中可能显示乱码

日期：2026-05-24

现象：

使用 `Get-Content` 默认读取中文 Markdown 时，终端可能显示乱码。

影响：

文件内容本身通常没坏，但终端显示会误导判断。

原因：

PowerShell 默认编码和文件 UTF-8 编码显示不一致。

修复：

读取中文 Markdown 时使用：

```powershell
Get-Content -Encoding UTF8 -LiteralPath '文件路径.md'
```

以后规则：

检查中文文档时优先显式指定 `-Encoding UTF8`。

### 问题：CAD Agent 文件散落在根目录会影响阅读

日期：2026-05-24

现象：

CAD 相关说明文件和 DWG、PDF、视频、临时目录混在一起。

影响：

用户难以判断哪些文件属于 CAD Agent 开发资料。

原因：

早期验证阶段先在根目录生成文件，尚未整理项目结构。

修复：

创建 `CAD测试相关文件` 子文件夹，并将 CAD Agent 相关说明归档到内部结构。

以后规则：

CAD Agent 的说明、规则、Schema、示例、脚本骨架统一放入 `CAD测试相关文件`。

### 问题：PowerShell 中全局 python 命令不可用

日期：2026-05-24

现象：

运行下面命令失败：

```powershell
python 'CAD测试相关文件\scripts\validate_plan.py' 'CAD测试相关文件\examples\plans\draw_test_cabinet.json'
```

影响：

脚本本身没坏，但不能依赖全局 `python` 命令运行测试。

原因：

当前系统 PATH 中没有可用的 `python` 命令。

修复：

使用 CAD-MCP 虚拟环境 Python：

```powershell
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' 'CAD测试相关文件\scripts\validate_plan.py' 'CAD测试相关文件\examples\plans\draw_test_cabinet.json'
```

以后规则：

运行 CAD Agent Python 脚本时，优先使用 CAD-MCP 虚拟环境 Python，除非以后单独建立项目级 `.venv`。

### 问题：Python 输出中文在 PowerShell 中可能显示乱码

日期：2026-05-24

现象：

`dry_run_plan.py` 可以读取中文对象名，但终端输出可能显示成乱码。

影响：

脚本结果容易被误判。

原因：

Windows PowerShell 控制台输出编码和 Python 输出编码不一致。

修复：

运行脚本前设置：

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

以后规则：

涉及中文 JSON 或中文 Markdown 的脚本验证，都显式设置 UTF-8 输出。
