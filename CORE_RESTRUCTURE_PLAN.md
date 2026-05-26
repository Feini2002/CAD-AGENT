# CAD Agent Core PlanMD（唯一开发主线）

状态：Phase O-V 非 CAD 主线与系统层安全补强已完成；当前主线收束为 Phase R / W / X / Y / Z
最后更新：2026-05-26

> 面向后续 Codex / agentic worker：本文是当前仓库唯一 `PlanMD`，也就是开发主线文件。根目录没有独立 `plan.md`；用户提到 `plan.md`、`PlanMD` 或“主 plan”时，默认指本文。执行开发前必须先读取 `AGENTS.md` 与 `CORE_CONTEXT_BRIEF.md`，再按本文目标 phase 展开。

本文不是本轮要立即执行代码的指令，而是一次深度复盘后的系统级开发计划：记录当前真实进度、维护方式、已知缺口、下一阶段可继续排查和优化的路线。具体开发仍需按 phase 拆小步、测试先行、留证据、同步状态文档。

本文是唯一主 plan。其他 Markdown 可以记录规则、状态、手册、设计依据、历史和执行剧本，但不得各自承载独立“下一步”。主平台 Markdown 精细化拆分已执行：Phase W/X/Y/Z 的长篇执行剧本已迁入 `docs/planning/phase-*.md`；已完成的拆分记录迁入 `docs/history/core-platform-md-split-plan-2026-05-25.md`。2026-05-26 二次雕琢新增 `docs/README.md` 作为文档区总地图，并把 `docs/ROADMAP.md` 降级为兼容跳转；同日又完成 `R-CAD-VIEW-CAPTURE` baseline 小开发包，把 CAD 总控视觉辅助截图升级为 AutoCAD 窗口级截图。

## 防偏离边界

`PlanMD` 只是文档治理和开发排序入口，不是新的产品方向、技术架构或工作流负担。后续任何开发都不能因为本文而偏离以下根方向：

- 本仓库仍是通用 CAD Agent Core Lab，不变成家装、工装、办公、餐饮、展陈或 CAD-MCP 专用项目。
- Core 优先：可复用能力进 `core/`，共享资源进 `libraries/`，项目资料进 `projects/`，场景差异只进 `agents/<scenario>/`。
- `CAD_PLAN` 仍是白话 / 高层模型到 CAD 落图之间的受控中间层；不得从白话直接跳到真实 CAD。
- 真实 CAD 几何准确仍只看 validate、dry-run、`CODEX_PREVIEW` 实际输出、created handles 定向回读和 `geometry_verified` 证据；截图和 benchmark 不能替代回读。
- 场景 Agent 继续保持轻量，只提供偏好、词汇、对象组合语义和排序权重，不实现 Core 算法、CAD 执行或验证。
- 文档收束不等于功能完成；任何百分比、Phase 状态或“可用”声明都必须回到 `CORE_STATUS.md` 和实际验证证据。

## PlanMD 主线协议

后续维护按这个主从关系执行：

| 层级 | 文档 | 可以决定 | 不可以决定 |
| --- | --- | --- | --- |
| 1 | `CORE_RESTRUCTURE_PLAN.md` | 当前活跃工作队列、Phase 顺序、优先级、Decision Gate、退出标准 | 真实 CAD 几何准确结论，除非有对应验证证据 |
| 2 | `docs/planning/phase-*.md` | 某个 Phase 的执行剧本、命令、检查表、失败处理 | 独立改变优先级或新增主线待办 |
| 3 | `CORE_STATUS.md`、`CAD_AGENT_STATUS.md` | 能力成熟度、当前证据、风险边界、最近验证 | 充当第二份计划 |
| 4 | `CORE_ROADMAP.md`、`docs/README.md`、`docs/architecture/`、`docs/governance/`、`docs/onboarding/`、`docs/verification/`、`docs/history/` | 路线说明、导航、架构依据、治理、交接、证据、历史 | 覆盖 PlanMD 的当前队列 |
| 5 | `CAD_AGENT_CHANGELOG.md`、`CAD_AGENT_ISSUES.md` | 历史流水和失败教训 | 推导新的开发优先级 |

