# Phase R Block Library Roadmap

状态：图块库与制图标准路线已细化  
最后同步：2026-05-26

> 本文是 Phase R 的图块库路线辅助文档，不是独立 PlanMD。它定义从 `symbol_2d fallback` 走向受控 block insertion alpha 的候选路线；是否进入实现、优先级和退出标准以 `CORE_RESTRUCTURE_PLAN.md` 为准。本文不接真实公司块库，不声称当前 schema、CAD_PLAN 或 CAD driver 已支持真实块插入。

## 字段矩阵

### `BLOCK_LIBRARY`

| 字段 | 必要性 | 归属 | 用途 |
| --- | --- | --- | --- |
| `schema_version` / `library_id` / `units` | 必须 | `libraries/blocks` + `core/schemas` | 明确版本和单位 |
| `block_id` / `block_version` / `name` / `category` / `domain` / `tags` | 必须 | `libraries/blocks` | 查询、筛选、版本追踪 |
| `source.type` / `source.path` / `source.status` | 必须 | `libraries/blocks` | 区分受控测试块、公司块库 deferred、生成符号 |
| `cad_identity.block_name` / `definition_name` / `expected_entity_type` | 必须 | `core/block_engine` schema | 真实 CAD 插入和 readback 对齐 |
| `size.width/depth/height` / `footprint_2d` | 必须 | `libraries/blocks` | 布置 bbox、碰撞、落图预期 |
| `anchor_points` | 必须 | `libraries/blocks` | 插入点、对齐点、靠墙点 |
| `connection_points` | 推荐 | `libraries/blocks` | 桌椅、柜门、设备接口等对象组合 |
| `clearance_zones` | 必须 | `libraries/blocks` | 椅后、柜前、开门、通道避让 |
| `symbol_2d` | 必须 | `libraries/blocks` | 无真实块时的受控 fallback |
| `attributes` | 第二阶段必须 | `libraries/blocks` | 属性块 tag、默认值、是否必填 |
| `layer_bindings` / `style_bindings` | 必须 | `libraries/blocks` + drawing standard | 块内部 / 插入层、文字、标注、填充标准绑定 |
| `validation.status` / `readback_fields` / `tolerance_mm` | 必须 | `core/block_engine` + verification | 区分 metadata-only、symbol fallback、真实插入已验证 |

### `OBJECT_SPEC`

| 字段 | 必要性 | 归属 | 用途 |
| --- | --- | --- | --- |
| `object_id` / `type` / `name` / `domain` | 必须 | `core/object_engine` + `libraries/objects` | 业务对象语义 |
| `size.width/depth/height` | 必须 | `libraries/objects` | 与 block footprint 和 CAD_PLAN 尺寸对齐 |
| `semantic_role` | 推荐 | `libraries/objects` | 如 `workstation`、`storage`、`seating` |
| `components` | 必须 | `libraries/objects` | 对象组成解释，不等于 CAD 实体 |
| `placement_requirements` | 必须 | `core/layout_engine` 消费 | 靠墙、通道、拉椅、柜前净空 |
| `clearance_requirements` | 必须 | `core/layout_engine` 消费 | 从对象语义生成 clearance bbox |
| `preferred_block_refs` | 推荐 | `core/block_engine` 消费 | 指向候选块，不把块细节塞进场景 agent |
| `fallback_symbol_ref` | 必须 | `core/block_engine` 消费 | 无真实块时转 `symbol_2d` |
| `default_layer_role` / `style_profile_id` | 必须 | drawing standard 消费 | 图层 / 样式解析 |
| `validation_expectations` | 推荐 | verification 消费 | 预期 bbox、对象数量、允许误差 |

### `drawing_standard_profile`

| 字段 | 必要性 | 归属 | 用途 |
| --- | --- | --- | --- |
| `profile_id` / `schema_version` / `units` / `domain` | 必须 | `libraries/drawing_standards` | 制图标准入口 |
| `layer_preset_id` / `layers` | 必须 | `libraries/layer_presets` | role 到 CAD layer 的映射 |
| `text_styles` | 必须 | `libraries/drawing_standards` | 标签、说明、房间名 |
| `dim_styles` | 必须 | `libraries/drawing_standards` | 尺寸样式、箭头、文字高度 |
| `hatch_styles` | 推荐 | `libraries/drawing_standards` | 墙体、不可放置区、净空区 |
| `lineweights` / `colors` / `linetypes` | 推荐 | `libraries/drawing_standards` | 输出一致性 |
| `object_role_bindings` | 必须 | Core 消费 | `furniture -> A-FURN`、`clearance -> A-CLEAR` |
| `block_layer_policy` | 必须 | `core/block_engine` + safety | 插入层、块内层、是否允许正式层 |
| `verification_policy` | 必须 | verification | 必须 readback 的字段和截图角色声明 |

## 最小制图标准

### Layer Preset

| role | 默认 layer | 说明 |
| --- | --- | --- |
| `preview` | `CODEX_PREVIEW` | 默认所有真实 CAD 测试只写这里 |
| `shell` | `A-SHELL` | 外壳、边界、房间框 |
| `wall` | `A-WALL` | 墙体或隔断 |
| `door_window` | `A-DOOR-WIND` | 门窗洞口 |
| `furniture` | `A-FURN` | 桌椅柜等对象 |
| `block` | `A-BLOCK` | 真实块插入的标准目标层，预览时仍解析到 `CODEX_PREVIEW` |
| `clearance` | `A-CLEAR` | 椅后、柜前、门扇、不可占用净空 |
| `circulation` | `A-PATH` | 主通道、次通道 |
| `annotation` | `A-ANNO` | 文字说明 |
| `dimension` | `A-DIMS` | 尺寸标注 |
| `hatch` | `A-HATCH` | 填充表达 |

