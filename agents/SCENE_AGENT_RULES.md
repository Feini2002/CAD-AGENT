# Scene Agent Rules

场景 Agent 是轻量偏好层，不是第二套 Core。当前仓库里已有的 `office`、`residential`、`restaurant` 等目录主要证明“多场景可以复用同一 Core pipeline”，不等于具体业务场景已经产品化完成。

`agents/demand_side/` 是一个数据型需求压力测试层，用来模拟不同用户角色提出需求。它不是 Scene Product，也不允许放 CAD 执行、几何、验证或业务算法实现；只能保存角色、用户原话、需求焦点和 Core 能力映射。

成熟度按四级表达：

| 层级 | 含义 |
| --- | --- |
| `Scene Alpha 壳层` | preferences、词汇、默认参数、排序权重、解释模板和边界扫描 |
| `Scene Beta 能力包` | 对象体系、微场景、failure benchmark 和 non-CAD 证据 |
| `Scene Product 场景产品` | 真实项目样本、图块策略、真实 CAD smoke、用户确认流和交付边界 |
| `Core 底座` | 所有通用算法、CAD 执行、验证和安全能力，归 `core/` |

只有进入某个场景的对象体系、业务规则、图块 metadata、项目样本、失败样本、真实 CAD readback 和用户确认闭环，才算具体场景开发。

## 调用方式：按需激活，不自动套场景

场景能力必须由 Core 中控按需调用，而不是在通用请求中自动介入。

建议架构：

```text
Core Orchestrator
-> Scene Router
-> Scene Registry
-> agents/<scenario>/ Scene Capability Module
-> Core workflow / CAD_PLAN / verification
```

默认规则：

- 用户没有明确提到场景、项目 manifest 没有指定场景时，返回 `no_scene`，只走通用 Core。
- 用户明确说“工装、办公室、住宅、餐饮、展陈”等，才允许加载对应 `agents/<scenario>`。
- 场景判断不确定时，先追问用户，不静默套用某个场景。
- 场景模块输出的是业务语义、偏好、对象清单、图块选择建议和解释，不直接写 CAD。

## 可以放在 Agent 中

- 场景词汇。
- 默认参数。
- 业务偏好。
- workflow 名称和步骤说明。
- 评分权重。
- 对 `libraries/` 资源的优先级。
- 场景对象清单的引用和优先级。
- 场景解释模板，说明偏好如何影响 Core 候选。
- 场景模块 registry、触发词、启用条件和禁用条件。
- 业务语义到 Core 输入的轻量 adapter 设计文档。

## 不可以放在 Agent 中

- 通用对象生成算法。
- 通用碰撞检测。
- 通用通道宽度算法。
- 通用图纸读取。
- 通用 `CAD_PLAN` 校验、dry-run、执行、截图、实体回读。
- 真实项目资料。
- 公司专属块库本体。
- 把 non-CAD benchmark pass 写成真实 CAD 几何准确。
- 把 Alpha / Beta 壳层写成可交付的 Scene Product。

这些能力应放在 `core/`、`libraries/` 或 `projects/` 的对应边界内。

## 边界扫描（X-SCENE-03）

`agents/` 目录下不得出现 Python 实现文件（`*.py`）；场景差异只通过 `preferences.json`、`rules.md`、`agent.json` 与 workflow 说明表达。

这是当前 Alpha 边界，用来防止场景层过早复制 Core。未来进入 Scene Product Alpha 时，可以在主计划中先建立 `Scene Capability Module` 接口，再有条件允许 `agents/<scenario>/capabilities/` 放置轻量 adapter 函数；但在接口、边界扫描和测试更新前，仍按“无 `.py`”执行。

机器扫描由 `core/agents/scene_boundary_scan.py` 执行，`tests/agents/test_scene_agent_boundaries.py` 在 CI / 本地 unittest 中强制校验。禁止项包括但不限于：

| 类别 | 示例（出现在 `agents/` 即失败） |
| --- | --- |
| CAD 执行 / COM | `execute_plan_file`、`AutoCADComDriver`、`AddLine(`、`win32com` |
| 回读 / 验证脚本 | `snapshot_modelspace`、`inspect_dwg`、`run_cad_validation` |
| Pipeline 实现 | `run_blank_shell_pipeline`、`build_blank_shell_candidate_sets` |
| 布局 / 几何算法 | `generate_circulation_candidates`、`split_zones(`、`rect_intersects` |
| 直接导入 Core 实现 | `from core.workflows`、`from core.layout_engine`、`from core.cad_io` |

workflow 文档可以用 `-> core.<module>` 描述**调用关系**，但不得在 `agents/` 内复制上述实现。

## 执行要求

Agent workflow 必须先输出高层模型或结构化意图，再进入 `CAD_PLAN`。真实落图前仍然需要 validate、dry-run、`CODEX_PREVIEW` 和 `VERIFICATION_REPORT`。

若用户要求开发具体场景，例如工装，应先在主计划中明确该场景的 `Scene Product Alpha` 范围，再按“对象体系 -> 图块 metadata -> 微场景 / failure benchmark -> 脱敏项目样本 -> 真实 CAD smoke -> 用户确认流”的顺序推进。
