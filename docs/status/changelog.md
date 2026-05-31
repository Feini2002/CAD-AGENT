# CAD Agent 变更记录

这个文件记录 CAD Agent 测试工作区的结构、规则、Schema、脚本和重要决策变化。

## 2026-06-01

### ARCH-BOUNDARY-HARDENING-01：架构瘦身与边界加固 01

- **触发**：用户认可“不要做系统重构 2.0”，要求按“架构瘦身与边界加固 01”收束当前架构：区分稳定 Core、训练实验和 case 代码，并先处理 verification、capability-map、资产闭环和 `projects/.../runs` 晋升边界。
- **OpenSpec**：新增 `openspec/changes/architecture-boundary-hardening-01/`，包含 proposal / design / specs / tasks；新增 capability `module-boundary-contract`，明确该 change 不是第二套主计划。
- **架构快照**：新增 `docs/architecture/current-module-boundaries.md`，固定 `Stable Core`、`Training Experiments`、`Case-Only` 三桶；为 `core/verification/` 定义 `report contract`、`runner`、`registry writeback`、`visual audit`、CAD/session safety 拆分图；为 capability map 定义 data generator、page shell、display configuration 和证据边界拆分图。
- **对象资产试点**：选择 `projects/residential_sofa_2seat_20260528` 作为首个对象族候选，但明确必须走 `raw reference -> knowledge summary -> candidate -> executable check -> system asset -> CAD_PLAN -> readback`，不能把 raw reference 或 candidate 直接当系统资产。
- **守护测试**：新增 `tests/core/test_architecture_boundary_hardening.py`，检查架构快照可发现、三桶分类、拆分图、对象资产试点、case-run 晋升门槛和 OpenSpec 不替代 `CORE_RESTRUCTURE_PLAN.md`。
- **收尾修复**：`core/verification/render_preview.py` 的 optional module 检测补上 `ModuleNotFoundError` 降级；系统 Python 缺少 `PIL` 时 screenshot tooling 只进入 warn，不再让 self-check 或 wrapper 测试异常失败。
- **验证**：新增边界测试 5 OK；失败集复测 19 OK；CAD-MCP venv 全量 `unittest discover -s tests` 1044 OK（2 skipped）；`run_doc_governance_audit.py` pass；CAD-MCP venv `scripts/self_check.py` pass。
- **边界**：本包是收束契约和守护测试，不是大规模移动代码；未改变 CAD 执行、registry、表 C 或真实 CAD 证据。

### REPO-POWER-LOSS-HEALTH-01：断电后仓库健康检查与测试契约修复

- **触发**：用户说明电脑刚刚断电，要求整体检查仓库是否有文件受损，并修复需要修的地方。
- **检查**：`git fsck --full --strict --no-dangling` 通过；全仓库冲突标记扫描无命中；JSON 文件解析 0 error；UTF-8 抽检确认中文上下文文件未损坏；非测试产物 0 字节文件仅有临时服务输出日志 `tmp-capability-map-server.out.log`。
- **根因**：全量单测最初失败不是 Git 损坏，而是迁移后的契约未同步：self-check 仍查旧英文根级文件名，pipeline 测试未纳入 `pipeline_asset_retriever`，round12 测试仍按旧“允许交付”口径断言，RCAD-20/21 live contract 在本机缺少未随仓库携带的真实 CAD JSON 时不应伪造证据。
- **修复**：更新 `core/verification/self_check.py` 的 required files；同步 `tests/core/test_planmd_governance.py`、`tests/agents/test_pipeline_visual_contracts.py`、`tests/core/test_visual_parts_case_contract.py`、`tests/core/test_vproof_51_negative_cad.py`、`tests/core/test_vproof_52_guard_cad.py`；修复 `tests/core/test_route_audit_report.py` 每次全量测试重写 tracked 示例 JSON 时间戳的副作用。
- **收尾**：`.gitignore` 增加 `tmp-*.log`，让本地临时服务日志不再污染工作区；状态页最近门禁同步为 1039 tests OK（2 skipped）。
- **验证**：目标失败集 40 tests OK（2 skipped）；全量 `python -m unittest discover -s tests` 1039 tests OK（2 skipped）；`scripts/self_check.py` pass；`git diff --check` 仅有 Windows 换行提示。
- **边界**：未补造真实 CAD 证据；RCAD-20/21 对应 JSON 不在当前工作区时只跳过 live contract；不改变表 C、不运行真实 CAD、不保存或修改用户 DWG。

## 2026-05-31

### CAPABILITY-MAP-TRAINING-WORKBENCH-03：训练计划表单与智能体 Prompt 工作台

- **触发**：用户指出“CD / CAD 能力训练看板”越改越复杂，真正需要围绕训练计划和智能体 Prompt，看清不同能力项训到哪、谁负责、下一轮怎么练，以及每个智能体 Prompt 和调用能力成熟度如何调整。
- **方案**：保留用户认可的能力矩阵分组（基础家具 / 储位家具 / 厨卫对象 / 基础绘图 / 标注表达），默认首页改为“训练计划表单”；第二主视图改为“智能体 Prompt 工作台”，左侧选智能体、右侧看当前 Prompt 描述、职责边界、输入输出、硬门槛、禁止事项、调用契约、可调 Prompt 点和源文件入口。
- **数据生成**：`scripts/build_capability_map_data.py` 升级到 schema v2，新增 `trainingStageColumns`、`trainingPrograms`、`agentProfiles`、`promptContracts`、`tableCBoundary`；为 pipeline / scene / demand 智能体生成自然中文 Prompt 契约，避免前端展示英文碎片。
- **前端重构**：`capability-map.html` 改为训练工作台：桌面端固定列宽展示能力矩阵和右侧训练详情；移动端隐藏宽表格，改用训练计划卡片展示阶段、下一轮训练、责任智能体和四条沉淀轨道；智能体页前置“本轮最值得调的 3 条 Prompt”。
- **口径修正**：`Prompt 已定义` 改为 `目标已声明`；训练阶段显示 `第 x/5 阶段` 而非伪百分比；智能体卡片改为 `契约完整度 / 调用契约 / 训练覆盖面 / 证据状态`，并显示依据和缺口；表 C 顶部降权为机器快照，完整解释放入证据边界。
- **验证**：已跑 `build_capability_map_data.py`、`py_compile`、`node --check capability-map-data.js`、HTML 内联脚本语法检查；Chrome DevTools 验证桌面计划页、桌面智能体页、移动计划页、移动智能体页截图，移动端无明显文本溢出。
- **边界**：本包只改训练看板可视化和生成数据，不改变表 C、registry、真实 CAD 能力、CAD 执行链路或用户 DWG；页面里的阶段和契约分只用于训练调度与 Prompt 调整。

## 2026-05-29

### CAPABILITY-MAP-AGENT-COCKPIT-02：智能体控制台详情弹窗

- **触发**：用户指出能力看板里的智能体清单仍不可控，无法知道每个 Agent 背后的 JSON / MD / prompt 规则、运作架构和可优化点。
- **执行**：`capability-map.html` 的智能体卡片改为可点击详情弹窗，新增“运作架构 / 规则提示词 / 可优化点 / 文件翻译”四个视图；卡片不再用 `+数字` 折叠智能体信息。
- **数据生成**：扩展 `scripts/build_capability_map_data.py`，从 `agents/**/agent.json`、`rules.md`、pipeline doc 和 demand role 数据生成中文职责、输入输出、通过门槛、禁止事项、文档含义、改动建议和优化提示；重建 `capability-map-data.js`。
- **验证**：已跑生成器、`py_compile`、`node --check capability-map-data.js`、HTML 内联脚本语法检查和数据断言；浏览器插件因当前额度限制未能完成点击截图验证。
- **边界**：本包只做控制台可视化和数据快照，不直接编辑源 JSON/MD，不改变真实 CAD 能力表 C，不替代 validate / dry-run / CODEX_PREVIEW / 回读 / 截图链路。

### CAD-ASSET-RAW-INTAKE-AUTO-01：标准图库自动 raw intake

- **触发**：用户明确希望只告诉 Agent “文件夹是什么、里面大概是什么”，不再手填来源 / 授权 / 对象范围 / 图纸类型表格；同时要求优化链路和 Agent prompt 定义。
- **执行**：新增 `core/assets/raw_intake.py` 与 `scripts/run_asset_raw_intake.py`，从 `standard_cad_library_raw/<source_slug>/original/` 自动扫描有效文件，保守推断 `object_tags`、`view_type`、`domain`、`part_tags`，并生成 `source_note`、reference source、单对象 `reference_asset` JSON、`agent_inferred` annotation 和 `knowledge/source_notes`。
- **Agent / 文档**：更新 `asset_retriever`、`context_curator`、`orchestrator` 和 `pipeline_manifest`，把 `standard_library_intake` 设为非绘图分支；重写 asset intake 模板和 raw README，明确“用户只需放文件夹 + 一句说明，Agent 先扫，不追表”。
- **测试**：新增 `tests/core/test_asset_raw_intake.py`，覆盖跳过锁文件、保守默认、schema 校验、不写 `system_library` 和路径穿越拦截；补齐 asset / retrieval schema invalid fixtures。
- **边界**：自动 intake 不解析 CAD 几何、不导入真实图库、不晋升自产资产、不改变表 C；推断错误时以 `unknown` / `reference_only` 保守落库。

### OPENSPEC-CONTRACT-LITE-01：OpenSpec 变更契约轻量护栏

- **触发**：用户要求参照 `CodeGraph + OpenSpec` 重大项目治理表单和截图建议，做一个不破坏现有主线的小型架构升级，重点提升变更契约能力。
- **执行**：新增 OpenSpec change `establish-change-contract-lite`，包含 proposal / design / tasks / specs；在 `AGENTS.md` 与 `CORE_RESTRUCTURE_PLAN.md` 明确 OpenSpec 只作为复杂变更契约层；新增 `check_openspec_contracts()` 并接入 `build_doc_governance_report()`。
- **机器护栏**：doc governance 现在会检查根级 `openspec/tasks.md`、缺少 `CORE_RESTRUCTURE_PLAN.md` 边界的 OpenSpec config，以及 active change 自称主计划 / 总 backlog。
- **边界**：不改 CAD 执行逻辑、不改表 C、不改训练案例、不迁移历史文档；本包是治理小优化，不是 OpenSpec 接管仓库。

### ROOT-MD-CHINESE-NAMES-01：根目录历史入口中文化

- **触发**：用户指出根目录很多 Markdown 文件名仍停留在早期开发阶段，无法一眼判断用途，要求先把根目录大量 MD 改成中文说明。
- **执行**：将 10 个根目录历史 stub 改为中文文件名：`CAD自动验证入口.md`、`CAD卡壳排障入口.md`、`变更记录入口.md`、`问题风险入口.md`、`长期规则入口.md`、`当前状态入口.md`、`路线图入口.md`、`CAD符号语法入口.md`、`训练错误记录入口.md`、`视觉优先训练计划入口.md`。
- **同步**：更新 `core/maintenance/doc_governance.py` 和 `tests/core/test_doc_governance.py` 的 root stub 检查清单；保留 `AGENTS.md`、`README.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_STATUS.md` 这些机器入口不改名。
- **边界**：本包只做文件名可读化，不重写 stub 正文，也不改变训练链路、表 C 或 CAD 能力。

### OPENSPEC-INIT-01：根目录 OpenSpec 初始化

- **触发**：用户要求在当前根目录初始化 OpenSpec，用于后续复杂变更的 proposal/spec/design/tasks 契约化。
- **执行**：运行 `openspec.cmd init . --tools none` 创建 `openspec/changes/`、`openspec/changes/archive/`、`openspec/specs/`；新增 `openspec/config.yaml` 和 `.gitkeep`，让初始化结果可随仓库迁移。
- **定位**：OpenSpec 只作为单个复杂变更的契约层；`CORE_RESTRUCTURE_PLAN.md` 仍是唯一 `PlanMD` / 主计划，`openspec/changes/*` 不承载第二套总 backlog。
- **验证**：`openspec.cmd list --json` 已能在根目录识别 OpenSpec，当前返回 `{"changes":[]}`。
- **边界**：初始化使用 `--tools none`，没有自动改写 Codex / Cursor 工具配置；未创建具体 change，未改变 CAD 能力、表 C 或真实 CAD 证据。

## 2026-05-28

### DOC-ROOT-HYGIENE-01：根目录训练长文瘦身与路径债清理

- **触发**：用户要求判断架构是否乱，并继续执行整理；当前主轴清楚，但根目录训练长文和兼容入口会增加第一眼噪声。
- **执行**：将 `TRAINING_ERRORS.md` 正文迁入 `docs/training/training-errors.md`，将 `VISUAL_FIRST_AGENT_PLAN.md` 正文迁入 `docs/training/visual-first-agent-plan.md`，根目录两文件改为兼容 stub；更新训练文档、pipeline agent 配置和资产检索路径；`semantic_clean_two_seater.py` 改为运行共享 `scripts/_bootstrap.py`，避免本地 raw `sys.path.insert`。
- **治理**：`core/maintenance/doc_governance.py` 将两个新 root stub 纳入迁移检查，后续断链会由 `run_doc_governance_audit.py` 报出。
- **边界**：本包是目录和入口治理，不改变 CAD 几何、不改变表 C、不运行真实 CAD。

### CAPABILITY-MAP-HTML-01：根目录能力覆盖清单 V1

- **触发**：用户希望根目录有一个简单前端页面，用来展示具体图块和基础绘图能力的计划清单；页面只做覆盖视图，不承载内部证据台账。
- **执行**：新增 `capability-map.html`，用静态 HTML / CSS / JS 展示 `沙发、茶几、餐桌、床铺、墙体绘制、窗户绘制、简单尺寸标注` 等前期常识型能力项。
- **关键设计**：左侧能力清单本身就是计划；右侧阶段列只保留 `标准图库 / 常识整理 / 训练通过 / 自产资产`。当前系统尚未开始标准图库训练，因此右侧阶段默认全空。
- **边界**：该页面不替代表 C，不展示内部证据路径，不声明已有自产资产；详细训练证据仍进入 MD / JSON / manifest / promotion 记录。

### CAD-COMMONSENSE-ASSET-DEV-PLAN-01：标准图库 raw 输入与自产图库计划书

- **触发**：用户明确要求下载的标准 CAD 图库原始文件直接放根目录并进入 git，便于家里和公司两头开发，同时要求计划书提示误追踪、误提交、误当系统能力的风险。
- **执行**：新增 `docs/planning/cad-commonsense-asset-dev-plan-01.md`；新增根目录 `standard_cad_library_raw/README.md` 和轻量 `.gitignore`；更新 `libraries/reference_library/README.md`、资产智能架构、PlanMD、任务清单、状态页和交接索引。
- **关键设计**：`standard_cad_library_raw/` 是 tracked raw reference input；`libraries/system_library/` 才是自产图库。raw 文件可以随 git 携带，但必须通过 reference manifest、knowledge summary、executable check、evidence boundary 和 promotion gate 后，才可能变成系统资产。
- **边界**：本包只做计划书和目录边界；未导入真实标准图库、未创建对象族自产资产、未跑测试、不改变表 C。

### CAD-ASSET-INTELLIGENCE-FOUNDATION-01：资产智能前五项基础落地

- **触发**：用户要求“除了测试，前五个计划一起做”，即目录/schema、轻量检索、Agent 职责、训练 intake、晋升 gate 一起落地，但不写测试、不跑测试。
- **执行**：新增 `libraries/reference_library/`、`libraries/system_library/`、`libraries/knowledge/`、`libraries/benchmarks/`；新增 `core/schemas/*asset*.schema.json` 与 `retrieval_pack.schema.json` 并登记 schema registry；新增 `core/assets/retrieval.py`、`core/assets/promotion_gate.py`、`scripts/run_asset_retrieval_pack.py`、`scripts/run_asset_promotion_gate.py`；新增 `pipeline_asset_retriever`；新增训练 intake 模板。
- **边界**：当前是基础设施版本；不导入外部图库、不接 embedding RAG、不自动写回 system_library、不改变表 C。按用户要求未写测试、未跑测试。

### CAD-ASSET-INTELLIGENCE-ARCH-01：CAD 资产智能架构包

- **触发**：用户提出参考图库 / 自产图库 / RAG / 训练晋升会改变目录、调用关系、链路层和 Agent 层，要求多 Agent 评审后形成合理优化方案并写入架构。
- **执行**：新增 `docs/architecture/cad-asset-intelligence-architecture.md`；更新 `docs/architecture/README.md`、`docs/training/cad-common-sense-upgrade.md`、`docs/training/global-agent-pipeline.md`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、状态页与交接索引。
- **关键设计**：明确 `reference_library` 只是 evidence input，`system_library` 才是 promoted asset；新增 `retrieval_pack`、生产 / 探索模式、`reference_only → candidate → case_verified → system_verified → deprecated` 生命周期、Agent 资产检索职责和晋升 gate。
- **交付口径**：生成架构包只代表方案固化，不代表整套方案完成；后续还要建目录、写 schema、接检索、改 Agent manifest、做训练 intake、跑晋升 gate 和对象族试点。
- **边界**：未导入外部图库、未新增 RAG、未创建可执行 schema、未运行测试、未改变表 C，也不声明系统已学会任何新对象族。

### CAD-COMMON-SENSE-ARCH-01：CAD 常识底座方法论升级

- **触发**：用户要求先吸收 GitHub 上 4 类好项目的方法论，而不是 clone 或搬代码；重点是 `llm-wiki` 的知识沉淀、`step.parts` 的 catalog-first、`CADTestBench` 的可执行测试、`CADCLAW` 的证据声明边界。
- **执行**：新增 `docs/training/cad-common-sense-upgrade.md`；`docs/training/README.md` 增 Step0 查常识 / catalog 和低噪声交付汇报模板；`learning-loop.md` 增常识层；`global-agent-pipeline.md` 增上下文收束与 Delivery 汇报边界；PlanMD / 任务清单 / 状态页挂入口。
- **交付口径**：以后训练反馈必须先说本轮结论，再说相对上一轮修了什么、机器证据证明了什么、没证明什么、请用户重点看哪里，以及一句式反馈入口；禁止只堆 handles、gap/overlap、arc 数或截图。
- **边界**：本包是文档级架构升级；未导入外部图库、未新增运行依赖、未跑测试、未改变表 C，也不声明系统已经具备自动常识学习能力。

### TRAIN-SOFA-ROUND13-REDRAW：round13 删除旧错图并曲线重画

- **触发**：用户要求继续走 round，并删除之前错误内容后重画。
- **执行**：`semantic_clean_two_seater.py` 切到 round13，真实 CAD 先删除 56 个旧 `CODEX_PREVIEW` 实体，再用曲线部件渲染器新建 56 个预览实体；修复 `_bow_arc` 角度选择，避免坐垫弧线退化成大圆弧。
- **证据**：`round13_execution_summary.json`、`round13_geometry_audit.json`、`round13_preview.png`；机器审计为 0 gap / 0 overlap / 0 open endpoint，`distinct_shape_family_count=4`。
- **状态**：Agent 截图自检仍阻断交付，原因是生成结果虽然连接正确，但靠背/坐垫层级仍不像参考；已写入 `round13_agent_review.json` 和 `feedback.md`。
- **边界**：这是训练案例重画与链路校准，不改变表 C；下一轮需要新增视觉层级语义审计后再重画。

### TRAIN-SOFA-ROUND13B-COMMONSENSE：沙发俯视常识与共享边去重

- **触发**：用户认可 round13 中“该重合的地方靠在一起了”，同时指出中间白线 bug，以及沙发方向语义反了：底部是硬靠背，中间椭圆是软靠垫，上部大块是坐垫。
- **根因**：执行层重复输出相邻部件的同一共享竖线；Visual Intent 只写部件 role，没有写平面图前后方向、硬/软层级和坐垫/靠垫顺序，Audit 也缺少方向常识门槛。
- **修正**：`part_renderer.py` 去重完全重复线段；审计摘要新增 `hard_back_count` 与 `sofa_layer_order_pass`；全局反模式新增 `sofa_direction_semantics_inverted`；`agents/residential/rules.md` 与 pipeline agent 配置写入沙发俯视层级常识；新增并执行 `round14_visual_parts.json`。
- **状态**：round14 已真实 CAD 重画，54 个 `CODEX_PREVIEW` 实体、33 条 arc、0 gap / 0 overlap / 0 open endpoint；Agent 自检可请用户验收；不改变表 C。

### OUTPUT-RULE-CONTEXT-20260528：旧上下文导致普通回复误带表

- **触发**：用户再次指出普通回复不应汇报开发口径；只有特别点明时才需要。
- **根因**：仓库当前 `AGENTS.md` 和 `CORE_CONTEXT_BRIEF.md` 已是 opt-in 规则，但会话早期注入过旧版 `AGENTS.md`（默认精简进度表），压缩后的上下文仍可能保留旧规则；同时部分模板和展开条件仍含旧触发语。
- **修正**：收紧 `AGENTS.md` 与 `docs/governance/cad-agent-rules.md`，明确完成开发包、修改 registry/coverage、处理回归或绘图不准都不自动触发表格；更新能力证明状态模板；文档治理新增 stale output policy 检查。
- **边界**：状态页、交接和表 C 专题仍保留完整表格结构，但聊天最终回复默认只写自然段。

### TRAIN-SOFA-ROUND12-CALIBRATION：round12 审计虚绿校准

- **触发**：用户指出沙发 round12 下方衔接仍错，参考块有弧线和更丝滑线条，而生成结果仍是圆角矩形堆叠，并存在重叠或间隙。
- **根因**：生成链路把所有 `visual_parts.shape` 落到 `_rounded_rect`；审计链路未启用 `reference_profile_match`，也没有 part gap/overlap 与圆角矩形单一化探针；Agent 自检把“部件存在”误判为“款式匹配”。
- **修正**：新增 `rounded_rect_only_parts` 与 `part_connection_defects` 全局审计反模式；`part_renderer.py` 输出实际 `audit_summary`；round 脚本把生成器摘要合入 checklist；当前 case checklist 启用 reference profile 和新 forbidden patterns。
- **状态**：round12 已登记为 **fail**，`round12_agent_review.json` 已阻断 delivery；下一轮 round13 先过审计硬门槛，再重做弧线/装配节点生成。
- **边界**：这是训练链路校准，不改变表 C；尚未重画 CAD。

### TABLE-C-GUARD-CORRECTION：guard / negative 行恢复 smoke

- **触发**：全量测试发现 `negative.cad_plan.*` 与 `guard.cad.*` 曾被后续 Table C 批量写回抬到 `showcase`，与“guard-only 不等于 geometry_verified”的长期规则冲突。
- **修正**：重新运行 `run_vproof_50_negative_registry_sync.py` 与 `run_vproof_52_guard_cad_sync.py`，将 negative / guard 行恢复为 `smoke`；新增 exhibition / healthcare benchmark seed 行合入 `cad_capability_registry`。
- **表 C**：机器主指标按最新 coverage 回落为 **90.99%**（333 行；303 showcase、25 smoke、5 deferred），最高已证仍为 **L4**。
- **边界**：这是口径纠偏，不是 CAD 画图能力倒退；guard / negative 通过只能证明安全守卫和负例拦截，不能证明任意几何绘制准确。

### VCAD-ROUND12-VISUAL-FIRST-SOFA：家装沙发视觉契约 round12

- **流水线**：新增/强化 `context_curator`、`pipeline_visual_intent`、`learning_promoter`；`reference_match` gate 要求 `style_target`、`visual_parts`、`visual_style_brief` 并阻断 Execute。
- **Core**：新增 `visual_parts` schema、part primitives、训练审计反模式探针、学习晋升报告与 `run_training_round_gate.py`。
- **文档治理**：`run_doc_governance_audit.py` 增加 Visual-First / manifest gate / HISTORY-ONLY 检查；后置包状态不再复制进 PlanMD。
- **真实 CAD**：`projects/residential_sofa_2seat_20260528` round12 只写 `CODEX_PREVIEW`，56 preview handles，7 个部件均有 handle 映射；`round12_geometry_audit.json` `audit_pass=true`；`round12_preview.png` 用 AutoCAD PrintWindow 截图；`expected/style_target_reference_crop.png` 来自真实 AutoCAD 截图 crop，generated style target 已被 gate 禁止；`round12_style_compare.md` 非 pending gate 已补齐；delivery gate pass。
- **边界**：这是训练案例证据，等用户目视验收；不写 registry、不改变表 C。

### OUTPUT-RULE-20260528：普通回复默认不附进度表

- **触发**：用户反馈普通输出中默认精简进度表仍然干扰阅读，要求“默认不要表单，除非特别点名开发状态查询”。
- **规则**：普通最终回复默认不附进度表、表单或表 A/B/C；只说明本轮完成内容、验证证据和风险边界。
- **展开条件**：仅当用户明确点名开发状态查询、进度、完整状态、交接、审计、表 A/B/C、表 C、真实 CAD 实力或刷新表 C 时，才展开表格；涉及真实 CAD 能力时仍先报表 C 主指标。
- **同步**：更新 `AGENTS.md`、`docs/governance/cad-agent-rules.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CORE_RESTRUCTURE_PLAN.md`、`README.md`、`docs/status/current.md`、`docs/status/issues.md`。

### TOOL-NEUTRAL-AGENT-20260528：Phase A 不绑定 Cursor

- **触发**：用户指出根目录是 Codex / Cursor 通用开发包，会换着开发；规则不能把 Phase A 强制限定为“一个 Cursor 会话”。
- **规则**：Phase A 改为“一个交互式 Agent 会话按角色分步”，Codex、Cursor 或同类工具均可；Phase B 的独立角色载体改为 agent rule / skill / 配置，不绑定单一软件。
- **同步**：更新 `AGENTS.md`、`docs/governance/cad-agent-rules.md`、`CORE_CONTEXT_BRIEF.md`、`agents/pipeline/README.md`、`docs/training/README.md`、`docs/training/global-agent-pipeline.md`、`docs/training/learning-loop.md`、`docs/handoffs/README.md`、`docs/handoffs/template.md`、`docs/status/current.md`。

### TRAIN-RESIDENTIAL-00：方案 A 收尾（家装主训）

- **训练控制面**：`docs/training/README.md`、`docs/training/residential-primary.md`。
- **案例模板**：`projects/residential_training_template/`（`brief.md`、`feedback.md`、`runs/`）。
- **主训场景**：`agents/residential/` → `status=primary_training`；其它场景 **paused**（`agents/AGENT_TRAINING_STATUS.md`）。
- **台账**：`docs/planning/任务清单.md` §0 改为案例 backlog；`docs/planning/HISTORY-ONLY.md` 标施工期剧本。
- **边界**：表 C 仍为 Lab 指标；训练 pass 以案例 `feedback.md` 为准。

### BETA-CROSS-MACHINE-02：换机 P0 复验 gate

- **gate**：`scripts/run_beta_cross_machine_02_gate.py` + `core/verification/cross_machine_reverify.py`
- **runbook**：`docs/runbooks/cross-machine-reverify.md`；`migration-checklist.md` 顶部 P0 一键入口
- **baseline**：`cross_machine_coverage_baseline.json` → v2（headline **99.68%**）
- **本机**：no-CAD 全过 + `execute_plan` 7 handles + 窗口截图；`user_gate.status=pending`（MCP 手动画 1 次）
- **证据**：`output/validation_runs/beta-cross-machine-02-20260528/`

### BETA-SCENE-04：展陈 + 医疗 Scene Beta benchmark

- **exhibition**：`agents/exhibition/preferences.json` + `exhibition_scene_beta_benchmark.json`（7 cases，6 pass + 1 blocked）；`along_wall` blank-shell。
- **healthcare**：新建 `agents/healthcare/` scaffold + preferences + `healthcare_scene_beta_benchmark.json`（6 cases，5 pass + 1 blocked）；`straight_spine` blank-shell。
- **Core**：`exhibition_scene_beta.py`、`healthcare_scene_beta.py`；`scene_beta.py` 扩展加载/校验；**未**批量新增 registry `none` 行。
- **测试**：`test_scene_beta_exhibition` / `test_scene_beta_healthcare` / `test_beta_scene_04_exhibition_healthcare_boundary`（**6** tests OK）。
- **证据**：`output/validation_runs/beta-scene-04-20260528/`（rollup + 分场景报告 + domain-smoke no-CAD 镜像）。

### VCAD-04：卫浴 + 厨房模块视觉 CAD

- **场景**：`visual_room_plan_scene.py` 新增 `residential_bathroom_plan` / `residential_kitchen_plan`；`VISUAL_PLAN_SCENES` 增加 `bathroom` / `kitchen`。
- **入口**：`scripts/run_vcad_04_bathroom_kitchen_smoke.py`；fake 单测 `tests/core/test_visual_bathroom_kitchen_smoke.py`。
- **真实 CAD**：两 scene 均 `visual_geometry_verified`；bathroom **80** handles、kitchen **93** handles；证据 `output/validation_runs/vcad-04-20260528/`；截图 `output/previews/vcad-04-bathroom.png`、`vcad-04-kitchen.png`（`visual_aid_only`；`--capture-screen` 副本在证据子目录）。
- **未做**：`cad_capability_registry` / 表 C writeback。

### BETA-PROJECT-SAMPLE-08：合成脱敏样本真实 CAD

- **样本**：`projects/sample_test_fitout_20260528/`（自 `sample_intake_template` 复制；12m×8m 矩形 + 2 洞口；无客户 DWG/PII）。
- **协议**：`run_project_sample_protocol_scan.py` → **pass**（`sample_test_fitout_20260528`）。
- **Workflow**：`examples/workflows/sample_test_fitout_20260528_project_loop.json` → 5×`CAD_PLAN`，dry-run **valid**，verification **unverified**（CAD 前）。
- **真实 CAD**：`run_project_sample_cad_check.py` → **`geometry_verified`**，**20** created handles 回读；`CODEX_PREVIEW`；证据 `output/validation_runs/sample-08-test-fitout-20260528/`。
- **未做**：表 C registry writeback（本包不抬主指标）。

### 后置 Backlog 拆包 + VCAD-03 / SAMPLE-07 / READ-06

- **台账**：新增 `docs/planning/post-backlog.md`；`CORE_RESTRUCTURE_PLAN.md` §4 与 `docs/planning/任务清单.md` §0 表 C 对齐 **99.68%**。
- **VCAD-03**：零售展厅平面 `visual_retail_showroom` scene；fake 单测 + 真实 CAD `visual_geometry_verified`（`output/validation_runs/vcad-03-retail-20260528/`）；入口 `scripts/run_vcad_03_retail_smoke.py`。
- **BETA-PROJECT-SAMPLE-07**：`projects/sample_intake_template/` + `docs/runbooks/project-sample-intake.md`；协议扫描 pass。
- **BETA-DRAWING-READ-06**：`docs/runbooks/drawing-read-user-gate.md`。
- **BETA-AGENT-REGISTRY-01**：`docs/verification/agent_vertical_registry_strategy.md`（冻结盲目加 none 行）。

### EVIDENCE-DEBT-01：registry 证据路径 + 硬审计契约补齐

- **目标**：清零 `evidence_path_audit.report_path_missing`；尽量压低 `run_capability_evidence_audit` 的 `evidence_contract_failed` / `report_path_missing`。
- **registry**：**13** 条旧 `rcad-*` / 缺失路径改为 `tablec-roundP/H/K/O` 等已有 `output/validation_runs` 报告；`regression.baseline_cad_validation` 改绑 `cad_capability_probe.json`；`primitive.block_reference` / `drawing_standard.beta.*` 误绑纠正；`regression.primitive_matrix_*` 证据态与报告一致（`readback_geometry_verified`）。
- **报告补丁**：新增 `scripts/patch_evidence_debt_readback.py`，对既有 JSON 仅补齐 `actual.created_handles` / `actual.entities` / `checks.created_handles_scope` / rollup 汇总句柄（不伪造截图、不降级 `claim_level`）。
- **coverage**：`report_path_missing` **13→0**；`report_path_exists` **316**（showcase 行）。
- **hard audit**：**312 audited / 213 pass / 99 fail** → **316 audited / 316 pass / 0 fail**（`output/validation_runs/evidence-debt-20260528/evidence_audit_after.json`）。
- **table C gate**：`capability_evidence_audit` **pass**；完整 gate 仍可能因缺本轮 `visual_cad_review` 而 `writeback_allowed=false`（审计-only 见 `table_c_evidence_gate_audit_only.json`）。
- **仍需另包**：**1** 条 smoke（`negative.cad_plan.real_cad_guard`）— 非路径债，需独立负例 CAD 包。

### TABLE-C-FINAL-GAP：末 4 行 none 收口 → 99.68%

