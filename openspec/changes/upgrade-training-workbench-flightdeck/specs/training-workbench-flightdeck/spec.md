## ADDED Requirements

### Requirement: Command center default view
The training workbench SHALL open to a command-center view that prioritizes daily training decisions over the full training matrix.

#### Scenario: Operator opens workbench
- **WHEN** the workbench is loaded from the generated snapshot
- **THEN** the default visible view shows next training candidates, sync health, gateboard health, latest run or queue status, Agent dispatch summary, and evidence boundary

#### Scenario: Training table remains available
- **WHEN** the operator needs to scan all training programs
- **THEN** the workbench provides a training map view with the full matrix or compact table without making it the default screen

### Requirement: Next training candidates
The workbench SHALL display a deterministic list of next training candidates with route mode, recommendation reason, responsible agents, evidence requirements, and blocking conditions.

#### Scenario: Candidate can be trained
- **WHEN** a candidate has no blocking source or gate condition
- **THEN** the candidate shows its route mode as `quick_trial`, `focused_retraining`, or `formal_acceptance` and lists the minimum evidence needed before it can be claimed as accepted

#### Scenario: Candidate is blocked
- **WHEN** a candidate depends on missing active evidence, data-bloat closure, or another hard gate
- **THEN** the candidate remains visible but is labeled with the blocking condition and must not be shown as ready for formal acceptance

### Requirement: Persistent inspector
The workbench SHALL provide a persistent inspector that explains the currently selected training program, Agent, source, run, trace, gate, or evidence bundle.

#### Scenario: Training program selected
- **WHEN** the operator selects a training program
- **THEN** the inspector shows its objective, stage, next training target, responsible Agent chain, evidence bundle summary, and evidence boundary

#### Scenario: Agent selected
- **WHEN** the operator selects an Agent
- **THEN** the inspector shows the Agent role, execution model, source refs, hard gates, prompt contract, and learning refs without implying CAD capability proof

### Requirement: Evidence boundary always visible
The workbench SHALL keep evidence-boundary language visible in command center, training map, Agent, evidence, and trace contexts.

#### Scenario: Table C displayed
- **WHEN** Table C or CAD strength metrics are shown
- **THEN** the view states that Table C is read from coverage JSON and is separate from training progress, Agent maturity, Prompt Pack readiness, and user acceptance

#### Scenario: Screenshot or trace displayed
- **WHEN** screenshot, model trace, dry-run, or derived snapshot evidence is displayed
- **THEN** the view labels it as auxiliary or derived unless a corresponding CAD readback / created-handle evidence bundle exists

### Requirement: Safe readonly browser operations
The workbench SHALL keep browser actions readonly in the MVP.

#### Scenario: Operator interacts with command center
- **WHEN** the operator clicks refresh, copy command, jump to source, jump to Agent, or jump to trace controls
- **THEN** the browser only changes local UI state, reloads the page, or copies commands / paths and must not silently write repository files or run training
