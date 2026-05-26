# Phase X Scene Agent Alpha Plan

状态：**Scene Alpha 父包已收口（X-SCENE-ALPHA 01–05，2026-05-26）**
最后同步：2026-05-26

> 本文是 Phase X 辅助执行剧本，不是独立 PlanMD。执行顺序、优先级和退出标准以根目录 `CORE_RESTRUCTURE_PLAN.md` 为准；执行前仍需先读 `AGENTS.md` 与 `CORE_CONTEXT_BRIEF.md`，并遵守 `CODEX_PREVIEW`、不保存、不覆盖、不删除、不改正式图层的 CAD 安全边界。

## Phase X：场景 Agent 接入与 Alpha 验收

目标：证明场景 Agent 是轻量复用层，而不是复制 Core 算法。至少 3 个场景应复用同一 `workflow.blank_shell_pipeline`，并通过 preferences 改变候选排序、对象组合或约束解释。

### 当前前置事实

- `agents/commercial_fitout/`、`agents/residential/`、`agents/office/`、`agents/restaurant/` 已有 preferences 或工作流基础。
- `workflow.blank_shell_pipeline` 已进入 capability registry。
- 4 场景 benchmark 已能跑通，但仍偏 Core benchmark，不等于完整场景 Alpha 验收。

### 文件范围

- 修改：`agents/commercial_fitout/preferences.json`
- 修改：`agents/residential/preferences.json`
- 修改：`agents/office/preferences.json`
- 修改：`agents/restaurant/preferences.json`
- 修改：`agents/SCENE_AGENT_RULES.md`
- 修改：`tests/agents/test_scene_preferences.py`
- 修改或新增：`tests/agents/test_blank_shell_scene_preferences.py`
- 修改：`examples/benchmarks/blank_shell_core_benchmark.json`

### 执行参考

- X-01 盘点四个场景 preferences，列出通道宽度、功能优先级、对象优先级、zone 权重、placement 偏好。
- X-02 写测试：同一 shell 输入在不同 preferences 下应产生不同候选排序、对象组合或解释字段。
- X-03 补齐 preferences 缺字段时的明确失败原因，不允许静默回退成隐式默认场景。
- X-04 扩展 agent 边界测试，继续禁止场景层实现 CAD 执行、回读、碰撞、几何算法。
- X-05 用至少 3 个场景跑 blank-shell pipeline，保存 benchmark summary。
- X-06 更新 `agents/SCENE_AGENT_RULES.md`，写清场景层只提供偏好、词汇、流程命名和业务权重。
- X-07 同步 `CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md`。

### 验证命令

```powershell
& $py -m unittest discover -s tests\agents
& $py -m unittest tests.core.test_capabilities
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\scene-alpha
```

### 退出标准（**已满足，2026-05-26**）

- 至少 3 个场景 Agent 可复用同一 blank-shell pipeline。✅ `scene_alpha_benchmark.json` 3/3 pass
- preferences 差异在测试或 benchmark 中可观察。✅ `test_scene_preferences` + benchmark 动线断言
- 场景层没有复制 Core 几何、CAD 执行或验证算法。✅ `scene_boundary_scan` + `test_scene_agent_boundaries`
- 仍明确标注：这是 non-CAD Alpha，不证明真实项目图纸、块库或 `geometry_verified`。✅ `scene_alpha_acceptance.md`

总验收文档：`docs/verification/scene_alpha_acceptance.md`；子校验 `tests/agents/test_scene_alpha_acceptance.py`。

---


## 状态同步要求

完成或调整本 Phase 后，同步：

- `CORE_RESTRUCTURE_PLAN.md`
- `CORE_CONTEXT_BRIEF.md`
- `CORE_STATUS.md`
- `CAD_AGENT_STATUS.md`
- `CAD_AGENT_CHANGELOG.md`

只有出现失败、回归、CAD 环境问题或验证教训时，才同步 `CAD_AGENT_ISSUES.md`。
