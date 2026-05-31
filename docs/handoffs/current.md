# 当前交接包窗口
## ARCH-BOUNDARY-HARDENING-01
1. **包名**：`ARCH-BOUNDARY-HARDENING-01`
2. **修改文件列表**：新增 `openspec/changes/architecture-boundary-hardening-01/`、`docs/architecture/current-module-boundaries.md`、`tests/core/test_architecture_boundary_hardening.py`；更新 `docs/architecture/README.md`、`core/verification/render_preview.py`、`tests/core/test_render_preview.py`、状态 / changelog / issues / handoff 索引。
3. **关键设计说明**：本包先做边界收成，不做系统重构 2.0。仓库当前按 `Stable Core`、`Training Experiments`、`Case-Only` 三桶判断；`core/verification/` 后续按 report contract、runner、registry writeback、visual audit 和 CAD/session safety 拆；capability map 后续按 data generator、page shell、display configuration 和 evidence boundary 拆。
4. **新增/修改测试**：新增 `tests/core/test_architecture_boundary_hardening.py`，守护边界快照、README 可发现性、对象资产试点链路、case-run 晋升门槛和 OpenSpec 不替代 `CORE_RESTRUCTURE_PLAN.md`。
5. **实际运行的命令和结果**：`python -m unittest tests.core.test_architecture_boundary_hardening` → 5 tests OK；失败集复测 `tests.core.test_render_preview tests.core.test_self_check tests.core.test_core_restructure` → 19 tests OK；`run_doc_governance_audit.py` → pass；CAD-MCP venv 全量 `unittest discover -s tests` → 1044 tests OK（2 skipped）；CAD-MCP venv `scripts/self_check.py` → pass。
6. **是否运行真实 CAD**：否。
7. **机器可读证据路径**：无新增 `output/validation_runs/**`；OpenSpec 契约在 `openspec/changes/architecture-boundary-hardening-01/`。
8. **结论分类表**：架构边界契约已落地（OpenSpec + docs + tests，geometry_verified=否）；verification / capability-map 大文件实际拆分：本包未做，后续按 split map 小包推进。
9. **剩余风险**：边界快照需要后续拆文件包持续执行；对象资产试点只是候选路线，不代表沙发对象族已经 system_verified。
---
## CAD-ASSET-RAW-INTAKE-AUTO-01
1. **包名**：`CAD-ASSET-RAW-INTAKE-AUTO-01`
2. **修改文件列表**：新增 `core/assets/raw_intake.py`、`scripts/run_asset_raw_intake.py`、`tests/core/test_asset_raw_intake.py`；更新 `core/assets/__init__.py`、asset schema invalid fixtures、`agents/pipeline/*.json`、`docs/training/asset-intake-template.md`、`standard_cad_library_raw/README.md`、资产架构 / 训练 / 计划 / reference README。
3. **关键设计说明**：标准图库 intake 默认由 Agent 扫描 `standard_cad_library_raw/<source_slug>/original/`，从路径、文件名和一句说明推断对象、图纸类型和适用范围；缺失字段保守写 `unknown` / `reference_only` / `agent_inferred`，每个 raw 文件生成单对象 `reference_asset` JSON，不写 `libraries/system_library/`。
4. **新增/修改测试**：新增 `tests/core/test_asset_raw_intake.py`；补齐 asset / retrieval schema invalid fixtures。
5. **实际运行的命令和结果**：`python -m unittest tests.core.test_asset_raw_intake tests.core.test_schema_validation tests.core.test_doc_governance tests.core.test_repo_audit -v` → 46 tests OK；`py_compile` → OK；`scripts/run_doc_governance_audit.py` → pass；`scripts/run_repo_audit.py --max-python-lines 500` → 仅 6 个既有 low `large_python_file` findings。
6. **是否运行真实 CAD**：否。
7. **机器可读证据路径**：无新增 CAD 证据；测试会在 `output/test_artifacts/` 下使用临时目录。
8. **结论分类表**：自动 raw intake CLI / core 已落地（code + tests，geometry_verified=否）；raw scan 仍不是能力证明、不改表 C。
9. **剩余风险**：自动推断可能误判对象或视图类型；不确定项必须保持 `unknown`，真实自产资产仍需后续 promotion gate。
---
## OPENSPEC-CONTRACT-LITE-01
1. **包名**：`OPENSPEC-CONTRACT-LITE-01`
2. **修改文件列表**：新增 `openspec/changes/establish-change-contract-lite/`；更新 `AGENTS.md`、`CORE_RESTRUCTURE_PLAN.md`、`core/maintenance/doc_governance.py`、`tests/core/test_doc_governance.py`、状态 / changelog / handoff 索引。
3. **关键设计说明**：OpenSpec 只作为单个复杂变更的契约层；`CORE_RESTRUCTURE_PLAN.md` 仍是唯一 PlanMD。新增 `check_openspec_contracts()`，阻断根级 `openspec/tasks.md`、缺少主线边界的 config，以及 active change 自称主计划 / 总 backlog。
4. **新增/修改测试**：新增 doc governance OpenSpec 契约测试，覆盖 misuse、config boundary、valid layer 和总报告接入。
5. **实际运行的命令和结果**：先跑新增测试红灯，随后实现后新增测试 4 tests OK；完整验证见本包最终回复。
6. **是否运行真实 CAD**：否。
7. **机器可读证据路径**：OpenSpec change 位于 `openspec/changes/establish-change-contract-lite/`；未新增 `output/validation_runs/**`。
8. **结论分类表**：变更契约能力已接入（docs + governance tests，geometry_verified=否）；CAD 几何能力提升：未做（geometry_verified=否）。
9. **剩余风险**：这是轻量护栏，不是完整 OpenSpec 平台；后续复杂包仍需人工判断是否开 change。
---
## ROOT-MD-CHINESE-NAMES-01
1. **包名**：`ROOT-MD-CHINESE-NAMES-01`
2. **修改文件列表**：重命名根目录 10 个历史 stub：`CAD_AGENT_AUTONOMOUS_VALIDATION.md`→`CAD自动验证入口.md`，`CAD_AGENT_BLOCKER_PLAYBOOK.md`→`CAD卡壳排障入口.md`，`CAD_AGENT_CHANGELOG.md`→`变更记录入口.md`，`CAD_AGENT_ISSUES.md`→`问题风险入口.md`，`CAD_AGENT_RULES.md`→`长期规则入口.md`，`CAD_AGENT_STATUS.md`→`当前状态入口.md`，`CORE_ROADMAP.md`→`路线图入口.md`，`SYMBOL_CORE_01_CAD_SYMBOL_GRAMMAR.md`→`CAD符号语法入口.md`，`TRAINING_ERRORS.md`→`训练错误记录入口.md`，`VISUAL_FIRST_AGENT_PLAN.md`→`视觉优先训练计划入口.md`；更新 `core/maintenance/doc_governance.py`、`tests/core/test_doc_governance.py`、状态 / changelog / handoff 索引。
3. **关键设计说明**：只把人看的根目录历史入口改成中文文件名；`AGENTS.md`、`README.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_STATUS.md` 是机器和仓库约定入口，暂不改名，避免打断恢复链路。
4. **新增/修改测试**：更新 `tests/core/test_doc_governance.py` 的中文 stub 断言。
5. **实际运行的命令和结果**：`python -m unittest tests.core.test_doc_governance -v` → 22 tests OK；`scripts/run_doc_governance_audit.py --fail-on-findings` → pass。
6. **是否运行真实 CAD**：否。
7. **机器可读证据路径**：无新增 `output/validation_runs/**`；验证来自 doc governance CLI 和单测输出。
8. **结论分类表**：根目录历史 stub 文件名已中文化（rename + docs，geometry_verified=否）；训练 / CAD 能力提升：未做（geometry_verified=否）。
9. **剩余风险**：主控入口 `CORE_RESTRUCTURE_PLAN.md` 仍是英文旧名；后续如果要继续现代化，建议单独做“主控计划重命名 / stub 兼容”小包。
---
## DOC-ROOT-HYGIENE-01
1. **包名**：`DOC-ROOT-HYGIENE-01`
2. **修改文件列表**：迁移 `TRAINING_ERRORS.md` 正文到 `docs/training/training-errors.md`；迁移 `VISUAL_FIRST_AGENT_PLAN.md` 正文到 `docs/training/visual-first-agent-plan.md`；根目录两文件保留 stub；更新训练 README、pipeline / learning / precision 文档、pipeline agent 配置、`core/assets/retrieval.py`、`core/maintenance/doc_governance.py`、`semantic_clean_two_seater.py`、状态 / changelog / issues / handoff 索引。
3. **关键设计说明**：根目录只保留控制入口和兼容 stub，训练错因台账和 Visual-First 专项计划回到 `docs/training/`；资产检索优先读取新错因台账，旧根路径只作 fallback；案例脚本不再本地插入 `sys.path`，改运行共享 bootstrap。
4. **新增/修改测试**：无新增测试；复用文档治理和 repo audit。
5. **实际运行的命令和结果**：`run_doc_governance_audit.py` pass；`unittest tests.core.test_doc_governance tests.core.test_repo_audit` 29 tests OK；`py_compile` OK；`run_repo_audit.py --max-python-lines 500` 仍有 6 个既有 low 大文件 findings，raw `sys.path` finding 已消失。
6. **是否运行真实 CAD**：否。
7. **机器可读证据路径**：无新增 `output/validation_runs/**`；主要为文档路径和审计命令输出。
8. **结论分类表**：根目录训练长文已迁入 `docs/training/`（docs / governance，geometry_verified=否）；案例脚本 raw `sys.path` 债已清理（code / repo audit，geometry_verified=否）。
9. **剩余风险**：大文件拆分仍有低优先级结构债；本包不做 Core 大重构，也不改变表 C。
---

