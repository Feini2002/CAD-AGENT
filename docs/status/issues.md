## 2026-06-06 旧能力百分比和探索式架构分片会误导真实训练判断

现象：早期开发阶段形成的表 A / B / C、V-PROOF、RCAD 和“真实 CAD 实力 90%”等口径，在当时用于追踪底座施工、registry 和 evidence 覆盖。但系统后续继续加入 CAD Designer Agent 训练、资产库、A-to-A、多 Agent、GPT-5.5 模型桥、Worker 编排、截图和工作台后，这些旧指标仍停留在主叙事位置，容易让用户误以为系统端到端真实绘图能力已经接近 90%。用户实际感受更接近：底座材料很厚，但真实任务成熟度仍可能只有 5%-10%。

影响：如果继续把旧表 C 当作“真实 CAD 实力”，训练前判断会被高估；系统也会继续在画布上分片加模块，而不是把旧模块归入统一生命周期。这样会导致训练、资产、模型桥、工作台和能力证明并列存在，却不知道谁服务谁、谁不能越过谁。

修复 / 计划：新增 `ARCH-CONVERGENCE-01` 架构归并画布工程。旧表 C 降级为 `Core Proof Coverage`，只表示底座证据覆盖；新增 `Agent Task Maturity` 和 `Project Delivery Readiness` 作为真实训练和交付判断口径。正式对象训练暂缓，先同步 `docs/architecture/system-architecture-convergence.md`、`CORE_RESTRUCTURE_PLAN.md`、`docs/planning/任务清单.md`、规则、状态和 OpenSpec 契约 `openspec/changes/unify-system-architecture-canvas/`。

以后规则：任何模块、脚本、Agent、资产、训练项或工作台显示，都必须能归入七层画布：系统入口、任务对象、决策编排、能力与证据、执行工具、审计修复、沉淀成长。旧表 A/B/C 可以作为历史和底座回归，但不得作为端到端真实 CAD 能力主指标。训练恢复前要完成脚本和派生显示口径审计。

