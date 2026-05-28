# runs/

每轮训练产物（建议大截图 gitignore，JSON 可留）：

| 步骤 | 文件 |
| --- | --- |
| Step1 需求拆分 | `roundN_intent.json`（必写） |
| Step1 可选 | `roundN_cad_plan.json`、`dry_run_report.json` |
| Step2 落图 | `roundN_execution_summary.json`、`*_vector_readback.json` |
| Step3 审计 | `roundN_geometry_audit.json`、`roundN_audit_review.md` |
| 目视 | `roundN_preview.png` |

三角色现阶段由**同一个 Agent 分步**完成；见 `docs/training/README.md` §三角色。
