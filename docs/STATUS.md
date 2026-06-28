# Status

Date: 2026-06-28

Current branch: `main`

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

- Stage 2 Gate 0 acceptance passed for the cleanroom desktop scene scope.
- Stage 3 has one completed staged object addition: `lamp`, covered through catalog, generator, compiler tests, and compiler fixture eval.
- Compiler fixture eval passes locally with fake backend.
- Natural-language Gate 0 attempt passes from raw prompts without SceneSpec fixtures.
- Real AutoCAD smoke passed with preview-only writes, created-handle readback, rollback, and `savedCurrentDwg=false`.
- Production native plugin, formal layer writes, training, and old evidence warehouse restoration are out of scope.

See `docs/GATE0_ACCEPTANCE.md` for evidence paths, checks, and not-proven boundaries.

Current catalog object kinds:

- Gate 0: `desk`, `monitor`, `keyboard`, `mouse`, `vase`
- Stage 3 fixture coverage: `lamp`
