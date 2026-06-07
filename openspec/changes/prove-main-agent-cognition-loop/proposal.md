## Why

The absorbed main-Agent cognition optimization proposal identified a real gap: the system has model-backed Agents, tool intents, handoffs, and hard gates, but it needs machine-readable proof that tool results or learned history can change a later route, dispatch, tool choice, or blocking judgement. Without that proof, memory and prompt changes are only mechanism work and must not be described as main Agent cognition improvement.

This change turns the temporary proposal into a scoped no-CAD cognition proof contract. It builds on the completed main-Agent dispatch-awareness and A-to-A gate work, but does not replace CAD hard gates, Core Proof Coverage, or user acceptance evidence.

## What Changes

- Add a sanitized `evidence_portfolio.json` builder for model-backed judgement. It writes minimal summaries and refs, blocks unsafe source classes, and remains subject to `build_model_export_manifest()`.
- Add no-CAD behavior-change proof helpers that distinguish `behavior_change_evidence` from `mechanism_only`.
- Add Agent Task Maturity summary helpers as a separate metric family from Table C / Core Proof Coverage.
- Extend model-review soft judgement schemas with `selfUncertainty` so soft gates can expose what might be wrong without weakening hard gates.
- Extend learning-promotion behavior-change evidence with `retestedOriginalTask` and prediction reconciliation fields.
- Add `cognitiveLoopSummary` to the no-CAD model-Agent chain result when a tool intent is executed and the same Agent receives the tool trace in a self-correction pass.
- Add conservative route complexity and `routeBudget` metadata to the Orchestrator Host. Cheapest-route metadata may reduce soft judgement work, but it never removes hard gates.

## Non-Goals

- No real CAD / DWG write, save, deletion, formal-layer edit, or table C promotion.
- No automatic writing of Agent memory, prompt addenda, checkers, or `docs/training/training-sources.json` from model output.
- No claim that confidence, `selfUncertainty`, prediction accuracy, model pass, or no-CAD fixture proves CAD geometry or user acceptance.
- No new PlanMD, no second backlog, and no new always-on global Agent.

## Impact

- Core: `core/model_review/evidence_portfolio.py`, `core/orchestrator/agent_cognition.py`, `core/orchestrator/model_agent_chain_runtime.py`, `core/orchestrator/orchestrator_host_runtime.py`.
- Schemas: model-review soft judgement schemas and `learning_promotion_review.schema.json`.
- Tests: focused no-CAD unit tests for portfolio export, schema contracts, orchestrator budget, cognitive loop, and behavior-change proof.
- Docs: `CORE_RESTRUCTURE_PLAN.md`, architecture/governance/status/changelog; the temporary proposal has been absorbed into this contract and removed as a standalone MD.
