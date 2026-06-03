## ADDED Requirements

### Requirement: Visual query profile
The system SHALL convert a user visual/semantic request into a structured query profile before scoring CAD block candidates.

#### Scenario: Sofa request profile
- **WHEN** the user asks to find a sofa shown in a screenshot
- **THEN** the system SHALL produce a query profile containing object category `sofa`, plan-view intent when available, expected visual parts, and a sofa-like aspect-ratio range.

### Requirement: Visual-first candidate ranking
The system SHALL rank current-DWG block references with visual/semantic signals before reading detailed CAD block construction for final confirmation.

#### Scenario: Current DWG sofa candidate
- **WHEN** the active DWG contains a wide three-seat sofa block and unrelated preview test blocks
- **THEN** the system SHALL rank the sofa block above unrelated preview test blocks using visual profile, bbox ratio, source layer, and furniture-scale signals.

### Requirement: CAD readback evidence boundary
The system SHALL output CAD readback evidence for the selected candidate and SHALL distinguish visual similarity from CAD geometry proof.

#### Scenario: Candidate report
- **WHEN** retrieval returns a best matching block
- **THEN** the report SHALL include `handle`, `block_name`, `layer`, `bbox`, scoring reasons, elapsed time, and a statement that screenshot similarity does not prove true CAD dimensions.

### Requirement: Read-only retrieval safety
The system SHALL perform current-DWG visual retrieval in read-only mode unless the caller explicitly invokes a separate drawing action.

#### Scenario: Retrieval safety
- **WHEN** the visual retrieval CLI runs against AutoCAD
- **THEN** it SHALL not save the DWG, delete entities, or write to formal layers.
