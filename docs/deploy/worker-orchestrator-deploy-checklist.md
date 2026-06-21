# Worker Orchestrator Deploy Checklist

Status: `INITIAL_REMOTE_DEPLOYED_NO_CAD`

This checklist remains a stop gate for production and real CAD / bridge integration. Initial Cloudflare deployment has been explicitly authorized and completed; production, real bridge runner, and CAD-MCP remain blocked until separately approved.

## Initial Remote Deployment Record

- Worker name: `cadagent` (`CADAgent` was requested, but Wrangler requires lowercase alphanumeric names with dashes only).
- URL: `https://cadagent.cmw1196466375.workers.dev`
- Account: `Cmw1196466375@gmail.com's Account`
- Current deployed version: `21fc6755-27d0-4e97-b13a-ef1e660c8401`
- Deployment method: `wrangler deploy --strict --secrets-file <temporary-json>`.
- Secret handling: generated `WORKER_API_TOKEN`, `BRIDGE_API_TOKEN`, and `ADMIN_API_TOKEN` locally for deployment and remote smoke; values were not committed or persisted in the repository.
- Remote smoke: pass, latest `runId=run_20260606151438_worker_orchestration_ready_f6260886`, `state=completed`.
- Boundary: no real CAD, no CAD-MCP, no local bridge runner, no `gpt-5.5` runner, no current DWG save.
- Note: the first immediate post-deploy smoke hit transient Cloudflare `1042`; redeploy plus a 30 second propagation wait passed remote smoke.

## Quick Bridge + CAD Preview Smoke

- Date: 2026-06-06.
- Remote Worker: redeployed `cadagent` with temporary secrets, version `21fc6755-27d0-4e97-b13a-ef1e660c8401`.
- Remote smoke mode: `WORKER_SMOKE_SKIP_REVOKE=true` for repeatable remote smoke; local runtime tests still cover revoked bridge behavior.
- Remote smoke result: pass, `runId=run_20260606151438_worker_orchestration_ready_f6260886`, `state=completed`.
- CAD preview command: `scripts/run_model_agent_live_collab_proof.py --fixture-model --driver-mode autocad_existing`.
- CAD preview result: `cadGeometryVerified=true`, `createdHandleCount=7`, `readbackEntityCount=7`, `targetLayer=CODEX_PREVIEW`, `savedCurrentDwg=false`.
- CAD run package: `output/runs/model-agent-live-collab-proof-20260606-151512/`.
- Screenshot: `output/previews/worker-bridge-cad-preview-20260606-151512.png`, task-scoped to the 7 created handles.
- Boundary: this is a quick smoke, not formal training and not a real `gpt-5.5` provider proof. Visual review did not become a formal closeout because the table-C visual review script expected an older `evidence_state` field in the readback report.

## Hard Stop

- [x] Stop before any real Cloudflare deployment unless explicitly approved.
- [x] Do not run `wrangler deploy` for staging or production without explicit user approval.
- [x] Do not run `wrangler secret put` without explicit user approval.
- [x] Do not write, paste, or commit real secret values.
- [x] Do not modify production CAD / bridge resources from Worker deployment work.
- [ ] Do not claim deployment readiness from `wrangler deploy --dry-run`; dry-run validates packaging/config shape only.

## Worker Boundary

- [ ] No Worker endpoint can execute local commands.
- [ ] No Worker endpoint can call `cmd`, `powershell`, shell, Codex CLI, CAD-MCP, AutoCAD, or arbitrary local tools.
- [ ] No Worker endpoint can read/write local files.
- [ ] No Worker endpoint can save the current DWG.
- [ ] All Worker-side task/result contracts keep `savedCurrentDwg=false`.
- [ ] Result payloads with `savedCurrentDwg=true` return `saved_current_dwg_violation`.
- [ ] Dangerous actions are blocked, audited, and not retried.
- [ ] `worker:boundary-check` fails on shell execution, local command execution, arbitrary user-supplied outbound fetch, CAD-MCP execution, AutoCAD execution, or DWG save capability in Worker source.

## Local Verification Gate

