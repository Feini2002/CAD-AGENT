## 1. Tests First

- [x] 1.1 Add no-CAD behavior-change proof tests that separate `mechanism_only` from `behavior_change_evidence`.
- [x] 1.2 Add Agent Task Maturity metric tests that explicitly separate this metric family from Table C / Core Proof Coverage.
- [x] 1.3 Add evidence portfolio export-boundary tests.
- [x] 1.4 Add schema tests for `selfUncertainty`, `retestedOriginalTask`, and prediction reconciliation.
- [x] 1.5 Add Orchestrator Host complexity / route budget tests that prove quick routes keep hard gates.
- [x] 1.6 Add no-CAD model-agent chain test coverage for `cognitiveLoopSummary`.

## 2. Core Implementation

- [x] 2.1 Add `core/model_review/evidence_portfolio.py`.
- [x] 2.2 Add `core/orchestrator/agent_cognition.py`.
- [x] 2.3 Wire sanitized portfolio refs into the no-CAD model-Agent chain payload.
- [x] 2.4 Add `cognitiveLoopSummary` to `model_agent_chain_result.json`.
- [x] 2.5 Add route `complexityAssessment` and `routeBudget` metadata to Orchestrator Host dispatch plans.
- [x] 2.6 Fix negated sedimentation phrases such as `不沉淀` so they do not trigger asset sedimentation routing.

## 3. Schema And Boundary Updates

- [x] 3.1 Extend soft judgement schemas with `selfUncertainty`.
- [x] 3.2 Extend learning promotion behavior-change evidence with `retestedOriginalTask` and `predictionReconciliation`.
- [x] 3.3 Keep learning promotion proposal-only; do not write memory/prompt/checker files from model output.
- [x] 3.4 Keep cheapest-route metadata from removing CAD or source hard gates.

## 4. Documentation And Records

- [x] 4.1 Add this OpenSpec change.
- [x] 4.2 Update `CORE_RESTRUCTURE_PLAN.md` with the adopted cognition-proof route.
- [x] 4.3 Update architecture/governance/status/changelog docs.
- [x] 4.4 Absorb the temporary proposal into system records and remove the standalone MD.

## 5. Verification

- [x] 5.1 Run focused no-CAD unit tests for cognition, export, prompt schemas, orchestrator host, and model-agent chain.
- [x] 5.2 Run broader model-review / workflow dispatch regression tests.
- [x] 5.3 Run relevant governance scripts and record residual whole-repo output blockers.
- [x] 5.4 Run OpenSpec validation.
- [x] 5.5 Review diff to ensure unrelated changes were not reverted.
