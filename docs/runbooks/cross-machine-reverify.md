# 换机复验 P0（BETA-CROSS-MACHINE-02）

最后更新：2026-05-28

## 何时跑

- 新电脑 / 重装系统 / 换 AutoCAD 或 CAD-MCP 路径后
- 回家办公第一次打开本仓库
- 用户口令：**换机复验**

## 前置

1. AutoCAD **已打开** 测试 DWG（可随意改，建议非正式项目图）
2. `$py` 指向 CAD-MCP venv：

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
cd <CAD-AGENT 根目录>
```

## 一键 gate（推荐）

```powershell
& $py scripts\run_beta_cross_machine_02_gate.py --output-dir output\validation_runs\beta-cross-machine-02-<日期>
```

| 结果 `status` | 含义 |
| --- | --- |
| `pass` | no-CAD + 自动化 CAD 步骤均过 |
| `partial` | 自动化 CAD 过，但 **MCP 手动画图** 仍需你在 IDE 里确认一次 |
| `blocked` | 环境或 Core gate 失败，先修再开发 |

仅环境/登记（不连 CAD）：

```powershell
& $py scripts\run_beta_cross_machine_02_gate.py --no-cad
```

## 报告位置

- `beta_cross_machine_02_report.json` — 全量步骤
- `beta_cross_machine_02_summary.json` — 摘要
- 同目录下可能有 `cad_validation/`、`migration-reverify-window.png`

## 仍须人工（1 项）

在 Cursor/Codex 用 **CAD-MCP** 手动画一条线或矩形，确认 MCP 链路与脚本链都通。详见 `docs/onboarding/migration-checklist.md` 第四步。

## 全量对照

完整组件表与历史验收命令：`docs/onboarding/migration-checklist.md`。
