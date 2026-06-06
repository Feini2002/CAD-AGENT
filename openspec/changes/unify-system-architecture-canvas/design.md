# Design: Unify System Architecture Canvas

## Overview

This change introduces a repository-level architecture canvas that absorbs historical CAD Agent modules into one task lifecycle. The work is intentionally deeper than a reporting rename: it reassigns old metrics, training plans, assets, orchestration, model bridge, execution and evidence to stable layers with explicit boundaries.

## Architecture

The new architecture has seven layers:

1. **System entry**: user text, DWG, screenshot, feedback, training commands, asset commands.
2. **Task object**: run packages, task envelopes, cases, training items, asset requests, repair requests.
3. **Decision orchestration**: semantic route, Orchestrator Host, A-to-A contracts, Worker state, bridge, model trigger.
4. **Capability and evidence**: registry, historical table A/B/C, proof coverage, training facts, asset evidence, risks.
5. **Execution tools**: CAD_PLAN, validate, dry-run, Tool Contract, CODEX_PREVIEW, readback, screenshot.
6. **Audit and repair**: geometry audit, visual review, local repair, closeout gate, neighbor protection.
7. **Sedimentation and learning**: learning promotion, Agent memory, rules, system assets, workbench, changelog.

The main lifecycle is:

```text
entry -> task object -> orchestration -> evidence lookup
  -> execution tools -> audit / repair -> sedimentation / learning
```

Every historical module must be reassigned to this lifecycle. The implementation should prefer mapping and adapter changes over deletion.

## Metric Reframe

Old table C values are preserved, but their semantic role changes:

- `Core Proof Coverage`: historical bottom-layer proof coverage from registry and coverage JSON.
- `Agent Task Maturity`: end-to-end maturity of CAD Designer Agent task handling.
- `Project Delivery Readiness`: readiness for complete real project delivery.

The old “真实 CAD 实力 90%” wording is unsafe because users naturally read it as task maturity. The convergence should remove or quarantine this wording from active planning and status paths, while preserving the underlying machine coverage for bottom-layer regression.

## Documentation Updates

The first implementation phase updates:

- `docs/architecture/system-architecture-convergence.md`
- `CORE_RESTRUCTURE_PLAN.md`
- `CORE_CONTEXT_BRIEF.md`
- `CORE_STATUS.md`
- `AGENTS.md`
- `docs/governance/cad-agent-rules.md`
- `docs/planning/任务清单.md`
- `docs/status/current.md`
- `docs/status/changelog.md`
- `docs/status/issues.md`
- `docs/training/README.md`
- `docs/architecture/README.md`

`CORE_RESTRUCTURE_PLAN.md` remains the only active PlanMD. OpenSpec remains the change contract only.

## Script Audit

The next execution pass should inspect these scripts and update only the labels / gates needed to align with the canvas:

- `scripts/run_capability_coverage.py`
- `scripts/build_capability_map_data.py`
- `scripts/sync_training_workbench.py`
- `scripts/run_training_workbench_agent_check.py`
- `scripts/run_doc_governance_audit.py`
- `scripts/run_a_to_a_orchestration_gate_check.py`
- `core/maintenance/doc_governance.py`

The goal is not to delete table C. The goal is to stop active outputs from presenting it as end-to-end true ability.

## Migration Strategy

1. Document the new canvas and plan.
2. Update rules and current status to pause new formal training until convergence is complete.
3. Audit derived displays and scripts for old metric labels.
4. Add or update tests that prevent the old “真实 CAD 实力” wording from reappearing as a primary active status claim.
5. Resume training once status, workbench and scripts all speak the new layered vocabulary.

## Non-Goals

- Do not delete historical evidence, registry rows, coverage JSON, old changelog entries or archive material.
- Do not rewrite CAD execution, model bridge or asset library internals in this first pass unless a label or gate directly violates the canvas.
- Do not claim Agent Task Maturity has improved because the documentation is cleaner.
- Do not run formal CAD training as part of the convergence setup.

## Verification

The convergence pass should be verified with:

- `openspec.cmd validate --all --strict --json --no-interactive`
- `scripts/run_doc_governance_audit.py`
- targeted tests for PlanMD governance and doc governance
- workbench agent check after any workbench generation change
- no real CAD required unless execution scripts are modified
