# 训练反馈记录

案例 id：`residential_sofa_2seat_20260528`

## §理解（白话是否听懂）

| 轮次 | 日期 | 你的原话摘要 | Agent 理解 | 问题 | 已改 rules? |
| --- | --- | --- | --- | --- | --- |
| 1 | 2026-05-28 | 左三座旁同款两座；矢量重绘勿缩放 | 块 `5S03232` 右侧预览 `CODEX_PREVIEW` | — | 已有 `agents/residential/rules.md` |

## §计划（CAD_PLAN 是否对上）

| 轮次 | validate | dry-run | 和你的预期差在哪 | 处理 |
| --- | --- | --- | --- | --- |
| 1 | 脚本直跑 | — | 未走独立 CAD_PLAN JSON | 案例用 `runs/vector_redraw_two_seater.py` |
| 2 | 脚本 + `audit_checklist.json` | 审计不过则 exit 1 | — | round2 按理想链路 |

## §几何（预览图是否对上）

| 轮次 | 你判定 | 不准点 | 证据 |
| --- | --- | --- | --- |
| 1 | **fail** | 少很多线；多轮截图一样；Agent 未分析 | `round1_preview.png` |
| 1b | **fail** | 靠背空、无中缝竖线、扶手角乱 | 用户截图 |
| 2 | **待你验收** | 样式基本对，但 **杂线很多**（左块干净） | 用户截图；`round2_preview.png` |
| 3 | **待你验收** | 断线、不顺滑、杂线 | `round3_preview.png` |
| 4 | **fail** | 断线、不顺滑、杂线；审计虚绿 | `round4_preview.png`；用户截图 |
| 5 | **fail** | 洁净度绿但款式错：厚框+座背比例反了 | `round5_preview.png`；缺 style 审计 |
| 6 | **fail** | schematic 方盒款 | `round6_preview.png` |
| 7 | **fail** | 款式仍不对；机器审计误绿 + 自检已写「仍有差距」仍交付 | `round7_preview.png`；用户截图 |
| 8 | **fail（Agent 目视）** | 洁净度/断点改善，但外框厚、坐垫仍偏 pill，与参考家族差距 | `round8_preview.png`；**未交付** |
| 9 | **fail** | 全封闭外框；座不凸出；无真靠垫/靠背 | 用户截图；`round9_preview.png` |
| 10 | **fail** | 全封闭盒 | 用户截图 |
| 11 | **待你验收** | 开放总成+1870+靠垫；visual 绿 | `round11_preview.png` |
| 12 | **fail** | 下方衔接仍错；左侧参考有弧线和更丝滑线条，右侧生成仍主要靠圆角矩形堆叠；部件之间有重叠或间隙；机器审计与 Agent 自检误绿 | 用户截图；`round12_preview.png`；`round12_geometry_audit.json`；`round12_agent_review.json`；`round12_style_compare.md`；`expected/style_target_reference_crop.png` |
| 13 | **自检阻断** | 已删除上一轮错误 `CODEX_PREVIEW` 56 个实体并重画；机器审计通过 0 gap / 0 overlap / 0 open endpoint，且不再是圆角矩形单一化。但截图自检仍发现款式层级不像参考：右侧生成的靠背/坐垫视觉关系仍偏机械，不能直接请你验收。 | `round13_preview.png`；`round13_execution_summary.json`；`round13_geometry_audit.json`；`round13_agent_review.json` |
| 14 | **待你验收** | 按你的标注修正方向：底部硬靠背，中间软靠垫，上部大块坐垫；中间重复白线已通过共享边去重消除；机器审计通过 0 gap / 0 overlap / 0 open endpoint。 | `round14_preview.png`；`round14_execution_summary.json`；`round14_geometry_audit.json`；`round14_agent_review.json` |

## §用户指出的错因（原话）

| 轮次 | 日期 | 你的原话 / 不准点 | 附件 |
| --- | --- | --- | --- |
| 1 | 2026-05-28 | 「少了很多线」「前面几轮截图都一样」「你没有自己思考过不通过原因」 | 截图 |
| 1b | 2026-05-28 | 「还是错，原因我不说，你自己思考了发给我」 | 截图 |
| — | 2026-05-28 | 仍 fail：断线、线条不够顺滑、远未验收 | 截图 |
| — | 2026-05-28 | 先写理想链路；再按新链路重跑 | 对话 |
| 12 | 2026-05-28 | 「下方的衔接还是有错误」「左侧示意有弧线、线条更丝滑」「右侧生成全靠圆角矩形支撑，丰富度极低」「要么有重叠要么有间隙，错误率还是很高」 | 用户截图 |
| 13 | 2026-05-28 | 「该重合的地方靠在一起了，我认为不错，可以记下」「中间莫名其妙有根白线，修复这个BUG」「方向错了：最下面是硬靠背，中间类似椭圆形的是靠垫，上面较大块是坐垫本身」 | 用户截图 + 标注图 |

