# Stage 3 Lamp Object Plan

## Scope

Add one new desktop object kind, `lamp`, through the cleanroom Stage 3 path:

- object catalog entry
- object generator registration
- compiler coverage through the existing scene pipeline
- verification/eval coverage
- no backend writes beyond `CODEX_PREVIEW`
- no formal layer writes, current DWG save, old orchestrator, training, or workbench restore

## Implementation Steps

1. Add failing tests for `lamp` catalog loading, generator registration, primitive safety, footprint parity, and scene compiler output.
2. Add a `lamp` object catalog entry with bounded default dimensions and a new `lamp_plan_2d_v1` generator key.
3. Implement the `lamp` generator using existing primitive helpers and only `CODEX_PREVIEW` primitives.
4. Add a compiler eval case that includes `lamp` and verifies expected object completeness plus existing safety rules.
5. Extend eval fixture construction only enough to place `lamp` on the desk through the existing relation solver.
6. Run project verification:
   - `python -m pytest`
   - `python tools/check_import_boundaries.py`
   - `python tools/check_cleanroom.py`
   - `python tools/export_schemas.py --output-dir .cad_agent_schemas --check`
   - `python tools/run_compiler_eval.py --backend fake --cases evals/compiler/cases.jsonl`
   - preview-only real AutoCAD smoke if available and needed for final confidence

## Acceptance

- `lamp` is supported by catalog lookup and generator registration.
- Generated primitives preserve semantic id, expected entity type, and `CODEX_PREVIEW` layer.
- Compiler can emit a patch containing `desk`, existing Gate 0 objects, and `lamp`.
- Eval continues to pass, including a new Stage 3 lamp case.
- Cleanroom checks still block old-system modules and old repo roots.
