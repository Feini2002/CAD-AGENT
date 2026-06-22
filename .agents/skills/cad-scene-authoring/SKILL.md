---
name: cad-scene-authoring
description: Use when the user asks Codex to create, arrange, modify, inspect, or verify CAD scene content in the CAD-AGENT repository. Requires SceneSpec planning, CODEX_PREVIEW-only execution, created-handle readback, verification, and local repair. Do not use for repository architecture work or status reporting.
---

# CAD Scene Authoring

Use this skill for CAD scene authoring requests, not repository migration or status reporting.

Read only the references needed for the current task:

- `references/scene-spec.md`
- `references/tool-loop.md`
- `references/gate0-checklist.md`

## Required Loop

1. Run `cad-agent-vnext begin-run --request "..."`.
2. Run `cad-agent-vnext inspect --run <run_id> --backend fake|autocad-existing`.
3. Create `scene_spec.json` from the user request, `drawing_snapshot.json`, object catalog, and SceneSpec schema.
4. Run `cad-agent-vnext validate-scene --run <run_id>`.
5. Run `cad-agent-vnext compile --run <run_id>`.
6. Inspect `impact_summary.json`.
7. Run `cad-agent-vnext execute-preview --run <run_id> --backend fake|autocad-existing`.
8. Run `cad-agent-vnext verify --run <run_id>`.
9. If the verification report is repairable, run `cad-agent-vnext repair --run <run_id>`, then execute and verify again. Stop after two repair rounds.
10. Capture screenshots only as visual aids.
11. Run `cad-agent-vnext closeout --run <run_id>` only after deterministic verification passes.
12. Report objects, evidence refs, blockers, and `savedCurrentDwg=false`.

## Safety Rules

- Do not call old drawing scripts.
- Do not execute arbitrary AutoLISP.
- Do not skip inspect.
- Do not guess that drawing succeeded without receipt/readback.
- Do not write formal layers.
- Do not save the current DWG.
- Do not claim success after deterministic verify fail.
- Do not add exact phrase routes.
- Keep all execution on `CODEX_PREVIEW`.
- Treat screenshots as visual aids, never as deterministic proof.
