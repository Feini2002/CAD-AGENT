# 通用 CAD Agent 开发包当前进展

## 2026-06-03 本轮补充
`DATA-BLOAT-A0-A3-IMPLEMENTATION-01` 已把前一轮“训练前 / 收尾防数据膨胀”从规则落到可执行脚本和回归测试：新增只读 `core.maintenance.data_bloat_audit` 与 `scripts/run_data_bloat_audit.py`，输出 `protected`、`derived`、`candidate`、`blocked` 和 capability-map ratchet；`scripts/build_capability_map_data.py` 默认写 compact 单行快照并删除 `capabilities` / `agents` / `stages` / `coverageSnapshot` 重复别名，`capability-map.html` 用 `normalizeWorkbenchData()` 兼容旧快照；`run_training_artifact_retention.py` 默认扫描 `output/debug` / `output/test_artifacts`，引用根扩到 handoffs / projects / validation / system library，`core.training.artifact_retention` 显式保护 `.json` / `.dwg` / `.dwt`，`--write` 时生成 relocation manifest 和 hash。当前真实 `capability-map-data.js` 已降到 1,361,055 bytes / 1 行，`node --check` 通过。真实仓库 `run_data_bloat_audit.py --summary-only` 正确返回 `blocked`：13 个 active fact_source 缺失，coverage `report_path_missing=303`；`sync_training_workbench.py` 因同一 `training_source_paths_exist` 缺口失败。这是证据链阻断，不是快照瘦身失败。
repo audit 已删除 `core/execution/execute_plan.py` 与 `core/verification/self_check.py` 的本地 `sys.path.insert`，由脚本层共享 `_bootstrap.py` 负责入口路径；`scripts/run_repo_audit.py` 新增 severity 汇总和 `--fail-on-severity medium`，当前仓库 `medium=0/high=0/blocking_finding_count=0`，剩余 20 个 `large_python_file` 为 low 治理项。coverage 报告新增 `claim_level_boundary`，明确 `showcase` 有证据路径但不等同严格 `claim_level=verified` 几何回写；当前 `strict_geometry_verified_count=0`、`evidence_path_showcase_count=303`。本轮 `ARCHITECTURE-DOC-HARDENING-02` 已把统一请求链路、系统硬门禁索引和模块禁止边界纳入 `architecture_hardening` 文档治理子报告，检查 3 个入口。

dev volume audit 已新增 severity 汇总、默认中风险阻断计数、`--fail-on-severity`、未跟踪文件分组、已跟踪变更分组、按 group 聚合的行数变化、top group 摘要和 `--summary-only --top-groups` 紧凑输出。当前真实仓库仍被 `--fail-on-severity medium` 阻断：`changed_file_count=185`、`untracked_file_count=105`、`blocking_finding_count=2`；紧凑审计 top 5 收口簇为 `tests/core`、`agents/pipeline`、`openspec/changes`、`core/training`、`docs/training`，最大派生 delta 仍是 `capability-map-data.js`。这些属于待分包收口的源码 / 合同 / 测试 / 派生快照变更，不是可直接忽略的缓存垃圾。

本轮 `DATA-BLOAT-GOVERNANCE-BEFORE-TRAINING-01` 已把“训练前 / 收尾防数据膨胀”接入全局规则、A-to-A 总链路、CAD Designer Agent、pipeline 共享 Prompt 合同和 manifest。新规则要求训练、复训、正式收尾型工作台同步、系统资产沉淀或仓库级治理产生新 output / debug / test artifacts 前后，区分 `protected`、`candidate`、`blocked`、`derived`；`data_bloat_governance` 成为相关 A-to-A 合同 hard gate；`workbench_snapshot_refresh` 保持轻量查看例外；retention report、data-bloat audit report、sync report 和 `capability-map-data.js` 只能作 diagnostic / derived，不进入训练事实源。`run_doc_governance_audit.py` 新增 `data_bloat_governance` 子项，检查 manifest 的 task kind → hard gate 映射、阻断完成声明、报告 artifact 模板和 Agent README 覆盖。边界：本轮不实现 compact 输出、不写清理脚本、不运行 CAD、不提升表 C。

最后更新：2026-06-03（架构链路硬门禁索引 + A-to-A TaskContract 门禁 + 系统资产 DWG 视觉仓库验收）

本文只保留“现在到哪、证据是什么、风险边界是什么”。历史流水见 `docs/status/changelog.md`，瘦身前全文快照见 `docs/history/snapshots/finished-architecture-2026-05-28/docs__status__current.md`，能力矩阵见 `CORE_STATUS.md`，唯一 `PlanMD` / 主计划见 `CORE_RESTRUCTURE_PLAN.md`。后续任务和优先级只写入 PlanMD，避免状态页变成第二份计划。

## 当前一句话

**Agent 训练期（方案 B/C）**：主训目标升级为 `CAD Designer Agent` 成长路径（`docs/training/cad-designer-growth-path.md`），第一阶段毕业目标是“电子设计师雏形”。正式训练前的计划已扩为 **V2 训练地图**（`docs/training/cad-designer-training-plan-v2.md`），工作台六类共 217 个训练计划项；V2.1 已补 8 个训练批次和 10 个机器验收器骨架；基础 CAD 操作类已明确图库 / 自产轨道为“不适用”，训练证据看结构化训练计划、handles、bbox、端点、闭合、图层和审计，不要求标准图块或自产资产。CAD 基础操作 31/31 已真实 CAD 批量训练并沉淀：前 10 项证据在 `output/training_queues/cad-foundation-first-10/`，剩余 21 项入口为 `scripts/run_cad_foundation_remaining_training.py`，最终报告为 `output/training_queues/cad-foundation-remaining-21/remaining-21-chinese/remaining_21_report.json`，截图为 `remaining_21_preview.png`。这些基础项不是永久封存：复杂任务暴露基本功问题时，必须回流复训并回测原任务。家装（`docs/training/residential-primary.md`）是当前主场景插件。Core 与 Lab 三轨已收口；默认 next 是 V2 对象课程 / 案例 + `feedback.md`，不是 V-PROOF 施工包。

