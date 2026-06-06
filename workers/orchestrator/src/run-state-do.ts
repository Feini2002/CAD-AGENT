import { DurableObject } from "cloudflare:workers";
import {
  AGENT_OUTPUT_SCHEMA,
  DEFAULT_BACKPRESSURE_LIMITS,
  DEFAULT_FORBIDDEN_ACTIONS,
  DEFAULT_MAX_ATTEMPTS,
  DEFAULT_TASK_TIMEOUT_SECONDS,
  FORBIDDEN_WORKER_ACTIONS,
  FORBIDDEN_WORKER_TOOLS,
  LEGACY_WORKER_RUN_STATE_SCHEMA,
  MAX_AUDIT_EVENTS_IN_RUN_STATE,
  STALE_BRIDGE_SECONDS,
  TASK_ENVELOPE_SCHEMA,
  WORKER_RUN_STATE_SCHEMA,
} from "./constants";
import { assertBridgeAuthBinding, assertBridgeIdentity, assertBridgeUsable, createBridgeState, issueLease, leaseResponse } from "./bridge-protocol";
import { ApiError } from "./responses";
import { redactForLog } from "./redaction";
import {
  auditEvent,
  blockTask,
  bridgeLeaseCapacity,
  clearLease,
  compactTimestamp,
  defaultCircuitBreakers,
  featureGatesForStage,
  hasPendingCapabilityGap,
  nextLeaseableTask,
  nowIso,
  openCircuit,
  progressRun,
  slug,
} from "./state-machine";
import type {
  AgentOutput,
  AlarmDueRow,
  AuthContext,
  BridgeRow,
  BridgeState,
  CountRow,
  CreateRunInput,
  Diagnostics,
  HeartbeatInput,
  IdempotencyRow,
  JsonObject,
  LeaseTaskInput,
  MutationMeta,
  OfflineBridgeInput,
  RegisterBridgeInput,
  RunRow,
  RunState,
  RunTask,
  SubmitResultInput,
  TaskSpec,
  TargetStage,
} from "./types";
import { boundedInteger, mutationKey, parseTargetStage, sha256Hex, stableJson } from "./validation";

type MigrationStatus = "ok" | "failed";

export class RunStateDurableObject extends DurableObject<Env> {
  private migrationStatus: MigrationStatus = "ok";
  private migrationError = "";

  constructor(ctx: DurableObjectState, env: Env) {
    super(ctx, env);
    ctx.blockConcurrencyWhile(async () => {
      try {
        this.applyMigrations();
      } catch (error) {
        this.migrationStatus = "failed";
        this.migrationError = error instanceof Error ? error.message : String(error);
      }
    });
  }

  async alarm(): Promise<void> {
    try {
      await this.processDueWork("alarm");
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      this.recordSystemAudit("alarm_failed", "alarm", message);
      try {
        this.openGlobalCircuit("worker_queue", "alarm_failed");
      } catch (circuitError) {
        this.recordSystemAudit("alarm_failed", "alarm_circuit", circuitError instanceof Error ? circuitError.message : String(circuitError));
      }
      try {
        await this.scheduleNextAlarm();
      } catch (rescheduleError) {
        this.recordSystemAudit(
          "alarm_failed",
          "alarm_reschedule",
          rescheduleError instanceof Error ? rescheduleError.message : String(rescheduleError),
        );
      }
    }
  }

  async health(): Promise<JsonObject> {
    return {
      status: this.migrationStatus === "ok" ? "ok" : "degraded",
      schemaVersion: WORKER_RUN_STATE_SCHEMA,
      migrationStatus: this.migrationStatus,
      migrationError: this.migrationStatus === "ok" ? "" : this.migrationError,
      now: nowIso(),
    };
  }

  async createRun(input: CreateRunInput, auth: AuthContext, meta: MutationMeta): Promise<JsonObject> {
    this.assertWritable();
    return this.withIdempotency(meta, async () => {
      await this.checkMutationRateLimit(meta);
      const targetStage = parseTargetStage(input.targetStage || "worker_orchestration_ready");
      const workspaceId = slug(input.workspaceId || this.env.DEFAULT_WORKSPACE_ID || "cad-agent-core-lab");
      const requestedBy = input.requestedBy || auth.subjectId;
      const agentIds = input.agentIds && input.agentIds.length > 0 ? input.agentIds.map(String) : ["pipeline_orchestrator"];
      const runId = `run_${compactTimestamp()}_${slug(targetStage)}_${crypto.randomUUID().replace(/-/g, "").slice(0, 8)}`;
      const tasks = buildTasks({
        runId,
        workspaceId,
        requestedBy,
        targetStage,
        agentIds,
        dependencies: input.dependencies || {},
        taskSpecs: input.taskSpecs,
      });
      const projected = await this.backlogCounts();
      const limits = this.backpressureLimits();
      if (
        projected.pending + tasks.length > limits.pending ||
        projected.retryScheduled >= limits.retryScheduled ||
        projected.dlq >= limits.dlq
      ) {
        await this.openQueueCircuit("backpressure_active");
        throw new ApiError(429, "backpressure_active", "Pending task threshold exceeded.");
      }

      const now = nowIso();
      const state: RunState = {
        schemaVersion: WORKER_RUN_STATE_SCHEMA,
        runId,
        workspaceId,
        requestedBy,
        authSubject: auth.subjectId,
        state: tasks.length > 0 ? "queued" : "created",
        currentStage: targetStage,
        completionClaim: targetStage,
        featureGates: featureGatesForStage(targetStage),
        requestSummary: input.requestSummary || "",
        tasks,
        modelInvoked: false,
        modelUnavailable: false,
        schemaValid: false,
        cadGeometryVerified: false,
        savedCurrentDwg: false,
        retryCount: 0,
        timeoutCount: 0,
        dlqCount: 0,
        legacyStateReadCount: 0,
        securityBlocks: [],
        blockedReasons: [],
        acceptedIdempotencyKeys: [],
        circuitBreakers: defaultCircuitBreakers(),
        auditEvents: [auditEvent("run_created", runId, `created ${tasks.length} worker task(s)`)],
        createdAt: now,
        updatedAt: now,
      };
      progressRun(state);
      this.saveRun(state);
      await this.scheduleNextAlarm();
      return state as unknown as JsonObject;
    });
  }

  async listRuns(limit = 50): Promise<JsonObject[]> {
    const boundedLimit = boundedInteger(limit, 50, 1, 100);
    const rows = this.ctx.storage.sql
      .exec<RunRow>(
        "SELECT run_id, schema_version, state, current_stage, completion_claim, state_json FROM runs ORDER BY updated_at DESC LIMIT ?",
        boundedLimit,
      )
      .toArray();
    return rows.map((row) => summarizeRun(this.deserializeRun(row)));
  }

  async getRun(runId: string): Promise<RunState | null> {
    await this.processDueWork("read");
    const state = this.loadRun(runId);
    if (!state) {
      return null;
    }
    return trimRunAudit(state);
  }

