# CAD Agent 规则

本目录是可迁移的 CAD Agent 开发包，不绑定某一张 DWG、某一套家装图纸或某一台电脑。

本仓库的规则、训练链路和交接材料面向 Codex、Cursor 及其它同类 agent 工具通用；不得把开发流程强制绑定到某一个软件。文档中如出现 Codex / Cursor 名称，应理解为可选载体或历史文件名，除非上下文明确是在描述该工具专属能力。

## 默认中文输出

面向用户的说明、状态汇报、方案讨论、结论和追问默认使用中文。只有以下内容保留英文或原文：

- 代码、命令、路径、文件名、Schema 字段和 JSON key
- CAD / Python / Git / MCP / AutoCAD 等工具、库、API 的专有名称
- 用户明确要求英文输出时

如果引用外部技能、插件或工具模板中的英文规则，应先理解其含义，再用中文向用户转述；不要把英文模板原样作为最终答复。

## 中文编码前置门禁

所有 CAD 写入、系统资产沉淀、系统资产 DWG 创建 / 打开 / 保存、表格类中文标注和训练落图入口，必须在第一步固定 UTF-8 运行环境并做文本编码预检。脚本入口默认由 `scripts/_bootstrap.py` 设置 `PYTHONUTF8=1`、`PYTHONIOENCODING=utf-8` 并重配 stdout/stderr；核心入口可用 `core.runtime.encoding_guard` 检测 `??`、`�`、`绾垮瀷` / `鏍峰` 等典型 mojibake。若项目路径、资产名称、别名、用途、来源文档、中文标注或 visible text 在进入 CAD 前已经损坏，必须立即阻断并报告 `encodingPreflight=fail`；不得先写 CAD / 保存 DWG / 截图自验后再修。

## 先恢复上下文

在进行 CAD Agent 开发、绘图、调试或状态汇报前，默认使用短入口恢复上下文，减少每轮开发的上下文抖动。多数 Codex / Cursor 会自动加载本文件；如果本文件已经在会话规则中生效，就从 `CORE_CONTEXT_BRIEF.md` 开始恢复，不要再反复全文读取本文件。

1. 先读取 `CORE_CONTEXT_BRIEF.md`
2. 再按当前任务读取 `CORE_CONTEXT_BRIEF.md` 里“按需展开”表指定的详细文件

只有在下列情况才全文读取旧的完整上下文文件组：

- 用户要求完整状态汇报、完整交接或全仓治理审计
- 要执行 `CORE_RESTRUCTURE_PLAN.md` 中某个 Phase
- 遇到卡壳、回归、绘图不准或 CAD 环境问题
- 要修改规则、计划、状态、变更记录或问题记录

完整上下文文件组为：

1. `README.md`
2. `CORE_STATUS.md`
3. `docs/roadmap/current.md`
4. `CORE_RESTRUCTURE_PLAN.md`
5. `docs/status/current.md`
6. `docs/governance/cad-agent-rules.md`
7. `docs/runbooks/blocker-playbook.md`
8. `docs/status/changelog.md`
9. `docs/status/issues.md`

## 单一 PlanMD 开发主线

当前唯一 `PlanMD` / 开发主线是 `CORE_RESTRUCTURE_PLAN.md`。根目录没有独立 `plan.md`；用户提到 `PlanMD`、`plan.md`、主计划或主 plan 时，默认指 `CORE_RESTRUCTURE_PLAN.md`。

- `PlanMD` 只做文档治理和开发排序，不改变本仓库“通用 CAD Agent Core Lab”的方向。
- `CORE_RESTRUCTURE_PLAN.md` 决定当前活跃工作队列、Phase 顺序、优先级、Decision Gate 和退出标准。
- `docs/planning/phases/*.md` 只是辅助执行剧本，可以写命令和检查表，但不能成为第二套主计划，也不能保留后置 Backlog 副本。
- `CORE_STATUS.md`、`docs/status/current.md` 只写能力、证据、风险和当前状态，不承载独立下一步。
- 新增待办、调整优先级、改变退出标准或拆分未来小包时，先同步 `CORE_RESTRUCTURE_PLAN.md`，再更新辅助 MD 的引用或状态说明。
- 若文档整理和 Core 优先、`CAD_PLAN` 中间层、真实 CAD 验证门槛或场景轻量化发生冲突，必须以这些根边界为准。

