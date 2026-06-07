# CAD Agent 长期治理规则

本文件只保留长期、可复用、跨任务的治理规则。它不是 `PlanMD`，不承载全局 backlog，也不记录短期进度。会话启动卡片、用户口令和即时安全边界以根目录 `AGENTS.md` 为入口；本文件负责说明这些规则的长期归属、迁移原则和收口标准。

修改本文件时必须同步记录到 `docs/status/changelog.md`；若修改来自失败、回归、误判或安全边界收紧，还要记录到 `docs/status/issues.md`。纯文档治理不证明 CAD 能力提升。

## 0. 事实源与反膨胀原则

每个事实只允许有一个权威源文档，其它文档只能放一句摘要和链接。若同一事实需要合并，必须使用四动作记录：

| 动作 | 含义 |
| --- | --- |
| `add` | 新事实进入权威源 |
| `replace` | 新段落替代旧段落，旧段落删除或降级 |
| `demote` | 已完成、历史性或低频信息迁入历史 / 状态 / changelog |
| `reference` | 非权威文档只保留一句话和链接 |

长期文档的职责如下：

| 文档 | 职责 |
| --- | --- |
| `AGENTS.md` | 会话启动卡片、用户口令、即时安全边界 |
| `CORE_CONTEXT_BRIEF.md` | 短上下文入口，只放下一轮需要直接引用的活跃事实 |
| `CORE_RESTRUCTURE_PLAN.md` | 唯一 `PlanMD`、主线顺序、退出标准 |
| `CORE_STATUS.md` | 能力矩阵、成熟度和证据摘要 |
| `docs/status/current.md` | 当前状态，不堆长历史 |
| `docs/status/changelog.md` | 历史流水和完整包 ID 记录 |
| `docs/status/issues.md` | 失败、回归、风险和教训 |
| `docs/architecture/**` | 架构解释、协议和长期设计 |
| `docs/planning/**` | 辅助执行清单，不成为第二套主计划 |

根目录新增临时 Markdown 必须写明退出路径：归档、迁移到 `docs/**`、合并到权威源，或在完成后删除。否则它不能变成长期入口。

## 1. 仓库定位

本仓库是通用 CAD Agent Core Lab，不绑定某张 DWG、某类家装图纸、某台电脑或某个 agent 软件。`core/` 放通用能力，`agents/<scenario>/` 放轻量场景差异，`libraries/` 放跨场景资源，`projects/` 放真实或样例项目资料。

场景能力不得绕开 Core 直接执行 CAD。新增场景能力必须说明它复用哪个 Core 能力、需要哪些场景词汇 / 偏好 / 对象表，以及验证证据在哪里。

## 2. 主计划与架构归并

`CORE_RESTRUCTURE_PLAN.md` 是唯一主计划。任何新增待办、优先级调整、退出门槛变化或复杂治理包，都先回写主计划，再更新辅助文档的引用。

当前仓库级主线是架构归并画布工程；权威执行入口见 `CORE_RESTRUCTURE_PLAN.md` §0.2，架构解释见 `docs/architecture/system-architecture-convergence.md`。归并期内，正式对象训练、整批训练、表 C 推进和系统资产大沉淀处于暂停或显式授权状态。

旧表 A/B/C、V-PROOF、RCAD、训练地图、资产库、多 Agent、Worker / bridge、模型桥、截图和工作台都必须能映射到统一任务生命周期：系统入口、任务对象、决策编排、能力与证据、执行工具、审计修复、沉淀成长。

## 3. 绘图链路

用户自然描述必须先形成结构化绘图意图或 `CAD_PLAN`，再进入校验、dry-run、预览绘制、readback / audit。低风险快试可以走轻量链路，但必须说明它未沉淀，不能说成正式训练或交付准确。

任何 CAD 交付声明都需要说明：

- 预期对象、尺寸、基点、图层、文字 / 标注和允许误差。
- `validate`、dry-run、执行报告、created handles、bbox / layer / entity type 回读。
- 实际输出与结构化意图的差异。
- 截图只作为视觉辅助，不能替代实体回读和几何证据。

