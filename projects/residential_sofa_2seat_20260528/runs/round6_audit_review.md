# Round6 自检

## 审计问题（回应你）

round5 **不该过审计**：旧 checklist 只查线数/微线/宽度，**没有款式语义**。
round5 若跑新审计会 fail：

- `style_seat_split_ratio`（座背分界 0.42 vs 参考 0.82）
- `style_back_band_ratio`（靠背带过高）
- `style_excessive_inset`（外框与坐垫间距过大 → 盒子感）

## 本轮审计（`audit_checklist_semantic.json`）

| 维度 | 参考块 | round6 预览 | 结果 |
|------|--------|-------------|------|
| 座背分界 | 0.821 | 0.821 | pass |
| 靠背带比例 | 0.179 | 0.179 | pass |
| 扶手宽 | 120mm | 120mm | pass |
| 微线 | 0 | 0 | pass |
| 宽度 | 2800→1867 | 1866.7 | pass |

`style_pass: true`，`audit_pass: true`

## 落图改动

- 从参考块 **读比例**（非 clone 碎线）
- 座背分界对齐参考（靠背在**顶部窄带**，不是 round5 那种大半截）
- 单层外轮廓 + 贴边坐垫，去掉「厚框 + 内盒」双层感

## 证据

- `round6_preview.png`
- `round6_geometry_audit.json`

## 请你验收

左右**款式是否接近**（两座、靠背在上、扶手厚度）？回 pass / fail。
