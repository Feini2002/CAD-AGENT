# OpenSpec 本地入口

本目录是仓库的 **复杂变更契约层**，只负责单个 change 的 proposal / design / specs / tasks；主计划仍是根目录 `CORE_RESTRUCTURE_PLAN.md`。

## 快速自检

```powershell
openspec.cmd list --json
openspec.cmd status --change <change-name> --json
openspec.cmd validate --all --strict --json --no-interactive
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_doc_governance_audit.py
```

注意：`openspec.cmd status --json` 不带 `--change` 会报缺少参数，这是 CLI 用法边界，不是 OpenSpec 初始化失败。

## 当前状态解释

- `openspec/changes/<change>/`：具体变更契约。完成态 change 可以暂时留在这里，作为仍被仓库文档引用的活跃历史。
- `openspec/specs/`：归档后沉淀的稳定规格。若 `openspec.cmd list --specs --json` 暂时为空，不代表 OpenSpec 不可用。
- `openspec/changes/archive/`：归档后的历史 change。归档前要确认稳定 spec 和仓库引用同步。

## Change Metadata

活跃 change 应保留 `.openspec.yaml`，至少写明：

- `schema`
- `metadataVersion`
- `created`
- `lifecycle.status`
- `lifecycle.archiveReady`
- `dependencies.dependsOn` / `blockedBy` / `supersedes`
- `openQuestions`

`scripts/run_doc_governance_audit.py` 会只读检查 metadata 缺失、生命周期状态、完成态 tasks、未闭环 open questions、缺失依赖目标和依赖 / supersedes 环。该审计不自动归档、不修改 metadata，也不证明任何 CAD 能力。

第一轮暂不检查结构化 impact 冲突、`impact.breaking` 传播、schema 目标存在性或 Agent 目标存在性；这些属于后续扩展，不应为了通过 metadata v2 审计而一次性补满所有历史 change。

## 使用边界

必须优先考虑 OpenSpec 的情况：

- 修改 `CAD_PLAN` 契约、真实 CAD 验证标准、能力登记 / 表 C 语义。
- 调整 Core 架构边界、跨多个模块的治理规则或高风险流程。
- 改变开发顺序、退出门槛或当前包范围。

可以不用 OpenSpec 的情况：

- 单文件小 bugfix、小文案修正、普通训练 round、只刷新表 C、状态 / changelog / handoff 记录。

禁止事项：

- 不新增根级 `openspec/tasks.md`。
- 不把 `openspec/changes/*` 写成第二套主计划、总 backlog、全局 next 或优先级队列。
- 不用 OpenSpec 的 completed / passed 状态暗示真实 CAD 能力提升；真实 CAD 仍以 `CAD_PLAN`、validate、dry-run、`CODEX_PREVIEW`、handles 回读和必要截图为证据。

## 归档口径

归档 completed change 时使用：

```powershell
openspec.cmd archive <change-name> -y
```

如果仓库文档仍引用 `openspec/changes/<change-name>/`，归档同一轮必须更新这些引用，或明确暂不归档。基础设施 / 文档型 change 如果不需要写入稳定 specs，可先讨论是否使用 `--skip-specs`。
