## ADDED Requirements

### Requirement: CAD plans carry semantic style intent

The system SHALL allow a CAD plan drawing object to carry a semantic style token and resolved style metadata for lineweight, linetype, color policy, inheritance, and layer role.

#### Scenario: Style token is resolved into plan drawing metadata
- **WHEN** a plan with `drawing.style_token` is passed through the drawing standard profile resolver
- **THEN** the plan drawing metadata includes `style_resolution` with the source profile, style token, layer role, semantic layer, resolved layer, lineweight, linetype, linetype scale, color policy, color, inheritance mode, and checked / not_checked evidence boundary

### Requirement: Drawing standards define reusable style tokens

The system SHALL define style tokens in drawing standard profiles rather than hard-coding lineweight, linetype, or color in CAD execution paths.

#### Scenario: User seed line styles exist in the default profile
- **WHEN** the default drawing standard profile is loaded
- **THEN** it defines tokens for heavy wall continuous line, medium furniture visible line, medium centerline, thin furniture detail, hidden edge, and thin dashed annotation / guide line

### Requirement: Style evidence is separated from geometry and plot evidence

The system SHALL report CAD style evidence separately from geometry verification and plot verification.

#### Scenario: Dry-run reports style evidence without claiming plot verification
- **WHEN** a styled CAD plan dry-run report is created
- **THEN** the report includes expected style metadata and states that CTB/STB plot output is not checked unless a plot verification path ran

### Requirement: Preview-only execution preserves semantic style resolution

The system SHALL keep preview-only CAD execution on `CODEX_PREVIEW` while preserving semantic layer and style resolution in summaries.

#### Scenario: Preview execution writes only preview layer but reports style intent
- **WHEN** a styled plan is executed in preview-only mode
- **THEN** the execution summary uses `CODEX_PREVIEW` as the CAD layer and includes the semantic layer plus expected style metadata for the created handles

### Requirement: Entity style overrides are explicit and auditable

The system SHALL represent entity or primitive style overrides as explicit semantic overrides rather than silent CAD property changes.

#### Scenario: Glyph primitive carries a part-specific style token
- **WHEN** a glyph primitive defines its own `style_token`
- **THEN** dry-run and execution evidence identify that primitive style separately from the object default style
