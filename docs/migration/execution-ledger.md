# CAD Agent vNext Migration Execution Ledger

本文记录 vNext migration 阶段执行事实。它不是 PlanMD，不承载第二套 next；唯一 PlanMD 是 `CORE_RESTRUCTURE_PLAN.md`。

## Phase 0 - Baseline & Inventory

日期：2026-06-14

状态：completed，口头交付，未落盘。

来源说明：Phase 0 在旧工作区 `C:\Users\User\Desktop\CAD-AGENT` 完成，只读输出包括 repo-inventory 草案、root-cleanup-ledger 草案、deletion-ledger 草案、protected evidence 清单、主线冲突清单和 Phase 1 文件建议。该轮未创建 `docs/migration/**` 文件。

关键结论：

- 当前旧仓库是 Legacy Core + Evidence Harness。
- 旧 `main` 有未提交 `output/validation_runs/**`、worker 类型文件和 untracked Word 母标准变化。
- 新 vNext 迁移应在隔离 worktree 中执行。
- 不删除、不移动、不改写 `output/**`、`projects/**`、`libraries/**`、registry、training-sources、OpenSpec active changes 和历史失败教训。

验证：

- `git status --short --branch`：旧工作区已检查。
- 真实 CAD：not_run。
- 训练同步：not_run。
- coverage / 表 C：not_run。
- doc governance audit：not_run。

## Phase 1 - 主线改旗

日期：2026-06-14

状态：completed

施工区：

- Worktree：`C:\Users\User\Desktop\CAD Agent WorkTree`
- 分支：`vnext-main`

目标：

- 将活跃入口统一改为 CAD Agent vNext Migration。
- 将旧 `ARCH-CONVERGENCE-01` 降级为已完成 / 被吸收的上一阶段架构归并成果。
- 不执行训练、表 C、插件、真实 CAD 或事实源移动。

修改文件：

- `README.md`
- `CORE_CONTEXT_BRIEF.md`
- `CORE_RESTRUCTURE_PLAN.md`
- `docs/planning/任务清单.md`
- `docs/migration/execution-ledger.md`

未触碰文件 / 路径：

- `AGENTS.md`
- Target Architecture RFC source files, moved in Phase 2 to `docs/rfcs/`
- `CAD_AGENT_vNext_v2_2_FINAL.docx`
- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- 任何 DWG

验证记录：

- `git diff -- README.md CORE_CONTEXT_BRIEF.md CORE_RESTRUCTURE_PLAN.md docs\planning\任务清单.md docs\migration\execution-ledger.md`：passed，diff 只覆盖 Phase 1 允许文件。
- legacy-current-main conflict search：passed。初次搜索的误报来自允许的降级说明和 ledger 命令文本，已调整同句表述并重跑；活跃入口未再把 `ARCH-CONVERGENCE-01` 写成当前主线或当前 next。
- doc governance audit：not_run
- OpenSpec validate：not_run
- tests：not_run
- coverage / 表 C：not_run
- training sync：not_run
- real CAD：not_run

事实源影响：none。仅文档控制面改旗。

能力声明边界：本阶段只证明活跃入口主线口径对齐，不证明 CAD 能力提升、训练恢复、表 C 提升、插件可用或真实 CAD preview 通过。

## Phase 2 - Target RFC 归位

日期：2026-06-14

状态：completed

目标：

- 将两份根级中文目标架构 MD 移入 `docs/rfcs/`。
- 修正活跃入口和 migration ledger 中的引用。
- 明确 RFC 是 Target Architecture RFC source，不承载 PlanMD、不定义 current next、不作为执行台账。

移动文件：

- `超级CADAgent系统架构参考文档.md` -> `docs/rfcs/vnext-super-cad-agent-architecture.md`
- `CAD工具演进与原生插件引入阶段说明.md` -> `docs/rfcs/vnext-tool-layer-native-plugin-roadmap.md`

新增文件：

- `docs/rfcs/README.md`
- `docs/migration/root-cleanup-ledger.md`

修改引用：

- `README.md`
- `CORE_CONTEXT_BRIEF.md`
- `CORE_RESTRUCTURE_PLAN.md`
- `docs/migration/execution-ledger.md`

未触碰文件 / 路径：

- `AGENTS.md`
- `CAD_AGENT_vNext_v2_2_FINAL.docx`
- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- 任何 DWG

验证记录：

- old root RFC filename search：passed。旧根目录文件名只保留在 migration / cleanup ledger 的 move mapping 中，均指向 `docs/rfcs/` 新路径；RFC 内部交叉链接已改为新文件名。
- `git diff --stat`：checked。未 staged 时 Git 将 move 显示为 root delete + `docs/rfcs/` untracked；`git status` 确认两份 RFC 已位于 `docs/rfcs/`。
- PlanMD uniqueness search：passed。`README.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_RESTRUCTURE_PLAN.md` 和 migration docs 仍声明唯一 PlanMD 是 `CORE_RESTRUCTURE_PLAN.md`。
- doc governance audit：not_run
- tests：not_run
- coverage / 表 C：not_run
- training sync：not_run
- real CAD：not_run

事实源影响：none。仅 RFC 归位和引用修复。

能力声明边界：RFC 归位只证明目标架构文档已有明确位置和权威边界；不证明 Tool Gateway、Evidence Ledger、Workbench、插件、训练、表 C 或真实 CAD 能力已落地。

## Phase 2 Closeout Patch - Phase 3 handoff

日期：2026-06-14

状态：completed

目标：

- 不进入 Phase 3 施工，只补齐 Phase 2 closeout 后的控制面口径。
- 将 `docs/planning/任务清单.md` 的 current active phase 改为 Phase 3：根目录治理与旧主线 MD 分层。
- 将 Phase 2 明确标为 completed：两份 RFC 已迁入 `docs/rfcs/`，不再承载 PlanMD / next。
- 更新口令表：`继续迁移` 默认进入 Phase 3；Phase 2 / RFC 归位只作为已完成记录查看。

修改文件：

- `docs/planning/任务清单.md`
- `docs/migration/execution-ledger.md`

未触碰文件 / 路径：

- 代码文件
- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- 任何 DWG

验证记录：

- Phase handoff stale-reference search：passed。未再命中 `docs/planning/任务清单.md` / `docs/migration/execution-ledger.md` 中的旧 current Phase 1 / next Phase 2 口径。
- Phase handoff positive-reference search：checked。`docs/planning/任务清单.md` 已显示 active Phase 3、Phase 2 completed 和 `继续迁移` 默认进入 Phase 3。
- old root RFC filename search：passed。旧根级 RFC 文件名只保留在 `docs/migration/root-cleanup-ledger.md` 与 `docs/migration/execution-ledger.md` 的 move mapping 中，均指向 `docs/rfcs/` 新路径。
- `git status --short`：checked。工作区仍包含 Phase 2 RFC move / docs migration 的未提交状态；本 closeout patch 只修改 `docs/planning/任务清单.md` 和 `docs/migration/execution-ledger.md`。
- tests：not_run
- coverage / 表 C：not_run
- training sync：not_run
- real CAD：not_run

事实源影响：none。仅同步 Phase 2 closeout 与 Phase 3 handoff 文档口径。

## Phase 3 - 根目录治理与旧主线 MD 分层

日期：2026-06-14

状态：completed

目标：

- 清点根目录文件，并按 active_control、external_authority_source、rfc_source、governance、runbook、deploy_checklist、derived_view、local_artifact、protected_evidence、binary_reference、archive_candidate 分类。
- 低风险根级 Markdown 可移动；高风险事实源、二进制、派生视图和 protected evidence 只登记不移动。
- 完成后将当前 next 指向 Phase 4：规则压缩。

新增文件：

- `docs/migration/repo-inventory.md`
- `docs/migration/deletion-ledger.md`

移动文件：

- `ARCH_DOC_GOVERNANCE_BOUNDARY_PACKAGE.md` -> `docs/governance/arch-doc-governance-boundary-package.md`
- `WORKER_ORCHESTRATOR_DEPLOY_CHECKLIST.md` -> `docs/deploy/worker-orchestrator-deploy-checklist.md`

修改引用：

- `README.md`
- `CORE_CONTEXT_BRIEF.md`
- `CORE_RESTRUCTURE_PLAN.md`
- `CORE_STATUS.md`
- `docs/planning/任务清单.md`
- `docs/status/current.md`
- `docs/status/changelog.md`
- `docs/handoffs/current.md`
- `core/maintenance/doc_governance.py`
- `scripts/build_runtime_trace_snapshot.py`
- `workers/orchestrator/scripts/secret-scan.mjs`
- `docs/governance/arch-doc-governance-boundary-package.md`
- `docs/migration/root-cleanup-ledger.md`
- `docs/migration/execution-ledger.md`

只登记未移动：

- `CORE_STATUS.md`
- `MODEL_DATA_EXPORT_AUTHORIZATION.md`
- `capability-map.html`
- `capability-map-data.js`
- `cad_mcp.log`
- `Claude Code DeepSeek.lnk`
- `超全家装工装CAD总图库.dwg`
- `CAD_AGENT_vNext_v2_2_FINAL.docx`：当前 worktree absent，仅登记为 external authority source。

未触碰文件 / 路径：

- `AGENTS.md` 未压缩，留到 Phase 4。
- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- 任何 DWG

验证记录：

- moved old-path search：passed。`rg 'ARCH_DOC_GOVERNANCE_BOUNDARY_PACKAGE\.md|WORKER_ORCHESTRATOR_DEPLOY_CHECKLIST\.md'` 排除 `docs/migration/**`、protected evidence、依赖目录和派生快照后无输出；旧路径只保留在 migration ledger / inventory 的 move mapping 中。
- active phase search：checked。`README.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_RESTRUCTURE_PLAN.md` 和 `docs/planning/任务清单.md` 已指向 Phase 4：规则压缩；历史 Phase 2 closeout 记录仍保留“当时进入 Phase 3”的事实。
- new path search：checked。新路径 `docs/governance/arch-doc-governance-boundary-package.md` 与 `docs/deploy/worker-orchestrator-deploy-checklist.md` 已在 README、brief、status、handoff、code path constants 和 migration docs 中出现。
- root file list：checked。根目录不再包含两份已移动 Markdown；仍保留 active control、派生视图、本机 artifact、授权文档和大型 DWG。
- `git diff --stat`：checked。Git 对未 staged move 显示为 root delete + untracked destination；具体状态以 `git status --short` 为准。
- `git status --short`：checked。显示 Phase 2 RFC move、Phase 3 Markdown move、文档更新和新增 `docs/migration/**` / `docs/deploy/**` / `docs/rfcs/**` 的未提交状态。
- doc governance audit：ran_with_findings。命令为 `$py scripts\run_doc_governance_audit.py --fail-on-findings`，返回 `status=findings` / `finding_count=6`；links、root stubs、active doc size、handoff、OpenSpec contracts、table C semantic boundary 等子项 pass。findings 来自旧训练上下文 token、README architecture hardening token 和永生文档重复 / completed fact 警告；本轮不把这些旧 checker 期待硬塞回 Phase 3 文档，留待 Phase 4 规则压缩处理。
- tests：not_run
- coverage / 表 C：not_run
- training sync：not_run
- real CAD：not_run

事实源影响：none。未移动、未删除、未改写 protected evidence。

能力声明边界：根目录治理只证明控制面和文件分层更清晰；不证明 CAD 能力提升、训练恢复、表 C 提升、插件可用或真实 CAD preview 通过。

## Phase 4 - 规则压缩第一包：旧主线阻断项修复

日期：2026-06-14

状态：checked

目标：

- 处理 Phase 3 review 暴露的阻断项。
- 将 `AGENTS.md`、`CORE_STATUS.md`、`docs/status/current.md` 和 `docs/governance/cad-agent-rules.md` 中仍把旧架构归并写成当前主线的表述改为 vNext migration。
- 调整文档治理 checker / tests：Visual-First / `visual_parts` 保留在训练文档要求里，不再强制出现在 vNext active control 文档；README 不再必须承载旧 architecture hardening token。
- 保留 `docs/planning/任务清单.md` 中“真实 CAD 实力 / 推进表 C / 刷新表 C”的路由边界，并明确当前阶段暂停。

修改文件：

- `AGENTS.md`
- `CORE_STATUS.md`
- `docs/status/current.md`
- `docs/governance/cad-agent-rules.md`
- `core/maintenance/doc_governance.py`
- `tests/core/test_doc_governance.py`
- `README.md`
- `CORE_CONTEXT_BRIEF.md`
- `CORE_RESTRUCTURE_PLAN.md`
- `docs/planning/任务清单.md`

验证记录：

- legacy-current-main route search：passed。旧架构归并仅作为 legacy mapping / evidence baseline 出现，不再定义 current next。
- doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- `git diff --check`：passed。退出码 0；仅出现 LF 将在 Git 触碰时替换为 CRLF 的工作区警告。

未触碰文件 / 路径：

- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包只证明旧主线阻断项被移出 active control，不证明 CAD 能力提升、训练恢复、表 C 提升、插件可用或真实 CAD preview 通过。

## Phase 4 - 规则压缩第二包：AGENTS 启动路由器

日期：2026-06-14

状态：checked

目标：

- 将 `AGENTS.md` 从长规则仓库压缩为启动路由器 + 高风险边界索引。
- 只在根级启动卡片保留默认中文输出、`CORE_CONTEXT_BRIEF.md` 首读、唯一 PlanMD、vNext / Phase 4 路由、protected evidence 硬边界和高风险入口索引。
- 把长期细则明确指向 governance / training / asset / migration 文档。
- 不改变 CAD 行为，不恢复训练，不推进表 C，不做插件，不写真实 CAD，不移动或改写 protected evidence。

修改文件：

- `AGENTS.md`
- `CORE_CONTEXT_BRIEF.md`
- `CORE_RESTRUCTURE_PLAN.md`
- `docs/planning/任务清单.md`
- `docs/migration/execution-ledger.md`

长期规则归位：

- 长期治理、CAD 写入、状态口径、模型桥和收口验证：`docs/governance/cad-agent-rules.md`
- 训练路由、Visual-First、`visual_parts`、`reference_match` 和案例训练边界：`docs/training/README.md`、`docs/training/cad-designer-growth-path.md`
- 系统资产沉淀、复用、native source 和 registry 边界：`docs/architecture/system-asset-sedimentation-protocol.md`
- 迁移执行事实、Phase closeout、根目录分类和未触碰边界：`docs/migration/execution-ledger.md`

未触碰文件 / 路径：

- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`

验证记录：

- legacy-current-main route search：passed。`AGENTS.md` 未再命中 `当前主线`、`当前主工程`、`ARCH-CONVERGENCE-01` 或 `架构归并画布`；命中项仅保留在 PlanMD、任务清单、status 和 governance 的 vNext / legacy mapping 说明中。
- doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- `git diff --check`：passed。退出码 0；仅出现 LF 将在 Git 触碰时替换为 CRLF 的工作区警告。

能力声明边界：本阶段只证明启动规则压缩和长期规则归位；不证明 CAD 能力提升、训练恢复、表 C 提升、插件可用或真实 CAD preview 通过。

## Phase 4 - 第三包：closeout 与 Phase 5 handoff 门禁

日期：2026-06-14

状态：checked

目标：

- 检查 `AGENTS.md` 是否已经降成轻启动入口，长期规则是否归位到 governance / training / asset / migration 文档。
- 检查 `README.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_RESTRUCTURE_PLAN.md`、`docs/planning/任务清单.md`、`CORE_STATUS.md` 和 `docs/status/current.md` 不互相抢 current next。
- 检查旧 `ARCH-CONVERGENCE-01` 只能作为历史 / legacy mapping 出现，不能再声明为当前主线。
- 若验收全绿，将 current next 切到 Phase 5：vNext Contracts；本包不进入 Phase 5 实现。

修改文件：

- `AGENTS.md`
- `README.md`
- `CORE_CONTEXT_BRIEF.md`
- `CORE_RESTRUCTURE_PLAN.md`
- `CORE_STATUS.md`
- `docs/planning/任务清单.md`
- `docs/status/current.md`
- `docs/migration/execution-ledger.md`

门禁判断：

- pre-switch doc governance audit：passed，`status=pass` / `finding_count=0`。
- pre-switch tests：passed，45 项 OK。
- pre-switch OpenSpec validate：passed，20/20 passed。
- pre-switch `git diff --check`：passed，退出码 0，仅 CRLF 工作区警告。
- current next handoff：Phase 4 可收口，current next 已切到 Phase 5：vNext Contracts；不启动实现。

- final validation：passed。阶段切换文本回写后曾触发一次 `CORE_RESTRUCTURE_PLAN.md` active doc size blocker（142 lines > 140）；已将 Phase 3 细节退回 migration ledger，PlanMD 压回 105 lines 后重新运行验收。
- final doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- final tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- final OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final route search：checked。活跃入口 current next 已指向 Phase 5；旧 `ARCH-CONVERGENCE-01` 仅作为降级 / legacy mapping / 历史入口出现。
- final `git diff --check`：passed。退出码 0；仅出现 LF 将在 Git 触碰时替换为 CRLF 的工作区警告。

未触碰文件 / 路径：

- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`

能力声明边界：本包只判断 Phase 4 是否可收口与是否允许进入 Phase 5 next；不证明 CAD 能力提升、训练恢复、表 C 提升、插件可用或真实 CAD preview 通过。

## Phase 5 - 第一包：vNext Contracts skeleton

日期：2026-06-14

状态：checked

目标：

- 从 `docs/rfcs/vnext-super-cad-agent-architecture.md` 与 `docs/rfcs/vnext-tool-layer-native-plugin-roadmap.md` 抽取最小合同骨架；RFC 只作 source，不替代 PlanMD。
- 在 Core 建立 `TaskObject`、`ToolContract`、`ToolCard`、`EvidencePackage`、`CompletionJudge` skeleton。
- 用负例测试固定 fail-closed 边界：模型文本不能替代 EvidencePackage；fake / dry-run / screenshot 不能冒充真实 CAD readback；ToolCard 不能越权；CompletionJudge 缺 evidence 时必须 blocked / not_verified；Phase 5 skeleton 不能改 protected evidence。

新增文件：

- `core/contracts/__init__.py`
- `core/contracts/vnext.py`
- `tests/core/test_vnext_contracts.py`

修改文件：

- `CORE_RESTRUCTURE_PLAN.md`
- `docs/planning/任务清单.md`
- `docs/migration/execution-ledger.md`

验证记录：

- TDD red：`$py -m unittest tests.core.test_vnext_contracts -v` 初次运行失败于 `ModuleNotFoundError: No module named 'core.contracts'`。
- TDD green：`$py -m unittest tests.core.test_vnext_contracts -v` 运行 6 项，全部 OK。
- final doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- final PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- final OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed。退出码 0；仅出现 LF 将在 Git 触碰时替换为 CRLF 的工作区警告。
- final protected evidence diff check：passed。`git diff --name-only -- output projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec` 无输出。

未触碰文件 / 路径：

- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`

能力声明边界：本包只建立合同描述、证据判定和负例门禁；不证明 CAD 能力提升、训练恢复、表 C 提升、插件可用或真实 CAD preview 通过。

## Phase 5 - 第二包：vNext Contracts no-CAD roundtrip

日期：2026-06-14

状态：checked

目标：

- 基于第一包 `TaskObject` / `ToolContract` / `ToolCard` / `EvidencePackage` / `CompletionJudge` skeleton，新增一条不触发真实 CAD 的合同闭环验证。
- roundtrip 只覆盖：TaskObject fixture -> ToolCard fixture -> ToolContract -> EvidencePackage -> CompletionJudge。
- 用正反例 fixture 固定边界：合同完整但无真实 CAD readback 只能 `not_verified`；缺 EvidencePackage 必须 `blocked`；ToolCard permission 不足必须 `blocked`；模型文本声称完成但缺 deterministic evidence 必须 `blocked`；no-CAD 合同闭环通过只能声明 contract roundtrip ready，不能声明 CAD geometry verified。

新增文件：

- `tests/core/test_vnext_contract_roundtrip.py`

修改文件：

- `core/contracts/__init__.py`
- `core/contracts/vnext.py`
- `CORE_RESTRUCTURE_PLAN.md`
- `docs/planning/任务清单.md`
- `docs/migration/execution-ledger.md`

验证记录：

- TDD red：`$py -m unittest tests.core.test_vnext_contract_roundtrip -v` 初次运行失败于 `ImportError: cannot import name 'run_no_cad_contract_roundtrip' from 'core.contracts.vnext'`。
- TDD green：`$py -m unittest tests.core.test_vnext_contracts -v` 运行 6 项，全部 OK；`$py -m unittest tests.core.test_vnext_contract_roundtrip -v` 运行 5 项，全部 OK。
- final doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- final OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed。退出码 0；仅出现 LF 将在 Git 触碰时替换为 CRLF 的工作区警告。
- final protected evidence diff check：passed。`git diff --name-only -- output projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec` 无输出。

未触碰文件 / 路径：

- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`

能力声明边界：本包只证明合同链 no-CAD roundtrip 可被生成、授权、证据化和裁判；不证明 CAD 几何、真实 CAD readback、训练恢复、表 C 提升、插件可用或 Worker 链路可用。

## Phase 5 - 第三包：vNext Contracts read-only adapter

日期：2026-06-14

状态：checked

目标：

- 基于前两包合同 skeleton 和 no-CAD roundtrip，新增只读 adapter，把 `TaskObject` 转成 `CAD_PLAN` candidate / structured intent，把 `ToolContract` 限定为 validate / dry-run request，把 validate / dry-run result 转成 `EvidencePackage`，再交给 `CompletionJudge`。
- 固定证据边界：validate pass 只证明 schema / plan 合法；dry-run pass 只证明预演可行；没有 created handles readback 时不得 `geometry_verified`；CompletionJudge 最多给 `contract_ready_non_cad` / `not_verified`，不得给真实 CAD 完成。
- 用负例覆盖 validate pass + dry-run pass 但无 readback、validate fail、dry-run fail、模型文字不能覆盖 deterministic evidence。

新增文件：

- `tests/core/test_vnext_contract_adapters.py`

修改文件：

- `core/contracts/__init__.py`
- `core/contracts/vnext.py`
- `CORE_RESTRUCTURE_PLAN.md`
- `docs/planning/任务清单.md`
- `docs/migration/execution-ledger.md`

