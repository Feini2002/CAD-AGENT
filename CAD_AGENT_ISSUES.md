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
