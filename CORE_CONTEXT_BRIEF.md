# Core Context Brief

最后更新：2026-06-07。本文是新会话短上下文入口，不是状态库、计划库或历史库。若 `AGENTS.md` 已自动加载，从本文开始恢复；普通任务只按“按需展开”追加 1-2 个文件。

## 当前一句话

本仓库是可迁移的 CAD Agent Core Lab；当前主线是 `ARCH-CONVERGENCE-01` 架构归并画布工程。正式对象训练、整批训练、表 C 推进和系统资产大沉淀默认暂缓，先把旧表格、训练、资产、多 Agent、Worker / bridge、模型桥、截图和工作台归入统一任务生命周期。

## 默认输出口径

普通最终回复默认不附进度表、表单或表 A/B/C，只说明本轮完成内容、证据和风险。只有用户明确点名状态、进度、完整交接、审计、表 A/B/C、表 C、Core Proof Coverage 或刷新表 C 时，才展开历史表格；展开时必须说明表 C 不是端到端真实能力。

## 当前 next

先执行架构归并与文档 / 入口 / 产物治理，不默认恢复训练。允许的小步是：仓库治理链、模型型 Agent no-CAD 链、单项真实 CAD preview 链三者中选一条最小闭环；CAD 可用时仍只写 `CODEX_PREVIEW` 并做 readback。

## 活跃事实

- **ARCH-CONVERGENCE-01**：唯一主线见 `CORE_RESTRUCTURE_PLAN.md` §0.2；架构解释见 `docs/architecture/system-architecture-convergence.md`；OpenSpec 见 `openspec/changes/unify-system-architecture-canvas/`。
- **Core Proof Coverage**：旧表 C 只表示底座证据覆盖，机器值以 `output/validation_runs/capability-lab/cad_capability_coverage.json` 为准；真实任务成熟度另看 `Agent Task Maturity`。
- **训练暂停边界**：CAD Designer Agent 成长路径、V2 训练地图、`Visual-First` / `visual_parts` 链路和基础 CAD 操作事实源保留；正式训练恢复前先过架构归并、数据防膨胀和证据闭合。
- **入口与权限治理**：入口 custody、denylist / kill switch、training report claim audit、model trace claim audit 已进入机器检查链；后续继续补最高风险真实写入入口的 runtime guard。
- **文档反膨胀治理**：根侧包 `ARCH_DOC_GOVERNANCE_BOUNDARY_PACKAGE.md` 已定义永生文档事实源边界；`scripts/run_doc_governance_audit.py` 输出 `immortal_doc_bloat` warning 作为后续瘦身依据。
- **系统资产边界**：沉淀走系统资产四件套和 `pipeline_asset_governor`；复用走 `core.assets.system_asset_reuse` / `scripts/reuse_system_asset.py`，当前业务 DWG 默认不保存。
- **模型型 Agent 边界**：模型只能请求工具和输出判断；CAD 写入、保存、删除、sourceSpec、readback、closeout 和表 C 都不能被模型文本替代。主 Agent 认知优化已拆入 OpenSpec `prove-main-agent-cognition-loop` 并完成 no-CAD 机器闭环；真实任务层面仍需 before / after 行为改变证据。
- **训练工作台边界**：`capability-map-data.js`、HTML、sync report、retention report 都是 derived / diagnostic，不得反向当训练事实源。

## 口令路由

| 用户口令 | 默认动作 |
| --- | --- |
| 架构归并 / 重画架构 / 先整理框架 | 执行 `ARCH-CONVERGENCE-01`，不新开训练 |
| CAD 基础课 / 总设计师训练 | 先提醒训练暂停；用户明确覆盖时只选 1 个 focused 目标 |
| 试一下 / 快画 / 小动作 / 先别沉淀 | `quick_trial`：只写 `CODEX_PREVIEW`，做关键 readback，不沉淀 |
| 开一轮训练 / 家装案例 | `brief.md` -> 计划 -> `CODEX_PREVIEW` -> `feedback.md` |
| 刷新表 C | 只跑 coverage，不新开包 |
| 打开训练工作台 | 优先 `start_training_workbench.bat` 或 `$py scripts\sync_training_workbench.py` |
| 画不准 | 先读 `docs/runbooks/blocker-playbook.md` |

## 主从关系

- `CORE_RESTRUCTURE_PLAN.md` 是唯一 `PlanMD`。
- `docs/planning/任务清单.md` 是执行台账和即时 next 镜像。
- `CORE_STATUS.md` 解释能力状态和表 C，机器值以 coverage JSON 为准。
- `docs/status/current.md` 写当前状态；`docs/status/changelog.md` 写历史流水；`docs/status/issues.md` 写风险和教训。
- `docs/handoffs/current.md` 写最近包交接；`docs/handoffs/package-index.md` 查全量包。
- `docs/training/training-sources.json` 是训练事实源；工作台和 sync report 只是派生显示。

## 不能声称

- 不能把 Core 进度、RCAD 数量、截图、dry-run、no-CAD benchmark 或旧表 C 百分比说成“已经能画准施工图”。
- 不能把 quick trial、schema pass、fake driver、model review pass 当成训练通过、系统资产 verified 或项目交付准备。
- 不能默认保存、覆盖、删除 DWG，不能修改正式图层；真实 CAD 默认只写 `CODEX_PREVIEW`。

## 按需展开

| 目标 | 先读 |
| --- | --- |
| 架构归并 | `docs/architecture/system-architecture-convergence.md` + `CORE_RESTRUCTURE_PLAN.md` |
| 文档治理 / 反膨胀 | `ARCH_DOC_GOVERNANCE_BOUNDARY_PACKAGE.md` + `scripts/run_doc_governance_audit.py` |
| 入口 custody / 权限安全 | `config/entrypoint_custody_manifest.json` + `scripts/run_entrypoint_custody_audit.py` |
| 模型型 Agent / Tool Contract / 认知证明 | `CORE_RESTRUCTURE_PLAN.md` §0.1 + `agents/pipeline/README.md` + `openspec/changes/prove-main-agent-cognition-loop/` |
| CAD Designer Agent 训练 | `docs/training/cad-designer-growth-path.md` + `docs/training/README.md` |
| 资产沉淀 / 复用 | `docs/architecture/system-asset-sedimentation-protocol.md` + `core/assets/semantic_rules.py` |
| 完整能力状态 | `CORE_STATUS.md` + `docs/status/current.md` + coverage JSON |
| 历史 / 风险 / 交接 | `docs/status/changelog.md` / `docs/status/issues.md` / `docs/handoffs/current.md` |

## 常用验证

固定 `$py="$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"` 后运行：`-m unittest discover -s tests`、`scripts\run_doc_governance_audit.py`、`scripts\run_entrypoint_custody_audit.py --fail-on-blocked`、`scripts\run_training_report_claim_audit.py --reports <report_root> --fail-on-blocked`、`scripts\run_capability_coverage.py --output output\validation_runs\capability-lab\cad_capability_coverage.json`。