若影响 CAD 落图、截图、训练、runner、验证、资产复用 / 沉淀、局部修复或真实 CAD 证据链，单元测试外还要跑一条代表性实际链路。真实 CAD / GUI / COM 不可用时，结论必须写 `not_run`、`not_verified` 或 `blocked`。

## 4. DWG 安全边界

常规写入使用启动卡片指定的预览层；不得无授权保存当前业务 DWG、覆盖原图、修改正式图层、清空全模型空间或删除全部可见对象。

删除、替换、清理和局部修复必须先声明 `target_handles` 或 `scope_bbox`，生成 victim set preview / dry-run，并列出受影响对象的 handle、layer、bbox、entity type 和所属 zone。没有精确范围时只能阻断或做只读分析。

局部错误优先原位修复：读取上一轮 execution summary、created handles 和当前 CAD readback，生成 `repair_plan`，只对证据锁定的对象做 `update`、`delete_replace` 或 `add_missing`。只有旧 handles 缺失、对象被删除 / 炸开、局部修复会破坏整体结构，或根因是全局坐标 / 比例 / 布局错误时，才允许整块重画。

## 5. 状态口径

普通交付用自然段说明本轮结果、证据和风险，不主动附进度表。只有用户点名状态、进度、交接、审计、表 A/B/C、覆盖率或刷新表 C 时，才展开表格。

成熟度必须拆成三层：

- 底座证据覆盖：机器 coverage、registry、benchmark、真实 CAD 证据覆盖。
- Agent 任务成熟度：端到端任务、训练案例、用户反馈、局部修复和学习闭环。
- 项目交付准备度：真实项目 / 完整施工图交付边界，不能由底座 coverage 自动推出。

任何百分比都不能替代测试、benchmark、截图、created handles 回读或 `geometry_verified`。历史百分比留在 changelog、history 或明确标注为历史快照的状态段落中。

## 6. 训练链路

训练和复训按最小充分原则路由：

| 模式 | 触发语义 | 必需证据 | 不自动执行 |
| --- | --- | --- | --- |
| `quick_trial` | 试一下、快画、小动作、先看看、不进训练 | 最小结构化意图、一次写入、一次关键回读 | 完整校验、截图、自检、工作台同步、learning promotion |
| `focused_retraining` | 训练某项、任务 X、加深、某图案 / 比例测试 | 点名能力、focused 报告、局部落图、关键 readback | 整批队列、覆盖整批验收、完整工作台同步 |
| `formal_acceptance` | 验收、沉淀、训练通过、整批、全部、刷新队列、推进表 C | 完整计划、校验、dry-run、落图、audit、截图、自检、报告、同步 / coverage | 无 |

用户点名单项时不得静默扩大成整批。若现有脚本只有整批入口，应先补 focused 参数，或询问是否允许放大范围。

训练脚本、CAD 调用、截图、回读、工作台同步和 Agent check 都要有 30 秒子动作 watchdog。一次有限自救后仍失败，应熔断并记录 `timeoutSeconds`、`selfRecoveryAttempted`、`circuitBreakerTriggered`、`blockedReason`、保留证据和下一步。

基础训练通过不代表永久封存。后续复杂任务暴露基础能力不稳时，要回流到对应基础项，追加新证据和 learning promotion；旧证据保留为历史版本。

## 7. 证据保留与数据瘦身

训练计划、案例反馈、Agent memory、Prompt addendum、learning ledger、registry 和最终验收报告是长期事实源。`capability-map-data.js`、HTML、sync report、retention report、debug report 和 data-bloat audit 只能作为派生或诊断展示。

正式训练、复训、队列推进、正式工作台同步、资产沉淀或仓库级治理会生成新证据前，必须判断哪些产物是长期事实源、哪些是短期候选、哪些是派生快照、哪些因仍被引用而不可清理。

清理 / 归档写入前必须先跑 retention dry-run 或等价 evidence-closure gate。若 active fact source 缺失、引用根未覆盖、候选仍被引用，或清理会让报告路径缺失变差，必须阻断。

## 8. 系统资产沉淀与复用

用户明确要求沉淀通用资产时，执行系统资产四件套：