如果辅助 MD 中出现新的“下一步、待办、优先级、退出标准”，必须回到本文登记或引用本文已有条目；否则只能写成背景、证据、执行步骤或历史记录。若两个 Markdown 口径冲突，在用户最新指令、`AGENTS.md` 和安全规则之后，以本文为准。

---

## 0. 当前复盘结论

当前仓库已经从早期 CAD 执行脚手架，推进到“通用 CAD Agent Core Lab”的非 CAD Alpha 原型阶段。最近一轮系统层安全补强和自检完成后，可以确认：

- `core/`、`agents/`、`libraries/`、`projects/`、`tests/` 等通用结构已建立。
- Phase O-V 已把 `docs/architecture/shell-layout-foundation-design.md` 的核心思想合并进主线，并落地为可运行的 blank-shell pipeline。
- 当前基线记录为：`unittest discover -s tests` 共 227 tests OK，repo audit 0 findings，blank-shell 4 场景 benchmark pass，office alpha benchmark 4 cases pass，interior delivery benchmark 3 persona composition cases pass；interior delivery 的 3 个 persona composition cases 已补跑真实 AutoCAD batch check，结果为 3/3 `geometry_verified`；`R-CAD-VIEW-CAPTURE` 已通过 no-CAD 与真实 CAD 总控，真实 CAD 证据为 `output\validation_runs\r-cad-view-cad\report.json` 和 `output\validation_runs\r-cad-view-cad\cad-validation-window.png`；此前 `self_check.py` pass、`render_preview.py --check` ready、`run_cad_validation.py --no-cad` pass 仍为稳定基线。
- `scripts/run_cad_validation.py` 已成为 CAD 层面验证总控入口。Phase W 已执行到 W-16；W-07 baseline 真实 CAD 总验证已在用户会话下通过，完成 `CODEX_PREVIEW` 落图、截图、created handles 和实体回读闭环。最新 CAD 底座加固补上了 `readback_report.status` 与 `cad_capability_probe.status` 双硬门禁，并让真实 CAD 回读优先按 created handles 定向读取。
- 当前可以声明 Phase W baseline `examples\plans\draw_test_cabinet.json` 的真实 CAD 几何已通过；不能扩大为真实项目图纸、块库或任意 CAD_PLAN 全部准确。

当前最准确的一句话：

```text
非 CAD 空壳布局链路已跑通，系统维护门禁已补强；下一阶段要把真实 CAD 证据链、场景 Alpha 验收、多候选布局硬化和文档治理继续闭合。
```

---

## 1. 已落地能力与证据边界

### 1.1 空壳布局底座落地情况

`docs/architecture/shell-layout-foundation-design.md` 早上的设计计划已经不再只是旁支蓝图，主要内容已被 Phase P-V 吸收。当前落地事实如下：

