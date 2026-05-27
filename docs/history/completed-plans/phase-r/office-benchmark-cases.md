# Phase R Office Benchmark Cases

状态：办公基础闭环 Alpha benchmark 已完成（17 cases，non-CAD only）
最后同步：2026-05-26（`R-OFFICE-MICRO-05` 收口）

> 本文是 Phase R 的办公 benchmark 辅助规格，不是独立 PlanMD。它把“办公桌、办公椅、电脑桌、柜体、入口、通道、失败样本”转成可执行 benchmark 规格；是否进入实现、优先级和退出标准以 `CORE_RESTRUCTURE_PLAN.md` 为准。它不把 office agent 写成算法层，也不声称真实 CAD 几何已验证。

## 当前落地

已新增 `examples/benchmarks/office_alpha_benchmark.json`，当前包含 **17 个 cases**：6 个 object spec、4 个 micro-scene composition spec、4 个 blank-shell scene、3 个 failure。当前 runner 已支持：

- `evidence_state`
- `geometry_accuracy`
- `screenshot_role`
- `minimums`
- `contains_object_types`
- `contains_component_roles`
- `contains_clearance_refs`
- `contains_binding_relations`
- `contains_circulation_roles`
- `object_spec` / `composition_spec` pipeline
- suite / case 配置校验
- 每个 CAD_PLAN 的 `dry_run_reports.json` 与 `verification_reports.json` 汇总证据

pass 样本证据为非 CAD：`benchmark_pass_non_cad`、`geometry_accuracy=not_verified_without_cad_readback`、`screenshot_role=visual_aid_only`。failure 样本为 `blocked_expected_non_cad`，含 `failure_category` 与 `blocked_reasons` 机器断言。这不证明真实 CAD 几何准确。

**Alpha 收口证据**（`R-OFFICE-MICRO-05`）：`294 tests OK`；`output/test_artifacts/benchmarks/office_alpha_r_micro/benchmark_summary.json` → 17/17 pass，`evidence_summary.non_cad_only=true`，`geometry_verified_case_count=0`。详见 `docs/verification/office_alpha_benchmark_evidence.md`。

## 对象字段约定

统一建议字段：

- `type`
- `business_name`
- `aliases`
- `default_size_mm`
- `size_range_mm`
- `anchor`
- `orientation_semantics`
- `clearance_refs`
- `preferred_layers`
- `placement_role`
- `candidate_tags`
- `assertion_hints`

这些字段是业务语义和验证提示，不在场景 Agent 内实现碰撞、通道、净空或 CAD 执行。

## 最小对象集合

| 对象 | 默认尺寸 / 字段 | 角色 | 验收重点 |
| --- | --- | --- | --- |
| `office_desk` | `1400x700x750` | `workstation_surface` | 与 chair、main aisle、chair pullback 关系可解释 |
| `office_chair` | `500x500x850`，绑定 `desk_id` | `seating_for_desk` | orientation 指向桌前，pullback clearance 存在 |
| `computer_desk` | `1200x700x750` 或 `1400x700x750` | `screen_workstation` | 带 `monitor_zone` / `cable_side_hint`，可靠墙或设备墙 |
| `storage_cabinet` | `900/1200/1800 x 450/600 x 2000` | `general_storage` | 柜前 `cabinet_front_clearance` 可解释 |
| `file_cabinet` | `900x450x1100` 或 `1200x450x1100` | `document_storage` | 背墙、办公区边缘、取物净空存在 |
| `main_aisle` | `min_width_mm`、`target_width_mm`、`connects`、`continuity_required` | 主通道 | 默认目标 `1100mm`，不能被对象断开 |
| `entry_clearance` | `opening_id`、`clear_depth_mm`、`clear_width_mm` | 入口净空 | 默认入口前净空深度 `1200mm` |
| `chair_pullback_clearance` | `bound_to`、`behind_depth_mm`、`side_margin_mm` | 椅后净空 | Alpha 默认 `800mm` |
| `cabinet_front_clearance` | `bound_to`、`front_depth_mm` | 柜前净空 | 默认 `800mm`，高频取物可 `900mm` |
| `no_place_zone` | `zone_id`、`reason`、`bbox`、`severity`、`source` | 禁布区 | 柱、设备、门前、消防或人工禁布 |

