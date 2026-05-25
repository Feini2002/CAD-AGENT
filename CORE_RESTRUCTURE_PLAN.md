# CAD Agent Core 可用化深水开发计划

状态：Phase O-V 非 CAD 主线已通过，下一步进入 Phase W / X
最后更新：2026-05-25

> 面向后续 Codex / agentic worker：本文是当前仓库的主计划文件。执行计划前必须先读取根目录 `AGENTS.md`；日常恢复先走 `CORE_CONTEXT_BRIEF.md`，执行具体 phase 时再按需展开本文对应章节。实现时按任务勾选推进，所有阶段都必须保留验证证据。用户提到 `plan.md` 时，默认指本文。

本文已从旧版 A-N 已完成清单整理为“接下来还要做什么”。已完成历史只保留摘要，详细记录见 `CORE_STATUS.md`、`CORE_ROADMAP.md`、`CAD_AGENT_STATUS.md` 和 `CAD_AGENT_CHANGELOG.md`。

本轮纳入 `SHELL_LAYOUT_FOUNDATION_DESIGN.md` 的设计思路，但不修改该文档。空壳布局底座不再作为旁支蓝图，而是下一轮让 Core 变得可用的主线。

最近同步检查：2026-05-25 15:17 已完成一轮非 CAD 基线复验，`unittest discover -s tests` 为 165 tests OK，`self_check.py` 为 pass，`render_preview.py --check` 为 ready，blank-shell pipeline 为 ok，4 场景 blank-shell benchmark 为 pass，`scripts/run_cad_validation.py --no-cad --output-dir output\validation_runs\docs-sync-no-cad` 为 pass。真实 CAD 落图、截图与实体回读仍未补验，不能据此声称几何准确。

---

## 执行交付协议

本文是交给后续 Codex / agentic worker 的主计划文件。它不是一次性从 Phase O 跑到 Phase X 的长脚本；执行者必须按 phase 逐段推进，并在每个 phase 内再拆成可验证的小步。

### 执行边界

- 一次只执行一个 phase。除非用户明确要求并行，否则不得同时推进两个以上 phase。
- Phase O 是后续所有 phase 的入口；Phase P-X 只有在前置 phase 退出标准满足或明确登记阻塞后才能开始。
- 任何自然语言、场景偏好或空壳输入都必须先进入结构化模型，再进入 `CAD_PLAN`；不得绕过 validate、dry-run 和确认门。
- 真实 CAD 相关动作只允许在 Phase W 或用户明确要求的 CAD 验证任务中执行，且默认只操作 `CODEX_PREVIEW`。
- 如果执行过程中发现本文引用的文件、脚本或 schema 与仓库实际不一致，先修正计划或登记阻塞，不要用猜测继续开发。

### 每个 Phase 的固定工作循环

执行任一 phase 时，按下面顺序推进：

1. 恢复上下文：读取根目录 `AGENTS.md` 要求的上下文文件，并确认当前 phase 的前置条件。
2. 文件盘点：检查本 phase “文件”清单中每个路径是已存在、待创建还是待修改；若状态不符，先在本 phase 中记录。
3. 测试先行：先写或更新最小失败测试 / schema 反例 / benchmark 断言，再写实现。
4. 红灯确认：运行本 phase 的最小验证命令，确认失败原因与预期一致。
5. 最小实现：只改本 phase 直接相关文件，不借机做跨 phase 重构。
6. 绿灯复验：运行本 phase 验证命令，再运行固定自检。
7. 证据落盘：把自动报告、benchmark、pipeline artifacts、CAD 截图或 readback 报告写入 `output/` 或 `docs/verification/`。
8. 状态同步：更新本文件的待校验登记表、`CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md`；如果有失败教训，更新 `CAD_AGENT_ISSUES.md`。
9. 交接说明：回复用户时列出完成的 phase、验证命令、证据路径、剩余阻塞和下一 phase 建议。

### 任务拆分要求

每个 phase 的任务列表是一级工作包。真正执行前，Codex 必须把当前 phase 拆成 2-5 分钟粒度的子步骤，至少包含：

- 要新增或修改的测试名称。
- 预期红灯结果。
- 最小实现入口。
- 目标验证命令。
- 证据输出路径。
- 本 phase 完成后需要更新的记录文件。

禁止出现只写“补验证”“处理边界情况”“完善逻辑”但没有测试、路径、命令或通过标准的子任务。

### 证据状态口径

| 状态 | 含义 | 允许用于完成声明 |
| --- | --- | --- |
| `pass` | 自动验证或真实 CAD 验证全部通过 | 可以 |
| `unverified` | 非 CAD 逻辑通过，但缺真实 CAD 证据 | 只能声明非 CAD 通过，不能声明几何准确 |
| `external_blocker` | 剩余问题依赖 CAD、授权、窗口、依赖安装或用户资料 | 不能声明完成，只能列阻塞清单 |
| `fail` | 仓库内测试、schema、执行器、pipeline 或验证逻辑仍失败 | 不能交付，必须继续最小修复 |
| `not_started` | 计划存在但尚未实现 | 不能交付 |

### 交给 Codex 前的计划自检

每次把本文交给新的 Codex 执行前，先确认：

- 每个 phase 都有目标、文件清单、任务、验证命令和退出标准。
- 每个新增脚本引用都已在对应 phase 标明是“已存在”还是“待创建”。
- CAD 相关命令均有安全边界和证据路径。
- 非 CAD phase 不依赖真实 CAD。
- 所有需要用户决策的分歧点集中在“停下来问用户的分歧点”，不要散落在任务里。
- 本文没有英文待办标记、拖延式表达，或其他不可执行占位。

---

## 0. 当前判断

当前 Core 已经具备非 CAD 可用 Alpha 原型闭环，但完整“能用”仍受两类约束限制：一是还缺真实 AutoCAD 落图 / 截图 / 实体回读闭环，二是设计推理和场景 Agent 验收还停留在 prototype。当前事实如下：

| 缺口 | 当前状态 | 为什么影响可用 |
| --- | --- | --- |
| 空壳理解 | `SHELL_MODEL` 已成为 blank-shell pipeline 主输入，manual shell loader 和 `PROJECT_MODEL.shell_context` 已保留入口、障碍、避让区与连通点 | 仍不承诺自动读懂任意 DWG / PDF，复杂空间语义和真实图纸提取待扩展 |
| 几何底座 | `rect2d` 与 `orthogonal_polygon` 已覆盖矩形、bbox 扣减、path strip、门洞/障碍距离和简单正交多边形校验 | 当前不替代成熟几何库，复杂多边形、曲线和 CAD kernel 仍需后续决策 |
| 布局生成 | blank-shell pipeline 已能生成动线候选、功能区、zone placement、layout proposal，并通过 4 场景 benchmark | 仍需要更真实的通道优化、候选解释和真实项目回归样本 |
| 对象与图块 | `object_defaults.json` 已覆盖 cabinet/table/chair/desk/shelf/counter/bed/sofa/display_unit，block metadata 与 fallback object spec 已接入 placement | 还没有真实块插入和块引用 readback 验证 |
| 方案推理 | `DESIGN_PROPOSAL` 已支持多候选、确认候选、比较摘要和来源化 evidence | 仍不是完整自动设计大脑，复杂方案取舍、用户确认流和风格细化待深化 |
| 端到端样例 | blank-shell pipeline 与 retail / office / residential / restaurant 四个 benchmark case 已重复通过 | 样本仍偏少，缺少真实项目趋势记录和失败基准 |
| CAD 验证 | `execute_plan`、截图、readback 都有入口 | 真实 AutoCAD 回读闭环仍待实机验证，不能声称几何准确 |
| 能力编排 | `workflow.blank_shell_pipeline` 已登记到 capability registry，并串联 shell -> circulation -> zones -> placement -> proposal -> plan | 还需补审计记录字段、更多 workflow 类型和 Phase X 场景 Agent Alpha 验收 |

本轮目标不是做“完整自动设计系统”，而是把 Core 推到可用 Alpha。非 CAD 主链已跑通：

```text
人工标注空壳输入
-> SHELL_MODEL
-> PROJECT_MODEL
-> CIRCULATION_MODEL
-> FUNCTION_ZONE
-> 多候选 LAYOUT_PROPOSAL
-> DESIGN_PROPOSAL
-> CAD_PLAN
-> validate / dry-run
-> CODEX_PREVIEW
-> VERIFICATION_REPORT
```

