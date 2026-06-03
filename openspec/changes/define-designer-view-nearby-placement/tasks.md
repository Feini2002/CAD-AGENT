## 1. Contract And Fixtures

- [x] 1.1 Define `CAD_VIEW_CONTEXT` and `placement_resolution` schemas or typed contracts with viewport bbox, visible entity summaries, anchor source, candidate slots, selected slot, checked, not_checked, and assumptions.
- [x] 1.2 Add no-CAD fixtures for selected-handle, recent-handle, visible-cluster, no-viewport, crowded-viewport, and direction-word nearby placement cases.
- [x] 1.3 Update CAD plan generation conventions so vague nearby phrases must reference a deterministic placement resolution before execution.

## 2. Nearby Resolver

- [x] 2.1 Implement focus anchor selection with priority for explicit target, selected handles, visible recent handles, visible focus cluster, then preview content cluster.
- [x] 2.2 Implement candidate slot generation around the anchor for right, left, top, bottom, and diagonal directions.
- [x] 2.3 Implement candidate scoring using viewport containment, distance to anchor, collision status, spacing readability, and user direction words.
- [x] 2.4 Return `needs_confirmation` with failed candidate reasons when no nearby candidate fits instead of producing a far-away fallback point.

## 3. CAD Context And Execution Integration

- [x] 3.1 Add a read-only AutoCAD context collector for current viewport bounds, selected handles when available, visible entity bbox summaries, and existing `CODEX_PREVIEW` entity summaries.
- [x] 3.2 Re-read recent created handles before anchor use and fall back cleanly when handles were moved, deleted, exploded, or are outside the current viewport.
- [x] 3.3 Wire the resolver into a preview-only quick trial path that can draw a simple test object from a nearby phrase and emit the resolution report.
- [x] 3.4 Ensure draw-time execution uses a deterministic `base_point` and does not depend on free-form natural language inside the executor.

## 4. Verification

- [x] 4.1 Add unit tests for all no-CAD resolver fixtures and anchor priority rules.
- [x] 4.2 Add negative tests proving missing viewport context, full viewport, missing readback, and out-of-original-viewport placement cannot pass nearby proof.
- [x] 4.3 Add dry-run checks that require deterministic placement data for nearby phrases.
- [x] 4.4 Add a real CAD smoke test that writes only to `CODEX_PREVIEW`, reads created handles / bbox, and verifies the bbox against the pre-draw viewport.

## 5. Documentation And Agent Rules

- [x] 5.1 Update the CAD Designer Agent or pipeline rules so "旁边 / 附近" routes through designer-view nearby placement instead of direct absolute placement.
- [x] 5.2 Update status / changelog / issues only after implementation changes land, including evidence boundary and any AutoCAD COM limitations discovered.
- [x] 5.3 Document the user-facing delivery wording: successful quick trials prove current-view nearby placement only, not object-family mastery, construction drawing accuracy, or table C improvement.