| 设计能力 | 当前落地情况 | 证据入口 | 仍有限制 |
| --- | --- | --- | --- |
| `SHELL_MODEL` | 已有 schema、example、invalid fixture 和 manual shell loader | `core/drawing_analysis/shell_loader.py`、`tests/core/test_shell_loader.py` | 主要依赖手工 JSON；自动 DWG/PDF 识别未完成 |
| `PROJECT_MODEL.shell_context` | 已能保留 shell_id、边界、入口、障碍、避让区、必连通点和不确定点 | `core/project_model/project_builder.py`、`tests/core/test_project_model.py` | 复杂项目冲突处理仍浅 |
| 动线候选 | 已支持 `straight_spine`、`l_spine`、`along_wall` | `core/layout_engine/path_generation.py`、`tests/core/test_circulation_generation.py` | 还不是成熟路径规划器 |
| 功能区切分 | 已可基于 bbox shell 和 path surface 切左右区，并处理 no-place-zone 保守扣减 | `core/layout_engine/zone_splitter.py`、`tests/core/test_zone_splitter.py` | 复杂多边形和曲线空间待增强 |
| zone placement | 已支持多类对象、block metadata 优先和 OBJECT_SPEC fallback | `core/layout_engine/placement.py`、`tests/core/test_placement_engine.py` | 真实块插入与 block readback 未闭环 |
| 多候选 proposal | `DESIGN_PROPOSAL` 已支持 candidates、confirmed_candidate_id、comparison_summary 和来源化 evidence | `core/proposal_engine/`、`tests/core/test_proposal_multi_candidate.py` | pipeline 当前仍偏“选定一条主候选”，完整多方案设计脑未完成 |
| blank-shell pipeline | 已串联 shell -> project -> circulation -> zones -> placements -> layout -> proposal -> CAD_PLAN -> dry-run -> unverified report | `core/workflows/blank_shell_pipeline.py`、`scripts/run_blank_shell_pipeline.py`、`tests/core/test_blank_shell_pipeline.py` | 无真实 CAD 证据时只能 `unverified` |
| benchmark | 已覆盖 retail / office / residential / restaurant 四个 workflow case，并新增卧室/餐桌/办公桌 persona composition case | `examples/benchmarks/blank_shell_core_benchmark.json`、`examples/benchmarks/interior_delivery_benchmark.json`、`tests/core/test_benchmarks.py` | 样本仍少，缺历史趋势、真实项目失败基准和组合真实 CAD readback |

### 1.2 当前不能扩大解释的内容

- 不能把非 CAD benchmark pass 解释为真实 CAD 图纸准确。
- 不能把截图能力检查解释为几何验证。
- 不能把 persona composition 的 SVG/PNG 预览解释为真实 CAD created-handle 回读。
- 不能把场景 preferences 当成完整场景 Agent。
- 不能把 blank-shell pipeline 当前输出当作“完整自动设计系统”。
- 不能默认保存 DWG、覆盖原图、删除实体或修改正式图层。

---

## 2. 文档职责分层

后续维护时，根目录文档按下面职责使用，避免重复写状态：

| 文档 | 职责 | 维护方式 |
| --- | --- | --- |
| `README.md` | 用户入口、项目定位、快速恢复、常用命令、换机说明入口 | 只写摘要和入口，不承载长历史 |
| `docs/README.md` | 文档区导航和目录职责 | 只做索引，不写状态或计划 |
| `AGENTS.md` | Codex 强制行为规则 | 只写必须遵守的规则 |
| `CORE_CONTEXT_BRIEF.md` | 日常短上下文入口 | 保持短、稳定、可扫读 |
| `CORE_RESTRUCTURE_PLAN.md` | 唯一 PlanMD 和下一阶段执行路线 | 每次阶段计划变化时更新 |
| `CORE_STATUS.md` | Core 能力矩阵和成熟度 | 更新能力状态、证据、主要缺口 |
| `CORE_ROADMAP.md` | 高层路线图 | 不写具体执行细节 |
| `CAD_AGENT_STATUS.md` | 当前进展页 | 只保留当前阶段、验证、风险边界和阻塞 |
| `CAD_AGENT_CHANGELOG.md` | 历史变更流水 | 每次结构、规则、脚本、状态变更追加记录 |
| `CAD_AGENT_ISSUES.md` | 问题与教训库 | 只有失败、回归、风险或排障教训时更新 |
| `docs/decisions/cad-agent-decisions.md` | 架构与方向决策 | 只记录“为什么这样做” |
| `CAD_AGENT_RULES.md` | 长期开发和 CAD 行为准则 | 写规则，不写阶段流水 |
| `CAD_AGENT_AUTONOMOUS_VALIDATION.md` | 真实 CAD / 换机验证手册 | Phase W 或 CAD 验证时读取 |
| `CAD_AGENT_BLOCKER_PLAYBOOK.md` | 卡壳、画不准、环境不通时的排障流程 | 遇到失败时读取 |
| `docs/architecture/shell-layout-foundation-design.md` | 空壳布局架构设计与边界 | 记录设计背景、已落地映射和剩余差距 |
| `docs/history/shell-layout-time-estimate.md` | 历史时间估算 | 仅作预期管理，不作为当前开发计划 |

