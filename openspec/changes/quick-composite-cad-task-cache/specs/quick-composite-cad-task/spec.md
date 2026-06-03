## ADDED Requirements

### Requirement: Current DWG block cache
The system SHALL be able to build and reuse a current-DWG block cache containing lightweight block reference facts.

#### Scenario: Cache manifest from active DWG snapshot
- **WHEN** modelspace entities contain block references
- **THEN** the system SHALL produce a manifest with document identity, block candidate rows, candidate count, and cache source metadata.

#### Scenario: Valid cache reuse
- **WHEN** a cache manifest document identity matches the active document
- **THEN** the quick composite task MAY rank candidates from the cache without taking a new full modelspace snapshot.

### Requirement: Generic bbox dimension action
The system SHALL provide an object-agnostic bbox dimension action for retrieved block candidates.

#### Scenario: Any block candidate with bbox
- **WHEN** a retrieved block candidate has a valid bbox
- **THEN** the system SHALL generate width/depth dimension operations from the bbox and SHALL write only preview-layer dimension entities during execution.

### Requirement: Quick composite find-and-annotate report
The system SHALL produce one report for the quick composite task that separates target retrieval, action planning, execution readback, timings, cache source, and safety.

#### Scenario: Find and annotate target
- **WHEN** the user asks to find an object and annotate bbox dimensions
- **THEN** the report SHALL include target `handle`, `block_name`, `bbox`, target size, created dimension handles, readback text, output layer, and cache/live source.

### Requirement: Preview-only safety
The system SHALL not save the DWG, delete entities, modify the target block, or write formal layers during quick composite execution.

#### Scenario: Execution safety
- **WHEN** the quick composite task writes dimensions
- **THEN** all created entities SHALL be on `CODEX_PREVIEW` and the report SHALL state that the target block and formal layers were not modified.