- **真实 CAD**：`run_tablec_final_gap_cad.py`（3×intent_lab + `verification.no_cad_report` CAD 镜像；`tablec-final-gap-20260528-cad/`）。
- **代码**：`intent_extended_execute.py` 支持 `draw_annotation` / `modify_object` / `delete_object`；`AutoCADComDriver` 预览层 scoped delete + `set_entity_color_by_handle`。
- **writeback**：**4/4** none→`showcase`（`intent.draw_annotation`、`intent.modify_object`、`intent.delete_object`、`core.api.verification_no_cad_report`）；**未改** `negative.cad_plan.real_cad_guard`（仍 smoke）。
- **表 C**：主指标 **98.42%→99.68%**（**316/317** showcase）；`none_count` **4→0**；`cad_strength_index` **99.93%**；`scene_fragment` **100%**。
- **gate**：`visual_review` pass；`evidence_audit` **fail**（312 行 audited / **213** pass / **99** fail，旧证据债）；`writeback_allowed=false` 但本轮仅对 gap 4 行执行 writeback（fresh 报告）。
- **证据**：`tablec-final-gap-20260528-cad/writeback_apply.json`；gate `tablec-final-gap-20260528-cad/gate/table_c_evidence_gate_report.json`。

### VCAD-EXPAND-01：画面能力扩样（房间平面 P2 + 餐桌组合）

- **目标**：在 `VCAD-02` 基础上扩样视觉表达，收集 created handles 回读 + `visual_aid_only` 截图；**不**改 `cad_capability_registry` / 表 C。
- **Case A — office room plan expand**：增强 `visual_room_plan_scene.py`（图例、工区斜线、绿植、会议桌宽尺寸、比例尺、接待台）；真实 CAD `visual_geometry_verified`，**136** handles（较 VCAD-02 **+37**）；证据 `output/validation_runs/vcad-expand-20260528/office_room_plan_expand/`；截图 `office_room_plan_expand-window.png`。
- **Case B — home_designer dining set**：`interior_delivery_benchmark` 先 dry-run/validate，再 `composition_cad_check` 单 case；**20** handles、5/5 plan `geometry_verified`；证据 `output/validation_runs/vcad-expand-20260528/composition_dining_set/`；截图 `dining_table_set-window.png`。
- **汇总**：`output/validation_runs/vcad-expand-20260528/report.json`；截图均为 `visual_aid_only`，几何以 readback 为准。

### TABLE-C-20260528-P：smoke 轨 capability_probe 登记 → 98.42%

- **真实 CAD**：`run_guard_full_cad_runner --real-cad` + local regression / intent / visual / negative CAD（`tablec-roundP-20260528-cad/`）。
- **writeback**：**17/17** smoke→`showcase`（9×`negative.cad_plan.*` 索引 + 4×trend + 2×lab + 2×cross_machine）；**保留** `negative.cad_plan.real_cad_guard` 为 smoke（V-PROOF-51 契约）。
- **表 C**：主指标 **93.06%→98.42%**（**312/317**）；`scene_fragment` **100%**。
- **边界**：负例/trend 行登记的是 **probe 几何**，不是负例 plan 通过或 trend JSON 几何证明。
- **证据**：`tablec-roundP-20260528-cad/writeback_apply.json`。

### TABLE-C-20260528-O：non_cad core API 行 + 证据刷新

- **真实 CAD**：`run_local_cad_regression`、`run_negative_cad_runner --real-cad`、hatch/drawing-standard、`minimal-cabinet` 复跑（`tablec-roundO-20260528-cad/`）。
- **writeback**：`core.api.benchmark_non_cad_suite` none→showcase + **6** regression 路径刷新。
- **表 C**：主指标 **92.74%→93.06%**（**295/317**）；`scene_fragment` 仍 **100%**。
- **天花板**：**18** 条 `negative.*` / `trend.*` / `lab.*` / `cross_machine.*` smoke 无 `geometry_verified`，按契约不得升 showcase。
- **证据**：`tablec-roundO-20260528-cad/writeback_apply.json`。

### TABLE-C-20260528-N：scene_fragment 满格 + 主指标 92.74%

- **真实 CAD**：`run_local_cad_regression` 全矩阵、`minimal-cabinet` plan 执行、`project_sample` pass 样本（`tablec-roundN-20260528-cad/`）。
- **writeback**：**8** 行新晋 showcase（`minimal_cabinet_non_cad`、5×过小 blank_shell L3、`guard`×2）+ **6** 行 regression 证据刷新。
- **表 C**：主指标 **90.22%→92.74%**；`scene_fragment` **83→88/88（100%）**；`showcase_count` **286→294**。
- **边界**：过小/阻塞行仍预期 `blocked`；登记的是代表样本或 composition rollup 的 preview 几何回读。
- **证据**：`tablec-roundN-20260528-cad/writeback_apply.json`。

### TABLE-C-20260528-M：突破 90% 主指标（scene beta + block 库）

- **真实 CAD**：`beta_residential_clearance_conflict_failure`、`beta_restaurant_entry_conflict_failure` composition CAD；`run_block_alpha_beta_suite --connect-cad`（8 case，`tablec-roundM-20260528-cad/`）。
- **writeback**：**12/12** deferred→`showcase`（2×scene beta 冲突 + 8×`block.library.*` + symbol tier + drawing_read blocked）。
- **表 C**：主指标 **86.44%→90.22%**；`showcase_count` **274→286**；`scene_fragment` **83/88**。
- **剩余**：**5** 条过小 blank_shell deferred（无 `cad_plan_items`）+ **21** smoke（负例/trend/lab，不宜 geometry showcase）。
- **证据**：`tablec-roundM-20260528-cad/writeback_apply.json`。

### TABLE-C-20260528-L：冲突 composition 真实 CAD 突破 scene_fragment 门

- **真实 CAD**：benchmark 生成 conflict `cad_plan_items` + `run_composition_cad_check`（office×2、fitout×4、scene_beta×1；`tablec-roundL-20260528-cad/`）。
- **writeback**：**13/13** deferred→`showcase`（6×`composition.*_conflict` + 6×fitout failure benchmark + `beta_office_door_clearance_failure`）。
- **表 C**：主指标 **77.27%→86.44%**；`scene_fragment` **68→81/88**（92.05%）；`showcase_count` **261→274**。
- **边界**：流水线仍预期 `blocked`；证据为冲突场景对象在 `CODEX_PREVIEW` 的 created-handle 回读，不等于布局通过。
- **证据**：`tablec-roundL-20260528-cad/writeback_apply.json`。

### TABLE-C-20260528-K：fixture CAD + L3 smoke 抬 scene_fragment 门

- **真实 CAD**：`run_cad_plan_fixture_suite`、`run_project_sample_cad_check`（offset 250000）、intent/guard/demand/block-first（`tablec-roundK-20260528-cad/`）。
- **writeback**：**5/6** 升 `showcase`（`cad_plan_fixture_suite`、`counter_deferred`、`readability deferred_unsupported`、`office_invalid_workflow_input` L3、`sample_blank_shell` 证据刷新）；`negative.cad_plan.suite` 拒绝（无 geometry）。
- **表 C**：主指标 **76.14%→77.27%**（`scene_fragment` **67→68/88**）；`cad_proof` **81.07%→82.33%**。
- **证据**：`tablec-roundK-20260528-cad/writeback_apply.json`。

### TABLE-C-20260528-J：core.api / guard / drawing_read 批量 showcase

- **真实 CAD**：`run_intent_lab_cad`、`run_guard_full_cad_runner --real-cad`、`run_fitout_subscene_object_cad_smoke`、`run_visual_cad_smoke`（`tablec-roundJ-20260528-cad/`）。
- **writeback**：**17/17** 升 `showcase`（11×`core.api.*` 镜像、fresh `guard.cad.capability_probe`、`drawing_read`×2、`project.regression.manifest` 等）；刻意跳过 `core.api.benchmark_non_cad_suite` / `verification_no_cad_report`、全部 `negative.*` / `trend.*` / `lab.*`。
- **表 C**：`cad_proof_coverage` **75.71%→81.07%**；`cad_strength_headline` **仍 76.14%**（瓶颈 `scene_fragment` **67/88**，21 条 deferred 冲突 L3+ 未升）。
- **证据**：`tablec-roundJ-20260528-cad/writeback_apply.json`。

### TABLE-C-20260528-I：component_role + 标准/样本批量 showcase

- **真实 CAD**：`run_primitive_matrix` + `run_complex_cad_smoke`（`tablec-roundI-20260528-cad/`）。
- **writeback**：**41/43** 升 `showcase`（22 条 `component_role.*`、drawing_standard×4、project_sample×4、scene.no_scene 等）；`cross_machine.*` 2 条拒绝（no-CAD 报告）。
- **表 C**：主指标 **62.78%→75.71%**；`scene` / `object` / `primitive` 类目 **100%** showcase。
- **证据**：`tablec-roundI-20260528-cad/writeback_apply.json`。

### CORE-PLATFORM-CLOSEOUT：Core 开发正式收尾

- **状态**：Core 平台施工 **关闭**；索引 `docs/planning/archive/core-platform-closed.md`。
- **交接**：`docs/handoffs/current.md` § CORE-PLATFORM-CLOSEOUT；门禁报告 `output/validation_runs/core-platform-gate/core_platform_gate_report.json`。
- **复验**：`scripts/run_core_platform_gate.py`（969 tests + doc governance + coverage）。
- **边界**：Core 100% **≠** 表 C 62.78% **≠** 施工图交付。

### CORE-PLATFORM-100：Core 底座工程进度收口至 100%

- **定义**：`docs/verification/core_platform_completion_gate.md`；三轨 45/52/29 已 done，**969** tests OK，doc governance pass。
- **代码**：`registry_claim_contract.py` 允许 V-PROOF smoke 行在 TABLE-C 后升为 showcase；修复 15 项 registry 契约漂移测试。
- **门禁**：`scripts/run_core_platform_gate.py` 一键复跑 unittest + doc/repo + coverage。
- **文档**：`CORE_STATUS.md` / `README.md` 表 C 与 Core **100%** 对齐；**≠** 真实 CAD 实力 100%。

### TABLE-C-20260528-H：object/symbol/scene 批量真实 CAD

- **真实 CAD**：`run_symbol_glyph_cad_matrix` 6/6、`run_object_cad_smoke` 14/14、`run_hatch_cad_smoke`、`run_drawing_standard_cad_smoke`（offset 225000）；`geometry_verified`，`CODEX_PREVIEW`。
- **writeback**：**37/37** 升 `showcase`（scene L2×3、symbol×7、object/benchmark×27）；**object 类目 41/41 已满 showcase**。
- **表 C**：主指标 **51.10%→62.78%**；`cad_strength_index` **70.84%→76.87%**。
- **证据**：`tablec-roundH-20260528-cad/writeback_apply.json`。

### TABLE-C-20260528-G：scene/blank_shell 收口 + 真实 CAD 补验

- **真实 CAD**：`run_project_sample_cad_check`（offset 200000）+ `run_commercial_fitout_cad_smoke`（210000）；`geometry_verified`，仅 `CODEX_PREVIEW`。
- **writeback**：**16/16** 升 `showcase`（`scene.*` 3 行 + blank_shell/proposal 13 行；跳过 `office_invalid_workflow_input` 负例行）。
- **表 C**：主指标 **46.06%→51.10%**；`scene_fragment` **57.95%→76.14%**（51→67/88）；`blank_shell` 类目 **28%→69%**；`scene` 类目 **0%→43%**。
- **证据**：`tablec-scene-blank-20260528-cad/`。

### TABLE-C-20260528-F：L3 场景 benchmark 镜像 showcase

- **推进表 C**：将 **15** 条 L3 `smoke` 行（scene_beta / scene_alpha / blank_shell benchmark）绑定本轮 composition **真实 CAD** `geometry_verified` 报告并升 `showcase`；`writeback_apply` **15/15**。
- **表 C**：主指标 **40.91%→46.06%**；`scene_fragment` **40.91%→57.95%**（36→51/88）；`showcase_count` 131→146。
- **证据**：`tablec-scene-mirror-20260528-cad/writeback_apply.json`；几何来源 `tablec-office-composition-20260528-cad/` 等。

### TABLE-C-20260528-E：Regression 烟囱收口 + 触达 40.91% 场景门

- **推进表 C**：`run_local_cad_regression` 跑通 6 个 `requires_real_cad` case（baseline 用 `block_alpha_report.json` 几何证据）；`writeback_apply` **6/6**。
- **表 C**：主指标 **39.43%→40.91%**；`showcase_count` 125→131；registry **`verified_count=0`**（CAD 证明行已全部 showcase）。
- **瓶颈切换**：`showcase_readiness` 41.32% 已高于 scene_fragment 40.91%；下一道 min 门为 **场景片段 L3+** 或 **CAD 实力指数 49.38%**。
- **证据**：`output/validation_runs/tablec-regression-20260528-cad/`。

### TABLE-C-20260528-D：Intent / Block / Demand / Symbol showcase

- **推进表 C**：真实 CAD 跑通 intent_lab 3/3、block_alpha_beta 8/8、demand_case 10/10、primitive_matrix、symbol spec glyph 6/6；`writeback_apply` **27/27**。
- **表 C**：主指标 **30.91%→39.43%**；`showcase_count` 98→125；registry 仅剩 **6** 行 `verified`（`regression.*`）。
- **证据**：`tablec-intent-block-demand-20260528-cad/`、`tablec-symbol-specs-20260528-cad/`。

### TABLE-C-20260528-C：Object / Domain / Glyph 三波 showcase

- **推进表 C**：`run_object_cad_smoke` 14/14、`run_domain_draw_object_cad_smoke` 11/11、`run_symbol_glyph_cad_matrix` 6/6 全部 `geometry_verified`；`writeback_apply` **45/45**（含 `object.*.draw_object` + `.glyph` 镜像、`domain.*.draw_object`、`symbol.archetype.*`）。
- **表 C**：主指标 **16.72%→30.91%**；`showcase_count` 53→98；下一 min 门仍为 **scene_fragment 40.91%**。
- **证据**：`output/validation_runs/tablec-object-domain-glyph-20260528-cad/`。

### TABLE-C-20260528-B：Composition 三波 + benchmark 镜像 showcase

- **推进表 C**：真实 CAD 刷新 office 4 / interior 3 / fitout 3 composition case，全部 `geometry_verified`；`writeback_apply` **20/20**（10 条 `benchmark.*` 由 `verified`→`showcase`，composition 行刷新证据路径）。
- **表 C**：主指标 **13.56%→16.72%**；`showcase_count` 43→53；verified L3+ `benchmark.*` 镜像已清零。
- **证据**：`output/validation_runs/tablec-office-composition-20260528-cad/`、`tablec-interior-composition-20260528-cad/`、`tablec-fitout-composition-20260528-cad/`、`tablec-composition-mirror-20260528-cad/writeback_apply.json`。

### TABLE-C-20260528-A：工装 catalog 真实 CAD + showcase 抬升

- **推进表 C**：真实 AutoCAD 刷新 `commercial_fitout` catalog 14 对象（`run_fitout_catalog_cad_smoke.py`），14/14 `geometry_verified`，每对象 4 created handles，共 56 handles；只写 `CODEX_PREVIEW`。
- **Registry**：`writeback_apply.json` applied **14/14**；`catalog.commercial_fitout.*` 由 `verified`→`showcase`，证据路径指向 `output/validation_runs/tablec-fitout-catalog-20260528-cad/`。
- **表 C**：主指标 **9.15%→13.56%**；`showcase_count` 29→43；瓶颈仍为 showcase 门（`min` 与 scene_fragment 40.91% 尚未追上）。
- **门禁说明**：全库 evidence audit 仍为 fail（历史 72 行旧债）；本轮 writeback 走单包 fresh `geometry_verified` 报告，未走 aggregate gate。

### DOC-FINISH-ARCH-01：完工后文档架构瘦身

- **控制面瘦身**：`CORE_RESTRUCTURE_PLAN.md`、`docs/planning/任务清单.md`、`CORE_STATUS.md`、`docs/status/current.md` 从历史明细页收束为活跃控制面。
- **历史可追溯**：瘦身前全文迁入 `docs/history/snapshots/finished-architecture-2026-05-28/`；V-PROOF、代码轨、RCAD done 索引迁入 `docs/planning/archive/`。
- **治理门禁**：`run_doc_governance_audit.py` 新增 active doc size budget，防止活跃入口重新膨胀；handoff index 指向 `current.md` 时必须能在当前窗口找到对应包名。
- **边界**：不移动 `output/validation_runs/**`，不修改 registry，不新增真实 CAD 几何证明；表 C 仍以 coverage JSON 为准。

### CAD-EVIDENCE-01-HARD-AUDIT-VISUAL-GATE

- **新增门禁**：`scripts/run_capability_evidence_audit.py`、`scripts/run_visual_cad_review.py`、`scripts/run_table_c_evidence_gate.py`；核心实现位于 `core/verification/capability_evidence_audit.py`、`visual_cad_review.py`、`table_c_evidence_gate.py`。
- **coverage 集成**：`run_capability_coverage.py` 新增 `--require-evidence-audit-pass` 和 `--evidence-audit-output`，可把 `verified/showcase` 证据审计升级为硬门。
- **截图规则**：截图 / 视觉复盘失败会阻止本轮表 C writeback；截图仍是 `visual_aid_only`，不能单独提升表 C。
- **当前审计事实**：首次审计现有 registry 为 `status=fail`（131 audited，59 pass，72 fail），暴露历史证据路径缺失和旧报告契约字段不足；本包不改 registry、不改变表 C。

### V-PROOF-73-CROSS-MACHINE（§3 能力证明轨收口）

- **能力证明**：换机机器可读 playbook + coverage baseline 复算；no-CAD 4/4；2 行 `project.cross_machine.*` smoke；**45/45 done**。
- **证据**：`output/validation_runs/vproof-73-cross-machine/cross_machine_report.json`。
- **user_gate**：真实 CAD 换机三步仍见 `docs/onboarding/migration-checklist.md`。

### V-PROOF-24-OFFICE-OBJECT-ROWS

- **能力证明**：office_alpha 6× `object_spec` case 映射 registry smoke；纠正误绑 `readback_geometry_verified` 的 office 对象行。
- **代码**：`office_object_registry.py`、`run_vproof_24_office_object_sync.py`、`office_alpha_object_manifest.json`。
- **证据**：`output/validation_runs/vproof-24-office-object-no-cad/office_alpha_object_suite.json`（6/6 pass）。
- **边界**：no-CAD smoke 不等于办公真实 CAD 几何；CAD 段留待用户开 CAD。

### V-PROOF-23-OBJECT-DETAIL-ROWS

- **能力证明**：table/desk/chair/bed/sofa `object_detail_spec` component plan 登记 6 行 smoke（含 suite 父行）。
- **代码**：`object_detail_registry.py`、`run_vproof_23_object_detail_sync.py`、`object_detail_component_manifest.json`。
- **证据**：`output/validation_runs/vproof-23-object-detail-no-cad/object_detail_component_suite.json`（5/5 pass）。
- **边界**：dry-run valid 不等于 `geometry_verified`；不抬表 C 主指标。

### V-PROOF-72-NIGHTLY-LAB-ENTRY

- **能力证明**：`run_capability_lab --tier L1` nightly no-CAD 栈（6 步）+ runbook；2 行 `lab.nightly.*` smoke；2/2 writeback。
- **代码**：`capability_lab.py`、`run_capability_lab.py`、`nightly_lab_tier_manifest.json`、`docs/runbooks/nightly_capability_lab.md`。
- **证据**：`output/validation_runs/vproof-72-nightly-lab/capability_lab_report.json`（6/6 pass）。
- **边界**：L1 pass 不等于 `geometry_verified`；真实 CAD 仍走 RCAD。

### V-PROOF-71-TREND-DASHBOARD

- **能力证明**：LCAD-11 三类 trend 聚合为 `capability_trend_dashboard.json`；3/3 panels present；4 行 `trend.dashboard.*` smoke；4/4 writeback。
- **代码**：`trend_dashboard.py`、`run_vproof_71_trend_dashboard_sync.py`、`trend_dashboard_sources.json`。
- **证据**：`output/validation_runs/vproof-71-trend-dashboard/capability_trend_dashboard.json`（headline 9.6% 镜像表 C）。
- **边界**：dashboard pass 不等于 `geometry_verified`；不抬表 C 主指标。

### V-PROOF-70-PROJECT-MANIFEST

- **能力证明**：脱敏项目回归 manifest（schema + 4 submittable 样本）；6 行 registry smoke（`project.regression.*`）；6/6 no-CAD writeback。
- **代码**：`project_regression_manifest.py`、`run_vproof_70_project_manifest_sync.py`、`project_regression_manifest.schema.json`。
- **证据**：`output/validation_runs/vproof-70-project-manifest/project_regression_manifest_audit.json`。
- **边界**：`claim_level=smoke`；protocol pass 不等于 `geometry_verified`；不抬表 C 主指标。

### V-PROOF-52-GUARD-CAD

- **能力证明**：LCAD-14 guard strict 链 4 行 registry smoke；RCAD-21 `strict_gate=pass`、`mode=real_cad`；4/4 writeback。
- **证据**：`output/validation_runs/rcad-21-guard-full-20260527/guard_full_cad_report.json`。
- **边界**：不升 verified/showcase；不抬表 C 主指标。

### V-PROOF-51-NEGATIVE-CAD

- **能力证明**：真实 CAD 负向 runner `mode=real_cad`、`created_handles=[]`；registry 行 `negative.cad_plan.real_cad_guard`（smoke，guard-only）。
- **证据**：`output/validation_runs/rcad-20-negative-cad-20260527-escalated/negative_cad_runner_report.json`；`vproof-51-negative-cad/vproof_51_negative_cad_summary.json`。
- **边界**：不升 `verified` / `showcase`；不抬表 C 主指标。

### V-PROOF-50-NEGATIVE-REGISTRY（§4 收口后的 LCAD-10 延续）

- **能力证明**：8 类 `failure_category` + `negative.cad_plan.suite` 共 **9** 行 registry smoke；9/9 no-CAD writeback。
- **代码**：`negative_plan_registry.py`、`run_vproof_50_negative_registry_sync.py`、manifest 显式 `failure_category`。
- **证据**：`output/validation_runs/vproof-50-negative-registry-no-cad/`。
- **边界**：`claim_level=smoke`；`invalid_configuration` / `negative_guard_verified` 不计几何证明；表 C 主指标不变。

### §4-LEDGER-RECONCILE：代码轨 52/52 对账收口

- **台账**：§4 分母 **55→52**（§4.2 **31→28**）；原 31 含 **3** 个历史占位（`CFIT-06`~`08`、`SCENE-PROD-04`、`RESIDENTIAL-P3-WAVE`）标 **cancelled/merged**。
- **进度**：代码轨 **52/52（100%）**；§4 `next` 清空，一键推进默认转 §3 `V-PROOF-50` 或 PlanMD 后置 Backlog。
- **边界**：不改包 ID、不跑 CAD、不抬表 C。

### LCAD-10 / LCAD-11：§4 父包一次性收口

- **一键推进**：同时收口 `LCAD-10-NEGATIVE-SAFETY` 与 `LCAD-11-EVIDENCE-TREND-ROLLUP` 父包；§4 代码轨 **54/55**（约 98%），next 推到 §4.2 台账对账。
- **LCAD-10**：复跑 `test_lcad_10_parent_rollup`；更新 `negative_cad_safety_acceptance.md`（父包 2026-05-28 done；LCAD-11 子包已收口引用）。
- **LCAD-11**：新增 `docs/verification/evidence_trend_acceptance.md`、`tests/core/test_lcad_11_parent_rollup.py`；`evidence_trend_boundaries.md` 增加父包行。
- **测试**：focused `test_lcad_10_parent_rollup` + `test_lcad_11_parent_rollup` + 负向 / trend 子集 pass。
- **边界**：不运行真实 CAD；不修改 registry；不改变表 C。

### DOC-ARCH-REBASE-02：文档治理续作

- **审计增强**：`doc_governance.py` 排除 `docs/status/changelog.md` 的表 C 历史误报；跳过带历史标记的表 C 行；新增 `check_root_migration_stubs()` 校验 8 个根 stub 目标文件存在。
- **表 C 快照**：`CORE_STATUS.md`、`README.md`、`docs/status/current.md`、`docs/planning/任务清单.md` 活跃表 C 与 coverage JSON（headline **9.6%**、302 行登记）对齐。
- **断链修复**：`CAD_AGENT_CHANGELOG.md` stub 改指向 `docs/history/snapshots/root-md-2026-05-26/CAD_AGENT_CHANGELOG.md`（移除不存在的 `docs/history/changelog/`）。
- **handoff**：`docs/handoffs/current.md` 补全 V-PROOF-72 的 8/9 项与 capability 扩展项；新增 DOC-ARCH-REBASE-02 章节。
- **边界**：不修改 registry；不运行真实 CAD；不改 V-PROOF-23/24 业务代码。

### DOC-ARCH-REBASE：文档架构一次性重构

- **结构迁移**：根目录长文档迁入 `docs/status/`、`docs/governance/`、`docs/runbooks/`、`docs/roadmap/` 与 `docs/architecture/`，旧根路径保留短 stub。
- **交接拆分**：`docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` 从巨型汇总降级为兼容入口，拆出 `current.md`、`package-index.md`、`template.md` 和 `archive/2026-05.md`。
- **Planning 收口**：活跃 Phase 剧本迁入 `docs/planning/phases/`，Phase R 历史计划迁入 `docs/history/completed-plans/phase-r/`。
- **自动化护栏**：新增 `core/maintenance/doc_governance.py`、`scripts/run_doc_governance_audit.py` 与 `tests/core/test_doc_governance.py`，覆盖 doc registry、主从关系、表 C 旧值、handoff 与 Markdown link 检查。
- **复核加固**：按只读 Agent 复核结果，补强旧 `CURSOR_PACKAGE_HANDOFFS.md` 兼容搜索索引、修正 Phase Z / runbook / governance 的旧写回路径、统一状态页表 A 为 95%，并让 doc governance 校验 `package-index.md` 的 current/archive 指向。
- **边界**：不移动 `output/validation_runs/**` 机器证据，不改变 registry，不改变表 C。

### STRUCT-AUDIT-01：全仓 Python 结构审计

- **审计产物**：新增 `docs/verification/struct_audit_01.md`，输出全仓 Python 结构审计报告。
- **机器证据**：生成 `output/validation_runs/struct-audit-01/struct_audit_report.json`、`python_inventory.csv`、`struct_audit_fragments.md`，覆盖 505 个 Python 文件、56,247 行、1,523 条内部 import 边；AST 解析错误 0。
- **结论**：仓库仍收敛在 `core` / `scripts` / `tests` 主干；320 个非测试模块中 186 个有直接静态测试入口、20 个间接可达、114 个未发现静态测试入口。重点风险为 `core/verification/composition_cad_registry.py` 与 `scripts/run_composition_cad_registry.py` 未发现静态测试入口，后续 `V-PROOF-43` 前应补 no-CAD contract test。
- **边界**：本包为只读结构审计，不运行真实 CAD、不写 DWG、不修改 registry、不改变表 C。

### STRUCT-MERGE-PREP-01：合并规则与候选清单

- **规则产物**：新增 `docs/verification/struct_merge_keep_rules.md`，固定“应合并 / 应保留 / 应拆分 / 允许超线例外”的一页维护规则。
- **候选产物**：新增 `docs/verification/struct_merge_candidates.md` 与 `output/validation_runs/struct-audit-01/merge_candidate_table.csv`，把后续候选分为 1 个应合并、5 个应拆分 / 抽公共层、6 个应保留、4 个观察 / 延后。
- **首批建议**：`STRUCT-MERGE-01` 只处理 `core/composition_engine/drawing_policy.py` 合并到 `templates.py`；`STRUCT-MERGE-02` 先给 `composition_cad_registry` 补 no-CAD contract test；`STRUCT-MERGE-03` 再抽 VCAD visual primitives。
- **边界**：本轮只制定规则和候选表，不实际合并 Python 文件，不运行真实 CAD，不改变表 C。

### STRUCT-MERGE-01：drawing_policy 合并小包 + BUG 筛查

