# CAD Agent Core PlanMD（唯一开发主线）

状态：Phase O-V 非 CAD 主线与系统层安全补强已完成；当前主线收束为真实 CAD 扩样、Core/Scene 边界和文档治理
最后更新：2026-05-26

本文是当前仓库唯一 `PlanMD`。用户提到 `plan.md`、`PlanMD` 或“主 plan”时，默认指本文。压缩前完整版本已归档到 `docs/history/root-md-full-snapshot-2026-05-26/CORE_RESTRUCTURE_PLAN.md`。

本文只决定当前活跃队列、Phase 顺序、优先级、Decision Gate 和退出标准；不记录长历史，不替代真实 CAD 验证证据。

未完成 plan、未校验证据和待开发任务包的**精细化执行台账**见 `docs/planning/任务清单.md`（§3 能力证明 **V-PROOF**、§4 代码轨、§5 **RCAD** CAD-MCP）。用户说「一键推进」→ §4 首项 `next`；「能力证明」→ §3 首项 `next`；「CAD 补验」→ §5。台账镜像本文优先级与 Decision Gate，不另立第二套退出标准。

## 防偏离边界

- 本仓库仍是通用 CAD Agent Core Lab，不变成家装、工装、办公、餐饮、展陈或 CAD-MCP 专用项目。
- Core 优先：可复用能力进 `core/`，共享资源进 `libraries/`，项目资料进 `projects/`，场景差异只进 `agents/<scenario>/`。
- `CAD_PLAN` 仍是白话 / 高层模型到 CAD 落图之间的受控中间层；不得从白话直接跳到真实 CAD。
- 真实 CAD 几何准确只看 validate、dry-run、`CODEX_PREVIEW` 实际输出、created handles 定向回读和 `geometry_verified` 证据。
- 场景 Agent 保持轻量。Scene Alpha / Beta 不能写成 Scene Product。
- 文档压缩只降低旧记录权重，不改变开发跟进、验证和状态同步规则。

## PlanMD 主线协议

| 层级 | 文档 | 可以决定 | 不可以决定 |
| --- | --- | --- | --- |
| 1 | `CORE_RESTRUCTURE_PLAN.md` | 当前队列、优先级、Decision Gate、退出标准、后置 Backlog | 无证据地声明真实 CAD 几何准确 |
| 2 | `docs/planning/phase-*.md` | 展开已登记开发包的步骤、命令、检查表 | 独立改变优先级或复制第二套主计划 |
| 3 | `CORE_STATUS.md`、`CAD_AGENT_STATUS.md` | 能力成熟度、证据、风险、当前状态 | 充当第二份计划 |
| 4 | `CAD_AGENT_CHANGELOG.md`、`CAD_AGENT_ISSUES.md`、`docs/history/` | 历史流水、失败教训、旧快照 | 推导新的开发优先级 |

辅助 MD 出现新的“下一步、待办、优先级、退出标准”时，必须回到本文登记或引用本文已有条目。

## 当前复盘结论

当前最准确的一句话：

```text
非 CAD 空壳布局链路已跑通，系统维护门禁已补强，本地 CAD 回归矩阵已有安全入口；场景层目前主要是 Alpha/Beta 验证壳，不是具体场景产品；下一阶段要先扩大真实 geometry_verified 样本，再选择首个场景做产品化闭环。
```

当前可信基线摘要：

