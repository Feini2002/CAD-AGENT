# Core Status

最后更新：2026-05-26

本文是通用 CAD Agent Core Lab 的能力状态页，只回答“当前能力成熟到哪里、证据是什么、缺口是什么”。长历史已归档到 `docs/history/root-md-full-snapshot-2026-05-26/CORE_STATUS.md`；计划入口只看 `CORE_RESTRUCTURE_PLAN.md`。

## 状态口径

| 状态 | 含义 |
| --- | --- |
| `alpha_ready_non_cad` | 非 CAD 链路已有稳定入口、测试和基线证据 |
| `alpha_verified_cad` | 有有限真实 AutoCAD 落图、截图辅助、created handles 回读和 `geometry_verified` |
| `prototype` | 有最小实现或脚本原型，但接口、样本或验证仍需增强 |
| `blocked_by_cad` | 仓库入口存在，但完成声明依赖真实 CAD 证据 |
| `scaffold` | 目录、文档或数据壳已建立 |
| `not_started` | 仅在计划中定义 |

## 当前总状态

```text
Core 底座：较厚 Alpha 原型，有限真实 CAD verified 样本可用
Scene Alpha：office / residential / restaurant 已完成壳层验收
Scene Beta：office / residential / restaurant 有 non-CAD beta benchmark
Scene Product：office / residential / restaurant 仍为 Alpha/Beta
commercial_fitout：Scene Product Alpha（C-CFIT-01..07 已收口；非完整工装产品）
能力证明 next：V-PROOF-00-REGISTRY-SCHEMA；代码轨 next：LCAD-10.1-NEG-FIXTURES（见 docs/planning/任务清单.md）
```

当前关键证据：

| 证据 | 摘要 |
| --- | --- |
| commercial_fitout micro-scene benchmark | `commercial_fitout_micro_scene_benchmark.json` 8 cases（4 pass + 4 blocked）；`tests.core.test_commercial_fitout_layout_failure` + benchmark suite 6 tests OK |
| commercial_fitout block mapping | `block_mapping.json` + `commercial_fitout_block_library.json`；`resolve_catalog_object_render`；禁止任意块名；7 tests OK |
| commercial_fitout object catalog | `capabilities/object_catalog.json`；14 catalog 项 → `OBJECT_SPEC`；`object_specs_for_subscene` 可喂 layout；5 tests OK |
| commercial_fitout product alpha boundary | `product_alpha_boundary.json`；可声明 / 不可声明 / 下一阶段差距；`product_alpha_status=product_boundary`；5 tests OK |
| commercial_fitout scope | `agents/commercial_fitout/SCOPE.md` + `subscenes.json`；三子场景 + 不做完整施工图；`tests.agents.test_commercial_fitout_scope` 5 tests OK |
| project sample CAD rollup (LCAD-08) | `output/validation_runs/project-sample-cad-rollup-real`；2/2 samples `geometry_verified`；handles 20+12 |
| commercial_fitout sample CAD smoke | 确认后 3× `draw_object`；rollup 真实 CAD verified（12 handles） |
| route audit report | `build_route_audit_report` + `route_audit_report.schema.json`；记录 workflow 选择、场景启用、证据与 deferred；`tests.core.test_route_audit_report` 4 tests OK |
| workflow dispatch | `orchestrate_request` + `workflow_routes.json`；non-CAD 全链路 / symbol glyph 经中控；7 tests OK |
| scene activation policy | `evaluate_scene_activation`；默认 `no_scene`；ambiguous → clarification；7 tests OK |
| scene registry | `examples/orchestrator/scene_registry.json`；7 scenes；`load_scene_registry`；7 tests OK |
| request context gate | `evaluate_request_gate`；缺输入 / 待澄清 / 禁 CAD 时 blocked；`tests.core.test_request_context` 6 tests OK |
| symbol fallback policy | `resolve_symbol_render_resolution`；block/symbol/component/bbox/deferred 分层 evidence；`tests.core.test_symbol_fallback_policy` 6 tests OK |
| symbol glyph CAD smoke | FakeCad + 真实 AutoCAD：`user-cad-full-verify-20260526/symbol-glyph-smoke` desk glyph verified |
| user CAD full verify | `output/validation_runs/user-cad-full-verify-20260526/`；manifest strict 7/7 几何 verified；94 handles |
| composition CAD (LCAD-09) | `composition_cad` 3/3 cases `geometry_verified`；40 handles |
| cad plan fixture suite real | 用户会话 3/3 fixture `geometry_verified` |
| block / attribute boundary | `cad_block_attribute_hatch_boundary.json`；hatch deferred |
| complex CAD smoke | `output\validation_runs\complex-cad-smoke-real-final`，`status=geometry_verified`，`created_handle_count=23` |
| full strict CAD matrix | `output\validation_runs\complex-cad-regression-strict-final`，`selected_case_count=4`，`geometry_verified_case_count=7`，`created_handle_count=113` |
| demand-side agent benchmark | `examples\benchmarks\demand_side_agent_benchmark.json`，10 个需求 case 覆盖 6 个场景，non-CAD pass |
| demand-side real CAD check | `output\validation_runs\demand-side-agent-cad-real-20260526`，10/10 cases `geometry_verified`，`created_handle_count=100` |
| object detail benchmark | `object_detail_spec` 已覆盖 table / bed / chair / sofa 组件级 plan；精细餐桌为 5 个 CAD_PLAN，办公椅为 6 个 CAD_PLAN，并已随 demand-side real CAD check 回读 |
| LCAD-01 | regression manifest、manifest metadata、no-CAD pass、受控真实 CAD smoke |
| LCAD-02 | selected case runner、`--strict` alias、strict all CAD pass |
| LCAD-04~06 | primitive matrix、`cad_plan_fixture_suite`（3 fixture）、manifest 7 case；no-CAD / fake-driver 单测通过 |
| no-CAD gates | 可证明 deferred / safety gate，不证明几何准确 |

