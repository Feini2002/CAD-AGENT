# CAD Agent 问题与修复记录

本文现在只保留活跃风险和高频教训。压缩前完整问题库已归档到 `docs/history/snapshots/root-md-2026-05-26/CAD_AGENT_ISSUES.md`。

## 当前活跃风险

| 风险 | 当前影响 | 处理口径 |
| --- | --- | --- |
| 活跃入口 MD 过长 | 旧完成流水会撑大每轮上下文，稀释当前主线 | PlanMD、任务清单、Core Status、current status 只保留控制面；旧记录查 `docs/history/snapshots/finished-architecture-2026-05-28/` 和 `docs/planning/archive/`；`run_doc_governance_audit.py` 校验体量预算 |
| 场景 Alpha / Beta 被误读为 Scene Product | 可能误以为工装、办公、住宅、餐饮 Agent 已产品化 | 统一四级成熟度；Scene Product 必须有真实项目样本、图块 metadata、真实 CAD smoke、用户确认流 |
| 真实 CAD 校验样本不足 | 不能证明任意项目 DWG 或任意 `CAD_PLAN` 几何准确 | 继续推进 §5 `RCAD-22+` 与 §3 `V-PROOF` 链式回写 |
| ActiveDocument / guard 仍需真实会话复验 | `LCAD-13/14` 已有 snapshot 与 strict guard 包装，但仍需更多真实 CAD 场景确认 | 优先用 `RCAD-21/22` 和后续真实 CAD smoke 扩样，不把 guard-only 当几何 verified |
| no-CAD deferred 被误读 | 顶层 pass 可能被误写成真实 CAD verified | 必须区分 `deferred`、`not_verified_without_cad_readback`、`geometry_verified` |
| 截图被误当几何证据 | 视觉辅助不能证明尺寸、图层、handle 和 bbox 准确 | 几何声明必须看 created handles readback |
| 路径边界回归 | runner 新增参数时可能越界读写 | 复用 `core.path_safety`，真实 CAD 连接前先做路径预检 |
| Schema 未登记 | schema 文件可能存在但 validator 不知道 | 新 schema 必须同步 registry、example、invalid fixture 和 tests |
| Markdown 进度漂移 | 表 A/B/C、RCAD 烟囱和 coverage JSON 容易被旧快照覆盖 | 表 C 以 `output/validation_runs/capability-lab/cad_capability_coverage.json` 为准；任务 next 以 PlanMD + 任务清单同步为准 |
| guard / negative 行误升 showcase | 安全守卫或负例拦截会被误算成几何能力，抬高表 C | negative / guard registry 行必须保持 `smoke`；只证明 guard-only，不得写成 `geometry_verified` / `showcase` |
| 普通回复表格噪声 / 状态查询漏报表 C | 普通交付若默认带表，会淹没用户真正关心的结论；但状态查询若漏表 C，又可能混淆真实 CAD 实力 | 普通最终回复默认不附进度表；只有用户点名开发状态查询、进度、完整状态、交接、审计、表 A/B/C、表 C 或真实 CAD 实力时才展开表格，并先报表 C 主指标 |
| 结构合并误伤边界 | 为减少文件数而合并 CLI / safety / evidence / CAD runner，会破坏可审计入口 | 按 `struct_merge_keep_rules.md` 执行；每个 `STRUCT-MERGE-xx` 只处理 1-3 组候选，必须 focused tests + repo audit |
| writeback 不识别 showcase 行 | registry 行从 verified/smoke 升到 showcase 后，旧绑定逻辑可能把它当 unsupported claim_level | 绑定类写回应把 showcase 视为“保留 evidence、只追加来源”的已验证类行；已有 RBLOCK-07 回归测试覆盖 |
| 文档迁移断链 | 大量 Markdown 移动后，旧路径、handoff、表 C 数字和新人入口可能漂移 | 旧根路径保留 stub；`output/validation_runs/**` 不移动；新增 `run_doc_governance_audit.py` 做链接、主从、表 C 和 handoff 检查 |
| coverage 证据路径缺失未成硬门 | coverage JSON 已统计 `report_path_missing`，但当前仍以 registry claim_level 计算表 C | 表 C 汇报必须同时看 `evidence_path_audit`；后续若把缺失路径改成硬门，需要先补齐历史证据路径，避免误降级 |
| 历史 verified/showcase 证据不满足新硬审计 | 新增 hard audit 后，旧报告可能缺 `checks`、`actual.created_handles`、`actual.entities` 或实际文件路径 | 新一轮表 C writeback 先过 `run_table_c_evidence_gate.py`；旧证据债另开补齐包，不用截图或旧 coverage 直接掩盖 |

