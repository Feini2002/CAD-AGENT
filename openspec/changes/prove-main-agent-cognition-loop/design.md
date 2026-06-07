## Context

The repository already has:

- `run_no_cad_model_agent_chain()` with model-backed design/style/review Agents.
- `toolIntent` execution and tool trace artifacts.
- self-correction after a tool trace for no-CAD deterministic/read-only tool intents.
- `pipeline_learning_promoter` registered as a prompt pack.
- A-to-A hard gates and main-Agent dispatch awareness.

The missing layer is not another Agent. The missing layer is a proof contract: after a tool result, memory, or prior failure is observed, can the system show a changed decision and avoid overclaiming when nothing changed?

## Decisions

### Decision 1: Keep cognition proof no-CAD and evidence-boundary first

The first implementation only emits no-CAD proof artifacts. It records `cadWriteAuthorized=false`, `savedCurrentDwg=false`, and explicit `notProofOf` boundaries. Real CAD proof still requires existing CAD_PLAN validation, dry-run, CODEX_PREVIEW execution, created-handle readback, and closeout gates.

### Decision 2: Evidence portfolio is a sanitized summary, not an automatic export allowlist

`evidence_portfolio.json` can summarize current evidence, memory refs, and historical risk refs, but model export still passes through `build_model_export_manifest()`. Portfolio refs do not automatically authorize every path listed inside the portfolio.

### Decision 3: Behavior change is separate from mechanism work

`build_behavior_change_proof()` compares before/after route, required Agents, tool choice, and blocking reasons. If no field changes, the proof returns `claimStatus=mechanism_only`; delivery text may only say mechanism work was added.

### Decision 4: Soft judgement becomes more informative, not more authoritative

`selfUncertainty` is required in soft judgement schemas. It helps downstream validation target weak points, but it cannot pass or waive CAD, source, save/delete, training, or table-C hard gates.

### Decision 5: Cheapest-route-first starts as route budget metadata

The Orchestrator Host records `complexityAssessment` and `routeBudget`. For quick trials it can identify skippable soft Agents, but `mustKeepHardGates` is copied from the selected route and may not be reduced by complexity assessment.

## Rollback

The new proof helpers and portfolio files can be ignored without changing existing CAD execution. If route-budget metadata causes confusion, keep the fields but mark `mode=standard` while retaining all hard gates.
