# CAD Agent 问题与修复记录

这个文件只记录开发和测试过程中遇到的问题。它不是普通日志，而是“以后别再踩同一个坑”的记录。

## 记录模板

```md
## 问题：一句话概括

日期：

现象：

影响：

原因：

修复：

以后规则：

相关文件：
```

## 已知问题

### 问题：legacy driver wrapper 保留本地 `sys.path.insert` 会漏过共享 bootstrap 收敛

日期：2026-05-25

现象：
系统层 repo audit 首轮通过代码迁移后，`drivers/autocad_com.py`、`drivers/dxf_writer.py`、`drivers/zwcad_com.py` 仍各自保留 `sys.path.insert(0, ...)`。

影响：
长期兼容入口和脚本入口的导入策略不一致；后续如果继续复制这种 wrapper 写法，会让路径污染重新扩散，repo audit 也会留下可修复 findings。

原因：
上一轮先收敛了 `scripts/*.py` 和 `tests/core/*.py`，但 legacy driver wrapper 被当作低风险兼容层，没有同步迁移到共享 bootstrap。

修复：
三个 driver wrapper 已改为复用 `scripts._bootstrap.PROJECT_ROOT`，删除本地 `sys` / `Path` / `sys.path.insert`；`scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings` 现在为 0 findings。

以后规则：
兼容 wrapper 也必须复用共享 bootstrap；除 `scripts/_bootstrap.py`、`tests/bootstrap.py` 和测试 fixture 外，不新增直接 `sys.path.insert(...)`。

相关文件：
- `drivers/autocad_com.py`
- `drivers/dxf_writer.py`
- `drivers/zwcad_com.py`
- `scripts/_bootstrap.py`
- `scripts/run_repo_audit.py`
- `core/maintenance/repo_audit.py`
- `tests/core/test_repo_audit.py`

### 问题：repo audit 只抓 `sys.path.insert` 会漏掉其他路径污染形态

日期：2026-05-25

现象：
初版 repo audit 只识别直接 `sys.path.insert(...)`，会漏掉 `sys.path.append/extend`、`import sys as system`、`from sys import path as sys_path` 和 `__path__.append(...)`。

影响：
代码可以绕过审计继续修改 Python 搜索路径，长期会削弱脚本 bootstrap 收敛效果，也容易让兼容入口再次复制本地路径注入。

原因：
首轮实现只针对已发现的 `insert` 残留，AST 规则没有覆盖同类 path mutation 变体。

修复：
`core/maintenance/repo_audit.py` 已扩展 AST 检测，覆盖常见 sys path mutation 和 package `__path__` mutation；`tests/core/test_repo_audit.py` 增加别名、from-import 和 `__path__` 回归测试。

以后规则：
repo audit 类门禁不能只覆盖当前已见症状；同一风险族的常见写法要一起进测试。

相关文件：
- `core/maintenance/repo_audit.py`
- `tests/core/test_repo_audit.py`

### 问题：pipeline 和 capability 路径未收紧会允许读写仓库外路径

日期：2026-05-25

现象：
`blank_shell_pipeline` 和部分 capability runner 会把 payload 中的绝对路径或 `..` 相对路径直接拼接或解析；缺 workflow 文件、坏 JSON 或越界 output_dir 时可能 traceback，甚至尝试写到 repo 外目录。

影响：
无 CAD pipeline 是长期可复用入口，如果路径边界不硬，后续 Agent 或 benchmark payload 可能误读本机文件、把 artifacts 写出仓库，或把环境权限错误误判为业务失败。

原因：
早期 pipeline 假定 workflow 都来自仓库内 examples，先关注链路可跑通，未把路径归属和文件级异常作为安全合约。

修复：
`core/workflows/blank_shell_pipeline.py` 在读取 workflow、解析输入文件和写 output artifacts 前检查 project root / `output/` 边界；缺文件、坏 JSON、越界输入和越界输出都返回结构化 `invalid`。`core/capabilities/runners.py` 的路径型入口也统一限制在 project root 与 `output/` 下。

以后规则：
所有可由 payload 指定的路径都要先解析边界再读写；输入读路径默认必须在 project root 内，输出写路径默认必须在 `output/` 下。

相关文件：
- `core/workflows/blank_shell_pipeline.py`
- `core/capabilities/runners.py`
- `tests/core/test_blank_shell_pipeline_failures.py`
- `tests/core/test_capability_registry_split.py`

### 问题：Windows 非 UTF-8 stdout 下 JSON CLI 可能因中文路径崩溃

日期：2026-05-25

现象：

在未设置 `PYTHONIOENCODING=utf-8` 的 PowerShell 环境中运行 `scripts/run_cad_validation.py --no-cad`，报告生成已完成，但最后向 stdout 打印 `json.dumps(..., ensure_ascii=False)` 时触发 `UnicodeEncodeError: 'gbk' codec can't encode character ...`。