## 最近修复教训
### Visual contract 不能只检查字段，必须检查证据文件

日期：2026-05-28

现象：round12 的 `round12_visual_parts.json` 已声明 `style_target`，但对应 `expected/style_target_2seat.png` 原本不存在；补齐时又临时生成了示意图，仍不是来自真实参考截图；`round12_style_compare.md` 也曾停在 `pending execution` 模板态，却没有被 delivery gate 阻断。
影响：Agent 容易把“字段存在”或“有一张生成目标图”误当成“视觉契约闭环”，导致 `delivery_allowed=true` 与真实参考证据状态矛盾。
修复 / 计划：`run_training_round_gate.py` 的 visual contract stage 现在会解析 `visual_parts` 并检查 `style_target` 必须是 case 内真实文件，且 `style_target_source` 必须是 `reference_crop` / `user_reference` / `reference_screenshot`；generated target、缺少真实截图来源、source image 缺失都会阻断。delivery stage 仍要求 `style_compare` 存在且不能包含 pending/未勾选模板标记。
以后规则：视觉契约类字段只算索引，不算证据；证据必须能在仓库中解析、打开或被 gate 检查。reference-match 任务不得把 Agent 生成图作为 style target 交付证据。
相关文件：`core/training/learning_promotion.py`、`projects/residential_sofa_2seat_20260528/expected/style_target_reference_crop.png`、`projects/residential_sofa_2seat_20260528/runs/round12_style_compare.md`


### 机器审计绿后仍要做视觉自检

日期：2026-05-28

现象：round12 初版 `visual_parts` 落图机器审计已过，但同屏截图显示座垫比例像上下四个大矩形，和参考沙发“薄座垫 + 高靠背”的款式仍有差距。

影响：如果只看 `geometry_audit.json`，会把“部件齐全但款式不准”的图交给用户，继续复现早期机器虚绿问题。

修复 / 计划：delivery gate 仍要求 `roundN_preview.png` + Agent 自检；`part_renderer.py` 增加薄座垫/高靠背比例，并用测试约束座垫高度和靠背高度。AutoCAD COM 图层访问也缓存一次，避免高频 `ensure_layer` 触发 `RPC_E_CALL_REJECTED`。

以后规则：训练案例要把“机器审计通过”和“可请用户验收”分开；截图自检发现款式问题时先 Repair，不直接交付。

相关文件：`projects/residential_sofa_2seat_20260528/runs/part_renderer.py`、`tests/core/test_visual_parts_case_contract.py`、`core/cad_io/autocad_com.py`

### 活跃文档要有体量预算，done 明细进 archive

日期：2026-05-28

现象：`CORE_RESTRUCTURE_PLAN.md`、`docs/planning/任务清单.md`、`CORE_STATUS.md`、`docs/status/current.md` 已经声明“不承载长历史 / 只做控制面”，但仍保留大量已完成包明细，默认上下文像施工现场。

影响：后续 Agent 每轮都要扫旧 Phase、旧 done 表和旧状态快照，容易误读 next、混淆表 A/B/C，或把历史包当作当前待办。