- `complex_cad_smoke` 已纳入默认 local CAD regression manifest，真实 CAD 单项 `created_handle_count=23`。
- 最新 full strict CAD matrix：`output\validation_runs\complex-cad-regression-strict-final`，`selected_case_count=4`、`geometry_verified_case_count=7`、`created_handle_count=113`。
- `LCAD-01-REGRESSION-MANIFEST` 已完成。
- `LCAD-02-STRICT-MATRIX-RUNNER` 已完成。
- `DEMAND-01-DEMAND-SIDE-AGENT-SUITE` 已建立需求侧角色 Agent 数据层和 cross-scene non-CAD benchmark，用来从用户需求侧持续暴露 Core 缺口；该层不等于 Scene Product 完成。
- `OBJ-DETAIL-01-COMPONENT-PLAN` 已把“精细餐桌 / 办公椅”等需求沉淀为对象组件级 `CAD_PLAN` 生成能力，并补跑 demand-side 10 case 真实 CAD readback。
- 下一层对象 / 家具图库破局点已明确：不能继续堆抽象矩形，必须在 Core 建立 `SYMBOL_SPEC -> symbol_engine -> symbol_readability` 的 CAD 符号语法层。
- 已按用户要求登记三条系统优化路线：A 先加固 CAD 安全与证据链；B 补 `Core Orchestrator` + `Scene Router`；C 选择 `commercial_fitout` 做首个 Scene Product Alpha 闭环。
- `A-LCAD-04-TO-06-SMOKE-AND-PLAN-MATRIX` 已完成（no-CAD + fake-driver + 用户会话真实 CAD：primitive matrix、fixture suite 3/3 verified）。
- `D-SYMBOL-01-SPEC-SCHEMA` 已完成（`symbol_spec` / `symbol_graph` schema + 反静默 bbox 语义门禁）。
- `D-SYMBOL-02-PRIMITIVES` 已完成（`draw_symbol_glyph` CAD_PLAN + 7 类 part 渲染；validate/dry-run 通过）。
- `D-SYMBOL-03-ARCHETYPE-GRAMMAR` 已完成（6 类 archetype 必备部件 + 位置约束 + 示例）。
- `D-SYMBOL-04-OBJECT-TO-SYMBOL` 已完成（6 类对象映射 + 显式 fallback）。
- `D-SYMBOL-05-READABILITY-GATE` 已完成（`symbol_readability_report` + 5 种可读性状态）。
- `D-SYMBOL-06-CAD-READBACK-SMOKE` 已完成（`execute_plan` 支持 `draw_symbol_glyph`；desk glyph smoke + readback；5 tests OK；真实 AutoCAD 已在 `user-cad-full-verify-20260526` verified）。
- `D-SYMBOL-07-BLOCK-FALLBACK-POLICY` 已完成（`resolve_symbol_render_resolution` + 四级 fallback evidence + 反静默退化；6 tests OK）。
- `B-ORCH-01-REQUEST-CONTEXT` 已完成（`REQUEST_CONTEXT` schema + `evaluate_request_gate`；缺输入 blocked；6 tests OK）。
- `B-ORCH-02-SCENE-REGISTRY` 已完成（`scene_registry.json` + `load_scene_registry`；7 scenes；7 tests OK）。
- `B-ORCH-03-ACTIVATION-POLICY` 已完成（`evaluate_scene_activation`；默认 `no_scene`；多触发词追问；7 tests OK）。
- `B-ORCH-04-WORKFLOW-DISPATCH` 已完成（`orchestrate_request` + `workflow_routes.json`；复用现有 Core runners；7 tests OK）。
- `B-ORCH-05-ROUTE-AUDIT-REPORT` 已完成（`route_audit_report` schema + `build_route_audit_report`；`orchestrate_request` 写入 `route_audit_report.json`；4 tests OK）。
- B 路线 `B-ORCH-01`~`05` 已全部收口。
- `C-CFIT-01-SCOPE-AND-SUBSCENES` 已完成（开放办公 / 会议室 / 前台接待三子场景；`SCOPE.md` + `subscenes.json`；边界扫描通过；5 tests OK）。
- `C-CFIT-02-OBJECT-CATALOG` 已完成（14 项 catalog + `catalog_entry_to_object_specs`；layout pipeline 可读；5 tests OK）。
- `C-CFIT-03-BLOCK-MAPPING` 已完成（受控 fitout 块库 + mapping；禁止任意块名；block / OBJECT_SPEC fallback；7 tests OK）。
- `C-CFIT-04-MICRO-SCENE-BENCHMARK` 已完成（8 case benchmark；4 pass + 4 `blocked_expected_non_cad`；6 tests OK）。
- `C-CFIT-05-SAMPLE-PROJECT-CONFIRMATION` 已完成（脱敏样本 `commercial_fitout_sample`；确认前 `confirmation_pending`；确认后 `confirmed_cad_plan_bundle` + assumptions/risks；4 tests OK）。
- `C-CFIT-06-REAL-CAD-SMOKE` 已完成（`commercial_fitout_sample` 确认后 3 个 `CAD_PLAN`；FakeCadDriver readback `geometry_verified`；`product_claim_boundary` 禁止扩大为完整工装产品；3 tests OK）。
- `C-CFIT-07-PRODUCT-BOUNDARY-ROLLUP` 已完成（`product_alpha_boundary.json` + 状态页保守口径；5 tests OK）。**C 路线工装 Scene Product Alpha 已收口。**
- `LCAD-07-BLOCK-ATTRIBUTE-HATCH` 已完成（`cad_block_attribute_hatch_boundary.json`；block/attribute verified；hatch deferred；12 tests OK）。
- `LCAD-08-PROJECT-SAMPLE-CAD` 已完成（双样本 rollup；真实 CAD `geometry_verified` 2/2；`created_handle_count` 20+12；3 tests OK）。
- `LCAD-09-SCENE-COMPOSITION-CAD` 已完成（用户会话 manifest strict：`composition_cad` 3/3 cases `geometry_verified`；40 handles；不扩大为 Scene Product）。
- 用户会话全量补验：`output/validation_runs/user-cad-full-verify-20260526/`（manifest 7/7 几何 verified；汇总见 `user_cad_full_verify_summary.json`）。
- 下一包（代码轨）：`LCAD-10.1-NEG-FIXTURES`（见 `docs/planning/任务清单.md` §4）。
- 能力证明体系（路线 **F**）：`V-PROOF-00-REGISTRY-SCHEMA`（见 §3、架构 `docs/planning/capability-proof-architecture.md`）。
- 真实 CAD 补验（路线 **E** / RCAD）：见 `docs/planning/任务清单.md` §5；执行后须回写能力登记表。

