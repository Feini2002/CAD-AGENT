# Core Platform Completion Gate

状态：**已收口**（2026-05-28）；Core 平台开发已关闭，仅作复验与交接引用。

## 口径

**Core 100%** 指通用 CAD Agent Core Lab 的工程底座已收口，不等于：

- 表 C 真实 CAD 实力 100%
- 任意项目 DWG / 公司块库已接入
- Scene Product 已产品化

## 退出门槛

| 项 | 要求 |
| --- | --- |
| 代码轨 | `docs/planning/任务清单.md` §4：**52/52 done** |
| 能力证明轨 | §3：**45/45 done** |
| RCAD 烟囱 | §5：**29/29 verified** |
| 单测 | `python -m unittest discover -s tests` 全绿 |
| 文档治理 | `scripts/run_doc_governance_audit.py` pass |
| 仓库审计 | `scripts/run_repo_audit.py --fail-on-findings` pass |
| 表 C 机器报告 | `scripts/run_capability_coverage.py` 可复跑且 `status=pass` |

一键复跑：

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_core_platform_gate.py
```

## 明确不在 Core 100% 内

- 表 C 旧证据债全量 hard audit 通过
- 正式图层 / 保存 DWG / 删除实体
- 自动 DWG/PDF 读图交付
- 真实公司块库

上述项走 `CORE_RESTRUCTURE_PLAN.md` 后置 Backlog 或用户 Decision Gate。