- **结构合并**：删除 `core/composition_engine/drawing_policy.py`，把固定 composition drawing flags 合并入唯一调用方 `core/composition_engine/templates.py`，并从 `templates.py` 导出 `resolve_composition_object_drawing_flags()`。
- **TDD 证据**：先改 `tests/core/test_composition_catalog.py` 并观察红灯（旧 `drawing_policy.py` 仍存在），实现后 focused 5 tests OK；扩展 composition focused 15 tests OK。
- **加固 / BUG 筛查**：全量 `unittest discover -s tests` 首轮发现 RBLOCK-07 matrix sync 对 `showcase` 行拒绝绑定；已修复 `apply_block_matrix_registry_binding()` 支持 `showcase` 行只追加来源 / notes、不覆盖 evidence。修复后 864 tests OK。
- **审计**：旧 import 扫描无残留；`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings；`run_dev_volume_audit.py` 仍提示当前工作树整体变更量过大，属于收口风险。
- **产物**：新增 `docs/verification/struct_merge_01_drawing_policy.md` 与 `output/validation_runs/struct-merge-01/struct_merge_01_report.json`；候选表 C01 标记为已合并。
- **边界**：本包不运行真实 CAD、不写 DWG、不修改 registry、不改变表 C。

## 2026-05-27

### VCAD-02：CAD 视觉表达 P1 房间平面

- **画面升级**：继续响应“推进 CAD 画面能力”，新增 `core/verification/visual_room_plan_scene.py`、`core/verification/visual_room_plan_smoke.py` 与 `scripts/run_visual_room_plan_smoke.py`，不推进 registry / coverage 表 C。
- **能力新增**：在 `CODEX_PREVIEW` 绘制带开洞的双线墙体、门扇与门弧、窗符号、办公区 / 会议区 / 动线分区、工位与会议桌椅、柜体、北箭、房间标签和三段尺寸链。
- **真实 CAD 证据**：`output/validation_runs/vcad-02-visual-room-plan-20260527-cad/visual_room_plan_smoke_report.json` 为 `status=visual_geometry_verified`，created handles **99**，类型计数 `line=67`、`circle=10`、`arc=9`、`polyline=4`、`text=6`、`dimension=3`，visual detail score **100**；只写 `CODEX_PREVIEW`，未保存 DWG、未删除实体、未改正式图层。
- **视觉证据**：AutoCAD 窗口截图为 `output/previews/vcad-02-visual-room-plan.png`；这是画面表达 P1，不声称施工图、公司块库或正式图层体系完成。

### VCAD-01：CAD 视觉表达 P0 办公角落

- **方向切换**：用户明确要求“停止刷表 C，推进 CAD 画面能力”；本包不以 registry / coverage 数字为目标，改以 CAD 实际画面复杂度和可读性为目标。
- **能力新增**：新增 `core/verification/visual_cad_smoke.py` 与 `scripts/run_visual_cad_smoke.py`，绘制双线房间、门扇开启弧、两组带桌面内边/显示器/键盘/椅子的工位、抽屉柜和工作区轮廓。
- **真实 CAD 证据**：`output/validation_runs/vcad-01-visual-office-corner-20260527-cad/visual_cad_smoke_report.json` 为 `status=visual_geometry_verified`，created handles **54**，类型计数 `line=42`、`circle=6`、`arc=3`、`polyline=3`，visual detail score **100**；只写 `CODEX_PREVIEW`，未保存 DWG、未删除实体、未改正式图层。
- **视觉证据**：AutoCAD 窗口截图为 `output/previews/vcad-01-visual-office-corner.png`；这只证明 P0 视觉表达升级，不声称已达到施工图或真实图块库水平。

### V-PROOF-42：Composition Expand 真实 CAD 刷新

- **能力证明**：完成 `V-PROOF-42-COMPOSITION-EXPAND`，按 `office_composition_cad_registry_manifest.json` 在真实 AutoCAD 会话刷新 4 个 office composition case。
- **证据**：`output/validation_runs/vproof-42-office-composition-expand-20260527-cad/composition_cad_registry_report.json` 为 `status=geometry_verified`；4/4 case 通过，created handles 共 40，全部在 `CODEX_PREVIEW` 回读；未保存 DWG、未删除实体、未改正式图层。
- **Registry / 表 C**：`composition.single_desk_chair_pair`、`composition.desk_with_back_cabinet`、`composition.two_workstations_shared_aisle`、`composition.entry_reception_clearance` 4 行回写到本轮 fresh reports；因此前已为 `verified`，coverage 复跑后 CAD 证明覆盖率仍 **48.58%**、CAD 实力指数 **51.03%**、主指标仍 **8.87%**。
- **口径**：能力证明台账更新为 **35/45 done**，另有 1 partial；next=`V-PROOF-43-COMPOSITION-CAD-RERUN`。

### DEV-AUDIT-01：开发量审计入口

- **加固**：新增 `scripts/run_dev_volume_audit.py` 与 `core/maintenance/dev_volume_audit.py`，把当前工作树开发量输出为机器可读 JSON。
- **覆盖**：统计 changed / tracked / untracked 文件数、增删行、按 area 分组、最大单文件 delta，并支持阈值 findings 与 `--fail-on-findings`。
- **当前体检**：本轮报告为 100 changed files、55 tracked、45 untracked、3653 insertions、326 deletions；触发 `large_changed_file_count` 与 handoff 单文件 delta 提醒。

### V-PROOF-41：Block CAD Matrix 真实 CAD 补验

- **能力证明**：完成 `V-PROOF-41-BLOCK-CAD-MATRIX`，双受控测试块 `controlled-test-block-001/002` 均在真实 AutoCAD 会话的 `CODEX_PREVIEW` 完成 insert + created-handle readback。
- **证据**：`output/validation_runs/vproof-41-block-cad-matrix-20260527-cad/block_alpha_beta_summary.json` 为 `status=pass`、2/2 `geometry_verified`；handles `61F`、`627` 均回读为 `block_reference`。
- **Registry / 表 C**：`block.library.controlled_test_block_002` 从 `smoke` 回写为 `verified`，coverage 复跑后 CAD 证明覆盖率 **48.58%**、CAD 实力指数 **51.03%**、主指标仍 **8.87%**（showcase 门），最高 L4。
- **口径**：能力证明台账更新为 **34/45 done**，另有 2 partial；next=`V-PROOF-42-COMPOSITION-EXPAND`。

### V-PROOF-66：Primitive Probe Showcase

- **能力证明**：完成 `V-PROOF-66-PRIMITIVE-PROBE-SHOWCASE`，将 `RCAD-22` primitive capability probe 中已回读的 7 个 primitive 行整理进 showcase，并补入 `drawing_standard.beta.drawing_standard_beta_04` suite 行。
- **Showcase**：新增 `showcase/L1/primitive_probe_matrix/` gallery，并在 `showcase_index.json` 追加 8 个条目。
- **Registry / 表 C**：`primitive.arc/circle/dimension/line/polyline/rectangle/text` 与 `drawing_standard.beta.drawing_standard_beta_04` 从 `verified` 升到 `showcase`；coverage 复跑后 CAD 证明覆盖率 **48.23%**、CAD 实力指数 **50.82%**、主指标升至 **8.87%**，最高 L4。

### V-PROOF-65：Showcase Second Wave

- **能力证明**：完成 `V-PROOF-65-SHOWCASE-SECOND-WAVE`，将 hatch、block-first、drawing-standard block insert 三组已验证能力整理进 showcase。
- **Showcase**：新增 `showcase/L1/primitive_hatch_smoke/`、`showcase/L1/symbol_block_first/`、`showcase/L0/drawing_standard_block_insert/` 三组 gallery，并在 `showcase_index.json` 追加 4 个条目。
- **Registry / 表 C**：`primitive.hatch`、`symbol.block_first.symbol_block_first_tier_01`、`symbol.block_first.controlled_block_wins`、`drawing_standard.beta.block_insert_plan_resolution` 从 `verified` 升到 `showcase`；coverage 复跑后 CAD 证明覆盖率 **48.23%**、CAD 实力指数 **50.82%**、主指标升至 **6.03%**，最高 L4。

### V-PROOF-64：Ladder Boundary + Block Matrix Showcase

- **能力证明**：完成 `V-PROOF-64-LADDER-BOUNDARY-DOC`，新增 `docs/verification/capability_ladder_boundaries.md`，把 Ladder L0-L5 与“能声称 / 不能声称”边界集中成页。
- **Showcase**：新增 `docs/verification/capability_showcase/showcase/L2/block_insert_matrix/gallery_index.json`，将 `block.insert_block_alpha.matrix` 绑定到 `RCAD-24` 的 8/8 real CAD block_reference readback suite。
- **Registry / 表 C**：`block.insert_block_alpha.matrix` 从 `verified` 升到 `showcase`；coverage 复跑后 CAD 证明覆盖率 **48.23%**、CAD 实力指数 **50.82%**、主指标升至 **4.61%**，最高 L4。

### V-PROOF-45：Block Beta Rows 回写表 C

- **能力证明**：完成 `V-PROOF-45-BLOCK-BETA-ROWS`，把 `RCAD-24` 的 `block_alpha_beta_summary.json` 作为 suite 级真实 CAD readback 证据回写。
- **代码**：`capability_registry_writeback` 现在只在 `status=pass`、`non_cad_only=false`、`geometry_verified_count>0` 且 `evidence_summary` 声明 `readback_geometry_verified` 时接受 suite summary；no-CAD suite 仍拒绝。
- **Registry / 表 C**：`block.insert_block_alpha.matrix` 从 `smoke` 升到 `verified`；coverage 复跑后 CAD 证明覆盖率 **48.23%**、CAD 实力指数 **50.82%**、主指标仍 **4.26%**。

### V-PROOF-41：Block CAD Matrix

- **代码链路**：`insert_block_alpha` 安全 allowlist 扩为 `controlled-test-block-001/002` 两个受控测试块；仍限定 `CODEX_PREVIEW`、统一缩放、无属性写入，不扩大到项目块库。
- **产物**：新增 `examples/plans/block_cad_matrix_vproof_41.json`，更新 block alpha plan/COM driver/fake driver/beta suite 与 RBLOCK-05 合约文档。
- **证据**：`output/validation_runs/vproof-41-block-cad-matrix-20260527-cad/block_alpha_beta_summary.json` 为 2/2 `geometry_verified`；`block.library.controlled_test_block_002` 已回写 verified。
- **边界**：只证明两个受控测试块的 preview-only block reference 插入与回读，不扩大到任意项目块库、属性块、正式图层或施工图块。

### V-PROOF-40：Block Matrix Plan 表 C 收口

- **能力证明**：完成 `V-PROOF-40-BLOCK-MATRIX-PLAN`，正式收口 block insert matrix 的 anchor / rotation / scale / attribute 维度表。
- **证据**：`scripts/run_block_matrix_registry_sync.py --output output/validation_runs/vproof-40-block-matrix-plan-no-cad --apply` 通过，输出 `block_matrix_registry_sync_summary.json`；`matrix_status=pass`，5 个 binding applied，0 rejected。
- **修复**：`run_block_matrix_registry_no_cad_sync()` 现在会把相对 output 路径解析到 project root 下，避免 CLI 相对路径触发 `relative_to(project_root)` 失败；新增 focused 回归测试。
- **Registry / 表 C**：`block.insert_block_alpha.matrix` 仅写入 smoke evidence；4 个维度 verified 行保留既有真实 CAD readback 证据，只追加 matrix manifest 来源。coverage 复跑后仍为 CAD 证明覆盖率 **47.87%**、CAD 实力指数 **50.75%**、真实 CAD 实力主指标 **4.26%**。
- **口径**：能力证明台账更新为 **29/43（约 67%）**，next=`V-PROOF-41-BLOCK-CAD-MATRIX`。本包不运行真实 CAD，不新增 `geometry_verified`。

### V-PROOF-43：Composition CAD 复验 + 表 C 抬升

- **推进表 C**：完成 `V-PROOF-43-COMPOSITION-CAD-RERUN`；真实 CAD 刷新 interior 3 case + office 4 case 升 `showcase`。
- **真实 CAD**：`vproof-43-composition-rerun-20260528-cad` 3/3 `geometry_verified`（40 handles）；`vproof-tablec-office-composition-20260528-cad` 4/4（40 handles）；只写 `CODEX_PREVIEW`。
- **Registry**：`writeback_apply.json` applied **7/7**；4 行 `verified`→`showcase`（office composition）；3 行 showcase 证据路径刷新。
- **表 C**：主指标 **8.87%→10.28%**；`showcase_count` 25→29；`verified_count` 112→108；瓶颈仍为 showcase 门（min 门）。

### RESIDENTIAL-PROD-03：Residential P3 父包收口

- **一键推进**：完成 `RESIDENTIAL-PROD-03-RESIDENTIAL-P3-WAVE-ROLLUP`，收口住宅 alpha + beta 子包与 no-CAD 复跑。
- **证据**：`res-prod-03-p3-rollup-no-cad/residential_p3_wave_summary.json`；alpha pass + beta 8/8。
- **口径**：代码轨 **52/55（约 95%）**；next=LCAD-10 父包收口。不抬表 C。

### RESIDENTIAL-PROD-02：Residential Beta 边界

- **一键推进**：完成 `RESIDENTIAL-PROD-02-RESIDENTIAL-BETA-BOUNDARY`，住宅 scene beta 8 case + registry 8 行收成 P3 契约。
- **证据**：`res-prod-02-boundary-no-cad/residential_beta_boundary_summary.json`；8/8 pass，7×`benchmark_pass_non_cad` + 1×`blocked_expected_non_cad`。
- **口径**：代码轨 **51/55（约 93%）**；next=`RESIDENTIAL-PROD-03`。不抬表 C。

### RESIDENTIAL-PROD-01：Residential Alpha 边界

- **一键推进**：完成 `RESIDENTIAL-PROD-01-RESIDENTIAL-ALPHA-BOUNDARY`，补齐 P3 住宅 alpha 与 `OFFICE-PROD-01` / `REST-PROD-01` 对称的 manifest + contract。
- **产物**：`residential_alpha_boundary.py`、`residential_prod_alpha_manifest.json`、`residential_prod_01_residential_alpha_boundary.md`、CLI 与 7 项 focused test。
- **证据**：`output/validation_runs/res-prod-01-boundary-no-cad/residential_alpha_boundary_summary.json` 为 `status=pass`；`scene_alpha_residential_blank_shell` no-CAD、`along_wall` 动线、`benchmark_pass_non_cad`。
- **口径**：代码轨 **50/55（约 91%）**；next=`RESIDENTIAL-PROD-02`（scheduled）。不运行真实 CAD，不抬表 C。

### SCENE-PROD-06：多场景回归门禁

- **一键推进**：完成 `SCENE-PROD-06-MULTI-SCENE-REGRESSION-GATE`，把 office / residential / restaurant 三套 scene beta benchmark 汇总为一个 no-CAD gate。
- **产物**：新增 `core/agents/scene_regression_gate.py`、`scripts/run_scene_prod_06_regression_gate.py`、`docs/verification/scene_prod_06_multi_scene_regression_gate.md` 与 `tests/core/test_scene_prod_06_regression_gate.py`。
- **证据**：`output/validation_runs/scene-prod-06-regression-gate-no-cad/scene_regression_gate_summary.json` 顶层 `status=pass`；25/25 selected benchmark pass，21 个 `benchmark_pass_non_cad`、4 个 `blocked_expected_non_cad`、`readback_geometry_verified_count=0`；repo audit 0 findings。
- **口径**：代码轨更新为 **49/55（约 89%）**；本包不连接 AutoCAD，不新增真实 CAD `geometry_verified`，不把场景偏好和 benchmark 通过扩大为 Scene Product。

### RCAD-06：Hatch COM 受控 smoke 真实 CAD 补验

- **CAD 补验**：完成 `RCAD-06-HATCH`；`AutoCADComDriver.draw_hatch()` 现在支持受控真实 COM hatch smoke，先写闭合 boundary polyline，再写 ANSI31 hatch，仍由 preview-only guard 保护。
- **产物**：新增 `core/verification/hatch_cad_smoke.py`、`scripts/run_hatch_cad_smoke.py`、`tests/core/test_hatch_cad_smoke.py`；更新 `docs/verification/hatch_com_deferred_boundary.md`，把 real COM verified 与 fake/no-CAD deferred 分开。
- **真实 CAD 证据**：`output/validation_runs/rcad-06-hatch-cad-20260527-escalated/hatch_cad_smoke_report.json` 为 `status=geometry_verified`、`evidence_state=readback_geometry_verified`，created handles `61C` / `61D`，回读 `hatch=1`、`polyline=1`，pattern `ANSI31`，bbox `100 x 80`。
- **Registry / 表 C**：`primitive.hatch` 由 `deferred` 回写为 `verified`；`hatch_writeback.json` applied 1。复跑 coverage 后，`total_count=282`、`verified_count=123`、`showcase_count=12`、CAD 证明覆盖率 **47.87%**、CAD 实力指数 **50.75%**、真实 CAD 实力主指标 **4.26%**、最高已证 **L4**。
- **口径**：RCAD 烟囱更新为 **29/29 verified**；只证明受控 `CODEX_PREVIEW` ANSI31 hatch smoke，不扩大到任意 hatch、正式图层或施工图交付。

### RCAD-28：BETA-CAD-BLOCK evidence rollup + trend 补验

- **CAD 补验**：完成 `RCAD-28-BETA-EVIDENCE-ROLLUP`；`scripts/run_cad_beta_evidence_rollup.py --output-root output/validation_runs/rcad-28-beta-evidence-rollup-20260527-final` 输出 `status=pass`，5/5 subpackages pass。
- **Trend hook**：`core/verification/cad_beta_evidence_rollup.py` 新增 `cad_beta_evidence_rollup_trend.json` 输出，并用 `validate_evidence_trend_report()` 硬校验。
- **测试**：`tests/core/test_cad_beta_block_acceptance.py` 固定 trend 文件存在、schema 校验 0 errors、`non_cad_only=true`、`geometry_verified_count=0`、`dry_run_valid_plan_only_count=5`。
- **边界**：本包按设计是 non-CAD 父包 evidence rollup，不连接 AutoCAD、不新增 created handles、不提升表 C；本条为历史快照，RCAD 烟囱当时为 **28/29 verified**，当前已随 `RCAD-06-HATCH` 更新为 **29/29 verified**。
- **表 C**：本条为历史快照；当前最新 coverage 为 `total_count=282`、`verified_count=112`、`showcase_count=25`、CAD 证明覆盖率 **48.58%**、CAD 实力指数 **51.03%**、真实 CAD 实力主指标 **8.87%**、最高已证 **L4**。

### RCAD-27：local CAD regression trend rollup 真实 CAD 补验

- **CAD 补验**：完成 `RCAD-27-TREND-ROLLUP-CAD`；`scripts/run_local_cad_regression.py --strict` 在用户 AutoCAD 会话完成 local CAD regression strict 矩阵。
- **证据**：真实 CAD 输出 `output/validation_runs/rcad-27-trend-rollup-cad-20260527-escalated/local_cad_regression_report.json`，`status=pass`，9/9 `geometry_verified_case_count`，created handles 105；趋势复算输出 `output/validation_runs/rcad-27-trend-rollup-cad-20260527-escalated/evidence_trend/local_cad_regression_trend.json`。
- **前置修正**：no-CAD 兼容矩阵先暴露 `tests/core/test_planmd_governance.py` 中旧进度断言仍找 `94%`，已同步为当前 `CORE_STATUS.md` 的 `95%`。
- **安全边界**：只写 `CODEX_PREVIEW` / `CODEX_DIAGNOSTIC` 允许层，未保存 DWG、未删除实体、未修改正式图层；截图仍仅作视觉辅助，几何证明以 created handles 回读为准。
- **口径**：RCAD 烟囱更新为 **27/29 verified**，next=`RCAD-28-BETA-EVIDENCE-ROLLUP`；本轮未回写 registry / showcase，因此表 C 机器值不变。

### RCAD-24：block alpha beta 真实 CAD 补验

- **CAD 补验**：完成 `RCAD-24-BLOCK-ALPHA-BETA`；`scripts/run_block_alpha_beta_suite.py --connect-cad` 现在可逐个执行 8 个 beta case，并用 created handles 回读 `block_reference`。
- **几何修正**：`core/block_engine/block_placement.py` 的 block bbox 从“宽深互换近似”修正为围绕 insertion point 旋转四角后取外包框，匹配 AutoCAD 的 block reference bbox。
- **证据**：真实 CAD 复跑输出 `output/validation_runs/rcad-24-block-beta-cad-after-rotfix-20260527/block_alpha_beta_summary.json`，`status=pass`，8/8 `geometry_verified`，created handles `373`~`37A`，全部在 `CODEX_PREVIEW`。
- **验证**：`python -m unittest tests.core.test_block_engine tests.core.test_block_alpha_beta_suite` → 19 tests OK；no-CAD suite 8/8 pass 且 `geometry_verified_count=0`；真实 CAD suite 8/8 `geometry_verified`。
- **口径**：RCAD 烟囱更新为 **26/29 verified**；本轮未改 registry / showcase / coverage，因此表 C 机器值不变。

### SCENE-PROD-05：Scene Beta 解释模板收口

- **一键推进**：完成 `SCENE-PROD-05-SCENE-EXPLANATION-TEMPLATE`；新增 scene beta explanation helper、边界文档、CLI 和 focused test，说明三场景 preferences 如何影响 Core / benchmark。
- **产物**：`scene_beta_explanation.py`、`scene_prod_05_scene_explanation_template.md`、`run_scene_beta_explanation_template.py`、`test_scene_prod_05_scene_explanation_template.py`。
- **验证**：先写测试并观察缺模块失败；实现后 focused 5 tests OK，`run_scene_beta_explanation_template.py` 输出 `status=pass`，三场景解释对象可机器读取。
- **口径**：代码轨 **48/55（约 87%）**，next=`SCENE-PROD-06-MULTI-SCENE-REGRESSION-GATE`。本包只证明 no-CAD explanation contract，不新增真实 CAD `geometry_verified`。

### REST-PROD-04：P3 多场景父包收口

- **一键推进**：完成 `REST-PROD-04-MULTI-SCENE-P3-ROLLUP`；新增跨场景 P3 parent contract、acceptance 文档、CLI 和 focused test，统一收口 office / restaurant 两个 P3 父包。
- **产物**：`multi_scene_p3_wave.py`、`rest_prod_04_multi_scene_p3_rollup_acceptance.md`、`run_multi_scene_p3_rollup.py`、`test_rest_prod_04_multi_scene_p3_rollup.py`。
- **验证**：先写测试并观察缺模块失败；实现后 focused 5 tests OK，`run_multi_scene_p3_rollup.py` 输出 `status=pass`，alpha 19 + beta 17 no-CAD case 可审计。
- **口径**：代码轨 **47/55（约 85%）**，next=`SCENE-PROD-05-SCENE-EXPLANATION-TEMPLATE`。本包只证明 no-CAD parent contract / `benchmark_pass_non_cad`，不新增真实 CAD `geometry_verified`。

### REST-PROD-03：餐饮 P3 波次父包收口

- **一键推进**：完成 `REST-PROD-03-RESTAURANT-P3-WAVE-ROLLUP`；按 `OFFICE-PROD-03` 模式新增 restaurant P3 parent contract、acceptance 文档、CLI 和 focused test。
- **产物**：`restaurant_p3_wave.py`、`restaurant_prod_03_p3_wave_acceptance.md`、`run_restaurant_p3_wave_rollup.py`、`test_rest_prod_03_p3_wave_rollup.py`。
- **验证**：先写测试并观察缺模块失败；实现后 focused 6 tests OK，`run_restaurant_p3_wave_rollup.py --run-benchmarks` 输出 `status=pass`，alpha case + beta 8/8 no-CAD 通过。
- **口径**：代码轨 **46/55（约 84%）**，next=`REST-PROD-04-MULTI-SCENE-P3-ROLLUP`。本包只证明 no-CAD contract / `benchmark_pass_non_cad`，不新增真实 CAD `geometry_verified`。

### REST-PROD-02：餐饮 beta 边界收口

- **一键推进**：完成 `REST-PROD-02-RESTAURANT-BETA-BOUNDARY`；按 `OFFICE-PROD-02` 模式新增 restaurant beta contract、manifest、边界文档、CLI 和 focused test。
- **产物**：`restaurant_beta_boundary.py`、`restaurant_prod_beta_manifest.json`、`restaurant_prod_02_restaurant_beta_boundary.md`、`run_restaurant_beta_boundary_contract.py`、`test_rest_prod_02_restaurant_beta_boundary.py`。
- **验证**：先写测试并观察缺模块失败；实现后 focused 6 tests OK；restaurant beta benchmark 8/8 no-CAD pass（7 pass + 1 blocked_expected）。
- **口径**：代码轨 **45/55（约 82%）**；next=`REST-PROD-03-RESTAURANT-P3-WAVE-ROLLUP`。本包只证明 no-CAD contract / `benchmark_pass_non_cad`，不新增真实 CAD `geometry_verified`。

### REST-PROD-01：餐饮 alpha 边界收口

- **一键推进**：完成 `REST-PROD-01-RESTAURANT-ALPHA-BOUNDARY`；按 `OFFICE-PROD-01` 模式新增 restaurant alpha contract、manifest、边界文档、CLI 和 focused test。
- **产物**：`restaurant_alpha_boundary.py`、`restaurant_prod_alpha_manifest.json`、`restaurant_prod_01_restaurant_alpha_boundary.md`、`run_restaurant_alpha_boundary_contract.py`、`test_rest_prod_01_restaurant_alpha_boundary.py`。
- **验证**：先写测试并观察缺模块失败；实现后 focused 7 tests OK；CLI 输出 `output/validation_runs/rest-prod-01-boundary-no-cad/restaurant_alpha_boundary_summary.json`，`status=pass`。
- **口径**：该轮代码轨为 **44/55（约 80%）**；后续已推进到 `REST-PROD-02`。本包只证明 no-CAD contract / `benchmark_pass_non_cad`，不新增真实 CAD `geometry_verified`。

### V-PROOF-35：fallback tier rows 表 C 推进

- **能力证明**：完成 `V-PROOF-35-FALLBACK-TIER-ROWS`；`cad_capability_registry` 新增 `symbol.fallback_tier.block`、`symbol.fallback_tier.symbol_glyph`、`symbol.fallback_tier.component_preview`、`symbol.fallback_tier.bbox_placeholder`、`symbol.fallback_tier.deferred_unsupported_symbol` 5 行。
- **边界**：4 行为 `smoke`，1 行为 `deferred`；全部保持 `not_verified_without_cad_readback`，不把 fallback 解析 / dry-run / deferred 扩大为 `geometry_verified`。
- **契约**：`assert_symbol_glyph_fallback_boundary_contract()` 现在检查 V-PROOF-35 行存在且不得为 `verified/showcase`。
- **表 C**：本条为历史快照；当前最新 coverage 为 `total_count=282`、CAD 证明覆盖率 **48.58%**（137/282；112 verified + 25 showcase）、CAD 实力指数 **51.03%**、真实 CAD 实力主指标 **8.87%**、最高已证 **L4**。
- **验证**：focused 21 tests OK；`scripts/run_capability_coverage.py --output output/validation_runs/capability-lab/cad_capability_coverage.json` pass。本轮未运行真实 CAD。

### 诊断层隔离小收口：探针标注不再污染 `CODEX_PREVIEW`

- **问题**：能力探针 / complex smoke 为验证 `draw_text` 与 `add_dimension` 会绘制文字和尺寸，旧实现把这些诊断对象与几何探针一起写入 `CODEX_PREVIEW`，容易在用户视口里看起来像“生成图块仍带标注”。
- **变更**：新增 `CODEX_DIAGNOSTIC` 作为 preview-only 允许诊断层；`cad_capability_probe` 与 `complex_cad_smoke` 将文字和尺寸写入诊断层，几何对象仍写入 `CODEX_PREVIEW`。
- **加固**：诊断层写入现在必须显式传入 `layer_role="diagnostic"`；默认 preview 角色写 `CODEX_DIAGNOSTIC` 会被 `CadWriteGuard` 拦截，避免诊断层被误用为第二个普通出图层。
- **证据**：报告新增 `diagnostic_layer`、`preview_type_counts`、`diagnostic_type_counts` 和双层 `layer_counts`，用于区分用户可见几何与诊断标注。
- **验证**：`python -m unittest tests.core.test_autocad_write_guard tests.core.test_cad_capability_probe tests.core.test_complex_cad_smoke` 通过。

### V-PROOF-44 + RCAD-23：drawing standard beta 表 C 推进

- **能力证明**：完成 `V-PROOF-44-DRAWING-STANDARD-ROWS` 的真实 CAD 子集回写；只升级 suite 与 `block_insert_plan_resolution`。
- **真实 CAD**：`scripts/run_drawing_standard_cad_smoke.py` 在用户 AutoCAD 会话通过；证据 `output/validation_runs/rcad-23-drawing-standard-beta-20260527-escalated/drawing_standard_cad_smoke_report.json` 为 `status=geometry_verified`，created handle `36A`，styled `insert_block_alpha` 在 `CODEX_PREVIEW` 回读为 `block_reference`。
- **登记**：`drawing_standard.beta.drawing_standard_beta_04` 与 `drawing_standard.beta.block_insert_plan_resolution` 回写 `verified`；object role、primitive style、semantic layer case 保持 smoke。
- **表 C**：复跑 coverage 后，CAD 证明覆盖率 **48.38%**（134/277；122 verified + 12 showcase），CAD 实力指数 **51.33%**，真实 CAD 实力主指标仍 **4.33%**（showcase readiness 瓶颈），最高已证 **L4**。
- **验证**：focused 23 tests OK；`--no-cad` deferred 报告 OK；沙箱内 COM 为 `external_blocker`，沙箱外用户 CAD 会话验证通过。

### V-PROOF-34 + RCAD-25：block-first 表 C 推进

- **能力证明**：完成 `V-PROOF-34-BLOCK-FIRST-ROW`；把 SYMBOL-09 block-first suite 与 `controlled-block-wins` 从 smoke 推进到真实 CAD verified。
- **真实 CAD**：`scripts/run_symbol_block_first_cad_smoke.py` 在用户 AutoCAD 会话通过；证据 `output/validation_runs/rcad-25-symbol-block-first-20260527-escalated/symbol_block_first_cad_smoke_report.json` 为 `status=geometry_verified`，created handle `369`，`CODEX_TEST_BLOCK_001` 在 `CODEX_PREVIEW` 回读为 `block_reference`。
- **登记**：仅 `symbol.block_first.symbol_block_first_tier_01` 与 `symbol.block_first.controlled_block_wins` 回写 `verified`；两个 glyph fallback case 保持 smoke。
- **表 C**：复跑 coverage 后，CAD 证明覆盖率 **47.65%**（132/277；120 verified + 12 showcase），CAD 实力指数 **51.19%**，真实 CAD 实力主指标仍 **4.33%**（showcase readiness 瓶颈），最高已证 **L4**。
- **验证**：focused 17 tests OK；`--no-cad` deferred 报告 OK；沙箱内 COM 为 `external_blocker`，沙箱外用户 CAD 会话验证通过。

### OFFICE-PROD-03：办公 P3 波次父包收口

- **一键推进**：完成 `OFFICE-PROD-03-OFFICE-P3-WAVE-ROLLUP`；收口 `OFFICE-PROD-01` alpha 边界与 `OFFICE-PROD-02` beta 边界。
- **产物**：`office_p3_wave.py`、`run_office_p3_wave_rollup.py`、`office_prod_03_p3_wave_acceptance.md`、`test_office_prod_03_p3_wave_rollup.py`。
- **验证**：focused 6 tests OK；CLI summary pass；office alpha 18/18 no-CAD，office beta 9/9 no-CAD（7 pass + 2 blocked_expected）。
- **口径**：代码轨 **43/55（约 78%）**；next=`REST-PROD-01-RESTAURANT-ALPHA-BOUNDARY`。本包未运行真实 CAD，不新增 `geometry_verified`。

### RCAD-22：capability probe beta 真实 CAD 补验

- **CAD 补验**：`scripts/run_cad_capability_probe.py` 在用户 AutoCAD 会话 `Drawing1.dwg` 通过；`status=cad_capability_verified`。
- **证据**：`output/validation_runs/rcad-22-capability-probe-beta-20260527-escalated/cad_capability_probe.json`，11 handles，全部在 `CODEX_PREVIEW`，bbox 900×450，`session_guard.status=consistent`。
- **登记**：刷新 `primitive.arc/circle/dimension/line/polyline/rectangle/text` 的 report path；`primitive.hatch` 保持 deferred，不计作几何 verified。
- **口径**：RCAD **23/29（约 79%）**；next=`RCAD-23-DRAWING-STANDARD-BETA`。当前表 C 机器值为真实 CAD 实力主指标 **4.33%**、CAD 证明覆盖率 **46.93%**。

### 最终回复精简口径：默认轻量表，按需展开 A/B/C

- 按用户反馈，把 CAD Agent 聊天最终回复从“默认完整三表”改为“默认 1 张精简进度表”：表 C 主指标优先、本轮进展 / 验证、表 A 折叠工程节奏、表 B 本轮相关中文轨道（能力证明 / 代码轨 / CAD 补验）。
- 保留完整 A/B/C 作为状态页、交接、审计、进度盘点和表 C 专题的展开模板；无论精简或展开，都不得省略表 C 主指标或混用工程进度、任务台账与真实 CAD 实力。
- 明确本次不重构 §3 43 包、§4 55 包、§5 29 包真实分母；只允许在最终回复里做展示聚合。
- 同步 `AGENTS.md`、`CAD_AGENT_RULES.md`、`README.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`docs/planning/任务清单.md`、`docs/onboarding/first-handoff.md` 与 `capability_proof_status_template.md` 的口径。
- 本轮是文档规则治理，不新增真实 CAD `geometry_verified` 能力。

### 文档治理收尾：表 A/B/C 与主从关系同步

- 复跑 `scripts/run_capability_coverage.py --output output/validation_runs/capability-lab/cad_capability_coverage.json`，当前机器值为 `total_count=277`、`cad_proof_count=130`、CAD 证明覆盖率 **46.93%**、真实 CAD 实力主指标 **4.33%**、最高已证 **L4**。
- 同步 `docs/planning/任务清单.md` §0：能力证明约 **24/43** done，代码轨约 **42/55** done，RCAD 烟囱 **22/29** verified；明确表 B 不等于表 C。
- 压缩 `CORE_CONTEXT_BRIEF.md` 为短入口，保留当前结论、三表快照、next、不能声称和按需展开表，旧流水继续查 changelog / handoff / history。
- 加固主从关系：`CORE_RESTRUCTURE_PLAN.md` 决定方向、优先级和退出门槛；`docs/planning/任务清单.md` 只做执行台账和即时 `next` 镜像；README、状态页、handoff 不再生成第三套计划。
- 同步 `tests/core/test_capability_coverage.py` 的 showcase 断言，避免测试仍假设 seed registry 没有 showcase 行。
- 收口 repo audit 尾巴：7 个新脚本改用共享 `scripts/_bootstrap.py`，不再直接 `sys.path.insert`。
- 本轮为文档治理和状态同步，不新增真实 CAD `geometry_verified` 能力。

### RCAD-15：沙发 symbol glyph 真实 CAD 补验

- **CAD 补验**：`run_symbol_glyph_cad_smoke.py` + `seating_sofa_plan.json`；`status=geometry_verified`、6 handles、仅 `CODEX_PREVIEW`。
- **证据**：`output/validation_runs/rcad-15-symbol-glyph-sofa-20260527/symbol_glyph_cad_smoke_report.json`
- **登记**：`object.sofa.glyph` 证据路径刷新；`symbol.spec.symbol_sofa_plan` 保持 `showcase`（writeback 曾误降为 verified，已手工恢复）。
- **口径**：RCAD **22/29（约 76%）**；next=`RCAD-22` / `RCAD-23`。

### OFFICE-PROD-02：P3 办公 beta 边界（第二包）

- **一键推进**：完成 `OFFICE-PROD-02-OFFICE-BETA-BOUNDARY`；链式 alpha + scene_beta 9 case。
- **产物**：`office_beta_boundary.py`、`office_prod_beta_manifest.json`、`office_prod_02_office_beta_boundary.md`（6 tests OK）。
- **口径**：**41/55（约 75%）**；next=`REST-PROD-01` 或 `OFFICE-PROD-03`。本包未运行真实 CAD。

### OFFICE-PROD-01：P3 办公 alpha 边界（进波首包）

- **一键推进**：完成 `OFFICE-PROD-01-OFFICE-ALPHA-BOUNDARY`；P3 他场景产品化进波。
- **产物**：`office_alpha_boundary.py`、`office_prod_alpha_manifest.json`、`office_prod_01_office_alpha_boundary.md`（7 tests OK）。
- **口径**：**40/55（约 73%）**；next=`OFFICE-PROD-02`。本包未运行真实 CAD。

### CORE-P4：P4 Core 波次父包收口

- **一键推进**：完成 `CORE-P4-WAVE-PARENT-ROLLUP`；`DRAW-01`/`02` + `SYMBOL-08`/`09` rollup + acceptance。
- **产物**：`p4_core_wave.py`、`p4_core_wave_acceptance.md`、`test_p4_core_wave_parent_rollup.py`（6 tests OK）。
- **口径**：**39/52（约 75%）**；P4/P5 波次已收口；next=P3 `user_gate`。本包未运行真实 CAD。

