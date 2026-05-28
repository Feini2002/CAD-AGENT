# 场景 Agent 训练状态

最后更新：2026-05-28（方案 A：家装主训）

| 场景目录 | 训练状态 | 说明 |
| --- | --- | --- |
| `residential/` | **primary_training** | 唯一默认扩面；改 rules/preferences + 案例 feedback |
| `commercial_fitout/` | paused | 已有 scaffold；等家装 3+ 案例稳定后再开 |
| `office/` | paused | Alpha 基线保留 |
| `restaurant/` | paused | Beta 基线保留 |
| `exhibition/` | paused | Beta benchmark 已存在，不并行训 |
| `healthcare/` | paused | 同上 |
| `custom/` | paused | 占位 |

**paused** = 不删目录、不接新训练案例；修 Core 回归或用户明确要求时再动。

训练入口：`docs/training/README.md`。
