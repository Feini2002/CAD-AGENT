## ADDED Requirements

### Requirement: Module boundary snapshot
The repository SHALL provide a discoverable module-boundary snapshot that classifies stable Core, training experiments, and case-only code.

#### Scenario: Agent prepares architecture work
- **WHEN** an agent needs to plan architecture slimming or boundary-hardening work
- **THEN** the agent can read one architecture document that names the three buckets and the promotion rules between them

### Requirement: Verification split map
The repository SHALL define a verification split map that separates report contracts, runners, registry writeback, visual audit, and CAD/session safety responsibilities.

#### Scenario: Agent splits verification code
- **WHEN** an agent prepares to move code out of a large `core/verification/` file
- **THEN** the agent can map the code to a named verification responsibility before editing

### Requirement: Capability map split map
The repository SHALL define a capability-map split map that separates data generation, page shell, display configuration, and evidence-boundary concerns.

#### Scenario: Agent changes the capability map
- **WHEN** an agent changes `capability-map.html` or its data generator
- **THEN** the agent can identify whether the change belongs to data, UI shell, display configuration, or evidence policy

### Requirement: Object asset trial route
The repository SHALL name one first object-family asset trial route from raw reference through readback evidence without treating the trial as an already promoted system asset.

#### Scenario: Agent promotes asset intelligence
- **WHEN** an agent starts an object-family asset promotion package
- **THEN** the agent can follow the documented raw reference -> knowledge summary -> candidate -> executable check -> system asset -> `CAD_PLAN` -> readback route

### Requirement: Case-run promotion gate
The repository SHALL define evidence gates for moving reusable render or audit logic from `projects/.../runs/` into Core or shared libraries.

#### Scenario: Agent finds reusable case-run code
- **WHEN** an agent sees renderer or audit logic under `projects/.../runs/`
- **THEN** the agent must verify the documented evidence gates before promoting it into Core or shared libraries
