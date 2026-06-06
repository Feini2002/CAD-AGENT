## ADDED Requirements

### Requirement: Adaptive CAD training replay modes

The system SHALL classify training-related requests into explicit replay modes before invoking foundation training runners or CAD execution.

#### Scenario: User asks for a quick smoke check

- **WHEN** the user asks for a quick check, smoke replay, API probe, or minimum run
- **THEN** the adaptive plan sets `replayMode=smoke_replay`
- **AND** records `acceptedLowExpression=true` with an explanation
- **AND** sets promotion to observation-only.

#### Scenario: User asks to retrain one capability

- **WHEN** the user names one capability, pattern, scale, style, or subtopic
- **THEN** the adaptive plan preserves `scope.mode=focused`
- **AND** uses `growth_replay` unless the user explicitly requests minimum smoke
- **AND** does not expand the request into a full 31-item or 217-item batch.

#### Scenario: User asks for a standard or sourceSpec-backed output

- **WHEN** a task has an explicit standard, sourceSpec, asset source, style spec, or checker
- **THEN** the adaptive plan prefers `standard_replay`
- **AND** reduces model freedom in favor of deterministic standard reproduction and readback checks.

### Requirement: Capability growth profiles use bounded evidence

The system SHALL represent training maturity with capability profiles whose source references, evidence roles, stale status, required features, and forbidden claims are explicit.

#### Scenario: Active source is available

- **WHEN** a profile references an active fact source with existing path and valid source role
- **THEN** the profile may use that source as a hard baseline within its stated evidence boundary.

#### Scenario: Source is derived or diagnostic

- **WHEN** a profile candidate references `capability-map-data.js`, `capability-map.html`, sync reports, retention reports, data-bloat audits, or `output/debug/**`
- **THEN** those references are classified as derived, diagnostic, or candidate
- **AND** they cannot become hard baselines or prove training pass.

#### Scenario: Source is archived or missing

- **WHEN** historical evidence is archived, missing, stale, or lacks closure
- **THEN** it may be used only as a planning clue
- **AND** the profile records `profileStale=true` or an equivalent stale/missing status before any hard comparison is attempted.

### Requirement: Transferable lessons require positive and negative boundaries

The system SHALL extract reusable training lessons only when each lesson includes what to do, what not to do, when it applies, when it does not apply, how it affects CAD planning, how it is audited, and what remains unchecked.

#### Scenario: Focused retraining produces a candidate lesson

- **WHEN** focused retraining passes for a capability
- **THEN** the promotion path may emit a `transferableLesson` candidate
- **AND** the candidate includes positive pattern, negative pattern, preconditions, exclusions, evidence boundary, affected agents, checker decision, and original-task retest decision.

#### Scenario: Lesson lacks evidence boundary

- **WHEN** a proposed lesson lacks source refs, `notChecked`, forbidden claims, or retest status
- **THEN** it remains invalid for promotion
- **AND** it cannot update rules, checkers, Agent memory, Prompt addenda, workbench facts, or profile baselines.

### Requirement: Expression regression gate blocks unsafe pass claims

The system SHALL block growth/focused/formal pass claims when trusted baseline evidence exists and the new output omits required semantic or machine-evidence features.

#### Scenario: Growth replay lacks required features

- **WHEN** `replayMode=growth_replay`
- **AND** a trusted profile baseline requires lineweight, linetype, linetype scale, sample cell, and style readback
- **AND** the new report only shows generic lines or screenshots
- **THEN** the regression gate returns blocked or replan
- **AND** the report cannot claim training pass.

#### Scenario: Explicit smoke is exempted

- **WHEN** the user explicitly requests minimum smoke
- **THEN** the regression gate may return skipped or exempted
- **AND** the report records `acceptedExemption=explicit_minimal_smoke`
- **AND** the smoke result does not update the profile.

#### Scenario: Comparison method is evidence-aware

- **WHEN** the regression gate compares two runs
- **THEN** it compares scope, requested capabilities, replay mode, profile version, consumed lessons, created handles, readback, bbox, type counts, layer counts, style/dimension/hatch readback, audit checks, and `not_checked`
- **AND** it does not rely only on screenshot size, handle count, file size, model rating, fake CAD, no-CAD draft, or workbench state.

### Requirement: Foundation runner compatibility is preserved

The system SHALL add adaptive replay behavior without silently changing existing foundation runner semantics.

#### Scenario: Existing batch defaults run

- **WHEN** the existing `remaining-21`, `all-31`, or equivalent foundation preset runs without an explicit growth/formal route
- **THEN** the previous smoke or existing panel behavior remains valid
- **AND** adaptive report fields are additive.

#### Scenario: Focused hatch options are used

- **WHEN** hatch-specific options such as hatch pattern, hatch scales, or full-fill mode are provided
- **THEN** the runner requires the hatch capability scope
- **AND** cannot broaden the run to unrelated capabilities.

#### Scenario: Workbench and retention flags are explicit

- **WHEN** the user or CLI disables post-sync, artifact retention, or preview capture
- **THEN** adaptive replay fields do not re-enable those side effects
- **AND** missing screenshots do not by themselves fail CAD geometry.

### Requirement: CAD execution remains deterministic and bounded

The system SHALL keep all real CAD writing under existing deterministic safety gates regardless of replay mode.

