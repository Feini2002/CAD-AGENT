# 架构治理硬化小任务

最后更新：2026-06-07

状态：**ACTIVE-SIDECAR-TASK / 独立小任务进行中**。本文整理本轮对话、CC 审查与临时 doc reviewer 视角形成的治理判断；它不是新的 `PlanMD`，不承载全局 backlog，也不替代已收口的 entrypoint custody 机器包（`config/entrypoint_custody_manifest.json` + audit scripts）。本轮允许把“正在推进此小任务”的事实最小同步到主计划、短上下文、状态、规则和变更记录，但具体任务仍以本文为主。

> ⚠️ 本文自身位于 `docs/planning/`，属于 P3 所述「辅助计划文件」范畴。完成本小任务后，应由用户或后续正式收口包决定是否归档到 `docs/history/completed-plans/`；不得自动删除，也不得长期演化成第二套主线。

## 0. 本轮 doc reviewer 收束

本轮“doc agent”只作为临时文档治理视角，不新增真实 `agent.json`、Prompt Pack 或全局 Agent。它的裁决口径如下：

| 视角 | 结论 |
| --- | --- |
| 应保留 | 先做入口 / schema / 产物盘点，再用 checker 形成 pass/fail；不要一开始大搬迁、大删除或大改 import。 |
| 应吸收 | CC 将三张 manifest 压缩为入口 custody + repo inventory 两类治理对象的方向合理，能减少治理物自身膨胀。 |
| 应纠偏 | “完成后删除本文”过急；本文在小任务执行期间是控制入口，只能在收口后按证据归档。 |
| 应防止 | `pyproject.toml`、repo inventory、schema 单源和入口 custody 都是治理底座，不证明 CAD 能力、不提升表 C、不代表 Agent 任务成熟。 |
| 同步边界 | 只向系统入口文档登记“此小任务进入 active sidecar 阶段”；不改 README 长叙事、不改训练事实源、不刷新工作台派生快照。 |

## 0.1 当前事实校准

| 项 | 当前判断 | 本任务要做什么 |
| --- | --- | --- |
| Python 项目身份 | 当前无 `pyproject.toml` / `requirements.txt`；仓库根有 `package.json`，主要服务 Worker / 工作台 / tooling | 补 Python 依赖和安装身份，同时说明 Node 不是 Core 主体 |
| 本机 CAD-MCP venv | 仍是当前常用验证入口，不能立刻否定 | 新增 launcher / resolver 方案，逐步降低硬编码路径依赖 |
| 入口 custody | 已有 `config/entrypoint_custody_manifest.json`、`scripts/run_entrypoint_custody_audit.py`、`scripts/run_training_report_claim_audit.py` 和 `scripts/run_model_trace_claim_audit.py` | 扩展既有 manifest 和 audit，不另起第二套入口保管账；只对最高风险真实写入入口继续补 runtime guard |
| Schema 单源 | `core/schemas/README.md` 已说明旧 `schemas/` 是兼容副本 | 补漂移检查、同步说明和废弃计划，不把它写成从零权威化 |
| Repo inventory | 尚无统一 repo inventory manifest | 建议新增 `config/repo_inventory_manifest.json`，扫描报告放 `output/diagnostics/**` 或 `output/validation_runs/**` |

## 1. 背景

本轮讨论基于外部审查清单中暴露的若干问题：Python 项目身份缺失、本机 venv 路径硬编码、根目录 `package.json` 造成主体技术栈误读、schema 双源、wrapper / adapter 边界不清、DWG / log / 派生快照污染根目录、多套指标与多层规划文档并存、Markdown 数量膨胀等。

核心判断不是“文件多就是错”，而是：

```text
入口没有统一保管，事实源和派生产物混在一起，声明边界主要依赖文档自觉，而不是机器门禁。
```

因此本小任务不建议马上做大规模搬迁、删除或重命名；优先建立机器可审计的归属、边界和门禁，再逐步治理。

## 2. 目标

用最小改动形成一组可执行的治理硬化任务，使仓库未来能回答四个问题：

1. 每个入口归谁管，能否直接运行，是否必须经过中枢 / lease / custody gate。
2. 每个 schema 的权威来源在哪里，兼容镜像如何防漂移。
3. 每个 DWG、log、派生 JS、output artifact 是事实源、派生物、诊断物、历史证据还是临时产物。
4. 每个进度或能力声明能证明什么，不能证明什么。

