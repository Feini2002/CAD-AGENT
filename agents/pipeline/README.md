# 全局流水线 Agent（`agents/pipeline/`）

本目录是 **多 Agent CAD 系统的角色注册表**，不是第二套 Core。

**精度优先：** 不准就不交付。见 [`docs/training/precision-first.md`](../../docs/training/precision-first.md)。

## 全局 Agent

| ID | 职责 |
| --- | --- |
| `pipeline_context_curator` | 收束上下文、案例状态和历史噪声 |
| `pipeline_asset_retriever` | 在 CAD_PLAN 前产出 `retrieval_pack` |
| `pipeline_asset_governor` | 资产库守门员，沉淀前判断能否进库、派哪些子 Agent、是否还需润色加固 |
| `pipeline_asset_librarian` | 资产馆员，管分类、命名、去重、检索词、状态和资产卡片 |
| `pipeline_asset_dwg_curator` | 资产 DWG 编排员，管分区排版、训练污染清洗、槽位和 native 写入证据边界 |
| `pipeline_asset_reuse_auditor` | 资产复用审计员，管复用回放、created handles、readback 和 verified 门禁 |
| `pipeline_orchestrator` | 编排轮次，禁止亲自落图 |
| `pipeline_visual_intent` | 参考图 / 样式目标 → `visual_parts` |
| `pipeline_intent` | 白话 → `intent.json` + checklist |
| `pipeline_execute` | 落 `CODEX_PREVIEW` |
| `pipeline_audit` | `training_geometry_audit` + checklist |
| `pipeline_repair` | 读 failures，最小修复，回环 |
| `pipeline_delivery` | 截图 + 自检 + 请你 feedback |

清单：`pipeline_manifest.json`
架构说明：`docs/training/global-agent-pipeline.md`

## 主 Agent 派发边界

`pipeline_orchestrator` 是主编排 Agent。它的“自我意识”只表示工程上的可审计自我模型：知道自己负责分流、拆任务、生成 `a_to_a_task_contract`、加派已登记 Agent、收 hard gate 输出，并在证据不足时阻断完成口吻；它不亲自替代 CAD 执行、资产守门、复用审计或视觉布局复审。

高风险任务会在合同里写入 `mainAgentSelfCheck` 和 `dispatchDecision`。主 Agent 只允许自动加派 manifest 已登记 Agent；未登记的新 Agent 只能作为 `additionalAgentRequests`，进入 `needs_reviewed_package` / `needs_openspec_change`，不得临场生效。

## 与场景 Agent 的关系

- **全局 Agent**：任何 `projects/<case>/` 共用，调用 `core/`
- **场景 Agent**（`agents/residential/` 等）：只给 Intent 提供词汇与偏好，**不**实现 COM/审计

## 当前阶段

**Phase A（现在）：** 一个交互式 Agent 会话按角色分步；Codex、Cursor 或同类工具均可，产物路径与本 manifest 一致。
**Phase B：** 每角色独立 agent rule / skill / 配置，Orchestrator 派发；具体载体不绑定单一软件。
**Phase C：** SDK 自动化 + `runs/state.json` 状态机。

## 边界

遵守 `agents/SCENE_AGENT_RULES.md`：**本目录不得出现 `*.py`**。
