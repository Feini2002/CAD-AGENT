## 1. Protocol Contract

- [x] 1.1 Add OpenSpec proposal, design, tasks, and capability spec for system asset sedimentation.
- [x] 1.2 Update repository docs/rules so "沉淀 XX 资产" has a default action.

## 2. Core Implementation

- [x] 2.1 Add failing tests for category resolution, repeated sofa sedimentation, and registry updates.
- [x] 2.2 Implement `core.assets.system_asset_sedimentation`.
- [x] 2.3 Add CLI `scripts/sediment_system_asset.py`.

## 3. Initial Packages

- [x] 3.1 Add `libraries/system_library/registry.json`.
- [x] 3.2 Add drawing-standard package seed contract.
- [x] 3.3 Add sofa package seed contract.

## 4. Verification

- [x] 4.1 Run targeted unit tests.
- [x] 4.2 Run CLI smoke against a temporary project root.
- [x] 4.3 Run training workbench sync / agent check if docs or system library sources changed.
- [x] 4.4 Update status/changelog/issues with evidence and boundaries.

## 5. V2 Hardening

- [x] 5.1 Add lifecycle, retrieval, layout, conflict, feedback, and verify-gate tests.
- [x] 5.2 Implement lifecycle statuses, explicit conflict policies, versioned variants, native layout plans, retrieval contracts, and feedback loops.
- [x] 5.3 Implement metadata-only package verification and expose it through the CLI.
- [x] 5.4 Upgrade seed system-library packages and registry rows to the hardened contract.
- [x] 5.5 Refresh docs/status and rerun OpenSpec, unit, doc governance, and workbench sync gates.

## 6. Source Boundary / Anti-Contamination Gate

- [x] 6.1 Add failing tests for object source boundaries, forbidden broad exports, style export, and CLI export manifests.
- [x] 6.2 Implement `assetKind`, `sourceBoundary`, `exportManifest`, and `antiContamination` contracts.
- [x] 6.3 Reject block export from whole preview/modelspace/screen/training-panel sources.
- [x] 6.4 Upgrade seed packages so drawing standards use `style_export` and sofa seed remains `metadata_only`.
- [x] 6.5 Refresh docs/status and rerun unit, OpenSpec, doc governance, and workbench gates.
