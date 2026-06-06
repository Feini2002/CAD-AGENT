import { DEFAULT_WORKSPACE_ID, KILL_SWITCHES } from "./constants";
import { assertClaimsAllowed, authenticate } from "./auth";
import { ApiError, errorResponse, jsonResponse, optionsResponse } from "./responses";
import { redactForLog } from "./redaction";
import { RunStateDurableObject } from "./run-state-do";
import { slug } from "./state-machine";
import type { AuthContext, AuthRole, CreateRunInput, JsonObject, MutationMeta } from "./types";
import {
  mutationKey,
  readJsonObject,
  sha256Hex,
  stableJson,
  validateCreateRunInput,
  validateHeartbeatInput,
  validateLeaseTaskInput,
  validateOfflineBridgeInput,
  validateRegisterBridgeInput,
  validateSubmitResultInput,
} from "./validation";

type RunStateRpc = {
  health(): Promise<JsonObject>;
  listRuns(limit?: number): Promise<JsonObject[]>;
  getRun(runId: string): Promise<unknown | null>;
  createRun(input: unknown, auth: AuthContext, meta: MutationMeta): Promise<JsonObject>;
  registerBridge(input: unknown, auth: AuthContext, meta: MutationMeta): Promise<JsonObject>;
  listBridges(): Promise<JsonObject[]>;
  getBridge(bridgeId: string): Promise<JsonObject | null>;
  markBridgeOffline(input: unknown, auth: AuthContext, meta: MutationMeta): Promise<JsonObject>;
  leaseTask(input: unknown, auth: AuthContext, meta: MutationMeta): Promise<JsonObject>;
  heartbeatBridge(input: unknown, auth: AuthContext, meta: MutationMeta): Promise<JsonObject>;
  submitResult(input: unknown, auth: AuthContext, meta: MutationMeta): Promise<JsonObject>;
  diagnostics(): Promise<unknown>;
  recordAuthFailure(input: { route: string; clientKey: string; code: string }): Promise<JsonObject>;
};

