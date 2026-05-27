# Hatch COM Deferred Boundary

最后更新：2026-05-27

## LCAD-12-HATCH-COM

`LCAD-12-HATCH-COM` 选择安全收口为 **structured deferred**，不是直接写入真实 AutoCAD hatch。当前 `draw_hatch` 入口存在于 real COM driver 与 fake driver，但只产出机器可读 deferred 证据：

- `primitive=hatch`
- `status=deferred`
- `failure_category=hatch_unverified`
- `created_handles=[]`
- `geometry_verified=false`

该边界服务于 `V-PROOF-53`：hatch 能力已经有显式能力槽位、写入守卫和可读失败分类，但不能被登记为真实 `geometry_verified`。后续若要升级为真实 COM hatch，必须补齐 boundary loop 构造、created handle 回读、图层映射检查、几何回读检查和负向 formal-layer guard 复验。

## 不得声称

- 不得把 `draw_hatch` structured deferred 说成真实 hatch 已绘制。
- 不得用 fake driver 的 deferred 证据替代 AutoCAD created-handle readback。
- 不得因为 `created_handles=[]` 而登记为几何通过；这只代表没有发生真实 CAD 写入。
