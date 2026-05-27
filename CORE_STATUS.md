# Core Status

最后更新：2026-05-27

本文是通用 CAD Agent Core Lab 的能力状态页。它只回答“当前能力成熟到哪里、证据是什么、缺口是什么”，不承载长历史和独立计划；历史变更看 `docs/status/changelog.md`，当前快照看 `docs/status/current.md`，唯一 `PlanMD` / 主计划看 `CORE_RESTRUCTURE_PLAN.md`。

## 状态口径

| 状态 | 含义 |
| --- | --- |
| `alpha_ready_non_cad` | 非 CAD 链路已有稳定入口、测试和基线证据，可作为 Alpha 原型使用 |
| `alpha_verified_cad` | 已对有限 baseline CAD_PLAN 完成真实 AutoCAD 落图、截图、实体回读和 `geometry_verified` 闭环 |
| `prototype` | 已有最小实现或脚本原型，但接口、样本或验证仍需增强 |
| `blocked_by_cad` | 仓库内入口已存在，但完成声明依赖真实 CAD 落图、截图辅助或实体回读；几何准确声明以实体回读为准 |
| `scaffold` | 目录、文档或数据壳已建立，核心能力尚未形成 |
| `not_started` | 仅在计划中定义，尚未开始 |
| `blocked` | 缺依赖、缺证据或有已知失败，不能继续声称可用 |

## 四进度口径（固定模板，V-PROOF-04 + 表 C）

以下四块 **禁止混用**。状态页保留完整 A/B/C 快照；聊天最终回复默认按 `AGENTS.md` 精简为 1 张轻量表，只有状态汇报、交接、审计、进度盘点或表 C 专题时展开完整表格。字段定义与禁止声称全文见 [`docs/verification/capability_proof_status_template.md`](docs/verification/capability_proof_status_template.md)；能力证明架构见 [`docs/planning/capability-proof-architecture.md`](docs/planning/capability-proof-architecture.md)。

```text
cad_capability_registry: 282 rows → cad_proof_coverage_percent=48.58%（137/282；112 verified + 25 showcase）
cad_strength: index=51.03%, L3+=40.91%, showcase=8.87% → `cad_strength_headline_percent=8.87`（min 门；`showcase_count=25`；最高已证 L4）
RCAD 烟囱: 29/29 verified；≠ 真实 CAD 实力
复跑: scripts/run_capability_coverage.py --output output/validation_runs/capability-lab/cad_capability_coverage.json
```

### 表 A — 工程完备度（工程节奏）

| 指标 | 当前值（2026-05-27） | 说明 |
| --- | --- | --- |
| 总进度 | 约 **95%** | Core×70% + Agent×30% |
| Core 底座开发进度 | 约 **96%** | schema、runner、unittest、non-CAD benchmark；**≠ CAD 几何已全面证明** |
| Agent 多场景实现进度 | 约 **93%** | Scene Alpha/Beta + 工装三样本 boundary/rollup 口径已同步；office/restaurant P3、多场景父包与 scene beta 解释模板已收口 |

### 表 B — 任务清单三指令执行进度

| 指令 | 板块 | 当前值（2026-05-27） |
| --- | --- | --- |
| 能力证明 | §3 `V-PROOF` | 约 **78%**（35/45 done；另有 1 partial；后续项见 `docs/planning/任务清单.md` §0） |
| 一键推进 | §4 代码轨 | 约 **89%**（约 49/55；后续项见 `CORE_RESTRUCTURE_PLAN.md`） |
| **RCAD 烟囱包** | §5 `RCAD` | **100%**（**29/29** `verified`；§5 暂无 pending） |

### 表 C — 真实 CAD 实力（登记表 + Ladder 加权；**≠ RCAD 烟囱**）

| 指标 | 当前值（2026-05-27） |
| --- | --- |
| **真实 CAD 实力（主指标）** | **8.87%**（`showcase_count=25`；最高已证 **L4**） |
| CAD 证明覆盖率 | **48.58%**（137/282；112 verified + 25 showcase） |
| CAD 实力指数（Ladder 加权） | **51.03%** |
| 场景片段实力（L3+ verified） | **40.91%**（36/88） |
| 展示就绪度（showcase） | **8.87%** |
| 最高已证 Ladder | **L4** |

机器报告：`output/validation_runs/capability-lab/cad_capability_coverage.json`（2026-05-27T15:21:55Z 复跑）。若 Markdown 与该 JSON 冲突，以 JSON 为准。**禁止**用「Core 约 96%」或「RCAD 烟囱 100%」代替表 C。

### 展示等级 Ladder（定性）

| 指标 | 当前值 |
| --- | --- |
| 当前最高已证 Ladder | **L4** |
| 项目切片证据 | **L4**（双工装项目切片 showcase；仍非 L5 交付预备） |
| L5 交付预备 | **未开始** |

## 当前总状态

### 2026-05-27 VCAD-01：CAD 视觉表达 P0

- **画面能力**：新增 `visual_cad_smoke`，从“矩形 smoke”推进到可读办公角落：双线房间、门扇开启弧、两组工位、显示器/键盘、椅子、抽屉柜与工作区轮廓。
- **真实 CAD 证据**：`output/validation_runs/vcad-01-visual-office-corner-20260527-cad/visual_cad_smoke_report.json` 为 `visual_geometry_verified`，54 created handles 全部回读，类型计数 `line=42`、`circle=6`、`arc=3`、`polyline=3`，只写 `CODEX_PREVIEW`，未保存 DWG、未删除实体、未改正式图层。
- **边界**：本包是 CAD 画面观感 P0 升级，不改变表 C 数值；截图 `output/previews/vcad-01-visual-office-corner.png` 是视觉证据，不替代施工图能力或 registry 机器值。

### 2026-05-27 V-PROOF-42：Composition Expand 真实 CAD 刷新