影响：

`report.json` 等 UTF-8 文件证据可能已经落盘，但 CLI 进程以失败状态退出，容易把已完成的无 CAD 验证误判为整体失败；中文工作区路径会放大这个问题。

原因：

脚本入口没有统一配置 stdout/stderr 编码，核心模块直接打印包含中文路径和中文内容的 JSON。Windows 控制台使用 GBK/CP936 时，部分 Unicode 字符无法编码。

修复：

本轮系统层安全重构已执行修复：新增 `scripts/_bootstrap.py` 的 `configure_utf8_stdio()`，让脚本入口统一 `stdout/stderr` 为 UTF-8 with replacement，并在 `tests/core/test_script_bootstrap.py` 增加非 UTF-8 stdout 回归测试。脚本入口同时兼容直接执行和包导入。

以后规则：

所有会向 stdout 打印 JSON 的脚本入口必须先导入共享 bootstrap；报告文件继续使用 UTF-8 写入，stdout 不能因为控制台编码导致命令失败。

相关文件：

- `scripts/run_cad_validation.py`
- `core/verification/cad_validation_runner.py`
- `scripts/_bootstrap.py`
- `tests/core/test_script_bootstrap.py`
- `docs/verification/system_hardening_audit.md`

### 问题：blank-shell workflow 坏输入会抛未分类异常或静默回退

日期：2026-05-25

现象：

缺少 `inputs.shell_model` 时，`blank_shell_pipeline` 会在读取输入时抛 `KeyError`；显式传入 `object_types: []` 时，pipeline 会静默回退到默认对象列表。

影响：

坏 workflow 可能被误当成正常流程继续生成默认布置，或者以未分类异常中断，后续 Agent 难以判断是输入错误、算法失败还是系统回归。

原因：

`run_blank_shell_pipeline()` 在读取 workflow 后缺少前置输入合约校验，只在后续执行路径里隐式依赖字段存在和类型正确。

修复：

新增 `_validate_workflow_inputs()`，对必填输入、可选路径字段和 `object_types` 做结构化校验；缺字段、路径类型错误或显式空对象列表时返回 `status: invalid`、空 artifacts 和明确 errors。新增 `tests/core/test_blank_shell_pipeline_failures.py` 覆盖缺字段、空对象列表和非字符串路径。

以后规则：

workflow 入口必须先分类坏输入，再运行 pipeline；缺失输入、类型错误和确认门阻塞都要返回结构化状态，不得静默回退或抛未分类异常。

相关文件：

- `core/workflows/blank_shell_pipeline.py`
- `tests/core/test_blank_shell_pipeline_failures.py`

### 问题：verification 边界入口对字符串截图路径和兼容调用不稳

日期：2026-05-25

现象：

`build_verification_report(..., screenshot_path="missing-screen.png")` 会把字符串当 Path 调用 `.exists()`；同时部分调用方需要不关心 timeout 参数的 `run_validation()` 兼容入口。

影响：

缺失截图路径本应只保留 `unverified` 并写入 warning，却可能触发类型错误；验证 runner 的兼容调用也不够稳定，容易让报告落盘行为缺少测试保护。

原因：

`screenshot_path` 类型过窄，未在函数入口统一规范化；`cad_validation_runner` 只有底层 `run_cad_validation()`，没有简化的兼容 wrapper。

修复：

`build_verification_report()` 支持 `Path | str | None` 并统一转成 `Path` 后判断存在性；新增 `run_validation()` wrapper，并保证相对 `output_dir` 按 root 解析。新增 `tests/core/test_validation_edges.py` 覆盖 required step 失败仍写 `report.json`、字符串截图缺失不升级 verified、相对输出路径归属。

以后规则：

验证报告入口必须先规范化路径类型；缺截图、无 readback、无 scoped handles 时只能保持 `unverified`，不能升级为真实几何验证。

相关文件：

- `core/verification/cad_validation_runner.py`
- `core/verification/verification_report.py`
- `tests/core/test_validation_edges.py`

### 问题：blank-shell placement bbox 与 CAD_PLAN 对象尺寸不一致

日期：2026-05-25

现象：

大范围审计 Phase V pipeline 时，`layout_proposal` 中的 shelf placement 使用块库命中的 `900 x 350` 尺寸，但最终生成的 CAD_PLAN 使用 `OBJECT_SPEC` 默认 shelf `1200 x 400`。

影响：

非 CAD 布局检查认为对象在 zone 内且不碰撞，但真实 CAD_PLAN 会画出另一套尺寸，可能导致预演和后续 CAD 回读验收不一致。

原因：

`blank_shell_pipeline` 先用 block metadata 做 placement，再重新按对象类型创建默认 `OBJECT_SPEC`，没有把 placement 的实际来源尺寸传给 CAD_PLAN 生成链路。

修复：

