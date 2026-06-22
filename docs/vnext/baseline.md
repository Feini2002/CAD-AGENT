# CAD-AGENT vNext VN-00 Baseline

Status: `validated` for VN-00 freeze and baseline recording.

Recorded at: `2026-06-22T21:59:22+08:00`

## Git Baseline

- Branch: `vnext-main`
- Baseline commit: `77cd10bfc58d3cb7fd0b06c2bce0a471213027e4`
- Local baseline tag: `legacy-baseline-2026-06-22`
- Remote tag: not pushed by VN-00
- Initial worktree status before VN-00 edits: only `?? CAD_AGENT_vNext_Doc_Pack/`
- Existing isolated workspace: linked git worktree at `C:\Users\User\Desktop\CAD Agent WorkTree`

## Source Document Pack

`CAD_AGENT_vNext_Doc_Pack/` contains exactly:

- `README.md`
- `docs/vnext/ARCHITECTURE_DECISION.md`
- `docs/vnext/IMPLEMENTATION_MASTER_PLAN.md`

VN-00 copied the two vNext authority documents into `docs/vnext/` and left the source pack untouched.

## Python Environment

- Standard `python` command: unavailable on PATH during VN-00.
- Standard `py` launcher: unavailable on PATH during VN-00.
- Baseline tests were run with `C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe`.
- Detected Python version: `Python 3.12.13`.
- `pytest` is not installed in the available Python runtimes before VN-01 dependency setup.

## Baseline Test Results

Command requested by plan:

```powershell
python -m unittest discover -s tests -q
```

Result: not runnable because `python` is not on PATH.

Equivalent local baseline command run:

```powershell
& "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe" -m unittest discover -s tests -q
```

Result:

- Ran: `1616`
- Failures: `4`
- Errors: `3`
- Skipped: `2`

Observed failure/error groups:

- `tests/core/test_model_agent_chain_runtime.py`: model trace artifact directories missing before writing `context_leak_audit.json` or `export_manifest.json`.
- `tests/core/test_legacy_entrypoint_custody_closure.py`: entrypoint custody still reports unregistered `scripts/cad_agent_harness.py` and `scripts/cad_session_host.py`.
- `tests/core/test_model_agent_live_collab_cli.py`: fixture CLI returned non-zero.
- `tests/core/test_model_prompt_library.py`: prompt-pack fixture/codex review paths returned unavailable or did not call the runner.

The old test run temporarily rewrote tracked `output/validation_runs/**` evidence files; those generated tracked diffs were restored after recording this baseline to avoid protected evidence pollution. Ignored `output/test_artifacts/**` remains local test scratch.

## VN-00 Verification

Command:

```powershell
& "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe" -m unittest discover -s tests\vnext -q
```

Result: `4` tests ran, `OK`.

Command:

```powershell
& "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe" scripts\vnext\check_legacy_expansion.py --baseline-ref legacy-baseline-2026-06-22
```

Result: `pass`, `checkedAddedPathCount=10`, `findings=[]`.

Plan command:

```powershell
python -m pytest tests/vnext/test_legacy_expansion_freeze.py -q
```

Result: not run in the current baseline environment because neither available Python runtime has `pytest` installed before VN-01 dependency setup.

## Governance Audit Results

Command:

```powershell
& "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe" scripts\run_doc_governance_audit.py
```

Result: `pass`, `finding_count=0`.

Command:

```powershell
& "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe" scripts\run_entrypoint_custody_audit.py
```

Result: `blocked`.

Findings recorded:

- `scripts/cad_agent_harness.py` is an unregistered repo entrypoint.
- `scripts/cad_session_host.py` is an unregistered repo entrypoint.
- `CORE_RESTRUCTURE_PLAN.md` still references `scripts/cad_agent_harness.py` as an active entrypoint.
- `docs/status/current.md` still references `scripts/cad_session_host.py` as an active entrypoint.

VN-00 records these as pre-existing custody blockers and does not repair them.

## AutoCAD And CAD Connectivity

- `acad.exe` process during VN-00 read-only probe: not detected.
- `cad-session-host` port `8765` during VN-00 read-only probe: not listening.
- Real CAD write/readback was not run in VN-00.
- Current DWG for real preview requires a user-opened AutoCAD document and explicit scoped authorization.
- Default safety boundary remains: write only `CODEX_PREVIEW`, require created-handle readback, keep `savedCurrentDwg=false`, do not write formal layers.

## Current CAD Preview / Readback Entry Candidates

- `scripts/cad_agent_harness.py` with `preview --backend cad-session-host` is the current legacy harness CLI path referenced by migration evidence.
- `core/contracts/cad_agent_harness.py` is the ToolCard / Adapter Registry aware harness implementation.
- `scripts/cad_session_host.py` and `core/cad_io/cad_session_host.py` are the current CAD Session Host bridge candidates for existing AutoCAD preview/readback.
- `core/contracts/native_thin_backend.py` and `native_plugins/native_thin_backend/NativeThinBackendCommands.cs` are the P13F scoped native thin live-spike path only.
- `scripts/render_preview.py` and `core/verification/render_preview.py` provide visual preview helpers; screenshots remain visual aid only and do not replace handle readback.

Reusable evidence references:

