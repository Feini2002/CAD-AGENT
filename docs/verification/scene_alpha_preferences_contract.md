# Scene Alpha Preferences 契约（X-SCENE-01）

最后更新：2026-05-26

> 机器清单：`agents/scene_alpha_manifest.json`；校验逻辑：`core/agents/scene_alpha.py`；测试：`tests/agents/test_scene_preferences.py`。

## 锁定的 3 个 Alpha 场景

| 场景 | `preferences.json` | 可观察差异（摘要） |
| --- | --- | --- |
| `office` | `agents/office/preferences.json` | 主对象优先 `table`；偏好 `straight_spine` 动线；主通道 1100mm |
| `residential` | `agents/residential/preferences.json` | 主对象优先 `cabinet`；偏好 `along_wall`；主通道 900mm |
| `restaurant` | `agents/restaurant/preferences.json` | 主对象优先 `chair`；偏好 `l_spine`；主通道 1200mm |

每个文件含 `scene_alpha.tier: "alpha"` 与 `circulation.circulation_strategy_weights`（**场景层数据**，非 Core 算法）。

## 可观察差异类型（X-SCENE-01 退出标准）

1. **对象优先级**：`object_preferences[0]` 在 manifest 中逐场景断言。
2. **通道宽度**：`main_aisle_width_mm` / `secondary_aisle_width_mm` 影响 `create_layout_candidates` 间距。
3. **候选排序权重**：`circulation_strategy_weights` 改变 `generate_circulation_candidates` 的 Top-1 strategy（无场景 if/else 分支）。

## 不能声称

- Scene Agent **不是** Core 算法副本；`agents/` 不得含 CAD 执行、碰撞、几何库调用（见 `SCENE_AGENT_RULES.md` 与 `scene_alpha_agent_boundaries.md`，**X-SCENE-03 已完成**）。
- preferences 差异 **不等于** 真实项目已验证或几何准确。
- `commercial_fitout`、`exhibition` 等仍存在于仓库，但 **不在** Scene Alpha 三场景契约内。

## 子校验

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.agents.test_scene_preferences -v
```

## 下一小包

`X-SCENE-02`（**已完成**）：`examples/benchmarks/scene_alpha_benchmark.json`；三场景 `blank_shell` workflow 均 `benchmark_pass_non_cad`；按场景断言 `selected_circulation_strategy`。

`X-SCENE-04`（**已完成**）：`scene_alpha_explanation_template.md`、`build_scene_explanation()`、三场景 `rules.md` 映射表、`first-handoff` Scene Alpha 段。

`X-SCENE-05`（**已完成**）：见 `scene_alpha_acceptance.md`。