- **真实 CAD 证据**：`output/validation_runs/vproof-42-office-composition-expand-20260527-cad/composition_cad_registry_report.json` 顶层 `status=geometry_verified`，4 个 office composition case 全部通过，created handles 共 40；只写 `CODEX_PREVIEW`，未保存 DWG、未删除实体、未改正式图层。
- **Registry / 表 C**：`composition.single_desk_chair_pair`、`composition.desk_with_back_cabinet`、`composition.two_workstations_shared_aisle`、`composition.entry_reception_clearance` 已回写到本轮 fresh verification reports；这些行此前已是 `verified`，所以 coverage 复跑后 `verified_count=112`、`showcase_count=25`、`cad_proof_count=137`、CAD 证明覆盖率 **48.58%**、CAD 实力指数 **51.03%**、主指标仍 **8.87%**（showcase 门）。
- **台账**：能力证明从 34/45 推进到 **35/45 done**，另有 1 partial；当前后续项见 `docs/planning/任务清单.md` §0。

### 2026-05-27 V-PROOF-66：Primitive Probe Showcase

- **Showcase 推进**：新增 `docs/verification/capability_showcase/showcase/L1/primitive_probe_matrix/gallery_index.json`，并把 `primitive.arc/circle/dimension/line/polyline/rectangle/text` 与 `drawing_standard.beta.drawing_standard_beta_04` 补入 showcase。
- **Registry 回写**：8 行均使用既有真实 CAD 报告从 `verified` 升级为 `showcase`；primitive probe 证据来自 `RCAD-22`，drawing-standard suite 证据来自 `RCAD-23`。
- **表 C**：coverage 复跑后 `showcase_count=25`，真实 CAD 实力主指标升至 **8.87%**；CAD 证明覆盖率仍 **48.23%**，CAD 实力指数 **50.82%**，最高 L4。

### 2026-05-27 V-PROOF-65：Showcase Second Wave

- **Showcase 推进**：新增 hatch、block-first、drawing-standard block insert 三组 showcase 条目，覆盖 `primitive.hatch`、`symbol.block_first.symbol_block_first_tier_01`、`symbol.block_first.controlled_block_wins`、`drawing_standard.beta.block_insert_plan_resolution`。
- **Registry 回写**：4 行均使用既有真实 CAD readback 报告从 `verified` 升级为 `showcase`；证据分别来自 `RCAD-06`、`RCAD-25`、`RCAD-23`。
- **表 C**：coverage 复跑后 `showcase_count=17`，真实 CAD 实力主指标升至 **6.03%**；CAD 证明覆盖率仍 **48.23%**，CAD 实力指数 **50.82%**，最高 L4。

### 2026-05-27 V-PROOF-64：Ladder Boundary + Block Matrix Showcase

- **Showcase 推进**：新增 `docs/verification/capability_ladder_boundaries.md`，并为 `block.insert_block_alpha.matrix` 增加 L2 showcase 入口 `docs/verification/capability_showcase/showcase/L2/block_insert_matrix/gallery_index.json`。
- **Registry 回写**：`block.insert_block_alpha.matrix` 使用 `RCAD-24` 的 8/8 real CAD block_reference readback suite summary 从 `verified` 升级为 `showcase`。
- **表 C**：coverage 复跑后 `showcase_count=13`，真实 CAD 实力主指标升至 **4.61%**；CAD 证明覆盖率仍 **48.23%**，CAD 实力指数 **50.82%**，最高 L4。

### 2026-05-27 V-PROOF-45：Block Beta Rows 回写表 C

- **Registry 回写**：`block.insert_block_alpha.matrix` 使用 `RCAD-24` 的 `block_alpha_beta_summary.json`（8/8 real CAD block_reference readback）由 `smoke` 升级为 `verified`。
- **证据**：`output/validation_runs/vproof-45-block-beta-rows/writeback_apply.json` 顶层 `status=pass`、`applied_count=1`；coverage 复跑后 `verified_count=124`、`cad_proof_count=136`。
- **表 C**：CAD 证明覆盖率升至 **48.23%**，CAD 实力指数升至 **50.82%**；主指标仍为 **4.26%**，因为 showcase 就绪度仍是 min 门。

### 2026-05-27 V-PROOF-41：双受控块 CAD matrix

- **代码链路**：`insert_block_alpha` 的安全 allowlist 从单一 `controlled-test-block-001` 扩为 `controlled-test-block-001/002` 两个受控测试块，仍限定 `CODEX_PREVIEW`、统一缩放、无属性写入。
- **真实 CAD 证据**：`output/validation_runs/vproof-41-block-cad-matrix-20260527-cad/block_alpha_beta_summary.json` 为 2/2 `geometry_verified`，created handles `61F` / `627` 均回读为 `block_reference`，只写 `CODEX_PREVIEW`，未保存 DWG、未删除实体、未改正式图层。
- **Registry / 表 C**：`block.library.controlled_test_block_002` 由 `smoke` 回写为 `verified`，证据为 `vproof_41_block_002_offset/block_alpha_report.json`；coverage 复跑后 `verified_count=112`、`cad_proof_count=137`、CAD 证明覆盖率 **48.58%**、CAD 实力指数 **51.03%**，主指标仍为 **8.87%**（showcase 门）。

### 2026-05-27 SCENE-PROD-06：多场景回归门禁

- **V-PROOF-40**：Block Matrix Plan 能力证明已收口，`output/validation_runs/vproof-40-block-matrix-plan-no-cad/block_matrix_registry_sync_summary.json` 显示 `matrix_status=pass`、5 个 binding applied。`block.insert_block_alpha.matrix` 仅更新为 `dry_run_valid_plan_only` smoke evidence；`anchor/rotation/scale/attributes` 4 个维度行保持既有 `readback_geometry_verified`，只追加矩阵 manifest 绑定，不把 no-CAD smoke 计作新几何证明。coverage 复跑后表 C 数值不变。
- **SCENE-PROD-06**：多场景回归门禁已完成，`output/validation_runs/scene-prod-06-regression-gate-no-cad/scene_regression_gate_summary.json` 顶层 `status=pass`，office / residential / restaurant selected scene beta benchmark 合计 25/25 pass，21 个 `benchmark_pass_non_cad`、4 个 `blocked_expected_non_cad`、`readback_geometry_verified_count=0`；repo audit 0 findings。本包只推进代码轨 no-CAD 回归门禁，不新增真实 CAD 几何证明。

### 2026-05-27 RCAD-06：Hatch COM 受控 smoke 真实 CAD 补验

