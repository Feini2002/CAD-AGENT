# CAD Agent 长期规则

这些规则用于约束后续开发和绘图行为。规则可以被修改，但每次修改都要写入 `docs/status/changelog.md`，如果是因为错误或测试失败导致的修改，还要写入 `docs/status/issues.md`。

## 0. 通用开发包定位

本文件夹是通用 CAD Agent 开发包，不绑定当前家装图、不绑定当前 DWG、不绑定当前电脑。

本仓库也不绑定单一 agent 软件。Codex、Cursor 或其它同类 agent 工具都应遵守同一套 `CAD_PLAN`、Core、训练、验证和交接规则；文档中的具体工具名只代表可选载体、历史文件名或某个工具专属能力，不得被解释为强制单一软件。

任何规则、Schema、脚本和对象库都应优先服务可迁移能力。具体项目的信息必须进入项目上下文文件，例如 `cad_context.json`，不要写死在通用规则里。

适用范围包括但不限于：

- 住宅家装
- 商业工装
- 零售店铺
- 办公空间
- 餐饮空间
- 展厅展陈
- 其他 CAD 平面绘制、布置、标注和修改场景

## 0.1 默认中文沟通

面向用户的说明、状态汇报、方案讨论、追问和最终结论默认使用中文。代码、命令、路径、文件名、Schema 字段、JSON key、工具名和 API 名称可以保留英文或原文。

如果外部 Skill、插件或工具模板提供英文流程，Codex 应先理解其含义，再用中文转述给用户；除非用户明确要求英文，不要把英文模板原样作为面向用户的输出。

## 0.2 上下文缓存友好入口

日常 CAD Agent 开发、状态恢复和普通调试默认先读取 `AGENTS.md` 与 `CORE_CONTEXT_BRIEF.md`，再按任务读取详细文件。不要每轮都无差别全文读取计划、变更流水和历史问题记录。

需要完整展开上下文的情况：

- 用户要求完整状态汇报、交接、审计或复盘。
- 要执行或修改 `CORE_RESTRUCTURE_PLAN.md` 中的 Phase。
- 遇到卡壳、测试失败、绘图不准、CAD 环境问题或回归。
- 要修改规则、状态、变更记录或问题记录。

`CORE_CONTEXT_BRIEF.md` 必须保持短、稳定、可扫读；详细历史继续留在 `docs/status/changelog.md` 和 `docs/status/issues.md`，不要搬进短入口。

## 0.3 单一 PlanMD 与开发状态文档职责

当前唯一 `PlanMD` / 开发主线文件是 `CORE_RESTRUCTURE_PLAN.md`。根目录没有独立 `plan.md`；用户提到 `PlanMD`、`plan.md`、主计划或主 plan 时，默认指 `CORE_RESTRUCTURE_PLAN.md`。

`CORE_RESTRUCTURE_PLAN.md` 负责决定当前活跃工作队列、Phase 顺序、优先级、Decision Gate 和退出标准。其他 Markdown 只能作为辅助文档：可以补充状态、证据、规则、执行剧本、设计依据、历史和问题教训，但不得形成第二套“下一步”。如果辅助 MD 需要新增待办、调整优先级或改变退出标准，先同步 `CORE_RESTRUCTURE_PLAN.md`。

`PlanMD` 不得改变系统根方向：通用 Core Lab、Core 优先、`CAD_PLAN` 中间层、真实 CAD 证据门槛、场景 Agent 轻量化和保护用户 DWG。若文档治理与这些边界冲突，以边界为准，先修文档，不改方向。

开发状态文档按职责维护：

- `CORE_CONTEXT_BRIEF.md`：短上下文入口，只写当前结论、目标入口和按需展开表。
- `CORE_RESTRUCTURE_PLAN.md`：唯一 PlanMD、主计划和下一阶段执行路线。
- `CORE_STATUS.md`：Core 能力矩阵和成熟度。
- `docs/status/current.md`：当前进展页，不堆长历史。
- `docs/status/changelog.md`：历史变更流水。
- `docs/status/issues.md`：失败、回归、风险和排障教训。
- `docs/decisions/cad-agent-decisions.md`：方向和架构决策。
- `docs/planning/phases/*.md`：Phase 辅助执行剧本，只展开主计划中的工作项。

如果未来判断根目录 Markdown 过多，优先迁移到 `docs/history/`、`docs/architecture/`、`docs/decisions/` 或 `docs/verification/`，不要直接删除仍有历史依据的文档。

## 0.4 开发状态查询与进度口径

后续每次完成 CAD Agent 相关改动后，Codex 可以在内部判断是否影响开发进度、任务台账或表 C，但**不要在普通最终回复里默认输出进度表、表单或百分比表格**。普通交付优先用自然段说明本轮完成内容、验证证据和风险边界。

只有用户明确点名 **开发状态查询 / 进度 / 完整状态 / 交接 / 审计 / 表 A / 表 B / 表 C / 真实 CAD 实力 / 刷新表 C / 报进度表** 时，最终回复才使用进度表格。该百分比是产品和工程节奏判断工具，不是严格项目管理 KPI，允许有 5-10 个百分点的主观误差。

