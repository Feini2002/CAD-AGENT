# Gate 0 Acceptance

Date: 2026-06-28

Status: `passed`

Gate 0 acceptance is proven for the cleanroom desktop scene scope only:

- objects: `desk`, `monitor`, `keyboard`, `mouse`, `vase`
- backend scope: deterministic fake backend plus preview-only real AutoCAD smoke
- CAD write scope: `CODEX_PREVIEW` only
- rollback scope: handles created by the current transaction only

## Evidence

Final evidence root:

```text
.cad_agent_runs/stage2-gate0-acceptance-20260628-final2/
```

Machine-readable decision:

```text
.cad_agent_runs/stage2-gate0-acceptance-20260628-final2/gate0_acceptance_precommit.json
```

Compiler fixture eval:

```text
.cad_agent_runs/stage2-gate0-acceptance-20260628-final2/compiler/compiler/summary.json
.cad_agent_runs/stage2-gate0-acceptance-20260628-final2/compiler/compiler/anti_cheat_report.json
```

Natural-language Gate 0 attempt:

```text
.cad_agent_runs/stage2-gate0-acceptance-20260628-final2/gate0_nl/nl_attempt/gate0_nl_attempt_summary.json
```

Real AutoCAD smoke:

```text
.cad_agent_runs/stage2-gate0-acceptance-20260628-final2/real_smoke/real_cad_backend_smoke.json
```

## Checked

- `python -m pytest`: 161 tests passed.
- `tools/check_import_boundaries.py`: `pass`.
- `tools/export_schemas.py --output-dir .cad_agent_schemas --check`: `pass`.
- `tools/check_cleanroom.py`: `pass`.
- `evals/compiler/anti_cheat.py --root .`: `pass`.
- Compiler fixture eval: `status=pass`, `passRate=1.0`, `safetyViolationCount=0`.
- Natural-language Gate 0 attempt: `status=passed`, `caseCount=10`, `passedCount=10`, `usesSceneSpecFixtures=false`.
- Real AutoCAD smoke: `status=succeeded`, `receiptStatus=succeeded`, `readbackEntityCount=3`, `rollbackStatus=succeeded`.
- Real AutoCAD safety: `previewOnly=true`, `savedCurrentDwg=false`, all readback entities on `CODEX_PREVIEW`, created handles had non-empty bounding boxes.
- Final real smoke handles `8F`, `90`, and `91` were independently checked after rollback and no longer existed.

## Fixes Made During Acceptance

- Reused the legacy AutoCAD COM driver pattern for AutoCAD array variants: `win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, ...)`.
- Changed live AutoCAD deletion to resolve created entities by `doc.HandleToObject(handle)` before deleting, instead of enumerating modelspace.
- Made post-delete rollback readback best-effort so AutoCAD enumeration instability after deletion cannot interrupt a successful created-handle rollback.
- Added a natural-language Gate 0 attempt runner that starts from raw prompts and does not consume compiler `sceneSpecFixture` data.

## Does Not Prove

- Gate 0 Release readiness.
- Production native plugin readiness.
- Formal layer write permission.
- Current DWG save permission.
- General natural-language CAD planning outside the Gate 0 desktop scene.
- Restoration of old orchestrator, training, workbench, or evidence warehouse.