**A-to-A 编排门禁**：主编排已新增 `a_to_a_task_contract`。系统资产沉淀会固定派发资产守门员、资产馆员、资产 DWG 编排员和复用审计员；系统资产 DWG 仓库 / 货架 / 置物架 / 动线 / 可扩展布局任务还必须派发 `pipeline_visual_layout_reviewer`。缺任一必需 Agent 输出时，`workflow_dispatch` 以 `a-to-a hard gate` 阻断，不允许用“截图非空 / 对象数量正确 / 回读通过”替代视觉布局复审。治理检查入口：`scripts/run_a_to_a_orchestration_gate_check.py`。

## 默认输出与工具中立口径

普通最终回复默认不附进度表、表单或表 A/B/C；只有用户明确点名开发状态查询、进度、完整状态、交接、审计、表 A/B/C、表 C、真实 CAD 实力或刷新表 C 时，才展开表格。训练链路和交接材料面向 Codex、Cursor 及其它同类 agent 工具通用；Phase A 是“一个交互式 Agent 会话按角色分步”，不强制绑定 Cursor 或任一单一软件。

## 表 C 当前机器快照

机器报告：`output/validation_runs/capability-lab/cad_capability_coverage.json`。

| 指标 | 当前值 |
| --- | --- |
| **真实 CAD 实力（主指标）** | **90.99%**，最高 L4 |
| CAD 证明覆盖率 | **90.99%**（333 行；**0 verified + 303 showcase**；25 smoke + 5 deferred） |
| CAD 实力指数 | **93.53%** |
| 场景片段实力（L3+） | **93.62%**（88/94） |
| 展示就绪度 | **90.99%** |

禁止用工程节奏、RCAD 烟囱、截图或 no-CAD benchmark 替代表 C。

## 工程节奏（表 A）

Core 底座 **100%**（`docs/verification/core_platform_completion_gate.md`）；Agent 多场景约 93%；总进度约 97%。

## 最近有效包

**本轮系统资产 DWG 视觉仓库验收 R5**：按用户指出的“验收口径偏了”继续修正。现在不是只看脚本能写 metadata、截图有框或分区名存在，而是新增 `audit_visual_rack_plan()` 机器门禁：`visualRackPlan` 必须是 `schemaVersion>=2`、`layoutMode=classified_expandable_visual_warehouse_v2`，并带 `warehouseArchitecture`、`acceptanceCriteria`、rack family 归属、slot ownership、copy policy、扩展空位和 zone bbox 比例。`refresh_system_asset_layout_metadata()` 会拒绝弱 plan；`scripts/run_asset_library_governance_check.py` 会读取当前系统库 `nativeLayout.visualRackPlan` 后复用同一审计器。真实 CAD 证据：`libraries/system_library/drawing_standards/basic/standard_assets.dwg` 已保存；脚本清理上一版 209 个货架 handles 并新建 209 个 handles；`createdEntityReadback.status=ok`、`resolvedHandleCount=209`、`unresolvedHandleCount=0`、`unmanagedLayerCount=0`、`primaryWarehouseAreaRatio=0.8694`、`ownedSlotCount=11`、`expansionSlotCount=9`、`savedCurrentBusinessDwg=false`。报告为 `output/validation_runs/system-assets/asset-library-shelves/shelf_layout_report.json`，治理报告为 `output/validation_runs/system-assets/library-governance/final_hardening_decision.json`，截图为 `output/previews/system-asset-library-shelves-r2.png`；`scripts/sediment_system_asset.py --verify --category drawing_standards.basic` 已通过。截图仍是视觉辅助，真实判断看 handles / bbox / readback / audit。

**本轮系统资产库守门员**：`SYSTEM-ASSET-LIBRARY-GOVERNANCE-01` 已把“沉淀资产”从训练画布搬运升级为资产库治理流程。新增 `pipeline_asset_governor` 作为沉淀默认入口，并注册 `pipeline_asset_librarian`、`pipeline_asset_dwg_curator`、`pipeline_asset_reuse_auditor` 三个子角色；`native.layoutPlan` 升级到 v2，包含 `00_INDEX`、`01_CLEAN_ASSETS`、`02_PREVIEW_CARDS`、`03_REVIEW_QUARANTINE`、`99_EVIDENCE_LINKS` 五区、slot、plannedBbox、cleanSource、previewCard、evidenceLinks 和 cleanupPolicy。训练标题、临时说明、边框、尺寸线、审计文字和证据路径默认不得进入 clean reusable source；来源不清时进入 metadata-only / quarantine。`scripts/sediment_system_asset.py` 输出 `assetGovernanceDecision` 和 `polishHardeningDecision`。边界：本包证明的是规则、合同、layoutPlan v2 和 CLI / 单测自校验；未执行真实 CAD-native DWG 重排，不保存当前业务 DWG，不提升表 C。

