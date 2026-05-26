# BETA-DRAWING-READ-03 Shell 候选置信度报告

最后更新：2026-05-26

> 机器入口：`core/drawing_analysis/shell_candidate_report.py`、`scripts/run_shell_candidate_report.py`。

## 目标

在 `BETA-DRAWING-READ-02` 几何候选基础上，输出 **`shell_candidate_confidence_report`**：

| 区块 | 内容 |
| --- | --- |
| `confidence` | overall / boundary / openings / fixed_obstacles / no_place_zones |
| `shell_candidate_draft` | 草案 boundary、开口、障碍、禁放区（非正式 SHELL_MODEL） |
| `gaps` | 结构化缺口（`code` + `severity`：warning / blocker） |
| `human_confirmation_items` | 需人工确认点（含 `confirm_*` / `resolve_gap`） |
| `ready_for_human_confirmation_file` | 无 blocker 且 overall ≥ 0.65 时为 true |

## 已交付

| 项 | 说明 |
| --- | --- |
| Schema | `shell_candidate_confidence_report.schema.json` |
| Core | `build_shell_candidate_confidence_report`、`read_shell_candidate_report_from_fixture` |
| Fixture | `sample_geometry_feature_fixture.json`（完整）、`sample_geometry_walls_only_fixture.json`（缺门洞） |
| CLI | `run_shell_candidate_report.py` |
| 测试 | `tests/core/test_shell_candidate_report.py` |

## 不能声称什么

- 草案 **≠** 已验证 `SHELL_MODEL`（`BETA-DRAWING-READ-04`）。
- `ready_for_human_confirmation_file=true` **≠** 可自动落 CAD。
- 报告 **≠** `geometry_verified`。

## 子校验

```powershell
& $py -m unittest tests.core.test_shell_candidate_report -v
& $py scripts\run_shell_candidate_report.py
```

## 下一小包

`BETA-DRAWING-READ-05`：读图链路 benchmark 化（READ-04 已完成，见 `beta_drawing_read_04_boundaries.md`）。
