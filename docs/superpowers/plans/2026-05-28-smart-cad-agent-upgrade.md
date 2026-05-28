# Smart CAD Agent Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the training-era CAD Agent into a visual-contract-driven multi-agent workflow that blocks weak outputs before CAD delivery.

**Architecture:** Implement the upgrade as small packages. Start by hardening the context and visual contract gates, then promote verified case behavior into reusable schemas, audit probes, and documentation.

**Tech Stack:** Python unittest, JSON schemas, `agents/pipeline/*.json`, `docs/training/*.md`, case artifacts under `projects/residential_sofa_2seat_20260528/`.

---

## Package 01A: Context + Visual Contract Gate

**Files:**
- Modify: `agents/pipeline/pipeline_manifest.json`
- Modify: `agents/pipeline/orchestrator/agent.json`
- Modify: `agents/pipeline/intent/agent.json`
- Modify: `agents/pipeline/execute/agent.json`
- Modify: `agents/pipeline/audit/agent.json`
- Modify: `agents/pipeline/repair/agent.json`
- Modify: `agents/pipeline/delivery/agent.json`
- Create: `agents/pipeline/context_curator/agent.json`
- Create: `agents/pipeline/visual_intent/agent.json`
- Create: `agents/pipeline/learning_promoter/agent.json`
- Modify: `agents/residential/rules.md`
- Create: `projects/residential_sofa_2seat_20260528/runs/round12_visual_parts.json`
- Modify: `projects/residential_sofa_2seat_20260528/feedback.md`
- Modify: `docs/planning/任务清单.md`
- Test: `tests/agents/test_pipeline_visual_contracts.py`

- [x] **Step 1: Write failing agent contract tests**
  Add tests that require `context_curator`, `pipeline_visual_intent`, and `learning_promoter` in the manifest; require `visual_parts` artifacts; require reference-match flows to block Execute without `style_target` and `visual_parts`.

- [x] **Step 2: Run the focused test and verify failure**
  Run: `$py -m unittest tests.agents.test_pipeline_visual_contracts`
  Expected: FAIL because the new agents and artifact gates are not yet registered.

- [x] **Step 3: Implement the manifest and agent JSON changes**
  Register the three new agents and update existing agent contracts so each has explicit inputs, outputs, pass gates, and must-not clauses for style target, visual parts, visual audit, and learning promotion.

- [x] **Step 4: Add case visual parts and residential scene vocabulary**
  Add `round12_visual_parts.json` with the sofa component contract. Update residential rules with sofa plan component defaults and forbidden visual shortcuts.

- [x] **Step 5: Sync current training state docs**
  Update the sofa case row in `docs/planning/任务清单.md` and `feedback.md` so the active state reflects round12 visual-contract prep rather than stale round1 status.

- [x] **Step 6: Run focused verification**
  Run: `$py -m unittest tests.agents.test_pipeline_visual_contracts`
  Expected: PASS.

- [x] **Step 7: Dispatch independent read-only verifier**
  Ask a sub-agent to review Package 01A changed files for missing gates, stale state, and divergence from `docs/training/visual-first-agent-plan.md`.

## Package 01B: Case-Local PartRenderer + Style Compare

**Files:**
- Create: `projects/residential_sofa_2seat_20260528/runs/part_renderer.py`
- Modify: `projects/residential_sofa_2seat_20260528/runs/semantic_clean_two_seater.py`
- Create: `projects/residential_sofa_2seat_20260528/runs/round12_style_compare.md`
- Create: `projects/residential_sofa_2seat_20260528/runs/round12_agent_review.json`
- Test: `tests/core/test_visual_parts_case_contract.py`

- [x] **Step 1: Write failing tests for part-only rendering contracts**
  Require the renderer to reject undeclared structures and map every `visual_parts.parts[].id` to created handles.

- [x] **Step 2: Implement minimal case renderer**
  Draw only declared closed parts on `CODEX_PREVIEW`; keep this case-local until the user accepts the visual result.

- [x] **Step 3: Produce round12 compare/review artifacts**
  Create a component-by-component compare template and agent review JSON.

- [x] **Step 4: Run focused tests and reviewer agent**
  Verify with unittest, then dispatch read-only sub-agent review.

## Package 02: Global Schema + Core Probe Promotion

**Files:**
- Create: `core/schemas/visual_parts.schema.json`
- Modify: `core/schemas/registry.py`
- Create: `core/drawing/part_primitives.py`
- Modify: `core/verification/training_geometry_audit.py`
- Test: `tests/core/test_visual_parts_schema.py`
- Test: `tests/core/test_training_geometry_audit.py`

- [x] **Step 1: Add schema and registry tests**
- [x] **Step 2: Add reusable closed part primitives**
- [x] **Step 3: Promote `closed_outer_shell`, `split_as_backrest`, and missing-part audit probes**
- [x] **Step 4: Run focused and existing audit tests**
- [x] **Step 5: Dispatch independent read-only verifier**

## Package 03: MD Context Governance

**Files:**
- Modify: `CORE_CONTEXT_BRIEF.md`
- Modify: `CORE_RESTRUCTURE_PLAN.md`
- Modify: `docs/training/README.md`
- Modify: `docs/planning/任务清单.md`
- Create or update: `docs/history/README.md`
- Test: `scripts/run_doc_governance_audit.py`

- [x] **Step 1: Mark active entrypoints and history-only docs**
- [x] **Step 2: Remove duplicate next/backlog language from active docs**
- [x] **Step 3: Run doc governance audit**
- [x] **Step 4: Dispatch independent read-only verifier**

## Package 04: Learning Loop Automation

**Files:**
- Create: `core/training/learning_promotion.py`
- Create: `scripts/run_training_round_gate.py`
- Test: `tests/core/test_training_learning_promotion.py`

- [x] **Step 1: Add tests for failure classification and promotion destination**
- [x] **Step 2: Implement learning promotion report writer**
- [x] **Step 3: Add a round gate script that validates required artifacts before next round**
- [x] **Step 4: Run focused tests and reviewer agent**

## Package 05: Round12 CAD Verification

**Files:**
- Modify: `projects/residential_sofa_2seat_20260528/runs/semantic_clean_two_seater.py`
- Output: `projects/residential_sofa_2seat_20260528/runs/round12_*`

- [x] **Step 1: Run validate/dry-run or declared case-script gate**
- [x] **Step 2: Execute only on `CODEX_PREVIEW`**
- [x] **Step 3: Run machine audit**
- [x] **Step 4: Capture preview screenshot**
- [x] **Step 5: Complete agent visual self-review**
- [x] **Step 6: Dispatch independent read-only verifier**
- [x] **Step 7: Ask user for visual feedback only if gates pass**
