# 架构治理小包：永生文档瘦身与事实源边界

状态：`DRAFT / ROOT-SIDECAR-PACKAGE`

创建日期：2026-06-07

本文只承接“永生文档审查：内容扩散与边界侵蚀”这一类长期治理问题。它不是新的 `PlanMD`，不承载全仓 next，不替代 `CORE_RESTRUCTURE_PLAN.md`，本轮也不要求同步其它根目录文档。后续若执行本包，应先由用户确认切入点，再按最小修改拆包推进。

根目录位置说明：本文按用户要求临时放在根目录，方便和其它根级永生文档并排审查。它不应成为根目录长期常驻计划；执行或收口后，应由后续治理包决定迁入 `docs/planning/`、`docs/governance/`、`docs/history/`，或删除根目录副本并保留引用。

## 0. 为什么单开这个小包

外部审查暴露的问题不是某一篇文档写得差，而是系统融合机制长期偏向“追加”，缺少“替代、降级、引用、归档”的动作。结果是每个文档单独看都有边界声明，但同一事实被复制到多个入口，短上下文越来越长，状态页和 brief 职责重叠，规则文档变成万能收纳箱，changelog 也逐渐承担事实源功能。

这个问题有长期隐患：

- 新会话加载成本变高，模型需要在多个“看起来都权威”的版本之间自行合并。
- 当前事实、历史事实、路线计划、规则、运行证据和口径声明互相缠绕。
- 架构归并完成后，同一句话如果已经被复制到 6-9 个文档，将很难稳定更新干净。
- 开发习惯会继续强化“多写几处更安全”的错觉，实际让系统越来越难接手。

本包的目标不是立刻删文档，而是先定下文档融合的架构规则：每个事实只有一个权威源，其它地方只做短引用；每次融合必须判断旧内容是否被替代、降级或归档。

### 0.1 当前基线快照

本轮基线不是主观印象，而是当前仓库可量化信号。以下数字为 2026-06-07 本包创建后的本地快照，后续执行前应重新跑一次。统计口径：UTF-8 读取；忽略 `output/`、`.git/`、`node_modules/` 等运行 / 依赖目录；以机器 baseline report 为准，本文数字只作风险快照。

| 信号 | 当前值 | 风险含义 |
| --- | ---: | --- |
| `docs/status/changelog.md` | 3303 行 | 历史追溯价值高，但已经不适合作为新会话入口 |
| `docs/governance/cad-agent-rules.md` | 487 行 | 规则、流程、架构说明和历史纠偏混合风险高 |
| `CORE_CONTEXT_BRIEF.md` | 119 行 | 已超过短入口目标，接近状态库 |
| `AGENTS.md` | 220 行 | 全局规则内含上下文恢复、PlanMD、架构归并等重复块 |
| `README.md` | 139 行 | 项目说明也承载当前主线与架构边界 |
| `docs/architecture/system-architecture-convergence.md` | 167 行 | 架构权威源合理，但内容被其它入口重复摘要 |
| 当前架构归并主线出现范围 | 至少 9 个活跃文档 | 同一主线事实已被多点复制 |
| 若继续只追加 10 轮 | 预计 Brief 约 300 行、Rules 约 1000 行以上 | 后续模型加载成本和人工维护成本会快速恶化 |

这张表只证明治理风险，不证明 CAD 能力、训练成熟度或表 C 变化。

### 0.2 与既有架构治理小任务的关系

仓库已有 `docs/planning/architecture-governance-hardening-mini-task.md`，它关注 Python 项目身份、schema 单源、repo inventory、入口 custody 和产物分类。

本文关注的是另一层：永生文档如何吸收事实、如何避免同一事实被复制到多个入口、如何让已完成内容降级为历史引用。两者可以共享 checker，但不应互相替代：

- `architecture-governance-hardening-mini-task.md` 管入口、schema、产物分类和 repo inventory。
- 本文管 Brief / Status / PlanMD / Rules / Changelog / AGENTS / README 的事实源边界。
- 若后续合并，应让前者保留工程资产治理，本文保留文档事实源治理。

## 1. 现象摘要

本轮审查指出的典型现象：

