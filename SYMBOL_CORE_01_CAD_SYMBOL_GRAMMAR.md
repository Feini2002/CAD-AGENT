# SYMBOL-CORE-01-CAD-SYMBOL-GRAMMAR 开发包任务

最后更新：2026-05-26

## 背景

当前 Core 已能把对象和组合写入 `CODEX_PREVIEW`，并通过 created handles 回读证明几何真实存在。但用户可见结果仍像一组抽象矩形：机器知道它们代表桌面、支撑、座面、靠背，人看到的却不是“家具图库”或“CAD 平面符号”。

本开发包的目标不是继续为 10 个 demand case 补特例，也不是先做几个破局样本；目标是在 Core 底座上建立通用 CAD 符号语法层，让系统从“画几何”升级为“会说 CAD 图纸语言”。

## 总目标

建立从 `OBJECT_SPEC` 到 `SYMBOL_SPEC`，再到可落图 `CAD_PLAN` / CAD primitives 的通用链路：

```text
OBJECT_SPEC
-> SYMBOL_SPEC
-> SYMBOL_GRAPH / SYMBOL_PLAN
-> CAD_PLAN / CAD primitives
-> validate + dry-run
-> CODEX_PREVIEW + created handles readback
-> symbol_readability_report
```

最终能力应支持生成可读家具图库符号，而不依赖文字标注或尺寸标注来解释“这是什么”。

## 非目标

- 不把需求侧角色 Agent 作为最终系统能力保留。
- 不把 10 个 demand case 当成边界。
- 不先堆餐桌、床、沙发等孤立特例模板。
- 不承诺完整公司块库、属性块、hatch 或施工图级符号。
- 不用文字 / 尺寸标注替代符号可读性。

## 核心设计

### 1. `SYMBOL_SPEC`

新增 Core 级符号模型，用于表达 CAD 平面符号，而不是直接表达家具组件矩形。

建议字段：

```text
version
symbol_id
object_type
archetype
view
footprint
orientation
parts
readability_constraints
fallback_policy
evidence
```

`parts` 表达符号部件，例如：

- `outline`
- `inner_offset`
- `thick_band`
- `split_line`
- `leg_marker`
- `arc_marker`
- `seat_split`
- `drawer_line`
- `door_swing`
- `clearance_ghost`
- `orientation_marker`

### 2. 符号 primitive 层

新增 `core/symbol_engine/`，先实现通用 primitive，而不是家具特例。

建议模块：

```text
core/symbol_engine/
  __init__.py
  symbol_spec.py
  primitives.py
  archetypes.py
  object_to_symbol.py
  symbol_to_plan.py
  readability.py
```

primitive 必须能转为现有安全 `CAD_PLAN` 或可执行 CAD primitives，并保持：

- 默认 `CODEX_PREVIEW`
- 默认不加文字
- 默认不加尺寸
- 支持 validate / dry-run
- 后续可真实 CAD readback

### 3. Archetype grammar

家具对象先归入通用 archetype，再由 archetype 组合 primitive。

首批 archetype：

| Archetype | 覆盖对象 | 必备可读部件示例 |
| --- | --- | --- |
| `surface` | 餐桌、办公桌、会议桌 | 外轮廓、边缘内缩线、腿/支撑标记、方向或座位关系 |
| `seating` | 椅子、沙发、卡座 | 座面、靠背、扶手或坐垫分缝、朝向 |
| `sleeping` | 床 | 外框、床垫内缩、枕头/床头方向 |
| `storage` | 柜子、文件柜、衣柜 | 外框、门缝、抽屉线、开启方向或柜前净空 |
| `display` | 展台、展示架、货架 | 展示面、层板/分格、观看方向 |
| `workstation` | 办公桌椅屏幕组合 | 桌面、座位、屏幕/键盘区、朝向关系 |

### 4. Fallback policy

不允许系统静默退化成抽象矩形。每次退化都必须可机器读：

```text
block_preferred
symbol_readable
fallback_component_preview
fallback_bbox_placeholder
deferred_unsupported_symbol
```

优先级建议：

```text
受控真实 block
-> symbol glyph
-> component preview
-> bbox placeholder
-> deferred
```

### 5. Readability gate

新增 `symbol_readability_report`。它不替代 `geometry_verified`，而是补充“人能不能看懂”。

机器检查项：

- 不是单一 bbox。
- 必备 symbol parts 存在。
- 关键部件相对位置符合 archetype。
- 最小可读尺寸满足阈值。
- 朝向可推断。
- fallback 状态明确。
- 不依赖文字 / 尺寸标注作为主要识别手段。

建议状态：

