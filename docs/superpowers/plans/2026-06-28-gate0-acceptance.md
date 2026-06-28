# Gate 0 Acceptance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete Stage 2 by producing verifiable Gate 0 acceptance evidence for compiler fixtures, anti-cheat checks, natural-language attempts, and preview-only real AutoCAD smoke.

**Architecture:** Keep Stage 2 as evidence production, not product broadening. Add only a narrow natural-language Gate 0 attempt runner if missing, then aggregate existing evidence through `tools/check_gate0_acceptance.py`.

**Tech Stack:** Python 3.11+, `pytest`, existing `cad_agent` package, fake backend for deterministic checks, existing AutoCAD COM backend for environment-gated preview smoke.

## Global Constraints

- CAD writes must target `CODEX_PREVIEW`.
- `savedCurrentDwg=false` must remain true for real and fake backend evidence.
- Real CAD smoke must use preview-only execution and rollback created handles.
- Screenshots are visual aids only; created handle readback is required evidence.
- Do not restore old orchestrator, training, workbench, evidence warehouse, or old root directories.
- Do not use exact prompt route, case-id route, or compiler fixture SceneSpec to fake natural-language Gate 0.

---

### Task 1: Acceptance Evidence Layout

**Files:**
- Create: `docs/superpowers/plans/2026-06-28-gate0-acceptance.md`
- Modify: `docs/STATUS.md`

**Interfaces:**
- Consumes: `docs/ROADMAP.md`, `docs/SAFETY.md`
- Produces: a tracked plan and corrected status branch name.

- [x] **Step 1: Update status metadata**

Set `docs/STATUS.md` current branch to `main` and keep the acceptance boundary explicit.

- [x] **Step 2: Verify docs remain clean**

Run: `git diff -- docs/STATUS.md docs/superpowers/plans/2026-06-28-gate0-acceptance.md`

Expected: only branch metadata and this plan are added.

### Task 2: Natural-Language Gate 0 Attempt Runner

**Files:**
- Create or modify: `tools/run_gate0_nl_attempt.py`
- Test: `tests/evals/test_gate0_nl_attempt.py`

**Interfaces:**
- Consumes: raw `prompt`, `expectedObjects`, `expectedRelations`, and `safety` from `evals/gate0/cases.jsonl`.
- Produces: `gate0_nl_attempt_summary.json`, `case_results.jsonl`, and `failures.jsonl`.

- [x] **Step 1: Write failing tests**

Add tests that run the tool on a temporary JSONL with raw prompts only, assert `status == "passed"`, and assert no `sceneSpecFixture` is required.

- [x] **Step 2: Implement the runner**

Use a generic Gate 0 desktop-scene natural-language parser that derives supported object kinds and stable default relations from prompt content. Do not match full prompt strings, case IDs, or fixture dimensions.

- [x] **Step 3: Run focused tests**

Run: `python -m pytest tests/evals/test_gate0_nl_attempt.py -q`

Expected: all tests pass.

### Task 3: Local Deterministic Proof Chain

**Files:**
- Generated only: `.cad_agent_runs/stage2-gate0-acceptance-<timestamp>/...`

**Interfaces:**
- Consumes: existing tests, schema export, compiler eval, anti-cheat, cleanroom checks.
- Produces: fresh command outputs and JSON reports.

- [x] **Step 1: Run unit and contract tests**

Run: `python -m pytest`

Expected: exit 0.

- [x] **Step 2: Run repository boundary checks**

Run: `python tools/check_import_boundaries.py`

Expected: `status == "pass"`.

Run: `python tools/check_cleanroom.py`

Expected: `status == "pass"`.

- [x] **Step 3: Run schema and compiler eval checks**

Run: `python tools/export_schemas.py --output-dir .cad_agent_schemas --check`

Expected: exit 0.

Run: `python tools/run_compiler_eval.py --backend fake --cases evals/compiler/cases.jsonl --output-root .cad_agent_runs/stage2-gate0-acceptance-<timestamp>/compiler`

Expected: `summary.status == "pass"`.

### Task 4: Real AutoCAD Preview-Only Smoke

**Files:**
- Generated only: `.cad_agent_runs/stage2-gate0-acceptance-<timestamp>/real_smoke/...`

**Interfaces:**
- Consumes: existing `tools/run_real_cad_backend_smoke.py`.
- Produces: `real_cad_backend_smoke.json`.

- [x] **Step 1: Run preview-only smoke**

Run: `python tools/run_real_cad_backend_smoke.py --preview-only --rollback-after-check --output-dir .cad_agent_runs/stage2-gate0-acceptance-<timestamp>/real_smoke`

Expected: `status == "succeeded"`, `savedCurrentDwg == false`, rollback succeeded, all created handles read back on `CODEX_PREVIEW`.

- [x] **Step 2: If environment blocks AutoCAD**

Record the exact blocker in the generated report and keep Gate 0 acceptance pending instead of declaring pass.

### Task 5: Acceptance Aggregation and Summary

**Files:**
- Create or modify: `docs/STATUS.md`
- Create: `docs/GATE0_ACCEPTANCE.md`
- Generated only: `.cad_agent_runs/stage2-gate0-acceptance-<timestamp>/gate0_acceptance.json`

**Interfaces:**
- Consumes: compiler `summary.json`, `anti_cheat_report.json`, real smoke report, and natural-language attempt summary.
- Produces: final Gate 0 decision report and human-readable acceptance summary.

- [x] **Step 1: Run acceptance aggregator**

Run: `python tools/check_gate0_acceptance.py --compiler-eval-summary <summary> --anti-cheat-report <anti_cheat> --real-smoke-report <real_smoke> --gate0-attempt-summary <nl_summary> --output <acceptance_json>`

Expected: `status == "passed"` only if all evidence passes; otherwise the decision must name the blocker.

- [x] **Step 2: Write human summary**

Record evidence paths, checked items, not-proven capabilities, and CAD safety invariants.

- [x] **Step 3: Final verification**

Run the full proof chain again after source/doc edits. Verify git status and do not claim Stage 2 complete unless the final acceptance report is `passed`.
