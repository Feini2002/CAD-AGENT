# Visual-First Agent 架构计划

最后更新：2026-05-28
状态：**待执行**（用户确认后按 Phase 开工）
关联案例：`projects/residential_sofa_2seat_20260528`
关联训练文档：[`vision-first-style.md`](vision-first-style.md)

---

## 0. 背景与问题陈述

### 0.1 本案教训（round1–11）

| 现象 | 根因 |
| --- | --- |
| 机器 audit 绿、用户仍 fail | 「同款」被降维成 probe 数字（宽 1866.7、seat_split 0.821），未做视觉语义 |
| 反复画成全封闭盒 / 分区工程图 | Execute 默认 `_outer_shell` + split 线，而非部件图标 |
| 无靠垫、座不凸出、断线多 | 常识部件激活晚；line+arc 碎拼，非「每部件一条闭合线」 |
| Agent 自审与用户判断偏差大 | Visual 非主门；缺 `style_target` 金标准；自审标准过松 |

### 0.2 用户金标准

用户用生图 AI 产出 **2 座 plan 图标**（部件清晰、闭合、像常规家具示意图），并明确：

> 系统 Agent 在懂 brief 后，**应自己想到**的就是这种图——而非参数盒或供应商碎线 clone。

金标准文件（执行 Phase A 时入库）：

- 源图：对话附件 → 存为 `projects/residential_sofa_2seat_20260528/expected/style_target_2seat.png`

### 0.3 与现有主计划关系

- 本仓库主 PlanMD 仍是 [`../../CORE_RESTRUCTURE_PLAN.md`](../../CORE_RESTRUCTURE_PLAN.md)（Core Lab / 表 C / V-PROOF）。
- **本文件**是训练期 **Visual-First 多 Agent 流水线**专项计划，不替代主计划；完成后将规则晋升 `core/` + `agents/pipeline/` + `docs/training/`。

---

## 1. North Star（北极星）

> **「同款」= 同一套部件图标语言（形状 + 层级 + 闭合），不是同一套 probe 数字。**

### 1.1 精度优先级（强制）

```text
1. 视觉同款（对照 style_target + 参考截图）
2. 常识部件齐全（沙发 = 扶手 + 座垫 + 靠垫 + 底栏…）
3. 每部件闭合、少断线
4. 尺寸取整近似（如 1870，不 chase 1866.7）
5. probe / 参考块精确比例（仅辅助）
```

### 1.2 「同款」操作定义

从 **3 座参考** 推 **2 座** 时，Agent 应默认：

| 部件 | 形状词汇 | 数量 |
| --- | --- | --- |
| 扶手 | `rounded_rect` 竖条 | 2 |
| 座垫 | `pill_horizontal`（宽 > 高） | 2 |
| 靠垫 | `rounded_rect_tall`（高 > 宽） | 2 |
| 前底栏 | `rounded_rect_wide` 整宽条 | 1 |
| （可选）后顶栏 | 细横线或窄条 | 0～1 |

**禁止：** 整圈 `closed_outer_shell`、用 split 线代替靠垫/靠背、框内细线冒充靠垫。

---

## 2. 目标架构

### 2.1 流水线（新）

```text
用户白话 + 参考 CAD 截图 + style_target
        │
        ▼
┌───────────────────────┐
│ pipeline_visual_intent │  ← 新增（Phase A 可先合并进 Intent 子阶段）
│ 产出 visual_parts.json │
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│ pipeline_intent        │  数值意图（取整尺寸、checklist 草案）
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│ pipeline_execute       │  PartRenderer：只画 parts[] 闭合形
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│ pipeline_audit         │  A. Visual Audit（主门）→ B. Machine（辅门）
└───────────┬───────────┘
            │ visual fail
            ▼
┌───────────────────────┐
│ pipeline_repair        │  按 style_target 对症，禁止 size-only repair
└───────────┬───────────┘
            │ visual pass
            ▼
┌───────────────────────┐
│ pipeline_delivery      │  三图并排 + 部件对照表
└───────────────────────┘
```

### 2.2 新增强制产物（契约）

