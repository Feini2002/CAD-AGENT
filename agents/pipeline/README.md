# 全局流水线 Agent（`agents/pipeline/`）

本目录是 **多 Agent CAD 系统的角色注册表**，不是第二套 Core。

**精度优先：** 不准就不交付。见 [`docs/training/precision-first.md`](../../docs/training/precision-first.md)。

## 六个全局 Agent

| ID | 职责 |
| --- | --- |
| `pipeline_orchestrator` | 编排轮次，禁止亲自落图 |
| `pipeline_intent` | 白话 → `intent.json` + checklist |
| `pipeline_execute` | 落 `CODEX_PREVIEW` |
| `pipeline_audit` | `training_geometry_audit` + checklist |
| `pipeline_repair` | 读 failures，最小修复，回环 |
| `pipeline_delivery` | 截图 + 自检 + 请你 feedback |

清单：`pipeline_manifest.json`
架构说明：`docs/training/global-agent-pipeline.md`

## 与场景 Agent 的关系

- **全局 Agent**：任何 `projects/<case>/` 共用，调用 `core/`
- **场景 Agent**（`agents/residential/` 等）：只给 Intent 提供词汇与偏好，**不**实现 COM/审计

## 当前阶段

**Phase A（现在）：** 一个交互式 Agent 会话按角色分步；Codex、Cursor 或同类工具均可，产物路径与本 manifest 一致。
**Phase B：** 每角色独立 agent rule / skill / 配置，Orchestrator 派发；具体载体不绑定单一软件。
**Phase C：** SDK 自动化 + `runs/state.json` 状态机。

## 边界

遵守 `agents/SCENE_AGENT_RULES.md`：**本目录不得出现 `*.py`**。
