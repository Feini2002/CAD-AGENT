# 全局 Agent 流水线架构

最后更新：2026-05-28

## 目标

把训练期「一个交互式 Agent 会话分步扮演三角」升级为 **可拆可合的多 Agent CAD 系统**：

- **全局 Agent**：白话 → 意图 → 落图 → 审计 → 修复 → 交付（任何场景共用）
- **场景 Agent**：只提供词汇、偏好、workflow 名（`agents/residential/` 等）
- **常识底座**：提供基础对象、图库来源、可执行审计和证据边界（见 `cad-common-sense-upgrade.md`）
- **资产检索层**：在 `CAD_PLAN` 前产出 `retrieval_pack`，区分受控 block、对象族、符号语法、历史失败和证据边界（见 `docs/architecture/cad-asset-intelligence-architecture.md`）
- **Core**：算法、COM、审计探针、截图（`core/`）

训练案例的价值 = **喂全局规则**（探针晋升、链路教训），不是堆案例私有脚本。

**North star：** 多 Agent 可以越来越聪明、链路越来越长，但 **一切必须精准**——不准则不能用。见 [`precision-first.md`](precision-first.md)。

---

## 默认流程（参照款）

```text
截图 + 用户标注
  → Context / Retrieve：查对象常识、catalog、自产资产、历史失败、已知证据边界
  → Route：exact_reuse / parametric_variant / semantic_redraw / novel_with_constraints / deferred
  → Intent：visual_style_brief（部件 + 取整尺寸 target_width_mm）
  → Execute：按 brief 闭合落图（不 chase 1866.7）
  → 截图
  → Audit：先 Visual agent_review，再机器（尺寸 fail 且 visual 绿 → approximate_ok）
  → Repair：只修视觉/断线/缺件，不为 R±2mm 或宽±10mm 单独 Repair
  → Delivery
```

**尺寸政策：** 见 [`vision-first-style.md`](vision-first-style.md) — 视觉 > 取整近似 > probe 精确。

---

## 分层（谁干什么）

```text
                    ┌─────────────────────────┐
                    │  Orchestrator（编排）    │
                    │  读 case manifest       │
                    │  调度下游 · 禁止亲自落图 │
                    └───────────┬─────────────┘
                                │
     ┌──────────────────────────┼──────────────────────────┐
     ▼                          ▼                          ▼
┌─────────────┐          ┌─────────────┐          ┌─────────────┐
│ Intent      │          │ Execute     │          │ Audit       │
│ 需求拆分     │ ───────► │ 落预览       │ ───────► │ 机器+目视门槛 │
│ intent.json │          │ CODEX_PREVIEW│          │ geometry_audit│
└─────────────┘          └──────┬──────┘          └──────┬──────┘
                                │                        │
                                │         audit_fail       │
                                ▼                        ▼
                         ┌─────────────┐          ┌─────────────┐
                         │ Repair      │◄─────────│ 诊断回环     │
                         │ 最小修复     │          │ TRAINING_ERR │
                         └──────┬──────┘          └─────────────┘
                                │ audit_pass + agent_review OK
                                ▼
                         ┌─────────────┐
                         │ Delivery    │
                         │ 截图+汇报    │ ──► 用户 feedback
                         └─────────────┘

          ═══════════════════════════════════════════
          Scene Plugin（residential / office / …）
          rules.md · preferences.json · 只影响 Intent 词汇与 checklist 默认值
          ═══════════════════════════════════════════
```

| 层 | 目录 | 能否写 Python | 能否碰 CAD |
| --- | --- | --- | --- |
| 全局 Agent 定义 | `agents/pipeline/` | **否**（仅 JSON/MD） | 仅通过 Core API |
| 场景 Agent | `agents/<scene>/` | **否** | 同上 |
| Core 底座 | `core/` | **是** | **是** |
| 案例 | `projects/<case>/` | runs 脚本可 | 仅 PREVIEW |

---

## 全局 Agent 注册

见 `agents/pipeline/pipeline_manifest.json` 与各子目录 `agent.json`。

