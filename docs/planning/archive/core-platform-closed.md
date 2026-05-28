# Core 平台开发已收口

状态：**已关闭**（2026-05-28）

## 含义

通用 CAD Agent **Core 底座**工程开发在此仓库内视为完成，不再开「Core 施工期」新包。

| 轨道 | 结果 |
| --- | --- |
| 能力证明 `V-PROOF` | 45/45 done → `vproof-packages-done.md` |
| 代码轨 | 52/52 done → `lcad-code-track-done.md` |
| RCAD 烟囱 | 29/29 verified → `rcad-packages-done.md` |
| 平台门禁 | `docs/verification/core_platform_completion_gate.md` |

## 复验

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_core_platform_gate.py
```

## 后续工作入口（非 Core 施工）

| 目标 | 入口 |
| --- | --- |
| 抬真实 CAD 实力 | 口令「推进表 C」→ `docs/planning/任务清单.md` §0.1 |
| 场景 / 项目 / 读图 | `CORE_RESTRUCTURE_PLAN.md` 后置 Backlog |
| Agent 产品化 | `agents/` + scene benchmark |

**禁止**把 Core 100% 说成施工图能力或表 C 100%。