其中真实 CAD 证据缺失时，最后一步只能是 `VERIFICATION_REPORT(unverified)`。

---

## 1. Core 可用 Alpha 定义

达到下面标准，才算 Core “差不多能用”：

1. 输入一个手工标注的空壳 JSON，至少包含外边界、入口、柱子或避让区、消防门或必连通点。
2. 能生成结构化 `SHELL_MODEL`，并把它合并进 `PROJECT_MODEL`，不丢失来源和不确定点。
3. 能生成至少 2 种动线候选，例如直线主轴、L 型主轴、沿边或环形策略。
4. 能沿动线切出若干 `FUNCTION_ZONE`，每个区有面积、深度、开口方向、可用性和候选功能。
5. 能放置至少 5 类通用对象或图块 fallback：`cabinet`、`table`、`chair`、`desk`、`shelf`、`counter`、`bed`、`sofa`、`display_unit` 中至少 5 类。
6. 能检查边界、对象碰撞、基础 clearance、主/次通道宽度、柱子/门洞/消防避让。
7. 能输出多个 `LAYOUT_PROPOSAL.candidates`，每个候选有分数、失败检查、解释、假设和待确认点。
8. 用户确认后能转为一个或多个安全 `CAD_PLAN`，默认只画 `CODEX_PREVIEW`。
9. `CAD_PLAN` 必须通过 validate 和 dry-run；无真实 CAD 证据时 `VERIFICATION_REPORT.status` 只能是 `unverified` 或更低证据状态。
10. 至少有 4 个非 CAD benchmark case：空壳零售、办公、住宅、餐饮或展陈中的 4 类；每个 case 可重复跑出 pass/fail 汇总。

---

## 2. 非目标与安全边界

本轮明确不做：

- 不承诺自动读懂任意 DWG / PDF。
- 不生成正式施工图、材料表、全专业图层和完整标注体系。
- 不把公司专用方案习惯写进 `core/`。
- 不新增重依赖，除非用户明确批准成熟几何库路线。
- 不默认保存 DWG、不覆盖原图、不修改正式图层、不删除实体。
- 不把截图当成几何准确证据；截图只能辅助，实体回读和预期对比才是硬证据。

默认策略：

```text
通用算法 -> core/
场景偏好 -> agents/<scenario>/
对象/块/尺寸/标准 -> libraries/
项目输入输出 -> projects/
验证证据 -> output/ 或 docs/verification/
```

---

## 3. 已完成基线摘要

以下内容已存在，后续不要重复规划成“从零开始”：

- `core/`、`agents/`、`libraries/`、`projects/`、`tests/` 结构已建立。
- `scripts/`、`drivers/` 作为兼容包装器保留。
- 高层 schema 已覆盖 `DESIGN_BRIEF`、`DRAWING_MODEL`、`PROJECT_MODEL`、`OBJECT_SPEC`、`STYLE_PROFILE`、`BLOCK_LIBRARY`、`LAYOUT_PROPOSAL`、`DESIGN_PROPOSAL`、`VERIFICATION_REPORT`、`SHELL_MODEL`、`CIRCULATION_MODEL`、`FUNCTION_ZONE`。
- 已有第一批 Core 原型：object/style/block/layout/proposal/plan/verification/safety/capability/benchmark/non-CAD pipeline。
- `projects/sample_blank_shell/input/shell.manual.json` 已成为空壳布局样例输入之一，Phase V 另补 retail / office / residential / restaurant workflow benchmark。
- 最近基线记录为 165 项单元测试通过，`self_check.py` pass，`render_preview.py --check` ready，blank-shell pipeline ok，4 场景 blank-shell benchmark pass，`run_cad_validation.py --no-cad` pass。
- 最近同步证据路径：`output\test_artifacts\blank_shell_pipeline\docs-sync\`、`output\test_artifacts\benchmarks\docs-sync\`、`output\validation_runs\docs-sync-no-cad\report.json`。

后续开发必须保护这些入口，不随手破坏兼容命令：

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"

& $py -m unittest discover -s tests
& $py scripts\self_check.py
& $py scripts\validate_plan.py examples\plans\draw_test_cabinet.json
& $py scripts\dry_run_plan.py examples\plans\draw_test_cabinet.json
& $py scripts\render_preview.py --check
& $py scripts\inspect_dwg.py --plan examples\plans\draw_test_cabinet.json --format json --no-cad
& $py scripts\run_benchmark_suite.py examples\benchmarks\non_cad_core_benchmark.json --output-root output\test_artifacts\benchmarks\manual
& $py scripts\run_blank_shell_pipeline.py examples\workflows\blank_shell_layout_loop.json --output-dir output\test_artifacts\blank_shell_pipeline\manual
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\blank_shell_manual
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\phase-manual-no-cad
```

---

## 4. 待校验登记表

执行任何 phase 时持续维护本表。新增能力如果“实现了但没有证据”，必须登记；验证后再更新状态。

| ID | 内容 | 当前状态 | 当前可做验证 | 需要 CAD 补验 | 通过标准 |
| --- | --- | --- | --- | --- | --- |
| V-CAD-001 | `scripts/execute_plan.py` 真机落图 | 待 CAD 补验 | recording driver、validate、dry-run | 是 | `CODEX_PREVIEW` 出现预期对象、文字和标注 |
| V-CAD-002 | `scripts/inspect_dwg.py --connect-cad` 实体回读 | 待 CAD 补验 | fake readback、`--no-cad` 报告壳 | 是 | 回读到本次新增实体，bbox、基点、图层、文字、标注检查通过 |
| V-CAD-003 | `render_preview.py --capture-screen` 真实 CAD 截图 | 待 CAD 补验 | `render_preview.py --check` | 是 | 截图文件落盘并挂入报告 |
| V-CAD-004 | `AutoCADComDriver.snapshot_modelspace()` 真实 COM 属性稳定性 | 待 CAD 补验 | COM-like fake entity 单测 | 是 | line/text/dimension 标准化为稳定 dict |
| V-CAD-005 | `VERIFICATION_REPORT.geometry_verified` 真实闭环 | 待 CAD 补验 | fake readback 几何验证测试 | 是 | 只有 readback scope 明确且全部检查通过时才为 `geometry_verified` |
| V-NONCAD-014 | `SHELL_MODEL` 成为布局主输入 | Phase P 已完成 shell loader 与 project merge，并补充 legacy drawing-style 输入兼容回归；circulation/zones 待 Phase R/S | `tests.core.test_shell_loader`、`tests.core.test_project_model`、shell schema example 校验 | 否 | 样例空壳可生成 project/circulation/zones |
| V-NONCAD-015 | 直线/L 型/沿边动线候选 | Phase R 已完成 straight_spine / l_spine / along_wall 生成器，失败候选保留 blocked_reasons | `tests.core.test_circulation_generation`、circulation schema examples、`tests.core.test_capabilities` | 否 | 同一 shell 至少生成 2 个可解释候选 |
| V-NONCAD-016 | 功能区切分 | Phase S 已完成 bbox shell + path surface 的左右功能区切分，支持 no-place-zone 保守扣减和 uncertainty | `tests.core.test_zone_splitter`、function zone schema examples、`tests.core.test_capabilities` | 否 | 动线两侧或沿边可生成多个功能区 |
| V-NONCAD-017 | 多类别对象 placement | Phase T 已完成 object defaults、扩展对象类型、zone placement 和 block/fallback source | `tests.core.test_placement_engine`、`tests.core.test_object_engine`、`tests.core.test_block_engine`、object spec schema examples | 否 | 至少 5 类对象可放置并输出 bbox/rotation |
| V-NONCAD-018 | 空壳布局 benchmark suite | Phase V 已完成：retail / office / residential / restaurant 四个不同 workflow case 可重复运行，并记录 candidates、zones、placements、CAD_PLAN、dry-run、verification 指标 | `tests.core.test_benchmarks`、`tests.core.test_benchmark_cli`、`scripts/run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json` | 否 | 至少 4 个场景 case 可重复 pass/fail |
| V-NONCAD-019 | 空壳 pipeline capability chain | Phase V 已完成：`workflow.blank_shell_pipeline` 已登记；pipeline 串联 shell/project/circulation/zones/placements/proposal/CAD_PLAN/dry-run/unverified report | `tests.core.test_blank_shell_pipeline`、`tests.core.test_capabilities`、`scripts/run_blank_shell_pipeline.py examples\workflows\blank_shell_layout_loop.json` | 否 | shell/layout/proposal/plan 能力可发现、可验证 |

