## 1. Contract And Baseline

- [x] 1.1 Validate the new OpenSpec change with `openspec.cmd status --change upgrade-training-workbench-flightdeck --json` and `openspec.cmd validate --all --strict --json --no-interactive`.
- [x] 1.2 Record the MVP scope in the implementation notes: `workbenchV3` draft data, command center view, gateboard, next training candidates, source health, persistent inspector hooks, and v3 agent-check gates.
- [x] 1.3 Confirm the dirty worktree before implementation and avoid reverting unrelated existing changes.

## 2. Data Contract MVP

- [x] 2.1 Add focused tests for a compact `workbenchV3` draft namespace while keeping root `schemaVersion=2` during the first slice.
- [x] 2.2 Add a small `core/training_workbench/` package with pure functions for `meta`, `sourceRegistry`, `gateboard`, `nextTrainingCandidates`, `agentGraph`, `evidenceBundles`, and `commandCenter` view data.
- [x] 2.3 Wire `scripts/build_capability_map_data.py` to include `workbenchV3` without removing existing v2 fields or legacy render compatibility.
- [x] 2.4 Ensure `workbenchV3.sourcePolicy.derivedOnly=true` and large reports, screenshots, traces, and readback arrays are referenced by path instead of embedded.

## 3. Source Health And Gateboard

- [x] 3.1 Derive `sourceRegistry` from `docs/training/training-sources.json`, including `id`, `kind`, `role`, `status`, `path`, `exists`, and historical-only classification.
- [x] 3.2 Derive `syncHealth` and `gateboard` items for snapshot freshness, coverage source, agent check status, source health, encoding placeholder status, data-bloat / evidence closure placeholder status, Table C boundary, and derived snapshot policy.
- [x] 3.3 Ensure archived training evidence cannot mark a training item accepted, systemized, verified, or learned in the new view model.

## 4. Agent System Observability MVP

- [x] 4.1 Build `agentGraph.nodes` for CAD Designer Agent, pipeline agents, scene agents, Prompt contract nodes, hard gate nodes, and evidence source nodes using existing manifests and prompt contracts.
- [ ] 4.2 Build `agentGraph.edges` for responsible-agent ownership, pipeline flow, source refs, learning refs, gate requirements, and trace/evidence refs when available. Current slice covers responsible-agent, prompt-contract, source, and gate-source edges; pipeline-flow / learning / trace edges remain follow-up.
- [x] 4.3 Add tests that selected training programs can resolve responsible agents, related prompt contracts, evidence bundles, and source refs through stable IDs.

## 5. Command Center UI

- [x] 5.1 Add an `overview` / command-center tab to `capability-map.html` and make it the default active view while keeping existing `plan`, `agents`, `failures`, `traces`, and `boundary` views available.
- [x] 5.2 Render next training candidates with route mode, reason, responsible agents, evidence requirements, and blocking conditions.
- [x] 5.3 Render gateboard health and source health with distinct states for `pass`, `warning`, `blocked`, `not_checked`, `derived`, and `archived_only`.
- [x] 5.4 Render a command-center evidence-boundary panel that separates Table C, training progress, Agent maturity, Prompt readiness, trace, screenshot, and CAD readback evidence.
- [x] 5.5 Add persistent inspector behavior or hooks so training item / Agent / source / trace selections can share one detail panel in later slices.

## 6. Workbench Agent Check

- [x] 6.1 Extend `scripts/run_training_workbench_agent_check.py` to require `workbenchV3`, command-center data, source registry, gateboard, next training candidates, agent graph basics, and evidence boundary fields.
- [x] 6.2 Add checks that v3 does not classify derived snapshots as active fact sources and does not use archived sources to drive accepted completion states.
- [x] 6.3 Add HTML checks for the overview tab, command-center mount point, gateboard copy, source-health copy, and persistent evidence-boundary copy.

## 7. Verification And Visual QA

- [x] 7.1 Run focused unit tests for training workbench sync / v3 data / agent graph.
- [x] 7.2 Run `scripts/sync_training_workbench.py --skip-coverage` and `scripts/run_training_workbench_agent_check.py`.
- [x] 7.3 Run `openspec.cmd validate --all --strict --json --no-interactive`.
- [x] 7.4 Run a browser visual smoke check of the generated workbench on desktop and narrow viewport, checking no JavaScript errors, no obvious Chinese overflow, no mojibake, default command center visibility, and evidence boundary visibility.
- [x] 7.5 Update status / handoff / CORE_CONTEXT_BRIEF only if implementation changes active training order, evidence boundaries, or user-facing operation instructions. Reviewed; no status or handoff update required for this first display/data-contract slice.
