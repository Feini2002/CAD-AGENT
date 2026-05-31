# 通用 CAD Agent 开发包当前进展

最后更新：2026-06-01（架构瘦身与边界加固 01）

本文只保留“现在到哪、证据是什么、风险边界是什么”。历史流水见 `docs/status/changelog.md`，瘦身前全文快照见 `docs/history/snapshots/finished-architecture-2026-05-28/docs__status__current.md`，能力矩阵见 `CORE_STATUS.md`，唯一 `PlanMD` / 主计划见 `CORE_RESTRUCTURE_PLAN.md`。后续任务和优先级只写入 PlanMD，避免状态页变成第二份计划。

## 当前一句话

**Agent 训练期（方案 A）**：主训家装（`docs/training/residential-primary.md`）；案例模板 `projects/residential_training_template/`。Core 与 Lab 三轨已收口；默认 next 是案例 + `feedback.md`，不是 V-PROOF 施工包。

## 默认输出口径

普通最终回复默认不附进度表、表单或表 A/B/C；只有用户明确点名开发状态查询、进度、完整状态、交接、审计、表 A/B/C、表 C、真实 CAD 实力或刷新表 C 时，才展开表格。

## 工具中立口径

训练链路和交接材料面向 Codex、Cursor 及其它同类 agent 工具通用；Phase A 是“一个交互式 Agent 会话按角色分步”，不强制绑定 Cursor 或任一单一软件。

## 表 C 当前机器快照

机器报告：`output/validation_runs/capability-lab/cad_capability_coverage.json`。

| 指标 | 当前值 |
| --- | --- |
| **真实 CAD 实力（主指标）** | **90.99%**，最高 L4 |
| CAD 证明覆盖率 | **90.99%**（333 行；**0 verified + 303 showcase**；25 smoke + 5 deferred） |
| CAD 实力指数 | **93.53%** |
| 场景片段实力（L3+） | **93.62%**（88/94） |
| 展示就绪度 | **90.99%** |

禁止用工程节奏、RCAD 烟囱、截图或 no-CAD benchmark 替代表 C。

## 工程节奏（表 A）

| 指标 | 当前值 |
| --- | --- |
| Core 底座 | **100%**（`docs/verification/core_platform_completion_gate.md`） |
| Agent 多场景 | 约 93% |
| 总进度 | 约 97% |

## 最近有效包