- 新增 `test_cad_plan_dimensions_match_layout_placement_bbox` 回归测试。
- `blank_shell_pipeline` 现在从 placement source 派生 `OBJECT_SPEC`：block 命中时使用 block size，fallback 时沿用 fallback object spec。

以后规则：

布局 bbox、`OBJECT_SPEC` 和 CAD_PLAN 对象尺寸必须来自同一来源；block-first placement 后不得再静默退回默认对象尺寸。

相关文件：

- `core/workflows/blank_shell_pipeline.py`
- `tests/core/test_blank_shell_pipeline.py`

### 问题：benchmark 四个 case 实际重复同一 workflow

日期：2026-05-25

现象：

`blank_shell_core_benchmark.json` 初版有 retail、office、residential、restaurant 四个 case id，但四个 case 都指向同一个 `blank_shell_layout_loop.json`。

影响：

benchmark 看似覆盖四个场景，实则只能证明同一输入重复运行成功，无法防止不同 shell / preferences / object_types 的回归。

原因：

Phase V 初版先接通 benchmark runner，尚未补齐四个独立 workflow 和场景偏好输入。

修复：

- 新增 office、residential、restaurant 三个 workflow 和对应 shell examples。
- 新增 `agents/restaurant/preferences.json`。
- 新增 `test_blank_shell_benchmark_cases_use_distinct_workflows`，确保四个 benchmark case 指向不同 workflow。

以后规则：

多 case benchmark 必须检查输入差异；不能只改 case id 或显示名称。

相关文件：

- `examples/benchmarks/blank_shell_core_benchmark.json`
- `examples/workflows/blank_shell_*_layout_loop.json`
- `tests/core/test_benchmarks.py`

### 问题：`path_to_rect_strips()` 遇到重复连续点会生成零面积 strip

日期：2026-05-25

现象：

当入口点和目标点在同一水平线上时，`l_spine` polyline 中可能出现重复连续点，`path_to_rect_strips()` 随后把零长度段转成零面积 rect 并抛出 `strip.min must be lower than strip.max.`。

影响：

合理的直通型 shell 会让 circulation generation 或 blank-shell benchmark 直接异常，而不是产出可解释的候选路径。

原因：

几何底座只处理正长度水平/竖直线段，没有跳过重复连续点。

修复：

- 新增 `test_path_to_rect_strips_skips_duplicate_consecutive_points`。
- `path_to_rect_strips()` 现在跳过零长度 segment；如果整条 polyline 没有任何有效 segment，则返回明确错误。

以后规则：

路径生成器可以产生轻微冗余点；几何底座应稳定处理重复连续点，并只对真正不可解释的路径报错。

相关文件：

- `core/geometry_backends/rect2d.py`
- `tests/core/test_geometry_rect2d.py`

### 问题：zone 剩余空间为负时 placement fallback 抛异常

日期：2026-05-25

现象：

对象顺排到 zone 末尾后，后续对象的 remaining width 可能为负。`create_zone_placements()` 把负数传给 `select_block_candidate()` 的 fallback object spec，最终 `create_object_spec()` 报 `width must be a positive number.`。

影响：

布局失败本应成为结构化 `blocked` placement，却会中断整个 pipeline / benchmark，导致调用方拿不到失败原因和中间 artifacts。

原因：

placement 层没有先检查剩余 zone 空间是否为正，把“空间不够”的业务失败交给了 object spec 尺寸校验。

修复：

- 新增 `test_placement_blocks_cleanly_when_no_remaining_zone_width_exists`。
- `create_zone_placements()` 现在在剩余空间不足时产出 `blocked` placement，并记录 `insufficient remaining zone space for placement.`。

以后规则：

布局容量不足属于可解释失败，应返回结构化 blocked reason；不要让下游尺寸校验承担布局决策职责。

相关文件：

- `core/layout_engine/placement.py`
- `tests/core/test_placement_engine.py`

### 问题：blank-shell pipeline 盲选最高分 zone 可能放不下对象

日期：2026-05-25

现象：

residential blank-shell workflow 中，底侧 zone 因面积/入口距离评分较高被优先选中，但该 zone 深度不足，无法放下 sofa 等对象，导致 `DESIGN_PROPOSAL needs confirmation before CAD_PLAN generation.`。

影响：

zone 分数通过不代表 placement 可行；pipeline 如果只取 `zones[0]`，会把可放置的候选 zone 跳过，使本可成功的 workflow 被阻断。

原因：

Phase V 初版 zone 选择策略只看 zone score，没有把对象放置可行性纳入选择。

修复：

- 新增 `test_residential_workflow_selects_zone_that_can_fit_objects`。
- `blank_shell_pipeline` 现在会对候选 zones 做 placement 试算，优先选择 failed placement 最少、placed count 更高的 zone。

以后规则：

端到端 pipeline 选择中间候选时，不能只看上游单项分数；下游可行性必须进入选择依据，至少要避免明显可放置候选被跳过。

