import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { cloudflareTest } from "@cloudflare/vitest-pool-workers";
import { defineConfig } from "vitest/config";

const here = fileURLToPath(new URL(".", import.meta.url));
const workspaceRoot = resolve(here, "../..");
const localWranglerConfig = resolve(workspaceRoot, ".wrangler-config");

process.env.XDG_CONFIG_HOME ||= localWranglerConfig;
process.env.WRANGLER_LOG_PATH ||= resolve(localWranglerConfig, "logs");
process.env.WORKER_API_TOKEN ||= "local-worker-token";
process.env.BRIDGE_API_TOKEN ||= "local-bridge-token";
process.env.ADMIN_API_TOKEN ||= "local-admin-token";

export default defineConfig({
  root: workspaceRoot,
  plugins: [
    cloudflareTest({
      main: resolve(here, "src/index.ts"),
      wrangler: {
        configPath: resolve(workspaceRoot, "wrangler.jsonc"),
      },
      miniflare: {
        bindings: {
          WORKER_API_TOKEN: "local-worker-token",
          BRIDGE_API_TOKEN: "local-bridge-token",
          ADMIN_API_TOKEN: "local-admin-token",
          ALLOWED_BRIDGE_IDS:
            "bridge_local_smoke,bridge_runtime,bridge_runtime_alt,bridge_alarm,bridge_revoke_smoke,bridge_replay_revoked,bridge_replay_result_revoked,bridge_offline_dlq,bridge_stale_dlq,bridge_capacity",
        },
      },
    }),
  ],
  test: {
    include: ["workers/orchestrator/test/**/*.test.ts"],
  },
});
