# 能力证明包交接模板（V-PROOF-05）

最后更新：2026-05-27

> **主模板位置**：[`docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md`](../handoffs/CURSOR_PACKAGE_HANDOFFS.md) 顶部「交接包标准模板」→ **能力证明包附加项（10~12）**。Codex 校验清单见 [`evidence_gate_handoff_rules.md`](evidence_gate_handoff_rules.md) §7。

## 何时必填

- 任意 `V-PROOF-*` 开发包（§3 能力证明轨）。
- 修改或回写 `examples/capability_proof/cad_capability_registry.json` 的包。
- RCAD / CAD 补验包在任务清单中要求 **回写 registry** 时。

其它包在交接章节写一行：`能力证明附加项：不适用`。

## 第 10 项 — registry 行

```markdown
### 10. 能力登记表

- registry_path: examples/capability_proof/cad_capability_registry.json

| capability_id | claim_level（前→后） | ladder_level | evidence.report_path |
| --- | --- | --- | --- |
| regression.complex_cad_smoke | deferred → verified | L1 | output/validation_runs/.../complex_cad_smoke_report.json |
```

无行变更时：

```markdown
### 10. 能力登记表

- registry_path: （路径）
- 本包触及行：**无**（仅文档/工具，未改 JSON）
```

## 第 11 项 — 覆盖率

```markdown
### 11. CAD 证明覆盖率

| 指标 | 值 |
| --- | --- |
| 回写前 cad_proof_coverage_rate | 0%（252 行，0 verified） |
| 回写后 cad_proof_coverage_rate | 0.4%（252 行，1 verified） |
| 复跑命令 | python scripts/run_capability_coverage.py |
| JSON | output/validation_runs/capability-lab/cad_capability_coverage.json |
```

未改 registry 时写「未复跑 / 与上次相同」。

## 第 12 项 — Ladder

```markdown
### 12. 展示等级 Ladder

- 本包最高触及：**L1**（单点真实 CAD readback smoke）
- 是否对外提升 Ladder 声称：**否**（未更新 showcase 册）
```

## 与标准第 8 项的关系

- 第 8 项仍填 **证据类型** + **geometry_verified**（本包 CAD 步骤）。
- 第 11 项填 **登记表覆盖率**（全库统计）；二者不可互相替代。