---

## 5. 执行路线总览

按顺序推进，不要并行铺太散：

1. Phase O：基线冻结与能力真相表。
2. Phase P：`SHELL_MODEL` 主输入与人工空壳加载。
3. Phase Q：几何底座 v1。
4. Phase R：动线生成 v1。
5. Phase S：功能区切分 v1。
6. Phase T：对象与图块 placement v1。
7. Phase U：多候选 proposal 与确认门强化。
8. Phase V：空壳端到端 pipeline 与 benchmark suite。
9. Phase W：真实 CAD 回读闭环补验。
10. Phase X：场景 Agent 接入与 Alpha 验收。

### Phase 依赖与交付物

| Phase | 允许开始的条件 | 主要交付物 | 必须留下的证据 |
| --- | --- | --- | --- |
| O | 已读取上下文文件，确认当前仓库状态 | capability maturity / known_limits、状态口径修正 | 基线命令输出、`run_cad_validation.py --no-cad` 报告 |
| P | Phase O 通过或只剩明确外部阻塞 | `SHELL_MODEL` 主输入、manual shell loader、project merge | shell loader 单测、schema 校验、有效/无效 shell examples |
| Q | Phase P 的 shell/project 输入稳定 | rect / orthogonal geometry backend v1 | 几何单测、结构化失败 reason 样例 |
| R | Phase Q 提供 path strip / obstacle 检查 | circulation candidates 生成 | circulation 单测、至少 2 个候选 example |
| S | Phase R 可输出 path surface | function zone splitter | zone 单测、zone schema example |
| T | Phase S 可输出可布置 zone | 多对象 placement 与 block fallback | placement/object/block 单测，至少 5 类对象放置证据 |
| U | Phase T 可输出 layout candidates | 多候选 design proposal 与确认门 | proposal/comparison 单测，未确认阻断测试 |
| V | Phase U 可转安全 `CAD_PLAN` | blank shell pipeline 与 4 case benchmark | pipeline artifacts、benchmark pass/fail 汇总 |
| W | 用户已打开 CAD，或明确只做无 CAD 阻塞登记 | CAD 落图、截图、readback、verification 闭环 | `CAD_AGENT_AUTONOMOUS_VALIDATION.md` 流程报告、截图、readback report |
| X | Phase V 通过；Phase W 通过或 CAD 阻塞已登记 | 多场景 preferences 接入 Alpha 验收 | agents 单测、scene benchmark、边界扫描 |

如果某个 phase 结束时不能满足退出标准，必须把状态登记为 `fail` 或 `external_blocker`，并停止进入下一个 phase。

### 建议 Agent 分工模式

后续执行时可以把一个 phase 拆给多个短生命周期 Agent，但每个 Agent 只处理一个清晰边界，避免共享状态混乱：

| Agent 名称 | 适用阶段 | 职责 | 输出 |
| --- | --- | --- | --- |
| `context-auditor` | O、所有 phase 开始前 | 读取上下文、核对状态口径、检查文件是否存在 | 状态差异清单、前置阻塞 |
| `schema-contract-agent` | P、S、U、V | 修改 schema、example、invalid fixture、registry | schema diff、validator 结果 |
| `unit-test-agent` | O-X | 先写失败测试，固定测试入口和预期红灯 | 测试文件、红灯输出摘要 |
| `engine-agent` | P-U | 实现 Core 纯逻辑，禁止触碰 CAD 窗口 | Core 模块修改、单测绿灯 |
| `pipeline-agent` | V、X | 串联 artifacts、benchmark、CLI wrapper | pipeline artifacts、benchmark 报告 |
| `cad-validation-agent` | W | 按 `CAD_AGENT_AUTONOMOUS_VALIDATION.md` 跑真实 CAD 验证 | `output/validation_runs/*/report.json` |
| `docs-sync-agent` | 每个 phase 结束 | 更新状态、changelog、issues、待校验登记表 | 文档同步 diff |
| `review-agent` | 每个 phase 结束 | 查跑偏、缺测试、证据状态误报、场景层越界 | review finding 清单 |

这些 Agent 是执行分工建议，不代表必须新增仓库代码文件。若使用 subagent-driven 执行，每个 Agent 完成后主 Codex 必须复核输出，再进入下一步。

---

## Phase O：基线冻结与能力真相表

目标：先把“哪些是真的可用、哪些只是原型”固定下来，避免后续继续在错觉上开发。

文件：

- 修改：`CORE_STATUS.md`
- 修改：`CAD_AGENT_STATUS.md`
- 修改：`CORE_RESTRUCTURE_PLAN.md`
- 修改：`core/capabilities/registry.py`
- 参考：`CAD_AGENT_AUTONOMOUS_VALIDATION.md`
- 测试：`tests/core/test_capabilities.py`

任务：

- [x] 运行完整非 CAD 基线命令，记录通过项和失败项。
- [x] 运行 `scripts/run_cad_validation.py --no-cad`，把结构化报告作为 Phase O 证据。
- [x] 在 capability catalog 中为每个能力增加 `maturity` 字段：`prototype`、`alpha_ready`、`blocked_by_cad`、`not_started`。
- [x] 为 capability 增加 `known_limits` 字段，写明当前能力不能做什么。
- [x] 在 `CORE_STATUS.md` 中把 `layout_engine`、`drawing_analysis`、`proposal_engine`、`verification` 的限制写清楚。
- [x] 对齐 `README.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md` 和本文中的 Phase O-X 口径，清掉旧字母阶段的执行口径残留。
- [x] 若验证失败，先按 `CAD_AGENT_BLOCKER_PLAYBOOK.md` 处理，不继续进入 Phase P。

细化执行清单：

- [x] O-01 `context-auditor`：读取 `README.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_ISSUES.md`，列出“已完成 / 原型 / 未开始 / CAD 阻塞”四类事实。
- [x] O-02 `unit-test-agent`：阅读 `tests/core/test_capabilities.py`，补一条红灯测试，断言 capability 记录必须暴露 `maturity` 和 `known_limits`。
- [x] O-03 `engine-agent`：更新 `core/capabilities/registry.py` 的 capability 数据结构，给已有能力填入保守成熟度，不把 prototype 写成 alpha_ready。
- [x] O-04 `unit-test-agent`：运行 `& $py -m unittest tests.core.test_capabilities`，确认 O-02 红灯转绿。
- [x] O-05 `context-auditor`：运行完整非 CAD 基线命令，并把 stdout/stderr 摘要登记到 Phase O 工作记录。
- [x] O-06 `context-auditor`：运行 `scripts/run_cad_validation.py --no-cad`，检查 `report.json.status`，按 `pass/fail/external_blocker` 分类。
- [x] O-07 `docs-sync-agent`：更新 `CORE_STATUS.md` 中 `layout_engine`、`drawing_analysis`、`proposal_engine`、`verification` 的限制，不新增实现承诺。
- [x] O-08 `docs-sync-agent`：更新 `CAD_AGENT_STATUS.md` 和 `CAD_AGENT_CHANGELOG.md`，说明 Phase O 是否完成、证据路径是什么。
- [x] O-09 `review-agent`：扫描文档是否仍存在旧执行口径、不可执行占位和“当前已能自动设计”的误导说法。
- [x] O-10 主 Codex：汇总 Phase O 证据，只有 `tests.core.test_capabilities`、全量单测、`self_check.py`、`run_cad_validation.py --no-cad` 均满足退出标准后，才允许进入 Phase P。

验证：

```powershell
& $py -m unittest tests.core.test_capabilities
& $py -m unittest discover -s tests
& $py scripts\self_check.py
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\phase-o-no-cad
```

退出标准：

- capability registry 能准确区分原型、可用 Alpha 和 CAD 阻塞能力。
- 用户或后续 Codex 读状态文档时不会误以为当前 Core 已经能自动设计。
- `output\validation_runs\phase-o-no-cad\report.json` 存在，且 `status` 为 `pass`；若不是 `pass`，已登记失败分类和下一步。

