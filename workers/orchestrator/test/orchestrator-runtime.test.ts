/// <reference path="../src/worker-configuration.d.ts" />
/// <reference types="@cloudflare/vitest-pool-workers/types" />

import { env } from "cloudflare:workers";
import { reset, runDurableObjectAlarm, SELF } from "cloudflare:test";
import { beforeEach, describe, expect, it } from "vitest";

const BASE = "https://orchestrator.runtime.test";
const WORKSPACE_ID = "cad-agent-core-lab";
const USER_TOKEN = "local-worker-token";
const BRIDGE_TOKEN = "local-bridge-token";
const ADMIN_TOKEN = "local-admin-token";

type Role = "user" | "bridge" | "admin";
type JsonRecord = Record<string, unknown>;

beforeEach(async () => {
  await reset();
});

describe("worker orchestrator runtime contract", () => {
  it("keeps health public, CORS closed by default, and mutation routes authenticated", async () => {
    const health = await api("/health", { method: "GET", origin: "https://example.invalid" });
    expect(health.status).toBe(200);
    expect(health.headers.get("Access-Control-Allow-Origin")).toBeNull();
    await expectJson(health, { status: "ok", schemaVersion: "worker_run_state/v2" });

    const missingAuth = await api("/runs", { method: "POST", body: createRunBody("auth_missing") });
    expect(missingAuth.status).toBe(401);
    await expectError(missingAuth, "auth_missing");

    const wrongRole = await api("/submit", { method: "POST", role: "user", body: submitBody("run_missing", "task_missing", "lease_missing") });
    expect(wrongRole.status).toBe(403);
    await expectError(wrongRole, "auth_role_forbidden");
  });

  it("blocks forbidden worker-side tools before a run is persisted", async () => {
    const response = await api("/runs", {
      method: "POST",
      role: "user",
      body: createRunBody("forbidden_tool", {
        taskSpecs: [
          {
            taskId: "task_forbidden",
            agentId: "agent_forbidden",
            allowedTools: ["powershell"],
          },
        ],
      }),
    });
    expect(response.status).toBe(422);
    await expectError(response, "forbidden_tool_requested");
  });

  it("rejects invalid task graphs before persistence", async () => {
    const duplicate = await api("/runs", {
      method: "POST",
      role: "user",
      body: createRunBody("duplicate_task", {
        taskSpecs: [
          { taskId: "task_duplicate", agentId: "agent_a", allowedTools: ["codex_cli_model_review"] },
          { taskId: "task_duplicate", agentId: "agent_b", allowedTools: ["codex_cli_model_review"] },
        ],
      }),
    });
    expect(duplicate.status).toBe(422);
    await expectError(duplicate, "duplicate_task_id");

    const missing = await api("/runs", {
      method: "POST",
      role: "user",
      body: createRunBody("missing_dependency", {
        taskSpecs: [{ taskId: "task_a", agentId: "agent_a", dependsOn: ["task_missing"], allowedTools: ["codex_cli_model_review"] }],
      }),
    });
    expect(missing.status).toBe(422);
    await expectError(missing, "invalid_task_dependency");

    const cycle = await api("/runs", {
      method: "POST",
      role: "user",
      body: createRunBody("dependency_cycle", {
        taskSpecs: [
          { taskId: "task_a", agentId: "agent_a", dependsOn: ["task_b"], allowedTools: ["codex_cli_model_review"] },
          { taskId: "task_b", agentId: "agent_b", dependsOn: ["task_a"], allowedTools: ["codex_cli_model_review"] },
        ],
      }),
    });
    expect(cycle.status).toBe(422);
    await expectError(cycle, "task_dependency_cycle");
  });

  it("registers a bridge, leases work, accepts heartbeat, and enforces submit replay keys", async () => {
    const bridgeId = "bridge_runtime";
    const bridge = bridgeBody(bridgeId, "register_main");
    const registered = await api("/bridges/register", { method: "POST", role: "bridge", body: bridge });
    expect(registered.status).toBe(201);
    await expectJson(registered, { status: "registered" });

    const created = await api("/runs", { method: "POST", role: "user", body: createRunBody("lease_submit") });
    expect(created.status).toBe(201);
    const run = await created.json<JsonRecord>();
    const runId = String(run.runId);
    const task = (run.tasks as JsonRecord[])[0];
    expect(task.state).toBe("pending");

    const listed = await api(`/runs?workspaceId=${WORKSPACE_ID}`, { method: "GET", role: "user" });
    expect(listed.status).toBe(200);
    const listPayload = await listed.json<JsonRecord>();
    expect((listPayload.runs as JsonRecord[]).some((item) => item.runId === runId)).toBe(true);

    const leased = await api(`/runs/${runId}/lease`, {
      method: "POST",
      role: "bridge",
      body: leaseBody(runId, bridgeId, "lease_main"),
    });
    expect(leased.status).toBe(200);
    const lease = await leased.json<JsonRecord>();
    expect(lease.status).toBe("leased");
    expect((lease.envelope as JsonRecord).constraints).toMatchObject({
      savedCurrentDwg: false,
      workerExecutesShell: false,
      workerSavesCurrentDwg: false,
    });

    const heartbeat = await api(`/bridges/${bridgeId}/heartbeat`, {
      method: "POST",
      role: "bridge",
      body: heartbeatBody(lease, 1, "heartbeat_main"),
    });
    expect(heartbeat.status).toBe(200);
    await expectJson(heartbeat, { status: "accepted", taskState: "running", heartbeatSeq: 1 });

    const result = agentResult(lease, "runtime submit accepted");
    const resultHash = await sha256Hex(stableJson(result));
    const submitPayload = submitBodyFromLease(lease, result, resultHash, "submit_once");
    const wrongSubmitToken = await api("/submit", {
      method: "POST",
      role: "bridge",
      body: { ...submitPayload, heartbeatToken: "not-the-issued-token", idempotencyKey: unique("wrong_submit_token") },
    });
    expect(wrongSubmitToken.status).toBe(409);
    await expectError(wrongSubmitToken, "lease_mismatch");

    const submitted = await api("/submit", { method: "POST", role: "bridge", body: submitPayload });
    expect(submitted.status).toBe(200);
    await expectJson(submitted, { status: "accepted" });

    const duplicate = await api("/submit", { method: "POST", role: "bridge", body: submitPayload });
    expect(duplicate.status).toBe(200);
    await expectJson(duplicate, { status: "accepted" });

    const finalRun = await api(`/runs/${runId}?workspaceId=${WORKSPACE_ID}`, { method: "GET", role: "user" });
    expect(finalRun.status).toBe(200);
    await expectJson(finalRun, {
      state: "completed",
      savedCurrentDwg: false,
      cadGeometryVerified: false,
    });
  });

  it("blocks idempotent bridge mutation replay after revocation", async () => {
    const { bridgeId, runId, leaseRequest } = await leaseFreshRun("bridge_replay_revoked", "replay_revoked");

    const revoked = await api(`/bridges/${bridgeId}/offline`, {
      method: "POST",
      role: "bridge",
      body: { workspaceId: WORKSPACE_ID, revoke: true, reason: "runtime_revocation", requestId: unique("revoke_replay") },
    });
    expect(revoked.status).toBe(200);

    const replay = await api(`/runs/${runId}/lease`, { method: "POST", role: "bridge", body: leaseRequest });
    expect(replay.status).toBe(409);
    await expectError(replay, "bridge_revoked");

    const resultReplay = await leaseFreshRun("bridge_replay_result_revoked", "replay_result_revoked");
    const heartbeatPayload = heartbeatBody(resultReplay.lease, 1, "replay_heartbeat");
    const heartbeat = await api(`/bridges/${resultReplay.bridgeId}/heartbeat`, { method: "POST", role: "bridge", body: heartbeatPayload });
    expect(heartbeat.status).toBe(200);

    const result = agentResult(resultReplay.lease, "revoked submit replay");
    const resultHash = await sha256Hex(stableJson(result));
    const submitPayload = submitBodyFromLease(resultReplay.lease, result, resultHash, "replay_submit");
    const submitted = await api("/submit", { method: "POST", role: "bridge", body: submitPayload });
    expect(submitted.status).toBe(200);

    const resultRevoked = await api(`/bridges/${resultReplay.bridgeId}/offline`, {
      method: "POST",
      role: "bridge",
      body: { workspaceId: WORKSPACE_ID, revoke: true, reason: "runtime_result_revocation", requestId: unique("revoke_result_replay") },
    });
    expect(resultRevoked.status).toBe(200);

    const heartbeatReplay = await api(`/bridges/${resultReplay.bridgeId}/heartbeat`, { method: "POST", role: "bridge", body: heartbeatPayload });
    expect(heartbeatReplay.status).toBe(409);
    await expectError(heartbeatReplay, "bridge_revoked");

    const submitReplay = await api("/submit", { method: "POST", role: "bridge", body: submitPayload });
    expect(submitReplay.status).toBe(409);
    await expectError(submitReplay, "bridge_revoked");
  });

  it("upgrades legacy v1 run state on read through the Durable Object", async () => {
    const stub = runStateStub("runtime_legacy");
    const legacyRunId = `legacy_${Date.now()}`;
    await (stub as unknown as { __debugInsertLegacyRun(runId: string): Promise<JsonRecord> }).__debugInsertLegacyRun(legacyRunId);

    const upgraded = await (stub as unknown as { getRun(runId: string): Promise<JsonRecord | null> }).getRun(legacyRunId);
    expect(upgraded).toMatchObject({
      runId: legacyRunId,
      schemaVersion: "worker_run_state/v2",
      legacyStateReadCount: 1,
      savedCurrentDwg: false,
    });

    const secondRead = await (stub as unknown as { getRun(runId: string): Promise<JsonRecord | null> }).getRun(legacyRunId);
    expect(secondRead?.legacyStateReadCount).toBe(1);
  });

  it("moves an expired single-attempt lease to DLQ exactly once via alarm", async () => {
    const bridgeId = "bridge_alarm";
    await api("/bridges/register", { method: "POST", role: "bridge", body: bridgeBody(bridgeId, "alarm_register") });
    const created = await api("/runs", {
      method: "POST",
      role: "user",
      body: createRunBody("alarm_dlq", {
        taskSpecs: [
          {
            taskId: "task_alarm",
            agentId: "agent_alarm",
            allowedTools: ["codex_cli_model_review"],
            timeoutSeconds: 1,
            maxAttempts: 1,
          },
        ],
      }),
    });
    const run = await created.json<JsonRecord>();
    const runId = String(run.runId);
    const lease = await api(`/runs/${runId}/lease`, {
      method: "POST",
      role: "bridge",
      body: leaseBody(runId, bridgeId, "alarm_lease"),
    });
    expect(lease.status).toBe(200);

    await sleep(1100);
    const stub = runStateStub(WORKSPACE_ID);
    expect(await runDurableObjectAlarm(stub)).toBe(true);
    await runDurableObjectAlarm(stub);

    const finalRun = await (stub as unknown as { getRun(runId: string): Promise<JsonRecord | null> }).getRun(runId);
    expect(finalRun).toMatchObject({
      state: "blocked",
      timeoutCount: 1,
      dlqCount: 1,
    });
    expect((finalRun?.tasks as JsonRecord[])[0]).toMatchObject({
      state: "blocked",
      blockedReason: "task_timeout",
    });
  });

  it("moves a single-attempt active lease to DLQ when its bridge goes offline", async () => {
    const bridgeId = "bridge_offline_dlq";
    await api("/bridges/register", { method: "POST", role: "bridge", body: bridgeBody(bridgeId, "offline_dlq_register") });
    const created = await api("/runs", {
      method: "POST",
      role: "user",
      body: createRunBody("offline_dlq", {
        taskSpecs: [
          {
            taskId: "task_offline_dlq",
            agentId: "agent_offline_dlq",
            allowedTools: ["codex_cli_model_review"],
            maxAttempts: 1,
          },
        ],
      }),
    });
    const run = await created.json<JsonRecord>();
    const runId = String(run.runId);
    const leased = await api(`/runs/${runId}/lease`, {
      method: "POST",
      role: "bridge",
      body: leaseBody(runId, bridgeId, "offline_dlq_lease"),
    });
    expect(leased.status).toBe(200);

    const offline = await api(`/bridges/${bridgeId}/offline`, {
      method: "POST",
      role: "bridge",
      body: { workspaceId: WORKSPACE_ID, reason: "offline_dlq", requestId: unique("offline_dlq") },
    });
    expect(offline.status).toBe(200);

    const finalRun = await (runStateStub(WORKSPACE_ID) as unknown as { getRun(runId: string): Promise<JsonRecord | null> }).getRun(runId);
    expect(finalRun).toMatchObject({ state: "blocked", dlqCount: 1 });
    expect((finalRun?.tasks as JsonRecord[])[0]).toMatchObject({ state: "blocked", blockedReason: "task_timeout" });
  });

  it("moves a single-attempt active lease to DLQ when its bridge becomes stale", async () => {
    const { runId } = await leaseFreshRun("bridge_stale_dlq", "stale_dlq", {
      taskSpecs: [
        {
          taskId: "task_stale_dlq",
          agentId: "agent_stale_dlq",
          allowedTools: ["codex_cli_model_review"],
          maxAttempts: 1,
        },
      ],
    });
    await forceBridgeStale("bridge_stale_dlq");

    const stub = runStateStub(WORKSPACE_ID);
    await runDurableObjectAlarm(stub);

    const finalRun = await (stub as unknown as { getRun(runId: string): Promise<JsonRecord | null> }).getRun(runId);
    expect(finalRun).toMatchObject({ state: "blocked", dlqCount: 1 });
    expect((finalRun?.tasks as JsonRecord[])[0]).toMatchObject({ state: "blocked", blockedReason: "task_timeout" });
  });

  it("enforces bridge maxConcurrentLeases before issuing another lease", async () => {
    const bridgeId = "bridge_capacity";
    await api("/bridges/register", { method: "POST", role: "bridge", body: bridgeBody(bridgeId, "capacity_register") });
    const created = await api("/runs", {
      method: "POST",
      role: "user",
      body: createRunBody("capacity", {
        taskSpecs: [
          { taskId: "task_capacity_a", agentId: "agent_capacity_a", allowedTools: ["codex_cli_model_review"] },
          { taskId: "task_capacity_b", agentId: "agent_capacity_b", allowedTools: ["codex_cli_model_review"] },
        ],
      }),
    });
    const run = await created.json<JsonRecord>();
    const runId = String(run.runId);
    const firstLease = await api(`/runs/${runId}/lease`, { method: "POST", role: "bridge", body: leaseBody(runId, bridgeId, "capacity_a") });
    expect(firstLease.status).toBe(200);

    const secondLease = await api(`/runs/${runId}/lease`, { method: "POST", role: "bridge", body: leaseBody(runId, bridgeId, "capacity_b") });
    expect(secondLease.status).toBe(200);
    await expectJson(secondLease, { status: "no_capacity" });
  });

  it("moves a retryable expired lease back to pending after retry delay", async () => {
    const bridgeId = "bridge_alarm";
    await api("/bridges/register", { method: "POST", role: "bridge", body: bridgeBody(bridgeId, "retry_register") });
    const created = await api("/runs", {
      method: "POST",
      role: "user",
      body: createRunBody("alarm_retry", {
        taskSpecs: [
          {
            taskId: "task_retry",
            agentId: "agent_retry",
            allowedTools: ["codex_cli_model_review"],
            timeoutSeconds: 1,
            maxAttempts: 2,
          },
        ],
      }),
    });
    const run = await created.json<JsonRecord>();
    const runId = String(run.runId);
    await api(`/runs/${runId}/lease`, {
      method: "POST",
      role: "bridge",
      body: leaseBody(runId, bridgeId, "retry_lease"),
    });

    await sleep(1100);
    const stub = runStateStub(WORKSPACE_ID);
    expect(await runDurableObjectAlarm(stub)).toBe(true);
    const retryScheduled = await (stub as unknown as { getRun(runId: string): Promise<JsonRecord | null> }).getRun(runId);
    expect(retryScheduled).toMatchObject({ timeoutCount: 1, retryCount: 1 });
    const retryTask = (retryScheduled?.tasks as JsonRecord[])[0];
    expect(retryTask.retryCount).toBe(1);
    expect(["retry_scheduled", "pending"]).toContain(retryTask.state);

    if (retryTask.state === "retry_scheduled") {
      await sleep(1100);
      expect(await runDurableObjectAlarm(stub)).toBe(true);
    }
    const retryReady = await (stub as unknown as { getRun(runId: string): Promise<JsonRecord | null> }).getRun(runId);
    expect((retryReady?.tasks as JsonRecord[])[0]).toMatchObject({ state: "pending", retryCount: 1 });
  });

  it("rejects single create requests above the pending task threshold", async () => {
    const response = await api("/runs", {
      method: "POST",
      role: "user",
      body: createRunBody("backpressure", {
        taskSpecs: Array.from({ length: 101 }, (_, index) => ({
          taskId: `task_backpressure_${index}`,
          agentId: `agent_backpressure_${index}`,
          allowedTools: ["codex_cli_model_review"],
        })),
      }),
    });

    expect(response.status).toBe(429);
    await expectError(response, "backpressure_active");
  });

  it("enforces JSON size using bytes actually read", async () => {
    const response = await api("/runs", {
      method: "POST",
      role: "user",
      body: createRunBody("oversize_actual_bytes", {
        requestSummary: "x".repeat(70 * 1024),
      }),
    });

    expect(response.status).toBe(413);
    await expectError(response, "payload_too_large");
  });

  it("reports diagnostics without leaking bearer tokens or local CAD paths", async () => {
    const bridgeId = "bridge_runtime_alt";
    await api("/bridges/register", { method: "POST", role: "bridge", body: bridgeBody(bridgeId, "diag_register") });
    await api("/runs", {
      method: "POST",
      role: "user",
      body: createRunBody("diag_redaction", {
        requestSummary: "token local-worker-token at C:\\Users\\User\\Desktop\\CAD-AGENT\\secret.dwg",
      }),
    });

    const diagnostics = await api(`/diagnostics?workspaceId=${WORKSPACE_ID}`, { method: "GET", role: "admin" });
    expect(diagnostics.status).toBe(200);
    const text = await diagnostics.text();
    expect(text).not.toContain("local-worker-token");
    expect(text).not.toContain("C:\\Users\\User\\Desktop");
    expect(JSON.parse(text)).toMatchObject({
      status: "ok",
      schemaVersion: "worker_run_state/v2",
    });

    const nonAdmin = await api(`/diagnostics?workspaceId=${WORKSPACE_ID}`, { method: "GET", role: "user" });
    expect(nonAdmin.status).toBe(403);
    await expectError(nonAdmin, "auth_role_forbidden");
  });
});

