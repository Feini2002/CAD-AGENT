# Core Context Brief
最后更新：2026-06-03（系统资产库守门员与 layoutPlan v2；系统资产 DWG 视觉仓库 readability 门禁；A-to-A TaskContract 门禁；截图编排底座加固；方案 B/C：CAD Designer Agent 成长路径）
本文是后续 Codex / Cursor / 其它 agent 工具接手本仓库时的稳定短上下文入口。若 `AGENTS.md` 已被工具自动加载，会话恢复从本文开始；人工迁移或新工具接手时先看 `AGENTS.md`，再看本文。普通任务只按“按需展开”表追加 1-2 个文件；不要默认全文扫 `README.md`、`docs/status/current.md`、`docs/handoffs/current.md` 或长期规则。
## 当前一句话

本仓库是可迁移的 CAD Agent Core Lab；**当前阶段：CAD Designer Agent 成长路径训练**（`docs/training/cad-designer-growth-path.md` + `docs/training/cad-designer-training-plan-v2.md` + `docs/training/README.md`）。总训练对象是 `agents/cad_designer/`，第一阶段毕业目标是“电子设计师雏形”；正式训练前计划已扩为 **V2 训练地图**，保留 `CAD 基础操作 / 基础家具 / 储位家具 / 厨卫对象 / 基础绘图 / 标注表达` 六类并扩到 217 个训练项；其中 `CAD 基础操作` 31/31 已真实 CAD 批量训练并沉淀，后续默认进入对象课程或案例 feedback，但复杂任务若暴露基本功不稳，必须回流到对应基础项二次 / 多次复训并回测原任务；单项 / 子图样加深训练默认走 focused retraining，不得因整批脚本存在而扩大到全队列；局部错误默认走原位 `repair_plan`，按 handles / bbox 在 `CODEX_PREVIEW` 中 update、delete_replace 或 add_missing，不在旁边整套重画；轻量 CAD 小动作默认按量化路由选 `quick_trial`（≤2 分钟、只写 `CODEX_PREVIEW`、关键回读、快试未沉淀）、`focused_retraining`（≤8 分钟、点名范围）或 `formal_acceptance`（完整验收 / 沉淀）；未列入计划的临场复合任务（如截图对象 + 标注 / 修改 / 尺度推断）默认拆成已有能力节点动态编排，不把所有排列组合塞进训练地图；V2.1 已补训练批次依赖图和机器验收器骨架；`agents/residential/` 是当前主场景插件。既有 **Visual-First + CAD 常识底座 + 资产智能架构** 保持：白话先经常识 / catalog / 自产资产检索口径形成 `retrieval_pack`，再由 `pipeline_visual_intent` 产出 `style_target` / `visual_parts` / `reference_match`，进入 `CAD_PLAN` → validate → dry-run → `CODEX_PREVIEW` → handles 回读；表 C ≠ 成长路径进度，V2 地图 / V2.1 骨架 ≠ 施工图能力。

## 默认输出口径

普通最终回复默认**不附进度表、表单或表 A/B/C**；只说明本轮完成内容、证据和风险。只有用户明确点名开发状态查询、进度、完整状态、交接、审计、表 A/B/C、表 C、真实 CAD 实力或刷新表 C 时，才展开表格；涉及真实 CAD 能力时先报表 C 主指标。

## 当前精简进度

表 C 只认机器报告：`output/validation_runs/capability-lab/cad_capability_coverage.json`。

| 口径 | 当前值 | 说明 |
| --- | --- | --- |
| **真实 CAD 实力** | **约 90.99%**（`scene_fragment` **93.62%**），最高已证 **L4** | **303/333** showcase；25 smoke + 5 deferred；guard / negative 行不计几何能力 |
| CAD 证明覆盖率 | 机器值见 coverage JSON（317 行；smoke 不计入证明率） | `cad_capability_coverage.json` |
| 工程节奏 | 总约 **97%**（**Core 100%**，Agent 93%） | 表 A；Core 见 `core_platform_completion_gate.md` |
| 训练台账 | 成长路径 + 案例 backlog：`docs/planning/任务清单.md` §0 | 主训 **CAD Designer Agent**；家装为当前主场景插件 |

