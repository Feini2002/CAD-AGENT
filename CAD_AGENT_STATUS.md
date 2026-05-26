# 通用 CAD Agent 开发包当前进展

最后更新：2026-05-26

本文是当前进展页，只保留“现在到哪、最近证据、风险边界、恢复开发怎么问”。压缩前完整版本已归档到 `docs/history/root-md-full-snapshot-2026-05-26/CAD_AGENT_STATUS.md`。

## 当前阶段摘要

```text
Phase O-V 非 CAD 主线已完成
系统层安全补强与自检已完成
本地 CAD regression manifest / strict runner 已建立
complex CAD smoke 已纳入默认 regression manifest
能力证明 next：V-PROOF-00-REGISTRY-SCHEMA；代码轨 next：LCAD-10.1-NEG-FIXTURES（见 docs/planning/任务清单.md §3~§5）
A/B/C/D 四条优化路线均已收口或进入 LCAD 尾项；工装为 Scene Product Alpha，非完整 Scene Product
执行台账：docs/planning/任务清单.md
```

最近完成的关键工作：

- `LCAD-01-REGRESSION-MANIFEST`：新增 CAD regression manifest schema、默认 manifest、loader 校验和 metadata 输出。
- `LCAD-02-STRICT-MATRIX-RUNNER`：支持 `--case` selected case、默认 all case、`--strict` 严格别名和统一 rollup。
- `complex_cad_smoke`：在 `CODEX_PREVIEW` 绘制混合测试图形，并按 created handles 定向回读；已加入默认 manifest。
- `DEMAND-01-DEMAND-SIDE-AGENT-SUITE`：新增需求侧角色 Agent 数据层、跨场景 demand benchmark 和 `demand_case` 分派，用需求侧持续暴露 Core 能力缺口。
- `OBJ-DETAIL-01-COMPONENT-PLAN`：把“精细餐桌 / 办公椅”等需求沉淀为对象组件级 `CAD_PLAN` 展开能力，table / bed / chair / sofa / desk 已有 non-CAD 验证。
- Core / Scene 口径重校准：Scene Alpha / Beta 不能写成 Scene Product。
- 根目录 MD 精度压缩：旧完成记录保留到 `docs/history/root-md-full-snapshot-2026-05-26/`，根目录回到短摘要。
- `LCAD-03` 已收口：`cad_session_guard`、`preview_only_audit`、`write_guard`、`created_handle_scope` 已接入 readback / probe / validation 门禁。
- `A-LCAD-04-TO-06-SMOKE-AND-PLAN-MATRIX`：`primitive_matrix`、`cad_plan_fixture_suite`、3 个 regression fixture、local manifest 7 case；focused 单测 23 tests OK（no-CAD）。
- `D-SYMBOL-01-SPEC-SCHEMA`：`symbol_spec` / `symbol_graph` schema、registry、`core/symbol_engine` 语义门禁（禁止 outline-only `symbol_readable`、bbox fallback 须显式声明）；17 tests OK。
- `D-SYMBOL-02-PRIMITIVES`：`core/symbol_engine/primitives.py`、`draw_symbol_glyph` CAD_PLAN intent；desk 示例 validate + dry-run；12 symbol tests OK。
- `D-SYMBOL-03-ARCHETYPE-GRAMMAR`：`core/symbol_engine/archetypes.py`、6 类 archetype 必备部件/位置约束、6 个 `examples/symbol_specs/*`；18 symbol tests OK。
- `D-SYMBOL-04-OBJECT-TO-SYMBOL`：`core/symbol_engine/object_to_symbol.py`；table/desk/chair/sofa/bed/cabinet → archetype；counter/elevation 显式 fallback；11 tests OK。
- `D-SYMBOL-05-READABILITY-GATE`：`symbol_readability_report` 区分 5 种可读性状态；明确 `geometry_verified=false`；11 tests OK。
- `D-SYMBOL-06-CAD-READBACK-SMOKE`：`execute_plan` 支持 `draw_symbol_glyph`；`symbol_glyph_cad_smoke` desk 样本 readback；5 tests OK（FakeCad `geometry_verified`；真实 CAD 需本机 smoke）。
- `D-SYMBOL-07-BLOCK-FALLBACK-POLICY`：`resolve_symbol_render_resolution` + 四级 fallback evidence + `detect_silent_degradation`；6 tests OK。
- `B-ORCH-01-REQUEST-CONTEXT`：`REQUEST_CONTEXT` schema + `evaluate_request_gate`；缺输入 blocked；6 tests OK。
- `B-ORCH-02-SCENE-REGISTRY`：`scene_registry.json` + `load_scene_registry`；7 tests OK。
- `B-ORCH-03-ACTIVATION-POLICY`：`evaluate_scene_activation` + manifest/触发词/追问；7 tests OK。
- `B-ORCH-04-WORKFLOW-DISPATCH`：`orchestrate_request` 分派至现有 Core workflow；7 tests OK。
- `B-ORCH-05-ROUTE-AUDIT-REPORT`：`route_audit_report` schema + `build_route_audit_report`；`orchestrate_request` 写入 audit JSON；4 tests OK。
- `C-CFIT-01-SCOPE-AND-SUBSCENES`：`SCOPE.md` + `subscenes.json`（开放办公 / 会议室 / 前台）；明确不做完整施工图；边界扫描通过；5 tests OK。
- `C-CFIT-02-OBJECT-CATALOG`：`object_catalog.json`（14 项）+ `commercial_fitout_catalog.py`；工位组 bundle → desk+chair；layout 可读；5 tests OK。
- `C-CFIT-03-BLOCK-MAPPING`：受控 fitout 块库 + mapping；`FITOUT_*` 块名 allowlist；找不到块回退 `OBJECT_SPEC`；7 tests OK。
- `C-CFIT-04-MICRO-SCENE-BENCHMARK`：`commercial_fitout_micro_scene_benchmark.json`（8 cases）；失败 case 均 `blocked_expected_non_cad`；6 tests OK。
- `C-CFIT-07-PRODUCT-BOUNDARY-ROLLUP`：`product_alpha_boundary.json` + 状态页保守口径；5 tests OK。**C 路线已收口。**
- `LCAD-07-BLOCK-ATTRIBUTE-HATCH`：`cad_block_attribute_hatch_boundary.json`；12 tests OK。
- `LCAD-08-PROJECT-SAMPLE-CAD`：`output/validation_runs/project-sample-cad-rollup-real`；2/2 `geometry_verified`。
- `LCAD-09-SCENE-COMPOSITION-CAD`：用户会话 `composition_cad` 3/3 `geometry_verified`（40 handles）。
- 用户会话全量补验：`output/validation_runs/user-cad-full-verify-20260526/`。
- **路线 F 能力证明体系**已登记：`capability-proof-architecture.md` + 一键推进 §3（V0~V7 共 37+ 任务包）；RCAD 为 P1 执行层。
- `docs/planning/任务清单.md`：§3 V-PROOF / §4 代码 / §5 RCAD；「能力证明」→ §3 首项 next。

