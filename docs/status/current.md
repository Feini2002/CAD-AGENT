# 通用 CAD Agent 开发包当前进展

最后更新：2026-05-28

本文是当前进展页，只保留“现在到哪、证据是什么、风险边界是什么”。历史流水见 `docs/status/changelog.md`，能力矩阵见 `CORE_STATUS.md`，唯一 `PlanMD` / 主计划见 `CORE_RESTRUCTURE_PLAN.md`。后续任务和优先级只写入 PlanMD，避免状态页变成第二份计划。

## 当前阶段

### 2026-05-28 DOC-ARCH-REBASE：文档架构一次性重构

- **控制面收缩**：根目录保留 `README.md`、`AGENTS.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_STATUS.md` 和兼容 stub；长状态 / 规则 / runbook 迁入 `docs/`。
- **交接收口**：`docs/handoffs/current.md` 保存活跃结构治理包，`docs/handoffs/package-index.md` 保存全量索引，`docs/handoffs/archive/2026-05.md` 保存历史包。
- **自动化护栏**：新增 `scripts/run_doc_governance_audit.py`，检查文档注册、主从关系、表 C 旧值、handoff 和 Markdown 链接。
- **复核加固**：旧 `CURSOR_PACKAGE_HANDOFFS.md` 保留包名搜索索引但不承载全文；Phase Z、runbook、governance 和状态页旧写回路径已改为 `docs/status/*`。
- **边界**：本轮不移动 `output/validation_runs/**`，不修改 registry，不改变表 C；`docs/verification/*.md` 路径暂保持稳定，因为代码常量和测试仍直接引用这些证据页。

### 2026-05-28 STRUCT-AUDIT-01：全仓 Python 结构审计

- **审计完成**：新增 `docs/verification/struct_audit_01.md`，按全仓 Python 文件行数、职责、内部 import 关系和测试覆盖入口完成结构审计。
- **机器证据**：`output/validation_runs/struct-audit-01/struct_audit_report.json` 覆盖 505 个 Python 文件、56,247 行、1,523 条内部 import 边，AST 解析错误 0；CSV 清单见同目录 `python_inventory.csv`。
- **风险提示**：320 个非测试模块中 186 个有直接静态测试入口、20 个间接可达、114 个未发现静态测试入口；其中 `core/verification/composition_cad_registry.py` 与 `scripts/run_composition_cad_registry.py` 仍是静态测试入口缺口，后续项以 `CORE_RESTRUCTURE_PLAN.md` 和 `docs/planning/任务清单.md` 为准。
- **边界**：本包只做结构审计，不运行真实 CAD、不写 DWG、不修改 registry、不改变表 C。

### 2026-05-28 STRUCT-MERGE-PREP-01：合并规则与候选清单

- **规则完成**：新增 `docs/verification/struct_merge_keep_rules.md`，固定“该合并 / 该保留 / 该拆分 / 允许超线例外”的判断口径。
- **候选完成**：新增 `docs/verification/struct_merge_candidates.md` 与 `output/validation_runs/struct-audit-01/merge_candidate_table.csv`；候选分为 1 个应合并、5 个应拆分 / 抽公共层、6 个应保留、4 个观察 / 延后。
- **合并候选状态**：首个高确定性候选是 `core/composition_engine/drawing_policy.py` 合并入 `core/composition_engine/templates.py`；`composition_cad_registry` 保持风险记录，不在状态页承载独立队列。
- **边界**：本轮没有实际合并 Python 文件，不运行真实 CAD、不写 DWG、不修改 registry、不改变表 C。

### 2026-05-28 STRUCT-MERGE-01：drawing_policy 合并小包

