# CAD Agent 问题与修复记录

本文现在只保留活跃风险和高频教训。压缩前完整问题库已归档到 `docs/history/snapshots/root-md-2026-05-26/CAD_AGENT_ISSUES.md`。

## 当前活跃风险

| 风险 | 当前影响 | 处理口径 |
| --- | --- | --- |
| OpenSpec 被误当第二主计划 | 初始化后若把 `openspec/changes/*` 当全局 next / backlog，会和唯一 PlanMD 冲突 | OpenSpec 只做复杂变更契约；`CORE_RESTRUCTURE_PLAN.md` 仍是唯一主线；`check_openspec_contracts()` 阻断根级 `openspec/tasks.md` 和 active change 自称主计划 |
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
| 普通回复表格噪声 / 旧上下文覆盖新规则 | 旧版 `AGENTS.md` 曾要求默认带精简进度表；若会话压缩或早期注入的旧规则仍在上下文中，可能覆盖当前仓库 opt-in 规则，导致普通回复误带表 | 普通最终回复默认不附进度表；只有用户点名开发状态查询、进度、完整状态、交接、审计、表 A/B/C、表 C 或真实 CAD 实力时才展开表格，并先报表 C 主指标；文档审计新增 stale output policy 检查 |
| 常识资料被误当成能力 | 把 GitHub 方法论、图库、PDF、DWG 或截图放进仓库，不会自动让 Agent 稳定使用，可能虚报“已学会” | 常识必须经过 `source_note → knowledge_summary → object_or_rule_candidate → executable_check → evidence_boundary`；未形成可执行检查前只能作为参考知识 |
| raw 标准图库进 git 的边界风险 | 用户需要 `standard_cad_library_raw/` 随 git 迁移；如果批次说明缺失，可能把临时文件、授权不清资料或下载失败缓存误提交，也可能把 raw 命中误报为系统能力 | 每批次默认跑 `scripts/run_asset_raw_intake.py --write` 生成 `source_note`、reference manifest 和 inferred annotation；提交前检查 `git status --short standard_cad_library_raw libraries/reference_library libraries/system_library`；raw 永远先按 `reference_only` 处理 |
| HTML 覆盖清单被误当能力证明 | 根目录 `capability-map.html` 是给人看的计划 / 覆盖清单，如果勾选口径不严，可能被误读为真实 CAD 已验证 | 页面只显示阶段；勾选必须来自 raw 导入、常识整理、训练通过或自产资产晋升事实；真实几何能力仍看 CAD 证据和表 C |
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
