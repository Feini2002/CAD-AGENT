# Round N 审计自检（审计环 · 简单步骤）

案例：`your_case_id`
输入：`roundN_intent.json` · `roundN_geometry_audit.json` · `roundN_preview.png`

## 1. 机器审计摘要

| 项 | 值 |
| --- | --- |
| `audit_pass` | |
| `audit_failures` | |

## 2. 对照 intent / brief + agent_review_required

Checklist 中 `agent_review_required` 每项须勾选：

| 项 | 结果 |
| --- | --- |
| visual_match_brief | |
| （案例自定义项） | |

## 3. 残留风险

-

## 4. 审计环判定

- [ ] 不可请你验收（须回到落图 / 改 checklist）
- [ ] 可请你 §几何 feedback

## 5. checklist / 全局探针优化建议（可选）

若 fail 或险些 fail：

- 先改 `expected/audit_checklist.json` 阈值
- 若 **第二个案例** 也遇到 → 晋升探针到 `core/verification/training_geometry_audit.py`（见 `audit-architecture.md`）