**Agent 训练期：** 见 `AGENTS.md`、`docs/training/README.md` 与 `docs/training/cad-common-sense-upgrade.md`——未点名开发状态或表 C 时，不附进度表；训练交付回复必须说明本轮结论、相对上一轮变化、机器证据证明了什么、没证明什么、请用户重点看哪里，禁止只堆 handles、arc 数、gap / overlap 数字或截图。

**训练期 / CAD 会话截图默认：**

1. **默认保留布局**：左 CAD / 右 IDE 分屏时，**不要**把 AutoCAD 全屏或强置顶；仅当窗口最小化时 `SW_RESTORE`。
2. **再**按本次任务目标重取景：局部修复时优先 `target_handles`、`repair_plan.target_handles`、`repair_plan.target_bbox` 或显式 `target_bbox`；没有局部目标时才退到整批 `execution_summary.created_handles`。用户中途误拖 / 误缩也须自动拉回。
3. **只截** AutoCAD 客户区（`--capture-autocad-window` + 默认 **`PrintWindow`**，IDE 挡在 CAD 上也不会被拍进去）；禁止默认整屏 `--capture-screen`（仅 fallback）。
4. **仅当 PrintWindow 失败或 CAD 完全被遮挡**时，才用 `--force-foreground` 置顶一次并重试。
5. 截完后用户可立即切到其它软件；Agent 不得长时间占前台。

推荐：`prepare_autocad_for_capture` / CLI 一条命令（默认 `preserve_layout`）。截图仍 `visual_aid_only`。

**状态查询必须保留：**

- **表 C 主指标**：`cad_strength_headline_percent`，必须先报；机器值以 `output/validation_runs/capability-lab/cad_capability_coverage.json` 为准。
- **本轮证据**：说明跑了哪些测试、benchmark、coverage、CAD readback；百分比不得替代证据。
- **表 A 折叠值**：`总进度`，可括号附 `Core` / `Agent`。
- **表 B 相关轨道**：只报本轮触达的中文轨道名（能力证明 / 代码轨 / CAD 补验）；未触达时写“本轮未改变任务台账”即可。

**完整展开条件：**

只有用户明确要求完整状态汇报、交接、审计、进度盘点、对比、开发状态、表 A/B/C、表 C、真实 CAD 实力或刷新表 C 时，才展开进度表格。完成开发包、修改 registry / showcase / coverage、处理回归、绘图不准或口径争议时，不自动触发表格；普通回复只说明本轮结果、证据和风险。用户说「真实 CAD 实力」「推进表 C」「表 C」「刷新表 C」时，先展开完整表 C，A/B 可摘要。

**完整表 A — 工程节奏**

- `总进度`、`Core 底座开发进度`、`Agent 多场景实现进度`（默认 `总进度 = Core × 70% + Agent × 30%`）。

**完整表 B — 任务清单三指令执行进度**（`docs/planning/任务清单.md` §0）

- `能力证明`（§3）、`一键推进`（§4 代码轨）、`RCAD 烟囱包`（§5）；展开时须带 `done/总量` 或 §5 的 `verified` 包数/总量。
- 口径：`done 包数 ÷ 该板块任务包总量`；新增需求入表时分母变大，百分比可能下降。
- 表 B ≠ 表 A；亦 ≠ 表 C（真实 CAD 实力）。

**完整表 C — 真实 CAD 实力**（`scripts/run_capability_coverage.py`）

- `cad_proof_coverage_percent`、`cad_strength_index_percent`、`scene_fragment_strength_percent`、`showcase_readiness_percent`、**`cad_strength_headline_percent`（主指标）**。
- 主指标 = `min(实力指数, L3+片段, showcase)`；`showcase_count=0` 时主指标为 0%，须同时报加权指数与 L3+ 子指标。
- 表 C ≠ RCAD 烟囱完成度；primitive 矩形 smoke verified 不计为「施工图能力」。

**用户口令「真实 CAD 实力」/「推进表 C」**（`docs/planning/任务清单.md` §0.1）：编排 §3 `V-PROOF` + 链式 RCAD + registry 回写 + 复跑 coverage；**不是** §4 一键推进。「刷新表 C」只复跑 coverage、不新开包。

当前基准估算见 `CORE_STATUS.md`、`docs/status/current.md` 与 `output/validation_runs/capability-lab/cad_capability_coverage.json`。本规则文件不写死“当前表 C”百分比；历史百分比只允许出现在 `docs/status/changelog.md`、`docs/history/`、`docs/planning/archive/` 或明确标注为历史快照的段落中。

## 0.5 能力证明体系（路线 F）

- 架构：`docs/planning/capability-proof-architecture.md`；任务包：`docs/planning/任务清单.md` §3（`V-PROOF-00`~`79`）。
- 每个可声称能力须在 `cad_capability_registry.json` 占一行，含 `claim_level`（`none` / `deferred` / `smoke` / `verified` / `showcase`）。
- **路线 E / RCAD** 只负责真实 CAD 执行；通过后须回写 registry，不得只留报告不入表。
- 新能力：**先登记（V-PROOF-01）再开发或 RCAD**，禁止「只写代码不登记」。
- 对外声称 CAD 已通过：仅当对应行 `claim_level` 为 `verified` 或 `showcase`，且有可复跑 `cad_case` 与 `geometry_verified` 路径。

估算规则：

