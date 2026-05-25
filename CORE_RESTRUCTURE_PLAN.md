# CAD Agent Core 可用化深水开发计划

状态：下一轮 Core 可用 Alpha 开发计划  
最后更新：2026-05-25

> 面向后续 Codex / agentic worker：本文是当前仓库的主计划文件。执行计划前必须先读取根目录 `AGENTS.md` 要求的上下文文件；实现时按任务勾选推进，所有阶段都必须保留验证证据。用户提到 `plan.md` 时，默认指本文。

本文已从旧版 A-N 已完成清单整理为“接下来还要做什么”。已完成历史只保留摘要，详细记录见 `CORE_STATUS.md`、`CORE_ROADMAP.md`、`CAD_AGENT_STATUS.md` 和 `CAD_AGENT_CHANGELOG.md`。

本轮纳入 `SHELL_LAYOUT_FOUNDATION_DESIGN.md` 的设计思路，但不修改该文档。空壳布局底座不再作为旁支蓝图，而是下一轮让 Core 变得可用的主线。

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
- 本文没有英文待办标记、中文“以后再处理”式表达，或其他不可执行占位。

---

## 0. 当前判断

当前 Core 已有很多原型，但还没有达到“能用”的程度。原因不是缺少目录或 schema，而是缺少可稳定产出合理方案的深层能力：

| 缺口 | 当前状态 | 为什么影响可用 |
| --- | --- | --- |
| 空壳理解 | 有 `SHELL_MODEL` schema 和手工样例，但主流程仍以简化 `DRAWING_MODEL.spaces` 为主 | 真实布局不能只靠一个 bbox，需要入口、洞口、柱子、消防、不可布置区和连通点 |
| 几何底座 | 只有 bbox、简单碰撞、clearance 和剩余深度通道检查 | 无法切动线面、功能区、避让区，也无法解释复杂布局失败原因 |
| 布局生成 | `create_layout_candidates()` 基本是横向顺排对象 | 不能生成多种动线、功能区，也不能做真实候选方案 |
| 对象与图块 | 参数化对象只有 cabinet / shelf / table 深度原型 | 不能覆盖办公、家装、零售、餐饮等基本场景的常用对象 |
| 方案推理 | proposal 可以包装说明和确认门，但不是强方案引擎 | 不能根据候选布局给出有差异的方案、取舍和风险 |
| 端到端样例 | 有最小非 CAD pipeline 和 benchmark | 样例太单一，不能代表“空壳到布局”的实际流程 |
| CAD 验证 | `execute_plan`、截图、readback 都有入口 | 真实 AutoCAD 回读闭环仍待实机验证，不能声称几何准确 |
| 能力编排 | capability registry 已存在 | 还没有把 shell -> circulation -> zones -> placement -> proposal -> plan 串成可发现能力链 |

本轮目标不是做“完整自动设计系统”，而是把 Core 推到可用 Alpha：

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
- 已有 `projects/sample_blank_shell/input/shell.manual.json`，但它还没有成为真正的空壳布局主流程输入。
- 最近基线记录为 109 项单元测试通过，`self_check.py` pass，`render_preview.py --check` ready，非 CAD benchmark pass。

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
| V-NONCAD-014 | `SHELL_MODEL` 成为布局主输入 | 未开始 | schema、manual loader 单测 | 否 | 样例空壳可生成 project/circulation/zones |
| V-NONCAD-015 | 直线/L 型/沿边动线候选 | 未开始 | circulation 单测、benchmark | 否 | 同一 shell 至少生成 2 个可解释候选 |
| V-NONCAD-016 | 功能区切分 | 未开始 | zone splitter 单测、schema 校验 | 否 | 动线两侧或沿边可生成多个功能区 |
| V-NONCAD-017 | 多类别对象 placement | 未开始 | placement 单测、plan 转换测试 | 否 | 至少 5 类对象可放置并输出 bbox/rotation |
| V-NONCAD-018 | 空壳布局 benchmark suite | 未开始 | benchmark runner | 否 | 至少 4 个场景 case 可重复 pass/fail |
| V-NONCAD-019 | 空壳 pipeline capability chain | 未开始 | capability registry 测试 | 否 | shell/layout/proposal/plan 能力可发现、可验证 |

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

- [ ] 运行完整非 CAD 基线命令，记录通过项和失败项。
- [ ] 运行 `scripts/run_cad_validation.py --no-cad`，把结构化报告作为 Phase O 证据。
- [ ] 在 capability catalog 中为每个能力增加 `maturity` 字段：`prototype`、`alpha_ready`、`blocked_by_cad`、`not_started`。
- [ ] 为 capability 增加 `known_limits` 字段，写明当前能力不能做什么。
- [ ] 在 `CORE_STATUS.md` 中把 `layout_engine`、`drawing_analysis`、`proposal_engine`、`verification` 的限制写清楚。
- [ ] 对齐 `README.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md` 和本文中的 Phase O-X 口径，清掉旧字母阶段的执行口径残留。
- [ ] 若验证失败，先按 `CAD_AGENT_BLOCKER_PLAYBOOK.md` 处理，不继续进入 Phase P。

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

- [ ] 扩展 `SHELL_MODEL`，支持 `boundary.type = bbox|polygon|orthogonal_polygon`。第一版计算仍可只完整支持 bbox 和正交多边形，任意 polygon 先标记为有限支持。
- [ ] 在 `SHELL_MODEL` 中加入 `openings`、`fixed_obstacles`、`no_place_zones`、`required_connections`、`building_elements`、`uncertainties`、`source`。
- [ ] 写 `load_manual_shell(path)`，把人工 JSON 规范化为 `SHELL_MODEL`，并校验单位、边界、洞口宽度、避让区 bbox。
- [ ] 兼容旧 `DRAWING_MODEL.spaces` 输入：`project_builder` 可从 `shell_model` 或旧 drawing spaces 构建项目模型。
- [ ] `PROJECT_MODEL` 保留 `shell_id`、`space_id`、约束、待确认问题和来源证据。
- [ ] 注册 capability：`drawing_analysis.load_shell_model`。
- [ ] 为错误输入补反例：边界无效、入口缺宽度、避让区越界、单位缺失。

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

