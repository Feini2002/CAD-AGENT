# BETA-DRAWING-READ-01 只读 DWG Entity Summary

最后更新：2026-05-26

> 机器入口：`core/drawing_analysis/dwg_read_only.py`、`scripts/run_dwg_entity_summary.py`。

## 目标

只读扫描 ModelSpace（或 fixture），输出 **`dwg_entity_summary`**：

| 区块 | 内容 |
| --- | --- |
| `type_counts` | line / text / block_reference / … |
| `layer_statistics` | 每层实体数、类型分布、层内 bbox |
| `bbox_union` | 全局包围盒 |
| `handles_sample` | handle 样本（最多 20） |
| `read_only_policy` | 明确禁止 mutate/save/write |

## 已交付

| 项 | 说明 |
| --- | --- |
| Schema | `dwg_entity_summary.schema.json` |
| Core | `build_dwg_entity_summary`、`read_entity_summary_from_fixture`、`read_active_cad_entity_summary` |
| Fixture | `examples/drawing_read/sample_modelspace_entities.json` |
| CLI | `run_dwg_entity_summary.py`（默认 fixture，`--use-cad` 可选） |
| 测试 | `tests/core/test_dwg_read_only.py` |

## 不能声称什么

- entity summary **≠** 已识别墙/门洞/柱（`BETA-DRAWING-READ-02`）。
- fixture / 只读扫描 **≠** `geometry_verified`。
- 本包 **不** 打开任意 DWG 文件路径（仅 active CAD 或 JSON fixture）。

## 子校验

```powershell
& $py -m unittest tests.core.test_dwg_read_only -v
& $py scripts\run_dwg_entity_summary.py
```

## 下一小包

`BETA-DRAWING-READ-02`：从 summary 提取墙、门洞、柱、no-place-zone 候选。
