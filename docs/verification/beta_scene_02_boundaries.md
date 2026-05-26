# BETA-SCENE-02 Residential Scene Beta

最后更新：2026-05-26

> 机器入口：`core/agents/residential_scene_beta.py`、`examples/benchmarks/residential_scene_beta_benchmark.json`。

## 目标

将 **residential** 提升为 Scene Beta，统一 benchmark 覆盖：

| case_tier | 内容 |
| --- | --- |
| `object` | sofa、bed 等住宅对象 |
| `bedroom` | `bedroom_bed_rug` 组合 |
| `dining` | `dining_table_set` 组合 |
| `storage` | shelf、cabinet 收纳对象 |
| `blank_shell` | 客厅 blank-shell + `along_wall` 动线 |
| `failure` | 净空冲突 blocked 样本 |

Scene Beta 仍是 **能力包**，不是住宅 Scene Product。它证明住宅对象与组合语义可跑通 non-CAD benchmark，但还没有真实住宅项目样本、真实 CAD smoke 和用户确认流。

## 已交付

| 项 | 说明 |
| --- | --- |
| 偏好 | `agents/residential/preferences.json` 增加 `scene_beta` |
| Suite | `residential_scene_beta_benchmark.json`（8 cases） |
| Runner | `residential_scene_beta.py` |
| CLI | `run_residential_scene_beta_benchmark.py` |

## 不能声称什么

- benchmark pass **≠** `geometry_verified`。
- Scene Beta **不** 实现 Core 算法或 CAD 执行。
- Scene Beta **不等于** 住宅场景产品完成。
- 失败样本为合成 composition，**不** 代表真实户型图纸。

## 子校验

```powershell
& $py -m unittest tests.agents.test_scene_beta_residential -v
& $py scripts\run_residential_scene_beta_benchmark.py
```

## 下一小包

`BETA-SCENE-03`：restaurant / commercial beta benchmark。