## Core / 场景成熟度

| 层级 | 进入标准 | 当前判断 |
| --- | --- | --- |
| Core 底座 | 通用 schema、workflow、`CAD_PLAN`、CAD IO、验证、安全、benchmark、读图、对象、图块能力 | Alpha 原型较厚，仍需真实 CAD 扩样 |
| Scene Alpha 壳层 | preferences、词汇、排序权重、解释模板、边界扫描 | office / residential / restaurant 已完成 Alpha 验收 |
| Scene Beta 能力包 | 对象体系、微场景、failure benchmark、non-CAD 证据 | office / residential / restaurant 已有 beta benchmark |
| Scene Product 场景产品 | 真实项目样本、图块 metadata、真实 CAD smoke、用户确认流 | `commercial_fitout` 为 Scene Product **Alpha**（C-CFIT 已收口）；office / residential / restaurant 仍为 Alpha/Beta |

未来场景能力采用：

```text
Core Orchestrator -> Scene Router -> Scene Registry -> Scene Capability Module -> Core workflow
```

没有明确场景或项目 manifest 指定时，路由必须是 `no_scene`。

## 当前活跃工作队列

| 包 | 状态 | 目标 | 退出证据 |
| --- | --- | --- | --- |
| `LCAD-01-REGRESSION-MANIFEST` | done | CAD regression manifest schema、默认 case、metadata 输出 | no-CAD manifest pass；真实 CAD strict smoke 已有受控证据 |
| `LCAD-02-STRICT-MATRIX-RUNNER` | done | `--case`、默认 all、`--strict`、统一 rollup | selected no-CAD pass；strict all CAD pass |
| `LCAD-COMPLEX-SMOKE` | done | 复杂混合图形 smoke 纳入默认 manifest | real smoke `geometry_verified`；full strict matrix pass |
| `DEMAND-01-DEMAND-SIDE-AGENT-SUITE` | done | 多场景需求侧角色 Agent、需求 case 记录和 benchmark 分派 | 12 个角色覆盖 6 场景；10 个 demand case non-CAD pass |
| `OBJ-DETAIL-01-COMPONENT-PLAN` | done | table / bed / chair / sofa / desk 组件级 `CAD_PLAN` 展开 | focused tests pass；demand benchmark 中精细餐桌和办公椅走 `object_detail_spec`；10 case 真实 CAD `geometry_verified` |
| `SYMBOL-CORE-01-CAD-SYMBOL-GRAMMAR` | done | 在 Core 建立 CAD 平面符号语法层，让对象从矩形组件升级为可读家具 / 图库符号 | D-SYMBOL-01~07 已收口；desk glyph FakeCad readback；fallback policy 证据链 |
| `LCAD-03-ACTIVE-DOCUMENT-GUARD` | done | 连接前后记录 ActiveDocument、no-save、no-delete、preview-only 守卫 | `03.1`~`03.4` 子包完成；snapshot、audit、write_guard、created_handle_scope 已接入 |
| `LCAD-04-BASELINE-SMOKE-EXPANSION` | done | 扩 baseline CAD smoke 样本 | local regression manifest 增至 7 case；primitive matrix + fixture suite 接入 |
| `LCAD-05-PRIMITIVE-MATRIX` | done | 扩 line / polyline / circle / arc / text / dimension 等实体矩阵 | `run_primitive_matrix.py` + no-CAD fake-driver pass |
| `LCAD-06-CAD-PLAN-FIXTURES` | done | 批量 `CAD_PLAN` fixture suite | 3 fixture validate + dry-run + fake-driver；用户会话真实 CAD 3/3 verified |
| `LCAD-07-BLOCK-ATTRIBUTE-HATCH` | done | 受控 block、attribute、hatch 能力边界 | `cad_block_attribute_hatch_boundary.json`；12 tests OK |
| `LCAD-08-PROJECT-SAMPLE-CAD` | done | 脱敏样本项目真实 CAD 闭环 | `project_sample_cad_rollup`；real CAD 2/2 verified |
| `LCAD-09-SCENE-COMPOSITION-CAD` | done | 多场景组合真实 CAD smoke | `composition_cad` 3/3 `geometry_verified`（40 handles）；不扩大为 Scene Product |
| `LCAD-10-NEGATIVE-SAFETY` | pending | 非法路径、非法图层、非法 block、保存/删除防线 | 负向用例不写入、不保存、不删除 |
| `LCAD-11-EVIDENCE-TREND-ROLLUP` | pending | 趋势、覆盖率、历史证据索引 | 可机器读趋势报告 |
| **F 能力证明体系（Phase V）** | **in progress** | 登记表 + Lab 矩阵 + Ladder 展示册 + 覆盖率 | 见下文 **路线 F**；任务包见 `docs/planning/任务清单.md` §3 |
| **E 真实 CAD 校验（CAD-MCP）** | **in progress** | P1 Lab 的真实 CAD 执行层 | 见下文 **路线 E**；RCAD 见 `docs/planning/任务清单.md` §5 |

