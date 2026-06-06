## Why

The current training workbench is useful as a static capability matrix, but the CAD Agent training system has outgrown a table-first page. The user now needs a durable flightdeck that answers what to train next, which real agents are involved, whether evidence is closed, and which gates block safe delivery.

This change matters now because the repository already has V2 training maps, Agent contracts, Prompt addenda, model traces, A-to-A gates, data-bloat governance, and training fact sources. Keeping them in parallel tabs makes the system harder to operate and easier to over-claim.

## What Changes

- Introduce a training flightdeck view model that keeps `capability-map-data.js` as a derived static snapshot while separating facts, indices, and UI views.
- Add a command-center first screen for next training candidates, sync health, gateboard status, active runs, evidence boundary, and the current CAD Designer Agent focus.
- Upgrade the training map from a table-first surface into a batch / stage / dependency-oriented route map with table scan as a secondary mode.
- Add an Agent system graph model for CAD Designer Agent, pipeline agents, scene agents, Prompt Packs, hard gates, Tool Contracts, run packages, and evidence artifacts.
- Add an evidence center that distinguishes active fact sources, archived history, derived snapshots, CAD readback, visual aids, model review, user feedback, and not-checked items.
- Add run / trace / gate observability that helps diagnose agent dispatch, Prompt Pack traces, tool intent risk, closeout blockers, and downstream evidence without treating traces as CAD proof.
- Extend workbench sync and agent-check gates so the flightdeck cannot show all-green status when encoding, source health, data-bloat, evidence closure, Table C boundary, or A-to-A gates are blocked.
- Keep the current root `capability-map.html` and `capability-map-data.js` entrypoints compatible while allowing a staged split into focused `workbench/` frontend files and `core/training_workbench/` data builders.

Non-goals:

- This change does not promote Table C, prove new CAD geometry capability, or mark any training item passed by UI display alone.
- This change does not make the browser a writable source of truth.
- This change does not require a framework migration in the first implementation slice.
- This change does not replace training reports, coverage JSON, Agent memory, Prompt addenda, or created-handle readback as fact sources.

## Capabilities

### New Capabilities

- `training-workbench-flightdeck`: Operator-facing flightdeck behavior for command center, training map, Agent graph, evidence center, trace view, failure loop, and fact-source governance.
- `workbench-data-contract-v3`: Derived snapshot contract that separates facts, indices, view models, source health, evidence bundles, gateboard status, and compatibility boundaries.
- `agent-system-observability`: Agent / Prompt Pack / Tool Contract / Trace observability model for real dispatch, hard gates, model/tool boundaries, and learning feedback.

### Modified Capabilities

- None. The repository currently has no stable OpenSpec specs under `openspec/specs/`; this change introduces new scoped capabilities rather than modifying an existing spec.

## Impact

- Affected frontend entrypoints: `capability-map.html`, `capability-map-data.js`, and proposed `workbench/**` split files.
- Affected data generation: `scripts/build_capability_map_data.py`, `scripts/sync_training_workbench.py`, `scripts/run_training_workbench_agent_check.py`, and proposed `core/training_workbench/**` modules.
- Affected tests: `tests/core/test_training_workbench_sync.py` and new focused tests for schema v3, flightdeck view models, source health, Agent graph, and evidence bundles.
- Affected governance: `CORE_RESTRUCTURE_PLAN.md`, `docs/training/training-sources.json`, and status / handoff documentation only when implementation changes active order, evidence boundary, or sync behavior.
- No external dependency is required for the first slice; browser verification should use the existing local static workbench flow.
