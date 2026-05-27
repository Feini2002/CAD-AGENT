# CAD Agent Core Lab

CAD Agent Core Lab 是一个可迁移的通用 CAD Agent 开发包，用结构化 `CAD_PLAN` 连接自然语言需求、设计模型、CAD 执行和可验证结果。它不绑定某一张 DWG、某一套家装图纸或某一台电脑，也不把办公、工装、家装等场景做成彼此割裂的独立系统。

本仓库的核心原则是：白话需求必须先进入 `CAD_PLAN` 或更高层结构化绘图意图，再经过校验、dry-run、真实 CAD 执行和实体回读验证。真实 CAD 输出默认只写入 `CODEX_PREVIEW`，不默认保存 DWG、不覆盖原始文件、不删除已有实体、不修改正式图层。

## 当前状态

最后状态快照以 `CORE_STATUS.md`、`CAD_AGENT_STATUS.md` 和 `docs/planning/任务清单.md` 为准。当前公开口径：

| 口径 | 当前值 | 说明 |
| --- | --- | --- |
| 真实 CAD 实力主指标 | 约 **8.87%**，最高已证 **L4** | 表 C 机器口径；不能用工程进度或 RCAD 烟囱替代 |
| CAD 证明覆盖率 | 约 **48.58%** | 282 行能力登记中，112 verified + 25 showcase |
| 工程节奏 | 总约 **95%**（Core 96%，Agent 93%） | 表 A 折叠口径，不等于真实 CAD 几何已全面证明 |
| 任务台账 | 能力证明约 78%；代码轨约 89%；RCAD 烟囱 29/29 verified | 表 B 口径；RCAD 烟囱不等于施工图能力 |

最近主线已经覆盖：

- Core 底座：`core.plan_engine`、benchmark runner、composition engine、CAD validation runner、write guard、capability registry。
- 多场景能力：office / restaurant / residential 的 alpha、beta、P3 rollup 与多场景回归门禁。
- 真实 CAD 证据：baseline、基础图元探针、block alpha/beta、hatch、symbol block-first、drawing standard、composition refresh、VCAD 视觉表达 smoke。
- 文档治理：根文档拆分、交接包索引、状态/计划/验证/历史目录分层。

仍需注意：这些证据不能扩大解释为“任意真实项目图纸、公司块库、复杂施工图或任意 `CAD_PLAN` 都已经准确”。当前系统是 Core Lab / Alpha 原型，不是完整自动设计大脑。

## 目录导览

| 路径 | 用途 |
| --- | --- |
| `core/` | 通用 CAD Agent 能力底座：模型、布局、对象、符号、执行、验证、安全边界 |
| `agents/` | 轻量场景 Agent，只保留场景差异，复用 Core |
| `libraries/` | 跨场景资源，如对象默认值、块库、风格、材料、尺寸和图层标准 |
| `projects/` | 真实或样例项目资料 |
| `scripts/` | CLI 验证、benchmark、registry writeback、CAD smoke 入口 |
| `tests/` | 单元测试与场景/验证契约测试 |
| `docs/` | 架构、计划、治理、交接、验证、状态和历史 |
| `examples/` | 能力证明、CAD_PLAN、manifest 和样例数据 |

关键入口：

- 日常上下文：`CORE_CONTEXT_BRIEF.md`
- 唯一主计划：`CORE_RESTRUCTURE_PLAN.md`
- 当前状态：`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`
- 当前交接：`docs/handoffs/current.md`
- 包索引：`docs/handoffs/package-index.md`
- 执行台账：`docs/planning/任务清单.md`
- 规则边界：`AGENTS.md`、`docs/governance/cad-agent-rules.md`

## 开发与验证

常用入口如下，运行前可按本机环境设置 Python：

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
```

常用验证命令：

```powershell
& $py -m unittest discover -s tests
& $py scripts\self_check.py
& $py scripts\render_preview.py --check
& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
& $py scripts\run_dev_volume_audit.py
& $py scripts\run_capability_coverage.py --output output\validation_runs\capability-lab\cad_capability_coverage.json
```

真实 CAD 验证默认只写 `CODEX_PREVIEW`，提交或对外声明前必须能给出：

- `validate_plan.py` 与 `dry_run_plan.py` 结果。
- `core.plan_engine` 对应入口结果。
- 实际 CAD 输出、created handles 回读、实体类型和 bbox / geometry checks。
- 截图只能作为视觉辅助，不能替代 `geometry_verified`。

## CodeGraph

本仓库已加入 CodeGraph 使用规则。`.codegraph/` 是每台机器的本地 SQLite 索引，已经被 `.gitignore` 忽略，不会随 GitHub 提交。

新电脑 clone 后，如果要使用 CodeGraph，在仓库根目录重新初始化本地索引：

```powershell
codegraph.cmd init -i
```

如果当前 PowerShell 允许运行 npm 的 `.ps1` shim，也可以使用：

```powershell
codegraph init -i
```

常用命令：

```powershell
codegraph.cmd status
codegraph.cmd query AutoCAD --limit 8
codegraph.cmd files --max-depth 2
codegraph.cmd sync
```

当前 Codex / MCP 会话如果尚未暴露 `codegraph_*` 工具，可以先用 CLI 查询；重新加载 MCP 配置后再使用 CodeGraph MCP 工具。

## 交付口径

每次 CAD Agent 相关交付默认用 1 张精简进度表，先报表 C 真实 CAD 实力主指标，再说明本轮完成内容、验证证据和风险边界。完整表 A/B/C 只在状态汇报、交接、审计、进度盘点或表 C 专题时展开。

三套进度禁止混用：

- 表 A：工程节奏，回答模块和流程成熟度。
- 表 B：任务台账，回答能力证明 / 代码轨 / CAD 补验包推进情况。
- 表 C：真实 CAD 实力，回答对外“能画多厉害”的诚实上限。

百分比不替代测试、benchmark、截图、created handles 回读或 `geometry_verified` 证据。