## 当前 next

**Agent 训练期（方案 B/C）**：主训 `agents/cad_designer/`；第一批课程走基础 CAD 操作，家装案例继续用 `agents/residential/` + `projects/residential_training_template/`。

| 用户口令 | 默认动作 |
| --- | --- |
| **CAD 基础课** / **总设计师训练** | CAD 基础操作 31/31 已完成；默认从基础家具 / 对象课程 / 案例 feedback 中选 1 个训练目标。若复杂任务暴露基础薄弱，回流到对应基础项复训并回测原任务 |
| **跑前 10 项队列** / **监督式基础队列** | 运行 `$py scripts\run_training_queue.py --preset cad-foundation-first-10`；每次暂停 1 项并提示用户验收 checklist / pass / fail 下一步；`--decision pass` 后脚本自动做训练工作台 post-sync；每个自动化子动作默认 30 秒 watchdog，超时先自救，连续超时熔断暂停 |
| **开一轮训练** / **家装案例** | `brief.md` → 计划 → `CODEX_PREVIEW` → `feedback.md` |
| **试一下** / **快画** / **小动作** / **先别沉淀** | 走 `quick_trial`：≤2 分钟，只写 `CODEX_PREVIEW`，做关键 readback，跳过完整训练同步；回复说明“快试未沉淀” |
| **记反馈** | 更新案例 `feedback.md` + 任务清单 backlog |
| **优化常识底座** | 读 `docs/training/cad-common-sense-upgrade.md`；只吸收方法论或资料为 summary / candidate / executable_check / evidence_boundary |
| **优化资产图库** | 读 `docs/architecture/cad-asset-intelligence-architecture.md` + `docs/planning/cad-commonsense-asset-dev-plan-01.md`；raw 标准图库放 `standard_cad_library_raw/`，默认跑 `scripts/run_asset_raw_intake.py --write`；自产图库放 `libraries/system_library/` |
| `刷新表 C` | 只跑 coverage（Lab） |
| `打开训练工作台` / `刷新训练工作台` | 优先运行 `start_training_workbench.bat` 或 `$py scripts\sync_training_workbench.py` |
| `画不准` | `docs/runbooks/blocker-playbook.md` |
| Lab 三轨 / Core 施工 | 已收口 → `archive/`、`post-backlog.md` |

## 最近有效事实

