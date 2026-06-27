# Gate 0 Checklist

- Use `CODEX_PREVIEW` only.
- Do not save the current DWG.
- Confirm `savedCurrentDwg=false` from receipt and closeout.
- Check created handles and semantic IDs.
- Check deterministic verifier output before any success claim.
- Treat deterministic verify fail as a blocker.
- Run local repair only for failed semantic IDs.
- Stop after two repair rounds.
- Do not modify nearby non-target handles.
- Do not rely on screenshots for pass/fail.
