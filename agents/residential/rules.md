# residential Rules

## Scene Differences

- Prefer bed heads against solid walls where possible.
- Keep wardrobe doors or access paths clear.
- Respect kitchen operation flow among storage, washing, preparation, and cooking.
- Treat TV walls, sofa walls, entry cabinets, wardrobes, and kitchen elevations as common residential targets.
- Keep living and dining relationships legible before adding decorative detail.
- **产品块沙发改座数**：必须 **矢量重绘**（按座宽模块保留/删中格/平移拼接），**禁止**整块 X 向缩放冒充两座；原产品块不动，新几何只落 `CODEX_PREVIEW`。
- **块内 Polyline**：按 **3D** `(x,y,z)` 读点（`len(Coordinates)%3==0` 则 step=3）；禁止 step=2 误读（曾导致跨屏巨三角，见根目录 `TRAINING_ERRORS.md`）。
- **改座数裁切**：禁止「中心落中座就删整段」；跨三座线/弧须 **X 向裁掉中座带**，右座带 **左移一座宽**。
- **参照款沙发 plan**：必须先写 `visual_parts.json`，默认部件为左右扶手、N 个座垫、N 个靠垫、前底栏；每个部件应有 `id`、`role`、`shape`、`closed=true`。
- **参照款视觉禁令**：禁止 `closed_outer_shell`、`split_line_as_main_structure`、`fake_back_cushion_as_inner_line`；split 线不能冒充靠垫或靠背语义。
- **视觉优先取整**：三座改两座优先保留部件语言和开放总成，宽度按 2/3 取整到 5～10mm；不得用 probe 小数驱动圆角、靠垫或座背形状。

## Defaults

- Wardrobe access clearance preference: 600 mm.
- Preview layer: `CODEX_PREVIEW`.
- 训练截图：先置顶 AutoCAD → 按 `execution_summary` 自动 Zoom 到参考+预览（覆盖误拖视图）→ 只截 CAD 窗 → 你可立刻切回其它软件。

## Core Boundary

- Do not implement room recognition here.
- Do not implement object generation, collision checks, or circulation / zone-split algorithms here.
- Do not implement CAD_PLAN validation, dry-run, execution, readback, or verification here.
- Store only residential preferences and scene vocabulary.

## Preference → Core Mapping

Residential preferences steer Core circulation and object priority; Core performs zone split and placement.

| Preference | Core entry | Observable in `scene_alpha_benchmark` |
| --- | --- | --- |
| `circulation.main_aisle_width_mm` (900) | `path_generation.generate_circulation_candidates` | Narrower main aisle than office/restaurant |
| `circulation.secondary_aisle_width_mm` (750) | `basic_layout.create_layout_candidates` | Tighter secondary spacing in layout candidates |
| `circulation_strategy_weights.along_wall` (1.4) | `blank_shell_pipeline._select_circulation_for_zones` | `selected_circulation_strategy=along_wall` |
| `object_preferences` (cabinet first) | workflow `object_types` + block selector | sofa/table/shelf/cabinet/chair ordering |
| `preview_layer` | execution / CAD_PLAN policy | `CODEX_PREVIEW` only |

Workflow: `examples/workflows/blank_shell_residential_layout_loop.json` → case `scene_alpha_residential_blank_shell`.

## What Scene Alpha Does Not Claim

- Does not prove `geometry_verified` or residential project DWG accuracy.
- Does not implement along-wall geometry or zone splitting in `agents/`.
- Non-CAD benchmark pass is not a complete home-design automation brain.