### Text / Dim / Hatch Style

| 类型 | style | 用途 | 最小字段 |
| --- | --- | --- | --- |
| text | `CAD_LABEL` | 对象标签 | `font`、`height_mm`、`width_factor`、`rotation_policy` |
| text | `CAD_ROOM_NAME` | 空间名 | `font`、`height_mm`、`align` |
| text | `CAD_NOTE` | 说明文字 | `font`、`height_mm`、`line_spacing` |
| dim | `CAD_DIM_MM` | 默认毫米标注 | `text_height_mm`、`arrow_size_mm`、`precision`、`unit_suffix`、`offset_mm` |
| dim | `CAD_DIM_SMALL` | 小对象局部尺寸 | `text_height_mm`、`arrow_size_mm`、`precision` |
| hatch | `HATCH_CLEARANCE` | 净空区 | `pattern`、`scale`、`angle`、`transparency` |
| hatch | `HATCH_NO_PLACE` | 不可放置区 | `pattern`、`scale`、`color` |
| hatch | `HATCH_WALL_SOLID` | 墙体表达 | `pattern`、`scale`、`color` |

## 迁移步骤

1. 保留当前 `symbol_2d` fallback 为基线，不改变现有参数化对象链路。
2. 在 `libraries/blocks` 新增受控测试块 metadata，只使用自造、极小、可重复的测试块。
3. 扩展 `BLOCK_LIBRARY` schema：补 `units`、`source`、`cad_identity`、`anchor_points`、`footprint_2d`、`clearance_zones`、`layer_bindings`、`validation`。
4. 扩展 `OBJECT_SPEC`：允许对象引用 `preferred_block_refs`，但仍能 fallback 到 `symbol_2d`。
5. 增加 CAD_PLAN block insertion intent：字段覆盖 `block_id`、`block_name`、`base_point`、`rotation`、`scale`、`layer_role`、`attributes`。
6. dry-run 阶段先只验证 bbox、layer role、anchor、rotation、clearance，不触碰 CAD。
7. 真实 CAD 阶段只在 `CODEX_PREVIEW` 插入受控测试块，记录 `created_handles`。
8. readback 验证 block name、插入点、旋转、缩放、图层、属性、bbox。
9. 通过后才把该测试块标为 `readback_geometry_verified`。
10. 再推进属性块、hatch、正式 `drawing_standard_profile`。
11. 真实公司块库最后接入，且只做 metadata 映射，不进入 `agents/<scenario>`。

## 接口归属

| 接口 | 归属 | 不应归属 |
| --- | --- | --- |
| block metadata schema | `core/schemas/block_library.schema.json` | `agents/<scenario>` |
| block metadata 实例 | `libraries/blocks` | `projects` 或场景 agent |
| block 查询、筛选、fallback、插入意图 | `core/block_engine` | `core/layout_engine` |
| 对象语义、默认尺寸、组件 | `libraries/objects` + `core/object_engine` | block metadata |
| 空间布置、bbox、碰撞、clearance 消费 | `core/layout_engine` | block library |
| layer/text/dim/hatch 标准 | `libraries/drawing_standards`、`libraries/layer_presets` | scene preferences |
| role 到 layer/style 解析 | `core/style_engine` 或后续 `core/drawing_standard_engine` | CAD driver |
| CAD_PLAN 最终落图指令 | `core/plan_engine` | scene agent |
| 真实 CAD 插入执行 | `core/cad_io` / execution driver | block metadata |
| readback 与验证报告 | `core/verification` | screenshot 或 benchmark summary |
| 业务对象组合偏好 | `agents/<scenario>` | schema、CAD 执行、真实块路径 |

## 实现参考项（以主计划为准）

| 编号 | 任务 | 交付物 |
| --- | --- | --- |
| R-BLOCK-01 | 定义 `BLOCK_LIBRARY v0.2` 字段矩阵和兼容策略 | schema 草案、旧 `0.1` 示例迁移说明 |
| R-BLOCK-02 | 定义 `OBJECT_SPEC` 到 block reference 的语义接口 | `preferred_block_refs`、`fallback_symbol_ref`、`clearance_requirements` 设计 |
| R-BLOCK-03 | 建立 `drawing_standard_profile` 最小模型 | layer / text / dim / hatch profile 草案 |
| R-BLOCK-04 | 创建受控测试块路线，而非真实公司块库接入 | 测试块 metadata 规范、命名、验证字段 |
| R-BLOCK-05 | 设计 CAD_PLAN block insertion intent | CAD_PLAN 字段、dry-run 预期、错误分类 |
| R-BLOCK-06 | 设计 block insertion readback 报告 | block name、handle、base point、rotation、scale、layer、attributes、bbox |
| R-BLOCK-07 | 增加对象级 block benchmark 规划 | desk / chair / cabinet / test_block 的 non-CAD 与 CAD deferred 验证状态 |
| R-BLOCK-08 | 明确接口归属和禁止项 | Interface Ownership Map |

## 本文不能声称

本文不能声称 schema 已修改、测试块已创建、CAD_PLAN 已支持真实块插入、真实 CAD block insertion 已通过、属性块或 hatch 已验证、公司块库已接入、截图或 dry-run 可证明几何准确。