**本轮修复交付门禁**：`REPAIR-RUN-BEFORE-DELIVERY-01` 已把“以后所有修复都默认运行后交付”写入 `AGENTS.md`、`CORE_CONTEXT_BRIEF.md` 和治理规则。普通代码 / 文档 / 规则修复至少要跑对应测试、校验、审计或格式检查；CAD 落图、截图、训练、runner、验证、资产复用 / 沉淀或局部修复链路改动，除单元测试外还必须补一条代表性实际链路。真实 CAD / GUI / COM 不可用时先按 blocker 自救并必要时申请外部执行；仍不可用只能报 `blocked` / `not_run` / `not_verified`，不得用完成口吻。边界：不改变保护用户 DWG 规则，默认仍只写 `CODEX_PREVIEW`、不保存当前业务 DWG、不改正式图层。

**本轮截图协议优化**：`TASK-SCOPED-CAD-PREVIEW-CAPTURE-01` 已把截图默认口径收紧为任务级视觉辅助证据：默认保留 CAD/IDE 布局，AutoCAD 客户区 `PrintWindow` 截图仍为主路径；聚焦目标优先级为 `target_handles` / `repair_plan.target_handles` / `repair_plan.target_bbox` / 显式 `target_bbox`，再退到整批 `execution_summary.created_handles`。局部修复 10 项中的 1 项时，调用方应传修复对象 handles 或 bbox，避免又截成整批。`zoom_to_handles_extents` 不再在目标句柄不可用时静默 `ZoomExtents` 到全图。第一批已接入 `render_preview`、`visual_cad_review`、`cross_machine_reverify` 和剩余 21 项基础训练入口；报告写入 `visualPreview.role=visual_aid_only`。验证：focused 40 tests OK；OpenSpec strict validate 11/11 changes pass。边界：截图不替代 created handles / readback / audit 几何证据，不保存 DWG、不提升表 C。

**本轮训练沉淀门禁**：`CAD-TRAINING-PROMOTION-GATE-01` 已把“训练后是否写规则 / 校准 Agent / 刷新工作台 / 回测原任务”落成机器 `promotionGate`。正式训练通过后，learning ledger / 工作台必须带 `updateTrainingSource`、`updateWorkbench`、`updateAgentCalibration`、`updateBaseRules`、`updateTaskRules`、`updateChecker`、`retestOriginalTask` 七项决策；`quick_trial` 保持 `observation` 不沉淀；未知 `capabilityId` 不再 fallback 到 `cad_designer`；规则、检查器和底座 delta 只进入 `needs_reviewed_package`。`scripts/sync_training_workbench.py --skip-coverage` 已刷新 `capability-map-data.js` 和 learning ledger，Agent check 39/39 pass。边界：本包不运行 CAD、不提升表 C、不替代 reviewed package 的规则质量审查。

**本轮系统任务链路整合**：`CAD-AGENT-TASK-CHAIN-01` 已把两条必要闭环合并为架构级默认流程：执行编排链路负责“白话 -> 语义拆分 -> 规则匹配 -> 单一子任务 -> 分发执行 -> 审计交付”，训练学习链路负责“训练 / 复训 -> 原任务回测 -> 底座规则 / 单一任务规则同步 -> A-to-A 校准 -> 事实源同步”。新增 `docs/architecture/cad-agent-task-chain.md`，并从 `CORE_CONTEXT_BRIEF.md`、架构 README、训练 README、全局 Agent 流水线和治理规则接入。边界：本包只做文档和规则链路沉淀，不运行 CAD、不改表 C。

**本轮线型表布局根修**：`LINETYPE-TABLE-INTEGRATED-LAYOUT-02` 已把线型表从 24 行分页 / 分区重画改为单外框整合双栏。24 行不是 CAD 限制，而是过保守的布局策略；现在 `layoutPolicy.mode=integrated_dual_panel`、`rowHeightStrategy=adaptive_min_height`、`sampleFitStrategy=fit_to_sample_cell_bbox`，标题区和分组标题行合并，普通数据行才画分段竖线，序号使用阿拉伯数字 `1..42`，并明确 `solidFillUsed=false`。真实 CAD 已清理旧预览表并在 `CODEX_PREVIEW` 重画，451/451 handles 回读，样式回读 pass，样例越格 0、实心填充 0、分组行竖线 0，报告为 `output/validation_runs/linetype-table/integrated-real/linetype_table_report.json`，截图为 `output/previews/linetype-table-integrated-20260602.png`。边界：不保存 DWG、不修改正式图层、不提升表 C。

**本轮修复策略加固**：`LOCAL-REPAIR-FIRST-01` 已把用户反馈“错哪修哪”沉淀为长期规则。后续回测、机器审计或 Agent 自检发现局部错误时，优先读取上一轮 `execution_summary`、created handles、当前 CAD readback 和截图证据，生成 `repair_plan`，按 `target_handles` / `target_bbox` 在原位置执行 `update`、`delete_replace` 或 `add_missing`。用户开放删除编辑命令后，默认只授权删改 `CODEX_PREVIEW` 中被证据锁定的错误对象；不得扩大为整图清空、全模型空间删除、正式图层修改、保存或覆盖 DWG。handles 失效、对象被炸开 / 删除、局部修复会破坏整体拓扑，或全局坐标 / 比例 / 布局根因错误时，才允许整块重画，并须先说明原因。边界：本包只改规则和链路文档，不连接真实 CAD、不删除现有实体、不提升表 C。

