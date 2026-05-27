# SCENE-PROD-05：Scene Beta 解释模板

最后更新：2026-05-27

本文是 `BETA-SCENE-04` 的代码轨收口文档：说明 office / residential / restaurant 的 scene beta 偏好如何影响 Core 候选、benchmark 可观察字段和证据边界。它不是新的 CAD 执行层，也不把场景 preferences 写成独立设计大脑。

## 机器入口

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_scene_prod_05_scene_explanation_template -v
& $py scripts\run_scene_beta_explanation_template.py --output output\validation_runs\scene-prod-05-explanation-template-no-cad
```

结构化入口：`core.agents.scene_beta_explanation.build_scene_beta_explanation()`

## 模板结构

每个 scene beta 解释对象必须包含：

| 字段 | 用途 |
| --- | --- |
| `scenario` / `tier` | 标识 office / residential / restaurant 与 beta 成熟度 |
| `benchmark_suite` | 指向对应 no-CAD benchmark |
| `observable_signature` | 记录首要对象、偏好动线、benchmark suite 与对象偏好数量 |
| `preference_to_core` | 把偏好字段映射到 Core 入口和可观察影响 |
| `benchmark_observables` | 标明 benchmark 中可被测试读取的观察点 |
| `evidence_boundaries` | 固定 `benchmark_pass_non_cad`、`blocked_expected_non_cad` 与 `not_verified_without_cad_readback` |
| `does_not_claim` | 固定不得声称边界 |

## 三场景可观察差异

| 场景 | beta benchmark | 首要对象 | 偏好动线 |
| --- | --- | --- | --- |
| office | `examples/benchmarks/office_scene_beta_benchmark.json` | table | straight_spine |
| residential | `examples/benchmarks/residential_scene_beta_benchmark.json` | cabinet | along_wall |
| restaurant | `examples/benchmarks/restaurant_scene_beta_benchmark.json` | chair | l_spine |

这些差异可解释为什么候选和 benchmark case 有不同对象、动线和失败样本；它们仍只是 no-CAD 可观察行为。

## 可声称

- `build_scene_beta_explanation()` 可以把 scene beta preferences 映射到 Core layout、object ordering、benchmark suite 和 evidence boundary。
- 三个 scene beta benchmark 的解释模板可统一生成，并能说明 `benchmark_pass_non_cad` 与 `blocked_expected_non_cad` 的含义。
- `BETA-SCENE-04` 的解释模板边界已具备机器可读入口。

## 不得声称

- 不得声称 scene beta preferences 或解释模板已经证明真实 CAD `geometry_verified`。
- 不得把 `benchmark_pass_non_cad`、`blocked_expected_non_cad`、SVG/PNG 预览或 dry-run 当成 created-handle readback。
- 不得声称 `agents/office`、`agents/residential`、`agents/restaurant` 已经是完整场景产品 Agent。
- 不得跳过 validate、dry-run、`CODEX_PREVIEW`、created handles 回读和 registry 回写来提升表 C。

## 证据路径

本包输出：

- `output/validation_runs/scene-prod-05-explanation-template-no-cad/scene_beta_explanation_summary.json`

该 JSON 只证明解释模板和 scene beta preferences 的 no-CAD 契约可读，不包含真实 CAD `geometry_verified`。