| 层 | 事实源 |
| --- | --- |
| 机器契约 | 分类 `assets.json` / 标准 JSON |
| CAD 原生资产 | 分类 `*_assets.dwg` / `.dwt` |
| 应用 / 验收工具 | `scripts/sediment_system_asset.py` 或对应 ensure / verify 工具 |
| 全局索引 | `libraries/system_library/registry.json` |

`metadata_only` / `candidate` 只能表示候选。声称 native 写入时，必须有可见 native 证据、created/readback 数量、报告、截图和保存状态；声称 `verified` 时，还必须有复用 workflow probe 或真实 reuse replay。

对象资产导出前必须过来源边界：只允许 `selected_handles`、`created_handles`、`active_dwg_handles`、`explicit_bbox` 或 `named_block`。不得把全模型空间、当前屏幕、全部可见对象、训练面板或全局预览 bbox 直接打成 block。

资产复用必须先查系统资产 registry，再生成结构化复用计划。匹配到资产但缺少精确来源时，返回 `needs_precise_native_source`；不得改成临场重画或硬拷贝。

仓库式系统资产 DWG 必须有视觉可读性复审：源定义、proof panel、标签、证据和可复制内容分层分角色；截图非空、对象数量正确、DWG 保存或 bbox 不相交都不能单独证明仓库排版合格。

## 9. 多 Agent 与模型桥

模型型 Agent 是只读判断 / 复审 / 建议层，不直接授权 CAD 写入、删除、移动、保存、正式图层编辑、覆盖 DWG、资产晋升或状态百分比声明。

凡声称多 Agent 真实协作，必须有 run package、上游 / 下游 JSON 引用、task contract、dispatch plan、agent outputs、冲突 / 阻断记录和 closeout decision。缺少这些证据时，只能说 Prompt Pack ready、单 Agent 调用或机制建议。

模型调用必须先有 trace，再有 prompt。trace 至少记录 `traceId`、`agentId`、任务类型、最终 prompt、schema 快照、sanitized command、cwd、timeout、输入摘要、stdout / stderr、schema 校验、normalized output 和 gate decision。

模型如需工具，必须输出 `toolIntent`，由 orchestrator 校验 schema、permission class、risk level、target scope 和 forbidden effects。只读工具、候选写入、确定性验证和受控 CAD intent 必须分阶段管理；工具返回 fail 或证据不足时，下游 closeout 只能阻断或标记未验证。

主 Agent 认知提升必须有机器可读 before / after 证据：至少能指出 route、requiredAgents、tool choice 或 blocking reason 发生变化。`cognitiveLoopSummary`、`behaviorChangeProof`、prediction reconciliation 和 Agent Task Maturity 指标都只证明 no-CAD 判断链边界；若没有行为改变，只能称为机制建设。`confidence`、`selfUncertainty`、预测准确率、模型 pass 或 no-CAD fixture 不得替代 CAD hard gate、source boundary、no-save/no-delete、表 C 或用户验收。

## 10. 复合任务与沉淀边界

临场复合任务不要求预先列入训练地图。Agent 应拆成输入来源、对象识别、尺度来源、绘图 / 修改 / 标注意图、结构化意图、校验、预览、readback / audit。

证据来源必须写清：只有截图时只能证明视觉定位和推断；截图加已知参照尺寸只能证明比例估算；有 DWG、created handles、原计划或用户明确尺寸，才可进入对应几何 / 标注审计。

单次成功或失败优先写案例反馈、训练错误或 learning ledger。只有重复失败、可机器检查、可泛化为课程族，或需要新增稳定验收器时，才升级为训练项、benchmark、规则包或 Core 检查器。

## 11. 收口验证

纯文档治理至少运行相关文档审计、单元测试和 diff 检查。代码或 CAD 链路治理至少运行对应单测、仓库审计和代表性链路。无法运行时必须说明原因、失败点、保留证据和未验证风险。

治理包收尾前必须确认：

- 权威源、引用源和历史源清楚。
- 短入口没有承载长历史。
- 临时 sidecar 有退出路径。
- checker 没有新增永生文档膨胀告警，或剩余告警有明确 owner 和下轮计划。
- 最终回复不把文档治理、截图、dry-run、no-CAD benchmark 或模型 pass 说成真实 CAD 端到端能力。