- P9 session-host live verify: `output/validation_runs/phase9-session-host-live-verify-20260619-235547/`
- P10 two-run live rehearsal: `output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/`
- P13F native thin live spike: `output/validation_runs/phase13f-native-thin-live-spike-20260621-160230/`
- P14 no-CAD engineering kernel DiffPackage: `output/validation_runs/phase14-engineering-kernel-diff-package-20260621-162452/`

## Frozen Legacy Surfaces

The following remain frozen before Gate 0:

- legacy orchestrator expansion
- legacy pipeline agent expansion
- formal training / curriculum expansion
- training workbench expansion
- Table A/B/C or coverage-surface expansion
- root architecture/control-plane Markdown sprawl
- new legacy-style `scripts/run_*.py` entrypoints

`scripts/vnext/check_legacy_expansion.py` enforces the VN-00 freeze for newly added paths outside the vNext allowlist.

## Proves

- Current repository baseline commit, branch and source document pack are recorded.
- Legacy full-test baseline is reproducible in the available local Python environment, including current failures.
- Existing governance audits are recorded without expanding the PR scope.
- vNext authority documents are present under `docs/vnext/`.
- Legacy expansion freeze checker has automated coverage.

## Does Not Prove

- No new real CAD geometry was created.
- No Gate 0 fake or real evaluation was run.
- No AutoCAD connection, readback, screenshot, or no-save live proof was produced in VN-00.
- No old test failure or entrypoint custody blocker was repaired.
- No vNext runtime, domain contracts, solver, compiler, fake backend, Skill, or Gate 0 harness behavior is implemented yet.

## VN-01 Project Identity Record

Recorded at: `2026-06-22T22:11:34+08:00`

VN-01 added the minimal Python project identity:

- `pyproject.toml`
- `src/cad_agent_vnext/__init__.py`
- `package.json` metadata marking Node/Worker as optional infrastructure
- root control-plane text already points to vNext Gate 0 and the vNext authority docs

Editable install command:

```powershell
& '.venv\Scripts\python.exe' -m pip install -e ".[dev]"
```

Result: editable install succeeded in the repository-local `.venv`.

Targeted verification:

```powershell
& '.venv\Scripts\python.exe' -c "import cad_agent_vnext; print(cad_agent_vnext.__version__)"
```

Result: `0.1.0`.

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext -q
```

Result: `8 passed`.

```powershell
& '.venv\Scripts\python.exe' scripts\vnext\check_legacy_expansion.py --baseline-ref legacy-baseline-2026-06-22
```

Result: `pass`, `findings=[]`.

Legacy baseline comparison used the same Python environment as VN-00:

```powershell
& "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe" -m unittest discover -s tests -q
```

Result:

- Ran: `1624`
- Failures: `4`
- Errors: `3`
- Skipped: `2`

The failure/error categories match VN-00 baseline. The count increased by the 8 new vNext tests, all of which passed. A full run inside the new `.venv` was also attempted, but it adds expected `pywin32` optional-extra failures because VN-01 installed `.[dev]` only, not `.[autocad]`; it is not used as the legacy baseline comparison.

VN-01 does not implement CLI behavior yet. The `cad-agent-vnext` entry point is declared in project metadata as required by the plan; `src/cad_agent_vnext/cli.py` belongs to VN-02.

## VN-02 Package Skeleton And Boundary Record

Recorded at: `2026-06-22T22:16:33+08:00`

VN-02 added the minimal package skeleton and dependency boundary checks:

- `src/cad_agent_vnext/app/__init__.py`
- `src/cad_agent_vnext/domain/__init__.py`
- `src/cad_agent_vnext/planning/__init__.py`
- `src/cad_agent_vnext/tools/__init__.py`
- `src/cad_agent_vnext/adapters/__init__.py`
- `src/cad_agent_vnext/runtime/__init__.py`
- `src/cad_agent_vnext/verification/__init__.py`
- `src/cad_agent_vnext/policy/__init__.py`
- `src/cad_agent_vnext/cli.py`
- `scripts/vnext/check_import_boundaries.py`
- `tests/vnext/test_cli_smoke.py`
- `tests/vnext/test_import_boundaries.py`

Targeted verification:

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext -q
```

Result: `15 passed`.

```powershell
& '.venv\Scripts\python.exe' scripts\vnext\check_import_boundaries.py
```

Result: `pass`, `findings=[]`.

```powershell
& '.venv\Scripts\python.exe' scripts\vnext\check_legacy_expansion.py --baseline-ref legacy-baseline-2026-06-22
```

Result: `pass`, `findings=[]`.

```powershell
& '.venv\Scripts\cad-agent-vnext.exe' version
& '.venv\Scripts\cad-agent-vnext.exe' doctor
```

Result:

- `version` printed `cad-agent-vnext 0.1.0`.
- `doctor` emitted `cad-agent-vnext-doctor/v1` JSON.
- `doctor` reported `cad.connected=false` and `cad.modified=false`; it did not connect to or modify CAD.

Legacy baseline comparison used the same Python environment as VN-00:

```powershell
& "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe" -m unittest discover -s tests -q
```

Result:

- Ran: `1631`
- Failures: `4`
- Errors: `3`
- Skipped: `2`

The failure/error categories match VN-00 baseline. The count increased by the 15 vNext tests now present, all of which passed.

VN-02 does not implement business logic, domain contracts, fake backend, real CAD adapter, solver, compiler, verification rules, repair, Skill loop, or Gate 0 eval behavior.

## VN-03 Domain Contracts Record