验证记录：

- TDD red：`$py -m unittest tests.core.test_vnext_contract_adapters -v` 初次运行失败于 `ImportError: cannot import name 'run_read_only_cad_plan_adapter' from 'core.contracts.vnext'`。
- TDD green：`$py -m unittest tests.core.test_vnext_contract_adapters -v` 运行 5 项，全部 OK。
- contract regression：`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters -v` 运行 16 项，全部 OK。
- final doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- final OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed。退出码 0；仅出现 LF 将在 Git 触碰时替换为 CRLF 的工作区警告。
- final protected evidence diff check：passed。`git diff --name-only -- output projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec` 无输出。

未触碰文件 / 路径：

- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`

能力声明边界：本包只证明合同层可以只读包住 `CAD_PLAN` validate / dry-run 并生成可裁判证据；不证明 CAD 几何、真实 CAD readback、训练恢复、表 C 提升、插件可用或 Worker 链路可用。

## Phase 5 - 第四包：closeout 与 Phase 6 handoff 门禁

日期：2026-06-14

状态：checked

目标：

- 检查 Phase 5 三包是否形成闭环：合同 skeleton、no-CAD roundtrip、validate / dry-run read-only adapter。
- 检查证据边界：模型文本不能替代 EvidencePackage；validate / dry-run 不能冒充真实 CAD readback；没有 created handles 时不得 `geometry_verified`；CompletionJudge 缺证据必须 blocked / not_verified。
- 检查 active docs 一致性；若全绿，只把 current next 切到 Phase 6：Legacy Gateway，不启动 Phase 6 实现。

修改文件：

- `README.md`
- `AGENTS.md`
- `CORE_CONTEXT_BRIEF.md`
- `CORE_RESTRUCTURE_PLAN.md`
- `docs/planning/任务清单.md`
- `docs/migration/execution-ledger.md`

门禁判断：

- pre-switch contracts：passed。`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters -v` 运行 16 项，全部 OK。
- pre-switch doc governance audit：passed。`$py scripts/run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- pre-switch PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- pre-switch OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- current next handoff：Phase 5 可收口，current next 已切到 Phase 6：Legacy Gateway；不启动实现。
- final validation：passed。合同三组单测运行 16 项全部 OK；doc governance audit 返回 `status=pass` / `finding_count=0`；PlanMD / doc governance 单测运行 45 项全部 OK；OpenSpec validate 返回 20/20 passed；route search 确认 active docs current next 已指向 Phase 6，Phase 5 仅作为 completed / history / closeout 出现；`git diff --check` 退出码 0，仅 CRLF 工作区警告；protected evidence diff check 无输出。

未触碰文件 / 路径：

- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`

能力声明边界：本包只判断 Phase 5 是否可收口与是否允许进入 Phase 6 next；不证明 CAD 能力提升、训练恢复、表 C 提升、插件可用或真实 CAD preview 通过。

## Phase 6 - 第一包：Legacy Gateway skeleton

日期：2026-06-14

状态：checked

目标：

- 基于 Phase 5 合同层新增 Legacy Gateway skeleton，只登记 legacy validate / dry-run / preview / readback adapter 的能力卡、permission class、allowed evidence 和 forbidden effects。
- preview adapter 只登记，不调用 AutoCAD；readback adapter 只登记，不读取真实 DWG。
- 用负例固定边界：preview 未显式授权不得写 CAD；readback 缺 created handles 不得 `geometry_verified`；dry-run / screenshot / model text 不能冒充 readback；gateway 不得保存 DWG、不改 registry、不推进表 C。

新增文件：

- `core/contracts/legacy_gateway.py`
- `tests/core/test_legacy_gateway.py`

修改文件：

- `core/contracts/__init__.py`
- `CORE_RESTRUCTURE_PLAN.md`
- `docs/planning/任务清单.md`
- `docs/migration/execution-ledger.md`

验证记录：

- TDD red：`$py -m unittest tests.core.test_legacy_gateway -v` 初次运行失败于 `ModuleNotFoundError: No module named 'core.contracts.legacy_gateway'`。
- TDD green：`$py -m unittest tests.core.test_legacy_gateway -v` 运行 5 项，全部 OK。
- contract regression：`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway -v` 运行 21 项，全部 OK。
- final doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- final OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed。退出码 0；仅出现 LF 将在 Git 触碰时替换为 CRLF 的工作区警告。
- final protected evidence diff check：passed。`git diff --name-only -- output projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec` 无输出。

未触碰文件 / 路径：

- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`

能力声明边界：本包只建立 Legacy Gateway skeleton 和负例门禁；不证明 CAD 能力提升、训练恢复、表 C 提升、插件可用或真实 CAD preview / readback 通过。

## Phase 6 - 第二包：Legacy Gateway validate / dry-run adapter

日期：2026-06-14

状态：checked

目标：

- 基于第一包 Legacy Gateway skeleton，把旧 `CAD_PLAN` validate / dry-run 入口接入 Phase 5 合同层。
- 将 `ToolContract` 转为 legacy validate / dry-run request，再将 validate / dry-run result 转为 `EvidencePackage` 并交给 `CompletionJudge`。
- 用负例固定边界：validate pass + dry-run pass 仍只能 `contract_ready_non_cad`；validate fail 必须 `blocked`；dry-run fail 必须 `blocked` / `not_verified`；模型文本不能覆盖 deterministic evidence。
- 本包只读，不调用 preview / AutoCAD / CAD-MCP，不写 DWG，不保存，不改 registry，不推进表 C。

新增文件：

- `tests/core/test_legacy_gateway_adapters.py`

修改文件：

- `core/contracts/legacy_gateway.py`
- `core/contracts/vnext.py`
- `core/contracts/__init__.py`
- `CORE_RESTRUCTURE_PLAN.md`
- `docs/planning/任务清单.md`
- `docs/migration/execution-ledger.md`

验证记录：

- TDD red：`$py -m unittest tests.core.test_legacy_gateway_adapters -v` 初次运行 5 项均失败于 `ImportError: cannot import name 'run_legacy_validate_dry_run_adapters'`。
- TDD green：`$py -m unittest tests.core.test_legacy_gateway_adapters -v` 运行 5 项，全部 OK。
- contract regression：`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters -v` 运行 26 项，全部 OK。
- final doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- final OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed。退出码 0；仅出现 LF 将在 Git 触碰时替换为 CRLF 的工作区警告。
- final protected evidence diff check：passed。`git diff --name-only -- output projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec` 无输出。

未触碰文件 / 路径：

- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`

能力声明边界：validate pass 只证明 schema / plan 合法；dry-run pass 只证明预演可行；没有 created handles readback 时不得 `geometry_verified`。本包不证明 CAD 能力提升、训练恢复、表 C 提升、插件可用或真实 CAD preview / readback 通过。

## Phase 6 - 第三包：Legacy Gateway preview / readback registration guards

日期：2026-06-14

状态：checked

目标：

- 基于第一包 Legacy Gateway skeleton 和第二包 validate / dry-run adapter，补齐 legacy preview / readback 入口的登记与护栏。
- preview 只登记可被授权的预览请求，默认不执行；request 与 evidence 均显式 `executes_cad=false`、`writes_dwg=false`、`saves_dwg=false`、`savedCurrentDwg=false`。
- preview 如有 layer 字段，只允许 `CODEX_PREVIEW`；请求 `cad_preview_write`、正式图层写入、DWG save、registry mutation 或 Table C mutation 必须 blocked。
- readback 登记依赖 created handles；缺 handles 时只能 `blocked` / `not_verified`，不得 `geometry_verified`。
- screenshot / dry-run / model text 不能冒充真实 readback。

新增文件：

- `tests/core/test_legacy_gateway_preview_readback.py`

修改文件：

- `core/contracts/legacy_gateway.py`
- `core/contracts/__init__.py`
- `CORE_RESTRUCTURE_PLAN.md`
- `docs/planning/任务清单.md`
- `docs/migration/execution-ledger.md`

验证记录：

- TDD red：`$py -m unittest tests.core.test_legacy_gateway_preview_readback -v` 初次运行 6 项，其中 5 项失败于 `ImportError: cannot import name 'run_legacy_preview_registration'` / `run_legacy_readback_registration`，既有 forbidden effects 用例已通过。
- TDD green：`$py -m unittest tests.core.test_legacy_gateway_preview_readback -v` 运行 6 项，全部 OK。
- contract regression：`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback -v` 运行 32 项，全部 OK。
- final doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- final OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed。退出码 0；仅出现 LF 将在 Git 触碰时替换为 CRLF 的工作区警告。
- final protected evidence diff check：passed。`git diff --name-only -- output projects libraries docs/training/training-sources.json libraries/system_library/registry.json openspec agents/pipeline/pipeline_manifest.json config/entrypoint_custody_manifest.json` 无输出。

未触碰文件 / 路径：

- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包只证明 preview / readback registration guards 在合同层可裁判；preview registered 不证明 CAD 已写入，readback registered 缺 created handles 不证明 geometry。未调用真实 CAD、AutoCAD、CAD-MCP 或 plugin；未保存或修改 DWG/DWT；未训练、未同步 training sources、未改 registry、未推进表 C。

## Phase 6 - 第四包：Legacy Gateway closeout 与 Phase 7 handoff 门禁

日期：2026-06-14

状态：checked

目标：

- 对 Phase 6 的五个边界做总校验：legacy gateway skeleton、validate adapter、dry-run adapter、preview registration guards 和 readback registration guards。
- 确认 Legacy Gateway 只作为旧入口适配层，不绕过 Phase 5 contracts；validate / dry-run / preview / readback 均有 `ToolCard`、`ToolContract`、permission class 和 `EvidencePackage` 边界。
- 确认 `CompletionJudge` 口径保持区分：schema / plan valid、dry-run feasible、preview registered、readback verified 和 `geometry_verified`。
- 确认没有真实 created handles readback 时不得 `geometry_verified`；screenshot、dry-run、model text 和 fixture evidence 不得冒充真实 CAD readback。
- 若验收全绿，将 current next 切到 Phase 7：Evidence Ledger；本包不启动 Phase 7 实现。

新增 / 修改文件：

- `core/contracts/legacy_gateway.py`
- `core/contracts/__init__.py`
- `tests/core/test_legacy_gateway_preview_readback.py`
- `README.md`
- `AGENTS.md`
- `CORE_CONTEXT_BRIEF.md`
- `CORE_RESTRUCTURE_PLAN.md`
- `docs/planning/任务清单.md`
- `docs/status/current.md`
- `docs/migration/execution-ledger.md`

门禁判断：

- closeout helper：新增 `legacy_gateway_phase6_closeout_summary()`，只读取 legacy adapter registry 并构造 Phase 5 `ToolContract` 授权检查；不执行 validate / dry-run / preview / readback，不调用真实 CAD，不读写 DWG。
- adapter boundary：`legacy.validate`、`legacy.dry_run`、`legacy.preview`、`legacy.readback` 均保持 `ToolCard`、permission class、allowed evidence 和 forbidden effects。
- completion boundary：validate pass 只证明 `cad_plan_validate`，dry-run pass 只证明 `cad_plan_dry_run`，preview registered 只证明 `legacy_preview_registered`，readback verified 需要 `real_cad_readback`，`geometry_verified` 需要 created handles + real CAD readback。
- no handles guard：构造缺 created handles 的 `geometry_verified` readback report 时，`EvidencePackage.satisfies("real_cad_readback") == False`。
- non-readback guard：screenshot、dry-run 和 model text 组合不能满足 `real_cad_readback`。
- handoff：Phase 6 可收口，current next 已切到 Phase 7：Evidence Ledger；不启动 Phase 7 实现。

验证记录：

- TDD red：`$py -m unittest tests.core.test_legacy_gateway_preview_readback -v` 新增 closeout 测试初次失败于 `ImportError: cannot import name 'legacy_gateway_phase6_closeout_summary'`。
- TDD green：`$py -m unittest tests.core.test_legacy_gateway_preview_readback -v` 运行 7 项，全部 OK。
- pre-doc contract regression：`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback -v` 运行 33 项，全部 OK。
- final validation：passed。合同 / gateway 回归运行 33 项全部 OK；doc governance audit 返回 `status=pass` / `finding_count=0`；PlanMD / doc governance 单测运行 45 项全部 OK；OpenSpec validate 返回 20/20 passed；`git diff --check` 退出码 0，仅 CRLF 工作区警告；protected evidence diff check 无输出。

未触碰文件 / 路径：

- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包只判断 Phase 6 是否可以收口，并在门禁通过时把 current next 切到 Phase 7。它不证明 CAD 能力提升、训练恢复、表 C 提升、插件可用、真实 CAD preview 通过、真实 readback 通过或 `geometry_verified` 能力提升。

## Phase 7 - 第一包：Evidence Ledger skeleton 与 fail-closed 门禁

日期：2026-06-14

状态：checked

目标：

- 基于 Phase 5 contracts 与 Phase 6 legacy gateway，新增最小 Evidence Ledger skeleton。
- Ledger 只记录 EvidencePackage 引用与裁判状态，不复制、不移动、不改写 protected evidence。
- CompletionJudge 新增 ledger-aware fail-closed 入口；缺 ledger record、record 指向缺失 package、record 与 package 不匹配、model text / dry-run / preview registered 冒充 readback、fixture readback 缺 created handles 均不得 completed / geometry_verified。
- 本包只做内存与 fixture 层，不写真实 ledger 文件，不调用 CAD / AutoCAD / CAD-MCP / plugin。

新增文件：

- `core/contracts/evidence_ledger.py`
- `tests/core/test_evidence_ledger.py`

修改文件：

- `core/contracts/vnext.py`
- `core/contracts/__init__.py`
- `docs/migration/execution-ledger.md`

门禁判断：

- `EvidenceLedgerRecord` / `LedgerEntry` 记录 `ledger_id`、`task_id`、`contract_id`、`evidence_package_id`、`evidence_type`、`producer`、`tool_card_id`、`verification_status`、`blocked_reason`、`not_verified_reason`、`source_ref`、`content_hash` 和 `metadata`。
- `InMemoryEvidenceLedger.append()` 只允许 append；duplicate `ledger_id` 抛出 `DuplicateLedgerIdError`；`overwrite()` / `delete()` 显式 fail-closed。
- `CompletionJudge.judge_with_ledger()` 只把同时满足 ledger record 存在、EvidencePackage 存在、task 匹配、可选 content hash 匹配、且 EvidencePackage 真正 satisfies `evidence_type` 的记录纳入 checked evidence。
- `real_cad_readback` 必须由 verified ledger record 与真实 `EvidencePackage.satisfies("real_cad_readback")` 同时满足；model text、dry-run、preview registered、缺 created handles 的 fixture readback 均不得替代。

验证记录：

- TDD red：`$py -m unittest tests.core.test_evidence_ledger -v` 首次运行 8 项均失败于 `ModuleNotFoundError: No module named 'core.contracts.evidence_ledger'`。
- TDD green：`$py -m unittest tests.core.test_evidence_ledger -v` 运行 8 项，全部 OK。
- contract / gateway regression：`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger -v` 运行 41 项，全部 OK。
- final doc governance audit：passed。`$py scripts/run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- final OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- final protected evidence diff check：passed。`git diff --name-only -- output projects libraries docs/training/training-sources.json libraries/system_library/registry.json openspec agents/pipeline/pipeline_manifest.json config/entrypoint_custody_manifest.json` 无输出。

未触碰文件 / 路径：

- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包只证明 Evidence Ledger skeleton 与 CompletionJudge fail-closed 门禁在内存 / fixture 层可被测试；不证明 CAD 能力提升、真实 CAD preview / readback 通过、`geometry_verified` 能力提升、训练恢复、表 C 推进、registry 更新、插件可用或 Worker 链路可用。当前 next 仍停留在 Phase 7，不切 Phase 8。

## Phase 7 - 第二包：Evidence Ledger closeout 与 Phase 8 handoff 门禁

日期：2026-06-14

状态：checked

目标：

- 不新增 Phase 7 功能实现，只检查第一包 Evidence Ledger skeleton 是否可收口。
- 同步活跃入口文档，明确 Phase 7 第一包已完成于内存 / fixture 层，不是真实 CAD preview / readback。
- 复核 append-only、duplicate `ledger_id` guard、ledger / package / task / hash 匹配、`real_cad_readback` fail-closed 边界。
- 确认 model text、dry-run、preview registered、fixture readback without created handles 均不能冒充 `real_cad_readback` 或 `geometry_verified`。
- 若验证全绿，将 current next 切到 Phase 8：Workbench 只读化；本包只做 handoff，不启动 Phase 8 实现。

修改文件：

- `README.md`
- `AGENTS.md`
- `CORE_CONTEXT_BRIEF.md`
- `CORE_RESTRUCTURE_PLAN.md`
- `docs/planning/任务清单.md`
- `docs/status/current.md`
- `docs/migration/execution-ledger.md`

门禁判断：

- `core/contracts/evidence_ledger.py` 保持内存 / fixture 层；无文件持久化、无 protected evidence copy / move / rewrite。
- `CompletionJudge.judge_with_ledger()` 保持 fail-closed：缺 ledger record、缺 EvidencePackage、task mismatch、content hash mismatch、EvidencePackage 不满足 `evidence_type` 均不得完成。
- `real_cad_readback` 必须由 verified ledger record 与 deterministic EvidencePackage 同时满足；model text、dry-run、preview registered 和缺 created handles readback 均不得替代。
- Phase 8 handoff 只允许后续 Workbench 展示 evidence / judge / blocked reason，不反向写事实源。

验证记录：