- **CAD-TRAINING-PROMOTION-GATE-01**：训练 / 复训 / 纠错收尾已新增机器 `promotionGate`。`quick_trial` 保持 `promotionLevel=observation`，不写训练事实源、工作台或 Agent 校准；正式训练通过后，ledger / workbench 必须声明 `updateTrainingSource`、`updateWorkbench`、`updateAgentCalibration`、`updateBaseRules`、`updateTaskRules`、`updateChecker`、`retestOriginalTask` 七项决策；未知 `capabilityId` 不再 fallback 到 `cad_designer`；规则 / 检查器 delta 只进入 `needs_reviewed_package`；`scripts/sync_training_workbench.py` 已刷新工作台，Agent check 39/39 pass。
- **CAD-AGENT-TASK-CHAIN-01**：系统任务链路已沉淀到 `docs/architecture/cad-agent-task-chain.md`。后续不能只保留执行闭环或训练闭环的一半：白话先经输入分流、语义拆分、单一子任务和责任分发，再执行 / 审计 / 交付；稳定失败或新能力要回流到训练 / 复训、原任务回测、底座规则、单一任务规则、检查器、Prompt / memory、A-to-A 校准和事实源同步。
- **A-TO-A-TASK-CONTRACT-GATE-01**：主编排新增 `a_to_a_task_contract`。系统资产沉淀固定要求 `pipeline_asset_governor`、`pipeline_asset_librarian`、`pipeline_asset_dwg_curator`、`pipeline_asset_reuse_auditor`；系统资产 DWG 仓库 / 货架 / 置物架 / 动线 / 可扩展布局任务还必须要求 `pipeline_visual_layout_reviewer` 和 `visual_layout_review`。视觉 reviewer 必须显式输出 `layoutReadabilityAcceptable`、`aisleClearanceAcceptable`、`contentDensityAcceptable`、`sourceProofRolesSeparated`、`layerSemanticsAcceptable`、`nonScreenshotEvidenceChecked`；缺任一必需 Agent 输出或字段时，`workflow_dispatch` 以 `a-to-a hard gate` 阻断；检查入口 `scripts/run_a_to_a_orchestration_gate_check.py`。
- **MAIN-AGENT-DISPATCH-AWARENESS-01**：高风险 A-to-A 合同轻量新增 `mainAgentSelfCheck` 与 `dispatchDecision`。主 Agent 自检只表示工程责任边界：识别任务、生成合同、动态加派已登记 Agent、收 hard gate 输出并阻断虚假完成；不模拟对话人格、不替代 CAD readback / 视觉复审 / 资产审计。未登记新 Agent 只能进入 `additionalAgentRequests`，状态为 `needs_reviewed_package` / `needs_openspec_change`，不得临场激活。
- **LOCAL-REPAIR-FIRST-01**：局部错误原位修复优先。用户指出局部乱码、缺线、错线型、错 hatch、标注或部件局部问题时，先读上一轮 `execution_summary` / created handles / CAD readback，生成 `repair_plan`，只对 `target_handles` / `target_bbox` 执行 `update`、`delete_replace` 或 `add_missing`；用户开放删除编辑命令只覆盖 `CODEX_PREVIEW` 中被证据锁定的错误对象，不允许整图清空、全模型空间删除、正式图层修改、保存或覆盖 DWG。handles 失效、对象被炸开 / 删除、局部修会破坏整体拓扑，或全局坐标 / 比例 / 布局根因错误时，才允许整块重画。
- **REPAIR-RUN-BEFORE-DELIVERY-01**：所有修复默认先运行覆盖原问题的最小实际链路再交付。普通代码 / 文档 / 规则修复至少跑对应测试、校验、审计或格式检查；CAD 落图、截图、训练、runner、验证、资产复用 / 沉淀或局部修复链路改动，除单测外还要补一条代表性实际链路。真实 CAD / GUI / COM 不可用时先按 blocker 自救并必要时申请外部执行；仍不可用只能报 `blocked` / `not_run` / `not_verified`，不得用完成口吻。
- **SCREENSHOT-ORCHESTRATION-HARDENING-01**：截图底座已改为任务级编排。截图入口先输出 `screenshotDecision`，局部 `target_handles` / `repair_plan` / bbox 优先，才退到 `execution_summary.created_handles`；默认用 AutoCAD 客户区 `PrintWindow`，不强制置顶，截图只作 `visual_aid_only`，不能替代 created handles / CAD readback / bbox 审计。Agent 共用合同和工作台 Agent check 已接入该规则；真实单 handle 截图证据为 `output/previews/screenshot-orchestration-target-1F7C.png`。
- **TRAINING-TIMEOUT-CIRCUIT-BREAKER-01**：自动化训练规则已要求 30 秒单步 watchdog、超时自救和连续超时熔断；规则层保护不等于脚本执行器已全量实现。
- **DESIGNER-AGENT-GROWTH-PATH-01**：主训目标是 `CAD Designer Agent` 成长路径；`agents/cad_designer/`、成长路径文档和 L0 基础课程已成为训练默认入口；不改表 C。
- **DESIGNER-TRAINING-PLAN-V2-01**：训练地图已扩到 217 项，V2.1 已有 8 个批次和 10 个验收器骨架；骨架不是 CAD proof，不代表已会施工图。
- **TRAINING-QUEUE-AUTO-SYNC-01**：监督式训练队列在 `--decision pass` 或队列完成后自动执行训练工作台 post-sync；用户不需要每轮额外提醒同步。
- **TRAINING-QUEUE-FOUNDATION-10-01**：第一批 10 个基础 CAD 操作项已验收并通过 learning promotion 沉淀到责任智能体；事实源登记见 `docs/training/training-sources.json`。
- **TRAINING-FOUNDATION-REMAINING-21-01**：剩余 21 个基础 CAD 操作项已由 `scripts/run_cad_foundation_remaining_training.py` 真实 CAD 批量训练；最终报告 `output/training_queues/cad-foundation-remaining-21/remaining-21-chinese/remaining_21_report.json` 已做中文标注复训，当前为 21/21 pass、235/235 句柄回读、`chinese_labels=text_labels=65 latin_terms=0`，可见文本扫描 86 条 / 英文术语 0 条，工作台同步 pass，learning promotion 合计 31 items / 7 agents。
- **TRAINING-HATCH-PATTERN-SAMPLES-01**：第 12 项“填充与边界”已按用户要求复训为 8 个小方格 hatch 样板；真实 CAD 回读 patterns=`ANSI31, ANSI31, ANSI32, ANSI37, AR-CONC, BRICK, GRAVEL, EARTH`，scales=`0.45, 1.1, 0.8, 0.75, 0.7, 0.65, 0.55, 0.6`，全部 `CODEX_PREVIEW`。
- **TRAINING-LATENCY-ROUTING-01**：训练期 CAD 小动作按三档量化路由执行：`quick_trial` ≤2 分钟、1 次 CAD 写入 + 1 次关键回读且不沉淀；`focused_retraining` ≤8 分钟、只覆盖点名能力；`formal_acceptance` 才跑完整验收 / 同步 / 表 C 相关链路。
- **TRAINING-SCOPE-GUARD-01**：单项 / 子主题加深训练不得自动扩大为整批训练；`scripts/run_cad_foundation_remaining_training.py` 支持 `--only`、`--hatch-pattern`、`--hatch-scales`，focused 报告写 `scope.mode=focused` 且不覆盖 full-batch 验收。
- **TRAINING-PARKING-ANCHOR-01**：用户可手动移动训练面板便于查看；复训脚本优先回读上一轮 created handles 的当前位置作为 `parking_anchor`，只有 handles 失效时才退回全局 `CODEX_PREVIEW` bbox，避免训练目标按全画布最右侧漂移。
- **TRAINING-FOUNDATION-REFLOW-RULE-01**：基础训练 `systemized/pass` 不是永久封存；复杂任务暴露基础薄弱时，要记录触发点、映射基础项、修改脚本 / Prompt / 检查器 / 规则，复训基础项并回测原任务，新证据追加到训练事实源和 learning promotion。
- **COMPOSITE-TASK-ROUTING-01**：未列入 V2 计划的临场复合任务走动态编排：拆能力节点、声明 `evidence_source`、走 `CAD_PLAN` / validate / dry-run / `CODEX_PREVIEW` / readback / audit；截图推断不得冒充 CAD 尺寸回读，单次组合不污染训练地图。
- **TRAINING-WORKBENCH-FOUNDATION-ASSET-NA-01**：基础 CAD 操作的“图库 / 自产”轨道为不适用；成功证据看 `CAD_PLAN`、handles、bbox、端点、闭合、图层和审计。
- **CAPABILITY-MAP-SYNC-01**：训练工作台是静态快照显示器，事实源来自 coverage、训练 source manifest、learning ledger 和 Agent memory；刷新必须跑 `scripts/sync_training_workbench.py`。
- **SYSTEM-ASSET-LIBRARY-GOVERNANCE-01 / SEDIMENTATION-PROTOCOL-01**：用户明确说“沉淀 XX 资产 / 通用资产 / 收进资产库”时，默认走系统资产四件套前先过 `pipeline_asset_governor` 资产库守门员；守门员判断来源边界、clean reusable source、子 Agent 派发和 `polishHardeningDecision`。系统资产 DWG 默认分 `00_INDEX`、`01_CLEAN_ASSETS`、`02_PREVIEW_CARDS`、`03_REVIEW_QUARANTINE`、`99_EVIDENCE_LINKS`，训练标题 / 临时说明 / 边框 / 尺寸线 / 审计文字 / 证据路径不得进入 `01_CLEAN_ASSETS`。入口 `scripts/sediment_system_asset.py`，协议 `docs/architecture/system-asset-sedimentation-protocol.md`；资产条目要求 `candidate/systemized/verified/deprecated` 状态流、`retrieval`、`native.layoutPlan` v2、`libraryGovernance`、`versioning`、`verification`、`feedbackLoop`、`exportManifest`、`antiContamination`。系统资产 DWG 仓库验收必须同时有 created-handle readback、`visualClearanceAudit.status=pass` 和 `visualReadabilityAudit.status=pass`；截图非空、保存成功或 `overlapCount=0` 不能替代通道、内容密度、source/proof 分离和图层语义审计。对象 block export 只能来自 selected/created/active handles、明确 bbox 或 named block，来源不足进入 metadata-only / quarantine；样式标准走 `style_export`。“沉淀”默认授权创建、打开 / 激活、写入和保存对应系统资产 DWG，但不覆盖用户当前业务 DWG；`--verify` 同时验元数据、layoutPlan v2、守门员决策和声明级门禁，缺 `nativeVisiblePanelEvidence`、`reuseWorkflowProbe` / `reuseReplay` 或 CAD readback 时不得声称真沉淀、可复用或 A-to-A 已打通。
- **SYSTEM-ASSET-REUSE-WORKFLOW-01**：跨 DWG 复用已升级为 workflow 底座；`core.assets.system_asset_reuse` 支持显式复用语义、隐式强匹配、候选排序、多资产任务拆分、`partial` 阻断、精确来源门禁和 fake-driver 回读，CLI 为 `scripts/reuse_system_asset.py --workflow`。主系统后续遇到“放一个线型表，再放一个沙发”或没有显式“资产”但强匹配系统库的请求时，应先生成 `system_asset_reuse_workflow`；无资产信号返回 `not_asset_reuse_request` 后再走普通 `CAD_PLAN`。润色加固后，单个复用计划只有 created handles 且 `readbackStatus=ok` 才能判为 `asset_reused`，CLI 输出必须是严格 JSON。
- **CAD-SEMANTIC-ASSET-REUSE-UPGRADE-01**：大型升级已新增 `core.assets.semantic_rules` 和 `core.training.linetype_table_audit`。白话请求先匹配语义规则库，再进入资产复用 / 沉淀 / 线型表 / 局部修复等链路；系统资产复用前对 registry 文本运行 `encodingPreflight`，坏中文返回 `asset_registry_encoding_failed`，弱匹配只给候选。线型表生成器支持 variable rows，报告新增独立 `layoutAudit`，审计中文 canonical 文本、无填充、样线格 containment、自适应行高、样式多样性和截图证据边界。
- **UTF8-FIRST-CAD-ASSET-GUARD-01**：中文编码问题必须前置根治，不得靠“先画错、截图发现、再修复”。`scripts/_bootstrap.py` 强制 `PYTHONUTF8=1` / `PYTHONIOENCODING=utf-8`；`core.runtime.encoding_guard` 检测 `??`、`�` 和典型 mojibake；系统资产沉淀在写 `assets.json` / `registry.json` 前运行 `encodingPreflight`，线型表在绘制前验证 visible text。失败时阻断，不写 CAD、不保存 DWG。
- **表 C / 旧施工包历史**：已迁入 `docs/status/changelog.md`、`docs/planning/archive/` 与 `docs/handoffs/archive/`；短上下文只保留当前机器值和活跃训练 / 架构事实。
## 主从关系

