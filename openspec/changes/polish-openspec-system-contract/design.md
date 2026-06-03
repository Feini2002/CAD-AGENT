## Context

OpenSpec 已初始化在仓库根目录，`openspec list --json`、逐 change `status`、`validate --all --strict` 都能运行。当前特殊点是：历史上几个 completed changes 仍保留在 `openspec/changes/`，而主规格目录暂时为空。这种状态对 CLI 校验是合法的，但对后续 Agent 不够友好，容易产生两个误解：

1. `openspec list --specs` 为空被误读为“OpenSpec 没初始化”。
2. `openspec status --json` 报 missing `--change` 被误读为“OpenSpec 坏了”。

本设计只润色系统契约和短入口，不改变 CAD Designer Agent 成长路径、不改变表 C，也不归档既有 completed changes。

## Goals / Non-Goals

**Goals:**

- 给后续 Agent 一个明确的 OpenSpec readiness 检查入口。
- 让系统契约说明 CLI 的真实用法：list 看变更，status 必须指定 change，validate 做总校验。
- 明确 completed changes、main specs、archive 三者关系，减少后续误归档或误删。
- 保持 OpenSpec 从属于 `CORE_RESTRUCTURE_PLAN.md`。

**Non-Goals:**

- OpenSpec 不替代 `CORE_RESTRUCTURE_PLAN.md`，也不承载总队列。
- 不归档旧 change，因为现有文档仍引用 `openspec/changes/<name>/` 路径。
- 不改变 OpenSpec CLI、schema 或工具安装方式。
- 不改变任何真实 CAD 能力声明。

## Decisions

### Decision 1: 保留 completed changes，不在本轮归档

已完成 changes 现在仍被 README、PlanMD、状态和交接记录引用。直接 `openspec archive <change> -y` 会把路径迁到 archive，并可能需要批量更新引用。本轮目标是“确保能用 + 契约润色”，所以只记录归档规则，不移动旧 change。

Alternative considered: 立即归档 3 个 completed changes。暂不采用，因为这会扩大改动面，且用户当前关心的是初始化可用性和系统契约，而不是历史结构迁移。

### Decision 2: 新增 `openspec/README.md` 作为短入口

`openspec/config.yaml` 适合给 CLI 和 Agent 提供上下文，但不适合作为人类短入口。README 记录最短命令、状态解释和归档边界，能让后续接手更稳。

Alternative considered: 只更新 `AGENTS.md`。不够，因为 OpenSpec 目录本身仍缺一个本地入口。

### Decision 3: 配置和主规则只写稳定边界，不写临时 next

`openspec/config.yaml`、`AGENTS.md`、`CORE_RESTRUCTURE_PLAN.md` 只补 OpenSpec 使用规则和校验命令，不放“下一步做什么”。具体开发顺序仍回到根主线文件和任务清单。

## Risks / Trade-offs

- [Risk] 完成态 changes 继续留在 active list，列表看起来不“干净”。 → Mitigation: README 明确这是可用状态；归档需同步引用和稳定 specs。
- [Risk] 新 README 变成第二套规则。 → Mitigation: 只写 OpenSpec 使用命令和边界，引用 `AGENTS.md` 与 `CORE_RESTRUCTURE_PLAN.md` 为上位规则。
- [Risk] 契约文字过细增加阅读负担。 → Mitigation: 控制在短入口和少量 bullets，机器校验仍以 `validate` 和 doc governance 为准。

## Migration Plan

1. 新增 OpenSpec readiness spec 与 tasks。
2. 更新 `openspec/config.yaml`、`openspec/README.md` 和主入口规则。
3. 运行 OpenSpec strict validate、文档治理审计和轻量文本检查。
4. 更新状态 / changelog / handoff，说明本轮不改 CAD 能力。

Rollback 是文档级别：撤回本 change 及本轮 README/config/rules 润色即可，不涉及代码迁移或 CAD 数据。

## Open Questions

无。后续若要真正归档 completed changes，应另开一个小变更，集中处理 `openspec archive`、稳定 specs 和文档引用迁移。
