# Roadmap

## Stage 1: Cleanroom Cut

- Keep only the minimal active package, tests, evals, tools, skill, and docs.
- Verify old content is recoverable from archive source.
- Block old-system imports and old repository roots.

## Stage 2: Gate 0 Acceptance

- Run compiler fixture eval.
- Run anti-cheat checks.
- Run preview-only real AutoCAD smoke where AutoCAD is available.
- Add a separate natural-language Gate 0 attempt summary before declaring acceptance.

## Stage 3: Broaden Carefully

- Add object kinds only through catalog, generator, compiler, verification, and eval updates together.
- Keep formal layer writes and DWG save blocked until a later explicit gate.
- Do not restore training or old workbench as part of normal development.

Progress:

- `lamp` has been added as the first Stage 3 object kind through catalog, generator, compiler tests, and compiler fixture eval.

Next candidates should repeat the same path, one object kind at a time.