- `CORE_RESTRUCTURE_PLAN.md` 是唯一 `PlanMD`。
- `docs/planning/任务清单.md` 是唯一执行台账和即时 `next` 镜像。
- `CORE_STATUS.md` 解释能力状态和表 C；机器值以 coverage JSON 为准。
- `docs/status/current.md` 写当前状态；`docs/status/changelog.md` 写历史流水；`docs/status/issues.md` 写风险和教训。
- `docs/handoffs/current.md` 写最近包交接；`docs/handoffs/package-index.md` 查全量包；历史包在 `docs/handoffs/archive/`。
- `output/validation_runs/**` 是机器证据本体，不因 Markdown 整合而移动。

## 不能声称

- 不能把 Core 约 96%、RCAD 29/29 或 no-CAD benchmark 说成“已经能画准施工图”。
- 不能把截图、SVG/PNG 预览、dry-run 或 `benchmark_pass_non_cad` 当成几何准确证据。
- 不能把 `negative_guard_verified`、fake driver 结果或 no-CAD deferred 当成真实 CAD 几何通过。
- 不能把单元测试通过或“已写未运行边界”当成 CAD 链路修复交付；影响 CAD / 截图 / runner / 训练 / 验证的修复默认要跑实际链路，跑不了就报 `blocked` / `not_verified`。
- 不能默认保存、覆盖、删除 DWG，不能修改正式图层；真实 CAD 默认只写 `CODEX_PREVIEW`。