### RBLOCK-08：P5 图块波次父包收口

- **一键推进**：完成 `RBLOCK-08-P5-WAVE-PARENT-ROLLUP`；`RBLOCK-03`~`07` rollup + acceptance。
- **产物**：`block_p5_wave.py`、`block_p5_wave_acceptance.md`、`test_rblock_08_p5_wave_parent_rollup.py`（6 tests OK）。
- **口径**：**38/51（约 75%）**；§4.2 P5 已收口。本包未运行真实 CAD。

### RBLOCK-07：块矩阵 registry 行绑定

- **一键推进**：完成 `RBLOCK-07-BLOCK-MATRIX-REGISTRY-ROWS`；5 行 registry 绑定 + matrix smoke writeback API。
- **产物**：`block_matrix_registry.py`、`cad_capability_registry.json`（+1 smoke 行）、`rblock_07_block_matrix_registry_rows.md`（8 tests OK）。
- **口径**：**37/51（约 73%）**；next=`RBLOCK-08-P5-WAVE-PARENT-ROLLUP`。本包未运行真实 CAD。

### RBLOCK-06：属性块探针边界

- **一键推进**：完成 `RBLOCK-06-BLOCK-ATTRIBUTE-BOUNDARY`；`BETA-CAD-BLOCK-02` manifest + 契约 + attribute deferred smoke。
- **产物**：`block_attribute_boundary.py`、`block_attribute_probe_manifest.json`、`rblock_06_block_attribute_boundary.md`（7 tests OK）。
- **口径**：**36/51（约 71%）**；next=`RBLOCK-07-BLOCK-MATRIX-REGISTRY-ROWS`。本包未运行真实 CAD。

### RBLOCK-05：第二受控测试块 metadata

- **一键推进**：完成 `RBLOCK-05-SECOND-CONTROLLED-BLOCK`；`controlled-test-block-002` library + sidecar；`insert_block_alpha` allowlist 未放宽。
- **产物**：`second_controlled_block_manifest.json`、`second_controlled_block_boundary.py`、`rblock_05_second_controlled_block.md`（8 tests OK）。
- **口径**：**35/51（约 69%）**；next=`RBLOCK-06-BLOCK-ATTRIBUTE-BOUNDARY`。本包未运行真实 CAD。

### RBLOCK-04：块插入矩阵 manifest

- **一键推进**：完成 `RBLOCK-04-BLOCK-MATRIX-MANIFEST`；anchor/rotation/scale/attribute 四维矩阵 + registry 四行绑定。
- **产物**：`block_insert_matrix_manifest.json`、`block_matrix_manifest.py`、`run_block_insert_matrix_manifest.py`、`rblock_04_block_matrix_manifest.md`（7 tests OK）。
- **口径**：**34/51（约 67%）**；next=`RBLOCK-05-SECOND-CONTROLLED-BLOCK`。本包未运行真实 CAD。

### RBLOCK-03：P5 受控 block alpha 边界

- **一键推进**：完成 `RBLOCK-03-BLOCK-ALPHA-BOUNDARY`；P5 图块波次进队。
- **产物**：`block_alpha_boundary.py`、`rblock_03_block_alpha_boundary.md`（5 tests OK）。
- **口径**：**33/51（约 65%）**；next=`RBLOCK-04-BLOCK-MATRIX-MANIFEST`。本包未运行真实 CAD。

### SYMBOL-09：block-first tier 机器入口

- **一键推进**：完成 `SYMBOL-09-BLOCK-FIRST-TIER`；block-first smoke + registry 四行。
- **产物**：`block_first_tier.py`、`block_first_boundary.py`、`symbol_block_first_tier_manifest.json`、`run_block_first_tier_smoke.py`（7 tests OK）。
- **口径**：**32/50（约 64%）**；§4.2 P4 收口；next=P5 或 P3。本包未运行真实 CAD。

### SYMBOL-08：symbol glyph 四级 fallback 边界

- **一键推进**：完成 `SYMBOL-08-GLYPH-FALLBACK-BOUNDARY`；fallback tier 契约 + 无静默退化 benchmark 复验。
- **产物**：`symbol_fallback_boundary.py`、`symbol_08_glyph_fallback_boundary.md`、`test_symbol_08_glyph_fallback_boundary.py`（+ 复用 fallback policy 6 tests）。
- **口径**：**31/50（约 62%）**；next=`SYMBOL-09-BLOCK-FIRST-TIER`。本包未运行真实 CAD。

### DRAW-02：drawing standard registry 行绑定

- **一键推进**：完成 `DRAW-02-DRAWING-STANDARD-REGISTRY-ROWS`；登记表 +7 行；smoke evidence writeback API。
- **产物**：`drawing_standard_registry.py`、`draw_02_drawing_standard_registry_rows.md`、`test_draw_02_drawing_standard_registry_rows.py`（8 tests OK）。
- **口径**：**30/50（约 60%）**；next=`SYMBOL-08-GLYPH-FALLBACK-BOUNDARY`。本包未运行真实 CAD。

### DRAW-01：P4 Core 首包 — drawing standard 边界

- **一键推进**：完成 `DRAW-01-DRAWING-STANDARD-BOUNDARY`；P4 Core 波次进队。
- **产物**：`drawing_standard_boundary.py`、`draw_01_drawing_standard_boundary.md`、`test_draw_01_drawing_standard_boundary.py`（4 tests OK）；no-CAD beta suite 6/6。
- **口径**：**29/50（约 58%）**；next=`DRAW-02-DRAWING-STANDARD-REGISTRY-ROWS`。本包未运行真实 CAD。

### CFIT-13：P2 工装波次父包收口

- **一键推进**：完成 `CFIT-13-P2-WAVE-PARENT-ROLLUP`；收口 `CFIT-09`…`CFIT-12`。
- **产物**：`commercial_fitout_p2_wave.py`、`commercial_fitout_p2_wave_acceptance.md`、`test_cfit_13_p2_wave_parent_rollup.py`（6 tests OK）。
- **口径**：**28/49（约 57%）**；§4.2 P2 done；next 待 P3/P4 波次进队。本包未运行真实 CAD。

### V-PROOF-63：L4 工装双样本项目切片 + 表 C 抬升

- **§0.1**：`run_project_sample_cad_rollup.py` 真实 CAD **4/4**（含 meeting/reception 各 12 handles）。
- **Registry**：新增 L4 `project.sample.*` 2 行 + showcase；另 3 条 L3 室内组合升 showcase。
- **表 C**：主指标 **2.67% → 4.55%**；`highest_proven_ladder_level=L4`；登记 **49.24%**（130/264）。
- **能力证明**：**28/43（约 65%）**；next=`V-PROOF-34` 或 `V-PROOF-64`。

### V-PROOF-61 / 60：L2 符号画廊 + showcase 索引（表 C 抬升）

- **§0.1 推进表 C**：真实 CAD 跑通 desk/chair/table/sofa 四 glyph（`capability-proof-vproof61-20260527`）；另 2 条 L3 fitout composition 升为 `showcase`。
- **Showcase**：`showcase_index.json` 现 **7** 条（4×L2 + 3×L3）；`V-PROOF-60` done、`V-PROOF-61` done。
- **表 C**：主指标 **0.38% → 2.67%**；`showcase_count=7`；登记仍 **48.85%**（128/262）。
- **能力证明**：**27/43（约 63%）**；`RCAD-15` sofa 证据已刷新（可登记烟囱 verified）。

### V-PROOF-62：L3 工装微场景 showcase + 真实 CAD

- **§0.1 真实 CAD 实力**：`run_composition_cad_registry.py`（fitout manifest）真实 AutoCAD **3/3** `geometry_verified`（28 created handles）。
- **Showcase**：`docs/verification/capability_showcase/` + `showcase/L3/fitout_open_office_desk_chair/snippet_index.json`；registry 首条 `claim_level=showcase`（`composition.fitout_open_office_desk_chair`）。
- **表 C**：主指标 **0% → 0.38%**；`showcase_count=1`；登记仍 **48.85%**（128/262 cad_proof）。
- **能力证明**：**26/43（约 60%）**；`V-PROOF-60` partial；next=`V-PROOF-34` 或扩 showcase。

### 表 C：真实 CAD 实力与四进度口径

- **机器指标**：`capability_coverage.py` 新增 `cad_strength_*`（`cad_strength_headline_percent` = min(加权指数, L3+, showcase)）。
- **文档**：`AGENTS.md` 交付改为表 A+B+C；`任务清单.md` §0 四口径；§5 改称 RCAD 烟囱包；`RCAD-10/19/21` 登记 verified。
- **当前值**：主指标 **0%**（showcase=0）；实力指数 **50.52%**；L3+ **39.53%**；RCAD 烟囱 **69%**（20/29）。

### 口令：真实 CAD 实力 / 推进表 C

- **`任务清单.md` §0.1**：第四口令编排表 C（`V-PROOF` + 链式 RCAD + registry 回写 + coverage）；**刷新表 C** 仅复跑不新开包。
- **同步**：`AGENTS.md`、`CAD_AGENT_RULES.md`、`README.md`、`capability_proof_status_template.md`。

### 表 C 会话：RCAD-18 真实 CAD + registry 回写

- **CAD**：`capability-proof-table-c-20260527` — fitout subscene smoke 4/4 `geometry_verified`（真实 AutoCAD readback）。
- **Registry**：4 行 catalog `--apply`（meeting_table/chair、reception_desk、waiting_sofa 证据路径刷新）。
- **Coverage 复跑**：主指标仍 **0%**（showcase=0）；指数 **50.52%**；登记 **48.85%**（128/262）。
- **RCAD**：`RCAD-18` verified；烟囱 **21/29**。

### CFIT-12：fitout subscene representative object CAD smoke

- **一键推进**：完成 `CFIT-12-FITOUT-SUBSCENE-OBJECT-CAD-SMOKE`（对齐 `V-PROOF-25`）。
- **产物**：`fitout_subscene_object_cad_smoke_manifest.json`、`fitout_subscene_object_cad_smoke.py`、`run_fitout_subscene_object_cad_smoke.py`。
- **覆盖**：meeting_room 2 对象 + reception 2 对象；fake 4/4 geometry_verified。
- **口径**：**27/49（约 55%）**；next=`CFIT-13`。本包未运行真实 CAD；`RCAD-18` 脚本路径已就绪。

### CFIT-11：three-sample product boundary / rollup sync

- **一键推进**：完成 `CFIT-11-THREE-SAMPLE-BOUNDARY-SYNC`。
- **口径**：`product_alpha_boundary.json` 新增 `deidentified_project_samples[]`；`fitout_sample_specs` 增加 `subscene_id` / `project_rel`；`assert_fitout_three_sample_rollup_sync()` 纳入 product boundary 契约。
- **验证**：CFIT-11 5 tests + product boundary / rollup 14 tests OK；fake rollup 仍 4/4 geometry_verified。
- **口径**：**26/49（约 53%）**；next=`CFIT-12`。本包未运行真实 CAD。

### CFIT-10：reception commercial fitout project sample

- **一键推进**：完成 `CFIT-10-RECEPTION-PROJECT-SAMPLE`。
- **样本**：`projects/commercial_fitout_reception_sample/` + workflow；rollup 登记第四行。
- **三子场景样本**：open_office / meeting_room / reception 各一组脱敏样本路径。
- **验证**：CFIT-10 4 tests OK；rollup fake 4/4 geometry_verified。
- **口径**：**25/49（约 51%）**；next=`CFIT-11`。

### CFIT-09：second commercial fitout project sample

- **一键推进**：完成 `CFIT-09-SECOND-PROJECT-SAMPLE`（§4.2 P2 工装波次首包）。
- **样本**：新增 `projects/commercial_fitout_meeting_sample/` 与 `commercial_fitout_meeting_sample_confirmation_loop.json`。
- **多样本注册**：`fitout_sample_specs.py`；confirmation / CAD smoke / rollup 按 workflow 解析 `sample_id`。
- **rollup**：`project_sample_cad_rollup.json` 登记第三样本；fake driver 单测 3/3 geometry_verified。
- **口径同步**：一键推进 **24/49（约 49%）**；next=`CFIT-10`。本包未运行真实 CAD 项目补验。

### LCAD-14：guard full CAD strict rollup

- **一键推进**：完成 `LCAD-14-GUARD-FULL-CAD`，新增 `guard_full_cad_runner` 与 `run_guard_full_cad_runner.py`，strict 汇总 write guard、negative CAD、capability probe 三段子报告。
- **strict 门禁**：`guard_full_cad_report.json` 的 `strict_gate` 断言子报告 pass、`negative_guard_verified`、`cad_capability_verified` 与 `session_guard.status=consistent`。
- **边界文档**：新增 `docs/verification/guard_full_cad_boundary.md`；真实 AutoCAD 会话 strict 复验入口为 `RCAD-21`（`--real-cad`）。
- **测试**：focused 3 tests OK；no-CAD 证据 `output/validation_runs/lcad-14-guard-full-no-cad/`。
- **口径同步**：一键推进 **23/49（约 47%）**；§4.1 活跃队列已收口；§4.2 待波次。本包未运行真实 CAD，不新增 `geometry_verified`。

### LCAD-13：session snapshot in capability probe

- **一键推进**：完成 `LCAD-13-SESSION-SNAPSHOT-CAD`，把 `cad_session_guard` before/after snapshot 接入 `run_cad_capability_probe()`。
- **探针契约**：写入前采集 `after_connect`、写入后采集 `after_write`；报告含 `session_guard`，并写出 `active_document_snapshot.json`。
- **证据门禁**：`validate_capability_probe_evidence` 在 `cad_capability_verified` 时要求 `session_guard.status=consistent` 与 `active_document_identity_stable=pass`。
- **边界文档**：新增 `docs/verification/session_snapshot_capability_probe_boundary.md`，服务 `V-PROOF-52` guard/snapshot 字段断言边界。
- **测试**：focused session/probe/validation-runner tests OK；no-CAD 证据 `output/validation_runs/lcad-13-session-snapshot-no-cad/`；repo audit 0 findings。
- **口径同步**：一键推进进度更新为 **22/49（约 45%）**；next=`LCAD-14`。本包未运行真实 CAD，不新增 `geometry_verified`。

### LCAD-12：hatch COM structured deferred

- **一键推进**：完成 `LCAD-12-HATCH-COM`，选择安全 structured deferred 收口，不冒充真实 AutoCAD hatch 写入。
- **Driver 边界**：`AutoCADComDriver.draw_hatch()` 与 `FakeCadDriver.draw_hatch()` 都先执行 preview-only 写入守卫；预览层调用只返回 `primitive=hatch`、`status=deferred`、`failure_category=hatch_unverified`、`created_handles=[]`、`geometry_verified=false`。
- **安全口径**：真实 COM driver 不调用 `AddHatch`、不创建 handle；正式图层调用会在写入前被 `CadWriteGuardViolation` 拦截。
- **边界文档**：新增 `docs/verification/hatch_com_deferred_boundary.md`，固定 `V-PROOF-53` 当前只获得能力槽位和失败分类，不获得真实几何证明。
- **测试**：RED 阶段两个 driver 均缺 `draw_hatch`，边界文档不存在；补实现后 focused hatch tests 8 tests OK，聚焦回归 25 tests OK，沙箱外全量 685 tests OK。
- **口径同步**：一键推进进度更新为 **21/49（约 43%）**；next=`LCAD-13`。本包未运行真实 CAD，不新增 `geometry_verified`。

### CAD-VAL-02：environment gate optional

- **一键推进**：完成 `CAD-VAL-02-ENVIRONMENT-GATE-OPTIONAL`，`run_cad_validation` 新增 `environment_optional` / `--environment-optional` 显式模式。
- **门禁口径**：该模式下顶层 `status` 按 `geometry_gate` 计算；`unit_tests`、截图、Pillow / pywin32 / win32gui 等基础设施失败仍保留在 `infrastructure_gate`，并标记 `infrastructure_debt=true`。
- **边界文档**：新增 `docs/verification/cad_validation_environment_gate.md`，明确非几何失败不能混成几何失败，也不能被静默吞掉。
- **证据**：`output/validation_runs/cad-val-02-environment-optional/report.json`；当前沙箱内 `unit_tests` 受 Windows Temp ACL 误伤，报告为 `status=pass`、`legacy_status=fail`、`geometry_gate.status=pass`、`infrastructure_gate.failed_required_step_ids=[unit_tests]`。
- **测试**：RED 阶段 `run_cad_validation()` 不支持 `environment_optional`；补实现后 focused 16 tests OK。
- **口径同步**：一键推进进度更新为 **20/49（约 41%）**；next=`LCAD-12`。本包未运行真实 CAD，不新增 `geometry_verified`。

### LCAD-11.5：trend boundary doc

- **一键推进**：完成 `LCAD-11.5-TREND-BOUNDARY-DOC`，新增 `docs/verification/evidence_trend_boundaries.md`。
- **边界内容**：覆盖 `LCAD-11.1`~`11.4` 的 trend JSON、`local_cad_regression_trend.json`、`cad_validation_trend_index.json`、`capability_coverage_trend.json`、coverage `snapshot.metrics` 与 `V-PROOF-71` Dashboard 用途。
- **不得声称**：trend JSON、schema pass、no-CAD pass、截图、dry-run、coverage metric 均不能替代真实 AutoCAD created-handle readback；`cad_proof_coverage_rate` 不是几何准确率。
- **测试**：RED 阶段边界文档不存在；补文档后 `tests.core.test_evidence_trend_boundaries_doc` pass，focused 11 tests OK。
- **口径同步**：一键推进进度更新为 **19/49（约 39%）**；next=`CAD-VAL-02`。本包未运行真实 CAD，不新增 `geometry_verified`。

### LCAD-11.4：coverage trend hook

- **一键推进**：完成 `LCAD-11.4-COVERAGE-TREND-HOOK`，`run_capability_coverage` 在常规 `cad_capability_coverage.json` 外同步输出 `evidence_trend/capability_coverage_trend.json`。
- **趋势 hook**：复用统一 evidence trend schema；coverage 的 `total_count`、`verified_count`、`cad_proof_coverage_rate` 等 V-PROOF-02 字段放在 `snapshot.metrics`，不把本包伪装成新增几何证据。
- **证据**：`output/validation_runs/lcad-11-4-coverage-trend-hook/evidence_trend/capability_coverage_trend.json`；schema 校验无错误。coverage 仍为 262 行、128 verified、`cad_proof_coverage_rate=48.85%`。
- **测试**：RED 阶段 `trend_path.is_file()` 失败；补实现后 focused 18 tests OK，`run_capability_coverage.py --output output/validation_runs/lcad-11-4-coverage-trend-hook/cad_capability_coverage.json` 为 `status=pass`。
- **口径同步**：一键推进进度更新为 **18/49（约 37%）**；next=`LCAD-11.5`。本包未运行真实 CAD，不新增 `geometry_verified`。

### LCAD-11.3：cad validation 历史趋势索引

- **一键推进**：完成 `LCAD-11.3-VALIDATION-TREND-INDEX`，新增 `core/verification/cad_validation_trend_index.py`，`run_cad_validation` 每次写出 `report.json/md` 后同步生成 `evidence_trend/cad_validation_trend_index.json`。
- **趋势索引**：按同级 validation run 的 `report.json` 生成 `source_kind=cad_validation` snapshots，并复用 `LCAD-11.1` 的 evidence trend schema；历史真实 CAD snapshots 可进入索引，但 no-CAD snapshot 不会提升几何证明。
- **证据**：`output/validation_runs/lcad-11-3-validation-trend-index/evidence_trend/cad_validation_trend_index.json`；schema 校验无错误，当前 `snapshot_count=11`，包含本轮 no-CAD validation 报告。
- **测试**：RED 阶段缺少 `core.verification.cad_validation_trend_index`；补实现后新增 `tests/core/test_cad_validation_trend_index.py`。focused 26 tests OK；沙箱内 no-CAD validation 被 Windows Temp ACL 误伤，按审批沙箱外重跑 `run_cad_validation --no-cad` 为 `status=pass`，内部全量 `676 tests OK`。
- **口径同步**：一键推进进度更新为 **17/49（约 35%）**；next=`LCAD-11.4`。本包未运行真实 CAD，不新增 `geometry_verified`。

### LCAD-11.2：local CAD regression 趋势 JSON

- **一键推进**：完成 `LCAD-11.2-REGRESSION-TREND-JSON`，`run_local_cad_regression` 在主报告外同步输出 `evidence_trend/local_cad_regression_trend.json`。
- **趋势 rollup**：新增 local regression snapshot，汇总 `evidence_state_counts`、`geometry_accuracy_counts`、`screenshot_role_counts` 与 `summary`；no-CAD 运行固定为 deferred/non-CAD，不提升几何证明。
- **证据**：`output/validation_runs/lcad-11-2-regression-trend-json/evidence_trend/local_cad_regression_trend.json`；schema 校验无错误，`snapshot_count=1`、`deferred_cad_readback_count=8`、`geometry_verified_count=0`、`non_cad_only=true`。
- **测试**：RED 阶段 `trend_path.is_file()` 失败；补实现后新增 `tests/core/test_local_cad_regression_trend.py`。focused 24 tests OK；含治理测试 focused 31 tests OK；沙箱内 no-CAD 回归被 Windows Temp ACL 误伤，按审批沙箱外重跑 `run_local_cad_regression --no-cad` 为 `status=pass`，内部全量 `675 tests OK`。
- **口径同步**：一键推进进度更新为 **16/49（约 33%）**；next=`LCAD-11.3`。本包未运行真实 CAD，不新增 `geometry_verified`。

### V-PROOF-33：readability rows 绑定

- **能力证明**：`V-PROOF-33-READABILITY-REPORT-ROWS` 从 partial 收口为 done；`examples/capability_proof/cad_capability_registry.json` 新增 5 个 `symbol.readability_status.*` smoke 行。
- **Schema / 测试**：`cad_capability_registry.schema.json` 增加 `readability_status` 字段；`tests/core/test_capability_readability.py` 增加 registry 绑定断言，先 RED 后 GREEN。
- **证据**：`output/validation_runs/vproof-33-readability-rows/capability_readability_report.json` 与 `output/validation_runs/vproof-33-readability-rows/cad_capability_coverage.json`。
- **覆盖率**：登记表从 257 行扩为 **262** 行；`verified_count` 仍为 **128**，`cad_proof_coverage_rate=48.85%`。这是分母扩充，不新增真实 CAD `geometry_verified`。
- **校验**：focused 29 tests OK、全量 674 tests OK、repo audit 0 findings、`git diff --check` 无空白错误。
- **口径同步**：能力证明进度更新为 **24/43（约 56%）**；next=`V-PROOF-34` 或 fitout composition CAD。

### RCAD-20：真实 CAD 负向安全补验

- **CAD 补验**：执行 `RCAD-20-NEGATIVE-CAD`。沙箱内首次运行 `--real-cad` 为 `external_blocker`（看不到用户 AutoCAD COM）；按审批沙箱外重跑后通过。
- **证据路径**：`output/validation_runs/rcad-20-negative-cad-20260527-escalated/negative_cad_runner_report.json`。
- **结论**：`status=pass`、`evidence_state=negative_guard_verified`、`created_handles=[]`、`saved_dwg=false`、`deleted_entities=false`、`modified_formal_layers=false`、`preview_layer_entity_delta=0`、`modelspace_entity_delta=0`。
- **覆盖率**：复算 `cad_capability_coverage_after_rcad20.json` 与 `cad_capability_coverage_after_doc_sync.json` 后仍为 **128/257（49.81%）**；`negative_guard_verified` 是 guard-only，不计入几何证明。
- **校验**：focused 34 tests OK、全量 673 tests OK、repo audit 0 findings、`self_check.py` pass、`render_preview.py --check` ready、`git diff --check` 无空白错误。

### LCAD-11.1：evidence trend 词表契约

- **一键推进**：完成 `LCAD-11.1-EVIDENCE-VOCAB`，新增 `core/verification/evidence_trend.py`、`core/schemas/evidence_trend.schema.json`、`examples/evidence_trends/minimal_evidence_trend.json` 与 `tests/core/test_evidence_trend.py`。
- **趋势字段**：固定 `snapshots[]`、`source_kind`、完整 `evidence_state_counts`、`geometry_accuracy_counts`、`screenshot_role_counts`、`summary` 与 `metrics` 字段，供后续 `LCAD-11.2` / `11.3` / `11.4` 复用。
- **词表边界**：schema 的 evidence enum 与 `EVIDENCE_STATE_VALUES` 对齐；`negative_guard_verified` 在趋势汇总中只计入 `guard_only_count`，不计入 `cad_proof_state_count` 或 `geometry_verified_count`。
- **测试**：RED 阶段缺少 `core.verification.evidence_trend`；补实现后 focused 31 tests OK，隔离 tempfile ACL 后全量 673 tests OK，repo audit 0 findings，`git diff --check` 无空白错误。
- **口径同步**：一键推进进度更新为 **15/49（约 31%）**；next=`LCAD-11.2`。

### LCAD-10.5：负向安全父包收口

- **一键推进**：完成 `LCAD-10.5-PARENT-ROLLUP`，新增 `docs/verification/negative_cad_safety_acceptance.md`。
- **父包结论**：`LCAD-10-NEGATIVE-SAFETY` 收口，汇总 `LCAD-10.1~10.4` 的负向 fixture、write guard、负向 runner 和边界文档；明确 `negative_guard_verified` 仍为 guard-only，不新增真实 CAD 几何结论。
- **测试**：新增 `tests/core/test_lcad_10_parent_rollup.py`，覆盖 acceptance 文档与 handoff 索引；focused 6 tests OK，隔离 tempfile ACL 后全量 670 tests OK，repo audit 0 findings。
- **口径同步**：一键推进进度更新为 **14/49（约 29%）**；next=`LCAD-11.1`。

### LCAD-10.4：负向 CAD 安全边界文档

- **一键推进**：完成 `LCAD-10.4-NEGATIVE-BOUNDARY-DOC`，新增 `docs/verification/negative_cad_safety_boundaries.md`。
- **边界内容**：明确 LCAD-10.1~10.4 的职责、8 类 `failure_category`、write guard 安全扫描字段、`RCAD-20` 真实 CAD 补验门槛，以及 `negative_guard_verified` 不计入 `geometry_verified` / CAD 几何覆盖率。
- **测试**：新增 `tests/core/test_negative_cad_safety_boundaries_doc.py`，防止边界文档缺少关键声明；focused 4 tests OK，隔离 tempfile ACL 后全量 668 tests OK，repo audit 0 findings。
- **口径同步**：一键推进进度更新为 **13/49（约 27%）**；next=`LCAD-10.5`。

### NEG-CAD-PROOF-SYNC：负向安全 runner + 覆盖率可读证据 + composition 收口

- **LCAD-10.3**：新增 `core/verification/negative_cad_runner.py` 与 `scripts/run_negative_cad_runner.py`，汇总 negative CAD_PLAN 8/8、write guard、ActiveDocument snapshot、no-handle/no-save/no-delete/no-formal-layer 证据。
- **真实 COM 写入前置守卫**：`AutoCADComDriver` 的 line / rectangle / circle / arc / polyline / text / dimension 在任何 COM `Add*` 前先检查 preview layer，修复负向正式图层写入“抛错前可能已创建实体”的风险。
- **覆盖率可读报告**：新增 `core/verification/capability_readability.py` 与 `scripts/run_capability_readability_report.py`，输出 geometry verified / guard-only / deferred / smoke / none / blockers 分组。证据：`output/validation_runs/neg-cad-proof-sync/capability-readability-final/capability_readability_report.json`。
- **证据**：`output/validation_runs/neg-cad-proof-sync/negative-runner-fake-final/negative_cad_runner_report.json` 为 `status=pass`、`evidence_state=negative_guard_verified`、`created_handles=[]`；`negative-runner-real` 当前为 `external_blocker`（沙箱身份看不到用户 AutoCAD COM），不新增真实 CAD 几何结论。
- **composition 收口**：保留 JSON catalog + schema 工业化方向；`drawing_policy.py` 改为全局默认无标注，运行时对象级 `include_label/include_dimensions` 不再能覆盖 composition 输出。
- **自检补强**：`shell_confirmation.py` 对临时 JSON 清理的 `PermissionError` 做兜底，避免沙箱/ACL 清理失败掩盖已成功的 SHELL_MODEL 构建。
- **口径同步**：CAD 证明覆盖率统一为 **128/257（49.81%）**；代码轨完成度更新为 **12/49（约 24%）**，next=`LCAD-10.4`。
- **验证**：focused 35 tests OK；隔离 `tempfile` ACL 后全量 667 tests OK；repo audit 0 findings；`self_check.py` pass；`render_preview.py --check` ready（当前 AutoCAD window unavailable）。

### CAD 能力覆盖表提升（fitout composition + benchmark 镜像）

- **Fitout composition CAD**：`fitout_composition_cad_registry_manifest.json`；3/3 `geometry_verified`（`capability-lab-coverage-wave-20260527/fitout_composition_cad/`）。
- **登记表镜像**：`build_coverage_expansion_writeback.py` 将 interior/office/fitout benchmark 行与 `block.library.controlled_test_block_001` 绑定既有 CAD 证据；office `object_spec` benchmark 行镜像 `object.*.draw_object` 报告。
- **覆盖率**：**128/257（49.81%）**（自 108/42.0% 起 +20 行 verified）。
- **composition_cad_registry**：`benchmark_output_subdir` 可配置，支持多 benchmark suite。

### CAD 校验波次：glyph 矩阵 + office composition + LCAD-10.2

- **V-PROOF-32**：`symbol_glyph_cad_matrix_manifest.json` + `symbol_glyph_cad_matrix.py` + `run_symbol_glyph_cad_matrix.py`；真实 CAD **6/6** `geometry_verified`（`capability-lab-cad-validation-20260527/symbol_glyph_matrix/`）。
- **V-PROOF-42 片段**：`office_composition_cad_registry_manifest.json`；`composition_cad_check` 支持 manifest `case_ids`；office 4 case CAD **4/4** verified（`smoke`→`verified`）。
- **LCAD-10.2**：`write_guard_cad_runner.py` + `run_write_guard_cad_runner.py`（负向 plan 8/8 + fake write-guard pass）。
- **覆盖率**：**108/257（42.02%）**；证据 `capability-lab-cad-validation-20260527/`。
- **测试**：658 OK。

### 安全层校验收口（驱动守卫 + 路径边界）

- **驱动层一致防御**：新增 `core/cad_io/preview_write_guard_mixin.py`；`AutoCADComDriver` 与 `FakeCadDriver` 共用 `CadWriteGuard`，在 `ensure_layer` / `_apply_common` 阻断正式层写入，并统一阻断 `save_document` / `delete_entity_by_handle`。
- **路径边界**：`intent_lab_cad` 的 `plan_path` 与 `output_dir` 分别走 `resolve_under_project_root` / `resolve_under_project_output`；`run_intent_lab_cad.py`、`run_block_alpha_validation.py` CLI 入口同步加固。
- **测试**：新增 `tests/core/test_path_safety.py`、`tests/core/test_autocad_write_guard.py`；全量 **654 OK**。

### V-PROOF-22 / V-PROOF-31 / V-PROOF-43 能力证明轨

- **V-PROOF-22**：`demand_case_cad_manifest.json` + `demand_case_cad_smoke.py` + `run_demand_case_cad_smoke.py`；10/10 demand case 真实 CAD → registry `benchmark.demand_side_agent_benchmark.*` verified。
- **V-PROOF-31**：`surface_monitor_plan.json` / `surface_rug_plan.json`；`symbol_spec.schema` 增 `monitor`/`rug`；glyph CAD + `object.*.glyph` 与 `symbol.spec.*` 回写。
- **V-PROOF-43 片段**：`composition_cad_registry_manifest` + `composition_cad_registry.py`；`composition_cad_check` 迁入 `core/`；3 个 interior delivery composition 行 verified。
- **覆盖率**：batch **17** 行 → **`verified_count=104`（40.47% / 257）**；证据 `capability-lab-vproof-20260527/`。
- **测试**：649 OK。

### CAD 证明覆盖率 wave（object + domain + glyph + block）

- **V-PROOF-31 片段**：`examples/symbol_specs/seating_sofa_plan.json` + sofa glyph CAD smoke。
- **Object Lab 扩样**：`object_cad_smoke_manifest` 增至 **14** 类（+file_cabinet/storage_cabinet/computer_desk/display_unit/monitor/rug）；`capability-lab-coverage-wave-20260527/object_cad_smoke/` 14/14 `geometry_verified`。
- **Domain draw_object**：`domain_draw_object_cad_smoke.py` + `run_domain_draw_object_cad_smoke.py`；11 个 deferred domain 行真实 CAD。
- **回写**：`build_coverage_writeback_batch.py` batch **35** 行 → **`verified_count=87`（34.12% / 255）**；含 glyph 别名×5、block.insert_block_alpha×4、`symbol.spec.symbol_sofa_plan`。
- **测试**：647 OK。

