# Phase R Rebirth Implementation Plan

状态：Phase R 执行剧本已细化  
最后同步：2026-05-26

> 本文是 Phase R 执行剧本，不是独立 PlanMD。优先级、待办和退出标准以根目录 `CORE_RESTRUCTURE_PLAN.md` 为准；本文只保留任务背景、拆单依据和执行参考。

## 执行边界

- Phase R 的目标是让下一轮通用底座开发更准，不是魔改系统。
- 当前系统仍是通用 CAD Agent Core Lab，不变成办公专用、工装专用或 CAD-MCP 专用项目。
- 场景 Agent 只做业务词汇、默认尺度、对象组合语义、候选排序权重和解释模板。
- Core 算法、CAD_PLAN、CAD 执行、截图、回读、验证、benchmark 总控必须留在 `core/`、`libraries/`、`examples/`、`tests/` 或 `docs/` 的对应位置。
- 本轮文档执行不改变功能成熟度百分比；后续只有形成可复验证据才调整进度。

## 证据状态词

| evidence_state | 含义 | 可以声称 | 不能声称 |
| --- | --- | --- | --- |
| `benchmark_pass_non_cad` | 非 CAD benchmark 跑通 | 结构化 pipeline / case 在无 CAD 下可复验 | 真实 CAD 几何准确 |
| `dry_run_valid_plan_only` | CAD_PLAN 校验和 dry-run 通过 | 计划结构和预演合法 | 实体已经画准 |
| `screenshot_captured_visual_only` | 截图已保存 | 有视觉辅助证据 | 几何已由截图证明 |
| `readback_geometry_verified` | 真实 CAD created handles 范围内回读通过 | 对该有限样本的几何准确有证据 | 任意 CAD_PLAN、真实块库或真实项目全量准确 |
| `blocked_expected_non_cad` | 失败样本按预期结构化 blocked / invalid | 系统能解释失败原因 | 系统能自动修复布局 |
| `deferred_cad_readback_required` | 需要真实 CAD 补验 | 当前有计划或 metadata | 当前已经 CAD 验证 |

报告中涉及无 CAD、dry-run 或截图时，必须显式写：

```json
{
  "geometry_accuracy": "not_verified_without_cad_readback",
  "screenshot_role": "visual_aid_only"
}
```

## R0-R6 总表

| 批次 | 目标 | 主要文档 | 状态 | 退出标准 |
| --- | --- | --- | --- | --- |
| R0 | 建立 Phase R 执行索引 | 本文 | `done_for_docs` | 有总表、任务编号、证据状态、同步清单 |
| R1 | CAD 能力契约 | `phase-r-cad-capability-contract.md` | `ready_for_implementation` | 图元和 block alpha 的 write-read-verify 契约清楚 |
| R2 | 图块库与制图标准路线 | `phase-r-block-library-roadmap.md` | `ready_for_implementation` | block metadata、OBJECT_SPEC、drawing standard profile 边界清楚 |
| R3 | 办公基础闭环 Alpha | `phase-r-office-benchmark-cases.md` | `partially_implemented_non_cad` | desk / chair / cabinet object cases 与第一条 office scene 可跑；微场景和失败样本仍需扩展 |
| R4 | Benchmark 与证据门禁 | 本文 + R1/R3/R6 | `partially_implemented_non_cad` | runner 已支持证据状态、最小指标、对象类型、组件角色、对象角色、object_spec / composition_spec pipeline、配置校验和每个 CAD_PLAN 的 dry-run / verification 汇总；更多 failure 分类待扩展 |
| R5 | 平台协作与新人接手 | `docs/governance/`、`docs/onboarding/` | `ready_for_use` | 新 agent 可从短入口理解边界和任务 |
| R6 | 角色驱动组合交付自检 | `examples/benchmarks/interior_delivery_benchmark.json`、`core/composition_engine/`、`scripts/run_composition_cad_check.py` | `limited_cad_batch_readback_verified` | 卧室床+地毯、餐桌组合、办公桌组合可生成组合规格、多 CAD_PLAN、dry-run、unverified verification 和 SVG/PNG 视觉辅助预览；3 个简单组合已补跑真实 AutoCAD batch readback，后续更多组合、真实块库和复杂家具符号仍 deferred |

## 实施顺序

| 顺序 | 任务组 | 先做 | 后做 | 验证 |
| --- | --- | --- | --- | --- |
| 1 | R-GOV | 文档入口、协作协议、first handoff | 状态文档同步 | 文档引用和占位词扫描 |
| 2 | R-CAD | 能力契约表、block alpha intent 草案 | schema / driver / readback 测试计划 | 先 non-CAD tests，再真实 CAD readback |
| 3 | R-BLOCK | `BLOCK_LIBRARY v0.2` 字段和受控测试块 metadata | block insertion dry-run / real CAD alpha | metadata validation、readback report |
| 4 | R-OFFICE | office 对象字段、benchmark cases | shell/workflow/runner 断言实现 | office alpha benchmark |
| 5 | R4 hard gate | 统一报告证据状态和 failure 分类 | 将门禁接入 runner | 不允许顶层 pass 掩盖未验证 |
| 6 | R-COMP | 角色需求组合模板、composition benchmark | 真实 CAD 批量执行与 readback | interior delivery benchmark；截图仅作为视觉辅助 |

## 任务清单

