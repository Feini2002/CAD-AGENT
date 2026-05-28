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

**Agent 训练期：** 见 `AGENTS.md` 与 `docs/training/README.md`——未点名开发状态或表 C 时，不附进度表。

**训练期 / CAD 会话截图默认：**

1. **默认保留布局**：左 CAD / 右 IDE 分屏时，**不要**把 AutoCAD 全屏或强置顶；仅当窗口最小化时 `SW_RESTORE`。
2. **再**按 `execution_summary` 的 handles **`ZoomWindow` 重取景**（用户中途误拖/误缩也须自动拉回）。
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

- 用户要求完整状态汇报、交接、审计、进度盘点或对比。
- 用户说「真实 CAD 实力」「推进表 C」「表 C」「刷新表 C」：先展开完整表 C，A/B 可摘要。
- 完成或更新能力证明 / 代码轨 / CAD 补验包，并改变任务清单计数或 next。
- 修改 registry、showcase、coverage JSON，或需要解释 CAD 能力瓶颈。
- 出现回归、绘图不准、口径争议或 Markdown 进度漂移。

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

当前基准估算见 `CORE_STATUS.md` 与 `docs/status/current.md`。截至 2026-05-28 文档架构重构后的同步口径为：

```text
总进度：约 97% = 100% * 0.70 + 93% * 0.30（工程节奏）
Core 底座开发进度：100%（工程完备度；见 core_platform_completion_gate.md）
Agent 多场景实现进度：约 93%
CAD 证明覆盖率：约 62.78%（317 行；199 showcase）
真实 CAD 实力主指标：约 62.78%
展示等级 Ladder：最高已证 L4
```

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

## 8. 卡壳时先自查，不盲目重试

当用户说“画不准”“画不出来”，或当前阶段出现执行失败、预览不对、截图缺失、回读验证缺失时，Codex 必须先进入 `docs/runbooks/blocker-playbook.md` 的自查闭环。

最小要求：

- 先确认当前阶段和最近变更。
- 运行或说明为什么不能运行 `scripts/self_check.py`。
- 对视觉问题先确认 `scripts/render_preview.py --check` 的截图能力。
- 如果已经绘制到 CAD，优先留下截图或回读证据。
- 定位问题属于白话理解、`CAD_PLAN`、Schema、dry-run、执行脚本、驱动、CAD 环境还是验证工具。
- 先做最小复现和最小修复，再扩大到复杂图纸。
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

- 不连接真实 CAD，不保存 DWG，不覆盖原图，不删除实体，不修改正式图层。
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

如果 `scripts\run_repo_audit.py --fail-on-findings` 失败，应把 findings 分为“本轮必须修复”和“已登记剩余风险”。剩余风险必须写入 `docs/verification/` 或 `docs/status/issues.md`，不能静默忽略。