## 3. 优先级

### P0：可迁移性与入口保管

- 补 Python 项目身份：建立 `pyproject.toml` 或等价依赖声明，让 Python Core 成为一等公民。
- 降级本机 venv 路径：`pyproject.toml` 声明依赖；新增 launcher / resolver 或脚本入口约定，逐步支持 repo-local `.venv` / 系统 Python / CAD-MCP venv 三类来源。`scripts/_bootstrap.py` 只负责 UTF-8、`sys.path` 和运行时预检，不应被写成解释器选择器。
- 扩展既有入口 custody manifest：在 `config/entrypoint_custody_manifest.json` 上继续覆盖 `scripts/*.py`、关键 `.bat`、Core CLI、Worker / 工作台入口，每个入口登记归属、直跑策略、写入范围、evidence boundary。
- 分阶段处理 hard gate：第一阶段先 manifest + checker；第二阶段只对 CAD 写入、训练沉淀、资产沉淀、registry 写回、保存 DWG、删除实体等最高风险入口补 lease / 参数 hash / fail-closed，不要求全仓脚本一次性接 runtime guard。
- 根 `package.json` 加技术栈边界说明：Node 只服务 Worker、工作台或前端工具；Python 是 Core 主体。

### P1：schema / adapter 边界 + 产物分类（合并）

- 明确 `core/schemas` 为 canonical schema source；根 `schemas/` 只允许作为兼容镜像、历史 shim 或生成产物。
- 对重复 schema 名称建立映射：根 `schemas/cad_plan.schema.json` 与 `core/schemas/cad_plan.schema.json` 必须说明权威版本、同步方式和废弃计划。
- 梳理 `drivers/`：允许保留 compatibility wrapper，但必须声明 adapter 身份，不藏业务逻辑，不绕过 `core/cad_io` 或 Tool Contract。
- 建立统一的 `config/repo_inventory_manifest.json`（合并 schema registry + artifact classification，不拆三张 manifest）：把 DWG、log、`capability-map-data.js`、`output/**`、运行 trace、截图、诊断报告、IDE 临时产物（如 `.cursor/plans/*.plan.md`）分为 `source`、`fact_source`、`derived`、`diagnostic`、`history_evidence`、`temporary`。
- 数据治理状态沿用 `protected`、`candidate`、`blocked`、`derived`：受保护事实源不得清理；候选产物需人审；断链或引用不闭合时 blocked；派生快照不能反向当事实源。
- `config/repo_inventory_manifest.json` 初版应由机器生成、人审核分类边界；扫描报告放 `output/diagnostics/**` 或 `output/validation_runs/**`。生成 inventory 不等于自动移动、删除、忽略或降级任何文件。
- 根目录 DWG 不直接视为源码资产；外部参考图库应进入 reference/raw 边界或 Git LFS / 外部存储策略。
- `capability-map-data.js` 必须标为 generated derived snapshot，不可手改，不可作为训练事实源。
- `cad_mcp.log` 这类进程日志不得进入项目根事实源；应转入 ignored runtime log 或诊断目录。

### P2：规划与文档控制面

- 保留三套成熟度口径，但禁止混用：工程节奏、任务台账、`Core Proof Coverage` 不能互相替代。
- 压缩活跃控制面：`CORE_RESTRUCTURE_PLAN.md` 定路线，OpenSpec 管复杂变更契约，任务台账管 next，状态页管当前事实。
- Phase 文档只做执行剧本，不承载第二套 backlog。
- Markdown 治理先分类再压缩：active control、architecture reference、training source、handoff / changelog、history archive、generated / diagnostic。

## 4. 建议任务切分

