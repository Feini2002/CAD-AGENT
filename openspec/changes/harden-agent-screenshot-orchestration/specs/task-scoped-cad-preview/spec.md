## MODIFIED Requirements

### Requirement: Task-scoped CAD preview capture

The system SHALL capture CAD previews as task-scoped visual evidence, using the most precise available target before falling back to broader execution context. A screenshot SHALL remain `visual_aid_only` and SHALL NOT replace created handles, CAD readback, geometry audit, or user review.

#### Scenario: Capture uses local repair target first
- **WHEN** a caller provides `target_handles`, `repair_plan.target_handles`, `repair_plan.target_bbox`, or explicit `target_bbox`
- **THEN** the screenshot focus MUST use that local target before considering the full `execution_summary.created_handles` list

#### Scenario: Capture does not silently zoom to full drawing
- **WHEN** the requested local target cannot be resolved in the active CAD document
- **THEN** the system MUST report `focus_target_unavailable` and MUST NOT silently use full drawing extents as evidence for the local task

#### Scenario: Agent orchestration selects capture input
- **WHEN** an Agent or runner asks for screenshot evidence for a CAD task
- **THEN** it MUST build or receive a screenshot orchestration decision and pass the selected focus inputs into the capture call