- **合并完成**：`core/composition_engine/drawing_policy.py` 已删除，固定 drawing flags 策略合并进 `core/composition_engine/templates.py`；旧 import 扫描无残留。
- **测试证据**：TDD 红灯为旧文件仍存在；实现后 `tests.core.test_composition_catalog` 5 tests OK，composition focused 15 tests OK。
- **加固 / BUG 筛查**：全量 unittest 首轮发现 RBLOCK-07 matrix sync 对 `showcase` 行拒绝绑定；已修复 `core/block_engine/block_matrix_registry.py`，修复后 864 tests OK。`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings。
- **剩余风险**：`run_dev_volume_audit.py` 仍提示工作树整体变更量偏大，需要继续收口。
- **边界**：不运行真实 CAD、不写 DWG、不修改 registry、不改变表 C。

### 2026-05-27 VCAD-02：CAD 视觉表达 P1 房间平面

- **能力升级**：在 `VCAD-01` 办公角落基础上继续推进画面能力，新增 `visual_room_plan_smoke`，目标从“可读场景符号”升级到“带门窗、尺寸、标签和分区的房间平面”。
- **能力新增**：真实 CAD 中绘制分段双线墙、门洞 / 门扇 / 门弧、窗符号、办公区 / 会议区 / 动线轮廓、双工位、会议桌椅、柜体、北箭、房间文字和三段尺寸链。
- **证据**：真实 AutoCAD 报告 `output/validation_runs/vcad-02-visual-room-plan-20260527-cad/visual_room_plan_smoke_report.json` 为 `visual_geometry_verified`；created handles **99**，类型计数 `line=67`、`circle=10`、`arc=9`、`polyline=4`、`text=6`、`dimension=3`，visual detail score **100**；截图 `output/previews/vcad-02-visual-room-plan.png`。
- **边界**：本包仍不改变表 C 机器值；它证明 CAD 画面可读性继续提升，但不声称施工图级制图、真实公司块库、正式图层体系或项目级交付完成。

### 2026-05-27 VCAD-01：CAD 视觉表达 P0 办公角落

- **方向切换**：用户指出 CAD 画面仍停留在 5-10% 左右，本轮暂停刷表 C，改做真实画面表达升级。
- **能力新增**：新增 `visual_cad_smoke`，直接在 `CODEX_PREVIEW` 绘制可读办公角落：双线房间、门扇开启弧、两组工位、显示器/键盘、椅子、抽屉柜和工作区轮廓。
- **证据**：真实 AutoCAD 报告 `output/validation_runs/vcad-01-visual-office-corner-20260527-cad/visual_cad_smoke_report.json` 为 `visual_geometry_verified`；created handles **54**，类型计数 `line=42`、`circle=6`、`arc=3`、`polyline=3`，visual detail score **100**；截图 `output/previews/vcad-01-visual-office-corner.png`。
- **边界**：这是 P0 视觉表达包，证明“画面复杂度开始上来”，不改变表 C 机器值，也不声称施工图、真实块库、正式图层或项目交付能力完成。

### 2026-05-27 V-PROOF-42：Composition Expand 真实 CAD 刷新

- **能力证明**：完成 `V-PROOF-42-COMPOSITION-EXPAND`，按 `office_composition_cad_registry_manifest.json` 在真实 AutoCAD 会话刷新 4 个 office composition case。
- **证据**：`output/validation_runs/vproof-42-office-composition-expand-20260527-cad/composition_cad_registry_report.json` 顶层 `status=geometry_verified`；4/4 case 通过，created handles 共 40，均写入并回读于 `CODEX_PREVIEW`；未保存 DWG、未删除实体、未改正式图层。
- **Registry / 表 C**：4 个 composition 行回写到本轮 fresh report，`writeback_apply.json` 为 `applied_count=4`；这些行此前已是 `verified`，coverage 复跑后仍为 `verified_count=112`、`showcase_count=25`、`cad_proof_count=137`、CAD 证明覆盖率 **48.58%**、CAD 实力指数 **51.03%**、真实 CAD 实力主指标 **8.87%**（showcase 门），最高 L4。
- **台账**：能力证明更新为 **35/45 done**，另有 1 partial；当前后续项见 `docs/planning/任务清单.md` §0。

### 2026-05-27 DEV-AUDIT-01：开发量审计入口

- **加固**：新增 `scripts/run_dev_volume_audit.py`，用于输出当前工作树开发量 JSON，便于大批表 C / CAD 补验后判断是否需要停下收口。
- **当前体检**：本轮审计显示 100 changed files、55 tracked、45 untracked、3653 insertions、326 deletions；触发文件数偏大与 handoff 单文件 delta 提醒。
- **边界**：该脚本只读 Git 状态，不触碰 CAD、不写 DWG、不改变表 C 数值。

### 2026-05-27 V-PROOF-41：Block CAD Matrix 真实 CAD 补验

- **能力证明**：完成 `V-PROOF-41-BLOCK-CAD-MATRIX`，双受控测试块 `controlled-test-block-001/002` 均在真实 AutoCAD 会话的 `CODEX_PREVIEW` 完成 insert + created-handle readback。
- **证据**：`output/validation_runs/vproof-41-block-cad-matrix-20260527-cad/block_alpha_beta_summary.json` 顶层 `status=pass`、2/2 `geometry_verified`；created handles `61F`、`627`，均回读为 `block_reference`，未保存 DWG、未删除实体、未改正式图层。
- **Registry / 表 C**：`block.library.controlled_test_block_002` 从 `smoke` 回写为 `verified`；coverage 复跑后 `verified_count=112`、`showcase_count=25`、`cad_proof_count=137`、CAD 证明覆盖率 **48.58%**、CAD 实力指数 **51.03%**、真实 CAD 实力主指标仍 **8.87%**（showcase 门），最高 L4。
- **台账**：该条为当时快照；当前已随 `V-PROOF-42` 更新为 **35/45 done**，另有 1 partial；当前后续项见 `docs/planning/任务清单.md` §0。

### 2026-05-27 V-PROOF-66：Primitive Probe Showcase

- **能力证明**：完成 `V-PROOF-66-PRIMITIVE-PROBE-SHOWCASE`，把 primitive probe 7 行与 drawing-standard suite 1 行既有真实 CAD 证据补入 showcase。
- **证据**：`output/validation_runs/vproof-66-primitive-probe-showcase/writeback_apply.json` 显示 8 行从 `verified` 升到 `showcase`；报告来源为 `RCAD-22` 与 `RCAD-23`。
- **表 C**：`verified_count=111`、`showcase_count=25`、`cad_proof_count=136`、CAD 证明覆盖率 **48.23%**、CAD 实力指数 **50.82%**、真实 CAD 实力主指标提升到 **8.87%**（showcase 门），最高 L4。
- **台账**：该条为当时快照；当前已随 `V-PROOF-42` 补验更新为 **35/45 done**，另有 1 partial；当前后续项见 `docs/planning/任务清单.md` §0。

### 2026-05-27 V-PROOF-65：Showcase Second Wave

- **能力证明**：完成 `V-PROOF-65-SHOWCASE-SECOND-WAVE`，把 hatch、block-first、drawing-standard block insert 三组既有真实 CAD 证据补入 showcase。
- **证据**：`output/validation_runs/vproof-65-showcase-second-wave/writeback_apply.json` 显示 4 行从 `verified` 升到 `showcase`；报告来源为 `RCAD-06`、`RCAD-25`、`RCAD-23`。
- **表 C**：`verified_count=119`、`showcase_count=17`、`cad_proof_count=136`、CAD 证明覆盖率 **48.23%**、CAD 实力指数 **50.82%**、真实 CAD 实力主指标提升到 **6.03%**（showcase 门），最高 L4。
- **台账**：该条为当时快照；当前已随 `V-PROOF-42` 补验更新为 **35/45 done**，另有 1 partial；当前后续项见 `docs/planning/任务清单.md` §0。

### 2026-05-27 V-PROOF-64：Ladder Boundary + Block Matrix Showcase

- **能力证明**：完成 `V-PROOF-64-LADDER-BOUNDARY-DOC`，新增全仓库 Ladder 边界页，并把 `block.insert_block_alpha.matrix` 从 verified 推进到 showcase。
- **证据**：showcase 条目 `docs/verification/capability_showcase/showcase/L2/block_insert_matrix/gallery_index.json` 绑定 `RCAD-24-BLOCK-ALPHA-BETA` 的 8/8 真实 CAD block_reference 回读证据；`output/validation_runs/vproof-64-ladder-boundary-doc/writeback_apply.json` 显示 `applied_count=1`。
- **表 C**：`verified_count=123`、`showcase_count=13`、`cad_proof_count=136`、CAD 证明覆盖率 **48.23%**、CAD 实力指数 **50.82%**、真实 CAD 实力主指标提升到 **4.61%**（showcase 门），最高 L4。
- **台账**：该条为当时快照；当前已随 `V-PROOF-42` 补验更新为 **35/45 done**，另有 1 partial；当前后续项见 `docs/planning/任务清单.md` §0。

### 2026-05-27 V-PROOF-45：Block Beta Rows 回写表 C

- **能力证明**：完成 `V-PROOF-45-BLOCK-BETA-ROWS`，把 `RCAD-24-BLOCK-ALPHA-BETA` 的 8/8 真实 CAD block_reference 回读证据写回 `block.insert_block_alpha.matrix` 父行。
- **证据**：`output/validation_runs/vproof-45-block-beta-rows/writeback_apply.json` 显示 `applied_count=1`；`output/validation_runs/capability-lab/cad_capability_coverage.json` 已复跑。
- **表 C**：`verified_count=124`、`cad_proof_count=136`、CAD 证明覆盖率 **48.23%**、CAD 实力指数 **50.82%**、真实 CAD 实力主指标仍 **4.26%**（showcase 门），最高 L4。
- **台账**：该条为当时快照；当前已随 `V-PROOF-42` 补验更新为 **35/45 done**；当前后续项见 `docs/planning/任务清单.md` §0。

### 2026-05-27 V-PROOF-41：双受控块 CAD matrix

- **能力证明推进**：`controlled-test-block-002` 已进入 `insert_block_alpha` 的受控 allowlist；新增 `examples/plans/block_cad_matrix_vproof_41.json` 双块 suite，001/002 均可 validate + dry-run。
- **验证证据**：`output/validation_runs/vproof-41-block-cad-matrix-20260527-cad/block_alpha_beta_summary.json` 顶层 `status=pass`、2/2 `geometry_verified`；handles `61F`、`627` 均回读为 `block_reference`。
- **边界**：本包只证明两个受控测试块在当前 AutoCAD 会话与 `CODEX_PREVIEW` 上可按 CAD_PLAN 插入并回读，不扩大到任意公司块库、属性块、正式图层或施工图块。

### 2026-05-27 V-PROOF-40：Block Matrix Plan 表 C 收口

- **能力证明**：完成 `V-PROOF-40-BLOCK-MATRIX-PLAN`，把 `RBLOCK-04/07` 的 block insert matrix 前置成果正式收成能力证明包。
- **证据**：`output/validation_runs/vproof-40-block-matrix-plan-no-cad/block_matrix_registry_sync_summary.json` 顶层 `matrix_status=pass`，5 个 binding applied，0 rejected；`block_insert_matrix_summary.json` 与四个 `dimension_*.json` 已输出。
- **Registry 口径**：`block.insert_block_alpha.matrix` 只更新 smoke evidence（`dry_run_valid_plan_only`）；`anchor/rotation/scale/attributes` 4 个维度行保持既有 `readback_geometry_verified`，只追加矩阵 manifest 来源，不覆盖真实 CAD 证据。
- **表 C**：coverage 复跑后数值保持 `total_count=282`、`verified_count=123`、`showcase_count=12`、CAD 证明覆盖率 **47.87%**、CAD 实力指数 **50.75%**、真实 CAD 实力主指标 **4.26%**。能力证明台账当时为 **29/43（约 67%）**；当前后续项见 `docs/planning/任务清单.md` §0。

### 2026-05-27 SCENE-PROD-06：多场景回归门禁

- **一键推进**：完成 `SCENE-PROD-06-MULTI-SCENE-REGRESSION-GATE`，把 office / residential / restaurant 三个 scene beta benchmark 收成一个 no-CAD 回归门禁，并同步检查 scene explanation 与 P3 rollup 仍可读。
- **产物**：`core/agents/scene_regression_gate.py`、`scripts/run_scene_prod_06_regression_gate.py`、`docs/verification/scene_prod_06_multi_scene_regression_gate.md`、`tests/core/test_scene_prod_06_regression_gate.py`。
- **证据**：`output/validation_runs/scene-prod-06-regression-gate-no-cad/scene_regression_gate_summary.json` 顶层 `status=pass`；25/25 selected benchmark pass，21 个 `benchmark_pass_non_cad`、4 个 `blocked_expected_non_cad`、`readback_geometry_verified_count=0`；repo audit 0 findings。
- **口径**：代码轨更新为 **49/55（约 89%）**；本包未运行真实 CAD、不新增 `geometry_verified`，也不把场景 beta 写成 Scene Product。

### 2026-05-27 RCAD-06：Hatch COM 受控 smoke 真实 CAD 补验

- **CAD 补验**：完成 `RCAD-06-HATCH`；real COM driver 的 `draw_hatch` 已从 structured deferred 推进为受控真实 AutoCAD 写入，先创建闭合 boundary polyline，再创建 ANSI31 hatch。
- **产物**：`core/cad_io/autocad_com.py` 新增 hatch COM 写入路径；`core/verification/hatch_cad_smoke.py`、`scripts/run_hatch_cad_smoke.py` 与 `tests/core/test_hatch_cad_smoke.py` 固定 no-CAD deferred 与真实 CAD smoke 证据。
- **证据**：`output/validation_runs/rcad-06-hatch-cad-20260527-escalated/hatch_cad_smoke_report.json` 为 `status=geometry_verified`、`evidence_state=readback_geometry_verified`，created handles `61C` / `61D`，回读类型 `hatch=1`、`polyline=1`，pattern `ANSI31`，bbox `100 x 80`；未保存 DWG、未删除实体、未修改正式图层。
- **Registry / 表 C**：`primitive.hatch` 已由 `deferred` 回写为 `verified`；coverage 复跑后为 `total_count=282`、`verified_count=123`、`showcase_count=12`、CAD 证明覆盖率 **47.87%**、CAD 实力指数 **50.75%**、真实 CAD 实力主指标 **4.26%**、最高 L4。
- **口径**：RCAD 烟囱更新为 **29/29 verified**；本包只证明一组受控 ANSI31 preview hatch smoke，不等于任意 hatch、正式图层 hatch 或施工图 hatch 全面准确。

### 2026-05-27 RCAD-28：BETA-CAD-BLOCK evidence rollup + trend 补验

- **CAD 补验**：完成 `RCAD-28-BETA-EVIDENCE-ROLLUP`；本包按既有设计是 non-CAD 父包证据汇总，不连接 AutoCAD、不新增实体。
- **代码补齐**：`core/verification/cad_beta_evidence_rollup.py` 现在同步写出 `evidence_trend/cad_beta_evidence_rollup_trend.json`；测试固定 5 个子包只能计为 `dry_run_valid_plan_only`，`geometry_verified_count=0`。
- **证据**：`output/validation_runs/rcad-28-beta-evidence-rollup-20260527-final/cad_beta_evidence_rollup.json` 顶层 `status=pass`，5/5 subpackages pass；trend 校验 0 errors，summary 为 `non_cad_only=true`、`dry_run_valid_plan_only_count=5`。
- **口径**：该条为历史快照；RCAD 烟囱当时为 **28/29 verified**，当前已随 `RCAD-06-HATCH` 更新为 **29/29 verified**。本包自身仍不新增真实 CAD `geometry_verified`。

### 2026-05-27 RCAD-27：local CAD regression trend rollup 真实 CAD 补验

- **CAD 补验**：完成 `RCAD-27-TREND-ROLLUP-CAD`，把 `LCAD-11.2` 的 local CAD regression strict 矩阵纳入真实 AutoCAD 会话复验。
- **证据**：`output/validation_runs/rcad-27-trend-rollup-cad-20260527-escalated/local_cad_regression_report.json` 顶层 `status=pass`，9/9 `geometry_verified_case_count`，created handles 共 105；趋势复算为 `output/validation_runs/rcad-27-trend-rollup-cad-20260527-escalated/evidence_trend/local_cad_regression_trend.json`。
- **安全边界**：只写 `CODEX_PREVIEW` / `CODEX_DIAGNOSTIC` 允许层，未保存 DWG、未删除实体、未修改正式图层；沙箱内 COM 不可见时为外部阻塞，按用户 CAD 会话提权复跑后通过。
- **口径**：RCAD 烟囱当时更新为 **27/29 verified**。本轮未回写 capability registry，表 C 机器值仍为真实 CAD 实力主指标 **4.26%**、最高 L4。

### 2026-05-27 RCAD-24：block alpha beta 真实 CAD 补验

- **CAD 补验**：完成 `RCAD-24-BLOCK-ALPHA-BETA`，把 `block-alpha-beta-01` 的 8 个 controlled block insert case 全部落到用户 AutoCAD 会话的 `CODEX_PREVIEW`。
- **产物**：`core/verification/block_alpha_beta_suite.py` 增加 `--connect-cad` 路径；`core/block_engine/block_placement.py` 修正旋转 block bbox 预期为四角旋转后的真实外包框；CLI 为 `scripts/run_block_alpha_beta_suite.py --connect-cad`。
- **证据**：`output/validation_runs/rcad-24-block-beta-cad-after-rotfix-20260527/block_alpha_beta_summary.json` 中 `status=pass`，8/8 `geometry_verified`，created handles `373`~`37A`；安全审计显示只写 `CODEX_PREVIEW`、未保存 DWG、未删除实体、未修改正式图层。
- **口径**：RCAD 烟囱当时更新为 **26/29 verified**。本轮未回写 capability registry，表 C 机器值仍为真实 CAD 实力主指标 **4.26%**、最高 L4。

### 2026-05-27 SCENE-PROD-05：Scene Beta 解释模板收口

- **一键推进**：完成 `SCENE-PROD-05-SCENE-EXPLANATION-TEMPLATE`，把 office / residential / restaurant 的 scene beta preferences 映射到 Core、benchmark observables 和 evidence boundaries。
- **产物**：`core/agents/scene_beta_explanation.py`、`docs/verification/scene_prod_05_scene_explanation_template.md`、`scripts/run_scene_beta_explanation_template.py`、`tests/core/test_scene_prod_05_scene_explanation_template.py`。
- **证据**：focused 5 tests OK；`output/validation_runs/scene-prod-05-explanation-template-no-cad/scene_beta_explanation_summary.json` 为 `status=pass`；三场景解释对象可机器读取，`readback_geometry_verified_count=0`。
- **口径**：代码轨当时更新为 **48/55（约 87%）**。本包未运行真实 CAD，不新增 `geometry_verified`。

### 2026-05-27 REST-PROD-04：P3 多场景父包收口

- **一键推进**：完成 `REST-PROD-04-MULTI-SCENE-P3-ROLLUP`，统一收口 `OFFICE-PROD-03` 与 `REST-PROD-03`。
- **产物**：`core/agents/multi_scene_p3_wave.py`、`docs/verification/rest_prod_04_multi_scene_p3_rollup_acceptance.md`、`scripts/run_multi_scene_p3_rollup.py`、`tests/core/test_rest_prod_04_multi_scene_p3_rollup.py`。
- **证据**：focused 5 tests OK；`output/validation_runs/rest-prod-04-multi-scene-p3-rollup-no-cad/multi_scene_p3_wave_summary.json` 为 `status=pass`；alpha 19 + beta 17 no-CAD case 可审计，`readback_geometry_verified_count=0`。
- **口径**：代码轨当时更新为 **47/55（约 85%）**。本包未运行真实 CAD，不新增 `geometry_verified`。

### 2026-05-27 REST-PROD-03：餐饮 P3 波次父包收口

- **一键推进**：完成 `REST-PROD-03-RESTAURANT-P3-WAVE-ROLLUP`，按 `OFFICE-PROD-03` 模式统一收口 restaurant alpha / beta 边界。
- **产物**：`core/agents/restaurant_p3_wave.py`、`docs/verification/restaurant_prod_03_p3_wave_acceptance.md`、`scripts/run_restaurant_p3_wave_rollup.py`、`tests/core/test_rest_prod_03_p3_wave_rollup.py`。
- **证据**：focused 6 tests OK；`output/validation_runs/rest-prod-03-p3-rollup-no-cad/restaurant_p3_wave_summary.json` 为 `status=pass`；alpha case + beta 8/8 no-CAD benchmark 通过，`readback_geometry_verified_count=0`。
- **口径**：代码轨当时更新为 **46/55（约 84%）**。本包未运行真实 CAD，不新增 `geometry_verified`。

### 2026-05-27 REST-PROD-02：餐饮 beta 边界收口

- **一键推进**：完成 `REST-PROD-02-RESTAURANT-BETA-BOUNDARY`，按 `OFFICE-PROD-02` 模式把 restaurant beta benchmark 收成可审计契约。
- **产物**：`core/agents/restaurant_beta_boundary.py`、`examples/capability_proof/restaurant_prod_beta_manifest.json`、`docs/verification/restaurant_prod_02_restaurant_beta_boundary.md`、`scripts/run_restaurant_beta_boundary_contract.py`、`tests/core/test_rest_prod_02_restaurant_beta_boundary.py`。
- **证据**：focused 6 tests OK；restaurant beta benchmark 8/8 pass（7×`benchmark_pass_non_cad` + 1×`blocked_expected_non_cad`）；registry 已有 8 行 `benchmark.restaurant_scene_beta_benchmark.*`。
- **口径**：代码轨当时更新为 **45/55（约 82%）**。本包未运行真实 CAD，不新增 `geometry_verified`。

### 2026-05-27 REST-PROD-01：餐饮 alpha 边界收口

- **一键推进**：完成 `REST-PROD-01-RESTAURANT-ALPHA-BOUNDARY`，按 `OFFICE-PROD-01` 模式把 restaurant alpha 入口收成可审计契约。
- **产物**：`core/agents/restaurant_alpha_boundary.py`、`examples/capability_proof/restaurant_prod_alpha_manifest.json`、`docs/verification/restaurant_prod_01_restaurant_alpha_boundary.md`、`scripts/run_restaurant_alpha_boundary_contract.py`、`tests/core/test_rest_prod_01_restaurant_alpha_boundary.py`。
- **证据**：focused 7 tests OK；`output/validation_runs/rest-prod-01-boundary-no-cad/restaurant_alpha_boundary_summary.json` 为 `status=pass`；scene alpha 中 `scene_alpha_restaurant_blank_shell` no-CAD case 通过，选择 `l_spine`，证据态为 `benchmark_pass_non_cad`。
- **口径**：该轮代码轨更新为 **44/55（约 80%）**；后续已推进到 `REST-PROD-02`。本包未运行真实 CAD，不新增 `geometry_verified`。

### 2026-05-27 V-PROOF-35：fallback tier rows 表 C 推进

- **能力证明**：完成 `V-PROOF-35-FALLBACK-TIER-ROWS`，在 `cad_capability_registry` 新增 5 个 fallback tier 行：`block`、`symbol_glyph`、`component_preview`、`bbox_placeholder`、`deferred_unsupported_symbol`。
- **证据边界**：4 行为 `smoke`，1 行为 `deferred`；全部写明 `not_verified_without_cad_readback`，不把 fallback 解析、dry-run 或 deferred 当成真实 CAD `geometry_verified`。
- **验证**：`tests.core.test_symbol_08_glyph_fallback_boundary`、`tests.core.test_symbol_fallback_policy`、registry seed 与 coverage focused tests 共 21 tests OK；`run_capability_coverage.py` 已复跑。
- **表 C 机器值**：该条为历史快照；当前最新值为 `total_count=282`、`verified_count=112`、`showcase_count=25`、CAD 证明覆盖率 **48.58%**、CAD 实力指数 **51.03%**、真实 CAD 实力主指标 **8.87%**、最高已证 **L4**。
- **任务台账**：该条后能力证明为 **27/43 done**；当前已随 `V-PROOF-42` 更新为 **35/45 done**；当前后续项见 `docs/planning/任务清单.md` §0。

### 2026-05-27 诊断层隔离小收口

- **边界修正**：能力探针 / complex smoke 的文字、尺寸等说明性对象改写入 `CODEX_DIAGNOSTIC`；`CODEX_PREVIEW` 保持为用户可见几何层，避免旧探针标注污染当前图块视口。
- **安全口径**：`CODEX_DIAGNOSTIC` 被纳入 preview-only 允许写入层，但必须显式使用 `layer_role="diagnostic"`；默认 preview 角色写诊断层会被 guard 拦截，仍禁止保存、删除、覆盖和正式图层写入。
- **报告口径**：报告分开统计 `preview_type_counts` 与 `diagnostic_type_counts`，避免把诊断标注算作用户生成层内容。
- **验证**：`tests.core.test_cad_capability_probe` 与 `tests.core.test_complex_cad_smoke` 聚焦单测通过；本收口不新增真实 CAD `geometry_verified`，不改变表 C 机器值。

### 2026-05-27 最终回复精简口径

- **交付模板**：聊天最终回复从旧的完整 A/B/C 强制展开，改为“默认 1 张精简进度表”：先报表 C 主指标，再报本轮进展 / 验证、表 A 折叠工程节奏、表 B 本轮相关中文轨道（能力证明 / 代码轨 / CAD 补验）。
- **展开条件**：完整状态汇报、交接、审计、进度盘点、表 C 专题、更新 registry/showcase/coverage，或改变能力证明 / 代码轨 / CAD 补验计数时，仍展开完整表 A/B/C。
- **包计数**：本轮只改展示口径，不重构能力证明 43 包、代码轨 55 包、CAD 补验 29 包分母，也不新增真实 CAD `geometry_verified`。

### 2026-05-27 文档治理收尾：表 A/B/C 口径同步

- **V-PROOF-44 + RCAD-23**：drawing standard beta 从 smoke 推进到真实 CAD 子集证据；`output/validation_runs/rcad-23-drawing-standard-beta-20260527-escalated/drawing_standard_cad_smoke_report.json` 为 `status=geometry_verified`，created handle `36A`，styled `insert_block_alpha` 在 `CODEX_PREVIEW` 回读为 `block_reference`。
- **登记回写**：仅 `drawing_standard.beta.drawing_standard_beta_04` 与 `drawing_standard.beta.block_insert_plan_resolution` 回写 `verified`；object role、primitive style、semantic layer case 保持 smoke，不算真实 CAD 几何 verified。
- **表 C 机器值**：该轮 `cad_capability_coverage.json` 为 `total_count=277`、`verified_count=122`、`showcase_count=12`、CAD 证明覆盖率 **48.38%**、CAD 实力指数 **51.33%**、真实 CAD 实力主指标 **4.33%**、最高已证 **L4**；当前最新值见本页 V-PROOF-35 条目。
- **任务台账**：该轮能力证明更新为 **26/43 done**，RCAD 烟囱更新为 **25/29 verified**；当前最新任务台账见本页 V-PROOF-35 条目。
- **V-PROOF-34 + RCAD-25**：block-first tier 已从 no-CAD smoke 推进到真实 CAD 回读证据；`output/validation_runs/rcad-25-symbol-block-first-20260527-escalated/symbol_block_first_cad_smoke_report.json` 为 `status=geometry_verified`，created handle `369`，`CODEX_TEST_BLOCK_001` 在 `CODEX_PREVIEW` 回读为 `block_reference`。
- **登记回写**：仅 `symbol.block_first.symbol_block_first_tier_01` 与 `symbol.block_first.controlled_block_wins` 回写 `verified`；`metadata-only-block-falls-to-glyph` 和 `block-preferred-without-library-glyph` 保持 smoke，不算真实 CAD 几何 verified。
- **V-PROOF-34 当时快照**：该包后 `verified_count=120`、CAD 证明覆盖率 **47.65%**、CAD 实力指数 **51.19%**；最新机器值见上方 RCAD-23 条目。
- **任务台账**：该轮 `docs/planning/任务清单.md` §0 已同步为能力证明约 **26/43 done**、代码轨约 **43/55 done**、RCAD **25/29 verified**；当前最新任务台账见本页 V-PROOF-35 条目。
- **主从关系**：`CORE_RESTRUCTURE_PLAN.md` 继续决定方向、优先级和退出门槛；`docs/planning/任务清单.md` 只做三指令执行台账和当前 `next` 镜像。

### 2026-05-27 OFFICE-PROD-03：办公 P3 波次父包收口

- **一键推进**：完成 `OFFICE-PROD-03-OFFICE-P3-WAVE-ROLLUP`，统一收口 `OFFICE-PROD-01` alpha 边界与 `OFFICE-PROD-02` beta 边界。
- **产物**：`core/agents/office_p3_wave.py`、`scripts/run_office_p3_wave_rollup.py`、`docs/verification/office_prod_03_p3_wave_acceptance.md`、`tests/core/test_office_prod_03_p3_wave_rollup.py`。
- **证据**：`output/validation_runs/office-prod-03-p3-rollup-no-cad/office_p3_wave_summary.json`；alpha benchmark 18/18 pass，beta benchmark 9/9 pass（7 pass + 2 blocked_expected），`readback_geometry_verified_count=0`。
- **口径**：代码轨当时更新为 **43/55（约 78%）**。本包未运行真实 CAD，不新增 `geometry_verified`。

### 2026-05-27 RCAD-22：capability probe beta 真实 CAD 补验

- **真实 CAD**：`scripts/run_cad_capability_probe.py` 在用户 AutoCAD 会话 `Drawing1.dwg` 通过，证据为 `output/validation_runs/rcad-22-capability-probe-beta-20260527-escalated/cad_capability_probe.json`。
- **回读结果**：`status=cad_capability_verified`，11 个 created handles（line 5、circle 1、arc 1、polyline 1、text 1、dimension 2），全部在 `CODEX_PREVIEW`，bbox 为 900×450，`session_guard.status=consistent`。
- **登记回写**：`primitive.arc/circle/dimension/line/polyline/rectangle/text` 的 report path 已刷新到本轮 RCAD-22 证据；该历史报告中 `primitive.hatch` 仍为 structured deferred，当前已由 `RCAD-06` 独立补验升级为 verified。
- **覆盖率复跑**：本条为 RCAD-22 当时快照；后续表 C 已多轮更新，当前最新值见本页 `RCAD-06` 条目。
- **任务台账**：RCAD-22 后为 **23/29 verified**；最新 RCAD 烟囱已随 RCAD-23 更新为 **25/29 verified**。

### 2026-05-27 能力证明：表 C 复跑 + RCAD-18 真实 CAD

- **真实 CAD**：`output/validation_runs/capability-proof-table-c-20260527/all_subscenes/` — meeting+reception 4/4 `geometry_verified`（各 4 handles）。
- **Registry 回写**：4 行 catalog 证据路径刷新（`writeback_batch.json --apply`）。
- **表 C（V-PROOF-63）**：`cad_capability_coverage.json`（2026-05-27T07:51:20Z）曾把主指标抬到 L4 showcase 阶段；后续 registry 分母扩展后，当前机器值见本页顶部。
- **RCAD-18**：已 `verified`；该条记录是当时快照。当前 RCAD 烟囱已随 `RCAD-23` 更新为 **25/29**。

### 2026-05-27 CFIT-12：工装子场景代表对象 CAD smoke

- **manifest**：`fitout_subscene_object_cad_smoke_manifest.json`（meeting_room + reception 各 2 代表对象）。
- **runner**：`run_fitout_subscene_object_cad_smoke.py`；fake 4/4 geometry_verified。
- **验证**：`tests/core/test_cfit_12_fitout_subscene_object_cad_smoke.py` 6 tests OK。

### 2026-05-27 CFIT-11：工装三样本 boundary / rollup 口径同步

- **契约**：`deidentified_project_samples[]` 对齐 open_office / meeting_room / reception 与三 `sample_id`。
- **代码**：`assert_fitout_three_sample_rollup_sync()`；`fitout_sample_specs.subscene_id`。
- **验证**：`tests/core/test_cfit_11_three_sample_boundary_sync.py` 5 tests OK。未跑真实 CAD。
- **边界**：`docs/verification/cfit_11_three_sample_product_boundary_sync.md`；`RCAD-10` / `RCAD-19` 仍待逐项补验。

### 2026-05-27 CFIT-10：前台接待脱敏项目样本

- **样本**：`projects/commercial_fitout_reception_sample/`（`reception` 子场景）。
- **三样本覆盖**：`commercial_fitout_sample` + meeting + reception；`fitout_sample_specs` 三键齐全。
- **rollup**：`project_sample_cad_rollup.json` 第四行；fake 单测 4/4 geometry_verified。
- **验证**：`tests/core/test_cfit_10_reception_sample.py` 4 tests OK。未跑真实 CAD。

### 2026-05-27 CFIT-09：第二组工装脱敏项目样本

- **样本**：`projects/commercial_fitout_meeting_sample/`（会议室；协议扫描 pass）。
- **管道**：`fitout_sample_specs.py` + 参数化 confirmation / CAD smoke / rollup（按 workflow 解析 sample）。
- **登记**：`examples/cad_regression/project_sample_cad_rollup.json` 新增第三样本行。
- **验证**：`tests/core/test_cfit_09_meeting_sample.py` 4 tests OK；rollup fake 3/3 geometry_verified。
- **边界**：`docs/verification/cfit_09_second_project_sample_boundary.md`；`RCAD-10` 路径已就绪，真实 CAD 待补验。

### 2026-05-27 LCAD-14：Guard 全链路 strict 包装

- **一键推进**：完成 `LCAD-14-GUARD-FULL-CAD`；`run_guard_full_cad_runner.py` 输出 `guard_full_cad_report.json` 与 `subreports/` 三段子报告。
- **strict_gate**：fake 模式 `status=pass`；要求 write guard、negative CAD、`cad_capability_verified` + `session_guard=consistent`。
- **证据**：`output/validation_runs/lcad-14-guard-full-no-cad/guard_full_cad_report.json`。
- **验证**：focused 3 tests OK。本包未运行真实 CAD；`RCAD-21` 待用户会话 `--real-cad` 补验。
- **队列**：§4.1（LCAD-10~14 + CAD-VAL）已全部 done；代码轨 next 转入 §4.2 波次占位包。

### 2026-05-27 NEG-CAD-PROOF-SYNC：负向安全 runner、覆盖率可读证据、composition 收口

- **负向安全 runner**：新增 `run_negative_cad_runner.py`，汇总 negative CAD_PLAN 8/8、write guard、ActiveDocument snapshot、no-handle/no-save/no-delete/no-formal-layer 证据。
- **安全补强**：`AutoCADComDriver` 基础写入方法改为 COM `Add*` 前先执行 preview-layer guard，防止正式图层负向 case 在抛错前已落实体。
- **RCAD-20 真实负向补验**：沙箱内真实 CAD COM 不可见时为 `external_blocker`；按审批沙箱外重跑后通过，证据为 `output/validation_runs/rcad-20-negative-cad-20260527-escalated/negative_cad_runner_report.json` → `status=pass`、`evidence_state=negative_guard_verified`、`created_handles=[]`、不保存、不删除、不改正式图层、entity delta=0。
- **V-PROOF-33 readability rows**：能力登记表新增 5 个 `symbol.readability_status.*` smoke 行，证据为 `output/validation_runs/vproof-33-readability-rows/capability_readability_report.json`；该条为历史快照，当前覆盖率以本页顶部机器值为准。
- **证据**：fake/no-CAD 负向 runner `output/validation_runs/neg-cad-proof-sync/negative-runner-fake-final/negative_cad_runner_report.json` → `status=pass`、`evidence_state=negative_guard_verified`、`created_handles=[]`；真实 `RCAD-20` 同为 guard-only，不新增真实 CAD 几何结论。
- **覆盖率可读报告**：`output/validation_runs/vproof-33-readability-rows/capability_readability_report.json`，分组显示 geometry verified / guard-only / deferred / smoke / none / blockers；guard-only 与 readability smoke 行均不计作几何证明。
- **composition 收口**：沿用 JSON catalog + schema；全局默认无标注，运行时对象级 `include_label/include_dimensions` 被忽略，避免 composition 预览文字/标注漂移。
- **LCAD-10.4**：新增 `docs/verification/negative_cad_safety_boundaries.md`，把负向 fixture 分类、安全扫描字段、`RCAD-20` 真实 CAD 补验门槛和不得声称边界固定下来。
- **LCAD-10.5**：新增 `docs/verification/negative_cad_safety_acceptance.md`，父包 `LCAD-10-NEGATIVE-SAFETY` 收口，next 推到 `LCAD-11.1`。
- **LCAD-11.1**：新增 `evidence_trend` 契约模块、schema、最小样例和 schema registry 接入；趋势 JSON 后续统一使用完整 `evidence_state_counts`，并把 `negative_guard_verified` 固定为 guard-only。
- **验证**：NEG-CAD focused 35 tests OK；LCAD-10.4 focused 4 tests OK；LCAD-10.5 focused 6 tests OK；LCAD-11.1 focused 31 tests OK；V-PROOF-33 focused 29 tests OK、全量 674 tests OK、repo audit 0 findings、`git diff --check` 无空白错误。真实 `RCAD-20` 已完成 guard-only pass，不新增 `geometry_verified`。

### 2026-05-27 CAD 能力覆盖表提升

- 证据：`output/validation_runs/capability-lab-coverage-wave-20260527/`（fitout composition 3/3 + 镜像回写批次）。
- **CAD 证明覆盖率**：该节为历史波次快照，当前机器值见本页顶部。
- 工具：`run_composition_cad_registry.py`（fitout manifest）、`build_coverage_expansion_writeback.py` + `run_capability_registry_writeback.py --apply`。

### 2026-05-27 CAD 校验波次（glyph 矩阵 + office composition）

- 证据：`output/validation_runs/capability-lab-cad-validation-20260527/`（glyph 6/6；office composition 4/4；write-guard runner pass）。
- **CAD 证明覆盖率**：**108/257（42.02%）** — 新增 4 个 office `composition.*` verified；archetype 证据刷新。
- **入口**：`run_symbol_glyph_cad_matrix.py`、`run_composition_cad_registry.py --manifest office_composition_cad_registry_manifest.json`、`run_write_guard_cad_runner.py`。
- **测试**：658 OK。

### 2026-05-27 安全层校验收口

- **驱动守卫**：`AutoCADComDriver` 与 `FakeCadDriver` 共用 `PreviewWriteGuardMixin`（`CadWriteGuard`）；非 preview 图层写入与 DWG save/delete 在驱动层即拒。
- **路径边界**：`intent_lab_cad`、`run_intent_lab_cad.py`、`run_block_alpha_validation.py` 的 plan/output 限制在 project root / `output/` 树内。
- **测试**：654 OK（含 `test_path_safety`、`test_autocad_write_guard`）。

### 2026-05-27 V-PROOF-22/31/43 能力证明轨

- 证据：`output/validation_runs/capability-lab-vproof-20260527/`（demand 10/10、composition 3/3、monitor/rug glyph）。
- **CAD 证明覆盖率**：**104/257（40.47%）** — demand benchmark×10；composition×3；symbol 30 verified；object 28/28。
- **测试**：649 OK。

### 2026-05-27 CAD 证明覆盖率 wave

- 证据：`output/validation_runs/capability-lab-coverage-wave-20260527/`（历史波次，已被 vproof 包覆盖提升）。
- **CAD 证明覆盖率**（历史）：**87/255（34.12%）**。

### 2026-05-27 登记表完善（fitout catalog 14 + glyph 回写）

- 证据：`output/validation_runs/capability-lab-registry-20260527/`（fitout_catalog_cad 14/14；`cad_capability_writeback_registry_batch.json`）。
- **CAD 证明覆盖率**（历史）：**59/254（23.23%）** — 已被上节 86/254 取代。
- 回写脚本：`scripts/build_registry_writeback_batch.py` + `run_capability_registry_writeback.py --apply`。
- 全量回归：**645 tests OK**。

### 2026-05-27 §5 CAD 补验 + 登记表回写 sprint

- 证据根目录：`output/validation_runs/capability-lab-sprint-20260527/`、`...-extra/`。
- **CAD 证明覆盖率**（V-PROOF 包后）：**42/254（16.54%）** — 已被上节 59/254 取代；历史证据 `capability-lab-vproof-20260527/`。
- 全量回归：**637 tests OK**。

### 2026-05-27 并行：V1 Intent Lab + LCAD-10.1 + RCAD-01

- **Intent Lab**：6 intent 最小 plan + `intent_lab_manifest.json`；`draw_annotation` / `modify_object` / `delete_object` 标 `deferred`（仅 validate/dry-run）。
- **负向安全**：8 个负向 `CAD_PLAN` fixture + schema/validate 双拒；CLI `run_negative_cad_plan_suite.py`。
- **几何门禁**：`run_cad_validation.py --geometry-gate --require-geometry-pass`；RCAD-01 复验目录 `output/validation_runs/rcad-01-baseline-geometry/`。
- **登记表**：`regression.baseline_cad_validation` → `verified`；CAD 证明覆盖率 **0.4%**（1/252）。
- 全量回归：**637 tests OK**。

### 2026-05-27 V-PROOF-04/05：三口径状态页 + handoff 模板

- **V-PROOF-04-STATUS-SYNC**：`CORE_STATUS.md` 增加固定「三进度口径」节；禁止单独用 Core 94% 暗示 CAD 已证；CAD 证明覆盖率以 `cad_capability_coverage.json` 为准（当前 **0%** / 252 行）。
- **V-PROOF-05-HANDOFF-TEMPLATE**：交接 9 项扩展能力证明附加表（`capability_id`、`claim_level`、`ladder_level`、覆盖率路径）；见 `docs/verification/capability_proof_handoff_template.md` 与 `evidence_gate_handoff_rules.md` §7。
- 全量回归：**629 tests OK**。

### 2026-05-27 V-PROOF-03：登记表 loader + RCAD 回写 API

- **V-PROOF-03-REGISTRY-LOADER** 已收口：`capability_registry_writeback.py` + `scripts/run_capability_registry_writeback.py`（dry-run 默认，`--apply` 写回并校验）。
- 回写规则：仅当报告为 `readback_geometry_verified` / `cad_capability_verified` 时可将行升为 `verified`；须带 `evidence.report_path`；支持从 `local_cad_regression` 输出目录 `--suggest-from-regression`。
- 当前最新回归基线：**629 tests OK**（含 writeback 6 tests）。
- §3 能力证明 next：**V-PROOF-04-STATUS-SYNC**。种子登记表仍为 0% verified，直至用户对真实 RCAD 目录执行 `--apply`。

### 2026-05-27 V-PROOF-02：CAD 能力证明覆盖率

- **V-PROOF-02-COVERAGE-REPORT** 已收口：`scripts/run_capability_coverage.py` → `output/validation_runs/capability-lab/cad_capability_coverage.json`。
- **CAD 证明覆盖率首算**：252 登记行，`verified`+`showcase` 当时为零。回写 API 已就绪，待对真实报告 `--apply` 后复跑覆盖率。

### 2026-05-27 V-PROOF-01：CAD 能力登记表种子

- **V-PROOF-01-REGISTRY-SEED** 已收口：`examples/capability_proof/cad_capability_registry.json` **252 行**（自动生成器 `capability_registry_seed.py`）；全部为 `none`/`deferred`/`smoke`，尚无 `verified` 回写。

### 2026-05-27 V-PROOF-00：CAD 能力登记表 Schema

- **V-PROOF-00-REGISTRY-SCHEMA** 已收口：`cad_capability_registry.schema.json` + `capability_registry_contract` + invalid fixture + 最小样例 JSON。

### 2026-05-27 P0：schema registry + FakeDriver + unittest 全绿

- 全量基线：**609 tests OK**（P0 收口时；含于当前 615）。
- P0 收口项：`MODEL_SCHEMAS` / invalid fixtures、`FakeCadDriver` 写保护与 block alpha、fitout composition 失败分类接入 benchmark runner、`commercial_fitout` domain 校验与 schema 双份同步。
- repo audit：`scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings` → **0 findings**（`templates` / `local_cad_regression` 及关联模块已拆分）。
- 本轮未重跑真实 AutoCAD；不新增 `geometry_verified` 结论。§3 能力证明（`V-PROOF-00` registry schema）仍待下一包。

### 2026-05-26 Codex 本地 CAD 回归矩阵加固

- 当前最新回归基线：`456 tests OK`。
- 新增本地 CAD 回归矩阵：`core/verification/local_cad_regression.py` + `scripts/run_local_cad_regression.py`，把 baseline 总控、project sample CAD check 和 interior composition CAD check 统一汇总为 `local_cad_regression_report.json`。
- no-CAD 安全复验：`scripts/run_local_cad_regression.py --no-cad --output-dir output\validation_runs\local-cad-regression-no-cad` 为 `status=pass`，`step_count=3`，`deferred_case_count=2`，`geometry_verified_case_count=0`。
- 严格模式门禁：真实 CAD 模式可加 `--require-cad-verified`；project sample 或 composition 任一子项不是 `geometry_verified` 时，矩阵顶层失败，避免 deferred / 顶层 pass 被误读。
- 依赖保护：composition CAD check 只有在 `interior_delivery_benchmark` 成功产出 artifacts 后才运行；前置失败时记录 `not_run` 和 `blocked_by`，不会拿空目录或旧产物继续写 CAD。
- 本轮未运行真实 AutoCAD，不新增 `geometry_verified` 结论；新增的是“本地真实 CAD 回归入口和 no-CAD 负向证据门禁”。

### 2026-05-26 Codex 进入下一阶段前雕琢

- 当前最新回归基线：`452 tests OK`；`scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings。
- no-CAD 总控复验：`scripts/run_cad_validation.py --no-cad --output-dir output\validation_runs\codex-polish-final-no-cad` 为 `status=pass`。
- 可迁移性修复：`docs/runbooks/blocker-playbook.md` 的 CAD-MCP Python 命令不再写死固定 Windows 用户目录，改为 `$env:USERPROFILE` 派生；新增文档治理测试防止活跃手册回退到固定用户路径。
- CLI 易用性修复：`run_office_scene_beta_benchmark.py`、`run_residential_scene_beta_benchmark.py`、`run_restaurant_scene_beta_benchmark.py` 现在同时支持 `--output` 和 `--output-root`，与通用 benchmark runner 的参数习惯对齐。
- 复验脚本：blank-shell benchmark 8/8、office alpha 18/18、interior delivery 3/3、project sample 2/2、proposal confirmed 2/2、CAD beta evidence rollup 5/5、scene beta 三套合计 25/25 均通过。本轮未运行真实 CAD，不新增 `geometry_verified` 结论。

