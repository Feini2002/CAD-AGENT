## ADDED Requirements

### Requirement: User-approved asset sedimentation uses a four-part system package

When the user explicitly asks to沉淀 a reusable CAD asset, the agent SHALL create or update a system-library package containing:

- a machine-readable asset contract,
- a native CAD asset location,
- an application/verification tool contract,
- and a global registry entry.

#### Scenario: Sofa assets accumulate in one category package

- **WHEN** the user asks to沉淀 sofa A and later sofa B
- **THEN** both assets are registered under the `furniture.seating.sofas` package
- **AND** both point to the same category native DWG path unless the user asks for a separate library.

### Requirement: System asset registry declares when assets should be used

The global system asset registry SHALL record searchable aliases, use cases, category, package path, contract path, native CAD path, and evidence refs for each promoted asset.

#### Scenario: Retrieval can choose the sofa package

- **WHEN** a future request mentions a sofa alias or use case
- **THEN** the registry entry gives the agent a stable package and native DWG location to consult before falling back to reference-only sources.

### Requirement: Sedimentation does not save or mutate active CAD by default

The first sedimentation protocol implementation SHALL write repository contracts and registry metadata only, unless the user explicitly approves a native CAD write/export step.

#### Scenario: Native DWG is only reserved

- **WHEN** a category native DWG path is registered but the file does not exist yet
- **THEN** the report marks `nativeDwgExists=false`
- **AND** does not claim CAD-native export has completed.

### Requirement: System assets carry lifecycle and promotion gates

Each sedimented asset SHALL record a lifecycle status from `candidate`, `systemized`, `verified`, or `deprecated`, plus the allowed statuses and promotion gate evidence expected before the asset is treated as stable reusable capability.

#### Scenario: Newly sedimented sofa remains candidate

- **WHEN** a sofa package seed is registered without a native DWG export or reuse verification
- **THEN** the asset lifecycle status is `candidate`
- **AND** the verification status remains `metadata_only`.

### Requirement: System assets expose retrieval, layout, versioning, and feedback contracts

Each sedimented asset SHALL include searchable retrieval fields, a native DWG layout plan, versioning metadata, and feedback loop references so future reuse can find, place, update, or repair the asset without relying on memory.

#### Scenario: Sofa A and sofa B share a native library layout

- **WHEN** sofa A and sofa B are registered in `furniture.seating.sofas`
- **THEN** each asset has a `native.layoutPlan` slot in the same category DWG
- **AND** registry rows expose retrieval aliases, scenario tags, verification status, lifecycle status, and layout plan.

### Requirement: Conflicting sedimentation is explicit

When an existing asset id is sedimented with materially different dimensions or block name, the agent SHALL follow an explicit conflict policy: update the existing asset, reject the change, or create a versioned variant.

#### Scenario: User wants a variant instead of overwriting

- **WHEN** `conflict_policy=new_variant` is used for an existing sofa id with different dimensions
- **THEN** the new row receives a deterministic variant id such as `_v2`
- **AND** `versioning.derivedFromAssetId` points back to the original asset.

### Requirement: Verification distinguishes metadata readiness from CAD geometry readiness

The package verification entry point SHALL check contract, registry, lifecycle, retrieval, layout, versioning, feedback, and native existence flags, but SHALL NOT claim native CAD geometry reuse unless a later CAD readback/export gate proves it.

#### Scenario: Metadata package passes while native DWG is absent

- **WHEN** `scripts/sediment_system_asset.py --verify --category furniture.seating.sofas` runs on a package whose native DWG is only reserved
- **THEN** the report can pass the metadata contract
- **AND** `notChecked` includes native DWG geometry and CAD insertion replay.

### Requirement: Block export requires an explicit source boundary

Object assets SHALL NOT be prepared for block export from broad or ambiguous sources such as the whole modelspace, whole `CODEX_PREVIEW`, current screen, all visible objects, a training panel, or a global preview bbox. Block export SHALL require selected handles, created handles, active DWG handles, an explicit bbox, or a named block boundary.

#### Scenario: Unclear sofa source remains metadata only

- **WHEN** a sofa asset is sedimented from manual metadata without selected handles, created handles, explicit bbox, or named block
- **THEN** `exportManifest.exportMode` is `metadata_only`
- **AND** `antiContamination.decision` defers export until a precise source boundary exists.

#### Scenario: Whole preview cannot become a block

- **WHEN** a block export is requested from `whole_codex_preview`
- **THEN** the command rejects the export request
- **AND** does not write a misleading block export manifest.

### Requirement: Style assets are not block assets

Drawing-standard assets SHALL use style export semantics, not block export, unless the user separately asks to sediment a visual sample block.

#### Scenario: Lineweight standard uses style export

- **WHEN** a lineweight/linetype standard is sedimented under `drawing_standards.basic`
- **THEN** `exportManifest.assetKind` is `style_standard`
- **AND** `exportManifest.exportMode` is `style_export`
- **AND** a block export request is rejected.
