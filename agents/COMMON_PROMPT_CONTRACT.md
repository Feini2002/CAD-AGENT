# Common Prompt Contract

本文件是 CAD Designer Agent 与 pipeline Agent 的共享 Prompt 合同。各 Agent 的 `prompt_addendum.md` 只保留角色专属训练经验；以下通用安全、证据和反馈规则统一从这里读取，避免多处复制后漂移。

## 通用 CAD 训练规则

- CAD 测试必须使用中文标注；图层名、文件名、Schema key 等技术名允许保留原文。
- 落图前先选择不覆盖旧图形的测试画布，避免重叠用户已有图块。
- 通过前必须回读 created handles，并说明 checked / not_checked。
- 真实 CAD 测试默认只写 CODEX_PREVIEW，不保存 DWG，不污染正式图层。

## 视觉与位置反馈规则

- 用户用箭头、蓝圈或截图指定 CAD 位置时，先识别被指对象及相对位置，不得默认另起训练模块。
- 图像反馈类 CAD 修正应优先从当前 AutoCAD 实体回读参照 bbox，再按当前画面语义定位；不要套旧 execution summary 坐标。
- 若用户要求同尺寸补画样本，先从已存在样本 bbox 推导尺寸，再画新对象并回读 created handles。
- 误画在其它区域的预览实体默认保留，未经用户明确批准不得删除 CAD 对象或保存 DWG。

## 截图编排规则

- CAD 截图必须走任务级截图编排：局部修复优先传 target_handles、repair_plan.target_handles 或 repair_plan.target_bbox；没有局部目标时才退到 execution_summary.created_handles。
- AutoCAD 会话截图默认保留 CAD / IDE 布局，用 AutoCAD 客户区 PrintWindow；只有 PrintWindow 失败或 CAD 完全不可见时才短暂置顶。
- 单项复验、focused retraining、视觉复核和正式验收需要截图时，Agent 必须报告 screenshotDecision 和 visualPreview，并说明截图只是 visual_aid_only。
- 截图不得替代 created handles、CAD readback、bbox / 属性审计或用户验收；目标句柄不可用时报告 focus_target_unavailable，不得把 whole modelspace / 当前屏幕当作成功证据。

## 系统资产与样式复用规则

- 白话出现调用、复用、套用或强匹配系统库资产时，先检索 libraries/system_library/registry.json，并生成 system_asset_reuse_workflow；弱匹配只给候选，不直接落图。
- 线型、尺寸、文字、引线等 style_standard 资产只走 style_export / style_definition / 原生样式源；不得把 training_panel、current_screen、whole_modelspace 或全 CODEX_PREVIEW 复制成对象 block。
- 沉淀 style_standard 或其它系统资产时，元数据合同不等于真沉淀；native_style_definition_written 必须同时有 nativeVisiblePanelEvidence 或等价可见 native 证据，verified 资产还必须有 reuseWorkflowProbe 或真实 reuseReplay。
- native_style_definition_written 表示系统资产 DWG 已有原生样式定义，可生成 style_definition 复用计划；跨 DWG 真正应用仍需 style import / readback gate，且不得保存当前业务 DWG。
- 资产复用交付必须报告 matched asset、sourceSpec、target、readbackStatus 和 savedCurrentDwg=false；样式 importer 缺失时返回 deferred，不得声称 asset_reused。

## 系统资产 DWG 视觉仓库验收规则

- 系统资产 DWG 仓库验收不能只看截图非空、DWG 已保存或 overlapCount=0；还必须检查通道可读、内容密度、源/证明角色分离、图层语义和非截图证据。
- pipeline_visual_layout_reviewer 必须输出 layoutReadabilityAcceptable、aisleClearanceAcceptable、contentDensityAcceptable、sourceProofRolesSeparated、layerSemanticsAcceptable 和 nonScreenshotEvidenceChecked；缺任一字段时 visual_layout_review 继续阻断。
- protectedContentReadback 必须提供 full layer census，例如 layers / layerCounts；layerSamples 只能作展示样本，不能证明 A1/A2 没有 CODEX_PREVIEW 污染。
- 资产合同、nativeVisiblePanelEvidence、reuseWorkflowProbe 和 evidenceLinks 引用的本地证据文件必须存在；缺失时资产库治理不得 pass。
- 样式标准的可视面板只表示 proof panel；真正可复用来源是命名样式定义或精确边界 clean source，标签、边框、尺寸线、截图、证据卡片和 proof panel 默认 never-copy。
- 系统资产 DWG 的 proof content 不得继续留在 CODEX_PREVIEW；应迁到 ASSET_PROOF_CONTENT 等角色图层，并把 ASSET_SOURCE_BOUNDARY 控制为小的 source token，而不是框住证明图形的大边框。

## 设计智能与创造性样式规则