- 新增一个测试或一次 CAD 截图通过，不得直接大幅提高百分比；只有形成可复验能力、文档同步和明确边界后，才小幅上调。
- 发现回归、验证缺口或之前结论夸大时，可以下调百分比。
- 百分比变化达到约 2 个百分点以上，或用户要求状态汇报时，同步 `CORE_STATUS.md` / `docs/status/current.md`。
- 任何百分比都不得替代真实验证证据；涉及 CAD 几何准确仍必须看 `readback_report.json`、`cad_capability_probe.json` 和关键 checks。

## 0.5 Core / 场景 Agent 边界

当前仓库存在多个 `agents/<scenario>/` 目录和 scene benchmark，但它们的成熟度必须分级表达：

- `Core 底座`：通用 schema、workflow、`CAD_PLAN`、CAD IO、验证、benchmark、读图、对象、图块和安全门禁。
- `Scene Alpha 壳层`：场景 preferences、词汇、默认参数、排序权重、解释模板和边界扫描，只证明多场景可复用同一 Core。
- `Scene Beta 能力包`：某个场景有对象体系、微场景、失败样本和 non-CAD benchmark，可证明场景语义可跑通。
- `Scene Product 场景产品`：某个真实业务场景有脱敏样本、图块策略、真实 CAD smoke、用户确认流和交付边界，才可接近可用 Agent。

因此，不得把 `office/residential/restaurant` 的 preferences、rules、Alpha 验收或 scene beta non-CAD benchmark 写成“多场景 Agent 已产品化完成”。真正的场景开发要进入该场景的对象体系、业务规则、图块 metadata、项目样本、失败样本、真实 CAD readback 和用户确认闭环。

以工装为例，只有当开放办公、会议室、前台接待等子场景的办公桌 / 工位组 / 会议桌 / 文件柜 / 前台等对象、规则、图块和真实 CAD smoke 都有证据后，才可以提升为工装 Scene Product。详细边界见 `docs/architecture/core-scene-agent-boundaries.md`。

未来场景能力采用“主底座中控按需调用”的架构：

- `Core Orchestrator` 是唯一主中控。
- `Scene Router` 只在用户明确场景或项目 manifest 指定场景时启用场景。
- 没有明确场景时必须返回 `no_scene`，只调用通用 Core。
- 场景能力以 `Scene Capability Module` 形式独立放在 `agents/<scenario>/`，可包含 registry、preferences、对象清单、微场景、图块映射和解释模板。
- 场景模块不得直接执行 CAD、做通用几何、碰撞、回读或验证；这些仍归 Core。
- 如果未来允许场景专属 adapter 函数，必须先在 `CORE_RESTRUCTURE_PLAN.md` 登记接口、边界扫描和测试，不能直接绕开当前 `agents/` 无 `.py` 的 Alpha 规则。

## 1. 不直接从白话画 CAD

用户用白话或语音提出需求后，Codex 必须先生成 `CAD_PLAN`。

只有以下情况可以直接画：

- 用户明确要求做快速临时测试。
- 图形非常简单，并且只画在测试图层。
- 已经说明这是一次临时验证，不作为正式流程。

## 2. 默认保护原图

- 不直接覆盖原始 DWG。
- 不默认保存当前 DWG。
- 不默认修改正式图层。
- 默认画到 `CODEX_PREVIEW` 图层。
- 大批量绘制前必须先 dry-run。

## 2.1 默认不落文字和尺寸标注

面向用户生产或交付的 CAD 输出，默认不生成中文文字标注、不生成英文文字标注，也不默认生成尺寸标注。

这不是删除能力。`include_label`、`include_dimensions`、`draw_text`、`add_dimension` 等文字和尺寸能力必须保留；只有在用户明确要求加名称、编号、说明、文字、尺寸、尺寸线或标注时，才在对应 `CAD_PLAN` 中显式启用。

能力探针、回归测试、benchmark 或专门验证文字 / 尺寸能力时可以启用这些开关，但必须把它们标记为测试或能力证据，不能当成普通生产出图默认值。

能力探针、回归测试和 benchmark 如果必须绘制文字、尺寸、箭头或说明性对象，必须写入 `CODEX_DIAGNOSTIC` 或等价诊断层；`CODEX_PREVIEW` 用户可见生成层默认只保留本轮几何结果。验证报告应分别统计预览层和诊断层，截图或交付口径不得把诊断层残留当成用户生成图块的一部分。

写入 `CODEX_DIAGNOSTIC` 时必须显式标记 `layer_role="diagnostic"`；没有诊断角色的诊断层写入应被 guard 拦截，避免 `CODEX_DIAGNOSTIC` 演变成第二个普通出图层。

对话、dry-run 报告和验证报告仍应说明对象、尺寸、基点、图层和允许误差；这类说明不等于在 DWG 中落文字实体或尺寸实体。

## 2.2 原位局部修复优先

当用户指出局部错误，或机器审计 / Agent 自检发现局部对象不对时，Codex 不得默认在旁边新开区域完整重画一份。优先动作是读取上一轮 `execution_summary`、created handles 和当前 CAD readback，生成 `repair_plan`，在原位置只修错的对象。

`repair_plan` 至少写清：

- `target_handles` / `target_bbox`：要编辑或删除的实体句柄和范围。
- `entity_types`：文字、尺寸、线、hatch、block reference、polyline 等实体类型。
- `failure_reason`：乱码、样式不对、缺线、错线、重叠、位置偏差、比例错误等。
- `operation`：`update`、`delete_replace`、`add_missing` 或 `no_change`。
- `neighbor_guard`：相邻对象或表格线、样例线、参考对象是否必须保持不动。
- `verification`：修复后需要回读的 handles、bbox、属性、图层和截图视角。