修复 / 计划：新增 active doc size budget 检查，活跃入口超预算时 `run_doc_governance_audit.py` 报 `active_doc_over_budget`；瘦身前全文迁入 `docs/history/snapshots/finished-architecture-2026-05-28/`，done 台账索引迁入 `docs/planning/archive/`。

以后规则：完成包明细只进 archive / history / handoff；活跃文件只保留口令、当前值、路由、风险和证据入口。

相关文件：`core/maintenance/doc_governance.py`、`docs/planning/archive/README.md`

### 表 C writeback 必须先过硬证据和视觉复盘门

日期：2026-05-28

现象：coverage JSON 已有 `evidence_path_audit`，但旧流程默认仍按 registry `claim_level=verified/showcase` 计算表 C；截图也容易只作为“看起来画了”的辅助物，未进入 writeback 硬门。

影响：后续 Agent 可能在证据路径缺失、旧报告缺 created handles/checks，或截图复盘失败时仍继续回写 registry，从而让表 C 继续漂移。

修复 / 计划：新增 `run_capability_evidence_audit.py`、`run_visual_cad_review.py`、`run_table_c_evidence_gate.py`；截图复盘失败时 `writeback_allowed=false`，coverage 可通过 `--require-evidence-audit-pass` 启用硬审计。首次审计现有 registry 为 131 audited / 59 pass / 72 fail，旧证据债后续另开补齐包处理。

以后规则：任何新表 C 推进包在 registry writeback 前，必须有 `geometry_verified` / `cad_capability_verified` 证据、硬审计通过、视觉复盘通过；截图仍不得替代 created-handle readback。

相关文件：`core/verification/capability_evidence_audit.py`、`core/verification/visual_cad_review.py`、`core/verification/table_c_evidence_gate.py`、`docs/verification/table_c_evidence_gate.md`

### 结构治理先立规则，再动文件

日期：2026-05-28

现象：`STRUCT-AUDIT-01` 显示仓库已有 505 个 Python 文件、56,247 行；其中很多脚本很薄，但它们同时承担用户可执行命令、交接证据路径或兼容入口。若只按“文件小 / 行数少”合并，容易删掉真正有操作价值的入口。

影响：盲目合并会让后续 CAD 补验、no-CAD benchmark、registry writeback 和状态交接难以复跑；尤其 `scripts/*.py`、`core.path_safety`、`evidence_contract`、CAD COM runner 不能为了少文件数合并。

处理 / 结果：新增 `docs/verification/struct_merge_keep_rules.md` 与 `docs/verification/struct_merge_candidates.md`，把候选分为应合并、应拆分 / 抽公共层、应保留、观察 / 延后；首批只建议 `drawing_policy.py` 这种低风险内部细节进入 `STRUCT-MERGE-01`。

后续结果：`STRUCT-MERGE-01` 已把 `drawing_policy.py` 合并入 `templates.py`，并用 composition focused tests + repo audit 验证。该模式说明：低风险合并也必须先红灯、再最小实现、再写交接。

以后规则：结构整理必须先引用候选表和规则页；真实 CAD / 表 C / safety / evidence 边界默认保留，除非有 focused tests 和明确替代入口。

相关文件：`docs/verification/struct_merge_keep_rules.md`、`docs/verification/struct_merge_candidates.md`

### Registry 绑定逻辑必须跟随 claim_level 晋级

日期：2026-05-28

现象：`STRUCT-MERGE-01` 后跑全量 unittest 时，`tests.core.test_rblock_07_block_matrix_registry_rows` 两个测试失败：matrix sync 只 applied 4/5。根因不是 composition 合并，而是 `block.insert_block_alpha.matrix` 已经晋级为 `showcase`，`apply_block_matrix_registry_binding()` 仍只接受 `smoke`、`verified`、`deferred`。