```text
symbol_readable
visual_review_required
fallback_component_preview
fallback_bbox_placeholder
deferred_unsupported_symbol
```

### 6. CAD 验证门槛

本包不只停在 non-CAD。至少要让代表 glyph 进入真实 CAD smoke：

- validate pass
- dry-run pass
- 写入 `CODEX_PREVIEW`
- created handles readback
- `geometry_verified`
- 输出 `symbol_readability_report`
- 截图只作为视觉辅助

## 建议开发顺序

### Step 1. Schema 和数据模型

- 新增 `core/schemas/symbol_spec.schema.json`
- 新增 invalid fixture
- 加入 `core/schemas/registry.py`
- 单测覆盖合法 / 非法 `SYMBOL_SPEC`

### Step 2. Symbol primitive

- 新增 `core/symbol_engine/primitives.py`
- 实现 outline、inner_offset、thick_band、split_line、leg_marker
- 输出安全 CAD_PLAN 或 CAD primitive plan items
- 单测验证所有 plan 可 validate / dry-run

### Step 3. Archetype grammar

- 新增 `core/symbol_engine/archetypes.py`
- 实现 `surface`、`seating`、`sleeping`、`storage` 的必备部件规则
- 不写成具体家具模板；对象通过 archetype 复用规则

### Step 4. Object to symbol

- 新增 `core/symbol_engine/object_to_symbol.py`
- 将现有 `OBJECT_SPEC` 映射到 `SYMBOL_SPEC`
- table / desk -> `surface`
- chair / sofa -> `seating`
- bed -> `sleeping`
- cabinet / file_cabinet / storage_cabinet -> `storage`
- display_unit / shelf -> `display`

### Step 5. Symbol to CAD plan

- 新增 `core/symbol_engine/symbol_to_plan.py`
- 将 `SYMBOL_SPEC.parts` 渲染成 CAD_PLAN item 列表
- 默认 `CODEX_PREVIEW`、不加文字、不加尺寸
- 输出 artifact 目录和 dry-run 汇总

### Step 6. Readability report

- 新增 `core/symbol_engine/readability.py`
- 输出 `symbol_readability_report`
- benchmark 断言 `symbol_readable`，并拒绝静默 bbox fallback

### Step 7. Benchmark

- 新增 `examples/benchmarks/symbol_core_benchmark.json`
- 覆盖至少 6 个 archetype / object mapping case
- 证明不是只生成矩形 bbox

### Step 8. 真实 CAD smoke

- 新增或扩展 runner，把代表 symbol glyph 写入 `CODEX_PREVIEW`
- 保存 created handles readback report
- 生成视觉辅助截图
- 真实 CAD 结论只覆盖本包代表 case，不扩大为任意块库 / 任意家具图库

### Step 9. 状态和交接

完成后同步：

- `CORE_RESTRUCTURE_PLAN.md`
- `CORE_STATUS.md`
- `CAD_AGENT_STATUS.md`
- `CAD_AGENT_CHANGELOG.md`
- `CAD_AGENT_ISSUES.md`（如有失败教训）
- `docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md`

## 验收标准

本包完成时，至少满足：

- `SYMBOL_SPEC` 有 schema、registry、invalid fixture。
- `core/symbol_engine/` 有清晰边界，不混入 CAD COM 执行。
- 至少 4 类 archetype 可生成符号。
- 至少 6 个 object mapping case 可跑 non-CAD benchmark。
- 所有 symbol plan validate + dry-run pass。
- `symbol_readability_report` 能识别 `symbol_readable` 和 fallback 状态。
- 至少一组代表 glyph 真实 CAD `geometry_verified`。
- 截图只作为视觉辅助，不替代 created handles readback。

## 风险边界

- 这不是正式公司块库。
- 这不是施工图符号全集。
- 这不是把所有家具都一次性产品化。
- `symbol_readable` 只能证明符号结构满足规则；视觉审美仍需人工评审或后续视觉规则。
- 真实 CAD 验证只覆盖本包代表 case，不扩大到任意 DWG 或任意 `SYMBOL_SPEC`。

## 推荐执行命令

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"

& $py -m unittest tests.core.test_symbol_engine
& $py -m unittest tests.core.test_schema_validation
& $py scripts\run_benchmark_suite.py examples\benchmarks\symbol_core_benchmark.json --output-root output\test_artifacts\benchmarks\symbol_core
& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
```

真实 CAD 阶段再补：

```powershell
& $py scripts\<symbol-cad-smoke-runner>.py --output-dir output\validation_runs\symbol-core-cad-smoke
```

具体 runner 名称由实施时确定，但必须写入 `output/validation_runs/` 并输出 created handles readback report。