| agent_id | 角色 | 输入 | 输出 | 调用的 Core |
| --- | --- | --- | --- | --- |
| `pipeline_orchestrator` | 编排 | brief、case 状态 | 下一步指令、轮次计划 | — |
| `pipeline_asset_retriever` | 资产检索 / raw intake | brief、附件、标准图库文件夹、已有常识、catalog、case 历史 | `retrieval_pack`；或 standard library intake：扫描摘要、`reference_only` manifest、`agent_inferred` 标注、not_checked | `core.assets.build_retrieval_pack` / `core.assets.build_raw_reference_intake` |
| `pipeline_context_curator` | 上下文收束 | brief、附件、标准图库文件夹、已有常识、case 历史 | 本轮相关对象常识、风险边界、需打开的证据；识别 standard_library_intake 时只提取 folder + rough note，不要求用户补表格 | — |
| `pipeline_intent` | 需求拆分 | 白话、场景 rules、**参考截图** | `roundN_intent.json`、**`roundN_visual_style_brief.md`**、checklist | `plan_engine` validate |
| `pipeline_execute` | 落图 | intent、CAD_PLAN / case_script | `execution_summary` | `execution`、`cad_io` |
| `pipeline_audit` | 审计 | checklist、预览、**截图** | `geometry_audit.json`、**`agent_review.json`** | `training_geometry_audit` |
| `pipeline_repair` | 修复 | audit_failures、feedback | 修复计划、改 intent/checklist/runs | 同 Execute |
| `pipeline_delivery` | 交付 | 过审证据 | preview.png、`audit_review.md`、进度汇报 | `render_preview` |

**硬边界（所有全局 Agent 共用）：**

1. Execute / Repair 不得改正式图层、不得 save DWG
2. Audit 不得为过关画假几何
3. Delivery 不得在 `audit_pass: false` 时请你验收
4. Orchestrator 不得跳过 Intent 直接落图
5. reference-match 家具必须显式写 `visual_semantics`；沙发平面图至少要判断硬靠背、软靠垫、坐垫的前后层级，不能把方向画反。
6. Execute 生成相邻部件时要去重共享边；“靠在一起”是对的，重复画同一段导致亮线/白线是错的。
7. Delivery 必须用低噪声反馈模板说明：本轮结论、证据证明了什么、还没证明什么、请用户重点看哪里；不得只堆 handles / gap / overlap 数字。
8. 资产检索命中不等于能力通过；`retrieval_pack` 只能作为上游契约，仍必须进入 visual_parts / SYMBOL_SPEC / CAD_PLAN / audit。
9. 图库无强命中时进入探索模式，输出候选和 `visual_review_required`；不得静默画空 bbox 冒充对象。

---

## 与现有训练链路的关系

| 现在（Phase A） | 将来（Phase B+） |
| --- | --- |
| 一个交互式 Agent 会话按 README 分步（Codex、Cursor 或同类工具均可） | 同一套产物，多 Agent 各读各的 `agent.json` |
| 三角：需求 / 落图 / 审计 | 六角：+ 编排 / 修复 / 交付 |
| `training_geometry_audit.py` 已 global | Audit Agent 只调这一入口 |
| 场景 paused，家装 primary | Scene 以 plugin 挂载到 Intent |

**Phase A（当前）：** 文档 + `agents/pipeline/*.json` 注册表；仍是一个会话分角色。
**Phase B：** 每个全局 Agent 独立 agent rule / skill / 配置，Orchestrator 派 Task；具体载体可用 Codex、Cursor 或其它 agent 工具。
**Phase C：** SDK / 自动化编排，轮次状态机写进 `projects/<case>/runs/state.json`。

---

## 案例 → 全局 晋升（Agent 也要遵守）

| 发现 | 写哪里 | 不写什么 |
| --- | --- | --- |
| 新反模式（schematic 网格） | Core 探针 + Audit Agent 说明 | 新 case 私有 audit.py |
| 新工序（必须先 intent） | `pipeline_manifest` + README | 沙发专用 orchestrator |
| 基础对象常识 | `libraries/objects/` / `libraries/knowledge/` + 可执行检查 | 单个案例反馈流水账 |
| 场景词汇 | `agents/residential/rules.md` | Core |
| 数值门槛 | `audit_checklist.json` | Core 硬编码 |

---

## 怎么算「切切实实多 Agent 系统」

最低可演示标准（建议作为 Phase B 出口）：

1. 用户白话进 **Intent Agent** → 产出 `intent.json`
2. **Execute Agent** 只读 intent → 预览层落图
3. **Audit Agent** 只读 checklist + Core 引擎 → 红灯 exit 1
4. **Repair Agent** 读 failures → 最小 diff 再跑 2→3
5. **Delivery Agent** 截图 + 精简汇报 → 请你 feedback
6. **Orchestrator** 串联轮次，案例 `feedback.md` done 才停

这与 Core Lab（表 C / V-PROOF）**并行**：训练 pass = 你的 feedback；Lab pass = registry verified。

---

## 相关文件

- 审计引擎：`core/verification/training_geometry_audit.py`
- 审计架构：`docs/training/audit-architecture.md`
- 训练主链路：`docs/training/README.md`
- 常识底座升级：`docs/training/cad-common-sense-upgrade.md`
- 资产智能架构：`docs/architecture/cad-asset-intelligence-architecture.md`
- 全局 Agent 清单：`agents/pipeline/pipeline_manifest.json`