  async registerBridge(input: RegisterBridgeInput, auth: AuthContext, meta: MutationMeta): Promise<JsonObject> {
    this.assertWritable();
    const previousBeforeReplay = this.loadBridge(input.bridgeId);
    if (previousBeforeReplay?.revokedAt) {
      throw new ApiError(409, "bridge_revoked", "Revoked bridge cannot register again.");
    }
    return this.withIdempotency(meta, async () => {
      await this.checkMutationRateLimit(meta);
      const previous = this.loadBridge(input.bridgeId);
      const bridge = createBridgeState(input, auth, previous || undefined);
      this.saveBridge(bridge);
      return { status: "registered", bridge: redactBridge(bridge) };
    });
  }

  async listBridges(): Promise<JsonObject[]> {
    const rows = this.ctx.storage.sql.exec<BridgeRow>("SELECT bridge_id, state, state_json FROM bridges ORDER BY bridge_id").toArray();
    return rows.map((row) => redactBridge(JSON.parse(row.state_json) as BridgeState));
  }

  async getBridge(bridgeId: string): Promise<JsonObject | null> {
    const bridge = this.loadBridge(bridgeId);
    return bridge ? redactBridge(bridge) : null;
  }

  async markBridgeOffline(input: OfflineBridgeInput, auth: AuthContext, meta: MutationMeta): Promise<JsonObject> {
    this.assertWritable();
    return this.withIdempotency(meta, async () => {
      await this.checkMutationRateLimit(meta);
      const bridge = this.loadBridge(input.bridgeId);
      if (!bridge) {
        throw new ApiError(404, "bridge_not_found", "Bridge was not found.");
      }
      if (auth.role === "bridge") {
        assertBridgeIdentity(bridge, input);
        assertBridgeAuthBinding(bridge, auth);
      }
      const now = nowIso();
      bridge.state = input.state || "offline";
      bridge.offlineAt = now;
      bridge.offlineReason = input.reason || "marked_offline";
      bridge.lastSeenAt = now;
      if (input.revoke) {
        bridge.revokedAt = now;
        bridge.revokedReason = input.reason || "revoked";
      }
      this.saveBridge(bridge);
      this.markActiveLeasesForBridgeUnavailable(bridge.bridgeId, input.reason || bridge.offlineReason);
      await this.scheduleNextAlarm();
      return { status: input.revoke ? "revoked" : "offline", bridge: redactBridge(bridge) };
    });
  }

  async leaseTask(input: LeaseTaskInput, auth: AuthContext, meta: MutationMeta): Promise<JsonObject> {
    this.assertWritable();
    this.assertBridgeNotRevokedForReplay(input.bridgeId);
    return this.withIdempotency(meta, async () => {
      await this.processDueWork("lease");
      await this.checkMutationRateLimit(meta);
      if ((this.env.BRIDGE_LEASING_DISABLED || "").toLowerCase() === "true") {
        throw new ApiError(429, "backpressure_active", "Bridge leasing is disabled by kill switch.");
      }
      const backlog = await this.backlogCounts();
      const limits = this.backpressureLimits();
      if (backlog.running >= limits.running || backlog.retryScheduled >= limits.retryScheduled || backlog.dlq >= limits.dlq) {
        await this.openQueueCircuit("backpressure_active");
        throw new ApiError(429, "backpressure_active", "Worker queue is under backpressure.");
      }
      const state = this.loadRun(input.runId);
      if (!state) {
        throw new ApiError(404, "run_not_found", "Run was not found in this workspace.");
      }
      const bridge = this.loadBridge(input.bridgeId);
      if (!bridge) {
        throw new ApiError(409, "bridge_unregistered", "Bridge must register before heartbeat, lease, or submit.", {
          bridgeId: input.bridgeId,
          knownBridgeIds: this.knownBridgeIds(),
        });
      }
      assertBridgeUsable(bridge, input);
      assertBridgeAuthBinding(bridge, auth);
      if (bridge.workspaceId !== state.workspaceId) {
        throw new ApiError(403, "bridge_identity_mismatch", "Bridge workspace does not match run workspace.");
      }
      const capacity = bridgeLeaseCapacity(bridge.capabilities, state.currentStage);
      if (capacity > 0 && this.countActiveLeasesForBridge(bridge.bridgeId) >= capacity) {
        return { status: "no_capacity", runId: state.runId, bridgeId: bridge.bridgeId, capacity };
      }
      const task = nextLeaseableTask(state, bridge);
      if (!task) {
        if (hasPendingCapabilityGap(state, bridge)) {
          this.markWaitingForBridge(state, bridge.bridgeId, "capability_mismatch");
          throw new ApiError(409, "capability_mismatch", "Bridge capabilities do not match pending tasks.");
        }
        this.saveRun(state);
        return { status: "no_task", runId: state.runId };
      }
      const lease = issueLease(task, bridge);
      state.state = "leasing";
      state.auditEvents.push(auditEvent("task_leased", state.runId, bridge.bridgeId, task.taskId, bridge.bridgeId));
      this.touch(state);
      this.saveRun(state);
      await this.scheduleNextAlarm();
      return leaseResponse(state, task, bridge, lease);
    });
  }

  async heartbeatBridge(input: HeartbeatInput, auth: AuthContext, meta: MutationMeta): Promise<JsonObject> {
    this.assertWritable();
    this.assertBridgeNotRevokedForReplay(input.bridgeId);
    return this.withIdempotency(meta, async () => {
      await this.checkMutationRateLimit(meta);
      const bridge = this.loadBridge(input.bridgeId);
      assertBridgeUsable(bridge, input);
      assertBridgeAuthBinding(bridge, auth);
      const state = this.loadRun(input.runId);
      if (!state) {
        throw new ApiError(404, "run_not_found", "Run was not found in this workspace.");
      }
      const task = findTask(state, input.taskId);
      assertLeaseIdentity(task, input);
      if (input.heartbeatSeq < task.heartbeatSeq) {
        throw new ApiError(409, "heartbeat_out_of_order", "Heartbeat sequence moved backwards.");
      }
      const now = nowIso();
      bridge.lastSeenAt = now;
      this.saveBridge(bridge);
      if (input.heartbeatSeq === task.heartbeatSeq) {
        const response: JsonObject = {
          status: "accepted",
          duplicate: true,
          runId: state.runId,
          taskId: task.taskId,
          heartbeatSeq: task.heartbeatSeq,
        };
        return response;
      }
      task.state = "running";
      task.heartbeatSeq = input.heartbeatSeq;
      task.heartbeatAt = now;
      state.state = "running";
      state.auditEvents.push(auditEvent("task_heartbeat", state.runId, input.bridgeStatus || "heartbeat", task.taskId, bridge.bridgeId));
      this.touch(state);
      this.saveRun(state);
      await this.scheduleNextAlarm();
      const response: JsonObject = {
        status: "accepted",
        runId: state.runId,
        taskId: task.taskId,
        taskState: task.state,
        heartbeatSeq: task.heartbeatSeq,
      };
      return response;
    });
  }

