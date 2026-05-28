# round12 style compare

Case: `residential_sofa_2seat_20260528`

Inputs:
- `runs/round12_visual_parts.json`
- `expected/style_target_reference_crop.png`
- reference block `5S03232` / handle `4A2`
- preview screenshot `runs/round12_preview.png`
- machine audit `runs/round12_geometry_audit.json`
- agent review `runs/round12_agent_review.json`

## Component Compare

| part_id | role | expected shape | round12 result |
| --- | --- | --- | --- |
| `arm_left` | arm | `rounded_rect` | pass; 8 preview handles |
| `arm_right` | arm | `rounded_rect` | pass; 8 preview handles |
| `seat_left` | seat_cushion | `pill_horizontal` | pass; 8 preview handles |
| `seat_right` | seat_cushion | `pill_horizontal` | pass; 8 preview handles |
| `back_left` | back_cushion | `rounded_rect_tall` | pass; 8 preview handles |
| `back_right` | back_cushion | `rounded_rect_tall` | pass; 8 preview handles |
| `base_rail` | front_rail | `rounded_rect_wide` | pass; 8 preview handles |

## Visual Gates

- [x] 7/7 required parts are declared by `round12_visual_parts.json`.
- [x] 7/7 required parts have created CAD preview handles.
- [x] Machine audit reports `audit_pass=true`.
- [x] Machine audit reports no `closed_outer_shell`, `split_as_backrest`, or `missing_required_parts` hit.
- [x] `expected/style_target_reference_crop.png` exists and is derived from the real AutoCAD screenshot, not generated art.
- [x] `round12_preview.png` shows an open two-seat sofa: two side arms, two thin seat cushions, two tall back cushions, and a base rail.
- [x] `round12_agent_review.json` allows delivery only after machine audit and visual self-review both pass.

## Notes

This compare file records the round12 Visual-First gate result. It is not a substitute for the user's visual acceptance.