Recorded at: `2026-06-22T22:21:51+08:00`

VN-03 added the initial Pydantic authority source for the vNext contracts:

- `UserBrief`
- `DrawingSnapshot`
- `SceneSpec`
- `Primitive`
- `CadPatch`
- `ExecutionReceipt`
- `VerificationReport`

The package also added `scripts/vnext/export_schemas.py` and generated JSON schemas under `schemas/vnext/generated/`.

Targeted verification:

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext\domain -q
```

Result: `30 passed`.

```powershell
& '.venv\Scripts\python.exe' scripts\vnext\export_schemas.py --check
```

Result: `pass`, `schemaCount=7`, `stale=[]`.

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext -q
```

Result: `45 passed`.

```powershell
& '.venv\Scripts\python.exe' scripts\vnext\check_import_boundaries.py
& '.venv\Scripts\python.exe' scripts\vnext\check_legacy_expansion.py --baseline-ref legacy-baseline-2026-06-22
```

Result: both `pass`, `findings=[]`.

Legacy baseline comparison used the same Python environment as VN-00:

```powershell
& "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe" -m unittest discover -s tests -q
```

Result:

- Ran: `1631`
- Failures: `4`
- Errors: `3`
- Skipped: `2`

The failure/error categories match VN-00 baseline. The VN-03 pytest-only domain tests are covered by `pytest tests\vnext`, not by `unittest discover`.

VN-03 does not implement run workspace, fake backend, real CAD adapter, transaction gateway, object catalog, solver, compiler, verification execution, repair, Skill loop, or Gate 0 eval behavior.

## VN-04 Run Workspace Record

Recorded at: `2026-06-22T22:26:06+08:00`

VN-04 added the first run workspace and tool envelope layer:

- `src/cad_agent_vnext/app/run_workspace.py`
- `src/cad_agent_vnext/app/run_service.py`
- `src/cad_agent_vnext/tools/envelopes.py`
- `tests/vnext/app/test_run_workspace.py`

Implemented behavior:

- unique run IDs with random suffixes;
- configurable output root;
- standard run directories: `screenshots/`, `debug/`, `events.jsonl`;
- path escape prevention;
- atomic stable UTF-8 JSON artifact writes;
- event recording with sequence numbers;
- debug artifacts excluded from evidence refs;
- `ToolEnvelope` contract for tool/CLI style returns;
- `begin_run()` writes `user_brief.json` and returns next action `inspect` without touching CAD.

Targeted verification:

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext\app -q
```

Result: `8 passed`.

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext -q
```

Result: `53 passed`.

```powershell
& '.venv\Scripts\python.exe' scripts\vnext\check_import_boundaries.py
& '.venv\Scripts\python.exe' scripts\vnext\check_legacy_expansion.py --baseline-ref legacy-baseline-2026-06-22
```

Result: both `pass`, `findings=[]`.

Legacy baseline comparison used the same Python environment as VN-00:

```powershell
& "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe" -m unittest discover -s tests -q
```

Result:

- Ran: `1631`
- Failures: `4`
- Errors: `3`
- Skipped: `2`

The failure/error categories match VN-00 baseline.

VN-04 does not implement fake backend, real CAD adapter, transaction gateway, object catalog, solver, compiler, verification execution, repair, Skill loop, or Gate 0 eval behavior. `begin_run()` does not inspect, connect to, write, readback, screenshot, or save CAD.

## VN-05 CadBackend Port And Fake Backend Record

Recorded at: `2026-06-22T22:30:32+08:00`

VN-05 completed the initial backend port and in-memory fake backend:

- expanded `src/cad_agent_vnext/domain/ports.py`;
- added `src/cad_agent_vnext/adapters/fake_backend.py`;
- added `tests/vnext/adapters/test_fake_backend.py`.

Implemented behavior:

- `CadBackend` protocol now includes `inspect_document`, `apply_patch`, `readback`, `capture_view`, and `rollback`;
- fake backend stores primitives in memory;
- fake backend generates stable handles such as `F0001`;
- fake backend computes bbox for basic primitives;
- create / update / delete are supported for preview entities;
- rollback restores a prior backend state;
- `saved_current_dwg` is always false;
- wrong-layer and partial-create failure injection are covered;
- repeated transaction IDs are rejected as blocked.

Targeted verification:

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext\adapters -q
```

Result: `7 passed`.

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext -q
```

Result: `60 passed`.

```powershell
& '.venv\Scripts\python.exe' scripts\vnext\check_import_boundaries.py
& '.venv\Scripts\python.exe' scripts\vnext\export_schemas.py --check
& '.venv\Scripts\python.exe' scripts\vnext\check_legacy_expansion.py --baseline-ref legacy-baseline-2026-06-22
```

Result: all `pass`.

Legacy baseline comparison used the same Python environment as VN-00:

```powershell
& "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe" -m unittest discover -s tests -q
```

Result:

- Ran: `1631`
- Failures: `4`
- Errors: `3`
- Skipped: `2`

The failure/error categories match VN-00 baseline. The VN-05 adapter tests are pytest-only and are covered by `pytest tests\vnext`.

VN-05 does not implement real CAD adapter, transaction gateway policy, object catalog, solver, compiler, verification execution, repair, Skill loop, or Gate 0 eval behavior. Fake `capture_view()` writes a JSON visual-aid placeholder only; it is not real CAD evidence.