async function api(path: string, init: { method: string; role?: Role; body?: JsonRecord; origin?: string }): Promise<Response> {
  const headers = new Headers();
  headers.set("Accept", "application/json");
  if (init.body !== undefined) {
    headers.set("Content-Type", "application/json");
  }
  if (init.role) {
    headers.set("Authorization", `Bearer ${tokenForRole(init.role)}`);
  }
  if (init.origin) {
    headers.set("Origin", init.origin);
  }
  return SELF.fetch(`${BASE}${path}`, {
    method: init.method,
    headers,
    body: init.body === undefined ? undefined : JSON.stringify(init.body),
  });
}

function tokenForRole(role: Role): string {
  if (role === "admin") {
    return ADMIN_TOKEN;
  }
  if (role === "bridge") {
    return BRIDGE_TOKEN;
  }
  return USER_TOKEN;
}

async function expectJson(response: Response, expected: JsonRecord): Promise<void> {
  expect(await response.json()).toMatchObject(expected);
}

async function expectError(response: Response, code: string): Promise<void> {
  expect(await response.json()).toMatchObject({ error: code });
}

function createRunBody(label: string, extra: JsonRecord = {}): JsonRecord {
  return {
    workspaceId: WORKSPACE_ID,
    targetStage: "worker_orchestration_ready",
    requestedBy: "runtime-test",
    requestSummary: `runtime contract ${label}`,
    requestId: unique(`run_${label}`),
    agentIds: ["agent_runtime"],
    ...extra,
  };
}

