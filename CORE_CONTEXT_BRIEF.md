# Core Context Brief

最后更新：2026-05-28（方案 A：家装 Agent 训练期）

本文是后续 Codex / Cursor / 其它 agent 工具接手本仓库时的稳定短上下文入口。默认先读 `AGENTS.md`，再读本文；只有执行具体包、完整复盘、排查失败、修改规则或同步状态时，才展开详细文档。

## 当前一句话

本仓库是可迁移的 CAD Agent Core Lab；**当前阶段：家装场景 Agent 训练**（`docs/training/README.md`）。当前升级为 **Visual-First**：白话先经 `pipeline_visual_intent` 产出 `style_target` / `visual_parts` / `reference_match`，再进入 `CAD_PLAN` → validate → dry-run → `CODEX_PREVIEW` → handles 回读；表 C ≠ 白话已训通。

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
| `刷新表 C` | 只跑 coverage（Lab） |
| `画不准` | `docs/runbooks/blocker-playbook.md` |
| Lab 三轨 / Core 施工 | 已收口 → `archive/`、`post-backlog.md` |

## 最近有效事实

- **CORE-PLATFORM-100**：Core 底座 **100%**（三轨收口 + **969** tests + `run_core_platform_gate.py` pass）；**≠** 表 C 100%。
- **BETA-CROSS-MACHINE-02**：换机 P0 gate + baseline v2（99.68%）；`run_beta_cross_machine_02_gate.py`；MCP 手动画仍须人工确认。
- **VCAD-03**：零售展厅平面真实 CAD `visual_geometry_verified`；证据 `vcad-03-retail-20260528/`；**不改**表 C registry。
- **后置 Backlog 拆包**：`docs/planning/post-backlog.md`；SAMPLE-07 intake 模板、READ-06 读图 gate runbook、AGENT-REGISTRY-01 策略文档已交付。
- **TABLE-C-FINAL-GAP**：末 **4** 行 none→showcase（3×intent + `verification_no_cad_report`）；主指标 **98.42%→99.68%**；`real_cad_guard` 仍 smoke。
- **TABLE-C-20260528-P**：**17** 条 smoke（negative/trend/lab/cross_machine）绑 fresh `capability_probe`；主指标 **93.06%→98.42%**；`real_cad_guard` 仍 smoke。
- **TABLE-C-20260528-O**：`core.api.benchmark_non_cad_suite`；**93.06%**（295 showcase）。
- **TABLE-C-20260528-N**：过小 blank_shell L3 满格 + guard；**92.74%**；`scene_fragment` **100%**。
- **TABLE-C-20260528-M**：scene beta 冲突 + block 库 **12** 行；主指标 **86.44%→90.22%**。
- **TABLE-C-20260528-L**：冲突 composition **13** 行；主指标 **77.27%→86.44%**。
- **TABLE-C-20260528-K**：fixture suite + **5** 行 writeback；主指标 **76.14%→77.27%**。
- **TABLE-C-20260528-J**：fresh guard probe + **17** 行 writeback；`cad_proof` **75.71%→81.07%**；当时 headline **76.14%**。
- **TABLE-C-20260528-I**：primitive/complex CAD + **41** 行 writeback（含 **22** `component_role.*`）；表 C **62.78%→75.71%**（`showcase_count` 240）；`scene` 类目 **7/7**。
- **TABLE-C-20260528-H**：object/symbol 批量；表 C **51.10%→62.78%**。
- **TABLE-C-20260528-G**：scene/blank_shell + project_sample；表 C **46.06%→51.10%**。
- **TABLE-C-20260528-F**：**15** 条 L3 benchmark 镜像；表 C **40.91%→46.06%**。
- **TABLE-C-20260528-E**：regression 6 case；表 C **39.43%→40.91%**；`verified_count`→**0**。
- **TABLE-C-20260528-D**：intent/block/demand/symbol；表 C **30.91%→39.43%**（`showcase_count` 125）。
- **TABLE-C-20260528-C**：object 14 + domain 11 + glyph matrix 6；表 C **16.72%→30.91%**；证据 `tablec-object-domain-glyph-20260528-cad/`。
- **TABLE-C-20260528-B**：composition 三波 + 10 条 `benchmark.*` 镜像；表 C **13.56%→16.72%**；证据 `tablec-*-composition-20260528-cad/`。
- **TABLE-C-20260528-A**：工装 catalog 14 对象真实 CAD 升 `showcase`；表 C **9.15%→13.56%**；证据 `tablec-fitout-catalog-20260528-cad/`。
- **§3 能力证明轨 45/45 已收口**；末包 `V-PROOF-73`：换机 playbook + coverage baseline 复算（no-CAD 4/4）；真实 CAD 换机仍见 `docs/onboarding/migration-checklist.md`。
- `DOC-FINISH-ARCH-01` 已把 PlanMD、任务清单、Core Status、当前状态页从施工期长明细瘦身为控制面；瘦身前全文在 `docs/history/snapshots/finished-architecture-2026-05-28/`，done 台账索引在 `docs/planning/archive/`。
- `CAD-EVIDENCE-01` 已新增表 C hard gate：`run_capability_evidence_audit.py` + `run_visual_cad_review.py` + `run_table_c_evidence_gate.py`。后续表 C writeback 前若硬证据或截图复盘失败，`writeback_allowed=false`；截图仍只是 `visual_aid_only`，不替代 created-handle readback。首次审计现有 registry 为 131 audited / 59 pass / 72 fail，说明旧证据债需另包补齐。
- `V-PROOF-23` / `V-PROOF-24` 已完成：五类 `component_detail` + office_alpha 6 对象 case 均为 **smoke / benchmark_pass_non_cad**；registry **315** 行；表 C headline **9.21%**（office 误绑 verified 已纠正，未用 smoke 抬高主指标）。
- `DOC-ARCH-REBASE` 根目录长文档已迁入 `docs/status/`、`docs/governance/`、`docs/runbooks/`（根路径保留 stub）；handoff 已拆为 current / index / archive / template；`scripts/run_doc_governance_audit.py` 覆盖 registry、表 C、handoff、链接与根 stub 目标。续作 `DOC-ARCH-REBASE-02` 已对齐表 C 活跃快照并增强审计（changelog 历史行、根 stub 校验）。
- `STRUCT-MERGE-01` 已完成：`drawing_policy.py` 合并进 `templates.py`，并修复 `block_matrix_registry` 对 `showcase` claim_level 的同步识别；全测曾为 864 tests OK。
- `VCAD-02` 已完成真实 AutoCAD 视觉表达 P1：99 created handles 回读，`visual_geometry_verified`；这是视觉表达证据，不改变表 C。
- `V-PROOF-42-COMPOSITION-EXPAND` 已完成真实 CAD 刷新：4/4 office composition case `geometry_verified`，40 created handles 回读；coverage 数值保持 8.87% 主指标。
- `V-PROOF-60`~`66` 已建立 showcase / Ladder 初版，最高已证 L4；当前主瓶颈仍是 showcase 就绪度。

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
