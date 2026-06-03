## Context

Current visual retrieval can find the sofa block quickly after `snapshot_modelspace`, and bbox dimension annotation can write two preview dimensions with handle readback. The slow part in lightweight user requests is avoidable orchestration overhead and repeated full snapshots.

This change introduces a small foundation for current-DWG quick composite tasks. It does not attempt to solve full gallery search or image embedding. It turns the successful sofa workflow into a generic reusable path.

## Goals / Non-Goals

**Goals:**

- Build a current-DWG block cache manifest that can be reused when document identity matches.
- Let quick composite tasks rank candidates from cache when available, falling back to live snapshot when needed.
- Provide a generic `find_and_annotate_bbox_dimensions` action that works for any block reference with a bbox.
- Keep execution preview-only and report evidence boundaries clearly.

**Non-Goals:**

- No cross-DWG thumbnail/embedding index.
- No formal-layer annotation.
- No saving, deleting, replacing, or editing target blocks.
- No table C capability registry writeback.

## Decisions

1. **Cache only lightweight block facts.**

   The cache stores normalized block reference rows and metadata. It does not store detailed line/arc construction or screenshots. This keeps it fast, portable, and safe.

2. **Use cache as candidate source, not proof.**

   A valid cache can accelerate candidate ranking. The selected target and created dimensions are still verified by active CAD readback during execution.

3. **Make the action object-agnostic.**

   The bbox dimension action accepts a candidate target and desired axes. Sofa, bed, table, cabinet, and other block-like objects share the same path.

4. **Expose one generic CLI.**

   `scripts/run_quick_composite_task.py` supports `find_and_annotate_bbox_dimensions`; sofa-specific scripts can delegate later, but the new capability is generic.

## Risks / Trade-offs

- Cache staleness can select an outdated handle. Mitigation: cache validity checks document identity and the execution report includes active CAD readback; a missing handle becomes `needs_review` or fallback to live snapshot.
- Generic bbox dimensions may not match domain-specific dimensions such as seat height or clear opening. Mitigation: this action is explicitly bbox width/depth only.
- The first run still needs a live snapshot. Mitigation: repeated commands in the same DWG can reuse the cache.

## Verification

- Unit tests prove cache manifests can be built and reused.
- Unit tests prove quick composite planning is object-agnostic.
- Real CAD self-test runs the generic command against the active sofa DWG and confirms target/readback/dimensions.