| 现象 | 风险 |
| --- | --- |
| 同一事实出现在多个文档 | 更新时需要多点同步，迟早漏改 |
| `CORE_CONTEXT_BRIEF.md` 不再短 | 新会话入口从“恢复上下文”变成“压缩版状态库” |
| `CORE_CONTEXT_BRIEF.md` 与 `docs/status/current.md` 职责重叠 | 模型需要手动 diff 两个当前状态版本 |
| `docs/governance/cad-agent-rules.md` 过度收纳 | 规则、流程、架构说明、历史纠偏混在一起 |
| `docs/status/changelog.md` 膨胀 | 追溯价值变高，但检索“最近发生什么”的成本也变高 |
| 文档都写了“本文不承载 X” | 说明作者知道边界，但缺少执行型融合机制 |
| 规划 / 状态 / brief / changelog 分层存在但无人强制遵守 | 逻辑分层在名义上存在，运行时仍会被绕过 |
| `AGENTS.md` 与 `cad-agent-rules.md` 重叠 | 上下文恢复、架构归并、PlanMD 规则在两处同时存在，未来会分叉 |

这不是单点文档质量问题，而是架构治理动作缺失。

### 1.1 永生 / 半永生文档清单

后续治理不能只盯 Brief、PlanMD、Status、Rules、Changelog 五类。当前应纳入盘点的“永生 / 半永生”文档至少包括：

| 文档 | 类型 | 为什么纳入 |
| --- | --- | --- |
| `AGENTS.md` | 永生规则入口 | 工具会自动加载，且已含上下文恢复、架构归并和 PlanMD 边界 |
| `CORE_CONTEXT_BRIEF.md` | 永生短入口 | 新会话最容易先读，膨胀会直接拖慢恢复 |
| `CORE_RESTRUCTURE_PLAN.md` | 永生主计划 | 唯一 PlanMD，容易被完成包摘要污染 |
| `CORE_STATUS.md` | 永生能力口径 | 表 A/B/C 与成熟度解释容易被误用为当前 next |
| `README.md` | 半永生项目入口 | 新人和模型都会读，容易复制当前状态 |
| `docs/status/current.md` | 当前状态权威候选 | 与 Brief 职责高度重叠 |
| `docs/status/changelog.md` | 历史流水 | 行数最大，容易反向成为事实源 |
| `docs/governance/cad-agent-rules.md` | 硬规则候选 | 需要和 `AGENTS.md` 分工，避免规则双写 |
| `docs/architecture/system-architecture-convergence.md` | 架构权威源 | 当前主线的解释源，应减少被其它文档复制 |
| `docs/planning/任务清单.md` | 执行台账 | 当前 next 和用户口令入口，不能变成第二套 PlanMD |
| `docs/planning/architecture-governance-hardening-mini-task.md` | active sidecar | 与本文有关联，需要定义前后关系 |
| `docs/status/issues.md` | 长期风险入口 | 记录失败教训和隐患，不能承载普通完成记录 |
| `docs/handoffs/current.md` | 当前交接入口 | 包交接、证据路径和剩余风险，不能回流成 current status |
| `docs/handoffs/package-index.md` | 包索引 | 全量包索引，不能承载当前 next |
| `docs/README.md` | 半永生索引 | 只应指向权威源，不应复制当前状态 |
| `docs/planning/README.md` | 规划索引 | 只应解释 planning 目录职责，不应承载第二套计划 |
| `docs/planning/phases/phase-z-doc-governance.md` | 执行剧本 | 只作阶段剧本，不应独立更新治理优先级 |
| `docs/training/README.md` | 训练控制入口 | 训练流程入口，不能替代训练事实源 |
| `docs/training/training-sources.json` | 训练事实源 | 长期训练事实源，不能被工作台派生快照反向覆盖 |
| `capability-map-data.js` | 派生工作台快照 | 只能由同步脚本生成，不能作为事实源 |
| `ARCH_DOC_GOVERNANCE_BOUNDARY_PACKAGE.md` | 临时根侧包 | 本文本身也必须有退出路径，不能变成新的永生文档 |

## 2. 根因诊断

当前融合动作主要是：

```text
把新事实追加到每个可能被读取的文档。
```

缺少的动作是：

```text
这条新事实替代了哪一段旧事实？
这条事实在哪个文档是权威源？
其它文档是否只需要一句摘要和链接？
这个包已完成后，是否应从当前状态降级为历史引用？
这个规则是硬约束，还是流程说明、架构说明、经验教训？
```

因此，治理重点不是“少写”，而是让每次写入都带有归属判断。

