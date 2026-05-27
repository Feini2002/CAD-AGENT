# BETA-SCENE-03 Restaurant / Commercial Scene Beta

最后更新：2026-05-26

> 机器入口：`core/agents/restaurant_scene_beta.py`、`examples/benchmarks/restaurant_scene_beta_benchmark.json`。

## 目标

将 **restaurant**（商用前厅）提升为 Scene Beta，统一 benchmark 覆盖：

| case_tier | 内容 |
| --- | --- |
| `object` | table、chair |
| `entrance` | counter + `entry_reception_clearance`（入口/接待） |
| `seating` | `dining_table_set` 堂食桌椅 |
| `back_of_house` | `storage_cabinet` 后场收纳 |
| `blank_shell` | 前厅 shell + `l_spine` 动线 + service 禁放区 |
| `failure` | 入口净空冲突 blocked |

## 已交付

| 项 | 说明 |
| --- | --- |
| 偏好 | `agents/restaurant/preferences.json` 增加 `scene_beta` |
| Suite | `restaurant_scene_beta_benchmark.json`（8 cases） |
| Runner | `restaurant_scene_beta.py` |
| CLI | `run_restaurant_scene_beta_benchmark.py` |

## 不能声称什么

- benchmark pass **≠** `geometry_verified` 或真实餐饮平面准确。
- 入口组合复用 office 模板 **≠** 餐饮专用语义已完备。
- Scene Beta **不** 实现 Core 算法或 CAD 执行。

## 子校验

```powershell
& $py -m unittest tests.agents.test_scene_beta_restaurant -v
& $py scripts\run_restaurant_scene_beta_benchmark.py
```

## 下一小包

`BETA-SCENE-04`：场景解释模板增强（偏好如何影响候选）。
