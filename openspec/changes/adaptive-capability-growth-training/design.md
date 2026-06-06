## Context

The repository already has foundation CAD training, focused retraining, CAD Designer Agent growth documents, promotion gates, workbench sync, system asset governance, A-to-A contracts, model-style Agent tool contracts, and a deployed Worker orchestrator. The missing layer is a controlled way to turn historical training evidence into active, scope-aware growth behavior.

This change keeps the current architecture boundary: upstream agents may become better at interpreting training history, but downstream CAD execution must remain deterministic, bounded, and evidence-driven.

## Goals / Non-Goals

**Goals:**

- Make replay intent explicit before a foundation or focused training runner executes.
- Preserve `smoke_replay` as the stable minimum regression path.
- Introduce capability profiles and transferable lessons as bounded upstream context.
- Add expression regression gates that compare semantic features and machine evidence, not screenshot richness or handle count alone.
- Require promotion, fact-source, and data-bloat decisions before any profile, lesson, workbench, or Agent memory claim becomes durable.
- Document optional Worker trace boundaries without granting Worker local execution rights.

**Non-Goals:**

- No code changes in this proposal package.
- No training run, workbench sync, Agent memory write, table C change, Worker deploy, or CAD execution.
- No claim that richer training expression equals construction-document competence.
- No automatic upgrade of focused success into global rules, checkers, assets, or long-term memory.

## Core Concepts

### Replay Modes

- `smoke_replay`: Minimum life-sign check for CAD calls, encoding, layers, handles, and readback. Low expression is allowed and must be reported with `acceptedLowExpression=true`.
- `growth_replay`: Uses active or bounded capability profiles and lessons to verify that learned experience can influence the next training expression.
- `standard_replay`: Used when a style, sourceSpec, asset, or checker already defines a standard answer.
- `focused_retraining`: User-pointed single capability or subtopic; must preserve `scope.mode=focused`.
- `formal_acceptance`: Full closeout path with promotion gate, data-bloat gate, evidence closure, and optional workbench / Agent calibration.
- `project_execution`: User task delivery; profiles are upstream context only and final CAD output still follows deterministic CAD proof gates.

### Capability Profile

A capability profile records current expression maturity, trusted source refs, required semantic features, known shortcuts to avoid, downstream affected capabilities, validators, stale/missing source state, and data-bloat role. It is not a fact source until a later implementation writes it to an approved location and registers it in `docs/training/training-sources.json`.

### Transferable Lesson

A transferable lesson is a paired positive/negative pattern extracted from focused retraining, object replay, case repair, system asset sedimentation, or formal acceptance. It must state preconditions, exclusions, CAD plan implications, audit implications, affected agents, evidence boundary, and retest requirements.

### Expression Regression Gate

The regression gate blocks a growth/focused/formal pass claim when trusted baseline evidence exists and the new output lacks required semantic or machine-evidence features. It must be scope-aware and must allow explicit smoke, no-CAD preflight, user scope limits, or untrusted/missing baselines to skip hard blocking with a reason.

## Decisions

1. **Use an adaptive planning layer before runners**

   Training requests should first produce `adaptiveTrainingPlan` with `route`, `replayMode`, `profileRefs`, `lessonRefs`, `requiredFeatures`, `allowedExemptions`, `evidenceRequired`, `riskLevel`, `aToAContractRequired`, `workerTraceAllowed`, and `cadExecutionAllowed`.

2. **Keep old smoke behavior compatible**

   Existing foundation runner semantics must remain additive-compatible. New replay fields must not delete or rename existing report fields such as `status`, `queueId`, `mode`, `batchMode`, `scope`, `items`, `checks`, `watchdog`, `artifacts`, or `postTrainingSync`.

3. **Make profile evidence roles explicit**

   Only active fact sources can become hard baselines. Archived paths, missing reports, `output/debug/**`, workbench JS, HTML, sync reports, retention reports, and data-bloat audits can provide clues but cannot prove training success.