## 按需展开

| 目标 | 先读 |
| --- | --- |
| 系统任务链路 / 白话拆分 / A-to-A 校准 | `docs/architecture/cad-agent-task-chain.md` |
| CAD Designer Agent 成长路径 / 基础课程 | `docs/training/cad-designer-growth-path.md` + `agents/cad_designer/rules.md` |
| 训练一轮 / 建案例 | `docs/training/README.md` + `docs/planning/任务清单.md` §0 |
| 执行开发包 / 调整优先级 | `CORE_RESTRUCTURE_PLAN.md` + 任务清单 |
| 汇报完整能力成熟度 / 展开 A/B/C | `CORE_STATUS.md` + `docs/status/current.md` + coverage JSON |
| CAD 补验 / 画不准 / 环境不通 | `docs/runbooks/blocker-playbook.md` + `docs/runbooks/cad-validation.md` |
| 查历史变更流水 | `docs/status/changelog.md` |
| 查失败教训和活跃风险 | `docs/status/issues.md` |
| 查按包交接 | `docs/handoffs/current.md` + `docs/handoffs/package-index.md` |
| 新人接手 | `docs/onboarding/first-handoff.md` |
| 文档治理 | `docs/planning/phases/phase-z-doc-governance.md` + `scripts/run_doc_governance_audit.py` |

## 常用验证

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest discover -s tests
& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-severity medium
& $py scripts\run_doc_governance_audit.py
& $py scripts\run_dev_volume_audit.py --summary-only --top-groups 5 --fail-on-severity medium
& $py scripts\run_capability_coverage.py --output output\validation_runs\capability-lab\cad_capability_coverage.json
```

## 缓存友好约定

- 本文只写短摘要、当前 next、口径和入口，不写长历史。
- 历史进 `docs/status/changelog.md` 或 `docs/history/`。
- 失败教训进 `docs/status/issues.md`。
- 计划和优先级进 `CORE_RESTRUCTURE_PLAN.md`，执行计数进 `docs/planning/任务清单.md`。