影响：已晋级 showcase 的 registry 行会在后续 dry-run / no-CAD binding 复跑中被误判为 rejected，造成台账 / 证据刷新失败。

修复 / 结果：`apply_block_matrix_registry_binding()` 现在接受 `showcase`，并像 verified 行一样只追加 matrix source ref / notes，不覆盖既有 readback evidence。修复后 focused RBLOCK-07 9 tests OK，全量 864 tests OK。

以后规则：任何 registry 绑定 / writeback 逻辑新增 claim_level 判断时，必须同时考虑 `showcase` 的“高于 verified、不可降级、不覆盖 evidence”语义。

相关文件：`core/block_engine/block_matrix_registry.py`、`tests/core/test_rblock_07_block_matrix_registry_rows.py`

### 表 C 推进可能掩盖 CAD 画面没有变好

日期：2026-05-27

现象：用户查看 AutoCAD 截图后指出图块仍很简单，真实 CAD 能力观感约 5-10%，且两三天来视觉上没有明显进步。

影响：如果继续只推进 registry、coverage、RCAD 烟囱和 created-handle 回读，工程证据会变厚，但用户看到的 CAD 画面仍可能停留在矩形 smoke / 简单受控块阶段。

处理 / 结果：新增 `VCAD-01` 视觉表达 P0 包：`visual_cad_smoke` 绘制双线房间、门扇弧、两组工位、显示器/键盘、椅子、抽屉柜和工作区轮廓；真实 CAD 回读 54 handles，截图为 `output/previews/vcad-01-visual-office-corner.png`。随后新增 `VCAD-02` 视觉表达 P1 包：`visual_room_plan_smoke` 绘制分段双线墙、门窗、尺寸、文字、分区和更密家具，真实 CAD 回读 99 handles，截图为 `output/previews/vcad-02-visual-room-plan.png`。

以后规则：用户说“停止刷表 C / 推进 CAD 画面能力 / 图块太简单”时，优先做视觉表达包；最终汇报必须同时讲清楚视觉进步和表 C 不变，不能再用工程百分比替代 CAD 画面观感。

相关文件：`core/verification/visual_cad_smoke.py`、`scripts/run_visual_cad_smoke.py`、`core/verification/visual_room_plan_smoke.py`、`scripts/run_visual_room_plan_smoke.py`

### Fresh CAD evidence 不一定提升表 C 计数

日期：2026-05-27

现象：`V-PROOF-42-COMPOSITION-EXPAND` 真实 CAD 刷新 4 个 office composition case 后，registry writeback applied 4，但 coverage 机器值没有上升。

影响：如果只看“本轮跑了真实 CAD + applied 4”，容易误以为表 C 覆盖率必然提升；事实上这 4 个 capability 行此前已是 `verified`，本轮只是把 evidence path 刷新到新的 created-handle readback 报告。

处理 / 结果：明确记录 coverage 复跑值保持 `verified_count=112`、`showcase_count=25`、`cad_proof_count=137`、主指标 8.87%；任务台账可从 partial 到 done，但真实 CAD 实力百分比不虚报上涨。

以后规则：表 C 是否提升只看最新 `cad_capability_coverage.json`；registry writeback 的 applied_count 可能只是更新证据路径，不等于新增 verified/showcase 计数。涉及 `showcase` 行时还要避免默认 writeback 把 `showcase` 降成 `verified`。

相关文件：`scripts/run_composition_cad_registry.py`、`scripts/build_office_composition_writeback_batch.py`、`output/validation_runs/vproof-42-office-composition-expand-20260527-cad/composition_cad_registry_report.json`

### V-PROOF-41 真实 CAD 补验要区分沙箱 COM 不可见与真实 CAD 几何失败

日期：2026-05-27