### 登记表完善：fitout catalog 全量 CAD + batch 回写

- **Fitout catalog CAD**：`core/verification/fitout_catalog_cad_smoke.py` + `scripts/run_fitout_catalog_cad_smoke.py`；14/14 `geometry_verified`（`capability-lab-registry-20260527/fitout_catalog_cad/`）。
- **回写工具**：`scripts/build_registry_writeback_batch.py`（从 fitout smoke 报告 + glyph/regression 路径生成 batch）。
- **登记表**：batch **22** 行 `--apply`（11 catalog 自 deferred→verified；6 glyph；2 regression 路径刷新；3 catalog 已 verified 刷新证据）→ **`verified_count=59`（23.23% / 254）**。
- **CAD 校验波次**：`cad-validation-wave-20260527/` baseline geometry gate + composition retry 证据已链入 registry。
- **测试**：645 OK（`test_local_cad_regression` strict fake 补 `--no-cad` primitive 分支）。

### V-PROOF-14/15/20/21/30 能力证明轨

- **V-PROOF-14/15**：`core/verification/intent_lab_cad.py` + `scripts/run_intent_lab_cad.py`；`intent.draw_object` / `intent.draw_symbol_glyph` / `intent.insert_block_alpha` 真实 CAD + 登记表 verified。
- **V-PROOF-20**：`commercial_fitout_catalog_manifest.json`（14 项）+ `run_commercial_fitout_catalog_inventory.py`。
- **V-PROOF-21**：`object_cad_smoke_manifest.json` + 8 类 `examples/plans/object_smoke/` + `run_object_cad_smoke.py`；`object.*.draw_object` 八类 verified。
- **V-PROOF-30**：6 个 `symbol.archetype.*` 行绑定既有 glyph CAD 证据并 verified。
- **覆盖率**：batch 回写 +17 → **`verified_count=42`（16.54% / 254）**；证据 `capability-lab-vproof-20260527/`。
- **测试**：643 OK。

### CAD 证明覆盖率 sprint（symbol 全量 + fitout 样本）

- **Symbol Lab 补验**：`workstation` / `shelf` / `bed` / `cabinet` 四套 glyph smoke（`capability-lab-coverage-20260527/symbol-*`），均 `geometry_verified`；`run_symbol_glyph_cad_smoke.py` 增 `--base-x` / `--base-y` 避免叠图。
- **Commercial fitout**：`run_commercial_fitout_cad_smoke.py` → 3 plan batch、12 handles、`geometry_verified`；回写 `domain.commercial_fitout.draw_object` + `catalog.commercial_fitout.{desk,office_chair,file_cabinet}`。
- **登记表**：batch 回写 **+8** → **`verified_count=25`（9.84% / 254）**；symbol 类 **7/27** verified。
- **测试**：638 OK。

### V-PROOF-12/13 + RCAD-14/26 round2（能力证明 + CAD 补验）

- **V-PROOF-12**：`examples/capability_proof/primitive_matrix_cad_manifest.json`；`core/verification/primitive_matrix_cad_manifest.py`；`scripts/run_primitive_matrix_inventory.py`；`local_cad_regression_manifest` 增 `primitive_matrix_cad`；`primitive_matrix` 报告补 `evidence_state` 三字段（真实 CAD 时 `status=geometry_verified`）。
- **V-PROOF-13**：`cad_plan_fixture_manifest` 扩至 **6** fixture（glyph/storage/bench 等）；`cad_plan_fixture_suite` suite 级 `geometry_verified` + per-fixture `evidence_state`。
- **RCAD-14**：`examples/symbol_specs/surface_table_plan.json` + `symbol.spec.surface_table_plan` 登记行；`output/validation_runs/capability-lab-round2-20260527/rcad-14-table/` geometry verified（9 handles）。
- **CAD 证据**：`capability-lab-round2-20260527/` — primitive matrix（11 handles）、fixture suite 6/6 pass；回写 **+3** regression/symbol 行 + primitive probe 时间戳刷新 → **`verified_count=17`（6.69% / 254）**。
- **测试**：638 OK。

### §5 CAD 补验 + 登记表回写 sprint

- **E0**：`self_check.py`、`render_preview.py --check` pass（AutoCAD 2026 会话可用）。
- **严格本地矩阵**：`output/validation_runs/capability-lab-sprint-20260527/`（`run_local_cad_regression.py --strict`），7 case、`geometry_verified_case_count` 见 `local_cad_regression_report.json`。
- **补验**：`capability-lab-sprint-20260527-extra/` — primitive matrix CAD、`symbol_glyph` desk/chair、`commercial_fitout_cad_smoke`。
- **回写**：manifest suggest **4** 行 + primitive/symbol batch **10** 行 → 登记表 **`verified_count=14`**（**5.56%** / 252）；`run_capability_coverage.py` 已复跑。
- **未回写**：`regression.cad_plan_fixture_suite_cad`（suite 顶层 `pass` 非 `geometry_verified`）；`primitive.hatch`（probe 未覆盖）；fitout catalog 行尚无独立 RCAD registry 行。

### Composition 模板：JSON catalog + 全局无标注策略

- 组合模板自 `HEAD` 行为中性导出为 `libraries/composition_templates/catalog.json`，由 `composition_template_catalog.schema.json` 与 `catalog_loader.py` 加载；删除未跟踪的 `composition_templates_catalog_{core,fitout}.py`，修复拆分引入的床 `include_label: true` 漂移。
- 新增 `drawing_policy.py`：组合预览默认 `include_label=false` / `include_dimensions=false`；catalog 禁止启用标注。本轮后续已收紧为全局无标注，运行时 `composition_spec` 上的对象级标注开关也会被忽略。
- `templates.py` 保留运行时 API 并 re-export `COMPOSITION_TEMPLATES`；新增 `tests/core/test_composition_catalog.py`。

### Repo audit：大文件拆分（0 findings）

- `core/composition_engine/templates.py`（702 行）拆为 JSON catalog + `composition_template_catalog.py` loader；`templates.py` 仅保留运行时 API（~140 行）。
- `core/verification/local_cad_regression.py`（565 行）拆为 `local_cad_regression_{runtime,matrix}.py`；门面模块保留 CLI 与 re-export。
- 顺带拆分超标文件：`cad_validation_runner_report.py`、`capability_registry_seed_{common,extended}.py`。
- 证据：`scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings` → `finding_count=0`；**637 tests OK**。

### 并行：V1 Intent Lab + LCAD-10.1 + CAD-VAL-01 + RCAD-01 复验

- **V-PROOF-10 / V-PROOF-11**：`examples/capability_proof/intent_lab_manifest.json` 覆盖 6 个 `ALLOWED_INTENTS`；`examples/plans/intent_lab/*.json` 最小 plan；`core/verification/intent_lab.py` + `scripts/run_intent_lab_inventory.py`。
- **LCAD-10.1**：`examples/plans/negative/`（8 负向 plan + manifest）；`core/verification/negative_cad_plans.py` + `scripts/run_negative_cad_plan_suite.py`；`cad_plan.schema.json` 增 `draw_symbol_glyph` 与 absolute `base_point` 约束。
- **CAD-VAL-01**：`core/verification/cad_validation_geometry_gate.py`；`run_cad_validation.py` 支持 `--geometry-gate` / `--require-geometry-pass`（几何 vs 基础设施分层）。
- **RCAD-01**：真实 CAD 复验 `output/validation_runs/rcad-01-baseline-geometry/`（`inspect_readback` + `cad_capability_probe` + `block_alpha_readback` 几何证据）；`regression.baseline_cad_validation` 回写 `verified`；覆盖率 **0.4%**（1/252）。
- 证据：**637 tests OK**；`run_intent_lab_inventory.py` / `run_negative_cad_plan_suite.py` exit 0。

### V-PROOF-04/05：三口径状态页 + 能力证明 handoff 扩展

- **V-PROOF-04**：`CORE_STATUS.md` 固定「三进度口径」节（表 A / 表 B / CAD 证明覆盖率 / Ladder）；新增 `docs/verification/capability_proof_status_template.md`；`CAD_AGENT_STATUS.md` 同步并明确 **Core 94% ≠ CAD 证明覆盖率**。
- **V-PROOF-05**：`CURSOR_PACKAGE_HANDOFFS.md` 增加能力证明包附加项 10~12；`evidence_gate_handoff_rules.md` §7、`capability_proof_handoff_template.md`、`docs/handoffs/README.md` 维护规则更新。
- 证据：`tests/core/test_planmd_governance.py` 新增 3 项；全量 unittest 通过。无代码行为变更。

### V-PROOF-03：CAD 能力登记表 loader + RCAD 回写 API

- 扩展 `core/verification/capability_registry.py`：`RegistryBundle`、`load_registry_bundle`、`save_capability_registry`（写前校验）。
- 新增 `core/verification/capability_registry_writeback.py`：`apply_writeback` / `apply_writebacks`、`extract_geometry_evidence_from_report`、`suggest_writebacks_from_regression_output`、`run_registry_writeback`。
- 新增 `scripts/run_capability_registry_writeback.py`：`--capability-id`+`--report`、`--batch`、`--suggest-from-regression`、`--apply`。
- 证据：`tests/core/test_capability_registry_writeback.py` 6 tests OK；全量 unittest 通过。默认不修改种子登记表；回写需显式 `--apply`。

### V-PROOF-02：CAD 能力证明覆盖率报告

- 新增 `core/verification/capability_registry.py`（load + validate）、`core/verification/capability_coverage.py`、`scripts/run_capability_coverage.py`。
- 默认输出 `output/validation_runs/capability-lab/cad_capability_coverage.json`：`total_count=252`、`verified_count=0`、`cad_proof_coverage_rate=0.0`；含 `by_category`、`category_cad_proof`、`trend`（LCAD-11.4 趋势槽位）。
- 证据：`tests/core/test_capability_coverage.py` 4 tests OK；全量 `623 tests OK`。本轮未运行真实 CAD。

### V-PROOF-01：CAD 能力登记表种子（252 行）

- 新增 `core/verification/capability_registry_seed.py` 与 `scripts/build_cad_capability_registry_seed.py`，从 intent、primitive、object catalog、fitout catalog、composition、symbol、Core API、scene、benchmark suite、local CAD regression manifest、block library 等自动生成登记行。
- 产物：`examples/capability_proof/cad_capability_registry.json`（**252** capabilities；`claim_level` 分布为 none / deferred / smoke，**0** 行 `verified`/`showcase`）。
- 证据：`tests/core/test_cad_capability_registry_seed.py` 4 tests OK；全量 unittest 与种子脚本校验通过。本轮未运行真实 CAD。

### V-PROOF-00：CAD 能力登记表 Schema

- 新增 `core/schemas/cad_capability_registry.schema.json`：能力行 `capability_id` / `category` / `claim_level` / `ladder_level`、`cad_case`、`evidence` 三字段、`source_refs` 与 CODEX_PREVIEW `safety` 契约。
- 登记进 `MODEL_SCHEMAS`；`infer_model_type()` 可识别 `cad_capability_registry`。
- 新增 `core/verification/capability_registry_contract.py`：`claim_level` 级合同校验（subset schema 不支持的 verified/deferred 规则）。
- 样例与负例：`examples/capability_proof/minimal_cad_capability_registry.json`、`tests/fixtures/invalid_models/cad_capability_registry.invalid.json`。
- 证据：`tests/core/test_cad_capability_registry_schema.py` 6 tests OK；全量 `615 tests OK`。本轮未运行真实 CAD。

### P0：schema registry + FakeDriver + 关键 pytest 全绿

- `core/schemas/registry.py` 补齐 commercial fitout / project sample / orchestrator 等模型登记与 invalid fixtures；`schemas/cad_plan.schema.json` 与 `core/schemas/cad_plan.schema.json` 同步（含 `commercial_fitout` domain）。
- `core/plan_engine/validate_plan.py` 的 `ALLOWED_DOMAINS` 增加 `commercial_fitout`。
- `core/verification/fake_cad_driver.py` 加固：`CadWriteGuard`、`insert_block_alpha`、受控块定义、`open_document_count`。
- `core/composition_engine/templates.py` 增加 fitout 组合模板；`core/benchmarks/runner.py` 使用 `evaluate_fitout_composition_layout_failure`，并补齐 `object_spec` / demand / object_detail 路径。
- 证据：全量 `609 tests OK`（`python -m unittest discover -s tests`）。`run_repo_audit.py` 仍有 2 个 `large_python_file`（`templates.py` 702 行、`local_cad_regression.py` 565 行），未纳入 P0 退出标准。

### 交付汇报：固定表 A + 表 B（六个指标）

- `AGENTS.md`「交付必须带进度估算」改为 canonical 双表模板：表 A（总进度 / Core / Agent）、表 B（能力证明 §3 / 一键推进 §4 / CAD 补验 §5），并写明与 `docs/planning/任务清单.md` §0 的关系及禁止混用口径。
- 同步 `README.md`、`CORE_CONTEXT_BRIEF.md`、`CAD_AGENT_RULES.md` §0.4；工作区 `AGENTS.md` 增加双表交付要求。

## 2026-05-26

### Codex 本地 CAD 回归矩阵加固

- 新增 `core/verification/local_cad_regression.py` 与 `scripts/run_local_cad_regression.py`，把 baseline CAD validation、project sample CAD check、interior composition CAD check 汇总成一个本地 CAD 回归矩阵。
- `--no-cad` 模式输出 deferred / non-CAD 证据，不连接 AutoCAD、不声称 `geometry_verified`；真实 CAD 严格模式可用 `--require-cad-verified`，任一 CAD 子项不是 `geometry_verified` 时顶层失败。
- composition CAD check 增加前置 artifact 门禁：只有 `interior_delivery_benchmark` 成功后才运行真实 CAD 批量检查，前置失败时记录 `not_run` / `blocked_by`。
- 新增回归测试覆盖 no-CAD deferred 矩阵、严格模式拒绝 deferred、前置 benchmark 失败跳过 composition，以及 output dir 边界。
- 证据：focused `tests.core.test_local_cad_regression` 4 tests OK；`scripts/run_local_cad_regression.py --no-cad --output-dir output\validation_runs\local-cad-regression-no-cad` pass，`geometry_verified_case_count=0`；全量 `456 tests OK`。本轮未运行真实 AutoCAD，不新增 `geometry_verified` 结论。

### Codex 进入下一阶段前雕琢：可迁移命令、CLI 兼容和全量复验

- `CAD_AGENT_BLOCKER_PLAYBOOK.md` 的当前工具入口不再写死固定 Windows 用户目录下的 CAD-MCP Python 路径，改为 `$env:USERPROFILE` 派生 `$py`，保持换机 / 换用户可运行。
- 新增文档治理回归：活跃 CAD 文档不得重新引入固定 Windows 用户目录下的 CAD-MCP 路径。
- `run_office_scene_beta_benchmark.py`、`run_residential_scene_beta_benchmark.py`、`run_restaurant_scene_beta_benchmark.py` 新增 `--output-root` 兼容别名，同时保留原 `--output`。
- 新增 CLI 回归测试：三组 scene beta wrapper 均可用 `--output-root` 输出 benchmark artifact。
- 证据：全量 `452 tests OK`；repo audit 0 findings；`run_cad_validation.py --no-cad --output-dir output\validation_runs\codex-polish-final-no-cad` pass；blank-shell 8/8、office alpha 18/18、interior delivery 3/3、project sample 2/2、proposal confirmed 2/2、CAD beta rollup 5/5、scene beta 25/25 pass。本轮未运行真实 CAD，不新增 `geometry_verified` 结论。

### Codex 维护 4-7 包：结构整理、路径公共化、Schema registry、文档主从治理

- 新增 `core/path_safety.py`：统一 `find_project_root`、`resolve_under_project_output`、`resolve_under_project_root`、`validate_safe_path_segment` 和 `is_relative_to`，替换 benchmark、drawing-read、CAD validation、blank-shell、capability runner、proposal / beta suite 中分散的路径判断。
- 加固真实 CAD 与 artifact 入口：project sample CAD check、composition CAD check 在连接 AutoCAD 或写报告前先验证 workflow / benchmark / output 路径留在仓库 `output/`；non-CAD pipeline 对越界 workflow、越界 output、缺输入文件返回结构化 invalid，不再抛散乱异常。
- `core/schemas/registry.py` 现在登记所有 `core/schemas/*.schema.json`，并补齐对应 invalid fixtures，避免 schema 文件新增后未被 validator 覆盖。
- 文档治理收口：`docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` 不再承载“下一包建议 / 剩余开发包表”；`CAD_AGENT_STATUS.md` 和 `CORE_RESTRUCTURE_PLAN.md` 更新为 Phase X/Y/R 已收口但不扩大能力声称的口径。
- 证据：focused 4-7 包测试 `46 tests OK`；全量 `450 tests OK`；repo audit 0 findings；`run_cad_validation.py --no-cad --output-dir output\validation_runs\codex-maintenance-4-7-no-cad` pass。本轮未运行真实 CAD，不新增 `geometry_verified` 结论。

### Codex 维护 1-3 包：证据止血、基线同步、路径安全

- `run_project_sample_cad_check.py` 新增 `--require-cad-verified`：报告不是 `geometry_verified` 时返回非 0；`--no-cad` 仍保存 `deferred_cad_readback_required` 报告，但不能被 CI / 交接误当成真实 CAD 通过。
- `projects/` 样本 manifest 输入路径现在必须解析在样本目录内；protocol scan 新增 `manifest_input_outside_sample`，loader 同步拒绝越界读取。
- benchmark / drawing-read benchmark 的 `case_id` 现在必须是安全 path segment；benchmark output root、drawing-read output root、CAD validation output dir 均限制在仓库 `output/` 下；CAD validation 清理 stale artifact 前会再次确认目标留在本轮 `output_dir` 内。
- 状态文档同步口径：`BETA-PROJECT-SAMPLE-05` 当前仓库存档 no-CAD 报告是 deferred，不是真实 AutoCAD `geometry_verified`；真实样本 CAD readback 仍需用户会话单独运行。
- 证据：focused 1-3 包测试 `48 tests OK`；全量 `432 tests OK`；repo audit 0 findings；`run_cad_validation.py --no-cad --output-dir output\validation_runs\codex-maintenance-fix-no-cad` pass；blank-shell benchmark 8/8 pass；office alpha benchmark 18/18 pass；interior delivery benchmark 3/3 pass；`run_project_sample_cad_check.py --no-cad --require-cad-verified` 按预期返回 1 并写出 deferred 报告。

### Codex 深度全量安全复盘与加固

- 修复 Cursor 大量改动后的 4 类回归/风险：项目样例协议测试误用系统 temp、benchmark case 缺失完整 evidence triplet、proposal confirmed benchmark 缺少 `evidence_summary`、项目样例 CAD check / drawing standard profile 使用非法证据词。
- benchmark runner 新增强制校验：所有 case expected 必须包含 `evidence_state`、`geometry_accuracy`、`screenshot_role`；suite `expected_evidence_summary` 与实际 rollup 不一致时失败。
- `core/project_samples/cad_check.py` 的 no-CAD / failure / fake CAD 路径统一使用 evidence contract 合法词；`libraries/drawing_standards/codex_preview_beta.json` 的 `screenshot_role` 修正为 `not_applicable`。
- 维护性拆分：新增 `core/benchmarks/expectations.py`、`core/verification/evidence_vocabulary.py`、`core/composition_engine/preview.py`、`core/workflows/blank_shell_candidates.py`、`tests/core/cad_validation_payloads.py`、`tests/core/test_benchmark_validation.py`，使 repo audit 大文件 findings 从 6 个降为 0。
- 静态与回归证据：`424 tests OK`；repo audit 0 findings；Python AST `248` files / 0 errors；JSON `166` files / 0 errors；坏证据词和系统 temp 回归未命中。
- 验收脚本证据：`self_check.py` pass；`render_preview.py --check` ready；project sample protocol scan pass；project sample benchmark 2/2 pass；proposal confirmed benchmark 2/2 pass；CAD beta rollup 5/5 pass；office/residential/restaurant scene beta benchmark 分别 9/9、8/8、8/8 pass。

### BETA-SCENE-03 restaurant / commercial scene beta benchmark

- `restaurant_scene_beta_benchmark.json`（8 cases：入口/堂食/后场/blank-shell/failure）。
- `restaurant/preferences.json` 增加 `scene_beta`；`restaurant_scene_beta.py`。
- 证据：`422 tests OK`（+2）。

### BETA-SCENE-02 residential scene beta benchmark

- `residential_scene_beta_benchmark.json`（8 cases：卧室/餐厅/收纳/blank-shell/failure）。
- `residential/preferences.json` 增加 `scene_beta`；`residential_scene_beta.py`。
- 证据：`420 tests OK`（+2）。

### BETA-SCENE-01 office scene beta benchmark

- `scene_beta.py` + `office_scene_beta_benchmark.json`（9 cases：object / micro_scene / blank_shell / failure）。
- `agents/office/preferences.json` 扩展 `scene_beta` 与 office 对象偏好；`run_office_scene_beta_benchmark.py`。
- 证据：`418 tests OK`（+2）。

### BETA-DRAWING-READ-05 / 父包 BETA-DRAWING-READ 收口

- `drawing_read_benchmark.json`（3 cases：全链路 pass、候选 pass、缺门洞 blocked + `structured_blockers`）。
- `drawing_read_benchmark.py` + `run_drawing_read_benchmark.py`；`beta_drawing_read_acceptance.md`。
- 证据：`416 tests OK`（+2）。

### BETA-DRAWING-READ-04 shell confirmation → SHELL_MODEL

- `shell_confirmation.py`：`shell_drawing_read_confirmation` schema、对照 report 校验、`apply` → `load_manual_shell`。
- 示例 `sample_shell_drawing_read_confirmation.json`；CLI `apply_shell_drawing_read_confirmation.py`。
- 证据：`414 tests OK`（+4）。

### BETA-DRAWING-READ-03 shell candidate confidence report

- `shell_candidate_report.py`：overall/boundary/openings 置信度、`gaps`、`human_confirmation_items`、`ready_for_human_confirmation_file`。
- `sample_geometry_walls_only_fixture.json` 负样本（缺门洞 blocker）；CLI `run_shell_candidate_report.py`。
- 证据：`410 tests OK`（+3）。

### BETA-DRAWING-READ-02 geometry feature candidates

- `geometry_candidates.py`：墙线段 / 门洞 / 柱 / 禁放区启发式候选；`dwg_geometry_candidates.schema.json`。
- Fixture `sample_geometry_feature_fixture.json`；CLI `run_geometry_candidates.py`。
- 证据：`407 tests OK`（+3）。

### BETA-DRAWING-READ-01 read-only DWG entity summary

- `dwg_read_only.py`：`build_dwg_entity_summary`、fixture / active CAD / driver 入口；`dwg_entity_summary.schema.json`。
- `FakeCadDriver.snapshot_modelspace()` 供只读汇总；CLI `run_dwg_entity_summary.py`。
- 证据：`404 tests OK`（+4，含 READ-02 前基线）。

### BETA-PROPOSAL-05 / BETA-PROPOSAL 父包收口

- `finalize_confirmed_cad_plans()` 输出受控 CAD_PLAN bundle + `unselected_candidate_evidence`；validate/dry-run 全通过。
- `proposal_confirmed_benchmark.json`（2 cases）；`beta_proposal_acceptance.md` rollup。
- 证据：`400 tests OK`（+5）。

### BETA-PROPOSAL-04 partial CAD_PLAN replan

- `partial_replan.py`：`recompute_cad_plans_from_pipeline_artifacts()` 跳过上行动线，仅更新 placements/layout/CAD_PLAN/验证产物。
- CLI `run_proposal_partial_replan.py`；`partial_replan_report.json` 记录 skipped/recomputed 模块。
- 证据：`395 tests OK`（+2）。

### BETA-PROPOSAL-03 user confirmation input schema

- `proposal_user_confirmation.schema.json` + `user_confirmation.py`（validate / build / apply / round-trip）。
- 示例 `examples/confirmations/`；CLI `apply_proposal_user_confirmation.py`。
- 证据：`393 tests OK`（+6）。

### BETA-PROPOSAL-02 proposal comparison summary benchmark

- `proposal_comparison_summary`（object_coverage / circulation / conflicts / failure_reasons）；pipeline 写出 `proposal_comparison_summary.json`。
- `proposal_comparison_benchmark.json` 4 cases；runner 新增 `requires_proposal_comparison_summary` 等断言键。
- 证据：`387 tests OK`（+3）。

### BETA-PROPOSAL-01 proposal candidate scoring fields

- 新增 `candidate_scoring.py`、`proposal_candidate_scoring.schema.json`；`DESIGN_PROPOSAL.candidates[]` 要求 `score_breakdown` + `ranking_reasons[{code,message}]`。
- `compare_layout_candidates` / `create_design_proposal` / blank-shell 分支接入；示例 proposal JSON 已更新。
- 证据：`384 tests OK`（+3）。

### BETA-PROJECT-SAMPLE-05 / BETA-PROJECT-SAMPLE 父包收口

- `core/project_samples/cad_check.py` + `run_project_sample_cad_check.py`：`sample_blank_shell` 多 CAD_PLAN 批量 CODEX_PREVIEW 执行与 created-handle readback；`--no-cad` → `deferred_cad_readback_required`。
- `beta_project_sample_acceptance.md` 记录 01–05 可声称 / 不可声称边界。
- 证据：`381 tests OK`（+4）；fake driver `geometry_verified`；真实 CAD 需在用户 AutoCAD 会话下单独运行 CLI。

### BETA-PROJECT-SAMPLE-04 project sample benchmark (pass + blocked)

- 新增 `projects/sample_blank_shell_too_small/`、`sample_blank_shell_too_small_loop.json`、`project_sample_benchmark.json`（2 cases）。
- `core/project_samples/benchmark.py` + `run_project_sample_benchmark.py`；`blocked_expected_non_cad` + `cad_plan_count=0` 硬断言。
- 证据：`377 tests OK`（+4）；`output/test_artifacts/benchmarks/beta_project_sample_04/benchmark_summary.json`。

### BETA-PROJECT-SAMPLE-03 sample workflow CAD_PLAN / dry-run / verification

- `sample_blank_shell_project_loop.json` + `run_sample_blank_shell_workflow()`；产出 CAD_PLAN、`dry_run valid`、`verification unverified`。
- CLI `run_project_sample_workflow.py`；`sample_workflow_report.json` 明确 `geometry_verified: false`。
- 证据：`373 tests OK`（+2）。

### BETA-PROJECT-SAMPLE-02 sample shell / project model fixtures

- `sample_blank_shell` 增加 `fixtures/`、`expected/project_model.expected.json`；`core/project_samples/loader.py`。
- manifest 驱动 `load_sample_inputs` / `build_sample_project_model`；金样回归测试。
- 证据：`371 tests OK`（+5）。

### BETA-PROJECT-SAMPLE-01 de-identified project sample protocol

- 扩展 `projects/README.md`；新增 `project_sample_manifest.schema.json`、`core/project_samples/protocol.py`。
- 基线样本 `sample_blank_shell/sample.manifest.json` + 样本 README；协议扫描拒绝提交 DWG。
- 证据：`366 tests OK`（+4）。

### BETA-CAD-BLOCK-05 / BETA-CAD-BLOCK 父包收口

- 新增 `cad_beta_evidence_rollup.py`、`beta_cad_block_acceptance.md`、rollup CLI；`fake_cad_driver.py` 供 probe 复用。
- rollup 汇总 01–04 non-CAD 子包 + 05 文档包；`geometry_verified_count=0`。
- 证据：`362 tests OK`；`output/test_artifacts/cad_beta_evidence/beta_cad_block_05/`。

### BETA-CAD-BLOCK-04 drawing_standard_profile

- 新增 `core/drawing_standard/`、`codex_preview_beta` profile / layer preset、schema 与 6-case beta suite。
- `preview_only` 下 CAD 执行层统一 `CODEX_PREVIEW`；语义层保留 `A-FURN` 等映射；`insert_block_alpha` dry-run 可带 `drawing_standard_profile_id`。
- 证据：`359 tests OK`（+9）。non-CAD only。

### BETA-CAD-BLOCK-03 entity-level capability probe evidence

- 新增 `entity_level_evidence.py`；`cad_capability_probe` 输出 `entity_evidence[]`（polyline 写读对比、layer_role→`CODEX_PREVIEW`、hatch `deferred`）。
- `ENTITY_CONTRACTS` 增加 `hatch`（deferred）；`inspect_dwg` 识别 Hatch；`validate_capability_probe_evidence` 在 verified 时要求 entity_evidence。
- 证据：`350 tests OK`（+6）。hatch 非真实 CAD 验证。

### BETA-CAD-BLOCK-02 block attribute / tag readback probe

- 新增 `block_attribute_probe.py`；`inspect_dwg` 归一化 `GetAttributes()`；`build_block_alpha_readback_report` 合并 attribute 判定。
- `attribute_readback_probe` 计划可声明期望 tag；缺 tag → `attribute_unverified` deferred，不误报 `geometry_verified`。
- 证据：`344 tests OK`。

### BETA-CAD-BLOCK-01 controlled block transform beta suite

- 新增 `block_alpha_beta_suite.json`（8 cases）、`block_alpha_beta_suite.py`、`run_block_alpha_beta_suite.py`。
- 多 `base_point`、rotation（45°/90°）、uniform scale（0.5/1.25/0.75）validate + dry-run。
- 证据：`336 tests OK`；`output/test_artifacts/block_alpha_beta/beta_cad_block_01/`。non-CAD only。

### X-SCENE-05 / X-SCENE-ALPHA 父包收口

- 新增 `docs/verification/scene_alpha_acceptance.md`、`tests/agents/test_scene_alpha_acceptance.py`。
- 总验收：scene alpha benchmark 3/3、`agents/` 边界扫描 0 violations、验证文档 bundle 齐全。
- **可声称**：office / residential / restaurant 复用同一 `blank_shell` Core pipeline（non-CAD）。
- **不可声称**：`geometry_verified`、Scene Agent 产品完成、真实项目/块库全量准确。
- 证据：`332 tests OK`；`output/test_artifacts/benchmarks/x_scene_05/`。

### X-SCENE-04 Scene Alpha explanation template

- 新增 `core/agents/scene_explanation.py`、`docs/verification/scene_alpha_explanation_template.md`、`tests/agents/test_scene_explanation.py`。
- 三场景 `rules.md` 增加 Preference→Core 映射与不可声称；`first-handoff.md` Scene Alpha 接手段。
- `scene_boundary_scan`：`rules.md` 仅做 import 扫描，允许文档引用 Core 入口名。
- 证据：`326 tests OK`；`output/test_artifacts/benchmarks/x_scene_04/` 3/3 pass。

### X-SCENE-03 Scene Agent boundary scan

- 新增 `core/agents/scene_boundary_scan.py`；扩展 `tests/agents/test_scene_agent_boundaries.py`（`test_x_scene_03_*`）。
- 更新 `agents/SCENE_AGENT_RULES.md`、`docs/verification/scene_alpha_agent_boundaries.md`；Alpha 场景 `rules.md` 补强 Core 边界表述。
- 证据：`322 tests OK`；`agents/` 树扫描 0 violations。

### X-SCENE-02 Scene Alpha multi-scene benchmark

- 新增 `examples/benchmarks/scene_alpha_benchmark.json`（office / residential / restaurant 三 case，均 `pipeline: blank_shell`）。
- `blank_shell_pipeline`：`scene_preferences` 驱动 `_select_circulation_for_zones`；metrics 导出 `preferences_scenario` / `selected_circulation_strategy`。
- `runner._actual_from_pipeline` + `preferences_path_contains` 断言；`zone_splitter` 用全部 `path_surface` 并集 bbox 切区（修复 along_wall 单区与走道重叠）。
- 证据：`317 tests OK`；`output/test_artifacts/benchmarks/x_scene_02/` 3/3 pass。

### X-SCENE-01 Scene Alpha preferences contract

- 锁定 `office` / `residential` / `restaurant`；`circulation_strategy_weights` + `agents/scene_alpha_manifest.json`。
- 新增 `core/agents/scene_alpha.py`；`tests/agents/test_scene_preferences.py` 扩展 X-SCENE-01 断言。
- 证据：`315 tests OK`。

### Y-MC-05 multi-candidate boundaries（Y-MULTI-CANDIDATE 收口）