本次收尾已把低频设计依据、历史估算、历史拆分记录和决策记录迁出根目录。后续若要进一步瘦身，优先“迁移到 `docs/history/`、`docs/architecture/`、`docs/decisions/` 或 `docs/verification/`”，不要直接删除历史依据。

---

## 3. 下一阶段总路线

下一阶段不建议继续盲目铺功能，应按下面五条主线推进：

```text
Phase W：真实 CAD 回读闭环补验
Phase X：场景 Agent 接入与 Alpha 验收
Phase Y：空壳布局硬化与真实样本扩展
Phase Z：长期维护、文档治理和回归基线
Phase R：新鲜视角评审与重生式开发校准
```

推荐顺序：

1. 先执行 Phase R，把外部新鲜视角、办公基础闭环、图块库和 benchmark 门禁纳入主线；Phase R 已进一步拆成执行总表、CAD 能力契约、图块库路线、办公 benchmark、协作协议和新人接手入口。
2. 有真实 CAD 环境时，按 Phase W 扩展真实 CAD / 块插入补验。
3. CAD 不稳定时，先做 Phase X 与 Phase Y 的非 CAD 工作。
4. 每完成一个 phase，都执行 Phase Z 的文档和基线同步。

其他文档如果需要写“下一步”，只能写成“以本文为准”。具体执行剧本可以保留在 `docs/planning/`，但主次关系必须清楚：本文决定优先级和出口，Phase 文档只服务执行。

## 当前活跃工作队列

| 优先级 | 编号 | 事项 | 证据 / 出口 | 边界 |
| --- | --- | --- | --- | --- |
| 1 | R-CAD | 把基础图元探针沉淀为正式 CAD 能力契约，并推进受控 `insert_block_alpha` | non-CAD tests 先过；真实 CAD 时必须有 created handles readback | 不接真实公司块库，不突破 `CODEX_PREVIEW` |
| 2 | R-BLOCK | 定义 `BLOCK_LIBRARY v0.2`、OBJECT_SPEC 到 block reference 的接口和受控测试块 metadata | metadata validation、dry-run、后续 block readback 报告字段清楚 | 先受控测试块，真实块库另需用户决策 |
| 3 | R-OFFICE | 扩展 office object / micro-scene / failure benchmark | office alpha benchmark 覆盖电脑桌、入口、通道、失败样本 | 场景 Agent 只给偏好，不实现 Core 算法 |
| 4 | R-CAD-VIEW | AutoCAD 窗口级 / 视口级截图 baseline 已完成，后续扩展更细绘图区裁剪、多显示器和遮挡边界 | 当前证据为 `output\validation_runs\r-cad-view-cad\cad-validation-window.png`，已按 AutoCAD 窗口句柄和本轮 created handles bbox 生成干净截图 | 截图仍只作视觉辅助，不替代 created handles readback |
| 5 | R4 | 扩展 runner 证据状态和 blocked / invalid failure 分类 | 不允许顶层 pass 掩盖未验证；`benchmark_pass_non_cad` 与 `geometry_verified` 分离 | 截图只能是视觉辅助 |
| 6 | X | 做场景 Agent Alpha 验收 | 至少 3 个场景复用同一 Core pipeline，preferences 差异可验证 | 禁止场景层实现 CAD 执行、回读、碰撞和几何算法 |
| 7 | Y | 硬化 blank-shell 多候选、失败基准和真实/近真实 shell 样本 | 多候选、失败原因分布、unverified verification 状态可复验 | 不把 pipeline 说成完整自动设计大脑 |
| 持续 | Z | 维护文档职责、引用和验证基线 | 根目录入口清楚；状态页不承载独立计划；文本自查通过 | 不把历史归档当作能力完成 |

## 下一轮开发拆解与子校验

本节把当前建议拆成可执行开发包。它决定开发顺序和退出门槛；更细的文件级步骤写在 `docs/planning/phase-r-rebirth-implementation-plan.md`。每个开发包都必须先完成本地子校验，再进入下一包；真实 CAD 相关结论必须额外通过 created handles 定向 readback，不得只看截图或 runner 顶层 `pass`。

