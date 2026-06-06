import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";

const baseUrl = process.env.ORCHESTRATOR_URL || "http://127.0.0.1:8787";
const workerToken = process.env.WORKER_API_TOKEN || "local-worker-token";
const bridgeToken = process.env.BRIDGE_API_TOKEN || "local-bridge-token";
const adminToken = process.env.ADMIN_API_TOKEN || "local-admin-token";
const skipRevoke = process.env.WORKER_SMOKE_SKIP_REVOKE === "true";

const workspaceId = "cad-agent-core-lab";
const machineId = "machine_smoke";
const smokeId = Date.now();
const bridgeId = "bridge_local_smoke";
const revokedBridgeId = "bridge_revoke_smoke";
const unregisteredBridgeId = "bridge_unregistered_smoke";
const bridgeInstanceId = `instance_${Date.now()}`;
const revokedBridgeInstanceId = `revoked_instance_${Date.now()}`;

async function request(path, options = {}) {
  const url = new URL(`${baseUrl}${path}`);
  const headers = {
    Connection: "close",
    ...(options.body ? { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(options.body) } : {}),
    ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
    ...(options.headers || {}),
  };
  const { statusCode, responseHeaders, text } = await httpRequest(url, {
    method: options.method || "GET",
    headers,
    body: options.body,
    timeoutSeconds: options.timeoutSeconds || 10,
  });
  const payload = text ? JSON.parse(text) : {};
  if (options.expectStatus && statusCode !== options.expectStatus) {
    throw new Error(`${options.method || "GET"} ${path} -> ${statusCode}, expected ${options.expectStatus}: ${text}`);
  }
  if (!options.expectStatus && !options.allowError && (statusCode < 200 || statusCode >= 300)) {
    throw new Error(`${options.method || "GET"} ${path} -> ${statusCode}: ${text}`);
  }
  return { response: { status: statusCode, headers: responseHeaders }, payload };
}

async function expectError(path, options, status, code) {
  const expectedStatuses = Array.isArray(status) ? status : [status];
  const { response, payload } = await request(path, { ...options, allowError: true });
  if (!expectedStatuses.includes(response.status)) {
    throw new Error(`${options.method || "GET"} ${path} -> ${response.status}, expected ${expectedStatuses.join(" or ")}: ${JSON.stringify(payload)}`);
  }
  const codes = Array.isArray(code) ? code : [code];
  if (!codes.includes(payload.error)) {
    throw new Error(`expected ${codes.join(" or ")} from ${path}, got ${JSON.stringify(payload)}`);
  }
}

function capability(capabilityId = "codex_cli_model_review", allowedTools = ["codex_cli_model_review"]) {
  return {
    capabilityId,
    version: "1.0.0",
    supportedStages: ["worker_orchestration_ready", "local_bridge_connected"],
    allowedTools,
    forbiddenActions: ["shell_arbitrary", "save_current_dwg", "delete_unscoped_entities", "upload_full_repo"],
    maxConcurrentLeases: 2,
    savedCurrentDwg: false,
  };
}