## OpenSpec 变更契约

根目录 `openspec/` 只作为**单个复杂变更的契约层**，不得替代 `CORE_RESTRUCTURE_PLAN.md` 或承载第二套 next、总 backlog、优先级和退出标准。

- OpenSpec 可用性自检优先用：`openspec.cmd list --json`、`openspec.cmd status --change <change> --json`、`openspec.cmd validate --all --strict --json --no-interactive`；`openspec status --json` 不带 `--change` 报错不是初始化失败。
- 必须优先考虑 OpenSpec：改 `CAD_PLAN` 契约、真实 CAD 验证标准、能力登记 / 表 C 语义、Core 架构边界、跨多个模块的治理包或高风险流程。
- 可以不用 OpenSpec：单文件小 bugfix、普通训练 round、只刷新表 C、状态 / changelog / handoff 记录、小文案或链接修正。
- OpenSpec tasks 只允许放在 `openspec/changes/<change>/tasks.md`；不得新增根级 `openspec/tasks.md`。
- 如果 OpenSpec change 影响开发顺序、退出门槛或当前包范围，必须回写 `CORE_RESTRUCTURE_PLAN.md` 或明确说明它不改变主线。
- completed change 可以暂留在 `openspec/changes/` 作为活跃历史；归档前必须确认稳定 specs 和仓库引用同步，不能因为 `openspec list --specs` 为空就判断 OpenSpec 不可用。

## 交付默认简洁回复

面向用户的最终回复默认**不要附进度表、表单或表 A/B/C**。普通开发、调查、修复、绘图或规则更新完成后，用简洁自然段说明：本轮做了什么、关键证据、有没有风险或未验证项。

只有用户明确点名 **开发状态查询 / 进度 / 完整状态 / 交接 / 审计 / 表 A / 表 B / 表 C / 真实 CAD 实力 / 刷新表 C / 报进度表** 时，才使用进度表格；其中涉及真实 CAD 能力时，必须先报 **表 C 真实 CAD 实力主指标**。详细口径见 `docs/governance/cad-agent-rules.md` §0.4；任务包计数与 next 以 `docs/planning/任务清单.md` §0 为准。

**Agent 训练期例外（方案 B/C）：** 当 `docs/training/README.md` 与 `docs/training/cad-designer-growth-path.md` 所指的 **Agent 训练**（CAD Designer Agent 基础课程、任意场景案例 `projects/<case_id>/`、`开一轮训练`、用户未点名表 C/A/B）时，最终回复同样不要附进度表或表 A/B/C；只汇报课程 / 案例进展、CAD 证据路径与待你验收项。落图工序必须遵循该文档 **「理想链路（全局 · 训练期）」**（机器审计 → 截图 → Agent 自检 → 未过则自修，再请你验收）。训练交付回复还必须遵循 `docs/training/cad-common-sense-upgrade.md` 的低噪声模板：先说本轮结论，再说相对上一轮变化、机器证据证明了什么、没证明什么、请用户重点看哪里、用户怎样反馈最有用；不得只堆 handles、arc 数、gap / overlap 数字或截图。CAD Designer Agent 成长路径进度不等于表 C，也不代表完整施工图能力。

**状态查询口径：** 下列内容只在用户点名时展开为完整 **表 A / 表 B / 表 C**；完成开发包、修改 registry / coverage、处理回归或绘图不准时，也不要自动附进度表。普通交付只用自然段说明本轮结果、证据和风险。用户问「真实 CAD 实力 / 推进表 C / 表 C / 刷新表 C」时，必须先展开完整表 C。

**完整口径定义：**

- **表 A — 工程节奏**：总进度、Core 底座开发进度、Agent 多场景实现进度；默认 `总进度 = Core × 70% + Agent × 30%`，允许约 5–10 个百分点主观误差。
- **表 B — 任务清单三指令执行进度**：§3 能力证明、§4 一键推进 / 代码轨、§5 RCAD 烟囱包；`执行进度 ≈ status=done 包数 ÷ 本板块任务包总量`，§5 使用 `cad_status=verified` 包数。
- **表 C — 真实 CAD 实力**：`scripts/run_capability_coverage.py` 的机器值，包括 `cad_proof_coverage_percent`、`cad_strength_index_percent`、`scene_fragment_strength_percent`、`showcase_readiness_percent`、`cad_strength_headline_percent` 和最高已证 Ladder。

