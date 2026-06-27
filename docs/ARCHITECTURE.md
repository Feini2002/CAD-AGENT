# Architecture

CAD Agent is a small Python package with explicit boundaries:

- `domain/`: immutable contracts for briefs, scenes, patches, receipts, drawings, and verification.
- `planning/`: object catalog loading, placement, candidate scoring, relation solving, and scene compilation.
- `policy/`: transaction and safety checks before execution.
- `adapters/`: fake backend for deterministic tests and `AutoCadBackend` for an already-open AutoCAD document.
- `verification/`: readback, geometry, and relation checks after execution.
- `tools/`: repository checks and acceptance scripts.

The core flow is:

1. User request becomes `SceneSpec`.
2. `SceneSpec` plus `DrawingSnapshot` compiles into `CadPatch`.
3. `CadPatch` passes transaction policy.
4. Backend writes only `CODEX_PREVIEW`.
5. Created handles are read back.
6. Verification decides pass, repairable fail, or blocked.

The package intentionally does not import old-system modules. Historical evidence, training assets, previous project outputs, and old orchestration code live only in the archive source.
