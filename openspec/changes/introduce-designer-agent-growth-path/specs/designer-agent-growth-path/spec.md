## ADDED Requirements

### Requirement: CAD Designer Agent training target
The system SHALL define a top-level CAD Designer Agent that represents the electronic designer being trained, and SHALL treat existing scene, pipeline, asset, and audit agents as callable knowledge/process resources rather than as competing final delivery agents.

#### Scenario: Workbench identifies the top-level training subject
- **WHEN** the training workbench data is generated
- **THEN** it includes a CAD Designer Agent profile with role, graduation target, first-stage focus, callable agents, evidence boundary, and source docs

#### Scenario: Scene agents remain lightweight
- **WHEN** the CAD Designer Agent references residential or future scene agents
- **THEN** those scene agents remain vocabulary/preference/rule providers and do not become CAD execution implementations

### Requirement: Growth path curriculum
The system SHALL expose a designer growth path that starts from CAD foundation operations and progresses toward professional drawing and construction-document competence.

#### Scenario: Growth stages are generated
- **WHEN** workbench data is built
- **THEN** the data includes ordered growth stages covering foundation operations, geometric constraints, object symbols, room plans, professional expression, construction drawings, and design judgment

#### Scenario: Existing capability matrix is preserved
- **WHEN** the growth path is introduced
- **THEN** existing object, drawing, annotation, asset, and pipeline capability rows remain available as the CAD Designer Agent capability passport

### Requirement: First-stage graduation target
The system SHALL set the first-stage graduation target to an electronic designer prototype that trains foundation commands, residential objects, and audit self-check together, while starting the first course batch from foundation CAD operations.

#### Scenario: Foundation courses are first batch
- **WHEN** the workbench lists first-stage courses
- **THEN** the first batch contains foundation CAD operations such as primitive drawing, selection/editing, transform, offset/trim, layer discipline, closure, and readback/audit basics

#### Scenario: Graduation does not overclaim capability
- **WHEN** a foundation course is marked planned, training, or passed
- **THEN** the system states that this is training evidence only and not a table C increase, construction-document proof, or user project acceptance

### Requirement: Evidence and acceptance boundary
The system SHALL keep Designer Agent curriculum progress separate from real CAD proof, table C metrics, and case user acceptance.

#### Scenario: Status reporting uses correct boundary
- **WHEN** status documents mention the Designer Agent growth path
- **THEN** they distinguish curriculum progress from `CAD_PLAN` validation, dry-run, `CODEX_PREVIEW`, handle readback, geometry audit, and user feedback pass

#### Scenario: Self-check is required after implementation
- **WHEN** this change is implemented
- **THEN** the repository runs a training workbench data sync/check and at least one documentation or repository audit relevant to the changed files
