# Worker Orchestrator Protocol

This Worker is a pre-deployment task dispatch layer for CAD Agent orchestration. It is not a CAD executor, not a local command runner, and not deployment-approved by this document.

The Cloudflare Worker is the HTTP entry. The Durable Object coordinates per-workspace run state. The local bridge is the only later layer that may call local Codex, CAD-MCP, AutoCAD, or filesystem/CAD workflows, and only under separate local rules.

## Worker Non-Execution Boundary

The Worker may only create, lease, monitor, and record task envelopes.

The Worker must never:

- execute `cmd`, `powershell`, shell commands, Codex CLI, CAD-MCP, AutoCAD, or arbitrary local tools.
- read or write local files.
- save the current DWG.
- accept a result that claims `savedCurrentDwg=true`.
- treat bridge `capabilities`, client `allowedTools`, or client `requestedActions` as authorization.
- expose bearer tokens, secret values, full prompts, full CAD data, full repository paths, or machine-local paths in diagnostics/logs.

All Worker-side contracts must keep:

- `savedCurrentDwg=false`
- `constraints.workerExecutesShell=false`
- `constraints.workerSavesCurrentDwg=false`

## Route Contract

| Route | Auth | Contract |
| --- | --- | --- |
| `GET /health` | anonymous | Non-sensitive status only. No secrets, paths, CAD data, prompts, or bridge internals. |
| `POST /runs` | user/admin | Create a run envelope only. Reject forbidden tools/actions and dangerous CAD/local execution requests. |
| `GET /runs` | user/admin | List bounded run summaries only. |
| `GET /runs/:id` | user/admin | Return bounded run detail with recent redacted audit summary. |
| `POST /bridges/register` | bridge | Explicit bridge registration. Heartbeat must not implicitly create unknown bridges. |
| `GET /bridges` | admin | List bridge summaries only. |
| `GET /bridges/:id` | admin | Return bridge detail without secrets. |
| `POST /bridges/:id/offline` | bridge/admin | Mark bridge lifecycle only. Active leases move to retry/blocked policy; no success result is created. |
| `POST /runs/:id/lease` | bridge | Lease only to registered, online, workspace-matched, capability-matched bridge identity. |
| `POST /bridges/:id/heartbeat` | bridge | Canonical heartbeat endpoint with lease identity and monotonic sequence validation. |
| `POST /heartbeat` | bridge | Temporary MVP compatibility alias only; final protocol must prefer `POST /bridges/:id/heartbeat`. |
| `POST /submit` | bridge | Submit result bound to current lease identity, heartbeat token, attempt, result hash, and idempotency key. |
| `GET /bridge-protocol` | optional/admin | Optional protocol/schema/error declaration. Admin-only unless explicitly downgraded to static public schema. |
| `GET /diagnostics` | admin | Aggregated redacted runtime diagnostics only. |

CORS is closed by default. If browser access is added later, exact allowed origins must be configured explicitly.

## AuthContext And Roles

Authentication must resolve an `AuthContext` before route handlers trust any request-body claims:

```ts
type AuthContext = {
  role: "user" | "bridge" | "admin";
  subjectId: string;
  tokenId: string;
  allowedTenantIds: string[];
  allowedWorkspaceIds: string[];
  allowedBridgeIds: string[];
};
```

Rules:

- `workspaceId`, `tenantId`, `bridgeId`, `machineId`, and `bridgeInstanceId` from request bodies are claims only.
- Claims become valid only after matching `AuthContext`.
- A bridge token must not impersonate arbitrary `bridgeId` values.
- Bridge routes must reject `bridge_identity_mismatch` when `AuthContext.allowedBridgeIds` does not match the requested bridge identity.
- User/admin routes must reject workspace/tenant mismatch.
- Use constant-time token comparison where token comparison is implemented.

Role expectations:

- `anonymous`: `GET /health` only.
- `user`: create/read run envelopes for allowed workspaces.
- `bridge`: register, heartbeat, lease, offline, and submit only for allowed bridge/workspace identities.
- `admin`: diagnostics and bridge inspection, plus user-level run inspection.

## Bridge Lifecycle

Bridge lifecycle is explicit:

1. `POST /bridges/register`
2. `POST /runs/:id/lease`
3. `POST /bridges/:id/heartbeat`
4. `POST /submit`
5. `POST /bridges/:id/offline`

Bridge registration fields include:

- `schemaVersion`
- `bridgeId`
- `machineId`
- `bridgeInstanceId`
- `workspaceId`
- `version`
- `protocolVersion`
- `capabilities`
- `state: "online" | "offline" | "draining"`
- `registeredAt`
- `lastSeenAt`
- `offlineAt`
- `offlineReason`
- `authSubject`
- `tokenId`
- `revokedAt`
- `revokedReason`

Each capability must be structured, not a bare string:

- `capabilityId`
- `version`
- `supportedStages`
- `allowedTools`
- `forbiddenActions`
- `maxConcurrentLeases`
- `savedCurrentDwg: false`

Revoked bridges cannot register, heartbeat, lease, or submit. Offline only changes lifecycle; it does not complete active tasks.

## Lease, Heartbeat, Submit

### Lease

`POST /runs/:id/lease` returns `200 no_task` when no work is available. A valid lease response includes:

- `leaseId`
- `leaseSequence`
- `runId`
- `taskId`
- `attempt`
- `bridgeId`
- `machineId`
- `bridgeInstanceId`
- `issuedAt`
- `leaseExpiresAt`
- `heartbeatIntervalSeconds`
- `heartbeatToken`
- `requiredCapabilities`
- `matchedCapabilities`
- `constraints.savedCurrentDwg: false`
- `constraints.workerExecutesShell: false`
- `constraints.workerSavesCurrentDwg: false`
- `constraints.forbiddenActions`