## 3. 核心原则

### 3.1 单事实单权威源

每个长期事实只能有一个权威源文档。其它文档允许出现同一事实的短摘要，但必须以引用身份存在，不复制完整内容。

推荐格式：

```markdown
- **架构归并主线**：当前主线，权威源见 `CORE_RESTRUCTURE_PLAN.md` §0.2。
```

不推荐格式：

```markdown
- **架构归并主线**：在每个入口文档重复完整描述背景、暂停项、Worker、Decision Gate、完成标准和风险边界。
```

### 3.2 Brief 只负责入口，不负责存档

`CORE_CONTEXT_BRIEF.md` 的职责应收缩为：

- 当前一句话。
- 当前必须知道的 5-10 条活跃事实。
- 当前 next 的最短入口。
- 按需展开表。
- 明确不能声称什么。

不应长期承载：

- 42 条最近有效事实。
- 完整包历史。
- 多套状态表。
- changelog 摘要副本。
- 规则全文。

### 3.3 Status 负责当前状态，不负责路线计划

`docs/status/current.md` 或同类状态页应回答：

- 当前系统处于什么状态。
- 当前能力、证据、风险和阻断是什么。
- 哪些内容已经完成但仍有边界。

它不应承担：

- 全局路线排序。
- 长期 backlog。
- 历史流水。
- 规则全集。
- brief 的入口职责。

### 3.4 PlanMD 负责路线，不负责状态库

`CORE_RESTRUCTURE_PLAN.md` 仍是唯一 `PlanMD`。它应定义阶段、优先级、Decision Gate 和退出标准，但不应成为每个已完成包的状态仓库。

已完成包的长期证据应进入：

- changelog / history。
- handoff archive。
- 机器报告路径。
- 对应 architecture reference。

PlanMD 只保留必要引用。

### 3.5 Changelog 只写流水，不替代当前事实源

`docs/status/changelog.md` 的价值是追溯，不是让新会话从头读历史。它可以长，但应具备检索结构，并且不能被其它文档复制成“第二套最近有效事实”。

推荐后续治理方向：

- 按月份、包、主题或阶段分节。
- 每条 changelog 只写变化、证据、影响。
- 当前有效事实回到 status 或 architecture 权威源。

### 3.6 Rules 只保留硬约束

`docs/governance/cad-agent-rules.md` 或同类规则文档应只保留会影响行为的硬规则：

- 必须做什么。
- 禁止做什么。
- 触发条件是什么。
- 失败时如何阻断。

不应长期收纳：

- 大段架构说明。
- 历史来龙去脉。
- 已完成包摘要。
- 与其它文档重复的上下文恢复流程。
- 只具有解释价值、没有执行约束的文本。

解释性内容应迁往 architecture / runbook / history，规则文档只保留引用。

### 3.7 `AGENTS.md` 与 governance rules 的所有权

`AGENTS.md` 和 `docs/governance/cad-agent-rules.md` 都是强约束入口，但它们不应长期双写同一规则。

| 规则类型 | 权威源 | 允许在另一处出现什么 |
| --- | --- | --- |
| 工具自动加载后必须立即遵守的顶层硬边界 | `AGENTS.md` | governance rules 可引用，不复制全文 |
| CAD / 训练 / 资产 / 复用 / 截图等细颗粒操作规则 | `docs/governance/cad-agent-rules.md` | `AGENTS.md` 只写触发摘要和链接 |
| 上下文恢复入口 | 二选一作为权威源，当前建议 `AGENTS.md` 只写入口，Brief 负责内容 | 其它文档只保留一句引用 |
| 唯一 PlanMD / OpenSpec 边界 | `AGENTS.md` 写最高层禁令；`CORE_RESTRUCTURE_PLAN.md` 和 OpenSpec 文档写执行细节 | governance rules 不再复制完整解释 |
| 阶段性主线说明 | `CORE_RESTRUCTURE_PLAN.md` / architecture 文档 | `AGENTS.md` 和 governance rules 只写当前触发边界 |

重复块治理标准：一处正文 + 一处短引用；超过两处完整正文时，checker 应至少 warning。

## 4. 文档职责矩阵