| 顺序 | 开发包 | 开发目标 | 主要文件边界 | 子校验 | 退出门槛 |
| --- | --- | --- | --- | --- | --- |
| 1 | `R-CAD-CONTRACT` | 把现有基础图元探针、readback 字段和证据状态固化为正式 CAD 能力契约 | `docs/planning/phase-r-cad-capability-contract.md`、`core/verification/cad_capability_probe.py`、`core/verification/inspect_dwg.py`、`tests/core/test_cad_capability_probe.py` | `python -m unittest tests.core.test_cad_capability_probe tests.core.test_geometry_checks tests.core.test_cad_validation_runner`；无 CAD 时报告仍必须标记 deferred | 契约字段、failure class、`evidence_state`、`geometry_accuracy` 和不可扩大边界清楚；不新增未验证能力声明 |
| 2 | `R-BLOCK-METADATA` | 定义 `BLOCK_LIBRARY v0.2`、受控测试块 metadata、OBJECT_SPEC 到 block reference 的接口 | `core/schemas/block_library.schema.json`、`libraries/blocks/block_library.example.json`、`core/block_engine/`、`tests/core/test_block_engine.py`、`tests/core/test_schema_validation.py` | schema 正反例测试；block metadata loader / selector 测试；`run_repo_audit.py --fail-on-findings` | metadata 可验证、可 fallback，不依赖真实公司块库；受控测试块字段能支持后续 dry-run 和 readback expectation |
| 3 | `R-BLOCK-PLAN` | 增加受控 `insert_block_alpha` CAD_PLAN intent、dry-run 校验和 fake driver 执行路径 | `core/schemas/cad_plan.schema.json`、`core/plan_engine/`、`core/execution/execute_plan.py`、`tests/core/test_plan_engine.py`、`tests/core/test_execute_plan.py` | 先写 invalid / valid plan 测试；`validate_plan.py` 与 `dry_run_plan.py` 必须区分 block alpha 与普通对象；fake driver 记录非空 block intent | no-CAD 链路能证明 plan 合法与执行意图完整，但报告仍写 `geometry_accuracy=not_verified_without_cad_readback` |
| 4 | `R-BLOCK-CAD-ALPHA` | 在真实 AutoCAD 中只向 `CODEX_PREVIEW` 插入受控测试块，并按 created handles 回读 | `core/cad_io/autocad_com.py`、`core/verification/inspect_dwg.py`、`core/verification/cad_validation_runner.py`、`scripts/run_cad_validation.py`、`docs/verification/` | 非 CAD 单测先过；真实 CAD 时运行 block alpha 专项 step；截图仅作视觉辅助 | 只有 `block_reference` readback checks 全 pass 且报告为 `readback_geometry_verified`，才能声称 block alpha 对受控样本通过 |
| 5 | `R-CAD-VIEW-CAPTURE` | 已把当前全屏截图升级为 AutoCAD 窗口级 / 视口级视觉辅助证据，优先避开 Codex 窗口遮挡 | `core/verification/render_preview.py`、`scripts/render_preview.py`、`core/cad_io/autocad_com.py`、`core/verification/cad_validation_runner.py`、`tests/core/test_render_preview.py`、`tests/core/test_cad_validation_runner.py` | focused tests 11 项 OK；no-CAD 总控 pass；真实 CAD 总控 pass，`cad-validation-window.png` 已生成；报告必须保留 `screenshot_role=visual_aid_only` | baseline 已完成；后续只扩展绘图区裁剪、多显示器和遮挡边界；几何准确仍只由 readback 决定 |
| 6 | `R-OFFICE-MICRO` | 扩展 office object / micro-scene / failure benchmark，覆盖电脑桌、入口、通道和冲突样本 | `examples/benchmarks/office_alpha_benchmark.json`、`examples/shell_models/`、`examples/workflows/`、`core/benchmarks/runner.py`、`tests/core/test_benchmarks.py` | `run_benchmark_suite.py examples/benchmarks/office_alpha_benchmark.json`；失败样本必须输出 `blocked_expected_non_cad` 或 `invalid` | office benchmark 覆盖对象、微场景、场景和失败样本；所有无 CAD 结论仍显式标记非几何验证 |
| 7 | `R4-EVIDENCE-GATES` | 强化 runner 证据状态、blocked / invalid 分类和报告门禁，防止顶层 pass 掩盖未验证 | `core/benchmarks/runner.py`、`core/verification/verification_report.py`、`tests/core/test_benchmarks.py`、`tests/core/test_verification_report.py` | runner 单测 + 三组 benchmark；报告必须区分 `benchmark_pass_non_cad`、`dry_run_valid_plan_only`、`readback_geometry_verified`、`blocked_expected_non_cad` | 任一 case 的状态、几何准确性和截图角色都可被机器断言，不靠人工解释 |
| 8 | `Y-MULTI-CANDIDATE` | 让 blank-shell pipeline 输出更可解释的多候选和结构化失败原因 | `core/workflows/blank_shell_pipeline.py`、`core/layout_engine/`、`core/proposal_engine/`、`examples/benchmarks/blank_shell_core_benchmark.json` | `run_blank_shell_pipeline.py` 与 blank-shell benchmark；新增失败样本不能静默少放对象 | pipeline 能输出多个候选、比较摘要和失败原因分布；仍不声称完整自动设计大脑 |
| 9 | `X-SCENE-ALPHA` | 场景 Agent Alpha 验收，验证至少 3 个场景复用同一 Core pipeline | `agents/*/preferences.json`、`agents/*/rules.md`、`tests/agents/`、`examples/benchmarks/` | agent 边界测试；至少 3 个场景 benchmark 跑通；确认场景目录没有 CAD 执行 / 几何算法 | preferences 差异可观察，Core pipeline 复用清楚，场景层保持轻量 |

