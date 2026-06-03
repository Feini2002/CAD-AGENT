## Context

`core/verification/render_preview.py` already supports AutoCAD window capture and execution-summary-based focus, but the behavior is not consistently used by training and verification runners. Some entry points only zoom inside CAD, some capture the current AutoCAD window without `execution_summary`, and some record preview metadata without producing an image. In large DWG files this makes visual review noisy because a failed focus can fall back to the whole drawing.

The change must preserve existing CAD safety rules: real geometry evidence comes from created-handle readback, screenshots are only visual aids, current DWGs are not saved, and formal layers are not modified.

## Goals / Non-Goals

**Goals:**

- Make task-scoped screenshot focus explicit and machine-readable.
- Preserve the user's CAD / IDE layout by default and avoid stealing foreground unless required by a failed capture path.
- Use `execution_summary.created_handles` as the primary focus source, with explicit bbox support as a fallback source.
- Use explicit local repair targets before whole-run handles, so a one-item repair inside a ten-item test captures only the repaired item.
- Prevent precise preview requests from silently zooming to full drawing extents.
- Connect the first batch of high-value runners to the same preview contract.

**Non-Goals:**

- No change to CAD geometry verification or Table C scoring.
- No current DWG save, formal layer edit, global cleanup, or destructive operation.
- No AutoCAD internal viewport-only crop, temporary highlight overlay, multi-display DPI correction, or per-part screenshot fan-out in this first batch.

## Decisions

1. **Use one task-scoped preview contract.**

   `render_preview` will normalize capture output into a `visualPreview`-shaped payload containing `role`, `status`, `mode`, `occlusion_safe`, and nested `focus`. Runners can store that payload directly instead of inventing local preview metadata.

   Alternative considered: leave runner-specific fields. That preserves old shapes but keeps the current inconsistency.

2. **Focus targets are explicit.**

   The focus source order is explicit `target_handles`, then `repair_plan.target_handles`, then `repair_plan.target_bbox`, then explicit `target_bbox`, then `execution_summary.created_handles`, then summary bbox fields. If neither is available, the focus result is `not_run` or `focus_target_unavailable`. A precision-oriented capture does not silently call `ZoomExtents`.

   Alternative considered: keep `ZoomExtents` as a friendly fallback. That is exactly what hides failures in files with many unrelated blocks.

3. **Default capture stays low-disruption.**

   The default path restores AutoCAD only if minimized, zooms through COM, captures by `PrintWindow`, and reports `occlusion_safe=true`. Foreground fallback is reserved for failure recovery and must be visible in the payload.

   Alternative considered: always bring AutoCAD to foreground. That solves some screenshots but interrupts the user's desktop and conflicts with the existing split-screen rule.

4. **First batch runner integration is narrow.**

   The first implementation covers the current training mainline and low-cost existing capture sites: foundation remaining training, visual CAD review, and cross-machine reverify. Dense table / dimension / visual smoke fan-out can follow once the contract is stable.

## Risks / Trade-offs

- **PrintWindow can return blank GPU content** -> Add a lightweight image validity check and expose failure classification before foreground fallback.
- **Multiple AutoCAD windows can mismatch COM document and captured window** -> Record document/window metadata now; strict target binding can be extended later.
- **Fake CAD tests cannot render real screenshots** -> Use dependency-injected capture functions and fake image objects in unit tests.
- **Runner reports may gain new fields** -> Keep old artifact paths and add structured `visualPreview` without removing existing evidence fields.
- **Local repair target can be missing from CAD after replacement** -> Report missing target handles and allow callers to pass replacement handles or repair bbox for the final capture.

## Migration Plan

1. Add tests for focus source reporting, no silent full-extents fallback, and runner visual preview payloads.
2. Implement `render_preview` helpers and CLI parameter wiring.
3. Update first-batch runners to call the shared preview helper or record a clear skipped/failed preview state.
4. Run focused unit tests and OpenSpec validation.

## Open Questions

- Whether later batches should create per-part screenshots for complex symbols remains deferred.
- Strict multi-window document binding remains deferred until the first contract is stable.
