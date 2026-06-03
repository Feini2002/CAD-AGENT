## Context

The current system already has system asset sedimentation, cross-DWG copy, UTF-8 preflight in sedimentation, and a line-type table generator with several report fields. The missing layer is a shared semantic contract that explains why a request should use assets, which asset is safe to reuse, and which CAD layout checks must be proven by readback rather than by generator declarations.

## Design

### Semantic rules

Create `core.assets.semantic_rules` as a small executable rule catalog. Each rule records:

- `ruleId`
- request triggers and aliases
- required route
- required guards
- forbidden behavior
- validation hooks
- evidence boundary

The module also exposes helpers for:

- matching rules to a user phrase,
- auditing system asset registry text for mojibake before reuse,
- explaining weak/strong semantic asset signals.

### Asset reuse hardening

`core.assets.system_asset_reuse` will call the registry encoding preflight before matching. If registry text is corrupt, the workflow returns `asset_registry_encoding_failed` and no ready plans.

Candidate ranking remains score-based but becomes stable by adding tie-breakers:

- score,
- lifecycle status,
- native DWG availability,
- precise reusable source readiness,
- asset id.

Weak matches are reported as candidates but do not become ready reuse plans. Current business DWG remains protected: reuse writes only to `CODEX_PREVIEW` and reports `savedCurrentDwg=false`.

### Line-type table audit

Create `core.training.linetype_table_audit` so layout checks are not only self-reported by the drawer. The audit consumes the generated report and a readback snapshot. It checks:

- canonical Chinese text exists and mojibake does not,
- no hatch/solid/wipeout/fill objects exist,
- sample handles are read back,
- every sample bbox stays inside its row sample cell,
- row height covers sample vertical needs plus margins,
- style readback covers multiple colors, lineweights, linetypes, and BYLAYER,
- screenshot/plot evidence is not overstated.

`draw_linetype_table` records this audit and fails the report if the audit fails.

### Variable row support

`draw_linetype_table` accepts optional rows. The default remains the full 42-row training table, but tests can generate 17/73-row layouts to prove the layout is not hard-coded to one row count.

## Verification

- Targeted unit tests for asset reuse and line-type audits.
- CLI plan-only JSON smoke for asset reuse remains strict JSON.
- OpenSpec validation.
- Existing UTF-8, sedimentation, and line-type table tests continue passing.
