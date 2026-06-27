# Tool Loop Reference

Run the CLI as a sequence of Tool Envelope JSON commands:

```powershell
cad-agent begin-run --request "..."
cad-agent inspect --run <run_id> --backend fake
cad-agent validate-scene --run <run_id>
cad-agent compile --run <run_id>
cad-agent execute-preview --run <run_id> --backend fake
cad-agent verify --run <run_id>
cad-agent repair --run <run_id>
cad-agent rollback --run <run_id>
cad-agent closeout --run <run_id>
```

Each command reads or writes only the current run directory under `.cad_agent_runs/<run_id>/`.

Do not run `execute-preview` before `validate-scene` and `compile` have produced `cad_patch.json`.

Do not run `closeout` unless `verification_report.json` has `overall_status: passed`.
