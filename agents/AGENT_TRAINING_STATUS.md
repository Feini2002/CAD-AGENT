# 场景 Agent 训练状态

最后更新：2026-06-01（CAD Designer Agent 成长路径）

总训练对象：`cad_designer/`。它统筹成长阶段、基础课程和多 Agent 调用；场景 Agent 仍只提供场景词汇、规则和偏好。

| 场景目录 | 训练状态 | 说明 |
| --- | --- | --- |
| `cad_designer/` | **primary_training** | 总设计师 Agent；第一阶段目标为电子设计师雏形，第一批课程从 CAD 基础操作开始 |
| `residential/` | active_scene_plugin | 当前主场景插件；改 rules/preferences + 案例 feedback |
| `commercial_fitout/` | paused | 已有 scaffold；等家装 3+ 案例稳定后再开 |
| `office/` | paused | Alpha 基线保留 |
| `restaurant/` | paused | Beta 基线保留 |
| `exhibition/` | paused | Beta benchmark 已存在，不并行训 |
| `healthcare/` | paused | 同上 |
| `custom/` | paused | 占位 |

**paused** = 不删目录、不接新训练案例；修 Core 回归或用户明确要求时再动。

训练入口：`docs/training/cad-designer-growth-path.md` 与 `docs/training/README.md`。