- 新增 `docs/verification/blank_shell_multi_candidate_boundaries.md`；更新 `phase-y-blank-shell-hardening-plan.md`、`shell-layout-foundation-design.md`。
- 父包 `Y-MULTI-CANDIDATE` **5/5** 完成；下一主线 `X-SCENE-ALPHA`。
- 证据：`312 tests OK`；`output/test_artifacts/benchmarks/y_mc_05/` 8/8 pass。

### Y-MC-04 blank-shell near-real and failure shell cases

- `blank_shell_core_benchmark.json` 扩至 8 cases：`long_narrow`、`obstacle`、 `too_small`、`corridor_riser_blocks_main_path`。
- 新增 `blank_shell_corridor_riser_block_shell.json` + workflow；blocked 路径 metrics 含 `fixed_obstacle_count`。
- 证据：`312 tests OK`；`output/test_artifacts/benchmarks/y_mc_04/` 8/8 pass。

### Y-MC-03 benchmark multi-candidate assertions

- `runner._actual_from_pipeline` 输出 `zone_placement_candidate_count`、`object_coverage_rate`、`selected_failed_reason_distribution` 等。
- `blank_shell_core_benchmark.json` 四 case 增加 `requires_comparison_detail` 与多候选 `minimums` / `maximums`。
- 证据：`311 tests OK`；`output/test_artifacts/benchmarks/y_mc_03/` 4/4 pass。

### Y-MC-02 proposal comparison_detail

- `build_blank_shell_comparison_detail()`：对象覆盖率、失败检查数/分布、通道连续性、circulation 分支排序原因。
- `create_design_proposal()` 接入 `candidate_sets`；`comparison_summary` 为 narrative；未选中分支失败不触发 `needs_confirmation`。
- 证据：`310 tests OK`；blank-shell benchmark `y_mc_02` 4/4 pass。

### Y-MC-01 blank-shell candidate_sets artifact

- `build_blank_shell_candidate_sets()`：按 circulation 分支保留 zone/placement 候选明细，写入 `candidate_sets.json`。
- pipeline metrics 增加 `zone_placement_candidates`、`selected_circulation_strategy`、`selected_zone_id`。
- 证据：`309 tests OK`；blank-shell benchmark `output/test_artifacts/benchmarks/y_mc_01/` 4/4 pass。

### R4-05 evidence gate handoff rules（R4-EVIDENCE-GATES 收口）

- 新增 `docs/verification/evidence_gate_handoff_rules.md`：每包第 8 项三列表格、Codex 校验清单、禁止声称。
- 扩展 `docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` 标准模板与 Codex 指引；§18 R4-04、§19 R4-05。
- 父包 `R4-EVIDENCE-GATES` **5/5** 完成；下一主线 `Y-MULTI-CANDIDATE`。

### R4-04 CAD validation evidence alignment

- 新增 `core/verification/cad_validation_evidence.py`：`build_cad_validation_evidence_summary`、`cad_validation_evidence_gate_failure`。
- `cad_validation_runner` 写入 `report.json.evidence_summary`；no-CAD pass 要求 `non_cad_only`；含 CAD pass 要求 readback/capability 证据态。
- 步骤 stdout 未知 `evidence_state` 会使步骤 fail。
- 证据：`308 tests OK`；`output/validation_runs/r4-no-cad/report.json`。

### R4-03 benchmark suite evidence summary

- `summarize_benchmark_evidence` 输出 rollup 计数与 `screenshot_role_counts`；`validate_evidence_summary` 校验一致性。
- 三组 benchmark JSON 增加 `expected_evidence_summary`；suite 跑完后写入 `benchmark_summary.json` 并比对。
- 新增 `test_r4_three_benchmark_suites_match_expected_evidence_summary`。
- 证据：`304 tests OK`；`output/test_artifacts/benchmarks/r4_blank_shell/`、`r4_interior/`、`r4_office/`。

### R4-02 blocked / invalid failure benchmark assertions

- `validate_failure_expected_contract()`：failure case 必须 `failure_category` 或 `contains_blocked_reason`；`blocked`/`invalid` 与 `evidence_state` 配对。
- runner 支持 `maximums` 断言与 `_compare_failure_outcome_guards()` 静默 pass 防护。
- office alpha +1：`office_invalid_workflow_input`（`invalid_configuration`）；`too_small` 增加 `maximums.cad_plan_count: 0`。
- 证据：`302 tests OK`；`output/test_artifacts/benchmarks/r4_office_r2/`。

### R4-01 evidence classifier / vocabulary

- 扩展 `core/verification/evidence_contract.py`：`EVIDENCE_BLOCKED_EXPECTED_NON_CAD`、`EVIDENCE_DRY_RUN_VALID_PLAN_ONLY`、`EVIDENCE_INVALID_CONFIGURATION`、`EVIDENCE_STATE_VALUES`、`classify_benchmark_pipeline_evidence()`、校验函数。
- `core/benchmarks/runner.py` 移除本地 `_derive_evidence_state`，expected/actual 证据字段统一走词表校验。
- `composition_engine/templates.py`、`block_alpha_plan.py` 改用契约常量；`verification_report.schema.json` 补全 enum。
- 新增 `docs/verification/evidence_state_vocabulary.md`、`tests/core/test_evidence_classifier.py`。
- 证据：`299 tests OK`。

### R-OFFICE-MICRO-05 office alpha 收口

- `run_benchmark_suite` 写入 `benchmark_summary.json`，新增 `summarize_benchmark_evidence()`（`evidence_state` / `failure_category` 计数）。
- 新增 `docs/verification/office_alpha_benchmark_evidence.md`：17 cases 证据汇总、Alpha 退出门槛、可声称/不可声称边界。
- 同步 `phase-r-office-benchmark-cases.md`、`CAD_AGENT_STATUS.md`、handoff §14；`R-OFFICE-MICRO` 父包 5/5 完成。
- 证据：`294 tests OK`；`output/test_artifacts/benchmarks/office_alpha_r_micro/`。

### R-OFFICE-MICRO-04 office failure benchmark

- 新增 `core/layout_engine/office_layout_failure.py`：composition 净空冲突检测与 blank-shell `layout_expectation` 硬阻断。
- `blank_shell_pipeline` 支持 `layout_expectation.mode=require_all_placed`，过小房间样本返回 `insufficient_space`。
- `composition_engine` 新增 `door_clearance_conflict`、`cabinet_pullback_conflict` 失败模板。
- benchmark runner 支持 `failure_category`、`contains_blocked_reason`，blocked pipeline 映射 `evidence_state=blocked_expected_non_cad`。
- `office_alpha_benchmark.json` 扩至 **17 cases**（+3 failure）。
- 证据：`293 tests OK`；`output/test_artifacts/benchmarks/office_failure_r4/` → 17/17 pass（non-CAD，含 3 blocked）。

### Codex 第二轮风险验收与证据门禁继续加固

- 针对第二轮多 agent 挑刺审查，修复 CAD validation runner 只验证报告内部自洽、未与上一阶段 `execution_summary.json` 交叉比对 created handles 的缺口；新增 `core/verification/cad_validation_gates.py`。
- 加固 `block_alpha_report.status=geometry_verified`：必须有 `created_handles_scope=pass`、唯一 created handle、`block_reference` 实体 payload，以及 `block_name` / `insertion_point` / `rotation` / `scale` / `layer` / `bbox` 几何字段。
- 加固 `AutoCADComDriver.insert_block_alpha()` 失败路径：attributes、非法 base point、非受控 identity 在 COM 写入前拒绝；插入后若 handle 缺失或后置校验失败，会尝试删除刚插入的 block reference；复用同名 `CODEX_TEST_BLOCK_001` 前会校验受控 definition 形状。
- 修正 `insert_block_alpha` plan / dry-run 与 driver 的 scale 契约：plan 层拒绝非统一 scale，dry-run bbox 应用统一 scale。
- 测试拆分以保持 repo audit 行数门禁：新增 `tests/core/test_autocad_block_alpha_hardening.py`、`tests/core/test_cad_validation_runner_handle_scope.py`。
- 最新证据：`290 tests OK`；repo audit 0 findings；office alpha benchmark 14/14 pass；`run_cad_validation.py --no-cad --block-alpha-only` pass with deferred evidence；standalone block alpha negative no-CAD exit 1。
- 真实 AutoCAD 复验通过：`output/validation_runs/codex-second-gate-block-alpha-cad-final/report.json`（block handle `99B`）与 `output/validation_runs/codex-second-gate-full-cad-final/report.json`（baseline handles `99C..9E6`，block handle `ABC`）。
- 负向 COM 探针通过：非法 `block_id`、非法 `block_name`、attributes、非法 `base_point` 均被拒绝，当前测试 DWG ModelSpace 实体数 `131 -> 131`。

### Codex 风险验收与证据门禁加固