现象：推进 `V-PROOF-41-BLOCK-CAD-MATRIX` 时，普通沙箱命令下 `scripts/run_block_alpha_beta_suite.py --connect-cad` 在创建 driver 前失败，报 `No active AutoCAD.Application instance is available`；同一会话中 CAD-MCP 可写 `CODEX_PREVIEW`，说明 CAD 本体可操作。
影响：这不是 001/002 几何失败，也不是 CAD_PLAN 失败，而是沙箱/权限边界导致 AutoCAD COM active object 不可见；若不区分，会把环境阻塞误判为绘图失败。
处理 / 结果：经用户允许在沙箱外访问已打开的 AutoCAD COM 后，重跑同一双块 suite 通过：`output/validation_runs/vproof-41-block-cad-matrix-20260527-cad/block_alpha_beta_summary.json` 为 2/2 `geometry_verified`，handles `61F` / `627` 均回读为 `block_reference`；`block.library.controlled_test_block_002` 已回写 verified。
以后规则：真实 CAD matrix 包必须把“active COM 可见性 / 权限边界”与“几何回读失败”分开记录；无 created-handle readback 时不得声称 `geometry_verified`，但沙箱内 COM 不可见时可请求合规提权复跑。
相关文件：`examples/plans/block_cad_matrix_vproof_41.json`、`scripts/run_block_alpha_beta_suite.py`

### Runner 内部相对路径要先归一到 project root

日期：2026-05-27

现象：推进 `V-PROOF-40` 时，`run_block_matrix_registry_sync.py --output output/...` 传入相对路径，内部直接对 `output_root.relative_to(project_root)` 求相对路径，导致 `ValueError`。

影响：证据已经可以生成，但 CLI 入口会因为路径形式失败，容易误判为 registry sync 或 block matrix 证据失败。

修复 / 计划：`run_block_matrix_registry_no_cad_sync()` 现在先把相对 output 解析到 project root 下，再进行 registry binding；新增 focused 回归测试覆盖相对 output。

以后规则：runner 接收 CLI 路径时，进入核心逻辑前应统一转换为 project root 内的绝对路径，再输出相对 evidence path。

相关文件：`core/block_engine/block_matrix_registry.py`、`tests/core/test_rblock_07_block_matrix_registry_rows.py`

### Hatch 已有受控 smoke，但不能扩大到任意填充

日期：2026-05-27

现象：`RCAD-06-HATCH` 已在真实 AutoCAD 会话中完成一组 ANSI31 矩形 hatch smoke，created handles 回读到 `hatch=1` 与 `polyline=1`，并把 `primitive.hatch` 从 `deferred` 回写为 `verified`。但该证据只覆盖受控闭合矩形边界、preview 图层和单一 hatch pattern。

影响：如果把这次 smoke 扩大理解为任意 hatch 已可用，会误报孤岛 hatch、复杂边界、正式图层填充、项目标准填充或任意 CAD_PLAN hatch 的几何准确性。

修复 / 计划：`docs/verification/hatch_com_deferred_boundary.md` 已改为同时记录 real COM verified 与 fake/no-CAD deferred 两层边界；最终口径固定为“受控 ANSI31 preview smoke 已 verified，任意 hatch 仍未证明”。

以后规则：hatch 能力扩样必须逐项增加 created-handle readback 证据；fake driver、no-CAD deferred、截图和顶层 pass 都不能替代真实 AutoCAD entity readback。

相关文件：`core/cad_io/autocad_com.py`、`core/verification/hatch_cad_smoke.py`、`docs/verification/hatch_com_deferred_boundary.md`

### RCAD 烟囱里也可能包含 non-CAD rollup

日期：2026-05-27

现象：`RCAD-28-BETA-EVIDENCE-ROLLUP` 属于 §5 CAD 补验台账，但其既有设计是 BETA-CAD-BLOCK 父包 evidence rollup，不连接 AutoCAD、不新增 created handles。若只看 RCAD 计数，很容易误以为 28/29 都是几何补验。

