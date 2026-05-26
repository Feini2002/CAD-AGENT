# office Rules

## Scene Differences

- Keep workstation areas readable and repeatable.
- Prefer meeting rooms near shared or public zones when the brief allows.
- Keep reception, circulation, and storage relationships clear.

## Defaults

- Preview layer: `CODEX_PREVIEW`.

## Core Boundary

- Do not implement workstation layout algorithms here.
- Do not implement collision checks here.
- Do not implement CAD execution or verification here.
- Add only office-specific preferences when needed.

## Preference → Core Mapping

Office preferences only steer Core; they do not run layout or CAD locally.

| Preference | Core entry | Observable in `scene_alpha_benchmark` |
| --- | --- | --- |
| `circulation.main_aisle_width_mm` (1100) | `path_generation.generate_circulation_candidates` | Wider main aisle strip vs residential/restaurant |
| `circulation.secondary_aisle_width_mm` (850) | `basic_layout.create_layout_candidates` | Object spacing in layout candidates |
| `circulation_strategy_weights.straight_spine` (1.35) | `blank_shell_pipeline._select_circulation_for_zones` | `selected_circulation_strategy=straight_spine` |
| `object_preferences` (table first) | workflow `object_types` + block selector | Plans emphasize desk/table/chair/cabinet mix |
| `preview_layer` | execution / CAD_PLAN policy | Draws target `CODEX_PREVIEW` only |

Workflow: `examples/workflows/blank_shell_office_layout_loop.json` → `examples/benchmarks/scene_alpha_benchmark.json` case `scene_alpha_office_blank_shell`.

## What Scene Alpha Does Not Claim

- Does not prove `geometry_verified` or real-project CAD accuracy.
- Does not implement blank-shell pipeline, collision, or block library logic in `agents/`.
- `benchmark_pass_non_cad` only shows preferences changed Core outputs on the same pipeline class.