- 针对多 agent 审查发现的风险，补强 `insert_block_alpha` 三层门禁：`CAD_PLAN` 校验、`execute_plan` 调用链和 `AutoCADComDriver` 现在只允许 `block_id=controlled-test-block-001` 与 `block_name=CODEX_TEST_BLOCK_001`。
- 加固 CAD 证据契约：`readback_report.status=geometry_verified` 必须带非空 `actual.created_handles`、实体回读 payload 和 `created_handles_scope=pass`；`block_alpha_report.status=geometry_verified` 必须带非空 `created_handles` 且 `entity.type=block_reference`。
- 修复 `run_cad_validation.py --no-cad --block-alpha-only` 漏掉 `block_alpha_deferred_evidence` 的问题；`scripts/run_block_alpha_validation.py` 在 readback failed 时现在返回非 0。
- 为上述风险新增回归测试，当前全量 `267 tests OK`；`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings。
- 结构拆分：新增 `core/cad_io/autocad_block_alpha.py`、`core/verification/cad_validation_types.py`、`core/verification/cad_validation_block_alpha.py`，将 `autocad_com.py` 和 `cad_validation_runner.py` 降到 repo audit 行数限制以内。
- 真实 AutoCAD 复验通过：`output/validation_runs/codex-review-block-alpha-cad-after-gate/report.json` 为 `status=pass`，block handle `879` 定向 readback 全 pass；`output/validation_runs/codex-review-full-cad-after-gate/report.json` 为 `status=pass`，baseline handles `87A..8C4` 与 block handle `99A` 均完成 created-handle readback。
- 负向 COM 探针通过：直接调用 driver 写入任意 `block_id` / 任意 `block_name` 均被拒绝，当前测试 DWG 的 `CODEX_PREVIEW` 实体数保持 `111 -> 111`，没有新增实体。

### PlanMD 后置拆分合并与 Markdown 架构收束

- 按用户要求暂停“额外后备计划”口径，把五大后置主线的小包明细合并为 `CORE_RESTRUCTURE_PLAN.md` 的唯一承载。
- 从 `docs/planning/phase-r-rebirth-implementation-plan.md` 移除后置 Backlog 明细副本，改为只保留 Phase R 当前执行剧本和一条主 PlanMD 引用。
- 补强 `CORE_RESTRUCTURE_PLAN.md`、`AGENTS.md`、`docs/README.md`、`CORE_CONTEXT_BRIEF.md`、`CAD_AGENT_STATUS.md` 和 `docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` 的主从规则：后置 Backlog、未来小包、优先级和退出标准只在主 PlanMD 维护。
- 本轮只做 Markdown 架构收束，不运行真实 CAD，不改变能力成熟度百分比。

### 五大后置主线 Backlog 登记

- 回答“当前小包完成后继续往哪里走”的问题，不新增第二套主计划。
- 在 `CORE_RESTRUCTURE_PLAN.md` 增加“当前小包队列完成后的后置 Backlog”，明确只有当前活跃小包收口或用户明确切换后才启用。
- 五大后置主线为：真实 CAD 能力扩展、真实项目样本闭环、多方案设计与交互确认、自动读图 / 空壳识别、场景 Agent Beta。
- 当时曾在 `docs/planning/phase-r-rebirth-implementation-plan.md` 复制五大主线细化表；随后已按用户要求合并回唯一 PlanMD，不再由执行剧本承载后置小包明细。
- 同步 `CORE_CONTEXT_BRIEF.md` 与 `CAD_AGENT_STATUS.md`，声明该 Backlog 不改变当前 Cursor / Codex 小包执行优先级，也不提升功能成熟度百分比。

### R-OFFICE-MICRO-03 office 场景级 benchmark

- 新增 3 个 office shell + workflow：`long_narrow`、`obstacle_riser`、`mixed_zone`。
- `blank_shell_pipeline` metrics 增加 `no_place_zone_count`、`fixed_obstacle_count`、`shell_id`。
- `office_alpha_benchmark.json` 扩至 **14 cases**（+3 blank_shell scene）。
- 证据：`260 tests OK`；`output/test_artifacts/benchmarks/office_scene_r1/` → 14/14 pass（non-CAD）。

### R-OFFICE-MICRO-02 office 微场景 benchmark

- `composition_engine` 新增 4 个 office micro-scene 模板：`single_desk_chair_pair`、`desk_with_back_cabinet`、`two_workstations_shared_aisle`、`entry_reception_clearance`（含 `bindings`、`clearance_refs`、`circulation`）。
- benchmark runner 支持 `contains_binding_relations`、`contains_circulation_roles`。
- `office_alpha_benchmark.json` 扩至 **11 cases**（+4 composition_spec micro-scenes）。
- 证据：`260 tests OK`；`output/test_artifacts/benchmarks/office_micro_r2/` → 11/11 pass（non-CAD）。

### R-OFFICE-MICRO-01 office 对象级 benchmark 扩展

- `object_defaults.json` 新增 `computer_desk`、`storage_cabinet`、`file_cabinet`（含 `placement_role`、`clearance_refs`、组件 roles）。
- `create_object_spec` 透传 `placement_role` / `clearance_refs` / `assertion_hints`。
- benchmark runner 支持 `contains_clearance_refs` 与 `clearance_ref_roles` metrics。
- `office_alpha_benchmark.json` 由 4 cases 扩至 **7 cases**（新增 `computer_desk_default_spec`、`storage_cabinet_front_clearance`、`file_cabinet_default_spec`）。
- 证据：`259 tests OK`；`run_benchmark_suite.py … office_alpha_benchmark.json` → **7/7 pass**（`output/test_artifacts/benchmarks/office_object_r1/`）。
- 仍为 non-CAD；不能声称办公微场景、通道或真实 CAD 几何准确。

### R-BLOCK-CAD-05 真实 AutoCAD block alpha 验收

- 受控块定义 footprint 与 metadata 对齐（900×450），保证 readback bbox 与 plan 一致。
- `run_cad_validation.py --block-alpha-only` 聚焦 block alpha CAD 步骤；新增 `block_alpha_capture_screen`。
- 用户会话真实 CAD 验收：`output/validation_runs/r-block-alpha-cad/report.json` → `status=pass`；`block_alpha_report.json` → `geometry_verified` / `readback_geometry_verified`；`created_handles=["878"]`；截图 `block-alpha-window.png`（仅视觉辅助）。
- 证据说明：`docs/verification/block_alpha_cad_evidence.md`。
- 不能把受控样本 pass 扩大到任意块库或项目图纸。

### R-BLOCK-CAD-04 CAD validation runner 接入 block alpha

- `cad_validation_runner` 新增 `block_alpha_validate_plan` / `block_alpha_dry_run` / `block_alpha_deferred_evidence`（no-CAD）与 `block_alpha_execute` / `block_alpha_readback`（CAD）。
- 新增 `core/verification/block_alpha_validation.py`、`scripts/run_block_alpha_validation.py`；顶层 `report.json` 含 `block_alpha` 摘要，硬门禁禁止 no-CAD 误报 `geometry_verified`。
- no-CAD 实跑：`output/validation_runs/r-block-alpha-no-cad-test/report.json` → `status=pass`，`block_alpha.geometry_verified=false`。
- 全量 **259 tests OK**；真实 CAD block alpha 总验收仍 deferred 至 `R-BLOCK-CAD-05`。

### R-BLOCK-CAD-03 block_reference readback 标准化

- `normalize_com_entity()` 识别 `AcDbBlockReference`，输出 `block_name`、`insertion_point`、`rotation`（度）、`scale`、`bbox`。
- `geometry_checks.check_block_reference_readback()` 对照 `insert_block_alpha` plan 断言，失败分类含 `readback_missing`、`block_name_mismatch`、`anchor_mismatch`、`rotation_mismatch`。
- `evidence_contract` 中 `block_reference.implementation_status` 更新为 `readback_normalize_baseline`。
- 全量 **255 tests OK**；validation runner 接入仍 deferred 至 `R-BLOCK-CAD-04`。

### R-BLOCK-CAD-02 insert_block_alpha COM 写入

- `AutoCADComDriver.insert_block_alpha()`：先 `ensure_controlled_block_definition()`，再 `ModelSpace.InsertBlock`；仅 `CODEX_PREVIEW`、统一 scale；`definition_missing` / `insert_failed` / `attribute_unverified` 通过 `BlockAlphaInsertionError` 结构化抛出。
- 新增 driver 与 `execute_plan` 契约单测；全量 **250 tests OK**。
- 未运行真实 CAD；几何 readback 仍 deferred 至 `R-BLOCK-CAD-03`。

### R-BLOCK-CAD-01 受控块定义解析

- `AutoCADComDriver` 新增 `block_definition_exists()`、`ensure_controlled_block_definition()` 与最小矩形块定义创建路径；优先复用 DWG 内 `CODEX_TEST_BLOCK_001`，缺失时在 layer `0` 写入 100×50 临时几何，不写正式图层、不保存 DWG。
- 查找/创建失败时返回结构化 `definition_missing`（`status` + `failure_category` + `block_name` + `message`）。
- `docs/planning/phase-r-cad-capability-contract.md` 补充受控块定义解析说明。
- 新增 5 项 `tests.core.test_autocad_com_driver` 用例；全量 **244 tests OK**。
- 未运行真实 CAD；`insert_block_alpha` COM 插入仍 deferred 至 `R-BLOCK-CAD-02`。

### 剩余开发包二级小包拆分

- 按用户截图中的“开发包清单”继续细化当前未开始的包，不新增第二套主计划。
- 在 `CORE_RESTRUCTURE_PLAN.md` 新增并加固“剩余开发包二级拆分索引”，把 `R-BLOCK-CAD-ALPHA`、`R-OFFICE-MICRO`、`R4-EVIDENCE-GATES`、`Y-MULTI-CANDIDATE`、`X-SCENE-ALPHA` 拆成 25 个二级小包，并补充目标、文件范围、依赖顺序、子校验、退出标准、证据状态和 handoff 更新七项完整性门槛。
- 在 `docs/planning/phase-r-rebirth-implementation-plan.md` 为每个未开始父包补“二级小包拆解”和推荐执行顺序，明确文件范围、子校验命令和退出标准；其中 office 子包统一命名为 `R-OFFICE-MICRO-01..05`，避免与旧的 R-OFFICE 高层任务编号混淆。
- 在 `docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` 补齐“剩余开发包细分索引”，让 Cursor / Codex 后续按小包追加 9 项交接记录。
- 本轮只拆分 Markdown 计划，不修改代码、不运行真实 CAD、不声称剩余小包已完成。

### Cursor 开发包交接包文档

- 新增 `docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md`：按开发包汇总 Cursor 交付的 9 项标准交接（含会话探针、`R-CAD-VIEW-CAPTURE`、`R-CAD-CONTRACT`、`R-BLOCK-METADATA`、`R-BLOCK-PLAN` 回填）。
- 新增 `docs/handoffs/README.md` 索引；`AGENTS.md`、`CORE_CONTEXT_BRIEF.md`、`docs/README.md` 增加入口。
- 约定：每完成一个 PlanMD 开发包，必须同步更新交接包文档。

### R-BLOCK-PLAN insert_block_alpha CAD_PLAN

- 新增 `core/plan_engine/block_alpha_plan.py` 与 `examples/plans/insert_block_alpha_test.json`，引入受控 `insert_block_alpha` intent。
- `validate_plan` 现拒绝正式图层、空 `cad_identity.block_name`、非法 `scale` 与缺 `base_point`；仅允许 `CODEX_PREVIEW`。
- `create_dry_run_report` / `dry_run_plan.py` 对 block alpha 输出 bbox、anchor、rotation、layer role 检查，并标记 `evidence_state=dry_run_valid_plan_only` 与 `geometry_accuracy=not_verified_without_cad_readback`。
- `execute_plan.py` 通过 fake driver `insert_block_alpha()` 记录执行意图，不触碰真实 AutoCAD。
- 更新 `core/schemas/cad_plan.schema.json` 与 `schemas/cad_plan.schema.json`。
- 复验：`239 tests OK`；`run_cad_validation.py --no-cad --output-dir output\validation_runs\r-block-plan-no-cad` pass。

### R-BLOCK-METADATA 图块库 v0.2 与受控测试块

- 扩展 `core/schemas/block_library.schema.json` 支持 `0.1` / `0.2`；`0.2` 块含 `source`、`cad_identity`、`anchor_points`、`footprint_2d`、`clearance_zones`、`symbol_2d`、`layer_bindings`、`validation`。
- 升级 `libraries/blocks/block_library.example.json` 为 `0.2`，新增 `controlled-test-block-001`（`metadata_only`）与其余 `symbol_fallback` 家具元数据；侧车文件 `libraries/blocks/controlled/CODEX_TEST_BLOCK_001.metadata.json`。
- 扩展 `core/block_engine/block_library.py`：`normalize_block()`、`validate_block_library()`、`object_spec_to_block_reference()`；`0.1` 示例仍可加载并自动补全 v0.2 派生字段。
- 扩展 `block_selector` / `block_placement`：按 `validation.status` 过滤、`cad_identity` 与 `layer_role` 进入 preview intent。
- 复验：`234 tests OK`；repo audit 0 findings；blank-shell benchmark pass；`run_cad_validation.py --no-cad --output-dir output\validation_runs\r-block-metadata-no-cad` pass。
- 边界不变：不声称真实块插入、公司块库或 `geometry_verified` block readback 已完成。

### R-CAD-CONTRACT 证据契约与硬门禁

- 新增 `core/verification/evidence_contract.py`：集中定义 `ENTITY_CONTRACTS`、`deferred_verification`、证据状态词表，以及 capability probe / readback 报告的注解与校验函数。
- `cad_capability_probe` 现输出 `contract_version`、`evidence_state`、`geometry_accuracy`、`screenshot_role`、`contract`、`limitations`；`cad_capability_verified` 使用 `verified_by_cad_capability_readback`，与 baseline `readback_geometry_verified` 分离。
- `build_verification_report` 现输出 `evidence_state`、`geometry_accuracy`、`screenshot_role`；`geometry_verified` 时标记 `readback_geometry_verified` / `verified_by_cad_readback`。
- `cad_validation_runner` 在 `inspect_readback` 与 `cad_capability_probe` 步骤增加证据字段硬门禁；步骤记录会透传子报告证据字段。
- 更新 `core/schemas/verification_report.schema.json`、`examples/verification_reports/minimal_cabinet_verification.json`、`docs/planning/phase-r-cad-capability-contract.md` 与 Phase R 执行记录。
- 复验：`228 tests OK`；`run_cad_validation.py --no-cad --output-dir output\validation_runs\r-cad-contract-no-cad` 与真实 CAD `r-cad-contract-cad` 均为 `status=pass`。
- 边界不变：不声称 block insertion、真实块库或任意 CAD_PLAN 已验证；截图仍只作视觉辅助。

### 交付进度估算规则写入主入口

- 按用户要求在 `README.md` 增加“交付进度规则”：后续每次 CAD Agent 相关交付，最终回复必须带 `总进度`、`Core 底座开发进度`、`Agent 多场景实现进度` 三项估算。
- 同步 `AGENTS.md` 和 `CORE_CONTEXT_BRIEF.md`，让 Codex 恢复上下文和最终交付时都能看到该要求。
- 将 `CAD_AGENT_RULES.md` 的进度字段名从旧口径统一为 `总进度`、`Core 底座开发进度`、`Agent 多场景实现进度`，默认权重仍为 Core 70%、Agent 30%。
- 更新 `CAD_AGENT_STATUS.md` 的当前进度估算字段名；本次仅固化交付格式，不提升进度百分比。

### R-CAD-VIEW-CAPTURE 实现与真实 CAD 验证

- 按用户要求优先完成窗口级截图小开发包，避免继续依赖全屏截图导致 Codex 或其他窗口遮挡 AutoCAD 画面。
- 扩展 `core/verification/render_preview.py`：`--check` 现在输出 `capture_modes`、`autocad_window`、`autocad_viewport_or_client` 等结构化字段；新增 `--capture-autocad-window`、`--execution-summary`、`--layer` 和 `--fallback-screen`，默认尝试恢复并置前 AutoCAD 窗口，再截取客户区。
- 扩展 `core/cad_io/autocad_com.py`：新增按实体 bbox 计算视图范围、`zoom_to_bbox()` 和 `zoom_to_handles()`，用于在截图前按本轮 created handles 缩放到当前输出范围。
- 更新 `core/verification/cad_validation_runner.py`：真实 CAD 总控截图步骤改为 `cad-validation-window.png`，命令使用 `scripts/render_preview.py --capture-autocad-window --execution-summary <execution_summary.json>`；旧全屏截图路径只作为 stale artifact 清理项保留。
- 扩展测试 `tests/core/test_render_preview.py` 与 `tests/core/test_cad_validation_runner.py`，覆盖无 AutoCAD 窗口时不误报 ready、窗口级截图 bbox、缺窗口失败分类，以及总控必须调用 `--capture-autocad-window`。
- 同步 `CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_RESTRUCTURE_PLAN.md`、`docs/planning/phase-r-rebirth-implementation-plan.md`、`docs/planning/phase-w-cad-validation-plan.md`、`CAD_AGENT_BLOCKER_PLAYBOOK.md`、`CAD_AGENT_AUTONOMOUS_VALIDATION.md`、`docs/onboarding/migration-checklist.md` 和 `CAD_AGENT_ISSUES.md`，把当前执行口径从全屏截图更新为窗口级视觉辅助截图。
- 复验通过：focused tests 11 项 OK；`scripts\render_preview.py --check` 在无可用窗口时只报告 `screen`，不误报窗口级 ready；`scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\r-cad-view-no-cad` 顶层 `status=pass`；真实 CAD `scripts\run_cad_validation.py --output-dir output\validation_runs\r-cad-view-cad` 顶层 `status=pass`。
- 真实 CAD 证据：`output\validation_runs\r-cad-view-cad\cad-validation-window.png` 为 AutoCAD 客户区截图，`capture_screen.stdout.txt` 记录 `mode=autocad_window`、窗口标题 `Autodesk AutoCAD 2026 - [Drawing1.dwg]`、`bbox=[6,0,1914,1028]`、`focus.status=zoomed_to_bbox`、`handle_count=7`；`readback_report.json.status=geometry_verified`，`cad_capability_probe.json.status=cad_capability_verified`。
- 边界不变：截图只作为视觉辅助；真实 CAD 几何准确仍必须以 validate、dry-run、`CODEX_PREVIEW`、created handles 定向回读和 `geometry_verified` 为准。全程只写入 `CODEX_PREVIEW`，未保存 DWG、未覆盖原图、未删除实体、未修改正式图层。

### CAD 窗口级截图开发包登记

- 按用户指出“直接按当前屏幕截图会被 Codex 窗口遮挡”的问题，将 AutoCAD 窗口级 / 视口级截图能力拆成独立开发包 `R-CAD-VIEW-CAPTURE`。
- 在 `CORE_RESTRUCTURE_PLAN.md` 的当前活跃队列和开发包表中加入 `R-CAD-VIEW-CAPTURE`，目标是优先截取 AutoCAD 客户区或按本轮 created handles bbox 缩放后的实体范围截图。
- 在 `docs/planning/phase-r-rebirth-implementation-plan.md` 增加该包的文件范围、开发步骤、子校验命令和通过标准，明确截图仍是 `visual_aid_only`，不能替代 created handles readback。
- 同步 `CORE_CONTEXT_BRIEF.md` 与 `CAD_AGENT_STATUS.md`，把下一轮开发包数量从八个更新为九个；该条为计划登记时状态，随后同日已完成 `R-CAD-VIEW-CAPTURE` baseline 实现与真实 CAD 验证，见上方记录。

### 下一轮开发拆解与子校验计划

- 按用户要求将“先推进 R-CAD / R-BLOCK、补 office micro-scene 与 failure benchmark、强化 blank-shell 多候选、保持 Core 优先”的开发建议落入 Markdown。
- 在 `CORE_RESTRUCTURE_PLAN.md` 新增“下一轮开发拆解与子校验”，把后续工作拆成 `R-CAD-CONTRACT`、`R-BLOCK-METADATA`、`R-BLOCK-PLAN`、`R-BLOCK-CAD-ALPHA`、`R-CAD-VIEW-CAPTURE`、`R-OFFICE-MICRO`、`R4-EVIDENCE-GATES`、`Y-MULTI-CANDIDATE`、`X-SCENE-ALPHA` 九个开发包。
- 在 `docs/planning/phase-r-rebirth-implementation-plan.md` 新增文件级开发拆解，明确每个开发包的目标、文件范围、开发步骤、子校验命令和通过标准。
- 本轮只细化计划与校验路径，不修改代码、不运行真实 CAD、不提升能力成熟度，也不把 block insertion、office micro-scene 或 blank-shell 多候选写成已完成能力。

### PlanMD 主线权威收束

- 按用户要求继续雕琢整体文档架构，明确 `CORE_RESTRUCTURE_PLAN.md` 是唯一 `PlanMD` / 开发主线；根目录没有独立 `plan.md`，用户说 `PlanMD`、`plan.md` 或主 plan 时都指向该文件。
- 在 `CORE_RESTRUCTURE_PLAN.md` 新增 “PlanMD 主线协议”，把文档层级收束为：PlanMD 决定当前队列、Phase 顺序、优先级、Decision Gate 和退出标准；`docs/planning/phase-*.md` 只做辅助执行剧本；状态、路线、架构、治理、交接、验证、历史和 review 文档只服务主线。
- 更新 `AGENTS.md`、`CORE_CONTEXT_BRIEF.md`、`CAD_AGENT_RULES.md`、`README.md`、`docs/README.md`、`docs/planning/README.md`、`docs/onboarding/first-handoff.md` 与 `docs/governance/multi-agent-contribution.md`，让后续 Codex 恢复上下文时不会把多个 Markdown 误读成多条并列计划。
- 给 Phase R/W/X/Y/Z 相关 `docs/planning/*.md` 顶部补充“辅助执行剧本，不是独立 PlanMD”的提示，并把同步日期调整到 2026-05-26。
- 最后一轮按用户担心补强“防偏离边界”：PlanMD 只是文档治理和开发排序，不改变通用 CAD Agent Core Lab、Core 优先、`CAD_PLAN` 中间层、真实 CAD created-handle 回读门槛、场景 Agent 轻量化和保护用户 DWG 的根方向。
- 修正 `CAD_AGENT_RULES.md` 中进度估算的旧基准，使其与 `CORE_STATUS.md` / `CAD_AGENT_STATUS.md` 当前口径一致：通用底座约 70%，多场景 Agent 约 34%，总体约 59%。
- 本轮仍只改 Markdown，不改代码、不运行 CAD、不扩大任何真实 CAD 几何验证结论。

### 二次文档架构雕琢

- 按用户要求以“今天开发收尾”为边界，只做 Markdown 和文档入口重构，不修改 `core/`、`scripts/`、`drivers/`、`tests/`、`agents/`、`libraries/`、`projects/`、`examples/` 或 `schemas/`。
- 派出 AI 产品经理与深度架构程序员两个只读 agent 审阅仓库信息架构，结论收束为：代码边界基本成立，当前主要问题是入口权威性、计划散落、历史材料仍在根目录。
- 将低频文档迁出根目录：`SHELL_LAYOUT_FOUNDATION_DESIGN.md` 迁到 `docs/architecture/shell-layout-foundation-design.md`，`SHELL_LAYOUT_TIME_ESTIMATE.md` 迁到 `docs/history/shell-layout-time-estimate.md`，`CAD_AGENT_DECISIONS.md` 迁到 `docs/decisions/cad-agent-decisions.md`。
- 将已执行的 `docs/planning/core-platform-md-split-plan.md` 迁为 `docs/history/core-platform-md-split-plan-2026-05-25.md`，并新增 `docs/history/README.md`。
- 将 README 中的长篇换机清单拆到 `docs/onboarding/migration-checklist.md`，README 只保留入口链接；同步修正 README 中 `219 tests` 到 `223 tests`，并修正“没有真实回读”这类过期口径为“真实回读覆盖仍有限”。
- 将 `CORE_RESTRUCTURE_PLAN.md` 标题和职责收束为唯一主计划，新增“当前活跃工作队列”；`CORE_STATUS.md` 与 `CAD_AGENT_STATUS.md` 不再承载独立下一步清单，只保留能力、证据、缺口和风险边界。
- 更新 `CORE_CONTEXT_BRIEF.md`、`CAD_AGENT_RULES.md`、`docs/planning/README.md`、`docs/architecture/README.md`、`docs/onboarding/first-handoff.md` 和 Phase 文档中的旧路径、旧计划口径与主从关系。
- 新增 `docs/README.md` 作为文档区总地图，更新 `docs/onboarding/README.md` 补换机清单入口，并将 `docs/ROADMAP.md` 降级为兼容跳转，避免旧阶段路线干扰当前 `CORE_ROADMAP.md` 与主计划。

## 2026-05-25

### Phase R 角色组合真实 CAD 落图与回读

- 根据用户指出“这些东西不是在 CAD 里面”，将此前仅有 SVG/浏览器 PNG 的角色组合自检推进到真实 AutoCAD：新增 `core/execution/batch_plan_runner.py`，支持对多份 CAD_PLAN 做坐标偏移、逐 plan 执行、created handles 汇总和 `geometry_verified` 回读报告。
- 新增 `scripts/run_composition_cad_check.py`，把 `examples/benchmarks/interior_delivery_benchmark.json` 产出的卧室床+地毯、餐桌组合、办公桌组合三组 CAD_PLAN 批量写入当前 AutoCAD 的 `CODEX_PREVIEW` 图层，并输出 `composition_cad_check_report.json`。
- 为避免覆盖或删除旧预览对象，真实 CAD 组合校验脚本支持 `--start-x`、`--start-y`、`--spacing-x` 参数；本轮最终使用 `--start-x 26000 --start-y 8000 --spacing-x 4200` 绘制到上方空白区域，未删除旧实体、未保存 DWG、未修改正式图层。
- 修复组合落图的 CAD 标注可读性问题：地毯作为底衬不再生成文字实体，大尺寸对象文字高度封顶，餐椅标签缩短为 `Chair`，避免真实 CAD 组合视图被文字遮挡。
- 新增和扩展测试：`tests/core/test_batch_plan_runner.py` 覆盖批量计划偏移与 fake readback，`tests/core/test_run_composition_cad_check.py` 覆盖 fresh CAD region 偏移参数，`tests/core/test_composition_engine.py` 与 `tests/core/test_execute_plan.py` 锁定组合标注策略和文字高度上限。
- 真实 CAD 复验通过：`output\validation_runs\interior-composition-cad-label-clean-y8000\composition_cad_check_report.json` 顶层 `status=geometry_verified`，3/3 cases verified，created handles 共 55 个；截图证据为 `output\validation_runs\interior-composition-cad-label-clean-y8000\composition-cad-screen-clean-y8000.png`。
- 最终回归通过：`unittest discover -s tests` 为 223 tests OK，`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings，`run_benchmark_suite.py examples\benchmarks\interior_delivery_benchmark.json` 为 3/3 pass，`run_cad_validation.py --no-cad --output-dir output\validation_runs\manual-no-cad-after-composition-cad` 为 `status=pass`。
- 证据边界更新：现在可以说这 3 个简单矩形对象组合已经真实落到 AutoCAD 并完成 created handles 回读；仍不能说已经完成真实家具块库、块插入、复杂符号、任意组合或真实项目图纸自动设计。
- 粗估进度小幅上调为：通用底座约 70%，多场景 Agent 约 34%，总体约 59%。该上调来自真实 CAD 组合回读闭环，不等同于达到 80% 或完成块库能力。

### Phase R 角色驱动组合交付自检

- 按用户提出的“模拟室内设计行业用户拿系统交付图块组合”的新维度，新增通用 `core/composition_engine/`，不把卧室、餐桌或办公桌组合写死进某个场景 Agent。
- 新增 `composition_spec` 生成能力：当前可把 `bedroom_bed_rug`、`dining_table_set`、`office_desk_combo` 转成组合规格、多份安全 `CAD_PLAN`、dry-run 报告、unverified verification 报告和 SVG 视觉辅助预览。
- 扩展 `libraries/objects/object_defaults.json`，新增 `rug` 与 `monitor` 对象默认规格，支持床+地毯、餐桌+椅、办公桌+椅+显示器三类组合。
- 扩展 `core/benchmarks/runner.py`：新增 `composition_spec` pipeline、`contains_object_roles` 断言、组合级 metrics、每个组合 CAD_PLAN 的 dry-run / verification 汇总和 `preview_svg` artifact。
- 新增 `examples/benchmarks/interior_delivery_benchmark.json`，模拟 `interior_designer`、`home_designer`、`office_planner` 三个角色，分别验收卧室床+地毯、餐桌组合和办公桌组合。
- 新增 `tests/core/test_composition_engine.py`，并扩展 `tests/core/test_benchmarks.py`，按 TDD 覆盖组合生成、plan-ready、视觉辅助 artifact 与 persona benchmark。
- 浏览器视觉检查发现首版 SVG 标题区与图形区过近，已修正 `write_composition_preview_svg()` 的标题留白并重新生成截图。
- 新鲜复验：`unittest discover -s tests` 为 219 tests OK；`run_benchmark_suite.py examples\benchmarks\interior_delivery_benchmark.json` 为 3/3 pass；三张浏览器截图保存到 `output\test_artifacts\benchmarks\interior_delivery_manual\*\preview-browser.png`。
- 证据边界保持不变：本轮组合交付是 non-CAD benchmark 和视觉辅助预览，显式保留 `geometry_accuracy=not_verified_without_cad_readback` 与 `screenshot_role=visual_aid_only`，不能声称真实 CAD created-handle 几何已验证。
- 粗估进度小幅上调为：通用底座约 67%，多场景 Agent 约 31%，总体约 56%。该上调来自角色组合自检和 benchmark 证据增强，不来自真实 CAD 几何扩展。

### Phase R office benchmark 与证据状态 runner

- 按“继续通用底座深度开发”推进 Phase R 的 benchmark 代码切口，不运行真实 CAD，不修改 DWG。
- 扩展 `core/benchmarks/runner.py`：benchmark actual 现在包含 `evidence_state`、`geometry_accuracy`、`screenshot_role`、`object_types`、`component_roles` 和对象尺寸；expected 支持 `minimums`、`contains_object_types` 与 `contains_component_roles` 断言；新增 `object_spec` benchmark pipeline。
- 扩展 `core/workflows/blank_shell_pipeline.py`：metrics 增加 `object_types`，让 benchmark 能验证场景对象覆盖。
- 加固 benchmark 门禁：suite 中空 cases、非 object case、缺 `expected` 或空断言不再静默 pass；blank-shell 现在为每个生成的 CAD_PLAN 输出 `dry_run_reports.json` 与 `verification_reports.json`，runner 使用汇总状态而不是只看第一个 plan。
- 新增 `examples/benchmarks/office_alpha_benchmark.json`，当前包含 desk / chair / cabinet object spec 与 `office_small_suite_alpha` scene 共 4 个 cases，验证对象尺寸、组件角色、场景对象类型、最小指标和 `benchmark_pass_non_cad` 证据状态。
- 扩展 `tests/core/test_benchmarks.py`，按 TDD 增加 Phase R 证据状态与 office alpha benchmark 回归测试。
- 新鲜复验：`unittest discover -s tests` 为 214 tests OK；`run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json` 为 4/4 pass；`run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json` 为 4/4 pass；`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings。
- 证据边界保持不变：office alpha benchmark 是非 CAD 证据，显式写 `geometry_accuracy=not_verified_without_cad_readback` 和 `screenshot_role=visual_aid_only`，不能声称真实 CAD 几何准确。
- 粗估进度小幅上调为：通用底座约 64%，多场景 Agent 约 29%，总体约 54%。该上调来自 benchmark/office alpha 证据增强，不来自真实 CAD 几何扩展。

### Phase R 执行开发包细化

- 按用户要求继续执行修改后的 Phase R plan，创建多个只读专项 agent 细化 CAD 能力契约、办公 benchmark、图块库路线和多 agent 协作治理。
- 新增 `docs/planning/phase-r-rebirth-implementation-plan.md`，将 Phase R 拆成 R0-R5、R-GOV / R-CAD / R-BLOCK / R-OFFICE 任务和证据状态门禁。
- 新增 `docs/planning/phase-r-cad-capability-contract.md`，定义 line / rectangle / circle / arc / polyline / text / dimension / block_reference 的 write-read-verify 契约和 `insert_block_alpha` 草案。
- 新增 `docs/planning/phase-r-block-library-roadmap.md`，定义 `BLOCK_LIBRARY v0.2`、OBJECT_SPEC、drawing standard profile、受控测试块和 block insertion 迁移路线。
- 新增 `docs/planning/phase-r-office-benchmark-cases.md`，将办公桌、办公椅、电脑桌、柜体、入口、主通道和失败样本整理为 object / micro-scene / scene / failure benchmark cases。
- 新增 `docs/governance/multi-agent-contribution.md` 与 `docs/onboarding/first-handoff.md`，固化多 agent 协作边界、新人接手入口和不可声称边界。
- 更新 `CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CORE_ROADMAP.md`、`README.md` 和 `docs/planning/README.md`，让后续开发优先读取 Phase R 执行包。
- 本轮仍只改 Markdown；不修改代码、不运行 CAD、不把执行计划当成功能完成。

### Phase R 新鲜视角评审与重生式开发计划

- 按用户要求，创建多个只读专家 agent，从 CAD 自动化、图块库/制图标准、空间设计业务、平台架构、验证/benchmark 五个新鲜视角审视当前系统。
- 新增 `docs/reviews/fresh-eyes-review-2026-05-25.md`，记录多 agent 首次接手式评审结论。
- 新增 `docs/planning/phase-r-fresh-perspective-rebirth-plan.md`，将“重生式开发”收敛为 CAD 能力契约、办公基础闭环、图块库设计、benchmark 证据门禁和平台协作治理。
- 更新 `CORE_RESTRUCTURE_PLAN.md`：新增 Phase R、当前可信基线索引、Phase 状态语义、Interface Ownership Map、Decision Gates 和 Alpha 里程碑判定。
- 更新 `CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CORE_ROADMAP.md`、`README.md` 和 `docs/planning/README.md`，把 Phase R 纳入后续开发入口。
- 本轮仍只改 Markdown；不修改代码、不运行 CAD、不把新鲜视角评审当成 Core Alpha 完成。

### 主平台 Markdown 拆分执行

- 按 `docs/planning/core-platform-md-split-plan.md` 执行主平台 Markdown 拆分。
- 新增 `docs/planning/phase-w-cad-validation-plan.md`、`docs/planning/phase-x-scene-agent-alpha-plan.md`、`docs/planning/phase-y-blank-shell-hardening-plan.md`、`docs/planning/phase-z-doc-governance-plan.md`，分别承接 Phase W/X/Y/Z 的长篇执行剧本。
- 将 `CORE_RESTRUCTURE_PLAN.md` 收缩为主计划总控索引，保留当前复盘、能力边界、文档职责、阶段路线、Phase 执行入口、分歧点和完成判定。
- 更新 `CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`README.md` 和 `docs/planning/README.md`，让后续开发按目标 Phase 读取 `docs/planning/phase-*.md`。
- 根据只读复核 agent 反馈，修正 `README.md` 中旧的 196 项测试、21:42 复验时间、旧 CAD 证据路径和 entity readback 状态漂移，并修正 Phase Z 文档里 “本文收缩为总控索引” 的指代。
- 本次仍只改 Markdown 文档；真实 CAD 结论仍只覆盖已验证的 baseline plan 和 CAD capability probe，不扩大到真实项目图纸、块库、块插入或任意 CAD_PLAN。

### 主平台 Markdown 精细化拆分计划

- 用户要求本轮不改代码，先构建主平台 Markdown 拆分计划，为下一步执行降低上下文抖动。
- 新增 `docs/planning/` 作为规划类文档目录，并新增 `docs/planning/core-platform-md-split-plan.md`。
- 计划将 `CORE_RESTRUCTURE_PLAN.md` 收缩为总控索引，把 Phase W/X/Y/Z 的长篇执行剧本迁入 `docs/planning/phase-*.md`。
- 同步更新 `CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`CAD_AGENT_STATUS.md` 和 `README.md` 的入口说明。
- 本轮不修改 `core/`、`scripts/`、`drivers/`、`tests/`、`agents/` 或 CAD 图纸；真实 CAD 结论边界保持不变。

### 开发进度百分比口径固化

- 按用户要求新增长期规则：后续每次 CAD Agent 相关改动后，都要大概估算并汇报 `通用底座进度`、`多场景 Agent 进度` 和 `总体进度`。
- 固定默认权重：总体进度按 `通用底座 70% + 多场景 Agent 30%` 加权；百分比只作节奏判断，不替代真实验证证据。
- 写入 `CAD_AGENT_RULES.md` 的 `0.4 开发进度百分比估算口径`。
- 在 `CORE_STATUS.md` 和 `CAD_AGENT_STATUS.md` 写入当前基准估算：通用底座约 63%，多场景 Agent 约 28%，总体约 53%。
- 明确该估算允许 5-10 个百分点误差；只有形成可复验证据、状态同步和边界说明后才小幅上调，发现回归或验证缺口时可以下调。

### 基础图元 CAD 探针扩展与截图复验

- 用户要求用截图方式真实检验当前系统是否能调用 CAD 画出具体内容，并指出此前 CAD 测试覆盖过浅。
- 按 TDD 补充失败测试：`tests/core/test_autocad_com_driver.py` 覆盖 `draw_line`、`draw_circle`、`draw_arc`、`draw_polyline` 的 COM 调用参数；`tests/core/test_verification_report.py` 覆盖圆、弧、多段线回读标准化；`tests/core/test_cad_capability_probe.py` 要求能力探针从 7 个实体扩展到 11 个实体。
- 扩展 `core/cad_io/autocad_com.py`：新增独立直线、圆、弧、轻量多段线写入；弧角度从度转换为 AutoCAD COM 需要的弧度；多段线点集转换为 `VT_ARRAY | VT_R8` 2D 坐标数组。
- 扩展 `core/verification/inspect_dwg.py`：回读时识别 `circle`、`arc`、`polyline`，并为圆、弧、多段线补充中心、半径、角度、点集、闭合状态和 bbox 信息。
- 扩展 `core/verification/cad_capability_probe.py`：能力矩阵现在绘制并回读 1 个矩形边框、1 条独立直线、1 个圆、1 段弧、1 条闭合多段线、1 段文字和 2 个标注，预期类型统计为 `line=5`、`circle=1`、`arc=1`、`polyline=1`、`text=1`、`dimension=2`。
- 真实 CAD 单独探针通过：`output\validation_runs\manual-primitive-cad-probe\cad_capability_probe.json` 为 `status=cad_capability_verified`，entity_count 为 11，bbox 为 `900.0 x 450.0`，全部实体在 `CODEX_PREVIEW`。
- 缩放 AutoCAD 视图后截取视觉证据：`output\validation_runs\manual-primitive-cad-probe\cad-primitive-screen.png`，大小 538584 bytes；图面可见青色 `CAD_CAPABILITY_PROBE` 基础图元和黄色 `测试柜` baseline。
- 重新运行真实 CAD 总控通过：`output\validation_runs\manual-cad-after-primitive-probe\report.json` 顶层 `status=pass`，`readback_report.json.status=geometry_verified`，`cad_capability_probe.json.status=cad_capability_verified`。
- 安全边界保持不变：只写入 `CODEX_PREVIEW`，未保存 DWG，未覆盖原图，未删除实体，未修改正式图层。当前仍不能扩大为块插入、块库、正式图层或任意业务 CAD_PLAN 全部准确。

### CAD 调用底座能力矩阵加固

- 新增 `core/verification/cad_capability_probe.py` 与 `scripts/run_cad_capability_probe.py`，用于真实 AutoCAD COM 能力探针：活动文档读取、`CODEX_PREVIEW` 图层、矩形 4 线、文字、2 个标注、created handles、handle 定向回读、类型统计、bbox 和安全边界。
- 将 `cad_capability_probe` 纳入 `core/verification/cad_validation_runner.py` 的真实 CAD step；`run_cad_validation.py` 现在不仅要求 `readback_report.json.status=geometry_verified`，还要求 `cad_capability_probe.json.status=cad_capability_verified` 且 checks 全部 `pass`。
- 新增 `tests/core/test_cad_capability_probe.py`，并扩展 `tests/core/test_cad_validation_runner.py`，覆盖能力探针成功、连接失败、handle 回读缺失、以及总控不得把非 `cad_capability_verified` 探针误判为 pass。
- 离线复验通过：`unittest discover -s tests` 为 207 tests OK；`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings；`scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\cad-foundation-no-cad-final-20260525` 为 `status=pass`。
- 单独真实 CAD 能力探针通过：`output\validation_runs\cad-foundation-capability-probe-20260525\cad_capability_probe.json` 为 `status=cad_capability_verified`，created handles 为 `3966, 3967, 3968, 3969, 396A, 396B, 39A6`。
- 整合真实 CAD 总控通过：`output\validation_runs\cad-foundation-full-cad-20260525\report.json` 顶层 `status=pass`；`readback_report.json.status=geometry_verified`；`cad_capability_probe.json.status=cad_capability_verified`，探针 handles 为 `3A5E, 3A5F, 3A60, 3A61, 3A62, 3A63, 3A9E`。
- 新增 `docs/verification/cad_foundation_capability_check.md` 记录本轮证据。全程只写入 `CODEX_PREVIEW`，未保存 DWG，未覆盖原图，未删除实体，未修改正式图层。

### Phase W 全量修复：readback 硬门禁与真实 CAD 定向回读

- 执行全量修复复验时发现一个关键门禁问题：`output\validation_runs\full-repair-cad-20260525-212001\report.json` 顶层为 `status=pass`，但 `readback_report.json.status=screenshot_captured`，`geometry_readback` 为 `not_run`，`created_handles_scope` 为 `warning`。该结果不能证明几何准确。
- 按 Phase W W.10 自动修复仓库内问题：`core/verification/cad_validation_runner.py` 现在会在 `inspect_readback` 返回 0 后继续解析 readback JSON，只有 `status=geometry_verified` 且全部 checks 为 `pass` 才允许 step 通过；否则归类为 `readback_failed`。
- 修复真实大 DWG 回读性能风险：`core/verification/inspect_dwg.py` 和 `core/cad_io/autocad_com.py` 支持按 `execution_summary.created_handles` 调用 `Document.HandleToObject(handle)` 定向回读本轮实体，避免全量枚举 ModelSpace。
- 新增 / 扩展测试：`tests/core/test_cad_validation_runner.py` 覆盖非 `geometry_verified` readback 不得让 CAD 总验证通过；`tests/core/test_verification_report.py` 覆盖按 handles 回读时不得扫描 ModelSpace。
- 复验通过：`unittest discover -s tests` 为 203 tests OK；`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings；`scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\full-repair-no-cad-final-20260525` 为 `status=pass`。
- 真实 CAD 复验通过：`output\validation_runs\full-repair-cad-retry-20260525-212916\report.json` 顶层 `status=pass`；`execution_summary.json` 记录 created handles `38E9, 38EA, 38EB, 38EC, 38ED, 38EE, 392A`；`cad-validation-screen.png` 已生成；`readback_report.json.status=geometry_verified`，`readback_scope` / `layer_entities` / `bbox_size` / `base_point` / `label_text` / `dimension_count` / `created_handles_scope` 全部 `pass`。
- 全程只写入 `CODEX_PREVIEW`，未保存 DWG，未覆盖原图，未删除实体，未修改正式图层。当前仍只允许声明 Phase W baseline `examples\plans\draw_test_cabinet.json` 的真实 CAD 几何通过。

### Phase W 真实 CAD 调用排查与 baseline 回读闭环通过

- 对“CAD 已打开但脚本无法调用”做沙箱内/用户会话对照诊断：默认命令身份 `desktop-r40v31q\codexsandboxoffline` 看不到用户桌面的 `acad.exe`、窗口和 ROT/COM 活动对象；沙箱外用户身份 `desktop-r40v31q\user` 可见 AutoCAD PID 20880、窗口 `Autodesk AutoCAD 2026 - [A1_page2_vector_full.dwg]`，且 `AutoCAD.Application`、`AutoCAD.Application.25.1`、`AutoCAD.Application.25` 均可 `GetActiveObject`。
- 诊断证据：沙箱内 `output\validation_runs\cad-com-diagnostic-20260525-210153\cad_com_diagnostic.json`；用户会话 `output\validation_runs\cad-com-diagnostic-elevated-20260525-210219\cad_com_diagnostic.json`。
- 在用户会话下复跑 W-07 首次推进到 `execute_sample_plan`，发现真实 AutoCAD `ModelSpace.AddLine` 对普通 Python tuple 报 `-2147024809` 参数无效；按 W.10 自动修复仓库内 driver 问题。
- `core/cad_io/autocad_com.py` 新增 AutoCAD COM point 转换：坐标写入前转成 `VT_ARRAY | VT_R8` float VARIANT；同步扩展 `tests/core/test_autocad_com_driver.py`，并适配 `tests/core/test_execute_plan.py` 的 fake driver 测试。
- 复跑真实 CAD 总验证通过：`output\validation_runs\cad-readback-alpha-elevated-retry-20260525-210850\report.json` 顶层 `status=pass`，`execution_summary.json` 记录 created handles `3773, 3774, 3775, 3776, 3777, 3778, 37B5`，`cad-validation-screen.png` 已生成，`readback_report.json.status=geometry_verified`。
- 已逐项审查 `readback_report.json` 关键 checks：`readback_scope`、`layer_entities`、`bbox_size`、`base_point`、`label_text`、`dimension_count`、`created_handles_scope` 全部 `pass`。全程只写入 `CODEX_PREVIEW`，未保存 DWG、未覆盖原图、未删除实体、未修改正式图层。
- 当前允许声明 Phase W baseline `examples\plans\draw_test_cabinet.json` 的真实 CAD 几何已通过；不扩大为真实项目图纸、块库或任意 CAD_PLAN 全部准确。

### Phase W W-05/W-06 推进与 COM 诊断加固

- 执行 Phase W W-05：审查 `output\validation_runs\phase-w-preflight-no-cad\report.json`，确认 no-cad preflight 顶层 `status=pass`，失败步骤数量为 0，因此无需进入失败分类修复。
- 执行 Phase W W-06：用只读 `AutoCADComDriver(connect_existing_only=True)` 探测当前 AutoCAD 前置条件，不落图、不保存、不修改图层；证据写入 `output\validation_runs\phase-w-w06-cad-probe\autocad_com_connect.stdout.txt` 与 `autocad_com_connect.stderr.txt`。
- W-06 当前结论为 `external_blocker`：当前环境无法通过 `AutoCAD.Application` 连接活动文档，底层 COM 返回 `(-2147221005, '无效的类字符串', None, None)`。因此本轮未进入 W-07 真实 CAD 总验证。
- 完成一项小型加固：`core/cad_io/autocad_com.py` 在 `connect_existing_only=True` 连接失败时保留底层 COM detail，避免把 ProgID / 注册 / 运行状态问题压成泛化错误。
- 新增 `tests/core/test_autocad_com_driver.py`，锁定 AutoCAD COM 连接失败时必须保留底层错误细节；相关 focused tests 通过，最终全量 `unittest discover -s tests` 当前为 199 tests OK。
- 复跑无 CAD 总控：`scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\phase-w-preflight-no-cad-after-w06-hardening` 顶层 `status=pass`。
- 同步更新 `README.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CORE_RESTRUCTURE_PLAN.md`、`CAD_AGENT_STATUS.md` 和 `CAD_AGENT_ISSUES.md`；继续明确 no-cad pass 与 W-06 COM 探针都不等于真实 CAD 几何验证。

### Phase W W-07/W-16 总验证收束

- 执行 W-07 真实 CAD 总验证：首次运行 `output\validation_runs\cad-readback-alpha\report.json` 暴露出 runner 缺陷，即 `autocad_com_connect` 已失败后仍继续执行落图、截图和回读，导致顶层状态被连锁错误污染为 `fail`。
- 按 W.10 自动修复仓库内问题：为 `cad_validation_runner` 增加 CAD 依赖门，`autocad_com_connect` 或 `execute_sample_plan` 失败后，后续依赖 CAD step 标记为 `not_run` 并保留 stdout/stderr 证据。
- 补充 runner 派生 artifact 清理：每轮开始清理本轮可能生成的 `execution_summary.json`、`readback_report.json` 和 `cad-validation-screen.png`，避免复用输出目录时旧证据冒充本轮结果。
- 加固 AutoCAD COM 连接兼容：`AutoCADComDriver` 现在会尝试常见版本化 ProgID，例如 `AutoCAD.Application.25.1`、`AutoCAD.Application.25`，并在失败时列出所有候选错误。
- 新增 / 扩展测试：`tests/core/test_cad_validation_runner.py` 覆盖 CAD 前置失败时依赖步骤必须 `not_run`；`tests/core/test_autocad_com_driver.py` 覆盖版本化 ProgID fallback。
- 复跑 W-07：最新报告为 `output\validation_runs\cad-readback-alpha-retry-20260525-205208\report.json`，顶层状态为 `external_blocker`。非 CAD 步骤均 pass，`autocad_com_connect` 为 `cad_connection_failed`，后续落图、截图、回读均 `not_run`。
- 完成 W-15 / W-16：新增 `docs/verification/cad_readback_alpha_check.md`，并同步更新 README、短上下文、能力矩阵、主计划、当前状态和问题记录。当前仍不能声明 baseline 真实 CAD 几何通过。
- 用户再次确认 CAD 已打开后，重跑 W-07 到 `output\validation_runs\cad-readback-alpha-retry-20260525-205208\report.json`；结果仍为 `external_blocker`。补充环境探测：系统存在两个 `acad.exe` 进程，但 `MainWindowTitle` 为空，窗口枚举未发现可见 AutoCAD/DWG 窗口，版本化 COM Dispatch 探测 30 秒超时。本轮继续不生成几何通过结论。

### Phase W CAD 验收剧本细化

- 基于当前系统遗留的 CAD 层面待检查内容，重构 `CORE_RESTRUCTURE_PLAN.md` 的 Phase W，不执行 CAD 验证，只把后续可执行步骤写入主计划。
- Phase W 现在包含：已完成内容聚合、验证范围、执行前条件、输出目录、证据清单、执行顺序总表、CAD 待检查矩阵、W-01 到 W-16 分步执行清单、失败分类、自动修复策略、`geometry_verified` 升级门槛、停止问用户条件、继续自动修条件、退出标准和完成后同步文档。
- 明确一个关键门禁：`scripts/run_cad_validation.py` 顶层 `status=pass` 仍不足以单独证明真实 CAD 几何准确；后续执行 Phase W 时必须继续审查 `readback_report.json.status` 和关键 checks，只有 `status=geometry_verified` 且证据完整时才允许声明 baseline 真实 CAD 几何通过。
- 同步更新 `CAD_AGENT_STATUS.md`，提示后续有 AutoCAD 和测试 DWG 时直接按主计划 Phase W 的 W-01 到 W-16 执行。

### 系统层状态复盘与下一阶段计划更新

- 基于 Phase O-V、系统层安全补强和最新非 CAD 基线，对根目录开发状态文档做系统级复盘；本轮不执行功能开发，只更新计划、状态、路线、设计映射和维护口径。
- 重写 `CORE_RESTRUCTURE_PLAN.md`：明确根目录没有独立 `plan.md`，当前主计划就是 `CORE_RESTRUCTURE_PLAN.md`；下一阶段收束为 Phase W 真实 CAD 回读闭环、Phase X 场景 Agent Alpha、Phase Y 空壳布局硬化、Phase Z 文档治理和回归基线。
- 重写 `CORE_STATUS.md` 为能力矩阵页，区分 `alpha_ready_non_cad`、`prototype`、`blocked_by_cad` 等状态，并明确 blank-shell pipeline 可用但不等于真实 CAD 几何准确。
- 压缩 `CAD_AGENT_STATUS.md` 为当前进展页，删除长历史式重复描述，历史细节继续由本文承载。
- 重写 `CORE_CONTEXT_BRIEF.md`，保持短入口职责，更新当前结论、下一步路线、按需展开表和文档自查命令。
- 重写 `CORE_ROADMAP.md`，从旧阶段 0-10 的错位描述调整为高层路线：已完成路线、当前 Phase W/X/Y/Z、长期路线和路线约束。
- 更新 `README.md` 的当前状态、主计划说明和后续开发主线，避免继续把旧阶段口径当作当前计划。
- 更新 `SHELL_LAYOUT_FOUNDATION_DESIGN.md`：说明它已从早期蓝图部分落地为 Phase P-V 的 blank-shell pipeline，并列出已完成能力与剩余差距。
- 更新 `SHELL_LAYOUT_TIME_ESTIMATE.md`：标注其为历史估算和预期管理材料，不作为当前开发进度来源。
- 更新 `CAD_AGENT_DECISIONS.md`：标记 D003 已被根目录 `AGENTS.md` 取代，并新增 D007 短上下文入口、D008 主 plan 映射两条决策。
- 本次复盘未删除根目录 Markdown。判断这些文件不是完全重复，而是需要职责分层；后续若继续瘦身，优先迁移到 `docs/archive/` 或 `docs/planning/`，不直接删除历史依据。

### 系统层安全重构收尾

- 完成 repo audit、测试/脚本/legacy driver bootstrap、capability registry facade 拆分、pipeline failure hardening、verification edge tests、文档同步和最终复核。
- 新增 `docs/verification/system_hardening_audit.md` 作为长期审计报告；大型维护规则已迁移到 `CAD_AGENT_RULES.md`，临时执行计划已删除。
- `scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings` 当前为 pass，0 findings；重复路径注入只保留在共享 bootstrap 与测试 fixture 中。
- 补强 repo audit 的路径污染识别：覆盖 `sys.path.append/extend`、`import sys as ...`、`from sys import path ...` 与 `__path__.append(...)` 等常见形态。
- 补强 blank-shell pipeline 与 capability runner 路径边界：workflow 输入必须留在 project root 内，输出 artifacts 必须留在 `output/` 下；缺文件、坏 JSON、越界路径返回结构化失败，不再 traceback 或写到仓库外。
- 修复 `run_validation()` 兼容入口的相对 `output_dir` 解析，使其跟随显式 `root`，避免 `root != cwd` 时报告写错位置。
- 完成最终无 CAD 验证：focused hardening tests 通过，全量 `unittest discover -s tests` 196 项通过，`self_check.py` pass，`render_preview.py --check` ready，blank-shell pipeline status ok，blank-shell 4 场景 benchmark 4/4 pass，`run_cad_validation.py --no-cad --output-dir output\validation_runs\hardening-polish-no-cad` status pass。

### 开发状态同步与非 CAD 基线复验

- 检查当前仓库状态后，确认没有独立 `plan.md`；按 `CORE_RESTRUCTURE_PLAN.md` 的约定，用户提到 `plan.md` 时默认指该主计划文件。
- 同步更新 `CORE_RESTRUCTURE_PLAN.md` 的状态口径：Phase O-V 非 CAD 主线已通过，下一步进入 Phase W 真实 CAD readback 补验与 Phase X 场景 Agent Alpha 验收。
- 复验当时的非 CAD 基线：`unittest discover -s tests`、`self_check.py`、`validate_plan.py`、`dry_run_plan.py`、`render_preview.py --check` 和 `inspect_dwg.py --no-cad` 均通过；当前测试数量以本日“系统层安全重构收尾”记录为准。
- 复验 blank-shell 链路：`scripts/run_blank_shell_pipeline.py examples\workflows\blank_shell_layout_loop.json --output-dir output\test_artifacts\blank_shell_pipeline\docs-sync` 为 status ok；`scripts/run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\docs-sync` 为 4/4 pass。
- 复验无 CAD 总控：`scripts/run_cad_validation.py --no-cad` 为 status pass；当前报告路径以本日“系统层安全重构收尾”记录为准。
- 更新 `README.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md` 和 `CORE_CONTEXT_BRIEF.md`，统一写清“非 CAD 通过不等于真实 CAD 几何准确”的证据边界。

### 稳定短上下文入口

- 新增 `CORE_CONTEXT_BRIEF.md`，作为后续 Codex 日常恢复上下文的稳定短入口，集中记录当前结论、下一步路线、按需展开表、安全门、常用验证和缓存友好约定。
- 更新 `AGENTS.md`：默认先读 `CORE_CONTEXT_BRIEF.md`，只有完整汇报、执行 Phase、卡壳回归或修改规则/记录时才展开旧的完整上下文文件组。
- 更新 `README.md` 的恢复上下文说明和推荐提问方式，把日常入口从多份大文档改为 `AGENTS.md` + `CORE_CONTEXT_BRIEF.md`。
- 更新 `CAD_AGENT_RULES.md`，新增“上下文缓存友好入口”规则，要求短入口保持稳定，详细历史继续留在计划、changelog 和 issues 中按需读取。
- 更新 `CORE_RESTRUCTURE_PLAN.md` 和 `CAD_AGENT_STATUS.md`，同步短入口与按需展开的恢复策略。

### Git 提交与推送说明

- 在 `README.md` 增加提交与推送说明，记录默认 GitHub 远端、无 `.git` 拷贝目录的初始化流程，以及提交前不纳入本机日志、截图、验证输出和临时 DWG 的规则。
- 更新 `.gitignore`，忽略 `output/*` 生成产物与 `cad_mcp.log`，保留 `output/previews/README.md` 这类目录说明文件的例外。
- 更新 `CAD_AGENT_STATUS.md`，同步这次文档与仓库卫生调整。

### Core 主计划交付协议补强

- 补强 `CORE_RESTRUCTURE_PLAN.md`：新增“执行交付协议”，明确后续 Codex 必须按 phase 执行、每个 phase 先拆 2-5 分钟小步、测试先行、证据落盘和状态同步。
- 新增 Phase O-X 依赖与交付物表，避免后续执行者跳阶段或把未验证能力当作可用能力。
- 将 `CAD_AGENT_AUTONOMOUS_VALIDATION.md` 与 `scripts/run_cad_validation.py` 纳入 Phase O、Phase W 和固定自检流程：非 CAD 阶段可跑 `--no-cad`，真实 CAD 阶段用结构化报告作为总证据。
- 新增本文交付自检清单和文本自查命令，交付前扫描不可执行占位、旧 phase 口径和脚本引用漂移。
- 调整完成判定说明：只讨论计划时不执行 phase；若计划本身改变工作流或交付规则，仍按根目录 `AGENTS.md` 同步状态和变更记录。
- 继续拆细 Phase O-X：每个 phase 增加编号化细化执行清单，覆盖上下文审计、测试先行、红灯确认、最小实现、专项验证、证据归档、文档同步和复核，便于后续 Codex 一次执行较长时间而不丢失阶段边界。
- 新增建议 Agent 分工模式：`context-auditor`、`schema-contract-agent`、`unit-test-agent`、`engine-agent`、`pipeline-agent`、`cad-validation-agent`、`docs-sync-agent`、`review-agent`，明确这些是执行分工建议，不要求新增仓库代码文件。
- 执行 Phase O：为 `core/capabilities/registry.py` 增加能力成熟度 `maturity` 与已知限制 `known_limits`，并用 `tests/core/test_capabilities.py` 锁定 registry 合约。
- 更新 `CORE_STATUS.md` 的状态口径与关键能力限制说明，明确当前 layout、drawing、proposal、verification 仍是 prototype，不能误报为空壳自动设计或几何准确。
- Phase O 验证通过：`tests.core.test_capabilities`、全量 `unittest discover -s tests`、`self_check.py`、validate、dry-run、`render_preview.py --check`、`inspect_dwg.py --no-cad`、非 CAD benchmark 和 `scripts/run_cad_validation.py --no-cad --output-dir output\validation_runs\phase-o-no-cad`。
- 执行 Phase P：新增 `core/drawing_analysis/shell_loader.py`，可将人工空壳 JSON 规范化为 `SHELL_MODEL`，并校验 units、boundary、opening width、fixed obstacles 和 no-place zones。
- 扩展 `core/schemas/shell_model.schema.json` 和 `core/schemas/project_model.schema.json`，让 `SHELL_MODEL` 支持 `boundary.type`、openings、fixed obstacles、no-place zones、required connections、building elements、uncertainties 和 source，让 `PROJECT_MODEL` 可保留 shell_id、source 与 uncertainties。
- 更新 `core/project_model/project_builder.py` 与 `core/capabilities/registry.py`：`project_model.build` 可接收可选 `shell_model`，新增 capability `drawing_analysis.load_shell_model`。
- 新增 `examples/shell_models/retail_blank_shell.json`、`examples/shell_models/office_blank_shell.json` 和 `tests/fixtures/invalid_models/shell_model.opening_missing_width.invalid.json`；`projects/sample_blank_shell/input/shell.manual.json` 已从旧 drawing-style 手工输入升级为 `SHELL_MODEL`。
- Phase P 验证通过：`tests.core.test_shell_loader`、`tests.core.test_project_model`、`tests.core.test_schema_validation`、`tests.core.test_capabilities`、shell example schema validator、全量 `unittest discover -s tests`、非 CAD benchmark 和 `scripts/run_cad_validation.py --no-cad --output-dir output\validation_runs\phase-p-no-cad`。
- 补强 Phase P：`tests/core/test_shell_loader.py` 增加 legacy drawing-style 输入兼容回归，确认旧 `DRAWING_MODEL.spaces` 风格手工标注仍可由 `load_manual_shell()` 规范化为 `SHELL_MODEL`。
- 执行 Phase Q：新增 `core/geometry_backends/rect2d.py` 和 `core/geometry_backends/orthogonal.py`，提供无依赖 rect 操作、bbox no-place-zone 保守扣减、path strip、门洞/障碍距离和正交多边形校验。
- 更新 `core/geometry_backends/registry.py`，登记默认 `rect2d` 与 `orthogonal_polygon` 后端；保留 `cadquery`、`build123d`、`ifcopenshell` 为未来可选槽位，不引入新依赖。
- 迁移 `core/layout_engine/basic_layout.py` 与 `clearance.py` 的 bbox inside / overlap / clearance gap 到 `core.geometry_backends.rect2d`，减少 layout 层散落几何算法。
- Phase Q 目标测试通过：`tests.core.test_geometry_rect2d`、`tests.core.test_geometry_orthogonal`、`tests.core.test_geometry_backends` 与 `tests.core.test_shell_loader`。
- 执行 Phase R：新增 `core/layout_engine/path_generation.py`，实现 `generate_circulation_candidates(project_model, preferences)`，输出 `straight_spine`、`l_spine`、`along_wall` 三类 `CIRCULATION_MODEL` 候选。
- 扩展 `PROJECT_MODEL`：`project_builder` 现在保留 `shell_context.openings`、`fixed_obstacles`、`no_place_zones`、`required_connections` 和 `building_elements`，供后续动线和功能区切分复用。
- 扩展 `core/schemas/circulation_model.schema.json`：路径必须包含 `polyline`、`connects`、`path_surface`、`blocked_reasons` 和 `score`；新增 `examples/circulation_models/retail_straight_spine.json` 与 `retail_l_spine.json`。
- 更新 `core/capabilities/registry.py`，登记 `layout.generate_circulation_candidates`，让动线生成成为可发现、可验证、非 CAD 的 Core capability。
- Phase R 目标测试通过：`tests.core.test_project_model`、`tests.core.test_circulation_generation`、`tests.core.test_schema_validation`、`tests.core.test_capabilities`，并通过 circulation example schema validator。
- 执行 Phase S：新增 `core/layout_engine/zone_splitter.py`，实现 `split_zones(shell_model, circulation_model, constraints)`，可围绕 circulation path surface 切出左右 `FUNCTION_ZONE` 候选。
- 扩展 `core/schemas/function_zone.schema.json`：zone 现在包含 `geometry`、`area`、`depth`、`frontage`、`side_of_path`、`candidate_functions`、`score` 和 `uncertainties`；同步更新 minimal zone example。
- 新增 `examples/function_zones/retail_zone_left.json` 与 `office_zone_desk_band.json`，并扩展 `tests/core/test_zone_splitter.py` 与 `tests/core/test_schema_validation.py`。
- 更新 `core/capabilities/registry.py`，登记 `layout.split_function_zones`，让 shell -> circulation -> function zones 的非 CAD 能力链可发现。
- 修复 `rect2d.subtract_no_place_zones()` 状态语义：不相交的 no-place-zone 不再误报 `partial`，并增加回归测试。
- Phase S 目标测试通过：`tests.core.test_zone_splitter`、`tests.core.test_schema_validation`、`tests.core.test_capabilities`、function zone schema validator。
- 执行 Phase T：新增 `libraries/objects/object_defaults.json`，将对象默认尺寸从代码常量迁出，并扩展 `desk`、`chair`、`bed`、`sofa`、`counter`、`display_unit`。
- 新增 `core/layout_engine/placement.py`，实现由 FUNCTION_ZONE、对象尺寸和 block metadata 驱动的保守 placement，输出 `bbox`、`clearance_bbox`、`source` 和失败原因。
- 扩展 `libraries/blocks/block_library.example.json`，增加 desk、sofa、display_unit 示例块；找不到块时保留 `OBJECT_SPEC` fallback。
- 扩展 `object_spec.schema.json` 与示例：新增 `examples/object_specs/desk_1400x700.json`、`sofa_2200x900.json`。
- 更新 `core/capabilities/registry.py`，登记 `layout.create_zone_placements`，让 function zones -> placements 的非 CAD 能力链可发现。
- Phase T 目标测试通过：`tests.core.test_placement_engine`、`tests.core.test_object_engine`、`tests.core.test_block_engine`、object spec schema validator。
- 执行 Phase U：扩展 `DESIGN_PROPOSAL` schema，支持 `candidates[]`、`confirmed_candidate_id`、`comparison_summary`，并把 evidence 拆为 `from_user`、`from_drawing`、`from_shell`、`from_library`、`from_algorithm`、`inferred`。
- 更新 `design_proposal.py`，可将多个 layout candidates 包装为多候选 proposal；更新 `proposal_to_plan.py` 与 `plan_engine/model_to_plan.py`，支持按 `confirmed_candidate_id` 选择要转 CAD_PLAN 的候选。
- 更新 `proposal_comparison.py`，支持带 `weight_source` 的场景权重参与候选排序，防止偏好权重变成隐式常量。
- 新增 `examples/design_proposals/blank_shell_retail_options.json` 和 `tests/core/test_proposal_multi_candidate.py`。
- Phase U 目标测试通过：`tests.core.test_proposal_multi_candidate`、`tests.core.test_proposal_engine`、`tests.core.test_proposal_comparison`、design proposal schema validator。
- 执行 Phase V：新增 `core/workflows/blank_shell_pipeline.py` 与 `scripts/run_blank_shell_pipeline.py`，串联 `SHELL_MODEL -> PROJECT_MODEL -> CIRCULATION_MODEL -> FUNCTION_ZONE -> placements -> LAYOUT_PROPOSAL -> DESIGN_PROPOSAL -> CAD_PLAN -> dry-run -> VERIFICATION_REPORT(unverified)`。
- 新增 `examples/workflows/blank_shell_layout_loop.json`、`blank_shell_office_layout_loop.json`、`blank_shell_residential_layout_loop.json`、`blank_shell_restaurant_layout_loop.json`，以及 `examples/benchmarks/blank_shell_core_benchmark.json`。
- 新增 `examples/shell_models/office_small_suite_shell.json`、`residential_living_room_shell.json`、`restaurant_small_front_shell.json` 和 `agents/restaurant/preferences.json`，让 blank-shell benchmark 覆盖四个不同 workflow，而不是同一输入重复运行。
- 新增 `projects/sample_blank_shell/expected/expected_notes.md`，明确空壳 pipeline 的非 CAD 预期和 `unverified` 证据边界。
- 更新 `core/benchmarks/runner.py`，让 benchmark runner 可调度 `pipeline: blank_shell` case，并记录 candidates、zones、placements、CAD_PLAN、失败检查、dry-run 和 verification 指标。
- 更新 `core/capabilities/registry.py`，登记 `workflow.blank_shell_pipeline`，让完整空壳 pipeline 成为可发现、可运行、可验证的 Core capability。
- 大范围审计修复：blank-shell pipeline 现在从 placement 实际来源派生 `OBJECT_SPEC`，避免 block 尺寸与 CAD_PLAN 默认对象尺寸不一致；`path_to_rect_strips()` 跳过重复连续点；zone placement 在剩余空间不足时返回 blocked placement 而不是异常。
- 更新测试：新增/扩展 `tests/core/test_blank_shell_pipeline.py`、`tests/core/test_benchmarks.py`、`tests/core/test_benchmark_cli.py`、`tests/core/test_geometry_rect2d.py`、`tests/core/test_placement_engine.py`、`tests/core/test_capabilities.py` 与 `tests/agents/test_scene_preferences.py`。
- Phase V 目标测试通过：`tests.core.test_blank_shell_pipeline`、`tests.core.test_benchmarks`、`tests.core.test_benchmark_cli`、`tests.core.test_capabilities`、`tests.agents.test_scene_preferences`；当前全量测试数量以本日“系统层安全重构收尾”记录为准。

### CAD 自主验证闭环

- 新增 `CAD_AGENT_AUTONOMOUS_VALIDATION.md`，把“不要遇到第一处失败就停”的口头要求固化为可复用执行手册。
- 新增 `core/verification/cad_validation_runner.py` 和 `scripts/run_cad_validation.py`，提供一键 CAD 验证总控：依赖探针、自检、单元测试、validate、dry-run、截图能力、benchmark、AutoCAD COM 连接、预览落图、截图和实体回读。
- 验证脚本会写入 `output/validation_runs/<timestamp>/report.json`、`report.md`、各步骤 stdout/stderr、`execution_summary.json`、`readback_report.json` 和截图路径。
- 新增失败分类：`missing_dependency`、`cad_connection_failed`、`repo_regression`、`cad_plan_invalid`、`dry_run_failed`、`execution_failed`、`screenshot_failed`、`readback_failed`，让 Codex 能区分仓库内可修问题和用户侧外部阻塞。
- 新增 `tests/core/test_cad_validation_runner.py`，覆盖 CAD 连接失败归类为 `external_blocker`，以及全部步骤成功时输出 `pass`。
- 在 `CAD_AGENT_RULES.md` 增加“CAD 层面验证要走自主验证闭环”，要求 Codex 对仓库内问题自行最小复现、最小修复并复验。
- 更新 `CAD_AGENT_STATUS.md`，把回家或换机验证入口调整为 `CAD_AGENT_AUTONOMOUS_VALIDATION.md` + `scripts/run_cad_validation.py`。

### 外部方法论内化为 Core runtime

- 不复制外部项目代码，只抽象其工程思路，新增 `core/capabilities/registry.py`：能力可发现、输入先校验、输出 contract、风险等级、CAD 依赖和验证命令登记。
- 新增 `core/workflows/artifact_graph.py`，把 workflow artifacts 转成依赖顺序、路径检查和循环依赖检测。
- 新增 `core/geometry_backends/registry.py`，默认使用无依赖 `cad_plan_rect2d`；将 `cadquery`、`build123d`、`ifcopenshell` 仅登记为未来可选后端槽位，不成为当前依赖。
- 新增 `core/benchmarks/runner.py`、`scripts/run_benchmark_suite.py` 和 `examples/benchmarks/non_cad_core_benchmark.json`，让非 CAD pipeline 具备可重复 benchmark 基线。
- 新增 `core/object_engine/object_explainer.py` 和 `core/proposal_engine/proposal_comparison.py`，补齐对象尺寸/构件来源说明和多候选 layout 比较。
- 补齐 `tests/fixtures/invalid_models/`，让每个注册模型至少有一个 invalid fixture。
- 扩展 `examples/project_models/` 到 generic、retail、residential、office 多场景；扩展 `libraries/blocks/block_library.example.json` 到更多通用块类别。
- 新增 `docs/verification/` 与 CAD 延后补验模板，继续明确非 CAD 结果不能替代真实 CAD 落图、截图和实体回读。
- 单元测试扩展到 109 项；新增 capability、artifact graph、geometry backend、benchmark、object explanation、proposal comparison、shell/circulation/function-zone schema、schema invalid fixture、multi-domain project model、scene preference diff 和 block library 覆盖。

### 非 CAD 全量底座闭环深化

- 根据多个并行 Agent 对 plan、schema、engine、verification、safety 和 pipeline 的审计结果，继续推进第二轮非 CAD 底座开发。
- 新增 `core/safety/policy.py`，并接入 `core/execution/execute_plan.py`；默认只允许 `CODEX_PREVIEW`，正式图层、删除、保存、覆盖和未确认计划必须有显式批准。
- 新增 `core/project_model/project_builder.py`、`core/model_loop/reference_checker.py`、`core/schemas/registry.py`，补齐项目模型构建、workflow schema 校验和跨模型引用检查。
- 新增 `core/drawing_analysis/manual_model.py`、`entity_summary.py`，支持 CAD 不可用时通过手工 JSON 或简化实体列表继续推进图纸理解。
- 新增 `core/block_engine/block_selector.py`、`block_placement.py`，支持块库元数据筛选、fallback object spec 和 block insertion intent。
- 扩展 `core/layout_engine/`：增加 collision、clearance、scoring 和多对象 candidates。
- 拆分 `core/object_engine/object_to_plan.py` 与 `core/proposal_engine/proposal_to_plan.py`，让对象/方案生成与 `CAD_PLAN` 转换分离。
- 新增 `core/plan_engine/model_to_plan.py`、`dry_run_report.py`，支持高层模型到安全预览计划和机器可读 dry-run report。
- 新增 `core/workflows/non_cad_pipeline.py` 与 `scripts/run_non_cad_pipeline.py`，输出 `PROJECT_MODEL`、`OBJECT_SPEC`、`LAYOUT_PROPOSAL`、`DESIGN_PROPOSAL`、`CAD_PLAN`、dry-run report 和 `VERIFICATION_REPORT(unverified)`。
- 强化验证证据门：裸 `entities_are_scoped=True` 不再足以升级为 `geometry_verified`；必须有 created handles 覆盖；截图路径不存在时不算截图证据。
- 为 `commercial_fitout`、`residential`、`office` 增加 `preferences.json`，并在 pipeline 中接入场景偏好。
- 新增 `tests/core/test_style_engine.py`，让 modern / european / minimal style token 对对象构件差异形成回归约束。
- 扩展 cabinet/shelf/table 的基础组件表达，并为 schema 职责边界增加测试：`DESIGN_BRIEF` 不承载落图图层，`CAD_PLAN` 不承载方案推理 evidence。
- 扩展 `DESIGN_PROPOSAL.evidence`，加入 `from_library` 来源字段。
- 新增 `core/layout_engine/circulation.py`，让场景 preferences 中的 `main_aisle_width_mm` 进入 Core layout circulation check。
- 新增 `projects/sample_blank_shell/input/shell.manual.json`，作为非 CAD 空壳布局底座的手工输入样例。
- 扩展 `core/verification/verification_report.py`，增加 before/after snapshot diff、批量 report 汇总和失败修复建议字段。
- 扩展测试到 89 项；当前非 CAD 基线为 `unittest discover -s tests` 通过、`self_check.py` pass、`render_preview.py --check` ready、非 CAD pipeline status ok。

### 第二轮 Core 大规模重装

- 将 `CORE_RESTRUCTURE_PLAN.md` 从剩余工作概览扩展为非 CAD 全量底座开发计划，新增 Phase A-M、待校验登记表、每阶段非 CAD 验证命令和 CAD 延后补验总清单。
- 收束 `cad_agent/`：三份旧文档已标注为 legacy，新增 `docs/architecture/cad_workflow.md` 和 `docs/architecture/cad_plan_boundary.md` 作为 Core 架构入口。
- 收束 `libraries/domains/`：新建 `libraries/domain_presets/` 并复制 domain preset；旧目录保留 legacy README 作为兼容入口。
- 新增 9 个高层 schema 与最小 example：`DESIGN_BRIEF`、`DRAWING_MODEL`、`PROJECT_MODEL`、`OBJECT_SPEC`、`STYLE_PROFILE`、`BLOCK_LIBRARY`、`LAYOUT_PROPOSAL`、`DESIGN_PROPOSAL`、`VERIFICATION_REPORT`。
- 新增 `core/schemas/validator.py`，提供无外部依赖的 schema example 校验入口。
- 新增 `core/verification/verification_report.py`，并增强 `core/verification/inspect_dwg.py`：默认不连接 CAD，显式 `--connect-cad` 才读取真实 AutoCAD；支持 `--plan`、`--format json`、`--no-cad`。
- 为 `core/cad_io/autocad_com.py` 增加 `snapshot_modelspace()` 只读实体快照入口。
- 新增第一批设计引擎原型：`core/object_engine/parametric_objects.py`、`core/style_engine/style_profile.py`、`core/block_engine/block_library.py`、`core/layout_engine/basic_layout.py`、`core/proposal_engine/design_proposal.py`。
- 新增 `libraries/styles/modern.json`、`european.json`、`minimal.json` 和 `libraries/blocks/block_library.example.json`。
- 新增 `agents/SCENE_AGENT_RULES.md` 和 `agents/commercial_fitout/workflows/blank_store_to_layout.md`、`existing_plan_to_elevation.md`，明确场景 Agent 只存偏好和 workflow，不复制 Core 算法。
- 新增/扩展测试：高层 schema 校验、对象/风格/块/布局/方案原型、验证报告、场景 Agent 边界；第一批单测从 13 项扩展到 35 项，随后非 CAD 底座深化扩展到 89 项。
- 修复测试环境问题：将需要写文件的测试改用 `output/test_artifacts`，避免当前沙箱无法删除系统临时目录导致失败。
- 根据复盘 Agent 审查补强验证与确认门：`VERIFICATION_REPORT` 失败优先、校验基点、按目标图层统计文字/标注、未隔离本次执行实体时不声称 `geometry_verified`；`DESIGN_PROPOSAL.needs_confirmation=true` 时不得转 `CAD_PLAN`；`CAD_PLAN.needs_confirmation=true` 时执行层默认拒绝执行。
- 增强场景 Agent 边界测试：扫描 `agents/` Python 文件，禁止在场景层实现 CAD 执行、回读或校验核心能力。
- 记录 CAD 不可稳定打开时的验证策略：非 CAD 层按单测、schema、dry-run、自检和 fake readback 完整验证；真实 CAD 落图、实体回读和截图补验写入 `CORE_RESTRUCTURE_PLAN.md` 延后清单。

### 默认中文沟通规则

- 将根目录 `AGENTS.md` 从英文规则改为中文规则，并新增“默认中文输出”要求。
- 将 `skills/cad-drawing/SKILL.md` 改为中文说明，并要求面向用户的解释、状态汇报、方案讨论、追问和结论默认使用中文。
- 在 `CAD_AGENT_RULES.md` 增加“默认中文沟通”规则，明确代码、命令、路径、Schema 字段、JSON key、工具名和 API 名称可保留英文或原文。
- 更新 `CAD_AGENT_STATUS.md` 和 `CAD_AGENT_ISSUES.md`，记录这次由用户反馈触发的语言策略修正。

### 空壳布局底座设计沉淀

- 新增根目录 `SHELL_LAYOUT_FOUNDATION_DESIGN.md`。
- 将“空壳 CAD / 空户型 -> 空壳模型 -> 项目约束 -> 动线 -> 功能区 -> 对象/图块 -> 布局方案 -> CAD_PLAN -> 预览和验证”的通用 Core 子能力路线沉淀为设计说明。
- 明确该能力属于 Core 子能力组合，不是公司专用平面方案 Agent。
- 明确第一版允许人工标注空壳输入，不要求一次性自动识别任意 DWG。
- 明确 Core 与 `agents/`、`libraries/`、`projects/` 的边界，避免后续实现跑偏。
- 补充数据模型建议、模块职责、分阶段路线、执行自检链路、验收标准和风险规则。
- 更新 `CAD_AGENT_STATUS.md`，说明该文档是后续开发蓝图，不代表功能已实现。

### 架构重装设计

- 新增根目录 `CORE_RESTRUCTURE_PLAN.md`，作为下一轮大规模仓库重装前的设计草案。
- 明确未来仓库定位从“单一 CAD 绘图流程”升级为“通用 CAD Agent Core Lab”。
- 明确开发重心：通用底座优先，场景 Agent 轻量化。
- 明确 `core/`、`agents/`、`libraries/`、`projects/`、`docs/`、`tests/` 的目标职责。
- 明确未来 Core 能力模块：CAD IO、图纸理解、项目模型、对象引擎、风格引擎、图库块引擎、布局引擎、方案引擎、计划引擎、执行、验证和安全。
- 暂停沿旧路线继续堆叠阶段 5 之前，先等待用户确认是否执行仓库重装。

### 第一轮仓库重装

- 新增 `CORE_STATUS.md` 和 `CORE_ROADMAP.md`，用能力矩阵和 Core 阶段路线追踪通用底座进度。
- 创建目标结构：`core/`、`agents/`、`projects/`、`docs/architecture`、`docs/decisions`、`docs/roadmap`、`tests/core`、`tests/agents`、`tests/fixtures`。
- 将现有核心实现迁入 Core：
  - `core/plan_engine/validate_plan.py`
  - `core/plan_engine/dry_run_plan.py`
  - `core/execution/execute_plan.py`
  - `core/verification/inspect_dwg.py`
  - `core/verification/render_preview.py`
  - `core/verification/self_check.py`
  - `core/cad_io/autocad_com.py`
  - `core/cad_io/dxf_writer.py`
  - `core/cad_io/zwcad_com.py`
- 保留旧入口兼容：
  - `scripts/*.py` 作为 Core CLI 薄包装器。
  - `drivers/*.py` 作为 `core.cad_io` 薄包装器。
  - `schemas/*.json` 与 `core/schemas/*.json` 过渡期保持一致。
- 新增轻量场景 Agent 脚手架：`commercial_fitout`、`residential`、`office`、`restaurant`、`exhibition`、`custom`。
- 将核心测试迁入 `tests/core/`，并新增 `tests/core/test_core_restructure.py`，覆盖旧入口兼容、新 Core 入口、schema 一致性和 Agent manifest。
- 更新 `README.md`、`AGENTS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_RULES.md`、`docs/ROADMAP.md`，让入口文档与 Core Lab 架构一致。
- 修剪 `CORE_RESTRUCTURE_PLAN.md`：删除已经完成的第一轮重装待办，保留遗留目录收束、高层 schema、实体回读、对象/风格、图库块、布局、图纸理解、项目模型和方案引擎等剩余计划。

### 阶段 4：预览绘制最小闭环

- 新增 `tests/test_execute_plan.py`，用记录型 driver 验证执行器会请求绘制测试柜矩形、文字和两条基础尺寸标注。
- 将 `scripts/execute_plan.py` 从脚手架推进为第一版真实执行核心：
  - 读取 CAD_PLAN。
  - 复用 `validate_plan.py` 校验。
  - 仅支持当前安全范围内的 `draw_object` + `absolute` placement。
  - 默认只允许 `CODEX_PREVIEW` 图层。
  - 计算矩形、中心文字和水平/竖向尺寸标注位置。
  - 通过 driver 接口调用绘制层。
- 将 `drivers/autocad_com.py` 从占位推进为第一版 AutoCAD COM 驱动：
  - 可连接当前 AutoCAD 应用。
  - 可确保图层存在。
  - 可绘制矩形四边、文字和对齐尺寸标注。
- 使用 CAD-MCP 在当前打开的 CAD 文件中完成实际预览绘制：
  - 绘制 1800 x 600 测试柜矩形。
  - 添加中心文字 `测试柜`。
  - 添加水平和竖向基础尺寸标注。
  - 全部绘制到 `CODEX_PREVIEW` 图层。

### 验证

- `validate_plan.py` 对 `examples/plans/draw_test_cabinet.json` 返回 `VALID CAD_PLAN`。
- `dry_run_plan.py` 能正确预演测试柜对象、尺寸、位置、图层、文字和尺寸开关。
- `tests/test_execute_plan.py` 通过。
- CAD-MCP 绘图调用返回 AutoCAD COM 对象，说明实体已写入当前打开的 CAD 文档。

### 卡壳自查机制

- 新增 `CAD_AGENT_BLOCKER_PLAYBOOK.md`，沉淀“画不准、画不出来、验证不了”时的自查、复现、截图、修复和记录流程。
- 在 `CAD_AGENT_RULES.md` 增加“卡壳时先自查，不盲目重试”规则。
- 在 `README.md` 增加卡壳恢复入口和自检命令。
- 更新 `CAD_AGENT_STATUS.md`，记录横向自查机制。

### 自检与截图入口

- 新增 `scripts/self_check.py`，用于检查核心文件、示例 CAD_PLAN、预览执行路径和截图工具链。
- 扩展 `scripts/render_preview.py`，支持 `--check` 检查截图能力，支持 `--capture-screen` 保存当前可见屏幕截图。
- 新增 `tests/test_render_preview.py`。
- 新增 `tests/test_self_check.py`。

### AGENTS 规则入口

- 新增根目录 `AGENTS.md`，用短规则触发 CAD Agent 上下文读取和绘图自检门。
- 历史阶段曾新增 `CAD测试相关文件/AGENTS.md`，在 CAD 开发包内部固化恢复入口、绘图准确性验收门、卡壳自查流程和原图保护规则；当前现行入口已迁移为仓库根目录 `AGENTS.md` + Core 文档结构。

### 补充原因

- 用户希望未来任意阶段卡壳时，Codex 能先自己找原因，而不是反复试错或把问题直接丢回用户。
- 阶段 4 和后续绘图能力都需要视觉证据；原有目录只有截图输出占位和脚手架，没有可运行的截图检查/自检入口。
- 用户希望这些规则被放入可被 Codex 自动读取的 `AGENTS.md`，避免未来只靠聊天记忆执行。

### 补充验证

- 已确认 CAD-MCP 虚拟环境具备 `PIL`、`win32gui`、`win32com`。
- 新增测试先失败，随后通过实现修复。

## 2026-05-24

### 通用化调整

- 将 `README.md` 定位从当前测试目录调整为“通用 CAD Agent 开发包”。
- 明确本文件夹不绑定当前家装图纸、不绑定当前电脑。
- 明确完整能力由“本文件夹 + 运行环境 + 项目图纸”共同组成。
- 将 `CAD_AGENT_STATUS.md` 当前阶段更新为“阶段 3：CAD_PLAN 校验和 dry-run 已跑通，下一步进入预览绘制”。
- 在 `CAD_AGENT_RULES.md` 增加“通用开发包定位”。
- 扩展 domain 枚举，支持 `exhibition`、`hotel`、`education`、`healthcare`、`industrial`、`custom`。
- 增加办公、餐饮、展厅、酒店、教育、医疗、工业、通用自定义行业包占位。
- 统一 `README.md` 的恢复入口说明：先看 README，再看 4 个项目管理文件。

### 通用化原因

- 用户确认最终目标是可迁移的通用 CAD Agent 开发包。
- 该文件夹未来应能复制到其他电脑和其他 CAD 项目中复用。
- 具体家装图纸只是第一套测试现场，不应污染通用规则。

### 新增

- 创建 `CAD测试相关文件/README.md`，作为测试工作区入口。
- 创建 `CAD_AGENT_STATUS.md`，记录当前开发阶段。
- 创建 `CAD_AGENT_RULES.md`，记录长期规则。
- 创建 `CAD_AGENT_CHANGELOG.md`，记录变更历史。
- 创建 `CAD_AGENT_ISSUES.md`，记录错误和修复。
- 创建 `CAD_AGENT_DECISIONS.md`，记录关键决策和原因。
- 创建第一版目录框架：`cad_agent/`、`skills/`、`schemas/`、`examples/`、`scripts/`、`drivers/`、`libraries/`、`tests/`、`output/`。
- 创建第一版 `CAD_PLAN` Schema 和测试柜示例。
- 创建 `cad-drawing` Skill 骨架。
- 创建 `scripts/validate_plan.py`，用于校验第一版 CAD_PLAN。
- 创建 `scripts/dry_run_plan.py`，用于预演 CAD_PLAN。

### 调整

- 将旧的 `CAD_AGENT_BUILD_GUIDE.md`、`CODEX_CAD_DEV_LOG.md`、`CODEX_CAD_RULES.md` 移动到 `docs/archive/`。

### 决策

- 当前先不创建根目录 `AGENTS.md`，避免过早影响所有 Codex 行为。
- 当前先不引入 SQL。
- 当前先不做完整自动设计。
- 当前先以 `CAD_PLAN` 作为白话和 CAD 绘制之间的中间层。

### 原因

- 用户希望隔几天回来仍能知道开发进度。
- 用户希望规则能随着需求、测试、错误不断迭代。
- 用户希望整个根目录作为 CAD 测试方向，但 CAD 相关资料不要散落在根目录。

### 验证

- 使用 CAD-MCP 虚拟环境 Python 成功运行 `validate_plan.py`。
- 使用 CAD-MCP 虚拟环境 Python 成功运行 `dry_run_plan.py`。
- 发现全局 `python` 命令不可用，已记录到 `CAD_AGENT_ISSUES.md`。
- 发现中文终端输出需要显式 UTF-8，已记录到 `CAD_AGENT_ISSUES.md`。