## 路线 E：真实 CAD 校验主线（CAD-MCP）

目标：把仓库内**所有**需要真实 AutoCAD 几何证据的入口，统一登记为 `RCAD-*` 最小包，经 **CAD-MCP 虚拟环境 Python** 调用 `scripts/run_*.py`，在 `CODEX_PREVIEW` 落图并按 **created handles 定向回读** 产出 `geometry_verified` 报告。截图、`dry_run` only、FakeCadDriver 单测、no-CAD benchmark **均不能**替代本路线验收。

### CAD-MCP 执行协议（固定）

```powershell
cd "C:\Users\User\Desktop\新家改造\CAD测试相关文件"
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
```

| 步骤 | 动作 | 通过标准 |
| --- | --- | --- |
| E0 | AutoCAD 已打开**测试 DWG**；允许 COM；未要求保存/覆盖正式图 | `& $py scripts\self_check.py`；`& $py scripts\render_preview.py --check` 见活动文档 |
| E1 | 执行对应 `RCAD` 包命令（见一键推进 §3B） | 报告 `status=geometry_verified` 或 `readback_geometry_verified`；`created_handles` 非空 |
| E2 | 可选视觉辅助 | `render_preview.py --capture-screen` 或窗口级截图；**不参与**几何 pass |
| E3 | 同步证据路径到状态页 / CHANGELOG；更新 `cad_*_boundary.json` 中 deferred 措辞 | 不得把受控样本扩大为任意项目 |

**触发词**：用户说「CAD 补验」「真实 CAD 校验」「开 CAD 了」时，优先推进 `docs/planning/任务清单.md` §5 中第一个 `cad_status=pending` 的 `RCAD` 包（可与 §3/§4 交错，但不得跳过 E0）。RCAD 通过后须回写 `cad_capability_registry.json` 对应行 `claim_level=verified`。

### 校验登记总表（路线 E 父包索引）

| 父包 | 范围 | 执行台账 |
| --- | --- | --- |
| `RCAD-MANIFEST` | 默认 manifest 7 case 与 strict 全矩阵复验 | `RCAD-00`~`03`、`07`~`11` |
| `RCAD-BLOCK-HATCH` | 受控块、属性块、hatch | `RCAD-04`~`06`（`06` 依赖 `LCAD-12` 代码） |
| `RCAD-SYMBOL` | 家具 glyph 真实 CAD | `RCAD-12`~`15` |
| `RCAD-SCENE-FITOUT` | 工装样本与子场景 smoke | `RCAD-17`~`19` |
| `RCAD-DEMAND-OBJECT` | demand-side / 对象细节批量 CAD | `RCAD-16` |
| `RCAD-SAFETY-NEGATIVE` | 负向 plan 真实 CAD 抽检 | `RCAD-20`（依赖 `LCAD-10.3`） |
| `RCAD-GUARD-BETA` | 会话守卫、能力探针、beta suite | `RCAD-21`~`25` |
| `RCAD-REGISTRY` | manifest 补登记、趋势纳入 | `RCAD-26`~`27`（依赖 `LCAD-11` 代码） |

