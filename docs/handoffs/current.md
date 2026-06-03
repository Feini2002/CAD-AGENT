# 当前交接包窗口
## DATA-BLOAT-A0-A3-IMPLEMENTATION-01
1. **包名**：`DATA-BLOAT-A0-A3-IMPLEMENTATION-01`
2. **修改文件列表**：新增 `core/maintenance/data_bloat_audit.py`、`scripts/run_data_bloat_audit.py`、`tests/core/test_data_bloat_audit.py`；更新 `scripts/build_capability_map_data.py`、`capability-map.html`、`core/training/artifact_retention.py`、`scripts/run_training_artifact_retention.py`、`tests/core/test_training_workbench_sync.py`、`tests/core/test_training_artifact_retention.py`、`capability-map-data.js`、状态 / changelog / issues / handoff 索引。
3. **关键设计说明**：A0/A2 是只读审计，不删除、不归档，输出 `protected`、`derived`、`candidate`、`blocked`；active fact_source 缺失、派生快照误登记 fact_source、coverage `report_path_missing` 会 blocked。A1 默认 compact 单行快照，HTML 用 `normalizeWorkbenchData()` 兼容旧 aliases。A3 retention 仍只计划 / 归档旧图片，`.json` / `.dwg` / `.dwt` 显式 protected；`--write` 时写 relocation manifest、原路径、归档路径、hash、原因和恢复提示。
4. **新增/修改测试**：新增 A0 data-bloat audit 3 个回归；新增 A1 compact / HTML normalize 断言；扩展 A3 默认 roots、protected suffix 和 relocation manifest 测试。
5. **实际运行的命令和结果**：`python -m unittest tests.core.test_data_bloat_audit tests.core.test_training_artifact_retention -v` → 8 OK；A1 compact / normalize + A3 retention 目标测试 7 OK；`python scripts\build_capability_map_data.py` → wrote；`node --check capability-map-data.js` → pass；真实快照 1,361,055 bytes / 1 行；`scripts/run_training_artifact_retention.py --output ...` → pass、`candidateCount=0`、`protectedArtifactCount=16`、未归档；`scripts/run_data_bloat_audit.py --summary-only` → exit 1 / blocked；`scripts/sync_training_workbench.py` → exit 1 / Agent check 仅 `training_source_paths_exist` fail。
6. **是否运行真实 CAD**：否。本包只改审计、快照、retention 和文档；不连接 AutoCAD、不写 DWG、不保存当前图。
7. **机器可读证据路径**：`scripts/run_data_bloat_audit.py --summary-only` stdout；`output/validation_runs/training-artifact-retention/retention_report.json`；`output/validation_runs/training-workbench-sync/training_workbench_sync_report.json`；`capability-map-data.js`。
8. **结论分类表**：A0/A2 data-bloat audit 已落地（code + tests +真实 blocked 报告，geometry_verified=否）；A1 快照瘦身已落盘（1 行 compact，node check pass）；A3 retention dry-run / protected suffix / manifest 行为已落地（code + tests，未执行 write 归档）。
9. **剩余风险**：当前仓库证据链未闭合：13 个 active fact_source 缺失，coverage `report_path_missing=303`。这不是本包要自动修复的垃圾清理问题；后续必须恢复事实源或审查归档引用后再让工作台同步变绿。
---
## DATA-BLOAT-GOVERNANCE-BEFORE-TRAINING-01
1. **包名**：`DATA-BLOAT-GOVERNANCE-BEFORE-TRAINING-01`
2. **修改文件列表**：更新 `AGENTS.md`、`CORE_CONTEXT_BRIEF.md`、`docs/architecture/cad-agent-task-chain.md`、`docs/training/README.md`、`docs/governance/cad-agent-rules.md`、`agents/cad_designer/rules.md`、`agents/COMMON_PROMPT_CONTRACT.md`、`agents/pipeline/README.md`、`agents/pipeline/pipeline_manifest.json`、`core/maintenance/doc_governance.py`、`tests/core/test_doc_governance.py`、状态 / changelog / issues / handoff 索引。
3. **关键设计说明**：把训练前 / 收尾数据防膨胀从一次性讨论沉淀为系统规则和 A-to-A 共识。后续训练、复训、正式收尾型工作台同步、系统资产沉淀或仓库级治理产生 output / debug / test artifacts 前后，必须区分 `protected`、`candidate`、`blocked`、`derived`；相关 A-to-A 合同必须列 `data_bloat_governance` hard gate。`workbench_snapshot_refresh` 保持轻量查看例外；诊断报告和工作台快照不得反向成为训练事实源。
4. **新增/修改测试**：新增 `check_data_bloat_governance_manifest()` 和 2 个回归测试，确认 manifest task kind / hard gate / blocks / artifact 模板 / Agent README 覆盖不跑偏；总文档治理报告新增 `data_bloat_governance` 子项。
5. **实际运行的命令和结果**：`python -m unittest tests.core.test_doc_governance -v` → 29 OK；`python -m json.tool agents/pipeline/pipeline_manifest.json` → ok；`python scripts/run_doc_governance_audit.py` → pass，`finding_count=0` 且 `data_bloat_governance.finding_count=0`；关键 `rg` 规则检索命中；`git diff --check` 无 whitespace error（仅 CRLF warning）。
6. **是否运行真实 CAD**：否。本包不连接 AutoCAD、不写 DWG、不保存当前图；它只同步规则、Agent 合同和交接事实。
7. **机器可读证据路径**：`agents/pipeline/pipeline_manifest.json` 的 `required_hard_gates_by_task_kind` / `data_bloat_governance`；`core/maintenance/doc_governance.py` 的 `data_bloat_governance` 审计子项；`tests/core/test_doc_governance.py` 回归测试；无新增 `output/validation_runs/**` 证据。
8. **结论分类表**：训练前数据防膨胀治理已进入规则 / Agent / A-to-A 共识并纳入文档治理审计（docs + manifest + tests，geometry_verified=否）；compact 输出、data-bloat audit CLI、retention 扩展和真实清理写入尚未实现。
9. **剩余风险**：后续 A 包仍需实现 `scripts/run_data_bloat_audit.py`、compact / 去重输出和 retention 引用闭合检查；当前只保证后续 Agent 不会忘记这条门禁。
---
## ARCHITECTURE-DOC-HARDENING-02
1. **包名**：`ARCHITECTURE-DOC-HARDENING-02`
2. **修改文件列表**：更新 `README.md`、`docs/architecture/README.md`、`docs/architecture/current-module-boundaries.md`、`core/maintenance/doc_governance.py`、`tests/core/test_doc_governance.py`、`openspec/changes/architecture-boundary-hardening-01/tasks.md`、状态 / changelog / handoff 索引。
3. **关键设计说明**：统一架构链路为 `User Request -> semantic route -> A-to-A contract -> CAD_PLAN / asset workflow / training route -> execution -> verification -> promotion/sync`；补系统硬门禁索引和 Core / Agent 禁止边界；复用既有 completed OpenSpec change，不新开第二套主线。
4. **新增/修改测试**：`check_architecture_hardening_index()` 和 `test_architecture_hardening_index_flags_missing_tokens`，综合报告新增 `architecture_hardening` 子项。
5. **实际运行的命令和结果**：`python -m unittest tests.core.test_doc_governance -v` → 27 OK；`scripts/run_doc_governance_audit.py` → pass，`finding_count=0`。
6. **是否运行真实 CAD**：否。本包只改文档和治理审计，不连接 AutoCAD、不写 DWG、不保存当前图。
7. **机器可读证据路径**：OpenSpec 记录在 `openspec/changes/architecture-boundary-hardening-01/tasks.md`；审计输出来自 `scripts/run_doc_governance_audit.py`。
8. **结论分类表**：架构链路 / 模块边界 / 门禁索引已纳入机器文档治理（docs + tests，geometry_verified=否）。
9. **剩余风险**：本轮是“架构收口 + 轻量加固”，不迁移 `core/verification`、capability map 或具体 Core 模块。
---
## SYSTEM-ASSET-LIBRARY-GOVERNANCE-01
1. **包名**：`SYSTEM-ASSET-LIBRARY-GOVERNANCE-01`
2. **修改文件列表**：新增 `openspec/changes/harden-system-asset-library-governance/`、`core/assets/system_asset_library_governance.py`、`scripts/run_asset_library_governance_check.py` 和 4 个资产治理 Agent；更新 `core/orchestrator/a_to_a_task_contract.py`、`scripts/layout_system_asset_shelves.py`、`agents/pipeline/visual_layout_reviewer/agent.json`、`agents/COMMON_PROMPT_CONTRACT.md`、Prompt 生成源、系统资产协议、全局规则、状态 / changelog / issues / handoff 索引。本轮第三次纠偏新增 visual readability 硬门禁。
3. **关键设计说明**：显式“沉淀资产”先过 `pipeline_asset_governor`；`visualRackPlan` 不只验 v2 架构和 shelf/content clearance，还必须有 `visualReadabilityAudit`：A1/A2 与 A2/B 通道、内容密度、proof content 图层、source/proof 分离和非截图证据都要过关。A-to-A `visual_layout_review` 也必须输出同一组可读性字段，否则主 Agent 不能完成。
4. **新增/修改测试**：扩展 `tests/core/test_system_asset_sedimentation.py` 和 `tests/core/test_a_to_a_task_contract.py`，覆盖旧 reviewer 五字段 pass 被阻断、failed readability report、零重叠但 A1/A2 拥挤且 proof content 仍在 `CODEX_PREVIEW` 的负例。
5. **实际运行的命令和结果**：`python -m unittest -v tests.core.test_a_to_a_task_contract` → 6 OK；`python -m unittest -v tests.core.test_system_asset_sedimentation` → 27 OK；`scripts/run_a_to_a_orchestration_gate_check.py` → pass；`scripts/layout_system_asset_shelves.py --clear-all-shelf-layers` → status pass；`scripts/run_asset_library_governance_check.py --output output/validation_runs/system-assets/asset-library-governance/governance_check.json` → pass；`scripts/render_preview.py --check` → ready；`scripts/render_preview.py --capture-autocad-window ... --output output/previews/system-asset-warehouse-readability.png` → captured。
6. **是否运行真实 CAD**：是。打开 / 激活并保存 `libraries/system_library/drawing_standards/basic/standard_assets.dwg`；旧 proof panel 从 `CODEX_PREVIEW` 迁到 `ASSET_PROOF_CONTENT`，A2 内容簇按 handles 右移；新建货架 handles 219，`createdEntityReadback.status=ok`、`resolvedHandleCount=219`、`unmanagedLayerCount=0`、`visualClearanceAudit.status=pass`、`overlapCount=0`、`visualReadabilityAudit.status=pass`、`issueCount=0`、`savedAssetDwg=true`、`savedCurrentBusinessDwg=false`。
7. **机器可读证据路径**：`output/validation_runs/system-assets/asset-library-shelves/shelf_layout_report.json`、`output/validation_runs/system-assets/asset-library-governance/governance_check.json`、`output/previews/system-asset-warehouse-readability.png`；OpenSpec 契约在 `openspec/changes/harden-system-asset-library-governance/`。
8. **结论分类表**：系统资产库守门员已落地（agents + manifest + docs + tests，geometry_verified=否）；系统资产 DWG 货架脚手架已真实写入并保存（created handles + readback + clearance + readability audit + screenshot，geometry_verified=局限于仓库脚手架）；真实对象 block 复用 replay 仍按各资产单独证明。
9. **剩余风险**：本包证明 `drawing_standards.basic` 的可视仓库架构、本轮货架实体回读、shelf/content bbox clearance 和视觉可读性过关；对象资产 block 本体仍需进入各自分类 DWG。截图仍是 `visual_aid_only`，不能替代 handles / bbox / readback / audit。
---
## SCREENSHOT-ORCHESTRATION-HARDENING-01
1. **包名**：`SCREENSHOT-ORCHESTRATION-HARDENING-01`
2. **修改文件列表**：新增 `openspec/changes/harden-agent-screenshot-orchestration/`；更新 `core/verification/render_preview.py`、`core/verification/visual_cad_review.py`、`core/training/foundation_batch_training.py`、`core/training/learning_promotion.py`、`scripts/run_training_workbench_agent_check.py`、`agents/COMMON_PROMPT_CONTRACT.md`、相关单测、`capability-map-data.js`、Agent memory 派生文件、状态 / changelog / issues / handoff 索引。
3. **关键设计说明**：截图入口现在先生成 `screenshotDecision`，按 `target_handles`、`repair_plan`、bbox、`execution_summary.created_handles` 的顺序选择任务焦点；局部修复和 focused / formal 验收要求截图，快试且关键 readback 足够时可跳过。截图结果固定声明 `visualAidOnly=true`，不得替代 CAD readback 或 created handles。
4. **新增/修改测试**：新增截图 decision、runner payload、focused training preview payload、Agent 共用合同和工作台 Agent check 断言；补 learning promotion 测试，确保同步重写共用合同时不会丢失截图编排规则。
5. **实际运行的命令和结果**：`python -m unittest -v tests.core.test_render_preview tests.core.test_table_c_evidence_gate tests.core.test_cad_foundation_remaining_training tests.core.test_training_workbench_sync tests.core.test_training_learning_promotion` → 66 OK；`openspec.cmd validate --all --strict --json --no-interactive` → 12/12 pass；`scripts/render_preview.py --check` → ready；`scripts/sync_training_workbench.py` → pass，Agent check 40/40 pass。
6. **是否运行真实 CAD**：是。连接 `Autodesk AutoCAD 2026 - [Drawing2.dwg]`，只执行客户区 `PrintWindow` 截图和视图聚焦；未保存当前业务 DWG，未删除实体，未修改正式图层。
7. **机器可读证据路径**：`output/previews/screenshot-orchestration-target-1F7C.png`；`output/validation_runs/training-workbench-sync/training_workbench_sync_report.json`；`output/validation_runs/training-workbench-sync/agent_check.json`；OpenSpec 契约位于 `openspec/changes/harden-agent-screenshot-orchestration/`。
8. **结论分类表**：截图底座任务级编排已落地（code + tests + real AutoCAD capture，geometry_verified=否）；Agent 共用截图理解已同步（common contract + workbench Agent check，geometry_verified=否）。真实 CAD 几何能力未因本包提升，截图仍为视觉辅助。
9. **剩余风险**：本包证明截图可以聚焦单 handle 并在后台/非置顶情况下走客户区截图；后续如果要把更多 runner 接入自动截图策略，仍需逐入口传递 `target_handles` / `repair_plan`，并继续用 readback 证明几何准确。
---
## CAD-TRAINING-PROMOTION-GATE-01
1. **包名**：`CAD-TRAINING-PROMOTION-GATE-01`
2. **修改文件列表**：新增 `core/training/promotion_gate.py`；更新 `core/training/learning_promotion.py`、`scripts/run_training_workbench_agent_check.py`、`scripts/sync_training_workbench.py`、`tests/core/test_training_learning_promotion.py`、`tests/core/test_training_workbench_sync.py`、`docs/architecture/cad-agent-task-chain.md`、`docs/training/README.md`、`docs/governance/cad-agent-rules.md`、`docs/training/training-sources.json`、`capability-map-data.js`、Agent memory / prompt 派生文件、状态 / changelog / issues / handoff 索引。
3. **关键设计说明**：新增训练收尾 `promotionGate`：正式训练通过后必须机器声明训练事实源、工作台同步、Agent 校准、底座规则、单项规则、检查器和原任务回测七项决策；`quick_trial` 保持 `observation`，未知 `capabilityId` 不再 fallback 到 `cad_designer`，规则 / 检查器 delta 只进入 `needs_reviewed_package`。
4. **新增/修改测试**：新增 promotion gate、quick trial 负例、未知能力负例、规则 delta 候选、纠错候选 gate、工作台缺 gate 失败和 sync 报告 gate 字段测试。
5. **实际运行的命令和结果**：`tests.core.test_training_learning_promotion` 10 OK；`tests.core.test_training_workbench_sync` 15 OK；`scripts/sync_training_workbench.py --skip-coverage` pass，Agent check 39/39 pass。
6. **是否运行真实 CAD**：否。本包只改训练收尾、工作台同步和文档规则，不连接 AutoCAD、不写 DWG、不保存当前图。
7. **机器可读证据路径**：`output/training_learning/agent_learning_ledger.json`、`output/validation_runs/training-workbench-sync/training_workbench_sync_report.json`、`output/validation_runs/training-workbench-sync/agent_check.json`、`capability-map-data.js`。
8. **结论分类表**：训练 promotion gate 已落地（code + tests + workbench sync，geometry_verified=否）；A-to-A 校准机器决策已写入 ledger / workbench；真实 CAD 能力提升：未做。
9. **剩余风险**：promotion gate 能证明“是否需要沉淀 / 校准 / 回测”的机器决策存在，但不能替代 reviewed package 的规则质量审查，也不能证明视觉语义或原任务回测质量。
## CAD-AGENT-TASK-CHAIN-01
1. **包名**：`CAD-AGENT-TASK-CHAIN-01`
2. **修改文件列表**：新增 `docs/architecture/cad-agent-task-chain.md`；更新 `CORE_CONTEXT_BRIEF.md`、`docs/architecture/README.md`、`docs/training/global-agent-pipeline.md`、`docs/training/README.md`、`docs/governance/cad-agent-rules.md`、状态 / changelog / issues / handoff 索引。
3. **关键设计说明**：把执行编排链路和训练学习链路合并成系统默认任务链路：白话先做输入分流、语义拆分、单一子任务和责任分发；稳定失败或新能力再回流到训练 / 复训、原任务回测、底座规则、单一任务规则、检查器、Prompt / memory、A-to-A 校准和事实源同步。
4. **新增/修改测试**：无新增单测；使用文档治理审计和 diff 检查验收。
5. **实际运行的命令和结果**：`scripts/run_doc_governance_audit.py`、`git diff --check -- CORE_CONTEXT_BRIEF.md docs/architecture/cad-agent-task-chain.md docs/architecture/README.md docs/training/global-agent-pipeline.md docs/training/README.md docs/governance/cad-agent-rules.md docs/status/current.md docs/status/changelog.md docs/status/issues.md docs/handoffs/current.md docs/handoffs/package-index.md`。
6. **是否运行真实 CAD**：否。本包只沉淀系统链路文档，不连接 AutoCAD、不写 DWG、不保存当前图。
7. **机器可读证据路径**：无新增 `output/validation_runs/**`；主要证据为 `docs/architecture/cad-agent-task-chain.md` 和文档治理结果。
8. **结论分类表**：系统任务链路已落地（docs / governance，geometry_verified=否）；训练或真实 CAD 能力提升：未做。
9. **剩余风险**：本包只定义链路和入口；后续若要强制机器校验“每次根源修复都同步 A-to-A 校准”，还需要另包接入可执行检查器。
## CAD-NATIVE-ASSET-REUSE-HARDENING-01
1. **包名**：`CAD-NATIVE-ASSET-REUSE-HARDENING-01`
2. **修改文件列表**：未改 Core 代码；新增真实 CAD 证据 `output/validation_runs/system-assets/cad-native-hardening/reuse_workflow_real.json` 与截图 `output/previews/system-asset-reuse-hardening-20260602.png`；同步 `docs/status/current.md`、`docs/status/changelog.md`、`docs/status/issues.md`、本交接窗口和 package index。
3. **关键设计说明**：本包专门补上上一轮语义资产复用升级未新增的真实 CAD-native 复用证据，验证系统资产库 DWG 可以跨图写入当前业务 DWG 的 `CODEX_PREVIEW`，且不保存当前业务 DWG。
4. **新增/修改测试**：无新增单测；使用真实 AutoCAD COM、报告硬断言和窗口截图做验收。
5. **实际运行的命令和结果**：普通沙箱执行 `scripts/reuse_system_asset.py --workflow "放一个线型表到当前图"` 因 COM 隔离失败；提权后同命令成功。`linetype_style_summary_table` 从 `standard_assets.dwg` 复制到 `Drawing2.dwg`，source selected 450、created handles 450、readback 450、`copyMethod=copyobjects_handle_diff`、`savedCurrentDwg=false`；`render_preview.py --capture-autocad-window --execution-summary ...` 成功截图并按 450 handles bbox 取景。
6. **是否运行真实 CAD**：是。连接 `Autodesk AutoCAD 2026 - [Drawing2.dwg]`，只写 `CODEX_PREVIEW`，未保存当前业务 DWG，未修改正式图层。
7. **机器可读证据路径**：`output/validation_runs/system-assets/cad-native-hardening/reuse_workflow_real.json`；`output/previews/system-asset-reuse-hardening-20260602.png`。
8. **结论分类表**：跨 DWG 线型表资产复用已完成真实 CAD-native 回读验收（geometry_verified=复用级 created handles/readback）；截图为视觉辅助，不替代 handles 证据。
9. **剩余风险**：本包不验证系统资产 DWG 新增原生内容后的 `Saved=true` / 打开复审链路；该链路应在真正执行“沉淀资产 CAD-native 写入”时单独验收。
## CAD-SEMANTIC-ASSET-REUSE-UPGRADE-01
1. **包名**：`CAD-SEMANTIC-ASSET-REUSE-UPGRADE-01`
2. **修改文件列表**：新增 `openspec/changes/cad-semantic-asset-reuse-upgrade/`、`docs/architecture/cad-semantic-asset-reuse-upgrade.md`、`core/assets/semantic_rules.py`、`core/training/linetype_table_audit.py`、`core/orchestrator/semantic_asset_route.py`、`tests/core/test_semantic_asset_rules.py`；更新 `core/assets/system_asset_reuse.py`、`core/assets/__init__.py`、`core/training/linetype_table_demo.py`、`core/orchestrator/workflow_dispatch.py`、`tests/core/test_linetype_table_demo.py`、`tests/core/test_workflow_dispatch.py`、`docs/architecture/system-asset-reuse-workflow.md`、`docs/governance/cad-agent-rules.md`、`AGENTS.md`、`CORE_CONTEXT_BRIEF.md`、状态 / changelog / issues / handoff 索引。
3. **关键设计说明**：把用户反馈中的线型表排版、资产复用、沉淀保存边界和中文编码问题提升为系统底座。`semantic_rules` 固化资产沉淀、线型表、系统资产复用和局部修复的触发词、必跑门禁、禁止行为和证据边界；资产复用在 registry 文本匹配前运行编码预检，并按 score、生命周期、native DWG、精确来源可用性稳定排序；orchestrator 会先报告 `semantic_asset_route`，再走普通 workflow dispatch；线型表生成器支持可变行数并通过独立 layout audit 审计。
4. **新增/修改测试**：新增 `tests/core/test_semantic_asset_rules.py`，覆盖坏 registry 编码阻断、候选排序、语义规则命中和弱匹配负例；更新 `tests/core/test_linetype_table_demo.py`，覆盖可变 17 行表和“报告字段被篡改也能由实体越格审计失败”；更新 `tests/core/test_workflow_dispatch.py`，覆盖主调度报告语义资产路由。
5. **实际运行的命令和结果**：`python -m unittest tests.core.test_semantic_asset_rules tests.core.test_workflow_dispatch` → 12 tests OK；第一轮相邻回归 `tests.core.test_semantic_asset_rules tests.core.test_system_asset_reuse tests.core.test_system_asset_sedimentation tests.core.test_linetype_table_demo tests.core.test_script_bootstrap` → 40 tests OK；`scripts/reuse_system_asset.py --workflow --plan-only "放一个线型表到当前图"` → status ready，`encodingPreflight=pass`；`scripts/draw_linetype_table.py --fake-cad --no-stream-demo` → status pass，`layoutAudit.status=pass`。
6. **是否运行真实 CAD**：否。本包使用 Core / fake CAD / plan-only 验证；未连接 AutoCAD 写新实体，未保存当前业务 DWG。真实跨 DWG 复用证据沿用上一包 `linetype_table_reuse_real.json`，本包不新增真实 CAD 证明。
7. **机器可读证据路径**：`output/validation_runs/system-assets/semantic-upgrade/reuse_workflow_plan.json`；`output/validation_runs/linetype-table/semantic-upgrade/linetype_table_report.json`；OpenSpec 契约在 `openspec/changes/cad-semantic-asset-reuse-upgrade/`。
8. **结论分类表**：语义规则库已落地（code + tests，geometry_verified=否）；资产复用 registry 编码预检和稳定排序已落地（code + tests，geometry_verified=否）；主调度语义资产路由已接入（code + tests，geometry_verified=否）；线型表可变行数和独立 layout audit 已落地（fake CAD readback，geometry_verified=否）。
9. **剩余风险**：沉淀资产 DWG 的 `Saved=true` / 打开复审链路目前是规则和协议要求，未在本包做真实 CAD-native 保存验收；线型表 fake CAD 审计不能证明 CTB/STB、PDF 或打印输出效果；后续对象资产应补真实 CAD readback、保存复审和人工复核。