| 产物 | 路径 | 生产者 | 消费者 |
| --- | --- | --- | --- |
| 金标准图 | `projects/<case>/expected/style_target_*.png` | 用户 / 生图 | Visual Intent、Audit、Delivery |
| 部件 JSON | `projects/<case>/runs/roundN_visual_parts.json` | Visual Intent | Execute、Audit |
| 视觉摘要 | `projects/<case>/runs/roundN_visual_style_brief.md` | Visual Intent | 人读、Repair |
| 三图对照 | `projects/<case>/runs/roundN_style_compare.md` | Audit | Delivery、用户 |
| Agent 视觉门 | `projects/<case>/runs/roundN_agent_review.json` | Audit | Delivery |

**硬门槛：** 参照款任务 **无 `visual_parts.json` → 禁止 Execute**。

---

## 3. `visual_parts.json` Schema（v1）

存放：`core/schemas/visual_parts.schema.json`（Phase B 注册）；案例先用手写 JSON。

```json
{
  "schema_version": 1,
  "object": "sofa_plan",
  "seat_count": 2,
  "parts": [
    { "id": "arm_left",  "shape": "rounded_rect",       "role": "arm" },
    { "id": "arm_right", "shape": "rounded_rect",       "role": "arm" },
    { "id": "seat_left", "shape": "pill_horizontal",    "role": "seat_cushion" },
    { "id": "seat_right","shape": "pill_horizontal",    "role": "seat_cushion" },
    { "id": "back_left", "shape": "rounded_rect_tall",  "role": "back_cushion" },
    { "id": "back_right","shape": "rounded_rect_tall",  "role": "back_cushion" },
    { "id": "base_rail", "shape": "rounded_rect_wide",  "role": "front_rail" }
  ],
  "layout": {
    "assembly": "open",
    "seat_protrude_past_arm_mm": 30,
    "symmetry": "vertical_axis"
  },
  "forbidden": [
    "closed_outer_shell",
    "split_line_as_main_structure",
    "fake_back_cushion_as_inner_line"
  ],
  "sizing": {
    "target_width_mm": 1870,
    "gap_from_reference_mm": 400,
    "height_mm": 960,
    "round_to_mm": 10,
    "fillet_mm_approx": 30
  }
}
```

### 3.1 Shape 词汇表（全局）

| shape | 含义 | CAD 画法 |
| --- | --- | --- |
| `rounded_rect` | 圆角矩形 | 四边 + 四角弧，**一条闭合** |
| `pill_horizontal` | 横向 pill | 宽 > 高，闭合 |
| `rounded_rect_tall` | 高扁圆角块 | 靠垫默认 |
| `rounded_rect_wide` | 整宽底栏 | 连左右扶手区 |

Execute **不得**绘制不在 `parts[]` 中的结构（如整宽 split、无 id 的中缝——中缝若需要，必须写入 parts 且 optional）。

---

## 4. Agent 职责变更清单

### 4.1 `pipeline_orchestrator`

- [ ] `default_flow` 首步增加 visual intent 检查（或合并 gate）
- [ ] 无 `style_target` + 用户说「参照同款」→ 停在 Intent，提示补金标准
- [ ] Repair 循环分类：`visual | structure | cleanliness | size`；**禁止** 仅 `size` 循环
- [ ] 更新 [`agents/pipeline/orchestrator/agent.json`](../../agents/pipeline/orchestrator/agent.json)

### 4.2 `pipeline_visual_intent`（新增或 Intent 子阶段）

- [ ] 读：参考截图、style_target、用户白话、scene rules
- [ ] 写：`visual_parts.json`、`visual_style_brief.md`
- [ ] 内置常识本体（沙发部件 default）
- [ ] 新增 [`agents/pipeline/visual_intent/agent.json`](../../agents/pipeline/visual_intent/agent.json)（或扩展 intent）
- [ ] 注册到 [`agents/pipeline/pipeline_manifest.json`](../../agents/pipeline/pipeline_manifest.json)

### 4.3 `pipeline_intent`

