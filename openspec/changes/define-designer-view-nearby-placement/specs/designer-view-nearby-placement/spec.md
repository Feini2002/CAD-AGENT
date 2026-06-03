## ADDED Requirements

### Requirement: Designer view context capture
The system SHALL capture or receive a structured CAD view context before resolving vague placement phrases such as "旁边", "附近", "边上", "right beside", or "nearby".

#### Scenario: Current viewport context is available
- **WHEN** a user asks to draw an object "在旁边" while an AutoCAD drawing is open
- **THEN** the system SHALL build a view context containing the current model-space viewport bounds, visible entity bbox summaries, available selected handles, available recent created handles, and the preview layer name.

#### Scenario: Current viewport context is unavailable
- **WHEN** the system cannot read or receive the current viewport bounds
- **THEN** it SHALL mark nearby placement resolution as `blocked` or `needs_confirmation` and SHALL NOT silently place the object in a far global empty area.

### Requirement: Focus anchor selection
The system SHALL select a focus anchor that represents what the designer is currently looking at before computing nearby placement candidates.

#### Scenario: Selected object takes priority
- **WHEN** the view context contains selected handles with readable bboxes
- **THEN** the system SHALL use those selected handles as the focus anchor before considering recent created handles or visible entity clusters.

#### Scenario: Recent created handles are reused only if visible
- **WHEN** recent created handles exist and their readback bboxes intersect the current viewport
- **THEN** the system SHALL allow them to become the focus anchor and SHALL record `anchor_source=recent_created_handles`.

#### Scenario: Fallback to visible focus cluster
- **WHEN** no explicit, selected, or recent visible handles are available
- **THEN** the system SHALL derive a focus cluster from visible CAD entities and SHALL record `anchor_source=visible_focus_cluster`.

### Requirement: Nearby candidate generation
The system SHALL generate nearby candidate slots around the focus anchor and SHALL choose a slot that remains within the original current viewport whenever possible.

#### Scenario: Direction phrase chooses matching side
- **WHEN** the user asks for placement "右边" and the right-side candidate fits within the original viewport without collisions
- **THEN** the system SHALL choose the right-side candidate and produce a deterministic target base point for the CAD plan.

#### Scenario: Vague nearby chooses clean nearest slot
- **WHEN** the user asks for placement "旁边" without a direction and multiple candidate slots fit
- **THEN** the system SHALL choose the highest-scoring clean nearby slot using viewport containment, distance to anchor, collision status, and spacing readability.

#### Scenario: No nearby slot fits
- **WHEN** every candidate slot would fall outside the original viewport or collide with protected visible geometry
- **THEN** the system SHALL return `needs_confirmation` with failed candidate reasons instead of placing the object far away.

### Requirement: Placement resolution evidence
The system SHALL emit a placement resolution artifact that explains how the vague phrase became a CAD coordinate.

#### Scenario: Resolution report is produced
- **WHEN** nearby placement resolves successfully
- **THEN** the report SHALL include the original phrase, viewport bounds before drawing, anchor source, anchor bbox, candidate slots, selected slot, expected target bbox, resolved base point, assumptions, checked items, and not-checked items.

#### Scenario: CAD_PLAN keeps deterministic placement
- **WHEN** a resolved nearby placement is converted into a CAD plan
- **THEN** the CAD plan SHALL contain a deterministic placement base point or a reference to a deterministic placement resolution artifact; execution SHALL NOT depend on free-form natural language at draw time.

### Requirement: Viewport-nearby readback audit
The system SHALL verify created CAD entities against the original viewport and focus anchor after preview execution before claiming that the object was drawn nearby.

#### Scenario: Created object is visible without moving view
- **WHEN** the object is written to `CODEX_PREVIEW` and created handles are readable
- **THEN** the audit SHALL confirm the created bbox is inside or acceptably intersects the original viewport and is within the configured nearby distance from the focus anchor.

#### Scenario: Hidden viewport movement cannot satisfy nearby proof
- **WHEN** the object is outside the original viewport but a later zoom or pan makes it visible
- **THEN** the audit SHALL fail the nearby placement claim because proof is based on the pre-draw viewport.

#### Scenario: Readback is missing
- **WHEN** created handles or their bboxes cannot be read back
- **THEN** the system SHALL report `geometry_verified=false` for the nearby placement claim and SHALL NOT state that the object was accurately drawn beside the anchor.

### Requirement: Preview-only safety boundary
The system SHALL keep designer-view nearby trials preview-only unless the user explicitly approves a broader CAD operation.

#### Scenario: Quick trial nearby draw
- **WHEN** the user asks to try drawing an object nearby without requesting formal drawing modification
- **THEN** the system SHALL write only to `CODEX_PREVIEW`, SHALL NOT save the DWG, SHALL NOT delete user entities, and SHALL NOT modify formal layers.

#### Scenario: Evidence boundary remains explicit
- **WHEN** a nearby placement trial succeeds
- **THEN** the delivery report SHALL state that the evidence proves nearby placement in the current view and SHALL NOT claim object-family mastery, construction drawing accuracy, or table C improvement.
