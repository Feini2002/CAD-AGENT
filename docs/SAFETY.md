# Safety

The active CAD safety contract is preview-only.

Required invariants:

- `target_layer == "CODEX_PREVIEW"`
- `savedCurrentDwg == false`
- operations are scoped to explicit created handles
- rollback deletes only current transaction handles
- readback must confirm layer, handles, entity count, and bounding boxes
- screenshots are optional visual aids, never proof

Blocked effects:

- current DWG save
- formal layer writes
- broad model-space deletion
- modifying nearby non-target handles
- arbitrary AutoLISP execution
- exact prompt routes that bypass planning

Real AutoCAD checks must use an already-open AutoCAD document and must report what was checked and what remains unproven.
