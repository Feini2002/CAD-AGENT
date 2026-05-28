# 视觉优先 + 常识造型（Vision First）

最后更新：2026-05-28

## 何时启用

用户说 **「参照左侧画同款」**、**「同款式两座」**、发参考截图 —— **必须先截图分析，再落图**。

**视觉 > 尺寸 > 弧度细节。** 数字比例、参考块 probe 是**辅助**，不能代替目视，也不能为了小数精度牺牲款式。

---

## 优先级（从高到低）

```text
1. 截图 Agent 分析 — 部件清单 + 造型语言（开放/封闭、凸出、圆角/椭圆）
2. 常识物件模型 — 沙发缺靠背/扶手/靠垫 = 结构错误（除非用户明确特殊款）
3. 视觉回环 — 落图后再截图，与参考并排比「像不像同款」
4. 机器 audit — 断线、全封闭反模式、宽度粗容差（必要非充分）
5. 尺寸近似 — 生活化取整，不纠结 2/3 小数
6. 弧度/圆角 — 看起来差不多即可，禁止为 R=30.0 vs R=28 反复改
```

---

## 尺寸：近似 + 取整（不死扣）

| 场景 | 做法 | 禁止 |
| --- | --- | --- |
| 三座 → 两座 | 总宽 ≈ 参考宽 × 2/3，**取整到 5 或 10mm**（如 1870） | 死用 1866.7、为 0.1mm 调参 |
| 座宽 / 扶手 | 按视觉平分或略留白，整数 mm | 精确 clone 参考块公式到小数 |
| 间距（如 +400） | 可取整 400，偏差 ±20mm 可接受 | 为对齐 probe 改 gap |
| 比例槽位 | seat/back 比例 **大致** 像参考即可（容差放宽） | audit 数字绿但款式错 |

**Execute 规则：** 读 `visual_style_brief` 里的 `target_width_mm`（取整值），不要反向从 probe 反推碎小数。

**Audit 规则：** 宽度 band 用 **±2～3% 或 ±30mm**；`reference_profile_match` 失败但 **visual 全绿** → 不得 alone 触发 Repair（先信视觉）。

---

## 造型：差不多就行（不抠弧）

| 元素 | 标准 | 不必 |
| --- | --- | --- |
| 圆角矩形（扶手/靠背） | R 与参考 **同级**（如 25～35） | 必须 R=probe 精确值 |
| 靠垫 | 略椭圆或圆角矩形，视觉鼓一点 | 精确椭圆长轴比 |
| 座前弧 | 有浅弧或圆角即可 | 与参考弧 sag 一致 |
| 部件轮廓 | 每个部件 **闭合**、少断线 | 与供应商块逐段同构 |

---

## Intent 阶段必产出

`runs/roundN_visual_style_brief.md`（或 intent.json 内 `visual_style` 段）：

| 字段 | 示例（本案） |
| --- | --- |
| `reference_screenshot` | 左块 + 用户标注 |
| `parts[]` | 左扶手、右扶手、座垫×2、靠垫×2、靠背顶栏 |
| `assembly` | **开放总成**；禁止整圈外框包死 |
| `seat_vs_arm` | 座垫前缘 **凸出** 扶手前缘 |
| `part_shapes` | 扶手/靠背 ≈ 圆角矩形；靠垫略椭圆 |
| `target_width_mm` | **1870**（取整，非 1866.7） |
| `sizing_notes` | 三座变两座，宽≈2/3 取整，不偏离参考太多 |
| `forbidden_visual` | 全封闭 tub、schematic 盒、框内细线冒充靠垫 |
| `closed_per_part` | 每部件闭合；部件之间可断开 |

**无 visual_style_brief → 禁止 Execute。**

---

## Audit 阶段必做

**顺序：先 Visual，后机器。**

1. **Visual Audit Agent** — 读 `roundN_preview.png` + 参考截图，填 `agent_review_required`
2. 机器 `training_geometry_audit` — 断线、反模式、**粗**尺寸 band

**visual 任一项 fail → 禁止 Delivery。**
**仅机器尺寸 fail、visual 全绿 → 记录为 approximate_ok，不阻塞 Delivery。**

---

## Execute 画法约定

| 部件 | 画法 |
| --- | --- |
| 扶手 | 独立圆角矩形条，前缘不封死座区 |
| 座垫 | 每座闭合圆角矩形 + 可选浅前弧 |
| 靠垫 | 略椭圆或圆角矩形 + 缝线 |
| 靠背 | 顶栏/后框，与靠垫分离可读 |

优先 **每部件一条闭合轮廓**（polyline 或端点重合的 line+arc）。

---

## 与 precision-first 的关系

- **准** = 视觉同款 + 常识结构 + 少断线 → 尺寸近似 → 弧度差不多。
- 机器 audit 误绿（round7/9）= 只验数字，没验「像不像正常沙发」。

---

## 案例沉淀

repeatable 视觉失败 → `forbidden_visual` → 第二案例仍犯 → 晋升 Core 探针。
repeatable **过度抠尺寸** → 写 pipeline 规则「visual 绿不得为尺寸 Repair」。