export async function routeRequest(request: Request, env: Env): Promise<Response> {
  try {
  const url = new URL(request.url);
  const parts = url.pathname.split("/").filter(Boolean);

  if (request.method === "OPTIONS") {
    return optionsResponse(request, env);
  }

  if (request.method === "GET" && parts.length === 1 && parts[0] === "health") {
    const workspaceId = sanitizeWorkspaceId(url.searchParams.get("workspaceId") || undefined, env);
    return jsonResponse(
      {
        status: "ok",
        schemaVersion: "worker_run_state/v2",
        now: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
        service: "cad-agent-orchestrator",
        version: env.ORCHESTRATOR_VERSION || "mvp-0.1.0",
        workspaceId,
        boundaries: {
          workerExecutesShell: false,
          workerSavesCurrentDwg: false,
          cadReadbackRequiredForCadClaims: true,
        },
      },
      {},
      request,
      env,
    );
  }

  if (parts[0] === "runs") {
    if (request.method === "GET" && parts.length === 1) {
      const workspaceId = sanitizeWorkspaceId(url.searchParams.get("workspaceId") || undefined, env);
      const auth = await authenticateWithFailureLimit(request, env, ["user", "admin"], { workspaceId });
      assertClaimsAllowed(auth, { workspaceId });
      const limit = Number(url.searchParams.get("limit") || 50);
      const runs = await runStateStub(env, workspaceId).listRuns(limit);
      return jsonResponse({ status: "ok", workspaceId, runs }, {}, request, env);
    }

    if (request.method === "POST" && parts.length === 1) {
      assertSwitch(env, KILL_SWITCHES.orchestrator);
      assertSwitch(env, KILL_SWITCHES.createRun);
      const body = await readJsonObject(request);
      const input = validateCreateRunInput(body);
      assertCreateRequestWithinBackpressure(input, env);
      const workspaceId = sanitizeWorkspaceId(input.workspaceId, env);
      const auth = await authenticateWithFailureLimit(request, env, ["user", "admin"], { workspaceId });
      const meta = await mutationMeta(request, auth, workspaceId, body, "/runs", mutationKey(input));
      const state = await runStateStub(env, workspaceId).createRun({ ...input, workspaceId }, auth, meta);
      return jsonResponse(state, { status: 201 }, request, env);
    }

    if (request.method === "GET" && parts.length === 2) {
      const workspaceId = sanitizeWorkspaceId(url.searchParams.get("workspaceId") || undefined, env);
      const auth = await authenticateWithFailureLimit(request, env, ["user", "admin"], { workspaceId });
      assertClaimsAllowed(auth, { workspaceId });
      const state = await runStateStub(env, workspaceId).getRun(decodeURIComponent(parts[1]));
      if (!state) {
        throw new ApiError(404, "run_not_found", "Run was not found in this workspace.");
      }
      return jsonResponse(redactForLog(state), {}, request, env);
    }

    if (request.method === "POST" && parts.length === 3 && parts[2] === "lease") {
      assertSwitch(env, KILL_SWITCHES.orchestrator);
      assertSwitch(env, KILL_SWITCHES.bridgeLeasing);
      const body = await readJsonObject(request);
      const input = validateLeaseTaskInput(decodeURIComponent(parts[1]), body);
      const workspaceId = sanitizeWorkspaceId(input.workspaceId, env);
      const auth = await authenticateWithFailureLimit(request, env, ["bridge"], { workspaceId, bridgeId: input.bridgeId });
      const meta = await mutationMeta(request, auth, workspaceId, body, `/runs/${input.runId}/lease`, mutationKey(input), {
        runId: input.runId,
        bridgeId: input.bridgeId,
      });
      const result = await runStateStub(env, workspaceId).leaseTask({ ...input, workspaceId }, auth, meta);
      return jsonResponse(result, {}, request, env);
    }
  }

  if (parts[0] === "bridges") {
    if (request.method === "POST" && parts.length === 2 && parts[1] === "register") {
      assertSwitch(env, KILL_SWITCHES.orchestrator);
      const body = await readJsonObject(request);
      const input = validateRegisterBridgeInput(body);
      const workspaceId = sanitizeWorkspaceId(input.workspaceId, env);
      const auth = await authenticateWithFailureLimit(request, env, ["bridge"], { workspaceId, bridgeId: input.bridgeId });
      const meta = await mutationMeta(request, auth, workspaceId, body, "/bridges/register", mutationKey(input), {
        bridgeId: input.bridgeId,
      });
      const result = await runStateStub(env, workspaceId).registerBridge({ ...input, workspaceId }, auth, meta);
      return jsonResponse(result, { status: 201 }, request, env);
    }

    if (request.method === "GET" && parts.length === 1) {
      const workspaceId = sanitizeWorkspaceId(url.searchParams.get("workspaceId") || undefined, env);
      await authenticateWithFailureLimit(request, env, ["admin"], { workspaceId });
      const bridges = await runStateStub(env, workspaceId).listBridges();
      return jsonResponse({ status: "ok", workspaceId, bridges }, {}, request, env);
    }

    if (request.method === "GET" && parts.length === 2) {
      const workspaceId = sanitizeWorkspaceId(url.searchParams.get("workspaceId") || undefined, env);
      await authenticateWithFailureLimit(request, env, ["admin"], { workspaceId });
      const bridge = await runStateStub(env, workspaceId).getBridge(decodeURIComponent(parts[1]));
      if (!bridge) {
        throw new ApiError(404, "bridge_not_found", "Bridge was not found.");
      }
      return jsonResponse(bridge, {}, request, env);
    }

    if (request.method === "POST" && parts.length === 3 && parts[2] === "offline") {
      assertSwitch(env, KILL_SWITCHES.orchestrator);
      const body = await readJsonObject(request);
      const input = validateOfflineBridgeInput(decodeURIComponent(parts[1]), body);
      const workspaceId = sanitizeWorkspaceId(input.workspaceId, env);
      const auth = await authenticateWithFailureLimit(request, env, ["bridge", "admin"], { workspaceId, bridgeId: input.bridgeId });
      const meta = await mutationMeta(request, auth, workspaceId, body, `/bridges/${input.bridgeId}/offline`, mutationKey(input), {
        bridgeId: input.bridgeId,
      });
      const result = await runStateStub(env, workspaceId).markBridgeOffline({ ...input, workspaceId }, auth, meta);
      return jsonResponse(result, {}, request, env);
    }

    if (request.method === "POST" && parts.length === 3 && parts[2] === "heartbeat") {
      return handleHeartbeat(request, env, bodyRoute(`/bridges/${decodeURIComponent(parts[1])}/heartbeat`, decodeURIComponent(parts[1])));
    }
  }

  if (request.method === "POST" && parts.length === 1 && parts[0] === "heartbeat") {
    return handleHeartbeat(request, env, bodyRoute("/heartbeat"));
  }

  if (request.method === "POST" && parts.length === 1 && parts[0] === "submit") {
    assertSwitch(env, KILL_SWITCHES.orchestrator);
    assertSwitch(env, KILL_SWITCHES.submit);
    const body = await readJsonObject(request);
    const input = validateSubmitResultInput(body);
    const workspaceId = sanitizeWorkspaceId(input.workspaceId, env);
    const auth = await authenticateWithFailureLimit(request, env, ["bridge"], { workspaceId, bridgeId: input.bridgeId });
    const meta = await mutationMeta(request, auth, workspaceId, body, "/submit", input.idempotencyKey, {
      runId: input.runId,
      taskId: input.taskId,
      bridgeId: input.bridgeId,
      leaseId: input.leaseId,
      attempt: input.attempt,
    });
    const result = await runStateStub(env, workspaceId).submitResult({ ...input, workspaceId }, auth, meta);
    return jsonResponse(result, {}, request, env);
  }

  if (request.method === "GET" && parts.length === 1 && parts[0] === "diagnostics") {
    const workspaceId = sanitizeWorkspaceId(url.searchParams.get("workspaceId") || undefined, env);
    await authenticateWithFailureLimit(request, env, ["admin"], { workspaceId });
    const diagnostics = await runStateStub(env, workspaceId).diagnostics();
    return jsonResponse(redactForLog(diagnostics), {}, request, env);
  }

  if (request.method === "GET" && parts.length === 1 && parts[0] === "bridge-protocol") {
    const workspaceId = sanitizeWorkspaceId(url.searchParams.get("workspaceId") || undefined, env);
    await authenticateWithFailureLimit(request, env, ["admin"], { workspaceId });
    return jsonResponse(bridgeProtocolDeclaration(), {}, request, env);
  }

  throw new ApiError(404, "not_found", "Route not found.");
  } catch (error) {
    return errorResponse(error, request, env);
  }
}

