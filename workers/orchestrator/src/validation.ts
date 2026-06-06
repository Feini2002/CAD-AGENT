import {
  CANONICAL_ALLOWED_TOOLS,
  DEFAULT_FORBIDDEN_ACTIONS,
  DEFAULT_MAX_ATTEMPTS,
  DEFAULT_TASK_TIMEOUT_SECONDS,
  FEATURE_GATE_STAGES,
  FORBIDDEN_WORKER_ACTIONS,
  FORBIDDEN_WORKER_TOOLS,
  MAX_JSON_BYTES,
} from "./constants";
import { ApiError } from "./responses";
import type {
  CapabilityDescriptor,
  CreateRunInput,
  HeartbeatInput,
  JsonObject,
  JsonValue,
  LeaseTaskInput,
  OfflineBridgeInput,
  RegisterBridgeInput,
  SubmitResultInput,
  TargetStage,
  TaskSpec,
} from "./types";

export async function readJsonObject(request: Request, required = true): Promise<JsonObject> {
  const contentType = request.headers.get("Content-Type") || "";
  if (required && !contentType.toLowerCase().includes("application/json")) {
    throw new ApiError(400, "invalid_json", "Expected application/json request body.");
  }
  if (!request.body) {
    if (required) {
      throw new ApiError(400, "missing_required_field", "Expected JSON object body.");
    }
    return {};
  }

  const contentLength = Number(request.headers.get("Content-Length") || 0);
  if (contentLength > MAX_JSON_BYTES) {
    throw new ApiError(413, "payload_too_large", `JSON body must be <= ${MAX_JSON_BYTES} bytes.`);
  }

  try {
    const raw = await request.text();
    const byteLength = new TextEncoder().encode(raw).byteLength;
    if (byteLength > MAX_JSON_BYTES) {
      throw new ApiError(413, "payload_too_large", `JSON body must be <= ${MAX_JSON_BYTES} bytes.`);
    }
    if (!raw.trim()) {
      if (required) {
        throw new ApiError(400, "missing_required_field", "Expected JSON object body.");
      }
      return {};
    }
    const parsed = JSON.parse(raw) as unknown;
    if (!isPlainObject(parsed)) {
      throw new ApiError(400, "invalid_json", "Expected a JSON object body.");
    }
    return parsed as JsonObject;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(400, "invalid_json", "Malformed JSON body.");
  }
}

export function validateCreateRunInput(body: JsonObject): CreateRunInput {
  const targetStage = optionalString(body.targetStage) || "worker_orchestration_ready";
  parseTargetStage(targetStage);

  const input: CreateRunInput = {
    requestSummary: optionalString(body.requestSummary),
    workspaceId: optionalString(body.workspaceId),
    targetStage,
    requestedBy: optionalString(body.requestedBy),
    requestId: optionalString(body.requestId),
    idempotencyKey: optionalString(body.idempotencyKey),
  };

  if (body.agentIds !== undefined) {
    input.agentIds = stringArray(body.agentIds, "agentIds");
  }
  if (body.dependencies !== undefined) {
    input.dependencies = dependencyMap(body.dependencies);
  }
  if (body.taskSpecs !== undefined) {
    if (!Array.isArray(body.taskSpecs)) {
      throw new ApiError(400, "missing_required_field", "taskSpecs must be an array.");
    }
    input.taskSpecs = body.taskSpecs.map((item, index) => validateTaskSpec(item, index));
  }

  const idempotencyKey = mutationKey(input);
  if (!idempotencyKey) {
    throw new ApiError(400, "missing_required_field", "Mutation routes require requestId or idempotencyKey.");
  }
  return input;
}

export function validateTaskSpec(value: JsonValue, index: number): TaskSpec {
  if (!isPlainObject(value)) {
    throw new ApiError(400, "missing_required_field", `taskSpecs[${index}] must be an object.`);
  }
  const spec = value as JsonObject;
  const allowedTools = spec.allowedTools === undefined ? ["codex_cli_model_review"] : stringArray(spec.allowedTools, "allowedTools");
  assertAllowedTools(allowedTools);

  const requestedActions =
    spec.requestedActions === undefined ? [] : stringArray(spec.requestedActions, "requestedActions");
  assertAllowedActions(requestedActions);

  const forbiddenActions =
    spec.forbiddenActions === undefined ? DEFAULT_FORBIDDEN_ACTIONS : stringArray(spec.forbiddenActions, "forbiddenActions");

  return {
    taskId: optionalString(spec.taskId),
    agentId: optionalString(spec.agentId),
    promptPackId: optionalString(spec.promptPackId),
    dependsOn: spec.dependsOn === undefined ? [] : stringArray(spec.dependsOn, "dependsOn"),
    inputRefs: spec.inputRefs === undefined ? [] : stringArray(spec.inputRefs, "inputRefs"),
    allowedTools,
    forbiddenActions,
    requestedActions,
    outputSchema: optionalString(spec.outputSchema),
    timeoutSeconds: boundedInteger(spec.timeoutSeconds, DEFAULT_TASK_TIMEOUT_SECONDS, 1, 300),
    maxAttempts: boundedInteger(spec.maxAttempts, DEFAULT_MAX_ATTEMPTS, 1, 5),
    idempotencyKey: optionalString(spec.idempotencyKey),
  };
}

