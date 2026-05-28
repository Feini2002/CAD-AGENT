# residential Agent（家装 · 主训）

**训练状态：`primary_training`**（2026-05-28 方案 A）。其它场景见 `agents/AGENT_TRAINING_STATUS.md`。

轻量场景层：只存家装词汇、默认参数、偏好；执行与回读一律走 `core/`。

训练入口：`docs/training/residential-primary.md`。案例目录：`projects/residential_training_template/`（复制后用）。

## Scope

- Residential layout preferences.
- Common room relationships.
- Typical home interior objects and feature walls.

## Core Reuse Contract

- Use core for CAD IO, drawing parsing, model building, layout solving, CAD_PLAN validation, dry-run, execution, and verification.
- Do not duplicate core schemas or execution logic in this agent.
