# 通用 CAD Agent 开发包当前进展

最后更新：2026-05-25

## 当前阶段

阶段 1：仓库重装已执行，通用 CAD Agent Core Lab 结构已建立。

新增横向机制：卡壳自查、截图能力检查和无 CAD 自检入口已建立。后续任何阶段出现“画不准、画不出来、验证不了”，先按 `CAD_AGENT_BLOCKER_PLAYBOOK.md` 排查。

规则入口已写入 `AGENTS.md`：根目录负责触发 CAD 相关任务，`CAD测试相关文件/AGENTS.md` 负责执行 CAD Agent 专用规则。

新增架构方向：已按 `CORE_RESTRUCTURE_PLAN.md` 执行第一轮大规模仓库重装，把当前工作区升级为“通用 CAD Agent Core Lab”：通用底座优先，场景 Agent 轻量化。

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
- 已实现 `scripts/execute_plan.py` 的第一版执行核心：读取 CAD_PLAN、校验、计算预览矩形/文字/尺寸，并调用驱动层。
- 已实现 `drivers/autocad_com.py` 的第一版 AutoCAD COM 驱动。
- 已新增并迁移 `tests/core/test_execute_plan.py`，覆盖测试柜预览绘制调用。
- 已通过 CAD-MCP 在当前打开的 CAD 文件中把 1800 x 600 测试柜画入 `CODEX_PREVIEW` 图层，并添加文字和基础尺寸标注。
- 已创建 `CAD_AGENT_BLOCKER_PLAYBOOK.md`，作为卡壳自查和自我迭代方法论。
- 已创建 `scripts/self_check.py`，可在不触碰当前 DWG 的情况下检查核心文件、示例计划、预览执行和截图工具链。
- 已让 `scripts/render_preview.py` 支持截图能力检查和可选屏幕截图。
- 已增加 `tests/test_render_preview.py` 和 `tests/test_self_check.py`。
- 已新增根目录 `AGENTS.md` 和 `CAD测试相关文件/AGENTS.md`，把 CAD 绘图自检门和卡壳自查规则固化为 Codex 入口规则。
- 已创建 `CORE_RESTRUCTURE_PLAN.md`，记录未来大规模仓库重装设计：以通用 Core 为主线，业务场景 Agent 作为轻量配置层。
- 已创建 `CORE_STATUS.md` 和 `CORE_ROADMAP.md`，用能力矩阵追踪通用底座进度。
- 已创建 `core/`、`agents/`、`projects/`、`docs/architecture`、`docs/decisions`、`docs/roadmap` 等目标结构。
- 已将计划校验、dry-run、执行、截图、自检、DWG 检查、CAD 驱动迁入 `core/` 对应模块。
- 已保留 `scripts/` 和 `drivers/` 兼容包装器，旧命令和旧导入仍可用。
- 已创建 6 个轻量场景 Agent 脚手架：`commercial_fitout`、`residential`、`office`、`restaurant`、`exhibition`、`custom`。
- 已将核心测试迁入 `tests/core/`，并增加重构兼容测试。
- 第一轮保留 `cad_agent/` 和 `libraries/domains/` 作为遗留目录，待第二轮迁移收束。
- 已修剪 `CORE_RESTRUCTURE_PLAN.md`，让它只保留第一轮重装后仍未完成的剩余工作。

## 正在做

- 第一轮仓库重装已完成，等待下一步进入 Core 数据模型或实体回读能力开发。
- 当前仍不扩张单一工装或家装 Agent，避免把通用能力写死到场景层。

## 下一步

1. 建立 Core 高层数据模型 schema：`DESIGN_BRIEF`、`DRAWING_MODEL`、`PROJECT_MODEL`、`OBJECT_SPEC`、`STYLE_PROFILE`、`BLOCK_LIBRARY`、`LAYOUT_PROPOSAL`、`DESIGN_PROPOSAL`、`VERIFICATION_REPORT`。
2. 或优先补 `entity readback`，让 `core/verification` 能回读 CAD 实体并输出验证报告。
3. 第二轮收束 `cad_agent/` 和 `libraries/domains/` 两个遗留目录。
4. 继续保持旧入口兼容，直到所有文档和调用方都迁移到 Core 正式入口。

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
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' 'CAD测试相关文件\tests\core\test_execute_plan.py'
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' -m unittest discover -s 'CAD测试相关文件\tests'
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' 'CAD测试相关文件\scripts\self_check.py'
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' 'CAD测试相关文件\scripts\render_preview.py' --check
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' -m core.plan_engine.validate_plan 'CAD测试相关文件\examples\plans\draw_test_cabinet.json'
```

结果：

```text
VALID CAD_PLAN
CAD_PLAN DRY RUN
core test_execute_plan: OK
unit test discover: 12 tests OK
self_check.py: status pass
render_preview.py --check: status ready
core.plan_engine.validate_plan: VALID CAD_PLAN
```

## 暂不做

- 暂不做完整自动设计。
- 暂不做复杂房间识别。
- 暂不做 SQL 数据库。
- 暂不做全行业对象库。
- 暂不把所有 CAD 细则写进根目录 `AGENTS.md`；根目录只保留 CAD 相关任务触发规则，细则仍放在 `CAD测试相关文件/AGENTS.md` 和本开发包文档里。

## 下次恢复开发时怎么问

你可以直接说：

```text
读取 CAD测试相关文件，告诉我 CAD Agent 开发到哪一步了。
```

我应该优先读取：

```text
README.md
AGENTS.md
CORE_STATUS.md
CORE_ROADMAP.md
CORE_RESTRUCTURE_PLAN.md
CAD_AGENT_STATUS.md
CAD_AGENT_RULES.md
CAD_AGENT_CHANGELOG.md
CAD_AGENT_ISSUES.md
CAD_AGENT_BLOCKER_PLAYBOOK.md
```