用户明确开放删除 / 编辑命令时，只表示允许 Codex 对 `CODEX_PREVIEW` 中被证据锁定的错误对象做局部删改；不得扩大为清空整张图、删除全模型空间、删除全部可见对象、修改正式图层、保存、覆盖或执行不可逆操作。若错误只是文字乱码，应只更新文字内容 / text style，或删除对应文字句柄后在原 bbox 内补回；没有错误的表格线、样例线、hatch、标注和参考对象不得重画。

只有在旧 handles 缺失、对象被炸开或删除、局部修复会破坏整体拓扑，或根因来自全局坐标系、比例、布局框架错误时，才允许整块重画。整块重画前必须说明局部修复为什么不可行，并尽量先清理或替换同一范围内的旧错误对象，而不是把新图无限向旁边漂移。

## 2.3 修复交付必须运行实际链路

所有修复默认要在交付前运行覆盖原问题的最小实际链路。普通代码、文档或规则修复至少运行对应单元测试、校验、审计或格式检查；CAD 相关修复不能只停在单元测试或报告字段检查。

凡改动影响 CAD 落图、截图、训练、runner、验证、资产复用 / 沉淀、局部修复或真实 CAD 证据链，必须在单元测试外再运行一条代表性实际链路。若 AutoCAD 可用，优先在当前真实 CAD 会话中复验；写入仍只允许 `CODEX_PREVIEW` 或诊断层，默认不保存当前业务 DWG、不修改正式图层、不扩大删除范围。若修复只影响截图或只读视觉复核，至少运行 `scripts/render_preview.py --check`，并在 CAD 可用时运行 `scripts/render_preview.py --capture-autocad-window`；有 `execution_summary`、`target_handles`、`target_bbox` 或 `repair_plan` 时必须传入，证明截图聚焦的是本次任务或局部修复对象。

如果真实 CAD / GUI / COM 因沙箱、权限、窗口、授权、文件锁或活动 DWG 不可用而失败，Agent 不能直接把问题交回用户，也不能把修复称为完成。必须先按 `docs/runbooks/blocker-playbook.md` 自救：读取 stdout / stderr、最近报告和 CAD 会话状态，必要时申请外部执行；仍不可用时，报告写 `blocked` / `not_run` / `not_verified`，并列出已运行命令、失败原因、保留证据和下一步。

## 3. 每个 CAD 动作都要可解释

执行前要能说明：

- 画什么。
- 画在哪。
- 尺寸是多少。
- 图层是什么。
- 哪些信息是用户明确说的。
- 哪些信息是 Codex 推断的。

## 4. 每次开发都要更新记录

只要创建、移动、修改了 CAD Agent 相关文件，就更新：

- `docs/status/current.md`：当前到哪一步。
- `docs/status/changelog.md`：改了什么，为什么改。
- `docs/status/issues.md`：如果遇到问题，记录现象、原因、修复。

## 5. 先小闭环，再扩展

新能力按这个顺序开发：

```text
白话例子
-> CAD_PLAN 示例
-> Schema 校验
-> dry-run 输出
-> 预览绘制
-> 回读验证
-> 扩展到更多对象
```

不要先做大系统。

## 6. 文件职责要清楚

- `core/` 放通用 CAD Agent 底座能力，是后续主要开发区域。
- `agents/` 放轻量场景 Agent，只写场景差异、默认偏好和专用 workflow。
- `libraries/` 放跨场景资源，例如块、对象、风格、材料、尺寸、人体工学和图层标准。
- `projects/` 放真实或样例项目资料，不污染通用规则。
- `scripts/` 放兼容旧命令的薄包装器，真实实现逐步迁入 `core/`。
- `drivers/` 放兼容旧导入的薄包装器，真实驱动逐步迁入 `core/cad_io/`。
- `schemas/` 放过渡期 schema 兼容副本，正式 schema 逐步迁入 `core/schemas/`。
- `docs/` 放架构、路线、决策、治理、验证、历史和 Phase 辅助执行剧本；不承载独立 PlanMD。
- `skills/` 放给 Codex 使用的 CAD Skill 草稿，后续逐步对齐 Core 架构。

## 7. 跑偏检查

如果某个功能不能回答下面问题，就暂停开发：

```text
1. 它是否是两个以上场景会复用的通用能力？
2. 如果是，为什么不放在 core？
3. 如果不是，它属于哪个 agents/<scenario>？
4. 它需要的共享资源是否应该进入 libraries？
5. 它的项目资料是否应该进入 projects？
6. 它最终如何转成 CAD_PLAN 或明确结构化绘图意图？
7. 校验、dry-run、执行和验证结果怎么看？
```

## 7.1 自动化训练超时与熔断保护

自动化训练 CAD 任务不得依赖无上限等待。训练脚本、CAD 调用、截图、回读、工作台同步和 Agent check 都必须按子动作设置默认 30 秒 watchdog；确需更长等待时，必须提前写明原因、分段检查点和最长等待。