| 编号 | 任务 | 交付物 | 依赖 |
| --- | --- | --- | --- |
| R-GOV-01 | 建立 Phase R 执行总表 | 本文 | 无 |
| R-GOV-02 | 固化多 agent 角色、可写边界、交付物和冲突处理 | `docs/governance/multi-agent-contribution.md` | 无 |
| R-GOV-03 | 编写新人 first handoff | `docs/onboarding/first-handoff.md` | 无 |
| R-GOV-04 | 固定证据状态命名 | 本文、R1、R3 | 无 |
| R-GOV-05 | 定义每轮同步 checklist | 本文 | 无 |
| R-CAD-01 | 写入 CAD 实体能力契约表 | `phase-r-cad-capability-contract.md` | Phase W baseline |
| R-CAD-02 | 设计 `insert_block_alpha` 最小 intent | `phase-r-cad-capability-contract.md` | R-BLOCK-01 |
| R-CAD-03 | 定义 block reference readback 字段和验收报告字段 | `phase-r-cad-capability-contract.md` | R-CAD-02 |
| R-CAD-04 | 列出 deferred verification | `phase-r-cad-capability-contract.md` | 无 |
| R-BLOCK-01 | 定义 `BLOCK_LIBRARY v0.2` 字段矩阵 | `phase-r-block-library-roadmap.md` | 无 |
| R-BLOCK-02 | 定义 OBJECT_SPEC 到 block reference 的接口 | `phase-r-block-library-roadmap.md` | R-BLOCK-01 |
| R-BLOCK-03 | 建立最小 `drawing_standard_profile` 路线 | `phase-r-block-library-roadmap.md` | 无 |
| R-BLOCK-04 | 规划受控测试块，不接真实公司块库 | `phase-r-block-library-roadmap.md` | R-BLOCK-01 |
| R-OFFICE-01 | 定义 office 最小对象字段 | `phase-r-office-benchmark-cases.md` | 无 |
| R-OFFICE-02 | 设计 office alpha benchmark cases | `phase-r-office-benchmark-cases.md` | R-OFFICE-01 |
| R-OFFICE-03 | 定义失败样本门槛 | `phase-r-office-benchmark-cases.md` | R-OFFICE-02 |
| R-OFFICE-04 | 规定 office agent 禁止事项 | `phase-r-office-benchmark-cases.md` | 无 |
| R-COMP-01 | 建立通用 composition engine，不把组合写入单一场景 agent | `core/composition_engine/` | R4 |
| R-COMP-02 | 建立 interior delivery persona benchmark | `examples/benchmarks/interior_delivery_benchmark.json` | R-COMP-01 |
| R-COMP-03 | 为组合输出多 CAD_PLAN、dry-run、unverified verification 与视觉辅助预览 | benchmark artifacts | R-COMP-01 |
| R-COMP-04 | 将组合从 non-CAD visual aid 推进到真实 CAD created handles readback | 已有 `output\validation_runs\interior-composition-cad-label-clean-y8000\composition_cad_check_report.json`；后续扩展更多组合和 block insertion | R-CAD |

## 每轮完成后的同步清单

| 文件 | 同步内容 |
| --- | --- |
| `README.md` | 同步用户向入口、当前主线和 Phase R 执行入口 |
| `CORE_CONTEXT_BRIEF.md` | 只同步短结论、入口和不能声称 |
| `CORE_RESTRUCTURE_PLAN.md` | 同步 Phase 状态、可信基线、Decision Gate、执行入口 |
| `CORE_ROADMAP.md` | 同步高层路线入口，不写执行细节 |
| `CORE_STATUS.md` | 同步能力成熟度、证据、主要缺口；无功能证据时不调百分比 |
| `CAD_AGENT_STATUS.md` | 同步当前阶段、最近验证、最重要缺口 |
| `CAD_AGENT_CHANGELOG.md` | 追加结构、规则、脚本、状态变更 |
| `CAD_AGENT_ISSUES.md` | 只有失败、回归、风险或排障教训才更新 |
| `docs/planning/README.md` | 新增或迁移计划文档时更新 |

## 停止条件

遇到下面情况应停止执行并登记问题或询问用户：

- 需要修改正式图层、保存、覆盖或删除 DWG。
- 要接入真实公司块库路径或真实项目敏感资料。
- 要把场景 Agent 写成 Core 算法层。
- 要引入新的几何库、CAD 依赖或安装步骤。
- 真实 CAD readback 无法证明几何准确，但任务要求声明“画准了”。

## 当前结论

Phase R 已从“新鲜视角评审”推进到“可执行开发包”。当前优先顺序已收束到 `CORE_RESTRUCTURE_PLAN.md` 的“当前活跃工作队列”，本文保留原始拆分参考：

1. R-CAD：把现有基础图元探针固化为正式能力契约。
2. R-BLOCK：用受控测试块启动 block insertion alpha，不碰真实公司块库。
3. R-COMP：`interior_delivery_benchmark.json` 已覆盖卧室床+地毯、餐桌组合、办公桌组合 3 个 persona composition cases；这些组合已经补跑真实 CAD 批量执行与 created handles readback，后续只能扩展到更多组合，不能把当前 3 个简单组合扩大为真实家具块库能力。
4. R-OFFICE：`office_alpha_benchmark.json` 已覆盖 desk / chair / cabinet object spec 与第一条 office scene；继续把电脑桌、入口、通道、micro-scene 和失败样本扩成多 case benchmark。
5. R4：runner 已开始区分 non-CAD、截图和真实 readback；后续要把 blocked / invalid failure 分类也纳入硬门禁。
