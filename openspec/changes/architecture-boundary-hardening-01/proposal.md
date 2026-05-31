## Why

Core has reached the point where stable reusable modules, training experiments, and case-local code are beginning to blur. This change establishes a small architecture slimming and boundary-hardening package so future refactors can happen deliberately instead of turning `core/` into a catch-all area.

## What Changes

- Add a current module-boundary snapshot that classifies stable Core, training experiments, and case-only code.
- Define split contracts for `core/verification/` so report contracts, runners, registry writeback, and visual audit responsibilities no longer keep accumulating in the same files.
- Define a split contract for the capability map so data generation, page shell, display configuration, and evidence boundaries are separate concerns.
- Choose the first object-family asset closed-loop trial and document the raw reference -> knowledge summary -> candidate -> executable check -> system asset -> `CAD_PLAN` -> readback route.
- Define migration gates for reusable render/audit logic currently living under `projects/.../runs/`.
- Add tests that guard the new boundary snapshot and keep this OpenSpec change scoped to its package contract.
- No **BREAKING** changes are introduced in this package.

## Capabilities

### New Capabilities

- `module-boundary-contract`: Architecture contract for classifying stable Core, training experiments, case-only code, and promotion gates between them.

### Modified Capabilities

- None.

## Impact

- Affects documentation under `docs/architecture/`, current status/changelog records, and OpenSpec change artifacts.
- Adds focused repository tests for the boundary snapshot.
- Does not change CAD execution behavior, registry semantics, Table C values, or real CAD capability claims.
