## Why

Line-type table training exposed a broader platform issue: CAD output quality cannot depend on prompt memory alone. The agent needs a machine-readable semantic rule base that can route natural-language requests, search reusable system assets, guard cross-DWG reuse, audit CAD layout constraints, and feed failures back into the right subsystem.

Without this upgrade, future assets will increase the chance of weak semantic matches, candidate assets being reused as verified assets, style standards being treated as blocks, table layouts self-certifying bad geometry, or Chinese text corruption being caught only after screenshots.

## What Changes

- Add a semantic rules layer for CAD asset reuse, sedimentation, local repair, and line-type table layout constraints.
- Harden cross-DWG system asset reuse with registry encoding preflight, stable candidate ranking, explicit weak/strong match reporting, and strict source readiness fields.
- Add an independent line-type table layout audit that validates visible Chinese text, no-fill constraints, sample containment, adaptive row heights, style diversity, and evidence boundaries from readback data.
- Make the line-type table generator support variable row counts so future tables are not constrained by accidental 24/42-row layouts.
- Update architecture docs, status records, and handoff notes so this becomes a reusable system capability rather than a one-off drawing fix.

## Impact

- New Core semantic rules module under `core/assets/`.
- New line-type table audit module under `core/training/`.
- Updates to `core/assets/system_asset_reuse.py` and `core/training/linetype_table_demo.py`.
- New and updated unit tests for semantic asset routing, registry encoding gates, layout audits, and variable row layouts.
- Documentation and governance updates for future agents.
