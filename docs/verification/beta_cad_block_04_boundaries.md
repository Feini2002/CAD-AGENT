# BETA-CAD-BLOCK-04 Drawing Standard Profile

最后更新：2026-05-26

> 后置主线：**真实 CAD 能力扩展** 第 4 小包。机器入口：`core/drawing_standard/drawing_standard_profile.py`、`libraries/drawing_standards/codex_preview_beta.json`。

## 目标

引入最小 **`drawing_standard_profile`**，把对象角色 / `layer_role` 映射到：

- **CAD 执行层**：`preview_only` 策略下统一解析为 `CODEX_PREVIEW`；
- **语义层**：`A-FURN`、`A-SHELL` 等正式图层名（仅 dry-run / 文档，不写入正式 DWG）；
- **样式**：`text_styles` / `dim_styles` / `hatch_styles` 最小字段集。

## 已交付

| 项 | 说明 |
| --- | --- |
| Schema | `drawing_standard_profile.schema.json`、`layer_preset.schema.json` |
| 库文件 | `libraries/drawing_standards/codex_preview_beta.json`、`libraries/layer_presets/codex_preview_beta.json` |
| 解析 | `resolve_layer_role`、`resolve_object_role`、`apply_drawing_standard_to_plan` |
| Beta suite | `drawing_standard_beta_suite.json`（6 cases）+ `run_drawing_standard_beta_suite.py` |
| 集成 | `block_alpha` dry-run 支持 `drawing_standard_profile_id`；`entity_level_evidence` 使用 profile 做 layer mapping |

## 行为摘要

| 模式 | `layer_role=furniture` | CAD 写入层 | 语义层 |
| --- | --- | --- | --- |
| `preview_only` | 是 | `CODEX_PREVIEW` | `A-FURN` |

## 不能声称什么

- **不是**正式项目图层 / 公司制图标准已落地。
- **不是**真实 CAD 已按 `A-FURN` 等正式层写入（preview 策略强制 `CODEX_PREVIEW`）。
- Beta suite **不等于** 用户 AutoCAD 会话实跑。

## 子校验

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_drawing_standard_profile tests.core.test_drawing_standard_beta_suite -v
& $py scripts/run_drawing_standard_beta_suite.py
```

## 下一小包

父包已收口：见 `beta_cad_block_acceptance.md`。