影响：RCAD 烟囱完成度会接近 97%，但表 C 主指标仍为 4.26%；把这个 rollup 当成真实 CAD `geometry_verified` 会再次混淆工程节奏、任务台账和真实 CAD 实力。

修复：为 `cad_beta_evidence_rollup` 补齐 `evidence_trend/cad_beta_evidence_rollup_trend.json`，并在测试中固定 `non_cad_only=true`、`geometry_verified_count=0`、`dry_run_valid_plan_only_count=5`。

以后规则：RCAD 台账状态可以说明补验包跑完，但是否提升真实 CAD 几何必须看 `geometry_verified_count`、created handles 和 registry/showcase 回写。non-CAD rollup 不提升表 C。

### 治理测试不要滞留旧进度断言

日期：2026-05-27

现象：推进 `RCAD-27` 的 no-CAD 兼容矩阵时，`baseline_cad_validation` 内的全量单测失败；根因不是 CAD 几何，而是 `tests/core/test_planmd_governance.py` 仍断言 `CORE_STATUS.md` 包含旧的 `94%`，当前状态页已更新为 `95%`。

影响：这类旧快照断言会把文档进度同步误报为 regression，阻塞真实 CAD 补验矩阵；如果只看顶层 fail，容易误判为 CAD runner 或几何链路坏了。

修复：将治理测试断言同步为当前 `CORE_STATUS.md` 的 `95%`，随后 no-CAD local regression 8/8 通过，真实 CAD strict 复跑 9/9 `geometry_verified_case_count`。

以后规则：状态页进度发生合法更新时，同步检查治理测试里的硬编码进度值；更好的后续方向是让测试验证“存在固定四进度口径与禁止混用声明”，而不是过度绑定某个历史百分比。

### block 旋转 bbox 不能用宽深互换近似

日期：2026-05-27

现象：`RCAD-24-BLOCK-ALPHA-BETA` 第一次真实 CAD 补验时，8 个 case 中 5 个通过，`beta_rotation_45`、`beta_rotation_90`、`beta_combined_transform` 失败；created handles 和 block reference 回读存在，但 bbox 检查不通过。

影响：如果继续沿用 dry-run 近似 bbox，会把旋转 block 的几何预期写错，真实 CAD 回读会持续失败；更危险的是，若放宽 bbox 检查，可能错把旋转几何当成已证明。

修复：`core/block_engine/block_placement.py` 改为围绕 insertion point 旋转 block 四角后计算外包框；`tests/core/test_block_engine.py` 与 `tests/core/test_block_alpha_beta_suite.py` 增加/更新对应验证。修正后真实 CAD 复跑 `RCAD-24` 8/8 `geometry_verified`。

以后规则：block / symbol / component 只要涉及旋转，bbox 预期必须按 CAD 实际变换计算；不得用“宽深互换”或非右角近似替代 created-handle readback 的几何断言。

相关文件：`core/block_engine/block_placement.py`、`core/verification/block_alpha_beta_suite.py`

### 诊断探针标注不能污染用户可见生成层

日期：2026-05-27

现象：用户在 AutoCAD 视口中看到大号 `CAD_CAPABILITY_PROBE` 文字和尺寸/箭头残留，容易判断为“生成图块仍然带标注”。回读证据显示最近的图块插入只创建 `block_reference`，但旧探针对象与当前生成结果混在同一 `CODEX_PREVIEW` 层，造成视觉污染。

影响：后续推进表 C 时，机器报告可能按 created handles 通过，但用户看到的 CAD 现场不干净，形成“证据通过、视口不可信”的落差。

修复：新增 `CODEX_DIAGNOSTIC` 诊断层，允许能力探针 / benchmark 在 preview-only 安全边界内验证文字和尺寸能力；探针几何仍写入 `CODEX_PREVIEW`，文字和尺寸写入 `CODEX_DIAGNOSTIC`，报告分开统计预览层与诊断层。诊断层写入必须显式 `layer_role="diagnostic"`，默认 preview 角色写诊断层会被 guard 拦截。

