# residential Rules

## Scene Differences

- Prefer bed heads against solid walls where possible.
- Keep wardrobe doors or access paths clear.
- Respect kitchen operation flow among storage, washing, preparation, and cooking.
- Treat TV walls, sofa walls, entry cabinets, wardrobes, and kitchen elevations as common residential targets.
- Keep living and dining relationships legible before adding decorative detail.

## Defaults

- Wardrobe access clearance preference: 600 mm.
- Preview layer: `CODEX_PREVIEW`.

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

