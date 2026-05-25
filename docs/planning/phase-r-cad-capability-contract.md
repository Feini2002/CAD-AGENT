# Phase R CAD Capability Contract

状态：能力契约计划已细化  
最后同步：2026-05-26

> 本文是 Phase R 的能力契约辅助文档，不是独立 PlanMD。它只把已有 Phase W baseline 和 CAD capability probe 转成可执行契约；是否进入实现、优先级和退出标准以 `CORE_RESTRUCTURE_PLAN.md` 为准，且本文不声称新增 CAD 能力已经实现。

## 总原则

- 只有真实 CAD created handles 范围内的 readback 可以证明几何准确。
- 截图只能作为视觉辅助。
- `cad_capability_verified` 证明基础图元探针可用，不证明 block insertion 已通过。
- 新实体类型如果本轮没有真实 CAD readback，必须进入 `deferred_verification`。
- 所有真实 CAD 写入仍默认只允许 `CODEX_PREVIEW`。

## 实体契约矩阵

| entity | intents | write_fields | readback_fields | tolerance | failure_classes | evidence_state |
| --- | --- | --- | --- | --- | --- | --- |
| `line` | `draw_line` / primitive CAD_PLAN intent | `start_point`、`end_point`、`layer`、`color?` | `handle`、`type`、`start_point`、`end_point`、`layer` | 端点和长度 `<=1mm` | `write_failed`、`handle_missing`、`readback_missing`、`geometry_mismatch`、`layer_mismatch` | 已有 probe，需契约化 |
| `rectangle` | `draw_rectangle` / current `draw_object` fallback | `corner1`、`corner2`、`bbox`、`layer` | `handles`、`type_counts`、`bbox`、`layer` | bbox 宽高和基点 `<=1mm` | `partial_handles`、`bbox_mismatch`、`base_point_mismatch`、`layer_mismatch` | Phase W baseline 已 `geometry_verified` |
| `circle` | `draw_circle` | `center`、`radius`、`layer` | `handle`、`type`、`center`、`radius`、`bbox`、`layer` | 中心和半径 `<=1mm` | `radius_mismatch`、`center_mismatch`、`bbox_mismatch` | 已有 probe，需契约化 |
| `arc` | `draw_arc` | `center`、`radius`、`start_angle`、`end_angle`、`layer` | `handle`、`type`、`center`、`radius`、`start_angle`、`end_angle`、`bbox`、`layer` | 半径和中心 `<=1mm`，角度 `<=0.5deg` | `angle_mismatch`、`direction_mismatch`、`radius_mismatch` | 已有 probe，方向语义需补强 |
| `polyline` | `draw_polyline` | `points`、`closed`、`layer` | `handle`、`type`、`points`、`closed`、`bbox`、`layer` | 点坐标 `<=1mm` | `point_count_mismatch`、`closed_mismatch`、`bbox_mismatch` | 已有闭合 polyline probe |
| `text` | `draw_text` | `text`、`position`、`height`、`rotation?`、`style?`、`layer` | `handle`、`type`、`text`、`position`、`height?`、`rotation?`、`style?`、`layer` | 位置 `<=1mm`，内容精确匹配 | `text_mismatch`、`position_mismatch`、`style_unverified` | 内容和位置基础回读已有，style 暂缓 |
| `dimension` | `add_dimension` | `start_point`、`end_point`、`text_position`、`textheight?`、`layer` | `handle`、`type`、`text?`、`bbox?`、`layer` | 数量精确，位置 / bbox `<=2mm` | `dimension_count_mismatch`、`dimension_position_unverified`、`style_unverified` | 数量 probe 已有，标注样式 deferred |
| `block_reference` | `insert_block_alpha` | `block_id`、`cad_identity.block_name`、`base_point`、`rotation`、`scale`、`layer`、`attributes?` | `handle`、`type`、`block_name`、`insertion_point`、`rotation`、`scale`、`layer`、`bbox`、`attributes?` | 插入点 `<=1mm`，旋转 `<=0.5deg`，bbox `<=2mm` | `definition_missing`、`insert_failed`、`block_name_mismatch`、`anchor_mismatch`、`rotation_mismatch`、`attribute_unverified` | 当前未验证，Phase R alpha 目标 |

