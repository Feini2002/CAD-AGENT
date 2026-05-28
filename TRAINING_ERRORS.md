# Agent 训练错误记录（根目录）

面向 `docs/training/` 训练期；每轮验收失败或 CAD 异常在此追加一条。**机器证据**仍在 `projects/<case_id>/runs/`。

**链路类**教训（工序 / 审计 / 自检）写入 `docs/training/pipeline-changelog.md`，本表仍记一行便于检索，但不必重复改 README。

| 日期 | 案例 | 轮次 | 现象 | 根因 | 修复 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-05-28 | `residential_sofa_2seat_20260528` | 1 | 预览层出现跨屏 **巨大青色三角线**；用户验收 fail | 块 `5S03232` 内 `AcDbPolyline` 为 **3D 坐标** `(x,y,z)×n`；`vector_redraw_two_seater.py` 用 `step=2` 当 2D 解析，**z 被误读为下一顶点 x**，顶点飞到块外/原点方向，连线成巨三角 | 仅 2D 解析：`step=3`；逐点校验在沙发 footprint 内；超跨度 polyline 跳过；重绘前清空 `CODEX_PREVIEW` | **已修复并重跑 round1** |
| 2026-05-28 | `residential_sofa_2seat_20260528` | 1 | 自检截图里 **Cursor/微信挡住 CAD** | `ImageGrab.grab(bbox=屏幕坐标)` 拍的是桌面像素，前台窗口挡住就会进图 | 改为 `PrintWindow(hwnd)` 只抓 AutoCAD 客户区；仍先置顶+Zoom | **已修复** |
| 2026-05-28 | `residential_sofa_2seat_20260528` | 1 | 右青两座 **只剩外框/角部毛刺**，不像两格沙发 | ① 按中心删中座 → 跨座线丢失；② 裁切坐标仍用错参考系 | **炸开**块副本 → 在 **预览区 WCS** 删中座 X 带 → 右座左移 933mm（`insert_explode_delete_middle_wcs`） | **已重跑 round1** |
| 2026-05-28 | `residential_sofa_2seat_20260528` | 1 | 用户：**少很多线**、多轮截图一样；Agent 未自检 | `wcs_from_block_local` 误用 `ins[0]+lx+(preview_x0-xmn)`，X 落到约 **-15 万**，裁切后几乎全丢（审计仅 **4** 条线）；却误报 `bottom_rail_present`（补了假底框） | 正确：`preview_x0+(lx-xmn)`、`ref_min_y+(ymx-ly)`；X 向裁中座带、保留全宽水平线；**禁止**无审计声称通过 | **已修复**：预览 **220** Line + 10 Arc + 2 Pline，底框 L=1866.67mm |
| 2026-05-28 | `residential_sofa_2seat_20260528` | 1 | 目视有两格但仍 **未通过**（用户图：中缝/叠线） | 右座左移后与左座在 **接缝 X** 叠了双层竖线/碎线 | 炸开流程 + **接缝带清理**（`seam_cleanup` 保留最长 2 条） | **round1 第 4 次重跑** |
| 2026-05-28 | `residential_sofa_2seat_20260528` | 2→3 | 用户：样式对但 **杂线多**，审计 Agent 界定不足 | 中缝带 20 条碎线；顶框 6 组短横线与全宽线叠线 | 洁净度 checklist；seam 清理 + handle 叠线去重（-8） | **round3 审计 pass** |

## 教训（写入规则）

- 从产品块 **矢量重绘** 时：禁止假设 polyline 为 2D；先读 `Coordinates` 长度与 `len%3`。
- 块内 `GetBoundingBox()` 不可靠时，用 **逐顶点** 范围校验。
- 验收 fail 后：先 **只保留参考块**（如 `4A2`），再重绘预览层。