## §Agent 根因与修复

| 轮次 | 根因（证据） | 修复步骤 | 判因类型 |
| --- | --- | --- | --- |
| 1 | 坐标公式错；审计虚报 | 改 WCS 映射 | 几何 |
| 1 | 缺截图后自检 | 写 `docs/training/README.md` 理想链路 | **链路** |
| 1b | 中缝边界开区间；中座靠背竖线偏入带内被删 | 文档化；round2 再修 | 几何 + **链路** |
| 2 | round2 样式对但杂线多；审计无洁净度项 | 中缝 20 碎线 + 顶框 6 组叠线 | round3 checklist + 去杂线 | 几何 + **链路** |
| 4 | 断线/不顺滑/杂线 | clone 产品碎线 DNA | round5 语义重绘 | **方法论** |
| 5 | 左右款式差极大 | 审计无 style；座背 0.42 反了 | round6 + `sofa_semantic_style_audit.py` | **链路** + 几何 |
| 7 | 款式不对；不应交付 | 审计只验比例/鼓弧数，未验款式；Delivery 违规 | round7 fail；收紧 Delivery 门槛 | **链路** |
| 8 | 断点 60→32；款式仍不对 | 修 endpoint 连接；Agent 目视拦交付 | round9 细臂/扁垫 | 几何 |
| 9 | 全封闭盒；无靠垫靠背；座不凸出 | `_outer_shell` 方法论错误 | round10 开放总成 | **方法论** |
| 10 | 参考块 probe 前凸30mm | 删外框；分层扶手/座/靠垫/顶栏 | 待用户目视 | 几何 + **方法论** |
| 12 | 生成链路仍把 `visual_parts.shape` 收窄为圆角矩形族；`part_renderer.py` 对所有部件统一调用 `_rounded_rect`，缺少弧线/切线/连接拓扑表达。审计链路缺 `reference_profile_match` 阻断项，`round12_geometry_audit.json` 已显示 preview `seat_split_ratio=0.05` / `back_band_ratio=0.95` 与 reference `0.821` / `0.179` 极不一致却仍 pass；也未检查部件间 gap/overlap 和圆角矩形单一化。Agent 自检把“部件存在”误当“款式匹配”。 | round13 前先补审计阻断：reference profile mismatch、部件衔接 gap/overlap、全圆角矩形单一化；再把生成从独立圆角矩形改为带装配节点的弧线/坐垫/扶手语义重绘 | **链路** + 几何 + **方法论** |
| 13 | 生成器已经从圆角矩形堆叠改成曲线部件并修正了 `_bow_arc` 的大圆弧角度问题；但审计里的 profile ratio 仍只约束分割比例和衔接，不足以判断“哪一层是靠背、哪一层是坐垫”的视觉语义。 | round14 增加参考方向/层级语义审计：低 Y/后侧是硬靠背，中间椭圆是软靠垫，高 Y/前侧大块是坐垫本体；通过后再落 CAD。 | **链路** + 几何 + **视觉语义** |
| 13b | `round13` 的衔接方向比 round12 好，说明 `part_gap_count=0` / `part_overlap_count=0` 这类装配拓扑门槛有效；白线来自相邻部件重复画完全相同的共享竖线。更大的问题是 `visual_parts` 没有表达沙发俯视常识：后侧硬靠背、前置软靠垫、更前方坐垫，因此 Agent 把坐垫和靠背方向画反。 | `part_renderer.py` 对完全重复线段做去重；`training_geometry_audit.py` 新增 `sofa_direction_semantics_inverted`；`agents/residential/rules.md` 和 pipeline agent 配置写入沙发俯视层级常识；准备 `round14_visual_parts.json`。 | **链路** + 几何 + **场景常识** |

## 案例结论

- [ ] done
- [x] round7 **fail**（不应交付）
- [x] round8 **fail**（Agent 目视；遵守 Delivery 未请你验收）
- [x] round9 **fail**（全封闭盒；不应交付）
- [x] round10 **fail**（全封闭盒）
- [ ] round11 **待你验收**（`round11_preview.png`）
- [x] round12 **fail**（生成链路圆角矩形单一化；审计/自检虚绿）
- [x] round13 **自检阻断**（已删旧错图并重画；机器 gap/overlap 通过，但截图自检不放行）
- [x] round13 用户纠错已记录：衔接贴合是正向进展；白线和沙发方向语义已转入 round14 修复链路
- [ ] round14 **待你验收**（`round14_preview.png`）

**next：** 等你对 round14 目视反馈；若仍 fail，进入 round15 并沿用本轮新增的方向语义和共享边去重门槛。
