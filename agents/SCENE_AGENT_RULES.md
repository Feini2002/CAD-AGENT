# Scene Agent Rules

场景 Agent 是轻量偏好层，不是第二套 Core。

## 可以放在 Agent 中

- 场景词汇。
- 默认参数。
- 业务偏好。
- workflow 名称和步骤说明。
- 评分权重。
- 对 `libraries/` 资源的优先级。

## 不可以放在 Agent 中

- 通用对象生成算法。
- 通用碰撞检测。
- 通用通道宽度算法。
- 通用图纸读取。
- 通用 `CAD_PLAN` 校验、dry-run、执行、截图、实体回读。
- 真实项目资料。
- 公司专属块库本体。

这些能力应放在 `core/`、`libraries/` 或 `projects/` 的对应边界内。

## 边界扫描（X-SCENE-03）

`agents/` 目录下不得出现 Python 实现文件（`*.py`）；场景差异只通过 `preferences.json`、`rules.md`、`agent.json` 与 workflow 说明表达。

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