相关文件：

- `core/workflows/blank_shell_pipeline.py`
- `tests/core/test_blank_shell_pipeline.py`

### 问题：no-place-zone 未相交时误报 `partial`

日期：2026-05-25

现象：

执行 Phase S 时，`zone_splitter` 调用 `rect2d.subtract_no_place_zones()` 后，发现下侧功能区并没有与任何 no-place-zone 相交，却仍被标记 uncertainty，分数也被降低。

影响：

无关避让区会污染功能区评分与解释，后续 placement / proposal 可能错误地认为可布置区域被扣减。

原因：

`subtract_no_place_zones()` 只根据“传入了 zones”判断返回 `partial`，没有记录实际 fragments 是否发生变化。

修复：

- 在 `core/geometry_backends/rect2d.py` 中增加 `changed` 标记，只有实际拆分或扣减时才返回 `partial`。
- 新增 `test_subtract_no_place_zones_ignores_non_intersecting_zones` 回归测试。

以后规则：

几何扣减函数的状态必须反映实际几何变化；传入约束但未发生相交时应保持 `pass`，不能制造虚假 uncertainty。

相关文件：

- `core/geometry_backends/rect2d.py`
- `tests/core/test_geometry_rect2d.py`
- `core/layout_engine/zone_splitter.py`

### 问题：空壳样例升级为 `SHELL_MODEL` 后旧 drawing schema 测试失配

日期：2026-05-25

现象：

执行 Phase P 后，`projects/sample_blank_shell/input/shell.manual.json` 已从旧 drawing-style 手工输入升级为 `SHELL_MODEL`。全量 `unittest discover -s tests` 中，`tests/core/test_drawing_analysis.py::test_sample_blank_shell_manual_input_validates` 仍按 `drawing_model.schema.json` 校验该文件，导致缺少 `drawing_id`、`layers`、`entities_summary` 等字段，并把 `shell_id`、`boundary`、`fixed_obstacles` 等新字段判为非法。

影响：

Phase P 的模型口径已经切到 `SHELL_MODEL`，但旧测试会把正确的新样例误判为错误，阻断全量回归。

原因：

样例文件职责变化后，旧 drawing analysis 测试没有同步到 shell schema 与 `load_manual_shell()` 入口。

修复：

- 更新 `tests/core/test_drawing_analysis.py`，让 sample blank shell 按 `shell_model.schema.json` 校验，并通过 `load_manual_shell()` 规范化后断言 `no_place_zones`。
- 保留 `build_manual_drawing_model()` 的原有测试，确保旧 `DRAWING_MODEL` 构建路径仍可用。

以后规则：

当样例文件从一种模型升级为另一种模型时，同步更新引用它的 schema 测试；不要让旧 schema 测试继续绑定已经换职责的文件。

相关文件：

- `projects/sample_blank_shell/input/shell.manual.json`
- `core/drawing_analysis/shell_loader.py`
- `tests/core/test_drawing_analysis.py`

### 问题：CAD 层面验证容易停在第一个失败点

日期：2026-05-25

现象：

用户准备在另一台电脑上 clone 仓库做真实 CAD 验证时，担心 Codex 只执行到第一处失败就停下来询问，导致一次对话只解决一个小点，整体换机验收和 CAD 补验效率很低。

影响：

真实 CAD 验证链路包含依赖、AutoCAD COM、预览落图、截图、实体回读和验证报告。任一环失败都可能中断；如果没有总控脚本和强约束手册，Codex 容易依赖聊天框里的临时文字要求，复用性不足。

原因：

已有 `CAD_AGENT_BLOCKER_PLAYBOOK.md` 偏向卡壳后的人工方法论，缺少一个能一次跑完整链路、结构化分类失败、输出报告并要求 Codex 自主修复仓库内问题的入口。

修复：

- 新增 `CAD_AGENT_AUTONOMOUS_VALIDATION.md`，固化自主验证规则和复制给 Codex 的启动语。
- 新增 `core/verification/cad_validation_runner.py` 与 `scripts/run_cad_validation.py`，按步骤执行验证并生成 `report.json` / `report.md`。
- 新增失败分类和下一步动作，让 Codex 区分仓库内可修问题与用户侧外部阻塞。
- 新增 `tests/core/test_cad_validation_runner.py` 覆盖关键分类行为。
- 在 `CAD_AGENT_RULES.md` 增加自主验证闭环规则。

以后规则：

真实 CAD 验证、换机验收或 CAD 补验时，优先运行 `scripts/run_cad_validation.py`，并以 `output/validation_runs/<timestamp>/report.json` 为证据。Codex 不得遇到第一处失败就停止；仓库内问题必须自行修复并复验，只有外部环境、权限或用户项目语义缺失才交回用户。

相关文件：