export function validateRegisterBridgeInput(body: JsonObject): RegisterBridgeInput {
  const input = {
    schemaVersion: optionalString(body.schemaVersion),
    bridgeId: requiredString(body.bridgeId, "bridgeId"),
    machineId: requiredString(body.machineId, "machineId"),
    bridgeInstanceId: requiredString(body.bridgeInstanceId, "bridgeInstanceId"),
    workspaceId: requiredString(body.workspaceId, "workspaceId"),
    version: requiredString(body.version, "version"),
    protocolVersion: requiredString(body.protocolVersion, "protocolVersion"),
    capabilities: validateCapabilities(body.capabilities),
    state: optionalBridgeState(body.state),
    requestId: optionalString(body.requestId),
    idempotencyKey: optionalString(body.idempotencyKey),
  };
  if (!mutationKey(input)) {
    throw new ApiError(400, "missing_required_field", "Mutation routes require requestId or idempotencyKey.");
  }
  return input;
}

export function validateLeaseTaskInput(runId: string, body: JsonObject): LeaseTaskInput {
  const input = {
    runId,
    workspaceId: requiredString(body.workspaceId, "workspaceId"),
    bridgeId: requiredString(body.bridgeId, "bridgeId"),
    machineId: requiredString(body.machineId, "machineId"),
    bridgeInstanceId: requiredString(body.bridgeInstanceId, "bridgeInstanceId"),
    requestId: optionalString(body.requestId),
    idempotencyKey: optionalString(body.idempotencyKey),
  };
  if (!mutationKey(input)) {
    throw new ApiError(400, "missing_required_field", "Mutation routes require requestId or idempotencyKey.");
  }
  return input;
}

export function validateHeartbeatInput(body: JsonObject): HeartbeatInput {
  const input = {
    workspaceId: requiredString(body.workspaceId, "workspaceId"),
    bridgeId: requiredString(body.bridgeId, "bridgeId"),
    machineId: requiredString(body.machineId, "machineId"),
    bridgeInstanceId: requiredString(body.bridgeInstanceId, "bridgeInstanceId"),
    runId: requiredString(body.runId, "runId"),
    taskId: requiredString(body.taskId, "taskId"),
    leaseId: requiredString(body.leaseId, "leaseId"),
    heartbeatToken: requiredString(body.heartbeatToken, "heartbeatToken"),
    heartbeatSeq: boundedInteger(body.heartbeatSeq, -1, 0, Number.MAX_SAFE_INTEGER),
    bridgeStatus: optionalString(body.bridgeStatus),
    requestId: optionalString(body.requestId),
    idempotencyKey: optionalString(body.idempotencyKey),
  };
  if (input.heartbeatSeq < 0) {
    throw new ApiError(400, "missing_required_field", "heartbeatSeq is required.");
  }
  if (!mutationKey(input)) {
    throw new ApiError(400, "missing_required_field", "Mutation routes require requestId or idempotencyKey.");
  }
  return input;
}

export function validateSubmitResultInput(body: JsonObject): SubmitResultInput {
  const result = body.result;
  if (!isPlainObject(result)) {
    throw new ApiError(400, "missing_required_field", "result must be an object.");
  }
  return {
    workspaceId: requiredString(body.workspaceId, "workspaceId"),
    runId: requiredString(body.runId, "runId"),
    taskId: requiredString(body.taskId, "taskId"),
    leaseId: requiredString(body.leaseId, "leaseId"),
    heartbeatToken: requiredString(body.heartbeatToken, "heartbeatToken"),
    attempt: boundedInteger(body.attempt, -1, 1, Number.MAX_SAFE_INTEGER),
    bridgeId: requiredString(body.bridgeId, "bridgeId"),
    machineId: requiredString(body.machineId, "machineId"),
    bridgeInstanceId: requiredString(body.bridgeInstanceId, "bridgeInstanceId"),
    idempotencyKey: requiredString(body.idempotencyKey, "idempotencyKey"),
    resultHash: requiredString(body.resultHash, "resultHash"),
    result: result as JsonObject,
  };
}

