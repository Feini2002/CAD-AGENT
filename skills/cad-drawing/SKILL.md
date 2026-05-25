---
name: cad-drawing
description: 当用户希望 Codex 通过自然语言绘制、修改、校验或规划 CAD 内容时使用，适用于住宅、零售、办公、餐饮、展陈、酒店、教育、医疗、工业或自定义平面图场景。
---

# CAD 绘图 Skill

用于 CAD 绘图或 CAD Agent 开发任务。这个项目 Skill 是 CAD Agent 开发包内的可迁移草稿，不绑定当前 DWG、当前目录路径或单一设计行业。

## 默认语言

面向用户的解释、状态汇报、方案讨论、追问和最终结论默认使用中文。代码、命令、路径、文件名、Schema 字段、JSON key、工具名和 API 名称保留英文或原文。除非用户明确要求英文，不要把英文模板原样作为最终答复。

## 核心流程

1. 恢复项目工作时，读取 `README.md`、`CORE_STATUS.md`、`CORE_ROADMAP.md`、`CORE_RESTRUCTURE_PLAN.md`、`CAD_AGENT_STATUS.md` 和 `CAD_AGENT_RULES.md`。
2. 绘图前，先把用户语言转换为 `CAD_PLAN`。
3. 使用 `core.plan_engine.validate_plan` 或兼容包装器 `scripts/validate_plan.py` 校验计划。
4. 使用 `core.plan_engine.dry_run_plan` 或兼容包装器 `scripts/dry_run_plan.py` 预演计划。
5. 除非用户明确批准正式修改，否则只绘制到 `CODEX_PREVIEW`。
6. 绘制后，用中文报告对象类型、图层、尺寸、位置和验证状态。
7. 如果绘图不准确、卡壳或无法验证，先读取 `CAD_AGENT_BLOCKER_PLAYBOOK.md`，运行 `scripts/self_check.py`，并检查截图能力，再重试。
8. 项目文件或规则变化时，更新状态、变更记录和问题记录。
9. 可复用 CAD Agent 能力放入 `core/`；场景专属 Agent 规则在 `agents/` 下保持轻量。

## 参考文件

仅在需要时读取：

- `references/CAD_WORKFLOW.md`：标准工作流。
- `references/CAD_PLAN_SCHEMA.md`：计划格式。
- `references/SAFETY_RULES.md`：CAD 安全约束。
