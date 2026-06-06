import { mkdirSync } from "node:fs";
import { resolve } from "node:path";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = resolve(fileURLToPath(new URL("../../..", import.meta.url)));
const wranglerConfigDir = resolve(root, ".wrangler-config");
const wranglerLogDir = resolve(wranglerConfigDir, "logs");
mkdirSync(wranglerLogDir, { recursive: true });

const vitestBin = resolve(root, "node_modules/vitest/vitest.mjs");
const child = spawn(process.execPath, [vitestBin, "run", "--config", "workers/orchestrator/vitest.config.ts"], {
  cwd: root,
  stdio: "inherit",
  env: {
    ...process.env,
    XDG_CONFIG_HOME: process.env.XDG_CONFIG_HOME || wranglerConfigDir,
    WRANGLER_LOG_PATH: process.env.WRANGLER_LOG_PATH || wranglerLogDir,
    WORKER_API_TOKEN: process.env.WORKER_API_TOKEN || "local-worker-token",
    BRIDGE_API_TOKEN: process.env.BRIDGE_API_TOKEN || "local-bridge-token",
    ADMIN_API_TOKEN: process.env.ADMIN_API_TOKEN || "local-admin-token",
  },
});

child.on("exit", (code, signal) => {
  if (signal) {
    console.error(`vitest terminated by signal ${signal}`);
    process.exit(1);
  }
  process.exit(code ?? 1);
});