| 文档 | 权威职责 | 不应承载 |
| --- | --- | --- |
| `AGENTS.md` | 最高层行为规则、用户偏好、仓库硬边界 | 长历史、包流水、阶段性细节 |
| `CORE_CONTEXT_BRIEF.md` | 新会话短入口、当前少量活跃事实、展开索引 | 状态库、changelog 副本、规则全集 |
| `CORE_RESTRUCTURE_PLAN.md` | 唯一 PlanMD、路线、优先级、Decision Gate | 包级历史流水、完整状态表 |
| `CORE_STATUS.md` | 能力口径、证据口径、表 A/B/C 定义和当前机器值 | 未来路线、下一步 backlog |
| `README.md` | 项目定位、仓库入口、主要目录说明 | 当前状态副本、临时治理包摘要 |
| `docs/status/current.md` | 当前状态、风险、有效证据、阻断 | PlanMD、brief 副本、历史流水 |
| `docs/status/changelog.md` | 历史变更流水 | 当前状态权威源、最近事实全集 |
| `docs/governance/cad-agent-rules.md` | 可执行硬规则和禁令 | 架构白皮书、流程长文、历史总结 |
| `docs/architecture/**` | 架构解释、生命周期、模块边界 | 当前 next、临时任务队列 |
| `docs/planning/任务清单.md` | 执行台账、用户口令、即时 next 镜像 | 架构解释、长期路线、状态库 |
| `docs/planning/phases/**` | 阶段执行剧本 | 第二套主计划、独立 backlog |
| `docs/handoffs/current.md` | 最近包交接、证据路径、剩余风险 | 当前状态权威列表、PlanMD、训练事实源 |
| `docs/handoffs/package-index.md` | 包索引和归档定位 | 当前 next、包详细复述 |
| `docs/status/issues.md` | 风险、失败教训、长期隐患 | 普通完成记录、状态快照 |
| `docs/training/training-sources.json` | 训练事实源 | 派生快照、普通状态摘要、诊断报告 |
| `docs/training/README.md` | 训练流程入口和边界 | 训练事实源正文、工作台快照事实 |
| `ARCH_DOC_GOVERNANCE_BOUNDARY_PACKAGE.md` | 临时审查包、后续治理草案 | 永久规则源、执行台账、长期根目录常驻文件 |

后续改文档时，先判断新增内容属于哪一列，再决定写入位置。

## 5. 文档融合四动作

每次把开发结果“释进系统文档”时，不允许只问“还要加到哪里”，必须同时问四个动作：

| 动作 | 含义 | 例子 |
| --- | --- | --- |
| `add` | 新事实没有已有承载处，新增到唯一权威源 | 新增一个 active sidecar 的入口 |
| `replace` | 新事实替代旧事实，旧段落应删短或改引用 | 架构归并状态更新后，旧阶段描述不再重复保留 |
| `demote` | 当前事实变成历史事实，迁入 changelog / archive | 已完成小包不再占 brief 的有效事实名额 |
| `reference` | 非权威文档只留一句摘要和链接 | brief 指向 status，不复制 status 列表 |

如果一次同步只有 `add`，没有任何 `replace / demote / reference` 判断，就应视为文档膨胀风险。

### 5.1 四动作同步记录模板

后续任何系统文档同步都必须留下四动作记录。没有记录时，即使文件内容看似正确，也视为未完成融合审查。

| 字段 | 要求 |
| --- | --- |
| `factId` | 包名、change id、规则名或可检索事实名 |
| `authoritySource` | 唯一权威源文档与章节 |
| `add` | 新增到哪个权威源；若无新增，写 `none` |
| `replace` | 被替代的旧段落、旧章节或旧事实；若无替代，写原因 |
| `demote` | 从当前入口降级到 changelog / archive / history 的内容；若无降级，写原因 |
| `reference` | 哪些非权威文档只保留一句引用 |
| `touchedFiles` | 本次实际修改的文件 |
| `skippedFiles` | 明确检查但不修改的文件及原因 |
| `evidence` | checker 输出、行数快照或人工审查结论 |

最低通过条件：一次同步不能只有 `add`；若没有 `replace / demote / reference` 中任一动作，必须写明为什么本次事实确实没有旧内容可替代、降级或引用化。

可复制的 before / after 模式：

