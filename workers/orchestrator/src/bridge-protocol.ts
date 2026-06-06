import { BRIDGE_REGISTRATION_SCHEMA, DEFAULT_HEARTBEAT_INTERVAL_SECONDS } from "./constants";
import { ApiError } from "./responses";
import { nowIso } from "./state-machine";
import type { AuthContext, BridgeState, CapabilityDescriptor, JsonObject, LeaseIdentity, RegisterBridgeInput, RunState, RunTask } from "./types";

export function createBridgeState(input: RegisterBridgeInput, auth: AuthContext, previous?: BridgeState): BridgeState {
  const now = nowIso();
  if (previous?.revokedAt) {
    throw new ApiError(409, "bridge_revoked", "Revoked bridge cannot register again.");
  }
  return {
    schemaVersion: BRIDGE_REGISTRATION_SCHEMA,
    bridgeId: input.bridgeId,
    machineId: input.machineId,
    bridgeInstanceId: input.bridgeInstanceId,
    workspaceId: input.workspaceId,
    version: input.version,
    protocolVersion: input.protocolVersion,
    state: input.state || "online",
    capabilities: normalizeCapabilities(input.capabilities),
    authSubject: auth.subjectId,
    tokenId: auth.tokenId,
    registeredAt: previous?.registeredAt || now,
    lastSeenAt: now,
    offlineAt: input.state === "offline" ? now : "",
    offlineReason: "",
    revokedAt: previous?.revokedAt || "",
    revokedReason: previous?.revokedReason || "",
  };
}

export function assertBridgeUsable(bridge: BridgeState | null, expected: {
  bridgeId: string;
  machineId: string;
  bridgeInstanceId: string;
  workspaceId: string;
}): asserts bridge is BridgeState {
  if (!bridge) {
    throw new ApiError(409, "bridge_unregistered", "Bridge must register before heartbeat, lease, or submit.");
  }
  assertBridgeIdentity(bridge, expected);
  if (bridge.revokedAt) {
    throw new ApiError(409, "bridge_revoked", "Bridge is revoked.");
  }
  if (bridge.state !== "online") {
    throw new ApiError(409, "bridge_offline", "Bridge is not online.");
  }
}

export function assertBridgeAuthBinding(bridge: BridgeState, auth: AuthContext): void {
  if (bridge.authSubject !== auth.subjectId || bridge.tokenId !== auth.tokenId) {
    throw new ApiError(403, "bridge_identity_mismatch", "Bridge auth subject does not match registration.");
  }
}

export function assertBridgeIdentity(bridge: BridgeState, expected: {
  bridgeId: string;
  machineId?: string;
  bridgeInstanceId?: string;
  workspaceId?: string;
}): void {
  if (bridge.bridgeId !== expected.bridgeId) {
    throw new ApiError(403, "bridge_identity_mismatch", "Bridge id mismatch.");
  }
  if (expected.machineId && bridge.machineId !== expected.machineId) {
    throw new ApiError(403, "bridge_identity_mismatch", "Bridge machine id mismatch.");
  }
  if (expected.bridgeInstanceId && bridge.bridgeInstanceId !== expected.bridgeInstanceId) {
    throw new ApiError(403, "bridge_identity_mismatch", "Bridge instance id mismatch.");
  }
  if (expected.workspaceId && bridge.workspaceId !== expected.workspaceId) {
    throw new ApiError(403, "bridge_identity_mismatch", "Bridge workspace mismatch.");
  }
}

export function issueLease(task: RunTask, bridge: BridgeState): LeaseIdentity {
  const now = nowIso();
  const leaseIdentity = {
    leaseId: crypto.randomUUID(),
    leaseSequence: task.leaseSequence + 1,
    bridgeId: bridge.bridgeId,
    machineId: bridge.machineId,
    bridgeInstanceId: bridge.bridgeInstanceId,
    heartbeatToken: crypto.randomUUID(),
    issuedAt: now,
    leaseExpiresAt: new Date(Date.now() + task.timeoutSeconds * 1000).toISOString().replace(/\.\d{3}Z$/, "Z"),
    heartbeatIntervalSeconds: DEFAULT_HEARTBEAT_INTERVAL_SECONDS,
  };
  task.state = "leased";
  task.leaseId = leaseIdentity.leaseId;
  task.leaseSequence = leaseIdentity.leaseSequence;
  task.leasedBy = bridge.bridgeId;
  task.machineId = bridge.machineId;
  task.bridgeInstanceId = bridge.bridgeInstanceId;
  task.heartbeatToken = leaseIdentity.heartbeatToken;
  task.heartbeatSeq = 0;
  task.heartbeatAt = now;
  task.leaseExpiresAt = leaseIdentity.leaseExpiresAt;
  task.retryAfter = "";
  task.attempt += 1;
  return leaseIdentity;
}

export function leaseResponse(state: RunState, task: RunTask, bridge: BridgeState, lease: LeaseIdentity): JsonObject {
  const matchedCapabilities = bridge.capabilities
    .filter((capability) => capability.supportedStages.includes(state.currentStage))
    .map((capability) => capability.capabilityId);
  return {
    status: "leased",
    leaseId: lease.leaseId,
    leaseSequence: lease.leaseSequence,
    runId: state.runId,
    taskId: task.taskId,
    attempt: task.attempt,
    bridgeId: bridge.bridgeId,
    machineId: bridge.machineId,
    bridgeInstanceId: bridge.bridgeInstanceId,
    issuedAt: lease.issuedAt,
    leaseExpiresAt: lease.leaseExpiresAt,
    heartbeatIntervalSeconds: lease.heartbeatIntervalSeconds,
    heartbeatToken: lease.heartbeatToken,
    requiredCapabilities: task.allowedTools,
    matchedCapabilities,
    constraints: {
      savedCurrentDwg: false,
      workerExecutesShell: false,
      workerSavesCurrentDwg: false,
      forbiddenActions: task.forbiddenActions,
    },
    envelope: task.envelope,
  };
}

function normalizeCapabilities(capabilities: CapabilityDescriptor[]): CapabilityDescriptor[] {
  return capabilities.map((capability) => ({
    ...capability,
    allowedTools: [...capability.allowedTools],
    forbiddenActions: [...capability.forbiddenActions],
    supportedStages: [...capability.supportedStages],
    savedCurrentDwg: false,
  }));
}
