import { mkdirSync } from "node:fs";
import { resolve } from "node:path";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = resolve(fileURLToPath(new URL("../../..", import.meta.url)));
const wranglerConfigDir = resolve(root, ".wrangler-config");
const wranglerLogDir = resolve(wranglerConfigDir, "logs");
const args = process.argv.slice(2);

assertAllowedWranglerCommand(args);
mkdirSync(wranglerLogDir, { recursive: true });

const wranglerBin = resolve(root, "node_modules/wrangler/bin/wrangler.js");
const child = spawn(process.execPath, [wranglerBin, ...args], {
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
    console.error(`wrangler terminated by signal ${signal}`);
    process.exit(1);
  }
  process.exit(code ?? 1);
});

function assertAllowedWranglerCommand(args) {
  const [command, subcommand] = args;
  if (!command) {
    deny("Missing Wrangler command. Allowed commands: dev, types, deploy --dry-run, deploy --strict with CADAGENT_DEPLOY_APPROVED=true, whoami.");
  }

  if (/^secrets?$/i.test(command) && /^put$/i.test(subcommand || "")) {
    deny("wrangler secret put is blocked by this local wrapper.");
  }

  if (/^deploy$/i.test(command)) {
    if (!args.includes("--dry-run")) {
      if (process.env.CADAGENT_DEPLOY_APPROVED !== "true") {
        deny("wrangler deploy without --dry-run requires CADAGENT_DEPLOY_APPROVED=true.");
      }
      if (!args.includes("--strict")) {
        deny("cadagent deploy must use --strict.");
      }
      if (!args.includes("--secrets-file")) {
        deny("cadagent deploy must use --secrets-file so required secrets are explicit and non-interactive.");
      }
    }
    return;
  }

  if (/^dev$/i.test(command)) {
    if (args.includes("--remote") || !args.includes("--local")) {
      deny("wrangler dev must be explicitly local; use dev --local.");
    }
    return;
  }

  if (/^types$/i.test(command)) {
    return;
  }

  if (/^whoami$/i.test(command)) {
    return;
  }

  deny(`Wrangler command '${args.join(" ")}' is not allowed by this local wrapper.`);
}

function deny(message) {
  console.error(JSON.stringify({ status: "blocked", reason: message }));
  process.exit(2);
}