30 秒超时后，Codex / Agent 先自救，不直接把问题丢给用户：读取 stdout / stderr、最近报告、队列状态和 CAD 会话状态，判断是否是 CAD 窗口、COM 可见性、文件锁、路径、依赖、截图工具或快照过期等问题；随后只做有限恢复，例如重连、刷新、重取景、重跑该子步骤或改用 deferred。相同子动作最多重试 1 次，或最多连续执行 2 个相邻恢复动作。

出现以下任一情况必须熔断暂停：同一训练项连续 2 次 30 秒超时；同一队列连续 3 个子动作超时 / 失败；超时后无法确认 CAD 输出是否安全。熔断时进入 `blocked` / `needs_user_review` 或等价状态，记录 `timeoutSeconds: 30`、`selfRecoveryAttempted`、`circuitBreakerTriggered`、`blockedReason`、卡点、自救动作、保留证据和下一步建议。

熔断后不得继续无人值守落图、保存 DWG、覆盖原图、删除实体或改正式图层；不得把 partial output、过期快照或未完成 post-sync 说成训练通过、工作台已同步或真实 CAD 能力已证明。

## 7.2 基础训练允许回流复训

训练项进入 `systemized/pass` 只代表当时的训练输入、机器证据、Agent 自检和沉淀记录通过，不是永久封存的交付状态。CAD Designer Agent 在后续对象课程、复杂场景或真实 CAD 案例中，仍可能暴露基础命令、图层纪律、闭合、回读、block 引用、layout / plot 或安全回滚等基本功不稳。

出现这类问题时，不得用“基础项已经训练完成”来跳过修复。Agent 必须做回流判断：把复杂任务中的失败归因到一个或多个基础训练项，记录触发案例、失败症状和缺失证据；必要时修改基础脚本、Prompt addendum、检查器、规则或训练数据；随后重新跑对应基础项的二次 / 三次加强训练，并回测原复杂任务是否因此改善。

复训应追加新的验收报告、learning promotion 和工作台同步结果。旧 `pass` 证据保留为历史版本，不直接删除或覆盖；如果新证据推翻旧假设，应在 `docs/training/training-errors.md` 或 `docs/status/issues.md` 说明口径变化。

复训停放区应尊重用户移动后的查看位置。若上一轮训练报告或 execution summary 记录了 created handles，后续复训先回读这些 handles 的当前位置和 bbox，并把它们作为训练停放区参考；不得因为用户移动了面板，就退回按全画布最右侧继续外扩。只有旧 handles 无法回读时，才使用全局 `CODEX_PREVIEW` bbox 选择新的空白区。报告中应记录 `parking_anchor` / 等价字段，便于判断本轮是跟随 `previous_handles`、退回 `global_preview_bbox`，还是从 `origin` 开始。

## 7.3 复训范围不得自动放大

用户点名单个训练项、某个子主题或截图里的局部模式时，Agent 必须按最小充分范围执行 focused retraining。例如“任务 12 加深训练”只允许重训第 12 项；“这个填充图案做不同比例测试”只允许围绕该 hatch pattern 和比例组生成对比，不得重新跑整批 21 项或 31 项。

整批训练只在用户明确说“全部 / 整批 / 重新跑所有 / 刷新整个队列”时执行。若当前只有整批脚本，没有 focused 入口，正确动作是先补 `--only` / `selected_capability_ids` / 子范围参数，或询问用户是否同意扩大范围；不得静默把轻量级需求扩大成完整队列。

focused 训练报告必须写入 `scope.mode=focused`、`requestedCapabilityIds`、`scopeReason` 和必要的子参数（如 hatch pattern / scales）。focused 证据可追加到训练事实源或 learning ledger，但不应覆盖 full-batch `completed` 证据，也不得冒充“整批重新验收通过”。

## 7.4 训练轻重链路量化路由

训练期 CAD 动作按最轻可证明原则路由。用户语义较轻时，不得默认套完整训练闭环；用户要求沉淀或验收时，才进入完整链路。

| 模式 | 触发词 / 语义 | 默认预算 | 必跑证据 | 默认跳过 |
| --- | --- | ---: | --- | --- |
| `quick_trial` | “试一下”“快画”“小动作”“先看看”“先别沉淀”“不进训练”“只画这个” | ≤ 2 分钟 | 最小结构化意图；只写 `CODEX_PREVIEW`；1 次 CAD 写入；1 次关键回读（handles / bbox / 图层 / hatch pattern / scale） | 完整 validate / dry-run、截图、自检文档、工作台同步、learning promotion、coverage |
| `focused_retraining` | “训练某项”“任务 X”“加深”“某图案”“某比例测试” | ≤ 8 分钟 | 只覆盖点名能力；focused 校验或 dry-run；局部落图；关键 readback；`scope.mode=focused` 报告 | 整批队列、覆盖整批验收、完整工作台同步 |
| `formal_acceptance` | “验收”“沉淀”“训练通过”“记入工作台”“整批”“全部”“刷新队列”“推进表 C” | 不设总时长；子动作仍受 30 秒 watchdog | 完整计划、validate / dry-run、`CODEX_PREVIEW`、readback / audit、必要截图、Agent 自检、报告、post-sync / coverage | 无 |