## 当前进度估算（三口径）

| 指标 | 粗估 | 含义 |
| --- | --- | --- |
| **工程完备度** | Core ≈ 96%，总 ≈ 86% | schema、runner、pytest、non-CAD benchmark |
| **CAD 证明覆盖率** | **待 V-PROOF-02 首算**（定性 **<10%**） | `cad_capability_registry` 中 `verified` / 总行数 |
| **展示等级 Ladder** | 最高约 **L3~L4 边缘** | 回答「能画多厉害」；见 `capability-proof-architecture.md` |

```text
总进度：约 86% = 96% * 0.70 + 52% * 0.30（仅工程节奏）
Agent 多场景实现进度：约 52%
```

**禁止**用工程完备度 96% 代替 CAD 证明覆盖率。Core 已有 LCAD manifest、用户会话 strict 补验等烟囱证据，但能力登记表尚未建立（`V-PROOF-00` pending）。hatch、公司块库、任意 DWG 仍不足。`commercial_fitout` 为 Scene Product Alpha。

## 能力矩阵

| 能力 | 状态 | 当前依据 | 主要缺口 |
| --- | --- | --- | --- |
| CAD execution | `alpha_verified_cad` | baseline、受控 block alpha、组合样例和 complex smoke 已有真实 CAD readback | 更多 `CAD_PLAN`、真实项目、公司块库 |
| CAD COM capability probe | `alpha_verified_cad` | line / circle / arc / polyline / text / dimension / bbox / layer / handle 回读已有证据 | attribute、hatch、选择集、复杂实体 |
| preview safety | `alpha_verified_non_cad` | snapshot、audit、write_guard、created_handle_scope 已机器可读 | 真实 CAD 会话下全链路复验 |
| validate / dry-run | `alpha_ready_non_cad` | `scripts/validate_plan.py`、`scripts/dry_run_plan.py` 和 core 入口稳定 | 批量 fixture 和失败隔离 |
| local CAD regression | `alpha_verified_cad` | manifest 7 case；用户会话 strict 7/7 几何 verified | LCAD-10 负向安全、LCAD-11 趋势汇总 |
| render preview | `alpha_verified_cad` | AutoCAD 窗口级截图和 bbox 聚焦可用 | 截图仍只是视觉辅助 |
| entity readback | `alpha_verified_cad` | created handles 定向回读和 evidence contract | before/after snapshot、更多实体 |
| schemas / registry | `alpha_ready_non_cad` | core schema 已纳入 registry 和 invalid fixture | 更多真实项目正反例 |
| blank-shell pipeline | `alpha_ready_non_cad` | shell -> project -> circulation -> zones -> placements -> proposal -> CAD_PLAN -> dry-run | 复杂几何、自动读图、真实项目样本 |
| object / composition | `alpha_verified_cad` | 常见对象和组合样例可转 CAD_PLAN；table / bed / chair / sofa / desk 可展开组件级 CAD_PLAN；demand-side 10 case 已真实 CAD readback；默认不落文字 / 尺寸标注 | 更多复杂对象、真实块库、属性块、更精确家具符号 |
| block engine | `alpha_verified_cad` | 受控 `CODEX_TEST_BLOCK_001` + attribute probe；LCAD-07 边界 rollup | 公司块库、任意块名、hatch readback |
| drawing analysis | `prototype` | entity summary、geometry candidates、manual shell confirmation | 自动 DWG/PDF 空壳识别未闭环 |
| proposal engine | `prototype` | 多候选比较、用户确认 schema、partial replan 原型 | 真实交互和设计策略 |
| scene agents | `alpha_shell / beta_non_cad` | office / residential / restaurant：Alpha/Beta non-CAD | Scene Product 尚未开始 |
| commercial_fitout agent | `scene_product_alpha` | C-CFIT-01..07；边界 rollup + 单样本 readback | 多项目样本、真实 AutoCAD、公司块库、全子场景 CAD |
| demand-side role agents | `scaffold / benchmark_non_cad` | `agents/demand_side/role_agents.json` 12 个角色；`demand_case` benchmark pipeline | 仍是开发期需求脚手架，不是自动用户代理或真实 CAD 产品闭环；能力沉淀后可清理角色表 |

## 近期关键风险

- **工程代码量大 ≠ CAD 证明覆盖率高**；须推进路线 F（`V-PROOF-00`~`02`）建立可机器读的覆盖率。
- 不能把有限 `geometry_verified` 样本扩大为任意真实项目图纸、块库、属性块、hatch 或任意 CAD_PLAN 全部准确。
- `ActiveDocument guard` 尚未落成硬门禁，是真实 CAD 安全层下一优先级。
- 场景层：office / residential / restaurant 仍是 Alpha / Beta；**commercial_fitout 为 Scene Product Alpha，不是 Scene Product**。
- 截图、浏览器 PNG、`render_preview.py --check` 均不能替代 created handles readback。
- 根目录 MD 已压缩；追溯旧细节时看 `docs/history/root-md-full-snapshot-2026-05-26/`，不要把历史流水重新复制回根目录。

## 计划入口

后续优先级、Phase 顺序和退出标准只以 `CORE_RESTRUCTURE_PLAN.md` 为准。本文只维护能力矩阵、成熟度、证据路径和能力缺口。