### 已验证 vs 待补验（2026-05-26 基线）

| 类别 | 已有一次真实 CAD `geometry_verified` | 仍待补验 / 文档仍为 deferred |
| --- | --- | --- |
| manifest strict 矩阵 | 7/7 几何 case（用户会话 `user-cad-full-verify-20260526`） | `baseline_cad_validation` **整包**可能非几何 fail（`M-01`） |
| 图元 / fixture / smoke | primitive matrix、fixture×3、complex smoke | manifest 中 `primitive_matrix` 仍为 `requires_real_cad:false`（`RCAD-26`） |
| 项目 / 组合 | rollup 2/2、composition 3/3 | 第二样本（`CFIT-09`）、子场景独立 case（`RCAD-18`~`19`） |
| 块 / 属性 | `CODEX_TEST_BLOCK_001`、attribute probe | hatch（`RCAD-06`）、公司块（user_gate） |
| 符号 | desk glyph | chair / table / sofa glyph（`RCAD-13`~`15`） |
| 工装 | rollup 内 12 handles | 专用 `run_commercial_fitout_cad_smoke.py` 报告（`RCAD-17`）；`product_alpha_boundary` 仍写 deferred（`M-04`） |
| demand-side | 10/10（100 handles） | 缺稳定 CLI 时需复验并文档化（`RCAD-16`） |
| 负向 / 守卫 | — | 负向真实 CAD（`RCAD-20`）、LCAD-03 全链路真实 CAD（`RCAD-21`） |

完整逐步命令、输出目录与 `cad_status` 见 **`docs/planning/任务清单.md` §5**。

## 路线 F：能力证明体系（Phase V / Capability Proof）

目标：把 **工程完备度**、**CAD 几何证明覆盖率**、**Capability Ladder 展示等级** 拆成三个独立指标；每个可对外声称的能力登记为一行，绑定 `claim_level`、`cad_case`、证据路径与 Ladder 等级。禁止用 Core 约 96% 的工程节奏估算代替「已证明能画准 / 能画复杂图块」。

架构说明：`docs/planning/capability-proof-architecture.md`（四层 P0~P3、claim_level、Ladder L0~L5）。

### 与路线 E 的关系

```text
路线 F（证明体系）= 登记什么能力、证明到什么程度、对外展示到哪一级
路线 E（RCAD）     = 在 AutoCAD 上执行最小 CAD case，产出 geometry_verified
```

RCAD 是 **P1 Capability Lab** 的执行手段，不是整套证明体系的全部。`LCAD-11` 证据趋势并入 **V-PROOF-71**。

### 父包索引（执行台账见任务清单 §3）

| 板块 | 包 ID 段 | 退出标准（摘要） |
| --- | --- | --- |
| V0 登记与覆盖率 | `V-PROOF-00`~`05` | schema + 首版 registry + `cad_capability_coverage.json` 可复跑 |
| V1 Intent / Primitive | `V-PROOF-10`~`19` | 每个 intent 有 case 或 explicit `deferred` |
| V2 Object / Catalog | `V-PROOF-20`~`29` | catalog 行 + 代表 CAD 或 deferred |
| V3 Symbol | `V-PROOF-30`~`39` | 6 archetype + readability 进 registry |
| V4 Block / Composition | `V-PROOF-40`~`49` | 块矩阵 + composition 扩样 verified |
| V5 Negative / Guard | `V-PROOF-50`~`59` | 负向与守卫真实 CAD |
| V6 Showcase / Ladder | `V-PROOF-60`~`69` | `docs/verification/capability_showcase/` 可浏览 |
| V7 项目回归 / 趋势 | `V-PROOF-70`~`79` | 多样本 manifest + 趋势 Dashboard |

**触发词**：用户说「能力证明」「能力考证」「覆盖率」「能画多厉害」时，推进 `docs/planning/任务清单.md` §3 首项 `status=next`（当前 **`V-PROOF-00-REGISTRY-SCHEMA`**）。

**当前诚实定位（2026-05-26）**：CAD 证明覆盖率定性 **<10%**（待 V-PROOF-02 首算）；展示等级最高约 **L3~L4 边缘**（工装片段）；**无 L5**。

