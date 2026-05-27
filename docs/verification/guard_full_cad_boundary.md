# LCAD-14：Guard 全链路 Strict 包装边界

最后更新：2026-05-27

## LCAD-14-GUARD-FULL-CAD

`LCAD-14-GUARD-FULL-CAD` 把 LCAD-03 守卫链收成一条可复跑的 strict 子报告，入口为 `scripts/run_guard_full_cad_runner.py`。子报告固定为三段：

1. `write_guard_cad_runner` — 负向 `CAD_PLAN` + preview write guard
2. `negative_cad_runner` — 无 handles / 不保存 / session snapshot delta
3. `run_cad_capability_probe` — preview 写入 + created-handle readback + `session_guard`

顶层 `guard_full_cad_report.json` 的 `strict_gate` 在 `strict` 模式下要求：

- `write_guard.status=pass`
- `negative_cad.status=pass` 且 `evidence_state=negative_guard_verified`
- `capability_probe.status=cad_capability_verified`
- `validate_capability_probe_evidence()` 无错误
- `capability_probe.session_guard.status=consistent`

## 与 RCAD-21 / V-PROOF-52

- **RCAD-21**：在用户 AutoCAD 会话下对同一 runner 加 `--real-cad`，复用 `subreports/` 工件路径。
- **V-PROOF-52**：登记 guard / snapshot 字段已可由 strict 子报告机器断言；不等于任意 `CAD_PLAN` 几何已通过。

## 不得声称

- 不得把 fake/no-CAD 的 `guard_full_cad_report.json` 说成真实 AutoCAD 会话已全链路 verified。
- 不得把 strict pass 说成 `geometry_verified` 已覆盖项目 DWG 或块库。
- `negative_guard_verified` 与 `cad_capability_verified` 仍只覆盖各自子报告语义；顶层 strict 只证明**守卫链字段齐全且自洽**。