`quick_trial` 回复不超过 3 句，必须说明“快试未沉淀”，不得声称训练通过、工作台已更新、表 C 提升或可交付准确。若快试预计新增对象超过 20 个、需要修改已有实体、涉及正式图层 / 保存 / 删除、关键回读失败、超过 2 分钟仍无关键证据，或用户要求正式准确性，必须先说明原因并升级到 `focused_retraining` / `formal_acceptance`，不得静默执行重链路。

训练收尾必须经过 `promotionGate`。正式训练或复训通过后，gate 至少要声明 `updateTrainingSource`、`updateWorkbench`、`updateAgentCalibration`、`updateBaseRules`、`updateTaskRules`、`updateChecker` 和 `retestOriginalTask` 七项决策。`quick_trial` 必须保持 `promotionLevel=observation`，不得写 Agent 校准或工作台已沉淀状态；底座规则、单项规则和检查器 delta 必须标为 `needs_reviewed_package`，不能由训练脚本静默写入长期规则。

## 7.5 未列入计划的复合任务动态编排

训练计划只列原子能力、代表性课程和必要验收器，不穷举所有业务组合。用户可能临场提出多个已有能力的组合任务，例如“截图里的沙发标注尺寸”“按参考图画对象并补尺寸”“识别已有门洞后补开启方向”。这类任务默认走动态编排，不因为计划中没有同名条目就拒绝，也不把每个组合追加进 V2 训练地图。

Agent 必须先拆解复合任务：

```text
输入来源
-> 对象 / 场景识别
-> 尺度来源判断
-> 绘图 / 修改 / 标注意图
-> CAD_PLAN 或结构化意图
-> validate / dry-run
-> CODEX_PREVIEW
-> readback / audit / checked-not_checked
```

`evidence_source` 必须写清：只有截图时只能说明视觉定位和推断；截图 + 已知参照尺寸只能说明比例估算；DWG、created handles、原 `CAD_PLAN` 或用户明确尺寸才能进入对应几何 / 标注审计。视觉识别、截图裁剪或比例估算不得被写成真实 CAD readback。

复合任务的沉淀规则：单次成功或失败优先写入案例反馈、`training-errors.md` 或 learning ledger；只有重复失败、可机器检查、可泛化为课程族、或需要新增稳定验收器时，才升级为训练项、benchmark、规则包或 Core 检查器。

完整系统任务链路见 `docs/architecture/cad-agent-task-chain.md`。复合任务不能只停在“执行成功”或“训练通过”单侧闭环；凡涉及新失败模式、精准复训、资产复用 / 沉淀或 Agent 分工变化，都要判断是否需要同步底座规则、单一任务规则、检查器、Prompt / memory 和 A-to-A 校准。

训练、复训、正式收尾型工作台同步、资产沉淀或仓库级治理还必须带数据防膨胀与证据闭合判断。主 Agent 不能只说“清理 output”：必须先区分 `protected`（active 事实源、final report、queue state、learning ledger、Agent memory / Prompt addendum、表 C / registry / 系统资产证据和仍被状态文档引用的路径）、`candidate`（短期 debug、test artifacts、retry、dry-run、execution summary、旧截图和临时报告）、`blocked`（事实源缺失、引用根未覆盖、候选仍被引用或证据断链会变差）和 `derived`（`capability-map-data.js`、HTML、sync report、retention report、data-bloat audit）。`derived` 不得反向登记为训练事实源；清理 / 归档写入前必须先有 retention dry-run 或等价 evidence-closure gate。A-to-A 合同若涉及训练收尾、正式工作台收尾或系统资产沉淀，应显式包含 `data_bloat_governance` hard gate；缺该 gate 时不得声称 A-to-A 已打通或产物治理完成。只为查看而刷新派生工作台快照属于轻量 `workbench_snapshot_refresh`，不得借此宣称正式训练 / 资产收尾完成。

## 7.1 系统资产沉淀协议

当用户明确说“沉淀 XX 资产 / 把这个作为通用资产 / 收进资产库”时，Codex 必须执行系统资产沉淀协议，而不是只保存截图或当前 DWG 预览结果。

系统资产沉淀采用四件套：

| 职责 | 事实源 |
| --- | --- |
| 机器契约 | 分类 `assets.json` / 标准 JSON |
| CAD 原生资产位置 | 分类 `*_assets.dwg` / `.dwt` |
| 应用 / 验收工具 | `scripts/sediment_system_asset.py` 或后续 `ensure_*` / `verify_*` |
| 全局索引 | `libraries/system_library/registry.json` |

同类资产必须进入稳定分类包。例如沙发进入 `libraries/system_library/furniture/seating/sofas/`，沙发 A / B 追加到同一个 `assets.json` 和同一个 `sofa_assets.dwg` 位置；绘图标准进入 `libraries/system_library/drawing_standards/basic/`，线宽、线型、尺寸样式、文字和引线样式共用 `standard_assets.dwg` 位置。

当前协议可以先登记合同并标记 `nativeDwgExists=false`。这只证明系统资产位置、机器契约和索引已建立；不得声称已经导出原生 DWG、已保存当前 DWG、或新 CAD 文件自动具备该资产。用户说“沉淀 XX 资产 / 通用资产 / 收进资产库”时，默认授权 Codex 对对应分类的系统资产 DWG 执行必要的创建、打开 / 激活、写入和保存；只要本轮向该系统资产 DWG 添加、替换或修复了原生 CAD 内容，必须保存并回读活动文档路径、`Saved=true` 和关键实体 / 样式证据。沉淀收尾时默认打开 / 激活对应系统资产 DWG，供用户人工复审。此授权不覆盖用户当前业务 DWG、原始图纸、正式图层、全模型空间清理或非系统资产文件的保存 / 覆盖；这些操作仍需另行明确授权和 CAD readback 验收。