| 包 | 状态 | 证据 | 边界 |
| --- | --- | --- | --- |
| `ARCH-BOUNDARY-HARDENING-01` | 架构瘦身与边界加固契约已落地；明确 Stable Core / Training Experiments / Case-Only 三类边界，并给出 verification、capability-map、对象资产试点和 case-run 晋升门槛；顺手修复截图可选依赖缺失时的降级检测 | `openspec/changes/architecture-boundary-hardening-01/`；`docs/architecture/current-module-boundaries.md`；`tests/core/test_architecture_boundary_hardening.py`；`core/verification/render_preview.py`；目标测试 5 OK；全量 1044 OK（2 skipped） | 这是边界收束包，不是系统重构 2.0；未拆所有大文件、不改变表 C、不运行真实 CAD |
| `REPO-POWER-LOSS-HEALTH-01` | 断电后仓库健康检查已完成；修复 self-check / 单测中的迁移滞后口径 | `git fsck --full --strict --no-dangling` pass；冲突标记扫描无命中；JSON 解析 0 error；`scripts/self_check.py` pass；`unittest discover -s tests` 1039 OK（2 skipped：本机未携带 RCAD-20/21 真实 CAD JSON） | 未伪造真实 CAD 证据；不改变表 C；未触碰用户 DWG；`run_repo_audit.py --fail-on-findings` 仍只报既有低风险大文件 / 大 delta 提示 |
| `CAPABILITY-MAP-TRAINING-WORKBENCH-03` | 能力看板重构为“训练计划表单 + 智能体 Prompt 工作台” | `capability-map.html`、`capability-map-data.js`、`scripts/build_capability_map_data.py`、`output/previews/capability-map-workbench-*-v2*.png` | 只做训练计划、Prompt 契约和可视化口径；训练阶段 / 智能体契约分不等于表 C 或真实 CAD 几何通过 |
| `CAPABILITY-MAP-AGENT-COCKPIT-02` | 能力看板升级为可钻取的智能体控制台 | `capability-map.html`、`capability-map-data.js`、`scripts/build_capability_map_data.py` | 只做前端可视化和数据快照生成；不直接编辑源 JSON/MD、不改变表 C、不替代真实 CAD 验证 |
| `CAD-ASSET-RAW-INTAKE-AUTO-01` | 标准图库自动 raw intake 已落地 | `core/assets/raw_intake.py`、`scripts/run_asset_raw_intake.py`、`tests/core/test_asset_raw_intake.py`、`docs/training/asset-intake-template.md`、`agents/pipeline/*` | 只生成 `reference_only` / `agent_inferred` 资产和标注；不写 `system_library`、不解析 CAD、不改变表 C |
| `ROOT-MD-CHINESE-NAMES-01` | 根目录历史 stub 已改为中文文件名 | `CAD自动验证入口.md`、`CAD卡壳排障入口.md`、`变更记录入口.md`、`问题风险入口.md`、`长期规则入口.md`、`当前状态入口.md`、`路线图入口.md`、`CAD符号语法入口.md`、`训练错误记录入口.md`、`视觉优先训练计划入口.md` | 仅改文件名和文档治理 stub 清单；`AGENTS.md`、`README.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_STATUS.md` 作为机器入口暂不改名 |
| `OPENSPEC-CONTRACT-LITE-01` | OpenSpec 变更契约轻量护栏已接入 | `openspec/changes/establish-change-contract-lite/`、`core/maintenance/doc_governance.py`、`tests/core/test_doc_governance.py` | 只做治理契约；不改 CAD 执行、不改表 C、不替代 `CORE_RESTRUCTURE_PLAN.md` |
| `OPENSPEC-INIT-01` | 根目录 OpenSpec 已初始化，并写入最小配置 | `openspec/config.yaml`、`openspec/changes/.gitkeep`、`openspec/changes/archive/.gitkeep`、`openspec/specs/.gitkeep`；`openspec.cmd list --json` 返回 `{"changes":[]}` | 只作为复杂变更的契约层；不替代 `CORE_RESTRUCTURE_PLAN.md`，不承载第二套主计划；初始化使用 `--tools none`，未自动改写 Codex / Cursor 工具配置 |
| `DOC-ROOT-HYGIENE-01` | 根目录训练长文已迁入 `docs/training/` 并保留兼容 stub；案例脚本 raw `sys.path` 债已改用共享 bootstrap | `docs/training/training-errors.md`、`docs/training/visual-first-agent-plan.md`、`TRAINING_ERRORS.md`、`VISUAL_FIRST_AGENT_PLAN.md`、`projects/residential_sofa_2seat_20260528/runs/semantic_clean_two_seater.py` | 无行为架构重写；不改变表 C；真实 CAD 未运行 |
| `CAPABILITY-MAP-HTML-01` | 根目录能力覆盖清单 V1 已创建 | `capability-map.html` | 只展示具体图块和基础绘图能力的计划覆盖；不展示内部证据路径、不替代表 C、未声明已有自产资产 |
| `CAD-COMMONSENSE-ASSET-DEV-PLAN-01` | 标准图库常识资产开发计划已写入 | `docs/planning/cad-commonsense-asset-dev-plan-01.md`、`standard_cad_library_raw/README.md`、`libraries/reference_library/README.md` | 只是计划和目录边界；未导入真实图库、未生成自产资产、未跑测试、不改变表 C |
| `CAD-ASSET-INTELLIGENCE-FOUNDATION-01` | 资产智能前五项基础版已落地 | `libraries/reference_library/`、`libraries/system_library/`、`libraries/knowledge/`、`libraries/benchmarks/`、`core/assets/`、`scripts/run_asset_retrieval_pack.py`、`scripts/run_asset_promotion_gate.py`、`agents/pipeline/asset_retriever/agent.json` | 未写测试、未跑测试；未导入图库、未接 RAG、未自动晋升、不改变表 C |
| `CAD-ASSET-INTELLIGENCE-ARCH-01` | CAD 资产智能架构已固化 | `docs/architecture/cad-asset-intelligence-architecture.md`、`docs/training/global-agent-pipeline.md`、`CORE_RESTRUCTURE_PLAN.md` | 方案固化；未建目录、未写 schema、未接 RAG、未导入图库、不改变表 C |
| `CAD-COMMON-SENSE-ARCH-01` | CAD 常识底座方法论已写入训练架构 | `docs/training/cad-common-sense-upgrade.md`、`docs/training/README.md`、`docs/training/learning-loop.md`、`docs/training/global-agent-pipeline.md` | 文档级升级；未导入外部图库、未运行测试、不改变表 C |
| `CORE-PLATFORM-100` | Core 平台门禁收口 | `scripts/run_core_platform_gate.py`；969 tests OK | **≠** 表 C 100% |
| `VCAD-ROUND14-VISUAL-FIRST-SOFA` | 家装沙发 round14 已按用户方向常识重画 | 用户认可衔接贴合；中间白线根因是重复共享边；方向错误根因是缺少硬靠背→软靠垫→坐垫的平面图语义；round14 已真实 CAD 重画，54 实体、33 arc、0 gap/overlap/open endpoint | Agent 自检可请用户验收；不改表 C |
| `TABLE-C-20260528-P` | smoke→probe showcase ×17 | **98.42%** | 非负例几何；`real_cad_guard` 仍 smoke |
| `TABLE-C-20260528-O` | core.api non_cad_suite | **93.06%** | — |
| `TABLE-C-20260528-N` | scene **100%** | **92.74%** | — |
| `TABLE-C-20260528-M` | scene beta + block 库 | **90.22%** | — |
| `TABLE-C-20260528-L` | 冲突 composition CAD | **86.44%** | — |
| `TABLE-C-20260528-K` | fixture + L3 smoke | **77.27%** | — |
| `TABLE-C-20260528-J` | core.api/guard writeback | `cad_proof` **81.07%** | 当时 headline 76.14% |
| `TABLE-C-20260528-I` | component_role 批量 | 表 C headline **75.71%** | — |
| `TABLE-C-20260528-H` | object/symbol 批量 CAD | 表 C **62.78%** | 旧 evidence audit 债仍在 |
| `TABLE-C-20260528-E` | regression 6 case CAD | 表 C **40.91%**；verified→0 | 下一门 scene_fragment / 实力指数 |
| `TABLE-C-20260528-D` | intent/block/demand/symbol | showcase +27 | — |
| `TABLE-C-20260528-C` | object/domain/glyph | showcase +45 | — |
| `TABLE-C-20260528-B` | composition + benchmark 镜像 | 三波 composition CAD；showcase +10 | 全库 hard audit 仍 fail |
| `TABLE-C-20260528-A` | 工装 catalog showcase | `tablec-fitout-catalog-20260528-cad/` 14/14 | 全库 hard audit 仍 fail |
| `DOC-FINISH-ARCH-01` | 本轮文档架构升级 | 活跃入口瘦身、history snapshot、planning archive、doc governance 预算门禁 | 不改 registry，不新增真实 CAD 几何证明 |
| `CAD-EVIDENCE-01` | 表 C hard audit + visual gate 已建立 | `output/validation_runs/table-c-evidence-gate/` | 旧 registry 审计 131 audited / 59 pass / 72 fail，需另包补债 |
| `V-PROOF-73` | §3 能力证明轨收口 | `output/validation_runs/vproof-73-cross-machine/cross_machine_report.json` | no-CAD 4/4；真实换机仍需人工 gate |
| `STRUCT-MERGE-01` | drawing policy 合并已完成 | composition focused tests、repo audit 历史记录 | 不改变表 C，不运行真实 CAD |
| `VCAD-02` | CAD 视觉表达 P1 已有真实 AutoCAD 证据 | `output/previews/vcad-02-visual-room-plan.png`、99 handles 回读 | 视觉表达不等于施工图交付能力 |