## `insert_block_alpha` 最小 intent 草案

第一轮不要把 CAD_PLAN 扩成任意 CAD DSL。建议只引入受控块插入 intent：

```json
{
  "intent": "insert_block_alpha",
  "object": {
    "type": "block_reference",
    "name": "Controlled Test Block",
    "block_id": "controlled-test-block-001",
    "cad_identity": {
      "block_name": "CODEX_TEST_BLOCK_001"
    }
  },
  "placement": {
    "mode": "absolute",
    "base_point": [0, 0, 0],
    "rotation": 0,
    "scale": [1, 1, 1]
  },
  "drawing": {
    "layer": "CODEX_PREVIEW"
  },
  "confidence": 1.0,
  "needs_confirmation": false
}
```

## Block Alpha 验收路径

| 步骤 | 内容 | 通过条件 |
| --- | --- | --- |
| 1 | 仓库内定义受控测试块 metadata | 不依赖外部 DWG 或真实公司块库 |
| 2 | dry-run 校验 intent | bbox、anchor、rotation、layer role 合法 |
| 3 | 真实 CAD 插入到 `CODEX_PREVIEW` | 记录非空 `created_handles` |
| 4 | 按 handles 定向 readback | 不扫描全 ModelSpace，不混入旧实体 |
| 5 | 验证 block reference 字段 | block name、插入点、旋转、缩放、图层、bbox 全部通过 |
| 6 | 写 verification report | `evidence_state=readback_geometry_verified` 才能声称 alpha 通过 |

验收报告必须含：

- `status`
- `failure_category`
- `intent`
- `expected`
- `actual`
- `created_handles`
- `checks`
- `evidence_state`
- `geometry_accuracy`
- `screenshot_role`
- `limitations`
- `deferred_verification`
- `safety`

## Deferred Verification

以下内容必须暂缓，不能随 block insertion alpha 一起声称完成：

- 真实公司块库路径、真实块名映射和批量块库准确性。
- 属性块 attribute definition / attribute reference 的创建、填写、回读和样式。
- hatch、填充、图案比例和 hatch 边界回读。
- dim style、text style、layer preset 的完整制图标准准确性。
- 任意角度 block bbox 的精确几何包络；alpha 只建议支持 `0/90/180/270` 或明确近似。
- 非统一 scale、镜像、动态块、嵌套块、匿名块。
- 任意 CAD_PLAN、真实项目图纸、正式图层落图。
- 自动 DWG/PDF 识别后的块语义匹配。

## 实现参考项（以主计划为准）

| 编号 | 任务 |
| --- | --- |
| R-CAD-01 | 将本文契约映射到现有 `cad_capability_probe` 和 `verification_report` 字段。 |
| R-CAD-02 | 为基础图元补 schema / dry-run / fake readback 回归测试。 |
| R-CAD-03 | 设计 `insert_block_alpha` 的 CAD_PLAN schema 最小扩展。 |
| R-CAD-04 | 为受控测试块定义 metadata、fallback symbol 和 readback expectation。 |
| R-CAD-05 | 扩展真实 CAD driver 的 block insertion 接口，但默认只写 `CODEX_PREVIEW`。 |
| R-CAD-06 | 扩展 readback 标准化，识别 `block_reference` 并输出 block fields。 |
| R-CAD-07 | 在 CAD validation runner 中新增 block alpha step 和硬门禁。 |
| R-CAD-08 | 追加真实 CAD evidence 文档，明确有限样本和不可扩大边界。 |

## 本文不能声称

本文不能声称 block insertion 已完成，不能声称真实块库可用，不能声称属性块、hatch 或样式标准已验证，不能声称任意 CAD_PLAN 准确，也不能把截图、dry-run 或 no-CAD benchmark 当作几何准确证据。