### 每个开发包的固定子校验顺序

1. 写或更新最小失败测试 / benchmark case。
2. 运行目标测试，确认失败原因对应本包目标。
3. 实现最小改动，不跨包做大重构。
4. 运行本包测试和相关 benchmark。
5. 若涉及真实 CAD，先跑 no-CAD 校验，再在用户会话下跑真实 CAD，并读取 readback 报告字段。
6. 更新 `CORE_STATUS.md`、`CAD_AGENT_STATUS.md` 和 `CAD_AGENT_CHANGELOG.md`；若出现失败教训，更新 `CAD_AGENT_ISSUES.md`。
7. 在最终汇报里明确哪些是 `benchmark_pass_non_cad`，哪些是 `readback_geometry_verified`。

---

## 当前可信基线索引

| 基线 | 最新证据 | 能声称 | 不能声称 |
| --- | --- | --- | --- |
| 非 CAD 测试基线 | `227 tests OK`、repo audit 0 findings、office alpha benchmark 4 cases pass、interior delivery benchmark 3 cases pass | 仓库非 CAD 主线、组合交付自检和维护门禁当前可复验 | 不证明真实 CAD 几何准确 |
| blank-shell benchmark | 4 场景 benchmark pass | `retail / office / residential / restaurant` 样例链路可跑通 | 不等于完整自动设计大脑 |
| CAD baseline 几何 | `output\validation_runs\manual-cad-after-primitive-probe\report.json`；窗口级截图验证为 `output\validation_runs\r-cad-view-cad\report.json` 与 `output\validation_runs\r-cad-view-cad\cad-validation-window.png` | baseline `draw_test_cabinet.json` 已真实 CAD `geometry_verified`；视觉辅助截图已能避开 Codex 窗口遮挡 | 不扩大到真实项目图纸、块库、块插入或任意 CAD_PLAN；截图不证明几何准确 |
| CAD capability probe | `cad_capability_probe.json.status=cad_capability_verified` | 当前用户会话下基础图元、文字、标注、handles 和定向回读底座可用 | 不代表属性块、hatch、选择集、真实块库已通过 |
| 文档治理基线 | `docs/planning/phase-*.md` 与 `CORE_RESTRUCTURE_PLAN.md` 索引化 | 主计划已从长篇剧本收缩为入口索引 | 不代表 Core Alpha 已完成 |