  async submitResult(input: SubmitResultInput, auth: AuthContext, meta: MutationMeta): Promise<JsonObject> {
    this.assertWritable();
    this.assertBridgeNotRevokedForReplay(input.bridgeId);
    return this.withIdempotency(meta, async () => {
      await this.checkMutationRateLimit(meta);
      if ((this.env.SUBMIT_DISABLED || "").toLowerCase() === "true") {
        throw new ApiError(429, "backpressure_active", "Submit is disabled by kill switch.");
      }
      const computedHash = await sha256Hex(stableJson(input.result));
      if (computedHash !== input.resultHash) {
        throw new ApiError(422, "replay_violation", "resultHash does not match result payload.");
      }
      const bridge = this.loadBridge(input.bridgeId);
      assertBridgeUsable(bridge, input);
      assertBridgeAuthBinding(bridge, auth);
      const state = this.loadRun(input.runId);
      if (!state) {
        throw new ApiError(404, "run_not_found", "Run was not found in this workspace.");
      }
      const task = findTask(state, input.taskId);
      assertLeaseIdentity(task, input);
      if (task.attempt !== input.attempt) {
        throw new ApiError(409, "lease_mismatch", "Submit attempt does not match active lease attempt.");
      }
      if (Date.parse(task.leaseExpiresAt) <= Date.now()) {
        throw new ApiError(410, "lease_expired", "Lease has expired.");
      }
      const dangerousResultReason = findDangerousResultReason(input.result);
      if (dangerousResultReason) {
        blockTask(state, task, dangerousResultReason, true);
        state.auditEvents.push(auditEvent("security_violation", state.runId, dangerousResultReason, task.taskId, bridge.bridgeId));
        progressRun(state);
        this.touch(state);
        this.saveRun(state);
        this.openGlobalCircuit("security_gate", dangerousResultReason);
        await this.scheduleNextAlarm();
        throw new ApiError(422, dangerousResultReason, "Worker-side result violates the non-execution boundary.");
      }
      const output = normalizeOutput(state, task, input.result);
      if (output.savedCurrentDwg !== false) {
        throw new ApiError(422, "saved_current_dwg_violation", "Worker-side result cannot save current DWG.");
      }

      state.acceptedIdempotencyKeys.push(input.idempotencyKey);
      task.result = output;
      task.resultHash = input.resultHash;
      task.resultIdempotencyKey = input.idempotencyKey;
      clearLease(task);
      if (output.schemaValid !== true) {
        task.state = "blocked";
        task.blockedReason = "schema_validation_failed";
        openCircuit(state, "codex_cli_model_review", "schema_validation_failed");
      } else if (output.status === "blocked" || output.status === "failed") {
        task.state = "blocked";
        task.blockedReason = output.blockedReason || output.status;
      } else {
        task.state = "completed";
        task.completedAt = nowIso();
      }

      state.modelInvoked = state.modelInvoked || output.modelInvoked;
      state.modelUnavailable = state.modelUnavailable || output.modelUnavailable;
      state.schemaValid = output.schemaValid;
      state.auditEvents.push(auditEvent("task_result_accepted", state.runId, output.summary || output.status, task.taskId, bridge.bridgeId));
      progressRun(state);
      this.touch(state);
      this.saveRun(state);
      await this.scheduleNextAlarm();
      return { status: "accepted", runId: state.runId, taskId: task.taskId, runState: trimRunAudit(state) as unknown as JsonObject };
    });
  }

  async diagnostics(): Promise<Diagnostics> {
    const backlog = await this.backlogCounts();
    const alarm = await this.ctx.storage.getAlarm();
    return {
      status: this.migrationStatus === "ok" ? "ok" : "degraded",
      environment: this.env.ENVIRONMENT || "local",
      orchestratorVersion: this.env.ORCHESTRATOR_VERSION || "mvp-0.1.0",
      compatibilityDate: this.env.COMPATIBILITY_DATE || "2026-05-01",
      compatibilityFlags: (this.env.COMPATIBILITY_FLAGS || "nodejs_compat").split(",").filter(Boolean),
      schemaVersion: WORKER_RUN_STATE_SCHEMA,
      migrationStatus: this.migrationStatus,
      alarmStatus: { scheduledAt: alarm || null },
      backlog: backlog as unknown as JsonObject,
      runCounts: this.countByState("runs", "state"),
      taskCounts: this.countByState("tasks", "state"),
      bridgeCounts: this.countByState("bridges", "state"),
      timeoutCount: this.sumColumn("runs", "timeout_count"),
      blockedReasonSummary: this.blockedReasonSummary(),
      circuitBreakers: this.loadCircuitBreakers(),
      recentErrors: this.recentErrors(),
    };
  }

  async recordAuthFailure(input: { route: string; clientKey: string; code: string }): Promise<JsonObject> {
    const windowMs = 60_000;
    const now = Date.now();
    const limit = boundedInteger(this.env.MUTATION_RATE_LIMIT_PER_MINUTE, 120, 10, 10_000);
    const key = `auth_failure:${input.clientKey}:${input.route}:${Math.floor(now / windowMs)}`;
    const rows = this.ctx.storage.sql
      .exec<{ count: number; reset_at: number }>("SELECT count, reset_at FROM rate_limit_counters WHERE counter_key = ?", key)
      .toArray();
    const count = rows.length === 0 || rows[0].reset_at <= now ? 1 : rows[0].count + 1;
    this.ctx.storage.sql.exec(
      "INSERT OR REPLACE INTO rate_limit_counters (counter_key, count, reset_at) VALUES (?, ?, ?)",
      key,
      count,
      rows.length === 0 || rows[0].reset_at <= now ? now + windowMs : rows[0].reset_at,
    );
    if (count > limit) {
      this.openGlobalCircuit("security_gate", "auth_failure_rate_limited");
      this.recordSystemAudit("security_violation", "auth_failure_rate_limited", `${input.route}:${input.code}`);
      return { status: "rate_limited", count };
    }
    return { status: "recorded", count };
  }

  async __debugInsertLegacyRun(runId: string): Promise<JsonObject> {
    const now = nowIso();
    const legacy = {
      schemaVersion: LEGACY_WORKER_RUN_STATE_SCHEMA,
      runId,
      workspaceId: "cad-agent-core-lab",
      requestedBy: "debug",
      state: "created",
      currentStage: "worker_orchestration_ready",
      completionClaim: "worker_orchestration_ready",
      featureGates: featureGatesForStage("worker_orchestration_ready"),
      requestSummary: "legacy debug",
      tasks: [],
      modelInvoked: false,
      modelUnavailable: false,
      schemaValid: false,
      cadGeometryVerified: false,
      savedCurrentDwg: false,
      retryCount: 0,
      timeoutCount: 0,
      dlqCount: 0,
      securityBlocks: [],
      blockedReasons: [],
      acceptedIdempotencyKeys: [],
      circuitBreakers: defaultCircuitBreakers(),
      auditEvents: [],
      createdAt: now,
      updatedAt: now,
    };
    this.ctx.storage.sql.exec(
      "INSERT OR REPLACE INTO runs (run_id, workspace_id, schema_version, state, current_stage, completion_claim, state_json, created_at, updated_at, timeout_count, dlq_count, legacy_state_read_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
      runId,
      "cad-agent-core-lab",
      LEGACY_WORKER_RUN_STATE_SCHEMA,
      "created",
      "worker_orchestration_ready",
      "worker_orchestration_ready",
      JSON.stringify(legacy),
      now,
      now,
      0,
      0,
      0,
    );
    return { status: "inserted", runId };
  }

  async __debugSetBridgeLastSeenAt(bridgeId: string, lastSeenAt: string): Promise<JsonObject> {
    const bridge = this.loadBridge(bridgeId);
    if (!bridge) {
      throw new ApiError(404, "bridge_not_found", "Bridge was not found.");
    }
    bridge.lastSeenAt = lastSeenAt;
    this.saveBridge(bridge);
    await this.scheduleNextAlarm();
    return { status: "updated", bridgeId, lastSeenAt };
  }

