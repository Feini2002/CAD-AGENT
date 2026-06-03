## 1. Tests First

- [x] 1.1 Add failing tests in `tests/core/test_a_to_a_task_contract.py` for `mainAgentSelfCheck` on `asset_dwg_layout`, including identity, mission, responsibility boundary, known limits, and decision basis.
- [x] 1.2 Add failing tests in `tests/core/test_a_to_a_task_contract.py` for missing or failed `mainAgentSelfCheck` blocking `a_to_a_task_contract.status` and `deliveryBoundary.mayClaimComplete`.
- [x] 1.3 Add failing tests in `tests/core/test_a_to_a_task_contract.py` for registered dynamic dispatch adding `pipeline_visual_layout_reviewer` to `effectiveRequiredAgents` with a non-empty reason and `visual_layout_review` hard gate.
- [x] 1.4 Add failing tests in `tests/core/test_a_to_a_task_contract.py` for unregistered Agent requests staying in `additionalAgentRequests` with `needs_reviewed_package`, and never entering `effectiveRequiredAgents`.
- [x] 1.5 Add failing tests in `tests/core/test_workflow_dispatch.py` for `workflow_dispatch.status=blocked` when main Agent self-check or dispatch decision is blocked.
- [x] 1.6 Add failing tests or extend existing tests so `layoutReadabilityAcceptable` is required for `pipeline_visual_layout_reviewer` pass output.

## 2. Contract Implementation

- [x] 2.1 Extend `core/orchestrator/a_to_a_task_contract.py` with manifest-aware helpers that can read registered Agent IDs and dynamic dispatch policy without creating a second workflow router.
- [x] 2.2 Add `mainAgentSelfCheck` generation for high-risk `taskKind` values: `system_asset_sedimentation`, `asset_dwg_layout`, and `visual_layout_review`.
- [x] 2.3 Add `dispatchDecision` generation with `baseRequiredAgents`, `registeredAdditionalAgents`, `effectiveRequiredAgents`, `additionalAgentRequests`, `blockedUntilAgentsReport`, and `reviewedPackageRequired`.
- [x] 2.4 Ensure dynamic additions are limited to manifest-registered Agent IDs and include triggering semantic reason plus affected hard gate.
- [x] 2.5 Ensure unregistered Agent needs are recorded only as reviewed-package / OpenSpec candidates and block any attempt to treat them as active required Agents.
- [x] 2.6 Integrate `dispatchDecision.effectiveRequiredAgents` into missing-output and failed-gate evaluation.
- [x] 2.7 Add `main_agent_dispatch_awareness` to failed hard gates when self-check, dynamic dispatch policy, or unregistered Agent activation rules fail.
- [x] 2.8 Add `layoutReadabilityAcceptable` to visual layout required checks and summary failures.

## 3. Workflow Dispatch Integration

- [x] 3.1 Update `core/orchestrator/workflow_dispatch.py` so blocked A-to-A contract reasons include main Agent self-check and dispatch decision failures without duplicating the contract rules.
- [x] 3.2 Ensure `orchestrate_request()` reports `mainAgentSelfCheck` and `dispatchDecision` inside `a_to_a_task_contract` for every high-risk request.
- [x] 3.3 Update route audit output only if needed to expose blocked main Agent dispatch awareness in deferred / not-claimable evidence.

## 4. Manifest And Agent Rules

- [x] 4.1 Update `agents/pipeline/pipeline_manifest.json` with `orchestration.main_agent_identity`.
- [x] 4.2 Add `orchestration.dynamic_dispatch_policy` defining registered-only automatic dispatch, required reasoning, and high-risk trigger scope.
- [x] 4.3 Add `orchestration.unregistered_agent_request_policy` requiring `needs_reviewed_package` / `needs_openspec_change` for new Agent requests.
- [x] 4.4 Add or update forbidden patterns for silent unregistered Agent activation and self-check-free completion claims.
- [x] 4.5 Update `agents/pipeline/README.md` and `agents/COMMON_PROMPT_CONTRACT.md` to explain the main Agent identity and dispatch boundary in Chinese.

## 5. Gate Check CLI

- [x] 5.1 Extend `scripts/run_a_to_a_orchestration_gate_check.py` manifest checks for `main_agent_identity`, `dynamic_dispatch_policy`, and `unregistered_agent_request_policy`.
- [x] 5.2 Extend contract checks for main Agent self-check pass, registered dynamic addition, unregistered Agent candidate handling, and blocked unregistered activation.
- [x] 5.3 Extend visual layout checks so `layoutReadabilityAcceptable` is required in pass outputs.
- [x] 5.4 Ensure the CLI report records checked / notChecked evidence boundary and does not claim real CAD validation.

## 6. Documentation And Records

- [x] 6.1 Update `docs/architecture/cad-agent-task-chain.md` with a new subsection for main Agent self-check and dynamic dispatch awareness.
- [x] 6.2 Update `docs/architecture/system-asset-sedimentation-protocol.md` to clarify that the main Agent may request new global Agents only as reviewed-package candidates.
- [x] 6.3 Update `docs/governance/cad-agent-rules.md` and `AGENTS.md` if the global rule boundary changes.
- [x] 6.4 Update `CORE_CONTEXT_BRIEF.md` with a short current-facts entry after implementation and verification.
- [x] 6.5 Update `docs/status/current.md` and `docs/status/changelog.md`; update `docs/status/issues.md` only if implementation uncovers a risk or regression.

## 7. Verification

- [x] 7.1 Run focused tests for A-to-A task contract behavior.
- [x] 7.2 Run workflow dispatch regression tests.
- [x] 7.3 Run `scripts/run_a_to_a_orchestration_gate_check.py` and save / review its JSON output if an output path is used.
- [x] 7.4 Run `openspec.cmd validate --all --strict --json --no-interactive`.
- [x] 7.5 Run repo-relevant no-CAD checks needed for this orchestration-only change and state that no real CAD / DWG write was part of the evidence.
- [x] 7.6 Review `git diff` to ensure unrelated user changes were not reverted or reformatted.