## Benchmark Cases

下表包含已落地 case。object + micro-scene + scene + failure 四类均已落地（2026-05-26，`R-OFFICE-MICRO-04` 完成 failure 行）。

| 类别 | case_id | input intent | expected assertions | evidence_state |
| --- | --- | --- | --- | --- |
| object | `office_desk_default_spec` | 生成 1 张办公桌 | type / size / name / component roles 合法；bbox 为 `1400x700`；CAD_PLAN dry-run valid | `benchmark_pass_non_cad` |
| object | `office_chair_default_spec` | 生成 1 把办公椅 | type / size / component roles 合法；seat / back 语义存在；CAD_PLAN dry-run valid | `benchmark_pass_non_cad` |
| object | `office_cabinet_default_spec` | 生成 1 组柜体 | type / size / component roles 合法；body / front_panel / shelf 语义存在；CAD_PLAN dry-run valid | `benchmark_pass_non_cad` |
| object | `computer_desk_default_spec` | 生成电脑桌 | 默认尺寸合法；带 screen / workstation 语义标签 | `benchmark_pass_non_cad` |
| object | `storage_cabinet_front_clearance` | 生成储物柜及柜前净空意图 | cabinet bbox 与 clearance intent 均存在 | `benchmark_pass_non_cad` |
| object | `file_cabinet_default_spec` | 生成文件柜 | 尺寸、front side、取物净空 refs 存在 | `benchmark_pass_non_cad` |
| micro-scene | `single_desk_chair_pair` | 1 张桌 + 1 把椅 | 椅子绑定桌；pullback clearance refs 存在 | `benchmark_pass_non_cad` |
| micro-scene | `desk_with_back_cabinet` | 办公桌 + 背柜 | desk / chair / cabinet placed 或明确 blocked；椅后和柜前净空不静默冲突 | `benchmark_pass_non_cad` |
| micro-scene | `two_workstations_shared_aisle` | 2 个工位共用主通道 | object_types 覆盖 desk/chair；main_aisle 连续；失败原因结构化 | `benchmark_pass_non_cad` |
| micro-scene | `entry_reception_clearance` | 入口附近接待桌 | entry_clearance 存在；接待对象不压入口净空 | `benchmark_pass_non_cad` |
| scene | `office_small_suite_alpha` | 小办公室：2-4 工位、电脑位、文件柜 | candidate_count > 0；zone_count > 0；placement 覆盖 desk/chair/cabinet；dry-run valid；verification unverified | `benchmark_pass_non_cad` |
| scene | `long_narrow_office_main_aisle` | 长条办公室沿墙 / 中轴布置 | main_aisle 连续；通道不被 placed bbox 断开 | `benchmark_pass_non_cad` |
| scene | `office_obstacle_avoidance_riser` | 有柱 / 设备 / 禁布区 | no_place_zone 被读入；对象不压禁布区，或 blocked reason 指向障碍 | `benchmark_pass_non_cad` |
| scene | `meeting_computer_mixed_zone` | 会议 / 电脑桌混合 | 会议区与办公区分区可解释；主通道连接入口和各区 | `benchmark_pass_non_cad` |
| failure | `too_small_room_for_workstation` | 房间过小但要求 2 工位 | status 为 blocked / invalid；原因含 insufficient space / clearance impossible | `blocked_expected_non_cad` |
| failure | `door_clearance_conflict` | 对象要求放在入口净空 | blocked；原因指向 entry_clearance conflict | `blocked_expected_non_cad` |
| failure | `cabinet_pullback_conflict` | 背柜与椅后净空硬冲突 | blocked 或需要确认；原因指向 chair / cabinet clearance conflict | `blocked_expected_non_cad` |

## 场景验收重点