- **RCAD-06 + V-PROOF-53**：`AutoCADComDriver.draw_hatch()` 已从历史 structured deferred 推进到受控真实 COM smoke；在 `CODEX_PREVIEW` 创建闭合 boundary polyline + ANSI31 hatch，证据为 `output/validation_runs/rcad-06-hatch-cad-20260527-escalated/hatch_cad_smoke_report.json`，`status=geometry_verified`、`evidence_state=readback_geometry_verified`、created handles `61C` / `61D`，回读类型 `hatch=1`、`polyline=1`，bbox `100 x 80`。未保存 DWG、未删除实体、未修改正式图层。
- **Registry 回写**：`primitive.hatch` 已由 `deferred` 升级为 `verified`，回写证据为 `output/validation_runs/rcad-06-hatch-cad-20260527-escalated/hatch_writeback.json`；fake driver / no-CAD 路径仍保留 structured deferred，不计几何通过。
- **表 C 机器值**：复跑 `output/validation_runs/capability-lab/cad_capability_coverage.json` 后，`total_count=282`、`verified_count=123`、`showcase_count=12`、CAD 证明覆盖率 **47.87%**、CAD 实力指数 **50.75%**、真实 CAD 实力主指标 **4.26%**、最高已证 **L4**。RCAD 烟囱更新为 **29/29 verified**，但仍不等于任意 hatch、任意 CAD_PLAN 或施工图已证明。

### 2026-05-27 NEG-CAD-PROOF-SYNC：负向安全 runner + 覆盖率可读报告 + composition 收口