---

## Phase P：SHELL_MODEL 主输入与人工空壳加载

目标：把空壳输入从旁路样例提升为布局主流程输入。第一版仍允许人工标注，不追求自动识别任意 DWG。

文件：

- 创建：`core/drawing_analysis/shell_loader.py`
- 修改：`core/schemas/shell_model.schema.json`
- 修改：`core/schemas/project_model.schema.json`
- 修改：`core/project_model/project_builder.py`
- 修改：`core/schemas/registry.py`
- 创建：`examples/shell_models/retail_blank_shell.json`
- 创建：`examples/shell_models/office_blank_shell.json`
- 修改：`projects/sample_blank_shell/input/shell.manual.json`
- 创建：`tests/core/test_shell_loader.py`
- 修改：`tests/core/test_project_model.py`
- 修改：`tests/core/test_schema_validation.py`

任务：

- [x] 扩展 `SHELL_MODEL`，支持 `boundary.type = bbox|polygon|orthogonal_polygon`。第一版计算仍可只完整支持 bbox 和正交多边形，任意 polygon 先标记为有限支持。
- [x] 在 `SHELL_MODEL` 中加入 `openings`、`fixed_obstacles`、`no_place_zones`、`required_connections`、`building_elements`、`uncertainties`、`source`。
- [x] 写 `load_manual_shell(path)`，把人工 JSON 规范化为 `SHELL_MODEL`，并校验单位、边界、洞口宽度、避让区 bbox。
- [x] 兼容旧 `DRAWING_MODEL.spaces` 输入：`project_builder` 可从 `shell_model` 或旧 drawing spaces 构建项目模型。
- [x] `PROJECT_MODEL` 保留 `shell_id`、`space_id`、约束、待确认问题和来源证据。
- [x] 注册 capability：`drawing_analysis.load_shell_model`。
- [x] 为错误输入补反例：边界无效、入口缺宽度、避让区越界、单位缺失。

细化执行清单：

- [x] P-01 `schema-contract-agent`：盘点现有 `shell_model.schema.json`、`project_model.schema.json` 和 `projects/sample_blank_shell/input/shell.manual.json`，列出字段缺口。
- [x] P-02 `unit-test-agent`：创建 `tests/core/test_shell_loader.py`，先写 `test_load_manual_shell_requires_units_and_boundary` 红灯。
- [x] P-03 `schema-contract-agent`：扩展 `SHELL_MODEL` schema，加入 `boundary`、`openings`、`fixed_obstacles`、`no_place_zones`、`required_connections`、`building_elements`、`uncertainties`、`source`。
- [x] P-04 `engine-agent`：创建 `core/drawing_analysis/shell_loader.py`，实现 `load_manual_shell(path)` 的最小路径读取、单位检查和 bbox 边界规范化。
- [x] P-05 `unit-test-agent`：补 `test_load_manual_shell_rejects_opening_without_width`，确认入口缺宽度时失败原因明确。
- [x] P-06 `engine-agent`：补洞口、避让区越界和固定障碍物的保守校验；复杂 polygon 不求计算，只标记有限支持和 uncertainty。
- [x] P-07 `schema-contract-agent`：创建 `examples/shell_models/retail_blank_shell.json` 和 `examples/shell_models/office_blank_shell.json`，并补 invalid fixture。
- [x] P-08 `engine-agent`：修改 `core/project_model/project_builder.py`，支持从 `shell_model` 构建 `PROJECT_MODEL`，同时保留旧 `DRAWING_MODEL.spaces` 路径。
- [x] P-09 `unit-test-agent`：扩展 `tests/core/test_project_model.py`，断言 `shell_id`、`source`、constraints、uncertainties 不丢失。
- [x] P-10 `schema-contract-agent`：注册 `drawing_analysis.load_shell_model` capability，并补 registry / schema validation 测试。
- [x] P-11 `review-agent`：检查 Phase P 是否偷偷实现了 Phase Q 的复杂几何；如果有，拆回 Q。
- [x] P-12 `docs-sync-agent`：更新待校验登记表 `V-NONCAD-014` 状态和证据路径。
- [x] P-13 `unit-test-agent`：补 `test_load_manual_shell_keeps_legacy_drawing_style_compatible`，确认旧 drawing-style 手工输入仍可规范化为 `SHELL_MODEL`。

验证：

```powershell
& $py -m unittest tests.core.test_shell_loader
& $py -m unittest tests.core.test_project_model
& $py -m unittest tests.core.test_schema_validation
& $py -m core.schemas.validator core\schemas\shell_model.schema.json examples\shell_models\retail_blank_shell.json
```

退出标准：

- `projects/sample_blank_shell/input/shell.manual.json` 能生成有效 `SHELL_MODEL` 和 `PROJECT_MODEL`。
- 没有 shell 边界时系统拒绝继续布局，而不是退回虚构默认空间并假装已理解图纸。

---

## Phase Q：几何底座 v1

目标：补齐布局必需的确定性几何能力。第一版不新增重依赖，先支持矩形和正交多边形。

文件：

- 创建：`core/geometry_backends/rect2d.py`
- 创建：`core/geometry_backends/orthogonal.py`
- 修改：`core/geometry_backends/registry.py`
- 创建：`tests/core/test_geometry_rect2d.py`
- 创建：`tests/core/test_geometry_orthogonal.py`
- 修改：`tests/core/test_geometry_backends.py`

任务：

- [x] 实现 bbox / rect 基础操作：面积、中心点、相交、包含、膨胀、扣减的保守近似。
- [x] 实现正交多边形基础校验：闭合、无自交、边水平/竖直、bbox、面积。
- [x] 实现 `subtract_no_place_zones()` 的第一版：对 bbox shell 先返回可布置矩形片段或保守不可用提示。
- [x] 实现 `path_to_rect_strips()`：把折线动线按宽度转换为一组矩形 strip，用于通道占地和碰撞检查。
- [x] 实现 `distance_to_opening_or_obstacle()` 的保守检查，用于门洞、柱子、消防避让。
- [x] 在 geometry backend registry 中把这些能力登记为默认后端。
- [x] 不引入 `shapely`、`cadquery` 等依赖；如后续要引入，单独问用户。

细化执行清单：

- [x] Q-01 `context-auditor`：盘点 `core/layout_engine/*` 中现有 bbox / collision / clearance 逻辑，列出可迁移函数。
- [x] Q-02 `unit-test-agent`：创建 `tests/core/test_geometry_rect2d.py`，先写面积、中心点、相交、包含、膨胀的红灯测试。
- [x] Q-03 `engine-agent`：创建 `core/geometry_backends/rect2d.py`，实现只依赖标准库的 rect 基础操作。
- [x] Q-04 `unit-test-agent`：补 `subtract_no_place_zones()` 的 bbox shell 测试，覆盖一个柱子把可布置区域切成左右片段的情况。
- [x] Q-05 `engine-agent`：实现保守扣减；无法可靠拆分时返回结构化 reason，不返回裸 `False`。
- [x] Q-06 `unit-test-agent`：创建 `tests/core/test_geometry_orthogonal.py`，覆盖闭合、非正交边、自交、面积、bbox。
- [x] Q-07 `engine-agent`：创建 `core/geometry_backends/orthogonal.py`，实现正交多边形基础校验，不引入新依赖。
- [x] Q-08 `unit-test-agent`：补 `path_to_rect_strips()` 测试，确保横向和纵向折线都能得到通道 strip。
- [x] Q-09 `engine-agent`：实现 `path_to_rect_strips()` 和 `distance_to_opening_or_obstacle()` 的保守版本。
- [x] Q-10 `engine-agent`：更新 `core/geometry_backends/registry.py`，登记 rect2d / orthogonal 能力和 known_limits。
- [x] Q-11 `unit-test-agent`：扩展 `tests/core/test_geometry_backends.py`，确认 registry 可发现新能力。
- [x] Q-12 `review-agent`：检查没有引入 `shapely`、`cadquery`、`numpy` 等新依赖；如确需引入，停止并问用户。
- [x] Q-13 `docs-sync-agent`：更新 `CORE_STATUS.md` 中 geometry backends 的能力与限制。

验证：

```powershell
& $py -m unittest tests.core.test_geometry_rect2d
& $py -m unittest tests.core.test_geometry_orthogonal
& $py -m unittest tests.core.test_geometry_backends
```