| 场景 | 最小验收 |
| --- | --- |
| 小办公室单入口 | 入口净空、2-4 工位、椅后净空、柜前净空、主通道均有结构化表达；Alpha 不要求最优布局 |
| 长条形办公室 | 主通道必须连续；候选排序优先通道连续，再看工位密度 |
| 有障碍柱 / 避让区 | `fixed_obstacles` 与 `no_place_zones` 进入断言；成功样本不压，失败样本原因明确 |
| 入口接待 / 等候 | 入口净空优先级最高；接待对象可近入口，但不能挡门或让访客动线穿过办公位 |
| 办公桌 + 背柜 | `chair_pullback_clearance` 与 `cabinet_front_clearance` 的关系必须可验证、可解释 |
| 会议 / 电脑桌混合 | 验收分区语义、对象类型覆盖、入口到会议区 / 办公区路径可解释 |
| 失败样本 | 必须输出 `blocked` / `invalid` 和结构化失败原因，不能用“少放对象”假装成功 |

## 场景 Agent 边界

office agent 可以写：

- 业务词汇。
- 默认尺度偏好。
- 对象组合语义。
- 候选排序权重。
- 业务解释模板。
- 对 `libraries/` 对象和块元数据的权重选择。

office agent 不得写：

- 碰撞检测。
- 通道生成。
- 多边形 / 净空算法。
- CAD_PLAN 校验、dry-run、执行、截图、回读。
- 真实项目数据或公司块库本体。

## 实现参考项（以主计划为准）

| 编号 | 任务 |
| --- | --- |
| R-OFFICE-01 | 定义 office 最小对象字段草案，区分 `libraries/objects` 通用字段与 `agents/office` 偏好字段。 |
| R-OFFICE-02 | 补 office 业务词汇、默认尺度、对象组合语义、解释模板，确保不含算法。 |
| R-OFFICE-03 | 设计 `office_alpha_benchmark.json` case schema，支持 object / micro-scene / scene / failure 分类和 evidence_state。（object spec + 第一条 scene case 已落地） |
| R-OFFICE-04 | 规划小办公室、长条办公室、障碍避让、入口接待、背柜、会议/电脑桌混合 shell/workflow 样本。 |
| R-OFFICE-05 | 为 benchmark runner 规划业务断言字段：`object_types`、`placement_count`、`failed_check_count`、`blocked_reason`、`clearance_refs`。 |
| R-OFFICE-06 | 定义失败样本验收门槛，禁止无声降级为 partial success。 |
| R-OFFICE-07 | 将 evidence_state 写入报告规范，显式保留 `geometry_accuracy: not_verified_without_cad_readback`。 |
| R-OFFICE-08 | 整理 office alpha 退出门槛：非 CAD benchmark pass、dry-run valid、真实 CAD readback deferred。（**2026-05-26 完成**，见 `docs/verification/office_alpha_benchmark_evidence.md`） |

## Alpha 退出门槛（R-OFFICE-08）

| 门槛 | 状态 | 证据 |
| --- | --- | --- |
| 四类 case 齐全（object / micro-scene / scene / failure） | 完成 | 17 cases in `office_alpha_benchmark.json` |
| `run_benchmark_suite` 全 pass | 完成 | `office_alpha_r_micro/benchmark_summary.json` |
| pass case 均为 `benchmark_pass_non_cad` | 完成 | `evidence_state_counts.benchmark_pass_non_cad = 14` |
| failure case 均为 `blocked_expected_non_cad` | 完成 | `evidence_state_counts.blocked_expected_non_cad = 3` |
| 无 case 声称 `geometry_verified` | 完成 | `geometry_verified_case_count = 0` |
| 真实 CAD office readback | **未做** | 后续 `R4-EVIDENCE-GATES` / CAD 扩展包 |

## 本文不能声称

本文不能声称办公布局几何已经真实准确，不能声称已经通过 AutoCAD readback，不能声称已有完整碰撞 / 通道 / 净空算法，不能把截图当几何证据，也不能把 `benchmark_pass_non_cad` 等同于 `readback_geometry_verified`。