function bridgeBody(bridgeId: string, label: string): JsonRecord {
  return {
    schemaVersion: "local_bridge_registration/v1",
    bridgeId,
    machineId: "runtime-machine",
    bridgeInstanceId: `${bridgeId}-instance`,
    workspaceId: WORKSPACE_ID,
    version: "runtime-test",
    protocolVersion: "bridge_protocol/v1",
    requestId: unique(`bridge_${label}`),
    state: "online",
    capabilities: [
      {
        capabilityId: "runtime_model_review",
        version: "v1",
        supportedStages: ["worker_orchestration_ready"],
        allowedTools: ["codex_cli_model_review"],
        forbiddenActions: ["shell_arbitrary", "save_current_dwg", "cad_mcp_execute"],
        maxConcurrentLeases: 1,
        savedCurrentDwg: false,
      },
    ],
  };
}

function leaseBody(runId: string, bridgeId: string, label: string): JsonRecord {
  return {
    runId,
    workspaceId: WORKSPACE_ID,
    bridgeId,
    machineId: "runtime-machine",
    bridgeInstanceId: `${bridgeId}-instance`,
    requestId: unique(`lease_${label}`),
  };
}

function heartbeatBody(lease: JsonRecord, heartbeatSeq: number, label: string): JsonRecord {
  return {
    workspaceId: WORKSPACE_ID,
    bridgeId: lease.bridgeId,
    machineId: lease.machineId,
    bridgeInstanceId: lease.bridgeInstanceId,
    runId: lease.runId,
    taskId: lease.taskId,
    leaseId: lease.leaseId,
    heartbeatToken: lease.heartbeatToken,
    heartbeatSeq,
    bridgeStatus: "running",
    requestId: unique(`heartbeat_${label}`),
  };
}

