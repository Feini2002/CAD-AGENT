## Why

Focused retraining, object replay, system asset work, Agent memory, and Prompt addenda can all record useful CAD training experience, but the next foundation smoke run may still fall back to the earliest small-panel pattern. That shows a repository-level gap:

```text
training evidence
  != transferable lesson
  != active capability profile
  != safe replay strategy
  != deterministic CAD proof
```

The CAD Designer Agent needs an auditable growth mechanism that can use already-learned experience without turning CAD execution into free-form improvisation. This change proposes that mechanism as an OpenSpec contract only.

## What Changes

- Define adaptive CAD training replay modes: `smoke_replay`, `growth_replay`, `standard_replay`, `focused_retraining`, `formal_acceptance`, and `project_execution`.
- Define capability growth profiles, transferable lessons, adaptive training plans, and expression regression gates as explicit contracts.
- Preserve old smoke replay as a low-cost life-sign check instead of replacing it with a richer template.
- Require growth replay to consume active or explicitly bounded profile evidence and to explain why an expression level was chosen.
- Add scope-aware regression checks so growth/focused/formal runs cannot silently pass with a lower expression level than trusted history supports.
- Keep CAD execution deterministic: structured intent or `CAD_PLAN`, UTF-8 preflight, validate, dry-run, `CODEX_PREVIEW`, created-handle readback, audit, and bounded closeout claims.
- Add fact-source and data-bloat gates so profiles, lessons, workbench summaries, sync reports, and retention reports do not become recursive pseudo-evidence.
- Define Worker trace as optional and remote-state-only; Worker must not train, read local sources, run shell, control AutoCAD, call CAD-MCP, or proxy model / CAD payloads.

## Capabilities

### New Capabilities

- `cad-training-adaptive-growth`: Defines how CAD training runs build and consume growth profiles, route replay mode, detect expression regression, preserve scope, and report evidence boundaries.

### Modified Capabilities

- Future implementation may modify foundation training runners, workbench summaries, promotion gates, and optional Worker trace contracts, but this OpenSpec creation does not change code or active training behavior.

## Non-Goals

- Do not replace `CORE_RESTRUCTURE_PLAN.md` or create a second master backlog.
- Do not resume formal training while `ARCH-CONVERGENCE-01` remains the active default, unless the user explicitly overrides that boundary.
- Do not register the deleted debug draft as a fact source.
- Do not update `docs/training/training-sources.json`, Agent memory, Prompt addenda, workbench data, or table C.
- Do not execute CAD, save DWG files, deploy Worker changes, or claim `Project Delivery Readiness`.
- Do not treat screenshots, dry-run, fake CAD, model pass, Worker state, sync report, or workbench display as CAD geometry proof.

## Impact

- OpenSpec-only impact in this proposal package: `openspec/changes/adaptive-capability-growth-training/**`.
- Future implementation impact may include no-CAD profile builders, adaptive planners, foundation runner report fields, expression regression checks, workbench profile summaries, A-to-A gates, and optional Worker trace schemas.
- Future verification must be test-first for source roles, schema validity, replay routing, scope guards, runner compatibility, data-bloat gates, Worker redaction, and CAD write/readback boundaries.
- Any later real CAD claim remains governed by existing CAD proof requirements: `CAD_PLAN`, validate, dry-run, `CODEX_PREVIEW`, created handles, readback, bbox/layer/type/style checks, and screenshot only as visual aid.
