# CAD Agent

Cleanroom CAD scene authoring core for generating and verifying preview-only AutoCAD geometry.

This repository is the new mainline after the 2026-06-27 cleanroom cut. The previous repository content is recoverable from:

- tag: `legacy-pre-cleanroom-20260627`
- archive branch: `archive/legacy-pre-cleanroom-20260627`

## Current Scope

Gate 0 remains intentionally small: a natural-language desktop scene with `desk`, `monitor`, `keyboard`, `mouse`, and `vase`, compiled into deterministic `SceneSpec` / `CadPatch` artifacts and executed only on `CODEX_PREVIEW`.

The current mainline has begun Stage 3 broadening with one additional desktop object kind, `lamp`. New object kinds must enter through the object catalog, generator, compiler, verification/eval coverage, and the same preview-only safety boundary.

The repository does not contain the old orchestrator, training workbench, project evidence warehouse, capability map, or protected evidence tree. Those remain in the archive source above.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `src/cad_agent/` | Python package: domain contracts, planning, policies, adapters, verification, CLI |
| `src/cad_agent/resources/object_catalog.json` | Cleanroom object catalog for Gate 0 plus staged additions |
| `tests/` | Unit and contract tests for the cleanroom package |
| `evals/compiler/` | Deterministic compiler fixture evals for CI |
| `evals/gate0/` | Public natural-language Gate 0 acceptance cases without SceneSpec fixtures |
| `tools/` | Boundary, schema, eval, real-CAD smoke, and acceptance scripts |
| `.agents/skills/cad-scene-authoring/` | Codex skill for safe scene authoring loops |
| `docs/ARCHITECTURE.md` | Cleanroom package architecture |
| `docs/SAFETY.md` | CAD write and verification safety contract |
| `docs/STATUS.md` | Current acceptance boundary |
| `docs/ROADMAP.md` | Next staged work |
| `docs/DEVELOPMENT.md` | Local verification notes |

## Safety Contract

- CAD writes are preview-only.
- Target layer must be `CODEX_PREVIEW`.
- `savedCurrentDwg=false` is required.
- Created handles must be read back before success is claimed.
- Rollback deletes only handles created by the current transaction.
- Screenshots are visual aids, not deterministic proof.
- Production native plugin, formal layer writes, current DWG save, and training workflows are not in scope.

## Quick Checks

```powershell
python -m pytest
python tools/check_import_boundaries.py
python tools/export_schemas.py --output-dir .cad_agent_schemas --check
python tools/run_compiler_eval.py --backend fake --cases evals/compiler/cases.jsonl
python tools/check_cleanroom.py
```

Real AutoCAD smoke is optional and environment-gated:

```powershell
python tools/run_real_cad_backend_smoke.py --preview-only --rollback-after-check
```

See `docs/STATUS.md` for the current acceptance boundary and `docs/ROADMAP.md` for staged work.