- `CAD_AGENT_AUTONOMOUS_VALIDATION.md`
- `core/verification/cad_validation_runner.py`
- `scripts/run_cad_validation.py`
- `tests/core/test_cad_validation_runner.py`
- `CAD_AGENT_RULES.md`

### 问题：Windows 子进程 stderr 可能不是 UTF-8，CLI 缺失测试会被解码错误遮住

日期：2026-05-25

现象：
新增 `tests/core/test_benchmark_cli.py` 时，脚本尚未存在，本应得到“文件不存在”的红灯；但 `subprocess.run(..., encoding="utf-8")` 读取 Windows Python stderr 时先触发 `UnicodeDecodeError`。

影响：
CLI wrapper 测试可能把真实失败原因遮住，尤其是路径中包含中文时更明显。

原因：
Windows 子进程错误输出可能使用本地代码页，而不是 UTF-8。

修复：
在 CLI 测试里使用 `errors="replace"`，让测试能稳定读取 stderr，并继续断言 return code 与 JSON 输出。

以后规则：
新增直接运行 `scripts/*.py` 的 subprocess 测试时，若使用 `text=True` 和 `encoding="utf-8"`，同时加 `errors="replace"`，避免编码问题遮住真实失败。

相关文件：
- `tests/core/test_benchmark_cli.py`
- `scripts/run_benchmark_suite.py`

### 问题：Agent preference 测试向 `sys.path` 注入项目根会重新触发 discover 遮蔽

日期：2026-05-25

现象：

新增 `tests/agents/test_scene_preferences.py` 后，`python -m unittest discover -s tests` 再次出现 `ModuleNotFoundError: No module named 'core.test_*'`。

影响：

单个测试文件可通过，但全量 discover 会失败，容易被误判为 Core 模块缺失。

原因：

Agent 测试为了导入 Core 函数把项目根插入 `sys.path`，导致真实 `core/` 包遮住 `tests/core` 测试包。这与此前 `test_scene_agent_boundaries.py` 的路径污染问题相同。

修复：

移除 Agent preference 测试中的 `sys.path.insert()`。在 `unittest discover -s tests` 模式下，直接导入 `core.*` 会先走 `tests/core/__init__.py` 的兼容路径扩展。

以后规则：

`tests/agents` 中需要读文件或导入 Core 时，不要手动把项目根插到 `sys.path`；新增 Agent 测试后必须跑完整 `unittest discover -s tests`。

相关文件：

- `tests/agents/test_scene_preferences.py`
- `tests/core/__init__.py`

### 问题：workflow schema 校验曾静默跳过未知 model_type

日期：2026-05-25

现象：

`validate_workflow_schemas()` 遇到未注册的 `model_type` 时会继续执行，而不是报错。

影响：

workflow 中模型类型拼错或新增模型未注册时，schema 校验可能给出“看似通过”的结果。

原因：

早期实现把未知 schema 当作临时兼容情况处理，适合探索，但不适合作为模型合约门。

修复：

未知 `model_type` 现在会返回明确错误，并由 `tests/core/test_model_loop.py` 覆盖。

以后规则：

新增高层模型必须先进入 `core/schemas/registry.py`，workflow 校验不得静默跳过未知模型。

相关文件：

- `core/model_loop/reference_checker.py`
- `core/schemas/registry.py`
- `tests/core/test_model_loop.py`

### 问题：`run_non_cad_pipeline.py` 直接运行时找不到 `core`

日期：2026-05-25

现象：

直接执行 `scripts/run_non_cad_pipeline.py` 时曾报 `ModuleNotFoundError: No module named 'core'`。

影响：

pipeline 单测可通过，但用户按脚本入口运行会失败，破坏非 CAD 闭环验收。

原因：

脚本包装器没有把项目根目录加入导入路径。

修复：

在 `scripts/run_non_cad_pipeline.py` 中加入项目根目录路径处理。

以后规则：

新增 `scripts/*.py` 兼容入口后，必须同时用“模块测试”和“脚本直接运行”两种方式验证。

相关文件：

- `scripts/run_non_cad_pipeline.py`
- `tests/core/test_non_cad_pipeline.py`

### 问题：当前 CAD 可能因环境或代理问题无法稳定打开

日期：2026-05-25

现象：

当前 AutoCAD 可能无法稳定打开，导致真实 `CODEX_PREVIEW` 落图、COM 实体回读和截图证据无法完整执行。

影响：

Core 的非 CAD 层开发不应被真实 CAD 环境卡住，但也不能因此声称已完成几何准确性验证。

原因：

真实 CAD 验证依赖本机 AutoCAD、活动 DWG、CAD-MCP/COM 链路和当前窗口状态；这些属于运行环境条件，不等同于 Core 逻辑是否正确。

修复：

- 将非 CAD 可验证内容作为当前交付门：单测、schema 校验、`CAD_PLAN` validate、dry-run、自检、截图能力检查、fake readback 验证报告。
- 将真实 CAD 相关命令写入 `CORE_RESTRUCTURE_PLAN.md` 的延后验证清单。

