## ADDED Requirements

### Requirement: Asset sedimentation is governed before library mutation

The system SHALL route explicit system asset sedimentation requests through an asset library governor before mutating system-library contracts, registry entries, or native asset DWG plans.

#### Scenario: Explicit sedimentation request

- **WHEN** a user asks to "沉淀", "通用资产", or "收进资产库"
- **THEN** the system produces an asset-governance decision with selected responsibilities, required guards, allowed child agents, source-boundary status, and evidence boundaries before treating the asset as reusable

#### Scenario: Source boundary is incomplete

- **WHEN** the governor cannot identify selected handles, created handles, active DWG handles, explicit bbox, named block, or style definition
- **THEN** the system marks the asset as metadata-only or review-quarantine and MUST NOT place it in the clean reusable source area

### Requirement: Asset library DWG layout is partitioned and auditable

The system SHALL represent native asset DWG layout plans with named library zones, stable slots, bbox plans, copy-source plans, preview cards, evidence-link plans, and cleanup exclusions.

#### Scenario: Layout plan is generated

- **WHEN** a system asset contract is created or updated
- **THEN** its native layout plan includes `schemaVersion`, `zones`, `slot`, `plannedBbox`, `cleanSource`, `previewCard`, `evidenceLinks`, `cleanupPolicy`, and a compatibility `grid`

#### Scenario: Training text appears in candidate content

- **WHEN** candidate content contains training titles, temporary notes, borders, dimensions, audit notes, or evidence text
- **THEN** the cleanup policy excludes those content types from the clean reusable source area unless explicitly included by precise source-boundary evidence

#### Scenario: Visual rack plan is label-only metadata

- **WHEN** a system asset package records a `visualRackPlan` that lacks v2 warehouse architecture, acceptance criteria, rack ownership, copy policy, expansion slots, or zone bbox ratios
- **THEN** the layout metadata refresh and asset-library governance check fail before treating the package as a visually accepted warehouse

#### Scenario: Visual rack plan is drawn in a system asset DWG

- **WHEN** the system writes a warehouse shelf scaffold into a system asset DWG
- **THEN** the report records the audited `visualRackPlan`, protected existing asset-content bboxes, created handles, resolved-handle count, per-layer readback, full shelf entity bboxes, shelf/content clearance audit, saved system asset DWG status, and `savedCurrentBusinessDwg=false`

#### Scenario: Shelf geometry overlaps protected asset content

- **WHEN** a warehouse shelf frame, label, route, or slot grid bbox intersects protected existing asset-content bboxes
- **THEN** the layout script and asset-library governance check fail instead of treating the DWG warehouse as visually accepted

#### Scenario: Warehouse layout is geometrically clear but visually unreadable

- **WHEN** a system asset DWG shelf layout has zero bbox overlaps but cramped aisles, over-dense A1/A2 shelves, proof content left on `CODEX_PREVIEW`, or source boundaries drawn around proof panels
- **THEN** `visualReadabilityAudit` and the `visual_layout_review` A-to-A hard gate fail until the report proves readable aisles, acceptable content density, source/proof separation, layer semantics, and non-screenshot evidence

### Requirement: Asset governance agents are globally registered

The global pipeline SHALL register an asset governor and asset governance child agents with clear responsibilities and constraints.

#### Scenario: Pipeline manifest is inspected

- **WHEN** the global pipeline manifest is loaded
- **THEN** it lists `pipeline_asset_governor`, `pipeline_asset_librarian`, `pipeline_asset_dwg_curator`, and `pipeline_asset_reuse_auditor`, and the default flow routes asset sedimentation through the governor

#### Scenario: Agent derivation is considered

- **WHEN** the governor determines existing child roles are insufficient
- **THEN** it records a reviewed-package requirement for any new global Agent rather than silently inventing an untracked Agent role

### Requirement: Reuse verification gates asset verification

The system SHALL distinguish asset registration, layout planning, native DWG writing, and reuse verification.

#### Scenario: Metadata and layout are valid but CAD replay is missing

- **WHEN** a system asset has valid contract fields and layoutPlan v2 but no real native CAD insertion replay or created-handle readback
- **THEN** it MUST NOT claim native CAD reuse verification solely from the layout plan

#### Scenario: Reuse replay passes

- **WHEN** an asset reuse audit records created handles, readback status `ok`, source spec, target layer, and saved-current-DWG false
- **THEN** the asset MAY be considered for `verified` status according to its lifecycle rules

### Requirement: Completion includes hardening decision

The system SHALL emit a machine-readable hardening decision at the end of asset-library governance work.

#### Scenario: Current scope is complete

- **WHEN** all planned governance tasks, metadata validation, layout checks, and available tests pass
- **THEN** the hardening decision reports `complete_for_current_scope` while preserving any not-run native CAD evidence boundaries

#### Scenario: More work is needed

- **WHEN** source boundaries, native CAD layout, reuse replay, text cleanup, or Agent rules remain incomplete
- **THEN** the hardening decision reports the precise next hardening category rather than claiming full native asset completion
