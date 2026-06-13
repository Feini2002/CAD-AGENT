# Agent 训练错误记录

面向 `docs/training/` 训练期；每轮验收失败或 CAD 异常在此追加一条。**机器证据**仍在 `projects/<case_id>/runs/`。

**链路类**教训（工序 / 审计 / 自检）写入 `docs/training/pipeline-changelog.md`，本表仍记一行便于检索，但不必重复改 README。

| 日期 | 案例 | 轮次 | 现象 | 根因 | 修复 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-06-09 | `cad-foundation-remaining-21` | item-22 线宽线型专项训练 | 第一次 focused 重画虽然 handles / 线宽线型回读通过，但截图显示第 22 项面板仍贴近并混入旧训练面板区域 | 停放区只读取 `CODEX_PREVIEW` bbox，忽略了旧训练可能位于 `CODEX_PREVIEW_RUN_*` 或其它预览层；机器不重叠检查与视觉上下文不一致 | 删除本轮 12 个 created handles；停车区改为参考全模型空间 bbox，新增回归测试 `test_training_parking_avoids_preview_run_layers_not_only_shared_preview_layer`；重跑 item-22 后新面板移至全模型空间右侧空白区，12/12 handles 回读，线宽 / 线型 / 线型比例 pass，截图无混入旧框 | **已修复并重画** |
| 2026-06-08 | `cad-foundation-all-31` | 当前打开测试 DWG 手工矩阵测试 | 0-31 基础训练矩阵出现空框、框内内容缺失、标题和面板互相重叠，并压到原有画布附近内容 | CAD-MCP 多次绘图调用被中断后只完成了部分边框；Agent 未在每格绘完后做视觉/内容完整性检查；停放区只按大概坐标选择，没有先确认当前视口内容 bbox、面板间距、标题高度和不重叠约束 | 后续基础训练矩阵必须先做布局预案：每格固定内边距、标题区、内容区和 footer；每格至少 1 个几何样例 + 1 行文字说明；先画小范围样板并截图确认，再扩展；禁止在未确认不重叠时继续批量铺开 | **已记录，待规则化回测** |
| 2026-06-08 | `cad-foundation-all-31` | 当前打开测试 DWG 删除修复 | 为删除错误测试框，误删了大量原有内容；用户需要手动 `Ctrl+Z` 恢复 | 删除命令用窗口选择 + `CODEX_PREVIEW` 图层过滤，但原有测试内容也在同图层 / 同窗口范围内；没有 created handles 或唯一 run layer/tag 作为删除证据；用坐标窗口删除属于高风险粗选 | 后续删除 / 清理只能优先按本轮 created handles 或唯一 run layer 删除；没有 handles 时不得用大窗口删除已有 `CODEX_PREVIEW`；若必须清理，先创建独立临时图层如 `CODEX_PREVIEW_RUN_<id>`，或请求用户框选 / 确认范围；删除前先报告受影响范围，删除后立即截图确认 | **已记录，作为安全回归** |
| 2026-06-08 | `cad-foundation-all-31` | 当前打开测试 DWG 撤销恢复 | Agent 发送 `Ctrl+Z` 和 `_OOPS` 后未能可靠恢复；用户手动 `Ctrl+Z` 可以恢复 | GUI 自动化发送快捷键依赖窗口焦点、命令行状态和时序；AutoCAD 中 `Ctrl+Z` 可能先撤销视图平移 / 缩放 / 当前命令状态，而不是刚才的 `ERASE`；CAD-MCP / AutoLISP / SendKeys 不保证和用户键盘处在同一可见上下文；Agent 没有在删除前设置可验证的 undo mark / handles 备份 | 后续不得把 Agent 可发送 `Ctrl+Z` 当作安全网。删除前必须先能定位可恢复对象；删除后若异常，立即暂停让用户手动恢复或确认，不连续发送会改变 undo 栈的 Zoom / Pan / 绘图命令；恢复动作只做一次并截图，不再继续绘制 | **已记录，作为恢复链路限制** |
| 2026-06-02 | `cad-foundation-remaining-21` | item-22 线宽线型复训 | 用户截图指出第 22 项三条线在 CAD 开启线宽显示后仍没有真实变化，线型 / 虚线差异也不明显 | 面板只画普通 `draw_line`；真实 AutoCAD driver 和 Fake driver 未写入 `Lineweight` / `Linetype` / `LinetypeScale`；训练报告只验句柄、图层和中文标注，没有验样式回读 | 新增任务 22 回归测试和运行时 `lineweight_linetype_standard` 检查；样例线改为 `70 + CONTINUOUS`、`35 + CENTER`、`13 + DASHED`，并设置线型比例；真实 CAD focused 复训 1/1 pass、12/12 handles 回读，截图 `output/previews/task22-lineweight-linetype-focused.png` | **已修复并完成 focused 复训** |
| 2026-06-01 | `cad-foundation-remaining-21` | 中文标注复训 | 用户截图指出剩余 21 项训练面板仍有 `checked`、`handles`、`bbox`、`locked`、`Rev-A`、`AUDIT/PURGE`、`checked/not_checked` 等英文可见标注 | 批量训练脚本的 `chinese_labels` 只检查文本含中文，没有阻断中英混排；第 29 项标题还从工作台数据源继承了 `handle 与 bbox 报告` | 新增可见文字英文术语回归测试和运行时 `latin_terms=0` 验收；把面板文案、第 29 项标题与焦点说明改为中文；重跑真实 CAD 后 21/21 pass、235/235 句柄回读、可见文本扫描 86 条 / 英文术语 0 条，并刷新截图和工作台 | **已修复并完成中文复训** |
| 2026-05-28 | `residential_sofa_2seat_20260528` | 1 | 预览层出现跨屏 **巨大青色三角线**；用户验收 fail | 块 `5S03232` 内 `AcDbPolyline` 为 **3D 坐标** `(x,y,z)×n`；`vector_redraw_two_seater.py` 用 `step=2` 当 2D 解析，**z 被误读为下一顶点 x**，顶点飞到块外/原点方向，连线成巨三角 | 仅 2D 解析：`step=3`；逐点校验在沙发 footprint 内；超跨度 polyline 跳过；重绘前清空 `CODEX_PREVIEW` | **已修复并重跑 round1** |
| 2026-05-28 | `residential_sofa_2seat_20260528` | 1 | 自检截图里 **Cursor/微信挡住 CAD** | `ImageGrab.grab(bbox=屏幕坐标)` 拍的是桌面像素，前台窗口挡住就会进图 | 改为 `PrintWindow(hwnd)` 只抓 AutoCAD 客户区；仍先置顶+Zoom | **已修复** |
| 2026-05-28 | `residential_sofa_2seat_20260528` | 1 | 右青两座 **只剩外框/角部毛刺**，不像两格沙发 | ① 按中心删中座 → 跨座线丢失；② 裁切坐标仍用错参考系 | **炸开**块副本 → 在 **预览区 WCS** 删中座 X 带 → 右座左移 933mm（`insert_explode_delete_middle_wcs`） | **已重跑 round1** |
| 2026-05-28 | `residential_sofa_2seat_20260528` | 1 | 用户：**少很多线**、多轮截图一样；Agent 未自检 | `wcs_from_block_local` 误用 `ins[0]+lx+(preview_x0-xmn)`，X 落到约 **-15 万**，裁切后几乎全丢（审计仅 **4** 条线）；却误报 `bottom_rail_present`（补了假底框） | 正确：`preview_x0+(lx-xmn)`、`ref_min_y+(ymx-ly)`；X 向裁中座带、保留全宽水平线；**禁止**无审计声称通过 | **已修复**：预览 **220** Line + 10 Arc + 2 Pline，底框 L=1866.67mm |
| 2026-05-28 | `residential_sofa_2seat_20260528` | 1 | 目视有两格但仍 **未通过**（用户图：中缝/叠线） | 右座左移后与左座在 **接缝 X** 叠了双层竖线/碎线 | 炸开流程 + **接缝带清理**（`seam_cleanup` 保留最长 2 条） | **round1 第 4 次重跑** |
| 2026-05-28 | `residential_sofa_2seat_20260528` | 2→3 | 用户：样式对但 **杂线多**，审计 Agent 界定不足 | 中缝带 20 条碎线；顶框 6 组短横线与全宽线叠线 | 洁净度 checklist；seam 清理 + handle 叠线去重（-8） | **round3 审计 pass** |
| 2026-05-28 | `residential_sofa_2seat_20260528` | 12 | 用户：下方衔接仍错；参考有弧线且线条丝滑，生成仍全靠圆角矩形；部件有重叠或间隙 | 生成链路把所有 `visual_parts.shape` 收敛为 `_rounded_rect`；审计链路未启用 `reference_profile_match`，且没有 gap/overlap 与“全圆角矩形单一化”阻断项；Agent 自检把部件存在误判为款式匹配 | round13 前先补审计硬门槛，再把生成改为带弧线与装配节点的语义重绘 | **待修复** |
| 2026-05-28 | `residential_sofa_2seat_20260528` | 13→14 | 用户认可“该重合的地方靠在一起”，但指出中间有白线，且沙发方向语义反了：底部是硬靠背，中间椭圆是软靠垫，上方大块是坐垫 | 执行层对相邻部件的同一共享线段重复出图；视觉契约只写 `role`，没有写平面图前后方向和硬/软/坐垫层级，Audit 也没有方向常识门槛；旧 reference split ratio 还带着反向语义假设 | 渲染器去重完全重复线段；新增 `hard_back_count` / `sofa_layer_order_pass` 摘要和 `sofa_direction_semantics_inverted` 全局反模式；round14 visual parts 改为硬靠背→软靠垫→坐垫，并跳过旧 split ratio 阻断 | **已真实 CAD 重画 round14；待用户目视验收** |
| 2026-06-01 | `cad-foundation-first-10` | item-01 | 监督式基础队列第 1 项默认 `CAD_CAPABILITY_PROBE` 语义不明、等待时间长，且固定坐标叠到已有沙发图形上 | 通用能力探针用于机器回读，固定 `PROBE_BASE_POINT=[2400,1200,0]`，还带大号技术标签；没有按当前 DWG 的已有 `CODEX_PREVIEW` bbox 选空白落点 | 记录 fail；清理旧 probe handles；改用 `draw_symbol_glyph` CAD_PLAN 在已有图形右侧空白区重画 5 格基础图元训练小样，22/22 handles 回读，截图 `output/training_queues/cad-foundation-first-10/item-01-cad-primitives-retry-02/retry_preview.png` | **已重试，暂停等待用户目视验收** |
| 2026-06-01 | `cad-foundation-remaining-21` | item-16 | 剩余 21 项批量训练首次真实 CAD 运行到“块插入与属性”时阻断：`insert_block_alpha alpha only supports uniform scale` | 批量训练脚本给 `insert_block_alpha` 传了 `[0.42, 0.42, 1]` 等非 uniform 三轴比例；真实 AutoCAD block alpha 要求 x/y/z scale 完全一致，Fake driver 未覆盖该约束 | 新增严格 block scale 回归测试；脚本改为 `[0.42, 0.42, 0.42]` / `[0.55,0.55,0.55]` / `[0.35,0.35,0.35]`；重跑真实 CAD 后 21/21 pass、235/235 handles 回读 | **已修复并完成 21 项批量训练** |

## 教训（写入规则）

- 从产品块 **矢量重绘** 时：禁止假设 polyline 为 2D；先读 `Coordinates` 长度与 `len%3`。
- 块内 `GetBoundingBox()` 不可靠时，用 **逐顶点** 范围校验。
- 验收 fail 后：先 **只保留参考块**（如 `4A2`），再重绘预览层。