- **V-PROOF-35**：fallback tier rows 已登记到 `cad_capability_registry`，新增 `symbol.fallback_tier.block/symbol_glyph/component_preview/bbox_placeholder/deferred_unsupported_symbol` 5 行；4 行 `smoke`、1 行 `deferred`，全部明确 `not_verified_without_cad_readback`，不新增真实 CAD `geometry_verified`。
- **RCAD-28**：BETA-CAD-BLOCK evidence rollup 已补齐 trend hook 并复跑通过，证据为 `output/validation_runs/rcad-28-beta-evidence-rollup-20260527-final/cad_beta_evidence_rollup.json` 与 `evidence_trend/cad_beta_evidence_rollup_trend.json`；5/5 subpackages pass，`non_cad_only=true`、`geometry_verified_count=0`、`dry_run_valid_plan_only_count=5`。本轮只推进 RCAD 台账和 trend 可读性，不新增真实 CAD 几何证明、不回写 registry。
- **RCAD-27**：local CAD regression strict 已在用户 AutoCAD 会话完成真实 CAD 补验，证据为 `output/validation_runs/rcad-27-trend-rollup-cad-20260527-escalated/local_cad_regression_report.json`；顶层 `status=pass`、9/9 `geometry_verified_case_count`、105 created handles，并输出 `evidence_trend/local_cad_regression_trend.json`。未保存 DWG、未删除实体、未修改正式图层；本轮只推进 RCAD 台账，不回写 registry。
- **RCAD-24**：block alpha beta suite 已在用户 AutoCAD 会话完成真实 CAD 补验，证据为 `output/validation_runs/rcad-24-block-beta-cad-after-rotfix-20260527/block_alpha_beta_summary.json`；8/8 case `geometry_verified`，created handles `373`~`37A`，全部写入 `CODEX_PREVIEW` 并回读为 `block_reference`。本轮同步修正 block insert 旋转 bbox 预期为 AutoCAD 实际旋转外包框；未保存 DWG、未删除实体、未修改正式图层。
- **表 C 机器值**：当前最新复跑见上方 `V-PROOF-41` 条目与 `output/validation_runs/capability-lab/cad_capability_coverage.json`；`total_count=282`、`verified_count=112`、`showcase_count=25`、CAD 证明覆盖率 **48.58%**、CAD 实力指数 **51.03%**、真实 CAD 实力主指标 **8.87%**、最高已证 **L4**。
- **REST-PROD-01**：restaurant alpha 边界已按 `OFFICE-PROD-01` 模式收口；产物为 `restaurant_alpha_boundary.py`、`restaurant_prod_alpha_manifest.json`、`restaurant_prod_01_restaurant_alpha_boundary.md`、CLI 和 focused test。证据为 `output/validation_runs/rest-prod-01-boundary-no-cad/restaurant_alpha_boundary_summary.json`，只证明 no-CAD contract / benchmark case 可复跑，不新增真实 CAD `geometry_verified`。
- **SCENE-PROD-05**：scene beta 解释模板已收口；产物为 `scene_beta_explanation.py`、`scene_prod_05_scene_explanation_template.md`、CLI 和 focused test。证据为 `output/validation_runs/scene-prod-05-explanation-template-no-cad/scene_beta_explanation_summary.json`，三场景 preferences → Core / benchmark 的解释对象可机器读取，不新增真实 CAD `geometry_verified`。
- **REST-PROD-04**：P3 多场景父包已收口；产物为 `multi_scene_p3_wave.py`、`rest_prod_04_multi_scene_p3_rollup_acceptance.md`、CLI 和 focused test。证据为 `output/validation_runs/rest-prod-04-multi-scene-p3-rollup-no-cad/multi_scene_p3_wave_summary.json`，office + restaurant P3 父包统一可审计，不新增真实 CAD `geometry_verified`。
- **REST-PROD-03**：restaurant P3 波次已按 `OFFICE-PROD-03` 模式收口；产物为 `restaurant_p3_wave.py`、`restaurant_prod_03_p3_wave_acceptance.md`、CLI 和 focused test。证据为 `output/validation_runs/rest-prod-03-p3-rollup-no-cad/restaurant_p3_wave_summary.json`，alpha case + beta 8/8 no-CAD pass，不新增真实 CAD `geometry_verified`。
- **REST-PROD-02**：restaurant beta 边界已按 `OFFICE-PROD-02` 模式收口；产物为 `restaurant_beta_boundary.py`、`restaurant_prod_beta_manifest.json`、`restaurant_prod_02_restaurant_beta_boundary.md`、CLI 和 focused test。证据为 `output/validation_runs/rest-prod-02-boundary-no-cad/restaurant_beta_boundary_summary.json`，8/8 no-CAD benchmark pass（7 pass + 1 blocked_expected），不新增真实 CAD `geometry_verified`。
- **V-PROOF-34 + RCAD-25**：block-first tier 已完成真实 CAD 补验，证据为 `output/validation_runs/rcad-25-symbol-block-first-20260527-escalated/symbol_block_first_cad_smoke_report.json`；`controlled-block-wins` 选择 `block` / `insert_block_alpha`，在用户 AutoCAD 会话 `CODEX_PREVIEW` 插入 `CODEX_TEST_BLOCK_001`，created handle `369` 回读为 `block_reference`，`status=geometry_verified`。仅 `symbol.block_first.symbol_block_first_tier_01` 与 `symbol.block_first.controlled_block_wins` 回写 `verified`；两个 glyph fallback case 保持 smoke，不扩大声称。
- **V-PROOF-44 + RCAD-23**：drawing standard beta 已完成真实 CAD 子集补验，证据为 `output/validation_runs/rcad-23-drawing-standard-beta-20260527-escalated/drawing_standard_cad_smoke_report.json`；`block_insert_plan_resolution` 生成 styled `insert_block_alpha`，在 `CODEX_PREVIEW` 创建 handle `36A` 并回读为 `block_reference`，`status=geometry_verified`。仅 suite 行与 block insert case 行回写 `verified`；object role、primitive style、semantic layer case 仍保持 smoke。
- **RCAD-20**：真实 CAD 负向安全补验已在沙箱外用户 CAD 会话通过，证据为 `output/validation_runs/rcad-20-negative-cad-20260527-escalated/negative_cad_runner_report.json`；`status=pass`、`evidence_state=negative_guard_verified`、`created_handles=[]`、不保存、不删除、不改正式图层、entity delta=0。guard-only 不计入几何证明；`V-PROOF-33` 扩表后的覆盖率仅为当时快照，当前表 C 以本页顶部机器复跑为准。
- **CFIT-10**：第三组工装脱敏样本 `commercial_fitout_reception_sample` 已落地；三子场景（开放办公 / 会议室 / 前台）各有一组脱敏样本 + rollup 登记；fake rollup 4/4 geometry_verified（单测）。`RCAD-19` 仍待真实 CAD。
- **CFIT-09**：第二组工装脱敏样本 `commercial_fitout_meeting_sample` 已落地并登记 `project_sample_cad_rollup`；`fitout_sample_specs.py` 统一 open-office / meeting-room 样本与 workflow 路径；fake rollup 3/3 `geometry_verified`（单测）。本包未运行真实 AutoCAD 会话补验；`RCAD-10` 仍待用户 CAD。
- **LCAD-14**：新增 `run_guard_full_cad_runner.py`，strict rollup 汇总 write guard、negative CAD、capability probe 三段子报告；`strict_gate` 要求 `session_guard.status=consistent` 与 `validate_capability_probe_evidence()` 通过。证据为 `output/validation_runs/lcad-14-guard-full-no-cad/guard_full_cad_report.json`。本包未运行真实 CAD；真实会话 strict 复验入口为 `RCAD-21`（`--real-cad`）。§4.1 代码轨活跃队列已收口。
- **LCAD-13**：`run_cad_capability_probe()` 已接入 ActiveDocument before/after snapshot：`session_guard` 写入探针 JSON 与 `active_document_snapshot.json`，`cad_capability_verified` 时要求 `session_guard.status=consistent` 与 `active_document_identity_stable=pass`。新增 `docs/verification/session_snapshot_capability_probe_boundary.md`，服务 `V-PROOF-52`；no-CAD 证据为 `output/validation_runs/lcad-13-session-snapshot-no-cad/`。本包未运行真实 CAD，不新增 `geometry_verified`。下一代码轨为 `LCAD-14`。
- **LCAD-12 / RCAD-06**：`LCAD-12` 历史收口曾把 `draw_hatch` 固定为 preview-only 守卫 + structured deferred；当前 `RCAD-06` 已补齐 real COM 受控 ANSI31 hatch smoke 并完成 created-handle 回读。`FakeCadDriver.draw_hatch()` 与 no-CAD 路径仍返回 `primitive=hatch`、`status=deferred`、`failure_category=hatch_unverified`、`created_handles=[]`、`geometry_verified=false`；真实 CAD 证据仅限 `RCAD-06` 的受控 smoke。
- **CAD-VAL-02**：`run_cad_validation` 新增 `environment_optional` / `--environment-optional`，让环境、截图、`unit_tests` 等基础设施失败保留在 `infrastructure_gate` 和 `infrastructure_debt`，但不把非几何失败混成 `geometry_gate` 失败；新增 `docs/verification/cad_validation_environment_gate.md`。证据为 `output/validation_runs/cad-val-02-environment-optional/report.json`，`status=pass`、`legacy_status=fail`、`geometry_gate.status=pass`、`infrastructure_gate.failed_required_step_ids=[unit_tests]`。后续 `LCAD-12` 已收口为 hatch deferred 边界，`RCAD-06` 已补上受控真实 hatch smoke。
- **LCAD-11.5**：新增 `docs/verification/evidence_trend_boundaries.md` 与 `tests/core/test_evidence_trend_boundaries_doc.py`，把 LCAD-11.1~11.4 的 trend JSON、coverage `snapshot.metrics`、`V-PROOF-71` 用途和不得声称边界写成可审计文档；明确 trend JSON、schema pass、no-CAD pass、coverage metric 都不能替代真实 AutoCAD created-handle readback。
- **LCAD-11.4**：`run_capability_coverage` 现在同步输出 `evidence_trend/capability_coverage_trend.json`，把 V-PROOF-02 coverage 字段放入统一 trend schema 的 `snapshot.metrics`；证据为 `output/validation_runs/lcad-11-4-coverage-trend-hook/evidence_trend/capability_coverage_trend.json`，schema 校验无错误。本包只接 trend hook，不新增真实 CAD `geometry_verified`。
- **LCAD-11.3**：`run_cad_validation` 现在同步输出 `evidence_trend/cad_validation_trend_index.json`，索引同级 validation run 的历史 `report.json`；no-CAD 复跑证据为 `output/validation_runs/lcad-11-3-validation-trend-index/evidence_trend/cad_validation_trend_index.json`，schema 校验无错误，当前 `snapshot_count=11`。索引吸收历史真实 CAD geometry snapshots，但本轮只跑 no-CAD，不新增真实 CAD `geometry_verified`。
- **LCAD-11.2**：`run_local_cad_regression` 现在同步输出 `evidence_trend/local_cad_regression_trend.json`；no-CAD 复跑证据为 `output/validation_runs/lcad-11-2-regression-trend-json/evidence_trend/local_cad_regression_trend.json`，schema 校验无错误，`snapshot_count=1`、`deferred_cad_readback_count=8`、`geometry_verified_count=0`、`non_cad_only=true`。本包只输出趋势 rollup，不新增真实 CAD `geometry_verified`。
- **LCAD-11.1**：新增 `core/verification/evidence_trend.py`、`core/schemas/evidence_trend.schema.json`、`examples/evidence_trends/minimal_evidence_trend.json` 与 `tests/core/test_evidence_trend.py`，把 evidence trend JSON 字段与统一 evidence 词表对齐；`negative_guard_verified` 在趋势汇总中只计入 `guard_only_count`，不计入 `cad_proof_state_count` 或 `geometry_verified_count`。
- **LCAD-10.5**：新增 `docs/verification/negative_cad_safety_acceptance.md` 与 `tests/core/test_lcad_10_parent_rollup.py`，父包 `LCAD-10-NEGATIVE-SAFETY` 收口；下一代码轨为 `LCAD-11.1`。
- **LCAD-10.4**：新增 `docs/verification/negative_cad_safety_boundaries.md`，把 LCAD-10.1~10.4 的负向 fixture、write guard、runner、`RCAD-20` 补验边界和“不得声称”口径写成可审计文档。
- **LCAD-10.3**：新增 `core/verification/negative_cad_runner.py` 与 `scripts/run_negative_cad_runner.py`，负向 CAD runner 汇总 8 个 negative CAD_PLAN、write guard、ActiveDocument snapshot 和 no-handle/no-save/no-delete/no-formal-layer 证据。
- **真实 COM 前置守卫补强**：`AutoCADComDriver` 的 line / rectangle / circle / arc / polyline / text / dimension 写入现在在任何 COM `Add*` 前先检查 preview layer，避免“拒绝后已创建实体”的安全漂移。
- **覆盖率可读证据**：新增 `core/verification/capability_readability.py` 与 `scripts/run_capability_readability_report.py`，把 `verified_geometry`、`guard_only`、`deferred`、`smoke_only`、`none`、`blocked` 分组输出；证据为 `output/validation_runs/neg-cad-proof-sync/capability-readability-final/capability_readability_report.json`。
- **composition 收口**：保留 JSON catalog + schema 方向；`drawing_policy.py` 改为全局默认无标注，运行时对象级 `include_label/include_dimensions` 不再能覆盖 composition 输出。
- 证据：focused **35 tests OK**；`negative-runner-fake-final` 为 `status=pass`、`created_handles=[]`；`RCAD-20` 真实 CAD 负向补验为 `status=pass`、`negative_guard_verified`、`created_handles=[]`。不新增真实 CAD `geometry_verified`。