## CAPABILITY-MAP-HTML-01
1. **包名**：`CAPABILITY-MAP-HTML-01`
2. **修改文件列表**：新增 `capability-map.html`；更新 `README.md`、`CORE_CONTEXT_BRIEF.md`、`docs/status/current.md`、`docs/status/changelog.md`、`docs/status/issues.md`、`docs/handoffs/current.md`、`docs/handoffs/package-index.md`。
3. **关键设计说明**：页面只展示具体图块和基础绘图能力的覆盖清单。V1 能力项包括沙发、茶几、餐桌、床铺、衣柜、墙体绘制、门窗绘制、简单尺寸标注等；左侧清单本身就是计划，右侧阶段列为标准图库、常识整理、训练通过、自产资产。当前未开始标准图库训练，因此右侧阶段默认全空。
4. **新增/修改测试**：无单元测试；这是静态 HTML 页面。
5. **实际运行的命令和结果**：已做静态 HTML 检查和浏览器打开验证；未运行 CAD 测试。
6. **是否运行真实 CAD**：否。
7. **机器可读证据路径**：无新增 `output/validation_runs/**`；页面文件为 `capability-map.html`。
8. **结论分类表**：能力覆盖清单 V1 已创建（HTML / docs，geometry_verified=否）；已训练出自产资产：未做（geometry_verified=否）。
9. **剩余风险**：页面不是表 C 或证据台账；未来勾选必须由 raw 导入、常识整理、训练通过或 system_library 晋升事实驱动。
---
## CAD-COMMONSENSE-ASSET-DEV-PLAN-01
1. **包名**：`CAD-COMMONSENSE-ASSET-DEV-PLAN-01`
2. **修改文件列表**：新增 `docs/planning/cad-commonsense-asset-dev-plan-01.md`；新增 `standard_cad_library_raw/README.md` 与 `standard_cad_library_raw/.gitignore`；更新 `libraries/reference_library/README.md`、`docs/architecture/cad-asset-intelligence-architecture.md`、`README.md`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md`、状态 / changelog / issues / handoff 索引。
3. **关键设计说明**：按用户新约束，标准 CAD 图库原始文件允许放根目录 `standard_cad_library_raw/` 并进入 git，便于家里和公司迁移；自产图库仍只放 `libraries/system_library/`。raw 文件默认 `reference_only`，必须经过 reference manifest、knowledge summary、executable check、evidence boundary 和 promotion gate，才能晋升为系统资产。
4. **新增/修改测试**：无。本轮是计划书和目录边界，不做测试。
5. **实际运行的命令和结果**：计划书写入后只做文档一致性检查；未运行 unit tests / CAD tests。
6. **是否运行真实 CAD**：否。
7. **机器可读证据路径**：无新增 `output/validation_runs/**`；主要证据为 `docs/planning/cad-commonsense-asset-dev-plan-01.md` 与 `standard_cad_library_raw/README.md`。
8. **结论分类表**：标准图库 raw 目录与自产图库边界已明确（docs，geometry_verified=否）；已导入真实图库或对象族能力已提升：未做（geometry_verified=否）。

9. **剩余风险**：raw 图库进 git 后仍需人工确认来源、授权、体积和批次说明；下一步真正开发常识底座时，应按一个对象族一批次推进。

---

## CAD-ASSET-INTELLIGENCE-FOUNDATION-01

1. **包名**：`CAD-ASSET-INTELLIGENCE-FOUNDATION-01`
2. **修改文件列表**：新增 `libraries/reference_library/`、`libraries/system_library/`、`libraries/knowledge/`、`libraries/benchmarks/`；新增 `core/schemas/reference_asset.schema.json`、`system_asset.schema.json`、`asset_annotation.schema.json`、`asset_promotion.schema.json`、`asset_evidence_boundary.schema.json`、`retrieval_pack.schema.json`；新增 `core/assets/`、`scripts/run_asset_retrieval_pack.py`、`scripts/run_asset_promotion_gate.py`；新增 `agents/pipeline/asset_retriever/agent.json`；新增训练 intake 模板；同步状态、changelog、pipeline 文档和 PlanMD 入口。
3. **关键设计说明**：按用户要求把前五项一起落地，但排除测试。当前实现只做本地 JSON / Markdown 资产检索和保守晋升 gate；`retrieval_pack` 是 `CAD_PLAN` 前的上游契约，promotion gate 只出报告、不自动写回图库。
4. **新增/修改测试**：无。用户明确要求“除了测试”。
5. **实际运行的命令和结果**：未运行 unit tests / CAD tests；仅做非测试类检查。
6. **是否运行真实 CAD**：否。
7. **机器可读证据路径**：无新增 `output/validation_runs/**`；基础入口为 `core/assets/*.py` 与 `scripts/run_asset_*.py`。
8. **结论分类表**：资产目录 / schema / 检索 / Agent / intake / gate 基础版已落地（code + docs，geometry_verified=否）；已导入图库、RAG 或对象族 verified：未做（geometry_verified=否）。

9. **剩余风险**：未写测试、未跑测试；下一包若继续自动化或对象族试点，应补 focused tests 和真实 CAD 证据。

---

## CAD-ASSET-INTELLIGENCE-ARCH-01

1. **包名**：`CAD-ASSET-INTELLIGENCE-ARCH-01`
2. **修改文件列表**：新增 `docs/architecture/cad-asset-intelligence-architecture.md`；更新 `docs/architecture/README.md`、`docs/training/cad-common-sense-upgrade.md`、`docs/training/global-agent-pipeline.md`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/status/current.md`、`docs/status/changelog.md`、`docs/status/issues.md`、handoff 索引。
3. **关键设计说明**：本包把“标准参考图库 → 系统自产图库 → 检索 / 生成 / 审计 / 晋升”定为资产化能力管线。`reference_library` 只作 evidence input；`system_library` 才是 promoted asset，必须有 schema、lineage、check 和 evidence_boundary。图库弱命中时进入探索模式，靠对象语法、参数化变体和审计候选保持创造性。
4. **新增/修改测试**：无。本轮是架构方案固化，不创建目录、不写 schema、不接 RAG、不跑真实 CAD。
5. **实际运行的命令和结果**：只做文档读取、4 个子 Agent 只读评审、Markdown 修改和轻量文本检查；未运行测试。
6. **是否运行真实 CAD**：否。
7. **机器可读证据路径**：无新增 `output/validation_runs/**`。主要证据是架构文档 `docs/architecture/cad-asset-intelligence-architecture.md`。
8. **结论分类表**：

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| CAD 资产智能架构已写入 | 文档 / architecture | 否 |
| 参考图库与自产图库边界已明确 | 文档 / governance | 否 |
| 已导入图库、RAG 或对象族能力 | 未做 | 否 |

9. **剩余风险**：生成架构包不等于方案完成。下一步仍需按小包建目录、写 schema、实现 `retrieval_pack`、调整 Agent manifest、建立训练 intake 和晋升 gate，再用对象族案例与真实 CAD 证据验证。

---

## CAD-COMMON-SENSE-ARCH-01

1. **包名**：`CAD-COMMON-SENSE-ARCH-01`
2. **修改文件列表**：新增 `docs/training/cad-common-sense-upgrade.md`；更新 `docs/training/README.md`、`docs/training/learning-loop.md`、`docs/training/global-agent-pipeline.md`、`docs/training/pipeline-changelog.md`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md`、`docs/status/current.md`、`docs/status/changelog.md`、`docs/status/issues.md`、handoff 索引。
3. **关键设计说明**：只吸收 GitHub 上 4 类项目的方法论，不 clone、不搬代码：`llm-wiki` → 资料沉淀；`step.parts` → catalog-first；`CADTestBench` → 可执行检查；`CADCLAW` → checked / not_checked / assumptions 的证据边界。常识进入系统必须走 `source_note → knowledge_summary → object_or_rule_candidate → executable_check → evidence_boundary`。
4. **新增/修改测试**：无。本轮按用户要求只做架构文档升级，不急着测试。
5. **实际运行的命令和结果**：未运行测试；仅做文档读取、GitHub 方法论梳理和 Markdown 修改。
6. **是否运行真实 CAD**：否。
7. **机器可读证据路径**：无新增 `output/validation_runs/**`。主要证据是 `docs/training/cad-common-sense-upgrade.md` 及训练文档入口。
8. **结论分类表**：

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| CAD 常识底座方法论已写入架构 | 文档 / training architecture | 否 |
| 训练反馈汇报模板已升级 | 文档 / workflow rule | 否 |
| 已导入图库或自动常识学习 | 未做 | 否 |

9. **剩余风险**：这不是能力证明包；后续仍需在新对话里通过对象族测试、训练案例、审计项和真实 CAD 证据，把常识逐步转为可证明能力。普通训练回复应按低噪声模板汇报，不再只堆 handles、arc 数、gap/overlap 数字。

历史见 `archive/2026-05.md`。