以后规则：

CAD 不可用时，继续推进不依赖 CAD 的 Core 能力并完整验证；凡需要真实 CAD 证明的内容，必须在计划中列出补验命令和通过标准，不得在未补验前声称图纸已几何准确。

相关文件：

- `CORE_RESTRUCTURE_PLAN.md`
- `core/verification/verification_report.py`
- `scripts/inspect_dwg.py`

### 问题：验证报告早期原型可能误报几何已验证

日期：2026-05-25

现象：

`VERIFICATION_REPORT` 初版只检查目标图层、bbox 尺寸、文字和标注数量，未检查基点，且在有截图或执行摘要时可能让失败检查被较低等级状态覆盖。后续审计又发现，如果外部调用方只传 `entities_are_scoped=True`，也可能把“调用方声明已隔离”误当成真实证据。

影响：

如果柜子尺寸正确但画错位置，或文字/标注在别的图层，报告可能错误接近“通过”。如果没有 created handles 或 before/after diff，却信任裸 scope 布尔值，也可能把旧实体误认为本次输出。这会违反“不能把画不准当完成”的门槛。

原因：

第一版验证报告过于关注“有无证据”和“尺寸”，没有把失败优先级、基点、图层过滤和本次执行实体隔离放进核心判断。

修复：

- `failed` 状态优先于 `screenshot_captured` 和 `executed_only`。
- 增加 `base_point` 检查。
- 文字和标注检查只统计目标图层。
- 增加 `readback_scope` 检查；未隔离本次执行实体时不能声称 `geometry_verified`。
- 裸 `entities_are_scoped=True` 不再足以升级为 `geometry_verified`；需要 `created_handles` 覆盖回读实体。
- 截图路径必须真实存在，才能算 `screenshot_captured`。
- 增加 before/after snapshot diff 数据结构、批量汇总和失败修复建议字段。
- 补充失败优先级、基点错误、错误图层、未隔离实体、created handles、截图路径、snapshot diff、批量汇总等测试。

以后规则：

实体回读验证必须同时覆盖图层、尺寸、基点、文字/标注图层和证据范围；没有本次执行实体隔离时，最多只能视作未完全验证。后续真实 CAD 闭环必须优先验证 handles / before-after diff 是否可靠。

相关文件：

- `core/verification/verification_report.py`
- `tests/core/test_verification_report.py`

### 问题：当前沙箱允许写入但不允许删除系统临时目录文件

日期：2026-05-25

现象：

运行 `python -m unittest discover -s tests` 时，使用 `tempfile.TemporaryDirectory()` 的测试会在 `C:\Users\123235\AppData\Local\Temp` 下写入/清理临时文件，并触发 `PermissionError: [WinError 5] 拒绝访问`。

影响：

测试结果会被误判为业务失败；即使设置 `TEMP` / `TMP` 到工作区，当前 Python 运行时仍可能选择系统临时目录，且文件清理动作会失败。

原因：

当前执行环境对删除/移动既有文件和系统临时目录清理有限制。它允许部分写入，但不保证 `TemporaryDirectory` 的自动清理能成功。

修复：

- 新增 `tests/helpers.py`，把测试产物写到 `output/test_artifacts`。
- 修改 `tests/core/test_execute_plan.py` 和 `tests/core/test_render_preview.py`，避免依赖 `TemporaryDirectory()` 清理。

以后规则：

在本仓库测试中优先使用工作区内的稳定测试产物目录；不要把系统临时目录清理失败当成 CAD Core 功能失败。

相关文件：

- `tests/helpers.py`
- `tests/core/test_execute_plan.py`
- `tests/core/test_render_preview.py`

### 问题：Agent 测试向 `sys.path` 注入项目根会破坏 `unittest discover -s tests`

日期：2026-05-25

现象：

新增 `tests/agents/test_scene_agent_boundaries.py` 后，`unittest discover -s tests` 报 `ModuleNotFoundError: No module named 'core.test_*'`。

影响：

`tests/core` 在该发现模式下会被导入为 `core` 测试包；如果其他测试提前把项目根插到 `sys.path` 最前，真实 `core/` 包会遮住测试包。

原因：

测试导入路径与真实包名同名，且 Agent 测试本来只需要读文件，却不必要地修改了 `sys.path`。

修复：

移除 Agent 边界测试中的 `sys.path.insert(0, str(PROJECT_ROOT))`，保持纯路径读取。

以后规则：

不需要导入项目模块的测试不要修改 `sys.path`；涉及 `tests/core` 包名兼容时，继续用 `tests/core/__init__.py` 的兼容处理。

相关文件：

- `tests/agents/test_scene_agent_boundaries.py`
- `tests/core/__init__.py`

### 问题：`inspect_dwg.py` 空跑时不应默认连接真实 CAD