function submitBody(runId: string, taskId: string, leaseId: string): JsonRecord {
  return {
    workspaceId: WORKSPACE_ID,
    runId,
    taskId,
    leaseId,
    heartbeatToken: "placeholder",
    attempt: 1,
    bridgeId: "bridge_runtime",
    machineId: "runtime-machine",
    bridgeInstanceId: "bridge_runtime-instance",
    idempotencyKey: unique("submit_placeholder"),
    resultHash: "placeholder",
    result: { status: "completed", schemaValid: true, savedCurrentDwg: false },
  };
}

function submitBodyFromLease(lease: JsonRecord, result: JsonRecord, resultHash: string, label: string): JsonRecord {
  return {
    workspaceId: WORKSPACE_ID,
    runId: lease.runId,
    taskId: lease.taskId,
    leaseId: lease.leaseId,
    heartbeatToken: lease.heartbeatToken,
    attempt: lease.attempt,
    bridgeId: lease.bridgeId,
    machineId: lease.machineId,
    bridgeInstanceId: lease.bridgeInstanceId,
    idempotencyKey: unique(label),
    resultHash,
    result,
  };
}

function agentResult(lease: JsonRecord, summary: string): JsonRecord {
  return {
    schemaVersion: "agent_output/v1",
    runId: lease.runId,
    taskId: lease.taskId,
    agentId: (lease.envelope as JsonRecord).agentId,
    status: "completed",
    decision: "continue",
    summary,
    modelInvoked: true,
    modelUnavailable: false,
    schemaValid: true,
    traceRef: "runtime-test",
    evidenceRefs: ["runtime-test"],
    blockedReason: "",
    savedCurrentDwg: false,
  };
}

