# Visual Style Brief 模板

复制到 `projects/<case>/runs/roundN_visual_style_brief.md`，Intent Agent 填完再 Execute。

```markdown
# roundN visual style brief

## 参考
- 截图：`（路径或说明：左参考块 + 用户标注）`
- 任务：同款式 N 座（视觉同款，非逐线 clone）

## 部件（常识，缺则错）
- [ ] 左扶手 — 圆角矩形条，前不封死
- [ ] 右扶手
- [ ] 座垫 ×N — 闭合，前缘凸出扶手
- [ ] 靠垫 ×N — 略椭圆/圆角矩形 + 缝线
- [ ] 靠背/顶栏 — 与靠垫可读分离

## 造型语言
- assembly: open | closed（默认 open）
- seat_vs_arm: protrude_forward_mm ≈ （如 30，取整）
- forbidden: 全封闭外框 / schematic 盒 / 框内假靠垫

## 尺寸（取整，视觉优先）
- target_width_mm: （如 1870，写整数）
- gap_from_reference_mm: （如 400）
- sizing_method: 「三座→两座：参考宽×2/3 取整到 10mm，不纠结小数」

## 弧度（差不多即可）
- corner_r_mm: ≈30（25～35 均可）
- seat_front: 浅弧或圆角即可，不必 match probe

## Agent 目视门槛（Delivery 前自填）
- visual_match_brief:
- same_product_family:
- no_schematic_shortcut:
```
