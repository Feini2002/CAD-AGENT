## Why

OpenSpec 已能运行，但当前仓库里完成态 changes 仍留在 `openspec/changes/`，而 `openspec list --specs` 为空；这不影响校验，却容易让后续 Agent 误判“未初始化”或误用 `openspec status --json`。

本变更做一次轻量系统契约润色：确认 OpenSpec 可用，补清初始化 / 校验 / 归档命令口径，并继续遵守 `CORE_RESTRUCTURE_PLAN.md` 的主线边界。

## What Changes

- 明确 OpenSpec readiness 检查命令：`openspec list --json`、`openspec status --change <name> --json`、`openspec validate --all --strict --json --no-interactive`。
- 明确 `openspec status --json` 不带 `--change` 会失败，这是 CLI 用法边界，不是初始化失败。
- 补充完成态 change 与稳定 spec 的关系：completed change 可以保留在 `openspec/changes/` 作为活跃历史；若要归档，应同步稳定 spec 与仓库引用。
- 新增一个 OpenSpec 本地 README，作为下一位 Agent 的短入口。
- 润色 `openspec/config.yaml`、`AGENTS.md`、`CORE_RESTRUCTURE_PLAN.md` 中的系统契约文字。
- 不改变表 C、真实 CAD 证据、CAD_PLAN 契约或训练目标。

## Capabilities

### New Capabilities

- `openspec-readiness-contract`: 定义本仓库 OpenSpec 初始化可用性、命令边界、完成态 change 与归档规则。

### Modified Capabilities

- 无。当前 `openspec/specs/` 为空；本轮以新的 readiness 契约承接，不重写既有 completed change 的 delta specs。

## Impact

- 影响文档与 OpenSpec 配置：`openspec/config.yaml`、`openspec/README.md`、`AGENTS.md`、`CORE_RESTRUCTURE_PLAN.md`、状态 / changelog / handoff 记录。
- 影响校验：需要复跑 OpenSpec strict validate、文档治理审计，以及必要的轻量文档/契约检查。
- 不影响 CAD 运行、训练工作台数据、能力 registry 或真实 CAD 证明。