- [ ] 实现 bbox / rect 基础操作：面积、中心点、相交、包含、膨胀、扣减的保守近似。
- [ ] 实现正交多边形基础校验：闭合、无自交、边水平/竖直、bbox、面积。
- [ ] 实现 `subtract_no_place_zones()` 的第一版：对 bbox shell 先返回可布置矩形片段或保守不可用提示。
- [ ] 实现 `path_to_rect_strips()`：把折线动线按宽度转换为一组矩形 strip，用于通道占地和碰撞检查。
- [ ] 实现 `distance_to_opening_or_obstacle()` 的保守检查，用于门洞、柱子、消防避让。
- [ ] 在 geometry backend registry 中把这些能力登记为默认后端。
- [ ] 不引入 `shapely`、`cadquery` 等依赖；如后续要引入，单独问用户。

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

- [ ] 定义动线候选策略接口：`generate_circulation_candidates(project_model, preferences) -> CIRCULATION_MODEL list`。
- [ ] 实现 `straight_spine`：从主入口指向空间深处或目标点。
- [ ] 实现 `l_spine`：入口到空间中心再到必连通点或远端。
- [ ] 实现 `perimeter` 或 `along_wall`：沿边预留主动线，适合零售、展陈、办公边界场景。
- [ ] 每条动线输出 `polyline`、`width`、`connects`、`path_surface`、`blocked_reasons`、`score`。
- [ ] 动线必须检查是否压固定障碍、是否过窄、是否无法连接必连通点。
- [ ] 场景 preferences 只能影响权重和优先级，不能写死 Core 动线。

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

- [ ] 定义 `split_zones(shell_model, circulation_model, constraints) -> FUNCTION_ZONE list`。
- [ ] 第一版支持 bbox shell：按动线 strip 的左右侧、端头和沿边区域切出候选区。
- [ ] 每个 zone 输出 `geometry`、`area`、`depth`、`frontage`、`side_of_path`、`candidate_functions`、`constraints`、`score`。
- [ ] 支持不可布置区和障碍物的保守扣减：无法可靠切分时降低分数并输出 uncertainty。
- [ ] 实现基本 zone 质量评分：面积过小、深度不足、开口不足、离入口过远都要解释。
- [ ] 不在 Core 写死公司功能名。Core 只输出通用候选功能，例如 `display`、`storage`、`desk_area`、`living`、`service`。

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

- [ ] 将对象默认尺寸从代码常量逐步迁到 `libraries/objects/object_defaults.json`。
- [ ] 扩展参数化对象：`desk`、`chair`、`bed`、`sofa`、`counter`、`display_unit`。
- [ ] 定义 placement 策略：靠墙、沿动线朝向、成排、成组、端头重点、避让门洞。
- [ ] 对每个 placement 输出 `object_id`、`zone_id`、`base_point`、`rotation`、`bbox`、`clearance_bbox`、`source`。
- [ ] 接入 block selector：优先选择适配 block；找不到时生成 `OBJECT_SPEC` fallback。
- [ ] 检查对象不压动线面、不压门洞、不压柱子、不越界、不互撞。
- [ ] 对失败 placement 保留失败原因，允许 proposal 解释为什么少放或换对象。

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

- [ ] `DESIGN_PROPOSAL` 支持多个候选方案，而不是只包装一个 layout。
- [ ] 每个候选输出 summary、优点、风险、失败检查、适用场景、需要用户确认的问题。
- [ ] `proposal_comparison` 同时考虑通用评分和场景权重，但权重来源必须可追踪。
- [ ] `needs_confirmation=true` 时，`proposal_to_plan` 和 `model_to_plans` 必须继续阻断。
- [ ] 允许 `confirmed_candidate_id` 指定要转成 CAD_PLAN 的候选。
- [ ] proposal 中的 evidence 必须区分 `from_user`、`from_drawing`、`from_shell`、`from_library`、`from_algorithm`、`inferred`。

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
- 创建：`examples/benchmarks/blank_shell_core_benchmark.json`
- 创建：`projects/sample_blank_shell/expected/expected_notes.md`
- 创建：`tests/core/test_blank_shell_pipeline.py`
- 修改：`tests/core/test_benchmarks.py`
- 修改：`tests/core/test_benchmark_cli.py`

任务：

- [ ] 新增 pipeline：`shell -> project -> circulation candidates -> zones -> placements -> layout proposal -> design proposal -> CAD_PLAN -> dry-run -> verification report`。
- [ ] 所有中间 artifact 写入 `output/test_artifacts/blank_shell_pipeline/<case>/`。
- [ ] 每个 artifact 通过对应 schema 或结构化校验。
- [ ] 生成 CAD_PLAN 后必须跑 validate 和 dry-run；失败则 pipeline status 为 `blocked` 或 `invalid`。
- [ ] benchmark case 至少包括：`retail_blank_shell`、`office_small_suite`、`residential_living_room`、`restaurant_small_front`。
- [ ] 每个 benchmark 记录关键断言：候选数、zone 数、placement 数、失败检查数、CAD_PLAN validate、dry-run status、verification status。
- [ ] benchmark 汇总输出 pass/fail 和失败原因，不能只有异常堆栈。

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
- [ ] capability registry 暴露 `workflow.blank_shell_pipeline`，并标明不依赖 CAD 的验证命令。

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
