import type {
  AGENT_OUTPUT_SCHEMA,
  BRIDGE_REGISTRATION_SCHEMA,
  DEFAULT_CIRCUIT_TARGETS,
  FEATURE_GATE_STAGES,
  TASK_ENVELOPE_SCHEMA,
  WORKER_RUN_STATE_SCHEMA,
} from "./constants";

export type JsonValue = string | number | boolean | null | JsonValue[] | { [key: string]: JsonValue };
export type JsonObject = { [key: string]: JsonValue };

export type TargetStage = (typeof FEATURE_GATE_STAGES)[number];
export type CircuitTarget = (typeof DEFAULT_CIRCUIT_TARGETS)[number];

export type RunLifecycleState =
  | "created"
  | "queued"
  | "leasing"
  | "running"
  | "waiting_for_bridge"
  | "completed"
  | "failed"
  | "blocked"
  | "cancelled";

export type TaskLifecycleState =
  | "pending"
  | "retry_scheduled"
  | "leased"
  | "running"
  | "completed"
  | "failed"
  | "blocked"
  | "cancelled";

export type BridgeLifecycleState = "online" | "offline" | "draining";
export type AuthRole = "anonymous" | "user" | "bridge" | "admin";

export type FeatureGate = {
  enabled: boolean;
  enabledBy: string;
  nextAction: string;
};

export type CircuitBreaker = {
  state: "closed" | "open" | "half_open";
  reason: string;
  openedAt: string;
  updatedAt: string;
};

export type AuditEvent = {
  eventId: string;
  eventType: string;
  runId: string;
  taskId?: string;
  bridgeId?: string;
  summary: string;
  details?: JsonObject;
  createdAt: string;
};

export type CapabilityDescriptor = {
  capabilityId: string;
  version: string;
  supportedStages: TargetStage[];
  allowedTools: string[];
  forbiddenActions: string[];
  maxConcurrentLeases: number;
  savedCurrentDwg: false;
};

export type TaskEnvelope = {
  schemaVersion: typeof TASK_ENVELOPE_SCHEMA;
  runId: string;
  taskId: string;
  workspaceId: string;
  requestedBy: string;
  stage: TargetStage;
  agentId: string;
  promptPackId: string;
  inputRefs: string[];
  allowedTools: string[];
  forbiddenActions: string[];
  outputSchema: string;
  timeoutSeconds: number;
  idempotencyKey: string;
  constraints: {
    savedCurrentDwg: false;
    workerExecutesShell: false;
    workerSavesCurrentDwg: false;
    forbiddenActions: string[];
  };
  savedCurrentDwg: false;
};

export type LeaseIdentity = {
  leaseId: string;
  leaseSequence: number;
  bridgeId: string;
  machineId: string;
  bridgeInstanceId: string;
  heartbeatToken: string;
  issuedAt: string;
  leaseExpiresAt: string;
  heartbeatIntervalSeconds: number;
};

export type RunTask = {
  taskId: string;
  agentId: string;
  state: TaskLifecycleState;
  dependsOn: string[];
  attempt: number;
  retryCount: number;
  maxAttempts: number;
  timeoutSeconds: number;
  retryAfter: string;
  leaseId: string;
  leaseSequence: number;
  leasedBy: string;
  machineId: string;
  bridgeInstanceId: string;
  heartbeatToken: string;
  heartbeatSeq: number;
  leaseExpiresAt: string;
  heartbeatAt: string;
  blockedReason: string;
  allowedTools: string[];
  forbiddenActions: string[];
  requestedActions: string[];
  envelope: TaskEnvelope;
  result?: AgentOutput;
  resultHash?: string;
  resultIdempotencyKey?: string;
  completedAt?: string;
};

export type RunState = {
  schemaVersion: typeof WORKER_RUN_STATE_SCHEMA;
  runId: string;
  workspaceId: string;
  requestedBy: string;
  authSubject: string;
  state: RunLifecycleState;
  currentStage: TargetStage;
  completionClaim: TargetStage;
  featureGates: Record<TargetStage, FeatureGate>;
  requestSummary: string;
  tasks: RunTask[];
  modelInvoked: boolean;
  modelUnavailable: boolean;
  schemaValid: boolean;
  cadGeometryVerified: boolean;
  savedCurrentDwg: false;
  retryCount: number;
  timeoutCount: number;
  dlqCount: number;
  legacyStateReadCount: number;
  securityBlocks: string[];
  blockedReasons: string[];
  acceptedIdempotencyKeys: string[];
  circuitBreakers: Record<string, CircuitBreaker>;
  auditEvents: AuditEvent[];
  createdAt: string;
  updatedAt: string;
};

