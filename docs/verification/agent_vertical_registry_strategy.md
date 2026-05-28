# 垂直行业 Registry 登记策略（BETA-AGENT-REGISTRY-01）

最后更新：2026-05-28

## 问题

`cad_capability_registry` 中 healthcare / hotel / industrial 等域行数很少；盲目新增 `claim_level: none` 行会**拉低表 C 主指标**。

## 策略

| 动作 | 何时做 |
| --- | --- |
| 新增 `none` 登记行 | 仅当需要跟踪「明确未实现」能力，且接受表 C 分母变大 |
| 直接 `showcase` writeback | 已有真实 CAD 证据 + table C gate pass |
| 只加 scene benchmark / agent 偏好 | 不改 registry；表 C 不变 |
| 扩 `micro_scene` / `project_sample` | 有脱敏样本 + CAD 证据后再 writeback |

## 当前建议

- Agent ~93% 通过 **scene benchmark + agents/** 配置推进，而非批量加 none 行。
- 表 C 已 99.68% 时，默认 **冻结 registry 行数**，新能力先走 `post-backlog.md` 的 VCAD / 样本包。

## 相关

- `docs/planning/post-backlog.md`
- `CORE_RESTRUCTURE_PLAN.md` Decision Gate G3/G4
