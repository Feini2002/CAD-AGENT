# Scene Alpha 总验收（X-SCENE-ALPHA 父包收口）

最后更新：2026-05-26

> 机器入口：`examples/benchmarks/scene_alpha_benchmark.json`、`agents/scene_alpha_manifest.json`、`tests/agents/test_scene_alpha_acceptance.py`。证据词表见 [`evidence_gate_handoff_rules.md`](evidence_gate_handoff_rules.md)。

本文只证明 **Scene Alpha 壳层**：场景 preferences 可以驱动同一 Core pipeline，并且 `agents/` 没有复制 Core 算法。它不证明 **Scene Product**：没有真实项目样本闭环、没有场景专属图块策略、没有多场景真实 CAD smoke，也没有用户确认流。

## 父包 `X-SCENE-ALPHA` 已交付（01–05）

| 小包 | 能力 | 主要 artifact / 入口 |
| --- | --- | --- |
| `X-SCENE-01` | 锁定 office / residential / restaurant preferences 差异 | `core/agents/scene_alpha.py`、`scene_alpha_preferences_contract.md` |
| `X-SCENE-02` | 三场景复用同一 `blank_shell` pipeline + benchmark | `scene_alpha_benchmark.json`（3 cases） |
| `X-SCENE-03` | `agents/` 边界静态扫描 | `scene_boundary_scan.py`、`scene_alpha_agent_boundaries.md` |
| `X-SCENE-04` | 偏好 → Core 解释模板 | `scene_explanation.py`、`scene_alpha_explanation_template.md` |
| `X-SCENE-05` | 本文 + 总验收测试与状态同步 | `test_scene_alpha_acceptance.py` |

**最新证据（2026-05-26）**：见 `output/test_artifacts/benchmarks/x_scene_05/`（scene alpha 3/3 pass）；全量 unittest 见 CHANGELOG / handoff §29。

## 现在可以声称什么

- **至少 3 个场景**（office、residential、restaurant）复用 **同一类** Core `blank_shell` pipeline，不经 `agents/` 复制实现。
- 场景 **preferences 差异可观察**：对象优先级、通道宽度、`circulation_strategy_weights` 导致不同的 `selected_circulation_strategy`（benchmark 硬断言）。
- `agents/` 为轻量层：无 `.py` 实现文件；边界扫描对 prefs/json 禁止 CAD/几何/pipeline 符号；`rules.md` 仅文档化 Core 入口。
- 场景解释模板说明偏好如何进入 Core，而非独立 Agent 大脑。

## 不能声称什么（必须继续遵守）

- **不能说** Scene Agent 产品已完整完成（无真实项目闭环、无 Beta 全场景、无用户确认流）。
- **不能说** office / residential / restaurant 的 Alpha 或 Beta benchmark 等于工装、办公、住宅、餐饮任一具体场景产品完成。
- **不能说** `scene_alpha_benchmark` 或 blank-shell non-CAD pass 等于 **`geometry_verified`**。
- **不能说** 任意 DWG、块库、真实项目图纸已由场景 Agent 自动画准。
- **不能说** 静态边界扫描替代 runtime CAD 审计或 created-handle 回读。
- **不能把** 场景层写成第二套 Core（碰撞、zone 切分、CAD 执行、readback 仍在 `core/`）。

## Benchmark 契约摘要（`scene_alpha_benchmark.json`）

| 汇总 | 值 |
| --- | --- |
| `case_count` | 3 |
| `benchmark_pass_non_cad_count` | 3 |
| `readback_geometry_verified_count` | 0 |
| `non_cad_only` | true |

| case_id | `preferences_scenario` | `selected_circulation_strategy` |
| --- | --- | --- |
| `scene_alpha_office_blank_shell` | office | straight_spine |
| `scene_alpha_residential_blank_shell` | residential | along_wall |
| `scene_alpha_restaurant_blank_shell` | restaurant | l_spine |

## 子校验（总验收）

```powershell
& $py -m unittest tests.agents.test_scene_alpha_acceptance tests.agents.test_scene_preferences tests.agents.test_scene_agent_boundaries tests.agents.test_scene_explanation -v
& $py scripts\run_benchmark_suite.py examples\benchmarks\scene_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\x_scene_05
```

## 下一主线（PlanMD）

`X-SCENE-ALPHA` 父包已收口。后续按 `CORE_RESTRUCTURE_PLAN.md` 后置 Backlog 或用户指定主线推进（真实 CAD 扩展、项目样本、多方案确认、自动读图、Scene Agent Beta、工装 Scene Product Alpha 等）；不得跳过证据门槛声称几何已验证。Core / 场景边界详见 `../architecture/core-scene-agent-boundaries.md`。
