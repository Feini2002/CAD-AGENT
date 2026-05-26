# BETA-DRAWING-READ-02 几何特征候选提取

最后更新：2026-05-26

> 机器入口：`core/drawing_analysis/geometry_candidates.py`、`scripts/run_geometry_candidates.py`。

## 目标

在 `BETA-DRAWING-READ-01` entity summary 基础上，从规范化实体列表启发式提取：

| 候选类型 | 说明 |
| --- | --- |
| `wall_segment_candidates` | 墙线段（层名 / 层内 line 主导） |
| `door_opening_candidates` | 门洞块参照（层名或块名） |
| `column_candidates` | 柱块参照 |
| `no_place_zone_candidates` | 禁放区 polyline/hatch（层名） |

输出 **`dwg_geometry_candidates`**，含 `confidence` 与 `detection_rule`。

## 已交付

| 项 | 说明 |
| --- | --- |
| Schema | `dwg_geometry_candidates.schema.json` |
| Core | `extract_geometry_candidates`、`read_geometry_candidates_from_fixture` |
| Fixture | `sample_geometry_feature_fixture.json`（4 墙 + 门 + 柱 + 禁放区） |
| CLI | `run_geometry_candidates.py` |
| 测试 | `tests/core/test_geometry_candidates.py` |

## 不能声称什么

- 候选列表 **≠** `SHELL_MODEL`（`BETA-DRAWING-READ-04`）。
- 启发式提取 **≠** `geometry_verified`。
- 未人工确认前 **不得** 直接驱动 blank-shell 落 CAD。

## 子校验

```powershell
& $py -m unittest tests.core.test_geometry_candidates -v
& $py scripts\run_geometry_candidates.py
```

## 下一小包

`BETA-DRAWING-READ-04`：人工确认文件回写为 `SHELL_MODEL`（READ-03 已完成，见 `beta_drawing_read_03_boundaries.md`）。