async function leaseFreshRun(
  bridgeId: string,
  label: string,
  createExtra: JsonRecord = {},
): Promise<{ bridgeId: string; runId: string; lease: JsonRecord; leaseRequest: JsonRecord }> {
  await api("/bridges/register", { method: "POST", role: "bridge", body: bridgeBody(bridgeId, `${label}_register`) });
  const created = await api("/runs", { method: "POST", role: "user", body: createRunBody(label, createExtra) });
  expect(created.status).toBe(201);
  const run = await created.json<JsonRecord>();
  const runId = String(run.runId);
  const leaseRequest = leaseBody(runId, bridgeId, `${label}_lease`);
  const leased = await api(`/runs/${runId}/lease`, { method: "POST", role: "bridge", body: leaseRequest });
  expect(leased.status).toBe(200);
  return { bridgeId, runId, lease: await leased.json<JsonRecord>(), leaseRequest };
}

async function forceBridgeStale(bridgeId: string): Promise<void> {
  const stub = runStateStub(WORKSPACE_ID) as unknown as { __debugSetBridgeLastSeenAt(bridgeId: string, lastSeenAt: string): Promise<JsonRecord> };
  await stub.__debugSetBridgeLastSeenAt(bridgeId, new Date(Date.now() - 120_000).toISOString().replace(/\.\d{3}Z$/, "Z"));
}

function runStateStub(workspaceId: string): DurableObjectStub {
  return env.RUN_STATE.getByName(`workspace:${workspaceId}`);
}

function unique(prefix: string): string {
  return `${prefix}_${Date.now()}_${crypto.randomUUID().replace(/-/g, "").slice(0, 8)}`;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function sha256Hex(value: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

function stableJson(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableJson(item)).join(",")}]`;
  }
  if (value && typeof value === "object") {
    return `{${Object.keys(value as Record<string, unknown>)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${stableJson((value as Record<string, unknown>)[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}
