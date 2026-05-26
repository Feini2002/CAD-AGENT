# commercial_fitout Agent

Lightweight scene agent for **commercial office fitout** (工装) toward Scene Product Alpha.

This agent records scene differences, subscene scope, default preferences, and workflow names. It must reuse Core for drawing analysis, project models, object generation, layout, `CAD_PLAN` creation, execution, safety, and verification.

## Scene Product Alpha v1 scope（C-CFIT-01）

首版仅覆盖三个子场景（详见 `SCOPE.md` 与 `subscenes.json`）：

| subscene_id | 名称 |
| --- | --- |
| `open_office` | 开放办公区 |
| `meeting_room` | 会议室 |
| `reception` | 前台接待 |

**不提供**完整施工图、机电/结构/消防专册或任意块库直写；真实几何结论须回到 Core + `CODEX_PREVIEW` readback。

## Core Reuse Contract

- Use Core for all CAD IO, drawing parsing, model building, layout solving, `CAD_PLAN` validation, dry-run, execution, and verification.
- Do not duplicate Core schemas or execution logic in this agent.
- Keep scene-specific rules small and explicit.

## Legacy retail workflows（deferred）

以下 workflow 为历史零售 scaffold，**不在** v1 三个工装子场景内：

- `existing_plan_to_elevation`
- `blank_store_to_layout`

## 验证

```powershell
& $py -m unittest tests.agents.test_commercial_fitout_scope -v
```