  private applyMigrations(): void {
    const sql = this.ctx.storage.sql;
    sql.exec(`
      CREATE TABLE IF NOT EXISTS _sql_schema_migrations (
        version INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        applied_at TEXT NOT NULL
      )
    `);
    sql.exec(`
      CREATE TABLE IF NOT EXISTS runs (
        run_id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        schema_version TEXT NOT NULL DEFAULT 'worker_run_state/v1',
        state TEXT NOT NULL,
        current_stage TEXT NOT NULL,
        completion_claim TEXT NOT NULL,
        state_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        timeout_count INTEGER NOT NULL DEFAULT 0,
        dlq_count INTEGER NOT NULL DEFAULT 0,
        legacy_state_read_count INTEGER NOT NULL DEFAULT 0
      )
    `);
    this.ensureColumn("runs", "schema_version", "TEXT NOT NULL DEFAULT 'worker_run_state/v1'");
    this.ensureColumn("runs", "state", "TEXT NOT NULL DEFAULT 'created'");
    this.ensureColumn("runs", "current_stage", "TEXT NOT NULL DEFAULT 'worker_orchestration_ready'");
    this.ensureColumn("runs", "completion_claim", "TEXT NOT NULL DEFAULT 'worker_orchestration_ready'");
    this.ensureColumn("runs", "timeout_count", "INTEGER NOT NULL DEFAULT 0");
    this.ensureColumn("runs", "dlq_count", "INTEGER NOT NULL DEFAULT 0");
    this.ensureColumn("runs", "legacy_state_read_count", "INTEGER NOT NULL DEFAULT 0");
    sql.exec("CREATE INDEX IF NOT EXISTS runs_updated_at_idx ON runs (updated_at DESC)");
    sql.exec("CREATE INDEX IF NOT EXISTS runs_state_idx ON runs (state)");
    sql.exec(`
      CREATE TABLE IF NOT EXISTS tasks (
        run_id TEXT NOT NULL,
        task_id TEXT NOT NULL,
        workspace_id TEXT NOT NULL,
        state TEXT NOT NULL,
        attempt INTEGER NOT NULL,
        lease_id TEXT NOT NULL,
        bridge_id TEXT NOT NULL,
        lease_expires_at TEXT NOT NULL,
        retry_after TEXT NOT NULL,
        state_json TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        PRIMARY KEY (run_id, task_id)
      )
    `);
    sql.exec("CREATE INDEX IF NOT EXISTS tasks_state_idx ON tasks (workspace_id, state)");
    sql.exec(`
      CREATE TABLE IF NOT EXISTS bridges (
        bridge_id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        state TEXT NOT NULL,
        machine_id TEXT NOT NULL,
        bridge_instance_id TEXT NOT NULL,
        auth_subject TEXT NOT NULL,
        token_id TEXT NOT NULL,
        revoked_at TEXT NOT NULL,
        last_seen_at TEXT NOT NULL,
        state_json TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )
    `);
    this.ensureColumn("bridges", "workspace_id", "TEXT NOT NULL DEFAULT 'cad-agent-core-lab'");
    this.ensureColumn("bridges", "state", "TEXT NOT NULL DEFAULT 'online'");
    this.ensureColumn("bridges", "machine_id", "TEXT NOT NULL DEFAULT ''");
    this.ensureColumn("bridges", "bridge_instance_id", "TEXT NOT NULL DEFAULT ''");
    this.ensureColumn("bridges", "auth_subject", "TEXT NOT NULL DEFAULT ''");
    this.ensureColumn("bridges", "token_id", "TEXT NOT NULL DEFAULT ''");
    this.ensureColumn("bridges", "revoked_at", "TEXT NOT NULL DEFAULT ''");
    this.ensureColumn("bridges", "last_seen_at", "TEXT NOT NULL DEFAULT ''");
    sql.exec("CREATE INDEX IF NOT EXISTS bridges_workspace_state_idx ON bridges (workspace_id, state)");
    sql.exec(`
      CREATE TABLE IF NOT EXISTS audit_events (
        event_id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL,
        task_id TEXT NOT NULL,
        bridge_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        summary TEXT NOT NULL,
        safe_json TEXT NOT NULL,
        created_at TEXT NOT NULL
      )
    `);
    sql.exec("CREATE INDEX IF NOT EXISTS audit_events_run_idx ON audit_events (run_id, created_at DESC)");
    sql.exec(`
      CREATE TABLE IF NOT EXISTS idempotency_keys (
        idempotency_id TEXT PRIMARY KEY,
        route TEXT NOT NULL,
        method TEXT NOT NULL,
        auth_subject TEXT NOT NULL,
        workspace_id TEXT NOT NULL,
        run_id TEXT NOT NULL,
        task_id TEXT NOT NULL,
        bridge_id TEXT NOT NULL,
        lease_id TEXT NOT NULL,
        attempt INTEGER NOT NULL,
        idempotency_key TEXT NOT NULL,
        body_hash TEXT NOT NULL,
        response_json TEXT NOT NULL,
        created_at TEXT NOT NULL
      )
    `);
    sql.exec(`
      CREATE TABLE IF NOT EXISTS dlq_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        task_id TEXT NOT NULL,
        lease_id TEXT NOT NULL,
        reason TEXT NOT NULL,
        created_at TEXT NOT NULL,
        UNIQUE (run_id, task_id, lease_id)
      )
    `);
    sql.exec(`
      CREATE TABLE IF NOT EXISTS rate_limit_counters (
        counter_key TEXT PRIMARY KEY,
        count INTEGER NOT NULL,
        reset_at INTEGER NOT NULL
      )
    `);
    sql.exec(`
      CREATE TABLE IF NOT EXISTS circuit_breakers (
        target TEXT PRIMARY KEY,
        state TEXT NOT NULL,
        reason TEXT NOT NULL,
        opened_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )
    `);
    sql.exec(
      "INSERT OR IGNORE INTO _sql_schema_migrations (version, name, applied_at) VALUES (?, ?, ?)",
      1,
      "worker_orchestrator_projection_v2",
      nowIso(),
    );
  }

