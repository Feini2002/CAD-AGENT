# BETA-SCENE-01 Office Scene Beta

最后更新：2026-05-26

> 机器入口：`core/agents/scene_beta.py`、`core/agents/office_scene_beta.py`、`examples/benchmarks/office_scene_beta_benchmark.json`。

## 目标

在 `X-SCENE-ALPHA` 已证明三场景复用 Core 的前提下，将 **office** 提升为 Scene Beta 入口：

| 层级 | 内容 |
| --- | --- |
| 偏好 | `agents/office/preferences.json` 增加 `scene_beta` + 扩展 `object_preferences` |
| 统一 benchmark | 对象 / 微场景 / blank-shell / 失败样本 9 cases 同一 suite |
| 断言 | `preferences_scenario=office`、`straight_spine`、evidence 计数 |

## 已交付

| 项 | 说明 |
| --- | --- |
| Core | `scene_beta.py`、`office_scene_beta.py` |
| Manifest | `agents/scene_beta_manifest.json` |
| Suite | `office_scene_beta_benchmark.json` |
| CLI | `run_office_scene_beta_benchmark.py` |
| 测试 | `tests/agents/test_scene_beta_office.py` |

## 不能声称什么

- office beta benchmark pass **≠** `geometry_verified` 或办公真实 CAD 准确。
- Scene Beta **不** 在 `agents/` 实现 Core 算法或 CAD 执行。
- 本包 **仅** 覆盖 office；residential / restaurant 为后续 `BETA-SCENE-02/03`。

## 子校验

```powershell
& $py -m unittest tests.agents.test_scene_beta_office -v
& $py scripts\run_office_scene_beta_benchmark.py
```

## 下一小包

`BETA-SCENE-02`：residential beta benchmark。