## Phase 状态语义

| 状态 | 含义 |
| --- | --- |
| `not_started` | 仅在计划中定义 |
| `in_progress` | 正在执行，尚未形成完整证据 |
| `baseline_passed` | 有有限 baseline 证据，但不能扩大到全量能力 |
| `partially_verified` | 部分能力已验证，仍有明确缺口 |
| `blocked` | 受环境、依赖、用户决策或证据缺口阻塞 |
| `done` | 满足该 Phase 退出标准 |
| `retired` | 已被新文档或新阶段取代 |

当前阶段状态：

| Phase | 状态 | 说明 |
| --- | --- | --- |
| Phase W | `baseline_passed` | baseline 真实 CAD 已通过；真实项目、块库、任意 CAD_PLAN 仍未补验 |
| Phase X | `in_progress` | 场景 preferences 和 benchmark 已有，正式 Alpha 验收未做 |
| Phase Y | `in_progress` | blank-shell pipeline 已跑通，多候选、失败基准和真实样本仍需硬化 |
| Phase Z | `in_progress` | 文档拆分已完成，后续每轮仍需同步 |
| Phase R | `in_progress` | 新鲜视角评审已转化为可执行开发包；已补 R-COMP non-CAD 角色组合交付自检；后续进入 R-CAD / R-BLOCK / R-OFFICE / composition CAD readback 的实现与验证 |

## Interface Ownership Map

| 接口 / 产物 | 归属 | 不应放入 |
| --- | --- | --- |
| `CAD_PLAN` | `core/plan_engine`、`core/execution`、`core/verification` | 场景 Agent |
| `PROJECT_MODEL` | `core/project_model` | 场景业务目录 |
| `SHELL_MODEL` | `core/drawing_analysis`、shell loader | 单场景规则 |
| `LAYOUT_PROPOSAL` | `core/layout_engine` | `agents/<scenario>` |
| `DESIGN_PROPOSAL` | `core/proposal_engine` | CAD driver |
| `VERIFICATION_REPORT` | `core/verification` | benchmark summary 的泛化 pass |
| `COMPOSITION_SPEC` | `core/composition_engine` | 场景 Agent 或真实块库 |
| scene preferences | `agents/<scenario>` | Core 算法和 CAD 执行 |
| block metadata | `libraries/blocks`、`core/block_engine` | 场景 Agent |
| layer/style standards | `libraries/layer_presets`、`libraries/drawing_standards`、`libraries/styles` | 单个对象或场景硬编码 |

## Decision Gates

| Gate | 默认选择 | 触发条件 | 不决策时保守路径 |
| --- | --- | --- | --- |
| G1：是否引入成熟几何库 | 暂不引入 | Phase Y 复杂多边形和 clearance 逻辑明显变重 | 继续用当前正交几何和小样本 |
| G2：是否优先自动 DWG/PDF 识别 | 暂不优先 | 用户要求真实图纸自动识别闭环 | 继续人工 JSON shell 闭环 |
| G3：首个真实业务场景 | office 基础闭环 | 用户选择真实场景验收 | 用办公桌/椅/电脑桌/柜体/入口/通道样本 |
| G4：真实块库接入策略 | 先用受控测试块 | block insertion alpha 通过后 | 继续参数化 fallback 和 block intent |
| G5：proposal 是否自动转 CAD_PLAN | 默认需用户确认 | 用户要求自动落图 | 保持 proposal -> confirmation -> CAD_PLAN |

## Alpha 里程碑判定