The lease is valid only for a registered, online, workspace-matched, capability-matched bridge. Expired leases cannot submit.

### Heartbeat

`POST /bridges/:id/heartbeat` validates:

- token role
- `bridgeId`
- `machineId`
- `bridgeInstanceId`
- `workspaceId`
- `runId`
- `taskId`
- `leaseId`
- `heartbeatToken`
- monotonic `heartbeatSeq`

Duplicate heartbeat may be idempotent. Out-of-order heartbeat returns `heartbeat_out_of_order`.

### Submit

`POST /submit` validates:

- same lease identity
- task state is `leased` or `running`
- lease is not expired
- matching `heartbeatToken`
- matching `attempt`
- valid `idempotencyKey`
- matching `resultHash`
- valid result schema
- `savedCurrentDwg` is absent or false

Duplicate submit may return the original response only when idempotency binding and body/result hash match.

## Replay And Idempotency

All mutation routes must include `requestId` or `idempotencyKey`.

Idempotency storage binds:

- `route`
- `method`
- `authSubject`
- `workspaceId`
- `runId`
- `taskId`
- `leaseId`
- `attempt`
- `idempotencyKey`
- canonical `bodyHash`

Behavior:

- same key + same hash returns the original response.
- same key + different hash returns `idempotency_conflict`.
- heartbeat enforces monotonic `heartbeatSeq`.
- submit enforces `leaseId`, `heartbeatToken`, `attempt`, `resultHash`, and non-expired lease identity.
- security violations are not retried.

## Error Codes

| HTTP | Code |
| --- | --- |
| `400` | `invalid_json` |
| `400` | `missing_required_field` |
| `401` | `auth_missing` |
| `401` | `auth_invalid` |
| `403` | `auth_role_forbidden` |
| `403` | `bridge_identity_mismatch` |
| `404` | `run_not_found` |
| `404` | `task_not_found` |
| `404` | `bridge_not_found` |
| `409` | `bridge_unregistered` |
| `409` | `bridge_offline` |
| `409` | `bridge_revoked` |
| `409` | `capability_mismatch` |
| `409` | `lease_mismatch` |
| `409` | `task_not_leaseable` |
| `409` | `idempotency_conflict` |
| `409` | `heartbeat_out_of_order` |
| `410` | `lease_expired` |
| `413` | `payload_too_large` |
| `422` | `forbidden_tool_requested` |
| `422` | `forbidden_action_requested` |
| `422` | `saved_current_dwg_violation` |
| `422` | `replay_violation` |
| `429` | `backpressure_active` |
| `200` | `no_task` |

## Local Verification Sequence

This sequence is local verification only. It does not authorize remote deploy or remote secret mutation.

Current baseline commands:

```powershell
npm.cmd run worker:types
npm.cmd run worker:dry-run
npm.cmd run worker:check
npm.cmd run worker:dev
npm.cmd run worker:smoke
```

The npm Wrangler wrapper sets local-only test tokens and directs Wrangler logs into `.wrangler-config/` before the CLI starts. It only allows explicit local `dev --local`, `types`, and `deploy --dry-run`; direct deploy, remote dev, and `secret put` are blocked at the wrapper layer.

`npm.cmd run worker:check` runs the checks that do not require a separately running dev server: boundary check, runtime tests, TypeScript `--noEmit`, local secret scan, Wrangler type generation, and Wrangler dry-run. Run `npm.cmd run worker:dev` and `npm.cmd run worker:smoke` as the public API smoke pair.

Hardening gates:

```powershell
npm.cmd run worker:boundary-check
npm.cmd run worker:test
npm.cmd run worker:typecheck
npm.cmd run worker:secret-scan
npm.cmd run worker:smoke
npm.cmd run worker:types
npm.cmd run worker:dry-run
```

Before claiming the local gate complete, verify negative cases for auth failure, workspace/bridge mismatch, bridge identity mismatch, replay/idempotency conflict, lease mismatch, wrong submit `heartbeatToken`, duplicate submit, stale/revoked bridge, timeout/retry/DLQ, backpressure, diagnostics redaction, and closed-by-default CORS.

## `.dev.vars.example` Workflow

`workers/orchestrator/.dev.vars.example` documents local variable names only. It must contain placeholders, not real secrets.

Expected names:

```dotenv
WORKER_API_TOKEN=replace-with-local-worker-token
BRIDGE_API_TOKEN=replace-with-local-bridge-token
ADMIN_API_TOKEN=replace-with-local-admin-token
DEFAULT_WORKSPACE_ID=cad-agent-core-lab
DEFAULT_BRIDGE_ID=bridge_local_smoke
ALLOWED_WORKSPACE_IDS=cad-agent-core-lab
ALLOWED_BRIDGE_IDS=bridge_local_smoke,bridge_revoke_smoke,bridge_unregistered_smoke
ALLOWED_ORIGINS=
ORCHESTRATOR_VERSION=local-dev
ORCHESTRATOR_DISABLED=false
RUN_CREATE_DISABLED=false
BRIDGE_LEASING_DISABLED=false
SUBMIT_DISABLED=false
```

Workflow:

1. Copy `.dev.vars.example` to `.dev.vars` locally.
2. Put real local-only token values in `.dev.vars` or process env.
3. Confirm `.dev.vars` is ignored by git.
4. Never commit real token values.
5. Do not run `wrangler secret put` until the deployment checklist reaches an explicit user-approved remote secret step.

Secret names may be declared in config or documentation. Secret values must stay outside git.
