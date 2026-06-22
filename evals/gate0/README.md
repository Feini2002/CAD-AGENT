# Gate 0 Eval Harness

This harness runs deterministic fake-backend checks for the desktop computer-desk slice.

It does not call a model and does not write real CAD. Test cases include prompts for evaluation metadata, while `sceneSpecFixture` provides deterministic SceneSpec inputs for repeatable CI runs.

Outputs are written under `output/vnext/evals/gate0/<eval_run_id>/`:

- `summary.json`
- `case_results.jsonl`
- `failures.jsonl`
- `safety_report.json`
- `anti_cheat_report.json`
- `report.md`

Run:

```powershell
python scripts/vnext/run_gate0_eval.py --backend fake --cases evals/gate0/cases.jsonl
python evals/gate0/anti_cheat.py --root .
```
