import {
  DEFAULT_CIRCUIT_TARGETS,
  FEATURE_GATE_NEXT_ACTION,
  FEATURE_GATE_ORDER,
  FEATURE_GATE_STAGES,
  FORBIDDEN_WORKER_ACTIONS,
  FORBIDDEN_WORKER_TOOLS,
} from "./constants";
import type { AuditEvent, BridgeState, CapabilityDescriptor, CircuitBreaker, FeatureGate, RunState, RunTask, TargetStage } from "./types";

export function nowIso(): string {
  return new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
}

export function compactTimestamp(): string {
  return new Date().toISOString().replace(/[-:.TZ]/g, "").slice(0, 14);
}

export function slug(value: string): string {
  return value.trim().toLowerCase().replace(/[^a-z0-9_-]+/g, "-").replace(/^-+|-+$/g, "") || "run";
}

export function featureGatesForStage(targetStage: TargetStage): Record<TargetStage, FeatureGate> {
  const targetOrder = FEATURE_GATE_ORDER[targetStage];
  const gates = {} as Record<TargetStage, FeatureGate>;
  for (const stage of FEATURE_GATE_STAGES) {
    const enabled = stage !== "current_dwg_save" && FEATURE_GATE_ORDER[stage] <= targetOrder;
    gates[stage] = {
      enabled,
      enabledBy: enabled ? `target_stage:${targetStage}` : "default_closed",
      nextAction: enabled ? "" : FEATURE_GATE_NEXT_ACTION[stage] || "",
    };
  }
  gates.worker_orchestration_ready.enabled = true;
  gates.current_dwg_save = {
    enabled: false,
    enabledBy: "default_closed",
    nextAction: FEATURE_GATE_NEXT_ACTION.current_dwg_save || "",
  };
  return gates;
}

export function defaultCircuitBreakers(): Record<string, CircuitBreaker> {
  const now = nowIso();
  return Object.fromEntries(
    DEFAULT_CIRCUIT_TARGETS.map((target) => [target, { state: "closed", reason: "", openedAt: "", updatedAt: now }]),
  ) as Record<string, CircuitBreaker>;
}

export function auditEvent(
  eventType: string,
  runId: string,
  summary: string,
  taskId?: string,
  bridgeId?: string,
): AuditEvent {
  return {
    eventId: crypto.randomUUID(),
    eventType,
    runId,
    taskId,
    bridgeId,
    summary,
    createdAt: nowIso(),
  };
}

export function progressRun(state: RunState): void {
  let changed = true;
  while (changed) {
    changed = false;
    for (const task of state.tasks) {
      if (task.state !== "pending" && task.state !== "retry_scheduled") {
        continue;
      }
      const blocked = blockedDependency(state, task);
      if (blocked) {
        blockTask(state, task, `upstream ${blocked} blocked`);
        changed = true;
        continue;
      }
      if (!dependenciesCompleted(state, task)) {
        continue;
      }
      if (hasSecurityBlock(task)) {
        blockTask(state, task, "security_blocked", true);
        changed = true;
      }
    }
  }

  if (state.tasks.some((task) => task.state === "blocked")) {
    state.state = "blocked";
  } else if (state.tasks.length > 0 && state.tasks.every((task) => task.state === "completed")) {
    state.state = "completed";
  } else if (state.tasks.some((task) => task.state === "running")) {
    state.state = "running";
  } else if (state.tasks.some((task) => task.state === "leased")) {
    state.state = "leasing";
  } else if (state.state !== "cancelled" && state.state !== "waiting_for_bridge") {
    state.state = state.tasks.length > 0 ? "queued" : "created";
  }
}

export function nextLeaseableTask(state: RunState, bridge: BridgeState): RunTask | undefined {
  for (const task of state.tasks) {
    if (task.state !== "pending" && task.state !== "retry_scheduled") {
      continue;
    }
    if (task.retryAfter && Date.parse(task.retryAfter) > Date.now()) {
      continue;
    }
    if (!dependenciesCompleted(state, task)) {
      continue;
    }
    if (hasSecurityBlock(task)) {
      blockTask(state, task, "security_blocked", true);
      continue;
    }
    if (!capabilitiesMatchTask(bridge.capabilities, state.currentStage, task)) {
      continue;
    }
    return task;
  }
  return undefined;
}