**本轮样式语义底座**：`CAD-STYLE-SEMANTICS-CONTRACT-01` 已把线宽、线型和颜色从三条样板线提升为 `CAD_PLAN` / `drawing_standard_profile` 的语义样式契约。新增 OpenSpec change `introduce-cad-style-semantics-contract`；默认 `codex_preview_beta` 现在包含 `wall.cut.heavy_continuous`、`furniture.visible.medium`、`furniture.centerline.medium`、`furniture.inner_detail.thin`、`object.hidden.thin_dashed`、`annotation.guide.thin_dashed` 等 style token；`apply_drawing_standard_to_plan` 会生成 `drawing.style_resolution`，dry-run 和 preview execution summary 会输出 `style_evidence`，glyph primitive 可用局部 style override 表达家具内部线条层级。独立 Review 后已加固：`by_layer` 样式不再写硬编码实体颜色，未解析 `style_token` 不能静默通过校验，`style_token` / `layer_role` 冲突会被拒绝，fake / COM-like readback 能保留显式 `Color`。边界：本包证明的是语义样式合同、属性写入意图和预览执行证据流；不运行真实 CAD、不保存 DWG、不验证 CTB/STB 或 plot 输出、不提升表 C。

**本轮 Prompt 治理**：`PROMPT-CONTRACT-SHARED-01` 已把 CAD 训练通用安全、证据和视觉反馈规则抽成 `agents/COMMON_PROMPT_CONTRACT.md`；各责任智能体的 `prompt_addendum.md` 只保留角色专属训练沉淀，训练工作台每个 Prompt contract 都引用共享合同。`core/training/learning_promotion.py` 后续自动沉淀时也会写共享合同并过滤通用重复句；`scripts/run_training_workbench_agent_check.py` 新增 `common_prompt_contract_referenced` 与 `prompt_addenda_do_not_duplicate_common_rules` 两项护栏。边界：只治理 Prompt 和工作台契约，不改 CAD 能力、不提升表 C。

**本轮空间语义底座**：`DESIGNER-VIEW-NEARBY-PLACEMENT-01` 已落地“旁边 / 附近”的设计师视角解析：新增 `core/placement/designer_view_nearby.py`、`CAD_VIEW_CONTEXT` / `placement_resolution` schema、no-CAD fixture、preview-only quick trial 和 `scripts/run_designer_view_nearby_smoke.py`。该能力把当前视口、可见实体、选中对象和最近 handles 解析为 `focus_anchor`，再生成当前视口内的邻近候选槽位，最终收口为确定 `CAD_PLAN.placement.base_point` 并通过 handles/bbox 回读验收。边界：只证明当前视域邻近放置，不证明沙发等对象族能力、不提升表 C、不代表施工图准确。

**本轮空间语义复盘**：真实 quick trial 中曾绕过 `designer_view_nearby`，直接用全局 `CODEX_PREVIEW` bbox 放置“旁边”对象，导致沙发远离用户当前左上视觉焦点。共享 Prompt 合同和 issues 已补充：含“旁边 / 附近 / 边上 / 方向词”的真实 CAD 小动作必须走当前视口链路；无法确定唯一视觉焦点时返回 `blocked` / `needs_confirmation`，不得用临时脚本或全局 bbox 代替视觉语义判断。

**本轮快路径优化**：新增 `core.quick_tasks.nearby_draw` 与 `scripts/run_quick_nearby_draw.py`，把“旁边快画”固定成轻量入口：当前视口上下文、焦点锚点、邻近槽位、`CODEX_PREVIEW` 写入和 handles/bbox 回读一次完成，默认不生成完整 CAD_PLAN / dry-run / 多份中间报告。no-CAD smoke 中沙发快画为 12 个 handles，fake 端到端约 0.0005s；真实 CAD 仍以 COM snapshot / draw / readback 为主要耗时。

**本轮视觉限定加固**：`core.quick_tasks.nearby_draw` 已新增 `visual_context` / `input_scope`，把“截图这里 / 图片这里 / 这里 / 我看到的地方 / 旁边”统一视为视觉限定请求，而不是普通全局坐标请求。快入口会记录视觉来源、锚点策略和 checked / not_checked；截图只作为视觉目标提示，CAD 坐标仍必须来自当前视口、选中对象 / recent handles / 可见焦点簇以及 created handles/bbox 回读。多焦点或无法映射时返回 `needs_confirmation` / `blocked`。

**本轮架构协议**：`SYSTEM-ASSET-SEDIMENTATION-PROTOCOL-01` 已落地并加固“沉淀 XX 资产”的默认动作：系统资产沉淀必须形成机器契约、CAD 原生资产位置、应用 / 验收工具和全局索引四件套，并写入 `candidate/systemized/verified/deprecated` 状态流、`retrieval`、`native.layoutPlan`、`versioning`、`verification`、`feedbackLoop`、`exportManifest` 与 `antiContamination`。对象资产只有用户选中实体、刚创建 handles、active DWG handles、明确 bbox 或 named block 这类精确来源才允许准备 `block_export`；不得把整个 `CODEX_PREVIEW`、全模型空间、当前屏幕、全部可见对象或训练面板打成 block。样式标准如线宽、线型、尺寸、文字和引线必须走 `style_standard` / `style_export`。当前 CLI 只写合同、索引和元数据验收；CAD-native 写入 / 保存 / 打开作为沉淀收尾步骤执行。`nativeDwgExists=false` 或 `native DWG geometry` 在 `notChecked` 时不声称原生 DWG 已导出 / 已验证复用。

**本轮系统资产保存 / 复审授权**：`SYSTEM-ASSET-NATIVE-SAVE-REVIEW-01` 已把用户口令“沉淀 XX 资产 / 通用资产 / 收进资产库”扩展为对应系统资产 DWG 的创建、打开 / 激活、写入和保存授权。只要本轮向 `libraries/system_library/**/**/*_assets.dwg` 或资产合同解析出的 `nativeDwg` 添加、替换或修复了原生 CAD 内容，必须保存该 DWG，并回读活动文档路径、`Saved=true` 和关键实体 / 样式证据；沉淀收尾默认打开 / 激活对应 DWG，供用户人工复审。边界：该授权只覆盖系统资产库 DWG，不覆盖用户当前业务 DWG、原始图纸、正式图层、全模型空间清理或非系统资产文件的保存 / 覆盖。