### 2026-05-27 V-PROOF-04/05：三口径状态页 + handoff 模板

- **V-PROOF-04**：本节固定表 A / 表 B / CAD 证明覆盖率 / Ladder；与 `capability_proof_status_template.md` 对齐。
- **V-PROOF-05**：`docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` 增加能力证明包附加项（`capability_id`、`claim_level`、`ladder_level`、覆盖率复跑）。
- 全量回归：**629 tests OK**。本轮未运行真实 AutoCAD，不新增 `geometry_verified` 结论。

### 2026-05-26 Codex 本地 CAD 回归矩阵加固

```text
456 tests OK
local CAD regression no-CAD pass: output\validation_runs\local-cad-regression-no-cad
local CAD regression summary: step_count=3, deferred_case_count=2, geometry_verified_case_count=0
```

本轮新增 `core/verification/local_cad_regression.py` 与 `scripts/run_local_cad_regression.py`，把 baseline CAD validation、project sample CAD check 和 interior composition CAD check 收拢为本地 CAD 回归矩阵。默认 `--no-cad` 模式不连接 AutoCAD，只输出可机器读取的 deferred / non-CAD 证据；真实 CAD 严格模式可加 `--require-cad-verified`，任一子项不是 `geometry_verified` 就会失败。composition CAD check 现在受前置 benchmark artifact 门禁保护，benchmark 未通过时不会继续写入 CAD。本轮未运行真实 AutoCAD，不新增 `geometry_verified` 结论。

### 2026-05-26 Codex 进入下一阶段前雕琢

```text
452 tests OK
repo audit 0 findings
run_cad_validation.py --no-cad pass: output\validation_runs\codex-polish-final-no-cad
blank-shell benchmark 8/8 pass (non-CAD)
office alpha benchmark 18/18 pass (non-CAD)
interior delivery benchmark 3/3 pass (non-CAD)
project sample benchmark 2/2 pass (non-CAD)
proposal confirmed benchmark 2/2 pass (non-CAD)
CAD beta evidence rollup 5/5 pass (non-CAD rollup)
office/residential/restaurant scene beta benchmark 25/25 pass (non-CAD)
```

本轮是进入下一开发阶段前的维护雕琢，不新增真实 CAD 能力结论。已修复活跃排障手册硬编码固定 Windows 用户目录的 CAD-MCP Python 路径问题，改为 `$env:USERPROFILE` 派生；scene beta 三个 CLI wrapper 保留 `--output`，同时兼容通用 benchmark 习惯的 `--output-root`。新增回归测试锁定这两类可迁移性 / 易用性边界。本轮未运行真实 CAD，不新增 `geometry_verified` 结论。

### 2026-05-26 Codex 维护 4-7 包：结构整理和优化

```text
450 tests OK
repo audit 0 findings
focused 4-7 package tests 46 OK
run_cad_validation.py --no-cad pass: output\validation_runs\codex-maintenance-4-7-no-cad
```

