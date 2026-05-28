## ADDED Requirements

### Requirement: OpenSpec change contract routing
The repository SHALL define OpenSpec as a scoped change-contract layer for complex CAD Agent changes, while preserving `CORE_RESTRUCTURE_PLAN.md` as the only master planning line.

#### Scenario: Complex change uses OpenSpec
- **WHEN** a requested change affects CAD_PLAN contracts, real CAD validation standards, capability registry semantics, Core architecture boundaries, or multiple modules
- **THEN** the agent MUST create or update a scoped OpenSpec change before implementation unless the user explicitly requests a direct small edit

#### Scenario: Small work stays lightweight
- **WHEN** a requested change is a single small bugfix, ordinary training round, Table C refresh, or status-only update
- **THEN** the agent MUST NOT require an OpenSpec change merely to proceed

### Requirement: OpenSpec cannot become a master roadmap
OpenSpec change artifacts SHALL NOT carry global `next`, PlanMD authority, master backlog, priority ordering, or repository-wide exit criteria.

#### Scenario: Root OpenSpec task ledger is rejected
- **WHEN** a root-level `openspec/tasks.md` file exists
- **THEN** the governance audit MUST report a finding because tasks must belong to a specific `openspec/changes/<change>/tasks.md`

#### Scenario: Active change claims master-plan authority
- **WHEN** an active OpenSpec change Markdown file states that it is the only PlanMD, master roadmap, or global backlog
- **THEN** the governance audit MUST report a finding and point back to `CORE_RESTRUCTURE_PLAN.md`

### Requirement: OpenSpec boundary is machine-auditable
The repository SHALL include a doc-governance check that verifies the OpenSpec root configuration preserves the single PlanMD boundary.

#### Scenario: Config omits single PlanMD boundary
- **WHEN** `openspec/config.yaml` exists but does not reference `CORE_RESTRUCTURE_PLAN.md`
- **THEN** the governance audit MUST report a finding that the OpenSpec contract boundary is incomplete

#### Scenario: Config preserves single PlanMD boundary
- **WHEN** `openspec/config.yaml` references `CORE_RESTRUCTURE_PLAN.md` and active changes do not claim master-plan authority
- **THEN** the governance audit MUST pass the OpenSpec contract section
