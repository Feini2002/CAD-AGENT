## ADDED Requirements

### Requirement: Agent system graph
The workbench SHALL model the Agent system as registered nodes and edges covering CAD Designer Agent, pipeline agents, scene agents, Prompt Packs, hard gates, Tool Contracts, run packages, evidence artifacts, and learning outputs.

#### Scenario: Agent graph built
- **WHEN** the builder reads Agent manifests, Prompt contracts, pipeline manifest, training programs, and trace summaries
- **THEN** the snapshot exposes stable node IDs, edge IDs, node types, edge types, source refs, and evidence boundaries

#### Scenario: Training program selected
- **WHEN** an operator selects a training program
- **THEN** the Agent system view can highlight responsible agents, required gates, related Prompt contracts, and evidence artifacts for that program

### Requirement: A-to-A and gate observability
The workbench SHALL show which agents and hard gates are required for registered high-risk task kinds and whether missing outputs block delivery claims.

#### Scenario: Task kind has required agents
- **WHEN** a task kind is present in the pipeline manifest hard-gate map or flow variants
- **THEN** the workbench exposes required agents, hard gates, blocked claim types, and source refs for that task kind

#### Scenario: Required output is missing
- **WHEN** a run or task summary lacks a required Agent output or hard gate result
- **THEN** the workbench marks the corresponding delivery claim as blocked or not checked rather than passed

### Requirement: Prompt Pack and model boundary
The workbench SHALL distinguish Prompt Pack readiness, model invocation, schema validity, and downstream evidence consumption.

#### Scenario: Prompt Pack ready
- **WHEN** a Prompt Pack or model-backed review node is marked ready
- **THEN** the workbench shows it as ready for that prompt contract but must not imply the model was invoked in a real run

#### Scenario: Model trace exists
- **WHEN** a model trace exists for a run
- **THEN** the trace view shows model invocation, provider status, schema validity if available, trace source paths, and downstream evidence refs without treating the trace as CAD geometry proof

### Requirement: Tool Contract visibility
The workbench SHALL expose tool intent and tool trace summaries when present, including permission class, risk level, target scope, deterministic entrypoint, expected evidence, and execution status.

#### Scenario: Tool request is readonly or preview-safe
- **WHEN** a tool intent is registered as readonly or preview-only and has a matching trace
- **THEN** the workbench shows the requested tool, status, expected evidence, and target scope

#### Scenario: Tool request is risky or incomplete
- **WHEN** a tool intent has missing approval, broad target scope, destructive risk, or no matching execution trace
- **THEN** the workbench marks the tool path as blocked, not executed, or not verified and must not imply CAD execution succeeded

### Requirement: Learning feedback loop
The workbench SHALL connect failures and accepted training outcomes to learning decisions for Agent memory, Prompt addenda, rules, checker candidates, and original-task retests.

#### Scenario: Training outcome promoted
- **WHEN** learning promotion evidence exists for a training item
- **THEN** the workbench shows which agents received memory or Prompt addendum updates and links the supporting source refs

#### Scenario: Failure requires follow-up
- **WHEN** a failure mode affects programs or agents
- **THEN** the workbench shows likely repair focus, responsible agents, and whether the next action is retrain, prompt update, rule update, checker candidate, or original-task retest
