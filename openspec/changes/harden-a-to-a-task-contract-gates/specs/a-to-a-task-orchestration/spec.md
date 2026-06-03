## ADDED Requirements

### Requirement: Main orchestration builds an A-to-A task contract

The system SHALL build a machine-readable `a_to_a_task_contract` before treating orchestration-critical requests as executable or deliverable.

#### Scenario: Asset DWG warehouse layout request

- **WHEN** a user request combines system asset / asset DWG semantics with warehouse, shelf, rack, aisle, layout, expandable slot, or display-form semantics
- **THEN** the contract sets `taskKind=asset_dwg_layout`
- **AND** the contract includes required asset governance agents and `pipeline_visual_layout_reviewer`
- **AND** the contract includes `visual_layout_review` as a hard gate

#### Scenario: System asset sedimentation request

- **WHEN** a user asks to sediment, promote, or collect an item into the system asset library
- **THEN** the contract sets `taskKind=system_asset_sedimentation`
- **AND** the contract requires `pipeline_asset_governor`, `pipeline_asset_librarian`, `pipeline_asset_dwg_curator`, and `pipeline_asset_reuse_auditor`

### Requirement: Missing required Agent outputs block dispatch

The system SHALL block workflow dispatch when an A-to-A task contract requires Agent outputs that are missing or failing.

#### Scenario: Visual layout reviewer output is missing

- **WHEN** the contract requires `pipeline_visual_layout_reviewer`
- **AND** the request context has no passing output from that Agent
- **THEN** `a_to_a_task_contract.status=blocked`
- **AND** `workflow_dispatch.status=blocked`
- **AND** `workflow_dispatch.reason` contains `a-to-a hard gate`

#### Scenario: Required Agent outputs pass

- **WHEN** all required Agent outputs are present with passing statuses
- **AND** the visual layout reviewer pass fields are all pass
- **THEN** the contract status is `ready`
- **AND** `missingRequiredAgents` and `failedHardGates` are empty

### Requirement: Visual layout acceptance is a dedicated hard gate

The system SHALL distinguish visual layout acceptance from screenshot capture, CAD object existence, ordinary readback, or geometry audits.

#### Scenario: Screenshot is nonblank but layout review is absent

- **WHEN** a screenshot or CAD readback exists
- **AND** the task requires visual layout review
- **AND** `pipeline_visual_layout_reviewer` has not produced a passing `visual_layout_review`
- **THEN** the system MUST NOT claim the asset DWG layout is accepted or ready for user acceptance

#### Scenario: Visual layout reviewer fails a semantic criterion

- **WHEN** `pipeline_visual_layout_reviewer` reports fail for layout metaphor, shelf clarity, expansion slots, retrieval path, or visual noise
- **THEN** the contract records `visual_layout_review` in `failedHardGates`
- **AND** delivery-complete claims remain blocked

### Requirement: Repository governance check covers A-to-A orchestration gates

The repository SHALL provide a runnable check that verifies the A-to-A contract, manifest Agent registration, hard gates, and dispatch blocking behavior.

#### Scenario: Governance check runs

- **WHEN** `scripts/run_a_to_a_orchestration_gate_check.py` is executed
- **THEN** it verifies required Agent registration, `asset_dwg_layout` flow, hard gates, contract task detection, missing visual reviewer blocking, pass-output readiness, and dispatch blocking
- **AND** it exits nonzero if any required wiring is missing