async function handleHeartbeat(
  request: Request,
  env: Env,
  route: { route: string; bridgeIdFromPath?: string },
): Promise<Response> {
  assertSwitch(env, KILL_SWITCHES.orchestrator);
  const body = await readJsonObject(request);
  const input = validateHeartbeatInput(body);
  if (route.bridgeIdFromPath && route.bridgeIdFromPath !== input.bridgeId) {
    throw new ApiError(403, "bridge_identity_mismatch", "Path bridge id does not match body bridge id.");
  }
  const workspaceId = sanitizeWorkspaceId(input.workspaceId, env);
  const auth = await authenticateWithFailureLimit(request, env, ["bridge"], { workspaceId, bridgeId: input.bridgeId });
  const meta = await mutationMeta(request, auth, workspaceId, body, route.route, mutationKey(input), {
    runId: input.runId,
    taskId: input.taskId,
    bridgeId: input.bridgeId,
    leaseId: input.leaseId,
  });
  const result = await runStateStub(env, workspaceId).heartbeatBridge({ ...input, workspaceId }, auth, meta);
  return jsonResponse(result, {}, request, env);
}

export function sanitizeWorkspaceId(value: string | undefined, env: Env): string {
  return slug(value || env.DEFAULT_WORKSPACE_ID || DEFAULT_WORKSPACE_ID);
}