## 已确认事实

- 本仓库是通用 CAD Agent Core Lab，不绑定当前 DWG、当前家装图或当前电脑。
- 唯一主计划是 `CORE_RESTRUCTURE_PLAN.md`；状态页和 changelog 不承载独立下一步。
- 后续优先级、Phase 顺序、待办和退出标准只以唯一 `PlanMD` / `CORE_RESTRUCTURE_PLAN.md` 为准。
- 自然语言真实落图前必须先结构化为 `CAD_PLAN` 或明确绘图意图，并跑 validate / dry-run。
- 真实 CAD 结论必须基于 `CODEX_PREVIEW` 输出、created handles 定向回读和 `geometry_verified`。
- no-CAD benchmark、fake driver、截图和浏览器 PNG 只能作为非 CAD 或视觉辅助证据。
- 面向用户生产的 CAD 输出默认不加中文 / 英文文字标注，也默认不加尺寸标注；文字和尺寸能力保留，只在明确需求或能力测试时启用。

## 最近验证记录

| 验证 | 结果 |
| --- | --- |
| complex CAD smoke real | `output\validation_runs\complex-cad-smoke-real-final`，`status=geometry_verified`，`created_handle_count=23` |
| complex CAD smoke no-CAD | `output\validation_runs\complex-cad-smoke-no-cad`，`status=deferred` |
| full strict CAD matrix | `output\validation_runs\complex-cad-regression-strict-final`，`selected_case_count=4`，`geometry_verified_case_count=7`，`created_handle_count=113` |
| demand-side agent benchmark | `examples\benchmarks\demand_side_agent_benchmark.json`，10/10 non-CAD pass；精细餐桌和办公椅已走 `object_detail_spec`；输出在 `output\test_artifacts\benchmarks\demand_side_agents_manual_after_detail` |
| demand-side real CAD check | `output\validation_runs\demand-side-agent-cad-real-20260526`，10/10 cases `geometry_verified`，`created_handle_count=100`；截图 `demand-side-agent-cad-window-focused.png` |
| LCAD-02 selected no-CAD | `output\validation_runs\lcad-02-selected-project-sample-no-cad`，只跑 `project_sample_cad_check` |
| LCAD-02 strict all CAD | `output\validation_runs\lcad-02-strict-all-cad`，`geometry_verified_case_count=6`，`created_handle_count=90` |
| LCAD-01 manifest no-CAD | `output\validation_runs\lcad-01-manifest-no-cad`，deferred gate 正常 |
| LCAD-01 strict CAD smoke | `output\validation_runs\lcad-01-manifest-cad-smoke`，受控测试会话通过 |
| user CAD full verify | `output\validation_runs\user-cad-full-verify-20260526`，manifest strict 7/7 几何 verified；汇总 `user_cad_full_verify_summary.json` |
| composition CAD | `composition_cad` 3/3 `geometry_verified`；40 handles |
| LCAD-08 project rollup | `sample_blank_shell` 20 + `commercial_fitout_sample` 12 handles |

