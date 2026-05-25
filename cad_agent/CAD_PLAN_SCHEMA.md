# legacy: CAD_PLAN 第一版说明

本文件是旧说明入口。机器可校验的权威 schema 位于：

- `core/schemas/cad_plan.schema.json`
- `core/schemas/*.schema.json`

高层模型边界说明见：

- `docs/architecture/cad_plan_boundary.md`
- `core/schemas/README.md`

以下旧说明仅作为历史兼容记录。

`CAD_PLAN` 是用户白话和 CAD 绘制脚本之间的中间层。

## 最小结构

```json
{
  "version": "0.1",
  "domain": "generic",
  "intent": "draw_object",
  "object": {
    "type": "cabinet",
    "name": "测试柜",
    "width": 1800,
    "depth": 600
  },
  "placement": {
    "mode": "absolute",
    "base_point": [0, 0, 0]
  },
  "drawing": {
    "layer": "CODEX_PREVIEW",
    "include_label": true,
    "include_dimensions": true
  },
  "confidence": 1.0,
  "needs_confirmation": false
}
```

## 字段解释

- `version`：CAD_PLAN 版本。
- `domain`：项目类型，如 `generic`、`residential`、`retail`、`office`、`restaurant`、`exhibition`、`hotel`、`education`、`healthcare`、`industrial`、`custom`。
- `intent`：动作类型，如 `draw_object`、`draw_annotation`、`modify_object`。
- `object`：要画的对象。
- `placement`：放置方式和位置。
- `drawing`：图层、标注、文字等绘图设置。
- `confidence`：Codex 对计划准确性的信心。
- `needs_confirmation`：是否需要用户确认后才能执行。

## 第一版只支持

- 矩形类对象。
- 文字标签。
- 简单线性尺寸。
- 绝对坐标放置。

后续再支持房间边界、相对墙体、门窗识别、对象组追踪。

具体项目的空间名称、图层、坐标、单位校准应放在项目级 `cad_context.json` 中，不应写死在本通用 Schema 说明里。
