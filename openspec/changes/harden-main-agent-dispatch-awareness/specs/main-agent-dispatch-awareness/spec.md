## ADDED Requirements

### Requirement: Main Agent Self Check

The system SHALL generate a machine-readable `mainAgentSelfCheck` section inside every high-risk `a_to_a_task_contract`. High-risk task kinds MUST include `system_asset_sedimentation`, `asset_dwg_layout`, and `visual_layout_review`. The self-check MUST state the main Agent identity, mission, task understanding, responsibility boundary, known limits, and decision basis.

#### Scenario: High-risk contract contains main Agent identity
- **WHEN** a request is classified as `asset_dwg_layout`
- **THEN** the contract contains `mainAgentSelfCheck.identity`
- **AND** `mainAgentSelfCheck.mission` states that the main Agent classifies, contracts, dispatches, and blocks unsupported completion claims
- **AND** `mainAgentSelfCheck.responsibilityBoundary.mayExecuteCad` is false

#### Scenario: Missing main Agent self-check blocks completion
- **WHEN** a high-risk contract lacks `mainAgentSelfCheck` or marks it as failed
- **THEN** `a_to_a_task_contract.status` is `blocked`
- **AND** `deliveryBoundary.mayClaimComplete` is false
- **AND** `workflow_dispatch.reason` includes an A-to-A hard gate reason

### Requirement: Registered Agent Dynamic Dispatch

The system SHALL allow the main Agent to add already registered pipeline Agents to the effective required Agent list when request semantics, semantic asset routing, or hard gate requirements require them. Every dynamic addition MUST include the Agent ID, triggering semantic reason, and hard gate affected.

#### Scenario: Visual layout semantics add visual reviewer
- **WHEN** a request asks for a system asset DWG warehouse, shelf, rack, aisle, expandable slot, or display layout
- **THEN** `dispatchDecision.registeredAdditionalAgents` includes `pipeline_visual_layout_reviewer`
- **AND** `dispatchDecision.effectiveRequiredAgents` includes `pipeline_visual_layout_reviewer`
- **AND** `hardGates` includes `visual_layout_review`

#### Scenario: Missing dynamically added Agent output blocks dispatch
- **WHEN** `pipeline_visual_layout_reviewer` is dynamically added to `effectiveRequiredAgents`
- **AND** no output exists for `pipeline_visual_layout_reviewer`
- **THEN** `missingRequiredAgents` includes `pipeline_visual_layout_reviewer`
- **AND** `workflow_dispatch.status` is `blocked`

### Requirement: Unregistered Agent Requests Stay As Reviewed Candidates

The system MUST NOT activate, require, or claim completion from an Agent that is absent from `agents/pipeline/pipeline_manifest.json`. A new Agent need identified by the main Agent MUST be recorded under `dispatchDecision.additionalAgentRequests` with `status` equal to `needs_reviewed_package` or `needs_openspec_change`.

#### Scenario: New Agent need is recorded but not activated
- **WHEN** the main Agent detects a need for `pipeline_asset_polish_reviewer`
- **AND** that Agent is not registered in the pipeline manifest
- **THEN** `dispatchDecision.additionalAgentRequests` includes `pipeline_asset_polish_reviewer`
- **AND** `dispatchDecision.effectiveRequiredAgents` does not include `pipeline_asset_polish_reviewer`
- **AND** `dispatchDecision.reviewedPackageRequired` is true

#### Scenario: Unregistered Agent activation is blocked
- **WHEN** a contract places an unregistered Agent inside `effectiveRequiredAgents`
- **THEN** `a_to_a_task_contract.status` is `blocked`
- **AND** `failedHardGates` includes `main_agent_dispatch_awareness`
- **AND** `deliveryBoundary.mustReportBlockedAgentGates` is true

### Requirement: Dispatch Decision Evidence Boundary

The system SHALL record a `dispatchDecision` section that distinguishes base required Agents, registered dynamic additions, effective required Agents, missing outputs, failed gates, and reviewed-package Agent requests. A complete delivery claim MUST be disallowed when `dispatchDecision.blockedUntilAgentsReport` is true.

#### Scenario: Blocked-until-report prevents complete claim
- **WHEN** `dispatchDecision.blockedUntilAgentsReport` is true
- **THEN** `deliveryBoundary.mayClaimComplete` is false
- **AND** `blockingReasons` explain which Agent outputs or reviewed-package decisions are missing

#### Scenario: Ready dispatch has explicit reasoning
- **WHEN** all effective required Agent outputs pass
- **THEN** `dispatchDecision.status` is `ready`
- **AND** every registered dynamic addition includes a non-empty `reason`
- **AND** `missingRequiredAgents` and `failedHardGates` are empty

### Requirement: Main Agent Policy Is Anchored In Manifest

The system SHALL treat `agents/pipeline/pipeline_manifest.json` as the source of truth for pipeline Agent registration and main Agent dynamic dispatch policy. The manifest MUST define main Agent identity, dynamic dispatch boundaries, unregistered Agent request policy, and forbidden patterns for silently activating untracked Agents.

#### Scenario: Manifest defines main Agent dispatch policy
- **WHEN** the A-to-A orchestration gate check runs
- **THEN** it verifies that `orchestration.main_agent_identity` exists
- **AND** it verifies that `orchestration.dynamic_dispatch_policy` exists
- **AND** it verifies that unregistered Agent activation is forbidden

#### Scenario: Missing manifest policy blocks gate check
- **WHEN** the manifest lacks main Agent identity or dynamic dispatch policy
- **THEN** `scripts/run_a_to_a_orchestration_gate_check.py` returns `status=fail`
- **AND** its issues list names the missing policy field

### Requirement: Visual Layout Readability Gate

The system SHALL require `layoutReadabilityAcceptable` as part of the visual layout review hard gate. A nonblank screenshot, existing CAD entities, or passing object counts MUST NOT replace this field.

#### Scenario: Incomplete visual layout readability fails
- **WHEN** `pipeline_visual_layout_reviewer` outputs `status=pass`
- **AND** omits `layoutReadabilityAcceptable`
- **THEN** the contract status is `blocked`
- **AND** `failedHardGates` includes `visual_layout_review`

#### Scenario: Screenshot-only review fails visual layout gate
- **WHEN** `pipeline_visual_layout_reviewer` sets `screenshotCapturedOnly=true`
- **THEN** the contract status is `blocked`
- **AND** `agentOutputSummary.pipeline_visual_layout_reviewer.visualFailures` includes `screenshotCapturedOnly`