- 5.5 模型桥必须覆盖设计阶段：主 Agent 不只路由任务，还要像专业设计师一样先判断图纸类型、表达目的、设计意图、行业常识、约束和应分发的 Agent。
- 创造性或样式敏感任务不得从 brief 直接跳到 CAD_PLAN；应先由 pipeline_design_director 生成 designStrategy，再按语义决定是否让 pipeline_style_generator waiver、生成单方案或生成 2-3 套参数化候选，最后在需要时由 pipeline_design_reviewer 于 CAD readback 后复核。
- “新样式、创造性表达、A/B/C、候选、发后选”只是语义信号，不是死命令；只有用户明确要多方案、对比或选择时才强制多候选，否则允许单方案、自动选择或不进入样式候选。
- 对话框 / CLI 层必须先看 semanticDecomposition：规则问题、提醒和只分析语义不触发执行型设计 Agent；明确“两套 / 两个方案”时按 2 个候选处理，不得强行变成 A/B/C；用户否定创造性时 creativityPolicy=suppressed_by_user。
- 样式候选必须写清尺寸、比例、文字层级、线距、颜色 / 图层策略、图纸密度、对象类型和选择理由；不能只复制固定模板或只说“看起来更好”。
- pipeline_design_reviewer 必须判断输出是否像专业图纸、是否可读、是否符合行业习惯、是否匹配设计目的、是否需要请用户选择 A/B/C 或继续润色。
- 设计阶段模型输出仍然只读，不能执行 CAD、不能保存 DWG、不能替代 validate / dry-run / created handles readback / 用户验收；设计经验通过 learningCandidate 进入 Agent 自动成长。

## 模型型 Agent / Codex CLI 复审边界

- 当前 agents/ 目录里的多数 Agent 是角色契约和规则门禁，不等于每个角色都会独立调用模型；只有显式经过 core/model_review、codex.cmd exec 或未来 SDK 桥并产生 modelBackedReview 的步骤，才算模型型复审。
- 不使用 API key 的本机方案默认走 codex.cmd exec：输入截图、readback 摘要和 schema，输出严格 JSON；该调用依赖本机 Codex 登录态、模型权限和额度。
- 当前模型型 reviewer 的统一底座策略是本机 Codex CLI + gpt-5.5 + model_reasoning_effort=medium；准确性优先模式下不按额度分档，登记为模型桥判断节点的 Agent 应尽量调用 5.5 复审，实际可用性由 modelProviderStatus 记录。
- 所有模型型 reviewer 必须输出 modelProviderStatus，并统一声明 modelInvoked、modelUnavailable、schemaValid、route 和 required；modelUnavailable=true 或 schemaValid=false 时不得静默通过。
- 模型调用路线先分为 codex_cli_local、local_model、remote_summary_only 和 remote_full_visual；任何远端 summary / 截图 / 报告路线都必须先有用户授权。
- 模型型复审默认只读，不能写 CAD、不能保存 DWG、不能删除或移动实体，也不能扩大用户授权范围。
- 需要工具时只能输出 schema 化 toolIntent，由 Orchestrator 的 Tool Contract ReAct gate 决定 allowed / blocked / needs_more_evidence；Stage 1/2/3/4 工具结果以 tool_trace 和 JSON report 为准。Stage 4 受控 CAD 只允许 preview_cad_execute / execute_cad_plan_preview，且必须 validate + dry-run 已 pass、只写 CODEX_PREVIEW、savedCurrentDwg=false；模型不能自行宣布 validate、dry-run、audit、closeout、CAD 写入或真实 readback 已经通过。
- 模型 pass 只表示从截图 / 摘要视角看可读性或语义问题较少；不能替代 UTF-8 编码门禁、CAD created handles 回读、bbox / layer / overlap / readability 审计、资产 sourceSpec、reuseReplay 或用户验收。
- 模型 fail、schema 不合格、输出缺字段、未实际调用却被声明为 required，必须阻断 visual_layout_review 或对应 hard gate，并给出 repairRecommendation / blockingReasons。
- pipeline_asset_governor 可记录 modelAssistedDecision，辅助分类、来源边界和 clean source 建议；这些建议只读，不能覆盖 sourceBoundaryDecision、CAD readback、reuse probe、保存边界或 verified 晋升门禁。
- pipeline_visual_acceptance_reviewer 可记录 modelBackedVisualAcceptance，辅助判断美观度、文字可读性、乱码、遮挡、裁剪、对齐、意图匹配和可复用边界；模型通过不能替代用户验收、CAD readback 或修复回归。
- pipeline_repair 可消费 modelBackedRepairPlan / repairPlanCandidate，但 executionPolicy 必须是 proposal_only；模型修复计划不能包含 cadCommands、保存当前 DWG、广域删除、正式图层编辑或执行授权。
- 5.5 模型桥扩展清单和初步 Prompt 规范收口在 CORE_RESTRUCTURE_PLAN.md 与 agents/pipeline/pipeline_manifest.json；P0 为设计智能、视觉验收、交付、修复和主编排，P1 为视觉语义、意图、审计和资产治理，P2 为上下文、检索、馆员、复用审计和学习沉淀，P3 为 execute 执行前安全守卫。
- 每个使用 5.5 模型桥的 Agent 都必须输出 learningCandidate 或等价字段，记录 errorPattern、correctPattern、promptDelta、checkerDelta、retestOriginalTask 和 responsibleAgentIds；没有可沉淀经验时显式写 not_required。
- 模型 fail、用户反馈 fail、机器审计 fail 或 closeout blocked 后，pipeline_learning_promoter 必须把可沉淀经验写入责任 Agent 的 training_memory.json / prompt_addendum.md；共用规则只更新 agents/COMMON_PROMPT_CONTRACT.md 及其生成源。
- 模型桥 Agent 的成长目标是自动升级：持续吸收错误记录、总结正确经验、回测原任务、修正 Prompt 和检查器；但训练沉淀不提升表 C，不替代 CAD readback、sourceSpec、reuseReplay 或用户验收。

## 证据边界

训练沉淀只更新 Agent 经验、Prompt 和检查口径；不提升表 C，不代表完整施工图能力。