以后规则：用户可见生成结果默认纯几何。测试文字、尺寸、箭头、说明只属于诊断层或临时对象；截图和交付口径必须区分当前 created handles、预览层和诊断层，不得把诊断残留当成图块交付结果。

### 普通最终回复默认不附进度表，状态查询再展开表 C

日期：2026-05-27；更新：2026-05-28

现象：每轮交付强制输出完整表 A/B/C 后，信息量变大但思考价值下降，容易让真正关键的“本轮做了什么、有没有证据、真实 CAD 实力有没有变化”被表格淹没。

影响：后续 Agent 可能机械复制三表或精简表，造成普通问答里表格噪声过高；如果状态查询又为了省字数漏掉表 C 主指标，则工程进度 / RCAD 烟囱完成度仍可能被误读成真实 CAD 能力。

修复 / 计划：2026-05-27 先从完整三表改为 1 张精简进度表；2026-05-28 根据用户反馈继续收紧为：普通最终回复默认不附进度表、表单或表 A/B/C，只有用户点名开发状态查询、进度盘点、完整状态、交接、审计、表 A/B/C、表 C 或真实 CAD 实力时才展开表格。此变更只改展示口径，不重构 §3 / §4 / §5 的真实任务分母。

以后规则：无表格不是删除证据。普通回复仍要说清本轮完成、验证和风险；状态查询或真实 CAD 能力汇报必须以 coverage JSON、created handles 回读和 `geometry_verified` 为准，并先报表 C 主指标。handoff、状态页和能力模板保留完整证据结构。

### 表 A/B/C 数字必须以机器值和任务台账为准

日期：2026-05-27