export function validateOfflineBridgeInput(bridgeId: string, body: JsonObject): OfflineBridgeInput {
  const input = {
    workspaceId: requiredString(body.workspaceId, "workspaceId"),
    bridgeId,
    machineId: optionalString(body.machineId),
    bridgeInstanceId: optionalString(body.bridgeInstanceId),
    reason: optionalString(body.reason),
    state: body.state === "draining" ? "draining" : "offline",
    revoke: body.revoke === true,
    requestId: optionalString(body.requestId),
    idempotencyKey: optionalString(body.idempotencyKey),
  } satisfies OfflineBridgeInput;
  if (!mutationKey(input)) {
    throw new ApiError(400, "missing_required_field", "Mutation routes require requestId or idempotencyKey.");
  }
  return input;
}

export function parseTargetStage(value: string): TargetStage {
  if ((FEATURE_GATE_STAGES as readonly string[]).includes(value)) {
    return value as TargetStage;
  }
  throw new ApiError(400, "invalid_target_stage", `Unknown targetStage: ${value}`);
}

export function mutationKey(input: { requestId?: string; idempotencyKey?: string }): string {
  return (input.idempotencyKey || input.requestId || "").trim();
}

export async function sha256Hex(value: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

export function stableJson(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableJson(item)).join(",")}]`;
  }
  if (isPlainObject(value)) {
    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${stableJson((value as Record<string, unknown>)[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

export function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function optionalString(value: JsonValue | undefined): string | undefined {
  return typeof value === "string" && value.trim() ? value.trim() : undefined;
}

export function requiredString(value: JsonValue | undefined, field: string): string {
  const result = optionalString(value);
  if (!result) {
    throw new ApiError(400, "missing_required_field", `${field} is required.`);
  }
  return result;
}

export function stringArray(value: JsonValue | undefined, field: string): string[] {
  if (!Array.isArray(value)) {
    throw new ApiError(400, "missing_required_field", `${field} must be an array.`);
  }
  return value.map((item) => String(item).trim()).filter(Boolean);
}

export function boundedInteger(value: unknown, fallback: number, min: number, max: number): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    return fallback;
  }
  return Math.max(min, Math.min(max, Math.trunc(parsed)));
}

function validateCapabilities(value: JsonValue | undefined): CapabilityDescriptor[] {
  if (!Array.isArray(value)) {
    throw new ApiError(400, "missing_required_field", "capabilities must be an array of capability descriptors.");
  }
  return value.map((item, index) => {
    if (!isPlainObject(item)) {
      throw new ApiError(400, "missing_required_field", `capabilities[${index}] must be an object, not a bare string.`);
    }
    const capability = item as JsonObject;
    const supportedStages = stringArray(capability.supportedStages, "supportedStages").map(parseTargetStage);
    const allowedTools = stringArray(capability.allowedTools, "allowedTools");
    const forbiddenActions = stringArray(capability.forbiddenActions, "forbiddenActions");
    assertAllowedTools(allowedTools);
    if (capability.savedCurrentDwg !== false) {
      throw new ApiError(422, "saved_current_dwg_violation", "capability.savedCurrentDwg must be false.");
    }
    return {
      capabilityId: requiredString(capability.capabilityId, "capabilityId"),
      version: requiredString(capability.version, "version"),
      supportedStages,
      allowedTools,
      forbiddenActions,
      maxConcurrentLeases: boundedInteger(capability.maxConcurrentLeases, 1, 1, 25),
      savedCurrentDwg: false,
    };
  });
}

function assertAllowedTools(tools: string[]): void {
  for (const tool of tools) {
    if (FORBIDDEN_WORKER_TOOLS.has(tool)) {
      throw new ApiError(422, "forbidden_tool_requested", `Forbidden Worker tool requested: ${tool}`);
    }
    if (!CANONICAL_ALLOWED_TOOLS.has(tool)) {
      throw new ApiError(422, "forbidden_tool_requested", `Unknown Worker tool requested: ${tool}`);
    }
  }
}

function assertAllowedActions(actions: string[]): void {
  for (const action of actions) {
    if (FORBIDDEN_WORKER_ACTIONS.has(action)) {
      throw new ApiError(422, "forbidden_action_requested", `Forbidden Worker action requested: ${action}`);
    }
  }
}

function dependencyMap(value: JsonValue | undefined): Record<string, string[]> {
  if (!isPlainObject(value)) {
    throw new ApiError(400, "missing_required_field", "dependencies must be an object.");
  }
  const result: Record<string, string[]> = {};
  for (const [key, deps] of Object.entries(value)) {
    result[key] = stringArray(deps as JsonValue, `dependencies.${key}`);
  }
  return result;
}

function optionalBridgeState(value: JsonValue | undefined): "online" | "offline" | "draining" | undefined {
  if (value === undefined || value === null) {
    return undefined;
  }
  if (value === "online" || value === "offline" || value === "draining") {
    return value;
  }
  throw new ApiError(400, "missing_required_field", "state must be online, offline, or draining.");
}
