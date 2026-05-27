# Scene Alpha Agent 边界扫描（X-SCENE-03）

## 目的

确保 `agents/` 保持轻量：只存场景偏好、词汇、workflow 说明与 manifest，不复制 Core 的 CAD 执行、回读、碰撞、几何库或 blank-shell pipeline 实现。

## 扫描入口

- 实现：`core/agents/scene_boundary_scan.py`
- 测试：`tests/agents/test_scene_agent_boundaries.py`（`test_x_scene_03_*`）
- 规则：`agents/SCENE_AGENT_RULES.md`

## 退出标准

- `agents/` 下无 `*.py` 文件。
- `scan_agent_tree(agents/)` 返回空违规列表。
- 合成违规样本能被扫描器检出（回归护栏）。

## 允许与禁止

| 允许 | 禁止 |
| --- | --- |
| `preferences.json` 中的权重、尺寸、对象优先级 | `from core.workflows` 等直接导入 Core 实现 |
| workflow 文档中的 `-> core.<module>` 流水线说明 | `run_blank_shell_pipeline`、`AutoCADComDriver` 等执行/算法符号 |
| `agent.json` 中声明 `usesCore` / `coreReuseRequired` | 在 `agents/` 内实现 `split_zones`、`rect_intersects` 等 |

## 不可声称

- 边界扫描通过 **不等于** Scene Agent 已具备真实 CAD 几何能力。
- 扫描是静态子串/导入前缀检查，不能替代 runtime 审计或 `geometry_verified` 证据。

## 相关

- 解释模板：`docs/verification/scene_alpha_explanation_template.md`（X-SCENE-04）

## 父包状态

`X-SCENE-ALPHA` 已收口；总验收见 `scene_alpha_acceptance.md`。