**本轮系统资产复用**：`SYSTEM-ASSET-REUSE-INSERT-01` 已落地“语义查库 + 跨 DWG 复用到当前文件”的最小闭环。新增 `core.assets.system_asset_reuse` 和 `scripts/reuse_system_asset.py`：当用户说“从 XX 资产调用 / 复用 / 插入 / 套用 / 放到当前 DWG”，或需求语义明显匹配系统资产时，先查 `libraries/system_library/registry.json`，按名称、别名、用途、标签和 `retrieval.matchText` 匹配资产；复用写入当前 DWG 时默认只写 `CODEX_PREVIEW`，回读 created handles，且 `savedCurrentDwg=false`。真实 CAD 烟测已从 `standard_assets.dwg` 跨 DWG 复用 `linetype_style_summary_table` 到新的未保存当前 DWG，450/450 handles 回读，截图为 `output/previews/system-asset-reuse-linetype-table-20260602.png`，报告为 `output/validation_runs/system-assets/asset-reuse/linetype_table_reuse_real.json`。边界：当前 fallback 支持 line/text/circle/arc/polyline 的资产展示几何；复杂 block 属性、CTB/STB 打印效果和业务图保存仍需后续专门验证。

**本轮 CAD-native 复用加固验证**：`CAD-NATIVE-ASSET-REUSE-HARDENING-01` 在用户已打开 AutoCAD 后，真实执行 `scripts/reuse_system_asset.py --workflow "放一个线型表到当前图"`。首次普通沙箱连接 COM 失败，按 GUI/COM 规则提权后成功连接 `Autodesk AutoCAD 2026 - [Drawing2.dwg]`；从 `libraries/system_library/drawing_standards/basic/standard_assets.dwg` 复制 `linetype_style_summary_table` 到当前 DWG 的 `CODEX_PREVIEW`，`copyMethod=copyobjects_handle_diff`，source selected 450、created handles 450、readback 450、`savedCurrentDwg=false`。报告为 `output/validation_runs/system-assets/cad-native-hardening/reuse_workflow_real.json`，截图为 `output/previews/system-asset-reuse-hardening-20260602.png`。边界：本轮不保存当前业务 DWG；系统资产 DWG 写入后 `Saved=true` / 打开复审仍留待真正执行“沉淀资产原生写入”时验证。

**本轮语义资产复用升级**：`CAD-SEMANTIC-ASSET-REUSE-UPGRADE-01` 已新增机器语义规则库、主调度语义资产路由和线型表独立审计。`core.assets.semantic_rules` 负责在 prompt 前固化资产沉淀、资产复用、线型表和局部修复的触发 / 禁止行为 / 验收 hooks；`core.orchestrator.semantic_asset_route` 让主系统在普通 workflow dispatch 前记录资产复用判断；`system_asset_reuse` 在 registry 文本匹配前执行 `encodingPreflight`，坏中文返回 `asset_registry_encoding_failed`；`draw_linetype_table(..., rows=...)` 支持可变行数并输出 `layoutAudit`。证据：相关回归通过，复用 plan-only 和线型表 fake CAD 审计报告已写入 `output/validation_runs/**/semantic-upgrade/`。

**本轮补训 / 纠偏**：`TRAINING-LINEWEIGHT-LINETYPE-STANDARD-01` 已按用户反馈复训第 22 项“线宽线型标准”。根因是原面板只画普通 `draw_line`，driver 未写入 `Lineweight` / `Linetype`，报告也未验样式回读；现在三条样例线分别回读 `Lineweight=70/35/13`、`Linetype=CONTINUOUS/CENTER/DASHED`、`LinetypeScale=1/25`。真实 CAD focused 复训 1/1 pass、12/12 handles 回读、全部 `CODEX_PREVIEW`，报告为 `output/training_queues/cad-foundation-remaining-21/focused/cad-layer-lineweight-standard/remaining_21_report.json`，截图为 `output/previews/task22-lineweight-linetype-focused.png`。本轮不覆盖整批 21 项验收、不提升表 C。

**本轮尺寸样式加强训练**：`DIMENSION-STYLE-FOCUSED-10-01` 已在用户打开的 `Drawing2.dwg` 中创建 10 个中文尺寸样式训练面板，全部写入 `CODEX_PREVIEW`，当前业务 DWG 未保存、未删除实体、未改正式图层。真实 CAD 证据：`desktopSwitch=pass` 后连接 `Autodesk AutoCAD 2026 - [Drawing2.dwg]`，`encodingPreflight=pass`，`styleCount=10`，`createdHandleCount=143`，`readbackEntityCount=143`，`dimensionReadbackCount=19`，`audit.failedStyleCount=0`；报告为 `output/training_queues/dimension-style-focused-10/real-cad/dimension_style_training_report.json`，截图为 `output/previews/dimension-style-focused-10-real.png`。本轮只完成训练样式落图与回读复审，资产沉淀仍为 `not_started`。