真沉淀必须过可见 native 与复用联通门禁。`metadata_only` / `candidate` 可以只登记合同；但 `style_standard` 只写不可见 DimStyle、文字样式或线型定义时，不能说“资产 DWG 里已经有可复审资产”。一旦资产记录 `native_style_definition_written` 或 `nativeWrite=written_to_standard_assets_dwg`，必须同时登记 `nativeVisiblePanelEvidence` 或等价可见 native 证据：系统资产 DWG 中可见图元 / 面板、created/readback 数量、报告、截图、保存状态和 `savedCurrentDwg=false`。一旦资产标为 `verified`，还必须登记 `reuseWorkflowProbe` 或真实 `reuseReplay`，证明白话复用能经 registry 编码预检、语义匹配、`system_asset_reuse_workflow` 和 `sourceSpec` 生成 ready 计划；否则 `scripts/sediment_system_asset.py --verify` 应返回 fail。

系统资产 DWG 仓库验收必须过视觉可读性门禁。截图非空、DWG 已保存、created handles 可回读、`visualClearanceAudit.overlapCount=0` 只能证明“脚本写进去了且没有 bbox 相交”，不能证明仓库排版合格。正式通过前必须同时有 `visualReadabilityAudit.status=pass`：A1/A2 与 A2/B 通道满足最小宽度、A1/A2 内容宽度占比不过密、proof content 不在 `CODEX_PREVIEW`、`ASSET_SOURCE_BOUNDARY` 只作为小 source token 而不是框住 proof panel 的大边界，源定义 / proof panel / 标签 / 证据 / 可复制内容分层分角色。A-to-A `pipeline_visual_layout_reviewer` 必须显式输出 `layoutReadabilityAcceptable`、`aisleClearanceAcceptable`、`contentDensityAcceptable`、`sourceProofRolesSeparated`、`layerSemanticsAcceptable`、`nonScreenshotEvidenceChecked`，缺任一字段时不得进入完成口吻。

高风险 A-to-A 编排还必须有主 Agent 自检和动态加派决策。`mainAgentSelfCheck` 用于声明主 Agent 身份、任务理解、责任边界和已知限制；`dispatchDecision` 用于说明哪些已登记 Agent 被加派、为什么加派、还缺哪些输出。主 Agent 可以判断是否需要新增全局 Agent，但未登记 Agent 只能进入 `additionalAgentRequests`，状态为 `needs_reviewed_package` 或 `needs_openspec_change`；不得临场激活、不得加入本轮 `effectiveRequiredAgents`、不得替代真实 CAD / 资产 / 视觉复审证据。

对象资产做 `block_export` 前必须先过来源边界门禁，只允许 `selected_handles`、`created_handles`、`active_dwg_handles`、`explicit_bbox` 或 `named_block` 等精确来源；不得把整个 `CODEX_PREVIEW`、全模型空间、当前屏幕、全部可见对象、训练面板或全局预览 bbox 默认打成 block。来源不清时只能登记为 `metadata_only` / `candidate`，并写明 `includedHandles`、`excludedHandles` 和 `antiContamination` 缺口；线宽、线型、尺寸、文字、引线等样式标准必须走 `style_standard` / `style_export`，不得误做对象 block。

系统资产还必须有晋升门槛：`candidate` 表示候选，`systemized` 表示已沉淀到规则 / Prompt / 检查器或训练证据，`verified` 表示已有复用验收或 CAD readback 证据，`deprecated` 表示历史保留不优先使用。每条资产必须保留 `retrieval`、`native.layoutPlan`、`versioning`、`verification`、`feedbackLoop`、可见 native 证据和复用 workflow / replay 证据。元数据验收通过不等于原生 DWG 几何复用通过；只要 `native DWG geometry`、`native visible asset evidence`、`executable reuse workflow probe` 或 `CAD insertion replay` 仍在 `notChecked`，最终回复不得把对应层级描述为 verified CAD-native asset。重复 asset id 且关键字段冲突时，必须显式选择 `update_existing`、`reject` 或 `new_variant`，不得静默覆盖。

系统资产复用也必须走同一资产库，而不是临场重画。用户明确说“从 XX 资产调用 XX / 复用 XX / 插入 XX / 套用 XX / 放到当前 DWG”，或需求语义明显匹配已有资产时，先查 `libraries/system_library/registry.json`，再由 `core.assets.system_asset_reuse` / `scripts/reuse_system_asset.py` 生成复用计划。复用到当前 DWG 默认只写 `CODEX_PREVIEW`，必须回读 created handles 和目标图层，且默认不保存当前业务 DWG。匹配到资产但没有 `includedHandles`、`blockName`、verified `style_standard` 或其它精确来源时，必须返回 `needs_precise_native_source`，不得从全模型空间、当前屏幕、全部可见对象或训练面板硬拷贝。