完整历史继续查 `docs/status/changelog.md` 与 `docs/handoffs/package-index.md`。

## 当前风险

| 风险 | 影响 | 当前处理 |
| --- | --- | --- |
| Core / training / case 边界继续变重 | `core/` 可能继续吸收临界模块，`core/verification/`、capability map、case renderer 可能变成混合层 | 新增 `current-module-boundaries.md` 和 `architecture-boundary-hardening-01` OpenSpec；后续拆分按 report contract、runner、registry writeback、visual audit、data generator、page shell、display configuration 和 case promotion gate 推进 |
| 表 C 旧证据债 | 旧 verified/showcase 报告缺路径或契约字段会阻止新 writeback | 表 C 新包先跑 hard audit、visual review、table C gate |
| CAD 画面与几何扩样仍少 | 用户看到的复杂 CAD 图面仍需持续提升 | 需要时优先 `VCAD-*` 或真实 CAD 扩样包 |
| 训练审计虚绿 | 部件齐全或 profile ratio 对齐仍可能被误判为款式准确，尤其 reference-match 案例 | 已新增 reference profile、形态丰富度、part gap/overlap、共享边去重与沙发方向语义门槛 |
| 常识文件被误读为已学会 | 把外部资料、图库或 GitHub 方法论放进仓库，不等于 Agent 能稳定使用 | 新增 CAD 常识底座文档，要求 source_note → summary → candidate → executable_check → evidence_boundary |
| raw 标准图库进 git 后边界变模糊 | 为了家里 / 公司两头开发，`standard_cad_library_raw/` 允许携带下载文件；若未写来源和边界，容易误追踪、误提交或误当能力 | 新增自动 raw intake：先扫描并生成 `source_note` / reference manifest / inferred annotation；raw 只算 reference input，自产资产只进 `libraries/system_library/` |
| 训练工作台被误读为证据 | `capability-map.html` 展示训练计划、智能体 Prompt 契约和阶段状态，若脱离表 C 口径，可能被误读成真实 CAD 能力证明 | 页面顶部、训练详情、智能体成熟度和证据边界均声明“训练阶段 / 契约分不等于 CAD 通过率”；真实证据仍在 registry、coverage、case runs、audit 和 promotion 记录里 |
| 参考图库被误读为自产能力 | 外部标准图库、用户截图或 vendor block 被混入系统库后，可能被误报为“系统已会画” | 新增资产智能架构：`reference_library` 只作 evidence input，`system_library` 必须有 schema、lineage、check、evidence_boundary 和晋升记录 |
| 训练反馈低信号 | 只报 handles、gap/overlap 或贴截图，用户仍不知道该判断什么 | README 新增低噪声反馈模板：本轮结论、变化、checked/not_checked、重点看点、反馈入口 |
| 自动读图未到交付预备 | 未确认 shell candidates 不能直接落 CAD | 保持人工确认 gate |
| 文档入口再膨胀 | 默认上下文会被 done 明细重新占满 | `run_doc_governance_audit.py` 增加活跃文档体量预算 |