**本轮尺寸样式比例重训**：`DIMENSION-STYLE-ARCH-SCALE-RETRAIN-01` 已按用户反馈把上一轮失败预览对象按 `createdHandles` 限定删除并重画。策略改为保留 10 个 canonical 中文尺寸样式，不盲目扩样式数量；每个样式追加 3 个比例 / 跨度样例，建筑 tick 的 `DIMASZ` 收敛到 1.2–1.7 区间。真实 CAD 证据：清理上轮失败 `CODEX_PREVIEW` handles 153/153，重画 `createdHandleCount=304`，`canonicalStyleCount=10`，`scaleVariantCount=30`，`dimensionReadbackCount=49`，`audit.failedStyleCount=0`，`duplicateStyleFingerprints=0`，`savedCurrentDwg=false`；报告为 `output/training_queues/dimension-style-focused-10/real-cad-architectural-scale-retrain/dimension_style_training_report.json`，截图为 `output/previews/dimension-style-focused-10-architectural-scale-retrain.png`。用户随后指出 06 标高符号比例样例越框，已重训修复：先验证旧 304 handles 已被清理，再重画 `createdHandleCount=322`，报告新增 `panelHandlesByStyle` / `panelBoundsByStyle` 与 `panel_containment` 审计，06 面板 `panelReadbackCount=63`、`failures=[]`；修复报告为 `output/training_queues/dimension-style-focused-10/real-cad-level-marker-containment-repair/dimension_style_training_report.json`，截图为 `output/previews/dimension-style-focused-10-level-marker-containment-repair.png`。用户进一步指出 06 不像常规尺寸样式，经设计师 / 训练架构 Agent 复核，已把“室内-标高符号尺寸”拆出 dimension style 范畴，改由真实尺寸实体的“室内-洞口宽高尺寸”替换；r3 真实 CAD 清理 301 handles 后重画 `createdHandleCount=328`、`dimensionReadbackCount=44`、`audit.failedStyleCount=0`、`savedCurrentDwg=false`，报告为 `output/training_queues/dimension-style-focused-10/real-cad-opening-dimension-rework-r3/dimension_style_training_report.json`，截图为 `output/previews/dimension-style-focused-10-opening-dimension-rework-r3.png`。资产沉淀仍未开始。

**本轮尺寸样式系统资产可见面板补写**：用户复审 `standard_assets.dwg` 时指出只能看到线型表，根因是上一轮原生写入只沉淀了不可见的 DimStyle / `CODEX_CN_TEXT` 定义，模型空间没有可见尺寸样式内容。已打开并保存 `libraries/system_library/drawing_standards/basic/standard_assets.dwg`，在模型空间追加 10 个尺寸样式可见面板，位于原线型表右侧；报告 `output/validation_runs/system-assets/dimension-style-standard-dwg/native_visible_panel_r1/native_visible_panel_summary.json` 记录 `createdHandleCount=325`、`dimensionReadbackCount=44`、`failedStyleCount=0`、`savedAssetDwg=true`、`savedCurrentBusinessDwg=false`。聚焦截图为 `output/previews/system-asset-dimension-style-visible-panel-r1-focused.png`。资产合同和 registry 已补 `nativeVisiblePanelEvidence`，资产 lifecycle 标为 `verified`；复用计划信号仍保持 `verificationStatus=native_style_definition_written`，跨 DWG style import / plot / 用户视觉验收仍为 `notChecked`。

**本轮系统资产真沉淀 / A-to-A 门禁加固**：用户指出“没有真的沉淀过去”和“可执行复用 + A-to-A 联通没有一次打牢”。已把规则从口头边界升级为机器门禁：`verify_system_asset_package()` 对 `native_style_definition_written` / `written_to_standard_assets_dwg` 的 `style_standard` 强制要求 `nativeVisiblePanelEvidence` 或等价可见 native 证据；对 lifecycle=`verified` 的资产强制要求 `reuseWorkflowProbe` 或真实 `reuseReplay`。缺任一门禁时 `scripts/sediment_system_asset.py --verify` 返回 fail，并在 `notChecked` 写入 `native visible asset evidence` / `executable reuse workflow probe`。语义规则库、共用 Prompt 生成源、Agent check、AGENTS 和治理文档均已同步；尺寸样式资产合同 / registry 已补 `reuseWorkflowProbe`，复跑 verify 时 checked 包含 `native visible asset evidence` 与 `executable reuse workflow probe`。

更多近期训练链路、复训和仓库治理包详见 `docs/status/changelog.md`。

完整历史继续查 `docs/status/changelog.md` 与 `docs/handoffs/package-index.md`。

## 当前风险

