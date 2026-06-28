# Gate 0 Eval Harness

This harness runs deterministic fake-backend checks for the desktop computer-desk slice.
It includes Gate 0 fixture cases and staged object-expansion cases such as the Stage 3 `lamp` case.

It does not call a model and does not write real CAD. Test cases include prompts for evaluation metadata, while `sceneSpecFixture` provides deterministic SceneSpec inputs for repeatable CI runs.

Outputs are written under `.cad_agent_runs/evals/compiler/<eval_run_id>/`:

- `summary.json`
- `case_results.jsonl`
- `failures.jsonl`
- `safety_report.json`
- `anti_cheat_report.json`
- `report.md`

Run:

```powershell
python tools/run_compiler_eval.py --backend fake --cases evals/compiler/cases.jsonl
python evals/compiler/anti_cheat.py --root .
```

Public natural-language Gate 0 cases live in `evals/gate0/cases.jsonl` and intentionally do not include `sceneSpecFixture`.
