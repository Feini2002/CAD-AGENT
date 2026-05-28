# 读图人工确认 Gate（BETA-DRAWING-READ-06）

最后更新：2026-05-28

## 目标

在 `BETA-DRAWING-READ-01`~`05` 机器链路之上，固定**人工确认**是唯一允许把读图结果写入 `SHELL_MODEL` 并进入落 CAD 的前置条件。

## 流程

```text
DWG/PDF（只读） → entity summary / 几何候选 → shell_candidate_confidence_report
    → 人工填写 shell_drawing_read_confirmation.json
    → BETA-DRAWING-READ-04 合成 SHELL_MODEL
    → validate + dry-run →（可选）CODEX_PREVIEW 落图
```

## 禁止

- 未确认 shell candidates **不得**直接生成可执行 `CAD_PLAN` 并落真实 CAD。
- 读图置信度报告 **≠** 几何 verified。
- 不能把 OCR/猜测尺寸当作 `geometry_verified`。

## 人工确认文件最小字段

| 字段 | 说明 |
| --- | --- |
| `confirmed_shell_id` | 与候选报告一致 |
| `confirmed_by` | 操作者标识 |
| `confirmed_at` | ISO 时间 |
| `accept_candidate_ids` | 采纳的候选 ID 列表 |
| `reject_candidate_ids` | 明确拒绝的候选 |
| `notes` | 自由文本备注 |

## 相关验证

- `docs/verification/beta_drawing_read_03_boundaries.md`
- `docs/verification/beta_drawing_read_04_boundaries.md`
- `tests/core/test_drawing_read_*`（按仓库现有用例）

## 下一包

- `BETA-DRAWING-READ-07`：真实 DWG 只读样本（需用户脱敏文件，放 `projects/` 而非 `core/`）