相关文件：`docs/architecture/system-architecture-convergence.md`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_STATUS.md`、`docs/planning/任务清单.md`、`docs/governance/cad-agent-rules.md`、`openspec/changes/unify-system-architecture-canvas/`

## 2026-06-06 本地活体模型桥不能被误解为绕过所有 CAD 证据

现象：用户讨论“Worker / 本地 bridge / Codex CLI / GPT-5.5 / CAD-MCP”时，很容易把三个层级混在一起：一是 Cloudflare Worker 是否已经承载远程触发、状态机、队列和多 Agent 编排；二是 Agent 是否真实调用模型、吃到 prompt 并返回 schema JSON；三是 CAD-MCP 是否已写入 `CODEX_PREVIEW`、是否有 handles readback、是否能交付或进入训练沉淀。

影响：如果把 `modelInvoked=true` 当成 CAD 已验证，系统会再次用模型 pass 替代 validate、dry-run、created handles、bbox / layer / entity audit、visual acceptance、neighbor protection、sourceSpec、reuseReplay 或用户验收。反过来，如果模型因缺 CAD_PLAN / readback / screenshot 证据而返回 `needs_more_evidence` 或 `unavailable`，也可能被误判为“模型没活”，从而掩盖正确的业务阻断。

修复 / 计划：`LOCAL-LIVE-MODEL-BRIDGE-HARDENING-MD-CLOSEOUT-01` 已把独立架构 MD 的剩余路线迁入 `CORE_RESTRUCTURE_PLAN.md` §3.1，并在本地 runtime 加固完成声明分层：`worker_orchestration_ready`、`local_bridge_connected`、`single_agent_live`、`multi_agent_live`、`cad_mcp_preview_live` 和 `formal_training_integrated`。Worker 编排证据必须有 run state、task envelope、队列 / retry、heartbeat 和结果回传；本地活体证据必须有 `modelInvoked=true`、`modelUnavailable=false`、`schemaValid=true`、sanitized `codex.cmd exec --model gpt-5.5` trace、完整 trace 包 diagnostics 和下游 decision；CAD 证据仍按原链路独立验证。

以后规则：Worker 编排只证明任务系统可远程触发和可排队；模型活体调用只证明“Agent 真在思考 / 复审 / 决策”，不证明 CAD 几何、不提升表 C、不等于用户验收。接入 CAD-MCP 前还要确认 Codex 配置不会被 `--ignore-user-config` 连带忽略 MCP；优先使用 bridge-owned Codex config。Worker 是长期编排入口，但不能保存 Codex 登录态、不能直接执行 `codex.cmd`、不能成为任意 shell 代理。

补充规则：Worker 实现不能只跑快乐路径。W1 起必须覆盖 timeout、circuit breaker、retry 上限、dead-letter queue / 等价 DLQ、bridge heartbeat 过期、idempotency、backpressure、kill switch、日志脱敏和 security-blocked 不重试。任何超时、provider unavailable、bridge offline 或 CAD-MCP unavailable 都只能进入可审计状态，不能伪造模型输出或 CAD evidence。

相关文件：`CORE_RESTRUCTURE_PLAN.md`、`core/orchestrator/local_live_model_bridge*.py`、`scripts/diagnose_local_live_model_bridge.py`、`agents/pipeline/README.md`、`docs/architecture/cad-agent-task-chain.md`

## 2026-06-04 A2 局部修复不能全局清理 CODEX_PREVIEW，误删 A1 表格框线

现象：用户只要求修复 `standard_assets.dwg` 的 A2 尺寸 / 文字 / 引线标准区域，但上一轮为了清掉 A2 上的遮挡线框，脚本把整张系统资产 DWG 的 `CODEX_PREVIEW` 实体全局删除。A1 线型 / 图层 / 填充标准表格的框线和行列线当时也在 `CODEX_PREVIEW` 上，因此被误删，导致 A1 原有表格内容只剩文字和样线，缺少表格骨架。

影响：这是局部修复边界错误，会破坏用户未授权修改的区域；也会让“视觉验收通过”产生假阳性，因为 A2 看起来干净了，但 A1 已经损坏。截图非空、A2 变清爽、对象数量回读通过都不能替代分区级回读和未触碰区域保护。

修复 / 计划：`_purge_forbidden_preview_layer_content()` 已改为显式 `scope_bbox` 才能执行；没有范围时返回 `not_run`，常规 layout 只允许把历史 proof 几何迁到 `ASSET_PROOF_CONTENT`，不得全图删除。新增回归测试覆盖“A2 范围内可删、A1 范围外必须保留”和“无范围不执行”。真实 CAD 已在 `standard_assets.dwg` 原位恢复 A1 线型表框线，新增 191 条 `ASSET_PROOF_CONTENT` 表格线，无删除现有实体，报告为 `output/validation_runs/system-assets/asset-library-shelves/a1_linetype_frame_repair_report.json`，截图为 `output/previews/system-asset-a1-restored-a2-cleaned.png`。

以后规则：局部修复必须先锁定目标分区、handles 或 bbox；任何“清理残留 / 删除噪声 / purge preview layer”都不得默认全局执行。若历史资产内容仍在 `CODEX_PREVIEW`，优先做图层归一化而不是删除；只有用户授权且有目标 bbox / handles 时才允许范围内删除。验收必须同时检查目标区和相邻未授权区是否被误伤。

相关文件：`scripts/layout_system_asset_shelves.py`、`tests/core/test_system_asset_sedimentation.py`、`libraries/system_library/drawing_standards/basic/standard_assets.dwg`

## 2026-06-03 系统资产 active evidence refs 不能指向已经缺失的历史产物

现象：仓库治理硬门禁补强后，`run_asset_library_governance_check.py` 正确暴露了系统资产合同 / registry 中仍引用已不存在的历史 evidence 文件，以及 latest shelf layout report 缺失的问题。若继续把这些路径当 active evidence，工作台、治理脚本和人工复审会以为资产证据仍可追溯，但实际已经断链。

影响：资产沉淀可能被误报为 verified / 可复用；A2 仓库排版即使真实 CAD 已重写，也会因为旧证据引用缺失而无法闭合。更危险的是用空 JSON、空截图或派生快照补洞，会把“不可追溯”伪装成“证据存在”。

修复 / 计划：`A2-ASSET-WAREHOUSE-EVIDENCE-CLOSURE-REALCAD-01` 已新增 evidence closure 工具，active refs 只指向本轮存在且可读的 shelf report、聚焦截图和 reuse probe；历史缺失 refs 只能进入归档边界，不再作为 active pass 条件。治理脚本已重新通过，`sediment_system_asset.py --verify --category drawing_standards.basic` 也通过。

以后规则：系统资产证据闭合只能用当前真实报告、CAD readback、截图或 reuse probe 重新闭合；不得创建空文件、派生快照或 sync report 冒充历史证据。闭合报告必须说明哪些历史文件没有重建，以及当前几何证明来自哪一组替代证据。

相关文件：`core/assets/asset_evidence_closure.py`、`scripts/close_system_asset_evidence_refs.py`、`libraries/system_library/drawing_standards/basic/assets.json`、`libraries/system_library/registry.json`、`output/validation_runs/system-assets/evidence-closure/drawing_standards_basic_evidence_closure.json`

## 2026-06-03 A2 仓库证据闭合不等于表 C 历史 coverage 缺口已修复

现象：A2 仓库真实 CAD 修复后，资产库治理与沉淀 verify 已经 pass；但 `scripts/run_data_bloat_audit.py --summary-only` 仍返回 blocked，剩余阻断为 coverage `report_path_missing=303`。

影响：如果把 A2 资产证据闭合和表 C coverage 历史证据缺口混在一起，Agent 可能会误报“全仓证据闭合完成”，或者为了让 audit 变绿而批量伪造 / 空置 303 条历史报告路径。

修复 / 计划：本包只解决 drawing standards basic / A2 仓库这一组系统资产证据链。303 条 coverage 缺口保持 blocked，后续必须单独恢复 / 重跑 Table C 对应证据，或审查后降级不具备证据的 registry claims。

以后规则：完成系统资产仓库治理包时，只能声称资产库证据闭合；不得把 `run_data_bloat_audit.py` 的 coverage 阻断说成已解决。表 C 证据缺口必须走表 C / registry 专项包。

相关文件：`scripts/run_data_bloat_audit.py`、`output/validation_runs/capability-lab/cad_capability_coverage.json`、`CORE_RESTRUCTURE_PLAN.md`

## 2026-06-03 模型辅助输出不能被误当作执行授权

现象：资产守门员和修复 Agent 引入模型能力后，最危险的误用不是“模型判断错”，而是后续链路把模型的分类 / clean source 建议 / repair plan 候选当作已经通过的规则门禁，甚至直接执行删除、保存或正式图层修改。

影响：如果模型建议覆盖 `sourceBoundaryDecision`、CAD readback、reuse probe 或保存边界，系统资产库可能再次把训练污染、whole modelspace、current screen 或 proof panel 当作 clean source；如果 repair plan 候选能直接带 CAD 命令，局部修复会绕开 handles / bbox / layer 证据，破坏用户 DWG 保护规则。

修复 / 计划：`MODEL-BACKED-ASSET-GOVERNOR-REPAIR-P3` 已把两类模型输出固定为只读建议：资产守门员输出 `modelAssistedDecision` 但规则决策不被覆盖；修复模型输出 `modelBackedRepairPlan` / `repairPlanCandidate`，且 `executionPolicy` 必须是 `proposal_only`。schema 和转换器拒绝 `cadCommands`、`executeNow`、`saveCurrentDwg`、`deleteEntities`、`executionAuthorized` 等直接执行字段。

以后规则：模型型 Agent 适合做视觉理解、资产分类和修复计划草案；执行、保存、删除、正式图层、表 C、资产 verified 晋升和用户 DWG 保护仍由规则门禁、CAD readback、精确 handles / bbox 和用户授权决定。任何模型建议如果缺字段、越权或要求 broad scope，都应进入 blocked / manual review，而不是被自动修正后放行。

相关文件：`core/model_review/asset_governor_review.py`、`core/model_review/repair_plan_review.py`、`agents/pipeline/asset_governor/agent.json`、`agents/pipeline/repair/agent.json`、`agents/COMMON_PROMPT_CONTRACT.md`

2026-06-04 补充：`DELETE-SCOPE-NEIGHBOR-PROTECTION-GATE-01` 已新增确定性 `delete_scope_gate.json` / `neighbor_protection.json` 生成器。后续模型给出的 repair / cleanup 建议必须先落到 target handles / scope bbox、victim preview、occupied bbox 和 neighbor diff 这些规则证据上；缺证据仍 blocked。

## 2026-06-03 训练前防膨胀不能绕过证据闭合

现象：`capability-map-data.js` 已经是明显膨胀的派生快照，训练、复训、正式收尾型工作台同步和系统资产沉淀还会持续产生 debug、test artifacts、retry、dry-run、execution summary、旧截图和临时报告。反方复核还指出当前事实源闭合可能已有缺口：若 active `fact_source`、registry evidence 或表 C report path 不可达，直接清理只会把断链包装成健康状态。

影响：如果后续 Agent 只按“output 太大就删”执行，可能误删 still-referenced preview、训练验收报告、created handles/readback 证据、learning ledger、Agent memory、Prompt addendum、系统资产 registry / assets.json / native DWG 或状态 / handoff / issue 中仍引用的路径；如果只压缩 `capability-map-data.js`，也可能让工作台继续显示“已沉淀”但底层事实源不可复盘。

修复 / 计划：本轮已把 `DATA-BLOAT-GOVERNANCE-BEFORE-TRAINING-01` 写入全局规则、A-to-A 任务链路、CAD Designer rules、common prompt contract 和 pipeline manifest，并纳入 `run_doc_governance_audit.py` 的 `data_bloat_governance` 子项。后续真正实现 A 包时，应先做 `data_bloat_audit` / retention dry-run 的 protected / candidate / blocked / derived 报告，再考虑 compact、去重复别名、ratchet threshold 和清理写入。

以后规则：`retention_report.json`、data-bloat audit report、sync report 和 `capability-map-data.js` 只能是 diagnostic / derived，不进入 `training-sources.json` 的 `fact_source`。清理 / 归档写入前必须先证明 active fact source 仍可追溯、候选未被引用、引用根覆盖充分，且不会让 `report_path_missing` 或 registry evidence 断链变差。否则报告 `dataBloatGate=blocked`，不得声称训练收尾或 A-to-A 已打通。仅为查看而刷新工作台快照属于 `workbench_snapshot_refresh`，不能借此宣称正式收尾完成。

相关文件：`AGENTS.md`、`CORE_CONTEXT_BRIEF.md`、`docs/architecture/cad-agent-task-chain.md`、`docs/training/README.md`、`docs/governance/cad-agent-rules.md`、`agents/COMMON_PROMPT_CONTRACT.md`、`agents/pipeline/pipeline_manifest.json`、`core/maintenance/doc_governance.py`

## 2026-06-03 dev volume 审计不能只报原始数量，工作树收口也不能靠误删

现象：仓库当前有大量 tracked / untracked 变更；旧 `run_dev_volume_audit.py` 只报告总数和阈值 findings，无法判断 `105` 个 untracked 是缓存垃圾、派生文件，还是新的源码 / Agent / OpenSpec / 测试包。

影响：如果只看总数，Agent 可能为了“让审计变绿”误删或忽略真实开发产物；如果完全不阻断，大体量工作树又会掩盖本轮改动边界，导致后续提交、review 和回归验证不可控。

修复 / 计划：本轮已让 dev volume audit 输出 `severity_counts`、`blocking_finding_count`、`untracked_by_area`、`untracked_groups`、`tracked_by_area`、`changed_groups`、`tracked_groups`、`by_group_line_delta` 和 top group 摘要，并新增 `--fail-on-severity`、`--summary-only`、`--top-groups`。当前真实审计仍因 `large_changed_file_count` 和 `large_untracked_file_count` 两个 medium finding 阻断；紧凑输出显示 top 收口簇集中在 `tests/core`、`agents/pipeline`、`openspec/changes`、`core/training` 和 `docs/training`，最大 tracked delta 仍是 `capability-map-data.js`。

以后规则：dev volume 中风险阻断不能通过删除未知文件来绕过；日常先跑 `scripts/run_dev_volume_audit.py --summary-only --top-groups 5 --fail-on-severity medium`，再按 top changed / tracked / untracked 分组和 group line delta 判断归属，最后按功能包提交、拆分或明确哪些派生文件可忽略 / 清理。没有用户明确批准，不 stage、提交或删除这些未跟踪文件。

相关文件：`core/maintenance/dev_volume_audit.py`、`scripts/run_dev_volume_audit.py`、`tests/core/test_dev_volume_audit.py`

## 2026-06-03 repo audit 低风险大文件不应和阻断项混在一起

现象：仓库审计曾同时报告 `raw_sys_path_insert` 和大量 `large_python_file`，导致用户看到“22 个维护性问题”时难以判断哪些必须立即修、哪些应登记为低风险治理项。

影响：如果所有 findings 都用同一个失败口径处理，容易在提交前被 low 大文件拖住；反过来如果直接忽略 findings，又会掩盖真正的路径污染、非 UTF-8 或语法错误。

修复 / 计划：本轮已删除 core 模块中的 2 个本地 `sys.path.insert`，并让 `run_repo_audit` 输出 `severity_counts` 与 `blocking_finding_count`；日常阻断使用 `--fail-on-severity medium`。当前剩余 20 个 `large_python_file` 为 low backlog，应后续按模块边界拆分，不作为本轮阻断项。

以后规则：low findings 必须继续留在报告和 issues 中，不能静默忽略；medium/high findings 才阻断普通交付。需要严格收口时仍可使用 `--fail-on-findings`。

## 2026-06-03 A-to-A 编排漏层会让视觉验收能力失效

现象：系统资产 DWG 仓库式排版多轮偏离用户意图时，问题并不是单纯没有视觉验收，而是主 Agent 没有把“仓库 / 货架 / 置物架 / 动线 / 可扩展货位 / 展示形式”这些语义拆成必需 Agent 合同。结果是资产守门员、DWG 编排员和视觉复审之间没有硬性收敛，截图非空、对象数量正确或普通 readback 可能被误当成“布局符合用户隐喻”。

影响：后续系统资产库越大，若没有主合同派发和 hard gate，Agent 可能继续把训练面板、预览卡、索引、资产源和复审区混在一起；即使已有视觉验收工具，也可能因为没被编排调用而形同虚设，削弱检索复用价值。

修复 / 计划：新增 `A-TO-A-TASK-CONTRACT-GATE-01`。主编排入口生成 `a_to_a_task_contract`，列出 `requiredAgents`、`hardGates`、`missingRequiredAgents` 和 `failedHardGates`；系统资产沉淀固定要求资产守门员、资产馆员、资产 DWG 编排员和复用审计员；系统资产 DWG 视觉布局任务还必须要求 `pipeline_visual_layout_reviewer`。缺任一必需输出时，`workflow_dispatch` 用 `a-to-a hard gate` 阻断。

以后规则：不要把“视觉验收已经存在”当成任务已验收；必须检查它是否在本次 `TaskContract` 中被列为 required agent / hard gate。截图、非空像素、实体数量和普通 readback 都只能是辅助证据，不能替代 `visual_layout_review`。

相关文件：`core/orchestrator/a_to_a_task_contract.py`、`core/orchestrator/workflow_dispatch.py`、`agents/pipeline/visual_layout_reviewer/agent.json`、`agents/pipeline/pipeline_manifest.json`、`scripts/run_a_to_a_orchestration_gate_check.py`、`docs/architecture/cad-agent-task-chain.md`

## 2026-06-03 系统资产 DWG 被训练内容污染会削弱检索复用

现象：训练完成后执行“沉淀”时，如果把训练面板、训练标题、临时说明、边框、尺寸线、截图说明或证据路径原封不动搬进系统资产 DWG，资产库会越来越像杂乱训练画布，而不是可检索、可复用、可人工复审的通用底座。

影响：未来检索可能命中一个“资产”，但实际复制源夹杂训练说明或不该复制的对象；复用时可能带入错误文字、边框或尺寸线；人工复审也难以判断哪些对象是可复用源、哪些只是证据。

修复 / 计划：新增 `SYSTEM-ASSET-LIBRARY-GOVERNANCE-01`。沉淀先过 `pipeline_asset_governor`；守门员派发资产馆员、资产 DWG 编排员和复用审计员；`native.layoutPlan` 升级为 v2，系统资产 DWG 分为 `00_INDEX`、`01_CLEAN_ASSETS`、`02_PREVIEW_CARDS`、`03_REVIEW_QUARANTINE` 和 `99_EVIDENCE_LINKS`。来源不清时进入 metadata-only / quarantine；clean source 只接受精确来源或 style definition。

以后规则：不得把整块 `CODEX_PREVIEW`、训练面板、当前屏幕、全模型空间或全部可见对象当成资产源。训练标题、临时说明、边框、尺寸线、审计文字和证据路径默认只进入 JSON 证据、资产卡或 evidence links，不得进入 `01_CLEAN_ASSETS`。守门员收尾必须输出 `polishHardeningDecision`，明确是否还需 native CAD relayout、reuse replay 或 source boundary review。

相关文件：`agents/pipeline/asset_governor/agent.json`、`core/assets/system_asset_library_governance.py`、`core/assets/system_asset_sedimentation.py`、`docs/architecture/system-asset-sedimentation-protocol.md`、`tests/core/test_system_asset_sedimentation.py`

2026-06-03 补充落地：`SYSTEM-ASSET-DWG-SHELVES-R1` 已把 `libraries/system_library/drawing_standards/basic/standard_assets.dwg` 直接改造成可视货架：`00_INDEX`、`01_CLEAN_ASSETS`、`02_PREVIEW_CARDS`、`03_REVIEW_QUARANTINE`、`99_EVIDENCE_LINKS`、`EXPANSION_BAY_A` 和动线箭头已经写入并保存。脚本默认只按上一份货架报告中的 handles 清理旧脚手架，只有显式 `--clear-all-shelf-layers` 才做全层清理；同时刷新 `assets.json` / `registry.json` 的 v2 货位元数据，并记录“货架脚手架已写入，不等于资产源几何已迁入”的 `nativeWriteBoundary`。证据为 `output/validation_runs/system-assets/asset-library-shelves/shelf_layout_report.json` 与 `output/previews/system-asset-library-shelves-r1.png`。

2026-06-03 二次修正：用户指出 R1/R2 仍然把现有线型表和尺寸样式面板留在中间，左侧小预留格既装不下资产，也没有形成“内容一一对应放入货架”的仓库感。`SYSTEM-ASSET-DWG-CLASSIFIED-RACKS-R3` 已改为让现有内容本身进入 `A 通用底座脚手架`：`A02_LINETYPE` 框住线型表，`A03_DIMENSION_STYLE` 框住尺寸样式面板，底部才放 A 类后续底座预留槽；右侧单独保留 B 类对象图块货架。后续同类修正不得只画小占位框，必须先判断已存在资产内容的 bbox 和类别，让大货架围绕实际内容排版。

2026-06-03 三次修正：Agent 复核发现 R3 仍容易把 `drawing_standards.basic` 这张 DWG 理解成“所有对象资产都能放进来的总仓”，这会让床铺、桌子、沙发等对象 block 本体和绘图标准混库。`SYSTEM-ASSET-DWG-THREE-COLUMN-WAREHOUSE-R4` 已改为三列仓库：`A1` 放线型 / 图层 / 填充标准，`A2` 放尺寸 / 文字 / 引线标准，`B` 只放对象资产索引和跨库入口；对象真实 block 后续进入各自分类 DWG。后续同类布局必须先判断当前资产 DWG 的分类职责：本分类能放 clean source，跨分类只能放 index-only 链接，不得为了视觉“货架很多”而把别的类别实体搬进来。

2026-06-03 四次修正：用户指出 R4/R5 的问题本质不是“有没有写 CAD”，而是验收把“脚本写通 + 元数据没坏 + 截图有框”误当成仓库架构过关。现已新增 `audit_visual_rack_plan()` 和 governance check 联动，弱 `visualRackPlan` 会因缺 v2 架构、acceptance criteria、rack ownership、copy policy、扩展空位或 zone bbox 比例 fail；`scripts/layout_system_asset_shelves.py` 写入前先审 plan，写入后必须回读本轮 created handles 的图层和 bbox。证据为 `output/validation_runs/system-assets/asset-library-shelves/shelf_layout_report.json`（209/209 handles resolved、unmanaged layers 0、primaryWarehouseAreaRatio=0.8694）、`output/validation_runs/system-assets/library-governance/final_hardening_decision.json` 和 `output/previews/system-asset-library-shelves-r2.png`。后续同类验收不得只看分区文字或截图，必须同时看视觉仓库审计与实体回读。

## 2026-06-03 训练截图只靠规则会继续堆积

现象：训练期规则已经要求收尾后只长期保留最终验收报告、队列状态、learning ledger / Agent memory / Prompt addendum 和最近一份人工复核预览图，但实际入口缺少统一执行器，`output/previews`、`output/training_queues` 和历史验证目录里的 PNG/JPG 容易继续堆积。

影响：旧截图会占用磁盘，也可能被后续 Agent 或人工复盘误当成最新训练证据；如果直接人工删除，又可能删掉仍被最终报告、工作台数据、learning ledger 或 `training-errors.md` 引用的证据。

修复 / 计划：新增 `TRAINING-ARTIFACT-RETENTION-01`。`scripts/run_training_artifact_retention.py` 默认 dry-run，引用感知地列出保留项和归档计划；训练队列 pass 后写入 `postTrainingArtifactRetention`。只有显式 `--write` / `--artifact-retention-write` 时才把未引用旧图移入 `archive/training_artifacts/`，不做不可逆删除。

以后规则：清理训练截图前先看 retention report；被引用的截图和每个目录最新人工复核预览图不得清理。旧截图清理不能替代失败根因沉淀，删除或归档前必须确认教训已经进入 `training-errors.md`、learning promotion 或对应规则。

相关文件：`core/training/artifact_retention.py`、`scripts/run_training_artifact_retention.py`、`scripts/run_training_queue.py`、`scripts/run_cad_foundation_remaining_training.py`、`tests/core/test_training_artifact_retention.py`

## 2026-06-03 CAD 链路修复只跑单测就交付会掩盖未运行

现象：截图、runner、训练、验证等 CAD 链路修复完成后，如果只跑单元测试和 OpenSpec 校验，再在最终回复里写“未运行真实 CAD”作为边界，用户仍会拿到一个没有实际链路复验的修复交付。

影响：这会让“代码看起来已修”与“当前 AutoCAD 会话真的能跑”脱节；尤其是截图、后台窗口、局部修复聚焦、COM 权限、活动 DWG、created handles 回读等问题，单元测试无法证明用户当下环境已经可用。

修复 / 计划：新增 `REPAIR-RUN-BEFORE-DELIVERY-01`。所有修复默认运行覆盖原问题的最小实际链路后再交付；CAD 落图、截图、训练、runner、验证、资产复用 / 沉淀或局部修复链路改动，除单元测试外还必须补一条代表性实际链路。真实 CAD / GUI / COM 不可用时先按 blocker 自救并必要时申请外部执行，仍不可用则只能报 `blocked` / `not_run` / `not_verified`。

以后规则：不得把“已说明未运行真实 CAD”当成 CAD 链路修复完成。影响截图功能的修复至少跑 `scripts/render_preview.py --check`，AutoCAD 可用时还要跑 `scripts/render_preview.py --capture-autocad-window`；影响落图 / 训练 / 复用的修复要跑对应代表性 runner，并保留 created handles / readback / audit 或截图证据。

相关文件：`AGENTS.md`、`CORE_CONTEXT_BRIEF.md`、`docs/governance/cad-agent-rules.md`、`docs/status/current.md`、`docs/status/changelog.md`

## 2026-06-03 截图按当前视图或整批 handles 会掩盖局部修复目标

现象：AutoCAD 在后台、被 IDE 遮挡或当前视图停留在大 DWG 全局区域时，截图可能看不到本次测试对象；如果一轮测试包含 10 个内容但只局部修复 1 个，按整批 `execution_summary.created_handles` 或当前 CAD 视图截图会把复核范围放大，用户无法确认修复对象本身是否正确。

影响：截图会变成低信号证据，甚至误导 Agent 认为“画面里有对象”就完成；句柄解析失败时若静默 `ZoomExtents`，海量无关图块会重新进入截图，掩盖目标对象。局部修复还可能因为缺少目标 handles / bbox 而回到整块重画或整批复核。

修复 / 计划：新增 `TASK-SCOPED-CAD-PREVIEW-CAPTURE-01`。`render_preview` 支持 `target_handles`、`repair_plan.target_handles`、`repair_plan.target_bbox`、显式 `target_bbox`、`execution_summary.created_handles` 的优先级聚焦；`AutoCADComDriver.zoom_to_handles_extents()` 目标不可用时返回 `focus_target_unavailable`，不再静默全图。第一批已接入视觉复核、跨机器复验和基础训练主入口，并写入结构化 `visualPreview`。

以后规则：局部修复、单项复验或“10 项里修 1 项”的截图必须优先传本次修复对象的 handles 或 bbox；只有没有局部目标时才使用整批 execution summary。截图仍是 `visual_aid_only`，不能替代 created handles / readback / audit。

相关文件：`core/verification/render_preview.py`、`core/cad_io/autocad_com.py`、`core/verification/visual_cad_review.py`、`core/verification/cross_machine_reverify.py`、`core/training/foundation_batch_training.py`、`openspec/changes/task-scoped-cad-preview-capture/`

## 2026-06-02 训练后沉淀靠人工确认容易漏同步

现象：训练、复训或纠错完成后，系统可能已经能画出来，也可能已经通过用户反馈或机器验收，但仍要人工再三追问：是否登记训练事实源、是否刷新 HTML 工作台、是否同步 Agent memory / Prompt、是否要写规则、是否要新增检查器、是否回测原任务。

影响：若只靠对话记忆，后续 Agent 可能漏写规则或校准；也可能反过来过度沉淀，把 quick trial、截图推断、未知能力或一次性案例反馈写成全局规则。训练工作台也可能显示“已沉淀”，但缺少机器可读的沉淀决策边界。

修复 / 计划：新增 `CAD-TRAINING-PROMOTION-GATE-01`。正式训练 promotion 必须写 `promotionGate`，声明 `updateTrainingSource`、`updateWorkbench`、`updateAgentCalibration`、`updateBaseRules`、`updateTaskRules`、`updateChecker`、`retestOriginalTask` 七项决策；工作台 Agent check 会拒绝缺 gate 的 systemized 训练。`quick_trial` 只保留 `observation`，未知 `capabilityId` 不再 fallback 到 `cad_designer`，规则 / 检查器 delta 只能进入 `needs_reviewed_package`。

以后规则：训练收尾若没有 `promotionGate`，不得声称“已沉淀到系统”；gate 标出 `needs_reviewed_package` 时，不得把候选规则说成已写入底座；gate 标出 `retestOriginalTask.required=true` 时，必须补原任务回测证据后才可说根源修复闭环完成。

相关文件：`core/training/promotion_gate.py`、`core/training/learning_promotion.py`、`scripts/sync_training_workbench.py`、`scripts/run_training_workbench_agent_check.py`、`docs/architecture/cad-agent-task-chain.md`、`docs/training/README.md`

## 2026-06-02 执行闭环和训练闭环割裂

现象：系统已经有训练期闭环，也逐步形成资产复用、局部修复、线型表审计等执行能力，但如果只记录其中一条，Agent 后续可能出现两类偏差：只把白话拆成可执行任务却不把失败回流训练；或只说某项训练通过，却没有同步到主系统分发、单一任务规则和责任 Agent 校准。

影响：复杂任务会在“执行成功一次”和“训练通过一次”之间断开。失败经验可能停留在对话或单个报告里，后续 Intent / Asset / Execute / Audit / Repair / Delivery Agent 仍按旧规则行动；资产库、检查器和工作台也可能不同步。

修复 / 计划：新增 `CAD-AGENT-TASK-CHAIN-01`，在 `docs/architecture/cad-agent-task-chain.md` 统一记录系统任务链路：白话输入先分流和语义拆分，再拆成单一子任务并分发执行；稳定失败或新能力再回流到训练 / 复训、原任务回测、底座规则、单一任务规则、检查器、Prompt / memory、A-to-A 校准和事实源同步。

以后规则：根源修复不能只问“要不要训练”，还要问“执行分发是否会用到新规则”；训练通过也不能只问“报告是否 pass”，还要问“主系统、单一任务规则、责任 Agent 和事实源是否已经同步”。若未同步，最终回复必须标为 partial / not_checked。

相关文件：`CORE_CONTEXT_BRIEF.md`、`docs/architecture/cad-agent-task-chain.md`、`docs/training/README.md`、`docs/training/global-agent-pipeline.md`、`docs/governance/cad-agent-rules.md`

## 2026-06-02 中文编码损坏不能靠截图后修复

现象：通用资产 DWG 沉淀第一步曾因中文工作区路径或中文 payload 经 Windows 控制台 / 管道后变成乱码，后续虽然能通过截图或 readback 发现并重画，但这已经允许错误进入 CAD 执行链路。

影响：如果中文资产名、用途、标注或路径在打开 / 写入 DWG 前已经损坏，后续截图自检只是补救；更危险的是伪中文 mojibake 仍是 CJK 字符，可能绕过“是否中文”的粗浅检查，沉淀进资产合同或原生 DWG。

修复 / 计划：新增 `UTF8-FIRST-CAD-ASSET-GUARD-01`。脚本入口强制 UTF-8 运行环境；系统资产沉淀入口写合同前运行 `encodingPreflight`；线型表绘制前验证 visible text；检测到 `??`、`�` 或典型 mojibake 时直接阻断，不写 CAD、不保存 DWG、不生成资产合同。

以后规则：CAD 写入和系统资产沉淀不得依赖 PowerShell stdin / heredoc 传中文 payload；优先使用 UTF-8 源文件、模块常量或 UTF-8 JSON 文件。编码损坏必须在第一步失败，不得把“截图发现后修复”当成正常链路。

相关文件：`scripts/_bootstrap.py`、`core/runtime/encoding_guard.py`、`core/assets/system_asset_sedimentation.py`、`core/training/linetype_table_demo.py`、`tests/core/test_script_bootstrap.py`、`tests/core/test_system_asset_sedimentation.py`、`tests/core/test_linetype_table_demo.py`

## 2026-06-02 已沉淀资产可能被绕过而临场重画

现象：用户未来可能说“从 XX 资产调用 XX 放到当前 DWG”，也可能只说“放一个线型表 / 沙发 / 符号 / 标准样式到当前图”。如果 Agent 不先查系统资产库，就会重新生成一份相似内容，绕过已沉淀资产的合同、来源边界和验证证据。

影响：资产库虽已沉淀但无法真正复用；同一对象或标准会出现多份不一致实现，后续反馈也不能回流到资产合同。更危险的是，临时重画可能绕过 `includedHandles`、blockName、style source 和 anti-contamination 规则，把不该复制的内容带入当前图。

修复 / 计划：新增 `SYSTEM-ASSET-REUSE-INSERT-01`。当用户说“调用 / 复用 / 插入 / 套用 / 放到当前 DWG”，或语义明显匹配系统资产时，先读 `libraries/system_library/registry.json`，通过 `core.assets.system_asset_reuse` 生成复用计划，再由 `scripts/reuse_system_asset.py` 或等价入口写入当前 DWG 的 `CODEX_PREVIEW`。真实 CAD 烟测已证明 `linetype_style_summary_table` 可从 `standard_assets.dwg` 跨 DWG 复用到新的当前 DWG，450/450 handles 回读。

2026-06-02 补充：单资产复用不足以覆盖未来资产库。已新增 `SYSTEM-ASSET-REUSE-WORKFLOW-01`，把复用底座升级为 `system_asset_reuse_workflow`：支持显式 / 隐式触发、候选排序、多资产拆分、`partial` 阻断、精确来源门禁和 workflow 写入回读；没有资产信号时返回 `not_asset_reuse_request`，再交回普通绘图链路。

2026-06-02 CAD-native 补验：用户已打开 AutoCAD 时，普通沙箱下 COM 仍可能报 “No active AutoCAD.Application instance”，但提权执行同一复用命令可连接并完成真实跨 DWG 复制。以后遇到 CAD 进程存在但 `GetActiveObject` 失败，不要立刻判断 CAD 未打开；先按 GUI/COM 权限边界申请外部执行，再看是否仍失败。补验证据：`output/validation_runs/system-assets/cad-native-hardening/reuse_workflow_real.json`，450/450 handles 回读，`savedCurrentDwg=false`。

以后规则：匹配到资产但来源不足时返回 `needs_precise_native_source`，不得从 whole_modelspace、current_screen、all_visible 或训练面板硬拷贝。复用当前业务 DWG 默认不保存，必须报告 matched asset、source spec、target layer、created handles、readback count 和 `savedCurrentDwg=false`。

相关文件：`core/assets/system_asset_reuse.py`、`scripts/reuse_system_asset.py`、`core/cad_io/autocad_com.py`、`tests/core/test_system_asset_reuse.py`、`libraries/system_library/registry.json`、`docs/architecture/system-asset-reuse-workflow.md`

## 2026-06-02 系统资产 DWG 写入后未强制保存和打开会削弱人工复审

现象：系统资产沉淀可能完成合同登记和 CAD 写入，但如果 Agent 没有把“沉淀资产”理解为对应系统资产 DWG 的保存 / 打开授权，就可能停在“内容已写入但 DWG 未保存”或“截图已生成但用户没有看到资产库 DWG”的状态。

影响：资产合同、截图和 AutoCAD 当前文件状态可能漂移；后续复用时以为原生资产已稳定落盘，实际用户尚未在对应 `*_assets.dwg` 中复审。对于文字样式、线型表、block 定义这类原生 DWG 内容，未保存或未打开复审会让问题延迟到下一次调用才暴露。

修复 / 计划：新增 `SYSTEM-ASSET-NATIVE-SAVE-REVIEW-01`。用户说“沉淀 XX 资产 / 通用资产 / 收进资产库”时，默认授权 Codex 对对应系统资产 DWG 执行必要的创建、打开 / 激活、写入和保存；只要本轮向该 DWG 添加、替换或修复了原生 CAD 内容，就必须保存并回读活动文档路径、`Saved=true` 和关键实体 / 样式证据。沉淀收尾默认打开 / 激活对应 DWG 供用户人工复审。

以后规则：保存权限只覆盖 `libraries/system_library/**/**/*_assets.dwg` 或资产合同解析出的 `nativeDwg`，不覆盖用户当前业务 DWG、原始图纸、正式图层、全模型空间清理或非系统资产文件的保存 / 覆盖。来源不足或没有生成 DWG 时，只能登记合同并说明未打开原因。

相关文件：`AGENTS.md`、`CORE_CONTEXT_BRIEF.md`、`docs/architecture/system-asset-sedimentation-protocol.md`、`docs/governance/cad-agent-rules.md`、`docs/status/current.md`、`docs/status/changelog.md`

## 2026-06-02 表格类 CAD 产物缺少布局审计导致视觉问题复发

现象：线型归纳表出现用户不需要的实心填充残留；标题区排版压迫感较强；分组标题行仍被内部竖线切割；左侧中文序号在测试表中不如阿拉伯数字清晰。后续扩展到 42 行时，又因过保守的 24 行分页策略把表拆到旁边；`开启范围线` 圆弧样例按固定半径和偏移绘制，越过本行样例格压到下一行。

影响：表格虽然“内容都在”，但视觉上不像可交付 CAD 标准表；分组标题被切割会让用户误判结构；硬分页会把用户要求的同一张归纳表割裂成多块；样例越格会让线型语义看起来像画错对象。若报告只记录 created handle 数量而不记录句柄，后续局部修复和截图聚焦会退回 bbox 猜测，增加误删或误聚焦风险。

修复 / 计划：线型表生成器改为显式布局策略：不使用填充 / 遮罩，标题区合并，分组行合并，普通数据行才绘制分段竖线，序号使用阿拉伯数字。扩展表使用单外框整合双栏，不把 24 行当限制；行高策略改为 `adaptive_min_height`，复合样例按 `sampleCellBbox` 自适应半径、振幅和边距。报告新增 `layoutPolicy`、`layoutChecks`、`rowHandles` 和 `created_handles`，并用测试固定 `solidFillEntityCount=0`、`groupRowVerticalSegmentCount=0`、`rowNumberStyle=arabic`、`sampleOutOfCellCount=0`。

以后规则：表格类 CAD 产物不能只验证文字和句柄数量，还要验证至少一组布局语义：标题 / 分组是否合并、内部竖线是否穿越分组、是否使用不必要填充或遮罩、序号和列宽是否符合阅读习惯、样例是否完全落入自己的单元格。不得把任意行数上限当成 CAD 限制；需要分页、双栏、折叠分组、缩放或可变行高时，应先按内容密度选择整合方式。需要清理旧版本时优先按 `created_handles`，没有句柄时才退回严格 bbox，且不得用宽松 overlap 扩大删除范围。

相关文件：`core/training/linetype_table_demo.py`、`scripts/draw_linetype_table.py`、`tests/core/test_linetype_table_demo.py`、`output/validation_runs/linetype-table/integrated-real/linetype_table_report.json`

## 2026-06-02 局部错误被旁边整套重画放大

现象：回测或 Agent 自检已经能发现局部错误，例如训练面板文字出现问号乱码、局部线型 / hatch / 标注不对，但修复时可能在旁边重新画完整测试内容，而不是删改原位置的错误对象。

影响：旧错误仍留在原位，画布噪声持续增加；用户需要比较多份相似图块才能判断哪份是最新；Agent 也会训练成“重新生成一份”而不是“编辑已有 CAD 图纸”，不符合真实 CAD 工作方式。

修复 / 计划：新增“原位局部修复优先”规则。后续反馈 fail 或审计局部失败时，先读取 `execution_summary`、created handles、当前 CAD readback 和截图证据，生成 `repair_plan`，按 `target_handles` / `target_bbox` 执行 `update`、`delete_replace` 或 `add_missing`；删除权限默认只作用于 `CODEX_PREVIEW` 中被证据锁定的错误对象。

以后规则：不得因为局部乱码、缺线、错线型、错 hatch 或局部标注问题就在旁边整套重画。只有 handles 失效、对象被炸开 / 删除、局部修复会破坏整体拓扑，或根因来自全局坐标系 / 比例 / 布局时，才允许整块重画；重画前必须说明局部修复为什么不可行。

相关文件：`AGENTS.md`、`docs/governance/cad-agent-rules.md`、`docs/runbooks/blocker-playbook.md`、`docs/training/README.md`、`docs/training/pipeline-changelog.md`

## 2026-06-02 Prompt addendum 重复沉淀导致合同漂移

现象：多个责任智能体的 `prompt_addendum.md` 同时包含“中文标注”“只写 CODEX_PREVIEW”“回读 created handles”等通用规则。短期看是强化记忆，长期会变成多处分叉：某个 Agent 更新了规则，另一个 Agent 仍保留旧句子。

影响：Prompt 看起来越来越厚，主 Agent 与分支 Agent 的职责边界会被重复文本模糊；训练工作台也可能把重复 addendum 当成多个不同来源，增加维护噪声。

修复 / 计划：新增 `agents/COMMON_PROMPT_CONTRACT.md` 作为通用 Prompt 合同；learning promotion 生成 addendum 时只写角色专属新增；Agent check 新增共享合同引用和通用规则去重检查，`duplicates=[]` 才允许通过。

以后规则：通用 CAD 安全、证据和视觉反馈规则只在共享合同维护；`training_memory.json` 可以保留完整历史经验，`prompt_addendum.md` 不再复制共享句子。

相关文件：`agents/COMMON_PROMPT_CONTRACT.md`、`core/training/learning_promotion.py`、`scripts/build_capability_map_data.py`、`scripts/run_training_workbench_agent_check.py`

## 2026-06-02 系统资产沉淀可能被误读为能力已提升

现象：用户说“沉淀 XX 资产”后，如果只生成 `assets.json`、registry 或预留 DWG 路径，Agent 可能把“已登记”误报为“已稳定复用”或“原生 DWG 已沉淀”；如果对象来源边界不清，还可能把整个 `CODEX_PREVIEW`、训练面板、文字说明、边框、尺寸线或其它无关实体一起误打成 block。

影响：资产库会越来越有秩序，但底座能力不一定真的提升；更糟的是，未验证资产或被污染的 block 可能被后续任务优先调用，造成尺寸、方向、blockName、样式或无关对象随块扩散。

修复 / 计划：系统资产协议 V3 已加 `candidate/systemized/verified/deprecated` 状态流、`retrieval`、`native.layoutPlan`、`versioning`、`verification`、`feedbackLoop`、`exportManifest` 和 `antiContamination`。`scripts/sediment_system_asset.py --verify` 只做元数据验收；对象 block export 必须有精确来源边界，原生几何复用必须等 native DWG export / CAD insertion replay / readback 证据补齐后才可升为 `verified`。

以后规则：沉淀命令默认提升资产秩序，不自动提升真实 CAD 能力。最终回复必须说明状态、导出模式、来源边界和 `notChecked` 边界；来源不清时只能 `metadata_only`，不得 block export。重复 asset id 且尺寸 / blockName 冲突时必须选择更新、拒绝或生成变体，不得静默覆盖。

相关文件：`core/assets/system_asset_sedimentation.py`、`scripts/sediment_system_asset.py`、`docs/architecture/system-asset-sedimentation-protocol.md`、`libraries/system_library/registry.json`

## 2026-06-02 “旁边”被误解成全局远处空白

现象：用户说“在旁边画个……”时，真实意思往往是当前眼睛看到的 CAD 视口附近；旧链路可能按全图 bbox、训练停放区或全局最右侧空白理解，导致新内容需要移动视角才看得到。

影响：Agent 看起来会执行命令，但不像设计师在电脑前工作；用户的空间语义被坐标算法带偏，临时测试内容也可能离当前关注对象太远。

修复 / 计划：新增 designer-view nearby placement：先采集 `CAD_VIEW_CONTEXT`，选择 `focus_anchor`，生成当前视口内候选槽位，再收口为确定 `CAD_PLAN` base point；审计用原始视口和 created handles/bbox 回读，禁止靠后续 zoom/pan 证明“旁边”。

以后规则：遇到“旁边 / 附近 / 边上 / 右边 / 上方”时，不得从白话直接跳绝对点，也不得画到全局远处；读不到视口、锚点或回读证据时应 `blocked` / `needs_confirmation`。成功只证明当前视域邻近放置，不证明对象族能力或表 C 提升。

2026-06-02 复发补充：本轮用户说“在旁边画个沙发”时，Agent 已经有 `designer_view_nearby` 专用链路，却手写脚本读取全局 `CODEX_PREVIEW` bbox 的右侧作为锚点，结果画到当前左上视觉焦点很远的位置。根因是执行入口绕过：规则和 Core 能力存在，但 quick trial 没有把“邻近词 -> 当前视口链路”当成硬门。

补充规则：含“旁边 / 附近 / 边上 / 右边 / 左边 / 上方 / 下方”的真实 CAD 小动作，必须优先调用 `core.placement.designer_view_nearby` 或等价的 `CAD_VIEW_CONTEXT -> focus_anchor -> placement_resolution` 证据链；不得用临时脚本、全局 bbox、全模型空间 bbox、历史停放区或后续 zoom/pan 绕过。若当前视口里有多个焦点且没有 selected / recent handles，应 `needs_confirmation`，而不是选择离全局空白最近的点。

2026-06-02 提速补充：为避免每次临场重新找 helper / 手写脚本，新增 `core.quick_tasks.nearby_draw` 和 `scripts/run_quick_nearby_draw.py`。后续“旁边快画”默认走该入口；它只做当前视口解析、轻量符号绘制、created handles/bbox 回读和 timing 汇报，默认不写完整 CAD_PLAN / dry-run / 截图 / 工作台同步。

2026-06-02 视觉限定补充：用户进一步指出“旁边”只是语言形式之一；有时会给截图说“在图片这里画”，有时不截图但说“旁边”，本质都是希望 Agent 按用户当前视觉焦点操作。已把 `core.quick_tasks.nearby_draw` 加固为 `input_scope` 入口：识别截图 / 图片 / 这里 / 看到 / 旁边 / 附近 / 方向词等视觉限定请求，记录视觉来源和锚点策略；截图只作视觉目标提示，不能替代 CAD 坐标、尺寸或 created handles 证据。没有当前视口、截图像素无法映射、焦点不唯一或没有 selected / recent handles 时必须 `blocked` / `needs_confirmation`，不得硬猜。

相关文件：`core/placement/designer_view_nearby.py`、`core/quick_tasks/nearby_draw.py`、`scripts/run_quick_nearby_draw.py`、`scripts/run_designer_view_nearby_smoke.py`、`agents/cad_designer/rules.md`、`openspec/changes/define-designer-view-nearby-placement/`

## 2026-06-01 小动作被完整训练闭环拖慢

现象：用户只是要求训练 CAD 某个计划里的一个很小动作，例如“画个正方体 + 填充”，理论上几秒即可完成；实际执行时却触发了完整训练链路，包括 plan / dry-run、真实 CAD、回读、截图、自检、报告、同步和沉淀等大量工序。

影响：轻量试画被放大为正式验收任务，用户等待时间和画布噪声上升；Agent 也容易把“临时看一下”和“训练通过并沉淀”混为一谈，降低训练迭代速度。

修复 / 计划：新增训练轻重链路量化路由：`quick_trial` ≤ 2 分钟，只写 `CODEX_PREVIEW`，最多 1 次 CAD 写入 + 1 次关键回读；`focused_retraining` ≤ 8 分钟，只覆盖点名能力或显式列表；`formal_acceptance` 才走完整训练闭环。快试若需要修改已有实体、超过 20 个新对象、碰正式图层 / 保存 / 删除、关键回读失败或用户要求正式准确性，才升级。

以后规则：默认使用最轻可证明链路。用户说“试一下 / 快画 / 小动作 / 先看看 / 先别沉淀 / 不进训练 / 只画这个”时，不跑截图、工作台同步、learning promotion 或 coverage；最终回复必须说明“快试未沉淀”。只有用户明确“验收 / 沉淀 / 训练通过 / 记入工作台 / 整批 / 全部 / 刷新队列 / 推进表 C”时，才执行完整链路。

相关文件：`AGENTS.md`、`docs/training/README.md`、`docs/governance/cad-agent-rules.md`、`agents/cad_designer/rules.md`、`docs/training/pipeline-changelog.md`

## 2026-06-01 复合任务可能让训练计划无限膨胀

现象：用户未来可能把多个已有能力临场组合，例如截图识别沙发、再对该沙发标注尺寸。这类组合可能没有出现在 V2 训练地图中。

影响：如果要求每个组合都预先写成训练项，训练计划会无限膨胀；如果完全不设规则，Agent 可能因为“计划里没有”而拒绝，或把截图推断尺寸误报为真实 CAD readback。

修复 / 计划：新增 `COMPOSITE-TASK-ROUTING-01` 规则链路：复合任务默认拆成已有能力节点动态编排，先声明输入来源和 `evidence_source`，再走结构化意图 / `CAD_PLAN`、validate、dry-run、`CODEX_PREVIEW`、readback 和 audit。单次组合只进入案例反馈或训练错误记录；重复失败、可机器检查或可泛化为课程族时才晋升训练项、benchmark、检查器或规则包。

以后规则：训练地图只列原子能力和代表性课程，不穷举排列组合。截图、参考图和比例估算只能作为视觉 / 推断证据，不能替代 created handles、DWG 回读、原 `CAD_PLAN` 或用户明确尺寸。

相关文件：`AGENTS.md`、`docs/training/README.md`、`agents/cad_designer/rules.md`、`docs/training/cad-designer-growth-path.md`、`docs/governance/cad-agent-rules.md`

## 2026-06-01 图片箭头语义定位被停放区逻辑带偏

现象：用户截图要求在第 12 项面板上方箭头 / 蓝圈处测试全填充，实际先按 focused retraining 在右侧另起模块；随后又用旧 execution summary 坐标画了一个实心方块，仍落在右侧模块附近。

影响：Agent 把“训练停放区规则”和“旧机器坐标”当成目标，忽略了用户截图里的空间语义；这会让图像反馈类任务偏离用户真正指的位置。

修复 / 计划：读图修正时必须优先从当前 CAD 实体回读定位目标参照物。本轮用当前 AutoCAD `CODEX_PREVIEW` 中原第 12 项 8 个非 `SOLID` hatch 样本 bbox 反推原面板位置和样本边长，在面板上方箭头语义位置画 1 个同尺寸 `SOLID` 正方形，并截图复核。

以后规则：用户用箭头、圈选或“图几位置”给反馈时，不得默认套用训练 parking anchor 或旧报告坐标；先识别截图中被指对象及其相对位置，再从当前 CAD 回读对应实体 bbox。若无法确定坐标，应说明图像语义假设，而不是另起模块。

相关文件：`core/training/foundation_panel_drawings.py`、`scripts/run_cad_foundation_remaining_training.py`、`tests/core/test_cad_foundation_remaining_training.py`、`output/training_queues/cad-foundation-remaining-21/focused/image-arrow-solid-fill-square/report.json`

## 2026-06-01 单项加深训练被整批脚本放大

现象：用户要求“任务 12 加深训练”，实际执行时沿用了 `scripts/run_cad_foundation_remaining_training.py` 的整批入口，导致剩余 21 项全部重新跑了一遍。用户真正需要的是贴近第 12 项和指定 hatch 图样 / 比例的轻量级复训。

影响：CAD 画布被不必要地新增整批训练面板，用户复核负担变重；更重要的是，Agent 可能把“已有批量脚本”误当作执行范围，忽略用户点名的最小需求。

修复 / 计划：新增训练范围硬边界：点名单项或子图样时只做 focused retraining，整批训练必须有“全部 / 整批 / 重新跑所有 / 刷新整个队列”等明确口令。剩余 21 项脚本新增 `--only`、`--hatch-pattern`、`--hatch-scales`，报告写入 `scope.mode=focused`、`requestedCapabilityIds` 和 `scopeReason`；focused 输出不覆盖整批验收状态。

以后规则：当用户只要求某个任务、某个图案或某组参数时，Agent 先找或补 focused 入口；没有窄范围入口时必须询问是否允许扩大范围，不得静默跑全量。验证时优先用 fake-cad focused 命令证明只生成请求范围内的对象，再决定是否需要真实 CAD 局部复训。

相关文件：`core/training/foundation_batch_training.py`、`core/training/foundation_panel_drawings.py`、`scripts/run_cad_foundation_remaining_training.py`、`tests/core/test_cad_foundation_remaining_training.py`、`AGENTS.md`

## 2026-06-01 训练面板复跑可能按全画布漂移

现象：用户为了查看方便会手动移动已训练出的 `CODEX_PREVIEW` 面板；旧脚本下一轮只看全局预览 bbox，画布上只要远处还有预览实体，复训就会继续往最右侧外扩。

影响：训练目标越来越分散，用户难以复核；同时用户移动后的“方便查看位置”不会被脚本尊重。

修复 / 计划：剩余 21 项批量训练脚本现在优先读取上一轮 execution summary 的 created handles，回读这些 handles 的当前位置和 bbox 作为 `parking_anchor`；只有旧 handles 缺失或无法回读时，才退回全局 `CODEX_PREVIEW` bbox 或原点。

以后规则：用户移动训练面板不应破坏识别；只要原 handles 仍在，复训应跟随新位置。若用户炸开、删除或复制重画导致 handles 失效，必须在报告中说明已退回 `global_preview_bbox` / `origin`，不得假装仍识别到原训练对象。

相关文件：`core/training/foundation_batch_training.py`、`tests/core/test_cad_foundation_remaining_training.py`、`AGENTS.md`、`docs/training/README.md`

## 2026-06-01 基础训练中文标注检查过宽

现象：用户复核 `CAD 基础操作` 剩余 21 项训练截图时，发现面板里仍有 `checked`、`handles`、`bbox`、`locked`、`Rev-A`、`AUDIT/PURGE`、`checked/not_checked` 等英文可见标注。

影响：训练工作台和报告显示 21/21 通过，但真实 CAD 预览没有达到“中文训练面板”的用户验收口径；后续 Agent 可能继续用“有中文即可”的弱检查放过中英混排。

修复 / 计划：面板可见文案、第 29 项标题与工作台数据源已改成中文；`foundation_batch_training` 的 `chinese_labels` 验收新增英文术语阻断，必须同时满足含中文且 `latin_terms=0`；单测新增 fake CAD 可见文字扫描。

以后规则：中文标注训练不能只检查 CJK 字符存在；面向用户可见的训练面板、标题和截图说明必须扫描英文术语。技术字段、Schema key、图层名和内部报告字段可以保留英文，但不得混进 CAD 面板可见标注。

相关文件：`core/training/foundation_panel_drawings.py`、`core/training/foundation_batch_training.py`、`scripts/build_capability_map_data.py`、`tests/core/test_cad_foundation_remaining_training.py`

## 2026-06-01 默认上下文与训练事实源漂移

现象：仓库已有短入口、状态页、长期规则、handoff、训练工作台和历史设计文档，但部分入口仍会互相抢话：`CORE_CONTEXT_BRIEF.md` 的最近事实段变长，长期规则里残留旧表 C 当前值，后置 backlog 里有旧 99.68% 快照，训练验收报告路径在工作台生成器中硬编码。

影响：新 Agent 容易读太多旧 MD，把历史施工包或旧案例当成当前主线；训练工作台也可能因为新增第二批验收报告却忘记改硬编码列表而漏接事实源。

修复 / 计划：新增 `docs/training/training-sources.json` 作为训练事实源 manifest；工作台生成和同步从 manifest 读取验收报告与 learning ledger；Agent check 阻断未登记验收源和派生快照反向冒充事实源。短入口压缩为当前事实 + 按需展开，旧表 C 数字只保留为历史快照。

以后规则：`capability-map-data.js`、`capability-map.html`、sync report 都是派生产物；训练验收报告、队列状态、learning ledger、Agent memory / Prompt addendum 才能登记为事实源。新增训练队列或验收报告时，先更新 manifest，再同步工作台。

相关文件：`CORE_CONTEXT_BRIEF.md`、`docs/training/training-sources.json`、`scripts/build_capability_map_data.py`、`scripts/run_training_workbench_agent_check.py`

## 2026-06-01 训练报告 JSON BOM 会导致 learning promotion 漏接

现象：CAD 基础操作剩余 21 项真实 CAD 训练通过后，手动回填截图路径时 PowerShell 写出了带 UTF-8 BOM 的 JSON；`sync_training_workbench.py` 能看到报告路径，但 `promote_training_acceptance()` 用 `encoding="utf-8"` 读取时把报告判为 invalid JSON，导致 learning promotion 只统计前 10 项。

影响：前端和训练报告可能看起来已更新，但智能体记忆 / Prompt addendum 没有吸收新训练项，形成“报告通过但 Agent 没学到”的隐性漂移。

修复 / 计划：`core/training/learning_promotion.py` 与 `scripts/build_capability_map_data.py` 读取 JSON 改为 `utf-8-sig`；新增 BOM 回归测试；重新同步后 learning promotion 为 31 items / 7 agents。

以后规则：训练事实源 JSON 可能来自 Python、PowerShell 或其它工具，读取侧必须兼容 UTF-8 BOM；同步结果里的 `acceptedItemCount` 必须与预期训练报告项数核对，不能只看 `status=pass`。

相关文件：`core/training/learning_promotion.py`、`scripts/build_capability_map_data.py`、`tests/core/test_training_learning_promotion.py`

## 2026-06-01 基础训练可能被误读为永久封存

现象：`CAD 基础操作` 31/31 通过并沉淀后，后续 Agent 可能把 `systemized/pass` 理解成“这个基础项已经交付封存，不再需要改”。但复杂对象、场景或施工图表达训练中，仍可能暴露基础命令、图层纪律、闭合、回读、block 引用、layout / plot 或安全回滚不扎实。

影响：如果不允许回流复训，复杂任务中的基础缺陷会被错误地只在上层打补丁，无法真正补基本功；也会让工作台 31/31 变成阻碍修正的假完成状态。

修复 / 计划：新增基础能力回流复训规则：复杂任务触发基础缺口后，记录触发任务和失败症状，映射到基础训练项，修改相关脚本 / Prompt / 检查器 / 规则，复训基础项，再回测原复杂任务。旧通过报告保留为历史证据，新复训报告追加沉淀。

以后规则：训练通过不是永久封存；`systemized/pass` 只表示当时证据通过。不得用“基础项已完成”拒绝修基础能力；也不得把复训需求说成表 C 已提升，仍需具体 CAD 证据。

相关文件：`AGENTS.md`、`docs/governance/cad-agent-rules.md`、`docs/training/README.md`、`docs/training/cad-designer-growth-path.md`、`agents/cad_designer/rules.md`

## 2026-06-01 自动化训练长任务可能卡死

现象：未来大面积自动化训练 CAD 任务时，CAD COM 等待、截图、created handles 回读、训练队列推进、post-sync 或 Agent check 都可能长时间不返回。如果没有统一 timeout 和熔断，队列可能卡住，也可能在证据不完整时继续无人值守推进。

影响：训练链路不稳定，用户需要手动盯守；partial output、过期快照或未完成同步可能被误判成训练通过；更严重时可能诱发不安全 CAD 操作。

修复 / 计划：新增自动化训练 30 秒单步 watchdog、有限自救和连续超时熔断规则。任一子动作超时后，Agent 先读取 stdout / stderr、最近报告、队列状态和 CAD 会话状态，自行尝试一次有限恢复；同一训练项连续 2 次超时，或同一队列连续 3 个子动作超时 / 失败，必须暂停到 `blocked` / `needs_user_review`。

以后规则：训练脚本和 Agent 记录应写入 `timeoutSeconds: 30`、`selfRecoveryAttempted`、`circuitBreakerTriggered`、`blockedReason`、卡点、自救动作、保留证据和下一步建议。熔断后不得继续无人值守落图、保存 DWG、覆盖原图、删除实体或改正式图层，也不得把 partial output 当作训练通过。

相关文件：`AGENTS.md`、`docs/governance/cad-agent-rules.md`、`docs/training/README.md`、`agents/cad_designer/rules.md`

## 2026-06-01 训练产物可能越积越多

现象：第一批 10 项基础训练后，`output/training_queues/cad-foundation-first-10/` 留下了最终验收报告 / 截图，也留下了中间 retry 目录、临时 dry-run、execution summary 和单项报告。当前总量不大，但长期训练会持续堆积。

影响：训练证据和临时调试产物混在一起，后续 Agent 难判断哪些必须保留、哪些可以删除；也会浪费空间并降低工作台 / memory source refs 的可读性。

修复 / 计划：新增训练产物最小保留规则：长期保留最终验收报告、队列状态、learning ledger、Agent memory / Prompt addendum 和最近一份人工复核预览图；中间 retry、临时计划、dry-run、execution summary、旧截图和一次性脚本在验收沉淀后清理。删除前必须校验引用关系。

以后规则：训练产物清理不能把教训一起删掉。失败根因先写入 `docs/training/training-errors.md` 或 learning promotion，再清理临时文件；最终验收报告若仍被工作台或 learning ledger 引用，不得删除。

相关文件：`AGENTS.md`、`agents/cad_designer/rules.md`、`docs/training/README.md`

## 2026-06-01 训练脚本通过后没有自动收尾同步

现象：`scripts/sync_training_workbench.py` 已能执行 learning promotion、重建前端数据并跑 Agent check，但监督式训练队列 `scripts/run_training_queue.py` 原先只更新队列状态；训练项通过后还要靠用户或 Agent 额外说“同步前端 / 沉淀 Prompt”。

影响：训练闭环容易断在脚本边界：队列状态通过了，但工作台、智能体 Prompt、learning ledger 和 Agent check 可能没有及时刷新。用户也会被迫重复提醒同一类收尾动作。

修复 / 计划：训练队列脚本新增自动 post-sync：`--decision pass` 后触发轻量同步，队列 `completed` 后触发完整 `sync_training_workbench.py`；JSON 输出写入 `postTrainingSync`。全局规则和 CAD Designer 规则要求后续训练脚本同样复用总同步入口，不复制逻辑。

以后规则：凡是本仓库维护的训练脚本记录 `pass` 或 `completed`，必须自动调用训练收尾同步，除非显式传调试跳过参数；不得把同步工作台和 learning promotion 变成每轮手工口头步骤。

相关文件：`scripts/run_training_queue.py`、`scripts/sync_training_workbench.py`、`AGENTS.md`、`agents/cad_designer/rules.md`、`docs/training/README.md`

## 2026-06-01 训练已沉淀但阶段仍显示 4/5

现象：训练项已通过用户验收并完成 learning promotion，但工作台阶段仍显示“用户反馈通过 / 第 4/5 阶段”。用户会自然理解为还有一个训练阶段没做完。

影响：前端阶段与实际训练沉淀状态不一致；用户无法判断剩余阶段是什么，也会怀疑验收和学习沉淀是否真的完成。

修复 / 计划：`stageState` 现在按 learning promotion 晋升：仅验收通过但未沉淀时显示 4/5；验收且已沉淀到责任智能体时显示 `systemized / 已沉淀 / 第 5/5 阶段`。

以后规则：训练阶段数字必须反映训练闭环状态；“第 5/5 阶段”只代表本训练项已验收并沉淀到规则 / Prompt，不得解释为表 C 或完整施工图能力。

相关文件：`scripts/build_capability_map_data.py`、`tests/core/test_training_workbench_sync.py`

## 2026-06-01 训练通过文案暴露后台路径

现象：训练工作台的“用户反馈通过 / 已通过训练”说明直接显示 `output/.../*.json` 验收报告路径，训练沉淀区域还显示 `agents/.../training_memory.json` 等文件路径。用户无法从前端直接判断这项训练到底学会了什么。

影响：工作台看起来像后台文件索引，而不是训练验收说明；用户需要理解内部文件结构才能验收训练状态，也容易误以为只要文件存在就等于训练有效。

修复 / 计划：验收结果新增 `plainLanguageSummary`，学习沉淀新增 `visibleLessons`；页面只展示“中文标注、CODEX_PREVIEW、handles 回读、未保存 DWG、未写正式图层、责任智能体已吸收经验”等白话摘要；Agent check 阻断可见训练文案中的 `.json`、`output/` 和缺失白话摘要。

以后规则：前端给用户看的“已通过训练 / 已学习”必须先翻译成白话；后台 source refs 只能用于机器追溯或折叠的工程调试，不得作为训练通过说明的主文案。

相关文件：`scripts/build_capability_map_data.py`、`core/training/learning_promotion.py`、`capability-map.html`、`scripts/run_training_workbench_agent_check.py`、`tests/core/test_training_workbench_sync.py`

## 2026-06-01 训练验收只改前端、不沉淀智能体

现象：训练报告已经通过并能让前端阶段变为通过，但如果没有强制 learning promotion，责任智能体的 Prompt、规则入口和经验记录可能没有同步更新，用户会看到“训练结束”，实际 Agent 仍没有吸收教训。

影响：训练工作台会变成状态看板，而不是训练闭环；后续测试可能重复犯同样的问题，例如英文标注、重叠旧图块、未回读 handles 或只改页面状态。

修复 / 计划：新增 `promote_training_acceptance()`、`scripts/promote_training_acceptance.py`、Agent 级 `training_memory.json` / `prompt_addendum.md`、`output/training_learning/agent_learning_ledger.json`，并把 `sync_training_workbench.py` 改成先沉淀再同步；Agent check 新增学习沉淀和 Prompt source refs 门槛。

以后规则：任何已验收训练项如果缺少 `learningPromotion.status=promoted`，不得声称智能体已经变聪明，也不得声称训练工作台已同步。训练通过仍不提升表 C，不等于施工图能力。

相关文件：`core/training/learning_promotion.py`、`scripts/promote_training_acceptance.py`、`scripts/sync_training_workbench.py`、`scripts/run_training_workbench_agent_check.py`、`agents/cad_designer/rules.md`

# CAD Agent 问题与修复记录

本文现在只保留活跃风险和高频教训。压缩前完整问题库已归档到 `docs/history/snapshots/root-md-2026-05-26/CAD_AGENT_ISSUES.md`。

## 2026-06-02 通用资产只留在当前 DWG 或训练报告

现象：训练中画出的线宽线型、尺寸样式、引线样式、沙发等对象如果只留在当前 `CODEX_PREVIEW` 或当前 DWG 中，新开 CAD 文件不会自动拥有这些标准或资产。

影响：用户说“沉淀资产”时，Agent 可能只保存截图、报告或当前 DWG 证据，未来检索不到、导入不了，也不知道什么时候应该使用该资产。

修复 / 计划：新增系统资产沉淀协议：机器契约 + CAD 原生资产位置 + 应用 / 验收工具 + 全局索引。当前入口 `scripts/sediment_system_asset.py` 会更新分类 `assets.json` 和 `libraries/system_library/registry.json`，例如沙发资产统一进入 `libraries/system_library/furniture/seating/sofas/`，绘图标准进入 `libraries/system_library/drawing_standards/basic/`。

以后规则：合同登记不等于原生 DWG 导出。只要报告中 `nativeDwgExists=false`，就只能声称系统资产位置和索引已建立；真实 `*_assets.dwg` 写入、block 导出、样式导入、保存和回读必须另有显式 CAD 操作和证据。

相关文件：`docs/architecture/system-asset-sedimentation-protocol.md`、`core/assets/system_asset_sedimentation.py`、`scripts/sediment_system_asset.py`、`libraries/system_library/registry.json`

## 2026-06-02 线宽线型训练只画普通线

现象：第 22 项“线宽线型标准”截图里三条测试线看起来没有真实线宽差异，CAD 已开启线宽显示也没有改善；线型变化也没有被机器证据证明。

影响：训练报告可能因句柄、图层和中文标注都通过而误判完成，但实际 CAD 实体仍是默认普通线；后续 Agent 会把“文字写了粗线 / 中线 / 细线”误当成真实 `Lineweight` / `Linetype` 能力。

修复 / 计划：任务 22 样例线必须真实写入并回读 `Lineweight`、`Linetype` 和 `LinetypeScale`。本轮已将三条样例线加固为 `70 + CONTINUOUS`、`35 + CENTER`、`13 + DASHED`，真实 CAD focused 报告新增 `styleEvidence`，批训练检查新增 `lineweight_linetype_standard`。

以后规则：凡是训练线宽、线型、颜色、填充图样、比例等 CAD 样式属性，不能只看截图或标签；必须在 driver 写入、`snapshot_handles` 回读和验收报告里都有对应属性字段。若样式视觉差异依赖 AutoCAD 显示设置，还要补实体属性证据和必要截图。

相关文件：`core/training/foundation_panel_drawings.py`、`core/cad_io/autocad_com.py`、`core/verification/fake_cad_driver.py`、`core/verification/inspect_dwg.py`、`core/training/foundation_batch_training.py`、`tests/core/test_cad_foundation_remaining_training.py`

## 2026-06-02 样式属性验证可能被误读为打印验证

现象：线宽、线型、颜色进入 `CAD_PLAN` 和 `drawing_standard_profile` 后，Agent 可能把 `style_resolution` 或 preview execution summary 中的 `style_evidence` 误报为“打印线宽已经正确”。

影响：CAD 属性正确不等于 CTB/STB、视口比例、`LTSCALE/PSLTSCALE` 和最终 PDF plot 都正确。尤其颜色可能只是 ACI 笔号，截图也会受线宽显示开关、缩放和抗锯齿影响。

修复 / 计划：样式语义契约把 `style_verified`、`geometry_verified`、`plot_verified` 分开；当前 `style_evidence.plot_verified=false`，`not_checked` 明确包含 `ctb_stb_plot_mapping`、`plot_output`、`viewport_linetype_scaling` 和 `visual_readability`。Review 后已补 `by_layer` 不写硬编码实体色、未解析 `style_token` 校验失败、`style_token` / `layer_role` 冲突拒绝和 `Color` readback 通道；这些只证明属性通道更闭合，仍不证明打印输出。

以后规则：没有 layout / CTB/STB / plot preview 或 PDF 输出验证前，只能声明 CAD 样式语义和属性意图已解析 / 写入；不得声称打印出图效果已验证。家具图块内部样式也必须说明是否已展开 block definition 或仅检查了 preview primitive。

相关文件：`core/drawing_standard/drawing_standard_profile.py`、`core/plan_engine/dry_run_report.py`、`core/plan_engine/symbol_glyph_plan.py`、`core/execution/execute_plan.py`

## 当前活跃风险

| 风险 | 当前影响 | 处理口径 |
| --- | --- | --- |
| Core / training / case 边界继续变重 | `core/` 子模块、`core/verification/`、capability map 和 `projects/.../runs` 里的可复用逻辑如果继续混放，会让后续 Agent 不知道该抽到哪里 | 以 `docs/architecture/current-module-boundaries.md` 为当前边界快照；稳定 Core、Training Experiments、Case-Only 三桶先判定，再按 split map 或 promotion gate 移动 |
| OpenSpec 被误当第二主计划或误判未初始化 | 初始化后若把 `openspec/changes/*` 当全局 next / backlog，会和唯一 PlanMD 冲突；若看到 `openspec list --specs` 暂空或 `status` 缺少 `--change` 报错，也可能误判 OpenSpec 不可用 | OpenSpec 只做复杂变更契约；`CORE_RESTRUCTURE_PLAN.md` 仍是唯一主线；readiness 用 `list --json`、`status --change <change> --json`、`validate --all --strict --json --no-interactive`；completed changes 归档前要同步稳定 specs 和引用；`check_openspec_contracts()` 阻断根级 `openspec/tasks.md` 和 active change 自称主计划 |
| 活跃入口 MD 过长 | 旧完成流水会撑大每轮上下文，稀释当前主线 | PlanMD、任务清单、Core Status、current status 只保留控制面；旧记录查 `docs/history/snapshots/finished-architecture-2026-05-28/` 和 `docs/planning/archive/`；`run_doc_governance_audit.py` 校验体量预算 |
| 场景 Alpha / Beta 被误读为 Scene Product | 可能误以为工装、办公、住宅、餐饮 Agent 已产品化 | 统一四级成熟度；Scene Product 必须有真实项目样本、图块 metadata、真实 CAD smoke、用户确认流 |
| 真实 CAD 校验样本不足 | 不能证明任意项目 DWG 或任意 `CAD_PLAN` 几何准确 | 继续推进 §5 `RCAD-22+` 与 §3 `V-PROOF` 链式回写 |
| ActiveDocument / guard 仍需真实会话复验 | `LCAD-13/14` 已有 snapshot 与 strict guard 包装，但仍需更多真实 CAD 场景确认 | 优先用 `RCAD-21/22` 和后续真实 CAD smoke 扩样，不把 guard-only 当几何 verified |
| no-CAD deferred 被误读 | 顶层 pass 可能被误写成真实 CAD verified | 必须区分 `deferred`、`not_verified_without_cad_readback`、`geometry_verified` |
| 截图被误当几何证据 | 视觉辅助不能证明尺寸、图层、handle 和 bbox 准确 | 几何声明必须看 created handles readback |
| 路径边界回归 | runner 新增参数时可能越界读写 | 复用 `core.path_safety`，真实 CAD 连接前先做路径预检 |
| Schema 未登记 | schema 文件可能存在但 validator 不知道 | 新 schema 必须同步 registry、example、invalid fixture 和 tests |
| Markdown 进度漂移 | 表 A/B/C、RCAD 烟囱和 coverage JSON 容易被旧快照覆盖 | 表 C 以 `output/validation_runs/capability-lab/cad_capability_coverage.json` 为准；任务 next 以 PlanMD + 任务清单同步为准 |
| guard / negative 行误升 showcase | 安全守卫或负例拦截会被误算成几何能力，抬高表 C | negative / guard registry 行必须保持 `smoke`；只证明 guard-only，不得写成 `geometry_verified` / `showcase` |
| 普通回复表格噪声 / 旧上下文覆盖新规则 | 旧版 `AGENTS.md` 曾要求默认带精简进度表；若会话压缩或早期注入的旧规则仍在上下文中，可能覆盖当前仓库 opt-in 规则，导致普通回复误带表 | 普通最终回复默认不附进度表；只有用户点名开发状态查询、进度、完整状态、交接、审计、表 A/B/C、表 C 或真实 CAD 实力时才展开表格；涉及真实 CAD 实力时先拆 `Core Proof Coverage`、`Agent Task Maturity` 和 `Project Delivery Readiness`，表 C 只作为 Core Proof Coverage 机器快照，不代表端到端交付能力 |
| 常识资料被误当成能力 | 把 GitHub 方法论、图库、PDF、DWG 或截图放进仓库，不会自动让 Agent 稳定使用，可能虚报“已学会” | 常识必须经过 `source_note → knowledge_summary → object_or_rule_candidate → executable_check → evidence_boundary`；未形成可执行检查前只能作为参考知识 |
| raw 标准图库进 git 的边界风险 | 用户需要 `standard_cad_library_raw/` 随 git 迁移；如果批次说明缺失，可能把临时文件、授权不清资料或下载失败缓存误提交，也可能把 raw 命中误报为系统能力 | 每批次默认跑 `scripts/run_asset_raw_intake.py --write` 生成 `source_note`、reference manifest 和 inferred annotation；提交前检查 `git status --short standard_cad_library_raw libraries/reference_library libraries/system_library`；raw 永远先按 `reference_only` 处理 |
| HTML 训练工作台被误当能力证明或最新事实源 | 根目录 `capability-map.html` 是给人看的计划 / 覆盖清单，如果勾选口径不严或数据快照未同步，可能被误读为真实 CAD 已验证或最新训练状态 | 页面只显示阶段；勾选必须来自 raw 导入、常识整理、训练通过或自产资产晋升事实；真实几何能力仍看 CAD 证据和表 C；训练、registry、coverage 或 Prompt 改动后必须跑 `scripts/sync_training_workbench.py`，并通过 `scripts/run_training_workbench_agent_check.py` |
| CAD Designer Agent 成长路径被误当施工图能力 | 新增总设计师 Agent、成长阶段和基础课程后，后续 Agent 可能把“第一阶段毕业目标”误解成已具备完整专业平面图或施工图交付能力 | 第一阶段只定义电子设计师雏形；L0 基础课程只证明训练进度。真实 CAD 声明仍必须看 `CAD_PLAN` / 结构化意图、validate、dry-run、`CODEX_PREVIEW`、created handles 回读、审计和用户反馈；不提升表 C |
| V2 训练地图被误当已经学会 | 正式训练前扩到 217 个训练项后，后续 Agent 可能把“计划里有”误读成“系统会画”或“施工图能力已覆盖” | V2 只是课程地图；每项仍要按 `目标已声明 → 案例训练中 → 用户反馈通过 → 已沉淀` 逐步晋升。条目存在、参考尺寸、图库命中和工作台显示都不能替代 `CODEX_PREVIEW`、created handles、审计和用户验收 |
| V2.1 验收器骨架被误当已实现检查器 | 新增 `validationCheckers` 后，后续 Agent 可能把图层安全、净距碰撞、跨图一致性等 skeleton 写成已经能跑的 CAD proof | 骨架只说明后续训练应检查什么；只有接入真实输入、输出报告、测试和 CAD 回读后，才能晋升为可执行 checker。当前不计入表 C，不替代真实 CAD 审计 |
| 基础 CAD 操作被误当资产缺口 | 基础图元、选择编辑、变换等 L0 课程如果共用“图库 / 自产”四轨并显示“未纳入”，容易被误读成还缺标准图块或自产资产 | 基础操作类在工作台显示 `not_applicable / 不适用`；它们不要求标准图块输入，也不晋升 `system_library`，默认沉淀命令参数、Prompt 约束、检查器、失败经验和审计口径 |
| 监督式训练队列被误当无人值守 CAD | `run_training_queue.py` 可能被误解为会连续自动落图、自动保存或自动判定用户验收 | 队列 v1 只做监督式编排：每次暂停 1 项，输出验收 checklist 和 `--decision pass/fail` 下一步；真实落图仍只写 `CODEX_PREVIEW`，并按 validate、dry-run、handles 回读和审计链路执行 |
| 训练前仓库审计仍有低风险维护项 | `run_repo_audit.py --max-python-lines 500 --fail-on-findings` 会因 7 个 low `large_python_file` findings 返回 1；`run_dev_volume_audit.py` 会因 `capability-map-data.js` 生成快照大 delta 报 low findings | 本轮已确认无阻塞级路径污染、文档治理或单测失败；Core gate 只把这些作为 non-blocking low findings。后续拆分 `scripts/build_capability_map_data.py`、`core/verification/*` 大文件和 case renderer 时按架构边界推进，生成快照大 delta 不单独当运行时 bug |
| 参考图库污染自产图库 | 外部标准 CAD 图库、vendor block、用户 DWG 截图或版权不清素材如果直接进入系统图库，会把“看过”伪装成“自产可复用能力” | `reference_library` 与 `system_library` 必须分层；自产资产必须有 lineage、schema、测试、晋升记录和 evidence_boundary；外部资料默认 `reference_only` |
| 图库驱动导致创造性收缩 | 如果只做 top-1 图库检索再拉伸变形，系统会变成模板变体机，图库没有的对象反而不会生成 | 用对象语法、参数化对象族、style modifiers 和探索模式；图库弱命中时输出候选和 `visual_review_required`，不直接声称完成 |
| 资产基础设施未测试 | 用户本轮明确排除测试，新增 retrieval / promotion gate 只做非测试检查，可能存在未覆盖边界 | 下一包若继续落地对象族或自动晋升，应补 focused tests；当前不得声称这些入口已完整验证 |
| 训练反馈低信号 | 只报 `0 gap / 0 overlap`、handles 数、arc 数或贴截图，用户仍不知道该看哪里，也无法高效纠错 | 训练汇报改用低噪声模板：本轮结论、变化、checked/not_checked、重点看点、反馈入口；不把机器绿等同于用户验收 |
| 结构合并误伤边界 | 为减少文件数而合并 CLI / safety / evidence / CAD runner，会破坏可审计入口 | 按 `struct_merge_keep_rules.md` 执行；每个 `STRUCT-MERGE-xx` 只处理 1-3 组候选，必须 focused tests + repo audit |
| writeback 不识别 showcase 行 | registry 行从 verified/smoke 升到 showcase 后，旧绑定逻辑可能把它当 unsupported claim_level | 绑定类写回应把 showcase 视为“保留 evidence、只追加来源”的已验证类行；已有 RBLOCK-07 回归测试覆盖 |
| 文档迁移断链 | 大量 Markdown 移动后，旧路径、handoff、表 C 数字和新人入口可能漂移 | 旧根路径保留 stub；`output/validation_runs/**` 不移动；新增 `run_doc_governance_audit.py` 做链接、主从、表 C 和 handoff 检查 |
| coverage 证据路径缺失未成硬门 | coverage JSON 已统计 `report_path_missing`，但当前仍以 registry claim_level 计算表 C | 表 C 汇报必须同时看 `evidence_path_audit`；后续若把缺失路径改成硬门，需要先补齐历史证据路径，避免误降级 |
| 历史 verified/showcase 证据不满足新硬审计 | 新增 hard audit 后，旧报告可能缺 `checks`、`actual.created_handles`、`actual.entities` 或实际文件路径 | 新一轮表 C writeback 先过 `run_table_c_evidence_gate.py`；旧证据债另开补齐包，不用截图或旧 coverage 直接掩盖 |
| 训练案例部件契约虚绿 | `visual_parts` 部件齐全不等于参考款式准确，profile ratio 对齐也可能放过靠背/坐垫层级方向错误 | round12 已登记 fail；round14 已补 `sofa_direction_semantics_inverted` 并真实重画；仍以用户目视验收为准 |

## 最近修复教训
### 基础 CAD 操作不应被四轨资产表误读为资产缺口

日期：2026-06-01

现象：训练工作台把所有训练项统一放进“图库 / 常识 / 训练 / 自产”四轨。基础图元绘制、选择编辑、旋转缩放等 L0 课程的图库和自产轨道显示“未纳入”，用户容易理解成还必须准备标准图块或总结自产资产。

影响：正式训练会被错误导向图库 intake 或 `system_library` 晋升，偏离基础课程真正要练的命令参数、几何洁净、图层安全和回读审计。

修复 / 计划：`scripts/build_capability_map_data.py` 对 `kind=foundation` 的 `raw/system` 轨道生成 `not_applicable / 不适用`；基础训练成功条件改为 `CAD_PLAN`、created handles、entity type、bbox、端点 / 闭合、gap / open endpoint 和 `CODEX_PREVIEW` 证据；文档同步说明基础操作中的 block 指命令 / 引用机制，不等于标准图块资产。

以后规则：基础 CAD 操作默认不走标准图库和自产资产沉淀；只有对象训练、图库优化或明确晋升任务才进入资产轨道。训练工作台逻辑调整必须改数据源和测试，再由 `scripts/sync_training_workbench.py` 刷新快照。

相关文件：`scripts/build_capability_map_data.py`、`capability-map.html`、`tests/core/test_training_workbench_sync.py`、`docs/training/cad-designer-training-plan-v2.md`

### 大体量训练计划必须有机器约束，不能只靠页面观感

日期：2026-06-01

现象：正式训练前用户要求把训练计划扩成大体量训练地图。如果只手工改 `capability-map-data.js` 或 HTML，很容易变成不可复盘快照，也容易把“训练项存在”误读成能力已通过。

影响：训练心流会被边训边补计划打断；更严重的是，工作台可能被当成真实 CAD 能力证明，和表 C / 用户案例验收混口径。

修复 / 计划：V2 扩容写回 `scripts/build_capability_map_data.py` 的结构化 seed 数据源，并新增 `test_training_plan_v2_has_large_scale_coverage` 锁住总量、分类底线、关键训练项和 ID 去重；训练计划文档明确 V2 只是课程地图。

以后规则：训练工作台的大体量计划调整必须先改数据源和测试，再由 `scripts/sync_training_workbench.py` 生成快照；不得手改 HTML / JS 快照后声称同步完成。

相关文件：`scripts/build_capability_map_data.py`、`tests/core/test_training_workbench_sync.py`、`docs/training/cad-designer-training-plan-v2.md`

### 测试临时目录和工作台快照要隔离环境副作用

日期：2026-06-01

现象：正式训练前全量测试最初出现 5 个 `PermissionError` 和 1 个训练工作台 Agent check failure。权限错误来自当前 Windows / 沙箱下 `tempfile.TemporaryDirectory()` 创建的目录后续不可写；Agent check failure 来自全量测试中 coverage JSON 刷新后，根目录 `capability-map-data.js` 的生成时间早于 coverage。

影响：这些失败会让训练前仓库健康检查误判为业务回归，也会让工作台校验受测试运行顺序影响。

修复 / 计划：测试统一使用 `tests.helpers.temporary_artifact_dir()` 在 `output/test_artifacts/` 下创建可写临时目录；工作台 CLI 测试先生成自己的临时快照再校验，根目录快照由 `sync_training_workbench.py` 负责刷新。

以后规则：单测不得依赖系统默认临时目录权限，也不得把根目录静态快照当作测试内可变 fixture；任何 coverage / registry / Prompt / 工作台数据变化后，都要复跑 `scripts/sync_training_workbench.py`。

相关文件：`tests/helpers.py`、`tests/core/test_asset_raw_intake.py`、`tests/core/test_training_workbench_sync.py`、`scripts/sync_training_workbench.py`

### 可选截图依赖缺失要降级，不应让自检失败

日期：2026-06-01

现象：系统 Python 没有安装 `PIL` 时，`importlib.util.find_spec("PIL.ImageGrab")` 会先因父包缺失抛 `ModuleNotFoundError`，导致 `render_preview --check`、`self_check.py` 和相关 wrapper 测试失败。

影响：截图能力是辅助视觉证据，不应因为当前解释器缺少可选截图依赖就让仓库健康检查误判为失败；标准 CAD-MCP venv 仍有完整截图依赖。

修复 / 计划：`module_available()` 捕获 `ModuleNotFoundError` 并返回 `False`；截图能力报告在缺少 `PIL` 时降级为 unavailable / warn；测试改为按 dependency 状态断言 capture mode。

以后规则：截图、窗口捕获和 GUI 依赖都按可选能力处理；缺失时报告能力不可用或 warn，真实 CAD 准确性仍以 created handles readback 和几何证据为准。

相关文件：`core/verification/render_preview.py`、`tests/core/test_render_preview.py`

### 架构瘦身先立边界，再按证据拆文件

日期：2026-06-01

现象：`core/` 子模块数量已接近“什么都往 Core 里放”的临界点；`core/verification/`、capability map、资产智能和 case-run renderer 都出现了职责变重迹象。

影响：如果只按行数机械拆文件，可能把 report contract、runner、registry writeback、visual audit、case 特例和训练实验拆散到更多文件，但职责仍然混在一起；如果直接把 `projects/.../runs` 的可复用片段上移，又可能把单案例假设误升为 Core 能力。

修复 / 计划：新增 `ARCH-BOUNDARY-HARDENING-01` OpenSpec 和 `docs/architecture/current-module-boundaries.md`，先固定 Stable Core / Training Experiments / Case-Only 三桶，再给 verification、capability-map、对象资产试点和 case-run 晋升分别定 split map / promotion gate。

以后规则：后续重构先问“这段逻辑属于哪一桶、是否通过晋升门槛”，再移动文件；对象资产必须走 `raw reference -> knowledge summary -> candidate -> executable check -> system asset -> CAD_PLAN -> readback`，candidate 不能直接当能力。

相关文件：`docs/architecture/current-module-boundaries.md`、`openspec/changes/architecture-boundary-hardening-01/`、`tests/core/test_architecture_boundary_hardening.py`

### 断电排查时先区分文件损坏和迁移口径滞后

日期：2026-06-01

现象：断电后全量单测最初出现 7 failure / 1 error，看起来像文件丢失或证据损坏；追查后发现 Git 对象库正常，失败集中在旧英文根级文件名、pipeline flow 预期、round12 交付口径和本机缺失 RCAD live JSON。

影响：如果直接补造缺失的真实 CAD JSON，会伪造证据；如果只看失败数量，又会把已迁移的文档入口误判为断电损坏。

修复 / 计划：self-check 和测试改为当前中文 root stub / docs 路径；`pipeline_asset_retriever` 纳入默认 flow 预期；round12 测试改为确认用户反馈后应阻断交付；RCAD-20/21 live contract 在真实 JSON 不存在时 skip，不伪造。

以后规则：断电后先跑 `git fsck --no-dangling`、冲突标记 / JSON / 空文件扫描和全量测试；对缺失真实 CAD 证据只能报告缺失或跳过 live contract，不能用 fixture 冒充真实 AutoCAD 会话。

相关文件：`core/verification/self_check.py`、`tests/core/test_planmd_governance.py`、`tests/agents/test_pipeline_visual_contracts.py`、`tests/core/test_vproof_51_negative_cad.py`、`tests/core/test_vproof_52_guard_cad.py`、`tests/core/test_route_audit_report.py`

### 标准图库 intake 不能靠用户填表和 prompt 记忆

日期：2026-05-29

现象：资产 intake 模板要求用户填写来源、授权、对象范围、图纸类型等字段，容易让用户误以为“没填表就不能入库”；同时仅靠 Agent prompt，后续工具切换到 Cursor 或其它模型时格式容易漂移。

影响：Agent 可能反复追问表格，或把 raw 文件存在误读成 system asset；manifest 批量示例还可能和现有单对象 schema / retrieval 实现不一致。

修复 / 计划：新增 `core/assets/raw_intake.py` 与 `scripts/run_asset_raw_intake.py`，默认扫描 raw 批次并生成单对象 `reference_asset`、`agent_inferred` annotation 和 `source_note`；缺字段保守写 `unknown` / `reference_only`，不写 `libraries/system_library/`。

以后规则：用户只需给文件夹和一句说明即可启动；Agent 先扫再推断，低置信度字段可入库但必须标为候选，不得当事实或能力证明。

相关文件：`core/assets/raw_intake.py`、`scripts/run_asset_raw_intake.py`、`docs/training/asset-intake-template.md`

### 根目录只保留控制入口，训练长文放回 docs/training

日期：2026-05-28

现象：架构主轴清楚，但根目录同时放控制入口、兼容 stub、训练错误长表和 Visual-First 长计划，会让后续 Agent 第一眼误判为“架构乱”。

影响：训练期文档越写越长时，根目录会重新变成默认上下文噪声源；旧根路径如果直接删除，又会造成历史引用和 agent 配置断链。

修复 / 计划：`TRAINING_ERRORS.md` 与 `VISUAL_FIRST_AGENT_PLAN.md` 正文迁入 `docs/training/`，根目录保留 stub；`run_doc_governance_audit.py` 的 root stub 检查同步纳入这两条迁移。

以后规则：根目录优先保留控制面、短入口和兼容 stub；训练正文、错因台账、专项计划进入 `docs/training/`，再由 README / stub / agent config 指向。

相关文件：`docs/training/training-errors.md`、`docs/training/visual-first-agent-plan.md`、`core/maintenance/doc_governance.py`

### 能力展示页面只展示覆盖，不承载证据台账

日期：2026-05-28

现象：用户希望根目录有一个 HTML 页面展示系统能力覆盖，但纠正了页面范围：只列“沙发、茶几、床铺、墙体绘制、窗户绘制”等具体图块和基础绘图能力，不展示每个对象背后的 raw、manifest、case evidence 细节。

影响：如果页面展示过多内部路径，会变成第二套台账；如果页面写得太宏大，又会提前出现“完整施工节点”“完整平面方案”等当前阶段还不该承诺的能力。

修复 / 计划：新增 `capability-map.html`，作为轻量覆盖清单；左侧能力项就是计划列表，右侧阶段默认全空。内部证据继续放 Markdown / JSON / manifest / promotion 记录。

以后规则：HTML 只做用户扫一眼的覆盖面；MD/JSON 才是证据和训练过程的来源。未来每个能力打勾前，必须先有对应阶段事实。

相关文件：`capability-map.html`

### raw 标准图库可以进 git，但必须和自产图库分层

日期：2026-05-28

现象：用户需要把下载过的标准 CAD 图库随 git 在家和公司两头开发。如果继续沿用“大图库默认不进 git”的旧口径，会妨碍迁移；如果直接散放根目录，又会让后续 Agent 把文件存在误读成系统已经学会。

影响：raw 图库一旦和 `system_library` 混在一起，可能出现三类错误：误追踪临时/重复/失败下载文件，误提交授权不清的资料，误把参考图库命中声明为系统自产能力。

修复 / 计划：新增根目录 `standard_cad_library_raw/` 作为 tracked raw reference input；新增 `docs/planning/cad-commonsense-asset-dev-plan-01.md`，规定 raw → reference manifest → knowledge → benchmark → system_library → promotion gate 的路径。

以后规则：下载文件放 `standard_cad_library_raw/`；自产图库放 `libraries/system_library/`。raw 文件可以进 git，但默认 `reference_only`，不得绕过 source note、manifest、可执行检查和 evidence boundary。

相关文件：`standard_cad_library_raw/README.md`、`docs/planning/cad-commonsense-asset-dev-plan-01.md`、`libraries/reference_library/README.md`

### 资产图库要做成能力管线，不是模板池

日期：2026-05-28

现象：用户提出用市面标准 CAD 图库快速训练系统，但担心自产图库只有少数沙发款式时，后续白话生成会被锁死在旧款式变形里。

影响：如果把图库当答案库，系统会误把参考图、vendor block 或单案例产物当能力证明；如果完全依赖 LLM 自由发挥，又会回到凭空画线和审计虚绿。

修复 / 计划：新增 `docs/architecture/cad-asset-intelligence-architecture.md`，把管线定义为 `reference_library -> knowledge -> benchmarks -> system_library -> retrieval_pack -> OBJECT_SPEC / SYMBOL_SPEC -> CAD_PLAN -> audit -> promotion`。新增生产模式和探索模式，要求图库弱命中时走对象语法、参数变体和用户目视验证。

以后规则：参考图库只能作为 evidence input；自产图库必须是 `metadata + generator/recipe + tests + verified examples + evidence_boundary`。单个截图通过最多到 `case_verified`，不能直接变成 `system_verified`。

相关文件：`docs/architecture/cad-asset-intelligence-architecture.md`、`docs/training/global-agent-pipeline.md`

### 常识底座要可查可测，不是把资料丢进仓库

日期：2026-05-28

现象：用户指出基础物件（沙发、桌子、床等）更像 CAD 常识，不应完全靠测试案例一轮轮训练；同时要求吸收外部 GitHub 项目的好方法，但不 clone、不搬代码。

影响：如果只把外部资料或图库放进根目录，Agent 下一轮未必会读到、理解或调用；如果把单案经验直接写成全局规则，又会污染 Core 或产生无法回归的“口头聪明”。

修复 / 计划：新增 `docs/training/cad-common-sense-upgrade.md`，把 `llm-wiki`、`step.parts`、`CADTestBench`、`CADCLAW` 的方法论改写为本系统口径：资料沉淀、catalog-first、可执行检查、证据声明边界。训练 README、learning loop 和 pipeline 文档已挂入口。

以后规则：基础常识必须形成 summary、候选对象或规则、可执行审计、证据边界；未被测试或审计覆盖的内容只能作为参考，不得作为“会画准”的能力声明。

相关文件：`docs/training/cad-common-sense-upgrade.md`、`docs/training/README.md`、`docs/training/learning-loop.md`

### 训练交付汇报必须帮助用户判断，而不是堆机器数字

日期：2026-05-28

现象：训练反馈曾只说明删了多少旧实体、新建多少曲线、机器审计多少项为 0、截图如下；用户仍无法从回复中快速判断“我应该看哪里、这轮是否真的值得验收、机器证据没覆盖什么”。

影响：低信号汇报会把诊断成本推给用户，且容易把 gap/overlap、arc 数或 handles 数误当成款式准确。

修复 / 计划：训练 README 新增低噪声反馈模板，强制汇报本轮结论、相对上一轮变化、机器证据只证明什么、还没证明什么、请用户重点看哪里、用户一句话怎么反馈最有用。

以后规则：训练期普通回复默认不带表 C或进度表；若可验收，必须告诉用户重点看点；若暂不交付，必须说明阻断原因和下一步修复方向。

相关文件：`docs/training/README.md`、`docs/training/cad-common-sense-upgrade.md`

### 部件存在不等于款式匹配，reference-match 必须审计形态和衔接

日期：2026-05-28

现象：round12 `visual_parts` 声明 7/7 部件且均有 CAD handles，机器审计与 Agent 自检曾放行；用户截图指出下方衔接仍错、参考有弧线和丝滑线条、生成结果仍全靠圆角矩形堆叠，并有重叠或间隙。

影响：如果只检查“部件是否存在”，训练链路会把低丰富度示意图当作参考款式匹配结果，继续把虚绿交给用户验收。

修复 / 计划：新增 `rounded_rect_only_parts` 与 `part_connection_defects` 全局审计反模式；case renderer 输出实际 `audit_summary`；round 脚本合入该摘要；沙发 checklist 启用 `reference_profile_match`。round13 已通过形态丰富度、reference profile 和 gap/overlap 门槛；用户指出“底部硬靠背 / 中间软靠垫 / 上部坐垫”的平面图常识后，已新增 `sofa_direction_semantics_inverted` 和共享边去重。

以后规则：reference-match 任务必须同时检查真实参考 profile、部件装配拓扑、形态丰富度和主要视觉层级方向；Agent 自检不能把 created handles、部件数量或 profile ratio 当作款式匹配。

相关文件：`core/verification/training_geometry_audit.py`、`projects/residential_sofa_2seat_20260528/runs/part_renderer.py`、`projects/residential_sofa_2seat_20260528/expected/audit_checklist.json`

### Visual contract 不能只检查字段，必须检查证据文件

日期：2026-05-28

现象：round12 的 `round12_visual_parts.json` 已声明 `style_target`，但对应 `expected/style_target_2seat.png` 原本不存在；补齐时又临时生成了示意图，仍不是来自真实参考截图；`round12_style_compare.md` 也曾停在 `pending execution` 模板态，却没有被 delivery gate 阻断。
影响：Agent 容易把“字段存在”或“有一张生成目标图”误当成“视觉契约闭环”，导致 `delivery_allowed=true` 与真实参考证据状态矛盾。
修复 / 计划：`run_training_round_gate.py` 的 visual contract stage 现在会解析 `visual_parts` 并检查 `style_target` 必须是 case 内真实文件，且 `style_target_source` 必须是 `reference_crop` / `user_reference` / `reference_screenshot`；generated target、缺少真实截图来源、source image 缺失都会阻断。delivery stage 仍要求 `style_compare` 存在且不能包含 pending/未勾选模板标记。
以后规则：视觉契约类字段只算索引，不算证据；证据必须能在仓库中解析、打开或被 gate 检查。reference-match 任务不得把 Agent 生成图作为 style target 交付证据。
相关文件：`core/training/learning_promotion.py`、`projects/residential_sofa_2seat_20260528/expected/style_target_reference_crop.png`、`projects/residential_sofa_2seat_20260528/runs/round12_style_compare.md`


### 机器审计绿后仍要做视觉自检

日期：2026-05-28

现象：round12 初版 `visual_parts` 落图机器审计已过，但同屏截图显示座垫比例像上下四个大矩形，和参考沙发“薄座垫 + 高靠背”的款式仍有差距。

影响：如果只看 `geometry_audit.json`，会把“部件齐全但款式不准”的图交给用户，继续复现早期机器虚绿问题。

修复 / 计划：delivery gate 仍要求 `roundN_preview.png` + Agent 自检；`part_renderer.py` 增加薄座垫/高靠背比例，并用测试约束座垫高度和靠背高度。AutoCAD COM 图层访问也缓存一次，避免高频 `ensure_layer` 触发 `RPC_E_CALL_REJECTED`。

以后规则：训练案例要把“机器审计通过”和“可请用户验收”分开；截图自检发现款式问题时先 Repair，不直接交付。

相关文件：`projects/residential_sofa_2seat_20260528/runs/part_renderer.py`、`tests/core/test_visual_parts_case_contract.py`、`core/cad_io/autocad_com.py`

### 活跃文档要有体量预算，done 明细进 archive

日期：2026-05-28

现象：`CORE_RESTRUCTURE_PLAN.md`、`docs/planning/任务清单.md`、`CORE_STATUS.md`、`docs/status/current.md` 已经声明“不承载长历史 / 只做控制面”，但仍保留大量已完成包明细，默认上下文像施工现场。

影响：后续 Agent 每轮都要扫旧 Phase、旧 done 表和旧状态快照，容易误读 next、混淆表 A/B/C，或把历史包当作当前待办。

修复 / 计划：新增 active doc size budget 检查，活跃入口超预算时 `run_doc_governance_audit.py` 报 `active_doc_over_budget`；瘦身前全文迁入 `docs/history/snapshots/finished-architecture-2026-05-28/`，done 台账索引迁入 `docs/planning/archive/`。

以后规则：完成包明细只进 archive / history / handoff；活跃文件只保留口令、当前值、路由、风险和证据入口。

相关文件：`core/maintenance/doc_governance.py`、`docs/planning/archive/README.md`

### 表 C writeback 必须先过硬证据和视觉复盘门

日期：2026-05-28

现象：coverage JSON 已有 `evidence_path_audit`，但旧流程默认仍按 registry `claim_level=verified/showcase` 计算表 C；截图也容易只作为“看起来画了”的辅助物，未进入 writeback 硬门。

影响：后续 Agent 可能在证据路径缺失、旧报告缺 created handles/checks，或截图复盘失败时仍继续回写 registry，从而让表 C 继续漂移。

修复 / 计划：新增 `run_capability_evidence_audit.py`、`run_visual_cad_review.py`、`run_table_c_evidence_gate.py`；截图复盘失败时 `writeback_allowed=false`，coverage 可通过 `--require-evidence-audit-pass` 启用硬审计。首次审计现有 registry 为 131 audited / 59 pass / 72 fail，旧证据债后续另开补齐包处理。

以后规则：任何新表 C 推进包在 registry writeback 前，必须有 `geometry_verified` / `cad_capability_verified` 证据、硬审计通过、视觉复盘通过；截图仍不得替代 created-handle readback。

相关文件：`core/verification/capability_evidence_audit.py`、`core/verification/visual_cad_review.py`、`core/verification/table_c_evidence_gate.py`、`docs/verification/table_c_evidence_gate.md`

### 结构治理先立规则，再动文件

日期：2026-05-28

现象：`STRUCT-AUDIT-01` 显示仓库已有 505 个 Python 文件、56,247 行；其中很多脚本很薄，但它们同时承担用户可执行命令、交接证据路径或兼容入口。若只按“文件小 / 行数少”合并，容易删掉真正有操作价值的入口。

影响：盲目合并会让后续 CAD 补验、no-CAD benchmark、registry writeback 和状态交接难以复跑；尤其 `scripts/*.py`、`core.path_safety`、`evidence_contract`、CAD COM runner 不能为了少文件数合并。

处理 / 结果：新增 `docs/verification/struct_merge_keep_rules.md` 与 `docs/verification/struct_merge_candidates.md`，把候选分为应合并、应拆分 / 抽公共层、应保留、观察 / 延后；首批只建议 `drawing_policy.py` 这种低风险内部细节进入 `STRUCT-MERGE-01`。

后续结果：`STRUCT-MERGE-01` 已把 `drawing_policy.py` 合并入 `templates.py`，并用 composition focused tests + repo audit 验证。该模式说明：低风险合并也必须先红灯、再最小实现、再写交接。

以后规则：结构整理必须先引用候选表和规则页；真实 CAD / 表 C / safety / evidence 边界默认保留，除非有 focused tests 和明确替代入口。

相关文件：`docs/verification/struct_merge_keep_rules.md`、`docs/verification/struct_merge_candidates.md`

### Registry 绑定逻辑必须跟随 claim_level 晋级

日期：2026-05-28

现象：`STRUCT-MERGE-01` 后跑全量 unittest 时，`tests.core.test_rblock_07_block_matrix_registry_rows` 两个测试失败：matrix sync 只 applied 4/5。根因不是 composition 合并，而是 `block.insert_block_alpha.matrix` 已经晋级为 `showcase`，`apply_block_matrix_registry_binding()` 仍只接受 `smoke`、`verified`、`deferred`。

影响：已晋级 showcase 的 registry 行会在后续 dry-run / no-CAD binding 复跑中被误判为 rejected，造成台账 / 证据刷新失败。

修复 / 结果：`apply_block_matrix_registry_binding()` 现在接受 `showcase`，并像 verified 行一样只追加 matrix source ref / notes，不覆盖既有 readback evidence。修复后 focused RBLOCK-07 9 tests OK，全量 864 tests OK。

以后规则：任何 registry 绑定 / writeback 逻辑新增 claim_level 判断时，必须同时考虑 `showcase` 的“高于 verified、不可降级、不覆盖 evidence”语义。

相关文件：`core/block_engine/block_matrix_registry.py`、`tests/core/test_rblock_07_block_matrix_registry_rows.py`

### 表 C 推进可能掩盖 CAD 画面没有变好

日期：2026-05-27

现象：用户查看 AutoCAD 截图后指出图块仍很简单，真实 CAD 能力观感约 5-10%，且两三天来视觉上没有明显进步。

影响：如果继续只推进 registry、coverage、RCAD 烟囱和 created-handle 回读，工程证据会变厚，但用户看到的 CAD 画面仍可能停留在矩形 smoke / 简单受控块阶段。

处理 / 结果：新增 `VCAD-01` 视觉表达 P0 包：`visual_cad_smoke` 绘制双线房间、门扇弧、两组工位、显示器/键盘、椅子、抽屉柜和工作区轮廓；真实 CAD 回读 54 handles，截图为 `output/previews/vcad-01-visual-office-corner.png`。随后新增 `VCAD-02` 视觉表达 P1 包：`visual_room_plan_smoke` 绘制分段双线墙、门窗、尺寸、文字、分区和更密家具，真实 CAD 回读 99 handles，截图为 `output/previews/vcad-02-visual-room-plan.png`。

以后规则：用户说“停止刷表 C / 推进 CAD 画面能力 / 图块太简单”时，优先做视觉表达包；最终汇报必须同时讲清楚视觉进步和表 C 不变，不能再用工程百分比替代 CAD 画面观感。

相关文件：`core/verification/visual_cad_smoke.py`、`scripts/run_visual_cad_smoke.py`、`core/verification/visual_room_plan_smoke.py`、`scripts/run_visual_room_plan_smoke.py`

### Fresh CAD evidence 不一定提升表 C 计数

日期：2026-05-27

现象：`V-PROOF-42-COMPOSITION-EXPAND` 真实 CAD 刷新 4 个 office composition case 后，registry writeback applied 4，但 coverage 机器值没有上升。

影响：如果只看“本轮跑了真实 CAD + applied 4”，容易误以为表 C 覆盖率必然提升；事实上这 4 个 capability 行此前已是 `verified`，本轮只是把 evidence path 刷新到新的 created-handle readback 报告。

处理 / 结果：明确记录 coverage 复跑值保持 `verified_count=112`、`showcase_count=25`、`cad_proof_count=137`、主指标 8.87%；任务台账可从 partial 到 done，但真实 CAD 实力百分比不虚报上涨。

以后规则：表 C 是否提升只看最新 `cad_capability_coverage.json`；registry writeback 的 applied_count 可能只是更新证据路径，不等于新增 verified/showcase 计数。涉及 `showcase` 行时还要避免默认 writeback 把 `showcase` 降成 `verified`。

相关文件：`scripts/run_composition_cad_registry.py`、`scripts/build_office_composition_writeback_batch.py`、`output/validation_runs/vproof-42-office-composition-expand-20260527-cad/composition_cad_registry_report.json`

### V-PROOF-41 真实 CAD 补验要区分沙箱 COM 不可见与真实 CAD 几何失败

日期：2026-05-27

现象：推进 `V-PROOF-41-BLOCK-CAD-MATRIX` 时，普通沙箱命令下 `scripts/run_block_alpha_beta_suite.py --connect-cad` 在创建 driver 前失败，报 `No active AutoCAD.Application instance is available`；同一会话中 CAD-MCP 可写 `CODEX_PREVIEW`，说明 CAD 本体可操作。
影响：这不是 001/002 几何失败，也不是 CAD_PLAN 失败，而是沙箱/权限边界导致 AutoCAD COM active object 不可见；若不区分，会把环境阻塞误判为绘图失败。
处理 / 结果：经用户允许在沙箱外访问已打开的 AutoCAD COM 后，重跑同一双块 suite 通过：`output/validation_runs/vproof-41-block-cad-matrix-20260527-cad/block_alpha_beta_summary.json` 为 2/2 `geometry_verified`，handles `61F` / `627` 均回读为 `block_reference`；`block.library.controlled_test_block_002` 已回写 verified。
以后规则：真实 CAD matrix 包必须把“active COM 可见性 / 权限边界”与“几何回读失败”分开记录；无 created-handle readback 时不得声称 `geometry_verified`，但沙箱内 COM 不可见时可请求合规提权复跑。
相关文件：`examples/plans/block_cad_matrix_vproof_41.json`、`scripts/run_block_alpha_beta_suite.py`

### Runner 内部相对路径要先归一到 project root

日期：2026-05-27

现象：推进 `V-PROOF-40` 时，`run_block_matrix_registry_sync.py --output output/...` 传入相对路径，内部直接对 `output_root.relative_to(project_root)` 求相对路径，导致 `ValueError`。

影响：证据已经可以生成，但 CLI 入口会因为路径形式失败，容易误判为 registry sync 或 block matrix 证据失败。

修复 / 计划：`run_block_matrix_registry_no_cad_sync()` 现在先把相对 output 解析到 project root 下，再进行 registry binding；新增 focused 回归测试覆盖相对 output。

以后规则：runner 接收 CLI 路径时，进入核心逻辑前应统一转换为 project root 内的绝对路径，再输出相对 evidence path。

相关文件：`core/block_engine/block_matrix_registry.py`、`tests/core/test_rblock_07_block_matrix_registry_rows.py`

### Hatch 已有受控 smoke，但不能扩大到任意填充

日期：2026-05-27

现象：`RCAD-06-HATCH` 已在真实 AutoCAD 会话中完成一组 ANSI31 矩形 hatch smoke，created handles 回读到 `hatch=1` 与 `polyline=1`，并把 `primitive.hatch` 从 `deferred` 回写为 `verified`。但该证据只覆盖受控闭合矩形边界、preview 图层和单一 hatch pattern。

影响：如果把这次 smoke 扩大理解为任意 hatch 已可用，会误报孤岛 hatch、复杂边界、正式图层填充、项目标准填充或任意 CAD_PLAN hatch 的几何准确性。

修复 / 计划：`docs/verification/hatch_com_deferred_boundary.md` 已改为同时记录 real COM verified 与 fake/no-CAD deferred 两层边界；最终口径固定为“受控 ANSI31 preview smoke 已 verified，任意 hatch 仍未证明”。

以后规则：hatch 能力扩样必须逐项增加 created-handle readback 证据；fake driver、no-CAD deferred、截图和顶层 pass 都不能替代真实 AutoCAD entity readback。

相关文件：`core/cad_io/autocad_com.py`、`core/verification/hatch_cad_smoke.py`、`docs/verification/hatch_com_deferred_boundary.md`

### RCAD 烟囱里也可能包含 non-CAD rollup

日期：2026-05-27

现象：`RCAD-28-BETA-EVIDENCE-ROLLUP` 属于 §5 CAD 补验台账，但其既有设计是 BETA-CAD-BLOCK 父包 evidence rollup，不连接 AutoCAD、不新增 created handles。若只看 RCAD 计数，很容易误以为 28/29 都是几何补验。

影响：RCAD 烟囱完成度会接近 97%，但表 C 主指标仍为 4.26%；把这个 rollup 当成真实 CAD `geometry_verified` 会再次混淆工程节奏、任务台账和真实 CAD 实力。

修复：为 `cad_beta_evidence_rollup` 补齐 `evidence_trend/cad_beta_evidence_rollup_trend.json`，并在测试中固定 `non_cad_only=true`、`geometry_verified_count=0`、`dry_run_valid_plan_only_count=5`。

以后规则：RCAD 台账状态可以说明补验包跑完，但是否提升真实 CAD 几何必须看 `geometry_verified_count`、created handles 和 registry/showcase 回写。non-CAD rollup 不提升表 C。

### 治理测试不要滞留旧进度断言

日期：2026-05-27

现象：推进 `RCAD-27` 的 no-CAD 兼容矩阵时，`baseline_cad_validation` 内的全量单测失败；根因不是 CAD 几何，而是 `tests/core/test_planmd_governance.py` 仍断言 `CORE_STATUS.md` 包含旧的 `94%`，当前状态页已更新为 `95%`。

影响：这类旧快照断言会把文档进度同步误报为 regression，阻塞真实 CAD 补验矩阵；如果只看顶层 fail，容易误判为 CAD runner 或几何链路坏了。

修复：将治理测试断言同步为当前 `CORE_STATUS.md` 的 `95%`，随后 no-CAD local regression 8/8 通过，真实 CAD strict 复跑 9/9 `geometry_verified_case_count`。

以后规则：状态页进度发生合法更新时，同步检查治理测试里的硬编码进度值；更好的后续方向是让测试验证“存在固定四进度口径与禁止混用声明”，而不是过度绑定某个历史百分比。

### block 旋转 bbox 不能用宽深互换近似

日期：2026-05-27

现象：`RCAD-24-BLOCK-ALPHA-BETA` 第一次真实 CAD 补验时，8 个 case 中 5 个通过，`beta_rotation_45`、`beta_rotation_90`、`beta_combined_transform` 失败；created handles 和 block reference 回读存在，但 bbox 检查不通过。

影响：如果继续沿用 dry-run 近似 bbox，会把旋转 block 的几何预期写错，真实 CAD 回读会持续失败；更危险的是，若放宽 bbox 检查，可能错把旋转几何当成已证明。

修复：`core/block_engine/block_placement.py` 改为围绕 insertion point 旋转 block 四角后计算外包框；`tests/core/test_block_engine.py` 与 `tests/core/test_block_alpha_beta_suite.py` 增加/更新对应验证。修正后真实 CAD 复跑 `RCAD-24` 8/8 `geometry_verified`。

以后规则：block / symbol / component 只要涉及旋转，bbox 预期必须按 CAD 实际变换计算；不得用“宽深互换”或非右角近似替代 created-handle readback 的几何断言。

相关文件：`core/block_engine/block_placement.py`、`core/verification/block_alpha_beta_suite.py`

### 诊断探针标注不能污染用户可见生成层

日期：2026-05-27

现象：用户在 AutoCAD 视口中看到大号 `CAD_CAPABILITY_PROBE` 文字和尺寸/箭头残留，容易判断为“生成图块仍然带标注”。回读证据显示最近的图块插入只创建 `block_reference`，但旧探针对象与当前生成结果混在同一 `CODEX_PREVIEW` 层，造成视觉污染。

影响：后续推进表 C 时，机器报告可能按 created handles 通过，但用户看到的 CAD 现场不干净，形成“证据通过、视口不可信”的落差。

修复：新增 `CODEX_DIAGNOSTIC` 诊断层，允许能力探针 / benchmark 在 preview-only 安全边界内验证文字和尺寸能力；探针几何仍写入 `CODEX_PREVIEW`，文字和尺寸写入 `CODEX_DIAGNOSTIC`，报告分开统计预览层与诊断层。诊断层写入必须显式 `layer_role="diagnostic"`，默认 preview 角色写诊断层会被 guard 拦截。

以后规则：用户可见生成结果默认纯几何。测试文字、尺寸、箭头、说明只属于诊断层或临时对象；截图和交付口径必须区分当前 created handles、预览层和诊断层，不得把诊断残留当成图块交付结果。

### 普通最终回复默认不附进度表，状态查询再展开表 C

日期：2026-05-27；更新：2026-05-28

现象：每轮交付强制输出完整表 A/B/C 后，信息量变大但思考价值下降，容易让真正关键的“本轮做了什么、有没有证据、真实 CAD 实力有没有变化”被表格淹没。

影响：后续 Agent 可能机械复制三表或精简表，造成普通问答里表格噪声过高；如果状态查询又为了省字数漏掉表 C 主指标，则工程进度 / RCAD 烟囱完成度仍可能被误读成真实 CAD 能力。

修复 / 计划：2026-05-27 先从完整三表改为 1 张精简进度表；2026-05-28 根据用户反馈继续收紧为：普通最终回复默认不附进度表、表单或表 A/B/C，只有用户点名开发状态查询、进度盘点、完整状态、交接、审计、表 A/B/C、表 C 或真实 CAD 实力时才展开表格。此变更只改展示口径，不重构 §3 / §4 / §5 的真实任务分母。

以后规则：无表格不是删除证据。普通回复仍要说清本轮完成、验证和风险；状态查询或真实 CAD 能力汇报必须以 coverage JSON、created handles 回读和 `geometry_verified` 为准，并先报表 C 主指标。handoff、状态页和能力模板保留完整证据结构。

### 表 A/B/C 数字必须以机器值和任务台账为准

日期：2026-05-27

现象：`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`docs/status/current.md` 与 `docs/planning/任务清单.md` 同时保留了 `0%`、`48.85%`、`49.24%`、`4.55%`、`4.35%` 等不同时间点快照，且 RCAD 烟囱也有 `21/29` 与 `22/29` 两套说法。

影响：后续 Agent 可能用旧 Markdown 数字覆盖最新机器报告，或把 RCAD / 工程进度误当成真实 CAD 实力。

修复 / 计划：收尾时复跑 `scripts/run_capability_coverage.py`，把表 C 同步为 `130/276 = 47.10%`、主指标 `4.35%`、最高 `L4`；把任务台账同步为 §3 `24/43`、§4 约 `42/55`、§5 `22/29`。

以后规则：表 C 一律以 `output/validation_runs/capability-lab/cad_capability_coverage.json` 为准；历史 changelog 数字只作为当时快照。任务 next 若冲突，先按 `CORE_RESTRUCTURE_PLAN.md` 的决策边界修正 `docs/planning/任务清单.md`，再汇报。

### 临时文件清理失败不应掩盖已完成的模型构建

日期：2026-05-27

现象：全量自检时，当前沙箱对 `tempfile` 创建的随机临时目录/文件可能返回 `PermissionError`，导致 `shell_confirmation.py` 在 `temp_path.unlink()` 清理阶段失败；此时 SHELL_MODEL 已经成功构建，失败点只是临时文件清理。

修复：`apply_shell_drawing_read_confirmation()` 保留原有临时 JSON round-trip，但在 finally 清理时捕获 `PermissionError`，避免把清理失败误报为业务转换失败。

以后规则：临时文件用于内部 round-trip 时，业务结果与清理结果要分层；清理失败可以记录或忽略，但不能覆盖已经完成的验证/转换结论。

### 真实 COM 写入守卫必须在 Add* 前触发

日期：2026-05-27

现象：负向安全复核发现 `AutoCADComDriver.draw_line()` 等方法曾在 COM `AddLine/AddCircle/...` 之后才调用 preview-layer guard；这会造成正式图层负向 case 虽然抛错，但实体可能已经被创建到当前 DWG。

修复：`AutoCADComDriver` 的 line / rectangle / circle / arc / polyline / text / dimension 写入均改为先执行 `_guard_preview_layer_write(layer)`，再调用 COM `Add*`；新增 `negative_cad_runner` 报告 no-handle/no-save/no-delete/no-formal-layer 证据。

以后规则：任何真实 CAD 写入入口都必须先做权限、图层、路径、ActiveDocument/snapshot 预检，再执行 COM 写入；负向 runner 的 `created_handles=[]` 和 modelspace delta 不能省略。

### 根目录 MD 历史权重过高

日期：2026-05-26

现象：旧 `CAD_AGENT_CHANGELOG.md`、旧 `CAD_AGENT_ISSUES.md`、`CORE_RESTRUCTURE_PLAN.md`、旧 `CAD_AGENT_STATUS.md` 等根文档曾持续累积已完成流水，每轮恢复上下文时噪声过高。

修复：创建 `docs/history/snapshots/root-md-2026-05-26/` 保存压缩前完整快照；根目录改为当前摘要、活跃队列、证据索引和风险边界。

以后规则：旧完成记录不要重新复制回根目录；需要追溯时展开 `docs/history/`。

### 场景成熟度口径容易误读

日期：2026-05-26

现象：已有 `office`、`residential`、`restaurant` 的 preferences、Scene Alpha 验收和 scene beta benchmark，容易被误读为具体场景 Agent 已完成。

修复：新增 `docs/architecture/core-scene-agent-boundaries.md`，统一 `Core 底座`、`Scene Alpha 壳层`、`Scene Beta 能力包`、`Scene Product 场景产品` 四级成熟度。

以后规则：没有真实项目样本、图块策略、真实 CAD readback 和用户确认流，不得称为 Scene Product。

### 本地真实 CAD 校验样本仍不足

日期：2026-05-26

现象：non-CAD 单测和 benchmark 较多，但真实 AutoCAD 用户会话下的 `geometry_verified` 样本仍有限。

修复 / 计划：唯一 `PlanMD` 已登记 `LCAD-01` 到 `LCAD-11`。当前 `LCAD-01`、`LCAD-02` 和 complex smoke 已完成，下一步推进 `LCAD-03`。

以后规则：任何新 CAD 能力没有 created handles readback 和 `geometry_verified` 时，只能写 deferred / non-CAD / fake-driver evidence。

### CAD 回归入口曾分散

日期：2026-05-26

现象：baseline validation、project sample check、composition check 曾经分散运行。

修复：新增 `core/verification/local_cad_regression.py` 和 `scripts/run_local_cad_regression.py`，支持 manifest、selected case、strict rollup 和 no-CAD deferred。

以后规则：进入下一阶段或做本地 CAD 回归时，优先跑 local CAD regression 矩阵。

## 不再高频展开的历史问题

以下问题仍可追溯，但不在根目录全文展开：

- 默认沙箱身份看不到用户会话 AutoCAD COM 活动对象。
- AutoCAD COM 点参数需要 `VT_ARRAY`。
- 顶层 validation pass 不能替代 readback `geometry_verified`。
- block alpha 失败路径必须先拒绝再写入。
- Windows / PowerShell 编码会影响中文路径和 JSON 输出。
- `sys.path` 注入、系统 temp、路径越界和 schema registry 缺口。
- blank-shell 早期几何、placement、zone、benchmark 和 workflow schema 问题。

完整条目见 `docs/history/snapshots/root-md-2026-05-26/CAD_AGENT_ISSUES.md`。

## 记录模板

新增问题按这个短格式写，避免再次膨胀：

```markdown
### 问题：一句话概括

日期：YYYY-MM-DD

现象：发生了什么。

影响：为什么危险。

修复 / 计划：已经做了什么，或下一步在哪里登记。

以后规则：后续如何避免。

相关文件：`path`
```
### 问题：资产复用和线型表验收不能只靠 prompt 或报告自证

日期：2026-06-02

现象：线型表反馈暴露了多类根因：临时布局策略可能被误当硬规则，弱语义匹配可能误复用资产，registry 中文若坏掉会污染匹配，线型表的无填充 / 样线不越格 / 自适应行高如果只写在报告字段里，可能被“自证通过”掩盖真实几何问题。

影响：系统资产越多，误触发、误排序、候选资产冒充 verified、样式标准误做 block、表格视觉问题复发的概率越高。

修复 / 计划：新增 `core.assets.semantic_rules`、复用前 registry `encodingPreflight`、稳定候选排序和 `core.training.linetype_table_audit`；线型表可变行数和样线 containment 已进入单测。后续对象资产继续按同一语义规则库和审计器模式扩展。

以后规则：资产复用 / 沉淀 / 线型表 / 局部修复先看机器语义规则和编码门禁；报告字段不能替代实体 readback 审计；弱匹配不得自动复用。

相关文件：`core/assets/semantic_rules.py`、`core/assets/system_asset_reuse.py`、`core/training/linetype_table_audit.py`、`tests/core/test_semantic_asset_rules.py`

### 问题：视觉检索 V0 仍受 AutoCAD 快照和截图画像边界限制

日期：2026-06-02

现象：当前 V0 能用“截图里的三人沙发”语义画像快速把 `5S03232` 排到第一，两次真实 CAD 只读自测端到端为 `4.165127s` / `3.682856s`，但真实耗时主要消耗在 AutoCAD `snapshot_modelspace`，且没有接入真正的图像 embedding 或跨文件缩略图索引。首次沙箱外 COM 调用还出现过 “被呼叫方拒绝接收呼叫”，重试后通过。

影响：如果未来图库很大，仍不能依赖当前 DWG 快照或逐 DWG 打开扫描；截图视觉判断也不能被误说成真实尺寸证明。

修复 / 计划：本轮新增 `visual-cad-asset-retrieval` V0，明确视觉/语义负责召回排序，CAD readback 负责最终确认。后续 V1 应增加离线 thumbnail / manifest / embedding 或 perceptual hash 索引，减少实时 AutoCAD COM 扫描。

以后规则：图库检索不得默认全量扫描线弧构造；先用视觉画像和索引召回 Top-K，再对少量候选做 CAD readback。任何截图相似度都不得替代 `handle`、`block_name`、`bbox`、图层和必要几何回读证据。

相关文件：`core/visual_retrieval/cad_block_retrieval.py`、`scripts/run_visual_block_retrieval.py`、`openspec/changes/visual-first-cad-asset-retrieval/`

### 问题：当前 DWG 快任务缓存需要防止被误当最终 CAD 证明

日期：2026-06-02

现象：`quick-composite-cad-task-cache` 已让同一 DWG 内的“找对象 + 标 bbox 尺寸”从 live snapshot dry-run `1.084232s` 降到 cache dry-run `0.002923s`，但 cache 只是轻量 block refs 候选源，可能随用户移动 / 删除 / 替换块而过期。

影响：如果后续把缓存结果直接当作几何证明，可能在 DWG 已变化时标注到旧 handle 或旧 bbox。

修复 / 计划：cache 仅允许作为候选召回来源；执行写入前仍需 active CAD readback / handle 验证，报告必须写 `candidate_source`、`cache_status` 和安全字段。跨文件图库索引另开 V1，不把当前 DWG cache 误说成 embedding。

相关文件：`core/visual_retrieval/current_dwg_cache.py`、`core/quick_tasks/find_and_annotate.py`、`scripts/run_quick_composite_task.py`
## 2026-06-02 真实中文“试一下”与多焦点视口可能误导旁边解析

现象：如果直接用单字“上 / 下”解析方向，`试一下`、`看一下` 这类自然口语里的“下”可能被误判成“下方”；如果当前视口里有多个分离对象而没有 selected / recent handles，旧逻辑可能把所有可见对象合并成一个大 bbox，导致“旁边”锚点并不像设计师眼睛真正关注的对象。

影响：Agent 会显得“执行了”，但实际不是按人的视觉焦点在画；尤其在 CAD 视口里有多个标准块、样例块、家具块时，旁边可能被解释成某个大合并框的边缘，而不是用户脑中那个对象旁边。

修复 / 计划：`placement_resolution` 已新增 `phrase_analysis`，方向词改为真实中文短语解析；上下方向避免单字误触；可见内容 fallback 新增聚类与评分，多个分离且势均力敌的焦点会返回 `needs_confirmation` 和候选锚点，不再强行落图。

以后规则：没有明确 target、selected handles 或 visible recent handles 时，Agent 必须先判断当前视口焦点是否唯一；焦点不唯一就请用户选择或说明方向，不得靠全局空白、全视口合并 bbox 或后续 zoom/pan 来伪装“旁边”。
### 问题：中文 CAD 绘图 payload 经 PowerShell 管道会乱码，临时 COM 脚本也可能绕过流式演示

日期：2026-06-02

现象：线型表第一次用内联 PowerShell here-string / stdin 方式运行 Python，中文字符串进入 Python 前被替换成 `????`；后续虽然用遮罩重画了中文版本，但实体回读仍能发现旧问号文字残留。另一个问题是临时直接 COM 脚本没有接入 `StreamingCadDemoRecorder`，用户看起来像所有图像一次性出现。

影响：如果后续继续用内联脚本承载中文标注、中文路径或中文 CAD 文本，同类乱码会复发；如果临时脚本绕过 recorder，用户可见 CAD 演示会退回批量写入，和训练期“流式展示”的预期不一致。若验收只看截图或 bbox 内所有文字，还可能被旧残留污染判断。

修复 / 计划：新增 `core/training/linetype_table_demo.py` 和 `scripts/draw_linetype_table.py`，把线型表演示固化为 UTF-8 文件 / 模块 payload；写前检查可见文本，写后只按本次 created handles 精确回读，并检查 `?` 与英文字母残留。脚本入口默认启用 `StreamingCadDemoRecorder`，逐行记录流式事件。

以后规则：含中文的 CAD 绘图 payload 不得通过 PowerShell 管道或临时 stdin 脚本传输；必须走 UTF-8 文件 / JSON / 模块入口。用户可见 CAD 演示默认接入 streaming recorder，除非明确是后台批处理或用户要求快速无流式。验收优先使用本次 created handles 精确回读，不用 bbox 内所有对象替代。

相关文件：`core/training/linetype_table_demo.py`、`scripts/draw_linetype_table.py`、`tests/core/test_linetype_table_demo.py`

### 问题：Codex 沙盒桌面会看不到用户可见 AutoCAD，角度尺寸名称也可能被误分成线

日期：2026-06-03

现象：用户已打开 `Autodesk AutoCAD 2026 - [Drawing2.dwg]`，但普通 shell 线程枚举窗口和 `GetActiveObject` 均失败；探针显示线程桌面为 `CodexSandboxDesktop...`，输入桌面为 `Default`。尺寸样式训练中还发现 `AcDb2LineAngularDimension` 因名称包含 `Line`，被旧回读逻辑误判为普通 `line`。

影响：真实 CAD 明明可见时 Agent 会误报“检测不到”；截图、COM 连接、readback 都可能失败。若尺寸回读分类顺序不严，角度标注可能被漏算或被错误审计为通过。

修复 / 计划：真实训练入口和 `render_preview.py` 已在 Windows 上先 `OpenInputDesktop` / `SetThreadDesktop`；`inspect_dwg.normalize_com_entity` 改为先识别 `dim`，再识别 `line`；尺寸样式训练审计要求期望尺寸句柄必须回读为 `dimension`。

以后规则：遇到可见 AutoCAD 但 COM / 窗口枚举失败时，先检查 window station / thread desktop / input desktop，不再默认认为用户没打开 CAD；CAD 对象类型归一化中，Dimension 类必须优先于 Line / Arc / Circle 等名称子串判断。

相关文件：`scripts/run_dimension_style_training.py`、`core/verification/render_preview.py`、`core/verification/inspect_dwg.py`、`core/training/dimension_style_training.py`

### 问题：快照瘦身成功后，训练事实源和 coverage 证据链仍会阻断同步

日期：2026-06-03

现象：`capability-map-data.js` 已从多 MB / 多万行派生快照瘦到 compact 1 行，legacy aliases 已移除。后续小修已把 13 个指向缺失历史 output 的 active `fact_source` 改为 `archived` 并保留 `archiveReason`，`scripts/sync_training_workbench.py` 和 Agent check 已恢复 pass；但 `scripts/run_data_bloat_audit.py --summary-only` 仍返回 `blocked`，剩余原因是 coverage `evidence_path_audit.report_path_missing=303`。

影响：如果只看工作台页面能否打开或快照大小，就会误判系统健康；如果为了让同步变绿而把缺失事实源改成 derived、删除引用或生成空报告，会把“证据链断裂”伪装成“治理完成”。当前 active training fact source 已闭合，但表 C registry 的历史 showcase 证据路径仍不可复盘。

修复 / 计划：A0 data-bloat audit 已只读报告 `protected`、`derived`、`candidate`、`blocked`；active fact_source 缺失、派生快照误登记 fact_source、coverage report path missing 都会 hard block。`DATA-BLOAT-EVIDENCE-CLOSURE-01` 已完成训练事实源归档修复；剩余 303 条 coverage 缺口应另开表 C 证据包，恢复 / 重跑历史 evidence reports，或审查后降级不再具备证据的 registry claims；不得用空 stub 或页面快照替代真实报告。

以后规则：防膨胀第一步先看 A0 blocked，而不是先清 output 或改快照；`capability-map-data.js`、sync report、retention report、data-bloat audit report 只能是 derived / diagnostic，不得作为训练 fact_source。

相关文件：`core/maintenance/data_bloat_audit.py`、`scripts/run_data_bloat_audit.py`、`docs/training/training-sources.json`、`output/validation_runs/capability-lab/cad_capability_coverage.json`

### 问题：尺寸样式训练不能靠数量凑差异，AutoCAD 箭头块读回还会本地化

日期：2026-06-03

现象：尺寸样式第一次真实落图虽然 10/10 机器审计通过，但用户指出许多标注视觉差异不够本质，建筑标记比例偏大。后续重训中还发现 AutoCAD 会把 `_ARCHTICK`、`_DOTSMALL`、`_NONE` 读回为本地化名称“建筑标记 / 小点 / 无”，fake driver 又没有 `DIMBLK` readback，导致审计可能把缺失读回或本地化读回误判为失败。PowerShell 默认编码读取 UTF-8 JSON 时也可能把中文报告读成 mojibake，引发 `ConvertFrom-Json` 假失败。

影响：如果只增加样式数量，会把颜色、箭头和位置变化误当底座能力提升；如果不处理本地化 DIMBLK 和编码读报，真实 CAD 通过 / 失败判断会不稳定。

修复 / 计划：本轮改为 10 个 canonical 样式 + 30 个比例 / 跨度样例，建筑 tick 的纸面箭头尺寸收敛到 1.2–1.7；审计新增 `scaleVariantCount` 和 duplicate fingerprint 检查，并对 `_ARCHTICK` / `_DOTSMALL` / `_NONE` 的中文读回做归一化，fake driver 缺少 `DIMBLK` 时不再误判。用户复核发现 06 标高符号比例样例越框后，新增 `panelHandlesByStyle` / `panelBoundsByStyle` / `panel_containment` 审计，后续面板对象 bbox 越框会直接 fail。用户继续指出 06 不像常规尺寸样式后，经设计师 / 训练架构 Agent 复核，已确认标高符号应归为 `annotation_symbol_style.level_marker`，不应计入 dimension style；本轮用真实尺寸实体的“室内-洞口宽高尺寸”替换 06，并把 r3 作为新的真实 CAD 通过证据。

以后规则：尺寸样式复训优先补比例泛化、用途语境和读回契约，不盲目横向堆名称；样例必须检查本面板 containment，不能只看尺寸句柄读回；AutoCAD 变量读回需要考虑本地化显示名；读取含中文 JSON / 报告时优先用 UTF-8 文件入口或 Python 明确编码，不用默认 PowerShell 解码结果下结论。标高符号、轴号圆圈、孔心十字等可作为样例上下文或符号资产，但不能替代 dimension entity readback 计入尺寸样式库。

相关文件：`core/training/dimension_style_training.py`、`scripts/run_dimension_style_training.py`、`tests/core/test_dimension_style_training.py`

### 问题：截图规则只改生成合同会被工作台同步覆盖

日期：2026-06-03

现象：截图编排规则最初写入 `agents/COMMON_PROMPT_CONTRACT.md` 后，`scripts/sync_training_workbench.py` 在 learning promotion 阶段会重新生成共用 Prompt 合同，导致新加的截图章节被旧的 `COMMON_PROMPT_GUIDANCE` / `POSITION_FEEDBACK_PROMPT_GUIDANCE` 源头覆盖。Agent check 因此报告 `screenshot_orchestration_rules_in_common_contract` 缺少 `截图编排`、`target_handles`、`repair_plan`、`PrintWindow` 和 `visual_aid_only` 等短语。

影响：如果只改最终生成文件，各 Agent 的截图理解会在下一次训练工作台同步后漂移，后续仍可能退回“截整个 CAD 当前窗口”，或者在单项修复复验时没有传局部 handles / repair plan。

修复 / 计划：已在 `core/training/learning_promotion.py` 增加 `SCREENSHOT_ORCHESTRATION_PROMPT_GUIDANCE`，并让 `_common_prompt_contract()` 生成“截图编排规则”章节；`scripts/run_training_workbench_agent_check.py` 继续强制检查共用合同短语。正式 `scripts/sync_training_workbench.py` 已通过，Agent check 40/40 pass。

以后规则：凡是要让所有 Agent 长期理解的共用规则，必须同时修改生成源和生成结果，并运行工作台同步；不得只手工编辑 `agents/COMMON_PROMPT_CONTRACT.md` 或单个 `prompt_addendum.md` 后就声称规则已沉淀。

相关文件：`core/training/learning_promotion.py`、`agents/COMMON_PROMPT_CONTRACT.md`、`scripts/run_training_workbench_agent_check.py`、`scripts/sync_training_workbench.py`

### 问题：尺寸样式局部错误会被整批重画入口放大

日期：2026-06-03

现象：用户只指出 06 尺寸样式面板不舒服，但旧训练入口只有“读取 cleanup report 的全局 `createdHandles` 并整批重画 10 个样式”的路径。虽然 r2/r3 报告已经记录 `panelHandlesByStyle` 和 `panelBoundsByStyle`，执行脚本没有消费这些字段，导致单格修复会被放大成整批重训。

影响：局部反馈会制造画布噪声，增加误删 / 重画范围，也让 Agent 给用户的“只修这一项”承诺缺少机器边界。

修复 / 计划：`scripts/run_dimension_style_training.py` 已新增 `--only-style`，局部 cleanup 只删除目标样式的 `panelHandlesByStyle`，并把 `panelBoundsByStyle` 传入 `run_dimension_style_training(..., only_style=..., panel_bounds_override=...)` 原位重画。缺少 panel handles 或 bbox 时 fail，不静默扩大为整批。真实 CAD smoke 已验证 06 只删除 56 个旧 handles 并重画 56 个新 handles。

以后规则：训练脚本如果报告里已有 panel / item / target handles，局部修复必须优先消费这些精确证据；只有证据缺失、句柄失效或布局根因全局错误时，才允许整块重画，并且重画前必须说明原因。

相关文件：`core/training/dimension_style_training.py`、`scripts/run_dimension_style_training.py`、`tests/core/test_dimension_style_training.py`

### 问题：尺寸样式机器审计通过但 05/06 视觉仍贴线、样例过小

日期：2026-06-03

现象：05/06 面板局部修复报告已 pass，但用户截图复核后指出观感仍像没修：06 横向 `900` 顶到完成面，右侧比例样例文字和数值过小，05/06 视觉不够齐整。第一次二次修复又把主示例整体上提过头，导致顶部轮廓接近标题区。

影响：如果只看 `dimensionReadbackCount`、`failedStyleCount=0` 和截图存在，就会把“实体正确”误当“视觉已可验收”；用户会看到同一类 bug 反复出现，尤其在 AutoCAD 自动调整 dimension text position 时，单纯改 text point 不可靠。

修复 / 计划：本轮把 05/06 主示例展示比例调整为 `2.4`，给标题区和底部说明区同时留白；06 横向尺寸线下移后用 bbox 回归断言确认 `900` 低于完成面；右侧比例样例改成固定大字号视觉示意，不再按真实跨度压缩。

以后规则：尺寸训练的“通过”必须同时看机器审计和局部截图；对用户指出的贴线、过小、越框、标题区挤压等视觉问题，要把对应 bbox / clearance / containment 转成回归测试或审计字段，不得只靠人工说“看起来好了”。

相关文件：`core/training/dimension_style_training.py`、`tests/core/test_dimension_style_training.py`

### 问题：PowerShell here-string 硬编码中文仓库路径会让资产报告路径变成问号

日期：2026-06-03

现象：尺寸样式资产 DWG 原生写入第一次用 PowerShell here-string 内联 Python，并在脚本里硬编码 `D:\工作文件\CAD-AGENT`；进入 Python 后路径变成 `D:\????\CAD-AGENT`，创建报告目录时报 `WinError 123`。该次失败发生在连接 / 写入 AutoCAD 前，没有保存 DWG。

影响：即便设置了 `PYTHONUTF8=1`，中文路径只要先在 PowerShell 命令字符串阶段损坏，Python 侧编码门禁也来不及修复；资产报告、CAD 文件路径或证据路径可能被错误写成 mojibake / 问号。

修复 / 计划：重跑时改用 `Path.cwd().resolve()` 获取仓库根目录，不在命令字符串中传递中文路径；系统资产 DWG 随后写入和保存通过。

以后规则：内联脚本、临时调试命令和资产原生写入不得硬编码中文绝对路径；优先从当前工作目录、已校验 JSON 或 UTF-8 文件读取路径。涉及中文路径的失败应先检查命令载体编码，而不是直接判断 CAD 或 Python 文件系统异常。

相关文件：`output/validation_runs/system-assets/dimension-style-standard-dwg/native_dimension_style_report.json`

### 问题：样式资产可被语义命中但复用计划被挡在 native source gate

日期：2026-06-03

现象：`interior_dimension_style_visual_standard` 已写入系统资产合同和 `standard_assets.dwg`，白话“调用室内洞口宽高尺寸样式，复用尺寸样式视觉标准”也能从 registry 命中该资产，但 `system_asset_reuse_workflow` 返回 `needs_precise_native_source`，没有生成可执行计划。

影响：这会造成“沉淀了但不能复用”的假闭环：系统理解力看起来通了，A-to-A 也可能以为资产可用，但执行链路仍被 native source gate 阻断。

修复 / 计划：复用器现在把 `style_standard + style_export + native_style_definition_written` 识别为 `sourceSpec.mode=style_definition`；registry 资产行补 `nativeDwgExists`；共用 Prompt 合同新增系统资产与样式复用规则，并由工作台 Agent check 锁定。

以后规则：样式资产不能靠 copying `CODEX_PREVIEW` 图元伪装复用；native style definition 已写入时可以生成 `style_definition` 计划，但真正跨 DWG 应用仍需 importer/readback gate。复用报告必须区分 `ready plan`、`style_reuse_deferred_cad_required` 和真正 `asset_reused`。

相关文件：`core/assets/system_asset_reuse.py`、`core/assets/system_asset_sedimentation.py`、`agents/COMMON_PROMPT_CONTRACT.md`、`output/validation_runs/system-assets/dimension-style-standard-dwg/reuse_workflow_probe.json`

### 问题：样式定义写入不等于模型空间可见资产，内联 JSON 更新也可能写坏中文

日期：2026-06-03

现象：尺寸样式资产沉淀后，用户打开 `standard_assets.dwg` 只看到线型表，没有看到尺寸样式面板。实际原因是上一轮只把 DimStyle / `CODEX_CN_TEXT` 写进 AutoCAD 样式定义，模型空间没有可见实体。后续补 registry / training source 时，内联 PowerShell 脚本又把新增中文约束写成 `????`，复用探针被 `asset_registry_encoding_failed` 正确阻断。

影响：如果把“样式表定义已写入”当成“系统资产 DWG 可人工复审”，资产库会出现看不见、无法验收的内容；如果 JSON 更新绕过编码门禁，registry 文本匹配和 A-to-A 复用会被坏中文阻断，甚至把错误事实源同步到工作台快照。

修复 / 计划：已在 `standard_assets.dwg` 模型空间追加尺寸样式可见面板，记录 325 个 created handles、44 个尺寸实体回读和聚焦截图；资产合同 / registry 补 `nativeVisiblePanelEvidence`。坏中文已用补丁修复，源码事实源和派生快照均扫空 `???`；复用探针复跑为 `status=ready`，registry `encodingPreflight=pass`。

以后规则：样式资产沉淀必须区分 `style_definition`、可见标准面板和跨 DWG import 三层证据；用户需要打开资产 DWG 复审时，不能只写不可见样式定义。含中文的资产合同、registry、training source 更新不得通过临时内联脚本写入；更新后必须跑 registry encodingPreflight 或等价复用探针，并扫描 `???` / mojibake。

相关文件：`libraries/system_library/drawing_standards/basic/assets.json`、`libraries/system_library/registry.json`、`docs/training/training-sources.json`、`output/validation_runs/system-assets/dimension-style-standard-dwg/native_visible_panel_r1/native_visible_panel_summary.json`、`output/previews/system-asset-dimension-style-visible-panel-r1-focused.png`

### 问题：系统资产沉淀与 A-to-A 联通曾只靠事后补强，缺少一次性门禁

日期：2026-06-03

现象：尺寸样式资产先经历“合同 / DimStyle 已写但 DWG 里看不见”，又经历“registry 能命中但复用计划 / A-to-A 联通还要二次加固”。这说明旧规则虽然有边界说明，但 `--verify` 仍主要验元数据，不能主动阻止 Agent 把半截沉淀说成完成。

影响：后续任何样式、文字、引线、线型或对象资产都可能复现同类问题：资产条目存在但系统资产 DWG 不可人工复审；或者 prompt / registry 能找到资产，但没有生成可执行 workflow、没有 `sourceSpec`、没有 readback 边界，导致“复用能力提升”只是表述。

修复 / 计划：已新增机器门禁：`native_style_definition_written` / `written_to_standard_assets_dwg` 的 `style_standard` 必须有 `nativeVisiblePanelEvidence` 或等价可见 native 证据；`verified` 资产必须有 `reuseWorkflowProbe` 或真实 `reuseReplay`。`verify_system_asset_package()` 缺证据会 fail，registry 行会透传两类证据，语义规则库、共用 Prompt 生成源和 Agent check 都锁定 `nativeVisiblePanelEvidence` / `reuseWorkflowProbe` 短语。

以后规则：系统资产交付前先跑 `scripts/sediment_system_asset.py --verify`，并读 checked / notChecked；不要只看资产是否在 registry。`reuseWorkflowProbe=ready` 只能说明 A-to-A 计划联通，不等于已 `asset_reused`；只有真实写入当前 DWG 并回读 created handles / `readbackStatus=ok` 才能称为已复用。

相关文件：`core/assets/system_asset_sedimentation.py`、`core/assets/semantic_rules.py`、`core/training/learning_promotion.py`、`scripts/run_training_workbench_agent_check.py`、`tests/core/test_system_asset_sedimentation.py`

### 问题：系统资产 DWG 视觉仓库验收只看结构 plan 会漏掉货架 / 内容重叠

日期：2026-06-03

现象：`standard_assets.dwg` 三列仓库上一轮报告显示 `visualRackPlan` 和 created-handle readback 通过，但用户截图复核仍能看到 A2 尺寸面板被青色 / 橙色框线和标签穿插，A1/A2 分区观感混乱。

影响：如果验收只检查“是否保存 DWG、是否有 v2 plan、是否创建了货架 handles”，就会把视觉上不可交付的仓库当成 pass；后续资产库可能继续按错误的分区线扩展，甚至把 label / frame 当成可复制源附近的正常内容。

修复 / 计划：`layout_system_asset_shelves.py` 已改为先回读非货架层上的保护资产内容，按 bbox 聚类 A1/A2，再用 `content_cluster_bbox_clearance_v1` 生成货架；SOURCE 边界和文字不再固定写入内容区。报告新增全量 `entityBboxes`、`protectedContentReadback` 和 `visualClearanceAudit`，任何货架实体 bbox 与保护内容 bbox 相交即 fail。治理脚本也必须读取最新 shelf 报告，确认 CAD readback 和 `overlapCount=0` 后才 pass。

以后规则：系统资产 DWG 货架 / 仓库验收不能只看 metadata、截图或 created handles 数量；必须同时检查保护内容 bbox、货架实体 bbox、clearance / overlap 审计、`savedAssetDwg=true` 和 `savedCurrentBusinessDwg=false`。用户指出排版错位时，先补机器门禁再改图，不得用“脚本通过”反驳截图。

相关文件：`scripts/layout_system_asset_shelves.py`、`core/assets/system_asset_library_governance.py`、`scripts/run_asset_library_governance_check.py`、`tests/core/test_system_asset_sedimentation.py`

### 问题：系统资产 DWG 零重叠仍可能视觉不可读

日期：2026-06-03

现象：上一轮 shelf/content clearance 已经做到 `overlapCount=0`，但用户截图复核仍能看到 A1/A2 过挤、通道不清、橙色 source 边界像是在框住 proof panel，整体不像可持续扩展的仓库。

影响：如果 Agent 只看 saved DWG、created handles、visualRackPlan v2 和 `overlapCount=0`，仍会把不可交付的仓库排版误判为通过；A-to-A 也会因为 reviewer 只输出泛化 pass 而放行。

修复 / 计划：新增 `visualReadabilityAudit` 和 Core `readability_report` 门禁，硬查 A1/A2、A2/B 通道，A1/A2 内容宽度占比，proof content 图层语义，source/proof 分离和非截图证据；A-to-A `visual_layout_review` 必须显式输出六个可读性字段。真实 CAD 重排已把 proof panel 从 `CODEX_PREVIEW` 迁到 `ASSET_PROOF_CONTENT`，A2 内容簇右移，`ASSET_SOURCE_BOUNDARY` 缩成 source token。

以后规则：系统资产 DWG 仓库验收必须同时有 `visualClearanceAudit.status=pass` 和 `visualReadabilityAudit.status=pass`；截图只是人工复审入口，不能替代 handles / bbox / readback / readability metrics。用户指出“排版乱”时，先补机器可读性门禁，再修布局。

相关文件：`scripts/layout_system_asset_shelves.py`、`core/assets/system_asset_library_governance.py`、`core/orchestrator/a_to_a_task_contract.py`、`agents/pipeline/visual_layout_reviewer/agent.json`、`agents/COMMON_PROMPT_CONTRACT.md`

### 问题：规则型 Agent 容易被误解为真实模型 Agent，视觉仓库“乱码感”也会漏过纯规则门禁

日期：2026-06-03

现象：用户复审 `standard_assets.dwg` 时指出 A2 尺寸 / 文字 / 引线标准在仓库总览里像乱码。只读调查显示中文编码本身通过，主要问题是 A2 proof panel 在总览中缩得过小、文本/尺寸密度过高，并且存在 `CODEX_PREVIEW` 遗留几何污染；同时用户追问系统里的 `pipeline_*` Agent 是否真的调用模型。

影响：如果仓库只保留角色名、schema 和规则门禁，容易让人以为每个 Agent 都有独立视觉理解；实际上大多数 Agent 只是契约型 / 规则型角色，能检查字段和阻断流程，但不能像当前 Codex 会话一样理解截图观感。纯规则门禁能抓 bbox、图层、overlap，却可能漏掉“整体像乱码、不可读、不像仓库”的视觉体验问题。

修复 / 计划：第一包已新增 `core/model_review` 和视觉 `modelBackedReview` 门禁，把 `codex.cmd exec` 作为本机只读模型复审桥；`pipeline_visual_layout_reviewer` 可在 workflow 要求时消费模型 JSON，失败则阻断 A-to-A。第二包仍需补全 layer census、A1/A2 内 `CODEX_PREVIEW` 污染阻断和证据文件存在性检查，并实际修复当前仓库排版。

以后规则：Agent 类型必须明确表达：契约型负责角色和输出，规则型负责可确定证据，模型型必须显式调用模型并产生 schema 化报告。模型复审不能写 CAD、不能保存 DWG、不能替代 handles / bbox / layer / sourceSpec / reuseReplay；但当视觉仓库验收出现“看起来乱、密、像乱码”时，应优先考虑模型型 reviewer 或人工复审，而不是只拿规则 pass 反驳视觉反馈。

相关文件：`CORE_RESTRUCTURE_PLAN.md`、`core/model_review/`、`core/orchestrator/a_to_a_task_contract.py`、`core/assets/system_asset_library_governance.py`、`agents/pipeline/visual_layout_reviewer/agent.json`、`agents/COMMON_PROMPT_CONTRACT.md`

### 问题：仓库治理只看 layerSamples 和 registry 引用，会漏掉 A1/A2 污染与断链证据

日期：2026-06-03

现象：A2 尺寸 / 文字 / 引线标准在仓库总览里有“乱码感”时，旧 `protectedContentReadback.clusters[*].layerSamples` 只取前若干实体图层；如果 `CODEX_PREVIEW` 污染对象不在 sample 窗口内，治理报告可能显示 proof content 已迁出预览层。另一个问题是资产合同、visible panel、reuse probe 和 evidence links 中引用的报告 / 截图可以已经不存在，但治理脚本仍只看 metadata 结构和 registry 条目。

影响：这会造成两类虚绿：一是仓库里实际仍混有训练 / 预览污染，却被 sample-only 报告漏过；二是资产看似有证据路径，实际文件缺失，后续训练工作台、复用审计和人工复审都断链。

修复 / 计划：已新增 `SYSTEM-ASSET-WAREHOUSE-GOVERNANCE-P2`。布局脚本输出 full layer census：`layers` / `layerCounts`；Core `audit_visual_rack_plan()` 接收 `protected_content_report`，sample-only fail，`CODEX_PREVIEW` / `ASSET_SOURCE_BOUNDARY` 进入保护内容即 fail。`run_asset_library_governance_check.py` 递归检查白名单证据字段引用的本地文件是否存在。

以后规则：系统资产仓库复审不得只用 `layerSamples`、截图或 registry 引用证明干净；必须看 full layer census、created handles/bbox、clearance/readability audit 和证据文件存在性。缺 latest shelf layout report 或缺 referenced evidence file 时，应先修证据链或重新生成，而不是继续声称资产库已治理通过。

相关文件：`scripts/layout_system_asset_shelves.py`、`core/assets/system_asset_library_governance.py`、`scripts/run_asset_library_governance_check.py`、`tests/core/test_asset_library_governance.py`、`agents/pipeline/visual_layout_reviewer/agent.json`
