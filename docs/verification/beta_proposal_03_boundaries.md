# BETA-PROPOSAL-03 用户确认输入 Schema

最后更新：2026-05-26

> 机器入口：`proposal_user_confirmation.schema.json`、`core/proposal_engine/user_confirmation.py`。

## 目标

定义 **`PROPOSAL_USER_CONFIRMATION`**，承载：

| 字段 | 说明 |
| --- | --- |
| `action` | `accept` / `accept_with_risks` / `reject_all` |
| `selected_candidate_id` | 选中候选 |
| `rejected_candidates[]` | `reason_code` + 可选 `reason_note` |
| `local_preferences` | `candidate_weights`、`placement_offsets`、`notes` |

## 已交付

| 项 | 说明 |
| --- | --- |
| Schema | `proposal_user_confirmation.schema.json` |
| Core | `validate_confirmation_*`、`build_user_confirmation`、`apply_user_confirmation` |
| 示例 | `examples/confirmations/*.json` |
| CLI | `scripts/apply_proposal_user_confirmation.py` |
| 测试 | round-trip、schema、apply 后 `proposal_to_plans` |

## 不能声称什么

- 确认 JSON 存在 **≠** 真实 CAD 已验证。
- `accept_with_risks` **≠** 自动忽略所有 layout 风险（仅关闭 `needs_confirmation` 门闩）。

## 子校验

```powershell
& $py -m unittest tests.core.test_proposal_user_confirmation -v
```

## 下一小包

`BETA-PROPOSAL-04`（已完成）：见 `beta_proposal_04_boundaries.md`。
