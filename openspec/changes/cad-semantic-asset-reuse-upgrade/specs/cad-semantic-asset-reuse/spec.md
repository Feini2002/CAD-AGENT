## ADDED Requirements

### Requirement: Semantic asset rules route reusable CAD requests before generic CAD drawing

The system SHALL evaluate a machine-readable semantic rule catalog before ordinary CAD_PLAN generation when a user request may involve reusable system assets, asset sedimentation, local repair, or line-type table layout constraints.

#### Scenario: Implicit line-type table reuse

- **WHEN** the user asks to place a line-type table without explicitly saying "资产"
- **THEN** the semantic rule catalog identifies the line-type table rule
- **AND** the asset reuse workflow is attempted before generic drawing.

### Requirement: System asset reuse blocks corrupt registry text before matching

The system SHALL run UTF-8 and mojibake preflight over searchable registry asset text before using it for semantic matching.

#### Scenario: Corrupt asset name

- **WHEN** a registry asset name or alias contains mojibake or replacement characters
- **THEN** the reuse workflow returns `asset_registry_encoding_failed`
- **AND** no ready reuse plan is generated.

### Requirement: Weak asset matches do not become ready reuse plans

The system SHALL report weak candidate matches without treating them as reusable assets unless explicit reuse language or a strong semantic score is present.

#### Scenario: Generic drawing request

- **WHEN** a normal drawing request only weakly overlaps with an existing asset
- **THEN** the workflow returns `not_asset_reuse_request`
- **AND** generic CAD planning may proceed separately.

### Requirement: Asset candidate ranking is stable and safety-aware

When multiple assets match a request, the system SHALL prefer verified, CAD-native, precisely sourced assets over candidate or metadata-only assets, and SHALL apply a deterministic tie-breaker.

#### Scenario: Candidate and verified asset share an alias

- **WHEN** both candidate and verified assets match the same phrase
- **THEN** the verified reusable asset is selected first.

### Requirement: Line-type table layout is independently audited

The line-type table report SHALL include an independent layout audit based on visible text and created-handle readback rather than only generator policy fields.

#### Scenario: Sample geometry leaves its cell

- **WHEN** a sample entity bbox is outside its row sample cell
- **THEN** the audit fails even if `layoutChecks.sampleOutOfCellCount` was manually set to zero.

### Requirement: Line-type tables support variable row counts

The line-type table generator SHALL support smaller or larger row sets without relying on fixed 24-row, 42-row, or one-page constants.

#### Scenario: A 17-row focused table

- **WHEN** the generator receives 17 valid rows
- **THEN** the report row count is 17
- **AND** layout auditing still passes.