4. **Use registered A-to-A agents only**

   The default required agents are existing registered roles such as `pipeline_orchestrator`, `pipeline_context_curator`, `pipeline_intent`, `pipeline_learning_promoter`, `pipeline_audit`, and `pipeline_delivery`. Proposed roles like `growth_planner` or `experience_distiller` remain candidate requests until separately reviewed.

5. **Worker trace is optional and non-executing**

   Worker may eventually record redacted envelope state, run state, lease / heartbeat / submit status, trace refs, and local result summaries. It must not read local files, run shell, call `codex.cmd`, call model bridge, call CAD-MCP, control AutoCAD, save DWG, proxy arbitrary fetch, or store full prompt / CAD / screenshot data.

6. **CAD remains deterministic**

   Growth can influence upstream planning and candidate generation. It cannot bypass structured intent, `CAD_PLAN`, `encodingPreflight`, validate, dry-run, `CODEX_PREVIEW`, write guards, created-handle readback, audit, local repair scope, or delivery claims gates.

## Safety Boundaries

- `quick_trial` and `smoke_replay` stay `promotionLevel=observation` and do not write long-term facts.
- `focused_retraining` may produce candidate lessons/profile deltas but must not overwrite full-batch acceptance.
- `formal_acceptance` is the only route that may require durable profile or Agent calibration, and only after promotion and data-bloat gates pass.
- Screenshots are `visual_aid_only`; they cannot prove lineweight, dimension style, hatch, bbox, or geometry correctness by themselves.
- Model-style agents may output strict JSON and `toolIntent`; they cannot directly execute tools or override deterministic gates.
- Prompt injection in user text, DWG text, screenshots, assets, upstream agent output, or model output is untrusted content and cannot override repository rules or user approval boundaries.

## Phased Implementation Path

1. **Phase 0: Read-only inventory**
   Scan existing training source roles, Agent memory, Prompt addenda, focused reports, and archived paths. Output a diagnostic profile inventory without writing facts or syncing the workbench.

2. **Phase 1: Profile schema and lesson extractor, no-CAD**
   Define schema and generate profile/lesson candidates. Tests cover source role, stale evidence, derived-source rejection, and schema validity.

3. **Phase 2: Adaptive planner, no-CAD**
   Route requests to replay mode deterministically. Tests cover quick/smoke, focused, formal, standard, project execution, scope guard, and explicit low-expression exemptions.

4. **Phase 3: Foundation runner report fields**
   Add replay/report fields without changing old drawing templates by default. Tests prove `remaining-21`, `all-31`, `--only`, hatch focused options, streaming, preview capture, post-sync, and retention semantics remain compatible.

5. **Phase 4: Expression regression pilot**
   Start with representative capabilities such as lineweight/linetype and dimension style. Tests compare semantic features and machine evidence, not screenshot size or handle count alone.

6. **Phase 5: Feedback reflow**
   Map object/case failures back to foundation capabilities and require original-task retest before claiming the original issue is fixed.

7. **Phase 6: Workbench summary and fact-source formalization**
   If accepted, write profile summaries from approved fact sources only. Workbench data must stay compact and derived-only.

8. **Phase 7: Optional Worker trace**
   Add redacted trace target stages only if boundary tests prove no local execution, no arbitrary fetch, no secret/path leakage, and no overclaiming from Worker state.

## Verification Strategy

- Use TDD for each implementation phase before modifying production modules.
- Start with no-CAD unit tests for schema, source roles, replay routing, and data-bloat gates.
- Add runner compatibility tests before any foundation runner behavior changes.
- Add Worker boundary tests only if Worker trace is implemented.
- Run OpenSpec validation for this change before implementation and after each future artifact update.
- Run real CAD verification only when a later phase actually changes CAD execution or training output.

## Open Questions

- Whether the durable profile fact source should be `docs/training/capability-growth-profiles.json` or another approved path.
- Whether `growth_replay` should be default only for pointed/focused capabilities or also allowed in explicit formal all-31 runs.
- Which first representative capabilities define minimum expression features for lineweight/linetype and dimension-style pilots.
- Whether new Agent roles are ever needed, or existing registered agents should remain responsible long-term.