### 2026-05-26 Codex 维护 4-7 包：结构整理和优化

- 当前最新回归基线：`450 tests OK`；`scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings。
- 结构整理：新增 `core/path_safety.py`，公共化 project root / output root / safe path segment 校验，减少各 runner 私有路径判断重复。
- 安全入口加固：project sample CAD check、composition CAD check、beta suite、proposal confirmed、drawing-read、blank-shell / non-CAD pipeline 等入口在写 artifact、读取 workflow 或连接 AutoCAD 前先做边界校验；无效输入统一输出结构化 invalid / blocker，不再抛散乱异常或越界写入。
- Schema registry 整理：所有 `core/schemas/*.schema.json` 已纳入 `MODEL_SCHEMAS`，并补齐 invalid fixtures，防止 schema 文件存在但 validator 不知道。
- 文档治理：`docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` 不再承载下一包建议或剩余 Backlog 副表；状态页只记录证据和风险，优先级仍只以唯一 `PlanMD` 为准。

### 2026-05-26 Codex 维护 1-3 包：证据止血、基线同步、路径安全

- 当前最新回归基线：`432 tests OK`；`scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings。
- 证据口径修正：`BETA-PROJECT-SAMPLE-05` 当前仓库存档 no-CAD 报告是 `deferred`，不是真实 AutoCAD `geometry_verified`；新增 `--require-cad-verified` 后，deferred 报告会返回非 0，避免交接或 CI 误判。
- 路径安全加固：样本 manifest input 必须留在样本目录内；benchmark / drawing-read `case_id` 必须是安全 path segment；benchmark output root、drawing-read output root、CAD validation output dir 均限制在仓库 `output/` 下。
- 验收脚本：focused 1-3 包测试 48 OK；no-CAD validation `output\validation_runs\codex-maintenance-fix-no-cad` pass；blank-shell benchmark 8/8 pass；office alpha benchmark 18/18 pass；interior delivery benchmark 3/3 pass；strict no-CAD project sample CAD check 按预期返回 1 并保存 deferred 报告。

### 2026-05-26 Codex 深度全量安全复盘与加固

- 本轮历史回归基线：`424 tests OK`；`scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings。
- 本轮从 Cursor 大量改动后做了全量盘查：Python AST 解析 `248` 个文件 0 errors，JSON 解析 `166` 个文件 0 errors，坏证据词 / 系统临时目录回归 / 旧 blank-shell 内部入口引用均未命中。
- 修复 `tests/core/test_project_sample_protocol.py` 使用系统 temp 造成的 `PermissionError` 回归，测试临时目录统一回到 `output/test_artifacts`。
- 加固 benchmark evidence gate：所有 `examples/benchmarks/*.json` case 必须包含 `expected.evidence_state` / `geometry_accuracy` / `screenshot_role`；`proposal_confirmed_benchmark` 现在输出并校验 `evidence_summary`。
- 修复项目样例 CAD check 与 drawing standard profile 的证据词表偏差：失败/延期路径统一使用 `deferred_cad_readback_required` + `not_verified_without_cad_readback`，`screenshot_role` 统一使用 `not_applicable` / `visual_aid_only` 合法词。
- repo audit 暴露的 6 个过大 Python 文件已拆分：benchmark expected 比对、evidence vocabulary、composition preview、blank-shell candidate sets、CAD validation 测试 payload、benchmark validation tests 均已独立成小模块；旧公开入口保持兼容。
- 验收脚本：`self_check.py` pass；`render_preview.py --check` ready（当前环境 AutoCAD window unavailable，截图仍仅为视觉辅助）；`run_project_sample_protocol_scan.py` pass；`run_project_sample_benchmark.py` 2/2 pass；`run_proposal_confirmed_benchmark.py` 2/2 pass；`run_cad_beta_evidence_rollup.py` 5/5 pass；office/residential/restaurant scene beta benchmark 分别 9/9、8/8、8/8 pass。

### 2026-05-26 Codex 第二轮风险验收补记

- 当轮回归基线：`290 tests OK`；`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings。
- 第二轮加固重点：CAD validation runner 现在会把 `inspect_readback` / `block_alpha_readback` 报告中的 created handles 与上一阶段 `execution_summary.json` / `block_alpha_execution_summary.json` 交叉比对，防止 fake JSON 自带另一套 handles 通过。
- `block_alpha_report.status=geometry_verified` 现在必须包含 `created_handles_scope=pass`、唯一 created handle、`block_reference` 实体 payload，以及 `block_name` / `insertion_point` / `rotation` / `scale` / `layer` / `bbox` 几何字段。
- `insert_block_alpha` 继续加固失败路径：attributes、非法 base point、非受控 identity 在任何 ModelSpace 写入前拒绝；插入后若 handle 缺失或后置校验失败，会尝试删除刚创建的 block reference；同名 `CODEX_TEST_BLOCK_001` 块定义复用前会校验 900x450、4 条线、layer `0`。
- 第二轮真实 CAD 验收：`output/validation_runs/codex-second-gate-block-alpha-cad-final/report.json` 和 `output/validation_runs/codex-second-gate-full-cad-final/report.json` 均为 `status=pass`；block handles 分别为 `99B` 和 `ABC`。
- 第二轮负向 COM 探针通过：非法 `block_id`、非法 `block_name`、attributes、非法 `base_point` 均被拒绝，当前测试 DWG 的 ModelSpace 实体数 `131 -> 131`。

### 2026-05-26 Codex 风险验收补记

- 当轮回归基线：`290 tests OK`；`run_repo_audit.py --max-python-lines 500 --fail-on-findings` 为 0 findings。
- `office_alpha_benchmark.json` 复跑 14/14 pass（non-CAD），证据目录：`output/test_artifacts/benchmarks/codex_review_office_alpha_after_refactor/`。
- `run_cad_validation.py --no-cad --block-alpha-only` 现在包含 `block_alpha_deferred_evidence`，证据目录：`output/validation_runs/codex-review-block-alpha-only-no-cad-after-refactor/`。
- 真实 CAD block alpha 复验通过：`output/validation_runs/codex-review-block-alpha-cad-after-gate/report.json`，created handle `879`，`block_alpha.geometry_verified=true`。
- 完整真实 CAD validation 通过：`output/validation_runs/codex-review-full-cad-after-gate/report.json`，baseline handles `87A..8C4` 与 block handle `99A` 均完成 created-handle readback。
- 负向 COM 探针通过：任意 `block_id` / 任意 `block_name` 被拒绝，当前测试 DWG 的 `CODEX_PREVIEW` 实体数 `111 -> 111`，未新增实体。
- 本轮只证明受控 `CODEX_TEST_BLOCK_001` 样本和当前测试会话下的 validation 链路，不扩大到真实公司块库、属性块、正式图层或任意项目图纸。

当前处于：

```text
Phase O-V 非 CAD 主线已完成
系统层安全补强与自检已完成
Phase W 已执行到 W-16；baseline 真实 CAD 回读闭环已验证通过
Phase R 角色驱动组合交付已从 non-CAD benchmark 推进到 3 个组合的真实 CAD batch readback
```

也就是说，仓库已经具备一条可运行的非 CAD 空壳布局 Alpha 原型链路；本轮已查明默认沙箱命令无法调用已打开 CAD 的根因，并在用户会话下完成 Phase W baseline 真实 CAD 落图、截图、实体回读和 `geometry_verified` 闭环。最新加固还补上了“顶层 pass 但 readback 未验证”的门禁漏洞，改为优先按本轮 created handles 定向回读真实 CAD 实体，并新增 CAD COM 能力矩阵探针验证底层调用能力。2026-05-25 22:08 又将能力矩阵从矩形/文字/标注扩展到独立直线、圆、弧和闭合多段线，并留下缩放后的截图证据。2026-05-25 之后，本轮角色组合交付已按用户指出的“必须在 CAD 里面”修正：卧室床+地毯、餐桌组合、办公桌组合已在 AutoCAD `CODEX_PREVIEW` 图层完成真实批量落图、created handles 定向回读和截图验证。

## 已确认事实

- 本仓库是通用 CAD Agent Core Lab，不绑定当前 DWG、当前家装图或当前电脑。
- 用户提到 `PlanMD`、`plan.md`、主计划或主 plan 时，当前默认指 `CORE_RESTRUCTURE_PLAN.md`；根目录没有独立 `plan.md`。
- `docs/architecture/shell-layout-foundation-design.md` 的核心路线已经被纳入主计划，并在 Phase P-V 中部分落地。
- `scripts/run_cad_validation.py` 已成为 CAD 层面检查总控入口。
- `CORE_RESTRUCTURE_PLAN.md` 已收缩为主计划总控索引；Phase W/X/Y/Z 的长篇执行剧本已迁入 `docs/planning/`。
- `CORE_CONTEXT_BRIEF.md` 是日常恢复上下文的短入口。
- Phase W W-05 已审查 `output\validation_runs\phase-w-preflight-no-cad\report.json`：无失败步骤需要分类。
- Phase W W-06 只读 AutoCAD COM 探针曾在默认沙箱身份下落证据到 `output\validation_runs\phase-w-w06-cad-probe\`，并暴露 `AutoCAD.Application` ProgID / 用户会话隔离问题；后续用户会话诊断已确认 COM 可用。
- Phase W W-07 真实 CAD 底座最新稳定报告为 `output\validation_runs\manual-cad-after-primitive-probe\report.json`，顶层 `status=pass`；`readback_report.json.status=geometry_verified`；`cad_capability_probe.json.status=cad_capability_verified`；关键 checks 全部 `pass`。
- 本轮已确认此前“CAD 已打开但无法调用”的主因是执行上下文隔离：默认沙箱身份 `desktop-r40v31q\codexsandboxoffline` 看不到用户桌面的 AutoCAD 进程、窗口和 ROT/COM 活动对象；用户会话身份 `desktop-r40v31q\user` 下 `AutoCAD.Application`、`.25.1`、`.25` 均可 `GetActiveObject`。
- 已完成七项加固：`AutoCADComDriver(connect_existing_only=True)` 连接失败时保留底层 COM detail 并尝试版本化 ProgID；`cad_validation_runner` 在 CAD 前置失败后跳过依赖步骤并清理旧派生 artifact；`AutoCADComDriver` 现在把点坐标转换为 AutoCAD COM 需要的 `VT_ARRAY | VT_R8` float VARIANT；`cad_validation_runner` 对 `inspect_readback` 增加 `geometry_verified` 和 checks 全 pass 硬门禁；`inspect_dwg.py` / `AutoCADComDriver` 支持按 created handles 定向回读，避免真实大图全量 ModelSpace 扫描；`cad_capability_probe` 已纳入总控，验证活动文档、preview 图层、矩形/文字/标注写入、handle 回读、类型统计、bbox 和安全边界；能力探针现已覆盖 `draw_line`、`draw_circle`、`draw_arc`、`draw_polyline` 并能回读识别 `line` / `circle` / `arc` / `polyline`。
- 主平台 Markdown 精细化拆分已执行；后续恢复开发时先读 `CORE_CONTEXT_BRIEF.md`，再按目标阶段读取 `docs/planning/phases/*.md`。
- 二次文档架构雕琢已执行：`docs/README.md` 成为文档区总地图，`docs/ROADMAP.md` 降级为兼容跳转，`docs/onboarding/README.md` 已补换机清单入口。
- 本轮继续收束文档权威关系：`CORE_RESTRUCTURE_PLAN.md` 是唯一 PlanMD / 开发主线；`docs/planning/phases/*.md` 是辅助执行剧本；状态、路线、架构、治理、验证和历史文档只服务主线，不生成第二套待办，也不保留后置 Backlog 副本。
- 最后一轮防偏离收尾已明确：PlanMD 只做文档治理和开发排序，不改变通用 Core Lab、Core 优先、`CAD_PLAN` 中间层、真实 CAD 验证门槛和场景轻量化方向。
- Phase R 新鲜视角评审已启动并落文档：`docs/reviews/fresh-eyes-review-2026-05-25.md` 记录多名只读专家 agent 建议，`docs/planning/phase-r-fresh-perspective-rebirth-plan.md` 作为后续重生式开发校准入口。
- Phase R 已进一步细化为执行开发包：`docs/planning/phase-r-rebirth-implementation-plan.md`、`phase-r-cad-capability-contract.md`、`phase-r-block-library-roadmap.md`、`phase-r-office-benchmark-cases.md`、`docs/governance/multi-agent-contribution.md`、`docs/onboarding/first-handoff.md`。
- Phase R 第一批代码切口已落地：benchmark runner 支持 `evidence_state`、`geometry_accuracy`、`screenshot_role`、`minimums`、`contains_object_types`、`contains_component_roles`、suite/case 配置校验和 `object_spec` pipeline；blank-shell pipeline 已输出每个 CAD_PLAN 的 dry-run / verification 汇总证据；新增 `examples/benchmarks/office_alpha_benchmark.json`，用于验证 desk / chair / cabinet 对象规格、office blank-shell 对象类型和 non-CAD 证据状态。
- Phase R 第二批代码切口已落地：新增 `core/composition_engine/`，支持将卧室床+地毯、餐桌+椅、办公桌+椅+显示器这类角色需求转成组合规格、多 CAD_PLAN、dry-run、unverified verification 和 SVG/PNG 视觉辅助预览；benchmark runner 新增 `composition_spec` pipeline、`contains_object_roles` 断言和 `examples/benchmarks/interior_delivery_benchmark.json`，当前 3 个 persona composition cases 在 non-CAD 下通过。
- Phase R 第三批真实 CAD 校验已落地：新增 `core/execution/batch_plan_runner.py` 与 `scripts/run_composition_cad_check.py`，可将 benchmark 产出的多 CAD_PLAN 按 case 偏移批量写入 AutoCAD，并对本轮 created handles 做逐 plan `geometry_verified` 回读；脚本支持 `--start-x` / `--start-y` / `--spacing-x`，避免为了取干净截图而删除旧预览实体。
- `R-CAD-VIEW-CAPTURE` baseline 已落地：`render_preview.py` 支持 AutoCAD 窗口级截图与 created handles bbox 聚焦；`run_cad_validation.py` 已改为输出 `cad-validation-window.png`，截图继续只作为 `visual_aid_only`，几何准确仍由 created handles 回读决定。
- `R-CAD-CONTRACT` baseline 已落地：新增 `core/verification/evidence_contract.py`，`cad_capability_probe` 与 `readback_report` 现输出 `evidence_state`、`geometry_accuracy`、`screenshot_role`；CAD validation runner 对缺失或错配证据字段做硬门禁。证据：`output\validation_runs\r-cad-contract-no-cad\report.json`、`output\validation_runs\r-cad-contract-cad\report.json`。
- `R-BLOCK-METADATA` baseline 已落地：`libraries/blocks/block_library.example.json` 升级为 `0.2`，含受控 `controlled-test-block-001`（`CODEX_TEST_BLOCK_001`）与 `symbol_fallback` 元数据；新增 `object_spec_to_block_reference()` 与 `validation.status` 过滤。证据：`234 tests OK`、`output\validation_runs\r-block-metadata-no-cad\report.json`、blank-shell benchmark pass。
- `R-BLOCK-PLAN` baseline 已落地：`insert_block_alpha` CAD_PLAN intent 已接入 `validate_plan`、`dry_run_report`、`execute_plan`（fake driver 记录 `insert_block_alpha` 调用）；示例 `examples/plans/insert_block_alpha_test.json`。证据：`239 tests OK`、`output\validation_runs\r-block-plan-no-cad\report.json`。
- `R-BLOCK-CAD-01` 已落地：`AutoCADComDriver.ensure_controlled_block_definition()` 可复用或创建 `CODEX_TEST_BLOCK_001` 块表定义，失败时输出 `definition_missing`。证据：`244 tests OK`（`tests.core.test_autocad_com_driver` 含 5 项受控块定义单测）。
- `R-BLOCK-CAD-02` 已落地：`AutoCADComDriver.insert_block_alpha()` COM 写入路径（`CODEX_PREVIEW`、统一 scale、结构化失败）。证据：`250 tests OK`。
- `R-BLOCK-CAD-03` 已落地：`block_reference` readback 标准化（`inspect_dwg.normalize_com_entity` + `geometry_checks.check_block_reference_readback`）。证据：`255 tests OK`。
- `R-BLOCK-CAD-04` 已落地：CAD validation runner 接入 block alpha no-CAD deferred 步骤与 CAD readback 步骤；`report.block_alpha.geometry_verified` 显式为 false（no-CAD）。证据：`259 tests OK`、`output\validation_runs\r-block-alpha-no-cad-test\report.json`。
- `R-BLOCK-CAD-05` 已落地：真实 AutoCAD 受控块 alpha 验收通过（`--block-alpha-only`）。证据：`output\validation_runs\r-block-alpha-cad\report.json`、`block_alpha_report.json`（`geometry_verified`）、`block_alpha_execution_summary.json`（`created_handles=["878"]`）、`block-alpha-window.png`。仅覆盖受控样本 `insert_block_alpha_test.json`，不扩大到任意块库或项目图纸。
- `R-OFFICE-MICRO-01` 已落地：office alpha 对象级扩展至 7 cases（电脑桌、储物柜柜前净空、文件柜）。证据：`259 tests OK`、`output\test_artifacts\benchmarks\office_object_r1/`（7/7 pass，`benchmark_pass_non_cad`）。
- `R-OFFICE-MICRO-02` 已落地：4 个 office micro-scene composition cases。证据：`output\test_artifacts\benchmarks\office_micro_r2/`（11/11 pass）。
- `R-OFFICE-MICRO-03` 已落地：3 个 blank-shell 场景 cases（长条主通道、障碍避让、会议/电脑混合区）。证据：`output\test_artifacts\benchmarks\office_scene_r1/`（14/14 pass）。
- `R-OFFICE-MICRO-04` 已落地：3 个 failure cases。证据：`output\test_artifacts\benchmarks\office_failure_r4/`（17/17 pass，3× `blocked_expected_non_cad`）。
- `R-OFFICE-MICRO-05` / 父包 `R-OFFICE-MICRO` 已收口：office alpha 17 cases + `benchmark_summary.json` 证据汇总；`docs/verification/office_alpha_benchmark_evidence.md`。
- `R4-01` 已落地：统一 evidence 词表与 `classify_benchmark_pipeline_evidence`。
- `R4-02` 已落地：failure 契约校验、`maximums`、静默 pass guard；office alpha 18 cases。
- `R4-03` 已落地：三组 benchmark `expected_evidence_summary` 机器断言。
- `R4-04` 已落地：CAD validation `evidence_summary` + 顶层 evidence gate。证据：`308 tests OK`、`output/validation_runs/r4-no-cad/`。
- `R4-05` / 父包 **`R4-EVIDENCE-GATES` 已收口**：`docs/verification/evidence_gate_handoff_rules.md`；交接模板扩展。
- `Y-MC-01` 已落地：blank-shell pipeline 输出 `candidate_sets.json`（多 circulation 分支 + zone/placement 候选）。
- `Y-MC-02` 已落地：`design_proposal.comparison_detail`（覆盖率、失败分布、通道连续性、ranking_reasons）。
- `Y-MC-03` 已落地：blank-shell benchmark 多候选硬断言。
- `Y-MC-04` 已落地：blank-shell core **8 cases**（6 pass + 2 blocked）。
- `Y-MC-05` / 父包 **`Y-MULTI-CANDIDATE` 已收口**。
- **父包 `BETA-PROPOSAL` 01–05 收口**：多方案对比 + 用户确认 + 受控 CAD_PLAN bundle。见 `docs/verification/beta_proposal_acceptance.md`。
- **后置 `BETA-DRAWING-READ-01`**：只读 DWG entity summary（层/类型/bbox/handle 统计）。见 `docs/verification/beta_drawing_read_01_boundaries.md`。证据：`404 tests OK`。
- **后置 `BETA-DRAWING-READ-02`**：墙/门洞/柱/禁放区几何候选启发式提取。见 `docs/verification/beta_drawing_read_02_boundaries.md`。证据：`407 tests OK`。
- **后置 `BETA-DRAWING-READ-03`**：shell 候选置信度 / 缺口 / 人工确认点报告。见 `docs/verification/beta_drawing_read_03_boundaries.md`。证据：`410 tests OK`。
- **后置 `BETA-DRAWING-READ-04`**：人工确认回写 `SHELL_MODEL`（shell_loader + schema pass）。见 `docs/verification/beta_drawing_read_04_boundaries.md`。证据：`414 tests OK`。
- **父包 `BETA-DRAWING-READ` 01–05 收口**（`BETA-DRAWING-READ-05`）：读图链路 benchmark + 结构化 blocker。见 `docs/verification/beta_drawing_read_acceptance.md`。证据：`416 tests OK`。
- **后置 `BETA-SCENE-01`**：office scene beta 偏好 + 统一 benchmark（9 cases，7 pass + 2 blocked）。见 `docs/verification/beta_scene_01_boundaries.md`。证据：`418 tests OK`。
- **后置 `BETA-SCENE-02`**：residential beta（卧室/餐厅/收纳 + blank-shell）。见 `docs/verification/beta_scene_02_boundaries.md`。证据：`420 tests OK`。
- **后置 `BETA-SCENE-03`**：restaurant/commercial beta（入口/堂食/后场 + blank-shell）。见 `docs/verification/beta_scene_03_boundaries.md`。下一后置：`BETA-SCENE-04`。证据：`422 tests OK`。
- **后置 `BETA-PROPOSAL-05`**：确认后 `confirmed_cad_plan_bundle`。见 `docs/verification/beta_proposal_05_boundaries.md`。
- **后置 `BETA-PROPOSAL-04`**：局部修改重算 CAD_PLAN。见 `docs/verification/beta_proposal_04_boundaries.md`。
- **后置 `BETA-PROPOSAL-03`**：用户确认 schema + apply。见 `docs/verification/beta_proposal_03_boundaries.md`。
- **后置 `BETA-PROPOSAL-02`**：`proposal_comparison_summary` benchmark。见 `docs/verification/beta_proposal_02_boundaries.md`。
- **后置 `BETA-PROPOSAL-01`**：候选 `score_breakdown` / `ranking_reasons` 固化。见 `docs/verification/beta_proposal_01_boundaries.md`。
- **父包 `BETA-PROJECT-SAMPLE` 01–05 收口**：脱敏样本协议 → workflow → benchmark → 可选 CAD readback。见 `docs/verification/beta_project_sample_acceptance.md`。
- **后置 `BETA-PROJECT-SAMPLE-05`**：样本 CAD check（`project_sample_cad_check_report.json`）。见 `docs/verification/beta_project_sample_05_boundaries.md`。
- **后置 `BETA-PROJECT-SAMPLE-04`**：样本 benchmark（pass + blocked）；`project_sample_benchmark.json`。见 `docs/verification/beta_project_sample_04_boundaries.md`。
- **后置 `BETA-PROJECT-SAMPLE-03`**：样本 workflow → CAD_PLAN / dry-run / unverified report。见 `docs/verification/beta_project_sample_03_boundaries.md`。
- **后置 `BETA-PROJECT-SAMPLE-02`**：样本 shell / project model fixture + loader。见 `docs/verification/beta_project_sample_02_boundaries.md`。
- **后置 `BETA-PROJECT-SAMPLE-01`**：脱敏样本目录协议 + manifest 扫描。见 `docs/verification/beta_project_sample_01_boundaries.md`。
- **父包 `BETA-CAD-BLOCK` 已收口（01–05）**：见 `docs/verification/beta_cad_block_acceptance.md`。
- **后置 `BETA-CAD-BLOCK-04`**：`drawing_standard_profile`（`codex_preview_beta`）。见 `docs/verification/beta_cad_block_04_boundaries.md`。
- **后置 `BETA-CAD-BLOCK-03`**：capability probe entity-level evidence（polyline / layer mapping / hatch deferred）。见 `docs/verification/beta_cad_block_03_boundaries.md`。
- **后置 `BETA-CAD-BLOCK-02`**：属性块 / tag readback 探针（deferred 与不误报）。见 `docs/verification/beta_cad_block_02_boundaries.md`。
- **后置 `BETA-CAD-BLOCK-01`**：受控 block transform beta suite（non-CAD）。
- **父包 `X-SCENE-ALPHA` 已收口（01–05）**：三场景 preferences + benchmark + 边界扫描 + 解释模板 + 总验收。见 `docs/verification/scene_alpha_acceptance.md`。可声称 non-CAD 多场景复用 Core pipeline；不可声称真实 CAD 几何或 Scene Agent 产品完成。
- `X-SCENE-04`：场景解释模板（`build_scene_explanation`、三场景 `rules.md`）。
- `X-SCENE-03`：Scene Agent 静态边界扫描（`scene_boundary_scan`）。
- `X-SCENE-02`：三场景 `scene_alpha_benchmark.json`（3/3 non-CAD pass）；动线权重进入 pipeline 选型。
- `X-SCENE-01`：Scene Alpha preferences 契约（对象优先、通道宽度、动线权重）。见 `docs/verification/scene_alpha_preferences_contract.md`。

## 当前可用链路

非 CAD blank-shell pipeline 当前可串联：

```text
SHELL_MODEL
-> PROJECT_MODEL
-> CIRCULATION_MODEL
-> FUNCTION_ZONE
-> placements
-> LAYOUT_PROPOSAL
-> DESIGN_PROPOSAL
-> CAD_PLAN
-> dry-run
-> VERIFICATION_REPORT(unverified)
```

当前已覆盖 retail、office、residential、restaurant 四个 benchmark workflow case。

## 最近验证记录

最近完整 CAD 底座复验快照：2026-05-26；2026-05-27/2026-05-28 的增量验证与审计见本页上方当前阶段条目。

```text
unittest discover -s tests: 452 tests OK
run_repo_audit.py --max-python-lines 500 --fail-on-findings: 0 findings
Python AST parse: 248 files checked, 0 errors
JSON parse: 166 files checked, 0 errors
focused 4-7 package tests: 46 tests OK
run_cad_validation.py --no-cad: output\validation_runs\codex-polish-final-no-cad status pass
self_check.py: pass
render_preview.py --check: ready（AutoCAD window 当前环境 unavailable；截图仍为 visual_aid_only）
run_project_sample_protocol_scan.py: pass, 2 samples
run_project_sample_benchmark.py: pass, 2/2 cases
run_proposal_confirmed_benchmark.py: pass, 2/2 cases
run_cad_beta_evidence_rollup.py: pass, 5/5 subpackages
run_office_scene_beta_benchmark.py --output-root: pass, 9/9 cases
run_residential_scene_beta_benchmark.py --output-root: pass, 8/8 cases
run_restaurant_scene_beta_benchmark.py --output-root: pass, 8/8 cases
run_benchmark_suite.py blank_shell_core_benchmark.json: output\test_artifacts\benchmarks\codex_polish_blank_shell 8/8 pass
run_benchmark_suite.py office_alpha_benchmark.json: output\test_artifacts\benchmarks\codex_polish_office_alpha 18/18 pass
run_benchmark_suite.py interior_delivery_benchmark.json: output\test_artifacts\benchmarks\codex_polish_interior_delivery 3/3 pass
focused 1-3 package tests: 48 tests OK
run_benchmark_suite.py blank_shell_core_benchmark.json: output\test_artifacts\benchmarks\codex_maintenance_fix_blank_shell 8/8 pass
run_benchmark_suite.py office_alpha_benchmark.json: output\test_artifacts\benchmarks\codex_maintenance_fix_office_alpha 18/18 pass
run_benchmark_suite.py interior_delivery_benchmark.json: output\test_artifacts\benchmarks\codex_maintenance_fix_interior_delivery 3/3 pass
run_project_sample_cad_check.py --no-cad --require-cad-verified: expected exit 1, report deferred at output\validation_runs\codex-maintenance-project-sample-strict-no-cad
run_cad_validation.py --no-cad: output\validation_runs\codex-maintenance-fix-no-cad status pass
run_cad_validation.py --no-cad: output\validation_runs\manual-no-cad-after-composition-cad status pass
run_cad_capability_probe.py: output\validation_runs\manual-primitive-cad-probe status cad_capability_verified
run_cad_validation.py: output\validation_runs\manual-cad-after-primitive-probe status pass
focused R-CAD-VIEW tests: tests.core.test_render_preview + tests.core.test_cad_validation_runner, 11 tests OK
run_cad_validation.py --no-cad: output\validation_runs\r-cad-view-no-cad status pass
run_cad_validation.py: output\validation_runs\r-cad-view-cad status pass
run_cad_validation.py --no-cad: output\validation_runs\r-cad-contract-no-cad status pass
run_cad_validation.py: output\validation_runs\r-cad-contract-cad status pass
run_composition_cad_check.py: output\validation_runs\interior-composition-cad-label-clean-y8000 status geometry_verified, 3/3 cases, 55 created handles
最新真实 CAD 报告: output\validation_runs\manual-cad-after-primitive-probe\report.json
最新窗口级截图 CAD 报告: output\validation_runs\r-cad-view-cad\report.json
最新角色组合真实 CAD 报告: output\validation_runs\interior-composition-cad-label-clean-y8000\composition_cad_check_report.json
readback_report.json: status geometry_verified
cad_capability_probe.json: status cad_capability_verified
baseline created_handles: 3C50, 3C51, 3C52, 3C53, 3C54, 3C55, 3C91
capability probe handles: 3CCD, 3CCE, 3CCF, 3CD0, 3CD1, 3CD2, 3CD3, 3CD4, 3CD5, 3CD6, 3D11
关键 checks: readback_scope / layer_entities / bbox_size / base_point / label_text / dimension_count / created_handles_scope 全部 pass
能力探针 checks: active_document_read / layer_policy / layer_ensure / rectangle_handles / line_handle / circle_handle / arc_handle / polyline_handle / text_handle / dimension_handles / handle_readback_count / readback_layer_scope / readback_type_counts / readback_bbox / safety_preview_only 全部 pass
截图证据: output\validation_runs\manual-primitive-cad-probe\cad-primitive-screen.png, 538584 bytes
窗口级截图证据: output\validation_runs\r-cad-view-cad\cad-validation-window.png, mode autocad_window, focus zoomed_to_bbox, 7 created handles
角色组合视觉辅助截图: output\test_artifacts\benchmarks\interior_delivery_manual\interior_designer_bedroom_bed_rug\preview-browser.png; output\test_artifacts\benchmarks\interior_delivery_manual\home_designer_dining_table_set\preview-browser.png; output\test_artifacts\benchmarks\interior_delivery_manual\office_planner_desk_combo\preview-browser.png
角色组合真实 CAD 截图: output\validation_runs\interior-composition-cad-label-clean-y8000\composition-cad-screen-clean-y8000.png
```

W-07 真实 CAD 总验证入口已经完成 baseline 落图、截图和实体回读闭环，并额外完成 CAD COM 能力矩阵探针。因此可以声明 Phase W baseline 真实 CAD 几何通过、当前用户会话下 CAD COM preview 写入与 handle 回读底座可用；扩展后的底层图元探针也已验证 1 个矩形边框、1 条独立直线、1 个圆、1 段弧、1 条闭合多段线、1 段文字和 2 个标注。该结论仍只覆盖 `examples\plans\draw_test_cabinet.json` 和当前能力探针，不能扩大为真实项目图纸、块库、块插入或任意 CAD_PLAN 全部已验证。后续判断必须继续以 `readback_report.json.status=geometry_verified`、`cad_capability_probe.json.status=cad_capability_verified` 和关键 checks 全部 `pass` 为准，不得只看 runner 顶层 `status=pass`。

## 当前进度估算

与 [`CORE_STATUS.md`](../../CORE_STATUS.md)「四进度口径」及 [`docs/verification/capability_proof_status_template.md`](../verification/capability_proof_status_template.md) **同步**（2026-05-27）。本节保留完整 A/B/C 状态快照；聊天交付默认用 `AGENTS.md` 的 **1 张精简进度表**，状态汇报、交接、审计、进度盘点或表 C 专题时再展开完整表格。

**表 A — 工程节奏**

| 指标 | 当前粗估 |
| --- | --- |
| 总进度 | 约 **95%**（96%×70% + 93%×30%） |
| Core 底座开发进度 | 约 **96%**（**≠** CAD 证明覆盖率） |
| Agent 多场景实现进度 | 约 **93%** |

**表 B — 任务清单三指令执行进度**

| 指令 | 板块 | 执行进度 |
| --- | --- | --- |
| 能力证明 | §3 `V-PROOF` | 约 **78%**（35/45 done；另有 1 partial；后续项见 `docs/planning/任务清单.md` §0） |
| 一键推进（代码轨） | §4 | 约 **89%**（约 49/55；**不等于 CAD 几何证明**） |
| **RCAD 烟囱包** | §5 `RCAD` | **100%**（**29/29** verified；**≠ 画图实力**） |

**表 C — 真实 CAD 实力**（`output/validation_runs/capability-lab/cad_capability_coverage.json`）

| 指标 | 当前值 |
| --- | --- |
| **真实 CAD 实力（主指标）** | **8.87%**（showcase 门仍为主瓶颈；最高已证 L4） |
| CAD 证明覆盖率 | **48.58%**（137/282；112 verified + 25 showcase） |
| CAD 实力指数（加权） | **51.03%** |
| 场景片段（L3+） | **40.91%**（36/88） |
| 展示就绪度 | **8.87%**（25/282） |
| 最高已证 Ladder | **L4** |

当前机器报告：`output/validation_runs/capability-lab/cad_capability_coverage.json`。可读分组历史入口：`output/validation_runs/neg-cad-proof-sync/capability-readability-final/capability_readability_report.json`。

**禁止混用**：不得只报「Core 96%」或「RCAD 烟囱 97%」而不报 **表 C**；不得用 RCAD / `negative_guard_verified` / non-CAD rollup 代替 registry 几何 `verified` 或声称全库 `geometry_verified`。

## 当前最重要缺口

| 缺口 | 影响 | 归属主线 |
| --- | --- | --- |
| 真实项目 DWG / 公司块库 / 正式图层尚未全量补验 | 当前证据不能扩大为任意项目几何准确 | 后续真实项目验收 |
| ActiveDocument guard 仍未落硬门禁 | 合法 preview plan 仍会写入当前激活 DWG 的 `CODEX_PREVIEW` 图层，需防误保存污染 | CAD 安全加固 |
| scene beta 多数仍是 non-CAD benchmark | office / residential / restaurant 通过不等于真实 CAD 落图 verified | Scene Beta / CAD 扩展 |
| 自动读图候选仍依赖人工确认 | 读图链路能产出候选和 blocker，但不能替代人工确认 `SHELL_MODEL` | Drawing Read |
| 截图能力仍是视觉辅助 | `render_preview.py --check` ready 不代表几何准确，准确性仍需 created-handle readback | Phase W / CAD 验证 |

## 计划入口

后续优先级、Phase 顺序、待办和退出标准只以唯一 `PlanMD`：`CORE_RESTRUCTURE_PLAN.md` 为准。本文只维护当前进展、最近验证、风险边界和状态快照。

2026-05-26 的九个 Phase R/X/Y 相关开发包与 25 个二级小包已经按历史记录和交接包收口，其中 `R-CAD-VIEW-CAPTURE` 的真实 CAD 证据为 `output\validation_runs\r-cad-view-cad\cad-validation-window.png`。这些记录现在只是历史快照；后续执行顺序、后置 Backlog 和新的维护包边界只在唯一 `PlanMD` 中维护。

同日登记的五大后置主线 Backlog（真实 CAD 能力扩展、真实项目样本闭环、多方案设计与交互确认、自动读图 / 空壳识别、场景 Agent Beta）仍只作为 PlanMD 中的未来路线，不在本文复制小包表，也不提升本页进度百分比。

## 后续恢复开发时怎么问

```text
读取本仓库 AGENTS.md 和 CORE_CONTEXT_BRIEF.md，告诉我 CAD Agent 当前开发状态和下一步建议。
```

若要执行主计划：

```text
读取 CORE_RESTRUCTURE_PLAN.md。若执行当前已登记开发包，再按目标阶段打开 docs/planning/phases/*.md；若查看后置 Backlog，只看 CORE_RESTRUCTURE_PLAN.md。
```