| 风险 | 影响 | 当前处理 |
| --- | --- | --- |
| 训练后靠人工确认是否沉淀 | 没有机器 gate 时，训练 pass 后可能漏写 Agent 校准、工作台同步、规则候选或原任务回测；也可能把 quick trial 误报为已沉淀 | 已新增 `promotionGate` 与 Agent check：systemized 训练缺 gate 会失败；quick trial 不可 promotion；规则 / 检查器 delta 只进入 reviewed package |
| 训练截图历史堆积 | 自动化训练、focused retraining 和截图复核会持续产生 PNG/JPG；如果只靠人工整理，旧截图会占磁盘并可能被误当最新证据 | 已新增训练产物保留执行器：pass 后写 `postTrainingArtifactRetention` dry-run 报告；被引用和最新预览图保留，未引用旧图需显式 `--artifact-retention-write` 才归档，不直接删除 |
| 执行闭环和训练闭环割裂 | Agent 可能会只把白话拆成执行任务，却不把失败回流训练；或只说训练通过，却没同步到执行分发、规则和 A-to-A 校准 | 已新增 `CAD-AGENT-TASK-CHAIN-01`：系统链路同时规定执行编排、训练学习、规则同步、单一任务规则和 A-to-A 校准 |
| 中文编码损坏靠截图后修 | 中文路径、资产名、用途或标注若在第一步已经变成 `??` / mojibake，截图自检只能补救，仍会让错误进入 CAD / 资产合同 | 已加 `UTF8-FIRST-CAD-ASSET-GUARD-01`：脚本强制 UTF-8 环境，沉淀写合同前和线型表绘制前运行 `encodingPreflight`，失败则不写 CAD、不保存 DWG |
| 资产规则只靠 prompt 记忆 | 资产库扩大后，弱匹配、候选资产、metadata-only、样式标准和对象 block 可能被误判，导致误复用或误沉淀 | 已新增 `core.assets.semantic_rules` 和复用前 registry 编码预检；线型表审计从实体 readback 查无填充、样线 containment、行高和样式差异 |
| 资产库 DWG 被训练内容污染 | 训练标题、临时说明、边框、尺寸线或整块训练面板若被原样沉淀，会让未来检索命中“资产”但复制源不干净，削弱系统资产库意义 | 已新增 `pipeline_asset_governor` 与 layoutPlan v2：来源不清进入 `03_REVIEW_QUARANTINE`，clean source 只允许精确来源或 style definition，收尾输出 `polishHardeningDecision` |
| 局部错误被旁边整套重画放大 | 回测已能发现局部乱码、线型、hatch、标注或局部几何错误时，Agent 可能另起一整套图，旧错留在原位并增加画布噪声 | 已写入“原位局部修复优先”：先生成 `repair_plan`，按 handles / bbox 局部 update、delete_replace 或 add_missing；删除权限只覆盖 `CODEX_PREVIEW` 中被证据锁定的错误对象 |
| 小动作被完整训练闭环拖慢 | 用户只想快速试画一个简单 CAD 动作时，Agent 可能自动执行截图、同步、learning promotion 等重工序，导致几秒动作变成复杂训练任务 | 已写入 `quick_trial` / `focused_retraining` / `formal_acceptance` 三档量化路由；快试 ≤ 2 分钟、focused ≤ 8 分钟，只有明确验收 / 沉淀 / 整批口令才走完整链路 |
| 单项复训被批量脚本放大 | 用户点名某个训练项或某个图案时，Agent 可能因为已有整批脚本而重新跑全部队列，造成画布噪声和验收负担 | 已写入训练范围硬边界；剩余 21 项脚本支持 `--only` focused retraining 和 hatch 子范围参数，focused 报告不覆盖整批验收 |
| 自动化训练长任务卡死 | 大面积训练 CAD 时，CAD COM、截图、回读或同步步骤可能长时间等待，导致队列卡断、无人值守误继续或 partial output 被误判通过 | 已写入 30 秒单步 watchdog、有限自救和连续超时熔断规则；后续训练脚本需要把字段和状态落到执行器 |
| Core / training / case 边界继续变重 | `core/` 可能继续吸收临界模块，`core/verification/`、capability map、case renderer 可能变成混合层 | 新增 `current-module-boundaries.md` 和 `architecture-boundary-hardening-01` OpenSpec；后续拆分按 report contract、runner、registry writeback、visual audit、data generator、page shell、display configuration 和 case promotion gate 推进 |
| 表 C 旧证据债 | 旧 verified/showcase 报告缺路径或契约字段会阻止新 writeback | 表 C 新包先跑 hard audit、visual review、table C gate |
| CAD 画面与几何扩样仍少 | 用户看到的复杂 CAD 图面仍需持续提升 | 需要时优先 `VCAD-*` 或真实 CAD 扩样包 |
| 训练审计虚绿 | 部件齐全或 profile ratio 对齐仍可能被误判为款式准确，尤其 reference-match 案例 | 已新增 reference profile、形态丰富度、part gap/overlap、共享边去重与沙发方向语义门槛 |
| 常识文件被误读为已学会 | 把外部资料、图库或 GitHub 方法论放进仓库，不等于 Agent 能稳定使用 | 新增 CAD 常识底座文档，要求 source_note → summary → candidate → executable_check → evidence_boundary |
| raw 标准图库进 git 后边界变模糊 | 为了家里 / 公司两头开发，`standard_cad_library_raw/` 允许携带下载文件；若未写来源和边界，容易误追踪、误提交或误当能力 | 新增自动 raw intake：先扫描并生成 `source_note` / reference manifest / inferred annotation；raw 只算 reference input，自产资产只进 `libraries/system_library/` |
| 训练工作台被误读为证据或过期快照 | `capability-map.html` 展示训练计划、智能体 Prompt 契约和阶段状态，若脱离表 C 口径或未同步，可能被误读成真实 CAD 能力证明或最新计划 | 页面顶部、训练详情、智能体成熟度和证据边界均声明“训练阶段 / 契约分不等于 CAD 通过率”；`sync_training_workbench.py` + Agent 校验检查 source refs、共享 Prompt 合同、表 C 快照和页面同步提示；真实证据仍在 registry、coverage、case runs、audit 和 promotion 记录里 |
| CAD Designer Agent 成长路径被过度承诺 | 基础课程、能力护照或毕业目标容易被误读成“已会施工图” | 文档和工作台明确：成长路径进度不提升表 C；真实 CAD 声明仍看 validate、dry-run、`CODEX_PREVIEW`、created handles 回读、审计和用户反馈 |
| V2 训练地图被误读为已学会 | 217 个训练项只是正式训练前的课程地图，容易被误当成系统能力已经覆盖 | V2 文档和工作台继续使用“目标已声明 / 计划中 / 训练中 / 已沉淀”口径；每项必须通过具体训练轮次和证据链，不能用条目存在替代 CAD 证明或用户验收 |
| 基础训练被误读为永久封存 | CAD 基础操作 31/31 通过后，后续复杂任务可能仍暴露基本功不稳；如果把通过项当成不能再改，会阻断真实能力成长 | 已写入回流复训规则：复杂任务触发 → 映射基础项 → 改脚本 / Prompt / 检查器 / 规则 → 复训基础项 → 回测原任务；旧证据保留为历史，新证据追加沉淀 |
| 复合任务被误读为训练计划缺项 | 用户临场组合截图、对象、标注、修改和尺度推断时，如果要求每个组合都预写进计划，会导致 V2 训练地图无限膨胀；若不声明证据来源，又容易把截图推断误当真实 CAD 尺寸 | 已写入复合任务动态编排规则：拆能力节点、声明 `evidence_source`、走结构化意图 / `CAD_PLAN` 与 readback / audit；单次组合不进训练地图，重复失败或可机器检查时才晋升训练项 / 检查器 |
| 基础 CAD 操作被误读为资产训练 | 基础图元、编辑、变换等 L0 课程如果显示“图库未纳入 / 自产未纳入”，容易被误解成缺标准图块或缺自产资产 | 工作台数据源已改为 `not_applicable / 不适用`；基础操作默认沉淀命令、参数、Prompt、检查器和失败经验，只有对象训练、图库优化或明确晋升任务才进入资产轨道 |
| 参考图库被误读为自产能力 | 外部标准图库、用户截图或 vendor block 被混入系统库后，可能被误报为“系统已会画” | 新增资产智能架构：`reference_library` 只作 evidence input，`system_library` 必须有 schema、lineage、check、evidence_boundary 和晋升记录 |
| 资产复用被误简化成单资产复制 | 用户描述可能同时包含多个系统资产，或没有显式“调用资产”但明显匹配已有系统库；若仍按单 query 处理，会漏找资产或把局部阻断放大成整句失败 | 已新增 `system_asset_reuse_workflow`：显式 / 隐式触发、多资产拆分、候选排序、partial 阻断和精确来源门禁；无资产信号返回 `not_asset_reuse_request` 后交回普通绘图链路 |
| 训练反馈低信号 | 只报 handles、gap/overlap 或贴截图，用户仍不知道该判断什么 | README 新增低噪声反馈模板：本轮结论、变化、checked/not_checked、重点看点、反馈入口 |
| 自动读图未到交付预备 | 未确认 shell candidates 不能直接落 CAD | 保持人工确认 gate |
| 文档入口再膨胀 | 默认上下文会被 done 明细重新占满 | `run_doc_governance_audit.py` 增加活跃文档体量预算 |

