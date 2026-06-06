# system-architecture-canvas Specification

## Purpose

Provide a repository-level architecture canvas that absorbs historical planning tables, Core proof coverage, CAD Designer training, asset governance, multi-agent orchestration, local model bridge, Worker orchestration, execution tools, audit, repair, and learning into one task lifecycle.

## ADDED Requirements

### Requirement: Seven-Layer Task Lifecycle

The system SHALL classify every CAD Agent concept, task, script, document, and status claim into one of these layers:

1. system entry
2. task object
3. decision orchestration
4. capability and evidence
5. execution tools
6. audit and repair
7. sedimentation and learning

#### Scenario: Classify a historical metric

- **GIVEN** a status claim references table C, `cad_strength_headline_percent`, `cad_proof_coverage_percent`, or old “真实 CAD 实力”
- **WHEN** the claim is used in planning or status
- **THEN** it SHALL be classified as layer 4 capability and evidence
- **AND** it SHALL NOT be used as direct evidence of end-to-end task maturity or project delivery readiness

#### Scenario: Classify model bridge output

- **GIVEN** a Worker, bridge, GPT-5.5, Prompt Pack, or model trace output
- **WHEN** the system describes its role
- **THEN** it SHALL be classified as layer 3 decision orchestration
- **AND** it SHALL NOT replace layer 5 CAD execution evidence or layer 6 closeout evidence

### Requirement: Mature Capability Metrics

The system SHALL separate maturity claims into at least three labels:

- `Core Proof Coverage`: historical bottom-layer proof and registry coverage.
- `Agent Task Maturity`: CAD Designer Agent end-to-end task maturity across understanding, execution, audit, repair, and feedback.
- `Project Delivery Readiness`: readiness for real projects and complete construction drawing delivery.

#### Scenario: Discussing current system ability

- **GIVEN** the user asks whether the system is ready to train or deliver CAD work
- **WHEN** the answer includes maturity claims
- **THEN** `Core Proof Coverage` MAY cite historical coverage JSON
- **AND** `Agent Task Maturity` MUST be discussed separately
- **AND** `Project Delivery Readiness` MUST NOT be inferred from table C, RCAD smoke, screenshots, dry-run, fake-driver output, or no-CAD benchmark.

### Requirement: Architecture Convergence Gate Before Training

Before opening new formal object training or case training, the system SHALL complete an architecture convergence pass.

#### Scenario: User asks to start a new training round before convergence

- **GIVEN** the architecture convergence change is active
- **WHEN** the user asks to start a formal training round
- **THEN** the agent SHALL explain that the current priority is architecture convergence
- **AND** SHALL only proceed with training if the user explicitly overrides the pause
- **AND** SHALL still obey existing quick / focused / formal training boundaries.

### Requirement: No Second Master Plan

The system SHALL keep `CORE_RESTRUCTURE_PLAN.md` as the only master PlanMD.

#### Scenario: OpenSpec tasks exist

- **GIVEN** `openspec/changes/unify-system-architecture-canvas/tasks.md` contains implementation tasks
- **WHEN** future agents choose what to execute next
- **THEN** they SHALL use OpenSpec as the change contract
- **AND** they SHALL use `CORE_RESTRUCTURE_PLAN.md` as the active priority source.

### Requirement: Script and Workbench Alignment

The implementation SHALL identify and update scripts or derived displays that still promote old metrics as end-to-end true CAD ability.

#### Scenario: Workbench displays coverage

- **GIVEN** `capability-map.html` or `capability-map-data.js` displays table C or coverage-like values
- **WHEN** the convergence implementation updates the workbench generation scripts
- **THEN** the UI or generated data SHALL label those values as Core proof / evidence coverage
- **AND** SHALL avoid implying Agent task maturity or project delivery readiness.

### Requirement: Testing Chain Admission After Convergence

After architecture convergence, the system SHALL distinguish architecture cleanliness from readiness for formal training or project delivery.

#### Scenario: Deciding whether to run the next test chain

- **GIVEN** the architecture convergence tasks are complete
- **WHEN** a user asks whether the system is clean enough for the next testing stage
- **THEN** the answer SHALL check repository cleanliness, single PlanMD status, OpenSpec contract status, A-to-A gate availability, execution evidence boundaries, and sedimentation boundaries
- **AND** it SHALL recommend a minimal testing chain before formal training
- **AND** it SHALL NOT present architecture-document cleanup as proof of Agent task maturity or project delivery readiness.
