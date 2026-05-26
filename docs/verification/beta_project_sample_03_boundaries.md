# BETA-PROJECT-SAMPLE-03 样本 Workflow → CAD_PLAN / Dry-run / Verification

最后更新：2026-05-26

> 后置主线：**真实项目样本闭环** 第 3 小包。机器入口：`examples/workflows/sample_blank_shell_project_loop.json`、`core/project_samples/workflow.py`。

## 目标

让 `sample_blank_shell` 走完整 **blank-shell pipeline**，产出：

- `cad_plan.json` / `cad_plans.json`
- `dry_run_report.json`（`status=valid`）
- `verification_report.json`（**`status=unverified`**，无 CAD readback）

## 已交付

| 项 | 说明 |
| --- | --- |
| Workflow | `sample_blank_shell_project_loop.json`（inputs 指向 `projects/sample_blank_shell/`） |
| Runner | `run_sample_blank_shell_workflow()`、`write_sample_workflow_report()` |
| CLI | `scripts/run_project_sample_workflow.py` |
| 测试 | `tests/core/test_project_sample_workflow.py` |

## 契约摘要

| 输出 | 期望 |
| --- | --- |
| pipeline `status` | `ok` |
| `dry_run_report.status` | `valid` |
| `verification_report.status` | `unverified` |
| `cad_plan.drawing.layer` | `CODEX_PREVIEW` |
| `geometry_verified` | **false**（报告字段） |

## 不能声称什么

- **不是** 真实 CAD 几何已验证。
- **不是** 任意项目 DWG 已自动落图准确。

## 子校验

```powershell
& $py -m unittest tests.core.test_project_sample_workflow -v
& $py scripts\run_project_sample_workflow.py
```

## 下一小包

`BETA-PROJECT-SAMPLE-04`：样本纳入 benchmark（成功/失败断言）。