退出标准：

- layout engine 不再直接散落 bbox 算法，而是通过 geometry backend 调用。
- 所有几何失败都能返回结构化 reason，不只返回 `False`。

---

## Phase R：动线生成 v1

目标：从 shell、入口、必连通点和避让区生成可解释的动线候选。

文件：

- 修改：`core/layout_engine/circulation.py`
- 创建：`core/layout_engine/path_generation.py`
- 创建：`examples/circulation_models/retail_straight_spine.json`
- 创建：`examples/circulation_models/retail_l_spine.json`
- 创建：`tests/core/test_circulation_generation.py`
- 修改：`tests/core/test_layout_engine.py`

任务：

- [x] 定义动线候选策略接口：`generate_circulation_candidates(project_model, preferences) -> CIRCULATION_MODEL list`。
- [x] 实现 `straight_spine`：从主入口指向空间深处或目标点。
- [x] 实现 `l_spine`：入口到空间中心再到必连通点或远端。
- [x] 实现 `perimeter` 或 `along_wall`：沿边预留主动线，适合零售、展陈、办公边界场景。
- [x] 每条动线输出 `polyline`、`width`、`connects`、`path_surface`、`blocked_reasons`、`score`。
- [x] 动线必须检查是否压固定障碍、是否过窄、是否无法连接必连通点。
- [x] 场景 preferences 只能影响权重和优先级，不能写死 Core 动线。

细化执行清单：

- [x] R-01 `context-auditor`：确认 Phase P 的 `PROJECT_MODEL` 已包含入口、必连通点、避让区和 shell 边界。
- [x] R-02 `unit-test-agent`：创建 `tests/core/test_circulation_generation.py`，先写同一 retail shell 至少生成两个候选的红灯测试。
- [x] R-03 `engine-agent`：创建 `core/layout_engine/path_generation.py`，定义 `generate_circulation_candidates(project_model, preferences)` 返回结构。
- [x] R-04 `engine-agent`：实现 `straight_spine`，从主入口指向空间深处或指定 required connection。
- [x] R-05 `unit-test-agent`：补 `straight_spine` schema 字段测试，断言 `polyline`、`width`、`connects`、`path_surface`、`score` 存在。
- [x] R-06 `engine-agent`：实现 `l_spine`，优先连接入口、中心点和远端/必连通点。
- [x] R-07 `engine-agent`：实现 `along_wall` 或 `perimeter`，用于沿边主动线候选。
- [x] R-08 `unit-test-agent`：补障碍压线测试，确认失败候选保留 `blocked_reasons`，不静默丢弃。
- [x] R-09 `schema-contract-agent`：创建 `examples/circulation_models/retail_straight_spine.json` 和 `retail_l_spine.json`。
- [x] R-10 `unit-test-agent`：运行 circulation schema validator，修正 example 与 schema 字段不一致。
- [x] R-11 `review-agent`：检查场景 preferences 只影响权重，不在 Core 中写死 `retail`、`office` 对应路径算法。
- [x] R-12 `docs-sync-agent`：更新 `V-NONCAD-015` 状态和证据。

验证：

```powershell
& $py -m unittest tests.core.test_circulation_generation
& $py -m core.schemas.validator core\schemas\circulation_model.schema.json examples\circulation_models\retail_straight_spine.json
```

退出标准：

- 同一个空壳至少能生成 2 个动线候选。
- 候选失败时有明确 `blocked_reasons`，不静默丢弃。

---

## Phase S：功能区切分 v1

目标：把动线周边的可布置区域切成 `FUNCTION_ZONE` 候选，而不是直接摆对象。

文件：

- 创建：`core/layout_engine/zone_splitter.py`
- 修改：`core/schemas/function_zone.schema.json`
- 创建：`examples/function_zones/retail_zone_left.json`
- 创建：`examples/function_zones/office_zone_desk_band.json`
- 创建：`tests/core/test_zone_splitter.py`
- 修改：`tests/core/test_schema_validation.py`

任务：

- [x] 定义 `split_zones(shell_model, circulation_model, constraints) -> FUNCTION_ZONE list`。
- [x] 第一版支持 bbox shell：按动线 strip 的左右侧、端头和沿边区域切出候选区。
- [x] 每个 zone 输出 `geometry`、`area`、`depth`、`frontage`、`side_of_path`、`candidate_functions`、`constraints`、`score`。
- [x] 支持不可布置区和障碍物的保守扣减：无法可靠切分时降低分数并输出 uncertainty。
- [x] 实现基本 zone 质量评分：面积过小、深度不足、开口不足、离入口过远都要解释。
- [x] 不在 Core 写死公司功能名。Core 只输出通用候选功能，例如 `display`、`storage`、`desk_area`、`living`、`service`。

细化执行清单：

- [x] S-01 `context-auditor`：确认 Phase Q 的 `path_to_rect_strips()` 和 Phase R 的 `path_surface` 可被 zone splitter 复用。
- [x] S-02 `unit-test-agent`：创建 `tests/core/test_zone_splitter.py`，先写 bbox shell + straight spine 能切出左右 zone 的红灯测试。
- [x] S-03 `engine-agent`：创建 `core/layout_engine/zone_splitter.py`，定义 `split_zones(shell_model, circulation_model, constraints)`。
- [x] S-04 `engine-agent`：实现动线左右侧、端头和沿边 zone 的第一版 bbox 切分。
- [x] S-05 `unit-test-agent`：补不可布置区扣减测试，断言扣减失败时输出 uncertainty 和降分原因。
- [x] S-06 `engine-agent`：实现 zone 质量评分：面积、深度、frontage、入口距离、可达性。
- [x] S-07 `schema-contract-agent`：扩展 `function_zone.schema.json`，覆盖 `geometry`、`area`、`depth`、`frontage`、`side_of_path`、`candidate_functions`、`constraints`、`score`。
- [x] S-08 `schema-contract-agent`：创建 `examples/function_zones/retail_zone_left.json` 和 `office_zone_desk_band.json`。
- [x] S-09 `unit-test-agent`：扩展 `tests/core/test_schema_validation.py`，确认 zone examples 通过、坏 zone fixture 失败。
- [x] S-10 `review-agent`：扫描 Core 代码，确认没有写死公司业务功能名或单一场景术语。
- [x] S-11 `docs-sync-agent`：更新 `V-NONCAD-016` 状态和 `CORE_STATUS.md` 的 shell/circulation/function zones 行。

验证：

```powershell
& $py -m unittest tests.core.test_zone_splitter
& $py -m core.schemas.validator core\schemas\function_zone.schema.json examples\function_zones\retail_zone_left.json
```

退出标准：

- 一个空壳 + 一条动线能得到多个可解释 zone。
- zone 与动线、障碍、边界之间的关系可追踪。

---

## Phase T：对象与图块 Placement v1

目标：让布局不再只是顺排一个柜子，而是能按功能区放置多类通用对象，并在没有真实块库时用参数化对象 fallback。

文件：

- 创建：`core/layout_engine/placement.py`
- 修改：`core/object_engine/parametric_objects.py`
- 创建：`libraries/objects/object_defaults.json`
- 修改：`libraries/blocks/block_library.example.json`
- 修改：`core/block_engine/block_selector.py`
- 修改：`core/block_engine/block_placement.py`
- 创建：`examples/object_specs/desk_1400x700.json`
- 创建：`examples/object_specs/sofa_2200x900.json`
- 创建：`tests/core/test_placement_engine.py`
- 修改：`tests/core/test_object_engine.py`
- 修改：`tests/core/test_block_engine.py`

任务：

- [x] 将对象默认尺寸从代码常量逐步迁到 `libraries/objects/object_defaults.json`。
- [x] 扩展参数化对象：`desk`、`chair`、`bed`、`sofa`、`counter`、`display_unit`。
- [x] 定义 placement 策略：靠墙、沿动线朝向、成排、成组、端头重点、避让门洞。
- [x] 对每个 placement 输出 `object_id`、`zone_id`、`base_point`、`rotation`、`bbox`、`clearance_bbox`、`source`。
- [x] 接入 block selector：优先选择适配 block；找不到时生成 `OBJECT_SPEC` fallback。
- [x] 检查对象不压动线面、不压门洞、不压柱子、不越界、不互撞。
- [x] 对失败 placement 保留失败原因，允许 proposal 解释为什么少放或换对象。

