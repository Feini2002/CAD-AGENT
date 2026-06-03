## Context

`CAD_PLAN` already carries `drawing.layer`, `drawing.layer_role`, `drawing.semantic_layer`, and `drawing_standard_profile_id`. The current drawing standard profile resolves layer roles and text / dimension / hatch styles, but it does not model lineweight, linetype, color, inheritance, or plot-style evidence as first-class semantics.

The recent focused training for lineweight / linetype proves three sample lines can write and read back CAD properties. The missing Core capability is deciding style from drawing meaning, carrying that decision through `CAD_PLAN`, and reporting what was actually verified.

## Goals / Non-Goals

**Goals:**

- Represent lineweight / linetype / color decisions as semantic tokens, not hard-coded execution defaults.
- Extend `drawing_standard_profile` with style tokens that resolve to preview-safe CAD properties.
- Preserve semantic formal layers while still writing to `CODEX_PREVIEW` under preview-only policy.
- Add dry-run and execution-summary style evidence that can support training and future readback audits.
- Keep style verification separate from geometry verification and plot verification.

**Non-Goals:**

- Do not save or export a native DWG standards file.
- Do not implement CTB/STB plot verification in this change.
- Do not claim full construction-document style compliance.
- Do not replace the main `CORE_RESTRUCTURE_PLAN.md` or create a second backlog.

## Decisions

### Use style tokens instead of hard-coded line classes

The system will use profile-defined tokens such as `wall.cut.heavy_continuous`, `furniture.visible.medium`, `furniture.centerline.medium`, and `annotation.guide.thin_dashed`. These tokens are resolved by the drawing standard profile.

Alternatives considered:

- Hard-code three rules in execution: faster, but fails for furniture internals and project-specific standards.
- Full plot-style library first: more complete, but too heavy before the CAD plan contract exists.

### Store style resolution on the drawing object

`drawing.style_token` and `drawing.style_resolution` will carry semantic and resolved CAD style data. The resolution snapshot includes the source profile, layer role, semantic layer, resolved preview layer, lineweight, linetype, linetype scale, color policy, color, inheritance mode, and evidence boundary.

This keeps `CAD_PLAN` explainable while allowing execution to remain preview-only.

### Keep inherited style as the default

Style tokens default to `inheritance_mode=by_layer`. Explicit per-entity or per-primitive overrides are allowed only when represented as an explicit override with a semantic reason.

This matches CAD maintenance expectations: standard layers and block inheritance remain the normal path; entity overrides are evidence-bearing exceptions.

### Distinguish property, visual, and plot evidence

Reports will treat `style_verified` / CAD property evidence separately from `geometry_verified` and `plot_verified`.

Screenshots can support visual readability, but they do not prove `Lineweight`, `Linetype`, `Color`, CTB/STB mapping, or viewport-scaled plot output.

## Risks / Trade-offs

- **Risk: style tokens become another rigid standard** → Keep user seeds as defaults and allow project profiles to override token values.
- **Risk: preview-only layer hides semantic layer names** → Store both `semantic_layer` and `resolved_layer`.
- **Risk: users mistake style readback for plot correctness** → Add explicit `not_checked` boundaries for CTB/STB and plot output.
- **Risk: primitives without style still execute** → Add tests and dry-run reporting so missing style is visible before future formal acceptance.

## Migration Plan

1. Extend profile and plan schemas without breaking existing plans.
2. Add default style tokens to `codex_preview_beta`.
3. Add resolver functions and apply them through `apply_drawing_standard_to_plan`.
4. Include style evidence in dry-run and execution summaries.
5. Add regression tests for schema validation, token resolution, dry-run propagation, preview execution propagation, and evidence boundaries.

Rollback is straightforward: existing plans still rely on `drawing.layer`; style fields are additive.

## Open Questions

- Plot verification should be a later change once CTB/STB handling and layout viewport scale evidence are designed.
- Native DWG style asset export should stay behind the existing system asset sedimentation protocol and explicit CAD write approval.