## VN-06 Legacy AutoCAD Adapter Record

Recorded at: `2026-06-22T22:37:56+08:00`

VN-06 automatic adapter work completed but the package is blocked before validation because the required real CAD smoke did not pass on this workstation.

Implemented:

- added `src/cad_agent_vnext/adapters/legacy_mapping.py`;
- added `src/cad_agent_vnext/adapters/legacy_autocad_backend.py`;
- added `tests/vnext/adapters/test_legacy_mapping.py`;
- added `scripts/vnext/run_real_cad_backend_smoke.py`.

Implemented behavior:

- vNext primitives map through an explicit Gate 0 mapping table;
- rectangle uses `draw_polyline(closed=True)` for a single stable LWPOLYLINE readback;
- ellipse maps to a polyline approximation;
- `LegacyAutoCadBackend` implements the `CadBackend` protocol around the existing preview driver surface;
- legacy imports are confined to `legacy_autocad_backend.py`;
- create-only preview patches return `ExecutionReceipt` with created handles, semantic mapping, layer readback, bbox readback, and `saved_current_dwg=false`;
- rollback deletes only handles created by the matching transaction when the driver exposes `delete_entity_by_handle`;
- smoke script draws one rectangle, one circle, and one text, then requires readback and rollback.

Targeted verification:

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext\adapters -q
```

Result: `12 passed`.

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext -q
```

Result: `65 passed`.

```powershell
& '.venv\Scripts\python.exe' scripts\vnext\check_import_boundaries.py
```

Result: `pass`, `findings=[]`.

Real smoke attempt with the project `.venv`:

```powershell
& '.venv\Scripts\python.exe' scripts\vnext\run_real_cad_backend_smoke.py --preview-only --rollback-after-check
```

Result: `blocked`.

Blocking reason: `.venv` does not include `pywin32`, so it cannot use AutoCAD COM.

Real smoke attempt with the legacy CAD-MCP Python environment:

```powershell
& "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe" scripts\vnext\run_real_cad_backend_smoke.py --preview-only --rollback-after-check
```

Result: `blocked`.

Report: `output\vnext\runs\vn06-real-cad-smoke-20260622T143740Z\vn06_real_cad_backend_smoke.json`.

Blocking reason: no active `AutoCAD.Application` instance was attachable; COM diagnostics reported `acadProcessRunning=False`.

VN-06 is therefore not validated. Per `IMPLEMENTATION_MASTER_PLAN.md` sections 12.7-12.8, real-CAD Gate 0 must not proceed until one real CAD smoke passes with created handle readback, non-empty bbox, `CODEX_PREVIEW` layer, `savedCurrentDwg=false`, and verified rollback. Fake/backend development may continue, but cannot be used to claim VN-06 real CAD validation.

## VN-07 CadTransactionGateway And Safety Policy Record

Recorded at: `2026-06-22T22:50:07+08:00`

VN-07 fake/backend development completed and was verified, but full migration remains upstream-blocked by the VN-06 real CAD smoke.

Implemented:

- added `src/cad_agent_vnext/policy/safety_policy.py`;
- added `src/cad_agent_vnext/policy/transaction_policy.py`;
- added `src/cad_agent_vnext/app/transaction_gateway.py`;
- added `tests/vnext/policy/test_transaction_gateway.py`;
- exported `CadTransactionGateway` and policy helpers from package `__init__` files.

Implemented behavior:

- Gate 0 policy constants are fixed: preview-only, `CODEX_PREVIEW`, no save, no formal layer, no general delete, max 100 created entities, max 2 repair rounds;
- gateway is the only app/tool execution entry point for backend writes;
- patch policy blocks wrong target layer, save requests, primitive layer drift, too many entities, unsupported update/delete targets, and duplicate transaction IDs before backend execution;
- local repair can update/delete only handles present in a prior receipt and matching the semantic ID;
- gateway applies patch, immediately readbacks created handles, audits receipt/readback, and rolls back on backend/receipt/readback policy failures;
- receipt audit checks status, `saved_current_dwg`, semantic mapping, created handle readback, `CODEX_PREVIEW` layer, bbox presence, and entity budget;
- rollback failure is reported without hiding the original policy failure.

Targeted verification:

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext\policy -q
```

Result: `23 passed`.

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext -q
```

Result: `88 passed`.

```powershell
& '.venv\Scripts\python.exe' scripts\vnext\check_import_boundaries.py
& '.venv\Scripts\python.exe' scripts\vnext\export_schemas.py --check
& '.venv\Scripts\python.exe' scripts\vnext\check_legacy_expansion.py --baseline-ref legacy-baseline-2026-06-22
```

Result: all `pass`.

Doc governance:

```powershell
& '.venv\Scripts\python.exe' scripts\run_doc_governance_audit.py
```

Result: `pass`, `finding_count=0`.

Legacy baseline comparison used the same Python environment as VN-00:

```powershell
& "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe" -m unittest discover -s tests -q
```

Result:

- Ran: `1631`
- Failures: `4`
- Errors: `3`
- Skipped: `2`

The failure/error categories match VN-00 baseline.

VN-07 does not validate VN-06 real CAD smoke, object catalog, relation solver, scene compiler, verification/repair, Skill loop, eval harness, or real-CAD acceptance.

## VN-08 Primitive IR And Object Catalog Record

