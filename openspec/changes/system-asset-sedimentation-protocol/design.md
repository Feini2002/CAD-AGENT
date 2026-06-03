## Context

The repository already separates `standard_cad_library_raw`, `libraries/reference_library`, and `libraries/system_library`. The missing piece is a default promotion path for user-approved reusable assets created during training or real CAD work.

This change makes the path explicit. It does not try to solve every CAD-native operation in one step. The first implementation records where the CAD-native asset belongs and how to find/apply it later; real DWG insertion or block definition export can be implemented behind the same package contract later.

## Goals / Non-Goals

**Goals:**

- Treat "沉淀 XX 资产" as a first-class workflow.
- Store promoted assets under deterministic category folders in `libraries/system_library`.
- Keep a category-local contract (`assets.json`) and a global registry (`libraries/system_library/registry.json`).
- Reserve a native CAD library path per category, such as `sofa_assets.dwg` or `standard_assets.dwg`.
- Record enough metadata to answer "when should this be used?" through aliases, use cases, tags, and evidence refs.
- Record lifecycle status, retrieval fields, native DWG layout plans, versioning/conflict policy, feedback references, and metadata verification results.

**Non-Goals:**

- No automatic saving of the active DWG.
- No destructive edits or deletion of preview/formal entities.
- No geometry extraction from arbitrary handles in this package.
- No table C registry writeback.
- No cross-file embedding index.

## Decisions

1. **Use four responsibilities, not fixed file counts.**

   Every system asset package must have a machine contract, a native CAD asset location, an application/verification tool contract, and a global registry entry. Simple packages may use one JSON file and shared scripts; complex packages may have several files.

2. **Category folders are stable API.**

   `furniture.seating.sofas` maps to `libraries/system_library/furniture/seating/sofas/`. Future sofa assets append to that package instead of scattering one folder per sofa.

3. **Native DWG may be registered before it exists.**

   The protocol can create the package contract and reserve `sofa_assets.dwg` before a later CAD-native export step writes the file. Reports must say `nativeDwgExists=false` when the native file is only reserved.

4. **Registry drives future retrieval.**

   The global registry stores `assetId`, `category`, `packagePath`, `contractPath`, `nativeDwg`, `aliases`, `useWhen`, and evidence refs. Agents should consult it before falling back to raw/reference libraries.

5. **Lifecycle separates order from capability.**

   `candidate` means the asset is recorded but not yet stable; `systemized` means it has reusable contract/prompt/check evidence; `verified` is reserved for assets with reuse evidence; `deprecated` keeps old assets discoverable without preferred use. A newly written JSON row is not automatically a verified CAD asset.

6. **Native layout is planned before native export.**

   The contract records a deterministic grid slot in the category DWG, so sofa A/B/C can accumulate in `sofa_assets.dwg` without layout ambiguity. This is still a layout plan until a later explicit CAD export writes or updates the DWG.

7. **Conflicts are explicit.**

   Reusing an asset id with different dimensions or block name uses one of three policies: update in place, reject, or create a variant such as `_v2`. Variant rows point back to the original through `versioning.derivedFromAssetId`.

8. **Verification is metadata-only until CAD readback exists.**

   `verify_system_asset_package` checks repository contracts, registry rows, lifecycle/retrieval/layout/versioning/feedback fields, and native existence flags. It deliberately keeps native geometry reuse and insertion replay in `notChecked`.

## Verification

- Unit tests cover category path resolution and native DWG naming.
- Unit tests cover repeated sofa asset sedimentation into the same package contract.
- Unit tests cover global registry updates and idempotent updates.
- CLI smoke with fake metadata writes package files into a temporary project root.
- Unit tests cover lifecycle/retrieval/layout/feedback fields, conflict rejection and variant creation, and metadata-only package verification.
- CLI `--verify` checks package metadata without writing CAD or claiming native geometry reuse.
