# Tool Loop Reference

Run the CLI as a sequence of Tool Envelope JSON commands:

```powershell
cad-agent-vnext begin-run --request "..."
cad-agent-vnext inspect --run <run_id> --backend fake
cad-agent-vnext validate-scene --run <run_id>
cad-agent-vnext compile --run <run_id>
cad-agent-vnext execute-preview --run <run_id> --backend fake
cad-agent-vnext verify --run <run_id>
cad-agent-vnext repair --run <run_id>
cad-agent-vnext rollback --run <run_id>
cad-agent-vnext closeout --run <run_id>
```

Each command reads or writes only the current run directory under `output/vnext/runs/<run_id>/`.

Do not run `execute-preview` before `validate-scene` and `compile` have produced `cad_patch.json`.

Do not run `closeout` unless `verification_report.json` has `overall_status: passed`.