Recorded at: `2026-06-22T22:56:58+08:00`

VN-08 fake/backend development completed and was verified, but full migration remains upstream-blocked by the VN-06 real CAD smoke.

Implemented:

- added `config/vnext/object_catalog.json`;
- added `src/cad_agent_vnext/planning/object_catalog.py`;
- added `src/cad_agent_vnext/planning/footprints.py`;
- added `src/cad_agent_vnext/planning/object_generators.py`;
- added `tests/vnext/planning/test_object_catalog.py`;
- added `tests/vnext/planning/test_object_generators.py`;
- exported planning helpers from `src/cad_agent_vnext/planning/__init__.py`.

Implemented behavior:

- object catalog defines only five Gate 0 atomic objects: desk, monitor, keyboard, mouse, vase;
- catalog resolves default dimensions and enforces min/max bounds where provided;
- unsupported catalog kinds return structured `unsupported_object_kind` lookup results;
- generator registry maps each catalog generator to exactly one atomic object generator;
- object generators accept `SceneObjectSpec + ResolvedPose` and emit only per-object primitives;
- generated primitives propagate semantic ID, use `CODEX_PREVIEW`, and stay under the small primitive budget;
- footprint helpers support rotation, bbox calculation, primitive bbox calculation, and primitive group bbox calculation;
- footprint bbox and primitive bbox are covered by tests;
- production generator code does not include a fixed computer-desk scene function, prompt text route, or backend write call.

Targeted verification:

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext\planning -q
```

Result: `18 passed`.

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext -q
```

Result: `106 passed`.

```powershell
& '.venv\Scripts\python.exe' scripts\vnext\check_import_boundaries.py
& '.venv\Scripts\python.exe' scripts\vnext\export_schemas.py --check
& '.venv\Scripts\python.exe' scripts\vnext\check_legacy_expansion.py --baseline-ref legacy-baseline-2026-06-22
```

Result: all `pass`.

Doc governance:

```powershell
& '.venv\Scripts\python.exe' scripts\run_doc_governance_audit.py
```

Result: `pass`, `finding_count=0`.

Legacy baseline comparison used the same Python environment as VN-00:

```powershell
& "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe" -m unittest discover -s tests -q
```

Result:

- Ran: `1631`
- Failures: `4`
- Errors: `3`
- Skipped: `2`

The failure/error categories match VN-00 baseline.

VN-08 does not validate VN-06 real CAD smoke, relation solver, scene compiler, verification/repair, Skill loop, eval harness, or real-CAD acceptance.

## VN-09 General Relation Solver Record

Recorded at: `2026-06-22T23:04:11+08:00`

VN-09 fake/planning development completed and was verified, but full migration remains upstream-blocked by the VN-06 real CAD smoke.

Implemented:

- added `src/cad_agent_vnext/planning/anchors.py`;
- added `src/cad_agent_vnext/planning/relation_graph.py`;
- added `src/cad_agent_vnext/planning/relation_solver.py`;
- added `src/cad_agent_vnext/planning/candidate_scoring.py`;
- added `tests/vnext/planning/test_relation_solver.py`;
- added `tests/vnext/planning/test_relation_variants.py`;
- extended `src/cad_agent_vnext/planning/footprints.py` with bbox overlap helpers;
- exported `solve_scene_relations` and `RelationSolveResult` from planning package init.

Implemented behavior:

- anchor points are computed generically from surface bbox and margin for the nine required anchors;
- candidate scoring weights are fixed in code and covered by tests;
- relation graph validates references, produces topological order, and reports cycles/missing references without guessing success;
- relation solver uses surface-local coordinates, then transforms poses to world coordinates;
- `on: desk`, `anchor`, `in_front_of`, `left_of`, `right_of`, `align_x`, and `align_y` are handled generically through placement fields;
- objects on a surface must stay inside the surface local bbox;
- overlap and nearby snapshot collisions block with explicit unsatisfied constraints;
- standard scene, mouse left/right, double monitor, wider desk, narrow feasible, narrow infeasible, vase rear-right, rotated desk, missing reference, cycle, and nearby collision cases are covered;
- production relation solver source is guarded by tests against exact prompt routes and fixed scene template names.

Targeted verification:

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext\planning -q
```

Result: `33 passed`.

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext -q
```

Result: `121 passed`.

```powershell
& '.venv\Scripts\python.exe' scripts\vnext\check_import_boundaries.py
& '.venv\Scripts\python.exe' scripts\vnext\export_schemas.py --check
& '.venv\Scripts\python.exe' scripts\vnext\check_legacy_expansion.py --baseline-ref legacy-baseline-2026-06-22
```

Result: all `pass`.

Doc governance:

```powershell
& '.venv\Scripts\python.exe' scripts\run_doc_governance_audit.py
```

Result: `pass`, `finding_count=0`.

Legacy baseline comparison used the same Python environment as VN-00:

```powershell
& "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe" -m unittest discover -s tests -q
```

Result:

- Ran: `1631`
- Failures: `4`
- Errors: `3`
- Skipped: `2`

The failure/error categories match VN-00 baseline.

VN-09 does not validate VN-06 real CAD smoke, scene compiler, verification/repair, Skill loop, eval harness, or real-CAD acceptance.

## VN-10 Scene Compiler To CadPatch Record

Recorded at: `2026-06-22T23:10:41+08:00`