细化执行清单：

- [x] T-01 `context-auditor`：盘点 `core/object_engine/parametric_objects.py`、`libraries/blocks/block_library.example.json` 和已有 block selector。
- [x] T-02 `unit-test-agent`：创建 `tests/core/test_placement_engine.py`，先写一个 zone 放置 `desk` 的红灯测试。
- [x] T-03 `schema-contract-agent`：创建 `libraries/objects/object_defaults.json`，先迁入 cabinet / shelf / table，保留现有行为。
- [x] T-04 `engine-agent`：修改 `parametric_objects.py`，从 object defaults 读取尺寸；缺配置时返回结构化错误。
- [x] T-05 `unit-test-agent`：扩展 `tests/core/test_object_engine.py`，覆盖 `desk`、`chair`、`sofa`、`counter`、`display_unit` 的最小 `OBJECT_SPEC`。
- [x] T-06 `engine-agent`：扩展参数化对象生成，确保每类对象有 bbox、base_point、rotation 和 component roles。
- [x] T-07 `engine-agent`：创建 `core/layout_engine/placement.py`，实现靠墙、沿动线朝向、成排、成组、端头重点等策略的保守版本。
- [x] T-08 `unit-test-agent`：补对象不压动线、不越界、不互撞、不压门洞/柱子的失败测试。
- [x] T-09 `engine-agent`：接入 `block_selector.py` 和 `block_placement.py`，优先 block metadata，失败时 fallback 到 `OBJECT_SPEC`。
- [x] T-10 `schema-contract-agent`：扩展 `libraries/blocks/block_library.example.json`，确保至少 5 类对象可被选择或 fallback。
- [x] T-11 `schema-contract-agent`：创建 `examples/object_specs/desk_1400x700.json` 和 `sofa_2200x900.json` 并跑 schema validator。
- [x] T-12 `review-agent`：检查 placement 不是硬编码坐标列表，而是由 zone、对象尺寸和策略驱动。
- [x] T-13 `docs-sync-agent`：更新 `V-NONCAD-017` 状态和对象/块能力说明。

验证：

```powershell
& $py -m unittest tests.core.test_placement_engine
& $py -m unittest tests.core.test_object_engine
& $py -m unittest tests.core.test_block_engine
& $py -m core.schemas.validator core\schemas\object_spec.schema.json examples\object_specs\desk_1400x700.json
```

退出标准：

- 至少 5 类对象能参与同一个 layout candidate。
- 对象放置由 zone 和规则驱动，不由硬编码坐标列表驱动。

---

## Phase U：多候选 Proposal 与确认门强化

目标：把 layout candidates 转成真正可比较的设计方案，用户确认前不落图。

文件：

- 修改：`core/proposal_engine/design_proposal.py`
- 修改：`core/proposal_engine/proposal_comparison.py`
- 修改：`core/proposal_engine/proposal_to_plan.py`
- 修改：`core/schemas/design_proposal.schema.json`
- 创建：`examples/design_proposals/blank_shell_retail_options.json`
- 创建：`tests/core/test_proposal_multi_candidate.py`
- 修改：`tests/core/test_proposal_engine.py`
- 修改：`tests/core/test_proposal_comparison.py`

任务：

- [x] `DESIGN_PROPOSAL` 支持多个候选方案，而不是只包装一个 layout。
- [x] 每个候选输出 summary、优点、风险、失败检查、适用场景、需要用户确认的问题。
- [x] `proposal_comparison` 同时考虑通用评分和场景权重，但权重来源必须可追踪。
- [x] `needs_confirmation=true` 时，`proposal_to_plan` 和 `model_to_plans` 必须继续阻断。
- [x] 允许 `confirmed_candidate_id` 指定要转成 CAD_PLAN 的候选。
- [x] proposal 中的 evidence 必须区分 `from_user`、`from_drawing`、`from_shell`、`from_library`、`from_algorithm`、`inferred`。

细化执行清单：

- [x] U-01 `context-auditor`：盘点 `design_proposal.py`、`proposal_comparison.py`、`proposal_to_plan.py` 和现有 confirmation tests。
- [x] U-02 `unit-test-agent`：创建 `tests/core/test_proposal_multi_candidate.py`，先写多候选 proposal schema 红灯。
- [x] U-03 `schema-contract-agent`：扩展 `design_proposal.schema.json`，支持 `candidates[]`、`confirmed_candidate_id`、`comparison_summary`。
- [x] U-04 `engine-agent`：修改 `design_proposal.py`，把多个 layout candidates 包装为多个可比较方案。
- [x] U-05 `unit-test-agent`：补每个候选必须包含 summary、优点、风险、失败检查、适用场景和确认问题的测试。
- [x] U-06 `engine-agent`：增强 `proposal_comparison.py`，把通用评分、场景权重和失败原因合并为可解释排序。
- [x] U-07 `unit-test-agent`：补权重来源可追踪测试，防止场景偏好变成隐式魔法常量。
- [x] U-08 `engine-agent`：修改 `proposal_to_plan.py` 和 `model_to_plans`，确保 `needs_confirmation=true` 时继续阻断。
- [ ] U-09 `unit-test-agent`：补 `confirmed_candidate_id` 测试，确认只转换被确认候选。
- [ ] U-10 `schema-contract-agent`：创建 `examples/design_proposals/blank_shell_retail_options.json` 并跑 schema validator。
- [ ] U-11 `review-agent`：检查 proposal evidence 来源字段完整，尤其区分 `from_shell`、`from_algorithm` 和 `inferred`。
- [ ] U-12 `docs-sync-agent`：更新 `CORE_STATUS.md` 的 proposal_engine / plan_engine 限制。

验证：

```powershell
& $py -m unittest tests.core.test_proposal_multi_candidate
& $py -m unittest tests.core.test_proposal_engine
& $py -m unittest tests.core.test_proposal_comparison
& $py -m core.schemas.validator core\schemas\design_proposal.schema.json examples\design_proposals\blank_shell_retail_options.json
```

退出标准：

- 用户能看到“为什么推荐 A，不推荐 B”。
- 未确认方案不能生成可执行 CAD_PLAN。

---

## Phase V：空壳端到端 Pipeline 与 Benchmark Suite

目标：形成真正代表可用 Alpha 的非 CAD 端到端闭环，并用 benchmark 防止回退。

文件：

- 创建：`core/workflows/blank_shell_pipeline.py`
- 修改：`core/workflows/non_cad_pipeline.py`
- 创建：`scripts/run_blank_shell_pipeline.py`
- 创建：`examples/workflows/blank_shell_layout_loop.json`
- 创建：`examples/workflows/blank_shell_office_layout_loop.json`
- 创建：`examples/workflows/blank_shell_residential_layout_loop.json`
- 创建：`examples/workflows/blank_shell_restaurant_layout_loop.json`
- 创建：`examples/benchmarks/blank_shell_core_benchmark.json`
- 创建：`projects/sample_blank_shell/expected/expected_notes.md`
- 创建：`examples/shell_models/office_small_suite_shell.json`
- 创建：`examples/shell_models/residential_living_room_shell.json`
- 创建：`examples/shell_models/restaurant_small_front_shell.json`
- 创建：`agents/restaurant/preferences.json`
- 创建：`tests/core/test_blank_shell_pipeline.py`
- 修改：`core/capabilities/registry.py`
- 修改：`tests/core/test_benchmarks.py`
- 修改：`tests/core/test_benchmark_cli.py`

任务：

- [x] 新增 pipeline：`shell -> project -> circulation candidates -> zones -> placements -> layout proposal -> design proposal -> CAD_PLAN -> dry-run -> verification report`。
- [x] 所有中间 artifact 写入 `output/test_artifacts/blank_shell_pipeline/<case>/` 或 benchmark 对应 case 输出目录。
- [x] 每个 artifact 通过对应 schema 或结构化校验；shell examples、layout/proposal/CAD_PLAN/dry-run/report 均有专项测试或 pipeline 结构断言。
- [x] 生成 CAD_PLAN 后必须跑 validate 和 dry-run；失败则 pipeline status 为 `blocked` 或 `invalid`。
- [x] benchmark case 至少包括：`retail_blank_shell`、`office_small_suite`、`residential_living_room`、`restaurant_small_front`。
- [x] 每个 benchmark 记录关键断言：候选数、zone 数、placement 数、失败检查数、CAD_PLAN validate、dry-run status、verification status。
- [x] benchmark 汇总输出 pass/fail 和失败原因，不能只有异常堆栈。

