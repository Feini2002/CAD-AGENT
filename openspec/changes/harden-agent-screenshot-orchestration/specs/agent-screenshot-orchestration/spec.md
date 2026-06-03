## ADDED Requirements

### Requirement: Screenshot orchestration decision

The system SHALL expose a structured screenshot orchestration decision that determines whether a CAD screenshot is required or recommended for a task, which focus target source must be used, and how the evidence must be described.

#### Scenario: Local repair requires focused screenshot
- **WHEN** the task context contains a `repair_plan` with `target_handles` or `target_bbox`
- **THEN** the decision MUST set `shouldCapture=true`, `required=true`, `focusSource` to the local repair target, and `visualAidOnly=true`

#### Scenario: Execution summary fallback remains task scoped
- **WHEN** no local target is present but an `execution_summary.created_handles` list is available
- **THEN** the decision MUST set the focus source to `execution_summary.created_handles` and MUST NOT allow current-screen or whole-modelspace capture as the primary target

#### Scenario: Quick trial can avoid heavy screenshot
- **WHEN** the task context is `quick_trial`, has successful key readback, and has no visual problem or formal acceptance request
- **THEN** the decision MUST allow `shouldCapture=false` while retaining `visualAidOnly=true` if a screenshot is later captured

### Requirement: Agent screenshot capability understanding

The system SHALL make screenshot capability rules visible to every responsibility Agent through the shared prompt contract and shall verify those rules with a machine check.

#### Scenario: Shared contract contains screenshot rules
- **WHEN** the training workbench Agent check runs
- **THEN** it MUST verify that `agents/COMMON_PROMPT_CONTRACT.md` contains rules for task-scoped screenshot orchestration, local repair focus targets, AutoCAD client-area PrintWindow capture, and `visual_aid_only` evidence boundaries

#### Scenario: Agent addenda rely on shared contract
- **WHEN** an Agent prompt addendum is inspected
- **THEN** it MUST reference the shared prompt contract instead of duplicating or omitting the screenshot orchestration rules

### Requirement: Runner screenshot payload consistency

CAD visual review, focused retraining, and cross-machine verification runners SHALL report a consistent screenshot decision / visual preview payload whenever they capture or intentionally skip a screenshot.

#### Scenario: Visual review reports decision payload
- **WHEN** `visual_cad_review` captures a screenshot from an execution summary
- **THEN** the report MUST include `screenshotDecision.visualAidOnly=true` and a focus source derived from `target_handles`, `repair_plan`, or `execution_summary.created_handles`

#### Scenario: Training capture records smart routing
- **WHEN** foundation training runs with `capture_preview=true`
- **THEN** its report MUST include `visualPreview` and `screenshotDecision` fields that identify whether the capture was required, which focus source was used, and why the screenshot remains visual evidence only
