## ADDED Requirements

### Requirement: Task-scoped preview focus
The system SHALL focus AutoCAD visual preview captures on the current task target when task handles or an explicit target bbox are available.

#### Scenario: Capture prefers local repair target handles
- **WHEN** a capture is requested with both whole-run `execution_summary.created_handles` and explicit local `target_handles`
- **THEN** the system SHALL zoom to the explicit local target handles and report `focus.source` as `target_handles`

#### Scenario: Capture prefers repair plan target bbox
- **WHEN** a capture is requested with a `repair_plan.target_bbox` and no usable local target handles
- **THEN** the system SHALL zoom to the repair target bbox and report `focus.source` as `repair_plan.target_bbox`

#### Scenario: Capture focuses from execution summary handles
- **WHEN** a capture is requested with an execution summary containing non-empty `created_handles` and no local repair target
- **THEN** the system SHALL zoom to the extents of those handles before capture and report `focus.source` as `execution_summary.created_handles`

#### Scenario: Capture focuses from explicit bbox
- **WHEN** a capture is requested with an explicit target bbox and no usable handles
- **THEN** the system SHALL zoom to that bbox before capture and report `focus.source` as `explicit_bbox`

#### Scenario: Precision capture does not silently zoom full drawing
- **WHEN** a precision capture is requested but the provided handles and bbox cannot produce a valid focus target
- **THEN** the system SHALL report `focus.status` as `focus_target_unavailable` or `failed` instead of silently using full drawing extents

### Requirement: Low-disruption AutoCAD window capture
The system SHALL preserve the user's desktop layout by default while capturing the AutoCAD client area.

#### Scenario: Default capture avoids foreground stealing
- **WHEN** a task-scoped preview capture runs without an explicit force-foreground request
- **THEN** the system SHALL avoid `SetForegroundWindow`, capture by AutoCAD client-window `PrintWindow` when possible, and report `foreground_first=false`

#### Scenario: Foreground fallback is explicit
- **WHEN** the default AutoCAD client-window capture path fails and a foreground retry is used
- **THEN** the system SHALL report `foreground_fallback=true` and include the fallback reason

### Requirement: Visual preview evidence boundary
The system SHALL identify screenshot evidence as visual aid only and keep geometry verification tied to CAD readback.

#### Scenario: Preview payload records visual aid role
- **WHEN** a runner records a generated CAD screenshot
- **THEN** the runner SHALL record `visualPreview.role` as `visual_aid_only`

#### Scenario: Screenshot does not replace readback evidence
- **WHEN** a screenshot is captured successfully but created-handle readback is missing or failed
- **THEN** the system SHALL NOT treat the task as geometry verified based on the screenshot alone

### Requirement: Runner preview integration
First-batch CAD training and review runners SHALL use the shared task-scoped preview contract when they request a screenshot.

#### Scenario: Foundation training writes preview payload
- **WHEN** foundation remaining training runs with `capture_preview=true`
- **THEN** the report SHALL include a non-empty `visualPreview` payload and a preview path or explicit preview failure reason

#### Scenario: Single-item repair preview uses repaired scope
- **WHEN** a runner captures a preview after repairing one item inside a multi-item test
- **THEN** the runner SHALL pass the repaired item's target handles or target bbox to the shared preview contract instead of relying only on the whole-run execution summary

#### Scenario: Visual CAD review capture uses execution summary
- **WHEN** visual CAD review is invoked with `capture=true` and an execution summary path
- **THEN** the capture SHALL use that execution summary for focus before writing the screenshot

#### Scenario: Cross-machine reverify capture uses task summary when available
- **WHEN** cross-machine reverify executes a plan and then captures an AutoCAD preview
- **THEN** the capture command SHALL pass the generated execution summary to `render_preview.py`