  private async processDueWork(reason: string): Promise<void> {
    if (this.migrationStatus !== "ok") {
      return;
    }
    const rows = this.ctx.storage.sql
      .exec<AlarmDueRow>(
        "SELECT run_id, task_id, lease_id, lease_expires_at, retry_after FROM tasks WHERE state IN ('leased', 'running', 'retry_scheduled')",
      )
      .toArray();
    const now = Date.now();
    const touched = new Set<string>();
    for (const row of rows) {
      const leaseDue = row.lease_expires_at ? Date.parse(row.lease_expires_at) <= now : false;
      const retryDue = row.retry_after ? Date.parse(row.retry_after) <= now : false;
      if (!leaseDue && !retryDue) {
        continue;
      }
      const state = this.loadRun(row.run_id);
      if (!state) {
        continue;
      }
      const task = state.tasks.find((item) => item.taskId === row.task_id);
      if (!task) {
        continue;
      }
      if ((task.state === "leased" || task.state === "running") && leaseDue) {
        state.timeoutCount += 1;
        if (task.attempt < task.maxAttempts) {
          task.state = "retry_scheduled";
          task.retryCount += 1;
          state.retryCount += 1;
          task.retryAfter = new Date(Date.now() + 1000).toISOString().replace(/\.\d{3}Z$/, "Z");
          state.auditEvents.push(auditEvent("task_retry_scheduled", state.runId, `bridge_timeout:${reason}`, task.taskId));
        } else {
          task.state = "blocked";
          task.blockedReason = "task_timeout";
          state.dlqCount += 1;
          this.insertDlq(task, state.runId, "task_timeout");
          state.auditEvents.push(auditEvent("task_blocked", state.runId, "task_timeout", task.taskId));
        }
        clearLease(task);
        progressRun(state);
        this.touch(state);
        this.saveRun(state);
        touched.add(state.runId);
      } else if (task.state === "retry_scheduled" && retryDue) {
        task.state = "pending";
        task.retryAfter = "";
        state.auditEvents.push(auditEvent("task_retry_ready", state.runId, "retry_after_elapsed", task.taskId));
        progressRun(state);
        this.touch(state);
        this.saveRun(state);
        touched.add(state.runId);
      }
    }
    this.markStaleBridges();
    await this.scheduleNextAlarm();
  }

  private async scheduleNextAlarm(): Promise<void> {
    const rows = this.ctx.storage.sql
      .exec<AlarmDueRow>(
        "SELECT run_id, task_id, lease_id, lease_expires_at, retry_after FROM tasks WHERE state IN ('leased', 'running', 'retry_scheduled')",
      )
      .toArray();
    const dueTimes: number[] = [];
    for (const row of rows) {
      for (const value of [row.lease_expires_at, row.retry_after]) {
        const parsed = Date.parse(value);
        if (Number.isFinite(parsed) && parsed > 0) {
          dueTimes.push(parsed);
        }
      }
    }
    const bridges = this.ctx.storage.sql.exec<BridgeRow>("SELECT bridge_id, state, state_json FROM bridges WHERE state = 'online'").toArray();
    for (const row of bridges) {
      const bridge = JSON.parse(row.state_json) as BridgeState;
      const staleAt = Date.parse(bridge.lastSeenAt) + STALE_BRIDGE_SECONDS * 1000;
      if (Number.isFinite(staleAt)) {
        dueTimes.push(staleAt);
      }
    }
    if (dueTimes.length === 0) {
      await this.ctx.storage.deleteAlarm();
      return;
    }
    await this.ctx.storage.setAlarm(Math.min(...dueTimes));
  }

  private loadRun(runId: string): RunState | null {
    const rows = this.ctx.storage.sql
      .exec<RunRow>(
        "SELECT run_id, schema_version, state, current_stage, completion_claim, state_json, legacy_state_read_count FROM runs WHERE run_id = ?",
        runId,
      )
      .toArray();
    if (rows.length === 0) {
      return null;
    }
    return this.deserializeRun(rows[0]);
  }

  private deserializeRun(row: RunRow): RunState {
    const parsed = JSON.parse(row.state_json) as RunState;
    if (parsed.schemaVersion === WORKER_RUN_STATE_SCHEMA) {
      return parsed;
    }
    const upgraded = upgradeLegacyRun(parsed);
    upgraded.legacyStateReadCount = (row.legacy_state_read_count || 0) + 1;
    this.ctx.storage.sql.exec(
      "UPDATE runs SET legacy_state_read_count = ?, schema_version = ?, state_json = ? WHERE run_id = ?",
      upgraded.legacyStateReadCount,
      WORKER_RUN_STATE_SCHEMA,
      JSON.stringify(upgraded),
      upgraded.runId,
    );
    return upgraded;
  }

  private saveRun(state: RunState): void {
    const saved = trimRunAudit({ ...state, auditEvents: [...state.auditEvents] });
    this.ctx.storage.sql.exec(
      "INSERT OR REPLACE INTO runs (run_id, workspace_id, schema_version, state, current_stage, completion_claim, state_json, created_at, updated_at, timeout_count, dlq_count, legacy_state_read_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
      state.runId,
      state.workspaceId,
      state.schemaVersion,
      state.state,
      state.currentStage,
      state.completionClaim,
      JSON.stringify(saved),
      state.createdAt,
      state.updatedAt,
      state.timeoutCount,
      state.dlqCount,
      state.legacyStateReadCount,
    );
    this.ctx.storage.sql.exec("DELETE FROM tasks WHERE run_id = ?", state.runId);
    for (const task of state.tasks) {
      this.ctx.storage.sql.exec(
        "INSERT INTO tasks (run_id, task_id, workspace_id, state, attempt, lease_id, bridge_id, lease_expires_at, retry_after, state_json, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        state.runId,
        task.taskId,
        state.workspaceId,
        task.state,
        task.attempt,
        task.leaseId,
        task.leasedBy,
        task.leaseExpiresAt,
        task.retryAfter,
        JSON.stringify(task),
        state.updatedAt,
      );
    }
    for (const event of state.auditEvents) {
      const safe = redactForLog(event);
      this.ctx.storage.sql.exec(
        "INSERT OR IGNORE INTO audit_events (event_id, run_id, task_id, bridge_id, event_type, summary, safe_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        event.eventId,
        event.runId,
        event.taskId || "",
        event.bridgeId || "",
        event.eventType,
        event.summary,
        JSON.stringify(safe),
        event.createdAt,
      );
    }
  }

  private loadBridge(bridgeId: string): BridgeState | null {
    const rows = this.ctx.storage.sql
      .exec<BridgeRow>("SELECT bridge_id, state, state_json FROM bridges WHERE bridge_id = ?", bridgeId)
      .toArray();
    if (rows.length === 0) {
      return null;
    }
    return JSON.parse(rows[0].state_json) as BridgeState;
  }

  private knownBridgeIds(): string[] {
    return this.ctx.storage.sql.exec<{ bridge_id: string }>("SELECT bridge_id FROM bridges ORDER BY bridge_id LIMIT 20").toArray().map((row) => row.bridge_id);
  }

  private saveBridge(bridge: BridgeState): void {
    this.ctx.storage.sql.exec(
      "INSERT OR REPLACE INTO bridges (bridge_id, workspace_id, state, machine_id, bridge_instance_id, auth_subject, token_id, revoked_at, last_seen_at, state_json, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
      bridge.bridgeId,
      bridge.workspaceId,
      bridge.state,
      bridge.machineId,
      bridge.bridgeInstanceId,
      bridge.authSubject,
      bridge.tokenId,
      bridge.revokedAt,
      bridge.lastSeenAt,
      JSON.stringify(bridge),
      nowIso(),
    );
  }