细化执行清单：

- [x] V-01 `context-auditor`：确认 P-U 的核心入口都能在无 CAD 环境中调用，并列出每一步输入输出模型。
- [x] V-02 `unit-test-agent`：创建 `tests/core/test_blank_shell_pipeline.py`，先写 pipeline 可以产出 artifacts 清单的红灯测试。
- [x] V-03 `pipeline-agent`：创建 `core/workflows/blank_shell_pipeline.py`，按 `shell -> project -> circulation -> zones -> placements -> layout -> proposal -> CAD_PLAN -> dry-run -> verification` 串联。
- [x] V-04 `pipeline-agent`：让每个 artifact 写入 `output/test_artifacts/blank_shell_pipeline/<case>/`，文件名稳定且可重复覆盖。
- [x] V-05 `unit-test-agent`：补 artifact schema 校验测试，任何中间产物无效时 pipeline status 必须为 `invalid` 或 `blocked`。
- [x] V-06 `pipeline-agent`：创建 `scripts/run_blank_shell_pipeline.py` 薄包装器，按既有脚本模式处理项目根路径。
- [x] V-07 `unit-test-agent`：扩展 `tests/core/test_benchmark_cli.py`，覆盖脚本直接运行和 JSON summary 输出。
- [x] V-08 `schema-contract-agent`：创建 `examples/workflows/blank_shell_layout_loop.json`，描述 case、input、preferences、output_dir。
- [x] V-09 `pipeline-agent`：创建 `examples/benchmarks/blank_shell_core_benchmark.json`，包含 retail、office、residential、restaurant 四个 case。
- [x] V-10 `unit-test-agent`：扩展 `tests/core/test_benchmarks.py`，断言每个 case 至少记录 candidates、zones、placements、validate、dry-run、verification status。
- [x] V-11 `pipeline-agent`：创建 `projects/sample_blank_shell/expected/expected_notes.md`，记录可解释的非 CAD 预期，不写成正式图纸验收。
- [x] V-12 `review-agent`：检查 benchmark pass 不依赖真实 CAD，不把 `unverified` 误报成 `geometry_verified`。
- [x] V-13 `docs-sync-agent`：更新 `V-NONCAD-018`、`V-NONCAD-019` 状态和证据路径。

验证：

```powershell
& $py -m unittest tests.core.test_blank_shell_pipeline
& $py -m unittest tests.core.test_benchmarks tests.core.test_benchmark_cli
& $py scripts\run_blank_shell_pipeline.py examples\workflows\blank_shell_layout_loop.json --output-dir output\test_artifacts\blank_shell_pipeline\manual
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\blank_shell_manual
```

退出标准：

- 不打开 CAD 的情况下，空壳布局完整链路可以重复跑。
- 至少 4 个 benchmark case pass。
- 产出的 verification report 在没有 CAD 证据时明确为 `unverified`，不声称准确。

---

## Phase W：真实 CAD 回读闭环补验

目标：把 `CODEX_PREVIEW` 落图、截图、实体回读和 `VERIFICATION_REPORT.geometry_verified` 真正闭合。

前置条件：

- 用户已打开 AutoCAD 和一个测试 DWG。
- 用户允许在 `CODEX_PREVIEW` 图层执行预览绘制。
- 不保存 DWG，不修改正式图层。
- 执行前先读取 `CAD_AGENT_AUTONOMOUS_VALIDATION.md`，按其失败分类处理，不在第一处失败时停止。

文件：

- 修改：`core/execution/execute_plan.py`
- 修改：`core/cad_io/autocad_com.py`
- 修改：`core/verification/inspect_dwg.py`
- 修改：`core/verification/verification_report.py`
- 参考：`CAD_AGENT_AUTONOMOUS_VALIDATION.md`
- 创建：`docs/verification/cad_readback_alpha_check.md`
- 修改：`tests/core/test_execute_plan.py`
- 修改：`tests/core/test_verification_report.py`

任务：

- [ ] `execute_plan` 输出本次执行摘要：`run_id`、`created_handles`、目标 layer、plan_id。
- [ ] `inspect_dwg --connect-cad` 支持按 `created_handles` 或 before/after snapshot 隔离本次新增实体。
- [ ] `snapshot_modelspace()` 对 line/text/dimension/block reference 做稳定标准化。
- [ ] `VERIFICATION_REPORT` 同时比较预期对象数量、bbox、基点、图层、文字、标注和 readback scope。
- [ ] 截图证据必须检查文件真实存在，并挂入报告。
- [ ] 如果 CAD 或截图不可用，报告保留 `unverified`，并写清楚缺失证据。
- [ ] 将 `scripts/run_cad_validation.py` 生成的 `report.json` 和 `report.md` 作为本 phase 的总证据；仓库内失败必须最小修复并复验，外部失败登记为 `external_blocker`。

细化执行清单：

- [ ] W-01 `context-auditor`：读取 `CAD_AGENT_AUTONOMOUS_VALIDATION.md`，确认当前环境是否允许真实 CAD 验证。
- [ ] W-02 `cad-validation-agent`：运行 `scripts/run_cad_validation.py --no-cad`，先确认仓库非 CAD 基线没有回归。
- [ ] W-03 `unit-test-agent`：扩展 `tests/core/test_execute_plan.py`，先写执行摘要必须包含 `run_id`、`plan_id`、`target_layer`、`created_handles` 的红灯测试。
- [ ] W-04 `engine-agent`：修改 `core/execution/execute_plan.py`，输出稳定执行摘要；无真实 CAD 时 recording driver 也能返回模拟 handles。
- [ ] W-05 `unit-test-agent`：扩展 `tests/core/test_verification_report.py`，覆盖 created handles 不完整时不得升级 `geometry_verified`。
- [ ] W-06 `engine-agent`：修改 `inspect_dwg.py`，支持 `--execution-summary` 与 before/after snapshot 两条隔离路径。
- [ ] W-07 `engine-agent`：增强 `AutoCADComDriver.snapshot_modelspace()` 标准化 line/text/dimension/block reference。
- [ ] W-08 `unit-test-agent`：补截图路径不存在时只能 `unverified` 或失败的测试。
- [ ] W-09 `cad-validation-agent`：在用户已打开 CAD 和测试 DWG 时运行 `scripts/run_cad_validation.py --output-dir output\validation_runs\cad-readback-alpha`。
- [ ] W-10 `cad-validation-agent`：读取 `report.json`，若 `status=fail` 且分类为仓库内问题，交给对应 `engine-agent` 最小修复并复验。
- [ ] W-11 `cad-validation-agent`：若 `status=external_blocker`，只列用户需要处理的 CAD / 依赖 / 窗口事项，不把它写成 Core 失败。
- [ ] W-12 `docs-sync-agent`：创建或更新 `docs/verification/cad_readback_alpha_check.md`，记录命令、报告路径、截图路径、readback report 和最终状态。
- [ ] W-13 `review-agent`：检查 Phase W 没有保存 DWG、覆盖原图、删除实体或修改正式图层。
- [ ] W-14 `docs-sync-agent`：更新 `V-CAD-001` 到 `V-CAD-005`，失败时同步 `CAD_AGENT_ISSUES.md`。

最低必跑探针：

```powershell
& $py scripts\self_check.py
& $py scripts\render_preview.py --check
```

CAD 可用时执行：

```powershell
& $py scripts\run_cad_validation.py --output-dir output\validation_runs\cad-readback-alpha
```

退出标准：

- `V-CAD-001` 到 `V-CAD-005` 至少对 baseline cabinet 有一次真实通过记录。
- `output\validation_runs\cad-readback-alpha\report.json` 的 `status` 为 `pass`；若为 `external_blocker`，已列出用户需要处理的 CAD 环境事项。
- 若失败，更新 `CAD_AGENT_ISSUES.md`，不能把失败图纸交付为完成品。

---

## Phase X：场景 Agent 接入与 Alpha 验收

目标：让场景 Agent 真正复用 Core，而不是复制算法；用场景差异证明 Core 可迁移。