- [x] `npm.cmd run worker:boundary-check`
- [x] `npm.cmd run worker:test`
- [x] `npm.cmd run worker:typecheck`
- [x] `npm.cmd run worker:secret-scan`
- [x] `npm.cmd run worker:smoke`
- [x] `npm.cmd run worker:types`
- [x] `npm.cmd run worker:dry-run`
- [ ] Auth failure cases pass.
- [ ] Auth subject to workspace/bridge mismatch cases pass.
- [ ] Bridge identity mismatch cases pass.
- [ ] Replay/idempotency conflict cases pass.
- [ ] Lease mismatch cases pass.
- [ ] Duplicate submit and wrong submit `heartbeatToken` cases pass.
- [ ] Timeout / retry / DLQ behavior tests pass.
- [ ] Duplicate alarm idempotency test passes.
- [ ] Backpressure threshold test passes.
- [ ] Diagnostics/run detail/audit redaction tests pass.
- [ ] CORS closed-by-default test passes.
- [ ] No committed secrets are detected.

## Staging And Production Separation

- [ ] `env.staging` and `env.production` are defined separately before real deployment.
- [ ] Staging and production use distinct Worker names.
- [ ] Staging and production use distinct Durable Object namespaces/classes/migration plans as applicable.
- [ ] Staging and production use distinct secret values.
- [ ] Staging and production use distinct bridge tokens.
- [ ] Staging and production use distinct observability labels.
- [ ] Staging never shares production Durable Object state.
- [ ] Deployment sequence is staging first, remote smoke, diagnostics verification, then stop for explicit production approval.

## Remote Staging Gate

- [x] User explicitly approves initial remote deploy before any deploy command.
- [x] Remote smoke covers register -> create -> lease -> heartbeat -> submit -> duplicate submit.
- [ ] Diagnostics expose environment, Worker version, compatibility date, compatibility flags, schema version, migration status, alarm status, backlog counts, circuit breaker states, and recent redacted error summaries.
- [ ] Secret presence is verified without exposing secret values.
- [ ] Internal SQL migration status is verified.
- [ ] Alarm/backpressure behavior is verified.
- [ ] Cloudflare 5xx/storage failure handling is tested or explicitly risk-accepted.
- [ ] Stop again before production.

## Rollback And Recovery

- [ ] Previous Worker version is recorded before deploy.
- [ ] Rollback command/process is documented and tested in staging.
- [ ] Irreversible schema migrations are listed before production.
- [ ] Run read compatibility after rollback is tested.
- [ ] Bridge re-registration after rollback is tested.
- [ ] Rollback smoke covers `/health`, `/diagnostics`, bridge re-register, and old run read.
- [ ] Migration failure behavior refuses writes, preserves rows, exposes redacted diagnostics, and issues no new leases.

## Secret Rotation

- [ ] Rotation process defines new/old token overlap window.
- [ ] Bridge re-registration during rotation is tested.
- [ ] Old token rejection after the overlap window is tested.
- [ ] Rotation smoke covers user/admin/bridge tokens as applicable.
- [ ] No rotated value is committed, logged, or pasted into diagnostics.
- [ ] `wrangler secret put` remains blocked until explicit user approval for the target environment.

## Kill Switches

- [ ] `ORCHESTRATOR_DISABLED` blocks mutation routes according to policy.
- [ ] `RUN_CREATE_DISABLED` prevents new run creation.
- [ ] `BRIDGE_LEASING_DISABLED` prevents new leases.
- [ ] `SUBMIT_DISABLED` prevents new submit acceptance.
- [ ] Kill switch tests prove disabled routes do not create, lease, or accept new submit data.
- [ ] Kill switches do not block `GET /health`.
- [ ] Kill switches do not block admin diagnostics needed for recovery.
- [ ] Kill switches allow bridge offline and existing lease closeout only where policy explicitly allows.

## No-Secrets Gate

- [ ] `.dev.vars.example` contains placeholder values only.
- [ ] Real `.dev.vars` is ignored by git.
- [ ] `wrangler.jsonc` declares secret names only, not values.
- [ ] Logs, diagnostics, audit events, and smoke output are redacted.
- [ ] No bearer token, heartbeat token, secret value, full prompt, full CAD data, full repository path, or machine-local path is exposed.

## Production Approval Stop

Production, real bridge runner, real model runner, Queue / Workflows, and CAD-MCP remain blocked until the user explicitly approves the target layer. Initial `cadagent` deployment only proves remote Worker / Durable Object orchestration smoke.