function runStateStub(env: Env, workspaceId: string): RunStateRpc {
  return env.RUN_STATE.getByName(`workspace:${workspaceId}`) as unknown as RunStateRpc;
}

async function authenticateWithFailureLimit(
  request: Request,
  env: Env,
  allowedRoles: AuthRole[],
  claims: { workspaceId?: string; bridgeId?: string } = {},
): Promise<AuthContext> {
  try {
    return await authenticate(request, env, allowedRoles, claims);
  } catch (error) {
    if (error instanceof ApiError && isAuthFailureCode(error.code)) {
      const workspaceId = sanitizeWorkspaceId(claims.workspaceId, env);
      const route = `${request.method} ${new URL(request.url).pathname}`;
      try {
        const result = await runStateStub(env, workspaceId).recordAuthFailure({
          route,
          clientKey: await authClientKey(request),
          code: error.code,
        });
        if (result.status === "rate_limited") {
          throw new ApiError(429, "backpressure_active", "Auth failure rate limit exceeded.");
        }
      } catch (recordError) {
        if (recordError instanceof ApiError && recordError.code === "backpressure_active") {
          throw recordError;
        }
      }
    }
    throw error;
  }
}

async function mutationMeta(
  request: Request,
  auth: AuthContext,
  workspaceId: string,
  body: JsonObject,
  route: string,
  key: string,
  extra: Partial<MutationMeta> = {},
): Promise<MutationMeta> {
  return {
    route,
    method: request.method,
    authSubject: auth.subjectId,
    workspaceId,
    idempotencyKey: key,
    bodyHash: await sha256Hex(stableJson(body)),
    ...extra,
  };
}

function isAuthFailureCode(code: string): boolean {
  return code === "auth_missing" || code === "auth_invalid" || code === "auth_role_forbidden" || code === "bridge_identity_mismatch";
}

async function authClientKey(request: Request): Promise<string> {
  const raw =
    request.headers.get("CF-Connecting-IP") ||
    request.headers.get("X-Forwarded-For")?.split(",")[0]?.trim() ||
    "local";
  return sha256Hex(raw);
}

function assertSwitch(env: Env, name: string): void {
  if (((env as unknown as Record<string, string | undefined>)[name] || "").toLowerCase() === "true") {
    throw new ApiError(429, "backpressure_active", `${name} is enabled.`);
  }
}

function bodyRoute(route: string, bridgeIdFromPath?: string): { route: string; bridgeIdFromPath?: string } {
  return { route, bridgeIdFromPath };
}

function assertCreateRequestWithinBackpressure(input: CreateRunInput, env: Env): void {
  const requestedTaskCount = input.taskSpecs
    ? input.taskSpecs.length
    : input.agentIds && input.agentIds.length > 0
      ? input.agentIds.length
      : 1;
  const maxPending = boundedEnvInteger(env.MAX_PENDING_TASKS, 100, 1, 10_000);
  if (requestedTaskCount > maxPending) {
    throw new ApiError(429, "backpressure_active", "Requested task count exceeds pending task threshold.");
  }
}

function boundedEnvInteger(value: string | undefined, fallback: number, min: number, max: number): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    return fallback;
  }
  return Math.max(min, Math.min(max, Math.trunc(parsed)));
}

function bridgeProtocolDeclaration(): JsonObject {
  return {
    status: "ok",
    schemaVersion: "bridge_protocol/v1",
    nonExecutionBoundary: {
      workerExecutesShell: false,
      workerSavesCurrentDwg: false,
      savedCurrentDwg: false,
    },
    requiredMutationKey: "requestId or idempotencyKey",
    heartbeatEndpoint: "POST /bridges/:id/heartbeat",
    submitEndpoint: "POST /submit",
    leaseEndpoint: "POST /runs/:id/lease",
  };
}
