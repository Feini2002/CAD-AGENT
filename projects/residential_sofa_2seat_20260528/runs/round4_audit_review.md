# Round 4 审计自检

案例：`residential_sofa_2seat_20260528`
链路：Step1 `round4_intent.json` → Step2 落图 → Step3 本文件

## 1. 机器审计（`round4_geometry_audit.json`）

| 项 | 值 |
| --- | --- |
| `audit_pass` | **true** |
| 线数 | 197（参考基线 222，保留比 0.887） |
| 叠线 | 0（去重 8） |
| 中缝碎线 | 0（清理 18） |
| 弧 | 10（与参考块一致） |
| 微短线 L&lt;6mm | 72（参考 88，更少且保留 fillet） |

## 2. 相对 round3 / 用户反馈

| 问题 | round4 处理 |
| --- | --- |
| 断线、不顺滑 | 左/右座 **整段映射**（不裁切），仅跨座带 clip |
| 杂线 | 叠线去重 + 仅中缝 &lt;5mm 清理；**不删**扶手圆角 fillet |
| 验收远未达标 | 已改善；仍须你目视 pass/fail |

## 3. 残留风险

- 197 线仍少于参考 222（删中座必然）；视觉应与左块接近但未必逐线一致
- 坐垫圆角仍由短线+弧拼成（与产品块同源），非 spline 光顺

## 4. 审计环判定

- [x] 机器 audit 全绿
- [x] 可请你 §几何 feedback

**证据：** `round4_preview.png`
