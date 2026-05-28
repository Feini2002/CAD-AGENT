# Core Context Brief

最后更新：2026-05-29（方案 A：家装 Agent 训练期）

本文是后续 Codex / Cursor / 其它 agent 工具接手本仓库时的稳定短上下文入口。默认先读 `AGENTS.md`，再读本文；只有执行具体包、完整复盘、排查失败、修改规则或同步状态时，才展开详细文档。

## 当前一句话

本仓库是可迁移的 CAD Agent Core Lab；**当前阶段：家装场景 Agent 训练**（`docs/training/README.md`）。当前升级为 **Visual-First + CAD 常识底座 + 资产智能架构**：白话先经常识 / catalog / 自产资产检索口径形成 `retrieval_pack`；标准图库先走自动 raw intake（文件夹 + 一句说明 → `reference_only` manifest），再由 `pipeline_visual_intent` 产出 `style_target` / `visual_parts` / `reference_match`，进入 `CAD_PLAN` → validate → dry-run → `CODEX_PREVIEW` → handles 回读；表 C ≠ 白话已训通。

## 默认输出口径

普通最终回复默认**不附进度表、表单或表 A/B/C**；只说明本轮完成内容、证据和风险。只有用户明确点名开发状态查询、进度、完整状态、交接、审计、表 A/B/C、表 C、真实 CAD 实力或刷新表 C 时，才展开表格；涉及真实 CAD 能力时先报表 C 主指标。

## 当前精简进度

表 C 只认机器报告：`output/validation_runs/capability-lab/cad_capability_coverage.json`。

| 口径 | 当前值 | 说明 |
| --- | --- | --- |
| **真实 CAD 实力** | **约 90.99%**（`scene_fragment` **93.62%**），最高已证 **L4** | **303/333** showcase；25 smoke + 5 deferred；guard / negative 行不计几何能力 |
| CAD 证明覆盖率 | 机器值见 coverage JSON（317 行；smoke 不计入证明率） | `cad_capability_coverage.json` |
| 工程节奏 | 总约 **97%**（**Core 100%**，Agent 93%） | 表 A；Core 见 `core_platform_completion_gate.md` |
| 训练台账 | 案例 backlog：`docs/planning/任务清单.md` §0 | 主训 **家装**；Lab 三轨已 100% 收口 |

## 当前 next

**Agent 训练期（方案 A）**：主训 `agents/residential/`；复制 `projects/residential_training_template/` 开案例。

| 用户口令 | 默认动作 |
| --- | --- |
| **开一轮训练** / **家装案例** | `brief.md` → 计划 → `CODEX_PREVIEW` → `feedback.md` |
| **记反馈** | 更新案例 `feedback.md` + 任务清单 backlog |
| **优化常识底座** | 读 `docs/training/cad-common-sense-upgrade.md`；只吸收方法论或资料为 summary / candidate / executable_check / evidence_boundary |
| **优化资产图库** | 读 `docs/architecture/cad-asset-intelligence-architecture.md` + `docs/planning/cad-commonsense-asset-dev-plan-01.md`；raw 标准图库放 `standard_cad_library_raw/`，默认跑 `scripts/run_asset_raw_intake.py --write`；自产图库放 `libraries/system_library/` |
| `刷新表 C` | 只跑 coverage（Lab） |
| `画不准` | `docs/runbooks/blocker-playbook.md` |
| Lab 三轨 / Core 施工 | 已收口 → `archive/`、`post-backlog.md` |

## 最近有效事实

