# 任务清单

最后更新：2026-05-28（§4 能力轨 52/52 对账收口）

唯一**执行台账**（原 `一键推进.md`）：含 **§3 能力证明**、**§4 代码轨**、**§5 CAD 补验** 三个板块，以及 §0 **「真实 CAD 实力」** 口令（编排表 C，不等于 §4 一键推进）。优先级与 Decision Gate 以 `CORE_RESTRUCTURE_PLAN.md`（路线 E + **路线 F**）为准。

架构说明：[`capability-proof-architecture.md`](capability-proof-architecture.md)

---

## 0. 30 秒上手

| 你说… | 做啥 | 看哪 |
| --- | --- | --- |
| **一键推进** | 推进 **1 个**代码包（§4 代码轨） | [§4 代码轨](#4-代码轨) 首行 `next` |
| **能力证明** / **能力考证** / **覆盖率** | 推进能力登记与 Lab 矩阵（§3 单包） | [§3 能力证明轨](#3-能力证明轨-phase-v) 首行 `next` |
| **CAD 补验** / **开 CAD 了** | 跑 RCAD 真实几何（§5 单包） | [§5 CAD-MCP 轨](#5-cad-mcp-轨路线-e) |
| **真实 CAD 实力** / **推进表 C** / **表 C** / **刷新表 C** | 拉高 **表 C**（登记 verified / L3+ / showcase）；见下节 | [§0.1 真实 CAD 实力口令](#01-真实-cad-实力口令) |
| **停止刷表 C，推进 CAD 画面能力** / **推进 CAD 画面能力** | 暂停 registry/coverage 刷数，推进 **VCAD 视觉表达包** | 已新增 `VCAD-01`/`VCAD-02`；后续按画面观感 + CAD 回读验收 |
| 查完成记录 | 不读队列 | `CORE_RESTRUCTURE_PLAN.md` |

### 三指令执行进度（台账完成度）

与下方「工程完备度 / CAD 证明覆盖率」**不是同一套数**。这里只回答：**本文三个板块里，任务包队列大概完成了多少**。

| 指令 | 对应板块 | 任务包总量（粗估） | 当前执行进度 | 说明 |
| --- | --- | ---: | --- | --- |
| **能力证明** | §3 `V-PROOF` | **45** | **100%** | **45/45 done**；§3 能力证明轨已收口 |
| **一键推进** | §4 代码轨 | **52**（§4.0 历史 9 + §4.1 活跃 15 + §4.2 波次 **28**） | **100%** | **52/52 done**；能力轨已收口；继续见 PlanMD 后置或 §3 |
| **RCAD 烟囱包** | §5 `RCAD` | **29** | **100%**（29/29 `verified`；+`RCAD-06`） | **≠ 表 C 真实 CAD 实力**；hatch 仅证明受控 ANSI31 smoke |

**估算口径（Agent 每轮交付时同步更新本表）：**

```text
执行进度 ≈ 本板块 status=done 的包数 ÷ 本板块任务包总量（见各节「包计数」）
新增包入表 → 分母变大 → 百分比可能下降
```

**当前 next（三指令各 1 个）：**

| 指令 | next 包 ID |
| --- | --- |
| 能力证明 | §3 **已收口**；继续见 `CORE_RESTRUCTURE_PLAN.md` 后置 Backlog |
| 一键推进 | §4 **已收口**；默认转 PlanMD 后置 Backlog |
| RCAD 烟囱包 | §5 暂无 pending；继续请转 §3 表 C / 能力证明 |
| **真实 CAD 实力** | 默认 §3 首行 `next` + 对应 RCAD；仅刷新时只跑 coverage |

### 最终回复轻量口径

聊天交付默认不展开完整 A/B/C，使用 **1 张精简进度表**：先报表 C 主指标，再报本轮进展 / 验证、表 A 折叠工程节奏、表 B 本轮相关中文轨道。

| 默认行 | 写什么 | 数据源 |
| --- | --- | --- |
| 真实 CAD 实力 | 主指标约 9.15%，最高 L4；必要时补瓶颈 | coverage JSON |
| 本轮进展 | 完成的包、文件、测试或“不新增真实 CAD 几何证明” | 本轮实际动作 |
| 工程节奏 | 总约 95%（Core 96%，Agent 93%） | `CORE_STATUS.md` |
| 任务台账 | 只写本轮相关中文轨道：能力证明 / 代码轨 / CAD 补验；未触达则写“本轮未改变任务台账” | 本节三指令执行进度 |

完整表 A/B/C 仅在完整状态、交接、审计、进度盘点、表 C 专题、更新 registry/showcase/coverage，或改变能力证明 / 代码轨 / CAD 补验计数时展开。无论精简或展开，表 A、表 B、表 C 都不得混用。

**任务包拆分 / 聚合边界：**

- §4 已于 2026-05-28 对账：**原分母 55（含 §4.2 历史占位 31）→ 执行包 52（§4.2 明细 28）**；历史包 ID 不改，3 个占位标 `cancelled`/`merged`（见 [§4.2 分母对账](#42-分母对账2026-05-28)）。
- 除上述 §4 对账外，**不随意重构** §3 的 45 包、§5 的 29 包分母。
- 可以把多个包在最终回复里展示为“能力证明 / 代码轨 / CAD 补验”三类或更粗的能力域，但真实计数仍以本节任务包表为准。
- 只有当退出条件过大、代码轨与真实 CAD 混杂、或一个包无法独立验证时才拆包；只有纯文档收口、同一证据链小包、无独立验证价值的占位包才考虑聚合。
- 真正改变包 ID、分母、优先级或退出标准时，先同步 `CORE_RESTRUCTURE_PLAN.md`，再更新本节计数和状态页。

### 0.1 真实 CAD 实力口令

用户说 **「真实 CAD 实力」**、**「推进表 C」**、**「表 C」** 或 **「刷新表 C」** 时，Agent **不以 §4 代码轨为主**；按下列顺序执行 **1 轮**（与「能力证明」「CAD 补验」可组合，但本口令自带收尾）：

| 步骤 | 动作 | 拉动表 C 哪一格 |
| ---: | --- | --- |
| 1 | 读 `cad_capability_coverage.json`（无则先 `run_capability_coverage.py`） | 基线 |
| 2 | 选 **1 个**最能抬高表 C 的 `V-PROOF` 包并执行（默认 §3 `next`；`showcase_count=0` 且用户未指定时优先 **V6** `V-PROOF-60`~`64`） | 覆盖率 / 实力指数 / L3+ / 展示就绪度 |
| 3 | 若该包登记了 `RCAD-*` 且用户会话可开 CAD → 跑对应 RCAD **`--real-cad`**（或用户已说「开 CAD 了」） | 几何证据 |
| 4 | 跑 `run_capability_evidence_audit.py` + `run_visual_cad_review.py` + `run_table_c_evidence_gate.py`；若 `writeback_allowed=false`，停止本轮 writeback | 硬证据 / 截图复盘门 |
| 5 | `run_capability_registry_writeback.py --apply`（有报告且 gate 通过时） | 登记表 |
| 6 | `run_capability_coverage.py`（必要时加 `--require-evidence-audit-pass`）→ 交付 **先报表 C**（含主指标与子指标） | 全表 C |

**仅刷新、不推进包**：用户说 **「刷新表 C」** 时只做步骤 1（缺报告则 5）与交付表 C，不新开 `V-PROOF` / RCAD。

**视觉优先口令**：用户说 **「停止刷表 C，推进 CAD 画面能力」**、**「推进 CAD 画面能力」**、**「图块太简单」** 或同等意思时，暂停本节表 C 刷数流程，优先推进 `VCAD-*` 视觉表达包；验收以 AutoCAD 截图、created handles 回读、实体类型丰富度和 preview-only 安全为准。`VCAD` 不自动改变 §3/§4/§5 包计数，也不允许用视觉截图替代表 C 机器值。

**默认 `next_strength`（2026-05-27）**

| 优先级 | 条件 | 推进包 |
| --- | --- | --- |
| P0 | `showcase_count=0` 且用户要抬 **主指标** | `V-PROOF-60-SHOWCASE-INDEX` 或 `V-PROOF-62-L3-FITOUT-SNIPPET`（§3 V6） |
| P1 | 抬 **L3+ 场景片段** | `V-PROOF-34` + fitout/composition 真实 CAD；链式 `RCAD-15` / `RCAD-18` 等 |
| P2 | 抬 **登记覆盖率** | §3 首行 `next` 的 verified 回写行（避免只加 smoke 行） |

**禁止**：用 RCAD 烟囱完成度代替表 C；用 primitive 矩形 smoke 冒充 L3 微场景；不回写 registry 就声称表 C 已上升；截图 / 视觉复盘失败时不得执行本轮表 C writeback。

### 四进度口径（禁止混用）

| 指标 | 当前粗估 | 回答什么 | 看哪 |
| --- | --- | --- | --- |
| **工程完备度（表 A）** | Core ≈ 96%，总 ≈ 95% | 模块有无、pytest、non-CAD benchmark | `CORE_STATUS.md` |
| **任务清单执行（表 B）** | §3~§5 包完成比例 | 台账烟囱是否在推进 | 本节「三指令执行进度」 |
| **CAD 证明覆盖率** | **41.32%**（317 行；102 verified + 29 showcase） | 登记行 `verified`+`showcase` 比例 | `output/validation_runs/capability-lab/cad_capability_coverage.json` |
| **真实 CAD 实力（表 C 主指标）** | **9.15%**（`cad_strength_headline_percent`；showcase 门仍为主瓶颈） | 对外「能画多厉害」诚实上限 | 同上 JSON `cad_strength` |
| **CAD 实力指数（加权）** | **49.38%** | Ladder 加权 verified 占比 | `cad_strength_index_percent` |
| **场景片段实力（L3+）** | **40.91%**（36/88 行） | 微场景/片段级证明 | `scene_fragment_strength_percent` |
| **展示就绪度** | **9.15%**（29/317 showcase 行） | showcase 册是否就绪 | `showcase_readiness_percent` |
| **展示等级 Ladder** | 最高已证 **L4**（双工装项目切片 showcase） | 定性上限 | §3.2、`highest_proven_ladder_level` |

```text
工程完备度高  ≠  真实 CAD 实力（表 C）
RCAD 烟囱包完成  ≠  能画准施工图（多为矩形 smoke / 守卫链）
表 C 主指标 = min(实力指数, L3+片段, showcase)；showcase=0 时主指标为 0%，须同时报子指标
表 C 数字只取最新 `output/validation_runs/capability-lab/cad_capability_coverage.json`；Markdown 历史快照不得覆盖机器值
三指令执行进度  ≠  工程完备度 96%
```

**表 C 机器复跑：**

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_capability_coverage.py --output output\validation_runs\capability-lab\cad_capability_coverage.json
```

### 四条并行轨

| 轨 | 代号 | 当前 next |
| --- | --- | --- |
| 能力证明 | **V-PROOF** | `V-PROOF-43-COMPOSITION-CAD-RERUN` |
| 代码开发 | §4 | **已收口**（52/52）；next 见 PlanMD 后置 Backlog |
| CAD 执行 | **RCAD** | 见 §5（服务于 V-PROOF-1x） |
| 已完成路线 | A/B/C/D、LCAD-01~09 | — |

---

## 1. 文档关系

| 文档 | 职责 |
| --- | --- |
| `CORE_RESTRUCTURE_PLAN.md` | PlanMD；路线 E（CAD-MCP）+ 路线 F（能力证明） |
| **本文（任务清单）** | 全部任务包；§0 四口令 + 三板块台账进度 |
| `capability-proof-architecture.md` | Ladder、四层模型、claim_level 定义 |
| `CORE_CONTEXT_BRIEF.md` | 短上下文 + 三口径 |
| `CORE_STATUS.md` / `docs/status/current.md` | 证据；**CAD 证明覆盖率** |
| `docs/handoffs/current.md` / `docs/handoffs/package-index.md` | PlanMD 包交接与索引 |

---

## 2. 能力证明体系总览

```text
P0 契约门禁（pytest / validate）     ← 已有，不等于会画图
        ↓
P1 Capability Lab（登记表 + 矩阵）   ← Phase V 主轴（本文 §3）
        ↓
P2 Capability Ladder（展示册）       ← 回答「多厉害」（§3.2 + V-PROOF-6x）
        ↓
P3 项目回归 + 趋势 Dashboard          ← V-PROOF-7x
```

**路线 E / RCAD** = 在 P1 里**执行**真实 CAD 的命令清单（§5），完成后必须回写 §3 登记表 `claim_level`。

---

## 3. 能力证明轨（Phase V）

> 状态：`next` | `scheduled` | `blocked` | `user_gate`
> 完成任一包：更新 registry 行 → `cad_capability_coverage.json` → `CORE_STATUS.md` → CHANGELOG → **同步 §0 三指令执行进度**。

### 3.1 板块与任务包索引

| 板块 | 包 ID 段 | 目标 | 包数 |
| --- | --- | --- | ---: |
| **V0 登记与覆盖率** | `V-PROOF-00`~`05` | 机器可读能力表 + 覆盖率指标 | 6 |
| **V1 Intent / Primitive Lab** | `V-PROOF-10`~`19` | 每个 CAD_PLAN intent 有 case 或 deferred | 6 |
| **V2 Object / Catalog Lab** | `V-PROOF-20`~`29` | 对象 catalog → CAD 或 deferred | 6 |
| **V3 Symbol Lab** | `V-PROOF-30`~`39` | 6 archetype + 可读性 | 6 |
| **V4 Block / Composition Lab** | `V-PROOF-40`~`49` | 块矩阵 + 组合扩样 | 6 |
| **V5 Negative / Guard Lab** | `V-PROOF-50`~`59` | 负向 + 守卫真实 CAD | 4 |
| **V6 Showcase / Ladder** | `V-PROOF-60`~`69` | 展示册（回答「多厉害」） | 7 |
| **V7 项目回归 / 趋势** | `V-PROOF-70`~`79` | 多样本 + Dashboard | 4 |

### 3.2 Capability Ladder（展示等级）

| 等级 | 你要看到什么 | 当前仓库（2026-05-26） |
| --- | --- | --- |
| **L0** | 能生成 plan | 大部分 Core API |
| **L1** | 测试 DWG 上几何对 | primitive、fixture、smoke、部分 object |
| **L2** | 家具符号可读 | desk、chair glyph |
| **L3** | 场景一角 | 工装 3 object；composition 3 组 |
| **L4** | 脱敏项目切片 | 双样本 rollup |
| **L5** | 交付预备 | **未开始** |

### 3.3 任务包队列（按顺序）

#### 板块 V0 — 登记与覆盖率（必先做）

| 包 ID | 状态 | 要做什么 | 退出条件 | 产物 |
| --- | --- | --- | --- | --- |
| **`V-PROOF-00-REGISTRY-SCHEMA`** | **done** | `cad_capability_registry.schema.json` + invalid fixture | schema 单测 | `core/schemas/` |
| **`V-PROOF-01-REGISTRY-SEED`** | **done** | 从现有 intent/catalog/archetype **种子登记** 200+ 行（大量 `smoke`/`deferred`） | 首版 JSON | `examples/capability_proof/cad_capability_registry.json` |
| **`V-PROOF-02-COVERAGE-REPORT`** | **done** | `run_capability_coverage.py` 输出覆盖率 | `verified_count/total_count` 可复跑 | `output/validation_runs/capability-lab/cad_capability_coverage.json` |
| **`V-PROOF-03-REGISTRY-LOADER`** | **done** | loader + validate + 与 RCAD 结果回写 API | 单测 | `core/verification/capability_registry.py` |
| **`V-PROOF-04-STATUS-SYNC`** | **done** | `CORE_STATUS.md` 固定三口径；禁止单用 96% 暗示 CAD 已证 | 状态页模板 | 根 MD + `capability_proof_status_template.md` |
| **`V-PROOF-05-HANDOFF-TEMPLATE`** | **done** | handoff 增：registry 行 id、claim_level、Ladder | 模板 §9+3 项 | handoffs + `evidence_gate` §7 |

#### 板块 V1 — Intent / Primitive Lab

| 包 ID | 状态 | 要做什么 | 退出条件 | 关联 RCAD |
| --- | --- | --- | --- | --- |
| **`V-PROOF-10-INTENT-INVENTORY`** | **done** | 枚举 `CAD_PLAN` 全部 intent | 登记表 intent 段完整 | `intent_lab_manifest.json` |
| **`V-PROOF-11-INTENT-CAD-CASES`** | **done** | 每 intent 1 最小 plan + 真实 CAD 或 `deferred` | 无「未登记 intent」 | `examples/plans/intent_lab/` |
| `V-PROOF-12-PRIMITIVE-MANIFEST` | done | `primitive_matrix_cad_manifest` + `local_cad_regression` case | round2 `geometry_verified` | **RCAD-26** done |
| `V-PROOF-13-FIXTURE-EXPAND` | done | fixture 6 个 + suite `geometry_verified` | round2 6/6 CAD | **RCAD-07** done |
| `V-PROOF-14-DRAW-SYMBOL-GLYPH-ROW` | done | `intent_lab_cad` + `intent.draw_symbol_glyph` verified | per-intent CAD 报告 | RCAD-12~15 |
| `V-PROOF-15-INSERT-BLOCK-ROW` | done | `intent.insert_block_alpha` verified | intent_lab CAD | RCAD-04~05 |

#### 板块 V2 — Object / Catalog Lab

| 包 ID | 状态 | 要做什么 | 退出条件 | 关联 |
| --- | --- | --- | --- | --- |
| `V-PROOF-20-CATALOG-INVENTORY` | done | `commercial_fitout_catalog_manifest` 14 项对齐 object_catalog | inventory pass | C-CFIT-02 |
| `V-PROOF-21-OBJECT-CAD-SMOKE` | done | 8 类 `draw_object` CAD smoke + registry 回写 | `object_cad_smoke` geometry_verified | RCAD-17 扩 |
| `V-PROOF-22-DEMAND-CASE-ROWS` | done | demand 10 case CAD smoke + registry 回写 | 10/10 geometry_verified | RCAD-16 |
| `V-PROOF-23-OBJECT-DETAIL-ROWS` | **done** | table/desk/chair/bed/sofa component plan 登记 | 6 smoke rows + 5/5 no-CAD suite pass | `object_detail_registry.py`、`vproof_23_*` |
| `V-PROOF-24-OFFICE-OBJECT-ROWS` | **done** | office_alpha 6× object_spec registry smoke | 6/6 no-CAD；误绑 verified 已降为 smoke | `office_object_registry.py`、`vproof_24_*` |
| `V-PROOF-25-FITOUT-SUBSCENE-OBJECTS` | **done** | meeting/reception 代表对象 CAD smoke manifest + runner | fake 4/4 geometry_verified | RCAD-18~19 |

#### 板块 V3 — Symbol Lab

| 包 ID | 状态 | 要做什么 | 退出条件 | 关联 |
| --- | --- | --- | --- | --- |
| `V-PROOF-30-ARCHETYPE-ROWS` | done | 6 `symbol.archetype.*` 绑定 spec CAD 证据 | 6 行 verified | D-SYMBOL-03 |
| `V-PROOF-31-SYMBOL-SPEC-SEED` | done | monitor/rug/sofa symbol specs + glyph CAD | validate + smoke pass | RCAD-15 |
| `V-PROOF-32-GLYPH-CAD-MATRIX` | **done** | 6 archetype 各跑 glyph CAD | 6/6 `geometry_verified` | `capability-lab-cad-validation-20260527/symbol_glyph_matrix/` |
| `V-PROOF-33-READABILITY-REPORT-ROWS` | **done** | coverage readability report + 5 个 readability 状态进 registry | `output/validation_runs/vproof-33-readability-rows/capability_readability_report.json` + registry rows | D-SYMBOL-05 |
| `V-PROOF-34-BLOCK-FIRST-ROW` | **done** | block-first tier 登记 | suite + `controlled-block-wins` 已由 RCAD-25 回写 verified；fallback case 不升级 | `output/validation_runs/rcad-25-symbol-block-first-20260527-escalated/symbol_block_first_cad_smoke_report.json` |
| `V-PROOF-35-FALLBACK-TIER-ROWS` | **done** | 四级 fallback 各 claim 边界 | 5 registry rows + 无静默退化；不新增 geometry_verified | D-SYMBOL-07 |

#### 板块 V4 — Block / Composition Lab

| 包 ID | 状态 | 要做什么 | 退出条件 | 关联 |
| --- | --- | --- | --- | --- |
| `V-PROOF-40-BLOCK-MATRIX-PLAN` | **done** | 块：旋转 × scale × attribute 维度表 | 5 个 registry binding applied；矩阵 no-CAD pass；suite 保持 smoke，不新增几何 verified | `output/validation_runs/vproof-40-block-matrix-plan-no-cad/` |
| `V-PROOF-41-BLOCK-CAD-MATRIX` | **done** | 双受控测试块 CAD matrix 已在真实 AutoCAD 会话完成 created-handle 回读 | 2/2 块 verified；`block.library.controlled_test_block_002` 回写 verified | `output/validation_runs/vproof-41-block-cad-matrix-20260527-cad/block_alpha_beta_summary.json`；handles `61F`,`627` |
| `V-PROOF-42-COMPOSITION-EXPAND` | **done** | office 4 case 已在真实 AutoCAD 会话刷新 CAD + registry evidence；interior 已有 3 case | 4/4 `geometry_verified`，40 created handles，writeback applied 4 | `output/validation_runs/vproof-42-office-composition-expand-20260527-cad/composition_cad_registry_report.json` |
| `V-PROOF-43-COMPOSITION-CAD-RERUN` | **done** | interior 3 case CAD 刷新 + office 4 case 升 showcase | 7/7 writeback applied；composition 类 7 行 showcase；表 C 主指标 8.87%→10.28% | `vproof-43-composition-rerun-20260528-cad` + `vproof-tablec-office-composition-20260528-cad` |
| `V-PROOF-44-DRAWING-STANDARD-ROWS` | **done** | drawing_standard beta → registry | suite + `block_insert_plan_resolution` 已由 RCAD-23 回写 verified；style/profile case 不升级 | `output/validation_runs/rcad-23-drawing-standard-beta-20260527-escalated/drawing_standard_cad_smoke_report.json` |
| `V-PROOF-45-BLOCK-BETA-ROWS` | **done** | block_alpha_beta → registry | `block.insert_block_alpha.matrix` 升级 verified | `output/validation_runs/vproof-45-block-beta-rows/writeback_apply.json`；RCAD-24 8/8 readback |

#### 板块 V5 — Negative / Guard Lab

| 包 ID | 状态 | 要做什么 | 退出条件 | 关联 |
| --- | --- | --- | --- | --- |
| `V-PROOF-50-NEGATIVE-REGISTRY` | **done** | 负向 plan 清单进 registry | 8 类 `failure_category` + suite 共 9 行 smoke；9/9 writeback | `vproof-50-negative-registry-no-cad` |
| `V-PROOF-51-NEGATIVE-CAD` | **done** | 真实 CAD：无 handles、不保存 | `negative.cad_plan.real_cad_guard` smoke + RCAD-20 报告绑定 | `rcad-20-negative-cad-20260527-escalated` |
| `V-PROOF-52-GUARD-CAD` | **done** | snapshot/audit/guard strict 登记 | 4 行 smoke + RCAD-21 strict_gate pass；4/4 writeback | `rcad-21-guard-full-20260527` |
| `V-PROOF-53-HATCH-ROW` | **done** | hatch：受控 ANSI31 smoke verified | registry `primitive.hatch` verified + hatch smoke 报告 | RCAD-06 + LCAD-12 |

#### 板块 V6 — Showcase / Ladder（给你「看能力」）

| 包 ID | 状态 | 要做什么 | 退出条件 | 产物 |
| --- | --- | --- | --- | --- |
| `V-PROOF-60-SHOWCASE-INDEX` | **done** | `docs/verification/capability_showcase/README.md` + 索引 JSON | L0~L5 示例清单 | `showcase_index.json`（7 条 L2+L3）；L4 待 `V-PROOF-63` |
| `V-PROOF-61-L2-SYMBOL-GALLERY` | **done** | L2：desk/chair/table/sofa 真实 CAD + readback 索引 | 4/4 glyph `geometry_verified` + showcase | `showcase/L2/`；证据 `capability-proof-vproof61-20260527/` |
| `V-PROOF-62-L3-FITOUT-SNIPPET` | **done** | L3：工装微场景平面片段（非 3 矩形） | 1 微场景 showcase + 3 微场景真实 CAD 刷新 | `showcase/L3/fitout_open_office_desk_chair/`；证据 `capability-proof-vproof62-20260527/` |
| `V-PROOF-63-L4-PROJECT-SLICE` | **done** | L4：双样本 rollup 真实 CAD + showcase | meeting+reception 12 handles 各；rollup 4/4 | `capability-proof-vproof63-20260527/`；`showcase/L4/` |
| `V-PROOF-64-LADDER-BOUNDARY-DOC` | **done** | 全仓库「不能声称」与 Ladder 对照页 + block matrix showcase | 边界扫描 + 1 行 showcase 回写 | `docs/verification/capability_ladder_boundaries.md`；`output/validation_runs/vproof-64-ladder-boundary-doc/writeback_apply.json` |
| `V-PROOF-65-SHOWCASE-SECOND-WAVE` | **done** | hatch / block-first / drawing-standard 真实 CAD 证据补入 showcase | 4 行 showcase 回写 + coverage 主指标提升 | `docs/verification/capability_showcase/showcase/L1/primitive_hatch_smoke/`；`output/validation_runs/vproof-65-showcase-second-wave/writeback_apply.json` |
| `V-PROOF-66-PRIMITIVE-PROBE-SHOWCASE` | **done** | primitive probe 7 行 + drawing-standard suite 补入 showcase | 8 行 showcase 回写 + coverage 主指标提升 | `docs/verification/capability_showcase/showcase/L1/primitive_probe_matrix/`；`output/validation_runs/vproof-66-primitive-probe-showcase/writeback_apply.json` |

#### 板块 V7 — 项目回归 / 趋势

| 包 ID | 状态 | 要做什么 | 退出条件 | 关联 |
| --- | --- | --- | --- | --- |
| `V-PROOF-70-PROJECT-MANIFEST` | **done** | 可提交脱敏项目回归 manifest | schema + 4 submittable + 6 registry smoke；6/6 writeback | `vproof-70-project-manifest` |
| `V-PROOF-71-TREND-DASHBOARD` | **done** | 吸收 LCAD-11：evidence 趋势 + 覆盖率趋势 | dashboard schema + 3/3 panels + 4 registry smoke；4/4 writeback | `vproof-71-trend-dashboard` |
| `V-PROOF-72-NIGHTLY-LAB-ENTRY` | **done** | 文档化 nightly：`run_capability_lab --tier L1` | L1 6/6 pass + runbook + 2 registry smoke；2/2 writeback | `vproof-72-nightly-lab` |
| `V-PROOF-73-CROSS-MACHINE` | **done** | 换机 playbook + 覆盖率复算 | no-CAD 4/4 + baseline 复算；user_gate 三步 pending 文档化 | `vproof-73-cross-machine` |

### 3.4 覆盖率（V-PROOF-02，2026-05-27 更新）

机器报告：`output/validation_runs/capability-lab/cad_capability_coverage.json`（2026-05-27 本轮复跑；`scripts/run_capability_coverage.py` 可复跑）。可读报告历史入口：`output/validation_runs/vproof-33-readability-rows/capability_readability_report.json`。

| 指标 | 值 |
| --- | ---: |
| `total_count` | 282 |
| `verified_count` | **112** |
| `showcase_count` | **25** |
| `cad_proof_count` | **137** |
| `cad_proof_coverage_rate` | **48.58%** |
| 最近复跑 | `output/validation_runs/capability-lab/cad_capability_coverage.json`；新增 smoke/none 行会扩大分母，百分比可能下降 |

| 亮点（2026-05-27） | 状态 |
| --- | --- |
| `catalog.commercial_fitout.*`（14 行） | 全部 **verified**（`fitout_catalog_cad_smoke`） |
| `object.*.glyph`（6 行） | **verified**（symbol smoke 链） |
| `object.*.draw_object`（8 行） | **verified**（V-PROOF-21） |
| `symbol.archetype.*`（6 行） | **verified**（V-PROOF-30） |
| `symbol.block_first.*`（suite + controlled case） | **verified**（RCAD-25；fallback case 保持 smoke） |
| `drawing_standard.beta.*`（suite + block insert case） | **verified**（RCAD-23；style/profile case 保持 smoke） |

说明：未回写项仍含 `intent.draw_annotation` / `modify_object` / `delete_object`（none）、`object.sofa.glyph`（无 spec）。不得用工程完备度或 RCAD 烟囱通过数代替本表。

---

## 4. 代码轨

> 可无 AutoCAD。状态：`done` | `next` | `scheduled` | `blocked` | `user_gate`
> 用户说 **「一键推进」** 时：§4 **已收口（52/52）** → 默认转 §3 首行 `next` 或 `CORE_RESTRUCTURE_PLAN.md` 后置 Backlog；§4 未收口时只推进 **§4.1 首行 `next`**，不跳 §5。
> **包计数（2026-05-28 对账后）**：§4.0 **9** + §4.1 **15** + §4.2 **28** = **52** 执行包，**52/52 done**。`LCAD-10`/`LCAD-11` 父包 acceptance 为文档收口层，已含在 §4.1 的 `LCAD-10.5` / `LCAD-11.5`，**不重复计入 52**。原 §4.2 分母 **31** 含 **3** 个历史占位，已取消/合并（见下节）。

### 4.2 分母对账（2026-05-28）

早期 §0 曾写 **§4.2 波次 31 包**（合计 9+15+31=**55**），明细表仅 **28** 行可执行包。差额 **3** 个为波次规划预留槽，**无独立退出条件、无明细行**，现统一标为 **已取消/合并**，不再占 `next`：

| 历史占位 ID | 状态 | 合并 / 取消说明 |
| --- | --- | --- |
| `CFIT-06`~`CFIT-08`（P2 工装波次预留） | **cancelled** | 能力已并入 `CFIT-09`~`CFIT-13` 明细（5 包） |
| `SCENE-PROD-04`（P3 多场景预留） | **merged** | 并入 `REST-PROD-04` 与 `SCENE-PROD-05`/`06` |
| `RESIDENTIAL-P3-WAVE`（P3 住宅波次预留） | **merged** | 并入 `RESIDENTIAL-PROD-01`~`03` |

对账后：**§4.2 = 28 包（全部 done）**；§4 总包数 **52/52**，代码轨 **100% 收口**。旧口径 55/55 仅作历史快照，不再用于进度百分比。

### 4.0 已收口（主计划 done，不再占 next）

| 包 ID | 状态 | 摘要 |
| --- | --- | --- |
| `LCAD-01`~`09` | done | manifest、primitive、fixture、block 边界、项目样本、composition 等（证据见 `CORE_RESTRUCTURE_PLAN.md` 活跃队列 done 行） |

### 4.1 活跃队列（LCAD-10 / 11 + 门禁）

父包收口（文档层；已计入 §4.1 子包 `LCAD-10.5` / `LCAD-11.5`，**不重复计入 52 分母**）：

| 包 ID | 状态 | 要做什么 | 退出条件 | 产物 / 测试 | 证明 / RCAD |
| --- | --- | --- | --- | --- | --- |
| **`LCAD-10-NEGATIVE-SAFETY`** | **done** | 负向 CAD 安全父包（10.1~10.5） | `negative_cad_safety_acceptance.md` + `test_lcad_10_parent_rollup` pass | `docs/verification/negative_cad_safety_acceptance.md` | `V-PROOF-50`、`V-PROOF-51`、`RCAD-20` |
| **`LCAD-11-EVIDENCE-TREND-ROLLUP`** | **done** | evidence trend 父包（11.1~11.5） | `evidence_trend_acceptance.md` + `test_lcad_11_parent_rollup` pass | `docs/verification/evidence_trend_acceptance.md` | `V-PROOF-71`、`RCAD-27` |

### 4.1 活跃子包（LCAD-10 / 11 子包 + 门禁）

| 包 ID | 状态 | 要做什么 | 退出条件 | 产物 / 测试 | 证明 / RCAD |
| --- | --- | --- | --- | --- | --- |
| **`LCAD-10.1-NEG-FIXTURES`** | **done** | 负向 `CAD_PLAN` fixture + schema | invalid fixture 单测；validate 拒收 | `examples/plans/negative/`、`core/schemas/` | → `V-PROOF-50` |
| **`LCAD-10.2-WRITE-GUARD-NEG-RUNNER`** | **done** | 负向 plan 接 `write_guard` / preview-only 门禁 | `run_write_guard_cad_runner.py` pass | `write_guard_cad_runner.py` | → `V-PROOF-50` |
| **`LCAD-10.3-NEGATIVE-CAD-RUNNER`** | **done** | 真实 CAD 负向 suite CLI（无 handles、不保存） | 报告 `failure_category` 可断言；fake runner pass；real runner 在用户 CAD 会话通过 | `scripts/run_negative_cad_runner.py` | → `RCAD-20`、`V-PROOF-51` |
| **`LCAD-10.4-NEGATIVE-BOUNDARY-DOC`** | **done** | 负向与安全边界扫描文档 | `negative_cad_safety_boundaries.md` + focused 4 tests OK | `docs/verification/negative_cad_safety_boundaries.md` | `V-PROOF-50` |
| **`LCAD-10.5-PARENT-ROLLUP`** | **done** | 父包 `LCAD-10` 收口与 handoff | `negative_cad_safety_acceptance.md` + parent rollup test pass | `docs/verification/negative_cad_safety_acceptance.md` | — |
| **`LCAD-11.1-EVIDENCE-VOCAB`** | **done** | 趋势 JSON 字段与 evidence 词表对齐 | schema / 单测 | `core/verification/evidence_trend.py`、`core/schemas/evidence_trend.schema.json` | `V-PROOF-71` |
| **`LCAD-11.2-REGRESSION-TREND-JSON`** | **done** | `run_local_cad_regression` 输出历史 rollup | no-CAD 可复跑 JSON；trend schema pass | `output/validation_runs/lcad-11-2-regression-trend-json/evidence_trend/local_cad_regression_trend.json` | `V-PROOF-71` |
| **`LCAD-11.3-VALIDATION-TREND-INDEX`** | **done** | `run_cad_validation` 历次报告索引 | 机器可读索引；no-CAD 复跑 pass | `output/validation_runs/lcad-11-3-validation-trend-index/evidence_trend/cad_validation_trend_index.json` | `M-01` 辅助 |
| **`LCAD-11.4-COVERAGE-TREND-HOOK`** | **done** | 为 `cad_capability_coverage` 预留趋势槽位 | 与 V-PROOF-02 字段一致；schema pass | `output/validation_runs/lcad-11-4-coverage-trend-hook/evidence_trend/capability_coverage_trend.json` | `V-PROOF-02`、`71` |
| **`LCAD-11.5-TREND-BOUNDARY-DOC`** | **done** | 趋势报告「不能声称」说明 | 边界 MD + focused tests OK | `docs/verification/evidence_trend_boundaries.md` | — |
| **`CAD-VAL-01-BASELINE-GEOMETRY-GATE`** | **done** | 拆分 baseline：**几何** vs **环境/截图/单测** | strict 矩阵几何 pass 不拖死顶层 | `cad_validation_geometry_gate.py` | `RCAD-01`、`M-01` |
| **`CAD-VAL-02-ENVIRONMENT-GATE-OPTIONAL`** | **done** | Pillow / 截图 / unit_tests 改为可选或独立门禁 | `--environment-optional` + 环境边界文档 | `cad_validation_environment_gate.md`、runner 步骤分组 | — |
| **`LCAD-12-HATCH-COM`** | **done** | hatch COM 受控 smoke + fake structured deferred | real COM `draw_hatch` + `RCAD-06` 回读；fake 仍保留 deferred 边界 | `core/cad_io/autocad_com.py`、`core/verification/hatch_cad_smoke.py`、`hatch_com_deferred_boundary.md` | `V-PROOF-53` |
| **`LCAD-13-SESSION-SNAPSHOT-CAD`** | **done** | 真实 CAD 会话 before/after snapshot 断言 | capability probe 扩展；`session_guard` + `active_document_snapshot.json` | `cad_capability_probe.py`、`cad_session_guard.py`、`session_snapshot_capability_probe_boundary.md` | `V-PROOF-52` |
| **`LCAD-14-GUARD-FULL-CAD`** | **done** | LCAD-03 全链路 guard strict 子报告包装 | fake strict pass；`guard_full_cad_report.json` + 三段子报告 | `guard_full_cad_runner.py`、`guard_full_cad_boundary.md` | `RCAD-21`、`V-PROOF-52` |

### 4.2 P2 工装波次（CFIT-09 起）

| 包 ID | 状态 | 要做什么 | 退出条件 | 产物 / 测试 | 证明 / RCAD |
| --- | --- | --- | --- | --- | --- |
| **`CFIT-09-SECOND-PROJECT-SAMPLE`** | **done** | 第二组脱敏工装项目样本（会议室） | 协议扫描 pass；rollup manifest 登记；pre-confirmation pass | `projects/commercial_fitout_meeting_sample/`、`fitout_sample_specs.py` | `RCAD-10` |
| **`CFIT-10-RECEPTION-PROJECT-SAMPLE`** | **done** | 第三组脱敏样本（前台接待） | 协议扫描 pass；rollup 第四行；三子场景样本齐全 | `commercial_fitout_reception_sample/` | `RCAD-19` |
| **`CFIT-11-THREE-SAMPLE-BOUNDARY-SYNC`** | **done** | 工装三样本 product boundary / rollup 口径同步 | `assert_fitout_three_sample_rollup_sync` + boundary 文档 + focused 5 tests OK | `product_alpha_boundary.json`、`fitout_sample_specs.py`、`cfit_11_three_sample_product_boundary_sync.md` | V-PROOF-62 |
| **`CFIT-12-FITOUT-SUBSCENE-OBJECT-CAD-SMOKE`** | **done** | meeting/reception 代表对象 CAD smoke | manifest + runner；fake 2 子场景 4/4 geometry_verified | `fitout_subscene_object_cad_smoke.py`、`cfit_12_*_boundary.md` | V-PROOF-25 |
| **`CFIT-13-P2-WAVE-PARENT-ROLLUP`** | **done** | P2 工装波次父包收口 | `assert_commercial_fitout_p2_wave_contract` + acceptance MD + 6 tests OK | `commercial_fitout_p2_wave.py`、`commercial_fitout_p2_wave_acceptance.md` | — |

### 4.2 P4 Core 波次（DRAW-01 起）

| 包 ID | 状态 | 要做什么 | 退出条件 | 产物 / 测试 | 证明 / RCAD |
| --- | --- | --- | --- | --- | --- |
| **`DRAW-01-DRAWING-STANDARD-BOUNDARY`** | **done** | 把 `drawing_standard_profile` / beta suite 收成 P4 可审计边界 | `assert_drawing_standard_boundary_contract` + boundary MD + fake 6/6 pass | `drawing_standard_boundary.py`、`draw_01_drawing_standard_boundary.md` | `V-PROOF-44`、`RCAD-23` |
| **`DRAW-02-DRAWING-STANDARD-REGISTRY-ROWS`** | **done** | beta suite case → `cad_capability_registry` 行绑定 | 7 registry 行 + `apply_smoke_registry_evidence_writeback` + 8 tests OK | `drawing_standard_registry.py`、`draw_02_*` | `V-PROOF-44`（代码轨前置） |
| **`SYMBOL-08-GLYPH-FALLBACK-BOUNDARY`** | **done** | 四级 fallback tier 边界文档 + 契约 | `assert_symbol_glyph_fallback_boundary_contract` + boundary MD + 11 tests OK | `symbol_fallback_boundary.py`、`symbol_08_*` | `V-PROOF-35`（边界前置） |
| **`SYMBOL-09-BLOCK-FIRST-TIER`** | **done** | block-first tier 机器入口与 deferred 边界 | manifest + runner + 4 registry 行 + 7 tests OK | `block_first_tier.py`、`symbol_09_*` | `V-PROOF-34`（代码轨前置）、`RCAD-25` |
| **`CORE-P4-WAVE-PARENT-ROLLUP`** | **done** | P4 Core 波次父包收口 | `assert_p4_core_wave_contract` + acceptance MD + 6 tests OK | `p4_core_wave.py`、`p4_core_wave_acceptance.md` | — |

### 4.2 P5 图块波次（RBLOCK-03 起）

| 包 ID | 状态 | 要做什么 | 退出条件 | 产物 / 测试 | 证明 / RCAD |
| --- | --- | --- | --- | --- | --- |
| **`RBLOCK-03-BLOCK-ALPHA-BOUNDARY`** | **done** | 受控 block alpha / beta suite 收成 P5 边界 | `assert_block_alpha_boundary_contract` + MD + beta 8/8 | `block_alpha_boundary.py`、`rblock_03_*` | `V-PROOF-40` |
| **`RBLOCK-04-BLOCK-MATRIX-MANIFEST`** | **done** | anchor/rotation/scale/attribute 块矩阵 manifest | manifest + 契约 + 7 tests OK；no-CAD 8/8 case pass | `block_matrix_manifest.py`、`rblock_04_*`、`block_insert_matrix_manifest.json` | `V-PROOF-40`（代码轨前置） |
| **`RBLOCK-05-SECOND-CONTROLLED-BLOCK`** | **done** | 第二受控测试块 metadata | library + sidecar + manifest + 8 tests OK；V-PROOF-41 后 002 已进入受控 insert allowlist | `second_controlled_block_boundary.py`、`rblock_05_*` | `V-PROOF-41`（代码轨前置） |
| **`RBLOCK-06-BLOCK-ATTRIBUTE-BOUNDARY`** | **done** | 属性块探针边界 | manifest + 契约 + 7 tests OK；deferred 不误报 smoke | `block_attribute_boundary.py`、`rblock_06_*` | BETA-CAD-BLOCK-02 |
| **`RBLOCK-07-BLOCK-MATRIX-REGISTRY-ROWS`** | **done** | 块矩阵 → registry 行 | 5 行绑定 + writeback API + 8 tests OK | `block_matrix_registry.py`、`rblock_07_*` | `V-PROOF-40`（代码轨前置） |
| **`RBLOCK-08-P5-WAVE-PARENT-ROLLUP`** | **done** | P5 父包收口 | `assert_block_p5_wave_contract` + acceptance MD + 6 tests OK | `block_p5_wave.py`、`block_p5_wave_acceptance.md` | — |

### 4.2 P3 他场景产品化（OFFICE-PROD-01 起）

| 包 ID | 状态 | 要做什么 | 退出条件 | 产物 / 测试 | 证明 / RCAD |
| --- | --- | --- | --- | --- | --- |
| **`OFFICE-PROD-01-OFFICE-ALPHA-BOUNDARY`** | **done** | 办公 alpha benchmark + scene preferences 收成 P3 边界 | manifest + 契约 + 7 tests OK；benchmark 18/18 no-CAD | `office_alpha_boundary.py`、`office_prod_01_*` | `V-PROOF-24` |
| **`OFFICE-PROD-02-OFFICE-BETA-BOUNDARY`** | **done** | 办公 beta benchmark 边界 | manifest + 契约 + 6 tests OK；benchmark 9/9 no-CAD | `office_beta_boundary.py`、`office_prod_02_*` | `V-PROOF-24` |
| **`OFFICE-PROD-03-OFFICE-P3-WAVE-ROLLUP`** | **done** | 办公 P3 父包收口 | `assert_office_p3_wave_contract` + alpha 18/18 + beta 9/9 no-CAD | `office_p3_wave.py`、`office_prod_03_p3_wave_acceptance.md`、`test_office_prod_03_*` | `V-PROOF-24` |
| **`REST-PROD-01-RESTAURANT-ALPHA-BOUNDARY`** | **done** | 餐饮场景 alpha 进波首包 | contract + manifest + restaurant alpha no-CAD case pass | `restaurant_alpha_boundary.py`、`restaurant_prod_01_*` | `BETA-SCENE-03` |
| **`REST-PROD-02-RESTAURANT-BETA-BOUNDARY`** | **done** | 餐饮 beta benchmark 边界 | manifest + 契约 + 6 tests OK；benchmark 8/8 no-CAD | `restaurant_beta_boundary.py`、`restaurant_prod_02_*` | `BETA-SCENE-03` |
| **`REST-PROD-03-RESTAURANT-P3-WAVE-ROLLUP`** | **done** | 餐饮 P3 父包收口 | `assert_restaurant_p3_wave_contract` + alpha case + beta 8/8 no-CAD | `restaurant_p3_wave.py`、`restaurant_prod_03_p3_wave_acceptance.md`、`test_rest_prod_03_*` | `BETA-SCENE-03` |
| **`REST-PROD-04-MULTI-SCENE-P3-ROLLUP`** | **done** | P3 多场景父包收口 | office + restaurant P3 rollup 均可审计 | `multi_scene_p3_wave.py`、`rest_prod_04_multi_scene_p3_rollup_acceptance.md`、`test_rest_prod_04_*` | `V-PROOF-24` / `BETA-SCENE-03` |
| **`RESIDENTIAL-PROD-01-RESIDENTIAL-ALPHA-BOUNDARY`** | **done** | 住宅 alpha 进 P3 波首包 | manifest + 契约 + 7 tests OK；`scene_alpha_residential_blank_shell` no-CAD pass | `residential_alpha_boundary.py`、`residential_prod_01_*`、`test_res_prod_01_*` | `BETA-SCENE-02` |
| **`RESIDENTIAL-PROD-02-RESIDENTIAL-BETA-BOUNDARY`** | **done** | 住宅 beta benchmark 边界 | manifest + 契约 + 6 tests OK；beta 8/8 no-CAD（7 pass + 1 blocked） | `residential_beta_boundary.py`、`residential_prod_02_*`、`test_res_prod_02_*` | `BETA-SCENE-02` |
| **`RESIDENTIAL-PROD-03-RESIDENTIAL-P3-WAVE-ROLLUP`** | **done** | 住宅 P3 父包收口 | `assert_residential_p3_wave_contract` + alpha 1 + beta 8/8 no-CAD | `residential_p3_wave.py`、`residential_prod_03_*`、`test_res_prod_03_*` | `BETA-SCENE-02` |
| **`SCENE-PROD-05-SCENE-EXPLANATION-TEMPLATE`** | **done** | 场景解释模板收口，说明偏好如何影响候选 | docs scan + agent boundary tests | `scene_beta_explanation.py`、`scene_prod_05_scene_explanation_template.md`、`test_scene_prod_05_*` | `BETA-SCENE-04` |
| **`SCENE-PROD-06-MULTI-SCENE-REGRESSION-GATE`** | **done** | 多场景回归门禁和状态同步 | 25/25 selected scene beta benchmark pass；repo audit 0 findings；不新增 CAD 几何证明 | `scene_regression_gate.py`、`scene_prod_06_multi_scene_regression_gate.md`、`test_scene_prod_06_*` | `BETA-SCENE-05` |

| 波次 | 明细包（§4.2 对账后） | 包数 | 证明体系 |
| --- | --- | ---: | --- |
| P2 工装 | `CFIT-09` … `CFIT-13` | **5** | V-PROOF-62、25、20~21 |
| P3 他场景 | `OFFICE-PROD-01` … `SCENE-PROD-06`（含 `REST`/`RESIDENTIAL`） | **12** | V-PROOF-24、BETA-SCENE |
| P4 Core | `DRAW-01` … `SYMBOL-09` + `CORE-P4` | **5** | V1~V4 |
| P5 图块 | `RBLOCK-03` … `RBLOCK-08` | **6** | V-PROOF-40~41 |
| **§4.2 合计** | — | **28** | 原规划 31 含 3 历史占位（已取消/合并） |

---

## 5. CAD-MCP 轨（路线 E）

> **定位**：P1 Capability Lab 的**执行层**。跑完后必须回写 `cad_capability_registry.json` 对应行 `claim_level=verified`。

### 5.1 会话前置

```powershell
cd "C:\Users\User\Desktop\CAD-AGENT"
$env:PYTHONIOENCODING='utf-8'
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\self_check.py
& $py scripts\render_preview.py --check
```

### 5.2 RCAD 执行队列（逐项）

> **包计数：29**。用户说 **「CAD 补验」** 时推进表中第一个 `cad_status` 为 `stale` 或 `pending` 的行（须先 §5.1 E0）。
> 通过后：回写 `cad_capability_registry`（V0 建成后）+ 更新本表 `cad_status` + §0 进度。

```powershell
$root = "C:\Users\User\Desktop\CAD-AGENT"
$out  = "$root\output\validation_runs\capability-lab-<yyyyMMdd>"
$py   = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
cd $root
$env:PYTHONIOENCODING='utf-8'
```

| RCAD | 包 ID | cad_status | 依赖 | 命令（`$out` 替换实际目录） | V-PROOF |
| ---: | --- | --- | --- | --- | --- |
| 00 | `RCAD-00-SESSION-GATE` | verified | — | `& $py scripts\self_check.py`；`& $py scripts\render_preview.py --check` | — |
| 01 | `RCAD-01-BASELINE-GEOMETRY` | **verified** | `CAD-VAL-01` | `& $py scripts\run_cad_validation.py --geometry-gate --require-geometry-pass --output-dir $out\rcad-01-baseline-geometry`；证据 `output/validation_runs/rcad-01-baseline-geometry/report.json` | V1、M-01 |
| 02 | `RCAD-02-PRIMITIVE-MATRIX` | verified | — | `& $py scripts\run_primitive_matrix.py --output-dir $out\rcad-02-primitive` | V-PROOF-12 |
| 03 | `RCAD-03-MANIFEST-STRICT` | verified | — | `& $py scripts\run_local_cad_regression.py --strict --output-dir $out\rcad-03-strict` | V1、V7 |
| 04 | `RCAD-04-BLOCK-ALPHA` | verified | — | `& $py scripts\run_block_alpha_validation.py --output-dir $out\rcad-04-block` | V4、V-PROOF-15 |
| 05 | `RCAD-05-BLOCK-ATTRIBUTE` | verified | — | manifest strict 内 attribute case 或 `run_cad_capability_probe.py` | V4 |
| 06 | `RCAD-06-HATCH` | **verified** | `LCAD-12` + `V-PROOF-53` | 证据：`output/validation_runs/rcad-06-hatch-cad-20260527-escalated/hatch_cad_smoke_report.json`（handles `61C`,`61D`；`hatch`+`polyline` 回读；ANSI31；只证明受控 preview smoke） | V-PROOF-53 |
| 07 | `RCAD-07-FIXTURE-SUITE` | verified | — | `& $py scripts\run_cad_plan_fixture_suite.py --output-dir $out\rcad-07-fixture` | V-PROOF-13 |
| 08 | `RCAD-08-COMPLEX-SMOKE` | verified | — | `& $py scripts\run_complex_cad_smoke.py --output-dir $out\rcad-08-smoke` | V1 |
| 09 | `RCAD-09-PROJECT-ROLLUP` | verified | — | `& $py scripts\run_project_sample_cad_rollup.py --output-dir $out\rcad-09-project` | V7 |
| 10 | `RCAD-10-PROJECT-SECOND-SAMPLE` | **verified** | **`CFIT-09` done** | 证据：`output/validation_runs/rcad-10-project-rollup-20260527/`（4/4 `geometry_verified`） | V7、V6-63 |
| 11 | `RCAD-11-COMPOSITION-CAD` | verified | — | `& $py scripts\run_composition_cad_check.py`（manifest case） | V-PROOF-43 |
| 12 | `RCAD-12-SYMBOL-GLYPH-DESK` | verified | — | `& $py scripts\run_symbol_glyph_cad_smoke.py --output-dir $out\rcad-12-desk`（默认 desk spec） | V3 |
| 13 | `RCAD-13-SYMBOL-GLYPH-CHAIR` | verified | — | `& $py scripts\run_symbol_glyph_cad_smoke.py --symbol-spec examples\symbol_specs\seating_chair_plan.json --output-dir $out\rcad-13-chair` | V3 |
| 14 | `RCAD-14-SYMBOL-GLYPH-TABLE` | verified | `surface_table_plan.json` | round2 `rcad-14-table` 9 handles | V-PROOF-31 片段 |
| 15 | `RCAD-15-SYMBOL-GLYPH-SOFA` | **verified** | `V-PROOF-31` | 证据：`output/validation_runs/rcad-15-symbol-glyph-sofa-20260527/`（6 handles、`geometry_verified`；registry `object.sofa.glyph` + `symbol.spec.symbol_sofa_plan` 证据路径） | V3 |
| 16 | `RCAD-16-DEMAND-SIDE-CAD` | verified | — | demand-side 10 case 报告路径登记（`demand-side-agent-cad-real-20260526`） | V-PROOF-22 |
| 17 | `RCAD-17-CFIT-SMOKE-CLI` | verified | — | `& $py scripts\run_commercial_fitout_cad_smoke.py --output-dir $out\rcad-17-cfit` | V2、V6 |
| 18 | `RCAD-18-FITOUT-MEETING` | **verified** | **`CFIT-12` done** | 证据：`output/validation_runs/capability-proof-table-c-20260527/all_subscenes/`（meeting 2/2 `geometry_verified`；registry 回写 4 行） | V2、V6 |
| 19 | `RCAD-19-FITOUT-RECEPTION` | **verified** | **`CFIT-10` done** | 复用 `rcad-10-project-rollup-20260527` reception 子报告 | V2、V6 |
| 20 | `RCAD-20-NEGATIVE-CAD` | verified | **`LCAD-10.3` done；2026-05-27 用户 CAD 会话通过** | 证据：`output/validation_runs/rcad-20-negative-cad-20260527-escalated/negative_cad_runner_report.json`（`created_handles=[]`、不保存、不删除、不改正式层、entity delta=0） | V-PROOF-51 |
| 21 | `RCAD-21-GUARD-FULL-CAD` | **verified** | **`LCAD-14` done** | 证据：`output/validation_runs/rcad-21-guard-full-20260527/guard_full_cad_report.json`（`strict_gate=pass`） | V-PROOF-52 |
| 22 | `RCAD-22-CAPABILITY-PROBE-BETA` | **verified** | 2026-05-27 用户 CAD 会话通过 | `output/validation_runs/rcad-22-capability-probe-beta-20260527-escalated/cad_capability_probe.json`（11 handles；`status=cad_capability_verified`；hatch 仍 deferred） | V4 |
| 23 | `RCAD-23-DRAWING-STANDARD-BETA` | **verified** | `DRAW-02` | 证据：`output/validation_runs/rcad-23-drawing-standard-beta-20260527-escalated/drawing_standard_cad_smoke_report.json`（handle `36A`，styled `insert_block_alpha` → `block_reference` 回读；只升级 suite + block insert case） | V-PROOF-44 |
| 24 | `RCAD-24-BLOCK-ALPHA-BETA` | **verified** | `block-alpha-beta-01` | 证据：`output/validation_runs/rcad-24-block-beta-cad-after-rotfix-20260527/block_alpha_beta_summary.json`（8/8 `geometry_verified`；handles `373`~`37A`；修正旋转 block bbox 预期为 AutoCAD 实际旋转外包框；只证明 controlled block alpha beta suite） | V-PROOF-45 |
| 25 | `RCAD-25-SYMBOL-BLOCK-FIRST` | **verified** | `SYMBOL-09` | 证据：`output/validation_runs/rcad-25-symbol-block-first-20260527-escalated/symbol_block_first_cad_smoke_report.json`（handle `369`，`insert_block_alpha` → `block_reference` 回读；只升级 suite + controlled case） | V-PROOF-34 |
| 26 | `RCAD-26-PRIMITIVE-MANIFEST-CAD` | verified | manifest + regression case | round2 `primitive_matrix_cad` | V-PROOF-12 |
| 27 | `RCAD-27-TREND-ROLLUP-CAD` | **verified** | **`LCAD-11.2`** | 证据：`output/validation_runs/rcad-27-trend-rollup-cad-20260527-escalated/local_cad_regression_report.json`（strict pass；9/9 `geometry_verified_case_count`；105 handles；趋势：`evidence_trend/local_cad_regression_trend.json`） | V-PROOF-71 |
| 28 | `RCAD-28-BETA-EVIDENCE-ROLLUP` | **verified** | — | 证据：`output/validation_runs/rcad-28-beta-evidence-rollup-20260527-final/cad_beta_evidence_rollup.json` + `evidence_trend/cad_beta_evidence_rollup_trend.json`；5/5 subpackages pass，`non_cad_only=true`，`geometry_verified_count=0`，不提升表 C | V7 |

**历史证据**：`output/validation_runs/rcad补验-20260526/rcad_verify_summary.json`

### 5.3 RCAD → V-PROOF 域映射（索引）

| 域 | RCAD 编号 |
| --- | --- |
| regression / intent | 01~03、07~08、26 |
| block | 04~05、24~25 |
| hatch | 06 |
| project | 09~10 |
| composition | 11 |
| symbol | 12~15、25 |
| object / demand | 16~19 |
| negative / guard | 20~21 |
| beta / trend | 22~28 |

---

## 6. 未校验项

| ID | 问题 | 证明体系 |
| --- | --- | --- |
| M-01 | baseline 整包非几何 fail | CAD-VAL + V-PROOF-71 |
| M-02 | hatch 受控 smoke 已 verified；任意 hatch / 正式层仍不声称 | V-PROOF-53 |
| M-03 | 历史实体 | V-PROOF-52 |
| M-04 | CFIT JSON | **已补验**；registry 待 V-PROOF-20 回写 |
| M-06 | 历史缺口：无能力登记表 | **已补齐**；当前 262 行，`V-PROOF-33` readability rows 已绑定 |

---

## 7. 证据索引

| 类型 | 路径 |
| --- | --- |
| 会话补验汇总 | `output/validation_runs/rcad补验-20260526/rcad_verify_summary.json` |
| strict 矩阵 | `output/validation_runs/rcad补验-20260526-strict/` |
| 最新覆盖率 | `output/validation_runs/neg-cad-proof-sync/cad_capability_coverage-final.json` |
| 最新可读覆盖率报告 | `output/validation_runs/neg-cad-proof-sync/capability-readability-final/capability_readability_report.json` |
| 登记表 schema + 最小样例 | `core/schemas/cad_capability_registry.schema.json`、`examples/capability_proof/minimal_cad_capability_registry.json` |
| 登记表当前基线（262 行） | `examples/capability_proof/cad_capability_registry.json`（`scripts/build_cad_capability_registry_seed.py` 可复生成种子；后续 writeback 增量更新） |
| 覆盖率（V-PROOF-02 历史首算） | `output/validation_runs/capability-lab/cad_capability_coverage.json` |

---

## 8. 不能声称

- **工程完备度 96%** ≠ 已证明能画准 / 能画复杂图块。
- 未在 registry 中 `verified` 的能力，不得对外声称 CAD 已通过。
- L5 交付、公司块库、任意 DWG、hatch 全面准确 — 均未开始或未 verified；当前 hatch 仅为受控 ANSI31 preview smoke。
- Showcase 截图 ≠ 几何证据（须 readback 报告路径）。

---

## 9. 执行协议

1. 读 `AGENTS.md`、`CORE_CONTEXT_BRIEF.md`、本文对应轨、`CORE_RESTRUCTURE_PLAN.md`。
2. **只推进 1 包**；CAD 包：E0 + readback + **回写 registry**。
3. 完成：更新状态 → **§0 三指令执行进度** → 主计划 → `CORE_STATUS.md` → CHANGELOG → handoff。
4. 新能力：先 **V-PROOF-01 登记**，再开发或 RCAD，禁止「只写代码不登记」。

### 主计划映射

| 主计划 | 本文 |
| --- | --- |
| 路线 F 能力证明 | §3 全表 |
| 路线 E CAD-MCP | §5 RCAD |
| LCAD-10/11 | §4 + §3 V5/V7 |
| 后置 Backlog | §4.2 + §3 各板块 |