- [ ] 数值意图与 visual 分离：`target_width_mm` 取整写入 intent
- [ ] **禁止** 从 probe 导出 sub-mm 造型参数
- [ ] 已部分完成，见 [`agents/pipeline/intent/agent.json`](../../agents/pipeline/intent/agent.json)

### 4.4 `pipeline_execute`

- [ ] 输入优先级：`visual_parts.json` > brief > intent
- [ ] 实现 **PartRenderer**（Core 或 case runs，Phase A 可先 case）
- [ ] `read_block_layout_profile` **仅**用于总尺 scale，不驱动圆角/座背形状
- [ ] 禁止 `_outer_shell` 整圈外框（除非 brief 明确）
- [ ] 更新 [`agents/pipeline/execute/agent.json`](../../agents/pipeline/execute/agent.json)

### 4.5 `pipeline_audit`

- [ ] **顺序：** Visual Audit → Machine Audit
- [ ] Visual：对照 style_target + 参考，填 `agent_review_required`
- [ ] Machine：cleanliness + forbidden；`reference_profile_match` 降为 warning
- [ ] `visual_pass` + 仅尺寸 fail → `approximate_ok`，不阻塞 Delivery
- [ ] 更新 [`agents/pipeline/audit/agent.json`](../../agents/pipeline/audit/agent.json)

### 4.6 `pipeline_repair`

- [ ] 修复优先级：缺件 / 全封闭 / shape 错 > 断线 > layout > 尺寸
- [ ] 输出必须引用 style_target 哪一项不像
- [ ] 禁止为 machine pass 收紧 checklist 或加 split 线
- [ ] 已部分完成，见 [`agents/pipeline/repair/agent.json`](../../agents/pipeline/repair/agent.json)

### 4.7 `pipeline_delivery`

- [ ] 默认三图并排：左参考 / 右预览 / style_target
- [ ] 汇报先 **部件对照表**（7 行），再尺寸
- [ ] 前置条件：`agent_review_all_pass`（非仅 `audit_pass`）
- [ ] 更新 [`agents/pipeline/delivery/agent.json`](../../agents/pipeline/delivery/agent.json)

---

## 5. Core 变更清单

| 项 | 路径 | 内容 |
| --- | --- | --- |
| 闭合图元 | `core/drawing/part_primitives.py`（新建） | `draw_rounded_rect_closed`, `draw_pill_horizontal_closed` |
| 外框探针 | `core/verification/training_geometry_audit.py` | `forbidden_closed_outer_shell`（需 closed shell 才判 schematic） |
| 修复误报 | 同上 | `schematic_equal_grid` 加前提，避免误伤多圆角部件 |
| Schema | `core/schemas/visual_parts.schema.json` | 校验 parts JSON |
| 注册 | `core/schemas/registry.py` | 注册 visual_parts |
| 三图对照 | `core/verification/style_compare.py`（新建） | 生成 `style_compare.md` 模板 |

**原则：** 数值门槛（1867、0.821）留 checklist；**造型反模式**晋升 Core。

---

## 6. Scene Plugin（residential）

更新 [`agents/residential/rules.md`](../../agents/residential/rules.md)：

- 参照款沙发 plan 默认部件表与 shape 词汇
- 禁止 closed_outer_shell
- 尺寸取整、视觉优先声明

---

## 7. 分阶段执行计划

### Phase A — 本案验证（优先，用户说「执行」后开工）

**目标：** round12 预览 ≈ `style_target_2seat.png`，用户目视 pass。

| # | 任务 | 产出 |
| --- | --- | --- |
| A1 | 金标准入库 | `expected/style_target_2seat.png` |
| A2 | 写部件 JSON | `runs/round12_visual_parts.json` |
| A3 | PartRenderer 落图 | 重写 `semantic_draw_helpers.py` 或新 `part_renderer.py` |
| A4 | round12 脚本 | `semantic_clean_two_seater.py` → round12 |
| A5 | Visual Audit 填表 | `round12_agent_review.json` + `round12_style_compare.md` |
| A6 | 三图截图 | `round12_preview.png` + compare 文档 |
| A7 | 用户 feedback | 更新 `feedback.md` |