更多风险和教训见 `docs/status/issues.md`。

## 当前入口

| 需要 | 看哪 |
| --- | --- |
| CAD Designer Agent 成长路径 | `docs/training/cad-designer-growth-path.md` |
| Agent 训练 / 家装主场景 | `docs/training/README.md` |
| 案例 backlog | `docs/planning/任务清单.md` §0 |
| 唯一主线 / 后置 Backlog | `CORE_RESTRUCTURE_PLAN.md` |
| 能力矩阵 / 表 A/B/C | `CORE_STATUS.md` |
| 已完成包明细 | `docs/planning/archive/` |
| 当前交接 | `docs/handoffs/current.md` |
| 全量交接索引 | `docs/handoffs/package-index.md` |
| 历史快照 | `docs/history/snapshots/finished-architecture-2026-05-28/` |

## 最近验证入口

本轮主 Agent 轻量派发感知加固：`a_to_a_task_contract` 新增 `mainAgentSelfCheck` 与 `dispatchDecision`，只在系统资产沉淀、资产 DWG 布局、视觉布局复审等高风险任务强制；主 Agent 可动态加派已登记 Agent，未登记新 Agent 只能作为 reviewed package / OpenSpec 候选，不得临场激活。验证已覆盖合同单测、workflow dispatch 阻断和 A-to-A gate check；本轮未写 CAD、未保存 DWG、不提升表 C。

本轮系统资产 DWG 视觉仓库可读性加固：`scripts/layout_system_asset_shelves.py --clear-all-shelf-layers` status=`pass`，重新保存 `libraries/system_library/drawing_standards/basic/standard_assets.dwg`；旧 proof panel 内容从 `CODEX_PREVIEW` 迁到 `ASSET_PROOF_CONTENT`，A2 内容簇按 readback handles 右移，`contentMutationCount=519`。新建货架 `createdHandleCount=219`、`createdEntityReadback.status=ok`、`resolvedHandleCount=219`、`unmanagedLayerCount=0`；`visualClearanceAudit.status=pass`、`overlapCount=0`；`visualReadabilityAudit.status=pass`、`issueCount=0`、A1/A2 通道 1600、A2/B 通道 1400、A1 内容宽度占比 0.7792、A2 内容宽度占比 0.7146、`protectedContentLayers=['ASSET_PROOF_CONTENT']`、`savedAssetDwg=true`、`savedCurrentBusinessDwg=false`。截图 `output/previews/system-asset-warehouse-readability.png`。系统资产库治理门禁同步要求最新 shelf CAD readback + clearance + readability，`scripts/run_asset_library_governance_check.py` status=`pass`，输出 `output/validation_runs/system-assets/asset-library-governance/governance_check.json`；A-to-A 自检 `scripts/run_a_to_a_orchestration_gate_check.py` status=`pass`；`scripts/render_preview.py --check` status=`ready`。当前 coverage 表 C 主指标以 `output/validation_runs/capability-lab/cad_capability_coverage.json` 为准。

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_doc_governance_audit.py
& $py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v
& $py scripts\run_capability_coverage.py --output output\validation_runs\capability-lab\cad_capability_coverage.json
```

真实 CAD 完成声明仍必须补 validate、dry-run、`CODEX_PREVIEW`、created handles 回读、实体检查和必要截图；截图只作视觉辅助。日期型流水已迁回 `docs/status/changelog.md`，当前页不再展开旧包明细。