日期：2026-05-25

现象：

增强实体回读后，旧兼容测试执行 `scripts/inspect_dwg.py` 空命令时尝试连接 AutoCAD COM，导致无 CAD 或沙箱环境下运行变慢或不稳定。

影响：

普通自检命令不应因为没有打开 CAD 而卡住；真实 CAD 回读也不应在用户无意触发时执行。

原因：

最初把“检查 DWG”默认理解为连接活动 CAD，但仓库规则要求无 CAD 自检与真实 CAD 操作分离。

修复：

`core/verification/inspect_dwg.py` 默认不连接 CAD；需要真实回读时显式传 `--connect-cad`。`--no-cad` 可输出无 CAD 的 `VERIFICATION_REPORT` 壳。回读路径使用 `AutoCADComDriver(connect_existing_only=True)`，不会自动启动 AutoCAD。

以后规则：

凡涉及真实 CAD 窗口、COM 或当前 DWG 的操作，默认保持低风险，必须用显式参数触发。

相关文件：

- `core/verification/inspect_dwg.py`
- `core/cad_io/autocad_com.py`
- `scripts/inspect_dwg.py`

### 问题：面向用户输出混入英文模板

日期：2026-05-25

现象：

在方案讨论过程中，Codex 的中间说明和最终答复混入了英文句子，例如外部 brainstorming Skill 的视觉辅助提示原文。

影响：

用户希望工作流以中文沟通为主。英文模板原样输出会打断阅读，也容易让用户误以为仓库规则要求英文回复。

原因：

根目录 `AGENTS.md` 和 `skills/cad-drawing/SKILL.md` 是英文规则，且仓库缺少“面向用户默认中文输出”的明确约束。外部 Skill 或插件模板为英文时，Codex 容易直接转发模板句子。

修复：

- 将根目录 `AGENTS.md` 改为中文规则，并新增“默认中文输出”。
- 将 `skills/cad-drawing/SKILL.md` 改为中文说明，并新增默认中文要求。
- 在 `CAD_AGENT_RULES.md` 增加“默认中文沟通”规则。
- 更新 `CAD_AGENT_STATUS.md` 和 `CAD_AGENT_CHANGELOG.md`。

以后规则：

除代码、命令、路径、Schema 字段、JSON key、工具名和 API 名称外，面向用户的说明、状态汇报、方案讨论、追问和结论默认使用中文。引用英文 Skill 或工具模板时，应理解后用中文转述，不要原样输出。

相关文件：

- `AGENTS.md`
- `skills/cad-drawing/SKILL.md`
- `CAD_AGENT_RULES.md`
- `CAD_AGENT_STATUS.md`
- `CAD_AGENT_CHANGELOG.md`

### 问题：`unittest discover -s tests` 会把 `tests/core` 当成 `core` 包

日期：2026-05-25

现象：

第一轮仓库重装后运行：

```powershell
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' -m unittest discover -s tests
```

出现 `ModuleNotFoundError: No module named 'core.execution'`、`No module named 'core.verification'` 等错误。

影响：

真实 `core/` 包已经存在，但测试发现从 `tests/` 作为起点时，会把 `tests/core` 导入成名为 `core` 的测试包，遮住项目根目录下的真实 `core/`。

原因：

`tests/core/__init__.py` 让测试目录成为 `core` 包，而测试命令的 top-level 默认是 `tests`。

修复：

在 `tests/core/__init__.py` 中扩展包搜索路径，把项目根目录下的真实 `core/` 加入 `__path__`，从而保留 `tests/core` 目录结构和旧 `unittest discover -s tests` 命令兼容。

以后规则：

如果继续使用 `tests/core` 目录名，要保留该兼容处理，或改用显式 top-level 的测试命令。迁移测试结构时必须跑完整 `unittest discover -s tests`。

### 问题：Core 迁移后 `self_check.py` 容易误判项目根目录

日期：2026-05-25

现象：

`self_check.py` 从 `scripts/` 迁到 `core/verification/` 后，如果继续使用 `Path(__file__).resolve().parents[1]` 推断项目根，会把 `core/` 当成根目录。

影响：

自检会错误判断必需文件缺失，或者把输出路径、示例计划路径解析到错误位置。

原因：

文件所在目录层级从 `scripts/self_check.py` 变为 `core/verification/self_check.py`，父级数量变化。

修复：

Core 实现中改为 `Path(__file__).resolve().parents[2]`，旧 `scripts/self_check.py` 只保留薄包装器。

以后规则：

迁移 CLI 脚本到 Core 后，必须重新检查所有基于 `__file__` 的根目录推断。

### 问题：卡壳时缺少统一自查和截图证据入口

日期：2026-05-25

现象：

目录里已有 `output/previews/` 和 `scripts/render_preview.py`，但 `render_preview.py` 只是脚手架；`inspect_dwg.py` 也只是回读验证脚手架。遇到“画不准、画不出来”时，缺少统一方法告诉 Codex 先查什么、如何留证据、何时修工具。