| 场景 | 膨胀写法 | 治理写法 |
| --- | --- | --- |
| 主线更新 | `AGENTS.md`、Brief、PlanMD、Status、README、Rules 全部复制架构归并完整说明 | 选 `CORE_RESTRUCTURE_PLAN.md` 或架构文档为权威源；其它文档只留一句摘要和链接 |
| 包完成 | 在 Brief 的“最近有效事实”追加完整包摘要，不删除旧包 | changelog 记流水；Brief 只保留仍影响下一轮工作的包 |
| 规则新增 | 在 `AGENTS.md` 和 `cad-agent-rules.md` 都写一遍完整规则 | `AGENTS.md` 写触发级硬边界；详细规则只在 governance rules 或 runbook |
| 状态变化 | status、brief、PlanMD 都各自写当前状态表 | status 为权威源；brief 链接 status；PlanMD 只写路线影响 |
| 临时侧包 | 根目录新增小包后长期不处理 | 文档头部写退出路径；checker 检查 root sidecar 是否过期 |

## 6. 后续执行目标（本文只提出，不执行）

### 6.1 授权执行后的固定工作流

当用户明确要求执行本包时，按以下顺序推进，不得一次性扩大为全仓文档重写：

1. 运行 UTF-8 读取与基线快照，确认目标文档没有中文乱码。
2. P0 先补或强化只读 checker，只输出 warning / require_review，不自动改文档。
3. 用 checker 结果选择一个最小治理对象，例如 Brief、Rules 或 Changelog。
4. 对该对象生成四动作同步记录，明确 `add / replace / demote / reference`。
5. 只修改本包授权范围内的文件。
6. 复跑 checker，并记录 blocker、warning 和人工解释。
7. 更新本包退出状态：继续草案、迁入正式位置、归档、删除根副本并保留引用，或交给后续正式治理包。

如果某一步缺少权威源、无法判断旧事实是否被替代，或 checker 无法区分 warning 与 blocker，应暂停为 `needs_review`，不得继续批量瘦身。

### 6.2 P0-P4 完成定义

| 阶段 | 输入 | 动作 | 完成定义 | 不得扩大范围 |
| --- | --- | --- | --- | --- |
| P0 反膨胀 checker | 永生文档清单、本包 §7 | 强化 `scripts/run_doc_governance_audit.py` 或等价 checker | 能输出 baseline 快照；能检测 Brief 行数、重复 fact、completed 包残留、根侧包退出路径、四动作缺失；第一阶段不自动改文件 | 不压缩文档、不迁移历史、不刷新工作台 |
| P1 Brief 瘦身 | `CORE_CONTEXT_BRIEF.md` + checker baseline | 只压缩 active facts 与重复状态摘要 | Brief 行数与 active facts 达到阈值，或 checker 明确返回 `require_review`；每条 active fact 有权威源链接 | 不改 PlanMD 路线、不改状态事实源 |
| P2 Brief / Current Status 拆分 | Brief 与 `docs/status/current.md` | 选一个当前有效包权威列表，另一个改短引用 | 两者不再各自维护一套当前有效包列表 | 不改 changelog 历史流水 |
| P3 Rules 瘦身 | `AGENTS.md` + `docs/governance/cad-agent-rules.md` | 迁移或引用非硬约束内容 | 规则文档中的非硬约束内容已有迁移目标或引用目标；重复上下文恢复块不超过一处权威源 | 不重写用户偏好，不改变 CAD 安全边界 |
| P4 Changelog 索引化 | `docs/status/changelog.md` | 设计索引 / 分卷 / supersedes 方案 | Changelog 不再被其它入口复制为当前事实源；若暂不分卷，至少有索引化方案和 checker warning | 不删除可追溯历史证据 |

执行激活规则：

- `activationRequires`：用户明确要求执行本包，或 `CORE_RESTRUCTURE_PLAN.md` / `docs/planning/architecture-governance-hardening-mini-task.md` 接管为活跃任务。
- `ownerPlan`：未接管前，本文只提供治理需求；接管后由唯一 PlanMD 或既有 architecture-governance mini-task 承载执行顺序。
- `mustSyncPlanMDIfPriorityChanges`：如果 P0-P4 的优先级、范围或退出标准影响全仓开发顺序，必须回写唯一 PlanMD；否则不得把本文当作第二套 backlog。

### P0：建立反膨胀禁令

先新增或强化一条机器可检查的规则：

```text
同一包名、任务名或事实名出现在超过 3 个活跃控制文档中时，至少 warning。
`CORE_CONTEXT_BRIEF.md` 超过 80 行时 warning，超过 120 行时 fail 或 require_review。
被标记为 completed / archived / history 的包仍出现在 brief 的“当前有效事实”中时 warning。
```

