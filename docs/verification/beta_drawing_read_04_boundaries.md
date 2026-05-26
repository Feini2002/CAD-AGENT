# BETA-DRAWING-READ-04 人工确认回写 SHELL_MODEL

最后更新：2026-05-26

> 机器入口：`core/drawing_analysis/shell_confirmation.py`、`scripts/apply_shell_drawing_read_confirmation.py`。

## 目标

将 `BETA-DRAWING-READ-03` 的 **`shell_candidate_confidence_report`** 与人工确认文件 **`shell_drawing_read_confirmation`** 合成为可通过 `shell_loader` 的 **`SHELL_MODEL`**。

| 步骤 | 说明 |
| --- | --- |
| 校验 | confirmation schema + 必填 `confirmed_items` 覆盖 report 中 `required` 项 |
| 合成 | 草案 boundary / openings / obstacles / no_place → shell 字段 |
| 规范化 | `load_manual_shell()` 做 bbox / 边界内含校验 |

## 已交付

| 项 | 说明 |
| --- | --- |
| Schema | `shell_drawing_read_confirmation.schema.json` |
| Core | `build_shell_drawing_read_confirmation`、`apply_shell_drawing_read_confirmation` |
| 示例 | `sample_shell_drawing_read_confirmation.json` |
| CLI | `apply_shell_drawing_read_confirmation.py` |
| 测试 | `tests/core/test_shell_confirmation.py`（含 shell_model schema pass） |

## 不能声称什么

- 通过 loader 的 SHELL_MODEL **≠** `geometry_verified` 或已跑 blank-shell CAD。
- `accept_with_risks` 可绕过 `ready_for_human_confirmation_file`，仍须人工承担风险。
- 本包 **不** 打开任意 DWG；仅处理 READ-01~03 的 fixture / 报告链路。

## 子校验

```powershell
& $py -m unittest tests.core.test_shell_confirmation -v
& $py scripts\apply_shell_drawing_read_confirmation.py
```

## 下一小包

`BETA-DRAWING-READ-05`：读图链路 benchmark 化。