| 任务 | 产物 | 验收标准 | 执行方式 |
| --- | --- | --- | --- |
| Python 身份梳理 | `pyproject.toml` + launcher / resolver 约定 | `pip install -e .` 可成功安装依赖；`package.json` 有技术栈边界注释；Node 不再被误认为主体 | agent_assisted（草案需人确认） |
| 入口保管账 MVP | 扩展 `config/entrypoint_custody_manifest.json` + `scripts/run_entrypoint_custody_audit.py` | audit 返回 0 或只保留可解释 warning；每个高风险入口有归属、写入范围和 evidence boundary；未分类入口至少 warning 暴露 | agent_assisted + 机器门禁 |
| 高风险入口 fail-closed 加固 | lease / 参数 hash / guard 接入点 | CAD 写入、训练沉淀、资产沉淀、registry 写回、保存 DWG、删除实体等入口未授权时 blocked | 第二阶段，只覆盖最高风险入口 |
| Schema 单源 + 产物分类（合并盘点） | `config/repo_inventory_manifest.json`（合并 schema registry + artifact classification） | 新 inventory audit 返回 0；`core/schemas` 权威化，根 `schemas` 不独立演化；根 DWG、log、派生 JS、IDE 临时产物角色明确 | 机器生成 + 人审核分类边界 |
| 文档控制面审计 | active / archive / generated 分类报告 | 能指出哪些文件不应承载 next；本文完成治理后由用户或正式收口包决定是否归档到 `docs/history/completed-plans/` | 机器盘点 + 人判断 |

最小验收命令口径：

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_doc_governance_audit.py
& $py scripts\run_entrypoint_custody_audit.py --fail-on-blocked
# 后续新增 inventory audit 后，再补对应命令。
```

## 5. 不做什么

- 不在本小任务里删除 DWG、log、Markdown 或历史证据。
- 不运行 CAD、不新开训练、不刷新训练工作台派生快照、不写训练事实源、不提升表 C。
- 不重命名 `core/` 下大量包，不做大规模 import 迁移。
- 不把所有脚本强塞进 `workflow_routes.json`。
- 不把 `package.json` 删除；Worker / 工作台仍可能需要 Node。
- 不把表 A/B/C 简单合并；只修正语义边界和声明门禁。
- 不因为截图、dry-run、工作台页面或模型 trace 存在，就声明真实 CAD 能力或项目交付能力提升。
- 不新增全局 Agent；治理所需的 checker / linter 全部以脚本形式运行，不登记为 Agent。
- 不产出三张独立 manifest；入口保管和 repo inventory 两张 JSON 封顶，避免 manifest 自身成为维护负担。
- 不让 `config/repo_inventory_manifest.json` 成为新的事实源权力中心；它是索引和分类账，不替代原文件、registry、训练事实源或运行报告。

## 6. 推荐执行顺序

1. 先做只读盘点（机器跑）：入口、schema、产物、活跃文档 → 产出 `config/repo_inventory_manifest.json` 初稿和 `output/diagnostics/**` 报告。
2. 人审核盘点结果，确认分类边界（哪些是 fact_source，哪些是 derived/temporary）。
3. 并行推进两件事：① Python 身份（`pyproject.toml` + bootstrap 解绑）② 入口保管 manifest + checker。
4. 对最高风险入口加 fail-closed 规则：CAD 写入、训练沉淀、资产沉淀、registry 写回。
5. 最后才做体积整理、文档归档、旧 shim 下线；本文是否归档由用户或正式收口包决定。

## 7. 系统同步范围

本轮允许的同步只做“系统知道此小任务进入 active sidecar 阶段”：

| 文档 | 同步内容 |
| --- | --- |
| `CORE_RESTRUCTURE_PLAN.md` | 在未来开发路由中登记本小任务，说明它不抢唯一 PlanMD。 |
| `CORE_CONTEXT_BRIEF.md` | 在短上下文和按需展开中加入本任务入口。 |
| `docs/status/current.md` | 记录当前状态里多了一个治理 sidecar，不改变训练暂停边界。 |
| `docs/status/changelog.md` | 记录本轮文档治理任务启动和同步范围。 |
| `docs/status/issues.md` | 记录防止小任务膨胀成第二套主线的风险。 |
| `docs/planning/任务清单.md` | 增加用户口令和执行台账入口，但不展开成长期 backlog。 |
| `docs/governance/cad-agent-rules.md` | 增加辅助治理任务的边界规则。 |

## 8. 一句话收束

这轮治理的第一目标不是让仓库看起来更少，而是让每个入口、schema、产物和能力声明都能被机器追责。衡量成功的标准不是产出多少 manifest 草案，而是 checker 脚本能否在本地返回 pass/fail——先跑通一个盘点→manifest→checker 的闭环，再往上加复杂度。