影响：

后续阶段 4 预览绘制和阶段 5 回读验证容易反复盲试；视觉问题也可能因为没有截图而无法复盘。

原因：

早期重点是搭建 CAD_PLAN、validate 和 dry-run 最小闭环，截图、自检、卡壳恢复还没有实现。

修复：

- 新增 `CAD_AGENT_BLOCKER_PLAYBOOK.md`。
- 新增 `scripts/self_check.py`。
- 扩展 `scripts/render_preview.py --check` 和 `--capture-screen`。
- 新增相关单测。

以后规则：

遇到卡壳先运行自检，视觉问题先确认截图能力；如果截图或自检能力不存在，先补工具入口，再继续绘图修复。

相关文件：

- `CAD_AGENT_BLOCKER_PLAYBOOK.md`
- `CAD_AGENT_RULES.md`
- `scripts/self_check.py`
- `scripts/render_preview.py`
- `tests/test_render_preview.py`
- `tests/test_self_check.py`

### 问题：早期测试目录未包化导致模块名运行失败

日期：2026-05-25

现象：

使用下面命令运行新增测试时失败：

```powershell
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' -m unittest tests.test_execute_plan
```

影响：

测试文件本身可用，但当时 `tests/` 目录还不是 Python package，模块名方式发现测试会失败。

原因：

当时还没有创建 `tests/__init__.py`，项目测试规模也很小。

修复：

早期临时修复是直接按文件路径运行：

```powershell
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' 'CAD测试相关文件\tests\test_execute_plan.py'
```

后续仓库重装时已创建 `tests/__init__.py`、`tests/core/__init__.py`。以下仍是历史路径示例，不是当前仓库根目录下的推荐命令：

```powershell
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' -m unittest discover -s 'CAD测试相关文件\tests'
```

以后规则：

当前优先使用 `unittest discover -s tests`。如果使用 `tests/core` 目录名，必须保留 `tests/core/__init__.py` 中对真实 `core/` 包路径的兼容处理。

### 问题：中文 Markdown 在 PowerShell 默认输出中可能显示乱码

日期：2026-05-24

现象：

使用 `Get-Content` 默认读取中文 Markdown 时，终端可能显示乱码。

影响：

文件内容本身通常没坏，但终端显示会误导判断。

原因：

PowerShell 默认编码和文件 UTF-8 编码显示不一致。

修复：

读取中文 Markdown 时使用：

```powershell
Get-Content -Encoding UTF8 -LiteralPath '文件路径.md'
```

以后规则：

检查中文文档时优先显式指定 `-Encoding UTF8`。

### 问题：CAD Agent 文件散落在根目录会影响阅读

日期：2026-05-24

现象：

CAD 相关说明文件和 DWG、PDF、视频、临时目录混在一起。

影响：

用户难以判断哪些文件属于 CAD Agent 开发资料。

原因：

早期验证阶段先在根目录生成文件，尚未整理项目结构。

修复：

早期修复是创建 `CAD测试相关文件` 子文件夹，并将 CAD Agent 相关说明归档到内部结构。当前 Core Lab 已进一步重装为仓库根目录结构。

以后规则：

当前现行规则：CAD Agent 说明和入口文档在仓库根目录，通用能力进入 `core/`，场景差异进入 `agents/`，共享资源进入 `libraries/`，真实项目资料进入 `projects/`。`CAD测试相关文件` 是历史路径口径，不再作为当前开发入口。

### 问题：PowerShell 中全局 python 命令不可用

日期：2026-05-24

现象：

运行下面命令失败：

```powershell
python 'CAD测试相关文件\scripts\validate_plan.py' 'CAD测试相关文件\examples\plans\draw_test_cabinet.json'
```

影响：

脚本本身没坏，但不能依赖全局 `python` 命令运行测试。

原因：

当前系统 PATH 中没有可用的 `python` 命令。

修复：

使用 CAD-MCP 虚拟环境 Python：

```powershell
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' 'CAD测试相关文件\scripts\validate_plan.py' 'CAD测试相关文件\examples\plans\draw_test_cabinet.json'
```

以后规则：

运行 CAD Agent Python 脚本时，优先使用 CAD-MCP 虚拟环境 Python，除非以后单独建立项目级 `.venv`。

### 问题：Python 输出中文在 PowerShell 中可能显示乱码

日期：2026-05-24

现象：

`dry_run_plan.py` 可以读取中文对象名，但终端输出可能显示成乱码。

影响：

脚本结果容易被误判。

原因：

Windows PowerShell 控制台输出编码和 Python 输出编码不一致。

修复：

运行脚本前设置：

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

以后规则：

涉及中文 JSON 或中文 Markdown 的脚本验证，都显式设置 UTF-8 输出。
