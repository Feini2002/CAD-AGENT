# BETA-SCENE-04 Exhibition + Healthcare Scene Beta

最后更新：2026-05-28

> 机器入口：`core/agents/exhibition_scene_beta.py`、`core/agents/healthcare_scene_beta.py`、`examples/benchmarks/*_scene_beta_benchmark.json`。

## 目标

在 office / residential / restaurant Scene Beta 已收口后，为 **exhibition（展陈）** 与 **healthcare（医疗）** 各增加最小 scene benchmark manifest + runner，复用 Core pipeline；算法与 CAD 执行仍在 `core/`，`agents/` 只承载偏好与路由。

| 场景 | case_tier 覆盖 |
| --- | --- |
| **exhibition** | `object` / `display` / `visitor_flow` / `back_of_house` / `blank_shell` / `failure`（7 cases，6 pass + 1 blocked） |
| **healthcare** | `object` / `clinical` / `waiting` / `blank_shell` / `failure`（6 cases，5 pass + 1 blocked） |

## 已交付

| 项 | 说明 |
| --- | --- |
| 偏好 | `agents/exhibition/preferences.json`、`agents/healthcare/preferences.json`（`scene_beta.tier=beta`） |
| Shell / workflow | `exhibition_small_hall_shell`、`healthcare_clinic_waiting_shell` + 对应 `blank_shell_*_layout_loop.json` |
| Suite | `exhibition_scene_beta_benchmark.json`、`healthcare_scene_beta_benchmark.json` |
| Runner | `exhibition_scene_beta.py`、`healthcare_scene_beta.py` |
| CLI | `run_exhibition_scene_beta_benchmark.py`、`run_healthcare_scene_beta_benchmark.py`、`run_beta_scene_04_exhibition_healthcare_benchmark.py` |
| 测试 | `tests/agents/test_scene_beta_exhibition.py`、`test_scene_beta_healthcare.py`、`test_beta_scene_04_exhibition_healthcare_boundary.py` |

## 不能声称什么

- benchmark pass **≠** `geometry_verified` 或展陈/医疗真实 CAD 平面准确。
- 本包 **不** 批量新增 `cad_capability_registry` 的 `claim_level: none` 行（见 `agent_vertical_registry_strategy.md`）。
- Scene Beta **不** 在 `agents/` 实现 Core 算法或 CAD 执行；**≠** 完整 Scene Product。

## 子校验

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.agents.test_scene_beta_exhibition tests.agents.test_scene_beta_healthcare tests.core.test_beta_scene_04_exhibition_healthcare_boundary -v
& $py scripts\run_beta_scene_04_exhibition_healthcare_benchmark.py
```

## 可选真实 CAD

- 已有域 smoke：`domain.exhibition.draw_object` / `domain.healthcare.draw_object`（表 C showcase，非本包新增 registry 行）。
- 本轮已执行 1 条：`domain-smoke/exhibition_only/domain_exhibition_cad_smoke.json`（`geometry_verified`）。

## 证据

- `output/validation_runs/beta-scene-04-20260528/beta_scene_04_rollup.json`
- `output/validation_runs/beta-scene-04-20260528/exhibition/`、`.../healthcare/`

## 下一小包

`BETA-SCENE-05` 或 `post-backlog.md` 中下一项 ready 包（如 `VCAD-04`、`BETA-CROSS-MACHINE-02`）。