VN-10 fake/planning development completed and was verified, but full migration remains upstream-blocked by the VN-06 real CAD smoke.

Implemented:

- added `src/cad_agent_vnext/planning/semantic_mapping.py`;
- added `src/cad_agent_vnext/planning/impact_estimator.py`;
- added `src/cad_agent_vnext/planning/scene_compiler.py`;
- added `tests/vnext/planning/test_scene_compiler.py`;
- exported `compile_scene` and `CompileSceneResult` from planning package init.

Implemented behavior:

- scene compiler validates `SceneSpec` input, resolves catalog defaults, selects a target region, solves relations, generates primitives, and emits a `CadPatch`;
- target region priority is explicit base/region first, then `DrawingSnapshot.target_region`, then a preview parking fallback;
- generated patch operations are grouped by semantic object and use only `CODEX_PREVIEW`;
- semantic mapping records object id to operation id, primitive ids, expected entity types, and bbox;
- impact estimator reports entity count, operation count, bbox, target layer, forbidden effects, and whether real-CAD confirmation is still required;
- stable semantic hash is used as the patch `transaction_id` for idempotent compile output;
- unsupported objects, infeasible relations, nearby snapshot collisions, and entity budget overflow block with explicit reasons;
- standard scene, mouse-left variant, double monitor, rotated desk, unknown object, infeasible narrow desk, nearby collision, stable hash, and entity budget cases are covered.

Targeted verification:

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext\planning -q
```

Result: `44 passed`.

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext -q
```

Result: `132 passed`.

```powershell
& '.venv\Scripts\python.exe' scripts\vnext\check_import_boundaries.py
& '.venv\Scripts\python.exe' scripts\vnext\export_schemas.py --check
& '.venv\Scripts\python.exe' scripts\vnext\check_legacy_expansion.py --baseline-ref legacy-baseline-2026-06-22
```

Result: all `pass`.

Doc governance:

```powershell
& '.venv\Scripts\python.exe' scripts\run_doc_governance_audit.py
```

Result: `pass`, `finding_count=0`.

Legacy baseline comparison used the same Python environment as VN-00:

```powershell
& "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe" -m unittest discover -s tests -q
```

Result:

- Ran: `1631`
- Failures: `4`
- Errors: `3`
- Skipped: `2`

The failure/error categories match VN-00 baseline.

VN-10 does not validate VN-06 real CAD smoke, verification/repair, Skill loop, eval harness, or real-CAD acceptance.

## VN-11 Verification And Minimal Repair Record

Recorded at: `2026-06-22T23:19:23+08:00`

VN-11 deterministic verification and minimal repair planning completed for the fake/backend slice, but full migration remains upstream-blocked by the VN-06 real CAD smoke.

Implemented:

- added `src/cad_agent_vnext/verification/geometry_checks.py`;
- added `src/cad_agent_vnext/verification/receipt_checks.py`;
- added `src/cad_agent_vnext/verification/relation_checks.py`;
- added `src/cad_agent_vnext/verification/scene_verifier.py`;
- added `src/cad_agent_vnext/verification/repair_planner.py`;
- updated `src/cad_agent_vnext/verification/__init__.py`;
- added `tests/vnext/verification/test_scene_verifier.py`.

Implemented behavior:

- verifier checks receipt/readback semantic handle presence, expected entity types, `CODEX_PREVIEW` layer, `savedCurrentDwg=false`, and bbox presence;
- verifier checks required object completeness, surface containment, severe overlap, keyboard/monitor front relation, mouse side relation, vase clearance through deterministic geometry;
- nearby handles from the pre-execution snapshot are protected against update/delete and bbox mutation;
- visual aid remains out of the deterministic pass/fail path;
- safety failures such as wrong layer, saved-current-DWG, and nearby-handle mutation are reported as blocked and are not auto-repaired;
- repair planner creates local `CadPatch` repair operations only for failed semantic IDs;
- missing objects produce `create` repair operations, while misplaced/overlapping/wrong-side objects produce `update` operations against prior receipt handles;
- repair planning is capped by `max_rounds=2` and does not redraw the full scene.

Targeted verification:

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext\verification\test_scene_verifier.py -q
```

Result: `7 passed`.

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext -q
```

Result: `139 passed`.

```powershell
& '.venv\Scripts\python.exe' scripts\vnext\check_import_boundaries.py
& '.venv\Scripts\python.exe' scripts\vnext\export_schemas.py --check
& '.venv\Scripts\python.exe' scripts\vnext\check_legacy_expansion.py --baseline-ref legacy-baseline-2026-06-22
```

Result: all `pass`; legacy expansion checked `80` added paths.

Doc governance:

```powershell
& '.venv\Scripts\python.exe' scripts\run_doc_governance_audit.py
```

Result: `pass`, `finding_count=0`.

Legacy baseline comparison used the same Python environment as VN-00:

```powershell
& "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe" -m unittest discover -s tests -q
```

Result:

- Ran: `1631`
- Failures: `4`
- Errors: `3`
- Skipped: `2`

The failure/error categories match VN-00 baseline.

VN-11 does not validate VN-06 real CAD smoke, Codex Skill trigger, CLI tool loop, eval harness, or real-CAD acceptance.

## VN-12 Codex Skill And Tool CLI Record

Recorded at: `2026-06-22T23:26:44+08:00`

VN-12 Codex-hosted fake tool loop completed and was verified, but full migration remains upstream-blocked by the VN-06 real CAD smoke.

