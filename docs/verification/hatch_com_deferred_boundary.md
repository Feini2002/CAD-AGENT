# Hatch COM Boundary

最后更新：2026-05-27

## LCAD-12-HATCH-COM 与 RCAD-06-HATCH

`LCAD-12-HATCH-COM` 最初选择安全收口为 **structured deferred**，用于固定 hatch 写入前的守卫、失败分类和不得声称边界。后续 `RCAD-06-HATCH` 已把 real COM driver 的受控 smoke 升级为真实 AutoCAD 写入：`AutoCADComDriver.draw_hatch()` 会在 `CODEX_PREVIEW` 创建闭合 boundary polyline，再创建 ANSI31 hatch，并由 created handles 回读验证。

当前边界分两层：

- real COM driver：仅对受控闭合边界 smoke 支持真实 `draw_hatch`，证据为 `readback_geometry_verified`。
- fake driver / no-CAD 路径：继续返回机器可读 **structured deferred**，不得计为几何通过。

fake / no-CAD deferred 证据字段固定为：

- `primitive=hatch`
- `status=deferred`
- `failure_category=hatch_unverified`
- `created_handles=[]`
- `geometry_verified=false`

`RCAD-06-HATCH` 真实 CAD 证据：

- 报告：`output/validation_runs/rcad-06-hatch-cad-20260527-escalated/hatch_cad_smoke_report.json`
- `status=geometry_verified`
- `evidence_state=readback_geometry_verified`
- `geometry_accuracy=verified_by_cad_readback`
- created handles：`61C`、`61D`
- 回读类型：`hatch=1`、`polyline=1`
- pattern：`ANSI31`
- bbox：`100 x 80`
- 安全边界：只写 `CODEX_PREVIEW`，未保存 DWG，未删除实体，未修改正式图层

该边界服务于 `V-PROOF-53`：hatch 已经从“只有能力槽位和 deferred 失败分类”推进到“受控真实 COM hatch smoke 已验证”。但它仍不代表任意复杂 hatch、孤岛 hatch、项目标准填充、正式图层 hatch 或任意 CAD_PLAN hatch 均已证明。

## 不得声称

- 不得把 fake driver / no-CAD 的 `draw_hatch` structured deferred 说成真实 hatch 已绘制。
- 不得用 fake driver 的 deferred 证据替代 AutoCAD created-handle readback。
- 不得因为 `created_handles=[]` 而登记为几何通过；这只代表没有发生真实 CAD 写入。
- 不得把 `RCAD-06-HATCH` 的 ANSI31 矩形 smoke 扩大为任意 hatch 能力已完成。
