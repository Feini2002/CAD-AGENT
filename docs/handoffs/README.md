# Cursor / Codex 交接包目录

## 用途

本目录存放 **Cursor 按开发包完成的交付交接包**，供后续 Codex 高智力校验、审计或换机接手使用。

## 主文档

| 文件 | 说明 |
| --- | --- |
| [`CURSOR_PACKAGE_HANDOFFS.md`](CURSOR_PACKAGE_HANDOFFS.md) | **唯一汇总入口**：按开发包分节，每节含 9 项标准字段 |
| [`../verification/evidence_gate_handoff_rules.md`](../verification/evidence_gate_handoff_rules.md) | **Evidence gate**：第 8 项结论分类与 Codex 校验清单（R4-05） |

## 与其它文档的关系

| 文档 | 职责 |
| --- | --- |
| `CURSOR_PACKAGE_HANDOFFS.md` | 按包的完整交接（给 Codex 校验） |
| `CAD_AGENT_CHANGELOG.md` | 按日期的变更流水（简版） |
| `CAD_AGENT_STATUS.md` | 当前能力与最近验证摘要 |
| `docs/planning/phase-r-rebirth-implementation-plan.md` | 执行剧本与「执行记录」 |
| `output/validation_runs/<包名>/` | 机器可读验证证据（report / readback / 截图） |

## 维护规则

每完成一个开发包，Cursor 必须：

1. 在 `CURSOR_PACKAGE_HANDOFFS.md` 追加或更新对应章节（固定 9 项模板；第 8 项按 `evidence_gate_handoff_rules.md` 填表）。
2. 同步 `CAD_AGENT_CHANGELOG.md`、`CAD_AGENT_STATUS.md`（有功能证据时还有 `CORE_STATUS.md`）。
3. 若包涉及真实 CAD，在 `output/validation_runs/<包名>-no-cad` 与（如适用）`<包名>-cad` 留下证据；第 8 项须区分 non-CAD 与 `geometry_verified`。
