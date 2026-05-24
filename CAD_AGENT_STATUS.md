# 通用 CAD Agent 开发包当前进展

最后更新：2026-05-24

## 当前阶段

阶段 3：通用开发包骨架已建立，CAD_PLAN 校验和 dry-run 已跑通，下一步进入预览绘制。

这个开发包不绑定当前家装图纸。当前电脑和当前 DWG 只作为第一套验证环境。后续应能迁移到任意安装好 Codex、CAD、CAD-MCP/Python 的电脑，并适配住宅、工装、店铺、办公、餐饮、展陈等项目。

## 已完成

- 已验证 Codex 可以通过 CAD MCP 在本机当前打开的 AutoCAD 图纸里绘制矩形、圆、直线和文字；这只是环境验证，不是项目绑定。
- 已确认长期路线：不从白话直接跳到画图，中间先生成结构化 `CAD_PLAN`。
- 已创建本通用 CAD Agent 开发包，用于集中管理规则、Schema、示例、脚本和开发记录。
- 已把旧说明文档归档到 `docs/archive/`。
- 已建立第一版通用目录框架。
- 已创建第一版 `draw_test_cabinet.json`。
- 已创建并验证 `scripts/validate_plan.py`。
- 已创建并验证 `scripts/dry_run_plan.py`。
- 已将项目定位修正为“可迁移通用 CAD Agent 开发包”，不绑定当前根目录或当前家装图纸。

## 正在做

- 准备把 `execute_plan.py` 从脚手架推进到真实 CAD 预览绘制。
- 准备让第一个测试柜从 CAD_PLAN 进入 `CODEX_PREVIEW` 图层。

## 下一步

1. 让 `execute_plan.py` 支持读取测试柜 CAD_PLAN。
2. 调用 CAD MCP 或 AutoCAD COM，在 `CODEX_PREVIEW` 图层画 1800 x 600 测试柜。
3. 添加文字 `测试柜`。
4. 添加基础尺寸标注。
5. 写入执行结果和问题记录。

## 通用适用范围

当前目标不是只服务某一张家装图，而是形成可迁移能力：

```text
住宅家装
商业工装
零售店铺
办公空间
餐饮空间
展厅展陈
其他 CAD 平面/布置/标注场景
```

如果进入某个具体项目，应先创建或读取该项目自己的 `cad_context.json`，不要把具体项目上下文写死到通用规则里。

## 已验证命令

PowerShell 中应优先使用 CAD-MCP 虚拟环境 Python：

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' 'CAD测试相关文件\scripts\validate_plan.py' 'CAD测试相关文件\examples\plans\draw_test_cabinet.json'
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' 'CAD测试相关文件\scripts\dry_run_plan.py' 'CAD测试相关文件\examples\plans\draw_test_cabinet.json'
```

结果：

```text
VALID CAD_PLAN
CAD_PLAN DRY RUN
```

## 暂不做

- 暂不做完整自动设计。
- 暂不做复杂房间识别。
- 暂不做 SQL 数据库。
- 暂不做全行业对象库。
- 暂不把所有规则写进根目录 `AGENTS.md`。

## 下次恢复开发时怎么问

你可以直接说：

```text
读取 CAD测试相关文件，告诉我 CAD Agent 开发到哪一步了。
```

我应该优先读取：

```text
README.md
CAD_AGENT_STATUS.md
CAD_AGENT_RULES.md
CAD_AGENT_CHANGELOG.md
CAD_AGENT_ISSUES.md
```