  private async withIdempotency(meta: MutationMeta, action: () => Promise<JsonObject>): Promise<JsonObject> {
    const id = await idempotencyId(meta);
    const rows = this.ctx.storage.sql
      .exec<IdempotencyRow>(
        "SELECT idempotency_id, body_hash, response_json FROM idempotency_keys WHERE idempotency_id = ?",
        id,
      )
      .toArray();
    if (rows.length > 0) {
      if (rows[0].body_hash !== meta.bodyHash) {
        throw new ApiError(409, "idempotency_conflict", "Same idempotency key used with a different payload.");
      }
      return JSON.parse(rows[0].response_json) as JsonObject;
    }
    const response = await action();
    this.ctx.storage.sql.exec(
      "INSERT INTO idempotency_keys (idempotency_id, route, method, auth_subject, workspace_id, run_id, task_id, bridge_id, lease_id, attempt, idempotency_key, body_hash, response_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
      id,
      meta.route,
      meta.method,
      meta.authSubject,
      meta.workspaceId,
      meta.runId || "",
      meta.taskId || "",
      meta.bridgeId || "",
      meta.leaseId || "",
      meta.attempt || 0,
      meta.idempotencyKey,
      meta.bodyHash,
      JSON.stringify(response),
      nowIso(),
    );
    return response;
  }

  private async checkMutationRateLimit(meta: MutationMeta): Promise<void> {
    const windowMs = 60_000;
    const now = Date.now();
    const limit = boundedInteger(this.env.MUTATION_RATE_LIMIT_PER_MINUTE, 120, 10, 10_000);
    const key = `${meta.authSubject}:${meta.route}:${Math.floor(now / windowMs)}`;
    const rows = this.ctx.storage.sql
      .exec<{ count: number; reset_at: number }>("SELECT count, reset_at FROM rate_limit_counters WHERE counter_key = ?", key)
      .toArray();
    if (rows.length === 0 || rows[0].reset_at <= now) {
      this.ctx.storage.sql.exec(
        "INSERT OR REPLACE INTO rate_limit_counters (counter_key, count, reset_at) VALUES (?, ?, ?)",
        key,
        1,
        now + windowMs,
      );
      return;
    }
    const count = rows[0].count + 1;
    this.ctx.storage.sql.exec("UPDATE rate_limit_counters SET count = ? WHERE counter_key = ?", count, key);
    if (count > limit) {
      throw new ApiError(429, "backpressure_active", "Mutation rate limit exceeded.");
    }
  }

  private async backlogCounts(): Promise<{ pending: number; running: number; retryScheduled: number; dlq: number }> {
    const pending = this.countTasks("pending");
    const leased = this.countTasks("leased");
    const running = this.countTasks("running");
    const retryScheduled = this.countTasks("retry_scheduled");
    const dlq = this.ctx.storage.sql.exec<CountRow>("SELECT COUNT(*) AS count FROM dlq_items").one().count;
    return { pending, running: running + leased, retryScheduled, dlq };
  }

  private backpressureLimits(): typeof DEFAULT_BACKPRESSURE_LIMITS {
    return {
      pending: boundedInteger(this.env.MAX_PENDING_TASKS, DEFAULT_BACKPRESSURE_LIMITS.pending, 1, 10_000),
      running: boundedInteger(this.env.MAX_RUNNING_TASKS, DEFAULT_BACKPRESSURE_LIMITS.running, 1, 10_000),
      retryScheduled: boundedInteger(this.env.MAX_RETRY_TASKS, DEFAULT_BACKPRESSURE_LIMITS.retryScheduled, 1, 10_000),
      dlq: boundedInteger(this.env.MAX_DLQ_ITEMS, DEFAULT_BACKPRESSURE_LIMITS.dlq, 1, 10_000),
    };
  }

  private countTasks(state: string): number {
    return this.ctx.storage.sql.exec<CountRow>("SELECT COUNT(*) AS count FROM tasks WHERE state = ?", state).one().count;
  }

  private countActiveLeasesForBridge(bridgeId: string): number {
    return this.ctx.storage.sql
      .exec<CountRow>("SELECT COUNT(*) AS count FROM tasks WHERE bridge_id = ? AND state IN ('leased', 'running')", bridgeId)
      .one().count;
  }

  private async openQueueCircuit(reason: string): Promise<void> {
    this.openGlobalCircuit("worker_queue", reason);
  }

  private openGlobalCircuit(target: string, reason: string): void {
    const now = nowIso();
    this.ctx.storage.sql.exec(
      "INSERT OR REPLACE INTO circuit_breakers (target, state, reason, opened_at, updated_at) VALUES (?, ?, ?, ?, ?)",
      target,
      "open",
      reason,
      now,
      now,
    );
  }

  private recordSystemAudit(eventType: string, runId: string, summary: string): void {
    try {
      const event = auditEvent(eventType, runId, summary);
      const safe = redactForLog(event);
      this.ctx.storage.sql.exec(
        "INSERT OR IGNORE INTO audit_events (event_id, run_id, task_id, bridge_id, event_type, summary, safe_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        event.eventId,
        event.runId,
        "",
        "",
        event.eventType,
        event.summary,
        JSON.stringify(safe),
        event.createdAt,
      );
    } catch (error) {
      console.error(JSON.stringify({ level: "error", message: "system_audit_write_failed", error: error instanceof Error ? error.message : String(error) }));
    }
  }

  private markWaitingForBridge(state: RunState, bridgeId: string, reason: string): void {
    if (state.state === "completed" || state.state === "blocked" || state.state === "cancelled") {
      return;
    }
    state.state = "waiting_for_bridge";
    openCircuit(state, "local_bridge", reason);
    if (!state.blockedReasons.includes(reason)) {
      state.blockedReasons.push(reason);
    }
    state.auditEvents.push(auditEvent("bridge_unavailable", state.runId, `${bridgeId}: ${reason}`, undefined, bridgeId));
    this.touch(state);
    this.saveRun(state);
  }

  private markActiveLeasesForBridgeUnavailable(bridgeId: string, reason: string): void {
    const rows = this.ctx.storage.sql
      .exec<AlarmDueRow>(
        "SELECT run_id, task_id, lease_id, lease_expires_at, retry_after FROM tasks WHERE bridge_id = ? AND state IN ('leased', 'running')",
        bridgeId,
      )
      .toArray();
    for (const row of rows) {
      const state = this.loadRun(row.run_id);
      if (!state) {
        continue;
      }
      const task = state.tasks.find((item) => item.taskId === row.task_id);
      if (!task) {
        continue;
      }
      if (task.attempt < task.maxAttempts) {
        task.state = "retry_scheduled";
        task.retryCount += 1;
        state.retryCount += 1;
        task.retryAfter = new Date(Date.now() + 1000).toISOString().replace(/\.\d{3}Z$/, "Z");
        state.auditEvents.push(auditEvent("task_retry_scheduled", state.runId, reason, task.taskId, bridgeId));
      } else {
        task.state = "blocked";
        task.blockedReason = "task_timeout";
        state.dlqCount += 1;
        this.insertDlq(task, state.runId, "task_timeout");
        state.auditEvents.push(auditEvent("task_blocked", state.runId, "task_timeout", task.taskId, bridgeId));
      }
      clearLease(task);
      progressRun(state);
      this.touch(state);
      this.saveRun(state);
    }
  }

  private markStaleBridges(): void {
    const rows = this.ctx.storage.sql.exec<BridgeRow>("SELECT bridge_id, state, state_json FROM bridges WHERE state = 'online'").toArray();
    const now = Date.now();
    for (const row of rows) {
      const bridge = JSON.parse(row.state_json) as BridgeState;
      if (Date.parse(bridge.lastSeenAt) + STALE_BRIDGE_SECONDS * 1000 > now) {
        continue;
      }
      bridge.state = "offline";
      bridge.offlineAt = nowIso();
      bridge.offlineReason = "bridge_stale";
      this.saveBridge(bridge);
      this.markActiveLeasesForBridgeUnavailable(bridge.bridgeId, "bridge_stale");
    }
  }

