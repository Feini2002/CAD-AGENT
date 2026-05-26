# Demand Side Agent Suite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a data-driven demand-side role Agent layer that records cross-scene user demands and runs them through existing Core benchmark pipelines.

**Architecture:** Demand personas remain data-only under `agents/demand_side/`. `core.demand_agents` loads and validates role and case records, while `core.benchmarks.runner` gets a small `demand_case` pipeline that delegates to existing `object_spec`, `composition_spec`, or `blank_shell` behavior.

**Tech Stack:** Python standard library, `unittest`, existing benchmark runner, JSON fixtures.

---

### Task 1: Demand Role Registry

**Files:**
- Create: `agents/demand_side/role_agents.json`
- Create: `agents/demand_side/README.md`
- Create: `core/demand_agents/__init__.py`
- Create: `core/demand_agents/loaders.py`
- Test: `tests/core/test_demand_agents.py`

- [ ] **Step 1: Write failing tests**

Add tests that require at least 12 roles and the 6 current scene ids.

- [ ] **Step 2: Run tests to verify failure**

Run: `$py -m unittest tests.core.test_demand_agents`
Expected: fail because `core.demand_agents` does not exist or role registry is missing.

- [ ] **Step 3: Add loader and role registry**

Implement JSON loading, required field checks, safe id checks, duplicate id rejection, and scene coverage summary.

- [ ] **Step 4: Run tests to verify pass**

Run: `$py -m unittest tests.core.test_demand_agents`
Expected: all tests in this file pass.

### Task 2: Demand Case Benchmark Pipeline

**Files:**
- Create: `examples/benchmarks/demand_side_agent_benchmark.json`
- Modify: `core/benchmarks/runner.py`
- Modify: `tests/core/test_benchmarks.py`
- Test: `tests/core/test_demand_agents.py`

- [ ] **Step 1: Write failing benchmark tests**

Add tests that run `examples/benchmarks/demand_side_agent_benchmark.json` and assert every result carries demand metadata.

- [ ] **Step 2: Run focused tests to verify failure**

Run: `$py -m unittest tests.core.test_demand_agents tests.core.test_benchmarks.BenchmarkRunnerTests.test_demand_side_agent_benchmark_runs_cross_scene_demands`
Expected: fail because `demand_case` is unsupported.

- [ ] **Step 3: Implement `demand_case` delegation**

Validate demand metadata, load the referenced role, delegate to the requested underlying pipeline, and merge demand metadata into metrics / actual output.

- [ ] **Step 4: Run focused tests**

Run: `$py -m unittest tests.core.test_demand_agents tests.core.test_benchmarks.BenchmarkRunnerTests.test_demand_side_agent_benchmark_runs_cross_scene_demands`
Expected: pass.

### Task 3: Documentation And Status Sync

**Files:**
- Modify: `CORE_RESTRUCTURE_PLAN.md`
- Modify: `CORE_STATUS.md`
- Modify: `CAD_AGENT_STATUS.md`
- Modify: `CAD_AGENT_CHANGELOG.md`
- Modify: `docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md`

- [ ] **Step 1: Update status docs**

Record the demand-side Agent layer as a demand/benchmark expansion, not Scene Product completion.

- [ ] **Step 2: Run verification**

Run focused unit tests and demand benchmark suite. If time permits, run full `unittest discover -s tests`.