| 里程碑 | 必须满足 | 明确不包含 |
| --- | --- | --- |
| Core Alpha | 非 CAD 主线、schema、pipeline、benchmark、自检和有限 CAD baseline 证据稳定 | 完整自动设计大脑、真实项目全量准确 |
| Scene Alpha | 至少 3 个场景复用同一 Core pipeline，preferences 差异可观察 | 场景内自建几何算法或 CAD 执行 |
| CAD Validation Alpha | baseline CAD_PLAN 真实落图、created handles、readback、截图和 `geometry_verified` 闭环 | 块库、属性块、hatch、任意 CAD_PLAN 全量准确 |
| Rebirth Review Alpha | 多角色 Fresh Eyes Review 有记录，建议转化为 Phase R 计划 | 直接修改代码或替代正式测试 |

---

## Phase 执行入口

Phase W/X/Y/Z 的长篇执行剧本已拆入 `docs/planning/`，本文只保留总控索引和阶段关系。执行具体阶段时，先读 `AGENTS.md`、`CORE_CONTEXT_BRIEF.md`，再打开对应 Phase 文档。

| Phase | 当前状态 | 执行文档 | 说明 |
| --- | --- | --- | --- |
| Phase R | 新鲜视角已消化为执行包，且角色组合交付自检已有 non-CAD 证据 | `docs/planning/phase-r-fresh-perspective-rebirth-plan.md`、`docs/planning/phase-r-rebirth-implementation-plan.md`、`docs/planning/phase-r-cad-capability-contract.md`、`docs/planning/phase-r-block-library-roadmap.md`、`docs/planning/phase-r-office-benchmark-cases.md`、`examples/benchmarks/interior_delivery_benchmark.json` | 多 agent 外部视角、CAD 能力契约、办公基础闭环、图块库、composition 自检和 benchmark 门禁 |
| Phase W | baseline 已完成，后续扩展真实 CAD 补验 | `docs/planning/phase-w-cad-validation-plan.md` | 真实 CAD 回读、截图、created handles 和 `geometry_verified` 门禁 |
| Phase X | 下一优先级 | `docs/planning/phase-x-scene-agent-alpha-plan.md` | 场景 Agent Alpha 验收 |
| Phase Y | 与 Phase X 并行或随后推进 | `docs/planning/phase-y-blank-shell-hardening-plan.md` | blank-shell 多候选、失败基准和真实样本 |
| Phase Z | 每轮都要同步 | `docs/planning/phase-z-doc-governance-plan.md` | 文档治理、回归基线和状态同步 |

文档拆分完成不等于 Core Alpha 完成；它只让后续 Phase X/Y/W 执行更稳定。

## 4. 停下来问用户的分歧点

以下事项不要擅自定死：

- 是否引入成熟几何库，例如 `shapely`，还是继续自研正交多边形能力。
- 是否优先自动 DWG/PDF 识别，还是继续人工标注 JSON 闭环。
- 是否接入真实公司块库，还是继续用 `libraries/blocks/*.json` 元数据。
- 首个真实 CAD Alpha 验收使用哪张 DWG。
- 首个真实业务场景验收优先选择 commercial、residential、office、restaurant 还是 exhibition。
- 是否允许低风险 proposal 自动转 CAD_PLAN；默认仍需要用户确认。
- 是否允许正式图层、保存、覆盖或删除操作；默认全部不允许。

---

## 5. 完成判定

只有同时满足下面条件，才可以说 Core 可用 Alpha 基本完成：

- Phase W 至少对 baseline plan 完成一次真实 CAD 落图、截图、实体回读闭环，或明确登记 `external_blocker`。
- Phase X 至少 3 个场景 Agent 复用同一 Core pipeline，且 preferences 差异可验证。
- Phase Y 让 blank-shell pipeline 输出多个可解释候选或结构化失败原因，并扩展真实/近真实样本。
- Phase R 的 Fresh Eyes Review 已转化为后续执行计划，且没有把新鲜视角变成偏离 Core 的魔改路线。
- 固定非 CAD 回归命令通过。
- `CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md` 已同步。
- 若过程出现失败或教训，`CAD_AGENT_ISSUES.md` 已记录。

如果用户明确说“只讨论计划，不执行开发”，则不得改代码；但计划、状态和文档治理本身发生变化时，仍要同步相关 Markdown。