## 系统优化路线拆分

这些路线都进入主计划，但执行顺序不同。默认推荐顺序仍为 **A -> B -> C**：先把真实 CAD 安全与证据链打稳，再补统一中控和场景路由，最后选择一个场景做产品闭环。`SYMBOL-CORE` 是对象 / 图库能力的横向 Core 路线，可在用户明确要求家具图库、符号可读性或“不要再是一堆矩形”时优先执行。用户明确切换优先级时，以用户指令为准。

### A. CAD 安全与证据链

目标：让任何真实 CAD 写入都能证明“写到了目标文档、只写了 `CODEX_PREVIEW`、没有保存/删除/污染正式图层，并能按 created handles 回读”。

| 子包 | 状态 | 目标 | 退出证据 |
| --- | --- | --- | --- |
| `A-LCAD-03.1-ACTIVE-DOC-SNAPSHOT` | done | 连接 CAD 前后记录 `ActiveDocument` 指纹、文档路径 / 标题、预览图层实体计数和 modelspace 快照摘要 | `core/verification/cad_session_guard.py` + capability probe `active_document_guard` / `active_document_snapshot.json`；fake-driver 9 tests OK |
| `A-LCAD-03.2-PREVIEW-ONLY-AUDIT` | done | 执行摘要统一记录 `layer=CODEX_PREVIEW`、`saved_dwg=false`、`deleted_entities=false`、`modified_formal_layers=false` | `preview_only_audit.py` + `execute_plan` / probe / smoke / validation 门禁；focused 单测通过 |
| `A-LCAD-03.3-NO-SAVE-NO-DELETE-GUARD` | done | 对保存、覆盖、删除、正式图层写入建立负向守卫 | `write_guard.py` + driver 门禁 + capability probe `write_guard_negative`；fake-driver 单测通过 |
| `A-LCAD-03.4-CREATED-HANDLE-SCOPE` | done | 明确所有几何验证只看本轮 created handles，不扫描或误判历史实体 | `created_handle_scope.py` + readback/probe `created_handle_scope` 字段；`miss_count`/`extra_entity_count` 门禁 |
| `A-LCAD-04-TO-06-SMOKE-AND-PLAN-MATRIX` | done | 扩 baseline smoke、基础图元矩阵和批量 `CAD_PLAN` fixture suite | no-CAD / fake-driver + 用户会话真实 CAD（primitive matrix、fixture suite） |
| `A-LCAD-07-TO-11-HARDENING-TAIL` | in progress | LCAD-07~09 done；LCAD-10..11 pending | 见各 LCAD 子包 |

### B. Core Orchestrator + Scene Router

目标：把“用户请求如何进入 Core、何时启用场景模块、何时保持 `no_scene`、证据如何汇总”做成统一中控，避免后续场景越做越散。

| 子包 | 状态 | 目标 | 退出证据 |
| --- | --- | --- | --- |
| `B-ORCH-01-REQUEST-CONTEXT` | done | 定义统一请求上下文，记录用户意图、项目 manifest、可用输入、是否允许 CAD、是否需要追问 | `request_context.schema.json` + `evaluate_request_gate`；blocked / needs_clarification 门禁；6 tests OK |
| `B-ORCH-02-SCENE-REGISTRY` | done | 建立 `Scene Registry`，登记场景 id、触发词、成熟度、能力清单和禁用条件 | `examples/orchestrator/scene_registry.json`；`load_scene_registry` / `match_trigger_terms`；7 tests OK |
| `B-ORCH-03-ACTIVATION-POLICY` | done | 建立场景启用策略：无明确场景默认 `no_scene`；低置信度先追问；场景模块不能绕过 Core | `activation_policy.py` + `merge_activation_into_request_gate`；7 tests OK |
| `B-ORCH-04-WORKFLOW-DISPATCH` | done | 中控按请求类型分派到 drawing / project / layout / object / proposal / CAD validation 等 Core workflow | `workflow_dispatch.py` + `orchestrate_request`；non-CAD 全链路与 symbol glyph 经中控跑通；7 tests OK |
| `B-ORCH-05-ROUTE-AUDIT-REPORT` | done | 输出 route audit：为什么选择该 workflow、是否启用场景、哪些证据可用、哪些能力 deferred | `route_audit_report.schema.json` + `build_route_audit_report`；`orchestrate_request` 附带 report；4 tests OK |

### C. `commercial_fitout` Scene Product Alpha