  private insertDlq(task: RunTask, runId: string, reason: string): void {
    this.ctx.storage.sql.exec(
      "INSERT OR IGNORE INTO dlq_items (run_id, task_id, lease_id, reason, created_at) VALUES (?, ?, ?, ?, ?)",
      runId,
      task.taskId,
      task.leaseId || `attempt:${task.attempt}`,
      reason,
      nowIso(),
    );
  }

  private countByState(table: string, column: string): Record<string, number> {
    const rows = this.ctx.storage.sql.exec<{ state: string; count: number }>(`SELECT ${column} AS state, COUNT(*) AS count FROM ${table} GROUP BY ${column}`).toArray();
    return Object.fromEntries(rows.map((row) => [row.state, row.count]));
  }

  private sumColumn(table: string, column: string): number {
    return this.ctx.storage.sql.exec<{ total: number }>(`SELECT COALESCE(SUM(${column}), 0) AS total FROM ${table}`).one().total;
  }

  private blockedReasonSummary(): Record<string, number> {
    const rows = this.ctx.storage.sql.exec<{ summary: string; count: number }>(
      "SELECT summary, COUNT(*) AS count FROM audit_events WHERE event_type = 'task_blocked' GROUP BY summary",
    ).toArray();
    return Object.fromEntries(rows.map((row) => [row.summary, row.count]));
  }

  private loadCircuitBreakers(): Record<string, RunState["circuitBreakers"][string]> {
    const rows = this.ctx.storage.sql.exec<{ target: string; state: "closed" | "open" | "half_open"; reason: string; opened_at: string; updated_at: string }>(
      "SELECT target, state, reason, opened_at, updated_at FROM circuit_breakers",
    ).toArray();
    return Object.fromEntries(rows.map((row) => [row.target, { state: row.state, reason: row.reason, openedAt: row.opened_at, updatedAt: row.updated_at }]));
  }

  private recentErrors(): JsonObject[] {
    const rows = this.ctx.storage.sql.exec<{ safe_json: string }>(
      "SELECT safe_json FROM audit_events WHERE event_type IN ('task_blocked', 'migration_failed', 'alarm_failed', 'security_violation') ORDER BY created_at DESC LIMIT 20",
    ).toArray();
    return rows.map((row) => JSON.parse(row.safe_json) as JsonObject);
  }

  private assertWritable(): void {
    if (this.migrationStatus !== "ok") {
      throw new ApiError(503, "migration_failed", "Durable Object migration failed; writes are refused.", {
        migrationStatus: this.migrationStatus,
        migrationError: this.migrationError,
      });
    }
  }

  private assertBridgeNotRevokedForReplay(bridgeId: string): void {
    const bridge = this.loadBridge(bridgeId);
    if (bridge?.revokedAt) {
      throw new ApiError(409, "bridge_revoked", "Bridge is revoked.");
    }
  }

  private touch(state: RunState): void {
    state.updatedAt = nowIso();
  }

  private ensureColumn(table: string, column: string, definition: string): void {
    const rows = this.ctx.storage.sql.exec<{ name: string }>(`PRAGMA table_info(${table})`).toArray();
    if (rows.some((row) => row.name === column)) {
      return;
    }
    this.ctx.storage.sql.exec(`ALTER TABLE ${table} ADD COLUMN ${column} ${definition}`);
  }
}

function buildTasks(input: {
  runId: string;
  workspaceId: string;
  requestedBy: string;
  targetStage: TargetStage;
  agentIds: string[];
  dependencies: Record<string, string[]>;
  taskSpecs?: TaskSpec[];
}): RunTask[] {
  let tasks: RunTask[];
  if (input.taskSpecs) {
    tasks = input.taskSpecs.map((spec, index) => buildTaskFromSpec(input, spec, index + 1));
    validateTaskGraph(tasks);
    return tasks;
  }
  const taskIds = Object.fromEntries(input.agentIds.map((agentId) => [agentId, `task_${agentId}_001`]));
  for (const [agentId, dependencies] of Object.entries(input.dependencies)) {
    if (!taskIds[agentId]) {
      throw new ApiError(422, "invalid_task_dependency", `Unknown dependency owner agent ${agentId}.`);
    }
    for (const dependency of dependencies) {
      if (!taskIds[dependency]) {
        throw new ApiError(422, "invalid_task_dependency", `Agent ${agentId} depends on unknown agent ${dependency}.`);
      }
    }
  }
  tasks = input.agentIds.map((agentId, index) =>
    buildTaskFromSpec(
      input,
      {
        taskId: taskIds[agentId],
        agentId,
        dependsOn: (input.dependencies[agentId] || []).map((dependency) => taskIds[dependency]).filter(Boolean),
        allowedTools: ["codex_cli_model_review"],
      },
      index + 1,
    ),
  );
  validateTaskGraph(tasks);
  return tasks;
}

function validateTaskGraph(tasks: RunTask[]): void {
  const taskIds = new Set<string>();
  for (const task of tasks) {
    if (taskIds.has(task.taskId)) {
      throw new ApiError(422, "duplicate_task_id", `Duplicate taskId: ${task.taskId}`);
    }
    taskIds.add(task.taskId);
  }

  for (const task of tasks) {
    for (const dependencyId of task.dependsOn) {
      if (!taskIds.has(dependencyId)) {
        throw new ApiError(422, "invalid_task_dependency", `Task ${task.taskId} depends on unknown task ${dependencyId}.`);
      }
    }
  }

  const visited = new Set<string>();
  const visiting = new Set<string>();
  const byId = new Map(tasks.map((task) => [task.taskId, task]));

  const visit = (task: RunTask): void => {
    if (visited.has(task.taskId)) {
      return;
    }
    if (visiting.has(task.taskId)) {
      throw new ApiError(422, "task_dependency_cycle", `Task dependency cycle includes ${task.taskId}.`);
    }
    visiting.add(task.taskId);
    for (const dependencyId of task.dependsOn) {
      const dependency = byId.get(dependencyId);
      if (dependency) {
        visit(dependency);
      }
    }
    visiting.delete(task.taskId);
    visited.add(task.taskId);
  };

  for (const task of tasks) {
    visit(task);
  }
}

