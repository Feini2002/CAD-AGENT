# commercial_fitout Scene Product Alpha — 范围（C-CFIT-01）

最后更新：2026-05-26

## 定位

`commercial_fitout` 是首个 **Scene Product Alpha** 试点场景，但仍保持 **轻量场景 Agent** 原则：只提供子场景范围、偏好、业务语义和确认边界；几何、布局求解、`CAD_PLAN`、CAD 执行与验证一律回到 Core。

机器可读范围见 `subscenes.json`（schema：`core/schemas/commercial_fitout_scope.schema.json`）。

## 首版三个子场景（仅此三个）

| subscene_id | 名称 | 典型对象（见 `capabilities/object_catalog.json`） |
| --- | --- | --- |
| `open_office` | 开放办公区 | 工位组、办公桌、办公椅、文件柜、打印区 |
| `meeting_room` | 会议室 | 会议桌、会议椅、边柜、AV 控制台 |
| `reception` | 前台接待 | 前台、等候沙发、形象墙、储物柜 |

子场景由项目 manifest、`scene_hint` 或用户触发词显式指定；**不得**静默把通用办公请求套成工装产品交付。

## 本阶段提供什么

- 子场景范围、触发词、典型对象清单（声明性，非 CAD 实现）。
- 场景偏好与 workflow 说明，供 Core Orchestrator / layout / object pipeline 读取。
- 通过 `no_scene` 默认 + 显式激活策略，避免未指定场景时自动工装化。

## 明确不提供什么（不得扩大声明）

- **完整施工图**、报建图、深化施工图包。
- 机电、结构、消防专册协调出图。
- 任意公司块库直写、无 metadata 的块插入。
- 无真实 CAD created handles readback 的 `geometry_verified`。
- 把 Scene Product Alpha 范围文档写成“工装 Agent 已产品化完成”。

## 与零售脚手架的关系

仓库中仍保留 `blank_store_to_layout`、`existing_plan_to_elevation` 等 **零售门店** workflow 文档，用于历史 scaffold 与 demand-side 压测；它们 **不在** Scene Product Alpha v1 三个子场景内，标记为 `deferred_legacy_workflows`，后续仅在 C 路线单独评估是否保留或迁移。

## Core 复用契约

```text
用户请求 / project manifest
-> Core Orchestrator（gate + scene activation）
-> commercial_fitout 子场景语义 + preferences
-> Core workflow（layout / object / CAD_PLAN / verification）
-> CODEX_PREVIEW（仅在有 allow_cad 与真实 smoke 证据时）
```

不得在 `agents/commercial_fitout/` 内实现 CAD 执行、回读、碰撞或布局算法；边界扫描见 `core/agents/scene_boundary_scan.py` 与 `tests/agents/test_scene_agent_boundaries.py`。

## 对象 catalog（C-CFIT-02）

- Fixture：`capabilities/object_catalog.json`
- Core 入口：`core/agents/commercial_fitout_catalog.py`（`catalog_entry_to_object_specs` / `object_specs_for_subscene`）

## 块映射（C-CFIT-03）

- Fixture：`capabilities/block_mapping.json` + `libraries/blocks/commercial_fitout_block_library.json`
- Core：`core/agents/commercial_fitout_block_mapping.py`（`resolve_catalog_object_render`；禁止任意块名）

## 微场景 benchmark（C-CFIT-04）

- Suite：`examples/benchmarks/commercial_fitout_micro_scene_benchmark.json`
- 脚本：`scripts/run_commercial_fitout_micro_scene_benchmark.py`

## 下一包

- `C-CFIT-05-SAMPLE-PROJECT-CONFIRMATION`：已完成（`projects/commercial_fitout_sample` + `commercial_fitout_sample_confirmation_bundle`）。
- `C-CFIT-06-REAL-CAD-SMOKE`：已完成（`run_commercial_fitout_cad_smoke.py`；样本范围 readback verified；非完整工装产品）。
- `C-CFIT-07-PRODUCT-BOUNDARY-ROLLUP`：已完成（`capabilities/product_alpha_boundary.json`；见 `docs/verification/commercial_fitout_product_alpha_boundaries.md`）。
