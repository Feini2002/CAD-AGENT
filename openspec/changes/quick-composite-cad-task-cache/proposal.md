## Why

The sofa dimension test proved that the CAD result can be correct while the full agent path is too slow for lightweight composite work. The reusable need is not "sofa annotation"; it is a generic current-DWG fast path for requests like "find this object and annotate its bbox dimensions".

## What Changes

- Add a current-DWG block cache that stores lightweight block reference facts: `handle`, `block_name`, `layer`, `bbox`, `size`, `aspect_ratio`, document identity, and timing metadata.
- Add a generic quick composite task entry for `find_and_annotate_bbox_dimensions`.
- Reuse visual-first retrieval and bbox dimension annotation actions without hard-coding sofa-specific behavior.
- Emit one report that separates target retrieval evidence, action plan, CAD readback, timing, and safety.
- Keep writes preview-only: only annotation entities may be written to `CODEX_PREVIEW`; target blocks and formal layers are not modified.

## Capabilities

### New Capabilities

- `quick-composite.find_and_annotate_bbox_dimensions`: Find a target block in the active DWG using visual/semantic signals and annotate its bbox width/depth through a preview-layer CAD action.
- `visual-retrieval.current_dwg_block_cache`: Reuse a current-DWG block manifest so repeated light tasks avoid unnecessary full modelspace snapshots when the cache is valid.

### Modified Capabilities

- `visual-cad-asset-retrieval`: Candidate sources may come from a cache manifest or live snapshot, but CAD readback remains required for final action claims.

## Impact

- New generic core module for current-DWG block cache.
- New generic quick task module and CLI.
- Existing sofa-specific script remains as a compatibility/demo entry, but the reusable path is object-agnostic.
- Unit tests cover cache reuse, generic dimension action planning, and quick composite reporting.
- No registry/table C writeback and no cross-file gallery indexing in this change.