现象：`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`docs/status/current.md` 与 `docs/planning/任务清单.md` 同时保留了 `0%`、`48.85%`、`49.24%`、`4.55%`、`4.35%` 等不同时间点快照，且 RCAD 烟囱也有 `21/29` 与 `22/29` 两套说法。

影响：后续 Agent 可能用旧 Markdown 数字覆盖最新机器报告，或把 RCAD / 工程进度误当成真实 CAD 实力。

修复 / 计划：收尾时复跑 `scripts/run_capability_coverage.py`，把表 C 同步为 `130/276 = 47.10%`、主指标 `4.35%`、最高 `L4`；把任务台账同步为 §3 `24/43`、§4 约 `42/55`、§5 `22/29`。

以后规则：表 C 一律以 `output/validation_runs/capability-lab/cad_capability_coverage.json` 为准；历史 changelog 数字只作为当时快照。任务 next 若冲突，先按 `CORE_RESTRUCTURE_PLAN.md` 的决策边界修正 `docs/planning/任务清单.md`，再汇报。

### 临时文件清理失败不应掩盖已完成的模型构建

日期：2026-05-27

现象：全量自检时，当前沙箱对 `tempfile` 创建的随机临时目录/文件可能返回 `PermissionError`，导致 `shell_confirmation.py` 在 `temp_path.unlink()` 清理阶段失败；此时 SHELL_MODEL 已经成功构建，失败点只是临时文件清理。

修复：`apply_shell_drawing_read_confirmation()` 保留原有临时 JSON round-trip，但在 finally 清理时捕获 `PermissionError`，避免把清理失败误报为业务转换失败。

以后规则：临时文件用于内部 round-trip 时，业务结果与清理结果要分层；清理失败可以记录或忽略，但不能覆盖已经完成的验证/转换结论。

### 真实 COM 写入守卫必须在 Add* 前触发

日期：2026-05-27

现象：负向安全复核发现 `AutoCADComDriver.draw_line()` 等方法曾在 COM `AddLine/AddCircle/...` 之后才调用 preview-layer guard；这会造成正式图层负向 case 虽然抛错，但实体可能已经被创建到当前 DWG。

修复：`AutoCADComDriver` 的 line / rectangle / circle / arc / polyline / text / dimension 写入均改为先执行 `_guard_preview_layer_write(layer)`，再调用 COM `Add*`；新增 `negative_cad_runner` 报告 no-handle/no-save/no-delete/no-formal-layer 证据。

以后规则：任何真实 CAD 写入入口都必须先做权限、图层、路径、ActiveDocument/snapshot 预检，再执行 COM 写入；负向 runner 的 `created_handles=[]` 和 modelspace delta 不能省略。

### 根目录 MD 历史权重过高

日期：2026-05-26

现象：旧 `CAD_AGENT_CHANGELOG.md`、旧 `CAD_AGENT_ISSUES.md`、`CORE_RESTRUCTURE_PLAN.md`、旧 `CAD_AGENT_STATUS.md` 等根文档曾持续累积已完成流水，每轮恢复上下文时噪声过高。

修复：创建 `docs/history/snapshots/root-md-2026-05-26/` 保存压缩前完整快照；根目录改为当前摘要、活跃队列、证据索引和风险边界。

以后规则：旧完成记录不要重新复制回根目录；需要追溯时展开 `docs/history/`。

### 场景成熟度口径容易误读

日期：2026-05-26

现象：已有 `office`、`residential`、`restaurant` 的 preferences、Scene Alpha 验收和 scene beta benchmark，容易被误读为具体场景 Agent 已完成。

修复：新增 `docs/architecture/core-scene-agent-boundaries.md`，统一 `Core 底座`、`Scene Alpha 壳层`、`Scene Beta 能力包`、`Scene Product 场景产品` 四级成熟度。

以后规则：没有真实项目样本、图块策略、真实 CAD readback 和用户确认流，不得称为 Scene Product。

### 本地真实 CAD 校验样本仍不足

日期：2026-05-26

现象：non-CAD 单测和 benchmark 较多，但真实 AutoCAD 用户会话下的 `geometry_verified` 样本仍有限。

修复 / 计划：唯一 `PlanMD` 已登记 `LCAD-01` 到 `LCAD-11`。当前 `LCAD-01`、`LCAD-02` 和 complex smoke 已完成，下一步推进 `LCAD-03`。

以后规则：任何新 CAD 能力没有 created handles readback 和 `geometry_verified` 时，只能写 deferred / non-CAD / fake-driver evidence。

### CAD 回归入口曾分散

日期：2026-05-26

现象：baseline validation、project sample check、composition check 曾经分散运行。

修复：新增 `core/verification/local_cad_regression.py` 和 `scripts/run_local_cad_regression.py`，支持 manifest、selected case、strict rollup 和 no-CAD deferred。

以后规则：进入下一阶段或做本地 CAD 回归时，优先跑 local CAD regression 矩阵。

## 不再高频展开的历史问题

以下问题仍可追溯，但不在根目录全文展开：

- 默认沙箱身份看不到用户会话 AutoCAD COM 活动对象。
- AutoCAD COM 点参数需要 `VT_ARRAY`。
- 顶层 validation pass 不能替代 readback `geometry_verified`。
- block alpha 失败路径必须先拒绝再写入。
- Windows / PowerShell 编码会影响中文路径和 JSON 输出。
- `sys.path` 注入、系统 temp、路径越界和 schema registry 缺口。
- blank-shell 早期几何、placement、zone、benchmark 和 workflow schema 问题。

完整条目见 `docs/history/snapshots/root-md-2026-05-26/CAD_AGENT_ISSUES.md`。

## 记录模板

新增问题按这个短格式写，避免再次膨胀：

```markdown
### 问题：一句话概括

日期：YYYY-MM-DD

现象：发生了什么。

影响：为什么危险。

修复 / 计划：已经做了什么，或下一步在哪里登记。

以后规则：后续如何避免。

相关文件：`path`
```