本轮把 1-3 包止血后的安全边界整理为可复用结构：新增 `core/path_safety.py`，统一 project root / output root / safe path segment 校验；project sample CAD check、composition CAD check、beta suite、proposal confirmed、drawing-read、blank-shell / non-CAD pipeline 等入口在连接真实 CAD 或写 artifact 前先拒绝越界路径。`core/schemas/*.schema.json` 已全部纳入 registry 和 invalid fixture 覆盖；handoff、状态页和 PlanMD 口径已去除“下一包/剩余表”副计划，后续优先级继续只以 `CORE_RESTRUCTURE_PLAN.md` 为准。本轮未运行真实 CAD，不新增 `geometry_verified` 结论。

### 2026-05-26 Codex 维护 1-3 包：先止血、再加固

```text
432 tests OK
repo audit 0 findings
focused 1-3 package tests 48 OK
run_cad_validation.py --no-cad pass: output\validation_runs\codex-maintenance-fix-no-cad
blank-shell benchmark 8/8 pass (non-CAD)
office alpha benchmark 18/18 pass (non-CAD)
interior delivery benchmark 3/3 pass (non-CAD)
project sample strict no-CAD check returns 1 with deferred report
```

本轮补上三类维护边界：`run_project_sample_cad_check.py --require-cad-verified` 防止把 no-CAD deferred 当作真实 CAD 几何通过；`projects/` 样本 manifest 输入路径限制在样本目录内；benchmark / drawing-read case_id 与 output root、CAD validation output dir 均限制在安全边界内。当前仓库存档的 `BETA-PROJECT-SAMPLE-05` no-CAD 报告仍是 `deferred`，不是真实 AutoCAD `geometry_verified`；真实样本 CAD 几何声明必须另跑用户会话下的 created-handle readback。

### 2026-05-26 Codex 深度全量安全复盘

```text
424 tests OK
repo audit 0 findings
Python AST parse 248 files / 0 errors
JSON parse 166 files / 0 errors
project sample protocol scan pass, 2 samples
project sample benchmark pass, 2/2 cases
proposal confirmed benchmark pass, 2/2 cases
CAD beta evidence rollup pass, 5/5 subpackages
office scene beta benchmark pass, 9/9 cases
residential scene beta benchmark pass, 8/8 cases
restaurant scene beta benchmark pass, 8/8 cases
```

Cursor 大改后的深度复盘已完成一轮加固：benchmark expected evidence triplet 现在强制包含 `evidence_state` / `geometry_accuracy` / `screenshot_role`，proposal confirmed benchmark 输出并校验 `evidence_summary`；项目样例 CAD check 和 drawing standard profile 已回到统一 evidence vocabulary；repo audit 暴露的 6 个大文件职责风险已拆为小模块。该轮结论仍主要证明 non-CAD benchmark、样本协议、证据门禁和有限 CAD 验证链路，不扩大为真实项目 DWG 或任意 CAD_PLAN 全量几何准确。

### 2026-05-26 Codex 风险验收补记

```text
290 tests OK
repo audit 0 findings
office alpha benchmark 14/14 pass (non-CAD)
run_cad_validation.py --no-cad --block-alpha-only pass with block_alpha_deferred_evidence
real CAD block alpha pass: output\validation_runs\codex-review-block-alpha-cad-after-gate
real CAD full validation pass: output\validation_runs\codex-review-full-cad-after-gate
negative COM probe pass: arbitrary block_id/name rejected, CODEX_PREVIEW entity count 111 -> 111
second gate real CAD block alpha pass: output\validation_runs\codex-second-gate-block-alpha-cad-final
second gate real CAD full validation pass: output\validation_runs\codex-second-gate-full-cad-final
second gate negative COM probe pass: illegal identity/attributes/base_point rejected, ModelSpace count 131 -> 131
```

本轮将 block alpha 和 CAD readback 证据门禁从“字段自报”加固为 created-handle 绑定：`geometry_verified` 必须有非空 `created_handles`、实体回读 payload 和 `created_handles_scope=pass`；block alpha 还必须证明 `entity.type=block_reference`。该结论仍只覆盖受控样本和当前测试 CAD 会话，不扩大到真实块库、属性块、正式图层或任意项目图纸。

当前 Core 已完成 Phase O-V 的非 CAD 主线和一次系统层安全补强。最新记录为：

```text
452 tests OK
self_check.py pass
render_preview.py --check ready
repo audit 0 findings
focused 4-7 package tests 46 OK
Python AST parse 248 files / 0 errors
JSON parse 166 files / 0 errors
blank-shell pipeline ok
office/residential/restaurant scene beta benchmark 25/25 cases pass
project sample benchmark 2/2 cases pass
proposal confirmed benchmark 2/2 cases pass
CAD beta evidence rollup 5/5 subpackages pass
interior delivery real CAD composition check 3/3 geometry_verified
project sample strict no-CAD check rejected deferred as expected
run_cad_validation.py --no-cad pass
run_cad_validation.py --no-cad pass: output\validation_runs\codex-polish-final-no-cad
Phase W W-07 CAD foundation run_cad_validation.py pass
R-BLOCK-PLAN insert_block_alpha validate/dry-run/fake execute
R-BLOCK-CAD-ALPHA real CAD block alpha geometry_verified (controlled sample)
R-BLOCK-METADATA BLOCK_LIBRARY v0.2 + controlled-test-block-001 metadata
R-CAD-CONTRACT evidence fields on probe/readback + validation hard gates
R-CAD-VIEW-CAPTURE run_cad_validation.py pass, cad-validation-window.png captured
readback_report.json status geometry_verified, evidence_state readback_geometry_verified
cad_capability_probe.json status cad_capability_verified, evidence_state cad_capability_verified
primitive probe covers line/circle/arc/polyline/text/dimensions
```

