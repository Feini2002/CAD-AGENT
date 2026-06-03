## 1. Contract Tests

- [x] 1.1 Add render preview tests for local target handle priority, repair bbox fallback, execution-summary focus metadata, explicit bbox fallback, layer forwarding, and no silent full-extents fallback.
- [x] 1.2 Add runner tests proving visual CAD review and cross-machine reverify pass execution summaries into task-scoped capture.
- [x] 1.3 Add foundation training tests proving `capture_preview=true` records structured `visualPreview` and preview path or failure reason.

## 2. Core Preview Implementation

- [x] 2.1 Extend `render_preview` focus helpers to normalize target handles, repair plan targets, execution summary handles, explicit bbox sources, and return machine-readable focus metadata.
- [x] 2.2 Wire CLI/API layer, target handles, repair plan, and bbox parameters into task-scoped focus.
- [x] 2.3 Add capture output normalization with `visual_aid_only`, occlusion-safe mode, foreground fallback, and failure classification.

## 3. Runner Integration

- [x] 3.1 Update visual CAD review to use `prepare_autocad_for_capture` when capture is requested with an execution summary.
- [x] 3.2 Update cross-machine reverify preview capture command to pass the generated execution summary.
- [x] 3.3 Update foundation remaining training to write a focused preview image and structured `visualPreview` when preview capture is enabled.

## 4. Verification

- [x] 4.1 Run focused unit tests for render preview and first-batch runner integrations.
- [x] 4.2 Run OpenSpec strict validation for the new change.
- [x] 4.3 Update OpenSpec task checkboxes and summarize any remaining deferred follow-up scope.