更多风险和教训见 `docs/status/issues.md`。

## 当前入口

| 需要 | 看哪 |
| --- | --- |
| Agent 训练 / 家装主训 | `docs/training/README.md` |
| 案例 backlog | `docs/planning/任务清单.md` §0 |
| 唯一主线 / 后置 Backlog | `CORE_RESTRUCTURE_PLAN.md` |
| 能力矩阵 / 表 A/B/C | `CORE_STATUS.md` |
| 已完成包明细 | `docs/planning/archive/` |
| 当前交接 | `docs/handoffs/current.md` |
| 全量交接索引 | `docs/handoffs/package-index.md` |
| 历史快照 | `docs/history/snapshots/finished-architecture-2026-05-28/` |

## 最近验证入口

最近完整门禁记录：CAD-MCP venv 全量 `unittest discover -s tests` **1044 OK（2 skipped）**；`run_doc_governance_audit.py` pass；CAD-MCP venv `scripts/self_check.py` pass。系统 Python 缺少 `PIL` 时，`self_check.py` 现在会降级为 screenshot tooling warn，而不是异常失败。`CAPABILITY-MAP-TRAINING-WORKBENCH-03` 已跑数据生成器、`py_compile`、`node --check capability-map-data.js`、HTML 内联脚本语法检查，并用 Chrome DevTools 验证桌面 / 移动截图与无明显文本溢出。round14 已真实 CAD 重画并删除上一版预览；用户纠错已沉淀为共享边去重和沙发方向语义门槛。当前 coverage 表 C 主指标以 `output/validation_runs/capability-lab/cad_capability_coverage.json` 为准：**90.99%**。

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_doc_governance_audit.py
& $py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v
& $py scripts\run_capability_coverage.py --output output\validation_runs\capability-lab\cad_capability_coverage.json
```

真实 CAD 完成声明仍必须补 validate、dry-run、`CODEX_PREVIEW`、created handles 回读、实体检查和必要截图；截图只作视觉辅助。