#### Scenario: CAD write is attempted

- **WHEN** any replay mode reaches real CAD output
- **THEN** UTF-8 / `encodingPreflight`, structured intent or `CAD_PLAN`, validate, dry-run, `CODEX_PREVIEW`, created handles, readback entities, bbox, layer, type count, relevant style/dimension/hatch readback, and `savedCurrentDwg=false` are required before verified CAD claims.

#### Scenario: Readback is unavailable

- **WHEN** dimensions, layers, annotations, hatch, style, or geometry cannot be verified by readback
- **THEN** the report marks those claims `not_checked` or `not_verified`
- **AND** screenshots, dry-run, fake CAD, model pass, no-CAD draft, Worker state, or workbench display cannot fill that proof gap.

#### Scenario: User asks for broader CAD effects

- **WHEN** a task would save the current business DWG, overwrite source files, delete beyond evidence-locked preview objects, change formal layers, or export imprecise whole-model sources
- **THEN** the system requires explicit scope-bound user approval before proceeding.

### Requirement: Promotion and data-bloat gates protect durable state

The system SHALL require explicit promotion and data-bloat decisions before adaptive growth artifacts update durable training state or derived displays.

#### Scenario: Quick or smoke run completes

- **WHEN** `quick_trial` or `smoke_replay` succeeds
- **THEN** the system records observation-only promotion
- **AND** does not update `training-sources.json`, Agent memory, Prompt addenda, workbench fact state, capability profiles, or table C.

#### Scenario: Formal acceptance is requested

- **WHEN** a run seeks durable learning, workbench state, Agent calibration, checker updates, or fact-source registration
- **THEN** `promotionGate` records explicit decisions for training source, workbench, Agent calibration, base rules, task rules, checker, original-task retest, and data-bloat gate
- **AND** missing gates block completion claims.

#### Scenario: Workbench summary is generated

- **WHEN** profile summary enters workbench data
- **THEN** `capability-map-data.js` remains derived-only, compact, parseable, and overwrite-generated
- **AND** it does not embed full profile history, full reports, recursive sync/retention reports, or debug candidates as facts.

### Requirement: A-to-A and model outputs cannot bypass deterministic gates

The system SHALL use only registered agents for effective hard-gate responsibility and SHALL treat model outputs as bounded schema data rather than execution authority.

#### Scenario: New agent role is proposed

- **WHEN** a role such as `growth_planner`, `experience_distiller`, `regression_reviewer`, or `profile_curator` is proposed
- **THEN** it remains in `additionalAgentRequests` with `needs_reviewed_package` or `needs_openspec_change`
- **AND** it cannot appear in `effectiveRequiredAgents` or release a hard gate until registered.

#### Scenario: Model output requests a tool

- **WHEN** a model-style agent emits `toolIntent`
- **THEN** the deterministic Tool Contract validates permission class, target scope, input refs, forbidden effects, expected reports, and approval requirement
- **AND** requests to save, delete, modify formal layers, run shell, read all files, or bypass evidence gates are denied unless separately authorized by repository rules and the user.

### Requirement: Optional Worker trace remains remote-state-only

The system SHALL allow Worker involvement only as an optional redacted envelope and trace layer, not as a training, CAD, shell, local-file, or model-execution layer.

#### Scenario: Worker trace is enabled

- **WHEN** a future phase sends adaptive growth trace information to Worker
- **THEN** the payload contains only redacted request summary, capability ids, scope, requested agents, blocked reason, repo-relative trace/report refs, schema status, and high-level booleans
- **AND** it excludes full prompts, full CAD data, full screenshots, secrets, local absolute paths, stdout/stderr dumps, local file contents, and all-model-space data.

#### Scenario: Worker receives a forbidden request

- **WHEN** Worker payload or requested action would run shell, call `codex.cmd`, call model bridge, call CAD-MCP, control AutoCAD, read/write local files, save DWG, fetch arbitrary user-supplied URLs, or proxy external APIs
- **THEN** the request is blocked.

#### Scenario: Worker run state is complete

- **WHEN** Worker run state reports success or completion
- **THEN** that state proves only remote envelope/state behavior
- **AND** it does not prove training pass, capability profile correctness, model invocation, CAD execution, readback pass, workbench sync, Agent growth, or user acceptance.

### Requirement: Verification is test-first and phase-specific

The system SHALL implement adaptive capability growth through phase-specific tests before production behavior changes.

#### Scenario: No-CAD phases are implemented

- **WHEN** profile inventory, profile schema, lesson extraction, or adaptive planner phases are implemented
- **THEN** tests cover schema validity, source roles, stale evidence, derived-source rejection, deterministic routing, explicit smoke exemptions, and scope guard
- **AND** no CAD execution or durable fact-source write is required.

#### Scenario: Runner integration is implemented

- **WHEN** foundation runner report fields or replay strategy integration is added
- **THEN** tests cover backwards compatibility, `--only` scope, all-31 non-formal behavior, hatch option scope, streaming/watchdog behavior, optional screenshot behavior, post-sync flags, and retention flags.

#### Scenario: Worker trace is implemented

- **WHEN** Worker trace support is added
- **THEN** tests cover redaction, payload size, no local execution, no arbitrary fetch, no secret leakage, and no overclaiming from Worker state.