目标：选择工装作为首个场景产品化闭环，但仍保持场景轻量：场景只提供对象体系、业务规则、图块 metadata、解释模板和确认流，几何、CAD 执行和验证继续回到 Core。

| 子包 | 状态 | 目标 | 退出证据 |
| --- | --- | --- | --- |
| `C-CFIT-01-SCOPE-AND-SUBSCENES` | done | 收敛首版工装范围：开放办公、会议室、前台接待三个子场景；明确不做完整施工图承诺 | `SCOPE.md` + `subscenes.json` + `commercial_fitout_scope` schema；`tests.agents.test_commercial_fitout_scope` 5 tests OK |
| `C-CFIT-02-OBJECT-CATALOG` | done | 建立工装对象体系：工位组、办公桌、办公椅、会议桌、文件柜、前台、打印区、设备柜等 | `capabilities/object_catalog.json` + `commercial_fitout_catalog.py`；`tests.agents.test_commercial_fitout_catalog` 5 tests OK |
| `C-CFIT-03-BLOCK-MAPPING` | done | 建立受控块 metadata：尺寸、插入点、旋转、fallback、适用子场景和禁用条件 | `block_mapping.json` + `commercial_fitout_block_library.json`；`resolve_catalog_object_render`；7 tests OK |
| `C-CFIT-04-MICRO-SCENE-BENCHMARK` | done | 建立成功 / 失败微场景：入口冲突、柜前净空不足、通道不足、会议座位不足等 | `commercial_fitout_micro_scene_benchmark.json`；`evaluate_fitout_composition_layout_failure`；6 tests OK |
| `C-CFIT-05-SAMPLE-PROJECT-CONFIRMATION` | done | 选择 1 组脱敏样本，从 `SHELL_MODEL` / proposal 到用户确认 bundle 形成闭环 | `projects/commercial_fitout_sample`；`confirmation_pending` gate；`commercial_fitout_sample_confirmation_bundle.json`；4 tests OK |
| `C-CFIT-06-REAL-CAD-SMOKE` | done | 对代表工装 case 执行 `CODEX_PREVIEW` 真实 CAD smoke 和 created handles readback | `run_commercial_fitout_cad_smoke.py`；FakeCadDriver `geometry_verified`；`product_claim_boundary`；3 tests OK |
| `C-CFIT-07-PRODUCT-BOUNDARY-ROLLUP` | done | 汇总场景产品 Alpha 能力、不可声明事项、下一阶段差距 | `product_alpha_boundary.json`；`subscenes.json` → `product_boundary`；5 tests OK |

### D. `SYMBOL-CORE` CAD 符号语法与家具图库底座

目标：把 Core 从“会画几何 / 多个矩形”升级为“会生成 CAD 图纸可读符号”。本路线不以某 10 个 demand case 为边界，也不先做一批孤立样本；它先建立通用 `SYMBOL_SPEC`、符号 primitive、archetype grammar、对象到符号的映射、可读性验收和真实 CAD readback 门槛。

核心链路：

```text
OBJECT_SPEC
-> SYMBOL_SPEC
-> SYMBOL_GRAPH / SYMBOL_PLAN
-> CAD_PLAN / CAD primitives
-> validate + dry-run
-> CODEX_PREVIEW + created handles readback
-> symbol_readability_report
```

| 子包 | 状态 | 目标 | 退出证据 |
| --- | --- | --- | --- |
| `D-SYMBOL-01-SPEC-SCHEMA` | done | 定义 `SYMBOL_SPEC` / `SYMBOL_GRAPH`，表达符号类型、视图、footprint、orientation、parts、readability constraints 和 fallback policy | schema registry + invalid fixture + `validate_symbol_spec` 反静默 bbox；17 tests OK |
| `D-SYMBOL-02-PRIMITIVES` | done | 建立通用符号 primitive：outline、inner_offset、thick_band、split_line、leg_marker、arc_marker、orientation_marker 等 | `draw_symbol_glyph` intent；desk 示例 validate + dry-run；12 symbol tests OK |
| `D-SYMBOL-03-ARCHETYPE-GRAMMAR` | done | 建立 archetype grammar：surface、seating、sleeping、storage、display、workstation | `ARCHETYPE_GRAMMARS` + 6 示例 + `validate_archetype_grammar`；18 symbol tests OK |
| `D-SYMBOL-04-OBJECT-TO-SYMBOL` | done | 将 `OBJECT_SPEC` 映射到 `SYMBOL_SPEC`，优先输出符号语法；不支持时明确 fallback | `object_spec_to_symbol_spec`；6 类对象 + counter/elevation 显式 fallback；11 tests OK |
| `D-SYMBOL-05-READABILITY-GATE` | done | 新增 `symbol_readability_report`，检查关键部件存在、相对位置、最小可读尺寸、非单 bbox、fallback 是否明确 | `readability.py`；5 状态可区分；11 tests OK（no-CAD） |
| `D-SYMBOL-06-CAD-READBACK-SMOKE` | done | 代表 glyph 写入 `CODEX_PREVIEW` 并按 created handles 回读；截图只作辅助 | `symbol_glyph_cad_smoke.py` + `execute_plan` `draw_symbol_glyph`；desk 样本 line:9 circle:1；FakeCad `geometry_verified` |
| `D-SYMBOL-07-BLOCK-FALLBACK-POLICY` | done | 预留真实块库优先策略：有受控 block 用 block，无 block 用 symbol glyph，再不行 component preview，最后 bbox placeholder | `fallback_policy.py`；`tier_assessments` + `silent_degradation` 检测；6 tests + benchmark fixture |

