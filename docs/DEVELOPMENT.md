# Development

Install editable package dependencies in a local environment, then run:

```powershell
python -m pytest
python tools/check_import_boundaries.py
python tools/export_schemas.py --output-dir .cad_agent_schemas --check
python tools/run_compiler_eval.py --backend fake --cases evals/compiler/cases.jsonl
python tools/check_cleanroom.py
```

Generated local outputs should stay out of source control:

- `.cad_agent_runs/`
- `.cad_agent_schemas/`
- `.pytest_cache/`
- `cad_mcp.log`

Before claiming CAD success, include the receipt path, readback evidence, rollback status, `savedCurrentDwg=false`, and any not-checked boundary.
