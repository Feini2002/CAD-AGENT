## Context

The repository has already converged on a stable governance model:

- `CORE_RESTRUCTURE_PLAN.md` is the only PlanMD and owns current priorities, decision gates, and exit criteria.
- `docs/planning/任务清单.md` is an execution control surface for training/backlog routing.
- `docs/status/*` records evidence, risks, and historical changes.
- `core/maintenance/doc_governance.py` already enforces several documentation and source-of-truth constraints.

OpenSpec is now initialized at the repository root. Its value is strongest for scoped complex changes, but it must not become a parallel roadmap. This design adds a narrow contract layer and a machine check to keep that boundary clear.

## Goals / Non-Goals

**Goals:**

- Define when OpenSpec is required, optional, or unnecessary for CAD Agent work.
- Keep OpenSpec changes subordinate to `CORE_RESTRUCTURE_PLAN.md`.
- Add a doc-governance check that catches obvious OpenSpec misuse.
- Add focused unit tests for the new governance behavior.
- Record the package in status/changelog/handoff materials.

**Non-Goals:**

- No CAD execution, geometry, driver, registry, or Table C behavior changes.
- No rewrite of planning documents or historical documentation.
- No new global dependency, database, dashboard, or workflow runner.
- No automatic creation of OpenSpec changes for normal training rounds or small fixes.

## Decisions

### Decision 1: OpenSpec remains a scoped contract layer

OpenSpec will be used for complex changes that affect contracts, architecture boundaries, validation standards, or multiple modules. It will not carry global `next`, package queues, Table C state, or PlanMD-style phase ordering.

Alternative considered: make OpenSpec the primary planning system. Rejected because the repository already has a clear single PlanMD and task ledger; replacing it would create churn without improving current execution.

### Decision 2: Add a governance check instead of a new process hub

The new rule will be implemented as `check_openspec_contracts()` inside `core/maintenance/doc_governance.py` and included in `build_doc_governance_report()`. It will check:

- `openspec/config.yaml` exists and preserves the `CORE_RESTRUCTURE_PLAN.md` boundary.
- `openspec/tasks.md` does not exist at the root, because tasks belong inside a specific change.
- Active change files do not claim to be the master roadmap or PlanMD.

Alternative considered: create a separate OpenSpec audit script. Rejected because the existing doc-governance audit is already the right control surface.

### Decision 3: Keep trigger rules in human-readable docs

`AGENTS.md` and `CORE_RESTRUCTURE_PLAN.md` will describe OpenSpec routing in plain language:

- Required for contract/architecture/validation/multi-module changes.
- Optional for doc-only governance when it benefits from review.
- Not required for small fixes, ordinary training rounds, Table C refreshes, or status-only updates.

Alternative considered: make every package an OpenSpec change. Rejected because it would make small work ceremonial and would dilute the signal of a real change contract.

## Risks / Trade-offs

- OpenSpec sprawl -> Mitigation: governance check blocks root-level OpenSpec task ledgers and active changes that claim master-plan authority.
- Overhead for small work -> Mitigation: docs explicitly say small fixes and ordinary training rounds do not require OpenSpec.
- False positives in change text -> Mitigation: check only for strong master-plan phrases in active change Markdown and ignores archived changes.
- Incomplete enforcement -> Mitigation: this is intentionally a lightweight guard, not a policy engine; project rules still carry the final source-of-truth hierarchy.

## Migration Plan

1. Add OpenSpec contract spec and tasks for this package.
2. Add failing governance tests.
3. Implement `check_openspec_contracts()` and include it in the doc-governance report.
4. Update `AGENTS.md`, `CORE_RESTRUCTURE_PLAN.md`, status, changelog, and handoff records.
5. Run targeted unit tests and `run_doc_governance_audit.py`.

Rollback is simple: revert the doc-governance function/tests and documentation additions. No runtime CAD state or schema migration is involved.

## Open Questions

None for this small package. Future larger architecture changes can define stricter OpenSpec archive gates in their own changes if needed.
