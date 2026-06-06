## 1. OpenSpec Contract

- [x] 1.1 Create proposal, design, tasks, and capability spec for `adaptive-capability-growth-training`.
- [x] 1.2 Run OpenSpec validation for this change and record any schema/style issues before implementation begins.

## 2. Phase 0: Read-Only Inventory

- [x] 2.1 Add tests for classifying profile source roles: `fact_source`, `derived`, `diagnostic`, `candidate`, `archived_index`, and `missing_or_stale`.
- [x] 2.2 Implement a no-CAD inventory that scans approved training sources, Agent memory, Prompt addenda, focused reports, and archived paths without writing facts.
- [x] 2.3 Emit `capability_growth_profile_inventory.json` or an equivalent diagnostic report with source status, hashes where available, staleness, and data-bloat role.

## 3. Phase 1: Profile Schema And Lesson Extraction, No-CAD

- [x] 3.1 Add schema tests for `capabilityProfile` and `transferableLesson`, including required evidence-boundary fields.
- [x] 3.2 Implement candidate profile and transferable lesson builders that reject `output/debug/**`, workbench snapshots, sync reports, and retention reports as hard baselines.
- [x] 3.3 Add tests that positive lessons require matching negative examples, preconditions, exclusions, audit implications, and retest decisions.
- [x] 3.4 Confirm this phase does not update `training-sources.json`, Agent memory, Prompt addenda, workbench data, or table C.

## 4. Phase 2: Adaptive Planner, No-CAD

- [x] 4.1 Add TDD cases for routing quick/smoke/API probes to `smoke_replay` with `promotionLevel=observation`.
- [x] 4.2 Add TDD cases for pointed single-capability requests routing to `focused_retraining` with `growth_replay` unless explicit minimal smoke is requested.
- [x] 4.3 Add TDD cases for formal/all/workbench/acceptance requests requiring promotion and data-bloat gates without treating `all-31` as automatic formal acceptance.
- [x] 4.4 Add TDD cases for standard/style/sourceSpec requests routing to `standard_replay`.
- [x] 4.5 Add TDD cases for project execution using profiles only as upstream context and preserving deterministic CAD planning.

## 5. Phase 3: Foundation Runner Compatibility

- [x] 5.1 Add compatibility tests proving existing `remaining-21`, `all-31`, `--only`, hatch focused options, streaming demo, preview capture, post-sync, and retention semantics remain stable.
- [x] 5.2 Add additive report fields: `replayMode`, `profileVersionUsed`, `consumedLessonIds`, `whyExpressionLevelChosen`, `acceptedLowExpression`, and `regressionGuardStatus`.
- [x] 5.3 Ensure `--only` and hatch focused options cannot expand scope or overwrite full-batch acceptance.
- [x] 5.4 Ensure `--no-post-sync`, `--no-artifact-retention`, and `--no-capture-preview` remain honored.
- [x] 5.5 Mark first-10 queue compatibility as either covered in this phase or explicitly `out_of_scope_but_compat_checked`.

## 6. Phase 4: Expression Regression Gate

- [x] 6.1 Add tests for lineweight/linetype and dimension-style pilot baselines using semantic features and machine evidence.
- [x] 6.2 Add tests that growth/focused/formal replay blocks pass claims when required features are missing.
- [x] 6.3 Add tests that explicit smoke, no-CAD preflight, user scope limits, and untrusted/missing baselines are exempted with a recorded reason.
- [x] 6.4 Ensure the gate never relies only on screenshot size, object count, file size, model judgment, fake CAD, no-CAD draft, or workbench state.

## 7. Promotion, Fact Source, And Data-Bloat Gates

- [x] 7.1 Extend promotion-gate tests to require explicit decisions for training source, workbench, Agent calibration, base rules, task rules, checker, original-task retest, and data-bloat gate.
- [x] 7.2 Add evidence-closure tests that prevent archived/missing/debug/derived sources from becoming hard baselines.
- [x] 7.3 Add retention dry-run tests that protect active fact sources, learning ledger, Agent memory, Prompt addenda, registry evidence, system assets, status/handoff/issues, and case feedback references.
- [x] 7.4 Add compact workbench summary tests so `capability-map-data.js` stays derived-only, parseable, bounded, and non-recursive.

## 8. A-to-A, Model, And Worker Boundaries

- [x] 8.1 Add A-to-A gate tests that block unregistered agents from `effectiveRequiredAgents` and keep new roles as `additionalAgentRequests`.
- [x] 8.2 Add model-output tests for strict JSON, invalid schema blocking, `toolIntent` denial on save/delete/shell/formal-layer requests, and prompt-injection isolation.
- [x] 8.3 If Worker trace is implemented, add boundary tests for redacted payloads, repo-relative refs, no local execution, no CAD-MCP, no AutoCAD control, no local file read/write, no full prompt/CAD/screenshot payloads, no secret leakage, and no arbitrary user-supplied fetch. 本轮未实现 Worker adaptive trace；仅复用现有 Worker boundary-check 和报告级 `deployRequired=false`。
- [x] 8.4 Ensure Worker run state cannot prove training pass, CAD execution, model invocation, workbench sync, readback pass, or Agent growth.

## 9. CAD Safety And Delivery Verification

- [x] 9.1 Add or update tests for UTF-8 / `encodingPreflight` blocking before any CAD write.
- [x] 9.2 Preserve CAD execution gates: structured intent or `CAD_PLAN`, validate, dry-run, `CODEX_PREVIEW`, created handles, readback entities, bbox/layer/type/style checks, and `savedCurrentDwg=false`.
- [x] 9.3 Keep screenshots marked `visual_aid_only` and require `not_checked` for unverified dimensions, layers, annotations, hatch, or style claims.
- [x] 9.4 Add final closeout tests that restrict allowed claims to verified evidence and distinguish `verified`, `ready_for_user_review`, `not_run`, `not_verified`, `blocked`, `needs_more_evidence`, and `not_implemented`.
