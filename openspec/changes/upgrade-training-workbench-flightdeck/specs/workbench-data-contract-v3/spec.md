## ADDED Requirements

### Requirement: Derived snapshot schema v3
The workbench data builder SHALL emit a schema v3 snapshot that separates metadata, facts, indices, views, and UI configuration while preserving the derived-only status of the snapshot.

#### Scenario: Snapshot generated
- **WHEN** `scripts/build_capability_map_data.py` generates `capability-map-data.js`
- **THEN** the assigned data contains schema v3 fields for `meta`, `facts`, `indices`, `views`, and `ui` or an explicitly versioned compatibility wrapper exposing those sections

#### Scenario: Snapshot source policy
- **WHEN** the snapshot describes its source policy
- **THEN** it states that `capability-map-data.js` and `capability-map.html` are derived views and not training fact sources

### Requirement: Source registry health
The schema v3 snapshot SHALL expose a source registry derived from `docs/training/training-sources.json` with role, kind, status, path, existence, and evidence-use classification.

#### Scenario: Active fact source exists
- **WHEN** a source is `role=fact_source`, `status=active`, and the path exists
- **THEN** the source registry marks it as usable for its declared evidence role

#### Scenario: Archived source exists or is missing
- **WHEN** a source is `status=archived`
- **THEN** the source registry marks it as historical only and it must not drive accepted, systemized, verified, or learned completion states

### Requirement: Gateboard health model
The schema v3 snapshot SHALL expose gateboard items for sync freshness, coverage freshness, Agent check, encoding health, source health, data-bloat / evidence closure, CAD safety, A-to-A gates, and visual acceptance when those facts are available.

#### Scenario: Gate is pass
- **WHEN** a gate has current passing evidence
- **THEN** the gateboard item includes `status=pass`, a concise reason, and the supporting source path

#### Scenario: Gate is blocked or unknown
- **WHEN** a gate is blocked, unknown, or not checked
- **THEN** the gateboard item includes a non-pass status, blocked claim types, and the evidence required to unblock it

### Requirement: Evidence bundles
The schema v3 snapshot SHALL expose compact evidence bundles for training programs and runs using summaries and paths, not full reports or large readback arrays.

#### Scenario: CAD evidence exists
- **WHEN** a training program has CAD execution evidence
- **THEN** its evidence bundle distinguishes validation, dry-run, created handles, readback, bbox / layer audit, screenshot, feedback, and learning promotion

#### Scenario: Evidence is auxiliary
- **WHEN** a bundle contains only screenshot, dry-run, model review, trace, or derived snapshot evidence
- **THEN** the bundle marks CAD geometry proof as not verified or not checked

### Requirement: Compact compatibility
The schema v3 snapshot SHALL avoid unbounded data growth and unnecessary duplicate aliases.

#### Scenario: Data builder emits snapshot
- **WHEN** the builder writes `capability-map-data.js`
- **THEN** the output remains compact and references large artifacts by path rather than embedding full artifact content

#### Scenario: Legacy view reads data
- **WHEN** existing v2 rendering code reads the snapshot during migration
- **THEN** the snapshot preserves compatibility fields or a normalization layer so current workbench checks can continue passing until the v3 page fully replaces them
