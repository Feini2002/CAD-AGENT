## Why

Current training can prove that a CAD object, style, or standard works in the active DWG, but that does not make it reusable in a new DWG. Users need a reliable command-level expectation: when they say "沉淀这个资产", the agent must promote the current CAD result into a reusable system asset with a CAD-native storage location, a machine-readable contract, an application path, and a discoverable index.

## What Changes

- Define the system asset sedimentation protocol: `contract + native CAD library + tools + registry`.
- Add a Core helper that derives deterministic system-library locations from asset categories such as `furniture.seating.sofas` or `drawing_standards.basic`.
- Add a CLI that can create/update the asset package contract and global registry for a named asset without writing or saving CAD by default.
- Add a starting drawing-standard package and sofa asset package layout so future CAD writes have a fixed place to deposit native `.dwg` / `.dwt` assets.
- Update training/status documentation so future "沉淀 XX 资产" requests trigger this protocol instead of leaving evidence only in the current preview drawing.

## Capabilities

### New Capabilities

- `system-assets.sediment`: Create or update a reusable system asset package and registry entry from explicit asset metadata.
- `system-assets.resolve-location`: Map an asset category to its stable system-library folder and native DWG path.
- `system-assets.registry`: Maintain a global index that tells retrieval and training agents when a system asset should be considered.

### Modified Capabilities

- CAD Designer training rules: user-approved asset sedimentation now requires a system-library registry entry and category package, not only a screenshot or training report.
- Asset retrieval boundary: `libraries/system_library` remains the promoted/self-owned asset source; raw and reference libraries are not treated as system assets.

## Impact

- New Core module under `core/assets/`.
- New CLI under `scripts/`.
- New system-library directories and JSON contracts.
- New tests for category resolution, repeated sofa sedimentation, registry updates, and no-CAD safety boundaries.
- No real CAD save, delete, or formal-layer modification in this change.
