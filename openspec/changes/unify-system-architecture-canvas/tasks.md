# Tasks: Unify System Architecture Canvas

## 1. Architecture Contract and Planning

- [x] Create or update `docs/architecture/system-architecture-convergence.md` with the seven-layer architecture canvas, old-module mapping, metric reframe, and training pause boundary.
- [x] Update `docs/architecture/README.md` so the architecture canvas is the first conceptual entry before task-chain and Worker / bridge details.
- [x] Update `CORE_RESTRUCTURE_PLAN.md` so the active priority is architecture convergence before new formal training.
- [x] Update `docs/planning/任务清单.md` so §0 points to the convergence package and lists training as paused unless explicitly overridden.

## 2. Rules and Status Synchronization

- [x] Update `AGENTS.md` to state that table C is now `Core Proof Coverage`, not end-to-end true CAD ability.
- [x] Update `docs/governance/cad-agent-rules.md` with the three maturity labels: `Core Proof Coverage`, `Agent Task Maturity`, `Project Delivery Readiness`.
- [x] Update `CORE_STATUS.md` to preserve old machine coverage while moving it under bottom-layer evidence.
- [x] Update `CORE_CONTEXT_BRIEF.md` so new conversations recover the convergence priority before training.
- [x] Update `docs/status/current.md`, `docs/status/changelog.md`, and `docs/status/issues.md` with the architecture fragmentation risk and convergence decision.
- [x] Update `docs/training/README.md` so formal training resumes only after the convergence pass or explicit user override.

## 3. Script and Derived Display Audit

- [x] Inspect `scripts/run_capability_coverage.py` and record whether output field names can remain machine-compatible while UI / docs relabel them as proof coverage.
- [x] Inspect `scripts/build_capability_map_data.py` for active display labels that imply true CAD task ability.
- [x] Inspect `scripts/sync_training_workbench.py` and `scripts/run_training_workbench_agent_check.py` for assumptions that table C equals training maturity.
- [x] Inspect `scripts/run_doc_governance_audit.py` and `core/maintenance/doc_governance.py` for rules that should catch old primary-status wording.
- [x] Inspect `scripts/run_a_to_a_orchestration_gate_check.py` for whether architecture convergence should require a `system_architecture_canvas` or equivalent hard gate on repo-level tasks.

## 4. Implementation Adjustments

- [x] Add minimal compatibility adapters or label changes so existing JSON fields remain stable but active user-facing language says `Core Proof Coverage`.
- [x] Add tests that reject active status docs claiming table C is end-to-end true CAD ability.
- [x] Add tests that keep `CORE_RESTRUCTURE_PLAN.md` as the single active PlanMD and prevent OpenSpec tasks from becoming a second backlog.
- [x] Regenerate the training workbench only if generation scripts or labels change; do not treat regenerated HTML as a fact source.

## 5. Verification and Handoff

- [x] Run `openspec.cmd validate --all --strict --json --no-interactive`.
- [x] Run `$py scripts\run_doc_governance_audit.py`.
- [x] Run targeted governance tests, at minimum `$py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v`.
- [x] If workbench scripts change, run `$py scripts\sync_training_workbench.py` and confirm Agent check output.
- [x] Update `docs/handoffs/current.md` and `docs/handoffs/package-index.md` only after implementation begins and produces a package-level change.
- [x] Before resuming formal training, confirm the active docs distinguish `Core Proof Coverage`, `Agent Task Maturity`, and `Project Delivery Readiness`.