这证明非 CAD 链路、benchmark、验证总控和维护门禁可用；Phase W baseline 真实 CAD 总验证已在用户会话下完成落图、截图、实体回读和 `geometry_verified` 闭环。本轮还加固了 CAD COM 调用底座：即使 `run_cad_validation.py` 顶层为 `pass`，也必须要求 `readback_report.json.status=geometry_verified`、`cad_capability_probe.json.status=cad_capability_verified` 且关键 checks 全部通过。最新能力探针已覆盖独立直线、圆、弧、闭合多段线、文字、标注和矩形边框。用户指出角色组合截图不在 CAD 后，本轮已将 3 个室内组合案例接入真实 AutoCAD 批量落图与 created handles 回读，最新证据为 `output\validation_runs\interior-composition-cad-label-clean-y8000\composition_cad_check_report.json`，3/3 cases `geometry_verified`。2026-05-26 又完成 `R-CAD-VIEW-CAPTURE` baseline：CAD 总控截图步骤改为 AutoCAD 客户区窗口级截图，并可按本轮 created handles bbox 缩放视图，证据为 `output\validation_runs\r-cad-view-cad\cad-validation-window.png`。当前另有视觉表达线 `VCAD-01/02`：`VCAD-02` 已在真实 AutoCAD 中绘制带门窗、尺寸、房间标签、分区和家具的房间平面，99 created handles 全部回读，截图 `output\previews\vcad-02-visual-room-plan.png`。这些结论仍不扩大为真实项目图纸、块库、块插入或任意 CAD_PLAN 全部准确；截图也仍只是视觉辅助。

## 当前进度估算

估算口径：通用底座和多场景 Agent 各自按 100% 计算；总体默认按 `通用底座 70% + 多场景 Agent 30%` 加权。该估算只用于节奏判断，误差允许约 5-10 个百分点，不能替代测试和真实 CAD 证据。

| 维度 | 当前估算 | 判断依据 | 主要剩余缺口 |
| --- | ---: | --- | --- |
| 通用底座进度 | 约 96% | Core 已覆盖 schema、dry-run、verification、benchmark evidence gate、CAD validation gate、project sample、drawing read、proposal confirmed、repo audit；本轮新增负向 CAD runner、COM 写入前置守卫、能力覆盖率可读报告和 composition 全局无标注策略；focused 35 tests OK | 真实项目 DWG、公司块库、正式图层、ActiveDocument guard 的真实 CAD 会话补验、复杂几何仍需后续真实场景扩展 |
| 多场景 Agent 进度 | 约 93% | office / residential / restaurant scene beta benchmark 合计 25/25 pass；工装三样本 boundary/rollup、office/restaurant P3 父包、多场景 P3 父包与 scene beta 解释模板已同步；composition 模板已收口为 JSON catalog + schema + 全局无标注 | 多数 scene beta 仍为 non-CAD；还不能声称真实 CAD 多场景几何 verified |
| 总体进度 | 约 95% | `96% * 0.70 + 93% * 0.30` | 取决于真实项目样本、正式 CAD 会话安全和多场景真实 CAD 验证扩展 |

本轮新增并细化 Phase R 新鲜视角评审计划，并把代码切口继续落到 benchmark runner 与真实 CAD 批量执行：非 CAD benchmark 现在能显式输出 `evidence_state`、`geometry_accuracy`、`screenshot_role`，并支持 `minimums`、`contains_object_types`、`contains_component_roles`、`contains_object_roles` 断言、`object_spec` 与 `composition_spec` pipeline、suite/case 配置校验，以及 blank-shell / composition 每个 CAD_PLAN 的 dry-run / verification 汇总证据。`examples/benchmarks/office_alpha_benchmark.json` 当前覆盖 object / micro-scene / blank-shell / failure / invalid 共 18 个 non-CAD cases；`examples/benchmarks/interior_delivery_benchmark.json` 覆盖卧室床+地毯、餐桌组合、办公桌组合 3 个 persona composition cases，并输出浏览器截图辅助证据。新增 `scripts/run_composition_cad_check.py` 后，这 3 个组合案例已经在真实 AutoCAD `CODEX_PREVIEW` 中完成批量落图和回读。该进展提升 benchmark 证据门禁，但仍不代表真实块库和复杂家具符号已经完成。

## 能力矩阵