Implemented:

- added `.agents/skills/cad-scene-authoring/SKILL.md`;
- added `.agents/skills/cad-scene-authoring/references/scene-spec.md`;
- added `.agents/skills/cad-scene-authoring/references/tool-loop.md`;
- added `.agents/skills/cad-scene-authoring/references/gate0-checklist.md`;
- added `src/cad_agent_vnext/tools/inspect_tools.py`;
- added `src/cad_agent_vnext/tools/scene_tools.py`;
- added `src/cad_agent_vnext/tools/cad_tools.py`;
- added `src/cad_agent_vnext/tools/verify_tools.py`;
- extended `src/cad_agent_vnext/cli.py`;
- extended `src/cad_agent_vnext/app/run_workspace.py`;
- added `tests/vnext/tools/test_tool_loop.py`;
- added `tests/vnext/test_skill_contract.py`.

Implemented behavior:

- CLI now exposes `begin-run`, `inspect`, `validate-scene`, `compile`, `execute-preview`, `verify`, `repair`, `rollback`, and `closeout`;
- each CLI command prints Tool Envelope JSON and reads/writes explicit run artifacts only;
- run workspace open/read helpers block path escape through run ids and artifact refs;
- Codex skill frontmatter targets CAD scene authoring and excludes repository architecture/status work;
- skill references describe SceneSpec authoring, the CLI tool loop, and Gate 0 safety checks;
- fake end-to-end loop covers begin, inspect, Codex-written `scene_spec.json`, validate, compile, execute-preview, verify, and closeout;
- `execute-preview` uses `CadTransactionGateway.execute(...)` rather than direct backend writes from tools;
- execute blocks before `cad_patch.json` exists;
- closeout blocks unless deterministic verification passed;
- repair command writes a local repair patch for failed semantic IDs and updates `cad_patch.json` for the next preview execution;
- real AutoCAD backend remains routed but still environment-blocked until the VN-06 smoke blocker is cleared.

Targeted verification:

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext\tools\test_tool_loop.py tests\vnext\test_skill_contract.py -q
```

Result: `8 passed`.

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext -q
```

Result: `147 passed`.

```powershell
& '.venv\Scripts\python.exe' scripts\vnext\check_import_boundaries.py
& '.venv\Scripts\python.exe' scripts\vnext\export_schemas.py --check
& '.venv\Scripts\python.exe' scripts\vnext\check_legacy_expansion.py --baseline-ref legacy-baseline-2026-06-22
```

Result: all `pass`; legacy expansion checked `90` added paths.

Doc governance:

```powershell
& '.venv\Scripts\python.exe' scripts\run_doc_governance_audit.py
```

Result: `pass`, `finding_count=0`.

Legacy baseline comparison used the same Python environment as VN-00:

```powershell
& "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe" -m unittest discover -s tests -q
```

Result:

- Ran: `1631`
- Failures: `4`
- Errors: `3`
- Skipped: `2`

The failure/error categories match VN-00 baseline.

VN-12 does not validate VN-06 real CAD smoke, eval harness, Gate 0 real-CAD acceptance, default vNext entrypoint, or production native plugin behavior.

## VN-13 Gate 0 Eval Harness Record

Recorded at: `2026-06-22T23:33:01+08:00`

VN-13 fake Gate 0 eval harness completed and was verified, but full migration remains upstream-blocked by the VN-06 real CAD smoke.

Implemented:

- added `evals/__init__.py`;
- added `evals/gate0/__init__.py`;
- added `evals/gate0/cases.jsonl`;
- added `evals/gate0/hidden_cases.example.jsonl`;
- added `evals/gate0/grader.py`;
- added `evals/gate0/anti_cheat.py`;
- added `evals/gate0/README.md`;
- added `scripts/vnext/run_gate0_eval.py`;
- added `tests/vnext/evals/test_gate0_eval.py`.

Implemented behavior:

- public Gate 0 cases include at least 10 main paraphrases plus direction/quantity variants;
- cases keep prompt metadata separate from deterministic `sceneSpecFixture` inputs, so production code does not route on exact prompts;
- fake case runner compiles SceneSpec, executes through `CadTransactionGateway`, verifies deterministic geometry, and grades object completeness, relation satisfaction, and safety;
- failure classifier maps failures to the VN-14 Gate 0 categories such as `readback_failure`, `relation_solver_failure`, `compiler_failure`, and `safety_block_expected`;
- anti-cheat checks public prompt leakage to source, hidden prompt leakage to skills, case id leakage, and forbidden combo route tokens;
- eval runner writes `summary.json`, `case_results.jsonl`, `failures.jsonl`, `safety_report.json`, `anti_cheat_report.json`, and `report.md`;
- eval summary uses pass/fail counts and pass rate, not legacy coverage percentage wording.

Targeted verification:

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext\evals\test_gate0_eval.py -q
```

Result: `6 passed`.

```powershell
& '.venv\Scripts\python.exe' scripts\vnext\run_gate0_eval.py --backend fake --cases evals\gate0\cases.jsonl --eval-run-id phase-vn13-check-2
```

Result: exit `0`; report path `output/vnext/evals/gate0/phase-vn13-check-2/`.

Eval summary:

- Case count: `12`
- Passed: `12`
- Failed: `0`
- Pass rate: `1.0`
- Safety violations: `0`
- Anti-cheat: `pass`

```powershell
& '.venv\Scripts\python.exe' evals\gate0\anti_cheat.py --root .
```

Result: `pass`.

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext -q
```