系统资产复用前还必须经过 `core.assets.semantic_rules` 和 registry 文本编码预检。语义规则库负责记录触发词、路由、禁止行为、验收 hooks 和证据边界；它不能被普通 prompt 记忆替代。若 registry 的资产名、别名、用途、检索字段出现 `??`、`�` 或典型 mojibake，必须返回 `asset_registry_encoding_failed`，不得继续匹配、生成 ready plan 或写 CAD。弱匹配只能作为候选提示，不能自动复用；候选排序优先 `verified` / native / 精确来源可用资产。

跨 DWG 复用请求必须优先生成结构化 workflow，而不是把整句白话压成单个 asset query。复合请求按 `build_system_asset_reuse_workflow` / `scripts/reuse_system_asset.py --workflow` 拆成多个 `asset_reuse_*` 子任务，并分别做候选匹配、精确来源门禁、目标层 / base point 分配、CAD 写入和 handles 回读。没有显式资产动词但强匹配系统资产时，允许以 `implicit_asset_match` 触发检索；没有强匹配时返回 `not_asset_reuse_request`，继续走普通 `CAD_PLAN` 链路。多资产请求允许 `partial`：已准备好的资产可以复用，来源不清的资产必须保留 `needs_precise_native_source`，不得静默改成临场重画或全模型空间拷贝。`style_definition` ready plan 只证明 A-to-A 计划联通，不等于已经写入当前 DWG；单个复用计划只有 copy / import 返回 created handles 且当前 DWG `readbackStatus=ok` 时才算 `asset_reused`；读不回时必须保留 readback blocked 状态，不得晋升为完成。

## 8. 卡壳时先自查，不盲目重试

当用户说“画不准”“画不出来”，或当前阶段出现执行失败、预览不对、截图缺失、回读验证缺失时，Codex 必须先进入 `docs/runbooks/blocker-playbook.md` 的自查闭环。

最小要求：

- 先确认当前阶段和最近变更。
- 运行或说明为什么不能运行 `scripts/self_check.py`。
- 对视觉问题先确认 `scripts/render_preview.py --check` 的截图能力。
- 如果已经绘制到 CAD，优先留下截图或回读证据。
- 定位问题属于白话理解、`CAD_PLAN`、Schema、dry-run、执行脚本、驱动、CAD 环境还是验证工具。
- 如果已有上一轮 handles 或 bbox，先生成原位 `repair_plan` 并局部修复；不得默认旁边整套重画。
- 先做最小复现和最小修复，再扩大到复杂图纸。
- 修复后运行覆盖原问题的最小实际链路；CAD / 截图 / runner / 训练链路修复默认补一条真实或代表性端到端复验。
- 修复后更新 `docs/status/current.md`、`docs/status/changelog.md`，失败或踩坑还要更新 `docs/status/issues.md`。

如果当前没有自检或截图能力，先补自检或截图入口，再继续推进依赖它们的绘图修复。

## 9. CAD 层面验证要走自主验证闭环

当用户要求在真实 CAD 环境中按计划做 CAD 层面验证、换机验收或回读补验时，Codex 应优先读取 `docs/runbooks/cad-validation.md`，并运行：

```powershell
& $py scripts\run_cad_validation.py
```

不得遇到第一个失败就停止。仓库内可修问题应由 Codex 自己最小复现、最小修复并重新运行验证；只有依赖安装、AutoCAD 授权/窗口/活动 DWG、正式图层/保存/删除/覆盖、或真实项目语义缺失时，才停下来问用户。

验证结果必须以 `output/validation_runs/<timestamp>/report.json`、`report.md`、`readback_report.json` 和 `cad_capability_probe.json` 为证据。没有通过真实 CAD 落图、截图、实体回读和 CAD COM 能力探针时，不得声称几何准确或 CAD 调用底座可用。

## 10. 系统维护与安全重构门禁

执行大型系统维护、代码债排查、BUG 寻找或安全重构时，Codex 必须先冻结当前 dirty tree 与 baseline，再按小任务推进。每个任务要有明确允许文件、禁止范围、红/绿测试或审计断言、验证命令和停止条件。

默认边界：

- 纯文档治理、无 CAD 影响的系统维护可以不连接真实 CAD；一旦修复影响 CAD 落图、截图、训练、runner、验证或资产复用 / 沉淀链路，就必须按 §2.3 运行代表性实际链路。无论是否连接真实 CAD，默认都不保存当前业务 DWG、不覆盖原图、不删除未授权实体、不修改正式图层。
- 不把无 CAD 验证写成真实 CAD 几何准确。
- 不回滚未理解的用户或其他 Agent 改动。
- 不把“文件存在”当作任务完成；必须有红/绿测试、审计报告或验证命令证据。
- 多 Agent 并行时必须分配互不重叠的写入范围；Review Agent 默认只读，除非用户明确要求它转为实现任务。
- 临时执行计划完成后，必须把长期规则迁移到 `docs/governance/cad-agent-rules.md`、把审计事实迁移到 `docs/verification/`，再删除临时计划文件。

系统维护完成前至少运行：

```powershell
& $py -m unittest discover -s tests
& $py scripts\self_check.py
& $py scripts\render_preview.py --check
& $py scripts\run_repo_audit.py --max-python-lines 500
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\<name>-no-cad
```

日常阻断门禁优先使用 `scripts\run_repo_audit.py --fail-on-severity medium`；`--fail-on-findings` 仍可用于严格收口。若存在 low findings，应把它们登记为剩余治理风险，不能静默忽略。
