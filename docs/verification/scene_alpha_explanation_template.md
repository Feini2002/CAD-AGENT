# Scene Alpha 解释模板（X-SCENE-04）

## 目的

说明 **场景偏好如何影响 Core**，而不是把 Scene Agent 写成独立设计大脑。机器可读结构由 `core/agents/scene_explanation.build_scene_explanation()` 生成；各场景 `agents/<scenario>/rules.md` 保留人类可读映射表。

## 模板结构

每个 Alpha 场景 `rules.md` 必须包含：

1. `## Preference → Core Mapping` — 偏好字段 → Core 入口 → benchmark 可观察结果  
2. `## What Scene Alpha Does Not Claim` — 不可声称边界（non-CAD、无几何 verified、非块库/非 pipeline 实现）

## Core 消费链（共用）

```text
agents/<scenario>/preferences.json
  -> workflow inputs (examples/workflows/blank_shell_<scenario>_layout_loop.json)
  -> core.workflows.blank_shell_pipeline
       -> path_generation / zone_splitter / placement / proposal / CAD_PLAN
  -> benchmark: examples/benchmarks/scene_alpha_benchmark.json
```

## 三场景可观察差异（Alpha 锁定）

| 场景 | 主对象优先 | 偏好动线 Top-1 | benchmark case |
| --- | --- | --- | --- |
| office | table | straight_spine | scene_alpha_office_blank_shell |
| residential | cabinet | along_wall | scene_alpha_residential_blank_shell |
| restaurant | chair | l_spine | scene_alpha_restaurant_blank_shell |

证据状态均为 `benchmark_pass_non_cad`，**不是** `geometry_verified`。

## 不可声称（全场景共用）

- 不能说 Scene Alpha 已完成真实 CAD 几何验证。  
- 不能说场景层实现了碰撞、通道算法、zone 切分或 CAD 执行。  
- 不能把 `scene_alpha_benchmark` pass 扩大为任意项目图纸或块库准确。  

## 相关文档

- `docs/verification/scene_alpha_preferences_contract.md`（X-SCENE-01）  
- `docs/verification/scene_alpha_agent_boundaries.md`（X-SCENE-03）  
- `agents/SCENE_AGENT_RULES.md`  
- `docs/onboarding/first-handoff.md`（Scene Alpha 接手段）

## 父包状态

`X-SCENE-ALPHA` 父包已收口（2026-05-26）；总验收见 `scene_alpha_acceptance.md`。