- Phase 5/6/7 回归：passed。`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger -v` 运行 41 项，全部 OK。
- doc governance audit：passed。`$py scripts/run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- PlanMD / doc governance 单测：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- protected evidence diff check：passed。`git diff --name-only -- output projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec agents\pipeline\pipeline_manifest.json config\entrypoint_custody_manifest.json` 无输出。
- route stale search：checked。活跃入口不再写 Phase 7 未启动；Phase 8 只作为 current next / handoff / pending 出现。

未触碰文件 / 路径：

- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包只判断 Phase 7 skeleton-level 是否可收口，并在门禁通过时把 current next 切到 Phase 8。它不证明 CAD 能力提升、真实 CAD preview / readback 通过、`geometry_verified` 能力提升、插件可用、训练恢复、表 C 推进、registry 更新或 Workbench 已实现。

## Phase 8 - 第一包：Workbench 只读投影 skeleton

日期：2026-06-14

状态：checked

目标：

- 建立最小 Workbench read-only projection skeleton。
- Projection 只消费 `TaskObject`、`EvidenceLedgerRecord` / `InMemoryEvidenceLedger`、`EvidencePackage` 和 `CompletionJudge.judge_with_ledger()`。
- 输出只读 view model：task、required / checked / missing evidence、completion / verification status、can_claim_complete、ledger records summary、EvidencePackage refs、blocked / not_verified reason、source_ref、content_hash、producer 和 tool_card_id。
- 保持 fail-closed：缺 ledger record、record 指向缺失 package、content_hash mismatch、model text / dry-run / preview registered / fixture readback without created handles 均不得显示为 `geometry_verified`。
- 保持 read-only：不 append / overwrite / delete ledger，不修改 EvidencePackage，不复制 / 移动 / 改写 protected evidence，不写真实文件作为事实源。

新增文件：

- `core/contracts/workbench_projection.py`
- `tests/core/test_workbench_projection.py`

修改文件：

- `core/contracts/__init__.py`
- `README.md`
- `CORE_CONTEXT_BRIEF.md`
- `CORE_RESTRUCTURE_PLAN.md`
- `docs/planning/任务清单.md`
- `docs/status/current.md`
- `docs/handoffs/current.md`
- `docs/migration/execution-ledger.md`

门禁判断：

- `WorkbenchProjection` 只读汇总 `CompletionJudge.judge_with_ledger()` 的 completion status、verification status、checked / missing evidence 和 can_claim_complete。
- ledger records summary 只读取 `records_for_task()` 返回值；mutation trap 测试证明 projection 不调用 append / overwrite / delete。
- EvidencePackage refs 只计算传入 package 的 content hash 和 item kinds，不复制、不写出 source_ref。
- blocked / not_verified reason 只作为展示诊断，不改变 CompletionJudge 判定，不把非 CAD evidence 变成 `geometry_verified`。
- 当前 next 仍留在 Phase 8：Workbench 只读化；不切 Phase 9。

验证记录：

- TDD red：`$py -m unittest tests.core.test_workbench_projection -v` 首次运行 6 项均失败于 `ModuleNotFoundError: No module named 'core.contracts.workbench_projection'`。
- TDD green：`$py -m unittest tests.core.test_workbench_projection -v` 运行 6 项，全部 OK。
- contract / gateway / ledger / workbench regression：`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger tests.core.test_workbench_projection -v` 运行 47 项，全部 OK。
- final doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- final PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- final OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- final protected evidence diff check：passed。`git diff --name-only -- output projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec agents\pipeline\pipeline_manifest.json config\entrypoint_custody_manifest.json` 无输出。

未触碰文件 / 路径：

- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包只证明 Workbench 只读投影 skeleton 在合同 / fixture 层可被测试；不证明完整 Workbench 产品化、CAD 能力提升、真实 CAD preview / readback 通过、`geometry_verified` 能力提升、训练恢复、表 C 推进、registry 更新、插件可用或 Worker 链路升级。

## Phase 8 - 第二包：Workbench 只读接入层与现有数据入口对齐

日期：2026-06-15

状态：checked

目标：

- 建立最小 read-only adapter，使 Phase 8 `WorkbenchProjection` 可被现有 workbench data entry 消费。
- Adapter 只把 projection 转为派生视图对象，保留 task、completion / verification status、checked / missing evidence、ledger summary、EvidencePackage refs、blocked / not_verified reason、source_ref、content_hash、producer、tool_card_id、`read_only=true` 和 `mutated_targets=[]`。
- 将 adapter 输出对齐到现有 `workbenchV3.views.evidenceCenter` / flightdeck 结构，并允许 trace viewer 附带 projection summary。
- 保持只读边界：不修改 ledger、EvidencePackage、训练事实源、registry、`output/**`、`projects/**`、`libraries/**` 或 `openspec/**`。

新增文件：

- `core/contracts/workbench_readonly_adapter.py`
- `tests/core/test_workbench_readonly_adapter.py`

修改文件：

- `core/contracts/__init__.py`
- `core/training_workbench/flightdeck.py`
- `core/training_workbench/__init__.py`
- `core/orchestrator/workbench_trace_viewer.py`
- `README.md`
- `CORE_CONTEXT_BRIEF.md`
- `CORE_RESTRUCTURE_PLAN.md`
- `docs/planning/任务清单.md`
- `docs/migration/execution-ledger.md`
- `docs/status/current.md`
- `docs/handoffs/current.md`

门禁判断：

- `build_workbench_readonly_adapter()` 只消费 `WorkbenchProjection` / dict row，不读取或写入事实源。
- Adapter 输出 `sourcePolicy.derivedOnly=true`、`readOnly=true`、`mutatedTargets=[]`，并保留 package missing、hash mismatch、blocked / not_verified reason 和 missing evidence。
- `build_workbench_v3()` 只通过可选 `contractWorkbench` / `contractWorkbenchProjections` 输入消费 adapter 输出；未提供时为空面板，不反向写训练工作台事实源。
- `build_workbench_trace_viewer_data()` 只通过可选 `contract_workbench` 附带只读摘要，不改变原有 `output/runs/**` trace 扫描行为。
- dry-run、preview registered、model text 或缺 handles fixture readback 仍不得显示为 `cad_geometry_verified`。
- 当前 next 仍留在 Phase 8：Workbench 只读化；不切 Phase 9。

验证记录：

- TDD red：`$py -m unittest tests.core.test_workbench_readonly_adapter -v` 首次运行 6 项均失败于 `ModuleNotFoundError: No module named 'core.contracts.workbench_readonly_adapter'`。
- TDD green：`$py -m unittest tests.core.test_workbench_readonly_adapter -v` 运行 6 项，全部 OK。
- 现有 workbench / trace viewer 回归：`$py -m unittest tests.core.test_workbench_trace_viewer tests.core.test_training_workbench_sync -v` 运行 24 项，全部 OK。
- Phase 5/6/7/8 regression：`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter -v` 运行 53 项，全部 OK。
- final doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- final PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- final OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- final protected evidence diff / status check：passed。`git diff --name-only -- output projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec agents\pipeline\pipeline_manifest.json config\entrypoint_custody_manifest.json` 与对应 `git status --short -- ...` 均无输出。

未触碰文件 / 路径：

- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包只证明 Workbench read-only adapter 与现有 flightdeck / trace viewer 数据入口在合同 / fixture 层可被测试；不证明完整 Workbench 产品化、CAD 能力提升、真实 CAD preview / readback 通过、`geometry_verified` 能力提升、训练恢复、表 C 推进、registry 更新、插件可用或 Worker 链路升级。

## Phase 8 - 第三包：Workbench 只读化 closeout 与 Phase 9 handoff 门禁

日期：2026-06-15

状态：checked

目标：

- 不新增 Phase 8 功能实现，只检查 projection / readonly adapter / flightdeck / trace viewer 只读链路是否可收口。
- 同步活跃入口文档，明确 Phase 8 已完成于合同 / fixture / 派生视图层，不是真实 CAD preview / readback。
- 确认 read-only adapter 保持 `derivedOnly=true`、`readOnly=true`、`mutatedTargets=[]`，且 package missing、hash mismatch、blocked / not_verified reason 和 missing evidence 继续 fail-closed 展示。
- 若验证全绿，将 current next 切到 Phase 9：单项 CAD Preview；本包只做 handoff，不执行 Phase 9。

修改文件：

- `README.md`
- `AGENTS.md`
- `CORE_CONTEXT_BRIEF.md`
- `CORE_RESTRUCTURE_PLAN.md`
- `docs/planning/任务清单.md`
- `docs/migration/execution-ledger.md`
- `docs/status/current.md`
- `docs/handoffs/current.md`
- `docs/status/changelog.md`

门禁判断：

- `build_workbench_projection()` / `build_workbench_readonly_adapter()` 只消费 task / ledger / package / judge 结果，不 append / overwrite / delete ledger，不复制 / 移动 / 改写 protected evidence。
- `build_workbench_v3()` 只通过可选 `contractWorkbench` / `contractWorkbenchProjections` 输入消费 adapter 输出；未提供时为空面板。
- `build_workbench_trace_viewer_data()` 只通过可选 `contract_workbench` 附带只读摘要，不改变原有 trace 扫描行为。
- model text、dry-run、preview registered 或缺 handles fixture readback 仍不得显示为 `cad_geometry_verified`。
- Phase 9 handoff 只表示下一阶段可在明确 scope 后启动单项 preview；本包不调用 AutoCAD / CAD-MCP、不写 DWG、不跑 preview。

验证记录：

- Phase 8 workbench closeout tests：passed。`$py -m unittest tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter tests.core.test_workbench_trace_viewer tests.core.test_training_workbench_sync -v` 运行 36 项，全部 OK。
- Phase 5/6/7/8 regression：passed。`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter -v` 运行 53 项，全部 OK。
- final doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- final PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- final OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- final protected evidence diff / status check：passed。`git diff --name-only -- output projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec agents\pipeline\pipeline_manifest.json config\entrypoint_custody_manifest.json` 与对应 `git status --short -- ...` 均无输出。

未触碰文件 / 路径：

- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包只判断 Phase 8 Workbench 只读化是否可收口，并在门禁通过时把 current next 切到 Phase 9。它不证明 CAD 能力提升、真实 CAD preview / readback 通过、`geometry_verified` 能力提升、插件可用、训练恢复、表 C 推进、registry 更新、完整 Workbench 产品化或 Phase 9 已执行。

## Phase 9 - 第一包：单项 CAD Preview scope lock / preflight / runner

日期：2026-06-17

状态：checked_external_blocker

目标：

- 锁定一个最小单项 CAD preview scope：`draw_object` / table / absolute placement / target layer `CODEX_PREVIEW`。
- 在真实 CAD 写入前先执行 validate / dry-run / preflight，并在 formal layer、缺 dry-run 或缺 validate 时 fail closed。
- 建立 Phase 9 EvidencePackage：只有真实后端名、created handles 全量 readback、实体都在 `CODEX_PREVIEW` 且 `savedCurrentDwg=false` 时，才满足 `real_cad_readback` 和 `no_save_guard`。
- 尝试连接既有 AutoCAD COM 实例；不可用时写出 `external_blocker` 证据，不宣称几何验证通过。

新增文件：

- `core/contracts/phase9_preview.py`
- `tests/core/test_phase9_single_preview.py`
- `output/validation_runs/phase9-single-preview-20260617-205703/**`

修改文件：

- `core/contracts/__init__.py`
- `README.md`
- `CORE_CONTEXT_BRIEF.md`
- `CORE_RESTRUCTURE_PLAN.md`
- `docs/planning/任务清单.md`
- `docs/migration/execution-ledger.md`
- `docs/status/current.md`
- `docs/handoffs/current.md`

门禁判断：

- `build_phase9_preview_scope_record()` 将 package 固定为 Phase 9 单项 preview，`maxPreviewTaskCount=1`，`targetLayer=CODEX_PREVIEW`，`savePolicy.savedCurrentDwg=false`，并显式禁止 formal layer、DWG save、registry / Table C / training source / protected evidence mutation、plugin 和 Phase 10 rehearsal。
- `run_phase9_single_preview()` 先写 task-scoped CAD_PLAN artifact，再做 validate / dry-run；preflight block 时不构造 driver，不执行 CAD。
- fake driver 即便返回 created handles 和 readback entities，也只能得到 `not_verified`，不能满足 `real_cad_readback`。
- 真实后端只有在 created handles 全量 readback、readback layer/type/bbox audit 可用、preview-only safety audit pass 且 no-save guard pass 时，才返回 `geometry_verified`。
- screenshot、dry-run、preview registered 和 model text 只作为信息项，不满足 `real_cad_readback`。
- 本轮真实 CAD 尝试只连接既有 AutoCAD COM 实例，不启动新 CAD、不保存当前 DWG、不改正式图层、不删除实体。

真实 CAD 尝试：

- 结果：`external_blocker` / `verification_status=not_verified`。
- blocker：无活动 `AutoCAD.Application` COM 实例；COM probe 返回 `No active AutoCAD.Application instance is available`。
- CAD_PLAN：`output/validation_runs/phase9-single-preview-20260617-205703/phase9_single_preview_cad_plan.json`。
- report：`output/validation_runs/phase9-single-preview-20260617-205703/phase9_preview_report.json`。
- `targetLayer=CODEX_PREVIEW`。
- `createdHandleCount=0`。
- `readbackEntityCount=0`。
- `cad_geometry_verified=false`。
- `savedCurrentDwg=false`。
- screenshot：not_run；本轮无真实 CAD readback，截图不作为完成证据。

验证记录：

- TDD red：`$py -m unittest tests.core.test_phase9_single_preview -v` 首次运行 7 项均失败于 `ModuleNotFoundError: No module named 'core.contracts.phase9_preview'`。
- TDD green：`$py -m unittest tests.core.test_phase9_single_preview -v` 运行 7 项，全部 OK。
- Phase 9 requested guards：`$py -m unittest tests.core.test_legacy_gateway_preview_readback tests.core.test_preview_only_audit tests.core.test_render_preview -v` 运行 28 项，全部 OK。
- Phase 5/6/7/8 regression：`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter -v` 运行 53 项，全部 OK。
- final doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`；首次运行曾因 `docs/handoffs/current.md` 超出 active doc budget 1 行失败，删除一个多余空行后重跑通过。
- final PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- final OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- final protected evidence diff / status check：tracked diff 无输出；status 仅显示允许的新增任务级证据目录 `output/validation_runs/phase9-single-preview-20260617-205703/`。

未触碰文件 / 路径：

- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包只证明 Phase 9 单项 preview 的 scope lock、preflight、EvidencePackage、CompletionJudge 和 no-save guard 在代码 / fixture 层可测试，并记录本机真实 AutoCAD COM 不可用的 external blocker。它不证明真实 CAD preview / readback 通过、不证明 `geometry_verified`、不恢复训练、不推进表 C、不改 registry、不做插件、不进入 Phase 10。

## Phase 9 - 第二包：AutoCAD 可连接重试与单项 CODEX_PREVIEW preview/readback

日期：2026-06-19

状态：checked_external_blocker

目标：

- 复用 Phase 9 第一包的单项 `CODEX_PREVIEW` CAD_PLAN，不扩大 scope。
- 增加 AutoCAD readiness probe：记录是否存在活动 `AutoCAD.Application`、是否有活动文档、活动文档是否可访问，以及是否尝试 preview write。
- 若 AutoCAD 可连接，则只写 `CODEX_PREVIEW` 并 readback created handles；若不可连接，则继续输出 `external_blocker`，不得伪造 `geometry_verified`。

新增 / 修改文件：

- 修改 `core/contracts/phase9_preview.py`
- 修改 `tests/core/test_phase9_single_preview.py`
- 新增 `output/validation_runs/phase9-single-preview-retry-20260619-223412/**`
- 同步 `README.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_RESTRUCTURE_PLAN.md`、`docs/planning/任务清单.md`、`docs/migration/execution-ledger.md`、`docs/status/current.md`、`docs/handoffs/current.md`、`docs/status/changelog.md`

门禁判断：

- readiness probe 在 preflight blocked 时为 `not_run`，不构造 driver，不执行 CAD。
- readiness probe 在 AutoCAD COM 不可连接时为 `external_blocker`，`applicationAvailable=false`、`activeDocumentAvailable=false`、`activeDocumentAccessible=false`、`previewAttempted=false`。
- readiness probe 在 driver 可用路径记录 active document name / fullName，并在 preview write 路径标记 `previewAttempted=true`。
- fake driver 仍不能满足 `real_cad_readback`；真实后端仍必须 created handles 全量 readback、preview-only audit pass 和 no-save guard pass 才能 `geometry_verified`。

真实 CAD 重试：

- 结果：`external_blocker` / `verificationStatus=not_verified`。
- probe：`output/validation_runs/phase9-single-preview-retry-20260619-223412/phase9_autocad_readiness_probe.json`。
- report：`output/validation_runs/phase9-single-preview-retry-20260619-223412/phase9_preview_report.json`。
- `targetLayer=CODEX_PREVIEW`。
- `dryRunStatus=valid`。
- `applicationAvailable=false`。
- `activeDocumentAvailable=false`。
- `activeDocumentAccessible=false`。
- `previewAttempted=false`。
- `createdHandleCount=0`。
- `readbackEntityCount=0`。
- `cadGeometryVerified=false`。
- `savedCurrentDwg=false`。
- blocker：无活动 `AutoCAD.Application` COM 实例；COM probe 返回 `No active AutoCAD.Application instance is available`。

验证记录：

- TDD red：`$py -m unittest tests.core.test_phase9_single_preview -v` 首次运行新增 8 项时 3 项失败，均指向缺 `autoCADReadinessProbe` / 缺 `phase9_autocad_readiness_probe.json`。
- TDD green：`$py -m unittest tests.core.test_phase9_single_preview -v` 运行 8 项，全部 OK。
- Phase 9 requested guards：`$py -m unittest tests.core.test_legacy_gateway_preview_readback tests.core.test_preview_only_audit tests.core.test_render_preview -v` 运行 28 项，全部 OK。
- Phase 5/6/7/8/9 regression：`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter tests.core.test_phase9_single_preview -v` 运行 61 项，全部 OK。
- final doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- final PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- final OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- final protected evidence diff / status check：passed。`git diff --name-only -- projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec agents\pipeline\pipeline_manifest.json config\entrypoint_custody_manifest.json` 与对应 `git status --short -- ...` 均无输出；本包只新增允许的任务级证据目录 `output/validation_runs/phase9-single-preview-retry-20260619-223412/`。

未触碰文件 / 路径：

- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包证明 Phase 9 单项 preview retry 具备结构化 readiness probe 和 fail-closed external blocker 证据；它不证明真实 CAD preview / readback 通过、不证明 `geometry_verified`、不恢复训练、不推进表 C、不改 registry、不做插件、不进入 Phase 10。

## Phase 9 - 第三包：AutoCAD-ready live retry / external blocker closeout

日期：2026-06-19

状态：checked_external_blocker

目标：

- 继续复用 Phase 9 第一包的单项 `CODEX_PREVIEW` CAD_PLAN，不扩大 scope。
- 若用户侧已经打开 AutoCAD 且有活动 DWG，则执行一次真实 preview write / created handles readback。
- 若仍不可连接，则正式收束为 Phase 9 external blocker closeout，明确不进入 Phase 10。

新增 / 修改文件：

- 新增 `output/validation_runs/phase9-single-preview-live-or-blocker-20260619-224058/**`
- 同步 `README.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_RESTRUCTURE_PLAN.md`、`docs/planning/任务清单.md`、`docs/migration/execution-ledger.md`、`docs/status/current.md`、`docs/handoffs/current.md`、`docs/status/changelog.md`

门禁判断：

- 本包没有新增生产代码；沿用第二包 readiness probe 和 fail-closed runner。
- 真实 retry 只连接既有 AutoCAD COM 实例，不启动新 CAD、不保存 DWG、不写正式图层、不删除实体。
- 有效 retry 输出目录为 `output/validation_runs/phase9-single-preview-live-or-blocker-20260619-224058/`。
- 先前一次 PowerShell / Python `-c` 命令封装失败发生在 runner 入口前，未生成 CAD 证据，不作为 Phase 9 结果。

真实 CAD live retry：

- 结果：`external_blocker` / `verificationStatus=not_verified`。
- probe：`output/validation_runs/phase9-single-preview-live-or-blocker-20260619-224058/phase9_autocad_readiness_probe.json`。
- report：`output/validation_runs/phase9-single-preview-live-or-blocker-20260619-224058/phase9_preview_report.json`。
- `targetLayer=CODEX_PREVIEW`。
- `dryRunStatus=valid`。
- `applicationAvailable=false`。
- `activeDocumentAvailable=false`。
- `activeDocumentAccessible=false`。
- `previewAttempted=false`。
- `createdHandleCount=0`。
- `readbackEntityCount=0`。
- `cadGeometryVerified=false`。
- `savedCurrentDwg=false`。
- blocker：无活动 `AutoCAD.Application` COM 实例；人工解除条件是用户打开 AutoCAD、打开目标 DWG，并保持活动文档可访问后再重试 Phase 9 live preview。

验证记录：

- live retry：passed as fail-closed external blocker。有效命令复用第一包 CAD_PLAN 调用 `run_phase9_single_preview(..., driver_backend="autocad_com_existing")`，输出 `output/validation_runs/phase9-single-preview-live-or-blocker-20260619-224058/phase9_preview_report.json`；结果为 `external_blocker`、`previewAttempted=false`、`createdHandleCount=0`、`readbackEntityCount=0`、`cadGeometryVerified=false`。首次 PowerShell / Python `-c` 命令封装失败发生在 runner 入口前，不作为 CAD 结果。
- TDD / code delta：not_applicable。本包没有新增生产代码或测试代码，沿用第二包已通过的 readiness probe 与 fail-closed runner。
- Phase 9 single preview tests：passed。`$py -m unittest tests.core.test_phase9_single_preview -v` 运行 8 项，全部 OK。
- Phase 9 requested guards：passed。`$py -m unittest tests.core.test_legacy_gateway_preview_readback tests.core.test_preview_only_audit tests.core.test_render_preview -v` 运行 28 项，全部 OK。
- Phase 5/6/7/8/9 regression：passed。`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter tests.core.test_phase9_single_preview -v` 运行 61 项，全部 OK。
- final doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- final PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- final OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- final protected evidence diff / status check：passed。`git diff --name-only -- projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec agents\pipeline\pipeline_manifest.json config\entrypoint_custody_manifest.json` 与对应 `git status --short -- ...` 均无输出；本包只新增允许的任务级证据目录 `output/validation_runs/phase9-single-preview-live-or-blocker-20260619-224058/`。

未触碰文件 / 路径：

- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包证明 Phase 9 单项 live retry 已按 AutoCAD-ready 条件再次尝试并 fail-closed 收束为 external blocker；它不证明真实 CAD preview / readback 通过、不证明 `geometry_verified`、不恢复训练、不推进表 C、不改 registry、不做插件、不进入 Phase 10。

## Phase 9 - 第四包：CAD-open live verify / COM 接管安全加固

日期：2026-06-19

状态：checked_external_blocker

触发：
- 用户确认当前 CAD 已打开，要求由 Codex 自行操作校验，确保 Phase 9 的真实 CAD 校验内容通过。

目标：
- 复用 Phase 9 第一包的单项 `CODEX_PREVIEW` CAD_PLAN，不扩大 scope。
- 在 CAD 已打开的前提下再次尝试真实 preview / created handles readback。
- 若 AutoCAD 进程可见但 COM 活动对象不可接管，写出精确 blocker，并加固 `connect_existing_only=True`，不得用 `Dispatch` 启动新 CAD 或挂起验证。

新增 / 修改文件：
- 修改 `core/cad_io/autocad_com.py`
- 修改 `tests/core/test_autocad_com_driver.py`
- 新增 `output/validation_runs/phase9-single-preview-live-verify-20260619-224732/**`
- 新增 `output/validation_runs/phase9-single-preview-live-verify-20260619-224946/**`（仅 preflight，旧 `Dispatch` fallback 路径超时，不作为有效 Phase 9 CAD evidence）
- 新增 `output/validation_runs/phase9-single-preview-live-verify-20260619-225504/**`
- 同步 `README.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_RESTRUCTURE_PLAN.md`、`docs/planning/任务清单.md`、`docs/migration/execution-ledger.md`、`docs/status/current.md`、`docs/handoffs/current.md`、`docs/status/changelog.md`

门禁判断：
- `_autocad_process_running()` 在 `tasklist` 被拒绝时会回退到 PowerShell `Get-Process -Name acad`，避免把“进程可见但 tasklist 无权限”误判为 CAD 未打开。
- `AutoCADComDriver(connect_existing_only=True)` 只允许 `GetActiveObject` 接管既有活动 COM 对象；当活动对象缺失时不再调用 `Dispatch` fallback，避免启动新 CAD、切换上下文或导致验证挂起。
- 即使 `acad.exe` 进程可见，缺少活动 `AutoCAD.Application` / ROT 对象时仍必须 `external_blocker`，不能执行 preview write，也不能声明 `real_cad_readback` 或 `geometry_verified`。

真实 CAD live verify：
- 最新有效输出目录：`output/validation_runs/phase9-single-preview-live-verify-20260619-225504/`
- 结果：`external_blocker` / `verificationStatus=not_verified`。
- report：`output/validation_runs/phase9-single-preview-live-verify-20260619-225504/phase9_preview_report.json`。
- `targetLayer=CODEX_PREVIEW`。
- `dryRunStatus=valid`。
- `applicationAvailable=false`。
- `activeDocumentAvailable=false`。
- `activeDocumentAccessible=false`。
- `previewAttempted=false`。
- `createdHandleCount=0`。
- `readbackEntityCount=0`。
- `cadGeometryVerified=false`。
- `savedCurrentDwg=false`。
- blocker：`acadProcessRunning=True`，但无活动 `AutoCAD.Application` COM 实例；`AutoCAD.Application.25.1` / `AutoCAD.Application.25` 的 `GetActiveObject` 返回操作无法使用，generic `AutoCAD.Application` 为无效类字符串；`connect_existing_only=True` 下 `Dispatch fallback skipped`。

验证记录：
- TDD red：新增 `_autocad_process_running()` PowerShell fallback 测试后先失败，旧实现只看 `tasklist` stdout，会在 `Access denied` 时误判。
- TDD green：实现 fallback 后 `tests.core.test_autocad_com_driver` 通过。
- TDD red：新增 `connect_existing_only` 不得调用 `Dispatch` 的测试后先失败，旧实现会在进程存在但 `GetActiveObject` 失败时尝试 `Dispatch`。
- TDD green：禁用 `connect_existing_only=True` 下的 `Dispatch` fallback 后 `tests.core.test_autocad_com_driver -v` 运行 20 项，全部 OK；`tests.core.test_phase9_single_preview -v` 运行 8 项，全部 OK。
- live verify：`output/validation_runs/phase9-single-preview-live-verify-20260619-225504/phase9_preview_report.json` 为有效 fail-closed external blocker；同轮前一次旧 `Dispatch` fallback 输出 `phase9-single-preview-live-verify-20260619-224946/` 只生成 CAD_PLAN / dry-run 后超时，不作为 CAD evidence。
- final affected tests：passed。`$py -m unittest tests.core.test_autocad_com_driver tests.core.test_phase9_single_preview -v` 运行 28 项，全部 OK。
- final Phase 5/6/7/8/9 guard regression：passed。`$py -m unittest tests.core.test_legacy_gateway_preview_readback tests.core.test_preview_only_audit tests.core.test_render_preview tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_evidence_ledger tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter -v` 运行 74 项，全部 OK。
- final doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- final PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- final OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- final protected evidence diff / status check：passed。`git diff --name-only -- projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec agents\pipeline\pipeline_manifest.json config\entrypoint_custody_manifest.json` 与对应 `git status --short -- ...` 均无输出；本包只新增允许的任务级验证目录。
- final read-only COM probe：`acadProcessRunning=true`、`connected=false`；`AutoCAD.Application.25.1` / `AutoCAD.Application.25` 仍返回操作无法使用，`Dispatch fallback skipped because connect_existing_only=True`，未执行 CAD 写入。

未触碰文件 / 路径：
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包证明在用户确认 CAD 已打开后，Phase 9 单项 live verify 已再次尝试，并将“进程可见但活动 COM / ROT 对象不可接管”的情况精确收束为 external blocker；它不证明真实 CAD preview / readback 通过、不证明 `geometry_verified`、不恢复训练、不推进表 C、不改 registry、不做插件、不进入 Phase 10。

## Phase 9 - 第五包：P9B Harness Result Contract

日期：2026-06-19

状态：checked

触发：
- 用户要求按照润色后的唯一主线 PlanMD 往前推进一阶段。

目标：
- 在 P9A 真 CAD 接管仍为 external blocker 的前提下，推进 P9B：把现有 Phase 9 runner 输出收成 CLI-harness-compatible JSON。
- 不扩大 CAD scope，不进入 P10，不启动插件，不恢复训练，不推进表 C。
- `validate`、`dry-run`、`probe`、`preview`、`readback`、`evidence` 命令均返回 `cad-agent-harness-result/v1`；fake backend 永远保持 `not_verified`。

新增 / 修改文件：
- 新增 `core/contracts/cad_agent_harness.py`
- 新增 `scripts/cad_agent_harness.py`
- 新增 `tests/core/test_cad_agent_harness.py`
- 修改 `core/contracts/__init__.py`
- 同步 `CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md`、`docs/migration/execution-ledger.md`

门禁判断：
- `core/contracts/cad_agent_harness.py` 只是 thin facade：validate / dry-run 使用既有 plan engine；preview 转调 `run_phase9_single_preview()`；evidence / readback 只读取既有 run dir 证据。
- 默认安全开关固定为 `saveAllowed=false`、`deleteAllowed=false`、`formalLayersAllowed=false`、`connectExistingOnly=true`。
- `probe` 在 P9B 中不接触 AutoCAD；P9A 仍拥有 live COM readiness。
- `fake-driver` 会映射为 `fake_driver_preflight`，即使有 created handles 和 readback entities，仍输出 `verificationStatus=not_verified`、`cadGeometryVerified=false`。

验证记录：
- TDD red：`$py -m unittest tests.core.test_cad_agent_harness -v` 首次运行 4 项均失败于缺少 `core.contracts.cad_agent_harness` / `scripts/cad_agent_harness.py`。
- TDD green：实现 facade 后 `tests.core.test_cad_agent_harness -v` 运行 5 项，全部 OK。
- final direct P9 check：passed。`$py -m unittest tests.core.test_cad_agent_harness tests.core.test_phase9_single_preview -v` 运行 13 项，全部 OK。
- final Phase 5/6/7/8/9 guard regression：passed。`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter tests.core.test_phase9_single_preview tests.core.test_cad_agent_harness -v` 运行 66 项，全部 OK。
- final doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- final PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- final OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- final protected evidence diff / status check：passed。`git diff --name-only -- projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec agents\pipeline\pipeline_manifest.json config\entrypoint_custody_manifest.json` 与对应 `git status --short -- ...` 均无输出。

未触碰文件 / 路径：
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包只证明 Phase 9 harness result contract 与 thin CLI facade 可用；它不证明真实 CAD preview / readback 通过、不证明 `geometry_verified`、不解除 AutoCAD COM / ROT external blocker、不进入 P10。

## Phase 9 - 第六包：P9C Preview Bundle Pilot

日期：2026-06-19

状态：checked

触发：
- 用户要求继续按照唯一主线 PlanMD 往前推进。

目标：
- 在 P9A 真 CAD 接管仍为 external blocker 的前提下，推进 P9C：把既有 P9 run dir 整理成 agent / human 可读的只读 preview bundle。
- 不重跑 CAD、不补造 readback、不扩大 CAD scope、不进入 P10、不启动插件、不恢复训练、不推进表 C。
- bundle 默认位于 P9 run dir 下的 `preview_bundle/`，包含 `manifest.json`、`summary.json`、`artifacts/`、`session.json`、`trajectory.json`。

新增 / 修改文件：
- 新增 `core/contracts/preview_bundle.py`
- 新增 `tests/core/test_phase9_preview_bundle.py`
- 修改 `core/contracts/cad_agent_harness.py`
- 修改 `core/contracts/__init__.py`
- 同步 `CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md`、`README.md`、`docs/migration/execution-ledger.md`

门禁判断：
- `build_phase9_preview_bundle()` 只读取既有 `phase9_preview_report.json` 与 report artifacts，并复制到 bundle 内的相对路径 `artifacts/`。
- harness 新增 `bundle` 命令，但命令输出仍是 `cad-agent-harness-result/v1`，且 `cadGeometryVerified` 只继承原 report，不因 bundle 存在而变为 true。
- `summary.json` 固定写 `completionBoundary=preview_bundle_is_read_only_not_readback_evidence`；若原 run 缺真实 readback，继续保留 `verificationStatus=not_verified` 与 `missingEvidence=real_cad_readback`。
- bundle_dir 必须留在 source run dir 之下，run_dir / bundle_dir 都必须位于仓库 `output/` 下。

验证记录：
- TDD red：`$py -m unittest tests.core.test_phase9_preview_bundle -v` 首次运行 3 项失败于缺少 `core.contracts.preview_bundle`、harness 不支持 `bundle` 命令、CLI choices 不接受 `bundle`。
- TDD green：实现 producer 与 harness command 后 `tests.core.test_phase9_preview_bundle -v` 运行 3 项，全部 OK。
- final direct P9 check：passed。`$py -m unittest tests.core.test_phase9_preview_bundle tests.core.test_cad_agent_harness tests.core.test_phase9_single_preview -v` 运行 16 项，全部 OK。
- final Phase 5/6/7/8/9 guard regression：passed。`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter tests.core.test_phase9_single_preview tests.core.test_cad_agent_harness tests.core.test_phase9_preview_bundle -v` 运行 69 项，全部 OK。
- final doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- final PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- final OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- final protected evidence diff / status check：passed。`git diff --name-only -- projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec agents\pipeline\pipeline_manifest.json config\entrypoint_custody_manifest.json` 与对应 `git status --short -- ...` 均无输出；`output\test_artifacts` status 也无输出。

未触碰文件 / 路径：
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包只证明 Phase 9 preview bundle 的只读证据展示协议可用；它不证明真实 CAD preview / readback 通过、不证明 `geometry_verified`、不解除 AutoCAD COM / ROT external blocker、不进入 P10。

## Phase 9 - 第七包：P9 Exit Gate Guard

日期：2026-06-19

状态：checked

触发：
- 用户要求继续推进。

目标：
- 在 P9A 真 CAD 接管仍为 external blocker 的前提下，推进 P9 Exit 的 fail-closed gate evaluator。
- 不重跑 CAD、不补造 readback、不扩大 CAD scope、不进入 P10、不启动插件、不恢复训练、不推进表 C。
- 只有既有 P9 report 已证明 `cadGeometryVerified=true`、`savedCurrentDwg=false`、created handles / readback entities 均存在，且 CompletionJudge `can_claim_complete=true` 时，才允许 `phase10Allowed=true`。

新增 / 修改文件：
- 新增 `core/contracts/phase9_exit_gate.py`
- 新增 `tests/core/test_phase9_exit_gate.py`
- 修改 `core/contracts/cad_agent_harness.py`
- 修改 `core/contracts/__init__.py`
- 同步 `CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md`、`README.md`、`docs/migration/execution-ledger.md`

门禁判断：
- `evaluate_phase9_exit_gate()` 只读取既有 `phase9_preview_report.json` 与可选 `preview_bundle/summary.json`，不创建 CAD 证据。
- harness 新增 `exit-gate` 命令，命令输出仍是 `cad-agent-harness-result/v1`，并附带 `phase10Allowed`、`completionCanClaimComplete` 与 `decisionBoundary`。
- fake backend / preview bundle / 截图 / dry-run / model text 都不能放行 P10；若 bundle summary 与 report 冲突，gate fail-closed 并输出 `preview_bundle_conflicts_with_report`。
- 当前真实 live evidence 仍是 P9A external blocker，因此实际主线仍停在 P9A Live CAD unblock / P9 Exit blocked。

验证记录：
- TDD red：`$py -m unittest tests.core.test_phase9_exit_gate -v` 首次运行 4 项失败于缺少 `core.contracts.phase9_exit_gate`，以及 harness CLI 不支持 `exit-gate`。
- TDD green：实现 gate evaluator 与 harness command 后 `tests.core.test_phase9_exit_gate -v` 运行 4 项，全部 OK。
- final direct P9 check：passed。`$py -m unittest tests.core.test_phase9_exit_gate tests.core.test_phase9_preview_bundle tests.core.test_cad_agent_harness tests.core.test_phase9_single_preview -v` 运行 20 项，全部 OK。
- final Phase 5/6/7/8/9 guard regression：passed。`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter tests.core.test_phase9_single_preview tests.core.test_cad_agent_harness tests.core.test_phase9_preview_bundle tests.core.test_phase9_exit_gate -v` 运行 73 项，全部 OK。
- final doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- final PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- final OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- final protected evidence diff / status check：passed。`git diff --name-only -- projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec agents\pipeline\pipeline_manifest.json config\entrypoint_custody_manifest.json` 与对应 `git status --short -- ...` 均无输出；`output\test_artifacts` status 也无输出。

未触碰文件 / 路径：
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包只证明 Phase 9 exit gate 可以 fail-closed 地裁决既有证据是否允许进入 P10；它不证明真实 CAD preview / readback 通过、不证明当前 live `geometry_verified`、不解除 AutoCAD COM / ROT external blocker、不进入 P10。

## Phase 9 - 第八包：P9 Exit / Bundle Review Hardening

日期：2026-06-19

状态：checked

触发：
- 用户要求 review 并修复加固。

目标：
- Review P9B/P9C/P9 Exit 近期实现，优先查找会让伪证据、手改报告或不可追踪 artifact 误穿过主线门禁的漏洞。
- 不重跑 CAD、不补造 readback、不扩大 CAD scope、不进入 P10、不启动插件、不恢复训练、不推进表 C。

新增 / 修改文件：
- 修改 `core/contracts/phase9_exit_gate.py`
- 修改 `core/contracts/preview_bundle.py`
- 修改 `tests/core/test_phase9_exit_gate.py`
- 修改 `tests/core/test_phase9_preview_bundle.py`
- 同步 `CORE_RESTRUCTURE_PLAN.md`、`docs/migration/execution-ledger.md`

review 发现与修复：
- 修复：P9 Exit gate 之前只读取 `missingEvidence` 用于输出，没有把非空 `missingEvidence` / CompletionJudge `missing_evidence` 作为阻断条件；现在新增 `p9_missing_evidence_not_empty` 与 `completion_missing_evidence_not_empty`。
- 修复：P9 Exit gate 之前只看 CompletionJudge `can_claim_complete=true`，没有独立要求 `checked_evidence` 覆盖 `real_cad_readback` 与 `no_save_guard`；现在新增 `completion_checked_evidence_incomplete`。
- 修复：`createdHandleCount` / `readbackEntityCount` 若被写成非数字字符串会抛异常；现在改为 fail-closed，输出 `p9_created_handle_count_invalid` / `p9_readback_entity_count_invalid`，不再崩溃。
- 修复：Preview Bundle 之前遇到 report artifact 指向 run dir 外或不存在时会静默跳过；现在在 result / manifest / summary 写入 `artifact_source_not_traceable:*` warning，不把不可追踪 artifact 包装成完整 bundle。
- 保留：harness `exit-gate` 命令对 blocked gate 仍返回进程码 0，并通过 JSON `status=blocked` / `phase10Allowed=false` 表达裁决结果；这是 machine-readable facade 口径，不代表放行。

门禁判断：
- P9 Exit 现在必须同时满足 `cadGeometryVerified=true`、`savedCurrentDwg=false`、`missingEvidence=[]`、created handles / readback entities 均为正整数、CompletionJudge `checked_evidence` 覆盖 `real_cad_readback` / `no_save_guard`、`missing_evidence=[]` 且 `can_claim_complete=true`，才允许 `phase10Allowed=true`。
- Preview Bundle 仍然只读；warning 只说明 artifact traceability 风险，不补造 evidence、不升级 readback、不改变 `cadGeometryVerified`。

验证记录：
- TDD red：新增 4 个反例后，`tests.core.test_phase9_exit_gate tests.core.test_phase9_preview_bundle -v` 先失败于伪 verified 报告误放行、checked evidence 缺口误放行、坏计数字段抛 `ValueError`、bundle 缺少 `warnings` 字段。
- TDD green：实现 hardening 后 `tests.core.test_phase9_exit_gate tests.core.test_phase9_preview_bundle -v` 运行 11 项，全部 OK。
- direct P9 check：passed。`$py -m unittest tests.core.test_phase9_exit_gate tests.core.test_phase9_preview_bundle tests.core.test_cad_agent_harness tests.core.test_phase9_single_preview -v` 运行 24 项，全部 OK。
- Phase 5/6/7/8/9 guard regression：passed。`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter tests.core.test_phase9_single_preview tests.core.test_cad_agent_harness tests.core.test_phase9_preview_bundle tests.core.test_phase9_exit_gate -v` 运行 77 项，全部 OK。
- final doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- final PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- final OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- final protected evidence diff / status check：passed。`git diff --name-only -- projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec agents\pipeline\pipeline_manifest.json config\entrypoint_custody_manifest.json` 与对应 `git status --short -- ...` 均无输出。

未触碰文件 / 路径：
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包只证明 P9 Exit / Preview Bundle 在伪证据和不可追踪 artifact 场景下更严格地 fail-closed；它不证明真实 CAD preview / readback 通过、不证明当前 live `geometry_verified`、不解除 AutoCAD COM / ROT external blocker、不进入 P10。

## Phase 9 - 第九包：CAD Session Host 根因修复与 P9 Exit closeout

日期：2026-06-19

状态：checked

触发：
- 用户指出“CAD 已打开但 agent 仍无法接管 CAD”是基础且致命的问题，要求以长期根治为目标修复，而不是只做最小补丁。

目标：
- 将直接从 Codex 进程接管 AutoCAD COM 的脆弱路径降级为诊断 / 兼容路径。
- 新增一个运行在本机 Windows 用户会话内的 `CAD Session Host`，由 Host 持有 AutoCAD COM，Phase 9 / 后续 harness 通过本地 token-protected RPC 调用。
- Host 必须 fail-closed：只绑定 localhost、必须 token、只允许 `CODEX_PREVIEW` preview 写入、不保存 DWG、不删除实体、不改正式图层。
- 修复 AutoCAD COM STA/thread-affine 隐患，避免后续开发再出现“连接上但基础 COM 对象不可用”的跨线程问题。

新增 / 修改文件：
- 新增 `core/cad_io/cad_session_host.py`
- 新增 `scripts/cad_session_host.py`
- 新增 / 修改 `tests/core/test_cad_session_host.py`
- 修改 `core/contracts/cad_agent_harness.py`
- 修改 `core/contracts/phase9_preview.py`
- 修改 `core/contracts/vnext.py`
- 修改 `core/orchestrator/tool_contract.py`
- 修改 `tests/core/test_cad_agent_harness.py`
- 修改 `tests/core/test_tool_contract_react.py`
- 同步 `AGENTS.md`、`README.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_RESTRUCTURE_PLAN.md`、`docs/planning/任务清单.md`、`docs/migration/execution-ledger.md`、`docs/status/current.md`、`docs/status/changelog.md`、`docs/handoffs/current.md`、`docs/handoffs/package-index.md`

根因与修复：
- direct COM blocker：上一包已证明 `acad.exe` 进程可见，但当前 Codex 会话无法通过活动 `AutoCAD.Application` / ROT 对象稳定接管；`connect_existing_only=True` 下必须禁用 `Dispatch` fallback。
- Host 方案：`CadSessionHostService` 持有 driver，`CadSessionHostClient` 作为 driver-compatible RPC client；harness / orchestrator 默认 live backend 从旧 direct COM 切为 `cad-session-host` / `cad_session_host`。
- 安全边界：Host request 必须携带 `X-CAD-Session-Token`；允许方法限定为 preview draw / readback / view refresh；写方法只能写 `CODEX_PREVIEW`，snapshot / zoom 只能无图层过滤或 `CODEX_PREVIEW`。
- STA 修复：首次 Host live 尝试输出 `output/validation_runs/phase9-session-host-live-verify-20260619-235359/`，readiness 已 `ready` 且活动文档可访问，但 `ThreadingHTTPServer` 跨线程复用 AutoCAD COM driver 导致 `<unknown>.Layers`；随后改为单线程 `HTTPServer`，保证 driver 在同一 STA server thread 内创建和使用。

真实 CAD live verify：
- 最新有效输出目录：`output/validation_runs/phase9-session-host-live-verify-20260619-235547/`
- report：`output/validation_runs/phase9-session-host-live-verify-20260619-235547/phase9_preview_report.json`
- readiness probe：`status=ready`、`applicationAvailable=true`、`activeDocumentAvailable=true`、`activeDocumentAccessible=true`，活动文档为 `projects/测试文件.dwg`
- driverBackend：`cad_session_host`
- targetLayer：`CODEX_PREVIEW`
- status：`geometry_verified`
- verificationStatus：`verified`
- cadGeometryVerified：`true`
- savedCurrentDwg：`false`
- createdHandleCount：`4`
- readbackEntityCount：`4`
- missingEvidence：`[]`
- blockingReasons：`[]`
- created handles：`DABA`、`DABB`、`DABC`、`DABD`
- readback audit：4 条 `AcDbLine`，全部在 `CODEX_PREVIEW`，bbox 对应 900 x 450 单项 table preview。

P9 Exit closeout：
- bundle：`output/validation_runs/phase9-session-host-live-verify-20260619-235547/preview_bundle/manifest.json`
- bundle summary：`output/validation_runs/phase9-session-host-live-verify-20260619-235547/preview_bundle/summary.json`
- exit gate：`scripts/cad_agent_harness.py exit-gate --run-dir output\validation_runs\phase9-session-host-live-verify-20260619-235547 --json`
- exit 结果：`status=ready`、`verificationStatus=verified`、`phase10Allowed=true`、`completionCanClaimComplete=true`、`blockingReasons=[]`、`missingEvidence=[]`
- next：Phase 10 Focused Harness Rehearsal；进入前仍必须确认 rehearsal scope。

验证记录：
- TDD red：`tests.core.test_cad_session_host -v` 首次失败于缺少 `core.cad_io.cad_session_host`。
- TDD green：实现 service / client / CLI 后 `tests.core.test_cad_session_host -v` 通过；随后新增单线程 Host 回归，防止 AutoCAD COM 再被跨线程复用。
- harness backend：`tests.core.test_cad_agent_harness -v` 通过，覆盖显式 `cad-session-host`、缺配置 fail-closed、默认 preview backend 改为 `cad-session-host`、fake backend 仍 `not_verified`。
- orchestrator backend：`tests.core.test_tool_contract_react -v` 通过，覆盖 Stage 4 默认 `cad_session_host` 与 fake preflight 边界。
- live CAD：`phase9-session-host-live-verify-20260619-235359/` 先暴露 `<unknown>.Layers` 跨线程问题；修复后 `phase9-session-host-live-verify-20260619-235547/` 真实 CAD `geometry_verified`。
- P9 bundle：passed。harness `bundle` 在成功 run 下生成 `preview_bundle/**`，无 warning。
- P9 exit：passed。harness `exit-gate` 在成功 run 下返回 `ready` / `phase10Allowed=true`。
- final broader regression：passed。`python -m unittest tests.core.test_cad_session_host tests.core.test_cad_agent_harness tests.core.test_autocad_com_driver tests.core.test_phase9_single_preview tests.core.test_phase9_exit_gate tests.core.test_phase9_preview_bundle tests.core.test_tool_contract_react -v` 通过 72 项；`python -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter -v` 通过 53 项；`python -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 通过 45 项。
- doc governance / OpenSpec / diff：passed。`python scripts/run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`；`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed；`git diff --check` exit 0（仅 CRLF 提示，无 whitespace error）。
- protected evidence checks：passed。`git diff --name-only -- projects libraries docs/training/training-sources.json libraries/system_library/registry.json openspec agents/pipeline/pipeline_manifest.json config/entrypoint_custody_manifest.json` 与对应 `git status --short -- ...` 均为空；未通过文件系统移动、删除或改写 protected evidence。

未触碰文件 / 路径：
- `projects/**`（除当前 AutoCAD 活动 DWG 被写入 `CODEX_PREVIEW` preview 实体外，未通过仓库文件系统移动、删除或改写）
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件的保存、覆盖、删除或正式图层修改

能力声明边界：本包证明 Phase 9 单项真实 CAD preview / created-handle readback / no-save guard / P9 Exit 已通过，并证明 `cad-session-host` 可作为后续真实 CAD bridge 默认入口；它不证明 Phase 10 rehearsal 已完成、不恢复训练、不推进表 C、不证明插件可用、不证明多项 CAD 能力稳定。

## Phase 10 - 第一包：P10A Rehearsal Plan Contract

日期：2026-06-20

状态：checked

触发：
- 用户要求 review 后继续往前推进。

review 结论：
- 当前主线已由 Phase 9 blocker 进入 Phase 10；Phase 9 最新有效 run 为 `output/validation_runs/phase9-session-host-live-verify-20260619-235547/`，P9 Exit `phase10Allowed=true`。
- Phase 10 的真实 live rehearsal 仍必须先确认 scope；本包不能代替用户 scope，也不能直接写 CAD。
- 安全推进方式是先落 P10A scope / run-plan 合同，作为 P10B live rehearsal 的停闸入口。

目标：
- 新增 P10A planning contract：只生成 rehearsal scope 与 run plan，不连接 CAD、不执行 preview、不写实体。
- 将 P10 run plan 继续挂在 agent-native harness 后面，保持 CLI-Anything 风格的稳定子命令 / JSON 输出。
- 在没有 confirmed scope、缺 ready P9 Exit reference、run 次数不足、非 `CODEX_PREVIEW` 图层或 fake backend 时 fail-closed。

新增 / 修改文件：
- 新增 `core/contracts/phase10_rehearsal.py`
- 新增 `tests/core/test_phase10_rehearsal.py`
- 修改 `core/contracts/cad_agent_harness.py`
- 修改 `core/contracts/__init__.py`
- 同步 `CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md`、`README.md`、`docs/status/current.md`、`docs/status/changelog.md`、`docs/handoffs/current.md`、`docs/handoffs/package-index.md`、`docs/migration/execution-ledger.md`

门禁判断：
- `prepare_phase10_rehearsal_plan()` 输出 `phase10_rehearsal_scope.json` 与 `phase10_rehearsal_plan.json`，并固定 `cadWritesAttempted=false`。
- harness 新增 `rehearsal-plan` 命令，输出仍是 `cad-agent-harness-result/v1`，并附带 `rehearsalPlan` 子对象。
- ready 条件：`scopeConfirmed=true`、`phase9ExitRunDir` 指向 `phase10Allowed=true` 的 P9 Exit run、`runCount>=2`、所有 CAD_PLAN 均为 `CODEX_PREVIEW`、backend 为 `cad-session-host` / `cad_session_host`。
- blocked 条件：`phase10_scope_not_confirmed`、`phase9_exit_reference_missing` / `phase9_exit_reference_invalid` / `phase9_exit_not_ready`、`phase10_repetition_count_too_low`、`phase10_non_preview_layer_forbidden`、`phase10_cad_plan_invalid`、`phase10_real_backend_required`。

验证记录：
- TDD red：`tests.core.test_phase10_rehearsal -v` 首次 5 项失败于缺少 `core.contracts.phase10_rehearsal`、harness 不支持 `rehearsal-plan`、CLI 不接受 `--scope`。
- TDD green：实现 P10A module / harness command 后 `tests.core.test_phase10_rehearsal -v` 运行 5 项，全部 OK。
- review hardening red：新增 ready P9 Exit reference 与 fake backend 反例后，测试先分别失败于缺 P9 Exit reference 仍 ready、`fake-driver` 仍 ready。
- review hardening green：补入 `phase9ExitRunDir` gate 与 real-backend gate 后 `tests.core.test_phase10_rehearsal -v` 运行 7 项，全部 OK。
- direct P10/P9/Host regression：passed。`$py -m unittest tests.core.test_phase10_rehearsal tests.core.test_cad_session_host tests.core.test_cad_agent_harness tests.core.test_autocad_com_driver tests.core.test_phase9_single_preview tests.core.test_phase9_exit_gate tests.core.test_phase9_preview_bundle tests.core.test_tool_contract_react -v` 运行 79 项，全部 OK。
- Phase 5/6/7/8 contract regression：passed。`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter -v` 运行 53 项，全部 OK。
- doc governance first pass：failed。`docs/handoffs/current.md` 因新增 P10A current line 后达到 141 行，超过 140 行 active budget；随后删除不在 current index 中的旧 Phase 8 handoff 行，保持 current 窗口轻量。
- final doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- final PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- final OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- final protected evidence diff / status check：passed。`git diff --name-only -- projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec agents\pipeline\pipeline_manifest.json config\entrypoint_custody_manifest.json` 与对应 `git status --short -- ...` 均无输出。

未触碰文件 / 路径：
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包只证明 Phase 10 focused rehearsal 的 scope / run-plan 合同已可测试、可审计、可由 harness 输出；它不证明 P10B live rehearsal 已执行、不证明多项 CAD 能力稳定、不恢复训练、不推进表 C、不证明插件可用。

## Phase 10 - 第二包：P10B Rehearsal Result Aggregate Contract

日期：2026-06-20

状态：checked

触发：
- 用户要求继续推进。

review 结论：
- P10B live rehearsal 仍缺用户确认 scope；不能在本包中连接 CAD、执行 preview 或写实体。
- 但 P10B 的真实 run 一旦产生，需要一个只读收口层统一判断多次 run 是否稳定，并生成 diff summary / failure ledger；否则 live runs 会缺少一致的完成裁判。
- 安全推进方式是先落 result aggregate contract：只消费已有 run dir，不创建 CAD proof。

目标：
- 新增 P10B result aggregate contract，读取已有 `phase9_preview_report.json` 并生成 P10 rehearsal 结果。
- 新增 harness `rehearsal-result` 命令，保持 CLI-Anything 风格的稳定子命令 / JSON 输出。
- 固定 fail-closed 门禁：run 数不足、缺 report、非真实 backend、非 `CODEX_PREVIEW`、保存当前 DWG、缺 created/readback、上游 missing evidence、几何签名漂移均 blocked。

新增 / 修改文件：
- 修改 `core/contracts/phase10_rehearsal.py`
- 修改 `core/contracts/cad_agent_harness.py`
- 修改 `core/contracts/__init__.py`
- 修改 `tests/core/test_phase10_rehearsal.py`
- 同步 `CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md`、`README.md`、`docs/status/current.md`、`docs/status/changelog.md`、`docs/handoffs/current.md`、`docs/handoffs/package-index.md`、`docs/migration/execution-ledger.md`

门禁判断：
- `evaluate_phase10_rehearsal_runs()` 输出 `phase10_rehearsal_result.json`、`phase10_rehearsal_diff_summary.json`、`phase10_rehearsal_failure_ledger.json`，并固定 `cadWritesAttempted=false`。
- ready 条件：至少 2 个 run；每个 run `verificationStatus=verified`、`cadGeometryVerified=true`、`savedCurrentDwg=false`、`createdHandleCount>0`、`readbackEntityCount>0`、backend 为 `cad-session-host` / `cad_session_host`、target layer 为 `CODEX_PREVIEW`、readback layer audit 通过、missing evidence 与 upstream blockers 均为空；所有 comparable run 的 geometry signature 稳定。
- blocked 条件：`phase10_rehearsal_run_count_too_low`、`phase10_rehearsal_run_missing`、`phase10_rehearsal_report_missing` / invalid、`phase10_run_backend_not_real`、`phase10_run_layer_not_preview`、`phase10_run_saved_current_dwg`、`phase10_run_created_handles_missing`、`phase10_run_readback_missing`、`phase10_run_missing_evidence`、`phase10_run_report_blocked`、`phase10_run_preview_layer_audit_failed`、`phase10_run_geometry_signature_missing`、`phase10_rehearsal_geometry_diff_detected`。

验证记录：
- TDD red：新增 P10B result aggregate 测试后，首次失败于缺少 `evaluate_phase10_rehearsal_runs()` 与 harness 不支持 `rehearsal-result`。
- TDD green：实现 result aggregate / diff / failure ledger / harness command 后 `tests.core.test_phase10_rehearsal -v` 运行 13 项，全部 OK。
- direct P10/P9/Host regression：passed。`$py -m unittest tests.core.test_phase10_rehearsal tests.core.test_cad_session_host tests.core.test_cad_agent_harness tests.core.test_autocad_com_driver tests.core.test_phase9_single_preview tests.core.test_phase9_exit_gate tests.core.test_phase9_preview_bundle tests.core.test_tool_contract_react -v` 运行 85 项，全部 OK。
- Phase 5/6/7/8 contract regression：passed。`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter -v` 运行 53 项，全部 OK。
- doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- protected evidence diff / status check：passed。`git diff --name-only -- projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec agents\pipeline\pipeline_manifest.json config\entrypoint_custody_manifest.json` 与对应 `git status --short -- ...` 均无输出。

未触碰文件 / 路径：
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包只证明 P10B 的只读结果聚合、稳定性 diff 与 failure ledger 合同已可测试、可由 harness 输出；它不证明 P10B live CAD runs 已执行、不连接 AutoCAD、不写 `CODEX_PREVIEW` 实体、不恢复训练、不推进表 C、不证明插件可用。

## Phase 10 - 第三包：P10B Live Run Gate Contract

日期：2026-06-20

状态：checked

触发：
- 用户继续要求推进。

review 结论：
- P10B live rehearsal scope 仍未由用户点名；不能把“继续推进”解释为直接写 CAD。
- P10A 已有 run plan，P10B 已有 result aggregate；下一块缺口是一个 fail-closed live-run 入口，确保真实执行只能在确认 scope / plan / host 配置后发生。

目标：
- 新增 `execute_phase10_rehearsal_plan()`，只消费 ready 的 `phase10_rehearsal_plan.json`。
- 新增 harness `rehearsal-run` 命令和 `--confirm-live-runs` flag。
- 没有 live 确认、缺 session-host 配置、plan / runSpec 不合规时，全部 blocked 且 `cadWritesAttempted=false`。

新增 / 修改文件：
- 修改 `core/contracts/phase10_rehearsal.py`
- 修改 `core/contracts/cad_agent_harness.py`
- 修改 `core/contracts/__init__.py`
- 修改 `tests/core/test_phase10_rehearsal.py`
- 同步 `CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md`、`README.md`、`docs/status/current.md`、`docs/status/changelog.md`、`docs/handoffs/current.md`、`docs/handoffs/package-index.md`、`docs/migration/execution-ledger.md`

门禁判断：
- 默认没有 `live_runs_confirmed=True` / CLI `--confirm-live-runs` 时，返回 `phase10_live_runs_not_confirmed`，不调用 preview executor。
- 默认生产路径缺 `CAD_SESSION_HOST_URL` 或 `CAD_SESSION_TOKEN` 时，返回 `phase10_session_host_env_missing`，不调用 preview executor。
- runSpec 校验要求 plan schema 为 `phase10-rehearsal-plan/v1`、plan `status=ready`、backend 为 `cad-session-host` / `cad_session_host`、runSpec command 为 `preview`、target layer 与 CAD_PLAN layer 均为 `CODEX_PREVIEW`、CAD_PLAN validate 通过、outputDir 留在 `output/**`。
- 明确确认且执行后，仍由 `evaluate_phase10_rehearsal_runs()` 收口；如果 aggregate blocked，则 execution blocked。

验证记录：
- TDD red：新增 live-run gate 测试后，首次失败于缺少 `execute_phase10_rehearsal_plan()`、harness 不支持 `rehearsal-run`。
- TDD green：实现 execution gate / harness command 后 `tests.core.test_phase10_rehearsal -v` 运行 18 项，全部 OK。
- direct P10/P9/Host regression：passed。`$py -m unittest tests.core.test_phase10_rehearsal tests.core.test_cad_session_host tests.core.test_cad_agent_harness tests.core.test_autocad_com_driver tests.core.test_phase9_single_preview tests.core.test_phase9_exit_gate tests.core.test_phase9_preview_bundle tests.core.test_tool_contract_react -v` 运行 90 项，全部 OK。
- Phase 5/6/7/8 contract regression：passed。`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter -v` 运行 53 项，全部 OK。
- doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- protected evidence diff / status check：passed。`git diff --name-only -- projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec agents\pipeline\pipeline_manifest.json config\entrypoint_custody_manifest.json` 与对应 `git status --short -- ...` 均无输出。

能力声明边界：本包只证明 P10B live-run 执行入口会 fail-closed，并能在明确确认后按 run plan 调用 preview executor；本轮没有连接 AutoCAD、没有执行真实 `cad-session-host` live run、没有写实体、不恢复训练、不推进表 C、不证明插件可用。

## Phase 10 - 第四包：P10B Launch Preflight Contract

日期：2026-06-20

状态：checked

触发：
- 用户继续要求推进。

review 结论：
- P10B live rehearsal scope 仍未由用户点名；不能把“继续推进”解释为直接写 CAD。
- live-run gate 已经 fail-closed，但在真实 run 前仍缺一个 operator launch packet，把 ready plan、session-host env、确认 flag 和实际启动 argv 收束成机器可审计 artifact。
- 安全推进方式是新增 launch preflight contract：只读 plan / env、只写 launch packet、不连接 AutoCAD、不调用 preview executor。

目标：
- 新增 `build_phase10_rehearsal_launch_packet()`，只消费 ready 的 `phase10_rehearsal_plan.json`。
- 新增 harness `rehearsal-preflight` 命令，输出 `phase10_rehearsal_launch_packet.json`。
- 没有 live 确认、缺 session-host 配置、plan / runSpec 不合规时，全部 blocked 且 `cadWritesAttempted=false`。
- ready 时只生成可审计 `rehearsal-run --confirm-live-runs` argv；不创建 run dir，不执行 preview。

新增 / 修改文件：
- 修改 `core/contracts/phase10_rehearsal.py`
- 修改 `core/contracts/cad_agent_harness.py`
- 修改 `core/contracts/__init__.py`
- 修改 `tests/core/test_phase10_rehearsal.py`
- 同步 `AGENTS.md`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md`、`README.md`、`docs/status/current.md`、`docs/status/changelog.md`、`docs/handoffs/current.md`、`docs/handoffs/package-index.md`、`docs/migration/execution-ledger.md`

门禁判断：
- `rehearsal-preflight` 默认没有 `live_runs_confirmed=True` / CLI `--confirm-live-runs` 时，返回 `phase10_live_runs_not_confirmed`。
- 默认缺 `CAD_SESSION_HOST_URL` 或 `CAD_SESSION_TOKEN` 时，返回 `phase10_session_host_env_missing`。
- plan / runSpec 校验复用 live-run gate：plan schema 必须为 `phase10-rehearsal-plan/v1`、plan `status=ready`、backend 为 `cad-session-host` / `cad_session_host`、runSpec command 为 `preview`、target layer 与 CAD_PLAN layer 均为 `CODEX_PREVIEW`、CAD_PLAN validate 通过、outputDir 留在 `output/**`。
- ready 输出 `launchAllowed=true`、`nextAllowedEffects=["phase10_rehearsal_live_preview_runs"]` 和 `launchCommand.argv`，但仍固定 `cadWritesAttempted=false`。

验证记录：
- TDD green：实现 launch packet / harness command 后 `$py -m unittest tests.core.test_phase10_rehearsal -v` 运行 22 项，全部 OK。
- direct P10/P9/Host regression：passed。`$py -m unittest tests.core.test_phase10_rehearsal tests.core.test_cad_session_host tests.core.test_cad_agent_harness tests.core.test_autocad_com_driver tests.core.test_phase9_single_preview tests.core.test_phase9_exit_gate tests.core.test_phase9_preview_bundle tests.core.test_tool_contract_react -v` 运行 94 项，全部 OK。
- Phase 5/6/7/8 contract regression：passed。`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter -v` 运行 53 项，全部 OK。
- doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- protected evidence diff / status check：passed。`git diff --name-only -- projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec agents\pipeline\pipeline_manifest.json config\entrypoint_custody_manifest.json` 与对应 `git status --short -- ...` 均无输出。

能力声明边界：本包只证明 P10B live-run 的发车前条件可以被机器审计，并能生成下一步真实 run 的 argv；本轮没有连接 AutoCAD、没有执行真实 `cad-session-host` live run、没有创建 run dir、没有写实体、不恢复训练、不推进表 C、不证明插件可用。

## Phase 10 - 第五包：P10B Closeout Gate Contract

日期：2026-06-20

状态：checked

触发：
- 用户继续要求推进。

review 结论：
- P10B live rehearsal scope 仍未由用户点名；不能把“继续推进”解释为直接写 CAD。
- P10B 已有 plan / aggregate / live-run gate / launch preflight；下一块缺口是 closeout 裁判，确保未来真实 live runs 不会仅凭“有输出文件”就进入 Phase 11。
- 安全推进方式是新增 closeout gate：只消费既有 launch packet / execution / result artifact，不连接 AutoCAD、不执行 preview、不写实体。

目标：
- 新增 `evaluate_phase10_rehearsal_closeout()`，输出 `phase10_rehearsal_closeout.json`。
- 新增 harness `rehearsal-closeout` 命令。
- closeout 只有在 launch ready、execution 为 production harness preview executor、source `cadWritesAttempted=true`、result verified / stable geometry、无 blockers / missing evidence 时，才允许 `phase10CloseoutAllowed=true` / `phase11Allowed=true`。
- injected executor artifact 只能证明测试路径，不允许作为生产 closeout proof。

新增 / 修改文件：
- 修改 `core/contracts/phase10_rehearsal.py`
- 修改 `core/contracts/cad_agent_harness.py`
- 修改 `core/contracts/__init__.py`
- 修改 `tests/core/test_phase10_rehearsal.py`
- 同步 `AGENTS.md`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md`、`README.md`、`docs/status/current.md`、`docs/status/changelog.md`、`docs/handoffs/current.md`、`docs/handoffs/package-index.md`、`docs/migration/execution-ledger.md`

门禁判断：
- 缺 `phase10_rehearsal_launch_packet.json`、`phase10_rehearsal_execution.json` 或 `phase10_rehearsal_result.json` 时 blocked。
- launch packet 必须 `status=ready`、`launchAllowed=true`、`liveRunsConfirmed=true`、`sessionHostEnvReady=true` 且 `cadWritesAttempted=false`。
- execution 必须 `status=ready`、`verificationStatus=verified`、`cadGeometryVerified=true`、`cadWritesAttempted=true`、`liveRunsConfirmed=true`、`executedRunCount>=2`，且 `executorMode=cad_agent_harness_preview`；`injected_executor` 或任何非 production executor mode 均 blocked。
- result 必须 `status=ready`、`verificationStatus=verified`、`cadGeometryVerified=true`、`stableGeometry=true`、run / verified / comparable count 均至少 2，且无 blocking reasons / missing evidence。
- closeout 自身固定 `cadWritesAttempted=false`，只写 closeout JSON。

验证记录：
- TDD green：实现 closeout gate / harness command 后 `$py -m unittest tests.core.test_phase10_rehearsal -v` 运行 27 项，全部 OK。
- direct P10/P9/Host regression：passed。`$py -m unittest tests.core.test_phase10_rehearsal tests.core.test_cad_session_host tests.core.test_cad_agent_harness tests.core.test_autocad_com_driver tests.core.test_phase9_single_preview tests.core.test_phase9_exit_gate tests.core.test_phase9_preview_bundle tests.core.test_tool_contract_react -v` 运行 99 项，全部 OK。
- Phase 5/6/7/8 contract regression：passed。`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter -v` 运行 53 项，全部 OK。
- doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- protected evidence diff / status check：passed。`git diff --name-only -- projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec agents\pipeline\pipeline_manifest.json config\entrypoint_custody_manifest.json` 与对应 `git status --short -- ...` 均无输出。

能力声明边界：本包只证明 P10B closeout 裁判已可测试、可由 harness 输出，并能拒绝 injected executor artifact；本轮没有连接 AutoCAD、没有执行真实 `cad-session-host` live run、没有创建真实 CAD run、没有写实体、不恢复训练、不推进表 C、不证明插件可用。

## Phase 10 - 第六包：P10B Closeout Artifact Integrity Hardening

日期：2026-06-20

状态：checked

触发：
- 用户要求 review 后继续推进。

review 结论：
- P10B closeout gate 已能拒绝 missing / blocked / injected executor artifact，但仍需要防止 launch packet、execution artifact 与 result artifact 被跨 run / 跨目录混搭后误放行。
- JSON artifact 读取也需要 fail-closed：合法 JSON 但顶层不是 object 时，应产生 invalid blocker，而不是命令异常退出。
- P10B live rehearsal scope 仍未由用户点名；本包只能加固 closeout gate，不连接 CAD、不执行 preview、不写实体。

目标：
- 在 `evaluate_phase10_rehearsal_closeout()` 中新增 artifact integrity blocker。
- 校验 launch / execution / result 的 `planPath`、`outputDir`、`runSpecs`、`runResults`、`runDirs`、`runSummaries`、run count、`resultPath` 与 execution `aggregateResult` 一致。
- 顶层非 object 的 JSON artifact 统一转成 closeout invalid blocker。
- 新增负测覆盖 foreign / mixed result artifact 与 non-object JSON artifact。

新增 / 修改文件：
- 修改 `core/contracts/phase10_rehearsal.py`
- 修改 `tests/core/test_phase10_rehearsal.py`
- 同步 `AGENTS.md`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`README.md`、`docs/planning/任务清单.md`、`docs/status/current.md`、`docs/status/changelog.md`、`docs/handoffs/current.md`、`docs/handoffs/package-index.md`、`docs/migration/execution-ledger.md`

门禁判断：
- `phase10_closeout_artifact_plan_path_mismatch`：launch packet 与 execution 的 `planPath` 不一致时 blocked。
- `phase10_closeout_artifact_output_dir_mismatch`：launch / execution / result 的 `outputDir` 不一致时 blocked。
- `phase10_closeout_artifact_result_path_mismatch`：result artifact 自声明路径、execution aggregate result path 或当前 closeout 读取路径不一致时 blocked。
- `phase10_closeout_artifact_result_mismatch`：execution `aggregateResult` 与实际 result artifact 的关键字段不一致时 blocked。
- `phase10_closeout_artifact_run_specs_mismatch`：launch 与 execution 的 run specs 不一致时 blocked。
- `phase10_closeout_artifact_run_dirs_mismatch`：execution run specs / run results、result run dirs / run summaries 不一致时 blocked。
- `phase10_closeout_artifact_run_count_mismatch`：planned / executed / result / list length 的 run count 不一致或低于最小 rehearsal count 时 blocked。
- 顶层非 object JSON artifact 返回对应 `phase10_closeout_*_invalid` blocker。

验证记录：
- targeted Phase 10 tests：passed。`$py -m unittest tests.core.test_phase10_rehearsal -v` 运行 29 项，全部 OK。
- 新增 `test_rehearsal_closeout_blocks_mixed_foreign_result_artifact`：foreign result artifact 被复制到当前 closeout 时 blocked，包含 result path / result / run dirs mismatch blocker。
- 新增 `test_rehearsal_closeout_blocks_non_object_json_artifact`：`phase10_rehearsal_execution.json` 为合法 JSON 数组时 blocked，包含 `phase10_closeout_execution_invalid`。

未触碰文件 / 路径：
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包只证明 P10B closeout gate 已补 artifact integrity 和 JSON fail-closed；本轮没有确认 rehearsal scope、没有连接 AutoCAD、没有执行真实 `cad-session-host` live run、没有创建真实 CAD run、没有写实体、不恢复训练、不推进表 C、不证明插件可用，也不放行 Phase 11。

## Phase 10 - 第七包：P10B Scope Confirmation Receipt Hardening

日期：2026-06-20

状态：checked

触发：
- 用户要求继续推进；当前仍未明确 P10B live rehearsal scope，不能直接写真实 CAD。

review 结论：
- P10B 已有 plan、aggregate、live-run gate、launch preflight 和 closeout gate，但此前确认只体现为 `--confirm-live-runs` 布尔参数，缺少可落盘、可审计、可被 preflight / run / closeout 共同消费的 scope confirmation artifact。
- 如果 plan 在确认后被改写，旧确认不应继续放行真实 rehearsal；closeout 也不能只校验 launch / execution / result 三件套，而要把 scope confirmation 纳入同一证据链。
- 安全推进方式是新增 scope receipt contract：只写确认 JSON，不连接 AutoCAD、不执行 preview、不创建 run dir、不写实体。

目标：
- 新增 `build_phase10_rehearsal_scope_receipt()`，输出 `phase10_rehearsal_scope_receipt.json`。
- 新增 harness `rehearsal-scope-receipt` 命令和 CLI `--scope-receipt` / `--confirmation` 参数。
- `rehearsal-preflight` 与 `rehearsal-run` 必须消费匹配 receipt；缺 receipt、stale receipt 或 receipt / plan 不一致时 blocked。
- `rehearsal-closeout` 必须把 scope receipt 纳入四件套完整性校验，缺 receipt 或 receipt / launch / execution / result 不一致时不放行 Phase 11。

新增 / 修改文件：
- 修改 `core/contracts/phase10_rehearsal.py`
- 修改 `core/contracts/cad_agent_harness.py`
- 修改 `core/contracts/__init__.py`
- 修改 `tests/core/test_phase10_rehearsal.py`
- 同步 `AGENTS.md`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`README.md`、`docs/planning/任务清单.md`、`docs/status/current.md`、`docs/status/changelog.md`、`docs/handoffs/current.md`、`docs/handoffs/package-index.md`、`docs/migration/execution-ledger.md`

门禁判断：
- `phase10_scope_receipt_missing`：preflight / run 缺 `phase10_rehearsal_scope_receipt.json` 时 blocked。
- `phase10_scope_receipt_live_runs_not_confirmed` / `phase10_scope_receipt_confirmation_missing`：缺 live-run 确认或确认声明为空时 receipt blocked。
- `phase10_scope_receipt_plan_path_mismatch` / `phase10_scope_receipt_plan_hash_mismatch` / `phase10_scope_receipt_scope_mismatch` / `phase10_scope_receipt_backend_mismatch` / `phase10_scope_receipt_run_count_mismatch` / `phase10_scope_receipt_run_specs_mismatch`：receipt 与当前 plan 不一致时 blocked。
- closeout 新增 `phase10_closeout_scope_receipt_missing`、`phase10_closeout_scope_receipt_not_ready`、`phase10_closeout_artifact_scope_receipt_path_mismatch`、`phase10_closeout_artifact_scope_receipt_hash_mismatch` 等 blocker；缺 receipt 或四件套不一致不能 `phase10CloseoutAllowed=true` / `phase11Allowed=true`。

验证记录：
- targeted Phase 10 tests：passed。`$py -m unittest tests.core.test_phase10_rehearsal -v` 运行 34 项，全部 OK。
- 新增 receipt 正测覆盖 builder、harness command 和 script command，均固定 `cadWritesAttempted=false`。
- 新增 stale receipt 负测：receipt 生成后 plan 被修改，launch packet blocked，包含 `phase10_scope_receipt_plan_hash_mismatch`。
- 新增 closeout 缺 receipt 负测：production-like artifact 删除 `phase10_rehearsal_scope_receipt.json` 后 closeout blocked，包含 `phase10_closeout_scope_receipt_missing`。
- direct P10/P9/Host regression：passed。`$py -m unittest tests.core.test_phase10_rehearsal tests.core.test_cad_session_host tests.core.test_cad_agent_harness tests.core.test_autocad_com_driver tests.core.test_phase9_single_preview tests.core.test_phase9_exit_gate tests.core.test_phase9_preview_bundle tests.core.test_tool_contract_react -v` 运行 106 项，全部 OK。
- Phase 5/6/7/8 contract regression：passed。`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter -v` 运行 53 项，全部 OK。
- doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- protected evidence diff / status check：passed。`git diff --name-only -- projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec agents\pipeline\pipeline_manifest.json config\entrypoint_custody_manifest.json` 与对应 `git status --short -- ...` 均无输出。

未触碰文件 / 路径：
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包只证明 P10B scope confirmation receipt 已可测试、可由 harness 输出，并被 preflight / run / closeout 消费；本轮没有确认 rehearsal scope、没有连接 AutoCAD、没有执行真实 `cad-session-host` live run、没有创建真实 CAD run、没有写实体、不恢复训练、不推进表 C、不证明插件可用，也不放行 Phase 11。

## Phase 10 - 第八包：P10B Scope Proposal Contract

日期：2026-06-20

状态：checked

触发：
- 用户继续要求推进；当前仍未明确 P10B live rehearsal scope，不能直接写真实 CAD。

review 结论：
- 当前真正 next 是 P10B Scope-confirmed live rehearsal，但仅有“继续推进”不能替代用户点名 scope。
- 已有 scope receipt / preflight / run / closeout 门禁要求确认 artifact；在确认之前，缺少一个从 ready P9 Exit evidence 收束候选 scope 的机器入口。
- 安全推进方式是新增 scope proposal contract：只读 P9 Exit run、report 和 CAD_PLAN，写 proposal JSON，不生成 receipt、不连接 AutoCAD、不执行 preview、不写实体。

目标：
- 新增 `build_phase10_rehearsal_scope_proposal()`，输出 `phase10_rehearsal_scope_proposal.json`。
- 新增 harness `rehearsal-scope-proposal` 命令。
- proposal 固定 `scopeConfirmed=false`、`liveRunsConfirmed=false`、`cadWritesAttempted=false`，只生成 `candidateScope` 和 operator confirmation actions。
- ready P9 Exit evidence、source CAD_PLAN、真实 backend、`runCount>=2` 和 `CODEX_PREVIEW` CAD_PLAN 是 proposal ready 条件；blocked proposal 不能进入 receipt / live run。

新增 / 修改文件：
- 修改 `core/contracts/phase10_rehearsal.py`
- 修改 `core/contracts/cad_agent_harness.py`
- 修改 `core/contracts/__init__.py`
- 修改 `tests/core/test_phase10_rehearsal.py`
- 同步 `AGENTS.md`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`README.md`、`docs/planning/任务清单.md`、`docs/status/current.md`、`docs/status/changelog.md`、`docs/handoffs/current.md`、`docs/handoffs/package-index.md`、`docs/migration/execution-ledger.md`

门禁判断：
- `phase10_scope_proposal_phase9_exit_missing` / `phase10_scope_proposal_phase9_exit_invalid` / `phase10_scope_proposal_phase9_exit_not_ready`：缺 ready P9 Exit evidence 时 blocked。
- `phase10_scope_proposal_cad_plan_missing` / `phase10_scope_proposal_cad_plan_invalid`：缺 source CAD_PLAN 或 CAD_PLAN validate 失败时 blocked。
- `phase10_scope_proposal_real_backend_required`：backend 不是 `cad-session-host` / `cad_session_host` 时 blocked。
- `phase10_scope_proposal_repetition_count_too_low`：run count 低于 2 时 blocked。
- `phase10_scope_proposal_non_preview_layer_forbidden`：CAD_PLAN 不写 `CODEX_PREVIEW` 时 blocked。

验证记录：
- targeted Phase 10 tests：passed。`$py -m unittest tests.core.test_phase10_rehearsal -v` 运行 38 项，全部 OK。
- 新增 proposal 正测覆盖 builder、harness command 和 script command，均固定 `cadWritesAttempted=false`、`scopeConfirmed=false`、`liveRunsConfirmed=false`。
- 新增缺 P9 evidence 负测：proposal blocked，包含 `phase10_scope_proposal_phase9_exit_invalid` 与 `phase10_scope_proposal_cad_plan_missing`。
- direct P10/P9/Host regression：passed。`$py -m unittest tests.core.test_phase10_rehearsal tests.core.test_cad_session_host tests.core.test_cad_agent_harness tests.core.test_autocad_com_driver tests.core.test_phase9_single_preview tests.core.test_phase9_exit_gate tests.core.test_phase9_preview_bundle tests.core.test_tool_contract_react -v` 运行 110 项，全部 OK。
- Phase 5/6/7/8 contract regression：passed。`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter -v` 运行 53 项，全部 OK。
- doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- protected evidence diff / status check：passed。`git diff --name-only -- projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec agents\pipeline\pipeline_manifest.json config\entrypoint_custody_manifest.json` 与对应 `git status --short -- ...` 均无输出。

未触碰文件 / 路径：
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包只证明 P10B scope proposal 已可测试、可由 harness 输出，并能从 ready P9 Exit evidence 收束未确认候选；本轮没有确认 rehearsal scope、没有生成 receipt、没有连接 AutoCAD、没有执行真实 `cad-session-host` live run、没有创建真实 CAD run、没有写实体、不恢复训练、不推进表 C、不证明插件可用，也不放行 Phase 11。

## Phase 10 - 第九包：P10B Scope-confirmed Live Rehearsal Blocker Closeout

日期：2026-06-20

状态：blocked / checked

触发：
- 用户说明 CAD 已打开，并要求在当前位置收口主 PlanMD、review 一轮、进行真实 CAD 校验。
- 本轮将该指令视为 P10B 默认候选 scope 的明确启动确认：`table / single_table_preview_repeatability`，目标是 2 次 live rehearsal，仍只允许写 `CODEX_PREVIEW`。

真实 CAD 校验动作：
- 启动 `cad-session-host`，绑定 localhost，使用 token，并轮询 `/rpc status`。
- 运行目录：`output/validation_runs/phase10-scope-confirmed-live-rehearsal-20260620-015727/`。
- 机器摘要：`output/validation_runs/phase10-scope-confirmed-live-rehearsal-20260620-015727/phase10_live_rehearsal_orchestrator_summary.json`。
- Host 日志：`cad_session_host.out.log` / `cad_session_host.err.log`。

结果：
- `hostStarted=true`，Host 已响应。
- `hostReady=false` / `/rpc status` `ready=false`。
- `cadWritesAttempted=false`。
- blocker：当前自动化会话无可接管活动 `AutoCAD.Application` / ROT 对象；状态同时显示 `acadProcessRunning=true`，且 `Dispatch fallback skipped because connect_existing_only=True`。

review 结论：
- AutoCAD 窗口或 `acad.exe` 进程存在，不等于可接管活动 COM 对象存在。
- 当前 fail-closed 行为正确：在 Host readiness 未通过时，不应生成 receipt / launch / execution / result / closeout 的假通过链条，也不应通过 `Dispatch` fallback 启动新 AutoCAD 实例。
- P10B 当前 next 不是继续新增合同层，而是解除 AutoCAD COM / ROT attach blocker 后复试 live rehearsal。

同步文件：
- 修改 `CORE_RESTRUCTURE_PLAN.md`
- 修改 `CORE_CONTEXT_BRIEF.md`
- 修改 `README.md`
- 修改 `AGENTS.md`
- 修改 `docs/planning/任务清单.md`
- 修改 `docs/status/current.md`
- 修改 `docs/status/changelog.md`
- 修改 `docs/status/issues.md`
- 修改 `docs/handoffs/current.md`
- 修改 `docs/handoffs/package-index.md`
- 修改 `docs/migration/execution-ledger.md`

未触碰文件 / 路径：
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

验证记录：
- real CAD live attempt：blocked as expected。`phase10_live_rehearsal_orchestrator_summary.json` 显示 `hostStarted=true`、`hostReady=false`、`cadWritesAttempted=false`，阻断于 AutoCAD COM / ROT attach readiness；未写 CAD。
- P10/P9/Host regression：passed。`$py -m unittest tests.core.test_phase10_rehearsal tests.core.test_cad_session_host tests.core.test_cad_agent_harness tests.core.test_autocad_com_driver tests.core.test_phase9_single_preview tests.core.test_phase9_exit_gate tests.core.test_phase9_preview_bundle tests.core.test_tool_contract_react -v` 运行 110 项，全部 OK。
- Phase 5/6/7/8 contract regression：passed。`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter -v` 运行 53 项，全部 OK。
- doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`；过程中发现并修正了 handoff 包 ID 误触发旧 R 类 9 项检查的问题，新 ID 为 `CAD-AGENT-VNEXT-PHASE10-LIVE-ATTACH-BLOCKED-09`。
- PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- protected evidence diff / status check：passed。`git diff --name-only -- projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec agents\pipeline\pipeline_manifest.json config\entrypoint_custody_manifest.json` 与对应 `git status --short -- ...` 均无输出。

能力声明边界：本包只证明 P10B live rehearsal 已真实尝试启动并被 AutoCAD COM / ROT attach blocker 正确阻断；没有执行 preview write、没有 created handles、没有 readback、没有 bbox / layer / entity audit、没有 result aggregate、没有 closeout proof、没有保存当前 DWG、没有改正式图层、不恢复训练、不推进表 C、不证明插件可用，也不放行 Phase 11。

## Phase 10 - 第十包：P10B AutoCAD COM Attach Hardening

日期：2026-06-20

状态：blocked / checked

触发：
- 用户指出 `CAD Session Host` 仍因活动 COM 对象不可接管 blocked，要求深度修复。
- 上一包已经证明 host 能启动但 readiness blocked；本包目标不是扩大 CAD 写入，而是补足安全 attach 路径、稳定诊断和真实 no-write 复验。

根因调查：
- 本机 COM 注册表只发现 `AutoCAD.Application.25` 与 `AutoCAD.Application.25.1`；代码原有 versioned ProgID 覆盖没有漏掉当前注册版本。
- 独立 PowerShell `Marshal.GetActiveObject("AutoCAD.Application.25/25.1")` 与 pywin32 路径一致返回 `MK_E_UNAVAILABLE`；裸 `AutoCAD.Application` 返回 invalid class string。
- 最新 host status 中 `acadProcessRunning=true`，但 `GetActiveObject` / `GetObject` 均不可用，ROT 枚举 `inspected=0`；因此当前阻塞不是 preview executor 逻辑，而是 Windows / AutoCAD 会话没有向当前自动化进程暴露可接管活动对象。

代码侧加固：
- 修改 `core/cad_io/autocad_com.py`
  - 新增 `AutoCADAttachError`，携带结构化 `diagnostics`。
  - existing-only attach 顺序改为：versioned `GetActiveObject` -> `GetObject(Class=...)` -> Running Object Table 枚举。
  - ROT candidate 支持 application-like 对象，也支持 document-like 对象通过 `.Application` 回溯。
  - 失败时分类 `blockerCode`：当前真实 blocker 为 `acad_process_running_without_visible_rot_object`。
  - `connect_existing_only=True` 仍禁止 `Dispatch` fallback，避免启动新 AutoCAD 或脱离用户当前 DWG。
- 修改 `core/cad_io/cad_session_host.py`
  - `/rpc status` ready 时返回 `attachDiagnostics`。
  - attach blocked 时将 `AutoCADAttachError.diagnostics` 原样返回给 orchestrator / evidence。
- 修改 `tests/core/test_autocad_com_driver.py`
  - 覆盖 `GetObject` fallback、ROT application attach、ROT document `.Application` attach。
  - 覆盖 active object 缺失时不调用 `Dispatch`，并返回 `acad_process_running_without_visible_rot_object`。
- 修改 `tests/core/test_cad_session_host.py`
  - 覆盖 status ready / blocked 均暴露 `attachDiagnostics`。

真实 no-write probe：
- 输出目录：`output/validation_runs/phase10-com-attach-hardened-readiness-20260620-021746/`
- summary：`output/validation_runs/phase10-com-attach-hardened-readiness-20260620-021746/cad_session_host_readiness_summary.json`
- 独立探针：`output/validation_runs/phase10-com-attach-hardened-readiness-20260620-021746/independent_getactiveobject_probe.txt`
- 结果：`hostStarted=true`，`hostReady=false`，`cadWritesAttempted=false`。
- Host status：`acadProcessRunning=true`、`ROT inspected=0`、`blockerCode=acad_process_running_without_visible_rot_object`。

同步文件：
- 修改 `AGENTS.md`
- 修改 `CORE_CONTEXT_BRIEF.md`
- 修改 `CORE_RESTRUCTURE_PLAN.md`
- 修改 `README.md`
- 修改 `core/cad_io/autocad_com.py`
- 修改 `core/cad_io/cad_session_host.py`
- 修改 `docs/handoffs/current.md`
- 修改 `docs/handoffs/package-index.md`
- 修改 `docs/migration/execution-ledger.md`
- 修改 `docs/planning/任务清单.md`
- 修改 `docs/status/changelog.md`
- 修改 `docs/status/current.md`
- 修改 `docs/status/issues.md`
- 修改 `tests/core/test_autocad_com_driver.py`
- 修改 `tests/core/test_cad_session_host.py`

验证记录：
- targeted attach / host regression：passed。`$py -m unittest tests.core.test_autocad_com_driver tests.core.test_cad_session_host -v` 运行 31 项，全部 OK。
- real no-write readiness probe：blocked as expected。`cad_session_host_readiness_summary.json` 显示 host 已启动但 `hostReady=false`，阻断于 `acad_process_running_without_visible_rot_object`；`cadWritesAttempted=false`，未写 CAD。
- P10/P9/Host regression：passed。`$py -m unittest tests.core.test_phase10_rehearsal tests.core.test_cad_session_host tests.core.test_cad_agent_harness tests.core.test_autocad_com_driver tests.core.test_phase9_single_preview tests.core.test_phase9_exit_gate tests.core.test_phase9_preview_bundle tests.core.test_tool_contract_react -v` 运行 114 项，全部 OK。
- Phase 5/6/7/8 contract regression：passed。`$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter -v` 运行 53 项，全部 OK。
- doc governance audit：passed。`$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- protected evidence diff / status check：passed。`git diff --name-only -- projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec agents\pipeline\pipeline_manifest.json config\entrypoint_custody_manifest.json` 与对应 `git status --short -- ...` 均无输出；本轮新增 `output/validation_runs/phase10-com-attach-hardened-readiness-20260620-021746/` 已作为 evidence 在本包登记。

未触碰文件 / 路径：
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包只证明 `cad-session-host` 的安全 attach 路径、blocker 分类和 status diagnostics 已加固，并通过真实 no-write probe 确认当前环境仍未暴露可接管活动 AutoCAD COM / ROT 对象。它不证明 P10B live CAD runs 已执行、不写 `CODEX_PREVIEW` 实体、不创建 handles、不 readback、不保存 DWG、不恢复训练、不推进表 C、不证明插件可用，也不放行 Phase 11。下一步应处理 Windows / AutoCAD COM 可见性、注册或同权限会话问题，再重新运行 readiness 与 P10B live rehearsal。

## Phase 10 - 第十一包：P10B CAD Reopened Readiness Retry

日期：2026-06-20

状态：blocked / checked

触发：
- 用户说明 CAD 已打开，要求继续进行校验。
- 本轮只复验 `cad-session-host` readiness，不扩大 CAD 写入，不绕过 existing-only attach safety。

真实 no-write probe：
- 输出目录：`output/validation_runs/phase10-cad-reopened-readiness-20260620-023225/`
- summary：`output/validation_runs/phase10-cad-reopened-readiness-20260620-023225/cad_session_host_readiness_summary.json`
- 独立探针：`output/validation_runs/phase10-cad-reopened-readiness-20260620-023225/independent_getactiveobject_probe.txt`
- Host 启动日志：`output/validation_runs/phase10-cad-reopened-readiness-20260620-023225/cad_session_host.out.log`

结果：
- `hostStarted=true`，Host 已输出 listening 状态并响应 `/rpc status`。
- `hostReady=false`，`cadWritesAttempted=false`。
- `acadProcessRunning=true`，但 `ROT inspected=0`。
- `blockerCode=acad_process_running_without_visible_rot_object`。
- PowerShell `Marshal.GetActiveObject("AutoCAD.Application.25.1")` 与 `.25` 仍返回 `MK_E_UNAVAILABLE`；裸 `AutoCAD.Application` 返回 `CO_E_CLASSSTRING`。
- 本轮未进入 P10B `rehearsal-run`，未写 `CODEX_PREVIEW` 实体，未产生 created handles / readback / bbox / layer / entity audit / result aggregate / closeout proof。

同步文件：
- 修改 `AGENTS.md`
- 修改 `CORE_CONTEXT_BRIEF.md`
- 修改 `CORE_RESTRUCTURE_PLAN.md`
- 修改 `README.md`
- 修改 `docs/handoffs/current.md`
- 修改 `docs/handoffs/package-index.md`
- 修改 `docs/migration/execution-ledger.md`
- 修改 `docs/planning/任务清单.md`
- 修改 `docs/status/changelog.md`
- 修改 `docs/status/current.md`
- 修改 `docs/status/issues.md`

验证记录：
- real no-write readiness probe：blocked。`cad_session_host_readiness_summary.json` 显示 host 可启动但 readiness 仍 blocked 于 `acad_process_running_without_visible_rot_object`；`cadWritesAttempted=false`，未写 CAD。
- independent COM probe：blocked。`independent_getactiveobject_probe.txt` 显示 `AutoCAD.Application.25.1` / `.25` 为 `MK_E_UNAVAILABLE`，裸 `AutoCAD.Application` 为 `CO_E_CLASSSTRING`。
- doc governance audit：passed。首次因 `docs/handoffs/current.md` 增至 141 行超过 140 行 active doc budget 失败；随后将较旧的“自适应能力成长训练包”一行从 current handoff 窗口和 package index 移出，历史仍保留在 changelog，重跑 `$py scripts\run_doc_governance_audit.py --fail-on-findings` 返回 `status=pass` / `finding_count=0`。
- PlanMD / doc governance tests：passed。`$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v` 运行 45 项，全部 OK。
- OpenSpec validate：passed。`openspec.cmd validate --all --strict --json --no-interactive` 返回 20/20 passed。
- final `git diff --check`：passed，退出码 0；仅保留 Git CRLF 工作区警告。
- protected evidence diff / status check：passed。`git diff --name-only -- projects libraries docs\training\training-sources.json libraries\system_library\registry.json openspec agents\pipeline\pipeline_manifest.json config\entrypoint_custody_manifest.json` 与对应 `git status --short -- ...` 均无输出。

未触碰文件 / 路径：
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：本包只证明“用户重新打开 CAD 后，当前自动化会话仍无法接管活动 AutoCAD COM / ROT 对象”。它不证明 P10B live CAD runs 已执行、不写 `CODEX_PREVIEW` 实体、不创建 handles、不 readback、不保存 DWG、不恢复训练、不推进表 C、不证明插件可用，也不放行 Phase 11。下一步仍应处理 Windows / AutoCAD COM 可见性、注册或同权限会话问题，再重新运行 readiness 与 P10B live rehearsal。
## Phase 10 - 第十二包：P10B Focused Live Rehearsal Verified Closeout

日期：2026-06-20

状态：verified / closed

触发：
- 用户要求继续快速收尾验证，并明确本轮可使用 elevated / full 权限操作 AutoCAD、registry 和 `D:\Design\CAD`。
- 前序 P10B readiness 曾因 `acad_process_running_without_visible_rot_object` blocked；本轮先处理 AutoCAD 配置和 CAD-MCP stale COM reference，再复跑真实 live rehearsal。

真实 CAD / 配置动作：
- 桌面配置包：`C:\Users\User\Desktop\AutoCAD 2026 - 简体中文 (Simplified Chinese)_cust_settings.zip`。
- 配置备份目录：`output/validation_runs/phase10-cad-config-restore-backup-20260620-033652/`。
- 已从桌面迁移包恢复 HKCU profile registry 与 AppData 文件；后续 COM readback 显示模型背景、OSMODE / SNAPUNIT / LWDISPLAY 等配置已按恢复后的 AutoCAD profile 暴露。
- CAD-MCP 本地代码侧修复 stale COM reference：`C:\Users\User\.codex\mcp\CAD-MCP\src\cad_controller.py` 在 `is_running()` 中触碰 `app.Visible` / `doc.Name`，失效时清空 cached COM object，避免 server 误以为旧 COM 仍可用。
- CAD-MCP 直接 smoke 已通过：`cad-mcp-direct-smoke-readback.json` 读回 `CODEX_PREVIEW` polyline，未保存 DWG。

预备 P9 evidence：
- 目录：`output/validation_runs/phase10-fast-closeout-host-preview-20260620-0418/`
- harness：`scripts/cad_agent_harness.py preview --backend cad-session-host`
- 结果：`status=geometry_verified`、`verificationStatus=verified`、created/readback handles 均为 4、全部在 `CODEX_PREVIEW`、`savedCurrentDwg=false`。
- P9 exit gate：`phase10Allowed=true`、`completionCanClaimComplete=true`。

P10B live rehearsal evidence：
- 目录：`output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/`
- scope：`phase10.table.rehearsal` / `table` / `single_table_preview_repeatability` / `runCount=2` / backend `cad-session-host`。
- 命令链：`rehearsal-plan` -> `rehearsal-scope-receipt` -> `rehearsal-preflight` -> `rehearsal-run` -> `rehearsal-result` -> `rehearsal-closeout`。
- run_01：`geometry_verified` / `verified`，backend `cad_session_host`，created/readback count 均为 4，全部在 `CODEX_PREVIEW`，bbox size `900.0 x 450.0`，`savedCurrentDwg=false`。
- run_02：`geometry_verified` / `verified`，backend `cad_session_host`，created/readback count 均为 4，全部在 `CODEX_PREVIEW`，bbox size `900.0 x 450.0`，`savedCurrentDwg=false`。
- aggregate：`stableGeometry=true`、`runCount=2`、`verifiedRunCount=2`、`diffCount=0`、`failureCount=0`、`blockingReasons=[]`、`missingEvidence=[]`。
- closeout：`phase10CloseoutAllowed=true`、`phase11Allowed=true`、`sourceCadWritesAttempted=true`、`cadGeometryVerified=true`。

外部资源收口：
- 本轮 `cad-session-host` 已停止，remaining host process count 为 0。
- AutoCAD 程序仍保留运行；当前 COM document collection 为 0，本轮临时未保存 `Drawing2.dwg` 已不再活动。
- 本轮未保存当前 DWG，未写正式图层，未推进表 C，未恢复训练，未证明 native plugin 可用。

同步文件：
- 修改 `CORE_RESTRUCTURE_PLAN.md`
- 修改 `CORE_CONTEXT_BRIEF.md`
- 修改 `docs/planning/任务清单.md`
- 修改 `AGENTS.md`
- 修改 `README.md`
- 修改 `docs/status/current.md`
- 修改 `docs/migration/execution-ledger.md`

能力声明边界：本包只证明 P10B focused live rehearsal 在 `cad-session-host` + AutoCAD 活动对象链路下完成 2 次稳定 `CODEX_PREVIEW` preview/readback，并由 result / closeout gate 放行 Phase 11。它不证明正式训练恢复、表 C 推进、native plugin 可用、业务 DWG 保存、正式图层写入或用户视觉验收。

## Phase 11 - ToolCard / Adapter Registry intake

日期：2026-06-20

状态：checked / closed

触发：
- 用户要求进入 P11，把现有 harness / `cad-session-host` / legacy preview-readback 链路注册为 Tool Gateway 后的 registered adapter，而不是继续作为散脚本调用。
- 边界固定为不写真实 CAD、不保存 DWG、不改正式图层、不恢复训练、不推进表 C、不做 native plugin，不移动 / 删除 / 改写 protected evidence。

代码侧收口：
- 新增 `core/contracts/adapter_registry.py`，定义 `RegisteredAdapter`、registry authorization、harness result consumption 与 blocked harness JSON 返回结构。
- `default_adapter_registry()` 注册 harness commands、`cad-session-host.preview/readback`、legacy preview/readback adapter；每个 adapter 都有 `ToolCard`、`ToolContract`、allowed / forbidden effects、entrypoint、backend、evidence boundary 与是否执行 CAD 的显式字段。
- `consume_harness_result_via_registry()` 只读消费既有 `cad-agent-harness-result/v1`，允许 `rehearsal-result` / `rehearsal-closeout` 作为既有 readback proof 输入；若 result consumer 声称 `cadWritesAttempted=true`，fail-closed 为 `harness_result_consumer_must_be_read_only`。
- `core/contracts/cad_agent_harness.py` 现在在加载 plan / run dir 或调用后端前先执行 registry authorization；新增 CLI 参数 `--requested-effect` / `--adapter-id`。越权 effect（如 `dwg_save`、`save_current_dwg`、`formal_layer_write`、训练 / 表 C / plugin mutation）会返回 blocked JSON，不写 result artifact。

新增 / 修改测试：
- `tests/core/test_vnext_contract_adapters.py` 新增 P11 registry tests，覆盖默认 registry 注册、allowed / forbidden effects、P10 harness result consumption、read-only consumer fail-closed。
- `tests/core/test_phase10_rehearsal.py` 新增 harness CLI registry annotation 与 forbidden effect bypass tests，确认 `rehearsal-result --requested-effect dwg_save` 在写 artifact 前 blocked。

同步文件：
- 修改 `CORE_RESTRUCTURE_PLAN.md`
- 修改 `CORE_CONTEXT_BRIEF.md`
- 修改 `docs/planning/任务清单.md`
- 修改 `docs/handoffs/current.md`
- 修改 `docs/handoffs/package-index.md`
- 修改 `docs/migration/execution-ledger.md`

验证记录：
- TDD red run：`$py -m unittest tests.core.test_vnext_contract_adapters tests.core.test_phase10_rehearsal -v` 初始失败于缺 `core.contracts.adapter_registry`、缺 `requested_effects` 参数和缺 `registryAuthorization` 字段，符合预期。
- Targeted P11 regression：同一命令实现后运行 49 项，全部 OK。
- 收尾验证以本轮最终命令为准：vNext / legacy / phase10 regression、doc governance audit、PlanMD / doc governance tests 与 `git diff --check`。

未触碰文件 / 路径：
- `output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/**` 只读查看，未改写。
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：P11 只证明 Tool Gateway 后的 adapter registry 最小闭环、harness result 受控消费和 CLI 越权拦截。它不执行新的 CAD preview、不保存当前 DWG、不写正式图层、不恢复训练、不推进表 C、不证明 native plugin 可用。当前 next 切到 Phase 12：Mock Plugin Transaction；P12 尚未启动。

## Phase 12 - Mock Plugin Transaction

日期：2026-06-20

状态：checked / closed

触发：
- 用户要求进入 P12，用 mock plugin-like backend 验证 transaction 字段、rollback / committed_preview 语义、ledger refs，以及 fake / mock / real proof 口径分离。
- 边界固定为不写真实 CAD、不连接 AutoCAD、不保存 DWG、不改正式图层、不恢复训练、不推进表 C、不做 native plugin，不移动 / 删除 / 改写 protected evidence。

代码侧收口：
- 新增 `core/contracts/mock_plugin_transaction.py`，定义 `mock-plugin-transaction/p12/v1` 合同与 `mock-plugin.transaction` transaction result。
- 最小 transaction 字段包括：`transactionId`、`rollbackRequired`、`rollbackStatus`、`committedPreview`、`createdHandles`、`createdHandlesRef`、`blockedReason`、`retryable`、`documentState`、`ledgerRefs`、`proofStatus`、`cadGeometryVerified=false`、`savedCurrentDwg=false`。
- `success` 裁决为 `proofStatus=mock_committed_preview`、`committedPreview=true`、`rollbackStatus=not_required`、`documentState=preview_committed`。
- `failure` / `blocked` 裁决为事务前或提交前 blocked，`committedPreview=false`，`documentState=unchanged`，不产生 real CAD proof。
- `rollback_success` 裁决为 `proofStatus=mock_rollback_verified`、`rollbackStatus=rolled_back`、`documentState=rolled_back`。
- `rollback_failed` 裁决为 `proofStatus=mock_rollback_failed`、`rollbackStatus=rollback_failed`、`documentState=in_flight_unknown`、`retryable=false`。
- `mock_plugin_transaction_evidence_package()` 只生成 `mock_plugin_transaction`、`mock_ledger_refs` 与 `no_save_guard` evidence；不生成 `real_cad_readback`，不能 claim `geometry_verified`。
- `core/contracts/adapter_registry.py` 注册 `mock-plugin.transaction` adapter，permission class 为 `deterministic_verify`，allowed effects 为 mock transaction / rollback / ledger refs，forbidden effects 包含 `plugin_execute`、`cad_execute`、`real_cad_readback`、`dwg_save`、`save_current_dwg`、`formal_layer_write`、训练 / 表 C / protected evidence mutation。
- `core/contracts/cad_agent_harness.py` 新增 `mock-plugin-transaction` command 与 `--mock-transaction-mode`，仍先走 P11 registry authorization；越权 effect 在 mock backend 前 fail-closed。
- `core/contracts/__init__.py` 导出 P12 mock transaction 合同入口。

新增 / 修改测试：
- `tests/core/test_vnext_contract_adapters.py` 新增 P12 mock plugin transaction tests，覆盖 success、failure、rollback_success、rollback_failed、blocked 五类 proof status。
- 覆盖 `mock-plugin.transaction` registry 注册、allowed / forbidden effects、permission class、harness result 中的 `transaction` 消费路径。
- 覆盖 CLI / harness 请求 `plugin_execute`、`cad_execute`、`real_cad_readback`、`dwg_save` 等越权 effect 时，在后端前 blocked。
- 覆盖 mock backend 不满足 `real_cad_readback`、不 claim `cadGeometryVerified`、ledger refs 存在且 `createdHandlesRef` 可追溯。

同步文件：
- 修改 `CORE_RESTRUCTURE_PLAN.md`
- 修改 `CORE_CONTEXT_BRIEF.md`
- 修改 `docs/planning/任务清单.md`
- 修改 `docs/migration/execution-ledger.md`
- 修改 `docs/status/current.md`
- 修改 `docs/handoffs/current.md`
- 修改 `docs/handoffs/package-index.md`
- 修改 `AGENTS.md`
- 修改 `AGENTS.md`
- 修改 `README.md`

验证记录：
- TDD red run：`$py -m unittest tests.core.test_vnext_contract_adapters -v` 初始失败于缺 `core.contracts.mock_plugin_transaction`、缺 `mock-plugin.transaction` registry registration、缺 `mock_transaction_mode` 参数，符合预期。
- Targeted P12 regression：实现后 `tests.core.test_vnext_contract_adapters` 运行 13 项，全部 OK。
- 收尾验证以本轮最终命令为准：vNext / legacy / phase10 regression、doc governance audit、PlanMD / doc governance tests 与 `git diff --check`。

未触碰文件 / 路径：
- `output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/**` 未改写。
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：P12 只证明 mock plugin-like transaction 合同、rollback / committed_preview 语义、ledger refs 与 mock / real proof 分离。它不连接 AutoCAD、不调用 native plugin、不写真实 CAD、不保存当前 DWG、不写正式图层、不恢复训练、不推进表 C，也不证明 native plugin 可用。后续 P13A 已完成 no-CAD / no-plugin skeleton；真实 scoped native backend 仍未启动。

## Phase 13A - Native Thin Backend Skeleton

日期：2026-06-20

状态：checked / closed

触发：
- 用户要求进入 P13 第一包，先做 Native Thin Backend 的合同层和 registry 接入，不直接启动真实 AutoCAD，不调用真实 native plugin。
- 边界固定为不连接 AutoCAD、不调用真实 native plugin、不写真实 CAD、不保存 DWG、不改正式图层、不恢复训练、不推进表 C，不移动 / 删除 / 改写 protected evidence。

代码侧收口：
- 新增 `core/contracts/native_thin_backend.py`，定义 `native-thin-backend/p13/v1` skeleton 合同。
- 最小字段复用 P12 transaction：`transactionId`、`rollbackRequired`、`rollbackStatus`、`committedPreview`、`createdHandlesRef`、`blockedReason`、`retryable`、`documentState`、`ledgerRefs`。
- 新增 P13 字段：`noSaveAudit`、`rollbackProof`、`nativePluginInvoked=false`、`previewStrategy=memory_transaction`、`cadGeometryVerified=false`、`cadWritesAttempted=false`、`savedCurrentDwg=false`。
- `native_thin_backend_evidence_package()` 只生成 `native_thin_backend_contract`、`native_thin_no_save_audit`、`native_thin_rollback_proof`、`native_thin_ledger_refs` 与 `no_save_guard` evidence；不生成 `real_cad_readback`，不能 claim `geometry_verified`。
- `core/contracts/adapter_registry.py` 注册 `native-thin.backend` adapter，permission class 为 `deterministic_verify`，allowed effects 为 `native_thin_contract_prepare`、`native_thin_no_save_audit`、`native_thin_rollback_proof_record`、`native_thin_ledger_ref_write`。
- P13 forbidden effects 包含 `native_plugin_execute`、`plugin_execute`、`cad_execute`、`cad_preview_write`、`apply_preview_batch`、`real_cad_readback`、`dwg_save`、`save_current_dwg`、`commit_save`、`save_copy`、`formal_layer_write`、删除、训练 / 表 C / protected evidence mutation。
- `core/contracts/cad_agent_harness.py` 新增 `native-thin-backend` command 与 `--native-backend-mode`，仍先走 registry authorization；越权 effect 在 skeleton backend 前 fail-closed。
- `core/contracts/__init__.py` 导出 P13 native skeleton 合同入口。

新增 / 修改测试：
- `tests/core/test_vnext_contract_adapters.py` 新增 P13 native thin backend tests，覆盖 skeleton 合同字段、blocked mode、registry ToolCard / allowed / forbidden effects、harness 不能绕过 ToolContract。
- TDD red run 初始失败于缺 `core.contracts.native_thin_backend`、缺 `native-thin.backend` registry registration、缺 `native_backend_mode` 参数，符合预期。
- Targeted P13 regression：实现后 `tests.core.test_vnext_contract_adapters` 运行 17 项，全部 OK。

同步文件：
- 修改 `CORE_RESTRUCTURE_PLAN.md`
- 修改 `CORE_CONTEXT_BRIEF.md`
- 修改 `docs/planning/任务清单.md`
- 修改 `docs/migration/execution-ledger.md`
- 修改 `docs/status/current.md`
- 修改 `docs/handoffs/current.md`
- 修改 `docs/handoffs/package-index.md`
- 修改 `AGENTS.md`
- 修改 `README.md`

未触碰文件 / 路径：
- `output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/**` 未改写。
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：P13A 只证明 native thin backend 的合同字段、ToolCard / Adapter Registry / ToolContract / EvidencePackage 接入、no-save audit 字段、rollback proof 字段和越权拦截。它不连接 AutoCAD、不调用真实 native plugin、不写真实 CAD、不保存当前 DWG、不写正式图层、不恢复训练、不推进表 C，也不证明 native plugin 可用。P13 真实 scoped backend spike 仍未启动；若继续，必须先单独确认 scope、CAD_PLAN、`CODEX_PREVIEW`、readback、rollback 和 no-save guard。

## Phase 13B - Native Thin Backend Preflight / Launch Packet

日期：2026-06-20

状态：checked / closed

触发：
- 用户要求继续 P13，但本轮只推进 Native Thin Backend scoped spike preflight / launch packet，不直接执行 AutoCAD 或真实 native plugin。
- 边界固定为不训练、不推进表 C、不沉淀系统资产包、不改 protected evidence、不保存或修改业务 DWG、不写正式图层。

代码侧收口：
- `core/contracts/native_thin_backend.py` 新增 `native-thin-preflight/p13b/v1` 合同。
- `build_native_thin_backend_scope_receipt()` 要求 scope confirmation、CAD_PLAN、`CODEX_PREVIEW`、readback plan、rollback plan、no-save guard 和 backend identity；缺任一项或非 `CODEX_PREVIEW` 均 blocked。
- `build_native_thin_backend_launch_packet()` 只消费 ready scope receipt，生成 ready / blocked JSON launch packet；ready 只表示发车前资料完整，不授权 live execution。
- `P13_NATIVE_ALLOWED_EFFECTS` 增加 `native_thin_scope_receipt_write`、`native_thin_preflight_packet_write`、`native_thin_launch_packet_write`；`native_plugin_execute`、`cad_execute`、`real_cad_readback`、`dwg_save`、`formal_layer_write` 等仍在 backend 前 blocked。
- `core/contracts/cad_agent_harness.py` 的 `native-thin-backend` 支持 `--native-backend-mode scope_receipt/preflight` 与 `--confirm-native-scope`，仍先走 registry authorization。
- ready packet 固定 `cadWritesAttempted=false`、`nativePluginInvoked=false`、`liveExecutionAuthorized=false`、`cadGeometryVerified=false`，并保留 `notEvidenceFor` 中的 `real_cad_readback` / `native_plugin_execution`。

新增 / 修改测试：
- `tests/core/test_vnext_contract_adapters.py` 新增 P13B tests，覆盖缺 scope / CAD_PLAN / safety plans blocked、非 `CODEX_PREVIEW` blocked、ready scope receipt、ready launch packet、缺或 blocked receipt、allowed / forbidden effects、harness 不能绕过 registry。
- TDD red run 初始失败于缺 `build_native_thin_backend_scope_receipt()` / `build_native_thin_backend_launch_packet()`、缺 P13B allowed effects、缺 `native_scope_confirmed` harness 参数，符合预期。
- Targeted P13B regression：实现后 `tests.core.test_vnext_contract_adapters` 运行 23 项，全部 OK。

同步文件：
- 修改 `CORE_RESTRUCTURE_PLAN.md`
- 修改 `CORE_CONTEXT_BRIEF.md`
- 修改 `docs/planning/任务清单.md`
- 修改 `docs/migration/execution-ledger.md`
- 修改 `docs/status/current.md`
- 修改 `docs/handoffs/current.md`
- 修改 `docs/handoffs/package-index.md`

未触碰文件 / 路径：
- `output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/**` 未改写。
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：P13B 只证明 native thin backend 的 scope receipt、preflight / launch packet、ToolCard / registry authorization 和 proof boundary。它不连接 AutoCAD、不调用真实 native plugin、不写真实 CAD、不保存当前 DWG、不写正式图层、不恢复训练、不推进表 C，也不证明 native plugin 可用。真实 native backend live spike 仍未启动；若继续，必须先单独确认 scope、CAD_PLAN、`CODEX_PREVIEW`、readback、rollback 和 no-save guard。
## Phase 13C - Native Thin Backend Authorization Gate / Execution Receipt

日期：2026-06-20

状态：checked / closed

触发：
- 用户要求继续 P13，但本轮目标不是连接 AutoCAD 或调用真实 native plugin，而是建立真实 scoped live spike 前的 authorization gate / scoped execution receipt。
- 边界固定为不训练、不推进表 C、不沉淀系统资产包、不保存 DWG、不写正式图层、不改 protected evidence；不能把“继续推进”当作 live spike 授权。

代码侧收口：
- `core/contracts/native_thin_backend.py` 新增 `native-thin-authorization/p13c/v1` 与 `native-thin-execution-receipt/p13c/v1` 合同。
- `build_native_thin_backend_authorization_gate()` 消费 P13B ready launch packet，校验 `CAD_PLAN`、`CODEX_PREVIEW`、readback plan、rollback plan、no-save guard、backend identity、`cadWritesAttempted=false`、`nativePluginInvoked=false`、`cadGeometryVerified=false`，并对 launch packet critical scope 生成稳定 hash。
- 授权必须显式提供 scope、CAD_PLAN、`CODEX_PREVIEW`、readback、rollback、no-save guard、backend identity 与 launch packet hash 确认；缺用户授权时为 `authorization_pending` / blocked，scope/hash drift 为 `native_scope_hash_mismatch` / blocked。
- `build_native_thin_backend_execution_receipt()` 只消费 ready authorization gate，生成 scoped receipt；即使 gate authorized，也固定 `executionStarted=false`、`cadWritesAttempted=false`、`nativePluginInvoked=false`、`cadGeometryVerified=false`。
- `P13_NATIVE_ALLOWED_EFFECTS` 增加 `native_thin_live_authorization_gate_write` 与 `native_thin_execution_receipt_write`；`native_plugin_execute`、`cad_execute`、`real_cad_readback`、`dwg_save`、`formal_layer_write` 等仍为 forbidden effects。
- `core/contracts/cad_agent_harness.py` 的 `native-thin-backend` 支持 `--native-backend-mode authorization/execution_receipt`、`--launch-packet` 与 `--authorization-gate`，仍先走 registry authorization；默认只输出 JSON pending / blocked / receipt，不启动后端。
- `core/contracts/adapter_registry.py` 更新 native thin adapter boundary 与 allowed evidence，仍声明不执行 CAD、不调用 plugin、不保存 DWG。

新增 / 修改测试：
- `tests/core/test_vnext_contract_adapters.py` 新增 P13C tests，覆盖 ready launch packet 进入 authorization pending、缺授权 execution receipt blocked、显式授权只生成 scoped receipt 且不执行、scope/hash drift blocked、registry allowed / forbidden effects、harness 不能绕过 ToolCard。
- TDD red run 初始失败于缺 `build_native_thin_backend_authorization_gate()` / `build_native_thin_backend_execution_receipt()`、缺 P13C allowed effects，符合预期。
- Targeted P13C regression：实现后 `tests.core.test_vnext_contract_adapters` 运行 28 项，全部 OK。

同步文件：
- 修改 `CORE_RESTRUCTURE_PLAN.md`
- 修改 `CORE_CONTEXT_BRIEF.md`
- 修改 `docs/planning/任务清单.md`
- 修改 `docs/migration/execution-ledger.md`
- 修改 `docs/status/current.md`
- 修改 `docs/handoffs/current.md`
- 修改 `docs/handoffs/package-index.md`

未触碰文件 / 路径：
- `output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/**` 未改写。
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：P13C 只证明 native thin backend 的 live spike authorization gate、scoped execution receipt、scope/hash 漂移拦截、ToolCard / registry authorization 和 proof boundary。它不连接 AutoCAD、不调用真实 native plugin、不写真实 CAD、不保存当前 DWG、不写正式图层、不恢复训练、不推进表 C，也不证明 native plugin 可用或 `geometry_verified`。真实 native backend live spike 仍未启动；若继续，必须先由用户单独确认 scope、CAD_PLAN、`CODEX_PREVIEW`、readback、rollback、no-save guard 和 backend identity。
## Phase 13D - Native Thin Backend Readiness / Operator Authorization Request

日期：2026-06-21

状态：checked / closed

触发：
- 用户要求继续 P13，但本轮不得连接 AutoCAD、不得调用真实 native plugin、不得写真实 CAD；目标是在 P13C execution receipt 之后建立真实 live spike readiness packet 与 operator authorization request。
- 边界固定为不训练、不推进表 C、不保存 DWG、不写正式图层、不改 protected evidence；真实 live spike 仍必须停下来等待用户单独确认。

代码侧收口：
- `core/contracts/native_thin_backend.py` 新增 `native-thin-readiness/p13d/v1` 合同。
- `build_native_thin_backend_readiness_packet()` 消费 P13C ready execution receipt，校验 scope、CAD_PLAN、`CODEX_PREVIEW`、readback plan、rollback plan、no-save guard、backend identity、launch packet hash 与 authorization receipt hash。
- P13D 输出只允许 `blocked` 或 `ready_for_user_authorization`；即使 ready，也固定 `cadWritesAttempted=false`、`nativePluginInvoked=false`、`executionStarted=false`、`cadGeometryVerified=false`、`savedCurrentDwg=false`。
- readiness packet 内嵌 `operatorAuthorizationRequest`，并可写出 `native_thin_readiness_packet.json` 与 `native_thin_operator_authorization_request.json`；它只请求用户授权，不代表用户已授权，也不启动真实 backend。
- `P13_NATIVE_ALLOWED_EFFECTS` 增加 `native_thin_live_readiness_packet_write` 与 `native_thin_operator_authorization_request_write`；`native_plugin_execute`、`cad_execute`、`real_cad_readback`、`dwg_save`、`formal_layer_write` 仍为 forbidden effects。
- `core/contracts/cad_agent_harness.py` 的 `native-thin-backend` 支持 `--native-backend-mode readiness` 与 `--execution-receipt`，仍先走 P11 Adapter Registry / ToolCard / ToolContract 授权。
- `core/contracts/adapter_registry.py` 与 `core/contracts/__init__.py` 同步 P13D evidence boundary 和导出。

新增 / 修改测试：
- `tests/core/test_vnext_contract_adapters.py` 新增 P13D tests，覆盖 P13C receipt -> readiness request、缺 receipt blocked、authorization receipt hash drift blocked、receipt 冒充真实执行 / real proof blocked、registry allowed / forbidden effects，以及 harness 不能绕过 ToolCard。
- TDD red run 初始失败于缺 `build_native_thin_backend_readiness_packet()` 与缺 P13D allowed effects，符合预期。
- Targeted P13D regression：实现后 `tests.core.test_vnext_contract_adapters.P13DNativeThinReadinessTests` 运行 4 项，全部 OK。
- Targeted adapter regression：实现后 `tests.core.test_vnext_contract_adapters` 运行 32 项，全部 OK。

同步文件：
- 修改 `CORE_RESTRUCTURE_PLAN.md`
- 修改 `CORE_CONTEXT_BRIEF.md`
- 修改 `docs/planning/任务清单.md`
- 修改 `docs/migration/execution-ledger.md`
- 修改 `docs/status/current.md`
- 修改 `docs/handoffs/current.md`
- 修改 `docs/handoffs/package-index.md`

未触碰文件 / 路径：
- `output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/**` 未改写。
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：P13D 只证明 native thin backend 的 real live spike readiness packet、operator authorization request、execution receipt hash/scope drift 拦截、ToolCard / registry authorization 和 proof boundary。它不连接 AutoCAD、不调用真实 native plugin、不写真实 CAD、不保存当前 DWG、不写正式图层、不恢复训练、不推进表 C，也不证明 native plugin 可用、`real_cad_readback` 或 `geometry_verified`。真实 native backend live spike 仍未启动；若继续，必须由用户单独确认 scope、CAD_PLAN、`CODEX_PREVIEW`、readback、rollback、no-save guard、backend identity、launch packet hash 与 authorization receipt hash。

## Phase 13E - Native Thin Backend Minimal Live Spike Execution Gate

日期：2026-06-21

状态：checked / closed

触发：
- 用户要求继续 P13，但明确说明不得把“继续推进”当作真实 live spike 授权；真实执行前必须先消费 P13D readiness packet / operatorAuthorizationRequest，并由用户单独确认 scope、CAD_PLAN、`CODEX_PREVIEW`、readback、rollback、no-save guard、backend identity、launch packet hash 与 authorization receipt hash。
- 本轮缺少上述单独 operator 授权与真实 live backend 环境，因此目标收口为 P13E execution gate / missing_authorization / external_blocker closeout 合同；不得连接 AutoCAD、不得调用 native plugin、不得写 CAD。

代码侧收口：
- `core/contracts/native_thin_backend.py` 新增 `native-thin-live-spike-gate/p13e/v1` 合同。
- `build_native_thin_backend_live_spike_execution_gate()` 消费 P13D readiness packet，校验 readiness schema / status、`CODEX_PREVIEW`、CAD_PLAN、readback plan、rollback plan、no-save guard、backend identity、launch packet hash、authorization receipt hash、以及 readiness 不能预授权或冒充 execution / CAD write / plugin invocation / geometry verified。
- operator authorization 必须显式提供 scope、CAD_PLAN、`CODEX_PREVIEW`、readback、rollback、no-save guard、backend identity、launch packet hash 与 authorization receipt hash 确认；缺任一项或 hash 漂移时返回 `blocked / missing_authorization`。
- 授权完整但缺真实 live backend / AutoCAD connection / readback runner / rollback runner / no-save guard / backend identity 环境时返回 `external_blocker`。
- P13E gate 固定 `cadWritesAttempted=false`、`nativePluginInvoked=false`、`executionStarted=false`、`cadGeometryVerified=false`、`savedCurrentDwg=false`；created handles readback、bbox / layer / entity audit、rollback proof、no-save audit 均保持 `not_run_no_execution` / `not_run_no_cad` 边界。
- `P13_NATIVE_ALLOWED_EFFECTS` 增加 `native_thin_live_spike_execution_gate_write` 与 `native_thin_external_blocker_closeout_write`；`native_plugin_execute`、`cad_execute`、`real_cad_readback`、`dwg_save`、`formal_layer_write` 仍为 forbidden effects。
- `core/contracts/cad_agent_harness.py` 的 `native-thin-backend` 支持 `--native-backend-mode live_spike_gate` 与 `--readiness-packet`，仍先走 P11 Adapter Registry / ToolCard / ToolContract 授权。
- `core/contracts/adapter_registry.py` 与 `core/contracts/__init__.py` 同步 P13E evidence boundary 和导出。

新增 / 修改测试：
- `tests/core/test_vnext_contract_adapters.py` 新增 P13E tests，覆盖缺 operator authorization blocked、authorization receipt hash drift blocked、授权完整但缺环境 external_blocker、registry allowed / forbidden effects，以及 harness 不能绕过 ToolCard。
- TDD red run 初始失败于缺 `build_native_thin_backend_live_spike_execution_gate()` 与缺 P13E allowed effects，符合预期。
- Targeted P13E regression：实现后 `tests.core.test_vnext_contract_adapters.P13ENativeThinLiveSpikeGateTests` 运行 4 项，全部 OK。

同步文件：
- 修改 `CORE_RESTRUCTURE_PLAN.md`
- 修改 `CORE_CONTEXT_BRIEF.md`
- 修改 `docs/planning/任务清单.md`
- 修改 `docs/migration/execution-ledger.md`
- 修改 `docs/status/current.md`
- 修改 `docs/handoffs/current.md`
- 修改 `docs/handoffs/package-index.md`

未触碰文件 / 路径：
- `output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/**` 未改写。
- 未新增 `output/**` protected evidence。
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件

能力声明边界：P13E 只证明 native thin backend 的 minimal live spike execution gate、missing_authorization blocker、external_blocker closeout、readiness / authorization hash 漂移拦截、ToolCard / registry authorization 和 proof boundary。它不连接 AutoCAD、不调用真实 native plugin、不写真实 CAD、不保存当前 DWG、不写正式图层、不恢复训练、不推进表 C，也不证明 native plugin 可用、`real_cad_readback` 或 `geometry_verified`。真实 native backend live spike 仍未启动；若继续，必须由用户单独确认 scope、CAD_PLAN、`CODEX_PREVIEW`、readback、rollback、no-save guard、backend identity、launch packet hash 与 authorization receipt hash，并确认真实环境齐备。

## Phase 13F - Native Thin Backend Minimal Real Live Spike

日期：2026-06-21

状态：checked / closed

触发：
- 用户显式授权进入 P13F 最小真实 native backend live spike，确认 scope、CAD_PLAN、`CODEX_PREVIEW-only`、readback plan、rollback plan、no-save guard、backend identity、launch packet hash、authorization receipt hash 和真实 CAD / backend 环境齐备。
- 后续用户要求按主线 MD 未完成项一次性执行；本轮不再停留在 no-CAD 合同叠加，而是实现并尝试真实 scoped native thin backend。

代码侧收口：
- `core/contracts/native_thin_backend.py` 新增 `native-thin-live-spike/p13f/v1` 与 `native-thin-autocad-plugin-result/p13f/v1`，新增 `execute_native_thin_live_spike()`、`run_native_thin_autocad_core_console_spike()` 和 `native_thin_live_spike_evidence_package()`。
- 新增 `P13_NATIVE_LIVE_ALLOWED_EFFECTS`，只允许 `native_thin_scoped_live_spike_execute`、`native_thin_created_handles_readback`、`native_thin_bbox_layer_entity_audit`、`native_thin_rollback_created_handles`、`native_thin_no_save_audit`；`native_plugin_execute`、`plugin_execute`、`cad_execute`、`real_cad_readback`、`dwg_save`、`save_current_dwg`、`formal_layer_write` 仍为 forbidden effects。
- `core/contracts/adapter_registry.py` 新增 `native-thin.live-spike` registered adapter，permission class 为 `cad_preview`，`executes_cad=true`、`reads_dwg=true`、`writes_dwg=true`、`calls_plugin=true`、`saves_dwg=false`、`mutates_registry=false`、`advances_table_c=false`。
- `core/contracts/cad_agent_harness.py` 新增 `native-thin-live-spike` command、`--operator-authorization` 与 `--native-live-environment`，仍先走 P11 Adapter Registry / ToolCard / ToolContract 授权，再调用 live runner。
- 新增 `native_plugins/native_thin_backend/NativeThinBackend.csproj` 与 `NativeThinBackendCommands.cs`。插件命令 `CADAGENT_P13F_SPIKE` 只创建一个 `CODEX_PREVIEW` polyline，读取 created handle / bbox / layer / entity，删除自身创建 handle 作为 rollback proof，并写 JSON report；代码不调用 DWG save。
- 本机没有全局 .NET SDK；本轮安装项目专用 .NET 8 SDK 到 `C:\Users\User\.codex\cad-agent-tools\dotnet-sdk\` 后编译插件。该 SDK 是构建工具，不是训练或 CAD evidence。

新增 / 修改测试：
- `tests/core/test_vnext_contract_adapters.py` 新增 P13F tests，覆盖 live adapter 注册、allowed / forbidden effects、直接合同 proof 裁决、harness 经 registry 路由 live runner、以及 `native_plugin_execute` 越权不能绕过 ToolCard。
- TDD red run 初始失败于缺 `native-thin.live-spike`、缺 `execute_native_thin_live_spike()` 与缺 live runner 符号，符合预期。
- Targeted P13F regression：实现后 `tests.core.test_vnext_contract_adapters.P13FNativeThinLiveSpikeTests` 运行 3 项，全部 OK。
- Targeted adapter regression：实现后 `tests.core.test_vnext_contract_adapters` 运行 39 项，全部 OK。

真实执行证据：
- 首次 Core Console 尝试 `output/validation_runs/phase13f-native-thin-live-spike-20260621-155919/` 因未指定 template / DLL 路径未 quote，收口为 `external_blocker`，`cadWritesAttempted=false`、`nativePluginInvoked=false`、`cadGeometryVerified=false`，不作为成功 CAD proof。
- 修复 runner 后的成功证据为 `output/validation_runs/phase13f-native-thin-live-spike-20260621-160230/`。
- `native_thin_plugin_result.json` 显示 `schemaVersion=native-thin-autocad-plugin-result/p13f/v1`、`status=geometry_verified`、`verificationStatus=verified`、`backend=autocad_plugin`、`targetLayer=CODEX_PREVIEW`、`nativePluginInvoked=true`、`cadWritesAttempted=true`、`savedCurrentDwg=false`、`committedPreview=true`。
- created handle 为 `2CF`；readback entity 为 `LWPOLYLINE`，layer `CODEX_PREVIEW`，bbox min `[100, 200, 0]`，bbox max `[1300, 800, 0]`。
- `bboxLayerEntityAudit.status=verified`、`bboxChecked=true`、`layerChecked=true`、`entityAuditChecked=true`。
- `rollbackRequired=true`、`rollbackStatus=rolled_back`、`rollbackProof.verified=true`、`rolledBackHandles=["2CF"]`。
- `noSaveAudit.status=verified`、`saveAttempted=false`、`saveAllowed=false`、`savedCurrentDwg=false`。
- `native_thin_live_spike_harness_result.json` 经 registry authorization 后同样为 `geometry_verified` / `verified`，`blockingReasons=[]`，`missingEvidence=[]`。

同步文件：
- 修改 `CORE_RESTRUCTURE_PLAN.md`
- 修改 `CORE_CONTEXT_BRIEF.md`
- 修改 `docs/planning/任务清单.md`
- 修改 `docs/migration/execution-ledger.md`
- 修改 `docs/status/current.md`
- 修改 `docs/handoffs/current.md`
- 修改 `docs/handoffs/package-index.md`

未触碰文件 / 路径：
- `output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/**` 未改写。
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何业务 DWG / 大型二进制 CAD 参考文件未保存、未修改。

能力声明边界：P13F 证明最小 scoped native thin backend create/readback/rollback/no-save 闭环。它不恢复训练、不推进表 C、不保存业务 DWG、不写正式图层、不证明生产级 native plugin 体系完成，也不授权扩大对象范围或后续真实 CAD 写入。

## Phase 14 - Engineering Kernel / BIM Minimal DiffPackage

日期：2026-06-21

状态：checked / closed

触发：
- 用户要求按照 `CORE_RESTRUCTURE_PLAN.md` 继续完成未做完的主线；P13F minimal real native thin live spike 已完成后，PlanMD 剩余 gate 为 P14 Engineering Kernel / BIM。
- 本轮目标不是再执行 CAD，也不是扩大 native plugin，而是把任务图、几何图、语义图、版本图和证据图收束为 no-CAD DiffPackage，并接入 ToolCard / Adapter Registry / ToolContract / harness route。

代码侧收口：
- 新增 `core/contracts/engineering_kernel.py`，定义 `engineering-kernel-graphs/p14/v1` 与 `engineering-kernel-diff-package/p14/v1`。
- `build_engineering_kernel_graphs()` 生成 `taskGraph`、`geometryGraph`、`semanticGraph`、`versionGraph`、`evidenceGraph`；默认 `cadWritesAttempted=false`、`nativePluginInvoked=false`、`savedCurrentDwg=false`、`cadGeometryVerified=false`，并明确 `notEvidenceFor` 包含 `real_cad_readback` / `geometry_verified` / 训练 / 表 C / 生产级 BIM export。
- `build_engineering_kernel_diff_package()` 比较 backend evidence / candidate docs，输出 `verifiedBackends`、`notRunBackends`、`geometryDelta`、`styleDelta`、`semanticDelta` 与 `backendCandidateDocs`。
- `core/contracts/adapter_registry.py` 新增 `engineering-kernel.diff-package` registered adapter，permission class 为 `deterministic_verify`；allowed effects 仅为 `engineering_kernel_graph_build`、`engineering_kernel_diff_package_write`、`backend_candidate_profile_write`；`cad_execute`、`native_plugin_execute`、`real_cad_readback`、`dwg_save`、`formal_layer_write`、训练 / 表 C mutation 均为 forbidden effects。
- `core/contracts/cad_agent_harness.py` 新增 `engineering-kernel-diff` command，并要求先走 registry authorization，再生成 P14 no-CAD result。
- `core/contracts/__init__.py` 导出 P14 schema、allowed / forbidden effects、builder 和 evidence helper。

新增 / 修改测试：
- `tests/core/test_vnext_contract_adapters.py` 新增 `P14EngineeringKernelBimTests`。
- TDD red run 初始失败于缺 `core.contracts.engineering_kernel` 与缺 `engineering-kernel.diff-package` 注册，符合预期。
- P14 tests 覆盖 CAD_PLAN graph projection、同一 CAD_PLAN 的 COM / plugin / DXF / geometry kernel / IFC candidate DiffPackage、registry 注册、allowed / forbidden effects、以及 harness 不能绕过 ToolCard。
- Targeted P14 regression：实现后 `tests.core.test_vnext_contract_adapters.P14EngineeringKernelBimTests` 运行 3 项，全部 OK。
- Full adapter regression：实现后 `tests.core.test_vnext_contract_adapters` 运行 42 项，全部 OK。

机器证据：
- 新增 `output/validation_runs/phase14-engineering-kernel-diff-package-20260621-162452/`。
- `phase14_engineering_kernel_closeout.json` 显示 `status=ready`、`verificationStatus=not_verified`、`cadWritesAttempted=false`、`nativePluginInvoked=false`、`savedCurrentDwg=false`、`cadGeometryVerified=false`、`registryRouteStatus=allowed`、`registryAdapterId=engineering-kernel.diff-package`。
- `p13f-source-diff/engineering_kernel_graphs.json` 与 `p13f-source-diff/engineering_kernel_diff_package.json` 消费 P13F native-thin live spike source；`verifiedBackends=["native_thin_live_backend"]`，`notRunBackends=["cad_session_host","dxf_file","geometry_kernel","ifc_bim"]`，`evidenceCompleteness=partial`，`comparisonStatus=complete`。
- `engineering_kernel_harness_result.json` 证明 harness `engineering-kernel-diff` 经 ToolCard / Adapter Registry / ToolContract 授权后生成 no-CAD result。
- 本轮没有改写既有 protected evidence；P13F / P10B 历史 evidence 仅只读引用。

同步文件：
- 修改 `CORE_RESTRUCTURE_PLAN.md`
- 修改 `CORE_CONTEXT_BRIEF.md`
- 修改 `docs/planning/任务清单.md`
- 修改 `docs/migration/execution-ledger.md`
- 修改 `docs/status/current.md`
- 修改 `docs/handoffs/current.md`
- 修改 `docs/handoffs/package-index.md`
- 修改 `AGENTS.md`

未触碰文件 / 路径：
- `output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/**` 未改写。
- `output/validation_runs/phase13f-native-thin-live-spike-20260621-160230/**` 未改写。
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`
- 任何业务 DWG / 大型二进制 CAD 参考文件未保存、未修改。

能力声明边界：P14 证明 Engineering Kernel / BIM minimal DiffPackage、graph projection、candidate backend docs、ToolCard / Adapter Registry / ToolContract 和 harness route 的 no-CAD 闭环。它不执行新 CAD、不连接 AutoCAD、不调用 native plugin、不写 DWG、不保存当前 DWG、不写正式图层、不恢复训练、不推进表 C，也不证明新的 `real_cad_readback`、`geometry_verified`、生产级 IFC / DXF / cloud backend 或多真实 live backend 同一 CAD_PLAN 对比。
