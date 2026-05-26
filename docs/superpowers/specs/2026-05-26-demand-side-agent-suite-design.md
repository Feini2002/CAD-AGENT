# 需求侧多角色 Agent 套件设计

最后更新：2026-05-26

## 目标

建立一层数据驱动的需求侧角色 Agent，用真实用户口吻覆盖当前仓库已有场景，并把每条需求映射到 Core 能力、可执行 benchmark 和验证证据。它不直接绘图，不复制 Core 算法，只负责在开发期持续产生、记录和验收需求。

该层是临时需求脚手架：用于帮助开发 Core 理解多场景需求。对应能力验收完成后，可以删除角色表和需求侧表单，只保留最终沉淀到 Core / 场景轻量层的生成能力、理解能力和回归测试。

## 边界

- 角色 Agent 放在 `agents/demand_side/`，只使用 JSON / Markdown。
- 可复用加载、校验和 benchmark 分派能力放在 `core/demand_agents/` 和 `core/benchmarks/runner.py`。
- 需求 case 可以指向现有 `object_spec`、`composition_spec`、`blank_shell` 或后续扩展 pipeline。
- 默认只证明 non-CAD benchmark、validate、dry-run 和未验证状态；真实 CAD 几何准确仍必须通过 `CODEX_PREVIEW` 和 created handles readback。
- 需求侧 Agent 不能声明某个 Scene Product 已完成，只能暴露需求覆盖、能力缺口和当前证据。

## 第一版覆盖

第一版覆盖 6 个现有场景：

- `residential`
- `office`
- `restaurant`
- `commercial_fitout`
- `exhibition`
- `custom`

每个场景至少 2 个需求侧角色。第一批可跑需求 case 选择已有 Core 能力能表达的对象和组合，以便先跑通需求记录到 benchmark 的闭环。

## 数据流

```text
agents/demand_side/role_agents.json
-> examples/benchmarks/demand_side_agent_benchmark.json
-> core.demand_agents.loaders
-> core.benchmarks.runner demand_case pipeline
-> object_spec / composition_spec / blank_shell pipeline
-> benchmark_summary.json
```

## 验收

- 能加载并校验至少 12 个需求侧角色，且覆盖 6 个场景。
- 能加载并运行需求侧 benchmark suite。
- 每个 demand case 的结果中保留 `demand_agent_id`、`scene_id`、`request_text`、`core_capability_targets` 和被分派的底层 pipeline。
- 第一批 demand benchmark 全部通过 non-CAD gate，并清楚标记 `not_verified_without_cad_readback`。
