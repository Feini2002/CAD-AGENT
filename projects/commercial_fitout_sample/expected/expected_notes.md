# Commercial Fitout Sample Expected Notes

脱敏工装开放办公样本（C-CFIT-05）的非 CAD 预期。

- `design_brief.needs_confirmation` 必须为 `true`；确认前 pipeline 状态为 `confirmation_pending`。
- 确认前不得写出 `cad_plan` / `cad_plans` / `dry_run_report`。
- 用户确认后应生成 `confirmed_cad_plan_bundle.json`，且所有 `CAD_PLAN.needs_confirmation` 为 `false`。
- `commercial_fitout_sample_confirmation_bundle.json` 必须记录 brief assumptions 与 confirmation 中的 risk notes。
- 没有真实 CAD 落图和实体回读前，不得声称几何准确。
