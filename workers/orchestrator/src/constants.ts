export const LEGACY_WORKER_RUN_STATE_SCHEMA = "worker_run_state/v1";
export const WORKER_RUN_STATE_SCHEMA = "worker_run_state/v2";
export const TASK_ENVELOPE_SCHEMA = "worker_task_envelope/v1";
export const AGENT_OUTPUT_SCHEMA = "agent_output/v1";
export const BRIDGE_REGISTRATION_SCHEMA = "local_bridge_registration/v1";

export const MAX_JSON_BYTES = 64 * 1024;
export const MAX_AUDIT_EVENTS_IN_RUN_STATE = 20;
export const DEFAULT_WORKSPACE_ID = "cad-agent-core-lab";
export const DEFAULT_HEARTBEAT_INTERVAL_SECONDS = 10;
export const DEFAULT_TASK_TIMEOUT_SECONDS = 30;
export const DEFAULT_MAX_ATTEMPTS = 2;
export const STALE_BRIDGE_SECONDS = 90;

export const FEATURE_GATE_STAGES = [
  "worker_orchestration_ready",
  "local_bridge_connected",
  "single_agent_live",
  "multi_agent_live",
  "cad_mcp_preview_live",
  "current_dwg_save",
] as const;

export const FEATURE_GATE_ORDER = Object.fromEntries(FEATURE_GATE_STAGES.map((stage, index) => [stage, index])) as Record<
  (typeof FEATURE_GATE_STAGES)[number],
  number
>;

export const FEATURE_GATE_NEXT_ACTION: Partial<Record<(typeof FEATURE_GATE_STAGES)[number], string>> = {
  local_bridge_connected: "register_or_start_local_bridge",
  single_agent_live: "enable_codex_cli_model_review",
  multi_agent_live: "enable_multi_agent_live_chain",
  cad_mcp_preview_live: "enable_cad_preview_after_validate_and_dry_run",
  current_dwg_save: "requires_explicit_save_authorization",
};

export const CANONICAL_ALLOWED_TOOLS = new Set([
  "codex_cli_model_review",
  "agent_trace_read",
  "task_envelope_only",
  "preview_cad_execute",
  "execute_cad_plan_preview",
]);

export const FORBIDDEN_WORKER_TOOLS = new Set([
  "shell_arbitrary",
  "cmd",
  "powershell",
  "child_process",
  "exec",
  "spawn",
  "cad_mcp_execute",
  "autocad_execute",
  "upload_full_repo",
]);

export const FORBIDDEN_WORKER_ACTIONS = new Set([
  "shell_arbitrary",
  "save_current_dwg",
  "delete_unscoped_entities",
  "upload_full_repo",
  "cad_mcp_execute",
  "autocad_execute",
  "dwg_save",
]);

export const DEFAULT_FORBIDDEN_ACTIONS = [
  "shell_arbitrary",
  "save_current_dwg",
  "delete_unscoped_entities",
  "upload_full_repo",
  "cad_mcp_execute",
  "autocad_execute",
  "dwg_save",
];

export const DEFAULT_CIRCUIT_TARGETS = [
  "local_bridge",
  "codex_cli_model_review",
  "cad_mcp_preview",
  "worker_queue",
  "security_gate",
] as const;

export const DEFAULT_BACKPRESSURE_LIMITS = {
  pending: 100,
  running: 25,
  retryScheduled: 50,
  dlq: 50,
};

export const KILL_SWITCHES = {
  orchestrator: "ORCHESTRATOR_DISABLED",
  createRun: "RUN_CREATE_DISABLED",
  bridgeLeasing: "BRIDGE_LEASING_DISABLED",
  submit: "SUBMIT_DISABLED",
} as const;

export const REQUIRED_SECRET_NAMES = ["WORKER_API_TOKEN", "BRIDGE_API_TOKEN", "ADMIN_API_TOKEN"] as const;