**出口标准：**

- [ ] 7/7 部件与 style_target 一致（用户 pass）
- [ ] 无 closed_outer_shell
- [ ] open_endpoint ≤ checklist 上限
- [ ] 未 save DWG，仅 CODEX_PREVIEW

**不做的：** 不 clone 参考块碎线；不为 audit 加 split 主结构。

---

### Phase B — 晋升全局（本案 pass 后）

| # | 任务 |
| --- | --- |
| B1 | `visual_parts.schema.json` + registry |
| B2 | Core `part_primitives.py` + `forbidden_closed_outer_shell` |
| B3 | 修复 `schematic_equal_grid` 逻辑 |
| B4 | 新增 `pipeline_visual_intent` agent.json + manifest 注册 |
| B5 | 更新 `docs/training/pipeline-changelog.md` |
| B6 | 模板：`projects/residential_training_template/expected/style_target.template.png` + visual_parts 样例 |

---

### Phase C — 自动化与第二案例（可选）

| # | 任务 |
| --- | --- |
| C1 | `projects/<case>/runs/state.json` 状态机 |
| C2 | Visual Intent 独立 Cursor Skill / Rule |
| C3 | 第二家具案例验证 taxonomy 可迁移（如单椅） |
| C4 | 评估是否 SDK 编排（`pipeline_manifest` Phase C） |

---

## 8. 禁止反模式（pipeline 级）

写入 [`agents/pipeline/pipeline_manifest.json`](../../agents/pipeline/pipeline_manifest.json) `forbidden_patterns`：

| ID | 说明 |
| --- | --- |
| `probe_drives_styling` | 用 read_block_layout_profile 驱动圆角/座背形状 |
| `machine_green_delivery` | audit_pass 即交付，无 visual gate |
| `style_match_without_target` | 无 style_target 做「参照同款」 |
| `split_as_backrest` | split 线代替靠垫/靠背语义 |
| `clone_reference_fragments` | clone 343 段碎线 |
| `size_only_repair_loop` | visual fail 时只调毫米 |

---

## 9. 验收与进度口径

### 9.1 本案 done 条件

- 用户 `feedback.md` §几何 **pass**
- `roundN_style_compare.md` 部件 7/7 绿
- 非仅机器 audit 绿

### 9.2 与表 A/B/C 关系

本计划属 **训练期 / Agent 流水线**，**不**直接改表 C registry。训练 pass 后，将 `forbidden_closed_outer_shell` 等探针并入 V-PROOF 时再走 [`CORE_RESTRUCTURE_PLAN.md`](../../CORE_RESTRUCTURE_PLAN.md) 能力证明包。

### 9.3 执行后文档同步

完成 Phase A 或 B 后更新：

- `docs/status/changelog.md`
- `docs/handoffs/current.md`（若整包交付）
- `projects/residential_sofa_2seat_20260528/feedback.md`

---

## 10. 执行口令（给用户）

| 用户说 | Agent 动作 |
| --- | --- |
| **执行 Visual 计划** / **执行 Phase A** | 按 §7 Phase A 表格开工 round12 |
| **执行 Phase B** | 本案 pass 后做 Core + 全局晋升 |
| **只写 brief** | 仅 A1–A2，不落图 |

---

## 11. 相关文件索引

| 文件 | 用途 |
| --- | --- |
| 本计划 | `docs/training/visual-first-agent-plan.md` |
| 视觉优先细则 | `docs/training/vision-first-style.md` |
| brief 模板 | `docs/training/visual_style_brief.template.md` |
| 精度宪章 | `docs/training/precision-first.md` |
| 流水线总览 | `docs/training/global-agent-pipeline.md` |
| 审计架构 | `docs/training/audit-architecture.md` |
| Agent 注册 | `agents/pipeline/pipeline_manifest.json` |
| 训练案例 | `projects/residential_sofa_2seat_20260528/` |

---

## 12. 变更记录

| 日期 | 说明 |
| --- | --- |
| 2026-05-28 | 初版：基于 round1–11 教训 + 用户生图金标准 + Agent 架构讨论 |