文件：

- 修改：`agents/commercial_fitout/preferences.json`
- 修改：`agents/residential/preferences.json`
- 修改：`agents/office/preferences.json`
- 创建：`agents/restaurant/preferences.json`
- 修改：`agents/SCENE_AGENT_RULES.md`
- 修改：`core/capabilities/registry.py`
- 创建：`tests/agents/test_blank_shell_scene_preferences.py`
- 修改：`tests/agents/test_scene_agent_boundaries.py`
- 修改：`tests/agents/test_scene_preferences.py`

任务：

- [ ] 为 commercial/residential/office/restaurant 定义空壳布局偏好：通道宽度、对象优先级、zone 权重、placement 偏好。
- [ ] Core 只读取偏好数据，不在 Core 中写死场景名对应算法。
- [ ] 同一 shell 输入在不同场景 preferences 下应产出不同候选排序或对象组合。
- [ ] Agent workflow 文档只描述业务流程和偏好输入，不实现 CAD、回读、碰撞、几何算法。
- [x] capability registry 暴露 `workflow.blank_shell_pipeline`，并标明不依赖 CAD 的验证命令（已在 Phase V 提前完成）。

细化执行清单：

- [ ] X-01 `context-auditor`：盘点 `agents/*/preferences.json`、`agents/SCENE_AGENT_RULES.md` 和现有 agent boundary tests。
- [ ] X-02 `unit-test-agent`：创建 `tests/agents/test_blank_shell_scene_preferences.py`，先写同一 shell 在不同 preferences 下排序不同的红灯测试。
- [ ] X-03 `pipeline-agent`：为 `commercial_fitout`、`residential`、`office`、`restaurant` 定义通道宽度、对象优先级、zone 权重、placement 偏好。
- [ ] X-04 `pipeline-agent`：确认 Core 只读取 preferences 数据，不在 Core 中写死场景名分支。
- [ ] X-05 `unit-test-agent`：扩展 `tests/agents/test_scene_agent_boundaries.py`，继续扫描场景层不得实现 CAD 执行、回读、碰撞、几何算法。
- [x] X-06 `pipeline-agent`：在 capability registry 暴露 `workflow.blank_shell_pipeline`，写清输入 schema、输出 contract、CAD 依赖为否、验证命令（Phase V 已完成）。
- [ ] X-07 `unit-test-agent`：扩展 `tests/agents/test_scene_preferences.py`，覆盖 preferences 缺字段时的明确失败原因。
- [ ] X-08 `pipeline-agent`：用 blank shell benchmark 跑至少 3 个场景 preferences，确认候选排序或对象组合存在差异。
- [ ] X-09 `review-agent`：检查场景 Agent workflow 文档只描述业务流程和偏好输入，不复制 Core 算法。
- [ ] X-10 `docs-sync-agent`：更新 `CORE_STATUS.md` 中场景 Agent 状态，仍标注为轻量复用层。
- [ ] X-11 `docs-sync-agent`：更新 `CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md` 和完成判定证据。
- [ ] X-12 主 Codex：汇总 Alpha 验收结果，明确哪些是非 CAD Alpha 通过，哪些仍需真实 CAD 或真实项目补验。

验证：

```powershell
& $py -m unittest discover -s tests\agents
& $py -m unittest tests.core.test_capabilities
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\scene_manual
```

退出标准：

- 至少 3 个场景 Agent 能复用同一 blank shell pipeline。
- Agent 边界扫描仍通过，场景层不出现 Core 算法复制。

---

## 6. 每轮开发固定自检

每完成一个 phase，至少运行两层验证：本 phase 的专项验证命令，以及下面的固定基线。若本 phase 只修改文档，可不跑完整单测，但必须做文本自查，确认没有引用不存在的执行入口或留下不可执行占位。

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"

& $py -m unittest discover -s tests
& $py scripts\self_check.py
& $py scripts\validate_plan.py examples\plans\draw_test_cabinet.json
& $py scripts\dry_run_plan.py examples\plans\draw_test_cabinet.json
& $py scripts\render_preview.py --check
& $py scripts\inspect_dwg.py --plan examples\plans\draw_test_cabinet.json --format json --no-cad
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\phase-manual-no-cad
```

如果涉及 benchmark：

```powershell
& $py scripts\run_benchmark_suite.py examples\benchmarks\non_cad_core_benchmark.json --output-root output\test_artifacts\benchmarks\manual
```

如果涉及空壳 pipeline：

```powershell
& $py scripts\run_blank_shell_pipeline.py examples\workflows\blank_shell_layout_loop.json --output-dir output\test_artifacts\blank_shell_pipeline\manual
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\blank_shell_manual
```

如果涉及真实 CAD：

```powershell
& $py scripts\run_cad_validation.py --output-dir output\validation_runs\manual-cad-check
```

如果只修改本文档，至少做：

```powershell
rg -n "TB[D]|TO[D]O|以后再[说]|补一[下]|随[便]|先占[位]" CORE_RESTRUCTURE_PLAN.md README.md CAD_AGENT_STATUS.md
rg -n "Phase A[-]N|A[-]M" CORE_RESTRUCTURE_PLAN.md README.md CAD_AGENT_STATUS.md
rg -n "run_cad_validation|run_blank_shell_pipeline|shell_loader" CORE_RESTRUCTURE_PLAN.md
```

---

## 7. 停下来问用户的分歧点

以下事项不要擅自定死：

- 是否引入成熟几何库，例如 `shapely`，还是继续自研正交多边形能力。
- 是否优先自动 DWG/PDF 识别，还是继续人工标注 JSON 闭环。
- 是否接入真实公司块库，还是继续用 `libraries/blocks/*.json` 元数据。
- 首个真实场景验收优先选择 `commercial_fitout`、`residential`、`office` 还是 `restaurant`。
- 是否允许低风险 proposal 自动转 CAD_PLAN；默认仍需要用户确认。
- 是否允许正式图层、保存、覆盖或删除操作；默认全部不允许。

---

## 8. 本文交付自检

在把本文交给 Codex 执行前，先完成下面检查：

- [ ] `CORE_RESTRUCTURE_PLAN.md` 中所有 phase 均有文件清单、任务、验证命令和退出标准。
- [ ] `Phase O-X` 是唯一当前执行口径；旧字母阶段只能作为历史描述出现，不能作为下一步执行路线。
- [ ] 所有 `scripts/*.py` 引用都要么已存在，要么在对应 phase 的“文件”清单中标为“创建”。
- [ ] 所有 CAD 命令都默认使用 `CODEX_PREVIEW`，并且有不保存、不覆盖、不删除的安全边界。
- [ ] 所有真实 CAD 结果都必须通过 `scripts/run_cad_validation.py` 或等价 readback 证据归档，不能只凭截图声称准确。
- [ ] 每个 phase 都能独立回答：输入是什么、输出是什么、怎么测试、失败如何分类、证据放在哪里。
- [ ] 执行者能从本文判断何时继续、何时修复、何时登记 `external_blocker`、何时必须问用户。

文本自查命令：

```powershell
rg -n "TB[D]|TO[D]O|以后再[说]|补一[下]|类[似]|随[便]|先占[位]" CORE_RESTRUCTURE_PLAN.md
rg -n "Phase A[-]N|A[-]M|A[-]N" CORE_RESTRUCTURE_PLAN.md CAD_AGENT_STATUS.md README.md
```

---

## 9. 完成判定

只有同时满足下面条件，才可以说“Core 可用 Alpha 基本完成”：

- Phase O-X 的非 CAD 测试和 benchmark 全部通过。
- 空壳 pipeline 至少 4 个 benchmark case 通过。
- 生成的 `CAD_PLAN` 均通过 validate 和 dry-run。
- `CODEX_PREVIEW` 安全策略没有被绕过。
- 真实 CAD 可用时，baseline cabinet 至少完成一次落图、截图、实体回读闭环。
- 若真实 CAD 不可用，所有相关结果明确标记为 `unverified`，并保留 CAD 补验清单。
- `CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md` 已同步更新；若过程出现失败或教训，`CAD_AGENT_ISSUES.md` 已记录。

如果用户只要求讨论本文档，不执行任何 phase；如果本文档发生工作流或交付规则变更，仍按根目录 `AGENTS.md` 同步更新状态和变更记录。