export type AgentOutput = {
  schemaVersion: typeof AGENT_OUTPUT_SCHEMA | string;
  runId: string;
  taskId: string;
  agentId: string;
  status: "completed" | "blocked" | "failed" | string;
  decision: string;
  summary: string;
  modelInvoked: boolean;
  modelUnavailable: boolean;
  schemaValid: boolean;
  traceRef: string;
  evidenceRefs: string[];
  blockedReason: string;
  savedCurrentDwg: false;
};

export type BridgeState = {
  schemaVersion: typeof BRIDGE_REGISTRATION_SCHEMA;
  bridgeId: string;
  machineId: string;
  bridgeInstanceId: string;
  workspaceId: string;
  version: string;
  protocolVersion: string;
  state: BridgeLifecycleState;
  capabilities: CapabilityDescriptor[];
  authSubject: string;
  tokenId: string;
  registeredAt: string;
  lastSeenAt: string;
  offlineAt: string;
  offlineReason: string;
  revokedAt: string;
  revokedReason: string;
};

export type TaskSpec = {
  taskId?: string;
  agentId?: string;
  promptPackId?: string;
  dependsOn?: string[];
  inputRefs?: string[];
  allowedTools?: string[];
  forbiddenActions?: string[];
  requestedActions?: string[];
  outputSchema?: string;
  timeoutSeconds?: number;
  maxAttempts?: number;
  idempotencyKey?: string;
};

export type CreateRunInput = {
  requestSummary?: string;
  workspaceId?: string;
  targetStage?: string;
  requestedBy?: string;
  agentIds?: string[];
  dependencies?: Record<string, string[]>;
  taskSpecs?: TaskSpec[];
  requestId?: string;
  idempotencyKey?: string;
};

export type RegisterBridgeInput = {
  schemaVersion?: string;
  bridgeId: string;
  machineId: string;
  bridgeInstanceId: string;
  workspaceId: string;
  version: string;
  protocolVersion: string;
  capabilities: CapabilityDescriptor[];
  state?: BridgeLifecycleState;
  requestId?: string;
  idempotencyKey?: string;
};

export type LeaseTaskInput = {
  runId: string;
  workspaceId: string;
  bridgeId: string;
  machineId: string;
  bridgeInstanceId: string;
  requestId?: string;
  idempotencyKey?: string;
};

export type HeartbeatInput = {
  workspaceId: string;
  bridgeId: string;
  machineId: string;
  bridgeInstanceId: string;
  runId: string;
  taskId: string;
  leaseId: string;
  heartbeatToken: string;
  heartbeatSeq: number;
  bridgeStatus?: string;
  requestId?: string;
  idempotencyKey?: string;
};

export type SubmitResultInput = {
  workspaceId: string;
  runId: string;
  taskId: string;
  leaseId: string;
  heartbeatToken: string;
  attempt: number;
  bridgeId: string;
  machineId: string;
  bridgeInstanceId: string;
  idempotencyKey: string;
  resultHash: string;
  result: JsonObject;
};

export type OfflineBridgeInput = {
  workspaceId: string;
  bridgeId: string;
  machineId?: string;
  bridgeInstanceId?: string;
  reason?: string;
  state?: "offline" | "draining";
  revoke?: boolean;
  requestId?: string;
  idempotencyKey?: string;
};

export type AuthContext = {
  role: AuthRole;
  subjectId: string;
  tokenId: string;
  allowedTenantIds: string[];
  allowedWorkspaceIds: string[];
  allowedBridgeIds: string[];
};

export type MutationMeta = {
  route: string;
  method: string;
  authSubject: string;
  workspaceId: string;
  runId?: string;
  taskId?: string;
  bridgeId?: string;
  leaseId?: string;
  attempt?: number;
  idempotencyKey: string;
  bodyHash: string;
};

export type IdempotencyRow = {
  idempotency_id: string;
  body_hash: string;
  response_json: string;
};

export type RunRow = {
  run_id: string;
  schema_version: string;
  state: RunLifecycleState;
  current_stage: TargetStage;
  completion_claim: TargetStage;
  state_json: string;
  legacy_state_read_count?: number;
};

export type BridgeRow = {
  bridge_id: string;
  state: BridgeLifecycleState;
  state_json: string;
};

export type CountRow = {
  count: number;
};

export type AlarmDueRow = {
  run_id: string;
  task_id: string;
  lease_id: string;
  lease_expires_at: string;
  retry_after: string;
};

export type Diagnostics = {
  status: "ok" | "degraded";
  environment: string;
  orchestratorVersion: string;
  compatibilityDate: string;
  compatibilityFlags: string[];
  schemaVersion: string;
  migrationStatus: string;
  alarmStatus: JsonObject;
  backlog: JsonObject;
  runCounts: Record<string, number>;
  taskCounts: Record<string, number>;
  bridgeCounts: Record<string, number>;
  timeoutCount: number;
  blockedReasonSummary: Record<string, number>;
  circuitBreakers: Record<string, CircuitBreaker>;
  recentErrors: JsonObject[];
};