export function hasPendingCapabilityGap(state: RunState, bridge: BridgeState): boolean {
  return state.tasks.some((task) => {
    if (task.state !== "pending" && task.state !== "retry_scheduled") {
      return false;
    }
    if (task.retryAfter && Date.parse(task.retryAfter) > Date.now()) {
      return false;
    }
    if (!dependenciesCompleted(state, task) || hasSecurityBlock(task)) {
      return false;
    }
    return !capabilitiesMatchTask(bridge.capabilities, state.currentStage, task);
  });
}

export function bridgeLeaseCapacity(capabilities: CapabilityDescriptor[], stage: TargetStage): number {
  return capabilities.reduce((total, capability) => {
    if (!capability.supportedStages.includes(stage)) {
      return total;
    }
    return total + capability.maxConcurrentLeases;
  }, 0);
}

export function capabilitiesMatchTask(capabilities: CapabilityDescriptor[], stage: TargetStage, task: RunTask): boolean {
  const allowed = new Set<string>();
  let leaseCapacity = 0;
  for (const capability of capabilities) {
    if (!capability.supportedStages.includes(stage)) {
      continue;
    }
    leaseCapacity += capability.maxConcurrentLeases;
    for (const tool of capability.allowedTools) {
      allowed.add(tool);
    }
  }
  return leaseCapacity > 0 && task.allowedTools.every((tool) => allowed.has(tool));
}

export function blockTask(state: RunState, task: RunTask, reason: string, security = false): void {
  task.state = "blocked";
  task.blockedReason = reason;
  clearLease(task);
  if (!state.blockedReasons.includes(reason)) {
    state.blockedReasons.push(reason);
  }
  if (security) {
    if (!state.securityBlocks.includes("security_blocked")) {
      state.securityBlocks.push("security_blocked");
    }
    openCircuit(state, "security_gate", reason);
  }
  state.auditEvents.push(auditEvent("task_blocked", state.runId, reason, task.taskId));
}

export function openCircuit(state: RunState, target: string, reason: string): void {
  const now = nowIso();
  state.circuitBreakers[target] = { state: "open", reason, openedAt: now, updatedAt: now };
}

export function clearLease(task: RunTask): void {
  task.leaseId = "";
  task.leasedBy = "";
  task.machineId = "";
  task.bridgeInstanceId = "";
  task.heartbeatToken = "";
  task.heartbeatSeq = 0;
  task.leaseExpiresAt = "";
  task.heartbeatAt = "";
}

export function dependenciesCompleted(state: RunState, task: RunTask): boolean {
  const tasks = new Map(state.tasks.map((item) => [item.taskId, item]));
  return task.dependsOn.every((dependencyId) => tasks.get(dependencyId)?.state === "completed");
}

export function hasSecurityBlock(task: RunTask): boolean {
  const allowedTools = new Set(task.allowedTools);
  const envelopeTools = new Set(task.envelope.allowedTools);
  const requestedActions = new Set(task.requestedActions);
  return (
    intersects(allowedTools, FORBIDDEN_WORKER_TOOLS) ||
    intersects(envelopeTools, FORBIDDEN_WORKER_TOOLS) ||
    intersects(requestedActions, FORBIDDEN_WORKER_ACTIONS)
  );
}

function blockedDependency(state: RunState, task: RunTask): string {
  const tasks = new Map(state.tasks.map((item) => [item.taskId, item]));
  return task.dependsOn.find((dependencyId) => tasks.get(dependencyId)?.state === "blocked") || "";
}

function intersects(left: Set<string>, right: Set<string>): boolean {
  for (const item of left) {
    if (right.has(item)) {
      return true;
    }
  }
  return false;
}
