# Status

Date: 2026-06-27

Current branch: `codex/cleanroom-final-cut`

Archive source for deleted old content:

- tag: `legacy-pre-cleanroom-20260627`
- branch: `archive/legacy-pre-cleanroom-20260627`

Current main repository keeps:

- `src/cad_agent`
- `tests`
- `evals/compiler`
- `evals/gate0`
- `tools`
- `.agents/skills/cad-scene-authoring`
- `docs`
- root project files

Acceptance boundary:

- Compiler fixture eval can be run locally and in CI.
- Natural-language Gate 0 cases are present but are not yet a model-backed release proof.
- Real AutoCAD smoke is environment-gated and must be run separately.
- Production native plugin, formal layer writes, training, and old evidence warehouse restoration are out of scope.
