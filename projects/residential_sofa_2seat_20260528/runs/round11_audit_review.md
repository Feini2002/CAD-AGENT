# round11 Agent 自检

- audit_pass: true
- target_width_mm: **1870**（取整，非 1866.7）
- delivery_allowed: true

| 项 | pass | 说明 |
|---|---|---|
| visual_match_brief | true | 开放总成；座凸出；靠垫+顶栏 |
| same_product_family | true | 分层 plan 同框族 |
| no_schematic_shortcut | true | 无全封闭 tub |

## 与 brief 对照

| brief 要求 | round11 |
|---|---|
| 开放总成 | ✓ 无 `_outer_shell` |
| 座垫前凸 ~30mm | ✓ `y_bot=py0`，扶手 `y_front=py0+30` |
| 靠垫略椭圆+缝线 | ✓ `_back_cushion_pillow` |
| 靠背顶栏 | ✓ 顶边独立线 |
| 宽 1870 取整 | ✓ 机器读 1870.0 |

## 请你验收

`round11_preview.png` — 左参考三座 / 右 cyan 两座。

仍 fail 请指具体部位；pass 则案例 done。
