## Why

The current lineweight / linetype training proves a small sample can write and read back CAD properties, but it does not give the Core a reusable way to understand when a wall, furniture outline, furniture detail, centerline, hidden edge, annotation, or plot color should use different style semantics.

This change turns lineweight, linetype, and color from ad-hoc drawing parameters into a CAD style semantics contract that can be planned, resolved, executed, audited, and honestly reported.

## What Changes

- Introduce a style-token contract for CAD plans, starting from the user seed examples: heavy wall continuous line, medium furniture visible line, centerline, and thin dashed annotation / guide line.
- Extend drawing standard profiles so semantic tokens resolve to layer role, semantic layer, preview-safe CAD layer, lineweight, linetype, linetype scale, color policy, and inheritance policy.
- Add dry-run and execution-summary evidence so style intent and style resolution are visible before and after CAD execution.
- Add readback-oriented audit vocabulary for style verification, separate from geometry verification and plot verification.
- Keep preview-only safety: execution remains on `CODEX_PREVIEW` unless formal-layer writes are explicitly approved.
- State evidence boundaries: CAD property readback can prove written entity properties, while screenshots and model-space views do not prove CTB/STB or plotted PDF output.

## Capabilities

### New Capabilities

- `cad-style-semantics`: Defines how CAD style semantics for lineweight, linetype, color, layer role, inheritance, and checked / not_checked evidence are expressed and verified.

### Modified Capabilities

- None. No stable OpenSpec specs currently exist for this area.

## Impact

- Affected schemas: `core/schemas/drawing_standard_profile.schema.json`, `core/schemas/cad_plan.schema.json`, and the mirrored `schemas/cad_plan.schema.json`.
- Affected profile data: `libraries/drawing_standards/codex_preview_beta.json` and `libraries/layer_presets/codex_preview_beta.json`.
- Affected Core modules: `core/drawing_standard/drawing_standard_profile.py`, CAD dry-run helpers, preview execution summaries, and style-oriented tests.
- Affected training / evidence: lineweight-linetype training can evolve from a three-line sample into a semantic style profile without claiming plot verification or full construction-document competence.
- No dependency changes and no native DWG save / overwrite / formal layer write are part of this change.