function buildTaskFromSpec(
  input: {
    runId: string;
    workspaceId: string;
    requestedBy: string;
    targetStage: TargetStage;
  },
  spec: TaskSpec,
  index: number,
): RunTask {
  const agentId = spec.agentId || `agent_${index}`;
  const taskId = spec.taskId || `task_${agentId}_${String(index).padStart(3, "0")}`;
  const allowedTools = spec.allowedTools || ["codex_cli_model_review"];
  const forbiddenActions = spec.forbiddenActions || DEFAULT_FORBIDDEN_ACTIONS;
  const timeoutSeconds = boundedInteger(spec.timeoutSeconds, DEFAULT_TASK_TIMEOUT_SECONDS, 1, 300);
  const envelope = {
    schemaVersion: TASK_ENVELOPE_SCHEMA,
    runId: input.runId,
    taskId,
    workspaceId: input.workspaceId,
    requestedBy: input.requestedBy,
    stage: input.targetStage,
    agentId,
    promptPackId: spec.promptPackId || agentId,
    inputRefs: spec.inputRefs || [],
    allowedTools,
    forbiddenActions,
    outputSchema: spec.outputSchema || `agent_output/${agentId}/v1`,
    timeoutSeconds,
    idempotencyKey: spec.idempotencyKey || `${input.runId}:${taskId}:attempt`,
    constraints: {
      savedCurrentDwg: false,
      workerExecutesShell: false,
      workerSavesCurrentDwg: false,
      forbiddenActions,
    },
    savedCurrentDwg: false,
  } as const;
  return {
    taskId,
    agentId,
    state: "pending",
    dependsOn: spec.dependsOn || [],
    attempt: 0,
    retryCount: 0,
    maxAttempts: boundedInteger(spec.maxAttempts, DEFAULT_MAX_ATTEMPTS, 1, 5),
    timeoutSeconds,
    retryAfter: "",
    leaseId: "",
    leaseSequence: 0,
    leasedBy: "",
    machineId: "",
    bridgeInstanceId: "",
    heartbeatToken: "",
    heartbeatSeq: 0,
    leaseExpiresAt: "",
    heartbeatAt: "",
    blockedReason: "",
    allowedTools,
    forbiddenActions,
    requestedActions: spec.requestedActions || [],
    envelope,
  };
}

function normalizeOutput(state: RunState, task: RunTask, result: JsonObject): AgentOutput {
  return {
    schemaVersion: typeof result.schemaVersion === "string" ? result.schemaVersion : AGENT_OUTPUT_SCHEMA,
    runId: state.runId,
    taskId: task.taskId,
    agentId: task.agentId,
    status: typeof result.status === "string" ? result.status : "completed",
    decision: typeof result.decision === "string" ? result.decision : "continue",
    summary: typeof result.summary === "string" ? result.summary : "",
    modelInvoked: result.modelInvoked === true,
    modelUnavailable: result.modelUnavailable === true,
    schemaValid: result.schemaValid === true,
    traceRef: typeof result.traceRef === "string" ? result.traceRef : "",
    evidenceRefs: Array.isArray(result.evidenceRefs) ? result.evidenceRefs.map(String) : [],
    blockedReason: typeof result.blockedReason === "string" ? result.blockedReason : "",
    savedCurrentDwg: false,
  };
}

function findTask(state: RunState, taskId: string): RunTask {
  const task = state.tasks.find((item) => item.taskId === taskId);
  if (!task) {
    throw new ApiError(404, "task_not_found", "Task was not found in this run.");
  }
  return task;
}

function assertLeaseIdentity(task: RunTask, input: {
  leaseId: string;
  bridgeId: string;
  machineId: string;
  bridgeInstanceId: string;
  heartbeatToken: string;
}): void {
  if (task.state !== "leased" && task.state !== "running") {
    throw new ApiError(409, "task_not_leaseable", "Task is not leased or running.");
  }
  if (
    task.leaseId !== input.leaseId ||
    task.leasedBy !== input.bridgeId ||
    task.machineId !== input.machineId ||
    task.bridgeInstanceId !== input.bridgeInstanceId ||
    task.heartbeatToken !== input.heartbeatToken
  ) {
    throw new ApiError(409, "lease_mismatch", "Lease identity mismatch.");
  }
}

function findDangerousResultReason(result: JsonObject): string {
  if (result.savedCurrentDwg === true) {
    return "saved_current_dwg_violation";
  }
  const payload = stableJson(result).toLowerCase();
  const forbiddenTerms = [
    ...Array.from(FORBIDDEN_WORKER_ACTIONS),
    ...Array.from(FORBIDDEN_WORKER_TOOLS).filter((term) => term.length > 3),
    "child_process",
    "powershell",
    "cad-mcp",
    "cad_mcp",
    "autocad",
  ];
  for (const term of forbiddenTerms) {
    if (payload.includes(term.toLowerCase())) {
      return "forbidden_action_requested";
    }
  }
  return "";
}

function trimRunAudit(state: RunState): RunState {
  return {
    ...state,
    auditEvents: state.auditEvents.slice(-MAX_AUDIT_EVENTS_IN_RUN_STATE),
  };
}

function upgradeLegacyRun(value: RunState): RunState {
  const now = nowIso();
  return {
    ...value,
    schemaVersion: WORKER_RUN_STATE_SCHEMA,
    authSubject: value.authSubject || value.requestedBy || "legacy",
    legacyStateReadCount: value.legacyStateReadCount || 0,
    tasks: (value.tasks || []).map((task) => ({
      ...task,
      retryAfter: task.retryAfter || "",
      leaseId: task.leaseId || "",
      leaseSequence: task.leaseSequence || 0,
      machineId: task.machineId || "",
      bridgeInstanceId: task.bridgeInstanceId || "",
      heartbeatSeq: task.heartbeatSeq || 0,
      envelope: {
        ...task.envelope,
        constraints: task.envelope.constraints || {
          savedCurrentDwg: false,
          workerExecutesShell: false,
          workerSavesCurrentDwg: false,
          forbiddenActions: task.forbiddenActions || DEFAULT_FORBIDDEN_ACTIONS,
        },
        savedCurrentDwg: false,
      },
    })),
    circuitBreakers: value.circuitBreakers || defaultCircuitBreakers(),
    auditEvents: value.auditEvents || [],
    updatedAt: value.updatedAt || now,
  };
}

function summarizeRun(state: RunState): JsonObject {
  return {
    runId: state.runId,
    workspaceId: state.workspaceId,
    state: state.state,
    currentStage: state.currentStage,
    completionClaim: state.completionClaim,
    taskCount: state.tasks.length,
    timeoutCount: state.timeoutCount,
    dlqCount: state.dlqCount,
    createdAt: state.createdAt,
    updatedAt: state.updatedAt,
  };
}

function redactBridge(bridge: BridgeState): JsonObject {
  return redactForLog({
    bridgeId: bridge.bridgeId,
    machineId: bridge.machineId,
    bridgeInstanceId: bridge.bridgeInstanceId,
    workspaceId: bridge.workspaceId,
    version: bridge.version,
    protocolVersion: bridge.protocolVersion,
    state: bridge.state,
    capabilities: bridge.capabilities.map((capability) => ({
      capabilityId: capability.capabilityId,
      version: capability.version,
      supportedStages: capability.supportedStages,
      allowedTools: capability.allowedTools,
      maxConcurrentLeases: capability.maxConcurrentLeases,
      savedCurrentDwg: false,
    })),
    authSubject: bridge.authSubject,
    tokenId: bridge.tokenId,
    registeredAt: bridge.registeredAt,
    lastSeenAt: bridge.lastSeenAt,
    offlineAt: bridge.offlineAt,
    offlineReason: bridge.offlineReason,
    revokedAt: bridge.revokedAt,
    revokedReason: bridge.revokedReason,
  });
}

async function idempotencyId(meta: MutationMeta): Promise<string> {
  return sha256Hex(
    [
      meta.route,
      meta.method,
      meta.authSubject,
      meta.workspaceId,
      meta.runId || "",
      meta.taskId || "",
      meta.bridgeId || "",
      meta.leaseId || "",
      meta.attempt || 0,
      meta.idempotencyKey,
    ].join("|"),
  );
}
