# CAD Agent Core Workflow

本文档是 `cad_agent/CAD_WORKFLOW.md` 的 Core 版收束入口。旧目录只保留 legacy 指引，新开发以本文件和 `core/` 模块为准。

## 标准流程

```text
自然语言 / 项目输入
-> DESIGN_BRIEF 或结构化意图
-> DRAWING_MODEL / PROJECT_MODEL
-> DESIGN_PROPOSAL / LAYOUT_PROPOSAL / OBJECT_SPEC
-> CAD_PLAN
-> validate
-> dry-run
-> CODEX_PREVIEW
-> VERIFICATION_REPORT
-> 用户确认后才允许正式落图、保存或覆盖
```

## 硬边界

- 不从白话直接跳到 CAD。
- `CAD_PLAN` 只表达最终落图指令，不承载完整设计推理。
- 所有真实绘图默认走 `CODEX_PREVIEW`。
- 不能把“已执行”或“已截图”说成“几何已验证”。
- 没有实体回读或截图证据时，必须在 `VERIFICATION_REPORT` 中写明限制。

## 卡壳分支

出现画不准、画不出来、截图或回读缺失时，进入：

```text
docs/runbooks/blocker-playbook.md
-> scripts/self_check.py
-> scripts/render_preview.py --check
-> scripts/inspect_dwg.py --plan <plan> --format json
-> 最小复现
-> 最小修复
-> 重新验证并记录
```

真实 CAD 实体回读需要显式传 `scripts/inspect_dwg.py --connect-cad`，避免普通自检在无 CAD 环境中误连或卡住。