| 能力 | 状态 | 当前依据 | 主要缺口 |
| --- | --- | --- | --- |
| CAD execution | `alpha_verified_cad` | `core/execution/execute_plan.py` 已在真实 AutoCAD 中执行 baseline CAD_PLAN 到 `CODEX_PREVIEW`；`core/execution/batch_plan_runner.py` 已将 3 个室内组合 benchmark 的多 CAD_PLAN 批量写入真实 AutoCAD 并按 created handles 回读；最新组合证据为 `output\validation_runs\interior-composition-cad-label-clean-y8000\composition_cad_check_report.json` | 扩展到更多 CAD_PLAN、真实项目样本和块库插入验证 |
| CAD COM capability probe | `alpha_verified_cad` | `core/verification/cad_capability_probe.py` 已验证活动文档读取、`CODEX_PREVIEW` 图层、矩形边框、独立直线、圆、弧、闭合多段线、文字、标注、handles、定向回读、类型统计和 bbox；`RCAD-06` 已补受控 ANSI31 hatch smoke 回读；证据见 `manual-cad-after-primitive-probe` 与 `output/validation_runs/rcad-06-hatch-cad-20260527-escalated/hatch_cad_smoke_report.json` | 扩展任意 hatch、孤岛 hatch、属性块、选择集和更复杂实体类型 |
| preview safety | `prototype` | `core/safety/policy.py` 默认只允许 `CODEX_PREVIEW`，正式图层/保存/覆盖/删除需要显式批准 | 补批准证据格式和审计字段 |
| validate / dry-run | `alpha_ready_non_cad` | `scripts/validate_plan.py`、`scripts/dry_run_plan.py` 和 core 入口稳定；baseline plan 通过 | 扩展批量 CAD_PLAN 和高层模型失败隔离 |
| self check / repo audit | `alpha_ready_non_cad` | `self_check.py`、`run_repo_audit.py --fail-on-findings` 已进入固定基线 | 继续把新维护风险纳入 audit |
| render preview | `alpha_verified_cad` | `render_preview.py --check` 输出结构化截图能力；`render_preview.py --capture-autocad-window --execution-summary ...` 已在真实 CAD 总控中生成 `output\validation_runs\r-cad-view-cad\cad-validation-window.png`，并按 created handles bbox 缩放视图 | 仍需扩展更细绘图区裁剪、多显示器和遮挡边界；截图不参与几何通过判断 |
| entity readback | `alpha_verified_cad` | `inspect_dwg.py --connect-cad` 已对真实 AutoCAD baseline 输出生成 `readback_report.json`；最新复验使用 created handles 定向回读，`status=geometry_verified` 且 `readback_scope`、`layer_entities`、`bbox_size`、`base_point`、`label_text`、`dimension_count`、`created_handles_scope` 全部 pass | 扩展 before/after snapshot、批量 plan 和真实图纸回读样本 |
| schemas | `alpha_ready_non_cad` | 高层 schema、examples、invalid fixtures、registry 和 validator 已建立 | 扩展真实项目正反例和跨模型引用边界 |
| capability runtime | `alpha_ready_non_cad` | `core/capabilities/` 已登记能力、风险、CAD 依赖、验证命令、maturity、known_limits；`workflow.blank_shell_pipeline` 可运行 | 增加审计记录字段和更多 workflow 类型 |
| artifact graph | `prototype` | workflow artifacts 可排序、检查路径和发现循环依赖 | 接更多工作流和产物差异检查 |
| geometry backends | `prototype` | `rect2d` 与 `orthogonal_polygon` 支持 bbox、正交多边形、no-place-zone、path strip 和基础距离检查 | Phase Y 评估复杂多边形/成熟几何库 |
| drawing analysis | `prototype` | manual drawing model、entity summary、manual shell loader 已可用 | 自动 DWG/PDF 空壳识别仍未开始闭环 |
| project model | `alpha_ready_non_cad` | `build_project_model()` 支持 `DESIGN_BRIEF + DRAWING_MODEL` 或 `DESIGN_BRIEF + SHELL_MODEL`，保留 shell_context | 增加冲突处理、真实样本和场景差异输入 |
| object engine | `prototype` | `object_defaults.json` 覆盖 cabinet/table/chair/desk/shelf/counter/bed/rug/sofa/display_unit/monitor，能生成 OBJECT_SPEC | 补尺寸来源说明和更多对象规格 |
| composition engine | `prototype` | `core/composition_engine/templates.py` 可将卧室床+地毯、餐桌+椅、办公桌+椅+显示器组合转成多 CAD_PLAN、dry-run、unverified verification 和 SVG/PNG 视觉辅助预览；当前 3 个模板已通过真实 CAD 批量落图与 created handles 回读 | 扩展更多组合模板、失败样本和 block insertion alpha |
| block engine | `alpha_verified_cad` | `BLOCK_LIBRARY v0.2`、受控 `controlled-test-block-001`；真实 CAD 受控块插入 + `block_reference` readback 已通过（`r-block-alpha-cad`） | 不扩大到公司块库、属性块或任意块名 |
| layout engine | `prototype` | 多 circulation/zone/placement 候选（`candidate_sets`）；blank-shell 8-case benchmark | 复杂几何、自动读图、真实项目大样本 |
| shell / circulation / function zones | `alpha_ready_non_cad` | Phase P/R/S/V 已完成 shell loader、动线候选、功能区切分并接入 pipeline | 扩展正交 shell、真实空间语义和更复杂样本 |
| proposal engine | `prototype` | `comparison_detail`（覆盖率/失败分布/通道连续性/排序原因，Y-MC-02）；多候选说明保留 | 用户确认流、真实多方案推理（BETA-PROPOSAL Backlog） |
| plan engine | `alpha_verified_cad` | `insert_block_alpha` intent：validate / dry-run / fake execute + 受控样本真实 CAD `geometry_verified` | 不声称任意 CAD_PLAN 或项目图纸块插入均已 verified |
| verification | `alpha_verified_cad` | fake readback、created handles 证据门、截图存在性、before/after diff 和修复建议已建立；`cad_validation_runner` 输出 `evidence_summary` 与顶层 evidence gate（R4-04）；交接 evidence 规则见 `evidence_gate_handoff_rules.md`（R4-05） | 继续扩大失败样本、真实项目样本和多对象 CAD_PLAN 验证 |
| benchmarks | `alpha_ready_non_cad` | minimal、blank-shell 8 cases、**office alpha 18 cases**（含 failure + `expected_evidence_summary`）、interior delivery benchmark 可重复运行；`R4-EVIDENCE-GATES` 已收口（词表、failure 断言、suite 汇总、CAD runner gate、`evidence_gate_handoff_rules.md`） | office / blank-shell 全量真实 CAD readback 仍待后续包 |
| blank-shell pipeline | `alpha_ready_non_cad` | `Y-MULTI-CANDIDATE` 已收口：8-case benchmark + 边界文档；非自动设计大脑 | 复杂几何、自动读图、真实项目样本库 |
| scene agents | `alpha` | Scene Alpha 父包收口（`X-SCENE-ALPHA` 01–05）：三场景 blank_shell benchmark、边界扫描、解释模板；non-CAD only | 后置 Backlog：Scene Beta、真实项目样本等 |

## 近期关键风险

- 不能把 Phase W baseline、基础图元探针或 3 个室内组合案例的 `geometry_verified` / `cad_capability_verified` 扩大解释为真实项目图纸、块库、块插入或任意 CAD_PLAN 全部准确。
- blank-shell pipeline 已可运行，但当前不等于完整自动设计大脑。
- 场景 Agent 已有 preferences，但仍是轻量数据层原型。
- 若继续扩张场景业务而不强化 Core，会重新把通用能力写死到单场景。
- 根目录文档曾经有重复状态描述；当前已把 Phase W/X/Y/Z 长篇执行剧本迁入 `docs/planning/`，并新增 Phase R 新鲜视角评审计划。后续应以 `CORE_CONTEXT_BRIEF.md` 为短入口、本文为能力矩阵、`CORE_RESTRUCTURE_PLAN.md` 为主计划索引。

## 计划入口

后续优先级、Phase 顺序和退出标准只以唯一 `PlanMD`：`CORE_RESTRUCTURE_PLAN.md` 为准。本文只维护能力矩阵、成熟度、证据路径和能力缺口，避免状态页再次变成第二份计划。
