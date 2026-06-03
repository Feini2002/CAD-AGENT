## ADDED Requirements

### Requirement: OpenSpec readiness commands
The repository SHALL define a short OpenSpec readiness path that proves the local OpenSpec installation and repository contract are usable.

#### Scenario: Agent checks OpenSpec readiness
- **WHEN** an agent needs to verify OpenSpec is usable in this repository
- **THEN** the documented readiness path MUST include `openspec list --json`, `openspec status --change <change> --json`, and `openspec validate --all --strict --json --no-interactive`

#### Scenario: Status command requires a change
- **WHEN** `openspec status --json` is run without `--change`
- **THEN** the system contract MUST explain that the CLI requires a specific change and that this failure is not an initialization failure

### Requirement: Completed changes and main specs boundary
The repository SHALL NOT treat completed OpenSpec changes or archived stable specs as repository planning authority.

#### Scenario: Main specs are empty
- **WHEN** `openspec list --specs --json` reports no specs while completed changes exist
- **THEN** the system contract MUST state that OpenSpec can still be usable and that stable specs are created through an explicit archive/sync decision

#### Scenario: Completed change is archived
- **WHEN** a completed OpenSpec change is archived
- **THEN** the agent MUST update or confirm stable specs and any repository references that still point at `openspec/changes/<change>/`

### Requirement: Scoped contract stays below root planning boundary
The repository SHALL keep OpenSpec as a scoped change-contract layer beneath `CORE_RESTRUCTURE_PLAN.md`.

#### Scenario: OpenSpec readiness docs are added
- **WHEN** OpenSpec readiness or contract docs are added
- **THEN** they MUST NOT introduce global `next`, master backlog, repository-wide priority ordering, or PlanMD replacement language

#### Scenario: CAD capability claims are discussed
- **WHEN** an OpenSpec change mentions CAD capability, training progress, or Designer Agent progress
- **THEN** it MUST preserve the evidence boundary between curriculum progress, Table C, real CAD proof, and user acceptance
