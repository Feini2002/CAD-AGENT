# Current Module Boundaries

Change marker: `ARCH-BOUNDARY-HARDENING-01`

This snapshot is the boundary contract for the architecture slimming package. It does not replace `CORE_RESTRUCTURE_PLAN.md`; this document is **not a second roadmap**. It only says where code belongs today and what evidence is required before code moves between layers.

## Boundary Buckets

### Stable Core

Stable Core is reusable platform behavior that can be called by multiple scenarios without carrying case assumptions.

Current stable Core examples:

- `core/plan_engine/`, `core/execution/`, `core/safety/`, and `core/schemas/`: plan validation, execution boundaries, safety rules, and shared schemas.
- `core/orchestrator/`: request context, route audit, activation policy, and workflow dispatch contracts.
- `core/assets/raw_intake.py`, `core/assets/retrieval.py`, and `core/assets/promotion_gate.py`: asset-intelligence entry points, as long as raw references stay evidence input and promoted assets stay gated.
- `core/verification/`: stable verification gates, but with a split map below because report contracts, runners, registry writeback, and visual audit are now too close together.

Stable Core rule: code can live here only when it has clear inputs/outputs, tests or machine checks, no project-path dependency, and no hidden training-case assumption.

### Training Experiments

Training Experiments are useful for learning, evaluation, and repeated case loops, but they are not automatically platform behavior.

Current training experiment examples:

- `core/training/`: training scaffolding and repeatable training utilities.
- `agents/residential/`: scene preference and vocabulary layer for the current residential training focus.
- `docs/training/`: training process, feedback protocol, and CAD common-sense upgrade notes.
- `capability-map.html`, `capability-map-data.js`, and `scripts/build_capability_map_data.py`: operator-facing capability map surface. It is a dashboard and data generator, not the source of truth for Table C.

Training Experiment rule: code can graduate only after it has a stable contract, no hidden dependency on one case folder, and a test or audit command that proves the behavior outside one run.

### Case-Only

Case-Only code is allowed to be practical, local, and even messy while a training case is being learned. It must not be treated as Core just because it is useful.

Current case-only examples:

- `projects/<case>/runs/`: one-off renderers, vector redraw scripts, visual audit helpers, and round-specific evidence.
- `projects/residential_sofa_2seat_20260528/runs/`: the current best candidate area for extracting reusable sofa render/audit lessons, but not a Core module yet.
- `output/test_artifacts/` and `output/validation_runs/**`: evidence output, not reusable source code.

Case-Only rule: local logic stays local until it has survived repeated rounds, has a neutral schema, and has a documented promotion gate.

## Verification Split Map

`core/verification/` remains a stable Core area, but future slimming should move by responsibility, not by line count alone.

| Responsibility | Target boundary | Belongs here |
| --- | --- | --- |
| `report contract` | report schemas and validators | Required fields, evidence paths, status values, and failure messages for verification reports. |
| `runner` | execution orchestration | Command composition, fixture setup, report emission, and deterministic test entry points. |
| `registry writeback` | registry mutation gate | Updating capability registries only after evidence gates pass. |
| `visual audit` | visual/readback assessment | Screenshot/readback comparison, visual scene summaries, and geometry-audit conclusions. |
| CAD/session safety | CAD boundary helpers | `CODEX_PREVIEW`, no-save defaults, capture strategy, and fallback safety notes. |

Next split preference: start with report contract helpers or visual audit helpers, because they are easiest to test without touching real CAD execution.

## Capability Map Split Map

The capability map should stop growing as one HTML/application/data blob. Its responsibilities are:

| Responsibility | Current pressure | Target boundary |
| --- | --- | --- |
| `data generator` | `scripts/build_capability_map_data.py` is already large | Build normalized capability view data only. |
| sync runner | HTML snapshots can become stale after training / registry / coverage changes | `scripts/sync_training_workbench.py` refreshes coverage, rebuilds data, and runs the workbench agent check. |
| agent check | dashboard drift is hard to spot manually | `scripts/run_training_workbench_agent_check.py` validates source refs, responsible agents, Table C snapshot alignment, and page sync affordances. |
| normalized view model | mixed with generator details | Small JSON/JS contract that the page consumes. |
| `page shell` | `capability-map.html` carries layout, copy, and rendering | Keep HTML/CSS/interaction shell separate from data. |
| `display configuration` | labels, group order, and evidence policy are embedded | Move operator-facing grouping and labels to a small config layer. |
| evidence boundary | dashboard can be mistaken for proof | Repeat that Table C only trusts machine coverage JSON and real CAD evidence gates. |

This split must not create another capability source of truth. The page displays current state; it does not certify CAD ability.

## Object Asset Trial

First candidate: `projects/residential_sofa_2seat_20260528`.

Trial route:

`raw reference -> knowledge summary -> candidate -> executable check -> system asset -> CAD_PLAN -> readback`

Why this object family first:

- It has recent residential training rounds and user feedback.
- It already exposed direction semantics, line cleanup, and visual/CAD readback concerns.
- It is concrete enough to test an object-family asset loop without inventing a new scenario.

Evidence boundary:

- Raw files remain reference input.
- A candidate is not a system asset.
- A system asset requires an executable check, system-library write location, `CAD_PLAN` use, and readback evidence.
- This trial does not change Table C until the normal registry and coverage gates pass.

## Case-Run Promotion Gate

Reusable code under `projects/.../runs` can move to `core/training/`, `core/style_engine/`, or another shared module only when all checks below are true:

1. It was used in at least two validated rounds, or it fixed one user-confirmed failure with a repeatable test.
2. Inputs are neutral schema/data, not hard-coded project paths.
3. Outputs are deterministic enough for unit tests, audit reports, or visual comparison.
4. It does not claim real CAD geometry unless it has `CAD_PLAN`, validate, dry-run, `CODEX_PREVIEW`, created handles, and readback evidence.
5. The destination module has a clear owner: training utility, style rule, verification audit, or stable Core behavior.

Promotion default: copy the smallest proven helper first, then delete or deprecate case-only duplication only after tests prove the shared helper covers the old behavior.

## Operating Notes

- OpenSpec change: `openspec/changes/architecture-boundary-hardening-01/`.
- Mainline remains: `CORE_RESTRUCTURE_PLAN.md`.
- This package is a boundary-hardening pass, not a full verification or capability-map rewrite.
- Large-file audits should still run, but line count is a signal for split planning rather than an automatic migration rule.