**禁止混用：**

- 表 A 的「工程完备度 / 工程节奏」≠ 表 B 的「台账包完成度」≠ 表 C 的「真实 CAD 实力」。
- 表 B 的 RCAD 烟囱通过 ≠ `cad_capability_registry` 已满 `verified`，也不等于“已经能画准施工图”。
- 普通回复可以不附表 C 数字，但只要进入开发状态查询、真实 CAD 能力汇报或表格口径，就不得省略表 C 主指标；任何时候都不得用 Core 进度、RCAD 高完成度、截图、dry-run 或 no-CAD benchmark 暗示真实 CAD 几何已证明。
- 各表百分比均不替代测试、benchmark、截图、created handles 回读或 `geometry_verified` 证据。

完成能力证明 / 代码轨 / CAD 补验相关包后，应同步更新 `docs/planning/任务清单.md` §0 的计数与 next；改登记表或 showcase 后须复跑 `run_capability_coverage.py` 并更新表 C。

## 训练工作台同步

根目录 `capability-map.html` 是训练工作台显示器，不是事实源。训练计划、智能体 Prompt、案例反馈、`projects/<case>/runs/**`、`libraries/reference_library`、`libraries/system_library`、capability registry 或表 C coverage 发生变化后，必须运行：

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\sync_training_workbench.py
```

同步脚本负责刷新 `output/validation_runs/capability-lab/cad_capability_coverage.json`、重建 `capability-map-data.js`，并运行 `scripts/run_training_workbench_agent_check.py` 检查责任智能体、Prompt source refs、表 C 快照和页面同步提示是否跑偏。未通过该脚本时，不得声称 HTML 已同步最新训练状态或真实能力边界。

训练验收、队列状态、learning ledger、Agent memory / Prompt addendum 等长期可追溯事实源必须登记在 `docs/training/training-sources.json`。`capability-map-data.js`、`capability-map.html`、sync report 只能作为派生快照，不得反向当作训练事实源。

本仓库维护的训练脚本在记录 `pass` 或队列 `completed` 后，应自动调用训练收尾同步入口，并在脚本 JSON 输出中写入 `postTrainingSync`；不得把“同步前端 / learning promotion / Agent check”作为每轮都需要用户额外提醒的手工步骤。`scripts/run_training_queue.py` 是当前参考实现：单项 `--decision pass` 后轻量同步，队列完成后完整同步。

**训练前数据防膨胀门禁：** 正式训练、focused 复训、队列推进、正式收尾型工作台同步或系统资产沉淀会产生新证据 / 快照 / debug / test artifact 前，主 Agent 必须先做数据防膨胀判断：`capability-map-data.js` 是派生快照，只能由 `scripts/build_capability_map_data.py` / `scripts/sync_training_workbench.py` 生成；后续生成策略要求 compact、避免重复兼容别名和无限增长，在脚本未实现 compact 前必须标为 `pending_implementation`，不得声称已生效，pretty 调试快照只能放 `output/debug/` 且不得当事实源。`output/debug/**`、`output/test_artifacts/**`、retry、dry-run、execution summary、旧截图和临时报告默认是短期产物；长期只保留 final acceptance report、queue state、learning ledger、Agent memory / Prompt addendum、必要 registry / 表 C 证据和最近人工复核 preview。任何清理 / 归档写入前必须先有 evidence-closure / retention dry-run：保护 `docs/training/training-sources.json` 中 active `fact_source`、learning ledger、Agent memory、Prompt addendum、表 C registry evidence、系统资产 registry / assets.json / native DWG、状态 / handoff / issues / case feedback 中仍引用的路径；若 active fact source 缺失、引用根未覆盖、候选仍被引用或会让 `report_path_missing` 变差，必须阻断并报告 `dataBloatGate=blocked`。`retention_report.json`、data-bloat audit report 和 workbench sync report 只能是 `diagnostic/derived`，不得登记为训练事实源，也不得让工作台用它们证明训练通过。A-to-A 合同遇到训练 / 资产 / 正式工作台收尾时，应把 `data_bloat_governance` 列入 hard gate；缺该门禁时不得声称训练收尾、工作台同步或产物清理已打通。

**训练停放区跟随规则：** 用户可以为了查看方便移动已经训练出的 `CODEX_PREVIEW` 训练面板。后续复训不得默认把训练目标按全画布最右侧无限外扩；应优先回读上一轮训练报告 / execution summary 中的 created handles，用这些句柄的当前位置和 bbox 作为训练停放区参考。只有上一轮 handles 缺失、被炸开、被删除或无法回读时，才退回按当前 `CODEX_PREVIEW` 全局 bbox 选择空白区。脚本输出应记录 `parking_anchor` / 等价字段，说明使用的是 `previous_handles`、`global_preview_bbox` 还是 `origin`。
**原位局部修复优先：** 用户指出局部错误、机器审计发现局部失败，或 Agent 自检发现局部文字 / 线型 / hatch / 标注 / 部件不对时，不得默认在旁边再完整画一遍。应先读取上一轮 `execution_summary` / created handles / 当前 CAD readback，生成 `repair_plan`：按 handle、bbox、图层、实体类型和错误原因定位 `target_handles`，只对这些对象执行 `update`、`delete_replace` 或 `add_missing`，并在原位置复验。用户明确开放删除编辑命令后，默认只授权删除 / 编辑 `CODEX_PREVIEW` 中被证据锁定的错误对象；不得扩大到整张图、全模型空间、全部可见对象、正式图层、保存或覆盖 DWG。只有旧 handles 缺失、目标已被炸开 / 删除、局部修复会破坏整体结构，或根因是全局坐标系 / 比例 / 布局错误时，才允许整块重画；重画前必须说明为什么不能局部修。
**训练范围硬边界：** 用户点名“任务 12 / 第 12 项 / 某个填充图案 / 某个比例测试 / 加深训练某一项”时，默认只执行该项或该子主题的轻量级 focused retraining，不得因为已有整批脚本就顺手跑完整队列。只有用户明确说“全部 / 整批 / 重新跑所有 / 刷新整个队列”时，才允许执行整批训练。若现有脚本没有 focused 入口，Agent 必须先补 focused 参数或询问是否允许放大范围；不得静默把单项请求扩大成 21 项、31 项或其它批量动作。focused 报告应记录 `scope.mode=focused`、`requestedCapabilityIds`、`scopeReason`，且不覆盖整批验收状态。
**训练轻重链路量化路由：** 用户说“试一下 / 快画 / 小动作 / 先看看 / 先别沉淀 / 不进训练 / 只画这个”时，默认走 `quick_trial`，总耗时目标 ≤ 2 分钟，只允许写 `CODEX_PREVIEW`，最多做 1 次 CAD 写入 + 1 次关键回读（如 handles、bbox、图层、hatch pattern / scale），不跑完整 validate / dry-run / 截图 / 工作台同步 / learning promotion；回复不超过 3 句，并明确“快试未沉淀”。用户说“训练某项 / 任务 X / 加深 / 某图案 / 某比例测试”时，默认走 `focused_retraining`，总耗时目标 ≤ 8 分钟，只覆盖点名能力或显式列表，必须记录 `scope.mode=focused` 和关键机器证据，默认不覆盖整批验收、不跑完整工作台同步。用户说“验收 / 沉淀 / 训练通过 / 记入工作台 / 整批 / 全部 / 刷新队列 / 推进表 C”时，才走 `formal_acceptance`，完整执行计划、校验、落图、审计、自检、必要截图和同步。若快试需要修改已有实体、超过 20 个新对象、涉及正式图层 / 保存 / 删除、用户要求可交付准确性，或关键回读失败，必须先升级为 focused / formal 或向用户说明原因，不得静默套重链路。
**未列入计划的复合任务：** 用户可以临场组合多个已训练或已登记能力，例如“给截图里的沙发标注尺寸”“按参考图画茶几并补尺寸”“识别门洞后补开启方向和编号”。这类任务默认**不**新增到 V2 训练地图，也不要求预先列出所有排列组合。Agent 必须先把任务拆成能力节点：输入来源（截图 / DWG / handles / 用户给定尺寸）、对象识别、尺度来源、绘图或标注意图、`CAD_PLAN` / 结构化意图、validate / dry-run、`CODEX_PREVIEW`、readback / audit。只有重复出现、暴露稳定失败模式、可做机器验收器或可复用 benchmark 时，才晋升为训练项、检查器或规则包。
复合任务的证据边界必须显式声明：只有截图时只能证明视觉定位和推断，不得声称真实 CAD 尺寸准确；截图加已知参照尺寸时可做比例估算但必须标注为推断；有 DWG / handles / 原 `CAD_PLAN` 回读时，才可把尺寸标注和几何检查提升为较强证据；用户直接给尺寸时，审计重点转为标注是否落在正确对象、文字/尺寸是否匹配、图层是否安全。任何视觉输入都不能替代 created handles 回读。
**系统资产沉淀协议：** 用户明确说“沉淀 XX 资产 / 把这个作为通用资产 / 收进资产库”时，默认执行系统资产四件套，不得只保留截图、训练报告或当前 DWG 预览对象。四件套为：机器契约（分类 `assets.json` / 标准 JSON）、CAD 原生资产位置（分类 `*_assets.dwg` / `.dwt`）、应用 / 验收工具、全局索引 `libraries/system_library/registry.json`。默认入口是 `scripts/sediment_system_asset.py`，协议说明见 `docs/architecture/system-asset-sedimentation-protocol.md`。
资产沉淀前必须先过 `pipeline_asset_governor` 资产库守门员；守门员判断来源边界、是否允许进入 clean reusable source、是否派发 `pipeline_asset_librarian` / `pipeline_asset_dwg_curator` / `pipeline_asset_reuse_auditor`，并在收尾输出 `polishHardeningDecision`。系统资产 DWG 不得作为训练画布搬运区，默认分为 `00_INDEX`、`01_CLEAN_ASSETS`、`02_PREVIEW_CARDS`、`03_REVIEW_QUARANTINE`、`99_EVIDENCE_LINKS`；训练标题、临时说明、边框、尺寸线、审计文字和证据路径不得进入 `01_CLEAN_ASSETS`。主 Agent 可以判断是否需要新增全局 Agent，但只能记录 reviewed package / OpenSpec / 全局规则更新需求，不得临时发明未登记 Agent。
主 Agent 对系统资产沉淀、系统资产 DWG 排版、仓库 / 货架 / 置物架 / 动线 / 可扩展货位 / 展示形式等任务，必须先生成 `a_to_a_task_contract` 并派发 `requiredAgents`；合同缺少任一必需 Agent 输出时，`workflow_dispatch` 必须以 `a-to-a hard gate` 阻断，不能进入完成口吻。高风险合同还必须写入 `mainAgentSelfCheck` 和 `dispatchDecision`：主 Agent 只允许动态加派已登记 Agent，未登记的新 Agent 只能进入 `additionalAgentRequests` 并标记 `needs_reviewed_package` / `needs_openspec_change`，不得临场激活或用于放行完成声明。资产沉淀固定要求 `pipeline_asset_governor`、`pipeline_asset_librarian`、`pipeline_asset_dwg_curator`、`pipeline_asset_reuse_auditor`；资产 DWG 仓库式布局还必须要求 `pipeline_visual_layout_reviewer` 输出 `visual_layout_review`，并显式通过 `layoutReadabilityAcceptable`、`aisleClearanceAcceptable`、`contentDensityAcceptable`、`sourceProofRolesSeparated`、`layerSemanticsAcceptable`、`nonScreenshotEvidenceChecked`。截图非空、对象数量正确、DWG 保存、机器回读通过或 `overlapCount=0`，都不能替代视觉仓库复审；源定义、proof panel、标签、证据和可复制内容必须分层分角色。仓库级检查入口为 `scripts/run_a_to_a_orchestration_gate_check.py`。
资产分类必须稳定：例如沙发进入 `libraries/system_library/furniture/seating/sofas/`，连续沉淀沙发 A / B 时更新同一个 `assets.json` 和同一个 `sofa_assets.dwg` 位置；绘图标准进入 `libraries/system_library/drawing_standards/basic/` 并预留 `standard_assets.dwg`。当前协议可以先登记合同并写 `nativeDwgExists=false`，不得把“已登记系统资产合同”说成“已导出 / 已保存原生 DWG”。
**系统资产 DWG 保存、复审与复用授权：** 用户说“沉淀 XX 资产 / 通用资产 / 收进资产库”时，默认授权创建、打开 / 激活、写入并保存对应系统资产 DWG（`libraries/system_library/**/**/*_assets.dwg` 或协议解析出的 `nativeDwg`），保存后回读活动文档路径与 `Saved=true`，并默认打开供人工复审；此授权不覆盖当前业务 DWG、原始图纸、正式图层、全模型空间清理或非系统资产文件。用户说“调用 / 复用 / 插入 / 套用 / 放到当前 DWG”，或语义强匹配已沉淀资产时，先检索 `libraries/system_library/registry.json`，默认入口为 `core.assets.system_asset_reuse` / `scripts/reuse_system_asset.py`；写当前 DWG 默认只写 `CODEX_PREVIEW`，必须输出 matched asset、source spec、target layer、created handles、readback count 和 `savedCurrentDwg=false`，不得保存当前业务 DWG。缺少精确来源边界时返回 `needs_precise_native_source`，不得从 whole_modelspace、current_screen、all_visible 或训练面板硬拷贝。
**真沉淀与复用联通硬门禁：** 系统资产沉淀不得只写 metadata、截图或不可见样式定义就声称完成。`metadata_only` / `candidate` 可以作为早期候选；一旦 `style_standard` 声称 `native_style_definition_written` 或 `nativeWrite=written_to_standard_assets_dwg`，必须同时登记 `nativeVisiblePanelEvidence` 或等价可见 native 证据（created/readback 数量、报告、截图、系统资产 DWG 保存状态）。一旦资产 lifecycle 标为 `verified`，必须登记 `reuseWorkflowProbe`（至少 `status=ready`、`readyTaskCount>0`、`sourceSpec`、registry `encodingPreflight=pass`、`savedCurrentDwg=false`）或真实 `reuseReplay`（created handles + readback）。`scripts/sediment_system_asset.py --verify` 必须执行这些 claim gates；缺可见证据或复用探针时返回 fail，不得用“已沉淀 / 可复用 / A-to-A 已打通”口吻交付。
**CAD 语义规则库与跨 DWG 工作流：** 白话进入资产复用、资产沉淀、线型表、局部修复或其它高风险 CAD 链路前，必须先参考 `core.assets.semantic_rules`；prompt 只能调用和解释这些规则，不能用临场判断替代。系统资产复用前必须运行 registry 文本 `encodingPreflight`，坏中文或 mojibake 返回 `asset_registry_encoding_failed`，弱匹配只给候选，不生成 ready 计划；线型表类输出必须通过 `core.training.linetype_table_audit` 的中文、无填充、样线格 containment、自适应行高、样式 readback 和证据边界审计。复合跨 DWG 请求走 `build_system_asset_reuse_workflow` / `scripts/reuse_system_asset.py --workflow` 拆成多个 `asset_reuse_*` 子任务，允许 partial 阻断；单个复用计划只有 copy 返回 created handles 且 `readbackStatus=ok` 才算 `asset_reused`，CLI / 报告必须是严格 JSON。
系统资产必须写明状态流和晋升边界：`candidate` 只表示候选，`systemized` 表示已沉淀到规则 / Prompt / 检查器或训练证据，`verified` 才表示已有复用验收或 CAD readback 证据，`deprecated` 表示历史保留不优先使用。资产条目还必须保留 `retrieval`、`native.layoutPlan` v2、`libraryGovernance`、`versioning`、`verification`、`feedbackLoop`、`nativeVisiblePanelEvidence` / 等价可见证据和 `reuseWorkflowProbe` / `reuseReplay`；`scripts/sediment_system_asset.py --verify` 同时验证元数据合同和声明级门禁，若 `native DWG geometry`、`native visible asset evidence`、`executable reuse workflow probe` 或 `CAD insertion replay` 仍在 `notChecked`，不得声称对应层级已经完成。重复 asset id 且尺寸 / blockName 冲突时，必须显式选择更新、拒绝或生成变体，不得静默覆盖。
对象资产 block 导出前必须先过来源边界门禁：只允许 `selected_handles`、`created_handles`、`active_dwg_handles`、`explicit_bbox` 或 `named_block` 这类精确来源进入 `block_export`；禁止默认把 `whole_codex_preview`、`whole_modelspace`、`current_screen`、`all_visible`、`training_panel` 或 `global_preview_bbox` 打成 block。若来源不清，资产只能保持 `metadata_only` / `candidate`，并记录 `includedHandles` / `excludedHandles` 后再进入后续原生导出。样式标准如线宽、线型、尺寸、文字、引线必须走 `style_standard` / `style_export`，不得误做 block。
训练脚本收尾还必须执行产物保留策略，避免每轮堆积一次性脚本和中间证据。默认只长期保留：最终验收报告、队列状态、必要的 learning ledger / Agent memory / Prompt addendum，以及最近一份用于人工复核的预览图；中间 retry 目录、临时 CAD_PLAN / dry-run / execution summary、旧截图和一次性脚本在验收沉淀后应删除或移入归档。删除前必须先跑引用闭合 / retention dry-run，确认最终报告、训练事实源、工作台派生数据、learning ledger、Agent memory、Prompt addendum、表 C registry、状态 / issue / handoff 和训练错误记录不再引用这些临时路径；不得为了“瘦身”删除或移动仍可复盘的 CAD handles/readback 证据。
**基础训练不是封存交付状态：** `systemized/pass` 只表示该训练项在当时证据下通过并已沉淀，不表示以后不能再改。后续复杂任务、对象课程或场景案例如果暴露基础操作不扎实，必须回流到对应基础能力：记录弱点和触发任务，修改相关脚本 / Prompt / 检查器 / 规则，再对基础项做二次或多次加强训练，并回测原复杂任务。复训结果应追加新证据和 learning promotion，旧证据保留为历史，不得用“基础项已完成”拒绝修基础能力。
**自动化训练超时与熔断保护：** 大面积铺开自动化 CAD 训练前，所有训练脚本和 Agent 执行链路必须有单步 watchdog。默认每个 CAD / 脚本 / 截图 / 回读 / 同步子动作最多等待 30 秒，包括 CAD COM 等待、validate / dry-run / execute、created handles 回读、截图、training queue 单项推进、post-sync 和 Agent check。确需超过 30 秒的子动作，必须在规则或脚本输出中写明原因、分段检查点和最长等待，不得无上限等待。

任一子动作超时后，Agent 不应立刻把问题交回用户；应先读取 stdout / stderr、最近报告、队列状态或 CAD 会话状态，判断是否是 CAD 窗口、COM 可见性、文件锁、路径、依赖、截图工具或快照过期等问题，并做一次有限自救：重连、刷新、重取景、重跑该子步骤或改用 deferred 等最小恢复动作，尽量保留已产生证据。自救同类重试最多 1 次，或最多 2 个相邻恢复动作，不得无限 retry。

同一训练项连续 2 次 30 秒超时，或同一队列连续 3 个子动作超时 / 失败，必须熔断暂停，进入 `blocked` / `needs_user_review` 或等价状态。脚本输出和记录应写明 `timeoutSeconds: 30`、`selfRecoveryAttempted`、`circuitBreakerTriggered`、`blockedReason`、卡在哪一步、已自救什么、保留了哪些证据和下一步建议。熔断后不得继续无人值守落图、保存 DWG、覆盖原图、删除实体或改正式图层，也不得把 partial output 说成训练通过或工作台已同步。

日常打开工作台优先用 `start_training_workbench.bat`；它会先同步，再用本地 `http.server` 打开 `capability-map.html`。直接双击 HTML 仍可查看上一次快照，但不能保证最新。仅为查看而刷新派生快照、且不改变训练事实源 / 验收状态 / 资产证据 / 清理写入时，属于 `workbench_snapshot_refresh`，不用升级为完整 `data_bloat_governance` hard gate，也不得借此声称正式训练或资产收尾已完成。

**用户口令（§0 四指令，详见 `docs/planning/任务清单.md`）**

| 用户说 | Agent 默认动作 |
| --- | --- |
| **一键推进** | §4 代码轨 1 包 |
| **能力证明** / **覆盖率** | §3 `V-PROOF` 1 包 |
| **CAD 补验** / **开 CAD 了** | §5 `RCAD` 1 包（真实 CAD） |
| **真实 CAD 实力** / **推进表 C** / **表 C** | §0.1：优先抬高表 C 的 1 个 `V-PROOF` + 链式 RCAD + registry 回写 + 复跑 coverage；**先报表 C** |
| **刷新表 C** | 仅 `run_capability_coverage.py` + 汇报表 C，不新开包 |

## Core 优先

本仓库是通用 CAD Agent Core Lab。可复用能力放入 `core/`，共享资源放入 `libraries/`，项目专属资料放入 `projects/`，只有场景差异放入 `agents/<scenario>/`。

不要把仓库改成工装专用、家装专用或 CAD-MCP 专用项目。场景 Agent 必须保持轻量，并复用 Core。

## 不从白话直接跳到 CAD

自然语言必须先变成 `CAD_PLAN` 或明确的结构化绘图意图，再执行 CAD 绘制；只有明确的临时低风险测试可以例外。真实落图前必须先校验和 dry-run。

## 强制绘图准确性门槛

在告诉用户 CAD 图纸已经完成或准确之前，Codex 必须用证据核验：

- 预期对象、尺寸、基点、图层、文字、标注和允许误差
- `scripts/validate_plan.py` 结果
- `scripts/dry_run_plan.py` 结果
- 使用新架构时，对应的 `core.plan_engine` 入口结果
- `CODEX_PREVIEW` 上的实际 CAD 输出
- `scripts/render_preview.py --capture-autocad-window`（必要时加 `--execution-summary`）截图；**默认保留 CAD/IDE 分屏**，仅 COM 重取景 + `PrintWindow`；PrintWindow 失败时才 `--force-foreground`。整屏 `--capture-screen` 仅作 fallback
- 实际输出与预期 `CAD_PLAN` 或结构化意图的对比

如果实际输出和预期不一致，Codex 不得把错误结果当成完成品交给用户。必须诊断差异，做最小安全修复，重新绘制或运行，并再次验证。

## 修复交付必须运行

以后所有修复默认必须先运行覆盖原问题的最小实际链路，再交付给用户；不能只改代码、只跑单元测试，或只写“未运行真实 CAD”的边界说明就把 CAD 相关修复当成完成。

- 普通代码 / 文档 / 规则修复：至少运行对应测试、校验、审计或格式检查，并在最终回复说明命令和结果。
- 影响 CAD 落图、截图、训练、runner、验证、资产复用 / 沉淀、局部修复的改动：除单元测试外，默认还要运行一条代表性实际链路；涉及真实 CAD 的，优先连接当前 AutoCAD，在 `CODEX_PREVIEW` 或只读截图 / 回读路径中复验，不保存当前业务 DWG、不修改正式图层。
- 影响截图功能的修复：必须至少运行 `scripts/render_preview.py --check`，并在 AutoCAD 可用时运行 `scripts/render_preview.py --capture-autocad-window`；有 `execution_summary`、`target_handles` 或 `repair_plan` 时必须传入，让截图聚焦本次任务或局部修复对象。
- 真实 CAD / GUI / COM 因沙箱、权限、窗口、授权或活动 DWG 不可用而失败时，Codex 必须先按 blocker 流程自救并在需要时申请外部执行；仍不可用时最终回复标为 `blocked` / `not_run` / `not_verified`，不得使用“完成”“已修好”“已交付准确”口吻。

## 卡壳或绘图不准流程

当用户说“画不准”“画不出来”“不对”“继续修”，或 Codex 无法证明图纸准确时，按 `docs/runbooks/blocker-playbook.md` 执行。

最低必跑探针：

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py 'scripts\self_check.py'
& $py 'scripts\render_preview.py' --check
```

如果需要视觉证据且用户没有禁止截图，保存一个检查点：

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py 'scripts\render_preview.py' --capture-autocad-window --output 'output\previews\manual-check.png'
```

如果截图或回读不可用，应说明暂时无法证明准确性，并优先补齐缺失的验证机制，再声称完成。

## 保护用户 DWG

- 默认使用 `CODEX_PREVIEW`。
- 默认不保存当前 DWG。
- 不覆盖原始 DWG 文件。
- 未经用户明确批准，不修改正式图层、不删除实体、不执行不可逆 CAD 操作。
- 用户允许删除 / 编辑时，先按 `repair_plan` 限定到具体 handles / bbox / 图层；默认只处理 `CODEX_PREVIEW` 中本轮或上一轮创建并已回读的错误对象，不做全局清空或整图删除。

## 保持记录更新

当 CAD Agent 规则、脚本、测试、工作流文档或状态发生变化时，更新：

- `docs/status/current.md`
- `docs/status/changelog.md`
- 如果变更源自失败、风险或调试教训，更新 `docs/status/issues.md`

每完成一个 PlanMD 开发包，还必须更新 Agent 交接包汇总：

- `docs/handoffs/current.md`（按固定 9 项模板追加该包章节，供 Codex 校验）
- `docs/handoffs/package-index.md`（同步全量包索引）
- 索引说明见 `docs/handoffs/README.md`