Result: `153 passed`.

```powershell
& '.venv\Scripts\python.exe' scripts\vnext\check_import_boundaries.py
& '.venv\Scripts\python.exe' scripts\vnext\export_schemas.py --check
& '.venv\Scripts\python.exe' scripts\vnext\check_legacy_expansion.py --baseline-ref legacy-baseline-2026-06-22
```

Result: all `pass`; legacy expansion checked `105` added paths.

Doc governance:

```powershell
& '.venv\Scripts\python.exe' scripts\run_doc_governance_audit.py
```

Result: `pass`, `finding_count=0`.

Legacy baseline comparison used the same Python environment as VN-00:

```powershell
& "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe" -m unittest discover -s tests -q
```

Result:

- Ran: `1631`
- Failures: `4`
- Errors: `3`
- Skipped: `2`

The failure/error categories match VN-00 baseline.

VN-13 does not validate VN-06 real CAD smoke, Gate 0 real-CAD acceptance, real CAD screenshot evidence, default vNext entrypoint, or production native plugin behavior.

## VN-14 Gate 0 Real-CAD Acceptance Record

Recorded at: `2026-06-22T23:37:25+08:00`

VN-14 real-CAD acceptance was evaluated and is `environment_blocked`. Fake Gate 0 remains valid as a fake/backend eval, but real Gate 0 must not be declared.

Implemented:

- added `scripts/vnext/check_gate0_real_acceptance.py`;
- added `tests/vnext/evals/test_gate0_real_acceptance.py`;
- updated `docs/vnext/MIGRATION_STATE.json` gate0 status to `environment_blocked`.

Implemented behavior:

- acceptance checker consumes fake eval summary, anti-cheat report, real-CAD smoke report, and worktree-clean state;
- checker requires fake eval status pass, fake pass rate >= `0.95`, zero safety violations, anti-cheat pass, real smoke status `succeeded`, `savedCurrentDwg=false`, and a clean worktree;
- checker returns `passed`, `failed`, or `environment_blocked` with concrete blocking reasons;
- environment-blocked decision explicitly says not to declare real Gate 0;
- VN-14 does not run arbitrary CAD writes itself; it consumes the scoped VN-06 real-smoke evidence.

Targeted verification:

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext\evals\test_gate0_real_acceptance.py -q
```

Result: `3 passed`.

Fake eval evidence used:

- Summary: `output/vnext/evals/gate0/phase-vn13-check-2/summary.json`
- Status: `pass`
- Case count: `12`
- Pass rate: `1.0`
- Safety violations: `0`
- Anti-cheat: `pass`

Real smoke command:

```powershell
& "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe" scripts\vnext\run_real_cad_backend_smoke.py --backend existing-autocad --preview-only --rollback-after-check --run-id vn14-real-smoke-check
```

Result: `blocked`.

Real smoke blocker:

- `backend_unavailable:AutoCADAttachError`
- no attachable `AutoCAD.Application`;
- `acadProcessRunning=False`;
- `connect_existing_only=True`;
- no current DWG was saved.

Acceptance command:

```powershell
& '.venv\Scripts\python.exe' scripts\vnext\check_gate0_real_acceptance.py --fake-eval-summary output\vnext\evals\gate0\phase-vn13-check-2\summary.json --anti-cheat-report output\vnext\evals\gate0\phase-vn13-check-2\anti_cheat_report.json --real-smoke-report output\vnext\runs\vn14-real-smoke-check\vn06_real_cad_backend_smoke.json --output output\vnext\evals\gate0\vn14-real-acceptance.json
```

Result: `environment_blocked`.

Acceptance blockers:

- `real_backend_smoke_not_passed`;
- `working_tree_not_clean`.

Gate 0 state:

- `gate0.devStatus`: `environment_blocked`
- `gate0.latestRunId`: `vn14-real-smoke-check`
- `gate0.latestReport`: `output/vnext/runs/vn14-real-smoke-check/vn06_real_cad_backend_smoke.json`

```powershell
& '.venv\Scripts\python.exe' -m pytest tests\vnext -q
```

Result: `156 passed`.

```powershell
& '.venv\Scripts\python.exe' evals\gate0\anti_cheat.py --root .
& '.venv\Scripts\python.exe' scripts\vnext\check_import_boundaries.py
& '.venv\Scripts\python.exe' scripts\vnext\export_schemas.py --check
& '.venv\Scripts\python.exe' scripts\vnext\check_legacy_expansion.py --baseline-ref legacy-baseline-2026-06-22
```

Result: all `pass`; legacy expansion checked `108` added paths.

Doc governance:

```powershell
& '.venv\Scripts\python.exe' scripts\run_doc_governance_audit.py
```

Result: `pass`, `finding_count=0`.

Legacy baseline comparison used the same Python environment as VN-00:

```powershell
& "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe" -m unittest discover -s tests -q
```

Result:

- Ran: `1631`
- Failures: `4`
- Errors: `3`
- Skipped: `2`

The failure/error categories match VN-00 baseline.

VN-14 does not validate Gate 0 Dev, Gate 0 Release, production native plugin readiness, formal layer writes, current DWG save permission, or default vNext entrypoint cutover.