## SYSTEM-ASSET-SEDIMENTATION-PROTOCOL-01
1. **包名**：`SYSTEM-ASSET-SEDIMENTATION-PROTOCOL-01`
2. **修改文件列表**：新增 / 更新 `core/assets/system_asset_sedimentation.py`、`scripts/sediment_system_asset.py`、`tests/core/test_system_asset_sedimentation.py`、`docs/architecture/system-asset-sedimentation-protocol.md`、`openspec/changes/system-asset-sedimentation-protocol/`、`libraries/system_library/registry.json`、`libraries/system_library/drawing_standards/basic/assets.json`、`libraries/system_library/furniture/seating/sofas/assets.json`；同步 `AGENTS.md`、`docs/training/README.md`、`agents/cad_designer/rules.md`、`docs/governance/cad-agent-rules.md`、`CORE_CONTEXT_BRIEF.md`、状态 / changelog / issues / handoff 索引。
3. **关键设计说明**：把用户口令“沉淀 XX 资产”加固成系统资产四件套 + 晋升门禁 + 源边界防污染门禁。每条资产现在带 `candidate/systemized/verified/deprecated` 状态流、`retrieval`、`native.layoutPlan`、`versioning`、`verification`、`feedbackLoop`、`exportManifest` 和 `antiContamination`；对象 `block_export` 只允许精确 handles / bbox / named block 来源，样式标准走 `style_export`。
4. **新增/修改测试**：`tests/core/test_system_asset_sedimentation.py` 从 4 个用例扩到 11 个，覆盖生命周期 / 检索 / 排版 / 反馈字段、冲突拒绝与 `_v2` 变体、元数据验收、CLI 新参数、对象来源边界、禁止整屏 block export 和样式导出。
5. **实际运行的命令和结果**：`python -m unittest tests.core.test_system_asset_sedimentation tests.core.test_asset_raw_intake tests.core.test_training_workbench_sync` → 28 tests OK；两个 seed 包 `scripts/sediment_system_asset.py --verify --category furniture.seating.sofas` / `drawing_standards.basic` → pass；OpenSpec 9/9 pass；doc governance pass；`scripts/sync_training_workbench.py` pass、Agent check 37/37 pass；`node --check capability-map-data.js` 与 `git diff --check` pass。
6. **是否运行真实 CAD**：否。只写仓库 JSON、OpenSpec 和文档；不连接 AutoCAD、不保存 DWG、不导出 block、不删除实体、不改正式图层。
7. **机器可读证据路径**：`libraries/system_library/registry.json`；`libraries/system_library/drawing_standards/basic/assets.json`；`libraries/system_library/furniture/seating/sofas/assets.json`；OpenSpec 契约在 `openspec/changes/system-asset-sedimentation-protocol/`。
8. **结论分类表**：系统资产沉淀协议 V3 源边界加固已落地（code + tests + OpenSpec + docs，geometry_verified=否）；绘图标准 seed 为 `style_standard/style_export`，沙发 seed 为 `object_block/metadata_only`；真实 native DWG export / CAD insertion replay：未做。
9. **剩余风险**：`nativeDwgExists=false` 时只证明合同、索引、排版计划和元数据门禁存在；后续若要把资产升为 `verified`，必须另包做原生 DWG 写入 / block 定义导出 / 样式导入 / CAD readback 和必要截图验收。
## TRAINING-FOUNDATION-REMAINING-21-01
1. **包名**：`TRAINING-FOUNDATION-REMAINING-21-01`
2. **修改文件列表**：新增 `core/training/foundation_batch_training.py`、`core/training/foundation_panel_drawings.py`、`scripts/run_cad_foundation_remaining_training.py`、`tests/core/test_cad_foundation_remaining_training.py`；更新 `core/training/learning_promotion.py`、`scripts/build_capability_map_data.py`、`tests/core/test_training_learning_promotion.py`、`docs/training/training-sources.json`、`capability-map-data.js`、状态 / changelog / issues / training README / 任务清单 / handoff 索引；新增训练证据位于 `output/training_queues/cad-foundation-remaining-21/`。
3. **关键设计说明**：把 `CAD 基础操作` 剩余 21 项做成可重复跑的自动化训练批次，默认连接真实 AutoCAD 并只写 `CODEX_PREVIEW`。批次会生成结构化训练 plan、dry-run、execution summary、验收 report 和 queue state；验收报告使用通用 `all_items_generated` 计数检查，避免后续批次被 `all_10_items_generated` 写死。图块插入训练统一使用等比 scale，防止真实 CAD `insert_block_alpha` 拒绝非等比块。
4. **新增/修改测试**：新增剩余 21 项训练批次测试，覆盖报告可被 learning promotion 接收、21 项全部写出、图块 scale 等比；更新 learning promotion 测试，覆盖通用 item-count check 和 UTF-8 BOM 报告读取。
5. **实际运行的命令和结果**：`python -m unittest tests.core.test_cad_foundation_remaining_training tests.core.test_training_learning_promotion` → 6 tests OK；真实 CAD 执行 `scripts/run_cad_foundation_remaining_training.py` → 21/21 pass，created/readback handles 235/235，formal layer / save / overwrite / delete 守卫均阻断；`scripts/render_preview.py --capture-autocad-window` → 生成 `remaining_21_preview.png`；`scripts/sync_training_workbench.py` → status pass，learning promotion acceptedItemCount=31，Agent check 35/35 pass。
6. **是否运行真实 CAD**：是。连接 AutoCAD `Drawing2.dwg`，仅向 `CODEX_PREVIEW` 写入训练实体，未保存当前 DWG，未覆盖原图，未写正式图层。首轮真实 CAD 在第 16 项暴露非等比 block scale 问题，已修复并登记到训练错误记录。
7. **机器可读证据路径**：`output/training_queues/cad-foundation-remaining-21/remaining-21-chinese/remaining_21_report.json`、`remaining_21_execution_summary.json`、`remaining_21_dry_run.json`、`remaining_21_training_plan.json`、`remaining_21_preview.png`；队列状态在 `output/training_queues/cad-foundation-remaining-21/queue_state.json`；同步报告在 `output/validation_runs/training-workbench-sync/training_workbench_sync_report.json` 和 `agent_check.json`。
8. **结论分类表**：`CAD 基础操作` 剩余 21 项已完成训练 + 机器验收 + 真实 CAD 回读 + 前端同步（training evidence，geometry_verified=训练级几何回读）；`CAD 基础操作` 工作台状态从 10/31 提升到 31/31；表 C 能力主指标未因此自动提升。
9. **剩余风险**：本包证明的是基础操作训练项在受控预览图层可生成、可回读、可沉淀，不等同完整施工图能力；`scripts/build_capability_map_data.py` 仍偏大，本轮只补通用验收接入口；后续新批次仍需登记 `training-sources.json` 并跑工作台同步。
## REPO-CONTEXT-HYGIENE-02
1. **包名**：`REPO-CONTEXT-HYGIENE-02`
2. **修改文件列表**：更新 `AGENTS.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_RESTRUCTURE_PLAN.md`、`README.md`、`docs/governance/cad-agent-rules.md`、`docs/planning/post-backlog.md`、`docs/ROADMAP.md`、`docs/roadmap/README.md`、`docs/training/README.md`、`docs/training/visual-first-agent-plan.md`、`docs/architecture/shell-layout-foundation-design.md`；新增 `docs/training/training-sources.json`、`core/training/source_manifest.py`；更新 `scripts/build_capability_map_data.py`、`scripts/sync_training_workbench.py`、`scripts/run_training_workbench_agent_check.py`、`core/execution/execute_plan.py`、`core/verification/self_check.py`、`tests/core/test_training_workbench_sync.py`、状态 / changelog / issues / handoff 索引。
3. **关键设计说明**：本包不做大重构，只做上下文治理、训练事实源 manifest 和小边界修补。训练验收报告、队列状态、learning ledger、Agent memory / Prompt addendum 是事实源；`capability-map-data.js` 与 HTML 是派生快照。
4. **新增/修改测试**：`tests/core/test_training_workbench_sync.py` 新增训练 source manifest 断言；Agent check 新增训练源存在、已验收来源登记和派生快照不得冒充事实源检查。
5. **实际运行的命令和结果**：`python -m unittest tests.core.test_training_workbench_sync tests.core.test_training_learning_promotion` → 15 tests OK；`python -m unittest tests.core.test_script_bootstrap tests.core.test_preview_only_audit tests.core.test_cad_session_guard` → 15 tests OK；`scripts/sync_training_workbench.py` → status pass，Agent check 35/35 pass。
6. **是否运行真实 CAD**：否。
7. **机器可读证据路径**：`docs/training/training-sources.json`；`output/validation_runs/training-workbench-sync/training_workbench_sync_report.json`；`output/validation_runs/training-workbench-sync/agent_check.json`；coverage 刷新到 `output/validation_runs/capability-lab/cad_capability_coverage.json`。
8. **结论分类表**：1-5 子包已验收闭环：默认上下文瘦身已落地（docs + governance，geometry_verified=否）；历史文档降噪已落地（docs，geometry_verified=否）；训练事实源 manifest 已接入（data + Agent check，geometry_verified=否）；工作台同步和 Agent 校验已接入（scripts + data，geometry_verified=否）；Core 反向脚本依赖与交接复核已清理（code + tests + handoff，geometry_verified=否）；真实 CAD 能力提升：未做。
9. **剩余风险**：`scripts/build_capability_map_data.py` 仍然偏大，本包只切走事实源入口；后续若继续膨胀，再拆 view-model / registry / writer。训练 manifest 当前登记第一批验收源，后续新队列必须继续登记。
## OPENSPEC-SYSTEM-CONTRACT-01
1. **包名**：`OPENSPEC-SYSTEM-CONTRACT-01`
2. **修改文件列表**：新增 `openspec/changes/polish-openspec-system-contract/`、`openspec/README.md`；更新 `openspec/config.yaml`、`AGENTS.md`、`CORE_RESTRUCTURE_PLAN.md`、状态 / changelog / issues / handoff 索引。
3. **关键设计说明**：OpenSpec 已可用，本包只补 readiness 和契约口径：`status` 必须带 `--change`；`list --specs` 暂空不等于未初始化；completed changes 可先留在 `openspec/changes/`，归档时再同步稳定 specs 与仓库引用。
4. **新增/修改测试**：无新增单测；本包是文档 / 契约润色。
5. **实际运行的命令和结果**：`openspec.cmd list --json` 可列出 completed changes；逐 change `openspec.cmd status --change <name> --json` 正常；`openspec.cmd validate --all --strict --json --no-interactive` pass；`scripts/run_doc_governance_audit.py` pass；`python -m unittest -v tests.core.test_doc_governance` 26 tests OK。
6. **是否运行真实 CAD**：否。
7. **机器可读证据路径**：OpenSpec 契约在 `openspec/changes/polish-openspec-system-contract/`；无新增 `output/validation_runs/**`。
8. **结论分类表**：OpenSpec 初始化可用性已复核（CLI + docs，geometry_verified=否）；系统契约已润色（docs，geometry_verified=否）；真实 CAD 能力提升：未做（geometry_verified=否）。
9. **剩余风险**：旧 completed changes 仍留在 `openspec/changes/`，这是有意保留；后续若要归档，应另轮同步 stable specs 和所有引用。
---
