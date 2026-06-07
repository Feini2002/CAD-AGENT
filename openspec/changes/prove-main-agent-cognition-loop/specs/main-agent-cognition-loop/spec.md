## ADDED Requirements

### Requirement: No-CAD cognitive loop records tool-result self-correction

The system SHALL record a machine-readable cognition-loop summary when a model-backed Agent requests an allowed no-CAD tool, receives the orchestrator-owned tool trace, and is called again for self-correction.

#### Scenario: Tool trace is fed back to the same Agent

- **WHEN** a model-backed Agent emits an allowed read-only, safe-generation, or deterministic-verify `toolIntent`
- **AND** the orchestrator executes the tool and writes a tool trace
- **THEN** the same Agent MAY receive a second prompt with a self-correction context
- **AND** the run result SHALL include `cognitiveLoopSummary.maxRounds=2`
- **AND** the event SHALL reference the tool trace and include behavior-change proof fields
- **AND** the event SHALL state that no CAD write, save, delete, or formal-layer permission is implied

### Requirement: Evidence portfolio is export-boundary safe

The system SHALL build model judgement portfolios as sanitized summaries and explicit refs, not as automatic permission to export arbitrary files.

#### Scenario: Portfolio is included in a model prompt

- **WHEN** a model prompt references `evidence_portfolio.json`
- **THEN** the portfolio itself SHALL pass through `build_model_export_manifest()`
- **AND** paths listed inside the portfolio SHALL NOT automatically become exported payload refs
- **AND** the portfolio SHALL record CAD, user-acceptance, Core Proof Coverage, and Project Delivery Readiness as non-proven claims

### Requirement: Behavior-change proof gates cognition claims

The system SHALL distinguish mechanism construction from cognition improvement using before/after decision evidence.

#### Scenario: No decision changes

- **WHEN** before/after route, required Agents, tool choice, and blocking reasons are unchanged
- **THEN** the proof SHALL return `claimStatus=mechanism_only`
- **AND** delivery text MUST NOT claim main Agent cognition improvement

#### Scenario: A decision changes

- **WHEN** at least one of route, required Agents, tool choice, or blocking reasons changes
- **THEN** the proof SHALL return `claimStatus=behavior_change_evidence`
- **AND** the proof SHALL still state that it is not CAD geometry or project delivery proof

### Requirement: Soft judgement exposes uncertainty without weakening hard gates

The system SHALL require soft judgement outputs to include `selfUncertainty`.

#### Scenario: Soft judgement is returned

- **WHEN** a model-backed design, visual, layout, or delivery reviewer returns `softJudgment`
- **THEN** `selfUncertainty` SHALL be present as a list
- **AND** confidence, uncertainty, and prediction accuracy SHALL NOT replace CAD, source, no-save, training, table-C, or delivery hard gates

### Requirement: Cheapest route preserves hard-gate isolation

The Orchestrator Host SHALL record complexity and route-budget metadata without removing hard gates.

#### Scenario: Quick trial is selected

- **WHEN** a request explicitly asks for a quick trial such as `试一下` or `先看看`
- **AND** it negates sedimentation with phrases such as `不沉淀`
- **THEN** the route MAY be `quick_trial`
- **AND** `routeBudget.mode` SHALL be `quick_draw`
- **AND** `routeBudget.mustKeepHardGates` SHALL still include the selected route hard gates

#### Scenario: High-risk route is selected

- **WHEN** the route is asset sedimentation, asset reuse, formal acceptance, or deletion/local repair
- **THEN** `complexityAssessment.riskLevel` SHALL be `high`
- **AND** route budget SHALL NOT skip source, data-bloat, CAD readback, or closeout hard gates