function stableJson(value) {
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableJson(item)).join(",")}]`;
  }
  if (value && typeof value === "object") {
    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

function hashJson(value) {
  return createHash("sha256").update(stableJson(value)).digest("hex");
}

function httpRequest(url, options) {
  const args = ["--max-time", String(options.timeoutSeconds || 10), "-sS", "-i", "-X", options.method];
  for (const [name, value] of Object.entries(options.headers || {})) {
    args.push("-H", `${name}: ${value}`);
  }
  if (options.body) {
    if (options.body.length > 8000) {
      const dir = mkdtempSync(path.join(tmpdir(), "worker-smoke-"));
      const file = path.join(dir, "body.json");
      writeFileSync(file, options.body);
      args.push("--data-binary", `@${file}`);
      args.push(url.href);
      try {
        return runCurl(url, args, dir);
      } finally {
        rmSync(dir, { recursive: true, force: true });
      }
    }
    args.push("--data-binary", options.body);
  }
  args.push(url.href);
  return Promise.resolve(runCurl(url, args));
}

function runCurl(url, args, tempDir) {
  const result = spawnSync("curl.exe", args, { encoding: "utf8" });
  if (result.status !== 0) {
    throw new Error(`curl failed for ${url.pathname}: ${result.error?.message || result.stderr || result.stdout}`);
  }
  const raw = result.stdout;
  const splitIndex = raw.indexOf("\r\n\r\n") >= 0 ? raw.indexOf("\r\n\r\n") : raw.indexOf("\n\n");
  const headerText = splitIndex >= 0 ? raw.slice(0, splitIndex) : raw;
  const text = splitIndex >= 0 ? raw.slice(splitIndex + (raw[splitIndex] === "\r" ? 4 : 2)) : "";
  const statusLine = headerText.split(/\r?\n/)[0] || "";
  const statusCode = Number(statusLine.split(" ")[1] || 0);
  const responseHeaders = {};
  for (const line of headerText.split(/\r?\n/).slice(1)) {
    const colon = line.indexOf(":");
    if (colon > 0) {
      responseHeaders[line.slice(0, colon).trim().toLowerCase()] = line.slice(colon + 1).trim();
    }
  }
  return { statusCode, responseHeaders, text };
}

function step(name) {
  process.stderr.write(`[worker-smoke] ${name}\n`);
}

function rid(name) {
  return `${name}_${smokeId}`;
}

async function createRun(body = {}) {
  const { payload } = await request("/runs", {
    method: "POST",
    token: workerToken,
    body: JSON.stringify({
      requestSummary: "smoke test worker orchestration only",
      workspaceId,
      targetStage: "worker_orchestration_ready",
      agentIds: ["pipeline_orchestrator"],
      requestId: `create_${Date.now()}_${Math.random()}`,
      ...body,
    }),
  });
  return payload;
}

async function registerBridge(extra = {}) {
  const { payload } = await request("/bridges/register", {
    method: "POST",
    token: bridgeToken,
    body: JSON.stringify({
      bridgeId,
      machineId,
      bridgeInstanceId,
      workspaceId,
      version: "smoke",
      protocolVersion: "bridge_protocol/v1",
      capabilities: [capability()],
      requestId: `register_${Date.now()}_${Math.random()}`,
      ...extra,
    }),
  });
  return payload;
}

async function lease(runId, expectStatus) {
  const { payload } = await request(`/runs/${encodeURIComponent(runId)}/lease`, {
    method: "POST",
    token: bridgeToken,
    expectStatus,
    body: JSON.stringify({
      workspaceId,
      bridgeId,
      machineId,
      bridgeInstanceId,
      requestId: `lease_${Date.now()}_${Math.random()}`,
    }),
  });
  return payload;
}

async function waitForHealth() {
  let lastError;
  for (let attempt = 1; attempt <= 12; attempt += 1) {
    try {
      return await request("/health", { timeoutSeconds: 3 });
    } catch (error) {
      lastError = error;
      await new Promise((resolve) => setTimeout(resolve, 1500));
    }
  }
  throw lastError;
}

step("health");
const health = await waitForHealth();
if (health.payload.status !== "ok") {
  throw new Error(`expected healthy worker, got ${JSON.stringify(health.payload)}`);
}
if (health.response.headers["access-control-allow-origin"]) {
  throw new Error("CORS should be closed by default for health response");
}

step("auth negatives");
await expectError("/runs", { method: "POST", body: JSON.stringify({ requestId: rid("missing_auth") }) }, 401, "auth_missing");
step("heartbeat before register");
await expectError(
  "/runs",
  { method: "POST", token: "wrong", body: JSON.stringify({ requestId: rid("wrong_auth") }) },
  401,
  "auth_invalid",
);
await expectError(
  "/runs",
  { method: "POST", token: workerToken, body: JSON.stringify({ workspaceId: "other", requestId: rid("bad_workspace") }) },
  403,
  "auth_role_forbidden",
);
await expectError(
  "/runs",
  {
    method: "POST",
    token: workerToken,
    body: JSON.stringify({ workspaceId, targetStage: "bogus", requestId: rid("bad_stage") }),
  },
  400,
  "invalid_target_stage",
);
await expectError(
  "/runs",
  {
    method: "POST",
    token: workerToken,
    body: JSON.stringify({
      workspaceId,
      requestId: rid("dangerous_tool"),
      taskSpecs: [{ taskId: "bad", allowedTools: ["powershell"] }],
    }),
  },
  422,
  "forbidden_tool_requested",
);
await expectError(
  "/runs",
  {
    method: "POST",
    token: workerToken,
    body: JSON.stringify({ workspaceId, requestId: rid("oversize"), requestSummary: "x".repeat(70 * 1024) }),
  },
  413,
  "payload_too_large",
);

await expectError(
  "/heartbeat",
  {
    method: "POST",
    token: bridgeToken,
    body: JSON.stringify({
      workspaceId,
      bridgeId,
      machineId,
      bridgeInstanceId,
      runId: "missing",
      taskId: "missing",
      leaseId: "missing",
      heartbeatToken: "missing",
      heartbeatSeq: 1,
      requestId: rid("heartbeat_before_register"),
    }),
  },
  [409, 403],
  ["bridge_unregistered", "bridge_identity_mismatch"],
);

step("register bridge");
await registerBridge();

step("admin bridge list");
const bridges = await request(`/bridges?workspaceId=${workspaceId}`, { token: adminToken });
if (!Array.isArray(bridges.payload.bridges) || bridges.payload.bridges.length < 1) {
  throw new Error("expected bridge list to contain registered bridge");
}

step("capability mismatch");
const mismatchRun = await createRun({
  taskSpecs: [{ taskId: "needs_preview", allowedTools: ["preview_cad_execute"] }],
});
await expectError(
  `/runs/${encodeURIComponent(mismatchRun.runId)}/lease`,
  {
    method: "POST",
    token: bridgeToken,
    body: JSON.stringify({
      workspaceId,
      bridgeId,
      machineId,
      bridgeInstanceId,
      requestId: rid("capability_mismatch"),
    }),
  },
  409,
  "capability_mismatch",
);

step("offline bridge");
const offlineRun = await createRun({ requestId: rid("offline_run") });
await request(`/bridges/${bridgeId}/offline`, {
  method: "POST",
  token: bridgeToken,
  body: JSON.stringify({
    workspaceId,
    bridgeId,
    machineId,
    bridgeInstanceId,
    reason: "smoke_offline",
      requestId: rid("offline_bridge"),
  }),
});
await expectError(
  `/runs/${encodeURIComponent(offlineRun.runId)}/lease`,
  {
    method: "POST",
    token: bridgeToken,
    body: JSON.stringify({ workspaceId, bridgeId, machineId, bridgeInstanceId, requestId: rid("offline_lease") }),
  },
  409,
  "bridge_offline",
);

step("valid lease");
const reRegistered = await registerBridge();
if (reRegistered.bridge?.state !== "online") {
  throw new Error(`expected bridge online after re-register, got ${JSON.stringify(reRegistered)}`);
}
const bridgeAfterRegister = await request(`/bridges/${bridgeId}?workspaceId=${workspaceId}`, { token: adminToken });
if (bridgeAfterRegister.payload.state !== "online") {
  throw new Error(`expected stored bridge online after re-register, got ${JSON.stringify(bridgeAfterRegister.payload)}`);
}
const run = await createRun({ requestId: rid("valid_run") });
const leased = await lease(run.runId);
if (leased.status !== "leased" || !leased.leaseId || leased.constraints.savedCurrentDwg !== false) {
  throw new Error(`expected lease envelope, got ${JSON.stringify(leased)}`);
}

step("lease mismatch");
await expectError(
  `/bridges/${bridgeId}/heartbeat`,
  {
    method: "POST",
    token: bridgeToken,
    body: JSON.stringify({
      workspaceId,
      bridgeId,
      machineId,
      bridgeInstanceId,
      runId: run.runId,
      taskId: leased.taskId,
      leaseId: "wrong",
      heartbeatToken: leased.heartbeatToken,
      heartbeatSeq: 1,
      requestId: rid("wrong_lease"),
    }),
  },
  409,
  "lease_mismatch",
);

step("heartbeat success");
await expectError(
  `/bridges/${bridgeId}/heartbeat`,
  {
    method: "POST",
    token: bridgeToken,
    body: JSON.stringify({
      workspaceId,
      bridgeId,
      machineId,
      bridgeInstanceId,
      runId: run.runId,
      taskId: leased.taskId,
      leaseId: leased.leaseId,
      heartbeatToken: "not-the-issued-token",
      heartbeatSeq: 1,
      requestId: rid("heartbeat_wrong_token"),
    }),
  },
  409,
  "lease_mismatch",
);
await request(`/bridges/${bridgeId}/heartbeat`, {
  method: "POST",
  token: bridgeToken,
  body: JSON.stringify({
    workspaceId,
    bridgeId,
    machineId,
    bridgeInstanceId,
    runId: run.runId,
    taskId: leased.taskId,
    leaseId: leased.leaseId,
    heartbeatToken: leased.heartbeatToken,
    heartbeatSeq: 1,
    bridgeStatus: "running smoke test",
    requestId: rid("heartbeat_1"),
  }),
});
step("heartbeat stale");
await expectError(
  `/bridges/${bridgeId}/heartbeat`,
  {
    method: "POST",
    token: bridgeToken,
    body: JSON.stringify({
      workspaceId,
      bridgeId,
      machineId,
      bridgeInstanceId,
      runId: run.runId,
      taskId: leased.taskId,
      leaseId: leased.leaseId,
      heartbeatToken: leased.heartbeatToken,
      heartbeatSeq: 0,
      requestId: rid("heartbeat_stale"),
    }),
  },
  409,
  "heartbeat_out_of_order",
);

const result = {
  schemaVersion: "agent_output/v1",
  status: "completed",
  decision: "continue",
  summary: "smoke result accepted",
  modelInvoked: false,
  modelUnavailable: false,
  schemaValid: true,
  evidenceRefs: [],
  traceRef: "",
  savedCurrentDwg: false,
};
const submitBody = {
  workspaceId,
  runId: run.runId,
  taskId: leased.taskId,
  bridgeId,
  machineId,
  bridgeInstanceId,
  leaseId: leased.leaseId,
  heartbeatToken: leased.heartbeatToken,
  attempt: leased.attempt,
  idempotencyKey: `${run.runId}:${leased.taskId}:smoke`,
  resultHash: hashJson(result),
  result,
};

step("submit role negative");
await expectError(
  "/submit",
  {
    method: "POST",
    token: workerToken,
    body: JSON.stringify(submitBody),
  },
  403,
  "auth_role_forbidden",
);

step("submit wrong heartbeat token");
await expectError(
  "/submit",
  {
    method: "POST",
    token: bridgeToken,
    body: JSON.stringify({ ...submitBody, heartbeatToken: "not-the-issued-token", idempotencyKey: `${run.runId}:${leased.taskId}:wrong-token` }),
  },
  409,
  "lease_mismatch",
);

step("submit accepted");
await request("/submit", {
  method: "POST",
  token: bridgeToken,
  body: JSON.stringify(submitBody),
});
step("duplicate submit");
await request("/submit", {
  method: "POST",
  token: bridgeToken,
  body: JSON.stringify(submitBody),
});
step("idempotency conflict");
await expectError(
  "/submit",
  {
    method: "POST",
    token: bridgeToken,
    body: JSON.stringify({ ...submitBody, result: { ...result, summary: "changed" }, resultHash: hashJson({ ...result, summary: "changed" }) }),
  },
  409,
  "idempotency_conflict",
);

step("dangerous submit blocked");
const dangerousRun = await createRun({ requestId: rid("dangerous_submit_run") });
const dangerousLease = await request(`/runs/${encodeURIComponent(dangerousRun.runId)}/lease`, {
  method: "POST",
  token: bridgeToken,
  body: JSON.stringify({
    workspaceId,
    bridgeId,
    machineId,
    bridgeInstanceId,
    requestId: rid("dangerous_submit_lease"),
  }),
});
const dangerousResult = {
  schemaVersion: "agent_output/v1",
  runId: dangerousRun.runId,
  taskId: dangerousLease.payload.taskId,
  agentId: dangerousLease.payload.envelope.agentId,
  status: "completed",
  decision: "continue",
  summary: "dangerous result should be blocked",
  modelInvoked: true,
  modelUnavailable: false,
  schemaValid: true,
  traceRef: "smoke",
  evidenceRefs: ["smoke"],
  blockedReason: "",
  savedCurrentDwg: true,
};
await expectError(
  "/submit",
  {
    method: "POST",
    token: bridgeToken,
    body: JSON.stringify({
      workspaceId,
      runId: dangerousRun.runId,
      taskId: dangerousLease.payload.taskId,
      bridgeId,
      machineId,
      bridgeInstanceId,
      leaseId: dangerousLease.payload.leaseId,
      heartbeatToken: dangerousLease.payload.heartbeatToken,
      attempt: dangerousLease.payload.attempt,
      idempotencyKey: `${dangerousRun.runId}:${dangerousLease.payload.taskId}:dangerous`,
      resultHash: hashJson(dangerousResult),
      result: dangerousResult,
    }),
  },
  422,
  "saved_current_dwg_violation",
);
const dangerousFinal = await request(`/runs/${encodeURIComponent(dangerousRun.runId)}?workspaceId=${workspaceId}`, { token: workerToken });
if (dangerousFinal.payload.state !== "blocked") {
  throw new Error(`expected dangerous run blocked, got ${dangerousFinal.payload.state}`);
}

step("final run read");
const finalState = await request(`/runs/${encodeURIComponent(run.runId)}?workspaceId=${workspaceId}`, { token: workerToken });
if (finalState.payload.state !== "completed") {
  throw new Error(`expected completed run, got ${finalState.payload.state}`);
}

if (skipRevoke) {
  step("revoke bridge skipped");
} else {
  step("revoke bridge");
  const revokedRegisterBody = {
    schemaVersion: "local_bridge_registration/v1",
    bridgeId: revokedBridgeId,
    machineId,
    bridgeInstanceId: revokedBridgeInstanceId,
    workspaceId,
    version: "smoke-test",
    protocolVersion: "bridge_protocol/v1",
    requestId: rid("register_revoke_bridge"),
    capabilities: [capability()],
  };
  await request("/bridges/register", {
    method: "POST",
    token: bridgeToken,
    body: JSON.stringify(revokedRegisterBody),
  });
  await request(`/bridges/${revokedBridgeId}/offline`, {
    method: "POST",
    token: adminToken,
    body: JSON.stringify({
      workspaceId,
      bridgeId: revokedBridgeId,
      reason: "smoke_revoke",
      revoke: true,
      requestId: rid("revoke_bridge"),
    }),
  });
  await expectError(
    "/bridges/register",
    {
      method: "POST",
      token: bridgeToken,
      body: JSON.stringify(revokedRegisterBody),
    },
    409,
    "bridge_revoked",
  );
  await expectError(
    "/bridges/register",
    {
      method: "POST",
      token: bridgeToken,
      body: JSON.stringify({
        ...revokedRegisterBody,
        requestId: rid("reregister_revoked_bridge"),
      }),
    },
    409,
    "bridge_revoked",
  );
  const revokedRun = await createRun({ requestId: rid("revoked_run") });
  await expectError(
    `/runs/${encodeURIComponent(revokedRun.runId)}/lease`,
    {
      method: "POST",
      token: bridgeToken,
      body: JSON.stringify({
        workspaceId,
        bridgeId: revokedBridgeId,
        machineId,
        bridgeInstanceId: revokedBridgeInstanceId,
        requestId: rid("revoked_lease"),
      }),
    },
    409,
    "bridge_revoked",
  );
}

step("diagnostics");
const diagnostics = await request(`/diagnostics?workspaceId=${workspaceId}`, { token: adminToken });
if (!diagnostics.payload.backlog || JSON.stringify(diagnostics.payload).includes("local-bridge-token")) {
  throw new Error(`diagnostics redaction/backlog check failed: ${JSON.stringify(diagnostics.payload)}`);
}

console.log(JSON.stringify({ status: "pass", runId: run.runId, state: finalState.payload.state }, null, 2));