这条规则不要求立刻删除旧内容，只要求后续 checker 能持续提醒。

### P1：压缩 Brief 的事实层

目标不是把 `CORE_CONTEXT_BRIEF.md` 砍空，而是让它重新成为入口：

- “最近有效事实”控制在 10 条以内。
- 每条事实只保留包名、一句摘要、权威源链接。
- 已经在 status / changelog / architecture 有完整描述的内容不再复制。
- 当前 next 只保留一条主线和必要口令，不展开历史。

推荐验收标准：

```text
brief_line_count <= 80
active_fact_count <= 10
each_active_fact_has_authoritative_source = true
no_completed_package_as_active_fact = true
```

### P2：合并 Brief 与 Current Status 的有效包

`CORE_CONTEXT_BRIEF.md` 与 `docs/status/current.md` 当前承担了相似职责。后续应选择一个作为“当前有效包”的权威源。

推荐方向：

- `docs/status/current.md` 作为当前状态权威源。
- `CORE_CONTEXT_BRIEF.md` 只保留“见 current status 的哪一节”。
- 需要新会话直接知道的高风险禁令可在 brief 保留一句，但不复制完整解释。

### P3：规则文档瘦身

不删规则，只迁移非硬约束内容：

- 架构说明迁入 `docs/architecture/**`。
- 流程长文迁入 `docs/runbooks/**`。
- 历史教训迁入 `docs/status/issues.md` 或 changelog。
- 重复的上下文恢复流程只保留一个权威源，其它地方引用。

推荐验收标准：

```text
governance_rule_doc_hard_rule_ratio >= 70%
long_explanatory_sections_have_architecture_or_runbook_targets = true
duplicate_context_recovery_blocks <= 1
```

### P4：Changelog 分卷或索引化

`docs/status/changelog.md` 可以长，但不能继续承担“最近有效事实存储”。后续可选方案：

- 按月份分卷。
- 保留一个短索引 + 历史文件。
- 每条 changelog 增加 `status_after` / `evidence` / `supersedes` 字段。

本包不要求本轮执行分卷，只把它列为后续治理方向。

## 7. 机器审计草案

后续可在 `scripts/run_doc_governance_audit.py` 或新 checker 中增加这些检查：

| 检查 | 触发 | 级别 |
| --- | --- | --- |
| `duplicate_fact_name` | 同一 all-caps 包名 / change id 出现在超过 3 个活跃文档 | warning |
| `immortal_doc_baseline_snapshot` | 输出永生 / 半永生文档当前行数、活跃事实数、重复 fact 名 | info |
| `brief_too_long` | `CORE_CONTEXT_BRIEF.md` 超过 80 行 | warning |
| `brief_oversized` | `CORE_CONTEXT_BRIEF.md` 超过 120 行 | require_review |
| `active_fact_without_source` | brief / current status 的事实没有权威源链接 | warning |
| `completed_package_in_brief` | completed / archived 包仍在 brief active facts | warning |
| `agents_rules_overlap` | `AGENTS.md` 与 `cad-agent-rules.md` 出现同一规则块或上下文恢复块 | warning |
| `rules_doc_contains_history_bloat` | 规则文档出现大量 changelog-like 包摘要 | warning |
| `status_contains_plan_backlog` | status 页出现长期 next / backlog 列表 | warning |
| `changelog_as_current_source` | 其它文档复制 changelog 的完整最近事实 | warning |
| `merge_action_missing` | 系统文档同步记录只有 `add`，没有 `replace / demote / reference` 判断 | warning |
| `root_sidecar_without_exit` | 根目录临时治理小包没有迁移 / 归档 / 删除的退出路径 | warning |
| `root_sidecar_past_trigger` | checker 已落地、Brief 压缩包完成或根目录治理包数量继续增长后，根侧包仍未迁移 / 归档 / 删除 | require_review |

这些检查的第一阶段只 warning，不自动改文档。

### 7.1 多 Agent 执行职责

正式执行本包时，建议用多个独立审查角色并行工作，但最终只能由主 Agent 合并，不允许多个 Agent 各自散写永生文档。

