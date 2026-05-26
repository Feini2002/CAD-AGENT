# restaurant Rules

## Scene Differences

- Keep dining circulation readable.
- Keep service paths clear between kitchen, counter, and dining zones.
- Separate customer-facing and back-of-house intent when the brief provides enough information.
- Treat cashier, service counter, feature wall, and dining-zone elevations as possible targets.

## Defaults

- Preview layer: `CODEX_PREVIEW`.

## Core Boundary

- Do not implement dining layout algorithms here.
- Do not implement collision checks, circulation routing, or zone-split algorithms here.
- Do not implement kitchen code or compliance logic here without a dedicated future requirement.
- Do not implement CAD execution, readback, or verification here.
- Add only restaurant-specific preferences when needed.

## Preference → Core Mapping

Restaurant preferences bias service circulation and seating objects; Core runs the shared blank-shell pipeline.

| Preference | Core entry | Observable in `scene_alpha_benchmark` |
| --- | --- | --- |
| `circulation.main_aisle_width_mm` (1200) | `path_generation.generate_circulation_candidates` | Widest main aisle among Alpha trio |
| `circulation.secondary_aisle_width_mm` (950) | `basic_layout.create_layout_candidates` | Wider guest circulation spacing |
| `circulation_strategy_weights.l_spine` (1.35) | `blank_shell_pipeline._select_circulation_for_zones` | `selected_circulation_strategy=l_spine` |
| `object_preferences` (chair first) | workflow `object_types` + block selector | table/chair/counter emphasis |
| `preview_layer` | execution / CAD_PLAN policy | `CODEX_PREVIEW` only |

Workflow: `examples/workflows/blank_shell_restaurant_layout_loop.json` → case `scene_alpha_restaurant_blank_shell`.

## What Scene Alpha Does Not Claim

- Does not prove `geometry_verified` or F&B code compliance in CAD.
- Does not implement kitchen code, collision, or CAD execution in `agents/`.
- Benchmark pass documents preference-driven Core outputs only.

