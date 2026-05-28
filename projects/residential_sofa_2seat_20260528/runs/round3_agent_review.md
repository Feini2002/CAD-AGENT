# Round 3 Agent 自检

案例：`residential_sofa_2seat_20260528`
触发：用户反馈 round2「样式基本对，但杂线很多」

## 机器审计（`round3_geometry_audit.json`）

| 检查项 | round2 | round3 |
| --- | --- | --- |
| `audit_pass` | true | **true** |
| 中缝带碎线 | 20 | **0** |
| 叠线横线 | 6 | **0**（去重 8 条） |
| 短线数 | 110 | **92**（参考基线 110） |
| 总线数 | 225 | **197** |

新增洁净度门槛：`expected/audit_checklist.json`

## 根因（杂线）

1. **中缝带 ±12mm**：裁切后残留 20 条 L<8mm 碎线（扶手圆角 tick 被映射到中缝）
2. **顶框叠线**：6 条短横线与全宽顶框共线重叠（COM 对象 id 去重失败，改 handle 去重后删 8 条）

## 修复

- 裁切阶段过滤中缝碎线
- `_cleanup_seam_clutter` + `_dedupe_overlapping_horizontals`（按 handle）
- 审计增：洁净度三层界定（见 `docs/training/README.md`）

## 目视（`round3_preview.png`）

- 两座形态、底框、两格坐垫：与 round2 一致
- 中缝/顶框区域杂线应明显减少（机器：seam 0、overlap 0）
- 扶手角短线仍可能存在（与参考块同类 fillet tick，92 vs 基线 110）

## Agent 判定

**可请你验收。** 已响应「审计 Agent 需更多界定」；若仍见杂线请指出区域（中缝 / 顶框 / 扶手 / 底框）。