| 角色 | 负责问题 | 允许产物 | 不允许 |
| --- | --- | --- | --- |
| `doc_scope_reviewer` | 判断永生 / 半永生文档范围是否漏列，尤其是 `AGENTS.md`、`README.md`、任务清单和 active sidecar | 只读审查清单、漏项列表 | 直接改文档 |
| `checker_worker` | 把 §7 的 warning 规则接入 `run_doc_governance_audit.py` 或等价 checker | 小范围脚本补丁、测试 | 修改长期系统文档 |
| `brief_status_refactor_reviewer` | 设计 Brief 与 current status 的权威源拆分方案 | before / after 映射表 | 直接压缩 Brief |
| `rules_overlap_reviewer` | 找出 `AGENTS.md` 与 `cad-agent-rules.md` 的重复硬规则和上下文恢复块 | 重复块清单、迁移建议 | 在两边同时重写规则 |
| `main_integrator` | 合并所有建议，执行唯一写入，跑 checker，记录剩余 warning | 最终 patch、测试结果、收口说明 | 把子 Agent 输出原样堆进文档 |

推荐流程：

```text
并行只读审查 -> 主 Agent 汇总差异 -> 小范围实现 checker -> 跑最小测试 -> 再决定是否压缩 Brief / Rules / Status。
```

若多个 Agent 给出相互冲突的建议，以“单事实单权威源”和“先 warning 后迁移”为优先原则。

## 8. 当前草案边界

本节约束“当前这个根目录草案”的行为，避免和 §6 的后续执行目标混淆：§6 只是目标列表，§7 只是 checker 草案，本文当前不执行任何同步、迁移或瘦身动作。

本包当前不做：

- 不同步 `CORE_CONTEXT_BRIEF.md`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_STATUS.md` 或其它根文档。
- 不删除、移动或归档任何历史文档。
- 不刷新训练工作台。
- 不改训练事实源。
- 不改表 C / Core Proof Coverage。
- 不运行 CAD。
- 不把本文升级成第二套 PlanMD。
- 不把“根目录临时侧包”当作未来治理文档默认位置。

后续真正执行时，应按“小刀口”拆包：

1. 先补 checker，只读 warning。
2. 再压缩 brief。
3. 再处理 brief / current status 重叠。
4. 再瘦身 rules。
5. 最后处理 changelog 索引或分卷。

每个小刀口完成后都要留下机器证据，至少包括：

- 改了哪些权威源。
- 哪些文档只保留引用。
- 哪些旧段落被替代或降级。
- `scripts/run_doc_governance_audit.py` 或相关 checker 的输出。
- 仍保留的 warning 及原因。

## 9. 人工审查清单

每次准备向系统文档写入新事实前，先回答：

- 这条事实的权威源是哪一篇？
- 哪些文档只需要引用，不需要复制？
- 它替代了哪段旧内容？
- 有没有已完成包还停留在“当前有效事实”里？
- 这是硬规则、状态、计划、历史、架构解释，还是运行证据？
- 这次同步是否包含 `replace / demote / reference`，而不仅是 `add`？
- Codex 是否明确说明自己做了哪些融合动作；如果没有，是否应判为 `merge_action_missing`？

如果这些问题答不出来，先不要把内容散写进多个永生文档。

## 10. 收口标准

本包完成时，不以“删掉多少行”为唯一指标，而以可检查结果为准：

- `CORE_CONTEXT_BRIEF.md` 控制在 80 行以内，或 checker 明确返回 `require_review`。
- Brief 的 active facts 不超过 10 条，每条都有唯一权威源链接。
- 同一包名 / change id 在活跃控制文档中超过 3 处时，checker 至少 warning。
- `AGENTS.md` 与 `docs/governance/cad-agent-rules.md` 的重复规则块被压缩为“一处权威源 + 一处引用”。
- `docs/status/current.md` 与 Brief 不再各自维护一套当前有效包列表。
- 已完成包从 Brief 降级到 changelog / archive / architecture reference。
- 每次系统文档同步记录都说明 `add / replace / demote / reference` 至少执行了哪些动作。
- 根目录本文有明确退出结果：迁入、归档、删除根副本并保留引用，或被后续正式治理包接管。
- checker 第一阶段能输出 baseline 快照；第二阶段能返回 `0 blocker`，且剩余 warning 都有解释。

一句话收束：这轮治理不是为了让文档显得更少，而是为了让每条事实知道自己住在哪里，并且在过期时能被降级，而不是永远活在每个入口里。