## 当前可用链路

非 CAD blank-shell pipeline 当前可串联：

```text
SHELL_MODEL
-> PROJECT_MODEL
-> CIRCULATION_MODEL
-> FUNCTION_ZONE
-> placements
-> LAYOUT_PROPOSAL
-> DESIGN_PROPOSAL
-> CAD_PLAN
-> dry-run
-> VERIFICATION_REPORT(unverified)
```

真实 CAD 验证当前优先入口：

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_local_cad_regression.py --strict --output-dir output\validation_runs\manual-local-cad-regression
& $py scripts\run_cad_validation.py --output-dir output\validation_runs\manual-cad-check
```

## 当前进度估算

```text
总进度：约 86%（工程节奏）
Core 底座开发进度：约 96%（工程完备度）
Agent 多场景实现进度：约 52%
CAD 证明覆盖率：待 V-PROOF-02（定性 <10%）
展示等级 Ladder：约 L3~L4 边缘；无 L5
```

工程节奏 ≠ CAD 证明覆盖率。Scene Alpha / Beta 不直接计为 Scene Product 完成。

## 当前最重要缺口

| 缺口 | 影响 | 归属 |
| --- | --- | --- |
| **无能力登记表** | 无法回答「哪些能力已 CAD 证明」 | `V-PROOF-00`~`02` |
| **CAD 证明覆盖率低** | 烟囱 verified 不能代表全 intent/对象/符号 | `V-PROOF-10`~`45` |
| 负向安全未系统化 | 非法路径/图层/block、保存与删除防线待 `LCAD-10` | `LCAD-10` + `V-PROOF-50` |
| 证据趋势未机器可读 | 覆盖率与历史索引 | `V-PROOF-71`（吸收 LCAD-11） |
| hatch COM 仍 deferred | 不能声称 hatch 全面 verified | `LCAD-07` 边界 |
| 全量 `run_cad_validation` 非几何门禁 | Pillow/截图/unit_tests 可能 fail，与几何 readback 分离 | CAD 验证 |
| 真实项目 DWG / 公司块库 | 仅脱敏样本与受控块，不能扩大为任意项目 | 真实项目验收 |
| office / residential / restaurant Scene Product | 仍为 Alpha/Beta | 各场景产品包 |
| commercial_fitout 非完整产品 | Scene Product Alpha；单样本、受控块库 | C 路线后续 |
| 需求侧 Agent 仍是测试层 | 角色表为开发期脚手架 | Demand-side |
| 自动读图依赖人工确认 | 不能替代确认后的 `SHELL_MODEL` | Drawing Read |
| created handles 历史实体排除 | before-after 快照仍不足 | LCAD 扩样 |

## 恢复开发时怎么问

查看状态：

```text
读取 AGENTS.md 和 CORE_CONTEXT_BRIEF.md，告诉我 CAD Agent 当前开发状态和下一步建议。
```

执行主计划：

```text
读取 CORE_RESTRUCTURE_PLAN.md。若继续当前队列，默认从 LCAD-10-NEGATIVE-SAFETY 开始。
```

选择优化路线：

```text
读取 CORE_RESTRUCTURE_PLAN.md 的“系统优化路线拆分”，从 A、B、C、D 中选择本轮优先路线。
```

盘点剩余任务：

```text
读取 docs/planning/任务清单.md，按“当前推进队列”的第一个未完成最小包继续推进。
```