- **TRAIN-SOFA-ROUND14-COMMONSENSE**：round13 用户认可衔接贴合但指出白线和方向语义错；已修共享边去重和 `sofa_direction_semantics_inverted`，round14 已真实 CAD 重画（54 实体、33 arc、0 gap/overlap/open endpoint），Agent 自检可请用户验收，不改表 C。
- **CAD-ASSET-RAW-INTAKE-AUTO-01**：标准图库 intake 已从“用户填表”改为“文件夹 + 一句说明 → Agent 自动扫描”；新增 `core/assets/raw_intake.py` 和 `scripts/run_asset_raw_intake.py`，默认 `unknown` / `reference_only` / `agent_inferred`，不写 `system_library`，不改表 C。
- **CAPABILITY-MAP-HTML-01**：根目录 `capability-map.html` 已作为能力覆盖清单 V1：左侧列具体图块和基础绘图能力计划，右侧只显示标准图库 / 常识整理 / 训练通过 / 自产资产覆盖阶段；当前阶段默认全空，不放内部证据路径，不替代表 C。
- **CAD-COMMONSENSE-ASSET-DEV-PLAN-01**：标准图库常识底座开发计划已明确：下载的原始标准图库放根目录 `standard_cad_library_raw/` 并可随 git 迁移；自产图库只放 `libraries/system_library/`；raw 文件默认不是系统能力。
- **CAD-ASSET-INTELLIGENCE-FOUNDATION-01**：资产智能前五项已落基础版：reference/system/knowledge/benchmarks 目录、core schema、`retrieval_pack` CLI、`pipeline_asset_retriever`、训练 intake 模板、promotion gate；未写测试、未跑测试、未接 RAG、不改表 C。
- **CAD-ASSET-INTELLIGENCE-ARCH-01**：资产智能架构包已固化；reference_library 只是 evidence input，system_library 才是 promoted asset；不把图库命中当能力证明。
- **CAD-COMMON-SENSE-ARCH-01**：吸收 `llm-wiki`、`step.parts`、`CADTestBench`、`CADCLAW` 方法论为 CAD 常识底座文档；新增“资料沉淀、catalog-first、可执行检查、证据边界”和低噪声训练反馈模板；未导入图库、未跑测试、不改表 C。
- **CORE-PLATFORM-100**：Core 底座 **100%**（三轨收口 + **969** tests + `run_core_platform_gate.py` pass）；**≠** 表 C 100%。
- **BETA-CROSS-MACHINE-02**：换机 P0 gate + baseline v2（99.68%）；`run_beta_cross_machine_02_gate.py`；MCP 手动画仍须人工确认。
- **VCAD-03**：零售展厅平面真实 CAD `visual_geometry_verified`；证据 `vcad-03-retail-20260528/`；**不改**表 C registry。
- **后置 Backlog 拆包**：`docs/planning/post-backlog.md`；SAMPLE-07 intake 模板、READ-06 读图 gate runbook、AGENT-REGISTRY-01 策略文档已交付。
- **表 C / 旧施工包历史**：已迁入 `docs/status/changelog.md`、`docs/planning/archive/` 与 `docs/handoffs/archive/`；短上下文只保留当前机器值和活跃训练 / 架构事实。

## 主从关系

- `CORE_RESTRUCTURE_PLAN.md` 是唯一 `PlanMD`。
- `docs/planning/任务清单.md` 是唯一执行台账和即时 `next` 镜像。
- `CORE_STATUS.md` 解释能力状态和表 C；机器值以 coverage JSON 为准。
- `docs/status/current.md` 写当前状态；`docs/status/changelog.md` 写历史流水；`docs/status/issues.md` 写风险和教训。
- `docs/handoffs/current.md` 写最近包交接；`docs/handoffs/package-index.md` 查全量包；历史包在 `docs/handoffs/archive/`。
- `output/validation_runs/**` 是机器证据本体，不因 Markdown 整合而移动。

## 不能声称

- 不能把 Core 约 96%、RCAD 29/29 或 no-CAD benchmark 说成“已经能画准施工图”。
- 不能把截图、SVG/PNG 预览、dry-run 或 `benchmark_pass_non_cad` 当成几何准确证据。
- 不能把 `negative_guard_verified`、fake driver 结果或 no-CAD deferred 当成真实 CAD 几何通过。
- 不能默认保存、覆盖、删除 DWG，不能修改正式图层；真实 CAD 默认只写 `CODEX_PREVIEW`。

## 按需展开

| 目标 | 先读 |
| --- | --- |
| 训练一轮 / 建案例 | `docs/training/README.md` + `docs/planning/任务清单.md` §0 |
| 执行开发包 / 调整优先级 | `CORE_RESTRUCTURE_PLAN.md` + 任务清单 |
| 汇报完整能力成熟度 / 展开 A/B/C | `CORE_STATUS.md` + `docs/status/current.md` + coverage JSON |
| CAD 补验 / 画不准 / 环境不通 | `docs/runbooks/blocker-playbook.md` + `docs/runbooks/cad-validation.md` |
| 查历史变更流水 | `docs/status/changelog.md` |
| 查失败教训和活跃风险 | `docs/status/issues.md` |
| 查按包交接 | `docs/handoffs/current.md` + `docs/handoffs/package-index.md` |
| 新人接手 | `docs/onboarding/first-handoff.md` |
| 文档治理 | `docs/planning/phases/phase-z-doc-governance.md` + `scripts/run_doc_governance_audit.py` |

## 常用验证

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest discover -s tests
& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
& $py scripts\run_doc_governance_audit.py
& $py scripts\run_dev_volume_audit.py
& $py scripts\run_capability_coverage.py --output output\validation_runs\capability-lab\cad_capability_coverage.json
```

## 缓存友好约定

- 本文只写短摘要、当前 next、口径和入口，不写长历史。
- 历史进 `docs/status/changelog.md` 或 `docs/history/`。
- 失败教训进 `docs/status/issues.md`。
- 计划和优先级进 `CORE_RESTRUCTURE_PLAN.md`，执行计数进 `docs/planning/任务清单.md`。