## 后置 Backlog

这些方向**不**在本节展开子包；能力证明见 §3 **V-PROOF**；代码轨见 §4；**真实 CAD** 见 §5 **RCAD** 与路线 E。

| 方向 | 目标 | 能力证明 §3 | 代码轨 §4 | CAD §5 |
| --- | --- | --- | --- | --- |
| 能力证明体系 | 登记 + Lab + Ladder | `V-PROOF-00`~`79` | `LCAD-10`/`11` | `RCAD-*` 回写 |
| 真实项目样本闭环 | 脱敏样本、回归集 | `V-PROOF-70` | `CFIT-09`、`PROJ-*` | `RCAD-10` |
| 工装 Scene Product | Alpha → Product | `V-PROOF-62` | `CFIT-08`~`12` | `RCAD-17`~`19` |
| 自动读图 / 空壳识别 | shell 候选 + 人工确认 | — | `DRAW-*` | — |
| 多方案设计与交互确认 | scoring、确认、replan | — | `PROP-*` | 确认后 CAD |
| 图块库能力扩展 | hatch、属性块、公司块库 | `V-PROOF-40`~`41` | `LCAD-12` | `RCAD-04`~`06` |
| CAD 符号 / 家具图库 | 多 archetype、block-first | `V-PROOF-30`~`35` | `SYMBOL-08`~`09` | `RCAD-12`~`15` |
| 其他场景 Scene Product | 三场景 Product | 新场景先 V0 登记 | P3 `user_gate` | 定稿后 RCAD |

## 每个开发包固定子校验

1. 更新或新增失败测试 / fixture。
2. 实现最小变更。
3. 跑 focused 测试。
4. 跑相关 no-CAD gate。
5. 若涉及真实 CAD，跑 `CODEX_PREVIEW` + created handles readback。
6. 同步 `CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md`；若来自失败或风险，同步 `CAD_AGENT_ISSUES.md`。
7. 每完成一个 PlanMD 开发包，更新 `docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md`。

## Decision Gates

- **CAD gate**：没有真实 CAD readback 时，只能写 `deferred` / `not_verified_without_cad_readback`。
- **Capability proof gate**：未在 `cad_capability_registry` 登记且 `claim_level` 非 `verified`/`showcase` 的能力，不得对外声称 CAD 已通过；工程完备度百分比不能代替 CAD 证明覆盖率。
- **Safety gate**：任何真实 CAD 写入必须默认 `CODEX_PREVIEW`，不得保存、覆盖、删除或修改正式图层。
- **Scene gate**：Scene Alpha / Beta 只能证明 Core 可被场景驱动；Scene Product 需要真实项目样本和真实 CAD smoke。
- **Doc gate**：根目录 MD 只保留当前摘要；长历史进入 `docs/history/`。
- **User gate**：遇到真实项目、正式 DWG、公司块库、保存/覆盖/删除、场景产品路线切换时，必须先获得用户明确指令。

## 完成判定

一个包只有同时满足以下条件，才能写成完成：

- 有明确范围和退出标准。
- 对应测试或验证命令已运行。
- CAD 相关声明有 validate、dry-run、`CODEX_PREVIEW`、created handles readback 和 `geometry_verified` 证据。
- 不能声称的边界已写清。
- 状态、变更、问题和 handoff 按需同步。
